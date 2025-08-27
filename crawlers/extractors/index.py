"""
IA Influencer Agent - Industrial Extractors Index System
=======================================================

Ultra-advanced professional interface for all industrial AI extractors.
Implements enterprise-grade unified access to all AI extraction capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de

Unified Interface for Industrial AI Extractors
==============================================

This module provides a centralized interface to access all industrial-grade
artificial intelligence extractors developed by the expert team.

Core Features:
- Unified multi-layer extractor management
- Intelligent orchestration of extraction processes
- High-level interface for system integration
- Automatic dependency and configuration management
- Performance monitoring and analytics
- Real-time extraction capabilities
- Enterprise-grade security and protection
"""

import asyncio
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod

# Imports des modules d'extraction
from .base import BaseExtractor, ExtractionRequest, ExtractionResult
from .content_extractors import (
    AudioContentExtractor, VideoContentExtractor, 
    ImageContentExtractor, TextContentExtractor
)
from .platform_extractors import (
    YouTubeExtractor, InstagramExtractor, 
    TikTokExtractor, SpotifyExtractor
)
from .fingerprint_extractors import (
    AudioFingerprintExtractor, VideoFingerprintExtractor,
    ImageFingerprintExtractor, TextFingerprintExtractor
)
from .revenue_extractors import (
    BaseRevenueExtractor, YouTubeRevenueExtractor, 
    SpotifyRevenueExtractor
)
from .collaboration_extractors import (
    BaseCollaborationExtractor, YouTubeCollaborationExtractor
)
from .surveillance_extractors import (
    BaseSurveillanceExtractor, YouTubeSurveillanceExtractor
)

# Configuration et énumérations
class ExtractionMode(Enum):
    """Modes d'extraction disponibles"""
    SEQUENTIAL = "sequential"      # Extraction séquentielle
    PARALLEL = "parallel"          # Extraction parallèle
    ADAPTIVE = "adaptive"          # Mode adaptatif intelligent
    REAL_TIME = "real_time"        # Extraction temps réel
    BATCH = "batch"                # Traitement par lots


class PriorityLevel(Enum):
    """Niveaux de priorité pour les extractions"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class ExtractionJob:
    """Tâche d'extraction complète"""
    job_id: str
    extraction_type: str
    priority: PriorityLevel
    request: ExtractionRequest
    
    # Configuration
    mode: ExtractionMode = ExtractionMode.ADAPTIVE
    timeout: timedelta = field(default_factory=lambda: timedelta(minutes=10))
    retry_count: int = 3
    
    # État
    status: str = "pending"  # pending, running, completed, failed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Résultats
    result: Optional[ExtractionResult] = None
    error: Optional[str] = None
    
    # Métriques
    processing_time: Optional[float] = None
    resources_used: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractorCapability:
    """Capacité d'un extracteur"""
    name: str
    description: str
    supported_formats: List[str] = field(default_factory=list)
    ai_features: List[str] = field(default_factory=list)
    performance_tier: str = "standard"  # basic, standard, premium, enterprise
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


