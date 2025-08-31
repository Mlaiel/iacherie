"""
 Content Migration System - Ultra-Industrial Media Content Evolution Engine
=============================================================================

Enterprise-grade content migration system for IA Influencer Agent platform:
- Multi-format content schema evolution (audio, video, image, text)
- Content protection database structure optimization
- Media metadata standardization and transformation
- Creator content ownership tracking migrations
- Cross-platform content synchronization updates

Technical Infrastructure:
- Content Processing: FFmpeg, PIL, MediaInfo, ExifRead
- Database Layer: PostgreSQL JSONB, MongoDB GridFS, S3 storage
- Validation: Content integrity checks, format verification
- Performance: Parallel processing, chunk-based migration
- Security: Content encryption, access control updates

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 
==================================================
This content migration system, architecture, and all associated concepts are the exclusive 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, modification, reverse 
engineering, or distribution without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is STRICTLY PROHIBITED and will be prosecuted to the full extent of international law.

LEGAL CONSEQUENCES: Violation will result in immediate legal action including:
- Criminal prosecution for intellectual property theft
- Civil litigation for damages and lost profits  
- Permanent injunction against unauthorized use
- Full legal costs and attorney fees recovery

For licensing inquiries: mlaiel@live.de

Business Logic Flow:
Creator Upload → Content Analysis → Format Detection → Schema Migration → 
Protection Setup → Fingerprint Generation → Metadata Extraction → Storage Optimization
"""

import asyncio
import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import uuid
import json
import hashlib
import mimetypes
import magic
from PIL import Image, ImageEnhance
import ffmpeg
import mutagen
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4

from sqlalchemy import create_engine, text, MetaData, Table, Column, String, DateTime, Boolean, Integer, JSON, Text, BigInteger
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base_migration import BaseMigration, MigrationStatus, MigrationResult
from .schema_manager import SchemaManager
from .integrity_validator import IntegrityValidator

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type enumeration for migration handling"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    PLAYLIST = "playlist"
    ALBUM = "album"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    UNKNOWN = "unknown"


class AudioFormat(Enum):
    """Audio format standards for migration"""
    MP3 = "mp3"
    FLAC = "flac"
    WAV = "wav"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"
    AIFF = "aiff"


class VideoFormat(Enum):
    """Video format standards for migration"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    WMV = "wmv"
    M4V = "m4v"


class ImageFormat(Enum):
    """Image format standards for migration"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    GIF = "gif"
    SVG = "svg"
    HEIC = "heic"


