"""Engagement Scoring Workflow

AI-powered engagement scoring and optimization workflow for gamification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class EngagementMetric(Enum):
    """Types of engagement metrics"""
    CONTENT_CREATION = "content_creation"
    SOCIAL_INTERACTION = "social_interaction"
    PLATFORM_USAGE = "platform_usage"
    COMMUNITY_PARTICIPATION = "community_participation"
    LEARNING_PROGRESS = "learning_progress"
    COLLABORATION = "collaboration"


@dataclass
class EngagementScore:
    """User engagement score data"""
    user_id: str
    overall_score: float
    metric_scores: Dict[str, float]
    score_history: List[float] = field(default_factory=list)
    engagement_level: str = "medium"  # low, medium, high, exceptional
    recommendations: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class EngagementScoringWorkflow:
    """AI-powered engagement scoring workflow"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.user_scores: Dict[str, EngagementScore] = {}
        self.scoring_weights = {
            EngagementMetric.CONTENT_CREATION: 0.25,
            EngagementMetric.SOCIAL_INTERACTION: 0.20,
            EngagementMetric.PLATFORM_USAGE: 0.15,
            EngagementMetric.COMMUNITY_PARTICIPATION: 0.20,
            EngagementMetric.LEARNING_PROGRESS: 0.10,
            EngagementMetric.COLLABORATION: 0.10
        }
        
    async def calculate_engagement_score(
        self,
        user_id: str,
        user_activities: Dict[str, Any],
        time_period_days: int = 30
    ) -> EngagementScore:
        """
        Calculate comprehensive engagement score for user
        
        Args:
            user_id: User identifier
            user_activities: User activity data
            time_period_days: Time period for calculation
            
        Returns:
            EngagementScore object
        """
        try:
            logger.info(f"Calculating engagement score for user {user_id}")
            
            # Calculate individual metric scores
            metric_scores = {}
            
            for metric in EngagementMetric:
                score = await self._calculate_metric_score(metric, user_activities, time_period_days)
                metric_scores[metric.value] = score
            
            # Calculate weighted overall score
            overall_score = sum(
                metric_scores[metric.value] * weight
                for metric, weight in self.scoring_weights.items()
            )
            
            # Determine engagement level
            engagement_level = await self._determine_engagement_level(overall_score)
            
            # Generate recommendations
            recommendations = await self._generate_engagement_recommendations(
                user_id, metric_scores, user_activities
            )
            
            # Update score history
            existing_score = self.user_scores.get(user_id)
            score_history = existing_score.score_history if existing_score else []
            score_history.append(overall_score)
            
            # Keep only last 30 scores
            if len(score_history) > 30:
                score_history = score_history[-30:]
            
            # Create engagement score object
            engagement_score = EngagementScore(
                user_id=user_id,
                overall_score=overall_score,
                metric_scores=metric_scores,
                score_history=score_history,
                engagement_level=engagement_level,
                recommendations=recommendations
            )
            
            # Store score
            self.user_scores[user_id] = engagement_score
            
            # Record metrics
            await self.metrics_collector.record_metric("engagement_score_calculated", 1)
            await self.metrics_collector.record_metric("user_engagement_score", overall_score)
            
            logger.info(f"Engagement score calculated: {overall_score:.3f} ({engagement_level})")
            return engagement_score
            
        except Exception as e:
            logger.error(f"Engagement score calculation failed: {e}")
            raise WorkflowError(f"Engagement score calculation failed: {e}")
    
    async def _calculate_metric_score(
        self, 
        metric: EngagementMetric, 
        activities: Dict[str, Any], 
        time_period_days: int
    ) -> float:
        """Calculate score for individual engagement metric"""
        
        if metric == EngagementMetric.CONTENT_CREATION:
            return await self._score_content_creation(activities, time_period_days)
        
        elif metric == EngagementMetric.SOCIAL_INTERACTION:
            return await self._score_social_interaction(activities, time_period_days)
        
        elif metric == EngagementMetric.PLATFORM_USAGE:
            return await self._score_platform_usage(activities, time_period_days)
        
        elif metric == EngagementMetric.COMMUNITY_PARTICIPATION:
            return await self._score_community_participation(activities, time_period_days)
        
        elif metric == EngagementMetric.LEARNING_PROGRESS:
            return await self._score_learning_progress(activities, time_period_days)
        
        elif metric == EngagementMetric.COLLABORATION:
            return await self._score_collaboration(activities, time_period_days)
        
        return 0.0
    
    async def _score_content_creation(self, activities: Dict[str, Any], days: int) -> float:
        """Score content creation activities"""
        
        posts_created = activities.get("posts_created", 0)
        content_quality_avg = activities.get("content_quality_avg", 0.5)
        media_types_used = len(activities.get("media_types", []))
        
        # Normalize based on time period
        posts_per_day = posts_created / days
        
        # Score components
        volume_score = min(posts_per_day / 2.0, 1.0)  # 2 posts/day = max
        quality_score = content_quality_avg
        diversity_score = min(media_types_used / 4.0, 1.0)  # 4 types = max
        
        # Weighted combination
        final_score = (volume_score * 0.4 + quality_score * 0.4 + diversity_score * 0.2)
        
        return min(final_score, 1.0)
    
    async def _score_social_interaction(self, activities: Dict[str, Any], days: int) -> float:
        """Score social interaction activities"""
        
        likes_given = activities.get("likes_given", 0)
        comments_made = activities.get("comments_made", 0)
        shares_made = activities.get("shares_made", 0)
        replies_to_comments = activities.get("replies_to_comments", 0)
        
        # Calculate daily averages
        daily_likes = likes_given / days
        daily_comments = comments_made / days
        daily_shares = shares_made / days
        daily_replies = replies_to_comments / days
        
        # Score components (normalized)
        likes_score = min(daily_likes / 10.0, 1.0)  # 10 likes/day = max
        comments_score = min(daily_comments / 5.0, 1.0)  # 5 comments/day = max
        shares_score = min(daily_shares / 2.0, 1.0)  # 2 shares/day = max
        replies_score = min(daily_replies / 3.0, 1.0)  # 3 replies/day = max
        
        # Weighted combination
        final_score = (likes_score * 0.2 + comments_score * 0.3 + 
                      shares_score * 0.25 + replies_score * 0.25)
        
        return min(final_score, 1.0)
    
    async def _score_platform_usage(self, activities: Dict[str, Any], days: int) -> float:
        """Score platform usage patterns"""
        
        login_days = activities.get("login_days", 0)
        session_duration_avg = activities.get("session_duration_avg", 0)
        features_used = len(activities.get("features_used", []))
        
        # Score components
        consistency_score = login_days / days  # Daily login rate
        duration_score = min(session_duration_avg / 60.0, 1.0)  # 60 min = max
        feature_adoption_score = min(features_used / 10.0, 1.0)  # 10 features = max
        
        # Weighted combination
        final_score = (consistency_score * 0.5 + duration_score * 0.3 + 
                      feature_adoption_score * 0.2)
        
        return min(final_score, 1.0)
    
    async def _score_community_participation(self, activities: Dict[str, Any], days: int) -> float:
        """Score community participation"""
        
        forum_posts = activities.get("forum_posts", 0)
        events_attended = activities.get("events_attended", 0)
        challenges_joined = activities.get("challenges_joined", 0)
        help_provided = activities.get("help_provided", 0)
        
        # Normalize to daily rates
        daily_forum = forum_posts / days
        weekly_events = events_attended / (days / 7)
        weekly_challenges = challenges_joined / (days / 7)
        daily_help = help_provided / days
        
        # Score components
        forum_score = min(daily_forum / 1.0, 1.0)  # 1 post/day = max
        events_score = min(weekly_events / 2.0, 1.0)  # 2 events/week = max
        challenges_score = min(weekly_challenges / 3.0, 1.0)  # 3 challenges/week = max
        help_score = min(daily_help / 2.0, 1.0)  # 2 helps/day = max
        
        # Weighted combination
        final_score = (forum_score * 0.3 + events_score * 0.25 + 
                      challenges_score * 0.25 + help_score * 0.2)
        
        return min(final_score, 1.0)
    
    async def _score_learning_progress(self, activities: Dict[str, Any], days: int) -> float:
        """Score learning and skill development"""
        
        tutorials_completed = activities.get("tutorials_completed", 0)
        skills_improved = activities.get("skills_improved", 0)
        certifications_earned = activities.get("certifications_earned", 0)
        
        # Score components
        tutorials_score = min(tutorials_completed / 10.0, 1.0)  # 10 tutorials = max
        skills_score = min(skills_improved / 5.0, 1.0)  # 5 skills = max
        certifications_score = min(certifications_earned / 2.0, 1.0)  # 2 certs = max
        
        # Weighted combination
        final_score = (tutorials_score * 0.4 + skills_score * 0.4 + 
                      certifications_score * 0.2)
        
        return min(final_score, 1.0)
    
    async def _score_collaboration(self, activities: Dict[str, Any], days: int) -> float:
        """Score collaboration activities"""
        
        collaborations_initiated = activities.get("collaborations_initiated", 0)
        collaborations_joined = activities.get("collaborations_joined", 0)
        team_projects = activities.get("team_projects", 0)
        mentoring_provided = activities.get("mentoring_provided", 0)
        
        # Score components
        initiation_score = min(collaborations_initiated / 2.0, 1.0)  # 2 initiations = max
        participation_score = min(collaborations_joined / 3.0, 1.0)  # 3 joins = max
        team_score = min(team_projects / 2.0, 1.0)  # 2 projects = max
        mentoring_score = min(mentoring_provided / 5.0, 1.0)  # 5 mentoring = max
        
        # Weighted combination
        final_score = (initiation_score * 0.3 + participation_score * 0.3 + 
                      team_score * 0.2 + mentoring_score * 0.2)
        
        return min(final_score, 1.0)
    
    async def _determine_engagement_level(self, overall_score: float) -> str:
        """Determine engagement level from overall score"""
        
        if overall_score >= 0.9:
            return "exceptional"
        elif overall_score >= 0.7:
            return "high"
        elif overall_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    async def _generate_engagement_recommendations(
        self, 
        user_id: str, 
        metric_scores: Dict[str, float], 
        activities: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized engagement recommendations"""
        
        recommendations = []
        
        # Find the lowest scoring metrics
        sorted_metrics = sorted(metric_scores.items(), key=lambda x: x[1])
        
        for metric_name, score in sorted_metrics[:3]:  # Focus on top 3 improvements
            if score < 0.5:  # Only recommend if significantly low
                
                if metric_name == "content_creation":
                    recommendations.append("Try creating more diverse content types (video, audio, images)")
                    recommendations.append("Focus on content quality - use AI suggestions for improvement")
                
                elif metric_name == "social_interaction":
                    recommendations.append("Engage more with community content - like and comment on posts")
                    recommendations.append("Join conversations and reply to comments on your content")
                
                elif metric_name == "platform_usage":
                    recommendations.append("Explore new platform features to enhance your experience")
                    recommendations.append("Try to maintain consistent daily platform usage")
                
                elif metric_name == "community_participation":
                    recommendations.append("Join community challenges and events")
                    recommendations.append("Participate in forum discussions and help other creators")
                
                elif metric_name == "learning_progress":
                    recommendations.append("Complete tutorials to improve your skills")
                    recommendations.append("Set learning goals and track your progress")
                
                elif metric_name == "collaboration":
                    recommendations.append("Initiate collaborations with other creators")
                    recommendations.append("Join team projects and mentoring programs")
        
        # Always include a positive reinforcement
        best_metric = max(metric_scores.items(), key=lambda x: x[1])
        recommendations.append(f"Keep up the excellent work in {best_metric[0].replace('_', ' ')}!")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def get_engagement_trends(self, user_id: str) -> Dict[str, Any]:
        """Get engagement trends for user"""
        
        if user_id not in self.user_scores:
            return {"error": "No engagement data found"}
        
        user_score = self.user_scores[user_id]
        history = user_score.score_history
        
        if len(history) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend
        recent_avg = sum(history[-7:]) / min(len(history), 7)  # Last 7 scores
        older_avg = sum(history[-14:-7]) / min(len(history[-14:-7]), 7) if len(history) > 7 else recent_avg
        
        trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        trend_strength = abs(recent_avg - older_avg)
        
        return {
            "current_score": user_score.overall_score,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "recent_average": recent_avg,
            "engagement_level": user_score.engagement_level,
            "history_length": len(history)
        }
    
    async def get_engagement_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get engagement leaderboard"""
        
        # Sort users by engagement score
        sorted_users = sorted(
            self.user_scores.values(),
            key=lambda x: x.overall_score,
            reverse=True
        )
        
        leaderboard = []
        for i, user_score in enumerate(sorted_users[:limit]):
            leaderboard.append({
                "rank": i + 1,
                "user_id": user_score.user_id,
                "engagement_score": round(user_score.overall_score, 3),
                "engagement_level": user_score.engagement_level,
                "last_updated": user_score.last_updated
            })
        
        return leaderboard