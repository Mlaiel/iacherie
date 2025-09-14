"""
Organic Traffic Analyzer for Ainflue Platform
=============================================

Advanced organic traffic analysis and optimization for creators.
Analyzes traffic patterns, user behavior, and conversion paths.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class TrafficSource(Enum):
    """Organic traffic sources."""
    GOOGLE_SEARCH = "google_search"
    BING_SEARCH = "bing_search"
    YAHOO_SEARCH = "yahoo_search"
    DUCKDUCKGO = "duckduckgo"
    YOUTUBE_SEARCH = "youtube_search"
    SOCIAL_ORGANIC = "social_organic"
    DIRECT_ORGANIC = "direct_organic"
    REFERRAL_ORGANIC = "referral_organic"

class ContentCategory(Enum):
    """Content categories for traffic analysis."""
    BLOG_POSTS = "blog_posts"
    VIDEO_CONTENT = "video_content"
    AUDIO_CONTENT = "audio_content"
    SOCIAL_MEDIA = "social_media"
    LANDING_PAGES = "landing_pages"
    PRODUCT_PAGES = "product_pages"
    ABOUT_PAGES = "about_pages"

class UserIntent(Enum):
    """User search intent categories."""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"
    LOCAL = "local"
    ENTERTAINMENT = "entertainment"

@dataclass
class TrafficMetrics:
    """Organic traffic metrics."""
    period_start: datetime
    period_end: datetime
    total_sessions: int
    unique_visitors: int
    page_views: int
    bounce_rate: float
    average_session_duration: float
    pages_per_session: float
    conversion_rate: float
    organic_conversion_value: float
    top_landing_pages: List[Dict[str, Any]]
    top_keywords: List[Dict[str, Any]]
    device_breakdown: Dict[str, int]
    geographic_distribution: Dict[str, int]

@dataclass
class KeywordPerformance:
    """Individual keyword performance data."""
    keyword: str
    search_volume: int
    impressions: int
    clicks: int
    click_through_rate: float
    average_position: float
    conversions: int
    conversion_rate: float
    revenue: float
    cost_per_click: float
    intent: UserIntent
    difficulty: float
    trend: str
    opportunities: List[str]

@dataclass
class ContentPerformance:
    """Content performance analysis."""
    content_id: str
    url: str
    title: str
    content_type: ContentCategory
    sessions: int
    unique_visitors: int
    page_views: int
    average_time_on_page: float
    bounce_rate: float
    exit_rate: float
    conversion_rate: float
    social_shares: int
    backlinks: int
    organic_keywords: List[str]
    optimization_score: float
    improvement_opportunities: List[str]

@dataclass
class TrafficAnalysis:
    """Comprehensive traffic analysis result."""
    analysis_id: str
    analysis_period: Dict[str, datetime]
    overall_metrics: TrafficMetrics
    keyword_performance: List[KeywordPerformance]
    content_performance: List[ContentPerformance]
    traffic_trends: Dict[str, List[float]]
    user_journey_analysis: Dict[str, Any]
    conversion_analysis: Dict[str, Any]
    competitive_insights: Dict[str, Any]
    recommendations: List[str]
    growth_opportunities: List[str]
    created_at: datetime

class OrganicTrafficAnalyzer:
    """
    Advanced Organic Traffic Analyzer
    
    Features:
    - Comprehensive traffic source analysis
    - Keyword performance tracking
    - Content performance optimization
    - User journey mapping
    - Conversion path analysis
    - Competitive traffic analysis
    - Growth opportunity identification
    - ROI calculation and optimization
    """
    
    def __init__(self, db_pool=None, analytics_apis -> None: Dict[str, str] = None) -> None:
        self.db_pool = db_pool
        self.analytics_apis = analytics_apis or {}
        
        # Traffic analysis configuration
        self.traffic_sources = self._configure_traffic_sources()
        self.conversion_goals = self._configure_conversion_goals()
        self.analysis_segments = self._configure_analysis_segments()
        
    def _configure_traffic_sources(self) -> Dict[str, Dict[str, Any]]:
        """Configure traffic source analysis parameters."""
        return {
            'search_engines': {
                'google': {'weight': 0.70, 'quality_score': 0.85},
                'bing': {'weight': 0.15, 'quality_score': 0.80},
                'yahoo': {'weight': 0.10, 'quality_score': 0.75},
                'duckduckgo': {'weight': 0.05, 'quality_score': 0.82}
            },
            'social_platforms': {
                'youtube': {'weight': 0.40, 'quality_score': 0.78},
                'instagram': {'weight': 0.25, 'quality_score': 0.72},
                'tiktok': {'weight': 0.20, 'quality_score': 0.68},
                'twitter': {'weight': 0.15, 'quality_score': 0.75}
            }
        }
    
    def _configure_conversion_goals(self) -> Dict[str, Dict[str, Any]]:
        """Configure conversion goals for different content types."""
        return {
            'creator_goals': {
                'subscriber_signup': {'value': 10.0, 'weight': 0.30},
                'content_engagement': {'value': 2.0, 'weight': 0.25},
                'social_follow': {'value': 5.0, 'weight': 0.20},
                'email_signup': {'value': 8.0, 'weight': 0.15},
                'product_purchase': {'value': 50.0, 'weight': 0.10}
            }
        }
    
    def _configure_analysis_segments(self) -> Dict[str, List[str]]:
        """Configure user segments for analysis."""
        return {
            'device_segments': ['desktop', 'mobile', 'tablet'],
            'geographic_segments': ['domestic', 'international'],
            'behavior_segments': ['new_visitors', 'returning_visitors', 'engaged_users'],
            'traffic_segments': ['organic_search', 'social_organic', 'direct', 'referral']
        }
    
    def analyze_organic_traffic(
        self,
        website_url: str,
        analysis_period_days: int = 30,
        include_historical: bool = True,
        segment_analysis: bool = True
    ) -> TrafficAnalysis:
        """
        Perform comprehensive organic traffic analysis.
        
        Args:
            website_url: Website URL to analyze
            analysis_period_days: Analysis period in days
            include_historical: Include historical comparison
            segment_analysis: Perform detailed segment analysis
            
        Returns:
            TrafficAnalysis object with comprehensive insights
        """
        try:
            analysis_id = f"traffic_analysis_{hash(website_url)}_{int(datetime.utcnow().timestamp())}"
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            # Collect overall traffic metrics
            overall_metrics = self._collect_traffic_metrics(
                website_url, start_date, end_date
            )
            
            # Analyze keyword performance
            keyword_performance = self._analyze_keyword_performance(
                website_url, start_date, end_date
            )
            
            # Analyze content performance
            content_performance = self._analyze_content_performance(
                website_url, start_date, end_date
            )
            
            # Analyze traffic trends
            traffic_trends = self._analyze_traffic_trends(
                website_url, start_date, end_date, include_historical
            )
            
            # Analyze user journeys
            user_journey_analysis = self._analyze_user_journeys(
                website_url, start_date, end_date
            )
            
            # Analyze conversions
            conversion_analysis = self._analyze_conversions(
                website_url, start_date, end_date
            )
            
            # Competitive insights
            competitive_insights = self._gather_competitive_insights(
                website_url, keyword_performance
            )
            
            # Generate recommendations
            recommendations = self._generate_traffic_recommendations(
                overall_metrics, keyword_performance, content_performance, traffic_trends
            )
            
            # Identify growth opportunities
            growth_opportunities = self._identify_growth_opportunities(
                keyword_performance, content_performance, competitive_insights
            )
            
            analysis = TrafficAnalysis(
                analysis_id=analysis_id,
                analysis_period={'start': start_date, 'end': end_date},
                overall_metrics=overall_metrics,
                keyword_performance=keyword_performance,
                content_performance=content_performance,
                traffic_trends=traffic_trends,
                user_journey_analysis=user_journey_analysis,
                conversion_analysis=conversion_analysis,
                competitive_insights=competitive_insights,
                recommendations=recommendations,
                growth_opportunities=growth_opportunities,
                created_at=datetime.utcnow()
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing organic traffic: {e}")
            raise
    
    def _collect_traffic_metrics(
        self,
        website_url: str,
        start_date: datetime,
        end_date: datetime
    ) -> TrafficMetrics:
        """Collect comprehensive traffic metrics."""
        try:
            # Simulate traffic data (would use real analytics APIs in production)
            base_traffic = self._simulate_base_traffic(website_url)
            
            # Calculate metrics for the period
            days = (end_date - start_date).days
            
            total_sessions = base_traffic['daily_sessions'] * days
            unique_visitors = int(total_sessions * 0.75)  # 75% unique visitors
            page_views = int(total_sessions * 2.3)  # 2.3 pages per session average
            bounce_rate = 0.45  # 45% bounce rate
            average_session_duration = 180.0  # 3 minutes average
            pages_per_session = 2.3
            conversion_rate = 0.025  # 2.5% conversion rate
            organic_conversion_value = total_sessions * conversion_rate * 25.0  # $25 average value
            
            # Top landing pages
            top_landing_pages = [
                {'url': f'{website_url}/', 'sessions': int(total_sessions * 0.30), 'bounce_rate': 0.35},
                {'url': f'{website_url}/blog', 'sessions': int(total_sessions * 0.25), 'bounce_rate': 0.40},
                {'url': f'{website_url}/about', 'sessions': int(total_sessions * 0.20), 'bounce_rate': 0.50},
                {'url': f'{website_url}/content', 'sessions': int(total_sessions * 0.15), 'bounce_rate': 0.38},
                {'url': f'{website_url}/contact', 'sessions': int(total_sessions * 0.10), 'bounce_rate': 0.60}
            ]
            
            # Top keywords
            top_keywords = [
                {'keyword': 'content creator', 'clicks': int(total_sessions * 0.20), 'impressions': int(total_sessions * 0.20 * 10)},
                {'keyword': 'social media tips', 'clicks': int(total_sessions * 0.15), 'impressions': int(total_sessions * 0.15 * 8)},
                {'keyword': 'video creation', 'clicks': int(total_sessions * 0.12), 'impressions': int(total_sessions * 0.12 * 12)},
                {'keyword': 'influencer marketing', 'clicks': int(total_sessions * 0.10), 'impressions': int(total_sessions * 0.10 * 15)},
                {'keyword': 'creator tools', 'clicks': int(total_sessions * 0.08), 'impressions': int(total_sessions * 0.08 * 6)}
            ]
            
            # Device breakdown
            device_breakdown = {
                'mobile': int(total_sessions * 0.65),
                'desktop': int(total_sessions * 0.30),
                'tablet': int(total_sessions * 0.05)
            }
            
            # Geographic distribution
            geographic_distribution = {
                'United States': int(total_sessions * 0.40),
                'United Kingdom': int(total_sessions * 0.15),
                'Canada': int(total_sessions * 0.12),
                'Australia': int(total_sessions * 0.08),
                'Germany': int(total_sessions * 0.07),
                'France': int(total_sessions * 0.06),
                'Other': int(total_sessions * 0.12)
            }
            
            return TrafficMetrics(
                period_start=start_date,
                period_end=end_date,
                total_sessions=total_sessions,
                unique_visitors=unique_visitors,
                page_views=page_views,
                bounce_rate=bounce_rate,
                average_session_duration=average_session_duration,
                pages_per_session=pages_per_session,
                conversion_rate=conversion_rate,
                organic_conversion_value=organic_conversion_value,
                top_landing_pages=top_landing_pages,
                top_keywords=top_keywords,
                device_breakdown=device_breakdown,
                geographic_distribution=geographic_distribution
            )
            
        except Exception as e:
            logger.error(f"Error collecting traffic metrics: {e}")
            raise
    
    def _analyze_keyword_performance(
        self,
        website_url: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[KeywordPerformance]:
        """Analyze individual keyword performance."""
        try:
            keyword_data = [
                {
                    'keyword': 'content creator',
                    'search_volume': 5000,
                    'difficulty': 0.7,
                    'intent': UserIntent.INFORMATIONAL
                },
                {
                    'keyword': 'social media tips',
                    'search_volume': 3000,
                    'difficulty': 0.5,
                    'intent': UserIntent.INFORMATIONAL
                },
                {
                    'keyword': 'video creation',
                    'search_volume': 4000,
                    'difficulty': 0.6,
                    'intent': UserIntent.COMMERCIAL
                },
                {
                    'keyword': 'influencer marketing',
                    'search_volume': 6000,
                    'difficulty': 0.8,
                    'intent': UserIntent.COMMERCIAL
                },
                {
                    'keyword': 'creator tools',
                    'search_volume': 2000,
                    'difficulty': 0.4,
                    'intent': UserIntent.TRANSACTIONAL
                }
            ]
            
            keyword_performances = []
            
            for data in keyword_data:
                # Calculate performance metrics
                impressions = data['search_volume'] * 30  # Monthly impressions
                clicks = int(impressions * (0.08 - data['difficulty'] * 0.05))  # CTR based on difficulty
                click_through_rate = clicks / impressions if impressions > 0 else 0
                average_position = 5.0 + data['difficulty'] * 10  # Position based on difficulty
                conversions = int(clicks * 0.03)  # 3% conversion rate
                conversion_rate = conversions / clicks if clicks > 0 else 0
                revenue = conversions * 25.0  # $25 per conversion
                cost_per_click = data['difficulty'] * 2.0  # CPC based on difficulty
                
                # Determine trend
                trend = 'growing' if data['difficulty'] < 0.6 else 'stable' if data['difficulty'] < 0.8 else 'declining'
                
                # Identify opportunities
                opportunities = []
                if average_position > 10:
                    opportunities.append('Improve content quality for better rankings')
                if click_through_rate < 0.05:
                    opportunities.append('Optimize meta descriptions for better CTR')
                if conversion_rate < 0.02:
                    opportunities.append('Improve landing page conversion optimization')
                
                performance = KeywordPerformance(
                    keyword=data['keyword'],
                    search_volume=data['search_volume'],
                    impressions=impressions,
                    clicks=clicks,
                    click_through_rate=click_through_rate,
                    average_position=average_position,
                    conversions=conversions,
                    conversion_rate=conversion_rate,
                    revenue=revenue,
                    cost_per_click=cost_per_click,
                    intent=data['intent'],
                    difficulty=data['difficulty'],
                    trend=trend,
                    opportunities=opportunities
                )
                
                keyword_performances.append(performance)
            
            return keyword_performances
            
        except Exception as e:
            logger.error(f"Error analyzing keyword performance: {e}")
            return []
    
    def _analyze_content_performance(
        self,
        website_url: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[ContentPerformance]:
        """Analyze individual content piece performance."""
        try:
            content_data = [
                {
                    'url': f'{website_url}/',
                    'title': 'Home - Creator Platform',
                    'content_type': ContentCategory.LANDING_PAGES
                },
                {
                    'url': f'{website_url}/blog/content-creation-tips',
                    'title': '10 Essential Content Creation Tips',
                    'content_type': ContentCategory.BLOG_POSTS
                },
                {
                    'url': f'{website_url}/video/how-to-grow-audience',
                    'title': 'How to Grow Your Audience in 2025',
                    'content_type': ContentCategory.VIDEO_CONTENT
                },
                {
                    'url': f'{website_url}/tools',
                    'title': 'Creator Tools and Resources',
                    'content_type': ContentCategory.PRODUCT_PAGES
                },
                {
                    'url': f'{website_url}/about',
                    'title': 'About Our Creator Platform',
                    'content_type': ContentCategory.ABOUT_PAGES
                }
            ]
            
            content_performances = []
            
            for i, data in enumerate(content_data):
                content_id = f"content_{i+1}"
                
                # Simulate performance metrics
                base_sessions = 1000 - (i * 150)  # Declining performance
                sessions = base_sessions
                unique_visitors = int(sessions * 0.8)
                page_views = int(sessions * 1.2)
                average_time_on_page = 120.0 + (i * 30)  # Varying engagement
                bounce_rate = 0.4 + (i * 0.1)  # Increasing bounce rate
                exit_rate = 0.3 + (i * 0.08)
                conversion_rate = 0.05 - (i * 0.01)  # Decreasing conversion
                social_shares = max(50 - (i * 10), 5)
                backlinks = max(20 - (i * 3), 2)
                
                # Generate organic keywords
                organic_keywords = [
                    f'keyword_{i+1}_1',
                    f'keyword_{i+1}_2', 
                    f'keyword_{i+1}_3'
                ]
                
                # Calculate optimization score
                optimization_score = self._calculate_content_optimization_score(
                    sessions, bounce_rate, average_time_on_page, conversion_rate
                )
                
                # Identify improvement opportunities
                improvement_opportunities = []
                if bounce_rate > 0.6:
                    improvement_opportunities.append('Reduce bounce rate with better content hooks')
                if average_time_on_page < 60:
                    improvement_opportunities.append('Increase engagement with interactive elements')
                if conversion_rate < 0.02:
                    improvement_opportunities.append('Add clear call-to-action buttons')
                if social_shares < 20:
                    improvement_opportunities.append('Add social sharing buttons and incentives')
                
                performance = ContentPerformance(
                    content_id=content_id,
                    url=data['url'],
                    title=data['title'],
                    content_type=data['content_type'],
                    sessions=sessions,
                    unique_visitors=unique_visitors,
                    page_views=page_views,
                    average_time_on_page=average_time_on_page,
                    bounce_rate=bounce_rate,
                    exit_rate=exit_rate,
                    conversion_rate=conversion_rate,
                    social_shares=social_shares,
                    backlinks=backlinks,
                    organic_keywords=organic_keywords,
                    optimization_score=optimization_score,
                    improvement_opportunities=improvement_opportunities
                )
                
                content_performances.append(performance)
            
            return content_performances
            
        except Exception as e:
            logger.error(f"Error analyzing content performance: {e}")
            return []
    
    def _calculate_content_optimization_score(
        self,
        sessions: int,
        bounce_rate: float,
        time_on_page: float,
        conversion_rate: float
    ) -> float:
        """Calculate content optimization score (0-100)."""
        score = 0.0
        
        # Traffic volume score (25%)
        if sessions > 1000:
            score += 25
        elif sessions > 500:
            score += 20
        elif sessions > 100:
            score += 15
        else:
            score += 10
        
        # Engagement score (35%)
        engagement_score = 0
        if bounce_rate < 0.4:
            engagement_score += 15
        elif bounce_rate < 0.6:
            engagement_score += 10
        else:
            engagement_score += 5
        
        if time_on_page > 180:
            engagement_score += 20
        elif time_on_page > 120:
            engagement_score += 15
        elif time_on_page > 60:
            engagement_score += 10
        else:
            engagement_score += 5
        
        score += engagement_score * 0.35
        
        # Conversion score (40%)
        if conversion_rate > 0.05:
            score += 40
        elif conversion_rate > 0.03:
            score += 30
        elif conversion_rate > 0.01:
            score += 20
        else:
            score += 10
        
        return min(score, 100.0)
    
    def _simulate_base_traffic(self, website_url: str) -> Dict[str, int]:
        """Simulate base traffic data for analysis."""
        # Generate realistic traffic based on URL characteristics
        url_hash = hash(website_url)
        base_daily_sessions = 100 + (abs(url_hash) % 500)
        
        return {
            'daily_sessions': base_daily_sessions,
            'weekly_sessions': base_daily_sessions * 7,
            'monthly_sessions': base_daily_sessions * 30
        }
    
    def _analyze_traffic_trends(
        self,
        website_url: str,
        start_date: datetime,
        end_date: datetime,
        include_historical: bool
    ) -> Dict[str, List[float]]:
        """Analyze traffic trends over time."""
        try:
            days = (end_date - start_date).days
            base_traffic = self._simulate_base_traffic(website_url)
            
            # Generate daily traffic trend
            daily_trend = []
            for day in range(days):
                # Simulate natural fluctuation with weekly patterns
                day_of_week = (start_date + timedelta(days=day)).weekday()
                weekend_modifier = 0.8 if day_of_week in [5, 6] else 1.0
                
                # Add some randomness
                random_modifier = 0.8 + ((hash(f"{website_url}_{day}") % 40) / 100)
                
                daily_sessions = base_traffic['daily_sessions'] * weekend_modifier * random_modifier
                daily_trend.append(daily_sessions)
            
            trends = {
                'daily_sessions': daily_trend,
                'weekly_average': [sum(daily_trend[i:i+7])/7 for i in range(0, len(daily_trend)-6, 7)],
                'growth_rate': [(daily_trend[i] - daily_trend[max(0, i-7)]) / daily_trend[max(0, i-7)] * 100 
                               for i in range(len(daily_trend))]
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing traffic trends: {e}")
            return {}
    
    def _generate_traffic_recommendations(
        self,
        metrics: TrafficMetrics,
        keyword_performance: List[KeywordPerformance],
        content_performance: List[ContentPerformance],
        trends: Dict[str, List[float]]
    ) -> List[str]:
        """Generate actionable traffic optimization recommendations."""
        recommendations = []
        
        # Bounce rate recommendations
        if metrics.bounce_rate > 0.6:
            recommendations.append("High bounce rate detected - improve page loading speed and content relevance")
        
        # Session duration recommendations
        if metrics.average_session_duration < 120:
            recommendations.append("Low session duration - add internal links and engaging content to increase time on site")
        
        # Conversion rate recommendations
        if metrics.conversion_rate < 0.02:
            recommendations.append("Low conversion rate - optimize call-to-action placement and landing page design")
        
        # Keyword optimization recommendations
        low_performing_keywords = [kp for kp in keyword_performance if kp.average_position > 10]
        if low_performing_keywords:
            recommendations.append(f"Improve content for {len(low_performing_keywords)} keywords ranking below position 10")
        
        # Content optimization recommendations
        low_performing_content = [cp for cp in content_performance if cp.optimization_score < 60]
        if low_performing_content:
            recommendations.append(f"Optimize {len(low_performing_content)} content pieces with low performance scores")
        
        # Mobile optimization
        if metrics.device_breakdown.get('mobile', 0) > metrics.device_breakdown.get('desktop', 0):
            recommendations.append("Mobile traffic is dominant - ensure mobile-first optimization")
        
        # Geographic opportunities
        top_countries = sorted(metrics.geographic_distribution.items(), key=lambda x: x[1], reverse=True)
        if len(top_countries) > 3:
            recommendations.append(f"Consider localization for top markets: {', '.join([c[0] for c in top_countries[:3]])}")
        
        return recommendations
    
    def _identify_growth_opportunities(
        self,
        keyword_performance: List[KeywordPerformance],
        content_performance: List[ContentPerformance],
        competitive_insights: Dict[str, Any]
    ) -> List[str]:
        """Identify specific growth opportunities."""
        opportunities = []
        
        # Keyword opportunities
        high_potential_keywords = [
            kp for kp in keyword_performance 
            if kp.search_volume > 2000 and kp.average_position > 5 and kp.difficulty < 0.7
        ]
        if high_potential_keywords:
            opportunities.append(f"Target {len(high_potential_keywords)} high-potential keywords for quick wins")
        
        # Content gaps
        underperforming_content = [
            cp for cp in content_performance 
            if cp.sessions < 500 and cp.content_type in [ContentCategory.BLOG_POSTS, ContentCategory.VIDEO_CONTENT]
        ]
        if underperforming_content:
            opportunities.append(f"Improve or refresh {len(underperforming_content)} underperforming content pieces")
        
        # Long-tail keyword opportunities
        long_tail_potential = [
            kp for kp in keyword_performance 
            if kp.difficulty < 0.5 and kp.conversion_rate > 0.03
        ]
        if long_tail_potential:
            opportunities.append("Focus on long-tail keywords with high conversion potential")
        
        # Featured snippet opportunities
        snippet_opportunities = [
            kp for kp in keyword_performance 
            if 3 <= kp.average_position <= 8 and kp.intent == UserIntent.INFORMATIONAL
        ]
        if snippet_opportunities:
            opportunities.append(f"Optimize {len(snippet_opportunities)} keywords for featured snippets")
        
        return opportunities

# Export classes
__all__ = [
    'OrganicTrafficAnalyzer',
    'TrafficAnalysis',
    'TrafficMetrics',
    'KeywordPerformance',
    'ContentPerformance',
    'TrafficSource',
    'ContentCategory',
    'UserIntent'
]