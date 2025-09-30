"""Platform APIs Integration Module
================================

Complete platform integration system with OAuth, rate limiting, and API management.
Supports YouTube, Instagram, TikTok, Spotify, Facebook, Twitter, and DMCA services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

# Core components that don't require external dependencies
try:
    from .api_rate_limiter import APIRateLimiter
    _API_RATE_LIMITER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"APIRateLimiter not available: {e}")
    APIRateLimiter = None
    _API_RATE_LIMITER_AVAILABLE = False

# Components that require aiohttp (optional dependency)
_AIOHTTP_COMPONENTS = {}
_AIOHTTP_AVAILABLE = False

try:
    import aiohttp
    _AIOHTTP_AVAILABLE = True
    
    # Try to import aiohttp-dependent components
    try:
        from .platform_coordinator import PlatformCoordinator
        _AIOHTTP_COMPONENTS['PlatformCoordinator'] = PlatformCoordinator
    except ImportError as e:
        logger.warning(f"PlatformCoordinator not available: {e}")
        _AIOHTTP_COMPONENTS['PlatformCoordinator'] = None

    try:
        from .platform_oauth_manager import PlatformOAuthManager
        _AIOHTTP_COMPONENTS['PlatformOAuthManager'] = PlatformOAuthManager
    except ImportError as e:
        logger.warning(f"PlatformOAuthManager not available: {e}")
        _AIOHTTP_COMPONENTS['PlatformOAuthManager'] = None

    try:
        from .youtube_content_id_api import YouTubeContentIDAPI
        _AIOHTTP_COMPONENTS['YouTubeContentIDAPI'] = YouTubeContentIDAPI
    except ImportError as e:
        logger.warning(f"YouTubeContentIDAPI not available: {e}")
        _AIOHTTP_COMPONENTS['YouTubeContentIDAPI'] = None

    try:
        from .instagram_business_api import InstagramBusinessAPI
        _AIOHTTP_COMPONENTS['InstagramBusinessAPI'] = InstagramBusinessAPI
    except ImportError as e:
        logger.warning(f"InstagramBusinessAPI not available: {e}")
        _AIOHTTP_COMPONENTS['InstagramBusinessAPI'] = None

    try:
        from .tiktok_creator_api import TikTokCreatorAPI
        _AIOHTTP_COMPONENTS['TikTokCreatorAPI'] = TikTokCreatorAPI
    except ImportError as e:
        logger.warning(f"TikTokCreatorAPI not available: {e}")
        _AIOHTTP_COMPONENTS['TikTokCreatorAPI'] = None

    try:
        from .spotify_artists_api import SpotifyArtistsAPI
        _AIOHTTP_COMPONENTS['SpotifyArtistsAPI'] = SpotifyArtistsAPI
    except ImportError as e:
        logger.warning(f"SpotifyArtistsAPI not available: {e}")
        _AIOHTTP_COMPONENTS['SpotifyArtistsAPI'] = None

    try:
        from .facebook_rights_api import FacebookRightsAPI
        _AIOHTTP_COMPONENTS['FacebookRightsAPI'] = FacebookRightsAPI
    except ImportError as e:
        logger.warning(f"FacebookRightsAPI not available: {e}")
        _AIOHTTP_COMPONENTS['FacebookRightsAPI'] = None

    try:
        from .twitter_api_v2 import TwitterAPIv2
        _AIOHTTP_COMPONENTS['TwitterAPIv2'] = TwitterAPIv2
    except ImportError as e:
        logger.warning(f"TwitterAPIv2 not available: {e}")
        _AIOHTTP_COMPONENTS['TwitterAPIv2'] = None

    try:
        from .dmca_services_api import DMCAServicesAPI
        _AIOHTTP_COMPONENTS['DMCAServicesAPI'] = DMCAServicesAPI
    except ImportError as e:
        logger.warning(f"DMCAServicesAPI not available: {e}")
        _AIOHTTP_COMPONENTS['DMCAServicesAPI'] = None

except ImportError:
    logger.info("aiohttp not available. Platform API integrations will be disabled.")
    # Create placeholder classes for missing components
    _AIOHTTP_COMPONENTS = {
        'PlatformCoordinator': None,
        'PlatformOAuthManager': None,
        'YouTubeContentIDAPI': None,
        'InstagramBusinessAPI': None,
        'TikTokCreatorAPI': None,
        'SpotifyArtistsAPI': None,
        'FacebookRightsAPI': None,
        'TwitterAPIv2': None,
        'DMCAServicesAPI': None
    }

# Export available components
PlatformCoordinator = _AIOHTTP_COMPONENTS.get('PlatformCoordinator')
PlatformOAuthManager = _AIOHTTP_COMPONENTS.get('PlatformOAuthManager')
YouTubeContentIDAPI = _AIOHTTP_COMPONENTS.get('YouTubeContentIDAPI')
InstagramBusinessAPI = _AIOHTTP_COMPONENTS.get('InstagramBusinessAPI')
TikTokCreatorAPI = _AIOHTTP_COMPONENTS.get('TikTokCreatorAPI')
SpotifyArtistsAPI = _AIOHTTP_COMPONENTS.get('SpotifyArtistsAPI')
FacebookRightsAPI = _AIOHTTP_COMPONENTS.get('FacebookRightsAPI')
TwitterAPIv2 = _AIOHTTP_COMPONENTS.get('TwitterAPIv2')
DMCAServicesAPI = _AIOHTTP_COMPONENTS.get('DMCAServicesAPI')

# Build __all__ list with available components
__all__ = []

if APIRateLimiter is not None:
    __all__.append("APIRateLimiter")

for component_name, component_class in _AIOHTTP_COMPONENTS.items():
    if component_class is not None:
        __all__.append(component_name)

# Add utility functions and constants
__all__.extend([
    "is_aiohttp_available",
    "get_available_components",
    "get_missing_dependencies"
])

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

def is_aiohttp_available() -> bool:
    """Check if aiohttp dependency is available."""
    return _AIOHTTP_AVAILABLE

def get_available_components() -> dict:
    """Get list of available platform integration components."""
    available = {}
    
    if APIRateLimiter is not None:
        available['APIRateLimiter'] = APIRateLimiter
    
    for name, component in _AIOHTTP_COMPONENTS.items():
        if component is not None:
            available[name] = component
    
    return available

def get_missing_dependencies() -> list:
    """Get list of missing dependencies that prevent full functionality."""
    missing = []
    
    if not _AIOHTTP_AVAILABLE:
        missing.append("aiohttp")
    
    if not _API_RATE_LIMITER_AVAILABLE:
        missing.append("api_rate_limiter module")
    
    return missing