"""
Guardian File Upload Routes
Upload and manage files (images, videos, documents) for missions
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import uuid
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from moderation import get_moderator
from rate_limiting import get_rate_limiter, check_rate_limit
from audit import get_audit_logger, AuditAction, AuditLevel

router = APIRouter()

# Configuration
UPLOAD_DIR = Path("/tmp/guardian_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "videos": {".mp4", ".webm", ".mov", ".avi"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md"},
    "audio": {".mp3", ".wav", ".ogg", ".m4a"}
}

# Models
class FileInfo(BaseModel):
    file_id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    mission_id: Optional[int] = None
    volunteer_id: Optional[int] = None
    uploaded_by: Optional[str] = None
    uploaded_at: datetime
    url: str

# Storage
uploaded_files: dict[str, FileInfo] = {}

# ============================================================================
# FILE UPLOAD
# ============================================================================

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    mission_id: Optional[int] = Form(None),
    volunteer_id: Optional[int] = Form(None),
    uploaded_by: Optional[str] = Form(None)
):
    """Upload un fichier"""
    
    user_id = uploaded_by or "anonymous"
    
    # Rate limit
    rate_limiter = get_rate_limiter()
    if not rate_limiter.check_rate_limit(f"file_upload:{user_id}", 50, 3600):
        raise HTTPException(status_code=429, detail="Too many uploads. Max 50 per hour.")
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_FILE_SIZE / 1024 / 1024}MB)")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    file_type = get_file_type(file_ext)
    
    if not file_type:
        raise HTTPException(status_code=400, detail=f"File type not allowed: {file_ext}")
    
    # Moderate file
    moderator = get_moderator()
    moderation_result = moderator.moderate_file(
        file.filename,
        file_size,
        file.content_type
    )
    
    if moderation_result.suggested_action == "block":
        audit_logger = get_audit_logger()
        audit_logger.log(
            AuditAction.FILE_UPLOADED,
            level=AuditLevel.WARNING,
            user_id=user_id,
            resource_type="file",
            details={
                "filename": file.filename,
                "blocked": True,
                "reasons": moderation_result.reasons
            },
            success=False
        )
        raise HTTPException(
            status_code=400,
            detail=f"File blocked: {', '.join(moderation_result.reasons)}"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    new_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / new_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    
    # Create file info
    file_info = FileInfo(
        file_id=file_id,
        filename=new_filename,
        original_filename=file.filename,
        file_type=file_type,
        file_size=file_size,
        mission_id=mission_id,
        volunteer_id=volunteer_id,
        uploaded_by=uploaded_by,
        uploaded_at=datetime.utcnow(),
        url=f"/api/guardian/files/download/{file_id}"
    )
    
    uploaded_files[file_id] = file_info
    
    # Audit log
    audit_logger = get_audit_logger()
    audit_logger.log(
        AuditAction.FILE_UPLOADED,
        user_id=user_id,
        resource_type="file",
        resource_id=file_id,
        details={
            "filename": file.filename,
            "size_bytes": file_size,
            "file_type": file_type,
            "mission_id": mission_id
        }
    )
    
    return {
        "success": True,
        "file": file_info.dict()
    }

@router.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    mission_id: Optional[int] = Form(None),
    volunteer_id: Optional[int] = Form(None),
    uploaded_by: Optional[str] = Form(None)
):
    """Upload plusieurs fichiers"""
    
    results = []
    errors = []
    
    for file in files:
        try:
            # Check file size
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                errors.append(f"{file.filename}: File too large")
                continue
            
            # Check file extension
            file_ext = Path(file.filename).suffix.lower()
            file_type = get_file_type(file_ext)
            
            if not file_type:
                errors.append(f"{file.filename}: File type not allowed")
                continue
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            new_filename = f"{file_id}{file_ext}"
            file_path = UPLOAD_DIR / new_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create file info
            file_info = FileInfo(
                file_id=file_id,
                filename=new_filename,
                original_filename=file.filename,
                file_type=file_type,
                file_size=file_size,
                mission_id=mission_id,
                volunteer_id=volunteer_id,
                uploaded_by=uploaded_by,
                uploaded_at=datetime.utcnow(),
                url=f"/api/guardian/files/download/{file_id}"
            )
            
            uploaded_files[file_id] = file_info
            results.append(file_info.dict())
        
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    return {
        "success": len(results) > 0,
        "uploaded": len(results),
        "failed": len(errors),
        "files": results,
        "errors": errors
    }

# ============================================================================
# FILE DOWNLOAD
# ============================================================================

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Télécharger un fichier"""
    
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[file_id]
    file_path = UPLOAD_DIR / file_info.filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=file_info.original_filename,
        media_type="application/octet-stream"
    )

# ============================================================================
# FILE MANAGEMENT
# ============================================================================

@router.get("/files")
def list_files(
    mission_id: Optional[int] = None,
    volunteer_id: Optional[int] = None,
    file_type: Optional[str] = None
):
    """Lister les fichiers"""
    
    files_list = list(uploaded_files.values())
    
    # Filter by mission_id
    if mission_id is not None:
        files_list = [f for f in files_list if f.mission_id == mission_id]
    
    # Filter by volunteer_id
    if volunteer_id is not None:
        files_list = [f for f in files_list if f.volunteer_id == volunteer_id]
    
    # Filter by file_type
    if file_type:
        files_list = [f for f in files_list if f.file_type == file_type]
    
    return {
        "success": True,
        "total": len(files_list),
        "files": [f.dict() for f in files_list]
    }

@router.get("/files/{file_id}")
def get_file_info(file_id: str):
    """Obtenir les infos d'un fichier"""
    
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "success": True,
        "file": uploaded_files[file_id].dict()
    }

@router.delete("/files/{file_id}")
def delete_file(file_id: str):
    """Supprimer un fichier"""
    
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[file_id]
    file_path = UPLOAD_DIR / file_info.filename
    
    # Delete file from disk
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {e}")
    
    # Remove from storage
    del uploaded_files[file_id]
    
    return {
        "success": True,
        "message": "File deleted"
    }

# ============================================================================
# FILE STATISTICS
# ============================================================================

@router.get("/files/stats/overview")
def get_files_stats():
    """Obtenir les statistiques des fichiers"""
    
    total_size = sum(f.file_size for f in uploaded_files.values())
    
    by_type = {}
    for file_info in uploaded_files.values():
        if file_info.file_type not in by_type:
            by_type[file_info.file_type] = {"count": 0, "size": 0}
        by_type[file_info.file_type]["count"] += 1
        by_type[file_info.file_type]["size"] += file_info.file_size
    
    return {
        "success": True,
        "total_files": len(uploaded_files),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        "by_type": by_type,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_file_type(extension: str) -> Optional[str]:
    """Déterminer le type de fichier à partir de l'extension"""
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return file_type
    return None
