"""
IA Influencer Agent - Content Metadata Management
===============================================

Advanced metadata extraction and management system for multi-modal content analysis.
Provides comprehensive content characterization and metadata enrichment capabilities.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import hashlib
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import base64

# Optional imports for enhanced metadata extraction
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import mutagen
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    UNKNOWN = "unknown"

class QualityLevel(Enum):
    """Content quality assessment levels"""
    ULTRA_LOW = "ultra_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA_HIGH = "ultra_high"
    LOSSLESS = "lossless"

@dataclass
class GeolocationData:
    """Geolocation information"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: Optional[datetime] = None
    source: Optional[str] = None  # GPS, EXIF, IP, etc.

@dataclass
class TechnicalMetadata:
    """Technical metadata for content"""
    # File information
    file_size: int = 0
    file_format: Optional[str] = None
    mime_type: Optional[str] = None
    encoding: Optional[str] = None
    
    # Quality metrics
    quality_level: QualityLevel = QualityLevel.MEDIUM
    compression_ratio: Optional[float] = None
    bit_depth: Optional[int] = None
    
    # Checksums and hashes
    md5_hash: Optional[str] = None
    sha256_hash: Optional[str] = None
    crc32_checksum: Optional[str] = None
    
    # Creation information
    created_timestamp: Optional[datetime] = None
    modified_timestamp: Optional[datetime] = None
    accessed_timestamp: Optional[datetime] = None

@dataclass
class AudioMetadata:
    """Audio-specific metadata"""
    # Basic properties
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bit_rate: Optional[int] = None
    bits_per_sample: Optional[int] = None
    
    # Audio format details
    codec: Optional[str] = None
    format_profile: Optional[str] = None
    format_settings: Optional[str] = None
    
    # Music metadata (ID3 tags)
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track_number: Optional[int] = None
    composer: Optional[str] = None
    
    # Advanced audio analysis
    loudness_lufs: Optional[float] = None
    dynamic_range: Optional[float] = None
    peak_level: Optional[float] = None
    spectral_centroid: Optional[float] = None
    zero_crossing_rate: Optional[float] = None
    tempo_bpm: Optional[float] = None
    
    # Audio fingerprinting results
    audio_fingerprint: Optional[str] = None
    chromagram_features: Optional[List[float]] = None
    mfcc_features: Optional[List[float]] = None

@dataclass
class VideoMetadata:
    """Video-specific metadata"""
    # Basic properties
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[str] = None
    frame_rate: Optional[float] = None
    total_frames: Optional[int] = None
    
    # Video format details
    codec: Optional[str] = None
    container: Optional[str] = None
    bit_rate: Optional[int] = None
    color_space: Optional[str] = None
    color_depth: Optional[int] = None
    
    # Video analysis
    scene_count: Optional[int] = None
    motion_intensity: Optional[float] = None
    visual_complexity: Optional[float] = None
    brightness_avg: Optional[float] = None
    contrast_avg: Optional[float] = None
    
    # Audio track (if present)
    has_audio: bool = False
    audio_tracks: List[AudioMetadata] = field(default_factory=list)
    
    # Video fingerprinting results
    video_fingerprint: Optional[str] = None
    keyframe_hashes: Optional[List[str]] = None
    color_histogram: Optional[List[float]] = None

@dataclass
class ImageMetadata:
    """Image-specific metadata"""
    # Basic properties
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[str] = None
    color_mode: Optional[str] = None
    bit_depth: Optional[int] = None
    
    # Image format details
    format: Optional[str] = None
    compression: Optional[str] = None
    dpi: Optional[Tuple[int, int]] = None
    
    # EXIF data
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[float] = None
    iso_speed: Optional[int] = None
    exposure_time: Optional[str] = None
    flash: Optional[bool] = None
    
    # Image analysis
    dominant_colors: Optional[List[Tuple[int, int, int]]] = None
    color_histogram: Optional[List[float]] = None
    brightness_avg: Optional[float] = None
    contrast_avg: Optional[float] = None
    sharpness_score: Optional[float] = None
    noise_level: Optional[float] = None
    
    # Image fingerprinting results
    perceptual_hash: Optional[str] = None
    difference_hash: Optional[str] = None
    wavelet_hash: Optional[str] = None
    feature_descriptors: Optional[List[float]] = None

