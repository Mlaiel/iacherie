#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SERVICE REGISTRY ENTERPRISE - CONTENT SERVICE REGISTRY
=========================================================

**Author**: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Project**: Ainflue Service Registry Enterprise
**Version**: 1.0 Production
**Created**: 2025-01-07 | Updated: 2025-12-14

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture service registry et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

🎬 CONTENT SERVICE REGISTRY
Registry spécialisé pour services contenu Ainflue.
Content-aware registration + media processing service discovery + creator workflows.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Set, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
from pathlib import Path

# Core logger
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types de contenu supportés"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"
    LIVE_STREAM = "live_stream"
    PODCAST = "podcast"
    MUSIC = "music"

class ProcessingCapability(Enum):
    """Capacités de traitement de contenu"""
    ENCODE = "encode"
    DECODE = "decode"
    ENHANCE = "enhance"
    ANALYZE = "analyze"
    METADATA_EXTRACT = "metadata_extract"
    TRANSCODE = "transcode"
    THUMBNAIL = "thumbnail"
    QUALITY_ANALYSIS = "quality_analysis"
    WATERMARK = "watermark"
    RESIZE = "resize"
    OPTIMIZE = "optimize"
    FILTER = "filter"
    NOISE_REDUCTION = "noise_reduction"
    UPSCALING = "upscaling"
    COLORIZATION = "colorization"

class BusinessPriority(Enum):
    """Priorité business pour services contenu"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ResourceRequirements:
    """Exigences de ressources pour service contenu"""
    gpu: bool = False
    gpu_memory_gb: Optional[int] = None
    memory_gb: int = 4
    storage_gb: int = 50
    cpu_cores: int = 2
    bandwidth_mbps: int = 100
    special_hardware: Optional[List[str]] = None

@dataclass
class SLARequirements:
    """Exigences SLA pour service contenu"""
    latency_ms: int = 1000
    availability: float = 0.99
    throughput_requests_per_second: int = 100
    error_rate_threshold: float = 0.01
    recovery_time_seconds: int = 60

@dataclass
class ContentServiceCapabilities:
    """Capacités d'un service de contenu"""
    supported_content_types: Set[ContentType]
    processing_capabilities: Set[ProcessingCapability]
    supported_formats: Dict[ContentType, List[str]]
    quality_levels: List[str]
    concurrent_processing_limit: int
    batch_processing_support: bool = False
    real_time_processing_support: bool = True

@dataclass
class ContentServiceInstance:
    """Instance de service contenu avec métadonnées spécialisées"""
    service_id: str
    service_name: str
    host: str
    port: int
    content_capabilities: ContentServiceCapabilities
    resource_requirements: ResourceRequirements
    sla_requirements: SLARequirements
    business_priority: BusinessPriority
    content_domains: Set[str]  # domaines métier (music, video, podcast, etc.)
    creator_types_supported: Set[str]  # musiciens, influenceurs, podcasters, etc.
    protocol: str = "http"
    health_check_endpoint: str = "/health"
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    version: str = "1.0.0"
    region: str = "default"
    datacenter: str = "default"
    environment: str = "production"
    weight: int = 100
    created_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    processing_queue_size: int = 0
    active_sessions: int = 0

@dataclass
class ContentRegistrationResult:
    """Résultat d'enregistrement service contenu"""
    success: bool
    service_id: str
    registration_time: float
    assigned_cluster: Optional[str] = None
    resource_allocation: Optional[Dict[str, Any]] = None
    sla_validation_result: Optional[Dict[str, Any]] = None
    content_routing_rules: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

@dataclass
class ContentDiscoveryRequest:
    """Requête de découverte service contenu"""
    content_type: ContentType
    required_capabilities: Set[ProcessingCapability]
    content_format: Optional[str] = None
    quality_requirements: Optional[str] = None
    latency_requirement_ms: Optional[int] = None
    throughput_requirement: Optional[int] = None
    region_preference: Optional[str] = None
    creator_type: Optional[str] = None
    business_priority: Optional[BusinessPriority] = None
    metadata_filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentDiscoveryResult:
    """Résultat de découverte service contenu"""
    matching_services: List[ContentServiceInstance]
    optimal_service: Optional[ContentServiceInstance]
    load_balancing_recommendations: List[Dict[str, Any]]
    routing_strategy: str
    estimated_processing_time_ms: Optional[int] = None
    cost_estimation: Optional[Dict[str, float]] = None
    alternative_services: List[ContentServiceInstance] = field(default_factory=list)

