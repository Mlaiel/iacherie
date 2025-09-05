"""MongoDB Data Models
===================

Data models and schemas for MongoDB collections in the Ainflue platform.
Provides ODM-like functionality with validation, serialization, and relationships.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List, Union, Type, get_type_hints
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import json
from abc import ABC, abstractmethod

try:
    from bson import ObjectId
    from bson.errors import InvalidId
    BSON_AVAILABLE = True
except ImportError:
    BSON_AVAILABLE = False
    # Create mock classes to prevent NameError
    class ObjectId:
        def __init__(self, oid=None):
            self.oid = oid
        def __str__(self):
            return str(self.oid) if self.oid else "000000000000000000000000"
    class InvalidId(Exception):
        pass

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Data validation error."""
    pass

class BaseModel(ABC):
    """Base model class for MongoDB documents."""
    
    def __init__(self, **kwargs):
        """Initialize model with data."""
        self._id: Optional[ObjectId] = kwargs.get('_id')
        self._data: Dict[str, Any] = {}
        self._original_data: Dict[str, Any] = {}
        self._modified_fields: set = set()
        
        # Set field values
        for key, value in kwargs.items():
            if key != '_id':
                setattr(self, key, value)
        
        # Store original data for change tracking
        self._original_data = self._data.copy()
    
    def __setattr__(self, name: str, value: Any):
        """Set attribute with change tracking."""
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            old_value = self._data.get(name) if hasattr(self, '_data') else None
            if hasattr(self, '_data'):
                self._data[name] = value
                if old_value != value and hasattr(self, '_modified_fields'):
                    self._modified_fields.add(name)
            super().__setattr__(name, value)
    
    def __getattr__(self, name: str):
        """Get attribute from data."""
        if hasattr(self, '_data') and name in self._data:
            return self._data[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
    
    @property
    def id(self) -> Optional[str]:
        """Get document ID as string."""
        return str(self._id) if self._id else None
    
    @property
    def object_id(self) -> Optional[ObjectId]:
        """Get ObjectId."""
        return self._id
    
    @property
    def is_new(self) -> bool:
        """Check if document is new (not saved)."""
        return self._id is None
    
    @property
    def is_modified(self) -> bool:
        """Check if document has been modified."""
        return bool(self._modified_fields)
    
    @property
    def modified_fields(self) -> set:
        """Get set of modified field names."""
        return self._modified_fields.copy()
    
    def to_dict(self, include_id: bool = True) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self._data.copy()
        if include_id and self._id:
            data['_id'] = self._id
        return data
    
    def to_json(self, include_id: bool = True) -> str:
        """Convert to JSON string."""
        data = self.to_dict(include_id)
        
        # Convert ObjectId to string for JSON serialization
        def convert_objectid(obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_objectid(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_objectid(item) for item in obj]
            return obj
        
        return json.dumps(convert_objectid(data), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create instance from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseModel':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> List[str]:
        """Validate document data. Return list of error messages."""
        errors = []
        
        # Get type hints for validation
        hints = get_type_hints(self.__class__)
        
        for field_name, field_type in hints.items():
            if field_name.startswith('_'):
                continue
            
            value = self._data.get(field_name)
            
            # Check required fields
            if value is None and not self._is_optional_field(field_type):
                errors.append(f"Field '{field_name}' is required")
                continue
            
            # Type validation
            if value is not None and not self._validate_field_type(value, field_type):
                errors.append(f"Field '{field_name}' has invalid type")
        
        return errors
    
    def _is_optional_field(self, field_type) -> bool:
        """Check if field type is optional."""
        # Handle Union types (Optional is Union[T, None])
        if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
            return type(None) in field_type.__args__
        return False
    
    def _validate_field_type(self, value: Any, expected_type: Type) -> bool:
        """Validate field type."""
        # Handle Union types
        if hasattr(expected_type, '__origin__') and expected_type.__origin__ is Union:
            return any(isinstance(value, arg) for arg in expected_type.__args__ if arg != type(None))
        
        # Handle List types
        if hasattr(expected_type, '__origin__') and expected_type.__origin__ is list:
            if not isinstance(value, list):
                return False
            if expected_type.__args__:
                item_type = expected_type.__args__[0]
                return all(isinstance(item, item_type) for item in value)
            return True
        
        # Handle Dict types
        if hasattr(expected_type, '__origin__') and expected_type.__origin__ is dict:
            return isinstance(value, dict)
        
        # Regular type check
        return isinstance(value, expected_type)
    
    def save_changes(self):
        """Mark changes as saved."""
        self._original_data = self._data.copy()
        self._modified_fields.clear()

@dataclass
class User(BaseModel):
    """User model for Ainflue platform."""
    user_id: str
    email: str
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    creator_type: str = "individual"  # individual, business, agency
    subscription_tier: str = "free"   # free, pro, enterprise
    account_status: str = "active"    # active, suspended, inactive
    skills: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    location: Optional[str] = None
    location_coordinates: Optional[Dict[str, float]] = None
    follower_count: int = 0
    following_count: int = 0
    content_count: int = 0
    engagement_rate: float = 0.0
    verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: Optional[datetime] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    social_links: Dict[str, str] = field(default_factory=dict)

@dataclass
class MediaContent(BaseModel):
    """Media content model."""
    content_id: str
    user_id: str
    title: str
    content_type: str  # video, image, audio, text
    description: Optional[str] = None
    category: Optional[str] = None
    genre: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    fingerprint_hash: Optional[str] = None
    duration: Optional[float] = None  # seconds
    dimensions: Optional[Dict[str, int]] = None  # width, height
    thumbnail_url: Optional[str] = None
    status: str = "draft"  # draft, published, archived, deleted
    visibility: str = "private"  # private, public, unlisted
    processing_status: str = "pending"  # pending, processing, completed, failed
    ai_analysis: Dict[str, Any] = field(default_factory=dict)
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    comment_count: int = 0
    engagement_rate: float = 0.0
    monetization_enabled: bool = False
    revenue_generated: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationProject(BaseModel):
    """Collaboration project model."""
    project_id: str
    title: str
    description: str
    creator_id: str  # Project creator
    collaborators: List[str] = field(default_factory=list)  # User IDs
    status: str = "active"  # active, completed, cancelled
    project_type: str = "content"  # content, campaign, event
    budget: Optional[float] = None
    budget_currency: str = "USD"
    deadline: Optional[datetime] = None
    requirements: List[str] = field(default_factory=list)
    deliverables: List[Dict[str, Any]] = field(default_factory=list)
    applications: List[Dict[str, Any]] = field(default_factory=list)
    messages_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsEvent(BaseModel):
    """Analytics event model."""
    event_id: str
    event_type: str  # view, like, share, comment, etc.
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    properties: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    device_info: Optional[Dict[str, str]] = None
    location_info: Optional[Dict[str, Any]] = None
    referrer: Optional[str] = None
    processed: bool = False

class MongoDBModels:
    """Collection of MongoDB models for Ainflue platform."""
    
    User = User
    MediaContent = MediaContent
    CollaborationProject = CollaborationProject
    AnalyticsEvent = AnalyticsEvent
    
    @classmethod
    def get_model_by_name(cls, name: str) -> Optional[Type[BaseModel]]:
        """Get model class by name."""
        return getattr(cls, name, None)
    
    @classmethod
    def get_all_models(cls) -> Dict[str, Type[BaseModel]]:
        """Get all model classes."""
        return {
            'User': cls.User,
            'MediaContent': cls.MediaContent,
            'CollaborationProject': cls.CollaborationProject,
            'AnalyticsEvent': cls.AnalyticsEvent
        }
    
    @classmethod
    def validate_model_data(cls, model_name: str, data: Dict[str, Any]) -> List[str]:
        """Validate data against model schema."""
        model_class = cls.get_model_by_name(model_name)
        if not model_class:
            return [f"Unknown model: {model_name}"]
        
        try:
            instance = model_class.from_dict(data)
            return instance.validate()
        except Exception as e:
            return [f"Validation error: {str(e)}"]

# Utility functions
def create_object_id() -> ObjectId:
    """Create new ObjectId."""
    if not BSON_AVAILABLE:
        raise ImportError("BSON library not available")
    return ObjectId()

def is_valid_object_id(oid: Union[str, ObjectId]) -> bool:
    """Check if string is valid ObjectId."""
    if not BSON_AVAILABLE:
        return False
    try:
        if isinstance(oid, str):
            ObjectId(oid)
        elif isinstance(oid, ObjectId):
            return True
        else:
            return False
        return True
    except InvalidId:
        return False

def convert_to_object_id(oid: Union[str, ObjectId]) -> Optional[ObjectId]:
    """Convert string to ObjectId safely."""
    if not BSON_AVAILABLE:
        return None
    try:
        if isinstance(oid, ObjectId):
            return oid
        return ObjectId(oid)
    except (InvalidId, TypeError):
        return None

# Export main classes and functions
__all__ = [
    'ValidationError',
    'BaseModel',
    'User',
    'MediaContent',
    'CollaborationProject',
    'AnalyticsEvent',
    'MongoDBModels',
    'create_object_id',
    'is_valid_object_id',
    'convert_to_object_id',
    'BSON_AVAILABLE'
]