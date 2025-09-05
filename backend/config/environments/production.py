"""Production Environment Configuration
=======================================

Production environment configuration with enterprise-grade security,
performance optimization, and high availability for the IA-Influencer Agent Platform.

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
    """Get production environment configuration"""
    return {
        'environment': 'production',
        'debug': False,
        'testing': False,
        'log_level': 'INFO',
        'hot_reload': False,
        
        # Database configuration for production
        'database': {
            'host': os.getenv('PROD_DB_HOST', ''),
            'port': int(os.getenv('PROD_DB_PORT', '5432')),
            'username': os.getenv('PROD_DB_USER', ''),
            'password': os.getenv('PROD_DB_PASSWORD', ''),
            'database': os.getenv('PROD_DB_NAME', 'ainflue_prod'),
            'pool_size': 20,
            'max_overflow': 50,
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'echo': False,
            'ssl_mode': 'require'
        },
        
        # Redis configuration for production
        'redis': {
            'host': os.getenv('PROD_REDIS_HOST', ''),
            'port': int(os.getenv('PROD_REDIS_PORT', '6379')),
            'db': int(os.getenv('PROD_REDIS_DB', '0')),
            'password': os.getenv('PROD_REDIS_PASSWORD', ''),
            'decode_responses': True,
            'socket_keepalive': True,
            'socket_keepalive_options': {},
            'connection_pool_max_size': 50,
            'retry_on_timeout': True,
            'ssl': True
        },
        
        # API configuration for production
        'api': {
            'host': os.getenv('PROD_API_HOST', '0.0.0.0'),
            'port': int(os.getenv('PROD_API_PORT', '8000')),
            'reload': False,
            'workers': int(os.getenv('PROD_API_WORKERS', '4')),
            'access_log': False,
            'cors_origins': os.getenv('PROD_CORS_ORIGINS', '').split(','),
            'timeout_keep_alive': 5,
            'max_requests': 1000,
            'max_requests_jitter': 100
        },
        
        # Security settings (production-grade)
        'security': {
            'secret_key': os.getenv('PROD_SECRET_KEY', ''),
            'algorithm': 'HS256',
            'access_token_expire_minutes': 60,  # 1 hour
            'refresh_token_expire_days': 7,
            'password_min_length': 12,
            'require_email_verification': True,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30,
            'enable_2fa': True,
            'session_timeout_minutes': 30,
            'csrf_protection': True,
            'content_security_policy': True
        },
        
        # AI/ML configuration for production
        'ai_ml': {
            'model_cache_dir': '/opt/ainflue/models',
            'enable_gpu': True,
            'gpu_memory_fraction': 0.8,
            'model_download_timeout': 600,
            'inference_timeout': 10,
            'batch_size': 32,
            'model_versioning': True,
            'auto_scaling': True,
            'load_balancing': True
        },
        
        # Storage configuration for production
        'storage': {
            'type': 's3',
            'aws_access_key_id': os.getenv('PROD_AWS_ACCESS_KEY_ID', ''),
            'aws_secret_access_key': os.getenv('PROD_AWS_SECRET_ACCESS_KEY', ''),
            'bucket_name': os.getenv('PROD_S3_BUCKET', ''),
            'region': os.getenv('PROD_AWS_REGION', 'eu-central-1'),
            'max_file_size': 500 * 1024 * 1024,  # 500MB
            'cdn_domain': os.getenv('PROD_CDN_DOMAIN', ''),
            'encryption': True,
            'versioning': True
        },
        
        # Monitoring configuration for production
        'monitoring': {
            'enable_metrics': True,
            'enable_tracing': True,
            'enable_logging': True,
            'log_sql_queries': False,
            'log_requests': False,
            'metrics_port': 9090,
            'health_check_interval': 30,
            'prometheus_enabled': True,
            'jaeger_enabled': True,
            'elasticsearch_enabled': True
        },
        
        # External services (production endpoints)
        'external_services': {
            'openai': {
                'api_key': os.getenv('PROD_OPENAI_API_KEY', ''),
                'model': 'gpt-4',
                'timeout': 30,
                'rate_limit': 1000,
                'retry_attempts': 3
            },
            'stripe': {
                'publishable_key': os.getenv('PROD_STRIPE_PUBLISHABLE_KEY', ''),
                'secret_key': os.getenv('PROD_STRIPE_SECRET_KEY', ''),
                'webhook_secret': os.getenv('PROD_STRIPE_WEBHOOK_SECRET', ''),
                'test_mode': False
            }
        },
        
        # Performance settings
        'performance': {
            'cache_ttl': 3600,  # 1 hour
            'session_cache_ttl': 1800,  # 30 minutes
            'api_rate_limit': '100/minute',
            'database_query_timeout': 30,
            'redis_timeout': 5,
            'connection_timeout': 10,
            'read_timeout': 30
        },
        
        # High availability settings
        'high_availability': {
            'enable_clustering': True,
            'replica_count': 3,
            'load_balancer': True,
            'auto_failover': True,
            'health_checks': True,
            'circuit_breaker': True,
            'retry_policy': True
        },
        
        # Feature flags for production
        'features': {
            'enable_ai_processing': True,
            'enable_real_time_analytics': True,
            'enable_advanced_security': True,
            'enable_content_protection': True,
            'enable_monetization': True,
            'enable_compliance_monitoring': True,
            'enable_audit_logging': True
        }
    }

def get_database_url() -> str:
    """Get database URL for production environment"""
    config = get_config()['database']
    return f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?sslmode={config['ssl_mode']}"

def get_redis_url() -> str:
    """Get Redis URL for production environment"""
    config = get_config()['redis']
    ssl_part = "s" if config['ssl'] else ""
    return f"redis{ssl_part}://:{config['password']}@{config['host']}:{config['port']}/{config['db']}"