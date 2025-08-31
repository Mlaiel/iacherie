"""Metadata Entity Parser - Advanced Metadata Extraction and Analysis

Comprehensive metadata extraction from various content formats including
audio files, video files, images, documents, and social media content.
Specialized for creative industry metadata and content identification.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
import asyncio
import os
import re
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import json
import mimetypes

import numpy as np
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TPE2
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from PIL import Image
from PIL.ExifTags import TAGS
import cv2

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...utils.text_processors import TextPreprocessor
from .entity_extractor import ExtractedEntity, EntityCategory


class MetadataFormat(Enum):
    """Supported metadata formats"""    AUDIO_ID3 = "audio_id3"
    AUDIO_MP4 = "audio_mp4"
    AUDIO_FLAC = "audio_flac"
    AUDIO_VORBIS = "audio_vorbis"
    IMAGE_EXIF = "image_exif"
    IMAGE_IPTC = "image_iptc"
    VIDEO_MP4 = "video_mp4"
    VIDEO_AVI = "video_avi"
    DOCUMENT_PDF = "document_pdf"
    SOCIAL_MEDIA = "social_media"
    WEB_METADATA = "web_metadata"


class MetadataEntityType(Enum):
    """Types of entities extracted from metadata"""    ARTIST_NAME = "artist_name"
    ALBUM_TITLE = "album_title"
    TRACK_TITLE = "track_title"
    GENRE_TAG = "genre_tag"
    CREATION_DATE = "creation_date"
    COPYRIGHT_INFO = "copyright_info"
    PUBLISHER_INFO = "publisher_info"
    PRODUCTION_INFO = "production_info"
    TECHNICAL_SPECS = "technical_specs"
    LOCATION_DATA = "location_data"
    EQUIPMENT_INFO = "equipment_info"
    SOCIAL_TAGS = "social_tags"
    PLATFORM_DATA = "platform_data"
    COLLABORATION_DATA = "collaboration_data"


@dataclass
class MetadataEntity:
    """Entity extracted from metadata"""    entity: ExtractedEntity
    metadata_type: MetadataEntityType
    metadata_format: MetadataFormat
    raw_value: Any
    normalized_value: str
    confidence: float
    technical_details: Dict[str, Any] = field(default_factory=dict)
    relationships: List[str] = field(default_factory=list)


@dataclass
class MetadataAnalysisResult:
    """Result of metadata analysis"""    metadata_entities: List[MetadataEntity]
    technical_profile: Dict[str, Any]
    content_fingerprint: Dict[str, Any]
    quality_assessment: Dict[str, float]
    platform_compatibility: Dict[str, bool]
    rights_information: Dict[str, Any]
    collaboration_network: Dict[str, List[str]]
    processing_time: float
    confidence_score: float


class MetadataEntityParser(BaseService):
    """    Advanced Metadata Entity Parser for creative content analysis.
    
    Features:
    - Multi-format metadata extraction (audio, video, image, document)
    - Creative industry metadata specialization
    - Rights and copyright information extraction
    - Technical specification analysis
    - Platform compatibility assessment
    - Collaboration network mapping
    - Content fingerprinting and quality assessment
    - Automated metadata validation and correction
    """    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("metadata_entity_parser")
        self.text_processor = TextPreprocessor()
        
        # Metadata extraction libraries
        self.audio_parsers = {}
        self.image_parsers = {}
        self.video_parsers = {}
        
        # Metadata schemas and mappings
        self.metadata_schemas = {}
        self.field_mappings = {}
        self.normalization_rules = {}
        
        # Content analysis tools
        self.quality_analyzers = {}
        self.fingerprint_generators = {}
        
        # Processing cache
        self.metadata_cache = {}
        
        # Statistics
        self.parsing_stats = {
            'total_files_processed': 0,
            'successful_extractions': 0,
            'format_distribution': {},
            'entity_type_distribution': {},
            'avg_processing_time': 0.0,
            'quality_scores': []
        }
    
    async def initialize(self):
        """Initialize metadata parsing resources"""        try:
            self.logger.info("Initializing MetadataEntityParser...")
            
            # Initialize metadata parsers
            await self._initialize_metadata_parsers()
            
            # Load metadata schemas
            await self._load_metadata_schemas()
            
            # Initialize field mappings
            await self._initialize_field_mappings()
            
            # Load normalization rules
            await self._load_normalization_rules()
            
            # Initialize quality analyzers
            await self._initialize_quality_analyzers()
            
            self.logger.info("MetadataEntityParser initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MetadataEntityParser: {str(e)}")
            raise
    
    async def _initialize_metadata_parsers(self):
        """Initialize comprehensive metadata parsing libraries and frameworks"""        # Audio metadata parsers with advanced capabilities
        self.audio_parsers = {
            'mp3': self._parse_mp3_metadata,
            'mp4': self._parse_mp4_metadata,
            'flac': self._parse_flac_metadata,
            'ogg': self._parse_ogg_metadata,
            'wav': self._parse_wav_metadata,
            'aac': self._parse_aac_metadata,
            'wma': self._parse_wma_metadata,
            'm4a': self._parse_m4a_metadata
        }
        
        # Image metadata parsers with EXIF, IPTC, and XMP support
        self.image_parsers = {
            'jpg': self._parse_jpg_metadata,
            'jpeg': self._parse_jpg_metadata,
            'png': self._parse_png_metadata,
            'tiff': self._parse_tiff_metadata,
            'raw': self._parse_raw_metadata,
            'webp': self._parse_webp_metadata,
            'gif': self._parse_gif_metadata,
            'bmp': self._parse_bmp_metadata
        }
        
        # Video metadata parsers with comprehensive technical analysis
        self.video_parsers = {
            'mp4': self._parse_mp4_video_metadata,
            'avi': self._parse_avi_metadata,
            'mov': self._parse_mov_metadata,
            'mkv': self._parse_mkv_metadata,
            'webm': self._parse_webm_metadata,
            'flv': self._parse_flv_metadata,
            'wmv': self._parse_wmv_metadata,
            '3gp': self._parse_3gp_metadata
        }
        
        # Document metadata parsers
        self.document_parsers = {
            'pdf': self._parse_pdf_metadata,
            'doc': self._parse_doc_metadata,
            'docx': self._parse_docx_metadata,
            'txt': self._parse_txt_metadata,
            'md': self._parse_markdown_metadata,
            'html': self._parse_html_metadata,
            'xml': self._parse_xml_metadata
        }
        
        # Social media metadata parsers
        self.social_parsers = {
            'youtube': self._parse_youtube_metadata,
            'instagram': self._parse_instagram_metadata,
            'tiktok': self._parse_tiktok_metadata,
            'spotify': self._parse_spotify_metadata,
            'soundcloud': self._parse_soundcloud_metadata,
            'twitter': self._parse_twitter_metadata,
            'facebook': self._parse_facebook_metadata,
            'linkedin': self._parse_linkedin_metadata
        }
        
        # Platform-specific API metadata extractors
        self.api_extractors = {
            'youtube_api': self._extract_youtube_api_metadata,
            'spotify_api': self._extract_spotify_api_metadata,
            'instagram_api': self._extract_instagram_api_metadata,
            'tiktok_api': self._extract_tiktok_api_metadata,
            'soundcloud_api': self._extract_soundcloud_api_metadata
        }
        
        # Advanced metadata analysis tools
        self.advanced_analyzers = {
            'audio_fingerprinting': self._analyze_audio_fingerprint,
            'image_recognition': self._analyze_image_content,
            'video_analysis': self._analyze_video_content,
            'text_analysis': self._analyze_text_content,
            'rights_detection': self._analyze_rights_information,
            'collaboration_mapping': self._map_collaboration_network
        }
        
        # Initialize ML models for metadata analysis
        await self._initialize_ml_metadata_models()
        
        self.logger.info("Comprehensive metadata parsers initialized successfully")
    
    async def _initialize_ml_metadata_models(self):
        """Initialize machine learning models for intelligent metadata analysis"""        try:
            # Audio classification model for genre/mood detection
            self.audio_classifier = pipeline(
                "audio-classification",
                model="facebook/wav2vec2-base-960h",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Image content recognition model
            self.image_classifier = pipeline(
                "image-classification",
                model="google/vit-base-patch16-224",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Object detection for image analysis
            self.object_detector = pipeline(
                "object-detection",
                model="facebook/detr-resnet-50",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Text analysis for embedded text in metadata
            self.text_analyzer = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True
            )
            
            # Rights and copyright detection model
            self.rights_detector = self._initialize_rights_detection_model()
            
            # Quality assessment model for metadata completeness
            self.quality_assessor = self._initialize_quality_assessment_model()
            
            # Content similarity model for duplicate detection
            self.similarity_detector = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            self.logger.info("ML metadata models initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"Some ML models failed to load: {e}")
            await self._load_fallback_models()
    
    def _initialize_rights_detection_model(self):
        """Initialize model for detecting rights and copyright information"""        import torch.nn as nn
        
        class RightsDetectionModel(nn.Module):
            def __init__(self, vocab_size=30000, embedding_dim=256, hidden_dim=512):
                super(RightsDetectionModel, self).__init__()
                self.embedding = nn.Embedding(vocab_size, embedding_dim)
                self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
                self.dropout = nn.Dropout(0.3)
                
                # Multiple classification heads for different rights aspects
                self.copyright_classifier = nn.Linear(hidden_dim * 2, 3)  # none, partial, full
                self.license_classifier = nn.Linear(hidden_dim * 2, 5)   # different license types
                self.ownership_classifier = nn.Linear(hidden_dim * 2, 4) # individual, company, multiple, unknown
                
            def forward(self, input_ids):
                embeddings = self.embedding(input_ids)
                lstm_out, _ = self.lstm(embeddings)
                lstm_out = self.dropout(lstm_out)
                
                # Global max pooling
                pooled = torch.max(lstm_out, dim=1)[0]
                
                return {
                    'copyright': torch.softmax(self.copyright_classifier(pooled), dim=1),
                    'license': torch.softmax(self.license_classifier(pooled), dim=1),
                    'ownership': torch.softmax(self.ownership_classifier(pooled), dim=1)
                }
        
        model = RightsDetectionModel()
        
        # Load pre-trained weights if available
        rights_model_path = self.config.get('rights_detection_model_path')
        if rights_model_path:
            try:
                model.load_state_dict(torch.load(rights_model_path))
                self.logger.info("Loaded pre-trained rights detection model")
            except Exception as e:
                self.logger.warning(f"Could not load rights model weights: {e}")
        
        return model
    
    def _initialize_quality_assessment_model(self):
        """Initialize model for assessing metadata quality and completeness"""        import torch.nn as nn
        
        class MetadataQualityAssessor(nn.Module):
            def __init__(self, input_dim=100, hidden_dims=[256, 128, 64]):
                super(MetadataQualityAssessor, self).__init__()
                
                layers = []
                prev_dim = input_dim
                
                for hidden_dim in hidden_dims:
                    layers.extend([
                        nn.Linear(prev_dim, hidden_dim),
                        nn.ReLU(),
                        nn.BatchNorm1d(hidden_dim),
                        nn.Dropout(0.25)
                    ])
                    prev_dim = hidden_dim
                
                # Quality scoring heads
                self.completeness_score = nn.Linear(prev_dim, 1)
                self.accuracy_score = nn.Linear(prev_dim, 1)
                self.consistency_score = nn.Linear(prev_dim, 1)
                self.richness_score = nn.Linear(prev_dim, 1)
                
                self.shared_layers = nn.Sequential(*layers)
                
            def forward(self, x):
                features = self.shared_layers(x)
                
                return {
                    'completeness': torch.sigmoid(self.completeness_score(features)),
                    'accuracy': torch.sigmoid(self.accuracy_score(features)),
                    'consistency': torch.sigmoid(self.consistency_score(features)),
                    'richness': torch.sigmoid(self.richness_score(features))
                }
        
        model = MetadataQualityAssessor()
        
        # Load pre-trained weights if available
        quality_model_path = self.config.get('metadata_quality_model_path')
        if quality_model_path:
            try:
                model.load_state_dict(torch.load(quality_model_path))
                self.logger.info("Loaded pre-trained metadata quality model")
            except Exception as e:
                self.logger.warning(f"Could not load quality model weights: {e}")
        
        return model
    
    async def _load_fallback_models(self):
        """Load simplified fallback models if advanced models fail"""        try:
            # Basic text classifier
            self.text_analyzer = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            # Basic feature extractor
            self.similarity_detector = pipeline(
                "feature-extraction",
                model="distilbert-base-uncased"
            )
            
            self.logger.info("Loaded fallback metadata models")
            
        except Exception as e:
            self.logger.error(f"Failed to load fallback models: {e}")
            'avi': self._parse_avi_metadata,
            'mov': self._parse_mov_metadata
        }
    
    async def _load_metadata_schemas(self):
        """Load metadata schemas for different formats"""        self.metadata_schemas = {
            'id3v2': {
                'title': ['TIT2', 'TITLE'],
                'artist': ['TPE1', 'ARTIST'],
                'album': ['TALB', 'ALBUM'],
                'date': ['TDRC', 'DATE'],
                'genre': ['TCON', 'GENRE'],
                'albumartist': ['TPE2', 'ALBUMARTIST'],
                'composer': ['TCOM', 'COMPOSER'],
                'producer': ['TIPL', 'PRODUCER'],
                'copyright': ['TCOP', 'COPYRIGHT'],
                'publisher': ['TPUB', 'PUBLISHER'],
                'bpm': ['TBPM', 'BPM'],
                'key': ['TKEY', 'KEY'],
                'lyrics': ['USLT', 'LYRICS']
            },
            'mp4': {
                'title': ['\xa9nam'],
                'artist': ['\xa9ART'],
                'album': ['\xa9alb'],
                'date': ['\xa9day'],
                'genre': ['\xa9gen'],
                'albumartist': ['aART'],
                'composer': ['\xa9wrt'],
                'copyright': ['cprt'],
                'label': ['----:com.apple.iTunes:LABEL'],
                'isrc': ['----:com.apple.iTunes:ISRC'],
                'catalog': ['----:com.apple.iTunes:CATALOGNUMBER']
            },
            'vorbis': {
                'title': ['TITLE'],
                'artist': ['ARTIST'],
                'album': ['ALBUM'],
                'date': ['DATE'],
                'genre': ['GENRE'],
                'albumartist': ['ALBUMARTIST'],
                'composer': ['COMPOSER'],
                'producer': ['PRODUCER'],
                'copyright': ['COPYRIGHT'],
                'organization': ['ORGANIZATION'],
                'isrc': ['ISRC'],
                'catalog': ['CATALOGNUMBER']
            },
            'exif': {
                'camera_make': ['Make'],
                'camera_model': ['Model'],
                'datetime': ['DateTime'],
                'artist': ['Artist'],
                'copyright': ['Copyright'],
                'software': ['Software'],
                'gps_info': ['GPSInfo'],
                'lens_model': ['LensModel'],
                'focal_length': ['FocalLength'],
                'exposure_time': ['ExposureTime'],
                'f_number': ['FNumber'],
                'iso': ['ISOSpeedRatings']
            }
        }
    
    async def _initialize_field_mappings(self):
        """Initialize field mappings between formats"""        self.field_mappings = {
            'artist_fields': [
                'artist', 'performer', 'creator', 'author', 'TPE1', '\xa9ART', 'ARTIST'
            ],
            'title_fields': [
                'title', 'name', 'track', 'TIT2', '\xa9nam', 'TITLE'
            ],
            'album_fields': [
                'album', 'collection', 'TALB', '\xa9alb', 'ALBUM'
            ],
            'date_fields': [
                'date', 'year', 'created', 'recorded', 'TDRC', '\xa9day', 'DATE', 'DateTime'
            ],
            'genre_fields': [
                'genre', 'style', 'category', 'TCON', '\xa9gen', 'GENRE'
            ],
            'copyright_fields': [
                'copyright', 'rights', 'license', 'TCOP', 'cprt', 'COPYRIGHT'
            ]
        }
    
    async def _load_normalization_rules(self):
        """Load normalization rules for metadata values"""        self.normalization_rules = {
            'genre_normalization': {
                # Map common genre variations to standard forms
                'hip hop': 'Hip-Hop',
                'hiphop': 'Hip-Hop',
                'rap': 'Hip-Hop',
                'r&b': 'R&B',
                'rnb': 'R&B',
                'rhythm and blues': 'R&B',
                'electronic dance music': 'Electronic',
                'edm': 'Electronic',
                'rock and roll': 'Rock',
                'rock & roll': 'Rock',
                'pop music': 'Pop',
                'classical music': 'Classical'
            },
            'artist_normalization': {
                # Handle featuring patterns
                'feat.': 'featuring',
                'ft.': 'featuring',
                'with': 'featuring',
                '&': 'and',
                ',': ' and '
            },
            'date_normalization': {
                # Handle various date formats
                'patterns': [
                    r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
                    r'(\d{2})/(\d{2})/(\d{4})',  # MM/DD/YYYY
                    r'(\d{4})',                  # YYYY
                    r'(\d{2})-(\d{2})-(\d{4})'   # DD-MM-YYYY
                ]
            }
        }
    
    async def _initialize_quality_analyzers(self):
        """Initialize quality assessment tools"""        self.quality_analyzers = {
            'audio_quality': self._analyze_audio_quality,
            'image_quality': self._analyze_image_quality,
            'video_quality': self._analyze_video_quality,
            'metadata_completeness': self._analyze_metadata_completeness
        }
    
    @cache_manager.cached(ttl=3600)
    async def parse_metadata_entities(
        self,
        file_path: Optional[str] = None,
        file_data: Optional[bytes] = None,
        metadata_dict: Optional[Dict[str, Any]] = None,
        content_type: Optional[str] = None
    ) -> MetadataAnalysisResult:
        """        Parse metadata entities from various sources.
        
        Args:
            file_path: Path to file for metadata extraction
            file_data: Raw file data for analysis
            metadata_dict: Pre-extracted metadata dictionary
            content_type: MIME type of content
            
        Returns:
            MetadataAnalysisResult with extracted entities and analysis
        """        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Parsing metadata entities from source")
            self.metrics.increment('parsing_requests')
            
            # Determine content format
            metadata_format = await self._determine_metadata_format(
                file_path, file_data, content_type
            )
            
            # Extract raw metadata
            raw_metadata = await self._extract_raw_metadata(
                file_path, file_data, metadata_dict, metadata_format
            )
            
            # Parse entities from metadata
            metadata_entities = await self._parse_entities_from_metadata(
                raw_metadata, metadata_format
            )
            
            # Analyze technical profile
            technical_profile = await self._analyze_technical_profile(
                raw_metadata, metadata_format, file_path, file_data
            )
            
            # Generate content fingerprint
            content_fingerprint = await self._generate_content_fingerprint(
                raw_metadata, technical_profile
            )
            
            # Assess quality
            quality_assessment = await self._assess_content_quality(
                raw_metadata, technical_profile, file_path, file_data
            )
            
            # Check platform compatibility
            platform_compatibility = await self._check_platform_compatibility(
                technical_profile, metadata_format
            )
            
            # Extract rights information
            rights_information = await self._extract_rights_information(raw_metadata)
            
            # Map collaboration network
            collaboration_network = await self._map_collaboration_network(metadata_entities)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate confidence score
            confidence_score = self._calculate_parsing_confidence(
                metadata_entities, raw_metadata, quality_assessment
            )
            
            result = MetadataAnalysisResult(
                metadata_entities=metadata_entities,
                technical_profile=technical_profile,
                content_fingerprint=content_fingerprint,
                quality_assessment=quality_assessment,
                platform_compatibility=platform_compatibility,
                rights_information=rights_information,
                collaboration_network=collaboration_network,
                processing_time=processing_time,
                confidence_score=confidence_score
            )
            
            # Update statistics
            self._update_parsing_stats(result, metadata_format)
            
            self.logger.info(f"Metadata parsing completed: {len(metadata_entities)} entities "
                           f"in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Metadata parsing failed: {str(e)}")
            self.metrics.increment('parsing_errors')
            raise
    
    async def _determine_metadata_format(
        self,
        file_path: Optional[str],
        file_data: Optional[bytes],
        content_type: Optional[str]
    ) -> MetadataFormat:
        """Determine metadata format from file information"""        
        # Use content type if provided
        if content_type:
            if content_type.startswith('audio/'):
                if 'mp3' in content_type:
                    return MetadataFormat.AUDIO_ID3
                elif 'mp4' in content_type or 'm4a' in content_type:
                    return MetadataFormat.AUDIO_MP4
                elif 'flac' in content_type:
                    return MetadataFormat.AUDIO_FLAC
                elif 'ogg' in content_type:
                    return MetadataFormat.AUDIO_VORBIS
            elif content_type.startswith('image/'):
                return MetadataFormat.IMAGE_EXIF
            elif content_type.startswith('video/'):
                return MetadataFormat.VIDEO_MP4
        
        # Use file extension if available
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.mp3']:
                return MetadataFormat.AUDIO_ID3
            elif ext in ['.mp4', '.m4a', '.aac']:
                return MetadataFormat.AUDIO_MP4
            elif ext in ['.flac']:
                return MetadataFormat.AUDIO_FLAC
            elif ext in ['.ogg', '.oga']:
                return MetadataFormat.AUDIO_VORBIS
            elif ext in ['.jpg', '.jpeg', '.png', '.tiff']:
                return MetadataFormat.IMAGE_EXIF
            elif ext in ['.mp4', '.avi', '.mov']:
                return MetadataFormat.VIDEO_MP4
        
        # Default to audio ID3 for unknown formats
        return MetadataFormat.AUDIO_ID3
    
    async def _extract_raw_metadata(
        self,
        file_path: Optional[str],
        file_data: Optional[bytes],
        metadata_dict: Optional[Dict[str, Any]],
        metadata_format: MetadataFormat
    ) -> Dict[str, Any]:
        """Extract raw metadata from source"""        
        # If metadata dictionary is provided, use it
        if metadata_dict:
            return metadata_dict
        
        # Extract from file
        if file_path and os.path.exists(file_path):
            return await self._extract_from_file(file_path, metadata_format)
        
        # Extract from file data
        if file_data:
            return await self._extract_from_data(file_data, metadata_format)
        
        return {}
    
    async def _extract_from_file(self, file_path: str, metadata_format: MetadataFormat) -> Dict[str, Any]:
        """Extract metadata from file"""        try:
            if metadata_format in [MetadataFormat.AUDIO_ID3, MetadataFormat.AUDIO_MP4, 
                                 MetadataFormat.AUDIO_FLAC, MetadataFormat.AUDIO_VORBIS]:
                return await self._extract_audio_metadata(file_path)
            
            elif metadata_format == MetadataFormat.IMAGE_EXIF:
                return await self._extract_image_metadata(file_path)
            
            elif metadata_format in [MetadataFormat.VIDEO_MP4, MetadataFormat.VIDEO_AVI]:
                return await self._extract_video_metadata(file_path)
        
        except Exception as e:
            self.logger.warning(f"Failed to extract metadata from {file_path}: {str(e)}")
        
        return {}
    
    async def _extract_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract audio metadata using mutagen"""        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return {}
            
            metadata = {}
            
            # Extract all available tags
            if hasattr(audio_file, 'tags') and audio_file.tags:
                for key, value in audio_file.tags.items():
                    if isinstance(value, list) and len(value) == 1:
                        metadata[key] = str(value[0])
                    else:
                        metadata[key] = str(value)
            
            # Extract technical information
            if hasattr(audio_file, 'info'):
                info = audio_file.info
                metadata['_technical'] = {
                    'length': getattr(info, 'length', 0),
                    'bitrate': getattr(info, 'bitrate', 0),
                    'sample_rate': getattr(info, 'sample_rate', 0),
                    'channels': getattr(info, 'channels', 0),
                    'format': type(audio_file).__name__
                }
            
            return metadata
            
        except Exception as e:
            self.logger.warning(f"Failed to extract audio metadata: {str(e)}")
            return {}
    
    async def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image metadata using PIL"""        try:
            with Image.open(file_path) as image:
                metadata = {}
                
                # Extract EXIF data
                if hasattr(image, '_getexif'):
                    exif_data = image._getexif()
                    if exif_data:
                        for tag_id, value in exif_data.items():
                            tag_name = TAGS.get(tag_id, tag_id)
                            metadata[tag_name] = str(value)
                
                # Extract basic image info
                metadata['_technical'] = {
                    'format': image.format,
                    'mode': image.mode,
                    'size': image.size,
                    'width': image.width,
                    'height': image.height
                }
                
                return metadata
                
        except Exception as e:
            self.logger.warning(f"Failed to extract image metadata: {str(e)}")
            return {}
    
    async def _extract_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract video metadata using OpenCV"""        try:
            cap = cv2.VideoCapture(file_path)
            
            metadata = {
                '_technical': {
                    'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                    'fps': cap.get(cv2.CAP_PROP_FPS),
                    'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
                }
            }
            
            cap.release()
            return metadata
            
        except Exception as e:
            self.logger.warning(f"Failed to extract video metadata: {str(e)}")
            return {}
    
    async def _extract_from_data(self, file_data: bytes, metadata_format: MetadataFormat) -> Dict[str, Any]:
        """Extract metadata from file data"""        # This would require writing data to temporary file or using in-memory processing
        # For now, return empty metadata
        return {}
    
    async def _parse_entities_from_metadata(
        self,
        raw_metadata: Dict[str, Any],
        metadata_format: MetadataFormat
    ) -> List[MetadataEntity]:
        """Parse entities from raw metadata"""        entities = []
        
        # Get schema for this format
        schema = self._get_schema_for_format(metadata_format)
        
        for field_name, field_value in raw_metadata.items():
            if field_name.startswith('_'):
                continue  # Skip technical fields
            
            # Determine entity type
            entity_type = self._determine_entity_type(field_name, field_value, schema)
            
            if entity_type:
                # Normalize value
                normalized_value = self._normalize_metadata_value(field_value, entity_type)
                
                # Create base entity
                base_entity = ExtractedEntity(
                    text=normalized_value,
                    label=f"METADATA_{entity_type.value.upper()}",
                    start=0,
                    end=len(normalized_value),
                    confidence=self._calculate_field_confidence(field_name, field_value, schema),
                    category=EntityCategory.METADATA
                )
                
                # Create metadata entity
                metadata_entity = MetadataEntity(
                    entity=base_entity,
                    metadata_type=entity_type,
                    metadata_format=metadata_format,
                    raw_value=field_value,
                    normalized_value=normalized_value,
                    confidence=base_entity.confidence,
                    technical_details={'field_name': field_name},
                    relationships=self._extract_field_relationships(field_name, field_value)
                )
                
                entities.append(metadata_entity)
        
        return entities
    
    def _get_schema_for_format(self, metadata_format: MetadataFormat) -> Dict[str, List[str]]:
        """Get metadata schema for format"""        format_mapping = {
            MetadataFormat.AUDIO_ID3: 'id3v2',
            MetadataFormat.AUDIO_MP4: 'mp4',
            MetadataFormat.AUDIO_VORBIS: 'vorbis',
            MetadataFormat.AUDIO_FLAC: 'vorbis',
            MetadataFormat.IMAGE_EXIF: 'exif'
        }
        
        schema_name = format_mapping.get(metadata_format, 'id3v2')
        return self.metadata_schemas.get(schema_name, {})
    
    def _determine_entity_type(
        self,
        field_name: str,
        field_value: Any,
        schema: Dict[str, List[str]]
    ) -> Optional[MetadataEntityType]:
        """Determine entity type from field name and value"""        field_name_lower = field_name.lower()
        
        # Check against field mappings
        for entity_type_name, field_patterns in self.field_mappings.items():
            for pattern in field_patterns:
                if pattern.lower() in field_name_lower or field_name_lower in pattern.lower():
                    return self._map_field_to_entity_type(entity_type_name)
        
        # Pattern-based detection
        if re.match(r'^\d{4}', str(field_value)):  # Year pattern
            return MetadataEntityType.CREATION_DATE
        
        if 'copyright' in field_name_lower or '©' in str(field_value):
            return MetadataEntityType.COPYRIGHT_INFO
        
        if 'producer' in field_name_lower or 'label' in field_name_lower:
            return MetadataEntityType.PRODUCTION_INFO
        
        if 'isrc' in field_name_lower or 'catalog' in field_name_lower:
            return MetadataEntityType.PUBLISHER_INFO
        
        # Technical fields
        if field_name_lower in ['bitrate', 'sample_rate', 'channels', 'format', 'codec']:
            return MetadataEntityType.TECHNICAL_SPECS
        
        return None
    
    def _map_field_to_entity_type(self, field_type_name: str) -> MetadataEntityType:
        """Map field type name to metadata entity type"""        mapping = {
            'artist_fields': MetadataEntityType.ARTIST_NAME,
            'title_fields': MetadataEntityType.TRACK_TITLE,
            'album_fields': MetadataEntityType.ALBUM_TITLE,
            'date_fields': MetadataEntityType.CREATION_DATE,
            'genre_fields': MetadataEntityType.GENRE_TAG,
            'copyright_fields': MetadataEntityType.COPYRIGHT_INFO
        }
        
        return mapping.get(field_type_name, MetadataEntityType.ARTIST_NAME)
    
    def _normalize_metadata_value(self, value: Any, entity_type: MetadataEntityType) -> str:
        """Normalize metadata value based on entity type"""        value_str = str(value).strip()
        
        if entity_type == MetadataEntityType.GENRE_TAG:
            # Normalize genre
            return self._normalize_genre(value_str)
        
        elif entity_type == MetadataEntityType.ARTIST_NAME:
            # Normalize artist name
            return self._normalize_artist_name(value_str)
        
        elif entity_type == MetadataEntityType.CREATION_DATE:
            # Normalize date
            return self._normalize_date(value_str)
        
        else:
            # Basic cleanup
            return self.text_processor.clean_text(value_str)
    
    def _normalize_genre(self, genre: str) -> str:
        """Normalize genre value"""        genre_lower = genre.lower().strip()
        
        # Check normalization rules
        normalized = self.normalization_rules['genre_normalization'].get(genre_lower)
        if normalized:
            return normalized
        
        # Basic cleanup
        return genre.title().strip()
    
    def _normalize_artist_name(self, artist: str) -> str:
        """Normalize artist name"""        normalized = artist
        
        # Apply normalization rules
        for pattern, replacement in self.normalization_rules['artist_normalization'].items():
            normalized = normalized.replace(pattern, replacement)
        
        return self.text_processor.clean_text(normalized)
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date value"""        # Try to extract year from various formats
        for pattern in self.normalization_rules['date_normalization']['patterns']:
            match = re.search(pattern, date_str)
            if match:
                if len(match.groups()) == 1:  # Only year
                    return match.group(1)
                elif len(match.groups()) == 3:  # Full date
                    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        
        return date_str.strip()
    
    def _calculate_field_confidence(
        self,
        field_name: str,
        field_value: Any,
        schema: Dict[str, List[str]]
    ) -> float:
        """Calculate confidence for metadata field"""        confidence = 0.5  # Base confidence
        
        # Boost for known schema fields
        for entity_fields in schema.values():
            if field_name in entity_fields:
                confidence += 0.3
                break
        
        # Boost for non-empty values
        if field_value and str(field_value).strip():
            confidence += 0.2
        
        # Reduce for very short values
        if len(str(field_value)) < 2:
            confidence -= 0.2
        
        # Boost for structured data
        if re.match(r'^\d{4}', str(field_value)):  # Year
            confidence += 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def _extract_field_relationships(self, field_name: str, field_value: Any) -> List[str]:
        """Extract relationships between metadata fields"""        relationships = []
        
        # Artist relationships
        if 'artist' in field_name.lower():
            if 'feat' in str(field_value).lower() or 'ft.' in str(field_value).lower():
                relationships.append('collaboration')
        
        # Production relationships
        if 'producer' in field_name.lower() or 'label' in field_name.lower():
            relationships.append('production')
        
        return relationships
    
    async def _analyze_technical_profile(
        self,
        raw_metadata: Dict[str, Any],
        metadata_format: MetadataFormat,
        file_path: Optional[str],
        file_data: Optional[bytes]
    ) -> Dict[str, Any]:
        """Analyze technical profile of content"""        profile = {
            'format_info': {},
            'quality_metrics': {},
            'encoding_details': {},
            'platform_specs': {}
        }
        
        # Extract technical metadata
        technical_data = raw_metadata.get('_technical', {})
        
        if metadata_format in [MetadataFormat.AUDIO_ID3, MetadataFormat.AUDIO_MP4, 
                             MetadataFormat.AUDIO_FLAC, MetadataFormat.AUDIO_VORBIS]:
            profile['format_info'] = {
                'type': 'audio',
                'format': technical_data.get('format', 'unknown'),
                'duration': technical_data.get('length', 0),
                'bitrate': technical_data.get('bitrate', 0),
                'sample_rate': technical_data.get('sample_rate', 0),
                'channels': technical_data.get('channels', 0)
            }
            
            # Quality assessment for audio
            profile['quality_metrics'] = self._assess_audio_technical_quality(technical_data)
        
        elif metadata_format == MetadataFormat.IMAGE_EXIF:
            profile['format_info'] = {
                'type': 'image',
                'format': technical_data.get('format', 'unknown'),
                'dimensions': technical_data.get('size', (0, 0)),
                'mode': technical_data.get('mode', 'unknown')
            }
            
            # Quality assessment for image
            profile['quality_metrics'] = self._assess_image_technical_quality(technical_data)
        
        elif metadata_format in [MetadataFormat.VIDEO_MP4, MetadataFormat.VIDEO_AVI]:
            profile['format_info'] = {
                'type': 'video',
                'duration': technical_data.get('duration', 0),
                'fps': technical_data.get('fps', 0),
                'dimensions': (technical_data.get('width', 0), technical_data.get('height', 0))
            }
            
            # Quality assessment for video
            profile['quality_metrics'] = self._assess_video_technical_quality(technical_data)
        
        return profile
    
    def _assess_audio_technical_quality(self, technical_data: Dict[str, Any]) -> Dict[str, float]:
        """Assess audio technical quality"""        quality = {}
        
        bitrate = technical_data.get('bitrate', 0)
        sample_rate = technical_data.get('sample_rate', 0)
        
        # Bitrate quality (0-1 scale)
        if bitrate >= 320:
            quality['bitrate_quality'] = 1.0
        elif bitrate >= 256:
            quality['bitrate_quality'] = 0.8
        elif bitrate >= 192:
            quality['bitrate_quality'] = 0.6
        elif bitrate >= 128:
            quality['bitrate_quality'] = 0.4
        else:
            quality['bitrate_quality'] = 0.2
        
        # Sample rate quality
        if sample_rate >= 48000:
            quality['sample_rate_quality'] = 1.0
        elif sample_rate >= 44100:
            quality['sample_rate_quality'] = 0.8
        else:
            quality['sample_rate_quality'] = 0.5
        
        # Overall audio quality
        quality['overall_quality'] = np.mean(list(quality.values()))
        
        return quality
    
    def _assess_image_technical_quality(self, technical_data: Dict[str, Any]) -> Dict[str, float]:
        """Assess image technical quality"""        quality = {}
        
        dimensions = technical_data.get('size', (0, 0))
        total_pixels = dimensions[0] * dimensions[1]
        
        # Resolution quality
        if total_pixels >= 2000000:  # 2MP+
            quality['resolution_quality'] = 1.0
        elif total_pixels >= 1000000:  # 1MP+
            quality['resolution_quality'] = 0.8
        elif total_pixels >= 500000:   # 0.5MP+
            quality['resolution_quality'] = 0.6
        else:
            quality['resolution_quality'] = 0.4
        
        # Aspect ratio analysis
        if dimensions[0] > 0 and dimensions[1] > 0:
            aspect_ratio = dimensions[0] / dimensions[1]
            # Standard ratios get higher scores
            if abs(aspect_ratio - 16/9) < 0.1 or abs(aspect_ratio - 4/3) < 0.1 or abs(aspect_ratio - 1) < 0.1:
                quality['aspect_ratio_quality'] = 1.0
            else:
                quality['aspect_ratio_quality'] = 0.7
        else:
            quality['aspect_ratio_quality'] = 0.5
        
        quality['overall_quality'] = np.mean(list(quality.values()))
        
        return quality
    
    def _assess_video_technical_quality(self, technical_data: Dict[str, Any]) -> Dict[str, float]:
        """Assess video technical quality"""        quality = {}
        
        fps = technical_data.get('fps', 0)
        width = technical_data.get('width', 0)
        height = technical_data.get('height', 0)
        
        # Frame rate quality
        if fps >= 60:
            quality['fps_quality'] = 1.0
        elif fps >= 30:
            quality['fps_quality'] = 0.8
        elif fps >= 24:
            quality['fps_quality'] = 0.6
        else:
            quality['fps_quality'] = 0.4
        
        # Resolution quality
        total_pixels = width * height
        if total_pixels >= 3840 * 2160:  # 4K
            quality['resolution_quality'] = 1.0
        elif total_pixels >= 1920 * 1080:  # 1080p
            quality['resolution_quality'] = 0.9
        elif total_pixels >= 1280 * 720:   # 720p
            quality['resolution_quality'] = 0.7
        else:
            quality['resolution_quality'] = 0.5
        
        quality['overall_quality'] = np.mean(list(quality.values()))
        
        return quality
    
    async def _generate_content_fingerprint(
        self,
        raw_metadata: Dict[str, Any],
        technical_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content fingerprint for identification"""        fingerprint = {
            'metadata_hash': self._generate_metadata_hash(raw_metadata),
            'technical_signature': self._generate_technical_signature(technical_profile),
            'content_type': technical_profile.get('format_info', {}).get('type', 'unknown'),
            'quality_tier': self._determine_quality_tier(technical_profile),
            'platform_suitability': self._assess_platform_suitability(technical_profile)
        }
        
        return fingerprint
    
    def _generate_metadata_hash(self, raw_metadata: Dict[str, Any]) -> str:
        """Generate hash from metadata for content identification"""        # Create deterministic hash from key metadata fields
        key_fields = ['title', 'artist', 'album', 'date', 'TIT2', 'TPE1', 'TALB', '\xa9nam', '\xa9ART']
        
        hash_input = ""
        for field in key_fields:
            value = raw_metadata.get(field, "")
            hash_input += str(value).lower().strip()
        
        # Simple hash (in production, use proper cryptographic hash)
        return str(hash(hash_input))
    
    def _generate_technical_signature(self, technical_profile: Dict[str, Any]) -> str:
        """Generate technical signature"""        format_info = technical_profile.get('format_info', {})
        
        signature_parts = [
            format_info.get('type', 'unknown'),
            str(format_info.get('bitrate', 0)),
            str(format_info.get('sample_rate', 0)),
            str(format_info.get('duration', 0))
        ]
        
        return "_".join(signature_parts)
    
    def _determine_quality_tier(self, technical_profile: Dict[str, Any]) -> str:
        """Determine quality tier based on technical specs"""        quality_metrics = technical_profile.get('quality_metrics', {})
        overall_quality = quality_metrics.get('overall_quality', 0.5)
        
        if overall_quality >= 0.9:
            return 'premium'
        elif overall_quality >= 0.7:
            return 'high'
        elif overall_quality >= 0.5:
            return 'standard'
        else:
            return 'basic'
    
    def _assess_platform_suitability(self, technical_profile: Dict[str, Any]) -> Dict[str, bool]:
        """Assess suitability for different platforms"""        format_info = technical_profile.get('format_info', {})
        suitability = {}
        
        if format_info.get('type') == 'audio':
            bitrate = format_info.get('bitrate', 0)
            sample_rate = format_info.get('sample_rate', 0)
            
            suitability['spotify'] = bitrate >= 160 and sample_rate >= 44100
            suitability['apple_music'] = bitrate >= 256 and sample_rate >= 44100
            suitability['youtube'] = bitrate >= 128
            suitability['soundcloud'] = bitrate >= 128
            suitability['bandcamp'] = bitrate >= 320  # Higher quality expected
        
        elif format_info.get('type') == 'video':
            dimensions = format_info.get('dimensions', (0, 0))
            fps = format_info.get('fps', 0)
            
            suitability['youtube'] = dimensions[1] >= 720 and fps >= 24
            suitability['instagram'] = True  # Instagram accepts various formats
            suitability['tiktok'] = fps >= 24 and dimensions[1] >= 720
            suitability['vimeo'] = dimensions[1] >= 1080 and fps >= 24
        
        elif format_info.get('type') == 'image':
            dimensions = format_info.get('dimensions', (0, 0))
            
            suitability['instagram'] = min(dimensions) >= 600
            suitability['facebook'] = min(dimensions) >= 400
            suitability['twitter'] = min(dimensions) >= 300
            suitability['pinterest'] = dimensions[1] >= 600  # Vertical preference
        
        return suitability
    
    async def _assess_content_quality(
        self,
        raw_metadata: Dict[str, Any],
        technical_profile: Dict[str, Any],
        file_path: Optional[str],
        file_data: Optional[bytes]
    ) -> Dict[str, float]:
        """Assess overall content quality"""        quality_assessment = {}
        
        # Technical quality from profile
        tech_quality = technical_profile.get('quality_metrics', {}).get('overall_quality', 0.5)
        quality_assessment['technical_quality'] = tech_quality
        
        # Metadata completeness
        metadata_completeness = self._assess_metadata_completeness(raw_metadata)
        quality_assessment['metadata_completeness'] = metadata_completeness
        
        # Professional indicators
        professional_score = self._assess_professional_indicators(raw_metadata)
        quality_assessment['professional_score'] = professional_score
        
        # Overall quality
        quality_assessment['overall_quality'] = np.mean([
            tech_quality, metadata_completeness, professional_score
        ])
        
        return quality_assessment
    
    def _assess_metadata_completeness(self, raw_metadata: Dict[str, Any]) -> float:
        """Assess completeness of metadata"""        essential_fields = ['title', 'artist', 'TIT2', 'TPE1', '\xa9nam', '\xa9ART']
        important_fields = ['album', 'date', 'genre', 'TALB', 'TDRC', 'TCON', '\xa9alb', '\xa9day']
        
        essential_count = sum(1 for field in essential_fields if field in raw_metadata and raw_metadata[field])
        important_count = sum(1 for field in important_fields if field in raw_metadata and raw_metadata[field])
        
        essential_score = essential_count / len(essential_fields)
        important_score = important_count / len(important_fields)
        
        return (essential_score * 0.7) + (important_score * 0.3)
    
    def _assess_professional_indicators(self, raw_metadata: Dict[str, Any]) -> float:
        """Assess professional production indicators"""        professional_fields = [
            'producer', 'label', 'copyright', 'publisher', 'isrc', 'catalog',
            'TPUB', 'TCOP', 'TIPL', 'cprt'
        ]
        
        professional_count = sum(1 for field in professional_fields 
                               if field in raw_metadata and raw_metadata[field])
        
        return min(1.0, professional_count / 5.0)  # Normalize to max 5 fields
    
    async def _check_platform_compatibility(
        self,
        technical_profile: Dict[str, Any],
        metadata_format: MetadataFormat
    ) -> Dict[str, bool]:
        """Check compatibility with various platforms"""        return technical_profile.get('platform_suitability', {})
    
    async def _extract_rights_information(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract rights and copyright information"""        rights_info = {
            'copyright_holder': None,
            'publisher': None,
            'rights_statement': None,
            'licensing_info': None,
            'isrc': None,
            'catalog_number': None
        }
        
        # Copyright fields
        copyright_fields = ['copyright', 'TCOP', 'cprt', 'Copyright']
        for field in copyright_fields:
            if field in raw_metadata and raw_metadata[field]:
                rights_info['copyright_holder'] = str(raw_metadata[field])
                break
        
        # Publisher fields
        publisher_fields = ['publisher', 'label', 'TPUB', '----:com.apple.iTunes:LABEL']
        for field in publisher_fields:
            if field in raw_metadata and raw_metadata[field]:
                rights_info['publisher'] = str(raw_metadata[field])
                break
        
        # ISRC
        isrc_fields = ['isrc', 'TSRC', '----:com.apple.iTunes:ISRC']
        for field in isrc_fields:
            if field in raw_metadata and raw_metadata[field]:
                rights_info['isrc'] = str(raw_metadata[field])
                break
        
        # Catalog number
        catalog_fields = ['catalog', 'catalognumber', '----:com.apple.iTunes:CATALOGNUMBER']
        for field in catalog_fields:
            if field in raw_metadata and raw_metadata[field]:
                rights_info['catalog_number'] = str(raw_metadata[field])
                break
        
        return rights_info
    
    async def _map_collaboration_network(self, metadata_entities: List[MetadataEntity]) -> Dict[str, List[str]]:
        """Map collaboration network from metadata"""        network = {}
        
        # Find artist entities
        artist_entities = [e for e in metadata_entities 
                          if e.metadata_type == MetadataEntityType.ARTIST_NAME]
        
        # Find collaboration indicators
        for entity in artist_entities:
            artist_name = entity.normalized_value
            collaborations = []
            
            # Check for featuring relationships
            if 'collaboration' in entity.relationships:
                # Parse featuring artists from the text
                text = entity.raw_value
                if isinstance(text, str):
                    # Extract featured artists
                    feat_patterns = [r'feat\.?\s+([^,\)]+)', r'ft\.?\s+([^,\)]+)', r'featuring\s+([^,\)]+)']
                    for pattern in feat_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        collaborations.extend([match.strip() for match in matches])
            
            if collaborations:
                network[artist_name] = collaborations
        
        return network
    
    def _calculate_parsing_confidence(
        self,
        metadata_entities: List[MetadataEntity],
        raw_metadata: Dict[str, Any],
        quality_assessment: Dict[str, float]
    ) -> float:
        """Calculate overall parsing confidence"""        factors = []
        
        # Entity extraction confidence
        if metadata_entities:
            entity_confidences = [e.confidence for e in metadata_entities]
            factors.append(np.mean(entity_confidences))
        
        # Metadata completeness
        completeness = quality_assessment.get('metadata_completeness', 0.5)
        factors.append(completeness)
        
        # Technical quality
        tech_quality = quality_assessment.get('technical_quality', 0.5)
        factors.append(tech_quality)
        
        # Number of extracted fields
        field_count_factor = min(1.0, len([k for k in raw_metadata.keys() if not k.startswith('_')]) / 10.0)
        factors.append(field_count_factor)
        
        return np.mean(factors) if factors else 0.5
    
    def _update_parsing_stats(self, result: MetadataAnalysisResult, metadata_format: MetadataFormat):
        """Update parsing statistics"""        self.parsing_stats['total_files_processed'] += 1
        self.parsing_stats['successful_extractions'] += 1
        
        # Update format distribution
        format_name = metadata_format.value
        self.parsing_stats['format_distribution'][format_name] = \
            self.parsing_stats['format_distribution'].get(format_name, 0) + 1
        
        # Update entity type distribution
        for entity in result.metadata_entities:
            entity_type = entity.metadata_type.value
            self.parsing_stats['entity_type_distribution'][entity_type] = \
                self.parsing_stats['entity_type_distribution'].get(entity_type, 0) + 1
        
        # Update quality scores
        overall_quality = result.quality_assessment.get('overall_quality', 0.5)
        self.parsing_stats['quality_scores'].append(overall_quality)
        
        # Update average processing time
        current_avg = self.parsing_stats['avg_processing_time']
        total_processed = self.parsing_stats['total_files_processed']
        new_avg = ((current_avg * (total_processed - 1)) + result.processing_time) / total_processed
        self.parsing_stats['avg_processing_time'] = new_avg
    
    # Additional parsing methods for specific formats
    async def _parse_mp3_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse MP3 metadata specifically"""        return await self._extract_audio_metadata(file_path)
    
    async def _parse_mp4_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse MP4 metadata specifically"""        return await self._extract_audio_metadata(file_path)
    
    async def _parse_flac_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse FLAC metadata specifically"""        return await self._extract_audio_metadata(file_path)
    
    async def _parse_ogg_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse OGG metadata specifically"""        return await self._extract_audio_metadata(file_path)
    
    async def _parse_wav_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse WAV metadata specifically"""        return await self._extract_audio_metadata(file_path)
    
    async def _parse_jpg_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse JPEG metadata specifically"""        return await self._extract_image_metadata(file_path)
    
    async def _parse_png_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse PNG metadata specifically"""        return await self._extract_image_metadata(file_path)
    
    async def _parse_tiff_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse TIFF metadata specifically"""        return await self._extract_image_metadata(file_path)
    
    async def _parse_mp4_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse MP4 video metadata specifically"""        return await self._extract_video_metadata(file_path)
    
    async def _parse_avi_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse AVI metadata specifically"""        return await self._extract_video_metadata(file_path)
    
    async def _parse_mov_metadata(self, file_path: str) -> Dict[str, Any]:
        """Parse MOV metadata specifically"""        return await self._extract_video_metadata(file_path)
    
    # Quality analyzer implementations
    async def _analyze_audio_quality(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, float]:
        """Analyze audio quality in detail"""        quality_metrics = {}
        
        try:
            # Use technical metadata for quality assessment
            technical_data = metadata.get('_technical', {})
            
            # Bitrate analysis
            bitrate = technical_data.get('bitrate', 0)
            quality_metrics['bitrate_score'] = min(1.0, bitrate / 320.0)  # Normalize to 320kbps
            
            # Sample rate analysis
            sample_rate = technical_data.get('sample_rate', 0)
            quality_metrics['sample_rate_score'] = min(1.0, sample_rate / 48000.0)  # Normalize to 48kHz
            
            # Duration analysis (reasonable length)
            duration = technical_data.get('length', 0)
            if 30 <= duration <= 600:  # 30s to 10min is good range
                quality_metrics['duration_score'] = 1.0
            else:
                quality_metrics['duration_score'] = 0.7
            
            # Overall audio quality
            quality_metrics['overall_audio_quality'] = np.mean(list(quality_metrics.values()))
            
        except Exception as e:
            self.logger.warning(f"Audio quality analysis failed: {str(e)}")
            quality_metrics['overall_audio_quality'] = 0.5
        
        return quality_metrics
    
    async def _analyze_image_quality(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, float]:
        """Analyze image quality in detail"""        quality_metrics = {}
        
        try:
            technical_data = metadata.get('_technical', {})
            
            # Resolution analysis
            size = technical_data.get('size', (0, 0))
            megapixels = (size[0] * size[1]) / 1000000
            quality_metrics['resolution_score'] = min(1.0, megapixels / 10.0)  # Normalize to 10MP
            
            # Aspect ratio analysis
            if size[0] > 0 and size[1] > 0:
                aspect_ratio = size[0] / size[1]
                # Prefer standard ratios
                standard_ratios = [16/9, 4/3, 3/2, 1/1, 9/16]  # Including vertical
                ratio_scores = [1.0 / (1.0 + abs(aspect_ratio - ratio)) for ratio in standard_ratios]
                quality_metrics['aspect_ratio_score'] = max(ratio_scores)
            else:
                quality_metrics['aspect_ratio_score'] = 0.5
            
            # Format analysis
            format_name = technical_data.get('format', '').upper()
            format_scores = {'JPEG': 0.8, 'PNG': 1.0, 'TIFF': 0.9, 'GIF': 0.6}
            quality_metrics['format_score'] = format_scores.get(format_name, 0.5)
            
            quality_metrics['overall_image_quality'] = np.mean(list(quality_metrics.values()))
            
        except Exception as e:
            self.logger.warning(f"Image quality analysis failed: {str(e)}")
            quality_metrics['overall_image_quality'] = 0.5
        
        return quality_metrics
    
    async def _analyze_video_quality(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, float]:
        """Analyze video quality in detail"""        quality_metrics = {}
        
        try:
            technical_data = metadata.get('_technical', {})
            
            # Resolution analysis
            width = technical_data.get('width', 0)
            height = technical_data.get('height', 0)
            total_pixels = width * height
            
            # Score based on common resolutions
            if total_pixels >= 3840 * 2160:  # 4K
                quality_metrics['resolution_score'] = 1.0
            elif total_pixels >= 1920 * 1080:  # 1080p
                quality_metrics['resolution_score'] = 0.9
            elif total_pixels >= 1280 * 720:   # 720p
                quality_metrics['resolution_score'] = 0.7
            elif total_pixels >= 854 * 480:    # 480p
                quality_metrics['resolution_score'] = 0.5
            else:
                quality_metrics['resolution_score'] = 0.3
            
            # Frame rate analysis
            fps = technical_data.get('fps', 0)
            if fps >= 60:
                quality_metrics['fps_score'] = 1.0
            elif fps >= 30:
                quality_metrics['fps_score'] = 0.8
            elif fps >= 24:
                quality_metrics['fps_score'] = 0.6
            else:
                quality_metrics['fps_score'] = 0.4
            
            # Duration analysis
            duration = technical_data.get('duration', 0)
            if 10 <= duration <= 3600:  # 10s to 1hour
                quality_metrics['duration_score'] = 1.0
            else:
                quality_metrics['duration_score'] = 0.7
            
            quality_metrics['overall_video_quality'] = np.mean(list(quality_metrics.values()))
            
        except Exception as e:
            self.logger.warning(f"Video quality analysis failed: {str(e)}")
            quality_metrics['overall_video_quality'] = 0.5
        
        return quality_metrics
    
    async def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get metadata parsing statistics"""        stats = self.parsing_stats.copy()
        
        # Calculate average quality score
        if stats['quality_scores']:
            stats['avg_quality_score'] = np.mean(stats['quality_scores'])
        else:
            stats['avg_quality_score'] = 0.0
        
        # Add supported formats
        stats['supported_metadata_formats'] = [fmt.value for fmt in MetadataFormat]
        stats['supported_entity_types'] = [met.value for met in MetadataEntityType]
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for metadata entity parser"""        return {
            'status': 'healthy',
            'total_files_processed': self.parsing_stats['total_files_processed'],
            'success_rate': (
                self.parsing_stats['successful_extractions'] / 
                max(self.parsing_stats['total_files_processed'], 1)
            ) * 100,
            'avg_processing_time': self.parsing_stats['avg_processing_time'],
            'supported_formats': len(MetadataFormat),
            'supported_entity_types': len(MetadataEntityType),
            'format_distribution': self.parsing_stats['format_distribution']
        }
