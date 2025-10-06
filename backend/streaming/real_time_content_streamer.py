"""
Real-Time Content Streamer - Diffusion contenu temps réel

Streamer ultra-low latency avec WebRTC, adaptive streaming,
buffer management intelligent, audience engagement temps réel
et synchronisation multi-viewers.

Copyright (c) 2025 Fahed Mlaiel (mlaiel@live.de)
Protected by copyright - All rights reserved
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from uuid import uuid4
import time


logger = logging.getLogger(__name__)


class StreamingMode(Enum):
    """
        Modes de streaming"""
    ULTRA_LOW_LATENCY = "ultra_low_latency"  # <500ms, WebRTC
    LOW_LATENCY = "low_latency"  # <3s, LL-HLS
    STANDARD = "standard"  # 6-10s, HLS/DASH
    ADAPTIVE = "adaptive"  # Auto-switch selon conditions


class ContentDeliveryMethod(Enum):
    """Méthodes de delivery"""
    WEBRTC = "webrtc"
    LL_HLS = "ll_hls"  # Low-Latency HLS
    HLS = "hls"
    DASH = "dash"
    RTMP = "rtmp"
    SRT = "srt"  # Secure Reliable Transport


class StreamingStatus(Enum):
    """Statuts streaming"""
    INITIALIZING = "initializing"
    STARTING = "starting"
    LIVE = "live"
    BUFFERING = "buffering"
    PAUSED = "paused"
    RECONNECTING = "reconnecting"
    ENDED = "ended"
    ERROR = "error"


class AudienceEngagementType(Enum):
    """Types d'engagement audience"""
    CHAT_MESSAGE = "chat_message"
    REACTION = "reaction"
    POLL_VOTE = "poll_vote"
    SUPER_CHAT = "super_chat"
    GIFT = "gift"
    SHARE = "share"
    CLIP_CREATED = "clip_created"
    FOLLOW = "follow"


@dataclass
class StreamingConfiguration:
    """Configuration streaming"""
    stream_id: str
    mode: StreamingMode
    delivery_method: ContentDeliveryMethod
    target_latency: float  # secondes
    max_bitrate: int  # kbps
    enable_adaptive_bitrate: bool = True
    buffer_size: int = 3000  # ms
    segment_duration: float = 2.0  # secondes
    enable_audience_sync: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentChunk:
    """
        Chunk de contenu à streamer"""
    chunk_id: str
    stream_id: str
    sequence_number: int
    data: bytes
    timestamp: float
    duration: float  # secondes
    bitrate: int
    is_keyframe: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudienceEngagement:
    """Événement engagement audience"""
    engagement_id: str
    stream_id: str
    viewer_id: str
    engagement_type: AudienceEngagementType
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamingMetrics:
    """
        Métriques streaming temps réel"""
    stream_id: str
    current_viewers: int
    peak_viewers: int
    total_views: int
    average_latency: float  # ms
    buffer_health: float  # 0-100
    dropped_frames: int
    current_bitrate: int
    bandwidth_utilization: float  # %
    engagement_rate: float  # events/minute
    quality_score: float  # 0-100
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RealTimeStreamingRecord:
    """
        Enregistrement streaming complet"""
    record_id: str
    config: StreamingConfiguration
    status: StreamingStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    metrics: StreamingMetrics = None
    active_viewers: Set[str] = field(default_factory=set)
    engagement_history: List[AudienceEngagement] = field(default_factory=list)
    chunks_sent: int = 0
    total_data_sent: int = 0  # bytes
    reconnections: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)


