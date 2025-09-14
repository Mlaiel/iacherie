"""
📁 Content Upload Microservice
Advanced multi-format content upload and validation service

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import uuid
import hashlib
import mimetypes
import logging
from abc import ABC, abstractmethod
import io
import json

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Supported content types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    MIXED = "mixed"


class ContentFormat(str, Enum):
    """Supported content formats"""
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    MKV = "mkv"
    WEBM = "webm"
    
    # Image formats
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    SVG = "svg"
    WEBP = "webp"
    
    # Text formats
    TXT = "txt"
    MD = "md"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    
    # Document formats
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    RTF = "rtf"
    
    # Archive formats
    ZIP = "zip"
    RAR = "rar"
    TAR = "tar"
    GZ = "gz"


class UploadStatus(str, Enum):
    """Upload status states"""
    INITIATED = "initiated"
    UPLOADING = "uploading"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"


class ValidationResult(BaseModel):
    """Content validation result"""
    is_valid: bool = Field(..., description="Whether content passed validation")
    validation_score: float = Field(..., ge=0, le=1, description="Validation confidence score")
    issues: List[str] = Field(default_factory=list, description="Validation issues found")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extracted metadata")
    file_info: Dict[str, Any] = Field(default_factory=dict, description="File information")
    security_scan: Dict[str, Any] = Field(default_factory=dict, description="Security scan results")


class ContentMetadata(BaseModel):
    """Content metadata model"""
    content_id: str = Field(..., description="Unique content identifier")
    original_filename: str = Field(..., description="Original filename")
    content_type: ContentType = Field(..., description="Content type")
    content_format: ContentFormat = Field(..., description="Content format")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")
    content_hash: str = Field(..., description="Content hash for integrity")
    mime_type: str = Field(..., description="MIME type")
    duration_seconds: Optional[float] = Field(None, description="Duration for audio/video")
    dimensions: Optional[Dict[str, int]] = Field(None, description="Width/height for images/video")
    resolution: Optional[str] = Field(None, description="Resolution string")
    bit_rate: Optional[int] = Field(None, description="Bit rate for audio/video")
    frame_rate: Optional[float] = Field(None, description="Frame rate for video")
    color_depth: Optional[int] = Field(None, description="Color depth for images")
    encoding: Optional[str] = Field(None, description="Text encoding")
    language: Optional[str] = Field(None, description="Content language")
    title: Optional[str] = Field(None, description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = Field(None, description="Last modification time")


class UploadChunk(BaseModel):
    """Upload chunk data model"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    upload_id: str = Field(..., description="Parent upload identifier")
    chunk_index: int = Field(..., ge=0, description="Chunk sequence number")
    chunk_size: int = Field(..., ge=1, description="Chunk size in bytes")
    chunk_hash: str = Field(..., description="Chunk data hash")
    data: bytes = Field(..., description="Chunk binary data")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class ContentUpload(BaseModel):
    """Content upload model"""
    upload_id: str = Field(..., description="Unique upload identifier")
    creator_id: str = Field(..., description="Creator identifier")
    session_id: str = Field(..., description="Upload session identifier")
    original_filename: str = Field(..., description="Original filename")
    expected_size: int = Field(..., ge=0, description="Expected total file size")
    uploaded_size: int = Field(default=0, ge=0, description="Currently uploaded size")
    content_type: ContentType = Field(..., description="Content type")
    content_format: ContentFormat = Field(..., description="Content format")
    status: UploadStatus = Field(default=UploadStatus.INITIATED)
    chunks: List[UploadChunk] = Field(default_factory=list, description="Upload chunks")
    metadata: Optional[ContentMetadata] = Field(None, description="Content metadata")
    validation_result: Optional[ValidationResult] = Field(None, description="Validation result")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Upload completion time")
    expires_at: datetime = Field(..., description="Upload session expiry")
    storage_location: Optional[str] = Field(None, description="Final storage location")


class UploadRequest(BaseModel):
    """Content upload request"""
    creator_id: str = Field(..., description="Creator identifier")
    filename: str = Field(..., description="File name")
    file_size: int = Field(..., ge=1, description="File size in bytes")
    content_type: Optional[ContentType] = Field(None, description="Content type hint")
    chunk_size: int = Field(default=1048576, ge=65536, le=10485760, description="Chunk size in bytes")  # 1MB default
    metadata_hints: Dict[str, Any] = Field(default_factory=dict, description="Metadata hints")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    privacy_level: str = Field(default="private", description="Content privacy level")
    license_type: Optional[str] = Field(None, description="Content license type")


