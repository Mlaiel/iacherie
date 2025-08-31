"""IA Influencer Agent - Services Layer
Professional-grade services orchestrating business logic and AI processing
Author: Fahed Mlaiel <mlaiel@live.de>

Team Specialities:
- Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps Expert
- Database Administrator + Security Expert + Microservices Architect
- IA Prompt Engineer + MLOps Engineer

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are proprietary to Fahed Mlaiel (mlaiel@live.de).
Unauthorized copying, distribution, modification or use without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .content_ingestion import ContentIngestionService

from .analytics import AnalyticsService

from .collaboration_matching import CollaborationMatchingService

from .distribution import DistributionService

from .monetization import MonetizationService

from .rights_protection import RightsProtectionService

from .seo_optimizer import SEOOptimizerService

from .audio_fingerprint_engine import AudioFingerprintEngine

from .video_fingerprint_engine import VideoFingerprintEngine

from .image_fingerprint_engine import ImageFingerprintEngine

from .text_fingerprint_engine import TextFingerprintEngine

__all__ = [
    "ContentIngestionService",
    "AnalyticsService",
    "CollaborationMatchingService",
    "DistributionService", 
    "MonetizationService",
    "RightsProtectionService",
    "SEOOptimizerService",
    "AudioFingerprintEngine",
    "VideoFingerprintEngine", 
    "ImageFingerprintEngine",
    "TextFingerprintEngine",
]
