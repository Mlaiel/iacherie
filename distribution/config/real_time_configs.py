"""
Real-Time Configuration
======================

Advanced real-time optimization configuration for Ainflue Distribution Platform.
Provides settings for live performance monitoring, adaptive optimization, and emergency response.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class OptimizationMode(Enum):
    """Real-time optimization modes"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class TriggerType(Enum):
    """Trigger types for real-time actions"""
    THRESHOLD = "threshold"
    TREND = "trend"
    ANOMALY = "anomaly"
    SCHEDULE = "schedule"
    MANUAL = "manual"

@dataclass
class PerformanceThresholds:
    """Performance monitoring thresholds"""
    engagement_rate_min: float = 0.01
    engagement_rate_target: float = 0.05
    reach_decline_threshold: float = 0.20  # 20% decline triggers alert
    response_time_max_ms: int = 5000
    error_rate_max: float = 0.05  # 5% error rate
    cpu_usage_max: float = 0.80  # 80% CPU usage
    memory_usage_max: float = 0.85  # 85% memory usage
    queue_size_max: int = 10000
    api_rate_limit_buffer: float = 0.10  # 10% buffer before rate limit

@dataclass
class OptimizationTrigger:
    """Real-time optimization trigger"""
    trigger_id: str
    name: str
    type: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    priority: int = 2
    cooldown_minutes: int = 15
    is_active: bool = True
    max_executions_per_hour: int = 10

@dataclass
class AdaptiveSettings:
    """Adaptive optimization settings"""
    enable_auto_posting_time: bool = True
    enable_auto_hashtag_optimization: bool = True
    enable_auto_content_adjustment: bool = True
    enable_auto_platform_selection: bool = True
    enable_auto_audience_targeting: bool = True
    
    learning_rate: float = 0.1
    adaptation_window_hours: int = 24
    min_data_points: int = 10
    confidence_threshold: float = 0.75
    
    max_adjustments_per_hour: int = 5
    max_adjustments_per_day: int = 50

@dataclass
class EmergencyResponse:
    """Emergency response configuration"""
    enable_emergency_mode: bool = True
    auto_escalation: bool = True
    
    # Response actions
    pause_distribution_on_error_rate: float = 0.15  # 15% error rate
    pause_distribution_on_negative_sentiment: float = 0.30  # 30% negative sentiment
    
    emergency_contacts: List[str] = field(default_factory=list)
    escalation_delay_minutes: int = 30
    
    backup_strategies: Dict[str, Any] = field(default_factory=dict)
    failover_platforms: List[str] = field(default_factory=list)

@dataclass
class MonitoringConfig:
    """Real-time monitoring configuration"""
    monitoring_interval_seconds: int = 30
    data_retention_hours: int = 168  # 7 days
    
    # Metrics to track
    track_engagement_metrics: bool = True
    track_performance_metrics: bool = True
    track_error_metrics: bool = True
    track_system_metrics: bool = True
    track_business_metrics: bool = True
    
    # Alerting
    enable_email_alerts: bool = True
    enable_sms_alerts: bool = True
    enable_slack_alerts: bool = True
    enable_webhook_alerts: bool = True
    
    alert_frequency_limit: int = 5  # Max 5 alerts per hour for same issue

@dataclass
class ABTestingConfig:
    """Real-time A/B testing configuration"""
    enable_real_time_ab_testing: bool = True
    auto_create_tests: bool = True
    auto_stop_losing_variants: bool = True
    
    min_sample_size: int = 100
    confidence_level: float = 0.95
    statistical_significance_threshold: float = 0.05
    
    max_concurrent_tests: int = 10
    test_duration_hours_min: int = 24
    test_duration_hours_max: int = 168  # 7 days
    
    traffic_allocation_step: float = 0.1  # 10% increments

