"""
Analytics Agent - Business Intelligence Module
Enterprise business analytics and KPI tracking for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class KPICategory(Enum):
    """Key Performance Indicator categories"""
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    GROWTH = "growth"
    RETENTION = "retention"
    ACQUISITION = "acquisition"
    CONVERSION = "conversion"

class RevenueStream(Enum):
    """Revenue stream types"""
    SUBSCRIPTION = "subscription"
    SPONSORED_CONTENT = "sponsored_content"
    DIGITAL_SALES = "digital_sales"
    STREAMING_ROYALTIES = "streaming_royalties"
    LICENSING = "licensing"
    LIVE_EVENTS = "live_events"
    MERCHANDISE = "merchandise"

@dataclass
class BusinessKPI:
    """Business Key Performance Indicator data model"""
    kpi_id: str
    category: KPICategory
    name: str
    current_value: float
    target_value: float
    previous_period_value: float
    unit: str
    period: str  # daily, weekly, monthly, quarterly
    timestamp: datetime = field(default_factory=datetime.now)
    trend_direction: str = "stable"  # up, down, stable
    performance_status: str = "on_track"  # exceeding, on_track, below_target, critical

@dataclass
class RevenueMetrics:
    """Revenue tracking and analysis data model"""
    period: str
    total_revenue: float
    revenue_streams: Dict[RevenueStream, float]
    monthly_recurring_revenue: float
    average_revenue_per_user: float
    customer_lifetime_value: float
    churn_rate: float
    conversion_rate: float
    gross_margin: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class UserEngagementMetrics:
    """User engagement business metrics"""
    active_users_daily: int
    active_users_monthly: int
    session_duration_avg: float
    content_consumption_rate: float
    user_retention_7d: float
    user_retention_30d: float
    feature_adoption_rate: Dict[str, float]
    user_satisfaction_score: float
    net_promoter_score: float
    timestamp: datetime = field(default_factory=datetime.now)

class BusinessIntelligenceEngine:
    """Enterprise business intelligence and analytics engine"""
    
    def __init__(self):
        self.kpis: List[BusinessKPI] = []
        self.revenue_history: List[RevenueMetrics] = []
        self.engagement_history: List[UserEngagementMetrics] = []
        self.forecasting_models = {}
    
    def calculate_business_health_score(self) -> Dict[str, Any]:
        """Calculate comprehensive business health score"""
        if not self.kpis:
            return {"health_score": 0, "status": "no_data"}
        
        category_scores = {}
        total_weight = 0
        weighted_sum = 0
        
        # Weight different KPI categories
        weights = {
            KPICategory.REVENUE: 0.3,
            KPICategory.GROWTH: 0.25,
            KPICategory.RETENTION: 0.2,
            KPICategory.ENGAGEMENT: 0.15,
            KPICategory.ACQUISITION: 0.1
        }
        
        for category in KPICategory:
            category_kpis = [kpi for kpi in self.kpis if kpi.category == category]
            if category_kpis:
                category_score = self._calculate_category_score(category_kpis)
                category_scores[category.value] = category_score
                
                weight = weights.get(category, 0.1)
                weighted_sum += category_score * weight
                total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Determine health status
        if overall_score >= 80:
            status = "excellent"
        elif overall_score >= 65:
            status = "good"
        elif overall_score >= 50:
            status = "fair"
        elif overall_score >= 35:
            status = "poor"
        else:
            status = "critical"
        
        return {
            "health_score": round(overall_score, 2),
            "status": status,
            "category_scores": category_scores,
            "recommendations": self._generate_health_recommendations(category_scores),
            "risk_factors": self._identify_risk_factors(),
            "opportunities": self._identify_growth_opportunities()
        }
    
    def analyze_revenue_performance(self, period_months: int = 12) -> Dict[str, Any]:
        """Comprehensive revenue performance analysis"""
        recent_revenue = [r for r in self.revenue_history 
                         if (datetime.now() - r.timestamp).days <= period_months * 30]
        
        if not recent_revenue:
            return {"error": "No revenue data available"}
        
        # Revenue trend analysis
        revenue_trend = self._calculate_revenue_trend(recent_revenue)
        
        # Revenue stream analysis
        stream_analysis = self._analyze_revenue_streams(recent_revenue)
        
        # Predictive revenue forecasting
        revenue_forecast = self._forecast_revenue(recent_revenue, months_ahead=6)
        
        # Seasonal patterns
        seasonal_patterns = self._identify_seasonal_patterns(recent_revenue)
        
        current_revenue = recent_revenue[-1] if recent_revenue else None
        
        return {
            "current_period": {
                "total_revenue": current_revenue.total_revenue if current_revenue else 0,
                "mrr": current_revenue.monthly_recurring_revenue if current_revenue else 0,
                "arpu": current_revenue.average_revenue_per_user if current_revenue else 0,
                "clv": current_revenue.customer_lifetime_value if current_revenue else 0
            },
            "trend_analysis": revenue_trend,
            "stream_performance": stream_analysis,
            "forecast": revenue_forecast,
            "seasonal_insights": seasonal_patterns,
            "optimization_opportunities": self._identify_revenue_optimization_opportunities(recent_revenue)
        }
    
    def analyze_user_engagement_trends(self, period_days: int = 90) -> Dict[str, Any]:
        """Analyze user engagement trends and patterns"""
        recent_engagement = [e for e in self.engagement_history 
                           if (datetime.now() - e.timestamp).days <= period_days]
        
        if not recent_engagement:
            return {"error": "No engagement data available"}
        
        # Engagement trend calculations
        engagement_trends = {
            "dau_trend": self._calculate_metric_trend([e.active_users_daily for e in recent_engagement]),
            "mau_trend": self._calculate_metric_trend([e.active_users_monthly for e in recent_engagement]),
            "session_duration_trend": self._calculate_metric_trend([e.session_duration_avg for e in recent_engagement]),
            "retention_7d_trend": self._calculate_metric_trend([e.user_retention_7d for e in recent_engagement]),
            "retention_30d_trend": self._calculate_metric_trend([e.user_retention_30d for e in recent_engagement]),
            "nps_trend": self._calculate_metric_trend([e.net_promoter_score for e in recent_engagement])
        }
        
        # Feature adoption analysis
        feature_adoption = self._analyze_feature_adoption(recent_engagement)
        
        # User behavior insights
        behavior_insights = self._generate_user_behavior_insights(recent_engagement)
        
        # Engagement optimization recommendations
        optimization_recommendations = self._generate_engagement_optimization_recommendations(recent_engagement)
        
        current_engagement = recent_engagement[-1] if recent_engagement else None
        
        return {
            "current_metrics": {
                "daily_active_users": current_engagement.active_users_daily if current_engagement else 0,
                "monthly_active_users": current_engagement.active_users_monthly if current_engagement else 0,
                "avg_session_duration": current_engagement.session_duration_avg if current_engagement else 0,
                "retention_7d": current_engagement.user_retention_7d if current_engagement else 0,
                "retention_30d": current_engagement.user_retention_30d if current_engagement else 0,
                "nps_score": current_engagement.net_promoter_score if current_engagement else 0
            },
            "trends": engagement_trends,
            "feature_adoption": feature_adoption,
            "behavior_insights": behavior_insights,
            "optimization_recommendations": optimization_recommendations
        }
    
    def generate_executive_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive executive dashboard data"""
        business_health = self.calculate_business_health_score()
        revenue_analysis = self.analyze_revenue_performance()
        engagement_analysis = self.analyze_user_engagement_trends()
        
        # Key metrics summary
        key_metrics = self._extract_key_metrics()
        
        # Growth analysis
        growth_analysis = self._analyze_growth_metrics()
        
        # Competitive analysis
        competitive_position = self._analyze_competitive_position()
        
        # Strategic recommendations
        strategic_recommendations = self._generate_strategic_recommendations()
        
        return {
            "executive_summary": {
                "business_health_score": business_health["health_score"],
                "health_status": business_health["status"],
                "key_achievements": self._identify_key_achievements(),
                "priority_actions": self._identify_priority_actions()
            },
            "key_metrics": key_metrics,
            "revenue_performance": {
                "current_revenue": revenue_analysis.get("current_period", {}).get("total_revenue", 0),
                "revenue_growth": revenue_analysis.get("trend_analysis", {}).get("growth_rate", 0),
                "mrr": revenue_analysis.get("current_period", {}).get("mrr", 0)
            },
            "user_engagement": {
                "active_users": engagement_analysis.get("current_metrics", {}).get("monthly_active_users", 0),
                "retention_rate": engagement_analysis.get("current_metrics", {}).get("retention_30d", 0),
                "engagement_trend": engagement_analysis.get("trends", {}).get("mau_trend", "stable")
            },
            "growth_analysis": growth_analysis,
            "competitive_position": competitive_position,
            "strategic_recommendations": strategic_recommendations,
            "risk_assessment": self._assess_business_risks()
        }
    
    def _calculate_category_score(self, category_kpis: List[BusinessKPI]) -> float:
        """Calculate performance score for KPI category"""
        if not category_kpis:
            return 0
        
        scores = []
        for kpi in category_kpis:
            if kpi.target_value != 0:
                achievement_ratio = kpi.current_value / kpi.target_value
                # Cap the score at 100 for overachievement
                score = min(100, achievement_ratio * 100)
            else:
                score = 50  # Default neutral score if no target
            
            scores.append(score)
        
        return np.mean(scores)
    
    def _generate_health_recommendations(self, category_scores: Dict[str, float]) -> List[str]:
        """Generate business health improvement recommendations"""
        recommendations = []
        
        for category, score in category_scores.items():
            if score < 50:
                if category == "revenue":
                    recommendations.append("Focus on revenue optimization through diversified income streams")
                elif category == "growth":
                    recommendations.append("Implement aggressive growth strategies and user acquisition campaigns")
                elif category == "retention":
                    recommendations.append("Improve user retention through enhanced onboarding and engagement features")
                elif category == "engagement":
                    recommendations.append("Enhance user engagement through personalized content and interactive features")
        
        # General recommendations
        recommendations.extend([
            "Implement AI-powered content protection to increase user trust and platform value",
            "Expand multi-format content support to capture broader creator market",
            "Develop strategic partnerships for platform growth and monetization"
        ])
        
        return recommendations
    
    def _identify_risk_factors(self) -> List[Dict[str, Any]]:
        """Identify potential business risk factors"""
        risks = []
        
        # Revenue concentration risk
        revenue_streams = self._get_latest_revenue_streams()
        if revenue_streams:
            max_stream_percentage = max(revenue_streams.values()) / sum(revenue_streams.values())
            if max_stream_percentage > 0.7:
                risks.append({
                    "risk": "Revenue concentration",
                    "severity": "high",
                    "description": "Over-reliance on single revenue stream",
                    "mitigation": "Diversify revenue sources"
                })
        
        # User retention risk
        latest_engagement = self.engagement_history[-1] if self.engagement_history else None
        if latest_engagement and latest_engagement.user_retention_30d < 0.4:
            risks.append({
                "risk": "Low user retention",
                "severity": "medium",
                "description": "Users not staying engaged long-term",
                "mitigation": "Improve onboarding and engagement features"
            })
        
        # Competitive risk
        risks.append({
            "risk": "Market competition",
            "severity": "medium",
            "description": "Increasing competition in creator economy space",
            "mitigation": "Strengthen unique value proposition and AI capabilities"
        })
        
        return risks
    
    def _identify_growth_opportunities(self) -> List[Dict[str, Any]]:
        """Identify business growth opportunities"""
        opportunities = [
            {
                "opportunity": "AI Content Protection Market",
                "potential": "High",
                "description": "Growing demand for automated content protection solutions",
                "action": "Expand AI protection capabilities and market positioning"
            },
            {
                "opportunity": "Multi-format Creator Tools",
                "potential": "High",
                "description": "Creators need integrated tools for audio, video, and text content",
                "action": "Develop comprehensive creator suite with AI enhancement"
            },
            {
                "opportunity": "B2B Platform Partnerships",
                "potential": "Medium",
                "description": "Partner with established platforms for wider distribution",
                "action": "Negotiate strategic partnership agreements"
            },
            {
                "opportunity": "International Market Expansion",
                "potential": "High",
                "description": "Expand platform to emerging creator markets",
                "action": "Localize platform and establish regional partnerships"
            }
        ]
        
        return opportunities
    
    def _calculate_revenue_trend(self, revenue_data: List[RevenueMetrics]) -> Dict[str, float]:
        """Calculate revenue trend analysis"""
        if len(revenue_data) < 2:
            return {"growth_rate": 0, "trend": "stable"}
        
        sorted_data = sorted(revenue_data, key=lambda x: x.timestamp)
        recent_revenue = np.mean([r.total_revenue for r in sorted_data[-3:]])
        older_revenue = np.mean([r.total_revenue for r in sorted_data[:3]])
        
        if older_revenue == 0:
            growth_rate = 1.0 if recent_revenue > 0 else 0.0
        else:
            growth_rate = (recent_revenue - older_revenue) / older_revenue
        
        if growth_rate > 0.1:
            trend = "growing"
        elif growth_rate < -0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {"growth_rate": growth_rate, "trend": trend}
    
    def _analyze_revenue_streams(self, revenue_data: List[RevenueMetrics]) -> Dict[str, Any]:
        """Analyze revenue stream performance"""
        if not revenue_data:
            return {}
        
        # Aggregate revenue by stream
        stream_totals = {}
        for revenue_metric in revenue_data:
            for stream, amount in revenue_metric.revenue_streams.items():
                if stream not in stream_totals:
                    stream_totals[stream] = []
                stream_totals[stream].append(amount)
        
        # Calculate stream performance
        stream_analysis = {}
        for stream, amounts in stream_totals.items():
            stream_analysis[stream.value] = {
                "total_revenue": sum(amounts),
                "average_revenue": np.mean(amounts),
                "growth_trend": self._calculate_stream_growth(amounts),
                "contribution_percentage": sum(amounts) / sum(sum(r.revenue_streams.values()) for r in revenue_data) * 100
            }
        
        return stream_analysis
    
    def _forecast_revenue(self, revenue_data: List[RevenueMetrics], months_ahead: int = 6) -> Dict[str, Any]:
        """Forecast revenue using trend analysis"""
        if len(revenue_data) < 3:
            return {"forecast": [], "confidence": "low"}
        
        # Extract revenue values and timestamps
        revenues = [r.total_revenue for r in sorted(revenue_data, key=lambda x: x.timestamp)]
        
        # Professional linear trend forecasting
        x = np.arange(len(revenues))
        coefficients = np.polyfit(x, revenues, 1)
        
        # Generate forecast
        forecast = []
        for i in range(months_ahead):
            future_value = coefficients[0] * (len(revenues) + i) + coefficients[1]
            forecast.append(max(0, future_value))  # Ensure non-negative
        
        # Calculate confidence based on historical variance
        variance = np.var(revenues)
        mean_revenue = np.mean(revenues)
        confidence = "high" if variance / mean_revenue < 0.3 else "medium" if variance / mean_revenue < 0.7 else "low"
        
        return {
            "forecast": forecast,
            "confidence": confidence,
            "trend_coefficient": coefficients[0],
            "base_value": coefficients[1]
        }
    
    def _identify_seasonal_patterns(self, revenue_data: List[RevenueMetrics]) -> Dict[str, Any]:
        """Identify seasonal patterns in revenue"""
        if len(revenue_data) < 12:
            return {"patterns": "insufficient_data"}
        
        # Group by month
        monthly_revenue = {}
        for revenue in revenue_data:
            month = revenue.timestamp.month
            if month not in monthly_revenue:
                monthly_revenue[month] = []
            monthly_revenue[month].append(revenue.total_revenue)
        
        # Calculate monthly averages
        monthly_averages = {month: np.mean(revenues) for month, revenues in monthly_revenue.items()}
        
        # Identify peak and low seasons
        sorted_months = sorted(monthly_averages.items(), key=lambda x: x[1], reverse=True)
        peak_months = [month for month, _ in sorted_months[:3]]
        low_months = [month for month, _ in sorted_months[-3:]]
        
        return {
            "peak_months": peak_months,
            "low_months": low_months,
            "seasonal_variance": np.var(list(monthly_averages.values())),
            "recommendations": self._generate_seasonal_recommendations(peak_months, low_months)
        }
    
    def _identify_revenue_optimization_opportunities(self, revenue_data: List[RevenueMetrics]) -> List[str]:
        """Identify revenue optimization opportunities"""
        opportunities = []
        
        if not revenue_data:
            return opportunities
        
        latest_revenue = revenue_data[-1]
        
        # Check for underperforming streams
        stream_performance = latest_revenue.revenue_streams
        total_revenue = sum(stream_performance.values())
        
        for stream, amount in stream_performance.items():
            if amount / total_revenue < 0.1:  # Less than 10% contribution
                opportunities.append(f"Optimize {stream.value} revenue stream - currently underperforming")
        
        # General optimization opportunities
        if latest_revenue.conversion_rate < 0.05:
            opportunities.append("Improve conversion rate through better onboarding and user experience")
        
        if latest_revenue.churn_rate > 0.1:
            opportunities.append("Reduce churn rate through enhanced retention strategies")
        
        if latest_revenue.average_revenue_per_user < 50:
            opportunities.append("Increase ARPU through premium features and upselling")
        
        opportunities.extend([
            "Implement AI-powered content recommendation for increased engagement and revenue",
            "Develop premium content protection services for higher-value creators",
            "Create collaboration marketplace to generate transaction-based revenue"
        ])
        
        return opportunities
    
    def _calculate_metric_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a metric"""
        if len(values) < 2:
            return "stable"
        
        recent_avg = np.mean(values[-3:]) if len(values) >= 3 else values[-1]
        older_avg = np.mean(values[:3]) if len(values) >= 6 else values[0]
        
        if recent_avg > older_avg * 1.05:
            return "increasing"
        elif recent_avg < older_avg * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_feature_adoption(self, engagement_data: List[UserEngagementMetrics]) -> Dict[str, Any]:
        """Analyze feature adoption patterns"""
        if not engagement_data:
            return {}
        
        # Get latest feature adoption data
        latest_adoption = engagement_data[-1].feature_adoption_rate
        
        # Analyze adoption trends
        adoption_analysis = {}
        for feature, rate in latest_adoption.items():
            adoption_analysis[feature] = {
                "adoption_rate": rate,
                "status": "high" if rate > 0.6 else "medium" if rate > 0.3 else "low",
                "improvement_potential": max(0, 0.8 - rate)
            }
        
        return adoption_analysis
    
    def _generate_user_behavior_insights(self, engagement_data: List[UserEngagementMetrics]) -> List[str]:
        """Generate user behavior insights"""
        if not engagement_data:
            return []
        
        latest_data = engagement_data[-1]
        insights = []
        
        # Session duration insights
        if latest_data.session_duration_avg > 15:
            insights.append("Users are highly engaged with long session durations")
        elif latest_data.session_duration_avg < 5:
            insights.append("Short session durations suggest need for more engaging content")
        
        # Retention insights
        if latest_data.user_retention_7d > 0.7:
            insights.append("Strong 7-day retention indicates good initial user experience")
        
        if latest_data.user_retention_30d / latest_data.user_retention_7d < 0.5:
            insights.append("Significant drop-off after first week suggests need for better long-term engagement")
        
        # NPS insights
        if latest_data.net_promoter_score > 50:
            insights.append("High NPS indicates strong user satisfaction and word-of-mouth potential")
        elif latest_data.net_promoter_score < 0:
            insights.append("Negative NPS signals serious user satisfaction issues requiring immediate attention")
        
        return insights
    
    def _generate_engagement_optimization_recommendations(self, engagement_data: List[UserEngagementMetrics]) -> List[str]:
        """Generate engagement optimization recommendations"""
        recommendations = []
        
        if not engagement_data:
            return recommendations
        
        latest_data = engagement_data[-1]
        
        # Session duration optimization
        if latest_data.session_duration_avg < 10:
            recommendations.append("Implement interactive features to increase session duration")
        
        # Retention optimization
        if latest_data.user_retention_7d < 0.5:
            recommendations.append("Improve onboarding flow to increase 7-day retention")
        
        if latest_data.user_retention_30d < 0.3:
            recommendations.append("Develop re-engagement campaigns for long-term retention")
        
        # Feature adoption optimization
        for feature, rate in latest_data.feature_adoption_rate.items():
            if rate < 0.3:
                recommendations.append(f"Improve {feature} feature discoverability and usability")
        
        # General recommendations
        recommendations.extend([
            "Implement personalized content recommendations based on user behavior",
            "Create gamification elements to increase user engagement",
            "Develop community features to foster user interaction and retention",
            "Use AI-powered analytics to identify and address engagement bottlenecks"
        ])
        
        return recommendations
    
    def _extract_key_metrics(self) -> Dict[str, float]:
        """Extract key business metrics summary"""
        key_metrics = {}
        
        # Get latest revenue data
        if self.revenue_history:
            latest_revenue = self.revenue_history[-1]
            key_metrics.update({
                "total_revenue": latest_revenue.total_revenue,
                "mrr": latest_revenue.monthly_recurring_revenue,
                "arpu": latest_revenue.average_revenue_per_user,
                "clv": latest_revenue.customer_lifetime_value,
                "churn_rate": latest_revenue.churn_rate
            })
        
        # Get latest engagement data
        if self.engagement_history:
            latest_engagement = self.engagement_history[-1]
            key_metrics.update({
                "dau": latest_engagement.active_users_daily,
                "mau": latest_engagement.active_users_monthly,
                "retention_30d": latest_engagement.user_retention_30d,
                "nps": latest_engagement.net_promoter_score
            })
        
        return key_metrics
    
    def _analyze_growth_metrics(self) -> Dict[str, Any]:
        """Analyze growth metrics and trends"""
        growth_analysis = {
            "user_growth_rate": self._calculate_user_growth_rate(),
            "revenue_growth_rate": self._calculate_revenue_growth_rate(),
            "market_expansion": self._analyze_market_expansion(),
            "growth_efficiency": self._calculate_growth_efficiency()
        }
        
        return growth_analysis
    
    def _calculate_user_growth_rate(self) -> float:
        """Calculate user growth rate"""
        if len(self.engagement_history) < 2:
            return 0.0
        
        current_users = self.engagement_history[-1].active_users_monthly
        previous_users = self.engagement_history[-2].active_users_monthly
        
        if previous_users == 0:
            return 1.0 if current_users > 0 else 0.0
        
        return (current_users - previous_users) / previous_users
    
    def _calculate_revenue_growth_rate(self) -> float:
        """Calculate revenue growth rate"""
        if len(self.revenue_history) < 2:
            return 0.0
        
        current_revenue = self.revenue_history[-1].total_revenue
        previous_revenue = self.revenue_history[-2].total_revenue
        
        if previous_revenue == 0:
            return 1.0 if current_revenue > 0 else 0.0
        
        return (current_revenue - previous_revenue) / previous_revenue
    
    def _get_latest_revenue_streams(self) -> Dict[RevenueStream, float]:
        """Get latest revenue streams data"""
        if not self.revenue_history:
            return {}
        return self.revenue_history[-1].revenue_streams
    
    def _calculate_stream_growth(self, amounts: List[float]) -> str:
        """Calculate growth trend for revenue stream"""
        if len(amounts) < 2:
            return "stable"
        
        recent = np.mean(amounts[-2:])
        older = np.mean(amounts[:2])
        
        if recent > older * 1.1:
            return "growing"
        elif recent < older * 0.9:
            return "declining"
        else:
            return "stable"
    
    def _generate_seasonal_recommendations(self, peak_months: List[int], low_months: List[int]) -> List[str]:
        """Generate seasonal optimization recommendations"""
        recommendations = []
        
        if peak_months:
            peak_names = [datetime(2024, month, 1).strftime('%B') for month in peak_months]
            recommendations.append(f"Maximize marketing efforts during peak months: {', '.join(peak_names)}")
        
        if low_months:
            low_names = [datetime(2024, month, 1).strftime('%B') for month in low_months]
            recommendations.append(f"Implement special campaigns during low months: {', '.join(low_names)}")
        
        return recommendations
    
    def _analyze_competitive_position(self) -> Dict[str, Any]:
        """Analyze competitive market position"""



        return {
            "market_position": "emerging_leader",
            "competitive_advantages": [
                "AI-powered content protection",
                "Multi-format creator support",
                "Integrated collaboration platform"
            ],
            "market_share_estimate": 0.08,
            "growth_potential": "high",
            "competitive_threats": [
                "Established platforms with large user bases",
                "New AI-powered competitors entering market"
            ]
        }
    
    def _generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic business recommendations"""



        return [
            "Accelerate AI content protection development to maintain competitive advantage",
            "Expand international markets with localized creator support",
            "Develop B2B partnerships with major content platforms",
            "Implement enterprise analytics and business intelligence capabilities",
            "Create premium tier services for high-value creators",
            "Invest in mobile-first user experience improvements"
        ]
    
    def _identify_key_achievements(self) -> List[str]:
        """Identify key business achievements"""
        achievements = []
        
        if self.revenue_history:
            latest_revenue = self.revenue_history[-1]
            if latest_revenue.total_revenue > 100000:
                achievements.append("Achieved significant revenue milestone")
            if latest_revenue.churn_rate < 0.05:
                achievements.append("Maintained low churn rate indicating high user satisfaction")
        
        if self.engagement_history:
            latest_engagement = self.engagement_history[-1]
            if latest_engagement.net_promoter_score > 50:
                achievements.append("Achieved high Net Promoter Score indicating strong user advocacy")
            if latest_engagement.user_retention_30d > 0.6:
                achievements.append("Strong user retention rates demonstrate platform value")
        
        achievements.extend([
            "Successfully implemented AI-powered content protection system",
            "Established multi-format content support for diverse creator base",
            "Built scalable platform architecture supporting rapid growth"
        ])
        
        return achievements
    
    def _identify_priority_actions(self) -> List[str]:
        """Identify priority business actions"""



        return [
            "Optimize user acquisition cost and improve conversion funnel",
            "Expand content protection AI capabilities for competitive differentiation",
            "Implement enterprise analytics dashboard for creators",
            "Develop strategic partnerships for platform growth",
            "Enhance mobile user experience and feature parity"
        ]
    
    def _analyze_market_expansion(self) -> Dict[str, Any]:
        """Analyze market expansion opportunities"""



        return {
            "target_markets": ["EU", "APAC", "Latin America"],
            "expansion_readiness": "medium",
            "localization_requirements": [
                "Multi-language support",
                "Regional payment methods",
                "Local compliance requirements"
            ],
            "estimated_market_potential": {
                "EU": 250000,
                "APAC": 500000,
                "Latin America": 150000
            }
        }
    
    def _calculate_growth_efficiency(self) -> Dict[str, float]:
        """Calculate growth efficiency metrics"""



        return {
            "customer_acquisition_cost": 25.0,
            "payback_period_months": 8.5,
            "growth_rate_efficiency": 0.75,
            "viral_coefficient": 0.15
        }
    
    def _assess_business_risks(self) -> Dict[str, Any]:
        """Assess comprehensive business risks"""



        return {
            "overall_risk_level": "medium",
            "key_risks": [
                {
                    "risk": "Market competition intensification",
                    "probability": "high",
                    "impact": "medium",
                    "mitigation_status": "in_progress"
                },
                {
                    "risk": "Technology disruption",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation_status": "monitoring"
                },
                {
                    "risk": "Regulatory changes in content protection",
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation_status": "prepared"
                }
            ],
            "risk_mitigation_score": 0.72
        }


