"""🔍 Web Crawling & Monitoring Configuration Manager - IA-Influencer-Agent
========================================================================
Project Creator & Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
         Microservices Architect + Audio Engineer + DevOps Engineer + IA Prompt Engineer
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Enterprise-grade web crawling and monitoring configuration management system.
========================================================================
"""

from typing import Dict, Any, Optional, List, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os
import logging
from pathlib import Path
import json
import yaml
from decimal import Decimal

# Initialize logger
logger = logging.getLogger(__name__)

class CrawlerType(Enum):
    """
Types of crawlers"""

    WEB_SCRAPER = "web_scraper"
    API_CRAWLER = "api_crawler"
    SOCIAL_MEDIA_CRAWLER = "social_media_crawler"
    SEARCH_ENGINE_CRAWLER = "search_engine_crawler"
    CONTENT_AGGREGATOR = "content_aggregator"
    PIRACY_DETECTOR = "piracy_detector"
    COMPETITOR_MONITOR = "competitor_monitor"
    TREND_ANALYZER = "trend_analyzer"

class CrawlFrequency(Enum):
    """Crawling frequency options"""

    REAL_TIME = "real_time"
    EVERY_MINUTE = "every_minute"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    EVERY_30_MINUTES = "every_30_minutes"
    HOURLY = "hourly"
    EVERY_6_HOURS = "every_6_hours"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"

class DetectionMode(Enum):
    """Content detection modes"""

    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"
    SEMANTIC_MATCH = "semantic_match"
    VISUAL_MATCH = "visual_match"
    AUDIO_MATCH = "audio_match"
    HYBRID_MATCH = "hybrid_match"

class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ActionType(Enum):
    """Automated action types"""

    NOTIFY_ONLY = "notify_only"
    LOG_VIOLATION = "log_violation"
    SEND_DMCA = "send_dmca"
    CONTACT_PLATFORM = "contact_platform"
    LEGAL_ACTION = "legal_action"
    BLOCK_CONTENT = "block_content"
    REPORT_ABUSE = "report_abuse"
    ESCALATE_HUMAN = "escalate_human"

class CrawlerEngine(Enum):
    """Crawler engines"""

    SCRAPY = "scrapy"
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"
    BEAUTIFULSOUP = "beautifulsoup"
    REQUESTS = "requests"
    AIOHTTP = "aiohttp"
    HTTPX = "httpx"
    CUSTOM = "custom"

@dataclass
class PlatformCrawlerConfig:
    """Individual platform crawler configuration"""
    platform_name: str
    enabled: bool = True
    crawler_type: CrawlerType = CrawlerType.WEB_SCRAPER
    engine: CrawlerEngine = CrawlerEngine.SCRAPY
    
    # API configuration
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    
    # Crawling parameters
    start_urls: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)
    crawl_frequency: CrawlFrequency = CrawlFrequency.HOURLY
    max_pages_per_crawl: int = 1000
    max_depth: int = 3
    concurrent_requests: int = 16
    download_delay: float = 1.0
    
    # Content filtering
    content_types_to_monitor: List[str] = field(default_factory=lambda: [
        "audio", "video", "image", "text", "music", "podcast"
    ])
    file_extensions: List[str] = field(default_factory=lambda: [
        ".mp3", ".wav", ".mp4", ".jpg", ".png", ".pdf", ".txt"
    ])
    min_file_size_kb: int = 100
    max_file_size_mb: int = 100
    
    # Detection settings
    detection_modes: List[DetectionMode] = field(default_factory=lambda: [
        DetectionMode.FUZZY_MATCH, DetectionMode.SEMANTIC_MATCH
    ])
    similarity_threshold: float = 0.85
    content_analysis_enabled: bool = True
    metadata_analysis_enabled: bool = True
    
    # Rate limiting and politeness
    respect_robots_txt: bool = True
    user_agent: str = "IA-Influencer-Agent-Crawler/2.0"
    request_timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    
    # Proxy and security
    use_proxies: bool = False
    proxy_list: List[str] = field(default_factory=list)
    rotate_proxies: bool = True
    use_tor: bool = False
    stealth_mode: bool = True
    
    # JavaScript and dynamic content
    javascript_enabled: bool = True
    wait_for_page_load: float = 3.0
    scroll_page: bool = True
    screenshot_enabled: bool = True
    
    # Output and storage
    save_screenshots: bool = True
    save_page_source: bool = True
    save_extracted_data: bool = True
    output_format: str = "json"
    compress_output: bool = True
    
    # Monitoring and alerts
    monitoring_enabled: bool = True
    alert_on_violation: bool = True
    alert_threshold: int = 1
    escalation_enabled: bool = True
    
    # Performance optimization
    cache_enabled: bool = True
    cache_duration_hours: int = 24
    parallel_processing: bool = True
    memory_optimization: bool = True
    bandwidth_optimization: bool = True

