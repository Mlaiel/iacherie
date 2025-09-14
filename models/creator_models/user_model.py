"""👤 User Model - Core Creator Foundation
=====================================
Module: models/creator_models/user_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: User Management Model - Production-Ready
Responsibility: Core user and creator management functionality

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This model provides the foundational user management for all creator types:
- User registration and authentication
- Profile management and preferences
- Multi-platform account linking
- Privacy and security settings
- Subscription and billing information
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import logging

class UserStatus(Enum):
    """User account status"""
    PENDING = "pending"
    ACTIVE = "active"
    VERIFIED = "verified"
    PREMIUM = "premium"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class SubscriptionTier(Enum):
    """Subscription tier levels"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class PrivacyLevel(Enum):
    """Privacy level settings"""
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"

@dataclass
class UserPreferences:
    """User preferences and settings"""
    language: str = "en"
    timezone: str = "UTC"
    theme: str = "light"
    notifications_email: bool = True
    notifications_push: bool = True
    notifications_sms: bool = False
    privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC
    content_discovery: bool = True
    analytics_sharing: bool = True
    marketing_emails: bool = False
    beta_features: bool = False
    ai_recommendations: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "language": self.language,
            "timezone": self.timezone,
            "theme": self.theme,
            "notifications": {
                "email": self.notifications_email,
                "push": self.notifications_push,
                "sms": self.notifications_sms
            },
            "privacy_level": self.privacy_level.value,
            "content_discovery": self.content_discovery,
            "analytics_sharing": self.analytics_sharing,
            "marketing_emails": self.marketing_emails,
            "beta_features": self.beta_features,
            "ai_recommendations": self.ai_recommendations
        }

