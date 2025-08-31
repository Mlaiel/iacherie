"""👤 Creator Model - IA Influencer Agent Platform Enterprise
=========================================================
Module: backend/data_management/models/creator_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Creator Data Model - Ultra Production-Ready
Responsibility: Advanced data models for multi-format creator profiles with AI-powered analytics
==========================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC CREATOR PIPELINE:
Registration → Profile Setup → Verification → Content Creation → AI Analytics → 
Protection Management → Collaboration → Monetization → Growth Analytics
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from decimal import Decimal
import uuid
import hashlib

class CreatorType(Enum):
    """Advanced creator types supported by the platform"""    MUSICIAN = "musician"
    MUSIC_PRODUCER = "music_producer"
    SINGER_SONGWRITER = "singer_songwriter"
    DJ = "dj"
    BAND = "band"
    PODCASTER = "podcaster"
    INFLUENCER = "influencer"
    CONTENT_CREATOR = "content_creator"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    BLOGGER = "blogger"
    WRITER = "writer"
    COMEDIAN = "comedian"
    ACTOR = "actor"
    VOICE_ACTOR = "voice_actor"
    ARTIST = "artist"
    DESIGNER = "designer"
    ANIMATOR = "animator"
    EDUCATOR = "educator"
    MULTI_FORMAT = "multi_format"
    BRAND = "brand"
    AGENCY = "agency"

class CreatorStatus(Enum):
    """Creator account status lifecycle"""    PENDING = "pending"
    ACTIVE = "active"
    VERIFIED = "verified"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    SUSPENDED = "suspended"
    BANNED = "banned"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class SubscriptionTier(Enum):
    """Subscription tiers with advanced features"""    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class VerificationLevel(IntEnum):
    """Verification levels for credibility"""    UNVERIFIED = 0
    EMAIL_VERIFIED = 1
    PHONE_VERIFIED = 2
    IDENTITY_VERIFIED = 3
    PROFESSIONAL_VERIFIED = 4
    PLATFORM_VERIFIED = 5

class CreatorTier(Enum):
    """Creator tier based on performance and engagement"""    STARTER = "starter"
    RISING = "rising"
    ESTABLISHED = "established"
    PREMIUM = "premium"
    ELITE = "elite"
    LEGENDARY = "legendary"

@dataclass
class CreatorProfile:
    """Advanced public creator profile with comprehensive information and AI analytics"""    
    # Core identity information
    display_name: str = ""
    bio: str = ""
    professional_tagline: str = ""
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    website_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    
    # Professional information
    professional_name: Optional[str] = None
    stage_name: Optional[str] = None
    artist_name: Optional[str] = None
    company_name: Optional[str] = None
    brand_name: Optional[str] = None
    record_label: Optional[str] = None
    management_company: Optional[str] = None
    
    # Specialization and skills
    primary_genre: Optional[str] = None
    genres: List[str] = field(default_factory=list)
    sub_genres: List[str] = field(default_factory=list)
    specialties: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    instruments: List[str] = field(default_factory=list)
    software_expertise: List[str] = field(default_factory=list)
    
    # Geographic and demographic
    country: Optional[str] = None
    state_province: Optional[str] = None
    city: Optional[str] = None
    timezone: str = "UTC"
    languages: List[str] = field(default_factory=list)
    
    # Social media and platform presence
    social_links: Dict[str, str] = field(default_factory=dict)
    platform_usernames: Dict[str, str] = field(default_factory=dict)
    platform_verified: Dict[str, bool] = field(default_factory=dict)
    platform_follower_counts: Dict[str, int] = field(default_factory=dict)
    
    # Public statistics
    total_followers: int = 0
    total_content: int = 0
    total_collaborations: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_shares: int = 0
    engagement_rate: float = 0.0
    
    # Verification and credibility
    verification_badges: List[str] = field(default_factory=list)
    verification_level: VerificationLevel = VerificationLevel.UNVERIFIED
    credibility_score: float = 0.0
    trust_rating: float = 0.0
    
    # Collaboration preferences
    open_to_collaborations: bool = True
    collaboration_types: List[str] = field(default_factory=list)
    collaboration_budget_range: Optional[str] = None
    response_time: Optional[str] = None
    availability_status: str = "available"  # available, busy, unavailable
    
    # Content creation preferences
    content_themes: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    content_schedule: Optional[str] = None
    
    # Professional ratings and reviews
    average_rating: float = 0.0
    total_reviews: int = 0
    professionalism_score: float = 0.0
    creativity_score: float = 0.0
    reliability_score: float = 0.0
    
    # AI-generated insights
    ai_generated_tags: List[str] = field(default_factory=list)
    ai_content_analysis: Dict[str, Any] = field(default_factory=dict)
    ai_audience_insights: Dict[str, Any] = field(default_factory=dict)
    ai_growth_recommendations: List[str] = field(default_factory=list)
    
    def calculate_engagement_rate(self) -> float:
        """Calculate overall engagement rate across platforms"""        if self.total_followers == 0:
            return 0.0
        
        total_engagement = self.total_likes + self.total_shares + (self.total_collaborations * 10)
        self.engagement_rate = (total_engagement / self.total_followers) * 100
        return self.engagement_rate
    
    def calculate_credibility_score(self) -> float:
        """Calculate credibility score based on various factors"""        score = 0.0
        
        # Verification level weight
        score += self.verification_level.value * 15
        
        # Social proof
        if self.total_followers > 1000:
            score += min(20, self.total_followers / 1000)
            
        # Content quality
        if self.total_content > 10:
            score += min(15, self.total_content / 2)
            
        # Collaboration history
        if self.total_collaborations > 5:
            score += min(10, self.total_collaborations)
            
        # Platform verification
        verified_platforms = sum(1 for verified in self.platform_verified.values() if verified)
        score += verified_platforms * 5
        
        # Professional information completeness
        completeness = self.get_profile_completeness()
        score += completeness * 20
        
        self.credibility_score = min(score, 100.0)
        return self.credibility_score
    
    def get_profile_completeness(self) -> float:
        """Calculate profile completeness percentage"""        required_fields = [
            self.display_name, self.bio, self.country, 
            len(self.genres) > 0, len(self.skills) > 0
        ]
        
        optional_fields = [
            self.avatar_url, self.banner_url, self.website_url,
            self.professional_name, len(self.social_links) > 0,
            len(self.languages) > 0, len(self.specialties) > 0
        ]
        
        required_complete = sum(1 for field in required_fields if field)
        optional_complete = sum(1 for field in optional_fields if field)
        
        # 70% weight for required fields, 30% for optional
        completeness = (required_complete / len(required_fields)) * 0.7
        completeness += (optional_complete / len(optional_fields)) * 0.3
        
        return completeness
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""        return {
            "display_name": self.display_name,
            "bio": self.bio,
            "professional_tagline": self.professional_tagline,
            "avatar_url": self.avatar_url,
            "banner_url": self.banner_url,
            "website_url": self.website_url,
            "portfolio_url": self.portfolio_url,
            "professional_name": self.professional_name,
            "stage_name": self.stage_name,
            "artist_name": self.artist_name,
            "company_name": self.company_name,
            "brand_name": self.brand_name,
            "record_label": self.record_label,
            "management_company": self.management_company,
            "primary_genre": self.primary_genre,
            "genres": self.genres,
            "sub_genres": self.sub_genres,
            "specialties": self.specialties,
            "skills": self.skills,
            "instruments": self.instruments,
            "software_expertise": self.software_expertise,
            "country": self.country,
            "state_province": self.state_province,
            "city": self.city,
            "timezone": self.timezone,
            "languages": self.languages,
            "social_links": self.social_links,
            "platform_usernames": self.platform_usernames,
            "platform_verified": self.platform_verified,
            "platform_follower_counts": self.platform_follower_counts,
            "total_followers": self.total_followers,
            "total_content": self.total_content,
            "total_collaborations": self.total_collaborations,
            "total_views": self.total_views,
            "total_likes": self.total_likes,
            "total_shares": self.total_shares,
            "engagement_rate": self.engagement_rate,
            "verification_badges": self.verification_badges,
            "verification_level": self.verification_level.value,
            "credibility_score": self.credibility_score,
            "trust_rating": self.trust_rating,
            "open_to_collaborations": self.open_to_collaborations,
            "collaboration_types": self.collaboration_types,
            "collaboration_budget_range": self.collaboration_budget_range,
            "response_time": self.response_time,
            "availability_status": self.availability_status,
            "content_themes": self.content_themes,
            "target_audience": self.target_audience,
            "content_schedule": self.content_schedule,
            "average_rating": self.average_rating,
            "total_reviews": self.total_reviews,
            "professionalism_score": self.professionalism_score,
            "creativity_score": self.creativity_score,
            "reliability_score": self.reliability_score,
            "ai_generated_tags": self.ai_generated_tags,
            "ai_content_analysis": self.ai_content_analysis,
            "ai_audience_insights": self.ai_audience_insights,
            "ai_growth_recommendations": self.ai_growth_recommendations,
            "profile_completeness": self.get_profile_completeness()
        }

@dataclass
class CreatorSettings:
    """Advanced creator settings and preferences for platform customization"""    
    # Content management preferences
    default_content_visibility: str = "public"  # public, private, unlisted, followers_only
    auto_fingerprinting: bool = True
    auto_protection: bool = True
    auto_distribution: bool = False
    auto_monetization: bool = False
    auto_seo_optimization: bool = True
    auto_social_sharing: bool = False
    
    # Quality and processing preferences
    content_quality_threshold: str = "good"  # poor, fair, good, excellent, premium
    auto_enhance_content: bool = False
    watermark_content: bool = False
    compress_uploads: bool = True
    
    # Notification preferences
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    in_app_notifications: bool = True
    notification_frequency: str = "immediate"  # immediate, daily, weekly
    
    notification_types: Dict[str, bool] = field(default_factory=lambda: {
        "new_collaboration": True,
        "content_match_detected": True,
        "revenue_update": True,
        "security_alert": True,
        "content_approved": True,
        "content_rejected": False,
        "new_follower": False,
        "achievement_unlocked": True,
        "system_maintenance": True,
        "feature_updates": False
    })
    
    # Privacy and security preferences
    profile_visibility: str = "public"  # public, verified_only, private
    analytics_sharing: bool = False
    revenue_sharing: bool = False
    collaboration_history_visible: bool = True
    contact_info_visible: bool = False
    
    # Security settings
    two_factor_enabled: bool = False
    login_notifications: bool = True
    suspicious_activity_alerts: bool = True
    auto_logout_minutes: int = 60
    ip_restriction_enabled: bool = False
    allowed_ips: List[str] = field(default_factory=list)
    
    # Financial preferences
    preferred_currency: str = "EUR"
    payment_methods: List[str] = field(default_factory=list)
    auto_withdrawal: bool = False
    minimum_withdrawal_amount: Decimal = field(default_factory=lambda: Decimal('50.00'))
    tax_info_provided: bool = False
    
    # API and integration preferences
    api_access_enabled: bool = False
    webhook_urls: List[str] = field(default_factory=list)
    integration_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Content distribution preferences
    platform_priorities: Dict[str, int] = field(default_factory=dict)  # platform: priority (1-10)
    cross_posting_enabled: bool = False
    content_scheduling_enabled: bool = False
    
    # Collaboration preferences
    collaboration_auto_accept: bool = False
    collaboration_approval_required: bool = True
    preferred_collaboration_types: List[str] = field(default_factory=list)
    collaboration_rate_ranges: Dict[str, str] = field(default_factory=dict)
    
    def update_notification_setting(self, notification_type: str, enabled: bool) -> None:
        """Update specific notification setting"""        self.notification_types[notification_type] = enabled
    
    def add_payment_method(self, method: str) -> None:
        """Add payment method if not already present"""        if method not in self.payment_methods:
            self.payment_methods.append(method)
    
    def remove_payment_method(self, method: str) -> None:
        """Remove payment method"""        if method in self.payment_methods:
            self.payment_methods.remove(method)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            "default_content_visibility": self.default_content_visibility,
            "auto_fingerprinting": self.auto_fingerprinting,
            "auto_protection": self.auto_protection,
            "auto_distribution": self.auto_distribution,
            "auto_monetization": self.auto_monetization,
            "auto_seo_optimization": self.auto_seo_optimization,
            "auto_social_sharing": self.auto_social_sharing,
            "content_quality_threshold": self.content_quality_threshold,
            "auto_enhance_content": self.auto_enhance_content,
            "watermark_content": self.watermark_content,
            "compress_uploads": self.compress_uploads,
            "email_notifications": self.email_notifications,
            "push_notifications": self.push_notifications,
            "sms_notifications": self.sms_notifications,
            "in_app_notifications": self.in_app_notifications,
            "notification_frequency": self.notification_frequency,
            "notification_types": self.notification_types,
            "profile_visibility": self.profile_visibility,
            "analytics_sharing": self.analytics_sharing,
            "revenue_sharing": self.revenue_sharing,
            "collaboration_history_visible": self.collaboration_history_visible,
            "contact_info_visible": self.contact_info_visible,
            "two_factor_enabled": self.two_factor_enabled,
            "login_notifications": self.login_notifications,
            "suspicious_activity_alerts": self.suspicious_activity_alerts,
            "auto_logout_minutes": self.auto_logout_minutes,
            "ip_restriction_enabled": self.ip_restriction_enabled,
            "allowed_ips": self.allowed_ips,
            "preferred_currency": self.preferred_currency,
            "payment_methods": self.payment_methods,
            "auto_withdrawal": self.auto_withdrawal,
            "minimum_withdrawal_amount": str(self.minimum_withdrawal_amount),
            "tax_info_provided": self.tax_info_provided,
            "api_access_enabled": self.api_access_enabled,
            "webhook_urls": self.webhook_urls,
            "integration_settings": self.integration_settings,
            "platform_priorities": self.platform_priorities,
            "cross_posting_enabled": self.cross_posting_enabled,
            "content_scheduling_enabled": self.content_scheduling_enabled,
            "collaboration_auto_accept": self.collaboration_auto_accept,
            "collaboration_approval_required": self.collaboration_approval_required,
            "preferred_collaboration_types": self.preferred_collaboration_types,
            "collaboration_rate_ranges": self.collaboration_rate_ranges
        }

@dataclass
class CreatorModel:
    """    Ultra-advanced creator model for multi-format content creators with AI-powered analytics and monetization
    Supports comprehensive creator lifecycle from registration to enterprise collaboration
    """    
    # Core identifiers
    creator_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""  # Reference to auth user
    tenant_id: str = ""  # Multi-tenant support
    
    # Account information
    email: str = ""
    username: str = ""
    phone: Optional[str] = None
    
    # Creator classification
    creator_type: CreatorType = CreatorType.MULTI_FORMAT
    creator_status: CreatorStatus = CreatorStatus.PENDING
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    verification_level: VerificationLevel = VerificationLevel.UNVERIFIED
    creator_tier: CreatorTier = CreatorTier.STARTER
    
    # Profile and settings
    profile: CreatorProfile = field(default_factory=CreatorProfile)
    settings: CreatorSettings = field(default_factory=CreatorSettings)
    
    # Analytics and performance metrics
    total_content_count: int = 0
    total_view_count: int = 0
    total_download_count: int = 0
    total_share_count: int = 0
    total_like_count: int = 0
    total_comment_count: int = 0
    total_collaborations: int = 0
    successful_collaborations: int = 0
    
    # Engagement metrics
    average_engagement_rate: float = 0.0
    monthly_growth_rate: float = 0.0
    content_quality_score: float = 0.0
    audience_retention_rate: float = 0.0
    
    # Revenue and monetization
    total_revenue: Decimal = field(default_factory=lambda: Decimal('0.00'))
    current_balance: Decimal = field(default_factory=lambda: Decimal('0.00'))
    total_earnings: Decimal = field(default_factory=lambda: Decimal('0.00'))
    total_withdrawals: Decimal = field(default_factory=lambda: Decimal('0.00'))
    pending_payments: Decimal = field(default_factory=lambda: Decimal('0.00'))
    last_payment_date: Optional[datetime] = None
    
    # Platform analytics
    platform_statistics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    revenue_by_platform: Dict[str, Decimal] = field(default_factory=dict)
    content_by_platform: Dict[str, int] = field(default_factory=dict)
    
    # Protection and security
    protection_alerts_count: int = 0
    security_violations_count: int = 0
    dmca_claims_received: int = 0
    dmca_claims_filed: int = 0
    content_matches_detected: int = 0
    
    # Platform usage and activity
    last_login_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    total_login_count: int = 0
    failed_login_attempts: int = 0
    session_duration_minutes: int = 0
    
    # Quotas and limits
    storage_quota_gb: int = 5  # Storage quota in GB
    storage_used_gb: float = 0.0
    monthly_upload_limit: int = 100
    monthly_uploads_count: int = 0
    api_calls_limit: int = 1000
    api_calls_count: int = 0
    bandwidth_quota_gb: int = 50
    bandwidth_used_gb: float = 0.0
    
    # Social connections and relationships
    following_creators: List[str] = field(default_factory=list)
    followers_creators: List[str] = field(default_factory=list)
    blocked_creators: List[str] = field(default_factory=list)
    favorite_creators: List[str] = field(default_factory=list)
    collaboration_requests_sent: List[str] = field(default_factory=list)
    collaboration_requests_received: List[str] = field(default_factory=list)
    
    # Projects and teams
    owned_projects: List[str] = field(default_factory=list)
    member_projects: List[str] = field(default_factory=list)
    team_members: List[str] = field(default_factory=list)
    
    # AI-powered features
    ai_recommendations: List[str] = field(default_factory=list)
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    ai_content_suggestions: List[str] = field(default_factory=list)
    ai_collaboration_matches: List[str] = field(default_factory=list)
    
    # Achievements and milestones
    achievements_unlocked: List[str] = field(default_factory=list)
    milestone_reached: List[str] = field(default_factory=list)
    badges_earned: List[str] = field(default_factory=list)
    
    # Compliance and legal
    terms_accepted_at: Optional[datetime] = None
    privacy_policy_accepted_at: Optional[datetime] = None
    age_verified: bool = False
    country_restrictions: List[str] = field(default_factory=list)
    
    # Timestamps and lifecycle
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: Optional[datetime] = None
    suspended_at: Optional[datetime] = None
    banned_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    # Status flags
    is_active: bool = True
    is_verified: bool = False
    is_featured: bool = False
    is_trending: bool = False
    is_premium: bool = False
    is_partner: bool = False
    is_beta_tester: bool = False
    
    # Custom data and extensibility
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    notes: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def update_status(self, new_status: CreatorStatus, reason: str = "") -> None:
        """Update creator status with audit trail"""        old_status = self.creator_status
        self.creator_status = new_status
        self.updated_at = datetime.now(timezone.utc)
        
        # Add audit log
        self.notes.append({
            "timestamp": self.updated_at.isoformat(),
            "action": "status_change",
            "old_status": old_status.value,
            "new_status": new_status.value,
            "reason": reason,
            "changed_by": "system"
        })
        
        # Handle status-specific actions
        if new_status == CreatorStatus.VERIFIED:
            self.verified_at = self.updated_at
            self.is_verified = True
            self.verification_level = VerificationLevel.PLATFORM_VERIFIED
        elif new_status == CreatorStatus.SUSPENDED:
            self.suspended_at = self.updated_at
            self.is_active = False
        elif new_status == CreatorStatus.BANNED:
            self.banned_at = self.updated_at
            self.is_active = False
        elif new_status == CreatorStatus.ACTIVE:
            self.is_active = True
            self.suspended_at = None
    
    def calculate_creator_tier(self) -> CreatorTier:
        """Calculate creator tier based on performance metrics"""        score = 0
        
        # Content volume scoring
        if self.total_content_count >= 100:
            score += 20
        elif self.total_content_count >= 50:
            score += 15
        elif self.total_content_count >= 20:
            score += 10
        elif self.total_content_count >= 5:
            score += 5
            
        # Engagement scoring
        if self.average_engagement_rate >= 10.0:
            score += 25
        elif self.average_engagement_rate >= 5.0:
            score += 20
        elif self.average_engagement_rate >= 2.0:
            score += 15
        elif self.average_engagement_rate >= 1.0:
            score += 10
            
        # Revenue scoring
        if self.total_revenue >= 10000:
            score += 30
        elif self.total_revenue >= 5000:
            score += 25
        elif self.total_revenue >= 1000:
            score += 20
        elif self.total_revenue >= 100:
            score += 15
        elif self.total_revenue >= 10:
            score += 10
            
        # Collaboration scoring
        if self.successful_collaborations >= 20:
            score += 15
        elif self.successful_collaborations >= 10:
            score += 10
        elif self.successful_collaborations >= 5:
            score += 5
            
        # Quality scoring
        if self.content_quality_score >= 4.5:
            score += 10
        elif self.content_quality_score >= 4.0:
            score += 8
        elif self.content_quality_score >= 3.5:
            score += 5
            
        # Assign tier based on score
        if score >= 90:
            self.creator_tier = CreatorTier.LEGENDARY
        elif score >= 75:
            self.creator_tier = CreatorTier.ELITE
        elif score >= 60:
            self.creator_tier = CreatorTier.PREMIUM
        elif score >= 45:
            self.creator_tier = CreatorTier.ESTABLISHED
        elif score >= 25:
            self.creator_tier = CreatorTier.RISING
        else:
            self.creator_tier = CreatorTier.STARTER
            
        return self.creator_tier
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary with optional sensitive data inclusion"""        base_data = {
            "creator_id": self.creator_id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "email": self.email,
            "username": self.username,
            "creator_type": self.creator_type.value,
            "creator_status": self.creator_status.value,
            "subscription_tier": self.subscription_tier.value,
            "verification_level": self.verification_level.value,
            "creator_tier": self.creator_tier.value,
            "profile": self.profile.to_dict(),
            "total_content_count": self.total_content_count,
            "total_view_count": self.total_view_count,
            "total_collaborations": self.total_collaborations,
            "successful_collaborations": self.successful_collaborations,
            "average_engagement_rate": self.average_engagement_rate,
            "content_quality_score": self.content_quality_score,
            "platform_statistics": self.platform_statistics,
            "achievements_unlocked": self.achievements_unlocked,
            "badges_earned": self.badges_earned,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_featured": self.is_featured,
            "is_trending": self.is_trending,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "verified_at": self.verified_at.isoformat() if self.verified_at else None
        }
        
        if include_sensitive:
            base_data.update({
                "phone": self.phone,
                "settings": self.settings.to_dict(),
                "total_revenue": str(self.total_revenue),
                "current_balance": str(self.current_balance),
                "revenue_by_platform": {k: str(v) for k, v in self.revenue_by_platform.items()},
                "protection_alerts_count": self.protection_alerts_count,
                "storage_used_gb": self.storage_used_gb,
                "following_creators": self.following_creators,
                "followers_creators": self.followers_creators,
                "owned_projects": self.owned_projects,
                "ai_recommendations": self.ai_recommendations,
                "ai_insights": self.ai_insights,
                "custom_fields": self.custom_fields,
                "notes": self.notes[-10:]  # Last 10 notes only
            })
        
        return base_data
    
    def __repr__(self) -> str:
        return f"CreatorModel(id={self.creator_id}, type={self.creator_type.value}, status={self.creator_status.value})"


