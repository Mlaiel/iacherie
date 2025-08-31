"""Performance Analytics Engine
Advanced performance tracking, insights generation and optimization recommendations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, extract

from ...database.models import User, RevenueRecord, ContentLicense, Payout
from .platform_revenue_integration import PlatformType, RevenueType


class MetricType(Enum):
    """Types of performance metrics"""
    REVENUE = "revenue"
    GROWTH = "growth"
    ENGAGEMENT = "engagement"
    EFFICIENCY = "efficiency"
    CONVERSION = "conversion"
    RETENTION = "retention"
    QUALITY = "quality"


class TimeGranularity(Enum):
    """Time granularity for analytics"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class InsightType(Enum):
    """Types of insights generated"""
    OPPORTUNITY = "opportunity"
    WARNING = "warning"
    RECOMMENDATION = "recommendation"
    TREND = "trend"
    ANOMALY = "anomaly"
    OPTIMIZATION = "optimization"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    platform: Optional[str] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_type": self.metric_type.value,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "platform": self.platform,
            "content_id": self.content_id,
            "metadata": self.metadata
        }


@dataclass
class PerformanceInsight:
    """Generated performance insight"""
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    importance_score: float  # 0-1
    actionable: bool
    related_metrics: List[str]
    recommendations: List[str] = field(default_factory=list)
    estimated_impact: Optional[Dict[str, float]] = None
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "insight_id": self.insight_id,
            "insight_type": self.insight_type.value,
            "title": self.title,
            "description": self.description,
            "importance_score": self.importance_score,
            "actionable": self.actionable,
            "related_metrics": self.related_metrics,
            "recommendations": self.recommendations,
            "estimated_impact": self.estimated_impact,
            "generated_at": self.generated_at.isoformat()
        }


@dataclass
class PerformanceBenchmark:
    """Performance benchmark data"""
    metric_type: MetricType
    platform: str
    industry_average: float
    top_quartile: float
    top_decile: float
    user_value: float
    percentile_rank: float
    
    def get_performance_tier(self) -> str:
        """Get performance tier classification"""
        if self.percentile_rank >= 90:
            return "EXCELLENT"
        elif self.percentile_rank >= 75:
            return "GOOD"
        elif self.percentile_rank >= 50:
            return "AVERAGE"
        elif self.percentile_rank >= 25:
            return "BELOW_AVERAGE"
        else:
            return "POOR"


