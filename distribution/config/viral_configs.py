"""
Viral Optimization Configuration Module
=====================================

Enterprise-grade configuration for viral prediction and optimization engines.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2024 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from enum import Enum
import os

class ViralityModel(Enum):
    """Viral prediction model types"""
    LIGHTWEIGHT = "lightweight"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

class ContentType(Enum):
    """Supported content types for viral analysis"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    REEL = "reel"
    STORY = "story"
    LIVE = "live"

@dataclass
class ViralPredictionConfig:
    """Configuration for viral prediction engine"""
    
    # Model configuration
    model_type: ViralityModel = ViralityModel.ADVANCED
    model_version: str = "3.2.1"
    confidence_threshold: float = 0.75
    prediction_timeout: int = 30  # seconds
    
    # Feature weights for prediction
    feature_weights: Dict[str, float] = field(default_factory=lambda: {
        "content_quality": 0.25,
        "timing_score": 0.20,
        "trend_alignment": 0.20,
        "audience_match": 0.15,
        "platform_optimization": 0.10,
        "creator_influence": 0.10
    })
    
    # Analysis depth settings
    quick_analysis_features: List[str] = field(default_factory=lambda: [
        "basic_engagement_metrics",
        "content_type_score",
        "posting_time_score"
    ])
    
    detailed_analysis_features: List[str] = field(default_factory=lambda: [
        "content_quality_analysis",
        "audience_sentiment_analysis", 
        "trend_correlation_analysis",
        "competitive_analysis",
        "platform_algorithm_alignment"
    ])
    
    comprehensive_analysis_features: List[str] = field(default_factory=lambda: [
        "deep_content_analysis",
        "psychographic_matching",
        "network_effect_analysis",
        "cultural_resonance_analysis",
        "viral_cascade_prediction",
        "cross_platform_synergy"
    ])

@dataclass
class TrendAnalysisConfig:
    """Configuration for trend analysis engine"""
    
    # Trend detection parameters
    trend_detection_window: int = 24  # hours
    trend_significance_threshold: float = 0.8
    trending_hashtag_limit: int = 50
    
    # Data sources for trend analysis
    trend_data_sources: List[str] = field(default_factory=lambda: [
        "google_trends",
        "social_media_apis",
        "news_apis",
        "platform_trending",
        "internal_analytics"
    ])
    
    # Regional trend analysis
    supported_regions: List[str] = field(default_factory=lambda: [
        "US", "UK", "CA", "AU", "DE", "FR", "ES", "IT", "JP", "KR", "BR", "MX"
    ])
    
    # Trend categories
    trend_categories: List[str] = field(default_factory=lambda: [
        "entertainment", "music", "technology", "lifestyle", "fitness",
        "food", "travel", "fashion", "sports", "gaming", "education"
    ])

@dataclass
class TimingOptimizationConfig:
    """Configuration for optimal timing prediction"""
    
    # Timing analysis parameters
    timezone_optimization: bool = True
    platform_specific_timing: bool = True
    audience_behavior_learning: bool = True
    
    # Default optimal posting times (UTC)
    default_optimal_times: Dict[str, List[str]] = field(default_factory=lambda: {
        "instagram": ["18:00", "19:00", "20:00"],
        "tiktok": ["18:30", "19:30", "20:30"], 
        "youtube": ["14:00", "15:00", "20:00"],
        "facebook": ["13:00", "15:00", "19:00"],
        "twitter": ["12:00", "17:00", "19:00"],
        "linkedin": ["08:00", "12:00", "17:00"]
    })
    
    # Peak engagement windows
    peak_engagement_windows: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "weekday": {"start": 18, "end": 21},
        "weekend": {"start": 12, "end": 15}
    })

@dataclass
class ViralAmplificationConfig:
    """Configuration for viral amplification strategies"""
    
    # Amplification thresholds
    viral_threshold_score: float = 0.85
    trending_threshold_score: float = 0.70
    boost_trigger_score: float = 0.60
    
    # Amplification strategies
    amplification_strategies: Dict[str, Dict] = field(default_factory=lambda: {
        "organic": {
            "cross_platform_posting": True,
            "hashtag_optimization": True,
            "community_engagement": True,
            "influencer_outreach": True
        },
        "paid": {
            "auto_boost_enabled": True,
            "max_boost_budget": 500.0,
            "boost_duration_hours": 24,
            "target_audience_expansion": 1.5
        },
        "collaborative": {
            "creator_network_activation": True,
            "cross_promotion_enabled": True,
            "viral_challenge_creation": True
        }
    })
    
    # Performance tracking
    performance_tracking: Dict[str, Union[bool, int]] = field(default_factory=lambda: {
        "real_time_monitoring": True,
        "monitoring_interval_seconds": 300,
        "alert_threshold_changes": 0.20,
        "automated_optimization": True
    })

