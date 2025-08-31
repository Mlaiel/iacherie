"""Multi-Platform Distribution Notification Manager

Gestionnaire spécialisé pour les notifications de distribution multi-plateformes
dans l'écosystème IA Influencer Agent. Orchestration distribution automatisée et monitoring.

Fonctionnalités:
- Distribution automatisée cross-platform intelligente
- Notifications statut publication et performance
- Optimisation timing et audience par plateforme
- Gestion erreurs et retry automatique
- Analytics distribution et ROI par canal

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Copyright © 2025 Fahed Mlaiel. Tous droits réservés.
AVERTISSEMENT LÉGAL STRICT:
Ce code constitue la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou tentative de reverse engineering
non autorisée par écrit est formellement interdite et passible de poursuites judiciaires
selon le droit allemand et international. Contact: mlaiel@live.de
"""from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
import asyncio
import logging
import json
import uuid
from decimal import Decimal
import aioredis
import asyncpg
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, DECIMAL, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, validator
import httpx
from jinja2 import Template
import hashlib
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)


class DistributionPlatform(Enum):
    """Plateformes de distribution supportées"""    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TIDAL = "tidal"
    PANDORA = "pandora"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    DISCORD = "discord"
    TWITCH = "twitch"


class ContentType(Enum):
    """Types de contenu distribués"""    SINGLE = "single"
    ALBUM = "album"
    EP = "ep"
    PODCAST = "podcast"
    VIDEO = "video"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    POST = "post"
    PLAYLIST = "playlist"
    REMIX = "remix"


class DistributionStatus(Enum):
    """États de distribution"""    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    LIVE = "live"
    FAILED = "failed"
    REJECTED = "rejected"
    TAKEN_DOWN = "taken_down"
    MONETIZED = "monetized"
    DEMONETIZED = "demonetized"


class OptimizationStrategy(Enum):
    """Stratégies d'optimisation de distribution"""    MAXIMIZE_REACH = "maximize_reach"
    MAXIMIZE_ENGAGEMENT = "maximize_engagement"
    MAXIMIZE_REVENUE = "maximize_revenue"
    BALANCED = "balanced"
    GEOGRAPHIC_TARGETING = "geographic_targeting"
    DEMOGRAPHIC_TARGETING = "demographic_targeting"
    TIME_OPTIMIZATION = "time_optimization"


@dataclass
class DistributionConfig:
    """Configuration de distribution pour une plateforme"""    platform: DistributionPlatform
    enabled: bool = True
    auto_publish: bool = False
    optimal_timing: bool = True
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    format_settings: Dict[str, Any] = field(default_factory=dict)
    monetization_enabled: bool = True
    audience_targeting: Dict[str, Any] = field(default_factory=dict)
    content_warnings: List[str] = field(default_factory=list)
    priority: int = 1  # 1=High, 2=Medium, 3=Low


@dataclass
class DistributionJob:
    """Job de distribution multi-plateformes"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = None
    content_id: str = None
    content_type: ContentType = ContentType.SINGLE
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    platforms: List[DistributionConfig] = field(default_factory=list)
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    scheduled_time: datetime = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime = None
    completed_at: datetime = None
    status: DistributionStatus = DistributionStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformPublication:
    """Publication sur une plateforme spécifique"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    distribution_job_id: str = None
    platform: DistributionPlatform = None
    platform_content_id: str = ""
    platform_url: str = ""
    status: DistributionStatus = DistributionStatus.PENDING
    upload_progress: float = 0.0
    published_at: datetime = None
    views: int = 0
    engagement_metrics: Dict[str, Any] = field(default_factory=dict)
    revenue_data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    retry_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistributionAnalytics:
    """Analytics de performance de distribution"""    distribution_job_id: str
    total_platforms: int = 0
    successful_publications: int = 0
    failed_publications: int = 0
    total_views: int = 0
    total_engagement: int = 0
    total_revenue: Decimal = field(default_factory=lambda: Decimal('0.00'))
    best_performing_platform: str = ""
    worst_performing_platform: str = ""
    optimization_score: float = 0.0
    roi_by_platform: Dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)


