"""
Enterprise Browser/API Drivers Module Index
===========================================

Central index file for easy access to all driver system components.
Provides convenient imports and factory functions for common use cases.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.
"""

# Import all components from the module
from . import *

# Convenience factory functions for common patterns
def create_enterprise_automation_suite():
    """
    Create a complete enterprise automation suite with all components
    configured for production use.
    """
    return {
        'automation_controller': create_automation_controller(),
        'browser_manager': create_browser_manager(max_sessions=20),
        'api_manager': APIClientManager(),
        'session_pool_manager': SessionPoolManager(),
        'proxy_manager': ProxyManager(),
        'user_agent_rotator': create_stealth_rotator(),
        'request_manager': create_request_manager(),
        'connection_pool': create_connection_pool()
    }


async def create_production_automation_stack():
    """
    Create production-ready automation stack with all managers initialized.
    """
    # Initialize automation controller
    controller = await create_automation_controller(
        mode=AutomationMode.BALANCED,
        max_concurrent_tasks=50,
        max_browser_sessions=10,
        max_api_sessions=100
    )
    
    # Initialize request manager
    request_manager = await create_request_manager(
        max_concurrent_requests=100,
        connection_pool_size=200,
        enable_rate_limiting=True
    )
    
    # Initialize connection pool manager
    pool_manager = await create_pool_manager(
        default_config=create_pool_configuration(
            max_connections=200,
            max_per_host=50,
            strategy=PoolStrategy.LEAST_CONNECTIONS
        )
    )
    
    return {
        'controller': controller,
        'request_manager': request_manager,
        'pool_manager': pool_manager
    }


def create_stealth_crawling_setup():
    """
    Create optimized setup for stealth web crawling operations.
    """
    # Browser configuration
    browser_config = create_stealth_config()
    
    # Session pool configuration
    pool_config = create_stealth_pool_config()
    
    # User agent rotator
    ua_rotator = create_stealth_rotator()
    
    # Proxy manager
    proxy_manager = ProxyManager()
    
    return {
        'browser_config': browser_config,
        'pool_config': pool_config,
        'user_agent_rotator': ua_rotator,
        'proxy_manager': proxy_manager
    }


def create_high_performance_crawling_setup():
    """
    Create setup optimized for high-performance crawling with request management.
    """
    # Request manager with performance settings
    request_config = RequestConfig(
        timeout=15,
        enable_compression=True,
        verify_ssl=False
    )
    
    retry_config = RetryConfig(
        max_attempts=2,
        strategy=RetryStrategy.FIXED_DELAY,
        base_delay=0.5
    )
    
    rate_limit = RateLimitConfig(
        requests_per_second=10.0,
        burst_limit=50
    )
    
    return {
        'request_config': request_config,
        'retry_config': retry_config,
        'rate_limit': rate_limit,
        'browser_config': create_performance_config(),
        'pool_config': create_pool_configuration(
            max_connections=100,
            strategy=PoolStrategy.FASTEST_RESPONSE
        )
    }


def create_enterprise_monitoring_setup():
    """
    Create comprehensive monitoring setup for all drivers.
    """
    automation_metrics = AutomationMetrics()
    request_metrics = RequestMetrics()
    pool_metrics = PoolMetrics()
    
    return {
        'automation_metrics': automation_metrics,
        'request_metrics': request_metrics,
        'pool_metrics': pool_metrics,
        'monitoring_enabled': True,
        'health_check_interval': 60
    }


def create_api_monitoring_setup():
    """
    Create setup optimized for API monitoring and data collection.
    """
    api_manager = APIClientManager()
    
    # Rate limit configurations for different platforms
    rate_configs = {
        'twitter': RateLimitConfig(
            requests_per_minute=50,
            requests_per_hour=1000,
            requests_per_day=5000
        ),
        'youtube': RateLimitConfig(
            requests_per_minute=100,
            requests_per_hour=10000,
            requests_per_day=100000
        )
    }
    
    return {
        'api_manager': api_manager,
        'rate_configs': rate_configs
    }


def create_mobile_testing_setup():
    """
    Create setup optimized for mobile device testing and emulation.
    """
    # Mobile browser configurations
    mobile_configs = [
        BrowserConfiguration(
            browser_type=BrowserType.CHROME,
            mode=BrowserMode.GUI,
            window_size=(375, 667),  # iPhone SE
            user_agent=get_random_user_agent(BrowserFamily.CHROME_MOBILE)
        ),
        BrowserConfiguration(
            browser_type=BrowserType.CHROME,
            mode=BrowserMode.GUI,
            window_size=(414, 896),  # iPhone 11
            user_agent=get_random_user_agent(BrowserFamily.MOBILE_SAFARI)
        )
    ]
    
    # Mobile user agent rotator
    mobile_rotator = create_mobile_rotator()
    
    return {
        'mobile_configs': mobile_configs,
        'mobile_rotator': mobile_rotator
    }


# Quick access patterns
COMMON_PATTERNS = {
    'stealth_crawling': create_stealth_crawling_setup,
    'performance_crawling': create_performance_crawling_setup,
    'api_monitoring': create_api_monitoring_setup,
    'mobile_testing': create_mobile_testing_setup,
    'enterprise_suite': create_enterprise_automation_suite
}


def get_pattern(pattern_name: str):
    """Get a pre-configured pattern by name"""
    pattern_func = COMMON_PATTERNS.get(pattern_name)
    if pattern_func:
        return pattern_func()
    else:
        available = ', '.join(COMMON_PATTERNS.keys())
        raise ValueError(f"Unknown pattern '{pattern_name}'. Available: {available}")


# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"
__description__ = "Enterprise Browser/API Drivers for Industrial-Grade Automation"

# Quick reference for developers
QUICK_REFERENCE = {
    'browser_management': {
        'create_manager': 'create_browser_manager()',
        'stealth_config': 'create_stealth_config()',
        'performance_config': 'create_performance_config()'
    },
    'api_clients': {
        'twitter': 'create_twitter_client(token)',
        'youtube': 'create_youtube_client(api_key)',
        'manager': 'APIClientManager()'
    },
    'session_pooling': {
        'manager': 'SessionPoolManager()',
        'stealth_pool': 'create_stealth_pool_config()',
        'performance_pool': 'create_performance_pool_config()'
    },
    'proxy_management': {
        'manager': 'ProxyManager()',
        'residential': 'create_residential_proxy_config()',
        'datacenter': 'create_datacenter_proxy_config()'
    },
    'user_agents': {
        'desktop': 'create_desktop_rotator()',
        'mobile': 'create_mobile_rotator()',
        'stealth': 'create_stealth_rotator()',
        'random': 'get_random_user_agent()'
    }
}
