#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Content Cache - Specialized Caching for Media and Content
========================================================

Advanced content-specific caching with media optimization,
metadata handling, and intelligent content-aware policies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
from pathlib import Path

from ...core.config import get_settings
from ...core.utils import generate_uuid, get_timestamp, calculate_file_hash
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """
Content type categories for specialized caching."""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    METADATA = "metadata"
    FINGERPRINT = "fingerprint"
    UNKNOWN = "unknown"

@dataclass
class ContentMetadata:
    """Content metadata for cache optimization."""
    content_type: ContentType
    mime_type: Optional[str] = None
    size_bytes: int = 0
    duration_seconds: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    quality: Optional[str] = None
    encoding: Optional[str] = None
    fingerprint_hash: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary for serialization."""
        return {
            "content_type": self.content_type.value,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "duration_seconds": self.duration_seconds,
            "dimensions": list(self.dimensions) if self.dimensions else None,
            "quality": self.quality,
            "encoding": self.encoding,
            "fingerprint_hash": self.fingerprint_hash,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentMetadata':
        """Create from dictionary."""
        dimensions = None
        if data.get('dimensions'):
            dimensions = tuple(data['dimensions'])
        
        return cls(
            content_type=ContentType(data['content_type']),
            mime_type=data.get('mime_type'),
            size_bytes=data.get('size_bytes', 0),
            duration_seconds=data.get('duration_seconds'),
            dimensions=dimensions,
            quality=data.get('quality'),
            encoding=data.get('encoding'),
            fingerprint_hash=data.get('fingerprint_hash'),
            created_at=datetime.fromisoformat(data['created_at']),
            tags=data.get('tags', [])
        )

@dataclass
class CachedContent:
    """
Cached content with metadata and optimization."""
    key: str
    content: Any
    metadata: ContentMetadata
    cached_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    compression_ratio: float = 1.0
    encrypted: bool = False

class ContentCache:
    """
    Advanced content cache for media and metadata.
    
    Features:
    - Content-type aware caching
    - Intelligent TTL based on content type
    - Media compression and optimization
    - Metadata indexing
    - Content fingerprinting integration
    - Multi-format support
    """
    
    def __init__(self, backend: str = "redis", cache_manager: Optional[CacheManager] = None):
        """
        Initialize content cache.
        
        Args:
            backend: Cache backend to use
            cache_manager: Existing cache manager instance
        """
        self.backend = backend
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(f"{__name__}.ContentCache")
        
        # Content-specific configuration
        self.ttl_by_type = {
            ContentType.AUDIO: 7200,      # 2 hours
            ContentType.VIDEO: 3600,      # 1 hour
            ContentType.IMAGE: 1800,      # 30 minutes
            ContentType.TEXT: 3600,       # 1 hour
            ContentType.DOCUMENT: 7200,   # 2 hours
            ContentType.METADATA: 86400,  # 24 hours
            ContentType.FINGERPRINT: 604800,  # 1 week
            ContentType.UNKNOWN: 1800     # 30 minutes
        }
        
        # Size limits by content type (bytes)
        self.size_limits = {
            ContentType.AUDIO: 52428800,      # 50MB
            ContentType.VIDEO: 104857600,     # 100MB
            ContentType.IMAGE: 10485760,      # 10MB
            ContentType.TEXT: 1048576,        # 1MB
            ContentType.DOCUMENT: 5242880,    # 5MB
            ContentType.METADATA: 102400,     # 100KB
            ContentType.FINGERPRINT: 1024,    # 1KB
            ContentType.UNKNOWN: 1048576      # 1MB
        }
        
        # Compression settings
        self.compression_thresholds = {
            ContentType.AUDIO: 1048576,   # 1MB
            ContentType.VIDEO: 2097152,   # 2MB
            ContentType.IMAGE: 524288,    # 512KB
            ContentType.TEXT: 1024,       # 1KB
            ContentType.DOCUMENT: 10240,  # 10KB
            ContentType.METADATA: 512,    # 512B
            ContentType.FINGERPRINT: 0,   # Never compress
            ContentType.UNKNOWN: 10240    # 10KB
        }
        
        # Key prefixes
        self.key_prefixes = {
            "content": "content:",
            "metadata": "meta:",
            "index": "idx:",
            "fingerprint": "fp:"
        }
        
        self.logger.info(f"Content cache initialized with {backend} backend")
    
    async def _get_cache_manager(self) -> CacheManager:
        """Get cache manager instance."""
        if self.cache_manager is None:
            from .cache_manager import get_cache_manager
            self.cache_manager = await get_cache_manager()
        return self.cache_manager
    
    def _detect_content_type(self, content: Any, mime_type: Optional[str] = None) -> ContentType:
        """
