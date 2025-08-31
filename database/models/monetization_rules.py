"""Monetization Rules Database Model

Enterprise-grade SQLAlchemy model for managing monetization rules, pricing strategies,
and automated revenue optimization across multiple platforms and content types.

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
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class RuleType(Enum):
    """Monetization rule types"""    PRICING = "pricing"
    REVENUE_SHARE = "revenue_share"
    ROYALTY = "royalty"
    LICENSING = "licensing"
    SUBSCRIPTION = "subscription"
    ADVERTISING = "advertising"
    COMMISSION = "commission"
    TIER_BASED = "tier_based"
    VOLUME_BASED = "volume_based"
    TIME_BASED = "time_based"
    GEOGRAPHIC = "geographic"
    DEMOGRAPHIC = "demographic"
    PLATFORM_SPECIFIC = "platform_specific"
    CONTENT_TYPE = "content_type"
    QUALITY_BASED = "quality_based"
    PERFORMANCE_BASED = "performance_based"
    COLLABORATION = "collaboration"
    BUNDLING = "bundling"
    DYNAMIC_PRICING = "dynamic_pricing"
    PROMOTIONAL = "promotional"


class TriggerType(Enum):
    """Rule trigger types"""    ALWAYS = "always"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_PUBLISH = "content_publish"
    PLAY_COUNT = "play_count"
    DOWNLOAD = "download"
    VIEW_COUNT = "view_count"
    TIME_PERIOD = "time_period"
    PLATFORM_SYNC = "platform_sync"
    REVENUE_THRESHOLD = "revenue_threshold"
    USER_ACTION = "user_action"
    COLLABORATION_REQUEST = "collaboration_request"
    LICENSE_REQUEST = "license_request"
    GEOGRAPHIC_ACCESS = "geographic_access"
    DEVICE_TYPE = "device_type"
    SUBSCRIPTION_TIER = "subscription_tier"
    ENGAGEMENT_RATE = "engagement_rate"
    QUALITY_SCORE = "quality_score"
    TREND_DETECTION = "trend_detection"
    SEASONAL = "seasonal"
    COMPETITIVE = "competitive"


class ActionType(Enum):
    """Rule action types"""    SET_PRICE = "set_price"
    ADJUST_PRICE = "adjust_price"
    APPLY_DISCOUNT = "apply_discount"
    APPLY_MARKUP = "apply_markup"
    SET_ROYALTY_RATE = "set_royalty_rate"
    ENABLE_MONETIZATION = "enable_monetization"
    DISABLE_MONETIZATION = "disable_monetization"
    GRANT_LICENSE = "grant_license"
    REVOKE_LICENSE = "revoke_license"
    SPLIT_REVENUE = "split_revenue"
    APPLY_FEE = "apply_fee"
    WAIVE_FEE = "waive_fee"
    CHANGE_TIER = "change_tier"
    APPLY_BONUS = "apply_bonus"
    SEND_NOTIFICATION = "send_notification"
    BLOCK_ACCESS = "block_access"
    ALLOW_ACCESS = "allow_access"
    REDIRECT_REVENUE = "redirect_revenue"
    OPTIMIZE_PRICING = "optimize_pricing"
    A_B_TEST = "a_b_test"


class RuleStatus(Enum):
    """Rule status enumeration"""    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TESTING = "testing"
    ARCHIVED = "archived"


class Priority(Enum):
    """Rule priority levels"""    CRITICAL = "critical"      # Priority 1
    HIGH = "high"              # Priority 2
    MEDIUM = "medium"          # Priority 3
    LOW = "low"                # Priority 4
    BACKGROUND = "background"  # Priority 5


class MonetizationRule(Base):
    """    Enterprise Monetization Rule Model
    
    Comprehensive rule engine for automated monetization decisions, pricing optimization,
    and revenue management with advanced AI-powered strategies.
    """    __tablename__ = "monetization_rules"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Rule identification and metadata
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text, nullable=True)
    rule_code = Column(String(100), unique=True, nullable=False, index=True)
    rule_version = Column(String(20), default="1.0")
    rule_category = Column(String(100), nullable=True)
    rule_tags = Column(ARRAY(String), nullable=True, index=True)
    
    # Rule classification
    rule_type = Column(SQLEnum(RuleType), nullable=False, index=True)
    trigger_type = Column(SQLEnum(TriggerType), nullable=False, index=True)
    action_type = Column(SQLEnum(ActionType), nullable=False, index=True)
    rule_status = Column(SQLEnum(RuleStatus), default=RuleStatus.DRAFT, index=True)
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM, index=True)
    
    # Scope and applicability
    content_types = Column(ARRAY(String), nullable=True)  # audio, video, image, etc.
    platforms = Column(ARRAY(String), nullable=True)      # spotify, youtube, etc.
    territories = Column(ARRAY(String), nullable=True)    # countries/regions
    user_tiers = Column(ARRAY(String), nullable=True)     # free, premium, pro
    languages = Column(ARRAY(String), nullable=True)      # language codes
    genres = Column(ARRAY(String), nullable=True)         # music genres
    
    # Conditions and triggers
    trigger_conditions = Column(JSON, nullable=False)
    condition_logic = Column(String(20), default="AND")  # AND, OR, CUSTOM
    custom_logic_expression = Column(Text, nullable=True)
    threshold_values = Column(JSON, nullable=True)
    comparison_operators = Column(JSON, nullable=True)
    
    # Actions and effects
    action_parameters = Column(JSON, nullable=False)
    action_values = Column(JSON, nullable=True)
    conditional_actions = Column(JSON, nullable=True)
    fallback_actions = Column(JSON, nullable=True)
    action_limits = Column(JSON, nullable=True)
    
    # Financial parameters
    base_price = Column(Numeric(15, 4), nullable=True)
    min_price = Column(Numeric(15, 4), nullable=True)
    max_price = Column(Numeric(15, 4), nullable=True)
    price_adjustment_factor = Column(Float, nullable=True)
    discount_percentage = Column(Float, nullable=True)
    markup_percentage = Column(Float, nullable=True)
    royalty_percentage = Column(Float, nullable=True)
    commission_percentage = Column(Float, nullable=True)
    currency = Column(String(3), default="EUR")
    
    # Revenue sharing and splits
    revenue_splits = Column(JSON, nullable=True)
    collaborator_shares = Column(JSON, nullable=True)
    platform_shares = Column(JSON, nullable=True)
    minimum_payout = Column(Numeric(10, 2), nullable=True)
    payment_frequency = Column(String(50), nullable=True)
    
    # Time-based parameters
    effective_from = Column(DateTime(timezone=True), nullable=True)
    effective_until = Column(DateTime(timezone=True), nullable=True)
    time_restrictions = Column(JSON, nullable=True)  # hours, days, seasons
    timezone = Column(String(50), default="UTC")
    
    # Frequency and limits
    max_applications = Column(Integer, nullable=True)  # Max times rule can be applied
    applications_count = Column(Integer, default=0)
    cooldown_period = Column(Integer, nullable=True)  # Seconds between applications
    rate_limit = Column(JSON, nullable=True)
    usage_limits = Column(JSON, nullable=True)
    
    # Performance tracking
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    total_revenue_generated = Column(Numeric(15, 4), default=0.0)
    total_revenue_saved = Column(Numeric(15, 4), default=0.0)
    average_execution_time = Column(Float, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    
    # AI and machine learning
    ai_enabled = Column(Boolean, default=False)
    ml_model_name = Column(String(255), nullable=True)
    ml_model_version = Column(String(50), nullable=True)
    ai_confidence_threshold = Column(Float, default=0.8)
    learning_enabled = Column(Boolean, default=False)
    optimization_target = Column(String(100), nullable=True)  # revenue, engagement, etc.
    
    # A/B testing and experimentation
    ab_test_enabled = Column(Boolean, default=False)
    ab_test_groups = Column(JSON, nullable=True)
    ab_test_split_percentage = Column(Float, nullable=True)
    control_group_percentage = Column(Float, default=20.0)
    statistical_significance = Column(Float, nullable=True)
    
    # Dependencies and relationships
    parent_rule_id = Column(UUID(as_uuid=True), ForeignKey('monetization_rules.id'), nullable=True)
    dependent_rule_ids = Column(ARRAY(UUID), nullable=True)
    conflicting_rule_ids = Column(ARRAY(UUID), nullable=True)
    rule_hierarchy_level = Column(Integer, default=1)
    execution_order = Column(Integer, default=1000)
    
    # Approval and governance
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_workflow = Column(JSON, nullable=True)
    compliance_rules = Column(JSON, nullable=True)
    risk_assessment = Column(JSON, nullable=True)
    
    # Notification and alerting
    notification_settings = Column(JSON, nullable=True)
    alert_thresholds = Column(JSON, nullable=True)
    escalation_rules = Column(JSON, nullable=True)
    stakeholder_notifications = Column(JSON, nullable=True)
    
    # Monitoring and logging
    monitoring_enabled = Column(Boolean, default=True)
    detailed_logging = Column(Boolean, default=False)
    audit_trail_enabled = Column(Boolean, default=True)
    performance_monitoring = Column(JSON, nullable=True)
    error_handling = Column(JSON, nullable=True)
    
    # Integration and automation
    api_endpoints = Column(JSON, nullable=True)
    webhook_urls = Column(JSON, nullable=True)
    external_integrations = Column(JSON, nullable=True)
    automation_level = Column(String(50), default="manual")  # manual, semi, full
    
    # Market and competitive analysis
    market_conditions = Column(JSON, nullable=True)
    competitive_rules = Column(JSON, nullable=True)
    price_sensitivity_analysis = Column(JSON, nullable=True)
    demand_elasticity = Column(Float, nullable=True)
    market_position = Column(String(50), nullable=True)
    
    # Personalization and segmentation
    user_segmentation = Column(JSON, nullable=True)
    personalization_enabled = Column(Boolean, default=False)
    behavioral_triggers = Column(JSON, nullable=True)
    demographic_factors = Column(JSON, nullable=True)
    psychographic_factors = Column(JSON, nullable=True)
    
    # Quality and content factors
    quality_thresholds = Column(JSON, nullable=True)
    content_popularity_factors = Column(JSON, nullable=True)
    engagement_metrics = Column(JSON, nullable=True)
    virality_indicators = Column(JSON, nullable=True)
    trend_analysis = Column(JSON, nullable=True)
    
    # Execution history and analytics
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    next_execution_at = Column(DateTime(timezone=True), nullable=True)
    execution_history = Column(JSON, nullable=True)
    performance_analytics = Column(JSON, nullable=True)
    optimization_suggestions = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    activated_at = Column(DateTime(timezone=True), nullable=True)
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
    last_modified_by = Column(String(255), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=False)
    is_global = Column(Boolean, default=False)  # Applies to all content
    is_automatic = Column(Boolean, default=False)
    is_experimental = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    requires_maintenance = Column(Boolean, default=False)
    
    # Relationships
    parent_rule = relationship("MonetizationRule", remote_side=[id], foreign_keys=[parent_rule_id])
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_monetization_rules_user_status', 'user_id', 'rule_status'),
        Index('idx_monetization_rules_type_trigger', 'rule_type', 'trigger_type'),
        Index('idx_monetization_rules_priority_active', 'priority', 'is_active'),
        Index('idx_monetization_rules_effective_period', 'effective_from', 'effective_until'),
        Index('idx_monetization_rules_content_platforms', 'content_types', 'platforms'),
        Index('idx_monetization_rules_execution_order', 'execution_order', 'rule_hierarchy_level'),
        Index('idx_monetization_rules_performance', 'success_count', 'total_revenue_generated'),
        Index('idx_monetization_rules_ai_enabled', 'ai_enabled', 'ml_model_name'),
        Index('idx_monetization_rules_ab_test', 'ab_test_enabled', 'statistical_significance'),
        Index('idx_monetization_rules_approval', 'requires_approval', 'approved_at'),
        Index('idx_monetization_rules_tags', 'rule_tags'),
        Index('idx_monetization_rules_code', 'rule_code'),
        Index('idx_monetization_rules_last_executed', 'last_executed_at', 'next_execution_at'),
    )
    
    def __repr__(self):
        return f"<MonetizationRule(id={self.id}, name='{self.rule_name}', type={self.rule_type.value}, status={self.rule_status.value})>"
    
    def to_dict(self, include_sensitive: bool = False, include_analytics: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""        base_dict = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "rule_name": self.rule_name,
            "rule_description": self.rule_description,
            "rule_code": self.rule_code,
            "rule_version": self.rule_version,
            "rule_category": self.rule_category,
            "rule_tags": self.rule_tags,
            "rule_type": self.rule_type.value if self.rule_type else None,
            "trigger_type": self.trigger_type.value if self.trigger_type else None,
            "action_type": self.action_type.value if self.action_type else None,
            "rule_status": self.rule_status.value if self.rule_status else None,
            "priority": self.priority.value if self.priority else None,
            "content_types": self.content_types,
            "platforms": self.platforms,
            "territories": self.territories,
            "user_tiers": self.user_tiers,
            "languages": self.languages,
            "genres": self.genres,
            "trigger_conditions": self.trigger_conditions,
            "condition_logic": self.condition_logic,
            "threshold_values": self.threshold_values,
            "action_parameters": self.action_parameters,
            "action_values": self.action_values,
            "base_price": float(self.base_price) if self.base_price else None,
            "min_price": float(self.min_price) if self.min_price else None,
            "max_price": float(self.max_price) if self.max_price else None,
            "price_adjustment_factor": self.price_adjustment_factor,
            "discount_percentage": self.discount_percentage,
            "markup_percentage": self.markup_percentage,
            "royalty_percentage": self.royalty_percentage,
            "commission_percentage": self.commission_percentage,
            "currency": self.currency,
            "revenue_splits": self.revenue_splits,
            "collaborator_shares": self.collaborator_shares,
            "platform_shares": self.platform_shares,
            "minimum_payout": float(self.minimum_payout) if self.minimum_payout else None,
            "payment_frequency": self.payment_frequency,
            "effective_from": self.effective_from.isoformat() if self.effective_from else None,
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
            "time_restrictions": self.time_restrictions,
            "timezone": self.timezone,
            "max_applications": self.max_applications,
            "applications_count": self.applications_count,
            "cooldown_period": self.cooldown_period,
            "rate_limit": self.rate_limit,
            "ai_enabled": self.ai_enabled,
            "ml_model_name": self.ml_model_name,
            "ml_model_version": self.ml_model_version,
            "ai_confidence_threshold": self.ai_confidence_threshold,
            "learning_enabled": self.learning_enabled,
            "optimization_target": self.optimization_target,
            "ab_test_enabled": self.ab_test_enabled,
            "ab_test_groups": self.ab_test_groups,
            "control_group_percentage": self.control_group_percentage,
            "parent_rule_id": str(self.parent_rule_id) if self.parent_rule_id else None,
            "dependent_rule_ids": [str(id) for id in self.dependent_rule_ids] if self.dependent_rule_ids else [],
            "rule_hierarchy_level": self.rule_hierarchy_level,
            "execution_order": self.execution_order,
            "requires_approval": self.requires_approval,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "monitoring_enabled": self.monitoring_enabled,
            "detailed_logging": self.detailed_logging,
            "automation_level": self.automation_level,
            "personalization_enabled": self.personalization_enabled,
            "last_executed_at": self.last_executed_at.isoformat() if self.last_executed_at else None,
            "next_execution_at": self.next_execution_at.isoformat() if self.next_execution_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "last_modified_by": self.last_modified_by,
            "is_active": self.is_active,
            "is_global": self.is_global,
            "is_automatic": self.is_automatic,
            "is_experimental": self.is_experimental,
            "is_deprecated": self.is_deprecated,
            "requires_maintenance": self.requires_maintenance
        }
        
        if include_analytics:
            base_dict.update({
                "success_count": self.success_count,
                "failure_count": self.failure_count,
                "total_revenue_generated": float(self.total_revenue_generated),
                "total_revenue_saved": float(self.total_revenue_saved),
                "average_execution_time": self.average_execution_time,
                "performance_metrics": self.performance_metrics,
                "statistical_significance": self.statistical_significance,
                "performance_analytics": self.performance_analytics,
                "optimization_suggestions": self.optimization_suggestions
            })
        
        if include_sensitive:
            base_dict.update({
                "custom_logic_expression": self.custom_logic_expression,
                "conditional_actions": self.conditional_actions,
                "fallback_actions": self.fallback_actions,
                "approval_workflow": self.approval_workflow,
                "risk_assessment": self.risk_assessment,
                "api_endpoints": self.api_endpoints,
                "webhook_urls": self.webhook_urls,
                "execution_history": self.execution_history
            })
        
        return base_dict
    
    def is_effective(self) -> bool:
        """Check if rule is currently effective"""        now = datetime.now(timezone.utc)
        return (
            self.rule_status == RuleStatus.ACTIVE and
            self.is_active and
            (not self.effective_from or self.effective_from <= now) and
            (not self.effective_until or self.effective_until > now) and
            (not self.max_applications or self.applications_count < self.max_applications)
        )
    
    def can_execute(self, context: Dict[str, Any] = None) -> bool:
        """Check if rule can be executed given current context"""        if not self.is_effective():
            return False
        
        # Check cooldown period
        if self.cooldown_period and self.last_executed_at:
            cooldown_end = self.last_executed_at + timedelta(seconds=self.cooldown_period)
            if datetime.now(timezone.utc) < cooldown_end:
                return False
        
        # Check time restrictions
        if self.time_restrictions and context:
            # Implementation would check time-based restrictions
            pass
        
        # Check rate limits
        if self.rate_limit and context:
            # Implementation would check rate limiting
            pass
        
        return True
    
    def calculate_roi(self) -> float:
        """Calculate return on investment for this rule"""        if self.total_revenue_generated <= 0:
            return 0.0
        
        # Simple ROI calculation - can be enhanced with cost factors
        total_value = float(self.total_revenue_generated + self.total_revenue_saved)
        execution_cost = (self.success_count + self.failure_count) * 0.01  # Estimated cost per execution
        
        if execution_cost == 0:
            return float('inf') if total_value > 0 else 0.0
        
        return ((total_value - execution_cost) / execution_cost) * 100
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""        total_executions = self.success_count + self.failure_count
        if total_executions == 0:
            return 0.0
        return (self.success_count / total_executions) * 100
    
    def should_optimize(self) -> bool:
        """Determine if rule should be optimized"""        return (
            self.ai_enabled and
            self.learning_enabled and
            self.success_count >= 10 and  # Minimum data points
            self.get_success_rate() < 80.0  # Success rate threshold
        )
    
    def get_priority_score(self) -> int:
        """Get numeric priority score for sorting"""        priority_scores = {
            Priority.CRITICAL: 1,
            Priority.HIGH: 2,
            Priority.MEDIUM: 3,
            Priority.LOW: 4,
            Priority.BACKGROUND: 5
        }
        return priority_scores.get(self.priority, 3)
    
    @classmethod
    def create_rule(cls, rule_data: Dict[str, Any], user_id: str) -> 'MonetizationRule':
        """Create MonetizationRule from rule configuration data"""        # Generate unique rule code
        rule_code = f"MR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        return cls(
            user_id=user_id,
            rule_name=rule_data.get('rule_name'),
            rule_description=rule_data.get('rule_description'),
            rule_code=rule_code,
            rule_category=rule_data.get('rule_category'),
            rule_tags=rule_data.get('rule_tags', []),
            rule_type=RuleType(rule_data.get('rule_type', 'pricing')),
            trigger_type=TriggerType(rule_data.get('trigger_type', 'always')),
            action_type=ActionType(rule_data.get('action_type', 'set_price')),
            priority=Priority(rule_data.get('priority', 'medium')),
            content_types=rule_data.get('content_types', []),
            platforms=rule_data.get('platforms', []),
            territories=rule_data.get('territories', []),
            trigger_conditions=rule_data.get('trigger_conditions', {}),
            action_parameters=rule_data.get('action_parameters', {}),
            base_price=Decimal(str(rule_data.get('base_price', 0.0))),
            currency=rule_data.get('currency', 'EUR'),
            effective_from=rule_data.get('effective_from'),
            effective_until=rule_data.get('effective_until'),
            ai_enabled=rule_data.get('ai_enabled', False),
            personalization_enabled=rule_data.get('personalization_enabled', False),
            monitoring_enabled=rule_data.get('monitoring_enabled', True),
            requires_approval=rule_data.get('requires_approval', True)
        )
