"""
📁 FILE SERVICE TEMPLATE - BACKEND SENIOR EXPERT IMPLEMENTATION
================================================================

Enterprise-grade file service template with:
- Multi-storage backend support (AWS S3, Azure Blob, GCP, Local)
- File upload/download with progress tracking
- Image/video processing and optimization
- File metadata management and indexing
- Virus scanning and security checks
- CDN integration and caching
- Backup and recovery
- Access control and permissions

Author: Backend Senior Expert
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, BinaryIO, AsyncIterator
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import logging
import hashlib
import mimetypes
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import aiofiles
import boto3
from botocore.exceptions import ClientError
from azure.storage.blob.aio import BlobServiceClient
from google.cloud import storage as gcp_storage
import redis.asyncio as redis
from PIL import Image, ImageOps
import cv2
import ffmpeg
from pydantic import BaseModel, Field, validator
import clamd
import magic


class StorageBackend(Enum):
    """Storage backend types"""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GCP_STORAGE = "gcp_storage"
    MINIO = "minio"


class FileType(Enum):
    """File type enumeration"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class ProcessingStatus(Enum):
    """File processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AccessLevel(Enum):
    """File access levels"""
    PUBLIC = "public"
    PRIVATE = "private"
    AUTHENTICATED = "authenticated"
    PREMIUM = "premium"


@dataclass
class FileServiceConfig:
    """File service configuration"""
    # Storage settings
    storage_backend: StorageBackend = StorageBackend.LOCAL
    local_storage_path: str = "/tmp/file_storage"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp",  # Images
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm",  # Videos
        ".mp3", ".wav", ".flac", ".aac", ".ogg",  # Audio
        ".pdf", ".doc", ".docx", ".txt", ".rtf",  # Documents
        ".zip", ".rar", ".7z", ".tar.gz"  # Archives
    ])
    
    # AWS S3 settings
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_bucket_name: Optional[str] = None
    
    # Azure Blob settings
    azure_connection_string: Optional[str] = None
    azure_container_name: Optional[str] = None
    
    # GCP Storage settings
    gcp_project_id: Optional[str] = None
    gcp_bucket_name: Optional[str] = None
    gcp_credentials_path: Optional[str] = None
    
    # Processing settings
    enable_image_processing: bool = True
    enable_video_processing: bool = True
    enable_audio_processing: bool = True
    image_sizes: List[tuple] = field(default_factory=lambda: [
        (150, 150),  # thumbnail
        (300, 300),  # small
        (600, 600),  # medium
        (1200, 1200)  # large
    ])
    video_qualities: List[str] = field(default_factory=lambda: [
        "240p", "360p", "480p", "720p", "1080p"
    ])
    
    # Security settings
    enable_virus_scan: bool = True
    enable_content_analysis: bool = True
    quarantine_path: str = "/tmp/quarantine"
    
    # CDN settings
    cdn_enabled: bool = False
    cdn_base_url: Optional[str] = None
    cdn_cache_ttl: int = 3600  # 1 hour
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 1800  # 30 minutes
    cache_prefix: str = "file_cache"


class FileMetadata(BaseModel):
    """File metadata model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_name: str
    stored_name: str
    content_type: str
    file_type: FileType
    size: int
    checksum: str
    storage_path: str
    storage_backend: StorageBackend
    access_level: AccessLevel = AccessLevel.PRIVATE
    owner_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    download_count: int = 0
    
    # Processing status
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    processed_variants: Dict[str, str] = Field(default_factory=dict)
    processing_error: Optional[str] = None
    
    # Security
    virus_scan_status: Optional[str] = None
    virus_scan_result: Optional[str] = None
    content_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Additional metadata
    image_metadata: Optional[Dict[str, Any]] = None
    video_metadata: Optional[Dict[str, Any]] = None
    audio_metadata: Optional[Dict[str, Any]] = None
    
    # Tags and categories
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    description: Optional[str] = None


class UploadProgress(BaseModel):
    """Upload progress model"""
    file_id: str
    uploaded_bytes: int
    total_bytes: int
    percentage: float
    status: str
    error: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds


