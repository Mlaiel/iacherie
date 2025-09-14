"""
🎮 MONITORING GAMIFICATION - Social Proof Automation Monitor
Advanced social proof automation and viral mechanics monitoring for Ainflue platform
Gaming + UX Engineer + Psychology Expert Implementation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from collections import defaultdict
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialProofType(Enum):
    """Types of social proof mechanisms"""
    USER_COUNT = "user_count"
    TESTIMONIALS = "testimonials" 
    SOCIAL_MEDIA_MENTIONS = "social_media_mentions"
    EXPERT_ENDORSEMENTS = "expert_endorsements"
    PEER_RECOMMENDATIONS = "peer_recommendations"
    TRENDING_CONTENT = "trending_content"
    ACHIEVEMENT_SHOWCASES = "achievement_showcases"
    SUCCESS_STORIES = "success_stories"
    COMMUNITY_ACTIVITY = "community_activity"
    INFLUENCER_PARTICIPATION = "influencer_participation"

class AutomationTrigger(Enum):
    """Triggers for social proof automation"""
    MILESTONE_REACHED = "milestone_reached"
    TRENDING_DETECTION = "trending_detection"
    HIGH_ENGAGEMENT = "high_engagement"
    NEW_USER_SIGNUP = "new_user_signup"
    CONTENT_VIRAL = "content_viral"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    COMMUNITY_GROWTH = "community_growth"
    EXPERT_MENTION = "expert_mention"
    TIME_BASED = "time_based"
    BEHAVIOR_PATTERN = "behavior_pattern"

class ProofEffectiveness(Enum):
    """Effectiveness levels of social proof"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INEFFECTIVE = "ineffective"

class ViralMechanic(Enum):
    """Viral mechanics for content spread"""
    REFERRAL_REWARDS = "referral_rewards"
    SHARING_INCENTIVES = "sharing_incentives"
    COLLABORATIVE_CONTENT = "collaborative_content"
    CHALLENGE_PARTICIPATION = "challenge_participation"
    SOCIAL_VOTING = "social_voting"
    PEER_TAGGING = "peer_tagging"
    MILESTONE_CELEBRATIONS = "milestone_celebrations"
    EXCLUSIVE_ACCESS = "exclusive_access"

@dataclass
class SocialProofEvent:
    """Social proof event data"""
    event_id: str
    proof_type: SocialProofType
    trigger: AutomationTrigger
    user_id: str
    content_id: Optional[str]
    timestamp: datetime
    context_data: Dict[str, Any]
    target_audience: List[str]
    effectiveness_score: float
    engagement_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class AutomationRule:
    """Social proof automation rule"""
    rule_id: str
    name: str
    proof_type: SocialProofType
    trigger_conditions: Dict[str, Any]
    target_criteria: Dict[str, Any]
    content_template: str
    priority: int
    active: bool
    success_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ViralCampaign:
    """Viral campaign tracking"""
    campaign_id: str
    name: str
    viral_mechanic: ViralMechanic
    start_date: datetime
    end_date: Optional[datetime]
    target_metrics: Dict[str, float]
    current_metrics: Dict[str, float]
    participants: Set[str] = field(default_factory=set)
    viral_coefficient: float = 0.0
    reach_multiplier: float = 1.0

@dataclass
class SocialProofAnalytics:
    """Social proof performance analytics"""
    proof_type: SocialProofType
    time_period: str
    total_impressions: int
    total_interactions: int
    conversion_rate: float
    effectiveness_score: float
    top_performing_content: List[str]
    audience_segments: Dict[str, Dict[str, float]]
    optimization_recommendations: List[str] = field(default_factory=list)

