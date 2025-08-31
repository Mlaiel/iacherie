"""Protection Policies Database Model

Enterprise-grade SQLAlchemy model for managing content protection policies,
rules, enforcement strategies, and automated protection workflows.

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
"""from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class PolicyType(Enum):
    """Protection policy type enumeration"""    COPYRIGHT_PROTECTION = "copyright_protection"
    TRADEMARK_PROTECTION = "trademark_protection"
    CONTENT_MONITORING = "content_monitoring"
    AUTOMATED_TAKEDOWN = "automated_takedown"
    WATERMARK_ENFORCEMENT = "watermark_enforcement"
    FINGERPRINT_MATCHING = "fingerprint_matching"
    PLAGIARISM_DETECTION = "plagiarism_detection"
    BRAND_PROTECTION = "brand_protection"
    REVENUE_PROTECTION = "revenue_protection"
    DMCA_ENFORCEMENT = "dmca_enforcement"
    PRIVACY_PROTECTION = "privacy_protection"
    ANTI_PIRACY = "anti_piracy"
    CONTENT_FILTERING = "content_filtering"
    DUPLICATE_DETECTION = "duplicate_detection"
    LICENSING_ENFORCEMENT = "licensing_enforcement"


class EnforcementLevel(Enum):
    """Enforcement level enumeration"""    MONITORING_ONLY = "monitoring_only"
    WARNING = "warning"
    SOFT_ENFORCEMENT = "soft_enforcement"
    STANDARD_ENFORCEMENT = "standard_enforcement"
    AGGRESSIVE_ENFORCEMENT = "aggressive_enforcement"
    MAXIMUM_ENFORCEMENT = "maximum_enforcement"
    LEGAL_ACTION = "legal_action"


class ActionType(Enum):
    """Automated action types"""    NOTIFY_OWNER = "notify_owner"
    SEND_WARNING = "send_warning"
    SEND_TAKEDOWN_NOTICE = "send_takedown_notice"
    FILE_DMCA = "file_dmca"
    CONTACT_PLATFORM = "contact_platform"
    BLOCK_ACCESS = "block_access"
    DEMONETIZE = "demonetize"
    CLAIM_REVENUE = "claim_revenue"
    LEGAL_NOTICE = "legal_notice"
    CEASE_AND_DESIST = "cease_and_desist"
    ESCALATE_TO_LEGAL = "escalate_to_legal"
    AUTO_STRIKE = "auto_strike"
    WATERMARK_CLAIM = "watermark_claim"
    CONTENT_ID_CLAIM = "content_id_claim"


class TriggerCondition(Enum):
    """Policy trigger conditions"""    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    SIMILARITY_THRESHOLD = "similarity_threshold"
    DURATION_THRESHOLD = "duration_threshold"
    VIEW_THRESHOLD = "view_threshold"
    REVENUE_THRESHOLD = "revenue_threshold"
    GEOGRAPHIC_MATCH = "geographic_match"
    PLATFORM_MATCH = "platform_match"
    TIME_BASED = "time_based"
    USER_REPUTATION = "user_reputation"
    MANUAL_TRIGGER = "manual_trigger"
    AI_DETECTION = "ai_detection"


class PolicyStatus(Enum):
    """Policy status enumeration"""    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class Scope(Enum):
    """Policy scope enumeration"""    GLOBAL = "global"
    PLATFORM_SPECIFIC = "platform_specific"
    GEOGRAPHIC = "geographic"
    CONTENT_TYPE_SPECIFIC = "content_type_specific"
    USER_SPECIFIC = "user_specific"
    TIME_LIMITED = "time_limited"
    CUSTOM = "custom"