@dataclass
class TextMetadata:
    """Text-specific metadata"""
    # Basic properties
    character_count: int = 0
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    line_count: int = 0
    
    # Language analysis
    detected_language: Optional[str] = None
    language_confidence: Optional[float] = None
    encoding: Optional[str] = None
    
    # Content analysis
    readability_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    emotion_scores: Optional[Dict[str, float]] = None
    topics: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    entities: Optional[List[Dict[str, Any]]] = None
    
    # Style analysis
    average_word_length: Optional[float] = None
    average_sentence_length: Optional[float] = None
    punctuation_ratio: Optional[float] = None
    uppercase_ratio: Optional[float] = None
    
    # Text fingerprinting results
    text_fingerprint: Optional[str] = None
    semantic_embedding: Optional[List[float]] = None
    ngram_signatures: Optional[Dict[str, List[str]]] = None

@dataclass
class ContentMetadata:
    """Comprehensive content metadata container"""
    # Identification
    content_id: str = ""
    source_url: Optional[str] = None
    original_filename: Optional[str] = None
    content_type: ContentType = ContentType.UNKNOWN
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: Optional[datetime] = None
    
    # Technical metadata
    technical: TechnicalMetadata = field(default_factory=TechnicalMetadata)
    
    # Content-specific metadata
    audio: Optional[AudioMetadata] = None
    video: Optional[VideoMetadata] = None
    image: Optional[ImageMetadata] = None
    text: Optional[TextMetadata] = None
    
    # Geolocation
    geolocation: Optional[GeolocationData] = None
    
    # Custom metadata
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis results
    fingerprints: Dict[str, str] = field(default_factory=dict)
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    
    # Version tracking
    version: str = "1.0.0"
    schema_version: str = "1.0.0"

