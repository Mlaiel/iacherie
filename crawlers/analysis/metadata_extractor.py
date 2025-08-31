"""
Metadata Extractor
==================

Advanced metadata extraction system for comprehensive content analysis.
Implements intelligent metadata parsing, enhancement, and standardization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import hashlib
import mimetypes
import os
import requests
from urllib.parse import urlparse, parse_qs, unquote
import exifread
from PIL import Image
from PIL.ExifTags import TAGS
import eyed3
import ffmpeg
import cv2
import librosa
import pandas as pd
from bs4 import BeautifulSoup
import magic
import chardet

logger = logging.getLogger(__name__)

class ExtractionStrategy(Enum):
    """Metadata extraction strategies."""
    COMPREHENSIVE = "comprehensive"
    FAST = "fast"
    DEEP_ANALYSIS = "deep_analysis"
    SECURITY_FOCUSED = "security_focused"
    COMPLIANCE = "compliance"

class MetadataCategory(Enum):
    """Metadata categories."""
    TECHNICAL = "technical"
    DESCRIPTIVE = "descriptive"
    RIGHTS = "rights"
    STRUCTURAL = "structural"
    ADMINISTRATIVE = "administrative"
    PRESERVATION = "preservation"

class ContentFormat(Enum):
    """Supported content formats."""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    WEB_PAGE = "web_page"
    SOCIAL_POST = "social_post"
    UNKNOWN = "unknown"

@dataclass
class ContentMetadata:
    """Comprehensive content metadata structure."""
    content_id: str
    format_type: ContentFormat
    extraction_strategy: ExtractionStrategy
    
    # Technical metadata
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    file_extension: Optional[str] = None
    encoding: Optional[str] = None
    checksum_md5: Optional[str] = None
    checksum_sha256: Optional[str] = None
    
    # Descriptive metadata
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    language: Optional[str] = None
    subject: Optional[str] = None
    
    # Rights metadata
    creator: Optional[str] = None
    author: Optional[str] = None
    copyright: Optional[str] = None
    license: Optional[str] = None
    rights_holder: Optional[str] = None
    usage_rights: Optional[str] = None
    
    # Temporal metadata
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    published_date: Optional[datetime] = None
    extracted_date: datetime = field(default_factory=datetime.now)
    
    # Location metadata
    location: Optional[str] = None
    coordinates: Optional[Tuple[float, float]] = None
    country: Optional[str] = None
    city: Optional[str] = None
    
    # Source metadata
    source_url: Optional[str] = None
    source_platform: Optional[str] = None
    source_domain: Optional[str] = None
    referrer: Optional[str] = None
    
    # Format-specific metadata
    image_metadata: Optional[Dict[str, Any]] = None
    audio_metadata: Optional[Dict[str, Any]] = None
    video_metadata: Optional[Dict[str, Any]] = None
    document_metadata: Optional[Dict[str, Any]] = None
    web_metadata: Optional[Dict[str, Any]] = None
    
    # Quality and integrity
    quality_score: float = 0.0
    completeness_score: float = 0.0
    reliability_score: float = 0.0
    
    # Processing metadata
    extraction_time: float = 0.0
    extraction_errors: List[str] = field(default_factory=list)
    validation_status: str = "pending"
    
    # Custom metadata
    custom_fields: Dict[str, Any] = field(default_factory=dict)

class MetadataExtractor:
    """
    Advanced metadata extraction system with comprehensive format support.
    
    Features:
    - Multi-format metadata extraction (images, audio, video, documents, web)
    - Intelligent metadata enhancement and enrichment
    - Privacy-aware and security-focused extraction
    - Compliance-ready metadata standardization
    - Real-time and batch processing capabilities
    - Quality assessment and validation
    """
    
    def __init__(
        self,
        cache_dir: str = "/tmp/metadata_cache",
        default_strategy: ExtractionStrategy = ExtractionStrategy.COMPREHENSIVE,
        enable_external_apis: bool = True,
        max_file_size: int = 100 * 1024 * 1024,  # 100MB
        timeout: int = 30
    ):
        """
        Initialize metadata extractor.
        
        Args:
            cache_dir: Directory for caching extracted metadata
            default_strategy: Default extraction strategy
            enable_external_apis: Enable external API calls for enrichment
            max_file_size: Maximum file size to process
            timeout: Extraction timeout in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_strategy = default_strategy
        self.enable_external_apis = enable_external_apis
        self.max_file_size = max_file_size
        self.timeout = timeout
        
        # Extraction statistics
        self.extraction_count = 0
        self.cache_hits = 0
        self.extraction_times = []
        self.format_counts = {}
        
        # Metadata cache
        self.metadata_cache = {}
        
        # External API configurations
        self.api_configs = {
            'reverse_image_search': {
                'enabled': False,
                'api_key': None,
                'endpoint': None
            },
            'content_recognition': {
                'enabled': False,
                'api_key': None,
                'endpoint': None
            }
        }
        
        logger.info(f"MetadataExtractor initialized with strategy: {default_strategy.value}")
    
    async def extract_metadata(
        self,
        content_id: str,
        content_source: Union[str, bytes, Path],
        strategy: Optional[ExtractionStrategy] = None,
        content_format: Optional[ContentFormat] = None
    ) -> ContentMetadata:
        """
        Extract comprehensive metadata from content.
        
        Args:
            content_id: Unique content identifier
            content_source: Content source (file path, URL, or raw data)
            strategy: Extraction strategy to use
            content_format: Content format hint
            
        Returns:
            ContentMetadata: Extracted metadata
        """
        start_time = datetime.now()
        strategy = strategy or self.default_strategy
        
        # Check cache first
        cache_key = self._generate_cache_key(content_id, content_source, strategy)
        if cache_key in self.metadata_cache:
            self.cache_hits += 1
            logger.debug(f"Metadata cache hit for {content_id}")
            return self.metadata_cache[cache_key]
        
        try:
            # Determine content format if not provided
            if content_format is None:
                content_format = await self._detect_content_format(content_source)
            
            # Initialize metadata structure
            metadata = ContentMetadata(
                content_id=content_id,
                format_type=content_format,
                extraction_strategy=strategy
            )
            
            # Extract basic metadata
            await self._extract_basic_metadata(metadata, content_source)
            
            # Extract format-specific metadata
            if content_format == ContentFormat.IMAGE:
                await self._extract_image_metadata(metadata, content_source)
            elif content_format == ContentFormat.AUDIO:
                await self._extract_audio_metadata(metadata, content_source)
            elif content_format == ContentFormat.VIDEO:
                await self._extract_video_metadata(metadata, content_source)
            elif content_format == ContentFormat.DOCUMENT:
                await self._extract_document_metadata(metadata, content_source)
            elif content_format == ContentFormat.WEB_PAGE:
                await self._extract_web_metadata(metadata, content_source)
            elif content_format == ContentFormat.SOCIAL_POST:
                await self._extract_social_metadata(metadata, content_source)
            
            # Enhance metadata based on strategy
            if strategy in [ExtractionStrategy.COMPREHENSIVE, ExtractionStrategy.DEEP_ANALYSIS]:
                await self._enhance_metadata(metadata, strategy)
            
            # Validate and assess quality
            await self._validate_metadata(metadata)
            await self._assess_metadata_quality(metadata)
            
            # Calculate extraction time
            extraction_time = (datetime.now() - start_time).total_seconds()
            metadata.extraction_time = extraction_time
            self.extraction_times.append(extraction_time)
            
            # Update statistics
            self.extraction_count += 1
            self.format_counts[content_format.value] = self.format_counts.get(content_format.value, 0) + 1
            
            # Cache metadata
            self.metadata_cache[cache_key] = metadata
            
            logger.info(f"Metadata extracted for {content_id}: {content_format.value}")
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed for {content_id}: {e}")
            # Return minimal metadata with error information
            return ContentMetadata(
                content_id=content_id,
                format_type=content_format or ContentFormat.UNKNOWN,
                extraction_strategy=strategy,
                extraction_errors=[str(e)],
                validation_status="failed",
                extraction_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _detect_content_format(self, content_source: Union[str, bytes, Path]) -> ContentFormat:
        """Detect content format from source."""



        try:
            if isinstance(content_source, str) and content_source.startswith(('http://', 'https://')):
                # Web URL
                parsed_url = urlparse(content_source)
                if any(platform in parsed_url.netloc.lower() for platform in 
                       ['twitter.com', 'instagram.com', 'facebook.com', 'tiktok.com']):
                    return ContentFormat.SOCIAL_POST
                else:
                    return ContentFormat.WEB_PAGE
            
            elif isinstance(content_source, (str, Path)):
                # File path
                path = Path(content_source)
                if path.exists():
                    mime_type, _ = mimetypes.guess_type(str(path))
                    if mime_type:
                        if mime_type.startswith('image/'):
                            return ContentFormat.IMAGE
                        elif mime_type.startswith('audio/'):
                            return ContentFormat.AUDIO
                        elif mime_type.startswith('video/'):
                            return ContentFormat.VIDEO
                        elif mime_type.startswith('text/') or mime_type == 'application/pdf':
                            return ContentFormat.DOCUMENT
                
                # Try to detect by extension
                extension = path.suffix.lower()
                if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                    return ContentFormat.IMAGE
                elif extension in ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']:
                    return ContentFormat.AUDIO
                elif extension in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']:
                    return ContentFormat.VIDEO
                elif extension in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
                    return ContentFormat.DOCUMENT
            
            elif isinstance(content_source, bytes):
                # Try to detect from binary data
                try:
                    file_type = magic.from_buffer(content_source, mime=True)
                    if file_type.startswith('image/'):
                        return ContentFormat.IMAGE
                    elif file_type.startswith('audio/'):
                        return ContentFormat.AUDIO
                    elif file_type.startswith('video/'):
                        return ContentFormat.VIDEO
                except:
                    pass
            
        except Exception as e:
            logger.warning(f"Content format detection failed: {e}")
        
        return ContentFormat.UNKNOWN
    
    async def _extract_basic_metadata(
        self,
        metadata: ContentMetadata,
        content_source: Union[str, bytes, Path]
    ) -> None:
        """Extract basic metadata common to all content types."""



        try:
            if isinstance(content_source, (str, Path)) and Path(content_source).exists():
                path = Path(content_source)
                stat = path.stat()
                
                metadata.file_size = stat.st_size
                metadata.file_extension = path.suffix.lower()
                metadata.created_date = datetime.fromtimestamp(stat.st_ctime)
                metadata.modified_date = datetime.fromtimestamp(stat.st_mtime)
                
                # Calculate checksums
                with open(path, 'rb') as f:
                    file_data = f.read()
                    metadata.checksum_md5 = hashlib.md5(file_data).hexdigest()
                    metadata.checksum_sha256 = hashlib.sha256(file_data).hexdigest()
                
                # Detect MIME type
                metadata.mime_type, _ = mimetypes.guess_type(str(path))
                
            elif isinstance(content_source, bytes):
                metadata.file_size = len(content_source)
                metadata.checksum_md5 = hashlib.md5(content_source).hexdigest()
                metadata.checksum_sha256 = hashlib.sha256(content_source).hexdigest()
                
                # Try to detect MIME type from binary data
                try:
                    metadata.mime_type = magic.from_buffer(content_source, mime=True)
                except:
                    pass
                
                # Try to detect encoding for text content
                if metadata.mime_type and metadata.mime_type.startswith('text/'):
                    try:
                        encoding_result = chardet.detect(content_source)
                        metadata.encoding = encoding_result.get('encoding')
                    except:
                        pass
            
            elif isinstance(content_source, str) and content_source.startswith(('http://', 'https://')):
                # URL source
                metadata.source_url = content_source
                parsed_url = urlparse(content_source)
                metadata.source_domain = parsed_url.netloc
                
                # Extract platform information
                domain_lower = parsed_url.netloc.lower()
                if 'youtube.com' in domain_lower:
                    metadata.source_platform = 'YouTube'
                elif 'instagram.com' in domain_lower:
                    metadata.source_platform = 'Instagram'
                elif 'twitter.com' in domain_lower or 'x.com' in domain_lower:
                    metadata.source_platform = 'Twitter/X'
                elif 'tiktok.com' in domain_lower:
                    metadata.source_platform = 'TikTok'
                elif 'facebook.com' in domain_lower:
                    metadata.source_platform = 'Facebook'
                
        except Exception as e:
            metadata.extraction_errors.append(f"Basic metadata extraction error: {str(e)}")
            logger.warning(f"Basic metadata extraction failed: {e}")
    
    async def _extract_image_metadata(
        self,
        metadata: ContentMetadata,
        content_source: Union[str, bytes, Path]
    ) -> None:
        """Extract image-specific metadata."""



        try:
            # Load image
            if isinstance(content_source, (str, Path)):
                image = Image.open(content_source)
                image_path = content_source
            else:
                from io import BytesIO
                image = Image.open(BytesIO(content_source))
                image_path = None
            
            # Basic image properties
            width, height = image.size
            image_metadata = {
                'width': width,
                'height': height,
                'mode': image.mode,
                'format': image.format,
                'aspect_ratio': width / height if height > 0 else 0,
                'megapixels': (width * height) / 1000000
            }
            
            # Extract EXIF data
            if hasattr(image, '_getexif') and image._getexif():
                exif_data = {}
                exif = image._getexif()
                
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)
                    exif_data[tag] = value
                
                image_metadata['exif'] = exif_data
                
                # Extract specific EXIF fields
                if 'DateTime' in exif_data:
                    try:
                        metadata.created_date = datetime.strptime(exif_data['DateTime'], '%Y:%m:%d %H:%M:%S')
                    except:
                        pass
                
                if 'Artist' in exif_data:
                    metadata.creator = exif_data['Artist']
                
                if 'Copyright' in exif_data:
                    metadata.copyright = exif_data['Copyright']
                
                # GPS data
                if 'GPSInfo' in exif_data:
                    gps_info = exif_data['GPSInfo']
                    try:
                        lat, lon = self._parse_gps_coordinates(gps_info)
                        if lat and lon:
                            metadata.coordinates = (lat, lon)
                    except:
                        pass
            
            # Color analysis
            try:
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    rgb_image = image.convert('RGB')
                else:
                    rgb_image = image
                
                # Get dominant colors
                colors = rgb_image.getcolors(maxcolors=256*256*256)
                if colors:
                    dominant_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:5]
                    image_metadata['dominant_colors'] = [
                        {'color': color[1], 'count': color[0]} for color in dominant_colors
                    ]
            except:
                pass
            
            metadata.image_metadata = image_metadata
            
        except Exception as e:
            metadata.extraction_errors.append(f"Image metadata extraction error: {str(e)}")
            logger.warning(f"Image metadata extraction failed: {e}")
    
    async def _extract_audio_metadata(
        self,
        metadata: ContentMetadata,
        content_source: Union[str, bytes, Path]
    ) -> None:
        """Extract audio-specific metadata."""



        try:
            audio_metadata = {}
            
            # Try with eyed3 for MP3 files
            if isinstance(content_source, (str, Path)) and str(content_source).endswith('.mp3'):
                try:
                    audiofile = eyed3.load(content_source)
                    if audiofile and audiofile.tag:
                        tag = audiofile.tag
                        
                        metadata.title = tag.title
                        metadata.creator = tag.artist
                        metadata.author = tag.artist
                        
                        audio_metadata.update({
                            'album': tag.album,
                            'track_number': tag.track_num[0] if tag.track_num else None,
                            'genre': tag.genre.name if tag.genre else None,
                            'year': tag.getBestDate().year if tag.getBestDate() else None,
                            'duration': audiofile.info.time_secs if audiofile.info else None,
                            'bitrate': audiofile.info.bit_rate[0] if audiofile.info and audiofile.info.bit_rate else None,
                            'sample_rate': audiofile.info.sample_freq if audiofile.info else None,
                            'channels': audiofile.info.mode if audiofile.info else None
                        })
                except Exception as e:
                    logger.debug(f"eyed3 extraction failed: {e}")
            
            # Use librosa for general audio analysis
            try:
                if isinstance(content_source, (str, Path)):
                    y, sr = librosa.load(content_source)
                else:
                    # Handle bytes data
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                        tmp.write(content_source)
                        tmp.flush()
                        y, sr = librosa.load(tmp.name)
                        os.unlink(tmp.name)
                
                duration = len(y) / sr
                
                # Extract audio features
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                
                audio_metadata.update({
                    'librosa_duration': duration,
                    'librosa_sample_rate': sr,
                    'spectral_centroid_mean': float(spectral_centroid.mean()),
                    'tempo': float(tempo),
                    'mfcc_mean': mfccs.mean(axis=1).tolist(),
                    'rms_energy': float(np.sqrt(np.mean(y**2))),
                    'zero_crossing_rate': float(librosa.feature.zero_crossing_rate(y).mean())
                })
                
            except Exception as e:
                logger.debug(f"librosa extraction failed: {e}")
            
            metadata.audio_metadata = audio_metadata
            
        except Exception as e:
            metadata.extraction_errors.append(f"Audio metadata extraction error: {str(e)}")
            logger.warning(f"Audio metadata extraction failed: {e}")
    
    async def _extract_video_metadata(
        self,
        metadata: ContentMetadata,
        content_source: Union[str, bytes, Path]
    ) -> None:
        """Extract video-specific metadata."""



        try:
            video_metadata = {}
            
            # Use ffmpeg-python for video metadata
            if isinstance(content_source, (str, Path)):
                try:
                    probe = ffmpeg.probe(str(content_source))
                    
                    # General video information
                    format_info = probe.get('format', {})
                    video_metadata.update({
                        'duration': float(format_info.get('duration', 0)),
                        'size': int(format_info.get('size', 0)),
                        'bit_rate': int(format_info.get('bit_rate', 0)),
                        'format_name': format_info.get('format_name'),
                        'format_long_name': format_info.get('format_long_name')
                    })
                    
                    # Extract tags
                    tags = format_info.get('tags', {})
                    if tags:
                        metadata.title = tags.get('title')
                        metadata.creator = tags.get('artist') or tags.get('author')
                        metadata.created_date = self._parse_date(tags.get('creation_time'))
                        
                        video_metadata['tags'] = tags
                    
                    # Video stream information
                    video_streams = [s for s in probe.get('streams', []) if s.get('codec_type') == 'video']
                    if video_streams:
                        video_stream = video_streams[0]
                        video_metadata.update({
                            'width': int(video_stream.get('width', 0)),
                            'height': int(video_stream.get('height', 0)),
                            'codec_name': video_stream.get('codec_name'),
                            'codec_long_name': video_stream.get('codec_long_name'),
                            'pix_fmt': video_stream.get('pix_fmt'),
                            'level': video_stream.get('level'),
                            'color_range': video_stream.get('color_range'),
                            'color_space': video_stream.get('color_space'),
                            'r_frame_rate': video_stream.get('r_frame_rate'),
                            'avg_frame_rate': video_stream.get('avg_frame_rate'),
                            'nb_frames': video_stream.get('nb_frames')
                        })
                        
                        # Calculate additional properties
                        width = video_metadata.get('width', 0)
                        height = video_metadata.get('height', 0)
                        if width and height:
                            video_metadata['aspect_ratio'] = width / height
                            video_metadata['resolution'] = f"{width}x{height}"
                    
                    # Audio stream information
                    audio_streams = [s for s in probe.get('streams', []) if s.get('codec_type') == 'audio']
                    if audio_streams:
                        audio_stream = audio_streams[0]
                        video_metadata['audio'] = {
                            'codec_name': audio_stream.get('codec_name'),
                            'sample_rate': int(audio_stream.get('sample_rate', 0)),
                            'channels': int(audio_stream.get('channels', 0)),
                            'channel_layout': audio_stream.get('channel_layout'),
                            'bit_rate': int(audio_stream.get('bit_rate', 0))
                        }
                    
                except Exception as e:
                    logger.debug(f"ffmpeg probe failed: {e}")
            
            # Use OpenCV for additional video analysis
            try:
                if isinstance(content_source, (str, Path)):
                    cap = cv2.VideoCapture(str(content_source))
                    
                    if cap.isOpened():
                        # Get video properties
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        
                        video_metadata.update({
                            'opencv_fps': fps,
                            'opencv_frame_count': frame_count,
                            'opencv_width': width,
                            'opencv_height': height,
                            'opencv_duration': frame_count / fps if fps > 0 else 0
                        })
                        
                        # Sample some frames for analysis
                        frame_samples = []
                        for i in range(0, frame_count, max(1, frame_count // 5)):  # Sample 5 frames
                            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                            ret, frame = cap.read()
                            if ret:
                                # Calculate frame statistics
                                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                brightness = np.mean(gray)
                                contrast = np.std(gray)
                                frame_samples.append({
                                    'frame_number': i,
                                    'brightness': float(brightness),
                                    'contrast': float(contrast)
                                })
                        
                        if frame_samples:
                            video_metadata['frame_analysis'] = {
                                'sample_count': len(frame_samples),
                                'avg_brightness': np.mean([f['brightness'] for f in frame_samples]),
                                'avg_contrast': np.mean([f['contrast'] for f in frame_samples]),
                                'samples': frame_samples
                            }
                    
                    cap.release()
                    
            except Exception as e:
                logger.debug(f"OpenCV analysis failed: {e}")
            
            metadata.video_metadata = video_metadata
            
        except Exception as e:
            metadata.extraction_errors.append(f"Video metadata extraction error: {str(e)}")
            logger.warning(f"Video metadata extraction failed: {e}")
    
    async def _extract_document_metadata(
        self,
        metadata: ContentMetadata,
        content_source: Union[str, bytes, Path]
    ) -> None:
        """Extract document-specific metadata."""



        try:
            document_metadata = {}
            
            if isinstance(content_source, (str, Path)):
                path = Path(content_source)
                
                if path.suffix.lower() == '.pdf':
                    # PDF metadata extraction
                    try:
                        import PyPDF2
                        with open(path, 'rb') as file:
                            pdf_reader = PyPDF2.PdfFileReader(file)
                            pdf_info = pdf_reader.getDocumentInfo()
                            
                            if pdf_info:
                                metadata.title = pdf_info.get('/Title')
                                metadata.creator = pdf_info.get('/Creator')
                                metadata.author = pdf_info.get('/Author')
                                metadata.subject = pdf_info.get('/Subject')
                                
                                document_metadata.update({
                                    'producer': pdf_info.get('/Producer'),
                                    'creation_date': pdf_info.get('/CreationDate'),
                                    'modification_date': pdf_info.get('/ModDate'),
                                    'page_count': pdf_reader.getNumPages(),
                                    'encrypted': pdf_reader.isEncrypted
                                })
                    except Exception as e:
                        logger.debug(f"PDF metadata extraction failed: {e}")
                
                elif path.suffix.lower() in ['.txt', '.md']:
                    # Text file analysis
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                            
                            document_metadata.update({
                                'character_count': len(content),
                                'word_count': len(content.split()),
                                'line_count': len(content.splitlines()),
                                'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
                                'language': self._detect_language(content)
                            })
                            
                            # Extract first lines as potential title
                            lines = content.splitlines()
                            if lines:
                                potential_title = lines[0].strip()
                                if len(potential_title) < 100:
                                    metadata.title = potential_title
                    
                    except Exception as e:
                        logger.debug(f"Text file analysis failed: {e}")
            
            metadata.document_metadata = document_metadata
            
        except Exception as e:
            metadata.extraction_errors.append(f"Document metadata extraction error: {str(e)}")
            logger.warning(f"Document metadata extraction failed: {e}")
    
    async def _extract_web_metadata(
        self,
        metadata: ContentMetadata,
        content_source: str
    ) -> None:
        """Extract web page metadata."""



        try:
            web_metadata = {}
            
            # Fetch web page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(content_source, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic metadata
            metadata.title = soup.title.string.strip() if soup.title else None
            
            # Meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                content = meta.get('content')
                if name and content:
                    meta_tags[name] = content
            
            # Extract specific meta information
            metadata.description = meta_tags.get('description')
            metadata.keywords = [k.strip() for k in meta_tags.get('keywords', '').split(',') if k.strip()]
            metadata.author = meta_tags.get('author')
            metadata.language = meta_tags.get('language') or soup.html.get('lang') if soup.html else None
            
            # Open Graph metadata
            og_data = {}
            for key, value in meta_tags.items():
                if key.startswith('og:'):
                    og_data[key] = value
            
            # Twitter Card metadata
            twitter_data = {}
            for key, value in meta_tags.items():
                if key.startswith('twitter:'):
                    twitter_data[key] = value
            
            # JSON-LD structured data
            json_ld_data = []
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    json_ld_data.append(json.loads(script.string))
                except:
                    pass
            
            web_metadata.update({
                'url': content_source,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type'),
                'content_length': len(response.content),
                'meta_tags': meta_tags,
                'open_graph': og_data,
                'twitter_card': twitter_data,
                'json_ld': json_ld_data,
                'links_count': len(soup.find_all('a')),
                'images_count': len(soup.find_all('img')),
                'has_ssl': content_source.startswith('https://'),
                'domain': urlparse(content_source).netloc
            })
            
            metadata.web_metadata = web_metadata
            
        except Exception as e:
            metadata.extraction_errors.append(f"Web metadata extraction error: {str(e)}")
            logger.warning(f"Web metadata extraction failed: {e}")
    
    async def _extract_social_metadata(
        self,
        metadata: ContentMetadata,
        content_source: str
    ) -> None:
        """Extract social media post metadata."""



        try:
            social_metadata = {}
            parsed_url = urlparse(content_source)
            platform = None
            
            # Determine platform
            domain = parsed_url.netloc.lower()
            if 'twitter.com' in domain or 'x.com' in domain:
                platform = 'twitter'
            elif 'instagram.com' in domain:
                platform = 'instagram'
            elif 'facebook.com' in domain:
                platform = 'facebook'
            elif 'tiktok.com' in domain:
                platform = 'tiktok'
            elif 'youtube.com' in domain:
                platform = 'youtube'
            
            metadata.source_platform = platform.title() if platform else 'Unknown'
            
            # Extract URL parameters and path information
            path_parts = parsed_url.path.strip('/').split('/')
            query_params = parse_qs(parsed_url.query)
            
            social_metadata.update({
                'platform': platform,
                'url': content_source,
                'domain': parsed_url.netloc,
                'path_parts': path_parts,
                'query_params': query_params
            })
            
            # Platform-specific extraction
            if platform == 'twitter':
                # Twitter URL structure: twitter.com/username/status/tweet_id
                if len(path_parts) >= 3 and path_parts[1] == 'status':
                    social_metadata.update({
                        'username': path_parts[0],
                        'tweet_id': path_parts[2],
                        'post_type': 'tweet'
                    })
            
            elif platform == 'instagram':
                # Instagram URL structure: instagram.com/p/post_id or instagram.com/username
                if len(path_parts) >= 2 and path_parts[0] == 'p':
                    social_metadata.update({
                        'post_id': path_parts[1],
                        'post_type': 'instagram_post'
                    })
                elif len(path_parts) >= 1:
                    social_metadata.update({
                        'username': path_parts[0],
                        'post_type': 'instagram_profile'
                    })
            
            elif platform == 'youtube':
                # YouTube URL structure: youtube.com/watch?v=video_id
                if 'v' in query_params:
                    social_metadata.update({
                        'video_id': query_params['v'][0],
                        'post_type': 'youtube_video'
                    })
            
            # Try to fetch basic page metadata
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(content_source, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract title and description
                    if soup.title:
                        metadata.title = soup.title.string.strip()
                    
                    description_meta = soup.find('meta', attrs={'name': 'description'})
                    if description_meta:
                        metadata.description = description_meta.get('content')
                    
                    social_metadata['page_title'] = metadata.title
                    social_metadata['page_description'] = metadata.description
                    
            except Exception as e:
                logger.debug(f"Social page metadata extraction failed: {e}")
            
            metadata.web_metadata = social_metadata
            
        except Exception as e:
            metadata.extraction_errors.append(f"Social metadata extraction error: {str(e)}")
            logger.warning(f"Social metadata extraction failed: {e}")
    
    async def _enhance_metadata(
        self,
        metadata: ContentMetadata,
        strategy: ExtractionStrategy
    ) -> None:
        """Enhance metadata with additional information and external APIs."""



        try:
            if strategy == ExtractionStrategy.DEEP_ANALYSIS and self.enable_external_apis:
                # Placeholder for external API enhancements
                # This would include reverse image search, content recognition, etc.
                pass
            
            # Language detection for text content
            if not metadata.language and metadata.title:
                metadata.language = self._detect_language(metadata.title)
            
            # Generate additional keywords from title and description
            if metadata.title or metadata.description:
                text_content = f"{metadata.title or ''} {metadata.description or ''}"
                additional_keywords = self._extract_keywords(text_content)
                metadata.keywords.extend([k for k in additional_keywords if k not in metadata.keywords])
            
            # Infer content category
            if metadata.keywords or metadata.tags:
                all_terms = metadata.keywords + metadata.tags
                metadata.custom_fields['inferred_category'] = self._infer_content_category(all_terms)
            
        except Exception as e:
            metadata.extraction_errors.append(f"Metadata enhancement error: {str(e)}")
            logger.warning(f"Metadata enhancement failed: {e}")
    
    async def _validate_metadata(self, metadata: ContentMetadata) -> None:
        """Validate extracted metadata for consistency and completeness."""



        try:
            validation_errors = []
            
            # Check required fields
            if not metadata.content_id:
                validation_errors.append("Missing content_id")
            
            # Validate dates
            current_time = datetime.now()
            if metadata.created_date and metadata.created_date > current_time:
                validation_errors.append("Creation date is in the future")
            
            if metadata.modified_date and metadata.created_date:
                if metadata.modified_date < metadata.created_date:
                    validation_errors.append("Modified date is before creation date")
            
            # Validate file size
            if metadata.file_size is not None and metadata.file_size < 0:
                validation_errors.append("Invalid file size")
            
            # Validate checksums
            if metadata.checksum_md5 and len(metadata.checksum_md5) != 32:
                validation_errors.append("Invalid MD5 checksum format")
            
            if metadata.checksum_sha256 and len(metadata.checksum_sha256) != 64:
                validation_errors.append("Invalid SHA256 checksum format")
            
            # Validate coordinates
            if metadata.coordinates:
                lat, lon = metadata.coordinates
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    validation_errors.append("Invalid GPS coordinates")
            
            # Set validation status
            if validation_errors:
                metadata.validation_status = "failed"
                metadata.extraction_errors.extend(validation_errors)
            else:
                metadata.validation_status = "passed"
            
        except Exception as e:
            metadata.validation_status = "error"
            metadata.extraction_errors.append(f"Validation error: {str(e)}")
    
    async def _assess_metadata_quality(self, metadata: ContentMetadata) -> None:
        """Assess the quality and completeness of extracted metadata."""



        try:
            # Count non-empty fields
            total_fields = 0
            filled_fields = 0
            
            for field_name, field_value in metadata.__dict__.items():
                if field_name in ['extraction_errors', 'custom_fields']:
                    continue
                
                total_fields += 1
                if field_value is not None and field_value != [] and field_value != {}:
                    filled_fields += 1
            
            # Calculate completeness score
            metadata.completeness_score = filled_fields / total_fields if total_fields > 0 else 0
            
            # Calculate quality score based on various factors
            quality_factors = []
            
            # Completeness factor
            quality_factors.append(metadata.completeness_score)
            
            # Validation factor
            validation_factor = 1.0 if metadata.validation_status == "passed" else 0.5
            quality_factors.append(validation_factor)
            
            # Error factor
            error_factor = max(0, 1.0 - len(metadata.extraction_errors) * 0.1)
            quality_factors.append(error_factor)
            
            # Format-specific quality
            format_quality = self._assess_format_specific_quality(metadata)
            quality_factors.append(format_quality)
            
            metadata.quality_score = np.mean(quality_factors)
            
            # Reliability score (based on extraction method and consistency)
            reliability_factors = [
                0.9 if metadata.extraction_strategy == ExtractionStrategy.COMPREHENSIVE else 0.7,
                0.8 if metadata.validation_status == "passed" else 0.4,
                max(0.3, 1.0 - len(metadata.extraction_errors) * 0.15)
            ]
            
            metadata.reliability_score = np.mean(reliability_factors)
            
        except Exception as e:
            metadata.extraction_errors.append(f"Quality assessment error: {str(e)}")
            metadata.quality_score = 0.5
            metadata.reliability_score = 0.5
    
    def _assess_format_specific_quality(self, metadata: ContentMetadata) -> float:
        """Assess quality specific to content format."""
        if metadata.format_type == ContentFormat.IMAGE and metadata.image_metadata:
            # Image quality factors
            factors = []
            img_meta = metadata.image_metadata
            
            if 'width' in img_meta and 'height' in img_meta:
                factors.append(0.8)  # Has dimensions
            if 'exif' in img_meta:
                factors.append(0.9)  # Has EXIF data
            if 'dominant_colors' in img_meta:
                factors.append(0.7)  # Has color analysis
            
            return np.mean(factors) if factors else 0.5
        
        elif metadata.format_type == ContentFormat.AUDIO and metadata.audio_metadata:
            # Audio quality factors
            factors = []
            audio_meta = metadata.audio_metadata
            
            if any(key in audio_meta for key in ['duration', 'librosa_duration']):
                factors.append(0.8)
            if 'mfcc_mean' in audio_meta:
                factors.append(0.9)
            if 'tempo' in audio_meta:
                factors.append(0.7)
            
            return np.mean(factors) if factors else 0.5
        
        elif metadata.format_type == ContentFormat.VIDEO and metadata.video_metadata:
            # Video quality factors
            factors = []
            video_meta = metadata.video_metadata
            
            if 'width' in video_meta and 'height' in video_meta:
                factors.append(0.8)
            if 'duration' in video_meta:
                factors.append(0.8)
            if 'codec_name' in video_meta:
                factors.append(0.7)
            if 'frame_analysis' in video_meta:
                factors.append(0.9)
            
            return np.mean(factors) if factors else 0.5
        
        return 0.6  # Default for other formats
    
    def _generate_cache_key(
        self,
        content_id: str,
        content_source: Union[str, bytes, Path],
        strategy: ExtractionStrategy
    ) -> str:
        """Generate cache key for metadata."""
        if isinstance(content_source, bytes):
            source_hash = hashlib.md5(content_source).hexdigest()
        else:
            source_hash = hashlib.md5(str(content_source).encode()).hexdigest()
        
        return f"{content_id}_{source_hash}_{strategy.value}"
    
    def _parse_gps_coordinates(self, gps_info: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Parse GPS coordinates from EXIF data."""



        try:
            lat_ref = gps_info.get(1)  # GPSLatitudeRef
            lat = gps_info.get(2)      # GPSLatitude
            lon_ref = gps_info.get(3)  # GPSLongitudeRef
            lon = gps_info.get(4)      # GPSLongitude
            
            if not all([lat_ref, lat, lon_ref, lon]):
                return None, None
            
            # Convert to decimal degrees
            def convert_to_degrees(value):
                d, m, s = value
                return d + (m / 60.0) + (s / 3600.0)
            
            latitude = convert_to_degrees(lat)
            longitude = convert_to_degrees(lon)
            
            # Apply direction
            if lat_ref == 'S':
                latitude = -latitude
            if lon_ref == 'W':
                longitude = -longitude
            
            return latitude, longitude
            
        except:
            return None, None
    
    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_string:
            return None
        
        # Try common date formats
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y:%m:%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y:%m:%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except:
                continue
        
        return None
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Detect language of text content."""
        # Simplified language detection
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        french_words = {'le', 'la', 'les', 'et', 'ou', 'mais', 'dans', 'sur', 'à', 'pour', 'de', 'avec'}
        german_words = {'der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'zu', 'für', 'von', 'mit'}
        
        words = set(text.lower().split())
        
        en_score = len(words & english_words)
        fr_score = len(words & french_words)
        de_score = len(words & german_words)
        
        if en_score >= fr_score and en_score >= de_score:
            return "en"
        elif fr_score >= de_score:
            return "fr"
        else:
            return "de"
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text content."""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'}
        filtered_words = [w for w in words if w not in stop_words]
        
        # Count word frequency
        from collections import Counter
        word_counts = Counter(filtered_words)
        
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def _infer_content_category(self, terms: List[str]) -> str:
        """Infer content category from keywords and tags."""
        categories = {
            'music': ['music', 'song', 'album', 'artist', 'band', 'audio', 'sound'],
            'photography': ['photo', 'photography', 'image', 'picture', 'camera', 'lens'],
            'video': ['video', 'film', 'movie', 'cinema', 'documentary', 'vlog'],
            'art': ['art', 'painting', 'drawing', 'design', 'creative', 'artwork'],
            'technology': ['tech', 'technology', 'software', 'hardware', 'computer', 'digital'],
            'business': ['business', 'company', 'corporate', 'marketing', 'finance', 'startup'],
            'education': ['education', 'learning', 'tutorial', 'course', 'teaching', 'academic'],
            'entertainment': ['entertainment', 'fun', 'game', 'comedy', 'humor', 'meme']
        }
        
        term_lower = [t.lower() for t in terms]
        scores = {}
        
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if any(keyword in term for term in term_lower))
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return 'general'
    
    async def batch_extract(
        self,
        content_batch: List[Tuple[str, Union[str, bytes, Path], Optional[ExtractionStrategy], Optional[ContentFormat]]]
    ) -> List[ContentMetadata]:
        """Extract metadata from multiple content items in batch."""
        tasks = []
        
        for content_id, content_source, strategy, content_format in content_batch:
            task = asyncio.create_task(
                self.extract_metadata(content_id, content_source, strategy, content_format)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        valid_results = [r for r in results if isinstance(r, ContentMetadata)]
        
        logger.info(f"Batch extracted metadata for {len(valid_results)} out of {len(content_batch)} items")
        return valid_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get extraction statistics and performance metrics."""
        avg_extraction_time = np.mean(self.extraction_times) if self.extraction_times else 0
        cache_hit_rate = self.cache_hits / max(1, self.extraction_count)
        
        return {
            "total_extractions": self.extraction_count,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": cache_hit_rate,
            "average_extraction_time": avg_extraction_time,
            "format_distribution": self.format_counts,
            "cache_size": len(self.metadata_cache),
            "extraction_time_percentiles": {
                "p50": np.percentile(self.extraction_times, 50) if self.extraction_times else 0,
                "p90": np.percentile(self.extraction_times, 90) if self.extraction_times else 0,
                "p99": np.percentile(self.extraction_times, 99) if self.extraction_times else 0
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and clear caches."""
        self.metadata_cache.clear()
        self.extraction_times.clear()
        self.format_counts.clear()
        
        logger.info("MetadataExtractor cleanup completed")