@dataclass
class CacheConfig:
    """Real-time caching configuration"""
    enable_redis_cache: bool = True
    enable_memory_cache: bool = True
    
    # TTL settings
    metrics_cache_ttl_seconds: int = 60
    config_cache_ttl_seconds: int = 300
    api_response_cache_ttl_seconds: int = 120
    
    # Cache sizes
    max_memory_cache_size_mb: int = 512
    max_redis_cache_size_mb: int = 2048
    
    # Cache invalidation
    auto_invalidate_on_update: bool = True
    cache_warming_enabled: bool = True

@dataclass
class RealTimeConfig:
    """Main real-time configuration"""
    # Core Settings
    enable_real_time_optimization: bool = True
    optimization_mode: str = "balanced"
    response_time_target_ms: int = 1000
    
    # Monitoring
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    thresholds: PerformanceThresholds = field(default_factory=PerformanceThresholds)
    
    # Optimization
    adaptive: AdaptiveSettings = field(default_factory=AdaptiveSettings)
    triggers: List[OptimizationTrigger] = field(default_factory=list)
    
    # Emergency Response
    emergency: EmergencyResponse = field(default_factory=EmergencyResponse)
    
    # A/B Testing
    ab_testing: ABTestingConfig = field(default_factory=ABTestingConfig)
    
    # Caching
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    # Platform-specific settings
    platform_settings: Dict[str, Dict] = field(default_factory=dict)
    
    # Feature flags
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default configurations"""
        if not self.triggers:
            self.triggers = self._get_default_triggers()
        
        if not self.platform_settings:
            self.platform_settings = self._get_default_platform_settings()
        
        if not self.feature_flags:
            self.feature_flags = self._get_default_feature_flags()
        
        if not self.emergency.backup_strategies:
            self.emergency.backup_strategies = self._get_default_backup_strategies()
    
    def _get_default_triggers(self) -> List[OptimizationTrigger]:
        """Get default optimization triggers"""
        triggers = []
        
        # Low engagement trigger
        triggers.append(OptimizationTrigger(
            trigger_id="low_engagement",
            name="Low Engagement Rate Trigger",
            type="threshold",
            condition={
                "metric": "engagement_rate",
                "operator": "less_than",
                "value": 0.02,
                "window_minutes": 30
            },
            action={
                "type": "adjust_posting_time",
                "parameters": {"shift_hours": 2, "test_new_time": True}
            },
            priority=3,
            cooldown_minutes=60
        ))
        
        # High error rate trigger
        triggers.append(OptimizationTrigger(
            trigger_id="high_error_rate",
            name="High Error Rate Trigger",
            type="threshold",
            condition={
                "metric": "error_rate",
                "operator": "greater_than",
                "value": 0.10,
                "window_minutes": 10
            },
            action={
                "type": "pause_platform",
                "parameters": {"duration_minutes": 30, "notify_team": True}
            },
            priority=4,
            cooldown_minutes=15
        ))
        
        # Trending content opportunity
        triggers.append(OptimizationTrigger(
            trigger_id="trending_opportunity",
            name="Trending Content Opportunity",
            type="trend",
            condition={
                "metric": "trending_score",
                "operator": "greater_than",
                "value": 0.8,
                "trend_direction": "increasing"
            },
            action={
                "type": "boost_content",
                "parameters": {"increase_frequency": 1.5, "add_trending_hashtags": True}
            },
            priority=2,
            cooldown_minutes=30
        ))
        
        # Performance anomaly detection
        triggers.append(OptimizationTrigger(
            trigger_id="performance_anomaly",
            name="Performance Anomaly Detection",
            type="anomaly",
            condition={
                "metric": "overall_performance",
                "anomaly_threshold": 2.0,  # 2 standard deviations
                "window_minutes": 60
            },
            action={
                "type": "investigate_and_alert",
                "parameters": {"create_alert": True, "priority": "high"}
            },
            priority=3,
            cooldown_minutes=30
        ))
        
        return triggers
    
    def _get_default_platform_settings(self) -> Dict[str, Dict]:
        """Get default platform-specific real-time settings"""
        return {
            "instagram": {
                "enable_story_optimization": True,
                "enable_hashtag_optimization": True,
                "max_posts_per_hour": 2,
                "response_time_target_ms": 2000,
                "engagement_check_interval_minutes": 15
            },
            "twitter": {
                "enable_trending_hashtags": True,
                "enable_reply_optimization": True,
                "max_tweets_per_hour": 10,
                "response_time_target_ms": 1000,
                "engagement_check_interval_minutes": 5
            },
            "facebook": {
                "enable_boost_optimization": True,
                "enable_audience_optimization": True,
                "max_posts_per_hour": 1,
                "response_time_target_ms": 3000,
                "engagement_check_interval_minutes": 30
            },
            "linkedin": {
                "enable_professional_optimization": True,
                "enable_timing_optimization": True,
                "max_posts_per_hour": 1,
                "response_time_target_ms": 2000,
                "engagement_check_interval_minutes": 30
            },
            "tiktok": {
                "enable_trend_optimization": True,
                "enable_music_optimization": True,
                "max_posts_per_hour": 3,
                "response_time_target_ms": 1500,
                "engagement_check_interval_minutes": 10
            },
            "youtube": {
                "enable_thumbnail_optimization": True,
                "enable_title_optimization": True,
                "max_uploads_per_hour": 1,
                "response_time_target_ms": 5000,
                "engagement_check_interval_minutes": 60
            }
        }
    
    def _get_default_feature_flags(self) -> Dict[str, bool]:
        """Get default feature flags"""
        return {
            "enable_ai_content_optimization": True,
            "enable_predictive_analytics": True,
            "enable_sentiment_analysis": True,
            "enable_competitor_monitoring": True,
            "enable_trend_detection": True,
            "enable_auto_scaling": True,
            "enable_load_balancing": True,
            "enable_circuit_breaker": True,
            "enable_rate_limiting": True,
            "enable_metrics_collection": True
        }
    
    def _get_default_backup_strategies(self) -> Dict[str, Any]:
        """Get default backup strategies"""
        return {
            "api_failure": {
                "action": "retry_with_backoff",
                "max_retries": 3,
                "backoff_seconds": [1, 5, 15],
                "fallback_platform": "manual_queue"
            },
            "rate_limit_exceeded": {
                "action": "switch_to_backup_account",
                "delay_minutes": 15,
                "redistribute_content": True
            },
            "platform_outage": {
                "action": "redirect_to_alternative_platforms",
                "maintain_schedule": True,
                "notify_users": True
            },
            "performance_degradation": {
                "action": "reduce_complexity",
                "disable_non_essential_features": True,
                "scale_resources": True
            }
        }
    
    def add_trigger(self, trigger: OptimizationTrigger) -> bool:
        """
        Add optimization trigger
        
        Args:
            trigger: Trigger to add
            
        Returns:
            bool: Success status
        """
        try:
            if not trigger.trigger_id or not trigger.name:
                logger.error("Trigger ID and name are required")
                return False
            
            # Check if trigger already exists
            existing_ids = [t.trigger_id for t in self.triggers]
            if trigger.trigger_id in existing_ids:
                logger.error(f"Trigger ID already exists: {trigger.trigger_id}")
                return False
            
            self.triggers.append(trigger)
            logger.info(f"Added optimization trigger: {trigger.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding trigger: {str(e)}")
            return False
    
    def remove_trigger(self, trigger_id: str) -> bool:
        """
        Remove optimization trigger
        
        Args:
            trigger_id: ID of trigger to remove
            
        Returns:
            bool: Success status
        """
        try:
            original_count = len(self.triggers)
            self.triggers = [t for t in self.triggers if t.trigger_id != trigger_id]
            
            if len(self.triggers) < original_count:
                logger.info(f"Removed optimization trigger: {trigger_id}")
                return True
            else:
                logger.warning(f"Trigger not found: {trigger_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing trigger: {str(e)}")
            return False
    
    def get_trigger(self, trigger_id: str) -> Optional[OptimizationTrigger]:
        """
        Get optimization trigger by ID
        
        Args:
            trigger_id: Trigger ID
            
        Returns:
            Optional[OptimizationTrigger]: Trigger if found
        """
        for trigger in self.triggers:
            if trigger.trigger_id == trigger_id:
                return trigger
        return None
    
    def get_active_triggers(self) -> List[OptimizationTrigger]:
        """
        Get all active optimization triggers
        
        Returns:
            List[OptimizationTrigger]: Active triggers
        """
        return [trigger for trigger in self.triggers if trigger.is_active]
    
    def update_feature_flag(self, flag_name: str, enabled: bool) -> bool:
        """
        Update feature flag
        
        Args:
            flag_name: Name of feature flag
            enabled: Whether feature is enabled
            
        Returns:
            bool: Success status
        """
        try:
            self.feature_flags[flag_name] = enabled
            logger.info(f"Updated feature flag {flag_name}: {enabled}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating feature flag: {str(e)}")
            return False
    
    def is_feature_enabled(self, flag_name: str) -> bool:
        """
        Check if feature is enabled
        
        Args:
            flag_name: Name of feature flag
            
        Returns:
            bool: Whether feature is enabled
        """
        return self.feature_flags.get(flag_name, False)
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """
        Get platform-specific configuration
        
        Args:
            platform: Platform name
            
        Returns:
            Dict[str, Any]: Platform configuration
        """
        return self.platform_settings.get(platform, {})
    
    def update_platform_config(self, platform: str, config: Dict[str, Any]) -> bool:
        """
        Update platform-specific configuration
        
        Args:
            platform: Platform name
            config: Configuration updates
            
        Returns:
            bool: Success status
        """
        try:
            if platform not in self.platform_settings:
                self.platform_settings[platform] = {}
            
            self.platform_settings[platform].update(config)
            logger.info(f"Updated platform config for: {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating platform config: {str(e)}")
            return False
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration settings
        
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate core settings
        if self.response_time_target_ms < 100:
            errors.append("Response time target must be at least 100ms")
        
        # Validate thresholds
        if not 0 <= self.thresholds.engagement_rate_min <= 1:
            errors.append("Engagement rate minimum must be between 0 and 1")
        
        if not 0 <= self.thresholds.engagement_rate_target <= 1:
            errors.append("Engagement rate target must be between 0 and 1")
        
        if self.thresholds.engagement_rate_target < self.thresholds.engagement_rate_min:
            errors.append("Engagement rate target must be greater than minimum")
        
        if not 0 <= self.thresholds.reach_decline_threshold <= 1:
            errors.append("Reach decline threshold must be between 0 and 1")
        
        if self.thresholds.response_time_max_ms < 1000:
            errors.append("Maximum response time must be at least 1000ms")
        
        # Validate adaptive settings
        if not 0 < self.adaptive.learning_rate <= 1:
            errors.append("Learning rate must be between 0 and 1")
        
        if self.adaptive.adaptation_window_hours < 1:
            errors.append("Adaptation window must be at least 1 hour")
        
        if self.adaptive.min_data_points < 5:
            errors.append("Minimum data points must be at least 5")
        
        # Validate triggers
        for trigger in self.triggers:
            if not trigger.name:
                errors.append(f"Trigger {trigger.trigger_id} must have a name")
            
            if not trigger.condition:
                errors.append(f"Trigger {trigger.trigger_id} must have a condition")
            
            if not trigger.action:
                errors.append(f"Trigger {trigger.trigger_id} must have an action")
            
            if trigger.cooldown_minutes < 1:
                errors.append(f"Trigger {trigger.trigger_id} cooldown must be at least 1 minute")
        
        # Validate monitoring settings
        if self.monitoring.monitoring_interval_seconds < 10:
            errors.append("Monitoring interval must be at least 10 seconds")
        
        if self.monitoring.data_retention_hours < 24:
            errors.append("Data retention must be at least 24 hours")
        
        # Validate A/B testing settings
        if self.ab_testing.min_sample_size < 10:
            errors.append("A/B testing minimum sample size must be at least 10")
        
        if not 0 < self.ab_testing.confidence_level < 1:
            errors.append("A/B testing confidence level must be between 0 and 1")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealTimeConfig':
        """
        Create configuration from dictionary
        
        Args:
            data: Configuration data
            
        Returns:
            RealTimeConfig: Configuration instance
        """
        # Convert nested dictionaries back to dataclass instances
        if 'monitoring' in data:
            data['monitoring'] = MonitoringConfig(**data['monitoring'])
        
        if 'thresholds' in data:
            data['thresholds'] = PerformanceThresholds(**data['thresholds'])
        
        if 'adaptive' in data:
            data['adaptive'] = AdaptiveSettings(**data['adaptive'])
        
        if 'emergency' in data:
            data['emergency'] = EmergencyResponse(**data['emergency'])
        
        if 'ab_testing' in data:
            data['ab_testing'] = ABTestingConfig(**data['ab_testing'])
        
        if 'cache' in data:
            data['cache'] = CacheConfig(**data['cache'])
        
        if 'triggers' in data:
            triggers = []
            for trigger_data in data['triggers']:
                triggers.append(OptimizationTrigger(**trigger_data))
            data['triggers'] = triggers
        
        return cls(**data)
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            file_path: Path to save file
            
        Returns:
            bool: Success status
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Saved real-time configuration to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['RealTimeConfig']:
        """
        Load configuration from JSON file
        
        Args:
            file_path: Path to load file
            
        Returns:
            Optional[RealTimeConfig]: Configuration instance if successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = cls.from_dict(data)
            logger.info(f"Loaded real-time configuration from: {file_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return None

# Global configuration instance
real_time_config = RealTimeConfig()

def get_real_time_config() -> RealTimeConfig:
    """Get global real-time configuration"""
    return real_time_config

def load_real_time_config(config_file: str = None) -> RealTimeConfig:
    """
    Load real-time configuration from file or environment
    
    Args:
        config_file: Optional config file path
        
    Returns:
        RealTimeConfig: Loaded configuration
    """
    global real_time_config
    
    # Try to load from specified file
    if config_file and os.path.exists(config_file):
        loaded_config = RealTimeConfig.load_from_file(config_file)
        if loaded_config:
            real_time_config = loaded_config
            return real_time_config
    
    # Try to load from environment-specified file
    env_config_file = os.getenv('AINFLUE_REALTIME_CONFIG')
    if env_config_file and os.path.exists(env_config_file):
        loaded_config = RealTimeConfig.load_from_file(env_config_file)
        if loaded_config:
            real_time_config = loaded_config
            return real_time_config
    
    # Return default configuration
    logger.info("Using default real-time configuration")
    return real_time_config

# Example usage
if __name__ == "__main__":
    # Create custom configuration
    config = RealTimeConfig()
    
    # Update optimization mode
    config.optimization_mode = "aggressive"
    
    # Add custom trigger
    custom_trigger = OptimizationTrigger(
        trigger_id="custom_viral_opportunity",
        name="Viral Content Opportunity",
        type="trend",
        condition={
            "metric": "viral_score",
            "operator": "greater_than",
            "value": 0.9,
            "window_minutes": 15
        },
        action={
            "type": "amplify_content",
            "parameters": {"boost_budget": 100, "extend_reach": True}
        },
        priority=4,
        cooldown_minutes=60
    )
    
    config.add_trigger(custom_trigger)
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        print(f"Configuration errors: {errors}")
    else:
        print("Configuration is valid")
    
    # Save to file
    config.save_to_file("real_time_config.json")
    
    print(f"Configuration created with {len(config.triggers)} triggers")