"""
Metadata Management System - Professional Audio Metadata Handling

Advanced metadata extraction, preservation, and injection system for audio format conversion.
Provides comprehensive metadata handling with support for all major tagging formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import json
import hashlib

# Audio metadata libraries
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TPE2, TRCK, TPE3, TXXX, APIC
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from mutagen.apev2 import APEv2

# Image processing for cover art
from PIL import Image
import io
import base64

from ..core.config import AudioConfig
from ..core.exceptions import MetadataError
from .models import MetadataProfile
from .config import MetadataConfig

logger = logging.getLogger(__name__)


@dataclass
class AudioMetadata:
    """Comprehensive audio metadata structure"""
    # Basic metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    album_artist: Optional[str] = None
    date: Optional[str] = None
    year: Optional[int] = None
    track_number: Optional[int] = None
    total_tracks: Optional[int] = None
    disc_number: Optional[int] = None
    total_discs: Optional[int] = None
    genre: Optional[str] = None
    
    # Extended metadata
    composer: Optional[str] = None
    conductor: Optional[str] = None
    performer: Optional[str] = None
    lyricist: Optional[str] = None
    publisher: Optional[str] = None
    isrc: Optional[str] = None
    barcode: Optional[str] = None
    catalog_number: Optional[str] = None
    
    # Technical metadata
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    duration: Optional[float] = None
    format: Optional[str] = None
    codec: Optional[str] = None
    bit_depth: Optional[int] = None
    
    # Rights and protection
    copyright: Optional[str] = None
    license: Optional[str] = None
    rights_holder: Optional[str] = None
    usage_rights: Optional[str] = None
    
    # Cover art
    cover_art: Optional[bytes] = None
    cover_art_type: Optional[str] = None
    cover_art_mime: Optional[str] = None
    
    # Custom fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Processing metadata
    processed_by: str = "IA Influencer Agent"
    processing_date: str = field(default_factory=lambda: datetime.now().isoformat())
    original_format: Optional[str] = None
    conversion_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Fingerprinting and protection
    audio_fingerprint: Optional[str] = None
    content_hash: Optional[str] = None
    protection_level: str = "standard"


class MetadataManager:
    """
    Professional Audio Metadata Manager
    
    Advanced metadata handling system providing:
    - Universal metadata extraction from all major formats
    - Intelligent metadata preservation during conversion
    - Comprehensive metadata injection and validation
    - Content protection and rights management integration
    """
    
    def __init__(self, config: Optional[MetadataConfig] = None):
        """Initialize metadata manager"""
        self.config = config or MetadataConfig()
        self.supported_formats = self._init_supported_formats()
        self.tag_mappings = self._init_tag_mappings()
        
    def _init_supported_formats(self) -> Dict[str, type]:
        """Initialize supported format handlers"""



        return {
            '.mp3': ID3,
            '.flac': FLAC,
            '.m4a': MP4,
            '.mp4': MP4,
            '.ogg': OggVorbis,
            '.oga': OggVorbis,
            '.ape': APEv2
        }
    
    def _init_tag_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize tag mapping for different formats"""



        return {
            'id3v2': {
                'title': 'TIT2',
                'artist': 'TPE1',
                'album': 'TALB',
                'date': 'TDRC',
                'genre': 'TCON',
                'album_artist': 'TPE2',
                'track': 'TRCK',
                'composer': 'TCOM',
                'conductor': 'TPE3',
                'copyright': 'TCOP',
                'isrc': 'TSRC',
                'publisher': 'TPUB'
            },
            'vorbis': {
                'title': 'TITLE',
                'artist': 'ARTIST',
                'album': 'ALBUM',
                'date': 'DATE',
                'genre': 'GENRE',
                'album_artist': 'ALBUMARTIST',
                'track': 'TRACKNUMBER',
                'total_tracks': 'TRACKTOTAL',
                'disc': 'DISCNUMBER',
                'total_discs': 'DISCTOTAL',
                'composer': 'COMPOSER',
                'conductor': 'CONDUCTOR',
                'copyright': 'COPYRIGHT',
                'isrc': 'ISRC',
                'publisher': 'PUBLISHER'
            },
            'mp4': {
                'title': '\xa9nam',
                'artist': '\xa9ART',
                'album': '\xa9alb',
                'date': '\xa9day',
                'genre': '\xa9gen',
                'album_artist': 'aART',
                'track': 'trkn',
                'disc': 'disk',
                'composer': '\xa9wrt',
                'copyright': 'cprt',
                'isrc': '----:com.apple.iTunes:ISRC',
                'publisher': '----:com.apple.iTunes:PUBLISHER'
            }
        }
    
    async def extract_metadata(self, file_path: Path) -> AudioMetadata:
        """
        Extract comprehensive metadata from audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioMetadata object with extracted information
        """



        try:
            metadata = AudioMetadata()
            
            # Load file with mutagen
            audio_file = mutagen.File(str(file_path))
            if not audio_file:
                raise MetadataError(f"Could not read metadata from {file_path}")
            
            # Extract basic metadata
            await self._extract_basic_metadata(audio_file, metadata)
            
            # Extract technical metadata
            await self._extract_technical_metadata(audio_file, metadata, file_path)
            
            # Extract cover art
            await self._extract_cover_art(audio_file, metadata)
            
            # Extract custom fields
            await self._extract_custom_fields(audio_file, metadata)
            
            # Generate content fingerprints
            await self._generate_fingerprints(file_path, metadata)
            
            # Add processing metadata
            metadata.original_format = file_path.suffix[1:].lower()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed for {file_path}: {e}")
            # Return minimal metadata
            return AudioMetadata(
                original_format=file_path.suffix[1:].lower() if file_path.suffix else None
            )
    
    async def inject_metadata(self, 
                            file_path: Path, 
                            metadata: AudioMetadata,
                            preserve_existing: bool = True) -> bool:
        """
        Inject metadata into audio file
        
        Args:
            file_path: Path to target audio file
            metadata: Metadata to inject
            preserve_existing: Whether to preserve existing metadata
            
        Returns:
            Success status
        """



        try:
            # Load existing file
            audio_file = mutagen.File(str(file_path))
            if not audio_file:
                raise MetadataError(f"Could not open file for metadata injection: {file_path}")
            
            # Get format-specific handler
            file_format = self._detect_format(file_path, audio_file)
            
            # Inject metadata based on format
            if file_format == 'id3v2':
                await self._inject_id3v2_metadata(audio_file, metadata, preserve_existing)
            elif file_format == 'vorbis':
                await self._inject_vorbis_metadata(audio_file, metadata, preserve_existing)
            elif file_format == 'mp4':
                await self._inject_mp4_metadata(audio_file, metadata, preserve_existing)
            else:
                logger.warning(f"Unsupported format for metadata injection: {file_format}")
                return False
            
            # Save metadata
            audio_file.save()
            
            logger.info(f"Metadata injected successfully to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Metadata injection failed for {file_path}: {e}")
            return False
    
    async def preserve_metadata(self,
                              source_path: Path,
                              target_path: Path,
                              enhance: bool = True) -> bool:
        """
        Preserve metadata from source to target file with optional enhancement
        
        Args:
            source_path: Source audio file
            target_path: Target audio file
            enhance: Whether to enhance metadata
            
        Returns:
            Success status
        """



        try:
            # Extract metadata from source
            source_metadata = await self.extract_metadata(source_path)
            
            # Enhance metadata if requested
            if enhance:
                source_metadata = await self._enhance_metadata(source_metadata, target_path)
            
            # Add conversion history
            source_metadata.conversion_history.append({
                'timestamp': datetime.now().isoformat(),
                'source_format': source_path.suffix[1:].lower(),
                'target_format': target_path.suffix[1:].lower(),
                'processed_by': source_metadata.processed_by
            })
            
            # Inject into target
            return await self.inject_metadata(target_path, source_metadata, preserve_existing=False)
            
        except Exception as e:
            logger.error(f"Metadata preservation failed: {e}")
            return False
    
    async def validate_metadata(self, metadata: AudioMetadata) -> Dict[str, List[str]]:
        """
        Validate metadata completeness and accuracy
        
        Args:
            metadata: Metadata to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Required fields validation
        required_fields = ['title', 'artist']
        for field in required_fields:
            if not getattr(metadata, field):
                validation_results['errors'].append(f"Missing required field: {field}")
        
        # Recommended fields validation
        recommended_fields = ['album', 'date', 'genre']
        for field in recommended_fields:
            if not getattr(metadata, field):
                validation_results['warnings'].append(f"Missing recommended field: {field}")
        
        # Data format validation
        if metadata.year and (metadata.year < 1900 or metadata.year > datetime.now().year + 1):
            validation_results['warnings'].append(f"Suspicious year value: {metadata.year}")
        
        if metadata.track_number and metadata.track_number < 1:
            validation_results['errors'].append("Track number must be positive")
        
        # ISRC validation
        if metadata.isrc:
            if not self._validate_isrc(metadata.isrc):
                validation_results['errors'].append(f"Invalid ISRC format: {metadata.isrc}")
        
        # Suggestions for enhancement
        if not metadata.cover_art:
            validation_results['suggestions'].append("Consider adding cover art")
        
        if not metadata.copyright:
            validation_results['suggestions'].append("Consider adding copyright information")
        
        return validation_results
    
    async def merge_metadata(self,
                           primary: AudioMetadata,
                           secondary: AudioMetadata,
                           strategy: str = "primary_priority") -> AudioMetadata:
        """
        Merge metadata from two sources with specified strategy
        
        Args:
            primary: Primary metadata source
            secondary: Secondary metadata source
            strategy: Merge strategy
            
        Returns:
            Merged metadata
        """
        merged = AudioMetadata()
        
        # Get all metadata fields
        fields = [f for f in AudioMetadata.__dataclass_fields__.keys() 
                 if f not in ['custom_fields', 'conversion_history']]
        
        for field in fields:
            primary_value = getattr(primary, field)
            secondary_value = getattr(secondary, field)
            
            if strategy == "primary_priority":
                merged_value = primary_value if primary_value is not None else secondary_value
            elif strategy == "secondary_priority":
                merged_value = secondary_value if secondary_value is not None else primary_value
            elif strategy == "most_complete":
                # Choose the more detailed value
                if primary_value and secondary_value:
                    merged_value = primary_value if len(str(primary_value)) >= len(str(secondary_value)) else secondary_value
                else:
                    merged_value = primary_value or secondary_value
            else:
                merged_value = primary_value
            
            setattr(merged, field, merged_value)
        
        # Merge custom fields
        merged.custom_fields = {**secondary.custom_fields, **primary.custom_fields}
        
        # Merge conversion history
        merged.conversion_history = primary.conversion_history + secondary.conversion_history
        
        return merged
    
    # Private methods for format-specific handling
    
    async def _extract_basic_metadata(self, audio_file: mutagen.FileType, metadata: AudioMetadata):
        """Extract basic metadata fields"""
        # Title
        metadata.title = self._get_tag_value(audio_file, ['TIT2', 'TITLE', '\xa9nam'])
        
        # Artist
        metadata.artist = self._get_tag_value(audio_file, ['TPE1', 'ARTIST', '\xa9ART'])
        
        # Album
        metadata.album = self._get_tag_value(audio_file, ['TALB', 'ALBUM', '\xa9alb'])
        
        # Album Artist
        metadata.album_artist = self._get_tag_value(audio_file, ['TPE2', 'ALBUMARTIST', 'aART'])
        
        # Date/Year
        date_value = self._get_tag_value(audio_file, ['TDRC', 'DATE', '\xa9day'])
        if date_value:
            metadata.date = str(date_value)
            try:
                # Extract year from date
                year_match = str(date_value)[:4]
                if year_match.isdigit():
                    metadata.year = int(year_match)
            except:
                pass
        
        # Genre
        metadata.genre = self._get_tag_value(audio_file, ['TCON', 'GENRE', '\xa9gen'])
        
        # Track number
        track_value = self._get_tag_value(audio_file, ['TRCK', 'TRACKNUMBER', 'trkn'])
        if track_value:
            try:
                if isinstance(track_value, tuple):
                    metadata.track_number = track_value[0]
                    metadata.total_tracks = track_value[1] if len(track_value) > 1 else None
                else:
                    # Handle "5/12" format
                    track_str = str(track_value)
                    if '/' in track_str:
                        parts = track_str.split('/')
                        metadata.track_number = int(parts[0])
                        metadata.total_tracks = int(parts[1]) if len(parts) > 1 else None
                    else:
                        metadata.track_number = int(track_str)
            except:
                pass
        
        # Disc number
        disc_value = self._get_tag_value(audio_file, ['TPOS', 'DISCNUMBER', 'disk'])
        if disc_value:
            try:
                if isinstance(disc_value, tuple):
                    metadata.disc_number = disc_value[0]
                    metadata.total_discs = disc_value[1] if len(disc_value) > 1 else None
                else:
                    disc_str = str(disc_value)
                    if '/' in disc_str:
                        parts = disc_str.split('/')
                        metadata.disc_number = int(parts[0])
                        metadata.total_discs = int(parts[1]) if len(parts) > 1 else None
                    else:
                        metadata.disc_number = int(disc_str)
            except:
                pass
        
        # Extended metadata
        metadata.composer = self._get_tag_value(audio_file, ['TCOM', 'COMPOSER', '\xa9wrt'])
        metadata.conductor = self._get_tag_value(audio_file, ['TPE3', 'CONDUCTOR'])
        metadata.copyright = self._get_tag_value(audio_file, ['TCOP', 'COPYRIGHT', 'cprt'])
        metadata.publisher = self._get_tag_value(audio_file, ['TPUB', 'PUBLISHER'])
        metadata.isrc = self._get_tag_value(audio_file, ['TSRC', 'ISRC'])
    
    async def _extract_technical_metadata(self, 
                                        audio_file: mutagen.FileType, 
                                        metadata: AudioMetadata, 
                                        file_path: Path):
        """Extract technical metadata"""
        if hasattr(audio_file, 'info'):
            info = audio_file.info
            metadata.bitrate = getattr(info, 'bitrate', None)
            metadata.sample_rate = getattr(info, 'sample_rate', None)
            metadata.channels = getattr(info, 'channels', None)
            metadata.duration = getattr(info, 'length', None)
            
            # Detect bit depth for lossless formats
            if hasattr(info, 'bits_per_sample'):
                metadata.bit_depth = info.bits_per_sample
            elif file_path.suffix.lower() in ['.wav', '.flac', '.aiff']:
                # Default bit depths for common formats
                metadata.bit_depth = 24 if metadata.sample_rate and metadata.sample_rate > 48000 else 16
        
        # Format information
        metadata.format = file_path.suffix[1:].lower()
        metadata.codec = self._detect_codec(audio_file, file_path)
    
    async def _extract_cover_art(self, audio_file: mutagen.FileType, metadata: AudioMetadata):
        """Extract cover art from audio file"""



        try:
            cover_data = None
            mime_type = None
            
            # ID3v2 (MP3)
            if hasattr(audio_file, 'tags') and audio_file.tags:
                apic_frames = [frame for frame in audio_file.tags.values() 
                              if hasattr(frame, 'type') and hasattr(frame, 'data')]
                if apic_frames:
                    frame = apic_frames[0]  # Use first image
                    cover_data = frame.data
                    mime_type = getattr(frame, 'mime', 'image/jpeg')
            
            # FLAC
            elif hasattr(audio_file, 'pictures') and audio_file.pictures:
                picture = audio_file.pictures[0]
                cover_data = picture.data
                mime_type = picture.mime
            
            # MP4
            elif hasattr(audio_file, 'tags') and 'covr' in audio_file.tags:
                cover_data = audio_file.tags['covr'][0]
                # Detect format from data
                if cover_data.startswith(b'\xff\xd8'):
                    mime_type = 'image/jpeg'
                elif cover_data.startswith(b'\x89PNG'):
                    mime_type = 'image/png'
                else:
                    mime_type = 'image/jpeg'
            
            if cover_data:
                metadata.cover_art = cover_data
                metadata.cover_art_mime = mime_type
                metadata.cover_art_type = 'front'
                
                # Validate and optimize cover art
                await self._optimize_cover_art(metadata)
                
        except Exception as e:
            logger.warning(f"Cover art extraction failed: {e}")
    
    async def _extract_custom_fields(self, audio_file: mutagen.FileType, metadata: AudioMetadata):
        """Extract custom/proprietary fields"""
        custom_fields = {}
        
        try:
            # ID3v2 TXXX frames (user-defined text)
            if hasattr(audio_file, 'tags') and audio_file.tags:
                for frame in audio_file.tags.values():
                    if hasattr(frame, 'desc') and hasattr(frame, 'text'):
                        if frame.__class__.__name__ == 'TXXX':
                            custom_fields[frame.desc] = frame.text[0] if frame.text else ''
            
            # Vorbis comments (case-insensitive)
            elif hasattr(audio_file, 'tags') and hasattr(audio_file.tags, 'items'):
                for key, values in audio_file.tags.items():
                    if key.upper() not in ['TITLE', 'ARTIST', 'ALBUM', 'DATE', 'GENRE']:
                        custom_fields[key] = values[0] if values else ''
            
            metadata.custom_fields = custom_fields
            
        except Exception as e:
            logger.warning(f"Custom fields extraction failed: {e}")
    
    async def _generate_fingerprints(self, file_path: Path, metadata: AudioMetadata):
        """Generate content fingerprints for protection"""



        try:
            # Generate file hash
            with open(file_path, 'rb') as f:
                file_content = f.read()
                metadata.content_hash = hashlib.sha256(file_content).hexdigest()
            
            # Generate metadata fingerprint (for tracking)
            metadata_str = f"{metadata.title}|{metadata.artist}|{metadata.album}|{metadata.duration}"
            metadata.audio_fingerprint = hashlib.md5(metadata_str.encode()).hexdigest()
            
        except Exception as e:
            logger.warning(f"Fingerprint generation failed: {e}")
    
    def _get_tag_value(self, audio_file: mutagen.FileType, possible_keys: List[str]) -> Optional[str]:
        """Get tag value trying multiple possible keys"""
        if not hasattr(audio_file, 'tags') or not audio_file.tags:
            return None
        
        for key in possible_keys:
            try:
                if key in audio_file.tags:
                    value = audio_file.tags[key]
                    if isinstance(value, list) and value:
                        return str(value[0])
                    elif value:
                        return str(value)
            except:
                continue
        
        return None
    
    def _detect_format(self, file_path: Path, audio_file: mutagen.FileType) -> str:
        """Detect metadata format type"""
        if hasattr(audio_file, 'tags'):
            if hasattr(audio_file.tags, 'version'):  # ID3
                return 'id3v2'
            elif any(key.startswith('\xa9') for key in audio_file.tags.keys()):  # MP4
                return 'mp4'
            else:  # Vorbis comments
                return 'vorbis'
        
        # Fallback to file extension
        ext = file_path.suffix.lower()
        if ext in ['.mp3']:
            return 'id3v2'
        elif ext in ['.flac', '.ogg', '.oga']:
            return 'vorbis'
        elif ext in ['.m4a', '.mp4']:
            return 'mp4'
        
        return 'unknown'
    
    def _detect_codec(self, audio_file: mutagen.FileType, file_path: Path) -> Optional[str]:
        """Detect audio codec"""
        if hasattr(audio_file, 'info'):
            if hasattr(audio_file.info, 'codec'):
                return audio_file.info.codec
        
        # Fallback to extension-based detection
        ext = file_path.suffix.lower()
        codec_map = {
            '.mp3': 'mp3',
            '.flac': 'flac',
            '.m4a': 'aac',
            '.mp4': 'aac',
            '.ogg': 'vorbis',
            '.wav': 'pcm',
            '.aiff': 'pcm'
        }
        
        return codec_map.get(ext, None)
    
    def _validate_isrc(self, isrc: str) -> bool:
        """Validate ISRC format (CC-XXX-YY-NNNNN)"""
        import re
        pattern = r'^[A-Z]{2}-[A-Z0-9]{3}-\d{2}-\d{5}$'
        return bool(re.match(pattern, isrc))
    
    async def _optimize_cover_art(self, metadata: AudioMetadata):
        """Optimize cover art size and quality"""
        if not metadata.cover_art:
            return
        
        try:
            # Load image
            img = Image.open(io.BytesIO(metadata.cover_art))
            
            # Optimize size (max 800x800 for reasonable file size)
            if img.size[0] > 800 or img.size[1] > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                
                # Save optimized image
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                metadata.cover_art = output.getvalue()
                metadata.cover_art_mime = 'image/jpeg'
                
        except Exception as e:
            logger.warning(f"Cover art optimization failed: {e}")
    
    async def _enhance_metadata(self, metadata: AudioMetadata, target_path: Path) -> AudioMetadata:
        """Enhance metadata with additional information"""
        # Add processing information
        metadata.processed_by = "IA Influencer Agent v2.0"
        metadata.processing_date = datetime.now().isoformat()
        
        # Update format information
        target_format = target_path.suffix[1:].lower()
        metadata.format = target_format
        
        # Add protection metadata if not present
        if not metadata.copyright and metadata.artist:
            current_year = datetime.now().year
            metadata.copyright = f"© {current_year} {metadata.artist}"
        
        # Enhanced rights management
        if not metadata.rights_holder and metadata.artist:
            metadata.rights_holder = metadata.artist
        
        metadata.usage_rights = "All rights reserved"
        
        return metadata
    
    # Format-specific injection methods
    
    async def _inject_id3v2_metadata(self, 
                                   audio_file: mutagen.FileType, 
                                   metadata: AudioMetadata, 
                                   preserve_existing: bool):
        """Inject ID3v2 metadata"""
        if not hasattr(audio_file, 'tags') or audio_file.tags is None:
            audio_file.add_tags()
        
        tags = audio_file.tags
        
        # Basic metadata
        if metadata.title:
            tags.add(TIT2(encoding=3, text=metadata.title))
        if metadata.artist:
            tags.add(TPE1(encoding=3, text=metadata.artist))
        if metadata.album:
            tags.add(TALB(encoding=3, text=metadata.album))
        if metadata.date:
            tags.add(TDRC(encoding=3, text=metadata.date))
        if metadata.genre:
            tags.add(TCON(encoding=3, text=metadata.genre))
        if metadata.album_artist:
            tags.add(TPE2(encoding=3, text=metadata.album_artist))
        
        # Track number
        if metadata.track_number:
            track_text = str(metadata.track_number)
            if metadata.total_tracks:
                track_text += f"/{metadata.total_tracks}"
            tags.add(TRCK(encoding=3, text=track_text))
        
        # Cover art
        if metadata.cover_art:
            tags.add(APIC(
                encoding=3,
                mime=metadata.cover_art_mime or 'image/jpeg',
                type=3,  # Cover (front)
                desc='Cover',
                data=metadata.cover_art
            ))
        
        # Custom fields
        for key, value in metadata.custom_fields.items():
            tags.add(TXXX(encoding=3, desc=key, text=str(value)))
    
    async def _inject_vorbis_metadata(self, 
                                    audio_file: mutagen.FileType, 
                                    metadata: AudioMetadata, 
                                    preserve_existing: bool):
        """Inject Vorbis comment metadata"""
        if not preserve_existing:
            audio_file.tags.clear()
        
        tags = audio_file.tags
        
        # Basic metadata
        if metadata.title:
            tags['TITLE'] = metadata.title
        if metadata.artist:
            tags['ARTIST'] = metadata.artist
        if metadata.album:
            tags['ALBUM'] = metadata.album
        if metadata.date:
            tags['DATE'] = metadata.date
        if metadata.genre:
            tags['GENRE'] = metadata.genre
        if metadata.album_artist:
            tags['ALBUMARTIST'] = metadata.album_artist
        if metadata.track_number:
            tags['TRACKNUMBER'] = str(metadata.track_number)
        if metadata.total_tracks:
            tags['TRACKTOTAL'] = str(metadata.total_tracks)
        
        # Custom fields
        for key, value in metadata.custom_fields.items():
            tags[key.upper()] = str(value)
    
    async def _inject_mp4_metadata(self, 
                                 audio_file: mutagen.FileType, 
                                 metadata: AudioMetadata, 
                                 preserve_existing: bool):
        """Inject MP4 metadata"""
        if not preserve_existing:
            audio_file.tags.clear()
        
        tags = audio_file.tags
        
        # Basic metadata
        if metadata.title:
            tags['\xa9nam'] = metadata.title
        if metadata.artist:
            tags['\xa9ART'] = metadata.artist
        if metadata.album:
            tags['\xa9alb'] = metadata.album
        if metadata.date:
            tags['\xa9day'] = metadata.date
        if metadata.genre:
            tags['\xa9gen'] = metadata.genre
        if metadata.album_artist:
            tags['aART'] = metadata.album_artist
        
        # Track and disc numbers
        if metadata.track_number:
            track_tuple = (metadata.track_number, metadata.total_tracks or 0)
            tags['trkn'] = [track_tuple]
        
        if metadata.disc_number:
            disc_tuple = (metadata.disc_number, metadata.total_discs or 0)
            tags['disk'] = [disc_tuple]
        
        # Cover art
        if metadata.cover_art:
            tags['covr'] = [metadata.cover_art]


class MetadataExtractor:
    """
    Specialized Metadata Extractor
    
    High-performance metadata extraction with caching and batch processing.
    """
    
    def __init__(self, manager: MetadataManager):
        """Initialize extractor"""
        self.manager = manager
        self.cache: Dict[str, AudioMetadata] = {}
        
    async def extract_batch(self, file_paths: List[Path]) -> Dict[Path, AudioMetadata]:
        """Extract metadata from multiple files"""
        results = {}
        
        # Process files in parallel
        tasks = [self.manager.extract_metadata(path) for path in file_paths]
        metadata_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for path, metadata in zip(file_paths, metadata_list):
            if isinstance(metadata, Exception):
                logger.error(f"Failed to extract metadata from {path}: {metadata}")
                results[path] = AudioMetadata()
            else:
                results[path] = metadata
        
        return results


class MetadataInjector:
    """
    Specialized Metadata Injector
    
    High-performance metadata injection with validation and error handling.
    """
    
    def __init__(self, manager: MetadataManager):
        """Initialize injector"""
        self.manager = manager
        
    async def inject_batch(self, 
                         file_paths: List[Path], 
                         metadata_list: List[AudioMetadata]) -> Dict[Path, bool]:
        """Inject metadata into multiple files"""
        results = {}
        
        # Process files in parallel
        tasks = [
            self.manager.inject_metadata(path, metadata) 
            for path, metadata in zip(file_paths, metadata_list)
        ]
        success_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for path, success in zip(file_paths, success_list):
            if isinstance(success, Exception):
                logger.error(f"Failed to inject metadata to {path}: {success}")
                results[path] = False
            else:
                results[path] = success
        
        return results


# Export main classes
__all__ = [
    'MetadataManager',
    'MetadataExtractor', 
    'MetadataInjector',
    'AudioMetadata'
]
