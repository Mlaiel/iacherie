"""
Content Processor - Advanced Multi-Format Content Processing Engine

Handles intelligent content processing, analysis, optimization, and transformation
for multiple content types including audio, video, image, and text content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import mimetypes
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import aiofiles
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import librosa
import torch
from transformers import pipeline, AutoTokenizer, AutoModel
from fastapi import HTTPException, UploadFile

from ...core.config import settings
from ...core.logging import get_logger
from ...services.ai.content_analysis import ContentAnalysisService
from ...services.storage.file_storage import FileStorageService
from ...utils.image_utils import ImageProcessor
from ...utils.audio_utils import AudioProcessor
from ...utils.video_utils import VideoProcessor
from ...utils.text_utils import TextProcessor

logger = get_logger(__name__)

class ContentType(Enum):
    """Content type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    UNKNOWN = "unknown"

class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    OPTIMIZED = "optimized"

@dataclass
class ContentMetadata:
    """Content metadata structure"""
    file_name: str
    file_size: int
    content_type: ContentType
    mime_type: str
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    encoding: Optional[str] = None
    language: Optional[str] = None
    quality_score: Optional[float] = None
    tags: List[str] = None
    extracted_text: Optional[str] = None

@dataclass
class ProcessingResult:
    """Content processing result"""
    content_id: str
    original_path: str
    processed_paths: Dict[str, str]
    metadata: ContentMetadata
    analysis_results: Dict[str, Any]
    optimization_results: Dict[str, Any]
    status: ProcessingStatus
    processing_time: float
    created_at: datetime

