# WARNING: Potential SQL injection risk - use parameterized queries
"""
🎨 Content Service Discovery Enterprise - Ainflue
================================================
Service discovery spécialisé pour services contenu Ainflue.
Media processing + content analysis + creator services discovery.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Service Discovery
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""

import asyncio
import time
import logging
import json
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from .distributed_service_registry import ServiceInstance, ServiceStatus
from .intelligent_load_balancer import IntelligentLoadBalancer, RequestContext, RequestType

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types de contenu supportés"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"

class ProcessingCapability(Enum):
    """Capacités de traitement"""
    ENCODING = "encoding"
    TRANSCODING = "transcoding"
    ENHANCEMENT = "enhancement"
    ANALYSIS = "analysis"
    THUMBNAIL = "thumbnail"
    METADATA_EXTRACTION = "metadata_extraction"
    QUALITY_ANALYSIS = "quality_analysis"
    CONTENT_MODERATION = "content_moderation"
    WATERMARKING = "watermarking"
    FINGERPRINTING = "fingerprinting"
    COMPRESSION = "compression"
    FORMAT_CONVERSION = "format_conversion"

class StorageType(Enum):
    """Types de stockage"""
    HOT_STORAGE = "hot_storage"  # Accès fréquent
    WARM_STORAGE = "warm_storage"  # Accès occasionnel
    COLD_STORAGE = "cold_storage"  # Archivage
    CDN_EDGE = "cdn_edge"  # Distribution
    BACKUP = "backup"  # Sauvegarde

class QualityTier(Enum):
    """Niveaux de qualité"""
    LOW = "low"        # 480p, 64kbps audio
    STANDARD = "standard"  # 720p, 128kbps audio
    HIGH = "high"      # 1080p, 256kbps audio
    PREMIUM = "premium"  # 4K, 320kbps audio
    LOSSLESS = "lossless"  # Sans perte

@dataclass
class ContentRequest:
    """Requête de traitement de contenu"""
    request_id: str
    content_type: ContentType
    creator_id: str
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_requirements: List[ProcessingCapability] = field(default_factory=list)
    quality_tier: QualityTier = QualityTier.STANDARD
    deadline: Optional[datetime] = None
    storage_preferences: List[StorageType] = field(default_factory=list)
    geographic_restrictions: List[str] = field(default_factory=list)
    monetization_enabled: bool = True
    collaboration_enabled: bool = False
    priority: int = 1  # 1=low, 5=high

@dataclass
class ContentServiceResult:
    """Résultat de découverte de services contenu"""
    success: bool
    selected_services: Dict[ProcessingCapability, List[ServiceInstance]] = field(default_factory=dict)
    estimated_processing_time: Optional[float] = None  # minutes
    estimated_cost: float = 0.0
    quality_assurance_score: float = 0.0
    recommended_workflow: List[str] = field(default_factory=list)
    storage_allocation: Dict[StorageType, List[ServiceInstance]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

@dataclass
class CreatorProfile:
    """Profil créateur pour optimisation des services"""
    creator_id: str
    subscription_tier: str = "free"  # free, premium, enterprise
    content_types: Set[ContentType] = field(default_factory=set)
    average_content_size: float = 0.0  # MB
    monthly_content_volume: int = 0
    preferred_quality: QualityTier = QualityTier.STANDARD
    regions: List[str] = field(default_factory=list)
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    monetization_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentServicePattern:
    """Pattern de service pour type de contenu"""
    pattern_id: str
    content_type: ContentType
    required_capabilities: List[ProcessingCapability]
    preferred_regions: List[str] = field(default_factory=list)
    gpu_requirements: bool = False
    storage_proximity: bool = False
    high_memory: bool = False
    fast_processing: bool = False
    cdn_integration: bool = False
    backup_requirements: bool = True

class ContentServiceRegistry:
    """Registry spécialisé pour services contenu"""
    
    def __init__(self):
        self.content_services: Dict[str, List[ServiceInstance]] = {}
        self.service_capabilities: Dict[str, List[ProcessingCapability]] = {}
        self.service_patterns = self._initialize_content_patterns()
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.performance_metrics: Dict[str, Dict] = {}
    
    def _initialize_content_patterns(self) -> Dict[str, ContentServicePattern]:
        """Initialiser les patterns de services contenu"""
        return {
            ContentType.AUDIO.value: ContentServicePattern(
                pattern_id="audio_processing",
                content_type=ContentType.AUDIO,
                required_capabilities=[
                    ProcessingCapability.ENCODING,
                    ProcessingCapability.ENHANCEMENT,
                    ProcessingCapability.ANALYSIS,
                    ProcessingCapability.FINGERPRINTING
                ],
                preferred_regions=['us-east-1', 'eu-west-1'],
                gpu_requirements=True,
                fast_processing=True
            ),
            ContentType.VIDEO.value: ContentServicePattern(
                pattern_id="video_processing",
                content_type=ContentType.VIDEO,
                required_capabilities=[
                    ProcessingCapability.TRANSCODING,
                    ProcessingCapability.THUMBNAIL,
                    ProcessingCapability.QUALITY_ANALYSIS,
                    ProcessingCapability.WATERMARKING
                ],
                storage_proximity=True,
                high_memory=True,
                gpu_requirements=True,
                cdn_integration=True
            ),
            ContentType.IMAGE.value: ContentServicePattern(
                pattern_id="image_processing",
                content_type=ContentType.IMAGE,
                required_capabilities=[
                    ProcessingCapability.ENHANCEMENT,
                    ProcessingCapability.COMPRESSION,
                    ProcessingCapability.THUMBNAIL,
                    ProcessingCapability.METADATA_EXTRACTION
                ],
                cdn_integration=True,
                fast_processing=True
            ),
            ContentType.LIVESTREAM.value: ContentServicePattern(
                pattern_id="livestream_processing",
                content_type=ContentType.LIVESTREAM,
                required_capabilities=[
                    ProcessingCapability.TRANSCODING,
                    ProcessingCapability.ANALYSIS,
                    ProcessingCapability.CONTENT_MODERATION
                ],
                gpu_requirements=True,
                fast_processing=True,
                cdn_integration=True,
                backup_requirements=False  # Temps réel
            ),
            ContentType.PODCAST.value: ContentServicePattern(
                pattern_id="podcast_processing",
                content_type=ContentType.PODCAST,
                required_capabilities=[
                    ProcessingCapability.ENCODING,
                    ProcessingCapability.ENHANCEMENT,
                    ProcessingCapability.METADATA_EXTRACTION,
                    ProcessingCapability.FINGERPRINTING
                ],
                preferred_regions=['us-east-1', 'eu-west-1'],
                cdn_integration=True
            )
        }
    
    async def register_content_service(self, service: ServiceInstance, 
                                     capabilities: List[ProcessingCapability]) -> bool:
        """Enregistrer un service de contenu avec ses capacités"""
        try:
            service_type = service.metadata.get('content_service_type', 'generic')
            
            if service_type not in self.content_services:
                self.content_services[service_type] = []
            
            # Ajouter les métadonnées de contenu
            service.metadata.update({
                'content_capabilities': [cap.value for cap in capabilities],
                'gpu_enabled': service.metadata.get('gpu_enabled', False),
                'max_file_size_mb': service.metadata.get('max_file_size_mb', 1000),
                'supported_formats': service.metadata.get('supported_formats', []),
                'processing_speed_factor': service.metadata.get('processing_speed_factor', 1.0)
            })
            
            self.content_services[service_type].append(service)
            self.service_capabilities[service.service_id] = capabilities
            
            # Initialiser les métriques de performance
            self.performance_metrics[service.service_id] = {
                'avg_processing_time': 0.0,
                'success_rate': 1.0,
                'quality_score': 0.8,
                'total_processed': 0,
                'last_performance_update': time.time()
            }
            
            logger.info(f"✅ Service contenu enregistré: {service.service_id} avec {len(capabilities)} capacités")
            return True
            
        except Exception as e:
            logger.error(f"Erreur enregistrement service contenu: {e}")
            return False
    
    async def get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Obtenir le profil d'un créateur"""
        if creator_id in self.creator_profiles:
            return self.creator_profiles[creator_id]
        
        # Créer un profil par défaut si inexistant
        profile = CreatorProfile(
            creator_id=creator_id,
            subscription_tier="free",
            content_types={ContentType.IMAGE, ContentType.AUDIO},
            preferred_quality=QualityTier.STANDARD
        )
        
        self.creator_profiles[creator_id] = profile
        return profile
    
    async def update_creator_profile(self, creator_id: str, profile_data: Dict[str, Any]) -> bool:
        """Mettre à jour le profil d'un créateur"""
        try:
            if creator_id not in self.creator_profiles:
                self.creator_profiles[creator_id] = CreatorProfile(creator_id=creator_id)
            
            profile = self.creator_profiles[creator_id]
            
            # Mettre à jour les champs du profil
            for key, value in profile_data.items():
                if hasattr(profile, key):
                    if key == 'content_types' and isinstance(value, list):
                        profile.content_types = {ContentType(ct) for ct in value}
                    elif key == 'preferred_quality' and isinstance(value, str):
                        profile.preferred_quality = QualityTier(value)
                    else:
                        setattr(profile, key, value)
            
            logger.info(f"✅ Profil créateur mis à jour: {creator_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour profil créateur: {e}")
            return False
    
    async def record_processing_metrics(self, service_id: str, processing_time: float, 
                                      success: bool, quality_score: float):
        """Enregistrer les métriques de traitement"""
        if service_id in self.performance_metrics:
            metrics = self.performance_metrics[service_id]
            
            # Mise à jour des moyennes mobiles
            total_processed = metrics['total_processed']
            
            # Temps de traitement moyen
            new_avg_time = ((metrics['avg_processing_time'] * total_processed) + processing_time) / (total_processed + 1)
            metrics['avg_processing_time'] = new_avg_time
            
            # Taux de succès
            current_successes = metrics['success_rate'] * total_processed
            new_successes = current_successes + (1 if success else 0)
            metrics['success_rate'] = new_successes / (total_processed + 1)
            
            # Score de qualité moyen
            new_quality = ((metrics['quality_score'] * total_processed) + quality_score) / (total_processed + 1)
            metrics['quality_score'] = new_quality
            
            metrics['total_processed'] += 1
            metrics['last_performance_update'] = time.time()

