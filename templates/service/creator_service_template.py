"""{{service_name}} Creator Service for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Set
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from pydantic import BaseModel, Field, validator, EmailStr
import aioredis
from fastapi import HTTPException

from core.base_service import BaseService
from core.config import get_settings
from core.database import get_async_session
from core.exceptions import ServiceException, ValidationError, AuthorizationError
from models.creator import Creator, CreatorProfile, CreatorStats, CreatorSettings
from models.content import Content, ContentStats
from models.collaboration import Collaboration, CollaborationRequest
from services.content_service import ContentService
from services.analytics_service import AnalyticsService
from services.notification_service import NotificationService
from utils.validation import validate_creator_data
from utils.image_processing import process_profile_image
from monitoring.creator_metrics import CreatorMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class CreatorStatus(Enum):
    """Creator account status"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    VERIFICATION_REQUIRED = "verification_required"


class CreatorType(Enum):
    """Types of creators"""
    MUSICIAN = "musician"
    PODCASTER = "podcaster"
    VIDEO_CREATOR = "video_creator"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    ARTIST = "artist"
    INFLUENCER = "influencer"
    BRAND = "brand"
    MULTI_CREATOR = "multi_creator"


class VerificationLevel(Enum):
    """Creator verification levels"""
    UNVERIFIED = "unverified"
    EMAIL_VERIFIED = "email_verified"
    PHONE_VERIFIED = "phone_verified"
    IDENTITY_VERIFIED = "identity_verified"
    PROFESSIONAL_VERIFIED = "professional_verified"
    CELEBRITY_VERIFIED = "celebrity_verified"