class SocialProofAutomationMonitor:
    """
    🎮 Advanced Social Proof Automation Monitor for Ainflue Platform
    
    Psychology-driven social proof automation with:
    - Real-time social proof event detection and generation
    - Intelligent automation rule engine with behavioral triggers
    - Viral mechanics tracking and optimization
    - A/B testing for social proof effectiveness
    - Cross-platform social proof synchronization
    - Audience segmentation for targeted social proof
    - Psychological impact measurement and optimization
    - Automated content generation for social proof
    """
    
    def __init__(self, db_url -> None: str = None, redis_url -> None: str = None) -> None:
        """Initialize social proof automation monitor"""
        self.db_url = db_url
        self.redis_url = redis_url
        
        # Data storage
        self.social_proof_events: List[SocialProofEvent] = []
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.viral_campaigns: Dict[str, ViralCampaign] = {}
        self.user_interactions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Analytics tracking
        self.proof_analytics: Dict[str, SocialProofAnalytics] = {}
        self.effectiveness_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Automation configuration
        self.automation_active = True
        self.min_threshold_for_automation = 0.1
        self.max_events_per_user_per_hour = 5
        
        # Initialize default automation rules
        asyncio.create_task(self._initialize_default_rules())
        
        logger.info("🎮 Social Proof Automation Monitor initialized")

    async def _initialize_default_rules(self) -> None:
        """Initialize default automation rules"""
        try:
            # User milestone achievements
            await self.create_automation_rule(
                "milestone_achievements",
                "User Milestone Celebrations",
                SocialProofType.ACHIEVEMENT_SHOWCASES,
                {
                    "trigger": AutomationTrigger.MILESTONE_REACHED,
                    "min_milestone_value": 1000,
                    "milestone_types": ["followers", "likes", "content_created"]
                },
                {
                    "audience_type": "similar_creators",
                    "exclude_self": True,
                    "max_audience_size": 1000
                },
                "🎉 {user_name} just reached {milestone_value} {milestone_type}! Amazing achievement!",
                priority=8
            )
            
            # Trending content promotion
            await self.create_automation_rule(
                "trending_content",
                "Trending Content Highlights",
                SocialProofType.TRENDING_CONTENT,
                {
                    "trigger": AutomationTrigger.TRENDING_DETECTION,
                    "min_engagement_rate": 0.15,
                    "time_window_hours": 2
                },
                {
                    "audience_type": "interested_users",
                    "interests_match": True,
                    "max_audience_size": 5000
                },
                "🔥 This content is trending! {engagement_count} people are engaging with {creator_name}'s latest creation",
                priority=9
            )
            
            # Expert endorsements
            await self.create_automation_rule(
                "expert_endorsements",
                "Expert Recognition",
                SocialProofType.EXPERT_ENDORSEMENTS,
                {
                    "trigger": AutomationTrigger.EXPERT_MENTION,
                    "expert_verification_required": True,
                    "min_expert_follower_count": 10000
                },
                {
                    "audience_type": "expert_followers",
                    "exclude_already_following": False,
                    "max_audience_size": 2000
                },
                "⭐ Industry expert {expert_name} is impressed by {creator_name}'s work!",
                priority=10
            )
            
            # Community activity showcases
            await self.create_automation_rule(
                "community_activity",
                "Community Engagement Highlights",
                SocialProofType.COMMUNITY_ACTIVITY,
                {
                    "trigger": AutomationTrigger.HIGH_ENGAGEMENT,
                    "min_comments": 20,
                    "min_shares": 10,
                    "time_window_hours": 1
                },
                {
                    "audience_type": "community_members",
                    "active_in_last_days": 7,
                    "max_audience_size": 3000
                },
                "💬 Amazing discussion happening around {content_title}! Join {comment_count} others in the conversation",
                priority=7
            )
            
            logger.info("✅ Default automation rules initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing default rules: {e}")

    async def create_automation_rule(
        self,
        rule_id: str,
        name: str,
        proof_type: SocialProofType,
        trigger_conditions: Dict[str, Any],
        target_criteria: Dict[str, Any],
        content_template: str,
        priority: int = 5
    ) -> bool:
        """
        📋 Create new automation rule for social proof
        
        Define conditions and templates for automated social proof generation
        """
        try:
            logger.info(f"📋 Creating automation rule: {rule_id}")
            
            rule = AutomationRule(
                rule_id=rule_id,
                name=name,
                proof_type=proof_type,
                trigger_conditions=trigger_conditions,
                target_criteria=target_criteria,
                content_template=content_template,
                priority=priority,
                active=True
            )
            
            self.automation_rules[rule_id] = rule
            
            logger.info(f"✅ Automation rule created: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating automation rule: {e}")
            return False

    async def detect_social_proof_opportunities(
        self,
        time_window_minutes: int = 15
    ) -> List[Dict[str, Any]]:
        """
        🔍 Detect opportunities for social proof automation
        
        Analyze recent activities to identify social proof opportunities
        """
        try:
            logger.info(f"🔍 Detecting social proof opportunities ({time_window_minutes}min window)")
            
            cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
            opportunities = []
            
            # Simulate activity detection - would integrate with real data in production
            activities = await self._get_recent_activities(cutoff_time)
            
            # Check each automation rule
            for rule_id, rule in self.automation_rules.items():
                if not rule.active:
                    continue
                
                # Find matching activities
                matching_activities = await self._find_matching_activities(activities, rule)
                
                for activity in matching_activities:
                    opportunity = {
                        'rule_id': rule_id,
                        'rule_name': rule.name,
                        'proof_type': rule.proof_type.value,
                        'trigger_activity': activity,
                        'priority': rule.priority,
                        'estimated_reach': await self._estimate_reach(rule, activity),
                        'estimated_effectiveness': await self._estimate_effectiveness(rule, activity),
                        'target_audience_size': await self._calculate_target_audience_size(rule, activity)
                    }
                    opportunities.append(opportunity)
            
            # Sort by priority and estimated effectiveness
            opportunities.sort(
                key=lambda x: (x['priority'], x['estimated_effectiveness']),
                reverse=True
            )
            
            logger.info(f"✅ Found {len(opportunities)} social proof opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Error detecting social proof opportunities: {e}")
            return []

    async def _get_recent_activities(self, cutoff_time: datetime) -> List[Dict[str, Any]]:
        """Get recent platform activities for analysis"""
        # Simulate recent activities - would integrate with real activity feeds
        activities = []
        
        # Milestone achievements
        activities.extend([
            {
                'type': 'milestone_reached',
                'user_id': f'user_{i}',
                'milestone_type': 'followers',
                'milestone_value': 1000 + i * 500,
                'timestamp': datetime.now() - timedelta(minutes=i*2),
                'metadata': {'user_name': f'Creator_{i}', 'verification_status': 'verified'}
            }
            for i in range(3)
        ])
        
        # High engagement content
        activities.extend([
            {
                'type': 'high_engagement',
                'user_id': f'user_{i+10}',
                'content_id': f'content_{i+10}',
                'engagement_rate': 0.15 + i * 0.05,
                'total_engagement': 500 + i * 200,
                'timestamp': datetime.now() - timedelta(minutes=i*3),
                'metadata': {
                    'content_title': f'Amazing Content {i}',
                    'content_type': 'video',
                    'duration_minutes': 5
                }
            }
            for i in range(2)
        ])
        
        # Expert mentions
        activities.append({
            'type': 'expert_mention',
            'expert_user_id': 'expert_1',
            'mentioned_user_id': 'user_20',
            'content_id': 'content_20',
            'timestamp': datetime.now() - timedelta(minutes=5),
            'metadata': {
                'expert_name': 'Industry Expert',
                'expert_follower_count': 50000,
                'mention_context': 'endorsement'
            }
        })
        
        return activities

    async def _find_matching_activities(
        self,
        activities: List[Dict[str, Any]],
        rule: AutomationRule
    ) -> List[Dict[str, Any]]:
        """Find activities that match automation rule conditions"""
        matching = []
        
        for activity in activities:
            # Check trigger type
            trigger_map = {
                AutomationTrigger.MILESTONE_REACHED: 'milestone_reached',
                AutomationTrigger.HIGH_ENGAGEMENT: 'high_engagement',
                AutomationTrigger.EXPERT_MENTION: 'expert_mention',
                AutomationTrigger.TRENDING_DETECTION: 'trending_detected'
            }
            
            expected_type = trigger_map.get(rule.trigger_conditions.get('trigger'))
            if activity.get('type') != expected_type:
                continue
            
            # Check specific conditions
            conditions_met = True
            
            if 'min_milestone_value' in rule.trigger_conditions:
                if activity.get('milestone_value', 0) < rule.trigger_conditions['min_milestone_value']:
                    conditions_met = False
            
            if 'min_engagement_rate' in rule.trigger_conditions:
                if activity.get('engagement_rate', 0) < rule.trigger_conditions['min_engagement_rate']:
                    conditions_met = False
            
            if 'min_expert_follower_count' in rule.trigger_conditions:
                expert_followers = activity.get('metadata', {}).get('expert_follower_count', 0)
                if expert_followers < rule.trigger_conditions['min_expert_follower_count']:
                    conditions_met = False
            
            if conditions_met:
                matching.append(activity)
        
        return matching

    async def _estimate_reach(self, rule: AutomationRule, activity: Dict[str, Any]) -> int:
        """Estimate potential reach for social proof event"""
        try:
            base_reach = 100
            
            # Adjust based on proof type
            proof_multipliers = {
                SocialProofType.ACHIEVEMENT_SHOWCASES: 1.2,
                SocialProofType.TRENDING_CONTENT: 2.0,
                SocialProofType.EXPERT_ENDORSEMENTS: 1.8,
                SocialProofType.COMMUNITY_ACTIVITY: 1.5,
                SocialProofType.SUCCESS_STORIES: 1.3
            }
            
            multiplier = proof_multipliers.get(rule.proof_type, 1.0)
            
            # Adjust based on activity characteristics
            if activity.get('type') == 'milestone_reached':
                milestone_value = activity.get('milestone_value', 0)
                reach_boost = min(3.0, milestone_value / 1000)
                multiplier *= reach_boost
            
            elif activity.get('type') == 'high_engagement':
                engagement_rate = activity.get('engagement_rate', 0)
                reach_boost = min(2.5, engagement_rate * 10)
                multiplier *= reach_boost
            
            estimated_reach = int(base_reach * multiplier)
            
            # Apply target criteria limits
            max_audience = rule.target_criteria.get('max_audience_size', 10000)
            return min(estimated_reach, max_audience)
            
        except Exception as e:
            logger.error(f"Error estimating reach: {e}")
            return 100

    async def _estimate_effectiveness(self, rule: AutomationRule, activity: Dict[str, Any]) -> float:
        """Estimate effectiveness score for social proof event"""
        try:
            base_effectiveness = 0.5
            
            # Historical performance of this rule
            if rule.rule_id in self.effectiveness_trends:
                recent_performance = self.effectiveness_trends[rule.rule_id][-10:]  # Last 10 events
                if recent_performance:
                    historical_avg = np.mean(recent_performance)
                    base_effectiveness = historical_avg
            
            # Adjust based on activity characteristics
            if activity.get('type') == 'milestone_reached':
                milestone_value = activity.get('milestone_value', 0)
                if milestone_value >= 10000:
                    base_effectiveness += 0.2
                elif milestone_value >= 5000:
                    base_effectiveness += 0.1
            
            elif activity.get('type') == 'high_engagement':
                engagement_rate = activity.get('engagement_rate', 0)
                if engagement_rate >= 0.25:
                    base_effectiveness += 0.3
                elif engagement_rate >= 0.15:
                    base_effectiveness += 0.2
            
            # Adjust based on timing (recent events might be less effective due to fatigue)
            recent_events = len([
                event for event in self.social_proof_events
                if event.timestamp >= datetime.now() - timedelta(hours=1) and
                event.proof_type == rule.proof_type
            ])
            
            if recent_events > 3:
                base_effectiveness *= 0.8  # Reduce effectiveness due to potential fatigue
            
            return min(1.0, max(0.0, base_effectiveness))
            
        except Exception as e:
            logger.error(f"Error estimating effectiveness: {e}")
            return 0.5

    async def _calculate_target_audience_size(self, rule: AutomationRule, activity: Dict[str, Any]) -> int:
        """Calculate target audience size for social proof event"""
        try:
            # Base audience calculation
            base_size = 500
            
            # Adjust based on target criteria
            audience_type = rule.target_criteria.get('audience_type', 'general')
            
            if audience_type == 'similar_creators':
                base_size = 300  # More targeted
            elif audience_type == 'interested_users':
                base_size = 1000  # Broader reach
            elif audience_type == 'expert_followers':
                base_size = 800
            elif audience_type == 'community_members':
                base_size = 600
            
            # Apply max audience size limit
            max_size = rule.target_criteria.get('max_audience_size', 5000)
            return min(base_size, max_size)
            
        except Exception as e:
            logger.error(f"Error calculating target audience size: {e}")
            return 500

    async def execute_social_proof_automation(
        self,
        opportunity: Dict[str, Any]
    ) -> Optional[SocialProofEvent]:
        """
        ⚡ Execute social proof automation for detected opportunity
        
        Generate and distribute social proof content
        """
        try:
            rule_id = opportunity['rule_id']
            if rule_id not in self.automation_rules:
                logger.error(f"Rule {rule_id} not found")
                return None
            
            rule = self.automation_rules[rule_id]
            activity = opportunity['trigger_activity']
            
            logger.info(f"⚡ Executing social proof automation: {rule_id}")
            
            # Check rate limiting
            if not await self._check_rate_limits(activity.get('user_id')):
                logger.warning(f"Rate limit exceeded for user {activity.get('user_id')}")
                return None
            
            # Generate content
            content = await self._generate_social_proof_content(rule, activity)
            if not content:
                return None
            
            # Determine target audience
            target_audience = await self._determine_target_audience(rule, activity)
            
            # Create social proof event
            event_id = f"proof_{rule_id}_{int(time.time())}"
            event = SocialProofEvent(
                event_id=event_id,
                proof_type=rule.proof_type,
                trigger=rule.trigger_conditions.get('trigger', AutomationTrigger.TIME_BASED),
                user_id=activity.get('user_id', ''),
                content_id=activity.get('content_id'),
                timestamp=datetime.now(),
                context_data={
                    'rule_id': rule_id,
                    'activity': activity,
                    'generated_content': content,
                    'automation_version': '1.0'
                },
                target_audience=target_audience,
                effectiveness_score=opportunity['estimated_effectiveness']
            )
            
            # Execute distribution
            success = await self._distribute_social_proof(event, content)
            
            if success:
                # Store event
                self.social_proof_events.append(event)
                
                # Update rule success metrics
                if 'executions' not in rule.success_metrics:
                    rule.success_metrics['executions'] = 0
                rule.success_metrics['executions'] += 1
                
                # Track for effectiveness analysis
                self.effectiveness_trends[rule_id].append(event.effectiveness_score)
                
                # Keep only recent trends
                if len(self.effectiveness_trends[rule_id]) > 50:
                    self.effectiveness_trends[rule_id] = self.effectiveness_trends[rule_id][-30:]
                
                logger.info(f"✅ Social proof automation executed: {event_id}")
                return event
            else:
                logger.error(f"❌ Failed to distribute social proof: {event_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error executing social proof automation: {e}")
            return None

    async def _check_rate_limits(self, user_id: str) -> bool:
        """Check if user is within rate limits for social proof events"""
        try:
            if not user_id:
                return True
            
            cutoff_time = datetime.now() - timedelta(hours=1)
            recent_events = [
                event for event in self.social_proof_events
                if event.user_id == user_id and event.timestamp >= cutoff_time
            ]
            
            return len(recent_events) < self.max_events_per_user_per_hour
            
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return False

    async def _generate_social_proof_content(
        self,
        rule: AutomationRule,
        activity: Dict[str, Any]
    ) -> Optional[str]:
        """Generate social proof content from template and activity data"""
        try:
            template = rule.content_template
            
            # Extract variables from activity and metadata
            variables = {
                'user_name': activity.get('metadata', {}).get('user_name', 'A creator'),
                'creator_name': activity.get('metadata', {}).get('user_name', 'A creator'),
                'milestone_value': activity.get('milestone_value', ''),
                'milestone_type': activity.get('milestone_type', ''),
                'engagement_count': activity.get('total_engagement', ''),
                'content_title': activity.get('metadata', {}).get('content_title', 'content'),
                'expert_name': activity.get('metadata', {}).get('expert_name', 'an expert'),
                'comment_count': activity.get('metadata', {}).get('comment_count', activity.get('total_engagement', 0))
            }
            
            # Replace template variables
            content = template
            for key, value in variables.items():
                content = content.replace(f'{{{key}}}', str(value))
            
            # Add dynamic elements based on proof type
            if rule.proof_type == SocialProofType.ACHIEVEMENT_SHOWCASES:
                content += f" 🎯 Be inspired and reach your own milestones!"
            elif rule.proof_type == SocialProofType.TRENDING_CONTENT:
                content += f" 📈 Don't miss out on what everyone's talking about!"
            elif rule.proof_type == SocialProofType.EXPERT_ENDORSEMENTS:
                content += f" 🌟 Quality recognized by industry leaders!"
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating social proof content: {e}")
            return None

    async def _determine_target_audience(
        self,
        rule: AutomationRule,
        activity: Dict[str, Any]
    ) -> List[str]:
        """Determine target audience for social proof event"""
        try:
            target_audience = []
            
            audience_type = rule.target_criteria.get('audience_type', 'general')
            max_size = rule.target_criteria.get('max_audience_size', 1000)
            
            # Simulate audience targeting - would integrate with real user data
            if audience_type == 'similar_creators':
                # Target creators with similar interests/follower counts
                target_audience = [f'creator_{i}' for i in range(min(max_size, 300))]
            
            elif audience_type == 'interested_users':
                # Target users interested in similar content
                target_audience = [f'interested_user_{i}' for i in range(min(max_size, 1000))]
            
            elif audience_type == 'expert_followers':
                # Target followers of industry experts
                target_audience = [f'expert_follower_{i}' for i in range(min(max_size, 800))]
            
            elif audience_type == 'community_members':
                # Target active community members
                target_audience = [f'community_member_{i}' for i in range(min(max_size, 600))]
            
            else:
                # General audience
                target_audience = [f'user_{i}' for i in range(min(max_size, 500))]
            
            # Apply exclusion criteria
            if rule.target_criteria.get('exclude_self', True):
                user_id = activity.get('user_id')
                if user_id in target_audience:
                    target_audience.remove(user_id)
            
            return target_audience
            
        except Exception as e:
            logger.error(f"Error determining target audience: {e}")
            return []

    async def _distribute_social_proof(
        self,
        event: SocialProofEvent,
        content: str
    ) -> bool:
        """Distribute social proof content to target audience"""
        try:
            # Simulate content distribution - would integrate with real notification systems
            logger.info(f"Distributing social proof to {len(event.target_audience)} users")
            
            # Track engagement metrics (simulated)
            event.engagement_metrics = {
                'impressions': len(event.target_audience),
                'clicks': int(len(event.target_audience) * 0.15),  # 15% CTR
                'shares': int(len(event.target_audience) * 0.03),   # 3% share rate
                'conversions': int(len(event.target_audience) * 0.02)  # 2% conversion rate
            }
            
            # Simulate distribution delay
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Error distributing social proof: {e}")
            return False

    async def analyze_social_proof_effectiveness(
        self,
        time_period_hours: int = 24
    ) -> Dict[str, SocialProofAnalytics]:
        """
        📊 Analyze effectiveness of social proof campaigns
        
        Measure impact and optimization opportunities
        """
        try:
            logger.info(f"📊 Analyzing social proof effectiveness ({time_period_hours}h)")
            
            cutoff_time = datetime.now() - timedelta(hours=time_period_hours)
            recent_events = [
                event for event in self.social_proof_events
                if event.timestamp >= cutoff_time
            ]
            
            analytics = {}
            
            # Analyze by proof type
            for proof_type in SocialProofType:
                type_events = [event for event in recent_events if event.proof_type == proof_type]
                
                if not type_events:
                    continue
                
                # Calculate metrics
                total_impressions = sum(event.engagement_metrics.get('impressions', 0) for event in type_events)
                total_interactions = sum(
                    event.engagement_metrics.get('clicks', 0) + 
                    event.engagement_metrics.get('shares', 0) + 
                    event.engagement_metrics.get('conversions', 0)
                    for event in type_events
                )
                
                conversion_rate = (
                    sum(event.engagement_metrics.get('conversions', 0) for event in type_events) /
                    max(1, total_impressions)
                )
                
                effectiveness_score = np.mean([event.effectiveness_score for event in type_events])
                
                # Top performing content
                top_content = sorted(
                    type_events,
                    key=lambda e: e.engagement_metrics.get('conversions', 0),
                    reverse=True
                )[:3]
                
                top_content_ids = [event.content_id for event in top_content if event.content_id]
                
                # Generate recommendations
                recommendations = await self._generate_effectiveness_recommendations(
                    proof_type, type_events, effectiveness_score
                )
                
                analytics[proof_type.value] = SocialProofAnalytics(
                    proof_type=proof_type,
                    time_period=f"{time_period_hours}h",
                    total_impressions=total_impressions,
                    total_interactions=total_interactions,
                    conversion_rate=conversion_rate,
                    effectiveness_score=effectiveness_score,
                    top_performing_content=top_content_ids,
                    audience_segments={},  # Would be populated with real segmentation data
                    optimization_recommendations=recommendations
                )
            
            # Store analytics
            self.proof_analytics.update(analytics)
            
            logger.info(f"✅ Effectiveness analysis completed for {len(analytics)} proof types")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error analyzing social proof effectiveness: {e}")
            return {}

    async def _generate_effectiveness_recommendations(
        self,
        proof_type: SocialProofType,
        events: List[SocialProofEvent],
        effectiveness_score: float
    ) -> List[str]:
        """Generate recommendations for improving social proof effectiveness"""
        recommendations = []
        
        try:
            if effectiveness_score < 0.3:
                recommendations.append(f"Low effectiveness for {proof_type.value} - review content templates and targeting")
            
            # Analyze timing patterns
            event_hours = [event.timestamp.hour for event in events]
            if event_hours:
                peak_hour = max(set(event_hours), key=event_hours.count)
                recommendations.append(f"Consider scheduling more {proof_type.value} events around {peak_hour}:00")
            
            # Analyze audience size vs effectiveness
            audience_sizes = [len(event.target_audience) for event in events]
            effectiveness_scores = [event.effectiveness_score for event in events]
            
            if len(audience_sizes) > 3:
                correlation = np.corrcoef(audience_sizes, effectiveness_scores)[0, 1]
                if correlation < -0.3:
                    recommendations.append(f"Smaller audiences may be more effective for {proof_type.value}")
                elif correlation > 0.3:
                    recommendations.append(f"Larger audiences may be more effective for {proof_type.value}")
            
            # Type-specific recommendations
            if proof_type == SocialProofType.ACHIEVEMENT_SHOWCASES:
                recommendations.append("Highlight unique and rare achievements for maximum impact")
            elif proof_type == SocialProofType.TRENDING_CONTENT:
                recommendations.append("Act quickly on trending content - timing is crucial")
            elif proof_type == SocialProofType.EXPERT_ENDORSEMENTS:
                recommendations.append("Verify expert credibility and relevance to audience")
            
            if not recommendations:
                recommendations.append(f"{proof_type.value} is performing well - maintain current strategy")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Unable to generate specific recommendations")
        
        return recommendations

    async def track_viral_campaign(
        self,
        campaign_id: str,
        name: str,
        viral_mechanic: ViralMechanic,
        target_metrics: Dict[str, float],
        duration_days: int = 30
    ) -> str:
        """
        🚀 Track viral campaign performance
        
        Monitor viral mechanics and campaign spread
        """
        try:
            logger.info(f"🚀 Starting viral campaign tracking: {campaign_id}")
            
            campaign = ViralCampaign(
                campaign_id=campaign_id,
                name=name,
                viral_mechanic=viral_mechanic,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=duration_days),
                target_metrics=target_metrics,
                current_metrics={
                    'participants': 0,
                    'shares': 0,
                    'reach': 0,
                    'conversions': 0
                }
            )
            
            self.viral_campaigns[campaign_id] = campaign
            
            logger.info(f"✅ Viral campaign tracking started: {campaign_id}")
            return campaign_id
            
        except Exception as e:
            logger.error(f"❌ Error tracking viral campaign: {e}")
            return ""

    async def update_viral_campaign_metrics(
        self,
        campaign_id: str,
        metrics_update: Dict[str, float]
    ) -> bool:
        """Update viral campaign metrics"""
        try:
            if campaign_id not in self.viral_campaigns:
                return False
            
            campaign = self.viral_campaigns[campaign_id]
            
            # Update metrics
            for metric, value in metrics_update.items():
                campaign.current_metrics[metric] = value
            
            # Calculate viral coefficient
            if campaign.current_metrics.get('participants', 0) > 0:
                campaign.viral_coefficient = (
                    campaign.current_metrics.get('shares', 0) /
                    campaign.current_metrics.get('participants', 1)
                )
            
            # Calculate reach multiplier
            initial_reach = campaign.target_metrics.get('reach', 1000)
            current_reach = campaign.current_metrics.get('reach', 0)
            campaign.reach_multiplier = current_reach / initial_reach if initial_reach > 0 else 1.0
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating viral campaign metrics: {e}")
            return False

    async def generate_social_proof_report(
        self,
        time_period_hours: int = 168  # 1 week
    ) -> Dict[str, Any]:
        """
        📊 Generate comprehensive social proof performance report
        
        Complete analysis of social proof automation effectiveness
        """
        try:
            logger.info(f"📊 Generating social proof report ({time_period_hours}h)")
            
            cutoff_time = datetime.now() - timedelta(hours=time_period_hours)
            
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'time_period_hours': time_period_hours,
                'executive_summary': {},
                'automation_performance': {},
                'proof_type_analysis': {},
                'viral_campaigns': {},
                'recommendations': [],
                'action_items': []
            }
            
            # Recent events
            recent_events = [
                event for event in self.social_proof_events
                if event.timestamp >= cutoff_time
            ]
            
            # Executive summary
            total_impressions = sum(event.engagement_metrics.get('impressions', 0) for event in recent_events)
            total_conversions = sum(event.engagement_metrics.get('conversions', 0) for event in recent_events)
            overall_conversion_rate = total_conversions / max(1, total_impressions)
            
            report['executive_summary'] = {
                'total_events': len(recent_events),
                'total_impressions': total_impressions,
                'total_conversions': total_conversions,
                'overall_conversion_rate': overall_conversion_rate,
                'active_automation_rules': len([r for r in self.automation_rules.values() if r.active]),
                'viral_campaigns_active': len([c for c in self.viral_campaigns.values() if c.end_date and c.end_date > datetime.now()])
            }
            
            # Automation rule performance
            rule_performance = {}
            for rule_id, rule in self.automation_rules.items():
                rule_events = [event for event in recent_events if event.context_data.get('rule_id') == rule_id]
                
                if rule_events:
                    rule_impressions = sum(event.engagement_metrics.get('impressions', 0) for event in rule_events)
                    rule_conversions = sum(event.engagement_metrics.get('conversions', 0) for event in rule_events)
                    rule_effectiveness = np.mean([event.effectiveness_score for event in rule_events])
                    
                    rule_performance[rule_id] = {
                        'rule_name': rule.name,
                        'events_generated': len(rule_events),
                        'total_impressions': rule_impressions,
                        'total_conversions': rule_conversions,
                        'conversion_rate': rule_conversions / max(1, rule_impressions),
                        'avg_effectiveness': rule_effectiveness
                    }
            
            report['automation_performance'] = rule_performance
            
            # Proof type analysis
            effectiveness_analysis = await self.analyze_social_proof_effectiveness(time_period_hours)
            report['proof_type_analysis'] = {
                proof_type: {
                    'total_impressions': analytics.total_impressions,
                    'total_interactions': analytics.total_interactions,
                    'conversion_rate': analytics.conversion_rate,
                    'effectiveness_score': analytics.effectiveness_score,
                    'recommendations': analytics.optimization_recommendations
                }
                for proof_type, analytics in effectiveness_analysis.items()
            }
            
            # Viral campaigns
            viral_summary = {}
            for campaign_id, campaign in self.viral_campaigns.items():
                if campaign.start_date >= cutoff_time:
                    viral_summary[campaign_id] = {
                        'name': campaign.name,
                        'viral_mechanic': campaign.viral_mechanic.value,
                        'viral_coefficient': campaign.viral_coefficient,
                        'reach_multiplier': campaign.reach_multiplier,
                        'current_metrics': campaign.current_metrics,
                        'target_metrics': campaign.target_metrics
                    }
            
            report['viral_campaigns'] = viral_summary
            
            # Generate recommendations
            recommendations = []
            
            if overall_conversion_rate < 0.02:
                recommendations.append("Overall conversion rate is low - review content quality and targeting")
            
            # Find best performing rule
            if rule_performance:
                best_rule = max(rule_performance.items(), key=lambda x: x[1]['conversion_rate'])
                recommendations.append(f"Best performing rule: {best_rule[0]} - consider similar approaches")
            
            # Viral campaign recommendations
            if viral_summary:
                high_performing_campaigns = [
                    c for c in viral_summary.values()
                    if c['viral_coefficient'] > 1.0
                ]
                if high_performing_campaigns:
                    recommendations.append("Some viral campaigns showing strong performance - scale successful mechanics")
            
            if not recommendations:
                recommendations.append("Social proof automation is performing well")
            
            report['recommendations'] = recommendations
            
            # Action items
            action_items = []
            
            if len(recent_events) < 10:
                action_items.append("Low social proof activity - review automation triggers")
            
            underperforming_rules = [
                rule_id for rule_id, perf in rule_performance.items()
                if perf['conversion_rate'] < 0.01
            ]
            
            if underperforming_rules:
                action_items.append(f"Optimize underperforming rules: {', '.join(underperforming_rules)}")
            
            if not action_items:
                action_items.append("Continue monitoring social proof performance")
            
            report['action_items'] = action_items
            
            logger.info(f"✅ Social proof report generated: {report['executive_summary']['overall_conversion_rate']:.2%} conversion rate")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating social proof report: {e}")
            return {}

