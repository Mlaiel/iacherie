"""Storage Configuration Module - Consolidated Storage Configs
===========================================================

Consolidates all storage-related configurations from:
- config/storage/ (14 files)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import os

# ===== STORAGE TYPES =====

class StorageType(str, Enum):
    """Storage backend types"""
    LOCAL = "local"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GCS = "gcs"
    MINIO = "minio"
    CEPH = "ceph"
    NFS = "nfs"

class CompressionType(str, Enum):
    """Compression algorithms"""
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    BROTLI = "brotli"
    NONE = "none"

class EncryptionType(str, Enum):
    """Encryption types"""
    AES_256 = "aes_256"
    AES_128 = "aes_128"
    SERVER_SIDE = "server_side"
    CLIENT_SIDE = "client_side"
    NONE = "none"

# ===== LOCAL STORAGE CONFIGURATION =====

@dataclass
class LocalStorageConfig:
    """Local file system storage configuration"""
    enabled: bool = True
    base_path: str = "/var/lib/ia-influencer/storage"
    max_file_size: int = 104857600  # 100MB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3", ".wav", ".pdf", ".txt"
    ])
    create_directories: bool = True
    file_permissions: str = "644"
    directory_permissions: str = "755"
    backup_enabled: bool = False
    backup_path: Optional[str] = None

# ===== S3 STORAGE CONFIGURATION =====

@dataclass
class S3Config:
    """Amazon S3 storage configuration"""
    enabled: bool = False
    bucket_name: str = ""
    region: str = "us-east-1"
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    endpoint_url: Optional[str] = None  # For S3-compatible services
    use_ssl: bool = True
    signature_version: str = "s3v4"
    max_pool_connections: int = 50
    retry_attempts: int = 3
    multipart_threshold: int = 8388608  # 8MB
    multipart_chunksize: int = 8388608  # 8MB
    transfer_config: Dict[str, Any] = field(default_factory=dict)

# ===== AZURE BLOB CONFIGURATION =====

@dataclass
class AzureBlobConfig:
    """Azure Blob Storage configuration"""
    enabled: bool = False
    account_name: str = ""
    account_key: Optional[str] = None
    connection_string: Optional[str] = None
    container_name: str = "ia-influencer-storage"
    sas_token: Optional[str] = None
    max_single_put_size: int = 67108864  # 64MB
    max_block_size: int = 4194304  # 4MB
    max_page_size: int = 4194304  # 4MB
    retry_total: int = 3

# ===== GOOGLE CLOUD STORAGE CONFIGURATION =====

@dataclass
class GCSConfig:
    """Google Cloud Storage configuration"""
    enabled: bool = False
    bucket_name: str = ""
    project_id: str = ""
    credentials_path: Optional[str] = None
    credentials_json: Optional[str] = None
    location: str = "US"
    storage_class: str = "STANDARD"  # STANDARD, NEARLINE, COLDLINE, ARCHIVE
    chunk_size: int = 8388608  # 8MB
    timeout: int = 60
    retry_attempts: int = 3

# ===== CDN CONFIGURATION =====

class CDNProvider(str, Enum):
    """CDN providers"""
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GCS_CDN = "gcs_cdn"
    FASTLY = "fastly"
    MAXCDN = "maxcdn"

@dataclass
class CDNConfig:
    """Content Delivery Network configuration"""
    enabled: bool = False
    provider: CDNProvider = CDNProvider.CLOUDFLARE
    base_url: str = ""
    api_key: Optional[str] = None
    zone_id: Optional[str] = None
    cache_ttl: int = 86400  # 24 hours
    purge_on_update: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])

# ===== BACKUP CONFIGURATION =====

class BackupType(str, Enum):
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

class BackupDestination(str, Enum):
    """Backup destinations"""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"
    FTP = "ftp"
    SFTP = "sftp"

@dataclass
class BackupSchedule:
    """Backup schedule configuration"""
    enabled: bool = True
    backup_type: BackupType = BackupType.INCREMENTAL
    frequency: str = "daily"  # hourly, daily, weekly, monthly
    time: str = "02:00"  # 2 AM
    retention_days: int = 30
    max_backups: int = 10

@dataclass
class BackupConfig:
    """Backup configuration"""
    enabled: bool = True
    destination: BackupDestination = BackupDestination.LOCAL
    backup_path: str = "/var/lib/ia-influencer/backups"
    encryption_enabled: bool = True
    compression_enabled: bool = True
    compression_type: CompressionType = CompressionType.GZIP
    verification_enabled: bool = True
    schedules: List[BackupSchedule] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.tmp", "*.log"])

# ===== FILE PROCESSING CONFIGURATION =====

class ImageFormat(str, Enum):
    """Image formats"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"

