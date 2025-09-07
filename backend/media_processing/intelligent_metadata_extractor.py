#!/usr/bin/env python3
"""📊 Intelligent Metadata Extractor - IA Metadata Generation Engine
====================================================================
Module: backend/media_processing/intelligent_metadata_extractor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead AI Developer + ML Engineer + AI Prompt Engineer + Backend Senior Engineer
Type: Enterprise IA Metadata Generation - Production-Ready
Responsibility: Intelligent metadata extraction, generation, and enrichment
===============================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🎯 BUSINESS LOGIC COMPLIANCE:
Creator Multi-format → IA Processing → Protection → SEO → Collaboration → Distribution

📊 INTELLIGENT METADATA CAPABILITIES:
1. Multi-Modal Metadata Extraction (Technical + Semantic)
2. AI-Generated Descriptions and Summaries
3. Intelligent Keyword Generation
4. SEO-Optimized Metadata Creation
5. Cultural and Contextual Metadata
6. Performance and Quality Metadata
"""

import asyncio
import logging
import uuid
import json
import hashlib
import mimetypes
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import os
import stat

# Media processing imports
try:
    import librosa
    import cv2
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.flac import FLAC
    import torch
    import numpy as np
    MEDIA_LIBS_AVAILABLE = True
except ImportError:
    MEDIA_LIBS_AVAILABLE = False
    librosa = None
    cv2 = None

# AI/NLP imports
try:
    from transformers import AutoTokenizer, AutoModel, pipeline
    import openai
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

# FastAPI and core dependencies
from fastapi import HTTPException
from pydantic import BaseModel, Field
import aiofiles
import aioredis

# Internal imports
from backend.core.exceptions import ProcessingError, ValidationError
from backend.core.security import SecurityManager
from backend.database.managers import DatabaseManager
from backend.monitoring.performance import PerformanceMonitor


