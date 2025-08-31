"""Bandcamp Agent - Automated Distribution System
==============================================

Professional Bandcamp integration providing comprehensive distribution,
sales management, and fan engagement capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved
"""
from .core.bandcamp_engine import BandcampEngine, BandcampRelease, BandcampTrack
from .core.distribution_manager import DistributionManager
from .utils.bandcamp_auth import BandcampAuthManager

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary - All Rights Reserved"

__all__ = [
    'BandcampEngine',
    'BandcampRelease',
    'BandcampTrack',
    'DistributionManager',
    'BandcampAuthManager'
]

def create_bandcamp_agent(config=None):
    """Factory function to create configured Bandcamp agent"""    return BandcampEngine(config)

def get_module_info():
    """Get module information and capabilities"""    return {
        "name": "Bandcamp Agent",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "capabilities": [
            "Automated Music Distribution",
            "Release Management",
            "Fan Engagement Tracking",
            "Sales Analytics",
            "Pricing Optimization",
            "Merchandise Integration",
            "Direct-to-Fan Marketing",
            "Revenue Maximization"
        ],
        "supported_formats": [
            "Bandcamp URLs",
            "Album & Track Data",
            "Artist Profiles",
            "Fan Data",
            "Audio Files (FLAC, MP3, WAV)"
        ],
        "integrations": [
            "Bandcamp API",
            "Payment Processing",
            "Fan Communication Tools",
            "Analytics Platforms"
        ]
    }