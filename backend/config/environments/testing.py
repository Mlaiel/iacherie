"""Testing Environment Configuration
====================================

Testing environment configuration optimized for automated testing,
CI/CD pipelines, and quality assurance for the IA-Influencer Agent Platform.

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
    """Get testing environment configuration"""
    return {
        'environment': 'testing',
        'debug': True,
        'testing': True,
        'log_level': 'DEBUG',
        'hot_reload': False,
        
        # Database configuration for testing (in-memory or lightweight)
        'database': {
            'host': os.getenv('TEST_DB_HOST', 'localhost'),
            'port': int(os.getenv('TEST_DB_PORT', '5432')),
            'username': os.getenv('TEST_DB_USER', 'ainflue_test'),
            'password': os.getenv('TEST_DB_PASSWORD', 'test_password'),
            'database': os.getenv('TEST_DB_NAME', 'ainflue_test'),
            'pool_size': 1,
            'max_overflow': 0,
            'echo': False,
            'use_in_memory': True  # For unit tests
        },
        
        # Redis configuration for testing
        'redis': {
            'host': os.getenv('TEST_REDIS_HOST', 'localhost'),
            'port': int(os.getenv('TEST_REDIS_PORT', '6379')),
            'db': int(os.getenv('TEST_REDIS_DB', '15')),  # Separate DB for tests
            'password': os.getenv('TEST_REDIS_PASSWORD', None),
            'decode_responses': True,
            'socket_timeout': 1,
            'connection_pool_max_size': 1
        },
        
        # API configuration for testing
        'api': {
            'host': '127.0.0.1',
            'port': int(os.getenv('TEST_API_PORT', '8001')),
            'reload': False,
            'workers': 1,
            'access_log': False,
            'cors_origins': ['http://localhost:3000'],
            'testing_mode': True
        },
        
        # Security settings (relaxed for testing)
        'security': {
            'secret_key': 'test-secret-key-for-testing-only',
            'algorithm': 'HS256',
            'access_token_expire_minutes': 5,  # Short for testing
            'password_min_length': 4,
            'require_email_verification': False,
            'max_login_attempts': 100,  # High for testing
            'lockout_duration_minutes': 1,
            'enable_2fa': False,
            'bypass_rate_limiting': True
        },
        
        # AI/ML configuration for testing (mock/fast modes)
        'ai_ml': {
            'model_cache_dir': '/tmp/ainflue_test_models',
            'enable_gpu': False,
            'model_download_timeout': 60,
            'inference_timeout': 5,
            'batch_size': 1,
            'use_mock_models': True,
            'fast_inference': True
        },
        
        # Storage configuration for testing (local/temporary)
        'storage': {
            'type': 'local',
            'local_path': '/tmp/ainflue_test_storage',
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'cleanup_after_test': True,
            'use_temp_dirs': True
        },
        
        # Monitoring configuration for testing
        'monitoring': {
            'enable_metrics': False,
            'enable_tracing': False,
            'enable_logging': True,
            'log_sql_queries': True,
            'log_requests': False,
            'silent_mode': False,  # For test output
            'capture_logs': True
        },
        
        # External services (mock/test endpoints)
        'external_services': {
            'openai': {
                'api_key': 'test-api-key',
                'model': 'gpt-3.5-turbo',
                'timeout': 5,
                'use_mock': True,
                'mock_responses': True
            },
            'stripe': {
                'publishable_key': 'pk_test_mock',
                'secret_key': 'sk_test_mock',
                'webhook_secret': 'whsec_test_mock',
                'test_mode': True,
                'use_mock': True
            }
        },
        
        # Test-specific settings
        'testing': {
            'parallel_execution': True,
            'test_isolation': True,
            'auto_rollback': True,
            'mock_external_calls': True,
            'fast_mode': True,
            'skip_slow_tests': False,
            'test_timeout': 30,
            'assertion_verbose': True
        },
        
        # Performance settings (minimal for testing)
        'performance': {
            'cache_ttl': 60,  # 1 minute
            'session_cache_ttl': 30,
            'api_rate_limit': 'disabled',
            'database_query_timeout': 5,
            'redis_timeout': 1,
            'connection_timeout': 2,
            'read_timeout': 5
        },
        
        # Feature flags for testing (all enabled for comprehensive testing)
        'features': {
            'enable_ai_processing': True,
            'enable_real_time_analytics': False,
            'enable_advanced_security': False,
            'enable_content_protection': True,
            'enable_monetization': True,
            'enable_experimental_features': True,
            'enable_test_features': True
        }
    }

def get_database_url() -> str:
    """Get database URL for testing environment"""
    config = get_config()['database']
    if config.get('use_in_memory'):
        return 'sqlite:///:memory:'
    return f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

def get_redis_url() -> str:
    """Get Redis URL for testing environment"""
    config = get_config()['redis']
    password_part = f":{config['password']}@" if config['password'] else ""
    return f"redis://{password_part}{config['host']}:{config['port']}/{config['db']}"

def setup_test_environment():
    """Setup test environment with required services and data"""
    import tempfile
    import shutil
    
    config = get_config()
    
    # Create temporary directories
    storage_path = config['storage']['local_path']
    models_path = config['ai_ml']['model_cache_dir']
    
    for path in [storage_path, models_path]:
        os.makedirs(path, exist_ok=True)
    
    return config

def cleanup_test_environment():
    """Cleanup test environment and temporary data"""
    import tempfile
    import shutil
    
    config = get_config()
    
    # Cleanup temporary directories
    storage_path = config['storage']['local_path']
    models_path = config['ai_ml']['model_cache_dir']
    
    for path in [storage_path, models_path]:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)