"""📡 Distribution Tracking Storage - Enterprise Grade
===================================================
Expert: BACKEND SENIOR + ML ENGINEER + IA PROMPT ENGINEER + DEVOPS
Technologies: Multi-Platform Distribution + Analytics + Performance Tracking + AI Insights
Architecture: Level 2 - Storage Layer - Creator Economy
Date: 2025-01-14

Enterprise storage solution for content distribution tracking across multiple platforms
with performance analytics, audience insights and AI-driven optimization recommendations.
===================================================
"""

import asyncio
import logging
import time
import hashlib
import json
import uuid
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

# Optional imports with fallbacks
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Plateformes de distribution"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    SPOTIFY = "spotify"
    PODCAST = "podcast"
    BLOG = "blog"
    WEBSITE = "website"

class DistributionStatus(Enum):
    """États de distribution"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    REMOVED = "removed"
    SUSPENDED = "suspended"

class ContentFormat(Enum):
    """Formats de contenu"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"

class PerformanceMetric(Enum):
    """Métriques de performance"""
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    CLICK_THROUGH_RATE = "click_through_rate"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"

@dataclass
class DistributionTrackingConfig:
    """Configuration tracking distribution"""
    redis_url: str = "redis://localhost:6379"
    max_pool_size: int = 30
    distribution_ttl: int = 86400 * 180  # 6 mois
    metrics_ttl: int = 86400 * 90        # 3 mois
    enable_real_time_tracking: bool = True
    enable_ai_optimization: bool = True
    max_platforms_per_content: int = 15
    tracking_interval: int = 300  # 5 minutes
    supported_platforms: Set[Platform] = field(default_factory=lambda: {
        Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM, 
        Platform.FACEBOOK, Platform.TWITTER, Platform.LINKEDIN
    })

@dataclass
class PlatformCredentials:
    """Identifiants plateforme"""
    platform: Platform
    api_key: str = ""
    access_token: str = ""
    refresh_token: str = ""
    user_id: str = ""
    account_handle: str = ""
    expires_at: Optional[datetime] = None
    permissions: List[str] = field(default_factory=list)
    rate_limit: Dict[str, int] = field(default_factory=dict)

@dataclass
class DistributionEntry:
    """Entrée de distribution"""
    distribution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    creator_id: str = ""
    platform: Platform = Platform.YOUTUBE
    platform_content_id: str = ""
    platform_url: str = ""
    content_format: ContentFormat = ContentFormat.VIDEO
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    thumbnail_url: str = ""
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    status: DistributionStatus = DistributionStatus.PENDING
    platform_specific_data: Dict[str, Any] = field(default_factory=dict)
    optimization_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceSnapshot:
    """Instantané performance"""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    distribution_id: str = ""
    platform: Platform = Platform.YOUTUBE
    metrics: Dict[str, Union[int, float]] = field(default_factory=dict)
    demographic_data: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, Any] = field(default_factory=dict)
    device_data: Dict[str, Any] = field(default_factory=dict)
    traffic_sources: Dict[str, int] = field(default_factory=dict)
    engagement_timeline: List[Dict[str, Any]] = field(default_factory=list)
    captured_at: datetime = field(default_factory=datetime.now)

@dataclass
class CrossPlatformAnalytics:
    """Analytics cross-platform"""
    content_id: str
    creator_id: str
    period_start: datetime
    period_end: datetime
    total_distributions: int = 0
    active_platforms: List[Platform] = field(default_factory=list)
    aggregate_metrics: Dict[str, Union[int, float]] = field(default_factory=dict)
    platform_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    best_performing_platform: Optional[Platform] = None
    content_optimization_score: float = 0.0
    audience_overlap: Dict[str, float] = field(default_factory=dict)
    revenue_attribution: Dict[str, float] = field(default_factory=dict)
    ai_insights: List[str] = field(default_factory=list)