class ContentProtectionLevel(Enum):
    """Content protection levels for migration"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"


@dataclass
class ContentMetadata:
    """Content metadata structure for migration"""
    content_id: str
    content_type: ContentType
    original_format: str
    target_format: Optional[str] = None
    file_size: int = 0
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec: Optional[str] = None
    mime_type: Optional[str] = None
    checksum: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: Optional[datetime] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    protection_level: ContentProtectionLevel = ContentProtectionLevel.STANDARD
    creator_id: Optional[str] = None
    platform_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentMigrationConfig:
    """Configuration for content migration operations"""
    source_format: str
    target_format: str
    quality_settings: Dict[str, Any] = field(default_factory=dict)
    preserve_metadata: bool = True
    generate_thumbnails: bool = True
    create_previews: bool = True
    enable_compression: bool = True
    backup_original: bool = True
    validate_integrity: bool = True
    parallel_processing: bool = True
    chunk_size: int = 1024 * 1024  # 1MB chunks
    max_workers: int = 4


@dataclass
class ContentMigrationResult:
    """Result of content migration operation"""
    content_id: str
    success: bool
    original_metadata: ContentMetadata
    migrated_metadata: Optional[ContentMetadata] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    storage_savings: float = 0.0
    quality_metrics: Dict[str, float] = field(default_factory=dict)


class ContentAnalyzer:
    """Advanced content analysis and metadata extraction"""
    
    def __init__(self):
        self.magic_detector = magic.Magic(mime=True)
    
    async def analyze_content(self, file_path: Path) -> ContentMetadata:
        """Analyze content and extract comprehensive metadata"""



        try:
            # Basic file information
            file_stats = file_path.stat()
            mime_type = self.magic_detector.from_file(str(file_path))
            checksum = await self._calculate_checksum(file_path)
            
            # Determine content type
            content_type = self._determine_content_type(mime_type, file_path.suffix)
            
            metadata = ContentMetadata(
                content_id=str(uuid.uuid4()),
                content_type=content_type,
                original_format=file_path.suffix.lower().lstrip('.'),
                file_size=file_stats.st_size,
                mime_type=mime_type,
                checksum=checksum,
                created_at=datetime.fromtimestamp(file_stats.st_ctime, timezone.utc),
                modified_at=datetime.fromtimestamp(file_stats.st_mtime, timezone.utc)
            )
            
            # Content-specific analysis
            if content_type == ContentType.AUDIO:
                await self._analyze_audio(file_path, metadata)
            elif content_type == ContentType.VIDEO:
                await self._analyze_video(file_path, metadata)
            elif content_type == ContentType.IMAGE:
                await self._analyze_image(file_path, metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Content analysis failed for {file_path}: {str(e)}")
            raise
    
    async def _analyze_audio(self, file_path: Path, metadata: ContentMetadata):
        """Analyze audio content and extract metadata"""



        try:
            # Use mutagen for audio metadata
            audio_file = mutagen.File(str(file_path))
            
            if audio_file is not None:
                metadata.duration = audio_file.info.length if hasattr(audio_file.info, 'length') else None
                metadata.bitrate = audio_file.info.bitrate if hasattr(audio_file.info, 'bitrate') else None
                metadata.sample_rate = audio_file.info.sample_rate if hasattr(audio_file.info, 'sample_rate') else None
                metadata.channels = audio_file.info.channels if hasattr(audio_file.info, 'channels') else None
                
                # Extract tags
                if audio_file.tags:
                    metadata.tags = {
                        'title': str(audio_file.tags.get('TIT2', [''])[0]) if 'TIT2' in audio_file.tags else None,
                        'artist': str(audio_file.tags.get('TPE1', [''])[0]) if 'TPE1' in audio_file.tags else None,
                        'album': str(audio_file.tags.get('TALB', [''])[0]) if 'TALB' in audio_file.tags else None,
                        'genre': str(audio_file.tags.get('TCON', [''])[0]) if 'TCON' in audio_file.tags else None,
                        'year': str(audio_file.tags.get('TDRC', [''])[0]) if 'TDRC' in audio_file.tags else None
                    }
            
            # Use ffprobe for additional technical details
            probe = ffmpeg.probe(str(file_path))
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            if audio_stream:
                metadata.codec = audio_stream.get('codec_name')
                if not metadata.sample_rate:
                    metadata.sample_rate = int(audio_stream.get('sample_rate', 0))
                if not metadata.channels:
                    metadata.channels = int(audio_stream.get('channels', 0))
                
        except Exception as e:
            logger.warning(f"Audio analysis failed for {file_path}: {str(e)}")
    
    async def _analyze_video(self, file_path: Path, metadata: ContentMetadata):
        """Analyze video content and extract metadata"""



        try:
            probe = ffmpeg.probe(str(file_path))
            
            # Get video stream info
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            if video_stream:
                metadata.width = int(video_stream.get('width', 0))
                metadata.height = int(video_stream.get('height', 0))
                metadata.codec = video_stream.get('codec_name')
                metadata.duration = float(video_stream.get('duration', 0))
                metadata.bitrate = int(video_stream.get('bit_rate', 0))
                
                # Extract video-specific metadata
                metadata.tags.update({
                    'fps': video_stream.get('r_frame_rate'),
                    'aspect_ratio': video_stream.get('display_aspect_ratio'),
                    'color_space': video_stream.get('color_space'),
                    'pixel_format': video_stream.get('pix_fmt')
                })
            
            if audio_stream:
                metadata.sample_rate = int(audio_stream.get('sample_rate', 0))
                metadata.channels = int(audio_stream.get('channels', 0))
                
        except Exception as e:
            logger.warning(f"Video analysis failed for {file_path}: {str(e)}")
    
    async def _analyze_image(self, file_path: Path, metadata: ContentMetadata):
        """Analyze image content and extract metadata"""



        try:
            with Image.open(file_path) as img:
                metadata.width, metadata.height = img.size
                metadata.tags = {
                    'mode': img.mode,
                    'format': img.format,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    metadata.tags['exif'] = {k: v for k, v in exif_data.items() if isinstance(v, (str, int, float))}
                
        except Exception as e:
            logger.warning(f"Image analysis failed for {file_path}: {str(e)}")
    
    def _determine_content_type(self, mime_type: str, file_extension: str) -> ContentType:
        """Determine content type based on MIME type and file extension"""
        if mime_type.startswith('audio/'):
            return ContentType.AUDIO
        elif mime_type.startswith('video/'):
            return ContentType.VIDEO
        elif mime_type.startswith('image/'):
            return ContentType.IMAGE
        elif mime_type.startswith('text/'):
            return ContentType.TEXT
        elif file_extension.lower() in ['.pdf', '.doc', '.docx', '.txt']:
            return ContentType.DOCUMENT
        else:
            return ContentType.UNKNOWN
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum for file integrity"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()


class ContentTransformer:
    """Advanced content transformation and format conversion"""
    
    def __init__(self, config: ContentMigrationConfig):
        self.config = config
    
    async def transform_content(self, source_path: Path, target_path: Path, metadata: ContentMetadata) -> ContentMigrationResult:
        """Transform content from source to target format"""
        start_time = datetime.now()
        result = ContentMigrationResult(
            content_id=metadata.content_id,
            success=False,
            original_metadata=metadata
        )
        
        try:
            # Create target directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Content-specific transformation
            if metadata.content_type == ContentType.AUDIO:
                await self._transform_audio(source_path, target_path, metadata, result)
            elif metadata.content_type == ContentType.VIDEO:
                await self._transform_video(source_path, target_path, metadata, result)
            elif metadata.content_type == ContentType.IMAGE:
                await self._transform_image(source_path, target_path, metadata, result)
            else:
                result.errors.append(f"Unsupported content type: {metadata.content_type}")
                return result
            
            # Calculate processing time and storage savings
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            if target_path.exists():
                original_size = source_path.stat().st_size
                new_size = target_path.stat().st_size
                result.storage_savings = ((original_size - new_size) / original_size) * 100
                
                # Analyze transformed content
                analyzer = ContentAnalyzer()
                result.migrated_metadata = await analyzer.analyze_content(target_path)
                result.success = True
            
        except Exception as e:
            error_msg = f"Content transformation failed: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
        
        return result
    
    async def _transform_audio(self, source_path: Path, target_path: Path, metadata: ContentMetadata, result: ContentMigrationResult):
        """Transform audio content with format conversion and quality optimization"""



        try:
            # Build ffmpeg command based on target format
            input_stream = ffmpeg.input(str(source_path))
            
            if self.config.target_format.lower() == 'flac':
                output_stream = ffmpeg.output(
                    input_stream,
                    str(target_path),
                    acodec='flac',
                    compression_level=8
                )
            elif self.config.target_format.lower() == 'mp3':
                bitrate = self.config.quality_settings.get('bitrate', '320k')
                output_stream = ffmpeg.output(
                    input_stream,
                    str(target_path),
                    acodec='libmp3lame',
                    audio_bitrate=bitrate
                )
            elif self.config.target_format.lower() == 'aac':
                bitrate = self.config.quality_settings.get('bitrate', '256k')
                output_stream = ffmpeg.output(
                    input_stream,
                    str(target_path),
                    acodec='aac',
                    audio_bitrate=bitrate
                )
            else:
                output_stream = ffmpeg.output(input_stream, str(target_path))
            
            # Execute conversion
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            # Preserve metadata if requested
            if self.config.preserve_metadata and metadata.tags:
                await self._preserve_audio_metadata(target_path, metadata.tags)
                
        except Exception as e:
            raise Exception(f"Audio transformation failed: {str(e)}")
    
    async def _transform_video(self, source_path: Path, target_path: Path, metadata: ContentMetadata, result: ContentMigrationResult):
        """Transform video content with codec optimization and quality settings"""



        try:
            input_stream = ffmpeg.input(str(source_path))
            
            # Default to H.264 with optimized settings
            video_codec = self.config.quality_settings.get('video_codec', 'libx264')
            crf = self.config.quality_settings.get('crf', 23)
            preset = self.config.quality_settings.get('preset', 'medium')
            
            output_stream = ffmpeg.output(
                input_stream,
                str(target_path),
                vcodec=video_codec,
                crf=crf,
                preset=preset,
                acodec='aac',
                audio_bitrate='128k'
            )
            
            # Generate thumbnail if requested
            if self.config.generate_thumbnails:
                thumbnail_path = target_path.with_suffix('.jpg')
                thumbnail_stream = ffmpeg.output(
                    input_stream,
                    str(thumbnail_path),
                    vframes=1,
                    ss=1
                )
                ffmpeg.run(thumbnail_stream, overwrite_output=True, quiet=True)
            
            # Execute conversion
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
        except Exception as e:
            raise Exception(f"Video transformation failed: {str(e)}")
    
    async def _transform_image(self, source_path: Path, target_path: Path, metadata: ContentMetadata, result: ContentMigrationResult):
        """Transform image content with optimization and format conversion"""



        try:
            with Image.open(source_path) as img:
                # Convert color mode if necessary
                if self.config.target_format.lower() == 'jpeg' and img.mode in ('RGBA', 'LA'):
                    # Convert transparent images to RGB with white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Apply quality settings
                save_kwargs = {}
                if self.config.target_format.lower() == 'jpeg':
                    quality = self.config.quality_settings.get('quality', 85)
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                elif self.config.target_format.lower() == 'png':
                    save_kwargs['optimize'] = True
                elif self.config.target_format.lower() == 'webp':
                    quality = self.config.quality_settings.get('quality', 80)
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                
                # Resize if specified
                if 'max_width' in self.config.quality_settings or 'max_height' in self.config.quality_settings:
                    max_width = self.config.quality_settings.get('max_width', img.width)
                    max_height = self.config.quality_settings.get('max_height', img.height)
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Save transformed image
                img.save(target_path, format=self.config.target_format.upper(), **save_kwargs)
                
        except Exception as e:
            raise Exception(f"Image transformation failed: {str(e)}")
    
    async def _preserve_audio_metadata(self, target_path: Path, tags: Dict[str, Any]):
        """Preserve audio metadata in transformed file"""



        try:
            audio_file = mutagen.File(str(target_path), easy=True)
            
            if audio_file is not None:
                if tags.get('title'):
                    audio_file['title'] = tags['title']
                if tags.get('artist'):
                    audio_file['artist'] = tags['artist']
                if tags.get('album'):
                    audio_file['album'] = tags['album']
                if tags.get('genre'):
                    audio_file['genre'] = tags['genre']
                if tags.get('year'):
                    audio_file['date'] = tags['year']
                
                audio_file.save()
                
        except Exception as e:
            logger.warning(f"Failed to preserve metadata: {str(e)}")


class ProtectionMigration(BaseMigration):
    """Content protection system migration for enhanced security features"""
    
    def __init__(self, version: str, description: str):
        super().__init__(version, description)
        self.migration_id = f"protection_{version}"
        self.category = "protection"
    
    async def execute_migration(self, session: Session) -> MigrationResult:
        """Execute content protection migration"""



        try:
            # Create protection tables
            await self._create_protection_tables(session)
            
            # Migrate existing content to protection system
            await self._migrate_content_protection(session)
            
            # Update indexes for performance
            await self._optimize_protection_indexes(session)
            
            return MigrationResult(
                migration_id=self.migration_id,
                success=True,
                message="Content protection migration completed successfully"
            )
            
        except Exception as e:
            error_msg = f"Protection migration failed: {str(e)}"
            logger.error(error_msg)
            return MigrationResult(
                migration_id=self.migration_id,
                success=False,
                message=error_msg,
                error=str(e)
            )
    
    async def _create_protection_tables(self, session: Session):
        """Create content protection related tables"""
        protection_table_sql = """
        CREATE TABLE IF NOT EXISTS content_protection (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content_id UUID NOT NULL REFERENCES content(id),
            protection_level VARCHAR(50) NOT NULL DEFAULT 'standard',
            encryption_key_id UUID,
            access_controls JSONB DEFAULT '{}',
            copyright_metadata JSONB DEFAULT '{}',
            dmca_settings JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_content_protection_content_id ON content_protection(content_id);
        CREATE INDEX IF NOT EXISTS idx_content_protection_level ON content_protection(protection_level);
        """
        
        session.execute(text(protection_table_sql))
        session.commit()
    
    async def _migrate_content_protection(self, session: Session):
        """Migrate existing content to protection system"""
        # Add protection records for existing content
        migration_sql = """
        INSERT INTO content_protection (content_id, protection_level, access_controls)
        SELECT 
            id as content_id,
            'standard' as protection_level,
            '{"public_access": true, "download_enabled": false}' as access_controls
        FROM content 
        WHERE id NOT IN (SELECT content_id FROM content_protection);
        """
        
        session.execute(text(migration_sql))
        session.commit()
    
    async def _optimize_protection_indexes(self, session: Session):
        """Optimize indexes for protection queries"""
        index_sql = """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_protection_composite 
        ON content_protection(content_id, protection_level);
        
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_protection_gin_access 
        ON content_protection USING GIN (access_controls);
        """
        
        session.execute(text(index_sql))
        session.commit()


class ContentMigration(BaseMigration):
    """Main content migration class for comprehensive content evolution"""
    
    def __init__(self, version: str, description: str, config: Optional[ContentMigrationConfig] = None):
        super().__init__(version, description)
        self.migration_id = f"content_{version}"
        self.category = "content"
        self.config = config or ContentMigrationConfig(
            source_format="*",
            target_format="optimized"
        )
        self.analyzer = ContentAnalyzer()
        self.transformer = ContentTransformer(self.config)
    
    async def execute_migration(self, session: Session) -> MigrationResult:
        """Execute comprehensive content migration"""



        try:
            # Update content schema
            await self._update_content_schema(session)
            
            # Migrate content metadata
            await self._migrate_content_metadata(session)
            
            # Optimize content storage
            await self._optimize_content_storage(session)
            
            # Update content indexes
            await self._update_content_indexes(session)
            
            return MigrationResult(
                migration_id=self.migration_id,
                success=True,
                message="Content migration completed successfully"
            )
            
        except Exception as e:
            error_msg = f"Content migration failed: {str(e)}"
            logger.error(error_msg)
            return MigrationResult(
                migration_id=self.migration_id,
                success=False,
                message=error_msg,
                error=str(e)
            )
    
    async def _update_content_schema(self, session: Session):
        """Update content table schema for enhanced features"""
        schema_updates = """
        -- Add new columns for enhanced content management
        ALTER TABLE content 
        ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64),
        ADD COLUMN IF NOT EXISTS content_size BIGINT DEFAULT 0,
        ADD COLUMN IF NOT EXISTS content_duration FLOAT,
        ADD COLUMN IF NOT EXISTS content_dimensions JSONB,
        ADD COLUMN IF NOT EXISTS technical_metadata JSONB DEFAULT '{}',
        ADD COLUMN IF NOT EXISTS protection_level VARCHAR(50) DEFAULT 'standard',
        ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) DEFAULT 'pending';
        
        -- Update existing records with default values
        UPDATE content 
        SET technical_metadata = '{}'::jsonb 
        WHERE technical_metadata IS NULL;
        """
        
        session.execute(text(schema_updates))
        session.commit()
    
    async def _migrate_content_metadata(self, session: Session):
        """Migrate and enhance content metadata"""
        # Get all content records that need metadata enhancement
        content_query = """
        SELECT id, file_path, content_type, created_at
        FROM content 
        WHERE technical_metadata = '{}'::jsonb OR technical_metadata IS NULL
        LIMIT 1000;
        """
        
        result = session.execute(text(content_query))
        content_records = result.fetchall()
        
        for record in content_records:
            try:
                content_id, file_path, content_type, created_at = record
                
                if file_path and Path(file_path).exists():
                    # Analyze content and extract metadata
                    metadata = await self.analyzer.analyze_content(Path(file_path))
                    
                    # Update content record with enhanced metadata
                    update_sql = """
                    UPDATE content 
                    SET 
                        content_hash = :hash,
                        content_size = :size,
                        content_duration = :duration,
                        content_dimensions = :dimensions,
                        technical_metadata = :metadata
                    WHERE id = :content_id;
                    """
                    
                    dimensions = None
                    if metadata.width and metadata.height:
                        dimensions = json.dumps({"width": metadata.width, "height": metadata.height})
                    
                    session.execute(text(update_sql), {
                        'content_id': content_id,
                        'hash': metadata.checksum,
                        'size': metadata.file_size,
                        'duration': metadata.duration,
                        'dimensions': dimensions,
                        'metadata': json.dumps(metadata.tags)
                    })
                
            except Exception as e:
                logger.warning(f"Failed to migrate metadata for content {content_id}: {str(e)}")
        
        session.commit()
    
    async def _optimize_content_storage(self, session: Session):
        """Optimize content storage and file organization"""
        # Clean up orphaned content records
        cleanup_sql = """
        UPDATE content 
        SET processing_status = 'orphaned'
        WHERE file_path IS NOT NULL 
        AND NOT EXISTS (
            SELECT 1 FROM pg_stat_file(file_path) 
        );
        """
        
        session.execute(text(cleanup_sql))
        session.commit()
    
    async def _update_content_indexes(self, session: Session):
        """Update and optimize content-related indexes"""
        index_sql = """
        -- Performance indexes for content queries
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_hash 
        ON content(content_hash) WHERE content_hash IS NOT NULL;
        
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_type_status 
        ON content(content_type, processing_status);
        
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_size 
        ON content(content_size) WHERE content_size > 0;
        
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_duration 
        ON content(content_duration) WHERE content_duration IS NOT NULL;
        
        -- GIN index for technical metadata search
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_technical_metadata_gin 
        ON content USING GIN (technical_metadata);
        """
        
        session.execute(text(index_sql))
        session.commit()
    
    async def rollback_migration(self, session: Session) -> MigrationResult:
        """Rollback content migration changes"""



        try:
            # Remove added columns
            rollback_sql = """
            ALTER TABLE content 
            DROP COLUMN IF EXISTS content_hash,
            DROP COLUMN IF EXISTS content_size,
            DROP COLUMN IF EXISTS content_duration,
            DROP COLUMN IF EXISTS content_dimensions,
            DROP COLUMN IF EXISTS technical_metadata,
            DROP COLUMN IF EXISTS protection_level,
            DROP COLUMN IF EXISTS processing_status;
            """
            
            session.execute(text(rollback_sql))
            session.commit()
            
            return MigrationResult(
                migration_id=self.migration_id,
                success=True,
                message="Content migration rollback completed successfully"
            )
            
        except Exception as e:
            error_msg = f"Content migration rollback failed: {str(e)}"
            logger.error(error_msg)
            return MigrationResult(
                migration_id=self.migration_id,
                success=False,
                message=error_msg,
                error=str(e)
            )