# Usage example
async def main() -> None:
    """Test the social proof automation monitor"""
    try:
        # Initialize monitor
        monitor = SocialProofAutomationMonitor()
        
        # Wait for initialization
        await asyncio.sleep(1)
        
        # Detect opportunities
        opportunities = await monitor.detect_social_proof_opportunities()
        print(f"Found {len(opportunities)} social proof opportunities")
        
        # Execute automation for first opportunity
        if opportunities:
            event = await monitor.execute_social_proof_automation(opportunities[0])
            if event:
                print(f"Executed social proof automation: {event.event_id}")
        
        # Analyze effectiveness
        analytics = await monitor.analyze_social_proof_effectiveness()
        print(f"Analyzed effectiveness for {len(analytics)} proof types")
        
        # Track viral campaign
        campaign_id = await monitor.track_viral_campaign(
            "viral_test_001",
            "Test Viral Campaign",
            ViralMechanic.REFERRAL_REWARDS,
            {'participants': 1000, 'shares': 500, 'reach': 10000}
        )
        print(f"Started viral campaign tracking: {campaign_id}")
        
        # Generate report
        report = await monitor.generate_social_proof_report()
        print(f"Report generated: {report.get('executive_summary', {}).get('total_events', 0)} events analyzed")
        
    except Exception as e:
        print(f"Error in social proof automation: {e}")

if __name__ == "__main__":
    asyncio.run(main())