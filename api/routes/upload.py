"""Upload API Routes
Multi-format file upload and processing endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import os
import uuid
import mimetypes
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import aiofiles

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import magic

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...multimedia.processors.audio_processor import AudioProcessor
from ...multimedia.processors.video_processor import VideoProcessor
from ...multimedia.processors.image_processor import ImageProcessor
from ...multimedia.processors.text_processor import TextProcessor


# Configuration
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
UPLOAD_DIRECTORY = "/tmp/uploads"
PROCESSED_DIRECTORY = "/tmp/processed"

ALLOWED_EXTENSIONS = {
    'audio': ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma'],
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'],
    'text': ['.txt', '.pdf', '.docx', '.html', '.md', '.rtf']
}

MIME_TYPE_MAPPING = {
    'audio': ['audio/', 'application/ogg'],
    'video': ['video/'],
    'image': ['image/'],
    'text': ['text/', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
}


# Pydantic models
class UploadMetadata(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default=[])
    genre: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    privacy_level: str = Field(default="private", regex="^(public|private|unlisted)$")
    enable_protection: bool = Field(default=True)
    auto_fingerprint: bool = Field(default=True)
    custom_metadata: Optional[Dict[str, Any]] = None


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: str
    file_size: int
    status: str
    upload_url: Optional[str] = None
    processing_status: str
    metadata: Dict[str, Any]
    created_at: datetime


class ProcessingStatus(BaseModel):
    file_id: str
    status: str = Field(..., regex="^(pending|processing|completed|failed)$")
    progress: float = Field(..., ge=0.0, le=100.0)
    current_step: str
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


class BatchUploadRequest(BaseModel):
    files: List[str]  # File IDs from individual uploads
    batch_metadata: UploadMetadata
    processing_options: Dict[str, Any] = Field(default={})


class ConversionRequest(BaseModel):
    file_id: str
    target_format: str
    quality_settings: Optional[Dict[str, Any]] = None
    processing_options: Optional[Dict[str, Any]] = None


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize processors
audio_processor = AudioProcessor()
video_processor = VideoProcessor()
image_processor = ImageProcessor()
text_processor = TextProcessor()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


def detect_content_type(file_content: bytes, filename: str) -> str:
    """Detect content type using file magic and extension"""    try:
        # Use python-magic for MIME type detection
        mime_type = magic.from_buffer(file_content, mime=True)
        
        # Map MIME type to our content types
        for content_type, mime_prefixes in MIME_TYPE_MAPPING.items():
            for prefix in mime_prefixes:
                if mime_type.startswith(prefix):
                    return content_type
        
        # Fallback to file extension
        file_extension = os.path.splitext(filename)[1].lower()
        for content_type, extensions in ALLOWED_EXTENSIONS.items():
            if file_extension in extensions:
                return content_type
                
        return "unknown"
        
    except Exception as e:
        logger.warning(f"Content type detection failed: {e}")
        return "unknown"


def validate_file(file_content: bytes, filename: str, content_type: str) -> Dict[str, Any]:
    """Validate uploaded file"""    errors = []
    
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        errors.append(f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024):.0f}MB")
    
    # Check file extension
    file_extension = os.path.splitext(filename)[1].lower()
    if content_type in ALLOWED_EXTENSIONS:
        if file_extension not in ALLOWED_EXTENSIONS[content_type]:
            errors.append(f"File extension {file_extension} not allowed for {content_type}")
    
    # Check for malicious content (basic check)
    if b'<script' in file_content.lower() or b'javascript:' in file_content.lower():
        errors.append("File contains potentially malicious content")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "file_size": len(file_content),
        "content_type": content_type,
        "file_extension": file_extension
    }


@router.post("/single", response_model=UploadResponse)
async def upload_single_file(
    file: UploadFile = File(...),
    metadata: str = Form(default="{}"),
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Upload a single file with metadata"""    try:
        # Parse metadata
        import json
        try:
            metadata_dict = json.loads(metadata)
            upload_metadata = UploadMetadata(**metadata_dict)
        except (json.JSONDecodeError, ValueError) as e:
            upload_metadata = UploadMetadata()
        
        # Read file content
        file_content = await file.read()
        
        # Detect content type
        content_type = detect_content_type(file_content, file.filename)
        
        # Validate file
        validation_result = validate_file(file_content, file.filename, content_type)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File validation failed: {', '.join(validation_result['errors'])}"
            )
        
        # Generate unique file ID and paths
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        original_filename = f"{file_id}_original{file_extension}"
        file_path = os.path.join(UPLOAD_DIRECTORY, original_filename)
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Create database record
        file_metadata = {
            "original_filename": file.filename,
            "title": upload_metadata.title or file.filename,
            "description": upload_metadata.description,
            "tags": upload_metadata.tags,
            "genre": upload_metadata.genre,
            "artist": upload_metadata.artist,
            "album": upload_metadata.album,
            "privacy_level": upload_metadata.privacy_level,
            "enable_protection": upload_metadata.enable_protection,
            "auto_fingerprint": upload_metadata.auto_fingerprint,
            "custom_metadata": upload_metadata.custom_metadata or {}
        }
        
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO uploaded_files (file_id, user_id, original_filename, stored_filename,
                                          file_path, content_type, file_size, status,
                                          metadata, upload_timestamp, processing_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                file_id, user['user_id'], file.filename, original_filename,
                file_path, content_type, len(file_content), "uploaded",
                file_metadata, datetime.utcnow(), "pending"
            ))
            await session.commit()
        
        # Schedule background processing
        if upload_metadata.auto_fingerprint or content_type in ['audio', 'video']:
            background_tasks.add_task(
                _process_uploaded_file, file_id, file_path, content_type, upload_metadata
            )
        
        logger.info(f"File uploaded: {file_id} ({content_type}) by user {user['user_id']}")
        
        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            content_type=content_type,
            file_size=len(file_content),
            status="uploaded",
            processing_status="pending" if upload_metadata.auto_fingerprint else "none",
            metadata=file_metadata,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )


@router.post("/multiple", response_model=List[UploadResponse])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    metadata: str = Form(default="{}"),
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Upload multiple files with shared metadata"""    try:
        if len(files) > 20:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 files allowed per batch upload"
            )
        
        # Parse metadata
        import json
        try:
            metadata_dict = json.loads(metadata)
            upload_metadata = UploadMetadata(**metadata_dict)
        except (json.JSONDecodeError, ValueError):
            upload_metadata = UploadMetadata()
        
        upload_results = []
        
        for file in files:
            try:
                # Process each file similar to single upload
                file_content = await file.read()
                content_type = detect_content_type(file_content, file.filename)
                
                # Validate file
                validation_result = validate_file(file_content, file.filename, content_type)
                if not validation_result["valid"]:
                    logger.warning(f"File validation failed for {file.filename}: {validation_result['errors']}")
                    continue
                
                # Generate unique file ID and paths
                file_id = str(uuid.uuid4())
                file_extension = os.path.splitext(file.filename)[1].lower()
                original_filename = f"{file_id}_original{file_extension}"
                file_path = os.path.join(UPLOAD_DIRECTORY, original_filename)
                
                # Save file
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(file_content)
                
                # Create database record
                file_metadata = {
                    "original_filename": file.filename,
                    "title": upload_metadata.title or file.filename,
                    "description": upload_metadata.description,
                    "tags": upload_metadata.tags,
                    "genre": upload_metadata.genre,
                    "artist": upload_metadata.artist,
                    "album": upload_metadata.album,
                    "privacy_level": upload_metadata.privacy_level,
                    "enable_protection": upload_metadata.enable_protection,
                    "auto_fingerprint": upload_metadata.auto_fingerprint,
                    "custom_metadata": upload_metadata.custom_metadata or {}
                }
                
                async with database_manager.get_postgres_session() as session:
                    await session.execute("""                        INSERT INTO uploaded_files (file_id, user_id, original_filename, stored_filename,
                                                  file_path, content_type, file_size, status,
                                                  metadata, upload_timestamp, processing_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        file_id, user['user_id'], file.filename, original_filename,
                        file_path, content_type, len(file_content), "uploaded",
                        file_metadata, datetime.utcnow(), "pending"
                    ))
                    await session.commit()
                
                # Schedule background processing
                if upload_metadata.auto_fingerprint or content_type in ['audio', 'video']:
                    background_tasks.add_task(
                        _process_uploaded_file, file_id, file_path, content_type, upload_metadata
                    )
                
                upload_results.append(UploadResponse(
                    file_id=file_id,
                    filename=file.filename,
                    content_type=content_type,
                    file_size=len(file_content),
                    status="uploaded",
                    processing_status="pending" if upload_metadata.auto_fingerprint else "none",
                    metadata=file_metadata,
                    created_at=datetime.utcnow()
                ))
                
            except Exception as e:
                logger.error(f"Failed to process file {file.filename}: {e}")
                continue
        
        logger.info(f"Batch upload completed: {len(upload_results)} files uploaded by user {user['user_id']}")
        
        return upload_results
        
    except Exception as e:
        logger.error(f"Batch upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch upload failed"
        )


