#!/usr/bin/env python3
"""Revenue Distribution Engine

Advanced multi-platform revenue tracking and distribution system for content
creators. Provides unified revenue analytics, ROI calculation, budget optimization,
and cross-platform monetization tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from decimal import Decimal, ROUND_HALF_UP
import uuid

logger = logging.getLogger(__name__)


class RevenueType(Enum):
    """Types of revenue streams"""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    MERCHANDISE = "merchandise"
    SPONSORSHIP = "sponsorship"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    TIP_DONATION = "tip_donation"
    NFT_SALES = "nft_sales"
    COMMISSION = "commission"


class PaymentMethod(Enum):
    """Payment methods for revenue collection"""
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    PLATFORM_NATIVE = "platform_native"
    CHECK = "check"


class Currency(Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"


class RevenueStatus(Enum):
    """Revenue payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"


@dataclass
class RevenueStream:
    """Individual revenue stream configuration"""
    stream_id: str
    platform: str
    revenue_type: RevenueType
    content_id: str
    creator_id: str
    rate_per_unit: Decimal
    currency: Currency
    payment_threshold: Decimal
    payment_frequency: str  # daily, weekly, monthly
    platform_fee_percentage: Decimal
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RevenueRecord:
    """Individual revenue transaction record"""
    record_id: str
    stream_id: str
    platform: str
    content_id: str
    creator_id: str
    revenue_type: RevenueType
    gross_amount: Decimal
    platform_fee: Decimal
    net_amount: Decimal
    currency: Currency
    units_sold: int
    transaction_date: datetime
    payment_date: Optional[datetime] = None
    status: RevenueStatus = RevenueStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformMetrics:
    """Platform-specific revenue metrics"""
    platform: str
    total_revenue: Decimal
    total_views: int
    total_downloads: int
    total_streams: int
    average_revenue_per_user: Decimal
    conversion_rate: float
    top_content: List[str]
    revenue_by_type: Dict[RevenueType, Decimal]
    period_start: datetime
    period_end: datetime


@dataclass
class ROIAnalysis:
    """Return on Investment analysis"""
    content_id: str
    investment: Decimal  # Production and promotion costs
    total_revenue: Decimal
    net_profit: Decimal
    roi_percentage: float
    break_even_date: Optional[datetime]
    platforms_performance: Dict[str, Dict[str, Any]]
    cost_breakdown: Dict[str, Decimal]
    revenue_breakdown: Dict[str, Decimal]
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class BudgetAllocation:
    """Budget allocation recommendation"""
    content_id: str
    total_budget: Decimal
    platform_allocations: Dict[str, Decimal]
    expected_roi: Dict[str, float]
    risk_assessment: Dict[str, str]
    optimization_suggestions: List[str]
    confidence_score: float
    valid_until: datetime


@dataclass
class ConsolidatedReport:
    """Consolidated revenue report across all platforms"""
    report_id: str
    creator_id: str
    period_start: datetime
    period_end: datetime
    total_gross_revenue: Decimal
    total_net_revenue: Decimal
    total_platform_fees: Decimal
    currency: Currency
    platform_breakdown: Dict[str, PlatformMetrics]
    content_breakdown: Dict[str, Decimal]
    revenue_trends: Dict[str, List[Tuple[datetime, Decimal]]]
    top_performing_content: List[Tuple[str, Decimal]]
    growth_rate: float
    projections: Dict[str, Decimal]
    generated_at: datetime = field(default_factory=datetime.now)


class RevenueDistribution:
    """
    Advanced revenue distribution and tracking engine.
    
    Provides comprehensive revenue management across multiple platforms
    including tracking, analytics, optimization, and automated distribution.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize revenue distribution engine"""
        self.config = config or {}
        self.revenue_streams = {}
        self.revenue_records = []
        self.platform_integrations = {}
        self.exchange_rates = {}
        self.payment_processors = {}
        self._initialize_default_configurations()

    def _initialize_default_configurations(self):
        """Initialize default platform configurations"""
        self.platform_configs = {
            "spotify": {
                "revenue_types": [RevenueType.STREAMING],
                "fee_percentage": Decimal("30.0"),
                "payment_threshold": Decimal("20.00"),
                "payment_frequency": "monthly",
                "currency": Currency.USD
            },
            "youtube": {
                "revenue_types": [RevenueType.ADVERTISING, RevenueType.SUBSCRIPTION],
                "fee_percentage": Decimal("45.0"),
                "payment_threshold": Decimal("100.00"),
                "payment_frequency": "monthly",
                "currency": Currency.USD
            },
            "instagram": {
                "revenue_types": [RevenueType.SPONSORSHIP, RevenueType.ADVERTISING],
                "fee_percentage": Decimal("30.0"),
                "payment_threshold": Decimal("50.00"),
                "payment_frequency": "weekly",
                "currency": Currency.USD
            },
            "bandcamp": {
                "revenue_types": [RevenueType.DOWNLOADS, RevenueType.MERCHANDISE],
                "fee_percentage": Decimal("10.0"),
                "payment_threshold": Decimal("10.00"),
                "payment_frequency": "weekly",
                "currency": Currency.USD
            },
            "patreon": {
                "revenue_types": [RevenueType.SUBSCRIPTION, RevenueType.TIP_DONATION],
                "fee_percentage": Decimal("8.0"),
                "payment_threshold": Decimal("1.00"),
                "payment_frequency": "monthly",
                "currency": Currency.USD
            },
            "onlyfans": {
                "revenue_types": [RevenueType.SUBSCRIPTION, RevenueType.TIP_DONATION],
                "fee_percentage": Decimal("20.0"),
                "payment_threshold": Decimal("20.00"),
                "payment_frequency": "weekly",
                "currency": Currency.USD
            }
        }
        
        # Load current exchange rates (placeholder)
        self.exchange_rates = {
            (Currency.USD, Currency.EUR): Decimal("0.85"),
            (Currency.USD, Currency.GBP): Decimal("0.75"),
            (Currency.EUR, Currency.USD): Decimal("1.18"),
            (Currency.GBP, Currency.USD): Decimal("1.33")
        }

    async def create_revenue_stream(
        self,
        platform: str,
        content_id: str,
        creator_id: str,
        revenue_type: RevenueType,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> RevenueStream:
        """
        Create a new revenue stream for content on a platform
        
        Args:
            platform: Platform name
            content_id: Content identifier
            creator_id: Creator identifier
            revenue_type: Type of revenue stream
            custom_config: Custom configuration overrides
            
        Returns:
            RevenueStream: Created revenue stream configuration
        """
        try:
            stream_id = f"{platform}_{content_id}_{revenue_type.value}_{uuid.uuid4().hex[:8]}"
            
            # Get platform default configuration
            platform_config = self.platform_configs.get(platform, {})
            config = platform_config.copy()
            
            if custom_config:
                config.update(custom_config)
            
            revenue_stream = RevenueStream(
                stream_id=stream_id,
                platform=platform,
                revenue_type=revenue_type,
                content_id=content_id,
                creator_id=creator_id,
                rate_per_unit=Decimal(str(config.get("rate_per_unit", "0.01"))),
                currency=config.get("currency", Currency.USD),
                payment_threshold=Decimal(str(config.get("payment_threshold", "20.00"))),
                payment_frequency=config.get("payment_frequency", "monthly"),
                platform_fee_percentage=Decimal(str(config.get("fee_percentage", "30.0")))
            )
            
            self.revenue_streams[stream_id] = revenue_stream
            
            logger.info(f"Created revenue stream {stream_id} for content {content_id} on {platform}")
            return revenue_stream
            
        except Exception as e:
            logger.error(f"Error creating revenue stream: {str(e)}")
            raise

    async def record_revenue(
        self,
        stream_id: str,
        gross_amount: Decimal,
        units_sold: int = 1,
        transaction_metadata: Optional[Dict[str, Any]] = None
    ) -> RevenueRecord:
        """
        Record a revenue transaction
        
        Args:
            stream_id: Revenue stream identifier
            gross_amount: Gross revenue amount
            units_sold: Number of units sold
            transaction_metadata: Additional transaction data
            
        Returns:
            RevenueRecord: Created revenue record
        """
        try:
            if stream_id not in self.revenue_streams:
                raise ValueError(f"Revenue stream {stream_id} not found")
            
            stream = self.revenue_streams[stream_id]
            
            # Calculate platform fee and net amount
            platform_fee = gross_amount * (stream.platform_fee_percentage / Decimal("100"))
            net_amount = gross_amount - platform_fee
            
            record = RevenueRecord(
                record_id=f"rev_{uuid.uuid4().hex}",
                stream_id=stream_id,
                platform=stream.platform,
                content_id=stream.content_id,
                creator_id=stream.creator_id,
                revenue_type=stream.revenue_type,
                gross_amount=gross_amount,
                platform_fee=platform_fee,
                net_amount=net_amount,
                currency=stream.currency,
                units_sold=units_sold,
                transaction_date=datetime.now(),
                metadata=transaction_metadata or {}
            )
            
            self.revenue_records.append(record)
            
            logger.info(f"Recorded revenue: {gross_amount} {stream.currency.value} for stream {stream_id}")
            return record
            
        except Exception as e:
            logger.error(f"Error recording revenue: {str(e)}")
            raise

    async def calculate_platform_metrics(
        self,
        platform: str,
        period_start: datetime,
        period_end: datetime,
        creator_id: Optional[str] = None
    ) -> PlatformMetrics:
        """
        Calculate comprehensive metrics for a platform
        
        Args:
            platform: Platform name
            period_start: Start of analysis period
            period_end: End of analysis period
            creator_id: Optional creator filter
            
        Returns:
            PlatformMetrics: Calculated platform metrics
        """
        try:
            # Filter records for platform and period
            records = [
                r for r in self.revenue_records
                if r.platform == platform
                and period_start <= r.transaction_date <= period_end
                and (not creator_id or r.creator_id == creator_id)
            ]
            
            if not records:
                return PlatformMetrics(
                    platform=platform,
                    total_revenue=Decimal("0"),
                    total_views=0,
                    total_downloads=0,
                    total_streams=0,
                    average_revenue_per_user=Decimal("0"),
                    conversion_rate=0.0,
                    top_content=[],
                    revenue_by_type={},
                    period_start=period_start,
                    period_end=period_end
                )
            
            # Calculate basic metrics
            total_revenue = sum(r.net_amount for r in records)
            total_units = sum(r.units_sold for r in records)
            
            # Calculate revenue by type
            revenue_by_type = {}
            for revenue_type in RevenueType:
                type_revenue = sum(
                    r.net_amount for r in records if r.revenue_type == revenue_type
                )
                if type_revenue > 0:
                    revenue_by_type[revenue_type] = type_revenue
            
            # Calculate top performing content
            content_revenue = {}
            for record in records:
                if record.content_id not in content_revenue:
                    content_revenue[record.content_id] = Decimal("0")
                content_revenue[record.content_id] += record.net_amount
            
            top_content = sorted(
                content_revenue.keys(),
                key=lambda x: content_revenue[x],
                reverse=True
            )[:10]
            
            # Calculate derived metrics
            unique_users = len(set(r.metadata.get("user_id", r.record_id) for r in records))
            average_revenue_per_user = total_revenue / max(unique_users, 1)
            
            # Placeholder for view/stream data (would come from platform APIs)
            total_views = sum(r.metadata.get("views", 0) for r in records)
            total_downloads = sum(r.units_sold for r in records if r.revenue_type == RevenueType.DOWNLOADS)
            total_streams = sum(r.units_sold for r in records if r.revenue_type == RevenueType.STREAMING)
            
            conversion_rate = (len(records) / max(total_views, 1)) * 100 if total_views > 0 else 0.0
            
            metrics = PlatformMetrics(
                platform=platform,
                total_revenue=total_revenue,
                total_views=total_views,
                total_downloads=total_downloads,
                total_streams=total_streams,
                average_revenue_per_user=average_revenue_per_user,
                conversion_rate=conversion_rate,
                top_content=top_content,
                revenue_by_type=revenue_by_type,
                period_start=period_start,
                period_end=period_end
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating platform metrics: {str(e)}")
            raise

    async def calculate_roi_analysis(
        self,
        content_id: str,
        investment_costs: Dict[str, Decimal]
    ) -> ROIAnalysis:
        """
        Calculate comprehensive ROI analysis for content
        
        Args:
            content_id: Content identifier
            investment_costs: Breakdown of investment costs
            
        Returns:
            ROIAnalysis: Comprehensive ROI analysis
        """
        try:
            # Get all revenue records for this content
            content_records = [r for r in self.revenue_records if r.content_id == content_id]
            
            if not content_records:
                raise ValueError(f"No revenue records found for content {content_id}")
            
            total_investment = sum(investment_costs.values())
            total_revenue = sum(r.net_amount for r in content_records)
            net_profit = total_revenue - total_investment
            
            roi_percentage = float((net_profit / total_investment) * 100) if total_investment > 0 else 0.0
            
            # Calculate break-even date
            break_even_date = None
            cumulative_revenue = Decimal("0")
            
            sorted_records = sorted(content_records, key=lambda x: x.transaction_date)
            for record in sorted_records:
                cumulative_revenue += record.net_amount
                if cumulative_revenue >= total_investment:
                    break_even_date = record.transaction_date
                    break
            
            # Calculate platform performance
            platform_performance = {}
            platforms = set(r.platform for r in content_records)
            
            for platform in platforms:
                platform_records = [r for r in content_records if r.platform == platform]
                platform_revenue = sum(r.net_amount for r in platform_records)
                platform_roi = float((platform_revenue / total_investment) * 100) if total_investment > 0 else 0.0
                
                platform_performance[platform] = {
                    "revenue": platform_revenue,
                    "roi_percentage": platform_roi,
                    "transaction_count": len(platform_records),
                    "average_transaction": platform_revenue / len(platform_records) if platform_records else Decimal("0")
                }
            
            # Revenue breakdown by type
            revenue_breakdown = {}
            for revenue_type in RevenueType:
                type_revenue = sum(
                    r.net_amount for r in content_records if r.revenue_type == revenue_type
                )
                if type_revenue > 0:
                    revenue_breakdown[revenue_type.value] = type_revenue
            
            analysis = ROIAnalysis(
                content_id=content_id,
                investment=total_investment,
                total_revenue=total_revenue,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                break_even_date=break_even_date,
                platforms_performance=platform_performance,
                cost_breakdown=investment_costs,
                revenue_breakdown=revenue_breakdown
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error calculating ROI analysis: {str(e)}")
            raise

    async def optimize_budget_allocation(
        self,
        content_data: Dict[str, Any],
        total_budget: Decimal,
        target_platforms: List[str],
        historical_performance: Optional[Dict[str, Any]] = None
    ) -> BudgetAllocation:
        """
        Optimize budget allocation across platforms based on predicted ROI
        
        Args:
            content_data: Content metadata for analysis
            total_budget: Total available budget
            target_platforms: Platforms to consider
            historical_performance: Historical performance data
            
        Returns:
            BudgetAllocation: Optimized budget allocation recommendations
        """
        try:
            platform_scores = {}
            expected_roi = {}
            risk_assessment = {}
            
            for platform in target_platforms:
                # Calculate platform score based on various factors
                score = await self._calculate_platform_score(
                    platform, content_data, historical_performance
                )
                platform_scores[platform] = score
                
                # Estimate expected ROI
                roi = await self._estimate_platform_roi(platform, content_data)
                expected_roi[platform] = roi
                
                # Assess risk level
                risk = self._assess_platform_risk(platform, content_data)
                risk_assessment[platform] = risk
            
            # Normalize scores and allocate budget
            total_score = sum(platform_scores.values())
            platform_allocations = {}
            
            if total_score > 0:
                for platform, score in platform_scores.items():
                    allocation_percentage = score / total_score
                    platform_allocations[platform] = total_budget * Decimal(str(allocation_percentage))
            else:
                # Equal allocation if no scores available
                equal_allocation = total_budget / len(target_platforms)
                for platform in target_platforms:
                    platform_allocations[platform] = equal_allocation
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                platform_allocations, expected_roi, risk_assessment
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_allocation_confidence(
                platform_scores, historical_performance
            )
            
            allocation = BudgetAllocation(
                content_id=content_data.get("id", ""),
                total_budget=total_budget,
                platform_allocations=platform_allocations,
                expected_roi=expected_roi,
                risk_assessment=risk_assessment,
                optimization_suggestions=optimization_suggestions,
                confidence_score=confidence_score,
                valid_until=datetime.now() + timedelta(days=7)
            )
            
            return allocation
            
        except Exception as e:
            logger.error(f"Error optimizing budget allocation: {str(e)}")
            raise

    async def _calculate_platform_score(
        self,
        platform: str,
        content_data: Dict[str, Any],
        historical_performance: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate scoring for platform based on content and historical data"""
        base_score = 1.0
        
        # Platform-content type alignment
        content_type = content_data.get("type", "")
        platform_content_scores = {
            "spotify": {"music": 0.95, "audio": 0.90, "podcast": 0.85},
            "youtube": {"video": 0.95, "music": 0.80, "podcast": 0.75},
            "instagram": {"image": 0.95, "video": 0.85, "story": 0.90},
            "tiktok": {"video": 0.95, "music": 0.80},
            "pinterest": {"image": 0.95, "art": 0.90}
        }
        
        content_score = platform_content_scores.get(platform, {}).get(content_type, 0.5)
        
        # Historical performance modifier
        historical_modifier = 1.0
        if historical_performance and platform in historical_performance:
            historical_roi = historical_performance[platform].get("average_roi", 0)
            historical_modifier = max(0.1, min(2.0, historical_roi / 100))
        
        # Creator audience size modifier
        audience_size = content_data.get("creator_followers", {}).get(platform, 0)
        audience_modifier = min(2.0, max(0.5, audience_size / 10000))
        
        final_score = base_score * content_score * historical_modifier * audience_modifier
        return max(0.1, min(5.0, final_score))

    async def _estimate_platform_roi(
        self,
        platform: str,
        content_data: Dict[str, Any]
    ) -> float:
        """Estimate expected ROI for platform"""
        # Baseline ROI estimates by platform
        baseline_roi = {
            "spotify": 25.0,
            "youtube": 35.0,
            "instagram": 30.0,
            "tiktok": 40.0,
            "pinterest": 20.0,
            "bandcamp": 45.0,
            "patreon": 60.0
        }
        
        base_roi = baseline_roi.get(platform, 25.0)
        
        # Adjust based on content quality and creator metrics
        quality_score = content_data.get("quality_score", 0.5)
        creator_engagement = content_data.get("creator_engagement_rate", 0.05)
        
        quality_modifier = quality_score
        engagement_modifier = min(2.0, creator_engagement * 20)
        
        estimated_roi = base_roi * quality_modifier * engagement_modifier
        return max(5.0, min(200.0, estimated_roi))

    def _assess_platform_risk(self, platform: str, content_data: Dict[str, Any]) -> str:
        """Assess risk level for platform investment"""
        # Platform risk factors
        platform_risks = {
            "spotify": "low",
            "youtube": "medium", 
            "instagram": "medium",
            "tiktok": "high",
            "pinterest": "low",
            "bandcamp": "low",
            "patreon": "low"
        }
        
        base_risk = platform_risks.get(platform, "medium")
        
        # Adjust based on content factors
        content_type = content_data.get("type", "")
        if content_type in ["adult", "controversial"]:
            risk_levels = {"low": "medium", "medium": "high", "high": "high"}
            base_risk = risk_levels.get(base_risk, "high")
        
        return base_risk

    def _generate_optimization_suggestions(
        self,
        allocations: Dict[str, Decimal],
        expected_roi: Dict[str, float],
        risk_assessment: Dict[str, str]
    ) -> List[str]:
        """Generate optimization suggestions based on allocation analysis"""
        suggestions = []
        
        # Find highest ROI platform
        best_roi_platform = max(expected_roi.keys(), key=lambda x: expected_roi[x])
        suggestions.append(f"Consider increasing allocation to {best_roi_platform} (highest expected ROI: {expected_roi[best_roi_platform]:.1f}%)")
        
        # Risk diversification
        high_risk_platforms = [p for p, risk in risk_assessment.items() if risk == "high"]
        if high_risk_platforms:
            suggestions.append(f"Monitor high-risk platforms closely: {', '.join(high_risk_platforms)}")
        
        # Budget concentration
        total_budget = sum(allocations.values())
        max_allocation = max(allocations.values())
        if max_allocation / total_budget > Decimal("0.6"):
            suggestions.append("Consider diversifying budget allocation to reduce concentration risk")
        
        return suggestions

    def _calculate_allocation_confidence(
        self,
        platform_scores: Dict[str, float],
        historical_performance: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for budget allocation"""
        base_confidence = 0.6
        
        # Increase confidence if we have historical data
        if historical_performance:
            base_confidence += 0.2
        
        # Increase confidence if platform scores are well-differentiated
        score_variance = np.var(list(platform_scores.values())) if platform_scores else 0
        variance_modifier = min(0.2, score_variance / 10)
        
        total_confidence = base_confidence + variance_modifier
        return max(0.3, min(0.95, total_confidence))

    async def generate_consolidated_report(
        self,
        creator_id: str,
        period_start: datetime,
        period_end: datetime,
        base_currency: Currency = Currency.USD
    ) -> ConsolidatedReport:
        """
        Generate comprehensive consolidated revenue report
        
        Args:
            creator_id: Creator identifier
            period_start: Report period start
            period_end: Report period end
            base_currency: Currency for consolidation
            
        Returns:
            ConsolidatedReport: Comprehensive revenue report
        """
        try:
            # Filter records for creator and period
            creator_records = [
                r for r in self.revenue_records
                if r.creator_id == creator_id
                and period_start <= r.transaction_date <= period_end
            ]
            
            if not creator_records:
                return ConsolidatedReport(
                    report_id=f"report_{uuid.uuid4().hex[:8]}",
                    creator_id=creator_id,
                    period_start=period_start,
                    period_end=period_end,
                    total_gross_revenue=Decimal("0"),
                    total_net_revenue=Decimal("0"),
                    total_platform_fees=Decimal("0"),
                    currency=base_currency,
                    platform_breakdown={},
                    content_breakdown={},
                    revenue_trends={},
                    top_performing_content=[],
                    growth_rate=0.0,
                    projections={}
                )
            
            # Convert all amounts to base currency
            converted_records = []
            for record in creator_records:
                converted_record = await self._convert_currency(record, base_currency)
                converted_records.append(converted_record)
            
            # Calculate totals
            total_gross_revenue = sum(r.gross_amount for r in converted_records)
            total_net_revenue = sum(r.net_amount for r in converted_records)
            total_platform_fees = sum(r.platform_fee for r in converted_records)
            
            # Calculate platform breakdown
            platform_breakdown = {}
            platforms = set(r.platform for r in converted_records)
            
            for platform in platforms:
                platform_metrics = await self.calculate_platform_metrics(
                    platform, period_start, period_end, creator_id
                )
                platform_breakdown[platform] = platform_metrics
            
            # Calculate content breakdown
            content_breakdown = {}
            for record in converted_records:
                if record.content_id not in content_breakdown:
                    content_breakdown[record.content_id] = Decimal("0")
                content_breakdown[record.content_id] += record.net_amount
            
            # Calculate top performing content
            top_performing_content = sorted(
                content_breakdown.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Calculate revenue trends (daily aggregation)
            revenue_trends = self._calculate_revenue_trends(converted_records, period_start, period_end)
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(creator_id, period_start, period_end)
            
            # Generate projections
            projections = await self._generate_revenue_projections(converted_records)
            
            report = ConsolidatedReport(
                report_id=f"report_{uuid.uuid4().hex[:8]}",
                creator_id=creator_id,
                period_start=period_start,
                period_end=period_end,
                total_gross_revenue=total_gross_revenue,
                total_net_revenue=total_net_revenue,
                total_platform_fees=total_platform_fees,
                currency=base_currency,
                platform_breakdown=platform_breakdown,
                content_breakdown=content_breakdown,
                revenue_trends=revenue_trends,
                top_performing_content=top_performing_content,
                growth_rate=growth_rate,
                projections=projections
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating consolidated report: {str(e)}")
            raise

    async def _convert_currency(self, record: RevenueRecord, target_currency: Currency) -> RevenueRecord:
        """Convert revenue record to target currency"""
        if record.currency == target_currency:
            return record
        
        # Get exchange rate
        rate_key = (record.currency, target_currency)
        if rate_key in self.exchange_rates:
            rate = self.exchange_rates[rate_key]
        else:
            # Use default rate or API call
            rate = Decimal("1.0")
        
        # Create converted record
        converted_record = RevenueRecord(
            record_id=record.record_id,
            stream_id=record.stream_id,
            platform=record.platform,
            content_id=record.content_id,
            creator_id=record.creator_id,
            revenue_type=record.revenue_type,
            gross_amount=record.gross_amount * rate,
            platform_fee=record.platform_fee * rate,
            net_amount=record.net_amount * rate,
            currency=target_currency,
            units_sold=record.units_sold,
            transaction_date=record.transaction_date,
            payment_date=record.payment_date,
            status=record.status,
            metadata=record.metadata
        )
        
        return converted_record

    def _calculate_revenue_trends(
        self,
        records: List[RevenueRecord],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, List[Tuple[datetime, Decimal]]]:
        """Calculate daily revenue trends"""
        trends = {"daily_revenue": [], "cumulative_revenue": []}
        
        # Create daily aggregation
        daily_revenue = {}
        current_date = period_start.date()
        end_date = period_end.date()
        
        while current_date <= end_date:
            daily_revenue[current_date] = Decimal("0")
            current_date += timedelta(days=1)
        
        # Aggregate daily revenue
        for record in records:
            date = record.transaction_date.date()
            if date in daily_revenue:
                daily_revenue[date] += record.net_amount
        
        # Build trends
        cumulative = Decimal("0")
        for date in sorted(daily_revenue.keys()):
            daily_amount = daily_revenue[date]
            cumulative += daily_amount
            
            date_dt = datetime.combine(date, datetime.min.time())
            trends["daily_revenue"].append((date_dt, daily_amount))
            trends["cumulative_revenue"].append((date_dt, cumulative))
        
        return trends

    async def _calculate_growth_rate(
        self,
        creator_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> float:
        """Calculate revenue growth rate compared to previous period"""
        # Get previous period data
        period_length = period_end - period_start
        previous_start = period_start - period_length
        previous_end = period_start
        
        current_records = [
            r for r in self.revenue_records
            if r.creator_id == creator_id
            and period_start <= r.transaction_date <= period_end
        ]
        
        previous_records = [
            r for r in self.revenue_records
            if r.creator_id == creator_id
            and previous_start <= r.transaction_date <= previous_end
        ]
        
        current_revenue = sum(r.net_amount for r in current_records)
        previous_revenue = sum(r.net_amount for r in previous_records)
        
        if previous_revenue > 0:
            growth_rate = float(((current_revenue - previous_revenue) / previous_revenue) * 100)
        else:
            growth_rate = 100.0 if current_revenue > 0 else 0.0
        
        return growth_rate

    async def _generate_revenue_projections(
        self,
        records: List[RevenueRecord]
    ) -> Dict[str, Decimal]:
        """Generate revenue projections based on historical data"""
        if not records:
            return {"next_month": Decimal("0"), "next_quarter": Decimal("0")}
        
        # Simple trend-based projection
        recent_records = [r for r in records if r.transaction_date >= datetime.now() - timedelta(days=30)]
        monthly_average = sum(r.net_amount for r in recent_records) if recent_records else Decimal("0")
        
        projections = {
            "next_month": monthly_average,
            "next_quarter": monthly_average * 3,
            "next_year": monthly_average * 12
        }
        
        return projections

    async def get_payment_summary(
        self,
        creator_id: str,
        payment_period: str = "monthly"
    ) -> Dict[str, Any]:
        """Get summary of pending and processed payments"""
        creator_records = [r for r in self.revenue_records if r.creator_id == creator_id]
        
        # Group by platform and payment status
        pending_payments = {}
        processed_payments = {}
        
        for record in creator_records:
            platform = record.platform
            
            if record.status == RevenueStatus.PENDING:
                if platform not in pending_payments:
                    pending_payments[platform] = {"amount": Decimal("0"), "count": 0}
                pending_payments[platform]["amount"] += record.net_amount
                pending_payments[platform]["count"] += 1
            
            elif record.status == RevenueStatus.PAID:
                if platform not in processed_payments:
                    processed_payments[platform] = {"amount": Decimal("0"), "count": 0}
                processed_payments[platform]["amount"] += record.net_amount
                processed_payments[platform]["count"] += 1
        
        return {
            "creator_id": creator_id,
            "pending_payments": pending_payments,
            "processed_payments": processed_payments,
            "next_payment_date": self._calculate_next_payment_date(payment_period),
            "total_pending": sum(p["amount"] for p in pending_payments.values()),
            "total_processed": sum(p["amount"] for p in processed_payments.values())
        }

    def _calculate_next_payment_date(self, payment_period: str) -> datetime:
        """Calculate next payment date based on payment period"""
        now = datetime.now()
        
        if payment_period == "weekly":
            days_ahead = 7 - now.weekday()
            return now + timedelta(days=days_ahead)
        elif payment_period == "monthly":
            if now.day <= 15:
                return now.replace(day=15)
            else:
                next_month = now.replace(day=28) + timedelta(days=4)
                return next_month.replace(day=1)
        else:
            return now + timedelta(days=30)