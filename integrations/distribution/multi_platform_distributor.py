"""
Multi-Platform Distributor - Distribution Module
===============================================
Système de distribution enterprise pour 65+ plateformes avec
optimization intelligente et gestion API automatisée.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class PlatformCategory(Enum):
    """Catégories de plateformes."""
    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_STREAMING = "video_streaming"
    CREATOR_ECONOMY = "creator_economy"
    E_COMMERCE = "e_commerce"
    PODCAST = "podcast"
    BLOG = "blog"

class ContentFormat(Enum):
    """Formats de contenu supportés."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    LIVE_STREAM = "live_stream"

class DistributionStatus(Enum):
    """Statuts de distribution."""
    QUEUED = "queued"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"

@dataclass
class PlatformConfig:
    """Configuration d'une plateforme."""
    platform_id: str
    name: str
    category: PlatformCategory
    supported_formats: List[ContentFormat]
    api_config: Dict[str, Any]
    rate_limits: Dict[str, int]
    optimal_timing: List[str]
    metadata_requirements: Dict[str, Any]
    monetization_features: List[str]

@dataclass
class ContentPackage:
    """Package de contenu à distribuer."""
    package_id: str
    title: str
    description: str
    content_files: Dict[ContentFormat, str]  # format -> file_path
    metadata: Dict[str, Any]
    tags: List[str]
    target_audience: Dict[str, Any]
    monetization_settings: Dict[str, Any]

@dataclass
class DistributionJob:
    """Job de distribution multi-plateformes."""
    job_id: str
    content_package: ContentPackage
    target_platforms: List[str]
    distribution_strategy: str
    status: DistributionStatus
    created_at: datetime
    scheduled_at: Optional[datetime]
    completed_at: Optional[datetime]
    platform_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    success_count: int = 0
    failure_count: int = 0

