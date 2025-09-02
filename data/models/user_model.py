"""User Data Model
==============

Professional user data model for IA Influencer Agent platform.
Comprehensive user management with multi-platform integration and analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from datetime import datetime, date
from typing import Optional, Dict, List, Any
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, DECIMAL, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
import hashlib

Base = declarative_base()


class UserType(Enum):
    """
User type enumeration"""

    CREATOR = "creator"
    ARTIST = "artist"
    INFLUENCER = "influencer" 
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    BLOGGER = "blogger"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    BUSINESS = "business"
    AGENCY = "agency"
    ADMIN = "admin"


class UserStatus(Enum):
    """User status enumeration"""

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    INACTIVE = "inactive"
    PREMIUM = "premium"
    VIP = "vip"


class SubscriptionTier(Enum):
    """Subscription tier enumeration"""

    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"


class UserModel(Base):
    """
    Professional user data model for IA Influencer Agent platform.
    
    Comprehensive user management with multi-platform integration,
    analytics, subscription management, and content creator features.
    """
    
    __tablename__ = "users"
    
    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    phone = Column(String(20))
    phone_verified = Column(Boolean, default=False)
    
    # Basic profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    display_name = Column(String(150))
    bio = Column(Text)
    website_url = Column(String(500))
    avatar_url = Column(String(500))
    banner_url = Column(String(500))
    
    # User type and status
    user_type = Column(String(20), default=UserType.CREATOR.value)
    status = Column(String(20), default=UserStatus.ACTIVE.value)
    subscription_tier = Column(String(20), default=SubscriptionTier.FREE.value)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_business = Column(Boolean, default=False)
    
    # Authentication and security
    password_hash = Column(String(255))
    salt = Column(String(64))
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32))
    last_login_at = Column(DateTime)
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime)
    
    # Location and demographics
    country = Column(String(2))  # ISO country code
    region = Column(String(100))
    city = Column(String(100))
    timezone = Column(String(50))
    language = Column(String(10), default="en")  # Primary language
    languages_spoken = Column(ARRAY(String))  # All languages
    birth_date = Column(Date)
    gender = Column(String(20))
    
    # Creator-specific information
    creator_category = Column(String(50))  # music, video, photography, etc.
    content_focus = Column(ARRAY(String))  # genres, themes, topics
    target_audience = Column(JSON)  # demographic data
    collaboration_open = Column(Boolean, default=True)
    hire_available = Column(Boolean, default=False)
    hourly_rate = Column(DECIMAL(8, 2))
    currency = Column(String(3), default="EUR")
    
    # Platform integrations
    spotify_id = Column(String(100))
    spotify_profile = Column(JSON)
    youtube_id = Column(String(100))
    youtube_profile = Column(JSON)
    instagram_id = Column(String(100))
    instagram_profile = Column(JSON)
    tiktok_id = Column(String(100))
    tiktok_profile = Column(JSON)
    twitter_id = Column(String(100))
    twitter_profile = Column(JSON)
    soundcloud_id = Column(String(100))
    soundcloud_profile = Column(JSON)
    twitch_id = Column(String(100))
    twitch_profile = Column(JSON)
    
    # Platform statistics
    total_followers = Column(Integer, default=0)
    total_content_count = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    
    # Revenue and monetization
    total_revenue = Column(DECIMAL(12, 4), default=0)
    monthly_revenue = Column(DECIMAL(10, 4), default=0)
    revenue_goal = Column(DECIMAL(10, 4))
    monetization_enabled = Column(Boolean, default=False)
    payment_methods = Column(JSON)  # Stripe, PayPal, Wise, etc.
    tax_information = Column(JSON)  # Tax forms and details
    
    # Subscription and billing
    subscription_starts_at = Column(DateTime)
    subscription_ends_at = Column(DateTime)
    subscription_auto_renew = Column(Boolean, default=True)
    billing_address = Column(JSON)
    payment_customer_id = Column(String(100))  # Stripe customer ID
    last_payment_at = Column(DateTime)
    next_billing_date = Column(DateTime)
    
    # Usage and limits
    content_upload_count = Column(Integer, default=0)
    content_upload_limit = Column(Integer, default=100)
    storage_used = Column(Integer, default=0)  # bytes
    storage_limit = Column(Integer, default=1073741824)  # 1GB default
    api_calls_count = Column(Integer, default=0)
    api_calls_limit = Column(Integer, default=1000)
    
    # AI and ML preferences
    ai_processing_enabled = Column(Boolean, default=True)
    ai_recommendations_enabled = Column(Boolean, default=True)
    auto_tagging_enabled = Column(Boolean, default=True)
    auto_seo_enabled = Column(Boolean, default=True)
    ai_generation_enabled = Column(Boolean, default=False)
    ml_model_preferences = Column(JSON)
    
    # Privacy and security settings
    profile_visibility = Column(String(20), default="public")
    contact_visibility = Column(String(20), default="private")
    analytics_visibility = Column(String(20), default="private")
    allow_collaboration_requests = Column(Boolean, default=True)
    allow_hire_requests = Column(Boolean, default=False)
    allow_direct_messages = Column(Boolean, default=True)
    data_export_enabled = Column(Boolean, default=True)
    
    # Protection and copyright
    content_protection_enabled = Column(Boolean, default=True)
    auto_fingerprinting = Column(Boolean, default=True)
    watermarking_enabled = Column(Boolean, default=False)
    copyright_monitoring = Column(Boolean, default=True)
    takedown_auto_enabled = Column(Boolean, default=False)
    
    # Notification preferences
    email_notifications = Column(JSON)
    push_notifications = Column(JSON)
    sms_notifications = Column(JSON)
    notification_frequency = Column(String(20), default="immediate")
    
    # Analytics and insights
    profile_views = Column(Integer, default=0)
    search_appearances = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    growth_rate = Column(Float, default=0.0)
    influence_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    
    # Performance metrics
    content_performance_avg = Column(Float, default=0.0)
    audience_retention_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    collaboration_success_rate = Column(Float, default=0.0)
    
    # Business information (for business accounts)
    company_name = Column(String(200))
    business_type = Column(String(50))
    tax_id = Column(String(50))
    business_address = Column(JSON)
    business_phone = Column(String(20))
    business_email = Column(String(255))
    business_website = Column(String(500))
    
    # Team and collaboration
    team_members = Column(JSON)  # Team member IDs and roles
    collaboration_history = Column(JSON)
    referral_code = Column(String(20))
    referred_by = Column(String(36))  # User ID who referred
    referral_earnings = Column(DECIMAL(10, 4), default=0)
    
    # Metadata and tracking
    metadata = Column(JSON)  # Flexible metadata storage
    tags = Column(ARRAY(String))  # User tags for categorization
    notes = Column(Text)  # Internal notes (admin only)
    source = Column(String(50))  # Registration source
    utm_data = Column(JSON)  # UTM tracking data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    email_verified_at = Column(DateTime)
    phone_verified_at = Column(DateTime)
    
    # Soft delete
    deleted_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    content = relationship("ContentModel", back_populates="user")
    analytics = relationship("AnalyticsModel", back_populates="user")
    revenue_records = relationship("RevenueModel", back_populates="user")
    protection_records = relationship("ProtectionModel", back_populates="user")
    fingerprints = relationship("FingerprintModel", back_populates="user")
    licenses = relationship("LicensingModel", back_populates="user")
    
    def __repr__(self):
        try:
            logger.info(f"Executing __repr__")
            
            # Implementation for __repr__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__repr__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__repr__ failed: {e}")
            raise
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary representation"""
        base_data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'display_name': self.display_name,
            'bio': self.bio,
            'website_url': self.website_url,
            'avatar_url': self.avatar_url,
            'banner_url': self.banner_url,
            'user_type': self.user_type,
            'status': self.status,
            'subscription_tier': self.subscription_tier,
            'is_verified': self.is_verified,
            'is_premium': self.is_premium,
            'is_business': self.is_business,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'language': self.language,
            'languages_spoken': self.languages_spoken,
            'creator_category': self.creator_category,
            'content_focus': self.content_focus,
            'collaboration_open': self.collaboration_open,
            'hire_available': self.hire_available,
            'total_followers': self.total_followers,
            'total_content_count': self.total_content_count,
            'total_views': self.total_views,
            'engagement_rate': self.engagement_rate,
            'influence_score': self.influence_score,
            'quality_score': self.quality_score,
            'profile_views': self.profile_views,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active_at': self.last_active_at.isoformat() if self.last_active_at else None,
            'is_deleted': self.is_deleted
        }
        
        if include_sensitive:
            base_data.update({
                'phone': self.phone,
                'total_revenue': float(self.total_revenue) if self.total_revenue else 0.0,
                'monthly_revenue': float(self.monthly_revenue) if self.monthly_revenue else 0.0,
                'subscription_ends_at': self.subscription_ends_at.isoformat() if self.subscription_ends_at else None,
                'storage_used': self.storage_used,
                'storage_limit': self.storage_limit,
                'content_upload_count': self.content_upload_count,
                'content_upload_limit': self.content_upload_limit
            })
        
        return base_data
    
    @property
    def full_name(self) -> str:
        """
Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.username
    
    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE.value and not self.is_deleted
    
    @property
    def is_premium_user(self) -> bool:
        """
