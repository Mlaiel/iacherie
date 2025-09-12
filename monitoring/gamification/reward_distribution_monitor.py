"""
Reward Distribution Monitor - Gamification Module
===============================================

Advanced reward distribution monitoring system for tracking, optimizing,
and analyzing reward distribution across the gamification platform.

Features:
- Real-time reward distribution tracking
- Reward optimization and balancing
- Economic impact analysis
- Fraud detection and prevention
- Player behavior analysis
- Reward system performance metrics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RewardType(Enum):
    """Types of rewards in the system"""
    POINTS = "points"
    BADGES = "badges"
    CURRENCY = "currency"
    EXCLUSIVE_ACCESS = "exclusive_access"
    MERCHANDISE = "merchandise"
    RECOGNITION = "recognition"
    BOOST = "boost"
    PREMIUM_FEATURES = "premium_features"

class RewardTrigger(Enum):
    """Events that trigger reward distribution"""
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    CHALLENGE_COMPLETION = "challenge_completion"
    MILESTONE_REACHED = "milestone_reached"
    DAILY_ACTIVITY = "daily_activity"
    SOCIAL_ENGAGEMENT = "social_engagement"
    CONTENT_QUALITY = "content_quality"
    COLLABORATION = "collaboration"
    REFERRAL = "referral"

class DistributionStatus(Enum):
    """Status of reward distribution"""
    PENDING = "pending"
    PROCESSING = "processing"
    DISTRIBUTED = "distributed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class Reward:
    """Reward definition and configuration"""
    reward_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    reward_type: RewardType = RewardType.POINTS
    
    # Value and rarity
    value: float = 0.0
    currency_code: str = "USD"
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    
    # Distribution rules
    max_per_user: int = -1  # -1 for unlimited
    max_total_distribution: int = -1  # -1 for unlimited
    expiry_hours: Optional[int] = None
    
    # Requirements
    minimum_level: int = 1
    required_achievements: List[str] = field(default_factory=list)
    exclusion_rules: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class RewardDistribution:
    """Individual reward distribution record"""
    distribution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    reward_id: str = ""
    trigger: RewardTrigger = RewardTrigger.ACHIEVEMENT_UNLOCK
    
    # Distribution details
    status: DistributionStatus = DistributionStatus.PENDING
    quantity: int = 1
    total_value: float = 0.0
    
    # Context and metadata
    trigger_context: Dict[str, Any] = field(default_factory=dict)
    distribution_reason: str = ""
    source_action_id: Optional[str] = None
    
    # Timing
    triggered_at: datetime = field(default_factory=datetime.now)
    distributed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Verification
    verified: bool = False
    verification_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RewardEconomics:
    """Economic analysis of reward distribution"""
    analysis_period_start: datetime = field(default_factory=datetime.now)
    analysis_period_end: datetime = field(default_factory=datetime.now)
    
    # Distribution metrics
    total_rewards_distributed: int = 0
    total_value_distributed: float = 0.0
    unique_recipients: int = 0
    average_reward_per_user: float = 0.0
    
    # Economic indicators
    inflation_rate: float = 0.0
    reward_velocity: float = 0.0  # How quickly rewards are earned/spent
    concentration_index: float = 0.0  # How concentrated rewards are among top users
    
    # Value distribution
    distribution_by_type: Dict[RewardType, float] = field(default_factory=dict)
    distribution_by_trigger: Dict[RewardTrigger, float] = field(default_factory=dict)
    
    # Behavioral impact
    engagement_correlation: float = 0.0
    retention_impact: float = 0.0
    monetization_correlation: float = 0.0

@dataclass
class RewardAlert:
    """Alert for reward distribution anomalies"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str = ""  # anomaly, fraud, economic_impact, etc.
    severity: str = "medium"  # low, medium, high, critical
    
    # Alert details
    title: str = ""
    description: str = ""
    affected_users: List[str] = field(default_factory=list)
    affected_rewards: List[str] = field(default_factory=list)
    
    # Data
    anomaly_metrics: Dict[str, float] = field(default_factory=dict)
    recommended_actions: List[str] = field(default_factory=list)
    
    # Metadata
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

