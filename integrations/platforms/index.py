"""
Platforms Module - Ainflue Integrations
======================================
Enterprise-grade platform integrations providing comprehensive API
management for 65+ content platforms, creator tools, and distribution
networks with automated publishing and analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Import all platform components
from .api_rate_limiter import *
from .discord_bot_api import *
from .dmca_services_api import *
from .facebook_rights_api import *
from .instagram_business_api import *
from .linkedin_creator_api import *
from .medium_partner_api import *
from .pinterest_business_api import *
from .platform_coordinator import *
from .platform_oauth_manager import *
from .reddit_api import *
from .snapchat_creator_api import *
from .spotify_artists_api import *
from .substack_api import *
from .tiktok_creator_api import *

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise platform integration infrastructure for 65+ content platforms"

# Configuration logique métier Ainflue
AINFLUE_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'platform_apis': 15,
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}