class MultiPlatformDistributor:
    """
    Distributeur multi-plateformes enterprise.
    Gestion simultanée de 65+ plateformes avec optimization.
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        """Initialise le distributeur multi-plateformes."""
        self.config = config or {}
        self.platform_configs: Dict[str, PlatformConfig] = {}
        self.active_jobs: Dict[str, DistributionJob] = {}
        self.api_clients: Dict[str, Any] = {}
        self.executor = ThreadPoolExecutor(max_workers=20)
        self._initialize_platforms()
        logger.info("Multi-Platform Distributor initialisé avec 65+ plateformes")
    
    def _initialize_platforms(self) -> None:
        """Initialise les configurations des 65+ plateformes."""
        
        # Social Media Platforms (29)
        social_platforms = [
            "instagram", "tiktok", "youtube", "facebook", "twitter", "linkedin",
            "snapchat", "pinterest", "threads", "bereal", "mastodon", "bluesky",
            "discord", "reddit", "clubhouse", "twitch", "kick", "vimeo",
            "dailymotion", "rumble", "weibo", "line", "kakaotalk", "vk",
            "qq", "wechat", "telegram", "whatsapp_business", "nostr"
        ]
        
        # Music Streaming Platforms (20)  
        music_platforms = [
            "spotify", "apple_music", "youtube_music", "amazon_music", "deezer",
            "tidal", "pandora", "iheart_radio", "soundcloud", "bandcamp",
            "audiomack", "mixcloud", "spotify_podcasts", "apple_podcasts",
            "google_podcasts", "anchor", "distrokid", "cd_baby", "tunecore", "landr"
        ]
        
        # Creator Economy Platforms (16)
        creator_platforms = [
            "onlyfans", "patreon", "ko_fi", "buy_me_coffee", "gumroad", "etsy",
            "opensea", "foundation", "superrare", "async_art", "known_origin",
            "onlyfans_live", "cam4", "chaturbate", "fiverr", "upwork"
        ]
        
        # Initialiser toutes les plateformes
        all_platforms = social_platforms + music_platforms + creator_platforms
        
        for platform_id in all_platforms:
            self.platform_configs[platform_id] = self._create_platform_config(platform_id)
        
        logger.info(f"Initialisé {len(all_platforms)} plateformes")
    
    def _create_platform_config(self, platform_id: str) -> PlatformConfig:
        """Crée la configuration d'une plateforme."""
        
        # Configurations par catégorie
        platform_data = {
            # Social Media
            "instagram": {
                "category": PlatformCategory.SOCIAL_MEDIA,
                "formats": [ContentFormat.IMAGE, ContentFormat.VIDEO],
                "rate_limits": {"posts": 25, "stories": 100},
                "optimal_timing": ["9:00", "13:00", "17:00"],
                "monetization": ["sponsored_posts", "affiliate", "shop"]
            },
            "tiktok": {
                "category": PlatformCategory.SOCIAL_MEDIA,
                "formats": [ContentFormat.VIDEO],
                "rate_limits": {"posts": 10, "comments": 50},
                "optimal_timing": ["6:00", "10:00", "19:00"],
                "monetization": ["creator_fund", "live_gifts", "brand_partnerships"]
            },
            "youtube": {
                "category": PlatformCategory.VIDEO_STREAMING,
                "formats": [ContentFormat.VIDEO, ContentFormat.LIVE_STREAM],
                "rate_limits": {"uploads": 6, "api_calls": 10000},
                "optimal_timing": ["14:00", "15:00", "16:00"],
                "monetization": ["ads", "memberships", "super_chat", "merchandise"]
            },
            
            # Music Streaming
            "spotify": {
                "category": PlatformCategory.MUSIC_STREAMING,
                "formats": [ContentFormat.AUDIO],
                "rate_limits": {"api_calls": 1000},
                "optimal_timing": ["00:00"],  # Release timing
                "monetization": ["streaming_royalties", "playlist_placement"]
            },
            "apple_music": {
                "category": PlatformCategory.MUSIC_STREAMING,
                "formats": [ContentFormat.AUDIO, ContentFormat.VIDEO],
                "rate_limits": {"api_calls": 500},
                "optimal_timing": ["00:00"],
                "monetization": ["streaming_royalties", "editorial_features"]
            },
            
            # Creator Economy
            "patreon": {
                "category": PlatformCategory.CREATOR_ECONOMY,
                "formats": [ContentFormat.VIDEO, ContentFormat.AUDIO, ContentFormat.IMAGE, ContentFormat.TEXT],
                "rate_limits": {"posts": 50},
                "optimal_timing": ["10:00", "15:00", "20:00"],
                "monetization": ["subscriptions", "tips", "exclusive_content"]
            },
            "gumroad": {
                "category": PlatformCategory.E_COMMERCE,
                "formats": [ContentFormat.DOCUMENT, ContentFormat.VIDEO, ContentFormat.AUDIO],
                "rate_limits": {"products": 100},
                "optimal_timing": ["12:00", "18:00"],
                "monetization": ["direct_sales", "bundles", "discounts"]
            }
        }
        
        # Configuration par défaut si plateforme pas définie
        default_config = {
            "category": PlatformCategory.SOCIAL_MEDIA,
            "formats": [ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.TEXT],
            "rate_limits": {"posts": 20, "api_calls": 1000},
            "optimal_timing": ["12:00", "18:00"],
            "monetization": ["basic"]
        }
        
        config_data = platform_data.get(platform_id, default_config)
        
        return PlatformConfig(
            platform_id=platform_id,
            name=platform_id.replace("_", " ").title(),
            category=config_data["category"],
            supported_formats=config_data["formats"],
            api_config={"base_url": f"https://api.{platform_id}.com"},
            rate_limits=config_data["rate_limits"],
            optimal_timing=config_data["optimal_timing"],
            metadata_requirements=self._get_metadata_requirements(platform_id),
            monetization_features=config_data["monetization"]
        )
    
    def _get_metadata_requirements(self, platform_id: str) -> Dict[str, Any]:
        """Retourne les exigences metadata par plateforme."""
        requirements = {
            "instagram": {
                "required": ["caption"],
                "optional": ["hashtags", "location", "alt_text"],
                "limits": {"caption": 2200, "hashtags": 30}
            },
            "youtube": {
                "required": ["title", "description"],
                "optional": ["tags", "thumbnail", "category", "playlist"],
                "limits": {"title": 100, "description": 5000, "tags": 500}
            },
            "spotify": {
                "required": ["track_name", "artist_name"],
                "optional": ["album_name", "genre", "mood", "isrc"],
                "limits": {"track_name": 100, "artist_name": 50}
            },
            "tiktok": {
                "required": ["description"],
                "optional": ["hashtags", "mentions", "sounds"],
                "limits": {"description": 150, "hashtags": 20}
            }
        }
        
        return requirements.get(platform_id, {
            "required": ["title"],
            "optional": ["description", "tags"],
            "limits": {"title": 100, "description": 1000}
        })
    
    async def distribute_content(
        self,
        content_package: ContentPackage,
        target_platforms: List[str],
        distribution_strategy: str = "simultaneous",
        scheduled_time: Optional[datetime] = None
    ) -> DistributionJob:
        """Distribue du contenu sur les plateformes sélectionnées."""
        
        job_id = str(uuid.uuid4())
        
        # Valider plateformes
        valid_platforms = [p for p in target_platforms if p in self.platform_configs]
        if len(valid_platforms) != len(target_platforms):
            invalid = set(target_platforms) - set(valid_platforms)
            logger.warning(f"Plateformes invalides ignorées: {invalid}")
        
        # Créer job de distribution
        job = DistributionJob(
            job_id=job_id,
            content_package=content_package,
            target_platforms=valid_platforms,
            distribution_strategy=distribution_strategy,
            status=DistributionStatus.QUEUED,
            created_at=datetime.now(),
            scheduled_at=scheduled_time
        )
        
        self.active_jobs[job_id] = job
        
        # Démarrer distribution
        if scheduled_time is None or scheduled_time <= datetime.now():
            asyncio.create_task(self._execute_distribution(job_id))
        else:
            asyncio.create_task(self._schedule_distribution(job_id, scheduled_time))
        
        logger.info(f"Distribution job créé: {job_id} pour {len(valid_platforms)} plateformes")
        return job
    
    async def _execute_distribution(self, job_id -> None: str) -> None:
        """Exécute la distribution d'un job."""
        if job_id not in self.active_jobs:
            return
        
        job = self.active_jobs[job_id]
        job.status = DistributionStatus.PROCESSING
        
        try:
            if job.distribution_strategy == "simultaneous":
                await self._distribute_simultaneous(job)
            elif job.distribution_strategy == "sequential":
                await self._distribute_sequential(job)
            elif job.distribution_strategy == "intelligent_sequential":
                await self._distribute_intelligent_sequential(job)
            else:
                await self._distribute_simultaneous(job)  # Défaut
            
            # Finaliser job
            job.completed_at = datetime.now()
            if job.failure_count == 0:
                job.status = DistributionStatus.COMPLETED
            elif job.success_count > 0:
                job.status = DistributionStatus.PARTIALLY_COMPLETED
            else:
                job.status = DistributionStatus.FAILED
                
            logger.info(f"Distribution terminée: {job_id} - {job.success_count} succès, {job.failure_count} échecs")
            
        except Exception as e:
            job.status = DistributionStatus.FAILED
            logger.error(f"Erreur distribution {job_id}: {e}")
    
    async def _distribute_simultaneous(self, job -> None: DistributionJob) -> None:
        """Distribution simultanée sur toutes les plateformes."""
        job.status = DistributionStatus.UPLOADING
        
        # Créer tâches parallèles
        tasks = []
        for platform_id in job.target_platforms:
            task = self._distribute_to_platform(job, platform_id)
            tasks.append(task)
        
        # Exécuter en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traiter résultats
        for i, result in enumerate(results):
            platform_id = job.target_platforms[i]
            if isinstance(result, Exception):
                job.platform_results[platform_id] = {
                    "status": "failed",
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                }
                job.failure_count += 1
            else:
                job.platform_results[platform_id] = result
                if result.get("status") == "success":
                    job.success_count += 1
                else:
                    job.failure_count += 1
    
    async def _distribute_sequential(self, job -> None: DistributionJob) -> None:
        """Distribution séquentielle sur les plateformes."""
        job.status = DistributionStatus.UPLOADING
        
        for platform_id in job.target_platforms:
            try:
                result = await self._distribute_to_platform(job, platform_id)
                job.platform_results[platform_id] = result
                
                if result.get("status") == "success":
                    job.success_count += 1
                else:
                    job.failure_count += 1
                    
                # Pause entre plateformes
                await asyncio.sleep(2)
                
            except Exception as e:
                job.platform_results[platform_id] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                job.failure_count += 1
    
    async def _distribute_intelligent_sequential(self, job -> None: DistributionJob) -> None:
        """Distribution séquentielle intelligente basée sur priorités."""
        job.status = DistributionStatus.UPLOADING
        
        # Trier plateformes par priorité
        prioritized_platforms = self._prioritize_platforms(
            job.target_platforms, job.content_package
        )
        
        for platform_id in prioritized_platforms:
            try:
                result = await self._distribute_to_platform(job, platform_id)
                job.platform_results[platform_id] = result
                
                if result.get("status") == "success":
                    job.success_count += 1
                else:
                    job.failure_count += 1
                
                # Pause intelligente basée sur plateforme
                delay = self._calculate_intelligent_delay(platform_id)
                await asyncio.sleep(delay)
                
            except Exception as e:
                job.platform_results[platform_id] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                job.failure_count += 1
    
    async def _distribute_to_platform(
        self, job: DistributionJob, platform_id: str
    ) -> Dict[str, Any]:
        """Distribue le contenu sur une plateforme spécifique."""
        
        platform_config = self.platform_configs[platform_id]
        content = job.content_package
        
        # Vérifier format supporté
        available_formats = set(content.content_files.keys())
        supported_formats = set(platform_config.supported_formats)
        compatible_formats = available_formats.intersection(supported_formats)
        
        if not compatible_formats:
            return {
                "status": "failed",
                "error": f"Aucun format compatible pour {platform_id}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Sélectionner meilleur format
        best_format = self._select_best_format(compatible_formats, platform_config)
        content_file = content.content_files[best_format]
        
        # Optimiser metadata pour la plateforme
        optimized_metadata = await self._optimize_metadata_for_platform(
            content.metadata, platform_config
        )
        
        # Simulation upload (en production = vraie API)
        try:
            upload_result = await self._simulate_platform_upload(
                platform_id, content_file, optimized_metadata
            )
            
            return {
                "status": "success",
                "platform_id": platform_id,
                "format_used": best_format.value,
                "content_url": upload_result.get("url"),
                "platform_post_id": upload_result.get("post_id"),
                "metadata_used": optimized_metadata,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "platform_id": platform_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _prioritize_platforms(
        self, platforms: List[str], content: ContentPackage
    ) -> List[str]:
        """Priorise les plateformes selon le contenu et stratégie."""
        
        # Facteurs de priorité
        priority_scores = {}
        
        for platform_id in platforms:
            config = self.platform_configs[platform_id]
            score = 0
            
            # Score basé sur catégorie de plateforme
            if config.category == PlatformCategory.SOCIAL_MEDIA:
                score += 100  # Priorité haute pour social
            elif config.category == PlatformCategory.MUSIC_STREAMING:
                score += 90
            elif config.category == PlatformCategory.CREATOR_ECONOMY:
                score += 80
            
            # Score basé sur compatibilité format
            available_formats = set(content.content_files.keys())
            supported_formats = set(config.supported_formats)
            compatibility = len(available_formats.intersection(supported_formats))
            score += compatibility * 20
            
            # Score basé sur features de monétisation
            monetization_score = len(config.monetization_features) * 5
            score += monetization_score
            
            priority_scores[platform_id] = score
        
        # Trier par score décroissant
        return sorted(platforms, key=lambda p: priority_scores[p], reverse=True)
    
    def _select_best_format(
        self, compatible_formats: Set[ContentFormat], platform_config: PlatformConfig
    ) -> ContentFormat:
        """Sélectionne le meilleur format pour une plateforme."""
        
        # Priorité des formats par plateforme
        format_priority = {
            ContentFormat.VIDEO: 100,
            ContentFormat.AUDIO: 90,
            ContentFormat.IMAGE: 80,
            ContentFormat.TEXT: 70,
            ContentFormat.DOCUMENT: 60,
            ContentFormat.LIVE_STREAM: 50
        }
        
        # Ajustements par catégorie de plateforme
        if platform_config.category == PlatformCategory.MUSIC_STREAMING:
            format_priority[ContentFormat.AUDIO] = 120
        elif platform_config.category == PlatformCategory.VIDEO_STREAMING:
            format_priority[ContentFormat.VIDEO] = 120
        
        # Sélectionner format avec score le plus élevé
        best_format = max(compatible_formats, key=lambda f: format_priority.get(f, 0))
        return best_format
    
    async def _optimize_metadata_for_platform(
        self, base_metadata: Dict[str, Any], platform_config: PlatformConfig
    ) -> Dict[str, Any]:
        """Optimise les metadata pour une plateforme spécifique."""
        
        optimized = base_metadata.copy()
        requirements = platform_config.metadata_requirements
        
        # Appliquer limites de caractères
        limits = requirements.get("limits", {})
        for field, limit in limits.items():
            if field in optimized and isinstance(optimized[field], str):
                optimized[field] = optimized[field][:limit]
        
        # Ajouter champs requis manquants
        required_fields = requirements.get("required", [])
        for field in required_fields:
            if field not in optimized:
                optimized[field] = self._generate_default_value(field, base_metadata)
        
        # Optimizations spécifiques par plateforme
        platform_id = platform_config.platform_id
        
        if platform_id == "instagram":
            # Optimiser hashtags pour Instagram
            if "hashtags" in optimized:
                hashtags = optimized["hashtags"][:30]  # Max 30 hashtags
                optimized["hashtags"] = hashtags
        
        elif platform_id == "youtube":
            # Optimiser pour YouTube SEO
            if "title" in optimized:
                title = optimized["title"]
                if len(title) > 60:  # Optimal pour thumbnail
                    optimized["title"] = title[:57] + "..."
        
        elif platform_id == "tiktok":
            # Optimiser pour TikTok trends
            if "description" in optimized:
                description = optimized["description"][:150]  # Limite TikTok
                optimized["description"] = description
        
        return optimized
    
    def _generate_default_value(self, field: str, base_metadata: Dict[str, Any]) -> str:
        """Génère une valeur par défaut pour un champ requis."""
        
        defaults = {
            "title": base_metadata.get("title", "Untitled Content"),
            "description": base_metadata.get("description", ""),
            "caption": base_metadata.get("description", ""),
            "track_name": base_metadata.get("title", "Untitled Track"),
            "artist_name": base_metadata.get("artist", "Unknown Artist")
        }
        
        return defaults.get(field, "")
    
    def _calculate_intelligent_delay(self, platform_id: str) -> float:
        """Calcule le délai intelligent entre publications."""
        
        # Délais basés sur type de plateforme
        delays = {
            "instagram": 30,  # 30 secondes
            "tiktok": 45,     # 45 secondes  
            "youtube": 120,   # 2 minutes
            "spotify": 300,   # 5 minutes
            "twitter": 15,    # 15 secondes
            "linkedin": 60,   # 1 minute
        }
        
        return delays.get(platform_id, 30)  # Défaut 30 secondes
    
    async def _simulate_platform_upload(
        self, platform_id: str, content_file: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simule l'upload sur une plateforme (remplacer par vraie API)."""
        
        # Simulation délai upload
        await asyncio.sleep(2 + hash(platform_id) % 3)  # 2-5 secondes
        
        # Simulation succès/échec (95% succès)
        import random
        if random.random() < 0.95:
            post_id = f"{platform_id}_{uuid.uuid4().hex[:8]}"
            url = f"https://{platform_id}.com/post/{post_id}"
            
            return {
                "success": True,
                "post_id": post_id,
                "url": url,
                "uploaded_at": datetime.now().isoformat()
            }
        else:
            raise Exception(f"Upload failed on {platform_id}")
    
    async def _schedule_distribution(self, job_id -> None: str, scheduled_time -> None: datetime) -> None:
        """Planifie une distribution pour plus tard."""
        
        wait_seconds = (scheduled_time - datetime.now()).total_seconds()
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)
            await self._execute_distribution(job_id)
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retourne le statut d'un job de distribution."""
        
        if job_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job_id,
            "status": job.status.value,
            "progress": {
                "total_platforms": len(job.target_platforms),
                "completed": job.success_count + job.failure_count,
                "successful": job.success_count,
                "failed": job.failure_count
            },
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "platform_results": job.platform_results
        }
    
    async def get_platform_analytics(self) -> Dict[str, Any]:
        """Retourne analytics des plateformes."""
        
        total_platforms = len(self.platform_configs)
        
        # Répartition par catégorie
        category_distribution = {}
        for config in self.platform_configs.values():
            category = config.category.value
            category_distribution[category] = category_distribution.get(category, 0) + 1
        
        # Plateformes populaires (simulation)
        popular_platforms = ["instagram", "youtube", "tiktok", "spotify", "twitter"]
        
        return {
            "total_platforms": total_platforms,
            "category_distribution": category_distribution,
            "popular_platforms": popular_platforms,
            "supported_formats": [f.value for f in ContentFormat],
            "active_jobs": len(self.active_jobs),
            "distribution_strategies": ["simultaneous", "sequential", "intelligent_sequential"]
        }