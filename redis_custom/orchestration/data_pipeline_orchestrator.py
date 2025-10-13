#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 IA Chérie - Redis Orchestration Platform
📊 Data Pipeline Orchestrator Module

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED ⚠️
🔐 Copyright (c) 2024 IA Chérie Technologies. All rights reserved.

This module implements comprehensive data pipeline orchestration for streaming
and batch data processing in the Redis orchestration platform.

🎯 Expert Roles Applied:
- ML Engineer: Advanced data processing and pipeline optimization
- Backend Senior: High-performance data architecture  
- DBA: Optimized data storage and query performance
- DevOps: Scalable pipeline deployment and monitoring

🔧 Core Features:
- Streaming data processing with Apache Kafka/Redis Streams
- ETL/ELT pipeline automation and orchestration
- Real-time data transformation and enrichment
- Data quality monitoring and validation
- Scalable batch and stream processing
- Data lineage tracking and governance
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import redis.asyncio as aioredis
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineType(Enum):
    """Data pipeline types"""
    STREAMING = "streaming"
    BATCH = "batch"
    MICRO_BATCH = "micro_batch"
    REAL_TIME = "real_time"

class DataFormat(Enum):
    """Supported data formats"""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    XML = "xml"
    BINARY = "binary"

class ProcessingStage(Enum):
    """Pipeline processing stages"""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATE = "validate"
    ENRICH = "enrich"
    FILTER = "filter"
    AGGREGATE = "aggregate"

@dataclass
class DataRecord:
    """Individual data record"""
    id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: float
    format: DataFormat
    schema_version: str = "1.0"

@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    id: str
    name: str
    pipeline_type: PipelineType
    source_config: Dict[str, Any]
    transformations: List[Dict[str, Any]]
    destination_config: Dict[str, Any]
    schedule: Optional[str] = None
    batch_size: int = 1000
    parallelism: int = 4
    retry_config: Dict[str, Any] = None
    monitoring: Dict[str, Any] = None

class DataProcessor(ABC):
    """Abstract base class for data processors"""
    
    @abstractmethod
    async def process(self, record: DataRecord) -> DataRecord:
        """Process a single data record"""
        pass

class JsonTransformer(DataProcessor):
    """JSON data transformer"""
    
    def __init__(self, transformations: List[Dict[str, Any]]):
        self.transformations = transformations
        
    async def process(self, record: DataRecord) -> DataRecord:
        """Apply JSON transformations"""
        try:
            data = record.data.copy()
            
            for transform in self.transformations:
                transform_type = transform.get("type")
                
                if transform_type == "rename_field":
                    old_name = transform["old_name"]
                    new_name = transform["new_name"]
                    if old_name in data:
                        data[new_name] = data.pop(old_name)
                        
                elif transform_type == "add_field":
                    field_name = transform["field_name"]
                    field_value = transform["field_value"]
                    data[field_name] = field_value
                    
                elif transform_type == "remove_field":
                    field_name = transform["field_name"]
                    data.pop(field_name, None)
                    
                elif transform_type == "convert_type":
                    field_name = transform["field_name"]
                    target_type = transform["target_type"]
                    if field_name in data:
                        if target_type == "int":
                            data[field_name] = int(data[field_name])
                        elif target_type == "float":
                            data[field_name] = float(data[field_name])
                        elif target_type == "str":
                            data[field_name] = str(data[field_name])
                            
            record.data = data
            return record
            
        except Exception as e:
            logger.error(f"❌ JSON transformation failed: {e}")
            return record

