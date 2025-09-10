"""Social Media Integration Module
==================================

Advanced social media analytics, community management, and engagement
optimization for creator monetization and audience growth.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .social_graph_analyzer import SocialGraphAnalyzer

try:
    from .advanced_analytics import AdvancedSocialAnalytics, ViralityScore, InfluencerProfile
except ImportError:
    AdvancedSocialAnalytics = None
    ViralityScore = None
    InfluencerProfile = None

try:
    from .community_manager import CommunityManager, CommunityMember, CommunityEvent
except ImportError:
    CommunityManager = None
    CommunityMember = None
    CommunityEvent = None

try:
    from .content_scheduler import ContentScheduler
except ImportError:
    ContentScheduler = None

try:
    from .engagement_tracker import EngagementTracker
except ImportError:
    EngagementTracker = None

try:
    from .influencer_discovery import InfluencerDiscovery
except ImportError:
    InfluencerDiscovery = None

try:
    from .hashtag_optimizer import HashtagOptimizer
except ImportError:
    HashtagOptimizer = None

try:
    from .trend_analyzer import TrendAnalyzer
except ImportError:
    TrendAnalyzer = None

try:
    from .audience_insights import AudienceInsights
except ImportError:
    AudienceInsights = None

try:
    from .brand_monitoring import BrandMonitoring
except ImportError:
    BrandMonitoring = None

try:
    from .crisis_detection import CrisisDetection
except ImportError:
    CrisisDetection = None

try:
    from .sentiment_analyzer import SentimentAnalyzer
except ImportError:
    SentimentAnalyzer = None

try:
    from .viral_predictor import ViralPredictor
except ImportError:
    ViralPredictor = None

__all__ = [
    'SocialGraphAnalyzer',
    'AdvancedSocialAnalytics',
    'ViralityScore',
    'InfluencerProfile',
    'CommunityManager',
    'CommunityMember',
    'CommunityEvent',
    'ContentScheduler',
    'EngagementTracker',
    'InfluencerDiscovery',
    'HashtagOptimizer',
    'TrendAnalyzer',
    'AudienceInsights',
    'BrandMonitoring',
    'CrisisDetection',
    'SentimentAnalyzer',
    'ViralPredictor'
]

# Social media service registry
SOCIAL_MEDIA_SERVICES = {
    'social_graph': SocialGraphAnalyzer,
}

if AdvancedSocialAnalytics:
    SOCIAL_MEDIA_SERVICES['advanced_analytics'] = AdvancedSocialAnalytics
if CommunityManager:
    SOCIAL_MEDIA_SERVICES['community_manager'] = CommunityManager
if ContentScheduler:
    SOCIAL_MEDIA_SERVICES['content_scheduler'] = ContentScheduler
if EngagementTracker:
    SOCIAL_MEDIA_SERVICES['engagement_tracker'] = EngagementTracker
if InfluencerDiscovery:
    SOCIAL_MEDIA_SERVICES['influencer_discovery'] = InfluencerDiscovery
if HashtagOptimizer:
    SOCIAL_MEDIA_SERVICES['hashtag_optimizer'] = HashtagOptimizer
if TrendAnalyzer:
    SOCIAL_MEDIA_SERVICES['trend_analyzer'] = TrendAnalyzer
if AudienceInsights:
    SOCIAL_MEDIA_SERVICES['audience_insights'] = AudienceInsights
if BrandMonitoring:
    SOCIAL_MEDIA_SERVICES['brand_monitoring'] = BrandMonitoring
if CrisisDetection:
    SOCIAL_MEDIA_SERVICES['crisis_detection'] = CrisisDetection
if SentimentAnalyzer:
    SOCIAL_MEDIA_SERVICES['sentiment_analyzer'] = SentimentAnalyzer
if ViralPredictor:
    SOCIAL_MEDIA_SERVICES['viral_predictor'] = ViralPredictor
