"""
Enterprise Feature Flag Manager for ML Models
DevOps + Backend Senior implementation with gradual rollout capabilities
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
import random
from abc import ABC, abstractmethod
from collections import defaultdict

logger = logging.getLogger(__name__)


class FeatureFlagType(Enum):
    """Types of feature flags"""
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    WHITELIST = "whitelist"
    EXPERIMENT = "experiment"
    GRADUAL_ROLLOUT = "gradual_rollout"


class FeatureFlagStatus(Enum):
    """Feature flag status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    SCHEDULED = "scheduled"
    EXPIRED = "expired"


class TargetingRule(Enum):
    """Targeting rules for feature flags"""
    USER_ID = "user_id"
    CREATOR_TYPE = "creator_type"
    CREATOR_TIER = "creator_tier"
    GEOGRAPHIC_REGION = "geographic_region"
    USER_AGENT = "user_agent"
    CUSTOM_ATTRIBUTE = "custom_attribute"


@dataclass
class FeatureFlag:
    """Feature flag configuration"""
    flag_id: str
    name: str
    description: str
    flag_type: FeatureFlagType
    status: FeatureFlagStatus
    default_value: Any = False
    rollout_percentage: float = 0.0
    targeting_rules: Dict[TargetingRule, Any] = field(default_factory=dict)
    creator_type_overrides: Dict[str, Any] = field(default_factory=dict)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)