class VideoFormat(str, Enum):
    """Video formats"""
    MP4 = "mp4"
    WEBM = "webm"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    FLV = "flv"

class AudioFormat(str, Enum):
    """Audio formats"""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"

@dataclass
class ImageProcessingConfig:
    """Image processing configuration"""
    enabled: bool = True
    auto_resize: bool = True
    max_width: int = 2048
    max_height: int = 2048
    quality: int = 85
    format: ImageFormat = ImageFormat.JPEG
    progressive: bool = True
    thumbnail_generation: bool = True
    thumbnail_sizes: List[tuple] = field(default_factory=lambda: [(150, 150), (300, 300)])
    watermark_enabled: bool = False
    watermark_path: Optional[str] = None

@dataclass
class VideoProcessingConfig:
    """Video processing configuration"""
    enabled: bool = True
    auto_transcode: bool = True
    target_format: VideoFormat = VideoFormat.MP4
    target_codec: str = "h264"
    target_resolution: str = "1080p"
    target_bitrate: str = "2M"
    thumbnail_generation: bool = True
    thumbnail_count: int = 3
    preview_generation: bool = True
    preview_duration: int = 30  # seconds

@dataclass
class AudioProcessingConfig:
    """Audio processing configuration"""
    enabled: bool = True
    auto_transcode: bool = True
    target_format: AudioFormat = AudioFormat.MP3
    target_bitrate: str = "192k"
    target_sample_rate: int = 44100
    normalize_audio: bool = True
    remove_silence: bool = False
    generate_waveform: bool = True
    generate_spectrogram: bool = False

@dataclass
class FileProcessingConfig:
    """File processing configuration"""
    enabled: bool = True
    max_file_size: int = 1073741824  # 1GB
    virus_scanning: bool = True
    metadata_extraction: bool = True
    image_processing: ImageProcessingConfig = field(default_factory=ImageProcessingConfig)
    video_processing: VideoProcessingConfig = field(default_factory=VideoProcessingConfig)
    audio_processing: AudioProcessingConfig = field(default_factory=AudioProcessingConfig)
    queue_processing: bool = True
    processing_timeout: int = 3600  # 1 hour

# ===== STORAGE SECURITY CONFIGURATION =====

@dataclass
class StorageSecurityConfig:
    """Storage security configuration"""
    encryption_at_rest: bool = True
    encryption_type: EncryptionType = EncryptionType.AES_256
    encryption_key: Optional[str] = None
    access_control_enabled: bool = True
    signed_urls_enabled: bool = True
    signed_url_expiry: int = 3600  # 1 hour
    ip_whitelist: List[str] = field(default_factory=list)
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    audit_logging: bool = True

# ===== MAIN STORAGE CONFIGURATION =====

