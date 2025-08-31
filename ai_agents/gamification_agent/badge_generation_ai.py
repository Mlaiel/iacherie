"""Badge Generation AI - Intelligent Badge Creation and Achievement System

Advanced AI system for generating personalized badges, managing achievement unlocks,
and creating dynamic recognition systems for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This badge generation AI and achievement algorithms are the exclusive intellectual property of Fahed Mlaiel.
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

class BadgeType(Enum):
    """Types of badges available"""
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    SKILL = "skill"
    COLLABORATION = "collaboration"
    QUALITY = "quality"
    CONSISTENCY = "consistency"
    INNOVATION = "innovation"
    COMMUNITY = "community"
    SPECIAL_EVENT = "special_event"

class BadgeRarity(Enum):
    """Badge rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class BadgeConfig:
    """Configuration for badge generation"""
    auto_generation_enabled: bool = True
    dynamic_criteria_enabled: bool = True
    personalization_enabled: bool = True
    rarity_balancing_enabled: bool = True
    visual_generation_enabled: bool = True
    achievement_tracking_enabled: bool = True

@dataclass
class GeneratedBadge:
    """Generated badge instance"""
    badge_id: str
    user_id: str
    title: str
    description: str
    badge_type: BadgeType
    rarity: BadgeRarity
    criteria_met: Dict[str, Any] = field(default_factory=dict)
    unlock_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    points_awarded: int = 0
    visual_attributes: Dict[str, Any] = field(default_factory=dict)
    special_properties: Dict[str, Any] = field(default_factory=dict)
    achievement_data: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Dict[str, Any] = field(default_factory=dict)

