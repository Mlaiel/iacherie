"""
Distribution Retry Engine - Ainflue
==================================
Retry spécialisé pour distribution multi-plateformes.
Platform API retry + SEO + social media posting patterns.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Retry Mechanisms
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture retry mechanisms et tous ses algorithmes sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import time
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Types de plateformes supportées"""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    TWITCH = "twitch"
    DISCORD = "discord"

class ContentType(Enum):
    """Types de contenu à distribuer"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    POST = "post"
    PODCAST = "podcast"
    ALBUM = "album"
    SINGLE = "single"

class DistributionStrategy(Enum):
    """Stratégies de distribution"""
    SIMULTANEOUS = "simultaneous"
    SEQUENTIAL = "sequential"
    PRIORITY_BASED = "priority_based"
    ALGORITHM_OPTIMIZED = "algorithm_optimized"
    TIME_ZONE_AWARE = "time_zone_aware"
    TRENDING_OPTIMIZED = "trending_optimized"

@dataclass
class PlatformConfig:
    """Configuration spécifique plateforme"""
    platform: PlatformType
    api_key: str
    rate_limit: int = 100  # requests per hour
    max_file_size: int = 100  # MB
    supported_formats: List[str] = field(default_factory=list)
    retry_after_header: bool = True
    quota_aware: bool = True
    priority: int = 1
    metadata_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionContent:
    """Contenu à distribuer"""
    content_id: str
    content_type: ContentType
    file_path: str
    metadata: Dict[str, Any]
    thumbnails: List[str] = field(default_factory=list)
    descriptions: Dict[str, str] = field(default_factory=dict)  # lang -> description
    tags: List[str] = field(default_factory=list)
    scheduling: Optional[datetime] = None
    seo_optimization: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionRequest:
    """Requête distribution multi-plateforme"""
    request_id: str
    content: DistributionContent
    target_platforms: List[PlatformType]
    strategy: DistributionStrategy
    max_retries_per_platform: int = 3
    global_timeout: int = 300
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlatformResult:
    """Résultat distribution pour une plateforme"""
    platform: PlatformType
    success: bool
    platform_id: Optional[str] = None
    url: Optional[str] = None
    retry_count: int = 0
    execution_time: float = 0.0
    error_details: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    next_available_slot: Optional[datetime] = None
    seo_score: Optional[float] = None

@dataclass
class DistributionResult:
    """Résultat complet distribution"""
    request_id: str
    overall_success: bool
    platform_results: List[PlatformResult]
    total_execution_time: float
    successful_platforms: int
    failed_platforms: int
    pending_platforms: int = 0
    seo_insights: Dict[str, Any] = field(default_factory=dict)

class RateLimitManager:
    """Gestionnaire rate limiting intelligent"""
    
    def __init__(self):
        self.platform_quotas = {}
        self.last_request_times = {}
        self.rate_limit_resets = {}
        self.backoff_multipliers = {}
    
    async def check_rate_limit(self, platform: PlatformType, current_quota: int = None) -> Dict[str, Any]:
        """Vérification rate limit avec prédiction"""
        platform_key = platform.value
        current_time = time.time()
        
        # Mise à jour quota si fourni
        if current_quota is not None:
            self.platform_quotas[platform_key] = current_quota
        
        # Vérification dernière requête
        if platform_key in self.last_request_times:
            time_since_last = current_time - self.last_request_times[platform_key]
            min_interval = self._get_min_interval(platform)
            
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                return {
                    'allowed': False,
                    'wait_time': wait_time,
                    'reason': 'rate_limit_interval',
                    'quota_remaining': self.platform_quotas.get(platform_key, 0)
                }
        
        # Vérification quota
        remaining_quota = self.platform_quotas.get(platform_key, 100)
        if remaining_quota <= 0:
            reset_time = self.rate_limit_resets.get(platform_key, current_time + 3600)
            return {
                'allowed': False,
                'wait_time': reset_time - current_time,
                'reason': 'quota_exhausted',
                'quota_remaining': 0
            }
        
        return {
            'allowed': True,
            'quota_remaining': remaining_quota,
            'estimated_reset': self.rate_limit_resets.get(platform_key)
        }
    
    def _get_min_interval(self, platform: PlatformType) -> float:
        """Calcul intervalle minimum entre requêtes"""
        intervals = {
            PlatformType.YOUTUBE: 2.0,
            PlatformType.INSTAGRAM: 1.0,
            PlatformType.TIKTOK: 1.5,
            PlatformType.TWITTER: 0.5,
            PlatformType.SPOTIFY: 3.0,
            PlatformType.SOUNDCLOUD: 1.0
        }
        return intervals.get(platform, 1.0)
    
    async def update_rate_limit_info(self, platform: PlatformType, headers: Dict[str, str]):
        """Mise à jour info rate limit depuis headers API"""
        platform_key = platform.value
        
        # Headers standards
        remaining = headers.get('X-RateLimit-Remaining') or headers.get('X-Rate-Limit-Remaining')
        reset = headers.get('X-RateLimit-Reset') or headers.get('X-Rate-Limit-Reset')
        retry_after = headers.get('Retry-After')
        
        if remaining:
            self.platform_quotas[platform_key] = int(remaining)
        
        if reset:
            self.rate_limit_resets[platform_key] = int(reset)
        
        if retry_after:
            self.rate_limit_resets[platform_key] = time.time() + int(retry_after)

class SEOOptimizer:
    """Optimiseur SEO pour distribution"""
    
    def __init__(self):
        self.platform_seo_rules = {
            PlatformType.YOUTUBE: {
                'title_max_length': 100,
                'description_max_length': 5000,
                'tags_max_count': 15,
                'optimal_upload_times': ['14:00', '15:00', '16:00', '17:00'],
                'trending_factors': ['engagement_rate', 'watch_time', 'click_through_rate']
            },
            PlatformType.INSTAGRAM: {
                'caption_max_length': 2200,
                'hashtags_max_count': 30,
                'optimal_hashtags': 11,
                'story_expiry_hours': 24,
                'optimal_post_times': ['11:00', '13:00', '17:00']
            },
            PlatformType.TIKTOK: {
                'caption_max_length': 150,
                'hashtags_max_count': 100,
                'trending_sounds': True,
                'algorithm_factors': ['completion_rate', 'shares', 'comments'],
                'optimal_upload_times': ['06:00', '10:00', '19:00', '20:00']
            }
        }
    
    async def optimize_content_for_platform(self, content: DistributionContent, platform: PlatformType) -> Dict[str, Any]:
        """Optimisation contenu pour plateforme spécifique"""
        rules = self.platform_seo_rules.get(platform, {})
        optimizations = {}
        
        # Optimisation titre
        if 'title_max_length' in rules:
            title = content.metadata.get('title', '')
            if len(title) > rules['title_max_length']:
                optimizations['title'] = title[:rules['title_max_length'] - 3] + '...'
                optimizations['title_truncated'] = True
        
        # Optimisation description
        platform_desc = content.descriptions.get(platform.value)
        if platform_desc and 'description_max_length' in rules:
            if len(platform_desc) > rules['description_max_length']:
                optimizations['description'] = platform_desc[:rules['description_max_length'] - 3] + '...'
                optimizations['description_truncated'] = True
        
        # Optimisation tags/hashtags
        if 'tags_max_count' in rules:
            if len(content.tags) > rules['tags_max_count']:
                optimizations['tags'] = content.tags[:rules['tags_max_count']]
                optimizations['tags_truncated'] = True
        
        # Recommandations timing
        if 'optimal_upload_times' in rules:
            current_hour = datetime.now().strftime('%H:00')
            if current_hour in rules['optimal_upload_times']:
                optimizations['timing_score'] = 1.0
            else:
                # Calcul score basé sur proximité des heures optimales
                optimizations['timing_score'] = self._calculate_timing_score(current_hour, rules['optimal_upload_times'])
        
        # Score SEO global
        optimizations['seo_score'] = self._calculate_seo_score(content, platform, optimizations)
        
        return optimizations
    
    def _calculate_timing_score(self, current_hour: str, optimal_hours: List[str]) -> float:
        """Calcul score timing basé sur proximité heures optimales"""
        current_h = int(current_hour.split(':')[0])
        optimal_h = [int(h.split(':')[0]) for h in optimal_hours]
        
        min_distance = min(abs(current_h - oh) for oh in optimal_h)
        return max(0.1, 1.0 - (min_distance / 12.0))  # Score entre 0.1 et 1.0
    
    def _calculate_seo_score(self, content: DistributionContent, platform: PlatformType, optimizations: Dict) -> float:
        """Calcul score SEO global"""
        score = 0.5  # Score de base
        
        # Bonus pour métadonnées complètes
        if content.metadata.get('title'):
            score += 0.1
        if content.descriptions.get(platform.value):
            score += 0.1
        if content.tags:
            score += 0.1
        if content.thumbnails:
            score += 0.1
        
        # Bonus timing
        score += optimizations.get('timing_score', 0) * 0.2
        
        return min(1.0, score)

class PlatformAdapter:
    """Adaptateur pour différentes plateformes"""
    
    def __init__(self, rate_limit_manager: RateLimitManager, seo_optimizer: SEOOptimizer):
        self.rate_limit_manager = rate_limit_manager
        self.seo_optimizer = seo_optimizer
        self.platform_strategies = {
            PlatformType.YOUTUBE: self._youtube_strategy,
            PlatformType.INSTAGRAM: self._instagram_strategy,
            PlatformType.TIKTOK: self._tiktok_strategy,
            PlatformType.SPOTIFY: self._spotify_strategy,
            PlatformType.TWITTER: self._twitter_strategy
        }
    
    async def upload_to_platform(self, content: DistributionContent, platform: PlatformType, config: PlatformConfig) -> Dict[str, Any]:
        """Upload vers plateforme avec adaptations spécifiques"""
        strategy = self.platform_strategies.get(platform, self._generic_strategy)
        return await strategy(content, config)
    
    async def _youtube_strategy(self, content: DistributionContent, config: PlatformConfig) -> Dict[str, Any]:
        """Stratégie spécifique YouTube"""
        # Vérification rate limit
        rate_check = await self.rate_limit_manager.check_rate_limit(PlatformType.YOUTUBE)
        if not rate_check['allowed']:
            raise Exception(f"Rate limit exceeded, wait {rate_check['wait_time']}s")
        
        # Optimisation SEO
        seo_opts = await self.seo_optimizer.optimize_content_for_platform(content, PlatformType.YOUTUBE)
        
        # Simulation upload YouTube
        await asyncio.sleep(random.uniform(2, 5))  # Simulation latence API
        
        return {
            'platform_id': f"YT_{uuid.uuid4().hex[:8]}",
            'url': f"https://youtube.com/watch?v={uuid.uuid4().hex[:11]}",
            'seo_score': seo_opts['seo_score'],
            'metadata_optimized': seo_opts,
            'processing_status': 'uploaded'
        }
    
    async def _instagram_strategy(self, content: DistributionContent, config: PlatformConfig) -> Dict[str, Any]:
        """Stratégie spécifique Instagram"""
        rate_check = await self.rate_limit_manager.check_rate_limit(PlatformType.INSTAGRAM)
        if not rate_check['allowed']:
            raise Exception(f"Rate limit exceeded, wait {rate_check['wait_time']}s")
        
        seo_opts = await self.seo_optimizer.optimize_content_for_platform(content, PlatformType.INSTAGRAM)
        
        # Gestion story vs post
        is_story = content.content_type == ContentType.STORY
        
        await asyncio.sleep(random.uniform(1, 3))
        
        return {
            'platform_id': f"IG_{uuid.uuid4().hex[:8]}",
            'url': f"https://instagram.com/p/{uuid.uuid4().hex[:11]}",
            'seo_score': seo_opts['seo_score'],
            'is_story': is_story,
            'expiry_time': datetime.now() + timedelta(hours=24) if is_story else None,
            'hashtags_count': len(content.tags)
        }
    
    async def _tiktok_strategy(self, content: DistributionContent, config: PlatformConfig) -> Dict[str, Any]:
        """Stratégie spécifique TikTok"""
        rate_check = await self.rate_limit_manager.check_rate_limit(PlatformType.TIKTOK)
        if not rate_check['allowed']:
            raise Exception(f"Rate limit exceeded, wait {rate_check['wait_time']}s")
        
        seo_opts = await self.seo_optimizer.optimize_content_for_platform(content, PlatformType.TIKTOK)
        
        await asyncio.sleep(random.uniform(1.5, 4))
        
        return {
            'platform_id': f"TT_{uuid.uuid4().hex[:8]}",
            'url': f"https://tiktok.com/@user/video/{uuid.uuid4().hex[:16]}",
            'seo_score': seo_opts['seo_score'],
            'algorithm_optimized': True,
            'trending_potential': random.uniform(0.1, 0.9)
        }
    
    async def _spotify_strategy(self, content: DistributionContent, config: PlatformConfig) -> Dict[str, Any]:
        """Stratégie spécifique Spotify"""
        if content.content_type not in [ContentType.AUDIO, ContentType.ALBUM, ContentType.SINGLE, ContentType.PODCAST]:
            raise Exception(f"Content type {content.content_type} not supported on Spotify")
        
        rate_check = await self.rate_limit_manager.check_rate_limit(PlatformType.SPOTIFY)
        if not rate_check['allowed']:
            raise Exception(f"Rate limit exceeded, wait {rate_check['wait_time']}s")
        
        await asyncio.sleep(random.uniform(3, 6))  # Spotify a processing plus long
        
        return {
            'platform_id': f"SP_{uuid.uuid4().hex[:8]}",
            'url': f"https://open.spotify.com/track/{uuid.uuid4().hex[:22]}",
            'release_date': content.scheduling or datetime.now(),
            'processing_status': 'pending_review',
            'estimated_live_date': datetime.now() + timedelta(hours=24)
        }
    
    async def _twitter_strategy(self, content: DistributionContent, config: PlatformConfig) -> Dict[str, Any]:
        """Stratégie spécifique Twitter"""
        rate_check = await self.rate_limit_manager.check_rate_limit(PlatformType.TWITTER)
        if not rate_check['allowed']:
            raise Exception(f"Rate limit exceeded, wait {rate_check['wait_time']}s")
        
        await asyncio.sleep(random.uniform(0.5, 2))
        
        return {
            'platform_id': f"TW_{uuid.uuid4().hex[:8]}",
            'url': f"https://twitter.com/user/status/{uuid.uuid4().hex[:16]}",
            'character_count': len(content.descriptions.get('twitter', '')),
            'media_attached': len(content.thumbnails) > 0
        }
    
    async def _generic_strategy(self, content: DistributionContent, config: PlatformConfig) -> Dict[str, Any]:
        """Stratégie générique pour plateformes non spécialisées"""
        await asyncio.sleep(random.uniform(1, 3))
        
        return {
            'platform_id': f"GEN_{uuid.uuid4().hex[:8]}",
            'url': f"https://platform.com/content/{uuid.uuid4().hex[:16]}",
            'generic_upload': True
        }

class DistributionRetry:
    """
    Retry spécialisé pour distribution multi-plateformes.
    Platform API retry + SEO + social media posting patterns.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.rate_limit_manager = RateLimitManager()
        self.seo_optimizer = SEOOptimizer()
        self.platform_adapter = PlatformAdapter(self.rate_limit_manager, self.seo_optimizer)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration patterns retry par plateforme
        self.platform_retry_strategies = {
            PlatformType.YOUTUBE: {
                'max_retries': 3,
                'timeout_progression': [30, 60, 120],
                'quota_aware': True,
                'retry_after_respect': True,
                'processing_wait': True
            },
            PlatformType.SPOTIFY: {
                'max_retries': 2,
                'timeout_progression': [60, 180],
                'release_window_aware': True,
                'metadata_retry': True,
                'review_process': True
            },
            PlatformType.INSTAGRAM: {
                'max_retries': 4,
                'timeout_progression': [10, 20, 40, 80],
                'story_expiry_aware': True,
                'rate_limit_backoff': True,
                'hashtag_optimization': True
            },
            PlatformType.TIKTOK: {
                'max_retries': 5,
                'timeout_progression': [5, 10, 20, 40, 80],
                'trending_window_optimization': True,
                'algorithm_aware': True,
                'completion_rate_focused': True
            },
            PlatformType.TWITTER: {
                'max_retries': 2,
                'timeout_progression': [15, 30],
                'character_limit_aware': True,
                'thread_support': True
            }
        }
    
    async def retry_platform_distribution(self, distribution_request: DistributionRequest) -> DistributionResult:
        """
        Retry spécialisé pour distribution avec platform rate limiting.
        
        Distribution Features:
        - Multi-platform simultaneous/sequential distribution
        - Rate limit awareness avec intelligent backoff
        - SEO optimization per platform
        - Content adaptation pour format requirements
        - Trending window optimization
        - Algorithm-aware posting strategies
        - Story expiry awareness
        - Release window coordination
        """
        start_time = time.time()
        platform_results = []
        
        # Configuration stratégie distribution
        if distribution_request.strategy == DistributionStrategy.SIMULTANEOUS:
            platform_results = await self._distribute_simultaneous(distribution_request)
        elif distribution_request.strategy == DistributionStrategy.SEQUENTIAL:
            platform_results = await self._distribute_sequential(distribution_request)
        elif distribution_request.strategy == DistributionStrategy.PRIORITY_BASED:
            platform_results = await self._distribute_priority_based(distribution_request)
        elif distribution_request.strategy == DistributionStrategy.ALGORITHM_OPTIMIZED:
            platform_results = await self._distribute_algorithm_optimized(distribution_request)
        else:
            platform_results = await self._distribute_simultaneous(distribution_request)
        
        # Calcul résultats
        successful = sum(1 for r in platform_results if r.success)
        failed = len(platform_results) - successful
        total_time = time.time() - start_time
        
        # Génération insights SEO
        seo_insights = await self._generate_seo_insights(platform_results)
        
        return DistributionResult(
            request_id=distribution_request.request_id,
            overall_success=successful > 0,
            platform_results=platform_results,
            total_execution_time=total_time,
            successful_platforms=successful,
            failed_platforms=failed,
            seo_insights=seo_insights
        )
    
    async def _distribute_simultaneous(self, request: DistributionRequest) -> List[PlatformResult]:
        """Distribution simultanée sur toutes plateformes"""
        tasks = []
        for platform in request.target_platforms:
            task = self._retry_single_platform(request, platform)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        platform_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                platform_results.append(PlatformResult(
                    platform=request.target_platforms[i],
                    success=False,
                    error_details=str(result)
                ))
            else:
                platform_results.append(result)
        
        return platform_results
    
    async def _distribute_sequential(self, request: DistributionRequest) -> List[PlatformResult]:
        """Distribution séquentielle avec optimisation timing"""
        platform_results = []
        
        for platform in request.target_platforms:
            result = await self._retry_single_platform(request, platform)
            platform_results.append(result)
            
            # Pause entre plateformes pour éviter conflicts
            if platform != request.target_platforms[-1]:
                await asyncio.sleep(1)
        
        return platform_results
    
    async def _distribute_priority_based(self, request: DistributionRequest) -> List[PlatformResult]:
        """Distribution basée sur priorités plateformes"""
        # Tri plateformes par priorité (YouTube et Spotify prioritaires)
        priority_order = {
            PlatformType.YOUTUBE: 1,
            PlatformType.SPOTIFY: 1,
            PlatformType.INSTAGRAM: 2,
            PlatformType.TIKTOK: 2,
            PlatformType.TWITTER: 3
        }
        
        sorted_platforms = sorted(
            request.target_platforms,
            key=lambda p: priority_order.get(p, 4)
        )
        
        platform_results = []
        for platform in sorted_platforms:
            result = await self._retry_single_platform(request, platform)
            platform_results.append(result)
        
        return platform_results
    
    async def _distribute_algorithm_optimized(self, request: DistributionRequest) -> List[PlatformResult]:
        """Distribution optimisée pour algorithmes plateformes"""
        # Optimisation timing basée sur algorithmes
        platform_results = []
        
        # TikTok et Instagram en premier (algorithm-sensitive)
        algorithm_sensitive = [p for p in request.target_platforms if p in [PlatformType.TIKTOK, PlatformType.INSTAGRAM]]
        others = [p for p in request.target_platforms if p not in algorithm_sensitive]
        
        # Distribution algorithm-sensitive d'abord
        for platform in algorithm_sensitive:
            result = await self._retry_single_platform(request, platform)
            platform_results.append(result)
            await asyncio.sleep(0.5)  # Spacing léger
        
        # Puis autres plateformes
        for platform in others:
            result = await self._retry_single_platform(request, platform)
            platform_results.append(result)
        
        return platform_results
    
    async def _retry_single_platform(self, request: DistributionRequest, platform: PlatformType) -> PlatformResult:
        """Retry pour une plateforme spécifique"""
        start_time = time.time()
        strategy_config = self.platform_retry_strategies.get(platform, {
            'max_retries': 3,
            'timeout_progression': [30, 60, 120]
        })
        
        max_retries = min(request.max_retries_per_platform, strategy_config.get('max_retries', 3))
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                # Configuration plateforme
                platform_config = PlatformConfig(
                    platform=platform,
                    api_key=f"key_{platform.value}",
                    rate_limit=100,
                    supported_formats=['mp4', 'jpg', 'png', 'mp3']
                )
                
                # Upload vers plateforme
                upload_result = await self.platform_adapter.upload_to_platform(
                    request.content,
                    platform,
                    platform_config
                )
                
                execution_time = time.time() - start_time
                
                return PlatformResult(
                    platform=platform,
                    success=True,
                    platform_id=upload_result.get('platform_id'),
                    url=upload_result.get('url'),
                    retry_count=attempt,
                    execution_time=execution_time,
                    seo_score=upload_result.get('seo_score')
                )
                
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    self.logger.error(f"Max retries reached for {platform.value}: {str(e)}")
                    break
                
                # Calcul delay basé sur stratégie
                timeout_progression = strategy_config.get('timeout_progression', [30, 60, 120])
                delay = timeout_progression[min(attempt, len(timeout_progression) - 1)]
                
                # Adjustment delay pour rate limiting
                if "rate limit" in str(e).lower():
                    delay *= 2  # Double delay pour rate limit
                
                self.logger.warning(f"Platform {platform.value} retry {attempt + 1}/{max_retries} in {delay}s: {str(e)}")
                await asyncio.sleep(delay)
        
        execution_time = time.time() - start_time
        return PlatformResult(
            platform=platform,
            success=False,
            retry_count=max_retries,
            execution_time=execution_time,
            error_details=str(last_exception) if last_exception else "Unknown error"
        )
    
    async def _generate_seo_insights(self, platform_results: List[PlatformResult]) -> Dict[str, Any]:
        """Génération insights SEO basés sur résultats"""
        insights = {
            'total_platforms': len(platform_results),
            'successful_uploads': sum(1 for r in platform_results if r.success),
            'average_seo_score': 0.0,
            'platform_performance': {},
            'recommendations': []
        }
        
        # Calcul score SEO moyen
        seo_scores = [r.seo_score for r in platform_results if r.seo_score is not None]
        if seo_scores:
            insights['average_seo_score'] = sum(seo_scores) / len(seo_scores)
        
        # Performance par plateforme
        for result in platform_results:
            insights['platform_performance'][result.platform.value] = {
                'success': result.success,
                'retry_count': result.retry_count,
                'execution_time': result.execution_time,
                'seo_score': result.seo_score
            }
        
        # Recommandations
        if insights['average_seo_score'] < 0.7:
            insights['recommendations'].append("Consider optimizing content metadata for better SEO")
        
        failed_platforms = [r.platform.value for r in platform_results if not r.success]
        if failed_platforms:
            insights['recommendations'].append(f"Review configuration for platforms: {', '.join(failed_platforms)}")
        
        return insights

# Instance globale
distribution_retry = DistributionRetry()

# Export des classes principales
__all__ = [
    'DistributionRetry',
    'PlatformType',
    'ContentType',
    'DistributionStrategy',
    'DistributionRequest',
    'DistributionResult',
    'PlatformResult',
    'distribution_retry'
]