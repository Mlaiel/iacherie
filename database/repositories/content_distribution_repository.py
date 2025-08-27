"""
Content Distribution Repository

Enterprise-grade repository for multi-platform content distribution management
including scheduling, optimization, and performance tracking across platforms.

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

from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from datetime import datetime, timedelta
import uuid
import json
import logging

from .base_repository import BaseRepository, RepositoryException
from ..models.content_distribution import ContentDistribution

logger = logging.getLogger(__name__)

class ContentDistributionRepository(BaseRepository[ContentDistribution]):
    """
    Repository for content distribution management with enterprise-grade
    features including multi-platform scheduling, optimization, and analytics.
    """
    
    def __init__(self, db_session: Session):
        """Initialize Content Distribution Repository"""
        super().__init__(db_session, ContentDistribution)
        
    def create_distribution_plan(self, 
                               user_id: int,
                               content_id: int,
                               platforms: List[str],
                               schedule_data: Dict[str, Any],
                               optimization_settings: Dict[str, Any]) -> ContentDistribution:
        """
        Create new content distribution plan
        
        Args:
            user_id: User creating the distribution
            content_id: Content to distribute
            platforms: Target platforms list
            schedule_data: Distribution scheduling information
            optimization_settings: Platform-specific optimization settings
            
        Returns:
            Created content distribution instance
        """
        try:
            distribution_data = {
                'user_id': user_id,
                'content_id': content_id,
                'platforms': json.dumps(platforms),
                'schedule_data': json.dumps(schedule_data),
                'optimization_settings': json.dumps(optimization_settings),
                'status': 'planned',
                'created_at': datetime.utcnow()
            }
            
            distribution = self.create(**distribution_data)
            
            self.logger.info(f"Created distribution plan ID: {distribution.id} for content: {content_id}")
            return distribution
            
        except Exception as e:
            raise RepositoryException(f"Failed to create distribution plan: {str(e)}")
            
    def update_distribution_status(self, 
                                 distribution_id: int,
                                 status: str,
                                 platform_results: Optional[Dict[str, Any]] = None,
                                 error_details: Optional[str] = None) -> Optional[ContentDistribution]:
        """
        Update content distribution status and results
        
        Args:
            distribution_id: Distribution ID
            status: New status (planned, distributing, completed, failed, partial)
            platform_results: Platform-specific distribution results
            error_details: Error details if failed
            
        Returns:
            Updated distribution instance
        """
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if status == 'distributing':
                update_data['started_at'] = datetime.utcnow()
            elif status in ['completed', 'failed', 'partial']:
                update_data['completed_at'] = datetime.utcnow()
                
            if platform_results:
                update_data['platform_results'] = json.dumps(platform_results)
                
            if error_details:
                update_data['error_details'] = error_details
                
            distribution = self.update(distribution_id, **update_data)
            
            if distribution:
                self.logger.info(f"Updated distribution {distribution_id} status to: {status}")
                
            return distribution
            
        except Exception as e:
            raise RepositoryException(f"Failed to update distribution status: {str(e)}")
            
    def get_scheduled_distributions(self, 
                                  schedule_time: Optional[datetime] = None,
                                  platform: Optional[str] = None,
                                  limit: int = 100) -> List[ContentDistribution]:
        """
        Get scheduled distributions for processing
        
        Args:
            schedule_time: Optional specific schedule time
            platform: Optional platform filter
            limit: Maximum results
            
        Returns:
            List of scheduled distributions
        """
        try:
            current_time = schedule_time or datetime.utcnow()
            
            query = self.db_session.query(ContentDistribution).filter(
                and_(
                    ContentDistribution.status == 'planned',
                    ContentDistribution.scheduled_for <= current_time
                )
            )
            
            if platform:
                # Filter by platform in platforms JSON array
                query = query.filter(
                    ContentDistribution.platforms.contains(f'"{platform}"')
                )
                
            distributions = query.order_by(ContentDistribution.scheduled_for).limit(limit).all()
            
            return distributions
            
        except Exception as e:
            raise RepositoryException(f"Failed to get scheduled distributions: {str(e)}")
            
    def get_user_distributions(self, 
                             user_id: int,
                             status: Optional[str] = None,
                             platform: Optional[str] = None,
                             limit: int = 50,
                             offset: int = 0) -> List[ContentDistribution]:
        """
        Get user's content distributions with filtering
        
        Args:
            user_id: User ID
            status: Filter by status
            platform: Filter by platform
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List of user's content distributions
        """
        try:
            filters = {'user_id': user_id}
            
            if status:
                filters['status'] = status
                
            distributions = self.get_by_filters(
                filters=filters,
                limit=limit,
                offset=offset,
                order_by='created_at',
                order_direction='desc'
            )
            
            # Additional platform filtering if needed
            if platform:
                distributions = [
                    dist for dist in distributions 
                    if platform in json.loads(dist.platforms or '[]')
                ]
                
            return distributions
            
        except Exception as e:
            raise RepositoryException(f"Failed to get user distributions: {str(e)}")
            
    def get_distribution_analytics(self, 
                                 user_id: Optional[int] = None,
                                 platform: Optional[str] = None,
                                 days: int = 30) -> Dict[str, Any]:
        """
        Get content distribution analytics and performance metrics
        
        Args:
            user_id: Optional user ID filter
            platform: Optional platform filter
            days: Number of days for analytics
            
        Returns:
            Distribution analytics data
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            base_query = self.db_session.query(ContentDistribution).filter(
                ContentDistribution.created_at >= start_date
            )
            
            if user_id:
                base_query = base_query.filter(ContentDistribution.user_id == user_id)
                
            # Total distributions
            total_distributions = base_query.count()
            
            # Distributions by status
            status_stats = base_query.with_entities(
                ContentDistribution.status,
                func.count(ContentDistribution.id).label('count')
            ).group_by(ContentDistribution.status).all()
            
            # Success rate calculation
            completed_count = base_query.filter(
                ContentDistribution.status == 'completed'
            ).count()
            
            success_rate = (completed_count / total_distributions * 100) if total_distributions > 0 else 0
            
            # Daily distribution counts
            daily_stats = base_query.with_entities(
                func.date(ContentDistribution.created_at).label('date'),
                func.count(ContentDistribution.id).label('count')
            ).group_by(func.date(ContentDistribution.created_at)).order_by(
                func.date(ContentDistribution.created_at)
            ).all()
            
            # Platform performance (if platform results available)
            platform_performance = {}
            if not platform:
                # Get all distributions with platform results
                distributions_with_results = base_query.filter(
                    ContentDistribution.platform_results.isnot(None)
                ).all()
                
                for dist in distributions_with_results:
                    try:
                        results = json.loads(dist.platform_results or '{}')
                        for platform_name, metrics in results.items():
                            if platform_name not in platform_performance:
                                platform_performance[platform_name] = {
                                    'total_posts': 0,
                                    'total_views': 0,
                                    'total_engagement': 0,
                                    'successful_posts': 0
                                }
                            
                            platform_performance[platform_name]['total_posts'] += 1
                            if metrics.get('success', False):
                                platform_performance[platform_name]['successful_posts'] += 1
                                platform_performance[platform_name]['total_views'] += metrics.get('views', 0)
                                platform_performance[platform_name]['total_engagement'] += metrics.get('engagement', 0)
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            analytics = {
                'total_distributions': total_distributions,
                'success_rate': round(success_rate, 2),
                'status_distribution': {status: count for status, count in status_stats},
                'daily_distribution_counts': [
                    {'date': str(date), 'count': count} for date, count in daily_stats
                ],
                'platform_performance': platform_performance,
                'period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            raise RepositoryException(f"Failed to get distribution analytics: {str(e)}")
            
    def get_platform_performance_stats(self, platform: str, days: int = 30) -> Dict[str, Any]:
        """
        Get performance statistics for specific platform
        
        Args:
            platform: Platform name
            days: Number of days for statistics
            
        Returns:
            Platform performance statistics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get distributions for specific platform
            platform_distributions = self.db_session.query(ContentDistribution).filter(
                and_(
                    ContentDistribution.created_at >= start_date,
                    ContentDistribution.platforms.contains(f'"{platform}"')
                )
            ).all()
            
            total_distributions = len(platform_distributions)
            successful_distributions = 0
            total_views = 0
            total_engagement = 0
            total_reach = 0
            
            for dist in platform_distributions:
                if dist.platform_results:
                    try:
                        results = json.loads(dist.platform_results)
                        platform_result = results.get(platform, {})
                        
                        if platform_result.get('success', False):
                            successful_distributions += 1
                            total_views += platform_result.get('views', 0)
                            total_engagement += platform_result.get('engagement', 0)
                            total_reach += platform_result.get('reach', 0)
                    except (json.JSONDecodeError, KeyError):
                        continue
                        
            success_rate = (successful_distributions / total_distributions * 100) if total_distributions > 0 else 0
            avg_views = total_views / successful_distributions if successful_distributions > 0 else 0
            avg_engagement = total_engagement / successful_distributions if successful_distributions > 0 else 0
            avg_reach = total_reach / successful_distributions if successful_distributions > 0 else 0
            
            stats = {
                'platform': platform,
                'total_distributions': total_distributions,
                'successful_distributions': successful_distributions,
                'success_rate': round(success_rate, 2),
                'total_views': total_views,
                'total_engagement': total_engagement,
                'total_reach': total_reach,
                'average_views_per_post': round(avg_views, 2),
                'average_engagement_per_post': round(avg_engagement, 2),
                'average_reach_per_post': round(avg_reach, 2),
                'period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            raise RepositoryException(f"Failed to get platform performance stats: {str(e)}")
            
    def get_optimization_recommendations(self, user_id: int) -> Dict[str, Any]:
        """
        Get AI-powered optimization recommendations for user's distributions
        
        Args:
            user_id: User ID
            
        Returns:
            Optimization recommendations
        """
        try:
            # Get user's recent distributions (last 30 days)
            recent_distributions = self.get_user_distributions(user_id, limit=100)
            
            # Analyze performance patterns
            platform_performance = {}
            timing_performance = {}
            content_type_performance = {}
            
            for dist in recent_distributions:
                if dist.platform_results:
                    try:
                        results = json.loads(dist.platform_results)
                        platforms = json.loads(dist.platforms or '[]')
                        
                        for platform in platforms:
                            platform_result = results.get(platform, {})
                            
                            if platform not in platform_performance:
                                platform_performance[platform] = {
                                    'total_posts': 0,
                                    'successful_posts': 0,
                                    'total_engagement': 0
                                }
                            
                            platform_performance[platform]['total_posts'] += 1
                            if platform_result.get('success', False):
                                platform_performance[platform]['successful_posts'] += 1
                                platform_performance[platform]['total_engagement'] += platform_result.get('engagement', 0)
                                
                        # Analyze posting times
                        if dist.scheduled_for:
                            hour = dist.scheduled_for.hour
                            if hour not in timing_performance:
                                timing_performance[hour] = {'total': 0, 'successful': 0}
                            
                            timing_performance[hour]['total'] += 1
                            if any(results.get(p, {}).get('success', False) for p in platforms):
                                timing_performance[hour]['successful'] += 1
                                
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            # Generate recommendations
            recommendations = {
                'platform_recommendations': [],
                'timing_recommendations': [],
                'optimization_tips': [],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Platform recommendations
            for platform, stats in platform_performance.items():
                success_rate = (stats['successful_posts'] / stats['total_posts'] * 100) if stats['total_posts'] > 0 else 0
                avg_engagement = stats['total_engagement'] / stats['successful_posts'] if stats['successful_posts'] > 0 else 0
                
                recommendations['platform_recommendations'].append({
                    'platform': platform,
                    'success_rate': round(success_rate, 2),
                    'average_engagement': round(avg_engagement, 2),
                    'recommendation': self._generate_platform_recommendation(platform, success_rate, avg_engagement)
                })
            
            # Timing recommendations
            best_hours = sorted(
                timing_performance.items(),
                key=lambda x: (x[1]['successful'] / x[1]['total']) if x[1]['total'] > 0 else 0,
                reverse=True
            )[:3]
            
            recommendations['timing_recommendations'] = [
                {
                    'hour': hour,
                    'success_rate': round((stats['successful'] / stats['total'] * 100), 2),
                    'recommendation': f"Post at {hour}:00 for better engagement"
                }
                for hour, stats in best_hours if stats['total'] >= 2
            ]
            
            return recommendations
            
        except Exception as e:
            raise RepositoryException(f"Failed to get optimization recommendations: {str(e)}")
            
    def _generate_platform_recommendation(self, platform: str, success_rate: float, avg_engagement: float) -> str:
        """Generate platform-specific recommendation"""
        if success_rate > 80:
            return f"Excellent performance on {platform}! Continue current strategy."
        elif success_rate > 60:
            return f"Good performance on {platform}. Consider A/B testing different posting times."
        elif success_rate > 40:
            return f"Moderate performance on {platform}. Review content format and hashtag strategy."
        else:
            return f"Low performance on {platform}. Consider content optimization or different posting strategy."
            
    def schedule_bulk_distribution(self, 
                                 user_id: int,
                                 content_ids: List[int],
                                 platform_schedule: Dict[str, Dict[str, Any]]) -> List[ContentDistribution]:
        """
        Schedule bulk content distribution across multiple platforms
        
        Args:
            user_id: User ID
            content_ids: List of content IDs to distribute
            platform_schedule: Platform-specific scheduling configuration
            
        Returns:
            List of created distribution plans
        """
        try:
            distributions = []
            
            for content_id in content_ids:
                for platform, schedule_config in platform_schedule.items():
                    distribution_data = {
                        'user_id': user_id,
                        'content_id': content_id,
                        'platforms': json.dumps([platform]),
                        'schedule_data': json.dumps(schedule_config),
                        'optimization_settings': json.dumps(schedule_config.get('optimization', {})),
                        'scheduled_for': schedule_config.get('scheduled_for'),
                        'status': 'planned',
                        'created_at': datetime.utcnow()
                    }
                    
                    distribution = self.create(**distribution_data)
                    distributions.append(distribution)
                    
            self.logger.info(f"Created {len(distributions)} bulk distribution plans for user: {user_id}")
            return distributions
            
        except Exception as e:
            raise RepositoryException(f"Failed to schedule bulk distribution: {str(e)}")
            
    def cleanup_old_distributions(self, days_to_keep: int = 180) -> int:
        """
        Clean up old distribution records
        
        Args:
            days_to_keep: Number of days to keep records
            
        Returns:
            Number of cleaned up records
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Only delete completed or failed distributions older than cutoff
            deleted_count = self.bulk_delete({
                'created_at': {'lt': cutoff_date},
                'status': {'in': ['completed', 'failed']}
            })
            
            self.logger.info(f"Cleaned up {deleted_count} old distribution records")
            return deleted_count
            
        except Exception as e:
            raise RepositoryException(f"Failed to cleanup old distributions: {str(e)}")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
