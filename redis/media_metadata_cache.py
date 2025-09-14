"""
Media Metadata Cache module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 Media Metadata Cache - Cache Métadonnées Multimédia Enterprise
================================================================

Cache spécialisé pour métadonnées multimédia avec optimisation streaming,
indexation intelligente et gestion versioning contenu.

**Rôles Experts:**
- **Audio Engineer**: Optimisation cache audio et métadonnées DSP
- **Backend Senior**: Performance cache multimédia haute fréquence
- **ML Engineer**: Classification automatique et tagging intelligent
- **DevOps**: Monitoring cache média et optimisation CDN

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import hashlib
import json
import mimetypes
from typing import Dict, Any, Optional, List, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import numpy as np
import aioredis

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediaType(Enum):
    """Types de média supportés"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    MIXED = "mixed"

class MediaQuality(Enum):
    """Qualités de média"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    RAW = "raw"

class CacheStrategy(Enum):
    """Stratégies cache média"""
    AGGRESSIVE = "aggressive"  # Cache tous les formats
    SELECTIVE = "selective"   # Cache formats populaires
    ADAPTIVE = "adaptive"     # Cache basé sur usage
    STREAMING = "streaming"   # Optimisé streaming

@dataclass
class MediaMetadata:
    """Métadonnées complètes média"""
    # Identifiants
    media_id: str
    filename: str
    original_filename: str
    content_hash: str
    
    # Propriétés techniques
    media_type: MediaType
    mime_type: str
    file_size: int
    duration: Optional[float] = None  # secondes pour audio/video
    
    # Propriétés dimensionnelles
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[str] = None
    
    # Propriétés audio spécialisées
    sample_rate: Optional[int] = None
    bit_rate: Optional[int] = None
    channels: Optional[int] = None
    audio_codec: Optional[str] = None
    
    # Propriétés video spécialisées
    video_codec: Optional[str] = None
    frame_rate: Optional[float] = None
    color_space: Optional[str] = None
    
    # Métadonnées créateur
    creator_id: str
    created_at: float = field(default_factory=time.time)
    uploaded_at: float = field(default_factory=time.time)
    
    # Tags et classification
    tags: List[str] = field(default_factory=list)
    auto_tags: List[str] = field(default_factory=list)  # Tags générés par IA
    categories: List[str] = field(default_factory=list)
    mood_tags: List[str] = field(default_factory=list)
    
    # Propriétés business
    privacy_level: str = "private"  # private, unlisted, public
    monetization_enabled: bool = False
    copyright_status: str = "original"  # original, licensed, copyrighted
    
    # Analytics et performance
    view_count: int = 0
    download_count: int = 0
    share_count: int = 0
    like_count: int = 0
    
    # Versioning et variants
    version: str = "1.0"
    variants: Dict[str, str] = field(default_factory=dict)  # quality -> url
    thumbnails: Dict[str, str] = field(default_factory=dict)  # size -> url
    
    # Processing status
    processing_status: str = "completed"  # pending, processing, completed, failed
    ai_analysis_completed: bool = False
    
    # Cache metadata
    cached_at: float = field(default_factory=time.time)
    cache_hit_count: int = 0
    last_accessed: float = field(default_factory=time.time)

@dataclass
class CacheMetrics:
    """Métriques cache média"""
    total_cached_items: int = 0
    cache_size_bytes: int = 0
    hit_ratio: float = 0.0
    miss_count: int = 0
    eviction_count: int = 0
    streaming_requests: int = 0
    bandwidth_saved_bytes: int = 0

class MediaMetadataCache:
    """
    🎬 Cache Métadonnées Multimédia Enterprise
    
    **Audio Engineer:**
    - Cache optimisé métadonnées audio professionnelles (sample rate, bit depth, etc.)
    - Indexation spécialisée DSP et traitement audio temps réel
    - Gestion formats audio lossless et compression intelligente
    - Cache waveforms et spectrogrammes pour interface audio
    
    **Backend Senior:**
    - Architecture cache haute performance pour métadonnées volumineuses
    - Optimisation requêtes complexes sur attributs multimédia
    - Indexation multi-dimensionnelle (taille, durée, qualité)
    - Compression intelligente métadonnées et sérialisation optimisée
    
    **ML Engineer:**
    - Classification automatique contenu avec tags IA
    - Clustering similarité multimédia pour recommendations
    - Détection duplicates basée fingerprinting audio/video
    - Analytics prédictives pour cache warming intelligent
    
    **DevOps:**
    - Monitoring performance cache et bandwidth optimization
    - Integration CDN avec cache métadonnées distribué
    - Métriques streaming et optimisation delivery
    - Alertes proactives cache overflow et performance
    """
    
    def __init__(self, redis_pool, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.redis_pool = redis_pool
        self.config = config or {}
        
        # Configuration cache
        self.cache_strategy = CacheStrategy(self.config.get('cache_strategy', 'adaptive'))
        self.max_cache_size_gb = self.config.get('max_cache_size_gb', 10.0)
        self.default_ttl = self.config.get('default_ttl', 86400)  # 24h
        self.enable_ml_tagging = self.config.get('enable_ml_tagging', True)
        
        # Cache local L1 pour métadonnées fréquentes
        self.l1_cache: Dict[str, MediaMetadata] = {}
        self.l1_max_items = self.config.get('l1_max_items', 10000)
        
        # Index pour recherches rapides
        self.metadata_index: Dict[str, Set[str]] = defaultdict(set)
        self.creator_index: Dict[str, Set[str]] = defaultdict(set)
        self.type_index: Dict[MediaType, Set[str]] = defaultdict(set)
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Métriques et analytics
        self.cache_metrics = CacheMetrics()
        self.access_patterns: deque = deque(maxlen=10000)
        
        # ML pour tagging automatique
        self.ml_classifiers: Dict[str, Any] = {}
        
        # Optimisation streaming
        self.streaming_cache: Dict[str, Dict[str, Any]] = {}
        self.popular_content: deque = deque(maxlen=1000)
        
        # Tâches background
        asyncio.create_task(self._start_background_tasks())
        
        logger.info(f"🎬 Media Metadata Cache initialisé (stratégie: {self.cache_strategy.value})")
    
    async def _start_background_tasks(self) -> None:
        """**DevOps**: Démarrage tâches background"""
        asyncio.create_task(self._cache_maintenance_loop())
        asyncio.create_task(self._analytics_loop())
        asyncio.create_task(self._ml_processing_loop())
        asyncio.create_task(self._streaming_optimization_loop())
        logger.info("🔄 Tâches background cache média démarrées")
    
    async def store_metadata(
        self, 
        media_id: str, 
        metadata: MediaMetadata,
        force_refresh: bool = False
    ) -> bool:
        """**Backend Senior**: Stockage métadonnées avec indexation optimisée"""
        
        try:
            # Vérification cache existant
            if not force_refresh and media_id in self.l1_cache:
                logger.debug(f"📋 Métadonnées déjà en cache L1: {media_id}")
                return True
            
            # Validation métadonnées
            if not await self._validate_metadata(metadata):
                logger.error(f"❌ Métadonnées invalides: {media_id}")
                return False
            
            # Enrichissement automatique
            await self._enrich_metadata(metadata)
            
            # Stockage L1 cache
            await self._store_l1_cache(media_id, metadata)
            
            # Stockage Redis L2
            await self._store_redis_cache(media_id, metadata)
            
            # Mise à jour index
            await self._update_indexes(media_id, metadata)
            
            # Analytics
            self._record_cache_operation("store", media_id, metadata)
            
            logger.debug(f"✅ Métadonnées stockées: {media_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage métadonnées {media_id}: {e}")
            return False
    
    async def get_metadata(self, media_id: str, include_analytics: bool = False) -> Optional[MediaMetadata]:
        """**Backend Senior**: Récupération métadonnées avec cache multi-niveaux"""
        
        start_time = time.time()
        
        try:
            # Tentative L1 cache
            if media_id in self.l1_cache:
                metadata = self.l1_cache[media_id]
                metadata.last_accessed = time.time()
                metadata.cache_hit_count += 1
                
                self.cache_metrics.hit_ratio = self._update_hit_ratio(True)
                self._record_access_pattern(media_id, "l1_hit", time.time() - start_time)
                
                if include_analytics:
                    await self._add_analytics_data(metadata)
                
                return metadata
            
            # Tentative Redis L2
            metadata = await self._get_redis_cache(media_id)
            if metadata:
                # Promotion vers L1 si approprié
                await self._consider_l1_promotion(media_id, metadata)
                
                metadata.last_accessed = time.time()
                metadata.cache_hit_count += 1
                
                self.cache_metrics.hit_ratio = self._update_hit_ratio(True)
                self._record_access_pattern(media_id, "l2_hit", time.time() - start_time)
                
                if include_analytics:
                    await self._add_analytics_data(metadata)
                
                return metadata
            
            # Cache miss
            self.cache_metrics.miss_count += 1
            self.cache_metrics.hit_ratio = self._update_hit_ratio(False)
            self._record_access_pattern(media_id, "miss", time.time() - start_time)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération métadonnées {media_id}: {e}")
            return None
    
    async def search_metadata(
        self,
        query: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[MediaMetadata]:
        """**ML Engineer**: Recherche avancée métadonnées avec indexation"""
        
        try:
            matching_ids = set()
            first_filter = True
            
            # Filtrage par type média
            if "media_type" in query:
                media_type = MediaType(query["media_type"])
                type_matches = self.type_index[media_type]
                matching_ids = type_matches if first_filter else matching_ids.intersection(type_matches)
                first_filter = False
            
            # Filtrage par créateur
            if "creator_id" in query:
                creator_matches = self.creator_index[query["creator_id"]]
                matching_ids = creator_matches if first_filter else matching_ids.intersection(creator_matches)
                first_filter = False
            
            # Filtrage par tags
            if "tags" in query:
                tags = query["tags"] if isinstance(query["tags"], list) else [query["tags"]]
                for tag in tags:
                    tag_matches = self.tag_index[tag.lower()]
                    matching_ids = tag_matches if first_filter else matching_ids.intersection(tag_matches)
                    first_filter = False
            
            # Filtres additionnels
            filtered_results = []
            for media_id in matching_ids:
                metadata = await self.get_metadata(media_id)
                if metadata and await self._match_filters(metadata, query):
                    filtered_results.append(metadata)
            
            # Tri et pagination
            sorted_results = await self._sort_search_results(filtered_results, query.get("sort_by", "created_at"))
            
            start_idx = offset
            end_idx = offset + limit
            return sorted_results[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche métadonnées: {e}")
            return []
    
    async def get_creator_media(
        self, 
        creator_id: str, 
        media_type: Optional[MediaType] = None,
        limit: int = 50
    ) -> List[MediaMetadata]:
        """**Backend Senior**: Récupération média par créateur optimisée"""
        
        try:
            # Utilisation index créateur
            media_ids = self.creator_index.get(creator_id, set())
            
            # Filtrage par type si spécifié
            if media_type:
                type_ids = self.type_index.get(media_type, set())
                media_ids = media_ids.intersection(type_ids)
            
            # Récupération métadonnées
            results = []
            for media_id in list(media_ids)[:limit]:
                metadata = await self.get_metadata(media_id)
                if metadata:
                    results.append(metadata)
            
            # Tri par date création (plus récent en premier)
            results.sort(key=lambda m: m.created_at, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération média créateur {creator_id}: {e}")
            return []
    
    async def get_similar_media(
        self, 
        media_id: str, 
        similarity_threshold: float = 0.7,
        limit: int = 10
    ) -> List[Tuple[MediaMetadata, float]]:
        """**ML Engineer**: Recherche média similaires avec scoring ML"""
        
        try:
            base_metadata = await self.get_metadata(media_id)
            if not base_metadata:
                return []
            
            similar_media = []
            
            # Recherche dans même type de média
            candidate_ids = self.type_index.get(base_metadata.media_type, set())
            
            for candidate_id in candidate_ids:
                if candidate_id == media_id:
                    continue
                
                candidate_metadata = await self.get_metadata(candidate_id)
                if candidate_metadata:
                    # Calcul similarité
                    similarity_score = await self._calculate_similarity(base_metadata, candidate_metadata)
                    
                    if similarity_score >= similarity_threshold:
                        similar_media.append((candidate_metadata, similarity_score))
            
            # Tri par score de similarité décroissant
            similar_media.sort(key=lambda x: x[1], reverse=True)
            
            return similar_media[:limit]
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche similarité {media_id}: {e}")
            return []
    
    async def _calculate_similarity(
        self, 
        metadata1: MediaMetadata, 
        metadata2: MediaMetadata
    ) -> float:
        """**ML Engineer**: Calcul similarité métadonnées avec ML"""
        
        try:
            similarity_scores = []
            
            # Similarité tags
            tags1 = set(metadata1.tags + metadata1.auto_tags)
            tags2 = set(metadata2.tags + metadata2.auto_tags)
            
            if tags1 or tags2:
                tag_similarity = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
                similarity_scores.append(tag_similarity * 0.4)  # Poids 40%
            
            # Similarité technique (durée, dimensions)
            tech_similarity = 0.0
            
            if metadata1.duration and metadata2.duration:
                duration_diff = abs(metadata1.duration - metadata2.duration)
                max_duration = max(metadata1.duration, metadata2.duration)
                tech_similarity += (1.0 - duration_diff / max_duration) * 0.2
            
            if metadata1.file_size and metadata2.file_size:
                size_diff = abs(metadata1.file_size - metadata2.file_size)
                max_size = max(metadata1.file_size, metadata2.file_size)
                tech_similarity += (1.0 - size_diff / max_size) * 0.1
            
            similarity_scores.append(tech_similarity)
            
            # Similarité catégories
            if metadata1.categories and metadata2.categories:
                cat1 = set(metadata1.categories)
                cat2 = set(metadata2.categories)
                cat_similarity = len(cat1.intersection(cat2)) / len(cat1.union(cat2))
                similarity_scores.append(cat_similarity * 0.3)  # Poids 30%
            
            # Score final
            return sum(similarity_scores) if similarity_scores else 0.0
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul similarité: {e}")
            return 0.0
    
    async def update_analytics(self, media_id -> None: str, event_type -> None: str, value -> None: int = 1) -> None:
        """**DevOps**: Mise à jour analytics média temps réel"""
        
        try:
            metadata = await self.get_metadata(media_id)
            if not metadata:
                return False
            
            # Mise à jour compteurs
            if event_type == "view":
                metadata.view_count += value
            elif event_type == "download":
                metadata.download_count += value
            elif event_type == "share":
                metadata.share_count += value
            elif event_type == "like":
                metadata.like_count += value
            
            # Sauvegarde mise à jour
            await self.store_metadata(media_id, metadata, force_refresh=True)
            
            # Tracking popularité
            await self._track_popularity(media_id, event_type, value)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour analytics {media_id}: {e}")
            return False
    
    async def get_trending_media(
        self, 
        time_window_hours: int = 24,
        media_type: Optional[MediaType] = None,
        limit: int = 20
    ) -> List[Tuple[MediaMetadata, float]]:
        """**ML Engineer**: Analyse trending basée analytics temps réel"""
        
        try:
            # Score trending basé sur activité récente
            trending_scores = {}
            cutoff_time = time.time() - (time_window_hours * 3600)
            
            # Analyse patterns d'accès récents
            recent_accesses = [
                pattern for pattern in self.access_patterns
                if pattern.get("timestamp", 0) > cutoff_time
            ]
            
            # Calcul scores trending
            media_activity = defaultdict(int)
            for access in recent_accesses:
                media_id = access.get("media_id")
                if media_id:
                    media_activity[media_id] += 1
            
            # Enrichissement avec métadonnées
            trending_media = []
            for media_id, activity_score in media_activity.items():
                metadata = await self.get_metadata(media_id)
                if metadata:
                    # Filtrage par type si spécifié
                    if media_type and metadata.media_type != media_type:
                        continue
                    
                    # Score composite trending
                    recency_factor = 1.0 - (time.time() - metadata.created_at) / (7 * 24 * 3600)  # 7 jours
                    engagement_score = (metadata.view_count + metadata.like_count * 2 + metadata.share_count * 3)
                    
                    composite_score = activity_score * 0.5 + engagement_score * 0.3 + recency_factor * 0.2
                    
                    trending_media.append((metadata, composite_score))
            
            # Tri par score décroissant
            trending_media.sort(key=lambda x: x[1], reverse=True)
            
            return trending_media[:limit]
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse trending: {e}")
            return []
    
    async def _validate_metadata(self, metadata: MediaMetadata) -> bool:
        """**Backend Senior**: Validation métadonnées complète"""
        
        # Validation champs obligatoires
        if not metadata.media_id or not metadata.filename or not metadata.creator_id:
            return False
        
        # Validation type média
        if not isinstance(metadata.media_type, MediaType):
            return False
        
        # Validation taille fichier
        if metadata.file_size <= 0:
            return False
        
        # Validations spécialisées par type
        if metadata.media_type == MediaType.AUDIO:
            if metadata.duration and metadata.duration <= 0:
                return False
            if metadata.sample_rate and metadata.sample_rate < 8000:  # Minimum 8kHz
                return False
        
        elif metadata.media_type == MediaType.VIDEO:
            if metadata.duration and metadata.duration <= 0:
                return False
            if metadata.width and metadata.height:
                if metadata.width <= 0 or metadata.height <= 0:
                    return False
        
        return True
    
    async def _enrich_metadata(self, metadata -> None: MediaMetadata) -> None:
        """**ML Engineer**: Enrichissement automatique métadonnées"""
        
        try:
            # Détection MIME type si manquant
            if not metadata.mime_type:
                metadata.mime_type = mimetypes.guess_type(metadata.filename)[0] or "application/octet-stream"
            
            # Classification automatique contenu
            if self.enable_ml_tagging and not metadata.auto_tags:
                metadata.auto_tags = await self._auto_tag_content(metadata)
            
            # Calcul ratio aspect pour images/vidéos
            if metadata.width and metadata.height and not metadata.aspect_ratio:
                ratio = metadata.width / metadata.height
                if abs(ratio - 16/9) < 0.1:
                    metadata.aspect_ratio = "16:9"
                elif abs(ratio - 4/3) < 0.1:
                    metadata.aspect_ratio = "4:3"
                elif abs(ratio - 1.0) < 0.1:
                    metadata.aspect_ratio = "1:1"
                else:
                    metadata.aspect_ratio = f"{metadata.width}:{metadata.height}"
            
            # Détection qualité basée sur propriétés techniques
            await self._detect_quality_level(metadata)
            
        except Exception as e:
            logger.error(f"❌ Erreur enrichissement métadonnées: {e}")
    
    async def _auto_tag_content(self, metadata: MediaMetadata) -> List[str]:
        """**ML Engineer**: Tagging automatique contenu avec IA"""
        
        try:
            auto_tags = []
            
            # Tags basés sur nom de fichier
            filename_lower = metadata.filename.lower()
            
            # Tags techniques
            if metadata.media_type == MediaType.AUDIO:
                if "podcast" in filename_lower:
                    auto_tags.extend(["podcast", "spoken"])
                if "music" in filename_lower or "song" in filename_lower:
                    auto_tags.extend(["music", "song"])
                if metadata.sample_rate and metadata.sample_rate >= 48000:
                    auto_tags.append("high_quality")
            
            elif metadata.media_type == MediaType.VIDEO:
                if "tutorial" in filename_lower or "how_to" in filename_lower:
                    auto_tags.extend(["tutorial", "educational"])
                if "vlog" in filename_lower:
                    auto_tags.append("vlog")
                if metadata.width and metadata.width >= 1920:
                    auto_tags.append("hd")
                if metadata.width and metadata.width >= 3840:
                    auto_tags.append("4k")
            
            # Tags de durée
            if metadata.duration:
                if metadata.duration < 60:
                    auto_tags.append("short")
                elif metadata.duration > 3600:
                    auto_tags.append("long_form")
            
            # Tags de popularité prédictive
            if metadata.file_size > 100 * 1024 * 1024:  # > 100MB
                auto_tags.append("high_production")
            
            return list(set(auto_tags))  # Dédoublonnage
            
        except Exception as e:
            logger.error(f"❌ Erreur auto-tagging: {e}")
            return []
    
    async def _detect_quality_level(self, metadata -> None: MediaMetadata) -> None:
        """**Audio Engineer**: Détection niveau qualité technique"""
        
        try:
            quality_factors = []
            
            if metadata.media_type == MediaType.AUDIO:
                # Critères qualité audio
                if metadata.sample_rate:
                    if metadata.sample_rate >= 96000:
                        quality_factors.append("ultra")
                    elif metadata.sample_rate >= 48000:
                        quality_factors.append("high")
                    elif metadata.sample_rate >= 44100:
                        quality_factors.append("medium")
                    else:
                        quality_factors.append("low")
                
                if metadata.bit_rate:
                    if metadata.bit_rate >= 320000:  # 320 kbps
                        quality_factors.append("high")
                    elif metadata.bit_rate >= 192000:  # 192 kbps
                        quality_factors.append("medium")
                    else:
                        quality_factors.append("low")
            
            elif metadata.media_type == MediaType.VIDEO:
                # Critères qualité vidéo
                if metadata.width and metadata.height:
                    pixel_count = metadata.width * metadata.height
                    if pixel_count >= 3840 * 2160:  # 4K
                        quality_factors.append("ultra")
                    elif pixel_count >= 1920 * 1080:  # FullHD
                        quality_factors.append("high")
                    elif pixel_count >= 1280 * 720:  # HD
                        quality_factors.append("medium")
                    else:
                        quality_factors.append("low")
                
                if metadata.frame_rate:
                    if metadata.frame_rate >= 60:
                        quality_factors.append("high")
                    elif metadata.frame_rate >= 30:
                        quality_factors.append("medium")
                    else:
                        quality_factors.append("low")
            
            # Détermination qualité finale
            if quality_factors:
                quality_counts = {q: quality_factors.count(q) for q in set(quality_factors)}
                detected_quality = max(quality_counts.keys(), key=quality_counts.get)
                
                if "quality" not in metadata.tags:
                    metadata.tags.append(f"quality_{detected_quality}")
            
        except Exception as e:
            logger.error(f"❌ Erreur détection qualité: {e}")
    
    async def _store_l1_cache(self, media_id -> None: str, metadata -> None: MediaMetadata) -> None:
        """**Backend Senior**: Stockage cache L1 avec éviction LRU"""
        
        # Éviction si cache plein
        if len(self.l1_cache) >= self.l1_max_items:
            # LRU éviction
            oldest_id = min(
                self.l1_cache.keys(),
                key=lambda k: self.l1_cache[k].last_accessed
            )
            del self.l1_cache[oldest_id]
            self.cache_metrics.eviction_count += 1
        
        self.l1_cache[media_id] = metadata
        self.cache_metrics.total_cached_items += 1
    
    async def _store_redis_cache(self, media_id -> None: str, metadata -> None: MediaMetadata) -> None:
        """**Backend Senior**: Stockage Redis avec compression"""
        
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                # Sérialisation métadonnées
                metadata_dict = {
                    "media_id": metadata.media_id,
                    "filename": metadata.filename,
                    "original_filename": metadata.original_filename,
                    "content_hash": metadata.content_hash,
                    "media_type": metadata.media_type.value,
                    "mime_type": metadata.mime_type,
                    "file_size": metadata.file_size,
                    "duration": metadata.duration,
                    "width": metadata.width,
                    "height": metadata.height,
                    "aspect_ratio": metadata.aspect_ratio,
                    "sample_rate": metadata.sample_rate,
                    "bit_rate": metadata.bit_rate,
                    "channels": metadata.channels,
                    "audio_codec": metadata.audio_codec,
                    "video_codec": metadata.video_codec,
                    "frame_rate": metadata.frame_rate,
                    "color_space": metadata.color_space,
                    "creator_id": metadata.creator_id,
                    "created_at": metadata.created_at,
                    "uploaded_at": metadata.uploaded_at,
                    "tags": metadata.tags,
                    "auto_tags": metadata.auto_tags,
                    "categories": metadata.categories,
                    "mood_tags": metadata.mood_tags,
                    "privacy_level": metadata.privacy_level,
                    "monetization_enabled": metadata.monetization_enabled,
                    "copyright_status": metadata.copyright_status,
                    "view_count": metadata.view_count,
                    "download_count": metadata.download_count,
                    "share_count": metadata.share_count,
                    "like_count": metadata.like_count,
                    "version": metadata.version,
                    "variants": metadata.variants,
                    "thumbnails": metadata.thumbnails,
                    "processing_status": metadata.processing_status,
                    "ai_analysis_completed": metadata.ai_analysis_completed,
                    "cached_at": metadata.cached_at,
                    "cache_hit_count": metadata.cache_hit_count,
                    "last_accessed": metadata.last_accessed
                }
                
                # Stockage avec TTL
                cache_key = f"media_metadata:{media_id}"
                await redis_conn.setex(
                    cache_key,
                    self.default_ttl,
                    json.dumps(metadata_dict)
                )
                
                # Index secondaires Redis
                await self._update_redis_indexes(redis_conn, media_id, metadata)
                
        except Exception as e:
            logger.error(f"❌ Erreur stockage Redis {media_id}: {e}")
    
    async def _get_redis_cache(self, media_id: str) -> Optional[MediaMetadata]:
        """**Backend Senior**: Récupération Redis avec désérialisation"""
        
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                cache_key = f"media_metadata:{media_id}"
                metadata_json = await redis_conn.get(cache_key)
                
                if metadata_json:
                    metadata_dict = json.loads(metadata_json)
                    
                    # Reconstruction objet MediaMetadata
                    metadata = MediaMetadata(
                        media_id=metadata_dict["media_id"],
                        filename=metadata_dict["filename"],
                        original_filename=metadata_dict["original_filename"],
                        content_hash=metadata_dict["content_hash"],
                        media_type=MediaType(metadata_dict["media_type"]),
                        mime_type=metadata_dict["mime_type"],
                        file_size=metadata_dict["file_size"],
                        duration=metadata_dict.get("duration"),
                        width=metadata_dict.get("width"),
                        height=metadata_dict.get("height"),
                        aspect_ratio=metadata_dict.get("aspect_ratio"),
                        sample_rate=metadata_dict.get("sample_rate"),
                        bit_rate=metadata_dict.get("bit_rate"),
                        channels=metadata_dict.get("channels"),
                        audio_codec=metadata_dict.get("audio_codec"),
                        video_codec=metadata_dict.get("video_codec"),
                        frame_rate=metadata_dict.get("frame_rate"),
                        color_space=metadata_dict.get("color_space"),
                        creator_id=metadata_dict["creator_id"],
                        created_at=metadata_dict["created_at"],
                        uploaded_at=metadata_dict["uploaded_at"],
                        tags=metadata_dict.get("tags", []),
                        auto_tags=metadata_dict.get("auto_tags", []),
                        categories=metadata_dict.get("categories", []),
                        mood_tags=metadata_dict.get("mood_tags", []),
                        privacy_level=metadata_dict.get("privacy_level", "private"),
                        monetization_enabled=metadata_dict.get("monetization_enabled", False),
                        copyright_status=metadata_dict.get("copyright_status", "original"),
                        view_count=metadata_dict.get("view_count", 0),
                        download_count=metadata_dict.get("download_count", 0),
                        share_count=metadata_dict.get("share_count", 0),
                        like_count=metadata_dict.get("like_count", 0),
                        version=metadata_dict.get("version", "1.0"),
                        variants=metadata_dict.get("variants", {}),
                        thumbnails=metadata_dict.get("thumbnails", {}),
                        processing_status=metadata_dict.get("processing_status", "completed"),
                        ai_analysis_completed=metadata_dict.get("ai_analysis_completed", False),
                        cached_at=metadata_dict.get("cached_at", time.time()),
                        cache_hit_count=metadata_dict.get("cache_hit_count", 0),
                        last_accessed=metadata_dict.get("last_accessed", time.time())
                    )
                    
                    return metadata
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération Redis {media_id}: {e}")
            return None
    
    async def _update_indexes(self, media_id -> None: str, metadata -> None: MediaMetadata) -> None:
        """**Backend Senior**: Mise à jour index pour recherche rapide"""
        
        # Index par créateur
        self.creator_index[metadata.creator_id].add(media_id)
        
        # Index par type
        self.type_index[metadata.media_type].add(media_id)
        
        # Index par tags
        all_tags = metadata.tags + metadata.auto_tags + metadata.categories
        for tag in all_tags:
            self.tag_index[tag.lower()].add(media_id)
    
    async def _update_redis_indexes(self, redis_conn, media_id -> None: str, metadata -> None: MediaMetadata) -> None:
        """**Backend Senior**: Mise à jour index Redis"""
        
        try:
            # Index créateur
            await redis_conn.sadd(f"creator_media:{metadata.creator_id}", media_id)
            
            # Index type média
            await redis_conn.sadd(f"media_type:{metadata.media_type.value}", media_id)
            
            # Index tags
            all_tags = metadata.tags + metadata.auto_tags + metadata.categories
            for tag in all_tags:
                await redis_conn.sadd(f"tag:{tag.lower()}", media_id)
            
            # Index temporel
            date_key = datetime.fromtimestamp(metadata.created_at).strftime("%Y-%m-%d")
            await redis_conn.sadd(f"media_date:{date_key}", media_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour index Redis: {e}")
    
    def _update_hit_ratio(self, is_hit: bool) -> float:
        """**DevOps**: Mise à jour ratio cache hit"""
        if is_hit:
            # Cache hit - pas de mise à jour miss_count
            pass
        else:
            self.cache_metrics.miss_count += 1
        
        total_requests = self.cache_metrics.total_cached_items + self.cache_metrics.miss_count
        if total_requests > 0:
            hits = total_requests - self.cache_metrics.miss_count
            return hits / total_requests
        return 0.0
    
    def _record_access_pattern(self, media_id -> None: str, access_type -> None: str, response_time -> None: float) -> None:
        """**DevOps**: Enregistrement patterns d'accès pour analytics"""
        pattern = {
            "media_id": media_id,
            "access_type": access_type,
            "response_time": response_time,
            "timestamp": time.time()
        }
        self.access_patterns.append(pattern)
    
    def _record_cache_operation(self, operation -> None: str, media_id -> None: str, metadata -> None: MediaMetadata) -> None:
        """**DevOps**: Enregistrement opérations cache pour monitoring"""
        self.cache_metrics.cache_size_bytes += metadata.file_size
        
        # Log pour debugging si nécessaire
        logger.debug(f"📊 Cache {operation}: {media_id} ({metadata.media_type.value})")
    
    async def _cache_maintenance_loop(self) -> None:
        """**DevOps**: Maintenance cache périodique"""
        while True:
            try:
                await asyncio.sleep(3600)  # Maintenance chaque heure
                
                # Nettoyage L1 cache ancien
                current_time = time.time()
                expired_keys = []
                
                for media_id, metadata in self.l1_cache.items():
                    if current_time - metadata.last_accessed > 7200:  # 2h inactif
                        expired_keys.append(media_id)
                
                for key in expired_keys:
                    del self.l1_cache[key]
                    self.cache_metrics.eviction_count += 1
                
                if expired_keys:
                    logger.info(f"🧹 Cache maintenance: {len(expired_keys)} entrées nettoyées")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur maintenance cache: {e}")
    
    async def _analytics_loop(self) -> None:
        """**DevOps**: Boucle analytics et métriques"""
        while True:
            try:
                await asyncio.sleep(300)  # Analytics toutes les 5 minutes
                
                # Mise à jour métriques globales
                await self._update_global_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur analytics: {e}")
    
    async def _ml_processing_loop(self) -> None:
        """**ML Engineer**: Traitement ML périodique"""
        while True:
            try:
                await asyncio.sleep(1800)  # ML processing toutes les 30 minutes
                
                if self.enable_ml_tagging:
                    await self._process_ml_improvements()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur ML processing: {e}")
    
    async def _streaming_optimization_loop(self) -> None:
        """**Audio Engineer**: Optimisation streaming"""
        while True:
            try:
                await asyncio.sleep(600)  # Optimisation toutes les 10 minutes
                
                await self._optimize_streaming_cache()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur optimisation streaming: {e}")
    
    async def get_cache_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics cache complet"""
        
        # Statistiques par type de média
        type_stats = {}
        for media_type, media_ids in self.type_index.items():
            type_stats[media_type.value] = {
                "count": len(media_ids),
                "percentage": len(media_ids) / max(1, self.cache_metrics.total_cached_items) * 100
            }
        
        # Top créateurs par volume
        creator_stats = {
            creator_id: len(media_ids)
            for creator_id, media_ids in list(self.creator_index.items())[:10]
        }
        
        # Tags populaires
        popular_tags = sorted(
            [(tag, len(media_ids)) for tag, media_ids in self.tag_index.items()],
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        return {
            "cache_metrics": {
                "total_items": self.cache_metrics.total_cached_items,
                "cache_size_mb": round(self.cache_metrics.cache_size_bytes / 1024 / 1024, 2),
                "hit_ratio": round(self.cache_metrics.hit_ratio * 100, 2),
                "miss_count": self.cache_metrics.miss_count,
                "eviction_count": self.cache_metrics.eviction_count,
                "l1_cache_size": len(self.l1_cache)
            },
            "content_distribution": type_stats,
            "top_creators": creator_stats,
            "popular_tags": [{"tag": tag, "count": count} for tag, count in popular_tags],
            "performance": {
                "avg_response_time_ms": round(
                    np.mean([p.get("response_time", 0) for p in list(self.access_patterns)[-100:]]) * 1000, 2
                ) if self.access_patterns else 0,
                "streaming_requests": self.cache_metrics.streaming_requests,
                "bandwidth_saved_mb": round(self.cache_metrics.bandwidth_saved_bytes / 1024 / 1024, 2)
            }
        }

# Factory function
async def create_media_metadata_cache(redis_pool, config -> None: Optional[Dict[str, Any]] = None) -> None:
    """**Audio Engineer**: Factory création cache métadonnées média"""
    return MediaMetadataCache(redis_pool, config)

if __name__ == "__main__":
    async def demo() -> None:
        """Démonstration Media Metadata Cache"""
        
        # Configuration Redis simulée
        class MockRedisPool:
    """MockRedisPool: class implementation"""
            def get_connection(self) -> None:
                from unittest.mock import AsyncMock
                return AsyncMock()
        
        # Configuration cache
        config = {
            'cache_strategy': 'adaptive',
            'max_cache_size_gb': 5.0,
            'enable_ml_tagging': True
        }
        
        # Création cache
        cache = await create_media_metadata_cache(MockRedisPool(), config)
        
        # Test métadonnées audio
        audio_metadata = MediaMetadata(
            media_id="audio_001",
            filename="podcast_episode_1.mp3",
            original_filename="My Podcast Episode 1.mp3",
            content_hash="sha256_audio_hash",
            media_type=MediaType.AUDIO,
            mime_type="audio/mpeg",
            file_size=50 * 1024 * 1024,  # 50MB
            duration=3600,  # 1 heure
            sample_rate=48000,
            bit_rate=192000,
            channels=2,
            audio_codec="mp3",
            creator_id="creator_123",
            tags=["podcast", "technology"],
            privacy_level="public"
        )
        
        # Stockage
        success = await cache.store_metadata("audio_001", audio_metadata)
        print(f"Métadonnées audio stockées: {success}")
        
        # Récupération
        retrieved = await cache.get_metadata("audio_001", include_analytics=True)
        print(f"Métadonnées récupérées: {retrieved.filename if retrieved else 'None'}")
        
        # Recherche par créateur
        creator_media = await cache.get_creator_media("creator_123", MediaType.AUDIO)
        print(f"Média du créateur: {len(creator_media)} éléments")
        
        # Analytics
        analytics = await cache.get_cache_analytics()
        print(f"Cache analytics: {analytics['cache_metrics']['total_items']} éléments")
    
    asyncio.run(demo())