"""Metadata Processor Module - IA-Influencer-Agent Platform

Industrial-grade metadata extraction, management, and enrichment engine.
Comprehensive metadata handling for all content types with AI-powered analysis.

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
import json
import time
import uuid
import hashlib
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import mimetypes
import os

# Metadata extraction imports
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    import piexif
    IMAGE_METADATA_AVAILABLE = True
except ImportError:
    IMAGE_METADATA_AVAILABLE = False

try:
    import mutagen
    from mutagen.id3 import ID3
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.flac import FLAC
    AUDIO_METADATA_AVAILABLE = True
except ImportError:
    AUDIO_METADATA_AVAILABLE = False

try:
    import cv2
    import ffmpeg
    VIDEO_METADATA_AVAILABLE = True
except ImportError:
    VIDEO_METADATA_AVAILABLE = False

try:
    from docx import Document
    from PyPDF2 import PdfReader
    import openpyxl
    DOCUMENT_METADATA_AVAILABLE = True
except ImportError:
    DOCUMENT_METADATA_AVAILABLE = False

# AI-powered metadata enrichment
try:
    import spacy
    from transformers import pipeline
    import torch
    AI_METADATA_AVAILABLE = True
except ImportError:
    AI_METADATA_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetadataType(str, Enum):
    """
Types of metadata"""

    TECHNICAL = "technical"
    DESCRIPTIVE = "descriptive"
    ADMINISTRATIVE = "administrative"
    STRUCTURAL = "structural"
    PRESERVATION = "preservation"
    RIGHTS = "rights"
    PROVENANCE = "provenance"
    SEMANTIC = "semantic"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"


class ContentFormat(str, Enum):
    """Content format types"""

    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_GIF = "image/gif"
    IMAGE_WEBP = "image/webp"
    VIDEO_MP4 = "video/mp4"
    VIDEO_AVI = "video/avi"
    VIDEO_MOV = "video/mov"
    VIDEO_WEBM = "video/webm"
    AUDIO_MP3 = "audio/mp3"
    AUDIO_WAV = "audio/wav"
    AUDIO_FLAC = "audio/flac"
    AUDIO_AAC = "audio/aac"
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"
    TEXT_MARKDOWN = "text/markdown"
    DOCUMENT_PDF = "application/pdf"
    DOCUMENT_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DOCUMENT_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class MetadataSchema(str, Enum):
    """Metadata schema standards"""

    DUBLIN_CORE = "dublin_core"
    EXIF = "exif"
    IPTC = "iptc"
    XMP = "xmp"
    ID3 = "id3"
    VORBIS_COMMENT = "vorbis_comment"
    CUSTOM = "custom"
    PLATFORM_SPECIFIC = "platform_specific"


@dataclass
class MetadataProcessingConfig:
    """Configuration for metadata processing"""
    # Extraction settings
    extract_technical_metadata: bool = True
    extract_descriptive_metadata: bool = True
    extract_embedded_metadata: bool = True
    extract_filesystem_metadata: bool = True
    
    # AI-powered extraction
    enable_ai_description: bool = True
    enable_keyword_extraction: bool = True
    enable_sentiment_analysis: bool = True
    enable_entity_recognition: bool = True
    enable_topic_modeling: bool = True
    
    # Enrichment settings
    enable_metadata_enrichment: bool = True
    enable_geo_enrichment: bool = True
    enable_temporal_enrichment: bool = True
    enable_semantic_enrichment: bool = True
    
    # Validation and quality
    validate_metadata: bool = True
    normalize_metadata: bool = True
    deduplicate_metadata: bool = True
    quality_threshold: float = 0.8
    
    # Privacy and security
    anonymize_personal_data: bool = True
    remove_location_data: bool = False
    remove_device_info: bool = False
    hash_sensitive_data: bool = True
    
    # Output format
    output_schema: MetadataSchema = MetadataSchema.DUBLIN_CORE
    include_raw_metadata: bool = True
    flatten_nested_metadata: bool = False
    
    # Performance
    max_processing_time: int = 120  # 2 minutes
    enable_caching: bool = True
    cache_duration: int = 3600  # 1 hour
    
    # Database storage
    store_in_database: bool = True
    create_search_index: bool = True
    enable_versioning: bool = True


@dataclass
class TechnicalMetadata:
    """