class MetadataExtractor:
    """Advanced metadata extraction engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Validate optional dependencies"""
        missing_deps = []
        
        if not PIL_AVAILABLE:
            missing_deps.append("Pillow (for image metadata)")
        if not MUTAGEN_AVAILABLE:
            missing_deps.append("mutagen (for audio metadata)")
        if not CV2_AVAILABLE:
            missing_deps.append("opencv-python (for video analysis)")
        
        if missing_deps:
            self.logger.warning(f"Optional dependencies missing: {', '.join(missing_deps)}")
    
    def extract_metadata(self, 
                        file_path: Union[str, Path], 
                        content_data: Optional[bytes] = None) -> ContentMetadata:
        """Extract comprehensive metadata from content"""
        try:
            file_path = Path(file_path)
            
            # Initialize metadata container
            metadata = ContentMetadata(
                content_id=self._generate_content_id(file_path, content_data),
                original_filename=file_path.name,
                content_type=self._detect_content_type(file_path)
            )
            
            # Extract technical metadata
            metadata.technical = self._extract_technical_metadata(file_path, content_data)
            
            # Extract content-specific metadata
            if metadata.content_type == ContentType.AUDIO:
                metadata.audio = self._extract_audio_metadata(file_path)
            elif metadata.content_type == ContentType.VIDEO:
                metadata.video = self._extract_video_metadata(file_path)
            elif metadata.content_type == ContentType.IMAGE:
                metadata.image = self._extract_image_metadata(file_path)
            elif metadata.content_type == ContentType.TEXT:
                metadata.text = self._extract_text_metadata(file_path, content_data)
            
            self.logger.info(f"Metadata extracted for: {file_path.name}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract metadata: {e}")
            return ContentMetadata()
    
    def _generate_content_id(self, file_path: Path, content_data: Optional[bytes] = None) -> str:
        """Generate unique content identifier"""
        try:
            if content_data:
                content_hash = hashlib.sha256(content_data).hexdigest()
            else:
                with open(file_path, 'rb') as f:
                    content_hash = hashlib.sha256(f.read()).hexdigest()
            
            return f"{file_path.stem}_{content_hash[:16]}"
            
        except Exception:
            # Fallback to timestamp-based ID
            timestamp = datetime.now(timezone.utc).isoformat()
            return f"{file_path.stem}_{hash(timestamp) % 1000000}"
    
    def _detect_content_type(self, file_path: Path) -> ContentType:
        """Detect content type from file extension and MIME type"""
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            if mime_type:
                if mime_type.startswith('audio/'):
                    return ContentType.AUDIO
                elif mime_type.startswith('video/'):
                    return ContentType.VIDEO
                elif mime_type.startswith('image/'):
                    return ContentType.IMAGE
                elif mime_type.startswith('text/'):
                    return ContentType.TEXT
            
            # Fallback to extension-based detection
            extension = file_path.suffix.lower()
            
            audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
            video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
            text_extensions = {'.txt', '.md', '.json', '.xml', '.html', '.css', '.js'}
            
            if extension in audio_extensions:
                return ContentType.AUDIO
            elif extension in video_extensions:
                return ContentType.VIDEO
            elif extension in image_extensions:
                return ContentType.IMAGE
            elif extension in text_extensions:
                return ContentType.TEXT
            
            return ContentType.UNKNOWN
            
        except Exception:
            return ContentType.UNKNOWN
    
    def _extract_technical_metadata(self, 
                                   file_path: Path, 
                                   content_data: Optional[bytes] = None) -> TechnicalMetadata:
        """Extract technical file metadata"""
        try:
            metadata = TechnicalMetadata()
            
            # File size and timestamps
            if file_path.exists():
                stat = file_path.stat()
                metadata.file_size = stat.st_size
                metadata.created_timestamp = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
                metadata.modified_timestamp = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                metadata.accessed_timestamp = datetime.fromtimestamp(stat.st_atime, tz=timezone.utc)
            
            # MIME type
            metadata.mime_type, _ = mimetypes.guess_type(str(file_path))
            metadata.file_format = file_path.suffix.lower().lstrip('.')
            
            # Generate hashes
            if content_data:
                data = content_data
            elif file_path.exists():
                with open(file_path, 'rb') as f:
                    data = f.read()
            else:
                return metadata
            
            metadata.md5_hash = hashlib.md5(data).hexdigest()
            metadata.sha256_hash = hashlib.sha256(data).hexdigest()
            
            # CRC32 checksum
            import zlib
            metadata.crc32_checksum = hex(zlib.crc32(data))
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract technical metadata: {e}")
            return TechnicalMetadata()
    
    def _extract_audio_metadata(self, file_path: Path) -> Optional[AudioMetadata]:
        """Extract audio-specific metadata"""
        if not MUTAGEN_AVAILABLE:
            return None
        
        try:
            metadata = AudioMetadata()
            
            # Load audio file with mutagen
            audio_file = mutagen.File(str(file_path))
            if not audio_file:
                return metadata
            
            # Basic properties
            if hasattr(audio_file, 'info'):
                info = audio_file.info
                metadata.duration = getattr(info, 'length', None)
                metadata.bit_rate = getattr(info, 'bitrate', None)
                metadata.sample_rate = getattr(info, 'sample_rate', None)
                metadata.channels = getattr(info, 'channels', None)
            
            # Extract ID3 tags
            if hasattr(audio_file, 'tags') and audio_file.tags:
                tags = audio_file.tags
                
                # Try different tag formats
                metadata.title = self._extract_tag_value(tags, ['TIT2', 'TITLE', '\xa9nam'])
                metadata.artist = self._extract_tag_value(tags, ['TPE1', 'ARTIST', '\xa9ART'])
                metadata.album = self._extract_tag_value(tags, ['TALB', 'ALBUM', '\xa9alb'])
                metadata.genre = self._extract_tag_value(tags, ['TCON', 'GENRE', '\xa9gen'])
                
                # Year handling
                year_value = self._extract_tag_value(tags, ['TDRC', 'DATE', '\xa9day'])
                if year_value:
                    try:
                        metadata.year = int(str(year_value)[:4])
                    except ValueError:
                        pass
                
                # Track number
                track_value = self._extract_tag_value(tags, ['TRCK', 'TRACKNUMBER', 'trkn'])
                if track_value:
                    try:
                        metadata.track_number = int(str(track_value).split('/')[0])
                    except ValueError:
                        pass
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract audio metadata: {e}")
            return AudioMetadata()
    
    def _extract_tag_value(self, tags, tag_keys: List[str]) -> Optional[str]:
        """Extract tag value with fallback keys"""
        for key in tag_keys:
            if key in tags:
                value = tags[key]
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
        return None
    
    def _extract_video_metadata(self, file_path: Path) -> Optional[VideoMetadata]:
        """Extract video-specific metadata"""
        if not CV2_AVAILABLE:
            return None
        
        try:
            metadata = VideoMetadata()
            
            # Open video with OpenCV
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                return metadata
            
            # Basic properties
            metadata.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            metadata.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            metadata.frame_rate = cap.get(cv2.CAP_PROP_FPS)
            metadata.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if metadata.frame_rate > 0:
                metadata.duration = metadata.total_frames / metadata.frame_rate
            
            if metadata.width > 0 and metadata.height > 0:
                metadata.aspect_ratio = f"{metadata.width}:{metadata.height}"
            
            # Analyze video content (sample frames)
            frame_count = 0
            brightness_sum = 0
            
            while frame_count < 10:  # Analyze first 10 frames
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Calculate brightness
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness_sum += np.mean(gray)
                frame_count += 1
            
            if frame_count > 0:
                metadata.brightness_avg = brightness_sum / frame_count
            
            cap.release()
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract video metadata: {e}")
            return VideoMetadata()
    
    def _extract_image_metadata(self, file_path: Path) -> Optional[ImageMetadata]:
        """Extract image-specific metadata"""
        if not PIL_AVAILABLE:
            return None
        
        try:
            metadata = ImageMetadata()
            
            # Open image with PIL
            with Image.open(file_path) as img:
                # Basic properties
                metadata.width, metadata.height = img.size
                metadata.color_mode = img.mode
                metadata.format = img.format
                
                if metadata.width > 0 and metadata.height > 0:
                    metadata.aspect_ratio = f"{metadata.width}:{metadata.height}"
                
                # DPI information
                if hasattr(img, 'info') and 'dpi' in img.info:
                    metadata.dpi = img.info['dpi']
                
                # EXIF data
                if hasattr(img, '_getexif'):
                    exif_data = img._getexif()
                    if exif_data:
                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)
                            
                            if tag == "Make":
                                metadata.camera_make = str(value)
                            elif tag == "Model":
                                metadata.camera_model = str(value)
                            elif tag == "LensModel":
                                metadata.lens_model = str(value)
                            elif tag == "FocalLength":
                                metadata.focal_length = float(value) if isinstance(value, (int, float)) else None
                            elif tag == "FNumber":
                                metadata.aperture = float(value) if isinstance(value, (int, float)) else None
                            elif tag == "ISOSpeedRatings":
                                metadata.iso_speed = int(value) if isinstance(value, (int, float)) else None
                            elif tag == "ExposureTime":
                                metadata.exposure_time = str(value)
                            elif tag == "Flash":
                                metadata.flash = bool(value & 1) if isinstance(value, int) else None
                
                # Color analysis
                if img.mode == 'RGB':
                    # Convert to array for analysis
                    img_array = np.array(img)
                    metadata.brightness_avg = float(np.mean(img_array))
                    
                    # Dominant colors (simplified)
                    colors = img.getcolors(maxcolors=256*256*256)
                    if colors:
                        dominant = sorted(colors, key=lambda x: x[0], reverse=True)[:5]
                        metadata.dominant_colors = [color[1] for color in dominant]
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract image metadata: {e}")
            return ImageMetadata()
    
    def _extract_text_metadata(self, 
                              file_path: Path, 
                              content_data: Optional[bytes] = None) -> Optional[TextMetadata]:
        """Extract text-specific metadata"""
        try:
            metadata = TextMetadata()
            
            # Read text content
            if content_data:
                try:
                    text = content_data.decode('utf-8')
                except UnicodeDecodeError:
                    # Try other encodings
                    for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                        try:
                            text = content_data.decode(encoding)
                            metadata.encoding = encoding
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        return metadata
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                metadata.encoding = 'utf-8'
            
            # Basic counts
            metadata.character_count = len(text)
            metadata.word_count = len(text.split())
            metadata.sentence_count = text.count('.') + text.count('!') + text.count('?')
            metadata.paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            metadata.line_count = text.count('\n') + 1
            
            # Style analysis
            if metadata.word_count > 0:
                words = text.split()
                metadata.average_word_length = sum(len(word) for word in words) / len(words)
            
            if metadata.sentence_count > 0:
                metadata.average_sentence_length = metadata.word_count / metadata.sentence_count
            
            # Character ratios
            if metadata.character_count > 0:
                punctuation_chars = sum(1 for c in text if c in '.,!?;:')
                metadata.punctuation_ratio = punctuation_chars / metadata.character_count
                
                uppercase_chars = sum(1 for c in text if c.isupper())
                metadata.uppercase_ratio = uppercase_chars / metadata.character_count
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract text metadata: {e}")
            return TextMetadata()