# Creator utility functions
def generate_username(display_name: str, creator_type: CreatorType) -> str:
    """Generate unique username suggestion"""    base = display_name.lower().replace(' ', '_')
    type_suffix = creator_type.value[:3]
    random_suffix = hashlib.md5(f"{base}{datetime.now().timestamp()}".encode()).hexdigest()[:4]
    
    return f"{base}_{type_suffix}_{random_suffix}"


def validate_creator_email(email: str) -> bool:
    """Validate creator email format"""    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def calculate_creator_score(creator: CreatorModel) -> float:
    """Calculate overall creator score for ranking"""    score = 0.0
    
    # Content contribution (30%)
    content_score = min(creator.total_content_count / 100, 1.0) * 30
    
    # Engagement performance (25%)
    engagement_score = min(creator.average_engagement_rate / 10, 1.0) * 25
    
    # Quality score (20%)
    quality_score = (creator.content_quality_score / 5.0) * 20
    
    # Collaboration success (15%)
    if creator.total_collaborations > 0:
        collab_success = creator.successful_collaborations / creator.total_collaborations
        collab_score = collab_success * 15
    else:
        collab_score = 0
    
    # Verification and trust (10%)
    verification_score = (creator.verification_level.value / 5.0) * 10
    
    score = content_score + engagement_score + quality_score + collab_score + verification_score
    
    return min(score, 100.0)


# Export all creator model classes
__all__ = [
    "CreatorType", "CreatorStatus", "SubscriptionTier", "VerificationLevel", 
    "CreatorTier", "CreatorProfile", "CreatorSettings", "CreatorModel",
    "generate_username", "validate_creator_email", "calculate_creator_score"
]