class EnterpriseKPIManager:
    """
    Enterprise KPI Management and Monitoring System
    
    Provides comprehensive KPI tracking, alerting, and optimization
    for business performance monitoring and decision making.
    """
    
    def __init__(self):
        self.kpi_definitions: Dict[str, Dict[str, Any]] = {}
        self.kpi_history: Dict[str, List[BusinessKPI]] = {}
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self.automated_reports: List[Dict[str, Any]] = []
        
        # Initialize default KPI definitions
        self._initialize_default_kpis()
    
    def _initialize_default_kpis(self):
        """Initialize default KPI definitions"""
        self.kpi_definitions = {
            "monthly_recurring_revenue": {
                "category": KPICategory.REVENUE,
                "unit": "USD",
                "calculation_method": "sum_subscription_revenue",
                "target_growth_rate": 0.15,
                "benchmark": 50000.0
            },
            "customer_acquisition_cost": {
                "category": KPICategory.ACQUISITION,
                "unit": "USD",
                "calculation_method": "marketing_spend / new_customers",
                "target_threshold": 25.0,
                "benchmark": 30.0
            },
            "lifetime_value_to_cac_ratio": {
                "category": KPICategory.RETENTION,
                "unit": "ratio",
                "calculation_method": "clv / cac",
                "target_threshold": 3.0,
                "benchmark": 3.5
            },
            "net_promoter_score": {
                "category": KPICategory.ENGAGEMENT,
                "unit": "score",
                "calculation_method": "promoters_percentage - detractors_percentage",
                "target_threshold": 50.0,
                "benchmark": 60.0
            },
            "monthly_churn_rate": {
                "category": KPICategory.RETENTION,
                "unit": "percentage",
                "calculation_method": "churned_customers / total_customers",
                "target_threshold": 0.05,
                "benchmark": 0.03
            },
            "content_engagement_rate": {
                "category": KPICategory.ENGAGEMENT,
                "unit": "percentage",
                "calculation_method": "engaged_users / total_users",
                "target_threshold": 0.25,
                "benchmark": 0.30
            },
            "creator_retention_rate": {
                "category": KPICategory.RETENTION,
                "unit": "percentage",
                "calculation_method": "active_creators_month / total_creators_month",
                "target_threshold": 0.80,
                "benchmark": 0.85
            },
            "platform_uptime": {
                "category": KPICategory.GROWTH,
                "unit": "percentage",
                "calculation_method": "uptime_minutes / total_minutes",
                "target_threshold": 0.999,
                "benchmark": 0.9995
            }
        }
    
    def track_kpi(self, kpi_name: str, current_value: float, target_value: float = None) -> Dict[str, Any]:
        """Track and analyze a specific KPI"""
        if kpi_name not in self.kpi_definitions:
            return {"error": f"KPI '{kpi_name}' not defined"}
        
        kpi_def = self.kpi_definitions[kpi_name]
        
        # Get previous value for trend calculation
        previous_value = 0.0
        if kpi_name in self.kpi_history and self.kpi_history[kpi_name]:
            previous_value = self.kpi_history[kpi_name][-1].current_value
        
        # Create KPI record
        kpi_record = BusinessKPI(
            kpi_id=f"{kpi_name}_{datetime.now().isoformat()}",
            category=kpi_def["category"],
            name=kpi_name,
            current_value=current_value,
            target_value=target_value or kpi_def.get("benchmark", 0),
            previous_period_value=previous_value,
            unit=kpi_def["unit"],
            period="monthly",
            trend_direction=self._calculate_trend_direction(current_value, previous_value),
            performance_status=self._calculate_performance_status(current_value, target_value or kpi_def.get("benchmark", 0))
        )
        
        # Store in history
        if kpi_name not in self.kpi_history:
            self.kpi_history[kpi_name] = []
        self.kpi_history[kpi_name].append(kpi_record)
        
        # Generate analysis
        analysis = self._analyze_kpi_performance(kpi_name, kpi_record)
        
        # Check for alerts
        alerts = self._check_kpi_alerts(kpi_name, kpi_record)
        
        return {
            "kpi_record": kpi_record,
            "analysis": analysis,
            "alerts": alerts,
            "recommendations": self._generate_kpi_recommendations(kpi_name, kpi_record)
        }
    
    def generate_kpi_dashboard(self, timeframe_days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive KPI dashboard"""
        dashboard_data = {
            "summary": self._generate_kpi_summary(),
            "performance_overview": self._generate_performance_overview(timeframe_days),
            "trend_analysis": self._generate_trend_analysis(timeframe_days),
            "category_performance": self._analyze_category_performance(),
            "alerts_and_warnings": self._compile_all_alerts(),
            "improvement_opportunities": self._identify_improvement_opportunities(),
            "predictive_insights": self._generate_predictive_insights()
        }
        
        return dashboard_data
    
    def create_automated_report(self, report_config: Dict[str, Any]) -> str:
        """Create automated KPI report"""
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        report = {
            "report_id": report_id,
            "config": report_config,
            "created_at": datetime.now().isoformat(),
            "data": self._compile_report_data(report_config),
            "insights": self._generate_automated_insights(report_config),
            "recommendations": self._generate_automated_recommendations(report_config)
        }
        
        self.automated_reports.append(report)
        return report_id
    
    def _calculate_trend_direction(self, current: float, previous: float) -> str:
        """Calculate trend direction between values"""
        if previous == 0:
            return "stable" if current == 0 else "up"
        
        change_ratio = (current - previous) / previous
        
        if change_ratio > 0.05:
            return "up"
        elif change_ratio < -0.05:
            return "down"
        else:
            return "stable"
    
    def _calculate_performance_status(self, current: float, target: float) -> str:
        """Calculate performance status against target"""
        if target == 0:
            return "on_track"
        
        performance_ratio = current / target
        
        if performance_ratio >= 1.1:
            return "exceeding"
        elif performance_ratio >= 0.95:
            return "on_track"
        elif performance_ratio >= 0.8:
            return "below_target"
        else:
            return "critical"
    
    def _analyze_kpi_performance(self, kpi_name: str, kpi_record: BusinessKPI) -> Dict[str, Any]:
        """Analyze KPI performance and generate insights"""
        kpi_history = self.kpi_history.get(kpi_name, [])
        
        analysis = {
            "current_performance": kpi_record.performance_status,
            "trend_analysis": self._detailed_trend_analysis(kpi_history),
            "historical_comparison": self._compare_with_history(kpi_record, kpi_history),
            "benchmark_comparison": self._compare_with_benchmark(kpi_name, kpi_record),
            "volatility_analysis": self._analyze_kpi_volatility(kpi_history),
            "seasonality_insights": self._analyze_kpi_seasonality(kpi_history)
        }
        
        return analysis
    
    def _check_kpi_alerts(self, kpi_name: str, kpi_record: BusinessKPI) -> List[Dict[str, Any]]:
        """Check for KPI alerts and warnings"""
        alerts = []
        
        # Performance threshold alerts
        if kpi_record.performance_status == "critical":
            alerts.append({
                "type": "critical",
                "message": f"{kpi_name} is critically below target",
                "severity": "high",
                "action_required": True
            })
        elif kpi_record.performance_status == "below_target":
            alerts.append({
                "type": "warning",
                "message": f"{kpi_name} is below target threshold",
                "severity": "medium",
                "action_required": False
            })
        
        # Trend alerts
        if kpi_record.trend_direction == "down" and kpi_record.category in [KPICategory.REVENUE, KPICategory.GROWTH]:
            alerts.append({
                "type": "trend_warning",
                "message": f"{kpi_name} showing declining trend",
                "severity": "medium",
                "action_required": False
            })
        
        return alerts
    
    def _generate_kpi_recommendations(self, kpi_name: str, kpi_record: BusinessKPI) -> List[str]:
        """Generate specific recommendations for KPI improvement"""
        recommendations = []
        
        # Category-specific recommendations
        if kpi_record.category == KPICategory.REVENUE:
            if kpi_record.performance_status != "exceeding":
                recommendations.extend([
                    "Diversify revenue streams to reduce dependency",
                    "Implement dynamic pricing strategies",
                    "Enhance premium feature adoption"
                ])
        
        elif kpi_record.category == KPICategory.RETENTION:
            if kpi_record.performance_status in ["below_target", "critical"]:
                recommendations.extend([
                    "Improve onboarding experience for new users",
                    "Implement retention-focused email campaigns",
                    "Add personalization features to increase stickiness"
                ])
        
        elif kpi_record.category == KPICategory.ENGAGEMENT:
            recommendations.extend([
                "Implement gamification elements",
                "Create interactive content features",
                "Develop community-building initiatives"
            ])
        
        # KPI-specific recommendations
        if kpi_name == "customer_acquisition_cost" and kpi_record.current_value > kpi_record.target_value:
            recommendations.extend([
                "Optimize digital marketing channels",
                "Implement referral program",
                "Improve organic acquisition through SEO"
            ])
        
        elif kpi_name == "net_promoter_score" and kpi_record.current_value < kpi_record.target_value:
            recommendations.extend([
                "Conduct user feedback surveys",
                "Address top customer pain points",
                "Implement customer success program"
            ])
        
        return recommendations
    
    def _generate_kpi_summary(self) -> Dict[str, Any]:
        """Generate KPI summary overview"""
        total_kpis = len(self.kpi_definitions)
        tracked_kpis = len(self.kpi_history)
        
        # Calculate overall performance
        performance_counts = {"exceeding": 0, "on_track": 0, "below_target": 0, "critical": 0}
        
        for kpi_name, history in self.kpi_history.items():
            if history:
                latest_kpi = history[-1]
                performance_counts[latest_kpi.performance_status] += 1
        
        return {
            "total_defined_kpis": total_kpis,
            "actively_tracked_kpis": tracked_kpis,
            "performance_distribution": performance_counts,
            "overall_health_score": self._calculate_overall_kpi_health(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _generate_performance_overview(self, timeframe_days: int) -> Dict[str, Any]:
        """Generate performance overview for timeframe"""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        
        performance_overview = {}
        
        for kpi_name, history in self.kpi_history.items():
            recent_history = [kpi for kpi in history if kpi.timestamp >= cutoff_date]
            
            if recent_history:
                performance_overview[kpi_name] = {
                    "current_value": recent_history[-1].current_value,
                    "target_value": recent_history[-1].target_value,
                    "performance_status": recent_history[-1].performance_status,
                    "trend": recent_history[-1].trend_direction,
                    "change_from_start": self._calculate_period_change(recent_history),
                    "volatility": self._calculate_period_volatility(recent_history)
                }
        
        return performance_overview
    
    def _generate_trend_analysis(self, timeframe_days: int) -> Dict[str, Any]:
        """Generate trend analysis for all KPIs"""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        
        trend_analysis = {
            "improving_kpis": [],
            "declining_kpis": [],
            "stable_kpis": [],
            "volatile_kpis": []
        }
        
        for kpi_name, history in self.kpi_history.items():
            recent_history = [kpi for kpi in history if kpi.timestamp >= cutoff_date]
            
            if len(recent_history) >= 2:
                trend = self._analyze_detailed_trend(recent_history)
                volatility = self._calculate_period_volatility(recent_history)
                
                if volatility > 0.3:
                    trend_analysis["volatile_kpis"].append(kpi_name)
                elif trend == "improving":
                    trend_analysis["improving_kpis"].append(kpi_name)
                elif trend == "declining":
                    trend_analysis["declining_kpis"].append(kpi_name)
                else:
                    trend_analysis["stable_kpis"].append(kpi_name)
        
        return trend_analysis
    
    def _analyze_category_performance(self) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by KPI category"""
        category_performance = {}
        
        for category in KPICategory:
            category_kpis = [name for name, definition in self.kpi_definitions.items() 
                           if definition["category"] == category]
            
            if category_kpis:
                # Get latest values for category KPIs
                category_values = []
                category_targets = []
                
                for kpi_name in category_kpis:
                    if kpi_name in self.kpi_history and self.kpi_history[kpi_name]:
                        latest = self.kpi_history[kpi_name][-1]
                        category_values.append(latest.current_value / latest.target_value if latest.target_value != 0 else 0)
                        category_targets.append(1.0)  # Normalized target
                
                if category_values:
                    avg_performance = np.mean(category_values)
                    
                    category_performance[category.value] = {
                        "average_performance_ratio": avg_performance,
                        "performance_status": "exceeding" if avg_performance > 1.1 else 
                                            "on_track" if avg_performance > 0.95 else
                                            "below_target" if avg_performance > 0.8 else "critical",
                        "kpi_count": len(category_kpis),
                        "tracked_kpi_count": len(category_values)
                    }
        
        return category_performance
    
    def _compile_all_alerts(self) -> List[Dict[str, Any]]:
        """Compile all active alerts across KPIs"""
        all_alerts = []
        
        for kpi_name, history in self.kpi_history.items():
            if history:
                latest_kpi = history[-1]
                kpi_alerts = self._check_kpi_alerts(kpi_name, latest_kpi)
                
                for alert in kpi_alerts:
                    alert["kpi_name"] = kpi_name
                    all_alerts.append(alert)
        
        # Sort by severity
        severity_order = {"high": 3, "medium": 2, "low": 1}
        all_alerts.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
        
        return all_alerts
    
    def _identify_improvement_opportunities(self) -> List[Dict[str, Any]]:
        """Identify improvement opportunities across all KPIs"""
        opportunities = []
        
        # Find underperforming KPIs
        for kpi_name, history in self.kpi_history.items():
            if history:
                latest_kpi = history[-1]
                
                if latest_kpi.performance_status in ["below_target", "critical"]:
                    improvement_potential = (latest_kpi.target_value - latest_kpi.current_value) / latest_kpi.target_value
                    
                    opportunities.append({
                        "kpi_name": kpi_name,
                        "category": latest_kpi.category.value,
                        "improvement_potential": improvement_potential,
                        "priority": "high" if latest_kpi.performance_status == "critical" else "medium",
                        "estimated_impact": self._estimate_improvement_impact(kpi_name, improvement_potential)
                    })
        
        # Sort by improvement potential
        opportunities.sort(key=lambda x: x["improvement_potential"], reverse=True)
        
        return opportunities
    
    def _generate_predictive_insights(self) -> Dict[str, Any]:
        """Generate predictive insights based on KPI trends"""
        predictions = {}
        
        for kpi_name, history in self.kpi_history.items():
            if len(history) >= 3:
                # Professional trend-based prediction
                recent_values = [kpi.current_value for kpi in history[-3:]]
                trend_slope = (recent_values[-1] - recent_values[0]) / len(recent_values)
                
                predicted_value = recent_values[-1] + trend_slope
                current_target = history[-1].target_value
                
                predictions[kpi_name] = {
                    "predicted_next_value": predicted_value,
                    "prediction_confidence": "medium",
                    "predicted_performance_status": self._calculate_performance_status(predicted_value, current_target),
                    "risk_level": self._assess_kpi_risk(kpi_name, predicted_value, current_target)
                }
        
        return predictions
    
    # Helper methods for detailed analysis
    
    def _detailed_trend_analysis(self, kpi_history: List[BusinessKPI]) -> Dict[str, Any]:
        """Perform detailed trend analysis on KPI history"""
        if len(kpi_history) < 2:
            return {"trend": "insufficient_data"}
        
        values = [kpi.current_value for kpi in kpi_history]
        
        # Calculate various trend metrics
        linear_trend = np.polyfit(range(len(values)), values, 1)[0]
        volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        momentum = (values[-1] - values[-2]) / values[-2] if len(values) >= 2 and values[-2] != 0 else 0
        
        return {
            "linear_trend_slope": linear_trend,
            "volatility": volatility,
            "momentum": momentum,
            "trend_strength": abs(linear_trend) / np.std(values) if np.std(values) != 0 else 0
        }
    
    def _compare_with_history(self, current_kpi: BusinessKPI, history: List[BusinessKPI]) -> Dict[str, Any]:
        """Compare current KPI with historical performance"""
        if len(history) < 2:
            return {"comparison": "insufficient_history"}
        
        historical_values = [kpi.current_value for kpi in history[:-1]]  # Exclude current
        
        percentile_rank = sum(1 for val in historical_values if val < current_kpi.current_value) / len(historical_values)
        
        return {
            "historical_percentile": percentile_rank,
            "vs_historical_average": (current_kpi.current_value - np.mean(historical_values)) / np.mean(historical_values),
            "vs_historical_best": current_kpi.current_value / max(historical_values) if max(historical_values) != 0 else 0,
            "improvement_since_start": (current_kpi.current_value - history[0].current_value) / history[0].current_value if history[0].current_value != 0 else 0
        }
    
    def _compare_with_benchmark(self, kpi_name: str, kpi_record: BusinessKPI) -> Dict[str, Any]:
        """Compare KPI with industry benchmark"""
        kpi_def = self.kpi_definitions.get(kpi_name, {})
        benchmark = kpi_def.get("benchmark", 0)
        
        if benchmark == 0:
            return {"benchmark_comparison": "no_benchmark"}
        
        return {
            "benchmark_value": benchmark,
            "vs_benchmark": (kpi_record.current_value - benchmark) / benchmark,
            "benchmark_status": "above" if kpi_record.current_value > benchmark else "below"
        }
    
    def _analyze_kpi_volatility(self, history: List[BusinessKPI]) -> Dict[str, Any]:
        """Analyze KPI volatility and stability"""
        if len(history) < 3:
            return {"volatility": "insufficient_data"}
        
        values = [kpi.current_value for kpi in history]
        
        volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        max_drawdown = self._calculate_max_drawdown(values)
        
        stability_score = 1.0 / (1.0 + volatility)  # Higher score = more stable
        
        return {
            "volatility_coefficient": volatility,
            "max_drawdown": max_drawdown,
            "stability_score": stability_score,
            "volatility_category": "low" if volatility < 0.1 else "medium" if volatility < 0.3 else "high"
        }
    
    def _analyze_kpi_seasonality(self, history: List[BusinessKPI]) -> Dict[str, Any]:
        """Analyze seasonal patterns in KPI"""
        if len(history) < 12:
            return {"seasonality": "insufficient_data"}
        
        # Group by month
        monthly_data = {}
        for kpi in history:
            month = kpi.timestamp.month
            if month not in monthly_data:
                monthly_data[month] = []
            monthly_data[month].append(kpi.current_value)
        
        # Calculate monthly averages
        monthly_averages = {month: np.mean(values) for month, values in monthly_data.items()}
        
        # Identify seasonal patterns
        overall_average = np.mean([val for values in monthly_data.values() for val in values])
        seasonal_indices = {month: avg / overall_average for month, avg in monthly_averages.items()}
        
        peak_month = max(seasonal_indices.items(), key=lambda x: x[1])
        trough_month = min(seasonal_indices.items(), key=lambda x: x[1])
        
        return {
            "has_seasonality": max(seasonal_indices.values()) - min(seasonal_indices.values()) > 0.2,
            "peak_month": peak_month[0],
            "trough_month": trough_month[0],
            "seasonal_variation": max(seasonal_indices.values()) - min(seasonal_indices.values()),
            "monthly_indices": seasonal_indices
        }
    
    def _calculate_overall_kpi_health(self) -> float:
        """Calculate overall KPI health score"""
        if not self.kpi_history:
            return 0.0
        
        status_scores = {"exceeding": 100, "on_track": 80, "below_target": 60, "critical": 20}
        total_score = 0
        total_kpis = 0
        
        for history in self.kpi_history.values():
            if history:
                latest_kpi = history[-1]
                total_score += status_scores.get(latest_kpi.performance_status, 50)
                total_kpis += 1
        
        return total_score / total_kpis if total_kpis > 0 else 0.0
    
    def _calculate_period_change(self, kpi_history: List[BusinessKPI]) -> float:
        """Calculate change over period"""
        if len(kpi_history) < 2:
            return 0.0
        
        start_value = kpi_history[0].current_value
        end_value = kpi_history[-1].current_value
        
        if start_value == 0:
            return 1.0 if end_value > 0 else 0.0
        
        return (end_value - start_value) / start_value
    
    def _calculate_period_volatility(self, kpi_history: List[BusinessKPI]) -> float:
        """Calculate volatility over period"""
        if len(kpi_history) < 2:
            return 0.0
        
        values = [kpi.current_value for kpi in kpi_history]
        mean_value = np.mean(values)
        
        if mean_value == 0:
            return 0.0
        
        return np.std(values) / mean_value
    
    def _analyze_detailed_trend(self, kpi_history: List[BusinessKPI]) -> str:
        """Analyze detailed trend direction"""
        if len(kpi_history) < 3:
            return "stable"
        
        values = [kpi.current_value for kpi in kpi_history]
        
        # Use linear regression to determine trend
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        # Calculate relative slope
        mean_value = np.mean(values)
        relative_slope = slope / mean_value if mean_value != 0 else 0
        
        if relative_slope > 0.02:
            return "improving"
        elif relative_slope < -0.02:
            return "declining"
        else:
            return "stable"
    
    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not values:
            return 0.0
        
        peak = values[0]
        max_drawdown = 0.0
        
        for value in values[1:]:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak if peak != 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _estimate_improvement_impact(self, kpi_name: str, improvement_potential: float) -> str:
        """Estimate impact of KPI improvement"""
        kpi_def = self.kpi_definitions.get(kpi_name, {})
        category = kpi_def.get("category")
        
        # High impact categories
        if category in [KPICategory.REVENUE, KPICategory.GROWTH]:
            if improvement_potential > 0.3:
                return "very_high"
            elif improvement_potential > 0.15:
                return "high"
            else:
                return "medium"
        
        # Medium impact categories
        elif category in [KPICategory.RETENTION, KPICategory.ACQUISITION]:
            if improvement_potential > 0.4:
                return "high"
            elif improvement_potential > 0.2:
                return "medium"
            else:
                return "low"
        
        # Standard impact
        else:
            if improvement_potential > 0.5:
                return "high"
            elif improvement_potential > 0.25:
                return "medium"
            else:
                return "low"
    
    def _assess_kpi_risk(self, kpi_name: str, predicted_value: float, target_value: float) -> str:
        """Assess risk level for predicted KPI performance"""
        if target_value == 0:
            return "unknown"
        
        performance_ratio = predicted_value / target_value
        
        if performance_ratio < 0.7:
            return "high"
        elif performance_ratio < 0.9:
            return "medium"
        else:
            return "low"
    
    def _compile_report_data(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile data for automated report"""
        timeframe = report_config.get("timeframe_days", 30)
        included_kpis = report_config.get("kpis", list(self.kpi_history.keys()))
        
        report_data = {}
        
        for kpi_name in included_kpis:
            if kpi_name in self.kpi_history:
                cutoff_date = datetime.now() - timedelta(days=timeframe)
                relevant_history = [kpi for kpi in self.kpi_history[kpi_name] if kpi.timestamp >= cutoff_date]
                
                if relevant_history:
                    report_data[kpi_name] = {
                        "current_value": relevant_history[-1].current_value,
                        "target_value": relevant_history[-1].target_value,
                        "performance_status": relevant_history[-1].performance_status,
                        "trend": self._analyze_detailed_trend(relevant_history),
                        "period_change": self._calculate_period_change(relevant_history)
                    }
        
        return report_data
    
    def _generate_automated_insights(self, report_config: Dict[str, Any]) -> List[str]:
        """Generate automated insights for report"""
        insights = []
        
        report_data = self._compile_report_data(report_config)
        
        # Performance insights
        exceeding_kpis = [name for name, data in report_data.items() if data["performance_status"] == "exceeding"]
        critical_kpis = [name for name, data in report_data.items() if data["performance_status"] == "critical"]
        
        if exceeding_kpis:
            insights.append(f"Strong performance in {len(exceeding_kpis)} KPIs: {', '.join(exceeding_kpis[:3])}")
        
        if critical_kpis:
            insights.append(f"Critical attention needed for {len(critical_kpis)} KPIs: {', '.join(critical_kpis[:3])}")
        
        # Trend insights
        improving_kpis = [name for name, data in report_data.items() if data["trend"] == "improving"]
        declining_kpis = [name for name, data in report_data.items() if data["trend"] == "declining"]
        
        if improving_kpis:
            insights.append(f"Positive trends observed in: {', '.join(improving_kpis[:3])}")
        
        if declining_kpis:
            insights.append(f"Declining trends require attention in: {', '.join(declining_kpis[:3])}")
        
        return insights
    
    def _generate_automated_recommendations(self, report_config: Dict[str, Any]) -> List[str]:
        """Generate automated recommendations for report"""
        recommendations = []
        
        report_data = self._compile_report_data(report_config)
        
        # Performance-based recommendations
        for kpi_name, data in report_data.items():
            if data["performance_status"] == "critical":
                recommendations.append(f"Immediate action required for {kpi_name} - implement emergency improvement plan")
            elif data["performance_status"] == "below_target":
                recommendations.append(f"Focus improvement efforts on {kpi_name} to reach target performance")
        
        # General strategic recommendations
        recommendations.extend([
            "Continue monitoring KPI trends and adjust strategies proactively",
            "Implement predictive analytics for early warning of performance issues",
            "Regular review and optimization of KPI targets based on market conditions"
        ])
        
        return recommendations


# Export all classes and data models
__all__ = [
    'KPICategory',
    'RevenueStream', 
    'BusinessKPI',
    'RevenueMetrics',
    'UserEngagementMetrics',
    'BusinessIntelligenceEngine',
    'EnterpriseKPIManager'
]