class UploadResponse(BaseModel):
    """Upload response"""
    success: bool = Field(..., description="Operation success status")
    upload_id: Optional[str] = Field(None, description="Upload identifier")
    session_id: Optional[str] = Field(None, description="Upload session identifier")
    upload_url: Optional[str] = Field(None, description="Upload endpoint URL")
    chunk_urls: List[str] = Field(default_factory=list, description="Chunk upload URLs")
    expires_in: Optional[int] = Field(None, description="Session expiry in seconds")
    max_chunk_size: Optional[int] = Field(None, description="Maximum chunk size")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    validation_requirements: Dict[str, Any] = Field(default_factory=dict, description="Validation requirements")


class ContentValidator:
    """Content validation engine"""
    
    def __init__(self) -> None:
        self.max_file_sizes = {
            ContentType.AUDIO: 100 * 1024 * 1024,      # 100MB
            ContentType.VIDEO: 2 * 1024 * 1024 * 1024,  # 2GB
            ContentType.IMAGE: 50 * 1024 * 1024,        # 50MB
            ContentType.TEXT: 10 * 1024 * 1024,         # 10MB
            ContentType.DOCUMENT: 100 * 1024 * 1024,    # 100MB
            ContentType.ARCHIVE: 500 * 1024 * 1024,     # 500MB
        }
        
        self.allowed_mime_types = {
            ContentType.AUDIO: [
                "audio/mpeg", "audio/wav", "audio/flac", "audio/aac",
                "audio/ogg", "audio/mp4", "audio/x-m4a"
            ],
            ContentType.VIDEO: [
                "video/mp4", "video/avi", "video/quicktime", "video/x-msvideo",
                "video/x-flv", "video/x-matroska", "video/webm"
            ],
            ContentType.IMAGE: [
                "image/jpeg", "image/png", "image/gif", "image/bmp",
                "image/tiff", "image/svg+xml", "image/webp"
            ],
            ContentType.TEXT: [
                "text/plain", "text/markdown", "text/html",
                "application/json", "application/xml"
            ],
            ContentType.DOCUMENT: [
                "application/pdf", "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/rtf"
            ]
        }
    
    async def validate_content(
        self, 
        content_data: bytes, 
        metadata: ContentMetadata,
        validation_level: str = "standard"
    ) -> ValidationResult:
        """Comprehensive content validation"""
        
        issues = []
        warnings = []
        security_scan = {}
        
        try:
            # File size validation
            if metadata.file_size_bytes > self.max_file_sizes.get(metadata.content_type, 0):
                issues.append(f"File size exceeds maximum allowed for {metadata.content_type}")
            
            # MIME type validation
            allowed_mimes = self.allowed_mime_types.get(metadata.content_type, [])
            if metadata.mime_type not in allowed_mimes:
                issues.append(f"Unsupported MIME type: {metadata.mime_type}")
            
            # Content integrity validation
            calculated_hash = hashlib.sha256(content_data).hexdigest()
            if calculated_hash != metadata.content_hash:
                issues.append("Content hash mismatch - file may be corrupted")
            
            # Security scanning
            security_scan = await self._security_scan(content_data, metadata)
            if security_scan.get("threats_detected", 0) > 0:
                issues.extend(security_scan.get("threat_details", []))
            
            # Format-specific validation
            format_validation = await self._validate_format_specific(content_data, metadata)
            issues.extend(format_validation.get("issues", []))
            warnings.extend(format_validation.get("warnings", []))
            
            # Content quality assessment
            quality_assessment = await self._assess_content_quality(content_data, metadata)
            if quality_assessment.get("quality_score", 1.0) < 0.5:
                warnings.append("Content quality is below recommended standards")
            
            # Calculate validation score
            validation_score = self._calculate_validation_score(issues, warnings, security_scan)
            
            return ValidationResult(
                is_valid=len(issues) == 0,
                validation_score=validation_score,
                issues=issues,
                warnings=warnings,
                metadata=metadata.dict(),
                file_info={
                    "size_mb": round(metadata.file_size_bytes / (1024 * 1024), 2),
                    "type": metadata.content_type,
                    "format": metadata.content_format,
                    "mime": metadata.mime_type
                },
                security_scan=security_scan
            )
            
        except Exception as e:
            logger.error(f"Content validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                validation_score=0.0,
                issues=[f"Validation error: {str(e)}"],
                warnings=[],
                metadata={},
                file_info={},
                security_scan={"error": str(e)}
            )
    
    async def _security_scan(self, content_data: bytes, metadata: ContentMetadata) -> Dict[str, Any]:
        """Security scanning for malicious content"""
        
        scan_result = {
            "scan_completed": True,
            "threats_detected": 0,
            "threat_details": [],
            "scan_time_ms": 100,  # Simulated
            "scanner_version": "1.0.0"
        }
        
        # Check for suspicious patterns (simplified)
        suspicious_patterns = [
            b"<script", b"javascript:", b"vbscript:",
            b"eval(", b"exec(", b"system(",
            b"\x4d\x5a",  # PE executable header
            b"\x7f\x45\x4c\x46"  # ELF executable header
        ]
        
        for pattern in suspicious_patterns:
            if pattern in content_data:
                scan_result["threats_detected"] += 1
                scan_result["threat_details"].append(f"Suspicious pattern detected: {pattern}")
        
        # File header analysis
        if len(content_data) >= 4:
            header = content_data[:4]
            if header in [b"\x50\x4b\x03\x04", b"\x50\x4b\x05\x06"]:  # ZIP headers
                if metadata.content_format not in [ContentFormat.ZIP]:
                    scan_result["threats_detected"] += 1
                    scan_result["threat_details"].append("File header mismatch detected")
        
        return scan_result
    
    async def _validate_format_specific(
        self, 
        content_data: bytes, 
        metadata: ContentMetadata
    ) -> Dict[str, Any]:
        """Format-specific validation"""
        
        issues = []
        warnings = []
        
        if metadata.content_type == ContentType.AUDIO:
            # Audio-specific validation
            if metadata.duration_seconds and metadata.duration_seconds < 1:
                warnings.append("Audio duration is very short")
            if metadata.bit_rate and metadata.bit_rate < 64000:
                warnings.append("Audio bit rate is low, quality may be poor")
                
        elif metadata.content_type == ContentType.VIDEO:
            # Video-specific validation
            if metadata.duration_seconds and metadata.duration_seconds < 1:
                warnings.append("Video duration is very short")
            if metadata.dimensions:
                width = metadata.dimensions.get("width", 0)
                height = metadata.dimensions.get("height", 0)
                if width < 240 or height < 240:
                    warnings.append("Video resolution is very low")
                    
        elif metadata.content_type == ContentType.IMAGE:
            # Image-specific validation
            if metadata.dimensions:
                width = metadata.dimensions.get("width", 0)
                height = metadata.dimensions.get("height", 0)
                if width < 100 or height < 100:
                    warnings.append("Image resolution is very low")
                if width > 10000 or height > 10000:
                    warnings.append("Image resolution is extremely high")
        
        return {"issues": issues, "warnings": warnings}
    
    async def _assess_content_quality(
        self, 
        content_data: bytes, 
        metadata: ContentMetadata
    ) -> Dict[str, Any]:
        """Assess content quality"""
        
        quality_score = 1.0
        quality_factors = []
        
        # File size to quality ratio
        size_mb = metadata.file_size_bytes / (1024 * 1024)
        
        if metadata.content_type == ContentType.AUDIO:
            if metadata.duration_seconds and metadata.duration_seconds > 0:
                bitrate_estimate = (metadata.file_size_bytes * 8) / metadata.duration_seconds / 1000
                if bitrate_estimate < 128:
                    quality_score *= 0.7
                    quality_factors.append("Low estimated bitrate")
                elif bitrate_estimate > 320:
                    quality_factors.append("High quality audio")
                    
        elif metadata.content_type == ContentType.IMAGE:
            if metadata.dimensions:
                pixel_count = metadata.dimensions.get("width", 0) * metadata.dimensions.get("height", 0)
                if pixel_count > 0:
                    bytes_per_pixel = metadata.file_size_bytes / pixel_count
                    if bytes_per_pixel < 0.1:
                        quality_score *= 0.8
                        quality_factors.append("Low compression quality")
        
        return {
            "quality_score": quality_score,
            "quality_factors": quality_factors
        }
    
    def _calculate_validation_score(
        self, 
        issues: List[str], 
        warnings: List[str], 
        security_scan: Dict[str, Any]
    ) -> float:
        """Calculate overall validation score"""
        
        base_score = 1.0
        
        # Deduct for issues
        base_score -= len(issues) * 0.3
        
        # Deduct for warnings
        base_score -= len(warnings) * 0.1
        
        # Deduct for security threats
        threats = security_scan.get("threats_detected", 0)
        base_score -= threats * 0.5
        
        return max(0.0, base_score)