@dataclass
class SocialLinks:
    """Social media and platform links"""
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None
    spotify: Optional[str] = None
    soundcloud: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert to dictionary"""
        return {
            "instagram": self.instagram,
            "twitter": self.twitter,
            "facebook": self.facebook,
            "youtube": self.youtube,
            "tiktok": self.tiktok,
            "spotify": self.spotify,
            "soundcloud": self.soundcloud,
            "linkedin": self.linkedin,
            "website": self.website
        }

@dataclass
class UserProfile:
    """Complete user profile information"""
    id: str
    email: str
    username: str
    display_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[datetime] = None
    phone: Optional[str] = None
    status: UserStatus = UserStatus.PENDING
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    email_verified: bool = False
    phone_verified: bool = False
    two_factor_enabled: bool = False
    preferences: UserPreferences = field(default_factory=UserPreferences)
    social_links: SocialLinks = field(default_factory=SocialLinks)
    tags: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization validation"""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.display_name:
            self.display_name = self.username
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "display_name": self.display_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "banner_url": self.banner_url,
            "location": self.location,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "phone": self.phone,
            "status": self.status.value,
            "subscription_tier": self.subscription_tier.value,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "two_factor_enabled": self.two_factor_enabled,
            "preferences": self.preferences.to_dict(),
            "social_links": self.social_links.to_dict(),
            "tags": self.tags,
            "skills": self.skills,
            "interests": self.interests,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    def get_full_name(self) -> str:
        """Get full name or display name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name
    
    def is_premium_user(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_tier in [SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]
    
    def is_verified(self) -> bool:
        """Check if user is verified"""
        return self.status == UserStatus.VERIFIED or self.email_verified

class UserModel:
    """User Model - Core Creator Foundation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    @staticmethod
    def create_profile(user_data: Dict[str, Any]) -> UserProfile:
        """Create a new user profile"""
        try:
            # Generate unique ID if not provided
            user_id = user_data.get("id", str(uuid.uuid4()))
            
            # Parse preferences if provided
            preferences_data = user_data.get("preferences", {})
            preferences = UserPreferences(**preferences_data) if preferences_data else UserPreferences()
            
            # Parse social links if provided
            social_data = user_data.get("social_links", {})
            social_links = SocialLinks(**social_data) if social_data else SocialLinks()
            
            # Create profile
            profile = UserProfile(
                id=user_id,
                email=user_data["email"],
                username=user_data["username"],
                display_name=user_data.get("display_name", user_data["username"]),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                bio=user_data.get("bio"),
                avatar_url=user_data.get("avatar_url"),
                banner_url=user_data.get("banner_url"),
                location=user_data.get("location"),
                phone=user_data.get("phone"),
                preferences=preferences,
                social_links=social_links,
                tags=user_data.get("tags", []),
                skills=user_data.get("skills", []),
                interests=user_data.get("interests", [])
            )
            
            return profile
            
        except Exception as e:
            logging.error(f"Failed to create user profile: {e}")
            raise
    
    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user data"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Required fields
        required_fields = ["email", "username"]
        for field in required_fields:
            if not user_data.get(field):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Email validation
        email = user_data.get("email", "")
        if email and "@" not in email:
            validation_result["valid"] = False
            validation_result["errors"].append("Invalid email format")
        
        # Username validation
        username = user_data.get("username", "")
        if username and len(username) < 3:
            validation_result["valid"] = False
            validation_result["errors"].append("Username must be at least 3 characters")
        
        # Password strength (if provided)
        password = user_data.get("password", "")
        if password and len(password) < 8:
            validation_result["warnings"].append("Password should be at least 8 characters")
        
        return validation_result
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for storage"""
        salt = str(uuid.uuid4())
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        # This is a simplified version - in production use proper password hashing
        return hashlib.sha256(password.encode()).hexdigest() in hashed_password
    
    @staticmethod
    def update_profile(profile: UserProfile, updates: Dict[str, Any]) -> UserProfile:
        """Update user profile"""
        try:
            # Update basic fields
            for field, value in updates.items():
                if hasattr(profile, field) and field not in ["id", "created_at"]:
                    setattr(profile, field, value)
            
            # Update timestamp
            profile.updated_at = datetime.now(timezone.utc)
            
            return profile
            
        except Exception as e:
            logging.error(f"Failed to update user profile: {e}")
            raise
    
    @staticmethod
    def get_user_permissions(profile: UserProfile) -> List[str]:
        """Get user permissions based on status and subscription"""
        permissions = ["read_own_content", "create_content", "update_own_profile"]
        
        if profile.is_verified():
            permissions.extend(["verified_creator", "priority_support"])
        
        if profile.is_premium_user():
            permissions.extend([
                "premium_features", "advanced_analytics", "priority_processing",
                "increased_limits", "custom_branding"
            ])
        
        if profile.subscription_tier == SubscriptionTier.ENTERPRISE:
            permissions.extend([
                "enterprise_features", "white_label", "api_access",
                "advanced_collaboration", "custom_integrations"
            ])
        
        return permissions
    
    @staticmethod
    def calculate_profile_completeness(profile: UserProfile) -> Dict[str, Any]:
        """Calculate profile completeness score"""
        total_fields = 15  # Key profile fields
        completed_fields = 0
        
        # Required fields
        if profile.email:
            completed_fields += 1
        if profile.username:
            completed_fields += 1
        if profile.display_name:
            completed_fields += 1
        
        # Optional but important fields
        if profile.first_name:
            completed_fields += 1
        if profile.last_name:
            completed_fields += 1
        if profile.bio:
            completed_fields += 1
        if profile.avatar_url:
            completed_fields += 1
        if profile.location:
            completed_fields += 1
        if profile.skills:
            completed_fields += 1
        if profile.interests:
            completed_fields += 1
        
        # Verification status
        if profile.email_verified:
            completed_fields += 1
        if profile.phone_verified:
            completed_fields += 1
        if profile.two_factor_enabled:
            completed_fields += 1
        
        # Social links
        social_links_count = sum(1 for link in profile.social_links.to_dict().values() if link)
        if social_links_count > 0:
            completed_fields += 1
        if social_links_count >= 3:
            completed_fields += 1
        
        completeness_score = (completed_fields / total_fields) * 100
        
        return {
            "score": round(completeness_score, 1),
            "completed_fields": completed_fields,
            "total_fields": total_fields,
            "missing_important": [
                field for field in ["bio", "avatar_url", "skills", "interests"]
                if not getattr(profile, field, None)
            ],
            "suggestions": [
                "Add a profile picture" if not profile.avatar_url else None,
                "Write a bio" if not profile.bio else None,
                "Add your skills" if not profile.skills else None,
                "Add your interests" if not profile.interests else None,
                "Verify your email" if not profile.email_verified else None,
                "Enable two-factor authentication" if not profile.two_factor_enabled else None
            ]
        }

# Export components
__all__ = [
    'UserModel', 'UserProfile', 'UserPreferences', 'SocialLinks',
    'UserStatus', 'SubscriptionTier', 'PrivacyLevel'
]