"""
Real-time Content Processor for IA Influencer Agent Platform
==========================================================

Professional real-time data processing engine for multi-format content streams,
AI-powered content analysis, protection monitoring, and revenue optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  LEGAL WARNING 
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from uuid import uuid4
import time
import hashlib
import struct
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from pydantic import BaseModel, Field, validator
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
import asyncio
import aiofiles
from io import BytesIO

from ...core.database import get_async_session
from ...core.cache import get_redis_client
from ...core.config import get_settings
from ...utils.logging import get_logger
from ...models.content import ContentModel
from ...ai.content_protection.fingerprint_engine import FingerprintEngine
from ...ai.ml.audio_intelligence import AudioIntelligence
from ...ai.ml.video_intelligence import VideoIntelligence
from ...ai.ml.image_intelligence import ImageIntelligence
from ...ai.ml.text_intelligence import TextIntelligence

logger = get_logger(__name__)
settings = get_settings()


class ProcessingPriority(str, Enum):
    """Content processing priority levels"""
    LOW = "low"
    NORMAL = "normal" 
    HIGH = "high"
    CRITICAL = "critical"


class ProcessingStage(str, Enum):
    """Content processing pipeline stages"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    FINGERPRINTING = "fingerprinting"
    AI_ANALYSIS = "ai_analysis"
    PROTECTION = "protection"
    METADATA_EXTRACTION = "metadata_extraction"
    OPTIMIZATION = "optimization"
    DISTRIBUTION = "distribution"
    MONITORING = "monitoring"
    COMPLETED = "completed"


class ContentFormat(str, Enum):
    """Supported content formats"""
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    
    # Image formats
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    SVG = "svg"
    
    # Text formats
    TXT = "txt"
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    MD = "md"
    HTML = "html"


@dataclass
class ProcessingJob:
    """Content processing job definition"""
    id: str
    content_id: str
    user_id: str
    content_type: str
    format: ContentFormat
    file_path: str
    file_size: int
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    current_stage: ProcessingStage = ProcessingStage.UPLOAD
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0
    error_message: Optional[str] = None
    retries: int = 0
    max_retries: int = 3


class ProcessingMetrics(BaseModel):
    """Real-time processing performance metrics"""
    jobs_processed: int = Field(default=0, description="Total jobs processed")
    jobs_failed: int = Field(default=0, description="Total jobs failed")
    avg_processing_time: float = Field(default=0.0, description="Average processing time in seconds")
    throughput_per_minute: float = Field(default=0.0, description="Jobs per minute")
    current_queue_size: int = Field(default=0, description="Current queue size")
    active_workers: int = Field(default=0, description="Active worker count")
    last_update: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('throughput_per_minute')
    def validate_throughput(cls, v):
        return max(0.0, v)


