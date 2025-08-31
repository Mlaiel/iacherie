"""Content Optimization Repository

Enterprise-grade repository for AI-powered content optimization,
SEO enhancement, and performance-driven content suggestions.

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
"""from typing import Dict, List, Optional, Union, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from datetime import datetime, timedelta
import uuid
import json
import logging
import re
from collections import Counter

from .base_repository import BaseRepository, RepositoryException
from ..models.content_optimization import ContentOptimization

logger = logging.getLogger(__name__)

class ContentOptimizationRepository(BaseRepository[ContentOptimization]):
    """    Repository for content optimization management with enterprise-grade
    features including AI-powered SEO, hashtag optimization, and performance enhancement.
    """    
    def __init__(self, db_session: Session):
        """Initialize Content Optimization Repository"""        super().__init__(db_session, ContentOptimization)
        
    def create_optimization_analysis(self, 
                                   user_id: int,
                                   content_id: int,
                                   content_type: str,
                                   original_content: Dict[str, Any],
                                   analysis_type: str,
                                   optimization_goals: List[str]) -> ContentOptimization:
        """        Create new content optimization analysis
        
        Args:
            user_id: User ID
            content_id: Content being optimized
            content_type: Type of content (post, video, audio, image)
            original_content: Original content data
            analysis_type: Type of analysis (seo, engagement, hashtag, readability)
            optimization_goals: List of optimization goals
            
        Returns:
            Created content optimization instance
        """        try:
            optimization_data = {
                'user_id': user_id,
                'content_id': content_id,
                'content_type': content_type,
                'original_content': json.dumps(original_content),
                'analysis_type': analysis_type,
                'optimization_goals': json.dumps(optimization_goals),
                'status': 'pending',
                'created_at': datetime.utcnow()
            }
            
            optimization = self.create(**optimization_data)
            
            self.logger.info(f"Created optimization analysis ID: {optimization.id} for content: {content_id}")
            return optimization
            
        except Exception as e:
            raise RepositoryException(f"Failed to create optimization analysis: {str(e)}")
            
    def update_optimization_results(self, 
                                  optimization_id: int,
                                  status: str,
                                  suggestions: Dict[str, Any],
                                  optimized_content: Optional[Dict[str, Any]] = None,
                                  seo_score: Optional[float] = None,
                                  readability_score: Optional[float] = None) -> Optional[ContentOptimization]:
        """        Update optimization analysis with results
        
        Args:
            optimization_id: Optimization ID
            status: New status (pending, completed, failed)
            suggestions: Optimization suggestions
            optimized_content: Optimized content data
            seo_score: SEO score (0-100)
            readability_score: Readability score (0-100)
            
        Returns:
            Updated optimization instance
        """        try:
            update_data = {
                'status': status,
                'suggestions': json.dumps(suggestions),
                'updated_at': datetime.utcnow()
            }
            
            if status == 'completed':
                update_data['completed_at'] = datetime.utcnow()
                
            if optimized_content:
                update_data['optimized_content'] = json.dumps(optimized_content)
                
            if seo_score is not None:
                update_data['seo_score'] = seo_score
                
            if readability_score is not None:
                update_data['readability_score'] = readability_score
                
            optimization = self.update(optimization_id, **update_data)
            
            if optimization:
                self.logger.info(f"Updated optimization {optimization_id} with results")
                
            return optimization
            
        except Exception as e:
            raise RepositoryException(f"Failed to update optimization results: {str(e)}")
            
    def get_user_optimizations(self, 
                             user_id: int,
                             content_type: Optional[str] = None,
                             analysis_type: Optional[str] = None,
                             limit: int = 50,
                             offset: int = 0) -> List[ContentOptimization]:
        """        Get user's content optimizations with filtering
        
        Args:
            user_id: User ID
            content_type: Filter by content type
            analysis_type: Filter by analysis type
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List of content optimizations
        """        try:
            filters = {'user_id': user_id}
            
            if content_type:
                filters['content_type'] = content_type
                
            if analysis_type:
                filters['analysis_type'] = analysis_type
                
            optimizations = self.get_by_filters(
                filters=filters,
                limit=limit,
                offset=offset,
                order_by='created_at',
                order_direction='desc'
            )
            
            return optimizations
            
        except Exception as e:
            raise RepositoryException(f"Failed to get user optimizations: {str(e)}")
            
    def analyze_seo_performance(self, 
                              user_id: int,
                              days: int = 30) -> Dict[str, Any]:
        """        Analyze SEO performance trends and improvements
        
        Args:
            user_id: User ID
            days: Number of days for analysis
            
        Returns:
            SEO performance analysis
        """        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            seo_optimizations = self.db_session.query(ContentOptimization).filter(
                and_(
                    ContentOptimization.user_id == user_id,
                    ContentOptimization.analysis_type == 'seo',
                    ContentOptimization.status == 'completed',
                    ContentOptimization.created_at >= start_date,
                    ContentOptimization.seo_score.isnot(None)
                )
            ).order_by(ContentOptimization.created_at).all()
            
            if not seo_optimizations:
                return {
                    'total_optimizations': 0,
                    'average_seo_score': 0,
                    'trend': 'no_data',
                    'improvements': [],
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            # Calculate trends
            seo_scores = [opt.seo_score for opt in seo_optimizations]
            average_score = sum(seo_scores) / len(seo_scores)
            
            # Trend analysis
            first_half = seo_scores[:len(seo_scores)//2]
            second_half = seo_scores[len(seo_scores)//2:]
            
            if len(first_half) > 0 and len(second_half) > 0:
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg + 5:
                    trend = 'improving'
                elif second_avg < first_avg - 5:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            # Common improvement suggestions
            improvement_suggestions = []
            for opt in seo_optimizations:
                try:
                    suggestions = json.loads(opt.suggestions or '{}')
                    if 'seo_improvements' in suggestions:
                        improvement_suggestions.extend(suggestions['seo_improvements'])
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Count most common suggestions
            suggestion_counts = Counter(improvement_suggestions)
            common_improvements = [
                {'suggestion': suggestion, 'frequency': count}
                for suggestion, count in suggestion_counts.most_common(5)
            ]
            
            analysis = {
                'total_optimizations': len(seo_optimizations),
                'average_seo_score': round(average_score, 2),
                'highest_score': max(seo_scores),
                'lowest_score': min(seo_scores),
                'trend': trend,
                'score_distribution': self._calculate_score_distribution(seo_scores),
                'common_improvements': common_improvements,
                'monthly_progress': self._calculate_monthly_progress(seo_optimizations),
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            raise RepositoryException(f"Failed to analyze SEO performance: {str(e)}")
            
    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution by ranges"""        distribution = {
            'excellent': 0,  # 90-100
            'good': 0,       # 70-89
            'fair': 0,       # 50-69
            'poor': 0        # 0-49
        }
        
        for score in scores:
            if score >= 90:
                distribution['excellent'] += 1
            elif score >= 70:
                distribution['good'] += 1
            elif score >= 50:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
                
        return distribution
        
    def _calculate_monthly_progress(self, optimizations: List[ContentOptimization]) -> Dict[str, Any]:
        """Calculate monthly progress in SEO scores"""        monthly_data = {}
        
        for opt in optimizations:
            month_key = opt.created_at.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'scores': [], 'count': 0}
            
            monthly_data[month_key]['scores'].append(opt.seo_score)
            monthly_data[month_key]['count'] += 1
        
        # Calculate monthly averages
        monthly_progress = []
        for month, data in sorted(monthly_data.items()):
            avg_score = sum(data['scores']) / len(data['scores'])
            monthly_progress.append({
                'month': month,
                'average_score': round(avg_score, 2),
                'optimization_count': data['count']
            })
            
        return monthly_progress
        
    def get_hashtag_optimization_insights(self, 
                                        user_id: int,
                                        platform: Optional[str] = None,
                                        days: int = 30) -> Dict[str, Any]:
        """        Get hashtag optimization insights and performance data
        
        Args:
            user_id: User ID
            platform: Optional platform filter
            days: Number of days for analysis
            
        Returns:
            Hashtag optimization insights
        """        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            hashtag_optimizations = self.db_session.query(ContentOptimization).filter(
                and_(
                    ContentOptimization.user_id == user_id,
                    ContentOptimization.analysis_type == 'hashtag',
                    ContentOptimization.status == 'completed',
                    ContentOptimization.created_at >= start_date
                )
            ).all()
            
            hashtag_performance = {}
            suggested_hashtags = Counter()
            hashtag_trends = {}
            
            for opt in hashtag_optimizations:
                try:
                    suggestions = json.loads(opt.suggestions or '{}')
                    original_content = json.loads(opt.original_content or '{}')
                    
                    # Extract hashtags from suggestions
                    if 'recommended_hashtags' in suggestions:
                        for hashtag in suggestions['recommended_hashtags']:
                            suggested_hashtags[hashtag] += 1
                    
                    # Analyze hashtag performance if available
                    if 'hashtag_performance' in suggestions:
                        for hashtag, metrics in suggestions['hashtag_performance'].items():
                            if hashtag not in hashtag_performance:
                                hashtag_performance[hashtag] = {
                                    'usage_count': 0,
                                    'total_reach': 0,
                                    'total_engagement': 0,
                                    'average_performance': 0
                                }
                            
                            hashtag_performance[hashtag]['usage_count'] += 1
                            hashtag_performance[hashtag]['total_reach'] += metrics.get('reach', 0)
                            hashtag_performance[hashtag]['total_engagement'] += metrics.get('engagement', 0)
                            
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Calculate average performance for hashtags
            for hashtag, data in hashtag_performance.items():
                if data['usage_count'] > 0:
                    data['average_reach'] = data['total_reach'] / data['usage_count']
                    data['average_engagement'] = data['total_engagement'] / data['usage_count']
                    data['average_performance'] = (data['average_reach'] + data['average_engagement']) / 2
            
            # Sort hashtags by performance
            top_performing_hashtags = sorted(
                hashtag_performance.items(),
                key=lambda x: x[1]['average_performance'],
                reverse=True
            )[:10]
            
            most_suggested_hashtags = suggested_hashtags.most_common(10)
            
            insights = {
                'total_hashtag_optimizations': len(hashtag_optimizations),
                'top_performing_hashtags': [
                    {
                        'hashtag': hashtag,
                        'average_performance': round(data['average_performance'], 2),
                        'usage_count': data['usage_count'],
                        'average_reach': round(data['average_reach'], 2),
                        'average_engagement': round(data['average_engagement'], 2)
                    }
                    for hashtag, data in top_performing_hashtags
                ],
                'most_suggested_hashtags': [
                    {'hashtag': hashtag, 'suggestion_count': count}
                    for hashtag, count in most_suggested_hashtags
                ],
                'hashtag_optimization_tips': self._generate_hashtag_tips(hashtag_performance),
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return insights
            
        except Exception as e:
            raise RepositoryException(f"Failed to get hashtag optimization insights: {str(e)}")
            
    def _generate_hashtag_tips(self, hashtag_performance: Dict[str, Any]) -> List[str]:
        """Generate hashtag optimization tips based on performance data"""        tips = []
        
        if not hashtag_performance:
            tips.append("Start using hashtags to improve content discoverability")
            tips.append("Research trending hashtags in your niche")
            return tips
        
        # Analyze hashtag diversity
        total_hashtags = len(hashtag_performance)
        highly_used_hashtags = sum(1 for data in hashtag_performance.values() if data['usage_count'] > 5)
        
        if highly_used_hashtags / total_hashtags > 0.3:
            tips.append("Consider diversifying your hashtag strategy to reach new audiences")
        
        # Performance-based tips
        avg_performances = [data['average_performance'] for data in hashtag_performance.values()]
        if avg_performances:
            avg_overall_performance = sum(avg_performances) / len(avg_performances)
            
            if avg_overall_performance < 50:
                tips.append("Focus on using more specific, niche hashtags for better engagement")
                tips.append("Research competitor hashtags for inspiration")
            else:
                tips.append("Great hashtag performance! Continue optimizing based on trending topics")
        
        return tips
        
    def get_content_readability_analysis(self, 
                                       user_id: int,
                                       content_type: str = 'post',
                                       days: int = 30) -> Dict[str, Any]:
        """        Analyze content readability trends and improvements
        
        Args:
            user_id: User ID
            content_type: Content type to analyze
            days: Number of days for analysis
            
        Returns:
            Readability analysis data
        """        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            readability_optimizations = self.db_session.query(ContentOptimization).filter(
                and_(
                    ContentOptimization.user_id == user_id,
                    ContentOptimization.content_type == content_type,
                    ContentOptimization.analysis_type == 'readability',
                    ContentOptimization.status == 'completed',
                    ContentOptimization.created_at >= start_date,
                    ContentOptimization.readability_score.isnot(None)
                )
            ).order_by(ContentOptimization.created_at).all()
            
            if not readability_optimizations:
                return {
                    'total_analyses': 0,
                    'average_readability_score': 0,
                    'trend': 'no_data',
                    'common_issues': [],
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            # Calculate readability metrics
            readability_scores = [opt.readability_score for opt in readability_optimizations]
            average_score = sum(readability_scores) / len(readability_scores)
            
            # Common readability issues
            common_issues = Counter()
            improvement_suggestions = Counter()
            
            for opt in readability_optimizations:
                try:
                    suggestions = json.loads(opt.suggestions or '{}')
                    
                    if 'readability_issues' in suggestions:
                        for issue in suggestions['readability_issues']:
                            common_issues[issue] += 1
                    
                    if 'readability_improvements' in suggestions:
                        for improvement in suggestions['readability_improvements']:
                            improvement_suggestions[improvement] += 1
                            
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Trend analysis
            if len(readability_scores) > 1:
                first_half = readability_scores[:len(readability_scores)//2]
                second_half = readability_scores[len(readability_scores)//2:]
                
                first_avg = sum(first_half) / len(first_half) if first_half else 0
                second_avg = sum(second_half) / len(second_half) if second_half else 0
                
                if second_avg > first_avg + 5:
                    trend = 'improving'
                elif second_avg < first_avg - 5:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            analysis = {
                'total_analyses': len(readability_optimizations),
                'average_readability_score': round(average_score, 2),
                'highest_score': max(readability_scores),
                'lowest_score': min(readability_scores),
                'trend': trend,
                'score_distribution': self._calculate_readability_distribution(readability_scores),
                'common_issues': [
                    {'issue': issue, 'frequency': count}
                    for issue, count in common_issues.most_common(5)
                ],
                'improvement_suggestions': [
                    {'suggestion': suggestion, 'frequency': count}
                    for suggestion, count in improvement_suggestions.most_common(5)
                ],
                'content_type': content_type,
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            raise RepositoryException(f"Failed to analyze content readability: {str(e)}")
            
    def _calculate_readability_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate readability score distribution"""        distribution = {
            'very_easy': 0,    # 90-100
            'easy': 0,         # 80-89
            'fairly_easy': 0,  # 70-79
            'standard': 0,     # 60-69
            'fairly_difficult': 0,  # 50-59
            'difficult': 0,    # 30-49
            'very_difficult': 0 # 0-29
        }
        
        for score in scores:
            if score >= 90:
                distribution['very_easy'] += 1
            elif score >= 80:
                distribution['easy'] += 1
            elif score >= 70:
                distribution['fairly_easy'] += 1
            elif score >= 60:
                distribution['standard'] += 1
            elif score >= 50:
                distribution['fairly_difficult'] += 1
            elif score >= 30:
                distribution['difficult'] += 1
            else:
                distribution['very_difficult'] += 1
                
        return distribution
        
    def get_optimization_recommendations(self, 
                                       user_id: int,
                                       content_type: Optional[str] = None) -> Dict[str, Any]:
        """        Get personalized optimization recommendations for user
        
        Args:
            user_id: User ID
            content_type: Optional content type filter
            
        Returns:
            Personalized optimization recommendations
        """        try:
            # Get recent optimizations for analysis
            filters = {'user_id': user_id, 'status': 'completed'}
            if content_type:
                filters['content_type'] = content_type
                
            recent_optimizations = self.get_by_filters(
                filters=filters,
                limit=50,
                order_by='created_at',
                order_direction='desc'
            )
            
            if not recent_optimizations:
                return {
                    'recommendations': [
                        "Start optimizing your content to improve performance",
                        "Focus on SEO optimization for better discoverability",
                        "Use hashtag optimization to reach more audiences"
                    ],
                    'priority_areas': ['seo', 'hashtag', 'readability'],
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            # Analyze optimization patterns
            seo_scores = []
            readability_scores = []
            optimization_types = Counter()
            
            for opt in recent_optimizations:
                optimization_types[opt.analysis_type] += 1
                
                if opt.seo_score is not None:
                    seo_scores.append(opt.seo_score)
                    
                if opt.readability_score is not None:
                    readability_scores.append(opt.readability_score)
            
            recommendations = []
            priority_areas = []
            
            # SEO recommendations
            if seo_scores:
                avg_seo = sum(seo_scores) / len(seo_scores)
                if avg_seo < 70:
                    recommendations.append(f"Improve SEO optimization - current average score: {avg_seo:.1f}")
                    priority_areas.append('seo')
                else:
                    recommendations.append(f"Excellent SEO performance - maintain current strategy")
            else:
                recommendations.append("Start SEO optimization to improve content discoverability")
                priority_areas.append('seo')
            
            # Readability recommendations
            if readability_scores:
                avg_readability = sum(readability_scores) / len(readability_scores)
                if avg_readability < 60:
                    recommendations.append(f"Focus on improving content readability - current score: {avg_readability:.1f}")
                    priority_areas.append('readability')
            else:
                recommendations.append("Analyze content readability to ensure audience engagement")
                priority_areas.append('readability')
            
            # Optimization frequency recommendations
            if optimization_types['hashtag'] < 5:
                recommendations.append("Increase hashtag optimization frequency for better reach")
                priority_areas.append('hashtag')
            
            if optimization_types['engagement'] < 3:
                recommendations.append("Analyze engagement patterns to optimize posting strategy")
                priority_areas.append('engagement')
            
            return {
                'recommendations': recommendations,
                'priority_areas': priority_areas[:3],  # Top 3 priority areas
                'current_performance': {
                    'average_seo_score': round(sum(seo_scores) / len(seo_scores), 2) if seo_scores else None,
                    'average_readability_score': round(sum(readability_scores) / len(readability_scores), 2) if readability_scores else None,
                    'optimization_count': len(recent_optimizations)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise RepositoryException(f"Failed to get optimization recommendations: {str(e)}")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
