"""
Intelligent Matching Database Model

Ultra-industrial SQLAlchemy model for AI-powered intelligent matching between creators,
collaboration opportunities, brand partnerships, and cross-format content synergies.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted to the full extent 
of international law.

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
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Union

Base = declarative_base()


class MatchingType(Enum):
    """Types of intelligent matching"""
    CREATOR_COLLABORATION = "creator_collaboration"
    BRAND_PARTNERSHIP = "brand_partnership"
    CONTENT_SYNERGY = "content_synergy"
    CROSS_FORMAT_FUSION = "cross_format_fusion"
    AUDIENCE_CROSSOVER = "audience_crossover"
    SKILL_COMPLEMENT = "skill_complement"
    GENRE_FUSION = "genre_fusion"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    REVENUE_OPPORTUNITY = "revenue_opportunity"
    LEARNING_PARTNERSHIP = "learning_partnership"
    MENTOR_MENTEE = "mentor_mentee"
    PROJECT_COLLABORATION = "project_collaboration"
    TOUR_PARTNERSHIP = "tour_partnership"
    REMIX_COLLABORATION = "remix_collaboration"
    MULTI_LANGUAGE = "multi_language"


class MatchingAlgorithm(Enum):
    """AI algorithms used for matching"""
    NEURAL_SIMILARITY = "neural_similarity"
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_EMBEDDING = "content_embedding"
    GRAPH_NEURAL_NETWORK = "graph_neural_network"
    TRANSFORMER_BASED = "transformer_based"
    DEEP_LEARNING_FUSION = "deep_learning_fusion"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    ENSEMBLE_METHODS = "ensemble_methods"
    QUANTUM_MATCHING = "quantum_matching"
    HYBRID_AI = "hybrid_ai"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    PREDICTIVE_MODELING = "predictive_modeling"
    GENETIC_ALGORITHM = "genetic_algorithm"


class MatchingStatus(Enum):
    """Status of matching suggestions"""
    PENDING = "pending"
    ACTIVE = "active"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    NEGOTIATING = "negotiating"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    ON_HOLD = "on_hold"
    UNDER_REVIEW = "under_review"
    SUSPENDED = "suspended"


class ConfidenceLevel(Enum):
    """AI confidence in matching quality"""
    VERY_LOW = "very_low"      # 0-20%
    LOW = "low"                # 20-40%
    MODERATE = "moderate"      # 40-60%
    HIGH = "high"              # 60-80%
    VERY_HIGH = "very_high"    # 80-95%
    PERFECT = "perfect"        # 95-100%


class SynergyType(Enum):
    """Types of content/creator synergies"""
    COMPLEMENTARY_SKILLS = "complementary_skills"
    OVERLAPPING_AUDIENCE = "overlapping_audience"
    GENRE_CROSSOVER = "genre_crossover"
    PLATFORM_STRENGTH = "platform_strength"
    GEOGRAPHIC_EXPANSION = "geographic_expansion"
    LANGUAGE_BRIDGE = "language_bridge"
    DEMOGRAPHIC_REACH = "demographic_reach"
    TECHNICAL_EXPERTISE = "technical_expertise"
    CREATIVE_CHEMISTRY = "creative_chemistry"
    BUSINESS_SYNERGY = "business_synergy"
    BRAND_ALIGNMENT = "brand_alignment"
    CULTURAL_FUSION = "cultural_fusion"
    SEASONAL_TIMING = "seasonal_timing"
    TRENDING_OPPORTUNITY = "trending_opportunity"


class CollaborationType(Enum):
    """Types of collaboration opportunities"""
    SINGLE_TRACK = "single_track"
    EP_COLLABORATION = "ep_collaboration"
    ALBUM_PROJECT = "album_project"
    LIVE_PERFORMANCE = "live_performance"
    STREAMING_SERIES = "streaming_series"
    CONTENT_EXCHANGE = "content_exchange"
    REMIX_PROJECT = "remix_project"
    COVER_COLLABORATION = "cover_collaboration"
    ORIGINAL_COMPOSITION = "original_composition"
    CROSS_PLATFORM_CAMPAIGN = "cross_platform_campaign"
    BRAND_CAMPAIGN = "brand_campaign"
    EDUCATIONAL_CONTENT = "educational_content"
    CHARITY_PROJECT = "charity_project"
    COMPETITION_ENTRY = "competition_entry"
    FESTIVAL_APPEARANCE = "festival_appearance"


class IntelligentMatching(Base):
    """
    Ultra-Industrial Intelligent Matching Model
    
    AI-powered matching system for creator collaborations, brand partnerships,
    and multi-format content synergies with advanced predictive analytics.
    """
    __tablename__ = "intelligent_matching"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matching_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Matching participants
    primary_creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    secondary_creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    brand_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # For brand partnerships
    
    # Matching classification
    matching_type = Column(SQLEnum(MatchingType), nullable=False, index=True)
    collaboration_type = Column(SQLEnum(CollaborationType), nullable=True, index=True)
    algorithm_used = Column(SQLEnum(MatchingAlgorithm), nullable=False, index=True)
    
    # AI analysis results
    matching_score = Column(Float, nullable=False, index=True)  # 0.0 - 1.0
    confidence_level = Column(SQLEnum(ConfidenceLevel), nullable=False, index=True)
    synergy_types = Column(ARRAY(SQLEnum(SynergyType)), nullable=True)
    success_probability = Column(Float, nullable=True)  # Predicted success rate
    roi_prediction = Column(Float, nullable=True)  # Predicted ROI
    
    # Matching criteria and weights
    criteria_weights = Column(JSONB, nullable=True)
    matching_factors = Column(JSONB, nullable=True)
    similarity_metrics = Column(JSONB, nullable=True)
    compatibility_analysis = Column(JSONB, nullable=True)
    
    # Creator compatibility analysis
    skill_compatibility = Column(Float, default=0.0)
    style_compatibility = Column(Float, default=0.0)
    audience_overlap = Column(Float, default=0.0)
    platform_synergy = Column(Float, default=0.0)
    creative_chemistry = Column(Float, default=0.0)
    professional_alignment = Column(Float, default=0.0)
    geographic_compatibility = Column(Float, default=0.0)
    schedule_compatibility = Column(Float, default=0.0)
    
    # Content analysis
    content_similarity = Column(JSONB, nullable=True)
    genre_compatibility = Column(JSONB, nullable=True)
    mood_alignment = Column(JSONB, nullable=True)
    technical_compatibility = Column(JSONB, nullable=True)
    production_quality_match = Column(Float, default=0.0)
    
    # Audience analytics
    audience_demographics = Column(JSONB, nullable=True)
    audience_behavior_patterns = Column(JSONB, nullable=True)
    engagement_predictions = Column(JSONB, nullable=True)
    cross_pollination_potential = Column(Float, default=0.0)
    viral_potential = Column(Float, default=0.0)
    
    # Market opportunity analysis
    market_timing_score = Column(Float, default=0.0)
    trend_alignment = Column(JSONB, nullable=True)
    seasonal_relevance = Column(Float, default=0.0)
    competitive_landscape = Column(JSONB, nullable=True)
    market_demand = Column(Float, default=0.0)
    
    # Financial projections
    estimated_revenue = Column(Numeric(15, 4), nullable=True)
    cost_estimate = Column(Numeric(15, 4), nullable=True)
    profit_margin = Column(Float, nullable=True)
    revenue_sharing_model = Column(JSONB, nullable=True)
    monetization_opportunities = Column(JSONB, nullable=True)
    
    # Platform performance predictions
    spotify_performance = Column(JSONB, nullable=True)
    youtube_performance = Column(JSONB, nullable=True)
    instagram_performance = Column(JSONB, nullable=True)
    tiktok_performance = Column(JSONB, nullable=True)
    platform_optimization = Column(JSONB, nullable=True)
    
    # Collaboration details
    collaboration_scope = Column(Text, nullable=True)
    suggested_approach = Column(Text, nullable=True)
    key_strengths = Column(ARRAY(String), nullable=True)
    potential_challenges = Column(ARRAY(String), nullable=True)
    success_factors = Column(ARRAY(String), nullable=True)
    risk_factors = Column(ARRAY(String), nullable=True)
    
    # Timeline and logistics
    estimated_duration = Column(Integer, nullable=True)  # Duration in days
    suggested_milestones = Column(JSONB, nullable=True)
    resource_requirements = Column(JSONB, nullable=True)
    location_preferences = Column(ARRAY(String), nullable=True)
    timezone_considerations = Column(JSONB, nullable=True)
    
    # Status and progress
    matching_status = Column(SQLEnum(MatchingStatus), default=MatchingStatus.PENDING, index=True)
    response_deadline = Column(DateTime(timezone=True), nullable=True)
    negotiation_terms = Column(JSONB, nullable=True)
    contract_template = Column(Text, nullable=True)
    legal_considerations = Column(JSONB, nullable=True)
    
    # Performance tracking
    view_count = Column(Integer, default=0)
    interest_level = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    feedback_score = Column(Float, nullable=True)
    actual_success_rate = Column(Float, nullable=True)
    actual_roi = Column(Float, nullable=True)
    
    # Machine learning feedback
    user_feedback = Column(JSONB, nullable=True)
    outcome_tracking = Column(JSONB, nullable=True)
    model_performance = Column(JSONB, nullable=True)
    learning_data = Column(JSONB, nullable=True)
    algorithm_version = Column(String(50), nullable=True)
    
    # External integrations
    spotify_data = Column(JSONB, nullable=True)
    social_media_data = Column(JSONB, nullable=True)
    streaming_analytics = Column(JSONB, nullable=True)
    industry_connections = Column(JSONB, nullable=True)
    
    # Advanced analytics
    predictive_models = Column(JSONB, nullable=True)
    sentiment_analysis = Column(JSONB, nullable=True)
    trend_analysis = Column(JSONB, nullable=True)
    competitive_analysis = Column(JSONB, nullable=True)
    market_research = Column(JSONB, nullable=True)
    
    # Timestamps
    algorithm_run_date = Column(DateTime(timezone=True), nullable=False)
    last_updated_analysis = Column(DateTime(timezone=True), nullable=True)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Status flags
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    is_premium_match = Column(Boolean, default=False)
    is_ai_verified = Column(Boolean, default=False)
    is_time_sensitive = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    
    # Privacy and visibility
    is_public = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    visibility_level = Column(String(50), default="mutual")
    privacy_settings = Column(JSONB, nullable=True)
    
    # Relationships
    primary_creator = relationship("User", back_populates="primary_matches", foreign_keys=[primary_creator_id])
    secondary_creator = relationship("User", back_populates="secondary_matches", foreign_keys=[secondary_creator_id])
    collaboration_requests = relationship("CollaborationRequest", back_populates="intelligent_matching", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="intelligent_matching", cascade="all, delete-orphan")
    
    # Ultra-performance indexes
    __table_args__ = (
        Index('idx_intelligent_matching_creators', 'primary_creator_id', 'secondary_creator_id'),
        Index('idx_intelligent_matching_score', 'matching_score', 'confidence_level'),
        Index('idx_intelligent_matching_type_status', 'matching_type', 'matching_status'),
        Index('idx_intelligent_matching_algorithm', 'algorithm_used', 'algorithm_run_date'),
        Index('idx_intelligent_matching_performance', 'success_probability', 'roi_prediction'),
        Index('idx_intelligent_matching_timing', 'response_deadline', 'expiration_date'),
        Index('idx_intelligent_matching_featured', 'is_featured', 'is_premium_match'),
        Index('idx_intelligent_matching_synergy', 'synergy_types', 'collaboration_type'),
        Index('idx_intelligent_matching_audience', 'audience_overlap', 'viral_potential'),
        Index('idx_intelligent_matching_market', 'market_timing_score', 'market_demand'),
    )
    
    def __repr__(self):
        return f"<IntelligentMatching(id={self.id}, type={self.matching_type.value}, score={self.matching_score})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""



        return {
            "id": str(self.id),
            "matching_id": self.matching_id,
            "primary_creator_id": str(self.primary_creator_id),
            "secondary_creator_id": str(self.secondary_creator_id) if self.secondary_creator_id else None,
            "matching_type": self.matching_type.value,
            "collaboration_type": self.collaboration_type.value if self.collaboration_type else None,
            "matching_score": self.matching_score,
            "confidence_level": self.confidence_level.value,
            "success_probability": self.success_probability,
            "roi_prediction": self.roi_prediction,
            "matching_status": self.matching_status.value,
            "is_featured": self.is_featured,
            "is_premium_match": self.is_premium_match,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def is_expired(self) -> bool:
        """Check if matching has expired"""
        if not self.expiration_date:
            return False
        return datetime.now(timezone.utc) > self.expiration_date
    
    def is_response_overdue(self) -> bool:
        """Check if response is overdue"""
        if not self.response_deadline:
            return False
        return datetime.now(timezone.utc) > self.response_deadline
    
    def calculate_overall_compatibility(self) -> float:
        """Calculate overall compatibility score"""
        weights = {
            'skill_compatibility': 0.20,
            'style_compatibility': 0.15,
            'audience_overlap': 0.15,
            'platform_synergy': 0.10,
            'creative_chemistry': 0.15,
            'professional_alignment': 0.10,
            'geographic_compatibility': 0.05,
            'schedule_compatibility': 0.10
        }
        
        total_score = 0.0
        for factor, weight in weights.items():
            score = getattr(self, factor, 0.0)
            total_score += score * weight
        
        return min(total_score, 1.0)
    
    def get_success_indicators(self) -> List[str]:
        """Get list of success indicators"""
        indicators = []
        
        if self.matching_score > 0.8:
            indicators.append("High matching score")
        if self.audience_overlap > 0.7:
            indicators.append("Strong audience overlap")
        if self.creative_chemistry > 0.8:
            indicators.append("Excellent creative chemistry")
        if self.platform_synergy > 0.7:
            indicators.append("Platform synergy potential")
        if self.viral_potential > 0.6:
            indicators.append("High viral potential")
        if self.roi_prediction and self.roi_prediction > 2.0:
            indicators.append("Strong ROI prediction")
        
        return indicators
    
    def get_risk_factors(self) -> List[str]:
        """Get list of risk factors"""
        risks = []
        
        if self.matching_score < 0.5:
            risks.append("Low matching score")
        if self.schedule_compatibility < 0.4:
            risks.append("Schedule conflicts")
        if self.geographic_compatibility < 0.3:
            risks.append("Geographic challenges")
        if self.professional_alignment < 0.5:
            risks.append("Professional misalignment")
        if self.is_response_overdue():
            risks.append("Response overdue")
        if self.is_expired():
            risks.append("Matching expired")
        
        return risks
    
    def update_performance_metrics(self, actual_success: bool, actual_roi: float = None):
        """Update performance metrics based on actual outcomes"""
        self.actual_success_rate = 1.0 if actual_success else 0.0
        if actual_roi is not None:
            self.actual_roi = actual_roi
        
        # Update model performance data for learning
        if not self.model_performance:
            self.model_performance = {}
        
        self.model_performance.update({
            "predicted_success": self.success_probability,
            "actual_success": self.actual_success_rate,
            "predicted_roi": self.roi_prediction,
            "actual_roi": self.actual_roi,
            "prediction_accuracy": abs((self.success_probability or 0.5) - self.actual_success_rate),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
