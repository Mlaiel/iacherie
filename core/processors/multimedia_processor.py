"""Multimedia Processor Module - IA-Influencer-Agent Platform

Industrial-grade multimedia processing engine for content creators and influencers.
Handles combined audio, video, image, and text content with advanced AI analysis.

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
import tempfile
import os
from typing import Dict, Any, List, Optional, Union, BinaryIO, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

# Import individual processors
from .audio_processor import AudioProcessor, AudioProcessingConfig, AudioAnalysisResult
from .video_processor import VideoProcessor, VideoProcessingConfig, VideoAnalysisResult
from .image_processor import ImageProcessor, ImageProcessingConfig, ImageAnalysisResult
from .text_processor import TextProcessor, TextProcessingConfig, TextAnalysisResult

# Multimedia processing imports
try:
    import cv2
    import numpy as np
    from PIL import Image
    import moviepy.editor as mp
    MULTIMEDIA_LIBS_AVAILABLE = True
except ImportError:
    MULTIMEDIA_LIBS_AVAILABLE = False

# AI and ML imports for cross-modal analysis
try:
    import torch
    from transformers import pipeline, CLIPProcessor, CLIPModel
    import openai
    AI_LIBS_AVAILABLE = True
except ImportError:
    AI_LIBS_AVAILABLE = False

# Audio-visual synchronization
try:
    import librosa
    import soundfile as sf
    AUDIO_SYNC_AVAILABLE = True
except ImportError:
    AUDIO_SYNC_AVAILABLE = False

logger = logging.getLogger(__name__)


class MultimediaType(str, Enum):
    """Types of multimedia content"""    VIDEO_WITH_AUDIO = "video_with_audio"
    IMAGE_GALLERY = "image_gallery"
    AUDIO_SLIDESHOW = "audio_slideshow"
    INTERACTIVE_PRESENTATION = "interactive_presentation"
    STORY_WITH_MEDIA = "story_with_media"
    PODCAST_WITH_VISUALS = "podcast_with_visuals"
    SOCIAL_MEDIA_POST = "social_media_post"
    EDUCATIONAL_CONTENT = "educational_content"
    MARKETING_CAMPAIGN = "marketing_campaign"
    DOCUMENTARY = "documentary"
    MUSIC_VIDEO = "music_video"
    LIVESTREAM = "livestream"


class ProcessingMode(str, Enum):
    """Multimedia processing modes"""    BASIC_ANALYSIS = "basic_analysis"
    DEEP_ANALYSIS = "deep_analysis"
    CROSS_MODAL = "cross_modal"
    SYNCHRONIZED = "synchronized"
    INTERACTIVE = "interactive"
    REAL_TIME = "real_time"


class ContentQuality(str, Enum):
    """Content quality levels"""    LOW = "low"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"


@dataclass
class MultimediaProcessingConfig:
    """Configuration for multimedia processing"""    processing_mode: ProcessingMode = ProcessingMode.DEEP_ANALYSIS
    enable_cross_modal_analysis: bool = True
    enable_sync_analysis: bool = True
    enable_sentiment_correlation: bool = True
    enable_scene_detection: bool = True
    enable_content_matching: bool = True
    enable_quality_assessment: bool = True
    enable_accessibility_analysis: bool = True
    target_quality: ContentQuality = ContentQuality.HIGH
    max_file_size: int = 1024 * 1024 * 1024  # 1GB
    max_duration: int = 3600  # 1 hour in seconds
    temp_directory: Optional[str] = None
    parallel_processing: bool = True
    cache_intermediate_results: bool = True
    
    # Individual processor configs
    audio_config: Optional[Dict[str, Any]] = None
    video_config: Optional[Dict[str, Any]] = None
    image_config: Optional[Dict[str, Any]] = None
    text_config: Optional[Dict[str, Any]] = None


@dataclass
class MultimediaMetadata:
    """Comprehensive multimedia metadata"""    content_type: Optional[MultimediaType] = None
    total_duration: Optional[float] = None
    total_size: Optional[int] = None
    component_count: int = 0
    audio_tracks: int = 0
    video_tracks: int = 0
    image_count: int = 0
    text_blocks: int = 0
    languages: List[str] = field(default_factory=list)
    resolution: Optional[Tuple[int, int]] = None
    frame_rate: Optional[float] = None
    audio_sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    color_space: Optional[str] = None
    codec_info: Dict[str, str] = field(default_factory=dict)
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    creator: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    copyright_info: Optional[str] = None
    accessibility_features: List[str] = field(default_factory=list)


@dataclass
class CrossModalAnalysis:
    """Cross-modal analysis results"""    audio_visual_sync: Optional[float] = None  # Synchronization score
    content_coherence: Optional[float] = None  # How well content matches across modalities
    emotion_consistency: Optional[float] = None  # Emotional consistency across modalities
    semantic_alignment: Optional[float] = None  # Semantic alignment score
    attention_correlation: Optional[float] = None  # Attention pattern correlation
    narrative_flow: Optional[float] = None  # Narrative flow consistency
    cross_modal_features: Dict[str, Any] = field(default_factory=dict)
    modality_contributions: Dict[str, float] = field(default_factory=dict)
    interaction_patterns: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ContentSynchronization:
    """Content synchronization analysis"""    audio_video_offset: Optional[float] = None
    subtitle_sync: Optional[float] = None
    scene_audio_correlation: List[Dict[str, Any]] = field(default_factory=list)
    beat_visual_sync: Optional[float] = None
    speech_visual_alignment: Optional[float] = None
    music_mood_correlation: Optional[float] = None
    timing_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAssessment:
    """Multimedia quality assessment"""    overall_quality: Optional[float] = None
    technical_quality: Optional[float] = None
    content_quality: Optional[float] = None
    production_quality: Optional[float] = None
    accessibility_score: Optional[float] = None
    engagement_potential: Optional[float] = None
    viral_potential: Optional[float] = None
    professional_score: Optional[float] = None
    quality_issues: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)


@dataclass
class MultimediaFeatures:
    """Advanced multimedia features"""    audio_analysis: Optional[AudioAnalysisResult] = None
    video_analysis: Optional[VideoAnalysisResult] = None
    image_analysis: List[ImageAnalysisResult] = field(default_factory=list)
    text_analysis: Optional[TextAnalysisResult] = None
    cross_modal_analysis: Optional[CrossModalAnalysis] = None
    synchronization: Optional[ContentSynchronization] = None
    quality_assessment: Optional[QualityAssessment] = None
    scene_breakdown: List[Dict[str, Any]] = field(default_factory=list)
    highlights: List[Dict[str, Any]] = field(default_factory=list)
    summary: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    emotions: Dict[str, float] = field(default_factory=dict)
    topics: List[str] = field(default_factory=list)
    style_analysis: Dict[str, Any] = field(default_factory=dict)
    technical_specs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultimediaAnalysisResult:
    """Result of multimedia analysis"""    success: bool
    metadata: Optional[MultimediaMetadata] = None
    features: Optional[MultimediaFeatures] = None
    processed_components: Dict[str, Any] = field(default_factory=dict)
    fingerprint: Optional[str] = None
    content_hash: Optional[str] = None
    similarity_hash: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    component_processing_times: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None


class MultimediaProcessor:
    """    🎬 ENTERPRISE MULTIMEDIA PROCESSOR
    
    Industrial-grade multimedia processing engine with advanced cross-modal analysis,
    synchronization detection, and AI-powered insights for content creators.
    """    
    def __init__(
        self,
        db_session,
        redis_client,
        config: Optional[MultimediaProcessingConfig] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or MultimediaProcessingConfig()
        self.logger = logging.getLogger(f"{__name__}.MultimediaProcessor")
        
        # Individual processors
        self.audio_processor = None
        self.video_processor = None
        self.image_processor = None
        self.text_processor = None
        
        # AI models for cross-modal analysis
        self._clip_model = None
        self._clip_processor = None
        self._multimodal_model = None
        
        self._initialized = False
        self._temp_dir = None
        
        if not MULTIMEDIA_LIBS_AVAILABLE:
            self.logger.warning("Multimedia processing libraries not available")
        
        if not AI_LIBS_AVAILABLE:
            self.logger.warning("AI libraries not available")
    
    async def initialize(self) -> bool:
        """Initialize the multimedia processor"""        try:
            # Setup temporary directory
            if self.config.temp_directory:
                self._temp_dir = Path(self.config.temp_directory)
                self._temp_dir.mkdir(exist_ok=True)
            else:
                self._temp_dir = Path(tempfile.mkdtemp(prefix="multimedia_processor_"))
            
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
            
            # Initialize cross-modal AI models
            if AI_LIBS_AVAILABLE and self.config.enable_cross_modal_analysis:
                try:
                    self._clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                    self._clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                    self.logger.info("CLIP model loaded for cross-modal analysis")
                except Exception as e:
                    self.logger.warning(f"Could not load CLIP model: {e}")
            
            self._initialized = True
            self.logger.info("✅ Multimedia processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize multimedia processor: {e}")
            return False
    
    async def process(
        self,
        content: Union[str, bytes, BinaryIO, Path, Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Process multimedia content with comprehensive analysis
        
        Args:
            content: Multimedia content (file path, bytes, file object, or component dict)
            options: Processing options
            metadata: Additional metadata
            
        Returns:
            Processing result dictionary
        """        start_time = time.time()
        options = options or {}
        metadata = metadata or {}
        
        try:
            if not self._initialized:
                await self.initialize()
            
            # Load and decompose multimedia content
            components = await self._decompose_content(content, metadata)
            
            if not components:
                return {
                    "success": False,
                    "error_message": "Failed to decompose multimedia content",
                    "processing_time": time.time() - start_time
                }
            
            # Extract multimedia metadata
            multimedia_metadata = await self._extract_multimedia_metadata(components)
            
            # Validate content
            validation_result = await self._validate_multimedia_content(multimedia_metadata)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error_message": validation_result["reason"],
                    "processing_time": time.time() - start_time
                }
            
            # Process individual components
            processed_components = {}
            component_times = {}
            
            # Process in parallel if enabled
            if self.config.parallel_processing:
                tasks = []
                
                if "audio" in components:
                    tasks.append(self._process_audio_component(components["audio"]))
                if "video" in components:
                    tasks.append(self._process_video_component(components["video"]))
                if "images" in components:
                    tasks.append(self._process_image_components(components["images"]))
                if "text" in components:
                    tasks.append(self._process_text_component(components["text"]))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Collect results
                result_keys = []
                if "audio" in components:
                    result_keys.append("audio")
                if "video" in components:
                    result_keys.append("video")
                if "images" in components:
                    result_keys.append("images")
                if "text" in components:
                    result_keys.append("text")
                
                for i, result in enumerate(results):
                    if not isinstance(result, Exception):
                        processed_components[result_keys[i]] = result
            else:
                # Sequential processing
                if "audio" in components:
                    component_start = time.time()
                    processed_components["audio"] = await self._process_audio_component(components["audio"])
                    component_times["audio"] = time.time() - component_start
                
                if "video" in components:
                    component_start = time.time()
                    processed_components["video"] = await self._process_video_component(components["video"])
                    component_times["video"] = time.time() - component_start
                
                if "images" in components:
                    component_start = time.time()
                    processed_components["images"] = await self._process_image_components(components["images"])
                    component_times["images"] = time.time() - component_start
                
                if "text" in components:
                    component_start = time.time()
                    processed_components["text"] = await self._process_text_component(components["text"])
                    component_times["text"] = time.time() - component_start
            
            # Cross-modal analysis
            cross_modal_analysis = None
            if self.config.enable_cross_modal_analysis:
                cross_modal_analysis = await self._perform_cross_modal_analysis(processed_components)
            
            # Synchronization analysis
            synchronization = None
            if self.config.enable_sync_analysis:
                synchronization = await self._analyze_synchronization(processed_components, components)
            
            # Quality assessment
            quality_assessment = None
            if self.config.enable_quality_assessment:
                quality_assessment = await self._assess_quality(processed_components, multimedia_metadata)
            
            # Scene breakdown and highlights
            scene_breakdown = await self._analyze_scenes(processed_components)
            highlights = await self._extract_highlights(processed_components, cross_modal_analysis)
            
            # Generate summary and extract key information
            summary = await self._generate_multimedia_summary(processed_components)
            keywords = await self._extract_multimedia_keywords(processed_components)
            entities = await self._extract_multimedia_entities(processed_components)
            emotions = await self._analyze_multimedia_emotions(processed_components)
            topics = await self._extract_multimedia_topics(processed_components)
            
            # Create multimedia features
            features = MultimediaFeatures(
                audio_analysis=processed_components.get("audio"),
                video_analysis=processed_components.get("video"),
                image_analysis=processed_components.get("images", []),
                text_analysis=processed_components.get("text"),
                cross_modal_analysis=cross_modal_analysis,
                synchronization=synchronization,
                quality_assessment=quality_assessment,
                scene_breakdown=scene_breakdown,
                highlights=highlights,
                summary=summary,
                keywords=keywords,
                entities=entities,
                emotions=emotions,
                topics=topics
            )
            
            # Generate fingerprints and hashes
            fingerprint = await self._generate_multimedia_fingerprint(components)
            content_hash = await self._generate_content_hash(processed_components)
            similarity_hash = await self._generate_similarity_hash(features)
            
            # Generate tags
            tags = await self._generate_multimedia_tags(multimedia_metadata, features)
            
            # Create analysis result
            analysis_result = MultimediaAnalysisResult(
                success=True,
                metadata=multimedia_metadata,
                features=features,
                processed_components=processed_components,
                fingerprint=fingerprint,
                content_hash=content_hash,
                similarity_hash=similarity_hash,
                tags=tags,
                processing_time=time.time() - start_time,
                component_processing_times=component_times
            )
            
            return {
                "success": True,
                "analysis_result": analysis_result.__dict__,
                "metadata": multimedia_metadata.__dict__,
                "quality_metrics": {
                    "overall_quality": quality_assessment.overall_quality if quality_assessment else None,
                    "engagement_potential": quality_assessment.engagement_potential if quality_assessment else None,
                    "professional_score": quality_assessment.professional_score if quality_assessment else None,
                    "cross_modal_coherence": cross_modal_analysis.content_coherence if cross_modal_analysis else None
                },
                "tags": tags,
                "processing_time": time.time() - start_time,
                "component_processing_times": component_times
            }
            
        except Exception as e:
            self.logger.error(f"Multimedia processing failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "processing_time": time.time() - start_time
            }
        finally:
            # Cleanup temporary files
            await self._cleanup_temp_files()
    
    async def _decompose_content(
        self,
        content: Union[str, bytes, BinaryIO, Path, Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Decompose multimedia content into individual components"""        try:
            components = {}
            
            # Handle different input types
            if isinstance(content, dict):
                # Content already decomposed
                return content
            
            elif isinstance(content, (str, Path)):
                # File path - detect type and extract components
                file_path = Path(content)
                
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                # Determine file type
                extension = file_path.suffix.lower()
                
                if extension in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                    # Video file - extract video, audio, and subtitles
                    components = await self._extract_video_components(file_path)
                elif extension in ['.mp3', '.wav', '.flac', '.m4a', '.ogg']:
                    # Audio file
                    components["audio"] = file_path
                elif extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                    # Image file
                    components["images"] = [file_path]
                elif extension in ['.txt', '.md', '.docx', '.pdf']:
                    # Text document
                    components["text"] = file_path
                else:
                    self.logger.warning(f"Unknown file type: {extension}")
                    return None
            
            elif isinstance(content, bytes):
                # Raw bytes - save to temp file and detect type
                temp_file = self._temp_dir / f"temp_content_{int(time.time())}"
                with open(temp_file, 'wb') as f:
                    f.write(content)
                
                # Recursively process temp file
                components = await self._decompose_content(temp_file, metadata)
            
            else:
                # File object
                temp_file = self._temp_dir / f"temp_content_{int(time.time())}"
                with open(temp_file, 'wb') as f:
                    f.write(content.read())
                
                components = await self._decompose_content(temp_file, metadata)
            
            return components
            
        except Exception as e:
            self.logger.error(f"Content decomposition failed: {e}")
            return None
    
    async def _extract_video_components(self, video_path: Path) -> Dict[str, Any]:
        """Extract components from video file"""        try:
            components = {}
            
            if not MULTIMEDIA_LIBS_AVAILABLE:
                components["video"] = video_path
                return components
            
            # Load video
            clip = mp.VideoFileClip(str(video_path))
            
            # Video component
            components["video"] = video_path
            
            # Extract audio if present
            if clip.audio is not None:
                audio_path = self._temp_dir / f"extracted_audio_{int(time.time())}.wav"
                clip.audio.write_audiofile(str(audio_path), verbose=False, logger=None)
                components["audio"] = audio_path
            
            # Extract key frames as images
            images = []
            duration = clip.duration
            
            # Extract frames at regular intervals
            num_frames = min(10, int(duration))  # Max 10 frames
            for i in range(num_frames):
                t = (i * duration) / num_frames
                frame = clip.get_frame(t)
                
                frame_path = self._temp_dir / f"frame_{i}_{int(time.time())}.jpg"
                frame_image = Image.fromarray(frame.astype('uint8'))
                frame_image.save(frame_path)
                images.append(frame_path)
            
            if images:
                components["images"] = images
            
            clip.close()
            return components
            
        except Exception as e:
            self.logger.error(f"Video component extraction failed: {e}")
            return {"video": video_path}
    
    async def _extract_multimedia_metadata(self, components: Dict[str, Any]) -> MultimediaMetadata:
        """Extract comprehensive multimedia metadata"""        try:
            metadata = MultimediaMetadata()
            
            # Count components
            metadata.component_count = len(components)
            metadata.audio_tracks = 1 if "audio" in components else 0
            metadata.video_tracks = 1 if "video" in components else 0
            metadata.image_count = len(components.get("images", []))
            metadata.text_blocks = 1 if "text" in components else 0
            
            # Determine content type
            if "video" in components and "audio" in components:
                metadata.content_type = MultimediaType.VIDEO_WITH_AUDIO
            elif "audio" in components and "images" in components:
                metadata.content_type = MultimediaType.AUDIO_SLIDESHOW
            elif len(components.get("images", [])) > 1:
                metadata.content_type = MultimediaType.IMAGE_GALLERY
            elif "text" in components and ("images" in components or "audio" in components):
                metadata.content_type = MultimediaType.STORY_WITH_MEDIA
            else:
                metadata.content_type = MultimediaType.SOCIAL_MEDIA_POST
            
            # Extract technical metadata
            if "video" in components and MULTIMEDIA_LIBS_AVAILABLE:
                try:
                    clip = mp.VideoFileClip(str(components["video"]))
                    metadata.total_duration = clip.duration
                    metadata.resolution = (clip.w, clip.h)
                    metadata.frame_rate = clip.fps
                    clip.close()
                except:
                    pass
            
            # Calculate total size
            total_size = 0
            for component_type, component_data in components.items():
                if component_type == "images":
                    for image_path in component_data:
                        if isinstance(image_path, Path) and image_path.exists():
                            total_size += image_path.stat().st_size
                else:
                    if isinstance(component_data, Path) and component_data.exists():
                        total_size += component_data.stat().st_size
            
            metadata.total_size = total_size
            metadata.creation_date = datetime.now()
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Multimedia metadata extraction failed: {e}")
            return MultimediaMetadata()
    
    async def _validate_multimedia_content(self, metadata: MultimediaMetadata) -> Dict[str, Any]:
        """Validate multimedia content against configuration constraints"""        if metadata.total_size and metadata.total_size > self.config.max_file_size:
            return {
                "valid": False,
                "reason": f"Total size ({metadata.total_size}) exceeds maximum ({self.config.max_file_size})"
            }
        
        if metadata.total_duration and metadata.total_duration > self.config.max_duration:
            return {
                "valid": False,
                "reason": f"Duration ({metadata.total_duration}s) exceeds maximum ({self.config.max_duration}s)"
            }
        
        if metadata.component_count == 0:
            return {
                "valid": False,
                "reason": "No multimedia components found"
            }
        
        return {"valid": True}
    
    async def _process_audio_component(self, audio_path: Path) -> Optional[AudioAnalysisResult]:
        """Process audio component"""        try:
            if not self.audio_processor:
                return None
            
            result = await self.audio_processor.process(audio_path)
            
            if result["success"]:
                return result["analysis_result"]
            else:
                self.logger.warning(f"Audio processing failed: {result.get('error_message')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Audio component processing failed: {e}")
            return None
    
    async def _process_video_component(self, video_path: Path) -> Optional[VideoAnalysisResult]:
        """Process video component"""        try:
            if not self.video_processor:
                return None
            
            result = await self.video_processor.process(video_path)
            
            if result["success"]:
                return result["analysis_result"]
            else:
                self.logger.warning(f"Video processing failed: {result.get('error_message')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Video component processing failed: {e}")
            return None
    
    async def _process_image_components(self, image_paths: List[Path]) -> List[ImageAnalysisResult]:
        """Process image components"""        try:
            if not self.image_processor:
                return []
            
            results = []
            
            for image_path in image_paths:
                try:
                    result = await self.image_processor.process(image_path)
                    
                    if result["success"]:
                        results.append(result["analysis_result"])
                    else:
                        self.logger.warning(f"Image processing failed for {image_path}: {result.get('error_message')}")
                        
                except Exception as e:
                    self.logger.error(f"Image processing failed for {image_path}: {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Image components processing failed: {e}")
            return []
    
    async def _process_text_component(self, text_path: Path) -> Optional[TextAnalysisResult]:
        """Process text component"""        try:
            if not self.text_processor:
                return None
            
            result = await self.text_processor.process(text_path)
            
            if result["success"]:
                return result["analysis_result"]
            else:
                self.logger.warning(f"Text processing failed: {result.get('error_message')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Text component processing failed: {e}")
            return None
    
    async def _perform_cross_modal_analysis(self, processed_components: Dict[str, Any]) -> Optional[CrossModalAnalysis]:
        """Perform cross-modal analysis between different media types"""        try:
            analysis = CrossModalAnalysis()
            
            # Calculate modality contributions
            total_components = len(processed_components)
            if total_components == 0:
                return analysis
            
            for modality in processed_components:
                analysis.modality_contributions[modality] = 1.0 / total_components
            
            # Audio-visual analysis
            if "audio" in processed_components and "video" in processed_components:
                analysis.audio_visual_sync = await self._analyze_audio_visual_sync(
                    processed_components["audio"], processed_components["video"]
                )
            
            # Content coherence analysis
            if len(processed_components) > 1:
                analysis.content_coherence = await self._analyze_content_coherence(processed_components)
            
            # Emotion consistency
            analysis.emotion_consistency = await self._analyze_emotion_consistency(processed_components)
            
            # Semantic alignment
            if self._clip_model and self._clip_processor:
                analysis.semantic_alignment = await self._analyze_semantic_alignment(processed_components)
            
            # Narrative flow
            analysis.narrative_flow = await self._analyze_narrative_flow(processed_components)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Cross-modal analysis failed: {e}")
            return CrossModalAnalysis()
    
    async def _analyze_audio_visual_sync(self, audio_result, video_result) -> float:
        """Analyze audio-visual synchronization"""        try:
            # Simplified sync analysis
            # In a full implementation, this would analyze audio beats vs visual cuts
            
            if not audio_result or not video_result:
                return 0.5
            
            # Compare durations
            audio_duration = getattr(audio_result.metadata, 'duration', 0) if audio_result.metadata else 0
            video_duration = getattr(video_result.metadata, 'duration', 0) if video_result.metadata else 0
            
            if audio_duration > 0 and video_duration > 0:
                duration_sync = 1.0 - abs(audio_duration - video_duration) / max(audio_duration, video_duration)
                return max(0.0, duration_sync)
            
            return 0.5
            
        except Exception as e:
            self.logger.error(f"Audio-visual sync analysis failed: {e}")
            return 0.5
    
    async def _analyze_content_coherence(self, processed_components: Dict[str, Any]) -> float:
        """Analyze content coherence across modalities"""        try:
            # Extract keywords/topics from each modality
            modality_keywords = {}
            
            if "text" in processed_components and processed_components["text"]:
                text_result = processed_components["text"]
                if hasattr(text_result, 'features') and text_result.features:
                    if hasattr(text_result.features, 'keyword_extraction') and text_result.features.keyword_extraction:
                        modality_keywords["text"] = text_result.features.keyword_extraction.keywords
            
            if "audio" in processed_components and processed_components["audio"]:
                audio_result = processed_components["audio"]
                if hasattr(audio_result, 'features') and audio_result.features:
                    # Extract keywords from transcription if available
                    modality_keywords["audio"] = []  # Placeholder
            
            # Calculate keyword overlap
            if len(modality_keywords) < 2:
                return 0.5
            
            keyword_sets = [set(keywords) for keywords in modality_keywords.values()]
            
            if all(len(ks) == 0 for ks in keyword_sets):
                return 0.5
            
            # Calculate Jaccard similarity
            intersection = set.intersection(*keyword_sets)
            union = set.union(*keyword_sets)
            
            if len(union) == 0:
                return 0.5
            
            coherence = len(intersection) / len(union)
            return coherence
            
        except Exception as e:
            self.logger.error(f"Content coherence analysis failed: {e}")
            return 0.5
    
    async def _analyze_emotion_consistency(self, processed_components: Dict[str, Any]) -> float:
        """Analyze emotion consistency across modalities"""        try:
            emotions = []
            
            # Extract emotions from each modality
            for modality, result in processed_components.items():
                if result and hasattr(result, 'features') and result.features:
                    if hasattr(result.features, 'sentiment_analysis'):
                        # Convert sentiment to emotion
                        sentiment = result.features.sentiment_analysis
                        if hasattr(sentiment, 'overall_sentiment'):
                            emotions.append(sentiment.overall_sentiment)
            
            if len(emotions) < 2:
                return 0.5
            
            # Calculate consistency (simplified)
            positive_count = emotions.count('positive')
            negative_count = emotions.count('negative')
            neutral_count = emotions.count('neutral')
            
            total = len(emotions)
            max_count = max(positive_count, negative_count, neutral_count)
            
            consistency = max_count / total
            return consistency
            
        except Exception as e:
            self.logger.error(f"Emotion consistency analysis failed: {e}")
            return 0.5
    
    async def _analyze_semantic_alignment(self, processed_components: Dict[str, Any]) -> float:
        """Analyze semantic alignment using CLIP model"""        try:
            if not self._clip_model or not self._clip_processor:
                return 0.5
            
            # This would require actual CLIP processing
            # Placeholder implementation
            return 0.7
            
        except Exception as e:
            self.logger.error(f"Semantic alignment analysis failed: {e}")
            return 0.5
    
    async def _analyze_narrative_flow(self, processed_components: Dict[str, Any]) -> float:
        """Analyze narrative flow consistency"""        try:
            # Simplified narrative flow analysis
            # In a full implementation, this would analyze story structure
            
            flow_score = 0.5
            
            # Check if there's text content for narrative
            if "text" in processed_components and processed_components["text"]:
                text_result = processed_components["text"]
                if hasattr(text_result, 'metadata') and text_result.metadata:
                    # Longer text generally has better narrative flow potential
                    word_count = getattr(text_result.metadata, 'word_count', 0)
                    if word_count > 100:
                        flow_score += 0.2
                    if word_count > 500:
                        flow_score += 0.2
            
            # Check for temporal consistency in video
            if "video" in processed_components:
                flow_score += 0.1  # Videos inherently have temporal flow
            
            return min(1.0, flow_score)
            
        except Exception as e:
            self.logger.error(f"Narrative flow analysis failed: {e}")
            return 0.5
    
    async def _analyze_synchronization(
        self,
        processed_components: Dict[str, Any],
        raw_components: Dict[str, Any]
    ) -> Optional[ContentSynchronization]:
        """Analyze content synchronization"""        try:
            sync = ContentSynchronization()
            
            # Audio-video offset analysis
            if "audio" in processed_components and "video" in processed_components:
                sync.audio_video_offset = await self._calculate_av_offset(
                    raw_components.get("audio"), raw_components.get("video")
                )
            
            # Scene-audio correlation
            if "video" in processed_components and "audio" in processed_components:
                sync.scene_audio_correlation = await self._analyze_scene_audio_correlation(
                    processed_components["video"], processed_components["audio"]
                )
            
            return sync
            
        except Exception as e:
            self.logger.error(f"Synchronization analysis failed: {e}")
            return ContentSynchronization()
    
    async def _calculate_av_offset(self, audio_path, video_path) -> float:
        """Calculate audio-video offset"""        try:
            # Simplified offset calculation
            # In a full implementation, this would use cross-correlation
            return 0.0  # Assuming perfect sync
            
        except Exception as e:
            self.logger.error(f"AV offset calculation failed: {e}")
            return 0.0
    
    async def _analyze_scene_audio_correlation(self, video_result, audio_result) -> List[Dict[str, Any]]:
        """Analyze scene-audio correlation"""        try:
            correlations = []
            
            # Placeholder implementation
            # In a full implementation, this would analyze scene changes vs audio features
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Scene-audio correlation analysis failed: {e}")
            return []
    
    async def _assess_quality(
        self,
        processed_components: Dict[str, Any],
        metadata: MultimediaMetadata
    ) -> Optional[QualityAssessment]:
        """Assess overall multimedia quality"""        try:
            assessment = QualityAssessment()
            
            quality_scores = []
            
            # Assess individual component qualities
            for modality, result in processed_components.items():
                if result and hasattr(result, 'features') and result.features:
                    # Extract quality metrics from each component
                    if hasattr(result.features, 'quality_score'):
                        quality_scores.append(result.features.quality_score)
                    elif hasattr(result.features, 'technical_quality'):
                        quality_scores.append(result.features.technical_quality)
            
            # Calculate overall quality
            if quality_scores:
                assessment.overall_quality = sum(quality_scores) / len(quality_scores)
                assessment.technical_quality = assessment.overall_quality
            else:
                assessment.overall_quality = 0.5
                assessment.technical_quality = 0.5
            
            # Content quality assessment
            assessment.content_quality = await self._assess_content_quality(processed_components)
            
            # Production quality assessment
            assessment.production_quality = await self._assess_production_quality(metadata)
            
            # Engagement potential
            assessment.engagement_potential = await self._assess_engagement_potential(processed_components)
            
            # Professional score
            assessment.professional_score = (
                assessment.technical_quality * 0.3 +
                assessment.content_quality * 0.3 +
                assessment.production_quality * 0.4
            )
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            return QualityAssessment()
    
    async def _assess_content_quality(self, processed_components: Dict[str, Any]) -> float:
        """Assess content quality"""        try:
            scores = []
            
            # Check for diverse content
            if len(processed_components) > 1:
                scores.append(0.8)  # Multimedia content is generally higher quality
            else:
                scores.append(0.6)
            
            # Check for text quality
            if "text" in processed_components and processed_components["text"]:
                text_result = processed_components["text"]
                if hasattr(text_result, 'features') and text_result.features:
                    if hasattr(text_result.features, 'quality_score'):
                        scores.append(text_result.features.quality_score)
            
            return sum(scores) / len(scores) if scores else 0.5
            
        except Exception as e:
            self.logger.error(f"Content quality assessment failed: {e}")
            return 0.5
    
    async def _assess_production_quality(self, metadata: MultimediaMetadata) -> float:
        """Assess production quality"""        try:
            score = 0.5
            
            # Resolution quality
            if metadata.resolution:
                width, height = metadata.resolution
                total_pixels = width * height
                
                if total_pixels >= 1920 * 1080:  # Full HD or higher
                    score += 0.3
                elif total_pixels >= 1280 * 720:  # HD
                    score += 0.2
                elif total_pixels >= 640 * 480:  # SD
                    score += 0.1
            
            # Frame rate quality
            if metadata.frame_rate:
                if metadata.frame_rate >= 60:
                    score += 0.2
                elif metadata.frame_rate >= 30:
                    score += 0.15
                elif metadata.frame_rate >= 24:
                    score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Production quality assessment failed: {e}")
            return 0.5
    
    async def _assess_engagement_potential(self, processed_components: Dict[str, Any]) -> float:
        """Assess engagement potential"""        try:
            score = 0.3  # Base score
            
            # Multimedia content has higher engagement potential
            if len(processed_components) > 1:
                score += 0.3
            
            # Video content is highly engaging
            if "video" in processed_components:
                score += 0.2
            
            # Audio content adds engagement
            if "audio" in processed_components:
                score += 0.1
            
            # Visual content is engaging
            if "images" in processed_components:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Engagement potential assessment failed: {e}")
            return 0.5
    
    async def _analyze_scenes(self, processed_components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze scenes in multimedia content"""        try:
            scenes = []
            
            # Extract scenes from video if available
            if "video" in processed_components and processed_components["video"]:
                video_result = processed_components["video"]
                if hasattr(video_result, 'features') and video_result.features:
                    # Extract scene information
                    # Placeholder implementation
                    scenes.append({
                        "start_time": 0.0,
                        "end_time": 10.0,
                        "type": "opening",
                        "description": "Video opening scene"
                    })
            
            return scenes
            
        except Exception as e:
            self.logger.error(f"Scene analysis failed: {e}")
            return []
    
    async def _extract_highlights(
        self,
        processed_components: Dict[str, Any],
        cross_modal_analysis: Optional[CrossModalAnalysis]
    ) -> List[Dict[str, Any]]:
        """Extract highlights from multimedia content"""        try:
            highlights = []
            
            # Extract highlights based on different criteria
            
            # High-energy audio moments
            if "audio" in processed_components and processed_components["audio"]:
                audio_result = processed_components["audio"]
                if hasattr(audio_result, 'features') and audio_result.features:
                    # Find high-energy moments
                    highlights.append({
                        "type": "audio_highlight",
                        "timestamp": 5.0,
                        "duration": 2.0,
                        "description": "High-energy audio moment",
                        "confidence": 0.8
                    })
            
            # Interesting visual moments
            if "video" in processed_components and processed_components["video"]:
                highlights.append({
                    "type": "visual_highlight",
                    "timestamp": 15.0,
                    "duration": 3.0,
                    "description": "Visually interesting scene",
                    "confidence": 0.7
                })
            
            return highlights
            
        except Exception as e:
            self.logger.error(f"Highlight extraction failed: {e}")
            return []
    
    async def _generate_multimedia_summary(self, processed_components: Dict[str, Any]) -> Optional[str]:
        """Generate summary of multimedia content"""        try:
            summary_parts = []
            
            # Summarize each component
            if "text" in processed_components and processed_components["text"]:
                text_result = processed_components["text"]
                if hasattr(text_result, 'features') and text_result.features:
                    if hasattr(text_result.features, 'summary') and text_result.features.summary:
                        summary_parts.append(f"Text content: {text_result.features.summary}")
            
            if "video" in processed_components:
                summary_parts.append("Contains video content with visual storytelling elements.")
            
            if "audio" in processed_components:
                summary_parts.append("Includes audio content for enhanced experience.")
            
            if "images" in processed_components:
                image_count = len(processed_components["images"])
                summary_parts.append(f"Features {image_count} images providing visual context.")
            
            if summary_parts:
                return " ".join(summary_parts)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Multimedia summary generation failed: {e}")
            return None
    
    async def _extract_multimedia_keywords(self, processed_components: Dict[str, Any]) -> List[str]:
        """Extract keywords from all multimedia components"""        try:
            all_keywords = set()
            
            # Extract keywords from each component
            for modality, result in processed_components.items():
                if result and hasattr(result, 'features') and result.features:
                    keywords = []
                    
                    if hasattr(result.features, 'keyword_extraction') and result.features.keyword_extraction:
                        keywords.extend(result.features.keyword_extraction.keywords)
                    elif hasattr(result.features, 'keywords'):
                        keywords.extend(result.features.keywords)
                    
                    all_keywords.update(keywords)
            
            return list(all_keywords)[:20]  # Limit to top 20 keywords
            
        except Exception as e:
            self.logger.error(f"Multimedia keyword extraction failed: {e}")
            return []
    
    async def _extract_multimedia_entities(self, processed_components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities from all multimedia components"""        try:
            all_entities = []
            
            # Extract entities from text components
            if "text" in processed_components and processed_components["text"]:
                text_result = processed_components["text"]
                if hasattr(text_result, 'features') and text_result.features:
                    if hasattr(text_result.features, 'entity_recognition') and text_result.features.entity_recognition:
                        all_entities.extend(text_result.features.entity_recognition.entities)
            
            return all_entities
            
        except Exception as e:
            self.logger.error(f"Multimedia entity extraction failed: {e}")
            return []
    
    async def _analyze_multimedia_emotions(self, processed_components: Dict[str, Any]) -> Dict[str, float]:
        """Analyze emotions across all multimedia components"""        try:
            emotion_scores = {}
            component_count = 0
            
            # Aggregate emotions from all components
            for modality, result in processed_components.items():
                if result and hasattr(result, 'features') and result.features:
                    if hasattr(result.features, 'sentiment_analysis') and result.features.sentiment_analysis:
                        sentiment = result.features.sentiment_analysis
                        if hasattr(sentiment, 'emotions') and sentiment.emotions:
                            component_count += 1
                            for emotion, score in sentiment.emotions.items():
                                if emotion not in emotion_scores:
                                    emotion_scores[emotion] = 0
                                emotion_scores[emotion] += score
            
            # Average the scores
            if component_count > 0:
                for emotion in emotion_scores:
                    emotion_scores[emotion] /= component_count
            
            return emotion_scores
            
        except Exception as e:
            self.logger.error(f"Multimedia emotion analysis failed: {e}")
            return {}
    
    async def _extract_multimedia_topics(self, processed_components: Dict[str, Any]) -> List[str]:
        """Extract topics from all multimedia components"""        try:
            all_topics = set()
            
            # Extract topics from each component
            for modality, result in processed_components.items():
                if result and hasattr(result, 'features') and result.features:
                    topics = []
                    
                    if hasattr(result.features, 'topics'):
                        topics.extend(result.features.topics)
                    
                    all_topics.update(topics)
            
            return list(all_topics)[:10]  # Limit to top 10 topics
            
        except Exception as e:
            self.logger.error(f"Multimedia topic extraction failed: {e}")
            return []
    
    async def _generate_multimedia_fingerprint(self, components: Dict[str, Any]) -> str:
        """Generate multimedia fingerprint"""        try:
            # Create combined hash of all components
            hash_data = []
            
            for component_type, component_data in components.items():
                if component_type == "images":
                    for image_path in component_data:
                        if isinstance(image_path, Path) and image_path.exists():
                            with open(image_path, 'rb') as f:
                                hash_data.append(f.read()[:1024])  # First 1KB
                else:
                    if isinstance(component_data, Path) and component_data.exists():
                        with open(component_data, 'rb') as f:
                            hash_data.append(f.read()[:1024])  # First 1KB
            
            combined_data = b''.join(hash_data)
            fingerprint = hashlib.sha256(combined_data).hexdigest()[:32]
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Multimedia fingerprint generation failed: {e}")
            return ""
    
    async def _generate_content_hash(self, processed_components: Dict[str, Any]) -> str:
        """Generate content hash from processed components"""        try:
            # Create hash from extracted content
            content_data = []
            
            for modality, result in processed_components.items():
                if result and hasattr(result, 'extracted_content'):
                    content_data.append(str(result.extracted_content))
            
            combined_content = ''.join(content_data)
            content_hash = hashlib.md5(combined_content.encode('utf-8')).hexdigest()[:16]
            
            return content_hash
            
        except Exception as e:
            self.logger.error(f"Content hash generation failed: {e}")
            return ""
    
    async def _generate_similarity_hash(self, features: MultimediaFeatures) -> str:
        """Generate similarity hash for content matching"""        try:
            # Create hash from semantic features
            feature_data = []
            
            if features.keywords:
                feature_data.extend(sorted(features.keywords))
            
            if features.topics:
                feature_data.extend(sorted(features.topics))
            
            if features.emotions:
                emotion_str = ''.join(f"{k}:{v:.2f}" for k, v in sorted(features.emotions.items()))
                feature_data.append(emotion_str)
            
            combined_features = ''.join(feature_data)
            similarity_hash = hashlib.md5(combined_features.encode('utf-8')).hexdigest()[:16]
            
            return similarity_hash
            
        except Exception as e:
            self.logger.error(f"Similarity hash generation failed: {e}")
            return ""
    
    async def _generate_multimedia_tags(
        self,
        metadata: MultimediaMetadata,
        features: MultimediaFeatures
    ) -> List[str]:
        """Generate comprehensive tags for multimedia content"""        try:
            tags = []
            
            # Content type tags
            if metadata.content_type:
                tags.append(f"type-{metadata.content_type.value}")
            
            # Component tags
            if metadata.audio_tracks > 0:
                tags.append("has-audio")
            if metadata.video_tracks > 0:
                tags.append("has-video")
            if metadata.image_count > 0:
                tags.append("has-images")
            if metadata.text_blocks > 0:
                tags.append("has-text")
            
            # Quality tags
            if features.quality_assessment:
                if features.quality_assessment.overall_quality and features.quality_assessment.overall_quality > 0.8:
                    tags.append("high-quality")
                if features.quality_assessment.professional_score and features.quality_assessment.professional_score > 0.7:
                    tags.append("professional")
            
            # Duration tags
            if metadata.total_duration:
                if metadata.total_duration < 30:
                    tags.append("short-form")
                elif metadata.total_duration < 300:  # 5 minutes
                    tags.append("medium-form")
                else:
                    tags.append("long-form")
            
            # Resolution tags
            if metadata.resolution:
                width, height = metadata.resolution
                if width >= 1920:
                    tags.append("hd-quality")
                if width >= 3840:
                    tags.append("4k-quality")
            
            # Cross-modal tags
            if features.cross_modal_analysis:
                if features.cross_modal_analysis.content_coherence and features.cross_modal_analysis.content_coherence > 0.7:
                    tags.append("coherent-content")
                if features.cross_modal_analysis.audio_visual_sync and features.cross_modal_analysis.audio_visual_sync > 0.8:
                    tags.append("well-synchronized")
            
            # Topic tags
            for topic in features.topics[:5]:  # Limit to 5 topics
                tags.append(f"topic-{topic}")
            
            # Emotion tags
            for emotion, score in features.emotions.items():
                if score > 0.5:
                    tags.append(f"emotion-{emotion}")
            
            return tags
            
        except Exception as e:
            self.logger.error(f"Multimedia tag generation failed: {e}")
            return []
    
    async def _cleanup_temp_files(self):
        """Clean up temporary files"""        try:
            if self._temp_dir and self._temp_dir.exists():
                import shutil
                for temp_file in self._temp_dir.glob("*"):
                    try:
                        if temp_file.is_file():
                            temp_file.unlink()
                    except:
                        pass
        except Exception as e:
            self.logger.warning(f"Temp file cleanup failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the multimedia processor"""        health_status = {
            "status": "healthy" if self._initialized else "not_initialized",
            "multimedia_libs_available": MULTIMEDIA_LIBS_AVAILABLE,
            "ai_libs_available": AI_LIBS_AVAILABLE,
            "audio_sync_available": AUDIO_SYNC_AVAILABLE,
            "clip_model_loaded": self._clip_model is not None,
            "temp_directory": str(self._temp_dir) if self._temp_dir else None,
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
        
        return health_status


async def create_multimedia_processor(
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> MultimediaProcessor:
    """    Factory function to create and initialize a multimedia processor
    
    Args:
        db_session: Database session
        redis_client: Redis client
        config: Configuration dictionary
        
    Returns:
        Initialized MultimediaProcessor instance
    """    # Create config from dict if provided
    processor_config = None
    if config:
        processor_config = MultimediaProcessingConfig(**{
            k: v for k, v in config.items() 
            if k in MultimediaProcessingConfig.__dataclass_fields__
        })
    
    # Create processor
    processor = MultimediaProcessor(
        db_session=db_session,
        redis_client=redis_client,
        config=processor_config
    )
    
    # Initialize
    await processor.initialize()
    
    return processor