Detect content type from content and mime type."""
        if mime_type:
            if mime_type.startswith('audio/'):
                return ContentType.AUDIO
            elif mime_type.startswith('video/'):
                return ContentType.VIDEO
            elif mime_type.startswith('image/'):
                return ContentType.IMAGE
            elif mime_type.startswith('text/'):
                return ContentType.TEXT
            elif mime_type in ['application/pdf', 'application/msword']:
                return ContentType.DOCUMENT
        
        # Analyze content structure for metadata
        if isinstance(content, dict):
            if 'fingerprint' in content or 'hash' in content:
                return ContentType.FINGERPRINT
            elif any(key in content for key in ['title', 'artist', 'album']):
                return ContentType.METADATA
        
        return ContentType.UNKNOWN
    
    def _create_metadata(self, content: Any, content_type: ContentType, 
                        **kwargs) -> ContentMetadata:
        """
Create metadata for content."""
        metadata = ContentMetadata(content_type=content_type)
        
        # Update with provided metadata
        for key, value in kwargs.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        
        # Calculate size
        if isinstance(content, (str, bytes)):
            metadata.size_bytes = len(content)
        elif isinstance(content, dict):
            metadata.size_bytes = len(json.dumps(content).encode())
        
        # Auto-detect mime type if not provided
        if not metadata.mime_type and content_type != ContentType.UNKNOWN:
            type_map = {
                ContentType.AUDIO: 'audio/mpeg',
                ContentType.VIDEO: 'video/mp4',
                ContentType.IMAGE: 'image/jpeg',
                ContentType.TEXT: 'text/plain',
                ContentType.DOCUMENT: 'application/octet-stream',
                ContentType.METADATA: 'application/json',
                ContentType.FINGERPRINT: 'application/json'
            }
            metadata.mime_type = type_map.get(content_type)
        
        return metadata
    
    def _make_content_key(self, key: str, content_type: ContentType) -> str:
        """
