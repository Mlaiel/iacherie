"""Social Competition AI - Intelligent Social Competition Management System

Advanced AI system for managing social competitions, tournaments, and collaborative
challenges among content creators in the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This social competition AI and algorithms are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED and will result in legal action.
"""
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class CompetitionType(Enum):
    """Types of social competitions"""
    INDIVIDUAL_CHALLENGE = "individual_challenge"
    TEAM_TOURNAMENT = "team_tournament"
    COLLABORATIVE_PROJECT = "collaborative_project"
    SKILL_CONTEST = "skill_contest"
    CREATIVE_SHOWCASE = "creative_showcase"
    MONETIZATION_RACE = "monetization_race"
    COMMUNITY_CHALLENGE = "community_challenge"

class CompetitionStatus(Enum):
    """Competition status states"""
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class CompetitionConfig:
    """Configuration for social competition management"""
    max_active_competitions: int = 10
    max_participants_per_competition: int = 100
    auto_matching_enabled: bool = True
    skill_based_matching: bool = True
    reward_optimization_enabled: bool = True
    real_time_updates_enabled: bool = True

@dataclass
class SocialCompetition:
    """Social competition instance"""
    competition_id: str
    title: str
    description: str
    competition_type: CompetitionType
    status: CompetitionStatus
    max_participants: int
    current_participants: List[str] = field(default_factory=list)
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    rules: Dict[str, Any] = field(default_factory=dict)
    rewards: Dict[str, Any] = field(default_factory=dict)
    leaderboard: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_by: str = ""
    ai_insights: Dict[str, Any] = field(default_factory=dict)