class ContentServiceRegistry:
    """
    Registry spécialisé pour services contenu Ainflue.
    Content-aware registration + media processing service discovery + creator workflows.
    """
    
    def __init__(self, registry_config: Dict[str, Any] = None):
        """Initialisation du registry contenu"""
        self.registry_config = registry_config or {}
        self.content_services: Dict[str, ContentServiceInstance] = {}
        self.content_clusters: Dict[ContentType, List[str]] = {}
        self.processing_queues: Dict[str, List[str]] = {}
        self.load_balancer = ContentLoadBalancer()
        self.quality_monitor = ContentQualityMonitor()
        self.resource_optimizer = ContentResourceOptimizer()
        self.workflow_coordinator = CreatorWorkflowCoordinator()
        
        # Initialisation des clusters par type de contenu
        for content_type in ContentType:
            self.content_clusters[content_type] = []
            
        # Configuration des types de services prédéfinis
        self._initialize_content_service_types()
        
        logger.info("🎬 Content Service Registry initialized")

    def _initialize_content_service_types(self):
        """Initialisation des types de services contenu prédéfinis"""
        self.content_service_types = {
            'audio_processing': {
                'content_types': {ContentType.AUDIO, ContentType.MUSIC, ContentType.PODCAST},
                'required_capabilities': {
                    ProcessingCapability.ENCODE, 
                    ProcessingCapability.ENHANCE, 
                    ProcessingCapability.ANALYZE, 
                    ProcessingCapability.METADATA_EXTRACT,
                    ProcessingCapability.NOISE_REDUCTION
                },
                'resource_requirements': ResourceRequirements(
                    gpu=True, gpu_memory_gb=8, memory_gb=16, storage_gb=200, 
                    cpu_cores=8, bandwidth_mbps=500
                ),
                'sla_requirements': SLARequirements(
                    latency_ms=2000, availability=0.999, throughput_requests_per_second=50
                ),
                'business_priority': BusinessPriority.HIGH,
                'supported_formats': ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg']
            },
            'video_processing': {
                'content_types': {ContentType.VIDEO, ContentType.LIVE_STREAM},
                'required_capabilities': {
                    ProcessingCapability.TRANSCODE, 
                    ProcessingCapability.THUMBNAIL, 
                    ProcessingCapability.QUALITY_ANALYSIS, 
                    ProcessingCapability.WATERMARK,
                    ProcessingCapability.ENHANCE
                },
                'resource_requirements': ResourceRequirements(
                    gpu=True, gpu_memory_gb=16, memory_gb=32, storage_gb=1000, 
                    cpu_cores=16, bandwidth_mbps=1000
                ),
                'sla_requirements': SLARequirements(
                    latency_ms=5000, availability=0.999, throughput_requests_per_second=20
                ),
                'business_priority': BusinessPriority.HIGH,
                'supported_formats': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']
            },
            'image_processing': {
                'content_types': {ContentType.IMAGE},
                'required_capabilities': {
                    ProcessingCapability.RESIZE, 
                    ProcessingCapability.OPTIMIZE, 
                    ProcessingCapability.METADATA_EXTRACT, 
                    ProcessingCapability.FILTER,
                    ProcessingCapability.UPSCALING
                },
                'resource_requirements': ResourceRequirements(
                    gpu=False, memory_gb=8, storage_gb=100, 
                    cpu_cores=4, bandwidth_mbps=200
                ),
                'sla_requirements': SLARequirements(
                    latency_ms=1000, availability=0.99, throughput_requests_per_second=200
                ),
                'business_priority': BusinessPriority.MEDIUM,
                'supported_formats': ['jpg', 'png', 'gif', 'webp', 'svg', 'bmp']
            },
            'mixed_media_processing': {
                'content_types': {ContentType.MIXED_MEDIA, ContentType.VIDEO, ContentType.AUDIO},
                'required_capabilities': {
                    ProcessingCapability.ENCODE, 
                    ProcessingCapability.TRANSCODE, 
                    ProcessingCapability.ANALYZE, 
                    ProcessingCapability.ENHANCE,
                    ProcessingCapability.METADATA_EXTRACT
                },
                'resource_requirements': ResourceRequirements(
                    gpu=True, gpu_memory_gb=12, memory_gb=24, storage_gb=500, 
                    cpu_cores=12, bandwidth_mbps=800
                ),
                'sla_requirements': SLARequirements(
                    latency_ms=8000, availability=0.998, throughput_requests_per_second=30
                ),
                'business_priority': BusinessPriority.HIGH,
                'supported_formats': ['multiple']
            }
        }

    async def register_content_service(
        self, 
        content_service: ContentServiceInstance
    ) -> ContentRegistrationResult:
        """
        Enregistrement service contenu avec content-type awareness.
        
        Features:
        - Validation des capacités de traitement
        - Allocation de ressources optimisée
        - Clustering par type de contenu
        - Validation SLA
        - Configuration de routage intelligent
        """
        try:
            start_time = time.time()
            
            # Validation des capacités requises
            validation_result = await self._validate_content_service_capabilities(content_service)
            if not validation_result['valid']:
                return ContentRegistrationResult(
                    success=False,
                    service_id=content_service.service_id,
                    registration_time=time.time() - start_time,
                    error_message=f"Validation failed: {validation_result['error']}"
                )
            
            # Allocation de cluster optimal
            assigned_cluster = await self._assign_optimal_content_cluster(content_service)
            
            # Allocation de ressources
            resource_allocation = await self._allocate_content_resources(content_service)
            
            # Validation SLA
            sla_validation = await self._validate_content_sla_requirements(content_service)
            
            # Configuration des règles de routage
            routing_rules = await self._configure_content_routing_rules(content_service)
            
            # Enregistrement dans le registry
            self.content_services[content_service.service_id] = content_service
            
            # Ajout aux clusters appropriés
            for content_type in content_service.content_capabilities.supported_content_types:
                if content_service.service_id not in self.content_clusters[content_type]:
                    self.content_clusters[content_type].append(content_service.service_id)
            
            # Initialisation de la file de traitement
            self.processing_queues[content_service.service_id] = []
            
            # Notification aux coordinateurs de workflow
            await self.workflow_coordinator.notify_service_registration(content_service)
            
            registration_time = time.time() - start_time
            
            logger.info(
                f"🎬 Content service registered: {content_service.service_id} "
                f"[{content_service.service_name}] in {registration_time:.3f}s"
            )
            
            return ContentRegistrationResult(
                success=True,
                service_id=content_service.service_id,
                registration_time=registration_time,
                assigned_cluster=assigned_cluster,
                resource_allocation=resource_allocation,
                sla_validation_result=sla_validation,
                content_routing_rules=routing_rules,
                warnings=validation_result.get('warnings', [])
            )
            
        except Exception as e:
            logger.error(f"❌ Content service registration failed: {str(e)}")
            return ContentRegistrationResult(
                success=False,
                service_id=content_service.service_id,
                registration_time=time.time() - start_time if 'start_time' in locals() else 0,
                error_message=f"Registration error: {str(e)}"
            )

    async def discover_content_services(
        self, 
        discovery_request: ContentDiscoveryRequest
    ) -> ContentDiscoveryResult:
        """
        Découverte de services contenu avec critères spécialisés.
        
        Features:
        - Matching par type de contenu et capacités
        - Optimisation de charge et performance
        - Recommandations de load balancing
        - Estimation de coûts et temps de traitement
        """
        try:
            # Filtrage initial par type de contenu
            candidate_services = await self._filter_services_by_content_type(
                discovery_request.content_type
            )
            
            # Filtrage par capacités requises
            capability_matched_services = await self._filter_services_by_capabilities(
                candidate_services, discovery_request.required_capabilities
            )
            
            # Filtrage par critères de performance
            performance_filtered_services = await self._filter_services_by_performance(
                capability_matched_services, discovery_request
            )
            
            # Calcul des scores de matching
            scored_services = await self._calculate_content_service_scores(
                performance_filtered_services, discovery_request
            )
            
            # Sélection du service optimal
            optimal_service = await self._select_optimal_content_service(
                scored_services, discovery_request
            )
            
            # Génération des recommandations de load balancing
            load_balancing_recommendations = await self._generate_load_balancing_recommendations(
                scored_services, discovery_request
            )
            
            # Détermination de la stratégie de routage
            routing_strategy = await self._determine_routing_strategy(
                discovery_request, optimal_service
            )
            
            # Estimation du temps de traitement
            processing_time_estimation = await self._estimate_processing_time(
                optimal_service, discovery_request
            )
            
            # Estimation des coûts
            cost_estimation = await self._estimate_processing_costs(
                optimal_service, discovery_request
            )
            
            # Services alternatifs
            alternative_services = scored_services[1:6] if len(scored_services) > 1 else []
            
            logger.info(
                f"🔍 Content service discovery completed: "
                f"{len(scored_services)} services found for {discovery_request.content_type}"
            )
            
            return ContentDiscoveryResult(
                matching_services=scored_services,
                optimal_service=optimal_service,
                load_balancing_recommendations=load_balancing_recommendations,
                routing_strategy=routing_strategy,
                estimated_processing_time_ms=processing_time_estimation,
                cost_estimation=cost_estimation,
                alternative_services=alternative_services
            )
            
        except Exception as e:
            logger.error(f"❌ Content service discovery failed: {str(e)}")
            return ContentDiscoveryResult(
                matching_services=[],
                optimal_service=None,
                load_balancing_recommendations=[],
                routing_strategy="fallback",
                error_message=f"Discovery error: {str(e)}"
            )

    async def _validate_content_service_capabilities(
        self, 
        service: ContentServiceInstance
    ) -> Dict[str, Any]:
        """Validation des capacités de service contenu"""
        warnings = []
        
        # Validation des types de contenu supportés
        if not service.content_capabilities.supported_content_types:
            return {'valid': False, 'error': 'No content types specified'}
        
        # Validation des capacités de traitement
        if not service.content_capabilities.processing_capabilities:
            return {'valid': False, 'error': 'No processing capabilities specified'}
        
        # Validation de la cohérence ressources/capacités
        if ProcessingCapability.TRANSCODE in service.content_capabilities.processing_capabilities:
            if not service.resource_requirements.gpu:
                warnings.append('Video transcoding recommended with GPU acceleration')
        
        # Validation des formats supportés
        for content_type in service.content_capabilities.supported_content_types:
            if content_type not in service.content_capabilities.supported_formats:
                warnings.append(f'No supported formats specified for {content_type}')
        
        return {
            'valid': True,
            'warnings': warnings
        }

    async def _assign_optimal_content_cluster(
        self, 
        service: ContentServiceInstance
    ) -> str:
        """Attribution du cluster optimal pour le service contenu"""
        # Logique d'assignation basée sur le type de contenu principal et la charge
        primary_content_type = list(service.content_capabilities.supported_content_types)[0]
        cluster_load = len(self.content_clusters.get(primary_content_type, []))
        
        cluster_name = f"{primary_content_type.value}_cluster_{service.region}"
        logger.debug(f"Assigned service {service.service_id} to cluster {cluster_name}")
        
        return cluster_name
        
    async def _allocate_content_resources(
        self, 
        service: ContentServiceInstance
    ) -> Dict[str, Any]:
        """Allocation de ressources pour le service contenu"""
        return {
            'allocated_gpu': service.resource_requirements.gpu,
            'allocated_memory_gb': service.resource_requirements.memory_gb,
            'allocated_storage_gb': service.resource_requirements.storage_gb,
            'allocated_cpu_cores': service.resource_requirements.cpu_cores,
            'allocated_bandwidth_mbps': service.resource_requirements.bandwidth_mbps,
            'resource_pool': 'content_processing_pool'
        }
        
    async def _validate_content_sla_requirements(
        self, 
        service: ContentServiceInstance
    ) -> Dict[str, Any]:
        """Validation des exigences SLA pour le service contenu"""
        return {
            'sla_validated': True,
            'latency_compliance': service.sla_requirements.latency_ms <= 10000,
            'availability_compliance': service.sla_requirements.availability >= 0.95,
            'throughput_compliance': service.sla_requirements.throughput_requests_per_second >= 1
        }
        
    async def _configure_content_routing_rules(
        self, 
        service: ContentServiceInstance
    ) -> List[Dict[str, Any]]:
        """Configuration des règles de routage pour le service contenu"""
        routing_rules = []
        
        for content_type in service.content_capabilities.supported_content_types:
            rule = {
                'content_type': content_type.value,
                'service_id': service.service_id,
                'priority': service.business_priority.value,
                'weight': service.weight,
                'conditions': {
                    'format_match': list(service.content_capabilities.supported_formats.get(content_type, [])),
                    'quality_levels': service.content_capabilities.quality_levels,
                    'region': service.region
                }
            }
            routing_rules.append(rule)
            
        return routing_rules

    async def _filter_services_by_content_type(
        self, 
        content_type: ContentType
    ) -> List[ContentServiceInstance]:
        """Filtrage des services par type de contenu"""
        matching_services = []
        
        for service_id in self.content_clusters.get(content_type, []):
            service = self.content_services.get(service_id)
            if service and content_type in service.content_capabilities.supported_content_types:
                matching_services.append(service)
                
        return matching_services

    async def _filter_services_by_capabilities(
        self, 
        services: List[ContentServiceInstance],
        required_capabilities: Set[ProcessingCapability]
    ) -> List[ContentServiceInstance]:
        """Filtrage des services par capacités requises"""
        matching_services = []
        
        for service in services:
            if required_capabilities.issubset(service.content_capabilities.processing_capabilities):
                matching_services.append(service)
                
        return matching_services

    async def _filter_services_by_performance(
        self, 
        services: List[ContentServiceInstance],
        discovery_request: ContentDiscoveryRequest
    ) -> List[ContentServiceInstance]:
        """Filtrage des services par critères de performance"""
        matching_services = []
        
        for service in services:
            # Filtrage par latence
            if (discovery_request.latency_requirement_ms and 
                service.sla_requirements.latency_ms > discovery_request.latency_requirement_ms):
                continue
                
            # Filtrage par throughput
            if (discovery_request.throughput_requirement and
                service.sla_requirements.throughput_requests_per_second < discovery_request.throughput_requirement):
                continue
                
            # Filtrage par région
            if (discovery_request.region_preference and
                service.region != discovery_request.region_preference):
                continue
                
            matching_services.append(service)
            
        return matching_services

    async def _calculate_content_service_scores(
        self, 
        services: List[ContentServiceInstance],
        discovery_request: ContentDiscoveryRequest
    ) -> List[ContentServiceInstance]:
        """Calcul des scores de matching pour les services"""
        scored_services = []
        
        for service in services:
            score = 100  # Score de base
            
            # Bonus pour priorité business
            if discovery_request.business_priority:
                if service.business_priority == discovery_request.business_priority:
                    score += 20
                    
            # Bonus pour région préférée
            if discovery_request.region_preference == service.region:
                score += 15
                
            # Pénalité pour charge actuelle
            load_penalty = (service.active_sessions / max(service.sla_requirements.throughput_requests_per_second, 1)) * 30
            score -= load_penalty
            
            # Bonus pour capacités supplémentaires
            extra_capabilities = len(service.content_capabilities.processing_capabilities - discovery_request.required_capabilities)
            score += min(extra_capabilities * 5, 25)
            
            service.metadata['matching_score'] = max(0, score)
            scored_services.append(service)
            
        # Tri par score décroissant
        scored_services.sort(key=lambda s: s.metadata.get('matching_score', 0), reverse=True)
        
        return scored_services

    async def _select_optimal_content_service(
        self, 
        services: List[ContentServiceInstance],
        discovery_request: ContentDiscoveryRequest
    ) -> Optional[ContentServiceInstance]:
        """Sélection du service optimal"""
        if not services:
            return None
            
        # Le service avec le meilleur score
        return services[0]

    async def _generate_load_balancing_recommendations(
        self, 
        services: List[ContentServiceInstance],
        discovery_request: ContentDiscoveryRequest
    ) -> List[Dict[str, Any]]:
        """Génération des recommandations de load balancing"""
        recommendations = []
        
        total_capacity = sum(s.sla_requirements.throughput_requests_per_second for s in services)
        
        for service in services[:3]:  # Top 3 services
            capacity_ratio = service.sla_requirements.throughput_requests_per_second / max(total_capacity, 1)
            load_ratio = service.active_sessions / max(service.sla_requirements.throughput_requests_per_second, 1)
            
            recommendation = {
                'service_id': service.service_id,
                'recommended_weight': int(capacity_ratio * 100),
                'current_load': load_ratio,
                'available_capacity': max(0, service.sla_requirements.throughput_requests_per_second - service.active_sessions),
                'strategy': 'weighted_round_robin' if len(services) > 1 else 'direct'
            }
            recommendations.append(recommendation)
            
        return recommendations

    async def _determine_routing_strategy(
        self, 
        discovery_request: ContentDiscoveryRequest,
        optimal_service: Optional[ContentServiceInstance]
    ) -> str:
        """Détermination de la stratégie de routage"""
        if not optimal_service:
            return "fallback"
            
        if discovery_request.latency_requirement_ms and discovery_request.latency_requirement_ms < 500:
            return "low_latency"
        elif discovery_request.throughput_requirement and discovery_request.throughput_requirement > 100:
            return "high_throughput"
        else:
            return "balanced"

    async def _estimate_processing_time(
        self, 
        service: Optional[ContentServiceInstance],
        discovery_request: ContentDiscoveryRequest
    ) -> Optional[int]:
        """Estimation du temps de traitement"""
        if not service:
            return None
            
        base_time = service.sla_requirements.latency_ms
        
        # Ajustement basé sur la charge actuelle
        load_factor = service.active_sessions / max(service.sla_requirements.throughput_requests_per_second, 1)
        adjusted_time = base_time * (1 + load_factor)
        
        return int(adjusted_time)

    async def _estimate_processing_costs(
        self, 
        service: Optional[ContentServiceInstance],
        discovery_request: ContentDiscoveryRequest
    ) -> Optional[Dict[str, float]]:
        """Estimation des coûts de traitement"""
        if not service:
            return None
            
        # Coûts basés sur les ressources et la complexité
        base_cost = 0.01  # Coût de base
        
        if service.resource_requirements.gpu:
            base_cost += 0.05
            
        if ProcessingCapability.TRANSCODE in service.content_capabilities.processing_capabilities:
            base_cost += 0.03
            
        return {
            'processing_cost_usd': base_cost,
            'estimated_total_cost_usd': base_cost * 1.2,  # Inclut marge et overhead
            'currency': 'USD'
        }

    async def get_content_service_health(self, service_id: str) -> Dict[str, Any]:
        """Récupération de l'état de santé d'un service contenu"""
        service = self.content_services.get(service_id)
        if not service:
            return {'error': 'Service not found'}
            
        return {
            'service_id': service_id,
            'status': 'healthy' if time.time() - service.last_heartbeat < 30 else 'unhealthy',
            'last_heartbeat': service.last_heartbeat,
            'active_sessions': service.active_sessions,
            'processing_queue_size': service.processing_queue_size,
            'uptime_seconds': time.time() - service.created_at,
            'resource_utilization': await self._get_resource_utilization(service)
        }

    async def _get_resource_utilization(self, service: ContentServiceInstance) -> Dict[str, float]:
        """Récupération de l'utilisation des ressources"""
        # Simulation d'utilisation des ressources
        return {
            'cpu_percent': min(100, (service.active_sessions / max(service.sla_requirements.throughput_requests_per_second, 1)) * 80),
            'memory_percent': min(100, (service.processing_queue_size / 100) * 60),
            'gpu_percent': min(100, (service.active_sessions / max(service.sla_requirements.throughput_requests_per_second, 1)) * 70) if service.resource_requirements.gpu else 0,
            'storage_percent': 25  # Valeur simulée
        }

    async def update_service_load(self, service_id: str, active_sessions: int, queue_size: int) -> bool:
        """Mise à jour de la charge d'un service"""
        service = self.content_services.get(service_id)
        if not service:
            return False
            
        service.active_sessions = active_sessions
        service.processing_queue_size = queue_size
        service.last_heartbeat = time.time()
        
        logger.debug(f"Updated load for service {service_id}: {active_sessions} sessions, {queue_size} queued")
        return True

