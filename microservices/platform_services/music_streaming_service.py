"""
🎵 MUSIC STREAMING SERVICE
Intégration avec 20+ plateformes de streaming musical

Plateformes: Spotify, Apple Music, YouTube Music, Amazon Music, Deezer, SoundCloud
Fonctionnalités: Upload automatique, sync metadata, analytics cross-platform
Workflow: Distribution intelligente basée sur l'audience

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
import time
import json
from dataclasses import dataclass, field
from enum import Enum
import aiohttp

logger = logging.getLogger(__name__)

class StreamingPlatform(Enum):
    """Plateformes de streaming musical supportées"""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TIDAL = "tidal"
    PANDORA = "pandora"
    AUDIOMACK = "audiomack"
    NAPSTER = "napster"
    SHAZAM = "shazam"
    LAST_FM = "last_fm"
    MUSIXMATCH = "musixmatch"
    GENIUS = "genius"
    BEATPORT = "beatport"
    TRAXSOURCE = "traxsource"
    JUNO_DOWNLOAD = "juno_download"
    BEATSTARS = "beatstars"
    DISTROKID = "distrokid"

class DistributionStatus(Enum):
    """Statuts de distribution"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    LIVE = "live"
    FAILED = "failed"
    REJECTED = "rejected"
    TAKEN_DOWN = "taken_down"

@dataclass
class TrackMetadata:
    """Métadonnées d'un track musical"""
    title: str
    artist: str
    album: str
    genre: str
    duration_seconds: int
    release_date: str
    label: str = ""
    composers: List[str] = field(default_factory=list)
    producers: List[str] = field(default_factory=list)
    featured_artists: List[str] = field(default_factory=list)
    explicit: bool = False
    language: str = "en"
    copyright: str = ""
    isrc: str = ""  # International Standard Recording Code
    upc: str = ""   # Universal Product Code
    tags: List[str] = field(default_factory=list)
    lyrics: str = ""
    artwork_url: str = ""
    preview_url: str = ""

@dataclass
class PlatformUpload:
    """Upload vers une plateforme spécifique"""
    platform: StreamingPlatform
    track_id: str
    platform_track_id: str = ""
    upload_url: str = ""
    status: DistributionStatus = DistributionStatus.PENDING
    upload_time: Optional[float] = None
    go_live_time: Optional[float] = None
    platform_specific_metadata: Dict[str, Any] = field(default_factory=dict)
    analytics_enabled: bool = True
    monetization_enabled: bool = True
    error_message: str = ""

@dataclass
class StreamingAnalytics:
    """Analytics de streaming"""
    platform: StreamingPlatform
    track_id: str
    plays: int
    unique_listeners: int
    revenue: float
    revenue_currency: str
    streams_by_country: Dict[str, int] = field(default_factory=dict)
    demographics: Dict[str, Any] = field(default_factory=dict)
    playlist_adds: int = 0
    shares: int = 0
    likes: int = 0
    comments: int = 0
    last_updated: float = 0

