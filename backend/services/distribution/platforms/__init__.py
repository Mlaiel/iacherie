"""Platform API Integrations
===========================

Platform-specific API integrations for content distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from . import youtube_api
from . import instagram_api
from . import tiktok_api
from . import spotify_api
from . import soundcloud_api

__all__ = [
    "youtube_api",
    "instagram_api",
    "tiktok_api", 
    "spotify_api",
    "soundcloud_api"
]