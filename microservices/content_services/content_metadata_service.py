"""
Content Metadata Service - Enterprise Microservice
================================================

Advanced metadata extraction and management system for content with AI-powered
analysis, automatic tagging, format detection, and comprehensive metadata indexing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import json
import hashlib
import mimetypes
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content type classification."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    CODE = "code"
    MODEL_3D = "model_3d"
    INTERACTIVE = "interactive"
    MIXED_MEDIA = "mixed_media"


class MetadataExtractionMethod(str, Enum):
    """Methods for metadata extraction."""
    AUTOMATIC = "automatic"
    AI_ANALYSIS = "ai_analysis"
    MANUAL_INPUT = "manual_input"
    API_ENRICHMENT = "api_enrichment"
    CROWDSOURCE = "crowdsource"
    TEMPLATE_BASED = "template_based"


class ContentFormat(str, Enum):
    """Supported content formats."""
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    SVG = "svg"
    TIFF = "tiff"
    BMP = "bmp"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    MKV = "mkv"
    
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    WMA = "wma"
    
    # Text/Document formats
    TXT = "txt"
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    HTML = "html"
    MD = "md"
    RTF = "rtf"
    
    # Other
    ZIP = "zip"
    RAR = "rar"
    JSON = "json"
    XML = "xml"
    CSV = "csv"


class MetadataField(BaseModel):
    """Individual metadata field."""
    key: str = Field(..., description="Metadata field key")
    value: Any = Field(..., description="Metadata field value")
    data_type: str = Field(..., description="Data type (string, number, boolean, array, object)")
    source: MetadataExtractionMethod = Field(..., description="How this metadata was obtained")
    confidence: float = Field(default=1.0, description="Confidence score (0-1)")
    extracted_at: datetime = Field(default_factory=datetime.now)
    verified: bool = Field(default=False, description="Whether metadata is verified")


class TechnicalMetadata(BaseModel):
    """Technical metadata for content."""
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    format: ContentFormat = Field(..., description="Content format")
    checksum_md5: str = Field(..., description="MD5 checksum")
    checksum_sha256: str = Field(..., description="SHA256 checksum")
    creation_date: Optional[datetime] = Field(None, description="Content creation date")
    modification_date: Optional[datetime] = Field(None, description="Last modification date")
    
    # Format-specific metadata
    dimensions: Optional[Dict[str, int]] = Field(None, description="Width/height for images/videos")
    duration: Optional[float] = Field(None, description="Duration in seconds for audio/video")
    bitrate: Optional[int] = Field(None, description="Bitrate for audio/video")
    sample_rate: Optional[int] = Field(None, description="Sample rate for audio")
    color_depth: Optional[int] = Field(None, description="Color depth for images")
    compression: Optional[str] = Field(None, description="Compression method")
    encoding: Optional[str] = Field(None, description="Text encoding")


class DescriptiveMetadata(BaseModel):
    """Descriptive metadata for content."""
    title: Optional[str] = Field(None, description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    keywords: List[str] = Field(default_factory=list, description="Keywords/tags")
    categories: List[str] = Field(default_factory=list, description="Content categories")
    genre: Optional[str] = Field(None, description="Content genre")
    mood: Optional[str] = Field(None, description="Content mood/tone")
    style: Optional[str] = Field(None, description="Content style")
    themes: List[str] = Field(default_factory=list, description="Content themes")
    subjects: List[str] = Field(default_factory=list, description="Content subjects")
    language: Optional[str] = Field(None, description="Primary language")
    languages_detected: List[str] = Field(default_factory=list, description="All detected languages")


class CreativeMetadata(BaseModel):
    """Creative/artistic metadata."""
    creator: Optional[str] = Field(None, description="Content creator")
    artist: Optional[str] = Field(None, description="Primary artist")
    collaborators: List[str] = Field(default_factory=list, description="Collaborating artists")
    album: Optional[str] = Field(None, description="Album/collection name")
    track_number: Optional[int] = Field(None, description="Track number in album")
    composer: Optional[str] = Field(None, description="Music composer")
    producer: Optional[str] = Field(None, description="Content producer")
    director: Optional[str] = Field(None, description="Video director")
    photographer: Optional[str] = Field(None, description="Photographer")
    copyright_holder: Optional[str] = Field(None, description="Copyright holder")
    license: Optional[str] = Field(None, description="Content license")
    rights_info: Optional[str] = Field(None, description="Rights information")


class ContextualMetadata(BaseModel):
    """Contextual metadata about content usage and environment."""
    location_created: Optional[str] = Field(None, description="Location where created")
    location_coordinates: Optional[Tuple[float, float]] = Field(None, description="GPS coordinates")
    equipment_used: List[str] = Field(default_factory=list, description="Equipment/software used")
    recording_conditions: Optional[str] = Field(None, description="Recording/creation conditions")
    audience_target: Optional[str] = Field(None, description="Target audience")
    cultural_context: Optional[str] = Field(None, description="Cultural context")
    historical_period: Optional[str] = Field(None, description="Historical period")
    related_events: List[str] = Field(default_factory=list, description="Related events")
    social_context: Optional[str] = Field(None, description="Social context")


class ContentMetadata(BaseModel):
    """Complete content metadata."""
    content_id: str = Field(..., description="Unique content identifier")
    content_type: ContentType = Field(..., description="Content type classification")
    technical: TechnicalMetadata = Field(..., description="Technical metadata")
    descriptive: DescriptiveMetadata = Field(..., description="Descriptive metadata")
    creative: CreativeMetadata = Field(..., description="Creative metadata")
    contextual: ContextualMetadata = Field(..., description="Contextual metadata")
    custom_fields: Dict[str, MetadataField] = Field(default_factory=dict, description="Custom metadata fields")
    ai_generated_tags: List[str] = Field(default_factory=list, description="AI-generated tags")
    quality_score: float = Field(default=0.0, description="Content quality score")
    completeness_score: float = Field(default=0.0, description="Metadata completeness score")
    extracted_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)


class MetadataExtractionResult(BaseModel):
    """Result of metadata extraction process."""
    content_id: str
    success: bool
    metadata: Optional[ContentMetadata]
    extraction_time: float  # seconds
    methods_used: List[MetadataExtractionMethod]
    confidence_scores: Dict[str, float]
    warnings: List[str]
    errors: List[str]


class ContentMetadataService:
    """
    Enterprise Content Metadata Service
    
    Provides comprehensive metadata extraction, management, and enrichment
    for all content types with AI-powered analysis and intelligent tagging.
    """
    
    def __init__(self) -> None:
        self.metadata_store: Dict[str, ContentMetadata] = {}
        self.extraction_templates: Dict[ContentType, Dict[str, Any]] = {}
        self.ai_models: Dict[str, Any] = {}
        self.format_handlers: Dict[ContentFormat, Any] = {}
        self.custom_extractors: Dict[str, Any] = {}
        self.enrichment_apis: Dict[str, Any] = {}
        
        # Initialize system
        self._initialize_extraction_templates()
        self._initialize_format_handlers()
        self._initialize_ai_models()
        self._initialize_enrichment_apis()
        
        logger.info("ContentMetadataService initialized successfully")
    
    def _initialize_extraction_templates(self) -> None:
        """Initialize extraction templates for different content types."""
        self.extraction_templates = {
            ContentType.IMAGE: {
                "required_fields": ["dimensions", "color_depth", "format"],
                "ai_analysis": ["objects", "scenes", "colors", "composition"],
                "extract_exif": True,
                "facial_recognition": True,
                "text_recognition": True
            },
            ContentType.VIDEO: {
                "required_fields": ["duration", "dimensions", "bitrate", "format"],
                "ai_analysis": ["scenes", "objects", "actions", "emotions"],
                "extract_frames": True,
                "audio_analysis": True,
                "motion_analysis": True
            },
            ContentType.AUDIO: {
                "required_fields": ["duration", "bitrate", "sample_rate", "format"],
                "ai_analysis": ["genre", "mood", "instruments", "vocals"],
                "spectral_analysis": True,
                "beat_detection": True,
                "voice_analysis": True
            },
            ContentType.TEXT: {
                "required_fields": ["language", "word_count", "encoding"],
                "ai_analysis": ["sentiment", "topics", "entities", "readability"],
                "nlp_processing": True,
                "keyword_extraction": True,
                "language_detection": True
            },
            ContentType.DOCUMENT: {
                "required_fields": ["format", "page_count", "creation_date"],
                "ai_analysis": ["document_type", "structure", "content_summary"],
                "text_extraction": True,
                "metadata_extraction": True,
                "table_detection": True
            }
        }
    
    def _initialize_format_handlers(self) -> None:
        """Initialize format-specific handlers."""
        # This would contain actual format handling logic
        self.format_handlers = {
            ContentFormat.JPEG: self._handle_jpeg,
            ContentFormat.PNG: self._handle_png,
            ContentFormat.MP4: self._handle_mp4,
            ContentFormat.MP3: self._handle_mp3,
            ContentFormat.PDF: self._handle_pdf,
            ContentFormat.TXT: self._handle_txt,
            # ... more handlers
        }
    
    def _initialize_ai_models(self) -> None:
        """Initialize AI models for content analysis."""
        # Placeholder for AI model initialization
        self.ai_models = {
            "image_classifier": {"model": "resnet50", "confidence_threshold": 0.7},
            "object_detector": {"model": "yolo_v5", "confidence_threshold": 0.5},
            "text_analyzer": {"model": "bert_base", "confidence_threshold": 0.8},
            "audio_classifier": {"model": "vgg16_audio", "confidence_threshold": 0.6},
            "scene_detector": {"model": "scene_recognition", "confidence_threshold": 0.7},
            "sentiment_analyzer": {"model": "roberta_sentiment", "confidence_threshold": 0.75}
        }
    
    def _initialize_enrichment_apis(self) -> None:
        """Initialize external APIs for metadata enrichment."""
        self.enrichment_apis = {
            "wikipedia": {"enabled": True, "rate_limit": 100},
            "wikidata": {"enabled": True, "rate_limit": 200},
            "musicbrainz": {"enabled": True, "rate_limit": 50},
            "tmdb": {"enabled": True, "rate_limit": 40},  # The Movie Database
            "last_fm": {"enabled": True, "rate_limit": 60},
            "genius": {"enabled": True, "rate_limit": 30},  # Lyrics API
            "google_vision": {"enabled": False, "rate_limit": 1000},
            "aws_rekognition": {"enabled": False, "rate_limit": 2000}
        }
    
    async def extract_metadata(
        self, 
        content_id: str, 
        file_path: str, 
        content_type: Optional[ContentType] = None,
        extraction_methods: Optional[List[MetadataExtractionMethod]] = None
    ) -> MetadataExtractionResult:
        """Extract comprehensive metadata from content."""
        start_time = datetime.now()
        warnings = []
        errors = []
        
        try:
            # Detect content type if not provided
            if not content_type:
                content_type = await self._detect_content_type(file_path)
            
            # Initialize metadata structure
            technical_metadata = await self._extract_technical_metadata(file_path, content_type)
            descriptive_metadata = DescriptiveMetadata()
            creative_metadata = CreativeMetadata()
            contextual_metadata = ContextualMetadata()
            custom_fields = {}
            ai_generated_tags = []
            
            # Use default extraction methods if not specified
            if not extraction_methods:
                extraction_methods = [
                    MetadataExtractionMethod.AUTOMATIC,
                    MetadataExtractionMethod.AI_ANALYSIS
                ]
            
            confidence_scores = {}
            
            # Apply each extraction method
            for method in extraction_methods:
                try:
                    if method == MetadataExtractionMethod.AUTOMATIC:
                        desc_data, conf = await self._extract_automatic_metadata(file_path, content_type)
                        descriptive_metadata = self._merge_descriptive_metadata(descriptive_metadata, desc_data)
                        confidence_scores["automatic"] = conf
                        
                    elif method == MetadataExtractionMethod.AI_ANALYSIS:
                        ai_data, ai_tags, conf = await self._extract_ai_metadata(file_path, content_type)
                        descriptive_metadata = self._merge_descriptive_metadata(descriptive_metadata, ai_data)
                        ai_generated_tags.extend(ai_tags)
                        confidence_scores["ai_analysis"] = conf
                        
                    elif method == MetadataExtractionMethod.API_ENRICHMENT:
                        enriched_data, conf = await self._enrich_metadata_via_apis(descriptive_metadata, content_type)
                        descriptive_metadata = self._merge_descriptive_metadata(descriptive_metadata, enriched_data)
                        confidence_scores["api_enrichment"] = conf
                        
                except Exception as e:
                    error_msg = f"Error in {method.value}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Calculate quality and completeness scores
            quality_score = await self._calculate_quality_score(technical_metadata, content_type)
            completeness_score = self._calculate_completeness_score(
                technical_metadata, descriptive_metadata, creative_metadata, contextual_metadata
            )
            
            # Create complete metadata object
            metadata = ContentMetadata(
                content_id=content_id,
                content_type=content_type,
                technical=technical_metadata,
                descriptive=descriptive_metadata,
                creative=creative_metadata,
                contextual=contextual_metadata,
                custom_fields=custom_fields,
                ai_generated_tags=list(set(ai_generated_tags)),  # Remove duplicates
                quality_score=quality_score,
                completeness_score=completeness_score
            )
            
            # Store metadata
            self.metadata_store[content_id] = metadata
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Extracted metadata for content {content_id} in {extraction_time:.2f}s")
            
            return MetadataExtractionResult(
                content_id=content_id,
                success=True,
                metadata=metadata,
                extraction_time=extraction_time,
                methods_used=extraction_methods,
                confidence_scores=confidence_scores,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            extraction_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Failed to extract metadata: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            
            return MetadataExtractionResult(
                content_id=content_id,
                success=False,
                metadata=None,
                extraction_time=extraction_time,
                methods_used=extraction_methods or [],
                confidence_scores={},
                warnings=warnings,
                errors=errors
            )
    
    async def _detect_content_type(self, file_path: str) -> ContentType:
        """Detect content type from file."""
        try:
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if mime_type:
                if mime_type.startswith('image/'):
                    return ContentType.IMAGE
                elif mime_type.startswith('video/'):
                    return ContentType.VIDEO
                elif mime_type.startswith('audio/'):
                    return ContentType.AUDIO
                elif mime_type.startswith('text/'):
                    return ContentType.TEXT
                elif mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                    return ContentType.DOCUMENT
                elif mime_type in ['application/zip', 'application/x-rar-compressed']:
                    return ContentType.ARCHIVE
            
            # Fallback to file extension
            extension = file_path.lower().split('.')[-1]
            
            image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'tiff', 'bmp']
            video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
            audio_extensions = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma']
            text_extensions = ['txt', 'md', 'html', 'css', 'js', 'py', 'java', 'cpp']
            doc_extensions = ['pdf', 'doc', 'docx', 'rtf', 'odt']
            
            if extension in image_extensions:
                return ContentType.IMAGE
            elif extension in video_extensions:
                return ContentType.VIDEO
            elif extension in audio_extensions:
                return ContentType.AUDIO
            elif extension in text_extensions:
                return ContentType.TEXT
            elif extension in doc_extensions:
                return ContentType.DOCUMENT
            
            return ContentType.MIXED_MEDIA  # Default fallback
            
        except Exception as e:
            logger.error(f"Error detecting content type: {e}")
            return ContentType.MIXED_MEDIA
    
    async def _extract_technical_metadata(self, file_path: str, content_type: ContentType) -> TechnicalMetadata:
        """Extract technical metadata from file."""
        try:
            import os
            import stat
            
            # Basic file information
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            creation_date = datetime.fromtimestamp(file_stats.st_ctime)
            modification_date = datetime.fromtimestamp(file_stats.st_mtime)
            
            # MIME type and format
            mime_type, _ = mimetypes.guess_type(file_path)
            extension = file_path.lower().split('.')[-1]
            
            try:
                format_enum = ContentFormat(extension)
            except ValueError:
                format_enum = ContentFormat.TXT  # Default fallback
            
            # Calculate checksums
            md5_hash = await self._calculate_md5(file_path)
            sha256_hash = await self._calculate_sha256(file_path)
            
            # Format-specific metadata
            dimensions = None
            duration = None
            bitrate = None
            sample_rate = None
            color_depth = None
            compression = None
            encoding = None
            
            # Extract format-specific metadata
            if content_type == ContentType.IMAGE:
                dimensions, color_depth = await self._extract_image_specs(file_path)
            elif content_type == ContentType.VIDEO:
                dimensions, duration, bitrate = await self._extract_video_specs(file_path)
            elif content_type == ContentType.AUDIO:
                duration, bitrate, sample_rate = await self._extract_audio_specs(file_path)
            elif content_type == ContentType.TEXT:
                encoding = await self._detect_text_encoding(file_path)
            
            return TechnicalMetadata(
                file_size=file_size,
                mime_type=mime_type or "application/octet-stream",
                format=format_enum,
                checksum_md5=md5_hash,
                checksum_sha256=sha256_hash,
                creation_date=creation_date,
                modification_date=modification_date,
                dimensions=dimensions,
                duration=duration,
                bitrate=bitrate,
                sample_rate=sample_rate,
                color_depth=color_depth,
                compression=compression,
                encoding=encoding
            )
            
        except Exception as e:
            logger.error(f"Error extracting technical metadata: {e}")
            # Return minimal metadata
            return TechnicalMetadata(
                file_size=0,
                mime_type="application/octet-stream",
                format=ContentFormat.TXT,
                checksum_md5="",
                checksum_sha256=""
            )
    
    async def _calculate_md5(self, file_path: str) -> str:
        """Calculate MD5 hash of file."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating MD5: {e}")
            return ""
    
    async def _calculate_sha256(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating SHA256: {e}")
            return ""
    
    async def _extract_image_specs(self, file_path: str) -> Tuple[Optional[Dict[str, int]], Optional[int]]:
        """Extract image-specific metadata."""
        try:
            # Placeholder for image analysis
            # In real implementation, would use PIL, OpenCV, or similar
            return {"width": 1920, "height": 1080}, 24
        except Exception as e:
            logger.error(f"Error extracting image specs: {e}")
            return None, None
    
    async def _extract_video_specs(self, file_path: str) -> Tuple[Optional[Dict[str, int]], Optional[float], Optional[int]]:
        """Extract video-specific metadata."""
        try:
            # Placeholder for video analysis
            # In real implementation, would use ffmpeg-python or similar
            return {"width": 1920, "height": 1080}, 120.5, 5000
        except Exception as e:
            logger.error(f"Error extracting video specs: {e}")
            return None, None, None
    
    async def _extract_audio_specs(self, file_path: str) -> Tuple[Optional[float], Optional[int], Optional[int]]:
        """Extract audio-specific metadata."""
        try:
            # Placeholder for audio analysis
            # In real implementation, would use librosa, mutagen, or similar
            return 180.3, 320, 44100
        except Exception as e:
            logger.error(f"Error extracting audio specs: {e}")
            return None, None, None
    
    async def _detect_text_encoding(self, file_path: str) -> Optional[str]:
        """Detect text file encoding."""
        try:
            import chardet
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8')
        except Exception as e:
            logger.error(f"Error detecting encoding: {e}")
            return "utf-8"
    
    async def _extract_automatic_metadata(
        self, 
        file_path: str, 
        content_type: ContentType
    ) -> Tuple[DescriptiveMetadata, float]:
        """Extract metadata using automatic methods."""
        try:
            descriptive = DescriptiveMetadata()
            
            # Extract filename-based metadata
            filename = file_path.split('/')[-1]
            title = filename.split('.')[0].replace('_', ' ').replace('-', ' ')
            descriptive.title = title
            
            # Extract keywords from filename
            keywords = re.findall(r'\b\w+\b', title.lower())
            descriptive.keywords = [kw for kw in keywords if len(kw) > 2]
            
            # Content-type specific extraction
            if content_type == ContentType.TEXT:
                # Extract content from text file
                content_text = await self._read_text_content(file_path)
                if content_text:
                    descriptive.description = content_text[:500]  # First 500 chars
                    descriptive.language = await self._detect_language(content_text)
            
            return descriptive, 0.7  # Medium confidence for automatic extraction
            
        except Exception as e:
            logger.error(f"Error in automatic extraction: {e}")
            return DescriptiveMetadata(), 0.0
    
    async def _extract_ai_metadata(
        self, 
        file_path: str, 
        content_type: ContentType
    ) -> Tuple[DescriptiveMetadata, List[str], float]:
        """Extract metadata using AI analysis."""
        try:
            descriptive = DescriptiveMetadata()
            ai_tags = []
            
            # AI analysis based on content type
            if content_type == ContentType.IMAGE:
                descriptive, ai_tags = await self._analyze_image_with_ai(file_path)
            elif content_type == ContentType.VIDEO:
                descriptive, ai_tags = await self._analyze_video_with_ai(file_path)
            elif content_type == ContentType.AUDIO:
                descriptive, ai_tags = await self._analyze_audio_with_ai(file_path)
            elif content_type == ContentType.TEXT:
                descriptive, ai_tags = await self._analyze_text_with_ai(file_path)
            
            return descriptive, ai_tags, 0.85  # High confidence for AI analysis
            
        except Exception as e:
            logger.error(f"Error in AI extraction: {e}")
            return DescriptiveMetadata(), [], 0.0
    
    async def _analyze_image_with_ai(self, file_path: str) -> Tuple[DescriptiveMetadata, List[str]]:
        """Analyze image with AI models."""
        # Placeholder for AI image analysis
        descriptive = DescriptiveMetadata()
        descriptive.categories = ["photography", "nature"]
        descriptive.keywords = ["landscape", "mountains", "sky"]
        descriptive.mood = "peaceful"
        descriptive.style = "realistic"
        
        ai_tags = ["outdoor", "scenic", "natural", "blue_sky", "landscape_photography"]
        
        return descriptive, ai_tags
    
    async def _analyze_video_with_ai(self, file_path: str) -> Tuple[DescriptiveMetadata, List[str]]:
        """Analyze video with AI models."""
        # Placeholder for AI video analysis
        descriptive = DescriptiveMetadata()
        descriptive.categories = ["entertainment", "tutorial"]
        descriptive.keywords = ["education", "technology", "coding"]
        descriptive.themes = ["learning", "development"]
        
        ai_tags = ["tutorial", "educational", "programming", "screen_recording"]
        
        return descriptive, ai_tags
    
    async def _analyze_audio_with_ai(self, file_path: str) -> Tuple[DescriptiveMetadata, List[str]]:
        """Analyze audio with AI models."""
        # Placeholder for AI audio analysis
        descriptive = DescriptiveMetadata()
        descriptive.genre = "electronic"
        descriptive.mood = "energetic"
        descriptive.keywords = ["music", "electronic", "synthesizer"]
        
        ai_tags = ["upbeat", "instrumental", "electronic_music", "synthesized"]
        
        return descriptive, ai_tags
    
    async def _analyze_text_with_ai(self, file_path: str) -> Tuple[DescriptiveMetadata, List[str]]:
        """Analyze text with AI models."""
        try:
            content = await self._read_text_content(file_path)
            if not content:
                return DescriptiveMetadata(), []
            
            # Placeholder for AI text analysis
            descriptive = DescriptiveMetadata()
            descriptive.language = await self._detect_language(content)
            descriptive.themes = ["technology", "business"]
            descriptive.keywords = await self._extract_keywords_ai(content)
            
            ai_tags = ["article", "informative", "professional", "technical_writing"]
            
            return descriptive, ai_tags
            
        except Exception as e:
            logger.error(f"Error analyzing text with AI: {e}")
            return DescriptiveMetadata(), []
    
    async def _read_text_content(self, file_path: str) -> str:
        """Read text content from file."""
        try:
            encoding = await self._detect_text_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text content: {e}")
            return ""
    
    async def _detect_language(self, text: str) -> str:
        """Detect language of text."""
        # Placeholder for language detection
        # In real implementation, would use langdetect or similar
        return "en"
    
    async def _extract_keywords_ai(self, text: str) -> List[str]:
        """Extract keywords using AI."""
        # Placeholder for AI keyword extraction
        # In real implementation, would use BERT, spaCy, or similar
        words = text.lower().split()
        return list(set([word for word in words if len(word) > 4]))[:10]
    
    async def _enrich_metadata_via_apis(
        self, 
        descriptive: DescriptiveMetadata, 
        content_type: ContentType
    ) -> Tuple[DescriptiveMetadata, float]:
        """Enrich metadata using external APIs."""
        try:
            # Placeholder for API enrichment
            # Would integrate with Wikipedia, MusicBrainz, TMDB, etc.
            
            enriched = descriptive.copy()
            
            # Example enrichment
            if descriptive.title:
                # Query external APIs for additional information
                enriched.description = f"Enhanced description for {descriptive.title}"
                enriched.categories.extend(["verified", "enriched"])
            
            return enriched, 0.9  # High confidence for API data
            
        except Exception as e:
            logger.error(f"Error in API enrichment: {e}")
            return descriptive, 0.0
    
    def _merge_descriptive_metadata(
        self, 
        base: DescriptiveMetadata, 
        new_data: DescriptiveMetadata
    ) -> DescriptiveMetadata:
        """Merge descriptive metadata, preferring higher quality data."""
        merged = base.copy()
        
        # Merge fields, preferring non-empty values
        if new_data.title and not merged.title:
            merged.title = new_data.title
        if new_data.description and not merged.description:
            merged.description = new_data.description
        if new_data.language and not merged.language:
            merged.language = new_data.language
        if new_data.genre and not merged.genre:
            merged.genre = new_data.genre
        if new_data.mood and not merged.mood:
            merged.mood = new_data.mood
        if new_data.style and not merged.style:
            merged.style = new_data.style
        
        # Merge lists, avoiding duplicates
        merged.keywords = list(set(merged.keywords + new_data.keywords))
        merged.categories = list(set(merged.categories + new_data.categories))
        merged.themes = list(set(merged.themes + new_data.themes))
        merged.subjects = list(set(merged.subjects + new_data.subjects))
        merged.languages_detected = list(set(merged.languages_detected + new_data.languages_detected))
        
        return merged
    
    async def _calculate_quality_score(
        self, 
        technical: TechnicalMetadata, 
        content_type: ContentType
    ) -> float:
        """Calculate content quality score based on technical parameters."""
        try:
            score = 0.0
            max_score = 100.0
            
            # File size considerations
            if technical.file_size > 0:
                if content_type == ContentType.IMAGE:
                    # Higher resolution generally means higher quality
                    if technical.dimensions:
                        pixels = technical.dimensions.get("width", 0) * technical.dimensions.get("height", 0)
                        if pixels > 2000000:  # > 2MP
                            score += 30
                        elif pixels > 800000:  # > 0.8MP
                            score += 20
                        else:
                            score += 10
                
                elif content_type == ContentType.VIDEO:
                    # Consider resolution and bitrate
                    if technical.dimensions and technical.bitrate:
                        width = technical.dimensions.get("width", 0)
                        if width >= 1920:  # 1080p or higher
                            score += 25
                        elif width >= 1280:  # 720p
                            score += 20
                        else:
                            score += 10
                        
                        if technical.bitrate >= 5000:  # High bitrate
                            score += 15
                        elif technical.bitrate >= 2000:  # Medium bitrate
                            score += 10
                        else:
                            score += 5
                
                elif content_type == ContentType.AUDIO:
                    # Consider bitrate and sample rate
                    if technical.bitrate and technical.bitrate >= 320:
                        score += 20
                    elif technical.bitrate and technical.bitrate >= 192:
                        score += 15
                    else:
                        score += 5
                    
                    if technical.sample_rate and technical.sample_rate >= 44100:
                        score += 15
                    else:
                        score += 5
                
                # File integrity (checksums available)
                if technical.checksum_md5 and technical.checksum_sha256:
                    score += 10
                
                # Proper format detection
                if technical.mime_type != "application/octet-stream":
                    score += 10
                
                # Recent creation (bonus for newer content)
                if technical.creation_date:
                    days_old = (datetime.now() - technical.creation_date).days
                    if days_old < 30:
                        score += 10
                    elif days_old < 90:
                        score += 5
            
            return min(score, max_score) / max_score  # Normalize to 0-1
            
        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
            return 0.0
    
    def _calculate_completeness_score(
        self, 
        technical: TechnicalMetadata,
        descriptive: DescriptiveMetadata,
        creative: CreativeMetadata,
        contextual: ContextualMetadata
    ) -> float:
        """Calculate metadata completeness score."""
        try:
            total_fields = 0
            filled_fields = 0
            
            # Technical metadata (required)
            tech_fields = [
                technical.file_size > 0,
                bool(technical.mime_type),
                bool(technical.format),
                bool(technical.checksum_md5),
                bool(technical.checksum_sha256)
            ]
            total_fields += len(tech_fields)
            filled_fields += sum(tech_fields)
            
            # Descriptive metadata
            desc_fields = [
                bool(descriptive.title),
                bool(descriptive.description),
                len(descriptive.keywords) > 0,
                len(descriptive.categories) > 0,
                bool(descriptive.language)
            ]
            total_fields += len(desc_fields)
            filled_fields += sum(desc_fields)
            
            # Creative metadata
            creative_fields = [
                bool(creative.creator),
                bool(creative.artist),
                bool(creative.copyright_holder),
                bool(creative.license)
            ]
            total_fields += len(creative_fields)
            filled_fields += sum(creative_fields)
            
            # Contextual metadata
            context_fields = [
                bool(contextual.location_created),
                bool(contextual.audience_target),
                len(contextual.equipment_used) > 0
            ]
            total_fields += len(context_fields)
            filled_fields += sum(context_fields)
            
            return filled_fields / total_fields if total_fields > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating completeness score: {e}")
            return 0.0
    
    # Format-specific handlers (placeholders)
    async def _handle_jpeg(self, file_path: str) -> Dict[str, Any]:
        """Handle JPEG-specific metadata extraction."""
        return {"exif_data": {}, "color_profile": "sRGB"}
    
    async def _handle_png(self, file_path: str) -> Dict[str, Any]:
        """Handle PNG-specific metadata extraction."""
        return {"transparency": True, "color_type": "RGBA"}
    
    async def _handle_mp4(self, file_path: str) -> Dict[str, Any]:
        """Handle MP4-specific metadata extraction."""
        return {"codec": "H.264", "container": "MP4"}
    
    async def _handle_mp3(self, file_path: str) -> Dict[str, Any]:
        """Handle MP3-specific metadata extraction."""
        return {"id3_tags": {}, "vbr": False}
    
    async def _handle_pdf(self, file_path: str) -> Dict[str, Any]:
        """Handle PDF-specific metadata extraction."""
        return {"pages": 10, "encrypted": False}
    
    async def _handle_txt(self, file_path: str) -> Dict[str, Any]:
        """Handle TXT-specific metadata extraction."""
        return {"line_count": 100, "word_count": 500}
    
    # Public API methods
    async def get_metadata(self, content_id: str) -> Optional[ContentMetadata]:
        """Get metadata for content."""
        return self.metadata_store.get(content_id)
    
    async def update_metadata(
        self, 
        content_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update specific metadata fields."""
        try:
            if content_id not in self.metadata_store:
                return False
            
            metadata = self.metadata_store[content_id]
            
            # Apply updates to appropriate sections
            for key, value in updates.items():
                if hasattr(metadata.descriptive, key):
                    setattr(metadata.descriptive, key, value)
                elif hasattr(metadata.creative, key):
                    setattr(metadata.creative, key, value)
                elif hasattr(metadata.contextual, key):
                    setattr(metadata.contextual, key, value)
                else:
                    # Add as custom field
                    metadata.custom_fields[key] = MetadataField(
                        key=key,
                        value=value,
                        data_type=type(value).__name__,
                        source=MetadataExtractionMethod.MANUAL_INPUT
                    )
            
            metadata.last_updated = datetime.now()
            
            # Recalculate completeness score
            metadata.completeness_score = self._calculate_completeness_score(
                metadata.technical, metadata.descriptive, 
                metadata.creative, metadata.contextual
            )
            
            logger.info(f"Updated metadata for content {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            return False
    
    async def search_by_metadata(
        self, 
        query: str, 
        content_type: Optional[ContentType] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Search content by metadata."""
        try:
            query_lower = query.lower()
            matching_content = []
            
            for content_id, metadata in self.metadata_store.items():
                # Content type filter
                if content_type and metadata.content_type != content_type:
                    continue
                
                # Text search in various fields
                searchable_text = " ".join([
                    metadata.descriptive.title or "",
                    metadata.descriptive.description or "",
                    " ".join(metadata.descriptive.keywords),
                    " ".join(metadata.descriptive.categories),
                    " ".join(metadata.ai_generated_tags),
                    metadata.creative.creator or "",
                    metadata.creative.artist or ""
                ]).lower()
                
                if query_lower in searchable_text:
                    # Apply additional filters if provided
                    if filters:
                        match = True
                        for filter_key, filter_value in filters.items():
                            if filter_key == "quality_score_min":
                                if metadata.quality_score < filter_value:
                                    match = False
                                    break
                            elif filter_key == "file_size_max":
                                if metadata.technical.file_size > filter_value:
                                    match = False
                                    break
                            # Add more filters as needed
                        
                        if match:
                            matching_content.append(content_id)
                    else:
                        matching_content.append(content_id)
            
            return matching_content
            
        except Exception as e:
            logger.error(f"Error searching metadata: {e}")
            return []
    
    async def get_metadata_analytics(self) -> Dict[str, Any]:
        """Get analytics about metadata in the system."""
        try:
            total_content = len(self.metadata_store)
            
            if total_content == 0:
                return {
                    "total_content": 0,
                    "content_type_distribution": {},
                    "format_distribution": {},
                    "average_quality_score": 0.0,
                    "average_completeness_score": 0.0
                }
            
            # Calculate distributions
            type_dist = defaultdict(int)
            format_dist = defaultdict(int)
            quality_scores = []
            completeness_scores = []
            
            for metadata in self.metadata_store.values():
                type_dist[metadata.content_type.value] += 1
                format_dist[metadata.technical.format.value] += 1
                quality_scores.append(metadata.quality_score)
                completeness_scores.append(metadata.completeness_score)
            
            avg_quality = sum(quality_scores) / len(quality_scores)
            avg_completeness = sum(completeness_scores) / len(completeness_scores)
            
            return {
                "total_content": total_content,
                "content_type_distribution": dict(type_dist),
                "format_distribution": dict(format_dist),
                "average_quality_score": avg_quality,
                "average_completeness_score": avg_completeness,
                "extraction_methods_supported": len(MetadataExtractionMethod),
                "ai_models_loaded": len(self.ai_models),
                "enrichment_apis_available": len(self.enrichment_apis)
            }
            
        except Exception as e:
            logger.error(f"Error getting metadata analytics: {e}")
            return {}
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics."""
        return {
            "total_metadata_records": len(self.metadata_store),
            "content_types_supported": len(ContentType),
            "formats_supported": len(ContentFormat),
            "extraction_methods": len(MetadataExtractionMethod),
            "ai_models_configured": len(self.ai_models),
            "format_handlers": len(self.format_handlers),
            "enrichment_apis": len(self.enrichment_apis),
            "extraction_templates": len(self.extraction_templates)
        }


# Global service instance
_metadata_service_instance = None

def get_content_metadata_service() -> ContentMetadataService:
    """Get singleton instance of ContentMetadataService."""
    global _metadata_service_instance
    if _metadata_service_instance is None:
        _metadata_service_instance = ContentMetadataService()
    return _metadata_service_instance


# Example usage and testing
async def example_usage() -> None:
    """Example usage of Content Metadata Service."""
    service = get_content_metadata_service()
    
    # Extract metadata from a file
    result = await service.extract_metadata(
        content_id="content_123",
        file_path="/tmp/sample_video.mp4",
        content_type=ContentType.VIDEO,
        extraction_methods=[
            MetadataExtractionMethod.AUTOMATIC,
            MetadataExtractionMethod.AI_ANALYSIS
        ]
    )
    
    print(f"Extraction result: Success={result.success}")
    print(f"Extraction time: {result.extraction_time:.2f}s")
    print(f"Confidence scores: {result.confidence_scores}")
    
    if result.metadata:
        print(f"Content type: {result.metadata.content_type}")
        print(f"Quality score: {result.metadata.quality_score:.2f}")
        print(f"Completeness score: {result.metadata.completeness_score:.2f}")
        print(f"AI tags: {result.metadata.ai_generated_tags}")
    
    # Update metadata
    updates = {
        "title": "My Amazing Video",
        "description": "This is a comprehensive tutorial on AI development",
        "creator": "John Doe",
        "license": "Creative Commons BY-SA"
    }
    
    updated = await service.update_metadata("content_123", updates)
    print(f"Metadata updated: {updated}")
    
    # Search content
    search_results = await service.search_by_metadata(
        "tutorial",
        content_type=ContentType.VIDEO,
        filters={"quality_score_min": 0.5}
    )
    print(f"Search results: {search_results}")
    
    # Get analytics
    analytics = await service.get_metadata_analytics()
    print(f"Analytics: {analytics}")
    
    # Get service metrics
    metrics = service.get_service_metrics()
    print(f"Service metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())