class RevenueAnalyzer:
    """Advanced revenue analytics and insights"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def analyze_revenue_performance(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Comprehensive revenue performance analysis"""
        
        try:
            # Get revenue data
            revenue_data = await self._get_revenue_data(user_id, start_date, end_date, session)
            
            # Calculate key metrics
            metrics = await self._calculate_revenue_metrics(revenue_data)
            
            # Generate time series analysis
            time_series = await self._generate_revenue_time_series(revenue_data)
            
            # Platform performance breakdown
            platform_analysis = await self._analyze_platform_performance(revenue_data)
            
            # Growth analysis
            growth_analysis = await self._analyze_revenue_growth(revenue_data, user_id, session)
            
            # Forecasting
            forecasts = await self._generate_revenue_forecasts(revenue_data)
            
            # Performance insights
            insights = await self._generate_revenue_insights(metrics, platform_analysis, growth_analysis)
            
            return {
                "summary_metrics": metrics,
                "time_series": time_series,
                "platform_analysis": platform_analysis,
                "growth_analysis": growth_analysis,
                "forecasts": forecasts,
                "insights": [insight.to_dict() for insight in insights],
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Revenue analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def _get_revenue_data(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get revenue data for analysis"""
        
        result = await session.execute(
            select(RevenueRecord).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.date >= start_date,
                RevenueRecord.date <= end_date,
                RevenueRecord.status == "confirmed"
            ).order_by(RevenueRecord.date)
        )
        
        revenue_data = []
        for record in result.scalars():
            revenue_data.append({
                "date": record.date,
                "amount": float(record.amount),
                "currency": record.currency,
                "platform": record.platform,
                "source": record.source,
                "revenue_type": record.revenue_type,
                "views": record.views,
                "streams": record.streams,
                "engagement_rate": record.engagement_rate,
                "metadata": record.metadata or {}
            })
        
        return revenue_data
    
    async def _calculate_revenue_metrics(self, revenue_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate key revenue metrics"""
        
        if not revenue_data:
            return {}
        
        df = pd.DataFrame(revenue_data)
        
        total_revenue = df['amount'].sum()
        avg_daily_revenue = df.groupby(df['date'])['amount'].sum().mean()
        revenue_variance = df['amount'].var()
        revenue_std = df['amount'].std()
        
        # Revenue per view/stream
        total_views = df['views'].sum() if 'views' in df.columns and not df['views'].isna().all() else 0
        total_streams = df['streams'].sum() if 'streams' in df.columns and not df['streams'].isna().all() else 0
        
        revenue_per_view = total_revenue / total_views if total_views > 0 else 0
        revenue_per_stream = total_revenue / total_streams if total_streams > 0 else 0
        
        # Platform diversification (Herfindahl Index)
        platform_revenues = df.groupby('platform')['amount'].sum()
        platform_shares = platform_revenues / total_revenue
        diversification_index = 1 - (platform_shares ** 2).sum()
        
        return {
            "total_revenue": float(total_revenue),
            "average_daily_revenue": float(avg_daily_revenue),
            "revenue_variance": float(revenue_variance),
            "revenue_standard_deviation": float(revenue_std),
            "coefficient_of_variation": float(revenue_std / avg_daily_revenue) if avg_daily_revenue > 0 else 0,
            "revenue_per_view": float(revenue_per_view),
            "revenue_per_stream": float(revenue_per_stream),
            "platform_diversification_index": float(diversification_index),
            "number_of_platforms": len(platform_revenues),
            "days_with_revenue": len(df.groupby('date')),
            "total_views": int(total_views),
            "total_streams": int(total_streams)
        }
    
    async def _generate_revenue_time_series(self, revenue_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate time series data for revenue"""
        
        if not revenue_data:
            return []
        
        df = pd.DataFrame(revenue_data)
        daily_revenue = df.groupby('date')['amount'].sum().reset_index()
        
        # Calculate moving averages
        daily_revenue['ma_7'] = daily_revenue['amount'].rolling(window=7, min_periods=1).mean()
        daily_revenue['ma_30'] = daily_revenue['amount'].rolling(window=30, min_periods=1).mean()
        
        # Calculate growth rates
        daily_revenue['daily_growth'] = daily_revenue['amount'].pct_change()
        daily_revenue['weekly_growth'] = daily_revenue['ma_7'].pct_change(periods=7)
        
        time_series = []
        for _, row in daily_revenue.iterrows():
            time_series.append({
                "date": row['date'].isoformat() if hasattr(row['date'], 'isoformat') else str(row['date']),
                "revenue": float(row['amount']),
                "moving_average_7d": float(row['ma_7']),
                "moving_average_30d": float(row['ma_30']),
                "daily_growth_rate": float(row['daily_growth']) if not pd.isna(row['daily_growth']) else 0,
                "weekly_growth_rate": float(row['weekly_growth']) if not pd.isna(row['weekly_growth']) else 0
            })
        
        return time_series
    
    async def _analyze_platform_performance(self, revenue_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by platform"""
        
        if not revenue_data:
            return {}
        
        df = pd.DataFrame(revenue_data)
        
        platform_metrics = {}
        
        for platform in df['platform'].unique():
            platform_df = df[df['platform'] == platform]
            
            total_revenue = platform_df['amount'].sum()
            avg_revenue = platform_df['amount'].mean()
            revenue_share = total_revenue / df['amount'].sum() * 100
            
            # Performance metrics
            total_views = platform_df['views'].sum() if 'views' in platform_df.columns and not platform_df['views'].isna().all() else 0
            total_streams = platform_df['streams'].sum() if 'streams' in platform_df.columns and not platform_df['streams'].isna().all() else 0
            
            avg_engagement = platform_df['engagement_rate'].mean() if 'engagement_rate' in platform_df.columns and not platform_df['engagement_rate'].isna().all() else 0
            
            platform_metrics[platform] = {
                "total_revenue": float(total_revenue),
                "average_revenue": float(avg_revenue),
                "revenue_share_percentage": float(revenue_share),
                "total_views": int(total_views),
                "total_streams": int(total_streams),
                "revenue_per_view": float(total_revenue / total_views) if total_views > 0 else 0,
                "revenue_per_stream": float(total_revenue / total_streams) if total_streams > 0 else 0,
                "average_engagement_rate": float(avg_engagement),
                "transaction_count": len(platform_df),
                "days_active": len(platform_df.groupby('date'))
            }
        
        # Rank platforms by performance
        ranked_platforms = sorted(
            platform_metrics.items(),
            key=lambda x: x[1]['total_revenue'],
            reverse=True
        )
        
        return {
            "platform_metrics": platform_metrics,
            "ranked_platforms": [{"platform": p[0], **p[1]} for p in ranked_platforms],
            "top_platform": ranked_platforms[0][0] if ranked_platforms else None,
            "platform_count": len(platform_metrics)
        }
    
    async def _analyze_revenue_growth(
        self,
        revenue_data: List[Dict[str, Any]],
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze revenue growth patterns"""
        
        if not revenue_data:
            return {}
        
        df = pd.DataFrame(revenue_data)
        daily_revenue = df.groupby('date')['amount'].sum().reset_index()
        daily_revenue = daily_revenue.sort_values('date')
        
        # Calculate various growth metrics
        total_days = len(daily_revenue)
        if total_days < 2:
            return {"error": "Insufficient data for growth analysis"}
        
        first_day_revenue = daily_revenue.iloc[0]['amount']
        last_day_revenue = daily_revenue.iloc[-1]['amount']
        
        # Overall growth rate
        total_growth_rate = ((last_day_revenue / first_day_revenue) - 1) * 100 if first_day_revenue > 0 else 0
        
        # Average daily growth
        daily_revenue['growth_rate'] = daily_revenue['amount'].pct_change()
        avg_daily_growth = daily_revenue['growth_rate'].mean() * 100
        
        # Compound Annual Growth Rate (CAGR)
        years = total_days / 365.25
        cagr = ((last_day_revenue / first_day_revenue) ** (1/years) - 1) * 100 if years > 0 and first_day_revenue > 0 else 0
        
        # Growth consistency (lower variance is better)
        growth_consistency = 1 / (daily_revenue['growth_rate'].std() + 1)
        
        # Trend analysis using linear regression
        daily_revenue['day_number'] = range(len(daily_revenue))
        correlation = daily_revenue['day_number'].corr(daily_revenue['amount'])
        
        return {
            "total_growth_rate_percentage": float(total_growth_rate),
            "average_daily_growth_percentage": float(avg_daily_growth),
            "compound_annual_growth_rate": float(cagr),
            "growth_consistency_score": float(growth_consistency),
            "revenue_trend_correlation": float(correlation),
            "first_day_revenue": float(first_day_revenue),
            "last_day_revenue": float(last_day_revenue),
            "analysis_period_days": total_days,
            "growth_volatility": float(daily_revenue['growth_rate'].std()),
            "positive_growth_days": int((daily_revenue['growth_rate'] > 0).sum()),
            "negative_growth_days": int((daily_revenue['growth_rate'] < 0).sum())
        }
    
    async def _generate_revenue_forecasts(self, revenue_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate revenue forecasts using simple models"""
        
        if not revenue_data or len(revenue_data) < 7:
            return {"error": "Insufficient data for forecasting"}
        
        df = pd.DataFrame(revenue_data)
        daily_revenue = df.groupby('date')['amount'].sum().reset_index()
        daily_revenue = daily_revenue.sort_values('date')
        
        # Simple moving average forecast
        recent_avg = daily_revenue['amount'].tail(7).mean()
        
        # Linear trend forecast
        daily_revenue['day_number'] = range(len(daily_revenue))
        trend_slope = np.polyfit(daily_revenue['day_number'], daily_revenue['amount'], 1)[0]
        
        # Generate forecasts for next 30 days
        last_day_num = daily_revenue['day_number'].iloc[-1]
        forecasts = []
        
        for i in range(1, 31):  # Next 30 days
            forecast_date = daily_revenue['date'].iloc[-1] + timedelta(days=i)
            
            # Moving average forecast
            ma_forecast = recent_avg
            
            # Trend forecast
            trend_forecast = daily_revenue['amount'].iloc[-1] + (trend_slope * i)
            trend_forecast = max(0, trend_forecast)  # Don't forecast negative revenue
            
            # Combined forecast (weighted average)
            combined_forecast = (ma_forecast * 0.6) + (trend_forecast * 0.4)
            
            forecasts.append({
                "date": forecast_date.isoformat() if hasattr(forecast_date, 'isoformat') else str(forecast_date),
                "moving_average_forecast": float(ma_forecast),
                "trend_forecast": float(trend_forecast),
                "combined_forecast": float(combined_forecast),
                "confidence_level": max(0.3, 0.9 - (i * 0.02))  # Decreasing confidence
            })
        
        return {
            "forecasts": forecasts,
            "forecast_method": "moving_average_trend_combination",
            "base_period_days": len(daily_revenue),
            "recent_average": float(recent_avg),
            "trend_slope": float(trend_slope)
        }
    
    async def _generate_revenue_insights(
        self,
        metrics: Dict[str, float],
        platform_analysis: Dict[str, Any],
        growth_analysis: Dict[str, Any]
    ) -> List[PerformanceInsight]:
        """Generate actionable revenue insights"""
        
        insights = []
        
        # Revenue diversification insight
        diversification_index = metrics.get('platform_diversification_index', 0)
        if diversification_index < 0.5:
            insights.append(PerformanceInsight(
                insight_id="revenue_diversification_low",
                insight_type=InsightType.OPPORTUNITY,
                title="Low Revenue Diversification",
                description=f"Your revenue is concentrated on few platforms (diversification index: {diversification_index:.2f}). Consider expanding to more platforms.",
                importance_score=0.8,
                actionable=True,
                related_metrics=["platform_diversification_index", "number_of_platforms"],
                recommendations=[
                    "Explore content distribution on additional platforms",
                    "Analyze which platforms work best for your content type",
                    "Set up accounts on 2-3 new relevant platforms"
                ],
                estimated_impact={"revenue_increase": 15.0, "risk_reduction": 25.0}
            ))
        
        # Revenue per view optimization
        revenue_per_view = metrics.get('revenue_per_view', 0)
        if revenue_per_view > 0 and revenue_per_view < 0.001:  # Less than €0.001 per view
            insights.append(PerformanceInsight(
                insight_id="low_revenue_per_view",
                insight_type=InsightType.OPTIMIZATION,
                title="Low Revenue Per View",
                description=f"Your revenue per view ({revenue_per_view:.4f}) suggests optimization opportunities in content monetization.",
                importance_score=0.7,
                actionable=True,
                related_metrics=["revenue_per_view"],
                recommendations=[
                    "Focus on higher-value content formats",
                    "Improve audience targeting for better CPM",
                    "Consider premium content or subscription models"
                ],
                estimated_impact={"revenue_increase": 20.0}
            ))
        
        # Growth trend insight
        growth_rate = growth_analysis.get('total_growth_rate_percentage', 0)
        if growth_rate < 0:
            insights.append(PerformanceInsight(
                insight_id="negative_growth_trend",
                insight_type=InsightType.WARNING,
                title="Declining Revenue Trend",
                description=f"Revenue has declined by {abs(growth_rate):.1f}% over the analysis period.",
                importance_score=0.9,
                actionable=True,
                related_metrics=["total_growth_rate_percentage", "average_daily_growth_percentage"],
                recommendations=[
                    "Analyze which platforms are underperforming",
                    "Review content strategy and audience engagement",
                    "Consider seasonal factors affecting performance"
                ],
                estimated_impact={"urgency_level": "high"}
            ))
        elif growth_rate > 50:
            insights.append(PerformanceInsight(
                insight_id="high_growth_trend",
                insight_type=InsightType.OPPORTUNITY,
                title="Strong Growth Momentum",
                description=f"Excellent revenue growth of {growth_rate:.1f}% - capitalize on this momentum.",
                importance_score=0.8,
                actionable=True,
                related_metrics=["total_growth_rate_percentage"],
                recommendations=[
                    "Scale successful content strategies",
                    "Invest in content production",
                    "Consider expanding team or resources"
                ],
                estimated_impact={"revenue_potential": 30.0}
            ))
        
        # Platform performance insight
        if platform_analysis.get('platform_metrics'):
            top_platform = platform_analysis.get('top_platform')
            platform_metrics = platform_analysis['platform_metrics']
            
            if top_platform and len(platform_metrics) > 1:
                top_share = platform_metrics[top_platform]['revenue_share_percentage']
                
                if top_share > 70:
                    insights.append(PerformanceInsight(
                        insight_id="platform_over_dependence",
                        insight_type=InsightType.WARNING,
                        title="Over-Dependence on Single Platform",
                        description=f"{top_platform} accounts for {top_share:.1f}% of your revenue. This creates risk.",
                        importance_score=0.75,
                        actionable=True,
                        related_metrics=["revenue_share_percentage"],
                        recommendations=[
                            f"Reduce dependence on {top_platform}",
                            "Develop content strategy for other platforms",
                            "Set target of max 50% revenue from any single platform"
                        ],
                        estimated_impact={"risk_reduction": 40.0}
                    ))
        
        return insights


class EngagementAnalyzer:
    """Engagement metrics and optimization analyzer"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def analyze_engagement_performance(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze engagement performance across platforms"""
        
        try:
            # Get engagement data from revenue records
            result = await session.execute(
                select(RevenueRecord).where(
                    RevenueRecord.user_id == user_id,
                    RevenueRecord.date >= start_date,
                    RevenueRecord.date <= end_date,
                    RevenueRecord.engagement_rate.isnot(None)
                )
            )
            
            engagement_data = []
            for record in result.scalars():
                engagement_data.append({
                    "date": record.date,
                    "platform": record.platform,
                    "engagement_rate": record.engagement_rate,
                    "views": record.views or 0,
                    "streams": record.streams or 0,
                    "revenue": float(record.amount)
                })
            
            if not engagement_data:
                return {"message": "No engagement data available"}
            
            # Calculate engagement metrics
            df = pd.DataFrame(engagement_data)
            
            # Overall engagement metrics
            avg_engagement = df['engagement_rate'].mean()
            engagement_trend = df['engagement_rate'].corr(df.index)  # Correlation with time
            
            # Platform comparison
            platform_engagement = df.groupby('platform').agg({
                'engagement_rate': ['mean', 'std', 'count'],
                'views': 'sum',
                'revenue': 'sum'
            }).round(4)
            
            # Engagement-revenue correlation
            engagement_revenue_corr = df['engagement_rate'].corr(df['revenue'])
            
            # Best performing content
            top_engagement = df.nlargest(5, 'engagement_rate')[['date', 'platform', 'engagement_rate', 'views', 'revenue']]
            
            return {
                "summary": {
                    "average_engagement_rate": float(avg_engagement),
                    "engagement_trend": float(engagement_trend),
                    "engagement_revenue_correlation": float(engagement_revenue_corr),
                    "total_data_points": len(df)
                },
                "platform_performance": platform_engagement.to_dict(),
                "top_performing_content": top_engagement.to_dict('records'),
                "insights": await self._generate_engagement_insights(df)
            }
            
        except Exception as e:
            self.logger.error(f"Engagement analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_engagement_insights(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate engagement-specific insights"""
        
        insights = []
        
        # Low engagement warning
        avg_engagement = df['engagement_rate'].mean()
        if avg_engagement < 0.02:  # Less than 2%
            insights.append({
                "type": "warning",
                "title": "Low Engagement Rate",
                "description": f"Average engagement rate of {avg_engagement:.2%} is below industry standards",
                "recommendation": "Focus on creating more interactive and engaging content"
            })
        
        # Platform with best engagement
        platform_avg = df.groupby('platform')['engagement_rate'].mean()
        best_platform = platform_avg.idxmax()
        best_rate = platform_avg.max()
        
        insights.append({
            "type": "opportunity",
            "title": f"Best Engagement on {best_platform}",
            "description": f"{best_platform} shows highest engagement rate of {best_rate:.2%}",
            "recommendation": f"Consider focusing more content strategy on {best_platform}"
        })
        
        return insights


class PerformanceAnalyticsEngine:
    """Main performance analytics engine"""
    
    def __init__(self):
        self.revenue_analyzer = RevenueAnalyzer()
        self.engagement_analyzer = EngagementAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    async def generate_comprehensive_report(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Generate comprehensive performance analytics report"""
        
        try:
            # Run all analyses in parallel
            revenue_analysis, engagement_analysis = await asyncio.gather(
                self.revenue_analyzer.analyze_revenue_performance(user_id, start_date, end_date, session),
                self.engagement_analyzer.analyze_engagement_performance(user_id, start_date, end_date, session),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(revenue_analysis, Exception):
                revenue_analysis = {"error": str(revenue_analysis)}
            
            if isinstance(engagement_analysis, Exception):
                engagement_analysis = {"error": str(engagement_analysis)}
            
            # Generate executive summary
            executive_summary = await self._generate_executive_summary(
                revenue_analysis, engagement_analysis
            )
            
            # Generate action plan
            action_plan = await self._generate_action_plan(
                revenue_analysis, engagement_analysis
            )
            
            return {
                "report_id": f"performance_{user_id}_{int(datetime.now().timestamp())}",
                "user_id": user_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "generated_at": datetime.now().isoformat(),
                "executive_summary": executive_summary,
                "revenue_analysis": revenue_analysis,
                "engagement_analysis": engagement_analysis,
                "action_plan": action_plan,
                "performance_score": await self._calculate_performance_score(revenue_analysis, engagement_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Comprehensive report generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_executive_summary(
        self,
        revenue_analysis: Dict[str, Any],
        engagement_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary of performance"""
        
        summary = {
            "period_highlights": [],
            "key_metrics": {},
            "major_insights": [],
            "priority_actions": []
        }
        
        # Revenue highlights
        if "summary_metrics" in revenue_analysis:
            metrics = revenue_analysis["summary_metrics"]
            summary["key_metrics"]["total_revenue"] = metrics.get("total_revenue", 0)
            summary["key_metrics"]["platform_count"] = metrics.get("number_of_platforms", 0)
            summary["key_metrics"]["diversification"] = metrics.get("platform_diversification_index", 0)
        
        # Growth highlights
        if "growth_analysis" in revenue_analysis:
            growth = revenue_analysis["growth_analysis"]
            growth_rate = growth.get("total_growth_rate_percentage", 0)
            
            if growth_rate > 0:
                summary["period_highlights"].append(f"Revenue grew by {growth_rate:.1f}%")
            else:
                summary["period_highlights"].append(f"Revenue declined by {abs(growth_rate):.1f}%")
        
        # Engagement highlights
        if "summary" in engagement_analysis:
            eng_summary = engagement_analysis["summary"]
            avg_engagement = eng_summary.get("average_engagement_rate", 0)
            summary["key_metrics"]["average_engagement"] = avg_engagement
            
            if avg_engagement > 0.05:  # 5%
                summary["period_highlights"].append("Strong engagement performance")
            elif avg_engagement < 0.02:  # 2%
                summary["period_highlights"].append("Engagement needs improvement")
        
        return summary
    
    async def _generate_action_plan(
        self,
        revenue_analysis: Dict[str, Any],
        engagement_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized action plan"""
        
        actions = []
        
        # Revenue-based actions
        if "insights" in revenue_analysis:
            for insight in revenue_analysis["insights"]:
                if insight.get("actionable") and insight.get("importance_score", 0) > 0.7:
                    actions.append({
                        "priority": "high",
                        "category": "revenue",
                        "title": insight["title"],
                        "description": insight["description"],
                        "recommendations": insight.get("recommendations", []),
                        "estimated_impact": insight.get("estimated_impact", {})
                    })
        
        # Engagement-based actions
        if "insights" in engagement_analysis:
            for insight in engagement_analysis["insights"]:
                if insight.get("type") == "warning":
                    actions.append({
                        "priority": "medium",
                        "category": "engagement",
                        "title": insight["title"],
                        "description": insight["description"],
                        "recommendations": [insight.get("recommendation", "")]
                    })
        
        # Sort by priority
        priority_order = {"high": 1, "medium": 2, "low": 3}
        actions.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return actions
    
    async def _calculate_performance_score(
        self,
        revenue_analysis: Dict[str, Any],
        engagement_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate overall performance score"""
        
        scores = {
            "revenue_score": 0.0,
            "growth_score": 0.0,
            "engagement_score": 0.0,
            "diversification_score": 0.0,
            "overall_score": 0.0
        }
        
        # Revenue score (based on total revenue relative to goals)
        if "summary_metrics" in revenue_analysis:
            total_revenue = revenue_analysis["summary_metrics"].get("total_revenue", 0)
            scores["revenue_score"] = min(100, (total_revenue / 1000) * 10)  # €1000 = 10 points
        
        # Growth score
        if "growth_analysis" in revenue_analysis:
            growth_rate = revenue_analysis["growth_analysis"].get("total_growth_rate_percentage", 0)
            scores["growth_score"] = max(0, min(100, 50 + growth_rate))  # 0% growth = 50 points
        
        # Engagement score
        if "summary" in engagement_analysis:
            engagement_rate = engagement_analysis["summary"].get("average_engagement_rate", 0)
            scores["engagement_score"] = min(100, engagement_rate * 2000)  # 5% = 100 points
        
        # Diversification score
        if "summary_metrics" in revenue_analysis:
            diversification = revenue_analysis["summary_metrics"].get("platform_diversification_index", 0)
            scores["diversification_score"] = diversification * 100
        
        # Overall score (weighted average)
        weights = {
            "revenue_score": 0.4,
            "growth_score": 0.3,
            "engagement_score": 0.2,
            "diversification_score": 0.1
        }
        
        scores["overall_score"] = sum(
            scores[metric] * weight for metric, weight in weights.items()
        )
        
        return scores
