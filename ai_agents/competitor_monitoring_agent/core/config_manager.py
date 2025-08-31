"""
Configuration Manager - Advanced Configuration Management System
Manages configuration settings for the competitor monitoring agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel. All rights reserved.
WARNING: Unauthorized use, copying, or distribution is strictly prohibited.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from core.exceptions import ConfigurationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ConfigurationError = globals().get('ConfigurationError', Exception)
from ...security.encryption import SecureDataHandler


@dataclass
class MonitoringConfig:
    """Monitoring configuration settings."""
    update_interval: int = 300  # seconds
    max_concurrent_collections: int = 10
    collection_timeout: int = 30
    retry_attempts: int = 3
    enable_real_time: bool = True
    enable_background_monitoring: bool = True
    data_retention_days: int = 90


@dataclass
class AlertConfig:
    """Alert system configuration."""
    enable_alerts: bool = True
    max_alerts_per_hour: int = 100
    alert_channels: list = None
    notification_delay: int = 0
    escalation_enabled: bool = True
    auto_resolve_time: int = 86400  # 24 hours


@dataclass
class DataSourceConfig:
    """Data source configuration."""
    enable_website_scraping: bool = True
    enable_social_media: bool = True
    enable_news_monitoring: bool = True
    enable_financial_data: bool = True
    api_rate_limits: Dict[str, int] = None
    proxy_settings: Dict[str, str] = None


@dataclass
class AnalysisConfig:
    """Analysis engine configuration."""
    enable_sentiment_analysis: bool = True
    enable_trend_analysis: bool = True
    enable_swot_analysis: bool = True
    confidence_threshold: float = 0.7
    trend_threshold: float = 0.15
    analysis_batch_size: int = 50


class ConfigurationManager:
    """
    Advanced configuration management for competitor monitoring agent.
    
    Provides centralized configuration management with environment variable
    support, validation, and secure credential handling.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager."""
        self.logger = logging.getLogger(__name__)
        self.secure_handler = SecureDataHandler()
        
        # Configuration file paths
        self.config_path = config_path or os.getenv("COMPETITOR_CONFIG_PATH", "config/competitor_monitoring.json")
        self.credentials_path = os.getenv("COMPETITOR_CREDENTIALS_PATH", "config/credentials.encrypted")
        
        # Default configurations
        self.monitoring_config = MonitoringConfig()
        self.alert_config = AlertConfig(alert_channels=["email"])
        self.data_source_config = DataSourceConfig(
            api_rate_limits={"default": 100, "twitter": 300, "linkedin": 50},
            proxy_settings={}
        )
        self.analysis_config = AnalysisConfig()
        
        # Load configurations
        self._load_configurations()
        
        self.logger.info("ConfigurationManager initialized")
    
    def _load_configurations(self):
        """Load configurations from file and environment variables."""



        try:
            # Load from file if exists
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    self._apply_config_data(config_data)
            
            # Override with environment variables
            self._load_from_environment()
            
            # Validate configurations
            self._validate_configurations()
            
            self.logger.info("Configurations loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading configurations: {str(e)}")
            raise ConfigurationError(f"Failed to load configurations: {str(e)}")
    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data from loaded config."""



        try:
            # Monitoring config
            if "monitoring" in config_data:
                monitoring_data = config_data["monitoring"]
                self.monitoring_config = MonitoringConfig(
                    update_interval=monitoring_data.get("update_interval", self.monitoring_config.update_interval),
                    max_concurrent_collections=monitoring_data.get("max_concurrent_collections", self.monitoring_config.max_concurrent_collections),
                    collection_timeout=monitoring_data.get("collection_timeout", self.monitoring_config.collection_timeout),
                    retry_attempts=monitoring_data.get("retry_attempts", self.monitoring_config.retry_attempts),
                    enable_real_time=monitoring_data.get("enable_real_time", self.monitoring_config.enable_real_time),
                    enable_background_monitoring=monitoring_data.get("enable_background_monitoring", self.monitoring_config.enable_background_monitoring),
                    data_retention_days=monitoring_data.get("data_retention_days", self.monitoring_config.data_retention_days)
                )
            
            # Alert config
            if "alerts" in config_data:
                alert_data = config_data["alerts"]
                self.alert_config = AlertConfig(
                    enable_alerts=alert_data.get("enable_alerts", self.alert_config.enable_alerts),
                    max_alerts_per_hour=alert_data.get("max_alerts_per_hour", self.alert_config.max_alerts_per_hour),
                    alert_channels=alert_data.get("alert_channels", self.alert_config.alert_channels),
                    notification_delay=alert_data.get("notification_delay", self.alert_config.notification_delay),
                    escalation_enabled=alert_data.get("escalation_enabled", self.alert_config.escalation_enabled),
                    auto_resolve_time=alert_data.get("auto_resolve_time", self.alert_config.auto_resolve_time)
                )
            
            # Data source config
            if "data_sources" in config_data:
                ds_data = config_data["data_sources"]
                self.data_source_config = DataSourceConfig(
                    enable_website_scraping=ds_data.get("enable_website_scraping", self.data_source_config.enable_website_scraping),
                    enable_social_media=ds_data.get("enable_social_media", self.data_source_config.enable_social_media),
                    enable_news_monitoring=ds_data.get("enable_news_monitoring", self.data_source_config.enable_news_monitoring),
                    enable_financial_data=ds_data.get("enable_financial_data", self.data_source_config.enable_financial_data),
                    api_rate_limits=ds_data.get("api_rate_limits", self.data_source_config.api_rate_limits),
                    proxy_settings=ds_data.get("proxy_settings", self.data_source_config.proxy_settings)
                )
            
            # Analysis config
            if "analysis" in config_data:
                analysis_data = config_data["analysis"]
                self.analysis_config = AnalysisConfig(
                    enable_sentiment_analysis=analysis_data.get("enable_sentiment_analysis", self.analysis_config.enable_sentiment_analysis),
                    enable_trend_analysis=analysis_data.get("enable_trend_analysis", self.analysis_config.enable_trend_analysis),
                    enable_swot_analysis=analysis_data.get("enable_swot_analysis", self.analysis_config.enable_swot_analysis),
                    confidence_threshold=analysis_data.get("confidence_threshold", self.analysis_config.confidence_threshold),
                    trend_threshold=analysis_data.get("trend_threshold", self.analysis_config.trend_threshold),
                    analysis_batch_size=analysis_data.get("analysis_batch_size", self.analysis_config.analysis_batch_size)
                )
                
        except Exception as e:
            self.logger.error(f"Error applying config data: {str(e)}")
            raise ConfigurationError(f"Invalid configuration data: {str(e)}")
    
    def _load_from_environment(self):
        """Load configuration values from environment variables."""



        try:
            # Monitoring environment variables
            if os.getenv("COMPETITOR_UPDATE_INTERVAL"):
                self.monitoring_config.update_interval = int(os.getenv("COMPETITOR_UPDATE_INTERVAL"))
            
            if os.getenv("COMPETITOR_MAX_CONCURRENT"):
                self.monitoring_config.max_concurrent_collections = int(os.getenv("COMPETITOR_MAX_CONCURRENT"))
            
            if os.getenv("COMPETITOR_COLLECTION_TIMEOUT"):
                self.monitoring_config.collection_timeout = int(os.getenv("COMPETITOR_COLLECTION_TIMEOUT"))
            
            # Alert environment variables
            if os.getenv("COMPETITOR_ENABLE_ALERTS"):
                self.alert_config.enable_alerts = os.getenv("COMPETITOR_ENABLE_ALERTS").lower() == "true"
            
            if os.getenv("COMPETITOR_MAX_ALERTS_PER_HOUR"):
                self.alert_config.max_alerts_per_hour = int(os.getenv("COMPETITOR_MAX_ALERTS_PER_HOUR"))
            
            if os.getenv("COMPETITOR_ALERT_CHANNELS"):
                self.alert_config.alert_channels = os.getenv("COMPETITOR_ALERT_CHANNELS").split(",")
            
            # Data source environment variables
            if os.getenv("COMPETITOR_ENABLE_WEBSITE_SCRAPING"):
                self.data_source_config.enable_website_scraping = os.getenv("COMPETITOR_ENABLE_WEBSITE_SCRAPING").lower() == "true"
            
            if os.getenv("COMPETITOR_ENABLE_SOCIAL_MEDIA"):
                self.data_source_config.enable_social_media = os.getenv("COMPETITOR_ENABLE_SOCIAL_MEDIA").lower() == "true"
            
            # Analysis environment variables
            if os.getenv("COMPETITOR_CONFIDENCE_THRESHOLD"):
                self.analysis_config.confidence_threshold = float(os.getenv("COMPETITOR_CONFIDENCE_THRESHOLD"))
            
            if os.getenv("COMPETITOR_TREND_THRESHOLD"):
                self.analysis_config.trend_threshold = float(os.getenv("COMPETITOR_TREND_THRESHOLD"))
                
        except Exception as e:
            self.logger.error(f"Error loading environment variables: {str(e)}")
            raise ConfigurationError(f"Invalid environment variable: {str(e)}")
    
    def _validate_configurations(self):
        """Validate configuration values."""



        try:
            # Validate monitoring config
            if self.monitoring_config.update_interval < 60:
                raise ConfigurationError("Update interval must be at least 60 seconds")
            
            if self.monitoring_config.max_concurrent_collections < 1:
                raise ConfigurationError("Max concurrent collections must be at least 1")
            
            if self.monitoring_config.collection_timeout < 5:
                raise ConfigurationError("Collection timeout must be at least 5 seconds")
            
            # Validate alert config
            if self.alert_config.max_alerts_per_hour < 1:
                raise ConfigurationError("Max alerts per hour must be at least 1")
            
            # Validate analysis config
            if not (0.0 <= self.analysis_config.confidence_threshold <= 1.0):
                raise ConfigurationError("Confidence threshold must be between 0.0 and 1.0")
            
            if not (0.0 <= self.analysis_config.trend_threshold <= 1.0):
                raise ConfigurationError("Trend threshold must be between 0.0 and 1.0")
            
            if self.analysis_config.analysis_batch_size < 1:
                raise ConfigurationError("Analysis batch size must be at least 1")
                
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            raise ConfigurationError(f"Configuration validation failed: {str(e)}")
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary."""



        return {
            "monitoring": asdict(self.monitoring_config),
            "alerts": asdict(self.alert_config),
            "data_sources": asdict(self.data_source_config),
            "analysis": asdict(self.analysis_config)
        }
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""



        return self.monitoring_config
    
    def get_alert_config(self) -> AlertConfig:
        """Get alert configuration."""



        return self.alert_config
    
    def get_data_source_config(self) -> DataSourceConfig:
        """Get data source configuration."""



        return self.data_source_config
    
    def get_analysis_config(self) -> AnalysisConfig:
        """Get analysis configuration."""



        return self.analysis_config
    
    def update_config(self, config_type: str, updates: Dict[str, Any]):
        """Update specific configuration section."""



        try:
            if config_type == "monitoring":
                for key, value in updates.items():
                    if hasattr(self.monitoring_config, key):
                        setattr(self.monitoring_config, key, value)
                        
            elif config_type == "alerts":
                for key, value in updates.items():
                    if hasattr(self.alert_config, key):
                        setattr(self.alert_config, key, value)
                        
            elif config_type == "data_sources":
                for key, value in updates.items():
                    if hasattr(self.data_source_config, key):
                        setattr(self.data_source_config, key, value)
                        
            elif config_type == "analysis":
                for key, value in updates.items():
                    if hasattr(self.analysis_config, key):
                        setattr(self.analysis_config, key, value)
            else:
                raise ConfigurationError(f"Unknown configuration type: {config_type}")
            
            # Validate updated configuration
            self._validate_configurations()
            
            # Save to file if needed
            self.save_config()
            
            self.logger.info(f"Configuration updated: {config_type}")
            
        except Exception as e:
            self.logger.error(f"Error updating configuration: {str(e)}")
            raise ConfigurationError(f"Failed to update configuration: {str(e)}")
    
    def save_config(self):
        """Save current configuration to file."""



        try:
            # Ensure config directory exists
            config_dir = os.path.dirname(self.config_path)
            if config_dir:
                Path(config_dir).mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            config_data = self.get_full_config()
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")
    
    def load_credentials(self) -> Dict[str, Any]:
        """Load encrypted credentials."""



        try:
            if os.path.exists(self.credentials_path):
                return self.secure_handler.decrypt_file(self.credentials_path)
            return {}
            
        except Exception as e:
            self.logger.error(f"Error loading credentials: {str(e)}")
            return {}
    
    def save_credentials(self, credentials: Dict[str, Any]):
        """Save encrypted credentials."""



        try:
            # Ensure credentials directory exists
            creds_dir = os.path.dirname(self.credentials_path)
            if creds_dir:
                Path(creds_dir).mkdir(parents=True, exist_ok=True)
            
            self.secure_handler.encrypt_data(credentials, self.credentials_path)
            self.logger.info("Credentials saved securely")
            
        except Exception as e:
            self.logger.error(f"Error saving credentials: {str(e)}")
            raise ConfigurationError(f"Failed to save credentials: {str(e)}")
    
    def get_api_credentials(self, service: str) -> Dict[str, str]:
        """Get API credentials for a specific service."""



        try:
            credentials = self.load_credentials()
            return credentials.get(service, {})
            
        except Exception as e:
            self.logger.error(f"Error getting API credentials for {service}: {str(e)}")
            return {}
    
    def validate_api_credentials(self, service: str) -> bool:
        """Validate API credentials for a service."""



        try:
            credentials = self.get_api_credentials(service)
            
            # Basic validation - check if required fields exist
            required_fields = {
                "twitter": ["api_key", "api_secret", "access_token", "access_token_secret"],
                "linkedin": ["client_id", "client_secret"],
                "facebook": ["app_id", "app_secret", "access_token"],
                "instagram": ["access_token"],
                "youtube": ["api_key"],
                "news_api": ["api_key"],
                "crunchbase": ["api_key"]
            }
            
            if service in required_fields:
                for field in required_fields[service]:
                    if field not in credentials or not credentials[field]:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating credentials for {service}: {str(e)}")
            return False
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get configuration status and health."""



        return {
            "config_loaded": True,
            "config_file_exists": os.path.exists(self.config_path),
            "credentials_file_exists": os.path.exists(self.credentials_path),
            "monitoring_enabled": self.monitoring_config.enable_real_time,
            "alerts_enabled": self.alert_config.enable_alerts,
            "data_sources_configured": {
                "website_scraping": self.data_source_config.enable_website_scraping,
                "social_media": self.data_source_config.enable_social_media,
                "news_monitoring": self.data_source_config.enable_news_monitoring,
                "financial_data": self.data_source_config.enable_financial_data
            },
            "analysis_features": {
                "sentiment_analysis": self.analysis_config.enable_sentiment_analysis,
                "trend_analysis": self.analysis_config.enable_trend_analysis,
                "swot_analysis": self.analysis_config.enable_swot_analysis
            },
            "last_updated": datetime.utcnow().isoformat() if 'datetime' in globals() else None
        }
