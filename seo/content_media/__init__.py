"""Content & Media SEO Package
Specialized SEO optimization for various content types and media formats.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Expertise: Lead Dev IA + Multi-Role Expert Team
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core Media Engines (Existing)
from .audio_seo_engine import AudioSEOEngine
from .video_seo_optimizer import VideoSEOOptimizer

# Creator Specializations (Phase 1 - Completed)
from .musician_seo_engine import MusicianSEOEngine
from .blogger_content_optimizer import BloggerContentOptimizer
from .photographer_seo_engine import PhotographerSEOEngine
from .influencer_content_optimizer import InfluencerContentOptimizer
from .comedian_content_engine import ComedianContentEngine

# Intelligence & Analytics (Phase 2 - Completed)
from .content_intelligence_hub import ContentIntelligenceHub
from .platform_integration_manager import PlatformIntegrationManager
from .content_performance_analytics import ContentPerformanceAnalytics
from .media_asset_optimizer import MediaAssetOptimizer

__all__ = [
    # Core Engines
    "AudioSEOEngine",
    "VideoSEOOptimizer",
    
    # Creator Specializations
    "MusicianSEOEngine",
    "BloggerContentOptimizer", 
    "PhotographerSEOEngine",
    "InfluencerContentOptimizer",
    "ComedianContentEngine",
    
    # Intelligence & Analytics
    "ContentIntelligenceHub",
    "PlatformIntegrationManager",
    "ContentPerformanceAnalytics",
    "MediaAssetOptimizer"
]