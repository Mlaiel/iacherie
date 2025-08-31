"""Model Serving Deployment
Enterprise model serving infrastructure

This module provides comprehensive model serving capabilities
including TensorFlow, PyTorch, ONNX, and custom model formats
with auto-scaling, monitoring, and A/B testing support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
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
import requests
import time

logger = logging.getLogger(__name__)


class ModelFormat(Enum):
    """Supported model formats"""
    TENSORFLOW_SAVEDMODEL = "tensorflow_savedmodel"
    TENSORFLOW_LITE = "tensorflow_lite"
    PYTORCH_TORCHSCRIPT = "pytorch_torchscript"
    PYTORCH_JIT = "pytorch_jit"
    ONNX = "onnx"
    HUGGINGFACE = "huggingface"
    SCIKIT_LEARN = "scikit_learn"
    XGBOOST = "xgboost"
    CUSTOM = "custom"


class ServingStrategy(Enum):
    """Model serving strategies"""
    BLUE_GREEN = "blue_green"
    ROLLING_UPDATE = "rolling_update"
    A_B_TESTING = "a_b_testing"
    CANARY = "canary"
    SHADOW = "shadow"


class ServingMode(Enum):
    """Serving modes"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    EDGE = "edge"


@dataclass
class ModelServingConfig:
    """Model serving configuration"""
    model_name: str
    model_version: str
    model_format: ModelFormat
    serving_strategy: ServingStrategy = ServingStrategy.ROLLING_UPDATE
    serving_mode: ServingMode = ServingMode.REAL_TIME
    replicas: int = 3
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    auto_scaling: bool = True
    gpu_acceleration: bool = True
    gpu_memory_fraction: float = 0.8
    batch_size: int = 32
    max_latency_ms: int = 100
    model_warmup: bool = True
    health_check_enabled: bool = True
    monitoring_enabled: bool = True
    a_b_testing_enabled: bool = False
    traffic_split: Dict[str, float] = None
    request_timeout: int = 30
    max_queue_size: int = 1000
    
    def __post_init__(self):
        if self.traffic_split is None:
            self.traffic_split = {"A": 1.0}