@dataclass
class NetworkDynamicsConfig:
    """Configuration for network dynamics analysis"""
    
    # Network analysis parameters
    influence_propagation_depth: int = 3
    network_analysis_timeout: int = 60  # seconds
    influencer_identification_threshold: float = 0.80
    
    # Network mapping
    network_mapping_enabled: bool = True
    cross_platform_network_analysis: bool = True
    
    # Cascade prediction
    cascade_prediction_models: List[str] = field(default_factory=lambda: [
        "linear_threshold",
        "independent_cascade", 
        "voter_model",
        "complex_contagion"
    ])

@dataclass
class ViralOptimizationConfig:
    """Main viral optimization configuration"""
    
    # Sub-configurations
    prediction: ViralPredictionConfig = field(default_factory=ViralPredictionConfig)
    trend_analysis: TrendAnalysisConfig = field(default_factory=TrendAnalysisConfig)
    timing: TimingOptimizationConfig = field(default_factory=TimingOptimizationConfig)
    amplification: ViralAmplificationConfig = field(default_factory=ViralAmplificationConfig)
    network_dynamics: NetworkDynamicsConfig = field(default_factory=NetworkDynamicsConfig)
    
    # Global settings
    enable_ai_optimization: bool = True
    enable_real_time_updates: bool = True
    enable_cross_platform_sync: bool = True
    
    # Performance settings
    max_concurrent_predictions: int = 100
    cache_prediction_results: bool = True
    cache_ttl_seconds: int = 3600
    
    # Logging and monitoring
    log_level: str = "INFO"
    enable_performance_metrics: bool = True
    enable_detailed_analytics: bool = True
    
    @classmethod
    def from_env(cls) -> 'ViralOptimizationConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Override with environment variables if available
        if os.getenv('VIRAL_MODEL_TYPE'):
            config.prediction.model_type = ViralityModel(os.getenv('VIRAL_MODEL_TYPE'))
        
        if os.getenv('VIRAL_CONFIDENCE_THRESHOLD'):
            config.prediction.confidence_threshold = float(os.getenv('VIRAL_CONFIDENCE_THRESHOLD'))
        
        if os.getenv('VIRAL_CACHE_TTL'):
            config.cache_ttl_seconds = int(os.getenv('VIRAL_CACHE_TTL'))
        
        return config
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            "prediction": self.prediction.__dict__,
            "trend_analysis": self.trend_analysis.__dict__,
            "timing": self.timing.__dict__,
            "amplification": self.amplification.__dict__,
            "network_dynamics": self.network_dynamics.__dict__,
            "global_settings": {
                "enable_ai_optimization": self.enable_ai_optimization,
                "enable_real_time_updates": self.enable_real_time_updates,
                "enable_cross_platform_sync": self.enable_cross_platform_sync,
                "max_concurrent_predictions": self.max_concurrent_predictions,
                "cache_prediction_results": self.cache_prediction_results,
                "cache_ttl_seconds": self.cache_ttl_seconds,
                "log_level": self.log_level,
                "enable_performance_metrics": self.enable_performance_metrics,
                "enable_detailed_analytics": self.enable_detailed_analytics
            }
        }

# Default configuration instance
DEFAULT_VIRAL_CONFIG = ViralOptimizationConfig()

# Environment-based configuration
VIRAL_CONFIG = ViralOptimizationConfig.from_env()

__all__ = [
    "ViralityModel",
    "ContentType", 
    "ViralPredictionConfig",
    "TrendAnalysisConfig",
    "TimingOptimizationConfig",
    "ViralAmplificationConfig",
    "NetworkDynamicsConfig",
    "ViralOptimizationConfig",
    "DEFAULT_VIRAL_CONFIG",
    "VIRAL_CONFIG"
]