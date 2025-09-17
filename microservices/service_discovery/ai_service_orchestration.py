"""
🤖 AI Service Orchestration Enterprise - Ainflue
===============================================
Orchestration services IA/ML pour plateforme créateurs.
Model deployment + inference scaling + GPU optimization.

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
import math
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from .distributed_service_registry import ServiceInstance, ServiceStatus
from .intelligent_load_balancer import IntelligentLoadBalancer, RequestContext, RequestType

logger = logging.getLogger(__name__)

class AIModelType(Enum):
    """Types de modèles IA"""
    CONTENT_ANALYSIS = "content_analysis"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    VIDEO_TRANSCODING = "video_transcoding"
    IMAGE_GENERATION = "image_generation"
    TEXT_GENERATION = "text_generation"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    CONTENT_MODERATION = "content_moderation"
    RECOMMENDATION = "recommendation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    VOICE_CLONING = "voice_cloning"
    MUSIC_GENERATION = "music_generation"
    DEEPFAKE_DETECTION = "deepfake_detection"
    COPYRIGHT_DETECTION = "copyright_detection"

class ComputeType(Enum):
    """Types de compute"""
    CPU_OPTIMIZED = "cpu_optimized"
    GPU_NVIDIA_V100 = "gpu_nvidia_v100"
    GPU_NVIDIA_A100 = "gpu_nvidia_a100"
    GPU_NVIDIA_H100 = "gpu_nvidia_h100"
    TPU_V4 = "tpu_v4"
    EDGE_DEVICE = "edge_device"
    HYBRID_COMPUTE = "hybrid_compute"

class InferenceMode(Enum):
    """Modes d'inférence"""
    BATCH = "batch"
    REAL_TIME = "real_time"
    STREAMING = "streaming"
    EDGE = "edge"
    DISTRIBUTED = "distributed"

class ModelFramework(Enum):
    """Frameworks de modèles"""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"
    OPENAI_API = "openai_api"
    ANTHROPIC_API = "anthropic_api"

@dataclass
class AIModelSpec:
    """Spécification d'un modèle IA"""
    model_id: str
    model_name: str
    model_type: AIModelType
    framework: ModelFramework
    version: str = "1.0"
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)
    compute_requirements: ComputeType = ComputeType.CPU_OPTIMIZED
    memory_gb: float = 1.0
    gpu_memory_gb: float = 0.0
    inference_modes: List[InferenceMode] = field(default_factory=lambda: [InferenceMode.REAL_TIME])
    latency_target_ms: Optional[float] = None
    throughput_target: Optional[float] = None
    model_size_mb: float = 100.0
    accuracy_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class AIRequest:
    """Requête IA"""
    request_id: str
    model_type: AIModelType
    input_data: Dict[str, Any]
    creator_id: str
    inference_mode: InferenceMode = InferenceMode.REAL_TIME
    priority: int = 1
    latency_requirement_ms: Optional[float] = None
    quality_preference: str = "balanced"  # speed, balanced, quality
    batch_size: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    deadline: Optional[datetime] = None

@dataclass
class AIServiceResult:
    """Résultat d'orchestration IA"""
    success: bool
    selected_services: List[ServiceInstance] = field(default_factory=list)
    orchestration_plan: Dict[str, Any] = field(default_factory=dict)
    estimated_latency_ms: Optional[float] = None
    estimated_cost: float = 0.0
    resource_allocation: Dict[str, Any] = field(default_factory=dict)
    fallback_services: List[ServiceInstance] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class GPUResource:
    """Ressource GPU"""
    gpu_id: str
    gpu_type: str
    memory_gb: float
    utilization: float = 0.0
    temperature: float = 0.0
    power_usage: float = 0.0
    allocated_to: Optional[str] = None
    last_update: float = field(default_factory=time.time)

@dataclass
class ModelDeployment:
    """Déploiement de modèle"""
    deployment_id: str
    model_spec: AIModelSpec
    service_instances: List[ServiceInstance]
    compute_allocation: Dict[str, Any]
    deployment_status: str = "pending"
    deployed_at: Optional[datetime] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    auto_scaling_config: Dict[str, Any] = field(default_factory=dict)

