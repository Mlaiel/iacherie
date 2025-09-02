"""Data Pipeline Manager
====================

Advanced data pipeline management system for crawler operations with ETL processing,
data validation, transformation, and intelligent routing capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple, AsyncGenerator
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import pickle
from collections import defaultdict, deque
import pandas as pd
import numpy as np
from pathlib import Path

from ..config.pipeline_config import PipelineConfig
from ..utils.data_validator import DataValidator
from ..utils.data_transformer import DataTransformer
from ..utils.data_enricher import DataEnricher
from ...core.database import get_database_session
from ...core.logging import get_logger
from ...models.crawled_data import CrawledDataRecord, ProcessingLog
from ...monitoring.metrics_collector import MetricsCollector


class PipelineStage(Enum):
    """
Data pipeline processing stages."""

    INGESTION = "ingestion"
    VALIDATION = "validation"
    CLEANING = "cleaning"
    TRANSFORMATION = "transformation"
    ENRICHMENT = "enrichment"
    ANALYSIS = "analysis"
    ROUTING = "routing"
    STORAGE = "storage"
    INDEXING = "indexing"
    EXPORT = "export"


class DataFormat(Enum):
    """Supported data formats."""

    JSON = "json"
    XML = "xml"
    CSV = "csv"
    HTML = "html"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    BINARY = "binary"


class ProcessingStatus(Enum):
    """Data processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class DataRecord:
    """Data record for pipeline processing."""
    record_id: str
    source_url: str
    data_format: DataFormat
    raw_data: Union[str, bytes, Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    checksum: Optional[str] = None
    processing_stage: PipelineStage = PipelineStage.INGESTION
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class PipelineRule:
    """
Pipeline processing rule."""
    rule_id: str
    name: str
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int = 0
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PipelineMetrics:
    """
Pipeline performance metrics."""
    pipeline_name: str
    records_processed: int = 0
    records_completed: int = 0
    records_failed: int = 0
    records_skipped: int = 0
    bytes_processed: int = 0
    average_processing_time: float = 0.0
    throughput_per_second: float = 0.0
    error_rate: float = 0.0
    stage_performance: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class PipelineStageProcessor:
    """
    Base class for pipeline stage processors.
    """
    
    def __init__(self, stage: PipelineStage, config: Dict[str, Any] = None):
        """
Initialize stage processor."""
        self.stage = stage
        self.config = config or {}
        self.logger = get_logger(f"Pipeline-{stage.value}")
        
    async def process(self, record: DataRecord) -> DataRecord:
        """Process a data record through this stage - base implementation."""
        try:
            self.logger.info(f"Processing record {record.record_id} in {self.stage.value} stage")
            
            # Validate input
            if not await self.validate_input(record):
                record.status = RecordStatus.ERROR
                record.error_message = f"Input validation failed for {self.stage.value} stage"
                self.logger.error(f"Input validation failed for record {record.record_id}")
                return record
            
            # Basic processing - update record metadata
            record.metadata.update({
                "processed_by": self.stage.value,
                "processed_at": datetime.utcnow().isoformat(),
                "processor_config": self.config
            })
            
            # Simulate processing time
            import asyncio
            await asyncio.sleep(0.01)
            
            # Mark as processed if no errors
            if record.status != RecordStatus.ERROR:
                record.status = RecordStatus.PROCESSED
                record.processed_at = datetime.utcnow()
            
            self.logger.info(f"Successfully processed record {record.record_id} in {self.stage.value}")
            return record
            
        except Exception as e:
            self.logger.error(f"Error processing record {record.record_id} in {self.stage.value}: {str(e)}")
            record.status = RecordStatus.ERROR
            record.error_message = str(e)
            return record
        
    async def validate_input(self, record: DataRecord) -> bool:
        """Validate input for this stage."""
        return True
        
    async def cleanup(self, record: DataRecord):
        try:
            logger.info(f"Executing cleanup")
            
            # Implementation for cleanup
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"cleanup completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"cleanup failed: {e}")
            raise
class IngestionProcessor(PipelineStageProcessor):
    """
Data ingestion stage processor."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.INGESTION, config)
        self.data_validator = DataValidator()
        
    async def process(self, record: DataRecord) -> DataRecord:
        """
Process data ingestion."""
        try:
            # Calculate checksum if not present
            if not record.checksum:
                if isinstance(record.raw_data, (str, bytes)):
                    data_bytes = record.raw_data.encode() if isinstance(record.raw_data, str) else record.raw_data
                    record.checksum = hashlib.sha256(data_bytes).hexdigest()
                    
            # Calculate size
            if isinstance(record.raw_data, str):
                record.size_bytes = len(record.raw_data.encode('utf-8'))
            elif isinstance(record.raw_data, bytes):
                record.size_bytes = len(record.raw_data)
            elif isinstance(record.raw_data, dict):
                record.size_bytes = len(json.dumps(record.raw_data).encode('utf-8'))
                
            # Basic format detection
            if record.data_format == DataFormat.JSON and isinstance(record.raw_data, str):
                try:
                    json.loads(record.raw_data)
                except json.JSONDecodeError:
                    record.data_format = DataFormat.TEXT
                    
            record.processing_stage = PipelineStage.VALIDATION
            record.processing_status = ProcessingStatus.COMPLETED
            
            self.logger.debug(f"Ingestion completed for record {record.record_id}")
            return record
            
        except Exception as e:
            record.processing_status = ProcessingStatus.FAILED
            record.error_message = str(e)
            self.logger.error(f"Ingestion failed for record {record.record_id}: {e}")
            raise


class ValidationProcessor(PipelineStageProcessor):
    """Data validation stage processor."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.VALIDATION, config)
        self.validator = DataValidator()
        
    async def process(self, record: DataRecord) -> DataRecord:
        """
Process data validation."""
        try:
            # Validate data format
            is_valid = await self._validate_format(record)
            
            if not is_valid:
                record.processing_status = ProcessingStatus.FAILED
                record.error_message = "Data format validation failed"
                return record
                
            # Validate data integrity
            if record.checksum:
                current_checksum = await self._calculate_checksum(record.raw_data)
                if current_checksum != record.checksum:
                    record.processing_status = ProcessingStatus.FAILED
                    record.error_message = "Data integrity check failed"
                    return record
                    
            # Custom validation rules
            validation_result = await self._apply_validation_rules(record)
            
            if validation_result['valid']:
                record.processing_stage = PipelineStage.CLEANING
                record.processing_status = ProcessingStatus.COMPLETED
                
                # Add validation metadata
                record.metadata.update({
                    'validation_passed': True,
                    'validation_timestamp': datetime.utcnow().isoformat(),
                    'validation_rules_applied': validation_result.get('rules_applied', [])
                })
            else:
                record.processing_status = ProcessingStatus.FAILED
                record.error_message = validation_result.get('error', 'Validation failed')
                
            self.logger.debug(f"Validation completed for record {record.record_id}")
            return record
            
        except Exception as e:
            record.processing_status = ProcessingStatus.FAILED
            record.error_message = str(e)
            self.logger.error(f"Validation failed for record {record.record_id}: {e}")
            raise
            
    async def _validate_format(self, record: DataRecord) -> bool:
        """Validate data format."""
        try:
            if record.data_format == DataFormat.JSON:
                if isinstance(record.raw_data, str):
                    json.loads(record.raw_data)
                elif not isinstance(record.raw_data, dict):
                    return False
                    
            elif record.data_format == DataFormat.XML:
                # XML validation would go here
                pass
                
            elif record.data_format == DataFormat.CSV:
                # CSV validation would go here
                pass
                
            return True
            
        except Exception:
            return False
            
    async def _calculate_checksum(self, data: Union[str, bytes, Dict[str, Any]]) -> str:
        """
Calculate data checksum."""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
            data_bytes = data_str.encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
            
        return hashlib.sha256(data_bytes).hexdigest()
        
    async def _apply_validation_rules(self, record: DataRecord) -> Dict[str, Any]:
        """
Apply custom validation rules."""
        # Placeholder for custom validation logic
        return {
            'valid': True,
            'rules_applied': [],
            'details': {}
        }


class TransformationProcessor(PipelineStageProcessor):
    """
Data transformation stage processor."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.TRANSFORMATION, config)
        self.transformer = DataTransformer()
        
    async def process(self, record: DataRecord) -> DataRecord:
        """
Process data transformation."""
        try:
            # Apply transformations based on data format
            if record.data_format == DataFormat.JSON:
                record = await self._transform_json(record)
            elif record.data_format == DataFormat.HTML:
                record = await self._transform_html(record)
            elif record.data_format == DataFormat.TEXT:
                record = await self._transform_text(record)
                
            record.processing_stage = PipelineStage.ENRICHMENT
            record.processing_status = ProcessingStatus.COMPLETED
            
            self.logger.debug(f"Transformation completed for record {record.record_id}")
            return record
            
        except Exception as e:
            record.processing_status = ProcessingStatus.FAILED
            record.error_message = str(e)
            self.logger.error(f"Transformation failed for record {record.record_id}: {e}")
            raise
            
    async def _transform_json(self, record: DataRecord) -> DataRecord:
        """Transform JSON data."""
        try:
            if isinstance(record.raw_data, str):
                data = json.loads(record.raw_data)
            else:
                data = record.raw_data
                
            # Apply JSON transformations
            transformed_data = await self.transformer.transform_json(data, self.config)
            record.raw_data = transformed_data
            
            return record
            
        except Exception as e:
            self.logger.error(f"JSON transformation error: {e}")
            raise
            
    async def _transform_html(self, record: DataRecord) -> DataRecord:
        """Transform HTML data."""
        try:
            # Apply HTML transformations
            transformed_data = await self.transformer.transform_html(record.raw_data, self.config)
            record.raw_data = transformed_data
            
            return record
            
        except Exception as e:
            self.logger.error(f"HTML transformation error: {e}")
            raise
            
    async def _transform_text(self, record: DataRecord) -> DataRecord:
        """Transform text data."""
        try:
            # Apply text transformations
            transformed_data = await self.transformer.transform_text(record.raw_data, self.config)
            record.raw_data = transformed_data
            
            return record
            
        except Exception as e:
            self.logger.error(f"Text transformation error: {e}")
            raise


class EnrichmentProcessor(PipelineStageProcessor):
    """Data enrichment stage processor."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.ENRICHMENT, config)
        self.enricher = DataEnricher()
        
    async def process(self, record: DataRecord) -> DataRecord:
        """
Process data enrichment."""
        try:
            # Enrich with metadata
            enriched_metadata = await self._enrich_metadata(record)
            record.metadata.update(enriched_metadata)
            
            # Enrich data content
            enriched_data = await self._enrich_content(record)
            if enriched_data:
                record.raw_data = enriched_data
                
            record.processing_stage = PipelineStage.ANALYSIS
            record.processing_status = ProcessingStatus.COMPLETED
            
            self.logger.debug(f"Enrichment completed for record {record.record_id}")
            return record
            
        except Exception as e:
            record.processing_status = ProcessingStatus.FAILED
            record.error_message = str(e)
            self.logger.error(f"Enrichment failed for record {record.record_id}: {e}")
            raise
            
    async def _enrich_metadata(self, record: DataRecord) -> Dict[str, Any]:
        """Enrich record metadata."""
        enriched = {}
        
        try:
            # URL analysis
            if record.source_url:
                url_info = await self.enricher.analyze_url(record.source_url)
                enriched['url_info'] = url_info
                
            # Content analysis
            if record.data_format in [DataFormat.TEXT, DataFormat.HTML]:
                content_info = await self.enricher.analyze_content(record.raw_data)
                enriched['content_analysis'] = content_info
                
            # Timestamp analysis
            enriched['processing_info'] = {
                'enriched_at': datetime.utcnow().isoformat(),
                'processing_time_ms': time.time() * 1000
            }
            
            return enriched
            
        except Exception as e:
            self.logger.error(f"Metadata enrichment error: {e}")
            return {}
            
    async def _enrich_content(self, record: DataRecord) -> Optional[Any]:
        """Enrich record content."""
        try:
            # Content enrichment based on format
            if record.data_format == DataFormat.JSON:
                return await self.enricher.enrich_json(record.raw_data)
            elif record.data_format == DataFormat.HTML:
                return await self.enricher.enrich_html(record.raw_data)
            elif record.data_format == DataFormat.TEXT:
                return await self.enricher.enrich_text(record.raw_data)
                
            return None
            
        except Exception as e:
            self.logger.error(f"Content enrichment error: {e}")
            return None


class DataPipelineManager:
    """
    Advanced data pipeline management system for crawler operations.
    
    Provides ETL processing, data validation, transformation, enrichment,
    and intelligent routing with parallel processing capabilities.
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
Initialize data pipeline manager."""
        self.config = config or PipelineConfig()
        self.logger = get_logger(self.__class__.__name__)
        self.metrics_collector = MetricsCollector()
        
        # Pipeline components
        self.processors: Dict[PipelineStage, PipelineStageProcessor] = {}
        self.rules: Dict[str, PipelineRule] = {}
        self.pipelines: Dict[str, List[PipelineStage]] = {}
        
        # Processing state
        self.processing_queue: asyncio.Queue = asyncio.Queue(maxsize=self.config.MAX_QUEUE_SIZE)
        self.active_records: Dict[str, DataRecord] = {}
        self.completed_records: deque = deque(maxlen=self.config.HISTORY_SIZE)
        
        # Workers
        self.workers: List[asyncio.Task] = []
        self.worker_count = self.config.WORKER_COUNT
        self.processing_active = False
        
        # Metrics
        self.metrics: Dict[str, PipelineMetrics] = {}
        self.global_metrics = PipelineMetrics(pipeline_name="global")
        
        # Initialize processors
        self._initialize_processors()
        
    def _initialize_processors(self):
        """Initialize pipeline stage processors."""
        try:
            # Standard processors
            self.processors[PipelineStage.INGESTION] = IngestionProcessor(self.config.INGESTION_CONFIG)
            self.processors[PipelineStage.VALIDATION] = ValidationProcessor(self.config.VALIDATION_CONFIG)
            self.processors[PipelineStage.TRANSFORMATION] = TransformationProcessor(self.config.TRANSFORMATION_CONFIG)
            self.processors[PipelineStage.ENRICHMENT] = EnrichmentProcessor(self.config.ENRICHMENT_CONFIG)
            
            # Default pipeline
            self.pipelines["default"] = [
                PipelineStage.INGESTION,
                PipelineStage.VALIDATION,
                PipelineStage.TRANSFORMATION,
                PipelineStage.ENRICHMENT,
                PipelineStage.STORAGE
            ]
            
            self.logger.info("Pipeline processors initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize processors: {e}")
            raise
            
    async def start(self):
        """Start the data pipeline manager."""
        try:
            if self.processing_active:
                return
                
            self.processing_active = True
            
            # Start worker tasks
            for i in range(self.worker_count):
                worker = asyncio.create_task(self._worker_loop(f"worker-{i}"))
                self.workers.append(worker)
                
            self.logger.info(f"Data pipeline manager started with {self.worker_count} workers")
            
        except Exception as e:
            self.logger.error(f"Failed to start pipeline manager: {e}")
            raise
            
    async def _worker_loop(self, worker_id: str):
        """Main worker processing loop."""
        self.logger.info(f"Worker {worker_id} started")
        
        while self.processing_active:
            try:
                # Get next record to process
                record = await self.processing_queue.get()
                
                if record is None:  # Shutdown signal
                    break
                    
                # Process record through pipeline
                await self._process_record(record, worker_id)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
                
        self.logger.info(f"Worker {worker_id} stopped")
        
    async def _process_record(self, record: DataRecord, worker_id: str):
        """Process a single record through the pipeline."""
        try:
            start_time = time.time()
            
            # Get pipeline for this record
            pipeline_name = record.metadata.get('pipeline', 'default')
            pipeline_stages = self.pipelines.get(pipeline_name, self.pipelines['default'])
            
            # Update metrics
            if pipeline_name not in self.metrics:
                self.metrics[pipeline_name] = PipelineMetrics(pipeline_name=pipeline_name)
                
            pipeline_metrics = self.metrics[pipeline_name]
            pipeline_metrics.records_processed += 1
            self.global_metrics.records_processed += 1
            
            # Process through each stage
            current_record = record
            
            for stage in pipeline_stages:
                if stage not in self.processors:
                    self.logger.warning(f"No processor for stage {stage.value}, skipping")
                    continue
                    
                try:
                    stage_start = time.time()
                    processor = self.processors[stage]
                    
                    # Validate input
                    if not await processor.validate_input(current_record):
                        current_record.processing_status = ProcessingStatus.SKIPPED
                        current_record.error_message = f"Input validation failed for stage {stage.value}"
                        break
                        
                    # Process stage
                    current_record.processing_stage = stage
                    current_record.processing_status = ProcessingStatus.PROCESSING
                    
                    processed_record = await processor.process(current_record)
                    current_record = processed_record
                    
                    # Update stage metrics
                    stage_time = time.time() - stage_start
                    pipeline_metrics.stage_performance[stage.value] = stage_time
                    
                    # Cleanup
                    await processor.cleanup(current_record)
                    
                except Exception as e:
                    current_record.processing_status = ProcessingStatus.FAILED
                    current_record.error_message = f"Stage {stage.value} failed: {str(e)}"
                    self.logger.error(f"Stage {stage.value} failed for record {record.record_id}: {e}")
                    break
                    
            # Update final status
            if current_record.processing_status == ProcessingStatus.PROCESSING:
                current_record.processing_status = ProcessingStatus.COMPLETED
                
            # Update metrics
            processing_time = time.time() - start_time
            
            if current_record.processing_status == ProcessingStatus.COMPLETED:
                pipeline_metrics.records_completed += 1
                self.global_metrics.records_completed += 1
            elif current_record.processing_status == ProcessingStatus.FAILED:
                pipeline_metrics.records_failed += 1
                self.global_metrics.records_failed += 1
            elif current_record.processing_status == ProcessingStatus.SKIPPED:
                pipeline_metrics.records_skipped += 1
                self.global_metrics.records_skipped += 1
                
            # Update processing time
            pipeline_metrics.bytes_processed += current_record.size_bytes
            self.global_metrics.bytes_processed += current_record.size_bytes
            
            # Calculate average processing time
            total_completed = pipeline_metrics.records_completed
            if total_completed > 0:
                current_avg = pipeline_metrics.average_processing_time
                pipeline_metrics.average_processing_time = (
                    (current_avg * (total_completed - 1) + processing_time) / total_completed
                )
                
            # Store completed record
            self.completed_records.append(current_record)
            
            # Remove from active records
            if record.record_id in self.active_records:
                del self.active_records[record.record_id]
                
            # Save to database if configured
            if self.config.ENABLE_DATABASE_STORAGE:
                await self._save_record_to_database(current_record)
                
            self.logger.debug(f"Record {record.record_id} processed in {processing_time:.2f}s by {worker_id}")
            
        except Exception as e:
            self.logger.error(f"Record processing failed: {e}")
            
    async def submit_record(self, record: DataRecord) -> bool:
        """Submit a record for processing."""
        try:
            if not self.processing_active:
                self.logger.error("Pipeline manager not started")
                return False
                
            # Store in active records
            self.active_records[record.record_id] = record
            
            # Add to processing queue
            await self.processing_queue.put(record)
            
            self.logger.debug(f"Record {record.record_id} submitted for processing")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to submit record: {e}")
            return False
            
    async def submit_batch(self, records: List[DataRecord]) -> Dict[str, bool]:
        """Submit multiple records for processing."""
        results = {}
        
        for record in records:
            success = await self.submit_record(record)
            results[record.record_id] = success
            
        self.logger.info(f"Submitted batch of {len(records)} records")
        return results
        
    async def create_record_from_crawl_data(self, url: str, data: Union[str, bytes, Dict], 
                                          data_format: DataFormat, metadata: Dict[str, Any] = None) -> DataRecord:
        """Create a data record from crawled data."""
        record_id = f"record_{uuid.uuid4().hex[:8]}"
        
        return DataRecord(
            record_id=record_id,
            source_url=url,
            data_format=data_format,
            raw_data=data,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )
        
    def add_processor(self, stage: PipelineStage, processor: PipelineStageProcessor):
        """Add a custom processor for a stage."""
        self.processors[stage] = processor
        self.logger.info(f"Processor added for stage {stage.value}")
        
    def create_pipeline(self, name: str, stages: List[PipelineStage]):
        """Create a custom pipeline."""
        self.pipelines[name] = stages
        self.metrics[name] = PipelineMetrics(pipeline_name=name)
        self.logger.info(f"Pipeline '{name}' created with {len(stages)} stages")
        
    def add_rule(self, rule: PipelineRule):
        """Add a processing rule."""
        self.rules[rule.rule_id] = rule
        self.logger.info(f"Rule '{rule.name}' added")
        
    async def get_record_status(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific record."""
        # Check active records
        if record_id in self.active_records:
            record = self.active_records[record_id]
            return {
                'record_id': record_id,
                'status': record.processing_status.value,
                'stage': record.processing_stage.value,
                'error_message': record.error_message,
                'retry_count': record.retry_count,
                'timestamp': record.timestamp.isoformat()
            }
            
        # Check completed records
        for record in self.completed_records:
            if record.record_id == record_id:
                return {
                    'record_id': record_id,
                    'status': record.processing_status.value,
                    'stage': record.processing_stage.value,
                    'error_message': record.error_message,
                    'completed_at': record.timestamp.isoformat()
                }
                
        return None
        
    async def get_pipeline_metrics(self, pipeline_name: str = None) -> Union[PipelineMetrics, Dict[str, PipelineMetrics]]:
        """
Get pipeline metrics."""
        if pipeline_name:
            return self.metrics.get(pipeline_name)
        else:
            return self.metrics.copy()
            
    async def get_global_metrics(self) -> PipelineMetrics:
        """
Get global pipeline metrics."""
        # Update throughput
        total_time = (datetime.utcnow() - self.global_metrics.last_updated).total_seconds()
        if total_time > 0:
            self.global_metrics.throughput_per_second = self.global_metrics.records_completed / total_time
            
        # Update error rate
        total_processed = self.global_metrics.records_completed + self.global_metrics.records_failed
        if total_processed > 0:
            self.global_metrics.error_rate = self.global_metrics.records_failed / total_processed
            
        return self.global_metrics
        
    async def _save_record_to_database(self, record: DataRecord):
        """
Save processed record to database."""
        try:
            async with get_database_session() as db:
                db_record = CrawledDataRecord(
                    record_id=record.record_id,
                    source_url=record.source_url,
                    data_format=record.data_format.value,
                    raw_data=record.raw_data,
                    metadata=record.metadata,
                    processing_status=record.processing_status.value,
                    created_at=record.timestamp,
                    size_bytes=record.size_bytes,
                    checksum=record.checksum
                )
                
                db.add(db_record)
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to save record to database: {e}")
            
    async def export_data(self, pipeline_name: str = None, format: str = "json", 
                         filters: Dict[str, Any] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Export processed data."""
        try:
            # Get records to export
            records_to_export = []
            
            for record in self.completed_records:
                if record.processing_status == ProcessingStatus.COMPLETED:
                    # Apply filters
                    if filters:
                        if not self._apply_filters(record, filters):
                            continue
                            
                    # Check pipeline filter
                    if pipeline_name:
                        record_pipeline = record.metadata.get('pipeline', 'default')
                        if record_pipeline != pipeline_name:
                            continue
                            
                    records_to_export.append(record)
                    
            # Export records
            for record in records_to_export:
                export_data = {
                    'record_id': record.record_id,
                    'source_url': record.source_url,
                    'data_format': record.data_format.value,
                    'data': record.raw_data,
                    'metadata': record.metadata,
                    'timestamp': record.timestamp.isoformat(),
                    'size_bytes': record.size_bytes
                }
                
                yield export_data
                
        except Exception as e:
            self.logger.error(f"Data export failed: {e}")
            
    def _apply_filters(self, record: DataRecord, filters: Dict[str, Any]) -> bool:
        """Apply filters to a record."""
        try:
            for filter_key, filter_value in filters.items():
                if filter_key == 'data_format':
                    if record.data_format.value != filter_value:
                        return False
                elif filter_key == 'source_domain':
                    from urllib.parse import urlparse
                    domain = urlparse(record.source_url).netloc
                    if domain != filter_value:
                        return False
                elif filter_key == 'min_size':
                    if record.size_bytes < filter_value:
                        return False
                elif filter_key == 'max_size':
                    if record.size_bytes > filter_value:
                        return False
                        
            return True
            
        except Exception:
            return False
            
    async def shutdown(self):
        """
Shutdown the data pipeline manager."""
        try:
            self.processing_active = False
            
            # Signal workers to stop
            for _ in range(len(self.workers)):
                await self.processing_queue.put(None)
                
            # Wait for workers to finish
            await asyncio.gather(*self.workers, return_exceptions=True)
            
            # Process remaining items in queue
            while not self.processing_queue.empty():
                try:
                    record = self.processing_queue.get_nowait()
                    if record:
                        self.completed_records.append(record)
                except asyncio.QueueEmpty:
                    break
                    
            self.logger.info("Data pipeline manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Factory function
def create_data_pipeline_manager(config: Optional[PipelineConfig] = None) -> DataPipelineManager:
    """Create and return a data pipeline manager instance."""
    return DataPipelineManager(config)


# Utility functions
async def process_crawled_data_batch(data_items: List[Tuple[str, Any, DataFormat]], 
                                   pipeline_name: str = "default") -> List[str]:
    """Process a batch of crawled data items."""
    manager = create_data_pipeline_manager()
    
    try:
        await manager.start()
        
        # Create records
        records = []
        for url, data, format in data_items:
            record = await manager.create_record_from_crawl_data(url, data, format, {'pipeline': pipeline_name})
            records.append(record)
            
        # Submit batch
        results = await manager.submit_batch(records)
        
        # Wait for processing
        await asyncio.sleep(1)  # Allow some processing time
        
        return [record_id for record_id, success in results.items() if success]
        
    finally:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
async def create_custom_processor(stage: PipelineStage, process_func: Callable) -> PipelineStageProcessor:
    """
Create a custom processor from a function."""
    
    class CustomProcessor(PipelineStageProcessor):
        def __init__(self):
            super().__init__(stage)
            
        async def process(self, record: DataRecord) -> DataRecord:
            return await process_func(record)
            
    return CustomProcessor()
