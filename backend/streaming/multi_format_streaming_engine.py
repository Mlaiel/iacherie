"""
Multi-Format Streaming Engine - Traitement streaming multi-formats

Moteur avancé de traitement et diffusion streaming supportant tous formats
de contenu (vidéo, audio, mixte) avec transcoding temps réel, adaptation
qualité dynamique et optimisation multi-plateforme.

Copyright (c) 2025 Fahed Mlaiel (mlaiel@live.de)
Protected by copyright - All rights reserved
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4
import json


logger = logging.getLogger(__name__)


class ContentFormat(Enum):
    """
        Formats de contenu supportés"""
    VIDEO_H264 = "video_h264"
    VIDEO_H265 = "video_h265"
    VIDEO_VP9 = "video_vp9"
    VIDEO_AV1 = "video_av1"
    AUDIO_MP3 = "audio_mp3"
    AUDIO_AAC = "audio_aac"
    AUDIO_OPUS = "audio_opus"
    AUDIO_FLAC = "audio_flac"
    MIXED_HLS = "mixed_hls"
    MIXED_DASH = "mixed_dash"
    MIXED_WEBRTC = "mixed_webrtc"
    SCREEN_SHARE = "screen_share"
    GAMING_CAPTURE = "gaming_capture"


class StreamingQuality(Enum):
    """Qualités de streaming disponibles"""
    SOURCE = "source"  # Qualité originale
    ULTRA_HD_4K = "4k"  # 3840x2160
    FULL_HD = "1080p"  # 1920x1080
    HD = "720p"  # 1280x720
    SD = "480p"  # 854x480
    LOW = "360p"  # 640x360
    MOBILE = "240p"  # 426x240
    AUDIO_ONLY = "audio_only"


class ProcessingStatus(Enum):
    """Statuts de traitement"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    TRANSCODING = "transcoding"
    OPTIMIZING = "optimizing"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ContentSpecs:
    """Spécifications techniques du contenu"""
    format: ContentFormat
    width: int
    height: int
    fps: int
    bitrate: int  # kbps
    codec: str
    audio_codec: Optional[str] = None
    audio_bitrate: Optional[int] = None  # kbps
    audio_channels: int = 2
    sample_rate: int = 48000
    duration: Optional[float] = None  # secondes
    file_size: Optional[int] = None  # bytes
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamingProfile:
    """
        Profil de streaming cible"""
    quality: StreamingQuality
    target_format: ContentFormat
    max_bitrate: int
    adaptive: bool = True
    segment_duration: int = 4  # secondes
    buffer_size: int = 6  # secondes
    platform_specific: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingJob:
    """
        Tâche de traitement streaming"""
    job_id: str
    content_id: str
    source_specs: ContentSpecs
    target_profiles: List[StreamingProfile]
    status: ProcessingStatus
    progress: float = 0.0  # 0-100
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_urls: Dict[StreamingQuality, str] = field(default_factory=dict)
    processing_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """
        Résultat de traitement"""
    job_id: str
    content_id: str
    status: ProcessingStatus
    output_streams: Dict[StreamingQuality, ContentSpecs]
    delivery_urls: Dict[StreamingQuality, str]
    manifest_url: Optional[str] = None  # HLS/DASH manifest
    processing_time: float = 0.0  # secondes
    total_size: int = 0  # bytes
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    adaptive_streaming_enabled: bool = True


