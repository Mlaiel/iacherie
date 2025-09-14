"""
API Gateway Index - Enterprise API Gateway Entry Point
© 2025 Fahed Mlaiel. All rights reserved.

Central entry point for Ainflue API Gateway providing unified access to
REST, GraphQL, WebSocket APIs with enterprise-grade features.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure Enterprise
Version: 1.0 Production
"""

from typing import Dict, List, Optional, Any

# Core API Gateway components
from .api_gateway import APIGateway, APIGatewayMode, LoadBalancingStrategy
from .rest_api import RESTAPIManager, APIEndpoint, HTTPMethod, APIEndpointType
from .rate_limiter import RateLimiter, RateLimitAlgorithm, RateLimitScope

# Configuration for Ainflue creator platform
AINFLUE_API_GATEWAY_CONFIG = {
    # Core gateway settings
    'gateway_mode': APIGatewayMode.PRODUCTION,
    'enable_cors': True,
    'enable_compression': True,
    'enable_caching': True,
    'max_request_size_mb': 100,  # 100MB for creator content
    'request_timeout_seconds': 60,
    'load_balancing_strategy': LoadBalancingStrategy.HEALTH_BASED,
    
    # Creator platform specific settings
    'creator_workflow_apis': {
        'content_upload_api': {
            'max_file_size_mb': 500,
            'allowed_formats': ['mp3', 'wav', 'mp4', 'avi', 'jpg', 'png', 'pdf'],
            'rate_limit_per_minute': 10,
            'ai_processing_queue_limit': 50
        },
        'ai_processing_api': {
            'concurrent_jobs_limit': 100,
            'rate_limit_per_minute': 20,
            'supported_ai_agents': 53,
            'supported_languages': 644
        },
        'platform_distribution_api': {
            'max_platforms_per_request': 10,
            'rate_limit_per_minute': 30,
            'supported_platforms': 65,
            'scheduling_buffer_hours': 24
        }
    },
    
    # Rate limiting configuration
    'rate_limiting': {
        'algorithm': RateLimitAlgorithm.TOKEN_BUCKET,
        'creator_tier_limit': 1000,  # requests per minute
        'premium_tier_limit': 5000,
        'enterprise_tier_limit': 10000,
        'platform_integration_limit': 50000,
        'burst_protection': True,
        'violation_tracking': True
    },
    
    # Authentication and security
    'authentication': {
        'jwt_enabled': True,
        'api_key_enabled': True,
        'oauth2_enabled': True,
        'multi_factor_required': True,
        'session_timeout_hours': 1,
        'token_refresh_threshold_minutes': 5
    },
    
    # Monitoring and analytics
    'monitoring': {
        'metrics_collection': True,
        'request_logging': True,
        'performance_tracking': True,
        'error_tracking': True,
        'compliance_monitoring': True
    }
}