class BadgeGenerator:
    """
    Advanced AI-powered badge generation and achievement system.
    
    Features:
    - Dynamic badge creation based on user achievements
    - Personalized badge criteria and rewards
    - Rarity balancing and progression tracking
    - Visual badge attribute generation
    - Achievement milestone tracking
    - Community recognition systems
    """
    
    def __init__(self, config: Optional[BadgeConfig] = None):
        self.config = config or BadgeConfig()
        self.badge_templates: Dict[str, Dict[str, Any]] = {}
        self.user_badge_history: Dict[str, List[GeneratedBadge]] = {}
        self.achievement_criteria: Dict[str, Dict[str, Any]] = {}
        self.rarity_distribution: Dict[str, int] = {}
        
        # Initialize badge generation system
        self._initialize_badge_system()
        
        logger.info("BadgeGenerator initialized successfully")
    
    def _initialize_badge_system(self):
        """Initialize badge generation system"""
        # Initialize badge templates
        self._initialize_badge_templates()
        
        # Initialize achievement criteria
        self._initialize_achievement_criteria()
        
        # Initialize rarity distribution targets
        self.rarity_distribution = {
            BadgeRarity.COMMON.value: 50,      # 50% common
            BadgeRarity.UNCOMMON.value: 30,    # 30% uncommon
            BadgeRarity.RARE.value: 15,        # 15% rare
            BadgeRarity.EPIC.value: 4,         # 4% epic
            BadgeRarity.LEGENDARY.value: 1     # 1% legendary
        }
    
    def _initialize_badge_templates(self):
        """Initialize badge templates for different achievements"""
        self.badge_templates = {
            # Content Creation Badges
            'content_creator_novice': {
                'title': 'Content Creator',
                'description': 'Created your first piece of content',
                'type': BadgeType.ACHIEVEMENT,
                'rarity': BadgeRarity.COMMON,
                'criteria': {'content_uploads': 1},
                'points': 50,
                'visual': {'color': 'bronze', 'icon': 'create'}
            },
            'content_master': {
                'title': 'Content Master',
                'description': 'Created 100 pieces of high-quality content',
                'type': BadgeType.MILESTONE,
                'rarity': BadgeRarity.EPIC,
                'criteria': {'content_uploads': 100, 'avg_quality': 4.0},
                'points': 500,
                'visual': {'color': 'gold', 'icon': 'crown'}
            },
            
            # Quality Badges
            'quality_craftsperson': {
                'title': 'Quality Craftsperson',
                'description': 'Maintained 4.5+ star rating on last 10 uploads',
                'type': BadgeType.QUALITY,
                'rarity': BadgeRarity.RARE,
                'criteria': {'recent_quality_avg': 4.5, 'recent_uploads': 10},
                'points': 300,
                'visual': {'color': 'silver', 'icon': 'star'}
            },
            
            # Collaboration Badges
            'team_player': {
                'title': 'Team Player',
                'description': 'Completed 5 successful collaborations',
                'type': BadgeType.COLLABORATION,
                'rarity': BadgeRarity.UNCOMMON,
                'criteria': {'successful_collaborations': 5},
                'points': 200,
                'visual': {'color': 'blue', 'icon': 'handshake'}
            },
            'collaboration_legend': {
                'title': 'Collaboration Legend',
                'description': 'Led 25 successful collaborations with 4.8+ rating',
                'type': BadgeType.COLLABORATION,
                'rarity': BadgeRarity.LEGENDARY,
                'criteria': {'led_collaborations': 25, 'avg_collaboration_rating': 4.8},
                'points': 1000,
                'visual': {'color': 'platinum', 'icon': 'network'}
            },
            
            # Consistency Badges
            'consistent_creator': {
                'title': 'Consistent Creator',
                'description': 'Maintained 30-day activity streak',
                'type': BadgeType.CONSISTENCY,
                'rarity': BadgeRarity.UNCOMMON,
                'criteria': {'activity_streak': 30},
                'points': 250,
                'visual': {'color': 'green', 'icon': 'calendar'}
            },
            
            # Innovation Badges
            'innovator': {
                'title': 'Innovator',
                'description': 'Pioneered 3 new creative techniques',
                'type': BadgeType.INNOVATION,
                'rarity': BadgeRarity.RARE,
                'criteria': {'innovation_count': 3, 'technique_adoption': 10},
                'points': 400,
                'visual': {'color': 'purple', 'icon': 'lightbulb'}
            },
            
            # Community Badges
            'community_champion': {
                'title': 'Community Champion',
                'description': 'Helped 20 new creators get started',
                'type': BadgeType.COMMUNITY,
                'rarity': BadgeRarity.EPIC,
                'criteria': {'creators_helped': 20, 'mentoring_rating': 4.5},
                'points': 600,
                'visual': {'color': 'orange', 'icon': 'heart'}
            },
            
            # Special Achievement Badges
            'viral_sensation': {
                'title': 'Viral Sensation',
                'description': 'Created content with 1M+ views',
                'type': BadgeType.SPECIAL_EVENT,
                'rarity': BadgeRarity.LEGENDARY,
                'criteria': {'max_content_views': 1000000},
                'points': 1500,
                'visual': {'color': 'rainbow', 'icon': 'fire'}
            }
        }
    
    def _initialize_achievement_criteria(self):
        """Initialize dynamic achievement criteria"""
        self.achievement_criteria = {
            'milestone_levels': {
                'content_uploads': [1, 5, 10, 25, 50, 100, 250, 500, 1000],
                'collaborations': [1, 3, 5, 10, 20, 50, 100],
                'followers': [100, 500, 1000, 5000, 10000, 50000, 100000],
                'total_views': [1000, 10000, 100000, 1000000, 10000000]
            },
            'quality_thresholds': {
                'content_rating': [3.0, 3.5, 4.0, 4.5, 4.8, 4.9],
                'engagement_rate': [0.3, 0.5, 0.7, 0.8, 0.9],
                'collaboration_rating': [3.0, 3.5, 4.0, 4.5, 4.8]
            },
            'consistency_metrics': {
                'activity_streak': [7, 14, 30, 60, 90, 180, 365],
                'upload_frequency': [1, 3, 5, 7, 10, 15, 20]  # per week
            }
        }
    
    async def generate_badges(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate badges for user based on their achievements and activity.
        
        Args:
            user_id: Unique user identifier
            activity_data: User activity and achievement data
            
        Returns:
            Generated badges and achievement updates
        """
        try:
            # Analyze user achievements
            achievement_analysis = await self._analyze_user_achievements(user_id, activity_data)
            
            # Check for new badge unlocks
            new_badges = await self._check_badge_unlocks(user_id, achievement_analysis)
            
            # Generate dynamic badges if enabled
            if self.config.dynamic_criteria_enabled:
                dynamic_badges = await self._generate_dynamic_badges(user_id, achievement_analysis)
                new_badges.extend(dynamic_badges)
            
            # Personalize badges if enabled
            if self.config.personalization_enabled:
                personalized_badges = await self._personalize_badges(user_id, new_badges)
                new_badges = personalized_badges
            
            # Apply rarity balancing
            if self.config.rarity_balancing_enabled:
                balanced_badges = await self._apply_rarity_balancing(user_id, new_badges)
                new_badges = balanced_badges
            
            # Add visual attributes
            if self.config.visual_generation_enabled:
                for badge in new_badges:
                    badge.visual_attributes = await self._generate_visual_attributes(badge)
            
            # Store badges in user history
            if user_id not in self.user_badge_history:
                self.user_badge_history[user_id] = []
            self.user_badge_history[user_id].extend(new_badges)
            
            # Calculate total points awarded
            total_points = sum(badge.points_awarded for badge in new_badges)
            
            return {
                'user_id': user_id,
                'new_badges': [self._serialize_badge(badge) for badge in new_badges],
                'total_points_awarded': total_points,
                'achievement_summary': achievement_analysis,
                'next_achievements': await self._predict_next_achievements(user_id, achievement_analysis),
                'badge_collection_stats': await self._get_badge_collection_stats(user_id),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating badges: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_user_achievements(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user achievements and milestones"""
        analysis = {
            'content_metrics': {
                'total_uploads': activity_data.get('total_content_uploads', 0),
                'avg_quality_rating': activity_data.get('avg_content_rating', 0.0),
                'max_views': activity_data.get('max_content_views', 0),
                'total_views': activity_data.get('total_content_views', 0)
            },
            'collaboration_metrics': {
                'total_collaborations': activity_data.get('successful_collaborations', 0),
                'avg_collaboration_rating': activity_data.get('avg_collaboration_rating', 0.0),
                'led_collaborations': activity_data.get('led_collaborations', 0)
            },
            'engagement_metrics': {
                'follower_count': activity_data.get('follower_count', 0),
                'engagement_rate': activity_data.get('engagement_rate', 0.0),
                'social_score': activity_data.get('social_engagement_score', 0.0)
            },
            'consistency_metrics': {
                'activity_streak': activity_data.get('streak_days', 0),
                'weekly_upload_frequency': activity_data.get('uploads_per_week', 0)
            },
            'innovation_metrics': {
                'innovation_count': activity_data.get('innovation_count', 0),
                'technique_adoption': activity_data.get('technique_adoption_count', 0)
            },
            'community_metrics': {
                'creators_helped': activity_data.get('creators_helped', 0),
                'mentoring_rating': activity_data.get('mentoring_rating', 0.0),
                'community_contributions': activity_data.get('community_contributions', 0)
            }
        }
        
        # Calculate achievement progress
        analysis['achievement_progress'] = self._calculate_achievement_progress(analysis)
        
        return analysis
    
    def _calculate_achievement_progress(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate progress towards various achievements"""
        progress = {}
        
        # Content milestones
        content_uploads = analysis['content_metrics']['total_uploads']
        content_milestones = self.achievement_criteria['milestone_levels']['content_uploads']
        progress['content_milestones'] = self._calculate_milestone_progress(
            content_uploads, content_milestones
        )
        
        # Collaboration milestones
        collaborations = analysis['collaboration_metrics']['total_collaborations']
        collab_milestones = self.achievement_criteria['milestone_levels']['collaborations']
        progress['collaboration_milestones'] = self._calculate_milestone_progress(
            collaborations, collab_milestones
        )
        
        # Quality achievements
        quality_rating = analysis['content_metrics']['avg_quality_rating']
        quality_thresholds = self.achievement_criteria['quality_thresholds']['content_rating']
        progress['quality_achievements'] = self._calculate_threshold_progress(
            quality_rating, quality_thresholds
        )
        
        # Consistency achievements
        streak_days = analysis['consistency_metrics']['activity_streak']
        streak_milestones = self.achievement_criteria['consistency_metrics']['activity_streak']
        progress['consistency_achievements'] = self._calculate_milestone_progress(
            streak_days, streak_milestones
        )
        
        return progress
    
    def _calculate_milestone_progress(self, current_value: int, milestones: List[int]) -> Dict[str, Any]:
        """Calculate progress towards milestone achievements"""
        achieved_milestones = [m for m in milestones if current_value >= m]
        next_milestone = None
        
        for milestone in milestones:
            if current_value < milestone:
                next_milestone = milestone
                break
        
        return {
            'current_value': current_value,
            'achieved_count': len(achieved_milestones),
            'next_milestone': next_milestone,
            'progress_to_next': (
                (current_value / next_milestone) * 100 if next_milestone else 100
            )
        }
    
    def _calculate_threshold_progress(self, current_value: float, thresholds: List[float]) -> Dict[str, Any]:
        """Calculate progress towards threshold achievements"""
        achieved_thresholds = [t for t in thresholds if current_value >= t]
        next_threshold = None
        
        for threshold in thresholds:
            if current_value < threshold:
                next_threshold = threshold
                break
        
        return {
            'current_value': current_value,
            'achieved_count': len(achieved_thresholds),
            'next_threshold': next_threshold,
            'progress_to_next': (
                (current_value / next_threshold) * 100 if next_threshold else 100
            )
        }
    
    async def _check_badge_unlocks(
        self,
        user_id: str,
        achievement_analysis: Dict[str, Any]
    ) -> List[GeneratedBadge]:
        """Check for new badge unlocks based on achievements"""
        new_badges = []
        existing_badges = [b.badge_id.split('_')[0] for b in self.user_badge_history.get(user_id, [])]
        
        for template_id, template in self.badge_templates.items():
            # Skip if user already has this badge type
            if template_id in existing_badges:
                continue
            
            # Check if criteria are met
            if self._check_badge_criteria(template['criteria'], achievement_analysis):
                badge = GeneratedBadge(
                    badge_id=f"{template_id}_{uuid.uuid4().hex[:8]}",
                    user_id=user_id,
                    title=template['title'],
                    description=template['description'],
                    badge_type=template['type'],
                    rarity=template['rarity'],
                    criteria_met=template['criteria'],
                    points_awarded=template['points'],
                    visual_attributes=template.get('visual', {}),
                    ai_insights=self._generate_badge_insights(template, achievement_analysis)
                )
                new_badges.append(badge)
        
        return new_badges
    
    def _check_badge_criteria(
        self,
        criteria: Dict[str, Any],
        achievement_analysis: Dict[str, Any]
    ) -> bool:
        """Check if badge criteria are met"""
        for criterion, required_value in criteria.items():
            current_value = self._get_metric_value(criterion, achievement_analysis)
            
            if current_value < required_value:
                return False
        
        return True
    
    def _get_metric_value(self, metric_name: str, achievement_analysis: Dict[str, Any]) -> float:
        """Get current value for a specific metric"""
        metric_mapping = {
            'content_uploads': achievement_analysis['content_metrics']['total_uploads'],
            'avg_quality': achievement_analysis['content_metrics']['avg_quality_rating'],
            'successful_collaborations': achievement_analysis['collaboration_metrics']['total_collaborations'],
            'led_collaborations': achievement_analysis['collaboration_metrics']['led_collaborations'],
            'avg_collaboration_rating': achievement_analysis['collaboration_metrics']['avg_collaboration_rating'],
            'activity_streak': achievement_analysis['consistency_metrics']['activity_streak'],
            'max_content_views': achievement_analysis['content_metrics']['max_views'],
            'innovation_count': achievement_analysis['innovation_metrics']['innovation_count'],
            'technique_adoption': achievement_analysis['innovation_metrics']['technique_adoption'],
            'creators_helped': achievement_analysis['community_metrics']['creators_helped'],
            'mentoring_rating': achievement_analysis['community_metrics']['mentoring_rating'],
            'recent_quality_avg': achievement_analysis['content_metrics']['avg_quality_rating'],
            'recent_uploads': achievement_analysis['content_metrics']['total_uploads']
        }
        
        return metric_mapping.get(metric_name, 0)
    
    async def _generate_dynamic_badges(
        self,
        user_id: str,
        achievement_analysis: Dict[str, Any]
    ) -> List[GeneratedBadge]:
        """Generate dynamic badges based on unique achievements"""
        dynamic_badges = []
        
        # Check for unique combinations or exceptional performance
        content_metrics = achievement_analysis['content_metrics']
        collaboration_metrics = achievement_analysis['collaboration_metrics']
        
        # High quality + high volume combination
        if (content_metrics['total_uploads'] > 50 and 
            content_metrics['avg_quality_rating'] > 4.5):
            
            badge = GeneratedBadge(
                badge_id=f"dynamic_quality_volume_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                title="Quality & Volume Master",
                description="Exceptional combination of high-quality and high-volume content creation",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.EPIC,
                points_awarded=750,
                ai_insights={'dynamic_generation': True, 'combination_achievement': True}
            )
            dynamic_badges.append(badge)
        
        # Collaboration leadership
        if (collaboration_metrics['led_collaborations'] > 10 and
            collaboration_metrics['avg_collaboration_rating'] > 4.0):
            
            badge = GeneratedBadge(
                badge_id=f"dynamic_collab_leader_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                title="Collaboration Leader",
                description="Outstanding leadership in collaborative projects",
                badge_type=BadgeType.COLLABORATION,
                rarity=BadgeRarity.RARE,
                points_awarded=500,
                ai_insights={'dynamic_generation': True, 'leadership_achievement': True}
            )
            dynamic_badges.append(badge)
        
        return dynamic_badges
    
    async def _personalize_badges(
        self,
        user_id: str,
        badges: List[GeneratedBadge]
    ) -> List[GeneratedBadge]:
        """Personalize badges based on user preferences and history"""
        # Get user's badge history for personalization insights
        user_history = self.user_badge_history.get(user_id, [])
        
        for badge in badges:
            # Personalize description based on specific achievements
            if badge.badge_type == BadgeType.COLLABORATION:
                collaboration_count = len([b for b in user_history 
                                         if b.badge_type == BadgeType.COLLABORATION])
                if collaboration_count == 0:
                    badge.description += " - Your first collaboration achievement!"
                else:
                    badge.description += f" - Your {collaboration_count + 1}th collaboration milestone!"
            
            # Add personal touch to title for special achievements
            if badge.rarity in [BadgeRarity.EPIC, BadgeRarity.LEGENDARY]:
                badge.special_properties['personalized'] = True
                badge.special_properties['achievement_rank'] = self._calculate_achievement_rank(
                    user_id, badge
                )
        
        return badges
    
    def _calculate_achievement_rank(self, user_id: str, badge: GeneratedBadge) -> str:
        """Calculate user's rank for this achievement type"""
        # Simplified ranking - would compare against other users in real implementation
        if badge.rarity == BadgeRarity.LEGENDARY:
            return "Top 1%"
        elif badge.rarity == BadgeRarity.EPIC:
            return "Top 5%"
        elif badge.rarity == BadgeRarity.RARE:
            return "Top 15%"
        else:
            return "Top 50%"
    
    async def _apply_rarity_balancing(
        self,
        user_id: str,
        badges: List[GeneratedBadge]
    ) -> List[GeneratedBadge]:
        """Apply rarity balancing to maintain proper distribution"""
        # Count current rarity distribution for user
        user_badges = self.user_badge_history.get(user_id, [])
        current_distribution = {}
        
        for badge in user_badges:
            rarity = badge.rarity.value
            current_distribution[rarity] = current_distribution.get(rarity, 0) + 1
        
        # Adjust new badges if needed to maintain balance
        adjusted_badges = []
        for badge in badges:
            original_rarity = badge.rarity
            
            # Check if this rarity is over-represented
            rarity_count = current_distribution.get(original_rarity.value, 0)
            total_badges = len(user_badges)
            
            if total_badges > 10:  # Only balance after user has some badges
                current_percentage = (rarity_count / total_badges) * 100
                target_percentage = self.rarity_distribution.get(original_rarity.value, 20)
                
                # If over-represented, consider downgrading rarity
                if current_percentage > target_percentage * 1.5:
                    badge.rarity = self._get_lower_rarity(original_rarity)
                    badge.ai_insights['rarity_balanced'] = True
            
            adjusted_badges.append(badge)
        
        return adjusted_badges
    
    def _get_lower_rarity(self, rarity: BadgeRarity) -> BadgeRarity:
        """Get lower rarity level for balancing"""
        rarity_hierarchy = [
            BadgeRarity.COMMON,
            BadgeRarity.UNCOMMON,
            BadgeRarity.RARE,
            BadgeRarity.EPIC,
            BadgeRarity.LEGENDARY
        ]
        
        current_index = rarity_hierarchy.index(rarity)
        if current_index > 0:
            return rarity_hierarchy[current_index - 1]
        return rarity
    
    async def _generate_visual_attributes(self, badge: GeneratedBadge) -> Dict[str, Any]:
        """Generate visual attributes for badge"""
        visual_attributes = badge.visual_attributes.copy() if badge.visual_attributes else {}
        
        # Add rarity-based visual enhancements
        rarity_colors = {
            BadgeRarity.COMMON: '#8D6E63',      # Brown
            BadgeRarity.UNCOMMON: '#66BB6A',    # Green
            BadgeRarity.RARE: '#42A5F5',        # Blue
            BadgeRarity.EPIC: '#AB47BC',        # Purple
            BadgeRarity.LEGENDARY: '#FFB74D'    # Gold
        }
        
        visual_attributes.update({
            'primary_color': rarity_colors.get(badge.rarity, '#8D6E63'),
            'glow_effect': badge.rarity in [BadgeRarity.EPIC, BadgeRarity.LEGENDARY],
            'animation': badge.rarity == BadgeRarity.LEGENDARY,
            'border_style': 'solid' if badge.rarity == BadgeRarity.COMMON else 'gradient',
            'size_multiplier': 1.0 + (list(BadgeRarity).index(badge.rarity) * 0.1)
        })
        
        # Add type-specific visual elements
        type_icons = {
            BadgeType.ACHIEVEMENT: 'trophy',
            BadgeType.MILESTONE: 'flag',
            BadgeType.SKILL: 'star',
            BadgeType.COLLABORATION: 'group',
            BadgeType.QUALITY: 'diamond',
            BadgeType.CONSISTENCY: 'clock',
            BadgeType.INNOVATION: 'lightbulb',
            BadgeType.COMMUNITY: 'heart',
            BadgeType.SPECIAL_EVENT: 'fire'
        }
        
        visual_attributes['icon'] = type_icons.get(badge.badge_type, 'badge')
        
        return visual_attributes
    
    def _generate_badge_insights(
        self,
        template: Dict[str, Any],
        achievement_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI insights for badge achievement"""
        insights = {
            'achievement_significance': self._assess_achievement_significance(template),
            'user_performance_context': self._analyze_performance_context(achievement_analysis),
            'rarity_justification': self._justify_rarity(template),
            'improvement_impact': self._assess_improvement_impact(template, achievement_analysis)
        }
        
        return insights
    
    def _assess_achievement_significance(self, template: Dict[str, Any]) -> str:
        """Assess the significance of the achievement"""
        rarity = template['rarity']
        
        if rarity == BadgeRarity.LEGENDARY:
            return "Exceptional achievement - top tier performance"
        elif rarity == BadgeRarity.EPIC:
            return "Outstanding achievement - well above average"
        elif rarity == BadgeRarity.RARE:
            return "Notable achievement - demonstrates skill and dedication"
        elif rarity == BadgeRarity.UNCOMMON:
            return "Good achievement - shows consistent effort"
        else:
            return "Milestone achievement - important step in progression"
    
    def _analyze_performance_context(self, achievement_analysis: Dict[str, Any]) -> str:
        """Analyze performance context for the achievement"""
        content_uploads = achievement_analysis['content_metrics']['total_uploads']
        quality_rating = achievement_analysis['content_metrics']['avg_quality_rating']
        
        if content_uploads > 100 and quality_rating > 4.0:
            return "High-volume, high-quality creator"
        elif quality_rating > 4.5:
            return "Quality-focused creator"
        elif content_uploads > 50:
            return "Prolific content creator"
        else:
            return "Developing creator with growth potential"
    
    def _justify_rarity(self, template: Dict[str, Any]) -> str:
        """Justify the rarity level of the badge"""
        criteria = template['criteria']
        rarity = template['rarity']
        
        difficulty_factors = []
        
        if 'content_uploads' in criteria and criteria['content_uploads'] > 50:
            difficulty_factors.append("high volume requirement")
        
        if 'avg_quality' in criteria and criteria['avg_quality'] > 4.0:
            difficulty_factors.append("high quality standard")
        
        if 'activity_streak' in criteria and criteria['activity_streak'] > 30:
            difficulty_factors.append("long-term consistency")
        
        if difficulty_factors:
            return f"Rarity justified by: {', '.join(difficulty_factors)}"
        else:
            return "Standard achievement criteria"
    
    def _assess_improvement_impact(
        self,
        template: Dict[str, Any],
        achievement_analysis: Dict[str, Any]
    ) -> str:
        """Assess the impact of this achievement on user improvement"""
        badge_type = template['type']
        
        if badge_type == BadgeType.QUALITY:
            return "Reinforces focus on content quality and craftsmanship"
        elif badge_type == BadgeType.COLLABORATION:
            return "Encourages teamwork and networking skills"
        elif badge_type == BadgeType.CONSISTENCY:
            return "Builds habits and sustainable content creation practices"
        elif badge_type == BadgeType.INNOVATION:
            return "Promotes creative exploration and thought leadership"
        else:
            return "Contributes to overall creator development and motivation"
    
    async def _predict_next_achievements(
        self,
        user_id: str,
        achievement_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Predict next achievable badges for user"""
        next_achievements = []
        
        progress = achievement_analysis['achievement_progress']
        
        # Check content milestones
        content_progress = progress['content_milestones']
        if content_progress['next_milestone']:
            next_achievements.append({
                'type': 'content_milestone',
                'target': content_progress['next_milestone'],
                'current': content_progress['current_value'],
                'progress_percentage': content_progress['progress_to_next'],
                'estimated_badge': 'Content Creator Badge'
            })
        
        # Check quality achievements
        quality_progress = progress['quality_achievements']
        if quality_progress['next_threshold']:
            next_achievements.append({
                'type': 'quality_achievement',
                'target': quality_progress['next_threshold'],
                'current': quality_progress['current_value'],
                'progress_percentage': quality_progress['progress_to_next'],
                'estimated_badge': 'Quality Master Badge'
            })
        
        return next_achievements[:3]  # Return top 3 next achievements
    
    async def _get_badge_collection_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's badge collection statistics"""
        user_badges = self.user_badge_history.get(user_id, [])
        
        if not user_badges:
            return {'total_badges': 0, 'total_points': 0}
        
        # Count by type
        type_counts = {}
        for badge in user_badges:
            badge_type = badge.badge_type.value
            type_counts[badge_type] = type_counts.get(badge_type, 0) + 1
        
        # Count by rarity
        rarity_counts = {}
        for badge in user_badges:
            rarity = badge.rarity.value
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        # Calculate total points
        total_points = sum(badge.points_awarded for badge in user_badges)
        
        # Find rarest badge
        rarest_badge = max(user_badges, key=lambda b: list(BadgeRarity).index(b.rarity))
        
        return {
            'total_badges': len(user_badges),
            'total_points': total_points,
            'badges_by_type': type_counts,
            'badges_by_rarity': rarity_counts,
            'rarest_badge': {
                'title': rarest_badge.title,
                'rarity': rarest_badge.rarity.value,
                'unlock_date': rarest_badge.unlock_date.isoformat()
            },
            'collection_completion_percentage': self._calculate_collection_completion(user_badges)
        }
    
    def _calculate_collection_completion(self, user_badges: List[GeneratedBadge]) -> float:
        """Calculate collection completion percentage"""
        total_possible_badges = len(self.badge_templates)
        unique_badge_types = len(set(badge.badge_id.split('_')[0] for badge in user_badges))
        
        return (unique_badge_types / total_possible_badges) * 100 if total_possible_badges > 0 else 0
    
    def _serialize_badge(self, badge: GeneratedBadge) -> Dict[str, Any]:
        """Serialize badge for JSON response"""
        return {
            'badge_id': badge.badge_id,
            'title': badge.title,
            'description': badge.description,
            'type': badge.badge_type.value,
            'rarity': badge.rarity.value,
            'points_awarded': badge.points_awarded,
            'unlock_date': badge.unlock_date.isoformat(),
            'visual_attributes': badge.visual_attributes,
            'special_properties': badge.special_properties,
            'ai_insights': badge.ai_insights
        }
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide badge analytics"""
        total_users = len(self.user_badge_history)
        total_badges = sum(len(badges) for badges in self.user_badge_history.values())
        
        # Calculate rarity distribution
        rarity_distribution = {}
        for badges in self.user_badge_history.values():
            for badge in badges:
                rarity = badge.rarity.value
                rarity_distribution[rarity] = rarity_distribution.get(rarity, 0) + 1
        
        return {
            'total_users_with_badges': total_users,
            'total_badges_awarded': total_badges,
            'average_badges_per_user': total_badges / total_users if total_users > 0 else 0,
            'rarity_distribution': rarity_distribution,
            'most_popular_badge_types': self._get_most_popular_badge_types(),
            'system_status': 'operational',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_most_popular_badge_types(self) -> Dict[str, int]:
        """Get most popular badge types"""
        type_counts = {}
        
        for badges in self.user_badge_history.values():
            for badge in badges:
                badge_type = badge.badge_type.value
                type_counts[badge_type] = type_counts.get(badge_type, 0) + 1
        
        # Sort by popularity
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_types[:5])  # Return top 5

# Export classes
__all__ = [
    'BadgeGenerator',
    'BadgeConfig',
    'GeneratedBadge',
    'BadgeType',
    'BadgeRarity'
]