@dataclass
class ContentDetectionConfig:
    """Content detection configuration"""
    enabled: bool = True
    
    # Detection algorithms
    fingerprint_matching: bool = True
    hash_comparison: bool = True
    metadata_comparison: bool = True
    semantic_analysis: bool = True
    visual_similarity: bool = True
    audio_similarity: bool = True
    
    # Matching thresholds
    exact_match_threshold: float = 1.0
    fuzzy_match_threshold: float = 0.9
    semantic_match_threshold: float = 0.8
    visual_match_threshold: float = 0.85
    audio_match_threshold: float = 0.9
    
    # Content analysis
    deep_content_analysis: bool = True
    style_analysis: bool = True
    structure_analysis: bool = True
    linguistic_analysis: bool = True
    technical_analysis: bool = True
    
    # Machine learning
    ml_models_enabled: bool = True
    model_ensemble: bool = True
    continuous_learning: bool = True
    model_updating: bool = True
    
    # Performance settings
    batch_processing: bool = True
    batch_size: int = 100
    parallel_analysis: bool = True
    gpu_acceleration: bool = True
    memory_optimization: bool = True
    
    # Quality control
    false_positive_reduction: bool = True
    confidence_scoring: bool = True
    human_verification: bool = True
    feedback_learning: bool = True

@dataclass
class AlertingConfig:
    """
Alerting configuration"""
    enabled: bool = True
    
    # Alert channels
    email_alerts: bool = True
    sms_alerts: bool = True
    webhook_alerts: bool = True
    dashboard_alerts: bool = True
    mobile_push_alerts: bool = True
    
    # Email configuration
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_recipients: List[str] = field(default_factory=list)
    
    # SMS configuration
    sms_provider: Optional[str] = None
    sms_api_key: Optional[str] = None
    sms_recipients: List[str] = field(default_factory=list)
    
    # Webhook configuration
    webhook_urls: List[str] = field(default_factory=list)
    webhook_timeout_seconds: int = 10
    webhook_retry_attempts: int = 3
    
    # Alert rules
    alert_levels: List[AlertLevel] = field(default_factory=lambda: [
        AlertLevel.MEDIUM, AlertLevel.HIGH, AlertLevel.CRITICAL
    ])
    min_confidence_score: float = 0.8
    alert_frequency_limit: int = 10  # per hour
    duplicate_alert_suppression: bool = True
    
    # Escalation
    escalation_enabled: bool = True
    escalation_delay_minutes: int = 30
    escalation_levels: List[str] = field(default_factory=lambda: [
        "team_lead", "legal_team", "management"
    ])
    
    # Alert formatting
    include_screenshots: bool = True
    include_evidence: bool = True
    include_recommendations: bool = True
    alert_template: Optional[str] = None
    
    # Quiet hours
    quiet_hours_enabled: bool = True
    quiet_start_hour: int = 22
    quiet_end_hour: int = 8
    emergency_override: bool = True

@dataclass
class AutomatedActionConfig:
    """Automated action configuration"""
    enabled: bool = True
    
    # Action settings
    auto_dmca_enabled: bool = True
    auto_takedown_enabled: bool = False
    auto_reporting_enabled: bool = True
    auto_escalation_enabled: bool = True
    
    # DMCA configuration
    dmca_template_path: Optional[str] = None
    dmca_sender_info: Dict[str, str] = field(default_factory=dict)
    dmca_legal_contacts: List[str] = field(default_factory=list)
    dmca_tracking_enabled: bool = True
    
    # Takedown requests
    takedown_platforms: List[str] = field(default_factory=list)
    takedown_templates: Dict[str, str] = field(default_factory=dict)
    takedown_tracking: bool = True
    
    # Reporting configuration
    abuse_report_templates: Dict[str, str] = field(default_factory=dict)
    platform_specific_reporting: bool = True
    bulk_reporting: bool = True
    
    # Action thresholds
    confidence_threshold_dmca: float = 0.95
    confidence_threshold_takedown: float = 0.9
    confidence_threshold_report: float = 0.8
    
    # Safety measures
    human_approval_required: bool = True
    test_mode: bool = False
    rate_limiting: bool = True
    max_actions_per_day: int = 50
    
    # Documentation
    action_logging: bool = True
    evidence_preservation: bool = True
    legal_documentation: bool = True
    audit_trail: bool = True