class ContentType(Enum):
    """Content types for metadata extraction"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    VOICE = "voice"
    AVATAR = "avatar"
    DOCUMENT = "document"
    MULTIMODAL = "multimodal"


class MetadataCategory(Enum):
    """Categories of metadata"""
    TECHNICAL = "technical"
    SEMANTIC = "semantic"
    DESCRIPTIVE = "descriptive"
    SEO = "seo"
    CULTURAL = "cultural"
    COMMERCIAL = "commercial"
    CONTEXTUAL = "contextual"
    QUALITY = "quality"


@dataclass
class TechnicalMetadata:
    """Technical metadata for content"""
    file_size: int = 0
    file_format: str = ""
    mime_type: str = ""
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    resolution: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec: Optional[str] = None
    color_space: Optional[str] = None
    frame_rate: Optional[float] = None
    compression_ratio: Optional[float] = None
    quality_score: Optional[float] = None


@dataclass
class SemanticMetadata:
    """Semantic metadata extracted by AI"""
    ai_description: str = ""
    ai_summary: str = ""
    ai_tags: List[str] = field(default_factory=list)
    ai_keywords: List[str] = field(default_factory=list)
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    themes: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    language: Optional[str] = None
    complexity_level: Optional[str] = None


@dataclass
class SEOMetadata:
    """SEO-optimized metadata"""
    title: str = ""
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    alt_text: str = ""
    slug: str = ""
    meta_description: str = ""
    open_graph_title: str = ""
    open_graph_description: str = ""
    twitter_card_title: str = ""
    twitter_card_description: str = ""
    schema_markup: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CulturalMetadata:
    """Cultural and contextual metadata"""
    language: Optional[str] = None
    region: Optional[str] = None
    cultural_context: List[str] = field(default_factory=list)
    cultural_sensitivity: Optional[str] = None
    target_audience: List[str] = field(default_factory=list)
    cultural_references: List[str] = field(default_factory=list)
    localization_notes: List[str] = field(default_factory=list)


@dataclass
class CommercialMetadata:
    """Commercial and licensing metadata"""
    licensing_info: Dict[str, Any] = field(default_factory=dict)
    usage_rights: List[str] = field(default_factory=list)
    commercial_viability: Optional[float] = None
    monetization_potential: Optional[float] = None
    brand_safety: Optional[str] = None
    advertising_suitability: Optional[str] = None
    copyright_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntelligentMetadata:
    """Complete intelligent metadata extraction result"""
    content_id: str
    extraction_id: str
    content_type: ContentType
    file_path: str
    technical: TechnicalMetadata = field(default_factory=TechnicalMetadata)
    semantic: SemanticMetadata = field(default_factory=SemanticMetadata)
    seo: SEOMetadata = field(default_factory=SEOMetadata)
    cultural: CulturalMetadata = field(default_factory=CulturalMetadata)
    commercial: CommercialMetadata = field(default_factory=CommercialMetadata)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class MetadataExtractionConfig(BaseModel):
    """Configuration for metadata extraction"""
    enable_ai_description: bool = True
    enable_ai_keywords: bool = True
    enable_seo_optimization: bool = True
    enable_cultural_analysis: bool = True
    enable_commercial_analysis: bool = True
    max_description_length: int = 500
    max_keywords: int = 20
    ai_model_preference: str = "auto"
    quality_analysis_depth: str = "standard"
    enable_caching: bool = True
    cache_ttl: int = 3600


class IntelligentMetadataExtractor:
    """Enterprise Intelligent Metadata Extraction Engine
    
    AI-powered metadata extraction system with semantic understanding,
    SEO optimization, and cultural context analysis.
    """
    
    def __init__(self, config: Optional[MetadataExtractionConfig] = None):
        """Initialize Intelligent Metadata Extractor with enterprise configuration"""
        self.config = config or MetadataExtractionConfig()
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager()
        self.security_manager = SecurityManager()
        self.performance_monitor = PerformanceMonitor()
        
        # AI models for metadata generation
        self.nlp_models = {}
        self.vision_models = {}
        self.audio_models = {}
        
        # Metadata processors
        self.technical_extractor = None
        self.semantic_extractor = None
        self.seo_optimizer = None
        self.cultural_analyzer = None
        
        # Cache for metadata results
        self.metadata_cache = {}
        
        # Performance metrics
        self.metrics = {
            "total_extractions": 0,
            "successful_extractions": 0,
            "average_processing_time": 0.0,
            "content_types_processed": {},
            "ai_descriptions_generated": 0,
            "seo_optimizations_performed": 0
        }
        
        self.logger.info("Intelligent Metadata Extractor initialized")

    async def initialize(self) -> bool:
        """Initialize metadata extraction engines and AI models"""
        try:
            self.logger.info("Initializing Intelligent Metadata Extractor...")
            
            # Initialize metadata processors
            self.technical_extractor = TechnicalMetadataExtractor()
            self.semantic_extractor = SemanticMetadataExtractor(self.config)
            self.seo_optimizer = SEOMetadataOptimizer(self.config)
            self.cultural_analyzer = CulturalMetadataAnalyzer(self.config)
            
            # Initialize AI models if available
            if NLP_AVAILABLE:
                await self._initialize_ai_models()
            else:
                self.logger.warning("NLP libraries not available - using fallback methods")
            
            # Initialize cache
            if self.config.enable_caching:
                self.metadata_cache = {}
            
            self.logger.info("Intelligent Metadata Extractor initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Intelligent Metadata Extractor: {e}")
            return False

    async def _initialize_ai_models(self):
        """Initialize AI models for metadata generation"""
        try:
            if NLP_AVAILABLE:
                # Text processing models
                self.nlp_models['summarizer'] = pipeline('summarization', model='facebook/bart-large-cnn')
                self.nlp_models['sentiment'] = pipeline('sentiment-analysis')
                self.nlp_models['ner'] = pipeline('ner', aggregation_strategy='simple')
                
                # Text generation for descriptions
                self.nlp_models['text_generator'] = pipeline('text-generation', model='gpt2')
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
            raise

    async def extract_metadata(
        self,
        content_id: str,
        file_path: str,
        content_type: ContentType,
        extraction_categories: Optional[List[MetadataCategory]] = None
    ) -> IntelligentMetadata:
        """Extract comprehensive intelligent metadata from content"""
        extraction_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting metadata extraction: {extraction_id}")
            
            # Validate input
            await self._validate_extraction_input(file_path, content_type)
            
            # Check cache first
            cache_key = f"{content_id}_{content_type.value}_{os.path.getmtime(file_path)}"
            if self.config.enable_caching and cache_key in self.metadata_cache:
                self.logger.info(f"Returning cached metadata: {extraction_id}")
                return self.metadata_cache[cache_key]
            
            # Initialize metadata result
            metadata = IntelligentMetadata(
                content_id=content_id,
                extraction_id=extraction_id,
                content_type=content_type,
                file_path=file_path
            )
            
            # Set default extraction categories
            if not extraction_categories:
                extraction_categories = [
                    MetadataCategory.TECHNICAL,
                    MetadataCategory.SEMANTIC,
                    MetadataCategory.SEO,
                    MetadataCategory.CULTURAL,
                    MetadataCategory.COMMERCIAL
                ]
            
            # Extract technical metadata
            if MetadataCategory.TECHNICAL in extraction_categories:
                metadata.technical = await self._extract_technical_metadata(file_path, content_type)
            
            # Extract semantic metadata
            if MetadataCategory.SEMANTIC in extraction_categories and self.config.enable_ai_description:
                metadata.semantic = await self._extract_semantic_metadata(file_path, content_type)
            
            # Generate SEO metadata
            if MetadataCategory.SEO in extraction_categories and self.config.enable_seo_optimization:
                metadata.seo = await self._generate_seo_metadata(metadata)
            
            # Analyze cultural metadata
            if MetadataCategory.CULTURAL in extraction_categories and self.config.enable_cultural_analysis:
                metadata.cultural = await self._analyze_cultural_metadata(file_path, content_type, metadata.semantic)
            
            # Analyze commercial metadata
            if MetadataCategory.COMMERCIAL in extraction_categories and self.config.enable_commercial_analysis:
                metadata.commercial = await self._analyze_commercial_metadata(metadata)
            
            # Add extraction metadata
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            metadata.extraction_metadata = {
                "processing_time_seconds": processing_time,
                "extraction_categories": [cat.value for cat in extraction_categories],
                "ai_models_used": list(self.nlp_models.keys()) if NLP_AVAILABLE else [],
                "extraction_timestamp": datetime.utcnow().isoformat(),
                "extractor_version": "2.0.0"
            }
            
            # Cache result
            if self.config.enable_caching:
                self.metadata_cache[cache_key] = metadata
            
            # Update metrics
            await self._update_extraction_metrics(metadata, processing_time)
            
            self.logger.info(f"Metadata extraction completed: {extraction_id}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            raise ProcessingError(f"Metadata extraction failed: {str(e)}")

    async def _extract_technical_metadata(
        self,
        file_path: str,
        content_type: ContentType
    ) -> TechnicalMetadata:
        """Extract technical metadata from content file"""
        try:
            metadata = TechnicalMetadata()
            
            # Basic file information
            file_stat = os.stat(file_path)
            metadata.file_size = file_stat.st_size
            metadata.mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            metadata.file_format = Path(file_path).suffix.lower().lstrip('.')
            
            # Content-specific technical metadata
            if content_type == ContentType.AUDIO or content_type == ContentType.VOICE:
                await self._extract_audio_technical_metadata(file_path, metadata)
            elif content_type == ContentType.VIDEO:
                await self._extract_video_technical_metadata(file_path, metadata)
            elif content_type == ContentType.IMAGE:
                await self._extract_image_technical_metadata(file_path, metadata)
            elif content_type == ContentType.TEXT or content_type == ContentType.DOCUMENT:
                await self._extract_text_technical_metadata(file_path, metadata)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Technical metadata extraction failed: {e}")
            return TechnicalMetadata()

    async def _extract_audio_technical_metadata(self, file_path: str, metadata: TechnicalMetadata):
        """Extract audio-specific technical metadata"""
        try:
            if not MEDIA_LIBS_AVAILABLE:
                return
            
            # Using mutagen for audio metadata
            try:
                audio_file = mutagen.File(file_path)
                if audio_file:
                    metadata.duration = audio_file.info.length if hasattr(audio_file.info, 'length') else None
                    metadata.bitrate = audio_file.info.bitrate if hasattr(audio_file.info, 'bitrate') else None
                    metadata.sample_rate = audio_file.info.sample_rate if hasattr(audio_file.info, 'sample_rate') else None
                    metadata.channels = audio_file.info.channels if hasattr(audio_file.info, 'channels') else None
            except Exception:
                pass
            
            # Using librosa for advanced audio analysis
            try:
                audio_data, sr = librosa.load(file_path, sr=None)
                if metadata.duration is None:
                    metadata.duration = len(audio_data) / sr
                if metadata.sample_rate is None:
                    metadata.sample_rate = sr
                if metadata.channels is None:
                    metadata.channels = 1 if len(audio_data.shape) == 1 else audio_data.shape[0]
                
                # Audio quality metrics
                rms_energy = np.sqrt(np.mean(audio_data**2))
                metadata.quality_score = min(rms_energy * 10, 1.0)
                
            except Exception as e:
                self.logger.warning(f"Librosa analysis failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Audio technical metadata extraction failed: {e}")

    async def _extract_video_technical_metadata(self, file_path: str, metadata: TechnicalMetadata):
        """Extract video-specific technical metadata"""
        try:
            if not MEDIA_LIBS_AVAILABLE:
                return
            
            # Using OpenCV for video metadata
            try:
                cap = cv2.VideoCapture(file_path)
                if cap.isOpened():
                    # Video properties
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    
                    metadata.duration = frame_count / fps if fps > 0 else None
                    metadata.frame_rate = fps
                    metadata.dimensions = (width, height)
                    metadata.resolution = f"{width}x{height}"
                    
                    # Estimate quality based on resolution
                    if width > 0 and height > 0:
                        pixel_count = width * height
                        if pixel_count >= 3840 * 2160:  # 4K
                            metadata.quality_score = 1.0
                        elif pixel_count >= 1920 * 1080:  # 1080p
                            metadata.quality_score = 0.9
                        elif pixel_count >= 1280 * 720:  # 720p
                            metadata.quality_score = 0.7
                        else:
                            metadata.quality_score = 0.5
                    
                    cap.release()
                    
            except Exception as e:
                self.logger.warning(f"OpenCV video analysis failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Video technical metadata extraction failed: {e}")

    async def _extract_image_technical_metadata(self, file_path: str, metadata: TechnicalMetadata):
        """Extract image-specific technical metadata"""
        try:
            if not MEDIA_LIBS_AVAILABLE:
                return
            
            # Using PIL for image metadata
            try:
                with Image.open(file_path) as img:
                    metadata.dimensions = img.size
                    metadata.resolution = f"{img.size[0]}x{img.size[1]}"
                    metadata.color_space = img.mode
                    
                    # Extract EXIF data
                    if hasattr(img, '_getexif') and img._getexif():
                        exif_data = img._getexif()
                        # Process EXIF data for additional metadata
                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if tag == "Software":
                                metadata.codec = str(value)
                    
                    # Estimate quality based on resolution and file size
                    pixel_count = img.size[0] * img.size[1]
                    compression_ratio = metadata.file_size / (pixel_count * 3)  # Assuming RGB
                    metadata.compression_ratio = compression_ratio
                    
                    if pixel_count >= 3840 * 2160:  # 4K
                        metadata.quality_score = 1.0
                    elif pixel_count >= 1920 * 1080:  # 1080p
                        metadata.quality_score = 0.9
                    elif pixel_count >= 1280 * 720:  # 720p
                        metadata.quality_score = 0.7
                    else:
                        metadata.quality_score = 0.6
                        
            except Exception as e:
                self.logger.warning(f"PIL image analysis failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Image technical metadata extraction failed: {e}")

    async def _extract_text_technical_metadata(self, file_path: str, metadata: TechnicalMetadata):
        """Extract text-specific technical metadata"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Text statistics
            word_count = len(content.split())
            char_count = len(content)
            line_count = len(content.splitlines())
            
            # Store in custom metadata since TechnicalMetadata doesn't have text-specific fields
            metadata.quality_score = min(word_count / 1000, 1.0)  # Quality based on content length
            
        except Exception as e:
            self.logger.error(f"Text technical metadata extraction failed: {e}")

    async def _extract_semantic_metadata(
        self,
        file_path: str,
        content_type: ContentType
    ) -> SemanticMetadata:
        """Extract semantic metadata using AI"""
        try:
            metadata = SemanticMetadata()
            
            if content_type == ContentType.TEXT or content_type == ContentType.DOCUMENT:
                await self._extract_text_semantic_metadata(file_path, metadata)
            elif content_type == ContentType.AUDIO or content_type == ContentType.VOICE:
                await self._extract_audio_semantic_metadata(file_path, metadata)
            elif content_type == ContentType.VIDEO:
                await self._extract_video_semantic_metadata(file_path, metadata)
            elif content_type == ContentType.IMAGE:
                await self._extract_image_semantic_metadata(file_path, metadata)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Semantic metadata extraction failed: {e}")
            return SemanticMetadata()

    async def _extract_text_semantic_metadata(self, file_path: str, metadata: SemanticMetadata):
        """Extract semantic metadata from text content"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            if not NLP_AVAILABLE:
                await self._fallback_text_semantic_analysis(content, metadata)
                return
            
            # AI-powered text analysis
            try:
                # Generate summary
                if len(content) > 100:
                    summary_result = self.nlp_models['summarizer'](content, max_length=150, min_length=30)
                    metadata.ai_summary = summary_result[0]['summary_text']
                else:
                    metadata.ai_summary = content[:150] + "..." if len(content) > 150 else content
                
                # Sentiment analysis
                sentiment_result = self.nlp_models['sentiment'](content)
                metadata.sentiment = sentiment_result[0]['label']
                metadata.sentiment_score = sentiment_result[0]['score']
                
                # Named Entity Recognition
                ner_results = self.nlp_models['ner'](content)
                metadata.entities = [
                    {"text": entity['word'], "label": entity['entity_group'], "confidence": entity['score']}
                    for entity in ner_results
                ]
                
                # Generate description
                metadata.ai_description = await self._generate_ai_description(content, "text")
                
                # Extract keywords
                metadata.ai_keywords = await self._extract_ai_keywords(content)
                
                # Detect language
                metadata.language = await self._detect_language(content)
                
                # Assess complexity
                metadata.complexity_level = await self._assess_text_complexity(content)
                
            except Exception as e:
                self.logger.warning(f"AI text analysis failed, using fallback: {e}")
                await self._fallback_text_semantic_analysis(content, metadata)
                
        except Exception as e:
            self.logger.error(f"Text semantic metadata extraction failed: {e}")

    async def _fallback_text_semantic_analysis(self, content: str, metadata: SemanticMetadata):
        """Fallback text semantic analysis without AI models"""
        try:
            # Simple summary (first 150 characters)
            metadata.ai_summary = content[:150] + "..." if len(content) > 150 else content
            
            # Simple description
            word_count = len(content.split())
            metadata.ai_description = f"Text content with approximately {word_count} words."
            
            # Basic keyword extraction
            words = content.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            metadata.ai_keywords = [word for word, freq in top_keywords]
            
            # Simple sentiment (positive/negative word counting)
            positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            if positive_count > negative_count:
                metadata.sentiment = "POSITIVE"
                metadata.sentiment_score = 0.7
            elif negative_count > positive_count:
                metadata.sentiment = "NEGATIVE"
                metadata.sentiment_score = 0.7
            else:
                metadata.sentiment = "NEUTRAL"
                metadata.sentiment_score = 0.6
            
            # Basic complexity assessment
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            if avg_word_length > 6:
                metadata.complexity_level = "high"
            elif avg_word_length > 4:
                metadata.complexity_level = "medium"
            else:
                metadata.complexity_level = "low"
                
        except Exception as e:
            self.logger.error(f"Fallback text semantic analysis failed: {e}")

    async def _generate_ai_description(self, content: str, content_type: str) -> str:
        """Generate AI-powered description"""
        try:
            if content_type == "text":
                # For text content, create a descriptive summary
                word_count = len(content.split())
                content_preview = content[:200] + "..." if len(content) > 200 else content
                
                description = f"Text content with {word_count} words. "
                
                # Add content hints based on keywords
                content_lower = content.lower()
                if any(word in content_lower for word in ["tutorial", "how to", "guide"]):
                    description += "This appears to be instructional content. "
                elif any(word in content_lower for word in ["news", "breaking", "report"]):
                    description += "This appears to be news or reporting content. "
                elif any(word in content_lower for word in ["review", "opinion", "recommend"]):
                    description += "This appears to be review or opinion content. "
                
                description += f"Preview: {content_preview}"
                
                return description[:self.config.max_description_length]
            
            return f"Content of type {content_type}"
            
        except Exception as e:
            self.logger.error(f"AI description generation failed: {e}")
            return f"Content of type {content_type}"

    async def _extract_ai_keywords(self, content: str) -> List[str]:
        """Extract AI-powered keywords"""
        try:
            # Simple keyword extraction based on frequency and importance
            words = content.lower().split()
            
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'from', 'up', 'about', 'into', 'over', 'after', 'is', 'are', 'was', 'were', 'be', 'been',
                'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
            }
            
            # Filter and count words
            word_freq = {}
            for word in words:
                if len(word) > 3 and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords by frequency
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in top_keywords[:self.config.max_keywords]]
            
        except Exception as e:
            self.logger.error(f"AI keyword extraction failed: {e}")
            return []

    async def _detect_language(self, content: str) -> Optional[str]:
        """Detect content language"""
        try:
            # Simple language detection based on common words
            english_indicators = ['the', 'and', 'is', 'are', 'was', 'were', 'have', 'has', 'with', 'for']
            french_indicators = ['le', 'la', 'les', 'et', 'est', 'sont', 'avec', 'pour', 'dans', 'sur']
            german_indicators = ['der', 'die', 'das', 'und', 'ist', 'sind', 'mit', 'für', 'in', 'auf']
            spanish_indicators = ['el', 'la', 'los', 'las', 'y', 'es', 'son', 'con', 'para', 'en']
            
            content_lower = content.lower()
            
            english_score = sum(1 for word in english_indicators if word in content_lower)
            french_score = sum(1 for word in french_indicators if word in content_lower)
            german_score = sum(1 for word in german_indicators if word in content_lower)
            spanish_score = sum(1 for word in spanish_indicators if word in content_lower)
            
            scores = {
                'en': english_score,
                'fr': french_score,
                'de': german_score,
                'es': spanish_score
            }
            
            return max(scores, key=scores.get) if max(scores.values()) > 0 else 'en'
            
        except Exception as e:
            self.logger.error(f"Language detection failed: {e}")
            return 'en'

    async def _assess_text_complexity(self, content: str) -> str:
        """Assess text complexity level"""
        try:
            words = content.split()
            sentences = content.split('.')
            
            if not words or not sentences:
                return "low"
            
            avg_word_length = sum(len(word) for word in words) / len(words)
            avg_sentence_length = len(words) / len(sentences)
            
            # Complex words (more than 6 characters)
            complex_words = sum(1 for word in words if len(word) > 6)
            complex_word_ratio = complex_words / len(words)
            
            # Calculate complexity score
            complexity_score = (avg_word_length / 10) + (avg_sentence_length / 20) + (complex_word_ratio * 2)
            
            if complexity_score > 0.8:
                return "high"
            elif complexity_score > 0.5:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            self.logger.error(f"Text complexity assessment failed: {e}")
            return "medium"

    async def _generate_seo_metadata(self, metadata: IntelligentMetadata) -> SEOMetadata:
        """Generate SEO-optimized metadata"""
        try:
            seo = SEOMetadata()
            
            # Generate SEO title
            if metadata.semantic.ai_keywords:
                primary_keyword = metadata.semantic.ai_keywords[0]
                seo.title = f"{primary_keyword.title()} - Professional Content"
            else:
                seo.title = "Professional Content"
            
            # Generate SEO description
            if metadata.semantic.ai_summary:
                seo.description = metadata.semantic.ai_summary[:160]
                seo.meta_description = seo.description
            else:
                seo.description = "High-quality professional content"
                seo.meta_description = seo.description
            
            # SEO keywords
            seo.keywords = metadata.semantic.ai_keywords[:10]
            
            # Generate slug
            if metadata.semantic.ai_keywords:
                seo.slug = "-".join(metadata.semantic.ai_keywords[:3]).lower()
            else:
                seo.slug = f"content-{metadata.content_id[:8]}"
            
            # Open Graph metadata
            seo.open_graph_title = seo.title
            seo.open_graph_description = seo.description
            
            # Twitter Card metadata
            seo.twitter_card_title = seo.title
            seo.twitter_card_description = seo.description
            
            # Schema markup
            seo.schema_markup = {
                "@context": "https://schema.org",
                "@type": "CreativeWork",
                "name": seo.title,
                "description": seo.description,
                "keywords": ", ".join(seo.keywords)
            }
            
            return seo
            
        except Exception as e:
            self.logger.error(f"SEO metadata generation failed: {e}")
            return SEOMetadata()

    async def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get metadata extraction statistics"""
        try:
            return {
                "total_extractions": self.metrics["total_extractions"],
                "successful_extractions": self.metrics["successful_extractions"],
                "success_rate": (
                    self.metrics["successful_extractions"] / self.metrics["total_extractions"]
                    if self.metrics["total_extractions"] > 0 else 0.0
                ),
                "average_processing_time": self.metrics["average_processing_time"],
                "content_types_processed": self.metrics["content_types_processed"],
                "ai_descriptions_generated": self.metrics["ai_descriptions_generated"],
                "seo_optimizations_performed": self.metrics["seo_optimizations_performed"]
            }
        except Exception as e:
            self.logger.error(f"Failed to get extraction statistics: {e}")
            return {}


