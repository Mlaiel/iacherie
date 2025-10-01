"""Creator Tier Intelligence Management System
==========================================

Enterprise-grade Creator Tier Intelligence system providing comprehensive
tier management, intelligent progression tracking, and advanced tier analytics
for the IA Chéries Creator Economy. Implements sophisticated tier algorithms,
automated progression, and intelligent tier optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team technical training included
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor

# Optional imports for enhanced functionality
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Mock numpy for basic operations
    np = type('MockNumpy', (), {
        'random': type('MockRandom', (), {
            'rand': lambda: __import__('random').random(),
            'choice': lambda x: __import__('random').choice(x),
            'normal': lambda mu, sigma: mu + sigma * (__import__('random').random() - 0.5) * 2
        })(),
        'mean': lambda x: sum(x) / len(x) if x else 0,
        'std': lambda x: (sum((i - sum(x)/len(x))**2 for i in x) / len(x))**0.5 if x else 0,
        'percentile': lambda x, p: sorted(x)[int(len(x) * p / 100)] if x else 0
    })()

logger = logging.getLogger(__name__)

class CreatorTier(Enum):
    """Creator tier levels in the ecosystem"""
    NEWCOMER = "newcomer"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    ELITE = "elite"
    LEGEND = "legend"

class TierMetricType(Enum):
    """Types of metrics used for tier calculation"""
    FOLLOWER_COUNT = "follower_count"
    ENGAGEMENT_RATE = "engagement_rate"
    CONTENT_QUALITY = "content_quality"
    REVENUE_GENERATED = "revenue_generated"
    COLLABORATION_COUNT = "collaboration_count"
    PLATFORM_DIVERSITY = "platform_diversity"
    CONSISTENCY_SCORE = "consistency_score"
    COMMUNITY_IMPACT = "community_impact"
    INNOVATION_INDEX = "innovation_index"
    MENTORSHIP_ACTIVITY = "mentorship_activity"

class TierBenefit(Enum):
    """Benefits available at different tiers"""
    PRIORITY_SUPPORT = "priority_support"
    EARLY_ACCESS = "early_access"
    EXCLUSIVE_FEATURES = "exclusive_features"
    MONETIZATION_BOOST = "monetization_boost"
    COLLABORATION_PRIORITY = "collaboration_priority"
    ANALYTICS_ADVANCED = "analytics_advanced"
    CONTENT_BOOST = "content_boost"
    REVENUE_SHARE_BONUS = "revenue_share_bonus"
    CUSTOM_BRANDING = "custom_branding"
    DEDICATED_MANAGER = "dedicated_manager"

class ProgressionStatus(Enum):
    """Tier progression status"""
    STABLE = "stable"
    PROGRESSING = "progressing"
    AT_RISK = "at_risk"
    DECLINING = "declining"
    EVALUATION = "evaluation"
    SUSPENDED = "suspended"

@dataclass
class TierRequirement:
    """Tier requirement definition"""
    tier: CreatorTier
    metric_type: TierMetricType
    min_value: float
    max_value: Optional[float] = None
    weight: float = 1.0
    is_mandatory: bool = True
    grace_period_days: int = 30
    description: str = ""

@dataclass
class TierMetric:
    """Creator tier metric data"""
    creator_id: str
    metric_type: TierMetricType
    value: float
    timestamp: datetime
    source: str = "system"
    verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreatorTierProfile:
    """Creator tier profile and progression data"""
    creator_id: str
    username: str
    current_tier: CreatorTier
    previous_tier: Optional[CreatorTier] = None
    tier_since: datetime = field(default_factory=datetime.now)
    progression_status: ProgressionStatus = ProgressionStatus.STABLE
    tier_score: float = 0.0
    next_tier_progress: float = 0.0
    metrics: Dict[TierMetricType, float] = field(default_factory=dict)
    benefits: List[TierBenefit] = field(default_factory=list)
    requirements_met: Dict[TierMetricType, bool] = field(default_factory=dict)
    grace_periods: Dict[TierMetricType, datetime] = field(default_factory=dict)
    tier_history: List[Dict[str, Any]] = field(default_factory=list)
    evaluation_notes: List[str] = field(default_factory=list)
    last_evaluated: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TierProgression:
    """Tier progression event"""
    progression_id: str
    creator_id: str
    from_tier: CreatorTier
    to_tier: CreatorTier
    progression_type: str  # "promotion", "demotion", "evaluation"
    reason: str
    metrics_snapshot: Dict[TierMetricType, float]
    timestamp: datetime = field(default_factory=datetime.now)
    auto_generated: bool = True
    administrator_id: Optional[str] = None
    notes: str = ""

@dataclass
class TierAnalytics:
    """Tier system analytics"""
    timeframe: str
    total_creators: int
    tier_distribution: Dict[CreatorTier, int]
    progression_events: Dict[str, int]  # promotion/demotion counts
    average_tier_duration: Dict[CreatorTier, float]
    top_performing_metrics: List[TierMetricType]
    churn_risk_creators: List[str]
    tier_satisfaction_scores: Dict[CreatorTier, float]
    system_health_score: float
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class TierRecommendation:
    """Tier improvement recommendation"""
    recommendation_id: str
    creator_id: str
    target_tier: CreatorTier
    priority_metrics: List[TierMetricType]
    improvement_suggestions: List[str]
    estimated_timeline: str
    success_probability: float
    required_actions: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.now)

class CreatorTierIntelligenceManagementSystem:
    """Enterprise Creator Tier Intelligence Management System
    
    Provides comprehensive tier management with intelligent progression,
    automated evaluation, and advanced tier optimization for Creator Economy.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Creator Tier Intelligence Management System
        
        Args:
            config: Configuration dictionary for tier management settings
        """
        self.config = config or {}
        self.tier_profiles = {}
        self.tier_metrics = defaultdict(list)
        self.tier_requirements = {}
        self.progression_history = []
        self.tier_analytics = {}
        self.recommendations = defaultdict(list)
        self.tier_benefits = {}
        self.evaluation_queue = deque()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize tier system configuration
        self._initialize_tier_requirements()
        self._initialize_tier_benefits()
        
        # Evaluation settings
        self.evaluation_settings = {
            "evaluation_interval": 86400,  # 24 hours
            "grace_period_default": 30,  # 30 days
            "auto_progression_enabled": True,
            "manual_override_allowed": True,
            "tier_lock_period": 7,  # Days before allowing another change
            "performance_window": 30  # Days to consider for metrics
        }
        
        # Start background evaluation process
        asyncio.create_task(self._tier_evaluation_processor())
        
        logger.info("Creator Tier Intelligence Management System initialized successfully")
    
    def _initialize_tier_requirements(self):
        """Initialize tier requirements for all levels"""
        # Newcomer Tier (Starting tier)
        newcomer_requirements = [
            TierRequirement(CreatorTier.NEWCOMER, TierMetricType.FOLLOWER_COUNT, 0, 99, 0.2, True, 0, "Starting level"),
            TierRequirement(CreatorTier.NEWCOMER, TierMetricType.CONTENT_QUALITY, 0.3, None, 0.3, True, 7, "Basic content quality"),
            TierRequirement(CreatorTier.NEWCOMER, TierMetricType.ENGAGEMENT_RATE, 0.01, None, 0.2, True, 7, "Minimal engagement"),
        ]
        
        # Bronze Tier
        bronze_requirements = [
            TierRequirement(CreatorTier.BRONZE, TierMetricType.FOLLOWER_COUNT, 100, 499, 0.2, True, 14, "Growing audience"),
            TierRequirement(CreatorTier.BRONZE, TierMetricType.ENGAGEMENT_RATE, 0.02, None, 0.25, True, 14, "Improved engagement"),
            TierRequirement(CreatorTier.BRONZE, TierMetricType.CONTENT_QUALITY, 0.5, None, 0.25, True, 14, "Quality content"),
            TierRequirement(CreatorTier.BRONZE, TierMetricType.CONSISTENCY_SCORE, 0.3, None, 0.15, True, 14, "Regular posting"),
            TierRequirement(CreatorTier.BRONZE, TierMetricType.PLATFORM_DIVERSITY, 1, None, 0.15, False, 30, "Multi-platform presence"),
        ]
        
        # Silver Tier
        silver_requirements = [
            TierRequirement(CreatorTier.SILVER, TierMetricType.FOLLOWER_COUNT, 500, 2499, 0.2, True, 21, "Established audience"),
            TierRequirement(CreatorTier.SILVER, TierMetricType.ENGAGEMENT_RATE, 0.04, None, 0.25, True, 21, "Strong engagement"),
            TierRequirement(CreatorTier.SILVER, TierMetricType.CONTENT_QUALITY, 0.65, None, 0.2, True, 21, "High quality content"),
            TierRequirement(CreatorTier.SILVER, TierMetricType.CONSISTENCY_SCORE, 0.5, None, 0.15, True, 21, "Consistent creator"),
            TierRequirement(CreatorTier.SILVER, TierMetricType.PLATFORM_DIVERSITY, 2, None, 0.1, True, 30, "Multi-platform"),
            TierRequirement(CreatorTier.SILVER, TierMetricType.COLLABORATION_COUNT, 1, None, 0.1, False, 30, "Collaborative spirit"),
        ]
        
        # Gold Tier
        gold_requirements = [
            TierRequirement(CreatorTier.GOLD, TierMetricType.FOLLOWER_COUNT, 2500, 9999, 0.18, True, 30, "Large audience"),
            TierRequirement(CreatorTier.GOLD, TierMetricType.ENGAGEMENT_RATE, 0.06, None, 0.22, True, 30, "Excellent engagement"),
            TierRequirement(CreatorTier.GOLD, TierMetricType.CONTENT_QUALITY, 0.75, None, 0.2, True, 30, "Premium content"),
            TierRequirement(CreatorTier.GOLD, TierMetricType.CONSISTENCY_SCORE, 0.7, None, 0.15, True, 30, "Highly consistent"),
            TierRequirement(CreatorTier.GOLD, TierMetricType.PLATFORM_DIVERSITY, 3, None, 0.1, True, 30, "Multi-platform expert"),
            TierRequirement(CreatorTier.GOLD, TierMetricType.COLLABORATION_COUNT, 3, None, 0.1, True, 30, "Active collaborator"),
            TierRequirement(CreatorTier.GOLD, TierMetricType.REVENUE_GENERATED, 100, None, 0.05, False, 60, "Monetization start"),
        ]
        
        # Platinum Tier
        platinum_requirements = [
            TierRequirement(CreatorTier.PLATINUM, TierMetricType.FOLLOWER_COUNT, 10000, 49999, 0.15, True, 30, "Influencer level"),
            TierRequirement(CreatorTier.PLATINUM, TierMetricType.ENGAGEMENT_RATE, 0.08, None, 0.2, True, 30, "Outstanding engagement"),
            TierRequirement(CreatorTier.PLATINUM, TierMetricType.CONTENT_QUALITY, 0.85, None, 0.2, True, 30, "Exceptional content"),
            TierRequirement(CreatorTier.PLATINUM, TierMetricType.CONSISTENCY_SCORE, 0.8, None, 0.15, True, 30, "Ultra consistent"),
            TierRequirement(CreatorTier.PLATINUM, TierMetricType.PLATFORM_DIVERSITY, 4, None, 0.1, True, 30, "Platform master"),
            TierRequirement(CreatorTier.PLATINUM, TierMetricType.COLLABORATION_COUNT, 5, None, 0.1, True, 30, "Collaboration leader"),
            TierRequirement(CreatorTier.PLATINUM, TierMetricType.REVENUE_GENERATED, 1000, None, 0.05, True, 60, "Strong monetization"),
            TierRequirement(CreatorTier.PLATINUM, TierMetricType.COMMUNITY_IMPACT, 0.7, None, 0.05, False, 60, "Community builder"),
        ]
        
        # Diamond Tier
        diamond_requirements = [
            TierRequirement(CreatorTier.DIAMOND, TierMetricType.FOLLOWER_COUNT, 50000, 199999, 0.12, True, 45, "Major influencer"),
            TierRequirement(CreatorTier.DIAMOND, TierMetricType.ENGAGEMENT_RATE, 0.10, None, 0.18, True, 45, "Premium engagement"),
            TierRequirement(CreatorTier.DIAMOND, TierMetricType.CONTENT_QUALITY, 0.90, None, 0.2, True, 45, "World-class content"),
            TierRequirement(CreatorTier.DIAMOND, TierMetricType.CONSISTENCY_SCORE, 0.85, None, 0.15, True, 45, "Legendary consistency"),
            TierRequirement(CreatorTier.DIAMOND, TierMetricType.PLATFORM_DIVERSITY, 5, None, 0.1, True, 45, "Omni-channel presence"),
            TierRequirement(CreatorTier.DIAMOND, TierMetricType.COLLABORATION_COUNT, 10, None, 0.1, True, 45, "Collaboration master"),
            TierRequirement(CreatorTier.DIAMOND, TierMetricType.REVENUE_GENERATED, 10000, None, 0.08, True, 60, "High revenue"),
            TierRequirement(CreatorTier.DIAMOND, TierMetricType.COMMUNITY_IMPACT, 0.8, None, 0.05, True, 60, "Community leader"),
            TierRequirement(CreatorTier.DIAMOND, TierMetricType.INNOVATION_INDEX, 0.7, None, 0.02, False, 90, "Innovation pioneer"),
        ]
        
        # Elite Tier
        elite_requirements = [
            TierRequirement(CreatorTier.ELITE, TierMetricType.FOLLOWER_COUNT, 200000, 999999, 0.1, True, 60, "Celebrity level"),
            TierRequirement(CreatorTier.ELITE, TierMetricType.ENGAGEMENT_RATE, 0.12, None, 0.15, True, 60, "Elite engagement"),
            TierRequirement(CreatorTier.ELITE, TierMetricType.CONTENT_QUALITY, 0.95, None, 0.2, True, 60, "Masterpiece content"),
            TierRequirement(CreatorTier.ELITE, TierMetricType.CONSISTENCY_SCORE, 0.9, None, 0.15, True, 60, "Perfect consistency"),
            TierRequirement(CreatorTier.ELITE, TierMetricType.PLATFORM_DIVERSITY, 6, None, 0.1, True, 60, "Platform dominance"),
            TierRequirement(CreatorTier.ELITE, TierMetricType.COLLABORATION_COUNT, 20, None, 0.1, True, 60, "Collaboration expert"),
            TierRequirement(CreatorTier.ELITE, TierMetricType.REVENUE_GENERATED, 50000, None, 0.1, True, 90, "Elite revenue"),
            TierRequirement(CreatorTier.ELITE, TierMetricType.COMMUNITY_IMPACT, 0.9, None, 0.05, True, 90, "Community icon"),
            TierRequirement(CreatorTier.ELITE, TierMetricType.INNOVATION_INDEX, 0.8, None, 0.03, True, 90, "Innovation leader"),
            TierRequirement(CreatorTier.ELITE, TierMetricType.MENTORSHIP_ACTIVITY, 0.7, None, 0.02, False, 90, "Mentor others"),
        ]
        
        # Legend Tier (Invitation only, highest tier)
        legend_requirements = [
            TierRequirement(CreatorTier.LEGEND, TierMetricType.FOLLOWER_COUNT, 1000000, None, 0.1, True, 90, "Legendary reach"),
            TierRequirement(CreatorTier.LEGEND, TierMetricType.ENGAGEMENT_RATE, 0.15, None, 0.15, True, 90, "Legendary engagement"),
            TierRequirement(CreatorTier.LEGEND, TierMetricType.CONTENT_QUALITY, 0.98, None, 0.2, True, 90, "Legendary quality"),
            TierRequirement(CreatorTier.LEGEND, TierMetricType.CONSISTENCY_SCORE, 0.95, None, 0.15, True, 90, "Legendary consistency"),
            TierRequirement(CreatorTier.LEGEND, TierMetricType.REVENUE_GENERATED, 100000, None, 0.1, True, 120, "Legendary revenue"),
            TierRequirement(CreatorTier.LEGEND, TierMetricType.COMMUNITY_IMPACT, 0.95, None, 0.1, True, 120, "Legendary impact"),
            TierRequirement(CreatorTier.LEGEND, TierMetricType.INNOVATION_INDEX, 0.9, None, 0.1, True, 120, "Legendary innovation"),
            TierRequirement(CreatorTier.LEGEND, TierMetricType.MENTORSHIP_ACTIVITY, 0.8, None, 0.1, True, 120, "Legendary mentor"),
        ]
        
        # Store requirements grouped by tier
        all_requirements = (
            newcomer_requirements + bronze_requirements + silver_requirements + 
            gold_requirements + platinum_requirements + diamond_requirements + 
            elite_requirements + legend_requirements
        )
        
        for requirement in all_requirements:
            if requirement.tier not in self.tier_requirements:
                self.tier_requirements[requirement.tier] = []
            self.tier_requirements[requirement.tier].append(requirement)
        
        logger.info(f"Initialized tier requirements for {len(self.tier_requirements)} tiers")
    
    def _initialize_tier_benefits(self):
        """Initialize benefits for each tier level"""
        self.tier_benefits = {
            CreatorTier.NEWCOMER: [
                TierBenefit.PRIORITY_SUPPORT,
            ],
            CreatorTier.BRONZE: [
                TierBenefit.PRIORITY_SUPPORT,
                TierBenefit.ANALYTICS_ADVANCED,
            ],
            CreatorTier.SILVER: [
                TierBenefit.PRIORITY_SUPPORT,
                TierBenefit.ANALYTICS_ADVANCED,
                TierBenefit.CONTENT_BOOST,
                TierBenefit.EARLY_ACCESS,
            ],
            CreatorTier.GOLD: [
                TierBenefit.PRIORITY_SUPPORT,
                TierBenefit.ANALYTICS_ADVANCED,
                TierBenefit.CONTENT_BOOST,
                TierBenefit.EARLY_ACCESS,
                TierBenefit.EXCLUSIVE_FEATURES,
                TierBenefit.MONETIZATION_BOOST,
            ],
            CreatorTier.PLATINUM: [
                TierBenefit.PRIORITY_SUPPORT,
                TierBenefit.ANALYTICS_ADVANCED,
                TierBenefit.CONTENT_BOOST,
                TierBenefit.EARLY_ACCESS,
                TierBenefit.EXCLUSIVE_FEATURES,
                TierBenefit.MONETIZATION_BOOST,
                TierBenefit.COLLABORATION_PRIORITY,
                TierBenefit.REVENUE_SHARE_BONUS,
            ],
            CreatorTier.DIAMOND: [
                TierBenefit.PRIORITY_SUPPORT,
                TierBenefit.ANALYTICS_ADVANCED,
                TierBenefit.CONTENT_BOOST,
                TierBenefit.EARLY_ACCESS,
                TierBenefit.EXCLUSIVE_FEATURES,
                TierBenefit.MONETIZATION_BOOST,
                TierBenefit.COLLABORATION_PRIORITY,
                TierBenefit.REVENUE_SHARE_BONUS,
                TierBenefit.CUSTOM_BRANDING,
            ],
            CreatorTier.ELITE: [
                TierBenefit.PRIORITY_SUPPORT,
                TierBenefit.ANALYTICS_ADVANCED,
                TierBenefit.CONTENT_BOOST,
                TierBenefit.EARLY_ACCESS,
                TierBenefit.EXCLUSIVE_FEATURES,
                TierBenefit.MONETIZATION_BOOST,
                TierBenefit.COLLABORATION_PRIORITY,
                TierBenefit.REVENUE_SHARE_BONUS,
                TierBenefit.CUSTOM_BRANDING,
                TierBenefit.DEDICATED_MANAGER,
            ],
            CreatorTier.LEGEND: [
                # All benefits
                benefit for benefit in TierBenefit
            ]
        }
    
    async def register_creator(self, creator_id: str, username: str) -> bool:
        """Register a new creator in the tier system
        
        Args:
            creator_id: Unique creator identifier
            username: Creator's username
            
        Returns:
            Success status of registration
        """
        try:
            if creator_id in self.tier_profiles:
                logger.warning(f"Creator {creator_id} already registered")
                return True
            
            # Create initial tier profile
            profile = CreatorTierProfile(
                creator_id=creator_id,
                username=username,
                current_tier=CreatorTier.NEWCOMER,
                benefits=self.tier_benefits[CreatorTier.NEWCOMER].copy()
            )
            
            # Initialize metrics with default values
            profile.metrics = {
                TierMetricType.FOLLOWER_COUNT: 0,
                TierMetricType.ENGAGEMENT_RATE: 0.0,
                TierMetricType.CONTENT_QUALITY: 0.3,
                TierMetricType.REVENUE_GENERATED: 0.0,
                TierMetricType.COLLABORATION_COUNT: 0,
                TierMetricType.PLATFORM_DIVERSITY: 1,
                TierMetricType.CONSISTENCY_SCORE: 0.0,
                TierMetricType.COMMUNITY_IMPACT: 0.0,
                TierMetricType.INNOVATION_INDEX: 0.0,
                TierMetricType.MENTORSHIP_ACTIVITY: 0.0
            }
            
            # Store profile
            self.tier_profiles[creator_id] = profile
            
            # Schedule initial evaluation
            self.evaluation_queue.append(creator_id)
            
            logger.info(f"Creator {username} registered in tier system as {profile.current_tier.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering creator: {str(e)}")
            return False
    
    async def update_creator_metric(
        self, 
        creator_id: str, 
        metric_type: TierMetricType, 
        value: float,
        source: str = "system",
        verified: bool = False
    ) -> bool:
        """Update a creator's tier metric
        
        Args:
            creator_id: Creator identifier
            metric_type: Type of metric to update
            value: New metric value
            source: Source of the metric update
            verified: Whether the metric is verified
            
        Returns:
            Success status of update
        """
        try:
            if creator_id not in self.tier_profiles:
                logger.error(f"Creator not found: {creator_id}")
                return False
            
            profile = self.tier_profiles[creator_id]
            
            # Create metric record
            metric = TierMetric(
                creator_id=creator_id,
                metric_type=metric_type,
                value=value,
                timestamp=datetime.now(),
                source=source,
                verified=verified
            )
            
            # Store metric
            self.tier_metrics[creator_id].append(metric)
            
            # Update profile metrics
            profile.metrics[metric_type] = value
            
            # Schedule tier evaluation
            if creator_id not in self.evaluation_queue:
                self.evaluation_queue.append(creator_id)
            
            logger.debug(f"Updated {metric_type.value} for creator {creator_id}: {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating creator metric: {str(e)}")
            return False
    
    async def _tier_evaluation_processor(self):
        """Background task to process tier evaluations"""
        while True:
            try:
                await self._process_evaluation_queue()
                await asyncio.sleep(self.evaluation_settings["evaluation_interval"])
                
            except Exception as e:
                logger.error(f"Error in tier evaluation processor: {str(e)}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _process_evaluation_queue(self):
        """Process pending tier evaluations"""
        try:
            evaluations_processed = 0
            max_evaluations_per_cycle = 100
            
            while self.evaluation_queue and evaluations_processed < max_evaluations_per_cycle:
                creator_id = self.evaluation_queue.popleft()
                
                if creator_id not in self.tier_profiles:
                    continue
                
                await self._evaluate_creator_tier(creator_id)
                evaluations_processed += 1
            
            logger.debug(f"Processed {evaluations_processed} tier evaluations")
            
        except Exception as e:
            logger.error(f"Error processing evaluation queue: {str(e)}")
    
    async def _evaluate_creator_tier(self, creator_id: str):
        """Evaluate creator's tier based on current metrics"""
        try:
            profile = self.tier_profiles[creator_id]
            
            # Check if evaluation is needed (respect tier lock period)
            if profile.tier_since and profile.tier_since > datetime.now() - timedelta(days=self.evaluation_settings["tier_lock_period"]):
                return  # Too soon for re-evaluation
            
            # Calculate tier scores for all tiers
            tier_scores = {}
            for tier in CreatorTier:
                score = await self._calculate_tier_score(creator_id, tier)
                tier_scores[tier] = score
            
            # Find best qualifying tier
            new_tier = await self._determine_qualifying_tier(creator_id, tier_scores)
            
            # Update tier if changed
            if new_tier != profile.current_tier:
                await self._process_tier_change(creator_id, new_tier, tier_scores[new_tier])
            else:
                # Update scores and progression status
                profile.tier_score = tier_scores[profile.current_tier]
                profile.progression_status = await self._assess_progression_status(creator_id, tier_scores)
                
                # Calculate next tier progress
                next_tier = await self._get_next_tier(profile.current_tier)
                if next_tier:
                    profile.next_tier_progress = min(100.0, tier_scores[next_tier] * 100)
            
            # Update evaluation timestamp
            profile.last_evaluated = datetime.now()
            
            # Generate recommendations
            await self._generate_tier_recommendations(creator_id)
            
        except Exception as e:
            logger.error(f"Error evaluating creator tier for {creator_id}: {str(e)}")
    
    async def _calculate_tier_score(self, creator_id: str, tier: CreatorTier) -> float:
        """Calculate tier qualification score for creator"""
        try:
            profile = self.tier_profiles[creator_id]
            requirements = self.tier_requirements.get(tier, [])
            
            if not requirements:
                return 0.0
            
            total_score = 0.0
            total_weight = 0.0
            
            for requirement in requirements:
                metric_value = profile.metrics.get(requirement.metric_type, 0.0)
                
                # Calculate requirement fulfillment score
                if requirement.max_value is None:
                    # No upper limit - score based on exceeding minimum
                    if metric_value >= requirement.min_value:
                        # Bonus for exceeding minimum
                        excess_ratio = (metric_value - requirement.min_value) / max(requirement.min_value, 1)
                        score = min(1.0, 1.0 + excess_ratio * 0.1)  # Up to 10% bonus
                    else:
                        # Partial score based on progress toward minimum
                        score = metric_value / requirement.min_value if requirement.min_value > 0 else 0.0
                else:
                    # Range requirement - score based on being within range
                    if requirement.min_value <= metric_value <= requirement.max_value:
                        score = 1.0
                    elif metric_value < requirement.min_value:
                        score = metric_value / requirement.min_value if requirement.min_value > 0 else 0.0
                    else:
                        # Above range - slight penalty
                        score = 0.9
                
                # Apply grace period if in effect
                if requirement.metric_type in profile.grace_periods:
                    grace_end = profile.grace_periods[requirement.metric_type]
                    if datetime.now() < grace_end and score < 1.0:
                        score = 1.0  # Grace period protection
                
                # Apply weight and mandatory flag
                weighted_score = score * requirement.weight
                if requirement.is_mandatory and score < 0.8:
                    # Mandatory requirements have stricter thresholds
                    weighted_score *= 0.5
                
                total_score += weighted_score
                total_weight += requirement.weight
            
            # Normalize score
            final_score = total_score / total_weight if total_weight > 0 else 0.0
            
            return min(1.0, final_score)
            
        except Exception as e:
            logger.error(f"Error calculating tier score: {str(e)}")
            return 0.0
    
    async def _determine_qualifying_tier(self, creator_id: str, tier_scores: Dict[CreatorTier, float]) -> CreatorTier:
        """Determine the highest tier the creator qualifies for"""
        try:
            # Sort tiers by level (highest first)
            tier_order = [CreatorTier.LEGEND, CreatorTier.ELITE, CreatorTier.DIAMOND, 
                         CreatorTier.PLATINUM, CreatorTier.GOLD, CreatorTier.SILVER, 
                         CreatorTier.BRONZE, CreatorTier.NEWCOMER]
            
            qualification_threshold = 0.8  # Must meet 80% of requirements
            
            for tier in tier_order:
                if tier_scores.get(tier, 0.0) >= qualification_threshold:
                    return tier
            
            # Default to newcomer if no tier qualifies
            return CreatorTier.NEWCOMER
            
        except Exception as e:
            logger.error(f"Error determining qualifying tier: {str(e)}")
            return CreatorTier.NEWCOMER
    
    async def _process_tier_change(self, creator_id: str, new_tier: CreatorTier, tier_score: float):
        """Process a tier change for a creator"""
        try:
            profile = self.tier_profiles[creator_id]
            old_tier = profile.current_tier
            
            # Determine progression type
            tier_order = [CreatorTier.NEWCOMER, CreatorTier.BRONZE, CreatorTier.SILVER, 
                         CreatorTier.GOLD, CreatorTier.PLATINUM, CreatorTier.DIAMOND, 
                         CreatorTier.ELITE, CreatorTier.LEGEND]
            
            old_index = tier_order.index(old_tier)
            new_index = tier_order.index(new_tier)
            
            progression_type = "promotion" if new_index > old_index else "demotion"
            
            # Create progression record
            progression = TierProgression(
                progression_id=str(uuid.uuid4()),
                creator_id=creator_id,
                from_tier=old_tier,
                to_tier=new_tier,
                progression_type=progression_type,
                reason=f"Automatic {progression_type} based on tier evaluation",
                metrics_snapshot=profile.metrics.copy()
            )
            
            # Update profile
            profile.previous_tier = old_tier
            profile.current_tier = new_tier
            profile.tier_since = datetime.now()
            profile.tier_score = tier_score
            profile.progression_status = ProgressionStatus.STABLE
            
            # Update benefits
            profile.benefits = self.tier_benefits.get(new_tier, []).copy()
            
            # Add to tier history
            profile.tier_history.append({
                "tier": old_tier.value,
                "start_date": profile.tier_since.isoformat(),
                "end_date": datetime.now().isoformat(),
                "progression_type": progression_type
            })
            
            # Store progression
            self.progression_history.append(progression)
            
            # Set grace periods for new tier if demotion
            if progression_type == "demotion":
                await self._set_grace_periods(creator_id, new_tier)
            
            logger.info(f"Creator {profile.username} {progression_type}: {old_tier.value} → {new_tier.value}")
            
        except Exception as e:
            logger.error(f"Error processing tier change: {str(e)}")
    
    async def _assess_progression_status(self, creator_id: str, tier_scores: Dict[CreatorTier, float]) -> ProgressionStatus:
        """Assess creator's progression status within current tier"""
        try:
            profile = self.tier_profiles[creator_id]
            current_tier = profile.current_tier
            current_score = tier_scores.get(current_tier, 0.0)
            
            # Get next and previous tier scores
            tier_order = [CreatorTier.NEWCOMER, CreatorTier.BRONZE, CreatorTier.SILVER, 
                         CreatorTier.GOLD, CreatorTier.PLATINUM, CreatorTier.DIAMOND, 
                         CreatorTier.ELITE, CreatorTier.LEGEND]
            
            current_index = tier_order.index(current_tier)
            
            next_tier_score = 0.0
            if current_index < len(tier_order) - 1:
                next_tier = tier_order[current_index + 1]
                next_tier_score = tier_scores.get(next_tier, 0.0)
            
            # Determine status
            if current_score < 0.6:
                return ProgressionStatus.AT_RISK
            elif current_score < 0.7:
                return ProgressionStatus.DECLINING
            elif next_tier_score > 0.6:
                return ProgressionStatus.PROGRESSING
            else:
                return ProgressionStatus.STABLE
                
        except Exception as e:
            logger.error(f"Error assessing progression status: {str(e)}")
            return ProgressionStatus.STABLE
    
    async def _get_next_tier(self, current_tier: CreatorTier) -> Optional[CreatorTier]:
        """Get the next tier level"""
        tier_order = [CreatorTier.NEWCOMER, CreatorTier.BRONZE, CreatorTier.SILVER, 
                     CreatorTier.GOLD, CreatorTier.PLATINUM, CreatorTier.DIAMOND, 
                     CreatorTier.ELITE, CreatorTier.LEGEND]
        
        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                return tier_order[current_index + 1]
            return None
        except ValueError:
            return None
    
    async def _set_grace_periods(self, creator_id: str, tier: CreatorTier):
        """Set grace periods for tier requirements after demotion"""
        try:
            profile = self.tier_profiles[creator_id]
            requirements = self.tier_requirements.get(tier, [])
            
            for requirement in requirements:
                if requirement.grace_period_days > 0:
                    grace_end = datetime.now() + timedelta(days=requirement.grace_period_days)
                    profile.grace_periods[requirement.metric_type] = grace_end
            
        except Exception as e:
            logger.error(f"Error setting grace periods: {str(e)}")
    
    async def _generate_tier_recommendations(self, creator_id: str):
        """Generate tier improvement recommendations for creator"""
        try:
            profile = self.tier_profiles[creator_id]
            
            # Get next tier
            next_tier = await self._get_next_tier(profile.current_tier)
            if not next_tier:
                return  # Already at highest tier
            
            # Analyze gap to next tier
            next_tier_requirements = self.tier_requirements.get(next_tier, [])
            priority_metrics = []
            improvement_suggestions = []
            required_actions = []
            
            for requirement in next_tier_requirements:
                current_value = profile.metrics.get(requirement.metric_type, 0.0)
                gap = requirement.min_value - current_value
                
                if gap > 0:
                    priority_metrics.append(requirement.metric_type)
                    
                    # Generate specific suggestions
                    if requirement.metric_type == TierMetricType.FOLLOWER_COUNT:
                        improvement_suggestions.append(f"Gain {int(gap)} more followers through engaging content and cross-promotion")
                        required_actions.append({
                            "metric": requirement.metric_type.value,
                            "current": current_value,
                            "required": requirement.min_value,
                            "gap": gap,
                            "action": "Increase follower acquisition rate"
                        })
                    
                    elif requirement.metric_type == TierMetricType.ENGAGEMENT_RATE:
                        improvement_suggestions.append(f"Improve engagement rate by {gap:.2%} through interactive content and community building")
                        required_actions.append({
                            "metric": requirement.metric_type.value,
                            "current": current_value,
                            "required": requirement.min_value,
                            "gap": gap,
                            "action": "Create more engaging content"
                        })
                    
                    elif requirement.metric_type == TierMetricType.CONTENT_QUALITY:
                        improvement_suggestions.append(f"Enhance content quality score by {gap:.2f} points through better production value and storytelling")
                        required_actions.append({
                            "metric": requirement.metric_type.value,
                            "current": current_value,
                            "required": requirement.min_value,
                            "gap": gap,
                            "action": "Improve content production quality"
                        })
                    
                    elif requirement.metric_type == TierMetricType.PLATFORM_DIVERSITY:
                        improvement_suggestions.append(f"Expand to {int(gap)} more platform(s) to increase reach and diversification")
                        required_actions.append({
                            "metric": requirement.metric_type.value,
                            "current": current_value,
                            "required": requirement.min_value,
                            "gap": gap,
                            "action": "Join additional platforms"
                        })
            
            # Calculate success probability
            total_gaps = len(priority_metrics)
            met_requirements = len(next_tier_requirements) - total_gaps
            success_probability = met_requirements / len(next_tier_requirements) if next_tier_requirements else 0.0
            
            # Estimate timeline
            if total_gaps <= 2:
                timeline = "1-2 months"
            elif total_gaps <= 4:
                timeline = "3-6 months"
            else:
                timeline = "6+ months"
            
            # Create recommendation
            recommendation = TierRecommendation(
                recommendation_id=str(uuid.uuid4()),
                creator_id=creator_id,
                target_tier=next_tier,
                priority_metrics=priority_metrics,
                improvement_suggestions=improvement_suggestions[:5],  # Top 5
                estimated_timeline=timeline,
                success_probability=success_probability,
                required_actions=required_actions
            )
            
            # Store recommendation
            self.recommendations[creator_id] = [recommendation]  # Replace old recommendations
            
        except Exception as e:
            logger.error(f"Error generating tier recommendations: {str(e)}")
    
    async def get_creator_tier_profile(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive tier profile for creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            Creator tier profile data
        """
        try:
            if creator_id not in self.tier_profiles:
                return None
            
            profile = self.tier_profiles[creator_id]
            
            # Get recent metrics
            recent_metrics = []
            for metric in self.tier_metrics[creator_id][-10:]:  # Last 10 metrics
                recent_metrics.append({
                    "metric_type": metric.metric_type.value,
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "source": metric.source,
                    "verified": metric.verified
                })
            
            # Get current tier requirements
            current_requirements = self.tier_requirements.get(profile.current_tier, [])
            requirements_status = []
            
            for req in current_requirements:
                current_value = profile.metrics.get(req.metric_type, 0.0)
                is_met = current_value >= req.min_value
                
                if req.max_value:
                    is_met = is_met and current_value <= req.max_value
                
                requirements_status.append({
                    "metric_type": req.metric_type.value,
                    "requirement": f"{req.min_value}" + (f"-{req.max_value}" if req.max_value else "+"),
                    "current_value": current_value,
                    "is_met": is_met,
                    "is_mandatory": req.is_mandatory,
                    "weight": req.weight,
                    "description": req.description
                })
            
            # Get recommendations
            recommendations = []
            for rec in self.recommendations.get(creator_id, []):
                recommendations.append({
                    "target_tier": rec.target_tier.value,
                    "priority_metrics": [m.value for m in rec.priority_metrics],
                    "improvement_suggestions": rec.improvement_suggestions,
                    "estimated_timeline": rec.estimated_timeline,
                    "success_probability": rec.success_probability,
                    "required_actions": rec.required_actions
                })
            
            return {
                "creator_id": creator_id,
                "username": profile.username,
                "current_tier": profile.current_tier.value,
                "previous_tier": profile.previous_tier.value if profile.previous_tier else None,
                "tier_since": profile.tier_since.isoformat(),
                "progression_status": profile.progression_status.value,
                "tier_score": profile.tier_score,
                "next_tier_progress": profile.next_tier_progress,
                "metrics": {k.value: v for k, v in profile.metrics.items()},
                "benefits": [b.value for b in profile.benefits],
                "requirements_status": requirements_status,
                "recent_metrics": recent_metrics,
                "tier_history": profile.tier_history,
                "recommendations": recommendations,
                "last_evaluated": profile.last_evaluated.isoformat(),
                "created_at": profile.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting creator tier profile: {str(e)}")
            return None
    
    async def get_tier_analytics(self, timeframe: str = "30d") -> TierAnalytics:
        """Get tier system analytics
        
        Args:
            timeframe: Analytics timeframe
            
        Returns:
            Tier analytics data
        """
        try:
            # Parse timeframe
            days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
            days = days_map.get(timeframe, 30)
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Calculate tier distribution
            tier_distribution = defaultdict(int)
            for profile in self.tier_profiles.values():
                tier_distribution[profile.current_tier] += 1
            
            # Progression events in timeframe
            progression_events = {"promotion": 0, "demotion": 0, "evaluation": 0}
            for progression in self.progression_history:
                if progression.timestamp >= cutoff_date:
                    progression_events[progression.progression_type] += 1
            
            # Average tier duration
            tier_durations = defaultdict(list)
            for profile in self.tier_profiles.values():
                for history_entry in profile.tier_history:
                    tier = CreatorTier(history_entry["tier"])
                    start_date = datetime.fromisoformat(history_entry["start_date"])
                    end_date = datetime.fromisoformat(history_entry["end_date"])
                    duration = (end_date - start_date).days
                    tier_durations[tier].append(duration)
            
            average_tier_duration = {}
            for tier, durations in tier_durations.items():
                average_tier_duration[tier] = sum(durations) / len(durations) if durations else 0
            
            # Top performing metrics (most improved)
            metric_improvements = defaultdict(float)
            for creator_metrics in self.tier_metrics.values():
                recent_metrics = [m for m in creator_metrics if m.timestamp >= cutoff_date]
                for metric_type in TierMetricType:
                    type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
                    if len(type_metrics) >= 2:
                        improvement = type_metrics[-1].value - type_metrics[0].value
                        metric_improvements[metric_type] += improvement
            
            top_performing_metrics = sorted(
                metric_improvements.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            # Identify at-risk creators
            churn_risk_creators = []
            for creator_id, profile in self.tier_profiles.items():
                if profile.progression_status in [ProgressionStatus.AT_RISK, ProgressionStatus.DECLINING]:
                    churn_risk_creators.append(creator_id)
            
            # Calculate tier satisfaction (mock - based on progression status)
            tier_satisfaction_scores = {}
            for tier in CreatorTier:
                tier_creators = [p for p in self.tier_profiles.values() if p.current_tier == tier]
                if tier_creators:
                    # Mock satisfaction based on progression status
                    stable_count = len([p for p in tier_creators if p.progression_status == ProgressionStatus.STABLE])
                    satisfaction = (stable_count / len(tier_creators)) * 100
                    tier_satisfaction_scores[tier] = satisfaction
                else:
                    tier_satisfaction_scores[tier] = 0.0
            
            # System health score
            total_creators = len(self.tier_profiles)
            healthy_creators = len([p for p in self.tier_profiles.values() 
                                  if p.progression_status not in [ProgressionStatus.AT_RISK, ProgressionStatus.DECLINING]])
            system_health_score = (healthy_creators / total_creators * 100) if total_creators > 0 else 100.0
            
            return TierAnalytics(
                timeframe=timeframe,
                total_creators=total_creators,
                tier_distribution=dict(tier_distribution),
                progression_events=progression_events,
                average_tier_duration=average_tier_duration,
                top_performing_metrics=[m[0] for m in top_performing_metrics],
                churn_risk_creators=churn_risk_creators,
                tier_satisfaction_scores=tier_satisfaction_scores,
                system_health_score=system_health_score
            )
            
        except Exception as e:
            logger.error(f"Error getting tier analytics: {str(e)}")
            return TierAnalytics(
                timeframe=timeframe,
                total_creators=0,
                tier_distribution={},
                progression_events={},
                average_tier_duration={},
                top_performing_metrics=[],
                churn_risk_creators=[],
                tier_satisfaction_scores={},
                system_health_score=0.0
            )
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and performance metrics
        
        Returns:
            System health information
        """
        try:
            return {
                "total_creators": len(self.tier_profiles),
                "tier_distribution": {
                    tier.value: len([p for p in self.tier_profiles.values() if p.current_tier == tier])
                    for tier in CreatorTier
                },
                "evaluation_queue_size": len(self.evaluation_queue),
                "total_progression_events": len(self.progression_history),
                "total_metrics_recorded": sum(len(metrics) for metrics in self.tier_metrics.values()),
                "tier_requirements_count": sum(len(reqs) for reqs in self.tier_requirements.values()),
                "auto_progression_enabled": self.evaluation_settings["auto_progression_enabled"],
                "evaluation_interval": self.evaluation_settings["evaluation_interval"],
                "system_status": "operational",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {"status": "error", "message": str(e)}

# Export main class and types
__all__ = [
    'CreatorTierIntelligenceManagementSystem',
    'CreatorTier',
    'TierMetricType',
    'TierBenefit',
    'ProgressionStatus',
    'TierRequirement',
    'TierMetric',
    'CreatorTierProfile',
    'TierProgression',
    'TierAnalytics',
    'TierRecommendation'
]