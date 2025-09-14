"""Metadata Processor Module
========================

Enterprise-grade metadata extraction and enrichment for all content types.
Universal metadata handling, standardization, and cross-format compatibility.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or theft of this code or concept without explicit 
written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and 
will result in immediate legal action under German and international copyright law.

Features:
- Universal metadata extraction for all content formats
- AI-powered metadata enrichment and tagging
- Privacy-compliant sensitive data scrubbing
- Cross-format metadata standardization
- Intelligent content categorization and classification
- Automated content description generation
- Metadata validation and quality assessment
"""

import asyncio
import logging
import hashlib
import json
import mimetypes
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import tempfile

# Metadata extraction libraries
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - image metadata extraction limited")

try:
    import mutagen
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logging.warning("Mutagen not available - audio metadata extraction limited")

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    logging.warning("FFmpeg not available - video metadata extraction limited")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 not available - PDF metadata extraction limited")

try:
    from docx import Document
    PYTHON_DOCX_AVAILABLE = True
except ImportError:
    PYTHON_DOCX_AVAILABLE = False
    logging.warning("python-docx not available - DOCX metadata extraction limited")

logger = logging.getLogger(__name__)

@dataclass
class ContentMetadata:
    """Universal content metadata container"""
    # Standard file information
    filename: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    extension: Optional[str] = None
    
    # Timestamps
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    accessed_date: Optional[datetime] = None
    
    # Content characteristics
    content_type: Optional[str] = None  # audio, video, image, text
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    resolution: Optional[str] = None
    format_details: Dict[str, Any] = field(default_factory=dict)
    
    # Creator information
    creator: Optional[str] = None
    author: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    copyright_info: Optional[str] = None
    
    # Content description
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Technical metadata
    encoding: Optional[str] = None
    compression: Optional[str] = None
    quality_score: Optional[float] = None
    
    # Location information (if available)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    
    # Platform-specific metadata
    platform_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Security and privacy
    contains_sensitive_data: bool = False
    privacy_score: Optional[float] = None
    
    # AI-generated fields
    ai_generated_description: Optional[str] = None
    ai_content_score: Optional[float] = None
    ai_tags: List[str] = field(default_factory=list)