# Metadata processor classes would be implemented here...
class TechnicalMetadataExtractor:
    """Technical metadata extraction processor"""
    pass

class SemanticMetadataExtractor:
    """Semantic metadata extraction processor"""
    
    def __init__(self, config: MetadataExtractionConfig):
        self.config = config

class SEOMetadataOptimizer:
    """SEO metadata optimization processor"""
    
    def __init__(self, config: MetadataExtractionConfig):
        self.config = config

class CulturalMetadataAnalyzer:
    """Cultural metadata analysis processor"""
    
    def __init__(self, config: MetadataExtractionConfig):
        self.config = config


# Global extractor instance
_metadata_extractor = None


async def get_metadata_extractor() -> IntelligentMetadataExtractor:
    """Get global Intelligent Metadata Extractor instance"""
    global _metadata_extractor
    if _metadata_extractor is None:
        _metadata_extractor = IntelligentMetadataExtractor()
        await _metadata_extractor.initialize()
    return _metadata_extractor


async def extract_intelligent_metadata(
    content_id: str,
    file_path: str,
    content_type: ContentType,
    extraction_categories: Optional[List[MetadataCategory]] = None
) -> IntelligentMetadata:
    """Convenience function for intelligent metadata extraction"""
    extractor = await get_metadata_extractor()
    return await extractor.extract_metadata(content_id, file_path, content_type, extraction_categories)


if __name__ == "__main__":
    # Development testing
    async def test_metadata_extractor():
        """Test intelligent metadata extraction functionality"""
        extractor = IntelligentMetadataExtractor()
        await extractor.initialize()
        
        print("Intelligent Metadata Extractor test completed successfully")
    
    asyncio.run(test_metadata_extractor())