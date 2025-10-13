"""
Creator Streaming Orchestrator - Orchestration streaming multi-créateurs

Système avancé d'orchestration des sessions streaming pour différents types de créateurs
avec support multi-plateforme, analytics temps réel et optimisation intelligente.

Copyright (c) 2025 Fahed Mlaiel (mlaiel@live.de)
Protected by copyright - All rights reserved
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from uuid import uuid4
import json


logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """
        Types de créateurs supportés"""
    GAMER = "gamer"
    MUSICIAN = "musician"
    ARTIST = "artist"
    PODCASTER = "podcaster"
    EDUCATOR = "educator"
    VLOGGER = "vlogger"
    DEVELOPER = "developer"
    CHEF = "chef"
    FITNESS = "fitness"
    BEAUTY = "beauty"
    BUSINESS = "business"
    OTHER = "other"


class ContentType(Enum):
    """Types de contenu streaming"""
    GAMING = "gaming"
    MUSIC = "music"
    ART = "art"
    TALK = "talk"
    TUTORIAL = "tutorial"
    VLOG = "vlog"
    CODING = "coding"
    COOKING = "cooking"
    WORKOUT = "workout"
    MAKEUP = "makeup"
    BUSINESS_TALK = "business_talk"
    GENERAL = "general"


class StreamingStatus(Enum):
    """Statuts de session streaming"""
    SCHEDULED = "scheduled"
    STARTING = "starting"
    LIVE = "live"
    PAUSED = "paused"
    ENDING = "ending"
    ENDED = "ended"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PlatformType(Enum):
    """Plateformes de streaming supportées"""
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    DISCORD = "discord"
    KICK = "kick"
    TROVO = "trovo"
    DLIVE = "dlive"
    CUSTOM = "custom"


@dataclass
class StreamingConfig:
    """Configuration d'une session streaming"""
    title: str
    description: str
    platforms: List[PlatformType]
    content_type: ContentType
    creator_type: CreatorType
    quality: str = "1080p60"
    bitrate: int = 6000
    enable_chat: bool = True
    enable_donations: bool = True
    enable_recording: bool = True
    enable_transcoding: bool = True
    enable_analytics: bool = True
    max_viewers: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # minutes
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    language: str = "en"
    age_restriction: Optional[int] = None
    enable_clips: bool = True
    enable_highlights: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamingMetrics:
    """Métriques en temps réel d'une session"""
    session_id: str
    current_viewers: int = 0
    peak_viewers: int = 0
    total_views: int = 0
    average_viewers: int = 0
    chat_messages: int = 0
    likes: int = 0
    shares: int = 0
    donations_count: int = 0
    donations_total: float = 0.0
    new_followers: int = 0
    new_subscribers: int = 0
    watch_time_minutes: int = 0
    engagement_rate: float = 0.0
    quality_drops: int = 0
    buffering_events: int = 0
    platform_breakdown: Dict[PlatformType, int] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StreamingAnalytics:
    """
        Analytics détaillées post-streaming"""
    session_id: str
    creator_id: str
    total_duration: int  # minutes
    metrics: StreamingMetrics
    viewer_demographics: Dict[str, Any] = field(default_factory=dict)
    peak_moments: List[Dict[str, Any]] = field(default_factory=list)
    chat_sentiment: Dict[str, float] = field(default_factory=dict)
    revenue_breakdown: Dict[str, float] = field(default_factory=dict)
    platform_performance: Dict[PlatformType, Dict[str, Any]] = field(default_factory=dict)
    content_insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreatorStreamingSession:
    """
        Session de streaming complète d'un créateur"""
    session_id: str
    creator_id: str
    creator_name: str
    config: StreamingConfig
    status: StreamingStatus
    stream_key: str
    rtmp_urls: Dict[PlatformType, str]
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    metrics: Optional[StreamingMetrics] = None
    analytics: Optional[StreamingAnalytics] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CreatorStreamingOrchestrator:
    """
    Orchestrateur principal pour la gestion des sessions streaming multi-créateurs
    
    Fonctionnalités:
    - Création et gestion de sessions streaming
    - Support multi-plateforme simultané
    - Métriques et analytics en temps réel
    - Optimisation qualité et performance
    - Gestion événements et notifications
    """
    
    def __init__(self, redis_client: Optional[Any] = None):
        """
        Initialise l'orchestrateur streaming
        
        Args:
            redis_client: Client Redis optionnel pour cache distribué
        """
        self.redis_client = redis_client
        self.active_sessions: Dict[str, CreatorStreamingSession] = {}
        self.scheduled_sessions: Dict[str, CreatorStreamingSession] = {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration RTMP par plateforme
        self.rtmp_endpoints = {
            PlatformType.TWITCH: "rtmp://live.twitch.tv/app/",
            PlatformType.YOUTUBE: "rtmp://a.rtmp.youtube.com/live2/",
            PlatformType.FACEBOOK: "rtmps://live-api-s.facebook.com:443/rtmp/",
            PlatformType.INSTAGRAM: "rtmps://live-upload.instagram.com:443/rtmp/",
            PlatformType.KICK: "rtmp://stream.kick.com:1935/live/",
            PlatformType.TROVO: "rtmp://live.trovo.live/live/",
            PlatformType.DLIVE: "rtmp://stream.dlive.tv/live/",
        }
        
        self.logger.info("CreatorStreamingOrchestrator initialized")
    
    async def create_session(
        self,
        creator_id: str,
        creator_name: str,
        config: StreamingConfig
    ) -> CreatorStreamingSession:
        """
        Crée une nouvelle session streaming
        
        Args:
            creator_id: ID unique du créateur
            creator_name: Nom du créateur
            config: Configuration de la session
            
        Returns:
            Session streaming créée
        """
        session_id = str(uuid4())

        stream_key = self._generate_stream_key(creator_id)
        
        # Générer URLs RTMP pour chaque plateforme

        rtmp_urls = {}
        for platform in config.platforms:
            if platform in self.rtmp_endpoints:
                rtmp_urls[platform] = f"{self.rtmp_endpoints[platform]}{stream_key}"
        
        # Créer métriques initiales

        metrics = StreamingMetrics(session_id=session_id)
        
        # Créer session

        session = CreatorStreamingSession(
            session_id=session_id,
            creator_id=creator_id,
            creator_name=creator_name,
            config=config,
            status=StreamingStatus.SCHEDULED if config.scheduled_start else StreamingStatus.STARTING,
            stream_key=stream_key,
            rtmp_urls=rtmp_urls,
            created_at=datetime.utcnow(),
            metrics=metrics
        )

        
        if config.scheduled_start:
            self.scheduled_sessions[session_id] = session
        else:
            self.active_sessions[session_id] = session
        
        self.logger.info(
            f"Created streaming session {session_id} for creator {creator_name} "
            f"on platforms: {[p.value for p in config.platforms]}"
        )

        
        return session
    
    async def start_session(self, session_id: str) -> bool:
        """
        Démarre une session streaming
        
        Args:
            session_id: ID de la session
            
        Returns:
            True si démarrage réussi
        """
        session = self._get_session(session_id)
        if not session:
            self.logger.error(f"Session {session_id} not found")

            return False
        
        if session.status == StreamingStatus.LIVE:
            self.logger.warning(f"Session {session_id} already live")

            return True
        
        try:
            session.status = StreamingStatus.STARTING
            session.started_at = datetime.utcnow()
            
            # Initialiser streaming sur chaque plateforme
            await self._initialize_platforms(session)
            
            # Démarrer monitoring métriques
            asyncio.create_task(self._monitor_metrics(session_id))

            
            session.status = StreamingStatus.LIVE
            self.active_sessions[session_id] = session
            
            self.logger.info(f"Started streaming session {session_id}")

            return True
            
        except Exception as e:
            session.status = StreamingStatus.FAILED
            session.error_message = str(e)

            self.logger.error(f"Failed to start session {session_id}: {e}")

            return False
    
    async def stop_session(self, session_id: str) -> Optional[StreamingAnalytics]:
        """
        Arrête une session streaming et génère les analytics
        
        Args:
            session_id: ID de la session
            
        Returns:
            Analytics de la session
        """
        session = self._get_session(session_id)
        if not session:
            return None
        
        try:
            session.status = StreamingStatus.ENDING
            session.ended_at = datetime.utcnow()
            
            # Arrêter streaming sur chaque plateforme
            await self._shutdown_platforms(session)
            
            # Générer analytics finales

            analytics = await self._generate_analytics(session)

            session.analytics = analytics
            session.status = StreamingStatus.ENDED
            
            # Nettoyer session active
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            self.logger.info(f"Stopped streaming session {session_id}")

            return analytics
            
        except Exception as e:
            session.status = StreamingStatus.FAILED
            session.error_message = str(e)

            self.logger.error(f"Failed to stop session {session_id}: {e}")

            return None
    
    async def update_metrics(self, session_id: str, metrics_update: Dict[str, Any]) -> bool:
        """
        Met à jour les métriques d'une session
        
        Args:
            session_id: ID de la session
            metrics_update: Dictionnaire de mises à jour métriques
            
        Returns:
            True si mise à jour réussie
        """
        session = self._get_session(session_id)
        if not session or not session.metrics:
            return False
        
        try:
            metrics = session.metrics
            
            # Mettre à jour métriques
            for key, value in metrics_update.items():
                if hasattr(metrics, key):
                    setattr(metrics, key, value)
            
            # Calculer métriques dérivées
            if metrics.current_viewers > metrics.peak_viewers:
                metrics.peak_viewers = metrics.current_viewers
            
            if metrics.chat_messages > 0 and metrics.current_viewers > 0:
                metrics.engagement_rate = (
                    (metrics.chat_messages + metrics.likes + metrics.shares) 
                    / max(metrics.total_views, 1)
                )

            
            metrics.updated_at = datetime.utcnow()

            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics for session {session_id}: {e}")

            return False
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut complet d'une session
        
        Args:
            session_id: ID de la session
            
        Returns:
            Dictionnaire avec statut et métriques
        """
        session = self._get_session(session_id)
        if not session:
            return None

        
        duration = 0
        if session.started_at:
            end_time = session.ended_at or datetime.utcnow()


            duration = int((end_time - session.started_at).total_seconds() / 60)

        
        return {
            "session_id": session.session_id,
            "creator_id": session.creator_id,
            "creator_name": session.creator_name,
            "status": session.status.value,
            "title": session.config.title,
            "platforms": [p.value for p in session.config.platforms],
            "duration_minutes": duration,
            "metrics": {
                "current_viewers": session.metrics.current_viewers if session.metrics else 0,
                "peak_viewers": session.metrics.peak_viewers if session.metrics else 0,
                "total_views": session.metrics.total_views if session.metrics else 0,
                "engagement_rate": session.metrics.engagement_rate if session.metrics else 0.0,
                "donations_total": session.metrics.donations_total if session.metrics else 0.0,
            },
            "created_at": session.created_at.isoformat(),
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        }
    
    async def get_active_sessions(
        self,
        creator_id: Optional[str] = None,
        platform: Optional[PlatformType] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère toutes les sessions actives avec filtres optionnels
        
        Args:
            creator_id: Filtrer par créateur
            platform: Filtrer par plateforme
            
        Returns:
            Liste des sessions actives
        """
        sessions = []
        
        for session in self.active_sessions.values():
            # Filtrer par créateur
            if creator_id and session.creator_id != creator_id:
                continue
            
            # Filtrer par plateforme
            if platform and platform not in session.config.platforms:
                continue

            
            status = await self.get_session_status(session.session_id)

            if status:
                sessions.append(status)

        
        return sessions
    
    def _get_session(self, session_id: str) -> Optional[CreatorStreamingSession]:
        """
        Récupère une session par ID"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        if session_id in self.scheduled_sessions:
            return self.scheduled_sessions[session_id]
        return None
    
    def _generate_stream_key(self, creator_id: str) -> str:
        """
        Génère une clé de streaming unique"""
        timestamp = datetime.utcnow().timestamp()
        return f"{creator_id}_{int(timestamp)}_{uuid4().hex[:8]}"
    
    async def _initialize_platforms(self, session: CreatorStreamingSession) -> None:
        """Initialise le streaming sur toutes les plateformes"""
        for platform in session.config.platforms:
            try:
                # Simuler initialisation plateforme
                await asyncio.sleep(0.1)

                self.logger.info(
                    f"Initialized streaming on {platform.value} for session {session.session_id}"
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to initialize {platform.value} for session {session.session_id}: {e}"
                )
    
    async def _shutdown_platforms(self, session: CreatorStreamingSession) -> None:
        """Arrête le streaming sur toutes les plateformes"""
        for platform in session.config.platforms:
            try:
                # Simuler arrêt plateforme
                await asyncio.sleep(0.1)

                self.logger.info(
                    f"Shut down streaming on {platform.value} for session {session.session_id}"
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to shut down {platform.value} for session {session.session_id}: {e}"
                )
    
    async def _monitor_metrics(self, session_id: str) -> None:
        """Monitoring continu des métriques pendant le streaming"""
        while True:
            session = self._get_session(session_id)

            if not session or session.status not in [StreamingStatus.LIVE, StreamingStatus.PAUSED]:
                break
            
            try:
                # Simuler collecte métriques temps réel
                await asyncio.sleep(10)
                
                # Mise à jour métriques exemple
                if session.metrics:
                    duration = (datetime.utcnow() - session.started_at).total_seconds() / 60
                    session.metrics.watch_time_minutes = int(duration)

                
            except Exception as e:
                self.logger.error(f"Error monitoring metrics for session {session_id}: {e}")
    
    async def _generate_analytics(self, session: CreatorStreamingSession) -> StreamingAnalytics:
        """Génère les analytics finales d'une session"""
        duration = 0
        if session.started_at and session.ended_at:
            duration = int((session.ended_at - session.started_at).total_seconds() / 60)
        
        # Calculer métriques moyennes
        if session.metrics and duration > 0:
            session.metrics.average_viewers = int(
                session.metrics.total_views / max(duration, 1)
            )
        
        # Générer recommendations basées sur performance

        recommendations = []
        if session.metrics:
            if session.metrics.engagement_rate < 0.05:
                recommendations.append("Améliorer l'interaction avec le chat pour augmenter l'engagement")

            if session.metrics.quality_drops > 10:
                recommendations.append("Optimiser la qualité de connexion pour réduire les drops")

            if session.metrics.peak_viewers > session.metrics.average_viewers * 2:
                recommendations.append("Identifier les moments peak pour répliquer le succès")


        
        analytics = StreamingAnalytics(
            session_id=session.session_id,
            creator_id=session.creator_id,
            total_duration=duration,
            metrics=session.metrics or StreamingMetrics(session_id=session.session_id),
            recommendations=recommendations
        )

        
        return analytics


def create_creator_streaming_orchestrator(
    redis_client: Optional[Any] = None
) -> CreatorStreamingOrchestrator:
    """
    Factory function pour créer un orchestrateur streaming
    
    Args:
        redis_client: Client Redis optionnel
        
    Returns:
        Instance de CreatorStreamingOrchestrator
    """
    return CreatorStreamingOrchestrator(redis_client=redis_client)


__all__ = [
    "CreatorStreamingOrchestrator",
    "CreatorType",
    "ContentType",
    "StreamingStatus",
    "PlatformType",
    "StreamingConfig",
    "StreamingMetrics",
    "StreamingAnalytics",
    "CreatorStreamingSession",
    "create_creator_streaming_orchestrator",
]