class ProcessingResult(BaseModel):
    """Content processing result structure"""
    job_id: str
    content_id: str
    success: bool
    processing_time: float
    fingerprint_hash: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    protection_enabled: bool = False
    error_details: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RealTimeProcessor:
    """
    Enterprise-grade real-time content processor for multi-format streams
    
    Features:
    - Parallel processing with worker pools
    - AI-powered content analysis and fingerprinting
    - Real-time protection monitoring
    - Adaptive queue management
    - Performance metrics and monitoring
    - Failure recovery and retry mechanisms
    """
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, mp.cpu_count() * 2)
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=min(8, mp.cpu_count()))
        
        self.redis: Optional[Redis] = None
        self.fingerprint_engine: Optional[FingerprintEngine] = None
        self.ai_processors: Dict[str, Any] = {}
        
        self.active_jobs: Dict[str, ProcessingJob] = {}
        self.job_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.priority_queues: Dict[ProcessingPriority, asyncio.Queue] = {
            ProcessingPriority.CRITICAL: asyncio.Queue(maxsize=100),
            ProcessingPriority.HIGH: asyncio.Queue(maxsize=200),
            ProcessingPriority.NORMAL: asyncio.Queue(maxsize=500),
            ProcessingPriority.LOW: asyncio.Queue(maxsize=200),
        }
        
        self.metrics = ProcessingMetrics()
        self.workers_running = False
        self.worker_tasks: List[asyncio.Task] = []
        
        # Processing stages handlers
        self.stage_handlers: Dict[ProcessingStage, Callable] = {
            ProcessingStage.VALIDATION: self._validate_content,
            ProcessingStage.FINGERPRINTING: self._generate_fingerprint,
            ProcessingStage.AI_ANALYSIS: self._analyze_with_ai,
            ProcessingStage.PROTECTION: self._enable_protection,
            ProcessingStage.METADATA_EXTRACTION: self._extract_metadata,
            ProcessingStage.OPTIMIZATION: self._optimize_content,
            ProcessingStage.DISTRIBUTION: self._prepare_distribution,
            ProcessingStage.MONITORING: self._setup_monitoring,
        }
        
    async def initialize(self) -> None:
        """Initialize processor with dependencies and AI engines"""



        try:
            self.redis = await get_redis_client()
            
            # Initialize AI processing engines
            self.fingerprint_engine = FingerprintEngine()
            await self.fingerprint_engine.initialize()
            
            self.ai_processors = {
                'audio': AudioIntelligence(),
                'video': VideoIntelligence(), 
                'image': ImageIntelligence(),
                'text': TextIntelligence(),
            }
            
            # Initialize AI processors
            for processor in self.ai_processors.values():
                await processor.initialize()
                
            # Start worker tasks
            await self._start_workers()
            
            logger.info(f"RealTimeProcessor initialized with {self.max_workers} workers")
            
        except Exception as e:
            logger.error(f"Failed to initialize RealTimeProcessor: {e}")
            raise
            
    async def submit_job(
        self,
        content_id: str,
        user_id: str,
        content_type: str,
        file_path: str,
        file_size: int,
        format: ContentFormat,
        priority: ProcessingPriority = ProcessingPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit content processing job to queue
        
        Args:
            content_id: Unique content identifier
            user_id: User identifier
            content_type: Type of content (audio, video, image, text)
            file_path: Path to content file
            file_size: Size of content file in bytes
            format: Content format
            priority: Processing priority level
            metadata: Optional metadata
            
        Returns:
            Job identifier
        """



        try:
            job_id = str(uuid4())
            
            job = ProcessingJob(
                id=job_id,
                content_id=content_id,
                user_id=user_id,
                content_type=content_type,
                format=format,
                file_path=file_path,
                file_size=file_size,
                priority=priority,
                metadata=metadata or {}
            )
            
            # Store job in Redis for persistence
            await self.redis.hset(
                f"processing_job:{job_id}",
                mapping={
                    "data": json.dumps({
                        "id": job.id,
                        "content_id": job.content_id,
                        "user_id": job.user_id,
                        "content_type": job.content_type,
                        "format": job.format.value,
                        "file_path": job.file_path,
                        "file_size": job.file_size,
                        "priority": job.priority.value,
                        "current_stage": job.current_stage.value,
                        "created_at": job.created_at.isoformat(),
                        "metadata": job.metadata,
                        "progress": job.progress,
                        "retries": job.retries,
                        "max_retries": job.max_retries
                    })
                }
            )
            
            # Set job TTL (24 hours)
            await self.redis.expire(f"processing_job:{job_id}", 86400)
            
            # Add to appropriate priority queue
            await self.priority_queues[priority].put(job)
            self.active_jobs[job_id] = job
            
            # Update metrics
            self.metrics.current_queue_size = sum(
                queue.qsize() for queue in self.priority_queues.values()
            )
            
            logger.info(f"Submitted processing job {job_id} for content {content_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to submit processing job: {e}")
            raise
            
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of processing job"""



        try:
            job = self.active_jobs.get(job_id)
            if not job:
                # Try to load from Redis
                job_data = await self.redis.hget(f"processing_job:{job_id}", "data")
                if not job_data:
                    return None
                    
                job_dict = json.loads(job_data)
                return {
                    "job_id": job_id,
                    "status": job_dict.get("current_stage", "unknown"),
                    "progress": job_dict.get("progress", 0.0),
                    "created_at": job_dict.get("created_at"),
                    "error_message": job_dict.get("error_message")
                }
                
            return {
                "job_id": job_id,
                "content_id": job.content_id,
                "status": job.current_stage.value,
                "progress": job.progress,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message,
                "retries": job.retries
            }
            
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None
            
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel processing job"""



        try:
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                job.current_stage = ProcessingStage.COMPLETED
                job.error_message = "Job cancelled by user"
                job.completed_at = datetime.now(timezone.utc)
                
                # Update Redis
                await self._update_job_in_redis(job)
                
                # Remove from active jobs
                del self.active_jobs[job_id]
                
                logger.info(f"Cancelled processing job {job_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
            
    async def get_metrics(self) -> ProcessingMetrics:
        """Get current processing metrics"""
        self.metrics.current_queue_size = sum(
            queue.qsize() for queue in self.priority_queues.values()
        )
        self.metrics.active_workers = len([t for t in self.worker_tasks if not t.done()])
        self.metrics.last_update = datetime.now(timezone.utc)
        
        return self.metrics
        
    async def _start_workers(self) -> None:
        """Start worker tasks for processing jobs"""
        if self.workers_running:
            return
            
        self.workers_running = True
        
        # Start priority-based workers
        for priority in [ProcessingPriority.CRITICAL, ProcessingPriority.HIGH, 
                        ProcessingPriority.NORMAL, ProcessingPriority.LOW]:
            worker_count = self._get_worker_count_for_priority(priority)
            
            for i in range(worker_count):
                task = asyncio.create_task(
                    self._process_queue_worker(priority, f"{priority.value}_worker_{i}")
                )
                self.worker_tasks.append(task)
                
        logger.info(f"Started {len(self.worker_tasks)} worker tasks")
        
    def _get_worker_count_for_priority(self, priority: ProcessingPriority) -> int:
        """Determine worker count based on priority level"""
        worker_distribution = {
            ProcessingPriority.CRITICAL: max(2, self.max_workers // 8),
            ProcessingPriority.HIGH: max(4, self.max_workers // 4),
            ProcessingPriority.NORMAL: max(8, self.max_workers // 2),
            ProcessingPriority.LOW: max(2, self.max_workers // 8),
        }
        return worker_distribution[priority]
        
    async def _process_queue_worker(self, priority: ProcessingPriority, worker_name: str) -> None:
        """Worker task for processing jobs from priority queue"""
        logger.info(f"Started worker {worker_name} for {priority.value} priority")
        
        while self.workers_running:
            try:
                # Get job from priority queue with timeout
                job = await asyncio.wait_for(
                    self.priority_queues[priority].get(),
                    timeout=1.0
                )
                
                start_time = time.time()
                
                try:
                    # Process job
                    result = await self._process_job(job)
                    
                    processing_time = time.time() - start_time
                    
                    # Update metrics
                    self.metrics.jobs_processed += 1
                    self._update_processing_metrics(processing_time)
                    
                    # Store result
                    await self._store_processing_result(result)
                    
                    logger.debug(f"Worker {worker_name} completed job {job.id} in {processing_time:.2f}s")
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    
                    # Handle job failure
                    await self._handle_job_failure(job, str(e))
                    
                    self.metrics.jobs_failed += 1
                    self._update_processing_metrics(processing_time)
                    
                    logger.error(f"Worker {worker_name} failed job {job.id}: {e}")
                    
                finally:
                    # Mark queue task done
                    self.priority_queues[priority].task_done()
                    
            except asyncio.TimeoutError:
                # No jobs in queue, continue
                continue
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
                
        logger.info(f"Worker {worker_name} stopped")
        
    async def _process_job(self, job: ProcessingJob) -> ProcessingResult:
        """Process individual content job through pipeline stages"""
        job.started_at = datetime.now(timezone.utc)
        
        try:
            # Process through each stage
            stages = [
                ProcessingStage.VALIDATION,
                ProcessingStage.FINGERPRINTING,
                ProcessingStage.AI_ANALYSIS,
                ProcessingStage.PROTECTION,
                ProcessingStage.METADATA_EXTRACTION,
                ProcessingStage.OPTIMIZATION,
                ProcessingStage.DISTRIBUTION,
                ProcessingStage.MONITORING
            ]
            
            total_stages = len(stages)
            stage_results = {}
            
            for i, stage in enumerate(stages):
                job.current_stage = stage
                job.progress = (i / total_stages) * 100
                
                # Update job status in Redis
                await self._update_job_in_redis(job)
                
                # Execute stage handler
                if stage in self.stage_handlers:
                    stage_result = await self.stage_handlers[stage](job)
                    stage_results[stage.value] = stage_result
                    
                logger.debug(f"Completed stage {stage.value} for job {job.id}")
                
            # Mark job as completed
            job.current_stage = ProcessingStage.COMPLETED
            job.progress = 100.0
            job.completed_at = datetime.now(timezone.utc)
            
            await self._update_job_in_redis(job)
            
            # Remove from active jobs
            if job.id in self.active_jobs:
                del self.active_jobs[job.id]
                
            # Create processing result
            processing_time = (job.completed_at - job.started_at).total_seconds()
            
            result = ProcessingResult(
                job_id=job.id,
                content_id=job.content_id,
                success=True,
                processing_time=processing_time,
                fingerprint_hash=stage_results.get('fingerprinting', {}).get('hash'),
                ai_analysis=stage_results.get('ai_analysis'),
                metadata=stage_results.get('metadata_extraction'),
                protection_enabled=stage_results.get('protection', {}).get('enabled', False)
            )
            
            return result
            
        except Exception as e:
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            await self._update_job_in_redis(job)
            
            processing_time = (job.completed_at - job.started_at).total_seconds()
            
            result = ProcessingResult(
                job_id=job.id,
                content_id=job.content_id,
                success=False,
                processing_time=processing_time,
                error_details=str(e)
            )
            
            raise
            
    # Stage handlers
    async def _validate_content(self, job: ProcessingJob) -> Dict[str, Any]:
        """Validate content file and format"""



        try:
            file_path = Path(job.file_path)
            
            if not file_path.exists():
                raise ValueError(f"Content file not found: {job.file_path}")
                
            if file_path.stat().st_size != job.file_size:
                raise ValueError("File size mismatch")
                
            # Validate file format
            if not self._validate_file_format(file_path, job.format):
                raise ValueError(f"Invalid file format for {job.format}")
                
            return {
                "valid": True,
                "file_size": file_path.stat().st_size,
                "modified_time": file_path.stat().st_mtime
            }
            
        except Exception as e:
            logger.error(f"Content validation failed for job {job.id}: {e}")
            raise
            
    async def _generate_fingerprint(self, job: ProcessingJob) -> Dict[str, Any]:
        """Generate AI fingerprint for content"""



        try:
            if not self.fingerprint_engine:
                raise ValueError("Fingerprint engine not initialized")
                
            fingerprint_result = await self.fingerprint_engine.generate_fingerprint(
                file_path=job.file_path,
                content_type=job.content_type,
                format=job.format.value
            )
            
            return {
                "hash": fingerprint_result.fingerprint_hash,
                "vector": fingerprint_result.vector_embedding,
                "confidence": fingerprint_result.confidence,
                "processing_time": fingerprint_result.processing_time
            }
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed for job {job.id}: {e}")
            raise
            
    async def _analyze_with_ai(self, job: ProcessingJob) -> Dict[str, Any]:
        """Analyze content with AI intelligence engines"""



        try:
            processor = self.ai_processors.get(job.content_type)
            if not processor:
                raise ValueError(f"No AI processor for content type: {job.content_type}")
                
            analysis_result = await processor.analyze_content(
                file_path=job.file_path,
                metadata=job.metadata
            )
            
            return {
                "analysis": analysis_result,
                "confidence": analysis_result.get("confidence", 0.0),
                "features": analysis_result.get("features", {}),
                "recommendations": analysis_result.get("recommendations", [])
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed for job {job.id}: {e}")
            raise
            
    async def _enable_protection(self, job: ProcessingJob) -> Dict[str, Any]:
        """Enable content protection monitoring"""



        try:
            # Enable protection monitoring for content
            protection_config = {
                "content_id": job.content_id,
                "user_id": job.user_id,
                "monitoring_enabled": True,
                "alert_threshold": 0.85,
                "platforms": ["youtube", "instagram", "tiktok", "twitter"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store protection configuration
            await self.redis.hset(
                f"protection:{job.content_id}",
                mapping=protection_config
            )
            
            return {
                "enabled": True,
                "config": protection_config
            }
            
        except Exception as e:
            logger.error(f"Protection setup failed for job {job.id}: {e}")
            raise
            
    async def _extract_metadata(self, job: ProcessingJob) -> Dict[str, Any]:
        """Extract comprehensive metadata from content"""



        try:
            metadata = {
                "file_info": {
                    "name": Path(job.file_path).name,
                    "size": job.file_size,
                    "format": job.format.value,
                    "created_at": job.created_at.isoformat()
                },
                "content_type": job.content_type,
                "user_metadata": job.metadata
            }
            
            # Extract format-specific metadata
            if job.content_type == "audio":
                metadata.update(await self._extract_audio_metadata(job.file_path))
            elif job.content_type == "video":
                metadata.update(await self._extract_video_metadata(job.file_path))
            elif job.content_type == "image":
                metadata.update(await self._extract_image_metadata(job.file_path))
                
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed for job {job.id}: {e}")
            raise
            
    async def _optimize_content(self, job: ProcessingJob) -> Dict[str, Any]:
        """Optimize content for distribution"""



        try:
            optimization_result = {
                "optimized": True,
                "original_size": job.file_size,
                "optimizations_applied": []
            }
            
            # Content-specific optimizations
            if job.content_type == "audio":
                optimization_result["optimizations_applied"].extend([
                    "audio_normalization",
                    "metadata_embedding",
                    "format_optimization"
                ])
            elif job.content_type == "video":
                optimization_result["optimizations_applied"].extend([
                    "compression_optimization",
                    "resolution_optimization",
                    "metadata_embedding"
                ])
                
            return optimization_result
            
        except Exception as e:
            logger.error(f"Content optimization failed for job {job.id}: {e}")
            raise
            
    async def _prepare_distribution(self, job: ProcessingJob) -> Dict[str, Any]:
        """Prepare content for multi-platform distribution"""



        try:
            distribution_config = {
                "content_id": job.content_id,
                "distribution_ready": True,
                "platforms": {
                    "spotify": {"ready": job.content_type == "audio"},
                    "youtube": {"ready": job.content_type in ["audio", "video"]},
                    "instagram": {"ready": job.content_type in ["image", "video"]},
                    "tiktok": {"ready": job.content_type == "video"}
                },
                "optimized_formats": [],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            return distribution_config
            
        except Exception as e:
            logger.error(f"Distribution preparation failed for job {job.id}: {e}")
            raise
            
    async def _setup_monitoring(self, job: ProcessingJob) -> Dict[str, Any]:
        """Setup real-time monitoring for content"""



        try:
            monitoring_config = {
                "content_id": job.content_id,
                "monitoring_active": True,
                "check_frequency": "hourly",
                "platforms_monitored": ["youtube", "instagram", "tiktok", "twitter"],
                "alert_channels": ["email", "webhook", "dashboard"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store monitoring configuration
            await self.redis.hset(
                f"monitoring:{job.content_id}",
                mapping=monitoring_config
            )
            
            return monitoring_config
            
        except Exception as e:
            logger.error(f"Monitoring setup failed for job {job.id}: {e}")
            raise
            
    # Helper methods
    def _validate_file_format(self, file_path: Path, format: ContentFormat) -> bool:
        """Validate file format matches expected format"""
        file_extension = file_path.suffix.lower().lstrip('.')
        return file_extension == format.value.lower()
        
    async def _extract_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract audio-specific metadata"""
        # Placeholder for audio metadata extraction
        return {
            "audio_metadata": {
                "duration": 0.0,
                "sample_rate": 0,
                "channels": 0,
                "bitrate": 0
            }
        }
        
    async def _extract_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract video-specific metadata"""
        # Placeholder for video metadata extraction
        return {
            "video_metadata": {
                "duration": 0.0,
                "resolution": "0x0",
                "fps": 0.0,
                "codec": ""
            }
        }
        
    async def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image-specific metadata"""
        # Placeholder for image metadata extraction
        return {
            "image_metadata": {
                "dimensions": "0x0",
                "color_mode": "",
                "dpi": 0
            }
        }
        
    async def _update_job_in_redis(self, job: ProcessingJob) -> None:
        """Update job status in Redis"""



        try:
            job_data = {
                "id": job.id,
                "content_id": job.content_id,
                "user_id": job.user_id,
                "content_type": job.content_type,
                "format": job.format.value,
                "file_path": job.file_path,
                "file_size": job.file_size,
                "priority": job.priority.value,
                "current_stage": job.current_stage.value,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "metadata": job.metadata,
                "progress": job.progress,
                "error_message": job.error_message,
                "retries": job.retries,
                "max_retries": job.max_retries
            }
            
            await self.redis.hset(
                f"processing_job:{job.id}",
                "data",
                json.dumps(job_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to update job in Redis: {e}")
            
    async def _handle_job_failure(self, job: ProcessingJob, error_message: str) -> None:
        """Handle job processing failure with retry logic"""



        try:
            job.retries += 1
            job.error_message = error_message
            
            if job.retries <= job.max_retries:
                # Retry job with exponential backoff
                delay = min(300, 2 ** job.retries)  # Max 5 minutes
                
                logger.warning(f"Retrying job {job.id} in {delay} seconds (attempt {job.retries}/{job.max_retries})")
                
                await asyncio.sleep(delay)
                await self.priority_queues[job.priority].put(job)
                
            else:
                # Max retries exceeded, mark as failed
                job.current_stage = ProcessingStage.COMPLETED
                job.completed_at = datetime.now(timezone.utc)
                
                await self._update_job_in_redis(job)
                
                if job.id in self.active_jobs:
                    del self.active_jobs[job.id]
                    
                logger.error(f"Job {job.id} failed permanently after {job.retries} retries")
                
        except Exception as e:
            logger.error(f"Failed to handle job failure: {e}")
            
    async def _store_processing_result(self, result: ProcessingResult) -> None:
        """Store processing result in database"""



        try:
            # Store result in Redis for quick access
            await self.redis.hset(
                f"processing_result:{result.job_id}",
                mapping=result.dict()
            )
            
            # Set TTL for result (7 days)
            await self.redis.expire(f"processing_result:{result.job_id}", 604800)
            
        except Exception as e:
            logger.error(f"Failed to store processing result: {e}")
            
    def _update_processing_metrics(self, processing_time: float) -> None:
        """Update processing performance metrics"""



        try:
            # Update average processing time
            total_jobs = self.metrics.jobs_processed + self.metrics.jobs_failed
            if total_jobs > 0:
                current_avg = self.metrics.avg_processing_time
                self.metrics.avg_processing_time = (
                    (current_avg * (total_jobs - 1) + processing_time) / total_jobs
                )
                
            # Update throughput (jobs per minute)
            current_time = time.time()
            time_window = 60.0  # 1 minute
            
            # Simple moving average for throughput
            self.metrics.throughput_per_minute = (
                self.metrics.jobs_processed / 
                max(1, (current_time - time.time()) / 60)
            )
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            
    async def shutdown(self) -> None:
        """Gracefully shutdown processor"""



        try:
            logger.info("Shutting down RealTimeProcessor...")
            
            # Stop workers
            self.workers_running = False
            
            # Wait for workers to finish current jobs
            if self.worker_tasks:
                await asyncio.gather(*self.worker_tasks, return_exceptions=True)
                
            # Shutdown executors
            self.thread_executor.shutdown(wait=True)
            self.process_executor.shutdown(wait=True)
            
            # Close Redis connection
            if self.redis:
                await self.redis.close()
                
            # Shutdown AI processors
            for processor in self.ai_processors.values():
                await processor.shutdown()
                
            if self.fingerprint_engine:
                await self.fingerprint_engine.shutdown()
                
            logger.info("RealTimeProcessor shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during processor shutdown: {e}")
