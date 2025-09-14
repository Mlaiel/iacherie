"""
Content Amplification Configuration for Ainflue Distribution
Provides enterprise-grade configuration for content amplification strategies

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field, validator

# Configure logging
logger = logging.getLogger(__name__)


class AmplificationStrategy(str, Enum):
    """Content amplification strategies"""
    ORGANIC_GROWTH = "organic_growth"
    PAID_BOOST = "paid_boost"
    INFLUENCER_NETWORK = "influencer_network"
    CROSS_PROMOTION = "cross_promotion"
    COMMUNITY_BUILDING = "community_building"
    VIRAL_ENGINEERING = "viral_engineering"
    ALGORITHMIC_OPTIMIZATION = "algorithmic_optimization"
    ENGAGEMENT_MULTIPLICATION = "engagement_multiplication"


class AmplificationTier(str, Enum):
    """Amplification service tiers"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    VIRAL = "viral"


class TargetingMode(str, Enum):
    """Audience targeting modes"""
    BROAD = "broad"
    SPECIFIC = "specific"
    LOOKALIKE = "lookalike"
    RETARGETING = "retargeting"
    BEHAVIORAL = "behavioral"
    INTEREST_BASED = "interest_based"
    DEMOGRAPHIC = "demographic"
    GEOGRAPHIC = "geographic"