class ModelServingDeployment:
    """
    Enterprise model serving deployment system
    
    Provides comprehensive model serving infrastructure with:
    - Multi-framework support (TensorFlow, PyTorch, ONNX, etc.)
    - Auto-scaling and load balancing
    - A/B testing and canary deployments
    - Real-time monitoring and observability
    - GPU acceleration and optimization
    - Edge computing support
    """
    
    def __init__(self, namespace: str = "ia-influencer-serving"):
        """
        Initialize model serving deployment
        
        Args:
            namespace: Kubernetes namespace for serving infrastructure
        """
        self.namespace = namespace
        self.deployed_models = {}
        self.serving_instances = {}
        self.traffic_manager = None
        self.status = "initializing"
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Kubernetes, Docker, and Redis clients"""
        try:
            # Kubernetes client
            config.load_incluster_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_autoscaling_v1 = client.AutoscalingV1Api()
            self.k8s_autoscaling_v2 = client.AutoscalingV2Api()
            self.k8s_networking_v1 = client.NetworkingV1Api()
            
            # Docker client for image management
            self._docker_client = docker.from_env()
            
            # Redis for serving metadata and caching
            self._redis_client = redis.Redis(
                host='serving-redis',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            logger.info("Model serving clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize serving clients: {e}")
            raise
    
    async def deploy_serving_infrastructure(self) -> Dict[str, Any]:
        """
        Deploy complete model serving infrastructure
        
        Returns:
            Infrastructure deployment summary
        """
        try:
            self.status = "deploying_infrastructure"
            logger.info("Deploying model serving infrastructure")
            
            # Create serving namespace
            await self._ensure_serving_namespace()
            
            # Deploy serving infrastructure components
            redis_result = await self._deploy_serving_redis()
            load_balancer_result = await self._deploy_load_balancer()
            monitoring_result = await self._deploy_serving_monitoring()
            autoscaler_result = await self._deploy_autoscaler()
            traffic_manager_result = await self._deploy_traffic_manager()
            
            # Deploy framework-specific serving engines
            tf_serving_result = await self._deploy_tensorflow_serving()
            torch_serving_result = await self._deploy_pytorch_serving()
            onnx_serving_result = await self._deploy_onnx_serving()
            hf_serving_result = await self._deploy_huggingface_serving()
            
            # Deploy edge serving infrastructure
            edge_result = await self._deploy_edge_serving()
            
            # Configure serving networking
            await self._configure_serving_networking()
            
            # Validate infrastructure
            if await self._validate_serving_infrastructure():
                self.status = "infrastructure_ready"
                logger.info("Model serving infrastructure deployed successfully")
                
                return {
                    "status": "success",
                    "infrastructure": {
                        "redis": redis_result,
                        "load_balancer": load_balancer_result,
                        "monitoring": monitoring_result,
                        "autoscaler": autoscaler_result,
                        "traffic_manager": traffic_manager_result
                    },
                    "serving_engines": {
                        "tensorflow": tf_serving_result,
                        "pytorch": torch_serving_result,
                        "onnx": onnx_serving_result,
                        "huggingface": hf_serving_result,
                        "edge": edge_result
                    },
                    "capabilities": {
                        "supported_formats": [f.value for f in ModelFormat],
                        "serving_strategies": [s.value for s in ServingStrategy],
                        "serving_modes": [m.value for m in ServingMode],
                        "auto_scaling": True,
                        "gpu_acceleration": True,
                        "a_b_testing": True
                    }
                }
            else:
                raise Exception("Serving infrastructure validation failed")
                
        except Exception as e:
            self.status = "infrastructure_failed"
            logger.error(f"Infrastructure deployment failed: {e}")
            await self._cleanup_failed_infrastructure()
            raise
    
    async def deploy_model(self, config: ModelServingConfig) -> Dict[str, Any]:
        """
        Deploy a model for serving
        
        Args:
            config: Model serving configuration
            
        Returns:
            Model deployment result
        """
        try:
            model_id = f"{config.model_name}-{config.model_version}"
            logger.info(f"Deploying model for serving: {model_id}")
            
            # Validate model configuration
            await self._validate_model_config(config)
            
            # Create model deployment
            deployment_spec = await self._create_model_deployment_spec(config)
            
            # Deploy model based on format
            if config.model_format == ModelFormat.TENSORFLOW_SAVEDMODEL:
                deployment_result = await self._deploy_tensorflow_model(config, deployment_spec)
            elif config.model_format in [ModelFormat.PYTORCH_TORCHSCRIPT, ModelFormat.PYTORCH_JIT]:
                deployment_result = await self._deploy_pytorch_model(config, deployment_spec)
            elif config.model_format == ModelFormat.ONNX:
                deployment_result = await self._deploy_onnx_model(config, deployment_spec)
            elif config.model_format == ModelFormat.HUGGINGFACE:
                deployment_result = await self._deploy_huggingface_model(config, deployment_spec)
            else:
                deployment_result = await self._deploy_custom_model(config, deployment_spec)
            
            # Configure auto-scaling
            if config.auto_scaling:
                await self._configure_model_autoscaling(config)
            
            # Configure traffic routing
            await self._configure_traffic_routing(config)
            
            # Set up monitoring
            if config.monitoring_enabled:
                await self._setup_model_monitoring(config)
            
            # Configure A/B testing if enabled
            if config.a_b_testing_enabled:
                await self._setup_ab_testing(config)
            
            # Store deployment information
            self.deployed_models[model_id] = {
                "config": config,
                "deployment_result": deployment_result,
                "status": "deployed",
                "deployed_at": datetime.utcnow().isoformat(),
                "endpoints": deployment_result.get("endpoints", [])
            }
            
            logger.info(f"Model {model_id} deployed successfully")
            
            return {
                "status": "success",
                "model_id": model_id,
                "deployment_result": deployment_result,
                "endpoints": deployment_result.get("endpoints", []),
                "capabilities": {
                    "auto_scaling": config.auto_scaling,
                    "gpu_acceleration": config.gpu_acceleration,
                    "monitoring": config.monitoring_enabled,
                    "a_b_testing": config.a_b_testing_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"Model deployment failed: {e}")
            await self._cleanup_failed_model_deployment(config.model_name, config.model_version)
            raise
    
    async def _ensure_serving_namespace(self) -> None:
        """Create serving namespace"""
        try:
            self.k8s_core_v1.read_namespace(name=self.namespace)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                namespace_body = client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name=self.namespace,
                        labels={
                            "name": self.namespace,
                            "purpose": "model-serving",
                            "gpu-enabled": "true",
                            "high-performance": "true"
                        }
                    )
                )
                self.k8s_core_v1.create_namespace(body=namespace_body)
                logger.info(f"Created serving namespace: {self.namespace}")
    
    async def _deploy_serving_redis(self) -> Dict[str, Any]:
        """Deploy Redis cluster for serving metadata"""
        redis_cluster = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "serving-redis",
                "namespace": self.namespace,
                "labels": {"app": "serving-redis", "component": "cache"}
            },
            "spec": {
                "serviceName": "serving-redis",
                "replicas": 3,
                "selector": {"matchLabels": {"app": "serving-redis"}},
                "template": {
                    "metadata": {"labels": {"app": "serving-redis"}},
                    "spec": {
                        "containers": [{
                            "name": "redis",
                            "image": "redis:7-alpine",
                            "args": [
                                "redis-server",
                                "--maxmemory", "4gb",
                                "--maxmemory-policy", "allkeys-lru",
                                "--appendonly", "yes",
                                "--tcp-keepalive", "60",
                                "--timeout", "300"
                            ],
                            "ports": [{"containerPort": 6379}],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "2Gi"},
                                "limits": {"cpu": "1000m", "memory": "4Gi"}
                            },
                            "volumeMounts": [{
                                "name": "redis-data",
                                "mountPath": "/data"
                            }]
                        }]
                    }
                },
                "volumeClaimTemplates": [{
                    "metadata": {"name": "redis-data"},
                    "spec": {
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {"requests": {"storage": "50Gi"}},
                        "storageClassName": "fast-ssd"
                    }
                }]
            }
        }
        
        # Deploy Redis
        redis_deployment = self.k8s_apps_v1.create_namespaced_stateful_set(
            namespace=self.namespace,
            body=redis_cluster
        )
        
        return {
            "deployment_id": redis_deployment.metadata.uid,
            "service": "serving-redis",
            "replicas": 3
        }
    
    async def _deploy_load_balancer(self) -> Dict[str, Any]:
        """Deploy intelligent load balancer"""
        load_balancer = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "serving-load-balancer",
                "namespace": self.namespace,
                "labels": {"app": "load-balancer", "component": "routing"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "load-balancer"}},
                "template": {
                    "metadata": {"labels": {"app": "load-balancer"}},
                    "spec": {
                        "containers": [{
                            "name": "nginx",
                            "image": "ia-influencer/smart-load-balancer:v1.0",
                            "ports": [
                                {"containerPort": 80, "name": "http"},
                                {"containerPort": 443, "name": "https"}
                            ],
                            "env": [
                                {"name": "LOAD_BALANCING_ALGORITHM", "value": "weighted_response_time"},
                                {"name": "HEALTH_CHECK_INTERVAL", "value": "10"},
                                {"name": "CIRCUIT_BREAKER", "value": "true"},
                                {"name": "RATE_LIMITING", "value": "1000"},
                                {"name": "CONNECTION_POOLING", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "1Gi"},
                                "limits": {"cpu": "2000m", "memory": "4Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy load balancer
        lb_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=load_balancer
        )
        
        return {
            "deployment_id": lb_deployment.metadata.uid,
            "service": "serving-load-balancer",
            "features": ["intelligent_routing", "circuit_breaker", "rate_limiting"]
        }
    
    async def _deploy_serving_monitoring(self) -> Dict[str, Any]:
        """Deploy serving-specific monitoring"""
        serving_monitor = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "serving-monitor",
                "namespace": self.namespace,
                "labels": {"app": "serving-monitor", "component": "observability"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "serving-monitor"}},
                "template": {
                    "metadata": {"labels": {"app": "serving-monitor"}},
                    "spec": {
                        "containers": [{
                            "name": "monitor",
                            "image": "ia-influencer/serving-monitor:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "METRICS_COLLECTION", "value": "latency,throughput,error_rate,resource_usage"},
                                {"name": "ALERTING_ENABLED", "value": "true"},
                                {"name": "DASHBOARD_ENABLED", "value": "true"},
                                {"name": "MODEL_DRIFT_DETECTION", "value": "true"},
                                {"name": "PERFORMANCE_BASELINE", "value": "auto"}
                            ],
                            "resources": {
                                "requests": {"cpu": "300m", "memory": "512Mi"},
                                "limits": {"cpu": "1000m", "memory": "2Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy monitoring
        monitor_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=serving_monitor
        )
        
        return {
            "deployment_id": monitor_deployment.metadata.uid,
            "service": "serving-monitor",
            "features": ["performance_monitoring", "drift_detection", "alerting"]
        }
    
    async def _deploy_autoscaler(self) -> Dict[str, Any]:
        """Deploy intelligent autoscaler"""
        autoscaler = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "serving-autoscaler",
                "namespace": self.namespace,
                "labels": {"app": "autoscaler", "component": "scaling"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "autoscaler"}},
                "template": {
                    "metadata": {"labels": {"app": "autoscaler"}},
                    "spec": {
                        "containers": [{
                            "name": "autoscaler",
                            "image": "ia-influencer/smart-autoscaler:v1.0",
                            "env": [
                                {"name": "SCALING_STRATEGY", "value": "predictive"},
                                {"name": "MIN_SCALING_INTERVAL", "value": "30"},
                                {"name": "MAX_SCALING_INTERVAL", "value": "300"},
                                {"name": "CPU_TARGET", "value": "70"},
                                {"name": "MEMORY_TARGET", "value": "80"},
                                {"name": "QUEUE_LENGTH_TARGET", "value": "100"},
                                {"name": "RESPONSE_TIME_TARGET", "value": "100"}
                            ],
                            "resources": {
                                "requests": {"cpu": "200m", "memory": "256Mi"},
                                "limits": {"cpu": "500m", "memory": "1Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy autoscaler
        autoscaler_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=autoscaler
        )
        
        return {
            "deployment_id": autoscaler_deployment.metadata.uid,
            "service": "serving-autoscaler",
            "features": ["predictive_scaling", "multi_metric", "intelligent_policies"]
        }
    
    async def _deploy_traffic_manager(self) -> Dict[str, Any]:
        """Deploy traffic management system"""
        traffic_manager = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "traffic-manager",
                "namespace": self.namespace,
                "labels": {"app": "traffic-manager", "component": "routing"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "traffic-manager"}},
                "template": {
                    "metadata": {"labels": {"app": "traffic-manager"}},
                    "spec": {
                        "containers": [{
                            "name": "traffic-manager",
                            "image": "ia-influencer/traffic-manager:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "ROUTING_STRATEGIES", "value": "blue_green,canary,a_b_testing"},
                                {"name": "TRAFFIC_SPLITTING", "value": "true"},
                                {"name": "GRADUAL_ROLLOUT", "value": "true"},
                                {"name": "ROLLBACK_AUTOMATION", "value": "true"},
                                {"name": "CIRCUIT_BREAKER", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "300m", "memory": "512Mi"},
                                "limits": {"cpu": "1000m", "memory": "2Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy traffic manager
        tm_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=traffic_manager
        )
        
        self.traffic_manager = tm_deployment.metadata.uid
        
        return {
            "deployment_id": tm_deployment.metadata.uid,
            "service": "traffic-manager",
            "features": ["traffic_splitting", "gradual_rollout", "automated_rollback"]
        }
    
    async def _deploy_tensorflow_serving(self) -> Dict[str, Any]:
        """Deploy TensorFlow Serving engine"""
        tf_serving = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "tensorflow-serving-engine",
                "namespace": self.namespace,
                "labels": {"app": "tensorflow-serving", "framework": "tensorflow"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "tensorflow-serving"}},
                "template": {
                    "metadata": {"labels": {"app": "tensorflow-serving"}},
                    "spec": {
                        "containers": [{
                            "name": "tf-serving",
                            "image": "tensorflow/serving:latest-gpu",
                            "ports": [
                                {"containerPort": 8500, "name": "grpc"},
                                {"containerPort": 8501, "name": "rest"}
                            ],
                            "env": [
                                {"name": "MODEL_CONFIG_FILE", "value": "/models/models.config"},
                                {"name": "MONITORING_CONFIG_FILE", "value": "/models/monitoring.config"},
                                {"name": "TENSORFLOW_INTER_OP_PARALLELISM", "value": "0"},
                                {"name": "TENSORFLOW_INTRA_OP_PARALLELISM", "value": "0"},
                                {"name": "TF_CPP_MIN_LOG_LEVEL", "value": "1"}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "1000m",
                                    "memory": "2Gi",
                                    "nvidia.com/gpu": "1"
                                },
                                "limits": {
                                    "cpu": "4000m",
                                    "memory": "8Gi",
                                    "nvidia.com/gpu": "2"
                                }
                            },
                            "volumeMounts": [{
                                "name": "model-storage",
                                "mountPath": "/models"
                            }]
                        }],
                        "volumes": [{
                            "name": "model-storage",
                            "persistentVolumeClaim": {"claimName": "tf-model-storage"}
                        }],
                        "nodeSelector": {"accelerator": "nvidia-tesla-v100"}
                    }
                }
            }
        }
        
        # Deploy TensorFlow Serving
        tf_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=tf_serving
        )
        
        return {
            "deployment_id": tf_deployment.metadata.uid,
            "service": "tensorflow-serving-engine",
            "framework": "tensorflow",
            "features": ["gpu_acceleration", "grpc_rest_api", "model_versioning"]
        }
    
    async def _deploy_pytorch_serving(self) -> Dict[str, Any]:
        """Deploy PyTorch Serving engine (TorchServe)"""
        torch_serving = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "pytorch-serving-engine",
                "namespace": self.namespace,
                "labels": {"app": "pytorch-serving", "framework": "pytorch"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "pytorch-serving"}},
                "template": {
                    "metadata": {"labels": {"app": "pytorch-serving"}},
                    "spec": {
                        "containers": [{
                            "name": "torchserve",
                            "image": "pytorch/torchserve:latest-gpu",
                            "ports": [
                                {"containerPort": 8080, "name": "inference"},
                                {"containerPort": 8081, "name": "management"},
                                {"containerPort": 8082, "name": "metrics"}
                            ],
                            "env": [
                                {"name": "TORCH_MODEL_STORE", "value": "/models"},
                                {"name": "TORCH_INFERENCE_ADDRESS", "value": "http://0.0.0.0:8080"},
                                {"name": "TORCH_MANAGEMENT_ADDRESS", "value": "http://0.0.0.0:8081"},
                                {"name": "TORCH_METRICS_ADDRESS", "value": "http://0.0.0.0:8082"},
                                {"name": "TS_NUMBER_OF_GPU", "value": "2"}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "1000m",
                                    "memory": "2Gi",
                                    "nvidia.com/gpu": "1"
                                },
                                "limits": {
                                    "cpu": "4000m",
                                    "memory": "8Gi",
                                    "nvidia.com/gpu": "2"
                                }
                            },
                            "volumeMounts": [{
                                "name": "model-storage",
                                "mountPath": "/models"
                            }]
                        }],
                        "volumes": [{
                            "name": "model-storage",
                            "persistentVolumeClaim": {"claimName": "torch-model-storage"}
                        }]
                    }
                }
            }
        }
        
        # Deploy PyTorch Serving
        torch_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=torch_serving
        )
        
        return {
            "deployment_id": torch_deployment.metadata.uid,
            "service": "pytorch-serving-engine",
            "framework": "pytorch",
            "features": ["gpu_acceleration", "management_api", "metrics_endpoint"]
        }
    
    async def _deploy_onnx_serving(self) -> Dict[str, Any]:
        """Deploy ONNX Runtime serving engine"""
        onnx_serving = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "onnx-serving-engine",
                "namespace": self.namespace,
                "labels": {"app": "onnx-serving", "framework": "onnx"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "onnx-serving"}},
                "template": {
                    "metadata": {"labels": {"app": "onnx-serving"}},
                    "spec": {
                        "containers": [{
                            "name": "onnx-runtime",
                            "image": "ia-influencer/onnx-serving:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "ONNX_MODEL_PATH", "value": "/models"},
                                {"name": "EXECUTION_PROVIDERS", "value": "CUDAExecutionProvider,CPUExecutionProvider"},
                                {"name": "INTRA_OP_NUM_THREADS", "value": "0"},
                                {"name": "INTER_OP_NUM_THREADS", "value": "0"},
                                {"name": "OPTIMIZATION_LEVEL", "value": "all"}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "500m",
                                    "memory": "1Gi",
                                    "nvidia.com/gpu": "1"
                                },
                                "limits": {
                                    "cpu": "2000m",
                                    "memory": "4Gi",
                                    "nvidia.com/gpu": "1"
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy ONNX serving
        onnx_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=onnx_serving
        )
        
        return {
            "deployment_id": onnx_deployment.metadata.uid,
            "service": "onnx-serving-engine",
            "framework": "onnx",
            "features": ["cross_platform", "optimization", "gpu_cpu_support"]
        }
    
    async def _deploy_huggingface_serving(self) -> Dict[str, Any]:
        """Deploy Hugging Face model serving"""
        hf_serving = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "huggingface-serving-engine",
                "namespace": self.namespace,
                "labels": {"app": "huggingface-serving", "framework": "huggingface"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "huggingface-serving"}},
                "template": {
                    "metadata": {"labels": {"app": "huggingface-serving"}},
                    "spec": {
                        "containers": [{
                            "name": "hf-serving",
                            "image": "ia-influencer/hf-serving:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "TRANSFORMERS_CACHE", "value": "/models/cache"},
                                {"name": "HF_MODEL_DIR", "value": "/models/huggingface"},
                                {"name": "CUDA_VISIBLE_DEVICES", "value": "0,1"},
                                {"name": "MAX_SEQUENCE_LENGTH", "value": "512"},
                                {"name": "BATCH_SIZE", "value": "16"}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "1000m",
                                    "memory": "4Gi",
                                    "nvidia.com/gpu": "1"
                                },
                                "limits": {
                                    "cpu": "4000m",
                                    "memory": "16Gi",
                                    "nvidia.com/gpu": "2"
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy Hugging Face serving
        hf_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=hf_serving
        )
        
        return {
            "deployment_id": hf_deployment.metadata.uid,
            "service": "huggingface-serving-engine",
            "framework": "huggingface",
            "features": ["transformer_models", "nlp_optimized", "model_hub_integration"]
        }
    
    async def _deploy_edge_serving(self) -> Dict[str, Any]:
        """Deploy edge computing serving infrastructure"""
        edge_serving = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "edge-serving-engine",
                "namespace": self.namespace,
                "labels": {"app": "edge-serving", "compute": "edge"}
            },
            "spec": {
                "replicas": 5,
                "selector": {"matchLabels": {"app": "edge-serving"}},
                "template": {
                    "metadata": {"labels": {"app": "edge-serving"}},
                    "spec": {
                        "containers": [{
                            "name": "edge-runtime",
                            "image": "ia-influencer/edge-runtime:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "RUNTIME_TYPE", "value": "lightweight"},
                                {"name": "MODEL_FORMAT", "value": "onnx"},
                                {"name": "QUANTIZATION", "value": "int8"},
                                {"name": "CACHE_SIZE", "value": "256MB"},
                                {"name": "MAX_CONCURRENT", "value": "50"}
                            ],
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "128Mi"},
                                "limits": {"cpu": "500m", "memory": "512Mi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy edge serving
        edge_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=edge_serving
        )
        
        return {
            "deployment_id": edge_deployment.metadata.uid,
            "service": "edge-serving-engine",
            "compute": "edge",
            "features": ["lightweight", "quantization", "low_latency"]
        }
    
    async def _configure_serving_networking(self) -> None:
        """Configure networking for serving infrastructure"""
        # Serving network policy
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "serving-network-policy",
                "namespace": self.namespace
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {"namespaceSelector": {"matchLabels": {"name": "ia-influencer"}}},
                            {"podSelector": {"matchLabels": {"app": "load-balancer"}}}
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
            namespace=self.namespace,
            body=network_policy
        )
        
        logger.info("Configured serving networking policies")
    
    async def _validate_serving_infrastructure(self) -> bool:
        """Validate serving infrastructure deployment"""
        try:
            # Check essential services
            essential_services = [
                "serving-redis", "serving-load-balancer", "serving-monitor",
                "serving-autoscaler", "traffic-manager"
            ]
            
            for service in essential_services:
                try:
                    deployment = self.k8s_apps_v1.read_namespaced_deployment(
                        name=service,
                        namespace=self.namespace
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
                logger.info("Serving Redis connectivity validated")
            except Exception as e:
                logger.error(f"Redis validation failed: {e}")
                return False
            
            logger.info("Serving infrastructure validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Infrastructure validation failed: {e}")
            return False
    
    async def _validate_model_config(self, config: ModelServingConfig) -> None:
        """Validate model serving configuration"""
        if not config.model_name or not config.model_version:
            raise ValueError("Model name and version are required")
        
        if config.replicas < 1:
            raise ValueError("Replicas must be at least 1")
        
        if config.max_latency_ms <= 0:
            raise ValueError("Max latency must be positive")
        
        if config.batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        logger.info(f"Model config validation passed for {config.model_name}")
    
    async def _create_model_deployment_spec(self, config: ModelServingConfig) -> Dict[str, Any]:
        """Create Kubernetes deployment specification for model"""
        model_id = f"{config.model_name}-{config.model_version}"
        
        deployment_spec = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"model-{model_id}",
                "namespace": self.namespace,
                "labels": {
                    "app": f"model-{model_id}",
                    "model-name": config.model_name,
                    "model-version": config.model_version,
                    "framework": config.model_format.value,
                    "serving-mode": config.serving_mode.value
                }
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {"matchLabels": {"app": f"model-{model_id}"}},
                "template": {
                    "metadata": {
                        "labels": {"app": f"model-{model_id}"},
                        "annotations": {
                            "model-config": json.dumps({
                                "name": config.model_name,
                                "version": config.model_version,
                                "format": config.model_format.value,
                                "batch_size": config.batch_size,
                                "max_latency_ms": config.max_latency_ms
                            })
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "model-server",
                            "image": f"ia-influencer/model-server:{config.model_format.value}",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "MODEL_NAME", "value": config.model_name},
                                {"name": "MODEL_VERSION", "value": config.model_version},
                                {"name": "BATCH_SIZE", "value": str(config.batch_size)},
                                {"name": "MAX_LATENCY_MS", "value": str(config.max_latency_ms)},
                                {"name": "GPU_ENABLED", "value": str(config.gpu_acceleration).lower()},
                                {"name": "GPU_MEMORY_FRACTION", "value": str(config.gpu_memory_fraction)}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "1000m",
                                    "memory": "2Gi"
                                },
                                "limits": {
                                    "cpu": "4000m",
                                    "memory": "8Gi"
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
        if config.gpu_acceleration:
            deployment_spec["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["nvidia.com/gpu"] = "1"
            deployment_spec["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"] = "2"
            deployment_spec["spec"]["template"]["spec"]["nodeSelector"] = {"accelerator": "nvidia-tesla-v100"}
        
        return deployment_spec
    
    async def _deploy_tensorflow_model(self, config: ModelServingConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy TensorFlow model"""
        # Customize for TensorFlow
        container = deployment_spec["spec"]["template"]["spec"]["containers"][0]
        container["image"] = "tensorflow/serving:latest-gpu" if config.gpu_acceleration else "tensorflow/serving:latest"
        container["ports"] = [
            {"containerPort": 8500, "name": "grpc"},
            {"containerPort": 8501, "name": "rest"}
        ]
        container["env"].extend([
            {"name": "MODEL_CONFIG_FILE", "value": f"/models/{config.model_name}/config"},
            {"name": "TENSORFLOW_INTER_OP_PARALLELISM", "value": "0"},
            {"name": "TENSORFLOW_INTRA_OP_PARALLELISM", "value": "0"}
        ])
        
        # Deploy model
        deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_spec
        )
        
        return {
            "deployment_id": deployment.metadata.uid,
            "framework": "tensorflow",
            "endpoints": [
                f"grpc://{deployment.metadata.name}:8500",
                f"http://{deployment.metadata.name}:8501"
            ]
        }
    
    async def _deploy_pytorch_model(self, config: ModelServingConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy PyTorch model"""
        # Customize for PyTorch
        container = deployment_spec["spec"]["template"]["spec"]["containers"][0]
        container["image"] = "pytorch/torchserve:latest-gpu" if config.gpu_acceleration else "pytorch/torchserve:latest"
        container["ports"] = [
            {"containerPort": 8080, "name": "inference"},
            {"containerPort": 8081, "name": "management"}
        ]
        container["env"].extend([
            {"name": "TORCH_MODEL_STORE", "value": f"/models/{config.model_name}"},
            {"name": "TORCH_INFERENCE_ADDRESS", "value": "http://0.0.0.0:8080"},
            {"name": "TORCH_MANAGEMENT_ADDRESS", "value": "http://0.0.0.0:8081"}
        ])
        
        # Deploy model
        deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_spec
        )
        
        return {
            "deployment_id": deployment.metadata.uid,
            "framework": "pytorch",
            "endpoints": [
                f"http://{deployment.metadata.name}:8080",
                f"http://{deployment.metadata.name}:8081"
            ]
        }
    
    async def _deploy_onnx_model(self, config: ModelServingConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy ONNX model"""
        # Customize for ONNX
        container = deployment_spec["spec"]["template"]["spec"]["containers"][0]
        container["image"] = "ia-influencer/onnx-serving:v1.0"
        container["env"].extend([
            {"name": "ONNX_MODEL_PATH", "value": f"/models/{config.model_name}/{config.model_version}"},
            {"name": "EXECUTION_PROVIDERS", "value": "CUDAExecutionProvider,CPUExecutionProvider" if config.gpu_acceleration else "CPUExecutionProvider"}
        ])
        
        # Deploy model
        deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_spec
        )
        
        return {
            "deployment_id": deployment.metadata.uid,
            "framework": "onnx",
            "endpoints": [f"http://{deployment.metadata.name}:8080"]
        }
    
    async def _deploy_huggingface_model(self, config: ModelServingConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy Hugging Face model"""
        # Customize for Hugging Face
        container = deployment_spec["spec"]["template"]["spec"]["containers"][0]
        container["image"] = "ia-influencer/hf-serving:v1.0"
        container["env"].extend([
            {"name": "HF_MODEL_ID", "value": config.model_name},
            {"name": "HF_MODEL_REVISION", "value": config.model_version},
            {"name": "TRANSFORMERS_CACHE", "value": "/models/cache"}
        ])
        
        # Deploy model
        deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_spec
        )
        
        return {
            "deployment_id": deployment.metadata.uid,
            "framework": "huggingface",
            "endpoints": [f"http://{deployment.metadata.name}:8080"]
        }
    
    async def _deploy_custom_model(self, config: ModelServingConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy custom model format"""
        # Deploy as-is for custom models
        deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_spec
        )
        
        return {
            "deployment_id": deployment.metadata.uid,
            "framework": "custom",
            "endpoints": [f"http://{deployment.metadata.name}:8080"]
        }
    
    async def _configure_model_autoscaling(self, config: ModelServingConfig) -> None:
        """Configure autoscaling for model"""
        model_id = f"{config.model_name}-{config.model_version}"
        
        hpa_spec = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"hpa-model-{model_id}",
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"model-{model_id}"
                },
                "minReplicas": config.min_replicas,
                "maxReplicas": config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": config.target_cpu_utilization
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": config.target_memory_utilization
                            }
                        }
                    }
                ]
            }
        }
        
        self.k8s_autoscaling_v2.create_namespaced_horizontal_pod_autoscaler(
            namespace=self.namespace,
            body=hpa_spec
        )
        
        logger.info(f"Configured autoscaling for model {model_id}")
    
    async def _configure_traffic_routing(self, config: ModelServingConfig) -> None:
        """Configure traffic routing for model"""
        model_id = f"{config.model_name}-{config.model_version}"
        
        # Create service for model
        service_spec = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"service-model-{model_id}",
                "namespace": self.namespace,
                "labels": {
                    "model-name": config.model_name,
                    "model-version": config.model_version
                }
            },
            "spec": {
                "selector": {"app": f"model-{model_id}"},
                "ports": [{"port": 8080, "targetPort": 8080}],
                "type": "ClusterIP"
            }
        }
        
        self.k8s_core_v1.create_namespaced_service(
            namespace=self.namespace,
            body=service_spec
        )
        
        logger.info(f"Configured traffic routing for model {model_id}")
    
    async def _setup_model_monitoring(self, config: ModelServingConfig) -> None:
        """Set up monitoring for model"""
        model_id = f"{config.model_name}-{config.model_version}"
        
        # Store monitoring configuration in Redis
        monitoring_config = {
            "model_id": model_id,
            "metrics": ["latency", "throughput", "error_rate", "resource_usage"],
            "alerting": True,
            "dashboard": True,
            "drift_detection": True
        }
        
        self._redis_client.hset(
            f"model:monitoring:{model_id}",
            mapping=monitoring_config
        )
        
        logger.info(f"Configured monitoring for model {model_id}")
    
    async def _setup_ab_testing(self, config: ModelServingConfig) -> None:
        """Set up A/B testing for model"""
        model_id = f"{config.model_name}-{config.model_version}"
        
        # Store A/B testing configuration
        ab_config = {
            "model_id": model_id,
            "traffic_split": config.traffic_split,
            "enabled": True,
            "metrics": ["accuracy", "latency", "user_satisfaction"]
        }
        
        self._redis_client.hset(
            f"model:ab_testing:{model_id}",
            mapping=ab_config
        )
        
        logger.info(f"Configured A/B testing for model {model_id}")
    
    async def _cleanup_failed_infrastructure(self) -> None:
        """Clean up failed infrastructure deployment"""
        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            logger.info("Cleaned up failed serving infrastructure")
        except Exception as e:
            logger.error(f"Infrastructure cleanup failed: {e}")
    
    async def _cleanup_failed_model_deployment(self, model_name: str, model_version: str) -> None:
        """Clean up failed model deployment"""
        try:
            model_id = f"{model_name}-{model_version}"
            
            # Delete deployment
            try:
                self.k8s_apps_v1.delete_namespaced_deployment(
                    name=f"model-{model_id}",
                    namespace=self.namespace
                )
            except:
                pass
            
            # Delete service
            try:
                self.k8s_core_v1.delete_namespaced_service(
                    name=f"service-model-{model_id}",
                    namespace=self.namespace
                )
            except:
                pass
            
            # Delete HPA
            try:
                self.k8s_autoscaling_v2.delete_namespaced_horizontal_pod_autoscaler(
                    name=f"hpa-model-{model_id}",
                    namespace=self.namespace
                )
            except:
                pass
            
            logger.info(f"Cleaned up failed model deployment: {model_id}")
            
        except Exception as e:
            logger.error(f"Model cleanup failed: {e}")
    
    async def get_serving_metrics(self) -> Dict[str, Any]:
        """Get comprehensive serving metrics"""
        try:
            metrics = {
                "infrastructure_status": self.status,
                "deployed_models": len(self.deployed_models),
                "serving_instances": len(self.serving_instances),
                "total_requests_24h": self._redis_client.get("total_requests_24h") or "0",
                "average_latency": self._redis_client.get("average_latency") or "0",
                "error_rate": self._redis_client.get("error_rate") or "0",
                "gpu_utilization": self._redis_client.get("gpu_utilization") or "0",
                "models": {}
            }
            
            # Get per-model metrics
            for model_id, model_info in self.deployed_models.items():
                model_metrics = {
                    "status": model_info["status"],
                    "deployed_at": model_info["deployed_at"],
                    "endpoints": model_info["endpoints"],
                    "requests_24h": self._redis_client.get(f"model:requests:{model_id}") or "0",
                    "latency": self._redis_client.get(f"model:latency:{model_id}") or "0",
                    "error_rate": self._redis_client.get(f"model:error_rate:{model_id}") or "0"
                }
                metrics["models"][model_id] = model_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get serving metrics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Clean up entire serving infrastructure"""
        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            
            self.status = "stopped"
            self.deployed_models = {}
            self.serving_instances = {}
            
            logger.info("Model serving infrastructure cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Serving cleanup failed: {e}")
            raise