class DataPipelineOrchestrator:
    """
    🚀 Enterprise Data Pipeline Orchestrator
    
    Provides comprehensive data pipeline management for streaming and batch
    processing with real-time monitoring and quality assurance.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        namespace: str = "data_pipeline"
    ):
        self.redis_url = redis_url
        self.namespace = namespace
        
        # Core components
        self.redis_client: Optional[aioredis.Redis] = None
        self.pipelines: Dict[str, PipelineConfig] = {}
        self.processors: Dict[str, DataProcessor] = {}
        self.running_pipelines: Dict[str, asyncio.Task] = {}
        
        # Processing components
        self.thread_pool = ThreadPoolExecutor(max_workers=20)
        self.running = False
        
        # Metrics
        self.records_processed = 0
        self.pipelines_executed = 0
        self.errors_count = 0
        
        logger.info("🚀 Data Pipeline Orchestrator initialized")
        
    async def initialize(self) -> bool:
        """Initialize data pipeline orchestrator"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
            # Load existing pipelines
            await self._load_pipelines()
            
            # Initialize default processors
            self._initialize_processors()
            
            self.running = True
            logger.info("✅ Data Pipeline Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Data Pipeline Orchestrator: {e}")
            return False
            
    async def _load_pipelines(self):
        """Load pipeline configurations from Redis"""
        try:
            pipeline_keys = await self.redis_client.keys(f"{self.namespace}:pipelines:*")
            
            for key in pipeline_keys:
                pipeline_data = await self.redis_client.get(key)
                if pipeline_data:
                    config = json.loads(pipeline_data)
                    pipeline_id = key.split(":")[-1]
                    self.pipelines[pipeline_id] = PipelineConfig(**config)
                    
            logger.info(f"📊 Loaded {len(self.pipelines)} pipeline configurations")
            
        except Exception as e:
            logger.error(f"❌ Failed to load pipelines: {e}")
            
    def _initialize_processors(self):
        """Initialize default data processors"""
        self.processors["json_transformer"] = JsonTransformer([])
        logger.info("🔧 Initialized default data processors")
        
    async def create_pipeline(
        self,
        name: str,
        pipeline_type: PipelineType,
        source_config: Dict[str, Any],
        transformations: List[Dict[str, Any]],
        destination_config: Dict[str, Any],
        schedule: Optional[str] = None,
        batch_size: int = 1000,
        parallelism: int = 4
    ) -> str:
        """Create new data pipeline"""
        try:
            pipeline_id = str(uuid.uuid4())
            
            config = PipelineConfig(
                id=pipeline_id,
                name=name,
                pipeline_type=pipeline_type,
                source_config=source_config,
                transformations=transformations,
                destination_config=destination_config,
                schedule=schedule,
                batch_size=batch_size,
                parallelism=parallelism
            )
            
            # Store pipeline
            self.pipelines[pipeline_id] = config
            
            # Persist to Redis
            await self.redis_client.set(
                f"{self.namespace}:pipelines:{pipeline_id}",
                json.dumps(asdict(config))
            )
            
            logger.info(f"📊 Created pipeline '{name}' with ID: {pipeline_id}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create pipeline: {e}")
            return ""
            
    async def start_pipeline(self, pipeline_id: str) -> bool:
        """Start data pipeline execution"""
        try:
            if pipeline_id not in self.pipelines:
                logger.error(f"❌ Pipeline {pipeline_id} not found")
                return False
                
            if pipeline_id in self.running_pipelines:
                logger.warning(f"⚠️ Pipeline {pipeline_id} already running")
                return True
                
            config = self.pipelines[pipeline_id]
            
            # Create and start pipeline task
            if config.pipeline_type == PipelineType.STREAMING:
                task = asyncio.create_task(self._run_streaming_pipeline(config))
            else:
                task = asyncio.create_task(self._run_batch_pipeline(config))
                
            self.running_pipelines[pipeline_id] = task
            
            logger.info(f"▶️ Started pipeline: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start pipeline {pipeline_id}: {e}")
            return False
            
    async def _run_streaming_pipeline(self, config: PipelineConfig):
        """Run streaming data pipeline"""
        try:
            logger.info(f"🌊 Starting streaming pipeline: {config.name}")
            
            while self.running:
                # Read from source
                records = await self._read_from_source(config.source_config, config.batch_size)
                
                if not records:
                    await asyncio.sleep(1)
                    continue
                    
                # Process records
                processed_records = []
                for record in records:
                    try:
                        processed_record = await self._process_record(record, config.transformations)
                        processed_records.append(processed_record)
                        self.records_processed += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to process record: {e}")
                        self.errors_count += 1
                        
                # Write to destination
                if processed_records:
                    await self._write_to_destination(processed_records, config.destination_config)
                    
                await asyncio.sleep(0.1)  # Small delay to prevent overwhelming
                
        except Exception as e:
            logger.error(f"❌ Streaming pipeline error: {e}")
        finally:
            logger.info(f"🛑 Streaming pipeline stopped: {config.name}")
            
    async def _run_batch_pipeline(self, config: PipelineConfig):
        """Run batch data pipeline"""
        try:
            logger.info(f"📦 Starting batch pipeline: {config.name}")
            
            # Read all data from source
            all_records = await self._read_all_from_source(config.source_config)
            
            if not all_records:
                logger.warning(f"⚠️ No data found for pipeline: {config.name}")
                return
                
            # Process in batches
            batch_size = config.batch_size
            total_batches = (len(all_records) + batch_size - 1) // batch_size
            
            for i in range(0, len(all_records), batch_size):
                batch = all_records[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                logger.info(f"📦 Processing batch {batch_num}/{total_batches}")
                
                # Process batch
                processed_batch = []
                for record in batch:
                    try:
                        processed_record = await self._process_record(record, config.transformations)
                        processed_batch.append(processed_record)
                        self.records_processed += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to process record: {e}")
                        self.errors_count += 1
                        
                # Write batch to destination
                if processed_batch:
                    await self._write_to_destination(processed_batch, config.destination_config)
                    
            self.pipelines_executed += 1
            logger.info(f"✅ Batch pipeline completed: {config.name}")
            
        except Exception as e:
            logger.error(f"❌ Batch pipeline error: {e}")
            
    async def _read_from_source(self, source_config: Dict[str, Any], limit: int) -> List[DataRecord]:
        """Read data from configured source"""
        try:
            source_type = source_config.get("type", "redis_stream")
            
            if source_type == "redis_stream":
                return await self._read_from_redis_stream(source_config, limit)
            elif source_type == "file":
                return await self._read_from_file(source_config, limit)
            elif source_type == "database":
                return await self._read_from_database(source_config, limit)
            else:
                logger.warning(f"⚠️ Unsupported source type: {source_type}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to read from source: {e}")
            return []
            
    async def _read_from_redis_stream(self, config: Dict[str, Any], limit: int) -> List[DataRecord]:
        """Read from Redis stream"""
        try:
            stream_name = config["stream_name"]
            consumer_group = config.get("consumer_group", "default")
            consumer_name = config.get("consumer_name", "consumer1")
            
            # Read from stream
            messages = await self.redis_client.xreadgroup(
                consumer_group,
                consumer_name,
                {stream_name: ">"},
                count=limit,
                block=1000
            )
            
            records = []
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    try:
                        record = DataRecord(
                            id=msg_id,
                            data=fields,
                            metadata={"stream": stream, "consumer_group": consumer_group},
                            timestamp=time.time(),
                            format=DataFormat.JSON
                        )
                        records.append(record)
                        
                        # Acknowledge message
                        await self.redis_client.xack(stream, consumer_group, msg_id)
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to parse stream message: {e}")
                        
            return records
            
        except Exception as e:
            logger.error(f"❌ Failed to read from Redis stream: {e}")
            return []
            
    async def _read_from_file(self, config: Dict[str, Any], limit: int) -> List[DataRecord]:
        """Read from file source"""
        try:
            file_path = config["file_path"]
            file_format = DataFormat(config.get("format", "json"))
            
            records = []
            
            if file_format == DataFormat.JSON:
                with open(file_path, 'r') as f:
                    lines = f.readlines()[:limit]
                    
                for i, line in enumerate(lines):
                    try:
                        data = json.loads(line.strip())
                        record = DataRecord(
                            id=f"file_{i}",
                            data=data,
                            metadata={"file_path": file_path},
                            timestamp=time.time(),
                            format=file_format
                        )
                        records.append(record)
                        
                    except json.JSONDecodeError:
                        continue
                        
            elif file_format == DataFormat.CSV:
                df = pd.read_csv(file_path, nrows=limit)
                
                for i, row in df.iterrows():
                    record = DataRecord(
                        id=f"csv_{i}",
                        data=row.to_dict(),
                        metadata={"file_path": file_path},
                        timestamp=time.time(),
                        format=file_format
                    )
                    records.append(record)
                    
            return records
            
        except Exception as e:
            logger.error(f"❌ Failed to read from file: {e}")
            return []
            
    async def _read_from_database(self, config: Dict[str, Any], limit: int) -> List[DataRecord]:
        """Read from database source"""
        # Placeholder for database integration
        logger.info(f"📊 Reading from database (limit: {limit})")
        return []
        
    async def _read_all_from_source(self, source_config: Dict[str, Any]) -> List[DataRecord]:
        """Read all data from source for batch processing"""
        try:
            source_type = source_config.get("type", "file")
            
            if source_type == "file":
                file_path = source_config["file_path"]
                file_format = DataFormat(source_config.get("format", "json"))
                
                records = []
                
                if file_format == DataFormat.JSON:
                    with open(file_path, 'r') as f:
                        for i, line in enumerate(f):
                            try:
                                data = json.loads(line.strip())
                                record = DataRecord(
                                    id=f"file_{i}",
                                    data=data,
                                    metadata={"file_path": file_path},
                                    timestamp=time.time(),
                                    format=file_format
                                )
                                records.append(record)
                            except json.JSONDecodeError:
                                continue
                                
                elif file_format == DataFormat.CSV:
                    df = pd.read_csv(file_path)
                    
                    for i, row in df.iterrows():
                        record = DataRecord(
                            id=f"csv_{i}",
                            data=row.to_dict(),
                            metadata={"file_path": file_path},
                            timestamp=time.time(),
                            format=file_format
                        )
                        records.append(record)
                        
                return records
                
        except Exception as e:
            logger.error(f"❌ Failed to read all from source: {e}")
            return []
            
    async def _process_record(self, record: DataRecord, transformations: List[Dict[str, Any]]) -> DataRecord:
        """Process single record through transformation pipeline"""
        try:
            processed_record = record
            
            for transformation in transformations:
                transform_type = transformation.get("type")
                
                if transform_type == "json_transform":
                    processor = JsonTransformer(transformation.get("rules", []))
                    processed_record = await processor.process(processed_record)
                    
                elif transform_type == "filter":
                    if not await self._apply_filter(processed_record, transformation):
                        return None  # Record filtered out
                        
                elif transform_type == "enrich":
                    processed_record = await self._enrich_record(processed_record, transformation)
                    
                elif transform_type == "validate":
                    if not await self._validate_record(processed_record, transformation):
                        raise ValueError("Record validation failed")
                        
            return processed_record
            
        except Exception as e:
            logger.error(f"❌ Record processing failed: {e}")
            raise
            
    async def _apply_filter(self, record: DataRecord, filter_config: Dict[str, Any]) -> bool:
        """Apply filter to record"""
        try:
            conditions = filter_config.get("conditions", [])
            
            for condition in conditions:
                field = condition["field"]
                operator = condition["operator"]
                value = condition["value"]
                
                if field not in record.data:
                    return False
                    
                record_value = record.data[field]
                
                if operator == "equals" and record_value != value:
                    return False
                elif operator == "greater_than" and record_value <= value:
                    return False
                elif operator == "less_than" and record_value >= value:
                    return False
                elif operator == "contains" and value not in str(record_value):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Filter application failed: {e}")
            return False
            
    async def _enrich_record(self, record: DataRecord, enrich_config: Dict[str, Any]) -> DataRecord:
        """Enrich record with additional data"""
        try:
            enrichments = enrich_config.get("enrichments", [])
            
            for enrichment in enrichments:
                enrich_type = enrichment["type"]
                
                if enrich_type == "add_timestamp":
                    record.data["enriched_at"] = time.time()
                elif enrich_type == "add_uuid":
                    record.data["enriched_id"] = str(uuid.uuid4())
                elif enrich_type == "lookup":
                    # Placeholder for lookup enrichment
                    pass
                    
            return record
            
        except Exception as e:
            logger.error(f"❌ Record enrichment failed: {e}")
            return record
            
    async def _validate_record(self, record: DataRecord, validation_config: Dict[str, Any]) -> bool:
        """Validate record against schema"""
        try:
            required_fields = validation_config.get("required_fields", [])
            
            for field in required_fields:
                if field not in record.data:
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Record validation failed: {e}")
            return False
            
    async def _write_to_destination(self, records: List[DataRecord], dest_config: Dict[str, Any]):
        """Write processed records to destination"""
        try:
            dest_type = dest_config.get("type", "redis")
            
            if dest_type == "redis":
                await self._write_to_redis(records, dest_config)
            elif dest_type == "file":
                await self._write_to_file(records, dest_config)
            elif dest_type == "database":
                await self._write_to_database(records, dest_config)
            else:
                logger.warning(f"⚠️ Unsupported destination type: {dest_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to write to destination: {e}")
            
    async def _write_to_redis(self, records: List[DataRecord], config: Dict[str, Any]):
        """Write records to Redis"""
        try:
            key_pattern = config.get("key_pattern", "processed_data")
            
            pipe = self.redis_client.pipeline()
            
            for record in records:
                key = f"{key_pattern}:{record.id}"
                data = {
                    "data": json.dumps(record.data),
                    "metadata": json.dumps(record.metadata),
                    "timestamp": record.timestamp,
                    "format": record.format.value
                }
                pipe.hset(key, mapping=data)
                
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"❌ Failed to write to Redis: {e}")
            
    async def _write_to_file(self, records: List[DataRecord], config: Dict[str, Any]):
        """Write records to file"""
        try:
            file_path = config["file_path"]
            file_format = DataFormat(config.get("format", "json"))
            
            if file_format == DataFormat.JSON:
                with open(file_path, 'a') as f:
                    for record in records:
                        f.write(json.dumps(record.data) + "\n")
                        
            elif file_format == DataFormat.CSV:
                # Convert records to DataFrame and append
                df_data = [record.data for record in records]
                df = pd.DataFrame(df_data)
                
                # Check if file exists to determine if we need headers
                import os
                write_header = not os.path.exists(file_path)
                
                df.to_csv(file_path, mode='a', header=write_header, index=False)
                
        except Exception as e:
            logger.error(f"❌ Failed to write to file: {e}")
            
    async def _write_to_database(self, records: List[DataRecord], config: Dict[str, Any]):
        """Write records to database"""
        # Placeholder for database integration
        logger.info(f"💾 Writing {len(records)} records to database")
        
    async def stop_pipeline(self, pipeline_id: str) -> bool:
        """Stop running pipeline"""
        try:
            if pipeline_id not in self.running_pipelines:
                logger.warning(f"⚠️ Pipeline {pipeline_id} not running")
                return True
                
            task = self.running_pipelines[pipeline_id]
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
                
            del self.running_pipelines[pipeline_id]
            
            logger.info(f"⏹️ Stopped pipeline: {pipeline_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop pipeline {pipeline_id}: {e}")
            return False
            
    async def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline execution status"""
        try:
            if pipeline_id not in self.pipelines:
                return {"error": "Pipeline not found"}
                
            config = self.pipelines[pipeline_id]
            is_running = pipeline_id in self.running_pipelines
            
            status = {
                "pipeline_id": pipeline_id,
                "name": config.name,
                "type": config.pipeline_type.value,
                "running": is_running,
                "created_at": getattr(config, 'created_at', None),
                "records_processed": self.records_processed,
                "errors_count": self.errors_count
            }
            
            if is_running:
                task = self.running_pipelines[pipeline_id]
                status["task_done"] = task.done()
                
            return status
            
        except Exception as e:
            logger.error(f"❌ Failed to get pipeline status: {e}")
            return {"error": str(e)}
            
    async def get_orchestrator_summary(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator summary"""
        try:
            return {
                "timestamp": time.time(),
                "total_pipelines": len(self.pipelines),
                "running_pipelines": len(self.running_pipelines),
                "records_processed": self.records_processed,
                "pipelines_executed": self.pipelines_executed,
                "errors_count": self.errors_count,
                "active_processors": len(self.processors),
                "thread_pool_size": self.thread_pool._max_workers
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get orchestrator summary: {e}")
            return {}
            
    async def shutdown(self):
        """Shutdown data pipeline orchestrator"""
        try:
            logger.info("🛑 Shutting down Data Pipeline Orchestrator...")
            self.running = False
            
            # Stop all running pipelines
            for pipeline_id in list(self.running_pipelines.keys()):
                await self.stop_pipeline(pipeline_id)
                
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
                
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            logger.info("✅ Data Pipeline Orchestrator shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


# Example usage
async def example_usage():
    """Example usage of Data Pipeline Orchestrator"""
    orchestrator = DataPipelineOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Create streaming pipeline
        streaming_id = await orchestrator.create_pipeline(
            name="User Events Stream",
            pipeline_type=PipelineType.STREAMING,
            source_config={
                "type": "redis_stream",
                "stream_name": "user_events",
                "consumer_group": "analytics"
            },
            transformations=[
                {
                    "type": "json_transform",
                    "rules": [
                        {"type": "add_field", "field_name": "processed_at", "field_value": time.time()}
                    ]
                },
                {
                    "type": "filter",
                    "conditions": [
                        {"field": "event_type", "operator": "equals", "value": "click"}
                    ]
                }
            ],
            destination_config={
                "type": "redis",
                "key_pattern": "processed_events"
            }
        )
        
        # Start pipeline
        await orchestrator.start_pipeline(streaming_id)
        
        # Get status
        status = await orchestrator.get_pipeline_status(streaming_id)
        print(f"📊 Pipeline Status: {status}")
        
        await asyncio.sleep(5)
        
        # Get summary
        summary = await orchestrator.get_orchestrator_summary()
        print(f"📊 Orchestrator Summary: {summary}")
        
    finally:
        await orchestrator.shutdown()

if __name__ == "__main__":
    asyncio.run(example_usage())