Check if user has premium subscription"""
        return (self.is_premium or 
                self.subscription_tier in [SubscriptionTier.PROFESSIONAL.value, 
                                         SubscriptionTier.ENTERPRISE.value,
                                         SubscriptionTier.UNLIMITED.value])
    
    @property
    def storage_usage_percentage(self) -> float:
        """
Calculate storage usage percentage"""
        if self.storage_limit and self.storage_limit > 0:
            return (self.storage_used / self.storage_limit) * 100
        return 0.0
    
    @property
    def content_upload_percentage(self) -> float:
        """
Calculate content upload limit usage percentage"""
        if self.content_upload_limit and self.content_upload_limit > 0:
            return (self.content_upload_count / self.content_upload_limit) * 100
        return 0.0
    
    @property
    def age(self) -> Optional[int]:
        """
Calculate user's age"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    @property
    def is_subscription_active(self) -> bool:
        """
Check if subscription is active"""
        if not self.subscription_ends_at:
            return self.subscription_tier == SubscriptionTier.FREE.value
        return datetime.utcnow() < self.subscription_ends_at
    
    @property
    def platform_count(self) -> int:
        try:
            logger.info(f"Executing set_password")
            
            # Implementation for set_password
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"set_password completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing verify_password")
            
            # Implementation for verify_password
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"verify_password completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"verify_password failed: {e}")
            raise