class ContentLoadBalancer:
    """Load balancer spécialisé pour services contenu"""
    
    def __init__(self):
        self.strategies = {
            'round_robin': self._round_robin,
            'weighted_round_robin': self._weighted_round_robin,
            'least_connections': self._least_connections,
            'content_aware': self._content_aware_balancing
        }
        
    async def _round_robin(self, services: List[ContentServiceInstance]) -> ContentServiceInstance:
        """Load balancing round robin simple"""
        return services[0] if services else None
        
    async def _weighted_round_robin(self, services: List[ContentServiceInstance]) -> ContentServiceInstance:
        """Load balancing pondéré par capacité"""
        if not services:
            return None
        return max(services, key=lambda s: s.weight)
        
    async def _least_connections(self, services: List[ContentServiceInstance]) -> ContentServiceInstance:
        """Load balancing par nombre minimal de connexions"""
        if not services:
            return None
        return min(services, key=lambda s: s.active_sessions)
        
    async def _content_aware_balancing(self, services: List[ContentServiceInstance]) -> ContentServiceInstance:
        """Load balancing intelligent basé sur le contenu"""
        if not services:
            return None
        # Sélection basée sur la charge et les capacités
        return min(services, key=lambda s: s.active_sessions / max(s.sla_requirements.throughput_requests_per_second, 1))