@dataclass
class StorageConfig:
    """Main storage configuration"""
    default_backend: StorageType = StorageType.LOCAL
    local: LocalStorageConfig = field(default_factory=LocalStorageConfig)
    s3: S3Config = field(default_factory=S3Config)
    azure_blob: AzureBlobConfig = field(default_factory=AzureBlobConfig)
    gcs: GCSConfig = field(default_factory=GCSConfig)
    cdn: CDNConfig = field(default_factory=CDNConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    file_processing: FileProcessingConfig = field(default_factory=FileProcessingConfig)
    security: StorageSecurityConfig = field(default_factory=StorageSecurityConfig)
    temp_cleanup_hours: int = 24
    upload_chunk_size: int = 8388608  # 8MB

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_storage_config() -> StorageConfig:
    """Get development storage configuration"""
    return StorageConfig(
        default_backend=StorageType.LOCAL,
        local=LocalStorageConfig(
            base_path="/tmp/ia-influencer-dev/storage",
            max_file_size=52428800,  # 50MB
            backup_enabled=False
        ),
        backup=BackupConfig(
            enabled=False
        ),
        file_processing=FileProcessingConfig(
            virus_scanning=False,
            queue_processing=False
        ),
        security=StorageSecurityConfig(
            encryption_at_rest=False,
            access_control_enabled=False,
            audit_logging=False
        )
    )

def get_production_storage_config() -> StorageConfig:
    """Get production storage configuration"""
    return StorageConfig(
        default_backend=StorageType.S3,
        local=LocalStorageConfig(
            base_path="/var/lib/ia-influencer/storage",
            backup_enabled=True,
            backup_path="/var/lib/ia-influencer/backups"
        ),
        s3=S3Config(
            enabled=True,
            bucket_name=os.getenv("S3_BUCKET_NAME", ""),
            region=os.getenv("AWS_REGION", "us-east-1"),
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        ),
        cdn=CDNConfig(
            enabled=True,
            provider=CDNProvider.AWS_CLOUDFRONT,
            base_url=os.getenv("CDN_BASE_URL", "")
        ),
        backup=BackupConfig(
            enabled=True,
            destination=BackupDestination.S3,
            encryption_enabled=True,
            compression_enabled=True
        ),
        file_processing=FileProcessingConfig(
            virus_scanning=True,
            queue_processing=True
        ),
        security=StorageSecurityConfig(
            encryption_at_rest=True,
            access_control_enabled=True,
            audit_logging=True
        )
    )

def get_testing_storage_config() -> StorageConfig:
    """Get testing storage configuration"""
    return StorageConfig(
        default_backend=StorageType.LOCAL,
        local=LocalStorageConfig(
            base_path="/tmp/ia-influencer-test/storage",
            max_file_size=10485760,  # 10MB
            backup_enabled=False
        ),
        backup=BackupConfig(
            enabled=False
        ),
        file_processing=FileProcessingConfig(
            virus_scanning=False,
            queue_processing=False,
            auto_resize=False,
            auto_transcode=False
        ),
        security=StorageSecurityConfig(
            encryption_at_rest=False,
            access_control_enabled=False,
            audit_logging=False
        )
    )

# ===== STORAGE CONFIGURATION FACTORY =====

class StorageConfigurationFactory:
    """Factory for creating storage configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> StorageConfig:
        """Create storage configuration for environment"""
        if environment.lower() == "production":
            return get_production_storage_config()
        elif environment.lower() == "testing":
            return get_testing_storage_config()
        else:
            return get_development_storage_config()

# Export all storage configurations
__all__ = [
    # Enums
    "StorageType",
    "CompressionType",
    "EncryptionType",
    "CDNProvider",
    "BackupType",
    "BackupDestination",
    "ImageFormat",
    "VideoFormat",
    "AudioFormat",
    
    # Configuration Classes
    "LocalStorageConfig",
    "S3Config",
    "AzureBlobConfig",
    "GCSConfig",
    "CDNConfig",
    "BackupSchedule",
    "BackupConfig",
    "ImageProcessingConfig",
    "VideoProcessingConfig",
    "AudioProcessingConfig",
    "FileProcessingConfig",
    "StorageSecurityConfig",
    "StorageConfig",
    
    # Factory and Functions
    "StorageConfigurationFactory",
    "get_development_storage_config",
    "get_production_storage_config",
    "get_testing_storage_config"
]