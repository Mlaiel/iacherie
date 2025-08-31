"""
IA Influencer Agent - Configuration de la Pipeline Créateur
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

 AVERTISSEMENT DE PROPRIÉTÉ INTELLECTUELLE 
Ce code et tous les concepts associés sont la propriété exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation écrite 
explicite de l'auteur est strictement interdite et constitue une violation du 
droit d'auteur. Contact: mlaiel@live.de

Configuration centralisée pour tous les composants de la pipeline créateur
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

class CreatorType(Enum):
    """Types de créateurs supportés"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

class ContentType(Enum):
    """Types de contenu supportés"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"

class Platform(Enum):
    """Plateformes supportées"""
    # Musique
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    
    # Vidéo/Social
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    
    # Blogging
    MEDIUM = "medium"
    SUBSTACK = "substack"
    
    # Photographie
    FLICKR = "flickr"
    SHUTTERSTOCK = "shutterstock"
    GETTY = "getty"
    UNSPLASH = "unsplash"

class RevenueStream(Enum):
    """Sources de revenus disponibles"""
    STREAMING = "streaming"
    ADVERTISING = "advertising"
    SPONSORSHIPS = "sponsorships"
    AFFILIATE = "affiliate"
    MERCHANDISE = "merchandise"
    SUBSCRIPTIONS = "subscriptions"
    LICENSING = "licensing"
    LIVE_EVENTS = "live_events"
    COURSES = "courses"
    TIPS = "tips"
    FREELANCE = "freelance"
    STOCK_SALES = "stock_sales"

@dataclass
class PipelineConfig:
    """Configuration principale de la pipeline"""
    
    # Paramètres généraux
    max_concurrent_tasks: int = 10
    timeout_seconds: int = 300
    retry_attempts: int = 3
    enable_metrics: bool = True
    enable_logging: bool = True
    
    # Protection du contenu
    enable_ai_protection: bool = True
    watermark_enabled: bool = True
    copyright_detection: bool = True
    fingerprinting_enabled: bool = True
    
    # Optimisation SEO
    seo_optimization: bool = True
    keyword_analysis: bool = True
    meta_generation: bool = True
    
    # Qualité et transformation
    quality_enhancement: bool = True
    auto_tagging: bool = True
    metadata_enrichment: bool = True

@dataclass
class CreatorConfig:
    """Configuration spécifique par type de créateur"""
    
    # Configuration musicien
    musician: Dict[str, Any] = field(default_factory=lambda: {
        'audio_formats': ['wav', 'mp3', 'flac', 'aac'],
        'quality_levels': ['128kbps', '320kbps', 'lossless'],
        'platforms': [Platform.SPOTIFY, Platform.YOUTUBE_MUSIC, Platform.SOUNDCLOUD],
        'revenue_streams': [RevenueStream.STREAMING, RevenueStream.LICENSING, RevenueStream.LIVE_EVENTS],
        'ai_mastering': True,
        'genre_detection': True,
        'mood_analysis': True,
        'collaboration_matching': True
    })
    
    # Configuration blogueur
    blogger: Dict[str, Any] = field(default_factory=lambda: {
        'content_formats': ['markdown', 'html', 'plain_text'],
        'platforms': [Platform.MEDIUM, Platform.LINKEDIN, Platform.SUBSTACK],
        'revenue_streams': [RevenueStream.AFFILIATE, RevenueStream.SPONSORSHIPS, RevenueStream.COURSES],
        'seo_optimization': True,
        'readability_analysis': True,
        'topic_extraction': True,
        'engagement_prediction': True,
        'auto_excerpts': True
    })
    
    # Configuration photographe
    photographer: Dict[str, Any] = field(default_factory=lambda: {
        'image_formats': ['jpg', 'png', 'tiff', 'raw'],
        'quality_levels': ['web', 'print', '4k', '8k'],
        'platforms': [Platform.INSTAGRAM, Platform.SHUTTERSTOCK, Platform.FLICKR],
        'revenue_streams': [RevenueStream.STOCK_SALES, RevenueStream.LICENSING, RevenueStream.FREELANCE],
        'auto_enhancement': True,
        'style_detection': True,
        'location_tagging': True,
        'portfolio_optimization': True
    })
    
    # Configuration influenceur
    influencer: Dict[str, Any] = field(default_factory=lambda: {
        'content_formats': ['video', 'image', 'text', 'story'],
        'platforms': [Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE],
        'revenue_streams': [RevenueStream.SPONSORSHIPS, RevenueStream.AFFILIATE, RevenueStream.MERCHANDISE],
        'brand_matching': True,
        'engagement_optimization': True,
        'trending_analysis': True,
        'audience_insights': True
    })
    
    # Configuration comédien
    comedian: Dict[str, Any] = field(default_factory=lambda: {
        'content_formats': ['video', 'audio', 'text'],
        'platforms': [Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM],
        'revenue_streams': [RevenueStream.LIVE_EVENTS, RevenueStream.MERCHANDISE, RevenueStream.SUBSCRIPTIONS],
        'humor_analysis': True,
        'timing_optimization': True,
        'audience_reaction': True,
        'viral_potential': True
    })

@dataclass
class PlatformConfig:
    """Configuration des plateformes"""
    
    # Configuration Spotify
    spotify: Dict[str, Any] = field(default_factory=lambda: {
        'api_base_url': 'https://api.spotify.com/v1',
        'upload_formats': ['mp3', 'wav'],
        'max_file_size_mb': 100,
        'metadata_fields': ['title', 'artist', 'album', 'genre', 'duration'],
        'analytics_metrics': ['streams', 'listeners', 'saves', 'shares'],
        'monetization_threshold': 1000  # streams minimum
    })
    
    # Configuration YouTube
    youtube: Dict[str, Any] = field(default_factory=lambda: {
        'api_base_url': 'https://www.googleapis.com/youtube/v3',
        'upload_formats': ['mp4', 'avi', 'mov', 'wmv'],
        'max_file_size_mb': 2048,
        'video_qualities': ['360p', '720p', '1080p', '4k'],
        'monetization_threshold': 1000  # subscribers + 4000 watch hours
    })
    
    # Configuration Instagram
    instagram: Dict[str, Any] = field(default_factory=lambda: {
        'api_base_url': 'https://graph.instagram.com',
        'image_formats': ['jpg', 'png'],
        'video_formats': ['mp4', 'mov'],
        'max_image_size_mb': 30,
        'max_video_size_mb': 100,
        'aspect_ratios': ['1:1', '4:5', '16:9']
    })

@dataclass
class MonetizationConfig:
    """Configuration de la monétisation"""
    
    # Seuils de revenus par créateur
    revenue_thresholds: Dict[str, int] = field(default_factory=lambda: {
        'musician': 1000,      # streams/mois pour débuter
        'blogger': 5000,       # vues/mois pour affiliate
        'photographer': 100,   # téléchargements/mois
        'influencer': 10000,   # followers pour sponsorships
        'comedian': 1000       # vues/vidéo pour monétisation
    })
    
    # Commissions par plateforme (%)
    platform_commissions: Dict[str, float] = field(default_factory=lambda: {
        'spotify': 30.0,
        'youtube': 45.0,
        'instagram': 0.0,  # pas de commission directe
        'shutterstock': 50.0,
        'medium': 0.0,  # modèle partenaire
        'substack': 10.0
    })
    
    # Types d'analyse de monétisation
    analysis_types: List[str] = field(default_factory=lambda: [
        'revenue_prediction',
        'opportunity_identification', 
        'market_analysis',
        'competition_analysis',
        'pricing_optimization',
        'audience_monetization'
    ])

@dataclass
class AIConfig:
    """Configuration des modèles IA"""
    
    # Modèles pour le traitement de contenu
    content_models: Dict[str, str] = field(default_factory=lambda: {
        'text_analysis': 'sentence-transformers/all-MiniLM-L6-v2',
        'image_analysis': 'google/vit-base-patch16-224',
        'audio_analysis': 'facebook/wav2vec2-base-960h',
        'seo_optimization': 'distilbert-base-uncased',
        'sentiment_analysis': 'cardiffnlp/twitter-roberta-base-sentiment'
    })
    
    # Configuration des transformers
    transformers_config: Dict[str, Any] = field(default_factory=lambda: {
        'max_length': 512,
        'batch_size': 32,
        'device': 'auto',  # cuda si disponible, sinon cpu
        'precision': 'fp16'
    })
    
    # Protection par IA
    protection_models: Dict[str, str] = field(default_factory=lambda: {
        'copyright_detection': 'custom/copyright-detector',
        'plagiarism_check': 'custom/plagiarism-detector',
        'content_fingerprinting': 'custom/content-fingerprint'
    })

# Configuration par défaut
DEFAULT_CONFIG = PipelineConfig()
DEFAULT_CREATOR_CONFIG = CreatorConfig()
DEFAULT_PLATFORM_CONFIG = PlatformConfig()
DEFAULT_MONETIZATION_CONFIG = MonetizationConfig()
DEFAULT_AI_CONFIG = AIConfig()

# Variables d'environnement
class EnvironmentConfig:
    """Configuration basée sur les variables d'environnement"""
    
    # Base de données
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/ia_influencer')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # APIs externes
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    
    # Stockage
    STORAGE_BUCKET = os.getenv('STORAGE_BUCKET', 'ia-influencer-content')
    CDN_BASE_URL = os.getenv('CDN_BASE_URL', 'https://cdn.ia-influencer.com')
    
    # Sécurité
    SECRET_KEY = os.getenv('SECRET_KEY', 'development-secret-key')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    # Monitoring
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    METRICS_ENDPOINT = os.getenv('METRICS_ENDPOINT')

# Export de toutes les configurations
__all__ = [
    'CreatorType',
    'ContentType', 
    'Platform',
    'RevenueStream',
    'PipelineConfig',
    'CreatorConfig',
    'PlatformConfig',
    'MonetizationConfig',
    'AIConfig',
    'EnvironmentConfig',
    'DEFAULT_CONFIG',
    'DEFAULT_CREATOR_CONFIG',
    'DEFAULT_PLATFORM_CONFIG',
    'DEFAULT_MONETIZATION_CONFIG',
    'DEFAULT_AI_CONFIG'
]
