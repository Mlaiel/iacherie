"""Staging Environment Configuration
====================================

Staging environment configuration that mirrors production settings
for pre-production testing and validation of the IA-Influencer Agent Platform.

Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
=====================================
This code is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is STRICTLY PROHIBITED
and will result in immediate legal action under German and International law.

For licensing, collaboration, or business inquiries:
📧 Contact: mlaiel@live.de
🌐 Official Project: IA-Influencer Agent Platform
"""

from typing import Dict, Any
import os

def get_config() -> Dict[str, Any]:
    """Get staging environment configuration"""
    return {
        'environment': 'staging',
        'debug': False,
        'testing': False,
        'log_level': 'INFO',
        'hot_reload': False,
        
        # Database configuration for staging
        'database': {
            'host': os.getenv('STAGING_DB_HOST', ''),
            'port': int(os.getenv('STAGING_DB_PORT', '5432')),
            'username': os.getenv('STAGING_DB_USER', ''),
            'password': os.getenv('STAGING_DB_PASSWORD', ''),
            'database': os.getenv('STAGING_DB_NAME', 'ainflue_staging'),
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'echo': False,
            'ssl_mode': 'require'
        },
        
        # Redis configuration for staging
        'redis': {
            'host': os.getenv('STAGING_REDIS_HOST', ''),
            'port': int(os.getenv('STAGING_REDIS_PORT', '6379')),
            'db': int(os.getenv('STAGING_REDIS_DB', '1')),
            'password': os.getenv('STAGING_REDIS_PASSWORD', ''),
            'decode_responses': True,
            'socket_keepalive': True,
            'connection_pool_max_size': 20,
            'retry_on_timeout': True,
            'ssl': True
        },
        
        # API configuration for staging
        'api': {
            'host': os.getenv('STAGING_API_HOST', '0.0.0.0'),
            'port': int(os.getenv('STAGING_API_PORT', '8000')),
            'reload': False,
            'workers': int(os.getenv('STAGING_API_WORKERS', '2')),
            'access_log': True,
            'cors_origins': os.getenv('STAGING_CORS_ORIGINS', '').split(','),
            'timeout_keep_alive': 5
        },
        
        # Security settings (production-like but with staging adjustments)
        'security': {
            'secret_key': os.getenv('STAGING_SECRET_KEY', ''),
            'algorithm': 'HS256',
            'access_token_expire_minutes': 60,
            'refresh_token_expire_days': 7,
            'password_min_length': 10,
            'require_email_verification': True,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 15,
            'enable_2fa': False,  # Disabled for easier testing
            'session_timeout_minutes': 60,
            'csrf_protection': True
        },
        
        # AI/ML configuration for staging
        'ai_ml': {
            'model_cache_dir': '/opt/ainflue/models_staging',
            'enable_gpu': True,
            'gpu_memory_fraction': 0.6,
            'model_download_timeout': 300,
            'inference_timeout': 15,
            'batch_size': 16,
            'model_versioning': True,
            'auto_scaling': False  # Disabled for cost control
        },
        
        # Storage configuration for staging
        'storage': {
            'type': 's3',
            'aws_access_key_id': os.getenv('STAGING_AWS_ACCESS_KEY_ID', ''),
            'aws_secret_access_key': os.getenv('STAGING_AWS_SECRET_ACCESS_KEY', ''),
            'bucket_name': os.getenv('STAGING_S3_BUCKET', ''),
            'region': os.getenv('STAGING_AWS_REGION', 'eu-central-1'),
            'max_file_size': 200 * 1024 * 1024,  # 200MB
            'encryption': True,
            'versioning': False  # Disabled for cost control
        },
        
        # Monitoring configuration for staging
        'monitoring': {
            'enable_metrics': True,
            'enable_tracing': True,
            'enable_logging': True,
            'log_sql_queries': True,  # Enabled for debugging
            'log_requests': True,
            'metrics_port': 9090,
            'health_check_interval': 60,
            'prometheus_enabled': True,
            'jaeger_enabled': True,
            'elasticsearch_enabled': False  # Disabled for cost control
        },
        
        # External services (staging/test endpoints)
        'external_services': {
            'openai': {
                'api_key': os.getenv('STAGING_OPENAI_API_KEY', ''),
                'model': 'gpt-3.5-turbo',
                'timeout': 30,
                'rate_limit': 100,
                'retry_attempts': 2
            },
            'stripe': {
                'publishable_key': os.getenv('STAGING_STRIPE_PUBLISHABLE_KEY', ''),
                'secret_key': os.getenv('STAGING_STRIPE_SECRET_KEY', ''),
                'webhook_secret': os.getenv('STAGING_STRIPE_WEBHOOK_SECRET', ''),
                'test_mode': True
            }
        },
        
        # Performance settings (moderate)
        'performance': {
            'cache_ttl': 1800,  # 30 minutes
            'session_cache_ttl': 900,  # 15 minutes
            'api_rate_limit': '50/minute',
            'database_query_timeout': 30,
            'redis_timeout': 5,
            'connection_timeout': 10,
            'read_timeout': 30
        },
        
        # Feature flags for staging
        'features': {
            'enable_ai_processing': True,
            'enable_real_time_analytics': True,
            'enable_advanced_security': True,
            'enable_content_protection': True,
            'enable_monetization': True,
            'enable_compliance_monitoring': True,
            'enable_audit_logging': True,
            'enable_experimental_features': True  # For testing new features
        }
    }

def get_database_url() -> str:
    """Get database URL for staging environment"""
    config = get_config()['database']
    return f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?sslmode={config['ssl_mode']}"

def get_redis_url() -> str:
    """Get Redis URL for staging environment"""
    config = get_config()['redis']
    ssl_part = "s" if config['ssl'] else ""
    return f"redis{ssl_part}://:{config['password']}@{config['host']}:{config['port']}/{config['db']}"