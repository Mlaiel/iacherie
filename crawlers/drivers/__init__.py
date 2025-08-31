"""Enterprise Browser/API Drivers Module
====================================

Professional driver systems for industrial-grade browser automation and API interactions.
Implements WebDriver management, API client interfaces, session pooling, and proxy management.

Key Features:
- Enterprise Browser Management with session pooling
- Multi-platform API client management 
- Advanced WebDriver factory with optimization profiles
- Intelligent proxy rotation and management
- User agent rotation and fingerprint masking
- Performance monitoring and health checking
- Automated task orchestration and control
- Advanced request management with retries
- Connection pooling and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.

Professional Development Team Specialties:
🥇 Lead AI Developer & Backend Senior Engineer - Advanced automation systems
🥇 Machine Learning Engineer & Audio Processing Specialist - Intelligence optimization  
🥇 Database Administrator & Security Expert - Data protection and performance
🥇 Microservices Architect & DevOps Engineer - Scalable infrastructure
🥇 AI Prompt Engineer & Content Protection Specialist - Content security
"""
# Browser Management
from .browser_manager import (
    BrowserManager,
    BrowserType,
    BrowserMode,
    BrowserConfiguration,
    BrowserCapabilities,
    BrowserSession,
    SessionStatus,
    ChromeDriver,
    FirefoxDriver,
    create_browser_manager,
    create_stealth_config,
    create_performance_config
)

# Configuration Management
from .config_manager import (
    ConfigurationManager,
    DriversConfiguration,
    Environment,
    ConfigSource,
    ProxyConfig,
    BrowserConfig,
    APIConfig,
    ConnectionConfig,
    SecurityConfig,
    MonitoringConfig,
    get_config_manager,
    load_drivers_config
)

# Automation Controller
from .automation_controller import (
    AutomationController,
    AutomationMode,
    TaskPriority,
    AutomationStatus,
    AutomationTask,
    AutomationMetrics,
    create_automation_controller,
    automation_context
)

# Browser Automation
from .browser_automation import (
    BrowserManager as AdvancedBrowserManager,
    BrowserConfiguration as AdvancedBrowserConfiguration,
    BrowserCapabilities as AdvancedBrowserCapabilities,
    BrowserSession as AdvancedBrowserSession,
    ChromeDriver as AdvancedChromeDriver,
    FirefoxDriver as AdvancedFirefoxDriver,
    create_browser_manager as create_advanced_browser_manager,
    create_stealth_config as create_advanced_stealth_config,
    create_performance_config as create_advanced_performance_config
)

# Request Management
from .request_manager import (
    RequestManager,
    RequestMethod,
    RetryStrategy,
    RequestPriority,
    RateLimitConfig,
    RetryConfig,
    RequestConfig,
    RequestMetrics,
    RequestRecord,
    create_request_manager,
    create_rate_limit_config,
    create_retry_config
)

# Connection Pool Management
from .connection_pool import (
    ConnectionPool,
    ConnectionPoolManager,
    ConnectionStatus,
    PoolStrategy,
    ConnectionInfo,
    PoolConfiguration,
    PoolMetrics,
    create_pool_configuration,
    create_connection_pool,
    create_pool_manager
)

# API Client Management
from .api_client_manager import (
    APIClientManager,
    APIClient,
    PlatformType,
    AuthType,
    ClientStatus,
    APIResponse,
    APIClientConfig,
    AuthCredentials,
    RateLimitConfig,
    TwitterAPIClient,
    YouTubeAPIClient,
    create_twitter_client,
    create_youtube_client
)

# WebDriver Factory
from .webdriver_factory import (
    WebDriverFactory,
    DriverProfile,
    EnvironmentType,
    DriverPreset,
    create_stealth_driver,
    create_performance_driver,
    create_mobile_driver,
    create_testing_driver
)

# Session Pool Management
from .session_pool import (
    SessionPool,
    SessionPoolManager,
    PoolConfiguration,
    PoolStrategy,
    SessionPriority,
    PooledSession,
    SessionMetrics,
    create_stealth_pool_config,
    create_performance_pool_config
)

# Proxy Management
from .proxy_manager import (
    ProxyManager,
    ProxyType,
    ProxyProvider,
    ProxyStatus,
    ProxyConfiguration,
    ProxyCredentials,
    ProxyInstance,
    ProxyMetrics,
    ProxyValidator,
    ProxyRotator,
    create_residential_proxy_config,
    create_datacenter_proxy_config
)

# User Agent Management
from .user_agent_rotator import (
    UserAgentRotator,
    UserAgentDatabase,
    HeaderGenerator,
    BrowserFamily,
    PlatformType as UAPlatformType,
    DeviceType,
    RotationStrategy,
    UserAgentData,
    HeaderProfile,
    create_desktop_rotator,
    create_mobile_rotator,
    create_stealth_rotator,
    get_random_user_agent,
    get_chrome_user_agent
)

__all__ = [
    # Browser Management
    'BrowserManager',
    'BrowserType',
    'BrowserMode', 
    'BrowserConfiguration',
    'BrowserCapabilities',
    'BrowserSession',
    'SessionStatus',
    'ChromeDriver',
    'FirefoxDriver',
    'create_browser_manager',
    'create_stealth_config',
    'create_performance_config',
    
    # API Client Management
    'APIClientManager',
    'APIClient',
    'PlatformType',
    'AuthType',
    'ClientStatus',
    'APIResponse',
    'APIClientConfig',
    'AuthCredentials',
    'RateLimitConfig',
    'TwitterAPIClient',
    'YouTubeAPIClient',
    'create_twitter_client',
    'create_youtube_client',
    
    # WebDriver Factory
    'WebDriverFactory',
    'DriverProfile',
    'EnvironmentType',
    'DriverPreset',
    'create_stealth_driver',
    'create_performance_driver',
    'create_mobile_driver',
    'create_testing_driver',
    
    # Session Pool Management
    'SessionPool',
    'SessionPoolManager',
    'PoolConfiguration',
    'PoolStrategy',
    'SessionPriority',
    'PooledSession',
    'SessionMetrics',
    'create_stealth_pool_config',
    'create_performance_pool_config',
    
    # Proxy Management
    'ProxyManager',
    'ProxyType',
    'ProxyProvider',
    'ProxyStatus',
    'ProxyConfiguration',
    'ProxyCredentials',
    'ProxyInstance',
    'ProxyMetrics',
    'ProxyValidator',
    'ProxyRotator',
    'create_residential_proxy_config',
    'create_datacenter_proxy_config',
    
    # User Agent Management
    'UserAgentRotator',
    'UserAgentDatabase',
    'HeaderGenerator',
    'BrowserFamily',
    'UAPlatformType',
    'DeviceType',
    'RotationStrategy',
    'UserAgentData',
    'HeaderProfile',
    'create_desktop_rotator',
    'create_mobile_rotator',
    'create_stealth_rotator',
    'get_random_user_agent',
    'get_chrome_user_agent'
]
