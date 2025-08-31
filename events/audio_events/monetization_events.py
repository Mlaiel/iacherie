"""Audio Monetization Events - Industrial Grade Revenue & Licensing Management
==========================================================================

This module handles all events related to audio monetization, licensing,
revenue tracking, and automated payment distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum
from decimal import Decimal

from ...core.events.base_event import BaseEvent, EventPriority, EventCategory


class LicenseType(Enum):
    """Types of music licenses"""
    SYNC_LICENSE = "sync_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"
    MASTER_LICENSE = "master_license"
    PRINT_LICENSE = "print_license"
    SAMPLING_LICENSE = "sampling_license"
    EXCLUSIVE_LICENSE = "exclusive_license"
    NON_EXCLUSIVE_LICENSE = "non_exclusive_license"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"


class RevenueSource(Enum):
    """Sources of audio revenue"""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    SYNC_DEALS = "sync_deals"
    LIVE_PERFORMANCE = "live_performance"
    MERCHANDISE = "merchandise"
    SPONSORSHIP = "sponsorship"
    COLLABORATION = "collaboration"
    REMIX_FEES = "remix_fees"
    SAMPLE_CLEARANCE = "sample_clearance"


class PaymentStatus(Enum):
    """Payment processing statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"


@dataclass
class AudioMonetizationStartedEvent(BaseEvent):
    """
    Event triggered when monetization setup for audio content begins.
    
    Initializes revenue tracking and licensing workflows.
    """
    user_id: UUID
    file_id: UUID
    monetization_id: UUID
    filename: str
    monetization_strategies: List[str]
    target_markets: List[str]
    pricing_strategy: str
    license_types_enabled: List[LicenseType]
    revenue_sources_enabled: List[RevenueSource]
    geographical_restrictions: List[str]
    age_restrictions: bool
    content_rating: str
    estimated_revenue_potential: float
    monetization_tier: str  # basic, premium, enterprise
    automated_licensing: bool = True
    dynamic_pricing: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.monetization.started",
            event_category=EventCategory.MONETIZATION,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "monetization_id": str(self.monetization_id),
                "strategies_count": len(self.monetization_strategies),
                "markets_count": len(self.target_markets),
                "license_types_count": len(self.license_types_enabled),
                "revenue_potential": self.estimated_revenue_potential,
                "automated_licensing": self.automated_licensing
            }
        )


@dataclass
class AudioLicenseCreatedEvent(BaseEvent):
    """
    Event triggered when a new audio license is created.
    
    Contains comprehensive license terms and conditions.
    """
    user_id: UUID
    file_id: UUID
    license_id: UUID
    license_type: LicenseType
    licensee_id: Optional[UUID] = None
    licensee_name: str = ""
    license_fee: Decimal = Decimal('0.00')
    royalty_percentage: float = 0.0
    license_duration: Optional[int] = None  # days
    usage_rights: List[str] = field(default_factory=list)
    geographical_scope: List[str] = field(default_factory=list)
    medium_restrictions: List[str] = field(default_factory=list)
    exclusive_license: bool = False
    sublicensing_allowed: bool = False
    commercial_use_allowed: bool = True
    modification_rights: List[str] = field(default_factory=list)
    attribution_required: bool = True
    license_effective_date: datetime = field(default_factory=datetime.now)
    license_expiry_date: Optional[datetime] = None
    auto_renewal: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.monetization.license_created",
            event_category=EventCategory.LICENSING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "license_id": str(self.license_id),
                "license_type": self.license_type.value,
                "licensee_id": str(self.licensee_id) if self.licensee_id else None,
                "license_fee": float(self.license_fee),
                "exclusive": self.exclusive_license,
                "commercial_use": self.commercial_use_allowed
            }
        )


