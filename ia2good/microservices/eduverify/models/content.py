"""
Content Models for EduVerify
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field, validator


class ContentType(str, Enum):
    """Type of educational content"""
    TEXT = "text"
    URL = "url"
    PDF = "pdf"
    VIDEO = "video"
    AUDIO = "audio"


class ProcessingMode(str, Enum):
    """Processing mode for content"""
    STANDARD = "standard"
    LIVE_LECTURE = "live_lecture"
    REAL_TIME = "real_time"


class AcademicLevel(str, Enum):
    """Academic level of content"""
    ELEMENTARY = "elementary"
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    DOCTORATE = "doctorate"


class ContentUpload(BaseModel):
    """Request model for uploading content - Support multilingue (644+ langues)"""
    title: str = Field(..., min_length=1, max_length=255)
    title_translations: Optional[Dict] = None  # {"EN": "...", "FR": "...", ...} 644 langues
    content_type: ContentType
    content_text: Optional[str] = None
    content_text_translations: Optional[Dict] = None  # Traductions 644 langues
    file_url: Optional[str] = None
    url: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=100)
    subject_translations: Optional[Dict] = None  # 644 langues
    topic: Optional[str] = Field(None, max_length=255)
    topic_translations: Optional[Dict] = None  # 644 langues
    language: str = Field(default="EN", max_length=10)  # Langue originale
    dialect: Optional[str] = Field(None, max_length=50)
    academic_level: Optional[AcademicLevel] = None
    processing_mode: ProcessingMode = ProcessingMode.STANDARD

    @validator('content_text', 'file_url', 'url')
    def validate_content_source(cls, v, values):
        """At least one content source must be provided"""
        if not any([values.get('content_text'), values.get('file_url'), values.get('url'), v]):
            raise ValueError("At least one content source (text, file_url, or url) must be provided")
        return v


class Content(BaseModel):
    """Content response model - Support multilingue (644+ langues)"""
    id: UUID
    user_id: UUID
    title: str
    title_translations: Optional[Dict] = Field(default_factory=dict)  # 644 langues
    content_text: Optional[str]
    content_text_translations: Optional[Dict] = Field(default_factory=dict)  # 644 langues
    content_type: ContentType
    file_url: Optional[str]
    subject: Optional[str]
    subject_translations: Optional[Dict] = Field(default_factory=dict)  # 644 langues
    topic: Optional[str]
    topic_translations: Optional[Dict] = Field(default_factory=dict)  # 644 langues
    language: str  # Langue originale
    dialect: Optional[str]
    academic_level: Optional[AcademicLevel]
    processing_mode: ProcessingMode
    ai_analysis: Optional[Dict] = Field(default_factory=dict)
    ai_analysis_translations: Optional[Dict] = Field(default_factory=dict)  # 644 langues
    summary_translations: Optional[Dict] = Field(default_factory=dict)  # 644 langues
    key_points_translations: Optional[Dict] = Field(default_factory=dict)  # 644 langues
    word_count: Optional[int]
    processing_status: str = "pending"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LiveLectureStart(BaseModel):
    """Request to start live lecture capture"""
    title: str = Field(..., min_length=1, max_length=255)
    subject: Optional[str] = Field(None, max_length=100)
    topic: Optional[str] = Field(None, max_length=255)
    language: str = Field(default="fr", max_length=10)
    enable_fact_checking: bool = True
    enable_real_time_alerts: bool = True


class ContentList(BaseModel):
    """List of contents with pagination"""
    items: List[Content]
    total: int
    page: int
    per_page: int
    pages: int
