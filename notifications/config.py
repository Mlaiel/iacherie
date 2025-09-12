"""
Notifications Configuration Module
Standalone configuration for the Ainflue notifications system
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class NotificationConfig:
    """Notification system configuration"""
    
    # Database settings
    database_url: str = "postgresql://localhost/ainflue_notifications"
    redis_url: str = "redis://localhost:6379/0"
    
    # Security settings
    encryption_key: str = "your-32-char-encryption-key-here"
    jwt_secret: str = "your-jwt-secret-key"
    
    # Email settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    
    # SMS settings
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    
    # Push notification settings
    fcm_server_key: str = ""
    apns_key_id: str = ""
    
    # Rate limiting
    rate_limit_per_minute: int = 1000
    max_concurrent_requests: int = 100
    
    # AI settings
    openai_api_key: str = ""
    ai_personalization_enabled: bool = True
    
    # Monitoring
    metrics_enabled: bool = True
    log_level: str = "INFO"

# Global configuration instance
settings = NotificationConfig()

# Update from environment variables
def load_from_env():
    """Load configuration from environment variables"""
    settings.database_url = os.getenv("NOTIFICATIONS_DATABASE_URL", settings.database_url)
    settings.redis_url = os.getenv("NOTIFICATIONS_REDIS_URL", settings.redis_url)
    settings.encryption_key = os.getenv("NOTIFICATIONS_ENCRYPTION_KEY", settings.encryption_key)
    settings.smtp_username = os.getenv("SMTP_USERNAME", settings.smtp_username)
    settings.smtp_password = os.getenv("SMTP_PASSWORD", settings.smtp_password)
    settings.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", settings.twilio_account_sid)
    settings.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", settings.twilio_auth_token)
    settings.openai_api_key = os.getenv("OPENAI_API_KEY", settings.openai_api_key)
    
    # Boolean settings
    settings.ai_personalization_enabled = os.getenv("AI_PERSONALIZATION_ENABLED", "true").lower() == "true"
    settings.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    
    # Numeric settings
    try:
        settings.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", str(settings.rate_limit_per_minute)))
        settings.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", str(settings.max_concurrent_requests)))
    except ValueError:
        pass  # Use defaults

# Simple metrics collector
class MetricsCollector:
    """Simple metrics collector for notifications"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger(__name__)
    
    async def increment(self, metric_name: str, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        key = f"{metric_name}:{':'.join(f'{k}={v}' for k, v in (tags or {}).items())}"
        self.metrics[key] = self.metrics.get(key, 0) + 1
        self.logger.debug(f"Metric incremented: {key} = {self.metrics[key]}")
    
    async def histogram(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram metric"""
        key = f"{metric_name}_histogram:{':'.join(f'{k}={v}' for k, v in (tags or {}).items())}"
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(value)
        self.logger.debug(f"Histogram recorded: {key} = {value}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return self.metrics.copy()

# Simple encryption functions
def encrypt_sensitive_data(data: str, key: Optional[str] = None) -> str:
    """Simple encryption for sensitive data (placeholder implementation)"""
    # In production, use proper encryption like Fernet
    return f"encrypted:{data}"

def decrypt_sensitive_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Simple decryption for sensitive data (placeholder implementation)"""
    if encrypted_data.startswith("encrypted:"):
        return encrypted_data[10:]  # Remove "encrypted:" prefix
    return encrypted_data

# Load configuration on import
load_from_env()

# Global instances
metrics = MetricsCollector()