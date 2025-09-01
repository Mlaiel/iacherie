"""Performance Analyzer
Content performance analysis and optimization recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContentPerformance:
    """
Content performance metrics"""
    content_id: str
    platform: str
    views: int
    likes: int
    shares: int
    comments: int
    engagement_rate: float
    revenue: float
    ctr: float  # Click-through rate
    retention_rate: float
    timestamp: datetime


@dataclass
class PerformanceInsight:
    """
Performance insight recommendation"""
    insight_type: str
    title: str
    description: str
    impact_level: str  # high, medium, low
    actionable_steps: List[str]
    expected_improvement: float


class PerformanceAnalyzer:
    """
Content performance analysis and optimization engine"""
    
    def __init__(self):
        self.performance_data = {}
        self.insights_cache = {}
        
    async def analyze_content_performance(
        self,
        content_id: str,
        platform_metrics: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
Analyze content performance across platforms"""
        try:
            performance_records = []
            
            for platform, metrics in platform_metrics.items():
                performance = ContentPerformance(
                    content_id=content_id,
                    platform=platform,
                    views=metrics.get("views", 0),
                    likes=metrics.get("likes", 0),
                    shares=metrics.get("shares", 0),
                    comments=metrics.get("comments", 0),
                    engagement_rate=self._calculate_engagement_rate(metrics),
                    revenue=metrics.get("revenue", 0.0),
                    ctr=metrics.get("ctr", 0.0),
                    retention_rate=metrics.get("retention_rate", 0.0),
                    timestamp=datetime.now()
                )
                performance_records.append(performance)
            
            # Store performance data
            if content_id not in self.performance_data:
                self.performance_data[content_id] = []
            self.performance_data[content_id].extend(performance_records)
            
            # Analyze performance
            analysis = {
                "content_id": content_id,
                "analyzed_at": datetime.now().isoformat(),
                "platform_performance": {},
                "overall_score": 0.0,
                "top_platform": "",
                "engagement_leader": "",
                "revenue_leader": ""
            }
            
            total_score = 0.0
            best_platform = ""
            best_engagement = 0.0
            best_revenue = 0.0
            
            for perf in performance_records:
                platform_score = self._calculate_platform_score(perf)
                
                analysis["platform_performance"][perf.platform] = {
                    "views": perf.views,
                    "engagement_rate": perf.engagement_rate,
                    "revenue": perf.revenue,
                    "performance_score": platform_score,
                    "rank": ""  # Will be set after comparison
                }
                
                total_score += platform_score
                
                if platform_score > 0 and (not best_platform or platform_score > analysis["platform_performance"][best_platform]["performance_score"]):
                    best_platform = perf.platform
                
                if perf.engagement_rate > best_engagement:
                    best_engagement = perf.engagement_rate
                    analysis["engagement_leader"] = perf.platform
                
                if perf.revenue > best_revenue:
                    best_revenue = perf.revenue
                    analysis["revenue_leader"] = perf.platform
            
            analysis["overall_score"] = total_score / len(performance_records) if performance_records else 0
            analysis["top_platform"] = best_platform
            
            # Rank platforms
            sorted_platforms = sorted(
                analysis["platform_performance"].items(),
                key=lambda x: x[1]["performance_score"],
                reverse=True
            )
            
            for i, (platform, data) in enumerate(sorted_platforms):
                analysis["platform_performance"][platform]["rank"] = i + 1
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content performance: {str(e)}")
            return {}
    
    async def predict_viral_potential(
        self,
        content_id: str,
        early_metrics: Dict[str, Any],
        content_type: str = "music"
    ) -> Dict[str, Any]:
        """Predict viral potential based on early performance"""
        try:
            # Early indicators of viral content
            viral_indicators = {
                "early_engagement": early_metrics.get("engagement_rate", 0.0),
                "share_rate": early_metrics.get("shares", 0) / max(early_metrics.get("views", 1), 1),
                "comment_rate": early_metrics.get("comments", 0) / max(early_metrics.get("views", 1), 1),
                "growth_velocity": early_metrics.get("hourly_growth", 0.0),
                "cross_platform_traction": len(early_metrics.get("platforms", [])),
                "time_to_peak": early_metrics.get("hours_since_publish", 24)
            }
            
            # Viral thresholds by content type
            viral_thresholds = {
                "music": {
                    "engagement_rate": 0.08,
                    "share_rate": 0.02,
                    "comment_rate": 0.01,
                    "growth_velocity": 100,
                    "cross_platform": 3
                },
                "video": {
                    "engagement_rate": 0.06,
                    "share_rate": 0.015,
                    "comment_rate": 0.008,
                    "growth_velocity": 150,
                    "cross_platform": 2
                },
                "podcast": {
                    "engagement_rate": 0.04,
                    "share_rate": 0.01,
                    "comment_rate": 0.005,
                    "growth_velocity": 50,
                    "cross_platform": 2
                }
            }
            
            thresholds = viral_thresholds.get(content_type, viral_thresholds["music"])
            
            # Calculate viral score
            viral_score = 0.0
            factor_scores = {}
            
            # Engagement rate factor (25%)
            engagement_score = min(viral_indicators["early_engagement"] / thresholds["engagement_rate"], 1.0) * 25
            factor_scores["engagement"] = engagement_score
            viral_score += engagement_score
            
            # Share rate factor (20%)
            share_score = min(viral_indicators["share_rate"] / thresholds["share_rate"], 1.0) * 20
            factor_scores["shares"] = share_score
            viral_score += share_score
            
            # Comment rate factor (15%)
            comment_score = min(viral_indicators["comment_rate"] / thresholds["comment_rate"], 1.0) * 15
            factor_scores["comments"] = comment_score
            viral_score += comment_score
            
            # Growth velocity factor (25%)
            velocity_score = min(viral_indicators["growth_velocity"] / thresholds["growth_velocity"], 1.0) * 25
            factor_scores["velocity"] = velocity_score
            viral_score += velocity_score
            
            # Cross-platform factor (15%)
            platform_score = min(viral_indicators["cross_platform_traction"] / thresholds["cross_platform"], 1.0) * 15
            factor_scores["cross_platform"] = platform_score
            viral_score += platform_score
            
            # Determine viral potential
            if viral_score >= 80:
                potential = "Very High"
                probability = 0.8 + (viral_score - 80) * 0.01
            elif viral_score >= 60:
                potential = "High"
                probability = 0.6 + (viral_score - 60) * 0.01
            elif viral_score >= 40:
                potential = "Medium"
                probability = 0.3 + (viral_score - 40) * 0.015
            elif viral_score >= 20:
                potential = "Low"
                probability = 0.1 + (viral_score - 20) * 0.01
            else:
                potential = "Very Low"
                probability = viral_score * 0.005
            
            prediction = {
                "content_id": content_id,
                "content_type": content_type,
                "viral_score": viral_score,
                "viral_potential": potential,
                "probability": min(1.0, probability),
                "factor_breakdown": factor_scores,
                "indicators": viral_indicators,
                "recommendations": self._generate_viral_recommendations(viral_score, factor_scores),
                "predicted_at": datetime.now().isoformat()
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting viral potential: {str(e)}")
            return {}
    
    async def analyze_audience_engagement(
        self,
        content_id: str,
        engagement_data: Dict[str, List]
    ) -> Dict[str, Any]:
        """Analyze audience engagement patterns"""
        try:
            # Analyze engagement timeline
            timeline_analysis = self._analyze_engagement_timeline(engagement_data)
            
            # Analyze engagement types
            engagement_breakdown = {
                "likes_ratio": 0.0,
                "shares_ratio": 0.0,
                "comments_ratio": 0.0,
                "saves_ratio": 0.0
            }
            
            total_engagement = sum(
                sum(engagement_data.get(key, []))
                for key in ["likes", "shares", "comments", "saves"]
            )
            
            if total_engagement > 0:
                engagement_breakdown = {
                    "likes_ratio": sum(engagement_data.get("likes", [])) / total_engagement,
                    "shares_ratio": sum(engagement_data.get("shares", [])) / total_engagement,
                    "comments_ratio": sum(engagement_data.get("comments", [])) / total_engagement,
                    "saves_ratio": sum(engagement_data.get("saves", [])) / total_engagement
                }
            
            # Determine engagement type
            dominant_type = max(engagement_breakdown.items(), key=lambda x: x[1])[0].replace("_ratio", "")
            
            # Calculate engagement quality score
            quality_score = self._calculate_engagement_quality(engagement_breakdown)
            
            analysis = {
                "content_id": content_id,
                "timeline_analysis": timeline_analysis,
                "engagement_breakdown": engagement_breakdown,
                "dominant_engagement_type": dominant_type,
                "engagement_quality_score": quality_score,
                "audience_sentiment": self._analyze_audience_sentiment(engagement_data),
                "optimal_posting_insights": self._get_optimal_posting_insights(engagement_data),
                "analyzed_at": datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing audience engagement: {str(e)}")
            return {}
    
    async def generate_optimization_recommendations(
        self,
        content_id: str,
        performance_history: List[Dict]
    ) -> List[PerformanceInsight]:
        """Generate actionable optimization recommendations"""
        try:
            insights = []
            
            # Analyze performance trends
            if len(performance_history) >= 3:
                recent_performance = performance_history[-3:]
                
                # Check for declining engagement
                engagement_trend = [p.get("engagement_rate", 0) for p in recent_performance]
                if all(engagement_trend[i] > engagement_trend[i+1] for i in range(len(engagement_trend)-1)):
                    insights.append(PerformanceInsight(
                        insight_type="engagement_decline",
                        title="Declining Engagement Detected",
                        description="Engagement rates have been consistently declining over recent posts",
                        impact_level="high",
                        actionable_steps=[
                            "Analyze top-performing content for successful elements",
                            "Experiment with different content formats",
                            "Increase audience interaction through polls and questions",
                            "Review posting times and frequency"
                        ],
                        expected_improvement=15.0
                    ))
                
                # Check for low cross-platform performance
                platform_count = len(set(p.get("platform") for p in recent_performance))
                if platform_count < 3:
                    insights.append(PerformanceInsight(
                        insight_type="platform_expansion",
                        title="Limited Platform Presence",
                        description="Content is not distributed across enough platforms",
                        impact_level="medium",
                        actionable_steps=[
                            "Expand to additional social media platforms",
                            "Adapt content format for each platform",
                            "Create platform-specific engagement strategies",
                            "Track cross-platform performance metrics"
                        ],
                        expected_improvement=25.0
                    ))
                
                # Check for revenue optimization opportunities
                revenue_performance = [p.get("revenue", 0) for p in recent_performance]
                avg_revenue = sum(revenue_performance) / len(revenue_performance)
                
                if avg_revenue < 50:  # Below average threshold
                    insights.append(PerformanceInsight(
                        insight_type="revenue_optimization",
                        title="Revenue Optimization Opportunity",
                        description="Revenue generation is below optimal levels",
                        impact_level="high",
                        actionable_steps=[
                            "Explore licensing opportunities",
                            "Implement call-to-action strategies",
                            "Consider premium content offerings",
                            "Analyze monetization best practices"
                        ],
                        expected_improvement=40.0
                    ))
            
            # General content quality insights
            if not insights:
                insights.append(PerformanceInsight(
                    insight_type="general_optimization",
                    title="Content Performance Enhancement",
                    description="Continue optimizing content for better performance",
                    impact_level="medium",
                    actionable_steps=[
                        "Monitor audience feedback regularly",
                        "A/B test different content approaches",
                        "Focus on trending topics and hashtags",
                        "Collaborate with other creators"
                    ],
                    expected_improvement=20.0
                ))
            
            logger.info(f"Generated {len(insights)} optimization insights for content {content_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {str(e)}")
            return []
    
    def _calculate_engagement_rate(self, metrics: Dict) -> float:
        """Calculate engagement rate from metrics"""
        try:
            views = metrics.get("views", 0)
            if views == 0:
                return 0.0
                
            total_engagement = (
                metrics.get("likes", 0) +
                metrics.get("shares", 0) +
                metrics.get("comments", 0)
            )
            
            return total_engagement / views
            
        except Exception as e:
            logger.error(f"Error calculating engagement rate: {str(e)}")
            return 0.0
    
    def _calculate_platform_score(self, performance: ContentPerformance) -> float:
        """Calculate overall platform performance score"""
        try:
            # Weighted scoring
            view_score = min(performance.views / 10000, 1.0) * 30  # Max 30 points
            engagement_score = min(performance.engagement_rate / 0.1, 1.0) * 25  # Max 25 points
            revenue_score = min(performance.revenue / 100, 1.0) * 25  # Max 25 points
            retention_score = performance.retention_rate * 20  # Max 20 points
            
            total_score = view_score + engagement_score + revenue_score + retention_score
            return min(100, total_score)
            
        except Exception as e:
            logger.error(f"Error calculating platform score: {str(e)}")
            return 0.0
    
    def _analyze_engagement_timeline(self, engagement_data: Dict[str, List]) -> Dict:
        """Analyze engagement timeline patterns"""
        try:
            timeline = {
                "peak_hours": [],
                "engagement_velocity": 0.0,
                "sustained_engagement": False
            }
            
            # Simplified timeline analysis
            likes_timeline = engagement_data.get("likes", [])
            if likes_timeline:
                # Find peak engagement hours (simplified)
                max_engagement = max(likes_timeline)
                peak_indices = [i for i, val in enumerate(likes_timeline) if val == max_engagement]
                timeline["peak_hours"] = peak_indices
                
                # Calculate velocity (change rate)
                if len(likes_timeline) > 1:
                    timeline["engagement_velocity"] = (likes_timeline[-1] - likes_timeline[0]) / len(likes_timeline)
                
                # Check if engagement is sustained
                timeline["sustained_engagement"] = len([x for x in likes_timeline if x > max_engagement * 0.5]) > len(likes_timeline) * 0.3
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error analyzing engagement timeline: {str(e)}")
            return {}
    
    def _calculate_engagement_quality(self, engagement_breakdown: Dict) -> float:
        """Calculate engagement quality score"""
        try:
            # Quality weights (comments and shares are higher quality than likes)
            quality_weights = {
                "likes_ratio": 0.2,
                "shares_ratio": 0.4,
                "comments_ratio": 0.3,
                "saves_ratio": 0.1
            }
            
            quality_score = sum(
                engagement_breakdown.get(key, 0) * weight
                for key, weight in quality_weights.items()
            )
            
            return min(100, quality_score * 100)
            
        except Exception as e:
            logger.error(f"Error calculating engagement quality: {str(e)}")
            return 50.0
    
    def _analyze_audience_sentiment(self, engagement_data: Dict) -> str:
        """Analyze audience sentiment from engagement patterns"""
        try:
            likes = sum(engagement_data.get("likes", []))
            shares = sum(engagement_data.get("shares", []))
            comments = sum(engagement_data.get("comments", []))
            
            if shares > likes * 0.1:
                return "Highly Positive"
            elif comments > likes * 0.05:
                return "Engaged"
            elif likes > 0:
                return "Positive"
            else:
                return "Neutral"
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return "Unknown"
    
    def _get_optimal_posting_insights(self, engagement_data: Dict) -> Dict:
        """Get insights about optimal posting times"""
        try:
            # Simplified optimal timing analysis
            return {
                "best_day": "Tuesday",  # Placeholder
                "best_time": "18:00",   # Placeholder
                "frequency_recommendation": "3-4 posts per week",
                "confidence": 0.7
            }
            
        except Exception as e:
            logger.error(f"Error getting posting insights: {str(e)}")
            return {}
    
    def _generate_viral_recommendations(
        self,
        viral_score: float,
        factor_scores: Dict
    ) -> List[str]:
        """Generate recommendations to improve viral potential"""
        try:
            recommendations = []
            
            if factor_scores.get("engagement", 0) < 15:
                recommendations.append("Improve content engagement through interactive elements")
            
            if factor_scores.get("shares", 0) < 15:
                recommendations.append("Create more shareable content with emotional appeal")
            
            if factor_scores.get("velocity", 0) < 20:
                recommendations.append("Optimize posting times for maximum initial traction")
            
            if factor_scores.get("cross_platform", 0) < 10:
                recommendations.append("Expand distribution across multiple platforms")
            
            if viral_score < 40:
                recommendations.extend([
                    "Focus on trending topics and hashtags",
                    "Collaborate with influencers and other creators",
                    "Improve content quality and production value"
                ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating viral recommendations: {str(e)}")
            return ["Continue monitoring performance and optimize based on analytics"]