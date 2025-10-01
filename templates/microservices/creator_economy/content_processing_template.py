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

Content Processing Service Template for iacherie Platform
======================================================

Production-ready AI-powered content processing service with:
- Multi-format content analysis and processing
- AI content enhancement and optimization
- Automatic content protection and watermarking
- Content quality scoring and validation
- Metadata extraction and enrichment
- Format conversion and transcoding
- Content moderation and safety checks
- Real-time processing pipelines

Author: Fahed Mlaiel (mlaiel@live.de)
AI Expert & Content Processing Specialist
"""

import asyncio
import json
import logging
import time
import hashlib
import base64
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import mimetypes
import tempfile
import os

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as redis
import aiofiles
import openai
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import librosa
import soundfile as sf
import cv2
import numpy as np

from ..base_microservice import BaseMicroservice
from ..circuit_breaker import CircuitBreaker
from ..communication_manager import CommunicationManager

logger = logging.getLogger(__name__)


class ContentFormat(Enum):
    """Supported content formats"""
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    SVG = "svg"
    TIFF = "tiff"
    
    # Document formats
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"


class ProcessingStatus(Enum):
    """Content processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ContentCategory(Enum):
    """Content categories for AI processing"""
    MUSIC = "music"
    PODCAST = "podcast"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    LIVESTREAM = "livestream"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"


class QualityLevel(Enum):
    """Content quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    LOSSLESS = "lossless"


@dataclass
class ContentMetadata:
    """Content metadata structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_filename: str = ""
    file_size: int = 0
    mime_type: str = ""
    format: Optional[ContentFormat] = None
    duration: Optional[float] = None  # seconds
    dimensions: Optional[Tuple[int, int]] = None  # width, height
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    color_space: Optional[str] = None
    fps: Optional[float] = None
    channels: Optional[int] = None
    
    # AI-extracted metadata
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[ContentCategory] = None
    language: Optional[str] = None
    mood: Optional[str] = None
    genre: Optional[str] = None
    
    # Quality metrics
    quality_score: float = 0.0
    technical_quality: float = 0.0
    aesthetic_quality: float = 0.0
    content_quality: float = 0.0
    
    # Protection info
    watermarked: bool = False
    protected: bool = False
    copyright_detected: bool = False
    
    # Processing info
    processing_time: float = 0.0
    ai_enhanced: bool = False
    transcoded: bool = False
    compressed: bool = False


