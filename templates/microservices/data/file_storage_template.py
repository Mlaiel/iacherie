"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

File Storage Template for iacherie Creator Economy Platform
Enterprise file storage service with multi-cloud support, CDN integration and intelligent optimization
"""

import asyncio
import hashlib
import mimetypes
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
import secrets
import json

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel, validator
import boto3
import aioboto3
from azure.storage.blob.aio import BlobServiceClient
from google.cloud import storage as gcs
import redis.asyncio as redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class StorageProvider(str, Enum):
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    LOCAL = "local"
    MINIO = "minio"


class FileType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class StorageClass(str, Enum):
    STANDARD = "standard"
    REDUCED_REDUNDANCY = "reduced_redundancy"
    GLACIER = "glacier"
    DEEP_ARCHIVE = "deep_archive"
    INTELLIGENT_TIERING = "intelligent_tiering"


class AccessLevel(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    AUTHENTICATED = "authenticated"
    RESTRICTED = "restricted"


@dataclass
class StorageConfig:
    """Configuration du service de stockage"""
    # Provider settings
    primary_provider: StorageProvider = StorageProvider.AWS_S3
    fallback_provider: Optional[StorageProvider] = None
    
    # AWS S3 configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_bucket_name: str = "iacherie-storage"
    
    # Azure Blob configuration
    azure_connection_string: Optional[str] = None
    azure_container_name: str = "iacherie-storage"
    
    # Google Cloud configuration
    gcp_project_id: Optional[str] = None
    gcp_bucket_name: str = "iacherie-storage"
    gcp_credentials_path: Optional[str] = None
    
    # Local storage configuration
    local_storage_path: str = "/var/lib/iacherie/storage"
    
    # File handling
    max_file_size_mb: int = 1000  # 1GB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".gif", ".webp",  # Images
        ".mp4", ".avi", ".mov", ".wmv", ".flv",     # Videos
        ".mp3", ".wav", ".aac", ".flac", ".ogg",   # Audio
        ".pdf", ".doc", ".docx", ".txt", ".md",    # Documents
        ".zip", ".rar", ".7z", ".tar.gz"           # Archives
    ])
    
    # CDN and optimization
    enable_cdn: bool = True
    cdn_url: Optional[str] = None
    enable_image_optimization: bool = True
    enable_video_transcoding: bool = True
    
    # Security
    enable_virus_scanning: bool = True
    enable_content_validation: bool = True
    signed_url_expiry_hours: int = 24
    
    # Performance
    enable_multipart_upload: bool = True
    multipart_threshold_mb: int = 100
    chunk_size_mb: int = 10
    enable_compression: bool = True
    
    # Backup and replication
    enable_cross_region_backup: bool = True
    backup_retention_days: int = 30
    enable_versioning: bool = True


class FileMetadata(BaseModel):
    """Métadonnées de fichier"""
    file_id: str
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    file_type: FileType
    storage_provider: StorageProvider
    storage_path: str
    access_level: AccessLevel = AccessLevel.PRIVATE
    storage_class: StorageClass = StorageClass.STANDARD
    
    # Upload info
    uploaded_by: str
    uploaded_at: datetime
    upload_source: str = "web"
    
    # Processing status
    processing_status: str = "uploaded"
    processing_progress: float = 0.0
    
    # File properties
    checksum_md5: str
    checksum_sha256: Optional[str] = None
    
    # Media-specific metadata
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    video_duration: Optional[float] = None
    audio_duration: Optional[float] = None
    
    # Optimization
    optimized_versions: Dict[str, str] = {}
    cdn_urls: Dict[str, str] = {}
    
    # Access tracking
    download_count: int = 0
    last_accessed: Optional[datetime] = None
    
    # Backup and versioning
    backup_status: str = "pending"
    version_number: int = 1
    previous_versions: List[str] = []


class UploadRequest(BaseModel):
    """Demande d'upload de fichier"""
    filename: str
    content_type: str
    file_size: int
    access_level: AccessLevel = AccessLevel.PRIVATE
    storage_class: StorageClass = StorageClass.STANDARD
    uploaded_by: str
    folder: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class UploadResponse(BaseModel):
    """Réponse d'upload"""
    file_id: str
    upload_url: Optional[str] = None  # For direct upload
    download_url: Optional[str] = None
    metadata: FileMetadata
    success: bool = True


