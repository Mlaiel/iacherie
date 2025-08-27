"""
Creator Profiles Database Model

Enterprise-grade SQLAlchemy model for managing comprehensive creator profiles,
skills, preferences, achievements, and professional information.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone, date
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class CreatorType(Enum):
    """Creator type enumeration"""
    MUSICIAN = "musician"
    PODCASTER = "podcaster"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ARTIST = "artist"
    WRITER = "writer"
    DANCER = "dancer"
    CHEF = "chef"
    FITNESS_TRAINER = "fitness_trainer"
    EDUCATOR = "educator"
    GAMER = "gamer"
    STREAMER = "streamer"
    VOICE_ACTOR = "voice_actor"
    PRODUCER = "producer"
    DJ = "dj"
    COMPOSER = "composer"
    SONGWRITER = "songwriter"
    MULTI_CREATOR = "multi_creator"


class CareerLevel(Enum):
    """Career level enumeration"""
    BEGINNER = "beginner"
    EMERGING = "emerging"
    INTERMEDIATE = "intermediate"
    EXPERIENCED = "experienced"
    PROFESSIONAL = "professional"
    EXPERT = "expert"
    INDUSTRY_LEADER = "industry_leader"
    LEGEND = "legend"


class VerificationStatus(Enum):
    """Account verification status"""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    PREMIUM_VERIFIED = "premium_verified"
    BLUE_CHECKMARK = "blue_checkmark"
    GOLD_CHECKMARK = "gold_checkmark"


class CollaborationStyle(Enum):
    """Collaboration preferences"""
    OPEN_TO_ALL = "open_to_all"
    SELECTIVE = "selective"
    INVITATION_ONLY = "invitation_only"
    NO_COLLABORATIONS = "no_collaborations"
    SAME_GENRE_ONLY = "same_genre_only"
    CROSS_GENRE = "cross_genre"
    PROFESSIONAL_ONLY = "professional_only"
    BEGINNERS_WELCOME = "beginners_welcome"


class ContentStyle(Enum):
    """Content creation style"""
    ORIGINAL = "original"
    COVERS = "covers"
    REMIXES = "remixes"
    MASHUPS = "mashups"
    TUTORIALS = "tutorials"
    REVIEWS = "reviews"
    COMMENTARY = "commentary"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    ARTISTIC = "artistic"
    COMMERCIAL = "commercial"
    EXPERIMENTAL = "experimental"


class AudienceSize(Enum):
    """Audience size categories"""
    NANO = "nano"          # 1-1K
    MICRO = "micro"        # 1K-10K
    MID_TIER = "mid_tier"  # 10K-100K
    MACRO = "macro"        # 100K-1M
    MEGA = "mega"          # 1M+
    CELEBRITY = "celebrity" # 10M+


class CreatorProfile(Base):
    """
    Enterprise Creator Profile Model
    
    Comprehensive creator profile management with skills tracking,
    achievements, preferences, and professional development metrics.
    """
    __tablename__ = 'creator_profiles'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    # Basic profile information
    stage_name = Column(String(200), nullable=False, index=True)
    real_name = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    tagline = Column(String(500), nullable=True)
    pronouns = Column(String(50), nullable=True)
    
    # Creator classification
    creator_type = Column(SQLEnum(CreatorType), nullable=False, index=True)
    secondary_types = Column(ARRAY(String), nullable=True)
    career_level = Column(SQLEnum(CareerLevel), nullable=False, default=CareerLevel.BEGINNER, index=True)
    verification_status = Column(SQLEnum(VerificationStatus), nullable=False, default=VerificationStatus.UNVERIFIED, index=True)
    
    # Demographics
    birth_date = Column(DateTime, nullable=True)
    location_country = Column(String(100), nullable=True, index=True)
    location_city = Column(String(100), nullable=True, index=True)
    location_timezone = Column(String(50), nullable=True)
    languages_spoken = Column(ARRAY(String), nullable=True)
    primary_language = Column(String(10), nullable=False, default="en")
    
    # Professional information
    years_active = Column(Integer, nullable=True)
    started_date = Column(DateTime, nullable=True)
    management_contact = Column(String(200), nullable=True)
    booking_contact = Column(String(200), nullable=True)
    press_contact = Column(String(200), nullable=True)
    business_email = Column(String(200), nullable=True)
    
    # Content creation preferences
    content_style = Column(SQLEnum(ContentStyle), nullable=False, default=ContentStyle.ORIGINAL, index=True)
    primary_genres = Column(ARRAY(String), nullable=True)
    secondary_genres = Column(ARRAY(String), nullable=True)
    content_themes = Column(ARRAY(String), nullable=True)
    content_formats = Column(ARRAY(String), nullable=True)  # audio, video, image, text
    
    # Collaboration preferences
    collaboration_style = Column(SQLEnum(CollaborationStyle), nullable=False, default=CollaborationStyle.OPEN_TO_ALL, index=True)
    open_to_collaborations = Column(Boolean, nullable=False, default=True)
    collaboration_rate = Column(Numeric(10, 2), nullable=True)
    collaboration_preferences = Column(JSONB, nullable=True)
    
    # Audience metrics
    audience_size = Column(SQLEnum(AudienceSize), nullable=False, default=AudienceSize.NANO, index=True)
    total_followers = Column(Integer, nullable=False, default=0)
    total_subscribers = Column(Integer, nullable=False, default=0)
    monthly_listeners = Column(Integer, nullable=False, default=0)
    avg_engagement_rate = Column(Float, nullable=False, default=0.0)
    
    # Platform presence
    platform_accounts = Column(JSONB, nullable=True)  # {platform: {username, followers, verified}}
    primary_platforms = Column(ARRAY(String), nullable=True)
    verified_platforms = Column(ARRAY(String), nullable=True)
    monetized_platforms = Column(ARRAY(String), nullable=True)
    
    # Skills and expertise
    technical_skills = Column(JSONB, nullable=True)  # {skill: proficiency_level}
    creative_skills = Column(JSONB, nullable=True)
    software_proficiency = Column(JSONB, nullable=True)
    equipment_owned = Column(JSONB, nullable=True)
    
    # Achievements and recognition
    awards = Column(JSONB, nullable=True)
    certifications = Column(JSONB, nullable=True)
    milestones = Column(JSONB, nullable=True)
    featured_in = Column(JSONB, nullable=True)  # Media mentions, features
    press_coverage = Column(JSONB, nullable=True)
    
    # Performance metrics
    content_count = Column(Integer, nullable=False, default=0)
    total_views = Column(Integer, nullable=False, default=0)
    total_plays = Column(Integer, nullable=False, default=0)
    total_downloads = Column(Integer, nullable=False, default=0)
    viral_content_count = Column(Integer, nullable=False, default=0)
    
    # Engagement metrics
    avg_likes_per_post = Column(Float, nullable=False, default=0.0)
    avg_comments_per_post = Column(Float, nullable=False, default=0.0)
    avg_shares_per_post = Column(Float, nullable=False, default=0.0)
    fan_growth_rate = Column(Float, nullable=False, default=0.0)
    retention_rate = Column(Float, nullable=False, default=0.0)
    
    # Revenue metrics
    total_revenue = Column(Numeric(12, 2), nullable=False, default=0.00)
    monthly_revenue = Column(Numeric(10, 2), nullable=False, default=0.00)
    revenue_streams = Column(JSONB, nullable=True)
    monetization_status = Column(String(50), nullable=False, default="inactive")
    
    # Brand partnerships
    brand_partnerships = Column(JSONB, nullable=True)
    sponsorship_rate = Column(Numeric(10, 2), nullable=True)
    partnership_preferences = Column(JSONB, nullable=True)
    brand_safety_score = Column(Float, nullable=True)  # 0-100
    
    # Content protection preferences
    protection_level = Column(String(50), nullable=False, default="standard")
    copyright_enforcement = Column(Boolean, nullable=False, default=True)
    watermark_preferences = Column(JSONB, nullable=True)
    licensing_preferences = Column(JSONB, nullable=True)
    
    # AI preferences
    ai_assistance_enabled = Column(Boolean, nullable=False, default=True)
    ai_content_generation = Column(Boolean, nullable=False, default=False)
    ai_analytics_enabled = Column(Boolean, nullable=False, default=True)
    ai_recommendations_enabled = Column(Boolean, nullable=False, default=True)
    
    # Privacy settings
    profile_visibility = Column(String(50), nullable=False, default="public")
    show_real_name = Column(Boolean, nullable=False, default=False)
    show_location = Column(Boolean, nullable=False, default=True)
    show_contact_info = Column(Boolean, nullable=False, default=True)
    show_metrics = Column(Boolean, nullable=False, default=True)
    
    # Professional development
    career_goals = Column(JSONB, nullable=True)
    learning_interests = Column(ARRAY(String), nullable=True)
    mentor_seeking = Column(Boolean, nullable=False, default=False)
    mentor_offering = Column(Boolean, nullable=False, default=False)
    workshop_interests = Column(ARRAY(String), nullable=True)
    
    # Quality scores
    profile_completeness = Column(Float, nullable=False, default=0.0)  # 0-100%
    content_quality_score = Column(Float, nullable=False, default=0.0)  # 0-100
    professionalism_score = Column(Float, nullable=False, default=0.0)  # 0-100
    reliability_score = Column(Float, nullable=False, default=0.0)  # 0-100
    
    # Activity tracking
    last_active_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_content_upload = Column(DateTime(timezone=True), nullable=True)
    content_upload_frequency = Column(String(50), nullable=True)  # daily, weekly, monthly
    activity_score = Column(Float, nullable=False, default=0.0)
    
    # Timing information
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    verified_at = Column(DateTime(timezone=True), nullable=True)
    featured_until = Column(DateTime(timezone=True), nullable=True)
    
    # Advanced features
    custom_branding = Column(JSONB, nullable=True)  # Colors, logos, themes
    portfolio_items = Column(JSONB, nullable=True)
    testimonials = Column(JSONB, nullable=True)
    press_kit_url = Column(Text, nullable=True)
    media_kit_url = Column(Text, nullable=True)
    
    # Analytics preferences
    analytics_sharing = Column(Boolean, nullable=False, default=False)
    benchmark_participation = Column(Boolean, nullable=False, default=True)
    trend_notifications = Column(Boolean, nullable=False, default=True)
    performance_alerts = Column(Boolean, nullable=False, default=True)
    
    # Administrative fields
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_featured = Column(Boolean, nullable=False, default=False, index=True)
    is_suspended = Column(Boolean, nullable=False, default=False, index=True)
    is_premium = Column(Boolean, nullable=False, default=False, index=True)
    
    # Audit trail
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_creator_profile_user_id', 'user_id'),
        Index('idx_creator_profile_stage_name', 'stage_name'),
        Index('idx_creator_profile_type_level', 'creator_type', 'career_level'),
        Index('idx_creator_profile_verification', 'verification_status'),
        Index('idx_creator_profile_location', 'location_country', 'location_city'),
        Index('idx_creator_profile_audience', 'audience_size', 'total_followers'),
        Index('idx_creator_profile_collaboration', 'collaboration_style', 'open_to_collaborations'),
        Index('idx_creator_profile_activity', 'is_active', 'last_active_at'),
        Index('idx_creator_profile_performance', 'content_quality_score', 'professionalism_score'),
        Index('idx_creator_profile_revenue', 'monthly_revenue'),
        Index('idx_creator_profile_featured', 'is_featured', 'featured_until'),
    )
    
    def __repr__(self):
        return f"<CreatorProfile(id={self.id}, stage_name={self.stage_name}, type={self.creator_type.value})>"
    
    @classmethod
    def create_basic_profile(cls, user_id: str, stage_name: str, creator_type: CreatorType) -> 'CreatorProfile':
        """Create basic creator profile"""
        return cls(
            user_id=user_id,
            stage_name=stage_name,
            creator_type=creator_type,
            profile_id=f"creator_{uuid.uuid4().hex[:8]}",
            created_by="system"
        )
    
    def calculate_profile_completeness(self) -> float:
        """Calculate profile completeness percentage"""
        fields_to_check = [
            'stage_name', 'bio', 'creator_type', 'primary_genres',
            'location_country', 'primary_language', 'platform_accounts',
            'technical_skills', 'content_style'
        ]
        
        completed_fields = 0
        for field in fields_to_check:
            value = getattr(self, field, None)
            if value is not None and value != [] and value != {}:
                completed_fields += 1
        
        self.profile_completeness = (completed_fields / len(fields_to_check)) * 100
        return self.profile_completeness
    
    def update_audience_metrics(self, platform_data: Dict[str, Dict[str, Any]]) -> None:
        """Update audience metrics from platform data"""
        total_followers = 0
        total_subscribers = 0
        
        for platform, data in platform_data.items():
            total_followers += data.get('followers', 0)
            total_subscribers += data.get('subscribers', 0)
        
        self.total_followers = total_followers
        self.total_subscribers = total_subscribers
        
        # Update audience size category
        if total_followers >= 10_000_000:
            self.audience_size = AudienceSize.CELEBRITY
        elif total_followers >= 1_000_000:
            self.audience_size = AudienceSize.MEGA
        elif total_followers >= 100_000:
            self.audience_size = AudienceSize.MACRO
        elif total_followers >= 10_000:
            self.audience_size = AudienceSize.MID_TIER
        elif total_followers >= 1_000:
            self.audience_size = AudienceSize.MICRO
        else:
            self.audience_size = AudienceSize.NANO
        
        self.updated_at = datetime.now(timezone.utc)
    
    def add_achievement(self, achievement_type: str, title: str, description: str, date_achieved: datetime = None) -> None:
        """Add achievement to profile"""
        if self.achievements is None:
            self.achievements = []
        
        achievement = {
            'id': str(uuid.uuid4()),
            'type': achievement_type,
            'title': title,
            'description': description,
            'date_achieved': (date_achieved or datetime.now(timezone.utc)).isoformat(),
            'verified': False
        }
        
        self.achievements.append(achievement)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_skill_proficiency(self, skill: str, proficiency: float) -> None:
        """Update skill proficiency level (0-100)"""
        if self.technical_skills is None:
            self.technical_skills = {}
        
        self.technical_skills[skill] = {
            'proficiency': min(100, max(0, proficiency)),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        self.updated_at = datetime.now(timezone.utc)
    
    def get_collaboration_score(self, other_creator: 'CreatorProfile') -> float:
        """Calculate collaboration compatibility score with another creator"""
        score = 0.0
        
        # Genre compatibility
        if self.primary_genres and other_creator.primary_genres:
            common_genres = set(self.primary_genres).intersection(set(other_creator.primary_genres))
            score += len(common_genres) * 10
        
        # Career level compatibility
        level_diff = abs(list(CareerLevel).index(self.career_level) - list(CareerLevel).index(other_creator.career_level))
        score += max(0, 20 - level_diff * 5)
        
        # Audience size compatibility
        audience_diff = abs(list(AudienceSize).index(self.audience_size) - list(AudienceSize).index(other_creator.audience_size))
        score += max(0, 15 - audience_diff * 3)
        
        # Collaboration openness
        if (self.collaboration_style != CollaborationStyle.NO_COLLABORATIONS and 
            other_creator.collaboration_style != CollaborationStyle.NO_COLLABORATIONS):
            score += 20
        
        # Quality scores
        avg_quality = (self.content_quality_score + other_creator.content_quality_score) / 2
        score += avg_quality * 0.3
        
        return min(100, score)
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get comprehensive profile summary"""
        return {
            'basic_info': {
                'stage_name': self.stage_name,
                'creator_type': self.creator_type.value,
                'career_level': self.career_level.value,
                'verification_status': self.verification_status.value,
                'location': f"{self.location_city}, {self.location_country}" if self.location_city else self.location_country
            },
            'audience_metrics': {
                'total_followers': self.total_followers,
                'audience_size': self.audience_size.value,
                'engagement_rate': self.avg_engagement_rate,
                'monthly_listeners': self.monthly_listeners
            },
            'performance_metrics': {
                'content_count': self.content_count,
                'total_views': self.total_views,
                'quality_score': self.content_quality_score,
                'professionalism_score': self.professionalism_score
            },
            'collaboration_info': {
                'collaboration_style': self.collaboration_style.value,
                'open_to_collaborations': self.open_to_collaborations,
                'genres': self.primary_genres or [],
                'collaboration_rate': float(self.collaboration_rate) if self.collaboration_rate else None
            },
            'platform_presence': {
                'primary_platforms': self.primary_platforms or [],
                'verified_platforms': self.verified_platforms or [],
                'monetized_platforms': self.monetized_platforms or []
            }
        }
    
    def is_eligible_for_verification(self) -> bool:
        """Check if profile is eligible for verification"""
        return (
            self.profile_completeness >= 80 and
            self.total_followers >= 1000 and
            self.content_count >= 10 and
            self.content_quality_score >= 70 and
            self.is_active
        )
    
    def update_activity_score(self) -> None:
        """Update activity score based on recent activity"""
        now = datetime.now(timezone.utc)
        
        # Days since last activity
        if self.last_active_at:
            days_inactive = (now - self.last_active_at).days
            activity_score = max(0, 100 - days_inactive * 2)
        else:
            activity_score = 0
        
        # Content upload frequency bonus
        if self.last_content_upload:
            days_since_upload = (now - self.last_content_upload).days
            if days_since_upload <= 7:
                activity_score += 20
            elif days_since_upload <= 30:
                activity_score += 10
        
        self.activity_score = min(100, activity_score)
        self.updated_at = now
