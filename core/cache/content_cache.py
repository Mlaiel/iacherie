"""Enterprise Content Cache for IA Influencer Agent Platform
Advanced multimedia content caching with AI processing, protection, and monetization features

Business Logic Integration:
- Creator content management with tenant isolation
- AI-powered content analysis and fingerprinting  
- Content protection and copyright monitoring
- Revenue tracking and monetization analytics
- Multi-platform distribution caching
- Collaboration and team sharing features

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
      Microservices Architect + Audio Processing Expert + DevOps Engineer + IA Prompt Engineer
"""import asyncio
import logging
import json
import hashlib
import uuid
import time
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import mimetypes
import base64
import aiofiles
import os
from collections import defaultdict
import tempfile
import shutil

from .redis_cache import RedisCache, RedisConfig
from .memory_cache import EnterpriseMemoryCache, CacheNamespace, CachePriority
from .vector_cache import VectorCache, FAISSCache, ContentType as VectorContentType

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Enhanced content types for IA Influencer Agent platform"""    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    PODCAST = "podcast"
    MUSIC = "music"
    VOICE_NOTE = "voice_note"
    LIVESTREAM = "livestream"
    SHORT_VIDEO = "short_video"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    UNKNOWN = "unknown"

class ProcessingStatus(Enum):
    """Enhanced processing status tracking"""    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    FINGERPRINTING = "fingerprinting"
    PROTECTING = "protecting"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"

class ContentPriority(Enum):
    """Content priority levels for processing and caching"""    URGENT = 5      # Live content, revenue-critical
    HIGH = 4        # Premium creator content  
    NORMAL = 3      # Standard content
    LOW = 2         # Bulk uploads
    BACKGROUND = 1  # Archive content

class ProtectionLevel(Enum):
    """Content protection levels"""    NONE = "none"
    BASIC = "basic"         # Simple fingerprinting
    ADVANCED = "advanced"   # Multi-vector fingerprinting
    PREMIUM = "premium"     # Real-time monitoring
    ENTERPRISE = "enterprise"  # Custom protection

class MonetizationStatus(Enum):
    """Content monetization status"""    NOT_MONETIZED = "not_monetized"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    GENERATING_REVENUE = "generating_revenue"
    SUSPENDED = "suspended"
    BANNED = "banned"

@dataclass
class ContentMetadata:
    """Enhanced content metadata for IA Influencer Agent platform"""    content_id: str
    creator_id: str  # Changed from user_id for consistency
    tenant_id: Optional[str]
    content_type: ContentType
    original_filename: str
    file_size: int
    mime_type: str
    
    # Upload metadata
    uploaded_at: datetime
    upload_ip: str
    upload_user_agent: str
    upload_session_id: Optional[str] = None
    
    # Enhanced processing metadata
    processing_status: ProcessingStatus
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    processing_progress: float = 0.0
    processing_queue_position: int = 0
    estimated_completion_time: Optional[datetime] = None
    
    # Content properties
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    format_info: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Enhanced protection metadata
    fingerprint_hash: Optional[str] = None
    protection_level: ProtectionLevel = ProtectionLevel.BASIC
    copyright_claimed: bool = False
    dmca_takedowns: int = 0
    violation_count: int = 0
    protection_enabled: bool = True
    monitoring_active: bool = False
    
    # Monetization metadata
    monetization_status: MonetizationStatus = MonetizationStatus.NOT_MONETIZED
    revenue_generated: float = 0.0
    view_revenue: float = 0.0
    download_revenue: float = 0.0
    licensing_revenue: float = 0.0
    subscription_revenue: float = 0.0
    
    # Enhanced analytics
    view_count: int = 0
    download_count: int = 0
    share_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    play_time_total: float = 0.0
    unique_viewers: int = 0
    geographic_views: Dict[str, int] = field(default_factory=dict)
    platform_views: Dict[str, int] = field(default_factory=dict)
    
    # Business metadata
    priority: ContentPriority = ContentPriority.NORMAL
    category: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    genre: Optional[str] = None
    mood: Optional[str] = None
    language: Optional[str] = None
    target_audience: Set[str] = field(default_factory=set)
    
    # Collaboration metadata  
    collaboration_id: Optional[str] = None
    team_members: Set[str] = field(default_factory=set)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    
    # Distribution metadata
    published_platforms: Set[str] = field(default_factory=set)
    scheduled_publish: Optional[datetime] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Set[str] = field(default_factory=set)
    
    # AI processing metadata
    ai_analysis_completed: bool = False
    ai_transcription: Optional[str] = None
    ai_sentiment_score: Optional[float] = None
    ai_content_rating: Optional[str] = None
    ai_recommendations: List[str] = field(default_factory=list)
    content_similarity_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization"""        data = {}
        for key, value in asdict(self).items():
            if isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, datetime):
                data[key] = value.isoformat() if value else None
            elif isinstance(value, set):
                data[key] = list(value)
            else:
                data[key] = value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentMetadata':
        """Create from dictionary with proper deserialization"""        # Convert enum fields
        if 'content_type' in data:
            data['content_type'] = ContentType(data['content_type'])
        if 'processing_status' in data:
            data['processing_status'] = ProcessingStatus(data['processing_status'])
        if 'protection_level' in data:
            data['protection_level'] = ProtectionLevel(data['protection_level'])
        if 'monetization_status' in data:
            data['monetization_status'] = MonetizationStatus(data['monetization_status'])
        if 'priority' in data:
            data['priority'] = ContentPriority(data['priority'])
        
        # Convert datetime fields
        datetime_fields = [
            'uploaded_at', 'processing_started_at', 'processing_completed_at',
            'scheduled_publish', 'estimated_completion_time'
        ]
        for field in datetime_fields:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        # Convert set fields
        set_fields = ['tags', 'target_audience', 'team_members', 'published_platforms', 'seo_keywords']
        for field in set_fields:
            if field in data and isinstance(data[field], list):
                data[field] = set(data[field])
        
        # Handle dict fields with defaults
        dict_fields = ['format_info', 'quality_metrics', 'geographic_views', 'platform_views', 'permissions']
        for field in dict_fields:
            if field not in data:
                data[field] = {}
        
        # Handle list fields with defaults
        list_fields = ['ai_recommendations']
        for field in list_fields:
            if field not in data:
                data[field] = []
                
        return cls(**data)
    
    def update_analytics(self, metric: str, value: Union[int, float] = 1):
        """Update analytics metrics"""        if hasattr(self, metric):
            current_value = getattr(self, metric)
            if isinstance(current_value, (int, float)):
                setattr(self, metric, current_value + value)
    
    def add_platform_view(self, platform: str, count: int = 1):
        """Add platform-specific view"""        self.platform_views[platform] = self.platform_views.get(platform, 0) + count
        self.view_count += count
    
    def add_geographic_view(self, country: str, count: int = 1):
        """Add geographic view"""        self.geographic_views[country] = self.geographic_views.get(country, 0) + count
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate"""        if self.view_count == 0:
            return 0.0
        
        total_engagement = self.like_count + self.comment_count + self.share_count
        return (total_engagement / self.view_count) * 100
    
    def calculate_completion_rate(self) -> float:
        """Calculate content completion rate"""        if not self.duration or self.view_count == 0:
            return 0.0
        
        expected_total_time = self.duration * self.view_count
        return (self.play_time_total / expected_total_time) * 100 if expected_total_time > 0 else 0.0

@dataclass
class ProcessingResult:
    """Enhanced content processing result"""    content_id: str
    processing_type: str
    result_data: Dict[str, Any]
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    created_at: datetime = None
    
    # Enhanced metadata
    model_version: Optional[str] = None
    processing_cost: float = 0.0
    resource_usage: Dict[str, float] = field(default_factory=dict)
    error_details: Optional[str] = None
    retry_count: int = 0
    quality_score: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingResult':
        """Create from dictionary"""        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

@dataclass
class ContentAnalytics:
    """Comprehensive content analytics"""    content_id: str
    creator_id: str
    
    # Time-based metrics
    hourly_views: Dict[str, int] = field(default_factory=dict)  # hour -> views
    daily_views: Dict[str, int] = field(default_factory=dict)   # date -> views
    monthly_revenue: Dict[str, float] = field(default_factory=dict)  # month -> revenue
    
    # User behavior
    average_watch_time: float = 0.0
    bounce_rate: float = 0.0
    retry_rate: float = 0.0
    conversion_rate: float = 0.0
    
    # Performance metrics
    load_time_avg: float = 0.0
    error_rate: float = 0.0
    quality_score: float = 0.0
    
    # Comparative metrics
    peer_performance_percentile: float = 0.0
    trend_score: float = 0.0
    virality_score: float = 0.0
    
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_view(self, timestamp: datetime = None):
        """Add a view with timestamp tracking"""        if not timestamp:
            timestamp = datetime.utcnow()
        
        hour_key = timestamp.strftime('%Y-%m-%d-%H')
        day_key = timestamp.strftime('%Y-%m-%d')
        
        self.hourly_views[hour_key] = self.hourly_views.get(hour_key, 0) + 1
        self.daily_views[day_key] = self.daily_views.get(day_key, 0) + 1
        self.last_updated = datetime.utcnow()
    
    def add_revenue(self, amount: float, timestamp: datetime = None):
        """Add revenue with monthly tracking"""        if not timestamp:
            timestamp = datetime.utcnow()
        
        month_key = timestamp.strftime('%Y-%m')
        self.monthly_revenue[month_key] = self.monthly_revenue.get(month_key, 0) + amount
        self.last_updated = datetime.utcnow()
    
    def get_trend_data(self, days: int = 30) -> Dict[str, Any]:
        """Get trend data for specified days"""        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_views = {}
        total_views = 0
        
        for date_str, views in self.daily_views.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if date_obj >= cutoff_date:
                recent_views[date_str] = views
                total_views += views
        
        return {
            'period_days': days,
            'total_views': total_views,
            'daily_breakdown': recent_views,
            'average_daily_views': total_views / days if days > 0 else 0
        }

class EnterpriseContentCache:
    """    Enterprise-grade content cache for IA Influencer Agent Platform
    
    Features:
    - Multi-tenant creator content management
    - AI-powered content analysis and fingerprinting
    - Real-time content protection and monitoring
    - Revenue tracking and monetization analytics
    - Advanced compression and optimization
    - Collaboration and team sharing
    - Multi-platform distribution support
    - Comprehensive analytics and reporting
    """    
    def __init__(self,
                 redis_config: RedisConfig,
                 vector_cache: Optional[VectorCache] = None,
                 max_file_size: int = 1024 * 1024 * 1024,  # 1GB
                 chunk_size: int = 2 * 1024 * 1024,  # 2MB chunks
                 default_ttl: int = 86400 * 7,  # 7 days
                 temp_storage_path: str = "/tmp/ia_content_cache"):
        
        self.max_file_size = max_file_size
        self.chunk_size = chunk_size
        self.default_ttl = default_ttl
        self.temp_storage_path = temp_storage_path
        
        # Create temp storage directory
        os.makedirs(temp_storage_path, exist_ok=True)
        
        # Initialize caches with enterprise configurations
        self.redis_cache = RedisCache(redis_config)
        self.memory_cache = EnterpriseMemoryCache(config=None)  # Use default config
        self.vector_cache = vector_cache
        
        # Cache key prefixes for organized storage
        self.METADATA_PREFIX = "ia:content:meta"
        self.CHUNK_PREFIX = "ia:content:chunk"
        self.PROCESSING_PREFIX = "ia:content:processing"
        self.FINGERPRINT_PREFIX = "ia:content:fingerprint"
        self.ANALYTICS_PREFIX = "ia:content:analytics"
        self.CREATOR_CONTENT_PREFIX = "ia:creator:content"
        self.COLLABORATION_PREFIX = "ia:collab"
        self.REVENUE_PREFIX = "ia:revenue"
        self.PROTECTION_PREFIX = "ia:protection"
        self.AI_ANALYSIS_PREFIX = "ia:ai:analysis"
        self.DISTRIBUTION_PREFIX = "ia:distribution"
        
        # Enterprise statistics with business logic
        self._stats = {
            'content_uploads': 0,
            'content_downloads': 0,
            'processing_jobs': 0,
            'fingerprints_generated': 0,
            'ai_analyses_completed': 0,
            'copyright_violations_detected': 0,
            'revenue_transactions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'storage_bytes': 0,
            'bandwidth_saved_bytes': 0,
            'processing_cost_saved': 0.0,
            'revenue_facilitated': 0.0
        }
        
        # Creator-specific metrics
        self._creator_stats = defaultdict(lambda: {
            'content_count': 0,
            'storage_used': 0,
            'views_total': 0,
            'revenue_total': 0.0,
            'violations_detected': 0
        })
        
        # Background task management
        self._background_tasks = set()
        self._shutdown_event = asyncio.Event()
        
        logger.info("EnterpriseContentCache initialized")
    
    async def initialize(self):
        """Initialize cache connections and background tasks"""        await self.redis_cache.connect()
        
        # Start background maintenance tasks
        self._background_tasks.add(
            asyncio.create_task(self._analytics_aggregation_task())
        )
        self._background_tasks.add(
            asyncio.create_task(self._content_protection_monitoring_task())
        )
        self._background_tasks.add(
            asyncio.create_task(self._storage_optimization_task())
        )
        
        logger.info("EnterpriseContentCache initialized with background tasks")
    
    def _get_enhanced_content_type(self, filename: str, mime_type: Optional[str] = None, 
                                  metadata: Optional[Dict[str, Any]] = None) -> ContentType:
        """Enhanced content type detection with AI assistance"""        
        # Check metadata hints first
        if metadata:
            category = metadata.get('category', '').lower()
            if 'podcast' in category:
                return ContentType.PODCAST
            elif 'music' in category:
                return ContentType.MUSIC
            elif 'voice' in category:
                return ContentType.VOICE_NOTE
            elif 'live' in category:
                return ContentType.LIVESTREAM
            elif 'short' in category:
                return ContentType.SHORT_VIDEO
            elif 'blog' in category:
                return ContentType.BLOG_POST
            elif 'social' in category:
                return ContentType.SOCIAL_POST
        
        # MIME type detection
        if mime_type:
            if mime_type.startswith('audio/'):
                # Differentiate audio types
                if 'podcast' in filename.lower() or 'episode' in filename.lower():
                    return ContentType.PODCAST
                elif any(genre in filename.lower() for genre in ['music', 'song', 'track', 'album']):
                    return ContentType.MUSIC
                elif 'voice' in filename.lower() or 'note' in filename.lower():
                    return ContentType.VOICE_NOTE
                else:
                    return ContentType.AUDIO
                    
            elif mime_type.startswith('video/'):
                # Differentiate video types
                if 'short' in filename.lower() or 'clip' in filename.lower():
                    return ContentType.SHORT_VIDEO
                elif 'live' in filename.lower() or 'stream' in filename.lower():
                    return ContentType.LIVESTREAM
                else:
                    return ContentType.VIDEO
                    
            elif mime_type.startswith('image/'):
                return ContentType.IMAGE
            elif mime_type.startswith('text/'):
                if 'blog' in filename.lower() or 'post' in filename.lower():
                    return ContentType.BLOG_POST
                elif 'social' in filename.lower():
                    return ContentType.SOCIAL_POST
                else:
                    return ContentType.TEXT
        
        # File extension fallback with enhanced mapping
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        content_type_mapping = {
            # Audio extensions
            'mp3': ContentType.MUSIC, 'wav': ContentType.AUDIO, 'flac': ContentType.MUSIC,
            'aac': ContentType.MUSIC, 'ogg': ContentType.AUDIO, 'm4a': ContentType.MUSIC,
            'wma': ContentType.AUDIO, 'opus': ContentType.VOICE_NOTE,
            
            # Video extensions  
            'mp4': ContentType.VIDEO, 'avi': ContentType.VIDEO, 'mov': ContentType.VIDEO,
            'wmv': ContentType.VIDEO, 'flv': ContentType.SHORT_VIDEO, 'webm': ContentType.SHORT_VIDEO,
            'mkv': ContentType.VIDEO, 'm4v': ContentType.VIDEO,
            
            # Image extensions
            'jpg': ContentType.IMAGE, 'jpeg': ContentType.IMAGE, 'png': ContentType.IMAGE,
            'gif': ContentType.IMAGE, 'bmp': ContentType.IMAGE, 'svg': ContentType.IMAGE,
            'webp': ContentType.IMAGE, 'tiff': ContentType.IMAGE,
            
            # Text/Document extensions
            'txt': ContentType.TEXT, 'md': ContentType.BLOG_POST, 'json': ContentType.TEXT,
            'xml': ContentType.TEXT, 'csv': ContentType.TEXT, 'log': ContentType.TEXT,
            'pdf': ContentType.DOCUMENT, 'doc': ContentType.DOCUMENT, 'docx': ContentType.DOCUMENT,
            'ppt': ContentType.DOCUMENT, 'pptx': ContentType.DOCUMENT
        }
        
        return content_type_mapping.get(ext, ContentType.UNKNOWN)
    
    def _generate_enhanced_content_id(self, creator_id: str, filename: str, 
                                    file_content: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate enhanced content ID with business logic"""        
        # Create compound hash for uniqueness
        content_hash = hashlib.sha256(file_content).hexdigest()[:16]
        metadata_hash = hashlib.md5(json.dumps(metadata or {}, sort_keys=True).encode()).hexdigest()[:8]
        timestamp = int(datetime.utcnow().timestamp())
        
        # Include tenant info if available
        tenant_suffix = f"_{metadata.get('tenant_id', 'default')}" if metadata else ""
        
        return f"{creator_id}_{timestamp}_{content_hash}_{metadata_hash}{tenant_suffix}"
    
    async def _chunk_content_async(self, content: bytes, content_id: str) -> List[Tuple[str, str]]:
        """Asynchronously chunk content for storage"""        chunks = []
        chunk_keys = []
        
        for i in range(0, len(content), self.chunk_size):
            chunk = content[i:i + self.chunk_size]
            chunk_key = f"{self.CHUNK_PREFIX}:{content_id}:{i // self.chunk_size}"
            
            # Compress chunk if beneficial
            chunk_data = base64.b64encode(chunk).decode('utf-8')
            chunks.append((chunk_key, chunk_data))
            chunk_keys.append(chunk_key)
        
        return chunks, chunk_keys
    
    async def upload_content(self,
                           creator_id: str,
                           filename: str,
                           file_content: bytes,
                           mime_type: Optional[str] = None,
                           tenant_id: Optional[str] = None,
                           ip_address: str = "unknown",
                           user_agent: str = "unknown",
                           upload_session_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None,
                           priority: ContentPriority = ContentPriority.NORMAL,
                           enable_ai_analysis: bool = True,
                           enable_protection: bool = True,
                           monetization_enabled: bool = False) -> Optional[str]:
        """Enhanced content upload with comprehensive business logic"""        
        upload_start_time = time.time()
        
        try:
            # Validate file size
            if len(file_content) > self.max_file_size:
                logger.error(f"File too large: {len(file_content)} bytes (max: {self.max_file_size})")
                return None
            
            # Generate content ID
            content_id = self._generate_enhanced_content_id(creator_id, filename, file_content, metadata)
            
            # Enhanced content type detection
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(filename)
            content_type = self._get_enhanced_content_type(filename, mime_type, metadata)
            
            # Create comprehensive metadata
            content_metadata = ContentMetadata(
                content_id=content_id,
                creator_id=creator_id,
                tenant_id=tenant_id,
                content_type=content_type,
                original_filename=filename,
                file_size=len(file_content),
                mime_type=mime_type or "application/octet-stream",
                uploaded_at=datetime.utcnow(),
                upload_ip=ip_address,
                upload_user_agent=user_agent,
                upload_session_id=upload_session_id,
                processing_status=ProcessingStatus.PENDING,
                priority=priority,
                protection_level=ProtectionLevel.ADVANCED if enable_protection else ProtectionLevel.NONE,
                monetization_status=MonetizationStatus.PENDING_APPROVAL if monetization_enabled else MonetizationStatus.NOT_MONETIZED,
                category=metadata.get('category') if metadata else None,
                tags=set(metadata.get('tags', [])) if metadata else set(),
                language=metadata.get('language') if metadata else None
            )
            
            # Store metadata in Redis with enterprise caching
            metadata_key = f"{self.METADATA_PREFIX}:{content_id}"
            await self.redis_cache.set(
                metadata_key,
                json.dumps(content_metadata.to_dict()),
                ttl=self.default_ttl
            )
            
            # Store in memory cache for fast access
            await self.memory_cache.set(
                key=f"meta:{content_id}",
                value=content_metadata,
                creator_id=creator_id,
                namespace=CacheNamespace.CREATOR_CONTENT,
                priority=CachePriority.HIGH if priority == ContentPriority.URGENT else CachePriority.MEDIUM,
                monetization_value=1.0 if monetization_enabled else 0.0,
                tags={'content_metadata'}
            )
            
            # Chunk and store content asynchronously
            chunks, chunk_keys = await self._chunk_content_async(file_content, content_id)
            
            # Store chunks in parallel
            chunk_tasks = []
            for chunk_key, chunk_data in chunks:
                task = self.redis_cache.set(chunk_key, chunk_data, ttl=self.default_ttl)
                chunk_tasks.append(task)
            
            await asyncio.gather(*chunk_tasks)
            
            # Store chunk index
            chunk_index_key = f"{self.CHUNK_PREFIX}:{content_id}:index"
            chunk_index = {
                'total_chunks': len(chunks),
                'chunk_keys': chunk_keys,
                'chunk_size': self.chunk_size,
                'total_size': len(file_content),
                'created_at': datetime.utcnow().isoformat()
            }
            await self.redis_cache.set(
                chunk_index_key,
                json.dumps(chunk_index),
                ttl=self.default_ttl
            )
            
            # Update creator content tracking
            await self._add_creator_content(creator_id, content_id, tenant_id)
            
            # Schedule AI analysis if enabled
            if enable_ai_analysis:
                await self._schedule_ai_analysis(content_id, content_type)
            
            # Schedule protection setup if enabled
            if enable_protection:
                await self._schedule_protection_setup(content_id)
            
            # Update statistics
            self._stats['content_uploads'] += 1
            self._stats['storage_bytes'] += len(file_content)
            
            # Update creator statistics
            creator_stat = self._creator_stats[creator_id]
            creator_stat['content_count'] += 1
            creator_stat['storage_used'] += len(file_content)
            
            upload_time = time.time() - upload_start_time
            logger.info(f"Content uploaded successfully: {content_id} "
                       f"({len(file_content)} bytes, {upload_time:.2f}s, creator: {creator_id})")
            
            return content_id
            
        except Exception as e:
            logger.error(f"Failed to upload content: {e}")
            return None
    
    async def get_content_metadata(self, content_id: str, use_cache: bool = True) -> Optional[ContentMetadata]:
        """Get content metadata with intelligent caching"""        
        if use_cache:
            # Try memory cache first
            cached_metadata = self.memory_cache.get(f"meta:{content_id}")
            if cached_metadata:
                self._stats['cache_hits'] += 1
                return cached_metadata
        
        # Try Redis cache
        metadata_key = f"{self.METADATA_PREFIX}:{content_id}"
        metadata_data = await self.redis_cache.get(metadata_key)
        
        if metadata_data:
            self._stats['cache_hits'] += 1
            metadata_dict = json.loads(metadata_data)
            metadata = ContentMetadata.from_dict(metadata_dict)
            
            # Cache in memory for fast future access
            if use_cache:
                await self.memory_cache.set(
                    key=f"meta:{content_id}",
                    value=metadata,
                    creator_id=metadata.creator_id,
                    namespace=CacheNamespace.CREATOR_CONTENT,
                    priority=CachePriority.HIGH,
                    tags={'content_metadata'}
                )
            
            return metadata
        
        self._stats['cache_misses'] += 1
        return None
    
    async def download_content(self, content_id: str, creator_id: Optional[str] = None,
                             track_analytics: bool = True) -> Optional[bytes]:
        """Enhanced content download with analytics and optimization"""        
        download_start_time = time.time()
        
        try:
            # Get content metadata for validation
            metadata = await self.get_content_metadata(content_id)
            if not metadata:
                self._stats['cache_misses'] += 1
                return None
            
            # Validate access permissions (basic check)
            if creator_id and metadata.creator_id != creator_id:
                # Additional permission checks could be added here
                logger.warning(f"Access attempt by {creator_id} for content owned by {metadata.creator_id}")
            
            # Get chunk index
            chunk_index_key = f"{self.CHUNK_PREFIX}:{content_id}:index"
            chunk_index_data = await self.redis_cache.get(chunk_index_key)
            
            if not chunk_index_data:
                self._stats['cache_misses'] += 1
                return None
            
            chunk_index = json.loads(chunk_index_data)
            total_chunks = chunk_index['total_chunks']
            
            # Retrieve chunks in parallel for better performance
            chunk_tasks = []
            for i in range(total_chunks):
                chunk_key = f"{self.CHUNK_PREFIX}:{content_id}:{i}"
                task = self.redis_cache.get(chunk_key)
                chunk_tasks.append(task)
            
            chunk_results = await asyncio.gather(*chunk_tasks)
            
            # Validate and decode chunks
            content_chunks = []
            for i, chunk_data in enumerate(chunk_results):
                if not chunk_data:
                    logger.error(f"Missing chunk {i} for content {content_id}")
                    return None
                
                try:
                    chunk_bytes = base64.b64decode(chunk_data.encode('utf-8'))
                    content_chunks.append(chunk_bytes)
                except Exception as e:
                    logger.error(f"Failed to decode chunk {i} for content {content_id}: {e}")
                    return None
            
            # Combine chunks
            content = b''.join(content_chunks)
            
            # Verify content integrity
            if len(content) != chunk_index.get('total_size', len(content)):
                logger.error(f"Content size mismatch for {content_id}")
                return None
            
            # Update analytics if enabled
            if track_analytics:
                await self._update_content_analytics(content_id, 'download')
                
                # Update metadata
                metadata.download_count += 1
                await self._update_metadata(content_id, metadata)
            
            # Update statistics
            self._stats['content_downloads'] += 1
            self._stats['cache_hits'] += 1
            self._stats['bandwidth_saved_bytes'] += len(content)
            
            download_time = time.time() - download_start_time
            logger.debug(f"Content downloaded: {content_id} ({len(content)} bytes, {download_time:.2f}s)")
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to download content {content_id}: {e}")
            return None
    
    async def update_content_metadata(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """Update content metadata"""        metadata = await self.get_content_metadata(content_id)
        if not metadata:
            return False
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        
        # Store updated metadata
        metadata_key = f"{self.METADATA_PREFIX}:{content_id}"
        await self.redis_cache.set(
            metadata_key, 
            json.dumps(metadata.to_dict()), 
            ttl=self.default_ttl
        )
        
        # Update memory cache
        cache_key = f"meta:{content_id}"
        self.memory_cache.set(cache_key, metadata, ttl=300)
        
        return True
    
    async def store_processing_result(self,
                                    content_id: str,
                                    processing_type: str,
                                    result_data: Dict[str, Any],
                                    confidence_score: Optional[float] = None) -> bool:
        """Store content processing result"""        
        result = ProcessingResult(
            content_id=content_id,
            processing_type=processing_type,
            result_data=result_data,
            confidence_score=confidence_score,
            created_at=datetime.utcnow()
        )
        
        result_key = f"{self.PROCESSING_PREFIX}:{content_id}:{processing_type}"
        result_data_json = {
            'content_id': result.content_id,
            'processing_type': result.processing_type,
            'result_data': result.result_data,
            'confidence_score': result.confidence_score,
            'created_at': result.created_at.isoformat()
        }
        
        await self.redis_cache.set(
            result_key, 
            json.dumps(result_data_json), 
            ttl=self.default_ttl * 7  # Keep processing results longer
        )
        
        # Update processing status in metadata
        if processing_type == "fingerprint":
            await self.update_content_metadata(content_id, {
                'processing_status': ProcessingStatus.COMPLETED,
                'processing_completed_at': datetime.utcnow(),
                'fingerprint_hash': result_data.get('fingerprint_hash'),
                'protection_enabled': True
            })
            self._stats['fingerprints_generated'] += 1
        
        self._stats['processing_jobs'] += 1
        return True
    
    async def get_processing_result(self, content_id: str, processing_type: str) -> Optional[ProcessingResult]:
        """Get processing result"""        result_key = f"{self.PROCESSING_PREFIX}:{content_id}:{processing_type}"
        result_data = await self.redis_cache.get(result_key)
        
        if result_data:
            result_dict = json.loads(result_data)
            result_dict['created_at'] = datetime.fromisoformat(result_dict['created_at'])
            return ProcessingResult(**result_dict)
        
        return None
    
    async def store_fingerprint(self,
                              content_id: str,
                              fingerprint_vector: List[float],
                              fingerprint_hash: str,
                              metadata: Dict[str, Any]) -> bool:
        """Store content fingerprint in vector cache"""        
        if not self.vector_cache:
            logger.warning("Vector cache not available for fingerprint storage")
            return False
        
        # Store in vector cache for similarity search
        success = self.vector_cache.add_vector(
            content_id=content_id,
            vector=fingerprint_vector,
            metadata=metadata,
            content_type=metadata.get('content_type'),
            fingerprint_hash=fingerprint_hash
        )
        
        if success:
            # Store fingerprint metadata in Redis
            fingerprint_key = f"{self.FINGERPRINT_PREFIX}:{content_id}"
            fingerprint_data = {
                'content_id': content_id,
                'fingerprint_hash': fingerprint_hash,
                'vector_dimension': len(fingerprint_vector),
                'created_at': datetime.utcnow().isoformat(),
                'metadata': metadata
            }
            
            await self.redis_cache.set(
                fingerprint_key, 
                json.dumps(fingerprint_data), 
                ttl=self.default_ttl * 30  # Keep fingerprints for 30 days
            )
            
            logger.info(f"Fingerprint stored for content: {content_id}")
            return True
        
        return False
    
    async def search_similar_content(self,
                                   query_vector: List[float],
                                   content_type: Optional[str] = None,
                                   top_k: int = 10,
                                   min_similarity: float = 0.8) -> List[Dict[str, Any]]:
        """Search for similar content using fingerprint vectors"""        
        if not self.vector_cache:
            logger.warning("Vector cache not available for similarity search")
            return []
        
        # Search in vector cache
        results = self.vector_cache.search_similar(
            query_vector=query_vector,
            top_k=top_k,
            content_type=content_type,
            min_similarity=min_similarity
        )
        
        # Enrich results with content metadata
        enriched_results = []
        for result in results:
            metadata = await self.get_content_metadata(result.content_id)
            if metadata:
                enriched_results.append({
                    'content_id': result.content_id,
                    'similarity_score': result.similarity_score,
                    'content_metadata': metadata.to_dict(),
                    'fingerprint_metadata': result.metadata
                })
        
        return enriched_results
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content and all associated data"""        try:
            # Get metadata first
            metadata = await self.get_content_metadata(content_id)
            if not metadata:
                return False
            
            # Delete chunks
            chunk_index_key = f"{self.CHUNK_PREFIX}:{content_id}:index"
            chunk_index_data = await self.redis_cache.get(chunk_index_key)
            
            if chunk_index_data:
                chunk_index = json.loads(chunk_index_data)
                total_chunks = chunk_index['total_chunks']
                
                # Delete all chunks
                for i in range(total_chunks):
                    chunk_key = f"{self.CHUNK_PREFIX}:{content_id}:{i}"
                    await self.redis_cache.delete(chunk_key)
                
                # Delete chunk index
                await self.redis_cache.delete(chunk_index_key)
            
            # Delete metadata
            metadata_key = f"{self.METADATA_PREFIX}:{content_id}"
            await self.redis_cache.delete(metadata_key)
            
            # Delete from memory cache
            cache_key = f"meta:{content_id}"
            self.memory_cache.delete(cache_key)
            
            # Delete processing results
            processing_keys = await self.redis_cache.keys(f"{self.PROCESSING_PREFIX}:{content_id}:*")
            for key in processing_keys:
                await self.redis_cache.delete(key)
            
            # Delete fingerprint
            fingerprint_key = f"{self.FINGERPRINT_PREFIX}:{content_id}"
            await self.redis_cache.delete(fingerprint_key)
            
            # Remove from vector cache
            if self.vector_cache:
                self.vector_cache.remove_vector(content_id)
            
            # Remove from user content list
            await self._remove_user_content(metadata.user_id, content_id)
            
            # Update statistics
            self._stats['storage_bytes'] -= metadata.file_size
            
            logger.info(f"Content deleted: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete content {content_id}: {e}")
            return False
    
    async def get_user_content(self, user_id: str, limit: int = 100) -> List[ContentMetadata]:
        """Get content list for user"""        user_content_key = f"{self.USER_CONTENT_PREFIX}:{user_id}"
        content_ids_data = await self.redis_cache.get(user_content_key)
        
        if not content_ids_data:
            return []
        
        content_ids = json.loads(content_ids_data)
        content_list = []
        
        for content_id in content_ids[-limit:]:  # Get most recent
            metadata = await self.get_content_metadata(content_id)
            if metadata:
                content_list.append(metadata)
        
        return content_list
    
    async def _add_user_content(self, user_id: str, content_id: str):
        """Add content to user's content list"""        user_content_key = f"{self.USER_CONTENT_PREFIX}:{user_id}"
        content_ids_data = await self.redis_cache.get(user_content_key)
        
        content_ids = json.loads(content_ids_data) if content_ids_data else []
        if content_id not in content_ids:
            content_ids.append(content_id)
        
        await self.redis_cache.set(
            user_content_key, 
            json.dumps(content_ids), 
            ttl=self.default_ttl * 30
        )
    
    async def _remove_user_content(self, user_id: str, content_id: str):
        """Remove content from user's content list"""        user_content_key = f"{self.USER_CONTENT_PREFIX}:{user_id}"
        content_ids_data = await self.redis_cache.get(user_content_key)
        
        if content_ids_data:
            content_ids = json.loads(content_ids_data)
            if content_id in content_ids:
                content_ids.remove(content_id)
                await self.redis_cache.set(
                    user_content_key, 
                    json.dumps(content_ids), 
                    ttl=self.default_ttl * 30
                )
    
    async def _update_analytics(self, content_id: str, metric: str):
        """Update content analytics"""        analytics_key = f"{self.ANALYTICS_PREFIX}:{content_id}"
        analytics_data = await self.redis_cache.get(analytics_key)
        
        analytics = json.loads(analytics_data) if analytics_data else {}
        analytics[metric] = analytics.get(metric, 0) + 1
        analytics['last_updated'] = datetime.utcnow().isoformat()
        
        await self.redis_cache.set(analytics_key, json.dumps(analytics), ttl=self.default_ttl * 7)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""        redis_stats = await self.redis_cache.get_stats()
        memory_stats = self.memory_cache.get_stats()
        vector_stats = self.vector_cache.get_stats() if self.vector_cache else {}
        
        return {
            'content_stats': self._stats,
            'redis_stats': redis_stats,
            'memory_stats': memory_stats,
            'vector_stats': vector_stats,
            'max_file_size_mb': self.max_file_size / (1024 * 1024),
            'chunk_size_kb': self.chunk_size / 1024,
            'storage_usage_mb': self._stats['storage_bytes'] / (1024 * 1024)
        }
    
    async def close(self):
        """Close cache connections"""        await self.redis_cache.close()
        self.memory_cache.close()
        if self.vector_cache:
            self.vector_cache.clear()

class MediaCache(ContentCache):
    """    Specialized cache for audio and video content
    Includes additional features for media processing
    """    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Media-specific prefixes
        self.THUMBNAIL_PREFIX = "media:thumbnail"
        self.WAVEFORM_PREFIX = "media:waveform"
        self.PREVIEW_PREFIX = "media:preview"
    
    async def store_thumbnail(self, content_id: str, thumbnail_data: bytes) -> bool:
        """Store thumbnail for video/image content"""        thumbnail_key = f"{self.THUMBNAIL_PREFIX}:{content_id}"
        thumbnail_b64 = base64.b64encode(thumbnail_data).decode('utf-8')
        
        return await self.redis_cache.set(
            thumbnail_key, 
            thumbnail_b64, 
            ttl=self.default_ttl * 7
        )
    
    async def get_thumbnail(self, content_id: str) -> Optional[bytes]:
        """Get thumbnail for content"""        thumbnail_key = f"{self.THUMBNAIL_PREFIX}:{content_id}"
        thumbnail_b64 = await self.redis_cache.get(thumbnail_key)
        
        if thumbnail_b64:
            return base64.b64decode(thumbnail_b64.encode('utf-8'))
        return None
    
    async def store_waveform(self, content_id: str, waveform_data: List[float]) -> bool:
        """Store audio waveform data"""        waveform_key = f"{self.WAVEFORM_PREFIX}:{content_id}"
        waveform_json = json.dumps(waveform_data)
        
        return await self.redis_cache.set(
            waveform_key, 
            waveform_json, 
            ttl=self.default_ttl * 7
        )
    
    async def get_waveform(self, content_id: str) -> Optional[List[float]]:
        """Get audio waveform data"""        waveform_key = f"{self.WAVEFORM_PREFIX}:{content_id}"
        waveform_json = await self.redis_cache.get(waveform_key)
        
        if waveform_json:
            return json.loads(waveform_json)
        return None
