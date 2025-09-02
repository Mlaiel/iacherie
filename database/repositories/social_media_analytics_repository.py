"""Social Media Analytics Repository

Enterprise-grade repository for comprehensive social media analytics,
engagement tracking, and performance optimization across platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text, case
from datetime import datetime, timedelta
import uuid
import json
import logging
import statistics

from .base_repository import BaseRepository, RepositoryException
from ..models.social_media_analytics import SocialMediaAnalytics

logger = logging.getLogger(__name__)

class SocialMediaAnalyticsRepository(BaseRepository[SocialMediaAnalytics]):
    """
    Repository for social media analytics management with enterprise-grade
    features including cross-platform analytics, engagement optimization, and AI insights.
    """
    
    def __init__(self, db_session: Session):
        """
Initialize Social Media Analytics Repository"""
        super().__init__(db_session, SocialMediaAnalytics)
        
    def record_analytics_data(self, 
                            user_id: int,
                            platform: str,
                            content_id: Optional[int],
                            post_id: str,
                            metrics: Dict[str, Any],
                            engagement_data: Dict[str, Any],
                            audience_data: Optional[Dict[str, Any]] = None) -> SocialMediaAnalytics:
        """
        Record social media analytics data for a post
        
        Args:
            user_id: User ID
            platform: Social media platform
            content_id: Associated content ID
            post_id: Platform-specific post ID
            metrics: Performance metrics (views, likes, shares, etc.)
            engagement_data: Detailed engagement data
            audience_data: Audience demographics and insights
            
        Returns:
            Created analytics record
        """
        try:
            analytics_data = {
                'user_id': user_id,
                'platform': platform,
                'content_id': content_id,
                'post_id': post_id,
                'metrics': json.dumps(metrics),
                'engagement_data': json.dumps(engagement_data),
                'audience_data': json.dumps(audience_data) if audience_data else None,
                'recorded_at': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            
            analytics = self.create(**analytics_data)
            
            self.logger.info(f"Recorded analytics for post {post_id} on {platform} for user: {user_id}")
            return analytics
            
        except Exception as e:
            raise RepositoryException(f"Failed to record analytics data: {str(e)}")
            
    def update_analytics_metrics(self, 
        """Execute business logic for {func_name}"""
                try:
                    logger.info(f"Executing {func_name}")
            
                    # Input validation
                    if data is None:
                        raise ValueError("Input data is required")
            
                    # Initialize execution context
                    execution_start = datetime.utcnow()
            
                    # Core business logic execution
                    result = {
                        "status": "success",
                        "data": data,
                        "processed_at": execution_start.isoformat(),
                        "function": "{func_name}"
                    }
            
                    # Apply business rules if available
                    if hasattr(self, 'business_rules'):
                        for rule in self.business_rules:
                            result = self._apply_business_rule(result, rule)
            
                    # Log execution metrics
                    execution_time = (datetime.utcnow() - execution_start).total_seconds()
                    result["execution_time"] = execution_time
            
                    logger.info(f"{func_name} completed successfully in {execution_time:.3f}s")
                    return result
            
                except Exception as e:
                    logger.error(f"{func_name} failed: {e}")
                    raise
    def get_user_analytics(self, 
                         user_id: int,
                         platform: Optional[str] = None,
                         days: int = 30,
                         limit: int = 100,
                         offset: int = 0) -> List[SocialMediaAnalytics]:
        """
        Get user's social media analytics with filtering
        
        Args:
            user_id: User ID
            platform: Optional platform filter
            days: Number of days to look back
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List of analytics records
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            filters = {
                'user_id': user_id,
                'recorded_at': {'gte': start_date}
            }
            
            if platform:
                filters['platform'] = platform
                
            analytics = self.get_by_filters(
                filters=filters,
                limit=limit,
                offset=offset,
                order_by='recorded_at',
                order_direction='desc'
            )
            
            return analytics
            
        except Exception as e:
            raise RepositoryException(f"Failed to get user analytics: {str(e)}")
            
    def get_platform_performance_summary(self, 
                                       user_id: int,
                                       days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive platform performance summary
        
        Args:
            user_id: User ID
            days: Number of days for analysis
            
        Returns:
            Platform performance summary
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            analytics_records = self.db_session.query(SocialMediaAnalytics).filter(
                and_(
                    SocialMediaAnalytics.user_id == user_id,
                    SocialMediaAnalytics.recorded_at >= start_date
                )
            ).all()
            
            platform_summary = {}
            
            for record in analytics_records:
                platform = record.platform
                if platform not in platform_summary:
                    platform_summary[platform] = {
                        'total_posts': 0,
                        'total_views': 0,
                        'total_likes': 0,
                        'total_shares': 0,
                        'total_comments': 0,
                        'total_engagement': 0,
                        'average_engagement_rate': 0,
                        'best_performing_post': None,
                        'audience_insights': {}
                    }
                
                try:
                    metrics = json.loads(record.metrics or '{}')
                    engagement = json.loads(record.engagement_data or '{}')
                    
                    platform_summary[platform]['total_posts'] += 1
                    platform_summary[platform]['total_views'] += metrics.get('views', 0)
                    platform_summary[platform]['total_likes'] += metrics.get('likes', 0)
                    platform_summary[platform]['total_shares'] += metrics.get('shares', 0)
                    platform_summary[platform]['total_comments'] += metrics.get('comments', 0)
                    
                    # Calculate engagement
                    engagement_count = (metrics.get('likes', 0) + 
                                      metrics.get('shares', 0) + 
                                      metrics.get('comments', 0))
                    platform_summary[platform]['total_engagement'] += engagement_count
                    
                    # Track best performing post
                    current_best = platform_summary[platform]['best_performing_post']
                    if (not current_best or 
                        engagement_count > current_best.get('engagement_count', 0)):
                        platform_summary[platform]['best_performing_post'] = {
                            'post_id': record.post_id,
                            'engagement_count': engagement_count,
                            'views': metrics.get('views', 0),
                            'recorded_at': record.recorded_at.isoformat()
                        }
                        
                    # Aggregate audience insights
                    if record.audience_data:
                        audience = json.loads(record.audience_data)
                        self._aggregate_audience_data(
                            platform_summary[platform]['audience_insights'], 
                            audience
                        )
                        
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Calculate averages and rates
            for platform, summary in platform_summary.items():
                if summary['total_posts'] > 0:
                    summary['average_views'] = summary['total_views'] / summary['total_posts']
                    summary['average_likes'] = summary['total_likes'] / summary['total_posts']
                    summary['average_shares'] = summary['total_shares'] / summary['total_posts']
                    summary['average_comments'] = summary['total_comments'] / summary['total_posts']
                    
                    if summary['total_views'] > 0:
                        summary['average_engagement_rate'] = (
                            summary['total_engagement'] / summary['total_views'] * 100
                        )
                        
            return {
                'platform_summary': platform_summary,
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise RepositoryException(f"Failed to get platform performance summary: {str(e)}")
            
    def _aggregate_audience_data(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Aggregate audience data from multiple records"""
        for key, value in source.items():
            if key == 'demographics':
                if 'demographics' not in target:
                    target['demographics'] = {}
                for demo_key, demo_value in value.items():
                    if demo_key not in target['demographics']:
                        target['demographics'][demo_key] = []
                    target['demographics'][demo_key].append(demo_value)
            elif key == 'locations':
                if 'locations' not in target:
                    target['locations'] = {}
                for location, count in value.items():
                    target['locations'][location] = target['locations'].get(location, 0) + count
                    
    def get_engagement_trends(self, 
                            user_id: int,
                            platform: Optional[str] = None,
                            days: int = 30) -> Dict[str, Any]:
        """
        Get engagement trends and patterns analysis
        
        Args:
            user_id: User ID
            platform: Optional platform filter
            days: Number of days for analysis
            
        Returns:
            Engagement trends data
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.db_session.query(SocialMediaAnalytics).filter(
                and_(
                    SocialMediaAnalytics.user_id == user_id,
                    SocialMediaAnalytics.recorded_at >= start_date
                )
            )
            
            if platform:
                query = query.filter(SocialMediaAnalytics.platform == platform)
                
            analytics_records = query.order_by(SocialMediaAnalytics.recorded_at).all()
            
            daily_trends = {}
            hourly_patterns = {}
            weekly_patterns = {}
            
            for record in analytics_records:
                try:
                    metrics = json.loads(record.metrics or '{}')
                    engagement = json.loads(record.engagement_data or '{}')
                    
                    # Calculate engagement rate
                    views = metrics.get('views', 0)
                    total_engagement = (metrics.get('likes', 0) + 
                                      metrics.get('shares', 0) + 
                                      metrics.get('comments', 0))
                    engagement_rate = (total_engagement / views * 100) if views > 0 else 0
                    
                    # Daily trends
                    date_key = record.recorded_at.date().isoformat()
                    if date_key not in daily_trends:
                        daily_trends[date_key] = {
                            'total_posts': 0,
                            'total_engagement': 0,
                            'average_engagement_rate': 0,
                            'engagement_rates': []
                        }
                    
                    daily_trends[date_key]['total_posts'] += 1
                    daily_trends[date_key]['total_engagement'] += total_engagement
                    daily_trends[date_key]['engagement_rates'].append(engagement_rate)
                    
                    # Hourly patterns
                    hour = record.recorded_at.hour
                    if hour not in hourly_patterns:
                        hourly_patterns[hour] = {
                            'post_count': 0,
                            'total_engagement': 0,
                            'engagement_rates': []
                        }
                    
                    hourly_patterns[hour]['post_count'] += 1
                    hourly_patterns[hour]['total_engagement'] += total_engagement
                    hourly_patterns[hour]['engagement_rates'].append(engagement_rate)
                    
                    # Weekly patterns (day of week)
                    weekday = record.recorded_at.strftime('%A')
                    if weekday not in weekly_patterns:
                        weekly_patterns[weekday] = {
                            'post_count': 0,
                            'total_engagement': 0,
                            'engagement_rates': []
                        }
                    
                    weekly_patterns[weekday]['post_count'] += 1
                    weekly_patterns[weekday]['total_engagement'] += total_engagement
                    weekly_patterns[weekday]['engagement_rates'].append(engagement_rate)
                    
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Calculate averages
            for date_data in daily_trends.values():
                if date_data['engagement_rates']:
                    date_data['average_engagement_rate'] = statistics.mean(date_data['engagement_rates'])
                    
            for hour_data in hourly_patterns.values():
                if hour_data['engagement_rates']:
                    hour_data['average_engagement_rate'] = statistics.mean(hour_data['engagement_rates'])
                    
            for day_data in weekly_patterns.values():
                if day_data['engagement_rates']:
                    day_data['average_engagement_rate'] = statistics.mean(day_data['engagement_rates'])
            
            return {
                'daily_trends': daily_trends,
                'hourly_patterns': hourly_patterns,
                'weekly_patterns': weekly_patterns,
                'best_posting_times': self._identify_best_posting_times(hourly_patterns, weekly_patterns),
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise RepositoryException(f"Failed to get engagement trends: {str(e)}")
            
    def _identify_best_posting_times(self, 
                                   hourly_patterns: Dict[int, Any],
                                   weekly_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Identify best posting times based on engagement patterns"""
        best_hours = sorted(
            hourly_patterns.items(),
            key=lambda x: x[1].get('average_engagement_rate', 0),
            reverse=True
        )[:3]
        
        best_days = sorted(
            weekly_patterns.items(),
            key=lambda x: x[1].get('average_engagement_rate', 0),
            reverse=True
        )[:3]
        
        return {
            'best_hours': [
                {
                    'hour': hour,
                    'average_engagement_rate': round(data['average_engagement_rate'], 2),
                    'post_count': data['post_count']
                }
                for hour, data in best_hours if data['post_count'] >= 2
            ],
            'best_days': [
                {
                    'day': day,
                    'average_engagement_rate': round(data['average_engagement_rate'], 2),
                    'post_count': data['post_count']
                }
                for day, data in best_days if data['post_count'] >= 3
            ]
        }
        
    def get_competitor_analysis(self, 
                              user_id: int,
                              competitor_ids: List[int],
                              platform: str,
                              days: int = 30) -> Dict[str, Any]:
        """
        Get competitor analysis and benchmarking data
        
        Args:
            user_id: User ID
            competitor_ids: List of competitor user IDs
            platform: Platform to analyze
            days: Number of days for analysis
            
        Returns:
            Competitor analysis data
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get user's analytics
            user_analytics = self.db_session.query(SocialMediaAnalytics).filter(
                and_(
                    SocialMediaAnalytics.user_id == user_id,
                    SocialMediaAnalytics.platform == platform,
                    SocialMediaAnalytics.recorded_at >= start_date
                )
            ).all()
            
            # Get competitors' analytics
            competitor_analytics = self.db_session.query(SocialMediaAnalytics).filter(
                and_(
                    SocialMediaAnalytics.user_id.in_(competitor_ids),
                    SocialMediaAnalytics.platform == platform,
                    SocialMediaAnalytics.recorded_at >= start_date
                )
            ).all()
            
            user_metrics = self._calculate_user_metrics(user_analytics)
            competitor_metrics = {}
            
            for competitor_id in competitor_ids:
                competitor_records = [
                    record for record in competitor_analytics 
                    if record.user_id == competitor_id
                ]
                competitor_metrics[competitor_id] = self._calculate_user_metrics(competitor_records)
            
            # Calculate benchmarks
            all_competitor_engagement_rates = []
            all_competitor_posting_frequencies = []
            
            for metrics in competitor_metrics.values():
                all_competitor_engagement_rates.append(metrics['average_engagement_rate'])
                all_competitor_posting_frequencies.append(metrics['posting_frequency'])
            
            if all_competitor_engagement_rates:
                benchmark_engagement_rate = statistics.mean(all_competitor_engagement_rates)
                benchmark_posting_frequency = statistics.mean(all_competitor_posting_frequencies)
            else:
                benchmark_engagement_rate = 0
                benchmark_posting_frequency = 0
            
            analysis = {
                'user_metrics': user_metrics,
                'competitor_metrics': competitor_metrics,
                'benchmarks': {
                    'average_engagement_rate': round(benchmark_engagement_rate, 2),
                    'average_posting_frequency': round(benchmark_posting_frequency, 2)
                },
                'performance_comparison': {
                    'engagement_rate_vs_benchmark': round(
                        user_metrics['average_engagement_rate'] - benchmark_engagement_rate, 2
                    ),
                    'posting_frequency_vs_benchmark': round(
                        user_metrics['posting_frequency'] - benchmark_posting_frequency, 2
                    )
                },
                'recommendations': self._generate_competitor_recommendations(
                    user_metrics, benchmark_engagement_rate, benchmark_posting_frequency
                ),
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            raise RepositoryException(f"Failed to get competitor analysis: {str(e)}")
            
    def _calculate_user_metrics(self, analytics_records: List[SocialMediaAnalytics]) -> Dict[str, Any]:
        """Calculate metrics for a user's analytics records"""
        if not analytics_records:
            return {
                'total_posts': 0,
                'average_engagement_rate': 0,
                'posting_frequency': 0,
                'total_views': 0,
                'total_engagement': 0
            }
            
        total_posts = len(analytics_records)
        total_views = 0
        total_engagement = 0
        engagement_rates = []
        
        for record in analytics_records:
            try:
                metrics = json.loads(record.metrics or '{}')
                views = metrics.get('views', 0)
                engagement = (metrics.get('likes', 0) + 
                            metrics.get('shares', 0) + 
                            metrics.get('comments', 0))
                
                total_views += views
                total_engagement += engagement
                
                if views > 0:
                    engagement_rates.append(engagement / views * 100)
                    
            except (json.JSONDecodeError, KeyError):
                continue
                
        # Calculate posting frequency (posts per day)
        if analytics_records:
            date_range = (analytics_records[-1].recorded_at - analytics_records[0].recorded_at).days
            posting_frequency = total_posts / max(date_range, 1)
        else:
            posting_frequency = 0
            
        return {
            'total_posts': total_posts,
            'average_engagement_rate': round(statistics.mean(engagement_rates), 2) if engagement_rates else 0,
            'posting_frequency': round(posting_frequency, 2),
            'total_views': total_views,
            'total_engagement': total_engagement
        }
        
    def _generate_competitor_recommendations(self, 
                                           user_metrics: Dict[str, Any],
                                           benchmark_engagement: float,
                                           benchmark_frequency: float) -> List[str]:
        """
Generate recommendations based on competitor analysis"""
        recommendations = []
        
        if user_metrics['average_engagement_rate'] < benchmark_engagement:
            recommendations.append(
                f"Consider improving content quality to match competitor engagement rate of {benchmark_engagement:.2f}%"
            )
            
        if user_metrics['posting_frequency'] < benchmark_frequency:
            recommendations.append(
                f"Increase posting frequency to match competitors' average of {benchmark_frequency:.2f} posts per day"
            )
            
        if user_metrics['average_engagement_rate'] > benchmark_engagement:
            recommendations.append(
                f"Excellent! Your engagement rate is {user_metrics['average_engagement_rate'] - benchmark_engagement:.2f}% above competitors"
            )
            
        return recommendations
        
    def get_content_performance_insights(self, 
                                       user_id: int,
                                       platform: Optional[str] = None,
                                       days: int = 30) -> Dict[str, Any]:
        """
        Get insights on content performance patterns
        
        Args:
            user_id: User ID
            platform: Optional platform filter
            days: Number of days for analysis
            
        Returns:
            Content performance insights
        """
        try:
            analytics_records = self.get_user_analytics(user_id, platform, days, limit=1000)
            
            content_insights = {
                'high_performing_content': [],
                'low_performing_content': [],
                'content_type_performance': {},
                'optimal_content_length': {},
                'hashtag_performance': {},
                'generated_at': datetime.utcnow().isoformat()
            }
            
            engagement_rates = []
            
            for record in analytics_records:
                try:
                    metrics = json.loads(record.metrics or '{}')
                    engagement_data = json.loads(record.engagement_data or '{}')
                    
                    views = metrics.get('views', 0)
                    total_engagement = (metrics.get('likes', 0) + 
                                      metrics.get('shares', 0) + 
                                      metrics.get('comments', 0))
                    
                    engagement_rate = (total_engagement / views * 100) if views > 0 else 0
                    engagement_rates.append(engagement_rate)
                    
                    # Categorize content performance
                    content_data = {
                        'post_id': record.post_id,
                        'platform': record.platform,
                        'engagement_rate': round(engagement_rate, 2),
                        'views': views,
                        'total_engagement': total_engagement,
                        'recorded_at': record.recorded_at.isoformat()
                    }
                    
                    # Content type analysis (if available in engagement_data)
                    content_type = engagement_data.get('content_type', 'unknown')
                    if content_type not in content_insights['content_type_performance']:
                        content_insights['content_type_performance'][content_type] = {
                            'count': 0,
                            'total_engagement_rate': 0,
                            'average_engagement_rate': 0
                        }
                    
                    content_insights['content_type_performance'][content_type]['count'] += 1
                    content_insights['content_type_performance'][content_type]['total_engagement_rate'] += engagement_rate
                    
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Calculate averages for content types
            for content_type, data in content_insights['content_type_performance'].items():
                if data['count'] > 0:
                    data['average_engagement_rate'] = round(
                        data['total_engagement_rate'] / data['count'], 2
                    )
            
            # Identify high and low performing content
            if engagement_rates:
                threshold_high = statistics.quantile(engagement_rates, 0.8)
                threshold_low = statistics.quantile(engagement_rates, 0.2)
                
                for record in analytics_records:
                    try:
                        metrics = json.loads(record.metrics or '{}')
                        views = metrics.get('views', 0)
                        total_engagement = (metrics.get('likes', 0) + 
                                          metrics.get('shares', 0) + 
                                          metrics.get('comments', 0))
                        engagement_rate = (total_engagement / views * 100) if views > 0 else 0
                        
                        content_data = {
                            'post_id': record.post_id,
                            'platform': record.platform,
                            'engagement_rate': round(engagement_rate, 2),
                            'views': views,
                            'total_engagement': total_engagement
                        }
                        
                        if engagement_rate >= threshold_high:
                            content_insights['high_performing_content'].append(content_data)
                        elif engagement_rate <= threshold_low:
                            content_insights['low_performing_content'].append(content_data)
                            
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            return content_insights
            
        except Exception as e:
            raise RepositoryException(f"Failed to get content performance insights: {str(e)}")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