class DistributionTrackingStorage:
    """Gestionnaire stockage tracking distribution enterprise"""
    
    def __init__(self, config: DistributionTrackingConfig):
        self.config = config
        self.redis_pool = None
        self.platform_credentials = {}
        self.distribution_cache = {}
        self.performance_cache = {}
        self.tracking_queue = asyncio.Queue()
        
        # Métriques de performance
        self.metrics = {
            'total_distributions': 0,
            'active_platforms': 0,
            'successful_publications': 0,
            'failed_publications': 0,
            'total_views_tracked': 0,
            'avg_engagement_rate': 0.0
        }
        
        logger.info("DistributionTrackingStorage initialisé")
    
    async def initialize(self):
        """Initialisation connexions Redis"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis non disponible - mode dégradé")
            return
        
        try:
            self.redis_pool = redis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.max_pool_size,
                retry_on_timeout=True
            )
            
            # Test connexion
            async with redis.Redis(connection_pool=self.redis_pool) as r:
                await r.ping()
            
            # Démarrage processus de tracking
            if self.config.enable_real_time_tracking:
                asyncio.create_task(self._performance_tracker())
                asyncio.create_task(self._tracking_processor())
            
            logger.info("Connexion Redis établie pour le tracking distribution")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Redis distribution: {e}")
            self.redis_pool = None
    
    async def create_distribution(self, content_id: str, creator_id: str,
                                 platform: Platform, distribution_data: Dict[str, Any]) -> str:
        """Création distribution sur plateforme"""
        try:
            # Validation données
            validation_result = await self._validate_distribution_data(
                platform, distribution_data
            )
            if not validation_result['valid']:
                raise ValueError(f"Distribution invalide: {validation_result['errors']}")
            
            # Création entrée distribution
            distribution = DistributionEntry(
                content_id=content_id,
                creator_id=creator_id,
                platform=platform,
                content_format=ContentFormat(distribution_data.get('format', ContentFormat.VIDEO.value)),
                title=distribution_data.get('title', ''),
                description=distribution_data.get('description', ''),
                tags=distribution_data.get('tags', []),
                thumbnail_url=distribution_data.get('thumbnail', ''),
                scheduled_at=datetime.fromisoformat(distribution_data['scheduled_at']) if 'scheduled_at' in distribution_data else None,
                platform_specific_data=distribution_data.get('platform_data', {}),
                optimization_settings=distribution_data.get('optimization', {})
            )
            
            # Statut initial
            if distribution.scheduled_at and distribution.scheduled_at > datetime.now():
                distribution.status = DistributionStatus.SCHEDULED
            else:
                distribution.status = DistributionStatus.PENDING
            
            # Optimisation AI si activée
            if self.config.enable_ai_optimization:
                await self._apply_ai_optimization(distribution)
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_distribution_to_redis(distribution)
            
            # Cache local
            self.distribution_cache[distribution.distribution_id] = distribution
            
            # Ajout à la queue de publication
            if distribution.status == DistributionStatus.PENDING:
                await self.tracking_queue.put({
                    'action': 'publish',
                    'distribution_id': distribution.distribution_id
                })
            
            # Mise à jour métriques
            self.metrics['total_distributions'] += 1
            
            logger.info(f"Distribution créée: {distribution.distribution_id} sur {platform.value}")
            return distribution.distribution_id
            
        except Exception as e:
            logger.error(f"Erreur création distribution: {e}")
            raise
    
    async def publish_to_platform(self, distribution_id: str) -> bool:
        """Publication sur plateforme"""
        try:
            distribution = await self._get_distribution(distribution_id)
            if not distribution:
                return False
            
            # Mise à jour statut
            distribution.status = DistributionStatus.PUBLISHING
            distribution.updated_at = datetime.now()
            
            # Simulation publication (à remplacer par vraies APIs)
            publication_result = await self._simulate_platform_publication(distribution)
            
            if publication_result['success']:
                distribution.status = DistributionStatus.PUBLISHED
                distribution.published_at = datetime.now()
                distribution.platform_content_id = publication_result['platform_id']
                distribution.platform_url = publication_result['url']
                
                # Démarrage tracking performance
                await self._start_performance_tracking(distribution)
                
                self.metrics['successful_publications'] += 1
            else:
                distribution.status = DistributionStatus.FAILED
                distribution.platform_specific_data['error'] = publication_result['error']
                self.metrics['failed_publications'] += 1
            
            # Sauvegarde
            if self.redis_pool:
                await self._store_distribution_to_redis(distribution)
            
            self.distribution_cache[distribution_id] = distribution
            
            logger.info(f"Publication {distribution_id}: {distribution.status.value}")
            return distribution.status == DistributionStatus.PUBLISHED
            
        except Exception as e:
            logger.error(f"Erreur publication {distribution_id}: {e}")
            return False
    
    async def track_performance(self, distribution_id: str) -> Optional[PerformanceSnapshot]:
        """Tracking performance distribution"""
        try:
            distribution = await self._get_distribution(distribution_id)
            if not distribution or distribution.status != DistributionStatus.PUBLISHED:
                return None
            
            # Récupération métriques plateforme
            metrics = await self._fetch_platform_metrics(distribution)
            
            # Création snapshot performance
            snapshot = PerformanceSnapshot(
                distribution_id=distribution_id,
                platform=distribution.platform,
                metrics=metrics['basic_metrics'],
                demographic_data=metrics.get('demographics', {}),
                geographic_data=metrics.get('geography', {}),
                device_data=metrics.get('devices', {}),
                traffic_sources=metrics.get('traffic_sources', {}),
                engagement_timeline=metrics.get('timeline', [])
            )
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_performance_snapshot_to_redis(snapshot)
            
            # Cache local
            cache_key = f"{distribution_id}:{snapshot.captured_at.date()}"
            self.performance_cache[cache_key] = snapshot
            
            # Mise à jour métriques globales
            if 'views' in metrics['basic_metrics']:
                self.metrics['total_views_tracked'] += metrics['basic_metrics']['views']
            
            logger.info(f"Performance trackée: {distribution_id} ({len(metrics['basic_metrics'])} métriques)")
            return snapshot
            
        except Exception as e:
            logger.error(f"Erreur tracking performance {distribution_id}: {e}")
            return None
    
    async def get_cross_platform_analytics(self, content_id: str, 
                                          period_days: int = 30) -> CrossPlatformAnalytics:
        """Analytics cross-platform pour contenu"""
        try:
            period_end = datetime.now()
            period_start = period_end - timedelta(days=period_days)
            
            # Récupération distributions du contenu
            distributions = await self._get_content_distributions(content_id, period_start, period_end)
            
            if not distributions:
                creator_id = distributions[0].creator_id if distributions else ""
                return CrossPlatformAnalytics(
                    content_id=content_id,
                    creator_id=creator_id,
                    period_start=period_start,
                    period_end=period_end
                )
            
            creator_id = distributions[0].creator_id
            
            # Calcul analytics cross-platform
            analytics = CrossPlatformAnalytics(
                content_id=content_id,
                creator_id=creator_id,
                period_start=period_start,
                period_end=period_end,
                total_distributions=len(distributions),
                active_platforms=[d.platform for d in distributions if d.status == DistributionStatus.PUBLISHED]
            )
            
            # Agrégation métriques
            aggregate_metrics = defaultdict(int)
            platform_performance = {}
            
            for distribution in distributions:
                if distribution.status == DistributionStatus.PUBLISHED:
                    # Récupération dernière performance
                    latest_snapshot = await self._get_latest_performance_snapshot(
                        distribution.distribution_id
                    )
                    
                    if latest_snapshot:
                        platform_key = distribution.platform.value
                        
                        # Agrégation globale
                        for metric, value in latest_snapshot.metrics.items():
                            aggregate_metrics[metric] += value
                        
                        # Performance par plateforme
                        platform_performance[platform_key] = {
                            'metrics': latest_snapshot.metrics,
                            'demographics': latest_snapshot.demographic_data,
                            'geography': latest_snapshot.geographic_data,
                            'url': distribution.platform_url
                        }
            
            analytics.aggregate_metrics = dict(aggregate_metrics)
            analytics.platform_performance = platform_performance
            
            # Identification meilleure plateforme
            analytics.best_performing_platform = await self._identify_best_platform(
                platform_performance
            )
            
            # Score optimisation contenu
            analytics.content_optimization_score = await self._calculate_optimization_score(
                analytics
            )
            
            # Overlap audience (estimation)
            analytics.audience_overlap = await self._estimate_audience_overlap(
                analytics.active_platforms
            )
            
            # Attribution revenus
            analytics.revenue_attribution = await self._calculate_revenue_attribution(
                content_id, analytics.platform_performance
            )
            
            # Insights IA
            if self.config.enable_ai_optimization:
                analytics.ai_insights = await self._generate_ai_insights(analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erreur analytics cross-platform {content_id}: {e}")
            return CrossPlatformAnalytics(
                content_id=content_id,
                creator_id="",
                period_start=period_start,
                period_end=period_end
            )
    
    async def optimize_distribution_strategy(self, creator_id: str, 
                                           content_type: ContentFormat) -> Dict[str, Any]:
        """Optimisation stratégie distribution"""
        try:
            optimization = {
                'creator_id': creator_id,
                'content_type': content_type.value,
                'recommended_platforms': [],
                'optimal_timing': {},
                'content_adaptations': {},
                'audience_targeting': {},
                'performance_predictions': {}
            }
            
            # Analyse historique créateur
            historical_data = await self._analyze_creator_history(creator_id, content_type)
            
            # Recommandations plateformes
            optimization['recommended_platforms'] = await self._recommend_platforms(
                historical_data, content_type
            )
            
            # Timing optimal
            optimization['optimal_timing'] = await self._calculate_optimal_timing(
                creator_id, optimization['recommended_platforms']
            )
            
            # Adaptations contenu
            optimization['content_adaptations'] = await self._suggest_content_adaptations(
                content_type, optimization['recommended_platforms']
            )
            
            # Ciblage audience
            optimization['audience_targeting'] = await self._optimize_audience_targeting(
                creator_id, historical_data
            )
            
            # Prédictions performance
            optimization['performance_predictions'] = await self._predict_performance(
                creator_id, content_type, optimization['recommended_platforms']
            )
            
            return optimization
            
        except Exception as e:
            logger.error(f"Erreur optimisation stratégie {creator_id}: {e}")
            return {'error': str(e)}
    
    async def _validate_distribution_data(self, platform: Platform, 
                                         data: Dict[str, Any]) -> Dict[str, Any]:
        """Validation données distribution"""
        errors = []
        
        # Validation champs requis
        required_fields = ['title', 'format']
        for field in required_fields:
            if field not in data:
                errors.append(f"Champ requis manquant: {field}")
        
        # Validation format pour plateforme
        if 'format' in data:
            format_value = data['format']
            platform_formats = self._get_supported_formats(platform)
            if format_value not in [f.value for f in platform_formats]:
                errors.append(f"Format {format_value} non supporté par {platform.value}")
        
        # Validation titre
        if 'title' in data:
            title_length = len(data['title'])
            max_length = self._get_platform_title_limit(platform)
            if title_length > max_length:
                errors.append(f"Titre trop long pour {platform.value}: {title_length}/{max_length}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _get_supported_formats(self, platform: Platform) -> List[ContentFormat]:
        """Formats supportés par plateforme"""
        platform_formats = {
            Platform.YOUTUBE: [ContentFormat.VIDEO, ContentFormat.SHORT],
            Platform.TIKTOK: [ContentFormat.VIDEO, ContentFormat.SHORT],
            Platform.INSTAGRAM: [ContentFormat.VIDEO, ContentFormat.IMAGE, ContentFormat.STORY, ContentFormat.REEL],
            Platform.FACEBOOK: [ContentFormat.VIDEO, ContentFormat.IMAGE, ContentFormat.TEXT],
            Platform.TWITTER: [ContentFormat.VIDEO, ContentFormat.IMAGE, ContentFormat.TEXT],
            Platform.LINKEDIN: [ContentFormat.VIDEO, ContentFormat.IMAGE, ContentFormat.TEXT],
            Platform.PINTEREST: [ContentFormat.IMAGE],
            Platform.SPOTIFY: [ContentFormat.AUDIO]
        }
        
        return platform_formats.get(platform, [ContentFormat.VIDEO, ContentFormat.IMAGE, ContentFormat.TEXT])
    
    def _get_platform_title_limit(self, platform: Platform) -> int:
        """Limite caractères titre par plateforme"""
        limits = {
            Platform.YOUTUBE: 100,
            Platform.TIKTOK: 150,
            Platform.INSTAGRAM: 125,
            Platform.FACEBOOK: 125,
            Platform.TWITTER: 280,
            Platform.LINKEDIN: 150,
            Platform.PINTEREST: 100
        }
        
        return limits.get(platform, 100)
    
    async def _apply_ai_optimization(self, distribution: DistributionEntry):
        """Application optimisation IA"""
        # Optimisation titre
        if len(distribution.title) < 10:
            distribution.optimization_settings['title_suggestion'] = \
                f"🔥 {distribution.title} - Guide Complet 2024"
        
        # Optimisation tags
        if len(distribution.tags) < 5:
            suggested_tags = await self._generate_suggested_tags(
                distribution.title, distribution.platform
            )
            distribution.tags.extend(suggested_tags[:5])
        
        # Optimisation description
        if len(distribution.description) < 50:
            distribution.optimization_settings['description_enhancement'] = True
    
    async def _generate_suggested_tags(self, title: str, platform: Platform) -> List[str]:
        """Génération tags suggérés"""
        # Tags basiques basés sur le titre
        words = title.lower().split()
        base_tags = [word for word in words if len(word) > 3]
        
        # Tags spécifiques plateforme
        platform_tags = {
            Platform.YOUTUBE: ['tutorial', 'howto', '2024'],
            Platform.TIKTOK: ['viral', 'trending', 'fyp'],
            Platform.INSTAGRAM: ['instagood', 'photooftheday', 'creator'],
            Platform.TWITTER: ['thread', 'tips', 'insights'],
            Platform.LINKEDIN: ['business', 'professional', 'industry']
        }
        
        suggested = base_tags + platform_tags.get(platform, [])
        return list(set(suggested))[:10]
    
    async def _simulate_platform_publication(self, distribution: DistributionEntry) -> Dict[str, Any]:
        """Simulation publication plateforme"""
        # Simulation simple (à remplacer par vraies APIs)
        platform_id = f"{distribution.platform.value}_{int(time.time())}"
        platform_url = f"https://{distribution.platform.value}.com/watch?v={platform_id}"
        
        # Simulation succès/échec
        success_rate = 0.95  # 95% de succès
        success = hash(distribution.distribution_id) % 100 < success_rate * 100
        
        if success:
            return {
                'success': True,
                'platform_id': platform_id,
                'url': platform_url
            }
        else:
            return {
                'success': False,
                'error': 'Erreur simulation publication'
            }
    
    async def _start_performance_tracking(self, distribution: DistributionEntry):
        """Démarrage tracking performance"""
        await self.tracking_queue.put({
            'action': 'track_performance',
            'distribution_id': distribution.distribution_id,
            'delay': 300  # 5 minutes
        })
    
    async def _fetch_platform_metrics(self, distribution: DistributionEntry) -> Dict[str, Any]:
        """Récupération métriques plateforme"""
        # Simulation métriques (à remplacer par vraies APIs)
        base_metrics = {
            'views': max(100, hash(distribution.platform_content_id) % 10000),
            'likes': max(10, hash(distribution.platform_content_id + 'likes') % 1000),
            'comments': max(1, hash(distribution.platform_content_id + 'comments') % 100),
            'shares': max(1, hash(distribution.platform_content_id + 'shares') % 50),
            'saves': max(1, hash(distribution.platform_content_id + 'saves') % 30)
        }
        
        # Calcul métriques dérivées
        base_metrics['engagement_rate'] = (
            (base_metrics['likes'] + base_metrics['comments'] + base_metrics['shares']) 
            / max(base_metrics['views'], 1)
        )
        
        return {
            'basic_metrics': base_metrics,
            'demographics': self._generate_mock_demographics(),
            'geography': self._generate_mock_geography(),
            'devices': self._generate_mock_devices(),
            'traffic_sources': self._generate_mock_traffic_sources(),
            'timeline': self._generate_mock_timeline()
        }
    
    def _generate_mock_demographics(self) -> Dict[str, Any]:
        """Génération démographiques mock"""
        return {
            'age_groups': {
                '18-24': 25, '25-34': 35, '35-44': 25, '45-54': 10, '55+': 5
            },
            'gender': {'male': 55, 'female': 45},
            'interests': ['technology', 'entertainment', 'education']
        }
    
    def _generate_mock_geography(self) -> Dict[str, Any]:
        """Génération géographie mock"""
        return {
            'countries': {
                'US': 40, 'UK': 15, 'CA': 10, 'AU': 8, 'DE': 7, 'FR': 6, 'Other': 14
            },
            'cities': {
                'New York': 12, 'Los Angeles': 10, 'London': 8, 'Toronto': 6, 'Sydney': 5
            }
        }
    
    def _generate_mock_devices(self) -> Dict[str, Any]:
        """Génération devices mock"""
        return {
            'device_types': {'mobile': 65, 'desktop': 25, 'tablet': 10},
            'operating_systems': {'iOS': 35, 'Android': 40, 'Windows': 20, 'Mac': 5}
        }
    
    def _generate_mock_traffic_sources(self) -> Dict[str, int]:
        """Génération sources trafic mock"""
        return {
            'direct': 40,
            'search': 25,
            'social': 20,
            'external': 10,
            'suggested': 5
        }
    
    def _generate_mock_timeline(self) -> List[Dict[str, Any]]:
        """Génération timeline mock"""
        timeline = []
        for i in range(24):  # 24 heures
            timeline.append({
                'hour': i,
                'views': max(10, hash(f"hour_{i}") % 100),
                'engagement': max(1, hash(f"engagement_{i}") % 20)
            })
        return timeline
    
    async def _store_distribution_to_redis(self, distribution: DistributionEntry):
        """Stockage distribution Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            distribution_key = f"distribution:entry:{distribution.distribution_id}"
            distribution_data = {
                'distribution_id': distribution.distribution_id,
                'content_id': distribution.content_id,
                'creator_id': distribution.creator_id,
                'platform': distribution.platform.value,
                'platform_content_id': distribution.platform_content_id,
                'platform_url': distribution.platform_url,
                'content_format': distribution.content_format.value,
                'title': distribution.title,
                'description': distribution.description,
                'tags': distribution.tags,
                'thumbnail_url': distribution.thumbnail_url,
                'scheduled_at': distribution.scheduled_at.isoformat() if distribution.scheduled_at else None,
                'published_at': distribution.published_at.isoformat() if distribution.published_at else None,
                'status': distribution.status.value,
                'platform_specific_data': distribution.platform_specific_data,
                'optimization_settings': distribution.optimization_settings,
                'created_at': distribution.created_at.isoformat(),
                'updated_at': distribution.updated_at.isoformat()
            }
            
            await r.setex(distribution_key, self.config.distribution_ttl, json.dumps(distribution_data))
            
            # Index par créateur
            creator_distributions_key = f"distribution:creator:{distribution.creator_id}"
            await r.zadd(creator_distributions_key, {
                distribution.distribution_id: distribution.created_at.timestamp()
            })
            
            # Index par contenu
            content_distributions_key = f"distribution:content:{distribution.content_id}"
            await r.sadd(content_distributions_key, distribution.distribution_id)
    
    async def _store_performance_snapshot_to_redis(self, snapshot: PerformanceSnapshot):
        """Stockage snapshot performance Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            snapshot_key = f"distribution:performance:{snapshot.distribution_id}:{snapshot.snapshot_id}"
            snapshot_data = {
                'snapshot_id': snapshot.snapshot_id,
                'distribution_id': snapshot.distribution_id,
                'platform': snapshot.platform.value,
                'metrics': snapshot.metrics,
                'demographic_data': snapshot.demographic_data,
                'geographic_data': snapshot.geographic_data,
                'device_data': snapshot.device_data,
                'traffic_sources': snapshot.traffic_sources,
                'engagement_timeline': snapshot.engagement_timeline,
                'captured_at': snapshot.captured_at.isoformat()
            }
            
            await r.setex(snapshot_key, self.config.metrics_ttl, json.dumps(snapshot_data))
            
            # Index temporel
            timeline_key = f"distribution:timeline:{snapshot.distribution_id}"
            await r.zadd(timeline_key, {
                snapshot.snapshot_id: snapshot.captured_at.timestamp()
            })
    
    async def _get_distribution(self, distribution_id: str) -> Optional[DistributionEntry]:
        """Récupération distribution"""
        # Cache local d'abord
        if distribution_id in self.distribution_cache:
            return self.distribution_cache[distribution_id]
        
        # Redis ensuite
        if not self.redis_pool:
            return None
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            distribution_key = f"distribution:entry:{distribution_id}"
            distribution_json = await r.get(distribution_key)
            
            if not distribution_json:
                return None
            
            data = json.loads(distribution_json)
            
            distribution = DistributionEntry(
                distribution_id=data['distribution_id'],
                content_id=data['content_id'],
                creator_id=data['creator_id'],
                platform=Platform(data['platform']),
                platform_content_id=data['platform_content_id'],
                platform_url=data['platform_url'],
                content_format=ContentFormat(data['content_format']),
                title=data['title'],
                description=data['description'],
                tags=data['tags'],
                thumbnail_url=data['thumbnail_url'],
                scheduled_at=datetime.fromisoformat(data['scheduled_at']) if data['scheduled_at'] else None,
                published_at=datetime.fromisoformat(data['published_at']) if data['published_at'] else None,
                status=DistributionStatus(data['status']),
                platform_specific_data=data['platform_specific_data'],
                optimization_settings=data['optimization_settings'],
                created_at=datetime.fromisoformat(data['created_at']),
                updated_at=datetime.fromisoformat(data['updated_at'])
            )
            
            # Mise en cache
            self.distribution_cache[distribution_id] = distribution
            return distribution
    
    async def _get_content_distributions(self, content_id: str, start_date: datetime, 
                                        end_date: datetime) -> List[DistributionEntry]:
        """Récupération distributions contenu"""
        distributions = []
        
        if not self.redis_pool:
            return distributions
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            content_distributions_key = f"distribution:content:{content_id}"
            distribution_ids = await r.smembers(content_distributions_key)
            
            for distribution_id in distribution_ids:
                distribution = await self._get_distribution(distribution_id)
                if (distribution and 
                    start_date <= distribution.created_at <= end_date):
                    distributions.append(distribution)
        
        return distributions
    
    async def _get_latest_performance_snapshot(self, distribution_id: str) -> Optional[PerformanceSnapshot]:
        """Récupération dernier snapshot performance"""
        if not self.redis_pool:
            return None
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            timeline_key = f"distribution:timeline:{distribution_id}"
            latest_snapshots = await r.zrevrange(timeline_key, 0, 0)
            
            if not latest_snapshots:
                return None
            
            snapshot_id = latest_snapshots[0]
            snapshot_key = f"distribution:performance:{distribution_id}:{snapshot_id}"
            snapshot_json = await r.get(snapshot_key)
            
            if not snapshot_json:
                return None
            
            data = json.loads(snapshot_json)
            
            return PerformanceSnapshot(
                snapshot_id=data['snapshot_id'],
                distribution_id=data['distribution_id'],
                platform=Platform(data['platform']),
                metrics=data['metrics'],
                demographic_data=data['demographic_data'],
                geographic_data=data['geographic_data'],
                device_data=data['device_data'],
                traffic_sources=data['traffic_sources'],
                engagement_timeline=data['engagement_timeline'],
                captured_at=datetime.fromisoformat(data['captured_at'])
            )
    
    async def _identify_best_platform(self, platform_performance: Dict[str, Dict[str, Any]]) -> Optional[Platform]:
        """Identification meilleure plateforme"""
        if not platform_performance:
            return None
        
        best_platform = None
        best_score = 0
        
        for platform_name, performance in platform_performance.items():
            metrics = performance.get('metrics', {})
            
            # Score composite basé sur engagement
            score = (
                metrics.get('views', 0) * 0.3 +
                metrics.get('likes', 0) * 0.25 +
                metrics.get('shares', 0) * 0.25 +
                metrics.get('comments', 0) * 0.20
            )
            
            if score > best_score:
                best_score = score
                best_platform = Platform(platform_name)
        
        return best_platform
    
    async def _calculate_optimization_score(self, analytics: CrossPlatformAnalytics) -> float:
        """Calcul score optimisation contenu"""
        if not analytics.platform_performance:
            return 0.0
        
        scores = []
        
        for platform_data in analytics.platform_performance.values():
            metrics = platform_data.get('metrics', {})
            
            # Score basé sur taux engagement
            engagement_rate = metrics.get('engagement_rate', 0)
            scores.append(min(engagement_rate * 100, 100))  # Normalisation
        
        return sum(scores) / len(scores) if scores else 0.0
    
    async def _estimate_audience_overlap(self, platforms: List[Platform]) -> Dict[str, float]:
        """Estimation overlap audience"""
        # Estimation simple (à améliorer avec vraies données)
        overlap = {}
        
        for i, platform1 in enumerate(platforms):
            for platform2 in platforms[i+1:]:
                key = f"{platform1.value}_{platform2.value}"
                # Simulation overlap basée sur similarité plateformes
                overlap[key] = self._calculate_platform_similarity(platform1, platform2)
        
        return overlap
    
    def _calculate_platform_similarity(self, platform1: Platform, platform2: Platform) -> float:
        """Calcul similarité plateformes"""
        # Similarité basée sur type audience
        audience_similarity = {
            (Platform.YOUTUBE, Platform.TIKTOK): 0.6,
            (Platform.INSTAGRAM, Platform.FACEBOOK): 0.8,
            (Platform.TWITTER, Platform.LINKEDIN): 0.4,
            (Platform.YOUTUBE, Platform.INSTAGRAM): 0.5,
            (Platform.TIKTOK, Platform.INSTAGRAM): 0.7
        }
        
        pair = (platform1, platform2) if platform1.value < platform2.value else (platform2, platform1)
        return audience_similarity.get(pair, 0.3)  # 30% par défaut
    
    async def _calculate_revenue_attribution(self, content_id: str, 
                                           platform_performance: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """Calcul attribution revenus"""
        # Attribution basée sur performance relative
        attribution = {}
        total_views = sum(
            perf.get('metrics', {}).get('views', 0) 
            for perf in platform_performance.values()
        )
        
        if total_views > 0:
            for platform, perf in platform_performance.items():
                views = perf.get('metrics', {}).get('views', 0)
                attribution[platform] = views / total_views
        
        return attribution
    
    async def _generate_ai_insights(self, analytics: CrossPlatformAnalytics) -> List[str]:
        """Génération insights IA"""
        insights = []
        
        # Analyse performance globale
        if analytics.content_optimization_score > 80:
            insights.append("📈 Excellent performance cross-platform - continuer cette stratégie")
        elif analytics.content_optimization_score < 40:
            insights.append("⚠️ Performance faible - recommandation d'optimisation urgente")
        
        # Analyse distribution
        if len(analytics.active_platforms) < 3:
            insights.append("🎯 Opportunité d'expansion sur plateformes additionnelles")
        
        # Analyse métriques
        total_views = analytics.aggregate_metrics.get('views', 0)
        if total_views > 10000:
            insights.append("🔥 Contenu viral - capitaliser avec contenu similaire")
        
        # Recommandations spécifiques
        insights.extend([
            "💡 Optimiser timing publication pour audience principale",
            "🎨 Adapter format contenu par plateforme pour meilleur engagement",
            "📊 Analyser démographiques pour ciblage plus précis"
        ])
        
        return insights
    
    # Méthodes d'optimisation (placeholders pour logique complexe)
    async def _analyze_creator_history(self, creator_id: str, 
                                      content_type: ContentFormat) -> Dict[str, Any]:
        """Analyse historique créateur"""
        return {
            'avg_performance_by_platform': {},
            'best_publishing_times': {},
            'audience_preferences': {},
            'content_trends': {}
        }
    
    async def _recommend_platforms(self, historical_data: Dict[str, Any], 
                                  content_type: ContentFormat) -> List[Platform]:
        """Recommandation plateformes"""
        # Recommandations basées sur type contenu
        content_platform_map = {
            ContentFormat.VIDEO: [Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM],
            ContentFormat.IMAGE: [Platform.INSTAGRAM, Platform.PINTEREST, Platform.FACEBOOK],
            ContentFormat.AUDIO: [Platform.SPOTIFY, Platform.PODCAST],
            ContentFormat.TEXT: [Platform.TWITTER, Platform.LINKEDIN, Platform.BLOG]
        }
        
        return content_platform_map.get(content_type, [Platform.YOUTUBE, Platform.INSTAGRAM])
    
    async def _calculate_optimal_timing(self, creator_id: str, 
                                       platforms: List[Platform]) -> Dict[str, Any]:
        """Calcul timing optimal"""
        return {
            'best_days': ['monday', 'wednesday', 'friday'],
            'best_hours_by_platform': {
                platform.value: {'hour': 18, 'confidence': 0.8}
                for platform in platforms
            }
        }
    
    async def _suggest_content_adaptations(self, content_type: ContentFormat, 
                                          platforms: List[Platform]) -> Dict[str, Any]:
        """Suggestions adaptations contenu"""
        adaptations = {}
        
        for platform in platforms:
            if platform == Platform.TIKTOK and content_type == ContentFormat.VIDEO:
                adaptations[platform.value] = {
                    'duration': '15-30 seconds',
                    'aspect_ratio': '9:16',
                    'features': ['trending_audio', 'hashtags', 'quick_cuts']
                }
            elif platform == Platform.YOUTUBE:
                adaptations[platform.value] = {
                    'duration': '8-12 minutes',
                    'aspect_ratio': '16:9',
                    'features': ['custom_thumbnail', 'chapters', 'end_screens']
                }
        
        return adaptations
    
    async def _optimize_audience_targeting(self, creator_id: str, 
                                          historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimisation ciblage audience"""
        return {
            'primary_demographics': {'age': '25-34', 'interests': ['technology', 'entertainment']},
            'geographic_focus': ['US', 'UK', 'CA'],
            'behavioral_targeting': ['engaged_users', 'content_creators']
        }
    
    async def _predict_performance(self, creator_id: str, content_type: ContentFormat, 
                                  platforms: List[Platform]) -> Dict[str, Any]:
        """Prédiction performance"""
        predictions = {}
        
        for platform in platforms:
            predictions[platform.value] = {
                'estimated_views': hash(f"{creator_id}_{platform.value}") % 10000 + 1000,
                'estimated_engagement_rate': 0.05 + (hash(f"engagement_{platform.value}") % 100) / 1000,
                'confidence': 0.7 + (hash(f"confidence_{platform.value}") % 30) / 100
            }
        
        return predictions
    
    async def _performance_tracker(self):
        """Traqueur performance périodique"""
        while True:
            try:
                await asyncio.sleep(self.config.tracking_interval)
                
                # Tracking distributions actives
                active_distributions = [
                    dist for dist in self.distribution_cache.values()
                    if dist.status == DistributionStatus.PUBLISHED
                ]
                
                for distribution in active_distributions[:10]:  # Limite pour performance
                    await self.track_performance(distribution.distribution_id)
                
            except Exception as e:
                logger.error(f"Erreur performance tracker: {e}")
                await asyncio.sleep(self.config.tracking_interval)
    
    async def _tracking_processor(self):
        """Processeur queue tracking"""
        while True:
            try:
                task = await self.tracking_queue.get()
                
                if task['action'] == 'publish':
                    await self.publish_to_platform(task['distribution_id'])
                elif task['action'] == 'track_performance':
                    if 'delay' in task:
                        await asyncio.sleep(task['delay'])
                    await self.track_performance(task['distribution_id'])
                
            except Exception as e:
                logger.error(f"Erreur tracking processor: {e}")
                await asyncio.sleep(1)
    
    async def get_distribution_statistics(self) -> Dict[str, Any]:
        """Statistiques distribution globales"""
        try:
            stats = self.metrics.copy()
            
            if self.redis_pool:
                async with redis.Redis(connection_pool=self.redis_pool) as r:
                    # Comptage créateurs actifs
                    creator_keys = await r.keys("distribution:creator:*")
                    stats['active_creators'] = len(creator_keys)
                    
                    # Plateformes actives
                    platforms = set()
                    for dist in self.distribution_cache.values():
                        platforms.add(dist.platform.value)
                    stats['active_platforms'] = len(platforms)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques distribution: {e}")
            return self.metrics

# Factory function
def create_distribution_tracking_storage(
    redis_url: str = "redis://localhost:6379",
    **kwargs
) -> DistributionTrackingStorage:
    """Factory pour création stockage tracking distribution"""
    config = DistributionTrackingConfig(redis_url=redis_url, **kwargs)
    return DistributionTrackingStorage(config)

# Export classes principales
__all__ = [
    'DistributionTrackingStorage',
    'DistributionTrackingConfig',
    'DistributionEntry',
    'PerformanceSnapshot',
    'CrossPlatformAnalytics',
    'PlatformCredentials',
    'Platform',
    'DistributionStatus',
    'ContentFormat',
    'PerformanceMetric',
    'create_distribution_tracking_storage'
]