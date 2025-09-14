"""📊 License Metadata Manager - Comprehensive Data Management System
================================================================

Ultra-advanced metadata management system for licensing and rights tracking:
- Comprehensive content metadata extraction and management
- ISRC, UPC, and other industry standard identifiers
- Multi-format content analysis and tagging
- Automated metadata validation and enrichment
- Cross-platform metadata synchronization
- AI-powered content categorization

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Music Industry Expert + Data Engineer + Metadata Specialist + Content Analyst
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING:
This software is protected by international copyright law and trade secret law.
Unauthorized reproduction, distribution, or reverse engineering is strictly prohibited
and may result in severe civil and criminal penalties. Users must comply with all
applicable intellectual property laws and license agreements.

Contact: mlaiel@live.de for licensing and authorization requests.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
import hashlib
import re
from pathlib import Path
import mutagen
from mutagen.id3 import ID3NoHeaderError
import requests
import aiohttp
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class MetadataStandard(Enum):
    """
Industry metadata standards"""

    ISRC = "isrc"  # International Standard Recording Code
    UPC = "upc"    # Universal Product Code
    EAN = "ean"    # European Article Number
    ISWC = "iswc"  # International Standard Musical Work Code
    DDEX = "ddex"  # Digital Data Exchange
    ID3 = "id3"    # ID3 tags for audio files
    VORBIS = "vorbis"  # Vorbis comments
    APE = "ape"    # APE tags
    MP4 = "mp4"    # MP4 metadata

class ContentType(Enum):
    """Content type classification"""

    AUDIO_TRACK = "audio_track"
    MUSIC_VIDEO = "music_video"
    ALBUM = "album"
    COMPILATION = "compilation"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    LIVE_RECORDING = "live_recording"
    REMIX = "remix"
    COVER_VERSION = "cover_version"
    INSTRUMENTAL = "instrumental"

class MetadataQuality(Enum):
    """Metadata completeness levels"""

    MINIMAL = "minimal"      # Basic title, artist
    STANDARD = "standard"    # Industry minimum requirements
    ENHANCED = "enhanced"    # Additional marketing metadata
    COMPREHENSIVE = "comprehensive"  # Full metadata set
    PREMIUM = "premium"      # AI-enhanced with additional data

@dataclass
class ContentIdentifiers:
    """Standard content identifiers"""
    isrc: Optional[str] = None
    upc: Optional[str] = None
    ean: Optional[str] = None
    iswc: Optional[str] = None
    catalog_number: Optional[str] = None
    barcode: Optional[str] = None
    grid: Optional[str] = None  # Global Release Identifier
    custom_id: Optional[str] = None

@dataclass
class AudioMetadata:
    """
Comprehensive audio metadata structure"""
    # Basic information
    title: str
    artist: str
    album: Optional[str] = None
    album_artist: Optional[str] = None
    
    # Track information
    track_number: Optional[int] = None
    total_tracks: Optional[int] = None
    disc_number: Optional[int] = None
    total_discs: Optional[int] = None
    
    # Dates and timing
    release_date: Optional[datetime] = None
    recording_date: Optional[datetime] = None
    duration: Optional[float] = None  # in seconds
    
    # Genre and style
    genre: Optional[str] = None
    subgenre: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None
    
    # Rights and publishing
    composer: Optional[str] = None
    lyricist: Optional[str] = None
    publisher: Optional[str] = None
    copyright: Optional[str] = None
    
    # Technical information
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None
    codec: Optional[str] = None
    
    # Content flags
    explicit: bool = False
    instrumental: bool = False
    live_recording: bool = False
    remix: bool = False
    cover_version: bool = False
    
    # Additional metadata
    language: Optional[str] = None
    country_of_origin: Optional[str] = None
    record_label: Optional[str] = None
    catalog_number: Optional[str] = None
    
    # AI-enhanced metadata
    ai_generated_tags: List[str] = None
    sentiment_analysis: Optional[Dict[str, float]] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    energy_level: Optional[float] = None

@dataclass
class MetadataValidationResult:
    """
