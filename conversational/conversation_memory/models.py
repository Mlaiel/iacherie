"""Conversation Memory Data Models - Enterprise Data Structures

Comprehensive data models for conversation memory management including
conversation records, memory entries, and specialized context models
for content creator interactions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING: Unauthorized use strictly prohibited ⚠️
Contact: mlaiel@live.de
"""from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid
import json

from sqlalchemy import Column, String, Text, DateTime, JSON, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from backend.core.database import Base
from backend.core.security import EncryptionManager

# Data models base
ConversationBase = declarative_base()


class ContentType(Enum):
    """Content creator specialization types"""    MUSIC_CREATION = "music_creation"
    BLOG_CONTENT = "blog_content"
    PHOTOGRAPHY = "photography"
    VIDEO_CONTENT = "video_content"
    COMEDY_CONTENT = "comedy_content"
    INFLUENCER_CONTENT = "influencer_content"
    COLLABORATION = "collaboration"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION = "monetization"
    GENERAL = "general"


class ConversationStatus(Enum):
    """Conversation processing status"""    ACTIVE = "active"
    ARCHIVED = "archived"
    PROCESSING = "processing"
    ERROR = "error"
    DELETED = "deleted"


class MemoryType(Enum):
    """Memory classification types"""    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING_MEMORY = "working_memory"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class ContextType(Enum):
    """Context classification types"""    CONTENT_CONTEXT = "content_context"
    COLLABORATION_CONTEXT = "collaboration_context"
    PROTECTION_CONTEXT = "protection_context"
    BUSINESS_CONTEXT = "business_context"
    TECHNICAL_CONTEXT = "technical_context"


@dataclass
class ConversationMetadata:
    """Metadata for conversation records"""    platform: Optional[str] = None
    language: Optional[str] = None
    sentiment_score: Optional[float] = None
    priority_level: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    related_content_ids: List[str] = field(default_factory=list)
    collaboration_indicators: List[str] = field(default_factory=list)
    protection_flags: List[str] = field(default_factory=list)
    monetization_potential: Optional[float] = None
    processing_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            "platform": self.platform,
            "language": self.language,
            "sentiment_score": self.sentiment_score,
            "priority_level": self.priority_level,
            "tags": self.tags,
            "related_content_ids": self.related_content_ids,
            "collaboration_indicators": self.collaboration_indicators,
            "protection_flags": self.protection_flags,
            "monetization_potential": self.monetization_potential,
            "processing_notes": self.processing_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMetadata':
        """Create from dictionary"""        return cls(
            platform=data.get("platform"),
            language=data.get("language"),
            sentiment_score=data.get("sentiment_score"),
            priority_level=data.get("priority_level"),
            tags=data.get("tags", []),
            related_content_ids=data.get("related_content_ids", []),
            collaboration_indicators=data.get("collaboration_indicators", []),
            protection_flags=data.get("protection_flags", []),
            monetization_potential=data.get("monetization_potential"),
            processing_notes=data.get("processing_notes", [])
        )


