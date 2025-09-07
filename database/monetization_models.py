"""🗃️ Monetization Database Models - Enterprise Creator Revenue Management
=========================================================================

Enterprise-grade database models for creator monetization, AI revenue optimization,
collaboration revenue sharing, protection revenue recovery, and gamification rewards.

Architecture: Enterprise Production-Ready (Database Level 3)
Module: database/monetization_models.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code contains advanced database schema designs and monetization
algorithms that are the exclusive property of Fahed Mlaiel.
"""

import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from enum import Enum
from uuid import uuid4

try:
    from sqlalchemy import Column, String, DateTime, Float, Boolean, Text, JSON, ForeignKey, DECIMAL, Enum as SQLEnum
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = None


class CreatorType(str, Enum):
    """Creator type classifications for monetization."""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    VIDEO_CREATOR = "video_creator"
    ARTIST = "artist"


class PayoutSchedule(str, Enum):
    """Payout schedule options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"


class OptimizationType(str, Enum):
    """AI optimization types."""
    PRICING = "pricing"
    PLATFORM_SELECTION = "platform_selection"
    TIMING = "timing"
    AUDIENCE_TARGETING = "audience_targeting"
    COLLABORATION_MATCHING = "collaboration_matching"


class ImplementationStatus(str, Enum):
    """Implementation status for AI optimizations."""
    PENDING = "pending"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ContractType(str, Enum):
    """Collaboration contract types."""
    REVENUE_SHARING = "revenue_sharing"
    FIXED_PAYMENT = "fixed_payment"
    HYBRID = "hybrid"
    MILESTONE_BASED = "milestone_based"


class ContractStatus(str, Enum):
    """Contract status options."""
    DRAFT = "draft"
    PENDING_SIGNATURES = "pending_signatures"
    ACTIVE = "active"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class TaxHandling(str, Enum):
    """Tax handling options."""
    INDIVIDUAL = "individual"
    COLLECTIVE = "collective"
    PLATFORM_MANAGED = "platform_managed"


class RecoveryType(str, Enum):
    """Revenue recovery types."""
    DMCA_SETTLEMENT = "dmca_settlement"
    LEGAL_ACTION = "legal_action"
    PLATFORM_COMPENSATION = "platform_compensation"
    NEGOTIATED_SETTLEMENT = "negotiated_settlement"


class RecoveryStatus(str, Enum):
    """Revenue recovery status."""
    IDENTIFIED = "identified"
    CLAIMED = "claimed"
    NEGOTIATING = "negotiating"
    SETTLED = "settled"
    REJECTED = "rejected"
    LITIGATION = "litigation"


class RewardType(str, Enum):
    """Gamification reward types."""
    CASH_BONUS = "cash_bonus"
    REVENUE_MULTIPLIER = "revenue_multiplier"
    PLATFORM_CREDITS = "platform_credits"
    PREMIUM_FEATURES = "premium_features"
    COLLABORATION_BOOST = "collaboration_boost"


class RedemptionStatus(str, Enum):
    """Reward redemption status."""
    EARNED = "earned"
    PENDING = "pending"
    REDEEMED = "redeemed"
    EXPIRED = "expired"


class OptimizationStatus(str, Enum):
    """SEO optimization status."""
    PLANNED = "planned"
    IMPLEMENTING = "implementing"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"


if SQLALCHEMY_AVAILABLE:
    
    class CreatorMonetizationProfile(Base):
        """Creator monetization profiles table."""
        __tablename__ = "creator_monetization_profiles"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
        creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
        creator_type = Column(SQLEnum(CreatorType), nullable=False, index=True)
        monetization_preferences = Column(JSON, nullable=True)
        revenue_goals = Column(JSON, nullable=True)
        preferred_payment_methods = Column(JSON, nullable=True)
        tax_settings = Column(JSON, nullable=True)
        payout_schedule = Column(SQLEnum(PayoutSchedule), default=PayoutSchedule.MONTHLY)
        minimum_payout_threshold = Column(DECIMAL(10, 2), default=Decimal('10.00'))
        auto_optimization_enabled = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
        
        # Relationships
        ai_optimizations = relationship("AIRevenueOptimization", back_populates="creator_profile")
        gamification_rewards = relationship("GamificationMonetizationReward", back_populates="creator_profile")


    class AIRevenueOptimization(Base):
        """AI revenue optimizations table."""
        __tablename__ = "ai_revenue_optimizations"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
        creator_id = Column(UUID(as_uuid=True), ForeignKey('creator_monetization_profiles.creator_id'), nullable=False)
        content_id = Column(UUID(as_uuid=True), nullable=True)
        optimization_type = Column(SQLEnum(OptimizationType), nullable=False, index=True)
        ai_model_version = Column(String(50), nullable=True)
        optimization_suggestions = Column(JSON, nullable=False)
        predicted_revenue_increase = Column(DECIMAL(5, 2), nullable=True)
        confidence_score = Column(DECIMAL(5, 4), nullable=True, index=True)
        implementation_status = Column(SQLEnum(ImplementationStatus), default=ImplementationStatus.PENDING, index=True)
        actual_revenue_impact = Column(DECIMAL(10, 2), nullable=True)
        implementation_date = Column(DateTime, nullable=True)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)
        
        # Relationships
        creator_profile = relationship("CreatorMonetizationProfile", back_populates="ai_optimizations")


    class CollaborationRevenueContract(Base):
        """Collaboration revenue contracts table."""
        __tablename__ = "collaboration_revenue_contracts"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
        project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
        contract_type = Column(SQLEnum(ContractType), nullable=False)
        participants = Column(JSON, nullable=False)
        revenue_split_rules = Column(JSON, nullable=False)
        payment_schedule = Column(JSON, nullable=True)
        contract_terms = Column(JSON, nullable=True)
        auto_distribution_enabled = Column(Boolean, default=True, index=True)
        tax_handling = Column(SQLEnum(TaxHandling), default=TaxHandling.INDIVIDUAL)
        contract_status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT, index=True)
        total_revenue_distributed = Column(DECIMAL(15, 2), default=Decimal('0.00'))
        created_at = Column(DateTime, default=datetime.datetime.utcnow)
        expires_at = Column(DateTime, nullable=True)


    class ProtectionRevenueRecovery(Base):
        """Protection revenue recovery table."""
        __tablename__ = "protection_revenue_recovery"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
        content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False)
        violation_id = Column(UUID(as_uuid=True), nullable=False)
        recovery_type = Column(SQLEnum(RecoveryType), nullable=False)
        claimed_amount = Column(DECIMAL(15, 2), nullable=True)
        recovered_amount = Column(DECIMAL(15, 2), nullable=True)
        recovery_status = Column(SQLEnum(RecoveryStatus), default=RecoveryStatus.IDENTIFIED, index=True)
        recovery_fees = Column(DECIMAL(15, 2), nullable=True)
        net_recovery = Column(DECIMAL(15, 2), nullable=True)
        recovery_date = Column(DateTime, nullable=True)
        settlement_terms = Column(JSON, nullable=True)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)


    class GamificationMonetizationReward(Base):
        """Gamification monetization rewards table."""
        __tablename__ = "gamification_monetization_rewards"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
        creator_id = Column(UUID(as_uuid=True), ForeignKey('creator_monetization_profiles.creator_id'), nullable=False)
        achievement_type = Column(String(100), nullable=True)
        reward_type = Column(SQLEnum(RewardType), nullable=False, index=True)
        reward_value = Column(DECIMAL(10, 2), nullable=True)
        reward_description = Column(Text, nullable=True)
        eligibility_criteria = Column(JSON, nullable=True)
        redemption_status = Column(SQLEnum(RedemptionStatus), default=RedemptionStatus.EARNED, index=True)
        earned_date = Column(DateTime, nullable=True)
        redeemed_date = Column(DateTime, nullable=True)
        expiry_date = Column(DateTime, nullable=True)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)
        
        # Relationships
        creator_profile = relationship("CreatorMonetizationProfile", back_populates="gamification_rewards")


    class SEORevenueOptimization(Base):
        """SEO revenue optimization table."""
        __tablename__ = "seo_revenue_optimization"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
        content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False)
        seo_strategy = Column(JSON, nullable=True)
        target_keywords = Column(JSON, nullable=True)
        optimization_goals = Column(JSON, nullable=True)
        predicted_traffic_increase = Column(DECIMAL(8, 2), nullable=True)
        predicted_revenue_increase = Column(DECIMAL(10, 2), nullable=True)
        actual_traffic_impact = Column(DECIMAL(8, 2), nullable=True)
        actual_revenue_impact = Column(DECIMAL(10, 2), nullable=True)
        optimization_roi = Column(DECIMAL(8, 4), nullable=True, index=True)
        optimization_status = Column(SQLEnum(OptimizationStatus), default=OptimizationStatus.PLANNED, index=True)
        implementation_date = Column(DateTime, nullable=True)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)


# Non-SQLAlchemy models for environments without SQLAlchemy
else:
    
    class BaseMonetizationModel:
        """Base model for monetization entities."""
        
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            self.id = str(uuid4())
            self.created_at = datetime.datetime.utcnow()
            self.updated_at = datetime.datetime.utcnow()
        
        def to_dict(self) -> Dict[str, Any]:
            """Convert model to dictionary."""
            result = {}
            for key, value in self.__dict__.items():
                if not key.startswith('_'):
                    if isinstance(value, datetime.datetime):
                        result[key] = value.isoformat()
                    elif isinstance(value, Enum):
                        result[key] = value.value
                    elif isinstance(value, Decimal):
                        result[key] = float(value)
                    else:
                        result[key] = value
            return result


    class CreatorMonetizationProfile(BaseMonetizationModel):
        """Creator monetization profile model."""
        
        def __init__(self, creator_id: str, creator_type: CreatorType, **kwargs):
            super().__init__(**kwargs)
            self.creator_id = creator_id
            self.creator_type = creator_type
            self.monetization_preferences = kwargs.get('monetization_preferences', {})
            self.revenue_goals = kwargs.get('revenue_goals', {})
            self.preferred_payment_methods = kwargs.get('preferred_payment_methods', [])
            self.tax_settings = kwargs.get('tax_settings', {})
            self.payout_schedule = kwargs.get('payout_schedule', PayoutSchedule.MONTHLY)
            self.minimum_payout_threshold = kwargs.get('minimum_payout_threshold', Decimal('10.00'))
            self.auto_optimization_enabled = kwargs.get('auto_optimization_enabled', True)


    class AIRevenueOptimization(BaseMonetizationModel):
        """AI revenue optimization model."""
        
        def __init__(self, creator_id: str, optimization_type: OptimizationType, 
                     optimization_suggestions: Dict[str, Any], **kwargs):
            super().__init__(**kwargs)
            self.creator_id = creator_id
            self.optimization_type = optimization_type
            self.optimization_suggestions = optimization_suggestions
            self.content_id = kwargs.get('content_id')
            self.ai_model_version = kwargs.get('ai_model_version')
            self.predicted_revenue_increase = kwargs.get('predicted_revenue_increase')
            self.confidence_score = kwargs.get('confidence_score')
            self.implementation_status = kwargs.get('implementation_status', ImplementationStatus.PENDING)
            self.actual_revenue_impact = kwargs.get('actual_revenue_impact')
            self.implementation_date = kwargs.get('implementation_date')


    class CollaborationRevenueContract(BaseMonetizationModel):
        """Collaboration revenue contract model."""
        
        def __init__(self, project_id: str, contract_type: ContractType, 
                     participants: Dict[str, Any], revenue_split_rules: Dict[str, Any], **kwargs):
            super().__init__(**kwargs)
            self.project_id = project_id
            self.contract_type = contract_type
            self.participants = participants
            self.revenue_split_rules = revenue_split_rules
            self.payment_schedule = kwargs.get('payment_schedule', {})
            self.contract_terms = kwargs.get('contract_terms', {})
            self.auto_distribution_enabled = kwargs.get('auto_distribution_enabled', True)
            self.tax_handling = kwargs.get('tax_handling', TaxHandling.INDIVIDUAL)
            self.contract_status = kwargs.get('contract_status', ContractStatus.DRAFT)
            self.total_revenue_distributed = kwargs.get('total_revenue_distributed', Decimal('0.00'))
            self.expires_at = kwargs.get('expires_at')


    class ProtectionRevenueRecovery(BaseMonetizationModel):
        """Protection revenue recovery model."""
        
        def __init__(self, content_id: str, violation_id: str, recovery_type: RecoveryType, **kwargs):
            super().__init__(**kwargs)
            self.content_id = content_id
            self.violation_id = violation_id
            self.recovery_type = recovery_type
            self.claimed_amount = kwargs.get('claimed_amount')
            self.recovered_amount = kwargs.get('recovered_amount')
            self.recovery_status = kwargs.get('recovery_status', RecoveryStatus.IDENTIFIED)
            self.recovery_fees = kwargs.get('recovery_fees')
            self.net_recovery = kwargs.get('net_recovery')
            self.recovery_date = kwargs.get('recovery_date')
            self.settlement_terms = kwargs.get('settlement_terms', {})


    class GamificationMonetizationReward(BaseMonetizationModel):
        """Gamification monetization reward model."""
        
        def __init__(self, creator_id: str, reward_type: RewardType, **kwargs):
            super().__init__(**kwargs)
            self.creator_id = creator_id
            self.reward_type = reward_type
            self.achievement_type = kwargs.get('achievement_type')
            self.reward_value = kwargs.get('reward_value')
            self.reward_description = kwargs.get('reward_description')
            self.eligibility_criteria = kwargs.get('eligibility_criteria', {})
            self.redemption_status = kwargs.get('redemption_status', RedemptionStatus.EARNED)
            self.earned_date = kwargs.get('earned_date')
            self.redeemed_date = kwargs.get('redeemed_date')
            self.expiry_date = kwargs.get('expiry_date')


    class SEORevenueOptimization(BaseMonetizationModel):
        """SEO revenue optimization model."""
        
        def __init__(self, content_id: str, **kwargs):
            super().__init__(**kwargs)
            self.content_id = content_id
            self.seo_strategy = kwargs.get('seo_strategy', {})
            self.target_keywords = kwargs.get('target_keywords', [])
            self.optimization_goals = kwargs.get('optimization_goals', {})
            self.predicted_traffic_increase = kwargs.get('predicted_traffic_increase')
            self.predicted_revenue_increase = kwargs.get('predicted_revenue_increase')
            self.actual_traffic_impact = kwargs.get('actual_traffic_impact')
            self.actual_revenue_impact = kwargs.get('actual_revenue_impact')
            self.optimization_roi = kwargs.get('optimization_roi')
            self.optimization_status = kwargs.get('optimization_status', OptimizationStatus.PLANNED)
            self.implementation_date = kwargs.get('implementation_date')


# Export all models
__all__ = [
    'CreatorType', 'PayoutSchedule', 'OptimizationType', 'ImplementationStatus',
    'ContractType', 'ContractStatus', 'TaxHandling', 'RecoveryType', 'RecoveryStatus',
    'RewardType', 'RedemptionStatus', 'OptimizationStatus',
    'CreatorMonetizationProfile', 'AIRevenueOptimization', 'CollaborationRevenueContract',
    'ProtectionRevenueRecovery', 'GamificationMonetizationReward', 'SEORevenueOptimization'
]