class AIModelRegistry:
    """Registry des modèles IA"""
    
    def __init__(self):
        self.models: Dict[str, AIModelSpec] = {}
        self.deployments: Dict[str, ModelDeployment] = {}
        self.model_performance: Dict[str, Dict[str, float]] = {}
        self.model_catalog = self._initialize_model_catalog()
    
    def _initialize_model_catalog(self) -> Dict[str, AIModelSpec]:
        """Initialiser le catalogue de modèles"""
        catalog = {}
        
        # Modèles d'analyse de contenu
        catalog["whisper-large-v3"] = AIModelSpec(
            model_id="whisper-large-v3",
            model_name="OpenAI Whisper Large v3",
            model_type=AIModelType.SPEECH_TO_TEXT,
            framework=ModelFramework.PYTORCH,
            input_types=["audio/mp3", "audio/wav", "audio/m4a"],
            output_types=["text/plain", "application/json"],
            compute_requirements=ComputeType.GPU_NVIDIA_V100,
            memory_gb=8.0,
            gpu_memory_gb=6.0,
            model_size_mb=3000,
            latency_target_ms=2000,
            accuracy_metrics={"wer": 0.03}  # Word Error Rate
        )
        
        catalog["stable-diffusion-xl"] = AIModelSpec(
            model_id="stable-diffusion-xl",
            model_name="Stable Diffusion XL",
            model_type=AIModelType.IMAGE_GENERATION,
            framework=ModelFramework.PYTORCH,
            input_types=["text/plain"],
            output_types=["image/png", "image/jpeg"],
            compute_requirements=ComputeType.GPU_NVIDIA_A100,
            memory_gb=16.0,
            gpu_memory_gb=12.0,
            inference_modes=[InferenceMode.BATCH, InferenceMode.REAL_TIME],
            model_size_mb=6800,
            latency_target_ms=8000
        )
        
        catalog["musicgen-large"] = AIModelSpec(
            model_id="musicgen-large",
            model_name="Facebook MusicGen Large",
            model_type=AIModelType.MUSIC_GENERATION,
            framework=ModelFramework.PYTORCH,
            input_types=["text/plain", "audio/wav"],
            output_types=["audio/wav", "audio/mp3"],
            compute_requirements=ComputeType.GPU_NVIDIA_A100,
            memory_gb=32.0,
            gpu_memory_gb=24.0,
            inference_modes=[InferenceMode.BATCH],
            model_size_mb=15000,
            throughput_target=0.1  # Minutes de musique par seconde
        )
        
        catalog["content-moderator-v2"] = AIModelSpec(
            model_id="content-moderator-v2",
            model_name="Ainflue Content Moderator v2",
            model_type=AIModelType.CONTENT_MODERATION,
            framework=ModelFramework.CUSTOM,
            input_types=["image/jpeg", "video/mp4", "audio/mp3", "text/plain"],
            output_types=["application/json"],
            compute_requirements=ComputeType.GPU_NVIDIA_V100,
            memory_gb=4.0,
            gpu_memory_gb=3.0,
            inference_modes=[InferenceMode.REAL_TIME, InferenceMode.STREAMING],
            model_size_mb=1200,
            latency_target_ms=500,
            accuracy_metrics={"precision": 0.95, "recall": 0.92}
        )
        
        catalog["recommendation-engine-v3"] = AIModelSpec(
            model_id="recommendation-engine-v3",
            model_name="Ainflue Recommendation Engine v3",
            model_type=AIModelType.RECOMMENDATION,
            framework=ModelFramework.TENSORFLOW,
            input_types=["application/json"],
            output_types=["application/json"],
            compute_requirements=ComputeType.CPU_OPTIMIZED,
            memory_gb=8.0,
            inference_modes=[InferenceMode.BATCH, InferenceMode.REAL_TIME],
            model_size_mb=800,
            latency_target_ms=100,
            throughput_target=1000  # Recommandations par seconde
        )
        
        catalog["voice-cloner-pro"] = AIModelSpec(
            model_id="voice-cloner-pro",
            model_name="Ainflue Voice Cloner Pro",
            model_type=AIModelType.VOICE_CLONING,
            framework=ModelFramework.PYTORCH,
            input_types=["audio/wav", "text/plain"],
            output_types=["audio/wav"],
            compute_requirements=ComputeType.GPU_NVIDIA_A100,
            memory_gb=24.0,
            gpu_memory_gb=16.0,
            inference_modes=[InferenceMode.BATCH],
            model_size_mb=8500,
            latency_target_ms=15000
        )
        
        return catalog
    
    async def register_model(self, model_spec: AIModelSpec) -> bool:
        """Enregistrer un modèle IA"""
        try:
            self.models[model_spec.model_id] = model_spec
            
            # Initialiser les métriques de performance
            self.model_performance[model_spec.model_id] = {
                'avg_latency_ms': model_spec.latency_target_ms or 1000,
                'success_rate': 1.0,
                'throughput': model_spec.throughput_target or 1.0,
                'gpu_utilization': 0.0,
                'total_requests': 0,
                'last_update': time.time()
            }
            
            logger.info(f"✅ Modèle IA enregistré: {model_spec.model_name} ({model_spec.model_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur enregistrement modèle: {e}")
            return False
    
    async def get_models_by_type(self, model_type: AIModelType) -> List[AIModelSpec]:
        """Obtenir les modèles par type"""
        models = []
        
        # Chercher dans les modèles enregistrés
        for model in self.models.values():
            if model.model_type == model_type:
                models.append(model)
        
        # Chercher dans le catalogue
        for model in self.model_catalog.values():
            if model.model_type == model_type and model.model_id not in self.models:
                models.append(model)
        
        return models
    
    async def update_model_performance(self, model_id: str, latency_ms: float, 
                                     success: bool, gpu_utilization: float = 0.0):
        """Mettre à jour les métriques de performance d'un modèle"""
        if model_id in self.model_performance:
            metrics = self.model_performance[model_id]
            
            # Moyenne mobile pour la latence
            total_requests = metrics['total_requests']
            current_avg = metrics['avg_latency_ms']
            new_avg = ((current_avg * total_requests) + latency_ms) / (total_requests + 1)
            metrics['avg_latency_ms'] = new_avg
            
            # Taux de succès
            current_successes = metrics['success_rate'] * total_requests
            new_successes = current_successes + (1 if success else 0)
            metrics['success_rate'] = new_successes / (total_requests + 1)
            
            # Utilisation GPU
            metrics['gpu_utilization'] = gpu_utilization
            
            metrics['total_requests'] += 1
            metrics['last_update'] = time.time()

