"""📄 Base Content Model - Foundation for All Content Types
========================================================
Module: models/content_models/base_content_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Base Content Model - Production-Ready
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib

class ContentStatus(Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"

class VisibilityLevel(Enum):
    """Content visibility levels"""
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    PREMIUM = "premium"

@dataclass
class ContentMetadata:
    """Base content metadata"""
    title: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    language: str = "en"
    copyright_info: Optional[str] = None
    license_type: str = "all_rights_reserved"
    content_warnings: List[str] = field(default_factory=list)
    age_rating: str = "general"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "language": self.language,
            "copyright_info": self.copyright_info,
            "license_type": self.license_type,
            "content_warnings": self.content_warnings,
            "age_rating": self.age_rating
        }

@dataclass
class ContentItem:
    """Base content item"""
    id: str
    creator_id: str
    content_type: str
    metadata: ContentMetadata
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    file_hash: Optional[str] = None
    mime_type: Optional[str] = None
    status: ContentStatus = ContentStatus.DRAFT
    visibility: VisibilityLevel = VisibilityLevel.PRIVATE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.file_hash and self.file_path:
            self.file_hash = self.generate_content_hash()
    
    def generate_content_hash(self) -> str:
        """Generate content hash for fingerprinting"""
        content_string = f"{self.metadata.title}_{self.file_size_bytes}_{self.created_at}"
        return hashlib.sha256(content_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "content_type": self.content_type,
            "metadata": self.metadata.to_dict(),
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "file_hash": self.file_hash,
            "mime_type": self.mime_type,
            "status": self.status.value,
            "visibility": self.visibility.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None
        }

class BaseContentModel:
    """Base Content Model - Foundation for All Content Types"""
    
    @staticmethod
    def create_content(content_data: Dict[str, Any]) -> ContentItem:
        """Create base content item"""
        try:
            # Create metadata
            metadata_data = content_data.get("metadata", {})
            metadata = ContentMetadata(
                title=metadata_data.get("title", "Untitled"),
                description=metadata_data.get("description"),
                tags=metadata_data.get("tags", []),
                language=metadata_data.get("language", "en"),
                copyright_info=metadata_data.get("copyright_info"),
                license_type=metadata_data.get("license_type", "all_rights_reserved"),
                content_warnings=metadata_data.get("content_warnings", []),
                age_rating=metadata_data.get("age_rating", "general")
            )
            
            # Create content item
            content = ContentItem(
                id=content_data.get("id", str(uuid.uuid4())),
                creator_id=content_data["creator_id"],
                content_type=content_data.get("content_type", "generic"),
                metadata=metadata,
                file_path=content_data.get("file_path"),
                file_size_bytes=content_data.get("file_size_bytes", 0),
                mime_type=content_data.get("mime_type"),
                status=ContentStatus(content_data.get("status", "draft")),
                visibility=VisibilityLevel(content_data.get("visibility", "private"))
            )
            
            return content
            
        except Exception as e:
            raise Exception(f"Failed to create content: {e}")
    
    @staticmethod
    def validate_content_data(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content data"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Required fields
        required_fields = ["creator_id"]
        for field in required_fields:
            if not content_data.get(field):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Metadata validation
        metadata = content_data.get("metadata", {})
        if not metadata.get("title"):
            validation_result["warnings"].append("Content title is recommended")
        
        # File validation
        if content_data.get("file_size_bytes", 0) == 0:
            validation_result["warnings"].append("File size is 0 bytes")
        
        return validation_result
    
    @staticmethod
    def update_content(content: ContentItem, updates: Dict[str, Any]) -> ContentItem:
        """Update content item"""
        try:
            # Update metadata if provided
            if "metadata" in updates:
                metadata_updates = updates["metadata"]
                for field, value in metadata_updates.items():
                    if hasattr(content.metadata, field):
                        setattr(content.metadata, field, value)
            
            # Update basic fields
            for field, value in updates.items():
                if hasattr(content, field) and field not in ["id", "created_at", "file_hash"]:
                    setattr(content, field, value)
            
            # Update timestamp
            content.updated_at = datetime.now(timezone.utc)
            
            # Update published timestamp if status changed to published
            if updates.get("status") == "published" and content.published_at is None:
                content.published_at = datetime.now(timezone.utc)
            
            return content
            
        except Exception as e:
            raise Exception(f"Failed to update content: {e}")

__all__ = ['BaseContentModel', 'ContentItem', 'ContentMetadata', 'ContentStatus', 'VisibilityLevel']