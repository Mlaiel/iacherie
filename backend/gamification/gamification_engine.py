"""
Gamification Engine for Ainflue Platform
Advanced gamification and engagement system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Import gamification modules
try:
    from .achievement_engine import *
except ImportError:
    pass
try:
    from .reward_system import *
except ImportError:
    pass
try:
    from .ranking_engine import *
except ImportError:
    pass
try:
    from .challenge_system import *
except ImportError:
    pass
try:
    from .badge_generator import *
except ImportError:
    pass
try:
    from .achievement_system import *
except ImportError:
    pass
try:
    from .rewards_manager import *
except ImportError:
    pass


class GamificationStatus(Enum):
    """Status enumeration for gamification operations"""
    ACTIVE = "active"
    PROCESSING = "processing"
    REWARDING = "rewarding"
    RANKING = "ranking"
    ERROR = "error"


@dataclass
class GamificationMetrics:
    """Metrics for gamification engine performance"""
    active_users: int = 0
    achievements_unlocked: int = 0
    badges_earned: int = 0
    challenges_completed: int = 0
    total_points_awarded: int = 0
    engagement_score: float = 0.0


class GamificationEngine:
    """
    Main Gamification Engine for Ainflue platform
    Manages all gamification elements, achievements, rewards, and user engagement
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Gamification Engine"""
        self.config = config or {}
        self.status = GamificationStatus.ACTIVE
        self.metrics = GamificationMetrics()
        self.logger = logging.getLogger(__name__)
        self.achievement_systems = self._initialize_achievement_systems()
        self.reward_systems = self._initialize_reward_systems()
        self.engagement_systems = self._initialize_engagement_systems()
        
    def _initialize_achievement_systems(self) -> Dict[str, Any]:
        """Initialize achievement systems"""
        return {
            'content_achievements': {
                'upload_milestones': [1, 10, 50, 100, 500],
                'quality_achievements': ['first_viral', 'quality_master', 'innovation_award'],
                'collaboration_achievements': ['team_player', 'mentor', 'collaboration_king']
            },
            'skill_achievements': {
                'technical_skills': ['audio_master', 'video_expert', 'mixing_pro'],
                'creative_skills': ['creative_genius', 'style_innovator', 'artistic_vision'],
                'business_skills': ['entrepreneur', 'revenue_master', 'market_leader']
            },
            'community_achievements': {
                'social_impact': ['influencer', 'community_builder', 'thought_leader'],
                'helping_others': ['mentor_badge', 'helper', 'knowledge_sharer'],
                'platform_loyalty': ['early_adopter', 'platform_ambassador', 'legend']
            },
            'special_achievements': {
                'seasonal': ['summer_creator', 'holiday_special', 'anniversary_badge'],
                'limited_edition': ['founder_badge', 'exclusive_member', 'vip_creator'],
                'competition': ['contest_winner', 'champion', 'grand_master']
            }
        }
    
    def _initialize_reward_systems(self) -> Dict[str, Any]:
        """Initialize reward systems"""
        return {
            'point_system': {
                'base_points': {
                    'content_upload': 10,
                    'collaboration_completion': 50,
                    'achievement_unlock': 25,
                    'challenge_completion': 30,
                    'community_interaction': 5
                },
                'multipliers': {
                    'quality_bonus': 2.0,
                    'viral_bonus': 5.0,
                    'first_time_bonus': 1.5,
                    'streak_bonus': 1.2
                }
            },
            'virtual_economy': {
                'currencies': {
                    'ainflue_coins': {'base_currency': True, 'exchange_rate': 1.0},
                    'premium_tokens': {'premium_currency': True, 'exchange_rate': 10.0},
                    'collaboration_credits': {'special_currency': True, 'exchange_rate': 5.0}
                },
                'economy_balance': 'automated',
                'inflation_control': True
            },
            'real_rewards': {
                'cash_rewards': {'enabled': True, 'minimum_threshold': 100},
                'premium_features': {'enabled': True, 'point_cost': 500},
                'merchandise': {'enabled': True, 'catalog_size': 50},
                'exclusive_access': {'enabled': True, 'vip_events': True}
            }
        }
    
    def _initialize_engagement_systems(self) -> Dict[str, Any]:
        """Initialize engagement systems"""
        return {
            'challenge_system': {
                'daily_challenges': True,
                'weekly_challenges': True,
                'monthly_challenges': True,
                'special_events': True,
                'difficulty_levels': ['beginner', 'intermediate', 'advanced', 'expert']
            },
            'competition_system': {
                'tournaments': True,
                'leaderboards': True,
                'seasonal_competitions': True,
                'bracket_system': True
            },
            'progression_system': {
                'level_system': {'max_level': 100, 'experience_curve': 'exponential'},
                'skill_trees': {'branches': 5, 'skills_per_branch': 20},
                'mastery_system': {'masteries': 10, 'requirements': 'varied'},
                'prestige_system': {'enabled': True, 'reset_benefits': True}
            }
        }
    
    async def process_user_action(self, user_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user action for gamification rewards"""
        try:
            self.status = GamificationStatus.PROCESSING
            self.logger.info(f"Processing gamification for user {user_id}, action: {action}")
            
            # Calculate points earned
            points_earned = await self._calculate_points(action, data)
            
            # Check for achievements
            achievements = await self._check_achievements(user_id, action, data)
            
            # Check for badge unlocks
            badges = await self._check_badge_unlocks(user_id, action, data)
            
            # Update user level/progress
            progression = await self._update_user_progression(user_id, points_earned)
            
            # Check for rewards
            rewards = await self._check_rewards(user_id, points_earned, achievements)
            
            # Update metrics
            self.metrics.total_points_awarded += points_earned['total']
            self.metrics.achievements_unlocked += len(achievements)
            self.metrics.badges_earned += len(badges)
            
            self.status = GamificationStatus.ACTIVE
            
            return {
                'success': True,
                'user_id': user_id,
                'action': action,
                'points_earned': points_earned,
                'achievements_unlocked': achievements,
                'badges_earned': badges,
                'progression_update': progression,
                'rewards_earned': rewards,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing gamification action: {e}")
            self.status = GamificationStatus.ERROR
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _calculate_points(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate points earned for an action"""
        base_points = self.reward_systems['point_system']['base_points'].get(action, 0)
        multipliers = self.reward_systems['point_system']['multipliers']
        
        # Apply multipliers based on data
        total_multiplier = 1.0
        applied_multipliers = []
        
        if data.get('high_quality', False):
            total_multiplier *= multipliers['quality_bonus']
            applied_multipliers.append('quality_bonus')
        
        if data.get('viral_content', False):
            total_multiplier *= multipliers['viral_bonus']
            applied_multipliers.append('viral_bonus')
        
        if data.get('first_time', False):
            total_multiplier *= multipliers['first_time_bonus']
            applied_multipliers.append('first_time_bonus')
        
        if data.get('streak_active', False):
            total_multiplier *= multipliers['streak_bonus']
            applied_multipliers.append('streak_bonus')
        
        total_points = int(base_points * total_multiplier)
        
        return {
            'base_points': base_points,
            'multiplier': total_multiplier,
            'applied_multipliers': applied_multipliers,
            'total': total_points
        }
    
    async def _check_achievements(self, user_id: str, action: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for achievement unlocks"""
        unlocked_achievements = []
        
        # Content achievements
        if action == 'content_upload':
            upload_count = data.get('user_upload_count', 0)
            milestones = self.achievement_systems['content_achievements']['upload_milestones']
            
            for milestone in milestones:
                if upload_count == milestone:
                    unlocked_achievements.append({
                        'type': 'content_milestone',
                        'name': f'Upload Master {milestone}',
                        'description': f'Uploaded {milestone} pieces of content',
                        'points_bonus': milestone * 10,
                        'rarity': 'common' if milestone <= 10 else 'rare' if milestone <= 100 else 'epic'
                    })
        
        # Collaboration achievements
        if action == 'collaboration_completion':
            collaboration_count = data.get('user_collaboration_count', 0)
            if collaboration_count == 1:
                unlocked_achievements.append({
                    'type': 'collaboration',
                    'name': 'Team Player',
                    'description': 'Completed first collaboration',
                    'points_bonus': 50,
                    'rarity': 'common'
                })
            elif collaboration_count == 10:
                unlocked_achievements.append({
                    'type': 'collaboration',
                    'name': 'Collaboration King',
                    'description': 'Completed 10 collaborations',
                    'points_bonus': 500,
                    'rarity': 'epic'
                })
        
        # Quality achievements
        if data.get('high_quality', False) and action == 'content_upload':
            unlocked_achievements.append({
                'type': 'quality',
                'name': 'Quality Master',
                'description': 'Created high-quality content',
                'points_bonus': 100,
                'rarity': 'rare'
            })
        
        return unlocked_achievements
    
    async def _check_badge_unlocks(self, user_id: str, action: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for badge unlocks"""
        unlocked_badges = []
        
        # Skill badges
        if action == 'skill_improvement':
            skill_type = data.get('skill_type', '')
            skill_level = data.get('skill_level', 0)
            
            if skill_level >= 50:
                unlocked_badges.append({
                    'type': 'skill',
                    'name': f'{skill_type.title()} Expert',
                    'description': f'Achieved expert level in {skill_type}',
                    'visual_design': 'golden_badge',
                    'display_priority': 'high'
                })
        
        # Activity badges
        if action == 'daily_login':
            streak = data.get('login_streak', 0)
            if streak == 7:
                unlocked_badges.append({
                    'type': 'activity',
                    'name': 'Dedicated Creator',
                    'description': '7-day login streak',
                    'visual_design': 'streak_badge',
                    'display_priority': 'medium'
                })
            elif streak == 30:
                unlocked_badges.append({
                    'type': 'activity',
                    'name': 'Platform Devotee',
                    'description': '30-day login streak',
                    'visual_design': 'dedication_badge',
                    'display_priority': 'high'
                })
        
        return unlocked_badges
    
    async def _update_user_progression(self, user_id: str, points_earned: Dict[str, Any]) -> Dict[str, Any]:
        """Update user progression (levels, experience, etc.)"""
        current_level = 15  # Mock current level
        current_xp = 1250   # Mock current XP
        
        new_xp = current_xp + points_earned['total']
        xp_for_next_level = 1500  # Mock calculation
        
        level_up = new_xp >= xp_for_next_level
        new_level = current_level + 1 if level_up else current_level
        
        return {
            'level_up': level_up,
            'old_level': current_level,
            'new_level': new_level,
            'old_xp': current_xp,
            'new_xp': new_xp,
            'xp_gained': points_earned['total'],
            'xp_to_next_level': xp_for_next_level - new_xp if not level_up else 0,
            'progression_percentage': (new_xp / xp_for_next_level) * 100 if not level_up else 100
        }
    
    async def _check_rewards(self, user_id: str, points_earned: Dict[str, Any], achievements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for rewards earned"""
        rewards = {
            'currency_rewards': {},
            'item_rewards': [],
            'access_rewards': [],
            'special_rewards': []
        }
        
        # Currency rewards
        total_points = points_earned['total']
        rewards['currency_rewards'] = {
            'ainflue_coins': total_points,
            'premium_tokens': total_points // 10,
            'collaboration_credits': total_points // 5 if 'collaboration' in str(achievements) else 0
        }
        
        # Achievement-based rewards
        for achievement in achievements:
            if achievement.get('rarity') == 'epic':
                rewards['special_rewards'].append({
                    'type': 'premium_feature_unlock',
                    'description': 'Unlocked premium AI tools for 7 days',
                    'duration': '7_days'
                })
        
        # Level-based rewards
        if total_points >= 100:
            rewards['access_rewards'].append({
                'type': 'exclusive_content',
                'description': 'Access to advanced tutorials',
                'permanent': True
            })
        
        return rewards
    
    async def create_challenge(self, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new gamification challenge"""
        try:
            self.logger.info("Creating new gamification challenge")
            
            challenge_id = f"challenge_{datetime.utcnow().timestamp()}"
            
            challenge = {
                'challenge_id': challenge_id,
                'title': challenge_data.get('title', 'Mystery Challenge'),
                'description': challenge_data.get('description', 'Complete the challenge to earn rewards'),
                'type': challenge_data.get('type', 'daily'),
                'difficulty': challenge_data.get('difficulty', 'intermediate'),
                'requirements': challenge_data.get('requirements', []),
                'rewards': {
                    'points': challenge_data.get('reward_points', 100),
                    'badges': challenge_data.get('reward_badges', []),
                    'special_rewards': challenge_data.get('special_rewards', [])
                },
                'duration': challenge_data.get('duration', '24_hours'),
                'participants': 0,
                'completion_rate': 0.0,
                'status': 'active',
                'created_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'challenge': challenge,
                'challenge_id': challenge_id
            }
            
        except Exception as e:
            self.logger.error(f"Error creating challenge: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def manage_leaderboards(self, leaderboard_type: str, time_period: str = 'weekly') -> Dict[str, Any]:
        """Manage and update leaderboards"""
        try:
            self.status = GamificationStatus.RANKING
            self.logger.info(f"Managing {leaderboard_type} leaderboard for {time_period}")
            
            # Mock leaderboard data
            leaderboard_data = [
                {'user_id': 'creator_001', 'score': 2500, 'rank': 1, 'change': 0},
                {'user_id': 'creator_002', 'score': 2350, 'rank': 2, 'change': 1},
                {'user_id': 'creator_003', 'score': 2200, 'rank': 3, 'change': -1},
                {'user_id': 'creator_004', 'score': 2100, 'rank': 4, 'change': 2},
                {'user_id': 'creator_005', 'score': 2050, 'rank': 5, 'change': 0}
            ]
            
            self.status = GamificationStatus.ACTIVE
            
            return {
                'success': True,
                'leaderboard_type': leaderboard_type,
                'time_period': time_period,
                'leaderboard': leaderboard_data,
                'total_participants': len(leaderboard_data),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error managing leaderboards: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_gamification_metrics(self) -> Dict[str, Any]:
        """Get gamification engine metrics"""
        return {
            'status': self.status.value,
            'active_users': self.metrics.active_users,
            'achievements_unlocked': self.metrics.achievements_unlocked,
            'badges_earned': self.metrics.badges_earned,
            'challenges_completed': self.metrics.challenges_completed,
            'total_points_awarded': self.metrics.total_points_awarded,
            'engagement_score': self.metrics.engagement_score
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            'status': 'healthy',
            'gamification_engine_status': self.status.value,
            'achievement_systems': self.achievement_systems,
            'reward_systems': self.reward_systems,
            'engagement_systems': self.engagement_systems,
            'metrics': self.get_gamification_metrics()
        }


# Export main classes and functions
__all__ = [
    'GamificationEngine',
    'GamificationStatus',
    'GamificationMetrics'
]