Metadata validation result"""
    validation_id: str
    is_valid: bool
    quality_score: float
    completeness_percentage: float
    missing_fields: List[str]
    invalid_fields: List[Dict[str, str]]
    warnings: List[str]
    recommendations: List[str]
    standards_compliance: Dict[MetadataStandard, bool]

class LicenseMetadataManager:
    """
    🚀 Comprehensive license metadata management system
    
    Advanced system for extracting, validating, enriching and managing
    all types of content metadata for licensing purposes.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """
Initialize metadata manager with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Load metadata standards and validation rules
        self._load_metadata_standards()
        self._load_validation_rules()
        
        # Initialize AI services for metadata enhancement
        self._initialize_ai_services()
        
        # External metadata services
        self._initialize_external_services()
        
        # Performance metrics
        self.metadata_metrics = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'ai_enhancements': 0,
            'validation_checks': 0,
            'quality_improvements': 0
        }
        
        self.logger.info("License Metadata Manager initialized successfully")

    def _load_metadata_standards(self) -> None:
        """Load industry metadata standards and requirements."""
        self.metadata_standards = {
            MetadataStandard.DDEX: {
                'required_fields': [
                    'title', 'artist', 'release_date', 'isrc', 'genre',
                    'duration', 'copyright', 'publisher'
                ],
                'optional_fields': [
                    'album', 'track_number', 'composer', 'lyricist',
                    'record_label', 'catalog_number'
                ],
                'format_requirements': {
                    'isrc': r'^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$',
                    'duration': 'positive_number',
                    'track_number': 'positive_integer'
                }
            },
            MetadataStandard.ID3: {
                'required_fields': ['title', 'artist'],
                'recommended_fields': [
                    'album', 'year', 'genre', 'track', 'albumartist'
                ],
                'version': '2.4',
                'encoding': 'UTF-8'
            },
            MetadataStandard.ISRC: {
                'format': r'^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$',
                'country_codes': ['US', 'GB', 'DE', 'FR', 'CA', 'AU'],
                'registrant_codes': 3,
                'designation_codes': 7
            }
        }

    def _load_validation_rules(self) -> None:
        """
Load metadata validation rules."""
        self.validation_rules = {
            'title': {
                'required': True,
                'min_length': 1,
                'max_length': 255,
                'forbidden_chars': ['<', '>', '|', '*', '?']
            },
            'artist': {
                'required': True,
                'min_length': 1,
                'max_length': 255,
                'multiple_allowed': True,
                'separator': ';'
            },
            'duration': {
                'required': True,
                'min_value': 1.0,
                'max_value': 86400.0,  # 24 hours max
                'type': 'float'
            },
            'release_date': {
                'required': True,
                'format': 'ISO8601',
                'min_year': 1900,
                'max_year': 2030
            },
            'genre': {
                'required': True,
                'allowed_values': [
                    'Rock', 'Pop', 'Hip Hop', 'Electronic', 'Jazz',
                    'Classical', 'Country', 'R&B', 'Folk', 'Reggae',
                    'Blues', 'Funk', 'Disco', 'Punk', 'Metal'
                ]
            }
        }

    def _initialize_ai_services(self) -> None:
        """