Create content-specific cache key."""
        prefix = self.key_prefixes["content"]
        type_prefix = content_type.value[:4]  # e.g., "audi", "vide"
        return f"{prefix}{type_prefix}:{key}"
    
    def _make_metadata_key(self, content_key: str) -> str:
        """Create metadata key for content."""
        return f"{self.key_prefixes['metadata']}{content_key}"
    
    def _make_index_key(self, index_type: str, value: str) -> str:
        """Create index key for lookups."""
        return f"{self.key_prefixes['index']}{index_type}:{value}"
    
    async def store_content(self, key: str, content: Any, 
                          content_type: Optional[ContentType] = None,
                          metadata: Optional[ContentMetadata] = None,
                          ttl: Optional[int] = None,
                          **kwargs) -> bool:
        """
        Store content with metadata and optimization.
        
        Args:
            key: Content key
            content: Content to store
            content_type: Content type (auto-detected if None)
            metadata: Content metadata
            ttl: Time to live override
            **kwargs: Additional metadata fields
            
        Returns:
            True if successful
        """
        try:
            cache_manager = await self._get_cache_manager()
            
            # Detect or use provided content type
            if content_type is None:
                content_type = self._detect_content_type(content, kwargs.get('mime_type'))
            
            # Create or update metadata
            if metadata is None:
                metadata = self._create_metadata(content, content_type, **kwargs)
            
            # Check size limits
            if metadata.size_bytes > self.size_limits.get(content_type, 0):
                self.logger.warning(f"Content too large for type {content_type}: {metadata.size_bytes} bytes")
                return False
            
            # Create cache keys
            content_key = self._make_content_key(key, content_type)
            metadata_key = self._make_metadata_key(content_key)
            
            # Determine TTL
            if ttl is None:
                ttl = self.ttl_by_type.get(content_type, 3600)
            
            # Store content
            content_stored = await cache_manager.set(content_key, content, ttl)
            if not content_stored:
                return False
            
            # Store metadata
            metadata_stored = await cache_manager.set(
                metadata_key, 
                metadata.to_dict(), 
                ttl + 86400  # Metadata lives longer
            )
            
            # Create indexes for efficient lookups
            await self._create_indexes(key, content_type, metadata)
            
            self.logger.debug(f"Stored content {key} as {content_type.value}")
            return content_stored and metadata_stored
            
        except Exception as e:
            self.logger.error(f"Error storing content {key}: {e}")
            return False
    
    async def get_content(self, key: str, 
                         content_type: Optional[ContentType] = None) -> Optional[Tuple[Any, ContentMetadata]]:
        """
        Get content with metadata.
        
        Args:
            key: Content key
            content_type: Expected content type (for optimization)
            
        Returns:
            Tuple of (content, metadata) or None if not found
        """
        try:
            cache_manager = await self._get_cache_manager()
            
            # If content type is known, try direct lookup
            if content_type:
                content_key = self._make_content_key(key, content_type)
                content = await cache_manager.get(content_key)
                
                if content is not None:
                    metadata = await self._get_content_metadata(content_key)
                    return content, metadata
            
            # Try all content types
            for ctype in ContentType:
                content_key = self._make_content_key(key, ctype)
                content = await cache_manager.get(content_key)
                
                if content is not None:
                    metadata = await self._get_content_metadata(content_key)
                    return content, metadata
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting content {key}: {e}")
            return None
    
    async def get_content_metadata(self, key: str, 
                                 content_type: Optional[ContentType] = None) -> Optional[ContentMetadata]:
        """Get only content metadata."""
        try:
            # If content type is known, try direct lookup
            if content_type:
                content_key = self._make_content_key(key, content_type)
                return await self._get_content_metadata(content_key)
            
            # Try all content types
            for ctype in ContentType:
                content_key = self._make_content_key(key, ctype)
                metadata = await self._get_content_metadata(content_key)
                if metadata:
                    return metadata
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting metadata for {key}: {e}")
            return None
    
    async def _get_content_metadata(self, content_key: str) -> Optional[ContentMetadata]:
        """Get metadata for content key."""
        try:
            cache_manager = await self._get_cache_manager()
            metadata_key = self._make_metadata_key(content_key)
            
            metadata_dict = await cache_manager.get(metadata_key)
            if metadata_dict:
                return ContentMetadata.from_dict(metadata_dict)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting metadata for {content_key}: {e}")
            return None
    
    async def delete_content(self, key: str, 
                           content_type: Optional[ContentType] = None) -> bool:
        """
        Delete content and its metadata.
        
        Args:
            key: Content key
            content_type: Content type (all types if None)
            
        Returns:
            True if any content was deleted
        """
        try:
            cache_manager = await self._get_cache_manager()
            deleted = False
            
            # Content types to check
            types_to_check = [content_type] if content_type else list(ContentType)
            
            for ctype in types_to_check:
                content_key = self._make_content_key(key, ctype)
                metadata_key = self._make_metadata_key(content_key)
                
                # Delete content and metadata
                content_deleted = await cache_manager.delete(content_key)
                metadata_deleted = await cache_manager.delete(metadata_key)
                
                if content_deleted or metadata_deleted:
                    deleted = True
                    await self._remove_indexes(key, ctype)
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting content {key}: {e}")
            return False
    
    async def find_by_fingerprint(self, fingerprint_hash: str) -> List[Tuple[str, ContentMetadata]]:
        """Find content by fingerprint hash."""
        try:
            cache_manager = await self._get_cache_manager()
            index_key = self._make_index_key("fingerprint", fingerprint_hash)
            
            content_keys = await cache_manager.get(index_key)
            if not content_keys:
                return []
            
            results = []
            for content_key in content_keys:
                metadata = await self._get_content_metadata(content_key)
                if metadata:
                    # Extract original key from content_key
                    original_key = content_key.split(':', 2)[-1]
                    results.append((original_key, metadata))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error finding by fingerprint {fingerprint_hash}: {e}")
            return []
    
    async def find_by_type(self, content_type: ContentType, 
                          limit: int = 100) -> List[Tuple[str, ContentMetadata]]:
        """Find content by type."""
        try:
            cache_manager = await self._get_cache_manager()
            
            # This would require implementing a type index
            # For now, we'll return empty list
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding by type {content_type}: {e}")
            return []
    
    async def _create_indexes(self, key: str, content_type: ContentType, 
                            metadata: ContentMetadata) -> None:
        """Create indexes for efficient lookups."""
        try:
            cache_manager = await self._get_cache_manager()
            content_key = self._make_content_key(key, content_type)
            
            # Fingerprint index
            if metadata.fingerprint_hash:
                index_key = self._make_index_key("fingerprint", metadata.fingerprint_hash)
                existing_keys = await cache_manager.get(index_key) or []
                if content_key not in existing_keys:
                    existing_keys.append(content_key)
                    await cache_manager.set(index_key, existing_keys, 86400)  # 24 hours
            
            # Type index
            type_index_key = self._make_index_key("type", content_type.value)
            existing_keys = await cache_manager.get(type_index_key) or []
            if content_key not in existing_keys:
                existing_keys.append(content_key)
                # Keep only recent entries
                if len(existing_keys) > 1000:
                    existing_keys = existing_keys[-1000:]
                await cache_manager.set(type_index_key, existing_keys, 86400)
            
        except Exception as e:
            self.logger.error(f"Error creating indexes for {key}: {e}")
    
    async def _remove_indexes(self, key: str, content_type: ContentType) -> None:
        """Remove content from indexes."""
        try:
            cache_manager = await self._get_cache_manager()
            content_key = self._make_content_key(key, content_type)
            
            # Remove from type index
            type_index_key = self._make_index_key("type", content_type.value)
            existing_keys = await cache_manager.get(type_index_key) or []
            if content_key in existing_keys:
                existing_keys.remove(content_key)
                await cache_manager.set(type_index_key, existing_keys, 86400)
            
        except Exception as e:
            self.logger.error(f"Error removing indexes for {key}: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get content cache statistics."""
        try:
            cache_manager = await self._get_cache_manager()
            
            stats = {
                "content_types": {},
                "total_size_by_type": {},
                "average_size_by_type": {}
            }
            
            # Count content by type
            for content_type in ContentType:
                type_index_key = self._make_index_key("type", content_type.value)
                content_keys = await cache_manager.get(type_index_key) or []
                stats["content_types"][content_type.value] = len(content_keys)
                
                # Calculate total size for this type
                total_size = 0
                valid_count = 0
                
                for content_key in content_keys[:100]:  # Sample first 100
                    metadata = await self._get_content_metadata(content_key)
                    if metadata:
                        total_size += metadata.size_bytes
                        valid_count += 1
                
                stats["total_size_by_type"][content_type.value] = total_size
                if valid_count > 0:
                    stats["average_size_by_type"][content_type.value] = total_size / valid_count
                else:
                    stats["average_size_by_type"][content_type.value] = 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting content cache stats: {e}")
            return {}

class MediaCache(ContentCache):
    """
    Specialized cache for media content (audio, video, images).
    
    Enhanced with media-specific optimizations and transformations.
    """
    
    def __init__(self, **kwargs):
        """
Initialize media cache."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(f"{__name__}.MediaCache")
        
        # Media-specific settings
        self.enable_thumbnails = True
        self.thumbnail_sizes = [(128, 128), (256, 256)]
        self.enable_previews = True
        self.preview_duration = 30  # seconds

class MetadataCache(ContentCache):
    """
    Specialized cache for metadata and structured data.
    
    Optimized for fast lookups and complex queries.
    """
    
    def __init__(self, **kwargs):
        """
Initialize metadata cache."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(f"{__name__}.MetadataCache")
        
        # Focus on metadata and structured content
        self.supported_types = [
            ContentType.METADATA,
            ContentType.FINGERPRINT,
            ContentType.TEXT
        ]