class MusicStreamingService:
    """
    🎵 SERVICE STREAMING MUSICAL ENTERPRISE
    
    Distribution automatique vers 20+ plateformes de streaming
    avec analytics unifiées et optimisation des revenus
    """
    
    def __init__(self, service_id: str = None):
        self.service_id = service_id or f"music-streaming-{int(time.time())}"
        self.status = "initializing"
        
        # Configuration des plateformes
        self.platform_configs = {
            StreamingPlatform.SPOTIFY: {
                "api_url": "https://api.spotify.com/v1",
                "auth_url": "https://accounts.spotify.com/api/token",
                "upload_endpoint": "/me/tracks",
                "analytics_endpoint": "/me/player/recently-played",
                "requires_approval": True,
                "processing_time_hours": 24,
                "revenue_share": 0.70,  # 70% to artist
                "supported_formats": ["mp3", "flac", "wav"],
                "max_file_size_mb": 200,
                "metadata_requirements": ["title", "artist", "album", "genre"]
            },
            StreamingPlatform.APPLE_MUSIC: {
                "api_url": "https://api.music.apple.com/v1",
                "auth_url": "https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa",
                "upload_endpoint": "/catalog/tracks",
                "analytics_endpoint": "/analytics/songs",
                "requires_approval": True,
                "processing_time_hours": 48,
                "revenue_share": 0.68,
                "supported_formats": ["mp3", "aac", "flac"],
                "max_file_size_mb": 300,
                "metadata_requirements": ["title", "artist", "album", "isrc"]
            },
            StreamingPlatform.YOUTUBE_MUSIC: {
                "api_url": "https://music.youtube.com/youtubei/v1",
                "auth_url": "https://accounts.google.com/oauth2/token",
                "upload_endpoint": "/upload",
                "analytics_endpoint": "/analytics",
                "requires_approval": False,
                "processing_time_hours": 2,
                "revenue_share": 0.55,
                "supported_formats": ["mp3", "wav", "flac", "aac"],
                "max_file_size_mb": 500,
                "metadata_requirements": ["title", "artist"]
            },
            StreamingPlatform.SOUNDCLOUD: {
                "api_url": "https://api.soundcloud.com",
                "auth_url": "https://api.soundcloud.com/oauth2/token",
                "upload_endpoint": "/tracks",
                "analytics_endpoint": "/me/tracks/stats",
                "requires_approval": False,
                "processing_time_hours": 0.5,
                "revenue_share": 0.85,  # Premium account
                "supported_formats": ["mp3", "wav", "flac", "aiff"],
                "max_file_size_mb": 1000,
                "metadata_requirements": ["title", "artist"]
            },
            StreamingPlatform.DEEZER: {
                "api_url": "https://api.deezer.com",
                "upload_endpoint": "/upload",
                "analytics_endpoint": "/artist/stats",
                "requires_approval": True,
                "processing_time_hours": 72,
                "revenue_share": 0.65,
                "supported_formats": ["mp3", "flac"],
                "max_file_size_mb": 250,
                "metadata_requirements": ["title", "artist", "album", "isrc"]
            }
        }
        
        # Uploads actifs
        self.active_uploads: Dict[str, List[PlatformUpload]] = {}
        
        # Analytics cache
        self.analytics_cache: Dict[str, List[StreamingAnalytics]] = {}
        self.analytics_cache_duration = 3600  # 1 heure
        
        # Distribution stats
        self.distribution_stats = {
            "total_uploads": 0,
            "successful_uploads": 0,
            "failed_uploads": 0,
            "total_streams": 0,
            "total_revenue": 0.0,
            "platform_performance": {}
        }
        
    async def initialize(self) -> bool:
        """Initialiser le service de streaming musical"""
        logger.info("🎵 Initializing Music Streaming Service...")
        
        try:
            # Tester la connectivité aux plateformes principales
            await self._test_platform_connectivity()
            
            # Charger les configurations personnalisées
            await self._load_platform_credentials()
            
            self.status = "ready"
            logger.info("✅ Music Streaming Service initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Music Streaming Service: {e}")
            self.status = "error"
            return False
    
    async def _test_platform_connectivity(self) -> None:
        """Tester la connectivité aux plateformes"""
        for platform in [StreamingPlatform.SOUNDCLOUD, StreamingPlatform.YOUTUBE_MUSIC]:
            try:
                # Test simple de connectivité
                config = self.platform_configs[platform]
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        config["api_url"], 
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status in [200, 401, 403]:  # 401/403 = auth required (bon signe)
                            logger.info(f"✅ {platform.value} API is reachable")
                        else:
                            logger.warning(f"⚠️ {platform.value} API returned {response.status}")
                            
            except Exception as e:
                logger.warning(f"⚠️ {platform.value} connectivity test failed: {e}")
    
    async def _load_platform_credentials(self) -> None:
        """Charger les credentials des plateformes"""
        # En production, charger depuis des variables d'environnement sécurisées
        self.platform_credentials = {
            StreamingPlatform.SPOTIFY: {
                "client_id": "spotify_client_id",
                "client_secret": "spotify_client_secret",
                "access_token": None
            },
            StreamingPlatform.APPLE_MUSIC: {
                "team_id": "apple_team_id",
                "key_id": "apple_key_id",
                "private_key": "apple_private_key",
                "access_token": None
            },
            StreamingPlatform.YOUTUBE_MUSIC: {
                "client_id": "youtube_client_id",
                "client_secret": "youtube_client_secret",
                "api_key": "youtube_api_key",
                "access_token": None
            },
            StreamingPlatform.SOUNDCLOUD: {
                "client_id": "soundcloud_client_id",
                "client_secret": "soundcloud_client_secret",
                "access_token": "soundcloud_access_token"
            }
        }
    
    async def distribute_track(
        self,
        track_id: str,
        track_metadata: TrackMetadata,
        audio_file_url: str,
        target_platforms: List[StreamingPlatform] = None,
        distribution_strategy: str = "all_platforms"
    ) -> Dict[str, Any]:
        """
        Distribuer un track sur les plateformes de streaming
        
        Args:
            track_id: Identifiant unique du track
            track_metadata: Métadonnées du track
            audio_file_url: URL du fichier audio
            target_platforms: Plateformes cibles (None = toutes)
            distribution_strategy: Stratégie de distribution
        """
        logger.info(f"🎵 Starting distribution for track: {track_metadata.title}")
        
        try:
            # Déterminer les plateformes cibles
            if target_platforms is None:
                target_platforms = await self._select_optimal_platforms(
                    track_metadata, 
                    distribution_strategy
                )
            
            # Valider les métadonnées pour chaque plateforme
            validated_platforms = []
            for platform in target_platforms:
                if await self._validate_track_for_platform(track_metadata, platform):
                    validated_platforms.append(platform)
                else:
                    logger.warning(f"Track validation failed for {platform.value}")
            
            # Créer les uploads
            uploads = []
            for platform in validated_platforms:
                upload = PlatformUpload(
                    platform=platform,
                    track_id=track_id,
                    status=DistributionStatus.PENDING
                )
                uploads.append(upload)
            
            self.active_uploads[track_id] = uploads
            
            # Démarrer les uploads en parallèle
            upload_tasks = []
            for upload in uploads:
                task = asyncio.create_task(
                    self._upload_to_platform(track_metadata, audio_file_url, upload)
                )
                upload_tasks.append(task)
            
            # Attendre tous les uploads (avec timeout)
            upload_results = await asyncio.gather(*upload_tasks, return_exceptions=True)
            
            # Analyser les résultats
            successful_uploads = 0
            failed_uploads = 0
            
            for i, result in enumerate(upload_results):
                upload = uploads[i]
                if isinstance(result, Exception):
                    upload.status = DistributionStatus.FAILED
                    upload.error_message = str(result)
                    failed_uploads += 1
                    logger.error(f"Upload failed for {upload.platform.value}: {result}")
                else:
                    upload.status = DistributionStatus.UPLOADING
                    successful_uploads += 1
                    logger.info(f"Upload started for {upload.platform.value}")
            
            # Mettre à jour les statistiques
            self.distribution_stats["total_uploads"] += len(uploads)
            self.distribution_stats["successful_uploads"] += successful_uploads
            self.distribution_stats["failed_uploads"] += failed_uploads
            
            distribution_result = {
                "track_id": track_id,
                "track_title": track_metadata.title,
                "total_platforms": len(target_platforms),
                "validated_platforms": len(validated_platforms),
                "successful_uploads": successful_uploads,
                "failed_uploads": failed_uploads,
                "uploads": [
                    {
                        "platform": upload.platform.value,
                        "status": upload.status.value,
                        "error": upload.error_message if upload.error_message else None
                    }
                    for upload in uploads
                ],
                "estimated_go_live": await self._calculate_estimated_go_live(uploads)
            }
            
            logger.info(f"✅ Distribution initiated: {successful_uploads}/{len(uploads)} uploads started")
            return distribution_result
            
        except Exception as e:
            logger.error(f"❌ Track distribution failed: {e}")
            raise
    
    async def _select_optimal_platforms(
        self, 
        track_metadata: TrackMetadata, 
        strategy: str
    ) -> List[StreamingPlatform]:
        """Sélectionner les plateformes optimales selon la stratégie"""
        
        if strategy == "all_platforms":
            return list(StreamingPlatform)
        
        elif strategy == "major_platforms":
            return [
                StreamingPlatform.SPOTIFY,
                StreamingPlatform.APPLE_MUSIC,
                StreamingPlatform.YOUTUBE_MUSIC,
                StreamingPlatform.AMAZON_MUSIC,
                StreamingPlatform.DEEZER
            ]
        
        elif strategy == "free_platforms":
            return [
                StreamingPlatform.SOUNDCLOUD,
                StreamingPlatform.YOUTUBE_MUSIC,
                StreamingPlatform.BANDCAMP
            ]
        
        elif strategy == "genre_optimized":
            # Sélection basée sur le genre
            genre_platforms = {
                "electronic": [StreamingPlatform.SOUNDCLOUD, StreamingPlatform.BEATPORT, StreamingPlatform.BANDCAMP],
                "hip-hop": [StreamingPlatform.SOUNDCLOUD, StreamingPlatform.AUDIOMACK, StreamingPlatform.SPOTIFY],
                "pop": [StreamingPlatform.SPOTIFY, StreamingPlatform.APPLE_MUSIC, StreamingPlatform.YOUTUBE_MUSIC],
                "rock": [StreamingPlatform.SPOTIFY, StreamingPlatform.BANDCAMP, StreamingPlatform.DEEZER],
                "jazz": [StreamingPlatform.TIDAL, StreamingPlatform.DEEZER, StreamingPlatform.BANDCAMP]
            }
            
            return genre_platforms.get(track_metadata.genre.lower(), [StreamingPlatform.SPOTIFY])
        
        # Par défaut, plateformes principales
        return [StreamingPlatform.SPOTIFY, StreamingPlatform.SOUNDCLOUD, StreamingPlatform.YOUTUBE_MUSIC]
    
    async def _validate_track_for_platform(
        self, 
        track_metadata: TrackMetadata, 
        platform: StreamingPlatform
    ) -> bool:
        """Valider qu'un track peut être uploadé sur une plateforme"""
        config = self.platform_configs.get(platform, {})
        requirements = config.get("metadata_requirements", [])
        
        # Vérifier les métadonnées requises
        metadata_dict = {
            "title": track_metadata.title,
            "artist": track_metadata.artist,
            "album": track_metadata.album,
            "genre": track_metadata.genre,
            "isrc": track_metadata.isrc,
            "upc": track_metadata.upc
        }
        
        for requirement in requirements:
            if not metadata_dict.get(requirement):
                logger.warning(f"Missing required metadata '{requirement}' for {platform.value}")
                return False
        
        # Vérifier les contraintes spécifiques
        if platform == StreamingPlatform.APPLE_MUSIC and not track_metadata.isrc:
            return False
        
        if platform == StreamingPlatform.SPOTIFY and track_metadata.duration_seconds < 30:
            return False  # Spotify require minimum 30 seconds
        
        return True
    
    async def _upload_to_platform(
        self,
        track_metadata: TrackMetadata,
        audio_file_url: str,
        upload: PlatformUpload
    ) -> bool:
        """Uploader vers une plateforme spécifique"""
        platform = upload.platform
        config = self.platform_configs[platform]
        
        logger.info(f"🎵 Uploading to {platform.value}...")
        
        try:
            upload.status = DistributionStatus.UPLOADING
            upload.upload_time = time.time()
            
            # Simuler l'upload (en production, implémentation réelle par plateforme)
            await asyncio.sleep(0.5)  # Simulation temps upload
            
            if platform == StreamingPlatform.SOUNDCLOUD:
                result = await self._upload_to_soundcloud(track_metadata, audio_file_url, upload)
            elif platform == StreamingPlatform.SPOTIFY:
                result = await self._upload_to_spotify(track_metadata, audio_file_url, upload)
            elif platform == StreamingPlatform.YOUTUBE_MUSIC:
                result = await self._upload_to_youtube_music(track_metadata, audio_file_url, upload)
            else:
                # Upload générique
                result = await self._generic_platform_upload(track_metadata, audio_file_url, upload)
            
            if result:
                upload.status = DistributionStatus.PROCESSING
                upload.platform_track_id = result.get("track_id", f"{platform.value}_{upload.track_id}")
                
                # Calculer le temps de mise en ligne estimé
                processing_hours = config.get("processing_time_hours", 24)
                upload.go_live_time = time.time() + (processing_hours * 3600)
                
                return True
            else:
                upload.status = DistributionStatus.FAILED
                upload.error_message = "Upload failed"
                return False
                
        except Exception as e:
            upload.status = DistributionStatus.FAILED
            upload.error_message = str(e)
            logger.error(f"Upload to {platform.value} failed: {e}")
            return False
    
    async def _upload_to_soundcloud(
        self, 
        track_metadata: TrackMetadata,
        audio_file_url: str,
        upload: PlatformUpload
    ) -> Optional[Dict[str, Any]]:
        """Upload spécifique SoundCloud"""
        # Simulation - en production, utiliser l'API SoundCloud
        await asyncio.sleep(0.2)
        
        return {
            "track_id": f"sc_{upload.track_id}",
            "permalink_url": f"https://soundcloud.com/user/{track_metadata.title.lower().replace(' ', '-')}",
            "artwork_url": track_metadata.artwork_url,
            "stream_url": f"https://api.soundcloud.com/tracks/sc_{upload.track_id}/stream"
        }
    
    async def _upload_to_spotify(
        self,
        track_metadata: TrackMetadata,
        audio_file_url: str,
        upload: PlatformUpload
    ) -> Optional[Dict[str, Any]]:
        """Upload spécifique Spotify"""
        # Simulation - en production, utiliser Spotify for Artists API
        await asyncio.sleep(0.3)
        
        return {
            "track_id": f"spotify_{upload.track_id}",
            "uri": f"spotify:track:{upload.track_id}",
            "external_urls": {
                "spotify": f"https://open.spotify.com/track/{upload.track_id}"
            }
        }
    
    async def _upload_to_youtube_music(
        self,
        track_metadata: TrackMetadata,
        audio_file_url: str,
        upload: PlatformUpload
    ) -> Optional[Dict[str, Any]]:
        """Upload spécifique YouTube Music"""
        # Simulation - en production, utiliser YouTube Data API
        await asyncio.sleep(0.1)
        
        return {
            "track_id": f"yt_{upload.track_id}",
            "video_id": f"yt_video_{upload.track_id}",
            "watch_url": f"https://music.youtube.com/watch?v=yt_{upload.track_id}"
        }
    
    async def _generic_platform_upload(
        self,
        track_metadata: TrackMetadata,
        audio_file_url: str,
        upload: PlatformUpload
    ) -> Optional[Dict[str, Any]]:
        """Upload générique pour autres plateformes"""
        await asyncio.sleep(0.2)
        
        return {
            "track_id": f"{upload.platform.value}_{upload.track_id}",
            "status": "uploaded"
        }
    
    async def _calculate_estimated_go_live(self, uploads: List[PlatformUpload]) -> Dict[str, Any]:
        """Calculer les temps estimés de mise en ligne"""
        earliest_live = None
        latest_live = None
        
        for upload in uploads:
            if upload.go_live_time:
                if earliest_live is None or upload.go_live_time < earliest_live:
                    earliest_live = upload.go_live_time
                if latest_live is None or upload.go_live_time > latest_live:
                    latest_live = upload.go_live_time
        
        return {
            "earliest_platform_live": earliest_live,
            "latest_platform_live": latest_live,
            "all_platforms_live_estimate": latest_live
        }
    
    async def get_track_analytics(
        self, 
        track_id: str, 
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """Obtenir les analytics d'un track sur toutes les plateformes"""
        logger.info(f"📊 Fetching analytics for track: {track_id}")
        
        # Vérifier le cache
        cache_key = f"{track_id}_{time_range}"
        if cache_key in self.analytics_cache:
            cached_data = self.analytics_cache[cache_key]
            if time.time() - cached_data[0].last_updated < self.analytics_cache_duration:
                return self._format_analytics_response(cached_data)
        
        # Récupérer les analytics de chaque plateforme
        analytics_list = []
        uploads = self.active_uploads.get(track_id, [])
        
        for upload in uploads:
            if upload.status == DistributionStatus.LIVE:
                platform_analytics = await self._fetch_platform_analytics(
                    upload.platform,
                    upload.platform_track_id,
                    time_range
                )
                if platform_analytics:
                    analytics_list.append(platform_analytics)
        
        # Mettre en cache
        self.analytics_cache[cache_key] = analytics_list
        
        return self._format_analytics_response(analytics_list)
    
    async def _fetch_platform_analytics(
        self,
        platform: StreamingPlatform,
        platform_track_id: str,
        time_range: str
    ) -> Optional[StreamingAnalytics]:
        """Récupérer les analytics d'une plateforme spécifique"""
        
        # Simulation des analytics - en production, appels API réels
        mock_analytics = {
            StreamingPlatform.SPOTIFY: {
                "plays": 15420,
                "unique_listeners": 8932,
                "revenue": 45.67,
                "streams_by_country": {"US": 6234, "UK": 2341, "DE": 1876, "FR": 1654},
                "playlist_adds": 234,
                "shares": 67,
                "likes": 892
            },
            StreamingPlatform.SOUNDCLOUD: {
                "plays": 8765,
                "unique_listeners": 5432,
                "revenue": 12.34,
                "streams_by_country": {"US": 3456, "UK": 1234, "CA": 876},
                "playlist_adds": 89,
                "shares": 234,
                "likes": 567
            },
            StreamingPlatform.YOUTUBE_MUSIC: {
                "plays": 23456,
                "unique_listeners": 12345,
                "revenue": 78.90,
                "streams_by_country": {"US": 9876, "IN": 4567, "BR": 3456},
                "playlist_adds": 456,
                "shares": 123,
                "likes": 1234
            }
        }
        
        data = mock_analytics.get(platform, {})
        
        return StreamingAnalytics(
            platform=platform,
            track_id=platform_track_id,
            plays=data.get("plays", 0),
            unique_listeners=data.get("unique_listeners", 0),
            revenue=data.get("revenue", 0.0),
            revenue_currency="USD",
            streams_by_country=data.get("streams_by_country", {}),
            playlist_adds=data.get("playlist_adds", 0),
            shares=data.get("shares", 0),
            likes=data.get("likes", 0),
            last_updated=time.time()
        )
    
    def _format_analytics_response(self, analytics_list: List[StreamingAnalytics]) -> Dict[str, Any]:
        """Formater la réponse analytics consolidée"""
        if not analytics_list:
            return {
                "total_plays": 0,
                "total_unique_listeners": 0,
                "total_revenue": 0.0,
                "platforms": [],
                "top_countries": {},
                "summary": "No analytics data available"
            }
        
        # Consolidation des métriques
        total_plays = sum(a.plays for a in analytics_list)
        total_unique_listeners = sum(a.unique_listeners for a in analytics_list)
        total_revenue = sum(a.revenue for a in analytics_list)
        
        # Consolidation par pays
        all_countries = {}
        for analytics in analytics_list:
            for country, streams in analytics.streams_by_country.items():
                all_countries[country] = all_countries.get(country, 0) + streams
        
        # Top 10 pays
        top_countries = dict(sorted(all_countries.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Détails par plateforme
        platform_details = []
        for analytics in analytics_list:
            platform_details.append({
                "platform": analytics.platform.value,
                "plays": analytics.plays,
                "unique_listeners": analytics.unique_listeners,
                "revenue": analytics.revenue,
                "market_share": round((analytics.plays / total_plays) * 100, 2) if total_plays > 0 else 0,
                "playlist_adds": analytics.playlist_adds,
                "engagement_score": analytics.likes + analytics.shares + analytics.playlist_adds
            })
        
        return {
            "total_plays": total_plays,
            "total_unique_listeners": total_unique_listeners,
            "total_revenue": round(total_revenue, 2),
            "revenue_currency": "USD",
            "platforms_count": len(analytics_list),
            "platforms": platform_details,
            "top_countries": top_countries,
            "performance_summary": {
                "best_performing_platform": max(platform_details, key=lambda x: x["plays"])["platform"] if platform_details else None,
                "highest_revenue_platform": max(platform_details, key=lambda x: x["revenue"])["platform"] if platform_details else None,
                "average_plays_per_platform": round(total_plays / len(analytics_list), 0) if analytics_list else 0
            }
        }
    
    async def get_distribution_status(self, track_id: str) -> Dict[str, Any]:
        """Obtenir le statut de distribution d'un track"""
        uploads = self.active_uploads.get(track_id, [])
        
        if not uploads:
            return {
                "track_id": track_id,
                "status": "not_found",
                "message": "No distribution found for this track"
            }
        
        platform_statuses = []
        for upload in uploads:
            platform_statuses.append({
                "platform": upload.platform.value,
                "status": upload.status.value,
                "upload_time": upload.upload_time,
                "estimated_go_live": upload.go_live_time,
                "platform_track_id": upload.platform_track_id,
                "error_message": upload.error_message if upload.error_message else None
            })
        
        # Statut global
        statuses = [upload.status for upload in uploads]
        if all(s == DistributionStatus.LIVE for s in statuses):
            overall_status = "live"
        elif any(s == DistributionStatus.FAILED for s in statuses):
            overall_status = "partial"
        elif any(s in [DistributionStatus.UPLOADING, DistributionStatus.PROCESSING] for s in statuses):
            overall_status = "in_progress"
        else:
            overall_status = "pending"
        
        return {
            "track_id": track_id,
            "overall_status": overall_status,
            "platforms": platform_statuses,
            "total_platforms": len(uploads),
            "live_platforms": len([u for u in uploads if u.status == DistributionStatus.LIVE]),
            "failed_platforms": len([u for u in uploads if u.status == DistributionStatus.FAILED])
        }
    
    def get_supported_platforms(self) -> List[Dict[str, Any]]:
        """Obtenir la liste des plateformes supportées"""
        platforms_info = []
        
        for platform in StreamingPlatform:
            config = self.platform_configs.get(platform, {})
            platforms_info.append({
                "platform": platform.value,
                "name": platform.value.replace("_", " ").title(),
                "requires_approval": config.get("requires_approval", True),
                "processing_time_hours": config.get("processing_time_hours", 24),
                "revenue_share": config.get("revenue_share", 0.70),
                "supported_formats": config.get("supported_formats", ["mp3"]),
                "max_file_size_mb": config.get("max_file_size_mb", 200),
                "metadata_requirements": config.get("metadata_requirements", [])
            })
        
        return platforms_info
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtenir le statut du service"""
        return {
            "service_id": self.service_id,
            "status": self.status,
            "supported_platforms": len(StreamingPlatform),
            "active_uploads": len(self.active_uploads),
            "total_distributions": self.distribution_stats["total_uploads"],
            "success_rate": round(
                (self.distribution_stats["successful_uploads"] / max(1, self.distribution_stats["total_uploads"])) * 100, 
                2
            ),
            "distribution_stats": self.distribution_stats
        }

# Instance globale du service
music_streaming_service = MusicStreamingService()

async def main():
    """Test du service de streaming musical"""
    await music_streaming_service.initialize()
    
    # Créer des métadonnées de test
    track_metadata = TrackMetadata(
        title="Test Song",
        artist="Test Artist", 
        album="Test Album",
        genre="Electronic",
        duration_seconds=180,
        release_date="2024-01-01",
        explicit=False,
        isrc="TEST123456789",
        tags=["electronic", "dance", "test"]
    )
    
    # Test de distribution
    result = await music_streaming_service.distribute_track(
        track_id="test_track_123",
        track_metadata=track_metadata,
        audio_file_url="https://example.com/test_track.mp3",
        target_platforms=[StreamingPlatform.SOUNDCLOUD, StreamingPlatform.SPOTIFY],
        distribution_strategy="major_platforms"
    )
    
    print(f"Distribution result: {result}")
    
    # Test du statut
    status = await music_streaming_service.get_distribution_status("test_track_123")
    print(f"Distribution status: {status}")
    
    # Test des plateformes supportées
    platforms = music_streaming_service.get_supported_platforms()
    print(f"Supported platforms: {len(platforms)} total")

if __name__ == "__main__":
    asyncio.run(main())