class MetadataManager:
    """Advanced metadata management and storage system"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("/tmp/metadata")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.extractor = MetadataExtractor()
        self.logger = logging.getLogger(__name__)
    
    def process_content(self, 
                       file_path: Union[str, Path], 
                       content_data: Optional[bytes] = None,
                       save_metadata: bool = True) -> ContentMetadata:
        """Process content and extract comprehensive metadata"""
        try:
            file_path = Path(file_path)
            
            # Extract metadata
            metadata = self.extractor.extract_metadata(file_path, content_data)
            
            # Save metadata if requested
            if save_metadata:
                self.save_metadata(metadata)
            
            self.logger.info(f"Content processed: {metadata.content_id}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to process content: {e}")
            return ContentMetadata()
    
    def save_metadata(self, metadata: ContentMetadata) -> bool:
        """Save metadata to storage"""
        try:
            metadata_file = self.storage_path / f"{metadata.content_id}_metadata.json"
            
            # Convert to serializable format
            metadata_dict = self._metadata_to_dict(metadata)
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata_dict, f, indent=2, default=str)
            
            self.logger.debug(f"Metadata saved: {metadata_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")
            return False
    
    def load_metadata(self, content_id: str) -> Optional[ContentMetadata]:
        """Load metadata from storage"""
        try:
            metadata_file = self.storage_path / f"{content_id}_metadata.json"
            
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)
            
            return self._dict_to_metadata(metadata_dict)
            
        except Exception as e:
            self.logger.error(f"Failed to load metadata: {e}")
            return None
    
    def search_metadata(self, 
                       content_type: Optional[ContentType] = None,
                       date_range: Optional[Tuple[datetime, datetime]] = None,
                       quality_level: Optional[QualityLevel] = None) -> List[ContentMetadata]:
        """Search metadata with filters"""
        try:
            results = []
            
            for metadata_file in self.storage_path.glob("*_metadata.json"):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata_dict = json.load(f)
                    
                    metadata = self._dict_to_metadata(metadata_dict)
                    
                    # Apply filters
                    if content_type and metadata.content_type != content_type:
                        continue
                    
                    if date_range:
                        start_date, end_date = date_range
                        if not (start_date <= metadata.created_at <= end_date):
                            continue
                    
                    if quality_level and metadata.technical.quality_level != quality_level:
                        continue
                    
                    results.append(metadata)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process metadata file {metadata_file}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search metadata: {e}")
            return []
    
    def _metadata_to_dict(self, metadata: ContentMetadata) -> Dict[str, Any]:
        """Convert metadata object to dictionary"""
        from dataclasses import asdict
        return asdict(metadata)
    
    def _dict_to_metadata(self, metadata_dict: Dict[str, Any]) -> ContentMetadata:
        """Convert dictionary to metadata object"""
        # This is a simplified conversion - in production, you'd want more robust deserialization
        metadata = ContentMetadata()
        
        # Basic fields
        metadata.content_id = metadata_dict.get('content_id', '')
        metadata.source_url = metadata_dict.get('source_url')
        metadata.original_filename = metadata_dict.get('original_filename')
        
        # Content type
        content_type_str = metadata_dict.get('content_type', 'unknown')
        metadata.content_type = ContentType(content_type_str)
        
        # Add more field mappings as needed...
        
        return metadata

# Global metadata manager instance
metadata_manager = MetadataManager()

def extract_content_metadata(file_path: Union[str, Path], 
                           content_data: Optional[bytes] = None) -> ContentMetadata:
    """Extract metadata from content (convenience function)"""
    return metadata_manager.process_content(file_path, content_data)