@dataclass
class PerformanceConfig:
    """
Performance and optimization configuration"""
    # Resource limits
    max_memory_gb: int = 8
    max_cpu_cores: int = 4
    max_disk_space_gb: int = 100
    max_network_bandwidth_mbps: int = 100
    
    # Concurrency settings
    max_concurrent_crawlers: int = 10
    max_concurrent_requests: int = 100
    max_concurrent_analysis: int = 20
    queue_size_limit: int = 10000
    
    # Caching
    cache_enabled: bool = True
    cache_size_mb: int = 1024
    cache_ttl_hours: int = 24
    distributed_cache: bool = True
    
    # Database optimization
    db_connection_pool_size: int = 20
    db_query_timeout_seconds: int = 30
    db_batch_size: int = 1000
    db_indexing_enabled: bool = True
    
    # Storage optimization
    compression_enabled: bool = True
    data_deduplication: bool = True
    archiving_enabled: bool = True
    cleanup_schedule: str = "daily"
    
    # Network optimization
    connection_pooling: bool = True
    keepalive_enabled: bool = True
    compression_algorithms: List[str] = field(default_factory=lambda: ["gzip", "deflate"])
    
    # Monitoring
    performance_monitoring: bool = True
    resource_monitoring: bool = True
    bottleneck_detection: bool = True
    auto_scaling: bool = True

@dataclass
class CrawlingMonitoringConfiguration:
    """Master crawling and monitoring configuration"""
    # Platform configurations
    platform_configs: Dict[str, PlatformCrawlerConfig] = field(default_factory=dict)
    
    # Core configurations
    content_detection_config: ContentDetectionConfig = field(default_factory=ContentDetectionConfig)
    alerting_config: AlertingConfig = field(default_factory=AlertingConfig)
    automated_action_config: AutomatedActionConfig = field(default_factory=AutomatedActionConfig)
    performance_config: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Global settings
    global_enabled: bool = True
    master_crawler_frequency: CrawlFrequency = CrawlFrequency.HOURLY
    priority_content_types: List[str] = field(default_factory=lambda: [
        "music", "audio", "video", "podcast"
    ])
    
    # Security settings
    secure_crawling: bool = True
    ethical_crawling: bool = True
    legal_compliance: bool = True
    privacy_protection: bool = True
    
    # Content library
    protected_content_database: Optional[str] = None
    fingerprint_database: Optional[str] = None
    whitelist_urls: List[str] = field(default_factory=list)
    blacklist_urls: List[str] = field(default_factory=list)
    
    # Reporting and analytics
    reporting_enabled: bool = True
    analytics_enabled: bool = True
    dashboard_enabled: bool = True
    api_access_enabled: bool = True
    
    # Data retention
    raw_data_retention_days: int = 30
    processed_data_retention_days: int = 365
    alert_data_retention_days: int = 90
    evidence_retention_years: int = 7
    
    # Integration settings
    third_party_integrations: List[str] = field(default_factory=list)
    webhook_integrations: bool = True
    api_integrations: bool = True
    
    # Quality assurance
    quality_checks_enabled: bool = True
    validation_enabled: bool = True
    testing_mode: bool = False
    
    # Metadata
    version: str = "2.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "Fahed Mlaiel"
    contact_email: str = "mlaiel@live.de"

class CrawlingMonitoringConfigManager:
    """
    Enterprise-grade crawling and monitoring configuration manager.
    
    Manages comprehensive configuration for web crawling, content monitoring,
    piracy detection, automated actions, and alerting systems.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
Initialize crawling monitoring configuration manager"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration path
        self.config_path = config_path or os.getenv(
            "CRAWLING_CONFIG_PATH",
            "/app/config/crawling_monitoring.yaml"
        )
        
        # Initialize default configuration
        self._config = CrawlingMonitoringConfiguration()
        
        # Initialize default platform configurations
        self._initialize_default_platforms()
        
        # Configuration state
        self.initialized = False
        self.last_updated = datetime.now()
        self.validation_errors = []
        
        # Load configuration from file if exists
        self._load_configuration()
        
        self.logger.info("Crawling monitoring configuration manager initialized")
    
    def _initialize_default_platforms(self) -> None:
        """Initialize default platform configurations"""
        default_platforms = {
            "youtube": {
                "platform_name": "YouTube",
                "api_base_url": "https://www.googleapis.com/youtube/v3",
                "start_urls": ["https://www.youtube.com"],
                "allowed_domains": ["youtube.com", "youtu.be"],
                "content_types_to_monitor": ["video", "audio", "music"]
            },
            "soundcloud": {
                "platform_name": "SoundCloud",
                "api_base_url": "https://api.soundcloud.com",
                "start_urls": ["https://soundcloud.com"],
                "allowed_domains": ["soundcloud.com"],
                "content_types_to_monitor": ["audio", "music", "podcast"]
            },
            "instagram": {
                "platform_name": "Instagram",
                "api_base_url": "https://graph.instagram.com",
                "start_urls": ["https://www.instagram.com"],
                "allowed_domains": ["instagram.com"],
                "content_types_to_monitor": ["image", "video", "music"]
            },
            "tiktok": {
                "platform_name": "TikTok",
                "start_urls": ["https://www.tiktok.com"],
                "allowed_domains": ["tiktok.com"],
                "content_types_to_monitor": ["video", "music", "audio"]
            },
            "spotify": {
                "platform_name": "Spotify",
                "api_base_url": "https://api.spotify.com/v1",
                "start_urls": ["https://open.spotify.com"],
                "allowed_domains": ["spotify.com"],
                "content_types_to_monitor": ["music", "audio", "podcast"]
            }
        }
        
        for platform_id, config_data in default_platforms.items():
            config = PlatformCrawlerConfig(**config_data)
            self._config.platform_configs[platform_id] = config
    
    def _load_configuration(self) -> bool:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Update configuration with loaded data
                self._update_config_from_dict(config_data)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                self.logger.info("No configuration file found, using defaults")
                return False
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for key, value in config_data.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self._config.updated_at = datetime.now()
        self.last_updated = datetime.now()
    
    def add_platform(self, platform_id: str, config: PlatformCrawlerConfig) -> bool:
        """