class ExtractionOrchestrator:
    """Orchestrateur principal pour la gestion des extractions IA"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Registres des extracteurs
        self._content_extractors = {}
        self._platform_extractors = {}
        self._fingerprint_extractors = {}
        self._revenue_extractors = {}
        self._collaboration_extractors = {}
        self._surveillance_extractors = {}
        
        # Gestion des tâches
        self._active_jobs = {}
        self._job_queue = asyncio.Queue()
        self._worker_pool = []
        self._max_workers = 10
        
        # Configuration
        self._default_mode = ExtractionMode.ADAPTIVE
        self._monitoring_enabled = True
        self._metrics_collector = None
        
        # État système
        self._is_running = False
        self._shutdown_event = asyncio.Event()
        
        # Initialisation automatique
        self._initialize_extractors()
        self._start_worker_pool()
    
    def _initialize_extractors(self):
        """Initialise tous les extracteurs disponibles"""
        try:
            # Extracteurs de contenu
            self._content_extractors = {
                'audio': AudioContentExtractor(),
                'video': VideoContentExtractor(),
                'image': ImageContentExtractor(),
                'text': TextContentExtractor()
            }
            
            # Extracteurs de plateformes (nécessitent configuration API)
            self._platform_extractors = {
                'youtube': None,  # Sera initialisé avec les clés API
                'instagram': None,
                'tiktok': None,
                'spotify': None
            }
            
            # Extracteurs d'empreintes
            self._fingerprint_extractors = {
                'audio': AudioFingerprintExtractor(),
                'video': VideoFingerprintExtractor(),
                'image': ImageFingerprintExtractor(),
                'text': TextFingerprintExtractor()
            }
            
            # Extracteurs de revenus
            self._revenue_extractors = {
                'youtube': None,  # Nécessite clés API
                'spotify': None
            }
            
            # Extracteurs de collaborations
            self._collaboration_extractors = {
                'youtube': None  # Nécessite clés API
            }
            
            # Extracteurs de surveillance
            self._surveillance_extractors = {
                'youtube': None  # Nécessite clés API
            }
            
            self.logger.info("Extractors initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize extractors: {e}")
    
    def _start_worker_pool(self):
        """Démarre le pool de workers pour le traitement asynchrone"""
        if not self._is_running:
            self._is_running = True
            for i in range(self._max_workers):
                worker = asyncio.create_task(self._worker_loop(f"worker-{i}"))
                self._worker_pool.append(worker)
            
            self.logger.info(f"Started worker pool with {self._max_workers} workers")
    
    async def _worker_loop(self, worker_id: str):
        """Boucle principale d'un worker"""
        while self._is_running and not self._shutdown_event.is_set():
            try:
                # Récupération d'une tâche
                job = await asyncio.wait_for(
                    self._job_queue.get(), 
                    timeout=1.0
                )
                
                # Traitement de la tâche
                await self._process_job(job, worker_id)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def _process_job(self, job: ExtractionJob, worker_id: str):
        """Traite une tâche d'extraction"""
        job.started_at = datetime.now()
        job.status = "running"
        
        try:
            self.logger.info(f"Worker {worker_id} processing job {job.job_id}")
            
            # Sélection de l'extracteur approprié
            extractor = self._select_extractor(job)
            
            if not extractor:
                raise ValueError(f"No suitable extractor found for {job.extraction_type}")
            
            # Vérification des capacités
            if not await extractor.can_handle(job.request):
                raise ValueError(f"Extractor cannot handle request")
            
            # Extraction avec timeout
            start_time = asyncio.get_event_loop().time()
            
            result = await asyncio.wait_for(
                extractor.extract(job.request),
                timeout=job.timeout.total_seconds()
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Mise à jour du job
            job.result = result
            job.status = "completed"
            job.completed_at = datetime.now()
            job.processing_time = processing_time
            
            # Métriques
            if self._monitoring_enabled:
                await self._collect_metrics(job, worker_id)
            
            self.logger.info(f"Job {job.job_id} completed in {processing_time:.2f}s")
            
        except asyncio.TimeoutError:
            job.status = "failed"
            job.error = "Extraction timeout"
            job.completed_at = datetime.now()
            self.logger.error(f"Job {job.job_id} timed out")
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.now()
            self.logger.error(f"Job {job.job_id} failed: {e}")
        
        finally:
            # Nettoyage
            if job.job_id in self._active_jobs:
                del self._active_jobs[job.job_id]
    
    def _select_extractor(self, job: ExtractionJob) -> Optional[BaseExtractor]:
        """Sélectionne l'extracteur approprié pour une tâche"""
        extraction_type = job.extraction_type.lower()
        
        # Extracteurs de contenu
        if extraction_type in ['audio', 'video', 'image', 'text']:
            return self._content_extractors.get(extraction_type)
        
        # Extracteurs de plateformes
        elif extraction_type in ['youtube', 'instagram', 'tiktok', 'spotify']:
            return self._platform_extractors.get(extraction_type)
        
        # Extracteurs d'empreintes
        elif extraction_type.endswith('_fingerprint'):
            content_type = extraction_type.replace('_fingerprint', '')
            return self._fingerprint_extractors.get(content_type)
        
        # Extracteurs de revenus
        elif extraction_type.endswith('_revenue'):
            platform = extraction_type.replace('_revenue', '')
            return self._revenue_extractors.get(platform)
        
        # Extracteurs de collaborations
        elif extraction_type.endswith('_collaboration'):
            platform = extraction_type.replace('_collaboration', '')
            return self._collaboration_extractors.get(platform)
        
        # Extracteurs de surveillance
        elif extraction_type.endswith('_surveillance'):
            platform = extraction_type.replace('_surveillance', '')
            return self._surveillance_extractors.get(platform)
        
        return None
    
    async def _collect_metrics(self, job: ExtractionJob, worker_id: str):
        """Collecte les métriques de performance"""
        try:
            metrics = {
                'job_id': job.job_id,
                'extraction_type': job.extraction_type,
                'worker_id': worker_id,
                'processing_time': job.processing_time,
                'status': job.status,
                'priority': job.priority.value,
                'mode': job.mode.value,
                'timestamp': datetime.now().isoformat()
            }
            
            # Ici on pourrait envoyer vers un système de monitoring
            self.logger.debug(f"Metrics collected: {metrics}")
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
    
    # ==================== Interface publique ====================
    
    def configure_platform_extractor(self, platform: str, **config):
        """Configure un extracteur de plateforme avec ses paramètres"""
        platform = platform.lower()
        
        try:
            if platform == 'youtube':
                api_key = config.get('api_key')
                if api_key:
                    self._platform_extractors['youtube'] = YouTubeExtractor(api_key)
                    self._revenue_extractors['youtube'] = YouTubeRevenueExtractor(api_key)
                    self._collaboration_extractors['youtube'] = YouTubeCollaborationExtractor(api_key)
                    self._surveillance_extractors['youtube'] = YouTubeSurveillanceExtractor(api_key)
            
            elif platform == 'instagram':
                access_token = config.get('access_token')
                if access_token:
                    self._platform_extractors['instagram'] = InstagramExtractor(access_token)
            
            elif platform == 'tiktok':
                api_key = config.get('api_key')
                if api_key:
                    self._platform_extractors['tiktok'] = TikTokExtractor(api_key)
            
            elif platform == 'spotify':
                client_id = config.get('client_id')
                client_secret = config.get('client_secret')
                if client_id and client_secret:
                    self._platform_extractors['spotify'] = SpotifyExtractor(client_id, client_secret)
                    self._revenue_extractors['spotify'] = SpotifyRevenueExtractor(client_id, client_secret)
            
            self.logger.info(f"Platform {platform} configured successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to configure platform {platform}: {e}")
            raise
    
    async def submit_extraction(self, extraction_type: str, request: ExtractionRequest,
                              priority: PriorityLevel = PriorityLevel.NORMAL,
                              mode: ExtractionMode = None) -> str:
        """Soumet une tâche d'extraction et retourne l'ID du job"""
        
        job_id = str(uuid.uuid4())
        mode = mode or self._default_mode
        
        job = ExtractionJob(
            job_id=job_id,
            extraction_type=extraction_type,
            priority=priority,
            request=request,
            mode=mode
        )
        
        self._active_jobs[job_id] = job
        await self._job_queue.put(job)
        
        self.logger.info(f"Submitted extraction job {job_id} (type: {extraction_type}, priority: {priority.name})")
        
        return job_id
    
    async def extract_content(self, content_type: str, request: ExtractionRequest) -> ExtractionResult:
        """Extraction synchrone de contenu"""
        job_id = await self.submit_extraction(content_type, request, PriorityLevel.HIGH)
        return await self.wait_for_result(job_id)
    
    async def extract_platform_data(self, platform: str, request: ExtractionRequest) -> ExtractionResult:
        """Extraction synchrone de données de plateforme"""
        job_id = await self.submit_extraction(platform, request, PriorityLevel.NORMAL)
        return await self.wait_for_result(job_id)
    
    async def create_fingerprint(self, content_type: str, request: ExtractionRequest) -> ExtractionResult:
        """Création synchrone d'empreinte digitale"""
        job_id = await self.submit_extraction(f"{content_type}_fingerprint", request, PriorityLevel.HIGH)
        return await self.wait_for_result(job_id)
    
    async def analyze_revenue(self, platform: str, request: ExtractionRequest) -> ExtractionResult:
        """Analyse synchrone de revenus"""
        job_id = await self.submit_extraction(f"{platform}_revenue", request, PriorityLevel.NORMAL)
        return await self.wait_for_result(job_id)
    
    async def find_collaborations(self, platform: str, request: ExtractionRequest) -> ExtractionResult:
        """Recherche synchrone de collaborations"""
        job_id = await self.submit_extraction(f"{platform}_collaboration", request, PriorityLevel.NORMAL)
        return await self.wait_for_result(job_id)
    
    async def monitor_surveillance(self, platform: str, request: ExtractionRequest) -> ExtractionResult:
        """Surveillance synchrone"""
        job_id = await self.submit_extraction(f"{platform}_surveillance", request, PriorityLevel.HIGH)
        return await self.wait_for_result(job_id)
    
    async def wait_for_result(self, job_id: str, timeout: Optional[float] = None) -> ExtractionResult:
        """Attend le résultat d'une tâche"""
        timeout = timeout or 300  # 5 minutes par défaut
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            job = self._active_jobs.get(job_id)
            
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            if job.status == "completed":
                return job.result
            elif job.status == "failed":
                raise RuntimeError(f"Job failed: {job.error}")
            elif job.status == "cancelled":
                raise RuntimeError("Job was cancelled")
            
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"Job {job_id} timed out")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'une tâche"""
        job = self._active_jobs.get(job_id)
        
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'extraction_type': job.extraction_type,
            'status': job.status,
            'priority': job.priority.name,
            'mode': job.mode.name,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'processing_time': job.processing_time,
            'error': job.error
        }
    
    def list_capabilities(self) -> Dict[str, List[ExtractorCapability]]:
        """Liste toutes les capacités disponibles"""
        capabilities = {
            'content_extraction': [
                ExtractorCapability(
                    name="Audio Content Analysis",
                    description="Advanced AI-powered audio content extraction and analysis",
                    supported_formats=['mp3', 'wav', 'flac', 'aac', 'm4a'],
                    ai_features=['speech_recognition', 'music_analysis', 'emotion_detection', 'fingerprinting'],
                    performance_tier="enterprise"
                ),
                ExtractorCapability(
                    name="Video Content Analysis", 
                    description="Comprehensive video content extraction with computer vision",
                    supported_formats=['mp4', 'avi', 'mov', 'mkv', 'webm'],
                    ai_features=['object_detection', 'scene_analysis', 'face_recognition', 'text_extraction'],
                    performance_tier="enterprise"
                ),
                ExtractorCapability(
                    name="Image Content Analysis",
                    description="AI-powered image analysis and metadata extraction",
                    supported_formats=['jpg', 'png', 'gif', 'bmp', 'webp'],
                    ai_features=['object_detection', 'text_ocr', 'face_recognition', 'style_analysis'],
                    performance_tier="premium"
                ),
                ExtractorCapability(
                    name="Text Content Analysis",
                    description="Natural language processing and text analysis",
                    supported_formats=['txt', 'md', 'html', 'pdf', 'docx'],
                    ai_features=['sentiment_analysis', 'entity_extraction', 'language_detection', 'summarization'],
                    performance_tier="standard"
                )
            ],
            'platform_extraction': [
                ExtractorCapability(
                    name="YouTube Data Extraction",
                    description="Comprehensive YouTube channel and video analysis",
                    supported_formats=['youtube_urls', 'channel_ids', 'video_ids'],
                    ai_features=['engagement_analysis', 'trend_detection', 'revenue_estimation'],
                    performance_tier="enterprise"
                ),
                ExtractorCapability(
                    name="Instagram Data Extraction",
                    description="Instagram profile and content analysis",
                    supported_formats=['instagram_urls', 'usernames'],
                    ai_features=['engagement_analysis', 'hashtag_analysis', 'influencer_scoring'],
                    performance_tier="premium"
                ),
                ExtractorCapability(
                    name="TikTok Data Extraction",
                    description="TikTok content and trend analysis",
                    supported_formats=['tiktok_urls', 'usernames'],
                    ai_features=['viral_prediction', 'trend_analysis', 'music_detection'],
                    performance_tier="premium"
                ),
                ExtractorCapability(
                    name="Spotify Data Extraction",
                    description="Spotify music and artist analysis",
                    supported_formats=['spotify_urls', 'track_ids', 'artist_ids'],
                    ai_features=['music_analysis', 'popularity_prediction', 'playlist_optimization'],
                    performance_tier="standard"
                )
            ],
            'fingerprinting': [
                ExtractorCapability(
                    name="Advanced Fingerprinting",
                    description="Industrial-grade content fingerprinting for protection",
                    supported_formats=['all_media_types'],
                    ai_features=['perceptual_hashing', 'similarity_detection', 'duplicate_identification'],
                    performance_tier="enterprise"
                )
            ],
            'revenue_analysis': [
                ExtractorCapability(
                    name="Revenue Analytics",
                    description="AI-powered revenue analysis and monetization optimization",
                    supported_formats=['platform_data'],
                    ai_features=['revenue_prediction', 'optimization_recommendations', 'trend_analysis'],
                    performance_tier="enterprise"
                )
            ],
            'collaboration_matching': [
                ExtractorCapability(
                    name="Creator Collaboration Matching",
                    description="AI-powered creator matching and collaboration opportunities",
                    supported_formats=['creator_profiles'],
                    ai_features=['compatibility_analysis', 'audience_overlap', 'roi_prediction'],
                    performance_tier="premium"
                )
            ],
            'surveillance': [
                ExtractorCapability(
                    name="Content Surveillance",
                    description="Advanced content monitoring and protection",
                    supported_formats=['all_platforms'],
                    ai_features=['copyright_detection', 'brand_monitoring', 'threat_analysis'],
                    performance_tier="enterprise"
                )
            ]
        }
        
        return capabilities
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques système"""
        return {
            'active_jobs': len(self._active_jobs),
            'queue_size': self._job_queue.qsize(),
            'workers_active': len([w for w in self._worker_pool if not w.done()]),
            'total_workers': len(self._worker_pool),
            'is_running': self._is_running,
            'extractors_configured': {
                'content': len([e for e in self._content_extractors.values() if e]),
                'platform': len([e for e in self._platform_extractors.values() if e]),
                'fingerprint': len([e for e in self._fingerprint_extractors.values() if e]),
                'revenue': len([e for e in self._revenue_extractors.values() if e]),
                'collaboration': len([e for e in self._collaboration_extractors.values() if e]),
                'surveillance': len([e for e in self._surveillance_extractors.values() if e])
            }
        }
    
    async def shutdown(self):
        """Arrêt propre du système"""
        self.logger.info("Shutting down extraction orchestrator...")
        
        self._is_running = False
        self._shutdown_event.set()
        
        # Attendre que tous les workers se terminent
        if self._worker_pool:
            await asyncio.gather(*self._worker_pool, return_exceptions=True)
        
        # Nettoyer les ressources
        self._active_jobs.clear()
        
        self.logger.info("Extraction orchestrator shut down successfully")


# Instance globale de l'orchestrateur
orchestrator = ExtractionOrchestrator()

# Interface de haut niveau simplifiée
class ExtractionInterface:
    """Interface simplifiée pour l'extraction de contenu"""
    
    def __init__(self):
        self.orchestrator = orchestrator
    
    async def configure_apis(self, **api_configs):
        """Configure toutes les APIs en une fois"""
        for platform, config in api_configs.items():
            self.orchestrator.configure_platform_extractor(platform, **config)
    
    async def extract(self, source: str, extraction_type: str = "auto", **options) -> ExtractionResult:
        """Interface unifiée d'extraction"""
        request = ExtractionRequest(
            url=source if source.startswith('http') else None,
            content=source if not source.startswith('http') else None,
            metadata=options
        )
        
        if extraction_type == "auto":
            # Détection automatique du type
            if source.startswith('http'):
                if 'youtube.com' in source or 'youtu.be' in source:
                    extraction_type = 'youtube'
                elif 'instagram.com' in source:
                    extraction_type = 'instagram'
                elif 'tiktok.com' in source:
                    extraction_type = 'tiktok'
                elif 'spotify.com' in source:
                    extraction_type = 'spotify'
            else:
                # Détection basée sur l'extension ou le contenu
                if source.endswith(('.mp3', '.wav', '.flac')):
                    extraction_type = 'audio'
                elif source.endswith(('.mp4', '.avi', '.mov')):
                    extraction_type = 'video'
                elif source.endswith(('.jpg', '.png', '.gif')):
                    extraction_type = 'image'
                else:
                    extraction_type = 'text'
        
        # Sélection de la méthode d'extraction appropriée
        if extraction_type in ['audio', 'video', 'image', 'text']:
            return await self.orchestrator.extract_content(extraction_type, request)
        elif extraction_type in ['youtube', 'instagram', 'tiktok', 'spotify']:
            return await self.orchestrator.extract_platform_data(extraction_type, request)
        else:
            raise ValueError(f"Unsupported extraction type: {extraction_type}")
    
    async def create_fingerprint(self, source: str, content_type: str = "auto") -> ExtractionResult:
        """Création d'empreinte digitale simplifiée"""
        request = ExtractionRequest(
            url=source if source.startswith('http') else None,
            content=source if not source.startswith('http') else None
        )
        
        if content_type == "auto":
            # Détection automatique
            if source.endswith(('.mp3', '.wav', '.flac')):
                content_type = 'audio'
            elif source.endswith(('.mp4', '.avi', '.mov')):
                content_type = 'video'
            elif source.endswith(('.jpg', '.png', '.gif')):
                content_type = 'image'
            else:
                content_type = 'text'
        
        return await self.orchestrator.create_fingerprint(content_type, request)
    
    async def analyze_revenue(self, platform: str, creator_id: str, **options) -> ExtractionResult:
        """Analyse de revenus simplifiée"""
        request = ExtractionRequest(
            metadata={'creator_id': creator_id, **options}
        )
        
        return await self.orchestrator.analyze_revenue(platform, request)
    
    async def find_collaborations(self, platform: str, creator_profile: Dict[str, Any]) -> ExtractionResult:
        """Recherche de collaborations simplifiée"""
        request = ExtractionRequest(
            metadata={'creator_profile': creator_profile}
        )
        
        return await self.orchestrator.find_collaborations(platform, request)
    
    async def monitor_content(self, platform: str, targets: List[str], **options) -> ExtractionResult:
        """Surveillance de contenu simplifiée"""
        request = ExtractionRequest(
            metadata={'targets': targets, **options}
        )
        
        return await self.orchestrator.monitor_surveillance(platform, request)


# Instance globale de l'interface simplifiée
extraction_interface = ExtractionInterface()

# Fonctions utilitaires de haut niveau
async def quick_extract(source: str, **options) -> ExtractionResult:
    """Extraction rapide avec détection automatique"""
    return await extraction_interface.extract(source, **options)

async def quick_fingerprint(source: str) -> ExtractionResult:
    """Création rapide d'empreinte digitale"""
    return await extraction_interface.create_fingerprint(source)

async def quick_revenue_analysis(platform: str, creator_id: str) -> ExtractionResult:
    """Analyse rapide de revenus"""
    return await extraction_interface.analyze_revenue(platform, creator_id)

async def setup_apis(**api_configs):
    """Configuration rapide des APIs"""
    await extraction_interface.configure_apis(**api_configs)

# Export des composants principaux
__all__ = [
    'ExtractionOrchestrator',
    'ExtractionInterface', 
    'ExtractionJob',
    'ExtractorCapability',
    'ExtractionMode',
    'PriorityLevel',
    'orchestrator',
    'extraction_interface',
    'quick_extract',
    'quick_fingerprint', 
    'quick_revenue_analysis',
    'setup_apis'
]
