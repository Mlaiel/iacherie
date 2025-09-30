"""Creator Performance Reports System
==================================

Advanced creator performance analytics and reporting for Ainflue Creator Economy.
Comprehensive tracking of creator engagement, content performance, revenue analysis,
and growth trajectory with multi-platform correlation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


class CreatorTier(Enum):
    """Creator performance tiers"""
    EMERGING = "emerging"
    RISING = "rising"
    ESTABLISHED = "established"
    ELITE = "elite"
    LEGENDARY = "legendary"


class ContentCategory(Enum):
    """Content performance categories"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"
    INTERACTIVE = "interactive"


class PerformanceMetric(Enum):
    """Performance tracking metrics"""
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    REVENUE_PER_POST = "revenue_per_post"
    GROWTH_RATE = "growth_rate"
    RETENTION_RATE = "retention_rate"
    VIRALITY_SCORE = "virality_score"


@dataclass
class CreatorProfile:
    """Creator profile data structure"""
    creator_id: str
    username: str
    display_name: str
    tier: CreatorTier
    categories: List[ContentCategory]
    join_date: datetime
    verification_status: bool
    platforms: List[str]
    total_followers: int
    total_content: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceData:
    """Creator performance data"""
    creator_id: str
    period_start: datetime
    period_end: datetime
    engagement_metrics: Dict[str, float]
    content_metrics: Dict[str, int]
    revenue_metrics: Dict[str, float]
    growth_metrics: Dict[str, float]
    platform_breakdown: Dict[str, Dict[str, Any]]
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContentPerformance:
    """Individual content performance"""
    content_id: str
    creator_id: str
    category: ContentCategory
    title: str
    published_at: datetime
    platforms: List[str]
    engagement: Dict[str, int]
    reach: Dict[str, int]
    revenue: Dict[str, float]
    virality_score: float
    quality_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class CreatorPerformanceReports:
    """Enterprise creator performance reporting system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize creator performance reporting system"""
        self.config = config or {}
        self.report_id = str(uuid.uuid4())
        self.cache = {}
        self.analytics_engine = None
        
        # Performance thresholds
        self.tier_thresholds = {
            CreatorTier.EMERGING: {"followers": 1000, "engagement": 2.0},
            CreatorTier.RISING: {"followers": 10000, "engagement": 3.0},
            CreatorTier.ESTABLISHED: {"followers": 100000, "engagement": 4.0},
            CreatorTier.ELITE: {"followers": 1000000, "engagement": 5.0},
            CreatorTier.LEGENDARY: {"followers": 10000000, "engagement": 6.0}
        }
        
        logger.info("🎯 Creator Performance Reports initialized")

    async def generate_creator_performance_report(
        self,
        creator_id: Optional[str] = None,
        time_period: int = 30,
        include_predictions: bool = True,
        export_format: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate comprehensive creator performance report"""
        try:
            logger.info(f"📊 Generating creator performance report for {creator_id or 'all creators'}")
            
            # Get creator data
            if creator_id:
                creators = [await self._get_creator_profile(creator_id)]
            else:
                creators = await self._get_all_active_creators()
            
            report_data = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "period_days": time_period,
                "total_creators": len(creators),
                "creator_reports": [],
                "aggregated_insights": {},
                "performance_trends": {},
                "tier_distribution": {},
                "platform_analysis": {}
            }
            
            # Generate individual creator reports
            for creator in creators:
                creator_report = await self._generate_individual_creator_report(
                    creator, time_period, include_predictions
                )
                report_data["creator_reports"].append(creator_report)
            
            # Generate aggregated insights
            report_data["aggregated_insights"] = await self._generate_aggregated_insights(
                report_data["creator_reports"]
            )
            
            # Generate performance trends
            report_data["performance_trends"] = await self._analyze_performance_trends(
                report_data["creator_reports"], time_period
            )
            
            # Analyze tier distribution
            report_data["tier_distribution"] = self._analyze_tier_distribution(creators)
            
            # Platform performance analysis
            report_data["platform_analysis"] = await self._analyze_platform_performance(
                report_data["creator_reports"]
            )
            
            # Generate visualizations
            if export_format in ["comprehensive", "visual"]:
                report_data["visualizations"] = await self._generate_performance_visualizations(
                    report_data
                )
            
            logger.info("✅ Creator performance report generated successfully")
            return report_data
            
        except Exception as e:
            logger.error(f"❌ Error generating creator performance report: {e}")
            raise

    async def _generate_individual_creator_report(
        self,
        creator: CreatorProfile,
        time_period: int,
        include_predictions: bool
    ) -> Dict[str, Any]:
        """Generate performance report for individual creator"""
        
        # Get performance data
        performance_data = await self._get_creator_performance_data(
            creator.creator_id, time_period
        )
        
        # Get content performance
        content_performance = await self._get_content_performance_data(
            creator.creator_id, time_period
        )
        
        # Calculate key metrics
        engagement_rate = self._calculate_engagement_rate(performance_data)
        growth_rate = self._calculate_growth_rate(performance_data)
        revenue_efficiency = self._calculate_revenue_efficiency(performance_data)
        content_quality_score = self._calculate_content_quality_score(content_performance)
        
        creator_report = {
            "creator_profile": asdict(creator),
            "performance_period": {
                "start_date": (datetime.now(timezone.utc) - timedelta(days=time_period)).isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat(),
                "days": time_period
            },
            "key_metrics": {
                "engagement_rate": engagement_rate,
                "growth_rate": growth_rate,
                "revenue_efficiency": revenue_efficiency,
                "content_quality_score": content_quality_score,
                "total_content_created": len(content_performance),
                "total_revenue": sum(c.revenue.get("total", 0) for c in content_performance),
                "average_reach": sum(sum(c.reach.values()) for c in content_performance) / max(len(content_performance), 1)
            },
            "platform_breakdown": await self._analyze_creator_platform_performance(
                creator.creator_id, performance_data
            ),
            "content_analysis": await self._analyze_creator_content_performance(
                content_performance
            ),
            "audience_insights": await self._generate_audience_insights(
                creator.creator_id, time_period
            ),
            "ranking": await self._calculate_creator_ranking(creator),
            "recommendations": await self._generate_creator_recommendations(
                creator, performance_data, content_performance
            )
        }
        
        # Add predictions if requested
        if include_predictions:
            creator_report["predictions"] = await self._generate_creator_predictions(
                creator, performance_data
            )
        
        return creator_report

    async def _get_creator_performance_data(
        self, creator_id: str, time_period: int
    ) -> PerformanceData:
        """Get creator performance data for specified period"""
        # Simulate getting performance data from database
        # In production, this would connect to the actual data sources
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=time_period)
        
        return PerformanceData(
            creator_id=creator_id,
            period_start=start_date,
            period_end=end_date,
            engagement_metrics={
                "likes": 15420.0,
                "comments": 3200.0,
                "shares": 1890.0,
                "saves": 2340.0,
                "click_through_rate": 4.2
            },
            content_metrics={
                "total_posts": 45,
                "videos": 20,
                "images": 15,
                "audio": 8,
                "mixed_media": 2
            },
            revenue_metrics={
                "total_revenue": 12450.50,
                "commission_revenue": 8900.25,
                "brand_partnerships": 3550.25,
                "direct_sales": 0.0
            },
            growth_metrics={
                "follower_growth": 8.5,
                "engagement_growth": 12.3,
                "revenue_growth": 15.7
            },
            platform_breakdown={
                "youtube": {"engagement": 45000, "revenue": 6800.25},
                "instagram": {"engagement": 32000, "revenue": 3200.15},
                "tiktok": {"engagement": 28000, "revenue": 2450.10}
            }
        )

    def _calculate_engagement_rate(self, performance_data: PerformanceData) -> float:
        """Calculate overall engagement rate"""
        total_engagement = sum(performance_data.engagement_metrics.values())
        total_reach = sum(
            platform_data.get("reach", 0) 
            for platform_data in performance_data.platform_breakdown.values()
        )
        
        if total_reach == 0:
            return 0.0
        
        return round((total_engagement / total_reach) * 100, 2)

    def _calculate_growth_rate(self, performance_data: PerformanceData) -> float:
        """Calculate weighted growth rate"""
        growth_metrics = performance_data.growth_metrics
        
        # Weight different growth metrics
        weights = {
            "follower_growth": 0.3,
            "engagement_growth": 0.4,
            "revenue_growth": 0.3
        }
        
        weighted_growth = sum(
            growth_metrics.get(metric, 0) * weight
            for metric, weight in weights.items()
        )
        
        return round(weighted_growth, 2)

    def _calculate_revenue_efficiency(self, performance_data: PerformanceData) -> float:
        """Calculate revenue per engagement"""
        total_revenue = performance_data.revenue_metrics.get("total_revenue", 0)
        total_engagement = sum(performance_data.engagement_metrics.values())
        
        if total_engagement == 0:
            return 0.0
        
        return round(total_revenue / total_engagement, 4)

    def _calculate_content_quality_score(self, content_performance: List[ContentPerformance]) -> float:
        """Calculate average content quality score"""
        if not content_performance:
            return 0.0
        
        total_score = sum(content.quality_score for content in content_performance)
        return round(total_score / len(content_performance), 2)

    async def _analyze_creator_platform_performance(
        self, creator_id: str, performance_data: PerformanceData
    ) -> Dict[str, Any]:
        """Analyze performance across different platforms"""
        platform_analysis = {}
        
        for platform, data in performance_data.platform_breakdown.items():
            engagement = data.get("engagement", 0)
            revenue = data.get("revenue", 0)
            
            platform_analysis[platform] = {
                "engagement": engagement,
                "revenue": revenue,
                "engagement_percentage": round(
                    (engagement / sum(p.get("engagement", 0) for p in performance_data.platform_breakdown.values())) * 100, 2
                ),
                "revenue_percentage": round(
                    (revenue / sum(p.get("revenue", 0) for p in performance_data.platform_breakdown.values())) * 100, 2
                ),
                "revenue_per_engagement": round(revenue / engagement, 4) if engagement > 0 else 0
            }
        
        return platform_analysis

    async def _analyze_creator_content_performance(
        self, content_performance: List[ContentPerformance]
    ) -> Dict[str, Any]:
        """Analyze content performance patterns"""
        if not content_performance:
            return {}
        
        # Group by category
        category_performance = {}
        for content in content_performance:
            category = content.category.value
            if category not in category_performance:
                category_performance[category] = {
                    "count": 0,
                    "total_engagement": 0,
                    "total_revenue": 0,
                    "avg_quality": 0,
                    "avg_virality": 0
                }
            
            category_data = category_performance[category]
            category_data["count"] += 1
            category_data["total_engagement"] += sum(content.engagement.values())
            category_data["total_revenue"] += sum(content.revenue.values())
            category_data["avg_quality"] += content.quality_score
            category_data["avg_virality"] += content.virality_score
        
        # Calculate averages
        for category_data in category_performance.values():
            count = category_data["count"]
            category_data["avg_engagement"] = round(category_data["total_engagement"] / count, 2)
            category_data["avg_revenue"] = round(category_data["total_revenue"] / count, 2)
            category_data["avg_quality"] = round(category_data["avg_quality"] / count, 2)
            category_data["avg_virality"] = round(category_data["avg_virality"] / count, 2)
        
        # Find best performing content
        best_content = max(content_performance, key=lambda x: sum(x.engagement.values()))
        most_viral = max(content_performance, key=lambda x: x.virality_score)
        highest_revenue = max(content_performance, key=lambda x: sum(x.revenue.values()))
        
        return {
            "category_breakdown": category_performance,
            "top_performers": {
                "highest_engagement": {
                    "content_id": best_content.content_id,
                    "title": best_content.title,
                    "engagement": sum(best_content.engagement.values())
                },
                "most_viral": {
                    "content_id": most_viral.content_id,
                    "title": most_viral.title,
                    "virality_score": most_viral.virality_score
                },
                "highest_revenue": {
                    "content_id": highest_revenue.content_id,
                    "title": highest_revenue.title,
                    "revenue": sum(highest_revenue.revenue.values())
                }
            },
            "performance_patterns": await self._identify_content_patterns(content_performance)
        }

    async def _generate_audience_insights(
        self, creator_id: str, time_period: int
    ) -> Dict[str, Any]:
        """Generate audience insights and demographics"""
        # Simulate audience data analysis
        return {
            "demographics": {
                "age_groups": {
                    "18-24": 25.4,
                    "25-34": 42.1,
                    "35-44": 20.3,
                    "45-54": 8.7,
                    "55+": 3.5
                },
                "gender_distribution": {
                    "female": 58.3,
                    "male": 40.2,
                    "other": 1.5
                },
                "geographic_distribution": {
                    "north_america": 35.2,
                    "europe": 28.7,
                    "asia": 24.1,
                    "latin_america": 8.3,
                    "other": 3.7
                }
            },
            "engagement_patterns": {
                "most_active_hours": ["19:00-21:00", "12:00-14:00"],
                "most_active_days": ["tuesday", "wednesday", "saturday"],
                "average_session_duration": 4.2,
                "return_rate": 68.5
            },
            "interests": {
                "technology": 78.3,
                "entertainment": 65.2,
                "lifestyle": 52.1,
                "education": 41.7,
                "business": 38.9
            }
        }

    async def _calculate_creator_ranking(self, creator: CreatorProfile) -> Dict[str, Any]:
        """Calculate creator ranking within tier and overall"""
        # Simulate ranking calculation
        return {
            "overall_rank": 1247,
            "tier_rank": 23,
            "category_rank": 156,
            "percentile": 92.3,
            "tier_percentile": 88.7,
            "trending_direction": "up",
            "rank_change_30d": 45
        }

    async def _generate_creator_recommendations(
        self,
        creator: CreatorProfile,
        performance_data: PerformanceData,
        content_performance: List[ContentPerformance]
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations for creator improvement"""
        recommendations = []
        
        # Analyze performance gaps
        engagement_rate = self._calculate_engagement_rate(performance_data)
        
        if engagement_rate < 3.0:
            recommendations.append({
                "type": "engagement_improvement",
                "priority": "high",
                "title": "Boost Engagement Rate",
                "description": "Your engagement rate is below average. Focus on interactive content and community building.",
                "action_items": [
                    "Increase story usage and polls",
                    "Respond to comments within 2 hours",
                    "Create content that encourages discussion"
                ],
                "expected_impact": "15-25% engagement increase"
            })
        
        # Content diversification
        category_counts = {}
        for content in content_performance:
            category = content.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        if len(category_counts) < 3:
            recommendations.append({
                "type": "content_diversification",
                "priority": "medium",
                "title": "Diversify Content Types",
                "description": "Expand into new content categories to reach broader audiences.",
                "action_items": [
                    "Experiment with video content",
                    "Try interactive media formats",
                    "Create educational content"
                ],
                "expected_impact": "10-20% audience growth"
            })
        
        # Revenue optimization
        total_revenue = performance_data.revenue_metrics.get("total_revenue", 0)
        if total_revenue < 10000:
            recommendations.append({
                "type": "monetization",
                "priority": "high",
                "title": "Optimize Revenue Streams",
                "description": "Explore additional monetization opportunities to increase revenue.",
                "action_items": [
                    "Apply for brand partnership programs",
                    "Create premium content offerings",
                    "Develop merchandise or digital products"
                ],
                "expected_impact": "30-50% revenue increase"
            })
        
        return recommendations

    async def _generate_creator_predictions(
        self,
        creator: CreatorProfile,
        performance_data: PerformanceData
    ) -> Dict[str, Any]:
        """Generate predictive analytics for creator performance"""
        # Simulate ML-based predictions
        current_growth = performance_data.growth_metrics.get("follower_growth", 0)
        
        return {
            "30_day_forecast": {
                "follower_growth": round(current_growth * 1.1, 2),
                "engagement_growth": round(current_growth * 0.9, 2),
                "revenue_growth": round(current_growth * 1.3, 2),
                "confidence": 85.2
            },
            "90_day_forecast": {
                "follower_growth": round(current_growth * 2.8, 2),
                "engagement_growth": round(current_growth * 2.4, 2),
                "revenue_growth": round(current_growth * 3.2, 2),
                "confidence": 72.5
            },
            "growth_trajectory": "accelerating",
            "risk_factors": [
                "Market saturation in primary category",
                "Platform algorithm changes"
            ],
            "opportunities": [
                "Emerging platform expansion",
                "Cross-platform collaboration potential"
            ]
        }

    async def _get_creator_profile(self, creator_id: str) -> CreatorProfile:
        """Get creator profile data"""
        # Simulate database query
        return CreatorProfile(
            creator_id=creator_id,
            username="creator_example",
            display_name="Creator Example",
            tier=CreatorTier.RISING,
            categories=[ContentCategory.VIDEO, ContentCategory.IMAGE],
            join_date=datetime.now(timezone.utc) - timedelta(days=365),
            verification_status=True,
            platforms=["youtube", "instagram", "tiktok"],
            total_followers=75000,
            total_content=234
        )

    async def _get_all_active_creators(self) -> List[CreatorProfile]:
        """Get all active creator profiles"""
        # Simulate getting multiple creators
        return [await self._get_creator_profile(f"creator_{i}") for i in range(1, 11)]

    async def _get_content_performance_data(
        self, creator_id: str, time_period: int
    ) -> List[ContentPerformance]:
        """Get content performance data for creator"""
        # Simulate content performance data
        content_list = []
        for i in range(1, 16):  # 15 pieces of content
            content = ContentPerformance(
                content_id=f"content_{creator_id}_{i}",
                creator_id=creator_id,
                category=ContentCategory.VIDEO,
                title=f"Amazing Content {i}",
                published_at=datetime.now(timezone.utc) - timedelta(days=i*2),
                platforms=["youtube", "instagram"],
                engagement={"likes": 1200 + i*50, "comments": 45 + i*3, "shares": 23 + i*2},
                reach={"organic": 15000 + i*500, "paid": 3000 + i*100},
                revenue={"total": 150.25 + i*10},
                virality_score=round(3.5 + (i % 5) * 0.8, 2),
                quality_score=round(7.2 + (i % 3) * 0.6, 2)
            )
            content_list.append(content)
        
        return content_list

    async def _identify_content_patterns(
        self, content_performance: List[ContentPerformance]
    ) -> Dict[str, Any]:
        """Identify patterns in content performance"""
        return {
            "optimal_posting_times": ["19:00", "12:00", "20:00"],
            "best_performing_categories": ["video", "mixed_media"],
            "trending_topics": ["technology", "lifestyle", "education"],
            "seasonal_patterns": {
                "high_engagement_months": ["march", "july", "november"],
                "low_engagement_months": ["january", "august"]
            }
        }

    async def _generate_aggregated_insights(
        self, creator_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate aggregated insights across all creators"""
        if not creator_reports:
            return {}
        
        # Calculate aggregated metrics
        total_engagement = sum(
            report["key_metrics"]["engagement_rate"] for report in creator_reports
        )
        avg_engagement = round(total_engagement / len(creator_reports), 2)
        
        total_revenue = sum(
            report["key_metrics"]["total_revenue"] for report in creator_reports
        )
        
        return {
            "average_engagement_rate": avg_engagement,
            "total_platform_revenue": total_revenue,
            "top_performing_creators": sorted(
                creator_reports,
                key=lambda x: x["key_metrics"]["engagement_rate"],
                reverse=True
            )[:10],
            "growth_leaders": sorted(
                creator_reports,
                key=lambda x: x["key_metrics"]["growth_rate"],
                reverse=True
            )[:5],
            "platform_distribution": await self._analyze_platform_usage(creator_reports)
        }

    async def _analyze_performance_trends(
        self, creator_reports: List[Dict[str, Any]], time_period: int
    ) -> Dict[str, Any]:
        """Analyze performance trends across the platform"""
        return {
            "engagement_trend": "increasing",
            "revenue_trend": "strong_growth",
            "creator_growth_trend": "accelerating",
            "content_volume_trend": "steady",
            "quality_trend": "improving",
            "seasonal_insights": {
                "peak_months": ["march", "july", "november"],
                "low_months": ["january", "august"],
                "predicted_next_peak": "march"
            }
        }

    def _analyze_tier_distribution(self, creators: List[CreatorProfile]) -> Dict[str, Any]:
        """Analyze creator tier distribution"""
        tier_counts = {}
        for creator in creators:
            tier = creator.tier.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        total_creators = len(creators)
        tier_percentages = {
            tier: round((count / total_creators) * 100, 2)
            for tier, count in tier_counts.items()
        }
        
        return {
            "counts": tier_counts,
            "percentages": tier_percentages,
            "distribution_health": "balanced"
        }

    async def _analyze_platform_performance(
        self, creator_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze performance across different platforms"""
        platform_data = {}
        
        for report in creator_reports:
            platform_breakdown = report.get("platform_breakdown", {})
            for platform, data in platform_breakdown.items():
                if platform not in platform_data:
                    platform_data[platform] = {
                        "total_engagement": 0,
                        "total_revenue": 0,
                        "creator_count": 0
                    }
                
                platform_data[platform]["total_engagement"] += data.get("engagement", 0)
                platform_data[platform]["total_revenue"] += data.get("revenue", 0)
                platform_data[platform]["creator_count"] += 1
        
        # Calculate averages
        for platform, data in platform_data.items():
            count = data["creator_count"]
            if count > 0:
                data["avg_engagement"] = round(data["total_engagement"] / count, 2)
                data["avg_revenue"] = round(data["total_revenue"] / count, 2)
                data["revenue_per_engagement"] = round(
                    data["total_revenue"] / data["total_engagement"], 4
                ) if data["total_engagement"] > 0 else 0
        
        return platform_data

    async def _analyze_platform_usage(
        self, creator_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze platform usage distribution"""
        platform_usage = {}
        
        for report in creator_reports:
            platforms = report["creator_profile"].get("platforms", [])
            for platform in platforms:
                platform_usage[platform] = platform_usage.get(platform, 0) + 1
        
        total_usage = sum(platform_usage.values())
        platform_percentages = {
            platform: round((count / total_usage) * 100, 2)
            for platform, count in platform_usage.items()
        }
        
        return {
            "usage_counts": platform_usage,
            "usage_percentages": platform_percentages,
            "most_popular": max(platform_usage.keys(), key=platform_usage.get),
            "multi_platform_creators": sum(
                1 for report in creator_reports
                if len(report["creator_profile"].get("platforms", [])) > 1
            )
        }

    async def _generate_performance_visualizations(
        self, report_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate performance visualization charts"""
        visualizations = {}
        
        try:
            # Set style for professional charts
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # Engagement rate distribution
            plt.figure(figsize=(10, 6))
            engagement_rates = [
                report["key_metrics"]["engagement_rate"]
                for report in report_data["creator_reports"]
            ]
            plt.hist(engagement_rates, bins=20, alpha=0.7, edgecolor='black')
            plt.title('Creator Engagement Rate Distribution')
            plt.xlabel('Engagement Rate (%)')
            plt.ylabel('Number of Creators')
            plt.grid(True, alpha=0.3)
            
            # Save to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            visualizations["engagement_distribution"] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            # Platform performance comparison
            plt.figure(figsize=(12, 6))
            platform_data = report_data["platform_analysis"]
            platforms = list(platform_data.keys())
            revenues = [platform_data[p]["total_revenue"] for p in platforms]
            
            plt.bar(platforms, revenues, alpha=0.8)
            plt.title('Platform Revenue Comparison')
            plt.xlabel('Platform')
            plt.ylabel('Total Revenue ($)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            visualizations["platform_revenue"] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            # Tier distribution pie chart
            plt.figure(figsize=(8, 8))
            tier_data = report_data["tier_distribution"]["percentages"]
            plt.pie(tier_data.values(), labels=tier_data.keys(), autopct='%1.1f%%')
            plt.title('Creator Tier Distribution')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            visualizations["tier_distribution"] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            logger.info("✅ Performance visualizations generated successfully")
            
        except Exception as e:
            logger.error(f"❌ Error generating visualizations: {e}")
            visualizations["error"] = str(e)
        
        return visualizations

    async def export_report(
        self,
        report_data: Dict[str, Any],
        format_type: str = "json",
        include_visualizations: bool = True
    ) -> Union[str, bytes]:
        """Export report in specified format"""
        try:
            if format_type.lower() == "json":
                return json.dumps(report_data, indent=2, default=str)
            
            elif format_type.lower() == "csv":
                # Convert to DataFrame for CSV export
                df_data = []
                for report in report_data["creator_reports"]:
                    profile = report["creator_profile"]
                    metrics = report["key_metrics"]
                    
                    df_data.append({
                        "creator_id": profile["creator_id"],
                        "username": profile["username"],
                        "tier": profile["tier"],
                        "engagement_rate": metrics["engagement_rate"],
                        "growth_rate": metrics["growth_rate"],
                        "total_revenue": metrics["total_revenue"],
                        "content_quality_score": metrics["content_quality_score"]
                    })
                
                df = pd.DataFrame(df_data)
                return df.to_csv(index=False)
            
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logger.error(f"❌ Error exporting report: {e}")
            raise


# Initialize the creator performance reports system
creator_performance_reports = CreatorPerformanceReports()