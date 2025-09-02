"""Profile Manager - Creator profile and portfolio management.

Handles comprehensive profile management for multi-format creators
including portfolio showcase, social links, and creator verification.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Advanced Content Protection
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID
import logging
from enum import Enum
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, validator, HttpUrl

from ...core.database import get_db
from ...core.exceptions import (
    ProfileNotFoundError,
    InvalidProfileDataError,
    ProfileServiceError
)
from ...models.profile import CreatorProfile, SocialPlatform, PortfolioItem
from ...services.verification.identity import IdentityVerificationService
from ...services.analytics.engagement import EngagementAnalytics
from ...services.storage.media import MediaStorageService
from ...utils.image_processing import ImageProcessor
from ...utils.url_validation import URLValidator


logger = logging.getLogger(__name__)


class CreatorTier(str, Enum):
    """
Creator tier levels based on followers and engagement."""

    EMERGING = "emerging"  # < 1K followers
    RISING = "rising"  # 1K - 10K followers
    ESTABLISHED = "established"  # 10K - 100K followers
    INFLUENCER = "influencer"  # 100K - 1M followers
    CELEBRITY = "celebrity"  # > 1M followers


class ProfileVisibility(str, Enum):
    """Profile visibility settings."""

    PUBLIC = "public"
    FOLLOWERS_ONLY = "followers_only"
    PRIVATE = "private"


class ProfileUpdateData(BaseModel):
    """Profile update validation model."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    social_links: Optional[Dict[str, str]] = None
    specialties: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    collaboration_rates: Optional[Dict[str, Decimal]] = None
    availability_status: Optional[str] = None
    portfolio_highlight_ids: Optional[List[str]] = None
    visibility: Optional[ProfileVisibility] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Display name must be at least 2 characters')
        return v.strip() if v else None
    
    @validator('bio')
    def validate_bio(cls, v):
        if v and len(v) > 2000:
            raise ValueError('Bio must be less than 2000 characters')
        return v
        
    @validator('specialties')
    def validate_specialties(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 specialties allowed')
        return v
        
    @validator('social_links')
    def validate_social_links(cls, v):
        if v:
            url_validator = URLValidator()
            for platform, url in v.items():
                if not url_validator.is_valid_url(url):
                    raise ValueError(f'Invalid URL for {platform}: {url}')
        return v


class PortfolioItemData(BaseModel):
    """
Portfolio item creation/update data."""
    title: str
    description: Optional[str] = None
    content_type: str  # audio, video, image, text
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    external_url: Optional[HttpUrl] = None
    tags: List[str] = []
    display_order: Optional[int] = None
    is_featured: bool = False
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters')
        return v.strip()


class ProfileManager:
    """
    Comprehensive profile management system for content creators.
    
    Features:
    - Multi-format creator profiles
    - Portfolio showcase management
    - Social media integration
    - Creator tier calculation
    - Engagement analytics integration
    - Profile verification support
    - Collaboration rate management
    """
    
    def __init__(
        self,
        db: Session,
        media_storage: MediaStorageService,
        identity_verification: IdentityVerificationService,
        engagement_analytics: EngagementAnalytics
    ):
        self.db = db
        self.media_storage = media_storage
        self.identity_verification = identity_verification
        self.engagement_analytics = engagement_analytics
        self.image_processor = ImageProcessor()
        self.url_validator = URLValidator()
        
    async def create_profile(
        self,
        client_id: UUID,
        profile_data: ProfileUpdateData
    ) -> Dict[str, Any]:
        """
        Create initial creator profile.
        
        Args:
            client_id: Client identifier
            profile_data: Profile creation data
            
        Returns:
            Created profile information
            
        Raises:
            InvalidProfileDataError: If profile data is invalid
        """
        try:
            # Check if profile already exists
            existing_profile = self.db.query(CreatorProfile).filter(
                CreatorProfile.client_id == client_id
            ).first()
            
            if existing_profile:
                raise InvalidProfileDataError("Profile already exists for this client")
                
            # Create new profile
            profile = CreatorProfile(
                client_id=client_id,
                display_name=profile_data.display_name,
                bio=profile_data.bio,
                location=profile_data.location,
                website_url=str(profile_data.website_url) if profile_data.website_url else None,
                social_links=profile_data.social_links or {},
                specialties=profile_data.specialties or [],
                languages=profile_data.languages or ["en"],
                collaboration_rates=profile_data.collaboration_rates or {},
                availability_status=profile_data.availability_status or "available",
                visibility=ProfileVisibility(profile_data.visibility or ProfileVisibility.PUBLIC),
                custom_fields=profile_data.custom_fields or {},
                tier=CreatorTier.EMERGING,  # Default tier
                total_followers=0,
                total_engagement=0,
                profile_completion=0
            )
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            # Calculate initial profile completion
            await self._update_profile_completion(profile)
            
            logger.info(f"Profile created for client: {client_id}")
            
            return await self._format_profile_data(profile)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating profile: {e}")
            raise ProfileServiceError("Failed to create profile") from e
            
    async def get_profile(
        self,
        client_id: UUID,
        viewer_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve creator profile with visibility checks.
        
        Args:
            client_id: Profile owner's client ID
            viewer_id: Optional viewer's client ID for access control
            
        Returns:
            Profile data or None if not found/accessible
        """
        try:
            profile = self.db.query(CreatorProfile).filter(
                CreatorProfile.client_id == client_id
            ).first()
            
            if not profile:
                return None
                
            # Check visibility permissions
            if not await self._can_view_profile(profile, viewer_id):
                return None
                
            return await self._format_profile_data(profile, include_private=viewer_id == client_id)
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            logger.error(f"Error retrieving profile for client {client_id}: {e}")
            return None
            
    async def update_profile(
        self,
        client_id: UUID,
        update_data: ProfileUpdateData
    ) -> Dict[str, Any]:
        """
        Update creator profile information.
        
        Args:
            client_id: Client identifier
            update_data: Updated profile data
            
        Returns:
            Updated profile information
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        try:
            profile = self.db.query(CreatorProfile).filter(
                CreatorProfile.client_id == client_id
            ).first()
            
            if not profile:
                raise ProfileNotFoundError(f"Profile not found for client: {client_id}")
                
            # Update provided fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(profile, field):
                    if field == 'website_url' and value:
                        setattr(profile, field, str(value))
                    else:
                        setattr(profile, field, value)
                        
            profile.updated_at = datetime.utcnow()
            self.db.commit()
            
            # Recalculate profile completion
            await self._update_profile_completion(profile)
            
            logger.info(f"Profile updated for client: {client_id}")
            
            return await self._format_profile_data(profile)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating profile: {e}")
            raise ProfileServiceError("Failed to update profile") from e
            
    async def upload_profile_image(
        self,
        client_id: UUID,
        image_data: bytes,
        image_type: str
    ) -> Dict[str, str]:
        """
        Upload and process profile image.
        
        Args:
            client_id: Client identifier
            image_data: Image binary data
            image_type: 'avatar' or 'banner'
            
        Returns:
            Upload result with image URLs
        """
        try:
            profile = self.db.query(CreatorProfile).filter(
                CreatorProfile.client_id == client_id
            ).first()
            
            if not profile:
                raise ProfileNotFoundError(f"Profile not found for client: {client_id}")
                
            # Process and optimize image
            if image_type == 'avatar':
                processed_image = await self.image_processor.process_avatar(image_data)
                sizes = {'small': 150, 'medium': 300, 'large': 600}
            else:  # banner
                processed_image = await self.image_processor.process_banner(image_data)
                sizes = {'medium': 800, 'large': 1200}
                
            # Upload different sizes
            image_urls = {}
            for size_name, dimensions in sizes.items():
                resized_image = await self.image_processor.resize_image(
                    processed_image, dimensions
                )
                
                storage_path = f"profiles/{client_id}/{image_type}_{size_name}.jpg"
                upload_result = await self.media_storage.upload_image(
                    resized_image, storage_path
                )
                
                if upload_result.get('success'):
                    image_urls[size_name] = upload_result['url']
                    
            # Update profile with image URLs
            if image_type == 'avatar':
                profile.avatar_urls = image_urls
            else:
                profile.banner_urls = image_urls
                
            self.db.commit()
            
            return {
                'success': True,
                'image_type': image_type,
                'urls': image_urls
            }
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            logger.error(f"Error uploading profile image: {e}")
            return {'success': False, 'error': str(e)}
            
    async def add_portfolio_item(
        self,
        client_id: UUID,
        item_data: PortfolioItemData
    ) -> Dict[str, Any]:
        """
        Add item to creator's portfolio.
        
        Args:
            client_id: Client identifier
            item_data: Portfolio item data
            
        Returns:
            Created portfolio item information
        """
        try:
            profile = self.db.query(CreatorProfile).filter(
                CreatorProfile.client_id == client_id
            ).first()
            
            if not profile:
                raise ProfileNotFoundError(f"Profile not found for client: {client_id}")
                
            # Create portfolio item
            portfolio_item = PortfolioItem(
                profile_id=profile.id,
                title=item_data.title,
                description=item_data.description,
                content_type=item_data.content_type,
                media_url=item_data.media_url,
                thumbnail_url=item_data.thumbnail_url,
                external_url=str(item_data.external_url) if item_data.external_url else None,
                tags=item_data.tags,
                display_order=item_data.display_order or 0,
                is_featured=item_data.is_featured
            )
            
            self.db.add(portfolio_item)
            self.db.commit()
            self.db.refresh(portfolio_item)
            
            logger.info(f"Portfolio item added for client: {client_id}")
            
            return self._format_portfolio_item(portfolio_item)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error adding portfolio item: {e}")
            raise ProfileServiceError("Failed to add portfolio item") from e
            
    async def update_creator_tier(self, client_id: UUID) -> CreatorTier:
        """
        Calculate and update creator tier based on analytics.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Updated creator tier
        """
        try:
            profile = self.db.query(CreatorProfile).filter(
                CreatorProfile.client_id == client_id
            ).first()
            
            if not profile:
                return CreatorTier.EMERGING
                
            # Get latest analytics
            analytics = await self.engagement_analytics.get_creator_metrics(client_id)
            
            total_followers = analytics.get('total_followers', 0)
            engagement_rate = analytics.get('engagement_rate', 0.0)
            
            # Calculate tier based on followers and engagement
            if total_followers >= 1000000:
                tier = CreatorTier.CELEBRITY
            elif total_followers >= 100000:
                tier = CreatorTier.INFLUENCER
            elif total_followers >= 10000:
                tier = CreatorTier.ESTABLISHED
            elif total_followers >= 1000:
                tier = CreatorTier.RISING
            else:
                tier = CreatorTier.EMERGING
                
            # Update profile
            profile.tier = tier
            profile.total_followers = total_followers
            profile.total_engagement = analytics.get('total_engagement', 0)
            profile.engagement_rate = engagement_rate
            
            self.db.commit()
            
            logger.info(f"Creator tier updated for client {client_id}: {tier.value}")
            
            return tier
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            logger.error(f"Error updating creator tier: {e}")
            return CreatorTier.EMERGING
            
    async def search_profiles(
        self,
        query: str,
        creator_type: Optional[str] = None,
        location: Optional[str] = None,
        tier: Optional[CreatorTier] = None,
        specialties: Optional[List[str]] = None,
        min_followers: Optional[int] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search creator profiles with filters.
        
        Args:
            query: Search query string
            creator_type: Filter by creator type
            location: Filter by location
            tier: Filter by creator tier
            specialties: Filter by specialties
            min_followers: Minimum follower count
            page: Page number
            limit: Items per page
            
        Returns:
            Search results with pagination
        """
        try:
            query_builder = self.db.query(CreatorProfile).filter(
                CreatorProfile.visibility == ProfileVisibility.PUBLIC
            )
            
            # Apply text search
            if query:
                query_builder = query_builder.filter(
                    CreatorProfile.display_name.ilike(f"%{query}%") |
                    CreatorProfile.bio.ilike(f"%{query}%")
                )
                
            # Apply filters
            if location:
                query_builder = query_builder.filter(
                    CreatorProfile.location.ilike(f"%{location}%")
                )
                
            if tier:
                query_builder = query_builder.filter(CreatorProfile.tier == tier)
                
            if min_followers:
                query_builder = query_builder.filter(
                    CreatorProfile.total_followers >= min_followers
                )
                
            # Apply specialty filter
            if specialties:
                for specialty in specialties:
                    query_builder = query_builder.filter(
                        CreatorProfile.specialties.contains([specialty])
                    )
                    
            # Get total count
            total = query_builder.count()
            
            # Apply pagination and ordering
            offset = (page - 1) * limit
            profiles = query_builder.order_by(
                CreatorProfile.total_followers.desc(),
                CreatorProfile.engagement_rate.desc()
            ).offset(offset).limit(limit).all()
            
            # Format results
            results = []
            for profile in profiles:
                formatted_profile = await self._format_profile_data(profile, summary=True)
                results.append(formatted_profile)
                
            return {
                "results": results,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            logger.error(f"Error searching profiles: {e}")
            raise ProfileServiceError("Profile search failed") from e
            
    async def _can_view_profile(
        self,
        profile: CreatorProfile,
        viewer_id: Optional[UUID]
    ) -> bool:
        """Check if viewer can access profile based on visibility settings."""
        if profile.visibility == ProfileVisibility.PUBLIC:
            return True
        elif profile.visibility == ProfileVisibility.PRIVATE:
            return viewer_id == profile.client_id
        elif profile.visibility == ProfileVisibility.FOLLOWERS_ONLY:
            # Implementation would check if viewer follows the profile owner
            return viewer_id is not None
        return False
        
    async def _update_profile_completion(self, profile: CreatorProfile) -> None:
        """
Calculate and update profile completion percentage."""
        completion_fields = [
            profile.display_name,
            profile.bio,
            profile.location,
            profile.website_url,
            profile.avatar_urls,
            profile.social_links,
            profile.specialties
        ]
        
        completed = sum(1 for field in completion_fields if field)
        completion_percentage = int((completed / len(completion_fields)) * 100)
        
        profile.profile_completion = completion_percentage
        self.db.commit()
        
    async def _format_profile_data(
        self,
        profile: CreatorProfile,
        include_private: bool = False,
        summary: bool = False
    ) -> Dict[str, Any]:
        """
Format profile data for API response."""
        data = {
            "id": str(profile.id),
            "client_id": str(profile.client_id),
            "display_name": profile.display_name,
            "bio": profile.bio,
            "location": profile.location,
            "website_url": profile.website_url,
            "avatar_urls": profile.avatar_urls,
            "banner_urls": profile.banner_urls,
            "social_links": profile.social_links,
            "specialties": profile.specialties,
            "languages": profile.languages,
            "tier": profile.tier.value if profile.tier else None,
            "total_followers": profile.total_followers,
            "engagement_rate": float(profile.engagement_rate or 0),
            "profile_completion": profile.profile_completion,
            "is_verified": profile.is_verified,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
        }
        
        # Include private data for profile owner
        if include_private:
            data.update({
                "collaboration_rates": profile.collaboration_rates,
                "availability_status": profile.availability_status,
                "visibility": profile.visibility.value,
                "custom_fields": profile.custom_fields
            })
            
        # Include portfolio for full profile view
        if not summary:
            portfolio_items = self.db.query(PortfolioItem).filter(
                PortfolioItem.profile_id == profile.id,
                PortfolioItem.is_active == True
            ).order_by(PortfolioItem.display_order, PortfolioItem.created_at).all()
            
            data["portfolio"] = [
                self._format_portfolio_item(item) for item in portfolio_items
            ]
            
        return data
        
    def _format_portfolio_item(self, item: PortfolioItem) -> Dict[str, Any]:
        """Format portfolio item data."""
        return {
            "id": str(item.id),
            "title": item.title,
            "description": item.description,
            "content_type": item.content_type,
            "media_url": item.media_url,
            "thumbnail_url": item.thumbnail_url,
            "external_url": item.external_url,
            "tags": item.tags,
            "is_featured": item.is_featured,
            "view_count": item.view_count,
            "created_at": item.created_at.isoformat()
        }