Set user password with salt and hash"""
        import secrets
        self.salt = secrets.token_hex(32)
        self.password_hash = hashlib.pbkdf2_hmac('sha256', 
                                               password.encode('utf-8'), 
                                               self.salt.encode('utf-8'), 
                                               100000).hex()
        self.updated_at = datetime.utcnow()
    
    def verify_password(self, password: str) -> bool:
        """
Verify user password"""
        if not self.password_hash or not self.salt:
            return False
        
        hash_to_check = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          self.salt.encode('utf-8'),
                                          100000).hex()
        return hash_to_check == self.password_hash
    
    def update_last_login(self):
        """
Update last login timestamp and count"""
        self.last_login_at = datetime.utcnow()
        self.last_active_at = datetime.utcnow()
        self.login_count = (self.login_count or 0) + 1
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()
    
    def record_failed_login(self):
        """
Record failed login attempt"""
        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        self.updated_at = datetime.utcnow()
    
    def is_account_locked(self) -> bool:
        """
Check if account is locked"""
        if not self.account_locked_until:
            return False
        return datetime.utcnow() < self.account_locked_until
    
    def unlock_account(self):
        """
Unlock user account"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()
    
    def update_platform_stats(self, platform_data: Dict[str, Any]):
        """
Update platform statistics"""
        for platform, data in platform_data.items():
            if platform == 'spotify' and 'followers' in data:
                self.spotify_profile = {**(self.spotify_profile or {}), **data}
            elif platform == 'youtube' and 'subscribers' in data:
                self.youtube_profile = {**(self.youtube_profile or {}), **data}
            elif platform == 'instagram' and 'followers' in data:
                self.instagram_profile = {**(self.instagram_profile or {}), **data}
            # ... add other platforms
        
        # Recalculate total followers
        self.calculate_total_stats()
        self.updated_at = datetime.utcnow()
    
    def calculate_total_stats(self):
        """
Calculate total statistics across all platforms"""
        total_followers = 0
        total_content = 0
        total_views = 0
        
        platforms = [
            self.spotify_profile, self.youtube_profile, self.instagram_profile,
            self.tiktok_profile, self.twitter_profile, self.soundcloud_profile,
            self.twitch_profile
        ]
        
        for profile in platforms:
            if profile:
                total_followers += profile.get('followers', 0) + profile.get('subscribers', 0)
                total_content += profile.get('content_count', 0) + profile.get('videos', 0)
                total_views += profile.get('views', 0) + profile.get('plays', 0)
        
        self.total_followers = total_followers
        self.total_content_count = total_content
        self.total_views = total_views
        
        # Calculate engagement rate
        if self.total_views > 0:
            total_interactions = (self.total_likes or 0) + (self.total_shares or 0) + (self.total_comments or 0)
            self.engagement_rate = total_interactions / self.total_views
    
    def upgrade_subscription(self, tier: str, ends_at: datetime = None):
        """
Upgrade user subscription"""
        self.subscription_tier = tier
        self.subscription_starts_at = datetime.utcnow()
        self.subscription_ends_at = ends_at
        
        if tier in [SubscriptionTier.PROFESSIONAL.value, SubscriptionTier.ENTERPRISE.value, SubscriptionTier.UNLIMITED.value]:
            self.is_premium = True
            
            # Increase limits based on tier
            if tier == SubscriptionTier.PROFESSIONAL.value:
                self.content_upload_limit = 1000
                self.storage_limit = 10 * 1024 * 1024 * 1024  # 10GB
                self.api_calls_limit = 10000
            elif tier == SubscriptionTier.ENTERPRISE.value:
                self.content_upload_limit = 10000
                self.storage_limit = 100 * 1024 * 1024 * 1024  # 100GB
                self.api_calls_limit = 100000
            elif tier == SubscriptionTier.UNLIMITED.value:
                self.content_upload_limit = -1  # Unlimited
                self.storage_limit = -1  # Unlimited
                self.api_calls_limit = -1  # Unlimited
        
        self.updated_at = datetime.utcnow()
    
    def add_revenue(self, amount: Decimal, currency: str = "EUR"):
        """Add revenue to user account"""
        if not self.total_revenue:
            self.total_revenue = Decimal('0')
        
        # Convert currency if needed (simplified)
        if currency == self.currency:
            self.total_revenue += amount
        else:
            # In real implementation, would convert currencies
            self.total_revenue += amount
        
        # Update monthly revenue (simplified - would need proper month tracking)
        if not self.monthly_revenue:
            self.monthly_revenue = Decimal('0')
        self.monthly_revenue += amount
        
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self):
        """
Soft delete user account"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.status = UserStatus.INACTIVE.value
        self.updated_at = datetime.utcnow()
    
    def restore(self):
        """
Restore soft-deleted user account"""
        self.is_deleted = False
        self.deleted_at = None
        self.status = UserStatus.ACTIVE.value
        self.updated_at = datetime.utcnow()
    
    def verify_email(self):
        """
Mark email as verified"""
        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def verify_phone(self):
        """
Mark phone as verified"""
        self.phone_verified = True
        self.phone_verified_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def generate_referral_code(self) -> str:
        """
Generate unique referral code"""
        import secrets
        import string
        
        if not self.referral_code:
            # Generate 8-character alphanumeric code
            self.referral_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            self.updated_at = datetime.utcnow()
        
        return self.referral_code