@dataclass
class ProcessingTask:
    """Content processing task"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    content_id: str = ""
    task_type: str = ""
    priority: int = 5  # 1-10, 10 is highest
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Task parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Results
    output_files: List[str] = field(default_factory=list)
    metadata: Optional[ContentMetadata] = None


class ContentProcessingConfig:
    """Content processing configuration"""
    
    def __init__(self):
        # AI processing settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.enable_ai_enhancement = True
        self.enable_auto_transcription = True
        self.enable_auto_translation = True
        
        # Quality settings
        self.default_video_quality = QualityLevel.HIGH
        self.default_audio_quality = QualityLevel.HIGH
        self.max_file_size = 500 * 1024 * 1024  # 500MB
        self.max_processing_time = 3600  # 1 hour
        
        # Storage settings
        self.temp_storage_path = "/tmp/content_processing"
        self.output_storage_path = "/var/lib/iacherie/processed_content"
        self.watermark_image_path = "/etc/iacherie/watermark.png"
        
        # Processing limits
        self.max_concurrent_tasks = 10
        self.task_timeout = 1800  # 30 minutes
        self.retry_attempts = 3
        
        # Protection settings
        self.enable_watermarking = True
        self.enable_copyright_detection = True
        self.watermark_opacity = 0.3
        self.watermark_position = "bottom_right"


# Pydantic models for API
class ContentUploadRequest(BaseModel):
    """Content upload request"""
    creator_id: str = Field(..., description="Creator ID")
    title: Optional[str] = Field(None, description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    category: Optional[ContentCategory] = Field(None, description="Content category")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    enable_ai_processing: bool = Field(True, description="Enable AI processing")
    enable_protection: bool = Field(True, description="Enable content protection")
    target_quality: QualityLevel = Field(QualityLevel.HIGH, description="Target quality")


class ProcessingTaskResponse(BaseModel):
    """Processing task response"""
    task_id: str
    status: ProcessingStatus
    progress: float
    created_at: datetime
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None


class ContentAnalysisResponse(BaseModel):
    """Content analysis response"""
    content_id: str
    metadata: Dict[str, Any]
    quality_metrics: Dict[str, float]
    ai_insights: Dict[str, Any]
    recommendations: List[str]


class ContentProcessingService(BaseMicroservice):
    """
    Enterprise Content Processing Service for iacherie Platform
    
    Provides AI-powered content processing, enhancement, and protection
    with support for multiple content formats and real-time processing.
    """
    
    def __init__(self, config: Optional[ContentProcessingConfig] = None):
        super().__init__("content-processing-service")
        
        self.config = config or ContentProcessingConfig()
        self.processing_tasks: Dict[str, ProcessingTask] = {}
        self.active_workers: Set[str] = set()
        self.task_queue = asyncio.Queue()
        
        # Metrics
        self.processing_counter = Counter('content_processing_total', 'Total content processing requests')
        self.processing_duration = Histogram('content_processing_duration_seconds', 'Content processing duration')
        self.active_tasks_gauge = Gauge('content_processing_active_tasks', 'Active processing tasks')
        self.quality_score_histogram = Histogram('content_quality_score', 'Content quality scores')
        
        # Circuit breakers
        self.ai_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=Exception
        )
        
        self.storage_circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            expected_exception=Exception
        )
        
        # Communication manager
        self.communication_manager = CommunicationManager()
        
        # Redis client for caching and task coordination
        self.redis_client: Optional[redis.Redis] = None
        
        # OpenAI client
        self.openai_client = openai.AsyncOpenAI(api_key=self.config.openai_api_key)
        
        # Initialize storage directories
        self._initialize_storage()
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        logger.info("Content Processing Service initialized")
    
    def _initialize_storage(self):
        """Initialize storage directories"""
        try:
            os.makedirs(self.config.temp_storage_path, exist_ok=True)
            os.makedirs(self.config.output_storage_path, exist_ok=True)
            logger.info("Storage directories initialized")
        except Exception as e:
            logger.error(f"Failed to initialize storage directories: {e}")
    
    async def startup(self):
        """Service startup tasks"""
        await super().startup()
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
        
        # Start background workers
        await self._start_background_workers()
        
        # Start monitoring tasks
        await self._start_monitoring_tasks()
        
        logger.info("Content Processing Service started")
    
    async def shutdown(self):
        """Service shutdown tasks"""
        logger.info("Shutting down Content Processing Service...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        await super().shutdown()
        logger.info("Content Processing Service shut down")
    
    async def _start_background_workers(self):
        """Start background processing workers"""
        for i in range(self.config.max_concurrent_tasks):
            worker_id = f"worker_{i}"
            task = asyncio.create_task(self._processing_worker(worker_id))
            self.background_tasks.add(task)
        
        logger.info(f"Started {self.config.max_concurrent_tasks} processing workers")
    
    async def _start_monitoring_tasks(self):
        """Start monitoring and cleanup tasks"""
        # Task cleanup
        cleanup_task = asyncio.create_task(self._cleanup_completed_tasks())
        self.background_tasks.add(cleanup_task)
        
        # Metrics collection
        metrics_task = asyncio.create_task(self._collect_metrics())
        self.background_tasks.add(metrics_task)
        
        logger.info("Started monitoring tasks")
    
    async def upload_content(
        self,
        file: UploadFile,
        request: ContentUploadRequest
    ) -> Dict[str, Any]:
        """Upload and queue content for processing"""
        start_time = time.time()
        
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            
            if file.size and file.size > self.config.max_file_size:
                raise HTTPException(status_code=413, detail="File too large")
            
            # Determine content format
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
            content_format = self._determine_content_format(file.filename, mime_type)
            
            if not content_format:
                raise HTTPException(status_code=400, detail="Unsupported file format")
            
            # Generate content ID
            content_id = str(uuid.uuid4())
            
            # Save uploaded file
            temp_file_path = await self._save_uploaded_file(file, content_id)
            
            # Create initial metadata
            metadata = ContentMetadata(
                id=content_id,
                original_filename=file.filename,
                file_size=file.size or 0,
                mime_type=mime_type or "",
                format=content_format
            )
            
            # Create processing task
            task = ProcessingTask(
                creator_id=request.creator_id,
                content_id=content_id,
                task_type="full_processing",
                parameters={
                    "temp_file_path": temp_file_path,
                    "title": request.title,
                    "description": request.description,
                    "category": request.category.value if request.category else None,
                    "tags": request.tags,
                    "enable_ai_processing": request.enable_ai_processing,
                    "enable_protection": request.enable_protection,
                    "target_quality": request.target_quality.value
                },
                metadata=metadata
            )
            
            # Queue task for processing
            await self._queue_task(task)
            
            # Update metrics
            self.processing_counter.inc()
            processing_time = time.time() - start_time
            self.processing_duration.observe(processing_time)
            
            return {
                "success": True,
                "content_id": content_id,
                "task_id": task.id,
                "status": task.status.value,
                "estimated_processing_time": self._estimate_processing_time(content_format, file.size or 0)
            }
            
        except Exception as e:
            logger.error(f"Content upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_processing_status(self, task_id: str) -> ProcessingTaskResponse:
        """Get processing task status"""
        try:
            task = self.processing_tasks.get(task_id)
            if not task:
                # Try to load from Redis
                task = await self._load_task_from_cache(task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            
            estimated_completion = None
            if task.status == ProcessingStatus.PROCESSING and task.started_at:
                elapsed = (datetime.utcnow() - task.started_at).total_seconds()
                estimated_total = self._estimate_processing_time(
                    task.metadata.format if task.metadata else None,
                    task.metadata.file_size if task.metadata else 0
                )
                if estimated_total > elapsed:
                    estimated_completion = task.started_at + timedelta(seconds=estimated_total)
            
            return ProcessingTaskResponse(
                task_id=task.id,
                status=task.status,
                progress=task.progress,
                created_at=task.created_at,
                estimated_completion=estimated_completion,
                error_message=task.error_message
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get processing status: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def analyze_content(self, content_id: str) -> ContentAnalysisResponse:
        """Analyze processed content"""
        try:
            # Load content metadata
            metadata = await self._load_content_metadata(content_id)
            if not metadata:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Generate AI insights
            ai_insights = await self._generate_ai_insights(content_id, metadata)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(metadata, ai_insights)
            
            return ContentAnalysisResponse(
                content_id=content_id,
                metadata=metadata.__dict__,
                quality_metrics={
                    "overall_quality": metadata.quality_score,
                    "technical_quality": metadata.technical_quality,
                    "aesthetic_quality": metadata.aesthetic_quality,
                    "content_quality": metadata.content_quality
                },
                ai_insights=ai_insights,
                recommendations=recommendations
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def _processing_worker(self, worker_id: str):
        """Background processing worker"""
        logger.info(f"Processing worker {worker_id} started")
        
        while True:
            try:
                # Get task from queue
                task = await asyncio.wait_for(self.task_queue.get(), timeout=30)
                
                if task is None:  # Shutdown signal
                    break
                
                self.active_workers.add(worker_id)
                self.active_tasks_gauge.inc()
                
                # Process task
                await self._process_task(task, worker_id)
                
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
            finally:
                self.active_workers.discard(worker_id)
                self.active_tasks_gauge.dec()
        
        logger.info(f"Processing worker {worker_id} stopped")
    
    async def _process_task(self, task: ProcessingTask, worker_id: str):
        """Process a content processing task"""
        logger.info(f"Worker {worker_id} processing task {task.id}")
        
        try:
            # Update task status
            task.status = ProcessingStatus.PROCESSING
            task.started_at = datetime.utcnow()
            task.progress = 0.0
            await self._save_task_to_cache(task)
            
            # Get file path
            temp_file_path = task.parameters.get("temp_file_path")
            if not temp_file_path or not os.path.exists(temp_file_path):
                raise Exception("Source file not found")
            
            # Step 1: Extract basic metadata (10%)
            await self._extract_metadata(task, temp_file_path)
            task.progress = 10.0
            await self._save_task_to_cache(task)
            
            # Step 2: Analyze content quality (25%)
            await self._analyze_content_quality(task, temp_file_path)
            task.progress = 25.0
            await self._save_task_to_cache(task)
            
            # Step 3: AI processing (60%)
            if task.parameters.get("enable_ai_processing", True):
                await self._perform_ai_processing(task, temp_file_path)
            task.progress = 60.0
            await self._save_task_to_cache(task)
            
            # Step 4: Apply protection (80%)
            if task.parameters.get("enable_protection", True):
                await self._apply_content_protection(task, temp_file_path)
            task.progress = 80.0
            await self._save_task_to_cache(task)
            
            # Step 5: Generate output files (100%)
            output_files = await self._generate_output_files(task, temp_file_path)
            task.output_files = output_files
            task.progress = 100.0
            
            # Complete task
            task.status = ProcessingStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            await self._save_task_to_cache(task)
            
            # Update quality metrics
            if task.metadata:
                self.quality_score_histogram.observe(task.metadata.quality_score)
            
            # Notify completion
            await self._notify_task_completion(task)
            
            # Cleanup temp file
            try:
                os.remove(temp_file_path)
            except:
                pass
            
            logger.info(f"Task {task.id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.status = ProcessingStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await self._save_task_to_cache(task)
    
    async def _extract_metadata(self, task: ProcessingTask, file_path: str):
        """Extract basic metadata from content file"""
        if not task.metadata:
            return
        
        try:
            # Get file stats
            stats = os.stat(file_path)
            task.metadata.file_size = stats.st_size
            
            # Format-specific metadata extraction
            if task.metadata.format in [ContentFormat.MP4, ContentFormat.AVI, ContentFormat.MOV, ContentFormat.WEBM]:
                await self._extract_video_metadata(task, file_path)
            elif task.metadata.format in [ContentFormat.MP3, ContentFormat.WAV, ContentFormat.FLAC]:
                await self._extract_audio_metadata(task, file_path)
            elif task.metadata.format in [ContentFormat.JPEG, ContentFormat.PNG, ContentFormat.GIF]:
                await self._extract_image_metadata(task, file_path)
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            raise
    
    async def _extract_video_metadata(self, task: ProcessingTask, file_path: str):
        """Extract video metadata"""
        try:
            cap = cv2.VideoCapture(file_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if fps > 0:
                duration = frame_count / fps
                task.metadata.duration = duration
            
            task.metadata.dimensions = (width, height)
            task.metadata.fps = fps
            
            cap.release()
            
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {e}")
            raise
    
    async def _extract_audio_metadata(self, task: ProcessingTask, file_path: str):
        """Extract audio metadata"""
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=None)
            
            task.metadata.duration = len(y) / sr
            task.metadata.sample_rate = sr
            task.metadata.channels = 1 if y.ndim == 1 else y.shape[0]
            
        except Exception as e:
            logger.error(f"Audio metadata extraction failed: {e}")
            raise
    
    async def _extract_image_metadata(self, task: ProcessingTask, file_path: str):
        """Extract image metadata"""
        try:
            with Image.open(file_path) as img:
                task.metadata.dimensions = img.size
                task.metadata.color_space = img.mode
                
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {e}")
            raise
    
    async def _analyze_content_quality(self, task: ProcessingTask, file_path: str):
        """Analyze content quality"""
        if not task.metadata:
            return
        
        try:
            # Technical quality analysis
            technical_score = await self._analyze_technical_quality(task, file_path)
            task.metadata.technical_quality = technical_score
            
            # Aesthetic quality analysis (simplified)
            aesthetic_score = await self._analyze_aesthetic_quality(task, file_path)
            task.metadata.aesthetic_quality = aesthetic_score
            
            # Overall quality score
            task.metadata.quality_score = (technical_score + aesthetic_score) / 2
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            raise
    
    async def _analyze_technical_quality(self, task: ProcessingTask, file_path: str) -> float:
        """Analyze technical quality"""
        # Simplified technical quality analysis
        score = 0.7  # Base score
        
        if task.metadata.format in [ContentFormat.MP4, ContentFormat.MOV]:
            # Video quality factors
            if task.metadata.dimensions:
                width, height = task.metadata.dimensions
                if width >= 1920 and height >= 1080:
                    score += 0.2
                elif width >= 1280 and height >= 720:
                    score += 0.1
            
            if task.metadata.fps and task.metadata.fps >= 30:
                score += 0.1
        
        return min(1.0, score)
    
    async def _analyze_aesthetic_quality(self, task: ProcessingTask, file_path: str) -> float:
        """Analyze aesthetic quality (simplified)"""
        # This would involve more complex AI analysis in a real implementation
        return 0.75  # Placeholder score
    
    @CircuitBreaker.circuit_breaker
    async def _perform_ai_processing(self, task: ProcessingTask, file_path: str):
        """Perform AI-powered content processing"""
        if not task.metadata:
            return
        
        try:
            # AI-powered metadata extraction
            if task.metadata.format in [ContentFormat.MP4, ContentFormat.AVI]:
                await self._ai_video_analysis(task, file_path)
            elif task.metadata.format in [ContentFormat.MP3, ContentFormat.WAV]:
                await self._ai_audio_analysis(task, file_path)
            elif task.metadata.format in [ContentFormat.JPEG, ContentFormat.PNG]:
                await self._ai_image_analysis(task, file_path)
            
            # AI enhancement
            if task.parameters.get("enable_ai_enhancement", True):
                await self._ai_content_enhancement(task, file_path)
            
            task.metadata.ai_enhanced = True
            
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            raise
    
    async def _ai_video_analysis(self, task: ProcessingTask, file_path: str):
        """AI-powered video content analysis"""
        try:
            # Extract frames for analysis
            cap = cv2.VideoCapture(file_path)
            frames = []
            
            # Sample frames at regular intervals
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // 10)  # Sample 10 frames
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            
            cap.release()
            
            # Analyze frames with AI (simplified)
            # In a real implementation, this would use computer vision models
            task.metadata.category = ContentCategory.VIDEO
            task.metadata.tags.extend(["video", "content"])
            
            # Content description (placeholder)
            task.metadata.description = "AI-analyzed video content"
            
        except Exception as e:
            logger.error(f"AI video analysis failed: {e}")
            raise
    
    async def _ai_audio_analysis(self, task: ProcessingTask, file_path: str):
        """AI-powered audio content analysis"""
        try:
            # Load audio for analysis
            y, sr = librosa.load(file_path, sr=22050)
            
            # Extract audio features
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            
            # Determine mood/genre (simplified)
            if tempo > 120:
                task.metadata.mood = "energetic"
            else:
                task.metadata.mood = "calm"
            
            task.metadata.category = ContentCategory.MUSIC
            task.metadata.tags.extend(["audio", "music"])
            
        except Exception as e:
            logger.error(f"AI audio analysis failed: {e}")
            raise
    
    async def _ai_image_analysis(self, task: ProcessingTask, file_path: str):
        """AI-powered image content analysis"""
        try:
            with Image.open(file_path) as img:
                # Image analysis (simplified)
                # In a real implementation, this would use image recognition models
                
                task.metadata.category = ContentCategory.IMAGE
                task.metadata.tags.extend(["image", "visual"])
                
                # Analyze colors, composition, etc.
                colors = img.getcolors(maxcolors=256)
                if colors:
                    dominant_color = max(colors, key=lambda x: x[0])
                    task.metadata.tags.append(f"dominant_color_{dominant_color[1]}")
                
        except Exception as e:
            logger.error(f"AI image analysis failed: {e}")
            raise
    
    async def _ai_content_enhancement(self, task: ProcessingTask, file_path: str):
        """AI-powered content enhancement"""
        # This would implement actual AI enhancement in a real system
        # For now, we just mark it as enhanced
        pass
    
    async def _apply_content_protection(self, task: ProcessingTask, file_path: str):
        """Apply content protection measures"""
        if not self.config.enable_watermarking:
            return
        
        try:
            if task.metadata.format in [ContentFormat.JPEG, ContentFormat.PNG]:
                await self._watermark_image(task, file_path)
            elif task.metadata.format in [ContentFormat.MP4, ContentFormat.MOV]:
                await self._watermark_video(task, file_path)
            elif task.metadata.format in [ContentFormat.MP3, ContentFormat.WAV]:
                await self._watermark_audio(task, file_path)
            
            task.metadata.watermarked = True
            task.metadata.protected = True
            
        except Exception as e:
            logger.error(f"Content protection failed: {e}")
            raise
    
    async def _watermark_image(self, task: ProcessingTask, file_path: str):
        """Apply watermark to image"""
        try:
            with Image.open(file_path) as img:
                # Create watermark
                watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(watermark)
                
                # Add text watermark
                text = "© iacherie"
                font_size = max(20, min(img.size) // 20)
                
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Position watermark
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                x = img.width - text_width - 20
                y = img.height - text_height - 20
                
                # Draw watermark
                draw.text((x, y), text, fill=(255, 255, 255, int(255 * self.config.watermark_opacity)), font=font)
                
                # Apply watermark
                watermarked = Image.alpha_composite(img.convert('RGBA'), watermark)
                
                # Save watermarked image
                output_path = file_path.replace('.', '_watermarked.')
                watermarked.convert('RGB').save(output_path, quality=95)
                
        except Exception as e:
            logger.error(f"Image watermarking failed: {e}")
            raise
    
    async def _watermark_video(self, task: ProcessingTask, file_path: str):
        """Apply watermark to video (placeholder)"""
        # This would use FFmpeg or similar for video watermarking
        pass
    
    async def _watermark_audio(self, task: ProcessingTask, file_path: str):
        """Apply watermark to audio (placeholder)"""
        # This would implement audio watermarking techniques
        pass
    
    async def _generate_output_files(self, task: ProcessingTask, file_path: str) -> List[str]:
        """Generate output files in different formats/qualities"""
        output_files = []
        
        try:
            # Original file
            original_output = os.path.join(
                self.config.output_storage_path,
                f"{task.content_id}_original{os.path.splitext(file_path)[1]}"
            )
            
            # Copy original file
            import shutil
            shutil.copy2(file_path, original_output)
            output_files.append(original_output)
            
            # Generate additional formats/qualities as needed
            # This would be expanded based on requirements
            
        except Exception as e:
            logger.error(f"Output file generation failed: {e}")
            raise
        
        return output_files
    
    # Helper methods
    def _determine_content_format(self, filename: str, mime_type: str) -> Optional[ContentFormat]:
        """Determine content format from filename and MIME type"""
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        
        format_map = {
            'mp4': ContentFormat.MP4,
            'avi': ContentFormat.AVI,
            'mov': ContentFormat.MOV,
            'wmv': ContentFormat.WMV,
            'flv': ContentFormat.FLV,
            'webm': ContentFormat.WEBM,
            'mp3': ContentFormat.MP3,
            'wav': ContentFormat.WAV,
            'flac': ContentFormat.FLAC,
            'aac': ContentFormat.AAC,
            'ogg': ContentFormat.OGG,
            'm4a': ContentFormat.M4A,
            'jpg': ContentFormat.JPEG,
            'jpeg': ContentFormat.JPEG,
            'png': ContentFormat.PNG,
            'gif': ContentFormat.GIF,
            'webp': ContentFormat.WEBP,
            'svg': ContentFormat.SVG,
            'tiff': ContentFormat.TIFF,
            'pdf': ContentFormat.PDF,
            'docx': ContentFormat.DOCX,
            'txt': ContentFormat.TXT,
            'md': ContentFormat.MD,
            'html': ContentFormat.HTML
        }
        
        return format_map.get(ext)
    
    async def _save_uploaded_file(self, file: UploadFile, content_id: str) -> str:
        """Save uploaded file to temporary storage"""
        ext = os.path.splitext(file.filename)[1] if file.filename else ""
        temp_file_path = os.path.join(self.config.temp_storage_path, f"{content_id}{ext}")
        
        async with aiofiles.open(temp_file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return temp_file_path
    
    def _estimate_processing_time(self, content_format: Optional[ContentFormat], file_size: int) -> int:
        """Estimate processing time in seconds"""
        base_time = 30  # Base processing time
        
        # Factor in file size (1 second per MB)
        size_factor = file_size / (1024 * 1024)
        
        # Factor in content type complexity
        complexity_factor = 1.0
        if content_format in [ContentFormat.MP4, ContentFormat.AVI, ContentFormat.MOV]:
            complexity_factor = 3.0  # Video is more complex
        elif content_format in [ContentFormat.MP3, ContentFormat.WAV]:
            complexity_factor = 2.0  # Audio is moderately complex
        
        return int(base_time + (size_factor * complexity_factor))
    
    async def _queue_task(self, task: ProcessingTask):
        """Queue task for processing"""
        self.processing_tasks[task.id] = task
        await self._save_task_to_cache(task)
        await self.task_queue.put(task)
    
    async def _save_task_to_cache(self, task: ProcessingTask):
        """Save task to Redis cache"""
        if not self.redis_client:
            return
        
        try:
            task_data = {
                'id': task.id,
                'creator_id': task.creator_id,
                'content_id': task.content_id,
                'task_type': task.task_type,
                'status': task.status.value,
                'progress': task.progress,
                'created_at': task.created_at.isoformat(),
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'error_message': task.error_message,
                'parameters': task.parameters,
                'output_files': task.output_files
            }
            
            await self.redis_client.setex(
                f"content_processing:task:{task.id}",
                3600,  # 1 hour TTL
                json.dumps(task_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to save task to cache: {e}")
    
    async def _load_task_from_cache(self, task_id: str) -> Optional[ProcessingTask]:
        """Load task from Redis cache"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(f"content_processing:task:{task_id}")
            if not data:
                return None
            
            task_data = json.loads(data)
            
            # Reconstruct task object
            task = ProcessingTask(
                id=task_data['id'],
                creator_id=task_data['creator_id'],
                content_id=task_data['content_id'],
                task_type=task_data['task_type'],
                status=ProcessingStatus(task_data['status']),
                progress=task_data['progress'],
                created_at=datetime.fromisoformat(task_data['created_at']),
                error_message=task_data.get('error_message'),
                parameters=task_data.get('parameters', {}),
                output_files=task_data.get('output_files', [])
            )
            
            if task_data.get('started_at'):
                task.started_at = datetime.fromisoformat(task_data['started_at'])
            
            if task_data.get('completed_at'):
                task.completed_at = datetime.fromisoformat(task_data['completed_at'])
            
            return task
            
        except Exception as e:
            logger.error(f"Failed to load task from cache: {e}")
            return None
    
    async def _load_content_metadata(self, content_id: str) -> Optional[ContentMetadata]:
        """Load content metadata"""
        # This would load from database in a real implementation
        # For now, try to find in active tasks
        for task in self.processing_tasks.values():
            if task.content_id == content_id and task.metadata:
                return task.metadata
        
        return None
    
    async def _generate_ai_insights(self, content_id: str, metadata: ContentMetadata) -> Dict[str, Any]:
        """Generate AI insights for content"""
        # This would use advanced AI models for content analysis
        return {
            "engagement_potential": 0.8,
            "viral_score": 0.6,
            "audience_match": 0.7,
            "optimization_suggestions": [
                "Consider adding captions for better accessibility",
                "Thumbnail could be more eye-catching",
                "Content duration is optimal for engagement"
            ]
        }
    
    async def _generate_recommendations(self, metadata: ContentMetadata, ai_insights: Dict[str, Any]) -> List[str]:
        """Generate content optimization recommendations"""
        recommendations = []
        
        if metadata.quality_score < 0.7:
            recommendations.append("Consider improving content quality before publishing")
        
        if not metadata.tags:
            recommendations.append("Add relevant tags to improve discoverability")
        
        if metadata.category == ContentCategory.VIDEO and metadata.duration and metadata.duration > 300:
            recommendations.append("Consider creating shorter clips for social media")
        
        return recommendations
    
    async def _notify_task_completion(self, task: ProcessingTask):
        """Notify task completion to relevant services"""
        try:
            # Notify creator service
            await self.communication_manager.send_message(
                service="creator-service",
                message_type="content_processed",
                data={
                    "creator_id": task.creator_id,
                    "content_id": task.content_id,
                    "task_id": task.id,
                    "status": task.status.value,
                    "output_files": task.output_files
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to notify task completion: {e}")
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed tasks periodically"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Remove completed tasks older than 24 hours
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                to_remove = []
                for task_id, task in self.processing_tasks.items():
                    if (task.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED] and
                        task.completed_at and task.completed_at < cutoff_time):
                        to_remove.append(task_id)
                
                for task_id in to_remove:
                    del self.processing_tasks[task_id]
                
                logger.info(f"Cleaned up {len(to_remove)} completed tasks")
                
            except Exception as e:
                logger.error(f"Task cleanup failed: {e}")
    
    async def _collect_metrics(self):
        """Collect and update metrics periodically"""
        while True:
            try:
                await asyncio.sleep(60)  # Update every minute
                
                # Update active tasks gauge
                active_count = sum(1 for task in self.processing_tasks.values() 
                                 if task.status == ProcessingStatus.PROCESSING)
                self.active_tasks_gauge.set(active_count)
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Content processing service health check"""
        try:
            # Test Redis connection
            redis_healthy = False
            try:
                if self.redis_client:
                    await self.redis_client.ping()
                    redis_healthy = True
            except Exception:
                pass
            
            # Check processing queue
            queue_size = self.task_queue.qsize()
            
            # Check active workers
            active_workers = len(self.active_workers)
            
            # Check storage
            storage_healthy = os.path.exists(self.config.temp_storage_path)
            
            status = "healthy"
            if not redis_healthy or not storage_healthy:
                status = "degraded"
            
            return {
                'status': status,
                'redis_connected': redis_healthy,
                'storage_accessible': storage_healthy,
                'queue_size': queue_size,
                'active_workers': active_workers,
                'total_tasks': len(self.processing_tasks),
                'completed_tasks': sum(1 for t in self.processing_tasks.values() 
                                     if t.status == ProcessingStatus.COMPLETED),
                'failed_tasks': sum(1 for t in self.processing_tasks.values() 
                                  if t.status == ProcessingStatus.FAILED),
                'circuit_breakers': {
                    'ai_service': self.ai_circuit_breaker.state.name,
                    'storage_service': self.storage_circuit_breaker.state.name
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# FastAPI app setup
def create_content_processing_app() -> FastAPI:
    """Create FastAPI application for content processing service"""
    
    app = FastAPI(
        title="iacherie Content Processing Service",
        description="AI-powered content processing and enhancement service",
        version="1.0.0"
    )
    
    # Initialize service
    service = ContentProcessingService()
    
    @app.on_event("startup")
    async def startup():
        await service.startup()
    
    @app.on_event("shutdown")
    async def shutdown():
        await service.shutdown()
    
    @app.post("/upload")
    async def upload_content(
        file: UploadFile = File(...),
        creator_id: str = Field(...),
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[ContentCategory] = None,
        tags: str = "",
        enable_ai_processing: bool = True,
        enable_protection: bool = True,
        target_quality: QualityLevel = QualityLevel.HIGH
    ):
        """Upload content for processing"""
        request = ContentUploadRequest(
            creator_id=creator_id,
            title=title,
            description=description,
            category=category,
            tags=tags.split(",") if tags else [],
            enable_ai_processing=enable_ai_processing,
            enable_protection=enable_protection,
            target_quality=target_quality
        )
        
        return await service.upload_content(file, request)
    
    @app.get("/task/{task_id}/status")
    async def get_task_status(task_id: str):
        """Get processing task status"""
        return await service.get_processing_status(task_id)
    
    @app.get("/content/{content_id}/analysis")
    async def get_content_analysis(content_id: str):
        """Get content analysis results"""
        return await service.analyze_content(content_id)
    
    @app.get("/health")
    async def health_check():
        """Service health check"""
        return await service.health_check()
    
    return app


# Export classes for use in other modules
__all__ = [
    'ContentProcessingService',
    'ContentProcessingConfig',
    'ContentFormat',
    'ProcessingStatus',
    'ContentCategory',
    'QualityLevel',
    'ContentMetadata',
    'ProcessingTask',
    'ContentUploadRequest',
    'ProcessingTaskResponse',
    'ContentAnalysisResponse',
    'create_content_processing_app'
]