class RewardDistributionMonitor:
    """Main reward distribution monitoring system"""
    
    def __init__(self):
        self.rewards: Dict[str, Reward] = {}
        self.distributions: List[RewardDistribution] = []
        self.economics_history: List[RewardEconomics] = []
        self.alerts: List[RewardAlert] = []
        
        # Configuration
        self.monitoring_active = False
        self.fraud_detection_enabled = True
        self.economic_analysis_interval_hours = 24
        
        # Thresholds and limits
        self.anomaly_thresholds = {
            "daily_distribution_spike": 5.0,    # 5x normal daily distribution
            "user_reward_spike": 10.0,           # 10x normal user rewards
            "value_concentration": 0.8,          # 80% of value to top 10% users
            "rapid_distribution": 100,           # 100 rewards in 1 hour per user
        }
        
        # Initialize with sample rewards
        self._initialize_sample_rewards()
        
    def _initialize_sample_rewards(self):
        """Initialize with sample reward configurations"""
        sample_rewards = [
            {
                "name": "Content Creator Points",
                "description": "Points awarded for creating quality content",
                "type": RewardType.POINTS,
                "value": 10.0,
                "rarity": "common"
            },
            {
                "name": "Viral Content Badge",
                "description": "Badge for content that goes viral",
                "type": RewardType.BADGES,
                "value": 0.0,
                "rarity": "rare",
                "max_per_user": 1
            },
            {
                "name": "Creator Coins",
                "description": "Platform currency for premium features",
                "type": RewardType.CURRENCY,
                "value": 1.0,
                "rarity": "common"
            },
            {
                "name": "Premium Access",
                "description": "30-day premium feature access",
                "type": RewardType.PREMIUM_FEATURES,
                "value": 29.99,
                "rarity": "epic",
                "expiry_hours": 720  # 30 days
            },
            {
                "name": "Creator Boost",
                "description": "2x engagement boost for 24 hours",
                "type": RewardType.BOOST,
                "value": 5.0,
                "rarity": "uncommon",
                "expiry_hours": 24
            }
        ]
        
        for reward_data in sample_rewards:
            reward = Reward(
                name=reward_data["name"],
                description=reward_data["description"],
                reward_type=reward_data["type"],
                value=reward_data["value"],
                rarity=reward_data["rarity"],
                max_per_user=reward_data.get("max_per_user", -1),
                expiry_hours=reward_data.get("expiry_hours")
            )
            
            self.rewards[reward.reward_id] = reward
            
    async def start_monitoring(self):
        """Start reward distribution monitoring"""
        self.monitoring_active = True
        
        monitoring_tasks = [
            self._monitor_distribution_patterns(),
            self._detect_fraud_and_anomalies(),
            self._analyze_economic_impact(),
            self._process_pending_distributions(),
            self._cleanup_expired_rewards()
        ]
        
        await asyncio.gather(*monitoring_tasks)
        
    async def stop_monitoring(self):
        """Stop reward distribution monitoring"""
        self.monitoring_active = False
        logger.info("Reward distribution monitoring stopped")
        
    async def distribute_reward(self, 
                              user_id: str,
                              reward_id: str,
                              trigger: RewardTrigger,
                              quantity: int = 1,
                              context: Dict[str, Any] = None) -> RewardDistribution:
        """Distribute reward to user"""
        
        reward = self.rewards.get(reward_id)
        if not reward:
            raise ValueError(f"Reward {reward_id} not found")
            
        if not reward.is_active:
            raise ValueError(f"Reward {reward_id} is not active")
            
        # Validate distribution eligibility
        if not await self._validate_distribution_eligibility(user_id, reward, quantity):
            raise ValueError("User not eligible for this reward")
            
        # Create distribution record
        distribution = RewardDistribution(
            user_id=user_id,
            reward_id=reward_id,
            trigger=trigger,
            quantity=quantity,
            total_value=reward.value * quantity,
            trigger_context=context or {},
            distribution_reason=f"Triggered by {trigger.value}"
        )
        
        # Set expiry if applicable
        if reward.expiry_hours:
            distribution.expires_at = datetime.now() + timedelta(hours=reward.expiry_hours)
            
        # Add to distribution queue
        self.distributions.append(distribution)
        
        # Process distribution
        await self._process_distribution(distribution)
        
        logger.info(f"Distributed {quantity}x {reward.name} to user {user_id}")
        return distribution
        
    async def _validate_distribution_eligibility(self, 
                                               user_id: str, 
                                               reward: Reward, 
                                               quantity: int) -> bool:
        """Validate if user is eligible for reward distribution"""
        
        # Check maximum per user limit
        if reward.max_per_user > 0:
            user_distributions = [
                d for d in self.distributions 
                if d.user_id == user_id and d.reward_id == reward.reward_id 
                and d.status == DistributionStatus.DISTRIBUTED
            ]
            
            current_quantity = sum(d.quantity for d in user_distributions)
            if current_quantity + quantity > reward.max_per_user:
                return False
                
        # Check total distribution limit
        if reward.max_total_distribution > 0:
            total_distributed = sum(
                d.quantity for d in self.distributions 
                if d.reward_id == reward.reward_id and d.status == DistributionStatus.DISTRIBUTED
            )
            
            if total_distributed + quantity > reward.max_total_distribution:
                return False
                
        # Check user level requirement (simulated)
        user_level = await self._get_user_level(user_id)
        if user_level < reward.minimum_level:
            return False
            
        # Check required achievements (simulated)
        if reward.required_achievements:
            user_achievements = await self._get_user_achievements(user_id)
            if not all(achievement in user_achievements for achievement in reward.required_achievements):
                return False
                
        return True
        
    async def _get_user_level(self, user_id: str) -> int:
        """Get user level (simulated)"""
        # In a real implementation, this would fetch from user database
        import random
        return random.randint(1, 50)
        
    async def _get_user_achievements(self, user_id: str) -> List[str]:
        """Get user achievements (simulated)"""
        # In a real implementation, this would fetch from achievements database
        sample_achievements = [
            "first_content", "viral_creator", "collaboration_master", 
            "consistent_creator", "community_helper"
        ]
        import random
        return random.sample(sample_achievements, random.randint(1, 4))
        
    async def _process_distribution(self, distribution: RewardDistribution):
        """Process a reward distribution"""
        
        distribution.status = DistributionStatus.PROCESSING
        
        try:
            # Fraud detection check
            if self.fraud_detection_enabled:
                is_fraudulent = await self._detect_fraud(distribution)
                if is_fraudulent:
                    distribution.status = DistributionStatus.FAILED
                    await self._create_fraud_alert(distribution)
                    return
                    
            # Verify distribution context
            if await self._verify_distribution_context(distribution):
                distribution.verified = True
                
            # Execute distribution
            await self._execute_distribution(distribution)
            
            distribution.status = DistributionStatus.DISTRIBUTED
            distribution.distributed_at = datetime.now()
            
            # Check for economic impacts
            await self._check_economic_impact(distribution)
            
        except Exception as e:
            distribution.status = DistributionStatus.FAILED
            logger.error(f"Failed to process distribution {distribution.distribution_id}: {e}")
            
    async def _detect_fraud(self, distribution: RewardDistribution) -> bool:
        """Detect potential fraud in reward distribution"""
        
        user_id = distribution.user_id
        
        # Check for rapid distribution pattern
        recent_distributions = [
            d for d in self.distributions 
            if d.user_id == user_id and 
            d.triggered_at > datetime.now() - timedelta(hours=1)
        ]
        
        if len(recent_distributions) > self.anomaly_thresholds["rapid_distribution"]:
            return True
            
        # Check for suspicious trigger patterns
        trigger_counts = Counter([d.trigger for d in recent_distributions])
        for trigger, count in trigger_counts.items():
            if count > 50:  # More than 50 of same trigger in 1 hour
                return True
                
        # Check for value concentration
        user_24h_value = sum(
            d.total_value for d in self.distributions 
            if d.user_id == user_id and 
            d.triggered_at > datetime.now() - timedelta(hours=24)
        )
        
        total_24h_value = sum(
            d.total_value for d in self.distributions 
            if d.triggered_at > datetime.now() - timedelta(hours=24)
        )
        
        if total_24h_value > 0 and user_24h_value / total_24h_value > 0.1:  # User gets >10% of daily rewards
            return True
            
        return False
        
    async def _verify_distribution_context(self, distribution: RewardDistribution) -> bool:
        """Verify the context and validity of distribution trigger"""
        
        trigger = distribution.trigger
        context = distribution.trigger_context
        
        # Verify based on trigger type
        if trigger == RewardTrigger.ACHIEVEMENT_UNLOCK:
            # Verify achievement was actually unlocked
            achievement_id = context.get("achievement_id")
            return achievement_id is not None
            
        elif trigger == RewardTrigger.CHALLENGE_COMPLETION:
            # Verify challenge was completed
            challenge_id = context.get("challenge_id")
            completion_verified = context.get("completion_verified", False)
            return challenge_id is not None and completion_verified
            
        elif trigger == RewardTrigger.CONTENT_QUALITY:
            # Verify content quality metrics
            quality_score = context.get("quality_score", 0)
            return quality_score > 0.7  # High quality threshold
            
        elif trigger == RewardTrigger.SOCIAL_ENGAGEMENT:
            # Verify engagement metrics
            engagement_count = context.get("engagement_count", 0)
            return engagement_count > 0
            
        # Default verification for other triggers
        return True
        
    async def _execute_distribution(self, distribution: RewardDistribution):
        """Execute the actual reward distribution"""
        
        reward = self.rewards[distribution.reward_id]
        
        # Execute based on reward type
        if reward.reward_type == RewardType.POINTS:
            await self._add_user_points(distribution.user_id, distribution.total_value)
            
        elif reward.reward_type == RewardType.CURRENCY:
            await self._add_user_currency(distribution.user_id, distribution.total_value)
            
        elif reward.reward_type == RewardType.BADGES:
            await self._award_badge(distribution.user_id, reward.name)
            
        elif reward.reward_type == RewardType.PREMIUM_FEATURES:
            await self._grant_premium_access(distribution.user_id, reward.expiry_hours)
            
        elif reward.reward_type == RewardType.BOOST:
            await self._apply_boost(distribution.user_id, reward.description, reward.expiry_hours)
            
        # Record verification data
        distribution.verification_data = {
            "executed_at": datetime.now().isoformat(),
            "execution_method": f"execute_{reward.reward_type.value}",
            "verification_id": str(uuid.uuid4())
        }
        
    async def _add_user_points(self, user_id: str, points: float):
        """Add points to user account (simulated)"""
        logger.info(f"Added {points} points to user {user_id}")
        
    async def _add_user_currency(self, user_id: str, currency: float):
        """Add currency to user account (simulated)"""
        logger.info(f"Added {currency} currency to user {user_id}")
        
    async def _award_badge(self, user_id: str, badge_name: str):
        """Award badge to user (simulated)"""
        logger.info(f"Awarded badge '{badge_name}' to user {user_id}")
        
    async def _grant_premium_access(self, user_id: str, duration_hours: int):
        """Grant premium access to user (simulated)"""
        logger.info(f"Granted {duration_hours} hours premium access to user {user_id}")
        
    async def _apply_boost(self, user_id: str, boost_description: str, duration_hours: int):
        """Apply boost to user (simulated)"""
        logger.info(f"Applied boost '{boost_description}' for {duration_hours} hours to user {user_id}")
        
    async def _check_economic_impact(self, distribution: RewardDistribution):
        """Check for significant economic impact"""
        
        # Calculate recent distribution volume
        recent_value = sum(
            d.total_value for d in self.distributions 
            if d.distributed_at and d.distributed_at > datetime.now() - timedelta(hours=1)
        )
        
        # Check for distribution spikes
        historical_hourly_avg = await self._get_historical_hourly_average()
        
        if recent_value > historical_hourly_avg * self.anomaly_thresholds["daily_distribution_spike"]:
            await self._create_economic_alert(
                "High Distribution Volume",
                f"Recent hourly distribution ({recent_value:.2f}) exceeds normal by {recent_value/historical_hourly_avg:.1f}x",
                {"recent_value": recent_value, "historical_avg": historical_hourly_avg}
            )
            
    async def _get_historical_hourly_average(self) -> float:
        """Get historical hourly average distribution value"""
        
        # Calculate from last 7 days, excluding current day
        start_time = datetime.now() - timedelta(days=8)
        end_time = datetime.now() - timedelta(days=1)
        
        historical_distributions = [
            d for d in self.distributions 
            if d.distributed_at and start_time <= d.distributed_at <= end_time
        ]
        
        if not historical_distributions:
            return 100.0  # Default baseline
            
        total_value = sum(d.total_value for d in historical_distributions)
        total_hours = (end_time - start_time).total_seconds() / 3600
        
        return total_value / total_hours if total_hours > 0 else 100.0
        
    async def _create_fraud_alert(self, distribution: RewardDistribution):
        """Create fraud detection alert"""
        
        alert = RewardAlert(
            alert_type="fraud_detection",
            severity="high",
            title="Potential Fraudulent Distribution",
            description=f"Suspicious reward distribution pattern detected for user {distribution.user_id}",
            affected_users=[distribution.user_id],
            affected_rewards=[distribution.reward_id],
            recommended_actions=[
                "Review user activity pattern",
                "Investigate trigger context",
                "Consider account suspension if confirmed"
            ]
        )
        
        self.alerts.append(alert)
        logger.warning(f"Fraud alert created: {alert.title}")
        
    async def _create_economic_alert(self, 
                                   title: str, 
                                   description: str, 
                                   metrics: Dict[str, float]):
        """Create economic impact alert"""
        
        alert = RewardAlert(
            alert_type="economic_impact",
            severity="medium",
            title=title,
            description=description,
            anomaly_metrics=metrics,
            recommended_actions=[
                "Monitor distribution patterns",
                "Review reward value settings",
                "Consider temporary distribution limits"
            ]
        )
        
        self.alerts.append(alert)
        
    async def _monitor_distribution_patterns(self):
        """Monitor distribution patterns for anomalies"""
        while self.monitoring_active:
            try:
                await self._analyze_distribution_patterns()
                await self._detect_abuse_patterns()
                await self._monitor_reward_velocity()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring distribution patterns: {e}")
                await asyncio.sleep(300)
                
    async def _analyze_distribution_patterns(self):
        """Analyze distribution patterns for unusual activity"""
        
        # Analyze hourly distribution patterns
        current_hour = datetime.now().hour
        current_hour_distributions = [
            d for d in self.distributions 
            if d.distributed_at and d.distributed_at.hour == current_hour
        ]
        
        # Compare with historical patterns for this hour
        historical_distributions = [
            d for d in self.distributions 
            if d.distributed_at and 
            d.distributed_at.hour == current_hour and
            d.distributed_at < datetime.now() - timedelta(days=1)
        ]
        
        if len(current_hour_distributions) > 0 and len(historical_distributions) > 0:
            current_rate = len(current_hour_distributions)
            historical_avg = len(historical_distributions) / 7  # Average over 7 days
            
            if current_rate > historical_avg * 3:  # 3x historical average
                await self._create_economic_alert(
                    "Distribution Rate Spike",
                    f"Current hour distribution rate ({current_rate}) is {current_rate/historical_avg:.1f}x historical average",
                    {"current_rate": current_rate, "historical_avg": historical_avg}
                )
                
    async def _detect_abuse_patterns(self):
        """Detect potential abuse patterns"""
        
        # Look for users with suspicious distribution patterns
        user_distributions = defaultdict(list)
        
        # Get last 24 hours of distributions
        recent_distributions = [
            d for d in self.distributions 
            if d.distributed_at and d.distributed_at > datetime.now() - timedelta(hours=24)
        ]
        
        for distribution in recent_distributions:
            user_distributions[distribution.user_id].append(distribution)
            
        # Analyze each user's pattern
        for user_id, distributions in user_distributions.items():
            if await self._is_abuse_pattern(distributions):
                await self._create_abuse_alert(user_id, distributions)
                
    async def _is_abuse_pattern(self, distributions: List[RewardDistribution]) -> bool:
        """Determine if distribution pattern indicates abuse"""
        
        if len(distributions) < 10:  # Need significant activity to analyze
            return False
            
        # Check for same trigger repetition
        trigger_counts = Counter([d.trigger for d in distributions])
        max_trigger_count = max(trigger_counts.values())
        
        if max_trigger_count > len(distributions) * 0.8:  # 80% same trigger
            return True
            
        # Check for rapid succession
        time_gaps = []
        sorted_distributions = sorted(distributions, key=lambda x: x.triggered_at)
        
        for i in range(1, len(sorted_distributions)):
            gap = (sorted_distributions[i].triggered_at - sorted_distributions[i-1].triggered_at).total_seconds()
            time_gaps.append(gap)
            
        if time_gaps:
            avg_gap = statistics.mean(time_gaps)
            if avg_gap < 60:  # Less than 1 minute average gap
                return True
                
        return False
        
    async def _create_abuse_alert(self, user_id: str, distributions: List[RewardDistribution]):
        """Create abuse pattern alert"""
        
        alert = RewardAlert(
            alert_type="abuse_pattern",
            severity="high",
            title="Potential Reward Abuse",
            description=f"User {user_id} shows suspicious reward distribution pattern",
            affected_users=[user_id],
            affected_rewards=list(set([d.reward_id for d in distributions])),
            recommended_actions=[
                "Investigate user activity logs",
                "Review recent distributions for validity",
                "Consider account review and temporary restrictions"
            ]
        )
        
        self.alerts.append(alert)
        
    async def _monitor_reward_velocity(self):
        """Monitor reward earning and spending velocity"""
        
        # Calculate reward velocity metrics
        daily_distributions = [
            d for d in self.distributions 
            if d.distributed_at and d.distributed_at > datetime.now() - timedelta(days=1)
        ]
        
        if daily_distributions:
            total_value = sum(d.total_value for d in daily_distributions)
            unique_users = len(set(d.user_id for d in daily_distributions))
            
            # Calculate velocity (rewards per user per day)
            velocity = total_value / unique_users if unique_users > 0 else 0
            
            # Compare with historical velocity
            historical_velocity = await self._get_historical_velocity()
            
            if velocity > historical_velocity * 2:  # 2x increase in velocity
                await self._create_economic_alert(
                    "High Reward Velocity",
                    f"Current reward velocity ({velocity:.2f}) is significantly higher than historical average ({historical_velocity:.2f})",
                    {"current_velocity": velocity, "historical_velocity": historical_velocity}
                )
                
    async def _get_historical_velocity(self) -> float:
        """Calculate historical reward velocity"""
        
        # Use 7-30 days ago as historical baseline
        start_time = datetime.now() - timedelta(days=30)
        end_time = datetime.now() - timedelta(days=7)
        
        historical_distributions = [
            d for d in self.distributions 
            if d.distributed_at and start_time <= d.distributed_at <= end_time
        ]
        
        if not historical_distributions:
            return 10.0  # Default baseline
            
        total_value = sum(d.total_value for d in historical_distributions)
        unique_users = len(set(d.user_id for d in historical_distributions))
        days = (end_time - start_time).days
        
        return (total_value / unique_users / days) if unique_users > 0 and days > 0 else 10.0
        
    async def _detect_fraud_and_anomalies(self):
        """Detect fraud and anomalies in reward distribution"""
        while self.monitoring_active:
            try:
                await self._detect_statistical_anomalies()
                await self._analyze_geographic_patterns()
                await self._detect_coordinated_activity()
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Error detecting fraud and anomalies: {e}")
                await asyncio.sleep(600)
                
    async def _detect_statistical_anomalies(self):
        """Detect statistical anomalies in distribution patterns"""
        
        # Analyze distribution values for outliers
        recent_distributions = [
            d for d in self.distributions 
            if d.distributed_at and d.distributed_at > datetime.now() - timedelta(hours=24)
        ]
        
        if len(recent_distributions) < 20:  # Need sufficient data
            return
            
        values = [d.total_value for d in recent_distributions]
        
        if len(values) > 1:
            mean_value = statistics.mean(values)
            std_dev = statistics.stdev(values)
            
            # Detect outliers (values > 3 standard deviations)
            outliers = [d for d in recent_distributions 
                       if abs(d.total_value - mean_value) > 3 * std_dev]
            
            if outliers:
                await self._create_anomaly_alert("Statistical Outliers", outliers)
                
    async def _analyze_geographic_patterns(self):
        """Analyze geographic distribution patterns (simulated)"""
        
        # In a real implementation, this would analyze IP geolocation patterns
        # For now, simulate geographic anomaly detection
        
        import random
        if random.random() < 0.05:  # 5% chance of geographic anomaly
            await self._create_economic_alert(
                "Geographic Anomaly",
                "Unusual geographic concentration of reward distributions detected",
                {"anomaly_score": random.uniform(0.7, 0.9)}
            )
            
    async def _detect_coordinated_activity(self):
        """Detect coordinated fraudulent activity"""
        
        # Look for users with similar distribution patterns
        recent_distributions = [
            d for d in self.distributions 
            if d.distributed_at and d.distributed_at > datetime.now() - timedelta(hours=6)
        ]
        
        # Group by user and analyze patterns
        user_patterns = defaultdict(list)
        for distribution in recent_distributions:
            pattern = (distribution.trigger, distribution.reward_id, distribution.quantity)
            user_patterns[distribution.user_id].append(pattern)
            
        # Look for identical patterns across multiple users
        pattern_users = defaultdict(list)
        for user_id, patterns in user_patterns.items():
            pattern_signature = tuple(sorted(patterns))
            pattern_users[pattern_signature].append(user_id)
            
        # Alert if multiple users have identical patterns
        for pattern, users in pattern_users.items():
            if len(users) >= 3:  # 3 or more users with identical patterns
                await self._create_economic_alert(
                    "Coordinated Activity Detected",
                    f"Detected {len(users)} users with identical reward patterns",
                    {"pattern_users": len(users), "pattern_complexity": len(pattern)}
                )
                
    async def _create_anomaly_alert(self, alert_type: str, anomalous_distributions: List[RewardDistribution]):
        """Create alert for detected anomalies"""
        
        affected_users = list(set([d.user_id for d in anomalous_distributions]))
        affected_rewards = list(set([d.reward_id for d in anomalous_distributions]))
        
        alert = RewardAlert(
            alert_type="anomaly_detection",
            severity="medium",
            title=f"Anomaly Detected: {alert_type}",
            description=f"Detected {len(anomalous_distributions)} anomalous distributions",
            affected_users=affected_users,
            affected_rewards=affected_rewards,
            recommended_actions=[
                "Review anomalous distributions",
                "Investigate user behavior patterns",
                "Consider adjusting detection thresholds"
            ]
        )
        
        self.alerts.append(alert)
        
    async def _analyze_economic_impact(self):
        """Analyze economic impact of reward distribution"""
        while self.monitoring_active:
            try:
                economics = await self._calculate_current_economics()
                self.economics_history.append(economics)
                
                # Keep only last 30 days of economic data
                cutoff_date = datetime.now() - timedelta(days=30)
                self.economics_history = [
                    e for e in self.economics_history 
                    if e.analysis_period_end > cutoff_date
                ]
                
                await self._check_economic_thresholds(economics)
                
                await asyncio.sleep(self.economic_analysis_interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error analyzing economic impact: {e}")
                await asyncio.sleep(3600)
                
    async def _calculate_current_economics(self) -> RewardEconomics:
        """Calculate current economic metrics"""
        
        # Analyze last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        relevant_distributions = [
            d for d in self.distributions 
            if d.distributed_at and start_time <= d.distributed_at <= end_time
            and d.status == DistributionStatus.DISTRIBUTED
        ]
        
        # Basic metrics
        total_rewards = len(relevant_distributions)
        total_value = sum(d.total_value for d in relevant_distributions)
        unique_recipients = len(set(d.user_id for d in relevant_distributions))
        avg_reward = total_value / unique_recipients if unique_recipients > 0 else 0
        
        # Distribution analysis
        distribution_by_type = defaultdict(float)
        distribution_by_trigger = defaultdict(float)
        
        for d in relevant_distributions:
            reward = self.rewards[d.reward_id]
            distribution_by_type[reward.reward_type] += d.total_value
            distribution_by_trigger[d.trigger] += d.total_value
            
        # Economic indicators
        inflation_rate = await self._calculate_inflation_rate()
        reward_velocity = await self._calculate_reward_velocity(relevant_distributions)
        concentration_index = await self._calculate_concentration_index(relevant_distributions)
        
        # Behavioral correlations (simulated)
        engagement_correlation = 0.75  # Positive correlation with engagement
        retention_impact = 0.65        # Positive impact on retention
        monetization_correlation = 0.45 # Moderate correlation with monetization
        
        return RewardEconomics(
            analysis_period_start=start_time,
            analysis_period_end=end_time,
            total_rewards_distributed=total_rewards,
            total_value_distributed=total_value,
            unique_recipients=unique_recipients,
            average_reward_per_user=avg_reward,
            inflation_rate=inflation_rate,
            reward_velocity=reward_velocity,
            concentration_index=concentration_index,
            distribution_by_type=dict(distribution_by_type),
            distribution_by_trigger=dict(distribution_by_trigger),
            engagement_correlation=engagement_correlation,
            retention_impact=retention_impact,
            monetization_correlation=monetization_correlation
        )
        
    async def _calculate_inflation_rate(self) -> float:
        """Calculate reward inflation rate"""
        
        # Compare current distribution rates with historical
        current_distributions = [
            d for d in self.distributions 
            if d.distributed_at and d.distributed_at > datetime.now() - timedelta(days=7)
        ]
        
        historical_distributions = [
            d for d in self.distributions 
            if d.distributed_at and 
            datetime.now() - timedelta(days=14) <= d.distributed_at <= datetime.now() - timedelta(days=7)
        ]
        
        if not historical_distributions:
            return 0.0
            
        current_rate = len(current_distributions) / 7  # Daily rate
        historical_rate = len(historical_distributions) / 7
        
        if historical_rate == 0:
            return 0.0
            
        inflation_rate = ((current_rate - historical_rate) / historical_rate) * 100
        return inflation_rate
        
    async def _calculate_reward_velocity(self, distributions: List[RewardDistribution]) -> float:
        """Calculate reward earning velocity"""
        
        if not distributions:
            return 0.0
            
        # Calculate average time between rewards per user
        user_distributions = defaultdict(list)
        for d in distributions:
            user_distributions[d.user_id].append(d)
            
        velocities = []
        for user_id, user_dists in user_distributions.items():
            if len(user_dists) > 1:
                sorted_dists = sorted(user_dists, key=lambda x: x.distributed_at)
                time_gaps = []
                
                for i in range(1, len(sorted_dists)):
                    gap = (sorted_dists[i].distributed_at - sorted_dists[i-1].distributed_at).total_seconds() / 3600
                    time_gaps.append(gap)
                    
                if time_gaps:
                    avg_gap = statistics.mean(time_gaps)
                    velocity = 1 / avg_gap if avg_gap > 0 else 0  # Rewards per hour
                    velocities.append(velocity)
                    
        return statistics.mean(velocities) if velocities else 0.0
        
    async def _calculate_concentration_index(self, distributions: List[RewardDistribution]) -> float:
        """Calculate concentration index (how concentrated rewards are among top users)"""
        
        if not distributions:
            return 0.0
            
        # Calculate total value per user
        user_values = defaultdict(float)
        for d in distributions:
            user_values[d.user_id] += d.total_value
            
        if len(user_values) == 0:
            return 0.0
            
        # Sort users by total value
        sorted_values = sorted(user_values.values(), reverse=True)
        total_value = sum(sorted_values)
        
        if total_value == 0:
            return 0.0
            
        # Calculate what percentage of value goes to top 10% of users
        top_10_percent_count = max(1, len(sorted_values) // 10)
        top_10_percent_value = sum(sorted_values[:top_10_percent_count])
        
        concentration_index = top_10_percent_value / total_value
        return concentration_index
        
    async def _check_economic_thresholds(self, economics: RewardEconomics):
        """Check economic metrics against thresholds"""
        
        # Check inflation rate
        if abs(economics.inflation_rate) > 50:  # 50% inflation change
            severity = "high" if abs(economics.inflation_rate) > 100 else "medium"
            await self._create_economic_alert(
                "High Inflation Rate",
                f"Reward inflation rate: {economics.inflation_rate:.1f}%",
                {"inflation_rate": economics.inflation_rate}
            )
            
        # Check concentration
        if economics.concentration_index > self.anomaly_thresholds["value_concentration"]:
            await self._create_economic_alert(
                "High Reward Concentration",
                f"Top 10% users receive {economics.concentration_index:.1%} of rewards",
                {"concentration_index": economics.concentration_index}
            )
            
        # Check velocity
        if economics.reward_velocity > 10:  # More than 10 rewards per hour per user
            await self._create_economic_alert(
                "High Reward Velocity",
                f"Reward velocity: {economics.reward_velocity:.2f} rewards/hour/user",
                {"reward_velocity": economics.reward_velocity}
            )
            
    async def _process_pending_distributions(self):
        """Process pending reward distributions"""
        while self.monitoring_active:
            try:
                pending_distributions = [
                    d for d in self.distributions 
                    if d.status == DistributionStatus.PENDING
                ]
                
                for distribution in pending_distributions:
                    await self._process_distribution(distribution)
                    
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                logger.error(f"Error processing pending distributions: {e}")
                await asyncio.sleep(60)
                
    async def _cleanup_expired_rewards(self):
        """Clean up expired reward distributions"""
        while self.monitoring_active:
            try:
                now = datetime.now()
                
                for distribution in self.distributions:
                    if (distribution.expires_at and 
                        distribution.expires_at < now and 
                        distribution.status != DistributionStatus.EXPIRED):
                        
                        distribution.status = DistributionStatus.EXPIRED
                        await self._revoke_expired_reward(distribution)
                        
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error cleaning up expired rewards: {e}")
                await asyncio.sleep(3600)
                
    async def _revoke_expired_reward(self, distribution: RewardDistribution):
        """Revoke expired reward from user"""
        
        reward = self.rewards[distribution.reward_id]
        
        # Revoke based on reward type
        if reward.reward_type == RewardType.BOOST:
            await self._remove_boost(distribution.user_id, reward.description)
        elif reward.reward_type == RewardType.PREMIUM_FEATURES:
            await self._revoke_premium_access(distribution.user_id)
            
        logger.info(f"Revoked expired reward {reward.name} from user {distribution.user_id}")
        
    async def _remove_boost(self, user_id: str, boost_description: str):
        """Remove boost from user (simulated)"""
        logger.info(f"Removed boost '{boost_description}' from user {user_id}")
        
    async def _revoke_premium_access(self, user_id: str):
        """Revoke premium access from user (simulated)"""
        logger.info(f"Revoked premium access from user {user_id}")
        
    def get_distribution_report(self, days_back: int = 7) -> Dict[str, Any]:
        """Generate comprehensive distribution report"""
        
        # Define time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        # Filter relevant distributions
        relevant_distributions = [
            d for d in self.distributions 
            if d.distributed_at and start_time <= d.distributed_at <= end_time
        ]
        
        # Calculate metrics
        total_distributions = len(relevant_distributions)
        total_value = sum(d.total_value for d in relevant_distributions)
        unique_recipients = len(set(d.user_id for d in relevant_distributions))
        
        # Distribution breakdown
        status_breakdown = Counter([d.status for d in self.distributions if d.triggered_at >= start_time])
        type_breakdown = defaultdict(lambda: {"count": 0, "value": 0.0})
        trigger_breakdown = defaultdict(lambda: {"count": 0, "value": 0.0})
        
        for d in relevant_distributions:
            reward = self.rewards[d.reward_id]
            type_breakdown[reward.reward_type.value]["count"] += 1
            type_breakdown[reward.reward_type.value]["value"] += d.total_value
            
            trigger_breakdown[d.trigger.value]["count"] += 1
            trigger_breakdown[d.trigger.value]["value"] += d.total_value
            
        # Recent alerts
        recent_alerts = [
            a for a in self.alerts 
            if a.triggered_at >= start_time
        ]
        
        # Economics
        latest_economics = self.economics_history[-1] if self.economics_history else None
        
        return {
            "period": {
                "start_date": start_time.isoformat(),
                "end_date": end_time.isoformat(),
                "days": days_back
            },
            "distribution_summary": {
                "total_distributions": total_distributions,
                "total_value_distributed": total_value,
                "unique_recipients": unique_recipients,
                "average_value_per_recipient": total_value / unique_recipients if unique_recipients > 0 else 0
            },
            "status_breakdown": dict(status_breakdown),
            "reward_type_breakdown": dict(type_breakdown),
            "trigger_breakdown": dict(trigger_breakdown),
            "recent_alerts": {
                "total_alerts": len(recent_alerts),
                "fraud_alerts": len([a for a in recent_alerts if a.alert_type == "fraud_detection"]),
                "economic_alerts": len([a for a in recent_alerts if a.alert_type == "economic_impact"]),
                "anomaly_alerts": len([a for a in recent_alerts if a.alert_type == "anomaly_detection"])
            },
            "economics": {
                "inflation_rate": latest_economics.inflation_rate if latest_economics else 0,
                "concentration_index": latest_economics.concentration_index if latest_economics else 0,
                "reward_velocity": latest_economics.reward_velocity if latest_economics else 0
            } if latest_economics else None,
            "insights": self._generate_distribution_insights(relevant_distributions, recent_alerts)
        }
        
    def _generate_distribution_insights(self, 
                                      distributions: List[RewardDistribution],
                                      alerts: List[RewardAlert]) -> List[str]:
        """Generate insights from distribution data"""
        
        insights = []
        
        # Distribution volume insights
        if len(distributions) > 1000:
            insights.append("High distribution volume - monitor for scaling impacts")
        elif len(distributions) < 10:
            insights.append("Low distribution volume - consider increasing engagement incentives")
            
        # Alert insights
        fraud_alerts = [a for a in alerts if a.alert_type == "fraud_detection"]
        if len(fraud_alerts) > 5:
            insights.append("Multiple fraud alerts - review detection thresholds and security measures")
        elif len(fraud_alerts) == 0:
            insights.append("No fraud detected - security measures appear effective")
            
        # Value insights
        if distributions:
            total_value = sum(d.total_value for d in distributions)
            if total_value > 10000:
                insights.append("High total value distributed - monitor economic impact")
            elif total_value < 100:
                insights.append("Low total value distributed - consider reward optimization")
                
        # Trigger diversity
        trigger_types = set(d.trigger for d in distributions)
        if len(trigger_types) < 3:
            insights.append("Limited trigger diversity - consider expanding reward triggers")
            
        return insights

# Export main classes
__all__ = [
    'RewardDistributionMonitor',
    'Reward',
    'RewardDistribution',
    'RewardEconomics',
    'RewardAlert',
    'RewardType',
    'RewardTrigger',
    'DistributionStatus'
]