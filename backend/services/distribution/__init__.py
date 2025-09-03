"""Multi-Platform Distribution Service
=====================================

Service for managing content distribution across multiple platforms
with intelligent scheduling, optimization, and cross-posting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .platforms import (
    youtube_api,
    instagram_api,
    tiktok_api,
    spotify_api,
    soundcloud_api
)

from .scheduler import (
    post_scheduler,
    cross_posting
)

from .optimizer import (
    format_adapter,
    timing_optimizer
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "youtube_api",
    "instagram_api", 
    "tiktok_api",
    "spotify_api",
    "soundcloud_api",
    "post_scheduler",
    "cross_posting",
    "format_adapter",
    "timing_optimizer"
]