@dataclass
class FeatureFlagEvaluation:
    """Feature flag evaluation result"""
    flag_id: str
    user_id: str
    value: Any
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    targeting_matched: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureFlagMetrics:
    """Feature flag usage metrics"""
    flag_id: str
    total_evaluations: int = 0
    true_evaluations: int = 0
    false_evaluations: int = 0
    unique_users: int = 0
    creator_type_breakdown: Dict[str, int] = field(default_factory=dict)
    performance_impact: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class FeatureFlagManager:
    """Enterprise feature flag manager for ML model deployments"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self.evaluations: List[FeatureFlagEvaluation] = []
        self.metrics: Dict[str, FeatureFlagMetrics] = {}
        self.user_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=5)
        
        # Creator-specific feature management
        self.creator_feature_categories = {
            'musicians': {
                'audio_processing_v2': 'model_enhancement',
                'collaboration_matching': 'feature_enhancement',
                'real_time_mixing': 'new_feature',
                'advanced_monetization': 'business_feature'
            },
            'photographers': {
                'ai_style_transfer': 'model_enhancement',
                'portfolio_optimization': 'feature_enhancement',
                'market_analysis': 'analytics_feature',
                'brand_matching': 'business_feature'
            },
            'bloggers': {
                'content_generation_v3': 'model_enhancement',
                'seo_optimization': 'feature_enhancement',
                'viral_prediction': 'analytics_feature',
                'monetization_tools': 'business_feature'
            },
            'influencers': {
                'multi_platform_sync': 'integration_feature',
                'audience_insights': 'analytics_feature',
                'trending_detection': 'model_enhancement',
                'brand_partnerships': 'business_feature'
            },
            'comedians': {
                'timing_analysis': 'model_enhancement',
                'audience_reaction': 'analytics_feature',
                'venue_optimization': 'business_feature',
                'performance_insights': 'analytics_feature'
            }
        }
        
    async def initialize(self) -> bool:
        """Initialize feature flag manager"""
        try:
            logger.info("Initializing Feature Flag Manager...")
            
            # Setup default feature flags
            await self._setup_default_flags()
            
            # Initialize metrics tracking
            await self._setup_metrics_tracking()
            
            # Start cache cleanup
            asyncio.create_task(self._cleanup_cache())
            
            logger.info("Feature Flag Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Feature Flag Manager: {e}")
            return False
    
    async def create_feature_flag(self, feature_flag: FeatureFlag) -> bool:
        """Create new feature flag"""
        try:
            self.feature_flags[feature_flag.flag_id] = feature_flag
            
            # Initialize metrics
            self.metrics[feature_flag.flag_id] = FeatureFlagMetrics(
                flag_id=feature_flag.flag_id
            )
            
            logger.info(f"Created feature flag: {feature_flag.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create feature flag: {e}")
            return False
    
    async def update_feature_flag(self, flag_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing feature flag"""
        try:
            if flag_id not in self.feature_flags:
                return False
            
            flag = self.feature_flags[flag_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(flag, key):
                    setattr(flag, key, value)
            
            flag.updated_at = datetime.utcnow()
            
            # Clear cache for affected users
            self.user_cache.clear()
            
            logger.info(f"Updated feature flag: {flag_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update feature flag: {e}")
            return False
    
    async def evaluate_feature_flag(self, 
                                  flag_id: str,
                                  user_id: str,
                                  user_context: Optional[Dict[str, Any]] = None) -> FeatureFlagEvaluation:
        """Evaluate feature flag for specific user"""
        try:
            # Check cache first
            cache_key = f"{flag_id}_{user_id}"
            if cache_key in self.user_cache:
                cached = self.user_cache[cache_key]
                if datetime.utcnow() - cached['timestamp'] < self.cache_ttl:
                    return cached['evaluation']
            
            if flag_id not in self.feature_flags:
                return FeatureFlagEvaluation(
                    flag_id=flag_id,
                    user_id=user_id,
                    value=False,
                    reason="Flag not found"
                )
            
            flag = self.feature_flags[flag_id]
            
            # Check if flag is active
            if flag.status != FeatureFlagStatus.ACTIVE:
                return FeatureFlagEvaluation(
                    flag_id=flag_id,
                    user_id=user_id,
                    value=flag.default_value,
                    reason=f"Flag status: {flag.status.value}"
                )
            
            # Check date constraints
            now = datetime.utcnow()
            if flag.start_date and now < flag.start_date:
                return FeatureFlagEvaluation(
                    flag_id=flag_id,
                    user_id=user_id,
                    value=flag.default_value,
                    reason="Not yet started"
                )
            
            if flag.end_date and now > flag.end_date:
                return FeatureFlagEvaluation(
                    flag_id=flag_id,
                    user_id=user_id,
                    value=flag.default_value,
                    reason="Expired"
                )
            
            # Evaluate based on flag type
            evaluation = await self._evaluate_by_type(flag, user_id, user_context)
            
            # Cache result
            self.user_cache[cache_key] = {
                'evaluation': evaluation,
                'timestamp': datetime.utcnow()
            }
            
            # Update metrics
            await self._update_flag_metrics(evaluation, user_context)
            
            # Store evaluation
            self.evaluations.append(evaluation)
            
            # Keep only recent evaluations (last 24 hours)
            cutoff = datetime.utcnow() - timedelta(hours=24)
            self.evaluations = [e for e in self.evaluations if e.timestamp >= cutoff]
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Failed to evaluate feature flag: {e}")
            return FeatureFlagEvaluation(
                flag_id=flag_id,
                user_id=user_id,
                value=False,
                reason=f"Evaluation error: {str(e)}"
            )
    
    async def get_feature_flags(self, 
                              status_filter: Optional[FeatureFlagStatus] = None,
                              creator_type: Optional[str] = None) -> List[FeatureFlag]:
        """Get feature flags with optional filters"""
        try:
            flags = list(self.feature_flags.values())
            
            if status_filter:
                flags = [f for f in flags if f.status == status_filter]
            
            if creator_type:
                # Filter by creator-relevant flags
                relevant_flags = []
                for flag in flags:
                    if creator_type in flag.creator_type_overrides:
                        relevant_flags.append(flag)
                    elif any(tag.startswith(creator_type) for tag in flag.tags):
                        relevant_flags.append(flag)
                flags = relevant_flags
            
            return flags
            
        except Exception as e:
            logger.error(f"Failed to get feature flags: {e}")
            return []
    
    async def get_flag_metrics(self, flag_id: str) -> Optional[FeatureFlagMetrics]:
        """Get metrics for specific feature flag"""
        try:
            return self.metrics.get(flag_id)
            
        except Exception as e:
            logger.error(f"Failed to get flag metrics: {e}")
            return None
    
    async def gradual_rollout(self, 
                            flag_id: str,
                            target_percentage: float,
                            rollout_steps: int = 5,
                            step_duration: timedelta = timedelta(hours=1)) -> bool:
        """Perform gradual rollout of feature flag"""
        try:
            if flag_id not in self.feature_flags:
                return False
            
            flag = self.feature_flags[flag_id]
            current_percentage = flag.rollout_percentage
            step_size = (target_percentage - current_percentage) / rollout_steps
            
            logger.info(f"Starting gradual rollout for {flag_id}: {current_percentage}% -> {target_percentage}%")
            
            for step in range(rollout_steps):
                new_percentage = current_percentage + (step_size * (step + 1))
                
                # Update rollout percentage
                await self.update_feature_flag(flag_id, {
                    'rollout_percentage': new_percentage
                })
                
                logger.info(f"Rollout step {step + 1}/{rollout_steps}: {new_percentage:.1f}%")
                
                # Wait for step duration (except last step)
                if step < rollout_steps - 1:
                    await asyncio.sleep(step_duration.total_seconds())
                
                # Check for issues during rollout
                metrics = await self.get_flag_metrics(flag_id)
                if metrics and await self._check_rollout_health(flag_id, metrics):
                    logger.warning(f"Health check failed during rollout of {flag_id}")
                    # Could implement automatic rollback here
            
            logger.info(f"Gradual rollout completed for {flag_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to perform gradual rollout: {e}")
            return False
    
    async def emergency_disable(self, flag_id: str, reason: str) -> bool:
        """Emergency disable feature flag"""
        try:
            if flag_id not in self.feature_flags:
                return False
            
            await self.update_feature_flag(flag_id, {
                'status': FeatureFlagStatus.PAUSED,
                'rollout_percentage': 0.0
            })
            
            # Clear all cached evaluations
            self.user_cache.clear()
            
            logger.warning(f"Emergency disabled feature flag {flag_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to emergency disable feature flag: {e}")
            return False
    
    async def get_user_flags(self, 
                           user_id: str,
                           user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get all applicable feature flags for a user"""
        try:
            user_flags = {}
            
            for flag_id in self.feature_flags.keys():
                evaluation = await self.evaluate_feature_flag(flag_id, user_id, user_context)
                user_flags[flag_id] = evaluation.value
            
            return user_flags
            
        except Exception as e:
            logger.error(f"Failed to get user flags: {e}")
            return {}
    
    async def _setup_default_flags(self) -> None:
        """Setup default feature flags for different creator types"""
        
        # Model enhancement flags
        for creator_type in self.creator_feature_categories:
            for feature, category in self.creator_feature_categories[creator_type].items():
                flag = FeatureFlag(
                    flag_id=f"{creator_type}_{feature}",
                    name=f"{creator_type.title()} {feature.replace('_', ' ').title()}",
                    description=f"{category} for {creator_type}",
                    flag_type=FeatureFlagType.PERCENTAGE,
                    status=FeatureFlagStatus.ACTIVE,
                    rollout_percentage=0.0,
                    creator_type_overrides={creator_type: True},
                    tags=[creator_type, category]
                )
                await self.create_feature_flag(flag)
    
    async def _setup_metrics_tracking(self) -> None:
        """Setup metrics tracking for feature flags"""
        for flag_id in self.feature_flags:
            if flag_id not in self.metrics:
                self.metrics[flag_id] = FeatureFlagMetrics(flag_id=flag_id)
    
    async def _evaluate_by_type(self, 
                              flag: FeatureFlag,
                              user_id: str,
                              user_context: Optional[Dict[str, Any]]) -> FeatureFlagEvaluation:
        """Evaluate feature flag based on its type"""
        
        if flag.flag_type == FeatureFlagType.BOOLEAN:
            return FeatureFlagEvaluation(
                flag_id=flag.flag_id,
                user_id=user_id,
                value=flag.default_value,
                reason="Boolean flag"
            )
        
        elif flag.flag_type == FeatureFlagType.PERCENTAGE:
            # Hash user ID for consistent assignment
            user_hash = int(hashlib.md5(f"{flag.flag_id}_{user_id}".encode()).hexdigest(), 16)
            user_percentage = (user_hash % 100) + 1
            
            in_rollout = user_percentage <= flag.rollout_percentage
            
            return FeatureFlagEvaluation(
                flag_id=flag.flag_id,
                user_id=user_id,
                value=in_rollout,
                reason=f"Percentage rollout: {user_percentage}% <= {flag.rollout_percentage}%"
            )
        
        elif flag.flag_type == FeatureFlagType.WHITELIST:
            # Check targeting rules
            return await self._evaluate_targeting_rules(flag, user_id, user_context)
        
        elif flag.flag_type == FeatureFlagType.EXPERIMENT:
            # A/B test logic
            return await self._evaluate_experiment(flag, user_id, user_context)
        
        elif flag.flag_type == FeatureFlagType.GRADUAL_ROLLOUT:
            # Similar to percentage but with additional safety checks
            return await self._evaluate_gradual_rollout(flag, user_id, user_context)
        
        else:
            return FeatureFlagEvaluation(
                flag_id=flag.flag_id,
                user_id=user_id,
                value=flag.default_value,
                reason="Unknown flag type"
            )
    
    async def _evaluate_targeting_rules(self, 
                                      flag: FeatureFlag,
                                      user_id: str,
                                      user_context: Optional[Dict[str, Any]]) -> FeatureFlagEvaluation:
        """Evaluate targeting rules"""
        if not user_context:
            return FeatureFlagEvaluation(
                flag_id=flag.flag_id,
                user_id=user_id,
                value=flag.default_value,
                reason="No user context provided"
            )
        
        matched_rules = {}
        
        for rule, criteria in flag.targeting_rules.items():
            if rule == TargetingRule.CREATOR_TYPE:
                creator_type = user_context.get('creator_type')
                if creator_type in criteria:
                    matched_rules[rule.value] = True
                    # Check for creator-specific override
                    if creator_type in flag.creator_type_overrides:
                        return FeatureFlagEvaluation(
                            flag_id=flag.flag_id,
                            user_id=user_id,
                            value=flag.creator_type_overrides[creator_type],
                            reason=f"Creator type override: {creator_type}",
                            targeting_matched=matched_rules
                        )
        
        # If any rules matched, return true
        if matched_rules:
            return FeatureFlagEvaluation(
                flag_id=flag.flag_id,
                user_id=user_id,
                value=True,
                reason="Targeting rules matched",
                targeting_matched=matched_rules
            )
        
        return FeatureFlagEvaluation(
            flag_id=flag.flag_id,
            user_id=user_id,
            value=flag.default_value,
            reason="No targeting rules matched"
        )
    
    async def _evaluate_experiment(self, 
                                 flag: FeatureFlag,
                                 user_id: str,
                                 user_context: Optional[Dict[str, Any]]) -> FeatureFlagEvaluation:
        """Evaluate A/B experiment flag"""
        # Simple A/B split based on user ID hash
        user_hash = int(hashlib.md5(f"{flag.flag_id}_{user_id}".encode()).hexdigest(), 16)
        variant = 'A' if user_hash % 2 == 0 else 'B'
        
        # For now, variant A gets the feature, variant B doesn't
        value = variant == 'A'
        
        return FeatureFlagEvaluation(
            flag_id=flag.flag_id,
            user_id=user_id,
            value=value,
            reason=f"Experiment variant: {variant}"
        )
    
    async def _evaluate_gradual_rollout(self, 
                                      flag: FeatureFlag,
                                      user_id: str,
                                      user_context: Optional[Dict[str, Any]]) -> FeatureFlagEvaluation:
        """Evaluate gradual rollout flag with safety checks"""
        # Similar to percentage but with additional safety
        user_hash = int(hashlib.md5(f"{flag.flag_id}_{user_id}".encode()).hexdigest(), 16)
        user_percentage = (user_hash % 100) + 1
        
        # Check current system health before enabling
        if await self._check_system_health():
            in_rollout = user_percentage <= flag.rollout_percentage
        else:
            in_rollout = False  # Don't enable new features if system is unhealthy
        
        return FeatureFlagEvaluation(
            flag_id=flag.flag_id,
            user_id=user_id,
            value=in_rollout,
            reason=f"Gradual rollout: {user_percentage}% <= {flag.rollout_percentage}%"
        )
    
    async def _update_flag_metrics(self, 
                                 evaluation -> None: FeatureFlagEvaluation,
                                 user_context -> None: Optional[Dict[str, Any]]) -> None:
        """Update metrics for feature flag evaluation"""
        try:
            flag_id = evaluation.flag_id
            if flag_id not in self.metrics:
                self.metrics[flag_id] = FeatureFlagMetrics(flag_id=flag_id)
            
            metrics = self.metrics[flag_id]
            metrics.total_evaluations += 1
            
            if evaluation.value:
                metrics.true_evaluations += 1
            else:
                metrics.false_evaluations += 1
            
            # Track by creator type
            if user_context and 'creator_type' in user_context:
                creator_type = user_context['creator_type']
                if creator_type not in metrics.creator_type_breakdown:
                    metrics.creator_type_breakdown[creator_type] = 0
                metrics.creator_type_breakdown[creator_type] += 1
            
            metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update flag metrics: {e}")
    
    async def _check_rollout_health(self, flag_id: str, metrics: FeatureFlagMetrics) -> bool:
        """Check if rollout is healthy (returns True if unhealthy)"""
        # Simple health check - could be expanded with actual monitoring data
        if metrics.total_evaluations > 1000:
            error_rate = metrics.false_evaluations / metrics.total_evaluations
            return error_rate > 0.1  # 10% error rate threshold
        return False
    
    async def _check_system_health(self) -> bool:
        """Check overall system health before enabling features"""
        # Simplified health check - in real implementation, this would check actual system metrics
        return True
    
    async def _cleanup_cache(self) -> None:
        """Cleanup expired cache entries"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_keys = []
                
                for key, value in self.user_cache.items():
                    if current_time - value['timestamp'] > self.cache_ttl:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.user_cache[key]
                
                # Sleep for cache TTL duration
                await asyncio.sleep(self.cache_ttl.total_seconds())
                
            except Exception as e:
                logger.error(f"Cache cleanup failed: {e}")
                await asyncio.sleep(300)  # 5 minutes


# Creator-specific feature flag management
class CreatorFeatureFlagManager:
    """Creator-specific feature flag management"""
    
    @staticmethod
    async def setup_musician_flags(flag_manager: FeatureFlagManager) -> bool:
        """Setup feature flags optimized for musicians"""
        
        # Advanced audio processing flag
        audio_v2_flag = FeatureFlag(
            flag_id="musicians_audio_processing_v2",
            name="Advanced Audio Processing V2",
            description="Next-generation audio processing with AI enhancement",
            flag_type=FeatureFlagType.GRADUAL_ROLLOUT,
            status=FeatureFlagStatus.ACTIVE,
            rollout_percentage=10.0,
            creator_type_overrides={'musicians': True},
            tags=['musicians', 'audio', 'ml_model']
        )
        
        return await flag_manager.create_feature_flag(audio_v2_flag)
    
    @staticmethod
    async def setup_photographer_flags(flag_manager: FeatureFlagManager) -> bool:
        """Setup feature flags optimized for photographers"""
        
        # AI style transfer flag
        style_flag = FeatureFlag(
            flag_id="photographers_ai_style_transfer",
            name="AI Style Transfer",
            description="AI-powered style transfer for professional photography",
            flag_type=FeatureFlagType.PERCENTAGE,
            status=FeatureFlagStatus.ACTIVE,
            rollout_percentage=25.0,
            creator_type_overrides={'photographers': True},
            tags=['photographers', 'ai', 'image_processing']
        )
        
        return await flag_manager.create_feature_flag(style_flag)


# Example usage and testing
async def main() -> None:
    """Example usage of Feature Flag Manager"""
    manager = FeatureFlagManager()
    
    # Initialize
    await manager.initialize()
    
    # Setup creator-specific flags
    await CreatorFeatureFlagManager.setup_musician_flags(manager)
    await CreatorFeatureFlagManager.setup_photographer_flags(manager)
    
    # Test evaluation
    user_context = {
        'creator_type': 'musicians',
        'tier': 'premium',
        'region': 'US'
    }
    
    evaluation = await manager.evaluate_feature_flag(
        "musicians_audio_processing_v2",
        "user123",
        user_context
    )
    
    print(f"Feature Flag Evaluation: {evaluation}")
    
    # Get all flags for user
    user_flags = await manager.get_user_flags("user123", user_context)
    print(f"User Flags: {user_flags}")


if __name__ == "__main__":
    asyncio.run(main())