class ContentProcessor:
    """
    Advanced multi-format content processing engine
    
    Features:
    - Intelligent content type detection
    - Multi-format content analysis
    - Quality assessment and optimization
    - SEO metadata extraction
    - Platform-specific optimization
    - AI-powered content enhancement
    """
    
    def __init__(self):
        self.content_analysis = ContentAnalysisService()
        self.file_storage = FileStorageService()
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.text_processor = TextProcessor()
        
        # AI models for content analysis
        self.text_analyzer = None
        self.image_classifier = None
        self.audio_classifier = None
        
        # Supported formats
        self.supported_formats = {
            ContentType.AUDIO: ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            ContentType.VIDEO: ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            ContentType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            ContentType.TEXT: ['.txt', '.md', '.rtf', '.doc', '.docx'],
            ContentType.DOCUMENT: ['.pdf', '.epub', '.mobi']
        }
    
    async def initialize(self) -> bool:
        """
        Initialize content processor and AI models
        
        Returns:
            bool: Initialization success status
        """
        try:
            logger.info("Initializing Content Processor...")
            
            # Initialize AI models
            await self._initialize_ai_models()
            
            # Initialize processors
            await self.image_processor.initialize()
            await self.audio_processor.initialize()
            await self.video_processor.initialize()
            await self.text_processor.initialize()
            
            logger.info("Content Processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Content Processor initialization failed: {e}")
            return False
    
    async def process_uploaded_content(
        self,
        file: UploadFile,
        user_id: int,
        processing_options: Dict[str, Any] = None
    ) -> ProcessingResult:
        """
        Process uploaded content file
        
        Args:
            file: Uploaded file object
            user_id: User ID for file organization
            processing_options: Custom processing options
            
        Returns:
            ProcessingResult with processing information
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate file
            await self._validate_uploaded_file(file)
            
            # Detect content type
            content_type = await self._detect_content_type(file)
            
            # Generate content ID
            content_id = f"content_{user_id}_{int(start_time.timestamp())}"
            
            # Save original file
            original_path = await self._save_original_file(file, content_id, user_id)
            
            # Extract basic metadata
            metadata = await self._extract_basic_metadata(original_path, content_type, file)
            
            # Process content based on type
            processed_paths = await self._process_by_type(
                original_path, content_type, processing_options or {}
            )
            
            # Perform AI analysis
            analysis_results = await self._perform_ai_analysis(
                original_path, content_type, metadata
            )
            
            # Optimize for different platforms
            optimization_results = await self._optimize_for_platforms(
                original_path, processed_paths, content_type
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create processing result
            result = ProcessingResult(
                content_id=content_id,
                original_path=original_path,
                processed_paths=processed_paths,
                metadata=metadata,
                analysis_results=analysis_results,
                optimization_results=optimization_results,
                status=ProcessingStatus.COMPLETED,
                processing_time=processing_time,
                created_at=start_time
            )
            
            logger.info(f"Content processed successfully: {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Content processing failed: {e}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    async def reprocess_content(
        self,
        content_id: str,
        original_path: str,
        new_options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Reprocess existing content with new options
        
        Args:
            content_id: Existing content ID
            original_path: Path to original file
            new_options: New processing options
            
        Returns:
            Updated ProcessingResult
        """
        start_time = datetime.utcnow()
        
        try:
            # Detect content type from file
            content_type = await self._detect_content_type_from_path(original_path)
            
            # Reprocess with new options
            processed_paths = await self._process_by_type(
                original_path, content_type, new_options
            )
            
            # Re-analyze if needed
            if new_options.get('reanalyze', False):
                metadata = await self._extract_basic_metadata_from_path(original_path, content_type)
                analysis_results = await self._perform_ai_analysis(
                    original_path, content_type, metadata
                )
            else:
                metadata = None
                analysis_results = {}
            
            # Re-optimize for platforms
            optimization_results = await self._optimize_for_platforms(
                original_path, processed_paths, content_type
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ProcessingResult(
                content_id=content_id,
                original_path=original_path,
                processed_paths=processed_paths,
                metadata=metadata,
                analysis_results=analysis_results,
                optimization_results=optimization_results,
                status=ProcessingStatus.OPTIMIZED,
                processing_time=processing_time,
                created_at=start_time
            )
            
            logger.info(f"Content reprocessed successfully: {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Content reprocessing failed: {e}")
            raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")
    
    async def extract_seo_metadata(
        self,
        content_path: str,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """
        Extract SEO-optimized metadata from content
        
        Args:
            content_path: Path to content file
            content_type: Type of content
            
        Returns:
            Dict containing SEO metadata
        """
        try:
            seo_metadata = {
                'title': '',
                'description': '',
                'keywords': [],
                'tags': [],
                'alt_text': '',
                'transcript': '',
                'duration': None,
                'quality_indicators': {}
            }
            
            if content_type == ContentType.AUDIO:
                seo_metadata.update(await self._extract_audio_seo_metadata(content_path))
            elif content_type == ContentType.VIDEO:
                seo_metadata.update(await self._extract_video_seo_metadata(content_path))
            elif content_type == ContentType.IMAGE:
                seo_metadata.update(await self._extract_image_seo_metadata(content_path))
            elif content_type == ContentType.TEXT:
                seo_metadata.update(await self._extract_text_seo_metadata(content_path))
            
            return seo_metadata
            
        except Exception as e:
            logger.error(f"SEO metadata extraction failed: {e}")
            return {}
    
    async def optimize_for_platform(
        self,
        content_path: str,
        platform: str,
        content_type: ContentType
    ) -> str:
        """
        Optimize content for specific platform requirements
        
        Args:
            content_path: Path to original content
            platform: Target platform (youtube, instagram, tiktok, etc.)
            content_type: Type of content
            
        Returns:
            Path to optimized content file
        """
        try:
            platform_configs = {
                'youtube': {
                    'video': {'max_size': 128000000, 'formats': ['mp4'], 'max_duration': 43200},
                    'audio': {'formats': ['mp3', 'wav'], 'bitrate': 320},
                    'image': {'max_size': 2000000, 'formats': ['jpg', 'png'], 'dimensions': (1280, 720)}
                },
                'instagram': {
                    'video': {'max_size': 100000000, 'formats': ['mp4'], 'max_duration': 60},
                    'audio': {'formats': ['mp3'], 'bitrate': 128},
                    'image': {'max_size': 8000000, 'formats': ['jpg'], 'dimensions': (1080, 1080)}
                },
                'tiktok': {
                    'video': {'max_size': 72000000, 'formats': ['mp4'], 'max_duration': 180},
                    'audio': {'formats': ['mp3'], 'bitrate': 128},
                    'image': {'max_size': 5000000, 'formats': ['jpg'], 'dimensions': (1080, 1920)}
                },
                'spotify': {
                    'audio': {'formats': ['mp3', 'flac'], 'bitrate': 320, 'sample_rate': 44100}
                }
            }
            
            platform_config = platform_configs.get(platform, {})
            content_config = platform_config.get(content_type.value, {})
            
            if not content_config:
                logger.warning(f"No optimization config for {platform} - {content_type.value}")
                return content_path
            
            # Generate optimized file path
            optimized_path = await self._generate_optimized_path(content_path, platform)
            
            # Perform platform-specific optimization
            if content_type == ContentType.VIDEO:
                await self._optimize_video_for_platform(
                    content_path, optimized_path, content_config
                )
            elif content_type == ContentType.AUDIO:
                await self._optimize_audio_for_platform(
                    content_path, optimized_path, content_config
                )
            elif content_type == ContentType.IMAGE:
                await self._optimize_image_for_platform(
                    content_path, optimized_path, content_config
                )
            
            logger.info(f"Content optimized for {platform}: {optimized_path}")
            return optimized_path
            
        except Exception as e:
            logger.error(f"Platform optimization failed: {e}")
            return content_path  # Return original if optimization fails
    
    async def _initialize_ai_models(self):
        """Initialize AI models for content analysis"""
        try:
            # Text analysis model
            self.text_analyzer = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Image classification model
            self.image_classifier = pipeline(
                "image-classification",
                model="microsoft/resnet-50",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.warning(f"AI model initialization failed: {e}")
    
    async def _validate_uploaded_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file size (max 500MB)
        if hasattr(file, 'size') and file.size > 500 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 500MB)")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        supported_extensions = []
        for extensions in self.supported_formats.values():
            supported_extensions.extend(extensions)
        
        if file_ext not in supported_extensions:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}")
    
    async def _detect_content_type(self, file: UploadFile) -> ContentType:
        """Detect content type from uploaded file"""
        file_ext = Path(file.filename).suffix.lower()
        mime_type = mimetypes.guess_type(file.filename)[0] or ''
        
        # Check by extension first
        for content_type, extensions in self.supported_formats.items():
            if file_ext in extensions:
                return content_type
        
        # Check by MIME type
        if mime_type.startswith('audio/'):
            return ContentType.AUDIO
        elif mime_type.startswith('video/'):
            return ContentType.VIDEO
        elif mime_type.startswith('image/'):
            return ContentType.IMAGE
        elif mime_type.startswith('text/'):
            return ContentType.TEXT
        
        return ContentType.UNKNOWN
    
    async def _detect_content_type_from_path(self, file_path: str) -> ContentType:
        """Detect content type from file path"""
        file_ext = Path(file_path).suffix.lower()
        
        for content_type, extensions in self.supported_formats.items():
            if file_ext in extensions:
                return content_type
        
        return ContentType.UNKNOWN
    
    async def _save_original_file(self, file: UploadFile, content_id: str, user_id: int) -> str:
        """Save original uploaded file"""
        file_ext = Path(file.filename).suffix
        filename = f"{content_id}{file_ext}"
        file_path = f"uploads/user_{user_id}/originals/{filename}"
        
        # Ensure directory exists
        full_path = Path(settings.UPLOAD_DIR) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        async with aiofiles.open(full_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return str(full_path)
    
    async def _extract_basic_metadata(
        self,
        file_path: str,
        content_type: ContentType,
        file: UploadFile
    ) -> ContentMetadata:
        """Extract basic metadata from file"""
        file_size = Path(file_path).stat().st_size
        mime_type = mimetypes.guess_type(file_path)[0] or ''
        
        metadata = ContentMetadata(
            file_name=file.filename,
            file_size=file_size,
            content_type=content_type,
            mime_type=mime_type,
            tags=[]
        )
        
        # Extract type-specific metadata
        if content_type == ContentType.AUDIO:
            await self._extract_audio_metadata(file_path, metadata)
        elif content_type == ContentType.VIDEO:
            await self._extract_video_metadata(file_path, metadata)
        elif content_type == ContentType.IMAGE:
            await self._extract_image_metadata(file_path, metadata)
        elif content_type == ContentType.TEXT:
            await self._extract_text_metadata(file_path, metadata)
        
        return metadata
    
    async def _extract_basic_metadata_from_path(
        self,
        file_path: str,
        content_type: ContentType
    ) -> ContentMetadata:
        """Extract basic metadata from file path only"""
        file_size = Path(file_path).stat().st_size
        mime_type = mimetypes.guess_type(file_path)[0] or ''
        
        metadata = ContentMetadata(
            file_name=Path(file_path).name,
            file_size=file_size,
            content_type=content_type,
            mime_type=mime_type,
            tags=[]
        )
        
        return metadata
    
    async def _extract_audio_metadata(self, file_path: str, metadata: ContentMetadata):
        """Extract audio-specific metadata"""
        try:
            y, sr = librosa.load(file_path, sr=None)
            metadata.duration = librosa.get_duration(y=y, sr=sr)
            metadata.sample_rate = sr
            metadata.channels = 1 if len(y.shape) == 1 else y.shape[0]
            
        except Exception as e:
            logger.warning(f"Audio metadata extraction failed: {e}")
    
    async def _extract_video_metadata(self, file_path: str, metadata: ContentMetadata):
        """Extract video-specific metadata"""
        try:
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                metadata.duration = frame_count / fps if fps > 0 else None
                metadata.dimensions = (width, height)
                
            cap.release()
            
        except Exception as e:
            logger.warning(f"Video metadata extraction failed: {e}")
    
    async def _extract_image_metadata(self, file_path: str, metadata: ContentMetadata):
        """Extract image-specific metadata"""
        try:
            with Image.open(file_path) as img:
                metadata.dimensions = img.size
                metadata.encoding = img.format
                
        except Exception as e:
            logger.warning(f"Image metadata extraction failed: {e}")
    
    async def _extract_text_metadata(self, file_path: str, metadata: ContentMetadata):
        """Extract text-specific metadata"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                metadata.extracted_text = content[:1000]  # First 1000 chars
                
        except Exception as e:
            logger.warning(f"Text metadata extraction failed: {e}")
    
    async def _process_by_type(
        self,
        file_path: str,
        content_type: ContentType,
        options: Dict[str, Any]
    ) -> Dict[str, str]:
        """Process content based on its type"""
        processed_paths = {}
        
        try:
            if content_type == ContentType.AUDIO:
                processed_paths = await self.audio_processor.process_audio(file_path, options)
            elif content_type == ContentType.VIDEO:
                processed_paths = await self.video_processor.process_video(file_path, options)
            elif content_type == ContentType.IMAGE:
                processed_paths = await self.image_processor.process_image(file_path, options)
            elif content_type == ContentType.TEXT:
                processed_paths = await self.text_processor.process_text(file_path, options)
            
            return processed_paths
            
        except Exception as e:
            logger.error(f"Type-specific processing failed: {e}")
            return {}
    
    async def _perform_ai_analysis(
        self,
        file_path: str,
        content_type: ContentType,
        metadata: ContentMetadata
    ) -> Dict[str, Any]:
        """Perform AI analysis on content"""
        analysis_results = {}
        
        try:
            if content_type == ContentType.TEXT and self.text_analyzer:
                # Analyze text sentiment and content
                if metadata.extracted_text:
                    sentiment = self.text_analyzer(metadata.extracted_text[:512])
                    analysis_results['sentiment'] = sentiment
            
            elif content_type == ContentType.IMAGE and self.image_classifier:
                # Classify image content
                with Image.open(file_path) as img:
                    classification = self.image_classifier(img)
                    analysis_results['classification'] = classification
            
            # Additional AI analysis can be added here
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {}
    
    async def _optimize_for_platforms(
        self,
        original_path: str,
        processed_paths: Dict[str, str],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Optimize content for different platforms"""
        optimization_results = {}
        
        # Define target platforms based on content type
        target_platforms = ['youtube', 'instagram', 'tiktok']
        if content_type == ContentType.AUDIO:
            target_platforms.append('spotify')
        
        for platform in target_platforms:
            try:
                optimized_path = await self.optimize_for_platform(
                    original_path, platform, content_type
                )
                optimization_results[platform] = optimized_path
                
            except Exception as e:
                logger.warning(f"Platform optimization failed for {platform}: {e}")
                optimization_results[platform] = original_path
        
        return optimization_results
    
    async def _extract_audio_seo_metadata(self, content_path: str) -> Dict[str, Any]:
        """Extract SEO metadata from audio content"""
        # Implementation for audio SEO metadata extraction
        return {'content_type': 'audio', 'duration': None}
    
    async def _extract_video_seo_metadata(self, content_path: str) -> Dict[str, Any]:
        """Extract SEO metadata from video content"""
        # Implementation for video SEO metadata extraction
        return {'content_type': 'video', 'duration': None}
    
    async def _extract_image_seo_metadata(self, content_path: str) -> Dict[str, Any]:
        """Extract SEO metadata from image content"""
        # Implementation for image SEO metadata extraction
        return {'content_type': 'image', 'alt_text': ''}
    
    async def _extract_text_seo_metadata(self, content_path: str) -> Dict[str, Any]:
        """Extract SEO metadata from text content"""
        # Implementation for text SEO metadata extraction
        return {'content_type': 'text', 'word_count': 0}
    
    async def _generate_optimized_path(self, original_path: str, platform: str) -> str:
        """Generate path for optimized content"""
        path = Path(original_path)
        parent = path.parent
        stem = path.stem
        suffix = path.suffix
        
        optimized_path = parent / "optimized" / platform / f"{stem}_{platform}{suffix}"
        optimized_path.parent.mkdir(parents=True, exist_ok=True)
        
        return str(optimized_path)
    
    async def _optimize_video_for_platform(
        self,
        input_path: str,
        output_path: str,
        config: Dict[str, Any]
    ):
        """Optimize video for platform-specific requirements"""
        # Implementation for video optimization
        pass
    
    async def _optimize_audio_for_platform(
        self,
        input_path: str,
        output_path: str,
        config: Dict[str, Any]
    ):
        """Optimize audio for platform-specific requirements"""
        # Implementation for audio optimization
        pass
    
    async def _optimize_image_for_platform(
        self,
        input_path: str,
        output_path: str,
        config: Dict[str, Any]
    ):
        """Optimize image for platform-specific requirements"""
        # Implementation for image optimization
        pass
