"""
Image Fingerprinting Deployment System
Enterprise image content protection deployment infrastructure

This module provides deployment infrastructure for image fingerprinting
services using CLIP, ImageHash, and perceptual hashing technologies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without written permission
will result in legal action under German and international copyright law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import yaml
import kubernetes
from kubernetes import client, config
import docker
import redis
from datetime import datetime, timedelta
import json
import base64
import hashlib

logger = logging.getLogger(__name__)


class ImageHashingAlgorithm(Enum):
    """Image hashing algorithms"""
    PERCEPTUAL = "perceptual"
    AVERAGE = "average"
    DIFFERENCE = "difference"
    WAVELET = "wavelet"
    COLOR_MOMENT = "color_moment"
    CLIP_EMBEDDING = "clip_embedding"
    DEEP_HASH = "deep_hash"


class SimilarityMetric(Enum):
    """Similarity calculation metrics"""
    HAMMING_DISTANCE = "hamming_distance"
    COSINE_SIMILARITY = "cosine_similarity"
    EUCLIDEAN_DISTANCE = "euclidean_distance"
    STRUCTURAL_SIMILARITY = "structural_similarity"
    FEATURE_MATCHING = "feature_matching"


class ProcessingPipeline(Enum):
    """Image processing pipelines"""
    REAL_TIME = "real_time"
    BATCH_PROCESSING = "batch_processing"
    STREAMING = "streaming"
    HIGH_ACCURACY = "high_accuracy"
    FAST_DETECTION = "fast_detection"


@dataclass
class ImageFingerprintConfig:
    """Image fingerprinting deployment configuration"""
    deployment_name: str
    namespace: str = "ia-influencer-protection"
    algorithms: List[ImageHashingAlgorithm] = None
    similarity_metrics: List[SimilarityMetric] = None
    processing_pipeline: ProcessingPipeline = ProcessingPipeline.REAL_TIME
    similarity_threshold: float = 0.85
    batch_size: int = 32
    max_image_size_mb: int = 50
    supported_formats: List[str] = None
    gpu_acceleration: bool = True
    clip_model: str = "ViT-B/32"
    vector_dimension: int = 512
    replicas: int = 3
    min_replicas: int = 2
    max_replicas: int = 20
    cpu_request: str = "1000m"
    memory_request: str = "2Gi"
    cpu_limit: str = "4000m"
    memory_limit: str = "8Gi"
    storage_size: str = "100Gi"
    persistence_enabled: bool = True
    monitoring_enabled: bool = True
    
    def __post_init__(self):
        if self.algorithms is None:
            self.algorithms = [
                ImageHashingAlgorithm.PERCEPTUAL,
                ImageHashingAlgorithm.CLIP_EMBEDDING,
                ImageHashingAlgorithm.DEEP_HASH
            ]
        if self.similarity_metrics is None:
            self.similarity_metrics = [
                SimilarityMetric.COSINE_SIMILARITY,
                SimilarityMetric.HAMMING_DISTANCE
            ]
        if self.supported_formats is None:
            self.supported_formats = ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"]


class ImageFingerprintDeployment:
    """
    Enterprise image fingerprinting deployment system
    
    Deploys and manages image content protection infrastructure:
    - CLIP-based deep learning embeddings
    - Perceptual and traditional hashing
    - Real-time similarity detection
    - Vector database for fast matching
    - Auto-scaling and load balancing
    - Comprehensive monitoring and metrics
    """
    
    def __init__(self, config: ImageFingerprintConfig):
        """
        Initialize image fingerprinting deployment
        
        Args:
            config: Deployment configuration
        """
        self.config = config
        self.deployment_status = "initializing"
        self.services_deployed = {}
        self.vector_db_ready = False
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Kubernetes, Docker, and Redis clients"""
        try:
            # Kubernetes client
            config.load_incluster_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_autoscaling_v2 = client.AutoscalingV2Api()
            self.k8s_networking_v1 = client.NetworkingV1Api()
            self.k8s_storage_v1 = client.StorageV1Api()
            
            # Docker client for image builds
            self._docker_client = docker.from_env()
            
            # Redis for fingerprint caching
            self._redis_client = redis.Redis(
                host='image-fingerprint-redis',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            logger.info("Image fingerprinting clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize image fingerprinting clients: {e}")
            raise
    
    async def deploy_image_fingerprinting_infrastructure(self) -> Dict[str, Any]:
        """
        Deploy complete image fingerprinting infrastructure
        
        Returns:
            Infrastructure deployment summary
        """
        try:
            self.deployment_status = "deploying_infrastructure"
            logger.info("Deploying image fingerprinting infrastructure")
            
            # Create namespace
            await self._ensure_namespace()
            
            # Deploy storage infrastructure
            storage_result = await self._deploy_storage_infrastructure()
            
            # Deploy vector database (FAISS)
            vector_db_result = await self._deploy_vector_database()
            
            # Deploy Redis for caching
            redis_result = await self._deploy_fingerprint_cache()
            
            # Deploy image processing services
            clip_service_result = await self._deploy_clip_service()
            hash_service_result = await self._deploy_traditional_hash_service()
            similarity_service_result = await self._deploy_similarity_service()
            
            # Deploy processing pipeline
            pipeline_result = await self._deploy_processing_pipeline()
            
            # Deploy API gateway
            api_gateway_result = await self._deploy_api_gateway()
            
            # Deploy monitoring and metrics
            monitoring_result = await self._deploy_monitoring_stack()
            
            # Configure networking and security
            await self._configure_networking()
            
            # Validate deployment
            if await self._validate_deployment():
                self.deployment_status = "deployed"
                logger.info("Image fingerprinting infrastructure deployed successfully")
                
                return {
                    "status": "success",
                    "deployment_name": self.config.deployment_name,
                    "namespace": self.config.namespace,
                    "services": {
                        "storage": storage_result,
                        "vector_database": vector_db_result,
                        "redis_cache": redis_result,
                        "clip_service": clip_service_result,
                        "hash_service": hash_service_result,
                        "similarity_service": similarity_service_result,
                        "processing_pipeline": pipeline_result,
                        "api_gateway": api_gateway_result,
                        "monitoring": monitoring_result
                    },
                    "capabilities": {
                        "algorithms": [alg.value for alg in self.config.algorithms],
                        "similarity_metrics": [met.value for met in self.config.similarity_metrics],
                        "supported_formats": self.config.supported_formats,
                        "processing_pipeline": self.config.processing_pipeline.value,
                        "gpu_acceleration": self.config.gpu_acceleration,
                        "similarity_threshold": self.config.similarity_threshold
                    },
                    "endpoints": {
                        "fingerprint_api": f"http://image-fingerprint-api.{self.config.namespace}.svc.cluster.local",
                        "similarity_api": f"http://image-similarity-api.{self.config.namespace}.svc.cluster.local",
                        "monitoring": f"http://image-fingerprint-monitor.{self.config.namespace}.svc.cluster.local"
                    }
                }
            else:
                raise Exception("Image fingerprinting infrastructure validation failed")
                
        except Exception as e:
            self.deployment_status = "deployment_failed"
            logger.error(f"Image fingerprinting infrastructure deployment failed: {e}")
            await self._cleanup_failed_deployment()
            raise
    
    async def _ensure_namespace(self) -> None:
        """Create namespace if it doesn't exist"""
        try:
            self.k8s_core_v1.read_namespace(name=self.config.namespace)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                namespace_body = client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name=self.config.namespace,
                        labels={
                            "name": self.config.namespace,
                            "purpose": "image-fingerprinting",
                            "protection-type": "content",
                            "ai-powered": "true"
                        }
                    )
                )
                self.k8s_core_v1.create_namespace(body=namespace_body)
                logger.info(f"Created namespace: {self.config.namespace}")
    
    async def _deploy_storage_infrastructure(self) -> Dict[str, Any]:
        """Deploy storage infrastructure for image fingerprints"""
        # Create persistent volume claim for image storage
        pvc_spec = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": "image-fingerprint-storage",
                "namespace": self.config.namespace,
                "labels": {"app": "image-fingerprinting", "component": "storage"}
            },
            "spec": {
                "accessModes": ["ReadWriteMany"],
                "resources": {"requests": {"storage": self.config.storage_size}},
                "storageClassName": "fast-ssd"
            }
        }
        
        pvc = self.k8s_core_v1.create_namespaced_persistent_volume_claim(
            namespace=self.config.namespace,
            body=pvc_spec
        )
        
        # Deploy MinIO for object storage
        minio_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "image-storage-minio",
                "namespace": self.config.namespace,
                "labels": {"app": "image-storage", "component": "object-storage"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "image-storage"}},
                "template": {
                    "metadata": {"labels": {"app": "image-storage"}},
                    "spec": {
                        "containers": [{
                            "name": "minio",
                            "image": "minio/minio:RELEASE.2024-01-16T16-07-38Z",
                            "args": ["server", "/data", "--console-address", ":9001"],
                            "ports": [
                                {"containerPort": 9000, "name": "api"},
                                {"containerPort": 9001, "name": "console"}
                            ],
                            "env": [
                                {"name": "MINIO_ACCESS_KEY", "value": "ia-influencer-storage"},
                                {"name": "MINIO_SECRET_KEY", "value": "super-secure-storage-key"}
                            ],
                            "volumeMounts": [{
                                "name": "storage",
                                "mountPath": "/data"
                            }],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "1Gi"},
                                "limits": {"cpu": "2000m", "memory": "4Gi"}
                            }
                        }],
                        "volumes": [{
                            "name": "storage",
                            "persistentVolumeClaim": {"claimName": "image-fingerprint-storage"}
                        }]
                    }
                }
            }
        }
        
        minio_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=minio_deployment
        )
        
        # Create service for MinIO
        minio_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "image-storage-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "image-storage"},
                "ports": [
                    {"port": 9000, "targetPort": 9000, "name": "api"},
                    {"port": 9001, "targetPort": 9001, "name": "console"}
                ]
            }
        }
        
        minio_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=minio_service
        )
        
        return {
            "pvc_id": pvc.metadata.uid,
            "deployment_id": minio_deploy.metadata.uid,
            "service_id": minio_svc.metadata.uid,
            "storage_size": self.config.storage_size,
            "features": ["persistent_volume", "object_storage", "high_availability"]
        }
    
    async def _deploy_vector_database(self) -> Dict[str, Any]:
        """Deploy FAISS vector database for similarity search"""
        faiss_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "image-vector-db",
                "namespace": self.config.namespace,
                "labels": {"app": "image-vector-db", "component": "vector-search"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "image-vector-db"}},
                "template": {
                    "metadata": {"labels": {"app": "image-vector-db"}},
                    "spec": {
                        "containers": [{
                            "name": "faiss-server",
                            "image": "ia-influencer/faiss-server:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "INDEX_TYPE", "value": "IVFFlat"},
                                {"name": "VECTOR_DIMENSION", "value": str(self.config.vector_dimension)},
                                {"name": "SIMILARITY_METRIC", "value": "L2"},
                                {"name": "NLIST", "value": "100"},
                                {"name": "MEMORY_MAPPING", "value": "true"},
                                {"name": "GPU_ENABLED", "value": str(self.config.gpu_acceleration).lower()}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "2000m",
                                    "memory": "8Gi"
                                },
                                "limits": {
                                    "cpu": "8000m",
                                    "memory": "32Gi"
                                }
                            },
                            "volumeMounts": [{
                                "name": "vector-storage",
                                "mountPath": "/data/vectors"
                            }]
                        }],
                        "volumes": [{
                            "name": "vector-storage",
                            "persistentVolumeClaim": {"claimName": "image-fingerprint-storage"}
                        }]
                    }
                }
            }
        }
        
        # Add GPU resources if enabled
        if self.config.gpu_acceleration:
            container = faiss_deployment["spec"]["template"]["spec"]["containers"][0]
            container["resources"]["requests"]["nvidia.com/gpu"] = "1"
            container["resources"]["limits"]["nvidia.com/gpu"] = "2"
        
        faiss_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=faiss_deployment
        )
        
        # Create service for vector database
        faiss_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "image-vector-db-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "image-vector-db"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        faiss_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=faiss_service
        )
        
        self.vector_db_ready = True
        
        return {
            "deployment_id": faiss_deploy.metadata.uid,
            "service_id": faiss_svc.metadata.uid,
            "vector_dimension": self.config.vector_dimension,
            "gpu_acceleration": self.config.gpu_acceleration,
            "features": ["similarity_search", "vector_indexing", "fast_retrieval"]
        }
    
    async def _deploy_fingerprint_cache(self) -> Dict[str, Any]:
        """Deploy Redis for fingerprint caching"""
        redis_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "image-fingerprint-redis",
                "namespace": self.config.namespace,
                "labels": {"app": "image-fingerprint-redis", "component": "cache"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "image-fingerprint-redis"}},
                "template": {
                    "metadata": {"labels": {"app": "image-fingerprint-redis"}},
                    "spec": {
                        "containers": [{
                            "name": "redis",
                            "image": "redis:7-alpine",
                            "args": [
                                "redis-server",
                                "--maxmemory", "8gb",
                                "--maxmemory-policy", "allkeys-lru",
                                "--tcp-keepalive", "60",
                                "--timeout", "300"
                            ],
                            "ports": [{"containerPort": 6379}],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "4Gi"},
                                "limits": {"cpu": "2000m", "memory": "8Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        redis_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=redis_deployment
        )
        
        # Create service for Redis
        redis_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "image-fingerprint-redis",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "image-fingerprint-redis"},
                "ports": [{"port": 6379, "targetPort": 6379}]
            }
        }
        
        redis_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=redis_service
        )
        
        return {
            "deployment_id": redis_deploy.metadata.uid,
            "service_id": redis_svc.metadata.uid,
            "memory_limit": "8Gi",
            "features": ["high_performance", "persistence", "clustering"]
        }
    
    async def _deploy_clip_service(self) -> Dict[str, Any]:
        """Deploy CLIP-based image embedding service"""
        clip_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "image-clip-service",
                "namespace": self.config.namespace,
                "labels": {"app": "image-clip-service", "component": "ai-embedding"}
            },
            "spec": {
                "replicas": self.config.replicas,
                "selector": {"matchLabels": {"app": "image-clip-service"}},
                "template": {
                    "metadata": {"labels": {"app": "image-clip-service"}},
                    "spec": {
                        "containers": [{
                            "name": "clip-embedder",
                            "image": "ia-influencer/clip-embedder:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "CLIP_MODEL", "value": self.config.clip_model},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)},
                                {"name": "MAX_IMAGE_SIZE_MB", "value": str(self.config.max_image_size_mb)},
                                {"name": "VECTOR_DIMENSION", "value": str(self.config.vector_dimension)},
                                {"name": "GPU_ENABLED", "value": str(self.config.gpu_acceleration).lower()},
                                {"name": "SUPPORTED_FORMATS", "value": ",".join(self.config.supported_formats)}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": self.config.cpu_request,
                                    "memory": self.config.memory_request
                                },
                                "limits": {
                                    "cpu": self.config.cpu_limit,
                                    "memory": self.config.memory_limit
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8080},
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        # Add GPU resources if enabled
        if self.config.gpu_acceleration:
            container = clip_deployment["spec"]["template"]["spec"]["containers"][0]
            container["resources"]["requests"]["nvidia.com/gpu"] = "1"
            container["resources"]["limits"]["nvidia.com/gpu"] = "1"
            container["env"].append({"name": "CUDA_VISIBLE_DEVICES", "value": "0"})
        
        clip_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=clip_deployment
        )
        
        # Create service for CLIP
        clip_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "image-clip-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "image-clip-service"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        clip_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=clip_service
        )
        
        # Set up auto-scaling
        if len(self.config.algorithms) > 1:
            await self._setup_autoscaling("image-clip-service")
        
        return {
            "deployment_id": clip_deploy.metadata.uid,
            "service_id": clip_svc.metadata.uid,
            "model": self.config.clip_model,
            "vector_dimension": self.config.vector_dimension,
            "gpu_acceleration": self.config.gpu_acceleration,
            "features": ["deep_learning", "semantic_understanding", "high_accuracy"]
        }
    
    async def _deploy_traditional_hash_service(self) -> Dict[str, Any]:
        """Deploy traditional image hashing service"""
        hash_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "image-hash-service",
                "namespace": self.config.namespace,
                "labels": {"app": "image-hash-service", "component": "traditional-hash"}
            },
            "spec": {
                "replicas": self.config.replicas,
                "selector": {"matchLabels": {"app": "image-hash-service"}},
                "template": {
                    "metadata": {"labels": {"app": "image-hash-service"}},
                    "spec": {
                        "containers": [{
                            "name": "image-hasher",
                            "image": "ia-influencer/image-hasher:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "HASH_ALGORITHMS", "value": ",".join([alg.value for alg in self.config.algorithms if alg != ImageHashingAlgorithm.CLIP_EMBEDDING])},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)},
                                {"name": "MAX_IMAGE_SIZE_MB", "value": str(self.config.max_image_size_mb)},
                                {"name": "HASH_SIZE", "value": "16"},
                                {"name": "HIGH_FREQUENCY_FACTOR", "value": "4"}
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "1Gi"},
                                "limits": {"cpu": "2000m", "memory": "4Gi"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 15,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8080},
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        hash_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=hash_deployment
        )
        
        # Create service for traditional hashing
        hash_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "image-hash-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "image-hash-service"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        hash_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=hash_service
        )
        
        return {
            "deployment_id": hash_deploy.metadata.uid,
            "service_id": hash_svc.metadata.uid,
            "algorithms": [alg.value for alg in self.config.algorithms if alg != ImageHashingAlgorithm.CLIP_EMBEDDING],
            "features": ["fast_processing", "low_resource", "traditional_methods"]
        }
    
    async def _deploy_similarity_service(self) -> Dict[str, Any]:
        """Deploy similarity calculation service"""
        similarity_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "image-similarity-service",
                "namespace": self.config.namespace,
                "labels": {"app": "image-similarity-service", "component": "similarity-engine"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "image-similarity-service"}},
                "template": {
                    "metadata": {"labels": {"app": "image-similarity-service"}},
                    "spec": {
                        "containers": [{
                            "name": "similarity-calculator",
                            "image": "ia-influencer/image-similarity:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "SIMILARITY_METRICS", "value": ",".join([met.value for met in self.config.similarity_metrics])},
                                {"name": "SIMILARITY_THRESHOLD", "value": str(self.config.similarity_threshold)},
                                {"name": "VECTOR_DB_URL", "value": "http://image-vector-db-service:8080"},
                                {"name": "CACHE_URL", "value": "redis://image-fingerprint-redis:6379"},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)}
                            ],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "2Gi"},
                                "limits": {"cpu": "4000m", "memory": "8Gi"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 20,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8080},
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        similarity_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=similarity_deployment
        )
        
        # Create service for similarity engine
        similarity_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "image-similarity-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "image-similarity-service"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        similarity_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=similarity_service
        )
        
        return {
            "deployment_id": similarity_deploy.metadata.uid,
            "service_id": similarity_svc.metadata.uid,
            "similarity_metrics": [met.value for met in self.config.similarity_metrics],
            "threshold": self.config.similarity_threshold,
            "features": ["multi_metric", "fast_search", "accuracy_tuning"]
        }
    
    async def _deploy_processing_pipeline(self) -> Dict[str, Any]:
        """Deploy image processing pipeline orchestrator"""
        pipeline_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "image-processing-pipeline",
                "namespace": self.config.namespace,
                "labels": {"app": "image-processing-pipeline", "component": "orchestrator"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "image-processing-pipeline"}},
                "template": {
                    "metadata": {"labels": {"app": "image-processing-pipeline"}},
                    "spec": {
                        "containers": [{
                            "name": "pipeline-orchestrator",
                            "image": "ia-influencer/image-pipeline:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "PROCESSING_PIPELINE", "value": self.config.processing_pipeline.value},
                                {"name": "CLIP_SERVICE_URL", "value": "http://image-clip-service:8080"},
                                {"name": "HASH_SERVICE_URL", "value": "http://image-hash-service:8080"},
                                {"name": "SIMILARITY_SERVICE_URL", "value": "http://image-similarity-service:8080"},
                                {"name": "STORAGE_SERVICE_URL", "value": "http://image-storage-service:9000"},
                                {"name": "CACHE_URL", "value": "redis://image-fingerprint-redis:6379"},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)},
                                {"name": "MAX_CONCURRENT_JOBS", "value": "100"}
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "1Gi"},
                                "limits": {"cpu": "2000m", "memory": "4Gi"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 15
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8080},
                                "initialDelaySeconds": 15,
                                "periodSeconds": 10
                            }
                        }]
                    }
                }
            }
        }
        
        pipeline_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=pipeline_deployment
        )
        
        # Create service for processing pipeline
        pipeline_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "image-processing-pipeline",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "image-processing-pipeline"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        pipeline_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=pipeline_service
        )
        
        return {
            "deployment_id": pipeline_deploy.metadata.uid,
            "service_id": pipeline_svc.metadata.uid,
            "pipeline_type": self.config.processing_pipeline.value,
            "features": ["workflow_orchestration", "parallel_processing", "fault_tolerance"]
        }
    
    async def _deploy_api_gateway(self) -> Dict[str, Any]:
        """Deploy API gateway for image fingerprinting services"""
        gateway_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "image-fingerprint-api",
                "namespace": self.config.namespace,
                "labels": {"app": "image-fingerprint-api", "component": "api-gateway"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "image-fingerprint-api"}},
                "template": {
                    "metadata": {"labels": {"app": "image-fingerprint-api"}},
                    "spec": {
                        "containers": [{
                            "name": "api-gateway",
                            "image": "ia-influencer/image-fingerprint-api:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "PIPELINE_SERVICE_URL", "value": "http://image-processing-pipeline:8080"},
                                {"name": "SIMILARITY_SERVICE_URL", "value": "http://image-similarity-service:8080"},
                                {"name": "CACHE_URL", "value": "redis://image-fingerprint-redis:6379"},
                                {"name": "AUTH_ENABLED", "value": "true"},
                                {"name": "RATE_LIMITING", "value": "true"},
                                {"name": "MAX_REQUESTS_PER_MINUTE", "value": "1000"},
                                {"name": "MAX_FILE_SIZE_MB", "value": str(self.config.max_image_size_mb)}
                            ],
                            "resources": {
                                "requests": {"cpu": "300m", "memory": "512Mi"},
                                "limits": {"cpu": "1000m", "memory": "2Gi"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 20,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8080},
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        gateway_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=gateway_deployment
        )
        
        # Create service for API gateway
        gateway_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "image-fingerprint-api",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "image-fingerprint-api"},
                "ports": [{"port": 80, "targetPort": 8080}],
                "type": "LoadBalancer"
            }
        }
        
        gateway_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=gateway_service
        )
        
        return {
            "deployment_id": gateway_deploy.metadata.uid,
            "service_id": gateway_svc.metadata.uid,
            "features": ["authentication", "rate_limiting", "load_balancing", "api_management"]
        }
    
    async def _deploy_monitoring_stack(self) -> Dict[str, Any]:
        """Deploy monitoring and metrics collection"""
        monitor_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "image-fingerprint-monitor",
                "namespace": self.config.namespace,
                "labels": {"app": "image-fingerprint-monitor", "component": "monitoring"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "image-fingerprint-monitor"}},
                "template": {
                    "metadata": {"labels": {"app": "image-fingerprint-monitor"}},
                    "spec": {
                        "containers": [{
                            "name": "metrics-collector",
                            "image": "ia-influencer/image-fingerprint-monitor:v1.0",
                            "ports": [{"containerPort": 8080}, {"containerPort": 9090}],
                            "env": [
                                {"name": "PROMETHEUS_PORT", "value": "9090"},
                                {"name": "METRICS_INTERVAL", "value": "30"},
                                {"name": "ALERT_WEBHOOK_URL", "value": "http://ia-influencer-alerts:8080/webhook"},
                                {"name": "SERVICES_TO_MONITOR", "value": "image-clip-service,image-hash-service,image-similarity-service"}
                            ],
                            "resources": {
                                "requests": {"cpu": "200m", "memory": "512Mi"},
                                "limits": {"cpu": "1000m", "memory": "2Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        monitor_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=monitor_deployment
        )
        
        # Create service for monitoring
        monitor_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "image-fingerprint-monitor",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "image-fingerprint-monitor"},
                "ports": [
                    {"port": 8080, "targetPort": 8080, "name": "dashboard"},
                    {"port": 9090, "targetPort": 9090, "name": "metrics"}
                ]
            }
        }
        
        monitor_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=monitor_service
        )
        
        return {
            "deployment_id": monitor_deploy.metadata.uid,
            "service_id": monitor_svc.metadata.uid,
            "features": ["prometheus_metrics", "alerting", "dashboard", "health_monitoring"]
        }
    
    async def _setup_autoscaling(self, deployment_name: str) -> None:
        """Set up horizontal pod autoscaling"""
        hpa_spec = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"hpa-{deployment_name}",
                "namespace": self.config.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": deployment_name
                },
                "minReplicas": self.config.min_replicas,
                "maxReplicas": self.config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 80
                            }
                        }
                    }
                ]
            }
        }
        
        self.k8s_autoscaling_v2.create_namespaced_horizontal_pod_autoscaler(
            namespace=self.config.namespace,
            body=hpa_spec
        )
        
        logger.info(f"Set up autoscaling for {deployment_name}")
    
    async def _configure_networking(self) -> None:
        """Configure networking and security policies"""
        # Network policy for image fingerprinting
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "image-fingerprint-network-policy",
                "namespace": self.config.namespace
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {"namespaceSelector": {"matchLabels": {"name": "ia-influencer"}}},
                            {"podSelector": {"matchLabels": {"app": "image-fingerprint-api"}}}
                        ],
                        "ports": [{"protocol": "TCP", "port": 8080}]
                    }
                ],
                "egress": [
                    {"to": [], "ports": [{"protocol": "TCP", "port": 53}, {"protocol": "UDP", "port": 53}]},
                    {"to": [], "ports": [{"protocol": "TCP", "port": 443}]},
                    {"to": [{"namespaceSelector": {}}]}
                ]
            }
        }
        
        self.k8s_networking_v1.create_namespaced_network_policy(
            namespace=self.config.namespace,
            body=network_policy
        )
        
        logger.info("Configured networking policies for image fingerprinting")
    
    async def _validate_deployment(self) -> bool:
        """Validate the deployment"""
        try:
            essential_services = [
                "image-clip-service", "image-hash-service", "image-similarity-service",
                "image-processing-pipeline", "image-fingerprint-api", "image-vector-db"
            ]
            
            for service in essential_services:
                try:
                    deployment = self.k8s_apps_v1.read_namespaced_deployment(
                        name=service,
                        namespace=self.config.namespace
                    )
                    if not deployment.status.ready_replicas:
                        logger.warning(f"Service {service} is not ready")
                        return False
                except Exception as e:
                    logger.error(f"Service {service} validation failed: {e}")
                    return False
            
            # Test Redis connectivity
            try:
                self._redis_client.ping()
                logger.info("Redis connectivity validated")
            except Exception as e:
                logger.error(f"Redis validation failed: {e}")
                return False
            
            logger.info("Image fingerprinting deployment validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Deployment validation failed: {e}")
            return False
    
    async def get_deployment_status(self) -> Dict[str, Any]:
        """Get deployment status and metrics"""
        try:
            services_status = {}
            
            # Check all services
            for service_name in ["image-clip-service", "image-hash-service", "image-similarity-service", 
                                "image-processing-pipeline", "image-fingerprint-api", "image-vector-db"]:
                try:
                    deployment = self.k8s_apps_v1.read_namespaced_deployment(
                        name=service_name,
                        namespace=self.config.namespace
                    )
                    services_status[service_name] = {
                        "replicas": deployment.status.replicas,
                        "ready_replicas": deployment.status.ready_replicas,
                        "status": "ready" if deployment.status.ready_replicas == deployment.status.replicas else "not_ready"
                    }
                except:
                    services_status[service_name] = {"status": "not_found"}
            
            return {
                "deployment_status": self.deployment_status,
                "namespace": self.config.namespace,
                "services": services_status,
                "vector_db_ready": self.vector_db_ready,
                "configuration": {
                    "algorithms": [alg.value for alg in self.config.algorithms],
                    "similarity_threshold": self.config.similarity_threshold,
                    "gpu_acceleration": self.config.gpu_acceleration,
                    "processing_pipeline": self.config.processing_pipeline.value
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return {"error": str(e)}
    
    async def _cleanup_failed_deployment(self) -> None:
        """Clean up failed deployment"""
        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.config.namespace)
            logger.info("Cleaned up failed image fingerprinting deployment")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up the entire deployment"""
        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.config.namespace)
            
            self.deployment_status = "stopped"
            self.services_deployed = {}
            self.vector_db_ready = False
            
            logger.info("Image fingerprinting deployment cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise
