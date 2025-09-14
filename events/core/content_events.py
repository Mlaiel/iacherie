"""Content Events Module

Content upload, processing, and lifecycle events for the Ainflue platform.
Handles multi-format content (audio, video, image, blog) processing events.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from .base_event import BaseEvent
from .event_priority import EventPriority
from .event_status import EventStatus

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    BLOG = "blog"
    DOCUMENT = "document"
    MIXED = "mixed"


class ContentUploadEvent(BaseEvent):
    """Event triggered when content is uploaded to the platform"""
    
    def __init__(self, 
                 content_id -> None: str,
                 user_id -> None: str,
                 content_type -> None: ContentType,
                 file_size -> None: int,
                 mime_type -> None: str,
                 original_filename -> None: str,
                 storage_path -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'user_id': user_id,
            'content_type': content_type.value,
            'file_size': file_size,
            'mime_type': mime_type,
            'original_filename': original_filename,
            'storage_path': storage_path,
            'upload_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="content.uploaded",
            data=data,
            priority=EventPriority.HIGH,
            status=EventStatus.PENDING,
            metadata=metadata or {},
            **kwargs
        )


class ContentValidationEvent(BaseEvent):
    """Event triggered when content undergoes validation"""
    
    def __init__(self,
                 content_id -> None: str,
                 validation_type -> None: str,
                 validation_rules -> None: List[str],
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'validation_type': validation_type,
            'validation_rules': validation_rules,
            'validation_started': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="content.validation.started",
            data=data,
            priority=EventPriority.HIGH,
            status=EventStatus.PROCESSING,
            metadata=metadata or {},
            **kwargs
        )


class ContentProcessingEvent(BaseEvent):
    """Event triggered during content processing operations"""
    
    def __init__(self,
                 content_id -> None: str,
                 processing_stage -> None: str,
                 processor_id -> None: str,
                 processing_config -> None: Dict[str, Any],
                 estimated_duration -> None: Optional[int] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'processing_stage': processing_stage,
            'processor_id': processor_id,
            'processing_config': processing_config,
            'estimated_duration': estimated_duration,
            'processing_started': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="content.processing.started",
            data=data,
            priority=EventPriority.MEDIUM,
            status=EventStatus.PROCESSING,
            metadata=metadata or {},
            **kwargs
        )


class ContentEnrichmentEvent(BaseEvent):
    """Event triggered when content metadata is enriched"""
    
    def __init__(self,
                 content_id -> None: str,
                 enrichment_type -> None: str,
                 enrichment_data -> None: Dict[str, Any],
                 confidence_score -> None: Optional[float] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'enrichment_type': enrichment_type,
            'enrichment_data': enrichment_data,
            'confidence_score': confidence_score,
            'enrichment_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="content.enriched",
            data=data,
            priority=EventPriority.MEDIUM,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class ContentPublishEvent(BaseEvent):
    """Event triggered when content is published"""
    
    def __init__(self,
                 content_id -> None: str,
                 user_id -> None: str,
                 publication_settings -> None: Dict[str, Any],
                 target_platforms -> None: List[str],
                 scheduled_time -> None: Optional[datetime] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'user_id': user_id,
            'publication_settings': publication_settings,
            'target_platforms': target_platforms,
            'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
            'publish_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="content.published",
            data=data,
            priority=EventPriority.HIGH,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class ContentModificationEvent(BaseEvent):
    """Event triggered when existing content is modified"""
    
    def __init__(self,
                 content_id -> None: str,
                 user_id -> None: str,
                 modification_type -> None: str,
                 changes -> None: Dict[str, Any],
                 previous_version -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'user_id': user_id,
            'modification_type': modification_type,
            'changes': changes,
            'previous_version': previous_version,
            'modification_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="content.modified",
            data=data,
            priority=EventPriority.MEDIUM,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class ContentDeletedEvent(BaseEvent):
    """Event triggered when content is deleted"""
    
    def __init__(self,
                 content_id -> None: str,
                 user_id -> None: str,
                 deletion_reason -> None: str,
                 backup_location -> None: Optional[str] = None,
                 permanent -> None: bool = False,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'user_id': user_id,
            'deletion_reason': deletion_reason,
            'backup_location': backup_location,
            'permanent': permanent,
            'deletion_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="content.deleted",
            data=data,
            priority=EventPriority.CRITICAL,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


# Export all content event classes
__all__ = [
    'ContentType',
    'ContentUploadEvent',
    'ContentValidationEvent', 
    'ContentProcessingEvent',
    'ContentEnrichmentEvent',
    'ContentPublishEvent',
    'ContentModificationEvent',
    'ContentDeletedEvent'
]

logger.info("Content events module initialized successfully")