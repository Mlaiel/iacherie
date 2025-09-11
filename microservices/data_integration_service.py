"""
🔄 Data Integration Service - Multi-source Data Integration & Synchronization
============================================================================

**Module**: Data Integration Service  
**Author**: Fahed Mlaiel (mlaiel@live.de)  
**Copyright**: (c) 2025 Fahed Mlaiel - All Rights Reserved  
**Role**: DBA + Backend Senior + Data Engineer + DevOps Engineer

Advanced data integration service for multi-source data synchronization,
ETL processing, and real-time data pipeline management.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This code is proprietary and confidential. Unauthorized use prohibited.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
import uuid

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataIntegrationService")

class DataSourceType(str, Enum):
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    CLOUD_STORAGE = "cloud_storage"
    WEBHOOK = "webhook"
    SOCIAL_MEDIA = "social_media"
    ANALYTICS = "analytics"

class IntegrationType(str, Enum):
    REAL_TIME = "real_time"
    BATCH = "batch"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"

class DataFormat(str, Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    YAML = "yaml"

class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class DataQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class IntegrationMetrics:
    """Data integration metrics"""
    total_sources: int
    active_integrations: int
    data_volume_processed: int
    sync_success_rate: float
    average_sync_time: float
    data_quality_score: float
    error_rate: float

class DataSourceModel(BaseModel):
    """Data source configuration model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    source_type: DataSourceType = DataSourceType.API
    connection_config: Dict[str, Any] = Field(default_factory=dict)
    credentials: Dict[str, Any] = Field(default_factory=dict)
    data_format: DataFormat = DataFormat.JSON
    schema_definition: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class IntegrationPipelineModel(BaseModel):
    """Data integration pipeline model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    source_ids: List[str] = Field(default_factory=list)
    target_config: Dict[str, Any] = Field(default_factory=dict)
    integration_type: IntegrationType = IntegrationType.BATCH
    schedule: Optional[str] = None  # Cron expression
    transformation_rules: List[Dict[str, Any]] = Field(default_factory=list)
    validation_rules: List[Dict[str, Any]] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SyncJobModel(BaseModel):
    """Data synchronization job model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pipeline_id: str
    status: SyncStatus = SyncStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_succeeded: int = 0
    records_failed: int = 0
    data_quality: DataQuality = DataQuality.GOOD
    error_details: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DataMappingModel(BaseModel):
    """Data field mapping model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_field: str
    target_field: str
    transformation_function: Optional[str] = None
    validation_rules: List[str] = Field(default_factory=list)
    is_required: bool = True
    default_value: Optional[Any] = None
    data_type: str = "string"

class DataIntegrationService:
    """Advanced data integration service with multi-source synchronization"""
    
    def __init__(self):
        self.data_sources: Dict[str, DataSourceModel] = {}
        self.pipelines: Dict[str, IntegrationPipelineModel] = {}
        self.sync_jobs: Dict[str, SyncJobModel] = {}
        self.active_jobs: Dict[str, asyncio.Task] = {}
        self.data_mappings: Dict[str, List[DataMappingModel]] = {}
        self.metrics = IntegrationMetrics(
            total_sources=0,
            active_integrations=0,
            data_volume_processed=0,
            sync_success_rate=0.0,
            average_sync_time=0.0,
            data_quality_score=0.0,
            error_rate=0.0
        )
        self.init_default_connectors()
        logger.info("Data Integration Service initialized successfully")

    def init_default_connectors(self):
        """Initialize default data source connectors"""
        # Social Media Sources
        youtube_source = DataSourceModel(
            id="source_youtube_analytics",
            name="YouTube Analytics",
            description="YouTube channel analytics and video performance data",
            source_type=DataSourceType.API,
            connection_config={
                "base_url": "https://www.googleapis.com/youtube/v3",
                "api_version": "v3",
                "rate_limit": 10000
            },
            data_format=DataFormat.JSON,
            schema_definition={
                "video_id": "string",
                "title": "string",
                "views": "integer",
                "likes": "integer",
                "comments": "integer",
                "published_at": "datetime"
            }
        )
        
        # Instagram API Source
        instagram_source = DataSourceModel(
            id="source_instagram_business",
            name="Instagram Business API",
            description="Instagram business account insights and post analytics",
            source_type=DataSourceType.API,
            connection_config={
                "base_url": "https://graph.facebook.com/v18.0",
                "api_version": "v18.0",
                "rate_limit": 200
            },
            data_format=DataFormat.JSON
        )
        
        # Analytics Database Source
        analytics_db = DataSourceModel(
            id="source_analytics_db",
            name="Analytics Database",
            description="Internal analytics database with user engagement data",
            source_type=DataSourceType.DATABASE,
            connection_config={
                "host": "analytics-db.internal",
                "port": 5432,
                "database": "analytics",
                "connection_pool_size": 20
            },
            data_format=DataFormat.JSON
        )
        
        self.data_sources = {
            youtube_source.id: youtube_source,
            instagram_source.id: instagram_source,
            analytics_db.id: analytics_db
        }
        
        self.metrics.total_sources = len(self.data_sources)

    async def create_data_source(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new data source"""
        try:
            source = DataSourceModel(**source_data)
            
            # Validate connection
            connection_valid = await self._validate_connection(source)
            if not connection_valid:
                raise HTTPException(status_code=400, detail="Invalid connection configuration")
            
            self.data_sources[source.id] = source
            self.metrics.total_sources += 1
            
            logger.info(f"Created data source: {source.id}")
            return {
                "success": True,
                "source_id": source.id,
                "message": "Data source created successfully",
                "source": source.dict()
            }
        except Exception as e:
            logger.error(f"Error creating data source: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to create data source: {str(e)}")

    async def create_integration_pipeline(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new integration pipeline"""
        try:
            pipeline = IntegrationPipelineModel(**pipeline_data)
            
            # Validate source IDs
            for source_id in pipeline.source_ids:
                if source_id not in self.data_sources:
                    raise HTTPException(status_code=400, detail=f"Data source {source_id} not found")
            
            self.pipelines[pipeline.id] = pipeline
            self.metrics.active_integrations += 1
            
            logger.info(f"Created integration pipeline: {pipeline.id}")
            return {
                "success": True,
                "pipeline_id": pipeline.id,
                "message": "Integration pipeline created successfully",
                "pipeline": pipeline.dict()
            }
        except Exception as e:
            logger.error(f"Error creating pipeline: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to create pipeline: {str(e)}")

    async def start_sync_job(self, pipeline_id: str, manual_trigger: bool = False) -> Dict[str, Any]:
        """Start data synchronization job"""
        try:
            if pipeline_id not in self.pipelines:
                raise HTTPException(status_code=404, detail="Pipeline not found")
            
            pipeline = self.pipelines[pipeline_id]
            if not pipeline.is_active:
                raise HTTPException(status_code=400, detail="Pipeline is inactive")
            
            # Create sync job
            job = SyncJobModel(
                pipeline_id=pipeline_id,
                status=SyncStatus.PENDING
            )
            
            self.sync_jobs[job.id] = job
            
            # Start job in background
            task = asyncio.create_task(self._execute_sync_job(job))
            self.active_jobs[job.id] = task
            
            logger.info(f"Started sync job: {job.id} for pipeline: {pipeline_id}")
            return {
                "success": True,
                "job_id": job.id,
                "pipeline_id": pipeline_id,
                "message": "Sync job started successfully",
                "status": job.status
            }
        except Exception as e:
            logger.error(f"Error starting sync job: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to start sync job: {str(e)}")

    async def _execute_sync_job(self, job: SyncJobModel):
        """Execute data synchronization job"""
        try:
            job.status = SyncStatus.RUNNING
            job.started_at = datetime.utcnow()
            
            pipeline = self.pipelines[job.pipeline_id]
            
            total_records = 0
            successful_records = 0
            failed_records = 0
            
            # Process each source
            for source_id in pipeline.source_ids:
                source = self.data_sources[source_id]
                
                # Extract data from source
                extracted_data = await self._extract_data(source)
                
                if extracted_data:
                    # Transform data
                    transformed_data = await self._transform_data(extracted_data, pipeline.transformation_rules)
                    
                    # Validate data
                    validated_data = await self._validate_data(transformed_data, pipeline.validation_rules)
                    
                    # Load data to target
                    load_result = await self._load_data(validated_data, pipeline.target_config)
                    
                    total_records += len(extracted_data)
                    successful_records += load_result.get("success_count", 0)
                    failed_records += load_result.get("error_count", 0)
                    
                    # Collect errors
                    if load_result.get("errors"):
                        job.error_details.extend(load_result["errors"])
            
            # Update job status
            job.records_processed = total_records
            job.records_succeeded = successful_records
            job.records_failed = failed_records
            job.status = SyncStatus.COMPLETED if failed_records == 0 else SyncStatus.FAILED
            job.completed_at = datetime.utcnow()
            
            # Calculate data quality
            if total_records > 0:
                success_rate = successful_records / total_records
                if success_rate >= 0.95:
                    job.data_quality = DataQuality.EXCELLENT
                elif success_rate >= 0.85:
                    job.data_quality = DataQuality.GOOD
                elif success_rate >= 0.70:
                    job.data_quality = DataQuality.FAIR
                elif success_rate >= 0.50:
                    job.data_quality = DataQuality.POOR
                else:
                    job.data_quality = DataQuality.CRITICAL
            
            # Update pipeline last run
            pipeline.last_run = datetime.utcnow()
            
            # Update metrics
            self.metrics.data_volume_processed += total_records
            if total_records > 0:
                self.metrics.sync_success_rate = (self.metrics.sync_success_rate + success_rate) / 2
            
            logger.info(f"Completed sync job {job.id}: {successful_records}/{total_records} records processed successfully")
            
        except Exception as e:
            job.status = SyncStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_details.append({
                "error_type": "execution_error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            logger.error(f"Error executing sync job {job.id}: {str(e)}")
        finally:
            # Clean up active job
            if job.id in self.active_jobs:
                del self.active_jobs[job.id]

    async def _validate_connection(self, source: DataSourceModel) -> bool:
        """Validate data source connection"""
        try:
            if source.source_type == DataSourceType.API:
                # Simulate API connection validation
                base_url = source.connection_config.get("base_url")
                if not base_url:
                    return False
                
                # In real implementation, make test API call
                logger.info(f"Validating API connection to {base_url}")
                return True
            
            elif source.source_type == DataSourceType.DATABASE:
                # Simulate database connection validation
                host = source.connection_config.get("host")
                port = source.connection_config.get("port")
                
                if not host or not port:
                    return False
                
                logger.info(f"Validating database connection to {host}:{port}")
                return True
            
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False

    async def _extract_data(self, source: DataSourceModel) -> List[Dict[str, Any]]:
        """Extract data from source"""
        try:
            if source.source_type == DataSourceType.API:
                return await self._extract_from_api(source)
            elif source.source_type == DataSourceType.DATABASE:
                return await self._extract_from_database(source)
            elif source.source_type == DataSourceType.FILE:
                return await self._extract_from_file(source)
            else:
                logger.warning(f"Unsupported source type: {source.source_type}")
                return []
        except Exception as e:
            logger.error(f"Error extracting data from {source.id}: {str(e)}")
            return []

    async def _extract_from_api(self, source: DataSourceModel) -> List[Dict[str, Any]]:
        """Extract data from API source"""
        # Simulate API data extraction
        logger.info(f"Extracting data from API source: {source.name}")
        
        # Sample data based on source type
        if "youtube" in source.name.lower():
            sample_data = [
                {
                    "video_id": "abc123",
                    "title": "Sample Video 1",
                    "views": 1000,
                    "likes": 50,
                    "comments": 10,
                    "published_at": "2025-01-20T10:00:00Z"
                },
                {
                    "video_id": "def456",
                    "title": "Sample Video 2",
                    "views": 2500,
                    "likes": 125,
                    "comments": 25,
                    "published_at": "2025-01-19T15:30:00Z"
                }
            ]
        elif "instagram" in source.name.lower():
            sample_data = [
                {
                    "post_id": "ig_123",
                    "caption": "Sample Instagram post",
                    "likes": 200,
                    "comments": 15,
                    "reach": 1500,
                    "posted_at": "2025-01-20T12:00:00Z"
                }
            ]
        else:
            sample_data = [{"id": 1, "data": "sample_data"}]
        
        # Simulate network delay
        await asyncio.sleep(0.5)
        return sample_data

    async def _extract_from_database(self, source: DataSourceModel) -> List[Dict[str, Any]]:
        """Extract data from database source"""
        logger.info(f"Extracting data from database source: {source.name}")
        
        # Simulate database query
        sample_data = [
            {
                "user_id": "user_001",
                "engagement_score": 85.5,
                "content_views": 1500,
                "session_duration": 300,
                "last_active": "2025-01-20T14:00:00Z"
            },
            {
                "user_id": "user_002",
                "engagement_score": 92.3,
                "content_views": 2200,
                "session_duration": 450,
                "last_active": "2025-01-20T13:45:00Z"
            }
        ]
        
        await asyncio.sleep(0.3)
        return sample_data

    async def _extract_from_file(self, source: DataSourceModel) -> List[Dict[str, Any]]:
        """Extract data from file source"""
        logger.info(f"Extracting data from file source: {source.name}")
        
        # Simulate file reading
        sample_data = [
            {"record_id": 1, "value": "file_data_1"},
            {"record_id": 2, "value": "file_data_2"}
        ]
        
        return sample_data

    async def _transform_data(self, data: List[Dict[str, Any]], 
                            transformation_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform data according to rules"""
        if not transformation_rules:
            return data
        
        transformed_data = []
        
        for record in data:
            transformed_record = record.copy()
            
            for rule in transformation_rules:
                rule_type = rule.get("type")
                
                if rule_type == "field_mapping":
                    # Map field names
                    source_field = rule.get("source_field")
                    target_field = rule.get("target_field")
                    
                    if source_field in transformed_record:
                        transformed_record[target_field] = transformed_record.pop(source_field)
                
                elif rule_type == "data_type_conversion":
                    # Convert data types
                    field = rule.get("field")
                    target_type = rule.get("target_type")
                    
                    if field in transformed_record:
                        try:
                            if target_type == "integer":
                                transformed_record[field] = int(transformed_record[field])
                            elif target_type == "float":
                                transformed_record[field] = float(transformed_record[field])
                            elif target_type == "string":
                                transformed_record[field] = str(transformed_record[field])
                        except (ValueError, TypeError):
                            logger.warning(f"Failed to convert {field} to {target_type}")
                
                elif rule_type == "field_calculation":
                    # Calculate new fields
                    target_field = rule.get("target_field")
                    expression = rule.get("expression")
                    
                    # Simple expression evaluation (in real implementation, use safe eval)
                    if expression and target_field:
                        transformed_record[target_field] = 0  # Simplified
            
            transformed_data.append(transformed_record)
        
        logger.info(f"Transformed {len(data)} records")
        return transformed_data

    async def _validate_data(self, data: List[Dict[str, Any]], 
                           validation_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate data according to rules"""
        if not validation_rules:
            return data
        
        validated_data = []
        
        for record in data:
            is_valid = True
            
            for rule in validation_rules:
                rule_type = rule.get("type")
                field = rule.get("field")
                
                if rule_type == "required_field":
                    if field not in record or record[field] is None:
                        is_valid = False
                        break
                
                elif rule_type == "data_type_check":
                    expected_type = rule.get("expected_type")
                    if field in record:
                        value = record[field]
                        if expected_type == "integer" and not isinstance(value, int):
                            is_valid = False
                            break
                        elif expected_type == "string" and not isinstance(value, str):
                            is_valid = False
                            break
                
                elif rule_type == "value_range":
                    if field in record:
                        value = record[field]
                        min_value = rule.get("min_value")
                        max_value = rule.get("max_value")
                        
                        if min_value is not None and value < min_value:
                            is_valid = False
                            break
                        if max_value is not None and value > max_value:
                            is_valid = False
                            break
            
            if is_valid:
                validated_data.append(record)
        
        logger.info(f"Validated {len(validated_data)}/{len(data)} records")
        return validated_data

    async def _load_data(self, data: List[Dict[str, Any]], 
                        target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to target destination"""
        try:
            target_type = target_config.get("type", "database")
            
            if target_type == "database":
                return await self._load_to_database(data, target_config)
            elif target_type == "api":
                return await self._load_to_api(data, target_config)
            elif target_type == "file":
                return await self._load_to_file(data, target_config)
            else:
                logger.warning(f"Unsupported target type: {target_type}")
                return {"success_count": 0, "error_count": len(data)}
        
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return {
                "success_count": 0,
                "error_count": len(data),
                "errors": [{"message": str(e)}]
            }

    async def _load_to_database(self, data: List[Dict[str, Any]], 
                              target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to database target"""
        logger.info(f"Loading {len(data)} records to database")
        
        # Simulate database insertion
        success_count = len(data)
        error_count = 0
        
        # Simulate some failures
        if len(data) > 5:
            error_count = 1
            success_count = len(data) - 1
        
        await asyncio.sleep(0.2)  # Simulate processing time
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": [{"message": "Sample error"}] if error_count > 0 else []
        }

    async def _load_to_api(self, data: List[Dict[str, Any]], 
                         target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to API target"""
        logger.info(f"Loading {len(data)} records to API")
        
        # Simulate API calls
        success_count = len(data)
        error_count = 0
        
        await asyncio.sleep(0.5)
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": []
        }

    async def _load_to_file(self, data: List[Dict[str, Any]], 
                          target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data to file target"""
        logger.info(f"Loading {len(data)} records to file")
        
        # Simulate file writing
        success_count = len(data)
        error_count = 0
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": []
        }

    async def get_sync_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get synchronization job status"""
        try:
            if job_id not in self.sync_jobs:
                raise HTTPException(status_code=404, detail="Sync job not found")
            
            job = self.sync_jobs[job_id]
            
            # Calculate progress
            progress = 0.0
            if job.records_processed > 0:
                progress = (job.records_succeeded / job.records_processed) * 100
            
            return {
                "job_id": job_id,
                "status": job.status,
                "progress": progress,
                "records_processed": job.records_processed,
                "records_succeeded": job.records_succeeded,
                "records_failed": job.records_failed,
                "data_quality": job.data_quality,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "errors": job.error_details
            }
        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to get job status: {str(e)}")

    async def cancel_sync_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel running synchronization job"""
        try:
            if job_id not in self.sync_jobs:
                raise HTTPException(status_code=404, detail="Sync job not found")
            
            job = self.sync_jobs[job_id]
            
            if job.status not in [SyncStatus.RUNNING, SyncStatus.PENDING]:
                raise HTTPException(status_code=400, detail="Job cannot be cancelled")
            
            # Cancel the task
            if job_id in self.active_jobs:
                self.active_jobs[job_id].cancel()
                del self.active_jobs[job_id]
            
            job.status = SyncStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            
            logger.info(f"Cancelled sync job: {job_id}")
            return {
                "success": True,
                "job_id": job_id,
                "message": "Sync job cancelled successfully"
            }
        except Exception as e:
            logger.error(f"Error cancelling job: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to cancel job: {str(e)}")

    async def get_integration_history(self, pipeline_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get integration history for pipeline"""
        try:
            if pipeline_id not in self.pipelines:
                raise HTTPException(status_code=404, detail="Pipeline not found")
            
            pipeline_jobs = [
                job.dict() for job in self.sync_jobs.values() 
                if job.pipeline_id == pipeline_id
            ]
            
            # Sort by creation time (most recent first)
            pipeline_jobs.sort(key=lambda x: x['created_at'], reverse=True)
            pipeline_jobs = pipeline_jobs[:limit]
            
            return {
                "pipeline_id": pipeline_id,
                "jobs": pipeline_jobs,
                "total_jobs": len(pipeline_jobs)
            }
        except Exception as e:
            logger.error(f"Error getting integration history: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to get history: {str(e)}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get data integration service metrics"""
        # Update metrics
        completed_jobs = [job for job in self.sync_jobs.values() if job.status == SyncStatus.COMPLETED]
        failed_jobs = [job for job in self.sync_jobs.values() if job.status == SyncStatus.FAILED]
        
        if self.sync_jobs:
            success_rate = len(completed_jobs) / len(self.sync_jobs) * 100
            self.metrics.sync_success_rate = success_rate
            
            if completed_jobs:
                avg_processing_time = sum(
                    (job.completed_at - job.started_at).total_seconds()
                    for job in completed_jobs if job.started_at and job.completed_at
                ) / len(completed_jobs)
                self.metrics.average_sync_time = avg_processing_time
        
        return {
            "total_sources": self.metrics.total_sources,
            "active_integrations": self.metrics.active_integrations,
            "total_pipelines": len(self.pipelines),
            "total_jobs": len(self.sync_jobs),
            "active_jobs": len(self.active_jobs),
            "data_volume_processed": self.metrics.data_volume_processed,
            "sync_success_rate": self.metrics.sync_success_rate,
            "average_sync_time": self.metrics.average_sync_time,
            "data_quality_score": self.metrics.data_quality_score
        }

# FastAPI application setup
app = FastAPI(title="Data Integration Service")
service = DataIntegrationService()

@app.post("/sources/")
async def create_data_source(source_data: Dict[str, Any]):
    """Create a new data source"""
    return await service.create_data_source(source_data)

@app.post("/pipelines/")
async def create_integration_pipeline(pipeline_data: Dict[str, Any]):
    """Create a new integration pipeline"""
    return await service.create_integration_pipeline(pipeline_data)

@app.post("/pipelines/{pipeline_id}/sync")
async def start_sync_job(pipeline_id: str, manual_trigger: bool = False):
    """Start data synchronization job"""
    return await service.start_sync_job(pipeline_id, manual_trigger)

@app.get("/jobs/{job_id}/status")
async def get_sync_job_status(job_id: str):
    """Get sync job status"""
    return await service.get_sync_job_status(job_id)

@app.delete("/jobs/{job_id}")
async def cancel_sync_job(job_id: str):
    """Cancel sync job"""
    return await service.cancel_sync_job(job_id)

@app.get("/pipelines/{pipeline_id}/history")
async def get_integration_history(pipeline_id: str, limit: int = 50):
    """Get integration history"""
    return await service.get_integration_history(pipeline_id, limit)

@app.get("/metrics")
async def get_metrics():
    """Get service metrics"""
    return await service.get_metrics()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DataIntegrationService"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)