@router.get("/status/{file_id}", response_model=ProcessingStatus)
async def get_processing_status(
    file_id: str,
    user: dict = Depends(get_current_user)
):
    """Get file processing status"""    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT processing_status, processing_progress, processing_step,
                       processing_error, processing_results, updated_at
                FROM uploaded_files
                WHERE file_id = %s AND user_id = %s
            """, (file_id, user['user_id']))
            
            file_info = result.fetchone()
            if not file_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found or access denied"
                )
        
        status_info = ProcessingStatus(
            file_id=file_id,
            status=file_info[0] or "pending",
            progress=file_info[1] or 0.0,
            current_step=file_info[2] or "queued",
            error_message=file_info[3],
            results=file_info[4]
        )
        
        return status_info
        
    except Exception as e:
        logger.error(f"Get processing status failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get processing status"
        )


@router.post("/convert", response_model=Dict[str, str])
async def convert_file_format(
    conversion_request: ConversionRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Convert file to different format"""    try:
        # Verify file ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT file_path, content_type, original_filename
                FROM uploaded_files
                WHERE file_id = %s AND user_id = %s
            """, (conversion_request.file_id, user['user_id']))
            
            file_info = result.fetchone()
            if not file_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found or access denied"
                )
        
        file_path, content_type, original_filename = file_info
        
        # Validate conversion
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source file not found"
            )
        
        conversion_id = str(uuid.uuid4())
        
        # Create conversion job
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                INSERT INTO file_conversions (conversion_id, file_id, user_id, source_format,
                                            target_format, quality_settings, processing_options,
                                            status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                conversion_id, conversion_request.file_id, user['user_id'], content_type,
                conversion_request.target_format, conversion_request.quality_settings,
                conversion_request.processing_options, "queued", datetime.utcnow()
            ))
            await session.commit()
        
        # Schedule conversion
        background_tasks.add_task(
            _process_file_conversion, conversion_id, conversion_request, file_path, content_type
        )
        
        logger.info(f"File conversion queued: {conversion_id}")
        
        return {
            "conversion_id": conversion_id,
            "status": "queued",
            "message": "File conversion queued successfully"
        }
        
    except Exception as e:
        logger.error(f"File conversion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue file conversion"
        )


@router.get("/list", response_model=List[Dict[str, Any]])
async def list_uploaded_files(
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Field(default=50, ge=1, le=100),
    offset: int = Field(default=0, ge=0),
    user: dict = Depends(get_current_user)
):
    """List user's uploaded files"""    try:
        query = """            SELECT file_id, original_filename, content_type, file_size, status,
                   metadata, upload_timestamp, processing_status, processing_progress
            FROM uploaded_files
            WHERE user_id = %s
        """        params = [user['user_id']]
        
        if content_type:
            query += " AND content_type = %s"
            params.append(content_type)
        
        if status:
            query += " AND status = %s"
            params.append(status)
            
        query += " ORDER BY upload_timestamp DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            files = result.fetchall()
        
        file_list = []
        for file_info in files:
            file_list.append({
                "file_id": file_info[0],
                "filename": file_info[1],
                "content_type": file_info[2],
                "file_size": file_info[3],
                "status": file_info[4],
                "metadata": file_info[5],
                "upload_timestamp": file_info[6],
                "processing_status": file_info[7],
                "processing_progress": file_info[8]
            })
        
        return file_list
        
    except Exception as e:
        logger.error(f"List uploaded files failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list uploaded files"
        )


@router.delete("/{file_id}")
async def delete_uploaded_file(
    file_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete an uploaded file"""    try:
        async with database_manager.get_postgres_session() as session:
            # Get file info
            result = await session.execute("""                SELECT file_path, stored_filename
                FROM uploaded_files
                WHERE file_id = %s AND user_id = %s
            """, (file_id, user['user_id']))
            
            file_info = result.fetchone()
            if not file_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found or access denied"
                )
            
            file_path, stored_filename = file_info
            
            # Delete from database
            await session.execute("""                DELETE FROM uploaded_files WHERE file_id = %s
            """, (file_id,))
            await session.commit()
        
        # Delete physical file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete processed versions
            processed_dir = os.path.join(PROCESSED_DIRECTORY, file_id)
            if os.path.exists(processed_dir):
                import shutil
                shutil.rmtree(processed_dir)
                
        except Exception as e:
            logger.warning(f"Failed to delete physical file {file_path}: {e}")
        
        logger.info(f"File deleted: {file_id}")
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete file failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    version: str = Field(default="original", regex="^(original|processed|compressed)$"),
    user: dict = Depends(get_current_user)
):
    """Download uploaded file"""    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""                SELECT file_path, original_filename, content_type
                FROM uploaded_files
                WHERE file_id = %s AND user_id = %s
            """, (file_id, user['user_id']))
            
            file_info = result.fetchone()
            if not file_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found or access denied"
                )
        
        file_path, original_filename, content_type = file_info
        
        # Select appropriate file version
        if version == "processed":
            processed_path = os.path.join(PROCESSED_DIRECTORY, file_id, "processed" + os.path.splitext(original_filename)[1])
            if os.path.exists(processed_path):
                file_path = processed_path
        elif version == "compressed":
            compressed_path = os.path.join(PROCESSED_DIRECTORY, file_id, "compressed" + os.path.splitext(original_filename)[1])
            if os.path.exists(compressed_path):
                file_path = compressed_path
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File version not found"
            )
        
        # Return download URL (in production, this would be a signed URL to cloud storage)
        download_url = f"/api/files/download/{file_id}?version={version}&token=temp_token"
        
        return {
            "download_url": download_url,
            "filename": original_filename,
            "content_type": content_type,
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Download file failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to prepare file download"
        )


