"""
Partnership Models for IA Influencer Agent
Core data models for partnership management and business relationships

 STRICT COPYRIGHT WARNING 
Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
All rights reserved. Unauthorized use, copying, or reproduction 
of this code, concept, or intellectual property without explicit 
written permission from Fahed Mlaiel is strictly prohibited.

Development Team Specialties:
- Lead Developer + AI Architect: Fahed Mlaiel  
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architecture Expert
- Audio Processing Developer
- DevOps Engineer  
- AI Prompt Engineering Specialist
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
import uuid


class PartnershipType(Enum):
    """Types of strategic partnerships"""
    STRATEGIC_ALLIANCE = "strategic_alliance"
    BRAND_AMBASSADOR = "brand_ambassador"
    CONTENT_LICENSING = "content_licensing"
    DISTRIBUTION_PARTNER = "distribution_partner"
    TECHNOLOGY_PARTNER = "technology_partner"
    INVESTMENT_PARTNER = "investment_partner"
    MEDIA_PARTNER = "media_partner"
    PLATFORM_PARTNER = "platform_partner"
    TALENT_AGENCY = "talent_agency"
    RECORD_LABEL = "record_label"


class PartnershipStatus(Enum):
    """Partnership lifecycle status"""
    PROSPECTING = "prospecting"
    NEGOTIATING = "negotiating"
    UNDER_REVIEW = "under_review"
    ACTIVE = "active"
    PAUSED = "paused" 
    TERMINATED = "terminated"
    RENEWED = "renewed"
    DISPUTE = "dispute"


class ContractType(Enum):
    """Contract types for partnerships"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    REVENUE_SHARE = "revenue_share"
    FLAT_FEE = "flat_fee"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"


class NegotiationStage(Enum):
    """Negotiation process stages"""
    INITIAL_CONTACT = "initial_contact"
    PROPOSAL_SENT = "proposal_sent"
    COUNTER_OFFER = "counter_offer"
    TERMS_DISCUSSION = "terms_discussion"
    LEGAL_REVIEW = "legal_review"
    FINAL_APPROVAL = "final_approval"
    SIGNED = "signed"
    REJECTED = "rejected"


class RevenueModel(Enum):
    """Revenue sharing models"""
    PERCENTAGE_SPLIT = "percentage_split"
    TIERED_COMMISSION = "tiered_commission"
    FLAT_RATE = "flat_rate"
    PERFORMANCE_BONUS = "performance_bonus"
    MILESTONE_BASED = "milestone_based"