@dataclass
class AmplificationBudget:
    """Amplification budget configuration"""
    daily_budget: float = 100.0
    campaign_budget: float = 1000.0
    emergency_budget: float = 500.0
    auto_scaling: bool = True
    budget_allocation: Dict[str, float] = field(default_factory=lambda: {
        'organic': 0.3,
        'paid_boost': 0.4,
        'influencer': 0.2,
        'cross_promotion': 0.1
    })
    roi_threshold: float = 2.0
    max_spend_per_content: float = 200.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EngagementTargets:
    """Engagement targeting configuration"""
    min_engagement_rate: float = 0.05  # 5%
    target_engagement_rate: float = 0.15  # 15%
    viral_engagement_threshold: float = 0.30  # 30%
    comments_to_likes_ratio: float = 0.1  # 10%
    shares_to_likes_ratio: float = 0.05  # 5%
    save_rate_target: float = 0.08  # 8%
    click_through_rate_target: float = 0.12  # 12%
    conversion_rate_target: float = 0.03  # 3%
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CrossPromotionSettings:
    """Cross-promotion configuration"""
    enabled: bool = True
    min_audience_overlap: float = 0.1  # 10%
    max_audience_overlap: float = 0.7  # 70%
    collaboration_frequency: str = "weekly"  # daily, weekly, monthly
    revenue_sharing: Dict[str, float] = field(default_factory=lambda: {
        'initiator': 0.6,
        'partner': 0.4
    })
    content_quality_threshold: float = 0.8
    brand_safety_check: bool = True
    auto_match_creators: bool = True
    max_partners_per_campaign: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ViralOptimizationSettings:
    """Viral optimization configuration"""
    viral_prediction_enabled: bool = True
    auto_viral_boost: bool = True
    viral_threshold: float = 0.8
    momentum_tracking: bool = True
    trend_surfing: bool = True
    hashtag_optimization: bool = True
    timing_optimization: bool = True
    network_analysis: bool = True
    cascade_amplification: bool = True
    emergency_viral_budget: float = 1000.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlatformAmplificationSettings:
    """Platform-specific amplification settings"""
    platform: str
    enabled: bool = True
    strategy: AmplificationStrategy = AmplificationStrategy.ORGANIC_GROWTH
    budget_allocation: float = 0.25  # 25% of total budget
    target_audience_size: int = 100000
    targeting_mode: TargetingMode = TargetingMode.BROAD
    boost_multiplier: float = 1.0
    engagement_weight: float = 1.0
    reach_weight: float = 1.0
    conversion_weight: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AmplificationConfig:
    """
    Comprehensive configuration for content amplification
    Manages strategies, budgets, targeting, and optimization settings
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "amplification_config.json"
        )
        
        # Core amplification settings
        self.tier: AmplificationTier = AmplificationTier.PROFESSIONAL
        self.budget: AmplificationBudget = AmplificationBudget()
        self.engagement_targets: EngagementTargets = EngagementTargets()
        self.cross_promotion: CrossPromotionSettings = CrossPromotionSettings()
        self.viral_optimization: ViralOptimizationSettings = ViralOptimizationSettings()
        
        # Platform-specific settings
        self.platform_settings: Dict[str, PlatformAmplificationSettings] = {}
        
        # Advanced settings
        self.ai_optimization_enabled: bool = True
        self.real_time_adjustment: bool = True
        self.performance_learning: bool = True
        self.auto_scaling: bool = True
        self.risk_management: bool = True
        
        # Monitoring and alerts
        self.performance_monitoring: bool = True
        self.alert_thresholds: Dict[str, float] = {
            'low_engagement': 0.02,
            'high_spend': 1.5,  # 150% of budget
            'poor_roi': 0.5,
            'viral_opportunity': 0.8
        }
        
        # Initialize with defaults
        self._load_default_config()
        
        # Load saved configuration if exists
        if os.path.exists(self.config_path):
            self.load_config()
            
    def _load_default_config(self) -> None:
        """Load default amplification configuration"""
        
        # Default platform settings
        default_platforms = [
            'instagram', 'tiktok', 'youtube', 'twitter', 'facebook',
            'linkedin', 'snapchat', 'pinterest', 'reddit', 'discord'
        ]
        
        for platform in default_platforms:
            self.platform_settings[platform] = PlatformAmplificationSettings(
                platform=platform,
                enabled=True,
                strategy=self._get_default_strategy(platform),
                budget_allocation=1.0 / len(default_platforms),
                target_audience_size=self._get_default_audience_size(platform),
                targeting_mode=self._get_default_targeting_mode(platform)
            )
            
        logger.info(f"Loaded default config for {len(default_platforms)} platforms")
        
    def _get_default_strategy(self, platform: str) -> AmplificationStrategy:
        """Get default strategy for platform"""
        strategy_map = {
            'instagram': AmplificationStrategy.VIRAL_ENGINEERING,
            'tiktok': AmplificationStrategy.VIRAL_ENGINEERING,
            'youtube': AmplificationStrategy.ALGORITHMIC_OPTIMIZATION,
            'twitter': AmplificationStrategy.ENGAGEMENT_MULTIPLICATION,
            'facebook': AmplificationStrategy.PAID_BOOST,
            'linkedin': AmplificationStrategy.COMMUNITY_BUILDING,
            'snapchat': AmplificationStrategy.ORGANIC_GROWTH,
            'pinterest': AmplificationStrategy.CROSS_PROMOTION,
            'reddit': AmplificationStrategy.COMMUNITY_BUILDING,
            'discord': AmplificationStrategy.COMMUNITY_BUILDING
        }
        return strategy_map.get(platform, AmplificationStrategy.ORGANIC_GROWTH)
        
    def _get_default_audience_size(self, platform: str) -> int:
        """Get default target audience size for platform"""
        size_map = {
            'instagram': 500000,
            'tiktok': 1000000,
            'youtube': 200000,
            'twitter': 300000,
            'facebook': 800000,
            'linkedin': 100000,
            'snapchat': 400000,
            'pinterest': 150000,
            'reddit': 50000,
            'discord': 25000
        }
        return size_map.get(platform, 100000)
        
    def _get_default_targeting_mode(self, platform: str) -> TargetingMode:
        """Get default targeting mode for platform"""
        targeting_map = {
            'instagram': TargetingMode.INTEREST_BASED,
            'tiktok': TargetingMode.BEHAVIORAL,
            'youtube': TargetingMode.DEMOGRAPHIC,
            'twitter': TargetingMode.INTEREST_BASED,
            'facebook': TargetingMode.LOOKALIKE,
            'linkedin': TargetingMode.DEMOGRAPHIC,
            'snapchat': TargetingMode.GEOGRAPHIC,
            'pinterest': TargetingMode.INTEREST_BASED,
            'reddit': TargetingMode.COMMUNITY_BASED,
            'discord': TargetingMode.COMMUNITY_BASED
        }
        return targeting_map.get(platform, TargetingMode.BROAD)
        
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # Load tier
            self.tier = AmplificationTier(config_data.get('tier', 'professional'))
            
            # Load budget settings
            if 'budget' in config_data:
                budget_data = config_data['budget']
                self.budget = AmplificationBudget(**budget_data)
                
            # Load engagement targets
            if 'engagement_targets' in config_data:
                engagement_data = config_data['engagement_targets']
                self.engagement_targets = EngagementTargets(**engagement_data)
                
            # Load cross-promotion settings
            if 'cross_promotion' in config_data:
                cross_promo_data = config_data['cross_promotion']
                self.cross_promotion = CrossPromotionSettings(**cross_promo_data)
                
            # Load viral optimization settings
            if 'viral_optimization' in config_data:
                viral_data = config_data['viral_optimization']
                self.viral_optimization = ViralOptimizationSettings(**viral_data)
                
            # Load platform settings
            if 'platform_settings' in config_data:
                for platform, platform_data in config_data['platform_settings'].items():
                    self.platform_settings[platform] = PlatformAmplificationSettings(
                        platform=platform, **platform_data
                    )
                    
            # Load advanced settings
            self.ai_optimization_enabled = config_data.get('ai_optimization_enabled', True)
            self.real_time_adjustment = config_data.get('real_time_adjustment', True)
            self.performance_learning = config_data.get('performance_learning', True)
            self.auto_scaling = config_data.get('auto_scaling', True)
            self.risk_management = config_data.get('risk_management', True)
            
            # Load monitoring settings
            self.performance_monitoring = config_data.get('performance_monitoring', True)
            if 'alert_thresholds' in config_data:
                self.alert_thresholds.update(config_data['alert_thresholds'])
                
            logger.info(f"Amplification configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load amplification config: {e}")
            return False
            
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            config_data = {
                'tier': self.tier.value,
                'budget': self.budget.to_dict(),
                'engagement_targets': self.engagement_targets.to_dict(),
                'cross_promotion': self.cross_promotion.to_dict(),
                'viral_optimization': self.viral_optimization.to_dict(),
                'platform_settings': {
                    platform: settings.to_dict()
                    for platform, settings in self.platform_settings.items()
                },
                'ai_optimization_enabled': self.ai_optimization_enabled,
                'real_time_adjustment': self.real_time_adjustment,
                'performance_learning': self.performance_learning,
                'auto_scaling': self.auto_scaling,
                'risk_management': self.risk_management,
                'performance_monitoring': self.performance_monitoring,
                'alert_thresholds': self.alert_thresholds,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Amplification configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save amplification config: {e}")
            return False
            
    def get_platform_config(self, platform: str) -> Optional[PlatformAmplificationSettings]:
        """Get configuration for specific platform"""
        return self.platform_settings.get(platform)
        
    def set_platform_config(self, platform: str, settings: PlatformAmplificationSettings) -> bool:
        """Set configuration for specific platform"""
        try:
            self.platform_settings[platform] = settings
            logger.info(f"Updated amplification config for platform: {platform}")
            return True
        except Exception as e:
            logger.error(f"Failed to set platform config: {e}")
            return False
            
    def get_budget_allocation(self, platform: str) -> float:
        """Get budget allocation for platform"""
        if platform in self.platform_settings:
            total_budget = self.budget.daily_budget
            allocation_percent = self.platform_settings[platform].budget_allocation
            return total_budget * allocation_percent
        return 0.0
        
    def set_budget_allocation(self, platform: str, allocation: float) -> bool:
        """Set budget allocation for platform"""
        try:
            if platform in self.platform_settings:
                self.platform_settings[platform].budget_allocation = allocation
                
                # Ensure total allocation doesn't exceed 100%
                total_allocation = sum(
                    settings.budget_allocation 
                    for settings in self.platform_settings.values()
                )
                
                if total_allocation > 1.0:
                    # Normalize allocations
                    for settings in self.platform_settings.values():
                        settings.budget_allocation /= total_allocation
                        
                logger.info(f"Updated budget allocation for {platform}: {allocation:.2%}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to set budget allocation: {e}")
            return False
            
    def get_amplification_strategy(self, platform: str, content_type: str = None) -> AmplificationStrategy:
        """Get amplification strategy for platform and content type"""
        if platform in self.platform_settings:
            base_strategy = self.platform_settings[platform].strategy
            
            # Adjust strategy based on content type
            if content_type:
                return self._adjust_strategy_for_content(base_strategy, content_type)
                
            return base_strategy
            
        return AmplificationStrategy.ORGANIC_GROWTH
        
    def _adjust_strategy_for_content(self, base_strategy: AmplificationStrategy, 
                                   content_type: str) -> AmplificationStrategy:
        """Adjust strategy based on content type"""
        
        # Strategy adjustments for different content types
        adjustments = {
            'video': {
                AmplificationStrategy.ORGANIC_GROWTH: AmplificationStrategy.VIRAL_ENGINEERING,
                AmplificationStrategy.COMMUNITY_BUILDING: AmplificationStrategy.ENGAGEMENT_MULTIPLICATION
            },
            'image': {
                AmplificationStrategy.VIRAL_ENGINEERING: AmplificationStrategy.CROSS_PROMOTION,
                AmplificationStrategy.ALGORITHMIC_OPTIMIZATION: AmplificationStrategy.ENGAGEMENT_MULTIPLICATION
            },
            'text': {
                AmplificationStrategy.VIRAL_ENGINEERING: AmplificationStrategy.COMMUNITY_BUILDING,
                AmplificationStrategy.PAID_BOOST: AmplificationStrategy.ENGAGEMENT_MULTIPLICATION
            },
            'audio': {
                AmplificationStrategy.CROSS_PROMOTION: AmplificationStrategy.COMMUNITY_BUILDING,
                AmplificationStrategy.ORGANIC_GROWTH: AmplificationStrategy.INFLUENCER_NETWORK
            }
        }
        
        if content_type in adjustments and base_strategy in adjustments[content_type]:
            return adjustments[content_type][base_strategy]
            
        return base_strategy
        
    def should_amplify_content(self, performance_metrics: Dict[str, Any]) -> bool:
        """Determine if content should be amplified based on performance"""
        try:
            engagement_rate = performance_metrics.get('engagement_rate', 0)
            reach = performance_metrics.get('reach', 0)
            viral_score = performance_metrics.get('viral_score', 0)
            roi = performance_metrics.get('roi', 0)
            
            # Check engagement threshold
            if engagement_rate < self.engagement_targets.min_engagement_rate:
                return False
                
            # Check viral potential
            if viral_score >= self.viral_optimization.viral_threshold:
                return True
                
            # Check ROI
            if roi >= self.budget.roi_threshold:
                return True
                
            # Check if targeting engagement goals
            if engagement_rate >= self.engagement_targets.target_engagement_rate:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Amplification decision error: {e}")
            return False
            
    def get_amplification_budget(self, platform: str, content_urgency: str = "normal") -> float:
        """Get amplification budget for specific content"""
        base_budget = self.get_budget_allocation(platform)
        
        # Adjust based on urgency
        urgency_multipliers = {
            'low': 0.5,
            'normal': 1.0,
            'high': 1.5,
            'viral': 2.0,
            'emergency': 3.0
        }
        
        multiplier = urgency_multipliers.get(content_urgency, 1.0)
        adjusted_budget = base_budget * multiplier
        
        # Cap at max spend per content
        return min(adjusted_budget, self.budget.max_spend_per_content)
        
    def validate_config(self) -> List[str]:
        """Validate configuration and return issues"""
        issues = []
        
        # Validate budget allocations
        total_allocation = sum(
            settings.budget_allocation 
            for settings in self.platform_settings.values()
        )
        
        if abs(total_allocation - 1.0) > 0.01:  # Allow 1% tolerance
            issues.append(f"Budget allocations don't sum to 100%: {total_allocation:.1%}")
            
        # Validate budget amounts
        if self.budget.daily_budget <= 0:
            issues.append("Daily budget must be positive")
            
        if self.budget.campaign_budget < self.budget.daily_budget:
            issues.append("Campaign budget should be at least daily budget")
            
        # Validate engagement targets
        if self.engagement_targets.min_engagement_rate >= self.engagement_targets.target_engagement_rate:
            issues.append("Min engagement rate should be less than target")
            
        # Validate cross-promotion settings
        if self.cross_promotion.min_audience_overlap >= self.cross_promotion.max_audience_overlap:
            issues.append("Min audience overlap should be less than max")
            
        return issues
        
    def optimize_for_performance(self, performance_data: Dict[str, Any]) -> bool:
        """Optimize configuration based on performance data"""
        try:
            if not self.performance_learning:
                return False
                
            # Analyze platform performance
            for platform, metrics in performance_data.items():
                if platform in self.platform_settings:
                    self._optimize_platform_settings(platform, metrics)
                    
            # Optimize budget allocation
            self._optimize_budget_allocation(performance_data)
            
            # Optimize engagement targets
            self._optimize_engagement_targets(performance_data)
            
            logger.info("Configuration optimized based on performance data")
            return True
            
        except Exception as e:
            logger.error(f"Performance optimization error: {e}")
            return False
            
    def _optimize_platform_settings(self, platform -> None: str, metrics -> None: Dict[str, Any]) -> None:
        """Optimize settings for specific platform"""
        settings = self.platform_settings[platform]
        
        # Adjust strategy based on performance
        roi = metrics.get('roi', 0)
        engagement_rate = metrics.get('engagement_rate', 0)
        
        if roi < self.budget.roi_threshold:
            # Poor ROI - switch to more organic strategy
            if settings.strategy == AmplificationStrategy.PAID_BOOST:
                settings.strategy = AmplificationStrategy.ORGANIC_GROWTH
        elif engagement_rate > self.engagement_targets.target_engagement_rate:
            # Good engagement - consider viral strategy
            if settings.strategy == AmplificationStrategy.ORGANIC_GROWTH:
                settings.strategy = AmplificationStrategy.VIRAL_ENGINEERING
                
    def _optimize_budget_allocation(self, performance_data -> None: Dict[str, Any]) -> None:
        """Optimize budget allocation across platforms"""
        
        # Calculate ROI for each platform
        platform_rois = {}
        for platform, metrics in performance_data.items():
            if platform in self.platform_settings:
                platform_rois[platform] = metrics.get('roi', 0)
                
        if not platform_rois:
            return
            
        # Redistribute budget towards higher ROI platforms
        total_roi = sum(platform_rois.values())
        if total_roi > 0:
            for platform, roi in platform_rois.items():
                # Weight allocation by ROI performance
                new_allocation = roi / total_roi
                
                # Smooth transition - don't change too drastically
                current_allocation = self.platform_settings[platform].budget_allocation
                adjusted_allocation = 0.7 * current_allocation + 0.3 * new_allocation
                
                self.platform_settings[platform].budget_allocation = adjusted_allocation
                
    def _optimize_engagement_targets(self, performance_data -> None: Dict[str, Any]) -> None:
        """Optimize engagement targets based on achieved performance"""
        
        all_engagement_rates = []
        for metrics in performance_data.values():
            if 'engagement_rate' in metrics:
                all_engagement_rates.append(metrics['engagement_rate'])
                
        if all_engagement_rates:
            avg_engagement = np.mean(all_engagement_rates)
            
            # Adjust targets based on actual performance
            if avg_engagement > self.engagement_targets.target_engagement_rate:
                # Performing well - raise targets
                self.engagement_targets.target_engagement_rate = min(
                    avg_engagement * 1.1, 0.30  # Cap at 30%
                )
            elif avg_engagement < self.engagement_targets.min_engagement_rate:
                # Underperforming - lower minimum
                self.engagement_targets.min_engagement_rate = max(
                    avg_engagement * 0.9, 0.01  # Floor at 1%
                )
                
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'tier': self.tier.value,
            'budget': self.budget.to_dict(),
            'engagement_targets': self.engagement_targets.to_dict(),
            'cross_promotion': self.cross_promotion.to_dict(),
            'viral_optimization': self.viral_optimization.to_dict(),
            'platform_settings': {
                platform: settings.to_dict()
                for platform, settings in self.platform_settings.items()
            },
            'ai_optimization_enabled': self.ai_optimization_enabled,
            'real_time_adjustment': self.real_time_adjustment,
            'performance_learning': self.performance_learning,
            'auto_scaling': self.auto_scaling,
            'risk_management': self.risk_management,
            'performance_monitoring': self.performance_monitoring,
            'alert_thresholds': self.alert_thresholds
        }


# Create global configuration instance
amplification_config = AmplificationConfig()


# Export main classes and instance
__all__ = [
    'AmplificationConfig',
    'AmplificationBudget',
    'EngagementTargets', 
    'CrossPromotionSettings',
    'ViralOptimizationSettings',
    'PlatformAmplificationSettings',
    'AmplificationStrategy',
    'AmplificationTier',
    'TargetingMode',
    'amplification_config'
]