class SocialCompetitionManager:
    """
    Advanced AI-powered social competition management system.
    
    Features:
    - Intelligent competition matching and recommendations
    - Dynamic leaderboard management
    - Skill-based participant grouping
    - Real-time competition analytics
    - Automated reward distribution
    - Social engagement optimization
    """
    
    def __init__(self, config: Optional[CompetitionConfig] = None):
        self.config = config or CompetitionConfig()
        self.active_competitions: Dict[str, SocialCompetition] = {}
        self.user_competition_history: Dict[str, List[str]] = {}
        self.competition_templates: Dict[str, Dict[str, Any]] = {}
        self.matching_algorithms: Dict[str, Any] = {}
        
        # Initialize competition system
        self._initialize_competition_system()
        
        logger.info("SocialCompetitionManager initialized successfully")
    
    def _initialize_competition_system(self):
        """Initialize competition management system"""
        # Initialize competition templates
        self._initialize_competition_templates()
        
        # Initialize matching algorithms
        self.matching_algorithms = {
            'skill_based': self._match_by_skill_level,
            'interest_based': self._match_by_interests,
            'collaboration_history': self._match_by_collaboration_history,
            'engagement_level': self._match_by_engagement_level
        }
    
    def _initialize_competition_templates(self):
        """Initialize default competition templates"""
        self.competition_templates = {
            'weekly_creator_challenge': {
                'title': 'Weekly Creator Challenge',
                'description': 'Create your best content this week and compete with peers',
                'type': CompetitionType.INDIVIDUAL_CHALLENGE,
                'duration_days': 7,
                'max_participants': 50,
                'rewards': {'winner': 500, 'top_3': 200, 'participation': 50}
            },
            'collaboration_tournament': {
                'title': 'Collaboration Masters Tournament',
                'description': 'Team up and create amazing collaborative content',
                'type': CompetitionType.TEAM_TOURNAMENT,
                'duration_days': 14,
                'max_participants': 40,
                'rewards': {'winning_team': 1000, 'runner_up': 500, 'participation': 100}
            },
            'skill_showcase': {
                'title': 'Monthly Skill Showcase',
                'description': 'Demonstrate your expertise in your chosen field',
                'type': CompetitionType.SKILL_CONTEST,
                'duration_days': 30,
                'max_participants': 30,
                'rewards': {'expert': 750, 'advanced': 300, 'promising': 150}
            }
        }
    
    async def process_competition_data(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user activity for competition management.
        
        Args:
            user_id: Unique user identifier
            activity_data: User activity and performance data
            
        Returns:
            Competition recommendations and updates
        """
        try:
            # Update user competition activity
            await self._update_user_competition_activity(user_id, activity_data)
            
            # Find suitable competitions
            recommended_competitions = await self._recommend_competitions(user_id, activity_data)
            
            # Update active competitions user is participating in
            participation_updates = await self._update_user_participations(user_id, activity_data)
            
            # Generate competition insights
            insights = await self._generate_competition_insights(user_id, activity_data)
            
            return {
                'user_id': user_id,
                'recommended_competitions': recommended_competitions,
                'participation_updates': participation_updates,
                'competition_insights': insights,
                'available_competitions': await self._get_available_competitions(user_id),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing competition data: {str(e)}")
            return {'error': str(e)}
    
    async def _recommend_competitions(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend suitable competitions for user"""
        recommendations = []
        
        user_profile = {
            'skill_level': activity_data.get('level', 1),
            'content_types': activity_data.get('content_types', []),
            'collaboration_preference': activity_data.get('collaboration_preference', 0.5),
            'competition_history': self.user_competition_history.get(user_id, [])
        }
        
        # Analyze suitable competitions
        for comp_id, competition in self.active_competitions.items():
            if competition.status != CompetitionStatus.REGISTRATION_OPEN:
                continue
            
            if len(competition.current_participants) >= competition.max_participants:
                continue
            
            if user_id in competition.current_participants:
                continue
            
            # Calculate suitability score
            suitability_score = await self._calculate_competition_suitability(
                user_profile, competition
            )
            
            if suitability_score >= 0.6:
                recommendations.append({
                    'competition_id': comp_id,
                    'title': competition.title,
                    'type': competition.competition_type.value,
                    'suitability_score': suitability_score,
                    'participants_count': len(competition.current_participants),
                    'max_participants': competition.max_participants,
                    'end_date': competition.end_date.isoformat() if competition.end_date else None,
                    'estimated_rewards': competition.rewards
                })
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def _calculate_competition_suitability(
        self,
        user_profile: Dict[str, Any],
        competition: SocialCompetition
    ) -> float:
        """Calculate how suitable a competition is for a user"""
        suitability_factors = []
        
        # Skill level matching
        user_skill = user_profile['skill_level']
        if competition.competition_type in [CompetitionType.SKILL_CONTEST, CompetitionType.CREATIVE_SHOWCASE]:
            # Prefer competitions with similar skill levels
            avg_participant_skill = 5  # Simplified average
            skill_diff = abs(user_skill - avg_participant_skill)
            skill_factor = max(0, 1 - skill_diff / 10)
            suitability_factors.append(skill_factor * 0.3)
        
        # Competition type preference
        type_preference = self._get_user_type_preference(user_profile, competition.competition_type)
        suitability_factors.append(type_preference * 0.25)
        
        # Participation level (not too crowded, not too empty)
        participation_ratio = len(competition.current_participants) / competition.max_participants
        participation_factor = 1 - abs(participation_ratio - 0.6)  # Prefer 60% full
        suitability_factors.append(participation_factor * 0.2)
        
        # Timing suitability
        if competition.end_date:
            days_remaining = (competition.end_date - datetime.now(timezone.utc)).days
            timing_factor = min(1.0, days_remaining / 7)  # Prefer competitions with reasonable time
            suitability_factors.append(timing_factor * 0.15)
        
        # Novelty factor (prefer new types of competitions)
        competition_history = user_profile.get('competition_history', [])
        similar_competitions = sum(1 for comp_id in competition_history 
                                 if self._is_similar_competition_type(comp_id, competition.competition_type))
        novelty_factor = max(0.3, 1 - similar_competitions / 10)
        suitability_factors.append(novelty_factor * 0.1)
        
        return sum(suitability_factors)
    
    def _get_user_type_preference(
        self,
        user_profile: Dict[str, Any],
        competition_type: CompetitionType
    ) -> float:
        """Get user preference for competition type"""
        collaboration_preference = user_profile.get('collaboration_preference', 0.5)
        
        if competition_type in [CompetitionType.TEAM_TOURNAMENT, CompetitionType.COLLABORATIVE_PROJECT]:
            return collaboration_preference
        elif competition_type in [CompetitionType.INDIVIDUAL_CHALLENGE, CompetitionType.SKILL_CONTEST]:
            return 1 - collaboration_preference
        else:
            return 0.7  # Neutral preference for other types
    
    def _is_similar_competition_type(self, comp_id: str, competition_type: CompetitionType) -> bool:
        """Check if a competition ID represents similar type"""
        # Simplified implementation - would query actual competition data
        return False
    
    async def _update_user_participations(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Update user's active competition participations"""
        updates = []
        
        for comp_id, competition in self.active_competitions.items():
            if user_id not in competition.current_participants:
                continue
            
            if competition.status != CompetitionStatus.ACTIVE:
                continue
            
            # Update user's competition progress
            progress_update = await self._calculate_competition_progress(
                user_id, competition, activity_data
            )
            
            if progress_update:
                updates.append({
                    'competition_id': comp_id,
                    'title': competition.title,
                    'progress': progress_update,
                    'leaderboard_position': self._get_user_leaderboard_position(user_id, competition)
                })
        
        return updates
    
    async def _calculate_competition_progress(
        self,
        user_id: str,
        competition: SocialCompetition,
        activity_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Calculate user's progress in a competition"""
        if competition.competition_type == CompetitionType.INDIVIDUAL_CHALLENGE:
            # Progress based on content creation metrics
            content_score = activity_data.get('content_quality_score', 0)
            engagement_score = activity_data.get('engagement_score', 0)
            overall_score = (content_score * 0.6 + engagement_score * 0.4) * 100
            
            return {
                'overall_score': overall_score,
                'content_quality': content_score,
                'engagement': engagement_score,
                'rank_change': 0  # Would calculate actual rank change
            }
        
        elif competition.competition_type == CompetitionType.COLLABORATION_PROJECT:
            # Progress based on collaboration metrics
            collaboration_count = activity_data.get('collaborations_in_period', 0)
            collaboration_quality = activity_data.get('collaboration_avg_rating', 0)
            team_score = collaboration_count * collaboration_quality * 20
            
            return {
                'team_score': team_score,
                'collaborations_completed': collaboration_count,
                'average_rating': collaboration_quality
            }
        
        return None
    
    def _get_user_leaderboard_position(
        self,
        user_id: str,
        competition: SocialCompetition
    ) -> int:
        """Get user's current position in competition leaderboard"""
        for i, entry in enumerate(competition.leaderboard):
            if entry.get('user_id') == user_id:
                return i + 1
        return len(competition.leaderboard) + 1
    
    async def _generate_competition_insights(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate competition-related insights for user"""
        insights = {
            'competitive_strength': self._analyze_competitive_strength(user_id, activity_data),
            'improvement_areas': self._identify_competition_improvement_areas(activity_data),
            'recommended_strategies': self._generate_competition_strategies(user_id, activity_data),
            'upcoming_opportunities': await self._identify_upcoming_opportunities(user_id)
        }
        
        return insights
    
    def _analyze_competitive_strength(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user's competitive strengths"""
        strengths = {}
        
        # Content creation strength
        content_quality = activity_data.get('avg_content_rating', 2.5)
        content_frequency = activity_data.get('uploads_per_week', 0)
        strengths['content_creation'] = (content_quality / 5.0 + min(1.0, content_frequency / 5)) / 2
        
        # Collaboration strength
        collaboration_success = activity_data.get('collaboration_success_rate', 0.5)
        collaboration_frequency = activity_data.get('collaborations_per_month', 0)
        strengths['collaboration'] = (collaboration_success + min(1.0, collaboration_frequency / 5)) / 2
        
        # Engagement strength
        engagement_rate = activity_data.get('engagement_rate', 0.5)
        social_score = activity_data.get('social_engagement_score', 0.5)
        strengths['engagement'] = (engagement_rate + social_score) / 2
        
        # Overall competitive rating
        overall_rating = sum(strengths.values()) / len(strengths)
        
        return {
            'content_creation': strengths['content_creation'],
            'collaboration': strengths['collaboration'],
            'engagement': strengths['engagement'],
            'overall_rating': overall_rating,
            'competitive_tier': self._determine_competitive_tier(overall_rating)
        }
    
    def _determine_competitive_tier(self, rating: float) -> str:
        """Determine competitive tier based on rating"""
        if rating >= 0.8:
            return 'champion'
        elif rating >= 0.6:
            return 'competitor'
        elif rating >= 0.4:
            return 'challenger'
        else:
            return 'novice'
    
    def _identify_competition_improvement_areas(
        self,
        activity_data: Dict[str, Any]
    ) -> List[str]:
        """Identify areas for competition improvement"""
        improvements = []
        
        if activity_data.get('avg_content_rating', 2.5) < 4.0:
            improvements.append("Content quality consistency")
        
        if activity_data.get('engagement_rate', 0.5) < 0.6:
            improvements.append("Audience engagement strategies")
        
        if activity_data.get('collaboration_success_rate', 0.5) < 0.7:
            improvements.append("Collaboration effectiveness")
        
        if activity_data.get('uploads_per_week', 0) < 3:
            improvements.append("Content creation frequency")
        
        return improvements
    
    def _generate_competition_strategies(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized competition strategies"""
        strategies = []
        
        # Based on competitive strengths
        content_strength = activity_data.get('avg_content_rating', 2.5) / 5.0
        collaboration_strength = activity_data.get('collaboration_success_rate', 0.5)
        
        if content_strength > 0.7:
            strategies.append("Focus on individual challenges to leverage content quality")
        
        if collaboration_strength > 0.7:
            strategies.append("Participate in team tournaments to maximize collaboration skills")
        
        if content_strength > 0.6 and collaboration_strength > 0.6:
            strategies.append("Consider mixed-format competitions for balanced growth")
        
        # General strategies
        strategies.extend([
            "Study successful competitors' strategies",
            "Build consistent practice routines",
            "Network with other active competitors"
        ])
        
        return strategies[:4]  # Return top 4 strategies
    
    async def _identify_upcoming_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        """Identify upcoming competition opportunities"""
        opportunities = []
        
        # Look for competitions starting soon
        upcoming_competitions = [
            comp for comp in self.active_competitions.values()
            if comp.status == CompetitionStatus.REGISTRATION_OPEN
            and comp.start_date > datetime.now(timezone.utc)
            and (comp.start_date - datetime.now(timezone.utc)).days <= 7
        ]
        
        for competition in upcoming_competitions[:3]:
            opportunities.append({
                'competition_id': competition.competition_id,
                'title': competition.title,
                'type': competition.competition_type.value,
                'start_date': competition.start_date.isoformat(),
                'registration_deadline': (competition.start_date - timedelta(days=1)).isoformat(),
                'potential_rewards': competition.rewards
            })
        
        return opportunities
    
    async def _get_available_competitions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all available competitions for user"""
        available = []
        
        for comp_id, competition in self.active_competitions.items():
            if competition.status in [CompetitionStatus.REGISTRATION_OPEN, CompetitionStatus.ACTIVE]:
                available.append({
                    'competition_id': comp_id,
                    'title': competition.title,
                    'type': competition.competition_type.value,
                    'status': competition.status.value,
                    'participants': len(competition.current_participants),
                    'max_participants': competition.max_participants,
                    'is_participating': user_id in competition.current_participants,
                    'end_date': competition.end_date.isoformat() if competition.end_date else None
                })
        
        return available
    
    async def _update_user_competition_activity(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ):
        """Update user's competition activity tracking"""
        if user_id not in self.user_competition_history:
            self.user_competition_history[user_id] = []
        
        # Update participation in active competitions
        for comp_id, competition in self.active_competitions.items():
            if user_id in competition.current_participants:
                # Update leaderboard if needed
                await self._update_competition_leaderboard(comp_id, user_id, activity_data)
    
    async def _update_competition_leaderboard(
        self,
        competition_id: str,
        user_id: str,
        activity_data: Dict[str, Any]
    ):
        """Update competition leaderboard with user's latest performance"""
        competition = self.active_competitions.get(competition_id)
        if not competition:
            return
        
        # Calculate user's current score
        user_score = await self._calculate_user_competition_score(
            user_id, competition, activity_data
        )
        
        # Update leaderboard
        user_entry = None
        for entry in competition.leaderboard:
            if entry['user_id'] == user_id:
                user_entry = entry
                break
        
        if user_entry:
            user_entry['score'] = user_score
            user_entry['last_updated'] = datetime.now(timezone.utc).isoformat()
        else:
            competition.leaderboard.append({
                'user_id': user_id,
                'score': user_score,
                'last_updated': datetime.now(timezone.utc).isoformat()
            })
        
        # Sort leaderboard
        competition.leaderboard.sort(key=lambda x: x['score'], reverse=True)
    
    async def _calculate_user_competition_score(
        self,
        user_id: str,
        competition: SocialCompetition,
        activity_data: Dict[str, Any]
    ) -> float:
        """Calculate user's score in a specific competition"""
        if competition.competition_type == CompetitionType.INDIVIDUAL_CHALLENGE:
            content_score = activity_data.get('content_quality_score', 0.5)
            engagement_score = activity_data.get('engagement_score', 0.5)
            return (content_score * 0.6 + engagement_score * 0.4) * 1000
        
        elif competition.competition_type == CompetitionType.COLLABORATION_PROJECT:
            collaboration_score = activity_data.get('collaboration_success_rate', 0.5)
            team_contribution = activity_data.get('team_contribution_score', 0.5)
            return (collaboration_score * 0.7 + team_contribution * 0.3) * 1000
        
        elif competition.competition_type == CompetitionType.SKILL_CONTEST:
            skill_demonstration = activity_data.get('skill_demonstration_score', 0.5)
            innovation_factor = activity_data.get('innovation_factor', 0.5)
            return (skill_demonstration * 0.8 + innovation_factor * 0.2) * 1000
        
        return activity_data.get('overall_performance_score', 0.5) * 1000
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide competition analytics"""
        total_competitions = len(self.active_competitions)
        total_participants = sum(
            len(comp.current_participants) for comp in self.active_competitions.values()
        )
        
        active_competitions = sum(
            1 for comp in self.active_competitions.values()
            if comp.status == CompetitionStatus.ACTIVE
        )
        
        return {
            'total_competitions': total_competitions,
            'active_competitions': active_competitions,
            'total_participants': total_participants,
            'average_participants_per_competition': (
                total_participants / total_competitions if total_competitions > 0 else 0
            ),
            'competition_types_distribution': self._get_competition_type_distribution(),
            'system_status': 'operational',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_competition_type_distribution(self) -> Dict[str, int]:
        """Get distribution of competition types"""
        distribution = {}
        for competition in self.active_competitions.values():
            comp_type = competition.competition_type.value
            distribution[comp_type] = distribution.get(comp_type, 0) + 1
        return distribution

# Export classes
__all__ = [
    'SocialCompetitionManager',
    'CompetitionConfig',
    'SocialCompetition',
    'CompetitionType',
    'CompetitionStatus'
]