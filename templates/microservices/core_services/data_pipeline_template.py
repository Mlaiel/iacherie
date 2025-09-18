"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Data Pipeline Template for Ainflue Microservices Platform
========================================================

Enterprise-grade ETL data pipeline template providing:
- High-performance parallel processing
- Multi-source data extraction (databases, APIs, files)
- Advanced data transformation with validation
- Multiple output destinations with atomic operations
- Schema evolution and data lineage tracking
- Data quality monitoring and profiling
- Fault tolerance with checkpointing
- Resource optimization and scaling
- Real-time and batch processing modes
- Comprehensive error handling and recovery

Author: Fahed Mlaiel (mlaiel@live.de)
DBA & Data Pipeline Specialist
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Type, Union, Iterator, AsyncIterator
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import uuid
from pathlib import Path
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import pandas as pd
import numpy as np
from great_expectations import DataContext
import pyarrow as pa
import pyarrow.parquet as pq
from elasticsearch import AsyncElasticsearch
import aiofiles
import aiohttp

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus
from ..communication_manager import CommunicationManager, CommunicationConfig

logger = logging.getLogger(__name__)

Base = declarative_base()


class PipelineStatus(str, Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class DataSourceType(str, Enum):
    """Data source types"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    MESSAGE_QUEUE = "message_queue"
    OBJECT_STORAGE = "object_storage"


class TransformationType(str, Enum):
    """Data transformation types"""
    FILTER = "filter"
    MAP = "map"
    AGGREGATE = "aggregate"
    JOIN = "join"
    SORT = "sort"
    DEDUPLICATE = "deduplicate"
    VALIDATE = "validate"
    ENRICH = "enrich"


class OutputDestination(str, Enum):
    """Output destination types"""
    DATABASE = "database"
    FILE = "file"
    API = "api"
    MESSAGE_QUEUE = "message_queue"
    OBJECT_STORAGE = "object_storage"
    SEARCH_INDEX = "search_index"


class DataQualityRule(BaseModel):
    """Data quality validation rule"""
    name: str = Field(..., description="Rule name")
    rule_type: str = Field(..., description="Rule type (completeness, uniqueness, validity, etc.)")
    column: Optional[str] = Field(default=None, description="Target column")
    expression: str = Field(..., description="Validation expression")
    threshold: float = Field(default=1.0, description="Quality threshold (0.0-1.0)")
    severity: str = Field(default="error", description="Severity level")
    enabled: bool = Field(default=True, description="Whether rule is enabled")


class DataSource(BaseModel):
    """Data source configuration"""
    id: str = Field(..., description="Unique source identifier")
    name: str = Field(..., description="Human-readable source name")
    source_type: DataSourceType = Field(..., description="Source type")
    connection_config: Dict[str, Any] = Field(..., description="Connection configuration")
    query_config: Optional[Dict[str, Any]] = Field(default=None, description="Query configuration")
    schema_config: Optional[Dict[str, Any]] = Field(default=None, description="Schema configuration")
    incremental_config: Optional[Dict[str, Any]] = Field(default=None, description="Incremental loading config")
    enabled: bool = Field(default=True, description="Whether source is enabled")


class DataTransformation(BaseModel):
    """Data transformation configuration"""
    id: str = Field(..., description="Unique transformation identifier")
    name: str = Field(..., description="Human-readable transformation name")
    transformation_type: TransformationType = Field(..., description="Transformation type")
    function_name: str = Field(..., description="Transformation function name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Transformation parameters")
    dependencies: List[str] = Field(default_factory=list, description="Dependency transformations")
    quality_rules: List[DataQualityRule] = Field(default_factory=list, description="Quality validation rules")
    enabled: bool = Field(default=True, description="Whether transformation is enabled")


class DataOutput(BaseModel):
    """Data output configuration"""
    id: str = Field(..., description="Unique output identifier")
    name: str = Field(..., description="Human-readable output name")
    destination_type: OutputDestination = Field(..., description="Destination type")
    connection_config: Dict[str, Any] = Field(..., description="Connection configuration")
    format_config: Optional[Dict[str, Any]] = Field(default=None, description="Output format configuration")
    partitioning_config: Optional[Dict[str, Any]] = Field(default=None, description="Partitioning configuration")
    compression_config: Optional[Dict[str, Any]] = Field(default=None, description="Compression configuration")
    enabled: bool = Field(default=True, description="Whether output is enabled")


class ProcessingConfig(BaseModel):
    """Pipeline processing configuration"""
    batch_size: int = Field(default=1000, ge=1, description="Processing batch size")
    max_workers: int = Field(default=4, ge=1, description="Maximum worker processes")
    chunk_size: int = Field(default=10000, ge=1, description="Data chunk size")
    enable_parallel_processing: bool = Field(default=True, description="Enable parallel processing")
    enable_checkpointing: bool = Field(default=True, description="Enable progress checkpointing")
    checkpoint_interval: int = Field(default=1000, description="Checkpoint interval (records)")
    memory_limit_mb: int = Field(default=1024, description="Memory limit per worker")
    timeout_seconds: int = Field(default=3600, description="Pipeline timeout")


class PipelineDefinition(BaseModel):
    """Data pipeline definition"""
    id: str = Field(..., description="Unique pipeline identifier")
    name: str = Field(..., description="Human-readable pipeline name")
    description: Optional[str] = Field(default=None, description="Pipeline description")
    sources: List[DataSource] = Field(..., description="Data sources")
    transformations: List[DataTransformation] = Field(..., description="Data transformations")
    outputs: List[DataOutput] = Field(..., description="Data outputs")
    processing_config: ProcessingConfig = Field(default_factory=ProcessingConfig, description="Processing configuration")
    schedule_config: Optional[Dict[str, Any]] = Field(default=None, description="Scheduling configuration")
    monitoring_config: Dict[str, Any] = Field(default_factory=dict, description="Monitoring configuration")
    enabled: bool = Field(default=True, description="Whether pipeline is enabled")
    tags: List[str] = Field(default_factory=list, description="Pipeline tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PipelineExecution(Base):
    """Pipeline execution record"""
    __tablename__ = "pipeline_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id = Column(String, nullable=False, index=True)
    execution_id = Column(String, nullable=False)
    status = Column(String, nullable=False, default=PipelineStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    records_processed = Column(BigInteger, default=0)
    records_output = Column(BigInteger, default=0)
    error_count = Column(Integer, default=0)
    quality_score = Column(Float, nullable=True)
    execution_log = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    resource_usage = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@dataclass
class PipelineContext:
    """Pipeline execution context"""
    pipeline_id: str
    execution_id: str
    started_at: datetime
    checkpoints: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class DataChunk:
    """Data processing chunk"""
    chunk_id: str
    data: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_id: str = ""
    size: int = field(init=False)
    
    def __post_init__(self):
        self.size = len(self.data)


class DataPipelineConfig(ServiceConfig):
    """Data pipeline service configuration"""
    # Database settings
    database_url: str = Field(..., description="Database connection URL")
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_timeout: int = Field(default=30, description="Database query timeout")
    
    # Redis settings for coordination
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=3, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # Processing settings
    default_chunk_size: int = Field(default=10000, description="Default data chunk size")
    max_memory_usage_mb: int = Field(default=4096, description="Maximum memory usage")
    temp_storage_path: str = Field(default="/tmp/pipeline", description="Temporary storage path")
    
    # Quality settings
    enable_data_profiling: bool = Field(default=True, description="Enable data profiling")
    enable_lineage_tracking: bool = Field(default=True, description="Enable data lineage tracking")
    quality_threshold: float = Field(default=0.95, description="Default quality threshold")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable pipeline metrics")
    metrics_retention_days: int = Field(default=30, description="Metrics retention period")


class DataPipelineTemplate(BaseMicroservice):
    """
    Enterprise Data Pipeline Template
    
    Provides comprehensive ETL pipeline capabilities with:
    - Multi-source data extraction
    - Parallel processing and optimization
    - Data quality validation
    - Schema evolution handling
    - Fault tolerance and recovery
    """
    
    def __init__(self, config: DataPipelineConfig):
        super().__init__(config)
        self.config = config
        self.database_engine = None
        self.redis_client: Optional[redis.Redis] = None
        self.registered_transformations: Dict[str, Callable] = {}
        self.active_pipelines: Dict[str, PipelineDefinition] = {}
        self.running_executions: Dict[str, PipelineContext] = {}
        self.data_context: Optional[DataContext] = None
        self.thread_executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
        self.process_executor = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
        
        # Metrics
        self.pipelines_executed_total = Counter(
            'data_pipeline_executions_total',
            'Total pipeline executions',
            ['pipeline_id', 'status']
        )
        self.pipeline_duration_seconds = Histogram(
            'data_pipeline_duration_seconds',
            'Pipeline execution duration',
            ['pipeline_id']
        )
        self.records_processed_total = Counter(
            'data_pipeline_records_processed_total',
            'Total records processed',
            ['pipeline_id', 'source_id']
        )
        self.data_quality_score = Gauge(
            'data_pipeline_quality_score',
            'Data quality score',
            ['pipeline_id']
        )
        self.active_pipelines_gauge = Gauge(
            'data_pipeline_active_pipelines',
            'Number of active pipeline executions'
        )
    
    async def initialize(self) -> None:
        """Initialize data pipeline service"""
        try:
            logger.info("Initializing data pipeline service")
            
            # Initialize database connection
            await self._initialize_database()
            
            # Initialize Redis client
            await self._initialize_redis()
            
            # Initialize data quality context
            if self.config.enable_data_profiling:
                await self._initialize_data_context()
            
            # Create temporary storage directory
            Path(self.config.temp_storage_path).mkdir(parents=True, exist_ok=True)
            
            logger.info("Data pipeline service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize data pipeline service: {e}")
            raise
    
    async def _initialize_database(self) -> None:
        """Initialize database connection"""
        self.database_engine = create_async_engine(
            self.config.database_url,
            pool_size=self.config.database_pool_size,
            echo=False
        )
        
        # Test connection
        async with self.database_engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        logger.info("Database connection established")
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=False  # Keep bytes for binary data
        )
        
        # Test connection
        await self.redis_client.ping()
        logger.info("Redis connection established")
    
    async def _initialize_data_context(self) -> None:
        """Initialize Great Expectations data context"""
        try:
            # Initialize minimal data context for validation
            self.data_context = DataContext()
            logger.info("Data quality context initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize data context: {e}")
            self.data_context = None
    
    async def register_transformation(self, name: str, func: Callable) -> None:
        """Register a data transformation function"""
        self.registered_transformations[name] = func
        logger.info(f"Registered transformation function: {name}")
    
    async def create_pipeline(self, pipeline_def: PipelineDefinition) -> Dict[str, Any]:
        """Create a new data pipeline"""
        try:
            # Validate pipeline definition
            await self._validate_pipeline_definition(pipeline_def)
            
            # Store pipeline definition
            self.active_pipelines[pipeline_def.id] = pipeline_def
            
            # Persist pipeline definition
            await self._persist_pipeline_definition(pipeline_def)
            
            logger.info(f"Created data pipeline: {pipeline_def.id}")
            
            return {
                "pipeline_id": pipeline_def.id,
                "name": pipeline_def.name,
                "status": "created",
                "sources": len(pipeline_def.sources),
                "transformations": len(pipeline_def.transformations),
                "outputs": len(pipeline_def.outputs)
            }
            
        except Exception as e:
            logger.error(f"Failed to create pipeline {pipeline_def.id}: {e}")
            raise
    
    async def execute_pipeline(self, pipeline_id: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Execute a data pipeline"""
        if pipeline_id not in self.active_pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        pipeline_def = self.active_pipelines[pipeline_id]
        execution_id = str(uuid.uuid4())
        
        # Create execution context
        context = PipelineContext(
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            started_at=datetime.utcnow()
        )
        
        self.running_executions[execution_id] = context
        
        # Start pipeline execution asynchronously
        asyncio.create_task(self._execute_pipeline_async(pipeline_def, context, parameters or {}))
        
        # Update metrics
        self.active_pipelines_gauge.inc()
        
        logger.info(f"Started pipeline execution: {execution_id}")
        return execution_id
    
    async def _execute_pipeline_async(
        self, pipeline_def: PipelineDefinition, context: PipelineContext, parameters: Dict[str, Any]
    ) -> None:
        """Execute pipeline asynchronously"""
        start_time = datetime.utcnow()
        
        try:
            # Record pipeline start
            await self._record_pipeline_execution(
                context, PipelineStatus.RUNNING, start_time
            )
            
            # Extract data from sources
            extracted_data = await self._extract_data(pipeline_def.sources, context)
            
            # Apply transformations
            transformed_data = await self._apply_transformations(
                extracted_data, pipeline_def.transformations, context
            )
            
            # Validate data quality
            if pipeline_def.transformations:
                quality_score = await self._validate_data_quality(
                    transformed_data, pipeline_def.transformations, context
                )
                context.metrics["quality_score"] = quality_score
                self.data_quality_score.labels(pipeline_id=pipeline_def.id).set(quality_score)
            
            # Load data to outputs
            await self._load_data(transformed_data, pipeline_def.outputs, context)
            
            # Calculate execution time
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Record successful completion
            await self._record_pipeline_execution(
                context, PipelineStatus.COMPLETED, start_time, duration
            )
            
            # Update metrics
            self.pipelines_executed_total.labels(
                pipeline_id=pipeline_def.id, status='completed'
            ).inc()
            self.pipeline_duration_seconds.labels(pipeline_id=pipeline_def.id).observe(duration)
            
            logger.info(f"Pipeline {pipeline_def.id} completed successfully in {duration:.2f}s")
            
        except Exception as e:
            # Handle failure
            duration = (datetime.utcnow() - start_time).total_seconds()
            context.errors.append(str(e))
            
            await self._record_pipeline_execution(
                context, PipelineStatus.FAILED, start_time, duration, str(e)
            )
            
            # Update metrics
            self.pipelines_executed_total.labels(
                pipeline_id=pipeline_def.id, status='failed'
            ).inc()
            
            logger.error(f"Pipeline {pipeline_def.id} failed: {e}")
            
        finally:
            # Cleanup
            self.active_pipelines_gauge.dec()
            if context.execution_id in self.running_executions:
                del self.running_executions[context.execution_id]
    
    async def _extract_data(self, sources: List[DataSource], context: PipelineContext) -> Dict[str, List[DataChunk]]:
        """Extract data from all sources"""
        extracted_data = {}
        
        for source in sources:
            if not source.enabled:
                continue
            
            try:
                logger.info(f"Extracting data from source: {source.id}")
                
                # Extract based on source type
                if source.source_type == DataSourceType.DATABASE:
                    chunks = await self._extract_from_database(source, context)
                elif source.source_type == DataSourceType.FILE:
                    chunks = await self._extract_from_file(source, context)
                elif source.source_type == DataSourceType.API:
                    chunks = await self._extract_from_api(source, context)
                else:
                    raise ValueError(f"Unsupported source type: {source.source_type}")
                
                extracted_data[source.id] = chunks
                
                # Update metrics
                total_records = sum(chunk.size for chunk in chunks)
                self.records_processed_total.labels(
                    pipeline_id=context.pipeline_id, source_id=source.id
                ).inc(total_records)
                
                logger.info(f"Extracted {total_records} records from {source.id}")
                
            except Exception as e:
                logger.error(f"Failed to extract from source {source.id}: {e}")
                context.errors.append(f"Source {source.id}: {str(e)}")
                extracted_data[source.id] = []
        
        return extracted_data
    
    async def _extract_from_database(self, source: DataSource, context: PipelineContext) -> List[DataChunk]:
        """Extract data from database source"""
        chunks = []
        
        try:
            query = source.query_config.get("query", "")
            chunk_size = source.query_config.get("chunk_size", self.config.default_chunk_size)
            
            # Handle incremental loading
            if source.incremental_config:
                query = self._apply_incremental_filter(query, source.incremental_config, context)
            
            # Execute query in chunks
            async with self.database_engine.begin() as conn:
                # Get total count for progress tracking
                count_query = f"SELECT COUNT(*) FROM ({query}) as subquery"
                result = await conn.execute(count_query)
                total_records = result.scalar()
                
                # Process in chunks
                offset = 0
                chunk_index = 0
                
                while offset < total_records:
                    chunk_query = f"{query} LIMIT {chunk_size} OFFSET {offset}"
                    chunk_result = await conn.execute(chunk_query)
                    
                    # Convert to DataFrame
                    rows = chunk_result.fetchall()
                    if not rows:
                        break
                    
                    columns = chunk_result.keys()
                    df = pd.DataFrame(rows, columns=columns)
                    
                    chunk = DataChunk(
                        chunk_id=f"{source.id}_{chunk_index}",
                        data=df,
                        source_id=source.id,
                        metadata={"offset": offset, "query": chunk_query}
                    )
                    
                    chunks.append(chunk)
                    offset += chunk_size
                    chunk_index += 1
                    
                    # Update checkpoint
                    context.checkpoints[f"extract_{source.id}"] = offset
            
            return chunks
            
        except Exception as e:
            logger.error(f"Database extraction failed for {source.id}: {e}")
            raise
    
    async def _extract_from_file(self, source: DataSource, context: PipelineContext) -> List[DataChunk]:
        """Extract data from file source"""
        chunks = []
        
        try:
            file_path = source.connection_config.get("file_path", "")
            file_type = source.connection_config.get("file_type", "csv")
            chunk_size = source.query_config.get("chunk_size", self.config.default_chunk_size)
            
            if file_type == "csv":
                # Read CSV in chunks
                chunk_index = 0
                async for chunk_df in self._read_csv_chunks(file_path, chunk_size):
                    chunk = DataChunk(
                        chunk_id=f"{source.id}_{chunk_index}",
                        data=chunk_df,
                        source_id=source.id,
                        metadata={"file_path": file_path, "chunk_index": chunk_index}
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            
            elif file_type == "parquet":
                # Read Parquet file
                table = pq.read_table(file_path)
                df = table.to_pandas()
                
                # Split into chunks
                for i in range(0, len(df), chunk_size):
                    chunk_df = df.iloc[i:i + chunk_size]
                    chunk = DataChunk(
                        chunk_id=f"{source.id}_{i // chunk_size}",
                        data=chunk_df,
                        source_id=source.id,
                        metadata={"file_path": file_path, "chunk_start": i}
                    )
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"File extraction failed for {source.id}: {e}")
            raise
    
    async def _extract_from_api(self, source: DataSource, context: PipelineContext) -> List[DataChunk]:
        """Extract data from API source"""
        chunks = []
        
        try:
            base_url = source.connection_config.get("base_url", "")
            endpoints = source.connection_config.get("endpoints", [])
            headers = source.connection_config.get("headers", {})
            
            async with aiohttp.ClientSession(headers=headers) as session:
                for endpoint_config in endpoints:
                    endpoint = endpoint_config.get("path", "")
                    params = endpoint_config.get("params", {})
                    
                    async with session.get(f"{base_url}{endpoint}", params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Convert to DataFrame
                            if isinstance(data, list):
                                df = pd.DataFrame(data)
                            elif isinstance(data, dict) and "data" in data:
                                df = pd.DataFrame(data["data"])
                            else:
                                df = pd.DataFrame([data])
                            
                            chunk = DataChunk(
                                chunk_id=f"{source.id}_{endpoint}",
                                data=df,
                                source_id=source.id,
                                metadata={"endpoint": endpoint, "status": response.status}
                            )
                            chunks.append(chunk)
                        else:
                            logger.warning(f"API request failed: {response.status}")
            
            return chunks
            
        except Exception as e:
            logger.error(f"API extraction failed for {source.id}: {e}")
            raise
    
    async def _apply_transformations(
        self, extracted_data: Dict[str, List[DataChunk]], 
        transformations: List[DataTransformation], 
        context: PipelineContext
    ) -> Dict[str, List[DataChunk]]:
        """Apply data transformations"""
        current_data = extracted_data.copy()
        
        # Sort transformations by dependencies
        sorted_transformations = self._sort_transformations_by_dependencies(transformations)
        
        for transformation in sorted_transformations:
            if not transformation.enabled:
                continue
            
            try:
                logger.info(f"Applying transformation: {transformation.id}")
                
                # Get transformation function
                if transformation.function_name not in self.registered_transformations:
                    raise ValueError(f"Transformation function not registered: {transformation.function_name}")
                
                transform_func = self.registered_transformations[transformation.function_name]
                
                # Apply transformation to all data chunks
                transformed_chunks = []
                for source_id, chunks in current_data.items():
                    for chunk in chunks:
                        try:
                            # Apply transformation
                            transformed_df = await self._apply_single_transformation(
                                chunk.data, transform_func, transformation.parameters
                            )
                            
                            # Create new chunk
                            new_chunk = DataChunk(
                                chunk_id=f"{chunk.chunk_id}_{transformation.id}",
                                data=transformed_df,
                                source_id=chunk.source_id,
                                metadata={
                                    **chunk.metadata,
                                    "transformation": transformation.id,
                                    "original_size": chunk.size
                                }
                            )
                            transformed_chunks.append(new_chunk)
                            
                        except Exception as e:
                            logger.error(f"Transformation failed for chunk {chunk.chunk_id}: {e}")
                            context.errors.append(f"Transformation {transformation.id}, chunk {chunk.chunk_id}: {str(e)}")
                
                # Update current data with transformed chunks
                if transformed_chunks:
                    current_data[f"transformed_{transformation.id}"] = transformed_chunks
                
                logger.info(f"Transformation {transformation.id} completed")
                
            except Exception as e:
                logger.error(f"Failed to apply transformation {transformation.id}: {e}")
                context.errors.append(f"Transformation {transformation.id}: {str(e)}")
        
        return current_data
    
    async def _apply_single_transformation(
        self, df: pd.DataFrame, transform_func: Callable, parameters: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply a single transformation to a DataFrame"""
        if asyncio.iscoroutinefunction(transform_func):
            return await transform_func(df, **parameters)
        else:
            # Run in thread pool for CPU-intensive operations
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.thread_executor, lambda: transform_func(df, **parameters)
            )
    
    async def _validate_data_quality(
        self, data: Dict[str, List[DataChunk]], 
        transformations: List[DataTransformation], 
        context: PipelineContext
    ) -> float:
        """Validate data quality using defined rules"""
        total_rules = 0
        passed_rules = 0
        
        for transformation in transformations:
            for rule in transformation.quality_rules:
                if not rule.enabled:
                    continue
                
                total_rules += 1
                
                try:
                    # Apply quality rule to data chunks
                    rule_passed = await self._apply_quality_rule(rule, data, context)
                    if rule_passed:
                        passed_rules += 1
                    else:
                        logger.warning(f"Quality rule failed: {rule.name}")
                        
                except Exception as e:
                    logger.error(f"Quality rule validation failed for {rule.name}: {e}")
        
        # Calculate quality score
        quality_score = passed_rules / total_rules if total_rules > 0 else 1.0
        return quality_score
    
    async def _apply_quality_rule(
        self, rule: DataQualityRule, data: Dict[str, List[DataChunk]], context: PipelineContext
    ) -> bool:
        """Apply a single data quality rule"""
        try:
            # Simple rule implementation
            # In practice, this would integrate with Great Expectations or similar
            
            for source_id, chunks in data.items():
                for chunk in chunks:
                    df = chunk.data
                    
                    if rule.rule_type == "completeness":
                        # Check for null values
                        if rule.column and rule.column in df.columns:
                            null_ratio = df[rule.column].isnull().sum() / len(df)
                            if null_ratio > (1 - rule.threshold):
                                return False
                    
                    elif rule.rule_type == "uniqueness":
                        # Check for duplicate values
                        if rule.column and rule.column in df.columns:
                            unique_ratio = df[rule.column].nunique() / len(df)
                            if unique_ratio < rule.threshold:
                                return False
                    
                    elif rule.rule_type == "validity":
                        # Check data validity using expression
                        try:
                            valid_mask = df.eval(rule.expression)
                            valid_ratio = valid_mask.sum() / len(df)
                            if valid_ratio < rule.threshold:
                                return False
                        except Exception:
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Quality rule application failed: {e}")
            return False
    
    async def _load_data(
        self, data: Dict[str, List[DataChunk]], outputs: List[DataOutput], context: PipelineContext
    ) -> None:
        """Load data to output destinations"""
        for output in outputs:
            if not output.enabled:
                continue
            
            try:
                logger.info(f"Loading data to output: {output.id}")
                
                # Load based on destination type
                if output.destination_type == OutputDestination.DATABASE:
                    await self._load_to_database(data, output, context)
                elif output.destination_type == OutputDestination.FILE:
                    await self._load_to_file(data, output, context)
                elif output.destination_type == OutputDestination.SEARCH_INDEX:
                    await self._load_to_search_index(data, output, context)
                else:
                    raise ValueError(f"Unsupported output type: {output.destination_type}")
                
                logger.info(f"Data loaded to output: {output.id}")
                
            except Exception as e:
                logger.error(f"Failed to load to output {output.id}: {e}")
                context.errors.append(f"Output {output.id}: {str(e)}")
    
    async def _load_to_database(
        self, data: Dict[str, List[DataChunk]], output: DataOutput, context: PipelineContext
    ) -> None:
        """Load data to database"""
        table_name = output.connection_config.get("table_name", "")
        if_exists = output.connection_config.get("if_exists", "append")
        
        async with self.database_engine.begin() as conn:
            for source_id, chunks in data.items():
                for chunk in chunks:
                    # Convert DataFrame to SQL
                    chunk.data.to_sql(
                        table_name,
                        conn,
                        if_exists=if_exists,
                        index=False,
                        method="multi"
                    )
    
    async def _load_to_file(
        self, data: Dict[str, List[DataChunk]], output: DataOutput, context: PipelineContext
    ) -> None:
        """Load data to file"""
        file_path = output.connection_config.get("file_path", "")
        file_format = output.format_config.get("format", "parquet")
        
        # Combine all chunks
        all_dataframes = []
        for source_id, chunks in data.items():
            for chunk in chunks:
                all_dataframes.append(chunk.data)
        
        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            
            if file_format == "parquet":
                combined_df.to_parquet(file_path, index=False)
            elif file_format == "csv":
                combined_df.to_csv(file_path, index=False)
            elif file_format == "json":
                combined_df.to_json(file_path, orient="records")
    
    async def _load_to_search_index(
        self, data: Dict[str, List[DataChunk]], output: DataOutput, context: PipelineContext
    ) -> None:
        """Load data to search index (Elasticsearch)"""
        es_config = output.connection_config
        index_name = es_config.get("index_name", "")
        
        async with AsyncElasticsearch([es_config.get("host", "localhost:9200")]) as es:
            for source_id, chunks in data.items():
                for chunk in chunks:
                    # Bulk index documents
                    documents = chunk.data.to_dict("records")
                    
                    body = []
                    for doc in documents:
                        body.append({"index": {"_index": index_name}})
                        body.append(doc)
                    
                    if body:
                        await es.bulk(body=body)
    
    async def _read_csv_chunks(self, file_path: str, chunk_size: int) -> AsyncIterator[pd.DataFrame]:
        """Read CSV file in chunks"""
        def read_chunk():
            return pd.read_csv(file_path, chunksize=chunk_size)
        
        loop = asyncio.get_event_loop()
        chunk_reader = await loop.run_in_executor(self.thread_executor, read_chunk)
        
        for chunk in chunk_reader:
            yield chunk
    
    def _sort_transformations_by_dependencies(
        self, transformations: List[DataTransformation]
    ) -> List[DataTransformation]:
        """Sort transformations by their dependencies"""
        # Simple topological sort
        sorted_transformations = []
        remaining = transformations.copy()
        
        while remaining:
            # Find transformations with no unresolved dependencies
            ready = []
            for transformation in remaining:
                dependencies_resolved = all(
                    any(t.id == dep for t in sorted_transformations)
                    for dep in transformation.dependencies
                ) if transformation.dependencies else True
                
                if dependencies_resolved:
                    ready.append(transformation)
            
            if not ready:
                # Circular dependency detected
                logger.warning("Circular dependency detected in transformations")
                ready = remaining  # Process remaining anyway
            
            sorted_transformations.extend(ready)
            for transformation in ready:
                remaining.remove(transformation)
        
        return sorted_transformations
    
    def _apply_incremental_filter(
        self, query: str, incremental_config: Dict[str, Any], context: PipelineContext
    ) -> str:
        """Apply incremental loading filter to query"""
        # Simple implementation - would be more sophisticated in practice
        timestamp_column = incremental_config.get("timestamp_column", "updated_at")
        last_sync = incremental_config.get("last_sync", "1970-01-01")
        
        if "WHERE" in query.upper():
            return f"{query} AND {timestamp_column} > '{last_sync}'"
        else:
            return f"{query} WHERE {timestamp_column} > '{last_sync}'"
    
    async def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline status and metrics"""
        if pipeline_id not in self.active_pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        pipeline_def = self.active_pipelines[pipeline_id]
        
        # Get recent executions
        executions = await self._get_recent_executions(pipeline_id, limit=10)
        
        # Get running execution if any
        running_execution = None
        for execution_id, context in self.running_executions.items():
            if context.pipeline_id == pipeline_id:
                running_execution = {
                    "execution_id": execution_id,
                    "started_at": context.started_at.isoformat(),
                    "duration": (datetime.utcnow() - context.started_at).total_seconds(),
                    "checkpoints": context.checkpoints,
                    "metrics": context.metrics,
                    "errors": context.errors
                }
                break
        
        return {
            "pipeline_id": pipeline_id,
            "name": pipeline_def.name,
            "enabled": pipeline_def.enabled,
            "sources": len(pipeline_def.sources),
            "transformations": len(pipeline_def.transformations),
            "outputs": len(pipeline_def.outputs),
            "current_execution": running_execution,
            "recent_executions": executions
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            # Check database connectivity
            db_healthy = False
            try:
                async with self.database_engine.begin() as conn:
                    await conn.execute("SELECT 1")
                db_healthy = True
            except Exception:
                pass
            
            # Check Redis connectivity
            redis_healthy = False
            try:
                await self.redis_client.ping()
                redis_healthy = True
            except Exception:
                pass
            
            return {
                "service": "data_pipeline_template",
                "status": "healthy" if db_healthy and redis_healthy else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "active_pipelines": len(self.active_pipelines),
                    "running_executions": len(self.running_executions),
                    "database_connected": db_healthy,
                    "redis_connected": redis_healthy
                }
            }
            
        except Exception as e:
            return {
                "service": "data_pipeline_template",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _validate_pipeline_definition(self, pipeline_def: PipelineDefinition) -> None:
        """Validate pipeline definition"""
        # Check that all transformation functions are registered
        for transformation in pipeline_def.transformations:
            if transformation.function_name not in self.registered_transformations:
                raise ValueError(f"Transformation function not registered: {transformation.function_name}")
        
        # Check transformation dependencies
        transformation_ids = {t.id for t in pipeline_def.transformations}
        for transformation in pipeline_def.transformations:
            for dep in transformation.dependencies:
                if dep not in transformation_ids:
                    raise ValueError(f"Transformation dependency not found: {dep}")
    
    async def _record_pipeline_execution(
        self, context: PipelineContext, status: PipelineStatus,
        started_at: datetime, duration: float = None, error_message: str = None
    ) -> None:
        """Record pipeline execution result"""
        execution_data = {
            "pipeline_id": context.pipeline_id,
            "execution_id": context.execution_id,
            "status": status.value,
            "started_at": started_at.isoformat(),
            "duration_seconds": duration,
            "checkpoints": context.checkpoints,
            "metrics": context.metrics,
            "errors": context.errors,
            "error_message": error_message
        }
        
        # Store in Redis
        key = f"execution:{context.pipeline_id}:{context.execution_id}"
        await self.redis_client.setex(
            key,
            timedelta(days=self.config.metrics_retention_days).total_seconds(),
            json.dumps(execution_data, default=str)
        )
    
    async def _get_recent_executions(self, pipeline_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent pipeline executions"""
        pattern = f"execution:{pipeline_id}:*"
        keys = await self.redis_client.keys(pattern)
        
        executions = []
        for key in keys[:limit]:
            data = await self.redis_client.get(key)
            if data:
                executions.append(json.loads(data))
        
        # Sort by started_at desc
        executions.sort(key=lambda x: x['started_at'], reverse=True)
        return executions[:limit]
    
    async def _persist_pipeline_definition(self, pipeline_def: PipelineDefinition) -> None:
        """Persist pipeline definition to Redis"""
        key = f"pipeline_def:{pipeline_def.id}"
        value = pipeline_def.json()
        await self.redis_client.set(key, value)
    
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        try:
            logger.info("Shutting down data pipeline service")
            
            # Stop all running executions gracefully
            for execution_id in list(self.running_executions.keys()):
                logger.info(f"Stopping execution: {execution_id}")
            
            # Shutdown executors
            self.thread_executor.shutdown(wait=True)
            self.process_executor.shutdown(wait=True)
            
            # Close database connection
            if self.database_engine:
                await self.database_engine.dispose()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Data pipeline service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")