class MultiPlatformDistributionManager:
    """    Gestionnaire avancé de distribution multi-plateformes
    
    Responsabilités:
    - Orchestration distribution automatisée
    - Optimisation timing et contenu par plateforme
    - Monitoring et retry automatique
    - Analytics cross-platform et ROI
    - Notifications statut et performance
    """    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis):
        self.db_pool = db_pool
        self.redis = redis_client
        self.platform_apis = self._init_platform_apis()
        self.notification_templates = self._load_distribution_templates()
        self.optimization_models = self._init_optimization_models()
        
    def _init_platform_apis(self) -> Dict[str, Any]:
        """Initialise les APIs des plateformes de distribution"""        return {
            "spotify": {
                "api_url": "https://api.spotify.com/v1/",
                "upload_url": "https://partners.spotify.com/api/",
                "auth_type": "oauth2",
                "max_file_size": 500 * 1024 * 1024,  # 500MB
                "supported_formats": ["mp3", "flac", "wav"],
                "required_metadata": ["title", "artist", "album", "isrc"]
            },
            "youtube": {
                "api_url": "https://www.googleapis.com/youtube/v3/",
                "upload_url": "https://www.googleapis.com/upload/youtube/v3/",
                "auth_type": "oauth2", 
                "max_file_size": 256 * 1024 * 1024 * 1024,  # 256GB
                "supported_formats": ["mp4", "mov", "avi", "wmv", "flv"],
                "required_metadata": ["title", "description"]
            },
            "instagram": {
                "api_url": "https://graph.instagram.com/",
                "auth_type": "oauth2",
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "supported_formats": ["mp4", "jpg", "png"],
                "required_metadata": ["caption"]
            },
            "tiktok": {
                "api_url": "https://open-api.tiktok.com/platform/",
                "auth_type": "oauth2",
                "max_file_size": 500 * 1024 * 1024,  # 500MB
                "supported_formats": ["mp4"],
                "required_metadata": ["title", "description"]
            }
        }

    def _load_distribution_templates(self) -> Dict[str, Template]:
        """Charge les templates de notification de distribution"""        templates = {
            "distribution_started": Template("""                🚀 DISTRIBUTION LANCÉE
                
                🎵 Contenu: {{ content_title }}
                📊 Plateformes: {{ total_platforms }}
                ⏰ Démarrage: {{ start_time }}
                
                📈 Stratégie: {{ optimization_strategy }}
                🎯 Timing optimal: {{ optimal_timing }}
                
                🔄 Statut par plateforme:
                {{ platform_status | join('\n') }}
                
                📱 Suivre progression: {{ tracking_url }}
                
                ⚡ Notifications automatiques activées
            """),
            
            "platform_published": Template("""                ✅ PUBLIÉ SUR {{ platform.upper() }}!
                
                🎵 "{{ content_title }}"
                🔗 {{ platform_url }}
                
                📊 Statut: {{ status }}
                ⏰ Publié: {{ published_time }}
                👀 Vues initiales: {{ initial_views }}
                
                💡 Optimisations appliquées:
                {{ optimizations | join('\n• ') }}
                
                🎯 Prochaines étapes:
                {{ next_steps | join('\n• ') }}
                
                📈 Dashboard: {{ analytics_url }}
            """),
            
            "distribution_completed": Template("""                🏆 DISTRIBUTION TERMINÉE
                
                🎵 "{{ content_title }}"
                
                📊 Résultats:
                ✅ Succès: {{ successful_platforms }}/{{ total_platforms }}
                ❌ Échecs: {{ failed_platforms }}
                ⏱️ Durée: {{ total_duration }}
                
                🔥 Meilleures performances:
                {{ top_platforms | join('\n') }}
                
                💰 Potentiel revenus estimé:
                {{ revenue_estimates | join('\n') }}
                
                📈 Voir analytics complètes: {{ full_report_url }}
            """),
            
            "distribution_failed": Template("""                ⚠️ ÉCHEC DISTRIBUTION - {{ platform.upper() }}
                
                🎵 Contenu: {{ content_title }}
                ❌ Erreur: {{ error_message }}
                
                🔄 Tentatives: {{ retry_count }}/{{ max_retries }}
                ⏰ Prochaine tentative: {{ next_retry_time }}
                
                💡 Solutions possibles:
                {{ suggested_solutions | join('\n• ') }}
                
                🛠️ Action manuelle requise: {{ manual_action_required }}
                
                📞 Support: {{ support_contact }}
            """),
            
            "performance_alert": Template("""                📈 ALERTE PERFORMANCE - {{ alert_type.upper() }}
                
                🎵 Contenu: {{ content_title }}
                📊 Plateforme: {{ platform }}
                
                📈 Métrique: {{ metric_name }}
                🔥 Valeur actuelle: {{ current_value }}
                🎯 Seuil: {{ threshold_value }}
                
                {% if alert_type == 'viral' %}
                🚀 CONTENU VIRAL DÉTECTÉ!
                💡 Amplification recommandée sur d'autres plateformes
                {% elif alert_type == 'underperforming' %}
                📉 Performance en dessous des attentes
                💡 Optimisations suggérées disponibles
                {% endif %}
                
                🔧 Actions recommandées:
                {{ recommended_actions | join('\n• ') }}
                
                📊 Analytics: {{ dashboard_url }}
            """),
            
            "optimization_suggestion": Template("""                💡 OPTIMISATION INTELLIGENTE DISPONIBLE
                
                🎵 Contenu: {{ content_title }}
                🎯 Opportunité: {{ optimization_type }}
                
                📊 Analyse IA:
                {{ ai_analysis }}
                
                🚀 Améliorations suggérées:
                {{ suggestions | join('\n• ') }}
                
                📈 Impact estimé:
                {{ impact_estimates | join('\n• ') }}
                
                ⚡ Appliquer automatiquement: {{ auto_apply_url }}
                🔧 Configurer manuellement: {{ manual_config_url }}
            """)
        }
        
        return templates

    def _init_optimization_models(self) -> Dict[str, Any]:
        """Initialise les modèles d'optimisation IA"""        return {
            "timing_optimizer": None,  # Modèle ML pour timing optimal
            "audience_matcher": None,  # Modèle pour matching audience
            "content_optimizer": None,  # Modèle pour optimisation contenu
            "performance_predictor": None  # Modèle prédiction performance
        }

    async def create_distribution_job(
        self,
        user_id: str,
        content_data: Dict[str, Any],
        distribution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Crée et lance un job de distribution multi-plateformes
        
        Args:
            user_id: ID de l'utilisateur
            content_data: Données du contenu à distribuer
            distribution_config: Configuration de distribution
            
        Returns:
            Dict contenant les résultats de la création du job
        """        try:
            # Validation du contenu
            validated_content = await self._validate_content_data(content_data)
            
            # Création du job de distribution
            distribution_job = DistributionJob(
                user_id=user_id,
                content_id=validated_content.get("content_id"),
                content_type=ContentType(validated_content.get("content_type", "single")),
                title=validated_content.get("title", ""),
                description=validated_content.get("description", ""),
                tags=validated_content.get("tags", []),
                optimization_strategy=OptimizationStrategy(
                    distribution_config.get("strategy", "balanced")
                ),
                scheduled_time=distribution_config.get("scheduled_time")
            )
            
            # Configuration des plateformes
            platform_configs = []
            for platform_config in distribution_config.get("platforms", []):
                config = DistributionConfig(
                    platform=DistributionPlatform(platform_config["platform"]),
                    enabled=platform_config.get("enabled", True),
                    auto_publish=platform_config.get("auto_publish", False),
                    optimal_timing=platform_config.get("optimal_timing", True),
                    custom_metadata=platform_config.get("metadata", {}),
                    monetization_enabled=platform_config.get("monetization", True),
                    audience_targeting=platform_config.get("targeting", {}),
                    priority=platform_config.get("priority", 1)
                )
                platform_configs.append(config)
            
            distribution_job.platforms = platform_configs
            
            # Optimisation intelligente
            if distribution_job.optimization_strategy != OptimizationStrategy.BALANCED:
                optimized_config = await self._optimize_distribution_config(
                    user_id, distribution_job
                )
                distribution_job.platforms = optimized_config
            
            # Sauvegarde du job
            job_id = await self._save_distribution_job(distribution_job)
            
            # Programmation ou lancement immédiat
            if distribution_job.scheduled_time:
                await self._schedule_distribution_job(distribution_job)
                status = "scheduled"
            else:
                await self._start_distribution_job(distribution_job)
                status = "started"
            
            # Notification de démarrage
            await self._send_distribution_notification(
                distribution_job, "distribution_started"
            )
            
            logger.info(f"Job de distribution {job_id} créé pour utilisateur {user_id}")
            
            return {
                "job_id": job_id,
                "status": status,
                "platforms_configured": len(platform_configs),
                "estimated_completion": await self._estimate_completion_time(distribution_job),
                "tracking_url": f"https://dashboard.ia-influencer.de/distribution/{job_id}"
            }
            
        except Exception as e:
            logger.error(f"Erreur création job distribution: {str(e)}")
            raise

    async def monitor_distribution_job(self, job_id: str) -> Dict[str, Any]:
        """Surveille et met à jour un job de distribution en cours"""        async with self.db_pool.acquire() as conn:
            # Récupération du job
            job_data = await conn.fetchrow("""                SELECT * FROM distribution_jobs 
                WHERE id = $1
            """, job_id)
            
            if not job_data:
                raise ValueError(f"Job {job_id} non trouvé")
            
            # Récupération des publications par plateforme
            publications = await conn.fetch("""                SELECT * FROM platform_publications 
                WHERE distribution_job_id = $1
                ORDER BY created_at
            """, job_id)
            
            # Mise à jour du statut de chaque publication
            updated_publications = []
            overall_status = DistributionStatus.PROCESSING
            
            for pub in publications:
                updated_pub = await self._update_publication_status(dict(pub))
                updated_publications.append(updated_pub)
                
                # Notifications si changement de statut
                if updated_pub["status"] != pub["status"]:
                    await self._send_platform_notification(updated_pub)
            
            # Calcul du statut global
            statuses = [pub["status"] for pub in updated_publications]
            
            if all(s in ["published", "live", "monetized"] for s in statuses):
                overall_status = DistributionStatus.PUBLISHED
                
                # Job terminé - notification finale et analytics
                await self._finalize_distribution_job(job_id, updated_publications)
                
            elif any(s == "failed" for s in statuses):
                # Vérification si retry possible
                failed_pubs = [p for p in updated_publications if p["status"] == "failed"]
                for failed_pub in failed_pubs:
                    if failed_pub["retry_count"] < 3:
                        await self._retry_failed_publication(failed_pub)
            
            # Mise à jour statut global
            await conn.execute("""                UPDATE distribution_jobs 
                SET status = $1, last_updated = NOW()
                WHERE id = $2
            """, overall_status.value, job_id)
            
            return {
                "job_id": job_id,
                "overall_status": overall_status.value,
                "publications": updated_publications,
                "completion_percentage": await self._calculate_completion_percentage(updated_publications),
                "estimated_remaining_time": await self._estimate_remaining_time(updated_publications)
            }

    async def get_distribution_analytics(
        self,
        user_id: str,
        period_start: datetime = None,
        period_end: datetime = None
    ) -> Dict[str, Any]:
        """Récupère les analytics de distribution pour un utilisateur"""        period_start = period_start or (datetime.now() - timedelta(days=30))
        period_end = period_end or datetime.now()
        
        async with self.db_pool.acquire() as conn:
            # Jobs de distribution dans la période
            distribution_jobs = await conn.fetch("""                SELECT 
                    dj.*,
                    COUNT(pp.id) as total_publications,
                    COUNT(pp.id) FILTER (WHERE pp.status IN ('published', 'live')) as successful_publications,
                    COUNT(pp.id) FILTER (WHERE pp.status = 'failed') as failed_publications,
                    SUM(pp.views) as total_views,
                    SUM((pp.engagement_metrics->>'likes')::int) as total_likes,
                    SUM((pp.revenue_data->>'amount')::decimal) as total_revenue
                FROM distribution_jobs dj
                LEFT JOIN platform_publications pp ON dj.id = pp.distribution_job_id
                WHERE dj.user_id = $1 
                AND dj.created_at BETWEEN $2 AND $3
                GROUP BY dj.id
                ORDER BY dj.created_at DESC
            """, user_id, period_start, period_end)
            
            # Performance par plateforme
            platform_performance = await conn.fetch("""                SELECT 
                    pp.platform,
                    COUNT(*) as total_publications,
                    COUNT(*) FILTER (WHERE pp.status IN ('published', 'live')) as successful,
                    AVG(pp.views) as avg_views,
                    SUM((pp.revenue_data->>'amount')::decimal) as total_revenue,
                    AVG((pp.engagement_metrics->>'engagement_rate')::float) as avg_engagement
                FROM platform_publications pp
                JOIN distribution_jobs dj ON pp.distribution_job_id = dj.id
                WHERE dj.user_id = $1 
                AND pp.published_at BETWEEN $2 AND $3
                GROUP BY pp.platform
                ORDER BY total_revenue DESC
            """, user_id, period_start, period_end)
            
            # Tendances temporelles
            temporal_trends = await conn.fetch("""                SELECT 
                    DATE_TRUNC('day', pp.published_at) as day,
                    COUNT(*) as publications_count,
                    SUM(pp.views) as daily_views,
                    SUM((pp.revenue_data->>'amount')::decimal) as daily_revenue
                FROM platform_publications pp
                JOIN distribution_jobs dj ON pp.distribution_job_id = dj.id
                WHERE dj.user_id = $1 
                AND pp.published_at BETWEEN $2 AND $3
                GROUP BY day
                ORDER BY day
            """, user_id, period_start, period_end)
            
            # Calculs analytiques
            total_jobs = len(distribution_jobs)
            success_rate = sum(1 for job in distribution_jobs 
                             if job['successful_publications'] > 0) / total_jobs if total_jobs > 0 else 0
            
            # ROI par plateforme
            roi_by_platform = {}
            for platform in platform_performance:
                if platform['total_revenue'] and platform['total_publications']:
                    roi_by_platform[platform['platform']] = float(
                        platform['total_revenue'] / platform['total_publications']
                    )
            
            # Recommandations d'optimisation
            optimization_recommendations = await self._generate_optimization_recommendations(
                user_id, distribution_jobs, platform_performance
            )
            
            return {
                "period": {
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat()
                },
                "summary": {
                    "total_distributions": total_jobs,
                    "success_rate": success_rate,
                    "total_publications": sum(job['total_publications'] or 0 for job in distribution_jobs),
                    "total_views": sum(job['total_views'] or 0 for job in distribution_jobs),
                    "total_revenue": float(sum(job['total_revenue'] or 0 for job in distribution_jobs))
                },
                "platform_performance": [dict(p) for p in platform_performance],
                "temporal_trends": [dict(t) for t in temporal_trends],
                "roi_by_platform": roi_by_platform,
                "optimization_recommendations": optimization_recommendations,
                "generated_at": datetime.now().isoformat()
            }

    async def optimize_distribution_strategy(
        self,
        user_id: str,
        content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimise la stratégie de distribution basée sur l'analyse IA"""        try:
            # Analyse historique de performance
            historical_performance = await self._analyze_historical_performance(user_id)
            
            # Analyse du contenu pour matching optimal
            content_insights = await self._analyze_content_for_distribution(content_analysis)
            
            # Prédictions de performance par plateforme
            platform_predictions = await self._predict_platform_performance(
                user_id, content_insights, historical_performance
            )
            
            # Optimisation timing
            optimal_timing = await self._optimize_publication_timing(
                user_id, platform_predictions
            )
            
            # Recommandations de ciblage audience
            audience_targeting = await self._recommend_audience_targeting(
                user_id, content_insights
            )
            
            # Génération de la stratégie optimisée
            optimized_strategy = {
                "recommended_platforms": sorted(
                    platform_predictions.items(),
                    key=lambda x: x[1]["predicted_performance"],
                    reverse=True
                )[:5],  # Top 5 plateformes
                "optimal_timing": optimal_timing,
                "audience_targeting": audience_targeting,
                "content_optimizations": content_insights["optimizations"],
                "expected_roi": await self._calculate_expected_roi(platform_predictions),
                "confidence_score": await self._calculate_strategy_confidence(
                    historical_performance, platform_predictions
                )
            }
            
            # Sauvegarde de la stratégie optimisée
            strategy_id = await self._save_optimization_strategy(user_id, optimized_strategy)
            
            logger.info(f"Stratégie optimisée générée pour utilisateur {user_id}")
            
            return {
                "strategy_id": strategy_id,
                "optimized_strategy": optimized_strategy,
                "implementation_guide": await self._generate_implementation_guide(optimized_strategy),
                "monitoring_setup": await self._setup_strategy_monitoring(user_id, optimized_strategy)
            }
            
        except Exception as e:
            logger.error(f"Erreur optimisation stratégie: {str(e)}")
            raise

    # Méthodes utilitaires privées
    async def _validate_content_data(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les données de contenu pour distribution"""        required_fields = ["title", "content_type", "file_url"]
        
        for field in required_fields:
            if field not in content_data:
                raise ValueError(f"Champ requis manquant: {field}")
        
        # Validation du type de contenu
        if content_data["content_type"] not in [ct.value for ct in ContentType]:
            raise ValueError(f"Type de contenu non supporté: {content_data['content_type']}")
        
        # Validation du fichier
        file_validation = await self._validate_content_file(content_data["file_url"])
        content_data.update(file_validation)
        
        return content_data

    async def _start_distribution_job(self, job: DistributionJob) -> None:
        """Lance l'exécution d'un job de distribution"""        job.status = DistributionStatus.PROCESSING
        job.started_at = datetime.now()
        
        # Création des publications pour chaque plateforme
        publication_tasks = []
        
        for platform_config in job.platforms:
            if platform_config.enabled:
                task = self._create_platform_publication(job, platform_config)
                publication_tasks.append(task)
        
        # Lancement parallèle des publications
        await asyncio.gather(*publication_tasks, return_exceptions=True)

    async def _create_platform_publication(
        self,
        job: DistributionJob,
        platform_config: DistributionConfig
    ) -> PlatformPublication:
        """Crée et lance une publication sur une plateforme spécifique"""        publication = PlatformPublication(
            distribution_job_id=job.id,
            platform=platform_config.platform,
            status=DistributionStatus.QUEUED
        )
        
        try:
            # Optimisation contenu pour la plateforme
            optimized_content = await self._optimize_content_for_platform(
                job, platform_config
            )
            
            # Upload et publication via API plateforme
            upload_result = await self._upload_to_platform(
                platform_config.platform, optimized_content
            )
            
            publication.platform_content_id = upload_result["content_id"]
            publication.platform_url = upload_result["url"]
            publication.status = DistributionStatus.PUBLISHED
            publication.published_at = datetime.now()
            
            # Sauvegarde en base
            await self._save_platform_publication(publication)
            
            logger.info(f"Publication réussie sur {platform_config.platform.value}")
            
        except Exception as e:
            publication.status = DistributionStatus.FAILED
            publication.error_message = str(e)
            logger.error(f"Échec publication {platform_config.platform.value}: {str(e)}")
        
        return publication

    async def _optimize_content_for_platform(
        self,
        job: DistributionJob,
        platform_config: DistributionConfig
    ) -> Dict[str, Any]:
        """Optimise le contenu pour une plateforme spécifique"""        platform_specs = self.platform_apis[platform_config.platform.value]
        
        optimized_content = {
            "title": job.title,
            "description": job.description,
            "tags": job.tags,
            "file_url": job.metadata.get("file_url"),
            "platform_specific": {}
        }
        
        # Optimisations spécifiques par plateforme
        if platform_config.platform == DistributionPlatform.YOUTUBE:
            optimized_content["platform_specific"] = {
                "thumbnail": await self._generate_thumbnail(job.metadata.get("artwork_url")),
                "category": "Music",
                "language": "fr",
                "monetization": platform_config.monetization_enabled
            }
        elif platform_config.platform == DistributionPlatform.INSTAGRAM:
            optimized_content["platform_specific"] = {
                "aspect_ratio": "1:1",
                "story_format": True if job.content_type == ContentType.STORY else False,
                "hashtags": await self._generate_hashtags(job.tags)
            }
        elif platform_config.platform == DistributionPlatform.TIKTOK:
            optimized_content["platform_specific"] = {
                "format": "vertical",
                "effects": await self._suggest_tiktok_effects(job.metadata),
                "trending_sounds": await self._get_trending_sounds()
            }
        
        return optimized_content


# Export des classes principales
__all__ = [
    "MultiPlatformDistributionManager",
    "DistributionJob",
    "PlatformPublication",
    "DistributionConfig",
    "DistributionAnalytics",
    "DistributionPlatform",
    "ContentType",
    "DistributionStatus",
    "OptimizationStrategy"
]