# Background processing functions
async def _process_uploaded_file(file_id: str, file_path: str, content_type: str, metadata: UploadMetadata):
    """Process uploaded file in background"""    try:
        # Update status to processing
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE uploaded_files 
                SET processing_status = 'processing', processing_step = 'initializing'
                WHERE file_id = %s
            """, (file_id,))
            await session.commit()
        
        # Create processing directory
        processing_dir = os.path.join(PROCESSED_DIRECTORY, file_id)
        os.makedirs(processing_dir, exist_ok=True)
        
        processing_results = {}
        
        # Process based on content type
        if content_type == "audio":
            processing_results = await audio_processor.process_file(
                file_path, processing_dir, metadata.dict()
            )
        elif content_type == "video":
            processing_results = await video_processor.process_file(
                file_path, processing_dir, metadata.dict()
            )
        elif content_type == "image":
            processing_results = await image_processor.process_file(
                file_path, processing_dir, metadata.dict()
            )
        elif content_type == "text":
            processing_results = await text_processor.process_file(
                file_path, processing_dir, metadata.dict()
            )
        
        # Update with results
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE uploaded_files 
                SET processing_status = 'completed', processing_progress = 100.0,
                    processing_results = %s, processing_step = 'completed'
                WHERE file_id = %s
            """, (processing_results, file_id))
            await session.commit()
        
        logger.info(f"File processing completed: {file_id}")
        
    except Exception as e:
        logger.error(f"File processing failed for {file_id}: {e}")
        
        # Update status to failed
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE uploaded_files 
                SET processing_status = 'failed', processing_error = %s
                WHERE file_id = %s
            """, (str(e), file_id))
            await session.commit()


async def _process_file_conversion(conversion_id: str, conversion_request: ConversionRequest, 
                                  source_path: str, source_type: str):
    """Process file format conversion"""    try:
        # Update status to processing
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE file_conversions 
                SET status = 'processing', started_at = %s
                WHERE conversion_id = %s
            """, (datetime.utcnow(), conversion_id))
            await session.commit()
        
        # Create output directory
        output_dir = os.path.join(PROCESSED_DIRECTORY, "conversions", conversion_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Perform conversion based on source and target types
        converted_path = None
        
        if source_type == "audio":
            converted_path = await audio_processor.convert_format(
                source_path, conversion_request.target_format, output_dir,
                conversion_request.quality_settings
            )
        elif source_type == "video":
            converted_path = await video_processor.convert_format(
                source_path, conversion_request.target_format, output_dir,
                conversion_request.quality_settings
            )
        elif source_type == "image":
            converted_path = await image_processor.convert_format(
                source_path, conversion_request.target_format, output_dir,
                conversion_request.quality_settings
            )
        
        if not converted_path or not os.path.exists(converted_path):
            raise Exception("Conversion failed - output file not created")
        
        # Update conversion record
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE file_conversions 
                SET status = 'completed', output_path = %s, completed_at = %s
                WHERE conversion_id = %s
            """, (converted_path, datetime.utcnow(), conversion_id))
            await session.commit()
        
        logger.info(f"File conversion completed: {conversion_id}")
        
    except Exception as e:
        logger.error(f"File conversion failed for {conversion_id}: {e}")
        
        # Update status to failed
        async with database_manager.get_postgres_session() as session:
            await session.execute("""                UPDATE file_conversions 
                SET status = 'failed', error_message = %s
                WHERE conversion_id = %s
            """, (str(e), conversion_id))
            await session.commit()