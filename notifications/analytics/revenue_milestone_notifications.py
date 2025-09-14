"""
🚀 REVENUE MILESTONE NOTIFICATIONS ENGINE
======================================
Enterprise-grade revenue milestone detection and celebration system for Ainflue Platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

FEATURES:
- Real-time revenue milestone detection
- Intelligent celebration notifications  
- Multi-channel delivery optimization
- AI-powered personalization
- Performance analytics integration
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class MilestoneType(Enum):
    """Types of revenue milestones"""
    FIRST_SALE = "first_sale"
    MONTHLY_TARGET = "monthly_target"
    YEARLY_TARGET = "yearly_target"
    MILESTONE_100 = "milestone_100"
    MILESTONE_1K = "milestone_1k"
    MILESTONE_10K = "milestone_10k"
    MILESTONE_100K = "milestone_100k"
    MILESTONE_1M = "milestone_1m"
    STREAK_ACHIEVEMENT = "streak_achievement"
    GROWTH_ACCELERATION = "growth_acceleration"

@dataclass
class RevenueMilestone:
    """Revenue milestone data structure"""
    milestone_id: str
    user_id: str
    milestone_type: MilestoneType
    amount: float
    currency: str
    achieved_at: datetime
    previous_milestone: Optional[str]
    growth_rate: float
    celebration_level: str
    metadata: Dict[str, Any]

class RevenueMilestoneEngine:
    """Enterprise Revenue Milestone Detection and Notification Engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the Revenue Milestone Engine"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Milestone thresholds configuration
        self.milestone_thresholds = {
            MilestoneType.FIRST_SALE: 0.01,
            MilestoneType.MILESTONE_100: 100.0,
            MilestoneType.MILESTONE_1K: 1000.0,
            MilestoneType.MILESTONE_10K: 10000.0,
            MilestoneType.MILESTONE_100K: 100000.0,
            MilestoneType.MILESTONE_1M: 1000000.0
        }
        
        # Celebration configurations
        self.celebration_configs = {
            'first_sale': {'emoji': '🎉', 'level': 'celebration'},
            'milestone_100': {'emoji': '💯', 'level': 'achievement'},
            'milestone_1k': {'emoji': '🚀', 'level': 'major'},
            'milestone_10k': {'emoji': '⭐', 'level': 'super'},
            'milestone_100k': {'emoji': '💎', 'level': 'legendary'},
            'milestone_1m': {'emoji': '👑', 'level': 'epic'}
        }
        
        self.logger.info("RevenueMilestoneEngine initialized successfully")

    async def celebrate_milestone(self, context) -> Dict[str, Any]:
        """Celebrate a revenue milestone achievement"""
        try:
            user_id = context.user_id
            revenue_data = context.metadata.get('revenue_data', {})
            
            # Detect achieved milestones
            milestones = await self._detect_milestones(user_id, revenue_data)
            
            if not milestones:
                return {
                    'status': 'no_milestones',
                    'message': 'No new milestones detected'
                }
            
            # Generate celebration notifications
            celebration_results = []
            for milestone in milestones:
                celebration = await self._generate_celebration(milestone, context)
                celebration_results.append(celebration)
            
            return {
                'status': 'success',
                'milestones_celebrated': len(milestones),
                'celebrations': celebration_results,
                'notification_id': f"revenue_milestone_{user_id}_{datetime.now().timestamp()}"
            }
            
        except Exception as e:
            self.logger.error(f"Error celebrating milestone: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _detect_milestones(self, user_id: str, revenue_data: Dict[str, Any]) -> List[RevenueMilestone]:
        """Detect achieved revenue milestones"""
        milestones = []
        current_revenue = revenue_data.get('total_revenue', 0.0)
        previous_revenue = revenue_data.get('previous_total', 0.0)
        
        # Check each milestone threshold
        for milestone_type, threshold in self.milestone_thresholds.items():
            if current_revenue >= threshold and previous_revenue < threshold:
                milestone = RevenueMilestone(
                    milestone_id=f"{user_id}_{milestone_type.value}_{datetime.now().timestamp()}",
                    user_id=user_id,
                    milestone_type=milestone_type,
                    amount=current_revenue,
                    currency=revenue_data.get('currency', 'USD'),
                    achieved_at=datetime.now(),
                    previous_milestone=None,
                    growth_rate=self._calculate_growth_rate(current_revenue, previous_revenue),
                    celebration_level=self.celebration_configs.get(milestone_type.value, {}).get('level', 'standard'),
                    metadata=revenue_data
                )
                milestones.append(milestone)
        
        return milestones
    
    async def _generate_celebration(self, milestone: RevenueMilestone, context) -> Dict[str, Any]:
        """Generate personalized celebration notification"""
        config = self.celebration_configs.get(milestone.milestone_type.value, {})
        
        celebration = {
            'milestone_id': milestone.milestone_id,
            'title': f"🎉 Milestone Achieved: {milestone.milestone_type.value.replace('_', ' ').title()}!",
            'message': self._create_celebration_message(milestone),
            'emoji': config.get('emoji', '🎉'),
            'level': config.get('level', 'standard'),
            'amount': milestone.amount,
            'currency': milestone.currency,
            'growth_rate': milestone.growth_rate,
            'timestamp': milestone.achieved_at.isoformat(),
            'personalization_data': await self._get_personalization_data(milestone, context)
        }
        
        return celebration
    
    def _create_celebration_message(self, milestone: RevenueMilestone) -> str:
        """Create personalized celebration message"""
        messages = {
            MilestoneType.FIRST_SALE: f"Congratulations! You've made your first sale of {milestone.amount} {milestone.currency}! 🎉",
            MilestoneType.MILESTONE_100: f"Amazing! You've reached {milestone.amount} {milestone.currency} in total revenue! 💯",
            MilestoneType.MILESTONE_1K: f"Incredible milestone! {milestone.amount:,.0f} {milestone.currency} total revenue achieved! 🚀",
            MilestoneType.MILESTONE_10K: f"Outstanding achievement! {milestone.amount:,.0f} {milestone.currency} in total revenue! ⭐",
            MilestoneType.MILESTONE_100K: f"Legendary milestone! {milestone.amount:,.0f} {milestone.currency} total revenue! 💎",
            MilestoneType.MILESTONE_1M: f"Epic achievement! {milestone.amount:,.0f} {milestone.currency} - You're a millionaire creator! 👑"
        }
        
        return messages.get(milestone.milestone_type, f"Milestone achieved: {milestone.amount} {milestone.currency}!")
    
    def _calculate_growth_rate(self, current: float, previous: float) -> float:
        """Calculate revenue growth rate"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100
    
    async def _get_personalization_data(self, milestone: RevenueMilestone, context) -> Dict[str, Any]:
        """Get AI personalization data for the celebration"""
        return {
            'user_preferences': context.ai_personalization.get('user_preferences', {}),
            'celebration_style': 'enthusiastic',
            'share_recommendation': True,
            'next_milestone_suggestion': self._suggest_next_milestone(milestone),
            'celebration_rewards': await self._get_celebration_rewards(milestone)
        }
    
    def _suggest_next_milestone(self, milestone: RevenueMilestone) -> Dict[str, Any]:
        """Suggest the next milestone to achieve"""
        next_thresholds = {
            MilestoneType.FIRST_SALE: (MilestoneType.MILESTONE_100, 100.0),
            MilestoneType.MILESTONE_100: (MilestoneType.MILESTONE_1K, 1000.0),
            MilestoneType.MILESTONE_1K: (MilestoneType.MILESTONE_10K, 10000.0),
            MilestoneType.MILESTONE_10K: (MilestoneType.MILESTONE_100K, 100000.0),
            MilestoneType.MILESTONE_100K: (MilestoneType.MILESTONE_1M, 1000000.0)
        }
        
        next_milestone = next_thresholds.get(milestone.milestone_type)
        if next_milestone:
            next_type, next_amount = next_milestone
            return {
                'type': next_type.value,
                'target_amount': next_amount,
                'remaining_amount': next_amount - milestone.amount,
                'progress_percentage': (milestone.amount / next_amount) * 100
            }
        
        return {'message': 'You\'ve achieved all major milestones! Keep growing!'}
    
    async def _get_celebration_rewards(self, milestone: RevenueMilestone) -> List[Dict[str, Any]]:
        """Get celebration rewards for the milestone"""
        rewards = []
        
        # Badge rewards
        rewards.append({
            'type': 'badge',
            'name': f"{milestone.milestone_type.value.replace('_', ' ').title()} Achiever",
            'description': f"Awarded for reaching {milestone.amount} {milestone.currency}",
            'rarity': milestone.celebration_level
        })
        
        # Feature unlocks based on milestone
        if milestone.milestone_type == MilestoneType.MILESTONE_1K:
            rewards.append({
                'type': 'feature_unlock',
                'name': 'Advanced Analytics',
                'description': 'Unlock detailed revenue analytics and insights'
            })
        elif milestone.milestone_type == MilestoneType.MILESTONE_10K:
            rewards.append({
                'type': 'feature_unlock',
                'name': 'Premium Distribution',
                'description': 'Access premium distribution channels'
            })
        
        return rewards

# Export the main class
__all__ = ['RevenueMilestoneEngine']