class ContentWorkflowOptimizer:
    """Optimiseur de workflow de traitement de contenu"""
    
    def __init__(self, service_registry: ContentServiceRegistry):
        self.service_registry = service_registry
        self.workflow_templates: Dict[str, List[str]] = self._initialize_workflow_templates()
        self.cost_models: Dict[ProcessingCapability, float] = self._initialize_cost_models()
    
    def _initialize_workflow_templates(self) -> Dict[str, List[str]]:
        """Initialiser les templates de workflow"""
        return {
            ContentType.AUDIO.value: [
                "audio_upload",
                "format_validation",
                "enhancement",
                "encoding",
                "fingerprinting",
                "metadata_extraction",
                "quality_analysis",
                "cdn_upload",
                "notification"
            ],
            ContentType.VIDEO.value: [
                "video_upload",
                "format_validation",
                "thumbnail_generation",
                "transcoding",
                "quality_analysis",
                "watermarking",
                "cdn_upload",
                "backup_storage",
                "notification"
            ],
            ContentType.IMAGE.value: [
                "image_upload",
                "format_validation",
                "enhancement",
                "compression",
                "thumbnail_generation",
                "metadata_extraction",
                "cdn_upload",
                "notification"
            ],
            ContentType.LIVESTREAM.value: [
                "stream_ingestion",
                "real_time_transcoding",
                "content_moderation",
                "cdn_distribution",
                "analytics_tracking",
                "recording_backup"
            ]
        }
    
    def _initialize_cost_models(self) -> Dict[ProcessingCapability, float]:
        """Initialiser les modèles de coût par capacité"""
        return {
            ProcessingCapability.ENCODING: 0.05,  # $ per minute
            ProcessingCapability.TRANSCODING: 0.10,
            ProcessingCapability.ENHANCEMENT: 0.08,
            ProcessingCapability.ANALYSIS: 0.03,
            ProcessingCapability.THUMBNAIL: 0.01,
            ProcessingCapability.METADATA_EXTRACTION: 0.02,
            ProcessingCapability.QUALITY_ANALYSIS: 0.04,
            ProcessingCapability.CONTENT_MODERATION: 0.06,
            ProcessingCapability.WATERMARKING: 0.03,
            ProcessingCapability.FINGERPRINTING: 0.05,
            ProcessingCapability.COMPRESSION: 0.02,
            ProcessingCapability.FORMAT_CONVERSION: 0.04
        }
    
    async def optimize_content_workflow(self, content_request: ContentRequest) -> List[str]:
        """Optimiser le workflow pour une requête de contenu"""
        try:
            content_type = content_request.content_type
            base_workflow = self.workflow_templates.get(content_type.value, [])
            
            # Personnaliser selon les requirements
            optimized_workflow = base_workflow.copy()
            
            # Ajouter des étapes selon les capacités requises
            for capability in content_request.processing_requirements:
                if capability == ProcessingCapability.CONTENT_MODERATION:
                    if "content_moderation" not in optimized_workflow:
                        # Insérer après validation
                        insert_index = next((i for i, step in enumerate(optimized_workflow) 
                                           if "validation" in step), 1)
                        optimized_workflow.insert(insert_index + 1, "content_moderation")
                
                elif capability == ProcessingCapability.WATERMARKING:
                    if "watermarking" not in optimized_workflow:
                        # Insérer avant upload CDN
                        insert_index = next((i for i, step in enumerate(optimized_workflow) 
                                           if "cdn_upload" in step), len(optimized_workflow))
                        optimized_workflow.insert(insert_index, "watermarking")
            
            # Optimiser selon le niveau de qualité
            if content_request.quality_tier == QualityTier.PREMIUM:
                if "quality_enhancement" not in optimized_workflow:
                    insert_index = next((i for i, step in enumerate(optimized_workflow) 
                                       if any(proc in step for proc in ["encoding", "transcoding"])), 2)
                    optimized_workflow.insert(insert_index, "quality_enhancement")
            
            # Optimiser selon la deadline
            if content_request.deadline:
                time_until_deadline = (content_request.deadline - datetime.now()).total_seconds() / 60
                if time_until_deadline < 30:  # Moins de 30 minutes
                    # Workflow accéléré - supprimer les étapes non essentielles
                    optional_steps = ["quality_analysis", "backup_storage"]
                    optimized_workflow = [step for step in optimized_workflow if step not in optional_steps]
            
            # Optimiser selon la collaboration
            if content_request.collaboration_enabled:
                if "collaboration_setup" not in optimized_workflow:
                    optimized_workflow.insert(1, "collaboration_setup")
                if "collaboration_notification" not in optimized_workflow:
                    optimized_workflow.append("collaboration_notification")
            
            logger.info(f"🔄 Workflow optimisé pour {content_type.value}: {len(optimized_workflow)} étapes")
            return optimized_workflow
            
        except Exception as e:
            logger.error(f"Erreur optimisation workflow: {e}")
            return self.workflow_templates.get(content_request.content_type.value, [])
    
    async def estimate_processing_cost(self, content_request: ContentRequest, 
                                     selected_services: Dict[ProcessingCapability, List[ServiceInstance]]) -> float:
        """Estimer le coût de traitement"""
        try:
            total_cost = 0.0
            content_size_factor = max(1.0, content_request.content_metadata.get('size_mb', 100) / 100)
            
            for capability, services in selected_services.items():
                if capability in self.cost_models:
                    base_cost = self.cost_models[capability]
                    
                    # Facteur de taille
                    cost_with_size = base_cost * content_size_factor
                    
                    # Facteur de qualité
                    quality_multiplier = {
                        QualityTier.LOW: 0.5,
                        QualityTier.STANDARD: 1.0,
                        QualityTier.HIGH: 1.5,
                        QualityTier.PREMIUM: 2.0,
                        QualityTier.LOSSLESS: 3.0
                    }.get(content_request.quality_tier, 1.0)
                    
                    cost_with_quality = cost_with_size * quality_multiplier
                    
                    # Facteur de priorité
                    priority_multiplier = 1.0 + (content_request.priority - 1) * 0.2
                    
                    final_cost = cost_with_quality * priority_multiplier
                    total_cost += final_cost
            
            # Rabais pour créateurs premium
            creator_profile = await self.service_registry.get_creator_profile(content_request.creator_id)
            if creator_profile and creator_profile.subscription_tier == "premium":
                total_cost *= 0.8
            elif creator_profile and creator_profile.subscription_tier == "enterprise":
                total_cost *= 0.6
            
            return round(total_cost, 3)
            
        except Exception as e:
            logger.error(f"Erreur estimation coût: {e}")
            return 0.0
    
    async def estimate_processing_time(self, content_request: ContentRequest,
                                     selected_services: Dict[ProcessingCapability, List[ServiceInstance]]) -> float:
        """Estimer le temps de traitement en minutes"""
        try:
            total_time = 0.0
            content_size_mb = content_request.content_metadata.get('size_mb', 100)
            
            # Temps de base selon le type de contenu
            base_times = {
                ContentType.AUDIO: 0.1,  # minutes par MB
                ContentType.VIDEO: 0.5,
                ContentType.IMAGE: 0.02,
                ContentType.LIVESTREAM: 0.0,  # Temps réel
                ContentType.PODCAST: 0.15,
                ContentType.DOCUMENT: 0.05
            }
            
            base_time = base_times.get(content_request.content_type, 0.1) * content_size_mb
            
            # Ajustements selon les capacités
            for capability, services in selected_services.items():
                if services:
                    service = services[0]  # Utiliser le premier service
                    
                    # Facteur de performance du service
                    speed_factor = service.metadata.get('processing_speed_factor', 1.0)
                    
                    # Temps selon la capacité
                    capability_times = {
                        ProcessingCapability.ENCODING: base_time * 0.3,
                        ProcessingCapability.TRANSCODING: base_time * 1.5,
                        ProcessingCapability.ENHANCEMENT: base_time * 0.8,
                        ProcessingCapability.ANALYSIS: base_time * 0.2,
                        ProcessingCapability.THUMBNAIL: 0.5,  # fixe
                        ProcessingCapability.WATERMARKING: base_time * 0.1,
                        ProcessingCapability.FINGERPRINTING: base_time * 0.4
                    }
                    
                    capability_time = capability_times.get(capability, base_time * 0.2)
                    adjusted_time = capability_time / speed_factor
                    total_time += adjusted_time
            
            # Ajustement selon la qualité
            quality_multipliers = {
                QualityTier.LOW: 0.5,
                QualityTier.STANDARD: 1.0,
                QualityTier.HIGH: 1.8,
                QualityTier.PREMIUM: 3.0,
                QualityTier.LOSSLESS: 5.0
            }
            
            quality_multiplier = quality_multipliers.get(content_request.quality_tier, 1.0)
            total_time *= quality_multiplier
            
            # Ajustement selon la charge actuelle
            # (En production, obtenir depuis métriques temps réel)
            load_factor = 1.2  # 20% de charge supplémentaire
            total_time *= load_factor
            
            return max(1.0, round(total_time, 1))  # Minimum 1 minute
            
        except Exception as e:
            logger.error(f"Erreur estimation temps: {e}")
            return 10.0  # Temps par défaut