@dataclass
class AudioRevenueGeneratedEvent(BaseEvent):
    """
    Event triggered when revenue is generated from audio content.
    
    Tracks all revenue streams and payment processing.
    """
    user_id: UUID
    file_id: UUID
    revenue_id: UUID
    revenue_source: RevenueSource
    gross_amount: Decimal
    net_amount: Decimal
    currency: str = "EUR"
    transaction_fee: Decimal = Decimal('0.00')
    platform_commission: Decimal = Decimal('0.00')
    tax_amount: Decimal = Decimal('0.00')
    payment_processor: str = ""
    transaction_id: str = ""
    payer_id: Optional[UUID] = None
    payer_name: str = ""
    revenue_period_start: datetime = field(default_factory=datetime.now)
    revenue_period_end: datetime = field(default_factory=datetime.now)
    geographical_source: str = ""
    platform_source: str = ""
    usage_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.monetization.revenue_generated",
            event_category=EventCategory.REVENUE,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "revenue_id": str(self.revenue_id),
                "revenue_source": self.revenue_source.value,
                "gross_amount": float(self.gross_amount),
                "net_amount": float(self.net_amount),
                "currency": self.currency,
                "platform_source": self.platform_source
            }
        )


@dataclass
class AudioRoyaltyDistributedEvent(BaseEvent):
    """
    Event triggered when royalties are distributed to rights holders.
    
    Handles automated royalty calculations and payments.
    """
    file_id: UUID
    distribution_id: UUID
    total_revenue: Decimal
    currency: str = "EUR"
    distribution_period_start: datetime
    distribution_period_end: datetime
    rights_holders: Dict[UUID, Dict[str, Any]]  # user_id -> {percentage, amount, role}
    distribution_method: str  # automated, manual
    payment_processor: str
    payment_batch_id: str
    distribution_fees: Decimal = Decimal('0.00')
    tax_withholdings: Dict[UUID, Decimal] = field(default_factory=dict)
    payment_status: Dict[UUID, PaymentStatus] = field(default_factory=dict)
    payment_dates: Dict[UUID, datetime] = field(default_factory=dict)
    distribution_accuracy: float = 1.0
    dispute_window_days: int = 30
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.monetization.royalty_distributed",
            event_category=EventCategory.ROYALTY,
            priority=EventPriority.HIGH,
            metadata={
                "file_id": str(self.file_id),
                "distribution_id": str(self.distribution_id),
                "total_revenue": float(self.total_revenue),
                "currency": self.currency,
                "rights_holders_count": len(self.rights_holders),
                "distribution_method": self.distribution_method,
                "distribution_accuracy": self.distribution_accuracy
            }
        )


@dataclass
class AudioSaleCompletedEvent(BaseEvent):
    """
    Event triggered when an audio sale transaction is completed.
    
    Handles individual sales and purchase confirmations.
    """
    seller_id: UUID
    buyer_id: UUID
    file_id: UUID
    sale_id: UUID
    sale_type: str  # download, license, exclusive_rights, bundle
    sale_price: Decimal
    currency: str = "EUR"
    payment_method: str = ""
    transaction_fee: Decimal = Decimal('0.00')
    seller_earnings: Decimal = Decimal('0.00')
    platform_commission: Decimal = Decimal('0.00')
    sale_timestamp: datetime = field(default_factory=datetime.now)
    delivery_method: str = "digital_download"
    license_terms: Dict[str, Any] = field(default_factory=dict)
    buyer_location: str = ""
    sale_channel: str = "direct"
    promotional_discount: Decimal = Decimal('0.00')
    affiliate_commission: Decimal = Decimal('0.00')
    refund_eligible: bool = True
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.monetization.sale_completed",
            event_category=EventCategory.SALES,
            priority=EventPriority.HIGH,
            user_id=self.seller_id,
            metadata={
                "sale_id": str(self.sale_id),
                "buyer_id": str(self.buyer_id),
                "file_id": str(self.file_id),
                "sale_type": self.sale_type,
                "sale_price": float(self.sale_price),
                "currency": self.currency,
                "seller_earnings": float(self.seller_earnings),
                "sale_channel": self.sale_channel
            }
        )


@dataclass
class AudioStreamingRevenueEvent(BaseEvent):
    """
    Event triggered when streaming revenue is calculated and attributed.
    
    Handles streaming platform revenue attribution and distribution.
    """
    user_id: UUID
    file_id: UUID
    streaming_period_start: datetime
    streaming_period_end: datetime
    total_streams: int
    total_revenue: Decimal
    currency: str = "EUR"
    platform_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # platform -> {streams, revenue}
    geographical_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    demographic_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    revenue_per_stream: Decimal = Decimal('0.00')
    premium_streams: int = 0
    free_tier_streams: int = 0
    playlist_additions: int = 0
    algorithmic_discoveries: int = 0
    organic_discoveries: int = 0
    completion_rate: float = 0.0
    replay_rate: float = 0.0
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.monetization.streaming_revenue",
            event_category=EventCategory.STREAMING,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "total_streams": self.total_streams,
                "total_revenue": float(self.total_revenue),
                "currency": self.currency,
                "platforms_count": len(self.platform_breakdown),
                "revenue_per_stream": float(self.revenue_per_stream),
                "completion_rate": self.completion_rate
            }
        )


