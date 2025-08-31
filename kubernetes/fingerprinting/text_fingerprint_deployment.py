"""Text Fingerprinting Deployment System
Enterprise text content protection deployment infrastructure

This module provides deployment infrastructure for text fingerprinting
services using BERT, RoBERTa, and advanced NLP technologies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without written permission
will result in legal action under German and international copyright law.
Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
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
import hashlib

logger = logging.getLogger(__name__)


class TextFingerprintAlgorithm(Enum):
    """Text fingerprinting algorithms"""    BERT_EMBEDDING = "bert_embedding"
    ROBERTA_EMBEDDING = "roberta_embedding"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    TFIDF_VECTORIZER = "tfidf_vectorizer"
    DOC2VEC = "doc2vec"
    FUZZY_HASHING = "fuzzy_hashing"
    SEMANTIC_HASHING = "semantic_hashing"
    N_GRAM_ANALYSIS = "n_gram_analysis"
    STYLOMETRIC_FEATURES = "stylometric_features"


class TextSimilarityMetric(Enum):
    """Text similarity metrics"""    COSINE_SIMILARITY = "cosine_similarity"
    JACCARD_SIMILARITY = "jaccard_similarity"
    LEVENSHTEIN_DISTANCE = "levenshtein_distance"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    BLEU_SCORE = "bleu_score"
    ROUGE_SCORE = "rouge_score"
    BERT_SCORE = "bert_score"


class ContentType(Enum):
    """Text content types"""    ARTICLE = "article"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    LYRICS = "lyrics"
    SCRIPT = "script"
    POEM = "poem"
    STORY = "story"
    REVIEW = "review"
    COMMENT = "comment"
    GENERIC_TEXT = "generic_text"


@dataclass
class TextFingerprintConfig:
    """Text fingerprinting deployment configuration"""    deployment_name: str
    namespace: str = "ia-influencer-protection"
    algorithms: List[TextFingerprintAlgorithm] = None
    similarity_metrics: List[TextSimilarityMetric] = None
    content_types: List[ContentType] = None
    similarity_threshold: float = 0.80
    min_text_length: int = 50
    max_text_length: int = 100000
    batch_size: int = 16
    chunk_size: int = 512
    overlap_size: int = 50
    supported_languages: List[str] = None
    bert_model: str = "bert-base-multilingual-cased"
    roberta_model: str = "roberta-base"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    vector_dimension: int = 768
    gpu_acceleration: bool = True
    preprocessing_enabled: bool = True
    replicas: int = 3
    min_replicas: int = 2
    max_replicas: int = 15
    cpu_request: str = "1000m"
    memory_request: str = "4Gi"
    cpu_limit: str = "4000m"
    memory_limit: str = "16Gi"
    storage_size: str = "200Gi"
    monitoring_enabled: bool = True
    
    def __post_init__(self):
        if self.algorithms is None:
            self.algorithms = [
                TextFingerprintAlgorithm.BERT_EMBEDDING,
                TextFingerprintAlgorithm.SENTENCE_TRANSFORMERS,
                TextFingerprintAlgorithm.FUZZY_HASHING
            ]
        if self.similarity_metrics is None:
            self.similarity_metrics = [
                TextSimilarityMetric.COSINE_SIMILARITY,
                TextSimilarityMetric.SEMANTIC_SIMILARITY,
                TextSimilarityMetric.BERT_SCORE
            ]
        if self.content_types is None:
            self.content_types = [
                ContentType.ARTICLE,
                ContentType.BLOG_POST,
                ContentType.SOCIAL_MEDIA,
                ContentType.LYRICS
            ]
        if self.supported_languages is None:
            self.supported_languages = ["en", "de", "fr", "es", "it", "pt", "nl", "pl", "ru", "zh"]


class TextFingerprintDeployment:
    """    Enterprise text fingerprinting deployment system
    
    Deploys and manages text content protection infrastructure:
    - BERT/RoBERTa-based semantic embeddings
    - Traditional text hashing and fingerprinting
    - Multi-language support and processing
    - Semantic similarity detection
    - Real-time and batch processing
    - Plagiarism and content theft detection
    """    
    def __init__(self, config: TextFingerprintConfig):
        """        Initialize text fingerprinting deployment
        
        Args:
            config: Deployment configuration
        """        self.config = config
        self.deployment_status = "initializing"
        self.services_deployed = {}
        self.nlp_models_ready = False
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Kubernetes, Docker, and Redis clients"""        try:
            # Kubernetes client
            config.load_incluster_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_autoscaling_v2 = client.AutoscalingV2Api()
            self.k8s_networking_v1 = client.NetworkingV1Api()
            
            # Docker client
            self._docker_client = docker.from_env()
            
            # Redis for text fingerprint caching
            self._redis_client = redis.Redis(
                host='text-fingerprint-redis',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            logger.info("Text fingerprinting clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize text fingerprinting clients: {e}")
            raise
    
    async def deploy_text_fingerprinting_infrastructure(self) -> Dict[str, Any]:
        """        Deploy complete text fingerprinting infrastructure
        
        Returns:
            Infrastructure deployment summary
        """        try:
            self.deployment_status = "deploying_infrastructure"
            logger.info("Deploying text fingerprinting infrastructure")
            
            # Create namespace
            await self._ensure_namespace()
            
            # Deploy storage infrastructure
            storage_result = await self._deploy_storage_infrastructure()
            
            # Deploy NLP models storage and management
            model_storage_result = await self._deploy_model_storage()
            
            # Deploy Redis for caching
            redis_result = await self._deploy_fingerprint_cache()
            
            # Deploy BERT/RoBERTa services
            bert_service_result = await self._deploy_bert_service()
            roberta_service_result = await self._deploy_roberta_service()
            
            # Deploy sentence transformers service
            sentence_transformer_result = await self._deploy_sentence_transformer_service()
            
            # Deploy traditional text hashing service
            traditional_hash_result = await self._deploy_traditional_hash_service()
            
            # Deploy text preprocessing service
            preprocessing_result = await self._deploy_preprocessing_service()
            
            # Deploy similarity calculation service
            similarity_service_result = await self._deploy_similarity_service()
            
            # Deploy text processing pipeline
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
                logger.info("Text fingerprinting infrastructure deployed successfully")
                
                return {
                    "status": "success",
                    "deployment_name": self.config.deployment_name,
                    "namespace": self.config.namespace,
                    "services": {
                        "storage": storage_result,
                        "model_storage": model_storage_result,
                        "redis_cache": redis_result,
                        "bert_service": bert_service_result,
                        "roberta_service": roberta_service_result,
                        "sentence_transformer": sentence_transformer_result,
                        "traditional_hash": traditional_hash_result,
                        "preprocessing": preprocessing_result,
                        "similarity_service": similarity_service_result,
                        "processing_pipeline": pipeline_result,
                        "api_gateway": api_gateway_result,
                        "monitoring": monitoring_result
                    },
                    "capabilities": {
                        "algorithms": [alg.value for alg in self.config.algorithms],
                        "similarity_metrics": [met.value for met in self.config.similarity_metrics],
                        "content_types": [ct.value for ct in self.config.content_types],
                        "supported_languages": self.config.supported_languages,
                        "gpu_acceleration": self.config.gpu_acceleration,
                        "similarity_threshold": self.config.similarity_threshold,
                        "max_text_length": self.config.max_text_length
                    },
                    "endpoints": {
                        "fingerprint_api": f"http://text-fingerprint-api.{self.config.namespace}.svc.cluster.local",
                        "similarity_api": f"http://text-similarity-api.{self.config.namespace}.svc.cluster.local",
                        "monitoring": f"http://text-fingerprint-monitor.{self.config.namespace}.svc.cluster.local"
                    }
                }
            else:
                raise Exception("Text fingerprinting infrastructure validation failed")
                
        except Exception as e:
            self.deployment_status = "deployment_failed"
            logger.error(f"Text fingerprinting infrastructure deployment failed: {e}")
            await self._cleanup_failed_deployment()
            raise
    
    async def _ensure_namespace(self) -> None:
        """Create namespace if it doesn't exist"""        try:
            self.k8s_core_v1.read_namespace(name=self.config.namespace)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                namespace_body = client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name=self.config.namespace,
                        labels={
                            "name": self.config.namespace,
                            "purpose": "text-fingerprinting",
                            "protection-type": "content",
                            "nlp-powered": "true"
                        }
                    )
                )
                self.k8s_core_v1.create_namespace(body=namespace_body)
                logger.info(f"Created namespace: {self.config.namespace}")
    
    async def _deploy_storage_infrastructure(self) -> Dict[str, Any]:
        """Deploy storage infrastructure for text fingerprints"""        # Create persistent volume claim
        pvc_spec = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": "text-fingerprint-storage",
                "namespace": self.config.namespace,
                "labels": {"app": "text-fingerprinting", "component": "storage"}
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
        
        # Deploy MongoDB for text storage and indexing
        mongodb_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-storage-mongodb",
                "namespace": self.config.namespace,
                "labels": {"app": "text-storage", "component": "document-db"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "text-storage"}},
                "template": {
                    "metadata": {"labels": {"app": "text-storage"}},
                    "spec": {
                        "containers": [{
                            "name": "mongodb",
                            "image": "mongo:6.0",
                            "ports": [{"containerPort": 27017}],
                            "env": [
                                {"name": "MONGO_INITDB_ROOT_USERNAME", "value": "textfingerprint"},
                                {"name": "MONGO_INITDB_ROOT_PASSWORD", "value": "secure-text-db-password"},
                                {"name": "MONGO_INITDB_DATABASE", "value": "text_fingerprints"}
                            ],
                            "volumeMounts": [{
                                "name": "storage",
                                "mountPath": "/data/db"
                            }],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "4Gi"},
                                "limits": {"cpu": "4000m", "memory": "16Gi"}
                            }
                        }],
                        "volumes": [{
                            "name": "storage",
                            "persistentVolumeClaim": {"claimName": "text-fingerprint-storage"}
                        }]
                    }
                }
            }
        }
        
        mongodb_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=mongodb_deployment
        )
        
        # Create service for MongoDB
        mongodb_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "text-storage-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-storage"},
                "ports": [{"port": 27017, "targetPort": 27017}]
            }
        }
        
        mongodb_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=mongodb_service
        )
        
        return {
            "pvc_id": pvc.metadata.uid,
            "deployment_id": mongodb_deploy.metadata.uid,
            "service_id": mongodb_svc.metadata.uid,
            "storage_size": self.config.storage_size,
            "features": ["document_storage", "text_indexing", "full_text_search"]
        }
    
    async def _deploy_model_storage(self) -> Dict[str, Any]:
        """Deploy model storage and management service"""        model_storage_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-model-storage",
                "namespace": self.config.namespace,
                "labels": {"app": "text-model-storage", "component": "model-management"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "text-model-storage"}},
                "template": {
                    "metadata": {"labels": {"app": "text-model-storage"}},
                    "spec": {
                        "containers": [{
                            "name": "model-manager",
                            "image": "ia-influencer/text-model-manager:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "MODELS_PATH", "value": "/models"},
                                {"name": "BERT_MODEL", "value": self.config.bert_model},
                                {"name": "ROBERTA_MODEL", "value": self.config.roberta_model},
                                {"name": "SENTENCE_TRANSFORMER_MODEL", "value": self.config.sentence_transformer_model},
                                {"name": "AUTO_DOWNLOAD", "value": "true"},
                                {"name": "MODEL_CACHING", "value": "true"}
                            ],
                            "volumeMounts": [{
                                "name": "model-storage",
                                "mountPath": "/models"
                            }],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "2Gi"},
                                "limits": {"cpu": "2000m", "memory": "8Gi"}
                            }
                        }],
                        "volumes": [{
                            "name": "model-storage",
                            "persistentVolumeClaim": {"claimName": "text-fingerprint-storage"}
                        }]
                    }
                }
            }
        }
        
        model_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=model_storage_deployment
        )
        
        # Create service for model storage
        model_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "text-model-storage",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-model-storage"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        model_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=model_service
        )
        
        return {
            "deployment_id": model_deploy.metadata.uid,
            "service_id": model_svc.metadata.uid,
            "supported_models": [self.config.bert_model, self.config.roberta_model, self.config.sentence_transformer_model],
            "features": ["model_caching", "auto_download", "model_versioning"]
        }
    
    async def _deploy_fingerprint_cache(self) -> Dict[str, Any]:
        """Deploy Redis for text fingerprint caching"""        redis_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-fingerprint-redis",
                "namespace": self.config.namespace,
                "labels": {"app": "text-fingerprint-redis", "component": "cache"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "text-fingerprint-redis"}},
                "template": {
                    "metadata": {"labels": {"app": "text-fingerprint-redis"}},
                    "spec": {
                        "containers": [{
                            "name": "redis",
                            "image": "redis:7-alpine",
                            "args": [
                                "redis-server",
                                "--maxmemory", "12gb",
                                "--maxmemory-policy", "allkeys-lru",
                                "--tcp-keepalive", "60",
                                "--timeout", "300"
                            ],
                            "ports": [{"containerPort": 6379}],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "6Gi"},
                                "limits": {"cpu": "2000m", "memory": "12Gi"}
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
                "name": "text-fingerprint-redis",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-fingerprint-redis"},
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
            "memory_limit": "12Gi",
            "features": ["high_memory", "clustering", "persistence"]
        }
    
    async def _deploy_bert_service(self) -> Dict[str, Any]:
        """Deploy BERT embedding service"""        bert_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-bert-service",
                "namespace": self.config.namespace,
                "labels": {"app": "text-bert-service", "component": "nlp-embedding"}
            },
            "spec": {
                "replicas": self.config.replicas,
                "selector": {"matchLabels": {"app": "text-bert-service"}},
                "template": {
                    "metadata": {"labels": {"app": "text-bert-service"}},
                    "spec": {
                        "containers": [{
                            "name": "bert-embedder",
                            "image": "ia-influencer/text-bert-embedder:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "BERT_MODEL", "value": self.config.bert_model},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)},
                                {"name": "MAX_LENGTH", "value": str(self.config.chunk_size)},
                                {"name": "VECTOR_DIMENSION", "value": str(self.config.vector_dimension)},
                                {"name": "GPU_ENABLED", "value": str(self.config.gpu_acceleration).lower()},
                                {"name": "SUPPORTED_LANGUAGES", "value": ",".join(self.config.supported_languages)},
                                {"name": "MODEL_SERVICE_URL", "value": "http://text-model-storage:8080"}
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
                                "initialDelaySeconds": 60,
                                "periodSeconds": 15
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8080},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            }
                        }]
                    }
                }
            }
        }
        
        # Add GPU resources if enabled
        if self.config.gpu_acceleration:
            container = bert_deployment["spec"]["template"]["spec"]["containers"][0]
            container["resources"]["requests"]["nvidia.com/gpu"] = "1"
            container["resources"]["limits"]["nvidia.com/gpu"] = "1"
        
        bert_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=bert_deployment
        )
        
        # Create service for BERT
        bert_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "text-bert-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-bert-service"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        bert_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=bert_service
        )
        
        # Set up auto-scaling
        await self._setup_autoscaling("text-bert-service")
        
        return {
            "deployment_id": bert_deploy.metadata.uid,
            "service_id": bert_svc.metadata.uid,
            "model": self.config.bert_model,
            "vector_dimension": self.config.vector_dimension,
            "gpu_acceleration": self.config.gpu_acceleration,
            "features": ["multilingual", "contextual_embeddings", "transfer_learning"]
        }
    
    async def _deploy_roberta_service(self) -> Dict[str, Any]:
        """Deploy RoBERTa embedding service"""        roberta_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-roberta-service",
                "namespace": self.config.namespace,
                "labels": {"app": "text-roberta-service", "component": "nlp-embedding"}
            },
            "spec": {
                "replicas": self.config.replicas,
                "selector": {"matchLabels": {"app": "text-roberta-service"}},
                "template": {
                    "metadata": {"labels": {"app": "text-roberta-service"}},
                    "spec": {
                        "containers": [{
                            "name": "roberta-embedder",
                            "image": "ia-influencer/text-roberta-embedder:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "ROBERTA_MODEL", "value": self.config.roberta_model},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)},
                                {"name": "MAX_LENGTH", "value": str(self.config.chunk_size)},
                                {"name": "VECTOR_DIMENSION", "value": str(self.config.vector_dimension)},
                                {"name": "GPU_ENABLED", "value": str(self.config.gpu_acceleration).lower()},
                                {"name": "MODEL_SERVICE_URL", "value": "http://text-model-storage:8080"}
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
                                "initialDelaySeconds": 60,
                                "periodSeconds": 15
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8080},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            }
                        }]
                    }
                }
            }
        }
        
        # Add GPU resources if enabled
        if self.config.gpu_acceleration:
            container = roberta_deployment["spec"]["template"]["spec"]["containers"][0]
            container["resources"]["requests"]["nvidia.com/gpu"] = "1"
            container["resources"]["limits"]["nvidia.com/gpu"] = "1"
        
        roberta_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=roberta_deployment
        )
        
        # Create service for RoBERTa
        roberta_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "text-roberta-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-roberta-service"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        roberta_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=roberta_service
        )
        
        # Set up auto-scaling
        await self._setup_autoscaling("text-roberta-service")
        
        return {
            "deployment_id": roberta_deploy.metadata.uid,
            "service_id": roberta_svc.metadata.uid,
            "model": self.config.roberta_model,
            "vector_dimension": self.config.vector_dimension,
            "features": ["optimized_bert", "robust_training", "improved_performance"]
        }
    
    async def _deploy_sentence_transformer_service(self) -> Dict[str, Any]:
        """Deploy Sentence Transformers service"""        st_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-sentence-transformer",
                "namespace": self.config.namespace,
                "labels": {"app": "text-sentence-transformer", "component": "sentence-embedding"}
            },
            "spec": {
                "replicas": self.config.replicas,
                "selector": {"matchLabels": {"app": "text-sentence-transformer"}},
                "template": {
                    "metadata": {"labels": {"app": "text-sentence-transformer"}},
                    "spec": {
                        "containers": [{
                            "name": "sentence-transformer",
                            "image": "ia-influencer/sentence-transformer:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "ST_MODEL", "value": self.config.sentence_transformer_model},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)},
                                {"name": "MAX_LENGTH", "value": str(self.config.chunk_size)},
                                {"name": "GPU_ENABLED", "value": str(self.config.gpu_acceleration).lower()},
                                {"name": "MODEL_SERVICE_URL", "value": "http://text-model-storage:8080"}
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "2Gi"},
                                "limits": {"cpu": "2000m", "memory": "8Gi"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8080},
                                "initialDelaySeconds": 15,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        st_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=st_deployment
        )
        
        # Create service for Sentence Transformers
        st_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "text-sentence-transformer",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-sentence-transformer"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        st_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=st_service
        )
        
        return {
            "deployment_id": st_deploy.metadata.uid,
            "service_id": st_svc.metadata.uid,
            "model": self.config.sentence_transformer_model,
            "features": ["sentence_level", "semantic_search", "lightweight"]
        }
    
    async def _deploy_traditional_hash_service(self) -> Dict[str, Any]:
        """Deploy traditional text hashing service"""        hash_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-hash-service",
                "namespace": self.config.namespace,
                "labels": {"app": "text-hash-service", "component": "traditional-hash"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "text-hash-service"}},
                "template": {
                    "metadata": {"labels": {"app": "text-hash-service"}},
                    "spec": {
                        "containers": [{
                            "name": "text-hasher",
                            "image": "ia-influencer/text-hasher:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "HASH_ALGORITHMS", "value": "fuzzy,ngram,stylometric"},
                                {"name": "N_GRAM_SIZE", "value": "3"},
                                {"name": "FUZZY_THRESHOLD", "value": "80"},
                                {"name": "STYLOMETRIC_FEATURES", "value": "sentence_length,word_frequency,punctuation"},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)}
                            ],
                            "resources": {
                                "requests": {"cpu": "300m", "memory": "1Gi"},
                                "limits": {"cpu": "1000m", "memory": "4Gi"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 15,
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
        
        hash_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=hash_deployment
        )
        
        # Create service for traditional hashing
        hash_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "text-hash-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-hash-service"},
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
            "algorithms": ["fuzzy_hashing", "n_gram_analysis", "stylometric_features"],
            "features": ["fast_processing", "traditional_methods", "language_independent"]
        }
    
    async def _deploy_preprocessing_service(self) -> Dict[str, Any]:
        """Deploy text preprocessing service"""        preprocessing_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-preprocessing",
                "namespace": self.config.namespace,
                "labels": {"app": "text-preprocessing", "component": "text-processing"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "text-preprocessing"}},
                "template": {
                    "metadata": {"labels": {"app": "text-preprocessing"}},
                    "spec": {
                        "containers": [{
                            "name": "text-preprocessor",
                            "image": "ia-influencer/text-preprocessor:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "SUPPORTED_LANGUAGES", "value": ",".join(self.config.supported_languages)},
                                {"name": "MIN_TEXT_LENGTH", "value": str(self.config.min_text_length)},
                                {"name": "MAX_TEXT_LENGTH", "value": str(self.config.max_text_length)},
                                {"name": "CHUNK_SIZE", "value": str(self.config.chunk_size)},
                                {"name": "OVERLAP_SIZE", "value": str(self.config.overlap_size)},
                                {"name": "NORMALIZE_TEXT", "value": "true"},
                                {"name": "REMOVE_STOP_WORDS", "value": "false"},
                                {"name": "LANGUAGE_DETECTION", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "300m", "memory": "1Gi"},
                                "limits": {"cpu": "1000m", "memory": "4Gi"}
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
        
        preprocessing_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=preprocessing_deployment
        )
        
        # Create service for preprocessing
        preprocessing_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "text-preprocessing",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-preprocessing"},
                "ports": [{"port": 8080, "targetPort": 8080}]
            }
        }
        
        preprocessing_svc = self.k8s_core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=preprocessing_service
        )
        
        return {
            "deployment_id": preprocessing_deploy.metadata.uid,
            "service_id": preprocessing_svc.metadata.uid,
            "supported_languages": self.config.supported_languages,
            "features": ["text_normalization", "chunking", "language_detection", "encoding_handling"]
        }
    
    async def _deploy_similarity_service(self) -> Dict[str, Any]:
        """Deploy text similarity calculation service"""        similarity_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-similarity-service",
                "namespace": self.config.namespace,
                "labels": {"app": "text-similarity-service", "component": "similarity-engine"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "text-similarity-service"}},
                "template": {
                    "metadata": {"labels": {"app": "text-similarity-service"}},
                    "spec": {
                        "containers": [{
                            "name": "similarity-calculator",
                            "image": "ia-influencer/text-similarity:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "SIMILARITY_METRICS", "value": ",".join([met.value for met in self.config.similarity_metrics])},
                                {"name": "SIMILARITY_THRESHOLD", "value": str(self.config.similarity_threshold)},
                                {"name": "STORAGE_URL", "value": "mongodb://text-storage-service:27017"},
                                {"name": "CACHE_URL", "value": "redis://text-fingerprint-redis:6379"},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)},
                                {"name": "PARALLEL_PROCESSING", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "4Gi"},
                                "limits": {"cpu": "4000m", "memory": "16Gi"}
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
        
        similarity_deploy = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=similarity_deployment
        )
        
        # Create service for similarity engine
        similarity_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "text-similarity-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-similarity-service"},
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
            "features": ["multi_metric", "parallel_processing", "threshold_tuning"]
        }
    
    async def _deploy_processing_pipeline(self) -> Dict[str, Any]:
        """Deploy text processing pipeline orchestrator"""        pipeline_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-processing-pipeline",
                "namespace": self.config.namespace,
                "labels": {"app": "text-processing-pipeline", "component": "orchestrator"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "text-processing-pipeline"}},
                "template": {
                    "metadata": {"labels": {"app": "text-processing-pipeline"}},
                    "spec": {
                        "containers": [{
                            "name": "pipeline-orchestrator",
                            "image": "ia-influencer/text-pipeline:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "PREPROCESSING_URL", "value": "http://text-preprocessing:8080"},
                                {"name": "BERT_SERVICE_URL", "value": "http://text-bert-service:8080"},
                                {"name": "ROBERTA_SERVICE_URL", "value": "http://text-roberta-service:8080"},
                                {"name": "SENTENCE_TRANSFORMER_URL", "value": "http://text-sentence-transformer:8080"},
                                {"name": "HASH_SERVICE_URL", "value": "http://text-hash-service:8080"},
                                {"name": "SIMILARITY_SERVICE_URL", "value": "http://text-similarity-service:8080"},
                                {"name": "STORAGE_URL", "value": "mongodb://text-storage-service:27017"},
                                {"name": "CACHE_URL", "value": "redis://text-fingerprint-redis:6379"},
                                {"name": "BATCH_SIZE", "value": str(self.config.batch_size)},
                                {"name": "MAX_CONCURRENT_JOBS", "value": "50"}
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "2Gi"},
                                "limits": {"cpu": "2000m", "memory": "8Gi"}
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
                "name": "text-processing-pipeline",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-processing-pipeline"},
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
            "features": ["workflow_orchestration", "parallel_processing", "fault_tolerance", "async_processing"]
        }
    
    async def _deploy_api_gateway(self) -> Dict[str, Any]:
        """Deploy API gateway for text fingerprinting services"""        gateway_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-fingerprint-api",
                "namespace": self.config.namespace,
                "labels": {"app": "text-fingerprint-api", "component": "api-gateway"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "text-fingerprint-api"}},
                "template": {
                    "metadata": {"labels": {"app": "text-fingerprint-api"}},
                    "spec": {
                        "containers": [{
                            "name": "api-gateway",
                            "image": "ia-influencer/text-fingerprint-api:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "PIPELINE_SERVICE_URL", "value": "http://text-processing-pipeline:8080"},
                                {"name": "SIMILARITY_SERVICE_URL", "value": "http://text-similarity-service:8080"},
                                {"name": "CACHE_URL", "value": "redis://text-fingerprint-redis:6379"},
                                {"name": "AUTH_ENABLED", "value": "true"},
                                {"name": "RATE_LIMITING", "value": "true"},
                                {"name": "MAX_REQUESTS_PER_MINUTE", "value": "500"},
                                {"name": "MAX_TEXT_LENGTH", "value": str(self.config.max_text_length)},
                                {"name": "SUPPORTED_LANGUAGES", "value": ",".join(self.config.supported_languages)}
                            ],
                            "resources": {
                                "requests": {"cpu": "300m", "memory": "1Gi"},
                                "limits": {"cpu": "1000m", "memory": "4Gi"}
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
                "name": "text-fingerprint-api",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-fingerprint-api"},
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
            "features": ["authentication", "rate_limiting", "load_balancing", "text_validation"]
        }
    
    async def _deploy_monitoring_stack(self) -> Dict[str, Any]:
        """Deploy monitoring and metrics collection"""        monitor_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "text-fingerprint-monitor",
                "namespace": self.config.namespace,
                "labels": {"app": "text-fingerprint-monitor", "component": "monitoring"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "text-fingerprint-monitor"}},
                "template": {
                    "metadata": {"labels": {"app": "text-fingerprint-monitor"}},
                    "spec": {
                        "containers": [{
                            "name": "metrics-collector",
                            "image": "ia-influencer/text-fingerprint-monitor:v1.0",
                            "ports": [{"containerPort": 8080}, {"containerPort": 9090}],
                            "env": [
                                {"name": "PROMETHEUS_PORT", "value": "9090"},
                                {"name": "METRICS_INTERVAL", "value": "30"},
                                {"name": "ALERT_WEBHOOK_URL", "value": "http://ia-influencer-alerts:8080/webhook"},
                                {"name": "SERVICES_TO_MONITOR", "value": "text-bert-service,text-roberta-service,text-similarity-service"}
                            ],
                            "resources": {
                                "requests": {"cpu": "200m", "memory": "1Gi"},
                                "limits": {"cpu": "1000m", "memory": "4Gi"}
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
                "name": "text-fingerprint-monitor",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {"app": "text-fingerprint-monitor"},
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
            "features": ["prometheus_metrics", "nlp_monitoring", "performance_tracking", "alerting"]
        }
    
    async def _setup_autoscaling(self, deployment_name: str) -> None:
        """Set up horizontal pod autoscaling"""        hpa_spec = {
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
        """Configure networking and security policies"""        # Network policy for text fingerprinting
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "text-fingerprint-network-policy",
                "namespace": self.config.namespace
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {"namespaceSelector": {"matchLabels": {"name": "ia-influencer"}}},
                            {"podSelector": {"matchLabels": {"app": "text-fingerprint-api"}}}
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
        
        logger.info("Configured networking policies for text fingerprinting")
    
    async def _validate_deployment(self) -> bool:
        """Validate the deployment"""        try:
            essential_services = [
                "text-bert-service", "text-roberta-service", "text-sentence-transformer",
                "text-hash-service", "text-preprocessing", "text-similarity-service",
                "text-processing-pipeline", "text-fingerprint-api"
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
            
            self.nlp_models_ready = True
            logger.info("Text fingerprinting deployment validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Deployment validation failed: {e}")
            return False
    
    async def get_deployment_status(self) -> Dict[str, Any]:
        """Get deployment status and metrics"""        try:
            services_status = {}
            
            # Check all services
            for service_name in ["text-bert-service", "text-roberta-service", "text-sentence-transformer",
                                "text-hash-service", "text-preprocessing", "text-similarity-service", 
                                "text-processing-pipeline", "text-fingerprint-api"]:
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
                "nlp_models_ready": self.nlp_models_ready,
                "configuration": {
                    "algorithms": [alg.value for alg in self.config.algorithms],
                    "similarity_threshold": self.config.similarity_threshold,
                    "supported_languages": self.config.supported_languages,
                    "gpu_acceleration": self.config.gpu_acceleration,
                    "vector_dimension": self.config.vector_dimension
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return {"error": str(e)}
    
    async def _cleanup_failed_deployment(self) -> None:
        """Clean up failed deployment"""        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.config.namespace)
            logger.info("Cleaned up failed text fingerprinting deployment")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up the entire deployment"""        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.config.namespace)
            
            self.deployment_status = "stopped"
            self.services_deployed = {}
            self.nlp_models_ready = False
            
            logger.info("Text fingerprinting deployment cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise
