# 📋 Ainflue Platform - Coding Standards

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 2.0.0  
**Last Updated:** January 2025  
**Copyright:** © 2025 Fahed Mlaiel. All rights reserved.

---

## 📚 Table of Contents

1. [**🐍 Python Standards**](#-python-standards)
2. [**🌐 API Standards**](#-api-standards)
3. [**🗄️ Database Standards**](#️-database-standards)
4. [**🤖 AI/ML Standards**](#-aiml-standards)
5. [**🔒 Security Standards**](#-security-standards)
6. [**📚 Documentation Standards**](#-documentation-standards)
7. [**🧪 Testing Standards**](#-testing-standards)
8. [**🔧 Configuration Standards**](#-configuration-standards)

---

## 🐍 Python Standards

### Code Style Guidelines

#### 1. PEP 8 Compliance with Modifications
- **Line Length**: 88 characters (Black default)
- **String Quotes**: Double quotes preferred
- **Imports**: Absolute imports, organized by type
- **Whitespace**: 4 spaces for indentation (no tabs)

```python
# ✅ Good Example
from typing import Dict, List, Optional, Union
import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import User, Content
from core.schemas import ContentCreate, ContentResponse
from core.services import ContentService


class ContentAnalyzer:
    """Analyze content for genre, quality, and fingerprinting."""
    
    def __init__(self, quality_threshold: float = 0.8):
        self.quality_threshold = quality_threshold
        self._models_loaded = False
    
    async def analyze_content(
        self, 
        content: Content, 
        options: Dict[str, Any] = None
    ) -> Dict[str, Union[str, float, bool]]:
        """Analyze content and extract features.
        
        Args:
            content: Content object to analyze
            options: Optional analysis parameters
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            ContentAnalysisError: If analysis fails
        """
        if options is None:
            options = {}
            
        try:
            # Analysis logic here
            return {"status": "success", "quality": 0.85}
        except Exception as e:
            logger.exception(f"Content analysis failed for {content.id}")
            raise ContentAnalysisError(f"Analysis failed: {str(e)}")
```

#### 2. Type Hints - Mandatory
All functions must include comprehensive type hints:

```python
from typing import Dict, List, Optional, Union, Any, Callable, AsyncGenerator
from pathlib import Path

# Function type hints
async def process_audio_file(
    file_path: Path,
    sample_rate: int = 22050,
    normalize: bool = True,
    callback: Optional[Callable[[float], None]] = None
) -> Dict[str, Union[str, float, List[float]]]:
    """Process audio file with comprehensive type hints."""
    pass

# Class type hints
class AudioProcessor:
    """Audio processing with type hints."""
    
    _models: Dict[str, Any]
    _cache: Optional[Dict[str, float]]
    
    def __init__(self, models: Dict[str, Any]) -> None:
        self._models = models
        self._cache = None
    
    @property
    def is_ready(self) -> bool:
        """Check if processor is ready."""
        return len(self._models) > 0

# Generic types
from typing import TypeVar, Generic

T = TypeVar('T')

class Repository(Generic[T]):
    """Generic repository pattern."""
    
    def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass
```

#### 3. Error Handling Standards

```python
import logging
from typing import Optional, Type
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Custom exceptions
class AinfluePlatformError(Exception):
    """Base exception for Ainflue platform."""
    pass

class ContentAnalysisError(AinfluePlatformError):
    """Raised when content analysis fails."""
    pass

class AuthenticationError(AinfluePlatformError):
    """Raised when authentication fails."""
    pass

# Error handling patterns
async def safe_content_analysis(content_id: str) -> Optional[Dict[str, Any]]:
    """Safely analyze content with proper error handling."""
    try:
        content = await get_content(content_id)
        if not content:
            logger.warning(f"Content not found: {content_id}")
            return None
            
        result = await analyze_content(content)
        logger.info(f"Content analysis completed: {content_id}")
        return result
        
    except ContentAnalysisError as e:
        logger.error(f"Content analysis failed for {content_id}: {e}")
        # Don't re-raise, return None for graceful degradation
        return None
        
    except Exception as e:
        logger.exception(f"Unexpected error analyzing content {content_id}")
        # Re-raise unexpected errors
        raise

# Context manager for resource cleanup
@asynccontextmanager
async def audio_processing_context(file_path: str):
    """Context manager for audio processing resources."""
    resources = None
    try:
        resources = await initialize_audio_resources(file_path)
        yield resources
    except Exception as e:
        logger.exception(f"Audio processing failed: {e}")
        raise
    finally:
        if resources:
            await cleanup_audio_resources(resources)
```

#### 4. Async/Await Best Practices

```python
import asyncio
from typing import List, Awaitable

# Use async/await for all I/O operations
async def fetch_multiple_apis(urls: List[str]) -> List[Dict[str, Any]]:
    """Fetch data from multiple APIs concurrently."""
    tasks = [fetch_api_data(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle results and exceptions
    successful_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"API call failed for {urls[i]}: {result}")
            continue
        successful_results.append(result)
    
    return successful_results

# Proper async context managers
async def with_database_transaction():
    """Use async context manager for database transactions."""
    async with get_async_session() as session:
        try:
            async with session.begin():
                # Database operations
                user = await session.get(User, user_id)
                user.last_login = datetime.utcnow()
                await session.commit()
        except Exception as e:
            await session.rollback()
            raise

# Background tasks
import asyncio
from functools import wraps

def background_task(func):
    """Decorator to run function as background task."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        task = loop.create_task(func(*args, **kwargs))
        
        def handle_result(task):
            try:
                result = task.result()
                logger.info(f"Background task completed: {func.__name__}")
            except Exception as e:
                logger.exception(f"Background task failed: {func.__name__}")
        
        task.add_done_callback(handle_result)
        return task
    return wrapper
```

### Code Organization Standards

#### 1. Module Structure
```python
# File: core/services/content_service.py

"""Content service for managing content lifecycle.

This module provides comprehensive content management functionality including
upload, analysis, protection setup, and monetization configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

# Standard library imports
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Third-party imports
import aiofiles
import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Local application imports
from core.config import get_settings
from core.database import get_async_session
from core.models import Content, User, ContentAnalysis
from core.schemas import ContentCreate, ContentUpdate, ContentResponse
from core.exceptions import ContentServiceError, ValidationError
from ai_engine.services import AIOrchestrator
from protection.services import ProtectionService

# Module constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
SUPPORTED_FORMATS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
ANALYSIS_TIMEOUT = 300  # 5 minutes

logger = logging.getLogger(__name__)
```

#### 2. Class Organization
```python
class ContentService:
    """Service for managing content operations.
    
    This service handles the complete content lifecycle including upload,
    analysis, protection, and monetization setup.
    
    Attributes:
        ai_orchestrator: AI service for content analysis
        protection_service: Service for content protection
        settings: Application configuration
    """
    
    def __init__(
        self,
        ai_orchestrator: AIOrchestrator,
        protection_service: ProtectionService,
        settings: Optional[Settings] = None
    ) -> None:
        """Initialize content service.
        
        Args:
            ai_orchestrator: AI service instance
            protection_service: Protection service instance
            settings: Optional application settings
        """
        self.ai_orchestrator = ai_orchestrator
        self.protection_service = protection_service
        self.settings = settings or get_settings()
        self._initialized = False
    
    # Public interface methods first
    async def create_content(
        self, 
        content_data: ContentCreate, 
        user_id: str,
        db: AsyncSession
    ) -> ContentResponse:
        """Create new content with full processing pipeline."""
        pass
    
    async def get_content(
        self, 
        content_id: str, 
        user_id: str,
        db: AsyncSession
    ) -> Optional[ContentResponse]:
        """Get content by ID with user authorization."""
        pass
    
    async def update_content(
        self,
        content_id: str,
        updates: ContentUpdate,
        user_id: str,
        db: AsyncSession
    ) -> ContentResponse:
        """Update existing content."""
        pass
    
    async def delete_content(
        self,
        content_id: str,
        user_id: str,
        db: AsyncSession
    ) -> bool:
        """Delete content and cleanup resources."""
        pass
    
    # Private helper methods
    async def _validate_content_file(self, file_path: Path) -> None:
        """Validate content file format and size."""
        pass
    
    async def _process_content_upload(
        self, 
        file_data: bytes, 
        filename: str
    ) -> Path:
        """Process and store uploaded content file."""
        pass
    
    async def _analyze_content(
        self, 
        content: Content
    ) -> Dict[str, Any]:
        """Analyze content using AI services."""
        pass
    
    # Properties
    @property
    def is_initialized(self) -> bool:
        """Check if service is properly initialized."""
        return self._initialized
    
    # Class methods
    @classmethod
    async def create_with_dependencies(cls) -> "ContentService":
        """Factory method to create service with all dependencies."""
        ai_orchestrator = await AIOrchestrator.initialize()
        protection_service = ProtectionService()
        return cls(ai_orchestrator, protection_service)
```

---

## 🌐 API Standards

### FastAPI Best Practices

#### 1. Router Organization
```python
# File: api/routers/content.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.schemas import ContentResponse, ContentCreate, ContentList
from core.services import ContentService
from core.auth import get_current_user, require_permissions
from core.models import User

router = APIRouter(
    prefix="/api/v1/content",
    tags=["content"],
    dependencies=[Depends(HTTPBearer())]
)

# Dependency injection
async def get_content_service() -> ContentService:
    """Get content service instance."""
    return await ContentService.create_with_dependencies()

@router.post(
    "/upload",
    response_model=ContentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload new content",
    description="Upload and process new content file with AI analysis"
)
async def upload_content(
    file: UploadFile = File(..., description="Content file to upload"),
    title: str = Form(..., description="Content title"),
    description: Optional[str] = Form(None, description="Content description"),
    tags: List[str] = Form([], description="Content tags"),
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
    db: AsyncSession = Depends(get_async_db)
) -> ContentResponse:
    """Upload new content with comprehensive processing.
    
    This endpoint handles:
    - File validation and storage
    - AI-powered content analysis
    - Content fingerprinting
    - Protection setup
    - Metadata extraction
    
    Args:
        file: Uploaded content file
        title: Content title
        description: Optional content description
        tags: Content tags for categorization
        current_user: Authenticated user
        content_service: Content service dependency
        db: Database session
        
    Returns:
        ContentResponse with content details and analysis results
        
    Raises:
        HTTPException: 400 for validation errors, 413 for file too large
    """
    # Validate file
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE} bytes"
        )
    
    if not file.filename.lower().endswith(tuple(SUPPORTED_FORMATS)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Supported: {SUPPORTED_FORMATS}"
        )
    
    try:
        content_data = ContentCreate(
            title=title,
            description=description,
            tags=tags,
            filename=file.filename
        )
        
        # Read file content
        file_content = await file.read()
        
        # Create content
        result = await content_service.create_content_with_file(
            content_data=content_data,
            file_content=file_content,
            user_id=current_user.id,
            db=db
        )
        
        return result
        
    except ContentServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Content upload failed for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during content upload"
        )
```

#### 2. Response Models
```python
# File: core/schemas/content.py

from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from enum import Enum

from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import UUID4

class ContentStatus(str, Enum):
    """Content processing status."""
    UPLOADING = "uploading"
    ANALYZING = "analyzing"
    PROCESSED = "processed"
    PROTECTED = "protected"
    ERROR = "error"

class ContentType(str, Enum):
    """Supported content types."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"

class ContentBase(BaseModel):
    """Base content schema."""
    title: str = Field(..., min_length=1, max_length=200, description="Content title")
    description: Optional[str] = Field(None, max_length=1000, description="Content description")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        
        for tag in v:
            if not tag.strip() or len(tag) > 50:
                raise ValueError("Tags must be 1-50 characters")
        
        return [tag.strip().lower() for tag in v]

class ContentCreate(ContentBase):
    """Schema for content creation."""
    filename: str = Field(..., description="Original filename")
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename format."""
        if not v or '/' in v or '\\' in v:
            raise ValueError("Invalid filename")
        return v

class ContentAnalysis(BaseModel):
    """Content analysis results."""
    genre: Optional[str] = Field(None, description="Detected genre")
    mood: Optional[str] = Field(None, description="Detected mood")
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Quality score 0-1")
    duration: Optional[float] = Field(None, ge=0, description="Duration in seconds")
    language: Optional[str] = Field(None, description="Detected language")
    instruments: List[str] = Field(default_factory=list, description="Detected instruments")
    bpm: Optional[int] = Field(None, ge=0, le=300, description="Beats per minute")
    key: Optional[str] = Field(None, description="Musical key")
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Analysis confidence")

class ContentProtection(BaseModel):
    """Content protection settings."""
    enabled: bool = Field(default=False, description="Protection enabled")
    fingerprint_id: Optional[str] = Field(None, description="Content fingerprint ID")
    monitoring_platforms: List[str] = Field(default_factory=list, description="Monitored platforms")
    similarity_threshold: float = Field(default=0.8, ge=0, le=1, description="Similarity threshold")
    auto_dmca: bool = Field(default=False, description="Automatic DMCA notices")

class ContentResponse(ContentBase):
    """Complete content response."""
    id: UUID4 = Field(..., description="Content unique identifier")
    user_id: UUID4 = Field(..., description="Owner user ID")
    content_type: ContentType = Field(..., description="Content type")
    status: ContentStatus = Field(..., description="Processing status")
    file_path: Optional[str] = Field(None, description="File storage path")
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Optional detailed information
    analysis: Optional[ContentAnalysis] = Field(None, description="Analysis results")
    protection: Optional[ContentProtection] = Field(None, description="Protection settings")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }

class ContentList(BaseModel):
    """Paginated content list response."""
    items: List[ContentResponse] = Field(..., description="Content items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    pages: int = Field(..., ge=0, description="Total number of pages")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    
    @root_validator
    def validate_pagination(cls, values):
        """Validate pagination consistency."""
        total = values.get('total', 0)
        per_page = values.get('per_page', 20)
        pages = values.get('pages', 0)
        
        expected_pages = (total + per_page - 1) // per_page if total > 0 else 0
        
        if pages != expected_pages:
            raise ValueError("Inconsistent pagination data")
        
        return values
```

#### 3. Error Handling
```python
# File: api/middleware/error_handling.py

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # Log HTTP exceptions
            logger.warning(
                f"HTTP Exception: {e.status_code} - {e.detail} - "
                f"URL: {request.url} - Method: {request.method}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "code": e.status_code,
                        "message": e.detail,
                        "type": "http_exception"
                    }
                }
            )
            
        except RequestValidationError as e:
            # Handle validation errors
            logger.warning(f"Validation error: {e} - URL: {request.url}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": {
                        "code": 422,
                        "message": "Validation error",
                        "type": "validation_error",
                        "details": e.errors()
                    }
                }
            )
            
        except Exception as e:
            # Log unexpected errors
            logger.exception(
                f"Unexpected error: {str(e)} - URL: {request.url} - "
                f"Method: {request.method}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": 500,
                        "message": "Internal server error",
                        "type": "internal_error",
                        "request_id": getattr(request.state, 'request_id', None)
                    }
                }
            )

# Custom exception handlers
async def content_service_error_handler(request: Request, exc: ContentServiceError):
    """Handle content service specific errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": 400,
                "message": str(exc),
                "type": "content_service_error"
            }
        }
    )

async def authentication_error_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": {
                "code": 401,
                "message": "Authentication failed",
                "type": "authentication_error"
            }
        }
    )
```

---

## 🗄️ Database Standards

### SQLAlchemy Model Standards

#### 1. Model Definition
```python
# File: core/models/content.py

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from core.database import Base

class Content(Base):
    """Content model for storing user-uploaded content.
    
    This model represents content uploaded by users including audio, video,
    and image files with their associated metadata and analysis results.
    """
    
    __tablename__ = "contents"
    __table_args__ = (
        # Indexes for common queries
        {"postgresql_partition_by": "RANGE (created_at)"},
    )
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4,
        comment="Unique content identifier"
    )
    
    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Content owner user ID"
    )
    
    # Content metadata
    title = Column(
        String(200), 
        nullable=False, 
        index=True,
        comment="Content title"
    )
    description = Column(
        Text, 
        nullable=True,
        comment="Content description"
    )
    content_type = Column(
        String(20), 
        nullable=False, 
        index=True,
        comment="Content type: audio, video, image"
    )
    
    # File information
    filename = Column(
        String(255), 
        nullable=False,
        comment="Original filename"
    )
    file_path = Column(
        String(500), 
        nullable=True,
        comment="File storage path"
    )
    file_size = Column(
        Integer, 
        nullable=True,
        comment="File size in bytes"
    )
    mime_type = Column(
        String(100), 
        nullable=True,
        comment="File MIME type"
    )
    
    # Processing status
    status = Column(
        String(20), 
        nullable=False, 
        default="uploading",
        index=True,
        comment="Processing status"
    )
    processing_progress = Column(
        Float, 
        nullable=False, 
        default=0.0,
        comment="Processing progress 0.0-1.0"
    )
    
    # Content analysis results
    analysis_results = Column(
        JSON, 
        nullable=True,
        comment="AI analysis results as JSON"
    )
    fingerprint_id = Column(
        String(64), 
        nullable=True, 
        unique=True, 
        index=True,
        comment="Content fingerprint identifier"
    )
    
    # Content properties
    duration = Column(
        Float, 
        nullable=True,
        comment="Content duration in seconds"
    )
    quality_score = Column(
        Float, 
        nullable=True,
        comment="Quality assessment score 0.0-1.0"
    )
    tags = Column(
        ARRAY(String(50)), 
        nullable=False, 
        default=[],
        comment="Content tags array"
    )
    
    # Protection settings
    protection_enabled = Column(
        Boolean, 
        nullable=False, 
        default=False,
        comment="Content protection enabled"
    )
    monitoring_platforms = Column(
        ARRAY(String(50)), 
        nullable=False, 
        default=[],
        comment="Platforms being monitored"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now(),
        index=True,
        comment="Creation timestamp"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp"
    )
    
    # Relationships
    user = relationship(
        "User", 
        back_populates="contents",
        lazy="select"
    )
    protection_violations = relationship(
        "ProtectionViolation",
        back_populates="content",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    revenue_records = relationship(
        "RevenueRecord",
        back_populates="content",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Validators
    @validates('content_type')
    def validate_content_type(self, key, value):
        """Validate content type."""
        allowed_types = {'audio', 'video', 'image'}
        if value not in allowed_types:
            raise ValueError(f"Content type must be one of: {allowed_types}")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate processing status."""
        allowed_statuses = {
            'uploading', 'analyzing', 'processed', 'protected', 'error'
        }
        if value not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return value
    
    @validates('quality_score')
    def validate_quality_score(self, key, value):
        """Validate quality score range."""
        if value is not None and not (0.0 <= value <= 1.0):
            raise ValueError("Quality score must be between 0.0 and 1.0")
        return value
    
    # Properties
    @property
    def is_processed(self) -> bool:
        """Check if content is fully processed."""
        return self.status in ('processed', 'protected')
    
    @property
    def has_analysis(self) -> bool:
        """Check if content has analysis results."""
        return self.analysis_results is not None
    
    # Class methods
    @classmethod
    def create_from_upload(
        cls, 
        user_id: str, 
        title: str, 
        filename: str,
        content_type: str
    ) -> "Content":
        """Factory method to create content from upload."""
        return cls(
            user_id=user_id,
            title=title,
            filename=filename,
            content_type=content_type,
            status="uploading"
        )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}')>"
```

#### 2. Repository Pattern
```python
# File: database/repositories/content_repository.py

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from core.models import Content, User, ProtectionViolation
from core.exceptions import ContentNotFoundError, RepositoryError

class ContentRepository:
    """Repository for content data access operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, content_data: Dict[str, Any]) -> Content:
        """Create new content record.
        
        Args:
            content_data: Content data dictionary
            
        Returns:
            Created content instance
            
        Raises:
            RepositoryError: If creation fails
        """
        try:
            content = Content(**content_data)
            self.session.add(content)
            await self.session.flush()
            await self.session.refresh(content)
            return content
            
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError(f"Failed to create content: {str(e)}")
    
    async def get_by_id(
        self, 
        content_id: UUID, 
        include_relations: bool = False
    ) -> Optional[Content]:
        """Get content by ID.
        
        Args:
            content_id: Content UUID
            include_relations: Whether to include related objects
            
        Returns:
            Content instance or None if not found
        """
        query = select(Content).where(Content.id == content_id)
        
        if include_relations:
            query = query.options(
                selectinload(Content.user),
                selectinload(Content.protection_violations),
                selectinload(Content.revenue_records)
            )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user_id(
        self, 
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Content]:
        """Get contents by user ID with pagination and filtering.
        
        Args:
            user_id: User UUID
            limit: Maximum number of results
            offset: Number of results to skip
            filters: Optional filters (status, content_type, etc.)
            
        Returns:
            List of content instances
        """
        query = select(Content).where(Content.user_id == user_id)
        
        # Apply filters
        if filters:
            if 'status' in filters:
                query = query.where(Content.status == filters['status'])
            
            if 'content_type' in filters:
                query = query.where(Content.content_type == filters['content_type'])
            
            if 'has_protection' in filters:
                query = query.where(Content.protection_enabled == filters['has_protection'])
            
            if 'created_after' in filters:
                query = query.where(Content.created_at >= filters['created_after'])
            
            if 'search' in filters:
                search_term = f"%{filters['search']}%"
                query = query.where(
                    or_(
                        Content.title.ilike(search_term),
                        Content.description.ilike(search_term)
                    )
                )
        
        # Apply pagination and ordering
        query = query.order_by(Content.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update(
        self, 
        content_id: UUID, 
        updates: Dict[str, Any]
    ) -> Optional[Content]:
        """Update content by ID.
        
        Args:
            content_id: Content UUID
            updates: Dictionary of fields to update
            
        Returns:
            Updated content instance or None if not found
        """
        # Add updated timestamp
        updates['updated_at'] = datetime.utcnow()
        
        query = (
            update(Content)
            .where(Content.id == content_id)
            .values(**updates)
            .returning(Content)
        )
        
        result = await self.session.execute(query)
        content = result.scalar_one_or_none()
        
        if content:
            await self.session.refresh(content)
        
        return content
    
    async def delete(self, content_id: UUID) -> bool:
        """Delete content by ID.
        
        Args:
            content_id: Content UUID
            
        Returns:
            True if deleted, False if not found
        """
        query = delete(Content).where(Content.id == content_id)
        result = await self.session.execute(query)
        return result.rowcount > 0
    
    async def get_analytics_data(
        self, 
        user_id: UUID,
        date_from: datetime,
        date_to: datetime
    ) -> Dict[str, Any]:
        """Get content analytics data for user.
        
        Args:
            user_id: User UUID
            date_from: Start date for analytics
            date_to: End date for analytics
            
        Returns:
            Analytics data dictionary
        """
        # Total content count
        total_query = select(func.count(Content.id)).where(
            and_(
                Content.user_id == user_id,
                Content.created_at.between(date_from, date_to)
            )
        )
        total_content = await self.session.scalar(total_query)
        
        # Content by type
        type_query = select(
            Content.content_type,
            func.count(Content.id)
        ).where(
            and_(
                Content.user_id == user_id,
                Content.created_at.between(date_from, date_to)
            )
        ).group_by(Content.content_type)
        
        type_result = await self.session.execute(type_query)
        content_by_type = dict(type_result.all())
        
        # Content by status
        status_query = select(
            Content.status,
            func.count(Content.id)
        ).where(
            and_(
                Content.user_id == user_id,
                Content.created_at.between(date_from, date_to)
            )
        ).group_by(Content.status)
        
        status_result = await self.session.execute(status_query)
        content_by_status = dict(status_result.all())
        
        # Average quality score
        quality_query = select(func.avg(Content.quality_score)).where(
            and_(
                Content.user_id == user_id,
                Content.quality_score.isnot(None),
                Content.created_at.between(date_from, date_to)
            )
        )
        avg_quality = await self.session.scalar(quality_query) or 0.0
        
        return {
            'total_content': total_content,
            'content_by_type': content_by_type,
            'content_by_status': content_by_status,
            'average_quality_score': float(avg_quality)
        }
    
    async def search_similar_content(
        self, 
        fingerprint_id: str,
        similarity_threshold: float = 0.8
    ) -> List[Content]:
        """Search for similar content by fingerprint.
        
        Args:
            fingerprint_id: Content fingerprint to search for
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar content instances
        """
        # This is a simplified example - in practice you'd use
        # vector similarity search or specialized similarity algorithms
        query = select(Content).where(
            and_(
                Content.fingerprint_id.isnot(None),
                Content.fingerprint_id != fingerprint_id
            )
        )
        
        result = await self.session.execute(query)
        all_content = list(result.scalars().all())
        
        # In practice, implement proper similarity calculation
        # For now, return empty list as placeholder
        return []
```

---

This completes the comprehensive coding standards documentation. The document provides detailed guidelines for Python development, API design, database modeling, and more, all specifically tailored for the Ainflue platform.