@dataclass
class AudioSyncLicenseRequestEvent(BaseEvent):
    """
    Event triggered when a sync license is requested for media placement.
    
    Handles synchronization licensing for films, TV, ads, games, etc.
    """
    user_id: UUID
    file_id: UUID
    sync_request_id: UUID
    requestor_id: UUID
    requestor_name: str
    project_type: str  # film, tv_show, commercial, video_game, podcast, youtube
    project_title: str
    usage_description: str
    usage_duration: float  # seconds of audio used
    territory: List[str]
    media_budget: Optional[Decimal] = None
    distribution_scope: str  # theatrical, streaming, broadcast, digital
    license_duration: int = 365  # days
    exclusivity_requested: bool = False
    modification_rights_requested: bool = False
    synchronization_fee_offered: Decimal = Decimal('0.00')
    master_recording_fee_offered: Decimal = Decimal('0.00')
    publishing_fee_offered: Decimal = Decimal('0.00')
    usage_deadline: datetime = field(default_factory=lambda: datetime.now())
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.monetization.sync_license_request",
            event_category=EventCategory.SYNC_LICENSING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "sync_request_id": str(self.sync_request_id),
                "requestor_id": str(self.requestor_id),
                "project_type": self.project_type,
                "territory_count": len(self.territory),
                "total_fee_offered": float(self.synchronization_fee_offered + self.master_recording_fee_offered + self.publishing_fee_offered),
                "exclusivity_requested": self.exclusivity_requested
            }
        )


@dataclass
class AudioPerformanceRoyaltyEvent(BaseEvent):
    """
    Event triggered when performance royalties are generated.
    
    Tracks public performance revenue from radio, live venues, streaming.
    """
    user_id: UUID
    file_id: UUID
    performance_period_start: datetime
    performance_period_end: datetime
    performing_rights_organization: str  # BMI, ASCAP, PRS, GEMA, etc.
    total_performances: int
    total_royalties: Decimal
    currency: str = "EUR"
    performance_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    radio_performances: int = 0
    streaming_performances: int = 0
    live_performances: int = 0
    background_music_performances: int = 0
    commercial_performances: int = 0
    international_collections: Dict[str, Decimal] = field(default_factory=dict)
    songwriter_share: Decimal = Decimal('0.00')
    publisher_share: Decimal = Decimal('0.00')
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.monetization.performance_royalty",
            event_category=EventCategory.PERFORMANCE,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "performing_rights_org": self.performing_rights_organization,
                "total_performances": self.total_performances,
                "total_royalties": float(self.total_royalties),
                "currency": self.currency,
                "songwriter_share": float(self.songwriter_share),
                "publisher_share": float(self.publisher_share)
            }
        )


@dataclass
class AudioMonetizationAnalyticsEvent(BaseEvent):
    """
    Event triggered for comprehensive monetization analytics updates.
    
    Provides insights and predictions for revenue optimization.
    """
    user_id: UUID
    file_id: UUID
    analytics_period_start: datetime
    analytics_period_end: datetime
    total_revenue: Decimal
    revenue_growth_rate: float
    revenue_sources_performance: Dict[str, Decimal]
    top_markets: List[Tuple[str, Decimal]]  # (market, revenue)
    revenue_predictions: Dict[str, float]  # next periods
    optimization_suggestions: List[str]
    market_trends: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    pricing_recommendations: Dict[str, Decimal]
    licensing_opportunities: List[Dict[str, Any]]
    roi_metrics: Dict[str, float]
    audience_insights: Dict[str, Any]
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.monetization.analytics",
            event_category=EventCategory.ANALYTICS,
            priority=EventPriority.LOW,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "total_revenue": float(self.total_revenue),
                "revenue_growth_rate": self.revenue_growth_rate,
                "top_markets_count": len(self.top_markets),
                "optimization_suggestions_count": len(self.optimization_suggestions),
                "licensing_opportunities_count": len(self.licensing_opportunities)
            }
        )
