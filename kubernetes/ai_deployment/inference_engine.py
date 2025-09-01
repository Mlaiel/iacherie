"""Inference Engine Deployment
Enterprise real-time inference infrastructure

This module provides high-performance inference engines for
real-time model predictions with auto-scaling, caching,
and optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
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
import time

logger = logging.getLogger(__name__)


class InferenceType(Enum):
    """
Inference types"""

    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    EDGE = "edge"
    SERVERLESS = "serverless"


class OptimizationLevel(Enum):
    """Optimization levels"""

    SPEED = "speed"
    ACCURACY = "accuracy"
    BALANCED = "balanced"
    MEMORY = "memory"
    THROUGHPUT = "throughput"


class CachingStrategy(Enum):
    """Caching strategies"""

    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    ADAPTIVE = "adaptive"
    NONE = "none"


@dataclass
class InferenceEngineConfig:
    """Inference engine configuration"""
    engine_name: str
    model_name: str
    model_version: str
    inference_type: InferenceType = InferenceType.REAL_TIME
    optimization_level: OptimizationLevel = OptimizationLevel.BALANCED
    caching_strategy: CachingStrategy = CachingStrategy.LRU
    replicas: int = 3
    min_replicas: int = 2
    max_replicas: int = 20
    target_latency_ms: int = 100
    max_throughput_rps: int = 1000
    batch_size: int = 32
    max_batch_delay_ms: int = 50
    auto_scaling: bool = True
    gpu_acceleration: bool = True
    quantization: bool = False
    model_caching: bool = True
    request_caching: bool = True
    cache_ttl_seconds: int = 3600
    circuit_breaker: bool = True
    rate_limiting: bool = True
    monitoring: bool = True
    
    def __post_init__(self):
        if self.target_latency_ms <= 0:
            self.target_latency_ms = 100
        if self.max_throughput_rps <= 0:
            self.max_throughput_rps = 1000


class InferenceEngineDeployment:
    """
    Enterprise inference engine deployment system
    
    Provides high-performance inference capabilities with:
    - Real-time and batch inference
    - Auto-scaling and load balancing
    - Intelligent caching and optimization
    - GPU acceleration and quantization
    - Circuit breakers and rate limiting
    - Comprehensive monitoring and observability
    """
    
    def __init__(self, namespace: str = "ia-influencer-inference"):
        """
        Initialize inference engine deployment
        
        Args:
            namespace: Kubernetes namespace for inference infrastructure
        """
        self.namespace = namespace
        self.deployed_engines = {}
        self.inference_metrics = {}
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
            self.k8s_autoscaling_v2 = client.AutoscalingV2Api()
            self.k8s_networking_v1 = client.NetworkingV1Api()
            
            # Docker client for inference images
            self._docker_client = docker.from_env()
            
            # Redis for inference caching and metadata
            self._redis_client = redis.Redis(
                host='inference-redis',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            logger.info("Inference engine clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize inference clients: {e}")
            raise
    
    async def deploy_inference_infrastructure(self) -> Dict[str, Any]:
        """
        Deploy complete inference infrastructure
        
        Returns:
            Infrastructure deployment summary
        """
        try:
            self.status = "deploying_infrastructure"
            logger.info("Deploying inference infrastructure")
            
            # Create inference namespace
            await self._ensure_inference_namespace()
            
            # Deploy core infrastructure
            redis_result = await self._deploy_inference_redis()
            load_balancer_result = await self._deploy_inference_load_balancer()
            cache_manager_result = await self._deploy_cache_manager()
            
            # Deploy optimization services
            optimizer_result = await self._deploy_inference_optimizer()
            quantizer_result = await self._deploy_model_quantizer()
            
            # Deploy monitoring and observability
            monitoring_result = await self._deploy_inference_monitoring()
            
            # Deploy rate limiting and circuit breaker
            rate_limiter_result = await self._deploy_rate_limiter()
            circuit_breaker_result = await self._deploy_circuit_breaker()
            
            # Deploy auto-scaler
            autoscaler_result = await self._deploy_inference_autoscaler()
            
            # Configure networking
            await self._configure_inference_networking()
            
            # Validate infrastructure
            if await self._validate_inference_infrastructure():
                self.status = "infrastructure_ready"
                logger.info("Inference infrastructure deployed successfully")
                
                return {
                    "status": "success",
                    "infrastructure": {
                        "redis": redis_result,
                        "load_balancer": load_balancer_result,
                        "cache_manager": cache_manager_result,
                        "optimizer": optimizer_result,
                        "quantizer": quantizer_result,
                        "monitoring": monitoring_result,
                        "rate_limiter": rate_limiter_result,
                        "circuit_breaker": circuit_breaker_result,
                        "autoscaler": autoscaler_result
                    },
                    "capabilities": {
                        "inference_types": [t.value for t in InferenceType],
                        "optimization_levels": [o.value for o in OptimizationLevel],
                        "caching_strategies": [c.value for c in CachingStrategy],
                        "auto_scaling": True,
                        "gpu_acceleration": True,
                        "quantization": True,
                        "intelligent_caching": True
                    }
                }
            else:
                raise Exception("Inference infrastructure validation failed")
                
        except Exception as e:
            self.status = "infrastructure_failed"
            logger.error(f"Inference infrastructure deployment failed: {e}")
            await self._cleanup_failed_infrastructure()
            raise
    
    async def deploy_inference_engine(self, config: InferenceEngineConfig) -> Dict[str, Any]:
        """
        Deploy an inference engine
        
        Args:
            config: Inference engine configuration
            
        Returns:
            Engine deployment result
        """
        try:
            engine_id = f"{config.engine_name}-{config.model_version}"
            logger.info(f"Deploying inference engine: {engine_id}")
            
            # Validate configuration
            await self._validate_inference_config(config)
            
            # Create deployment specification
            deployment_spec = await self._create_inference_deployment_spec(config)
            
            # Deploy based on inference type
            if config.inference_type == InferenceType.REAL_TIME:
                deployment_result = await self._deploy_realtime_engine(config, deployment_spec)
            elif config.inference_type == InferenceType.BATCH:
                deployment_result = await self._deploy_batch_engine(config, deployment_spec)
            elif config.inference_type == InferenceType.STREAMING:
                deployment_result = await self._deploy_streaming_engine(config, deployment_spec)
            elif config.inference_type == InferenceType.EDGE:
                deployment_result = await self._deploy_edge_engine(config, deployment_spec)
            else:
                deployment_result = await self._deploy_serverless_engine(config, deployment_spec)
            
            # Configure auto-scaling
            if config.auto_scaling:
                await self._configure_engine_autoscaling(config)
            
            # Set up caching
            if config.model_caching or config.request_caching:
                await self._setup_inference_caching(config)
            
            # Configure monitoring
            if config.monitoring:
                await self._setup_inference_monitoring(config)
            
            # Set up rate limiting
            if config.rate_limiting:
                await self._setup_rate_limiting(config)
            
            # Configure circuit breaker
            if config.circuit_breaker:
                await self._setup_circuit_breaker(config)
            
            # Store deployment information
            self.deployed_engines[engine_id] = {
                "config": config,
                "deployment_result": deployment_result,
                "status": "deployed",
                "deployed_at": datetime.utcnow().isoformat(),
                "endpoints": deployment_result.get("endpoints", [])
            }
            
            logger.info(f"Inference engine {engine_id} deployed successfully")
            
            return {
                "status": "success",
                "engine_id": engine_id,
                "deployment_result": deployment_result,
                "endpoints": deployment_result.get("endpoints", []),
                "performance_targets": {
                    "latency": f"< {config.target_latency_ms}ms",
                    "throughput": f"> {config.max_throughput_rps} RPS",
                    "uptime": "99.99%",
                    "accuracy": "maintained"
                }
            }
            
        except Exception as e:
            logger.error(f"Inference engine deployment failed: {e}")
            await self._cleanup_failed_engine_deployment(config.engine_name)
            raise
    
    async def _ensure_inference_namespace(self) -> None:
        """Create inference namespace"""
        try:
            self.k8s_core_v1.read_namespace(name=self.namespace)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                namespace_body = client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name=self.namespace,
                        labels={
                            "name": self.namespace,
                            "purpose": "inference",
                            "real-time": "true",
                            "high-performance": "true"
                        }
                    )
                )
                self.k8s_core_v1.create_namespace(body=namespace_body)
                logger.info(f"Created inference namespace: {self.namespace}")
    
    async def _deploy_inference_redis(self) -> Dict[str, Any]:
        """Deploy Redis cluster for inference caching"""
        redis_cluster = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "inference-redis",
                "namespace": self.namespace,
                "labels": {"app": "inference-redis", "component": "cache"}
            },
            "spec": {
                "serviceName": "inference-redis",
                "replicas": 3,
                "selector": {"matchLabels": {"app": "inference-redis"}},
                "template": {
                    "metadata": {"labels": {"app": "inference-redis"}},
                    "spec": {
                        "containers": [{
                            "name": "redis",
                            "image": "redis:7-alpine",
                            "args": [
                                "redis-server",
                                "--maxmemory", "16gb",
                                "--maxmemory-policy", "allkeys-lru",
                                "--tcp-keepalive", "60",
                                "--timeout", "300",
                                "--save", ""  # Disable persistence for cache
                            ],
                            "ports": [{"containerPort": 6379}],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "8Gi"},
                                "limits": {"cpu": "2000m", "memory": "16Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy Redis
        redis_deployment = self.k8s_apps_v1.create_namespaced_stateful_set(
            namespace=self.namespace,
            body=redis_cluster
        )
        
        return {
            "deployment_id": redis_deployment.metadata.uid,
            "service": "inference-redis",
            "replicas": 3,
            "features": ["high_memory", "low_latency", "clustering"]
        }
    
    async def _deploy_inference_load_balancer(self) -> Dict[str, Any]:
        """Deploy intelligent load balancer for inference"""
        load_balancer = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "inference-load-balancer",
                "namespace": self.namespace,
                "labels": {"app": "inference-lb", "component": "routing"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "inference-lb"}},
                "template": {
                    "metadata": {"labels": {"app": "inference-lb"}},
                    "spec": {
                        "containers": [{
                            "name": "nginx-plus",
                            "image": "ia-influencer/inference-lb:v1.0",
                            "ports": [
                                {"containerPort": 80, "name": "http"},
                                {"containerPort": 443, "name": "https"}
                            ],
                            "env": [
                                {"name": "LB_ALGORITHM", "value": "least_response_time"},
                                {"name": "HEALTH_CHECK_INTERVAL", "value": "5"},
                                {"name": "SESSION_PERSISTENCE", "value": "false"},
                                {"name": "CONNECTION_POOLING", "value": "true"},
                                {"name": "KEEP_ALIVE", "value": "300"}
                            ],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "2Gi"},
                                "limits": {"cpu": "3000m", "memory": "6Gi"}
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
            "service": "inference-load-balancer",
            "features": ["intelligent_routing", "health_checks", "connection_pooling"]
        }
    
    async def _deploy_cache_manager(self) -> Dict[str, Any]:
        """Deploy intelligent cache manager"""
        cache_manager = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "cache-manager",
                "namespace": self.namespace,
                "labels": {"app": "cache-manager", "component": "optimization"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "cache-manager"}},
                "template": {
                    "metadata": {"labels": {"app": "cache-manager"}},
                    "spec": {
                        "containers": [{
                            "name": "cache-manager",
                            "image": "ia-influencer/cache-manager:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "CACHE_STRATEGIES", "value": "lru,lfu,adaptive"},
                                {"name": "CACHE_WARMING", "value": "true"},
                                {"name": "PREFETCH_ENABLED", "value": "true"},
                                {"name": "CACHE_COMPRESSION", "value": "true"},
                                {"name": "CACHE_ANALYTICS", "value": "true"}
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
        
        # Deploy cache manager
        cache_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=cache_manager
        )
        
        return {
            "deployment_id": cache_deployment.metadata.uid,
            "service": "cache-manager",
            "features": ["intelligent_caching", "cache_warming", "prefetching"]
        }
    
    async def _deploy_inference_optimizer(self) -> Dict[str, Any]:
        """Deploy inference optimizer"""
        optimizer = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "inference-optimizer",
                "namespace": self.namespace,
                "labels": {"app": "inference-optimizer", "component": "optimization"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "inference-optimizer"}},
                "template": {
                    "metadata": {"labels": {"app": "inference-optimizer"}},
                    "spec": {
                        "containers": [{
                            "name": "optimizer",
                            "image": "ia-influencer/inference-optimizer:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "OPTIMIZATION_TECHNIQUES", "value": "tensorrt,onnx,openvino"},
                                {"name": "AUTO_OPTIMIZATION", "value": "true"},
                                {"name": "GRAPH_OPTIMIZATION", "value": "true"},
                                {"name": "KERNEL_FUSION", "value": "true"},
                                {"name": "MEMORY_OPTIMIZATION", "value": "true"}
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
        
        # Deploy optimizer
        optimizer_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=optimizer
        )
        
        return {
            "deployment_id": optimizer_deployment.metadata.uid,
            "service": "inference-optimizer",
            "features": ["tensorrt", "onnx", "openvino", "graph_optimization"]
        }
    
    async def _deploy_model_quantizer(self) -> Dict[str, Any]:
        """Deploy model quantization service"""
        quantizer = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "model-quantizer",
                "namespace": self.namespace,
                "labels": {"app": "model-quantizer", "component": "optimization"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "model-quantizer"}},
                "template": {
                    "metadata": {"labels": {"app": "model-quantizer"}},
                    "spec": {
                        "containers": [{
                            "name": "quantizer",
                            "image": "ia-influencer/model-quantizer:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "QUANTIZATION_METHODS", "value": "int8,fp16,dynamic"},
                                {"name": "CALIBRATION_ENABLED", "value": "true"},
                                {"name": "ACCURACY_VALIDATION", "value": "true"},
                                {"name": "PERFORMANCE_PROFILING", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "2000m", "memory": "8Gi"},
                                "limits": {"cpu": "8000m", "memory": "32Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy quantizer
        quantizer_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=quantizer
        )
        
        return {
            "deployment_id": quantizer_deployment.metadata.uid,
            "service": "model-quantizer",
            "features": ["int8_quantization", "fp16_precision", "dynamic_quantization"]
        }
    
    async def _deploy_inference_monitoring(self) -> Dict[str, Any]:
        """Deploy inference monitoring system"""
        monitor = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "inference-monitor",
                "namespace": self.namespace,
                "labels": {"app": "inference-monitor", "component": "observability"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "inference-monitor"}},
                "template": {
                    "metadata": {"labels": {"app": "inference-monitor"}},
                    "spec": {
                        "containers": [{
                            "name": "monitor",
                            "image": "ia-influencer/inference-monitor:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "METRICS", "value": "latency,throughput,accuracy,gpu_utilization,memory"},
                                {"name": "REAL_TIME_ALERTS", "value": "true"},
                                {"name": "ANOMALY_DETECTION", "value": "true"},
                                {"name": "PERFORMANCE_PROFILING", "value": "true"},
                                {"name": "DASHBOARD_ENABLED", "value": "true"}
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
        
        # Deploy monitor
        monitor_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=monitor
        )
        
        return {
            "deployment_id": monitor_deployment.metadata.uid,
            "service": "inference-monitor",
            "features": ["real_time_metrics", "anomaly_detection", "performance_profiling"]
        }
    
    async def _deploy_rate_limiter(self) -> Dict[str, Any]:
        """Deploy rate limiting service"""
        rate_limiter = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "rate-limiter",
                "namespace": self.namespace,
                "labels": {"app": "rate-limiter", "component": "protection"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "rate-limiter"}},
                "template": {
                    "metadata": {"labels": {"app": "rate-limiter"}},
                    "spec": {
                        "containers": [{
                            "name": "rate-limiter",
                            "image": "ia-influencer/rate-limiter:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "ALGORITHMS", "value": "token_bucket,sliding_window,fixed_window"},
                                {"name": "ADAPTIVE_LIMITING", "value": "true"},
                                {"name": "USER_QUOTAS", "value": "true"},
                                {"name": "BURST_HANDLING", "value": "true"}
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
        
        # Deploy rate limiter
        limiter_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=rate_limiter
        )
        
        return {
            "deployment_id": limiter_deployment.metadata.uid,
            "service": "rate-limiter",
            "features": ["adaptive_limiting", "user_quotas", "burst_handling"]
        }
    
    async def _deploy_circuit_breaker(self) -> Dict[str, Any]:
        """Deploy circuit breaker service"""
        circuit_breaker = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "circuit-breaker",
                "namespace": self.namespace,
                "labels": {"app": "circuit-breaker", "component": "protection"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "circuit-breaker"}},
                "template": {
                    "metadata": {"labels": {"app": "circuit-breaker"}},
                    "spec": {
                        "containers": [{
                            "name": "circuit-breaker",
                            "image": "ia-influencer/circuit-breaker:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "FAILURE_THRESHOLD", "value": "50"},
                                {"name": "TIMEOUT_THRESHOLD", "value": "30"},
                                {"name": "RECOVERY_TIMEOUT", "value": "60"},
                                {"name": "HALF_OPEN_REQUESTS", "value": "5"},
                                {"name": "METRICS_WINDOW", "value": "300"}
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
        
        # Deploy circuit breaker
        breaker_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=circuit_breaker
        )
        
        return {
            "deployment_id": breaker_deployment.metadata.uid,
            "service": "circuit-breaker",
            "features": ["failure_protection", "automatic_recovery", "half_open_testing"]
        }
    
    async def _deploy_inference_autoscaler(self) -> Dict[str, Any]:
        """Deploy inference autoscaler"""
        autoscaler = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "inference-autoscaler",
                "namespace": self.namespace,
                "labels": {"app": "inference-autoscaler", "component": "scaling"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "inference-autoscaler"}},
                "template": {
                    "metadata": {"labels": {"app": "inference-autoscaler"}},
                    "spec": {
                        "containers": [{
                            "name": "autoscaler",
                            "image": "ia-influencer/inference-autoscaler:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "SCALING_STRATEGY", "value": "predictive"},
                                {"name": "METRICS", "value": "latency,throughput,queue_length,cpu,memory"},
                                {"name": "SCALE_UP_THRESHOLD", "value": "70"},
                                {"name": "SCALE_DOWN_THRESHOLD", "value": "30"},
                                {"name": "COOLDOWN_PERIOD", "value": "60"}
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
        
        # Deploy autoscaler
        autoscaler_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=autoscaler
        )
        
        return {
            "deployment_id": autoscaler_deployment.metadata.uid,
            "service": "inference-autoscaler",
            "features": ["predictive_scaling", "multi_metric", "intelligent_cooldown"]
        }
    
    async def _configure_inference_networking(self) -> None:
        """Configure networking for inference infrastructure"""
        # Inference network policy
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "inference-network-policy",
                "namespace": self.namespace
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {"namespaceSelector": {"matchLabels": {"name": "ia-influencer"}}},
                            {"podSelector": {"matchLabels": {"app": "inference-lb"}}}
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
        
        logger.info("Configured inference networking policies")
    
    async def _validate_inference_infrastructure(self) -> bool:
        """Validate inference infrastructure deployment"""
        try:
            # Check essential services
            essential_services = [
                "inference-redis", "inference-load-balancer", "cache-manager",
                "inference-optimizer", "inference-monitor", "inference-autoscaler"
            ]
            
            for service in essential_services:
                try:
                    deployment = self.k8s_apps_v1.read_namespaced_deployment(
                        name=service,
                        namespace=self.namespace
                    )
                    if not deployment.status.ready_replicas:
                        logger.warning(f"Inference service {service} is not ready")
                        return False
                except Exception as e:
                    logger.error(f"Inference service {service} validation failed: {e}")
                    return False
            
            # Test Redis connectivity
            try:
                self._redis_client.ping()
                logger.info("Inference Redis connectivity validated")
            except Exception as e:
                logger.error(f"Inference Redis validation failed: {e}")
                return False
            
            logger.info("Inference infrastructure validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Inference infrastructure validation failed: {e}")
            return False
    
    async def _validate_inference_config(self, config: InferenceEngineConfig) -> None:
        """Validate inference configuration"""
        if not config.engine_name or not config.model_name:
            raise ValueError("Engine name and model name are required")
        
        if config.target_latency_ms <= 0:
            raise ValueError("Target latency must be positive")
        
        if config.max_throughput_rps <= 0:
            raise ValueError("Max throughput must be positive")
        
        if config.replicas < 1:
            raise ValueError("Replicas must be at least 1")
        
        logger.info(f"Inference config validation passed for {config.engine_name}")
    
    async def _create_inference_deployment_spec(self, config: InferenceEngineConfig) -> Dict[str, Any]:
        """Create deployment specification for inference engine"""
        engine_id = f"{config.engine_name}-{config.model_version}"
        
        deployment_spec = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"inference-{engine_id}",
                "namespace": self.namespace,
                "labels": {
                    "app": f"inference-{engine_id}",
                    "engine-name": config.engine_name,
                    "model-name": config.model_name,
                    "model-version": config.model_version,
                    "inference-type": config.inference_type.value
                }
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {"matchLabels": {"app": f"inference-{engine_id}"}},
                "template": {
                    "metadata": {
                        "labels": {"app": f"inference-{engine_id}"},
                        "annotations": {
                            "inference-config": json.dumps({
                                "engine_name": config.engine_name,
                                "model_name": config.model_name,
                                "model_version": config.model_version,
                                "target_latency_ms": config.target_latency_ms,
                                "batch_size": config.batch_size
                            })
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "inference-engine",
                            "image": f"ia-influencer/inference-{config.inference_type.value}:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "ENGINE_NAME", "value": config.engine_name},
                                {"name": "MODEL_NAME", "value": config.model_name},
                                {"name": "MODEL_VERSION", "value": config.model_version},
                                {"name": "INFERENCE_TYPE", "value": config.inference_type.value},
                                {"name": "OPTIMIZATION_LEVEL", "value": config.optimization_level.value},
                                {"name": "BATCH_SIZE", "value": str(config.batch_size)},
                                {"name": "TARGET_LATENCY_MS", "value": str(config.target_latency_ms)},
                                {"name": "MAX_THROUGHPUT_RPS", "value": str(config.max_throughput_rps)},
                                {"name": "GPU_ENABLED", "value": str(config.gpu_acceleration).lower()},
                                {"name": "QUANTIZATION", "value": str(config.quantization).lower()},
                                {"name": "MODEL_CACHING", "value": str(config.model_caching).lower()},
                                {"name": "CACHING_STRATEGY", "value": config.caching_strategy.value}
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
    
    async def _deploy_realtime_engine(self, config: InferenceEngineConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy real-time inference engine"""
        # Optimize for real-time
        container = deployment_spec["spec"]["template"]["spec"]["containers"][0]
        container["env"].extend([
            {"name": "REAL_TIME_OPTIMIZATION", "value": "true"},
            {"name": "PRELOAD_MODELS", "value": "true"},
            {"name": "CONNECTION_POOLING", "value": "true"},
            {"name": "ZERO_COPY", "value": "true"}
        ])
        
        # Deploy engine
        deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_spec
        )
        
        return {
            "deployment_id": deployment.metadata.uid,
            "type": "real_time",
            "endpoints": [f"http://{deployment.metadata.name}:8080"]
        }
    
    async def _deploy_batch_engine(self, config: InferenceEngineConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy batch inference engine"""
        # Optimize for batch processing
        container = deployment_spec["spec"]["template"]["spec"]["containers"][0]
        container["env"].extend([
            {"name": "BATCH_OPTIMIZATION", "value": "true"},
            {"name": "LARGE_BATCH_SIZE", "value": str(config.batch_size * 4)},
            {"name": "THROUGHPUT_MODE", "value": "true"}
        ])
        
        # Deploy engine
        deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_spec
        )
        
        return {
            "deployment_id": deployment.metadata.uid,
            "type": "batch",
            "endpoints": [f"http://{deployment.metadata.name}:8080"]
        }
    
    async def _deploy_streaming_engine(self, config: InferenceEngineConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy streaming inference engine"""
        # Optimize for streaming
        container = deployment_spec["spec"]["template"]["spec"]["containers"][0]
        container["env"].extend([
            {"name": "STREAMING_MODE", "value": "true"},
            {"name": "BUFFER_SIZE", "value": "1000"},
            {"name": "ASYNC_PROCESSING", "value": "true"}
        ])
        
        # Deploy engine
        deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_spec
        )
        
        return {
            "deployment_id": deployment.metadata.uid,
            "type": "streaming",
            "endpoints": [f"http://{deployment.metadata.name}:8080"]
        }
    
    async def _deploy_edge_engine(self, config: InferenceEngineConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy edge inference engine"""
        # Optimize for edge
        container = deployment_spec["spec"]["template"]["spec"]["containers"][0]
        container["image"] = "ia-influencer/inference-edge:v1.0"
        container["env"].extend([
            {"name": "EDGE_OPTIMIZATION", "value": "true"},
            {"name": "LOW_MEMORY_MODE", "value": "true"},
            {"name": "QUANTIZED_MODELS", "value": "true"}
        ])
        
        # Reduce resource requirements for edge
        container["resources"] = {
            "requests": {"cpu": "200m", "memory": "512Mi"},
            "limits": {"cpu": "1000m", "memory": "2Gi"}
        }
        
        # Deploy engine
        deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_spec
        )
        
        return {
            "deployment_id": deployment.metadata.uid,
            "type": "edge",
            "endpoints": [f"http://{deployment.metadata.name}:8080"]
        }
    
    async def _deploy_serverless_engine(self, config: InferenceEngineConfig, deployment_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy serverless inference engine"""
        # Convert to serverless (Knative)
        serverless_spec = {
            "apiVersion": "serving.knative.dev/v1",
            "kind": "Service",
            "metadata": {
                "name": f"inference-{config.engine_name}-{config.model_version}",
                "namespace": self.namespace
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "autoscaling.knative.dev/minScale": "0",
                            "autoscaling.knative.dev/maxScale": "100"
                        }
                    },
                    "spec": {
                        "containers": deployment_spec["spec"]["template"]["spec"]["containers"]
                    }
                }
            }
        }
        
        # Deploy serverless service
        # Note: This requires Knative to be installed
        service = self.k8s_custom_objects.create_namespaced_custom_object(
            group="serving.knative.dev",
            version="v1",
            namespace=self.namespace,
            plural="services",
            body=serverless_spec
        )
        
        return {
            "service_id": service["metadata"]["uid"],
            "type": "serverless",
            "endpoints": [service["status"]["url"]]
        }
    
    async def _configure_engine_autoscaling(self, config: InferenceEngineConfig) -> None:
        """Configure autoscaling for inference engine"""
        engine_id = f"{config.engine_name}-{config.model_version}"
        
        hpa_spec = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"hpa-inference-{engine_id}",
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"inference-{engine_id}"
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
                                "averageUtilization": 70
                            }
                        }
                    },
                    {
                        "type": "Pods",
                        "pods": {
                            "metric": {
                                "name": "inference_latency_ms"
                            },
                            "target": {
                                "type": "AverageValue",
                                "averageValue": str(config.target_latency_ms)
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
        
        logger.info(f"Configured autoscaling for inference engine {engine_id}")
    
    async def _setup_inference_caching(self, config: InferenceEngineConfig) -> None:
        """Set up caching for inference engine"""
        engine_id = f"{config.engine_name}-{config.model_version}"
        
        caching_config = {
            "engine_id": engine_id,
            "model_caching": config.model_caching,
            "request_caching": config.request_caching,
            "strategy": config.caching_strategy.value,
            "ttl_seconds": config.cache_ttl_seconds
        }
        
        self._redis_client.hset(
            f"inference:caching:{engine_id}",
            mapping=caching_config
        )
        
        logger.info(f"Configured caching for inference engine {engine_id}")
    
    async def _setup_inference_monitoring(self, config: InferenceEngineConfig) -> None:
        """Set up monitoring for inference engine"""
        engine_id = f"{config.engine_name}-{config.model_version}"
        
        monitoring_config = {
            "engine_id": engine_id,
            "metrics": ["latency", "throughput", "accuracy", "error_rate"],
            "alerting": True,
            "dashboard": True,
            "profiling": True
        }
        
        self._redis_client.hset(
            f"inference:monitoring:{engine_id}",
            mapping=monitoring_config
        )
        
        logger.info(f"Configured monitoring for inference engine {engine_id}")
    
    async def _setup_rate_limiting(self, config: InferenceEngineConfig) -> None:
        """Set up rate limiting for inference engine"""
        engine_id = f"{config.engine_name}-{config.model_version}"
        
        rate_config = {
            "engine_id": engine_id,
            "max_rps": config.max_throughput_rps,
            "burst_limit": config.max_throughput_rps * 2,
            "algorithm": "token_bucket"
        }
        
        self._redis_client.hset(
            f"inference:rate_limit:{engine_id}",
            mapping=rate_config
        )
        
        logger.info(f"Configured rate limiting for inference engine {engine_id}")
    
    async def _setup_circuit_breaker(self, config: InferenceEngineConfig) -> None:
        """Set up circuit breaker for inference engine"""
        engine_id = f"{config.engine_name}-{config.model_version}"
        
        breaker_config = {
            "engine_id": engine_id,
            "failure_threshold": 50,
            "timeout_threshold": config.target_latency_ms * 3,
            "recovery_timeout": 60
        }
        
        self._redis_client.hset(
            f"inference:circuit_breaker:{engine_id}",
            mapping=breaker_config
        )
        
        logger.info(f"Configured circuit breaker for inference engine {engine_id}")
    
    async def get_inference_metrics(self) -> Dict[str, Any]:
        """Get comprehensive inference metrics"""
        try:
            metrics = {
                "infrastructure_status": self.status,
                "deployed_engines": len(self.deployed_engines),
                "total_requests_24h": self._redis_client.get("total_inference_requests_24h") or "0",
                "average_latency": self._redis_client.get("average_inference_latency") or "0",
                "throughput_rps": self._redis_client.get("inference_throughput_rps") or "0",
                "error_rate": self._redis_client.get("inference_error_rate") or "0",
                "cache_hit_rate": self._redis_client.get("inference_cache_hit_rate") or "0",
                "engines": {}
            }
            
            # Get per-engine metrics
            for engine_id, engine_info in self.deployed_engines.items():
                engine_metrics = {
                    "status": engine_info["status"],
                    "deployed_at": engine_info["deployed_at"],
                    "endpoints": engine_info["endpoints"],
                    "requests_24h": self._redis_client.get(f"engine:requests:{engine_id}") or "0",
                    "latency": self._redis_client.get(f"engine:latency:{engine_id}") or "0",
                    "throughput": self._redis_client.get(f"engine:throughput:{engine_id}") or "0",
                    "error_rate": self._redis_client.get(f"engine:error_rate:{engine_id}") or "0"
                }
                metrics["engines"][engine_id] = engine_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get inference metrics: {e}")
            return {"error": str(e)}
    
    async def _cleanup_failed_infrastructure(self) -> None:
        """Clean up failed inference infrastructure"""
        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            logger.info("Cleaned up failed inference infrastructure")
        except Exception as e:
            logger.error(f"Inference infrastructure cleanup failed: {e}")
    
    async def _cleanup_failed_engine_deployment(self, engine_name: str) -> None:
        """Clean up failed engine deployment"""
        try:
            # Delete deployment
            try:
                self.k8s_apps_v1.delete_namespaced_deployment(
                    name=f"inference-{engine_name}",
                    namespace=self.namespace
                )
            except:
                pass
            
            logger.info(f"Cleaned up failed engine deployment: {engine_name}")
            
        except Exception as e:
            logger.error(f"Engine cleanup failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up entire inference infrastructure"""
        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            
            self.status = "stopped"
            self.deployed_engines = {}
            self.inference_metrics = {}
            
            logger.info("Inference infrastructure cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Inference cleanup failed: {e}")
            raise
