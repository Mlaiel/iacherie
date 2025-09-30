"""Revenue & Monetization Schemas for IA Influencer Agent Platform
Professional revenue tracking, monetization, and financial analytics schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pydantic import Field, HttpUrl, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class RevenueCreate(BaseSchema):
    """
Revenue creation/tracking request schema."""
    
    creator_id: UUID = Field(description="Creator receiving revenue")
    content_id: Optional[UUID] = Field(None, description="Associated content")
    revenue_source: str = Field(description="Source of revenue")
    revenue_type: str = Field(description="Type of revenue")
    
    # Financial details
    gross_amount: Decimal = Field(ge=0, description="Gross revenue amount")
    currency: str = Field(default="EUR", max_length=3, description="Revenue currency")
    exchange_rate: Optional[Decimal] = Field(None, description="Exchange rate if applicable")
    
    # Revenue attribution
    platform: str = Field(description="Platform generating revenue")
    territory: str = Field(description="Geographic territory")
    revenue_period_start: datetime = Field(description="Revenue period start")
    revenue_period_end: datetime = Field(description="Revenue period end")
    
    # Transaction details
    transaction_id: str = Field(description="External transaction identifier")
    payment_reference: Optional[str] = Field(None, description="Payment reference number")
    invoice_number: Optional[str] = Field(None, description="Associated invoice number")
    
    # Metadata
    revenue_metadata: Dict[str, Any] = Field(default_factory=dict)
    reporting_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('revenue_source')
    def validate_revenue_source(cls, v):
        """Validate revenue source."""
        allowed_sources = {
            "streaming", "downloads", "licensing", "synchronization", "performance",
            "merchandise", "live_events", "sponsorship", "advertising", "subscription",
            "crowdfunding", "grants", "royalties", "collaboration", "nft_sales"
        }
        if v not in allowed_sources:
            raise ValueError(f'Revenue source must be one of: {", ".join(allowed_sources)}')
        return v


class RevenueOut(UUIDSchema, TimestampSchema):
    """Revenue information schema."""
    
    creator_id: UUID
    content_id: Optional[UUID]
    revenue_source: str
    revenue_type: str
    
    # Financial information
    gross_amount: Decimal
    net_amount: Decimal = Field(description="Net amount after fees")
    currency: str
    fees_deducted: Decimal = Field(default=Decimal('0.00'), ge=0)
    tax_withheld: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Platform and attribution
    platform: str
    territory: str
    revenue_period_start: datetime
    revenue_period_end: datetime
    
    # Payment status
    payment_status: str = Field(default="pending", description="Payment processing status")
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    payout_schedule: Optional[str] = None
    
    # Performance metrics
    units_sold: Optional[int] = Field(None, ge=0, description="Units sold/streamed")
    conversion_rate: Optional[float] = Field(None, ge=0.0, description="Conversion rate")
    average_revenue_per_user: Optional[Decimal] = None
    
    # Quality and verification
    verification_status: str = Field(default="pending")
    dispute_status: Optional[str] = None
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    
    @property
    def fee_percentage(self) -> float:
        """Calculate fee percentage."""
        if self.gross_amount == 0:
            return 0.0
        return float((self.fees_deducted / self.gross_amount) * 100)


class RevenueStream(UUIDSchema, TimestampSchema):
    """
Revenue stream configuration schema."""
    
    creator_id: UUID
    stream_name: str = Field(description="Revenue stream name")
    stream_type: str = Field(description="Type of revenue stream")
    stream_category: str = Field(description="Revenue stream category")
    
    # Stream configuration
    is_active: bool = Field(default=True)
    auto_collection_enabled: bool = Field(default=True)
    collection_frequency: str = Field(default="monthly")
    minimum_payout_threshold: Decimal = Field(default=Decimal('10.00'), ge=0)
    
    # Revenue sources within stream
    connected_platforms: List[str] = Field(default_factory=list)
    content_associations: List[UUID] = Field(default_factory=list)
    partnership_agreements: List[UUID] = Field(default_factory=list)
    
    # Financial settings
    default_currency: str = Field(default="EUR", max_length=3)
    tax_settings: Dict[str, Any] = Field(default_factory=dict)
    fee_structures: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Performance tracking
    total_revenue_lifetime: Decimal = Field(default=Decimal('0.00'), ge=0)
    average_monthly_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    revenue_growth_rate: Optional[float] = None
    last_collection_date: Optional[datetime] = None
    
    # Forecasting
    revenue_forecast: Dict[str, Decimal] = Field(default_factory=dict)
    seasonal_patterns: Dict[str, float] = Field(default_factory=dict)
    growth_projections: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('stream_type')
    def validate_stream_type(cls, v):
        """Validate stream type."""
        allowed_types = {
            "direct_sales", "subscription", "advertising", "licensing", "royalties",
            "commission", "affiliate", "sponsorship", "crowdfunding", "merchandise"
        }
        if v not in allowed_types:
            raise ValueError(f'Stream type must be one of: {", ".join(allowed_types)}')
        return v


class RevenueShare(UUIDSchema, TimestampSchema, AuditSchema):
    """Revenue sharing agreement schema."""
    
    primary_creator_id: UUID = Field(description="Primary revenue recipient")
    collaboration_id: Optional[UUID] = Field(None, description="Associated collaboration")
    sharing_agreement_name: str = Field(description="Revenue sharing agreement name")
    
    # Sharing participants
    participants: List[Dict[str, Any]] = Field(description="Revenue sharing participants")
    sharing_percentages: Dict[str, float] = Field(description="Revenue share percentages")
    minimum_thresholds: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Agreement terms
    effective_date: datetime = Field(description="Agreement effective date")
    expiration_date: Optional[datetime] = None
    auto_renewal: bool = Field(default=False)
    termination_notice_period: int = Field(default=30, description="Notice period in days")
    
    # Revenue scope
    included_revenue_types: List[str] = Field(description="Revenue types included in sharing")
    excluded_revenue_types: List[str] = Field(default_factory=list)
    geographic_scope: List[str] = Field(default_factory=list)
    platform_scope: List[str] = Field(default_factory=list)
    
    # Financial rules
    fee_allocation: Dict[str, str] = Field(default_factory=dict, description="How fees are allocated")
    tax_responsibility: Dict[str, str] = Field(default_factory=dict)
    payment_timing: str = Field(default="monthly")
    currency_conversion_rules: Dict[str, str] = Field(default_factory=dict)
    
    # Tracking and reporting
    revenue_tracking_method: str = Field(default="automated")
    reporting_frequency: str = Field(default="monthly")
    audit_rights: Dict[str, bool] = Field(default_factory=dict)
    dispute_resolution_method: str = Field(default="mediation")
    
    # Performance metrics
    total_shared_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    last_distribution_date: Optional[datetime] = None
    distributions_count: int = Field(default=0, ge=0)
    average_distribution_amount: Decimal = Field(default=Decimal('0.00'), ge=0)


class PaymentRecord(UUIDSchema, TimestampSchema):
    """Payment transaction record schema."""
    
    creator_id: UUID = Field(description="Payment recipient")
    revenue_id: Optional[UUID] = Field(None, description="Associated revenue record")
    payment_type: str = Field(description="Type of payment")
    payment_method: str = Field(description="Payment method used")
    
    # Payment amounts
    gross_amount: Decimal = Field(ge=0, description="Gross payment amount")
    net_amount: Decimal = Field(ge=0, description="Net payment amount")
    currency: str = Field(max_length=3)
    processing_fees: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Payment details
    payment_processor: str = Field(description="Payment processor used")
    transaction_id: str = Field(description="Processor transaction ID")
    payment_reference: str = Field(description="Internal payment reference")
    batch_id: Optional[str] = Field(None, description="Batch processing ID")
    
    # Status and timing
    payment_status: str = Field(description="Current payment status")
    initiated_at: datetime = Field(description="Payment initiation timestamp")
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    # Recipient information
    recipient_account_info: Dict[str, str] = Field(description="Recipient account details")
    recipient_verification_status: str = Field(default="verified")
    
    # Error handling
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=1)
    
    # Compliance and audit
    compliance_checks: Dict[str, bool] = Field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    tax_reporting_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('payment_type')
    def validate_payment_type(cls, v):
        """Validate payment type."""
        allowed_types = {
            "royalty_payment", "revenue_share", "licensing_fee", "advance_payment",
            "bonus_payment", "refund", "adjustment", "settlement", "commission"
        }
        if v not in allowed_types:
            raise ValueError(f'Payment type must be one of: {", ".join(allowed_types)}')
        return v


class RoyaltyCalculation(UUIDSchema, TimestampSchema):
    """Royalty calculation schema."""
    
    content_id: UUID = Field(description="Content generating royalties")
    rights_holder_id: UUID = Field(description="Rights holder receiving royalties")
    calculation_period_start: datetime
    calculation_period_end: datetime
    
    # Calculation parameters
    royalty_rate: Decimal = Field(ge=0, le=100, description="Royalty rate percentage")
    minimum_royalty: Optional[Decimal] = Field(None, ge=0)
    maximum_royalty: Optional[Decimal] = None
    calculation_method: str = Field(description="Royalty calculation method")
    
    # Usage data
    total_usage_units: int = Field(ge=0, description="Total usage units")
    usage_by_territory: Dict[str, int] = Field(default_factory=dict)
    usage_by_platform: Dict[str, int] = Field(default_factory=dict)
    usage_by_type: Dict[str, int] = Field(default_factory=dict)
    
    # Revenue data
    gross_revenue: Decimal = Field(ge=0, description="Gross revenue generated")
    net_revenue: Decimal = Field(ge=0, description="Net revenue after platform fees")
    applicable_revenue: Decimal = Field(ge=0, description="Revenue subject to royalties")
    
    # Calculated royalties
    calculated_royalties: Decimal = Field(ge=0, description="Calculated royalty amount")
    adjustments: Decimal = Field(default=Decimal('0.00'), description="Manual adjustments")
    final_royalties: Decimal = Field(ge=0, description="Final royalty amount after adjustments")
    
    # Deductions and fees
    collection_fees: Decimal = Field(default=Decimal('0.00'), ge=0)
    administration_fees: Decimal = Field(default=Decimal('0.00'), ge=0)
    currency_conversion_fees: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Verification and audit
    calculation_verified: bool = Field(default=False)
    verification_notes: Optional[str] = None
    external_audit_required: bool = Field(default=False)
    dispute_period_end: Optional[datetime] = None
    
    @validator('calculation_method')
    def validate_calculation_method(cls, v):
        """Validate calculation method."""
        allowed_methods = {
            "percentage_of_revenue", "per_unit", "tiered_percentage", "minimum_guarantee",
            "advance_recoupment", "pro_rata", "weighted_average", "custom_formula"
        }
        if v not in allowed_methods:
            raise ValueError(f'Calculation method must be one of: {", ".join(allowed_methods)}')
        return v


class MonetizationReport(UUIDSchema, TimestampSchema):
    """Comprehensive monetization report schema."""
    
    creator_id: UUID
    report_type: str = Field(description="Type of monetization report")
    report_period_start: datetime
    report_period_end: datetime
    
    # Revenue summary
    total_gross_revenue: Decimal = Field(ge=0)
    total_net_revenue: Decimal = Field(ge=0)
    revenue_by_source: Dict[str, Decimal] = Field(default_factory=dict)
    revenue_by_platform: Dict[str, Decimal] = Field(default_factory=dict)
    revenue_by_territory: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Performance metrics
    revenue_growth_rate: Optional[float] = None
    average_revenue_per_content: Decimal = Field(default=Decimal('0.00'), ge=0)
    conversion_rates: Dict[str, float] = Field(default_factory=dict)
    top_performing_content: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Financial analysis
    profit_margins: Dict[str, float] = Field(default_factory=dict)
    cost_breakdown: Dict[str, Decimal] = Field(default_factory=dict)
    roi_analysis: Dict[str, float] = Field(default_factory=dict)
    break_even_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Comparative analysis
    period_over_period_comparison: Dict[str, Any] = Field(default_factory=dict)
    benchmark_comparisons: Dict[str, Any] = Field(default_factory=dict)
    industry_position: Optional[Dict[str, Any]] = None
    
    # Forecasting
    revenue_projections: Dict[str, Decimal] = Field(default_factory=dict)
    growth_opportunities: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Supporting data
    detailed_transactions: int = Field(ge=0, description="Number of transactions")
    data_quality_score: float = Field(ge=0.0, le=1.0, description="Data completeness score")
    report_confidence_level: float = Field(ge=0.0, le=1.0, description="Report accuracy confidence")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        """Validate report type."""
        allowed_types = {
            "monthly_summary", "quarterly_analysis", "annual_report", "performance_dashboard",
            "comparative_analysis", "forecasting_report", "audit_report", "tax_report"
        }
        if v not in allowed_types:
            raise ValueError(f'Report type must be one of: {", ".join(allowed_types)}')
        return v


class FinancialAnalytics(UUIDSchema, TimestampSchema):
    """Advanced financial analytics schema."""
    
    creator_id: UUID
    analytics_type: str = Field(description="Type of financial analysis")
    analysis_period_start: datetime
    analysis_period_end: datetime
    
    # Revenue analytics
    revenue_trends: Dict[str, List[float]] = Field(default_factory=dict)
    seasonality_patterns: Dict[str, float] = Field(default_factory=dict)
    revenue_volatility: float = Field(ge=0.0, description="Revenue volatility measure")
    predictability_score: float = Field(ge=0.0, le=1.0, description="Revenue predictability")
    
    # Profitability analysis
    gross_margin_trends: List[float] = Field(default_factory=list)
    net_margin_trends: List[float] = Field(default_factory=list)
    cost_efficiency_ratios: Dict[str, float] = Field(default_factory=dict)
    break_even_points: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Portfolio analysis
    content_portfolio_performance: Dict[str, Any] = Field(default_factory=dict)
    diversification_metrics: Dict[str, float] = Field(default_factory=dict)
    risk_adjusted_returns: Dict[str, float] = Field(default_factory=dict)
    
    # Market analysis
    market_share_estimates: Dict[str, float] = Field(default_factory=dict)
    competitive_positioning: Dict[str, Any] = Field(default_factory=dict)
    market_opportunity_size: Optional[Decimal] = None
    addressable_market_penetration: Optional[float] = None
    
    # Investment analysis
    roi_by_investment_type: Dict[str, float] = Field(default_factory=dict)
    payback_periods: Dict[str, float] = Field(default_factory=dict)
    investment_efficiency: Dict[str, float] = Field(default_factory=dict)
    
    # Risk assessment
    financial_risk_score: float = Field(ge=0.0, le=1.0)
    concentration_risk: Dict[str, float] = Field(default_factory=dict)
    market_risk_factors: List[str] = Field(default_factory=list)
    mitigation_strategies: List[str] = Field(default_factory=list)
    
    # Predictive modeling
    revenue_forecasts: Dict[str, Decimal] = Field(default_factory=dict)
    growth_scenarios: Dict[str, Any] = Field(default_factory=dict)
    sensitivity_analysis: Dict[str, float] = Field(default_factory=dict)
    
    # Key performance indicators
    financial_kpis: Dict[str, float] = Field(default_factory=dict)
    benchmark_comparisons: Dict[str, float] = Field(default_factory=dict)
    performance_alerts: List[str] = Field(default_factory=list)
    
    @validator('analytics_type')
    def validate_analytics_type(cls, v):
        """Validate analytics type."""
        allowed_types = {
            "revenue_analysis", "profitability_analysis", "portfolio_analysis",
            "market_analysis", "risk_assessment", "investment_analysis",
            "predictive_modeling", "comparative_benchmarking"
        }
        if v not in allowed_types:
            raise ValueError(f'Analytics type must be one of: {", ".join(allowed_types)}')
        return v