class ProtectionPolicy(Base):
    """    Enterprise Protection Policy Model
    
    Comprehensive content protection policy management with automated enforcement,
    customizable rules, and intelligent detection mechanisms.
    """    __tablename__ = 'protection_policies'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # References
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_profile_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=True, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey('user_contents.id'), nullable=True, index=True)
    
    # Policy classification
    policy_type = Column(SQLEnum(PolicyType), nullable=False, index=True)
    enforcement_level = Column(SQLEnum(EnforcementLevel), nullable=False, default=EnforcementLevel.STANDARD_ENFORCEMENT, index=True)
    status = Column(SQLEnum(PolicyStatus), nullable=False, default=PolicyStatus.DRAFT, index=True)
    scope = Column(SQLEnum(Scope), nullable=False, default=Scope.GLOBAL, index=True)
    
    # Policy metadata
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    priority = Column(Integer, nullable=False, default=50)  # 1-100 priority
    
    # Timing information
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    activated_at = Column(DateTime(timezone=True), nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Detection configuration
    similarity_threshold = Column(Float, nullable=False, default=0.85)  # 0-1 threshold
    minimum_duration = Column(Integer, nullable=True)  # Seconds
    minimum_views = Column(Integer, nullable=True)
    minimum_revenue = Column(Float, nullable=True)
    detection_algorithms = Column(ARRAY(String), nullable=True)
    
    # Trigger conditions
    trigger_conditions = Column(JSONB, nullable=False, default=list)
    condition_logic = Column(String(10), nullable=False, default="AND")  # AND/OR
    manual_review_required = Column(Boolean, nullable=False, default=False)
    auto_execution_enabled = Column(Boolean, nullable=False, default=True)
    
    # Target platforms and scope
    target_platforms = Column(ARRAY(String), nullable=True)
    excluded_platforms = Column(ARRAY(String), nullable=True)
    geographic_scope = Column(ARRAY(String), nullable=True)  # Country codes
    content_types = Column(ARRAY(String), nullable=True)
    
    # Automated actions
    automated_actions = Column(JSONB, nullable=False, default=list)
    escalation_actions = Column(JSONB, nullable=True)
    action_sequence = Column(JSONB, nullable=True)  # Ordered list of actions
    cooldown_period = Column(Integer, nullable=True)  # Hours between actions
    
    # Notification settings
    notify_on_detection = Column(Boolean, nullable=False, default=True)
    notify_on_action = Column(Boolean, nullable=False, default=True)
    notification_channels = Column(ARRAY(String), nullable=True)
    custom_notifications = Column(JSONB, nullable=True)
    
    # Legal and compliance
    legal_basis = Column(String(200), nullable=True)
    applicable_laws = Column(ARRAY(String), nullable=True)
    compliance_requirements = Column(JSONB, nullable=True)
    terms_of_service_section = Column(String(100), nullable=True)
    privacy_policy_section = Column(String(100), nullable=True)
    
    # Template and messaging
    warning_template = Column(Text, nullable=True)
    takedown_template = Column(Text, nullable=True)
    dmca_template = Column(Text, nullable=True)
    custom_messages = Column(JSONB, nullable=True)
    response_templates = Column(JSONB, nullable=True)
    
    # Filtering and exceptions
    whitelist_users = Column(ARRAY(String), nullable=True)
    blacklist_users = Column(ARRAY(String), nullable=True)
    whitelisted_content = Column(ARRAY(String), nullable=True)
    exception_rules = Column(JSONB, nullable=True)
    exemption_criteria = Column(JSONB, nullable=True)
    
    # Machine learning configuration
    ai_model_version = Column(String(50), nullable=True)
    training_data_version = Column(String(50), nullable=True)
    confidence_threshold = Column(Float, nullable=False, default=0.8)
    false_positive_learning = Column(Boolean, nullable=False, default=True)
    adaptive_thresholds = Column(Boolean, nullable=False, default=False)
    
    # Performance tracking
    executions_count = Column(Integer, nullable=False, default=0)
    successful_actions = Column(Integer, nullable=False, default=0)
    false_positives = Column(Integer, nullable=False, default=0)
    false_negatives = Column(Integer, nullable=False, default=0)
    accuracy_rate = Column(Float, nullable=False, default=0.0)
    
    # Timing and scheduling
    active_hours = Column(JSONB, nullable=True)  # {day: [start_hour, end_hour]}
    timezone = Column(String(50), nullable=False, default="UTC")
    execution_frequency = Column(String(50), nullable=False, default="real_time")
    batch_processing = Column(Boolean, nullable=False, default=False)
    batch_size = Column(Integer, nullable=True)
    
    # Integration settings
    platform_apis = Column(JSONB, nullable=True)  # Platform-specific API configs
    webhook_urls = Column(ARRAY(String), nullable=True)
    external_services = Column(JSONB, nullable=True)
    monitoring_tools = Column(JSONB, nullable=True)
    
    # Cost and budget
    monthly_budget = Column(Float, nullable=True)
    cost_per_action = Column(Float, nullable=True)
    budget_alerts = Column(Boolean, nullable=False, default=False)
    cost_tracking = Column(Boolean, nullable=False, default=True)
    
    # Reporting and analytics
    generate_reports = Column(Boolean, nullable=False, default=True)
    report_frequency = Column(String(50), nullable=False, default="weekly")
    analytics_enabled = Column(Boolean, nullable=False, default=True)
    trend_analysis = Column(Boolean, nullable=False, default=True)
    performance_monitoring = Column(Boolean, nullable=False, default=True)
    
    # Quality assurance
    review_process = Column(JSONB, nullable=True)
    approval_workflow = Column(JSONB, nullable=True)
    quality_checks = Column(JSONB, nullable=True)
    testing_requirements = Column(JSONB, nullable=True)
    validation_rules = Column(JSONB, nullable=True)
    
    # Advanced features
    dynamic_pricing = Column(Boolean, nullable=False, default=False)
    market_analysis = Column(Boolean, nullable=False, default=False)
    competitor_monitoring = Column(Boolean, nullable=False, default=False)
    trend_prediction = Column(Boolean, nullable=False, default=False)
    sentiment_analysis = Column(Boolean, nullable=False, default=False)
    
    # Administrative fields
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_template = Column(Boolean, nullable=False, default=False)
    is_system_policy = Column(Boolean, nullable=False, default=False)
    requires_approval = Column(Boolean, nullable=False, default=False)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit trail
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    change_log = Column(JSONB, nullable=True)
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_protection_policy_user_type', 'user_id', 'policy_type'),
        Index('idx_protection_policy_status_priority', 'status', 'priority'),
        Index('idx_protection_policy_enforcement_scope', 'enforcement_level', 'scope'),
        Index('idx_protection_policy_active_expires', 'activated_at', 'expires_at'),
        Index('idx_protection_policy_performance', 'accuracy_rate', 'successful_actions'),
        Index('idx_protection_policy_execution', 'last_executed_at', 'executions_count'),
        Index('idx_protection_policy_content', 'content_id', 'is_active'),
        Index('idx_protection_policy_template', 'is_template', 'is_system_policy'),
        Index('idx_protection_policy_approval', 'requires_approval', 'approved_at'),
        Index('idx_protection_policy_similarity', 'similarity_threshold', 'confidence_threshold'),
    )
    
    # Relationships
    creator_profile = relationship("CreatorProfile", back_populates="protection_policies")
    content = relationship("UserContent", back_populates="protection_policies")
    
    def __repr__(self):
        return f"<ProtectionPolicy(id={self.id}, name={self.name}, type={self.policy_type.value})>"
    
    @classmethod
    def create_default_policy(
        cls, 
        user_id: str, 
        policy_type: PolicyType,
        name: str,
        enforcement_level: EnforcementLevel = EnforcementLevel.STANDARD_ENFORCEMENT
    ) -> 'ProtectionPolicy':
        """Create a default protection policy"""        return cls(
            user_id=user_id,
            policy_type=policy_type,
            name=name,
            enforcement_level=enforcement_level,
            policy_id=f"{policy_type.value}_{uuid.uuid4().hex[:8]}",
            created_by="system"
        )
    
    @classmethod
    def create_copyright_policy(cls, user_id: str, content_id: str = None) -> 'ProtectionPolicy':
        """Create a standard copyright protection policy"""        return cls(
            user_id=user_id,
            content_id=content_id,
            policy_type=PolicyType.COPYRIGHT_PROTECTION,
            enforcement_level=EnforcementLevel.STANDARD_ENFORCEMENT,
            name="Standard Copyright Protection",
            description="Automated copyright protection with DMCA takedown notices",
            similarity_threshold=0.85,
            trigger_conditions=[
                {
                    "type": TriggerCondition.SIMILARITY_THRESHOLD.value,
                    "threshold": 0.85,
                    "content_duration_threshold": 30
                }
            ],
            automated_actions=[
                {
                    "type": ActionType.NOTIFY_OWNER.value,
                    "delay_minutes": 0
                },
                {
                    "type": ActionType.SEND_WARNING.value,
                    "delay_minutes": 15
                },
                {
                    "type": ActionType.SEND_TAKEDOWN_NOTICE.value,
                    "delay_minutes": 60
                },
                {
                    "type": ActionType.FILE_DMCA.value,
                    "delay_minutes": 1440  # 24 hours
                }
            ],
            policy_id=f"copyright_{uuid.uuid4().hex[:8]}",
            created_by="system"
        )
    
    def is_triggered(self, detection_data: Dict[str, Any]) -> bool:
        """Check if policy should be triggered based on detection data"""        if not self.is_active or self.status != PolicyStatus.ACTIVE:
            return False
        
        # Check if current time is within active hours
        if not self._is_within_active_hours():
            return False
        
        # Evaluate trigger conditions
        for condition in self.trigger_conditions:
            if not self._evaluate_condition(condition, detection_data):
                if self.condition_logic == "AND":
                    return False
            elif self.condition_logic == "OR":
                return True
        
        return self.condition_logic == "AND"
    
    def _is_within_active_hours(self) -> bool:
        """Check if current time is within active hours"""        if not self.active_hours:
            return True
        
        now = datetime.now(timezone.utc)
        day_name = now.strftime('%A').lower()
        
        if day_name in self.active_hours:
            start_hour, end_hour = self.active_hours[day_name]
            current_hour = now.hour
            return start_hour <= current_hour <= end_hour
        
        return True
    
    def _evaluate_condition(self, condition: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Evaluate a single trigger condition"""        condition_type = condition.get('type')
        
        if condition_type == TriggerCondition.SIMILARITY_THRESHOLD.value:
            similarity = data.get('similarity_score', 0.0)
            threshold = condition.get('threshold', self.similarity_threshold)
            return similarity >= threshold
        
        elif condition_type == TriggerCondition.DURATION_THRESHOLD.value:
            duration = data.get('match_duration', 0)
            threshold = condition.get('threshold', self.minimum_duration or 0)
            return duration >= threshold
        
        elif condition_type == TriggerCondition.VIEW_THRESHOLD.value:
            views = data.get('views', 0)
            threshold = condition.get('threshold', self.minimum_views or 0)
            return views >= threshold
        
        elif condition_type == TriggerCondition.REVENUE_THRESHOLD.value:
            revenue = data.get('estimated_revenue', 0.0)
            threshold = condition.get('threshold', self.minimum_revenue or 0.0)
            return revenue >= threshold
        
        return False
    
    def execute_automated_actions(self, detection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute automated actions based on policy configuration"""        if not self.auto_execution_enabled:
            return []
        
        executed_actions = []
        
        for action in self.automated_actions:
            action_type = action.get('type')
            delay_minutes = action.get('delay_minutes', 0)
            
            # Schedule or execute action
            if delay_minutes > 0:
                execution_time = datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)
                # In production, this would schedule the action
                executed_actions.append({
                    'action_type': action_type,
                    'scheduled_for': execution_time.isoformat(),
                    'status': 'scheduled'
                })
            else:
                # Execute immediately
                result = self._execute_action(action_type, detection_data)
                executed_actions.append(result)
        
        self.executions_count += 1
        self.last_executed_at = datetime.now(timezone.utc)
        
        return executed_actions
    
    def _execute_action(self, action_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action type"""        # This would contain the actual implementation for each action type
        # For now, return a mock result
        return {
            'action_type': action_type,
            'executed_at': datetime.now(timezone.utc).isoformat(),
            'status': 'completed',
            'data': data
        }
    
    def update_performance_metrics(self, success: bool, false_positive: bool = False) -> None:
        """Update performance metrics based on action results"""        if success:
            self.successful_actions += 1
        
        if false_positive:
            self.false_positives += 1
        
        # Calculate accuracy rate
        total_actions = self.successful_actions + self.false_positives
        if total_actions > 0:
            self.accuracy_rate = (self.successful_actions / total_actions) * 100
        
        self.updated_at = datetime.now(timezone.utc)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""        return {
            'execution_metrics': {
                'total_executions': self.executions_count,
                'successful_actions': self.successful_actions,
                'accuracy_rate': self.accuracy_rate,
                'false_positive_rate': (self.false_positives / max(1, self.executions_count)) * 100
            },
            'configuration': {
                'policy_type': self.policy_type.value,
                'enforcement_level': self.enforcement_level.value,
                'similarity_threshold': self.similarity_threshold,
                'auto_execution_enabled': self.auto_execution_enabled
            },
            'timing': {
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'last_executed_at': self.last_executed_at.isoformat() if self.last_executed_at else None,
                'expires_at': self.expires_at.isoformat() if self.expires_at else None
            }
        }
    
    def clone_policy(self, new_name: str, user_id: str = None) -> 'ProtectionPolicy':
        """Clone policy with new configuration"""        new_policy = ProtectionPolicy(
            user_id=user_id or self.user_id,
            policy_type=self.policy_type,
            enforcement_level=self.enforcement_level,
            name=new_name,
            description=f"Cloned from: {self.name}",
            similarity_threshold=self.similarity_threshold,
            trigger_conditions=self.trigger_conditions.copy() if self.trigger_conditions else [],
            automated_actions=self.automated_actions.copy() if self.automated_actions else [],
            target_platforms=self.target_platforms.copy() if self.target_platforms else None,
            policy_id=f"clone_{uuid.uuid4().hex[:8]}",
            created_by="clone_system"
        )
        
        return new_policy
    
    def validate_configuration(self) -> List[str]:
        """Validate policy configuration and return any errors"""        errors = []
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Policy name is required")
        
        if not self.trigger_conditions:
            errors.append("At least one trigger condition is required")
        
        if not self.automated_actions and self.auto_execution_enabled:
            errors.append("Automated actions are required when auto-execution is enabled")
        
        if self.similarity_threshold < 0 or self.similarity_threshold > 1:
            errors.append("Similarity threshold must be between 0 and 1")
        
        if self.expires_at and self.expires_at <= datetime.now(timezone.utc):
            errors.append("Expiration date must be in the future")
        
        return errors