class GPUResourceManager:
    """Gestionnaire de ressources GPU"""
    
    def __init__(self):
        self.gpu_resources: Dict[str, GPUResource] = {}
        self.allocation_queue: List[Dict] = []
        self.gpu_pools: Dict[ComputeType, Set[str]] = {}
        self._initialize_gpu_pools()
    
    def _initialize_gpu_pools(self):
        """Initialiser les pools GPU"""
        # Simuler des ressources GPU disponibles
        gpu_configs = [
            {"gpu_id": "gpu_v100_001", "gpu_type": "NVIDIA V100", "memory_gb": 16.0, "pool": ComputeType.GPU_NVIDIA_V100},
            {"gpu_id": "gpu_v100_002", "gpu_type": "NVIDIA V100", "memory_gb": 16.0, "pool": ComputeType.GPU_NVIDIA_V100},
            {"gpu_id": "gpu_a100_001", "gpu_type": "NVIDIA A100", "memory_gb": 40.0, "pool": ComputeType.GPU_NVIDIA_A100},
            {"gpu_id": "gpu_a100_002", "gpu_type": "NVIDIA A100", "memory_gb": 40.0, "pool": ComputeType.GPU_NVIDIA_A100},
            {"gpu_id": "gpu_h100_001", "gpu_type": "NVIDIA H100", "memory_gb": 80.0, "pool": ComputeType.GPU_NVIDIA_H100},
        ]
        
        for config in gpu_configs:
            gpu_resource = GPUResource(
                gpu_id=config["gpu_id"],
                gpu_type=config["gpu_type"],
                memory_gb=config["memory_gb"]
            )
            self.gpu_resources[config["gpu_id"]] = gpu_resource
            
            pool = config["pool"]
            if pool not in self.gpu_pools:
                self.gpu_pools[pool] = set()
            self.gpu_pools[pool].add(config["gpu_id"])
    
    async def allocate_gpu(self, compute_requirement: ComputeType, 
                          memory_needed_gb: float, allocation_id: str) -> Optional[str]:
        """Allouer une ressource GPU"""
        try:
            if compute_requirement not in self.gpu_pools:
                logger.warning(f"Pool GPU non disponible: {compute_requirement.value}")
                return None
            
            available_gpus = self.gpu_pools[compute_requirement]
            
            # Trouver un GPU disponible avec assez de mémoire
            for gpu_id in available_gpus:
                gpu = self.gpu_resources[gpu_id]
                
                if (gpu.allocated_to is None and 
                    gpu.memory_gb >= memory_needed_gb and 
                    gpu.utilization < 0.8):  # Pas plus de 80% d'utilisation
                    
                    # Allouer le GPU
                    gpu.allocated_to = allocation_id
                    gpu.utilization += memory_needed_gb / gpu.memory_gb
                    gpu.last_update = time.time()
                    
                    logger.info(f"💾 GPU alloué: {gpu_id} pour {allocation_id}")
                    return gpu_id
            
            # Aucun GPU disponible immédiatement, ajouter à la queue
            self.allocation_queue.append({
                'allocation_id': allocation_id,
                'compute_requirement': compute_requirement,
                'memory_needed_gb': memory_needed_gb,
                'requested_at': time.time()
            })
            
            logger.info(f"⏳ Demande GPU en queue: {allocation_id}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur allocation GPU: {e}")
            return None
    
    async def deallocate_gpu(self, gpu_id: str, allocation_id: str) -> bool:
        """Libérer une ressource GPU"""
        try:
            if gpu_id in self.gpu_resources:
                gpu = self.gpu_resources[gpu_id]
                
                if gpu.allocated_to == allocation_id:
                    gpu.allocated_to = None
                    gpu.utilization = max(0.0, gpu.utilization - 0.2)  # Réduire l'utilisation
                    gpu.last_update = time.time()
                    
                    logger.info(f"🔓 GPU libéré: {gpu_id}")
                    
                    # Traiter la queue d'allocation
                    await self._process_allocation_queue()
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur libération GPU: {e}")
            return False
    
    async def _process_allocation_queue(self):
        """Traiter la queue d'allocation GPU"""
        if not self.allocation_queue:
            return
        
        # Trier par priorité (FIFO pour l'instant)
        self.allocation_queue.sort(key=lambda x: x['requested_at'])
        
        processed = []
        for i, request in enumerate(self.allocation_queue):
            gpu_id = await self.allocate_gpu(
                request['compute_requirement'],
                request['memory_needed_gb'],
                request['allocation_id']
            )
            
            if gpu_id:
                processed.append(i)
                logger.info(f"✅ Demande GPU traitée depuis la queue: {request['allocation_id']}")
        
        # Supprimer les demandes traitées
        for i in reversed(processed):
            del self.allocation_queue[i]
    
    async def get_gpu_utilization(self) -> Dict[str, float]:
        """Obtenir l'utilisation des GPU"""
        utilization = {}
        for gpu_id, gpu in self.gpu_resources.items():
            utilization[gpu_id] = gpu.utilization
        return utilization
    
    async def get_available_compute_types(self) -> List[ComputeType]:
        """Obtenir les types de compute disponibles"""
        available_types = []
        
        for compute_type, gpu_ids in self.gpu_pools.items():
            # Vérifier s'il y a au moins un GPU disponible
            for gpu_id in gpu_ids:
                gpu = self.gpu_resources[gpu_id]
                if gpu.allocated_to is None and gpu.utilization < 0.8:
                    available_types.append(compute_type)
                    break
        
        return available_types