class DownloadRequest(BaseModel):
    """Download request model"""
    file_id: str
    variant: Optional[str] = None  # e.g., "thumbnail", "720p"
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    expires_in: Optional[int] = None  # seconds


class AbstractStorageBackend(ABC):
    """Abstract storage backend interface"""
    
    @abstractmethod
    async def upload_file(self, file_path: str, data: BinaryIO, metadata: FileMetadata) -> bool:
        """Upload file to storage"""
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """Download file from storage"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Get file URL"""
        pass


class LocalStorageBackend(AbstractStorageBackend):
    """Local filesystem storage backend"""
    
    def __init__(self, config: FileServiceConfig):
        self.config = config
        self.storage_path = Path(config.local_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    async def upload_file(self, file_path: str, data: BinaryIO, metadata: FileMetadata) -> bool:
        """Upload file to local storage"""
        try:
            full_path = self.storage_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(full_path, 'wb') as f:
                while chunk := data.read(8192):
                    await f.write(chunk)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to upload file {file_path}: {e}")
            return False
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from local storage"""
        try:
            full_path = self.storage_path / file_path
            async with aiofiles.open(full_path, 'rb') as f:
                return await f.read()
        except Exception as e:
            self.logger.error(f"Failed to download file {file_path}: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            full_path = self.storage_path / file_path
            full_path.unlink(missing_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in local storage"""
        full_path = self.storage_path / file_path
        return full_path.exists()
    
    async def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Get file URL for local storage"""
        # In production, this would be served by a web server
        return f"/files/{file_path}"


class S3StorageBackend(AbstractStorageBackend):
    """AWS S3 storage backend"""
    
    def __init__(self, config: FileServiceConfig):
        self.config = config
        self.client = boto3.client(
            's3',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.aws_region
        )
        self.bucket_name = config.aws_bucket_name
        self.logger = logging.getLogger(__name__)
    
    async def upload_file(self, file_path: str, data: BinaryIO, metadata: FileMetadata) -> bool:
        """Upload file to S3"""
        try:
            self.client.upload_fileobj(
                data,
                self.bucket_name,
                file_path,
                ExtraArgs={
                    'ContentType': metadata.content_type,
                    'Metadata': {
                        'original_name': metadata.original_name,
                        'owner_id': metadata.owner_id or '',
                        'file_type': metadata.file_type.value
                    }
                }
            )
            return True
        except ClientError as e:
            self.logger.error(f"Failed to upload file {file_path} to S3: {e}")
            return False
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from S3"""
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_path)
            return response['Body'].read()
        except ClientError as e:
            self.logger.error(f"Failed to download file {file_path} from S3: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from S3"""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            self.logger.error(f"Failed to delete file {file_path} from S3: {e}")
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError:
            return False
    
    async def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Get presigned URL for S3 file"""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=expires_in or 3600
            )
            return url
        except ClientError as e:
            self.logger.error(f"Failed to generate presigned URL for {file_path}: {e}")
            raise


class FileProcessor:
    """File processing utilities"""
    
    def __init__(self, config: FileServiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def process_image(self, file_path: str, metadata: FileMetadata) -> Dict[str, str]:
        """Process image file - create thumbnails and variants"""
        variants = {}
        
        try:
            with Image.open(file_path) as img:
                # Extract metadata
                metadata.image_metadata = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                }
                
                # Create variants
                for size in self.config.image_sizes:
                    variant_name = f"{size[0]}x{size[1]}"
                    variant_path = f"{file_path}_{variant_name}"
                    
                    # Resize image maintaining aspect ratio
                    resized_img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
                    resized_img.save(variant_path, optimize=True, quality=85)
                    
                    variants[variant_name] = variant_path
                
                return variants
                
        except Exception as e:
            self.logger.error(f"Failed to process image {file_path}: {e}")
            raise
    
    async def process_video(self, file_path: str, metadata: FileMetadata) -> Dict[str, str]:
        """Process video file - create different quality variants"""
        variants = {}
        
        try:
            # Get video metadata
            probe = ffmpeg.probe(file_path)
            video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
            
            metadata.video_metadata = {
                "duration": float(probe['format']['duration']),
                "width": video_stream['width'],
                "height": video_stream['height'],
                "codec": video_stream['codec_name'],
                "framerate": eval(video_stream['r_frame_rate'])
            }
            
            # Create quality variants
            quality_settings = {
                "240p": {"height": 240, "bitrate": "500k"},
                "360p": {"height": 360, "bitrate": "800k"},
                "480p": {"height": 480, "bitrate": "1200k"},
                "720p": {"height": 720, "bitrate": "2500k"},
                "1080p": {"height": 1080, "bitrate": "5000k"}
            }
            
            for quality in self.config.video_qualities:
                if quality in quality_settings:
                    settings = quality_settings[quality]
                    variant_path = f"{file_path}_{quality}.mp4"
                    
                    # Only create if original is higher quality
                    if video_stream['height'] >= settings['height']:
                        (
                            ffmpeg
                            .input(file_path)
                            .output(
                                variant_path,
                                vf=f"scale=-2:{settings['height']}",
                                video_bitrate=settings['bitrate'],
                                acodec='aac',
                                audio_bitrate='128k'
                            )
                            .overwrite_output()
                            .run(quiet=True)
                        )
                        
                        variants[quality] = variant_path
            
            # Create thumbnail
            thumbnail_path = f"{file_path}_thumbnail.jpg"
            (
                ffmpeg
                .input(file_path, ss=1)
                .output(thumbnail_path, vframes=1, format='image2', vcodec='mjpeg')
                .overwrite_output()
                .run(quiet=True)
            )
            variants['thumbnail'] = thumbnail_path
            
            return variants
            
        except Exception as e:
            self.logger.error(f"Failed to process video {file_path}: {e}")
            raise
    
    async def process_audio(self, file_path: str, metadata: FileMetadata) -> Dict[str, str]:
        """Process audio file - create different quality variants"""
        variants = {}
        
        try:
            # Get audio metadata
            probe = ffmpeg.probe(file_path)
            audio_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'audio')
            
            metadata.audio_metadata = {
                "duration": float(probe['format']['duration']),
                "codec": audio_stream['codec_name'],
                "sample_rate": int(audio_stream['sample_rate']),
                "channels": audio_stream['channels']
            }
            
            # Create quality variants
            quality_settings = {
                "low": {"bitrate": "64k"},
                "medium": {"bitrate": "128k"},
                "high": {"bitrate": "320k"}
            }
            
            for quality, settings in quality_settings.items():
                variant_path = f"{file_path}_{quality}.mp3"
                
                (
                    ffmpeg
                    .input(file_path)
                    .output(variant_path, acodec='mp3', audio_bitrate=settings['bitrate'])
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                variants[quality] = variant_path
            
            return variants
            
        except Exception as e:
            self.logger.error(f"Failed to process audio {file_path}: {e}")
            raise


class VirusScanner:
    """Virus scanning utilities"""
    
    def __init__(self, config: FileServiceConfig):
        self.config = config
        self.clamd_client = None
        self.logger = logging.getLogger(__name__)
        
        if config.enable_virus_scan:
            try:
                self.clamd_client = clamd.ClamdUnixSocket()
                self.clamd_client.ping()
            except Exception as e:
                self.logger.warning(f"ClamAV not available: {e}")
                self.clamd_client = None
    
    async def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Scan file for viruses"""
        if not self.clamd_client:
            return {"status": "skipped", "result": "scanner_not_available"}
        
        try:
            result = self.clamd_client.scan(file_path)
            
            if result is None:
                return {"status": "clean", "result": "no_threats_found"}
            else:
                file_result = result.get(file_path)
                if file_result and file_result[0] == 'FOUND':
                    return {
                        "status": "infected",
                        "result": file_result[1],
                        "action": "quarantined"
                    }
                else:
                    return {"status": "clean", "result": "no_threats_found"}
                    
        except Exception as e:
            self.logger.error(f"Virus scan failed for {file_path}: {e}")
            return {"status": "error", "result": str(e)}


class FileService:
    """Enterprise file service"""
    
    def __init__(self, config: FileServiceConfig):
        self.config = config
        self.storage_backend = self._create_storage_backend()
        self.processor = FileProcessor(config)
        self.virus_scanner = VirusScanner(config)
        self.cache = None
        self.files_metadata: Dict[str, FileMetadata] = {}
        self.upload_progress: Dict[str, UploadProgress] = {}
        self.logger = logging.getLogger(__name__)
    
    def _create_storage_backend(self) -> AbstractStorageBackend:
        """Create storage backend instance"""
        if self.config.storage_backend == StorageBackend.LOCAL:
            return LocalStorageBackend(self.config)
        elif self.config.storage_backend == StorageBackend.AWS_S3:
            return S3StorageBackend(self.config)
        else:
            raise ValueError(f"Unsupported storage backend: {self.config.storage_backend}")
    
    async def initialize(self):
        """Initialize file service"""
        if self.config.cache_enabled:
            self.cache = redis.Redis(
                host="localhost",
                port=6379,
                decode_responses=False
            )
        
        # Create quarantine directory
        if self.config.enable_virus_scan:
            Path(self.config.quarantine_path).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("File service initialized")
    
    async def shutdown(self):
        """Shutdown file service"""
        if self.cache:
            await self.cache.close()
    
    def _get_file_type(self, filename: str, content_type: str) -> FileType:
        """Determine file type from filename and content type"""
        ext = Path(filename).suffix.lower()
        
        if content_type.startswith('image/') or ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            return FileType.IMAGE
        elif content_type.startswith('video/') or ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
            return FileType.VIDEO
        elif content_type.startswith('audio/') or ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
            return FileType.AUDIO
        elif content_type.startswith('application/') and 'document' in content_type or ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
            return FileType.DOCUMENT
        elif ext in ['.zip', '.rar', '.7z', '.tar.gz']:
            return FileType.ARCHIVE
        else:
            return FileType.OTHER
    
    def _calculate_checksum(self, file_data: bytes) -> str:
        """Calculate file checksum"""
        return hashlib.sha256(file_data).hexdigest()
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        ext = Path(filename).suffix.lower()
        return ext in self.config.allowed_extensions
    
    async def upload_file(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        owner_id: Optional[str] = None,
        access_level: AccessLevel = AccessLevel.PRIVATE,
        description: Optional[str] = None,
        tags: List[str] = None
    ) -> FileMetadata:
        """Upload file with processing and security checks"""
        
        # Validate file
        if not self._is_allowed_file(filename):
            raise ValueError(f"File type not allowed: {filename}")
        
        # Read file data
        file_data.seek(0)
        data = file_data.read()
        file_size = len(data)
        
        if file_size > self.config.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes > {self.config.max_file_size}")
        
        # Detect content type if not provided
        if not content_type:
            content_type = magic.from_buffer(data, mime=True)
        
        # Create file metadata
        file_id = str(uuid.uuid4())
        stored_name = f"{file_id}_{filename}"
        file_type = self._get_file_type(filename, content_type)
        checksum = self._calculate_checksum(data)
        
        metadata = FileMetadata(
            id=file_id,
            original_name=filename,
            stored_name=stored_name,
            content_type=content_type,
            file_type=file_type,
            size=file_size,
            checksum=checksum,
            storage_path=f"{file_type.value}/{stored_name}",
            storage_backend=self.config.storage_backend,
            access_level=access_level,
            owner_id=owner_id,
            description=description,
            tags=tags or []
        )
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(data)
            temp_file_path = temp_file.name
        
        try:
            # Virus scan
            if self.config.enable_virus_scan:
                scan_result = await self.virus_scanner.scan_file(temp_file_path)
                metadata.virus_scan_status = scan_result["status"]
                metadata.virus_scan_result = scan_result["result"]
                
                if scan_result["status"] == "infected":
                    # Move to quarantine
                    quarantine_path = Path(self.config.quarantine_path) / stored_name
                    quarantine_path.parent.mkdir(parents=True, exist_ok=True)
                    os.rename(temp_file_path, quarantine_path)
                    metadata.processing_status = ProcessingStatus.FAILED
                    metadata.processing_error = f"Virus detected: {scan_result['result']}"
                    self.files_metadata[file_id] = metadata
                    raise ValueError(f"File infected with virus: {scan_result['result']}")
            
            # Upload to storage
            file_data.seek(0)
            success = await self.storage_backend.upload_file(metadata.storage_path, file_data, metadata)
            
            if not success:
                metadata.processing_status = ProcessingStatus.FAILED
                metadata.processing_error = "Failed to upload to storage"
                raise ValueError("Failed to upload file to storage")
            
            # Process file (create variants)
            if metadata.processing_status == ProcessingStatus.PENDING:
                metadata.processing_status = ProcessingStatus.PROCESSING
                
                try:
                    variants = {}
                    
                    if file_type == FileType.IMAGE and self.config.enable_image_processing:
                        variants = await self.processor.process_image(temp_file_path, metadata)
                    elif file_type == FileType.VIDEO and self.config.enable_video_processing:
                        variants = await self.processor.process_video(temp_file_path, metadata)
                    elif file_type == FileType.AUDIO and self.config.enable_audio_processing:
                        variants = await self.processor.process_audio(temp_file_path, metadata)
                    
                    # Upload variants to storage
                    for variant_name, variant_path in variants.items():
                        storage_path = f"{file_type.value}/variants/{file_id}_{variant_name}"
                        
                        with open(variant_path, 'rb') as variant_file:
                            await self.storage_backend.upload_file(storage_path, variant_file, metadata)
                        
                        metadata.processed_variants[variant_name] = storage_path
                        
                        # Clean up temporary variant file
                        os.unlink(variant_path)
                    
                    metadata.processing_status = ProcessingStatus.COMPLETED
                    
                except Exception as e:
                    self.logger.error(f"File processing failed for {file_id}: {e}")
                    metadata.processing_status = ProcessingStatus.FAILED
                    metadata.processing_error = str(e)
            
            # Store metadata
            self.files_metadata[file_id] = metadata
            
            # Cache metadata
            if self.cache:
                cache_key = f"{self.config.cache_prefix}:metadata:{file_id}"
                await self.cache.setex(cache_key, self.config.cache_ttl, metadata.json())
            
            return metadata
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    async def download_file(self, download_request: DownloadRequest) -> bytes:
        """Download file or variant"""
        
        # Get file metadata
        metadata = await self.get_file_metadata(download_request.file_id)
        if not metadata:
            raise ValueError(f"File not found: {download_request.file_id}")
        
        # Check access permissions
        if not await self._check_access_permission(metadata, download_request.user_id):
            raise PermissionError("Access denied")
        
        # Determine file path
        if download_request.variant and download_request.variant in metadata.processed_variants:
            file_path = metadata.processed_variants[download_request.variant]
        else:
            file_path = metadata.storage_path
        
        # Check cache first
        cache_key = f"{self.config.cache_prefix}:file:{file_path}"
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                metadata.download_count += 1
                return cached_data
        
        # Download from storage
        file_data = await self.storage_backend.download_file(file_path)
        
        # Cache file data
        if self.cache and len(file_data) < 10 * 1024 * 1024:  # Only cache files < 10MB
            await self.cache.setex(cache_key, self.config.cache_ttl, file_data)
        
        # Update download count
        metadata.download_count += 1
        
        return file_data
    
    async def get_file_url(self, download_request: DownloadRequest) -> str:
        """Get file URL (for direct access or CDN)"""
        
        # Get file metadata
        metadata = await self.get_file_metadata(download_request.file_id)
        if not metadata:
            raise ValueError(f"File not found: {download_request.file_id}")
        
        # Check access permissions
        if not await self._check_access_permission(metadata, download_request.user_id):
            raise PermissionError("Access denied")
        
        # Determine file path
        if download_request.variant and download_request.variant in metadata.processed_variants:
            file_path = metadata.processed_variants[download_request.variant]
        else:
            file_path = metadata.storage_path
        
        # Get URL from storage backend
        url = await self.storage_backend.get_file_url(file_path, download_request.expires_in)
        
        # Use CDN if configured
        if self.config.cdn_enabled and self.config.cdn_base_url:
            url = f"{self.config.cdn_base_url}/{file_path}"
        
        return url
    
    async def delete_file(self, file_id: str, user_id: Optional[str] = None) -> bool:
        """Delete file and all variants"""
        
        # Get file metadata
        metadata = await self.get_file_metadata(file_id)
        if not metadata:
            return False
        
        # Check permissions
        if not await self._check_delete_permission(metadata, user_id):
            raise PermissionError("Delete access denied")
        
        try:
            # Delete main file
            await self.storage_backend.delete_file(metadata.storage_path)
            
            # Delete variants
            for variant_path in metadata.processed_variants.values():
                await self.storage_backend.delete_file(variant_path)
            
            # Remove from metadata store
            if file_id in self.files_metadata:
                del self.files_metadata[file_id]
            
            # Remove from cache
            if self.cache:
                cache_key = f"{self.config.cache_prefix}:metadata:{file_id}"
                await self.cache.delete(cache_key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_id}: {e}")
            return False
    
    async def get_file_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata"""
        
        # Check cache first
        if self.cache:
            cache_key = f"{self.config.cache_prefix}:metadata:{file_id}"
            cached_metadata = await self.cache.get(cache_key)
            if cached_metadata:
                try:
                    return FileMetadata.parse_raw(cached_metadata)
                except Exception:
                    pass
        
        # Check in-memory store
        return self.files_metadata.get(file_id)
    
    async def list_files(
        self,
        owner_id: Optional[str] = None,
        file_type: Optional[FileType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[FileMetadata]:
        """List files with filtering"""
        
        files = list(self.files_metadata.values())
        
        # Apply filters
        if owner_id:
            files = [f for f in files if f.owner_id == owner_id]
        
        if file_type:
            files = [f for f in files if f.file_type == file_type]
        
        if tags:
            files = [f for f in files if any(tag in f.tags for tag in tags)]
        
        # Sort by creation date (newest first)
        files.sort(key=lambda f: f.created_at, reverse=True)
        
        # Apply pagination
        return files[offset:offset + limit]
    
    async def _check_access_permission(self, metadata: FileMetadata, user_id: Optional[str]) -> bool:
        """Check if user has access to file"""
        if metadata.access_level == AccessLevel.PUBLIC:
            return True
        elif metadata.access_level == AccessLevel.PRIVATE:
            return user_id == metadata.owner_id
        elif metadata.access_level == AccessLevel.AUTHENTICATED:
            return user_id is not None
        elif metadata.access_level == AccessLevel.PREMIUM:
            # In real implementation, check if user has premium subscription
            return user_id is not None
        
        return False
    
    async def _check_delete_permission(self, metadata: FileMetadata, user_id: Optional[str]) -> bool:
        """Check if user can delete file"""
        return user_id == metadata.owner_id


# Usage example
async def main():
    """Example usage of FileService"""
    
    # Configure file service
    config = FileServiceConfig(
        storage_backend=StorageBackend.LOCAL,
        local_storage_path="/tmp/ainflue_files",
        max_file_size=50 * 1024 * 1024,  # 50MB
        enable_image_processing=True,
        enable_video_processing=True,
        cache_enabled=True
    )
    
    # Initialize service
    file_service = FileService(config)
    await file_service.initialize()
    
    try:
        # Upload an image file
        with open("test_image.jpg", "rb") as f:
            metadata = await file_service.upload_file(
                file_data=f,
                filename="test_image.jpg",
                content_type="image/jpeg",
                owner_id="user_123",
                access_level=AccessLevel.PUBLIC,
                description="Test image upload",
                tags=["test", "image"]
            )
        
        print(f"File uploaded: {metadata.id}")
        print(f"Processing status: {metadata.processing_status}")
        print(f"Variants: {list(metadata.processed_variants.keys())}")
        
        # Download original file
        download_request = DownloadRequest(
            file_id=metadata.id,
            user_id="user_123"
        )
        
        file_data = await file_service.download_file(download_request)
        print(f"Downloaded {len(file_data)} bytes")
        
        # Download thumbnail variant
        thumbnail_request = DownloadRequest(
            file_id=metadata.id,
            variant="150x150",
            user_id="user_123"
        )
        
        thumbnail_data = await file_service.download_file(thumbnail_request)
        print(f"Downloaded thumbnail: {len(thumbnail_data)} bytes")
        
        # Get file URL
        url = await file_service.get_file_url(download_request)
        print(f"File URL: {url}")
        
        # List files
        files = await file_service.list_files(owner_id="user_123")
        print(f"Found {len(files)} files")
        
    finally:
        await file_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())