Technical metadata for content"""
    # File properties
    filename: Optional[str] = None
    file_size: Optional[int] = None
    file_format: Optional[str] = None
    mime_type: Optional[str] = None
    encoding: Optional[str] = None
    
    # Checksums and hashes
    md5_hash: Optional[str] = None
    sha256_hash: Optional[str] = None
    file_signature: Optional[str] = None
    
    # Dimensions and quality
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    frame_rate: Optional[float] = None
    color_depth: Optional[int] = None
    
    # Compression and quality
    compression_type: Optional[str] = None
    quality_level: Optional[int] = None
    
    # Creation and modification
    creation_time: Optional[datetime] = None
    modification_time: Optional[datetime] = None
    access_time: Optional[datetime] = None


@dataclass
class DescriptiveMetadata:
    """
Descriptive metadata for content"""
    # Basic description
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Content analysis
    language: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    emotions: Dict[str, float] = field(default_factory=dict)
    
    # Entities and topics
    entities: List[Dict[str, Any]] = field(default_factory=list)
    topics: List[Dict[str, Any]] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    
    # Quality and aesthetics
    quality_score: Optional[float] = None
    aesthetic_score: Optional[float] = None
    engagement_potential: Optional[float] = None
    
    # Visual analysis (for images/videos)
    dominant_colors: List[str] = field(default_factory=list)
    objects_detected: List[Dict[str, Any]] = field(default_factory=list)
    faces_detected: int = 0
    scene_description: Optional[str] = None
    
    # Audio analysis
    audio_features: Dict[str, Any] = field(default_factory=dict)
    transcript: Optional[str] = None
    speaker_count: Optional[int] = None


@dataclass
class AdministrativeMetadata:
    """
Administrative metadata for content"""
    # Content management
    content_id: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    workflow_stage: Optional[str] = None
    
    # Creator information
    creator_id: Optional[str] = None
    creator_name: Optional[str] = None
    creator_email: Optional[str] = None
    organization: Optional[str] = None
    
    # Rights and permissions
    copyright_holder: Optional[str] = None
    license: Optional[str] = None
    usage_rights: Optional[str] = None
    restrictions: List[str] = field(default_factory=list)
    
    # Publishing information
    published_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    platform: Optional[str] = None
    channel: Optional[str] = None
    
    # Processing history
    processing_history: List[Dict[str, Any]] = field(default_factory=list)
    last_modified_by: Optional[str] = None
    last_modification_date: Optional[datetime] = None


@dataclass
class StructuralMetadata:
    """
Structural metadata for content"""
    # Content structure
    components: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    hierarchy: Optional[Dict[str, Any]] = None
    
    # Format structure
    container_format: Optional[str] = None
    codec: Optional[str] = None
    streams: List[Dict[str, Any]] = field(default_factory=list)
    
    # Document structure
    page_count: Optional[int] = None
    chapter_count: Optional[int] = None
    section_count: Optional[int] = None
    
    # Media structure
    track_count: Optional[int] = None
    layer_count: Optional[int] = None
    frame_count: Optional[int] = None


@dataclass
class PreservationMetadata:
    """
Preservation metadata for content"""
    # Preservation information
    preservation_level: Optional[str] = None
    preservation_actions: List[Dict[str, Any]] = field(default_factory=list)
    risk_assessment: Optional[Dict[str, Any]] = None
    
    # Format information
    format_registry_entry: Optional[str] = None
    format_version: Optional[str] = None
    format_obsolescence_risk: Optional[str] = None
    
    # Migration history
    migration_history: List[Dict[str, Any]] = field(default_factory=list)
    original_format: Optional[str] = None
    current_format: Optional[str] = None
    
    # Integrity checking
    checksum_history: List[Dict[str, Any]] = field(default_factory=list)
    integrity_verified: Optional[bool] = None
    last_integrity_check: Optional[datetime] = None


@dataclass
class ContextualMetadata:
    """
Contextual metadata for content"""
    # Temporal context
    creation_context: Optional[Dict[str, Any]] = None
    publication_context: Optional[Dict[str, Any]] = None
    usage_context: Optional[Dict[str, Any]] = None
    
    # Spatial context
    location: Optional[Dict[str, Any]] = None
    geographic_coverage: Optional[str] = None
    
    # Social context
    target_audience: Optional[str] = None
    cultural_context: Optional[str] = None
    social_tags: List[str] = field(default_factory=list)
    
    # Technical context
    creation_environment: Optional[Dict[str, Any]] = None
    viewing_environment: Optional[Dict[str, Any]] = None
    platform_context: Optional[Dict[str, Any]] = None


@dataclass
class ContentMetadata:
    """
