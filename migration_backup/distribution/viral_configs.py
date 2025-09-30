"""
Viral Configuration Module
=========================

Enterprise-grade configuration management for viral optimization features.
Centralized settings for viral prediction, timing, and amplification strategies.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import json
import os

logger = logging.getLogger(__name__)

class ViralStrategy(Enum):
    """Viral optimization strategies"""
    AGGRESSIVE = "aggressive"      # Maximum viral push
    BALANCED = "balanced"          # Balanced growth
    CONSERVATIVE = "conservative"  # Steady, sustainable growth
    ORGANIC = "organic"           # Minimal intervention
    EXPERIMENTAL = "experimental" # A/B testing strategies

class ContentViralityLevel(Enum):
    """Content virality classification levels"""
    ULTRA_VIRAL = "ultra_viral"    # 1M+ interactions in 24h
    HIGHLY_VIRAL = "highly_viral"  # 100K+ interactions in 24h
    VIRAL = "viral"                # 10K+ interactions in 24h
    TRENDING = "trending"          # 1K+ interactions in 24h
    NORMAL = "normal"              # <1K interactions in 24h

@dataclass
class ViralTriggerConfig:
    """Configuration for viral trigger conditions"""
    min_engagement_rate: float = 5.0        # Minimum engagement rate %
    min_share_velocity: int = 10             # Shares per minute
    min_comment_velocity: int = 20           # Comments per minute
    min_like_velocity: int = 100             # Likes per minute
    sentiment_threshold: float = 0.7         # Positive sentiment threshold
    trending_hashtag_boost: float = 1.5      # Boost for trending hashtags
    influencer_interaction_boost: float = 2.0 # Boost for influencer interactions
    time_window_minutes: int = 60            # Time window for velocity calculations

@dataclass
class ViralAmplificationConfig:
    """Configuration for viral content amplification"""
    auto_amplify_enabled: bool = True
    amplification_budget_usd: float = 1000.0
    max_amplification_hours: int = 24
    target_platforms: List[str] = field(default_factory=lambda: [
        "instagram", "tiktok", "twitter", "youtube", "facebook"
    ])
    amplification_multiplier: float = 2.0    # How much to boost distribution
    cross_platform_sync: bool = True
    hashtag_optimization: bool = True
    timing_optimization: bool = True

@dataclass
class ViralPredictionConfig:
    """Configuration for viral prediction models"""
    model_update_frequency: str = "hourly"  # hourly, daily, weekly
    prediction_confidence_threshold: float = 0.8
    feature_weights: Dict[str, float] = field(default_factory=lambda: {
        "engagement_rate": 0.25,
        "share_velocity": 0.20,
        "sentiment_score": 0.15,
        "trending_alignment": 0.15,
        "influencer_factor": 0.10,
        "optimal_timing": 0.10,
        "content_quality": 0.05
    })
    viral_threshold_scores: Dict[ContentViralityLevel, float] = field(default_factory=lambda: {
        ContentViralityLevel.ULTRA_VIRAL: 0.95,
        ContentViralityLevel.HIGHLY_VIRAL: 0.85,
        ContentViralityLevel.VIRAL: 0.75,
        ContentViralityLevel.TRENDING: 0.60,
        ContentViralityLevel.NORMAL: 0.0
    })

@dataclass
class PlatformViralConfig:
    """Platform-specific viral configuration"""
    platform_name: str
    viral_threshold_multiplier: float = 1.0
    optimal_posting_hours: List[int] = field(default_factory=lambda: [12, 17, 19, 21])
    hashtag_limits: Dict[str, int] = field(default_factory=lambda: {
        "max_hashtags": 30,
        "trending_hashtags": 5,
        "branded_hashtags": 3
    })
    content_type_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "video": 1.5,
        "image": 1.2,
        "carousel": 1.3,
        "text": 1.0,
        "live": 2.0,
        "story": 1.1
    })
    engagement_weights: Dict[str, float] = field(default_factory=lambda: {
        "likes": 1.0,
        "comments": 3.0,
        "shares": 5.0,
        "saves": 2.0,
        "clicks": 1.5
    })

@dataclass
class ViralAnalyticsConfig:
    """Configuration for viral analytics tracking"""
    tracking_enabled: bool = True
    real_time_monitoring: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "viral_probability": 0.8,
        "negative_sentiment": -0.5,
        "rapid_growth": 10.0,  # 10x normal engagement
        "audience_fatigue": 0.3
    })
    metrics_retention_days: int = 90
    detailed_logging: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["json", "csv", "pdf"])

class ViralConfigManager:
    """Manager for viral optimization configurations"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "viral_config.json"
        self.strategy = ViralStrategy.BALANCED
        self.trigger_config = ViralTriggerConfig()
        self.amplification_config = ViralAmplificationConfig()
        self.prediction_config = ViralPredictionConfig()
        self.analytics_config = ViralAnalyticsConfig()
        self.platform_configs: Dict[str, PlatformViralConfig] = {}
        
        # Initialize default platform configs
        self._initialize_default_platforms()
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            self.load_config()
    
    def _initialize_default_platforms(self):
        """Initialize default platform configurations"""
        # Instagram configuration
        self.platform_configs["instagram"] = PlatformViralConfig(
            platform_name="instagram",
            viral_threshold_multiplier=1.2,
            optimal_posting_hours=[11, 13, 17, 19],
            hashtag_limits={
                "max_hashtags": 30,
                "trending_hashtags": 5,
                "branded_hashtags": 3
            },
            content_type_multipliers={
                "video": 1.4,
                "image": 1.0,
                "carousel": 1.3,
                "story": 1.1,
                "reels": 1.8
            }
        )
        
        # TikTok configuration
        self.platform_configs["tiktok"] = PlatformViralConfig(
            platform_name="tiktok",
            viral_threshold_multiplier=1.5,
            optimal_posting_hours=[14, 18, 20, 22],
            hashtag_limits={
                "max_hashtags": 5,
                "trending_hashtags": 3,
                "branded_hashtags": 1
            },
            content_type_multipliers={
                "video": 2.0,
                "live": 1.8
            }
        )
        
        # Twitter configuration
        self.platform_configs["twitter"] = PlatformViralConfig(
            platform_name="twitter",
            viral_threshold_multiplier=1.0,
            optimal_posting_hours=[9, 12, 15, 18],
            hashtag_limits={
                "max_hashtags": 10,
                "trending_hashtags": 3,
                "branded_hashtags": 2
            },
            content_type_multipliers={
                "text": 1.0,
                "image": 1.2,
                "video": 1.5,
                "thread": 1.3
            }
        )
        
        # YouTube configuration
        self.platform_configs["youtube"] = PlatformViralConfig(
            platform_name="youtube",
            viral_threshold_multiplier=1.3,
            optimal_posting_hours=[14, 16, 18, 20],
            hashtag_limits={
                "max_hashtags": 15,
                "trending_hashtags": 5,
                "branded_hashtags": 3
            },
            content_type_multipliers={
                "video": 2.0,
                "shorts": 1.8,
                "live": 1.5
            }
        )
    
    def get_viral_strategy(self) -> ViralStrategy:
        """Get current viral strategy"""
        return self.strategy
    
    def set_viral_strategy(self, strategy: ViralStrategy):
        """Set viral optimization strategy"""
        self.strategy = strategy
        self._update_configs_for_strategy()
        logger.info(f"Viral strategy updated to: {strategy.value}")
    
    def _update_configs_for_strategy(self):
        """Update configurations based on selected strategy"""
        if self.strategy == ViralStrategy.AGGRESSIVE:
            # Aggressive settings
            self.trigger_config.min_engagement_rate = 3.0
            self.trigger_config.min_share_velocity = 5
            self.amplification_config.amplification_multiplier = 3.0
            self.amplification_config.amplification_budget_usd = 2000.0
            
        elif self.strategy == ViralStrategy.BALANCED:
            # Balanced settings (default)
            self.trigger_config.min_engagement_rate = 5.0
            self.trigger_config.min_share_velocity = 10
            self.amplification_config.amplification_multiplier = 2.0
            self.amplification_config.amplification_budget_usd = 1000.0
            
        elif self.strategy == ViralStrategy.CONSERVATIVE:
            # Conservative settings
            self.trigger_config.min_engagement_rate = 8.0
            self.trigger_config.min_share_velocity = 15
            self.amplification_config.amplification_multiplier = 1.5
            self.amplification_config.amplification_budget_usd = 500.0
            
        elif self.strategy == ViralStrategy.ORGANIC:
            # Organic settings
            self.trigger_config.min_engagement_rate = 10.0
            self.amplification_config.auto_amplify_enabled = False
            self.amplification_config.amplification_budget_usd = 0.0
    
    def get_platform_config(self, platform: str) -> Optional[PlatformViralConfig]:
        """Get configuration for specific platform"""
        return self.platform_configs.get(platform.lower())
    
    def update_platform_config(self, platform: str, config: PlatformViralConfig):
        """Update configuration for specific platform"""
        self.platform_configs[platform.lower()] = config
        logger.info(f"Updated viral config for platform: {platform}")
    
    def get_viral_threshold(self, platform: str, content_type: str) -> float:
        """Get viral threshold for platform and content type"""
        platform_config = self.get_platform_config(platform)
        if not platform_config:
            return 0.75  # Default threshold
        
        base_threshold = self.prediction_config.viral_threshold_scores[ContentViralityLevel.VIRAL]
        platform_multiplier = platform_config.viral_threshold_multiplier
        content_multiplier = platform_config.content_type_multipliers.get(content_type, 1.0)
        
        return base_threshold * platform_multiplier * content_multiplier
    
    def should_amplify_content(
        self, 
        engagement_rate: float,
        share_velocity: int,
        sentiment_score: float,
        platform: str
    ) -> bool:
        """Determine if content should be amplified"""
        if not self.amplification_config.auto_amplify_enabled:
            return False
        
        # Check trigger conditions
        if engagement_rate < self.trigger_config.min_engagement_rate:
            return False
        
        if share_velocity < self.trigger_config.min_share_velocity:
            return False
        
        if sentiment_score < self.trigger_config.sentiment_threshold:
            return False
        
        # Check platform-specific conditions
        platform_config = self.get_platform_config(platform)
        if platform_config and platform not in self.amplification_config.target_platforms:
            return False
        
        return True
    
    def get_optimal_posting_times(self, platform: str) -> List[int]:
        """Get optimal posting times for platform"""
        platform_config = self.get_platform_config(platform)
        if platform_config:
            return platform_config.optimal_posting_hours
        
        return [12, 17, 19, 21]  # Default times
    
    def get_hashtag_recommendations(
        self, 
        platform: str, 
        trending_hashtags: List[str],
        content_keywords: List[str]
    ) -> Dict[str, List[str]]:
        """Get hashtag recommendations for platform"""
        platform_config = self.get_platform_config(platform)
        if not platform_config:
            return {"recommended": [], "trending": [], "branded": []}
        
        limits = platform_config.hashtag_limits
        
        # Select trending hashtags
        selected_trending = trending_hashtags[:limits.get("trending_hashtags", 3)]
        
        # Generate content-based hashtags
        content_hashtags = [f"#{keyword.lower()}" for keyword in content_keywords[:5]]
        
        # Add branded hashtags (example)
        branded_hashtags = ["#ainflue", "#contentcreator"][:limits.get("branded_hashtags", 2)]
        
        return {
            "recommended": content_hashtags,
            "trending": selected_trending,
            "branded": branded_hashtags
        }
    
    def calculate_viral_score(
        self,
        engagement_rate: float,
        share_velocity: int,
        sentiment_score: float,
        trending_alignment: float,
        influencer_factor: float,
        timing_score: float,
        content_quality: float
    ) -> float:
        """Calculate viral potential score"""
        weights = self.prediction_config.feature_weights
        
        score = (
            (engagement_rate / 100) * weights["engagement_rate"] +
            min(share_velocity / 100, 1.0) * weights["share_velocity"] +
            ((sentiment_score + 1) / 2) * weights["sentiment_score"] +
            trending_alignment * weights["trending_alignment"] +
            influencer_factor * weights["influencer_factor"] +
            timing_score * weights["optimal_timing"] +
            content_quality * weights["content_quality"]
        )
        
        return min(score, 1.0)
    
    def get_virality_level(self, viral_score: float) -> ContentViralityLevel:
        """Get virality level based on score"""
        thresholds = self.prediction_config.viral_threshold_scores
        
        for level, threshold in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            if viral_score >= threshold:
                return level
        
        return ContentViralityLevel.NORMAL
    
    def should_send_alert(self, metric: str, value: float) -> bool:
        """Check if alert should be sent for metric value"""
        if not self.analytics_config.tracking_enabled:
            return False
        
        threshold = self.analytics_config.alert_thresholds.get(metric)
        if threshold is None:
            return False
        
        if metric in ["viral_probability", "rapid_growth", "audience_fatigue"]:
            return value >= threshold
        elif metric == "negative_sentiment":
            return value <= threshold
        
        return False
    
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration"""
        return {
            "strategy": self.strategy.value,
            "trigger_config": {
                "min_engagement_rate": self.trigger_config.min_engagement_rate,
                "min_share_velocity": self.trigger_config.min_share_velocity,
                "min_comment_velocity": self.trigger_config.min_comment_velocity,
                "min_like_velocity": self.trigger_config.min_like_velocity,
                "sentiment_threshold": self.trigger_config.sentiment_threshold,
                "trending_hashtag_boost": self.trigger_config.trending_hashtag_boost,
                "influencer_interaction_boost": self.trigger_config.influencer_interaction_boost,
                "time_window_minutes": self.trigger_config.time_window_minutes
            },
            "amplification_config": {
                "auto_amplify_enabled": self.amplification_config.auto_amplify_enabled,
                "amplification_budget_usd": self.amplification_config.amplification_budget_usd,
                "max_amplification_hours": self.amplification_config.max_amplification_hours,
                "target_platforms": self.amplification_config.target_platforms,
                "amplification_multiplier": self.amplification_config.amplification_multiplier,
                "cross_platform_sync": self.amplification_config.cross_platform_sync,
                "hashtag_optimization": self.amplification_config.hashtag_optimization,
                "timing_optimization": self.amplification_config.timing_optimization
            },
            "prediction_config": {
                "model_update_frequency": self.prediction_config.model_update_frequency,
                "prediction_confidence_threshold": self.prediction_config.prediction_confidence_threshold,
                "feature_weights": self.prediction_config.feature_weights,
                "viral_threshold_scores": {
                    level.value: score for level, score in self.prediction_config.viral_threshold_scores.items()
                }
            },
            "analytics_config": {
                "tracking_enabled": self.analytics_config.tracking_enabled,
                "real_time_monitoring": self.analytics_config.real_time_monitoring,
                "alert_thresholds": self.analytics_config.alert_thresholds,
                "metrics_retention_days": self.analytics_config.metrics_retention_days,
                "detailed_logging": self.analytics_config.detailed_logging,
                "export_formats": self.analytics_config.export_formats
            },
            "platform_configs": {
                platform: {
                    "platform_name": config.platform_name,
                    "viral_threshold_multiplier": config.viral_threshold_multiplier,
                    "optimal_posting_hours": config.optimal_posting_hours,
                    "hashtag_limits": config.hashtag_limits,
                    "content_type_multipliers": config.content_type_multipliers,
                    "engagement_weights": config.engagement_weights
                }
                for platform, config in self.platform_configs.items()
            }
        }
    
    def save_config(self, filename: Optional[str] = None):
        """Save configuration to file"""
        try:
            filename = filename or self.config_file
            config_data = self.export_config()
            
            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Viral configuration saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save viral configuration: {e}")
            raise
    
    def load_config(self, filename: Optional[str] = None):
        """Load configuration from file"""
        try:
            filename = filename or self.config_file
            
            with open(filename, 'r') as f:
                config_data = json.load(f)
            
            # Load strategy
            self.strategy = ViralStrategy(config_data.get("strategy", "balanced"))
            
            # Load trigger config
            trigger_data = config_data.get("trigger_config", {})
            self.trigger_config = ViralTriggerConfig(**trigger_data)
            
            # Load amplification config
            amp_data = config_data.get("amplification_config", {})
            self.amplification_config = ViralAmplificationConfig(**amp_data)
            
            # Load prediction config
            pred_data = config_data.get("prediction_config", {})
            if "viral_threshold_scores" in pred_data:
                # Convert string keys back to enum
                threshold_scores = {
                    ContentViralityLevel(level): score
                    for level, score in pred_data["viral_threshold_scores"].items()
                }
                pred_data["viral_threshold_scores"] = threshold_scores
            
            self.prediction_config = ViralPredictionConfig(**pred_data)
            
            # Load analytics config
            analytics_data = config_data.get("analytics_config", {})
            self.analytics_config = ViralAnalyticsConfig(**analytics_data)
            
            # Load platform configs
            platform_data = config_data.get("platform_configs", {})
            for platform, config in platform_data.items():
                self.platform_configs[platform] = PlatformViralConfig(**config)
            
            logger.info(f"Viral configuration loaded from {filename}")
            
        except Exception as e:
            logger.error(f"Failed to load viral configuration: {e}")
            # Continue with default configuration
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration"""
        issues = []
        warnings = []
        
        # Validate trigger config
        if self.trigger_config.min_engagement_rate < 0:
            issues.append("min_engagement_rate cannot be negative")
        
        if self.trigger_config.min_share_velocity < 0:
            issues.append("min_share_velocity cannot be negative")
        
        # Validate amplification config
        if self.amplification_config.amplification_budget_usd < 0:
            issues.append("amplification_budget_usd cannot be negative")
        
        if self.amplification_config.amplification_multiplier < 1.0:
            warnings.append("amplification_multiplier less than 1.0 may reduce reach")
        
        # Validate prediction config
        feature_weight_sum = sum(self.prediction_config.feature_weights.values())
        if abs(feature_weight_sum - 1.0) > 0.01:
            warnings.append(f"Feature weights sum to {feature_weight_sum:.3f}, should be 1.0")
        
        # Validate platform configs
        for platform, config in self.platform_configs.items():
            if not config.optimal_posting_hours:
                warnings.append(f"No optimal posting hours defined for {platform}")
            
            if any(hour < 0 or hour > 23 for hour in config.optimal_posting_hours):
                issues.append(f"Invalid posting hours for {platform}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }


# Global configuration instance
_viral_config_manager: Optional[ViralConfigManager] = None

def get_viral_config_manager() -> ViralConfigManager:
    """Get global viral configuration manager"""
    global _viral_config_manager
    if _viral_config_manager is None:
        _viral_config_manager = ViralConfigManager()
    return _viral_config_manager

# Export main components
__all__ = [
    "ViralConfigManager",
    "ViralStrategy",
    "ContentViralityLevel",
    "ViralTriggerConfig",
    "ViralAmplificationConfig",
    "ViralPredictionConfig",
    "PlatformViralConfig",
    "ViralAnalyticsConfig",
    "get_viral_config_manager"
]