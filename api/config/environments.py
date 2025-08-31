"""Environment Configurations - IA Influencer Agent Platform
Environment-specific configuration classes for different deployment stages

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""
import os
from typing import List, Dict, Any
from datetime import timedelta
from .app_config import AppConfig


class DevelopmentConfig(AppConfig):
    """Development environment configuration"""
    
    def __init__(self):
        super().__init__()
        
        # Environment settings
        self.environment = "development"
        self.debug = True
        self.testing = False
        
        # Security settings (relaxed for development)
        self.cors_origins = [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080"
        ]
        
        # Database settings (local development)
        self.database_url = os.getenv("DEV_DATABASE_URL", 
            "postgresql://postgres:password@localhost:5432/ia_influencer_agent_dev")
        self.database_name = "ia_influencer_agent_dev"
        self.database_max_connections = 20
        self.database_pool_size = 5
        
        # Redis settings (local development)
        self.redis_url = os.getenv("DEV_REDIS_URL", "redis://localhost:6379/0")
        self.redis_db = 0
        
        # MongoDB settings (local development)
        self.mongodb_url = os.getenv("DEV_MONGODB_URL", "mongodb://localhost:27017/ia_influencer_agent_dev")
        self.mongodb_database = "ia_influencer_agent_dev"
        
        # Elasticsearch settings
        self.elasticsearch_url = os.getenv("DEV_ELASTICSEARCH_URL", "http://localhost:9200")
        
        # Logging settings (verbose for development)
        self.log_level = "DEBUG"
        self.log_to_console = True
        self.structured_logging = False  # Simple format for development
        
        # JWT settings (short expiry for development)
        self.jwt_access_token_expire = timedelta(hours=2)
        self.jwt_refresh_token_expire = timedelta(days=7)
        
        # Feature toggles (all enabled for development)
        self.enable_fingerprinting = True
        self.enable_content_protection = True
        self.enable_monetization = True
        self.enable_web_crawling = False  # Disabled to avoid external calls
        self.enable_ai_agent = True
        
        # Rate limiting (relaxed for development)
        self.rate_limit_per_minute = 1000
        self.rate_limit_per_hour = 10000
        self.rate_limit_per_day = 100000
        
        # Storage settings (local for development)
        self.storage_type = "local"
        self.local_storage_path = os.path.join(os.getcwd(), "dev_uploads")
        
        # Blockchain settings (testnet only)
        self.default_network = "ethereum_sepolia"
        self.development_mode = True
        self.use_local_blockchain = True
        
        # Monitoring (minimal for development)
        self.prometheus_host = "localhost"
        self.grafana_host = "localhost"
        
        # Business settings (testing values)
        self.creator_commission_rate = 0.10  # 10% for testing
        self.platform_commission_rate = 0.02  # 2% for testing
        self.minimum_payout_threshold = 10.0  # Low threshold for testing


class TestingConfig(AppConfig):
    """Testing environment configuration"""
    
    def __init__(self):
        super().__init__()
        
        # Environment settings
        self.environment = "testing"
        self.debug = True
        self.testing = True
        
        # Database settings (in-memory for testing)
        self.database_url = os.getenv("TEST_DATABASE_URL", 
            "postgresql://postgres:password@localhost:5432/ia_influencer_agent_test")
        self.database_name = "ia_influencer_agent_test"
        self.database_max_connections = 10
        self.database_pool_size = 2
        
        # Redis settings (separate DB for testing)
        self.redis_url = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")
        self.redis_db = 1
        
        # MongoDB settings (separate database for testing)
        self.mongodb_url = os.getenv("TEST_MONGODB_URL", "mongodb://localhost:27017/ia_influencer_agent_test")
        self.mongodb_database = "ia_influencer_agent_test"
        
        # Elasticsearch settings (test index)
        self.elasticsearch_url = os.getenv("TEST_ELASTICSEARCH_URL", "http://localhost:9200")
        self.elasticsearch_index_prefix = "ia_influencer_test"
        
        # Logging settings (minimal for testing)
        self.log_level = "WARNING"
        self.log_to_console = False
        self.log_file_path = "/tmp/ia_influencer_test.log"
        
        # JWT settings (short expiry for testing)
        self.jwt_access_token_expire = timedelta(minutes=15)
        self.jwt_refresh_token_expire = timedelta(hours=1)
        
        # Security settings (relaxed for testing)
        self.max_login_attempts = 10
        self.login_lockout_duration_minutes = 1
        
        # Feature toggles (selectively enabled for testing)
        self.enable_fingerprinting = True
        self.enable_content_protection = True
        self.enable_monetization = False  # Disabled to avoid payment calls
        self.enable_web_crawling = False  # Disabled to avoid external calls
        self.enable_ai_agent = True
        
        # Rate limiting (very high for testing)
        self.rate_limit_per_minute = 10000
        self.rate_limit_per_hour = 100000
        self.rate_limit_per_day = 1000000
        
        # Storage settings (temporary for testing)
        self.storage_type = "local"
        self.local_storage_path = "/tmp/test_uploads"
        self.max_upload_size = 1048576  # 1MB for testing
        
        # Blockchain settings (mock for testing)
        self.blockchain_enabled = False
        self.development_mode = True
        self.use_local_blockchain = True
        
        # External services (disabled for testing)
        self.prometheus.enabled = False
        self.grafana.enabled = False
        self.alertmanager_enabled = False
        
        # Business settings (minimal for testing)
        self.creator_commission_rate = 0.05
        self.platform_commission_rate = 0.01
        self.minimum_payout_threshold = 1.0


class StagingConfig(AppConfig):
    """Staging environment configuration"""
    
    def __init__(self):
        super().__init__()
        
        # Environment settings
        self.environment = "staging"
        self.debug = False
        self.testing = False
        
        # Security settings (production-like)
        self.cors_origins = [
            "https://staging-app.ia-influencer-agent.com",
            "https://staging-dashboard.ia-influencer-agent.com"
        ]
        
        # Database settings (staging database)
        self.database_url = os.getenv("STAGING_DATABASE_URL", 
            "postgresql://ia_user:secure_password@staging-db:5432/ia_influencer_agent_staging")
        self.database_name = "ia_influencer_agent_staging"
        self.database_max_connections = 50
        self.database_pool_size = 10
        
        # Redis settings (staging instance)
        self.redis_url = os.getenv("STAGING_REDIS_URL", "redis://staging-redis:6379/0")
        
        # MongoDB settings (staging cluster)
        self.mongodb_url = os.getenv("STAGING_MONGODB_URL", 
            "mongodb://staging-mongo:27017/ia_influencer_agent_staging")
        self.mongodb_database = "ia_influencer_agent_staging"
        
        # Elasticsearch settings (staging cluster)
        self.elasticsearch_url = os.getenv("STAGING_ELASTICSEARCH_URL", "http://staging-elasticsearch:9200")
        self.elasticsearch_index_prefix = "ia_influencer_staging"
        
        # Logging settings (structured for staging)
        self.log_level = "INFO"
        self.structured_logging = True
        self.log_file_path = "/var/log/ia_influencer_agent_staging.log"
        
        # JWT settings (moderate expiry for staging)
        self.jwt_access_token_expire = timedelta(hours=1)
        self.jwt_refresh_token_expire = timedelta(days=7)
        
        # Feature toggles (all enabled for staging testing)
        self.enable_fingerprinting = True
        self.enable_content_protection = True
        self.enable_monetization = True
        self.enable_web_crawling = True
        self.enable_ai_agent = True
        
        # Rate limiting (moderate for staging)
        self.rate_limit_per_minute = 200
        self.rate_limit_per_hour = 2000
        self.rate_limit_per_day = 20000
        
        # Storage settings (S3 compatible for staging)
        self.storage_type = "s3"
        self.s3_bucket_name = "ia-influencer-staging-storage"
        self.s3_region = "us-east-1"
        
        # Blockchain settings (testnet for staging)
        self.default_network = "polygon_mumbai"
        self.development_mode = False
        
        # Monitoring (enabled for staging)
        self.prometheus.enabled = True
        self.grafana.enabled = True
        self.prometheus_host = "staging-prometheus"
        self.grafana_host = "staging-grafana"
        
        # Business settings (realistic staging values)
        self.creator_commission_rate = 0.12
        self.platform_commission_rate = 0.03
        self.minimum_payout_threshold = 25.0


class ProductionConfig(AppConfig):
    """Production environment configuration"""
    
    def __init__(self):
        super().__init__()
        
        # Environment settings
        self.environment = "production"
        self.debug = False
        self.testing = False
        
        # Security settings (strict for production)
        self.cors_origins = [
            "https://app.ia-influencer-agent.com",
            "https://dashboard.ia-influencer-agent.com",
            "https://www.ia-influencer-agent.com"
        ]
        
        # Database settings (production cluster)
        self.database_url = os.getenv("PROD_DATABASE_URL", 
            "postgresql://ia_prod_user:ultra_secure_password@prod-db-cluster:5432/ia_influencer_agent")
        self.database_name = "ia_influencer_agent"
        self.database_max_connections = 200
        self.database_pool_size = 50
        self.database_ssl_mode = "require"
        
        # Redis settings (production cluster)
        self.redis_url = os.getenv("PROD_REDIS_URL", "redis://prod-redis-cluster:6379/0")
        self.redis_max_connections = 200
        
        # MongoDB settings (production replica set)
        self.mongodb_url = os.getenv("PROD_MONGODB_URL", 
            "mongodb://prod-mongo-cluster:27017/ia_influencer_agent?replicaSet=rs0")
        self.mongodb_database = "ia_influencer_agent"
        
        # Elasticsearch settings (production cluster)
        self.elasticsearch_url = os.getenv("PROD_ELASTICSEARCH_URL", "https://prod-elasticsearch:9200")
        self.elasticsearch_index_prefix = "ia_influencer_prod"
        
        # Logging settings (optimized for production)
        self.log_level = "WARNING"
        self.structured_logging = True
        self.log_file_path = "/var/log/ia_influencer_agent.log"
        self.log_max_size = 52428800  # 50MB
        self.log_backup_count = 10
        
        # JWT settings (secure expiry for production)
        self.jwt_access_token_expire = timedelta(minutes=30)
        self.jwt_refresh_token_expire = timedelta(days=30)
        
        # Security settings (maximum security)
        self.session_cookie_secure = True
        self.session_cookie_httponly = True
        self.session_cookie_samesite = "strict"
        self.max_login_attempts = 3
        self.login_lockout_duration_minutes = 60
        self.require_email_verification = True
        self.enable_two_factor_auth = True
        
        # Feature toggles (all enabled for production)
        self.enable_fingerprinting = True
        self.enable_content_protection = True
        self.enable_monetization = True
        self.enable_web_crawling = True
        self.enable_ai_agent = True
        
        # Rate limiting (strict for production)
        self.rate_limit_per_minute = 100
        self.rate_limit_per_hour = 1000
        self.rate_limit_per_day = 10000
        
        # Storage settings (AWS S3 for production)
        self.storage_type = "s3"
        self.s3_bucket_name = "ia-influencer-production-storage"
        self.s3_region = "us-east-1"
        
        # Blockchain settings (mainnet for production)
        self.default_network = "ethereum_mainnet"
        self.development_mode = False
        self.multi_sig_enabled = True
        
        # Monitoring (comprehensive for production)
        self.prometheus.enabled = True
        self.grafana.enabled = True
        self.jaeger.enabled = True
        self.elasticsearch_logging_enabled = True
        self.prometheus_host = "prod-prometheus"
        self.grafana_host = "prod-grafana"
        
        # Alerting (critical for production)
        self.alerts.enabled = True
        self.alerts.email_enabled = True
        self.alerts.slack_enabled = True
        self.alerts.webhook_enabled = True
        
        # Business settings (production rates)
        self.creator_commission_rate = 0.15  # 15%
        self.platform_commission_rate = 0.05  # 5%
        self.minimum_payout_threshold = 50.0
        self.payout_processing_time = 48  # 48 hours
        
        # Performance optimizations
        self.celery_worker_concurrency = 8
        self.vector_dimension = 512
        self.max_upload_size = 1073741824  # 1GB
        
        # Compliance settings
        self.audit_log_enabled = True
        self.security_log_enabled = True
        self.gdpr_compliance = True
        self.ccpa_compliance = True


def get_config_class(environment: str = None):
    """Get configuration class based on environment"""
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "dev": DevelopmentConfig,
        "testing": TestingConfig,
        "test": TestingConfig,
        "staging": StagingConfig,
        "stage": StagingConfig,
        "production": ProductionConfig,
        "prod": ProductionConfig
    }
    
    return config_map.get(environment, DevelopmentConfig)


def get_config(environment: str = None) -> AppConfig:
    """Get configuration instance based on environment"""
    config_class = get_config_class(environment)
    return config_class()


def validate_environment_config(config: AppConfig) -> Dict[str, Any]:
    """Validate environment-specific configuration"""
    issues = []
    
    # Production-specific validations
    if config.is_production:
        if config.debug:
            issues.append("Debug mode should be disabled in production")
        
        if not config.session_cookie_secure:
            issues.append("Secure cookies should be enabled in production")
        
        if config.cors_origins == ["*"]:
            issues.append("CORS origins should be specific in production")
        
        if config.log_level == "DEBUG":
            issues.append("Log level should not be DEBUG in production")
        
        if not config.database_ssl_mode or config.database_ssl_mode == "disable":
            issues.append("Database SSL should be enabled in production")
        
        if config.jwt_access_token_expire.total_seconds() > 3600:
            issues.append("JWT access token expiry should be <= 1 hour in production")
        
        if not config.multi_sig_enabled and config.blockchain_enabled:
            issues.append("Multi-signature should be enabled for blockchain in production")
    
    # Development-specific validations
    if config.is_development:
        if not config.debug:
            issues.append("Debug mode should be enabled in development")
        
        if config.log_level not in ["DEBUG", "INFO"]:
            issues.append("Log level should be DEBUG or INFO in development")
    
    # General validations
    if config.creator_commission_rate + config.platform_commission_rate > 0.5:
        issues.append("Total commission rates seem too high (>50%)")
    
    if config.minimum_payout_threshold <= 0:
        issues.append("Minimum payout threshold should be positive")
    
    if config.max_upload_size <= 0:
        issues.append("Max upload size should be positive")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "environment": config.environment,
        "config_class": config.__class__.__name__
    }
