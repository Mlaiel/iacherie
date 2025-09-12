"""
Milestone Celebration Tracker - Enterprise Achievement & Milestone Celebration System

This module implements comprehensive milestone celebration tracking for the Ainflue platform,
managing achievement celebrations, milestone recognition, and automated celebration campaigns.

Author: Fahed Mlaiel
Role: Lead Dev IA + Gamification Engineer + Community Manager + Marketing Automation
Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MilestoneType(Enum):
    """Types of milestones to celebrate"""
    FOLLOWER_MILESTONE = "follower_milestone"
    CONTENT_MILESTONE = "content_milestone"
    ENGAGEMENT_MILESTONE = "engagement_milestone"
    REVENUE_MILESTONE = "revenue_milestone"
    COLLABORATION_MILESTONE = "collaboration_milestone"
    QUALITY_MILESTONE = "quality_milestone"
    STREAK_MILESTONE = "streak_milestone"
    ANNIVERSARY_MILESTONE = "anniversary_milestone"
    ACHIEVEMENT_MILESTONE = "achievement_milestone"
    PLATFORM_MILESTONE = "platform_milestone"

class CelebrationType(Enum):
    """Types of celebration campaigns"""
    PERSONAL_CELEBRATION = "personal_celebration"
    COMMUNITY_SHOUTOUT = "community_shoutout"
    EXCLUSIVE_REWARD = "exclusive_reward"
    BADGE_CEREMONY = "badge_ceremony"
    LEADERBOARD_FEATURE = "leaderboard_feature"
    SOCIAL_AMPLIFICATION = "social_amplification"
    PREMIUM_UNLOCK = "premium_unlock"
    COLLABORATION_BOOST = "collaboration_boost"

class CelebrationStatus(Enum):
    """Status of celebration campaigns"""
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Milestone:
    """Milestone definition"""
    milestone_id: str
    milestone_type: MilestoneType
    name: str
    description: str
    threshold_value: float
    threshold_unit: str
    rarity_score: float  # 0-1, how rare this milestone is
    celebration_config: Dict[str, Any]
    badge_design: Optional[str]
    reward_points: int
    social_share_template: str
    created_at: datetime

@dataclass
class UserMilestone:
    """User milestone achievement"""
    user_milestone_id: str
    user_id: str
    milestone_id: str
    achieved_at: datetime
    achieved_value: float
    celebration_status: CelebrationStatus
    celebration_campaigns: List[str]
    social_shares: int
    community_reactions: Dict[str, int]
    impact_score: float
    celebration_metrics: Dict[str, Any]

@dataclass
class CelebrationCampaign:
    """Celebration campaign for milestone achievement"""
    campaign_id: str
    user_id: str
    milestone_id: str
    celebration_type: CelebrationType
    campaign_config: Dict[str, Any]
    launch_time: datetime
    duration: timedelta
    status: CelebrationStatus
    engagement_metrics: Dict[str, Any]
    success_score: float
    audience_reach: int
    created_at: datetime

class MilestoneCelebrationTracker:
    """
    Enterprise milestone celebration tracking system for Ainflue platform.
    
    Features:
    - Automated milestone detection
    - Personalized celebration campaigns
    - Social amplification strategies
    - Community engagement optimization
    - Achievement badge management
    - Celebration impact analytics
    - Cross-platform celebration sync
    - Influencer milestone highlighting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize milestone celebration tracker"""
        self.config = config or {}
        self.milestones: Dict[str, Milestone] = {}
        self.user_milestones: Dict[str, List[UserMilestone]] = defaultdict(list)
        self.celebration_campaigns: List[CelebrationCampaign] = []
        self.user_progress: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.celebration_templates = {}
        
        # Initialize tracking system
        self._initialize_milestone_system()
        logger.info("Milestone Celebration Tracker initialized")
    
    def _initialize_milestone_system(self):
        """Initialize milestone tracking system"""
        try:
            # Setup default milestones
            self._setup_default_milestones()
            
            # Initialize celebration templates
            self._setup_celebration_templates()
            
            # Setup tracking algorithms
            self._setup_milestone_detection()
            
            logger.info("Milestone system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize milestone system: {e}")
            raise
    
    def _setup_default_milestones(self):
        """Setup default milestone definitions"""
        default_milestones = [
            # Follower milestones
            {
                "milestone_type": MilestoneType.FOLLOWER_MILESTONE,
                "name": "First Hundred",
                "description": "Reached 100 followers!",
                "threshold_value": 100,
                "threshold_unit": "followers",
                "rarity_score": 0.3,
                "reward_points": 500,
                "badge_design": "first_hundred_badge",
                "social_share_template": "🎉 Just hit 100 followers! Thank you for joining my journey! #AinflueMilestone #CreatorLife"
            },
            {
                "milestone_type": MilestoneType.FOLLOWER_MILESTONE,
                "name": "Thousand Club",
                "description": "Reached 1,000 followers!",
                "threshold_value": 1000,
                "threshold_unit": "followers",
                "rarity_score": 0.6,
                "reward_points": 2000,
                "badge_design": "thousand_club_badge",
                "social_share_template": "🚀 1K followers! This community is amazing! #ThousandClub #AinflueMilestone"
            },
            {
                "milestone_type": MilestoneType.FOLLOWER_MILESTONE,
                "name": "Ten Thousand Strong",
                "description": "Reached 10,000 followers!",
                "threshold_value": 10000,
                "threshold_unit": "followers",
                "rarity_score": 0.85,
                "reward_points": 10000,
                "badge_design": "ten_k_badge",
                "social_share_template": "🎊 10K FOLLOWERS! You all are incredible! This is just the beginning! #10KStrong #AinflueMilestone"
            },
            # Content milestones
            {
                "milestone_type": MilestoneType.CONTENT_MILESTONE,
                "name": "Content Creator",
                "description": "Published 10 pieces of content!",
                "threshold_value": 10,
                "threshold_unit": "content_pieces",
                "rarity_score": 0.2,
                "reward_points": 200,
                "badge_design": "content_creator_badge",
                "social_share_template": "📝 Just published my 10th piece of content! The creative journey continues! #ContentCreator"
            },
            {
                "milestone_type": MilestoneType.CONTENT_MILESTONE,
                "name": "Prolific Producer",
                "description": "Published 100 pieces of content!",
                "threshold_value": 100,
                "threshold_unit": "content_pieces",
                "rarity_score": 0.7,
                "reward_points": 3000,
                "badge_design": "prolific_producer_badge",
                "social_share_template": "🏆 100 pieces of content published! Consistency pays off! #ProlificProducer #ContentMilestone"
            },
            # Engagement milestones
            {
                "milestone_type": MilestoneType.ENGAGEMENT_MILESTONE,
                "name": "Viral Sensation",
                "description": "Achieved 1M total views!",
                "threshold_value": 1000000,
                "threshold_unit": "total_views",
                "rarity_score": 0.9,
                "reward_points": 20000,
                "badge_design": "viral_sensation_badge",
                "social_share_template": "🔥 1 MILLION VIEWS! Thank you for watching and engaging! #ViralSensation #1MViews"
            },
            # Revenue milestones
            {
                "milestone_type": MilestoneType.REVENUE_MILESTONE,
                "name": "First Dollar",
                "description": "Earned your first dollar!",
                "threshold_value": 1,
                "threshold_unit": "dollars",
                "rarity_score": 0.4,
                "reward_points": 1000,
                "badge_design": "first_dollar_badge",
                "social_share_template": "💰 First dollar earned as a creator! The journey to financial freedom begins! #FirstDollar"
            },
            {
                "milestone_type": MilestoneType.REVENUE_MILESTONE,
                "name": "Thousand Dollar Club",
                "description": "Earned $1,000!",
                "threshold_value": 1000,
                "threshold_unit": "dollars",
                "rarity_score": 0.8,
                "reward_points": 5000,
                "badge_design": "thousand_dollar_badge",
                "social_share_template": "🎯 $1,000 earned! Proving that passion can pay! #ThousandDollarClub #CreatorEconomy"
            },
            # Collaboration milestones
            {
                "milestone_type": MilestoneType.COLLABORATION_MILESTONE,
                "name": "Team Player",
                "description": "Completed first collaboration!",
                "threshold_value": 1,
                "threshold_unit": "collaborations",
                "rarity_score": 0.3,
                "reward_points": 750,
                "badge_design": "team_player_badge",
                "social_share_template": "🤝 First collaboration complete! Amazing what we can achieve together! #TeamPlayer #Collaboration"
            },
            # Anniversary milestones
            {
                "milestone_type": MilestoneType.ANNIVERSARY_MILESTONE,
                "name": "One Year Strong",
                "description": "One year as an Ainflue creator!",
                "threshold_value": 365,
                "threshold_unit": "days",
                "rarity_score": 0.6,
                "reward_points": 3650,
                "badge_design": "one_year_badge",
                "social_share_template": "🎂 One year on Ainflue! What an incredible journey it's been! #OneYear #Anniversary"
            }
        ]
        
        for milestone_data in default_milestones:
            milestone = Milestone(
                milestone_id=str(uuid.uuid4()),
                milestone_type=milestone_data["milestone_type"],
                name=milestone_data["name"],
                description=milestone_data["description"],
                threshold_value=milestone_data["threshold_value"],
                threshold_unit=milestone_data["threshold_unit"],
                rarity_score=milestone_data["rarity_score"],
                celebration_config=self._get_default_celebration_config(milestone_data["milestone_type"]),
                badge_design=milestone_data.get("badge_design"),
                reward_points=milestone_data["reward_points"],
                social_share_template=milestone_data["social_share_template"],
                created_at=datetime.now()
            )
            self.milestones[milestone.milestone_id] = milestone
    
    def _get_default_celebration_config(self, milestone_type: MilestoneType) -> Dict[str, Any]:
        """Get default celebration configuration for milestone type"""
        base_config = {
            "auto_celebrate": True,
            "social_amplification": True,
            "community_notification": True,
            "reward_multiplier": 1.0
        }
        
        if milestone_type == MilestoneType.FOLLOWER_MILESTONE:
            base_config.update({
                "celebration_types": ["personal_celebration", "community_shoutout", "leaderboard_feature"],
                "duration_hours": 24,
                "highlight_community": True
            })
        elif milestone_type == MilestoneType.REVENUE_MILESTONE:
            base_config.update({
                "celebration_types": ["personal_celebration", "exclusive_reward", "premium_unlock"],
                "duration_hours": 48,
                "highlight_achievement": True
            })
        elif milestone_type == MilestoneType.COLLABORATION_MILESTONE:
            base_config.update({
                "celebration_types": ["personal_celebration", "collaboration_boost", "social_amplification"],
                "duration_hours": 12,
                "promote_collaboration": True
            })
        else:
            base_config.update({
                "celebration_types": ["personal_celebration", "badge_ceremony"],
                "duration_hours": 24
            })
        
        return base_config
    
    def _setup_celebration_templates(self):
        """Setup celebration campaign templates"""
        self.celebration_templates = {
            CelebrationType.PERSONAL_CELEBRATION: {
                "notification_title": "🎉 Milestone Achieved!",
                "notification_message": "Congratulations on reaching {milestone_name}! {description}",
                "reward_message": "You've earned {reward_points} points for this achievement!",
                "call_to_action": "Share your success with the community!"
            },
            CelebrationType.COMMUNITY_SHOUTOUT: {
                "post_template": "🌟 Community Spotlight: @{username} just achieved {milestone_name}! {description} Let's celebrate together! #CommunityWin",
                "feature_duration": 24,  # hours
                "engagement_boost": 1.5
            },
            CelebrationType.EXCLUSIVE_REWARD: {
                "reward_types": ["premium_trial", "exclusive_content", "special_badge", "bonus_points"],
                "reward_message": "Here's an exclusive reward for your amazing achievement!",
                "validity_days": 30
            },
            CelebrationType.BADGE_CEREMONY: {
                "ceremony_message": "🏆 Badge Ceremony: You've earned the {badge_name} badge for {milestone_name}!",
                "badge_showcase": True,
                "profile_highlight": True
            },
            CelebrationType.LEADERBOARD_FEATURE: {
                "feature_position": "milestone_achievers",
                "feature_duration": 72,  # hours
                "special_highlighting": True
            },
            CelebrationType.SOCIAL_AMPLIFICATION: {
                "platforms": ["instagram", "twitter", "linkedin", "tiktok"],
                "amplification_factor": 2.0,
                "hashtag_boost": True
            },
            CelebrationType.PREMIUM_UNLOCK: {
                "unlock_features": ["advanced_analytics", "premium_tools", "exclusive_content"],
                "trial_duration": 14,  # days
                "permanent_benefits": ["milestone_badge", "profile_enhancement"]
            }
        }
    
    def _setup_milestone_detection(self):
        """Setup milestone detection algorithms"""
        self.detection_config = {
            "check_frequency": 300,  # seconds
            "batch_size": 100,  # users to check per batch
            "detection_sensitivity": 0.95,  # accuracy threshold
            "auto_celebration_threshold": 0.8  # rarity threshold for auto-celebration
        }
    
    async def track_user_progress(self, user_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track user progress towards milestones
        
        Args:
            user_id: User identifier
            metrics: Current user metrics
            
        Returns:
            Progress tracking results with milestone achievements
        """
        try:
            # Update user progress
            self._update_user_progress(user_id, metrics)
            
            # Check for milestone achievements
            achievements = await self._check_milestone_achievements(user_id, metrics)
            
            # Process new achievements
            celebration_results = []
            for achievement in achievements:
                celebration_result = await self._process_milestone_achievement(user_id, achievement)
                celebration_results.append(celebration_result)
            
            # Calculate progress towards upcoming milestones
            upcoming_milestones = await self._calculate_upcoming_milestones(user_id, metrics)
            
            result = {
                "user_id": user_id,
                "new_achievements": len(achievements),
                "achievements": achievements,
                "celebrations_launched": len(celebration_results),
                "celebration_results": celebration_results,
                "upcoming_milestones": upcoming_milestones,
                "progress_summary": self._get_progress_summary(user_id),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Progress tracked for {user_id}: {len(achievements)} new achievements")
            return result
            
        except Exception as e:
            logger.error(f"Failed to track user progress for {user_id}: {e}")
            return {"error": str(e)}
    
    def _update_user_progress(self, user_id: str, metrics: Dict[str, Any]):
        """Update user progress tracking"""
        current_progress = self.user_progress[user_id]
        
        # Map metrics to milestone types
        metric_mappings = {
            "followers": "followers",
            "content_count": "content_pieces",
            "total_views": "total_views",
            "total_revenue": "dollars",
            "collaborations": "collaborations",
            "days_active": "days"
        }
        
        for metric_key, milestone_unit in metric_mappings.items():
            if metric_key in metrics:
                current_progress[milestone_unit] = metrics[metric_key]
        
        # Update timestamp
        current_progress["last_updated"] = datetime.now()
    
    async def _check_milestone_achievements(self, user_id: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for milestone achievements"""
        achievements = []
        user_progress = self.user_progress[user_id]
        
        # Get user's existing achievements to avoid duplicates
        existing_achievements = {um.milestone_id for um in self.user_milestones[user_id]}
        
        for milestone_id, milestone in self.milestones.items():
            # Skip if already achieved
            if milestone_id in existing_achievements:
                continue
            
            # Check if threshold is met
            current_value = user_progress.get(milestone.threshold_unit, 0)
            if current_value >= milestone.threshold_value:
                achievement = {
                    "milestone_id": milestone_id,
                    "milestone": milestone,
                    "achieved_value": current_value,
                    "achieved_at": datetime.now()
                }
                achievements.append(achievement)
        
        return achievements
    
    async def _process_milestone_achievement(self, user_id: str, achievement: Dict[str, Any]) -> Dict[str, Any]:
        """Process milestone achievement and launch celebrations"""
        milestone = achievement["milestone"]
        
        # Create user milestone record
        user_milestone = UserMilestone(
            user_milestone_id=str(uuid.uuid4()),
            user_id=user_id,
            milestone_id=achievement["milestone_id"],
            achieved_at=achievement["achieved_at"],
            achieved_value=achievement["achieved_value"],
            celebration_status=CelebrationStatus.PLANNED,
            celebration_campaigns=[],
            social_shares=0,
            community_reactions={},
            impact_score=0.0,
            celebration_metrics={}
        )
        
        self.user_milestones[user_id].append(user_milestone)
        
        # Launch celebration campaigns
        campaigns = await self._launch_celebration_campaigns(user_id, milestone, user_milestone)
        
        # Update user milestone with campaign IDs
        user_milestone.celebration_campaigns = [c.campaign_id for c in campaigns]
        user_milestone.celebration_status = CelebrationStatus.ACTIVE
        
        return {
            "user_milestone_id": user_milestone.user_milestone_id,
            "milestone_name": milestone.name,
            "campaigns_launched": len(campaigns),
            "campaign_types": [c.celebration_type.value for c in campaigns],
            "estimated_reach": sum(c.audience_reach for c in campaigns),
            "reward_points": milestone.reward_points
        }
    
    async def _launch_celebration_campaigns(self, user_id: str, milestone: Milestone, user_milestone: UserMilestone) -> List[CelebrationCampaign]:
        """Launch celebration campaigns for milestone achievement"""
        campaigns = []
        celebration_config = milestone.celebration_config
        
        # Determine which celebration types to launch
        celebration_types = celebration_config.get("celebration_types", ["personal_celebration"])
        
        for celebration_type_str in celebration_types:
            try:
                celebration_type = CelebrationType(celebration_type_str)
                campaign = await self._create_celebration_campaign(
                    user_id, milestone, user_milestone, celebration_type
                )
                campaigns.append(campaign)
                self.celebration_campaigns.append(campaign)
                
            except ValueError:
                logger.warning(f"Unknown celebration type: {celebration_type_str}")
                continue
        
        return campaigns
    
    async def _create_celebration_campaign(self, user_id: str, milestone: Milestone, user_milestone: UserMilestone, celebration_type: CelebrationType) -> CelebrationCampaign:
        """Create specific celebration campaign"""
        template = self.celebration_templates[celebration_type]
        
        # Calculate campaign reach based on milestone rarity and user stats
        base_reach = 100  # Base audience reach
        rarity_multiplier = milestone.rarity_score * 10
        audience_reach = int(base_reach * rarity_multiplier)
        
        # Configure campaign based on type
        campaign_config = self._configure_celebration_campaign(celebration_type, milestone, template)
        
        # Determine campaign duration
        duration_hours = milestone.celebration_config.get("duration_hours", 24)
        duration = timedelta(hours=duration_hours)
        
        campaign = CelebrationCampaign(
            campaign_id=str(uuid.uuid4()),
            user_id=user_id,
            milestone_id=milestone.milestone_id,
            celebration_type=celebration_type,
            campaign_config=campaign_config,
            launch_time=datetime.now(),
            duration=duration,
            status=CelebrationStatus.ACTIVE,
            engagement_metrics={},
            success_score=0.0,
            audience_reach=audience_reach,
            created_at=datetime.now()
        )
        
        # Simulate campaign execution
        await self._execute_celebration_campaign(campaign)
        
        return campaign
    
    def _configure_celebration_campaign(self, celebration_type: CelebrationType, milestone: Milestone, template: Dict[str, Any]) -> Dict[str, Any]:
        """Configure celebration campaign based on type and milestone"""
        config = template.copy()
        
        # Add milestone-specific configuration
        config.update({
            "milestone_name": milestone.name,
            "milestone_description": milestone.description,
            "reward_points": milestone.reward_points,
            "badge_design": milestone.badge_design,
            "social_share_template": milestone.social_share_template,
            "rarity_score": milestone.rarity_score
        })
        
        # Type-specific enhancements
        if celebration_type == CelebrationType.COMMUNITY_SHOUTOUT:
            config["engagement_boost"] = 1.0 + milestone.rarity_score
        elif celebration_type == CelebrationType.EXCLUSIVE_REWARD:
            config["reward_value"] = milestone.reward_points * milestone.rarity_score
        elif celebration_type == CelebrationType.SOCIAL_AMPLIFICATION:
            config["amplification_factor"] = 1.0 + (milestone.rarity_score * 2)
        
        return config
    
    async def _execute_celebration_campaign(self, campaign: CelebrationCampaign):
        """Execute celebration campaign (simulate for now)"""
        # This would integrate with actual notification, social media, and reward systems
        
        execution_result = {
            "notifications_sent": campaign.audience_reach,
            "social_posts_created": 1 if campaign.celebration_type == CelebrationType.SOCIAL_AMPLIFICATION else 0,
            "rewards_distributed": 1 if campaign.celebration_type == CelebrationType.EXCLUSIVE_REWARD else 0,
            "community_features": 1 if campaign.celebration_type == CelebrationType.COMMUNITY_SHOUTOUT else 0,
            "execution_time": datetime.now().isoformat()
        }
        
        # Simulate engagement metrics
        campaign.engagement_metrics = {
            "views": int(campaign.audience_reach * 0.8),
            "clicks": int(campaign.audience_reach * 0.3),
            "shares": int(campaign.audience_reach * 0.1),
            "positive_reactions": int(campaign.audience_reach * 0.4),
            "execution_result": execution_result
        }
        
        # Calculate success score
        campaign.success_score = self._calculate_campaign_success_score(campaign)
    
    def _calculate_campaign_success_score(self, campaign: CelebrationCampaign) -> float:
        """Calculate celebration campaign success score"""
        metrics = campaign.engagement_metrics
        
        # Calculate engagement rate
        views = metrics.get("views", 0)
        total_engagement = metrics.get("clicks", 0) + metrics.get("shares", 0) + metrics.get("positive_reactions", 0)
        engagement_rate = total_engagement / max(views, 1)
        
        # Factor in campaign reach and type effectiveness
        reach_factor = min(campaign.audience_reach / 1000, 1.0)  # Normalize reach
        type_effectiveness = 0.8  # Base effectiveness for all types
        
        # Calculate overall success score
        success_score = (engagement_rate * 0.6) + (reach_factor * 0.3) + (type_effectiveness * 0.1)
        
        return min(success_score, 1.0)
    
    async def _calculate_upcoming_milestones(self, user_id: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate progress towards upcoming milestones"""
        upcoming = []
        user_progress = self.user_progress[user_id]
        
        # Get user's existing achievements
        existing_achievements = {um.milestone_id for um in self.user_milestones[user_id]}
        
        for milestone_id, milestone in self.milestones.items():
            # Skip if already achieved
            if milestone_id in existing_achievements:
                continue
            
            current_value = user_progress.get(milestone.threshold_unit, 0)
            
            # Only include milestones that are reasonably close
            if current_value >= milestone.threshold_value * 0.1:  # At least 10% progress
                progress_percentage = (current_value / milestone.threshold_value) * 100
                remaining_value = milestone.threshold_value - current_value
                
                upcoming.append({
                    "milestone_id": milestone_id,
                    "name": milestone.name,
                    "description": milestone.description,
                    "current_value": current_value,
                    "target_value": milestone.threshold_value,
                    "progress_percentage": min(progress_percentage, 100),
                    "remaining_value": max(remaining_value, 0),
                    "unit": milestone.threshold_unit,
                    "reward_points": milestone.reward_points,
                    "rarity_score": milestone.rarity_score
                })
        
        # Sort by progress percentage (descending)
        upcoming.sort(key=lambda x: x["progress_percentage"], reverse=True)
        
        return upcoming[:10]  # Return top 10 closest milestones
    
    def _get_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user progress summary"""
        user_milestones = self.user_milestones[user_id]
        user_progress = self.user_progress[user_id]
        
        # Calculate statistics
        total_achievements = len(user_milestones)
        total_points_earned = sum(
            self.milestones[um.milestone_id].reward_points 
            for um in user_milestones 
            if um.milestone_id in self.milestones
        )
        
        # Achievement breakdown by type
        achievement_breakdown = defaultdict(int)
        for um in user_milestones:
            if um.milestone_id in self.milestones:
                milestone_type = self.milestones[um.milestone_id].milestone_type.value
                achievement_breakdown[milestone_type] += 1
        
        # Rarity distribution
        rare_achievements = len([
            um for um in user_milestones 
            if um.milestone_id in self.milestones and self.milestones[um.milestone_id].rarity_score >= 0.7
        ])
        
        return {
            "total_achievements": total_achievements,
            "total_points_earned": total_points_earned,
            "rare_achievements": rare_achievements,
            "achievement_breakdown": dict(achievement_breakdown),
            "current_metrics": dict(user_progress),
            "last_achievement": user_milestones[-1].achieved_at.isoformat() if user_milestones else None
        }
    
    async def analyze_celebration_performance(self, time_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Analyze celebration campaign performance
        
        Args:
            time_range: Optional time range for analysis
            
        Returns:
            Comprehensive celebration performance analysis
        """
        try:
            if time_range is None:
                end_time = datetime.now()
                start_time = end_time - timedelta(days=30)
                time_range = (start_time, end_time)
            
            # Filter campaigns in time range
            campaigns_in_range = [
                c for c in self.celebration_campaigns
                if time_range[0] <= c.created_at <= time_range[1]
            ]
            
            analysis = {
                "time_range": {
                    "start": time_range[0].isoformat(),
                    "end": time_range[1].isoformat()
                },
                "campaign_statistics": self._analyze_campaign_statistics(campaigns_in_range),
                "milestone_achievement_stats": self._analyze_milestone_achievements(time_range),
                "celebration_effectiveness": self._analyze_celebration_effectiveness(campaigns_in_range),
                "user_engagement_impact": self._analyze_user_engagement_impact(campaigns_in_range),
                "platform_celebration_health": self._assess_celebration_health(),
                "recommendations": self._generate_celebration_recommendations()
            }
            
            logger.info(f"Celebration performance analyzed for {len(campaigns_in_range)} campaigns")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze celebration performance: {e}")
            return {"error": str(e)}
    
    def _analyze_campaign_statistics(self, campaigns: List[CelebrationCampaign]) -> Dict[str, Any]:
        """Analyze campaign statistics"""
        if not campaigns:
            return {"total_campaigns": 0}
        
        total_campaigns = len(campaigns)
        
        # Campaign type distribution
        type_distribution = defaultdict(int)
        for campaign in campaigns:
            type_distribution[campaign.celebration_type.value] += 1
        
        # Average success scores
        avg_success_score = sum(c.success_score for c in campaigns) / total_campaigns
        
        # Total reach
        total_reach = sum(c.audience_reach for c in campaigns)
        
        # Campaign status distribution
        status_distribution = defaultdict(int)
        for campaign in campaigns:
            status_distribution[campaign.status.value] += 1
        
        return {
            "total_campaigns": total_campaigns,
            "type_distribution": dict(type_distribution),
            "average_success_score": avg_success_score,
            "total_audience_reach": total_reach,
            "status_distribution": dict(status_distribution)
        }
    
    def _analyze_milestone_achievements(self, time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Analyze milestone achievements in time range"""
        achievements_in_range = []
        
        for user_milestones in self.user_milestones.values():
            for um in user_milestones:
                if time_range[0] <= um.achieved_at <= time_range[1]:
                    achievements_in_range.append(um)
        
        if not achievements_in_range:
            return {"total_achievements": 0}
        
        # Achievement type distribution
        type_distribution = defaultdict(int)
        for um in achievements_in_range:
            if um.milestone_id in self.milestones:
                milestone_type = self.milestones[um.milestone_id].milestone_type.value
                type_distribution[milestone_type] += 1
        
        # Rarity distribution
        rarity_distribution = {"common": 0, "rare": 0, "legendary": 0}
        for um in achievements_in_range:
            if um.milestone_id in self.milestones:
                rarity = self.milestones[um.milestone_id].rarity_score
                if rarity < 0.5:
                    rarity_distribution["common"] += 1
                elif rarity < 0.8:
                    rarity_distribution["rare"] += 1
                else:
                    rarity_distribution["legendary"] += 1
        
        return {
            "total_achievements": len(achievements_in_range),
            "type_distribution": dict(type_distribution),
            "rarity_distribution": rarity_distribution,
            "unique_achievers": len(set(um.user_id for um in achievements_in_range))
        }
    
    def _analyze_celebration_effectiveness(self, campaigns: List[CelebrationCampaign]) -> Dict[str, Any]:
        """Analyze celebration effectiveness by type"""
        if not campaigns:
            return {}
        
        effectiveness_by_type = defaultdict(list)
        for campaign in campaigns:
            effectiveness_by_type[campaign.celebration_type.value].append(campaign.success_score)
        
        # Calculate average effectiveness
        avg_effectiveness = {}
        for celebration_type, scores in effectiveness_by_type.items():
            avg_effectiveness[celebration_type] = sum(scores) / len(scores)
        
        # Find most and least effective types
        most_effective = max(avg_effectiveness.items(), key=lambda x: x[1]) if avg_effectiveness else None
        least_effective = min(avg_effectiveness.items(), key=lambda x: x[1]) if avg_effectiveness else None
        
        return {
            "effectiveness_by_type": avg_effectiveness,
            "most_effective_type": most_effective[0] if most_effective else None,
            "least_effective_type": least_effective[0] if least_effective else None,
            "overall_effectiveness": sum(avg_effectiveness.values()) / len(avg_effectiveness) if avg_effectiveness else 0
        }
    
    def _analyze_user_engagement_impact(self, campaigns: List[CelebrationCampaign]) -> Dict[str, Any]:
        """Analyze user engagement impact of celebrations"""
        if not campaigns:
            return {"total_engagement": 0}
        
        total_views = sum(c.engagement_metrics.get("views", 0) for c in campaigns)
        total_clicks = sum(c.engagement_metrics.get("clicks", 0) for c in campaigns)
        total_shares = sum(c.engagement_metrics.get("shares", 0) for c in campaigns)
        total_reactions = sum(c.engagement_metrics.get("positive_reactions", 0) for c in campaigns)
        
        overall_engagement_rate = (total_clicks + total_shares + total_reactions) / max(total_views, 1)
        
        return {
            "total_views": total_views,
            "total_clicks": total_clicks,
            "total_shares": total_shares,
            "total_reactions": total_reactions,
            "overall_engagement_rate": overall_engagement_rate,
            "average_campaign_engagement": overall_engagement_rate
        }
    
    def _assess_celebration_health(self) -> Dict[str, Any]:
        """Assess overall platform celebration health"""
        total_users_with_achievements = len(self.user_milestones)
        total_campaigns = len(self.celebration_campaigns)
        
        if total_campaigns == 0:
            return {"health_score": 0, "health_status": "inactive"}
        
        # Calculate health metrics
        avg_success_score = sum(c.success_score for c in self.celebration_campaigns) / total_campaigns
        active_campaigns = len([c for c in self.celebration_campaigns if c.status == CelebrationStatus.ACTIVE])
        
        # Health score calculation
        health_score = (
            avg_success_score * 0.6 +
            min(active_campaigns / 50, 1.0) * 0.4  # Normalize active campaigns
        )
        
        health_status = "excellent" if health_score > 0.8 else \
                       "good" if health_score > 0.6 else \
                       "fair" if health_score > 0.4 else "poor"
        
        return {
            "health_score": health_score,
            "health_status": health_status,
            "total_users_with_achievements": total_users_with_achievements,
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "average_success_score": avg_success_score
        }
    
    def _generate_celebration_recommendations(self) -> List[Dict[str, Any]]:
        """Generate celebration optimization recommendations"""
        recommendations = []
        
        # Analyze celebration effectiveness
        if self.celebration_campaigns:
            avg_success = sum(c.success_score for c in self.celebration_campaigns) / len(self.celebration_campaigns)
            
            if avg_success < 0.6:
                recommendations.append({
                    "type": "celebration_optimization",
                    "priority": "high",
                    "description": "Low celebration success rate - optimize campaign strategies",
                    "suggested_actions": [
                        "Personalize celebration messages",
                        "Improve timing of celebrations",
                        "Enhance reward offerings"
                    ]
                })
        
        # Check for milestone gaps
        follower_milestones = [m for m in self.milestones.values() if m.milestone_type == MilestoneType.FOLLOWER_MILESTONE]
        if len(follower_milestones) < 5:
            recommendations.append({
                "type": "milestone_expansion",
                "priority": "medium",
                "description": "Limited milestone variety - expand milestone types",
                "suggested_actions": [
                    "Add more follower milestone tiers",
                    "Create engagement-based milestones",
                    "Introduce creative achievement milestones"
                ]
            })
        
        return recommendations
    
    def get_user_milestones(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's milestone achievements"""
        user_milestones = self.user_milestones.get(user_id, [])
        return [asdict(um) for um in user_milestones]
    
    def get_milestone_definition(self, milestone_id: str) -> Optional[Dict[str, Any]]:
        """Get milestone definition"""
        milestone = self.milestones.get(milestone_id)
        return asdict(milestone) if milestone else None
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current milestone monitoring status"""
        return {
            "total_milestones": len(self.milestones),
            "total_users_tracked": len(self.user_progress),
            "total_achievements": sum(len(achievements) for achievements in self.user_milestones.values()),
            "active_celebrations": len([c for c in self.celebration_campaigns if c.status == CelebrationStatus.ACTIVE]),
            "last_updated": datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    async def test_milestone_celebration():
        """Test milestone celebration functionality"""
        tracker = MilestoneCelebrationTracker()
        
        # Test user progress tracking
        user_id = "test_user_001"
        metrics = {
            "followers": 150,
            "content_count": 8,
            "total_views": 5000,
            "total_revenue": 0,
            "collaborations": 0,
            "days_active": 45
        }
        
        result = await tracker.track_user_progress(user_id, metrics)
        print(f"Progress tracking result: {result}")
        
        # Simulate milestone achievement
        metrics.update({
            "followers": 1000,
            "content_count": 15
        })
        
        result = await tracker.track_user_progress(user_id, metrics)
        print(f"Milestone achievement result: {result}")
        
        # Test performance analysis
        performance = await tracker.analyze_celebration_performance()
        print(f"Celebration performance: {performance}")
        
        # Test user milestones retrieval
        milestones = tracker.get_user_milestones(user_id)
        print(f"User milestones: {milestones}")
        
        # Test monitoring status
        status = tracker.get_monitoring_status()
        print(f"Monitoring status: {status}")
    
    # Run test
    asyncio.run(test_milestone_celebration())