# Exports
__all__ = [
    'APIGateway',
    'RESTAPIManager',
    'RateLimiter',
    'APIGatewayMode',
    'LoadBalancingStrategy',
    'APIEndpoint',
    'HTTPMethod',
    'APIEndpointType',
    'RateLimitAlgorithm',
    'RateLimitScope',
    'AINFLUE_API_GATEWAY_CONFIG'
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise API Gateway for Ainflue Creator Platform"

# Ainflue business logic integration
CREATOR_WORKFLOW_MAPPING = {
    'upload_content': {
        'endpoint': '/api/v1/creators/content/upload',
        'method': 'POST',
        'rate_limit': 'creator_content_upload',
        'ai_processing_trigger': True,
        'platform_distribution_eligible': True
    },
    'process_ai': {
        'endpoint': '/api/v1/ai/process',
        'method': 'POST', 
        'rate_limit': 'ai_processing_requests',
        'ai_agents_available': 53,
        'language_support': 644
    },
    'distribute_content': {
        'endpoint': '/api/v1/creators/distribute',
        'method': 'POST',
        'rate_limit': 'platform_distribution',
        'max_platforms': 65,
        'scheduling_enabled': True
    },
    'analyze_performance': {
        'endpoint': '/api/v1/analytics/performance',
        'method': 'GET',
        'rate_limit': 'analytics_queries',
        'real_time_data': True,
        'multi_platform_aggregation': True
    },
    'manage_monetization': {
        'endpoint': '/api/v1/monetization',
        'method': 'GET',
        'rate_limit': 'analytics_queries',
        'revenue_transparency': True,
        'tax_compliance': True
    }
}

def get_default_api_gateway() -> APIGateway:
    """Get default configured API gateway for Ainflue platform"""
    gateway = APIGateway()
    
    # Apply Ainflue-specific configuration
    gateway.gateway_config.update({
        'mode': AINFLUE_API_GATEWAY_CONFIG['gateway_mode'],
        'enable_cors': AINFLUE_API_GATEWAY_CONFIG['enable_cors'],
        'enable_compression': AINFLUE_API_GATEWAY_CONFIG['enable_compression'],
        'enable_caching': AINFLUE_API_GATEWAY_CONFIG['enable_caching'],
        'max_request_size': AINFLUE_API_GATEWAY_CONFIG['max_request_size_mb'] * 1024 * 1024,
        'request_timeout': AINFLUE_API_GATEWAY_CONFIG['request_timeout_seconds'],
        'load_balancing_strategy': AINFLUE_API_GATEWAY_CONFIG['load_balancing_strategy']
    })
    
    return gateway

def get_creator_workflow_endpoints() -> List[APIEndpoint]:
    """Get creator workflow API endpoints"""
    endpoints = []
    
    for workflow, config in CREATOR_WORKFLOW_MAPPING.items():
        endpoint = APIEndpoint(
            endpoint_id=f"creator_{workflow}",
            path=config['endpoint'],
            method=HTTPMethod(config['method']),
            endpoint_type=APIEndpointType.CREATOR_WORKFLOW,
            description=f"Creator workflow: {workflow}",
            version='v1',
            authentication_required=True,
            rate_limit_tier='creator_tier',
            request_schema=None,  # Would be defined based on workflow
            response_schema=None,  # Would be defined based on workflow
            creator_specific=True,
            platform_specific=config.get('platform_distribution_eligible', False)
        )
        endpoints.append(endpoint)
    
    return endpoints

def get_platform_integration_endpoints() -> List[APIEndpoint]:
    """Get platform integration API endpoints for 65+ platforms"""
    platforms = [
        # Social Media (29 platforms)
        'instagram', 'tiktok', 'youtube', 'facebook', 'twitter', 'linkedin', 
        'snapchat', 'pinterest', 'threads', 'bereal', 'mastodon', 'bluesky',
        'nostr', 'weibo', 'line', 'kakaotalk', 'vk', 'qq', 'wechat',
        'telegram', 'whatsapp_business', 'discord', 'reddit', 'clubhouse',
        'twitch', 'kick', 'vimeo', 'dailymotion', 'rumble',
        
        # Music Streaming (20 platforms)
        'spotify', 'apple_music', 'youtube_music', 'amazon_music', 'deezer',
        'tidal', 'pandora', 'iheartradio', 'soundcloud', 'bandcamp',
        'audiomack', 'mixcloud', 'spotify_podcasts', 'apple_podcasts',
        'google_podcasts', 'anchor', 'distrokid', 'cd_baby', 'tunecore', 'landr',
        
        # Creator Economy (16 platforms)
        'onlyfans', 'patreon', 'kofi', 'buymeacoffee', 'gumroad', 'etsy',
        'opensea', 'foundation', 'superrare', 'async_art', 'knownorigin',
        'onlyfans_live', 'cam4', 'chaturbate', 'fiverr', 'upwork'
    ]
    
    endpoints = []
    
    for platform in platforms:
        # OAuth callback endpoint
        oauth_endpoint = APIEndpoint(
            endpoint_id=f"platform_oauth_{platform}",
            path=f"/api/v1/platforms/{platform}/oauth/callback",
            method=HTTPMethod.POST,
            endpoint_type=APIEndpointType.PLATFORM_INTEGRATION,
            description=f"OAuth callback for {platform}",
            version='v1',
            authentication_required=False,
            rate_limit_tier='platform_integration',
            request_schema=None,
            response_schema=None,
            creator_specific=False,
            platform_specific=True
        )
        endpoints.append(oauth_endpoint)
        
        # Platform sync status endpoint
        sync_endpoint = APIEndpoint(
            endpoint_id=f"platform_sync_{platform}",
            path=f"/api/v1/platforms/{platform}/sync/status",
            method=HTTPMethod.GET,
            endpoint_type=APIEndpointType.PLATFORM_INTEGRATION,
            description=f"Sync status for {platform}",
            version='v1',
            authentication_required=True,
            rate_limit_tier='platform_integration',
            request_schema=None,
            response_schema=None,
            creator_specific=True,
            platform_specific=True
        )
        endpoints.append(sync_endpoint)
    
    return endpoints

def get_ai_processing_endpoints() -> List[APIEndpoint]:
    """Get AI processing API endpoints for 53 AI agents"""
    
    ai_agents = [
        'content_enhancer', 'seo_optimizer', 'translation_engine', 'sentiment_analyzer',
        'thumbnail_generator', 'audio_enhancer', 'video_stabilizer', 'color_corrector',
        'noise_reducer', 'voice_synthesizer', 'music_generator', 'lyrics_writer',
        'hashtag_optimizer', 'title_generator', 'description_writer', 'transcriber',
        'subtitle_generator', 'face_detector', 'object_recognizer', 'scene_classifier',
        'emotion_detector', 'age_estimator', 'gender_classifier', 'brand_detector',
        'logo_recognizer', 'text_extractor', 'qr_code_reader', 'barcode_scanner',
        'watermark_detector', 'duplicate_finder', 'similarity_matcher', 'content_classifier',
        'spam_detector', 'toxicity_analyzer', 'copyright_checker', 'plagiarism_detector',
        'trend_analyzer', 'engagement_predictor', 'virality_scorer', 'monetization_optimizer',
        'audience_analyzer', 'demographic_classifier', 'interest_predictor', 'behavior_analyzer',
        'conversion_optimizer', 'retention_predictor', 'churn_analyzer', 'growth_forecaster',
        'performance_optimizer', 'quality_assessor', 'compliance_checker', 'risk_analyzer',
        'recommendation_engine'
    ]
    
    endpoints = []
    
    for agent in ai_agents:
        endpoint = APIEndpoint(
            endpoint_id=f"ai_agent_{agent}",
            path=f"/api/v1/ai/agents/{agent}/process",
            method=HTTPMethod.POST,
            endpoint_type=APIEndpointType.AI_PROCESSING,
            description=f"AI processing with {agent} agent",
            version='v1',
            authentication_required=True,
            rate_limit_tier='premium_tier',
            request_schema=None,
            response_schema=None,
            creator_specific=True,
            platform_specific=False
        )
        endpoints.append(endpoint)
    
    return endpoints

# Initialize default configuration
DEFAULT_GATEWAY = None

def initialize_default_gateway() -> None:
    """Initialize default gateway instance"""
    global DEFAULT_GATEWAY
    if DEFAULT_GATEWAY is None:
        DEFAULT_GATEWAY = get_default_api_gateway()

# Auto-initialize on import
initialize_default_gateway()