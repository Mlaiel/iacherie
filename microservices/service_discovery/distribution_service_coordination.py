"""
📡 Distribution Service Coordination Enterprise - IA Chérie
========================================================
Coordination distribution multi-plateformes pour créateurs.
Cross-platform publishing + CDN optimization + scheduling.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Service Discovery
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from .distributed_service_registry import ServiceInstance, ServiceStatus
from .multi_region_discovery import MultiRegionDiscovery

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Plateformes de distribution"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    APPLE_PODCASTS = "apple_podcasts"
    CUSTOM_WEBSITE = "custom_website"

class ContentFormat(Enum):
    """Formats de contenu"""
    VIDEO_LONG = "video_long"        # >10 min
    VIDEO_SHORT = "video_short"      # <60s
    AUDIO_PODCAST = "audio_podcast"
    AUDIO_MUSIC = "audio_music"
    IMAGE_POST = "image_post"
    TEXT_POST = "text_post"
    LIVESTREAM = "livestream"
    STORY = "story"

class DistributionPriority(Enum):
    """Priorités de distribution"""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    OPTIMIZED_TIMING = "optimized_timing"
    BATCH_PROCESSING = "batch_processing"

@dataclass
class DistributionRequest:
    """Requête de distribution"""
    request_id: str
    creator_id: str
    content_id: str
    content_format: ContentFormat
    target_platforms: List[Platform]
    priority: DistributionPriority = DistributionPriority.OPTIMIZED_TIMING
    scheduled_time: Optional[datetime] = None
    geographic_targeting: List[str] = field(default_factory=list)
    audience_preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionPlan:
    """Plan de distribution optimisé"""
    platforms: Dict[Platform, Dict[str, Any]]
    optimal_timing: Dict[Platform, datetime]
    content_adaptations: Dict[Platform, Dict[str, Any]]
    cdn_strategy: Dict[str, Any]
    estimated_reach: Dict[Platform, int]
    distribution_cost: float

class DistributionServiceCoordination:
    """
    Coordination distribution multi-plateformes pour créateurs.
    Cross-platform publishing + CDN optimization + scheduling.
    """
    
    def __init__(self):
        self.distribution_services: Dict[str, List[ServiceInstance]] = {}
        self.platform_connectors: Dict[Platform, ServiceInstance] = {}
        self.cdn_services: List[ServiceInstance] = []
        self.multi_region_discovery = MultiRegionDiscovery()
        
        self._initialize_distribution_services()
        
        self.stats = {
            'total_distributions': 0,
            'successful_distributions': 0,
            'platforms_used': {},
            'total_reach': 0,
            'avg_distribution_time': 0.0
        }
        
        logger.info("📡 DistributionServiceCoordination initialisé")
    
    def _initialize_distribution_services(self):
        """Initialiser les services de distribution"""
        # Connecteurs de plateformes
        platforms_config = {
            Platform.YOUTUBE: {"api_endpoint": "youtube.googleapis.com", "port": 443},
            Platform.TIKTOK: {"api_endpoint": "open-api.tiktok.com", "port": 443},
            Platform.INSTAGRAM: {"api_endpoint": "graph.instagram.com", "port": 443},
            Platform.TWITTER: {"api_endpoint": "api.twitter.com", "port": 443},
            Platform.TWITCH: {"api_endpoint": "api.twitch.tv", "port": 443},
            Platform.SPOTIFY: {"api_endpoint": "api.spotify.com", "port": 443}
        }
        
        for platform, config in platforms_config.items():
            connector = ServiceInstance(
                service_id=f"connector_{platform.value}_001",
                service_name=f"platform_connector_{platform.value}",
                host=config["api_endpoint"],
                port=config["port"],
                health_check_url="/health",
                metadata={
                    'platform': platform.value,
                    'supported_formats': self._get_platform_formats(platform),
                    'rate_limits': self._get_platform_rate_limits(platform),
                    'authentication': 'oauth2'
                }
            )
            self.platform_connectors[platform] = connector
        
        # Services CDN
        self.cdn_services = [
            ServiceInstance(
                service_id="cdn_cloudflare_001",
                service_name="cdn_cloudflare",
                host="cdn.iacherie.com",
                port=443,
                health_check_url="/health",
                metadata={
                    'provider': 'cloudflare',
                    'global_presence': True,
                    'edge_locations': 200,
                    'supported_formats': ['video', 'audio', 'image']
                }
            ),
            ServiceInstance(
                service_id="cdn_aws_001", 
                service_name="cdn_aws_cloudfront",
                host="cdn-aws.iacherie.com",
                port=443,
                health_check_url="/health",
                metadata={
                    'provider': 'aws_cloudfront',
                    'global_presence': True, 
                    'edge_locations': 300,
                    'supported_formats': ['video', 'audio', 'image']
                }
            )
        ]
        
        # Services de traitement de contenu pour adaptation
        self.distribution_services['content_adaptation'] = [
            ServiceInstance(
                service_id="adaptation_001",
                service_name="content_adaptation",
                host="adaptation.iacherie.com",
                port=8080,
                health_check_url="/health",
                metadata={
                    'capabilities': ['resize', 'format_conversion', 'compression', 'watermarking'],
                    'supported_input_formats': ['mp4', 'mov', 'avi', 'mp3', 'wav', 'jpg', 'png'],
                    'supported_output_formats': ['mp4', 'webm', 'mp3', 'aac', 'jpg', 'webp']
                }
            )
        ]
        
        # Services de planification
        self.distribution_services['scheduling'] = [
            ServiceInstance(
                service_id="scheduler_001",
                service_name="distribution_scheduler",
                host="scheduler.iacherie.com",
                port=8080,
                health_check_url="/health",
                metadata={
                    'capabilities': ['optimal_timing', 'audience_analysis', 'timezone_optimization'],
                    'supported_platforms': [p.value for p in Platform],
                    'scheduling_accuracy': 0.95
                }
            )
        ]
    
    def _get_platform_formats(self, platform: Platform) -> List[str]:
        """Obtenir les formats supportés par plateforme"""
        format_mapping = {
            Platform.YOUTUBE: ['video_long', 'video_short', 'livestream'],
            Platform.TIKTOK: ['video_short'],
            Platform.INSTAGRAM: ['video_short', 'image_post', 'story'],
            Platform.TWITTER: ['video_short', 'image_post', 'text_post'],
            Platform.SPOTIFY: ['audio_podcast', 'audio_music'],
            Platform.TWITCH: ['livestream'],
        }
        return format_mapping.get(platform, ['video_long', 'image_post'])
    
    def _get_platform_rate_limits(self, platform: Platform) -> Dict[str, int]:
        """Obtenir les limites de taux par plateforme"""
        rate_limits = {
            Platform.YOUTUBE: {'requests_per_hour': 1000, 'uploads_per_day': 100},
            Platform.TIKTOK: {'requests_per_hour': 500, 'uploads_per_day': 50},
            Platform.INSTAGRAM: {'requests_per_hour': 200, 'uploads_per_day': 25},
            Platform.TWITTER: {'requests_per_hour': 300, 'uploads_per_day': 300},
            Platform.SPOTIFY: {'requests_per_hour': 100, 'uploads_per_day': 10},
        }
        return rate_limits.get(platform, {'requests_per_hour': 100, 'uploads_per_day': 10})
    
    async def coordinate_cross_platform_distribution(self, request: DistributionRequest) -> DistributionPlan:
        """Coordonner la distribution cross-platform"""
        try:
            start_time = time.time()
            self.stats['total_distributions'] += 1
            
            # 1. Analyser la compatibilité des plateformes
            compatible_platforms = await self._analyze_platform_compatibility(
                request.content_format, request.target_platforms
            )
            
            # 2. Optimiser le timing de distribution
            optimal_timing = await self._optimize_distribution_timing(
                compatible_platforms, request.audience_preferences
            )
            
            # 3. Planifier les adaptations de contenu
            content_adaptations = await self._plan_content_adaptations(
                request.content_format, compatible_platforms
            )
            
            # 4. Optimiser la stratégie CDN
            cdn_strategy = await self._optimize_cdn_strategy(
                request.geographic_targeting, request.content_format
            )
            
            # 5. Estimer la portée
            estimated_reach = await self._estimate_platform_reach(
                compatible_platforms, request.audience_preferences
            )
            
            # 6. Calculer les coûts
            distribution_cost = await self._calculate_distribution_cost(
                compatible_platforms, content_adaptations, cdn_strategy
            )
            
            plan = DistributionPlan(
                platforms=compatible_platforms,
                optimal_timing=optimal_timing,
                content_adaptations=content_adaptations,
                cdn_strategy=cdn_strategy,
                estimated_reach=estimated_reach,
                distribution_cost=distribution_cost
            )
            
            # Mettre à jour les statistiques
            processing_time = time.time() - start_time
            await self._update_distribution_stats(plan, processing_time)
            
            logger.info(f"📡 Plan distribution créé: {len(compatible_platforms)} plateformes, portée estimée: {sum(estimated_reach.values())}")
            return plan
            
        except Exception as e:
            logger.error(f"Erreur coordination distribution: {e}")
            return DistributionPlan(
                platforms={},
                optimal_timing={},
                content_adaptations={},
                cdn_strategy={},
                estimated_reach={},
                distribution_cost=0.0
            )
    
    async def _analyze_platform_compatibility(self, content_format: ContentFormat, 
                                           target_platforms: List[Platform]) -> Dict[Platform, Dict[str, Any]]:
        """Analyser la compatibilité des plateformes"""
        compatible_platforms = {}
        
        for platform in target_platforms:
            if platform in self.platform_connectors:
                connector = self.platform_connectors[platform]
                supported_formats = connector.metadata.get('supported_formats', [])
                
                if content_format.value in supported_formats:
                    compatible_platforms[platform] = {
                        'connector': connector,
                        'compatibility_score': 1.0,
                        'supported_formats': supported_formats,
                        'rate_limits': connector.metadata.get('rate_limits', {}),
                        'recommended_adaptations': self._get_platform_adaptations(platform, content_format)
                    }
                else:
                    # Platform partiellement compatible avec adaptations
                    adaptations = self._get_required_adaptations(content_format, platform)
                    if adaptations:
                        compatible_platforms[platform] = {
                            'connector': connector,
                            'compatibility_score': 0.7,
                            'supported_formats': supported_formats,
                            'rate_limits': connector.metadata.get('rate_limits', {}),
                            'required_adaptations': adaptations
                        }
        
        return compatible_platforms
    
    def _get_platform_adaptations(self, platform: Platform, content_format: ContentFormat) -> List[str]:
        """Obtenir les adaptations recommandées par plateforme"""
        adaptations = []
        
        if platform == Platform.TIKTOK:
            if content_format == ContentFormat.VIDEO_LONG:
                adaptations.extend(['crop_to_vertical', 'trim_to_60s', 'add_captions'])
            elif content_format == ContentFormat.VIDEO_SHORT:
                adaptations.extend(['crop_to_vertical', 'add_captions'])
        
        elif platform == Platform.INSTAGRAM:
            if content_format in [ContentFormat.VIDEO_LONG, ContentFormat.VIDEO_SHORT]:
                adaptations.extend(['crop_to_square', 'add_branded_overlay'])
            elif content_format == ContentFormat.IMAGE_POST:
                adaptations.extend(['crop_to_square', 'add_watermark'])
        
        elif platform == Platform.YOUTUBE:
            if content_format == ContentFormat.VIDEO_SHORT:
                adaptations.extend(['crop_to_vertical', 'add_youtube_shorts_overlay'])
            elif content_format == ContentFormat.VIDEO_LONG:
                adaptations.extend(['add_intro_outro', 'add_chapters'])
        
        return adaptations
    
    def _get_required_adaptations(self, content_format: ContentFormat, platform: Platform) -> List[str]:
        """Obtenir les adaptations requises pour compatibilité"""
        # Logic pour adaptations obligatoires
        if content_format == ContentFormat.VIDEO_LONG and platform == Platform.TIKTOK:
            return ['segment_to_shorts', 'crop_to_vertical']
        elif content_format == ContentFormat.AUDIO_PODCAST and platform == Platform.YOUTUBE:
            return ['convert_to_video', 'add_waveform_visualization']
        
        return []
    
    async def _optimize_distribution_timing(self, platforms: Dict[Platform, Dict[str, Any]], 
                                          audience_preferences: Dict[str, Any]) -> Dict[Platform, datetime]:
        """Optimiser le timing de distribution"""
        optimal_timing = {}
        
        # Timing par défaut basé sur les meilleures pratiques
        platform_timing = {
            Platform.YOUTUBE: 14,  # 14h00
            Platform.TIKTOK: 18,   # 18h00
            Platform.INSTAGRAM: 11, # 11h00
            Platform.TWITTER: 12,   # 12h00
            Platform.LINKEDIN: 10,  # 10h00
        }
        
        for platform in platforms.keys():
            base_hour = platform_timing.get(platform, 12)
            
            # Ajuster selon les préférences d'audience
            timezone_offset = audience_preferences.get('timezone_offset', 0)
            optimal_hour = (base_hour + timezone_offset) % 24
            
            # Programmer pour le prochain créneau optimal
            now = datetime.now()
            optimal_time = now.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
            
            # Si l'heure est déjà passée aujourd'hui, programmer pour demain
            if optimal_time <= now:
                optimal_time += timedelta(days=1)
            
            optimal_timing[platform] = optimal_time
        
        return optimal_timing
    
    async def _plan_content_adaptations(self, content_format: ContentFormat, 
                                      platforms: Dict[Platform, Dict[str, Any]]) -> Dict[Platform, Dict[str, Any]]:
        """Planifier les adaptations de contenu"""
        adaptations = {}
        
        for platform, platform_info in platforms.items():
            platform_adaptations = {}
            
            # Adaptations recommandées
            recommended = platform_info.get('recommended_adaptations', [])
            if recommended:
                platform_adaptations['recommended'] = recommended
            
            # Adaptations requises
            required = platform_info.get('required_adaptations', [])
            if required:
                platform_adaptations['required'] = required
            
            # Spécifications techniques
            platform_adaptations['technical_specs'] = self._get_platform_specs(platform, content_format)
            
            adaptations[platform] = platform_adaptations
        
        return adaptations
    
    def _get_platform_specs(self, platform: Platform, content_format: ContentFormat) -> Dict[str, Any]:
        """Obtenir les spécifications techniques par plateforme"""
        specs = {
            Platform.YOUTUBE: {
                'video': {'resolution': '1920x1080', 'bitrate': '8000kbps', 'format': 'mp4'},
                'audio': {'bitrate': '128kbps', 'format': 'aac'}
            },
            Platform.TIKTOK: {
                'video': {'resolution': '1080x1920', 'bitrate': '4000kbps', 'format': 'mp4'},
                'audio': {'bitrate': '128kbps', 'format': 'aac'}
            },
            Platform.INSTAGRAM: {
                'video': {'resolution': '1080x1080', 'bitrate': '3500kbps', 'format': 'mp4'},
                'image': {'resolution': '1080x1080', 'format': 'jpg'}
            }
        }
        
        return specs.get(platform, {})
    
    async def _optimize_cdn_strategy(self, geographic_targeting: List[str], 
                                   content_format: ContentFormat) -> Dict[str, Any]:
        """Optimiser la stratégie CDN"""
        cdn_strategy = {
            'primary_cdn': None,
            'backup_cdn': None,
            'edge_locations': [],
            'caching_strategy': {},
            'estimated_cost': 0.0
        }
        
        # Sélectionner le CDN principal
        if self.cdn_services:
            primary_cdn = self.cdn_services[0]  # Cloudflare par défaut
            cdn_strategy['primary_cdn'] = primary_cdn.service_id
            
            if len(self.cdn_services) > 1:
                cdn_strategy['backup_cdn'] = self.cdn_services[1].service_id
        
        # Optimiser selon la géolocalisation
        if geographic_targeting:
            cdn_strategy['edge_locations'] = geographic_targeting[:5]  # Top 5 régions
        else:
            cdn_strategy['edge_locations'] = ['us-east-1', 'eu-west-1', 'ap-southeast-1']
        
        # Stratégie de cache selon le format
        if content_format in [ContentFormat.VIDEO_LONG, ContentFormat.VIDEO_SHORT]:
            cdn_strategy['caching_strategy'] = {
                'ttl_seconds': 86400,  # 24h
                'compression': True,
                'adaptive_bitrate': True
            }
        elif content_format in [ContentFormat.IMAGE_POST]:
            cdn_strategy['caching_strategy'] = {
                'ttl_seconds': 604800,  # 7 jours
                'compression': True,
                'webp_conversion': True
            }
        
        # Estimation de coût CDN
        base_cost_per_gb = 0.08  # $0.08 per GB
        estimated_size_gb = self._estimate_content_size(content_format)
        cdn_strategy['estimated_cost'] = estimated_size_gb * base_cost_per_gb * len(cdn_strategy['edge_locations'])
        
        return cdn_strategy
    
    def _estimate_content_size(self, content_format: ContentFormat) -> float:
        """Estimer la taille du contenu en GB"""
        size_estimates = {
            ContentFormat.VIDEO_LONG: 2.0,      # 2GB pour 30min de vidéo
            ContentFormat.VIDEO_SHORT: 0.1,     # 100MB pour 1min
            ContentFormat.AUDIO_PODCAST: 0.5,   # 500MB pour 1h d'audio
            ContentFormat.AUDIO_MUSIC: 0.05,    # 50MB pour 3min
            ContentFormat.IMAGE_POST: 0.01,     # 10MB pour image HD
            ContentFormat.TEXT_POST: 0.001,     # 1MB pour texte
        }
        return size_estimates.get(content_format, 0.1)
    
    async def _estimate_platform_reach(self, platforms: Dict[Platform, Dict[str, Any]], 
                                     audience_preferences: Dict[str, Any]) -> Dict[Platform, int]:
        """Estimer la portée par plateforme"""
        estimated_reach = {}
        
        # Facteurs de base de portée par plateforme
        base_reach = {
            Platform.YOUTUBE: 1000,
            Platform.TIKTOK: 5000,
            Platform.INSTAGRAM: 800,
            Platform.TWITTER: 500,
            Platform.FACEBOOK: 600,
            Platform.LINKEDIN: 300,
        }
        
        # Multiplicateurs selon l'audience
        follower_count = audience_preferences.get('follower_count', 1000)
        engagement_rate = audience_preferences.get('engagement_rate', 0.05)
        
        for platform in platforms.keys():
            base = base_reach.get(platform, 500)
            
            # Ajuster selon les followers et l'engagement
            follower_factor = min(10, max(0.1, follower_count / 1000))
            engagement_factor = min(5, max(0.5, engagement_rate * 20))
            
            estimated_reach[platform] = int(base * follower_factor * engagement_factor)
        
        return estimated_reach
    
    async def _calculate_distribution_cost(self, platforms: Dict[Platform, Dict[str, Any]], 
                                         content_adaptations: Dict[Platform, Dict[str, Any]], 
                                         cdn_strategy: Dict[str, Any]) -> float:
        """Calculer le coût de distribution"""
        total_cost = 0.0
        
        # Coût CDN
        total_cost += cdn_strategy.get('estimated_cost', 0.0)
        
        # Coût d'adaptation de contenu
        adaptation_cost_per_platform = 0.50  # $0.50 par adaptation
        for platform, adaptations in content_adaptations.items():
            adaptation_count = (
                len(adaptations.get('recommended', [])) + 
                len(adaptations.get('required', []))
            )
            total_cost += adaptation_count * adaptation_cost_per_platform
        
        # Coût de distribution par plateforme
        platform_cost = 0.10  # $0.10 par plateforme
        total_cost += len(platforms) * platform_cost
        
        return round(total_cost, 2)
    
    async def _update_distribution_stats(self, plan: DistributionPlan, processing_time: float):
        """Mettre à jour les statistiques de distribution"""
        try:
            # Marquer comme succès si au moins une plateforme
            if plan.platforms:
                self.stats['successful_distributions'] += 1
            
            # Mettre à jour par plateforme
            for platform in plan.platforms.keys():
                platform_key = platform.value
                self.stats['platforms_used'][platform_key] = \
                    self.stats['platforms_used'].get(platform_key, 0) + 1
            
            # Portée totale
            total_reach = sum(plan.estimated_reach.values())
            self.stats['total_reach'] += total_reach
            
            # Temps de traitement moyen
            total_requests = self.stats['total_distributions']
            current_avg = self.stats['avg_distribution_time']
            new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
            self.stats['avg_distribution_time'] = new_avg
            
        except Exception as e:
            logger.error(f"Erreur mise à jour stats distribution: {e}")
    
    async def get_distribution_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de distribution"""
        stats = self.stats.copy()
        
        if self.stats['total_distributions'] > 0:
            stats['success_rate'] = self.stats['successful_distributions'] / self.stats['total_distributions']
            stats['avg_reach_per_distribution'] = self.stats['total_reach'] / self.stats['total_distributions']
        else:
            stats['success_rate'] = 0.0
            stats['avg_reach_per_distribution'] = 0.0
        
        stats['available_platforms'] = [p.value for p in self.platform_connectors.keys()]
        stats['available_cdn_services'] = len(self.cdn_services)
        
        return stats

# Factory function
def create_distribution_service_coordination() -> DistributionServiceCoordination:
    """Factory pour créer une coordination de services de distribution"""
    return DistributionServiceCoordination()

__all__ = [
    'DistributionServiceCoordination',
    'Platform',
    'ContentFormat', 
    'DistributionPriority',
    'DistributionRequest',
    'DistributionPlan',
    'create_distribution_service_coordination'
]