@dataclass
class PartnershipMetrics:
    """Partnership performance metrics"""
    partnership_id: str
    revenue_generated: Decimal
    content_views: int
    engagement_rate: float
    conversion_rate: float
    roi_percentage: float
    brand_lift: float
    audience_growth: int
    collaboration_count: int
    satisfaction_score: float
    renewal_probability: float
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContractTerm:
    """Individual contract terms and conditions"""
    term_id: str
    term_name: str
    term_value: Any
    is_negotiable: bool
    priority_level: str
    legal_implications: List[str]
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class Partnership(BaseModel):
    """Core partnership business entity"""
    partnership_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    partner_id: str
    partner_name: str
    partner_type: PartnershipType
    status: PartnershipStatus = PartnershipStatus.PROSPECTING
    
    # Business terms
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renewal: bool = False
    revenue_model: RevenueModel
    commission_rate: Decimal
    minimum_guarantee: Optional[Decimal] = None
    
    # Partnership scope
    content_categories: List[str] = Field(default_factory=list)
    platform_scope: List[str] = Field(default_factory=list)
    geographic_scope: List[str] = Field(default_factory=list)
    exclusivity_terms: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance tracking
    metrics: Optional[PartnershipMetrics] = None
    kpis: Dict[str, Any] = Field(default_factory=dict)
    performance_benchmarks: Dict[str, float] = Field(default_factory=dict)
    
    # Relationship management
    primary_contact: Dict[str, str] = Field(default_factory=dict)
    communication_history: List[Dict] = Field(default_factory=list)
    satisfaction_rating: Optional[float] = None
    
    # Legal and compliance
    contract_version: str = "1.0"
    legal_entity: Optional[str] = None
    tax_implications: Dict[str, Any] = Field(default_factory=dict)
    compliance_requirements: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    tags: List[str] = Field(default_factory=list)

    @validator('commission_rate')
    def validate_commission_rate(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Commission rate must be between 0 and 1')
        return v

    class Config:
        use_enum_values = True


class Contract(BaseModel):
    """Legal contract entity for partnerships"""
    contract_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partnership_id: str
    contract_type: ContractType
    contract_version: str = "1.0"
    
    # Contract content
    terms_and_conditions: List[ContractTerm] = Field(default_factory=list)
    payment_terms: Dict[str, Any] = Field(default_factory=dict)
    intellectual_property: Dict[str, Any] = Field(default_factory=dict)
    termination_clauses: List[str] = Field(default_factory=list)
    
    # Legal framework
    governing_law: str
    jurisdiction: str
    dispute_resolution: str = "arbitration"
    force_majeure: List[str] = Field(default_factory=list)
    
    # Signatures and approval
    creator_signature: Optional[Dict[str, Any]] = None
    partner_signature: Optional[Dict[str, Any]] = None
    legal_review_status: str = "pending"
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    
    # Document management
    contract_document_url: Optional[str] = None
    amendments: List[Dict] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


@dataclass
class PartnershipRevenue:
    """Revenue tracking for partnerships"""
    revenue_id: str
    partnership_id: str
    period_start: datetime
    period_end: datetime
    gross_revenue: Decimal
    platform_fees: Decimal
    partner_commission: Decimal
    net_revenue: Decimal
    currency: str = "USD"
    revenue_sources: Dict[str, Decimal] = field(default_factory=dict)
    payment_status: str = "pending"
    payout_date: Optional[datetime] = None
    transaction_references: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PartnershipOpportunity:
    """Partnership opportunity identification"""
    opportunity_id: str
    creator_id: str
    potential_partner_id: str
    opportunity_type: PartnershipType
    match_score: float
    revenue_potential: Decimal
    risk_assessment: float
    strategic_alignment: float
    market_opportunity: Dict[str, Any] = field(default_factory=dict)
    recommended_terms: Dict[str, Any] = field(default_factory=dict)
    next_actions: List[str] = field(default_factory=list)
    expiration_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    created_at: datetime = field(default_factory=datetime.utcnow)


class NegotiationRecord(BaseModel):
    """Negotiation process tracking"""
    negotiation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partnership_id: str
    stage: NegotiationStage = NegotiationStage.INITIAL_CONTACT
    
    # Negotiation details
    proposal_version: str = "1.0"
    key_terms_discussed: List[str] = Field(default_factory=list)
    concessions_made: List[Dict] = Field(default_factory=list)
    outstanding_issues: List[str] = Field(default_factory=list)
    
    # Communication tracking
    meeting_notes: List[Dict] = Field(default_factory=list)
    email_thread_id: Optional[str] = None
    decision_makers: List[str] = Field(default_factory=list)
    
    # Timeline and milestones
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expected_close_date: Optional[datetime] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    # Success probability
    close_probability: float = 0.5
    deal_value_estimate: Optional[Decimal] = None

    class Config:
        use_enum_values = True


@dataclass
class PartnershipBenchmark:
    """Industry benchmarks for partnership performance"""
    industry_sector: str
    partnership_type: str
    avg_commission_rate: float
    avg_deal_size: Decimal
    avg_contract_length: int  # in months
    success_rate: float
    avg_roi: float
    renewal_rate: float
    satisfaction_score: float
    data_source: str
    last_updated: datetime = field(default_factory=datetime.utcnow)
