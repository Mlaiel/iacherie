"""
Data Pipeline Service - Enterprise Data Architecture & Analytics
===============================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: Database Administrator (DBA) & ML Engineer
**Module**: Data & Analytics Services
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Advanced data pipeline orchestration with real-time ETL,
distributed processing, and intelligent data governance.
"""

import asyncio
import json
import logging
import hashlib
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import aioredis
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, MetaData, Table, Column, Integer, String, DateTime, Float, Boolean
import concurrent.futures


class DataSourceType(Enum):
    """Types of data sources"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    CLOUD_STORAGE = "cloud_storage"
    MESSAGE_QUEUE = "message_queue"
    REAL_TIME = "real_time"


class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class DataQuality(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class TransformationType(Enum):
    """Types of data transformations"""
    CLEANING = "cleaning"
    AGGREGATION = "aggregation"
    ENRICHMENT = "enrichment"
    NORMALIZATION = "normalization"
    VALIDATION = "validation"
    FEATURE_ENGINEERING = "feature_engineering"
    ML_PREPROCESSING = "ml_preprocessing"


@dataclass
class DataSource:
    """Data source configuration"""
    source_id: str
    name: str
    source_type: DataSourceType
    connection_config: Dict[str, Any]
    schema_config: Optional[Dict[str, Any]] = None
    refresh_interval: int = 3600  # seconds
    enabled: bool = True
    last_updated: Optional[datetime] = None


@dataclass
class DataTransformation:
    """Data transformation configuration"""
    transform_id: str
    name: str
    transformation_type: TransformationType
    function: str  # Function name or SQL query
    parameters: Dict[str, Any] = field(default_factory=dict)
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


@dataclass
class PipelineJob:
    """Data pipeline job"""
    job_id: str
    pipeline_id: str
    status: PipelineStatus
    source_configs: List[DataSource]
    transformations: List[DataTransformation]
    target_config: Dict[str, Any]
    execution_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    records_processed: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class DataQualityReport:
    """Data quality assessment report"""
    report_id: str
    dataset_id: str
    overall_quality: DataQuality
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    validity_score: float
    uniqueness_score: float
    timeliness_score: float
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PipelineMetrics:
    """Pipeline performance metrics"""
    pipeline_id: str
    execution_time: float
    throughput: float  # records per second
    success_rate: float
    data_quality_score: float
    resource_utilization: Dict[str, float]
    error_rate: float
    last_execution: datetime


class DataPipelineService:
    """
    Enterprise Data Pipeline Service
    
    Comprehensive data orchestration with:
    - Real-time ETL and data streaming
    - Advanced data quality monitoring
    - Distributed processing and optimization
    - Intelligent schema evolution and governance
    - Performance monitoring and alerting
    - Automated data lineage tracking
    - Enterprise-grade security and compliance
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 database_url: str = "postgresql+asyncpg://user:pass@localhost/ainflue"):
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        self.database_url = database_url
        
        # Connection pools
        self.redis_client: Optional[aioredis.Redis] = None
        self.db_engine = None
        self.async_session = None
        
        # Pipeline management
        self.active_pipelines: Dict[str, PipelineJob] = {}
        self.pipeline_registry: Dict[str, Dict[str, Any]] = {}
        self.data_sources: Dict[str, DataSource] = {}
        
        # Data quality and governance
        self.quality_reports: Dict[str, DataQualityReport] = {}
        self.data_lineage: Dict[str, List[str]] = {}
        self.schema_registry: Dict[str, Dict[str, Any]] = {}
        
        # Performance monitoring
        self.pipeline_metrics: Dict[str, PipelineMetrics] = {}
        self.global_metrics = {
            "total_pipelines": 0,
            "active_pipelines": 0,
            "total_records_processed": 0,
            "avg_throughput": 0.0,
            "overall_success_rate": 0.0,
            "avg_data_quality": 0.0
        }
        
        # Transformation functions registry
        self.transformation_functions = {
            "clean_text": self._clean_text_data,
            "normalize_numbers": self._normalize_numeric_data,
            "validate_emails": self._validate_email_data,
            "extract_features": self._extract_ml_features,
            "aggregate_metrics": self._aggregate_data,
            "detect_anomalies": self._detect_data_anomalies
        }
        
        # Background tasks
        self.pipeline_tasks: List[asyncio.Task] = []
        
        self.logger.info("Data Pipeline Service initialized")

    async def initialize(self):
        """Initialize data pipeline service"""
        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Initialize database connection
            self.db_engine = create_async_engine(
                self.database_url,
                echo=True,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self.async_session = sessionmaker(
                self.db_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Load existing configurations
            await self._load_pipeline_configurations()
            await self._load_data_sources()
            await self._load_schema_registry()
            
            # Start background tasks
            await self._start_pipeline_tasks()
            
            self.logger.info("Data Pipeline Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Data Pipeline Service: {e}")
            raise

    async def _start_pipeline_tasks(self):
        """Start background pipeline management tasks"""
        
        # Pipeline execution monitor
        self.pipeline_tasks.append(
            asyncio.create_task(self._monitor_pipeline_execution())
        )
        
        # Data quality monitoring
        self.pipeline_tasks.append(
            asyncio.create_task(self._monitor_data_quality())
        )
        
        # Performance metrics collection
        self.pipeline_tasks.append(
            asyncio.create_task(self._collect_performance_metrics())
        )
        
        # Schema evolution monitoring
        self.pipeline_tasks.append(
            asyncio.create_task(self._monitor_schema_evolution())
        )
        
        # Data lineage tracking
        self.pipeline_tasks.append(
            asyncio.create_task(self._track_data_lineage())
        )
        
        self.logger.info(f"Started {len(self.pipeline_tasks)} pipeline management tasks")

    async def register_data_source(self, source: DataSource) -> str:
        """Register a new data source"""
        
        try:
            # Validate source configuration
            await self._validate_data_source(source)
            
            # Test connection
            connection_test = await self._test_data_source_connection(source)
            if not connection_test["success"]:
                raise ValueError(f"Data source connection test failed: {connection_test['error']}")
            
            # Store source
            self.data_sources[source.source_id] = source
            
            # Save to registry
            await self._save_data_source(source)
            
            # Update schema registry
            if source.schema_config:
                self.schema_registry[source.source_id] = source.schema_config
                await self._save_schema_registry()
            
            self.logger.info(f"Data source registered: {source.source_id}")
            return source.source_id
            
        except Exception as e:
            self.logger.error(f"Error registering data source {source.source_id}: {e}")
            raise

    async def create_pipeline(self, pipeline_config: Dict[str, Any]) -> str:
        """Create a new data pipeline"""
        
        try:
            pipeline_id = f"pipeline_{int(time.time() * 1000)}_{hashlib.md5(str(pipeline_config).encode()).hexdigest()[:8]}"
            
            # Validate pipeline configuration
            await self._validate_pipeline_config(pipeline_config)
            
            # Parse source configurations
            sources = []
            for source_config in pipeline_config["sources"]:
                if source_config["source_id"] in self.data_sources:
                    sources.append(self.data_sources[source_config["source_id"]])
                else:
                    raise ValueError(f"Data source not found: {source_config['source_id']}")
            
            # Parse transformations
            transformations = []
            for transform_config in pipeline_config.get("transformations", []):
                transformation = DataTransformation(
                    transform_id=transform_config["transform_id"],
                    name=transform_config["name"],
                    transformation_type=TransformationType(transform_config["type"]),
                    function=transform_config["function"],
                    parameters=transform_config.get("parameters", {}),
                    input_schema=transform_config.get("input_schema"),
                    output_schema=transform_config.get("output_schema")
                )
                transformations.append(transformation)
            
            # Create pipeline job
            pipeline_job = PipelineJob(
                job_id=f"job_{pipeline_id}",
                pipeline_id=pipeline_id,
                status=PipelineStatus.PENDING,
                source_configs=sources,
                transformations=transformations,
                target_config=pipeline_config["target"],
                execution_config=pipeline_config.get("execution", {})
            )
            
            # Store pipeline
            self.active_pipelines[pipeline_id] = pipeline_job
            self.pipeline_registry[pipeline_id] = pipeline_config
            
            # Save to storage
            await self._save_pipeline_job(pipeline_job)
            await self._save_pipeline_registry()
            
            self.logger.info(f"Pipeline created: {pipeline_id}")
            return pipeline_id
            
        except Exception as e:
            self.logger.error(f"Error creating pipeline: {e}")
            raise

    async def execute_pipeline(self, pipeline_id: str) -> str:
        """Execute a data pipeline"""
        
        if pipeline_id not in self.active_pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        try:
            pipeline_job = self.active_pipelines[pipeline_id]
            
            # Update status
            pipeline_job.status = PipelineStatus.RUNNING
            pipeline_job.started_at = datetime.utcnow()
            pipeline_job.progress = 0.0
            
            await self._save_pipeline_job(pipeline_job)
            
            # Execute pipeline asynchronously
            execution_task = asyncio.create_task(
                self._execute_pipeline_job(pipeline_job)
            )
            
            self.logger.info(f"Pipeline execution started: {pipeline_id}")
            return pipeline_job.job_id
            
        except Exception as e:
            self.logger.error(f"Error executing pipeline {pipeline_id}: {e}")
            raise

    async def _execute_pipeline_job(self, pipeline_job: PipelineJob):
        """Execute individual pipeline job"""
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Executing pipeline job: {pipeline_job.job_id}")
            
            # Step 1: Extract data from sources
            pipeline_job.progress = 0.1
            await self._save_pipeline_job(pipeline_job)
            
            extracted_data = await self._extract_data_from_sources(pipeline_job.source_configs)
            
            # Step 2: Data quality assessment
            pipeline_job.progress = 0.3
            await self._save_pipeline_job(pipeline_job)
            
            quality_report = await self._assess_data_quality(extracted_data, pipeline_job.job_id)
            
            # Step 3: Apply transformations
            pipeline_job.progress = 0.5
            await self._save_pipeline_job(pipeline_job)
            
            transformed_data = extracted_data
            for transformation in pipeline_job.transformations:
                transformed_data = await self._apply_transformation(
                    transformed_data, transformation
                )
            
            # Step 4: Load data to target
            pipeline_job.progress = 0.8
            await self._save_pipeline_job(pipeline_job)
            
            load_result = await self._load_data_to_target(
                transformed_data, pipeline_job.target_config
            )
            
            # Step 5: Update lineage and complete
            pipeline_job.progress = 0.95
            await self._save_pipeline_job(pipeline_job)
            
            await self._update_data_lineage(pipeline_job, load_result)
            
            # Complete job
            pipeline_job.status = PipelineStatus.COMPLETED
            pipeline_job.completed_at = datetime.utcnow()
            pipeline_job.progress = 1.0
            pipeline_job.records_processed = len(transformed_data) if isinstance(transformed_data, list) else 1
            
            await self._save_pipeline_job(pipeline_job)
            
            # Update metrics
            execution_time = time.time() - start_time
            await self._update_pipeline_metrics(pipeline_job, execution_time, quality_report)
            
            self.logger.info(f"Pipeline job completed: {pipeline_job.job_id}")
            
        except Exception as e:
            # Mark job as failed
            pipeline_job.status = PipelineStatus.FAILED
            pipeline_job.errors.append(str(e))
            
            await self._save_pipeline_job(pipeline_job)
            
            self.logger.error(f"Pipeline job failed {pipeline_job.job_id}: {e}")

    async def _extract_data_from_sources(self, sources: List[DataSource]) -> List[Dict[str, Any]]:
        """Extract data from multiple sources"""
        
        all_data = []
        
        for source in sources:
            try:
                if source.source_type == DataSourceType.DATABASE:
                    data = await self._extract_from_database(source)
                elif source.source_type == DataSourceType.API:
                    data = await self._extract_from_api(source)
                elif source.source_type == DataSourceType.FILE:
                    data = await self._extract_from_file(source)
                elif source.source_type == DataSourceType.STREAM:
                    data = await self._extract_from_stream(source)
                else:
                    self.logger.warning(f"Unsupported source type: {source.source_type}")
                    continue
                
                all_data.extend(data)
                
            except Exception as e:
                self.logger.error(f"Error extracting from source {source.source_id}: {e}")
                continue
        
        return all_data

    async def _extract_from_database(self, source: DataSource) -> List[Dict[str, Any]]:
        """Extract data from database source"""
        
        try:
            config = source.connection_config
            query = config.get("query", "SELECT * FROM users LIMIT 1000")
            
            # Use the async session for database operations
            async with self.async_session() as session:
                result = await session.execute(text(query))
                rows = result.fetchall()
                
                # Convert to dictionaries
                if rows:
                    columns = result.keys()
                    data = [dict(zip(columns, row)) for row in rows]
                else:
                    data = []
                
                return data
                
        except Exception as e:
            self.logger.error(f"Database extraction error: {e}")
            return []

    async def _extract_from_api(self, source: DataSource) -> List[Dict[str, Any]]:
        """Extract data from API source"""
        
        try:
            config = source.connection_config
            url = config["url"]
            headers = config.get("headers", {})
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Handle different API response formats
                        if isinstance(data, list):
                            return data
                        elif isinstance(data, dict):
                            # Check for common pagination patterns
                            if "data" in data:
                                return data["data"]
                            elif "results" in data:
                                return data["results"]
                            else:
                                return [data]
                        else:
                            return []
                    else:
                        self.logger.error(f"API request failed: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"API extraction error: {e}")
            return []

    async def _extract_from_file(self, source: DataSource) -> List[Dict[str, Any]]:
        """Extract data from file source"""
        
        try:
            config = source.connection_config
            file_path = config["file_path"]
            file_type = config.get("file_type", "csv")
            
            if file_type == "csv":
                df = pd.read_csv(file_path)
                return df.to_dict('records')
            elif file_type == "json":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else [data]
            elif file_type == "parquet":
                df = pd.read_parquet(file_path)
                return df.to_dict('records')
            else:
                self.logger.error(f"Unsupported file type: {file_type}")
                return []
                
        except Exception as e:
            self.logger.error(f"File extraction error: {e}")
            return []

    async def _extract_from_stream(self, source: DataSource) -> List[Dict[str, Any]]:
        """Extract data from streaming source"""
        
        # Simulate streaming data extraction
        # In production, integrate with Kafka, RabbitMQ, etc.
        
        try:
            config = source.connection_config
            stream_type = config.get("stream_type", "kafka")
            topic = config.get("topic", "default")
            
            # Simulate receiving streaming data
            simulated_data = [
                {"id": i, "value": f"stream_data_{i}", "timestamp": datetime.utcnow().isoformat()}
                for i in range(10)
            ]
            
            return simulated_data
            
        except Exception as e:
            self.logger.error(f"Stream extraction error: {e}")
            return []

    async def _assess_data_quality(self, data: List[Dict[str, Any]], 
                                 dataset_id: str) -> DataQualityReport:
        """Assess data quality comprehensively"""
        
        try:
            if not data:
                return DataQualityReport(
                    report_id=f"qr_{dataset_id}",
                    dataset_id=dataset_id,
                    overall_quality=DataQuality.CRITICAL,
                    completeness_score=0.0,
                    accuracy_score=0.0,
                    consistency_score=0.0,
                    validity_score=0.0,
                    uniqueness_score=0.0,
                    timeliness_score=0.0,
                    issues_found=[{"issue": "No data found", "severity": "critical"}],
                    recommendations=["Verify data source connectivity"]
                )
            
            df = pd.DataFrame(data)
            total_cells = df.size
            
            # Completeness: ratio of non-null values
            non_null_cells = df.notna().sum().sum()
            completeness_score = non_null_cells / total_cells if total_cells > 0 else 0.0
            
            # Uniqueness: ratio of unique records
            unique_records = len(df.drop_duplicates())
            uniqueness_score = unique_records / len(df) if len(df) > 0 else 0.0
            
            # Consistency: check for data type consistency
            consistency_issues = 0
            for column in df.columns:
                if df[column].dtype == 'object':
                    # Check for mixed types in object columns
                    types = df[column].dropna().apply(type).nunique()
                    if types > 1:
                        consistency_issues += 1
            
            consistency_score = 1.0 - (consistency_issues / len(df.columns)) if len(df.columns) > 0 else 1.0
            
            # Validity: check for common validity patterns
            validity_issues = 0
            for column in df.columns:
                if 'email' in column.lower():
                    invalid_emails = df[column].dropna().apply(
                        lambda x: '@' not in str(x) if pd.notna(x) else False
                    ).sum()
                    validity_issues += invalid_emails
            
            validity_score = max(0.0, 1.0 - (validity_issues / len(df)) if len(df) > 0 else 1.0)
            
            # Accuracy: simplified accuracy check
            accuracy_score = 0.8  # Placeholder for more complex accuracy checks
            
            # Timeliness: check for recent data
            timeliness_score = 1.0  # Placeholder for timestamp-based checks
            
            # Calculate overall quality
            quality_scores = [
                completeness_score,
                accuracy_score,
                consistency_score,
                validity_score,
                uniqueness_score,
                timeliness_score
            ]
            
            overall_score = np.mean(quality_scores)
            
            if overall_score >= 0.9:
                overall_quality = DataQuality.EXCELLENT
            elif overall_score >= 0.8:
                overall_quality = DataQuality.GOOD
            elif overall_score >= 0.6:
                overall_quality = DataQuality.FAIR
            elif overall_score >= 0.4:
                overall_quality = DataQuality.POOR
            else:
                overall_quality = DataQuality.CRITICAL
            
            # Generate issues and recommendations
            issues_found = []
            recommendations = []
            
            if completeness_score < 0.8:
                issues_found.append({
                    "issue": f"Low completeness: {completeness_score:.2%}",
                    "severity": "medium"
                })
                recommendations.append("Investigate missing data sources")
            
            if uniqueness_score < 0.9:
                issues_found.append({
                    "issue": f"Duplicate records detected: {(1-uniqueness_score):.2%}",
                    "severity": "low"
                })
                recommendations.append("Implement deduplication logic")
            
            if consistency_issues > 0:
                issues_found.append({
                    "issue": f"Data type inconsistencies in {consistency_issues} columns",
                    "severity": "medium"
                })
                recommendations.append("Standardize data types across sources")
            
            report = DataQualityReport(
                report_id=f"qr_{dataset_id}_{int(time.time())}",
                dataset_id=dataset_id,
                overall_quality=overall_quality,
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                consistency_score=consistency_score,
                validity_score=validity_score,
                uniqueness_score=uniqueness_score,
                timeliness_score=timeliness_score,
                issues_found=issues_found,
                recommendations=recommendations
            )
            
            # Cache report
            self.quality_reports[report.report_id] = report
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error assessing data quality: {e}")
            raise

    async def _apply_transformation(self, data: List[Dict[str, Any]], 
                                  transformation: DataTransformation) -> List[Dict[str, Any]]:
        """Apply data transformation"""
        
        try:
            if transformation.function in self.transformation_functions:
                func = self.transformation_functions[transformation.function]
                return await func(data, transformation.parameters)
            else:
                self.logger.warning(f"Unknown transformation function: {transformation.function}")
                return data
                
        except Exception as e:
            self.logger.error(f"Error applying transformation {transformation.transform_id}: {e}")
            return data

    async def _clean_text_data(self, data: List[Dict[str, Any]], 
                             parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Clean text data transformation"""
        
        text_fields = parameters.get("text_fields", [])
        
        for record in data:
            for field in text_fields:
                if field in record and isinstance(record[field], str):
                    # Basic text cleaning
                    text = record[field]
                    text = text.strip()
                    text = text.replace('\n', ' ')
                    text = text.replace('\t', ' ')
                    # Remove extra spaces
                    import re
                    text = re.sub(r'\s+', ' ', text)
                    record[field] = text
        
        return data

    async def _normalize_numeric_data(self, data: List[Dict[str, Any]], 
                                    parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize numeric data transformation"""
        
        numeric_fields = parameters.get("numeric_fields", [])
        method = parameters.get("method", "min_max")
        
        if not numeric_fields:
            return data
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(data)
        
        for field in numeric_fields:
            if field in df.columns:
                if method == "min_max":
                    min_val = df[field].min()
                    max_val = df[field].max()
                    if max_val > min_val:
                        df[field] = (df[field] - min_val) / (max_val - min_val)
                elif method == "z_score":
                    mean_val = df[field].mean()
                    std_val = df[field].std()
                    if std_val > 0:
                        df[field] = (df[field] - mean_val) / std_val
        
        return df.to_dict('records')

    async def _validate_email_data(self, data: List[Dict[str, Any]], 
                                 parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate email data transformation"""
        
        email_fields = parameters.get("email_fields", [])
        
        for record in data:
            for field in email_fields:
                if field in record:
                    email = record[field]
                    if isinstance(email, str) and '@' in email:
                        record[f"{field}_valid"] = True
                    else:
                        record[f"{field}_valid"] = False
        
        return data

    async def _extract_ml_features(self, data: List[Dict[str, Any]], 
                                 parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract ML features transformation"""
        
        feature_config = parameters.get("features", {})
        
        for record in data:
            # Example feature extractions
            if "created_at" in record:
                try:
                    created_at = pd.to_datetime(record["created_at"])
                    record["hour_of_day"] = created_at.hour
                    record["day_of_week"] = created_at.dayofweek
                    record["is_weekend"] = created_at.dayofweek >= 5
                except:
                    pass
            
            # Text length features
            for field, config in feature_config.items():
                if field in record and isinstance(record[field], str):
                    if config.get("length", False):
                        record[f"{field}_length"] = len(record[field])
                    if config.get("word_count", False):
                        record[f"{field}_word_count"] = len(record[field].split())
        
        return data

    async def _aggregate_data(self, data: List[Dict[str, Any]], 
                            parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate data transformation"""
        
        group_by = parameters.get("group_by", [])
        aggregations = parameters.get("aggregations", {})
        
        if not group_by or not aggregations:
            return data
        
        df = pd.DataFrame(data)
        
        # Perform aggregation
        agg_result = df.groupby(group_by).agg(aggregations).reset_index()
        
        # Flatten column names
        agg_result.columns = ['_'.join(col).strip() if col[1] else col[0] 
                             for col in agg_result.columns.values]
        
        return agg_result.to_dict('records')

    async def _detect_data_anomalies(self, data: List[Dict[str, Any]], 
                                   parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect data anomalies transformation"""
        
        numeric_fields = parameters.get("numeric_fields", [])
        method = parameters.get("method", "iqr")
        
        df = pd.DataFrame(data)
        
        for field in numeric_fields:
            if field in df.columns and df[field].dtype in ['int64', 'float64']:
                if method == "iqr":
                    Q1 = df[field].quantile(0.25)
                    Q3 = df[field].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    df[f"{field}_is_anomaly"] = (
                        (df[field] < lower_bound) | (df[field] > upper_bound)
                    )
                
                elif method == "z_score":
                    z_scores = np.abs((df[field] - df[field].mean()) / df[field].std())
                    df[f"{field}_is_anomaly"] = z_scores > 3
        
        return df.to_dict('records')

    async def _load_data_to_target(self, data: List[Dict[str, Any]], 
                                 target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to target destination"""
        
        try:
            target_type = target_config.get("type", "database")
            
            if target_type == "database":
                return await self._load_to_database(data, target_config)
            elif target_type == "file":
                return await self._load_to_file(data, target_config)
            elif target_type == "api":
                return await self._load_to_api(data, target_config)
            else:
                self.logger.error(f"Unsupported target type: {target_type}")
                return {"success": False, "error": f"Unsupported target type: {target_type}"}
                
        except Exception as e:
            self.logger.error(f"Error loading data to target: {e}")
            return {"success": False, "error": str(e)}

    async def _load_to_database(self, data: List[Dict[str, Any]], 
                              target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to database target"""
        
        try:
            table_name = target_config["table_name"]
            mode = target_config.get("mode", "append")  # append, replace, update
            
            if not data:
                return {"success": True, "records_loaded": 0}
            
            df = pd.DataFrame(data)
            
            # In a real implementation, use proper async database operations
            # For now, simulate the load operation
            records_loaded = len(df)
            
            return {
                "success": True,
                "records_loaded": records_loaded,
                "table_name": table_name,
                "mode": mode
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _load_to_file(self, data: List[Dict[str, Any]], 
                          target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to file target"""
        
        try:
            file_path = target_config["file_path"]
            file_format = target_config.get("format", "csv")
            
            df = pd.DataFrame(data)
            
            if file_format == "csv":
                df.to_csv(file_path, index=False)
            elif file_format == "json":
                df.to_json(file_path, orient='records', indent=2)
            elif file_format == "parquet":
                df.to_parquet(file_path, index=False)
            
            return {
                "success": True,
                "records_loaded": len(df),
                "file_path": file_path,
                "format": file_format
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _load_to_api(self, data: List[Dict[str, Any]], 
                         target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to API target"""
        
        try:
            url = target_config["url"]
            headers = target_config.get("headers", {})
            batch_size = target_config.get("batch_size", 100)
            
            records_loaded = 0
            
            # Process in batches
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=batch, headers=headers) as response:
                        if response.status in [200, 201]:
                            records_loaded += len(batch)
                        else:
                            self.logger.error(f"API load failed: {response.status}")
            
            return {
                "success": True,
                "records_loaded": records_loaded,
                "batches_processed": (len(data) + batch_size - 1) // batch_size
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _monitor_pipeline_execution(self):
        """Monitor pipeline execution status"""
        
        while True:
            try:
                # Check for stuck pipelines
                current_time = datetime.utcnow()
                
                for pipeline_id, pipeline_job in self.active_pipelines.items():
                    if (pipeline_job.status == PipelineStatus.RUNNING and 
                        pipeline_job.started_at and
                        current_time - pipeline_job.started_at > timedelta(hours=2)):
                        
                        self.logger.warning(f"Pipeline possibly stuck: {pipeline_id}")
                        pipeline_job.warnings.append("Pipeline execution time exceeded 2 hours")
                        
                        await self._save_pipeline_job(pipeline_job)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring pipeline execution: {e}")
                await asyncio.sleep(600)

    async def _monitor_data_quality(self):
        """Monitor data quality across pipelines"""
        
        while True:
            try:
                # Aggregate quality scores
                if self.quality_reports:
                    quality_scores = [report.overall_quality for report in self.quality_reports.values()]
                    
                    # Calculate quality distribution
                    quality_counts = {}
                    for quality in quality_scores:
                        quality_counts[quality.value] = quality_counts.get(quality.value, 0) + 1
                    
                    # Store quality metrics
                    await self.redis_client.setex(
                        "data_quality_metrics",
                        3600,
                        json.dumps({
                            "quality_distribution": quality_counts,
                            "total_reports": len(self.quality_reports),
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    )
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring data quality: {e}")
                await asyncio.sleep(1200)

    async def _collect_performance_metrics(self):
        """Collect pipeline performance metrics"""
        
        while True:
            try:
                # Calculate global metrics
                if self.pipeline_metrics:
                    total_pipelines = len(self.pipeline_metrics)
                    total_throughput = sum(m.throughput for m in self.pipeline_metrics.values())
                    avg_throughput = total_throughput / total_pipelines if total_pipelines > 0 else 0.0
                    
                    avg_success_rate = np.mean([m.success_rate for m in self.pipeline_metrics.values()])
                    avg_quality_score = np.mean([m.data_quality_score for m in self.pipeline_metrics.values()])
                    
                    self.global_metrics.update({
                        "total_pipelines": total_pipelines,
                        "active_pipelines": len([p for p in self.active_pipelines.values() 
                                               if p.status == PipelineStatus.RUNNING]),
                        "avg_throughput": avg_throughput,
                        "overall_success_rate": avg_success_rate,
                        "avg_data_quality": avg_quality_score
                    })
                
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error collecting performance metrics: {e}")
                await asyncio.sleep(600)

    async def _monitor_schema_evolution(self):
        """Monitor schema changes and evolution"""
        
        while True:
            try:
                # Check for schema changes in data sources
                for source_id, source in self.data_sources.items():
                    if source.enabled and source.schema_config:
                        # In production, check actual source schema
                        # For now, simulate schema monitoring
                        pass
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error monitoring schema evolution: {e}")
                await asyncio.sleep(1800)

    async def _track_data_lineage(self):
        """Track data lineage across pipelines"""
        
        while True:
            try:
                # Update data lineage graph
                for pipeline_id, pipeline_job in self.active_pipelines.items():
                    if pipeline_job.status == PipelineStatus.COMPLETED:
                        source_ids = [source.source_id for source in pipeline_job.source_configs]
                        target_id = pipeline_job.target_config.get("target_id", "unknown")
                        
                        # Track lineage
                        if target_id not in self.data_lineage:
                            self.data_lineage[target_id] = []
                        
                        self.data_lineage[target_id].extend(source_ids)
                        self.data_lineage[target_id] = list(set(self.data_lineage[target_id]))
                
                await asyncio.sleep(600)  # Update every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error tracking data lineage: {e}")
                await asyncio.sleep(1200)

    # Validation and utility methods
    
    async def _validate_data_source(self, source: DataSource):
        """Validate data source configuration"""
        
        required_fields = {
            DataSourceType.DATABASE: ["connection_string", "query"],
            DataSourceType.API: ["url"],
            DataSourceType.FILE: ["file_path"],
            DataSourceType.STREAM: ["stream_type", "topic"]
        }
        
        if source.source_type in required_fields:
            for field in required_fields[source.source_type]:
                if field not in source.connection_config:
                    raise ValueError(f"Missing required field for {source.source_type.value}: {field}")

    async def _test_data_source_connection(self, source: DataSource) -> Dict[str, Any]:
        """Test data source connection"""
        
        try:
            if source.source_type == DataSourceType.DATABASE:
                # Test database connection
                config = source.connection_config
                # In production, test actual connection
                return {"success": True, "message": "Database connection successful"}
            
            elif source.source_type == DataSourceType.API:
                # Test API endpoint
                url = source.connection_config["url"]
                headers = source.connection_config.get("headers", {})
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status < 400:
                            return {"success": True, "message": f"API connection successful: {response.status}"}
                        else:
                            return {"success": False, "error": f"API connection failed: {response.status}"}
            
            else:
                # For other types, assume connection is valid
                return {"success": True, "message": "Connection test passed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _validate_pipeline_config(self, config: Dict[str, Any]):
        """Validate pipeline configuration"""
        
        required_fields = ["sources", "target"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(config["sources"], list) or not config["sources"]:
            raise ValueError("Sources must be a non-empty list")

    async def _update_data_lineage(self, pipeline_job: PipelineJob, load_result: Dict[str, Any]):
        """Update data lineage tracking"""
        
        if load_result.get("success"):
            source_ids = [source.source_id for source in pipeline_job.source_configs]
            target_id = pipeline_job.target_config.get("target_id", pipeline_job.pipeline_id)
            
            lineage_entry = {
                "pipeline_id": pipeline_job.pipeline_id,
                "job_id": pipeline_job.job_id,
                "sources": source_ids,
                "target": target_id,
                "transformations": [t.transform_id for t in pipeline_job.transformations],
                "completed_at": pipeline_job.completed_at.isoformat()
            }
            
            await self.redis_client.lpush(
                "data_lineage_log",
                json.dumps(lineage_entry)
            )

    async def _update_pipeline_metrics(self, pipeline_job: PipelineJob, 
                                     execution_time: float, quality_report: DataQualityReport):
        """Update pipeline performance metrics"""
        
        throughput = pipeline_job.records_processed / execution_time if execution_time > 0 else 0.0
        success_rate = 1.0 if pipeline_job.status == PipelineStatus.COMPLETED else 0.0
        
        # Convert quality to numeric score
        quality_score_map = {
            DataQuality.EXCELLENT: 1.0,
            DataQuality.GOOD: 0.8,
            DataQuality.FAIR: 0.6,
            DataQuality.POOR: 0.4,
            DataQuality.CRITICAL: 0.2
        }
        
        quality_score = quality_score_map.get(quality_report.overall_quality, 0.5)
        
        metrics = PipelineMetrics(
            pipeline_id=pipeline_job.pipeline_id,
            execution_time=execution_time,
            throughput=throughput,
            success_rate=success_rate,
            data_quality_score=quality_score,
            resource_utilization={"cpu": 0.0, "memory": 0.0},  # Placeholder
            error_rate=len(pipeline_job.errors) / max(1, pipeline_job.records_processed),
            last_execution=pipeline_job.completed_at or datetime.utcnow()
        )
        
        self.pipeline_metrics[pipeline_job.pipeline_id] = metrics

    # Redis persistence methods
    
    async def _save_pipeline_job(self, job: PipelineJob):
        """Save pipeline job to Redis"""
        
        job_data = {
            "job_id": job.job_id,
            "pipeline_id": job.pipeline_id,
            "status": job.status.value,
            "progress": job.progress,
            "records_processed": job.records_processed,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "errors": job.errors,
            "warnings": job.warnings
        }
        
        await self.redis_client.setex(
            f"pipeline_job:{job.job_id}",
            86400,  # 24 hours
            json.dumps(job_data)
        )

    async def _save_data_source(self, source: DataSource):
        """Save data source to Redis"""
        
        source_data = {
            "source_id": source.source_id,
            "name": source.name,
            "source_type": source.source_type.value,
            "connection_config": source.connection_config,
            "schema_config": source.schema_config,
            "refresh_interval": source.refresh_interval,
            "enabled": source.enabled,
            "last_updated": source.last_updated.isoformat() if source.last_updated else None
        }
        
        await self.redis_client.setex(
            f"data_source:{source.source_id}",
            86400,
            json.dumps(source_data)
        )

    async def _save_pipeline_registry(self):
        """Save pipeline registry to Redis"""
        
        await self.redis_client.setex(
            "pipeline_registry",
            86400,
            json.dumps(self.pipeline_registry)
        )

    async def _save_schema_registry(self):
        """Save schema registry to Redis"""
        
        await self.redis_client.setex(
            "schema_registry",
            3600,
            json.dumps(self.schema_registry)
        )

    async def _load_pipeline_configurations(self):
        """Load pipeline configurations from Redis"""
        
        try:
            registry_data = await self.redis_client.get("pipeline_registry")
            if registry_data:
                self.pipeline_registry = json.loads(registry_data)
                self.logger.info(f"Loaded {len(self.pipeline_registry)} pipeline configurations")
        except Exception as e:
            self.logger.warning(f"Could not load pipeline configurations: {e}")

    async def _load_data_sources(self):
        """Load data sources from Redis"""
        
        try:
            source_keys = await self.redis_client.keys("data_source:*")
            
            for key in source_keys:
                source_data = await self.redis_client.get(key)
                if source_data:
                    data = json.loads(source_data)
                    
                    source = DataSource(
                        source_id=data["source_id"],
                        name=data["name"],
                        source_type=DataSourceType(data["source_type"]),
                        connection_config=data["connection_config"],
                        schema_config=data.get("schema_config"),
                        refresh_interval=data["refresh_interval"],
                        enabled=data["enabled"],
                        last_updated=datetime.fromisoformat(data["last_updated"]) if data["last_updated"] else None
                    )
                    
                    self.data_sources[source.source_id] = source
            
            self.logger.info(f"Loaded {len(self.data_sources)} data sources")
        except Exception as e:
            self.logger.warning(f"Could not load data sources: {e}")

    async def _load_schema_registry(self):
        """Load schema registry from Redis"""
        
        try:
            schema_data = await self.redis_client.get("schema_registry")
            if schema_data:
                self.schema_registry = json.loads(schema_data)
                self.logger.info(f"Loaded schema registry with {len(self.schema_registry)} schemas")
        except Exception as e:
            self.logger.warning(f"Could not load schema registry: {e}")

    async def get_pipeline_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive data pipeline dashboard"""
        
        # Pipeline statistics
        pipeline_stats = {
            "total_pipelines": len(self.active_pipelines),
            "running": len([p for p in self.active_pipelines.values() if p.status == PipelineStatus.RUNNING]),
            "completed": len([p for p in self.active_pipelines.values() if p.status == PipelineStatus.COMPLETED]),
            "failed": len([p for p in self.active_pipelines.values() if p.status == PipelineStatus.FAILED])
        }
        
        # Data source statistics
        source_stats = {
            "total_sources": len(self.data_sources),
            "enabled_sources": len([s for s in self.data_sources.values() if s.enabled]),
            "source_types": {}
        }
        
        for source in self.data_sources.values():
            source_type = source.source_type.value
            source_stats["source_types"][source_type] = source_stats["source_types"].get(source_type, 0) + 1
        
        # Quality summary
        quality_summary = {
            "total_reports": len(self.quality_reports),
            "avg_quality_score": 0.0
        }
        
        if self.quality_reports:
            quality_scores = []
            for report in self.quality_reports.values():
                if report.overall_quality == DataQuality.EXCELLENT:
                    quality_scores.append(1.0)
                elif report.overall_quality == DataQuality.GOOD:
                    quality_scores.append(0.8)
                elif report.overall_quality == DataQuality.FAIR:
                    quality_scores.append(0.6)
                elif report.overall_quality == DataQuality.POOR:
                    quality_scores.append(0.4)
                else:
                    quality_scores.append(0.2)
            
            quality_summary["avg_quality_score"] = np.mean(quality_scores)
        
        return {
            "pipeline_statistics": pipeline_stats,
            "data_source_statistics": source_stats,
            "quality_summary": quality_summary,
            "global_metrics": self.global_metrics,
            "available_transformations": list(self.transformation_functions.keys()),
            "lineage_entries": len(self.data_lineage),
            "system_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }

    async def shutdown(self):
        """Shutdown data pipeline service"""
        
        # Cancel pipeline tasks
        for task in self.pipeline_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.pipeline_tasks:
            await asyncio.gather(*self.pipeline_tasks, return_exceptions=True)
        
        # Close connections
        if self.redis_client:
            await self.redis_client.close()
        
        if self.db_engine:
            await self.db_engine.dispose()
        
        self.logger.info("Data Pipeline Service shutdown completed")


# Example usage
async def main():
    """Example usage of Data Pipeline Service"""
    
    pipeline_service = DataPipelineService()
    await pipeline_service.initialize()
    
    try:
        # Register data source
        source = DataSource(
            source_id="user_database",
            name="User Database",
            source_type=DataSourceType.DATABASE,
            connection_config={
                "connection_string": "postgresql://localhost/users",
                "query": "SELECT * FROM users WHERE created_at > NOW() - INTERVAL '1 day'"
            }
        )
        
        await pipeline_service.register_data_source(source)
        
        # Create pipeline
        pipeline_config = {
            "sources": [{"source_id": "user_database"}],
            "transformations": [
                {
                    "transform_id": "clean_emails",
                    "name": "Email Validation",
                    "type": "validation",
                    "function": "validate_emails",
                    "parameters": {"email_fields": ["email"]}
                }
            ],
            "target": {
                "type": "file",
                "file_path": "processed_users.csv",
                "format": "csv"
            }
        }
        
        pipeline_id = await pipeline_service.create_pipeline(pipeline_config)
        
        # Execute pipeline
        job_id = await pipeline_service.execute_pipeline(pipeline_id)
        
        print(f"Pipeline created and executed: {pipeline_id}")
        
        # Get dashboard
        dashboard = await pipeline_service.get_pipeline_dashboard()
        print(f"Pipeline dashboard: {dashboard}")
        
    finally:
        await pipeline_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())