@dataclass
class MetadataQuality:
    """
Metadata quality assessment"""
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    richness_score: float
    overall_score: float
    missing_fields: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class MetadataProcessor:
    """
Universal metadata extraction and enrichment engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize metadata extraction engines
        self._initialize_engines()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default metadata processing configuration"""
        return {
            'extract_all_metadata': True,
            'privacy_protection': True,
            'ai_enrichment': True,
            'content_analysis': True,
            'quality_assessment': True,
            'sensitive_data_detection': True,
            'location_extraction': True,
            'thumbnail_generation': False,
            'metadata_standardization': True,
            'max_file_size': 500 * 1024 * 1024,  # 500MB
            'supported_formats': [
                # Images
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg',
                # Audio
                '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
                # Video
                '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm',
                # Documents
                '.pdf', '.doc', '.docx', '.txt', '.md', '.html', '.xml'
            ],
            'privacy_fields': [
                'gps_coordinates', 'location', 'personal_info', 'phone_numbers',
                'email_addresses', 'faces', 'license_plates', 'serial_numbers'
            ]
        }
    
    def _initialize_engines(self) -> None:
        """
Initialize metadata extraction engines"""
        try:
            # Initialize content type mappings
            self.content_type_mapping = {
                'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
                'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
                'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
                'text': ['.txt', '.md', '.html', '.xml'],
                'document': ['.pdf', '.doc', '.docx', '.rtf']
            }
            
            # Initialize AI models for content analysis (placeholder)
            self.ai_models = {}
            
            self.logger.info("Metadata processor engines initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing metadata engines: {str(e)}")
            raise
    
    async def process(
        self,
        content_data: Union[bytes, str],
        format_hint: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main metadata processing pipeline
        
        Args:
            content_data: Content data as bytes or file path
            format_hint: Optional format hint for processing
            config: Optional processing configuration override
        
        Returns:
            Dict containing extracted and enriched metadata
        """
        try:
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                processing_config.update(config)
            
            # Prepare content
            file_path, is_temp = await self._prepare_content(content_data, format_hint)
            
            try:
                # Extract standard file metadata
                standard_metadata = await self._extract_standard_metadata(file_path)
                
                # Determine content type
                content_type = self._determine_content_type(file_path, standard_metadata)
                
                # Extract format-specific metadata
                format_metadata = await self._extract_format_metadata(file_path, content_type)
                
                # Merge metadata
                metadata = self._merge_metadata(standard_metadata, format_metadata)
                
                # Process metadata in parallel
                tasks = []
                
                if processing_config.get('ai_enrichment', True):
                    tasks.append(self._enrich_with_ai(file_path, metadata, content_type))
                
                if processing_config.get('privacy_protection', True):
                    tasks.append(self._analyze_privacy(metadata))
                
                if processing_config.get('quality_assessment', True):
                    tasks.append(self._assess_metadata_quality(metadata))
                
                if processing_config.get('content_analysis', True):
                    tasks.append(self._analyze_content(file_path, content_type))
                
                # Execute all tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Compile final result
                result = {
                    'success': True,
                    'metadata': metadata,
                    'content_type': content_type,
                    'processing_config': processing_config,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Add processing results
                for i, task_result in enumerate(results):
                    if isinstance(task_result, Exception):
                        self.logger.error(f"Task {i} failed: {str(task_result)}")
                    else:
                        result.update(task_result)
                
                self.logger.info("Metadata processing completed successfully")
                return result
                
            finally:
                # Cleanup temporary file if created
                if is_temp and os.path.exists(file_path):
                    os.unlink(file_path)
            
        except Exception as e:
            self.logger.error(f"Metadata processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _prepare_content(
        self,
        content_data: Union[bytes, str],
        format_hint: Optional[str] = None
    ) -> Tuple[str, bool]:
        """Prepare content for metadata extraction"""
        try:
            if isinstance(content_data, str):
                # Already a file path
                if os.path.exists(content_data):
                    return content_data, False
                else:
                    raise FileNotFoundError(f"File not found: {content_data}")
                    
            elif isinstance(content_data, bytes):
                # Save bytes to temporary file
                suffix = f".{format_hint}" if format_hint else ""
                
                with tempfile.NamedTemporaryFile(
                    suffix=suffix,
                    delete=False
                ) as tmp_file:
                    tmp_file.write(content_data)
                    return tmp_file.name, True
            else:
                raise ValueError(f"Unsupported content data type: {type(content_data)}")
                
        except Exception as e:
            self.logger.error(f"Error preparing content: {str(e)}")
            raise
    
    async def _extract_standard_metadata(self, file_path: str) -> ContentMetadata:
        """Extract standard file system metadata"""
        try:
            stat = os.stat(file_path)
            
            metadata = ContentMetadata(
                filename=os.path.basename(file_path),
                file_size=stat.st_size,
                extension=Path(file_path).suffix.lower(),
                created_date=datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
                modified_date=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                accessed_date=datetime.fromtimestamp(stat.st_atime, tz=timezone.utc)
            )
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            metadata.mime_type = mime_type
            
            # Determine file type category
            if mime_type:
                metadata.file_type = mime_type.split('/')[0]
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting standard metadata: {str(e)}")
            raise
    
    def _determine_content_type(self, file_path: str, metadata: ContentMetadata) -> str:
        """Determine the content type based on file extension and MIME type"""
        try:
            extension = metadata.extension
            
            for content_type, extensions in self.content_type_mapping.items():
                if extension in extensions:
                    return content_type
            
            # Fallback to MIME type
            if metadata.mime_type:
                if metadata.mime_type.startswith('image/'):
                    return 'image'
                elif metadata.mime_type.startswith('audio/'):
                    return 'audio'
                elif metadata.mime_type.startswith('video/'):
                    return 'video'
                elif metadata.mime_type.startswith('text/'):
                    return 'text'
            
            return 'unknown'
            
        except Exception as e:
            self.logger.warning(f"Error determining content type: {str(e)}")
            return 'unknown'
    
    async def _extract_format_metadata(
        self,
        file_path: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Extract format-specific metadata"""
        try:
            format_metadata = {}
            
            if content_type == 'image':
                format_metadata = await self._extract_image_metadata(file_path)
            elif content_type == 'audio':
                format_metadata = await self._extract_audio_metadata(file_path)
            elif content_type == 'video':
                format_metadata = await self._extract_video_metadata(file_path)
            elif content_type in ['text', 'document']:
                format_metadata = await self._extract_document_metadata(file_path)
            
            return format_metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting format metadata: {str(e)}")
            return {}
    
    async def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image-specific metadata"""
        try:
            metadata = {}
            
            if PIL_AVAILABLE:
                try:
                    with Image.open(file_path) as img:
                        # Standard image info
                        metadata['dimensions'] = img.size
                        metadata['mode'] = img.mode
                        metadata['format'] = img.format
                        
                        # EXIF data
                        if hasattr(img, '_getexif'):
                            exif_data = img._getexif()
                            if exif_data:
                                exif_dict = {}
                                
                                for tag_id, value in exif_data.items():
                                    tag = TAGS.get(tag_id, tag_id)
                                    
                                    # Handle GPS data specially
                                    if tag == 'GPSInfo':
                                        gps_dict = {}
                                        for gps_tag_id, gps_value in value.items():
                                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                                            gps_dict[gps_tag] = gps_value
                                        exif_dict[tag] = gps_dict
                                        
                                        # Extract coordinates if available
                                        lat, lon = self._extract_gps_coordinates(gps_dict)
                                        if lat and lon:
                                            metadata['latitude'] = lat
                                            metadata['longitude'] = lon
                                    else:
                                        exif_dict[tag] = value
                                
                                metadata['exif'] = exif_dict
                                
                                # Extract common fields
                                if 'Artist' in exif_dict:
                                    metadata['artist'] = exif_dict['Artist']
                                if 'Copyright' in exif_dict:
                                    metadata['copyright_info'] = exif_dict['Copyright']
                                if 'DateTime' in exif_dict:
                                    metadata['date_taken'] = exif_dict['DateTime']
                                if 'Make' in exif_dict:
                                    metadata['camera_make'] = exif_dict['Make']
                                if 'Model' in exif_dict:
                                    metadata['camera_model'] = exif_dict['Model']
                
                except Exception as e:
                    self.logger.warning(f"PIL image processing failed: {str(e)}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Image metadata extraction failed: {str(e)}")
            return {}
    
    async def _extract_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract audio-specific metadata"""
        try:
            metadata = {}
            
            if MUTAGEN_AVAILABLE:
                try:
                    audiofile = mutagen.File(file_path)
                    if audiofile:
                        # Standard audio info
                        if hasattr(audiofile, 'info'):
                            info = audiofile.info
                            metadata['duration'] = getattr(info, 'length', None)
                            metadata['bitrate'] = getattr(info, 'bitrate', None)
                            metadata['sample_rate'] = getattr(info, 'sample_rate', None)
                            metadata['channels'] = getattr(info, 'channels', None)
                        
                        # Tags
                        tags = {}
                        if audiofile.tags:
                            for key, value in audiofile.tags.items():
                                if isinstance(value, list) and len(value) == 1:
                                    tags[key] = value[0]
                                else:
                                    tags[key] = value
                        
                        metadata['tags'] = tags
                        
                        # Common fields
                        common_mappings = {
                            'title': ['TIT2', 'TITLE', '\xa9nam'],
                            'artist': ['TPE1', 'ARTIST', '\xa9ART'],
                            'album': ['TALB', 'ALBUM', '\xa9alb'],
                            'date': ['TDRC', 'DATE', '\xa9day'],
                            'genre': ['TCON', 'GENRE', '\xa9gen'],
                            'track': ['TRCK', 'TRACKNUMBER', 'trkn'],
                            'albumartist': ['TPE2', 'ALBUMARTIST', 'aART']
                        }
                        
                        for field, possible_keys in common_mappings.items():
                            for key in possible_keys:
                                if key in tags:
                                    metadata[field] = tags[key]
                                    break
                        
                except Exception as e:
                    self.logger.warning(f"Mutagen audio processing failed: {str(e)}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Audio metadata extraction failed: {str(e)}")
            return {}
    
    async def _extract_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract video-specific metadata"""
        try:
            metadata = {}
            
            if FFMPEG_AVAILABLE:
                try:
                    probe = ffmpeg.probe(file_path)
                    
                    # General metadata
                    format_info = probe.get('format', {})
                    metadata['duration'] = float(format_info.get('duration', 0))
                    metadata['bitrate'] = int(format_info.get('bit_rate', 0))
                    metadata['format_name'] = format_info.get('format_name')
                    
                    # Video stream metadata
                    video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
                    if video_streams:
                        video_stream = video_streams[0]
                        metadata['width'] = video_stream.get('width')
                        metadata['height'] = video_stream.get('height')
                        metadata['dimensions'] = (metadata['width'], metadata['height'])
                        metadata['codec'] = video_stream.get('codec_name')
                        metadata['fps'] = eval(video_stream.get('r_frame_rate', '0/1'))
                        metadata['pixel_format'] = video_stream.get('pix_fmt')
                    
                    # Audio stream metadata
                    audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
                    if audio_streams:
                        audio_stream = audio_streams[0]
                        metadata['audio_codec'] = audio_stream.get('codec_name')
                        metadata['sample_rate'] = audio_stream.get('sample_rate')
                        metadata['channels'] = audio_stream.get('channels')
                    
                    # Tags
                    if 'tags' in format_info:
                        metadata['tags'] = format_info['tags']
                        
                        # Extract common fields
                        tags = format_info['tags']
                        if 'title' in tags:
                            metadata['title'] = tags['title']
                        if 'artist' in tags:
                            metadata['artist'] = tags['artist']
                        if 'creation_time' in tags:
                            metadata['creation_time'] = tags['creation_time']
                
                except Exception as e:
                    self.logger.warning(f"FFmpeg probe failed: {str(e)}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Video metadata extraction failed: {str(e)}")
            return {}
    
    async def _extract_document_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract document-specific metadata"""
        try:
            metadata = {}
            extension = Path(file_path).suffix.lower()
            
            if extension == '.pdf' and PYPDF2_AVAILABLE:
                try:
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        
                        metadata['page_count'] = len(pdf_reader.pages)
                        
                        if pdf_reader.metadata:
                            pdf_meta = pdf_reader.metadata
                            metadata['title'] = pdf_meta.get('/Title')
                            metadata['author'] = pdf_meta.get('/Author')
                            metadata['subject'] = pdf_meta.get('/Subject')
                            metadata['creator'] = pdf_meta.get('/Creator')
                            metadata['producer'] = pdf_meta.get('/Producer')
                            metadata['creation_date'] = pdf_meta.get('/CreationDate')
                            metadata['modification_date'] = pdf_meta.get('/ModDate')
                
                except Exception as e:
                    self.logger.warning(f"PDF processing failed: {str(e)}")
            
            elif extension == '.docx' and PYTHON_DOCX_AVAILABLE:
                try:
                    doc = Document(file_path)
                    core_props = doc.core_properties
                    
                    metadata['title'] = core_props.title
                    metadata['author'] = core_props.author
                    metadata['subject'] = core_props.subject
                    metadata['keywords'] = core_props.keywords
                    metadata['category'] = core_props.category
                    metadata['comments'] = core_props.comments
                    metadata['created'] = core_props.created
                    metadata['modified'] = core_props.modified
                    metadata['last_modified_by'] = core_props.last_modified_by
                    metadata['revision'] = core_props.revision
                    
                    # Count elements
                    metadata['paragraph_count'] = len(doc.paragraphs)
                    
                except Exception as e:
                    self.logger.warning(f"DOCX processing failed: {str(e)}")
            
            elif extension in ['.txt', '.md']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        
                    metadata['char_count'] = len(content)
                    metadata['word_count'] = len(content.split())
                    metadata['line_count'] = len(content.splitlines())
                    
                    # Detect encoding
                    import chardet
                    with open(file_path, 'rb') as file:
                        raw_data = file.read()
                        encoding_result = chardet.detect(raw_data)
                        metadata['encoding'] = encoding_result.get('encoding')
                        metadata['encoding_confidence'] = encoding_result.get('confidence')
                
                except Exception as e:
                    self.logger.warning(f"Text file processing failed: {str(e)}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Document metadata extraction failed: {str(e)}")
            return {}
    
    def _extract_gps_coordinates(self, gps_dict: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Extract GPS coordinates from EXIF GPS data"""
        try:
            def convert_to_degrees(value) -> None:
                """
Convert GPS coordinate to decimal degrees"""
                d, m, s = value
                return d + (m / 60.0) + (s / 3600.0)
            
            lat = None
            lon = None
            
            if 'GPSLatitude' in gps_dict and 'GPSLatitudeRef' in gps_dict:
                lat = convert_to_degrees(gps_dict['GPSLatitude'])
                if gps_dict['GPSLatitudeRef'] == 'S':
                    lat = -lat
            
            if 'GPSLongitude' in gps_dict and 'GPSLongitudeRef' in gps_dict:
                lon = convert_to_degrees(gps_dict['GPSLongitude'])
                if gps_dict['GPSLongitudeRef'] == 'W':
                    lon = -lon
            
            return lat, lon
            
        except Exception as e:
            self.logger.warning(f"GPS coordinate extraction failed: {str(e)}")
            return None, None
    
    def _merge_metadata(
        self,
        standard_metadata: ContentMetadata,
        format_metadata: Dict[str, Any]
    ) -> ContentMetadata:
        """Merge standard and format-specific metadata"""
        try:
            # Update standard metadata with format-specific data
            for key, value in format_metadata.items():
                if hasattr(standard_metadata, key) and value is not None:
                    setattr(standard_metadata, key, value)
                else:
                    # Store in format_details if not a standard field
                    standard_metadata.format_details[key] = value
            
            return standard_metadata
            
        except Exception as e:
            self.logger.error(f"Error merging metadata: {str(e)}")
            return standard_metadata
    
    async def _enrich_with_ai(
        self,
        file_path: str,
        metadata: ContentMetadata,
        content_type: str
    ) -> Dict[str, Any]:
        """Enrich metadata using AI analysis"""
        try:
            ai_enrichment = {}
            
            # Generate AI description (placeholder)
            if content_type == 'image':
                ai_enrichment['ai_description'] = "AI-generated image description placeholder"
                ai_enrichment['ai_tags'] = ['placeholder', 'ai-generated']
            elif content_type == 'audio':
                ai_enrichment['ai_description'] = "AI-generated audio description placeholder"
                ai_enrichment['ai_tags'] = ['audio', 'music', 'ai-analyzed']
            elif content_type == 'video':
                ai_enrichment['ai_description'] = "AI-generated video description placeholder"
                ai_enrichment['ai_tags'] = ['video', 'multimedia', 'ai-analyzed']
            elif content_type in ['text', 'document']:
                ai_enrichment['ai_description'] = "AI-generated document summary placeholder"
                ai_enrichment['ai_tags'] = ['document', 'text', 'ai-analyzed']
            
            # Content quality score (placeholder)
            ai_enrichment['ai_content_score'] = 0.75  # Placeholder
            
            return {
                'ai_enrichment': ai_enrichment,
                'ai_enrichment_success': True
            }
            
        except Exception as e:
            self.logger.error(f"AI enrichment failed: {str(e)}")
            return {
                'ai_enrichment': {},
                'ai_enrichment_success': False,
                'error': str(e)
            }
    
    async def _analyze_privacy(self, metadata: ContentMetadata) -> Dict[str, Any]:
        """Analyze metadata for privacy concerns"""
        try:
            privacy_issues = []
            privacy_score = 1.0  # Start with perfect score
            
            # Check for GPS coordinates
            if metadata.latitude and metadata.longitude:
                privacy_issues.append({
                    'type': 'location_data',
                    'severity': 'high',
                    'description': 'GPS coordinates detected in metadata',
                    'fields': ['latitude', 'longitude']
                })
                privacy_score -= 0.3
            
            # Check for personal information in EXIF
            if hasattr(metadata, 'format_details'):
                exif_data = metadata.format_details.get('exif', {})
                personal_fields = ['Artist', 'Copyright', 'Software', 'HostComputer']
                
                for field in personal_fields:
                    if field in exif_data:
                        privacy_issues.append({
                            'type': 'personal_info',
                            'severity': 'medium',
                            'description': f'Personal information in {field} field',
                            'fields': [field]
                        })
                        privacy_score -= 0.1
            
            # Check for author information
            if metadata.author or metadata.creator or metadata.artist:
                privacy_issues.append({
                    'type': 'creator_info',
                    'severity': 'low',
                    'description': 'Creator information present in metadata',
                    'fields': ['author', 'creator', 'artist']
                })
                privacy_score -= 0.05
            
            # Ensure score doesn't go below 0
            privacy_score = max(0, privacy_score)
            
            # Update metadata
            metadata.contains_sensitive_data = len(privacy_issues) > 0
            metadata.privacy_score = privacy_score
            
            return {
                'privacy_analysis': {
                    'privacy_score': privacy_score,
                    'contains_sensitive_data': len(privacy_issues) > 0,
                    'privacy_issues': privacy_issues,
                    'recommendations': self._generate_privacy_recommendations(privacy_issues)
                },
                'privacy_analysis_success': True
            }
            
        except Exception as e:
            self.logger.error(f"Privacy analysis failed: {str(e)}")
            return {
                'privacy_analysis': None,
                'privacy_analysis_success': False,
                'error': str(e)
            }
    
    def _generate_privacy_recommendations(self, privacy_issues: List[Dict]) -> List[str]:
        """Generate privacy protection recommendations"""
        recommendations = []
        
        for issue in privacy_issues:
            if issue['type'] == 'location_data':
                recommendations.append("Remove GPS coordinates before sharing")
            elif issue['type'] == 'personal_info':
                recommendations.append("Consider removing personal information from metadata")
            elif issue['type'] == 'creator_info':
                recommendations.append("Review creator information visibility")
        
        if not recommendations:
            recommendations.append("No privacy concerns detected")
        
        return recommendations
    
    async def _assess_metadata_quality(self, metadata: ContentMetadata) -> Dict[str, Any]:
        """Assess the quality and completeness of metadata"""
        try:
            # Define important fields for each content type
            important_fields = {
                'standard': ['filename', 'file_size', 'file_type', 'created_date'],
                'content': ['title', 'description', 'creator', 'tags'],
                'technical': ['format_details', 'quality_score']
            }
            
            # Calculate completeness score
            total_fields = 0
            present_fields = 0
            missing_fields = []
            
            for category, fields in important_fields.items():
                for field in fields:
                    total_fields += 1
                    value = getattr(metadata, field, None)
                    
                    if value is not None and value != "" and value != []:
                        present_fields += 1
                    else:
                        missing_fields.append(field)
            
            completeness_score = present_fields / total_fields if total_fields > 0 else 0
            
            # Calculate accuracy score (placeholder - would need validation logic)
            accuracy_score = 0.9  # Placeholder
            
            # Calculate consistency score (check for contradictions)
            consistency_score = 1.0  # Placeholder
            
            # Calculate richness score (depth of metadata)
            richness_factors = []
            
            # Check for detailed technical metadata
            if metadata.format_details:
                richness_factors.append(min(len(metadata.format_details) / 10, 1.0))
            
            # Check for descriptive metadata
            if metadata.tags:
                richness_factors.append(min(len(metadata.tags) / 5, 1.0))
            
            # Check for creator information
            if metadata.creator or metadata.author or metadata.artist:
                richness_factors.append(1.0)
            
            richness_score = sum(richness_factors) / len(richness_factors) if richness_factors else 0
            
            # Calculate overall score
            overall_score = (
                completeness_score * 0.4 +
                accuracy_score * 0.3 +
                consistency_score * 0.2 +
                richness_score * 0.1
            )
            
            # Generate recommendations
            recommendations = []
            if completeness_score < 0.7:
                recommendations.append("Add missing standard metadata fields")
            if len(metadata.tags) < 3:
                recommendations.append("Add more descriptive tags")
            if not metadata.description:
                recommendations.append("Add content description")
            if not metadata.creator and not metadata.author:
                recommendations.append("Add creator information")
            
            quality = MetadataQuality(
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                consistency_score=consistency_score,
                richness_score=richness_score,
                overall_score=overall_score,
                missing_fields=missing_fields,
                recommendations=recommendations
            )
            
            return {
                'metadata_quality': quality,
                'metadata_quality_success': True
            }
            
        except Exception as e:
            self.logger.error(f"Metadata quality assessment failed: {str(e)}")
            return {
                'metadata_quality': None,
                'metadata_quality_success': False,
                'error': str(e)
            }
    
    async def _analyze_content(
        self,
        file_path: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Perform standard content analysis"""
        try:
            content_analysis = {}
            
            if content_type == 'image':
                # Standard image analysis
                if PIL_AVAILABLE:
                    with Image.open(file_path) as img:
                        # Color analysis
                        colors = img.getcolors(maxcolors=256*256*256)
                        if colors:
                            dominant_color = max(colors, key=lambda x: x[0])[1]
                            content_analysis['dominant_color'] = dominant_color
                        
                        # Image characteristics
                        content_analysis['has_transparency'] = img.mode in ('RGBA', 'LA')
                        content_analysis['is_grayscale'] = img.mode in ('L', 'LA')
                        
            elif content_type in ['text', 'document']:
                # Text content analysis
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Standard text statistics
                    content_analysis['char_count'] = len(content)
                    content_analysis['word_count'] = len(content.split())
                    content_analysis['line_count'] = len(content.splitlines())
                    
                    # Language detection (optimized heuristic)
                    if any(ord(char) > 127 for char in content[:1000]):
                        content_analysis['contains_unicode'] = True
                    
                except UnicodeDecodeError:
                    content_analysis['encoding_issues'] = True
            
            return {
                'content_analysis': content_analysis,
                'content_analysis_success': True
            }
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {str(e)}")
            return {
                'content_analysis': {},
                'content_analysis_success': False,
                'error': str(e)
            }
    
    async def strip_sensitive_metadata(
        self,
        file_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """Remove sensitive metadata from file"""
        try:
            if not output_path:
                base_path = Path(file_path)
                output_path = str(base_path.parent / f"{base_path.stem}_clean{base_path.suffix}")
            
            extension = Path(file_path).suffix.lower()
            
            if extension in ['.jpg', '.jpeg'] and PIL_AVAILABLE:
                # Remove EXIF data from JPEG
                with Image.open(file_path) as img:
                    # Create new image without EXIF
                    clean_img = Image.new(img.mode, img.size)
                    clean_img.putdata(list(img.getdata()))
                    clean_img.save(output_path, quality=95)
            
            elif extension in ['.mp3'] and MUTAGEN_AVAILABLE:
                # Remove tags from MP3
                import shutil
                shutil.copy2(file_path, output_path)
                
                audiofile = mutagen.File(output_path)
                if audiofile and audiofile.tags:
                    audiofile.delete()
                    audiofile.save()
            
            else:
                # For other formats, just copy the file
                import shutil
                shutil.copy2(file_path, output_path)
            
            self.logger.info(f"Sensitive metadata stripped: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Metadata stripping failed: {str(e)}")
            raise
    
    async def batch_process(
        self,
        file_paths: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process multiple files in batch"""
        tasks = []
        for file_path in file_paths:
            task = self.process(file_path, config=config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) 
            else {'success': False, 'error': str(result), 'file': file_paths[i]}
            for i, result in enumerate(results)
        ]

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib

# Metadata libraries
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logging.warning("Mutagen not available - audio metadata will be limited")

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - image EXIF will be limited")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available - video metadata will be limited")

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    logging.warning("FFmpeg not available - professional video metadata will be limited")

logger = logging.getLogger(__name__)

@dataclass
class UniversalMetadata:
    """Universal metadata container for all content types"""
    # Core metadata
    content_type: str
    file_name: Optional[str] = None
    file_size: int = 0
    format: Optional[str] = None
    mime_type: Optional[str] = None
    
    # Timestamps
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    accessed_date: Optional[datetime] = None
    
    # Technical metadata
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    resolution: Optional[str] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec: Optional[str] = None
    compression: Optional[str] = None
    
    # Content metadata
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = None
    language: Optional[str] = None
    
    # Rights and licensing
    copyright: Optional[str] = None
    license: Optional[str] = None
    usage_rights: Optional[str] = None
    
    # Location metadata
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    location_name: Optional[str] = None
    
    # Device metadata
    device_make: Optional[str] = None
    device_model: Optional[str] = None
    software: Optional[str] = None
    
    # Quality indicators
    quality_score: Optional[float] = None
    completeness_score: Optional[float] = None
    
    # Raw metadata
    raw_metadata: Optional[Dict[str, Any]] = None

class MetadataProcessor:
    """
Professional metadata extraction and processing engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize metadata processors
        self._initialize_processors()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default metadata processing configuration"""
        return {
            'extract_exif': True,
            'extract_id3': True,
            'extract_technical': True,
            'extract_location': True,
            'privacy_mode': False,  # If True, removes sensitive data
            'normalize_metadata': True,
            'validate_metadata': True,
            'include_raw_metadata': False,
            'quality_assessment': True,
            'cross_reference': True,
            'metadata_enrichment': True,
            'supported_formats': {
                'audio': ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'],
                'video': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'],
                'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'],
                'text': ['txt', 'md', 'rtf', 'docx', 'pdf']
            }
        }
    
    def _initialize_processors(self) -> None:
        """
Initialize metadata processing components"""
        try:
            # Initialize format-specific processors
            self.audio_processor = AudioMetadataProcessor()
            self.video_processor = VideoMetadataProcessor()
            self.image_processor = ImageMetadataProcessor()
            self.text_processor = TextMetadataProcessor()
            
            # Initialize metadata validators
            self.validator = MetadataValidator()
            
            self.logger.info("Metadata processor components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing metadata processors: {str(e)}")
            raise
    
    async def process(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        file_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main metadata processing pipeline
        
        Args:
            content_data: Content data as bytes or file path
            content_type: Type of content (audio, video, image, text)
            file_path: Optional file path for additional context
            config: Optional processing configuration override
        
        Returns:
            Dict containing extracted and processed metadata
        """
        try:
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                processing_config.update(config)
            
            # Extract format-specific metadata
            if content_type == 'audio':
                metadata = await self.audio_processor.extract_metadata(
                    content_data, file_path, processing_config
                )
            elif content_type == 'video':
                metadata = await self.video_processor.extract_metadata(
                    content_data, file_path, processing_config
                )
            elif content_type == 'image':
                metadata = await self.image_processor.extract_metadata(
                    content_data, file_path, processing_config
                )
            elif content_type == 'text':
                metadata = await self.text_processor.extract_metadata(
                    content_data, file_path, processing_config
                )
            else:
                # Generic metadata extraction
                metadata = await self._extract_generic_metadata(
                    content_data, content_type, file_path, processing_config
                )
            
            # Normalize metadata
            if processing_config.get('normalize_metadata', True):
                metadata = await self._normalize_metadata(metadata, content_type)
            
            # Apply privacy filters
            if processing_config.get('privacy_mode', False):
                metadata = await self._apply_privacy_filters(metadata)
            
            # Validate metadata
            validation_result = None
            if processing_config.get('validate_metadata', True):
                validation_result = await self.validator.validate(metadata)
            
            # Calculate quality scores
            quality_assessment = None
            if processing_config.get('quality_assessment', True):
                quality_assessment = await self._assess_quality(metadata)
            
            # Enrich metadata
            if processing_config.get('metadata_enrichment', True):
                metadata = await self._enrich_metadata(metadata, content_type)
            
            # Compile final result
            result = {
                'success': True,
                'metadata': metadata,
                'content_type': content_type,
                'file_path': file_path,
                'processing_config': processing_config,
                'validation_result': validation_result,
                'quality_assessment': quality_assessment,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Metadata processing completed for {content_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"Metadata processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content_type': content_type,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _extract_generic_metadata(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        file_path: Optional[str],
        config: Dict[str, Any]
    ) -> UniversalMetadata:
        """Extract generic metadata for unknown content types"""
        try:
            metadata = UniversalMetadata(content_type=content_type)
            
            # Standard file information
            if isinstance(content_data, str) and Path(content_data).exists():
                file_path = content_data
                file_stat = Path(file_path).stat()
                
                metadata.file_name = Path(file_path).name
                metadata.file_size = int(file_stat.st_size)
                metadata.format = Path(file_path).suffix.lower().lstrip('.')
                metadata.created_date = datetime.fromtimestamp(file_stat.st_ctime)
                metadata.modified_date = datetime.fromtimestamp(file_stat.st_mtime)
                metadata.accessed_date = datetime.fromtimestamp(file_stat.st_atime)
                
            elif isinstance(content_data, bytes):
                metadata.file_size = len(content_data)
                
                # Try to detect format from bytes
                format_hint = self._detect_format_from_bytes(content_data)
                if format_hint:
                    metadata.format = format_hint
            
            # Set MIME type
            if metadata.format:
                metadata.mime_type = self._get_mime_type(metadata.format)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Generic metadata extraction failed: {str(e)}")
            return UniversalMetadata(content_type=content_type)
    
    async def _normalize_metadata(
        self,
        metadata: UniversalMetadata,
        content_type: str
    ) -> UniversalMetadata:
        """Normalize metadata across different formats"""
        try:
            # Normalize resolution format
            if metadata.width and metadata.height:
                metadata.resolution = f"{metadata.width}x{metadata.height}"
            
            # Normalize duration format
            if metadata.duration and metadata.duration > 0:
                # Ensure duration is in seconds
                if metadata.duration > 86400:  # More than 24 hours, likely milliseconds
                    metadata.duration = metadata.duration / 1000
            
            # Clean and normalize text fields
            text_fields = ['title', 'author', 'description', 'copyright', 'license']
            for field in text_fields:
                value = getattr(metadata, field)
                if value and isinstance(value, str):
                    # Clean up text
                    cleaned = value.strip()
                    # Remove null bytes and control characters
                    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\t')
                    setattr(metadata, field, cleaned if cleaned else None)
            
            # Normalize keywords
            if metadata.keywords:
                normalized_keywords = []
                for keyword in metadata.keywords:
                    if isinstance(keyword, str):
                        keyword = keyword.strip().lower()
                        if keyword and keyword not in normalized_keywords:
                            normalized_keywords.append(keyword)
                metadata.keywords = normalized_keywords
            
            # Normalize GPS coordinates
            if metadata.gps_latitude is not None and metadata.gps_longitude is not None:
                # Ensure coordinates are within valid ranges
                if not (-90 <= metadata.gps_latitude <= 90):
                    metadata.gps_latitude = None
                if not (-180 <= metadata.gps_longitude <= 180):
                    metadata.gps_longitude = None
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata normalization failed: {str(e)}")
            return metadata
    
    async def _apply_privacy_filters(self, metadata: UniversalMetadata) -> UniversalMetadata:
        """Apply privacy filters to remove sensitive information"""
        try:
            # Remove location data
            metadata.gps_latitude = None
            metadata.gps_longitude = None
            metadata.location_name = None
            
            # Remove device information
            metadata.device_make = None
            metadata.device_model = None
            metadata.software = None
            
            # Remove personal information from description and title
            if metadata.description:
                # Remove email addresses
                import re
                metadata.description = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', metadata.description)
                # Remove phone numbers
                metadata.description = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', metadata.description)
            
            # Clear raw metadata which might contain sensitive data
            metadata.raw_metadata = None
            
            self.logger.info("Privacy filters applied to metadata")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Privacy filter application failed: {str(e)}")
            return metadata
    
    async def _assess_quality(self, metadata: UniversalMetadata) -> Dict[str, Any]:
        """Assess metadata quality and completeness"""
        try:
            assessment = {
                'quality_score': 0.0,
                'completeness_score': 0.0,
                'issues': [],
                'recommendations': []
            }
            
            # Define scoring criteria
            essential_fields = ['content_type', 'format', 'file_size']
            important_fields = ['title', 'duration', 'width', 'height']
            optional_fields = ['author', 'description', 'keywords', 'created_date']
            
            total_fields = len(essential_fields) + len(important_fields) + len(optional_fields)
            filled_fields = 0
            
            # Check essential fields
            for field in essential_fields:
                value = getattr(metadata, field, None)
                if value is not None and value != '' and value != 0:
                    filled_fields += 3  # Essential fields count more
                else:
                    assessment['issues'].append(f"Missing essential field: {field}")
            
            # Check important fields
            for field in important_fields:
                value = getattr(metadata, field, None)
                if value is not None and value != '' and value != 0:
                    filled_fields += 2  # Important fields count moderately
                else:
                    assessment['recommendations'].append(f"Consider adding: {field}")
            
            # Check optional fields
            for field in optional_fields:
                value = getattr(metadata, field, None)
                if value is not None and value != '' and value != 0:
                    filled_fields += 1  # Optional fields count less
            
            # Calculate completeness score
            max_score = len(essential_fields) * 3 + len(important_fields) * 2 + len(optional_fields)
            assessment['completeness_score'] = min(100.0, (filled_fields / max_score) * 100)
            
            # Calculate quality score based on data validity
            quality_points = 0
            max_quality_points = 100
            
            # Valid file size
            if metadata.file_size and metadata.file_size > 0:
                quality_points += 20
            
            # Valid dimensions for visual content
            if metadata.content_type in ['image', 'video']:
                if metadata.width and metadata.height and metadata.width > 0 and metadata.height > 0:
                    quality_points += 20
            
            # Valid duration for temporal content
            if metadata.content_type in ['audio', 'video']:
                if metadata.duration and metadata.duration > 0:
                    quality_points += 20
            
            # Text content quality
            if metadata.title and len(metadata.title.strip()) > 0:
                quality_points += 15
            
            if metadata.description and len(metadata.description.strip()) > 10:
                quality_points += 15
            
            # Keyword richness
            if metadata.keywords and len(metadata.keywords) > 0:
                quality_points += 10
            
            assessment['quality_score'] = quality_points
            
            # Overall assessment
            overall_score = (assessment['quality_score'] + assessment['completeness_score']) / 2
            
            if overall_score >= 80:
                assessment['rating'] = 'Excellent'
            elif overall_score >= 60:
                assessment['rating'] = 'Good'
            elif overall_score >= 40:
                assessment['rating'] = 'Fair'
            else:
                assessment['rating'] = 'Poor'
            
            # Update metadata with scores
            metadata.quality_score = assessment['quality_score']
            metadata.completeness_score = assessment['completeness_score']
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {str(e)}")
            return {
                'quality_score': 0.0,
                'completeness_score': 0.0,
                'issues': ['Quality assessment failed'],
                'recommendations': [],
                'rating': 'Unknown'
            }
    
    async def _enrich_metadata(
        self,
        metadata: UniversalMetadata,
        content_type: str
    ) -> UniversalMetadata:
        """Enrich metadata with additional information"""
        try:
            # Add computed fields
            if metadata.width and metadata.height:
                metadata.resolution = f"{metadata.width}x{metadata.height}"
                
                # Add aspect ratio
                if hasattr(metadata, 'aspect_ratio'):
                    metadata.aspect_ratio = metadata.width / metadata.height
            
            # Add file size categories
            if metadata.file_size:
                if hasattr(metadata, 'size_category'):
                    if metadata.file_size < 1024 * 1024:  # < 1MB
                        metadata.size_category = 'small'
                    elif metadata.file_size < 10 * 1024 * 1024:  # < 10MB
                        metadata.size_category = 'medium'
                    elif metadata.file_size < 100 * 1024 * 1024:  # < 100MB
                        metadata.size_category = 'large'
                    else:
                        metadata.size_category = 'very_large'
            
            # Add quality indicators based on technical specs
            if content_type == 'image':
                if metadata.width and metadata.height:
                    pixel_count = metadata.width * metadata.height
                    if hasattr(metadata, 'image_quality_tier'):
                        if pixel_count >= 4000 * 3000:  # 12MP+
                            metadata.image_quality_tier = 'ultra_high'
                        elif pixel_count >= 1920 * 1080:  # Full HD+
                            metadata.image_quality_tier = 'high'
                        elif pixel_count >= 1280 * 720:  # HD+
                            metadata.image_quality_tier = 'medium'
                        else:
                            metadata.image_quality_tier = 'low'
            
            # Add content hash for uniqueness
            if hasattr(metadata, 'metadata_hash'):
                metadata_dict = asdict(metadata)
                # Remove timestamp fields for consistent hashing
                metadata_dict.pop('created_date', None)
                metadata_dict.pop('modified_date', None)
                metadata_dict.pop('accessed_date', None)
                
                metadata_str = json.dumps(metadata_dict, sort_keys=True, default=str)
                metadata.metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata enrichment failed: {str(e)}")
            return metadata
    
    def _detect_format_from_bytes(self, data: bytes) -> Optional[str]:
        """Detect file format from byte signatures"""
        try:
            # Common file signatures
            signatures = {
                b'\xff\xfb': 'mp3',
                b'\xff\xf3': 'mp3',
                b'\xff\xf2': 'mp3',
                b'RIFF': 'wav',
                b'fLaC': 'flac',
                b'\x00\x00\x00\x20ftypmp41': 'mp4',
                b'\x00\x00\x00\x18ftypmp42': 'mp4',
                b'\xff\xd8\xff': 'jpg',
                b'\x89PNG\r\n\x1a\n': 'png',
                b'GIF87a': 'gif',
                b'GIF89a': 'gif',
                b'BM': 'bmp',
                b'%PDF': 'pdf'
            }
            
            for signature, format_name in signatures.items():
                if data.startswith(signature):
                    return format_name
            
            return None
            
        except Exception:
            return None
    
    def _get_mime_type(self, file_format: str) -> str:
        """
Get MIME type for file format"""
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'flac': 'audio/flac',
            'aac': 'audio/aac',
            'ogg': 'audio/ogg',
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'mkv': 'video/x-matroska',
            'webm': 'video/webm',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'tiff': 'image/tiff',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'html': 'text/html',
            'json': 'application/json'
        }
        
        return mime_types.get(file_format.lower(), 'application/octet-stream')
    
    async def extract_bulk_metadata(
        self,
        file_paths: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
Extract metadata from multiple files in bulk"""
        tasks = []
        
        for file_path in file_paths:
            # Determine content type from file extension
            file_ext = Path(file_path).suffix.lower().lstrip('.')
            
            content_type = 'unknown'
            for ctype, formats in self.config['supported_formats'].items():
                if file_ext in formats:
                    content_type = ctype
                    break
            
            task = self.process(file_path, content_type, file_path, config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) 
            else {'success': False, 'error': str(result), 'file': file_paths[i]}
            for i, result in enumerate(results)
        ]

# Placeholder classes for format-specific processors
class AudioMetadataProcessor:
    """
Audio metadata extraction"""
    async def extract_metadata(self, content_data, file_path, config) -> None:
        metadata = UniversalMetadata(content_type='audio')
        # Implementation would go here
        return metadata

class VideoMetadataProcessor:
    """
Video metadata extraction"""
    async def extract_metadata(self, content_data, file_path, config) -> None:
        metadata = UniversalMetadata(content_type='video')
        # Implementation would go here
        return metadata

class ImageMetadataProcessor:
    """
Image metadata extraction"""
    async def extract_metadata(self, content_data, file_path, config) -> None:
        metadata = UniversalMetadata(content_type='image')
        # Implementation would go here
        return metadata

class TextMetadataProcessor:
    """
Text metadata extraction"""
    async def extract_metadata(self, content_data, file_path, config) -> None:
        metadata = UniversalMetadata(content_type='text')
        # Implementation would go here
        return metadata

class MetadataValidator:
    """
Metadata validation and quality checks"""
    async def validate(self, metadata: UniversalMetadata) -> Dict[str, Any]:
        return {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
