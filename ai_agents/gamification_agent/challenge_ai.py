"""Challenge AI - Intelligent Challenge Generation and Management System

Advanced AI system for creating personalized challenges, managing challenge lifecycles,
and optimizing challenge difficulty and engagement for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This challenge generation AI and algorithms are the exclusive intellectual property of Fahed Mlaiel.
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
import random
import uuid

logger = logging.getLogger(__name__)

class ChallengeType(Enum):
    """Types of challenges available"""    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    MILESTONE = "milestone"
    SOCIAL = "social"
    SKILL_BASED = "skill_based"
    CREATIVE = "creative"

class ChallengeDifficulty(Enum):
    """Challenge difficulty levels"""    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

class ChallengeStatus(Enum):
    """Challenge status tracking"""    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

@dataclass
class ChallengeConfig:
    """Configuration for challenge generation"""    max_active_challenges_per_user: int = 5
    daily_challenge_count: int = 3
    weekly_challenge_count: int = 2
    monthly_challenge_count: int = 1
    difficulty_adaptation_enabled: bool = True
    personalization_enabled: bool = True
    social_challenges_enabled: bool = True
    ai_optimization_enabled: bool = True
    challenge_expiry_hours: int = 168  # 1 week default

@dataclass
class ChallengeTemplate:
    """Template for challenge creation"""    template_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    category: str
    target_metric: str
    target_value: float
    reward_points: int
    duration_hours: int
    prerequisites: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PersonalizedChallenge:
    """Personalized challenge instance"""    challenge_id: str
    user_id: str
    template_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    target_metric: str
    target_value: float
    current_progress: float = 0.0
    reward_points: int = 0
    bonus_multiplier: float = 1.0
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    status: ChallengeStatus = ChallengeStatus.ACTIVE
    completion_percentage: float = 0.0
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ChallengeGenerator:
    """    Advanced AI-powered challenge generation system.
    
    Features:
    - Personalized challenge creation based on user behavior
    - Dynamic difficulty adaptation
    - Multi-category challenge templates
    - Progress tracking and optimization
    - Social and collaborative challenges
    - AI-driven engagement optimization
    """    
    def __init__(self, config: Optional[ChallengeConfig] = None):
        self.config = config or ChallengeConfig()
        self.challenge_templates: Dict[str, ChallengeTemplate] = {}
        self.active_challenges: Dict[str, List[PersonalizedChallenge]] = {}
        self.user_challenge_history: Dict[str, List[str]] = {}
        self.completion_stats: Dict[str, Dict[str, Any]] = {}
        
        # AI optimization metrics
        self.template_performance: Dict[str, float] = {}
        self.user_preference_scores: Dict[str, Dict[str, float]] = {}
        self.difficulty_success_rates: Dict[str, Dict[str, float]] = {}
        
        # Initialize default templates
        self._initialize_challenge_templates()
        
        logger.info("ChallengeGenerator initialized successfully")
    
    def _initialize_challenge_templates(self):
        """Initialize default challenge templates"""        templates = [
            # Content Creation Challenges
            ChallengeTemplate(
                template_id="daily_upload",
                title="Daily Creator",
                description="Upload {target_value} piece(s) of content today",
                challenge_type=ChallengeType.DAILY,
                difficulty=ChallengeDifficulty.BEGINNER,
                category="content_creation",
                target_metric="content_uploads",
                target_value=1.0,
                reward_points=25,
                duration_hours=24,
                tags=["content", "daily", "productivity"]
            ),
            
            ChallengeTemplate(
                template_id="quality_content_week",
                title="Quality Week",
                description="Upload {target_value} high-quality pieces this week (4+ star rating)",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.INTERMEDIATE,
                category="content_creation",
                target_metric="high_quality_uploads",
                target_value=3.0,
                reward_points=150,
                duration_hours=168,
                tags=["content", "quality", "weekly"]
            ),
            
            # Collaboration Challenges
            ChallengeTemplate(
                template_id="collaboration_starter",
                title="Team Player",
                description="Start {target_value} collaboration(s) this week",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.INTERMEDIATE,
                category="collaboration",
                target_metric="collaborations_started",
                target_value=2.0,
                reward_points=100,
                duration_hours=168,
                tags=["collaboration", "social", "networking"]
            ),
            
            ChallengeTemplate(
                template_id="collaboration_master",
                title="Collaboration Master",
                description="Complete {target_value} successful collaborations this month",
                challenge_type=ChallengeType.MONTHLY,
                difficulty=ChallengeDifficulty.ADVANCED,
                category="collaboration",
                target_metric="collaborations_completed",
                target_value=5.0,
                reward_points=500,
                duration_hours=720,  # 30 days
                tags=["collaboration", "achievement", "monthly"]
            ),
            
            # Engagement Challenges
            ChallengeTemplate(
                template_id="engagement_boost",
                title="Engagement Booster",
                description="Achieve {target_value}% engagement rate on your content",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.INTERMEDIATE,
                category="engagement",
                target_metric="engagement_rate",
                target_value=75.0,
                reward_points=200,
                duration_hours=168,
                tags=["engagement", "social", "performance"]
            ),
            
            # Skill Development Challenges
            ChallengeTemplate(
                template_id="skill_mastery",
                title="Skill Mastery Path",
                description="Complete {target_value} skill development activities",
                challenge_type=ChallengeType.MONTHLY,
                difficulty=ChallengeDifficulty.ADVANCED,
                category="skill_development",
                target_metric="skills_learned",
                target_value=3.0,
                reward_points=300,
                duration_hours=720,
                tags=["skills", "learning", "development"]
            ),
            
            # Monetization Challenges
            ChallengeTemplate(
                template_id="revenue_milestone",
                title="Revenue Achiever",
                description="Reach ${target_value} in revenue this month",
                challenge_type=ChallengeType.MONTHLY,
                difficulty=ChallengeDifficulty.EXPERT,
                category="monetization",
                target_metric="revenue_generated",
                target_value=100.0,
                reward_points=750,
                duration_hours=720,
                tags=["monetization", "revenue", "business"]
            ),
            
            # Community Challenges
            ChallengeTemplate(
                template_id="community_helper",
                title="Community Helper",
                description="Help {target_value} new creator(s) this week",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.INTERMEDIATE,
                category="community",
                target_metric="creators_helped",
                target_value=2.0,
                reward_points=125,
                duration_hours=168,
                tags=["community", "mentoring", "social"]
            ),
            
            # Creative Challenges
            ChallengeTemplate(
                template_id="creative_experiment",
                title="Creative Explorer",
                description="Try {target_value} new creative technique(s) or style(s)",
                challenge_type=ChallengeType.WEEKLY,
                difficulty=ChallengeDifficulty.INTERMEDIATE,
                category="creativity",
                target_metric="creative_experiments",
                target_value=2.0,
                reward_points=175,
                duration_hours=168,
                tags=["creativity", "innovation", "exploration"]
            ),
            
            # Consistency Challenges
            ChallengeTemplate(
                template_id="consistency_streak",
                title="Consistency Champion",
                description="Maintain a {target_value}-day activity streak",
                challenge_type=ChallengeType.MILESTONE,
                difficulty=ChallengeDifficulty.ADVANCED,
                category="consistency",
                target_metric="activity_streak",
                target_value=14.0,
                reward_points=400,
                duration_hours=336,  # 14 days
                tags=["consistency", "habits", "dedication"]
            )
        ]
        
        for template in templates:
            self.challenge_templates[template.template_id] = template
    
    async def generate_personalized_challenges(
        self,
        user_id: str,
        user_data: Dict[str, Any]
    ) -> List[PersonalizedChallenge]:
        """        Generate personalized challenges for a user based on their profile and behavior.
        
        Args:
            user_id: Unique user identifier
            user_data: User profile and activity data
            
        Returns:
            List of personalized challenges
        """        try:
            # Analyze user profile for personalization
            user_analysis = await self._analyze_user_profile(user_id, user_data)
            
            # Get current active challenges count
            current_challenges = self.active_challenges.get(user_id, [])
            available_slots = self.config.max_active_challenges_per_user - len(current_challenges)
            
            if available_slots <= 0:
                return []
            
            # Select appropriate challenge templates
            suitable_templates = await self._select_suitable_templates(user_analysis)
            
            # Generate personalized challenges
            new_challenges = []
            for template in suitable_templates[:available_slots]:
                challenge = await self._create_personalized_challenge(
                    user_id, template, user_analysis
                )
                new_challenges.append(challenge)
            
            # Store active challenges
            if user_id not in self.active_challenges:
                self.active_challenges[user_id] = []
            self.active_challenges[user_id].extend(new_challenges)
            
            # Update user challenge history
            if user_id not in self.user_challenge_history:
                self.user_challenge_history[user_id] = []
            
            challenge_ids = [c.challenge_id for c in new_challenges]
            self.user_challenge_history[user_id].extend(challenge_ids)
            
            logger.info(f"Generated {len(new_challenges)} personalized challenges for user {user_id}")
            return new_challenges
            
        except Exception as e:
            logger.error(f"Error generating personalized challenges: {str(e)}")
            return []
    
    async def _analyze_user_profile(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user profile for challenge personalization"""        analysis = {
            'user_id': user_id,
            'experience_level': 'beginner',
            'preferred_categories': [],
            'completion_rate': 0.0,
            'activity_patterns': {},
            'strengths': [],
            'improvement_areas': [],
            'engagement_level': 'moderate'
        }
        
        # Analyze experience level
        total_uploads = user_data.get('total_content_uploads', 0)
        collaborations = user_data.get('successful_collaborations', 0)
        level = user_data.get('level', 1)
        
        if level <= 3 and total_uploads < 10:
            analysis['experience_level'] = 'beginner'
        elif level <= 7 and total_uploads < 50:
            analysis['experience_level'] = 'intermediate'
        elif level <= 12 and total_uploads < 100:
            analysis['experience_level'] = 'advanced'
        else:
            analysis['experience_level'] = 'expert'
        
        # Analyze preferred categories based on past activity
        if total_uploads > 20:
            analysis['preferred_categories'].append('content_creation')
        
        if collaborations > 5:
            analysis['preferred_categories'].append('collaboration')
        
        social_score = user_data.get('social_engagement_score', 0)
        if social_score > 0.6:
            analysis['preferred_categories'].append('engagement')
        
        # Calculate completion rate
        user_history = self.user_challenge_history.get(user_id, [])
        if user_history:
            completed = len([c for c in user_history if self._is_challenge_completed(c)])
            analysis['completion_rate'] = completed / len(user_history)
        
        # Analyze strengths and improvement areas
        if total_uploads > 15:
            analysis['strengths'].append('content_creation')
        else:
            analysis['improvement_areas'].append('content_creation')
        
        if collaborations > 3:
            analysis['strengths'].append('collaboration')
        else:
            analysis['improvement_areas'].append('collaboration')
        
        if social_score < 0.5:
            analysis['improvement_areas'].append('engagement')
        
        # Determine engagement level
        streak_days = user_data.get('streak_days', 0)
        if streak_days > 14:
            analysis['engagement_level'] = 'high'
        elif streak_days > 7:
            analysis['engagement_level'] = 'moderate'
        else:
            analysis['engagement_level'] = 'low'
        
        return analysis
    
    async def _select_suitable_templates(self, user_analysis: Dict[str, Any]) -> List[ChallengeTemplate]:
        """Select suitable challenge templates based on user analysis"""        suitable_templates = []
        experience_level = user_analysis['experience_level']
        preferred_categories = user_analysis['preferred_categories']
        improvement_areas = user_analysis['improvement_areas']
        
        # Map experience level to difficulty
        difficulty_mapping = {
            'beginner': [ChallengeDifficulty.BEGINNER, ChallengeDifficulty.INTERMEDIATE],
            'intermediate': [ChallengeDifficulty.BEGINNER, ChallengeDifficulty.INTERMEDIATE, ChallengeDifficulty.ADVANCED],
            'advanced': [ChallengeDifficulty.INTERMEDIATE, ChallengeDifficulty.ADVANCED, ChallengeDifficulty.EXPERT],
            'expert': [ChallengeDifficulty.ADVANCED, ChallengeDifficulty.EXPERT, ChallengeDifficulty.MASTER]
        }
        
        suitable_difficulties = difficulty_mapping.get(experience_level, [ChallengeDifficulty.BEGINNER])
        
        for template in self.challenge_templates.values():
            # Check difficulty suitability
            if template.difficulty not in suitable_difficulties:
                continue
            
            # Prioritize improvement areas
            if template.category in improvement_areas:
                suitable_templates.append(template)
                continue
            
            # Include preferred categories
            if template.category in preferred_categories:
                suitable_templates.append(template)
                continue
            
            # Include daily challenges for engagement
            if template.challenge_type == ChallengeType.DAILY:
                suitable_templates.append(template)
        
        # Ensure variety by limiting templates per category
        category_counts = {}
        filtered_templates = []
        
        for template in suitable_templates:
            category = template.category
            if category_counts.get(category, 0) < 2:  # Max 2 per category
                filtered_templates.append(template)
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Shuffle for randomness while maintaining AI optimization
        random.shuffle(filtered_templates)
        
        return filtered_templates[:3]  # Return top 3 suitable templates
    
    async def _create_personalized_challenge(
        self,
        user_id: str,
        template: ChallengeTemplate,
        user_analysis: Dict[str, Any]
    ) -> PersonalizedChallenge:
        """Create a personalized challenge from template"""        
        # Calculate personalized target value
        base_target = template.target_value
        experience_multiplier = {
            'beginner': 0.7,
            'intermediate': 1.0,
            'advanced': 1.3,
            'expert': 1.6
        }
        
        multiplier = experience_multiplier.get(user_analysis['experience_level'], 1.0)
        personalized_target = max(1, int(base_target * multiplier))
        
        # Calculate end date
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(hours=template.duration_hours)
        
        # Create personalized challenge
        challenge = PersonalizedChallenge(
            challenge_id=f"challenge_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            template_id=template.template_id,
            title=template.title,
            description=template.description.format(target_value=personalized_target),
            challenge_type=template.challenge_type,
            difficulty=template.difficulty,
            target_metric=template.target_metric,
            target_value=personalized_target,
            reward_points=template.reward_points,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add AI insights for optimization
        challenge.ai_insights = {
            'personalization_factor': multiplier,
            'user_experience_level': user_analysis['experience_level'],
            'predicted_completion_probability': self._predict_completion_probability(
                user_analysis, template
            ),
            'optimization_suggestions': self._generate_optimization_suggestions(
                user_analysis, template
            )
        }
        
        return challenge
    
    def _predict_completion_probability(
        self,
        user_analysis: Dict[str, Any],
        template: ChallengeTemplate
    ) -> float:
        """Predict the probability of challenge completion using AI"""        base_probability = 0.6  # Base 60% completion rate
        
        # Adjust based on user completion history
        completion_rate = user_analysis.get('completion_rate', 0.5)
        probability = base_probability * (0.5 + completion_rate)
        
        # Adjust based on difficulty vs experience
        experience_level = user_analysis['experience_level']
        difficulty = template.difficulty
        
        difficulty_adjustment = {
            ('beginner', ChallengeDifficulty.BEGINNER): 1.2,
            ('beginner', ChallengeDifficulty.INTERMEDIATE): 0.8,
            ('intermediate', ChallengeDifficulty.BEGINNER): 1.1,
            ('intermediate', ChallengeDifficulty.INTERMEDIATE): 1.0,
            ('intermediate', ChallengeDifficulty.ADVANCED): 0.8,
            ('advanced', ChallengeDifficulty.INTERMEDIATE): 1.1,
            ('advanced', ChallengeDifficulty.ADVANCED): 1.0,
            ('advanced', ChallengeDifficulty.EXPERT): 0.7,
            ('expert', ChallengeDifficulty.ADVANCED): 1.1,
            ('expert', ChallengeDifficulty.EXPERT): 1.0,
            ('expert', ChallengeDifficulty.MASTER): 0.8
        }
        
        adjustment = difficulty_adjustment.get((experience_level, difficulty), 0.9)
        probability *= adjustment
        
        # Adjust based on category preference
        preferred_categories = user_analysis.get('preferred_categories', [])
        if template.category in preferred_categories:
            probability *= 1.2
        
        return min(1.0, max(0.1, probability))
    
    def _generate_optimization_suggestions(
        self,
        user_analysis: Dict[str, Any],
        template: ChallengeTemplate
    ) -> List[str]:
        """Generate AI-powered optimization suggestions"""        suggestions = []
        
        # Difficulty optimization
        experience_level = user_analysis['experience_level']
        if experience_level == 'beginner' and template.difficulty != ChallengeDifficulty.BEGINNER:
            suggestions.append("Consider reducing difficulty for better completion rate")
        
        # Category optimization
        improvement_areas = user_analysis.get('improvement_areas', [])
        if template.category in improvement_areas:
            suggestions.append("Focus challenge aligns with improvement needs")
        
        # Engagement optimization
        engagement_level = user_analysis.get('engagement_level', 'moderate')
        if engagement_level == 'low':
            suggestions.append("Consider shorter duration or easier targets for re-engagement")
        
        # Timing optimization
        if template.challenge_type == ChallengeType.DAILY:
            suggestions.append("Daily challenges help build consistent habits")
        
        return suggestions
    
    async def update_challenge_progress(
        self,
        user_id: str,
        challenge_id: str,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update challenge progress and check for completion"""        try:
            # Find the challenge
            user_challenges = self.active_challenges.get(user_id, [])
            challenge = None
            
            for c in user_challenges:
                if c.challenge_id == challenge_id:
                    challenge = c
                    break
            
            if not challenge:
                return {'error': 'Challenge not found'}
            
            # Update progress
            metric_value = progress_data.get(challenge.target_metric, 0)
            challenge.current_progress = metric_value
            challenge.completion_percentage = min(100, (metric_value / challenge.target_value) * 100)
            
            # Check for completion
            if metric_value >= challenge.target_value:
                challenge.status = ChallengeStatus.COMPLETED
                completion_reward = self._calculate_completion_reward(challenge)
                
                # Update completion stats
                self._update_completion_stats(user_id, challenge)
                
                return {
                    'status': 'completed',
                    'challenge_id': challenge_id,
                    'reward_points': completion_reward,
                    'completion_percentage': 100,
                    'completion_time': datetime.now(timezone.utc).isoformat()
                }
            
            # Check for expiry
            if challenge.end_date and datetime.now(timezone.utc) > challenge.end_date:
                challenge.status = ChallengeStatus.EXPIRED
                return {
                    'status': 'expired',
                    'challenge_id': challenge_id,
                    'completion_percentage': challenge.completion_percentage
                }
            
            return {
                'status': 'in_progress',
                'challenge_id': challenge_id,
                'current_progress': challenge.current_progress,
                'completion_percentage': challenge.completion_percentage,
                'target_value': challenge.target_value
            }
            
        except Exception as e:
            logger.error(f"Error updating challenge progress: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_completion_reward(self, challenge: PersonalizedChallenge) -> int:
        """Calculate reward points for challenge completion"""        base_reward = challenge.reward_points
        
        # Early completion bonus
        if challenge.end_date:
            time_remaining = challenge.end_date - datetime.now(timezone.utc)
            total_duration = challenge.end_date - challenge.start_date
            time_ratio = time_remaining.total_seconds() / total_duration.total_seconds()
            
            if time_ratio > 0.5:  # Completed in first half of time
                base_reward = int(base_reward * 1.2)
        
        # Difficulty bonus
        difficulty_bonus = {
            ChallengeDifficulty.BEGINNER: 1.0,
            ChallengeDifficulty.INTERMEDIATE: 1.1,
            ChallengeDifficulty.ADVANCED: 1.2,
            ChallengeDifficulty.EXPERT: 1.3,
            ChallengeDifficulty.MASTER: 1.5
        }
        
        multiplier = difficulty_bonus.get(challenge.difficulty, 1.0)
        final_reward = int(base_reward * multiplier * challenge.bonus_multiplier)
        
        return final_reward
    
    def _update_completion_stats(self, user_id: str, challenge: PersonalizedChallenge):
        """Update completion statistics for optimization"""        if user_id not in self.completion_stats:
            self.completion_stats[user_id] = {}
        
        stats = self.completion_stats[user_id]
        template_id = challenge.template_id
        
        if template_id not in stats:
            stats[template_id] = {
                'attempts': 0,
                'completions': 0,
                'completion_rate': 0.0,
                'average_time': 0.0
            }
        
        stats[template_id]['attempts'] += 1
        stats[template_id]['completions'] += 1
        stats[template_id]['completion_rate'] = (
            stats[template_id]['completions'] / stats[template_id]['attempts']
        )
        
        # Update global template performance
        if template_id not in self.template_performance:
            self.template_performance[template_id] = 0.0
        
        # Update performance score (weighted average)
        self.template_performance[template_id] = (
            self.template_performance[template_id] * 0.8 + 
            stats[template_id]['completion_rate'] * 0.2
        )
    
    def _is_challenge_completed(self, challenge_id: str) -> bool:
        """Check if a challenge was completed"""        for user_challenges in self.active_challenges.values():
            for challenge in user_challenges:
                if challenge.challenge_id == challenge_id:
                    return challenge.status == ChallengeStatus.COMPLETED
        return False
    
    async def get_user_challenges(self, user_id: str) -> Dict[str, Any]:
        """Get all challenges for a user"""        try:
            user_challenges = self.active_challenges.get(user_id, [])
            
            challenges_data = {
                'user_id': user_id,
                'total_challenges': len(user_challenges),
                'active_challenges': [],
                'completed_challenges': [],
                'expired_challenges': []
            }
            
            for challenge in user_challenges:
                challenge_data = {
                    'challenge_id': challenge.challenge_id,
                    'title': challenge.title,
                    'description': challenge.description,
                    'type': challenge.challenge_type.value,
                    'difficulty': challenge.difficulty.value,
                    'target_value': challenge.target_value,
                    'current_progress': challenge.current_progress,
                    'completion_percentage': challenge.completion_percentage,
                    'reward_points': challenge.reward_points,
                    'start_date': challenge.start_date.isoformat(),
                    'end_date': challenge.end_date.isoformat() if challenge.end_date else None,
                    'status': challenge.status.value
                }
                
                if challenge.status == ChallengeStatus.ACTIVE:
                    challenges_data['active_challenges'].append(challenge_data)
                elif challenge.status == ChallengeStatus.COMPLETED:
                    challenges_data['completed_challenges'].append(challenge_data)
                elif challenge.status == ChallengeStatus.EXPIRED:
                    challenges_data['expired_challenges'].append(challenge_data)
            
            return challenges_data
            
        except Exception as e:
            logger.error(f"Error getting user challenges: {str(e)}")
            return {'error': str(e)}
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide challenge analytics"""        total_challenges = sum(len(challenges) for challenges in self.active_challenges.values())
        total_users = len(self.active_challenges)
        
        # Calculate average completion rate
        total_completion_rate = 0.0
        total_users_with_stats = 0
        
        for user_stats in self.completion_stats.values():
            for template_stats in user_stats.values():
                total_completion_rate += template_stats['completion_rate']
                total_users_with_stats += 1
        
        avg_completion_rate = (
            total_completion_rate / total_users_with_stats 
            if total_users_with_stats > 0 else 0.0
        )
        
        return {
            'total_active_challenges': total_challenges,
            'total_users_with_challenges': total_users,
            'total_challenge_templates': len(self.challenge_templates),
            'average_completion_rate': round(avg_completion_rate, 3),
            'template_performance': self.template_performance.copy(),
            'system_status': 'operational',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Export classes
__all__ = [
    'ChallengeGenerator',
    'ChallengeConfig',
    'ChallengeTemplate',
    'PersonalizedChallenge',
    'ChallengeType',
    'ChallengeDifficulty',
    'ChallengeStatus'
]