class ContentQualityMonitor:
    """Moniteur de qualité pour services contenu"""
    
    async def monitor_content_quality(self, service_id: str) -> Dict[str, Any]:
        """Monitoring de la qualité de traitement contenu"""
        return {
            'quality_score': 95.5,
            'processing_accuracy': 0.98,
            'error_rate': 0.02,
            'average_processing_time_ms': 1500,
            'throughput_actual': 45,
            'sla_compliance': 0.995
        }

class ContentResourceOptimizer:
    """Optimiseur de ressources pour services contenu"""
    
    async def optimize_resource_allocation(self, service_id: str) -> Dict[str, Any]:
        """Optimisation de l'allocation de ressources"""
        return {
            'optimization_recommendations': [
                'Increase GPU memory allocation for better video processing',
                'Consider horizontal scaling for peak hours',
                'Optimize storage allocation for temporary files'
            ],
            'estimated_performance_improvement': 15,
            'cost_optimization_potential': 8
        }

class CreatorWorkflowCoordinator:
    """Coordinateur de workflows créateurs"""
    
    async def notify_service_registration(self, service: ContentServiceInstance):
        """Notification d'enregistrement de service aux workflows créateurs"""
        logger.info(f"🎨 Notifying creator workflows about new content service: {service.service_id}")
        
        # Ici on notifierait les différents workflows créateurs
        # selon les types de contenu et capacités du service
        
    async def coordinate_creator_workflow(self, creator_type: str, content_type: ContentType) -> Dict[str, Any]:
        """Coordination d'un workflow créateur spécifique"""
        workflows = {
            'musician': ['upload', 'audio_enhance', 'metadata_extract', 'rights_protect', 'distribute'],
            'video_creator': ['upload', 'transcode', 'thumbnail', 'seo_optimize', 'monetize', 'distribute'],
            'podcaster': ['upload', 'audio_process', 'transcript', 'chapter_mark', 'distribute'],
            'influencer': ['upload', 'multi_format', 'optimize', 'cross_platform_distribute']
        }
        
        workflow_steps = workflows.get(creator_type, ['upload', 'process', 'distribute'])
        
        return {
            'workflow_id': f"{creator_type}_{content_type.value}_{int(time.time())}",
            'steps': workflow_steps,
            'estimated_duration_minutes': len(workflow_steps) * 5,
            'required_services': workflow_steps
        }

# Factory function
def create_content_service_registry(config: Dict[str, Any] = None) -> ContentServiceRegistry:
    """Factory function pour créer un Content Service Registry"""
    return ContentServiceRegistry(config)

# Export des classes principales
__all__ = [
    'ContentServiceRegistry',
    'ContentServiceInstance', 
    'ContentRegistrationResult',
    'ContentDiscoveryRequest',
    'ContentDiscoveryResult',
    'ContentType',
    'ProcessingCapability',
    'BusinessPriority',
    'ResourceRequirements',
    'SLARequirements',
    'ContentServiceCapabilities',
    'create_content_service_registry'
]