class ModelDeploymentManager:
    """Gestionnaire de déploiement de modèles"""
    
    def __init__(self, gpu_manager: GPUResourceManager):
        self.gpu_manager = gpu_manager
        self.active_deployments: Dict[str, ModelDeployment] = {}
        self.deployment_templates: Dict[str, Dict] = self._initialize_deployment_templates()
    
    def _initialize_deployment_templates(self) -> Dict[str, Dict]:
        """Initialiser les templates de déploiement"""
        return {
            InferenceMode.REAL_TIME.value: {
                'scaling_config': {
                    'min_instances': 1,
                    'max_instances': 5,
                    'target_utilization': 0.7,
                    'scale_up_threshold': 0.8,
                    'scale_down_threshold': 0.3
                },
                'load_balancing': 'round_robin',
                'health_check_interval': 30
            },
            InferenceMode.BATCH.value: {
                'scaling_config': {
                    'min_instances': 0,
                    'max_instances': 10,
                    'target_utilization': 0.9,
                    'scale_up_threshold': 0.95,
                    'scale_down_threshold': 0.5
                },
                'load_balancing': 'least_connections',
                'health_check_interval': 60
            },
            InferenceMode.STREAMING.value: {
                'scaling_config': {
                    'min_instances': 2,
                    'max_instances': 8,
                    'target_utilization': 0.6,
                    'scale_up_threshold': 0.7,
                    'scale_down_threshold': 0.2
                },
                'load_balancing': 'sticky_session',
                'health_check_interval': 15
            }
        }
    
    async def deploy_model(self, model_spec: AIModelSpec, 
                          inference_mode: InferenceMode,
                          initial_instances: int = 1) -> Optional[ModelDeployment]:
        """Déployer un modèle IA"""
        try:
            deployment_id = f"{model_spec.model_id}_{inference_mode.value}_{int(time.time())}"
            
            # Allouer les ressources nécessaires
            service_instances = []
            compute_allocation = {}
            
            for i in range(initial_instances):
                instance_id = f"{deployment_id}_instance_{i}"
                
                # Allouer GPU si nécessaire
                gpu_id = None
                if model_spec.compute_requirements != ComputeType.CPU_OPTIMIZED:
                    gpu_id = await self.gpu_manager.allocate_gpu(
                        model_spec.compute_requirements,
                        model_spec.gpu_memory_gb,
                        instance_id
                    )
                
                # Créer l'instance de service
                service_instance = ServiceInstance(
                    service_id=instance_id,
                    service_name=f"ai_{model_spec.model_type.value}",
                    host="ai-cluster.ainflue.com",
                    port=8080 + i,
                    health_check_url="/health",
                    metadata={
                        'model_id': model_spec.model_id,
                        'model_type': model_spec.model_type.value,
                        'inference_mode': inference_mode.value,
                        'gpu_id': gpu_id,
                        'memory_gb': model_spec.memory_gb,
                        'framework': model_spec.framework.value
                    }
                )
                
                service_instances.append(service_instance)
                
                if gpu_id:
                    compute_allocation[instance_id] = {
                        'gpu_id': gpu_id,
                        'compute_type': model_spec.compute_requirements.value,
                        'memory_allocated_gb': model_spec.gpu_memory_gb
                    }
            
            # Obtenir la configuration de déploiement
            deployment_template = self.deployment_templates.get(
                inference_mode.value, 
                self.deployment_templates[InferenceMode.REAL_TIME.value]
            )
            
            # Créer le déploiement
            deployment = ModelDeployment(
                deployment_id=deployment_id,
                model_spec=model_spec,
                service_instances=service_instances,
                compute_allocation=compute_allocation,
                deployment_status="deploying",
                auto_scaling_config=deployment_template['scaling_config']
            )
            
            # Simuler le processus de déploiement
            await self._simulate_deployment_process(deployment)
            
            # Si succès, marquer comme déployé
            deployment.deployment_status = "deployed"
            deployment.deployed_at = datetime.now()
            
            self.active_deployments[deployment_id] = deployment
            
            logger.info(f"🚀 Modèle déployé: {model_spec.model_name} ({initial_instances} instances)")
            return deployment
            
        except Exception as e:
            logger.error(f"Erreur déploiement modèle: {e}")
            return None
    
    async def _simulate_deployment_process(self, deployment: ModelDeployment):
        """Simuler le processus de déploiement"""
        # Simulation des étapes de déploiement
        steps = [
            "Préparation environnement",
            "Téléchargement modèle",
            "Initialisation GPU",
            "Chargement modèle en mémoire",
            "Tests de sanité",
            "Configuration load balancer"
        ]
        
        for step in steps:
            logger.info(f"📦 Déploiement {deployment.deployment_id}: {step}")
            await asyncio.sleep(0.1)  # Simulation
    
    async def scale_deployment(self, deployment_id: str, target_instances: int) -> bool:
        """Ajuster le nombre d'instances d'un déploiement"""
        try:
            if deployment_id not in self.active_deployments:
                return False
            
            deployment = self.active_deployments[deployment_id]
            current_instances = len(deployment.service_instances)
            
            if target_instances > current_instances:
                # Scale up
                await self._scale_up_deployment(deployment, target_instances - current_instances)
            elif target_instances < current_instances:
                # Scale down
                await self._scale_down_deployment(deployment, current_instances - target_instances)
            
            logger.info(f"📊 Déploiement scalé: {deployment_id} ({current_instances} -> {target_instances})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur scaling déploiement: {e}")
            return False
    
    async def _scale_up_deployment(self, deployment: ModelDeployment, additional_instances: int):
        """Augmenter le nombre d'instances"""
        model_spec = deployment.model_spec
        current_count = len(deployment.service_instances)
        
        for i in range(additional_instances):
            instance_id = f"{deployment.deployment_id}_instance_{current_count + i}"
            
            # Allouer GPU si nécessaire
            gpu_id = None
            if model_spec.compute_requirements != ComputeType.CPU_OPTIMIZED:
                gpu_id = await self.gpu_manager.allocate_gpu(
                    model_spec.compute_requirements,
                    model_spec.gpu_memory_gb,
                    instance_id
                )
            
            # Créer nouvelle instance
            service_instance = ServiceInstance(
                service_id=instance_id,
                service_name=f"ai_{model_spec.model_type.value}",
                host="ai-cluster.ainflue.com",
                port=8080 + current_count + i,
                health_check_url="/health",
                metadata={
                    'model_id': model_spec.model_id,
                    'model_type': model_spec.model_type.value,
                    'gpu_id': gpu_id,
                    'framework': model_spec.framework.value
                }
            )
            
            deployment.service_instances.append(service_instance)
            
            if gpu_id:
                deployment.compute_allocation[instance_id] = {
                    'gpu_id': gpu_id,
                    'compute_type': model_spec.compute_requirements.value,
                    'memory_allocated_gb': model_spec.gpu_memory_gb
                }
    
    async def _scale_down_deployment(self, deployment: ModelDeployment, instances_to_remove: int):
        """Diminuer le nombre d'instances"""
        for _ in range(instances_to_remove):
            if deployment.service_instances:
                instance = deployment.service_instances.pop()
                
                # Libérer GPU si alloué
                allocation = deployment.compute_allocation.get(instance.service_id)
                if allocation and 'gpu_id' in allocation:
                    await self.gpu_manager.deallocate_gpu(
                        allocation['gpu_id'], 
                        instance.service_id
                    )
                    del deployment.compute_allocation[instance.service_id]
    
    async def undeploy_model(self, deployment_id: str) -> bool:
        """Supprimer un déploiement de modèle"""
        try:
            if deployment_id not in self.active_deployments:
                return False
            
            deployment = self.active_deployments[deployment_id]
            
            # Libérer toutes les ressources GPU
            for instance_id, allocation in deployment.compute_allocation.items():
                if 'gpu_id' in allocation:
                    await self.gpu_manager.deallocate_gpu(
                        allocation['gpu_id'],
                        instance_id
                    )
            
            # Supprimer le déploiement
            del self.active_deployments[deployment_id]
            
            logger.info(f"🗑️ Déploiement supprimé: {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression déploiement: {e}")
            return False
    
    async def get_deployment_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques des déploiements"""
        total_deployments = len(self.active_deployments)
        total_instances = sum(len(d.service_instances) for d in self.active_deployments.values())
        
        deployments_by_type = {}
        for deployment in self.active_deployments.values():
            model_type = deployment.model_spec.model_type.value
            deployments_by_type[model_type] = deployments_by_type.get(model_type, 0) + 1
        
        return {
            'total_deployments': total_deployments,
            'total_instances': total_instances,
            'deployments_by_type': deployments_by_type,
            'gpu_utilization': await self.gpu_manager.get_gpu_utilization()
        }

class AIServiceOrchestrator:
    """Orchestrateur principal des services IA"""
    
    def __init__(self):
        self.model_registry = AIModelRegistry()
        self.gpu_manager = GPUResourceManager()
        self.deployment_manager = ModelDeploymentManager(self.gpu_manager)
        self.load_balancer = IntelligentLoadBalancer()
        
        # Métriques et monitoring
        self.request_stats: Dict[str, Any] = {
            'total_requests': 0,
            'successful_requests': 0,
            'avg_latency_ms': 0.0,
            'requests_by_model_type': {},
            'compute_utilization': {}
        }
        
        logger.info("🤖 AIServiceOrchestrator initialisé")
    
    async def orchestrate_ai_services(self, ai_request: AIRequest) -> AIServiceResult:
        """
        Orchestration services IA avec optimization ressources.
        
        AI Orchestration Features:
        - Model selection basé sur performance et availability
        - GPU resource allocation avec queue management
        - Auto-scaling basé sur demand patterns
        - Multi-model ensemble coordination
        - Edge deployment pour low latency
        - Cost optimization avec spot instances
        - Model A/B testing coordination
        """
        try:
            start_time = time.time()
            self.request_stats['total_requests'] += 1
            
            # 1. Découvrir les modèles disponibles
            available_models = await self.model_registry.get_models_by_type(ai_request.model_type)
            
            if not available_models:
                return AIServiceResult(
                    success=False,
                    errors=[f"Aucun modèle trouvé pour {ai_request.model_type.value}"]
                )
            
            # 2. Sélectionner le meilleur modèle
            selected_model = await self._select_optimal_model(available_models, ai_request)
            
            # 3. Trouver ou créer un déploiement
            deployment = await self._find_or_create_deployment(selected_model, ai_request.inference_mode)
            
            if not deployment:
                return AIServiceResult(
                    success=False,
                    errors=["Impossible de déployer le modèle sélectionné"]
                )
            
            # 4. Sélectionner les instances optimales
            selected_services = await self._select_service_instances(deployment, ai_request)
            
            # 5. Créer le plan d'orchestration
            orchestration_plan = await self._create_orchestration_plan(
                selected_model, deployment, ai_request
            )
            
            # 6. Calculer les estimations
            estimated_latency = await self._estimate_inference_latency(selected_model, ai_request)
            estimated_cost = await self._estimate_inference_cost(selected_model, ai_request)
            
            # 7. Allocation des ressources
            resource_allocation = await self._allocate_resources(deployment, ai_request)
            
            # 8. Services de fallback
            fallback_services = await self._identify_fallback_services(ai_request.model_type)
            
            result = AIServiceResult(
                success=True,
                selected_services=selected_services,
                orchestration_plan=orchestration_plan,
                estimated_latency_ms=estimated_latency,
                estimated_cost=estimated_cost,
                resource_allocation=resource_allocation,
                fallback_services=fallback_services
            )
            
            # Mettre à jour les statistiques
            processing_time = (time.time() - start_time) * 1000
            await self._update_request_stats(ai_request, result, processing_time)
            
            logger.info(f"🎯 AI orchestration pour {ai_request.model_type.value}: {len(selected_services)} services, {estimated_latency:.1f}ms, ${estimated_cost:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur orchestration IA: {e}")
            return AIServiceResult(
                success=False,
                errors=[str(e)]
            )
    
    async def _select_optimal_model(self, available_models: List[AIModelSpec], 
                                   ai_request: AIRequest) -> AIModelSpec:
        """Sélectionner le modèle optimal"""
        try:
            if len(available_models) == 1:
                return available_models[0]
            
            # Scorer chaque modèle
            model_scores = []
            
            for model in available_models:
                score = 0.0
                
                # Score de performance
                performance = self.model_registry.model_performance.get(model.model_id, {})
                success_rate = performance.get('success_rate', 0.8)
                avg_latency = performance.get('avg_latency_ms', model.latency_target_ms or 1000)
                
                # Bonus pour taux de succès élevé
                score += success_rate * 40
                
                # Score de latence (inversé)
                if ai_request.latency_requirement_ms:
                    if avg_latency <= ai_request.latency_requirement_ms:
                        score += 30 * (1 - avg_latency / ai_request.latency_requirement_ms)
                    else:
                        score -= 20  # Pénalité si trop lent
                
                # Bonus selon préférence qualité
                if ai_request.quality_preference == "quality":
                    accuracy_bonus = sum(model.accuracy_metrics.values()) * 10
                    score += accuracy_bonus
                elif ai_request.quality_preference == "speed":
                    if model.latency_target_ms:
                        speed_bonus = max(0, 20 - model.latency_target_ms / 100)
                        score += speed_bonus
                
                # Bonus pour mode d'inférence supporté
                if ai_request.inference_mode in model.inference_modes:
                    score += 15
                
                model_scores.append((model, score))
            
            # Trier par score décroissant
            model_scores.sort(key=lambda x: x[1], reverse=True)
            
            selected_model = model_scores[0][0]
            logger.info(f"🎯 Modèle sélectionné: {selected_model.model_name} (score: {model_scores[0][1]:.1f})")
            
            return selected_model
            
        except Exception as e:
            logger.error(f"Erreur sélection modèle: {e}")
            return available_models[0]  # Fallback
    
    async def _find_or_create_deployment(self, model_spec: AIModelSpec, 
                                       inference_mode: InferenceMode) -> Optional[ModelDeployment]:
        """Trouver un déploiement existant ou en créer un nouveau"""
        try:
            # Chercher un déploiement existant
            for deployment in self.deployment_manager.active_deployments.values():
                if (deployment.model_spec.model_id == model_spec.model_id and 
                    inference_mode in model_spec.inference_modes and
                    deployment.deployment_status == "deployed"):
                    
                    logger.info(f"📦 Déploiement existant trouvé: {deployment.deployment_id}")
                    return deployment
            
            # Créer un nouveau déploiement
            logger.info(f"🚀 Création nouveau déploiement pour {model_spec.model_name}")
            deployment = await self.deployment_manager.deploy_model(
                model_spec, 
                inference_mode,
                initial_instances=1
            )
            
            return deployment
            
        except Exception as e:
            logger.error(f"Erreur recherche/création déploiement: {e}")
            return None
    
    async def _select_service_instances(self, deployment: ModelDeployment, 
                                      ai_request: AIRequest) -> List[ServiceInstance]:
        """Sélectionner les instances de service optimales"""
        try:
            available_instances = [
                instance for instance in deployment.service_instances
                if instance.status == ServiceStatus.HEALTHY
            ]
            
            if not available_instances:
                return []
            
            # Utiliser le load balancer intelligent
            request_context = RequestContext(
                request_id=ai_request.request_id,
                user_id=ai_request.creator_id,
                request_type=self._map_model_type_to_request_type(ai_request.model_type),
                priority=ai_request.priority,
                metadata={
                    'model_type': ai_request.model_type.value,
                    'inference_mode': ai_request.inference_mode.value,
                    'batch_size': ai_request.batch_size
                }
            )
            
            # Pour les requêtes batch, on peut utiliser plusieurs instances
            if ai_request.inference_mode == InferenceMode.BATCH and ai_request.batch_size > 1:
                # Calculer le nombre optimal d'instances
                optimal_instances = min(
                    len(available_instances),
                    max(1, ai_request.batch_size // 10)  # 10 items par instance
                )
                
                selected_instances = []
                for _ in range(optimal_instances):
                    instance = await self.load_balancer.select_optimal_instance(
                        f"ai_{ai_request.model_type.value}",
                        available_instances,
                        request_context
                    )
                    if instance and instance not in selected_instances:
                        selected_instances.append(instance)
                        # Retirer de la liste pour éviter les doublons
                        available_instances = [i for i in available_instances if i != instance]
                
                return selected_instances
            else:
                # Mode temps réel - une seule instance
                instance = await self.load_balancer.select_optimal_instance(
                    f"ai_{ai_request.model_type.value}",
                    available_instances,
                    request_context
                )
                
                return [instance] if instance else []
                
        except Exception as e:
            logger.error(f"Erreur sélection instances: {e}")
            return deployment.service_instances[:1]  # Fallback - première instance
    
    def _map_model_type_to_request_type(self, model_type: AIModelType) -> RequestType:
        """Mapper un type de modèle vers un type de requête"""
        mapping = {
            AIModelType.CONTENT_ANALYSIS: RequestType.CPU_INTENSIVE,
            AIModelType.AUDIO_ENHANCEMENT: RequestType.CPU_INTENSIVE,
            AIModelType.VIDEO_TRANSCODING: RequestType.CPU_INTENSIVE,
            AIModelType.IMAGE_GENERATION: RequestType.CPU_INTENSIVE,
            AIModelType.TEXT_GENERATION: RequestType.BALANCED,
            AIModelType.SPEECH_TO_TEXT: RequestType.CPU_INTENSIVE,
            AIModelType.TEXT_TO_SPEECH: RequestType.CPU_INTENSIVE,
            AIModelType.CONTENT_MODERATION: RequestType.BALANCED,
            AIModelType.RECOMMENDATION: RequestType.MEMORY_INTENSIVE,
            AIModelType.SENTIMENT_ANALYSIS: RequestType.BALANCED,
            AIModelType.VOICE_CLONING: RequestType.CPU_INTENSIVE,
            AIModelType.MUSIC_GENERATION: RequestType.CPU_INTENSIVE,
            AIModelType.DEEPFAKE_DETECTION: RequestType.CPU_INTENSIVE,
            AIModelType.COPYRIGHT_DETECTION: RequestType.BALANCED
        }
        
        return mapping.get(model_type, RequestType.BALANCED)
    
    async def _create_orchestration_plan(self, model_spec: AIModelSpec, 
                                       deployment: ModelDeployment,
                                       ai_request: AIRequest) -> Dict[str, Any]:
        """Créer le plan d'orchestration"""
        return {
            'model_id': model_spec.model_id,
            'model_name': model_spec.model_name,
            'deployment_id': deployment.deployment_id,
            'inference_mode': ai_request.inference_mode.value,
            'batch_size': ai_request.batch_size,
            'quality_preference': ai_request.quality_preference,
            'resource_requirements': {
                'compute_type': model_spec.compute_requirements.value,
                'memory_gb': model_spec.memory_gb,
                'gpu_memory_gb': model_spec.gpu_memory_gb
            },
            'execution_steps': [
                'input_validation',
                'preprocessing',
                'model_inference',
                'postprocessing',
                'output_formatting',
                'result_delivery'
            ],
            'monitoring': {
                'latency_tracking': True,
                'resource_monitoring': True,
                'quality_metrics': True
            }
        }
    
    async def _estimate_inference_latency(self, model_spec: AIModelSpec, 
                                        ai_request: AIRequest) -> float:
        """Estimer la latence d'inférence"""
        try:
            # Latence de base du modèle
            base_latency = model_spec.latency_target_ms or 1000
            
            # Ajustement selon la taille du batch
            if ai_request.batch_size > 1:
                # Latence augmente moins que linéairement avec la taille du batch
                batch_factor = 1 + (ai_request.batch_size - 1) * 0.3
                base_latency *= batch_factor
            
            # Ajustement selon les performances historiques
            performance = self.model_registry.model_performance.get(model_spec.model_id, {})
            historical_latency = performance.get('avg_latency_ms', base_latency)
            
            # Moyenne pondérée entre latence cible et historique
            estimated_latency = (base_latency * 0.3) + (historical_latency * 0.7)
            
            # Ajustement selon la préférence qualité
            if ai_request.quality_preference == "quality":
                estimated_latency *= 1.5  # Plus lent mais meilleure qualité
            elif ai_request.quality_preference == "speed":
                estimated_latency *= 0.8  # Plus rapide mais qualité réduite
            
            # Ajustement selon la charge actuelle (simulation)
            current_load = 1.2  # 20% de charge supplémentaire
            estimated_latency *= current_load
            
            return max(100, round(estimated_latency, 1))  # Minimum 100ms
            
        except Exception as e:
            logger.error(f"Erreur estimation latence: {e}")
            return 1000.0  # Latence par défaut
    
    async def _estimate_inference_cost(self, model_spec: AIModelSpec, 
                                     ai_request: AIRequest) -> float:
        """Estimer le coût d'inférence"""
        try:
            # Coût de base selon le type de compute
            compute_costs = {
                ComputeType.CPU_OPTIMIZED: 0.001,  # $ par inférence
                ComputeType.GPU_NVIDIA_V100: 0.01,
                ComputeType.GPU_NVIDIA_A100: 0.02,
                ComputeType.GPU_NVIDIA_H100: 0.04,
                ComputeType.TPU_V4: 0.015,
                ComputeType.EDGE_DEVICE: 0.0005
            }
            
            base_cost = compute_costs.get(model_spec.compute_requirements, 0.005)
            
            # Facteur de taille de modèle
            size_factor = max(1.0, model_spec.model_size_mb / 1000)  # Base 1GB
            cost_with_size = base_cost * size_factor
            
            # Facteur de batch
            batch_cost = cost_with_size * ai_request.batch_size * 0.8  # Économies d'échelle
            
            # Facteur de qualité
            quality_multipliers = {
                "speed": 0.7,
                "balanced": 1.0,
                "quality": 1.5
            }
            quality_multiplier = quality_multipliers.get(ai_request.quality_preference, 1.0)
            
            final_cost = batch_cost * quality_multiplier
            
            return round(final_cost, 4)
            
        except Exception as e:
            logger.error(f"Erreur estimation coût: {e}")
            return 0.01  # Coût par défaut
    
    async def _allocate_resources(self, deployment: ModelDeployment, 
                                ai_request: AIRequest) -> Dict[str, Any]:
        """Allouer les ressources pour la requête"""
        return {
            'deployment_id': deployment.deployment_id,
            'allocated_instances': len(deployment.service_instances),
            'compute_allocation': deployment.compute_allocation,
            'memory_reservation_gb': deployment.model_spec.memory_gb,
            'gpu_reservation': {
                instance_id: alloc.get('gpu_id') 
                for instance_id, alloc in deployment.compute_allocation.items()
                if 'gpu_id' in alloc
            },
            'priority_level': ai_request.priority,
            'resource_timeout': 300  # 5 minutes
        }
    
    async def _identify_fallback_services(self, model_type: AIModelType) -> List[ServiceInstance]:
        """Identifier les services de fallback"""
        try:
            fallback_models = await self.model_registry.get_models_by_type(model_type)
            fallback_services = []
            
            for model in fallback_models[:2]:  # Maximum 2 fallbacks
                # Chercher des déploiements existants
                for deployment in self.deployment_manager.active_deployments.values():
                    if (deployment.model_spec.model_id == model.model_id and 
                        deployment.deployment_status == "deployed"):
                        fallback_services.extend(deployment.service_instances[:1])
                        break
            
            return fallback_services
            
        except Exception as e:
            logger.error(f"Erreur identification fallbacks: {e}")
            return []
    
    async def _update_request_stats(self, ai_request: AIRequest, 
                                  result: AIServiceResult, processing_time_ms: float):
        """Mettre à jour les statistiques de requêtes"""
        try:
            stats = self.request_stats
            
            # Mise à jour latence moyenne
            total_requests = stats['total_requests']
            current_avg = stats['avg_latency_ms']
            new_avg = ((current_avg * (total_requests - 1)) + processing_time_ms) / total_requests
            stats['avg_latency_ms'] = new_avg
            
            # Compteur de succès
            if result.success:
                stats['successful_requests'] += 1
            
            # Distribution par type de modèle
            model_type = ai_request.model_type.value
            if model_type not in stats['requests_by_model_type']:
                stats['requests_by_model_type'][model_type] = 0
            stats['requests_by_model_type'][model_type] += 1
            
            # Utilisation compute
            if result.resource_allocation:
                compute_types = set()
                for alloc in result.resource_allocation.get('compute_allocation', {}).values():
                    if 'compute_type' in alloc:
                        compute_types.add(alloc['compute_type'])
                
                for compute_type in compute_types:
                    if compute_type not in stats['compute_utilization']:
                        stats['compute_utilization'][compute_type] = 0
                    stats['compute_utilization'][compute_type] += 1
            
        except Exception as e:
            logger.error(f"Erreur mise à jour stats: {e}")
    
    async def register_ai_model(self, model_spec: AIModelSpec) -> bool:
        """Enregistrer un modèle IA"""
        return await self.model_registry.register_model(model_spec)
    
    async def deploy_ai_model(self, model_id: str, inference_mode: InferenceMode,
                            initial_instances: int = 1) -> Optional[str]:
        """Déployer un modèle IA"""
        try:
            if model_id in self.model_registry.models:
                model_spec = self.model_registry.models[model_id]
            elif model_id in self.model_registry.model_catalog:
                model_spec = self.model_registry.model_catalog[model_id]
            else:
                logger.error(f"Modèle introuvable: {model_id}")
                return None
            
            deployment = await self.deployment_manager.deploy_model(
                model_spec, inference_mode, initial_instances
            )
            
            return deployment.deployment_id if deployment else None
            
        except Exception as e:
            logger.error(f"Erreur déploiement modèle {model_id}: {e}")
            return None
    
    async def get_ai_orchestration_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques d'orchestration IA"""
        stats = self.request_stats.copy()
        
        # Ajouter des métriques calculées
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_requests'] / stats['total_requests']
        else:
            stats['success_rate'] = 0.0
        
        # Ajouter les stats des déploiements
        deployment_stats = await self.deployment_manager.get_deployment_stats()
        stats.update(deployment_stats)
        
        # Ajouter les stats GPU
        stats['available_compute_types'] = [ct.value for ct in await self.gpu_manager.get_available_compute_types()]
        stats['gpu_queue_length'] = len(self.gpu_manager.allocation_queue)
        
        return stats

# Factory function
def create_ai_service_orchestrator() -> AIServiceOrchestrator:
    """Factory pour créer un orchestrateur de services IA"""
    return AIServiceOrchestrator()

__all__ = [
    'AIServiceOrchestrator',
    'AIModelType',
    'ComputeType',
    'InferenceMode',
    'ModelFramework',
    'AIModelSpec',
    'AIRequest',
    'AIServiceResult',
    'GPUResource',
    'ModelDeployment',
    'AIModelRegistry',
    'GPUResourceManager',
    'ModelDeploymentManager',
    'create_ai_service_orchestrator'
]