Add platform crawler configuration"""
        try:
            self._config.platform_configs[platform_id] = config
            self._config.updated_at = datetime.now()
            self.last_updated = datetime.now()
            self.logger.info(f"Platform {platform_id} crawler configuration added")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add platform crawler configuration: {e}")
            return False
    
    def get_platform_config(self, platform_id: str) -> Optional[PlatformCrawlerConfig]:
        """Get platform crawler configuration"""
        return self._config.platform_configs.get(platform_id)
    
    def get_enabled_platforms(self) -> List[str]:
        """
Get list of enabled platforms"""
        return [
            platform_id for platform_id, config in self._config.platform_configs.items()
            if config.enabled
        ]
    
    def validate_configuration(self) -> List[str]:
        """
Validate configuration and return list of errors"""
        errors = []
        
        try:
            # Validate platform configurations
            for platform_id, config in self._config.platform_configs.items():
                if config.enabled and not config.start_urls:
                    errors.append(f"Platform {platform_id} has no start URLs")
                
                if config.similarity_threshold < 0 or config.similarity_threshold > 1:
                    errors.append(f"Platform {platform_id} similarity threshold must be between 0 and 1")
            
            # Validate detection configuration
            detection_config = self._config.content_detection_config
            for threshold_attr in ['exact_match_threshold', 'fuzzy_match_threshold', 'semantic_match_threshold']:
                threshold = getattr(detection_config, threshold_attr)
                if threshold < 0 or threshold > 1:
                    errors.append(f"Detection {threshold_attr} must be between 0 and 1")
            
            # Validate performance configuration
            perf_config = self._config.performance_config
            if perf_config.max_concurrent_crawlers <= 0:
                errors.append("Max concurrent crawlers must be positive")
            
            if perf_config.max_memory_gb <= 0:
                errors.append("Max memory must be positive")
            
            self.validation_errors = errors
            
            if not errors:
                self.logger.info("Configuration validation passed")
            else:
                self.logger.warning(f"Configuration validation failed with {len(errors)} errors")
            
            return errors
        
        except Exception as e:
            error_msg = f"Configuration validation error: {e}"
            self.logger.error(error_msg)
            return [error_msg]
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration status and metadata"""
        return {
            "initialized": self.initialized,
            "last_updated": self.last_updated,
            "config_path": self.config_path,
            "validation_errors": self.validation_errors,
            "version": self._config.version,
            "created_by": self._config.created_by,
            "contact_email": self._config.contact_email,
            "enabled_platforms": len(self.get_enabled_platforms()),
            "total_platforms": len(self._config.platform_configs),
            "global_enabled": self._config.global_enabled,
            "features_enabled": {
                "content_detection": self._config.content_detection_config.enabled,
                "alerting": self._config.alerting_config.enabled,
                "automated_actions": self._config.automated_action_config.enabled,
                "reporting": self._config.reporting_enabled,
                "analytics": self._config.analytics_enabled,
                "quality_checks": self._config.quality_checks_enabled
            }
        }

# Global instance
crawling_monitoring_config_manager = CrawlingMonitoringConfigManager()

# Export public API
__all__ = [
    "CrawlingMonitoringConfigManager",
    "CrawlingMonitoringConfiguration",
    "PlatformCrawlerConfig",
    "ContentDetectionConfig",
    "AlertingConfig",
    "AutomatedActionConfig",
    "PerformanceConfig",
    "CrawlerType",
    "CrawlFrequency",
    "DetectionMode",
    "AlertLevel",
    "ActionType",
    "CrawlerEngine",
    "crawling_monitoring_config_manager"
]