class ContentServiceDiscovery:
    """
    Service discovery spécialisé pour services contenu Ainflue.
    Media processing + content analysis + creator services discovery.
    """
    
    def __init__(self):
        self.service_registry = ContentServiceRegistry()
        self.workflow_optimizer = ContentWorkflowOptimizer(self.service_registry)
        self.load_balancer = IntelligentLoadBalancer()
        
        # Métriques de performance
        self.discovery_stats: Dict[str, Any] = {
            'total_requests': 0,
            'successful_discoveries': 0,
            'avg_response_time': 0.0,
            'content_type_distribution': {},
            'creator_tier_distribution': {}
        }
        
        logger.info("🎨 ContentServiceDiscovery initialisé")
    
    async def discover_content_processing_services(self, content_request: ContentRequest) -> ContentServiceResult:
        """Discovery services processing contenu avec content-type awareness"""
        try:
            start_time = time.time()
            self.discovery_stats['total_requests'] += 1
            
            # Obtenir le profil du créateur
            creator_profile = await self.service_registry.get_creator_profile(content_request.creator_id)
            
            # Optimiser le workflow
            recommended_workflow = await self.workflow_optimizer.optimize_content_workflow(content_request)
            
            # Découvrir les services pour chaque capacité requise
            selected_services: Dict[ProcessingCapability, List[ServiceInstance]] = {}
            
            # Utiliser les capacités du pattern ou celles spécifiées
            content_pattern = self.service_registry.service_patterns.get(content_request.content_type.value)
            
            required_capabilities = content_request.processing_requirements
            if not required_capabilities and content_pattern:
                required_capabilities = content_pattern.required_capabilities
            
            for capability in required_capabilities:
                services = await self._find_services_for_capability(
                    capability, content_request, creator_profile
                )
                if services:
                    selected_services[capability] = services
            
            # Découvrir les services de stockage
            storage_allocation = await self._discover_storage_services(content_request, creator_profile)
            
            # Estimer coûts et temps
            estimated_cost = await self.workflow_optimizer.estimate_processing_cost(
                content_request, selected_services
            )
            
            estimated_time = await self.workflow_optimizer.estimate_processing_time(
                content_request, selected_services
            )
            
            # Calculer le score de qualité
            quality_score = await self._calculate_quality_assurance_score(
                selected_services, content_request
            )
            
            # Créer le résultat
            result = ContentServiceResult(
                success=len(selected_services) > 0,
                selected_services=selected_services,
                estimated_processing_time=estimated_time,
                estimated_cost=estimated_cost,
                quality_assurance_score=quality_score,
                recommended_workflow=recommended_workflow,
                storage_allocation=storage_allocation
            )
            
            if not result.success:
                result.errors.append(f"Aucun service trouvé pour {content_request.content_type.value}")
            
            # Mettre à jour les statistiques
            processing_time = time.time() - start_time
            await self._update_discovery_stats(content_request, result, processing_time)
            
            logger.info(f"🎯 Content discovery pour {content_request.content_type.value}: {len(selected_services)} capacités, {estimated_time:.1f}min, ${estimated_cost}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur content discovery: {e}")
            return ContentServiceResult(
                success=False,
                errors=[str(e)]
            )
    
    async def _find_services_for_capability(self, capability: ProcessingCapability, 
                                          content_request: ContentRequest,
                                          creator_profile: Optional[CreatorProfile]) -> List[ServiceInstance]:
        """Trouver les services pour une capacité spécifique"""
        try:
            candidate_services = []
            
            # Chercher dans tous les services contenu
            for service_type, services in self.service_registry.content_services.items():
                for service in services:
                    service_capabilities = self.service_registry.service_capabilities.get(
                        service.service_id, []
                    )
                    
                    if capability in service_capabilities:
                        # Vérifier si le service peut traiter ce type de contenu
                        if await self._service_supports_content_type(service, content_request.content_type):
                            candidate_services.append(service)
            
            # Filtrer par santé et disponibilité
            healthy_services = [s for s in candidate_services if s.status == ServiceStatus.HEALTHY]
            
            if not healthy_services:
                return []
            
            # Utiliser le load balancer intelligent pour sélectionner
            request_context = RequestContext(
                request_id=content_request.request_id,
                user_id=content_request.creator_id,
                request_type=self._map_capability_to_request_type(capability),
                priority=content_request.priority,
                metadata={
                    'content_type': content_request.content_type.value,
                    'quality_tier': content_request.quality_tier.value,
                    'file_size_mb': content_request.content_metadata.get('size_mb', 0)
                }
            )
            
            # Sélectionner le meilleur service
            best_service = await self.load_balancer.select_optimal_instance(
                f"content_{capability.value}",
                healthy_services,
                request_context
            )
            
            return [best_service] if best_service else []
            
        except Exception as e:
            logger.error(f"Erreur recherche services pour {capability.value}: {e}")
            return []
    
    async def _service_supports_content_type(self, service: ServiceInstance, 
                                           content_type: ContentType) -> bool:
        """Vérifier si un service supporte un type de contenu"""
        supported_formats = service.metadata.get('supported_formats', [])
        
        # Mapping type de contenu -> formats
        content_format_mapping = {
            ContentType.AUDIO: ['mp3', 'wav', 'aac', 'flac', 'ogg'],
            ContentType.VIDEO: ['mp4', 'avi', 'mov', 'mkv', 'webm'],
            ContentType.IMAGE: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
            ContentType.LIVESTREAM: ['rtmp', 'hls', 'dash', 'webrtc'],
            ContentType.PODCAST: ['mp3', 'aac', 'wav'],
            ContentType.DOCUMENT: ['pdf', 'doc', 'docx', 'txt']
        }
        
        expected_formats = content_format_mapping.get(content_type, [])
        
        # Si pas de formats spécifiés, accepter tous
        if not supported_formats:
            return True
        
        # Vérifier intersection
        return bool(set(supported_formats).intersection(set(expected_formats)))
    
    def _map_capability_to_request_type(self, capability: ProcessingCapability) -> RequestType:
        """Mapper une capacité vers un type de requête"""
        capability_mapping = {
            ProcessingCapability.ENCODING: RequestType.CPU_INTENSIVE,
            ProcessingCapability.TRANSCODING: RequestType.CPU_INTENSIVE,
            ProcessingCapability.ENHANCEMENT: RequestType.CPU_INTENSIVE,
            ProcessingCapability.ANALYSIS: RequestType.BALANCED,
            ProcessingCapability.THUMBNAIL: RequestType.MEMORY_INTENSIVE,
            ProcessingCapability.METADATA_EXTRACTION: RequestType.IO_INTENSIVE,
            ProcessingCapability.QUALITY_ANALYSIS: RequestType.CPU_INTENSIVE,
            ProcessingCapability.CONTENT_MODERATION: RequestType.CPU_INTENSIVE,
            ProcessingCapability.WATERMARKING: RequestType.MEMORY_INTENSIVE,
            ProcessingCapability.FINGERPRINTING: RequestType.CPU_INTENSIVE,
            ProcessingCapability.COMPRESSION: RequestType.CPU_INTENSIVE,
            ProcessingCapability.FORMAT_CONVERSION: RequestType.BALANCED
        }
        
        return capability_mapping.get(capability, RequestType.BALANCED)
    
    async def _discover_storage_services(self, content_request: ContentRequest,
                                       creator_profile: Optional[CreatorProfile]) -> Dict[StorageType, List[ServiceInstance]]:
        """Découvrir les services de stockage"""
        storage_allocation = {}
        
        # Déterminer les besoins de stockage selon le type de contenu
        storage_needs = []
        
        if content_request.content_type in [ContentType.VIDEO, ContentType.AUDIO, ContentType.PODCAST]:
            storage_needs.extend([StorageType.HOT_STORAGE, StorageType.CDN_EDGE, StorageType.WARM_STORAGE])
        elif content_request.content_type == ContentType.LIVESTREAM:
            storage_needs.extend([StorageType.CDN_EDGE, StorageType.HOT_STORAGE])
        else:
            storage_needs.extend([StorageType.HOT_STORAGE, StorageType.CDN_EDGE])
        
        # Ajouter backup si nécessaire
        content_pattern = self.service_registry.service_patterns.get(content_request.content_type.value)
        if content_pattern and content_pattern.backup_requirements:
            storage_needs.append(StorageType.BACKUP)
        
        # Simuler la découverte de services de stockage
        for storage_type in storage_needs:
            # En production, interroger le registry pour les services de stockage
            mock_storage_service = ServiceInstance(
                service_id=f"storage-{storage_type.value}-001",
                service_name=f"storage_{storage_type.value}",
                host="storage.ainflue.com",
                port=443,
                health_check_url="/health",
                metadata={
                    'storage_type': storage_type.value,
                    'capacity_gb': 10000,
                    'available_gb': 8000
                }
            )
            storage_allocation[storage_type] = [mock_storage_service]
        
        return storage_allocation
    
    async def _calculate_quality_assurance_score(self, selected_services: Dict[ProcessingCapability, List[ServiceInstance]],
                                                content_request: ContentRequest) -> float:
        """Calculer le score d'assurance qualité"""
        try:
            if not selected_services:
                return 0.0
            
            total_score = 0.0
            service_count = 0
            
            for capability, services in selected_services.items():
                for service in services:
                    # Score basé sur les métriques de performance
                    service_metrics = self.service_registry.performance_metrics.get(service.service_id, {})
                    
                    success_rate = service_metrics.get('success_rate', 0.8)
                    quality_score = service_metrics.get('quality_score', 0.8)
                    
                    # Score combiné
                    service_score = (success_rate * 0.6) + (quality_score * 0.4)
                    
                    # Bonus pour services GPU si requis
                    if service.metadata.get('gpu_enabled') and content_request.content_type in [ContentType.VIDEO, ContentType.AUDIO]:
                        service_score *= 1.1
                    
                    # Bonus pour services avec capacités spécialisées
                    service_capabilities = len(self.service_registry.service_capabilities.get(service.service_id, []))
                    specialization_bonus = min(0.2, service_capabilities * 0.02)
                    service_score += specialization_bonus
                    
                    total_score += service_score
                    service_count += 1
            
            # Score moyen avec normalisation
            avg_score = total_score / service_count if service_count > 0 else 0.0
            return min(1.0, max(0.0, avg_score))
            
        except Exception as e:
            logger.error(f"Erreur calcul quality score: {e}")
            return 0.5
    
    async def _update_discovery_stats(self, content_request: ContentRequest, 
                                    result: ContentServiceResult, processing_time: float):
        """Mettre à jour les statistiques de discovery"""
        try:
            stats = self.discovery_stats
            
            # Mise à jour du temps de réponse moyen
            total_requests = stats['total_requests']
            current_avg = stats['avg_response_time']
            new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
            stats['avg_response_time'] = new_avg
            
            # Compteur de succès
            if result.success:
                stats['successful_discoveries'] += 1
            
            # Distribution par type de contenu
            content_type = content_request.content_type.value
            if content_type not in stats['content_type_distribution']:
                stats['content_type_distribution'][content_type] = 0
            stats['content_type_distribution'][content_type] += 1
            
            # Distribution par tier créateur
            creator_profile = await self.service_registry.get_creator_profile(content_request.creator_id)
            if creator_profile:
                tier = creator_profile.subscription_tier
                if tier not in stats['creator_tier_distribution']:
                    stats['creator_tier_distribution'][tier] = 0
                stats['creator_tier_distribution'][tier] += 1
            
        except Exception as e:
            logger.error(f"Erreur mise à jour stats: {e}")
    
    async def register_content_service(self, service: ServiceInstance, 
                                     capabilities: List[ProcessingCapability]) -> bool:
        """Enregistrer un service de contenu"""
        return await self.service_registry.register_content_service(service, capabilities)
    
    async def update_creator_profile(self, creator_id: str, profile_data: Dict[str, Any]) -> bool:
        """Mettre à jour le profil d'un créateur"""
        return await self.service_registry.update_creator_profile(creator_id, profile_data)
    
    async def get_content_discovery_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de discovery de contenu"""
        stats = self.discovery_stats.copy()
        
        # Ajouter des métriques calculées
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_discoveries'] / stats['total_requests']
        else:
            stats['success_rate'] = 0.0
        
        # Ajouter les stats des services
        stats['registered_services'] = len(self.service_registry.content_services)
        stats['total_capabilities'] = len(self.service_registry.service_capabilities)
        stats['registered_creators'] = len(self.service_registry.creator_profiles)
        
        return stats

# Factory function
def create_content_service_discovery() -> ContentServiceDiscovery:
    """Factory pour créer un service discovery de contenu"""
    return ContentServiceDiscovery()

__all__ = [
    'ContentServiceDiscovery',
    'ContentType',
    'ProcessingCapability',
    'StorageType',
    'QualityTier',
    'ContentRequest',
    'ContentServiceResult',
    'CreatorProfile',
    'ContentServicePattern',
    'ContentServiceRegistry',
    'ContentWorkflowOptimizer',
    'create_content_service_discovery'
]