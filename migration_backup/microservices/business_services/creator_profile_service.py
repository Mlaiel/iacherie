"""
🎯 Creator Profile Management Microservice
Creator profile management and verification service with comprehensive profile data, verification workflows, and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import time
import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import datetime, timedelta
from collections import defaultdict
import re
from pydantic import BaseModel, Field, EmailStr

logger = logging.getLogger(__name__)


class CreatorType(str, Enum):
    """Types of creators"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    ARTIST = "artist"
    WRITER = "writer"
    DANCER = "dancer"
    EDUCATOR = "educator"
    GAMER = "gamer"
    CHEF = "chef"
    FITNESS_TRAINER = "fitness_trainer"
    FASHION_DESIGNER = "fashion_designer"
    TECH_REVIEWER = "tech_reviewer"


class VerificationStatus(str, Enum):
    """Verification status"""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    IN_REVIEW = "in_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class ProfileCompletionLevel(str, Enum):
    """Profile completion levels"""
    BASIC = "basic"  # 0-25%
    PARTIAL = "partial"  # 25-50%
    SUBSTANTIAL = "substantial"  # 50-75%
    COMPLETE = "complete"  # 75-100%


class SocialPlatform(str, Enum):
    """Social media platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    REDDIT = "reddit"


@dataclass
class SocialMediaAccount:
    """Social media account information"""
    platform: SocialPlatform
    username: str
    url: str
    followers_count: int = 0
    is_verified: bool = False
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'platform': self.platform.value,
            'username': self.username,
            'url': self.url,
            'followers_count': self.followers_count,
            'is_verified': self.is_verified,
            'last_updated': self.last_updated.isoformat()
        }


@dataclass
class CreatorMetrics:
    """Creator performance metrics"""
    total_followers: int = 0
    engagement_rate: float = 0.0
    content_count: int = 0
    revenue_generated: float = 0.0
    collaborations_count: int = 0
    rating: float = 0.0
    reputation_score: int = 0
    last_active: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_followers': self.total_followers,
            'engagement_rate': self.engagement_rate,
            'content_count': self.content_count,
            'revenue_generated': self.revenue_generated,
            'collaborations_count': self.collaborations_count,
            'rating': self.rating,
            'reputation_score': self.reputation_score,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }


@dataclass
class VerificationDocument:
    """Verification document"""
    id: str
    document_type: str  # id_card, passport, business_license, etc.
    file_url: str
    uploaded_at: datetime
    status: VerificationStatus = VerificationStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'document_type': self.document_type,
            'file_url': self.file_url,
            'uploaded_at': self.uploaded_at.isoformat(),
            'status': self.status.value,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'rejection_reason': self.rejection_reason
        }


@dataclass
class CreatorSkill:
    """Creator skill/expertise"""
    name: str
    level: int  # 1-10
    verified: bool = False
    endorsements: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'level': self.level,
            'verified': self.verified,
            'endorsements': self.endorsements
        }


@dataclass
class CreatorProfile:
    """Comprehensive creator profile"""
    id: str
    user_id: str
    creator_type: CreatorType
    display_name: str
    bio: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: str = "UTC"
    profile_image_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    website_url: Optional[str] = None
    
    # Social media accounts
    social_accounts: List[SocialMediaAccount] = field(default_factory=list)
    
    # Professional information
    years_of_experience: int = 0
    languages: List[str] = field(default_factory=list)
    skills: List[CreatorSkill] = field(default_factory=list)
    portfolio_urls: List[str] = field(default_factory=list)
    
    # Verification
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verification_documents: List[VerificationDocument] = field(default_factory=list)
    verification_badge: bool = False
    
    # Metrics
    metrics: CreatorMetrics = field(default_factory=CreatorMetrics)
    
    # Settings
    is_public: bool = True
    is_available_for_collaboration: bool = True
    preferred_collaboration_types: List[str] = field(default_factory=list)
    minimum_rate: Optional[float] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Tags and categories
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    def calculate_completion_percentage(self) -> float:
        """Calculate profile completion percentage"""
        total_fields = 20  # Total number of important fields
        completed_fields = 0
        
        # Basic information (40% weight)
        if self.display_name: completed_fields += 1
        if self.bio and len(self.bio) >= 50: completed_fields += 1
        if self.email: completed_fields += 1
        if self.profile_image_url: completed_fields += 1
        if self.location: completed_fields += 1
        if self.creator_type: completed_fields += 1
        
        # Professional information (30% weight)
        if self.years_of_experience > 0: completed_fields += 1
        if self.languages: completed_fields += 1
        if self.skills: completed_fields += 1
        if self.portfolio_urls: completed_fields += 1
        
        # Social media (20% weight)
        if self.social_accounts: completed_fields += 2
        if self.website_url: completed_fields += 1
        
        # Additional details (10% weight)
        if self.phone: completed_fields += 1
        if self.banner_image_url: completed_fields += 1
        if self.tags: completed_fields += 1
        if self.categories: completed_fields += 1
        if self.preferred_collaboration_types: completed_fields += 1
        if self.minimum_rate is not None: completed_fields += 1
        
        # Verification bonus
        if self.verification_status == VerificationStatus.VERIFIED:
            completed_fields += 1
            
        return min(100.0, (completed_fields / total_fields) * 100)
        
    def get_completion_level(self) -> ProfileCompletionLevel:
        """Get profile completion level"""
        percentage = self.calculate_completion_percentage()
        
        if percentage < 25:
            return ProfileCompletionLevel.BASIC
        elif percentage < 50:
            return ProfileCompletionLevel.PARTIAL
        elif percentage < 75:
            return ProfileCompletionLevel.SUBSTANTIAL
        else:
            return ProfileCompletionLevel.COMPLETE
            
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'creator_type': self.creator_type.value,
            'display_name': self.display_name,
            'bio': self.bio,
            'email': self.email,
            'location': self.location,
            'timezone': self.timezone,
            'profile_image_url': self.profile_image_url,
            'banner_image_url': self.banner_image_url,
            'website_url': self.website_url,
            'social_accounts': [acc.to_dict() for acc in self.social_accounts],
            'years_of_experience': self.years_of_experience,
            'languages': self.languages,
            'skills': [skill.to_dict() for skill in self.skills],
            'portfolio_urls': self.portfolio_urls,
            'verification_status': self.verification_status.value,
            'verification_badge': self.verification_badge,
            'metrics': self.metrics.to_dict(),
            'is_public': self.is_public,
            'is_available_for_collaboration': self.is_available_for_collaboration,
            'preferred_collaboration_types': self.preferred_collaboration_types,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'tags': self.tags,
            'categories': self.categories,
            'completion_percentage': self.calculate_completion_percentage(),
            'completion_level': self.get_completion_level().value
        }
        
        if include_sensitive:
            data.update({
                'phone': self.phone,
                'minimum_rate': self.minimum_rate,
                'verification_documents': [doc.to_dict() for doc in self.verification_documents]
            })
            
        return data


class ProfileValidator:
    """Profile data validation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Basic phone validation - supports international formats
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))
        
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
        return bool(re.match(pattern, url))
        
    @staticmethod
    def validate_social_media_url(platform: SocialPlatform, url: str) -> bool:
        """Validate social media URL for specific platform"""
        platform_patterns = {
            SocialPlatform.YOUTUBE: r'https?://(?:www\.)?youtube\.com/(?:channel/|c/|user/)?[\w-]+',
            SocialPlatform.INSTAGRAM: r'https?://(?:www\.)?instagram\.com/[\w.]+',
            SocialPlatform.TWITTER: r'https?://(?:www\.)?twitter\.com/[\w]+',
            SocialPlatform.TIKTOK: r'https?://(?:www\.)?tiktok\.com/@[\w.]+',
            SocialPlatform.LINKEDIN: r'https?://(?:www\.)?linkedin\.com/in/[\w-]+',
            SocialPlatform.TWITCH: r'https?://(?:www\.)?twitch\.tv/[\w]+',
            SocialPlatform.SPOTIFY: r'https?://open\.spotify\.com/artist/[\w]+',
        }
        
        pattern = platform_patterns.get(platform)
        if pattern:
            return bool(re.match(pattern, url))
        else:
            # Fallback to generic URL validation
            return ProfileValidator.validate_url(url)