class ConversationRecord(Base):
    """    Main conversation record for database storage
    
    Stores conversation data with encryption and metadata for
    multi-format content creators with specialized context tracking.
    """    __tablename__ = "conversation_records"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Conversation data
    conversation_data = Column(JSON, nullable=True)  # Encrypted conversation content
    raw_content = Column(Text, nullable=True)  # Raw text content for search
    
    # Classification and context
    content_type = Column(String(50), nullable=False, default=ContentType.GENERAL.value)
    context_type = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default=ConversationStatus.ACTIVE.value)
    
    # Metadata and analytics
    metadata = Column(JSON, nullable=True)  # Additional metadata
    sentiment_score = Column(Float, nullable=True)
    priority_score = Column(Float, nullable=True, default=0.5)
    
    # Vector embeddings for semantic search
    embedding_vector = Column(JSON, nullable=True)  # Stored as JSON array
    
    # Temporal information
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
    # Encryption and security
    is_encrypted = Column(Boolean, default=True)
    encryption_key_id = Column(String(255), nullable=True)
    
    # Indexing and search
    search_vector = Column(Text, nullable=True)  # Full-text search vector
    
    def __init__(self, **kwargs):
        # Handle context parameter
        context = kwargs.pop('context', None)
        super().__init__(**kwargs)
        
        # Set context if provided
        if context:
            self.context = context
    
    @property
    def context(self) -> Optional['ConversationContext']:
        """Get conversation context"""        if not self.metadata:
            return None
        
        context_data = self.metadata.get('context')
        if not context_data:
            return None
        
        context_type = context_data.get('type')
        if context_type == ContextType.CONTENT_CONTEXT.value:
            return ContentContext.from_dict(context_data)
        elif context_type == ContextType.COLLABORATION_CONTEXT.value:
            return CollaborationContext.from_dict(context_data)
        elif context_type == ContextType.PROTECTION_CONTEXT.value:
            return ProtectionContext.from_dict(context_data)
        
        return None
    
    @context.setter
    def context(self, value: Optional['ConversationContext']):
        """Set conversation context"""        if not self.metadata:
            self.metadata = {}
        
        if value:
            self.metadata['context'] = value.to_dict()
        else:
            self.metadata.pop('context', None)
    
    def encrypt_content(self, encryption_manager: EncryptionManager) -> bool:
        """Encrypt conversation content"""        try:
            if self.conversation_data and not self.is_encrypted:
                encrypted_data, key_id = encryption_manager.encrypt_data(
                    json.dumps(self.conversation_data)
                )
                self.conversation_data = {"encrypted": encrypted_data}
                self.encryption_key_id = key_id
                self.is_encrypted = True
                return True
        except Exception:
            return False
        return False
    
    def decrypt_content(self, encryption_manager: EncryptionManager) -> bool:
        """Decrypt conversation content"""        try:
            if self.is_encrypted and self.conversation_data:
                encrypted_data = self.conversation_data.get("encrypted")
                if encrypted_data and self.encryption_key_id:
                    decrypted_data = encryption_manager.decrypt_data(
                        encrypted_data, self.encryption_key_id
                    )
                    self.conversation_data = json.loads(decrypted_data)
                    self.is_encrypted = False
                    return True
        except Exception:
            return False
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""        return {
            "id": str(self.id),
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "conversation_data": self.conversation_data,
            "content_type": self.content_type,
            "context_type": self.context_type,
            "status": self.status,
            "metadata": self.metadata,
            "sentiment_score": self.sentiment_score,
            "priority_score": self.priority_score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class MemoryEntry:
    """    Individual memory entry for conversation components
    
    Represents a single memory item that can be stored in different
    memory systems (short-term, long-term, working memory).
    """    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    user_id: str = ""
    
    # Memory content
    content: Any = None
    content_type: str = ""
    memory_type: MemoryType = MemoryType.SHORT_TERM
    
    # Relevance and importance
    relevance_score: float = 0.5
    importance_score: float = 0.5
    access_count: int = 0
    
    # Temporal information
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    # Relationships
    related_entries: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if memory entry has expired"""        if self.expires_at:
            return datetime.now(timezone.utc) > self.expires_at
        return False
    
    def update_access(self):
        """Update access tracking"""        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)
    
    def calculate_retention_score(self) -> float:
        """Calculate how long this memory should be retained"""        # Combine relevance, importance, and access patterns
        base_score = (self.relevance_score + self.importance_score) / 2
        
        # Boost for frequently accessed memories
        access_boost = min(self.access_count * 0.1, 0.5)
        
        # Recency factor
        age_hours = (datetime.now(timezone.utc) - self.created_at).total_seconds() / 3600
        recency_factor = max(0, 1 - (age_hours / 168))  # Decay over 1 week
        
        return min(base_score + access_boost + (recency_factor * 0.2), 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            "entry_id": self.entry_id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "content": self.content,
            "content_type": self.content_type,
            "memory_type": self.memory_type.value,
            "relevance_score": self.relevance_score,
            "importance_score": self.importance_score,
            "access_count": self.access_count,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "related_entries": self.related_entries,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""        entry = cls(
            entry_id=data.get("entry_id", str(uuid.uuid4())),
            conversation_id=data.get("conversation_id", ""),
            user_id=data.get("user_id", ""),
            content=data.get("content"),
            content_type=data.get("content_type", ""),
            memory_type=MemoryType(data.get("memory_type", MemoryType.SHORT_TERM.value)),
            relevance_score=data.get("relevance_score", 0.5),
            importance_score=data.get("importance_score", 0.5),
            access_count=data.get("access_count", 0),
            related_entries=data.get("related_entries", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
        
        # Parse datetime fields
        if data.get("created_at"):
            entry.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("last_accessed"):
            entry.last_accessed = datetime.fromisoformat(data["last_accessed"])
        if data.get("expires_at"):
            entry.expires_at = datetime.fromisoformat(data["expires_at"])
        
        return entry


# Specialized Context Models

@dataclass
class ConversationContext:
    """Base class for conversation context"""    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context_type: ContextType = ContextType.CONTENT_CONTEXT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            "context_id": self.context_id,
            "type": self.context_type.value,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Create from dictionary"""        context = cls(
            context_id=data.get("context_id", str(uuid.uuid4())),
            context_type=ContextType(data.get("type", ContextType.CONTENT_CONTEXT.value)),
            metadata=data.get("metadata", {})
        )
        
        if data.get("created_at"):
            context.created_at = datetime.fromisoformat(data["created_at"])
        
        return context


@dataclass
class ContentContext(ConversationContext):
    """Context for content creation conversations"""    content_type: str = ""
    content_format: str = ""  # audio, video, image, text
    creation_stage: str = ""  # ideation, production, post_production, distribution
    quality_requirements: Dict[str, Any] = field(default_factory=dict)
    target_platforms: List[str] = field(default_factory=list)
    seo_keywords: List[str] = field(default_factory=list)
    monetization_strategy: str = ""
    collaboration_needs: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.context_type = ContextType.CONTENT_CONTEXT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        base_dict = super().to_dict()
        base_dict.update({
            "content_type": self.content_type,
            "content_format": self.content_format,
            "creation_stage": self.creation_stage,
            "quality_requirements": self.quality_requirements,
            "target_platforms": self.target_platforms,
            "seo_keywords": self.seo_keywords,
            "monetization_strategy": self.monetization_strategy,
            "collaboration_needs": self.collaboration_needs
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentContext':
        """Create from dictionary"""        context = cls(
            context_id=data.get("context_id", str(uuid.uuid4())),
            content_type=data.get("content_type", ""),
            content_format=data.get("content_format", ""),
            creation_stage=data.get("creation_stage", ""),
            quality_requirements=data.get("quality_requirements", {}),
            target_platforms=data.get("target_platforms", []),
            seo_keywords=data.get("seo_keywords", []),
            monetization_strategy=data.get("monetization_strategy", ""),
            collaboration_needs=data.get("collaboration_needs", []),
            metadata=data.get("metadata", {})
        )
        
        if data.get("created_at"):
            context.created_at = datetime.fromisoformat(data["created_at"])
        
        return context


@dataclass
class CollaborationContext(ConversationContext):
    """Context for collaboration conversations"""    collaboration_type: str = ""  # cross_promotion, joint_content, skill_sharing, resource_sharing
    partner_types: List[str] = field(default_factory=list)  # musician, blogger, photographer, etc.
    collaboration_scope: str = ""  # local, national, international
    duration_type: str = ""  # one_time, short_term, long_term, ongoing
    resource_requirements: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    revenue_sharing: Dict[str, Any] = field(default_factory=dict)
    legal_considerations: List[str] = field(default_factory=list)
    communication_preferences: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.context_type = ContextType.COLLABORATION_CONTEXT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        base_dict = super().to_dict()
        base_dict.update({
            "collaboration_type": self.collaboration_type,
            "partner_types": self.partner_types,
            "collaboration_scope": self.collaboration_scope,
            "duration_type": self.duration_type,
            "resource_requirements": self.resource_requirements,
            "expected_outcomes": self.expected_outcomes,
            "revenue_sharing": self.revenue_sharing,
            "legal_considerations": self.legal_considerations,
            "communication_preferences": self.communication_preferences
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollaborationContext':
        """Create from dictionary"""        context = cls(
            context_id=data.get("context_id", str(uuid.uuid4())),
            collaboration_type=data.get("collaboration_type", ""),
            partner_types=data.get("partner_types", []),
            collaboration_scope=data.get("collaboration_scope", ""),
            duration_type=data.get("duration_type", ""),
            resource_requirements=data.get("resource_requirements", []),
            expected_outcomes=data.get("expected_outcomes", []),
            revenue_sharing=data.get("revenue_sharing", {}),
            legal_considerations=data.get("legal_considerations", []),
            communication_preferences=data.get("communication_preferences", {}),
            metadata=data.get("metadata", {})
        )
        
        if data.get("created_at"):
            context.created_at = datetime.fromisoformat(data["created_at"])
        
        return context


@dataclass
class ProtectionContext(ConversationContext):
    """Context for content protection conversations"""    protection_type: str = ""  # copyright, trademark, privacy, unauthorized_use
    content_at_risk: List[str] = field(default_factory=list)
    threat_level: str = ""  # low, medium, high, critical
    violation_platforms: List[str] = field(default_factory=list)
    evidence_collected: List[str] = field(default_factory=list)
    legal_actions_taken: List[str] = field(default_factory=list)
    monitoring_preferences: Dict[str, Any] = field(default_factory=dict)
    notification_settings: Dict[str, Any] = field(default_factory=dict)
    protection_strategies: List[str] = field(default_factory=list)
    financial_impact: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.context_type = ContextType.PROTECTION_CONTEXT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        base_dict = super().to_dict()
        base_dict.update({
            "protection_type": self.protection_type,
            "content_at_risk": self.content_at_risk,
            "threat_level": self.threat_level,
            "violation_platforms": self.violation_platforms,
            "evidence_collected": self.evidence_collected,
            "legal_actions_taken": self.legal_actions_taken,
            "monitoring_preferences": self.monitoring_preferences,
            "notification_settings": self.notification_settings,
            "protection_strategies": self.protection_strategies,
            "financial_impact": self.financial_impact
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtectionContext':
        """Create from dictionary"""        context = cls(
            context_id=data.get("context_id", str(uuid.uuid4())),
            protection_type=data.get("protection_type", ""),
            content_at_risk=data.get("content_at_risk", []),
            threat_level=data.get("threat_level", ""),
            violation_platforms=data.get("violation_platforms", []),
            evidence_collected=data.get("evidence_collected", []),
            legal_actions_taken=data.get("legal_actions_taken", []),
            monitoring_preferences=data.get("monitoring_preferences", {}),
            notification_settings=data.get("notification_settings", {}),
            protection_strategies=data.get("protection_strategies", []),
            financial_impact=data.get("financial_impact", {}),
            metadata=data.get("metadata", {})
        )
        
        if data.get("created_at"):
            context.created_at = datetime.fromisoformat(data["created_at"])
        
        return context


# Export all models
__all__ = [
    # Enums
    "ContentType",
    "ConversationStatus", 
    "MemoryType",
    "ContextType",
    
    # Data classes
    "ConversationMetadata",
    "MemoryEntry",
    
    # Database models
    "ConversationRecord",
    
    # Context models
    "ConversationContext",
    "ContentContext",
    "CollaborationContext", 
    "ProtectionContext"
]