class FileStorageTemplate:
    """
    Template de service de stockage de fichiers enterprise pour iacherie
    
    Fonctionnalités:
    - Multi-cloud storage (AWS S3, Azure Blob, Google Cloud)
    - Intelligent file optimization (images, videos)
    - CDN integration avec cache invalidation
    - Virus scanning et content validation
    - Multipart upload pour gros fichiers
    - Versioning et backup automatique
    - Access control granulaire
    - Monitoring et analytics
    - Cost optimization avec storage classes
    """
    
    def __init__(self, config: StorageConfig = None):
        self.config = config or StorageConfig()
        self.app = FastAPI(
            title="iacherie File Storage Service",
            description="Enterprise file storage with multi-cloud support",
            version="1.0.0"
        )
        
        # Storage clients
        self.s3_client = None
        self.azure_client = None
        self.gcs_client = None
        
        # Redis pour métadonnées et cache
        self.redis = redis.Redis(host='localhost', port=6379, db=10, decode_responses=True)
        
        # File metadata storage
        self.file_metadata: Dict[str, FileMetadata] = {}
        
        # Upload tracking
        self.active_uploads: Dict[str, Dict[str, Any]] = {}
        
        # Métriques Prometheus
        self.upload_requests = Counter('storage_upload_requests_total', ['provider', 'file_type', 'status'])
        self.download_requests = Counter('storage_download_requests_total', ['provider', 'access_type'])
        self.storage_operations = Counter('storage_operations_total', ['provider', 'operation'])
        self.file_size_histogram = Histogram('storage_file_size_bytes', ['file_type'])
        self.upload_duration = Histogram('storage_upload_duration_seconds', ['provider', 'file_type'])
        self.total_storage_size = Gauge('storage_total_size_bytes', ['provider'])
        self.file_count = Gauge('storage_file_count_total', ['provider', 'file_type'])
        
        # Setup
        asyncio.create_task(self._initialize_storage_clients())
        self._setup_routes()
        self._start_background_tasks()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def _initialize_storage_clients(self):
        """Initialisation des clients de stockage"""
        try:
            # AWS S3
            if self.config.primary_provider == StorageProvider.AWS_S3 or self.config.fallback_provider == StorageProvider.AWS_S3:
                await self._initialize_s3_client()
            
            # Azure Blob Storage
            if self.config.primary_provider == StorageProvider.AZURE_BLOB or self.config.fallback_provider == StorageProvider.AZURE_BLOB:
                await self._initialize_azure_client()
            
            # Google Cloud Storage
            if self.config.primary_provider == StorageProvider.GOOGLE_CLOUD or self.config.fallback_provider == StorageProvider.GOOGLE_CLOUD:
                await self._initialize_gcs_client()
            
            # Local storage
            if self.config.primary_provider == StorageProvider.LOCAL:
                await self._initialize_local_storage()
            
            self.logger.info("Storage clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize storage clients: {str(e)}")
            raise

    async def _initialize_s3_client(self):
        """Initialisation du client S3"""
        try:
            session = aioboto3.Session()
            self.s3_client = session.client(
                's3',
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
                region_name=self.config.aws_region
            )
            
            # Test connection and create bucket if needed
            async with self.s3_client as s3:
                try:
                    await s3.head_bucket(Bucket=self.config.aws_bucket_name)
                except:
                    await s3.create_bucket(Bucket=self.config.aws_bucket_name)
                    self.logger.info(f"Created S3 bucket: {self.config.aws_bucket_name}")
            
            self.logger.info("S3 client initialized")
            
        except Exception as e:
            self.logger.error(f"S3 initialization failed: {str(e)}")
            if self.config.primary_provider == StorageProvider.AWS_S3:
                raise

    async def _initialize_azure_client(self):
        """Initialisation du client Azure Blob"""
        try:
            self.azure_client = BlobServiceClient.from_connection_string(
                self.config.azure_connection_string
            )
            
            # Test connection and create container if needed
            try:
                await self.azure_client.get_container_client(self.config.azure_container_name).get_container_properties()
            except:
                await self.azure_client.create_container(self.config.azure_container_name)
                self.logger.info(f"Created Azure container: {self.config.azure_container_name}")
            
            self.logger.info("Azure Blob client initialized")
            
        except Exception as e:
            self.logger.error(f"Azure Blob initialization failed: {str(e)}")
            if self.config.primary_provider == StorageProvider.AZURE_BLOB:
                raise

    async def _initialize_gcs_client(self):
        """Initialisation du client Google Cloud Storage"""
        try:
            if self.config.gcp_credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.gcp_credentials_path
            
            self.gcs_client = gcs.Client(project=self.config.gcp_project_id)
            
            # Test connection and create bucket if needed
            try:
                bucket = self.gcs_client.bucket(self.config.gcp_bucket_name)
                bucket.reload()
            except:
                bucket = self.gcs_client.create_bucket(self.config.gcp_bucket_name)
                self.logger.info(f"Created GCS bucket: {self.config.gcp_bucket_name}")
            
            self.logger.info("GCS client initialized")
            
        except Exception as e:
            self.logger.error(f"GCS initialization failed: {str(e)}")
            if self.config.primary_provider == StorageProvider.GOOGLE_CLOUD:
                raise

    async def _initialize_local_storage(self):
        """Initialisation du stockage local"""
        try:
            os.makedirs(self.config.local_storage_path, exist_ok=True)
            self.logger.info(f"Local storage initialized at: {self.config.local_storage_path}")
            
        except Exception as e:
            self.logger.error(f"Local storage initialization failed: {str(e)}")
            raise

    def _start_background_tasks(self):
        """Démarre les tâches en arrière-plan"""
        # File cleanup task
        asyncio.create_task(self._cleanup_old_files())
        
        # Backup task
        if self.config.enable_cross_region_backup:
            asyncio.create_task(self._backup_files())
        
        # Optimization task
        asyncio.create_task(self._optimize_files())

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/storage/upload", response_model=UploadResponse)
        async def upload_file(
            file: UploadFile = File(...),
            uploaded_by: str = Form(...),
            access_level: AccessLevel = Form(AccessLevel.PRIVATE),
            storage_class: StorageClass = Form(StorageClass.STANDARD),
            folder: Optional[str] = Form(None),
            tags: str = Form("[]"),  # JSON string
            background_tasks: BackgroundTasks = None
        ):
            """Upload d'un fichier"""
            start_time = time.time()
            
            try:
                # Validation
                await self._validate_file_upload(file)
                
                # Parse tags
                parsed_tags = json.loads(tags) if tags else []
                
                # Générer ID unique
                file_id = f"{int(time.time())}_{secrets.token_hex(8)}"
                
                # Calculer checksums
                content = await file.read()
                await file.seek(0)  # Reset pour upload
                
                md5_hash = hashlib.md5(content).hexdigest()
                sha256_hash = hashlib.sha256(content).hexdigest()
                
                # Détecter type de fichier
                file_type = self._detect_file_type(file.content_type, file.filename)
                
                # Générer path de stockage
                storage_path = self._generate_storage_path(file_id, file.filename, folder)
                
                # Créer métadonnées
                metadata = FileMetadata(
                    file_id=file_id,
                    filename=file.filename,
                    original_filename=file.filename,
                    content_type=file.content_type,
                    file_size=file.size,
                    file_type=file_type,
                    storage_provider=self.config.primary_provider,
                    storage_path=storage_path,
                    access_level=access_level,
                    storage_class=storage_class,
                    uploaded_by=uploaded_by,
                    uploaded_at=datetime.utcnow(),
                    checksum_md5=md5_hash,
                    checksum_sha256=sha256_hash
                )
                
                # Upload vers le provider principal
                upload_result = await self._upload_to_provider(
                    self.config.primary_provider, 
                    storage_path, 
                    content, 
                    metadata
                )
                
                if not upload_result:
                    raise HTTPException(status_code=500, detail="Upload failed")
                
                # Stocker métadonnées
                await self._store_file_metadata(file_id, metadata)
                
                # Tâches en arrière-plan
                if background_tasks:
                    # Génération de thumbnails/optimisation
                    if file_type in [FileType.IMAGE, FileType.VIDEO]:
                        background_tasks.add_task(self._optimize_media_file, file_id, content)
                    
                    # Virus scanning
                    if self.config.enable_virus_scanning:
                        background_tasks.add_task(self._scan_file_for_viruses, file_id, content)
                    
                    # Backup si activé
                    if self.config.enable_cross_region_backup:
                        background_tasks.add_task(self._backup_file, file_id)
                
                # Métriques
                upload_time = time.time() - start_time
                
                self.upload_requests.labels(
                    provider=self.config.primary_provider.value,
                    file_type=file_type.value,
                    status="success"
                ).inc()
                
                self.file_size_histogram.labels(file_type=file_type.value).observe(file.size)
                self.upload_duration.labels(
                    provider=self.config.primary_provider.value,
                    file_type=file_type.value
                ).observe(upload_time)
                
                # Générer URL de téléchargement
                download_url = await self._generate_download_url(file_id, access_level)
                
                return UploadResponse(
                    file_id=file_id,
                    download_url=download_url,
                    metadata=metadata,
                    success=True
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.upload_requests.labels(
                    provider=self.config.primary_provider.value,
                    file_type="unknown",
                    status="error"
                ).inc()
                
                self.logger.error(f"Upload error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

        @self.app.get("/storage/download/{file_id}")
        async def download_file(file_id: str, thumbnail: bool = False):
            """Téléchargement d'un fichier"""
            try:
                # Récupérer métadonnées
                metadata = await self._get_file_metadata(file_id)
                if not metadata:
                    raise HTTPException(status_code=404, detail="File not found")
                
                # Vérifier permissions d'accès
                # TODO: Implémenter vérification des permissions
                
                # Déterminer URL ou stream
                if thumbnail and metadata.optimized_versions.get("thumbnail"):
                    file_path = metadata.optimized_versions["thumbnail"]
                else:
                    file_path = metadata.storage_path
                
                # CDN redirect si disponible
                if self.config.enable_cdn and metadata.cdn_urls.get("default"):
                    self.download_requests.labels(
                        provider="cdn",
                        access_type="redirect"
                    ).inc()
                    return RedirectResponse(metadata.cdn_urls["default"])
                
                # Stream depuis le provider
                file_stream = await self._get_file_stream(
                    metadata.storage_provider, 
                    file_path
                )
                
                if not file_stream:
                    raise HTTPException(status_code=404, detail="File not accessible")
                
                # Mettre à jour stats d'accès
                await self._update_access_stats(file_id)
                
                self.download_requests.labels(
                    provider=metadata.storage_provider.value,
                    access_type="stream"
                ).inc()
                
                # Retourner stream
                return StreamingResponse(
                    file_stream,
                    media_type=metadata.content_type,
                    headers={
                        "Content-Disposition": f"attachment; filename={metadata.filename}",
                        "Content-Length": str(metadata.file_size),
                        "ETag": metadata.checksum_md5
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Download error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

        @self.app.delete("/storage/delete/{file_id}")
        async def delete_file(file_id: str, permanent: bool = False):
            """Supprimer un fichier"""
            try:
                # Récupérer métadonnées
                metadata = await self._get_file_metadata(file_id)
                if not metadata:
                    raise HTTPException(status_code=404, detail="File not found")
                
                # Supprimer du provider
                success = await self._delete_from_provider(
                    metadata.storage_provider,
                    metadata.storage_path,
                    permanent
                )
                
                if success:
                    # Supprimer métadonnées
                    await self._remove_file_metadata(file_id)
                    
                    # Invalider cache CDN
                    if self.config.enable_cdn:
                        await self._invalidate_cdn_cache(metadata.cdn_urls.values())
                    
                    self.storage_operations.labels(
                        provider=metadata.storage_provider.value,
                        operation="delete"
                    ).inc()
                
                return {
                    "success": success,
                    "file_id": file_id,
                    "permanent": permanent
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Delete error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

        @self.app.get("/storage/metadata/{file_id}", response_model=FileMetadata)
        async def get_file_metadata(file_id: str):
            """Récupérer métadonnées d'un fichier"""
            try:
                metadata = await self._get_file_metadata(file_id)
                if not metadata:
                    raise HTTPException(status_code=404, detail="File not found")
                
                return metadata
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Metadata retrieval error: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve metadata")

        @self.app.post("/storage/signed-url")
        async def generate_signed_url(
            file_id: str,
            expiry_hours: int = None,
            access_type: str = "download"
        ):
            """Générer URL signée pour accès temporaire"""
            try:
                metadata = await self._get_file_metadata(file_id)
                if not metadata:
                    raise HTTPException(status_code=404, detail="File not found")
                
                expiry = expiry_hours or self.config.signed_url_expiry_hours
                
                signed_url = await self._generate_signed_url(
                    metadata.storage_provider,
                    metadata.storage_path,
                    expiry_hours=expiry,
                    access_type=access_type
                )
                
                return {
                    "signed_url": signed_url,
                    "expires_in_hours": expiry,
                    "file_id": file_id
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Signed URL generation error: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to generate signed URL")

        @self.app.get("/storage/health")
        async def get_storage_health():
            """Health check du service de stockage"""
            try:
                health_status = {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "providers": {},
                    "metrics": {
                        "total_files": len(self.file_metadata),
                        "total_size_gb": sum(f.file_size for f in self.file_metadata.values()) / 1024 / 1024 / 1024
                    }
                }
                
                # Test providers
                for provider in [self.config.primary_provider, self.config.fallback_provider]:
                    if provider:
                        try:
                            health = await self._test_provider_health(provider)
                            health_status["providers"][provider.value] = health
                        except Exception as e:
                            health_status["providers"][provider.value] = {
                                "status": "unhealthy",
                                "error": str(e)
                            }
                
                return health_status
                
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _validate_file_upload(self, file: UploadFile):
        """Valider upload de fichier"""
        # Vérifier taille
        if file.size > self.config.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {self.config.max_file_size_mb}MB"
            )
        
        # Vérifier extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in self.config.allowed_extensions:
            raise HTTPException(
                status_code=415,
                detail=f"File type not allowed. Allowed extensions: {self.config.allowed_extensions}"
            )

    def _detect_file_type(self, content_type: str, filename: str) -> FileType:
        """Détecter le type de fichier"""
        if content_type.startswith("image/"):
            return FileType.IMAGE
        elif content_type.startswith("video/"):
            return FileType.VIDEO
        elif content_type.startswith("audio/"):
            return FileType.AUDIO
        elif content_type in ["application/pdf", "text/plain", "application/msword"]:
            return FileType.DOCUMENT
        elif content_type in ["application/zip", "application/x-rar"]:
            return FileType.ARCHIVE
        else:
            return FileType.OTHER

    def _generate_storage_path(self, file_id: str, filename: str, folder: Optional[str]) -> str:
        """Générer chemin de stockage"""
        # Structure: year/month/day/folder/file_id_filename
        now = datetime.utcnow()
        date_path = f"{now.year:04d}/{now.month:02d}/{now.day:02d}"
        
        if folder:
            folder_path = f"{date_path}/{folder}"
        else:
            folder_path = date_path
        
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        return f"{folder_path}/{file_id}_{safe_filename}"

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_file_storage_service(config: StorageConfig = None) -> FastAPI:
    """
    Factory pour créer service de stockage de fichiers
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    storage_service = FileStorageTemplate(config)
    return storage_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = StorageConfig(
        primary_provider=StorageProvider.AWS_S3,
        enable_cdn=True,
        enable_image_optimization=True,
        enable_virus_scanning=True
    )
    
    app = create_file_storage_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )