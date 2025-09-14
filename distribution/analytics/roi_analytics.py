"""
ROI Analytics Engine
===================

Enterprise-grade ROI (Return on Investment) analytics for content monetization.
Comprehensive tracking and analysis of financial performance across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import json
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

class RevenueSource(Enum):
    """Revenue source types"""
    ADVERTISING = "advertising"
    SPONSORSHIP = "sponsorship"
    AFFILIATE = "affiliate"
    MERCHANDISE = "merchandise"
    SUBSCRIPTION = "subscription"
    DONATIONS = "donations"
    LICENSING = "licensing"
    DIRECT_SALES = "direct_sales"
    PLATFORM_REVENUE = "platform_revenue"
    BRAND_PARTNERSHIP = "brand_partnership"

class CostCategory(Enum):
    """Cost category types"""
    PRODUCTION = "production"
    PLATFORM_FEES = "platform_fees"
    ADVERTISING_SPEND = "advertising_spend"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    PERSONNEL = "personnel"
    DISTRIBUTION = "distribution"
    MARKETING = "marketing"
    OVERHEAD = "overhead"
    COMPLIANCE = "compliance"

class ROIMetricType(Enum):
    """ROI metric types"""
    BASIC_ROI = "basic_roi"                    # (Revenue - Cost) / Cost
    ROAS = "roas"                             # Return on Ad Spend
    CLV = "clv"                               # Customer Lifetime Value
    CAC = "cac"                               # Customer Acquisition Cost
    LTV_CAC_RATIO = "ltv_cac_ratio"          # LTV to CAC ratio
    ENGAGEMENT_VALUE = "engagement_value"     # Revenue per engagement
    REACH_VALUE = "reach_value"               # Revenue per reach
    CONVERSION_VALUE = "conversion_value"     # Revenue per conversion

@dataclass
class RevenueEntry:
    """Revenue tracking entry"""
    id: str
    amount: Decimal
    source: RevenueSource
    platform: str
    content_id: Optional[str] = None
    campaign_id: Optional[str] = None
    currency: str = "USD"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CostEntry:
    """Cost tracking entry"""
    id: str
    amount: Decimal
    category: CostCategory
    platform: str
    content_id: Optional[str] = None
    campaign_id: Optional[str] = None
    currency: str = "USD"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    is_recurring: bool = False
    recurrence_period: Optional[str] = None  # "monthly", "weekly", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ROIMetrics:
    """ROI calculation results"""
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    total_costs: Decimal
    net_profit: Decimal
    roi_percentage: float
    roas: Optional[float] = None
    profit_margin: float = 0.0
    revenue_by_source: Dict[RevenueSource, Decimal] = field(default_factory=dict)
    costs_by_category: Dict[CostCategory, Decimal] = field(default_factory=dict)
    platform_performance: Dict[str, Dict[str, Decimal]] = field(default_factory=dict)

@dataclass
class ContentROI:
    """ROI analysis for specific content"""
    content_id: str
    title: str
    platform: str
    total_revenue: Decimal
    total_costs: Decimal
    net_profit: Decimal
    roi_percentage: float
    engagement_value: float  # Revenue per engagement
    reach_value: float       # Revenue per reach
    views: int = 0
    engagements: int = 0
    conversions: int = 0
    production_date: Optional[datetime] = None
    metrics_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class CampaignROI:
    """ROI analysis for marketing campaigns"""
    campaign_id: str
    campaign_name: str
    total_spend: Decimal
    total_revenue: Decimal
    roi_percentage: float
    roas: float
    cac: float  # Customer Acquisition Cost
    clv: float  # Customer Lifetime Value
    ltv_cac_ratio: float
    conversion_rate: float
    customers_acquired: int = 0
    campaign_start: Optional[datetime] = None
    campaign_end: Optional[datetime] = None

class ROIAnalyticsEngine:
    """Main ROI analytics engine"""
    
    def __init__(self) -> None:
        self.revenue_entries: List[RevenueEntry] = []
        self.cost_entries: List[CostEntry] = []
        self.content_performance: Dict[str, ContentROI] = {}
        self.campaign_performance: Dict[str, CampaignROI] = {}
        
        # Exchange rates (simplified - in production, use real-time rates)
        self.exchange_rates = {
            "USD": Decimal("1.0"),
            "EUR": Decimal("0.85"),
            "GBP": Decimal("0.75"),
            "CAD": Decimal("1.25"),
            "AUD": Decimal("1.35")
        }
        
        # Configuration
        self.base_currency = "USD"
        self.precision = 2
    
    async def add_revenue(self, entry: RevenueEntry) -> str:
        """Add revenue entry"""
        try:
            # Convert to base currency if needed
            if entry.currency != self.base_currency:
                entry.amount = await self._convert_currency(
                    entry.amount, entry.currency, self.base_currency
                )
                entry.currency = self.base_currency
            
            # Round to specified precision
            entry.amount = entry.amount.quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            self.revenue_entries.append(entry)
            
            # Update content performance if applicable
            if entry.content_id:
                await self._update_content_roi(entry.content_id)
            
            # Update campaign performance if applicable
            if entry.campaign_id:
                await self._update_campaign_roi(entry.campaign_id)
            
            logger.info(f"Added revenue entry: {entry.amount} {entry.currency} from {entry.source.value}")
            
            return entry.id
            
        except Exception as e:
            logger.error(f"Failed to add revenue entry: {e}")
            raise
    
    async def add_cost(self, entry: CostEntry) -> str:
        """Add cost entry"""
        try:
            # Convert to base currency if needed
            if entry.currency != self.base_currency:
                entry.amount = await self._convert_currency(
                    entry.amount, entry.currency, self.base_currency
                )
                entry.currency = self.base_currency
            
            # Round to specified precision
            entry.amount = entry.amount.quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            self.cost_entries.append(entry)
            
            # Update content performance if applicable
            if entry.content_id:
                await self._update_content_roi(entry.content_id)
            
            # Update campaign performance if applicable
            if entry.campaign_id:
                await self._update_campaign_roi(entry.campaign_id)
            
            logger.info(f"Added cost entry: {entry.amount} {entry.currency} for {entry.category.value}")
            
            return entry.id
            
        except Exception as e:
            logger.error(f"Failed to add cost entry: {e}")
            raise
    
    async def calculate_roi(
        self,
        start_date: datetime,
        end_date: datetime,
        platform_filter: Optional[str] = None,
        content_filter: Optional[str] = None
    ) -> ROIMetrics:
        """Calculate ROI for specified period"""
        try:
            # Filter entries by date range
            revenue_entries = [
                entry for entry in self.revenue_entries
                if start_date <= entry.timestamp <= end_date
            ]
            
            cost_entries = [
                entry for entry in self.cost_entries
                if start_date <= entry.timestamp <= end_date
            ]
            
            # Apply additional filters
            if platform_filter:
                revenue_entries = [e for e in revenue_entries if e.platform == platform_filter]
                cost_entries = [e for e in cost_entries if e.platform == platform_filter]
            
            if content_filter:
                revenue_entries = [e for e in revenue_entries if e.content_id == content_filter]
                cost_entries = [e for e in cost_entries if e.content_id == content_filter]
            
            # Calculate totals
            total_revenue = sum(entry.amount for entry in revenue_entries)
            total_costs = sum(entry.amount for entry in cost_entries)
            net_profit = total_revenue - total_costs
            
            # Calculate ROI percentage
            if total_costs > 0:
                roi_percentage = float((net_profit / total_costs) * 100)
            else:
                roi_percentage = 0.0 if total_revenue == 0 else float('inf')
            
            # Calculate profit margin
            if total_revenue > 0:
                profit_margin = float((net_profit / total_revenue) * 100)
            else:
                profit_margin = 0.0
            
            # Calculate ROAS (for advertising spend)
            ad_costs = sum(
                entry.amount for entry in cost_entries
                if entry.category == CostCategory.ADVERTISING_SPEND
            )
            
            roas = float(total_revenue / ad_costs) if ad_costs > 0 else None
            
            # Group revenue by source
            revenue_by_source = {}
            for entry in revenue_entries:
                source = entry.source
                revenue_by_source[source] = revenue_by_source.get(source, Decimal('0')) + entry.amount
            
            # Group costs by category
            costs_by_category = {}
            for entry in cost_entries:
                category = entry.category
                costs_by_category[category] = costs_by_category.get(category, Decimal('0')) + entry.amount
            
            # Calculate platform performance
            platform_performance = {}
            platforms = set(entry.platform for entry in revenue_entries + cost_entries)
            
            for platform in platforms:
                platform_revenue = sum(
                    entry.amount for entry in revenue_entries 
                    if entry.platform == platform
                )
                platform_costs = sum(
                    entry.amount for entry in cost_entries 
                    if entry.platform == platform
                )
                
                platform_performance[platform] = {
                    "revenue": platform_revenue,
                    "costs": platform_costs,
                    "profit": platform_revenue - platform_costs
                }
            
            return ROIMetrics(
                period_start=start_date,
                period_end=end_date,
                total_revenue=total_revenue,
                total_costs=total_costs,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                roas=roas,
                profit_margin=profit_margin,
                revenue_by_source=revenue_by_source,
                costs_by_category=costs_by_category,
                platform_performance=platform_performance
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate ROI: {e}")
            raise
    
    async def get_content_roi(self, content_id: str) -> Optional[ContentROI]:
        """Get ROI analysis for specific content"""
        return self.content_performance.get(content_id)
    
    async def get_top_performing_content(
        self,
        metric: str = "roi_percentage",
        limit: int = 10,
        min_revenue: Optional[Decimal] = None
    ) -> List[ContentROI]:
        """Get top performing content by specified metric"""
        try:
            content_list = list(self.content_performance.values())
            
            # Filter by minimum revenue if specified
            if min_revenue:
                content_list = [c for c in content_list if c.total_revenue >= min_revenue]
            
            # Sort by specified metric
            if metric == "roi_percentage":
                content_list.sort(key=lambda x: x.roi_percentage, reverse=True)
            elif metric == "total_revenue":
                content_list.sort(key=lambda x: x.total_revenue, reverse=True)
            elif metric == "net_profit":
                content_list.sort(key=lambda x: x.net_profit, reverse=True)
            elif metric == "engagement_value":
                content_list.sort(key=lambda x: x.engagement_value, reverse=True)
            elif metric == "reach_value":
                content_list.sort(key=lambda x: x.reach_value, reverse=True)
            
            return content_list[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top performing content: {e}")
            return []
    
    async def analyze_revenue_trends(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "daily"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze revenue trends over time"""
        try:
            # Filter revenue entries
            revenue_entries = [
                entry for entry in self.revenue_entries
                if start_date <= entry.timestamp <= end_date
            ]
            
            # Group by time period
            time_groups = {}
            
            for entry in revenue_entries:
                if granularity == "daily":
                    time_key = entry.timestamp.date().isoformat()
                elif granularity == "weekly":
                    # Get Monday of the week
                    monday = entry.timestamp.date() - timedelta(days=entry.timestamp.weekday())
                    time_key = monday.isoformat()
                elif granularity == "monthly":
                    time_key = entry.timestamp.strftime("%Y-%m")
                else:
                    time_key = entry.timestamp.date().isoformat()
                
                if time_key not in time_groups:
                    time_groups[time_key] = {
                        "total_revenue": Decimal('0'),
                        "by_source": {},
                        "by_platform": {}
                    }
                
                time_groups[time_key]["total_revenue"] += entry.amount
                
                # Group by source
                source = entry.source
                if source not in time_groups[time_key]["by_source"]:
                    time_groups[time_key]["by_source"][source] = Decimal('0')
                time_groups[time_key]["by_source"][source] += entry.amount
                
                # Group by platform
                platform = entry.platform
                if platform not in time_groups[time_key]["by_platform"]:
                    time_groups[time_key]["by_platform"][platform] = Decimal('0')
                time_groups[time_key]["by_platform"][platform] += entry.amount
            
            # Convert to list format
            trend_data = []
            for time_key in sorted(time_groups.keys()):
                data = time_groups[time_key]
                trend_data.append({
                    "period": time_key,
                    "total_revenue": float(data["total_revenue"]),
                    "by_source": {source.value: float(amount) for source, amount in data["by_source"].items()},
                    "by_platform": {platform: float(amount) for platform, amount in data["by_platform"].items()}
                })
            
            return {
                "granularity": granularity,
                "data": trend_data
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze revenue trends: {e}")
            return {"granularity": granularity, "data": []}
    
    async def calculate_customer_metrics(
        self,
        customer_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate customer-related ROI metrics"""
        try:
            if not customer_data:
                return {
                    "cac": 0.0,
                    "clv": 0.0,
                    "ltv_cac_ratio": 0.0,
                    "churn_rate": 0.0
                }
            
            # Calculate Customer Acquisition Cost (CAC)
            total_marketing_costs = sum(
                entry.amount for entry in self.cost_entries
                if entry.category in [CostCategory.MARKETING, CostCategory.ADVERTISING_SPEND]
            )
            
            total_customers_acquired = len(customer_data)
            cac = float(total_marketing_costs / total_customers_acquired) if total_customers_acquired > 0 else 0.0
            
            # Calculate Customer Lifetime Value (CLV)
            total_customer_revenue = sum(customer.get("total_revenue", 0) for customer in customer_data)
            average_customer_lifespan = sum(customer.get("lifespan_months", 12) for customer in customer_data) / len(customer_data)
            
            clv = float(total_customer_revenue / total_customers_acquired) if total_customers_acquired > 0 else 0.0
            
            # Calculate LTV:CAC ratio
            ltv_cac_ratio = clv / cac if cac > 0 else 0.0
            
            # Calculate churn rate
            churned_customers = sum(1 for customer in customer_data if customer.get("churned", False))
            churn_rate = (churned_customers / total_customers_acquired) * 100 if total_customers_acquired > 0 else 0.0
            
            return {
                "cac": cac,
                "clv": clv,
                "ltv_cac_ratio": ltv_cac_ratio,
                "churn_rate": churn_rate,
                "total_customers": total_customers_acquired,
                "average_lifespan_months": average_customer_lifespan
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate customer metrics: {e}")
            return {}
    
    async def forecast_roi(
        self,
        forecast_period_days: int,
        confidence_level: float = 0.8
    ) -> Dict[str, Any]:
        """Forecast ROI for future period"""
        try:
            if len(self.revenue_entries) < 30:  # Need at least 30 days of data
                return {
                    "error": "Insufficient historical data for forecasting",
                    "required_days": 30,
                    "available_days": len(self.revenue_entries)
                }
            
            # Calculate historical averages (last 30 days)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            recent_revenue = [
                entry for entry in self.revenue_entries
                if entry.timestamp >= cutoff_date
            ]
            recent_costs = [
                entry for entry in self.cost_entries
                if entry.timestamp >= cutoff_date
            ]
            
            # Calculate daily averages
            total_days = 30
            avg_daily_revenue = sum(entry.amount for entry in recent_revenue) / total_days
            avg_daily_costs = sum(entry.amount for entry in recent_costs) / total_days
            
            # Forecast totals
            forecast_revenue = avg_daily_revenue * forecast_period_days
            forecast_costs = avg_daily_costs * forecast_period_days
            forecast_profit = forecast_revenue - forecast_costs
            
            # Calculate forecast ROI
            forecast_roi = float((forecast_profit / forecast_costs) * 100) if forecast_costs > 0 else 0.0
            
            # Calculate confidence intervals (simplified)
            revenue_variance = self._calculate_variance([float(entry.amount) for entry in recent_revenue])
            cost_variance = self._calculate_variance([float(entry.amount) for entry in recent_costs])
            
            # Confidence intervals
            revenue_margin = (revenue_variance ** 0.5) * forecast_period_days * (1 - confidence_level)
            cost_margin = (cost_variance ** 0.5) * forecast_period_days * (1 - confidence_level)
            
            return {
                "forecast_period_days": forecast_period_days,
                "confidence_level": confidence_level,
                "forecast": {
                    "revenue": {
                        "predicted": float(forecast_revenue),
                        "min": float(forecast_revenue - revenue_margin),
                        "max": float(forecast_revenue + revenue_margin)
                    },
                    "costs": {
                        "predicted": float(forecast_costs),
                        "min": float(forecast_costs - cost_margin),
                        "max": float(forecast_costs + cost_margin)
                    },
                    "profit": {
                        "predicted": float(forecast_profit),
                        "min": float(forecast_profit - revenue_margin - cost_margin),
                        "max": float(forecast_profit + revenue_margin + cost_margin)
                    },
                    "roi_percentage": forecast_roi
                },
                "based_on": {
                    "historical_days": 30,
                    "avg_daily_revenue": float(avg_daily_revenue),
                    "avg_daily_costs": float(avg_daily_costs)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to forecast ROI: {e}")
            return {"error": str(e)}
    
    async def _update_content_roi(self, content_id -> None: str) -> None:
        """Update ROI metrics for specific content"""
        try:
            # Get all revenue and costs for this content
            content_revenue = sum(
                entry.amount for entry in self.revenue_entries
                if entry.content_id == content_id
            )
            
            content_costs = sum(
                entry.amount for entry in self.cost_entries
                if entry.content_id == content_id
            )
            
            net_profit = content_revenue - content_costs
            roi_percentage = float((net_profit / content_costs) * 100) if content_costs > 0 else 0.0
            
            # Get content metadata (simplified - in production, fetch from content system)
            content_entries = [e for e in self.revenue_entries if e.content_id == content_id]
            platform = content_entries[0].platform if content_entries else "unknown"
            
            # Calculate engagement and reach values (placeholder)
            engagement_value = float(content_revenue / 1000) if content_revenue > 0 else 0.0  # Simplified
            reach_value = float(content_revenue / 10000) if content_revenue > 0 else 0.0      # Simplified
            
            # Update or create content ROI record
            self.content_performance[content_id] = ContentROI(
                content_id=content_id,
                title=f"Content {content_id}",  # Placeholder
                platform=platform,
                total_revenue=content_revenue,
                total_costs=content_costs,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                engagement_value=engagement_value,
                reach_value=reach_value
            )
            
        except Exception as e:
            logger.error(f"Failed to update content ROI for {content_id}: {e}")
    
    async def _update_campaign_roi(self, campaign_id -> None: str) -> None:
        """Update ROI metrics for specific campaign"""
        try:
            # Get all revenue and costs for this campaign
            campaign_revenue = sum(
                entry.amount for entry in self.revenue_entries
                if entry.campaign_id == campaign_id
            )
            
            campaign_costs = sum(
                entry.amount for entry in self.cost_entries
                if entry.campaign_id == campaign_id
            )
            
            roi_percentage = float(((campaign_revenue - campaign_costs) / campaign_costs) * 100) if campaign_costs > 0 else 0.0
            roas = float(campaign_revenue / campaign_costs) if campaign_costs > 0 else 0.0
            
            # Placeholder values (in production, integrate with customer data)
            cac = float(campaign_costs / 10) if campaign_costs > 0 else 0.0  # Simplified
            clv = float(campaign_revenue / 5) if campaign_revenue > 0 else 0.0  # Simplified
            ltv_cac_ratio = clv / cac if cac > 0 else 0.0
            conversion_rate = 5.0  # Placeholder
            
            # Update or create campaign ROI record
            self.campaign_performance[campaign_id] = CampaignROI(
                campaign_id=campaign_id,
                campaign_name=f"Campaign {campaign_id}",
                total_spend=campaign_costs,
                total_revenue=campaign_revenue,
                roi_percentage=roi_percentage,
                roas=roas,
                cac=cac,
                clv=clv,
                ltv_cac_ratio=ltv_cac_ratio,
                conversion_rate=conversion_rate
            )
            
        except Exception as e:
            logger.error(f"Failed to update campaign ROI for {campaign_id}: {e}")
    
    async def _convert_currency(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """Convert currency (simplified - use real exchange rates in production)"""
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first, then to target currency
        usd_amount = amount / self.exchange_rates.get(from_currency, Decimal("1.0"))
        converted_amount = usd_amount * self.exchange_rates.get(to_currency, Decimal("1.0"))
        
        return converted_amount
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        return variance
    
    async def export_roi_report(
        self,
        start_date: datetime,
        end_date: datetime,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """Export comprehensive ROI report"""
        try:
            # Calculate overall ROI
            roi_metrics = await self.calculate_roi(start_date, end_date)
            
            # Get revenue trends
            revenue_trends = await self.analyze_revenue_trends(start_date, end_date)
            
            # Get top performing content
            top_content = await self.get_top_performing_content(limit=5)
            
            report = {
                "report_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "summary": {
                    "total_revenue": float(roi_metrics.total_revenue),
                    "total_costs": float(roi_metrics.total_costs),
                    "net_profit": float(roi_metrics.net_profit),
                    "roi_percentage": roi_metrics.roi_percentage,
                    "profit_margin": roi_metrics.profit_margin,
                    "roas": roi_metrics.roas
                },
                "revenue_breakdown": {
                    source.value: float(amount) 
                    for source, amount in roi_metrics.revenue_by_source.items()
                },
                "cost_breakdown": {
                    category.value: float(amount) 
                    for category, amount in roi_metrics.costs_by_category.items()
                },
                "platform_performance": {
                    platform: {
                        "revenue": float(data["revenue"]),
                        "costs": float(data["costs"]),
                        "profit": float(data["profit"])
                    }
                    for platform, data in roi_metrics.platform_performance.items()
                },
                "trends": revenue_trends,
                "top_content": [
                    {
                        "content_id": content.content_id,
                        "platform": content.platform,
                        "revenue": float(content.total_revenue),
                        "roi_percentage": content.roi_percentage
                    }
                    for content in top_content
                ]
            }
            
            if include_details:
                report["detailed_entries"] = {
                    "revenue_count": len(self.revenue_entries),
                    "cost_count": len(self.cost_entries),
                    "content_analyzed": len(self.content_performance),
                    "campaigns_analyzed": len(self.campaign_performance)
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to export ROI report: {e}")
            return {"error": str(e)}


# Export main components
__all__ = [
    "ROIAnalyticsEngine",
    "RevenueEntry",
    "CostEntry",
    "ROIMetrics",
    "ContentROI",
    "CampaignROI",
    "RevenueSource",
    "CostCategory",
    "ROIMetricType"
]