class CreatorProfileService:
    """Creator Profile Management and Verification Service"""
    
    def __init__(self, name: str = "creator_profile_service"):
        self.name = name
        self.profiles: Dict[str, CreatorProfile] = {}
        self.profiles_by_user: Dict[str, str] = {}  # user_id -> profile_id
        self.verification_queue: List[str] = []  # profile_ids pending verification
        self.validator = ProfileValidator()
        self.running = False
        self.stats = {
            'total_profiles': 0,
            'verified_profiles': 0,
            'pending_verification': 0,
            'profile_views': 0,
            'profile_updates': 0
        }
        
    async def start(self):
        """Start creator profile service"""
        self.running = True
        logger.info(f"Started creator profile service: {self.name}")
        
    async def stop(self):
        """Stop creator profile service"""
        self.running = False
        logger.info(f"Stopped creator profile service: {self.name}")
        
    async def create_profile(self, user_id: str, creator_type: CreatorType,
                           display_name: str, email: str, bio: str = "") -> Optional[CreatorProfile]:
        """Create new creator profile"""
        try:
            # Check if user already has a profile
            if user_id in self.profiles_by_user:
                logger.warning(f"User {user_id} already has a profile")
                return None
                
            # Validate email
            if not self.validator.validate_email(email):
                logger.error(f"Invalid email format: {email}")
                return None
                
            # Create profile
            profile_id = str(uuid.uuid4())
            profile = CreatorProfile(
                id=profile_id,
                user_id=user_id,
                creator_type=creator_type,
                display_name=display_name,
                email=email,
                bio=bio
            )
            
            # Store profile
            self.profiles[profile_id] = profile
            self.profiles_by_user[user_id] = profile_id
            self.stats['total_profiles'] += 1
            
            logger.info(f"Created profile for user {user_id}: {profile_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}")
            return None
            
    async def get_profile(self, profile_id: str) -> Optional[CreatorProfile]:
        """Get creator profile by ID"""
        try:
            if profile_id in self.profiles:
                self.stats['profile_views'] += 1
                return self.profiles[profile_id]
            return None
        except Exception as e:
            logger.error(f"Error getting profile: {str(e)}")
            return None
            
    async def get_profile_by_user(self, user_id: str) -> Optional[CreatorProfile]:
        """Get creator profile by user ID"""
        try:
            profile_id = self.profiles_by_user.get(user_id)
            if profile_id:
                return await self.get_profile(profile_id)
            return None
        except Exception as e:
            logger.error(f"Error getting profile by user: {str(e)}")
            return None
            
    async def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> bool:
        """Update creator profile"""
        try:
            if profile_id not in self.profiles:
                return False
                
            profile = self.profiles[profile_id]
            
            # Validate updates
            if 'email' in updates and not self.validator.validate_email(updates['email']):
                logger.error(f"Invalid email format: {updates['email']}")
                return False
                
            if 'phone' in updates and updates['phone'] and not self.validator.validate_phone(updates['phone']):
                logger.error(f"Invalid phone format: {updates['phone']}")
                return False
                
            if 'website_url' in updates and updates['website_url'] and not self.validator.validate_url(updates['website_url']):
                logger.error(f"Invalid website URL: {updates['website_url']}")
                return False
                
            # Apply updates
            for field, value in updates.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
                    
            profile.updated_at = datetime.utcnow()
            self.stats['profile_updates'] += 1
            
            logger.info(f"Updated profile {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return False
            
    async def add_social_account(self, profile_id: str, platform: SocialPlatform,
                               username: str, url: str, followers_count: int = 0) -> bool:
        """Add social media account to profile"""
        try:
            if profile_id not in self.profiles:
                return False
                
            profile = self.profiles[profile_id]
            
            # Validate URL
            if not self.validator.validate_social_media_url(platform, url):
                logger.error(f"Invalid {platform.value} URL: {url}")
                return False
                
            # Check if platform already exists
            for account in profile.social_accounts:
                if account.platform == platform:
                    # Update existing account
                    account.username = username
                    account.url = url
                    account.followers_count = followers_count
                    account.last_updated = datetime.utcnow()
                    break
            else:
                # Add new account
                account = SocialMediaAccount(
                    platform=platform,
                    username=username,
                    url=url,
                    followers_count=followers_count
                )
                profile.social_accounts.append(account)
                
            profile.updated_at = datetime.utcnow()
            
            logger.info(f"Added/updated {platform.value} account for profile {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding social account: {str(e)}")
            return False
            
    async def add_skill(self, profile_id: str, skill_name: str, level: int) -> bool:
        """Add skill to creator profile"""
        try:
            if profile_id not in self.profiles:
                return False
                
            if level < 1 or level > 10:
                logger.error(f"Invalid skill level: {level}")
                return False
                
            profile = self.profiles[profile_id]
            
            # Check if skill already exists
            for skill in profile.skills:
                if skill.name.lower() == skill_name.lower():
                    skill.level = level
                    break
            else:
                # Add new skill
                skill = CreatorSkill(name=skill_name, level=level)
                profile.skills.append(skill)
                
            profile.updated_at = datetime.utcnow()
            
            logger.info(f"Added/updated skill {skill_name} for profile {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding skill: {str(e)}")
            return False
            
    async def submit_verification(self, profile_id: str, document_type: str, file_url: str) -> bool:
        """Submit verification document"""
        try:
            if profile_id not in self.profiles:
                return False
                
            profile = self.profiles[profile_id]
            
            # Create verification document
            doc = VerificationDocument(
                id=str(uuid.uuid4()),
                document_type=document_type,
                file_url=file_url,
                uploaded_at=datetime.utcnow()
            )
            
            profile.verification_documents.append(doc)
            profile.verification_status = VerificationStatus.PENDING
            profile.updated_at = datetime.utcnow()
            
            # Add to verification queue
            if profile_id not in self.verification_queue:
                self.verification_queue.append(profile_id)
                self.stats['pending_verification'] += 1
                
            logger.info(f"Submitted verification document for profile {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting verification: {str(e)}")
            return False
            
    async def process_verification(self, profile_id: str, approved: bool, 
                                 reviewer_id: str, rejection_reason: str = None) -> bool:
        """Process verification request"""
        try:
            if profile_id not in self.profiles:
                return False
                
            profile = self.profiles[profile_id]
            
            if approved:
                profile.verification_status = VerificationStatus.VERIFIED
                profile.verification_badge = True
                self.stats['verified_profiles'] += 1
            else:
                profile.verification_status = VerificationStatus.REJECTED
                
            # Update verification documents
            for doc in profile.verification_documents:
                if doc.status == VerificationStatus.PENDING:
                    doc.status = profile.verification_status
                    doc.reviewed_by = reviewer_id
                    doc.reviewed_at = datetime.utcnow()
                    doc.rejection_reason = rejection_reason
                    
            profile.updated_at = datetime.utcnow()
            
            # Remove from verification queue
            if profile_id in self.verification_queue:
                self.verification_queue.remove(profile_id)
                self.stats['pending_verification'] -= 1
                
            logger.info(f"Processed verification for profile {profile_id}: {'approved' if approved else 'rejected'}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing verification: {str(e)}")
            return False
            
    async def update_metrics(self, profile_id: str, metrics_update: Dict[str, Any]) -> bool:
        """Update creator metrics"""
        try:
            if profile_id not in self.profiles:
                return False
                
            profile = self.profiles[profile_id]
            metrics = profile.metrics
            
            # Update metrics
            for field, value in metrics_update.items():
                if hasattr(metrics, field):
                    setattr(metrics, field, value)
                    
            metrics.last_updated = datetime.utcnow()
            profile.updated_at = datetime.utcnow()
            
            logger.info(f"Updated metrics for profile {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
            return False
            
    async def search_profiles(self, creator_type: CreatorType = None, 
                            location: str = None, skills: List[str] = None,
                            min_followers: int = None, verified_only: bool = False,
                            available_for_collaboration: bool = None,
                            limit: int = 50, offset: int = 0) -> List[CreatorProfile]:
        """Search creator profiles"""
        try:
            results = []
            
            for profile in self.profiles.values():
                # Skip private profiles
                if not profile.is_public:
                    continue
                    
                # Filter by creator type
                if creator_type and profile.creator_type != creator_type:
                    continue
                    
                # Filter by location
                if location and (not profile.location or location.lower() not in profile.location.lower()):
                    continue
                    
                # Filter by skills
                if skills:
                    profile_skills = [skill.name.lower() for skill in profile.skills]
                    if not any(skill.lower() in profile_skills for skill in skills):
                        continue
                        
                # Filter by minimum followers
                if min_followers and profile.metrics.total_followers < min_followers:
                    continue
                    
                # Filter by verification status
                if verified_only and profile.verification_status != VerificationStatus.VERIFIED:
                    continue
                    
                # Filter by collaboration availability
                if available_for_collaboration is not None and profile.is_available_for_collaboration != available_for_collaboration:
                    continue
                    
                results.append(profile)
                
            # Sort by relevance (verified first, then by followers)
            results.sort(key=lambda p: (
                p.verification_status == VerificationStatus.VERIFIED,
                p.metrics.total_followers
            ), reverse=True)
            
            # Apply pagination
            return results[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error searching profiles: {str(e)}")
            return []
            
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        completion_levels = defaultdict(int)
        verification_statuses = defaultdict(int)
        
        for profile in self.profiles.values():
            completion_levels[profile.get_completion_level().value] += 1
            verification_statuses[profile.verification_status.value] += 1
            
        return {
            "name": self.name,
            "status": "running" if self.running else "stopped",
            "stats": self.stats,
            "completion_levels": dict(completion_levels),
            "verification_statuses": dict(verification_statuses),
            "verification_queue_size": len(self.verification_queue),
            "timestamp": datetime.utcnow().isoformat()
        }


def create_creator_profile_service(config: Dict[str, Any] = None) -> CreatorProfileService:
    """Factory function to create Creator Profile service"""
    config = config or {}
    service_name = config.get('name', 'creator_profile_service')
    
    service = CreatorProfileService(service_name)
    
    return service


__all__ = [
    'CreatorProfileService', 'CreatorProfile', 'SocialMediaAccount', 'CreatorMetrics',
    'CreatorSkill', 'VerificationDocument', 'ProfileValidator',
    'CreatorType', 'VerificationStatus', 'ProfileCompletionLevel', 'SocialPlatform',
    'create_creator_profile_service'
]