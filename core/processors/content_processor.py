"""
Content Processor Module - IA-Influencer-Agent Platform

Industrial-grade content processing orchestrator for content creators and influencers.
Manages the complete content pipeline from upload to distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Any unauthorized use, copying, 
distribution, or commercialization without explicit written permission is 
strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
================================================================================
"""

import asyncio
import logging
import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Union, BinaryIO, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import uuid

# Import individual processors
from .audio_processor import AudioProcessor, AudioProcessingConfig
from .video_processor import VideoProcessor, VideoProcessingConfig
from .image_processor import ImageProcessor, ImageProcessingConfig
from .text_processor import TextProcessor, TextProcessingConfig
from .document_processor import DocumentProcessor, DocumentProcessingConfig
from .multimedia_processor import MultimediaProcessor, MultimediaProcessingConfig

# Workflow and pipeline imports
try:
    import celery
    from celery import group, chain, chord
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

# Content analysis and enhancement
try:
    import openai
    from transformers import pipeline
    AI_ENHANCEMENT_AVAILABLE = True
except ImportError:
    AI_ENHANCEMENT_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Types of content"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MULTIMEDIA = "multimedia"
    UNKNOWN = "unknown"


class ProcessingStage(str, Enum):
    """Content processing stages"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    ANALYSIS = "analysis"
    ENHANCEMENT = "enhancement"
    PROTECTION = "protection"
    OPTIMIZATION = "optimization"
    DISTRIBUTION = "distribution"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingPriority(str, Enum):
    """Processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    REAL_TIME = "real_time"