class ChunkedUploadManager:
    """Manages chunked file uploads"""
    
    def __init__(self) -> None:
        self.active_uploads: Dict[str, ContentUpload] = {}
        self.chunk_storage: Dict[str, bytes] = {}  # In production, use cloud storage
    
    async def initiate_upload(self, request: UploadRequest) -> UploadResponse:
        """Initiate a new chunked upload"""
        
        try:
            # Generate unique identifiers
            upload_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            # Determine content type from filename if not provided
            content_type = request.content_type
            if not content_type:
                content_type = self._detect_content_type(request.filename)
            
            # Determine content format
            content_format = self._detect_content_format(request.filename)
            
            # Create upload record
            upload = ContentUpload(
                upload_id=upload_id,
                creator_id=request.creator_id,
                session_id=session_id,
                original_filename=request.filename,
                expected_size=request.file_size,
                content_type=content_type,
                content_format=content_format,
                expires_at=datetime.utcnow() + timedelta(hours=24)  # 24-hour expiry
            )
            
            # Store upload record
            self.active_uploads[upload_id] = upload
            
            # Generate chunk URLs
            chunk_count = (request.file_size + request.chunk_size - 1) // request.chunk_size
            chunk_urls = [
                f"/upload/{upload_id}/chunk/{i}" 
                for i in range(chunk_count)
            ]
            
            logger.info(f"Initiated upload {upload_id} for creator {request.creator_id}")
            
            return UploadResponse(
                success=True,
                upload_id=upload_id,
                session_id=session_id,
                upload_url=f"/upload/{upload_id}",
                chunk_urls=chunk_urls,
                expires_in=86400,  # 24 hours
                max_chunk_size=10485760,  # 10MB
                validation_requirements={
                    "max_file_size": 2 * 1024 * 1024 * 1024,  # 2GB
                    "allowed_formats": [fmt.value for fmt in ContentFormat]
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to initiate upload: {str(e)}")
            return UploadResponse(
                success=False,
                error_message=f"Upload initiation failed: {str(e)}"
            )
    
    async def upload_chunk(
        self, 
        upload_id: str, 
        chunk_index: int, 
        chunk_data: bytes
    ) -> bool:
        """Upload a file chunk"""
        
        if upload_id not in self.active_uploads:
            return False
        
        upload = self.active_uploads[upload_id]
        
        # Check if upload is still valid
        if datetime.utcnow() > upload.expires_at:
            upload.status = UploadStatus.FAILED
            upload.error_message = "Upload session expired"
            return False
        
        # Create chunk record
        chunk_id = f"{upload_id}_{chunk_index}"
        chunk = UploadChunk(
            chunk_id=chunk_id,
            upload_id=upload_id,
            chunk_index=chunk_index,
            chunk_size=len(chunk_data),
            chunk_hash=hashlib.sha256(chunk_data).hexdigest(),
            data=chunk_data
        )
        
        # Store chunk data
        self.chunk_storage[chunk_id] = chunk_data
        upload.chunks.append(chunk)
        upload.uploaded_size += len(chunk_data)
        upload.status = UploadStatus.UPLOADING
        
        logger.debug(f"Uploaded chunk {chunk_index} for upload {upload_id}")
        
        # Check if upload is complete
        if upload.uploaded_size >= upload.expected_size:
            await self._finalize_upload(upload_id)
        
        return True
    
    async def _finalize_upload(self, upload_id: str) -> bool:
        """Finalize and validate completed upload"""
        
        upload = self.active_uploads[upload_id]
        upload.status = UploadStatus.VALIDATING
        
        try:
            # Reconstruct file from chunks
            upload.chunks.sort(key=lambda c: c.chunk_index)
            file_data = b"".join([
                self.chunk_storage[chunk.chunk_id] 
                for chunk in upload.chunks
            ])
            
            # Create metadata
            content_hash = hashlib.sha256(file_data).hexdigest()
            mime_type, _ = mimetypes.guess_type(upload.original_filename)
            
            metadata = ContentMetadata(
                content_id=upload.upload_id,
                original_filename=upload.original_filename,
                content_type=upload.content_type,
                content_format=upload.content_format,
                file_size_bytes=len(file_data),
                content_hash=content_hash,
                mime_type=mime_type or "application/octet-stream"
            )
            
            # Validate content
            validator = ContentValidator()
            validation_result = await validator.validate_content(file_data, metadata)
            
            upload.metadata = metadata
            upload.validation_result = validation_result
            
            if validation_result.is_valid:
                upload.status = UploadStatus.COMPLETED
                upload.storage_location = f"storage/{upload.creator_id}/{upload_id}"
                logger.info(f"Upload {upload_id} completed successfully")
            else:
                upload.status = UploadStatus.REJECTED
                upload.error_message = f"Validation failed: {', '.join(validation_result.issues)}"
                logger.warning(f"Upload {upload_id} rejected: {upload.error_message}")
            
            upload.completed_at = datetime.utcnow()
            
            # Cleanup chunk storage
            for chunk in upload.chunks:
                if chunk.chunk_id in self.chunk_storage:
                    del self.chunk_storage[chunk.chunk_id]
            
            return True
            
        except Exception as e:
            upload.status = UploadStatus.FAILED
            upload.error_message = f"Finalization failed: {str(e)}"
            logger.error(f"Upload {upload_id} finalization failed: {str(e)}")
            return False
    
    async def get_upload_status(self, upload_id: str) -> Optional[ContentUpload]:
        """Get upload status"""
        return self.active_uploads.get(upload_id)
    
    async def cancel_upload(self, upload_id: str) -> bool:
        """Cancel an ongoing upload"""
        if upload_id not in self.active_uploads:
            return False
        
        upload = self.active_uploads[upload_id]
        upload.status = UploadStatus.FAILED
        upload.error_message = "Upload cancelled by user"
        
        # Cleanup chunk storage
        for chunk in upload.chunks:
            if chunk.chunk_id in self.chunk_storage:
                del self.chunk_storage[chunk.chunk_id]
        
        logger.info(f"Upload {upload_id} cancelled")
        return True
    
    def _detect_content_type(self, filename: str) -> ContentType:
        """Detect content type from filename"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if extension in ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']:
            return ContentType.AUDIO
        elif extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm']:
            return ContentType.VIDEO
        elif extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg', 'webp']:
            return ContentType.IMAGE
        elif extension in ['txt', 'md', 'html', 'json', 'xml']:
            return ContentType.TEXT
        elif extension in ['pdf', 'doc', 'docx', 'rtf']:
            return ContentType.DOCUMENT
        elif extension in ['zip', 'rar', 'tar', 'gz']:
            return ContentType.ARCHIVE
        else:
            return ContentType.MIXED
    
    def _detect_content_format(self, filename: str) -> ContentFormat:
        """Detect content format from filename"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        # Map extensions to ContentFormat enum
        format_mapping = {
            'mp3': ContentFormat.MP3,
            'wav': ContentFormat.WAV,
            'flac': ContentFormat.FLAC,
            'aac': ContentFormat.AAC,
            'ogg': ContentFormat.OGG,
            'm4a': ContentFormat.M4A,
            'mp4': ContentFormat.MP4,
            'avi': ContentFormat.AVI,
            'mov': ContentFormat.MOV,
            'wmv': ContentFormat.WMV,
            'flv': ContentFormat.FLV,
            'mkv': ContentFormat.MKV,
            'webm': ContentFormat.WEBM,
            'jpg': ContentFormat.JPG,
            'jpeg': ContentFormat.JPEG,
            'png': ContentFormat.PNG,
            'gif': ContentFormat.GIF,
            'bmp': ContentFormat.BMP,
            'tiff': ContentFormat.TIFF,
            'svg': ContentFormat.SVG,
            'webp': ContentFormat.WEBP,
            'txt': ContentFormat.TXT,
            'md': ContentFormat.MD,
            'html': ContentFormat.HTML,
            'json': ContentFormat.JSON,
            'xml': ContentFormat.XML,
            'pdf': ContentFormat.PDF,
            'doc': ContentFormat.DOC,
            'docx': ContentFormat.DOCX,
            'rtf': ContentFormat.RTF,
            'zip': ContentFormat.ZIP,
            'rar': ContentFormat.RAR,
            'tar': ContentFormat.TAR,
            'gz': ContentFormat.GZ
        }
        
        return format_mapping.get(extension, ContentFormat.TXT)
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health metrics"""
        active_uploads = len(self.active_uploads)
        completed_uploads = sum(
            1 for upload in self.active_uploads.values()
            if upload.status == UploadStatus.COMPLETED
        )
        
        return {
            "service_status": "healthy",
            "active_uploads": active_uploads,
            "completed_uploads": completed_uploads,
            "success_rate": completed_uploads / active_uploads if active_uploads > 0 else 0,
            "supported_formats": [fmt.value for fmt in ContentFormat],
            "max_file_size_gb": 2,
            "chunk_storage_size": len(self.chunk_storage)
        }


# Export classes for external use
__all__ = [
    'ContentType',
    'ContentFormat',
    'UploadStatus',
    'ValidationResult',
    'ContentMetadata',
    'UploadChunk',
    'ContentUpload',
    'UploadRequest',
    'UploadResponse',
    'ContentValidator',
    'ChunkedUploadManager'
]