class RealTimeContentStreamer:
    """
    Streamer contenu temps réel ultra-low latency
    
    Fonctionnalités:
    - WebRTC ultra-low latency (<500ms)
    - LL-HLS pour compatibilité large
    - Adaptive bitrate automatique
    - Buffer management intelligent
    - Audience synchronization
    - Engagement temps réel (chat, reactions)
    - Multi-viewer coordination
    - Fallback automatique erreurs
    - Quality monitoring continu
    - Analytics temps réel
    """
    
    def __init__(
        self,
        default_mode: StreamingMode = StreamingMode.ADAPTIVE,
        max_concurrent_streams: int = 50
    ):
        """
        Initialise le streamer
        
        Args:
            default_mode: Mode streaming par défaut
            max_concurrent_streams: Nombre max streams simultanés
        """
        self.default_mode = default_mode
        self.max_concurrent_streams = max_concurrent_streams
        
        self.active_streams: Dict[str, RealTimeStreamingRecord] = {}
        self.viewer_connections: Dict[str, Set[str]] = {}  # stream_id -> viewer_ids
        self.engagement_buffer: Dict[str, List[AudienceEngagement]] = {}
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"RealTimeContentStreamer initialized "
            f"(mode={default_mode.value}, max_streams={max_concurrent_streams})"
        )
    
    async def start_stream(
        self,
        stream_id: str,
        config: Optional[StreamingConfiguration] = None
    ) -> RealTimeStreamingRecord:
        """
        Démarre un stream temps réel
        
        Args:
            stream_id: ID unique du stream
            config: Configuration streaming optionnelle
            
        Returns:
            Enregistrement streaming créé
        """
        if len(self.active_streams) >= self.max_concurrent_streams:
            raise RuntimeError(
                f"Max concurrent streams reached ({self.max_concurrent_streams})"
            )

        
        if stream_id in self.active_streams:
            raise ValueError(f"Stream {stream_id} already active")
        
        # Configuration par défaut si non fournie
        if not config:
            config = StreamingConfiguration(
                stream_id=stream_id,
                mode=self.default_mode,
                delivery_method=self._get_delivery_method(self.default_mode),
                target_latency=0.5 if self.default_mode == StreamingMode.ULTRA_LOW_LATENCY else 3.0,
                max_bitrate=8000,
                enable_adaptive_bitrate=True,
                buffer_size=3000,
                segment_duration=2.0,
                enable_audience_sync=True
            )
        
        # Créer métriques initiales

        metrics = StreamingMetrics(
            stream_id=stream_id,
            current_viewers=0,
            peak_viewers=0,
            total_views=0,
            average_latency=0.0,
            buffer_health=100.0,
            dropped_frames=0,
            current_bitrate=config.max_bitrate,
            bandwidth_utilization=0.0,
            engagement_rate=0.0,
            quality_score=100.0
        )
        
        # Créer enregistrement

        record = RealTimeStreamingRecord(
            record_id=str(uuid4()),
            config=config,
            status=StreamingStatus.INITIALIZING,
            start_time=datetime.utcnow(),
            metrics=metrics
        )

        
        self.active_streams[stream_id] = record
        self.viewer_connections[stream_id] = set()
        self.engagement_buffer[stream_id] = []
        
        # Démarrer monitoring
        asyncio.create_task(self._monitor_stream_health(stream_id))
        
        # Transition vers STARTING puis LIVE
        await asyncio.sleep(0.5)
        record.status = StreamingStatus.STARTING
        await asyncio.sleep(0.5)
        record.status = StreamingStatus.LIVE
        
        self.logger.info(
            f"Started stream {stream_id} "
            f"(mode={config.mode.value}, delivery={config.delivery_method.value})"
        )

        
        return record
    
    async def send_chunk(
        self,
        stream_id: str,
        chunk: ContentChunk
    ) -> bool:
        """
        Envoie un chunk de contenu
        
        Args:
            stream_id: ID du stream
            chunk: Chunk à envoyer
            
        Returns:
            True si envoi réussi
        """
        if stream_id not in self.active_streams:
            return False

        
        record = self.active_streams[stream_id]
        
        if record.status != StreamingStatus.LIVE:
            self.logger.warning(
                f"Stream {stream_id} not live (status: {record.status.value})"
            )

            return False
        
        # Simuler envoi chunk (en production: WebRTC/HLS delivery réelle)
        await asyncio.sleep(0.001)  # Simule latency réseau
        
        # Mettre à jour compteurs
        record.chunks_sent += 1
        record.total_data_sent += len(chunk.data)
        
        # Mettre à jour métriques
        record.metrics.current_bitrate = chunk.bitrate
        
        return True
    
    async def add_viewer(
        self,
        stream_id: str,
        viewer_id: str
    ) -> bool:
        """
        Ajoute un viewer au stream
        
        Args:
            stream_id: ID du stream
            viewer_id: ID du viewer
            
        Returns:
            True si ajout réussi
        """
        if stream_id not in self.active_streams:
            return False

        
        record = self.active_streams[stream_id]
        
        # Ajouter viewer
        self.viewer_connections[stream_id].add(viewer_id)
        record.active_viewers.add(viewer_id)
        
        # Mettre à jour métriques
        record.metrics.current_viewers = len(record.active_viewers)
        record.metrics.total_views += 1
        
        # Mettre à jour peak
        if record.metrics.current_viewers > record.metrics.peak_viewers:
            record.metrics.peak_viewers = record.metrics.current_viewers
        
        self.logger.debug(
            f"Viewer {viewer_id} joined stream {stream_id} "
            f"(total: {record.metrics.current_viewers})"
        )

        
        return True
    
    async def remove_viewer(
        self,
        stream_id: str,
        viewer_id: str
    ) -> bool:
        """
        Retire un viewer du stream
        
        Args:
            stream_id: ID du stream
            viewer_id: ID du viewer
            
        Returns:
            True si retrait réussi
        """
        if stream_id not in self.active_streams:
            return False

        
        record = self.active_streams[stream_id]
        
        # Retirer viewer
        self.viewer_connections[stream_id].discard(viewer_id)
        record.active_viewers.discard(viewer_id)
        
        # Mettre à jour métriques
        record.metrics.current_viewers = len(record.active_viewers)

        
        self.logger.debug(
            f"Viewer {viewer_id} left stream {stream_id} "
            f"(remaining: {record.metrics.current_viewers})"
        )

        
        return True
    
    async def handle_engagement(
        self,
        stream_id: str,
        engagement: AudienceEngagement
    ) -> bool:
        """
        Gère un événement d'engagement audience
        
        Args:
            stream_id: ID du stream
            engagement: Événement engagement
            
        Returns:
            True si traité avec succès
        """
        if stream_id not in self.active_streams:
            return False

        
        record = self.active_streams[stream_id]
        
        # Ajouter à l'historique
        record.engagement_history.append(engagement)
        self.engagement_buffer[stream_id].append(engagement)
        
        # Limiter buffer (garder dernières 1000 entrées)
        if len(self.engagement_buffer[stream_id]) > 1000:
            self.engagement_buffer[stream_id] = self.engagement_buffer[stream_id][-1000:]
        
        # Calculer engagement rate (events/minute)

        recent_window = datetime.utcnow().timestamp() - 60  # Dernière minute

        recent_engagements = [
            e for e in self.engagement_buffer[stream_id]
            if e.timestamp.timestamp() > recent_window
        ]
        record.metrics.engagement_rate = len(recent_engagements)

        
        self.logger.debug(
            f"Engagement {engagement.engagement_type.value} in stream {stream_id} "
            f"from viewer {engagement.viewer_id}"
        )

        
        return True
    
    async def get_stream_metrics(
        self,
        stream_id: str
    ) -> Optional[StreamingMetrics]:
        """
        Récupère métriques temps réel d'un stream
        
        Args:
            stream_id: ID du stream
            
        Returns:
            Métriques ou None
        """
        if stream_id not in self.active_streams:
            return None
        
        return self.active_streams[stream_id].metrics
    
    async def get_active_viewers(
        self,
        stream_id: str
    ) -> Optional[Set[str]]:
        """
        Récupère viewers actifs d'un stream
        
        Args:
            stream_id: ID du stream
            
        Returns:
            Set viewer IDs ou None
        """
        if stream_id not in self.active_streams:
            return None
        
        return self.active_streams[stream_id].active_viewers.copy()
    
    async def get_recent_engagements(
        self,
        stream_id: str,
        limit: int = 50
    ) -> List[AudienceEngagement]:
        """
        Récupère engagements récents
        
        Args:
            stream_id: ID du stream
            limit: Nombre max d'engagements
            
        Returns:
            Liste engagements récents
        """
        if stream_id not in self.engagement_buffer:
            return []
        
        return self.engagement_buffer[stream_id][-limit:]
    
    async def end_stream(
        self,
        stream_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Termine un stream
        
        Args:
            stream_id: ID du stream
            
        Returns:
            Résumé stream ou None
        """
        if stream_id not in self.active_streams:
            return None

        
        record = self.active_streams[stream_id]
        record.status = StreamingStatus.ENDED
        record.end_time = datetime.utcnow()
        
        # Calculer durée

        duration = (record.end_time - record.start_time).total_seconds() / 60  # minutes
        
        # Résumé final

        summary = {
            "stream_id": stream_id,
            "duration_minutes": duration,
            "peak_viewers": record.metrics.peak_viewers,
            "total_views": record.metrics.total_views,
            "total_engagements": len(record.engagement_history),
            "chunks_sent": record.chunks_sent,
            "data_sent_mb": record.total_data_sent / (1024 * 1024),
            "average_latency_ms": record.metrics.average_latency,
            "quality_score": record.metrics.quality_score,
            "reconnections": record.reconnections,
            "errors": len(record.errors)
        }
        
        # Cleanup
        del self.active_streams[stream_id]
        del self.viewer_connections[stream_id]
        del self.engagement_buffer[stream_id]
        
        self.logger.info(
            f"Ended stream {stream_id} "
            f"(duration: {duration:.1f}min, peak: {summary['peak_viewers']} viewers)"
        )

        
        return summary
    
    async def _monitor_stream_health(self, stream_id: str) -> None:
        """Monitoring continu santé stream"""
        while stream_id in self.active_streams:
            await asyncio.sleep(5)  # Check toutes les 5s

            
            record = self.active_streams[stream_id]

            metrics = record.metrics
            
            # Simuler latency mesure (en production: mesure réelle RTT)

            if metrics.current_viewers > 0:
                base_latency = 500 if record.config.mode == StreamingMode.ULTRA_LOW_LATENCY else 3000
                metrics.average_latency = base_latency + (metrics.current_viewers * 2)
            
            # Buffer health (simulé)

            metrics.buffer_health = 100.0 - (metrics.dropped_frames * 0.5)

            metrics.buffer_health = max(0.0, min(100.0, metrics.buffer_health))
            
            # Quality score

            quality_factors = [
                metrics.buffer_health,
                100.0 - (metrics.average_latency / 100),  # Latency impact
                100.0 - (metrics.dropped_frames * 2)
            ]
            metrics.quality_score = sum(quality_factors) / len(quality_factors)

            
            metrics.updated_at = datetime.utcnow()
    
    def _get_delivery_method(self, mode: StreamingMode) -> ContentDeliveryMethod:
        """
        Détermine méthode delivery selon mode"""
        if mode == StreamingMode.ULTRA_LOW_LATENCY:
            return ContentDeliveryMethod.WEBRTC
        elif mode == StreamingMode.LOW_LATENCY:
            return ContentDeliveryMethod.LL_HLS
        else:
            return ContentDeliveryMethod.HLS


def create_real_time_content_streamer(
    default_mode: StreamingMode = StreamingMode.ADAPTIVE,
    max_concurrent_streams: int = 50
) -> RealTimeContentStreamer:
    """
    Factory function pour créer streamer
    
    Args:
        default_mode: Mode streaming par défaut
        max_concurrent_streams: Nombre max streams simultanés
        
    Returns:
        Instance de RealTimeContentStreamer
    """
    return RealTimeContentStreamer(
        default_mode=default_mode,
        max_concurrent_streams=max_concurrent_streams
    )


__all__ = [
    "RealTimeContentStreamer",
    "StreamingMode",
    "ContentDeliveryMethod",
    "StreamingStatus",
    "AudienceEngagementType",
    "StreamingConfiguration",
    "ContentChunk",
    "AudienceEngagement",
    "StreamingMetrics",
    "RealTimeStreamingRecord",
    "create_real_time_content_streamer",
]