class ContentStatus(str, Enum):
    """Content status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ENHANCED = "enhanced"
    PROTECTED = "protected"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    FAILED = "failed"
    DELETED = "deleted"


@dataclass
class ContentProcessingConfig:
    """Configuration for content processing"""
    # Pipeline configuration
    enable_auto_enhancement: bool = True
    enable_content_protection: bool = True
    enable_seo_optimization: bool = True
    enable_quality_checks: bool = True
    enable_content_moderation: bool = True
    enable_accessibility_checks: bool = True
    enable_analytics_tracking: bool = True
    
    # Processing preferences
    default_priority: ProcessingPriority = ProcessingPriority.NORMAL
    max_concurrent_jobs: int = 10
    job_timeout: int = 3600  # 1 hour
    retry_attempts: int = 3
    retry_delay: int = 60  # 1 minute
    
    # Quality thresholds
    min_quality_score: float = 0.6
    min_uniqueness_score: float = 0.7
    max_similarity_threshold: float = 0.8
    
    # Content constraints
    max_file_size: int = 2 * 1024 * 1024 * 1024  # 2GB
    supported_formats: List[str] = field(default_factory=lambda: [
        'mp4', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'png', 'pdf', 'docx', 'txt'
    ])
    
    # Enhancement settings
    auto_generate_thumbnails: bool = True
    auto_generate_transcripts: bool = True
    auto_generate_summaries: bool = True
    auto_generate_tags: bool = True
    auto_generate_titles: bool = True
    auto_generate_descriptions: bool = True
    
    # Distribution settings
    auto_publish: bool = False
    default_visibility: str = "private"
    enable_social_sharing: bool = True
    enable_cross_platform: bool = True
    
    # Individual processor configs
    audio_config: Optional[Dict[str, Any]] = None
    video_config: Optional[Dict[str, Any]] = None
    image_config: Optional[Dict[str, Any]] = None
    text_config: Optional[Dict[str, Any]] = None
    document_config: Optional[Dict[str, Any]] = None
    multimedia_config: Optional[Dict[str, Any]] = None


@dataclass
class ContentMetadata:
    """Comprehensive content metadata"""
    content_id: str
    content_type: ContentType
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    creator_id: Optional[str] = None
    creator_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    language: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    uploaded_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    copyright_info: Optional[str] = None
    license_type: Optional[str] = None
    content_rating: Optional[str] = None
    visibility: str = "private"
    is_monetizable: bool = False
    is_original: bool = True
    source_url: Optional[str] = None
    content_fingerprint: Optional[str] = None
    similarity_hash: Optional[str] = None


@dataclass
class ProcessingJob:
    """Content processing job"""
    job_id: str
    content_id: str
    stage: ProcessingStage
    status: ContentStatus
    priority: ProcessingPriority
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    result_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentEnhancement:
    """Content enhancement results"""
    auto_generated_title: Optional[str] = None
    auto_generated_description: Optional[str] = None
    auto_generated_tags: List[str] = field(default_factory=list)
    auto_generated_summary: Optional[str] = None
    auto_generated_transcript: Optional[str] = None
    auto_generated_captions: List[Dict[str, Any]] = field(default_factory=list)
    auto_generated_thumbnails: List[str] = field(default_factory=list)
    seo_optimizations: Dict[str, Any] = field(default_factory=dict)
    accessibility_features: Dict[str, Any] = field(default_factory=dict)
    quality_improvements: Dict[str, Any] = field(default_factory=dict)
    content_suggestions: List[str] = field(default_factory=list)


@dataclass
class ContentProtection:
    """Content protection measures"""
    watermark_applied: bool = False
    fingerprint_registered: bool = False
    copyright_claimed: bool = False
    usage_tracking_enabled: bool = False
    download_protection: bool = False
    piracy_monitoring: bool = False
    content_encryption: bool = False
    access_controls: Dict[str, Any] = field(default_factory=dict)
    protection_level: str = "standard"
    protection_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAssessment:
    """Content quality assessment"""
    overall_score: float = 0.0
    technical_quality: float = 0.0
    content_quality: float = 0.0
    originality_score: float = 0.0
    engagement_potential: float = 0.0
    monetization_potential: float = 0.0
    viral_potential: float = 0.0
    seo_score: float = 0.0
    accessibility_score: float = 0.0
    quality_issues: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ContentAnalysisResult:
    """Comprehensive content analysis result"""
    content_metadata: ContentMetadata
    processing_results: Dict[str, Any] = field(default_factory=dict)
    enhancement: Optional[ContentEnhancement] = None
    protection: Optional[ContentProtection] = None
    quality_assessment: Optional[QualityAssessment] = None
    extracted_features: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    total_cost: float = 0.0


class ContentProcessor:
    """
    🎯 ENTERPRISE CONTENT PROCESSOR
    
    Industrial-grade content processing orchestrator that manages the complete
    content lifecycle from upload to distribution for creators and influencers.
    """
    
    def __init__(
        self,
        db_session,
        redis_client,
        config: Optional[ContentProcessingConfig] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or ContentProcessingConfig()
        self.logger = logging.getLogger(f"{__name__}.ContentProcessor")
        
        # Individual processors
        self.audio_processor = None
        self.video_processor = None
        self.image_processor = None
        self.text_processor = None
        self.document_processor = None
        self.multimedia_processor = None
        
        # Processing pipeline
        self._pipeline_stages = {}
        self._job_queue = asyncio.Queue()
        self._active_jobs = {}
        self._job_handlers = {}
        
        # Content registry
        self._content_registry = {}
        self._processing_stats = {
            "total_processed": 0,
            "successful_jobs": 0,
            "failed_jobs": 0,
            "average_processing_time": 0.0
        }
        
        self._initialized = False
        self._worker_tasks = []
        
        if not AI_ENHANCEMENT_AVAILABLE:
            self.logger.warning("AI enhancement libraries not available")
    
    async def initialize(self) -> bool:
        """Initialize the content processor"""
        try:
            # Initialize individual processors
            self.audio_processor = AudioProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client,
                config=AudioProcessingConfig(**(self.config.audio_config or {}))
            )
            await self.audio_processor.initialize()
            
            self.video_processor = VideoProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client,
                config=VideoProcessingConfig(**(self.config.video_config or {}))
            )
            await self.video_processor.initialize()
            
            self.image_processor = ImageProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client,
                config=ImageProcessingConfig(**(self.config.image_config or {}))
            )
            await self.image_processor.initialize()
            
            self.text_processor = TextProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client,
                config=TextProcessingConfig(**(self.config.text_config or {}))
            )
            await self.text_processor.initialize()
            
            self.document_processor = DocumentProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client,
                config=DocumentProcessingConfig(**(self.config.document_config or {}))
            )
            await self.document_processor.initialize()
            
            self.multimedia_processor = MultimediaProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client,
                config=MultimediaProcessingConfig(**(self.config.multimedia_config or {}))
            )
            await self.multimedia_processor.initialize()
            
            # Setup processing pipeline
            await self._setup_pipeline()
            
            # Start worker tasks
            await self._start_workers()
            
            self._initialized = True
            self.logger.info("✅ Content processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize content processor: {e}")
            return False
    
    async def process_content(
        self,
        content: Union[str, bytes, BinaryIO, Path],
        options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: ProcessingPriority = ProcessingPriority.NORMAL
    ) -> Dict[str, Any]:
        """
        Process content through the complete pipeline
        
        Args:
            content: Content to process
            options: Processing options
            metadata: Additional metadata
            priority: Processing priority
            
        Returns:
            Processing result with job ID for tracking
        """
        start_time = time.time()
        options = options or {}
        metadata = metadata or {}
        
        try:
            if not self._initialized:
                await self.initialize()
            
            # Generate content ID
            content_id = str(uuid.uuid4())
            
            # Detect content type
            content_type = await self._detect_content_type(content, metadata)
            
            # Create content metadata
            content_metadata = await self._create_content_metadata(
                content_id, content_type, content, metadata
            )
            
            # Register content
            self._content_registry[content_id] = {
                "metadata": content_metadata,
                "content": content,
                "options": options,
                "created_at": datetime.now()
            }
            
            # Create processing job
            job = ProcessingJob(
                job_id=str(uuid.uuid4()),
                content_id=content_id,
                stage=ProcessingStage.UPLOAD,
                status=ContentStatus.PENDING,
                priority=priority,
                metadata=metadata
            )
            
            # Add to job queue
            await self._job_queue.put(job)
            self._active_jobs[job.job_id] = job
            
            self.logger.info(f"Content processing job {job.job_id} created for content {content_id}")
            
            return {
                "success": True,
                "job_id": job.job_id,
                "content_id": content_id,
                "status": "queued",
                "estimated_completion": datetime.now() + timedelta(minutes=30),
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            self.logger.error(f"Content processing initiation failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a processing job"""
        try:
            if job_id not in self._active_jobs:
                return {
                    "success": False,
                    "error_message": "Job not found"
                }
            
            job = self._active_jobs[job_id]
            
            return {
                "success": True,
                "job_id": job.job_id,
                "content_id": job.content_id,
                "stage": job.stage.value,
                "status": job.status.value,
                "progress": job.progress,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message,
                "retry_count": job.retry_count,
                "result_data": job.result_data
            }
            
        except Exception as e:
            self.logger.error(f"Job status retrieval failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def get_content_analysis(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive content analysis results"""
        try:
            if content_id not in self._content_registry:
                return {
                    "success": False,
                    "error_message": "Content not found"
                }
            
            # Find completed jobs for this content
            completed_jobs = [
                job for job in self._active_jobs.values()
                if job.content_id == content_id and job.status == ContentStatus.PROCESSED
            ]
            
            if not completed_jobs:
                return {
                    "success": False,
                    "error_message": "Content not yet processed"
                }
            
            # Aggregate results from all processing stages
            analysis_result = await self._aggregate_analysis_results(content_id, completed_jobs)
            
            return {
                "success": True,
                "content_id": content_id,
                "analysis_result": analysis_result.__dict__
            }
            
        except Exception as e:
            self.logger.error(f"Content analysis retrieval failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _detect_content_type(
        self,
        content: Union[str, bytes, BinaryIO, Path],
        metadata: Dict[str, Any]
    ) -> ContentType:
        """Detect content type from input"""
        try:
            # Check metadata first
            if "content_type" in metadata:
                return ContentType(metadata["content_type"])
            
            # Detect from file extension
            if isinstance(content, (str, Path)):
                file_path = Path(content)
                extension = file_path.suffix.lower()
                
                audio_exts = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']
                video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
                image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif']
                text_exts = ['.txt', '.md', '.json', '.csv', '.xml', '.html']
                doc_exts = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt']
                
                if extension in audio_exts:
                    return ContentType.AUDIO
                elif extension in video_exts:
                    return ContentType.VIDEO
                elif extension in image_exts:
                    return ContentType.IMAGE
                elif extension in text_exts:
                    return ContentType.TEXT
                elif extension in doc_exts:
                    return ContentType.DOCUMENT
            
            # Check MIME type if available
            mime_type = metadata.get("mime_type", "")
            if mime_type.startswith("audio/"):
                return ContentType.AUDIO
            elif mime_type.startswith("video/"):
                return ContentType.VIDEO
            elif mime_type.startswith("image/"):
                return ContentType.IMAGE
            elif mime_type.startswith("text/"):
                return ContentType.TEXT
            elif mime_type in ["application/pdf", "application/msword"]:
                return ContentType.DOCUMENT
            
            # Default to unknown
            return ContentType.UNKNOWN
            
        except Exception as e:
            self.logger.error(f"Content type detection failed: {e}")
            return ContentType.UNKNOWN
    
    async def _create_content_metadata(
        self,
        content_id: str,
        content_type: ContentType,
        content: Union[str, bytes, BinaryIO, Path],
        metadata: Dict[str, Any]
    ) -> ContentMetadata:
        """Create comprehensive content metadata"""
        try:
            # Extract basic information
            filename = None
            file_size = None
            
            if isinstance(content, (str, Path)):
                file_path = Path(content)
                filename = file_path.name
                if file_path.exists():
                    file_size = file_path.stat().st_size
            elif isinstance(content, bytes):
                file_size = len(content)
                filename = metadata.get("filename", "uploaded_content")
            else:
                filename = getattr(content, 'name', metadata.get("filename", "uploaded_content"))
                if hasattr(content, 'seek') and hasattr(content, 'tell'):
                    current_pos = content.tell()
                    content.seek(0, 2)  # Seek to end
                    file_size = content.tell()
                    content.seek(current_pos)  # Restore position
            
            return ContentMetadata(
                content_id=content_id,
                content_type=content_type,
                original_filename=filename,
                file_size=file_size,
                mime_type=metadata.get("mime_type"),
                creator_id=metadata.get("creator_id"),
                creator_name=metadata.get("creator_name"),
                title=metadata.get("title"),
                description=metadata.get("description"),
                tags=metadata.get("tags", []),
                language=metadata.get("language"),
                copyright_info=metadata.get("copyright_info"),
                license_type=metadata.get("license_type", "proprietary"),
                content_rating=metadata.get("content_rating", "general"),
                visibility=metadata.get("visibility", self.config.default_visibility),
                is_monetizable=metadata.get("is_monetizable", False),
                uploaded_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Content metadata creation failed: {e}")
            return ContentMetadata(
                content_id=content_id,
                content_type=content_type
            )
    
    async def _setup_pipeline(self):
        """Setup the content processing pipeline"""
        try:
            # Define pipeline stages and their handlers
            self._pipeline_stages = {
                ProcessingStage.UPLOAD: self._handle_upload_stage,
                ProcessingStage.VALIDATION: self._handle_validation_stage,
                ProcessingStage.ANALYSIS: self._handle_analysis_stage,
                ProcessingStage.ENHANCEMENT: self._handle_enhancement_stage,
                ProcessingStage.PROTECTION: self._handle_protection_stage,
                ProcessingStage.OPTIMIZATION: self._handle_optimization_stage,
                ProcessingStage.DISTRIBUTION: self._handle_distribution_stage
            }
            
            self.logger.info(f"Processing pipeline setup with {len(self._pipeline_stages)} stages")
            
        except Exception as e:
            self.logger.error(f"Pipeline setup failed: {e}")
            raise
    
    async def _start_workers(self):
        """Start background worker tasks"""
        try:
            # Start worker tasks for processing jobs
            for i in range(self.config.max_concurrent_jobs):
                worker_task = asyncio.create_task(
                    self._worker_loop(f"worker-{i}")
                )
                self._worker_tasks.append(worker_task)
            
            self.logger.info(f"Started {len(self._worker_tasks)} worker tasks")
            
        except Exception as e:
            self.logger.error(f"Worker startup failed: {e}")
            raise
    
    async def _worker_loop(self, worker_id: str):
        """Worker loop for processing jobs"""
        while True:
            try:
                # Get job from queue
                job = await asyncio.wait_for(self._job_queue.get(), timeout=1.0)
                
                # Process job
                await self._process_job(job, worker_id)
                
            except asyncio.TimeoutError:
                # No jobs available, continue
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def _process_job(self, job: ProcessingJob, worker_id: str):
        """Process a single job"""
        try:
            job.worker_id = worker_id
            job.started_at = datetime.now()
            job.status = ContentStatus.PROCESSING
            
            self.logger.info(f"Worker {worker_id} processing job {job.job_id} stage {job.stage.value}")
            
            # Get stage handler
            handler = self._pipeline_stages.get(job.stage)
            if not handler:
                raise ValueError(f"No handler for stage {job.stage}")
            
            # Execute stage
            result = await handler(job)
            
            if result["success"]:
                # Move to next stage or complete
                next_stage = await self._get_next_stage(job.stage)
                
                if next_stage:
                    # Create next job
                    next_job = ProcessingJob(
                        job_id=str(uuid.uuid4()),
                        content_id=job.content_id,
                        stage=next_stage,
                        status=ContentStatus.PENDING,
                        priority=job.priority,
                        metadata=job.metadata
                    )
                    
                    await self._job_queue.put(next_job)
                    self._active_jobs[next_job.job_id] = next_job
                
                # Mark current job as completed
                job.status = ContentStatus.PROCESSED
                job.completed_at = datetime.now()
                job.result_data = result
                
                self._processing_stats["successful_jobs"] += 1
            else:
                # Handle failure
                await self._handle_job_failure(job, result.get("error_message", "Unknown error"))
                
        except Exception as e:
            self.logger.error(f"Job processing failed: {e}")
            await self._handle_job_failure(job, str(e))
    
    async def _get_next_stage(self, current_stage: ProcessingStage) -> Optional[ProcessingStage]:
        """Get the next processing stage"""
        stage_order = [
            ProcessingStage.UPLOAD,
            ProcessingStage.VALIDATION,
            ProcessingStage.ANALYSIS,
            ProcessingStage.ENHANCEMENT,
            ProcessingStage.PROTECTION,
            ProcessingStage.OPTIMIZATION,
            ProcessingStage.DISTRIBUTION
        ]
        
        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                next_stage = stage_order[current_index + 1]
                
                # Skip stages based on configuration
                if next_stage == ProcessingStage.ENHANCEMENT and not self.config.enable_auto_enhancement:
                    return await self._get_next_stage(next_stage)
                elif next_stage == ProcessingStage.PROTECTION and not self.config.enable_content_protection:
                    return await self._get_next_stage(next_stage)
                elif next_stage == ProcessingStage.OPTIMIZATION and not self.config.enable_seo_optimization:
                    return await self._get_next_stage(next_stage)
                elif next_stage == ProcessingStage.DISTRIBUTION and not self.config.auto_publish:
                    return None
                
                return next_stage
            
            return None
            
        except ValueError:
            return None
    
    async def _handle_job_failure(self, job: ProcessingJob, error_message: str):
        """Handle job failure with retry logic"""
        try:
            job.error_message = error_message
            job.retry_count += 1
            job.failed_at = datetime.now()
            
            if job.retry_count < self.config.retry_attempts:
                # Schedule retry
                job.next_retry_at = datetime.now() + timedelta(seconds=self.config.retry_delay)
                job.status = ContentStatus.PENDING
                
                # Add back to queue
                await asyncio.sleep(self.config.retry_delay)
                await self._job_queue.put(job)
                
                self.logger.info(f"Job {job.job_id} scheduled for retry {job.retry_count}/{self.config.retry_attempts}")
            else:
                # Max retries reached
                job.status = ContentStatus.FAILED
                self._processing_stats["failed_jobs"] += 1
                
                self.logger.error(f"Job {job.job_id} failed after {job.retry_count} retries: {error_message}")
                
        except Exception as e:
            self.logger.error(f"Job failure handling failed: {e}")
    
    # Stage Handlers
    
    async def _handle_upload_stage(self, job: ProcessingJob) -> Dict[str, Any]:
        """Handle upload stage"""
        try:
            content_data = self._content_registry[job.content_id]
            content = content_data["content"]
            metadata = content_data["metadata"]
            
            # Validate file size
            if metadata.file_size and metadata.file_size > self.config.max_file_size:
                return {
                    "success": False,
                    "error_message": f"File size exceeds limit: {metadata.file_size} > {self.config.max_file_size}"
                }
            
            # Validate format
            if metadata.original_filename:
                extension = Path(metadata.original_filename).suffix.lower()[1:]
                if extension not in self.config.supported_formats:
                    return {
                        "success": False,
                        "error_message": f"Unsupported format: {extension}"
                    }
            
            job.progress = 1.0
            
            return {
                "success": True,
                "message": "Upload validated successfully",
                "file_size": metadata.file_size,
                "format": extension if metadata.original_filename else "unknown"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _handle_validation_stage(self, job: ProcessingJob) -> Dict[str, Any]:
        """Handle validation stage"""
        try:
            content_data = self._content_registry[job.content_id]
            content = content_data["content"]
            metadata = content_data["metadata"]
            
            # Content integrity checks
            if isinstance(content, (str, Path)):
                file_path = Path(content)
                if not file_path.exists():
                    return {
                        "success": False,
                        "error_message": "Content file not found"
                    }
            
            # Virus scan (placeholder)
            virus_scan_result = await self._scan_for_viruses(content)
            if not virus_scan_result["clean"]:
                return {
                    "success": False,
                    "error_message": "Content failed security scan"
                }
            
            # Content moderation
            if self.config.enable_content_moderation:
                moderation_result = await self._moderate_content(content, metadata)
                if not moderation_result["approved"]:
                    return {
                        "success": False,
                        "error_message": f"Content moderation failed: {moderation_result['reason']}"
                    }
            
            job.progress = 1.0
            
            return {
                "success": True,
                "message": "Content validation passed",
                "moderation_score": moderation_result.get("score", 1.0) if self.config.enable_content_moderation else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _handle_analysis_stage(self, job: ProcessingJob) -> Dict[str, Any]:
        """Handle analysis stage"""
        try:
            content_data = self._content_registry[job.content_id]
            content = content_data["content"]
            metadata = content_data["metadata"]
            options = content_data["options"]
            
            # Route to appropriate processor
            processor_result = None
            
            if metadata.content_type == ContentType.AUDIO:
                processor_result = await self.audio_processor.process(content, options)
            elif metadata.content_type == ContentType.VIDEO:
                processor_result = await self.video_processor.process(content, options)
            elif metadata.content_type == ContentType.IMAGE:
                processor_result = await self.image_processor.process(content, options)
            elif metadata.content_type == ContentType.TEXT:
                processor_result = await self.text_processor.process(content, options)
            elif metadata.content_type == ContentType.DOCUMENT:
                processor_result = await self.document_processor.process(content, options)
            elif metadata.content_type == ContentType.MULTIMEDIA:
                processor_result = await self.multimedia_processor.process(content, options)
            else:
                return {
                    "success": False,
                    "error_message": f"Unsupported content type: {metadata.content_type}"
                }
            
            if not processor_result["success"]:
                return processor_result
            
            # Extract key information
            analysis_result = processor_result.get("analysis_result", {})
            
            # Update content metadata with analysis results
            await self._update_content_metadata(job.content_id, analysis_result)
            
            job.progress = 1.0
            
            return {
                "success": True,
                "message": "Content analysis completed",
                "analysis_result": analysis_result,
                "processing_time": processor_result.get("processing_time", 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _handle_enhancement_stage(self, job: ProcessingJob) -> Dict[str, Any]:
        """Handle enhancement stage"""
        try:
            if not self.config.enable_auto_enhancement:
                return {
                    "success": True,
                    "message": "Enhancement skipped"
                }
            
            content_data = self._content_registry[job.content_id]
            metadata = content_data["metadata"]
            
            # Get analysis results from previous stage
            analysis_jobs = [
                j for j in self._active_jobs.values()
                if j.content_id == job.content_id and j.stage == ProcessingStage.ANALYSIS
            ]
            
            if not analysis_jobs:
                return {
                    "success": False,
                    "error_message": "No analysis results found"
                }
            
            analysis_result = analysis_jobs[0].result_data.get("analysis_result", {})
            
            # Generate enhancements
            enhancement = ContentEnhancement()
            
            # Auto-generate title
            if self.config.auto_generate_titles and not metadata.title:
                enhancement.auto_generated_title = await self._generate_title(analysis_result)
            
            # Auto-generate description
            if self.config.auto_generate_descriptions and not metadata.description:
                enhancement.auto_generated_description = await self._generate_description(analysis_result)
            
            # Auto-generate tags
            if self.config.auto_generate_tags:
                enhancement.auto_generated_tags = await self._generate_tags(analysis_result)
            
            # Auto-generate summary
            if self.config.auto_generate_summaries:
                enhancement.auto_generated_summary = await self._generate_summary(analysis_result)
            
            # SEO optimizations
            if self.config.enable_seo_optimization:
                enhancement.seo_optimizations = await self._generate_seo_optimizations(analysis_result, metadata)
            
            job.progress = 1.0
            
            return {
                "success": True,
                "message": "Content enhancement completed",
                "enhancement": enhancement.__dict__
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _handle_protection_stage(self, job: ProcessingJob) -> Dict[str, Any]:
        """Handle protection stage"""
        try:
            if not self.config.enable_content_protection:
                return {
                    "success": True,
                    "message": "Protection skipped"
                }
            
            content_data = self._content_registry[job.content_id]
            metadata = content_data["metadata"]
            
            # Apply content protection measures
            protection = ContentProtection()
            
            # Generate and register fingerprint
            protection.fingerprint_registered = await self._register_content_fingerprint(job.content_id)
            
            # Apply watermarking
            protection.watermark_applied = await self._apply_watermark(job.content_id)
            
            # Enable usage tracking
            protection.usage_tracking_enabled = await self._enable_usage_tracking(job.content_id)
            
            # Set protection level
            protection.protection_level = await self._determine_protection_level(metadata)
            
            job.progress = 1.0
            
            return {
                "success": True,
                "message": "Content protection applied",
                "protection": protection.__dict__
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _handle_optimization_stage(self, job: ProcessingJob) -> Dict[str, Any]:
        """Handle optimization stage"""
        try:
            # Placeholder for optimization logic
            # This would include format optimization, compression, etc.
            
            job.progress = 1.0
            
            return {
                "success": True,
                "message": "Content optimization completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _handle_distribution_stage(self, job: ProcessingJob) -> Dict[str, Any]:
        """Handle distribution stage"""
        try:
            # Placeholder for distribution logic
            # This would include publishing to platforms, CDN upload, etc.
            
            job.progress = 1.0
            
            return {
                "success": True,
                "message": "Content distribution completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    # Helper Methods
    
    async def _scan_for_viruses(self, content) -> Dict[str, Any]:
        """Scan content for viruses (placeholder)"""
        # In production, this would integrate with antivirus APIs
        return {"clean": True, "scan_result": "clean"}
    
    async def _moderate_content(self, content, metadata) -> Dict[str, Any]:
        """Moderate content for policy compliance"""
        # Placeholder for content moderation
        return {"approved": True, "score": 1.0, "reason": None}
    
    async def _update_content_metadata(self, content_id: str, analysis_result: Dict[str, Any]):
        """Update content metadata with analysis results"""
        try:
            if content_id in self._content_registry:
                content_data = self._content_registry[content_id]
                metadata = content_data["metadata"]
                
                # Extract useful metadata from analysis
                if "metadata" in analysis_result:
                    analysis_metadata = analysis_result["metadata"]
                    
                    # Update duration if available
                    if "duration" in analysis_metadata:
                        metadata.duration = analysis_metadata["duration"]
                    
                    # Update dimensions if available
                    if "dimensions" in analysis_metadata:
                        metadata.dimensions = analysis_metadata["dimensions"]
                    
                    # Update language if detected
                    if "language" in analysis_metadata and not metadata.language:
                        metadata.language = analysis_metadata["language"]
                
                metadata.processed_at = datetime.now()
                metadata.updated_at = datetime.now()
                
        except Exception as e:
            self.logger.error(f"Metadata update failed: {e}")
    
    async def _generate_title(self, analysis_result: Dict[str, Any]) -> Optional[str]:
        """Generate auto title from analysis results"""
        try:
            # Extract keywords and topics for title generation
            keywords = []
            
            if "features" in analysis_result:
                features = analysis_result["features"]
                if "keywords" in features:
                    keywords.extend(features["keywords"][:3])
                elif "topics" in features:
                    keywords.extend(features["topics"][:3])
            
            if keywords:
                # Simple title generation
                return " ".join(word.title() for word in keywords)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Title generation failed: {e}")
            return None
    
    async def _generate_description(self, analysis_result: Dict[str, Any]) -> Optional[str]:
        """Generate auto description from analysis results"""
        try:
            # Use summary if available
            if "features" in analysis_result:
                features = analysis_result["features"]
                if "summary" in features:
                    return features["summary"]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Description generation failed: {e}")
            return None
    
    async def _generate_tags(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate auto tags from analysis results"""
        try:
            tags = []
            
            if "tags" in analysis_result:
                tags.extend(analysis_result["tags"])
            
            if "features" in analysis_result:
                features = analysis_result["features"]
                if "keywords" in features:
                    tags.extend(features["keywords"][:10])
                if "topics" in features:
                    tags.extend(features["topics"])
            
            return list(set(tags))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Tag generation failed: {e}")
            return []
    
    async def _generate_summary(self, analysis_result: Dict[str, Any]) -> Optional[str]:
        """Generate auto summary from analysis results"""
        try:
            if "features" in analysis_result:
                features = analysis_result["features"]
                if "summary" in features:
                    return features["summary"]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}")
            return None
    
    async def _generate_seo_optimizations(
        self,
        analysis_result: Dict[str, Any],
        metadata: ContentMetadata
    ) -> Dict[str, Any]:
        """Generate SEO optimizations"""
        try:
            optimizations = {}
            
            # Extract SEO score if available
            if "quality_metrics" in analysis_result:
                quality_metrics = analysis_result["quality_metrics"]
                if "seo_score" in quality_metrics:
                    optimizations["current_seo_score"] = quality_metrics["seo_score"]
            
            # Generate SEO suggestions
            optimizations["suggestions"] = [
                "Add relevant keywords to title",
                "Include descriptive alt text for images",
                "Optimize content length for target audience",
                "Use structured data markup"
            ]
            
            return optimizations
            
        except Exception as e:
            self.logger.error(f"SEO optimization generation failed: {e}")
            return {}
    
    async def _register_content_fingerprint(self, content_id: str) -> bool:
        """Register content fingerprint for protection"""
        try:
            # Placeholder for fingerprint registration
            return True
        except Exception as e:
            self.logger.error(f"Fingerprint registration failed: {e}")
            return False
    
    async def _apply_watermark(self, content_id: str) -> bool:
        """Apply watermark to content"""
        try:
            # Placeholder for watermarking
            return True
        except Exception as e:
            self.logger.error(f"Watermarking failed: {e}")
            return False
    
    async def _enable_usage_tracking(self, content_id: str) -> bool:
        """Enable usage tracking for content"""
        try:
            # Placeholder for usage tracking setup
            return True
        except Exception as e:
            self.logger.error(f"Usage tracking setup failed: {e}")
            return False
    
    async def _determine_protection_level(self, metadata: ContentMetadata) -> str:
        """Determine appropriate protection level"""
        try:
            if metadata.is_monetizable:
                return "premium"
            elif metadata.license_type == "proprietary":
                return "standard"
            else:
                return "basic"
        except:
            return "standard"
    
    async def _aggregate_analysis_results(
        self,
        content_id: str,
        completed_jobs: List[ProcessingJob]
    ) -> ContentAnalysisResult:
        """Aggregate results from all processing stages"""
        try:
            content_data = self._content_registry[content_id]
            metadata = content_data["metadata"]
            
            # Initialize result
            result = ContentAnalysisResult(content_metadata=metadata)
            
            # Aggregate results from all jobs
            total_processing_time = 0.0
            
            for job in completed_jobs:
                if job.result_data:
                    result.processing_results[job.stage.value] = job.result_data
                    total_processing_time += job.result_data.get("processing_time", 0)
                    
                    # Extract specific data
                    if job.stage == ProcessingStage.ANALYSIS:
                        result.extracted_features = job.result_data.get("analysis_result", {})
                    elif job.stage == ProcessingStage.ENHANCEMENT:
                        enhancement_data = job.result_data.get("enhancement", {})
                        result.enhancement = ContentEnhancement(**enhancement_data)
                    elif job.stage == ProcessingStage.PROTECTION:
                        protection_data = job.result_data.get("protection", {})
                        result.protection = ContentProtection(**protection_data)
            
            result.processing_time = total_processing_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"Result aggregation failed: {e}")
            return ContentAnalysisResult(content_metadata=metadata)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the content processor"""
        health_status = {
            "status": "healthy" if self._initialized else "not_initialized",
            "active_jobs": len(self._active_jobs),
            "queue_size": self._job_queue.qsize(),
            "worker_count": len(self._worker_tasks),
            "processing_stats": self._processing_stats,
            "config": self.config.__dict__
        }
        
        # Check individual processors
        if self.audio_processor:
            health_status["audio_processor"] = await self.audio_processor.health_check()
        if self.video_processor:
            health_status["video_processor"] = await self.video_processor.health_check()
        if self.image_processor:
            health_status["image_processor"] = await self.image_processor.health_check()
        if self.text_processor:
            health_status["text_processor"] = await self.text_processor.health_check()
        if self.document_processor:
            health_status["document_processor"] = await self.document_processor.health_check()
        if self.multimedia_processor:
            health_status["multimedia_processor"] = await self.multimedia_processor.health_check()
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown the content processor"""
        try:
            # Cancel worker tasks
            for task in self._worker_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
            
            self.logger.info("Content processor shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")


async def create_content_processor(
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> ContentProcessor:
    """
    Factory function to create and initialize a content processor
    
    Args:
        db_session: Database session
        redis_client: Redis client
        config: Configuration dictionary
        
    Returns:
        Initialized ContentProcessor instance
    """
    # Create config from dict if provided
    processor_config = None
    if config:
        processor_config = ContentProcessingConfig(**{
            k: v for k, v in config.items() 
            if k in ContentProcessingConfig.__dataclass_fields__
        })
    
    # Create processor
    processor = ContentProcessor(
        db_session=db_session,
        redis_client=redis_client,
        config=processor_config
    )
    
    # Initialize
    await processor.initialize()
    
    return processor
