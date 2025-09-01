"""Support Agent Configuration Settings

Enterprise configuration management for Support Agent with environment-based settings,
security configurations, and performance tuning parameters.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class Environment(Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class AIModelConfig:
    """Configuration for AI models"""
    conversation_model: str = "microsoft/DialoGPT-medium"
    intent_model: str = "facebook/bart-large-mnli"
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Model parameters
    max_response_length: int = 150
    temperature: float = 0.7
    do_sample: bool = True
    top_k: int = 50
    top_p: float = 0.95
    
    # Performance settings
    model_cache_dir: str = "./model_cache"
    use_gpu: bool = True
    gpu_memory_limit: float = 0.8  # 80% of GPU memory

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = field(default_factory=lambda: os.getenv("SUPPORT_DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("SUPPORT_DB_PORT", "5432")))
    database: str = field(default_factory=lambda: os.getenv("SUPPORT_DB_NAME", "ia_influencer_support"))
    username: str = field(default_factory=lambda: os.getenv("SUPPORT_DB_USER", "support_user"))
    password: str = field(default_factory=lambda: os.getenv("SUPPORT_DB_PASSWORD", ""))
    
    # Connection pool settings
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # SSL settings
    use_ssl: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None

@dataclass
class RedisConfig:
    """Redis configuration for caching"""
    url: str = field(default_factory=lambda: os.getenv("SUPPORT_REDIS_URL", "redis://localhost:6379/2"))
    max_connections: int = 100
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    
    # Cache TTL settings (in seconds)
    knowledge_base_ttl: int = 3600  # 1 hour
    conversation_ttl: int = 1800    # 30 minutes
    analytics_ttl: int = 300        # 5 minutes

@dataclass
class SecurityConfig:
    """Security and encryption configuration"""
    encryption_key: str = field(default_factory=lambda: os.getenv("SUPPORT_ENCRYPTION_KEY", ""))
    jwt_secret: str = field(default_factory=lambda: os.getenv("SUPPORT_JWT_SECRET", ""))
    
    # Rate limiting
    requests_per_minute: int = 100
    conversations_per_user_per_hour: int = 10
    
    # Session settings
    session_timeout: int = 3600  # 1 hour
    max_concurrent_sessions_per_user: int = 3
    
    # Data retention (in days)
    ticket_retention_days: int = 365
    conversation_retention_days: int = 90
    analytics_retention_days: int = 730

@dataclass
class KnowledgeBaseConfig:
    """Knowledge base configuration"""
    max_articles: int = 10000
    similarity_threshold: float = 0.7
    max_search_results: int = 5
    reindex_interval_hours: int = 24
    
    # Semantic search settings
    embedding_dimension: int = 384
    index_type: str = "flat"  # flat, hnsw, ivf
    
    # Content settings
    max_article_length: int = 5000
    supported_formats: List[str] = field(default_factory=lambda: ["markdown", "html", "text"])

@dataclass
class EscalationConfig:
    """Escalation rules and settings"""
    sentiment_threshold: float = -0.7
    max_conversation_turns: int = 10
    escalation_timeout_minutes: int = 30
    
    keywords_requiring_human: List[str] = field(default_factory=lambda: [
        "speak to human", "human agent", "escalate", "manager", 
        "supervisor", "complaint", "legal", "lawsuit"
    ])
    
    categories_auto_escalate: List[str] = field(default_factory=lambda: [
        "SECURITY_PRIVACY", "BILLING_PAYMENT", "LEGAL"
    ])
    
    priority_auto_escalate: List[str] = field(default_factory=lambda: [
        "URGENT", "CRITICAL"
    ])
    
    # Human agent settings
    max_human_queue_length: int = 50
    average_human_response_time: int = 300  # 5 minutes

@dataclass
class PerformanceConfig:
    """Performance and scaling configuration"""
    max_concurrent_conversations: int = field(
        default_factory=lambda: int(os.getenv("SUPPORT_MAX_CONCURRENT_CONVERSATIONS", "1000"))
    )
    response_timeout: int = 30
    health_check_interval: int = 60
    
    # Load balancing
    load_balancer_strategy: str = "round_robin"  # round_robin, least_connections, weighted
    agent_pool_size: int = 5
    auto_scale_enabled: bool = True
    scale_up_threshold: float = 0.8  # 80% utilization
    scale_down_threshold: float = 0.3  # 30% utilization
    
    # Caching
    response_cache_size: int = 1000
    conversation_cache_size: int = 5000
    
    # Resource limits
    max_memory_mb: int = 2048
    max_cpu_percent: int = 80

@dataclass
class MonitoringConfig:
    """Monitoring and analytics configuration"""
    enable_metrics: bool = True
    metrics_port: int = 8090
    
    # Prometheus settings
    prometheus_enabled: bool = True
    prometheus_namespace: str = "support_agent"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file_max_size: int = 100  # MB
    log_file_backup_count: int = 5
    
    # Analytics
    analytics_batch_size: int = 100
    analytics_flush_interval: int = 60  # seconds
    
    # Health checks
    health_check_endpoints: List[str] = field(default_factory=lambda: [
        "/health", "/metrics", "/ready"
    ])

@dataclass 
class SupportAgentConfig:
    """Master configuration for Support Agent"""
    environment: Environment = Environment.PRODUCTION
    
    # Component configurations
    ai_models: AIModelConfig = field(default_factory=AIModelConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    knowledge_base: KnowledgeBaseConfig = field(default_factory=KnowledgeBaseConfig)
    escalation: EscalationConfig = field(default_factory=EscalationConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Supported features
    supported_languages: List[str] = field(default_factory=lambda: [
        "en", "de", "fr", "es", "it", "pt"
    ])
    
    supported_channels: List[str] = field(default_factory=lambda: [
        "chat", "email", "phone", "video_call", "knowledge_base", "community_forum"
    ])
    
    # Feature flags
    enable_proactive_support: bool = True
    enable_auto_resolution: bool = True
    enable_sentiment_analysis: bool = True
    enable_multilingual_support: bool = True
    enable_voice_support: bool = False  # Future feature
    enable_video_support: bool = False  # Future feature
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment.value,
            "ai_models": {
                "conversation_model": self.ai_models.conversation_model,
                "intent_model": self.ai_models.intent_model,
                "sentiment_model": self.ai_models.sentiment_model,
                "embedding_model": self.ai_models.embedding_model,
                "parameters": {
                    "max_response_length": self.ai_models.max_response_length,
                    "temperature": self.ai_models.temperature,
                    "do_sample": self.ai_models.do_sample
                }
            },
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "pool_size": self.database.pool_size
            },
            "performance": {
                "max_concurrent_conversations": self.performance.max_concurrent_conversations,
                "response_timeout": self.performance.response_timeout,
                "load_balancer_strategy": self.performance.load_balancer_strategy
            },
            "features": {
                "supported_languages": self.supported_languages,
                "supported_channels": self.supported_channels,
                "enable_proactive_support": self.enable_proactive_support,
                "enable_auto_resolution": self.enable_auto_resolution,
                "enable_sentiment_analysis": self.enable_sentiment_analysis
            }
        }
    
    @classmethod
    def from_environment(cls, env: Environment = None) -> 'SupportAgentConfig':
        """Create configuration from environment variables"""
        if env is None:
            env_str = os.getenv("SUPPORT_ENVIRONMENT", "production")
            env = Environment(env_str.lower())
        
        config = cls(environment=env)
        
        # Override with environment-specific settings
        if env == Environment.DEVELOPMENT:
            config.ai_models.use_gpu = False
            config.performance.max_concurrent_conversations = 100
            config.monitoring.log_level = "DEBUG"
            config.database.pool_size = 5
        
        elif env == Environment.TESTING:
            config.ai_models.use_gpu = False
            config.performance.max_concurrent_conversations = 10
            config.monitoring.log_level = "WARNING"
            config.database.database = "ia_influencer_support_test"
        
        elif env == Environment.STAGING:
            config.performance.max_concurrent_conversations = 500
            config.monitoring.log_level = "INFO"
        
        return config
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Database validation
        if not self.database.password:
            errors.append("Database password is required")
        
        # Security validation
        if not self.security.encryption_key:
            errors.append("Encryption key is required")
        
        if not self.security.jwt_secret:
            errors.append("JWT secret is required")
        
        # Performance validation
        if self.performance.max_concurrent_conversations <= 0:
            errors.append("Max concurrent conversations must be positive")
        
        if self.performance.response_timeout <= 0:
            errors.append("Response timeout must be positive")
        
        # AI models validation
        if self.ai_models.temperature < 0 or self.ai_models.temperature > 2:
            errors.append("AI model temperature must be between 0 and 2")
        
        return errors

# Global configuration instance
_config: Optional[SupportAgentConfig] = None

def get_config() -> SupportAgentConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = SupportAgentConfig.from_environment()
    return _config

def set_config(config: SupportAgentConfig):
    """Set global configuration instance"""
    global _config
    _config = config

def load_config_from_file(config_path: str) -> SupportAgentConfig:
    """Load configuration from JSON or YAML file"""
    import json
    
    with open(config_path, 'r') as f:
        if config_path.endswith('.json'):
            config_data = json.load(f)
        elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
            import yaml
            config_data = yaml.safe_load(f)
        else:
            raise ValueError("Configuration file must be JSON or YAML")
    
    # Convert dict to config object (simplified)
    config = SupportAgentConfig()
    
    if 'environment' in config_data:
        config.environment = Environment(config_data['environment'])
    
    # Override specific settings
    if 'ai_models' in config_data:
        ai_config = config_data['ai_models']
        if 'conversation_model' in ai_config:
            config.ai_models.conversation_model = ai_config['conversation_model']
        if 'temperature' in ai_config:
            config.ai_models.temperature = ai_config['temperature']
    
    return config
