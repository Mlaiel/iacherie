"""Video SEO Optimizer
Advanced SEO optimization for video content creators and platforms.

Features:
- Video metadata optimization
- Thumbnail analysis and optimization
- Video transcript generation and SEO
- Multi-platform video optimization
- Video accessibility enhancements

Author: Fahed Mlaiel (mlaiel@live.de)
Video SEO + Content Creator expertise applied
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import re
import hashlib

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageStat
    import moviepy.editor as mp
    from transformers import pipeline
    import speech_recognition as sr
    from pydub import AudioSegment
    import pytesseract
    from colorthief import ColorThief
except ImportError as e:
    logging.warning(f"Optional video dependencies not available: {e}")

logger = logging.getLogger(__name__)

class VideoFormat(Enum):
    """Supported video formats."""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    MKV = "mkv"

class VideoQuality(Enum):
    """Video quality levels."""
    SD_480P = "480p"
    HD_720P = "720p"
    FHD_1080P = "1080p"
    QHD_1440P = "1440p"
    UHD_4K = "4k"
    UHD_8K = "8k"

@dataclass
class VideoMetadata:
    """Video file metadata."""
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    bitrate: Optional[int] = None
    format: Optional[VideoFormat] = None
    file_size: Optional[int] = None
    codec: Optional[str] = None
    audio_codec: Optional[str] = None
    quality: Optional[VideoQuality] = None
    aspect_ratio: Optional[str] = None
    thumbnail_count: int = 0
    has_audio: bool = True
    has_subtitles: bool = False

@dataclass
class VideoTranscript:
    """Video transcript with timestamps."""
    full_text: str
    segments: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    language: str = "en"
    speaker_count: int = 1
    auto_generated: bool = True

@dataclass
class ThumbnailAnalysis:
    """Thumbnail analysis results."""
    image_path: str
    width: int
    height: int
    aspect_ratio: str
    file_size: int
    dominant_colors: List[str]
    brightness: float
    contrast: float
    has_text: bool
    text_content: Optional[str] = None
    quality_score: float = 0.0
    click_potential: float = 0.0

@dataclass
class VideoSEOResult:
    """Result of video SEO optimization."""
    original_metadata: VideoMetadata
    optimized_metadata: VideoMetadata
    transcript: Optional[VideoTranscript]
    thumbnail_analysis: List[ThumbnailAnalysis]
    seo_title: str
    seo_description: str
    keywords: List[str]
    hashtags: List[str]
    categories: List[str]
    platform_optimizations: Dict[str, Dict[str, Any]]
    accessibility_features: Dict[str, Any]
    schema_markup: Dict[str, Any]
    optimization_score: float
    recommendations: List[str]

@dataclass
class VideoSEOConfig:
    """Configuration for video SEO optimization."""
    target_platforms: List[str] = field(default_factory=lambda: ["youtube", "tiktok", "instagram", "facebook"])
    content_type: str = "entertainment"  # entertainment, educational, commercial, tutorial
    target_audience: str = "general"
    target_keywords: List[str] = field(default_factory=list)
    generate_transcript: bool = True
    analyze_thumbnails: bool = True
    optimize_for_mobile: bool = True
    include_accessibility: bool = True
    max_title_length: int = 100
    max_description_length: int = 5000
    language: str = "en"

class VideoSEOOptimizer:
    """Advanced video SEO optimization engine."""
    
    def __init__(self) -> None:
        """Initialize the Video SEO Optimizer."""
        self.speech_recognizer = None
        self.image_classifier = None
        self.text_recognizer = None
        self._setup_video_tools()
        
        # Platform-specific requirements
        self.platform_requirements = self._load_platform_requirements()
        
        # Video analysis cache
        self.analysis_cache = {}
        
    def _setup_video_tools(self) -> None:
        """Setup video processing tools."""
        try:
            # Setup speech recognition
            self.speech_recognizer = sr.Recognizer()
            
            # Setup image classification model
            try:
                self.image_classifier = pipeline(
                    "image-classification",
                    model="google/vit-base-patch16-224"
                )
            except Exception as e:
                logger.warning(f"Could not load image classifier: {e}")
            
            # Setup text recognition (OCR)
            try:
                # pytesseract should be available if installed
                self.text_recognizer = pytesseract
            except Exception as e:
                logger.warning(f"Could not setup text recognizer: {e}")
                
        except Exception as e:
            logger.error(f"Error setting up video tools: {e}")
    
    def _load_platform_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific video SEO requirements."""
        return {
            "youtube": {
                "title_max_length": 100,
                "description_max_length": 5000,
                "optimal_duration": {"min": 600, "max": 1200},  # 10-20 minutes
                "thumbnail_specs": {"width": 1280, "height": 720, "aspect_ratio": "16:9"},
                "recommended_formats": [VideoFormat.MP4],
                "min_quality": VideoQuality.HD_720P,
                "keywords_focus": ["trending", "viral", "tutorial", "review"],
                "engagement_factors": ["watch_time", "comments", "likes", "shares"]
            },
            "tiktok": {
                "title_max_length": 150,
                "description_max_length": 2200,
                "optimal_duration": {"min": 15, "max": 60},  # 15-60 seconds
                "thumbnail_specs": {"width": 720, "height": 1280, "aspect_ratio": "9:16"},
                "recommended_formats": [VideoFormat.MP4],
                "min_quality": VideoQuality.HD_720P,
                "keywords_focus": ["viral", "trending", "challenge", "dance", "music"],
                "engagement_factors": ["completion_rate", "shares", "likes", "comments"]
            },
            "instagram": {
                "title_max_length": 125,
                "description_max_length": 2200,
                "optimal_duration": {"min": 15, "max": 90},  # 15-90 seconds
                "thumbnail_specs": {"width": 1080, "height": 1080, "aspect_ratio": "1:1"},
                "recommended_formats": [VideoFormat.MP4],
                "min_quality": VideoQuality.HD_720P,
                "keywords_focus": ["aesthetic", "lifestyle", "brand", "influencer"],
                "engagement_factors": ["likes", "comments", "saves", "shares"]
            },
            "facebook": {
                "title_max_length": 255,
                "description_max_length": 8000,
                "optimal_duration": {"min": 60, "max": 300},  # 1-5 minutes
                "thumbnail_specs": {"width": 1280, "height": 720, "aspect_ratio": "16:9"},
                "recommended_formats": [VideoFormat.MP4],
                "min_quality": VideoQuality.HD_720P,
                "keywords_focus": ["community", "family", "local", "business"],
                "engagement_factors": ["watch_time", "shares", "reactions", "comments"]
            },
            "linkedin": {
                "title_max_length": 150,
                "description_max_length": 3000,
                "optimal_duration": {"min": 30, "max": 300},  # 30 seconds - 5 minutes
                "thumbnail_specs": {"width": 1280, "height": 720, "aspect_ratio": "16:9"},
                "recommended_formats": [VideoFormat.MP4],
                "min_quality": VideoQuality.HD_720P,
                "keywords_focus": ["professional", "business", "career", "industry"],
                "engagement_factors": ["views", "comments", "shares", "clicks"]
            }
        }
    
    async def optimize_video_seo(
        self,
        video_file_path: str,
        config: VideoSEOConfig
    ) -> VideoSEOResult:
        """Optimize video content for SEO across platforms.
        
        Args:
            video_file_path: Path to video file
            config: Optimization configuration
            
        Returns:
            VideoSEOResult with comprehensive optimization
        """
        try:
            # Extract original metadata
            original_metadata = await self._extract_video_metadata(video_file_path)
            
            # Generate transcript if requested
            transcript = None
            if config.generate_transcript:
                transcript = await self._generate_video_transcript(video_file_path, config.language)
            
            # Analyze thumbnails if requested
            thumbnail_analysis = []
            if config.analyze_thumbnails:
                thumbnail_analysis = await self._analyze_video_thumbnails(video_file_path)
            
            # Optimize metadata
            optimized_metadata = await self._optimize_video_metadata(
                original_metadata, transcript, config
            )
            
            # Generate SEO content
            seo_title, seo_description = await self._generate_video_seo_content(
                optimized_metadata, transcript, thumbnail_analysis, config
            )
            
            # Extract keywords
            keywords = await self._extract_video_keywords(
                optimized_metadata, transcript, config
            )
            
            # Generate hashtags
            hashtags = await self._generate_video_hashtags(keywords, config)
            
            # Categorize content
            categories = await self._categorize_video_content(
                optimized_metadata, transcript, config
            )
            
            # Platform-specific optimizations
            platform_optimizations = await self._optimize_for_video_platforms(
                optimized_metadata, seo_title, seo_description, keywords, config
            )
            
            # Generate accessibility features
            accessibility_features = await self._generate_video_accessibility_features(
                transcript, optimized_metadata, config
            )
            
            # Generate schema markup
            schema_markup = await self._generate_video_schema_markup(
                optimized_metadata, transcript, config
            )
            
            # Calculate optimization score
            optimization_score = self._calculate_video_optimization_score(
                original_metadata, optimized_metadata, transcript, config
            )
            
            # Generate recommendations
            recommendations = self._generate_video_recommendations(
                original_metadata, optimized_metadata, thumbnail_analysis, config
            )
            
            return VideoSEOResult(
                original_metadata=original_metadata,
                optimized_metadata=optimized_metadata,
                transcript=transcript,
                thumbnail_analysis=thumbnail_analysis,
                seo_title=seo_title,
                seo_description=seo_description,
                keywords=keywords,
                hashtags=hashtags,
                categories=categories,
                platform_optimizations=platform_optimizations,
                accessibility_features=accessibility_features,
                schema_markup=schema_markup,
                optimization_score=optimization_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error optimizing video SEO: {e}")
            raise
    
    async def _extract_video_metadata(self, video_file_path: str) -> VideoMetadata:
        """Extract metadata from video file."""
        try:
            metadata = VideoMetadata()
            
            # Get file size
            metadata.file_size = os.path.getsize(video_file_path)
            
            # Determine format from extension
            file_extension = os.path.splitext(video_file_path)[1].lower()
            format_mapping = {
                '.mp4': VideoFormat.MP4,
                '.avi': VideoFormat.AVI,
                '.mov': VideoFormat.MOV,
                '.wmv': VideoFormat.WMV,
                '.flv': VideoFormat.FLV,
                '.webm': VideoFormat.WEBM,
                '.mkv': VideoFormat.MKV
            }
            metadata.format = format_mapping.get(file_extension, VideoFormat.MP4)
            
            # Use OpenCV to extract basic video info
            try:
                cap = cv2.VideoCapture(video_file_path)
                
                if cap.isOpened():
                    # Get video properties
                    metadata.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    metadata.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    metadata.fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    
                    if metadata.fps > 0:
                        metadata.duration = frame_count / metadata.fps
                    
                    # Determine quality
                    if metadata.height:
                        if metadata.height >= 2160:
                            metadata.quality = VideoQuality.UHD_4K
                        elif metadata.height >= 1440:
                            metadata.quality = VideoQuality.QHD_1440P
                        elif metadata.height >= 1080:
                            metadata.quality = VideoQuality.FHD_1080P
                        elif metadata.height >= 720:
                            metadata.quality = VideoQuality.HD_720P
                        else:
                            metadata.quality = VideoQuality.SD_480P
                    
                    # Calculate aspect ratio
                    if metadata.width and metadata.height:
                        ratio = metadata.width / metadata.height
                        if abs(ratio - 16/9) < 0.1:
                            metadata.aspect_ratio = "16:9"
                        elif abs(ratio - 4/3) < 0.1:
                            metadata.aspect_ratio = "4:3"
                        elif abs(ratio - 1) < 0.1:
                            metadata.aspect_ratio = "1:1"
                        elif abs(ratio - 9/16) < 0.1:
                            metadata.aspect_ratio = "9:16"
                        else:
                            metadata.aspect_ratio = f"{metadata.width}:{metadata.height}"
                
                cap.release()
                
            except Exception as cv_error:
                logger.warning(f"Error extracting video metadata with OpenCV: {cv_error}")
            
            # Try moviepy for additional metadata
            try:
                with mp.VideoFileClip(video_file_path) as clip:
                    if not metadata.duration:
                        metadata.duration = clip.duration
                    
                    if not metadata.width:
                        metadata.width, metadata.height = clip.size
                    
                    if not metadata.fps:
                        metadata.fps = clip.fps
                    
                    # Check for audio
                    metadata.has_audio = clip.audio is not None
                    
            except Exception as mp_error:
                logger.warning(f"Error extracting metadata with moviepy: {mp_error}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting video metadata: {e}")
            return VideoMetadata()
    
    async def _generate_video_transcript(
        self,
        video_file_path: str,
        language: str = "en"
    ) -> Optional[VideoTranscript]:
        """Generate transcript from video audio."""
        try:
            if not self.speech_recognizer:
                return None
            
            # Extract audio from video
            temp_audio_path = None
            try:
                with mp.VideoFileClip(video_file_path) as video:
                    if video.audio is None:
                        return None
                    
                    temp_audio_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
                    video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
                
                # Convert to format compatible with speech recognition
                audio = AudioSegment.from_wav(temp_audio_path)
                
                # Split audio into chunks for better recognition
                chunk_length_ms = 30000  # 30 seconds
                chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
                
                full_transcript = ""
                segments = []
                total_confidence = 0
                successful_chunks = 0
                
                for i, chunk in enumerate(chunks):
                    try:
                        # Save chunk to temporary file
                        chunk_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
                        chunk.export(chunk_path, format="wav")
                        
                        # Recognize speech
                        with sr.AudioFile(chunk_path) as source:
                            audio_data = self.speech_recognizer.record(source)
                        
                        try:
                            text = self.speech_recognizer.recognize_google(audio_data, language=language)
                            confidence = 0.8  # Google typically has good confidence
                        except sr.UnknownValueError:
                            try:
                                text = self.speech_recognizer.recognize_sphinx(audio_data)
                                confidence = 0.6
                            except:
                                continue
                        except sr.RequestError:
                            continue
                        
                        if text.strip():
                            full_transcript += text + " "
                            
                            segment = {
                                'text': text.strip(),
                                'start_time': i * 30.0,
                                'end_time': min((i + 1) * 30.0, len(audio) / 1000),
                                'confidence': confidence
                            }
                            segments.append(segment)
                            
                            total_confidence += confidence
                            successful_chunks += 1
                        
                        # Clean up chunk file
                        os.unlink(chunk_path)
                        
                    except Exception as chunk_error:
                        logger.warning(f"Error processing audio chunk {i}: {chunk_error}")
                        continue
                
                if successful_chunks > 0:
                    avg_confidence = total_confidence / successful_chunks
                    
                    return VideoTranscript(
                        full_text=full_transcript.strip(),
                        segments=segments,
                        confidence=avg_confidence,
                        language=language,
                        auto_generated=True
                    )
                
            finally:
                # Clean up temporary files
                if temp_audio_path and os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating video transcript: {e}")
            return None
    
    async def _analyze_video_thumbnails(
        self,
        video_file_path: str,
        num_thumbnails: int = 5
    ) -> List[ThumbnailAnalysis]:
        """Analyze video thumbnails for SEO optimization."""
        try:
            thumbnail_analyses = []
            
            # Extract frames for thumbnail analysis
            cap = cv2.VideoCapture(video_file_path)
            
            if not cap.isOpened():
                return []
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_positions = [int(total_frames * i / (num_thumbnails + 1)) for i in range(1, num_thumbnails + 1)]
            
            for i, frame_pos in enumerate(frame_positions):
                try:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                    ret, frame = cap.read()
                    
                    if not ret:
                        continue
                    
                    # Save frame as temporary image
                    temp_image_path = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False).name
                    cv2.imwrite(temp_image_path, frame)
                    
                    # Analyze thumbnail
                    analysis = await self._analyze_single_thumbnail(temp_image_path)
                    thumbnail_analyses.append(analysis)
                    
                    # Clean up
                    os.unlink(temp_image_path)
                    
                except Exception as frame_error:
                    logger.warning(f"Error analyzing frame {i}: {frame_error}")
                    continue
            
            cap.release()
            return thumbnail_analyses
            
        except Exception as e:
            logger.error(f"Error analyzing video thumbnails: {e}")
            return []
    
    async def _analyze_single_thumbnail(self, image_path: str) -> ThumbnailAnalysis:
        """Analyze a single thumbnail image."""
        try:
            # Basic image properties
            with Image.open(image_path) as img:
                width, height = img.size
                file_size = os.path.getsize(image_path)
                
                # Calculate aspect ratio
                ratio = width / height
                if abs(ratio - 16/9) < 0.1:
                    aspect_ratio = "16:9"
                elif abs(ratio - 4/3) < 0.1:
                    aspect_ratio = "4:3"
                elif abs(ratio - 1) < 0.1:
                    aspect_ratio = "1:1"
                elif abs(ratio - 9/16) < 0.1:
                    aspect_ratio = "9:16"
                else:
                    aspect_ratio = f"{width}:{height}"
                
                # Analyze brightness and contrast
                stat = ImageStat.Stat(img)
                brightness = sum(stat.mean) / len(stat.mean) / 255
                
                # Calculate contrast (standard deviation)
                contrast = sum(stat.stddev) / len(stat.stddev) / 255
                
                # Extract dominant colors
                dominant_colors = []
                try:
                    color_thief = ColorThief(image_path)
                    palette = color_thief.get_palette(color_count=3)
                    dominant_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette]
                except:
                    dominant_colors = ["#000000", "#808080", "#ffffff"]  # Default colors
                
                # Text detection
                has_text = False
                text_content = None
                try:
                    if self.text_recognizer:
                        text_content = self.text_recognizer.image_to_string(img)
                        has_text = len(text_content.strip()) > 0
                except:
                    pass
                
                # Calculate quality score based on various factors
                quality_score = self._calculate_thumbnail_quality_score(
                    width, height, brightness, contrast, file_size
                )
                
                # Calculate click potential
                click_potential = self._calculate_click_potential(
                    brightness, contrast, has_text, aspect_ratio
                )
                
                return ThumbnailAnalysis(
                    image_path=image_path,
                    width=width,
                    height=height,
                    aspect_ratio=aspect_ratio,
                    file_size=file_size,
                    dominant_colors=dominant_colors,
                    brightness=brightness,
                    contrast=contrast,
                    has_text=has_text,
                    text_content=text_content,
                    quality_score=quality_score,
                    click_potential=click_potential
                )
            
        except Exception as e:
            logger.error(f"Error analyzing single thumbnail: {e}")
            return ThumbnailAnalysis(
                image_path=image_path,
                width=0,
                height=0,
                aspect_ratio="unknown",
                file_size=0,
                dominant_colors=[],
                brightness=0.0,
                contrast=0.0,
                has_text=False
            )
    
    def _calculate_thumbnail_quality_score(
        self,
        width: int,
        height: int,
        brightness: float,
        contrast: float,
        file_size: int
    ) -> float:
        """Calculate thumbnail quality score."""
        try:
            score = 0.0
            
            # Resolution score (0-0.3)
            resolution = width * height
            if resolution >= 1280 * 720:  # HD or better
                score += 0.3
            elif resolution >= 640 * 480:  # Standard definition
                score += 0.2
            else:
                score += 0.1
            
            # Brightness score (0-0.2) - optimal around 0.4-0.7
            if 0.4 <= brightness <= 0.7:
                score += 0.2
            elif 0.3 <= brightness <= 0.8:
                score += 0.15
            else:
                score += 0.1
            
            # Contrast score (0-0.2) - higher contrast generally better
            if contrast > 0.3:
                score += 0.2
            elif contrast > 0.2:
                score += 0.15
            else:
                score += 0.1
            
            # File size score (0-0.3) - balance quality and loading speed
            size_mb = file_size / (1024 * 1024)
            if 0.1 <= size_mb <= 2.0:  # Optimal range
                score += 0.3
            elif size_mb <= 5.0:
                score += 0.2
            else:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating thumbnail quality score: {e}")
            return 0.5
    
    def _calculate_click_potential(
        self,
        brightness: float,
        contrast: float,
        has_text: bool,
        aspect_ratio: str
    ) -> float:
        """Calculate click potential based on thumbnail features."""
        try:
            potential = 0.0
            
            # Brightness factor (bright thumbnails often get more clicks)
            if 0.5 <= brightness <= 0.8:
                potential += 0.25
            elif 0.4 <= brightness <= 0.9:
                potential += 0.2
            else:
                potential += 0.1
            
            # Contrast factor (high contrast attracts attention)
            if contrast > 0.3:
                potential += 0.25
            elif contrast > 0.2:
                potential += 0.2
            else:
                potential += 0.1
            
            # Text factor (text can increase clicks if readable)
            if has_text:
                potential += 0.2
            else:
                potential += 0.1
            
            # Aspect ratio factor (platform-optimized ratios)
            if aspect_ratio in ["16:9", "1:1", "9:16"]:
                potential += 0.3
            else:
                potential += 0.15
            
            return min(potential, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating click potential: {e}")
            return 0.5
    
    async def _optimize_video_metadata(
        self,
        original_metadata: VideoMetadata,
        transcript: Optional[VideoTranscript],
        config: VideoSEOConfig
    ) -> VideoMetadata:
        """Optimize video metadata for SEO."""
        try:
            optimized = VideoMetadata()
            
            # Copy original metadata
            for field in original_metadata.__dataclass_fields__:
                setattr(optimized, field, getattr(original_metadata, field))
            
            # Enhance with transcript analysis
            if transcript and transcript.full_text:
                # Extract potential title from transcript
                if not optimized.title:
                    first_sentence = transcript.full_text.split('.')[0]
                    if len(first_sentence) <= config.max_title_length:
                        optimized.title = first_sentence.strip()
                
                # Generate description from transcript
                if not optimized.description:
                    summary = transcript.full_text[:config.max_description_length]
                    optimized.description = summary + "..." if len(transcript.full_text) > config.max_description_length else summary
                
                # Add subtitle availability
                optimized.has_subtitles = True
            
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing video metadata: {e}")
            return original_metadata
    
    async def _generate_video_seo_content(
        self,
        metadata: VideoMetadata,
        transcript: Optional[VideoTranscript],
        thumbnail_analysis: List[ThumbnailAnalysis],
        config: VideoSEOConfig
    ) -> Tuple[str, str]:
        """Generate SEO-optimized title and description for video."""
        try:
            # Generate title
            title_parts = []
            
            if metadata.title:
                title_parts.append(metadata.title)
            elif transcript and transcript.full_text:
                # Extract key topics from transcript
                topics = self._extract_topics_from_transcript(transcript.full_text)
                if topics:
                    title_parts.append(f"About {topics[0]}")
            
            # Add content type indicator
            if config.content_type == "tutorial":
                title_parts.append("Tutorial")
            elif config.content_type == "review":
                title_parts.append("Review")
            elif config.content_type == "entertainment":
                title_parts.append("Video")
            
            seo_title = " - ".join(title_parts) if title_parts else "Video Content"
            
            # Ensure title length compliance
            if len(seo_title) > config.max_title_length:
                seo_title = seo_title[:config.max_title_length - 3] + "..."
            
            # Generate description
            description_parts = []
            
            if metadata.description:
                description_parts.append(metadata.description)
            elif transcript and transcript.full_text:
                # Create summary from transcript
                summary_length = min(500, config.max_description_length // 2)
                summary = transcript.full_text[:summary_length]
                description_parts.append(f"In this video: {summary}...")
            
            # Add video details
            if metadata.duration:
                minutes = int(metadata.duration // 60)
                seconds = int(metadata.duration % 60)
                description_parts.append(f"Duration: {minutes}:{seconds:02d}")
            
            if metadata.quality:
                description_parts.append(f"Quality: {metadata.quality.value}")
            
            # Add keywords naturally
            if config.target_keywords:
                keyword_section = f"Keywords: {', '.join(config.target_keywords[:5])}"
                description_parts.append(keyword_section)
            
            seo_description = "\n\n".join(description_parts) if description_parts else "Quality video content"
            
            # Ensure description length compliance
            if len(seo_description) > config.max_description_length:
                seo_description = seo_description[:config.max_description_length - 3] + "..."
            
            return seo_title, seo_description
            
        except Exception as e:
            logger.error(f"Error generating video SEO content: {e}")
            return "Video Content", "Quality video content"
    
    def _extract_topics_from_transcript(self, transcript_text: str) -> List[str]:
        """Extract key topics from video transcript."""
        try:
            # Simple topic extraction
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', transcript_text)
            
            # Filter common words
            stop_words = {'The', 'This', 'That', 'They', 'There', 'Then', 'When', 'Where', 'What', 'Who', 'Why', 'How'}
            topics = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Return most frequent topics
            from collections import Counter
            topic_counts = Counter(topics)
            return [topic for topic, count in topic_counts.most_common(5)]
            
        except Exception as e:
            logger.error(f"Error extracting topics from transcript: {e}")
            return []
    
    async def _extract_video_keywords(
        self,
        metadata: VideoMetadata,
        transcript: Optional[VideoTranscript],
        config: VideoSEOConfig
    ) -> List[str]:
        """Extract SEO keywords from video content."""
        try:
            keywords = set()
            
            # Add target keywords
            keywords.update(config.target_keywords)
            
            # Content type keywords
            content_type_keywords = {
                "tutorial": ["tutorial", "how to", "guide", "learn", "step by step"],
                "review": ["review", "opinion", "rating", "comparison", "pros and cons"],
                "entertainment": ["funny", "entertaining", "fun", "comedy", "viral"],
                "educational": ["education", "learning", "facts", "information", "knowledge"],
                "commercial": ["product", "brand", "business", "commercial", "marketing"]
            }
            
            if config.content_type in content_type_keywords:
                keywords.update(content_type_keywords[config.content_type])
            
            # Duration-based keywords
            if metadata.duration:
                if metadata.duration < 60:
                    keywords.update(["short", "quick", "brief"])
                elif metadata.duration > 600:
                    keywords.update(["long form", "detailed", "comprehensive"])
                else:
                    keywords.update(["medium length", "concise"])
            
            # Quality-based keywords
            if metadata.quality:
                if metadata.quality in [VideoQuality.FHD_1080P, VideoQuality.UHD_4K]:
                    keywords.update(["high quality", "HD", "crisp"])
            
            # Transcript-based keywords
            if transcript and transcript.full_text:
                transcript_keywords = self._extract_keywords_from_text(transcript.full_text)
                keywords.update(transcript_keywords)
            
            # Platform-specific keywords
            for platform in config.target_platforms:
                platform_focus = self.platform_requirements.get(platform, {}).get('keywords_focus', [])
                keywords.update(platform_focus)
            
            return list(keywords)[:25]  # Limit to top 25 keywords
            
        except Exception as e:
            logger.error(f"Error extracting video keywords: {e}")
            return []
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text content."""
        try:
            # Simple keyword extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Filter stop words
            stop_words = {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
                'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                'can', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'when',
                'where', 'why', 'how', 'not', 'no', 'yes', 'very', 'really', 'quite'
            }
            
            keywords = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Return most frequent keywords
            from collections import Counter
            keyword_counts = Counter(keywords)
            return [keyword for keyword, count in keyword_counts.most_common(15)]
            
        except Exception as e:
            logger.error(f"Error extracting keywords from text: {e}")
            return []
    
    async def _generate_video_hashtags(
        self,
        keywords: List[str],
        config: VideoSEOConfig
    ) -> List[str]:
        """Generate hashtags from video keywords."""
        try:
            hashtags = []
            
            # Convert keywords to hashtags
            for keyword in keywords[:20]:  # Limit to 20 hashtags
                # Clean keyword for hashtag
                hashtag = re.sub(r'[^a-zA-Z0-9]', '', keyword)
                if len(hashtag) > 2:
                    hashtags.append(f"#{hashtag}")
            
            # Add content type hashtags
            content_hashtags = {
                "tutorial": ["#tutorial", "#howto", "#guide", "#learn"],
                "review": ["#review", "#opinion", "#rating"],
                "entertainment": ["#entertainment", "#fun", "#viral"],
                "educational": ["#education", "#learning", "#facts"],
                "commercial": ["#business", "#marketing", "#brand"]
            }
            
            if config.content_type in content_hashtags:
                hashtags.extend(content_hashtags[config.content_type])
            
            # Add platform-specific hashtags
            if "youtube" in config.target_platforms:
                hashtags.extend(["#youtube", "#youtuber", "#subscribe"])
            if "tiktok" in config.target_platforms:
                hashtags.extend(["#tiktok", "#viral", "#fyp"])
            if "instagram" in config.target_platforms:
                hashtags.extend(["#instagram", "#reels", "#viral"])
            
            return hashtags[:30]  # Limit to 30 hashtags
            
        except Exception as e:
            logger.error(f"Error generating video hashtags: {e}")
            return []
    
    async def _categorize_video_content(
        self,
        metadata: VideoMetadata,
        transcript: Optional[VideoTranscript],
        config: VideoSEOConfig
    ) -> List[str]:
        """Categorize video content for better discoverability."""
        try:
            categories = []
            
            # Primary category based on content type
            primary_categories = {
                "tutorial": "Education",
                "review": "Entertainment",
                "entertainment": "Entertainment",
                "educational": "Education",
                "commercial": "Business"
            }
            
            if config.content_type in primary_categories:
                categories.append(primary_categories[config.content_type])
            
            # Duration-based categories
            if metadata.duration:
                if metadata.duration < 60:
                    categories.append("Short Form")
                elif metadata.duration > 600:
                    categories.append("Long Form")
            
            # Content analysis from transcript
            if transcript and transcript.full_text:
                content_lower = transcript.full_text.lower()
                
                # Technology category
                tech_keywords = ["technology", "software", "app", "digital", "computer", "tech"]
                if any(keyword in content_lower for keyword in tech_keywords):
                    categories.append("Technology")
                
                # Music category
                music_keywords = ["music", "song", "album", "artist", "band", "musician"]
                if any(keyword in content_lower for keyword in music_keywords):
                    categories.append("Music")
                
                # Gaming category
                gaming_keywords = ["game", "gaming", "player", "level", "character", "gameplay"]
                if any(keyword in content_lower for keyword in gaming_keywords):
                    categories.append("Gaming")
                
                # Lifestyle category
                lifestyle_keywords = ["lifestyle", "travel", "food", "fashion", "beauty", "health"]
                if any(keyword in content_lower for keyword in lifestyle_keywords):
                    categories.append("Lifestyle")
            
            return list(set(categories))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error categorizing video content: {e}")
            return ["General"]
    
    async def _optimize_for_video_platforms(
        self,
        metadata: VideoMetadata,
        title: str,
        description: str,
        keywords: List[str],
        config: VideoSEOConfig
    ) -> Dict[str, Dict[str, Any]]:
        """Optimize video content for specific platforms."""
        try:
            optimizations = {}
            
            for platform in config.target_platforms:
                platform_req = self.platform_requirements.get(platform, {})
                
                # Optimize title length
                max_title_length = platform_req.get('title_max_length', 100)
                optimized_title = title[:max_title_length] if len(title) > max_title_length else title
                
                # Optimize description length
                max_desc_length = platform_req.get('description_max_length', 5000)
                optimized_desc = description[:max_desc_length] if len(description) > max_desc_length else description
                
                # Duration recommendations
                optimal_duration = platform_req.get('optimal_duration', {})
                duration_status = "optimal"
                
                if metadata.duration:
                    if metadata.duration < optimal_duration.get('min', 0):
                        duration_status = "too_short"
                    elif metadata.duration > optimal_duration.get('max', float('inf')):
                        duration_status = "too_long"
                
                # Quality status
                min_quality = platform_req.get('min_quality', VideoQuality.SD_480P)
                quality_status = "adequate"
                
                if metadata.quality:
                    quality_order = [VideoQuality.SD_480P, VideoQuality.HD_720P, VideoQuality.FHD_1080P, VideoQuality.QHD_1440P, VideoQuality.UHD_4K]
                    if quality_order.index(metadata.quality) < quality_order.index(min_quality):
                        quality_status = "below_minimum"
                    elif quality_order.index(metadata.quality) >= quality_order.index(VideoQuality.FHD_1080P):
                        quality_status = "excellent"
                
                # Thumbnail recommendations
                thumbnail_specs = platform_req.get('thumbnail_specs', {})
                
                optimizations[platform] = {
                    'optimized_title': optimized_title,
                    'optimized_description': optimized_desc,
                    'duration_status': duration_status,
                    'quality_status': quality_status,
                    'recommended_thumbnail_size': f"{thumbnail_specs.get('width', 1280)}x{thumbnail_specs.get('height', 720)}",
                    'recommended_aspect_ratio': thumbnail_specs.get('aspect_ratio', '16:9'),
                    'engagement_factors': platform_req.get('engagement_factors', []),
                    'focused_keywords': [kw for kw in keywords if any(focus in kw for focus in platform_req.get('keywords_focus', []))]
                }
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Error optimizing for video platforms: {e}")
            return {}
    
    async def _generate_video_accessibility_features(
        self,
        transcript: Optional[VideoTranscript],
        metadata: VideoMetadata,
        config: VideoSEOConfig
    ) -> Dict[str, Any]:
        """Generate accessibility features for video content."""
        try:
            accessibility = {}
            
            # Transcript availability
            accessibility['has_transcript'] = transcript is not None
            
            if transcript:
                accessibility['transcript_quality'] = transcript.confidence
                accessibility['transcript_language'] = transcript.language
                accessibility['word_count'] = len(transcript.full_text.split())
                accessibility['auto_generated'] = transcript.auto_generated
                
                # Time-coded captions
                if transcript.segments:
                    accessibility['has_captions'] = True
                    accessibility['caption_format'] = "SRT"
                    accessibility['segment_count'] = len(transcript.segments)
            
            # Audio accessibility
            accessibility['has_audio'] = metadata.has_audio
            accessibility['has_subtitles'] = metadata.has_subtitles
            
            # Visual accessibility
            accessibility['visual_features'] = {
                'has_high_contrast': True,  # Would be determined by thumbnail analysis
                'readable_text_size': True,  # Would be determined by content analysis
                'color_blind_friendly': True  # Would be determined by color analysis
            }
            
            # Content warnings (placeholder - would use content analysis)
            accessibility['content_warnings'] = []
            
            # Duration accessibility
            if metadata.duration:
                if metadata.duration > 1800:  # 30 minutes
                    accessibility['long_content_warning'] = True
                    accessibility['suggested_breaks'] = list(range(900, int(metadata.duration), 900))  # Every 15 minutes
            
            return accessibility
            
        except Exception as e:
            logger.error(f"Error generating video accessibility features: {e}")
            return {}
    
    async def _generate_video_schema_markup(
        self,
        metadata: VideoMetadata,
        transcript: Optional[VideoTranscript],
        config: VideoSEOConfig
    ) -> Dict[str, Any]:
        """Generate schema.org markup for video content."""
        try:
            schema = {
                "@context": "https://schema.org",
                "@type": "VideoObject"
            }
            
            # Basic properties
            if metadata.title:
                schema["name"] = metadata.title
            
            if metadata.description:
                schema["description"] = metadata.description
            
            if metadata.duration:
                # Convert to ISO 8601 duration format
                duration_seconds = int(metadata.duration)
                hours = duration_seconds // 3600
                minutes = (duration_seconds % 3600) // 60
                seconds = duration_seconds % 60
                
                if hours > 0:
                    schema["duration"] = f"PT{hours}H{minutes}M{seconds}S"
                else:
                    schema["duration"] = f"PT{minutes}M{seconds}S"
            
            # Technical properties
            if metadata.width and metadata.height:
                schema["width"] = metadata.width
                schema["height"] = metadata.height
                schema["videoQuality"] = metadata.quality.value if metadata.quality else "HD"
            
            if metadata.format:
                schema["encodingFormat"] = f"video/{metadata.format.value}"
            
            # Content properties
            schema["uploadDate"] = datetime.utcnow().isoformat()
            
            # Transcript
            if transcript:
                schema["transcript"] = {
                    "@type": "MediaObject",
                    "encodingFormat": "text/plain",
                    "text": transcript.full_text
                }
            
            # Accessibility
            accessibility_features = []
            if transcript:
                accessibility_features.extend(["transcript", "captions"])
            if metadata.has_audio:
                accessibility_features.append("audioDescription")
            
            if accessibility_features:
                schema["accessibilityFeature"] = accessibility_features
                schema["accessibilityHazard"] = "none"
                schema["accessibilityControl"] = ["fullKeyboardControl", "fullMouseControl"]
            
            return schema
            
        except Exception as e:
            logger.error(f"Error generating video schema markup: {e}")
            return {}
    
    def _calculate_video_optimization_score(
        self,
        original_metadata: VideoMetadata,
        optimized_metadata: VideoMetadata,
        transcript: Optional[VideoTranscript],
        config: VideoSEOConfig
    ) -> float:
        """Calculate overall video optimization score."""
        try:
            score_components = []
            
            # Metadata completeness (0-1)
            metadata_fields = ['title', 'description', 'duration', 'width', 'height']
            present_fields = sum(1 for field in metadata_fields if getattr(optimized_metadata, field))
            metadata_score = present_fields / len(metadata_fields)
            score_components.append(metadata_score * 0.25)
            
            # Video quality (0-1)
            quality_score = 0.5  # Base score
            if optimized_metadata.quality:
                quality_mapping = {
                    VideoQuality.SD_480P: 0.4,
                    VideoQuality.HD_720P: 0.6,
                    VideoQuality.FHD_1080P: 0.8,
                    VideoQuality.QHD_1440P: 0.9,
                    VideoQuality.UHD_4K: 1.0
                }
                quality_score = quality_mapping.get(optimized_metadata.quality, 0.5)
            score_components.append(quality_score * 0.2)
            
            # Transcript availability (0-1)
            transcript_score = 0.0
            if transcript:
                transcript_score = min(transcript.confidence, 1.0)
            score_components.append(transcript_score * 0.2)
            
            # Platform optimization (0-1)
            platform_score = len(config.target_platforms) / 4  # Normalize to 4 platforms max
            score_components.append(min(platform_score, 1.0) * 0.15)
            
            # Content optimization (0-1)
            content_score = 0.7  # Base score for having content
            if config.target_keywords:
                content_score += 0.2
            if optimized_metadata.has_audio:
                content_score += 0.1
            score_components.append(min(content_score, 1.0) * 0.2)
            
            return sum(score_components)
            
        except Exception as e:
            logger.error(f"Error calculating video optimization score: {e}")
            return 0.0
    
    def _generate_video_recommendations(
        self,
        original_metadata: VideoMetadata,
        optimized_metadata: VideoMetadata,
        thumbnail_analysis: List[ThumbnailAnalysis],
        config: VideoSEOConfig
    ) -> List[str]:
        """Generate video optimization recommendations."""
        try:
            recommendations = []
            
            # Quality recommendations
            if optimized_metadata.quality and optimized_metadata.quality == VideoQuality.SD_480P:
                recommendations.append("Consider upgrading to HD (720p) or higher for better quality")
            
            # Duration recommendations
            if optimized_metadata.duration:
                if optimized_metadata.duration < 30:
                    recommendations.append("Video might be too short for some platforms - consider adding more content")
                elif optimized_metadata.duration > 3600:  # 1 hour
                    recommendations.append("Consider breaking long content into shorter segments for better engagement")
            
            # Audio recommendations
            if not optimized_metadata.has_audio:
                recommendations.append("Consider adding background music or narration for better engagement")
            
            # Transcript recommendations
            if config.generate_transcript and not optimized_metadata.has_subtitles:
                recommendations.append("Add captions/subtitles for better accessibility and SEO")
            
            # Thumbnail recommendations
            if thumbnail_analysis:
                avg_quality = sum(t.quality_score for t in thumbnail_analysis) / len(thumbnail_analysis)
                if avg_quality < 0.6:
                    recommendations.append("Improve thumbnail quality - use higher resolution and better composition")
                
                avg_click_potential = sum(t.click_potential for t in thumbnail_analysis) / len(thumbnail_analysis)
                if avg_click_potential < 0.6:
                    recommendations.append("Optimize thumbnails for better click-through rates - use contrasting colors and clear text")
            
            # Platform-specific recommendations
            for platform in config.target_platforms:
                platform_req = self.platform_requirements.get(platform, {})
                optimal_duration = platform_req.get('optimal_duration', {})
                
                if optimized_metadata.duration:
                    if optimized_metadata.duration < optimal_duration.get('min', 0):
                        recommendations.append(f"Video is shorter than optimal for {platform} ({optimal_duration['min']}s minimum)")
                    elif optimized_metadata.duration > optimal_duration.get('max', float('inf')):
                        recommendations.append(f"Video is longer than optimal for {platform} ({optimal_duration['max']}s maximum)")
            
            # SEO recommendations
            if not config.target_keywords:
                recommendations.append("Add target keywords for better SEO optimization")
            
            if not optimized_metadata.title:
                recommendations.append("Add a compelling title for better discoverability")
            
            if not optimized_metadata.description:
                recommendations.append("Add a detailed description with keywords for better SEO")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating video recommendations: {e}")
            return []

    async def batch_optimize_videos(
        self,
        video_files: List[str],
        configs: List[VideoSEOConfig]
    ) -> List[VideoSEOResult]:
        """Optimize multiple videos in batch."""
        try:
            tasks = [
                self.optimize_video_seo(video_file, config)
                for video_file, config in zip(video_files, configs)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error optimizing video {i}: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch video optimization: {e}")
            return []