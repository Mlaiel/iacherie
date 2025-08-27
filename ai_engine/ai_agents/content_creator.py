"""
Content Creator Agent

Specialized AI agent for multi-format content creation including text, audio, video, 
and image generation. Handles creative workflows and content optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Set
from dataclasses import dataclass, field
import logging

from .base_agent import BaseAIAgent, AgentCapability, AgentConfiguration, AgentTask
from ..content_protection.fingerprinting import ContentFingerprinter
from ..ml.content_generation import ContentGenerator
from ..ml.style_transfer import StyleTransferEngine
from ..audio_processing.music_generation import MusicGenerationEngine
from ..core.content_types import ContentType, ContentFormat, ContentQuality

logger = logging.getLogger(__name__)


@dataclass
class ContentCreationRequest:
    """Request for content creation"""
    content_type: ContentType
    format: ContentFormat
    quality: ContentQuality
    style_preferences: Dict[str, Any] = field(default_factory=dict)
    target_audience: str = ""
    platform_requirements: Dict[str, Any] = field(default_factory=dict)
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    inspiration_content: List[str] = field(default_factory=list)
    duration_seconds: Optional[int] = None
    resolution: Optional[str] = None
    language: str = "en"
    mood: str = "neutral"
    genre: str = ""
    keywords: List[str] = field(default_factory=list)
    collaboration_id: Optional[str] = None


@dataclass
class ContentCreationResult:
    """Result of content creation"""
    content_id: str
    content_type: ContentType
    format: ContentFormat
    file_path: str
    metadata: Dict[str, Any]
    fingerprint: str
    quality_score: float
    style_analysis: Dict[str, Any]
    creation_time: datetime
    processing_time_seconds: float
    size_bytes: int
    copyright_status: str
    monetization_ready: bool
    platform_compatibility: Dict[str, bool]
    seo_metadata: Dict[str, Any]


class ContentCreatorAgent(BaseAIAgent):
    """
    Advanced content creation agent supporting multiple formats
    
    Capabilities:
    - Multi-format content generation (text, audio, video, image)
    - Style transfer and adaptation
    - Brand consistency enforcement
    - Platform-specific optimization
    - Copyright protection integration
    - Quality assessment and enhancement
    """
    
    def __init__(self, config: AgentConfiguration):
        # Ensure required capabilities
        required_capabilities = {
            AgentCapability.TEXT_GENERATION,
            AgentCapability.IMAGE_GENERATION,
            AgentCapability.AUDIO_GENERATION,
            AgentCapability.VIDEO_GENERATION,
            AgentCapability.MUSIC_COMPOSITION,
            AgentCapability.CONTENT_OPTIMIZATION,
            AgentCapability.COPYRIGHT_DETECTION
        }
        
        config.capabilities.update(required_capabilities)
        super().__init__(config)
        
        # Content generation engines
        self.content_generator: Optional[ContentGenerator] = None
        self.style_transfer: Optional[StyleTransferEngine] = None
        self.music_engine: Optional[MusicGenerationEngine] = None
        self.fingerprinter: Optional[ContentFingerprinter] = None
        
        # Quality thresholds
        self.min_quality_score = 0.7
        self.max_generation_retries = 3
        
        # Content cache for optimization
        self.content_cache: Dict[str, Any] = {}
        self.style_cache: Dict[str, Any] = {}
    
    async def _custom_initialize(self) -> None:
        """Initialize content creation engines"""
        try:
            # Initialize content generation engines
            self.content_generator = ContentGenerator()
            await self.content_generator.initialize()
            
            self.style_transfer = StyleTransferEngine()
            await self.style_transfer.initialize()
            
            self.music_engine = MusicGenerationEngine()
            await self.music_engine.initialize()
            
            self.fingerprinter = ContentFingerprinter()
            await self.fingerprinter.initialize()
            
            self.logger.info("Content creation engines initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize content creation engines: {str(e)}")
            raise
    
    async def _execute_task_impl(self, task: AgentTask) -> Dict[str, Any]:
        """Execute content creation task"""
        task_type = task.task_type
        context = task.context
        
        if task_type == "create_content":
            return await self._create_content(context)
        elif task_type == "optimize_content":
            return await self._optimize_content(context)
        elif task_type == "style_transfer":
            return await self._apply_style_transfer(context)
        elif task_type == "batch_creation":
            return await self._batch_content_creation(context)
        elif task_type == "adaptive_creation":
            return await self._adaptive_content_creation(context)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _create_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create content based on request"""
        request = ContentCreationRequest(**context.get("request", {}))
        
        self.logger.info(f"Creating {request.content_type.value} content in {request.format.value} format")
        
        start_time = datetime.utcnow()
        content_id = str(uuid.uuid4())
        
        try:
            # Generate base content
            if request.content_type == ContentType.TEXT:
                result = await self._create_text_content(request, content_id)
            elif request.content_type == ContentType.AUDIO:
                result = await self._create_audio_content(request, content_id)
            elif request.content_type == ContentType.VIDEO:
                result = await self._create_video_content(request, content_id)
            elif request.content_type == ContentType.IMAGE:
                result = await self._create_image_content(request, content_id)
            elif request.content_type == ContentType.MUSIC:
                result = await self._create_music_content(request, content_id)
            else:
                raise ValueError(f"Unsupported content type: {request.content_type}")
            
            # Apply quality checks
            quality_score = await self._assess_content_quality(result, request)
            if quality_score < self.min_quality_score:
                self.logger.warning(f"Content quality {quality_score} below threshold {self.min_quality_score}")
                # Attempt enhancement
                result = await self._enhance_content_quality(result, request)
                quality_score = await self._assess_content_quality(result, request)
            
            # Generate fingerprint for copyright protection
            fingerprint = await self.fingerprinter.generate_fingerprint(result.file_path)
            result.fingerprint = fingerprint
            result.quality_score = quality_score
            
            # SEO optimization
            seo_metadata = await self._generate_seo_metadata(result, request)
            result.seo_metadata = seo_metadata
            
            # Platform compatibility check
            compatibility = await self._check_platform_compatibility(result, request)
            result.platform_compatibility = compatibility
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time_seconds = processing_time
            
            self.logger.info(f"Content creation completed in {processing_time:.2f}s with quality score {quality_score:.2f}")
            
            return {
                "success": True,
                "result": result,
                "content_id": content_id,
                "processing_time": processing_time,
                "quality_score": quality_score
            }
            
        except Exception as e:
            self.logger.error(f"Content creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id,
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }
    
    async def _create_text_content(self, request: ContentCreationRequest, content_id: str) -> ContentCreationResult:
        """Create text content"""
        # Generate text using language model
        text_params = {
            "prompt": request.style_preferences.get("prompt", ""),
            "max_length": request.style_preferences.get("max_length", 1000),
            "style": request.style_preferences.get("style", "professional"),
            "tone": request.mood,
            "language": request.language,
            "keywords": request.keywords,
            "target_audience": request.target_audience
        }
        
        generated_text = await self.content_generator.generate_text(text_params)
        
        # Save to file
        file_path = f"generated_content/text/{content_id}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(generated_text)
        
        # Analyze style and metadata
        style_analysis = await self._analyze_text_style(generated_text)
        metadata = {
            "word_count": len(generated_text.split()),
            "character_count": len(generated_text),
            "language": request.language,
            "style": request.style_preferences.get("style", "professional"),
            "keywords_used": request.keywords,
            "readability_score": await self._calculate_readability(generated_text)
        }
        
        return ContentCreationResult(
            content_id=content_id,
            content_type=ContentType.TEXT,
            format=request.format,
            file_path=file_path,
            metadata=metadata,
            fingerprint="",  # Will be filled later
            quality_score=0.0,  # Will be calculated later
            style_analysis=style_analysis,
            creation_time=datetime.utcnow(),
            processing_time_seconds=0.0,
            size_bytes=len(generated_text.encode('utf-8')),
            copyright_status="original",
            monetization_ready=True,
            platform_compatibility={},
            seo_metadata={}
        )
    
    async def _create_audio_content(self, request: ContentCreationRequest, content_id: str) -> ContentCreationResult:
        """Create audio content"""
        audio_params = {
            "duration": request.duration_seconds or 30,
            "genre": request.genre,
            "mood": request.mood,
            "tempo": request.style_preferences.get("tempo", 120),
            "key": request.style_preferences.get("key", "C"),
            "instruments": request.style_preferences.get("instruments", ["piano"]),
            "quality": request.quality.value
        }
        
        # Generate audio
        audio_data = await self.content_generator.generate_audio(audio_params)
        
        # Save to file
        file_format = request.format.value
        file_path = f"generated_content/audio/{content_id}.{file_format}"
        
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        
        # Analyze audio properties
        audio_analysis = await self._analyze_audio_properties(file_path)
        metadata = {
            "duration_seconds": audio_params["duration"],
            "genre": audio_params["genre"],
            "tempo": audio_params["tempo"],
            "key": audio_params["key"],
            "sample_rate": audio_analysis.get("sample_rate", 44100),
            "bit_rate": audio_analysis.get("bit_rate", 320),
            "channels": audio_analysis.get("channels", 2)
        }
        
        return ContentCreationResult(
            content_id=content_id,
            content_type=ContentType.AUDIO,
            format=request.format,
            file_path=file_path,
            metadata=metadata,
            fingerprint="",
            quality_score=0.0,
            style_analysis=audio_analysis,
            creation_time=datetime.utcnow(),
            processing_time_seconds=0.0,
            size_bytes=len(audio_data),
            copyright_status="original",
            monetization_ready=True,
            platform_compatibility={},
            seo_metadata={}
        )
    
    async def _create_music_content(self, request: ContentCreationRequest, content_id: str) -> ContentCreationResult:
        """Create music content using advanced music generation"""
        music_params = {
            "style": request.genre,
            "mood": request.mood,
            "duration": request.duration_seconds or 180,
            "complexity": request.style_preferences.get("complexity", "medium"),
            "harmonic_style": request.style_preferences.get("harmonic_style", "modern"),
            "rhythm_pattern": request.style_preferences.get("rhythm_pattern", "standard"),
            "melody_range": request.style_preferences.get("melody_range", "medium"),
            "instrumentation": request.style_preferences.get("instrumentation", "full_band")
        }
        
        # Generate music using specialized engine
        music_data = await self.music_engine.compose_music(music_params)
        
        # Save in multiple formats for platform compatibility
        formats = ["mp3", "wav", "flac"] if request.quality == ContentQuality.HIGH else ["mp3"]
        file_paths = {}
        
        for fmt in formats:
            file_path = f"generated_content/music/{content_id}.{fmt}"
            await self.music_engine.export_audio(music_data, file_path, fmt)
            file_paths[fmt] = file_path
        
        # Detailed music analysis
        music_analysis = await self.music_engine.analyze_composition(music_data)
        metadata = {
            "composition_structure": music_analysis.get("structure", {}),
            "harmonic_analysis": music_analysis.get("harmony", {}),
            "rhythmic_analysis": music_analysis.get("rhythm", {}),
            "melodic_analysis": music_analysis.get("melody", {}),
            "instrumentation": music_analysis.get("instruments", []),
            "genre_classification": music_analysis.get("genre_scores", {}),
            "mood_analysis": music_analysis.get("mood_scores", {}),
            "technical_specs": music_analysis.get("technical", {})
        }
        
        return ContentCreationResult(
            content_id=content_id,
            content_type=ContentType.MUSIC,
            format=request.format,
            file_path=file_paths.get("mp3", file_paths[list(file_paths.keys())[0]]),
            metadata=metadata,
            fingerprint="",
            quality_score=0.0,
            style_analysis=music_analysis,
            creation_time=datetime.utcnow(),
            processing_time_seconds=0.0,
            size_bytes=sum(os.path.getsize(path) for path in file_paths.values()),
            copyright_status="original",
            monetization_ready=True,
            platform_compatibility={},
            seo_metadata={}
        )
    
    async def _create_image_content(self, request: ContentCreationRequest, content_id: str) -> ContentCreationResult:
        """Create image content"""
        image_params = {
            "prompt": request.style_preferences.get("prompt", ""),
            "style": request.style_preferences.get("art_style", "realistic"),
            "resolution": request.resolution or "1024x1024",
            "aspect_ratio": request.style_preferences.get("aspect_ratio", "1:1"),
            "color_scheme": request.style_preferences.get("color_scheme", "natural"),
            "mood": request.mood,
            "quality": request.quality.value
        }
        
        # Generate image
        image_data = await self.content_generator.generate_image(image_params)
        
        # Save to file
        file_format = request.format.value
        file_path = f"generated_content/images/{content_id}.{file_format}"
        
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Analyze image properties
        image_analysis = await self._analyze_image_properties(file_path)
        metadata = {
            "resolution": image_params["resolution"],
            "aspect_ratio": image_params["aspect_ratio"],
            "color_analysis": image_analysis.get("colors", {}),
            "composition_analysis": image_analysis.get("composition", {}),
            "aesthetic_score": image_analysis.get("aesthetic_score", 0.0),
            "technical_quality": image_analysis.get("technical_quality", {})
        }
        
        return ContentCreationResult(
            content_id=content_id,
            content_type=ContentType.IMAGE,
            format=request.format,
            file_path=file_path,
            metadata=metadata,
            fingerprint="",
            quality_score=0.0,
            style_analysis=image_analysis,
            creation_time=datetime.utcnow(),
            processing_time_seconds=0.0,
            size_bytes=len(image_data),
            copyright_status="original",
            monetization_ready=True,
            platform_compatibility={},
            seo_metadata={}
        )
    
    async def _create_video_content(self, request: ContentCreationRequest, content_id: str) -> ContentCreationResult:
        """Create video content"""
        video_params = {
            "duration": request.duration_seconds or 60,
            "resolution": request.resolution or "1920x1080",
            "fps": request.style_preferences.get("fps", 30),
            "style": request.style_preferences.get("video_style", "cinematic"),
            "transition_style": request.style_preferences.get("transitions", "smooth"),
            "audio_track": request.style_preferences.get("include_audio", True),
            "quality": request.quality.value
        }
        
        # Generate video content
        video_data = await self.content_generator.generate_video(video_params)
        
        # Save to file
        file_format = request.format.value
        file_path = f"generated_content/videos/{content_id}.{file_format}"
        
        with open(file_path, 'wb') as f:
            f.write(video_data)
        
        # Analyze video properties
        video_analysis = await self._analyze_video_properties(file_path)
        metadata = {
            "duration_seconds": video_params["duration"],
            "resolution": video_params["resolution"],
            "fps": video_params["fps"],
            "codec": video_analysis.get("codec", "h264"),
            "bitrate": video_analysis.get("bitrate", "5000k"),
            "has_audio": video_analysis.get("has_audio", False),
            "scene_analysis": video_analysis.get("scenes", []),
            "motion_analysis": video_analysis.get("motion", {})
        }
        
        return ContentCreationResult(
            content_id=content_id,
            content_type=ContentType.VIDEO,
            format=request.format,
            file_path=file_path,
            metadata=metadata,
            fingerprint="",
            quality_score=0.0,
            style_analysis=video_analysis,
            creation_time=datetime.utcnow(),
            processing_time_seconds=0.0,
            size_bytes=len(video_data),
            copyright_status="original",
            monetization_ready=True,
            platform_compatibility={},
            seo_metadata={}
        )
    
    async def _assess_content_quality(self, result: ContentCreationResult, request: ContentCreationRequest) -> float:
        """Assess the quality of generated content"""
        if result.content_type == ContentType.TEXT:
            return await self._assess_text_quality(result.file_path, request)
        elif result.content_type == ContentType.AUDIO:
            return await self._assess_audio_quality(result.file_path, request)
        elif result.content_type == ContentType.MUSIC:
            return await self._assess_music_quality(result.file_path, request)
        elif result.content_type == ContentType.IMAGE:
            return await self._assess_image_quality(result.file_path, request)
        elif result.content_type == ContentType.VIDEO:
            return await self._assess_video_quality(result.file_path, request)
        else:
            return 0.5  # Default neutral score
    
    async def _assess_text_quality(self, file_path: str, request: ContentCreationRequest) -> float:
        """Assess text content quality"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Multiple quality metrics
        scores = []
        
        # Readability score
        readability = await self._calculate_readability(text)
        scores.append(min(readability / 100, 1.0))
        
        # Keyword relevance
        keyword_score = await self._calculate_keyword_relevance(text, request.keywords)
        scores.append(keyword_score)
        
        # Style consistency
        style_score = await self._calculate_style_consistency(text, request.style_preferences)
        scores.append(style_score)
        
        # Length appropriateness
        length_score = await self._calculate_length_appropriateness(text, request)
        scores.append(length_score)
        
        return sum(scores) / len(scores)
    
    async def _generate_seo_metadata(self, result: ContentCreationResult, request: ContentCreationRequest) -> Dict[str, Any]:
        """Generate SEO metadata for content"""
        return {
            "title": await self._generate_seo_title(result, request),
            "description": await self._generate_seo_description(result, request),
            "keywords": await self._extract_seo_keywords(result, request),
            "tags": await self._generate_content_tags(result, request),
            "category": await self._classify_content_category(result),
            "language": request.language,
            "target_audience": request.target_audience,
            "content_type": result.content_type.value,
            "format": result.format.value,
            "quality": request.quality.value
        }
    
    async def _check_platform_compatibility(self, result: ContentCreationResult, request: ContentCreationRequest) -> Dict[str, bool]:
        """Check compatibility with various platforms"""
        platforms = ["spotify", "youtube", "tiktok", "instagram", "twitter", "facebook"]
        compatibility = {}
        
        for platform in platforms:
            compatibility[platform] = await self._check_single_platform_compatibility(result, platform)
        
        return compatibility
    
    async def can_handle_task(self, task_type: str, context: Dict[str, Any]) -> bool:
        """Check if agent can handle specific content creation task"""
        supported_tasks = [
            "create_content",
            "optimize_content", 
            "style_transfer",
            "batch_creation",
            "adaptive_creation"
        ]
        
        if task_type not in supported_tasks:
            return False
        
        # Check if we support the requested content type
        if task_type == "create_content":
            request_data = context.get("request", {})
            content_type = request_data.get("content_type")
            
            supported_types = [
                ContentType.TEXT,
                ContentType.AUDIO,
                ContentType.VIDEO,
                ContentType.IMAGE,
                ContentType.MUSIC
            ]
            
            return content_type in [ct.value for ct in supported_types]
        
        return True
    
    # Additional helper methods would be implemented here for:
    # - Style analysis
    # - Quality enhancement
    # - Platform-specific optimization
    # - Batch processing
    # - Adaptive creation based on performance feedback
