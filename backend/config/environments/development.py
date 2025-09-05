"""Development Environment Configuration
==========================================

Development environment configuration for local development with debugging,
hot reload, and development-friendly settings for the IA-Influencer Agent Platform.

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
    """Get development environment configuration"""
    return {
        'environment': 'development',
        'debug': True,
        'testing': False,
        'log_level': 'DEBUG',
        'hot_reload': True,
        
        # Database configuration for development
        'database': {
            'host': os.getenv('DEV_DB_HOST', 'localhost'),
            'port': int(os.getenv('DEV_DB_PORT', '5432')),
            'username': os.getenv('DEV_DB_USER', 'ainflue_dev'),
            'password': os.getenv('DEV_DB_PASSWORD', 'dev_password'),
            'database': os.getenv('DEV_DB_NAME', 'ainflue_dev'),
            'pool_size': 5,
            'max_overflow': 10,
            'echo': True  # SQL query logging for development
        },
        
        # Redis configuration for development
        'redis': {
            'host': os.getenv('DEV_REDIS_HOST', 'localhost'),
            'port': int(os.getenv('DEV_REDIS_PORT', '6379')),
            'db': int(os.getenv('DEV_REDIS_DB', '0')),
            'password': os.getenv('DEV_REDIS_PASSWORD', None),
            'decode_responses': True
        },
        
        # API configuration for development
        'api': {
            'host': os.getenv('DEV_API_HOST', '0.0.0.0'),
            'port': int(os.getenv('DEV_API_PORT', '8000')),
            'reload': True,
            'workers': 1,
            'access_log': True,
            'cors_origins': ['http://localhost:3000', 'http://127.0.0.1:3000']
        },
        
        # Security settings (relaxed for development)
        'security': {
            'secret_key': os.getenv('DEV_SECRET_KEY', 'development-secret-key-change-in-production'),
            'algorithm': 'HS256',
            'access_token_expire_minutes': 60 * 24,  # 24 hours for development
            'password_min_length': 6,  # Relaxed for development
            'require_email_verification': False
        },
        
        # AI/ML configuration for development
        'ai_ml': {
            'model_cache_dir': '/tmp/ainflue_models_dev',
            'enable_gpu': False,  # Disable GPU for local development
            'model_download_timeout': 300,
            'inference_timeout': 30,
            'batch_size': 1
        },
        
        # Storage configuration for development
        'storage': {
            'type': 'local',
            'local_path': '/tmp/ainflue_storage_dev',
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'allowed_extensions': ['.jpg', '.jpeg', '.png', '.gif', '.mp3', '.wav', '.mp4', '.avi']
        },
        
        # Monitoring configuration for development
        'monitoring': {
            'enable_metrics': False,
            'enable_tracing': False,
            'log_sql_queries': True,
            'log_requests': True,
            'metrics_port': 9090
        },
        
        # External services (development/testing endpoints)
        'external_services': {
            'openai': {
                'api_key': os.getenv('DEV_OPENAI_API_KEY', ''),
                'model': 'gpt-3.5-turbo',
                'timeout': 30
            },
            'stripe': {
                'publishable_key': os.getenv('DEV_STRIPE_PUBLISHABLE_KEY', ''),
                'secret_key': os.getenv('DEV_STRIPE_SECRET_KEY', ''),
                'webhook_secret': os.getenv('DEV_STRIPE_WEBHOOK_SECRET', ''),
                'test_mode': True
            }
        },
        
        # Feature flags for development
        'features': {
            'enable_ai_processing': True,
            'enable_real_time_analytics': False,
            'enable_advanced_security': False,
            'enable_content_protection': True,
            'enable_monetization': True
        }
    }

def get_database_url() -> str:
    """Get database URL for development environment"""
    config = get_config()['database']
    return f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

def get_redis_url() -> str:
    """Get Redis URL for development environment"""
    config = get_config()['redis']
    password_part = f":{config['password']}@" if config['password'] else ""
    return f"redis://{password_part}{config['host']}:{config['port']}/{config['db']}"