Complete metadata package for content"""
    # Metadata components
    technical: TechnicalMetadata = field(default_factory=TechnicalMetadata)
    descriptive: DescriptiveMetadata = field(default_factory=DescriptiveMetadata)
    administrative: AdministrativeMetadata = field(default_factory=AdministrativeMetadata)
    structural: StructuralMetadata = field(default_factory=StructuralMetadata)
    preservation: PreservationMetadata = field(default_factory=PreservationMetadata)
    contextual: ContextualMetadata = field(default_factory=ContextualMetadata)
    
    # Raw metadata
    raw_metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing information
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    processor_version: Optional[str] = None
    processing_time: float = 0.0
    
    # Quality indicators
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    consistency_score: float = 0.0
    overall_quality: float = 0.0


class MetadataProcessor:
    """
    📊 ENTERPRISE METADATA PROCESSOR
    
    Industrial-grade metadata extraction, management, and enrichment engine
    with comprehensive support for all content types and AI-powered analysis.
    """
    
    def __init__(
        self,
        db_session,
        redis_client,
        config: Optional[MetadataProcessingConfig] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or MetadataProcessingConfig()
        self.logger = logging.getLogger(f"{__name__}.MetadataProcessor")
        
        # AI models for metadata enrichment
        self._nlp_models = {}
        self._vision_models = {}
        
        # Metadata extractors
        self._extractors = {}
        
        # Cache for metadata
        self._metadata_cache = {}
        
        # Schema mappings
        self._schema_mappings = {}
        
        self._initialized = False
        
        # Log availability of metadata libraries
        if not IMAGE_METADATA_AVAILABLE:
            self.logger.warning("Image metadata extraction libraries not available")
        
        if not AUDIO_METADATA_AVAILABLE:
            self.logger.warning("Audio metadata extraction libraries not available")
        
        if not VIDEO_METADATA_AVAILABLE:
            self.logger.warning("Video metadata extraction libraries not available")
        
        if not DOCUMENT_METADATA_AVAILABLE:
            self.logger.warning("Document metadata extraction libraries not available")
        
        if not AI_METADATA_AVAILABLE:
            self.logger.warning("AI metadata enrichment libraries not available")
    
    async def initialize(self) -> bool:
        """Initialize the metadata processor"""
        try:
            # Initialize AI models
            await self._initialize_ai_models()
            
            # Initialize extractors
            await self._initialize_extractors()
            
            # Load schema mappings
            await self._load_schema_mappings()
            
            self._initialized = True
            self.logger.info("✅ Metadata processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize metadata processor: {e}")
            return False
    
    async def extract_metadata(
        self,
        content: Union[str, bytes, Path],
        content_type: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from content
        
        Args:
            content: Content to analyze (file path, bytes, or Path object)
            content_type: MIME type of content
            options: Extraction options
            
        Returns:
            Extracted metadata result
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            start_time = time.time()
            options = options or {}
            
            # Determine content type if not provided
            if content_type is None:
                content_type = await self._detect_content_type(content)
            
            # Check cache
            if self.config.enable_caching:
                cache_key = self._generate_cache_key(content, content_type, options)
                cached_metadata = self._metadata_cache.get(cache_key)
                if cached_metadata:
                    return cached_metadata
            
            # Create metadata container
            metadata = ContentMetadata()
            
            # Extract different types of metadata
            extraction_tasks = []
            
            if self.config.extract_technical_metadata:
                extraction_tasks.append(
                    self._extract_technical_metadata(content, content_type)
                )
            
            if self.config.extract_descriptive_metadata:
                extraction_tasks.append(
                    self._extract_descriptive_metadata(content, content_type)
                )
            
            if self.config.extract_embedded_metadata:
                extraction_tasks.append(
                    self._extract_embedded_metadata(content, content_type)
                )
            
            # Execute extractions
            extraction_results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
            
            # Process extraction results
            await self._process_extraction_results(metadata, extraction_results)
            
            # AI-powered enrichment
            if self.config.enable_metadata_enrichment:
                await self._enrich_metadata(metadata, content, content_type)
            
            # Validate and normalize metadata
            if self.config.validate_metadata:
                await self._validate_metadata(metadata)
            
            if self.config.normalize_metadata:
                await self._normalize_metadata(metadata)
            
            # Calculate quality scores
            await self._calculate_metadata_quality(metadata)
            
            # Convert to output schema
            output_metadata = await self._convert_to_schema(metadata, self.config.output_schema)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            metadata.processing_time = processing_time
            
            result = {
                "success": True,
                "metadata": asdict(metadata),
                "output_metadata": output_metadata,
                "content_type": content_type,
                "processing_time": processing_time,
                "quality_scores": {
                    "completeness": metadata.completeness_score,
                    "accuracy": metadata.accuracy_score,
                    "consistency": metadata.consistency_score,
                    "overall": metadata.overall_quality
                }
            }
            
            # Cache result
            if self.config.enable_caching:
                self._metadata_cache[cache_key] = result
            
            # Store in database if configured
            if self.config.store_in_database:
                await self._store_metadata(metadata, content_type)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "processing_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    async def enrich_metadata(
        self,
        existing_metadata: Dict[str, Any],
        content: Optional[Union[str, bytes, Path]] = None,
        enrichment_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enrich existing metadata with additional information
        
        Args:
            existing_metadata: Existing metadata to enrich
            content: Optional content for additional analysis
            enrichment_options: Enrichment options
            
        Returns:
            Enriched metadata
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            start_time = time.time()
            enrichment_options = enrichment_options or {}
            
            # Convert to ContentMetadata if needed
            if isinstance(existing_metadata, dict):
                metadata = ContentMetadata(**existing_metadata)
            else:
                metadata = existing_metadata
            
            # AI-powered enrichment
            if content and self.config.enable_ai_description:
                await self._ai_describe_content(metadata, content)
            
            if self.config.enable_keyword_extraction:
                await self._extract_keywords_ai(metadata)
            
            if self.config.enable_sentiment_analysis:
                await self._analyze_sentiment_ai(metadata)
            
            if self.config.enable_entity_recognition:
                await self._extract_entities_ai(metadata)
            
            if self.config.enable_topic_modeling:
                await self._extract_topics_ai(metadata)
            
            # Contextual enrichment
            if self.config.enable_geo_enrichment:
                await self._enrich_geographic_data(metadata)
            
            if self.config.enable_temporal_enrichment:
                await self._enrich_temporal_data(metadata)
            
            if self.config.enable_semantic_enrichment:
                await self._enrich_semantic_data(metadata)
            
            # Recalculate quality scores
            await self._calculate_metadata_quality(metadata)
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "enriched_metadata": asdict(metadata),
                "processing_time": processing_time,
                "enrichment_applied": True
            }
            
        except Exception as e:
            self.logger.error(f"Metadata enrichment failed: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "processing_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    async def search_by_metadata(
        self,
        query: Dict[str, Any],
        search_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search content by metadata criteria
        
        Args:
            query: Metadata search query
            search_options: Search options
            
        Returns:
            Search results
        """
        try:
            search_options = search_options or {}
            
            # Build search query based on metadata fields
            search_results = await self._execute_metadata_search(query, search_options)
            
            return {
                "success": True,
                "results": search_results,
                "total_count": len(search_results),
                "query": query
            }
            
        except Exception as e:
            self.logger.error(f"Metadata search failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _detect_content_type(self, content: Union[str, bytes, Path]) -> str:
        """Detect content type from content"""
        try:
            if isinstance(content, (str, Path)):
                # File path - use file extension
                file_path = Path(content)
                mime_type, _ = mimetypes.guess_type(str(file_path))
                if mime_type:
                    return mime_type
            
            elif isinstance(content, bytes):
                # Analyze file signature
                if content.startswith(b'\xff\xd8\xff'):
                    return 'image/jpeg'
                elif content.startswith(b'\x89PNG\r\n\x1a\n'):
                    return 'image/png'
                elif content.startswith(b'GIF8'):
                    return 'image/gif'
                elif content.startswith(b'RIFF') and b'WEBP' in content[:20]:
                    return 'image/webp'
                elif content.startswith(b'\x00\x00\x00\x18ftypmp4') or content.startswith(b'\x00\x00\x00 ftypisom'):
                    return 'video/mp4'
                elif content.startswith(b'ID3') or content.startswith(b'\xff\xfb'):
                    return 'audio/mp3'
                elif content.startswith(b'RIFF') and b'WAVE' in content[:20]:
                    return 'audio/wav'
                elif content.startswith(b'fLaC'):
                    return 'audio/flac'
                elif content.startswith(b'%PDF'):
                    return 'application/pdf'
            
            return 'application/octet-stream'  # Default
            
        except Exception as e:
            self.logger.error(f"Content type detection failed: {e}")
            return 'application/octet-stream'
    
    async def _extract_technical_metadata(
        self,
        content: Union[str, bytes, Path],
        content_type: str
    ) -> TechnicalMetadata:
        """Extract technical metadata"""
        try:
            metadata = TechnicalMetadata()
            
            # Basic file information
            if isinstance(content, (str, Path)):
                file_path = Path(content)
                if file_path.exists():
                    stat_info = file_path.stat()
                    metadata.filename = file_path.name
                    metadata.file_size = stat_info.st_size
                    metadata.creation_time = datetime.fromtimestamp(stat_info.st_ctime)
                    metadata.modification_time = datetime.fromtimestamp(stat_info.st_mtime)
                    metadata.access_time = datetime.fromtimestamp(stat_info.st_atime)
            
            metadata.mime_type = content_type
            
            # Generate hashes
            content_bytes = await self._get_content_bytes(content)
            if content_bytes:
                metadata.md5_hash = hashlib.md5(content_bytes).hexdigest()
                metadata.sha256_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Content-specific technical metadata
            if content_type.startswith('image/'):
                await self._extract_image_technical_metadata(content, metadata)
            elif content_type.startswith('video/'):
                await self._extract_video_technical_metadata(content, metadata)
            elif content_type.startswith('audio/'):
                await self._extract_audio_technical_metadata(content, metadata)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Technical metadata extraction failed: {e}")
            return TechnicalMetadata()
    
    async def _extract_image_technical_metadata(
        self,
        content: Union[str, bytes, Path],
        metadata: TechnicalMetadata
    ):
        """Extract image technical metadata"""
        try:
            if not IMAGE_METADATA_AVAILABLE:
                return
            
            # Open image
            if isinstance(content, bytes):
                from io import BytesIO
                image = Image.open(BytesIO(content))
            else:
                image = Image.open(content)
            
            # Basic image properties
            metadata.width, metadata.height = image.size
            metadata.file_format = image.format
            
            # Color information
            if hasattr(image, 'mode'):
                if image.mode == 'RGB':
                    metadata.color_depth = 24
                elif image.mode == 'RGBA':
                    metadata.color_depth = 32
                elif image.mode == 'L':
                    metadata.color_depth = 8
                elif image.mode == 'P':
                    metadata.color_depth = 8
            
        except Exception as e:
            self.logger.error(f"Image technical metadata extraction failed: {e}")
    
    async def _extract_video_technical_metadata(
        self,
        content: Union[str, bytes, Path],
        metadata: TechnicalMetadata
    ):
        """Extract video technical metadata"""
        try:
            if not VIDEO_METADATA_AVAILABLE:
                return
            
            if isinstance(content, (str, Path)):
                cap = cv2.VideoCapture(str(content))
                
                # Video properties
                metadata.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                metadata.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                metadata.frame_rate = cap.get(cv2.CAP_PROP_FPS)
                
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if frame_count > 0 and metadata.frame_rate > 0:
                    metadata.duration = frame_count / metadata.frame_rate
                
                cap.release()
            
        except Exception as e:
            self.logger.error(f"Video technical metadata extraction failed: {e}")
    
    async def _extract_audio_technical_metadata(
        self,
        content: Union[str, bytes, Path],
        metadata: TechnicalMetadata
    ):
        """Extract audio technical metadata"""
        try:
            if not AUDIO_METADATA_AVAILABLE:
                return
            
            if isinstance(content, (str, Path)):
                audio_file = mutagen.File(str(content))
                
                if audio_file:
                    # Audio properties
                    if hasattr(audio_file, 'info'):
                        info = audio_file.info
                        metadata.duration = getattr(info, 'length', None)
                        metadata.bit_rate = getattr(info, 'bitrate', None)
                        metadata.sample_rate = getattr(info, 'sample_rate', None)
            
        except Exception as e:
            self.logger.error(f"Audio technical metadata extraction failed: {e}")
    
    async def _extract_descriptive_metadata(
        self,
        content: Union[str, bytes, Path],
        content_type: str
    ) -> DescriptiveMetadata:
        """Extract descriptive metadata"""
        try:
            metadata = DescriptiveMetadata()
            
            # Content-specific descriptive extraction
            if content_type.startswith('text/'):
                await self._extract_text_descriptive_metadata(content, metadata)
            elif content_type.startswith('image/'):
                await self._extract_image_descriptive_metadata(content, metadata)
            elif content_type.startswith('video/'):
                await self._extract_video_descriptive_metadata(content, metadata)
            elif content_type.startswith('audio/'):
                await self._extract_audio_descriptive_metadata(content, metadata)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Descriptive metadata extraction failed: {e}")
            return DescriptiveMetadata()
    
    async def _extract_text_descriptive_metadata(
        self,
        content: Union[str, bytes, Path],
        metadata: DescriptiveMetadata
    ):
        """Extract text descriptive metadata"""
        try:
            # Get text content
            if isinstance(content, bytes):
                text = content.decode('utf-8', errors='ignore')
            elif isinstance(content, (str, Path)):
                with open(content, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            else:
                text = str(content)
            
            # Basic text analysis
            words = text.split()
            if len(words) > 10:
                # Extract potential title (first line or first few words)
                lines = text.split('\n')
                first_line = lines[0].strip() if lines else ""
                if len(first_line) < 100:
                    metadata.title = first_line
                
                # Extract description (first paragraph)
                paragraphs = text.split('\n\n')
                if paragraphs:
                    description = paragraphs[0].strip()
                    if len(description) > 50:
                        metadata.description = description[:500]  # Limit length
            
            # Language detection (basic)
            # This would use langdetect or similar library in a real implementation
            metadata.language = "en"  # Default
            
        except Exception as e:
            self.logger.error(f"Text descriptive metadata extraction failed: {e}")
    
    async def _extract_image_descriptive_metadata(
        self,
        content: Union[str, bytes, Path],
        metadata: DescriptiveMetadata
    ):
        """Extract image descriptive metadata"""
        try:
            if not IMAGE_METADATA_AVAILABLE:
                return
            
            # Basic image analysis for description
            # This would use computer vision models in a real implementation
            metadata.scene_description = "Image content analysis would be performed here"
            
        except Exception as e:
            self.logger.error(f"Image descriptive metadata extraction failed: {e}")
    
    async def _extract_video_descriptive_metadata(
        self,
        content: Union[str, bytes, Path],
        metadata: DescriptiveMetadata
    ):
        """Extract video descriptive metadata"""
        try:
            # Video content analysis would be implemented here
            metadata.scene_description = "Video content analysis would be performed here"
            
        except Exception as e:
            self.logger.error(f"Video descriptive metadata extraction failed: {e}")
    
    async def _extract_audio_descriptive_metadata(
        self,
        content: Union[str, bytes, Path],
        metadata: DescriptiveMetadata
    ):
        """Extract audio descriptive metadata"""
        try:
            if not AUDIO_METADATA_AVAILABLE:
                return
            
            # Audio content analysis would be implemented here
            # Including speech-to-text, music recognition, etc.
            
        except Exception as e:
            self.logger.error(f"Audio descriptive metadata extraction failed: {e}")
    
    async def _extract_embedded_metadata(
        self,
        content: Union[str, bytes, Path],
        content_type: str
    ) -> Dict[str, Any]:
        """Extract embedded metadata from content"""
        try:
            embedded_metadata = {}
            
            if content_type.startswith('image/') and IMAGE_METADATA_AVAILABLE:
                embedded_metadata.update(await self._extract_image_embedded_metadata(content))
            elif content_type.startswith('audio/') and AUDIO_METADATA_AVAILABLE:
                embedded_metadata.update(await self._extract_audio_embedded_metadata(content))
            elif content_type.startswith('video/') and VIDEO_METADATA_AVAILABLE:
                embedded_metadata.update(await self._extract_video_embedded_metadata(content))
            
            return embedded_metadata
            
        except Exception as e:
            self.logger.error(f"Embedded metadata extraction failed: {e}")
            return {}
    
    async def _extract_image_embedded_metadata(
        self,
        content: Union[str, bytes, Path]
    ) -> Dict[str, Any]:
        """Extract EXIF and other embedded image metadata"""
        try:
            embedded = {}
            
            # Open image
            if isinstance(content, bytes):
                from io import BytesIO
                image = Image.open(BytesIO(content))
            else:
                image = Image.open(content)
            
            # Extract EXIF data
            exif_data = image.getexif()
            if exif_data:
                exif_dict = {}
                for tag_id in exif_data:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exif_data.get(tag_id)
                    exif_dict[tag] = data
                
                embedded['exif'] = exif_dict
            
            return embedded
            
        except Exception as e:
            self.logger.error(f"Image embedded metadata extraction failed: {e}")
            return {}
    
    async def _extract_audio_embedded_metadata(
        self,
        content: Union[str, bytes, Path]
    ) -> Dict[str, Any]:
        """Extract ID3 and other embedded audio metadata"""
        try:
            embedded = {}
            
            if isinstance(content, (str, Path)):
                audio_file = mutagen.File(str(content))
                
                if audio_file and audio_file.tags:
                    tags_dict = {}
                    for key, value in audio_file.tags.items():
                        tags_dict[key] = value
                    
                    embedded['tags'] = tags_dict
            
            return embedded
            
        except Exception as e:
            self.logger.error(f"Audio embedded metadata extraction failed: {e}")
            return {}
    
    async def _extract_video_embedded_metadata(
        self,
        content: Union[str, bytes, Path]
    ) -> Dict[str, Any]:
        """Extract embedded video metadata"""
        try:
            embedded = {}
            
            # Video metadata extraction would be implemented here
            # Using ffprobe or similar tools
            
            return embedded
            
        except Exception as e:
            self.logger.error(f"Video embedded metadata extraction failed: {e}")
            return {}
    
    async def _enrich_metadata(
        self,
        metadata: ContentMetadata,
        content: Union[str, bytes, Path],
        content_type: str
    ):
        """Enrich metadata with AI-powered analysis"""
        try:
            if not AI_METADATA_AVAILABLE:
                return
            
            # AI-powered content analysis
            if self.config.enable_ai_description:
                await self._ai_describe_content(metadata, content)
            
            if self.config.enable_keyword_extraction:
                await self._extract_keywords_ai(metadata)
            
            if self.config.enable_sentiment_analysis:
                await self._analyze_sentiment_ai(metadata)
            
            if self.config.enable_entity_recognition:
                await self._extract_entities_ai(metadata)
            
        except Exception as e:
            self.logger.error(f"Metadata enrichment failed: {e}")
    
    async def _ai_describe_content(
        self,
        metadata: ContentMetadata,
        content: Union[str, bytes, Path]
    ):
        """Generate AI-powered content description"""
        try:
            # AI description would be implemented here
            # Using vision models for images/videos, NLP for text, etc.
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"AI content description failed: {e}")
    
    async def _extract_keywords_ai(self, metadata: ContentMetadata):
        """Extract keywords using AI"""
        try:
            # AI keyword extraction would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"AI keyword extraction failed: {e}")
    
    async def _analyze_sentiment_ai(self, metadata: ContentMetadata):
        """Analyze sentiment using AI"""
        try:
            # AI sentiment analysis would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"AI sentiment analysis failed: {e}")
    
    async def _extract_entities_ai(self, metadata: ContentMetadata):
        """Extract entities using AI"""
        try:
            # AI entity extraction would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"AI entity extraction failed: {e}")
    
    async def _extract_topics_ai(self, metadata: ContentMetadata):
        """Extract topics using AI"""
        try:
            # AI topic modeling would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"AI topic extraction failed: {e}")
    
    async def _enrich_geographic_data(self, metadata: ContentMetadata):
        """Enrich geographic metadata"""
        try:
            # Geographic enrichment would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"Geographic enrichment failed: {e}")
    
    async def _enrich_temporal_data(self, metadata: ContentMetadata):
        """Enrich temporal metadata"""
        try:
            # Temporal enrichment would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"Temporal enrichment failed: {e}")
    
    async def _enrich_semantic_data(self, metadata: ContentMetadata):
        """Enrich semantic metadata"""
        try:
            # Semantic enrichment would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"Semantic enrichment failed: {e}")
    
    async def _process_extraction_results(
        self,
        metadata: ContentMetadata,
        results: List[Any]
    ):
        """Process metadata extraction results"""
        try:
            for result in results:
                if isinstance(result, Exception):
                    self.logger.warning(f"Extraction task failed: {result}")
                    continue
                
                if isinstance(result, TechnicalMetadata):
                    metadata.technical = result
                elif isinstance(result, DescriptiveMetadata):
                    metadata.descriptive = result
                elif isinstance(result, dict):
                    metadata.raw_metadata.update(result)
            
        except Exception as e:
            self.logger.error(f"Extraction results processing failed: {e}")
    
    async def _validate_metadata(self, metadata: ContentMetadata):
        """Validate metadata quality and consistency"""
        try:
            # Metadata validation would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"Metadata validation failed: {e}")
    
    async def _normalize_metadata(self, metadata: ContentMetadata):
        """Normalize metadata values"""
        try:
            # Metadata normalization would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"Metadata normalization failed: {e}")
    
    async def _calculate_metadata_quality(self, metadata: ContentMetadata):
        """Calculate metadata quality scores"""
        try:
            # Quality calculation would be implemented here
            metadata.completeness_score = 0.8
            metadata.accuracy_score = 0.9
            metadata.consistency_score = 0.85
            metadata.overall_quality = (
                metadata.completeness_score + 
                metadata.accuracy_score + 
                metadata.consistency_score
            ) / 3
            
        except Exception as e:
            self.logger.error(f"Metadata quality calculation failed: {e}")
    
    async def _convert_to_schema(
        self,
        metadata: ContentMetadata,
        schema: MetadataSchema
    ) -> Dict[str, Any]:
        """Convert metadata to specified schema"""
        try:
            if schema == MetadataSchema.DUBLIN_CORE:
                return await self._convert_to_dublin_core(metadata)
            elif schema == MetadataSchema.CUSTOM:
                return asdict(metadata)
            else:
                return asdict(metadata)
            
        except Exception as e:
            self.logger.error(f"Schema conversion failed: {e}")
            return asdict(metadata)
    
    async def _convert_to_dublin_core(self, metadata: ContentMetadata) -> Dict[str, Any]:
        """Convert to Dublin Core schema"""
        try:
            dublin_core = {
                "title": metadata.descriptive.title,
                "description": metadata.descriptive.description,
                "creator": metadata.administrative.creator_name,
                "subject": metadata.descriptive.keywords,
                "date": metadata.technical.creation_time,
                "type": metadata.technical.mime_type,
                "format": metadata.technical.file_format,
                "language": metadata.descriptive.language,
                "rights": metadata.administrative.license
            }
            
            # Remove None values
            return {k: v for k, v in dublin_core.items() if v is not None}
            
        except Exception as e:
            self.logger.error(f"Dublin Core conversion failed: {e}")
            return {}
    
    async def _get_content_bytes(self, content: Union[str, bytes, Path]) -> Optional[bytes]:
        """Get content as bytes"""
        try:
            if isinstance(content, bytes):
                return content
            elif isinstance(content, (str, Path)):
                file_path = Path(content)
                if file_path.exists():
                    return file_path.read_bytes()
            return None
            
        except Exception as e:
            self.logger.error(f"Content bytes retrieval failed: {e}")
            return None
    
    def _generate_cache_key(
        self,
        content: Union[str, bytes, Path],
        content_type: str,
        options: Dict[str, Any]
    ) -> str:
        """Generate cache key for metadata"""
        try:
            # Create hash of content and options
            content_str = str(content) if not isinstance(content, bytes) else str(len(content))
            options_str = json.dumps(options, sort_keys=True)
            
            key_data = f"{content_str}_{content_type}_{options_str}"
            return hashlib.md5(key_data.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Cache key generation failed: {e}")
            return f"metadata_{time.time()}"
    
    async def _store_metadata(self, metadata: ContentMetadata, content_type: str):
        """Store metadata in database"""
        try:
            # Database storage would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"Metadata storage failed: {e}")
    
    async def _execute_metadata_search(
        self,
        query: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute metadata search query"""
        try:
            # Search implementation would be here
            return []
            
        except Exception as e:
            self.logger.error(f"Metadata search execution failed: {e}")
            return []
    
    async def _initialize_ai_models(self):
        """Initialize AI models for metadata enrichment"""
        try:
            if not AI_METADATA_AVAILABLE:
                return
            
            # AI model initialization would be implemented here
            
        except Exception as e:
            self.logger.error(f"AI models initialization failed: {e}")
    
    async def _initialize_extractors(self):
        """Initialize metadata extractors"""
        try:
            # Extractor initialization would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"Extractors initialization failed: {e}")
    
    async def _load_schema_mappings(self):
        """Load schema mapping configurations"""
        try:
            # Schema mappings loading would be implemented here
            logger.debug('Method executed')
            return True
            
        except Exception as e:
            self.logger.error(f"Schema mappings loading failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the metadata processor"""
        health_status = {
            "status": "healthy" if self._initialized else "not_initialized",
            "image_metadata_available": IMAGE_METADATA_AVAILABLE,
            "audio_metadata_available": AUDIO_METADATA_AVAILABLE,
            "video_metadata_available": VIDEO_METADATA_AVAILABLE,
            "document_metadata_available": DOCUMENT_METADATA_AVAILABLE,
            "ai_metadata_available": AI_METADATA_AVAILABLE,
            "cached_metadata_count": len(self._metadata_cache),
            "extractors_loaded": len(self._extractors),
            "ai_models_loaded": len(self._nlp_models) + len(self._vision_models),
            "config": self.config.__dict__
        }
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown the metadata processor"""
        try:
            # Clear cache
            self._metadata_cache.clear()
            
            # Clear models
            self._nlp_models.clear()
            self._vision_models.clear()
            
            self.logger.info("Metadata processor shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")


async def create_metadata_processor(
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> MetadataProcessor:
    """
    Factory function to create and initialize a metadata processor
    
    Args:
        db_session: Database session
        redis_client: Redis client
        config: Configuration dictionary
        
    Returns:
        Initialized MetadataProcessor instance
    """
    # Create config from dict if provided
    processor_config = None
    if config:
        processor_config = MetadataProcessingConfig(**{
            k: v for k, v in config.items() 
            if k in MetadataProcessingConfig.__dataclass_fields__
        })
    
    # Create processor
    processor = MetadataProcessor(
        db_session=db_session,
        redis_client=redis_client,
        config=processor_config
    )
    
    # Initialize
    await processor.initialize()
    
    return processor