class CreatorRequest(BaseModel):
    """Creator registration/update request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: Optional[str] = Field(None, min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    creator_type: CreatorType
    bio: Optional[str] = Field(None, max_length=1000)
    location: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = None
    social_links: Dict[str, str] = Field(default_factory=dict)
    specialties: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower()

    @validator('specialties')
    def validate_specialties(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 specialties allowed')
        return v


class CreatorResponse(BaseModel):
    """Creator response model"""
    creator_id: str
    username: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    creator_type: CreatorType
    status: CreatorStatus
    verification_level: VerificationLevel
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    social_links: Dict[str, str] = Field(default_factory=dict)
    specialties: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    follower_count: int = 0
    following_count: int = 0
    content_count: int = 0
    total_views: int = 0
    total_likes: int = 0
    joined_date: datetime
    last_active: Optional[datetime] = None
    is_premium: bool = False
    subscription_tier: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreatorSearchRequest(BaseModel):
    """Creator search request"""
    query: Optional[str] = None
    creator_types: List[CreatorType] = Field(default_factory=list)
    specialties: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    verification_levels: List[VerificationLevel] = Field(default_factory=list)
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    is_premium: Optional[bool] = None
    languages: List[str] = Field(default_factory=list)
    sort_by: str = "relevance"  # relevance, followers, activity, joined_date
    sort_order: str = "desc"  # asc, desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class CreatorConfig(BaseModel):
    """Creator service configuration"""
    enable_auto_verification: bool = True
    enable_creator_matching: bool = True
    enable_analytics_tracking: bool = True
    enable_content_moderation: bool = True
    max_daily_uploads: int = 50
    max_profile_image_size: int = 5 * 1024 * 1024  # 5MB
    max_bio_length: int = 1000
    require_email_verification: bool = True
    enable_premium_features: bool = True
    cache_ttl_seconds: int = 300


class {{service_class_name}}(BaseService):
    """
    Advanced creator service for Ainflue platform.
    
    Features:
    - Creator registration and profile management
    - Multi-type creator support (musicians, bloggers, etc.)
    - Verification and trust system
    - Creator discovery and search
    - Analytics and insights tracking
    - Collaboration management
    - Content workflow integration
    - Social features (followers, following)
    - Premium subscription management
    - Creator monetization tools
    - Performance optimization with caching
    """
    
    def __init__(
        self,
        name: str = "{{service_name}}",
        config: Optional[CreatorConfig] = None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.config = config or CreatorConfig()
        
        # Initialize related services
        self.content_service = ContentService()
        self.analytics_service = AnalyticsService()
        self.notification_service = NotificationService()
        
        # Initialize metrics collector
        self.metrics = CreatorMetricsCollector()
        
        # Redis client for caching
        self.redis_client = None
        
        logger.info(f"Creator service '{name}' initialized successfully")

    async def initialize(self) -> None:
        """Initialize the creator service"""
        try:
            # Initialize Redis for caching
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            logger.info("Creator service initialized successfully")
            
        except Exception as e:
            logger.error(f"Creator service initialization failed: {str(e)}")
            raise ServiceException(f"Initialization failed: {str(e)}")

    async def register_creator(
        self,
        request: CreatorRequest,
        db: AsyncSession = None
    ) -> CreatorResponse:
        """
        Register a new creator.
        
        Args:
            request: Creator registration request
            db: Database session
            
        Returns:
            CreatorResponse with created creator data
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Validate request data
            await self._validate_creator_request(request, db)
            
            # Hash password if provided
            password_hash = None
            if request.password:
                password_hash = bcrypt.hashpw(
                    request.password.encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
            
            # Create creator record
            creator_id = str(uuid.uuid4())
            creator = Creator(
                creator_id=creator_id,
                username=request.username,
                email=request.email,
                password_hash=password_hash,
                first_name=request.first_name,
                last_name=request.last_name,
                display_name=f"{request.first_name} {request.last_name}",
                creator_type=request.creator_type,
                status=CreatorStatus.PENDING if self.config.require_email_verification else CreatorStatus.ACTIVE,
                verification_level=VerificationLevel.UNVERIFIED,
                joined_date=datetime.utcnow()
            )
            
            db.add(creator)
            
            # Create creator profile
            profile = CreatorProfile(
                creator_id=creator_id,
                bio=request.bio,
                location=request.location,
                website=request.website,
                social_links=request.social_links,
                specialties=request.specialties,
                languages=request.languages,
                metadata=request.metadata
            )
            
            db.add(profile)
            
            # Create creator stats
            stats = CreatorStats(
                creator_id=creator_id,
                follower_count=0,
                following_count=0,
                content_count=0,
                total_views=0,
                total_likes=0,
                total_shares=0
            )
            
            db.add(stats)
            
            # Create creator settings with defaults
            settings = CreatorSettings(
                creator_id=creator_id,
                privacy_settings={'profile_public': True, 'show_email': False},
                notification_settings={'email_notifications': True, 'push_notifications': True},
                content_settings={'auto_publish': False, 'content_moderation': True}
            )
            
            db.add(settings)
            
            await db.commit()
            
            # Convert to response
            creator_response = await self._creator_to_response(creator, profile, stats)
            
            # Send verification email if required
            if self.config.require_email_verification:
                await self._send_verification_email(creator)
            
            # Record metrics
            await self.metrics.record_creator_registered(
                creator_type=request.creator_type.value,
                verification_required=self.config.require_email_verification
            )
            
            # Send welcome notification
            await self.notification_service.send_welcome_notification(creator_id)
            
            return creator_response
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Creator registration failed: {str(e)}")
            raise ServiceException(f"Registration failed: {str(e)}")

    async def get_creator(
        self,
        creator_id: str,
        include_stats: bool = True,
        db: AsyncSession = None
    ) -> Optional[CreatorResponse]:
        """
        Get creator by ID.
        
        Args:
            creator_id: Creator identifier
            include_stats: Whether to include statistics
            db: Database session
            
        Returns:
            CreatorResponse if found, None otherwise
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Check cache first
            cache_key = f"creator:{creator_id}"
            cached_data = await self._get_from_cache(cache_key)
            
            if cached_data:
                return CreatorResponse(**cached_data)
            
            # Query database
            query = select(Creator).where(Creator.creator_id == creator_id)
            result = await db.execute(query)
            creator = result.scalar_one_or_none()
            
            if not creator:
                return None
            
            # Get profile
            profile_query = select(CreatorProfile).where(CreatorProfile.creator_id == creator_id)
            profile_result = await db.execute(profile_query)
            profile = profile_result.scalar_one_or_none()
            
            # Get stats if requested
            stats = None
            if include_stats:
                stats_query = select(CreatorStats).where(CreatorStats.creator_id == creator_id)
                stats_result = await db.execute(stats_query)
                stats = stats_result.scalar_one_or_none()
            
            # Convert to response
            creator_response = await self._creator_to_response(creator, profile, stats)
            
            # Cache the result
            await self._set_cache(cache_key, creator_response.dict())
            
            return creator_response
            
        except Exception as e:
            logger.error(f"Failed to get creator {creator_id}: {str(e)}")
            raise ServiceException(f"Failed to get creator: {str(e)}")

    async def update_creator(
        self,
        creator_id: str,
        updates: Dict[str, Any],
        updated_by: str,
        db: AsyncSession = None
    ) -> CreatorResponse:
        """
        Update creator information.
        
        Args:
            creator_id: Creator identifier
            updates: Fields to update
            updated_by: ID of user making the update
            db: Database session
            
        Returns:
            Updated CreatorResponse
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Verify authorization
            if not await self._can_update_creator(creator_id, updated_by, db):
                raise AuthorizationError("Not authorized to update this creator")
            
            # Get current creator
            creator = await self._get_creator_by_id(creator_id, db)
            if not creator:
                raise ValidationError("Creator not found")
            
            # Update creator fields
            creator_updates = {}
            profile_updates = {}
            
            # Separate updates by table
            creator_fields = {'username', 'email', 'first_name', 'last_name', 'creator_type', 'status'}
            profile_fields = {'bio', 'location', 'website', 'social_links', 'specialties', 'languages'}
            
            for field, value in updates.items():
                if field in creator_fields:
                    creator_updates[field] = value
                elif field in profile_fields:
                    profile_updates[field] = value
            
            # Update creator record
            if creator_updates:
                creator_updates['updated_at'] = datetime.utcnow()
                await db.execute(
                    update(Creator)
                    .where(Creator.creator_id == creator_id)
                    .values(**creator_updates)
                )
            
            # Update profile record
            if profile_updates:
                profile_updates['updated_at'] = datetime.utcnow()
                await db.execute(
                    update(CreatorProfile)
                    .where(CreatorProfile.creator_id == creator_id)
                    .values(**profile_updates)
                )
            
            await db.commit()
            
            # Clear cache
            await self._clear_creator_cache(creator_id)
            
            # Get updated creator
            updated_creator = await self.get_creator(creator_id, db=db)
            
            # Record metrics
            await self.metrics.record_creator_updated(
                creator_id=creator_id,
                fields_updated=list(updates.keys())
            )
            
            return updated_creator
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update creator {creator_id}: {str(e)}")
            raise ServiceException(f"Update failed: {str(e)}")

    async def search_creators(
        self,
        search_request: CreatorSearchRequest,
        requester_id: Optional[str] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Search for creators based on criteria.
        
        Args:
            search_request: Search parameters
            requester_id: ID of user making the request
            db: Database session
            
        Returns:
            Search results with pagination
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Build base query
            query = select(Creator).join(CreatorProfile, isouter=True).join(CreatorStats, isouter=True)
            
            # Apply filters
            conditions = []
            
            # Text search
            if search_request.query:
                text_conditions = [
                    Creator.username.ilike(f"%{search_request.query}%"),
                    Creator.display_name.ilike(f"%{search_request.query}%"),
                    CreatorProfile.bio.ilike(f"%{search_request.query}%")
                ]
                conditions.append(or_(*text_conditions))
            
            # Creator types
            if search_request.creator_types:
                conditions.append(Creator.creator_type.in_([ct.value for ct in search_request.creator_types]))
            
            # Location
            if search_request.location:
                conditions.append(CreatorProfile.location.ilike(f"%{search_request.location}%"))
            
            # Verification levels
            if search_request.verification_levels:
                conditions.append(Creator.verification_level.in_([vl.value for vl in search_request.verification_levels]))
            
            # Follower count range
            if search_request.min_followers is not None:
                conditions.append(CreatorStats.follower_count >= search_request.min_followers)
            
            if search_request.max_followers is not None:
                conditions.append(CreatorStats.follower_count <= search_request.max_followers)
            
            # Premium status
            if search_request.is_premium is not None:
                conditions.append(Creator.is_premium == search_request.is_premium)
            
            # Apply all conditions
            if conditions:
                query = query.where(and_(*conditions))
            
            # Apply sorting
            if search_request.sort_by == "followers":
                order_col = CreatorStats.follower_count
            elif search_request.sort_by == "activity":
                order_col = Creator.last_active
            elif search_request.sort_by == "joined_date":
                order_col = Creator.joined_date
            else:  # relevance
                order_col = Creator.created_at
            
            if search_request.sort_order == "asc":
                query = query.order_by(order_col.asc())
            else:
                query = query.order_by(order_col.desc())
            
            # Count total results
            count_query = select(Creator.creator_id).select_from(query.subquery())
            total_count = len((await db.execute(count_query)).fetchall())
            
            # Apply pagination
            offset = (search_request.page - 1) * search_request.page_size
            query = query.offset(offset).limit(search_request.page_size)
            
            # Execute query
            result = await db.execute(query)
            creators = result.fetchall()
            
            # Convert to responses
            creator_responses = []
            for creator_row in creators:
                creator = creator_row.Creator
                profile = creator_row.CreatorProfile
                stats = creator_row.CreatorStats
                
                response = await self._creator_to_response(creator, profile, stats)
                creator_responses.append(response)
            
            # Calculate pagination info
            total_pages = (total_count + search_request.page_size - 1) // search_request.page_size
            
            search_results = {
                'creators': creator_responses,
                'pagination': {
                    'current_page': search_request.page,
                    'page_size': search_request.page_size,
                    'total_pages': total_pages,
                    'total_count': total_count,
                    'has_next': search_request.page < total_pages,
                    'has_prev': search_request.page > 1
                },
                'search_metadata': {
                    'query': search_request.query,
                    'filters_applied': len([f for f in [
                        search_request.creator_types,
                        search_request.specialties,
                        search_request.location,
                        search_request.verification_levels
                    ] if f]),
                    'sort_by': search_request.sort_by,
                    'sort_order': search_request.sort_order
                }
            }
            
            # Record search metrics
            await self.metrics.record_creator_search(
                query=search_request.query,
                filters_count=search_results['search_metadata']['filters_applied'],
                results_count=len(creator_responses),
                requester_id=requester_id
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Creator search failed: {str(e)}")
            raise ServiceException(f"Search failed: {str(e)}")

    async def follow_creator(
        self,
        follower_id: str,
        creator_id: str,
        db: AsyncSession = None
    ) -> bool:
        """
        Follow a creator.
        
        Args:
            follower_id: ID of user following
            creator_id: ID of creator being followed
            db: Database session
            
        Returns:
            True if successful
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Validate users exist
            if not await self._creator_exists(follower_id, db) or not await self._creator_exists(creator_id, db):
                raise ValidationError("Creator not found")
            
            if follower_id == creator_id:
                raise ValidationError("Cannot follow yourself")
            
            # Check if already following
            if await self._is_following(follower_id, creator_id, db):
                return True  # Already following
            
            # Create follow relationship
            # This would involve a Follows table/model
            # For now, we'll update the stats
            
            # Update follower count
            await db.execute(
                update(CreatorStats)
                .where(CreatorStats.creator_id == creator_id)
                .values(follower_count=CreatorStats.follower_count + 1)
            )
            
            # Update following count
            await db.execute(
                update(CreatorStats)
                .where(CreatorStats.creator_id == follower_id)
                .values(following_count=CreatorStats.following_count + 1)
            )
            
            await db.commit()
            
            # Clear cache
            await self._clear_creator_cache(creator_id)
            await self._clear_creator_cache(follower_id)
            
            # Send notification
            await self.notification_service.send_follow_notification(
                creator_id, follower_id
            )
            
            # Record metrics
            await self.metrics.record_creator_followed(
                follower_id=follower_id,
                creator_id=creator_id
            )
            
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Follow failed: {str(e)}")
            raise ServiceException(f"Follow failed: {str(e)}")

    async def verify_creator(
        self,
        creator_id: str,
        verification_level: VerificationLevel,
        verified_by: str,
        verification_data: Dict[str, Any] = None,
        db: AsyncSession = None
    ) -> bool:
        """
        Verify a creator at specified level.
        
        Args:
            creator_id: Creator to verify
            verification_level: Level of verification
            verified_by: ID of user performing verification
            verification_data: Additional verification data
            db: Database session
            
        Returns:
            True if successful
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Update creator verification
            await db.execute(
                update(Creator)
                .where(Creator.creator_id == creator_id)
                .values(
                    verification_level=verification_level,
                    verified_at=datetime.utcnow(),
                    verified_by=verified_by,
                    updated_at=datetime.utcnow()
                )
            )
            
            await db.commit()
            
            # Clear cache
            await self._clear_creator_cache(creator_id)
            
            # Send verification notification
            await self.notification_service.send_verification_notification(
                creator_id, verification_level
            )
            
            # Record metrics
            await self.metrics.record_creator_verified(
                creator_id=creator_id,
                verification_level=verification_level.value,
                verified_by=verified_by
            )
            
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Verification failed: {str(e)}")
            raise ServiceException(f"Verification failed: {str(e)}")

    # Helper methods

    async def _validate_creator_request(
        self,
        request: CreatorRequest,
        db: AsyncSession
    ) -> None:
        """Validate creator registration request"""
        # Check username uniqueness
        username_query = select(Creator.creator_id).where(Creator.username == request.username)
        existing_username = await db.execute(username_query)
        if existing_username.scalar_one_or_none():
            raise ValidationError("Username already exists")
        
        # Check email uniqueness
        email_query = select(Creator.creator_id).where(Creator.email == request.email)
        existing_email = await db.execute(email_query)
        if existing_email.scalar_one_or_none():
            raise ValidationError("Email already registered")

    async def _creator_to_response(
        self,
        creator: Creator,
        profile: CreatorProfile = None,
        stats: CreatorStats = None
    ) -> CreatorResponse:
        """Convert creator model to response"""
        return CreatorResponse(
            creator_id=creator.creator_id,
            username=creator.username,
            email=creator.email,
            first_name=creator.first_name,
            last_name=creator.last_name,
            display_name=creator.display_name,
            creator_type=creator.creator_type,
            status=creator.status,
            verification_level=creator.verification_level,
            bio=profile.bio if profile else None,
            location=profile.location if profile else None,
            website=profile.website if profile else None,
            avatar_url=profile.avatar_url if profile else None,
            cover_image_url=profile.cover_image_url if profile else None,
            social_links=profile.social_links if profile else {},
            specialties=profile.specialties if profile else [],
            languages=profile.languages if profile else [],
            follower_count=stats.follower_count if stats else 0,
            following_count=stats.following_count if stats else 0,
            content_count=stats.content_count if stats else 0,
            total_views=stats.total_views if stats else 0,
            total_likes=stats.total_likes if stats else 0,
            joined_date=creator.joined_date,
            last_active=creator.last_active,
            is_premium=creator.is_premium,
            subscription_tier=creator.subscription_tier,
            metadata=profile.metadata if profile else {}
        )

    async def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from Redis cache"""
        try:
            if self.redis_client:
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.error(f"Cache get failed: {str(e)}")
        return None

    async def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Set data in Redis cache"""
        try:
            if self.redis_client:
                await self.redis_client.setex(
                    key,
                    self.config.cache_ttl_seconds,
                    json.dumps(data, default=str)
                )
        except Exception as e:
            logger.error(f"Cache set failed: {str(e)}")

    async def _clear_creator_cache(self, creator_id: str) -> None:
        """Clear creator cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(f"creator:{creator_id}")
        except Exception as e:
            logger.error(f"Cache clear failed: {str(e)}")

    async def _can_update_creator(
        self,
        creator_id: str,
        updater_id: str,
        db: AsyncSession
    ) -> bool:
        """Check if user can update creator"""
        # Creator can update themselves, admins can update anyone
        return creator_id == updater_id  # Simplified check

    async def _get_creator_by_id(
        self,
        creator_id: str,
        db: AsyncSession
    ) -> Optional[Creator]:
        """Get creator by ID"""
        query = select(Creator).where(Creator.creator_id == creator_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _creator_exists(self, creator_id: str, db: AsyncSession) -> bool:
        """Check if creator exists"""
        query = select(Creator.creator_id).where(Creator.creator_id == creator_id)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _is_following(
        self,
        follower_id: str,
        creator_id: str,
        db: AsyncSession
    ) -> bool:
        """Check if user is following creator"""
        # This would check a Follows table
        # For now, return False
        return False

    async def _send_verification_email(self, creator: Creator) -> None:
        """Send email verification"""
        # Implementation would send verification email
        pass

    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "service_name": self.name,
            "status": "active",
            "config": {
                "auto_verification": self.config.enable_auto_verification,
                "creator_matching": self.config.enable_creator_matching,
                "analytics_tracking": self.config.enable_analytics_tracking,
                "email_verification_required": self.config.require_email_verification
            },
            "metrics": self.metrics.get_summary()
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities"""
        return {
            "creator_types": [ct.value for ct in CreatorType],
            "verification_levels": [vl.value for vl in VerificationLevel],
            "creator_statuses": [cs.value for cs in CreatorStatus],
            "features": [
                "creator_registration",
                "profile_management",
                "creator_search",
                "verification_system",
                "social_features",
                "analytics_integration",
                "content_workflow",
                "collaboration_tools",
                "premium_features",
                "caching_optimization"
            ],
            "search_capabilities": [
                "text_search",
                "type_filtering",
                "location_filtering",
                "verification_filtering",
                "follower_range_filtering",
                "custom_sorting",
                "pagination"
            ]
        }