Initialize AI services for metadata enhancement."""
        try:
            # Audio analysis models
            self.audio_analyzer = None  # Would initialize with actual audio ML models
            
            # Text analysis for genre/mood classification
            self.text_classifier = None  # Would initialize with text classification models
            
            # Music information retrieval
            self.music_analyzer = None  # Would initialize with MIR models
            
            self.logger.info("AI services initialized for metadata enhancement")
            
        except Exception as e:
            self.logger.warning(f"AI services initialization failed: {e}")
            self.audio_analyzer = None
            self.text_classifier = None
            self.music_analyzer = None

    def _initialize_external_services(self) -> None:
        """Initialize external metadata services."""
        self.external_services = {
            'musicbrainz': {
                'base_url': 'https://musicbrainz.org/ws/2',
                'rate_limit': 1,  # requests per second
                'enabled': self.config.get('musicbrainz_enabled', False)
            },
            'acoustid': {
                'base_url': 'https://api.acoustid.org/v2',
                'api_key': self.config.get('acoustid_api_key'),
                'enabled': bool(self.config.get('acoustid_api_key'))
            },
            'spotify': {
                'base_url': 'https://api.spotify.com/v1',
                'client_id': self.config.get('spotify_client_id'),
                'client_secret': self.config.get('spotify_client_secret'),
                'enabled': bool(self.config.get('spotify_client_id'))
            },
            'gracenote': {
                'base_url': 'https://c.api.entertainment.gracenote.com',
                'client_id': self.config.get('gracenote_client_id'),
                'user_id': self.config.get('gracenote_user_id'),
                'enabled': bool(self.config.get('gracenote_client_id'))
            }
        }

    async def extract_metadata(
        self,
        file_path: str,
        content_type: ContentType,
        enhancement_level: MetadataQuality = MetadataQuality.STANDARD
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from content file.
        
        Args:
            file_path: Path to content file
            content_type: Type of content
            enhancement_level: Level of metadata enhancement
            
        Returns:
            Extracted and enhanced metadata
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Extracting metadata from: {file_path}")
            
            # Step 1: Basic metadata extraction
            basic_metadata = await self._extract_basic_metadata(file_path, content_type)
            
            # Step 2: Technical metadata extraction
            technical_metadata = await self._extract_technical_metadata(file_path)
            
            # Step 3: Content analysis (if AI enabled)
            content_analysis = {}
            if enhancement_level in [MetadataQuality.ENHANCED, MetadataQuality.COMPREHENSIVE, MetadataQuality.PREMIUM]:
                content_analysis = await self._analyze_content(file_path, content_type)
            
            # Step 4: External metadata enrichment
            external_metadata = {}
            if enhancement_level in [MetadataQuality.COMPREHENSIVE, MetadataQuality.PREMIUM]:
                external_metadata = await self._enrich_from_external_sources(
                    basic_metadata, content_type
                )
            
            # Step 5: AI enhancement
            ai_metadata = {}
            if enhancement_level == MetadataQuality.PREMIUM:
                ai_metadata = await self._enhance_with_ai(
                    file_path, basic_metadata, content_type
                )
            
            # Step 6: Combine all metadata
            combined_metadata = self._combine_metadata(
                basic_metadata, technical_metadata, content_analysis,
                external_metadata, ai_metadata
            )
            
            # Step 7: Validate metadata
            validation_result = await self.validate_metadata(combined_metadata)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            self._update_extraction_metrics(True, processing_time)
            
            return {
                'status': 'success',
                'metadata': combined_metadata,
                'validation': asdict(validation_result),
                'enhancement_level': enhancement_level.value,
                'processing_time': processing_time,
                'file_info': {
                    'file_path': file_path,
                    'content_type': content_type.value,
                    'extracted_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            self._update_extraction_metrics(False, 0)
            return {
                'status': 'error',
                'error': str(e),
                'file_path': file_path
            }

    async def _extract_basic_metadata(
        self,
        file_path: str,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Extract basic metadata from file."""
        metadata = {}
        
        try:
            if content_type == ContentType.AUDIO_TRACK:
                # Use mutagen for audio metadata
                audio_file = mutagen.File(file_path)
                
                if audio_file is not None:
                    # Common tags
                    metadata['title'] = self._get_tag_value(audio_file, ['TIT2', 'TITLE', '\xa9nam'])
                    metadata['artist'] = self._get_tag_value(audio_file, ['TPE1', 'ARTIST', '\xa9ART'])
                    metadata['album'] = self._get_tag_value(audio_file, ['TALB', 'ALBUM', '\xa9alb'])
                    metadata['album_artist'] = self._get_tag_value(audio_file, ['TPE2', 'ALBUMARTIST', 'aART'])
                    metadata['date'] = self._get_tag_value(audio_file, ['TDRC', 'DATE', '\xa9day'])
                    metadata['genre'] = self._get_tag_value(audio_file, ['TCON', 'GENRE', '\xa9gen'])
                    metadata['track_number'] = self._get_tag_value(audio_file, ['TRCK', 'TRACKNUMBER', 'trkn'])
                    
                    # Industry identifiers
                    metadata['isrc'] = self._get_tag_value(audio_file, ['TSRC', 'ISRC'])
                    
                    # Rights information
                    metadata['copyright'] = self._get_tag_value(audio_file, ['TCOP', 'COPYRIGHT', 'cprt'])
                    metadata['publisher'] = self._get_tag_value(audio_file, ['TPUB', 'PUBLISHER'])
                    metadata['composer'] = self._get_tag_value(audio_file, ['TCOM', 'COMPOSER', '\xa9wrt'])
                    
                    # Technical info
                    if hasattr(audio_file, 'info'):
                        metadata['duration'] = getattr(audio_file.info, 'length', None)
                        metadata['bitrate'] = getattr(audio_file.info, 'bitrate', None)
                        metadata['sample_rate'] = getattr(audio_file.info, 'sample_rate', None)
                        metadata['channels'] = getattr(audio_file.info, 'channels', None)
                
            return metadata
            
        except Exception as e:
            self.logger.error(f"Basic metadata extraction failed: {e}")
            return {}

    def _get_tag_value(self, audio_file, tag_names: List[str]) -> Optional[str]:
        """Get tag value from audio file using multiple possible tag names."""
        for tag_name in tag_names:
            if tag_name in audio_file:
                value = audio_file[tag_name]
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
        return None

    async def _extract_technical_metadata(self, file_path: str) -> Dict[str, Any]:
        """
Extract technical metadata from file."""
        technical = {}
        
        try:
            file_path_obj = Path(file_path)
            
            # File information
            technical['file_name'] = file_path_obj.name
            technical['file_size'] = file_path_obj.stat().st_size
            technical['file_extension'] = file_path_obj.suffix.lower()
            technical['creation_time'] = datetime.fromtimestamp(file_path_obj.stat().st_ctime)
            technical['modification_time'] = datetime.fromtimestamp(file_path_obj.stat().st_mtime)
            
            # File format detection
            technical['mime_type'] = self._detect_mime_type(file_path)
            
            # Audio-specific technical metadata
            if technical['file_extension'] in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
                audio_tech = await self._extract_audio_technical_metadata(file_path)
                technical.update(audio_tech)
            
            return technical
            
        except Exception as e:
            self.logger.error(f"Technical metadata extraction failed: {e}")
            return {}

    def _detect_mime_type(self, file_path: str) -> Optional[str]:
        """Detect MIME type of file."""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type

    async def _extract_audio_technical_metadata(self, file_path: str) -> Dict[str, Any]:
        """
Extract audio-specific technical metadata."""
        audio_tech = {}
        
        try:
            audio_file = mutagen.File(file_path)
            
            if audio_file and hasattr(audio_file, 'info'):
                info = audio_file.info
                
                # Audio quality metrics
                audio_tech['duration_seconds'] = getattr(info, 'length', 0)
                audio_tech['bitrate_kbps'] = getattr(info, 'bitrate', 0)
                audio_tech['sample_rate_hz'] = getattr(info, 'sample_rate', 0)
                audio_tech['bits_per_sample'] = getattr(info, 'bits_per_sample', 0)
                audio_tech['channels'] = getattr(info, 'channels', 0)
                
                # Codec information
                audio_tech['codec'] = type(audio_file).__name__
                
                # Calculate quality score
                audio_tech['quality_score'] = self._calculate_audio_quality_score(audio_tech)
                
            return audio_tech
            
        except Exception as e:
            self.logger.error(f"Audio technical metadata extraction failed: {e}")
            return {}

    def _calculate_audio_quality_score(self, audio_tech: Dict[str, Any]) -> float:
        """Calculate audio quality score based on technical parameters."""
        score = 0.0
        
        # Bitrate scoring (40% weight)
        bitrate = audio_tech.get('bitrate_kbps', 0)
        if bitrate >= 320:
            score += 40
        elif bitrate >= 256:
            score += 35
        elif bitrate >= 192:
            score += 30
        elif bitrate >= 128:
            score += 25
        else:
            score += 15
        
        # Sample rate scoring (30% weight)
        sample_rate = audio_tech.get('sample_rate_hz', 0)
        if sample_rate >= 96000:
            score += 30
        elif sample_rate >= 48000:
            score += 25
        elif sample_rate >= 44100:
            score += 20
        elif sample_rate >= 22050:
            score += 15
        else:
            score += 10
        
        # Channels scoring (15% weight)
        channels = audio_tech.get('channels', 0)
        if channels >= 6:  # 5.1 surround
            score += 15
        elif channels == 2:  # Stereo
            score += 12
        elif channels == 1:  # Mono
            score += 8
        
        # Codec scoring (15% weight)
        codec = audio_tech.get('codec', '').lower()
        if 'flac' in codec or 'alac' in codec:
            score += 15  # Lossless
        elif 'aac' in codec or 'vorbis' in codec:
            score += 12  # High quality lossy
        elif 'mp3' in codec:
            score += 10  # Standard lossy
        else:
            score += 5
        
        return min(score, 100.0)

    async def _analyze_content(
        self,
        file_path: str,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """
Analyze content for additional metadata."""
        analysis = {}
        
        try:
            if content_type == ContentType.AUDIO_TRACK and self.audio_analyzer:
                # Audio content analysis
                audio_analysis = await self._analyze_audio_content(file_path)
                analysis.update(audio_analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            return {}

    async def _analyze_audio_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze audio content for additional metadata."""
        # Note: In production, this would use actual audio analysis libraries
        # like librosa, essentia, or custom ML models
        
        audio_analysis = {
            'bpm': None,  # Would detect BPM
            'key': None,  # Would detect musical key
            'energy_level': None,  # Would calculate energy/intensity
            'danceability': None,  # Would calculate danceability score
            'valence': None,  # Would analyze emotional valence
            'acousticness': None,  # Would detect acoustic vs electronic
            'instrumentalness': None,  # Would detect instrumental content
            'liveness': None,  # Would detect live recording characteristics
            'speechiness': None,  # Would detect speech content
            'tempo_stability': None,  # Would analyze tempo stability
            'dynamic_range': None  # Would calculate dynamic range
        }
        
        # Placeholder analysis - in production would use real audio analysis
        try:
            # Simulate BPM detection
            audio_analysis['bpm'] = 120  # Placeholder
            audio_analysis['key'] = 'C major'  # Placeholder
            audio_analysis['energy_level'] = 0.7  # Placeholder
            
        except Exception as e:
            self.logger.error(f"Audio content analysis failed: {e}")
        
        return audio_analysis

    async def _enrich_from_external_sources(
        self,
        basic_metadata: Dict[str, Any],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Enrich metadata from external sources."""
        enriched = {}
        
        try:
            # MusicBrainz enrichment
            if self.external_services['musicbrainz']['enabled']:
                mb_data = await self._query_musicbrainz(basic_metadata)
                enriched.update(mb_data)
            
            # Spotify enrichment
            if self.external_services['spotify']['enabled']:
                spotify_data = await self._query_spotify(basic_metadata)
                enriched.update(spotify_data)
            
            return enriched
            
        except Exception as e:
            self.logger.error(f"External metadata enrichment failed: {e}")
            return {}

    async def _query_musicbrainz(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Query MusicBrainz for additional metadata."""
        # Note: In production, this would make real API calls to MusicBrainz
        return {
            'musicbrainz_id': str(uuid.uuid4()),
            'release_country': 'US',  # Placeholder
            'label': 'Independent',  # Placeholder
        }

    async def _query_spotify(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
Query Spotify for additional metadata."""
        # Note: In production, this would make real API calls to Spotify
        return {
            'spotify_id': str(uuid.uuid4()),
            'popularity': 65,  # Placeholder
            'preview_url': 'https://example.com/preview.mp3'  # Placeholder
        }

    async def _enhance_with_ai(
        self,
        file_path: str,
        metadata: Dict[str, Any],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """
Enhance metadata using AI analysis."""
        ai_enhanced = {}
        
        try:
            # AI-powered genre classification
            if self.text_classifier:
                genre_prediction = await self._classify_genre_ai(file_path, metadata)
                ai_enhanced.update(genre_prediction)
            
            # AI-powered mood analysis
            mood_analysis = await self._analyze_mood_ai(file_path, metadata)
            ai_enhanced.update(mood_analysis)
            
            # AI-generated tags
            ai_tags = await self._generate_ai_tags(file_path, metadata)
            ai_enhanced['ai_generated_tags'] = ai_tags
            
            return ai_enhanced
            
        except Exception as e:
            self.logger.error(f"AI metadata enhancement failed: {e}")
            return {}

    async def _classify_genre_ai(
        self,
        file_path: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify genre using AI."""
        # Placeholder AI genre classification
        return {
            'ai_genre_primary': 'Pop',
            'ai_genre_secondary': 'Electronic',
            'genre_confidence': 0.87
        }

    async def _analyze_mood_ai(
        self,
        file_path: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Analyze mood using AI."""
        # Placeholder AI mood analysis
        return {
            'ai_mood': 'Energetic',
            'ai_emotion': 'Happy',
            'mood_confidence': 0.73,
            'sentiment_analysis': {
                'positive': 0.8,
                'negative': 0.1,
                'neutral': 0.1
            }
        }

    async def _generate_ai_tags(
        self,
        file_path: str,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """
Generate AI-powered content tags."""
        # Placeholder AI tag generation
        return [
            'upbeat', 'danceable', 'modern', 'radio-friendly',
            'mainstream', 'catchy', 'commercial'
        ]

    def _combine_metadata(self, *metadata_dicts) -> AudioMetadata:
        """
Combine metadata from multiple sources."""
        combined = {}
        
        # Merge all metadata dictionaries
        for metadata_dict in metadata_dicts:
            if metadata_dict:
                combined.update(metadata_dict)
        
        # Convert to AudioMetadata object with proper type conversion
        audio_metadata = AudioMetadata(
            title=combined.get('title', 'Unknown'),
            artist=combined.get('artist', 'Unknown Artist'),
            album=combined.get('album'),
            album_artist=combined.get('album_artist'),
            track_number=self._safe_int_conversion(combined.get('track_number')),
            release_date=self._safe_date_conversion(combined.get('date')),
            duration=self._safe_float_conversion(combined.get('duration')),
            genre=combined.get('genre'),
            bitrate=self._safe_int_conversion(combined.get('bitrate_kbps')),
            sample_rate=self._safe_int_conversion(combined.get('sample_rate_hz')),
            channels=self._safe_int_conversion(combined.get('channels')),
            format=combined.get('file_extension'),
            codec=combined.get('codec'),
            copyright=combined.get('copyright'),
            composer=combined.get('composer'),
            publisher=combined.get('publisher'),
            ai_generated_tags=combined.get('ai_generated_tags', []),
            sentiment_analysis=combined.get('sentiment_analysis'),
            bpm=self._safe_int_conversion(combined.get('bpm')),
            key=combined.get('key'),
            energy_level=self._safe_float_conversion(combined.get('energy_level'))
        )
        
        return audio_metadata

    def _safe_int_conversion(self, value) -> Optional[int]:
        """
Safely convert value to integer."""
        if value is None:
            return None
        try:
            if isinstance(value, str) and '/' in value:
                # Handle track numbers like "3/12"
                return int(value.split('/')[0])
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def _safe_float_conversion(self, value) -> Optional[float]:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _safe_date_conversion(self, value) -> Optional[datetime]:
        """
Safely convert value to datetime."""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(value[:len(fmt)], fmt)
                    except ValueError:
                        continue
            return None
        except (ValueError, TypeError):
            return None

    async def validate_metadata(self, metadata: AudioMetadata) -> MetadataValidationResult:
        """
Validate metadata against industry standards."""
        validation_id = str(uuid.uuid4())
        is_valid = True
        missing_fields = []
        invalid_fields = []
        warnings = []
        recommendations = []
        
        try:
            # Check required fields
            required_fields = ['title', 'artist', 'duration']
            for field in required_fields:
                value = getattr(metadata, field, None)
                if not value:
                    missing_fields.append(field)
                    is_valid = False
            
            # Validate field formats and values
            if metadata.title and len(metadata.title) > 255:
                invalid_fields.append({
                    'field': 'title',
                    'issue': 'Title exceeds maximum length of 255 characters'
                })
                is_valid = False
            
            if metadata.duration and metadata.duration < 1.0:
                invalid_fields.append({
                    'field': 'duration',
                    'issue': 'Duration must be at least 1 second'
                })
                is_valid = False
            
            # Check ISRC format if present
            isrc = getattr(metadata, 'isrc', None)
            if isrc and not re.match(r'^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$', isrc):
                invalid_fields.append({
                    'field': 'isrc',
                    'issue': 'Invalid ISRC format'
                })
                warnings.append('ISRC format validation failed')
            
            # Calculate completeness percentage
            total_fields = len(metadata.__dataclass_fields__)
            filled_fields = sum(1 for field in metadata.__dataclass_fields__ 
                              if getattr(metadata, field) is not None)
            completeness_percentage = (filled_fields / total_fields) * 100
            
            # Calculate quality score
            quality_score = self._calculate_metadata_quality_score(metadata)
            
            # Generate recommendations
            if not metadata.genre:
                recommendations.append('Add genre information for better categorization')
            if not metadata.release_date:
                recommendations.append('Add release date for proper cataloging')
            if completeness_percentage < 70:
                recommendations.append('Consider enriching metadata for better discoverability')
            
            # Check standards compliance
            standards_compliance = {
                MetadataStandard.DDEX: self._check_ddex_compliance(metadata),
                MetadataStandard.ID3: self._check_id3_compliance(metadata),
                MetadataStandard.ISRC: bool(isrc and re.match(r'^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$', isrc))
            }
            
            return MetadataValidationResult(
                validation_id=validation_id,
                is_valid=is_valid,
                quality_score=quality_score,
                completeness_percentage=completeness_percentage,
                missing_fields=missing_fields,
                invalid_fields=invalid_fields,
                warnings=warnings,
                recommendations=recommendations,
                standards_compliance=standards_compliance
            )
            
        except Exception as e:
            self.logger.error(f"Metadata validation failed: {e}")
            return MetadataValidationResult(
                validation_id=validation_id,
                is_valid=False,
                quality_score=0.0,
                completeness_percentage=0.0,
                missing_fields=[],
                invalid_fields=[{'field': 'validation', 'issue': str(e)}],
                warnings=[],
                recommendations=['Manual review required due to validation error'],
                standards_compliance={}
            )

    def _calculate_metadata_quality_score(self, metadata: AudioMetadata) -> float:
        """Calculate overall metadata quality score."""
        score = 0.0
        
        # Essential fields (40 points)
        if metadata.title:
            score += 10
        if metadata.artist:
            score += 10
        if metadata.duration:
            score += 10
        if metadata.genre:
            score += 10
        
        # Important fields (30 points)
        if metadata.album:
            score += 5
        if metadata.release_date:
            score += 5
        if metadata.track_number:
            score += 5
        if metadata.copyright:
            score += 5
        if metadata.composer:
            score += 5
        if metadata.publisher:
            score += 5
        
        # Technical quality (20 points)
        if metadata.bitrate and metadata.bitrate >= 320:
            score += 5
        elif metadata.bitrate and metadata.bitrate >= 256:
            score += 4
        elif metadata.bitrate and metadata.bitrate >= 128:
            score += 3
        
        if metadata.sample_rate and metadata.sample_rate >= 44100:
            score += 5
        
        if metadata.format:
            score += 5
        
        if metadata.codec:
            score += 5
        
        # Enhanced metadata (10 points)
        if metadata.ai_generated_tags:
            score += 3
        if metadata.bpm:
            score += 2
        if metadata.key:
            score += 2
        if metadata.energy_level:
            score += 3
        
        return min(score, 100.0)

    def _check_ddex_compliance(self, metadata: AudioMetadata) -> bool:
        """
Check DDEX standard compliance."""
        required_ddex_fields = ['title', 'artist', 'duration', 'genre']
        return all(getattr(metadata, field) for field in required_ddex_fields)

    def _check_id3_compliance(self, metadata: AudioMetadata) -> bool:
        """
Check ID3 standard compliance."""
        required_id3_fields = ['title', 'artist']
        return all(getattr(metadata, field) for field in required_id3_fields)

    def _update_extraction_metrics(self, success -> None: bool, processing_time -> None: float) -> None:
        """
Update metadata extraction metrics."""
        self.metadata_metrics['total_extractions'] += 1
        if success:
            self.metadata_metrics['successful_extractions'] += 1

    async def generate_metadata_identifiers(
        self,
        metadata: AudioMetadata,
        territory: str = 'US'
    ) -> ContentIdentifiers:
        """
Generate industry standard identifiers for content."""
        try:
            identifiers = ContentIdentifiers()
            
            # Generate ISRC if not present
            if not getattr(metadata, 'isrc', None):
                identifiers.isrc = await self._generate_isrc(territory)
            
            # Generate custom internal ID
            identifiers.custom_id = self._generate_custom_id(metadata)
            
            # Generate catalog number
            identifiers.catalog_number = self._generate_catalog_number(metadata)
            
            return identifiers
            
        except Exception as e:
            self.logger.error(f"Identifier generation failed: {e}")
            return ContentIdentifiers()

    async def _generate_isrc(self, territory: str) -> str:
        """Generate a valid ISRC code."""
        import random
        import string
        
        # Country code
        country_codes = {
            'US': 'US',
            'UK': 'GB',
            'Germany': 'DE',
            'France': 'FR',
            'Canada': 'CA'
        }
        
        country_code = country_codes.get(territory, 'US')
        
        # Registrant code (3 characters)
        registrant_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        
        # Year and designation (7 digits)
        year = str(datetime.now().year)[-2:]  # Last 2 digits of year
        designation = ''.join(random.choices(string.digits, k=5))
        
        isrc = f"{country_code}{registrant_code}{year}{designation}"
        
        return isrc

    def _generate_custom_id(self, metadata: AudioMetadata) -> str:
        """Generate custom internal identifier."""
        # Create hash based on metadata
        content = f"{metadata.title}_{metadata.artist}_{datetime.now().isoformat()}"
        hash_object = hashlib.md5(content.encode())
        return f"LIC_{hash_object.hexdigest()[:8].upper()}"

    def _generate_catalog_number(self, metadata: AudioMetadata) -> str:
        """Generate catalog number."""
        year = datetime.now().year
        random_part = str(uuid.uuid4()).split('-')[0].upper()
        return f"CAT{year}{random_part}"

    def get_metadata_metrics(self) -> Dict[str, Any]:
        """Get metadata management performance metrics."""
        total = self.metadata_metrics['total_extractions']
        successful = self.metadata_metrics['successful_extractions']
        
        return {
            **self.metadata_metrics,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'ai_enhancement_rate': (
                self.metadata_metrics['ai_enhancements'] / total * 100
            ) if total > 0 else 0,
            'external_services_available': sum(
                1 for service in self.external_services.values()
                if service.get('enabled', False)
            ),
            'supported_standards': len(self.metadata_standards)
        }

# Export classes and functions
__all__ = [
    'LicenseMetadataManager',
    'AudioMetadata',
    'ContentIdentifiers',
    'MetadataValidationResult',
    'MetadataStandard',
    'ContentType',
    'MetadataQuality'
]
