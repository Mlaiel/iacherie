"""
Ainflue Infrastructure Docker Module

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Infrastructure Docker module initialization for Ainflue platform.
Provides Docker Compose orchestration for audio processing, rights protection,
monetization, and analytics services according to business logic requirements.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Infrastructure services configuration
INFRASTRUCTURE_SERVICES = {
    "audio": {
        "compose_file": "docker-compose.audio.yml",
        "description": "Audio processing infrastructure with DEMUCS separation and EBU R128 normalization",
        "required_for": ["MUSICIAN", "COMEDIAN"]
    },
    "protection": {
        "compose_file": "docker-compose.protection.yml", 
        "description": "Rights protection infrastructure with fingerprinting and watermarking",
        "required_for": ["MUSICIAN", "PHOTOGRAPHER", "COMEDIAN"]
    },
    "monetization": {
        "compose_file": "docker-compose.monetization.yml",
        "description": "Monetization infrastructure with payment processing and licensing",
        "required_for": ["MUSICIAN", "PHOTOGRAPHER", "BLOGGER", "INFLUENCER", "COMEDIAN"]
    },
    "analytics": {
        "compose_file": "docker-compose.analytics.yml",
        "description": "SEO and analytics infrastructure with trending monitoring",
        "required_for": ["PHOTOGRAPHER", "BLOGGER", "INFLUENCER"]
    }
}

# Business logic stages mapping
BUSINESS_LOGIC_STAGES = {
    1: "upload_processing",
    2: "ai_processing", 
    3: "protection_rights",
    4: "seo_optimization",
    5: "collaboration_matching",
    6: "monetization",
    7: "distribution",
    8: "analytics"
}

# Creator type infrastructure requirements
CREATOR_INFRASTRUCTURE = {
    "MUSICIAN": ["audio", "protection", "monetization"],
    "PHOTOGRAPHER": ["protection", "analytics", "monetization"],
    "BLOGGER": ["analytics", "monetization"],
    "INFLUENCER": ["analytics", "monetization"],
    "COMEDIAN": ["audio", "protection", "monetization"]
}