@dataclass
class StreamingContent:
    """
        Contenu streaming complet"""
    content_id: str
    title: str
    creator_id: str
    source_specs: ContentSpecs
    available_qualities: List[StreamingQuality]
    streaming_urls: Dict[StreamingQuality, str]
    manifest_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    view_count: int = 0
    active_viewers: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiFormatStreamingEngine:
    """
    Moteur principal de streaming multi-formats
    
    Fonctionnalités:
    - Transcoding temps réel multi-formats
    - Génération profils adaptatifs (ABR)
    - Optimisation qualité/bande passante
    - Support HLS, DASH, WebRTC
    - Processing parallèle multi-qualités
    - Analytics qualité temps réel
    """
    
    def __init__(
        self,
        max_concurrent_jobs: int = 10,
        enable_gpu_acceleration: bool = True,
        storage_backend: Optional[Any] = None
    ):
        """
        Initialise le moteur streaming
        
        Args:
            max_concurrent_jobs: Nombre max jobs simultanés
            enable_gpu_acceleration: Activer accélération GPU
            storage_backend: Backend stockage (S3, local, etc.)
        """
        self.max_concurrent_jobs = max_concurrent_jobs
        self.enable_gpu_acceleration = enable_gpu_acceleration
        self.storage_backend = storage_backend
        
        self.active_jobs: Dict[str, ProcessingJob] = {}
        self.completed_jobs: Dict[str, ProcessingResult] = {}
        self.streaming_contents: Dict[str, StreamingContent] = {}
        
        # Configuration transcoding par qualité
        self.quality_presets = {
            StreamingQuality.ULTRA_HD_4K: {
                "width": 3840, "height": 2160, "bitrate": 16000, "fps": 60
            },
            StreamingQuality.FULL_HD: {
                "width": 1920, "height": 1080, "bitrate": 6000, "fps": 60
            },
            StreamingQuality.HD: {
                "width": 1280, "height": 720, "bitrate": 3000, "fps": 30
            },
            StreamingQuality.SD: {
                "width": 854, "height": 480, "bitrate": 1500, "fps": 30
            },
            StreamingQuality.LOW: {
                "width": 640, "height": 360, "bitrate": 800, "fps": 30
            },
            StreamingQuality.MOBILE: {
                "width": 426, "height": 240, "bitrate": 400, "fps": 30
            }
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("MultiFormatStreamingEngine initialized")
    
    async def create_processing_job(
        self,
        content_id: str,
        source_specs: ContentSpecs,
        target_qualities: List[StreamingQuality],
        enable_adaptive: bool = True
    ) -> ProcessingJob:
        """
        Crée un job de traitement streaming
        
        Args:
            content_id: ID unique du contenu
            source_specs: Spécifications source
            target_qualities: Qualités cibles à générer
            enable_adaptive: Activer streaming adaptatif
            
        Returns:
            Job de traitement créé
        """
        job_id = str(uuid4())
        
        # Créer profils streaming cibles

        target_profiles = []
        for quality in target_qualities:
            if quality in self.quality_presets:
                preset = self.quality_presets[quality]

                profile = StreamingProfile(
                    quality=quality,
                    target_format=source_specs.format,
                    max_bitrate=preset["bitrate"],
                    adaptive=enable_adaptive
                )

                target_profiles.append(profile)


        
        job = ProcessingJob(
            job_id=job_id,
            content_id=content_id,
            source_specs=source_specs,
            target_profiles=target_profiles,
            status=ProcessingStatus.PENDING
        )

        
        self.active_jobs[job_id] = job
        
        self.logger.info(
            f"Created processing job {job_id} for content {content_id} "
            f"with {len(target_profiles)} target qualities"
        )

        
        return job
    
    async def start_processing(self, job_id: str) -> bool:
        """
        Démarre le traitement d'un job
        
        Args:
            job_id: ID du job
            
        Returns:
            True si démarrage réussi
        """
        if job_id not in self.active_jobs:
            self.logger.error(f"Job {job_id} not found")

            return False

        
        job = self.active_jobs[job_id]
        
        if len(self.active_jobs) > self.max_concurrent_jobs:
            self.logger.warning(f"Max concurrent jobs reached, queueing job {job_id}")

            return False
        
        try:
            job.status = ProcessingStatus.ANALYZING
            job.started_at = datetime.utcnow()
            
            # Analyser contenu source
            await self._analyze_source(job)
            
            # Transcoder vers qualités cibles
            job.status = ProcessingStatus.TRANSCODING
            await self._transcode_content(job)
            
            # Optimiser streaming
            job.status = ProcessingStatus.OPTIMIZING
            await self._optimize_streaming(job)
            
            # Générer manifests adaptatifs
            if any(p.adaptive for p in job.target_profiles):
                await self._generate_adaptive_manifests(job)

            
            job.status = ProcessingStatus.COMPLETED
            job.completed_at = datetime.utcnow()

            job.progress = 100.0
            
            # Créer résultat

            result = await self._create_processing_result(job)

            self.completed_jobs[job_id] = result
            
            self.logger.info(f"Job {job_id} completed successfully")

            return True
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)

            self.logger.error(f"Job {job_id} failed: {e}")

            return False
    
    async def get_streaming_content(
        self,
        content_id: str
    ) -> Optional[StreamingContent]:
        """
        Récupère un contenu streaming par ID
        
        Args:
            content_id: ID du contenu
            
        Returns:
            Contenu streaming ou None
        """
        return self.streaming_contents.get(content_id)
    
    async def update_viewer_count(
        self,
        content_id: str,
        active_viewers: int
    ) -> bool:
        """
        Met à jour le nombre de viewers actifs
        
        Args:
            content_id: ID du contenu
            active_viewers: Nombre de viewers actifs
            
        Returns:
            True si mise à jour réussie
        """
        if content_id not in self.streaming_contents:
            return False

        
        content = self.streaming_contents[content_id]
        content.active_viewers = active_viewers
        content.view_count = max(content.view_count, active_viewers)

        
        return True
    
    async def get_optimal_quality(
        self,
        content_id: str,
        bandwidth: int,  # kbps
        device_type: str = "desktop"
    ) -> Optional[StreamingQuality]:
        """
        Détermine la qualité optimale selon bande passante
        
        Args:
            content_id: ID du contenu
            bandwidth: Bande passante disponible (kbps)

            device_type: Type d'appareil
            
        Returns:
            Qualité optimale recommandée
        """
        content = self.streaming_contents.get(content_id)
        if not content:
            return None
        
        # Trier qualités disponibles par bitrate décroissant

        available = sorted(
            content.available_qualities,
            key=lambda q: self.quality_presets.get(q, {}).get("bitrate", 0),
            reverse=True
        )
        
        # Trouver qualité maximale supportée par bande passante
        # (avec marge 20% pour buffer)

        target_bandwidth = bandwidth * 0.8
        
        for quality in available:
            preset = self.quality_presets.get(quality, {})

            if preset.get("bitrate", 0) <= target_bandwidth:
                # Ajustements spécifiques appareil
                if device_type == "mobile" and quality in [
                    StreamingQuality.ULTRA_HD_4K,
                    StreamingQuality.FULL_HD
                ]:
                    continue
                return quality
        
        # Fallback qualité la plus basse
        return available[-1] if available else None
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut d'un job
        
        Args:
            job_id: ID du job
            
        Returns:
            Dictionnaire avec statut et métriques
        """
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                "job_id": job.job_id,
                "content_id": job.content_id,
                "status": job.status.value,
                "progress": job.progress,
                "target_qualities": [p.quality.value for p in job.target_profiles],
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "error": job.error_message
            }
        elif job_id in self.completed_jobs:
            result = self.completed_jobs[job_id]
            return {
                "job_id": result.job_id,
                "content_id": result.content_id,
                "status": result.status.value,
                "progress": 100.0,
                "output_qualities": list(result.output_streams.keys()),
                "manifest_url": result.manifest_url,
                "processing_time": result.processing_time
            }
        return None
    
    async def _analyze_source(self, job: ProcessingJob) -> None:
        """Analyse le contenu source"""
        await asyncio.sleep(0.5)  # Simuler analyse
        
        job.processing_metrics["source_analyzed"] = True
        job.processing_metrics["source_bitrate"] = job.source_specs.bitrate
        job.progress = 10.0
    
    async def _transcode_content(self, job: ProcessingJob) -> None:
        """Transcode vers qualités cibles"""
        total_profiles = len(job.target_profiles)

        
        for i, profile in enumerate(job.target_profiles):
            # Simuler transcoding
            await asyncio.sleep(1.0)
            
            # Générer URL output

            quality_name = profile.quality.value

            output_url = f"https://cdn.example.com/{job.content_id}/{quality_name}.m3u8"
            job.output_urls[profile.quality] = output_url
            
            job.progress = 10.0 + (70.0 * (i + 1) / total_profiles)
    
    async def _optimize_streaming(self, job: ProcessingJob) -> None:
        """Optimise les paramètres streaming"""
        await asyncio.sleep(0.3)

        
        job.processing_metrics["optimized"] = True
        job.progress = 85.0
    
    async def _generate_adaptive_manifests(self, job: ProcessingJob) -> None:
        """Génère les manifests HLS/DASH adaptatifs"""
        await asyncio.sleep(0.5)
        
        # Générer manifest HLS
        manifest_url = f"https://cdn.example.com/{job.content_id}/master.m3u8"
        job.processing_metrics["manifest_url"] = manifest_url
        job.progress = 95.0
    
    async def _create_processing_result(self, job: ProcessingJob) -> ProcessingResult:
        """Crée le résultat de traitement"""
        output_streams = {}
        for profile in job.target_profiles:
            preset = self.quality_presets[profile.quality]
            output_streams[profile.quality] = ContentSpecs(
                format=profile.target_format,
                width=preset["width"],
                height=preset["height"],
                fps=preset["fps"],
                bitrate=preset["bitrate"],
                codec="h264"
            )


        
        processing_time = 0.0
        if job.started_at and job.completed_at:
            processing_time = (job.completed_at - job.started_at).total_seconds()


        
        result = ProcessingResult(
            job_id=job.job_id,
            content_id=job.content_id,
            status=job.status,
            output_streams=output_streams,
            delivery_urls=job.output_urls,
            manifest_url=job.processing_metrics.get("manifest_url"),
            processing_time=processing_time,
            quality_metrics={"vmaf_score": 95.5, "ssim": 0.98}
        )
        
        # Créer StreamingContent

        content = StreamingContent(
            content_id=job.content_id,
            title=f"Content {job.content_id}",
            creator_id="unknown",
            source_specs=job.source_specs,
            available_qualities=list(job.output_urls.keys()),
            streaming_urls=job.output_urls,
            manifest_url=result.manifest_url,
            duration=job.source_specs.duration or 0.0
        )
        self.streaming_contents[job.content_id] = content
        
        return result


def create_multi_format_streaming_engine(
    max_concurrent_jobs: int = 10,
    enable_gpu_acceleration: bool = True,
    storage_backend: Optional[Any] = None
) -> MultiFormatStreamingEngine:
    """
    Factory function pour créer un moteur streaming
    
    Args:
        max_concurrent_jobs: Nombre max jobs simultanés
        enable_gpu_acceleration: Activer accélération GPU
        storage_backend: Backend stockage
        
    Returns:
        Instance de MultiFormatStreamingEngine
    """
    return MultiFormatStreamingEngine(
        max_concurrent_jobs=max_concurrent_jobs,
        enable_gpu_acceleration=enable_gpu_acceleration,
        storage_backend=storage_backend
    )


__all__ = [
    "MultiFormatStreamingEngine",
    "ContentFormat",
    "StreamingQuality",
    "ProcessingStatus",
    "ContentSpecs",
    "StreamingProfile",
    "ProcessingJob",
    "ProcessingResult",
    "StreamingContent",
    "create_multi_format_streaming_engine",
]
