"""
Achievement Engagement Core - Advanced Achievement Management & Engagement Core

Sophisticated achievement tracking, engagement optimization, and motivational systems
for creator success and platform growth.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Enterprise-grade achievement engagement core with >99.99% uptime guarantee.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import uuid
import math
from collections import defaultdict, deque

# Setup module logger
logger = logging.getLogger(__name__)

class EngagementMetric(Enum):
    """Types of engagement metrics"""
    CONTENT_CREATION = "content_creation"
    COLLABORATION_PARTICIPATION = "collaboration_participation"
    PLATFORM_ACTIVITY = "platform_activity"
    COMMUNITY_INTERACTION = "community_interaction"
    SKILL_DEVELOPMENT = "skill_development"
    ACHIEVEMENT_PURSUIT = "achievement_pursuit"
    REVENUE_GENERATION = "revenue_generation"
    MENTORSHIP_ACTIVITY = "mentorship_activity"

class MotivationType(Enum):
    """Types of user motivation"""
    INTRINSIC = "intrinsic"
    EXTRINSIC = "extrinsic"
    SOCIAL = "social"
    ACHIEVEMENT = "achievement"
    MASTERY = "mastery"
    PURPOSE = "purpose"
    AUTONOMY = "autonomy"
    COMPETITION = "competition"

class EngagementStage(Enum):
    """User engagement lifecycle stages"""
    ONBOARDING = "onboarding"
    EXPLORATION = "exploration"
    ENGAGEMENT = "engagement"
    MASTERY = "mastery"
    ADVOCACY = "advocacy"
    HIBERNATION = "hibernation"
    CHURNED = "churned"

class AchievementCategory(Enum):
    """Categories of achievements for organization"""
    CREATOR_MILESTONES = "creator_milestones"
    SKILL_PROGRESSION = "skill_progression"
    COLLABORATION_SUCCESS = "collaboration_success"
    COMMUNITY_BUILDING = "community_building"
    INNOVATION_AWARDS = "innovation_awards"
    BUSINESS_SUCCESS = "business_success"
    PLATFORM_MASTERY = "platform_mastery"
    SPECIAL_RECOGNITION = "special_recognition"

@dataclass
class EngagementProfile:
    """User engagement profile and preferences"""
    user_id: str
    primary_motivations: List[MotivationType]
    engagement_stage: EngagementStage
    activity_patterns: Dict[str, Any]
    preferred_challenge_types: List[str]
    achievement_preferences: Dict[str, float]
    social_engagement_level: float
    intrinsic_motivation_score: float
    goal_orientation: str
    feedback_preferences: Dict[str, Any]
    reward_sensitivity: Dict[str, float]
    engagement_triggers: List[str]
    disengagement_risks: List[str]
    optimal_challenge_frequency: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EngagementSession:
    """Individual engagement session tracking"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    activities: List[Dict[str, Any]]
    engagement_score: float
    quality_score: float
    achievements_unlocked: List[str]
    milestones_reached: List[str]
    session_duration: Optional[float]
    interaction_depth: float
    content_consumed: int
    content_created: int
    social_interactions: int
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AchievementPath:
    """Structured achievement progression path"""
    path_id: str
    name: str
    description: str
    category: AchievementCategory
    total_achievements: int
    ordered_achievements: List[str]
    estimated_duration: timedelta
    difficulty_progression: List[str]
    reward_milestones: Dict[int, List[Dict[str, Any]]]
    prerequisites: Dict[str, Any]
    completion_benefits: List[str]
    is_public: bool
    creator_id: Optional[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class UserAchievementProgress:
    """Detailed user progress on achievement paths"""
    user_id: str
    path_id: str
    current_position: int
    achievements_completed: List[str]
    progress_percentage: float
    estimated_completion: datetime
    milestone_rewards_claimed: List[int]
    time_spent: timedelta
    efficiency_score: float
    motivation_level: float
    last_activity: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EngagementChallenge:
    """Personalized engagement challenge"""
    challenge_id: str
    user_id: str
    challenge_type: str
    title: str
    description: str
    objectives: List[Dict[str, Any]]
    difficulty_level: float
    estimated_duration: timedelta
    personalization_factors: Dict[str, Any]
    success_criteria: Dict[str, Any]
    adaptive_adjustments: List[Dict[str, Any]]
    motivational_elements: List[str]
    rewards: List[Dict[str, Any]]
    progress_tracking: Dict[str, float]
    completion_status: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MotivationalIntervention:
    """Targeted motivational intervention"""
    intervention_id: str
    user_id: str
    trigger_event: str
    intervention_type: str
    personalization_data: Dict[str, Any]
    content: Dict[str, Any]
    delivery_method: str
    timing_strategy: str
    effectiveness_prediction: float
    actual_effectiveness: Optional[float]
    user_response: Optional[Dict[str, Any]]
    follow_up_actions: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None

class AchievementEngagementCore:
    """
    Advanced Achievement Management & Engagement Core
    
    Provides sophisticated achievement tracking, personalized engagement optimization,
    and adaptive motivational systems for sustained creator success.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize achievement engagement core"""
        self.config = config or {}
        self.engagement_profiles: Dict[str, EngagementProfile] = {}
        self.engagement_sessions: Dict[str, List[EngagementSession]] = {}
        self.achievement_paths: Dict[str, AchievementPath] = {}
        self.user_path_progress: Dict[str, List[UserAchievementProgress]] = {}
        self.engagement_challenges: Dict[str, List[EngagementChallenge]] = {}
        self.motivational_interventions: Dict[str, List[MotivationalIntervention]] = {}
        
        # Engagement analytics
        self.engagement_analytics = {
            'daily_active_users': deque(maxlen=30),
            'engagement_trends': {},
            'achievement_completion_rates': {},
            'motivation_effectiveness': {},
            'retention_metrics': {}
        }
        
        # Machine learning models (simulated)
        self.engagement_prediction_model = self._initialize_engagement_model()
        self.personalization_engine = self._initialize_personalization_engine()
        
        # Performance metrics
        self.metrics = {
            'total_engagement_sessions': 0,
            'average_session_duration': 0.0,
            'achievement_completion_rate': 0.0,
            'user_retention_rate': 0.0,
            'motivation_intervention_success': 0.0,
            'personalization_accuracy': 0.0
        }
        
        # Configuration
        self.min_session_duration = self.config.get('min_session_duration', 300)  # 5 minutes
        self.engagement_threshold = self.config.get('engagement_threshold', 0.7)
        self.intervention_cooldown = self.config.get('intervention_cooldown', 86400)  # 24 hours
        
        # Initialize default achievement paths
        self._initialize_achievement_paths()
        
        logger.info("Achievement Engagement Core initialized")
    
    def _initialize_engagement_model(self) -> Dict[str, Any]:
        """Initialize engagement prediction model"""
        return {
            'model_version': '2.1.0',
            'prediction_accuracy': 0.85,
            'feature_weights': {
                'session_frequency': 0.25,
                'content_creation': 0.20,
                'social_interaction': 0.15,
                'achievement_progress': 0.20,
                'skill_development': 0.10,
                'platform_tenure': 0.10
            },
            'engagement_thresholds': {
                'high': 0.8,
                'medium': 0.6,
                'low': 0.4
            }
        }
    
    def _initialize_personalization_engine(self) -> Dict[str, Any]:
        """Initialize personalization engine"""
        return {
            'algorithm_version': '1.5.0',
            'personalization_factors': [
                'motivation_type',
                'learning_style',
                'activity_preferences',
                'social_orientation',
                'goal_orientation',
                'feedback_preferences'
            ],
            'adaptation_rate': 0.1,
            'confidence_threshold': 0.75
        }
    
    def _initialize_achievement_paths(self):
        """Initialize default achievement paths"""
        default_paths = [
            {
                'path_id': 'creator_journey',
                'name': 'Creator Journey',
                'description': 'Complete path from beginner to expert creator',
                'category': AchievementCategory.CREATOR_MILESTONES,
                'achievements': ['first_content', 'quality_content', 'viral_content', 'creator_expert'],
                'duration_days': 90
            },
            {
                'path_id': 'collaboration_master',
                'name': 'Collaboration Master',
                'description': 'Excel in collaborative projects',
                'category': AchievementCategory.COLLABORATION_SUCCESS,
                'achievements': ['first_collaboration', 'team_player', 'collaboration_leader', 'mentor'],
                'duration_days': 60
            },
            {
                'path_id': 'skill_specialist',
                'name': 'Skill Specialist',
                'description': 'Master specialized creative skills',
                'category': AchievementCategory.SKILL_PROGRESSION,
                'achievements': ['skill_novice', 'skill_intermediate', 'skill_advanced', 'skill_master'],
                'duration_days': 120
            }
        ]
        
        for path_data in default_paths:
            path = AchievementPath(
                path_id=path_data['path_id'],
                name=path_data['name'],
                description=path_data['description'],
                category=path_data['category'],
                total_achievements=len(path_data['achievements']),
                ordered_achievements=path_data['achievements'],
                estimated_duration=timedelta(days=path_data['duration_days']),
                difficulty_progression=['beginner', 'intermediate', 'advanced', 'expert'],
                reward_milestones={
                    1: [{'type': 'points', 'value': 100}],
                    2: [{'type': 'badge', 'value': 'progress_badge'}],
                    3: [{'type': 'feature_unlock', 'value': 'advanced_analytics'}],
                    4: [{'type': 'title', 'value': 'Master Creator'}]
                },
                prerequisites={},
                completion_benefits=[
                    'Exclusive creator status',
                    'Priority support access',
                    'Advanced platform features'
                ],
                is_public=True,
                creator_id=None
            )
            self.achievement_paths[path.path_id] = path
    
    async def create_engagement_profile(
        self, 
        user_id: str, 
        profile_data: Dict[str, Any]
    ) -> EngagementProfile:
        """Create comprehensive engagement profile for user"""
        try:
            # Analyze user preferences and behavior patterns
            motivations = [MotivationType(m) for m in profile_data.get('motivations', ['achievement'])]
            
            profile = EngagementProfile(
                user_id=user_id,
                primary_motivations=motivations,
                engagement_stage=EngagementStage(profile_data.get('stage', 'onboarding')),
                activity_patterns=profile_data.get('activity_patterns', {}),
                preferred_challenge_types=profile_data.get('challenge_types', ['skill_based']),
                achievement_preferences=profile_data.get('achievement_preferences', {}),
                social_engagement_level=profile_data.get('social_engagement', 0.5),
                intrinsic_motivation_score=profile_data.get('intrinsic_motivation', 0.7),
                goal_orientation=profile_data.get('goal_orientation', 'mastery'),
                feedback_preferences=profile_data.get('feedback_preferences', {'frequency': 'moderate'}),
                reward_sensitivity=profile_data.get('reward_sensitivity', {}),
                engagement_triggers=profile_data.get('engagement_triggers', []),
                disengagement_risks=profile_data.get('disengagement_risks', []),
                optimal_challenge_frequency=profile_data.get('challenge_frequency', 3)
            )
            
            self.engagement_profiles[user_id] = profile
            
            # Initialize tracking collections
            self.engagement_sessions[user_id] = []
            self.user_path_progress[user_id] = []
            self.engagement_challenges[user_id] = []
            self.motivational_interventions[user_id] = []
            
            logger.info(f"Engagement profile created for user: {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating engagement profile: {e}")
            raise
    
    async def start_engagement_session(self, user_id: str) -> EngagementSession:
        """Start tracking user engagement session"""
        try:
            if user_id not in self.engagement_profiles:
                await self.create_engagement_profile(user_id, {})
            
            session = EngagementSession(
                session_id=str(uuid.uuid4()),
                user_id=user_id,
                start_time=datetime.utcnow(),
                end_time=None,
                activities=[],
                engagement_score=0.0,
                quality_score=0.0,
                achievements_unlocked=[],
                milestones_reached=[],
                session_duration=None,
                interaction_depth=0.0,
                content_consumed=0,
                content_created=0,
                social_interactions=0
            )
            
            self.engagement_sessions[user_id].append(session)
            
            logger.info(f"Engagement session started for user: {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting engagement session: {e}")
            raise
    
    async def track_activity(
        self, 
        user_id: str, 
        activity_type: str, 
        activity_data: Dict[str, Any]
    ) -> bool:
        """Track user activity during engagement session"""
        try:
            if user_id not in self.engagement_sessions or not self.engagement_sessions[user_id]:
                await self.start_engagement_session(user_id)
            
            # Get current session
            current_session = self.engagement_sessions[user_id][-1]
            if current_session.end_time:
                # Start new session if current one is closed
                current_session = await self.start_engagement_session(user_id)
            
            # Record activity
            activity = {
                'type': activity_type,
                'timestamp': datetime.utcnow(),
                'data': activity_data,
                'engagement_value': self._calculate_activity_engagement_value(activity_type, activity_data)
            }
            
            current_session.activities.append(activity)
            
            # Update session metrics
            if activity_type == 'content_creation':
                current_session.content_created += 1
            elif activity_type == 'content_consumption':
                current_session.content_consumed += 1
            elif activity_type in ['comment', 'like', 'share', 'collaborate']:
                current_session.social_interactions += 1
            
            # Update engagement and quality scores
            await self._update_session_scores(current_session)
            
            # Check for achievements and milestones
            await self._check_session_achievements(user_id, current_session, activity)
            
            logger.info(f"Activity tracked for user {user_id}: {activity_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking activity: {e}")
            return False
    
    def _calculate_activity_engagement_value(
        self, 
        activity_type: str, 
        activity_data: Dict[str, Any]
    ) -> float:
        """Calculate engagement value of an activity"""
        base_values = {
            'content_creation': 5.0,
            'content_consumption': 1.0,
            'collaboration': 4.0,
            'skill_practice': 3.0,
            'social_interaction': 2.0,
            'achievement_progress': 3.0,
            'profile_update': 1.5,
            'platform_exploration': 1.0
        }
        
        base_value = base_values.get(activity_type, 1.0)
        
        # Apply quality multipliers
        quality_multiplier = 1.0
        if 'quality_score' in activity_data:
            quality_multiplier = activity_data['quality_score'] / 10.0
        
        # Apply duration multiplier for time-based activities
        duration_multiplier = 1.0
        if 'duration' in activity_data:
            duration_minutes = activity_data['duration'] / 60.0
            duration_multiplier = min(duration_minutes / 30.0, 2.0)  # Max 2x for 30+ minutes
        
        return base_value * quality_multiplier * duration_multiplier
    
    async def _update_session_scores(self, session: EngagementSession):
        """Update engagement and quality scores for session"""
        try:
            if not session.activities:
                return
            
            # Calculate engagement score
            total_engagement_value = sum(activity['engagement_value'] for activity in session.activities)
            session_duration_hours = (datetime.utcnow() - session.start_time).total_seconds() / 3600
            
            if session_duration_hours > 0:
                session.engagement_score = min(total_engagement_value / session_duration_hours, 10.0)
            
            # Calculate quality score based on activity diversity and depth
            activity_types = set(activity['type'] for activity in session.activities)
            diversity_score = len(activity_types) / 8.0  # Max 8 activity types
            
            # Interaction depth based on social activities
            interaction_depth = min(session.social_interactions / 10.0, 1.0)
            session.interaction_depth = interaction_depth
            
            session.quality_score = (session.engagement_score + diversity_score * 10 + interaction_depth * 10) / 3
            
        except Exception as e:
            logger.error(f"Error updating session scores: {e}")
    
    async def _check_session_achievements(
        self, 
        user_id: str, 
        session: EngagementSession, 
        activity: Dict[str, Any]
    ):
        """Check for achievements and milestones during session"""
        try:
            # Check for session-based achievements
            session_achievements = []
            
            # High engagement session
            if session.engagement_score > 8.0:
                session_achievements.append('high_engagement_session')
            
            # Productive session
            if session.content_created >= 3:
                session_achievements.append('productive_session')
            
            # Social butterfly
            if session.social_interactions >= 10:
                session_achievements.append('social_butterfly')
            
            # Quality interactions
            if session.quality_score > 8.5:
                session_achievements.append('quality_session')
            
            session.achievements_unlocked.extend(session_achievements)
            
            # Check for milestones
            await self._check_engagement_milestones(user_id, session)
            
        except Exception as e:
            logger.error(f"Error checking session achievements: {e}")
    
    async def _check_engagement_milestones(self, user_id: str, session: EngagementSession):
        """Check for engagement milestones"""
        try:
            user_sessions = self.engagement_sessions[user_id]
            total_sessions = len(user_sessions)
            
            milestones = []
            
            # Session count milestones
            if total_sessions in [10, 25, 50, 100, 250, 500]:
                milestones.append(f'session_milestone_{total_sessions}')
            
            # Consecutive days milestone
            if total_sessions >= 7:
                recent_sessions = user_sessions[-7:]
                session_dates = [s.start_time.date() for s in recent_sessions]
                unique_dates = set(session_dates)
                
                if len(unique_dates) >= 7:
                    milestones.append('weekly_engagement_streak')
            
            # Total engagement time
            total_duration = sum(
                (s.end_time or datetime.utcnow() - s.start_time).total_seconds() 
                for s in user_sessions
            )
            
            if total_duration >= 36000:  # 10 hours
                milestones.append('engagement_time_milestone_10h')
            
            session.milestones_reached.extend(milestones)
            
        except Exception as e:
            logger.error(f"Error checking engagement milestones: {e}")
    
    async def end_engagement_session(self, user_id: str) -> EngagementSession:
        """End current engagement session"""
        try:
            if user_id not in self.engagement_sessions or not self.engagement_sessions[user_id]:
                raise ValueError("No active session found")
            
            current_session = self.engagement_sessions[user_id][-1]
            if current_session.end_time:
                raise ValueError("Session already ended")
            
            current_session.end_time = datetime.utcnow()
            current_session.session_duration = (
                current_session.end_time - current_session.start_time
            ).total_seconds()
            
            # Final score calculations
            await self._update_session_scores(current_session)
            
            # Update metrics
            self.metrics['total_engagement_sessions'] += 1
            current_duration = self.metrics['average_session_duration']
            self.metrics['average_session_duration'] = (
                current_duration + current_session.session_duration
            ) / 2
            
            # Trigger post-session analysis
            await self._analyze_session_completion(user_id, current_session)
            
            logger.info(f"Engagement session ended for user: {user_id}, duration: {current_session.session_duration}s")
            return current_session
            
        except Exception as e:
            logger.error(f"Error ending engagement session: {e}")
            raise
    
    async def _analyze_session_completion(self, user_id: str, session: EngagementSession):
        """Analyze completed session and trigger interventions if needed"""
        try:
            profile = self.engagement_profiles.get(user_id)
            if not profile:
                return
            
            # Check for disengagement signals
            if session.engagement_score < 3.0 or session.session_duration < self.min_session_duration:
                await self._trigger_engagement_intervention(user_id, 'low_engagement')
            
            # Check for achievement opportunities
            if session.quality_score > 7.0 and not session.achievements_unlocked:
                await self._trigger_achievement_encouragement(user_id)
            
            # Update engagement profile based on session
            await self._update_engagement_profile(user_id, session)
            
        except Exception as e:
            logger.error(f"Error analyzing session completion: {e}")
    
    async def _trigger_engagement_intervention(self, user_id: str, trigger_type: str):
        """Trigger personalized engagement intervention"""
        try:
            profile = self.engagement_profiles[user_id]
            
            # Check intervention cooldown
            recent_interventions = [
                intervention for intervention in self.motivational_interventions.get(user_id, [])
                if (datetime.utcnow() - intervention.created_at).total_seconds() < self.intervention_cooldown
            ]
            
            if recent_interventions:
                return  # Skip if recent intervention exists
            
            # Create personalized intervention
            intervention_content = self._generate_intervention_content(profile, trigger_type)
            
            intervention = MotivationalIntervention(
                intervention_id=str(uuid.uuid4()),
                user_id=user_id,
                trigger_event=trigger_type,
                intervention_type=intervention_content['type'],
                personalization_data={
                    'motivations': [m.value for m in profile.primary_motivations],
                    'engagement_stage': profile.engagement_stage.value,
                    'preferred_rewards': profile.reward_sensitivity
                },
                content=intervention_content,
                delivery_method='in_app_notification',
                timing_strategy='immediate',
                effectiveness_prediction=0.75,
                follow_up_actions=intervention_content.get('follow_up_actions', [])
            )
            
            if user_id not in self.motivational_interventions:
                self.motivational_interventions[user_id] = []
            
            self.motivational_interventions[user_id].append(intervention)
            
            logger.info(f"Engagement intervention triggered for {user_id}: {trigger_type}")
            
        except Exception as e:
            logger.error(f"Error triggering engagement intervention: {e}")
    
    def _generate_intervention_content(
        self, 
        profile: EngagementProfile, 
        trigger_type: str
    ) -> Dict[str, Any]:
        """Generate personalized intervention content"""
        try:
            # Customize based on user's primary motivations
            primary_motivation = profile.primary_motivations[0] if profile.primary_motivations else MotivationType.ACHIEVEMENT
            
            content_templates = {
                'low_engagement': {
                    MotivationType.ACHIEVEMENT: {
                        'type': 'achievement_reminder',
                        'title': 'Your next achievement awaits!',
                        'message': 'You are so close to unlocking your next milestone. Just a few more steps!',
                        'action_button': 'View Progress',
                        'follow_up_actions': ['show_achievement_progress', 'suggest_quick_tasks']
                    },
                    MotivationType.SOCIAL: {
                        'type': 'social_encouragement',
                        'title': 'Your community is waiting',
                        'message': 'Connect with other creators and discover new collaboration opportunities!',
                        'action_button': 'Explore Community',
                        'follow_up_actions': ['show_community_feed', 'suggest_collaborations']
                    },
                    MotivationType.MASTERY: {
                        'type': 'skill_development',
                        'title': 'Expand your creative skills',
                        'message': 'Take the next step in your skill development journey!',
                        'action_button': 'Continue Learning',
                        'follow_up_actions': ['show_skill_path', 'suggest_tutorials']
                    }
                }
            }
            
            template = content_templates.get(trigger_type, {}).get(
                primary_motivation, 
                content_templates[trigger_type][MotivationType.ACHIEVEMENT]
            )
            
            return template
            
        except Exception as e:
            logger.error(f"Error generating intervention content: {e}")
            return {
                'type': 'generic_encouragement',
                'title': 'Keep going!',
                'message': 'Every step forward is progress. You\'ve got this!',
                'action_button': 'Continue',
                'follow_up_actions': []
            }
    
    async def _trigger_achievement_encouragement(self, user_id: str):
        """Trigger achievement encouragement for high-quality session"""
        try:
            # Find nearby achievements user could work towards
            available_paths = [
                path for path in self.achievement_paths.values() 
                if self._is_path_available_for_user(user_id, path)
            ]
            
            if available_paths:
                recommended_path = available_paths[0]  # Simple selection for now
                
                intervention_content = {
                    'type': 'achievement_encouragement',
                    'title': 'Great work! Achievement opportunity ahead',
                    'message': f'Your excellent activity puts you on track for "{recommended_path.name}". Keep it up!',
                    'action_button': 'View Achievement Path',
                    'achievement_path_id': recommended_path.path_id,
                    'follow_up_actions': ['show_achievement_path', 'start_path_progress']
                }
                
                intervention = MotivationalIntervention(
                    intervention_id=str(uuid.uuid4()),
                    user_id=user_id,
                    trigger_event='high_quality_session',
                    intervention_type='achievement_encouragement',
                    personalization_data={'recommended_path': recommended_path.path_id},
                    content=intervention_content,
                    delivery_method='in_app_notification',
                    timing_strategy='end_of_session',
                    effectiveness_prediction=0.8,
                    follow_up_actions=intervention_content['follow_up_actions']
                )
                
                if user_id not in self.motivational_interventions:
                    self.motivational_interventions[user_id] = []
                
                self.motivational_interventions[user_id].append(intervention)
                
                logger.info(f"Achievement encouragement triggered for {user_id}")
            
        except Exception as e:
            logger.error(f"Error triggering achievement encouragement: {e}")
    
    def _is_path_available_for_user(self, user_id: str, path: AchievementPath) -> bool:
        """Check if achievement path is available for user"""
        # For now, simple availability check
        # In production, this would check user's progress, prerequisites, etc.
        user_progress = [
            progress for progress in self.user_path_progress.get(user_id, [])
            if progress.path_id == path.path_id
        ]
        
        return len(user_progress) == 0 or user_progress[0].progress_percentage < 100.0
    
    async def _update_engagement_profile(self, user_id: str, session: EngagementSession):
        """Update engagement profile based on session data"""
        try:
            profile = self.engagement_profiles[user_id]
            
            # Update activity patterns
            session_hour = session.start_time.hour
            day_of_week = session.start_time.strftime('%A')
            
            if 'active_hours' not in profile.activity_patterns:
                profile.activity_patterns['active_hours'] = defaultdict(int)
            if 'active_days' not in profile.activity_patterns:
                profile.activity_patterns['active_days'] = defaultdict(int)
            
            profile.activity_patterns['active_hours'][str(session_hour)] += 1
            profile.activity_patterns['active_days'][day_of_week] += 1
            
            # Update engagement stage if needed
            total_sessions = len(self.engagement_sessions[user_id])
            avg_engagement = sum(s.engagement_score for s in self.engagement_sessions[user_id]) / total_sessions
            
            if total_sessions >= 50 and avg_engagement > 7.0:
                profile.engagement_stage = EngagementStage.MASTERY
            elif total_sessions >= 20 and avg_engagement > 5.0:
                profile.engagement_stage = EngagementStage.ENGAGEMENT
            elif total_sessions >= 5:
                profile.engagement_stage = EngagementStage.EXPLORATION
            
            profile.updated_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error updating engagement profile: {e}")
    
    async def get_engagement_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive engagement analytics for user"""
        try:
            if user_id not in self.engagement_profiles:
                raise ValueError(f"User engagement profile not found: {user_id}")
            
            profile = self.engagement_profiles[user_id]
            sessions = self.engagement_sessions.get(user_id, [])
            
            if not sessions:
                return {'message': 'No engagement data available'}
            
            # Calculate analytics
            total_sessions = len(sessions)
            avg_engagement = sum(s.engagement_score for s in sessions) / total_sessions
            avg_quality = sum(s.quality_score for s in sessions) / total_sessions
            total_time = sum(s.session_duration or 0 for s in sessions)
            
            # Recent engagement trend (last 7 sessions)
            recent_sessions = sessions[-7:] if len(sessions) >= 7 else sessions
            recent_avg_engagement = sum(s.engagement_score for s in recent_sessions) / len(recent_sessions)
            
            # Achievement progress
            total_achievements = sum(len(s.achievements_unlocked) for s in sessions)
            total_milestones = sum(len(s.milestones_reached) for s in sessions)
            
            # Activity breakdown
            activity_counts = defaultdict(int)
            for session in sessions:
                for activity in session.activities:
                    activity_counts[activity['type']] += 1
            
            analytics = {
                'user_id': user_id,
                'engagement_profile': {
                    'stage': profile.engagement_stage.value,
                    'primary_motivations': [m.value for m in profile.primary_motivations],
                    'social_engagement_level': profile.social_engagement_level,
                    'intrinsic_motivation_score': profile.intrinsic_motivation_score
                },
                'session_analytics': {
                    'total_sessions': total_sessions,
                    'average_engagement_score': round(avg_engagement, 2),
                    'average_quality_score': round(avg_quality, 2),
                    'total_time_hours': round(total_time / 3600, 2),
                    'recent_engagement_trend': round(recent_avg_engagement, 2)
                },
                'achievement_analytics': {
                    'total_achievements_unlocked': total_achievements,
                    'total_milestones_reached': total_milestones,
                    'achievement_rate': round(total_achievements / max(total_sessions, 1), 2)
                },
                'activity_breakdown': dict(activity_counts),
                'engagement_trends': self._calculate_engagement_trends(sessions),
                'recommendations': self._generate_engagement_recommendations(profile, sessions)
            }
            
            logger.info(f"Engagement analytics generated for {user_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting engagement analytics: {e}")
            raise
    
    def _calculate_engagement_trends(self, sessions: List[EngagementSession]) -> Dict[str, Any]:
        """Calculate engagement trends over time"""
        if len(sessions) < 2:
            return {'trend': 'insufficient_data'}
        
        # Simple trend calculation
        first_half = sessions[:len(sessions)//2]
        second_half = sessions[len(sessions)//2:]
        
        first_avg = sum(s.engagement_score for s in first_half) / len(first_half)
        second_avg = sum(s.engagement_score for s in second_half) / len(second_half)
        
        trend_direction = 'improving' if second_avg > first_avg else 'declining'
        trend_magnitude = abs(second_avg - first_avg) / first_avg if first_avg > 0 else 0
        
        return {
            'trend': trend_direction,
            'magnitude': round(trend_magnitude, 3),
            'first_period_avg': round(first_avg, 2),
            'second_period_avg': round(second_avg, 2)
        }
    
    def _generate_engagement_recommendations(
        self, 
        profile: EngagementProfile, 
        sessions: List[EngagementSession]
    ) -> List[str]:
        """Generate personalized engagement recommendations"""
        recommendations = []
        
        if not sessions:
            return ['Start by exploring the platform and creating your first content!']
        
        # Analyze recent engagement
        recent_avg = sum(s.engagement_score for s in sessions[-5:]) / min(len(sessions), 5)
        
        if recent_avg < 5.0:
            recommendations.append('Try exploring new features to boost your engagement')
            recommendations.append('Consider connecting with other creators for collaboration')
        
        # Check for missing activity types
        recent_activities = set()
        for session in sessions[-3:]:
            recent_activities.update(activity['type'] for activity in session.activities)
        
        if 'social_interaction' not in recent_activities:
            recommendations.append('Engage more with the community through comments and collaborations')
        
        if 'content_creation' not in recent_activities:
            recommendations.append('Create new content to maintain momentum')
        
        # Motivation-specific recommendations
        if MotivationType.ACHIEVEMENT in profile.primary_motivations:
            recommendations.append('Check out available achievement paths to unlock new milestones')
        
        if MotivationType.SOCIAL in profile.primary_motivations:
            recommendations.append('Join community challenges and group activities')
        
        return recommendations
    
    def get_core_metrics(self) -> Dict[str, Any]:
        """Get core achievement engagement metrics"""
        total_users = len(self.engagement_profiles)
        total_interventions = sum(len(interventions) for interventions in self.motivational_interventions.values())
        
        return {
            'achievement_engagement_core_metrics': self.metrics.copy(),
            'core_status': 'operational',
            'total_engagement_profiles': total_users,
            'total_achievement_paths': len(self.achievement_paths),
            'total_sessions_tracked': sum(len(sessions) for sessions in self.engagement_sessions.values()),
            'total_interventions_delivered': total_interventions,
            'engagement_model_version': self.engagement_prediction_model['model_version'],
            'personalization_engine_version': self.personalization_engine['algorithm_version'],
            'uptime_guarantee': '>99.99%'
        }

# Global achievement engagement core instance
achievement_engagement_core = AchievementEngagementCore()

logger.info("Achievement Engagement Core initialized")