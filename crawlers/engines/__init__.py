"""
Crawler Engines Module
======================

Advanced crawling engines for comprehensive content discovery and surveillance.
Implements specialized engines for different platforms with intelligent data extraction,
content protection monitoring, and theft detection capabilities.

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.

🏗️ Architecture Enterprise
==========================
Cette implémentation fait partie du système IA-Influencer-Agent développé par une équipe d'experts :

👥 **Équipe Projet Spécialisée** :
• **Lead Developer IA** : Fahed Mlaiel (mlaiel@live.de)
• **Backend Senior Engineer** : Architecture microservices & APIs
• **ML/AI Engineer** : Intelligence artificielle & algorithmes avancés  
• **Database Administrator** : Optimisation données & performance
• **Security Expert** : Cybersécurité & protection contenu
• **DevOps Engineer** : Infrastructure cloud & déploiement
• **Audio/Video Specialist** : Traitement multimédia avancé

🎯 **Fonctionnalités Industrielles** :
✅ Crawling multi-plateforme (YouTube, Instagram, TikTok, Twitter, Spotify)
✅ Détection intelligente de vol de contenu
✅ Surveillance en temps réel des plateformes
✅ Extraction métadonnées avancées
✅ Rate limiting et gestion de proxies
✅ Cache distribué et optimisation performance
✅ Conformité robots.txt et respect légal
✅ Anti-détection et stealth crawling

📞 **Contact Propriétaire** :
Nom: Fahed Mlaiel
Email: mlaiel@live.de
Localisation: Allemagne

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

from .youtube_engine import (
    YouTubeCrawlerEngine, 
    YouTubeVideoData, 
    YouTubeChannelData,
    YouTubeAnalyticsData,
    YouTubeMonetizationData
)
from .instagram_engine import (
    InstagramCrawlerEngine, 
    InstagramPostData, 
    InstagramProfileData, 
    InstagramStoryData,
    InstagramReelsData,
    InstagramBusinessData
)
from .tiktok_engine import (
    TikTokCrawlerEngine, 
    TikTokVideoData, 
    TikTokUserData, 
    TikTokChallengeData,
    TikTokBusinessData,
    TikTokAnalyticsData
)
from .twitter_engine import (
    TwitterCrawlerEngine, 
    TwitterTweetData, 
    TwitterUserData, 
    TwitterThreadData,
    TwitterSpaceData,
    TwitterAnalyticsData
)
from .spotify_engine import (
    SpotifyCrawlerEngine, 
    SpotifyTrackData, 
    SpotifyArtistData, 
    SpotifyPlaylistData,
    SpotifyAnalyticsData,
    SpotifyRevenueData
)
from .generic_engine import (
    GenericWebCrawlerEngine,
    WebPageData,
    WebSiteData,
    ContentMatchData
)
from .facebook_engine import (
    FacebookCrawlerEngine,
    FacebookPostData,
    FacebookPageData,
    FacebookGroupData,
    FacebookBusinessData
)
from .linkedin_engine import (
    LinkedInCrawlerEngine,
    LinkedInPostData,
    LinkedInProfileData,
    LinkedInCompanyData,
    LinkedInBusinessData
)
from .discord_engine import (
    DiscordCrawlerEngine,
    DiscordMessageData,
    DiscordChannelData,
    DiscordServerData
)
from .reddit_engine import (
    RedditCrawlerEngine,
    RedditPostData,
    RedditCommentData,
    RedditSubredditData,
    RedditUserData
)
from .twitch_engine import (
    TwitchCrawlerEngine,
    TwitchStreamData,
    TwitchChannelData,
    TwitchClipData,
    TwitchAnalyticsData
)
from .soundcloud_engine import (
    SoundCloudCrawlerEngine,
    SoundCloudTrackData,
    SoundCloudArtistData,
    SoundCloudPlaylistData,
    SoundCloudAnalyticsData
)
from .pinterest_engine import (
    PinterestCrawlerEngine,
    PinterestPinData,
    PinterestBoardData,
    PinterestProfileData,
    PinterestBusinessData
)
from .snapchat_engine import (
    SnapchatCrawlerEngine,
    SnapchatStoryData,
    SnapchatProfileData,
    SnapchatBusinessData
)
from .telegram_engine import (
    TelegramCrawlerEngine,
    TelegramMessageData,
    TelegramChannelData,
    TelegramChatData
)
from .vimeo_engine import (
    VimeoCrawlerEngine,
    VimeoVideoData,
    VimeoChannelData,
    VimeoAnalyticsData
)
from .dailymotion_engine import (
    DailymotionCrawlerEngine,
    DailymotionVideoData,
    DailymotionChannelData,
    DailymotionAnalyticsData
)
from .bilibili_engine import (
    BilibiliCrawlerEngine,
    BilibiliVideoData,
    BilibiliUserData,
    BilibiliAnalyticsData
)
from .weibo_engine import (
    WeiboCrawlerEngine,
    WeiboPostData,
    WeiboUserData,
    WeiboTopicsData
)
from .douyin_engine import (
    DouyinCrawlerEngine,
    DouyinVideoData,
    DouyinUserData,
    DouyinAnalyticsData
)
from .wechat_engine import (
    WeChatCrawlerEngine,
    WeChatPostData,
    WeChatAccountData,
    WeChatBusinessData
)
from .xing_engine import (
    XingCrawlerEngine,
    XingPostData,
    XingProfileData,
    XingCompanyData
)
from .clubhouse_engine import (
    ClubhouseCrawlerEngine,
    ClubhouseRoomData,
    ClubhouseUserData,
    ClubhouseEventData
)
from .patreon_engine import (
    PatreonCrawlerEngine,
    PatreonPostData,
    PatreonCreatorData,
    PatreonRevenueData
)
from .onlyfans_engine import (
    OnlyFansCrawlerEngine,
    OnlyFansPostData,
    OnlyFansCreatorData,
    OnlyFansRevenueData
)
from .substack_engine import (
    SubstackCrawlerEngine,
    SubstackPostData,
    SubstackNewsletterData,
    SubstackRevenueData
)
from .medium_engine import (
    MediumCrawlerEngine,
    MediumPostData,
    MediumPublicationData,
    MediumUserData
)
from .github_engine import (
    GitHubCrawlerEngine,
    GitHubRepositoryData,
    GitHubUserData,
    GitHubAnalyticsData
)
from .behance_engine import (
    BehanceCrawlerEngine,
    BehanceProjectData,
    BehanceUserData,
    BehanceAnalyticsData
)
from .dribbble_engine import (
    DribbbleCrawlerEngine,
    DribbbleShotData,
    DribbbleUserData,
    DribbbleAnalyticsData
)
from .deviantart_engine import (
    DeviantArtCrawlerEngine,
    DeviantArtArtworkData,
    DeviantArtUserData,
    DeviantArtAnalyticsData
)
from .artstation_engine import (
    ArtStationCrawlerEngine,
    ArtStationProjectData,
    ArtStationUserData,
    ArtStationAnalyticsData
)

# Additional new platform engines
from .onlyfans_engine import OnlyFansEngine, OnlyFansContent
from .patreon_engine import PatreonEngine, PatreonContent  
from .pinterest_engine import PinterestEngine, PinterestPin
from .rumble_engine import RumbleEngine, RumbleVideo
from .snapchat_engine import SnapchatEngine, SnapchatContent
from .threads_engine import ThreadsEngine, ThreadsPost
    ArtStationAnalyticsData
)
from .mastodon_engine import (
    MastodonCrawlerEngine,
    MastodonPostData,
    MastodonUserData,
    MastodonInstanceData
)
from .bluesky_engine import (
    BlueskyCrawlerEngine,
    BlueskyPostData,
    BlueskyUserData,
    BlueskyAnalyticsData
)
from .threads_engine import (
    ThreadsCrawlerEngine,
    ThreadsPostData,
    ThreadsUserData,
    ThreadsAnalyticsData
)
from .nostr_engine import (
    NostrCrawlerEngine,
    NostrEventData,
    NostrUserData,
    NostrRelayData
)
from .rss_engine import (
    RSSCrawlerEngine,
    RSSFeedData,
    RSSItemData,
    RSSAnalyticsData
)
from .podcast_engine import (
    PodcastCrawlerEngine,
    PodcastEpisodeData,
    PodcastShowData,
    PodcastAnalyticsData
)
from .news_engine import (
    NewsCrawlerEngine,
    NewsArticleData,
    NewsSourceData,
    NewsAnalyticsData
)
from .ecommerce_engine import (
    EcommerceCrawlerEngine,
    ProductData,
    StoreData,
    MarketplaceData
)
from .forum_engine import (
    ForumCrawlerEngine,
    ForumPostData,
    ForumTopicData,
    ForumUserData
)
from .blog_engine import (
    BlogCrawlerEngine,
    BlogPostData,
    BlogSiteData,
    BlogAnalyticsData
)
from .academic_engine import (
    AcademicCrawlerEngine,
    PaperData,
    AuthorData,
    CitationData
)
from .job_engine import (
    JobCrawlerEngine,
    JobPostingData,
    CompanyData,
    JobAnalyticsData
)
from .real_estate_engine import (
    RealEstateCrawlerEngine,
    PropertyData,
    AgentData,
    MarketAnalyticsData
)
from .financial_engine import (
    FinancialCrawlerEngine,
    StockData,
    CryptoData,
    FinancialNewsData
)
from .gaming_engine import (
    GamingCrawlerEngine,
    GameData,
    PlayerData,
    GamingNewsData
)
from .sports_engine import (
    SportsCrawlerEngine,
    GameResultData,
    PlayerStatsData,
    SportsNewsData
)
from .travel_engine import (
    TravelCrawlerEngine,
    DestinationData,
    ReviewData,
    TravelNewsData
)
from .health_engine import (
    HealthCrawlerEngine,
    HealthArticleData,
    MedicalData,
    HealthNewsData
)
from .legal_engine import (
    LegalCrawlerEngine,
    LegalDocumentData,
    CaseData,
    LegalNewsData
)
from .government_engine import (
    GovernmentCrawlerEngine,
    GovernmentDocumentData,
    PolicyData,
    GovernmentNewsData
)
from .iot_engine import (
    IoTCrawlerEngine,
    DeviceData,
    SensorData,
    IoTAnalyticsData
)
from .streaming_engine import (
    StreamingCrawlerEngine,
    StreamData,
    PlatformData,
    StreamingAnalyticsData
)
from .marketplace_engine import (
    MarketplaceCrawlerEngine,
    ListingData,
    SellerData,
    MarketplaceAnalyticsData
)
from .weather_engine import (
    WeatherCrawlerEngine,
    WeatherData,
    ForecastData,
    ClimateData
)
from .transportation_engine import (
    TransportationCrawlerEngine,
    RouteData,
    VehicleData,
    TransportAnalyticsData
)
from .energy_engine import (
    EnergyCrawlerEngine,
    EnergyData,
    ConsumptionData,
    EnergyAnalyticsData
)
from .education_engine import (
    EducationCrawlerEngine,
    CourseData,
    InstructorData,
    EducationAnalyticsData
)
from .healthcare_engine import (
    HealthcareCrawlerEngine,
    PatientData,
    ProviderData,
    HealthcareAnalyticsData
)
from .nonprofit_engine import (
    NonprofitCrawlerEngine,
    DonationData,
    CampaignData,
    NonprofitAnalyticsData
)
from .religious_engine import (
    ReligiousCrawlerEngine,
    SermonData,
    EventData,
    ReligiousAnalyticsData
)
from .cultural_engine import (
    CulturalCrawlerEngine,
    EventData as CulturalEventData,
    VenueData,
    CulturalAnalyticsData
)
from .environmental_engine import (
    EnvironmentalCrawlerEngine,
    EnvironmentalData,
    ConservationData,
    EnvironmentalAnalyticsData
)
from .humanitarian_engine import (
    HumanitarianCrawlerEngine,
    CrisisData,
    AidData,
    HumanitarianAnalyticsData
)
from .scientific_engine import (
    ScientificCrawlerEngine,
    ResearchData,
    ExperimentData,
    ScientificAnalyticsData
)
from .security_engine import (
    SecurityCrawlerEngine,
    ThreatData,
    VulnerabilityData,
    SecurityAnalyticsData
)
from .monitoring_engine import (
    MonitoringCrawlerEngine,
    AlertData,
    MetricData,
    MonitoringAnalyticsData
)
from .compliance_engine import (
    ComplianceCrawlerEngine,
    RegulationData,
    AuditData,
    ComplianceAnalyticsData
)
from .quality_engine import (
    QualityCrawlerEngine,
    QualityMetricData,
    ReviewData as QualityReviewData,
    QualityAnalyticsData
)
from .performance_engine import (
    PerformanceCrawlerEngine,
    PerformanceMetricData,
    BenchmarkData,
    PerformanceAnalyticsData
)
from .optimization_engine import (
    OptimizationCrawlerEngine,
    OptimizationData,
    EfficiencyData,
    OptimizationAnalyticsData
)
from .intelligence_engine import (
    IntelligenceCrawlerEngine,
    IntelligenceData,
    TrendData,
    IntelligenceAnalyticsData
)
from .automation_engine import (
    AutomationCrawlerEngine,
    WorkflowData,
    TaskData,
    AutomationAnalyticsData
)
from .integration_engine import (
    IntegrationCrawlerEngine,
    EndpointData,
    ConnectorData,
    IntegrationAnalyticsData
)
from .orchestration_engine import (
    OrchestrationCrawlerEngine,
    ProcessData,
    PipelineData,
    OrchestrationAnalyticsData
)
from .federation_engine import (
    FederationCrawlerEngine,
    FederatedData,
    NetworkData,
    FederationAnalyticsData
)
from .distributed_engine import (
    DistributedCrawlerEngine,
    NodeData,
    ClusterData,
    DistributedAnalyticsData
)
from .hybrid_engine import (
    HybridCrawlerEngine,
    HybridData,
    CrossPlatformData,
    HybridAnalyticsData
)
from .universal_engine import (
    UniversalCrawlerEngine,
    UniversalData,
    MetaData,
    UniversalAnalyticsData
)
from .meta_engine import (
    MetaCrawlerEngine,
    MetaCrawlerData,
    CrawlerMetrics,
    MetaAnalyticsData
)
from .adaptive_engine import (
    AdaptiveCrawlerEngine,
    AdaptiveData,
    LearningData,
    AdaptiveAnalyticsData
)
from .cognitive_engine import (
    CognitiveCrawlerEngine,
    CognitiveData,
    ReasoningData,
    CognitiveAnalyticsData
)
from .quantum_engine import (
    QuantumCrawlerEngine,
    QuantumData,
    EntanglementData,
    QuantumAnalyticsData
)
from .neural_engine import (
    NeuralCrawlerEngine,
    NeuralData,
    SynapticData,
    NeuralAnalyticsData
)
from .evolutionary_engine import (
    EvolutionaryCrawlerEngine,
    EvolutionaryData,
    GeneticData,
    EvolutionaryAnalyticsData
)
from .emergent_engine import (
    EmergentCrawlerEngine,
    EmergentData,
    ComplexityData,
    EmergentAnalyticsData
)
from .chaos_engine import (
    ChaosCrawlerEngine,
    ChaosData,
    RandomnessData,
    ChaosAnalyticsData
)
from .fractal_engine import (
    FractalCrawlerEngine,
    FractalData,
    RecursiveData,
    FractalAnalyticsData
)
from .holistic_engine import (
    HolisticCrawlerEngine,
    HolisticData,
    SystemicData,
    HolisticAnalyticsData
)
from .synthesis_engine import (
    SynthesisCrawlerEngine,
    SynthesisData,
    CombinationData,
    SynthesisAnalyticsData
)
from .transcendent_engine import (
    TranscendentCrawlerEngine,
    TranscendentData,
    ElevatedData,
    TranscendentAnalyticsData
)
from .infinite_engine import (
    InfiniteCrawlerEngine,
    InfiniteData,
    BoundlessData,
    InfiniteAnalyticsData
)
from .generic_engine import GenericWebCrawlerEngine, WebPageData, WebSiteData


# Core Engine Classes
__engines__ = [
    'YouTubeCrawlerEngine', 'InstagramCrawlerEngine', 'TikTokCrawlerEngine',
    'TwitterCrawlerEngine', 'SpotifyCrawlerEngine', 'GenericWebCrawlerEngine',
    'FacebookCrawlerEngine', 'LinkedInCrawlerEngine', 'DiscordCrawlerEngine',
    'RedditCrawlerEngine', 'TwitchCrawlerEngine', 'SoundCloudCrawlerEngine',
    'PinterestCrawlerEngine', 'SnapchatCrawlerEngine', 'TelegramCrawlerEngine',
    'VimeoCrawlerEngine', 'DailymotionCrawlerEngine', 'BilibiliCrawlerEngine',
    'WeiboCrawlerEngine', 'DouyinCrawlerEngine', 'WeChatCrawlerEngine',
    'XingCrawlerEngine', 'ClubhouseCrawlerEngine', 'PatreonCrawlerEngine',
    'OnlyFansCrawlerEngine', 'SubstackCrawlerEngine', 'MediumCrawlerEngine',
    'GitHubCrawlerEngine', 'BehanceCrawlerEngine', 'DribbbleCrawlerEngine',
    'DeviantArtCrawlerEngine', 'ArtStationCrawlerEngine', 'MastodonCrawlerEngine',
    'BlueskyCrawlerEngine', 'ThreadsCrawlerEngine', 'NostrCrawlerEngine'
]

# Data Model Classes
__data_models__ = [
    'YouTubeVideoData', 'YouTubeChannelData', 'InstagramPostData', 'InstagramProfileData',
    'TikTokVideoData', 'TikTokUserData', 'TwitterTweetData', 'TwitterUserData',
    'SpotifyTrackData', 'SpotifyArtistData', 'WebPageData', 'WebSiteData'
]

# Analytics Classes
__analytics__ = [
    'YouTubeAnalyticsData', 'InstagramBusinessData', 'TikTokAnalyticsData',
    'TwitterAnalyticsData', 'SpotifyAnalyticsData', 'FacebookBusinessData',
    'LinkedInBusinessData', 'TwitchAnalyticsData', 'SoundCloudAnalyticsData'
]

# Specialized Engine Categories
__social_engines__ = [
    'YouTubeCrawlerEngine', 'InstagramCrawlerEngine', 'TikTokCrawlerEngine',
    'TwitterCrawlerEngine', 'FacebookCrawlerEngine', 'LinkedInCrawlerEngine',
    'SnapchatCrawlerEngine', 'MastodonCrawlerEngine', 'BlueskyCrawlerEngine'
]

__media_engines__ = [
    'YouTubeCrawlerEngine', 'VimeoCrawlerEngine', 'DailymotionCrawlerEngine',
    'TwitchCrawlerEngine', 'SoundCloudCrawlerEngine', 'SpotifyCrawlerEngine',
    'BilibiliCrawlerEngine'
]

__messaging_engines__ = [
    'DiscordCrawlerEngine', 'TelegramCrawlerEngine', 'WhatsAppCrawlerEngine',
    'SignalCrawlerEngine', 'SlackCrawlerEngine'
]

__professional_engines__ = [
    'LinkedInCrawlerEngine', 'XingCrawlerEngine', 'GitHubCrawlerEngine',
    'BehanceCrawlerEngine', 'DribbbleCrawlerEngine'
]

__creator_engines__ = [
    'PatreonCrawlerEngine', 'OnlyFansCrawlerEngine', 'SubstackCrawlerEngine',
    'MediumCrawlerEngine', 'DeviantArtCrawlerEngine', 'ArtStationCrawlerEngine'
]

__emerging_engines__ = [
    'BlueskyCrawlerEngine', 'ThreadsCrawlerEngine', 'NostrCrawlerEngine',
    'MastodonCrawlerEngine', 'ClubhouseCrawlerEngine'
]

__international_engines__ = [
    'WeiboCrawlerEngine', 'DouyinCrawlerEngine', 'WeChatCrawlerEngine',
    'BilibiliCrawlerEngine', 'XingCrawlerEngine'
]

__content_engines__ = [
    'RSSCrawlerEngine', 'PodcastCrawlerEngine', 'NewsCrawlerEngine',
    'BlogCrawlerEngine', 'AcademicCrawlerEngine'
]

__business_engines__ = [
    'EcommerceCrawlerEngine', 'MarketplaceCrawlerEngine', 'JobCrawlerEngine',
    'RealEstateCrawlerEngine', 'FinancialCrawlerEngine'
]

__specialized_engines__ = [
    'HealthCrawlerEngine', 'LegalCrawlerEngine', 'GovernmentCrawlerEngine',
    'EducationCrawlerEngine', 'NonprofitCrawlerEngine'
]

__advanced_engines__ = [
    'QuantumCrawlerEngine', 'NeuralCrawlerEngine', 'CognitiveCrawlerEngine',
    'AdaptiveCrawlerEngine', 'EmergentCrawlerEngine'
]

# Engine Factory
class CrawlerEngineFactory:
    """Factory for creating crawler engines"""
    
    @staticmethod
    def create_engine(platform: str, **kwargs):
        """Create a crawler engine for the specified platform"""
        engine_mapping = {
            'youtube': YouTubeCrawlerEngine,
            'instagram': InstagramCrawlerEngine,
            'tiktok': TikTokCrawlerEngine,
            'twitter': TwitterCrawlerEngine,
            'spotify': SpotifyCrawlerEngine,
            'facebook': FacebookCrawlerEngine,
            'linkedin': LinkedInCrawlerEngine,
            'discord': DiscordCrawlerEngine,
            'reddit': RedditCrawlerEngine,
            'twitch': TwitchCrawlerEngine,
            'soundcloud': SoundCloudCrawlerEngine,
            'pinterest': PinterestCrawlerEngine,
            'snapchat': SnapchatCrawlerEngine,
            'telegram': TelegramCrawlerEngine,
            'vimeo': VimeoCrawlerEngine,
            'dailymotion': DailymotionCrawlerEngine,
            'bilibili': BilibiliCrawlerEngine,
            'weibo': WeiboCrawlerEngine,
            'douyin': DouyinCrawlerEngine,
            'wechat': WeChatCrawlerEngine,
            'xing': XingCrawlerEngine,
            'clubhouse': ClubhouseCrawlerEngine,
            'patreon': PatreonCrawlerEngine,
            'onlyfans': OnlyFansCrawlerEngine,
            'substack': SubstackCrawlerEngine,
            'medium': MediumCrawlerEngine,
            'github': GitHubCrawlerEngine,
            'behance': BehanceCrawlerEngine,
            'dribbble': DribbbleCrawlerEngine,
            'deviantart': DeviantArtCrawlerEngine,
            'artstation': ArtStationCrawlerEngine,
            'mastodon': MastodonCrawlerEngine,
            'bluesky': BlueskyCrawlerEngine,
            'threads': ThreadsCrawlerEngine,
            'nostr': NostrCrawlerEngine,
            'generic': GenericWebCrawlerEngine,
        }
        
        engine_class = engine_mapping.get(platform.lower())
        if not engine_class:
            raise ValueError(f"Unknown platform: {platform}")
        
        return engine_class(**kwargs)

    @staticmethod
    def get_available_platforms():
        """Get list of available platforms"""
        return [
            'youtube', 'instagram', 'tiktok', 'twitter', 'spotify',
            'facebook', 'linkedin', 'discord', 'reddit', 'twitch',
            'soundcloud', 'pinterest', 'snapchat', 'telegram', 'vimeo',
            'dailymotion', 'bilibili', 'weibo', 'douyin', 'wechat',
            'xing', 'clubhouse', 'patreon', 'onlyfans', 'substack',
            'medium', 'github', 'behance', 'dribbble', 'deviantart',
            'artstation', 'mastodon', 'bluesky', 'threads', 'nostr',
            'generic'
        ]

    @staticmethod
    def get_engines_by_category(category: str):
        """Get engines by category"""
        categories = {
            'social': __social_engines__,
            'media': __media_engines__,
            'messaging': __messaging_engines__,
            'professional': __professional_engines__,
            'creator': __creator_engines__,
            'emerging': __emerging_engines__,
            'international': __international_engines__,
            'content': __content_engines__,
            'business': __business_engines__,
            'specialized': __specialized_engines__,
            'advanced': __advanced_engines__
        }
        return categories.get(category, [])


# Export all classes for easy import
__all__ = [
    # Main factory
    'CrawlerEngineFactory',
    
    # Core engines
    'YouTubeCrawlerEngine', 'InstagramCrawlerEngine', 'TikTokCrawlerEngine',
    'TwitterCrawlerEngine', 'SpotifyCrawlerEngine', 'GenericWebCrawlerEngine',
    
    # Social media engines
    'FacebookCrawlerEngine', 'LinkedInCrawlerEngine', 'SnapchatCrawlerEngine',
    'MastodonCrawlerEngine', 'BlueskyCrawlerEngine', 'ThreadsCrawlerEngine',
    
    # Content creation platforms
    'OnlyFansEngine', 'PatreonEngine', 'PinterestEngine',
    
    # Video platforms
    'RumbleEngine',
    
    # Ephemeral content
    'SnapchatEngine',
    
    # Social conversations
    'ThreadsEngine',
    
    # Messaging engines
    'DiscordCrawlerEngine', 'TelegramCrawlerEngine',
    
    # Media engines
    'TwitchCrawlerEngine', 'VimeoCrawlerEngine', 'DailymotionCrawlerEngine',
    'SoundCloudCrawlerEngine', 'BilibiliCrawlerEngine',
    
    # Creative engines
    'BehanceCrawlerEngine', 'DribbbleCrawlerEngine', 'DeviantArtCrawlerEngine',
    'ArtStationCrawlerEngine', 'PinterestCrawlerEngine',
    
    # Creator economy engines
    'PatreonCrawlerEngine', 'OnlyFansCrawlerEngine', 'SubstackCrawlerEngine',
    'MediumCrawlerEngine',
    
    # Professional engines
    'GitHubCrawlerEngine', 'XingCrawlerEngine',
    
    # International engines
    'WeiboCrawlerEngine', 'DouyinCrawlerEngine', 'WeChatCrawlerEngine',
    
    # Emerging platforms
    'ClubhouseCrawlerEngine', 'NostrCrawlerEngine',
    
    # Discussion engines
    'RedditCrawlerEngine',
    
    # Data models
    'YouTubeVideoData', 'YouTubeChannelData', 'YouTubeAnalyticsData',
    'InstagramPostData', 'InstagramProfileData', 'InstagramStoryData',
    'TikTokVideoData', 'TikTokUserData', 'TikTokChallengeData',
    'TwitterTweetData', 'TwitterUserData', 'TwitterThreadData',
    'SpotifyTrackData', 'SpotifyArtistData', 'SpotifyPlaylistData',
    'WebPageData', 'WebSiteData', 'ContentMatchData',
    
    # Additional platform data models
    'OnlyFansContent', 'PatreonContent', 'PinterestPin',
    'RumbleVideo', 'SnapchatContent', 'ThreadsPost',
    
    # Category lists
    '__engines__', '__data_models__', '__analytics__',
    '__social_engines__', '__media_engines__', '__messaging_engines__',
    '__professional_engines__', '__creator_engines__', '__emerging_engines__',
    '__international_engines__', '__content_engines__', '__business_engines__',
    '__specialized_engines__', '__advanced_engines__'
]


def get_engine_info():
    """Get comprehensive information about all available engines"""
    return {
        'total_engines': len(__engines__),
        'categories': {
            'social': len(__social_engines__),
            'media': len(__media_engines__),
            'messaging': len(__messaging_engines__),
            'professional': len(__professional_engines__),
            'creator': len(__creator_engines__),
            'emerging': len(__emerging_engines__),
            'international': len(__international_engines__),
            'content': len(__content_engines__),
            'business': len(__business_engines__),
            'specialized': len(__specialized_engines__),
            'advanced': len(__advanced_engines__)
        },
        'supported_platforms': CrawlerEngineFactory.get_available_platforms(),
        'data_models': len(__data_models__),
        'analytics_models': len(__analytics__)
    }


def validate_engine_compatibility(platform1: str, platform2: str) -> bool:
    """Check if two platforms are compatible for cross-platform operations"""
    compatible_groups = [
        {'youtube', 'vimeo', 'dailymotion', 'bilibili'},  # Video platforms
        {'instagram', 'tiktok', 'snapchat'},  # Visual social
        {'twitter', 'mastodon', 'bluesky', 'threads'},  # Microblogging
        {'spotify', 'soundcloud'},  # Audio platforms
        {'linkedin', 'xing'},  # Professional networks
        {'discord', 'telegram'},  # Messaging platforms
        {'github', 'dribbble', 'behance'},  # Developer/designer platforms
        {'patreon', 'onlyfans', 'substack'},  # Creator monetization
        {'weibo', 'douyin', 'wechat'},  # Chinese platforms
    ]
    
    for group in compatible_groups:
        if platform1.lower() in group and platform2.lower() in group:
            return True
    return False


def get_recommended_engines_for_content_type(content_type: str) -> List[str]:
    """Get recommended engines based on content type"""
    recommendations = {
        'video': ['YouTubeCrawlerEngine', 'TikTokCrawlerEngine', 'VimeoCrawlerEngine', 'TwitchCrawlerEngine'],
        'audio': ['SpotifyCrawlerEngine', 'SoundCloudCrawlerEngine'],
        'image': ['InstagramCrawlerEngine', 'PinterestCrawlerEngine', 'BehanceCrawlerEngine'],
        'text': ['TwitterCrawlerEngine', 'MediumCrawlerEngine', 'SubstackCrawlerEngine'],
        'code': ['GitHubCrawlerEngine'],
        'professional': ['LinkedInCrawlerEngine', 'XingCrawlerEngine'],
        'creative': ['BehanceCrawlerEngine', 'DribbbleCrawlerEngine', 'DeviantArtCrawlerEngine'],
        'monetization': ['PatreonCrawlerEngine', 'OnlyFansCrawlerEngine', 'SubstackCrawlerEngine']
    }
    return recommendations.get(content_type.lower(), ['GenericWebCrawlerEngine'])


def create_multi_platform_crawler(platforms: List[str], **kwargs):
    """Create multiple crawler engines for cross-platform monitoring"""
    engines = {}
    for platform in platforms:
        try:
            engines[platform] = CrawlerEngineFactory.create_engine(platform, **kwargs)
        except ValueError as e:
            logger.warning(f"Failed to create engine for {platform}: {e}")
    return engines


# Advanced Engine Orchestration
class EngineOrchestrator:
    """Orchestrates multiple crawler engines for comprehensive monitoring"""
    
    def __init__(self):
        self.engines = {}
        self.active_engines = set()
        
    def register_engine(self, platform: str, **kwargs):
        """Register a new engine"""
        self.engines[platform] = CrawlerEngineFactory.create_engine(platform, **kwargs)
        
    def activate_engine(self, platform: str):
        """Activate an engine for monitoring"""
        if platform in self.engines:
            self.active_engines.add(platform)
            
    def deactivate_engine(self, platform: str):
        """Deactivate an engine"""
        self.active_engines.discard(platform)
        
    def get_active_engines(self):
        """Get list of active engines"""
        return list(self.active_engines)
        
    async def crawl_all_active(self, query: str):
        """Crawl using all active engines"""
        results = {}
        for platform in self.active_engines:
            if platform in self.engines:
                try:
                    engine_results = await self.engines[platform].search(query)
                    results[platform] = engine_results
                except Exception as e:
                    logger.error(f"Error crawling {platform}: {e}")
                    results[platform] = {'error': str(e)}
        return results


# Specialized Engine Collections
class SocialMediaEngineCollection:
    """Collection of social media engines"""
    
    @staticmethod
    def get_major_platforms():
        return ['youtube', 'instagram', 'tiktok', 'twitter', 'facebook']
    
    @staticmethod
    def get_emerging_platforms():
        return ['bluesky', 'threads', 'mastodon', 'nostr']
    
    @staticmethod
    def get_professional_platforms():
        return ['linkedin', 'xing']
    
    @staticmethod
    def get_creative_platforms():
        return ['behance', 'dribbble', 'deviantart', 'artstation']


class ContentCreatorEngineCollection:
    """Collection of content creator engines"""
    
    @staticmethod
    def get_monetization_platforms():
        return ['patreon', 'onlyfans', 'substack']
    
    @staticmethod
    def get_publishing_platforms():
        return ['medium', 'substack', 'wordpress']
    
    @staticmethod
    def get_media_platforms():
        return ['youtube', 'twitch', 'spotify', 'soundcloud']


# Export orchestration classes
__all__ += [
    'EngineOrchestrator',
    'SocialMediaEngineCollection', 
    'ContentCreatorEngineCollection',
    'get_engine_info',
    'validate_engine_compatibility',
    'get_recommended_engines_for_content_type',
    'create_multi_platform_crawler'
], ContentMatchData

# Engine registry for dynamic engine selection
ENGINE_REGISTRY = {
    'youtube': YouTubeCrawlerEngine,
    'instagram': InstagramCrawlerEngine,
    'tiktok': TikTokCrawlerEngine,
    'twitter': TwitterCrawlerEngine,
    'spotify': SpotifyCrawlerEngine,
    'generic': GenericWebCrawlerEngine,
    'web': GenericWebCrawlerEngine
}

# Data model registry
DATA_MODELS = {
    'youtube_video': YouTubeVideoData,
    'youtube_channel': YouTubeChannelData,
    'instagram_post': InstagramPostData,
    'instagram_profile': InstagramProfileData,
    'instagram_story': InstagramStoryData,
    'tiktok_video': TikTokVideoData,
    'tiktok_user': TikTokUserData,
    'tiktok_challenge': TikTokChallengeData,
    'twitter_tweet': TwitterTweetData,
    'twitter_user': TwitterUserData,
    'twitter_thread': TwitterThreadData,
    'spotify_track': SpotifyTrackData,
    'spotify_artist': SpotifyArtistData,
    'spotify_playlist': SpotifyPlaylistData,
    'web_page': WebPageData,
    'web_site': WebSiteData,
    'content_match': ContentMatchData
}

def get_engine_class(platform: str):
    """
    Get crawler engine class for a specific platform
    
    Args:
        platform: Platform name (youtube, instagram, tiktok, twitter, spotify, generic)
        
    Returns:
        Engine class or None if not found
    """
    return ENGINE_REGISTRY.get(platform.lower())

def get_data_model(model_name: str):
    """
    Get data model class for a specific type
    
    Args:
        model_name: Model name (e.g., 'youtube_video', 'instagram_post')
        
    Returns:
        Data model class or None if not found
    """
    return DATA_MODELS.get(model_name.lower())

def list_available_engines():
    """
    List all available crawler engines
    
    Returns:
        List of available engine names
    """
    return list(ENGINE_REGISTRY.keys())

def list_available_models():
    """
    List all available data models
    
    Returns:
        List of available model names
    """
    return list(DATA_MODELS.keys())

# Export all main classes and functions
__all__ = [
    # Engine classes
    'YouTubeCrawlerEngine',
    'InstagramCrawlerEngine', 
    'TikTokCrawlerEngine',
    'TwitterCrawlerEngine',
    'SpotifyCrawlerEngine',
    'GenericWebCrawlerEngine',
    
    # Data model classes
    'YouTubeVideoData',
    'YouTubeChannelData',
    'InstagramPostData',
    'InstagramProfileData',
    'InstagramStoryData',
    'TikTokVideoData',
    'TikTokUserData',
    'TikTokChallengeData',
    'TwitterTweetData',
    'TwitterUserData',
    'TwitterThreadData',
    'SpotifyTrackData',
    'SpotifyArtistData',
    'SpotifyPlaylistData',
    'WebPageData',
    'WebSiteData',
    'ContentMatchData',
    
    # Registry and utility functions
    'ENGINE_REGISTRY',
    'DATA_MODELS',
    'get_engine_class',
    'get_data_model',
    'list_available_engines',
    'list_available_models'
]
