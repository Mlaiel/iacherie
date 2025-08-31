"""Federated Learning Deployment Manager
Enterprise federated learning infrastructure

This module provides comprehensive federated learning deployment capabilities
for distributed AI training across multiple edge devices and data sources
while preserving privacy and data sovereignty.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml
import kubernetes
from kubernetes import client, config
import docker
import redis
from datetime import datetime, timedelta
import json
import time
import numpy as np
import hashlib
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class FederatedStrategy(Enum):
    """Federated learning strategies"""    FEDERATED_AVERAGING = "federated_averaging"
    FEDERATED_SGD = "federated_sgd"
    FEDERATED_PROX = "federated_prox"
    SCAFFOLD = "scaffold"
    FEDOPT = "fedopt"
    MIME = "mime"
    QFFL = "qffl"
    PERSONALIZED_FL = "personalized_fl"


class AggregationMethod(Enum):
    """Model aggregation methods"""    WEIGHTED_AVERAGE = "weighted_average"
    SIMPLE_AVERAGE = "simple_average"
    MEDIAN_AGGREGATION = "median_aggregation"
    KRUM = "krum"
    TRIMMED_MEAN = "trimmed_mean"
    BYZANTINE_ROBUST = "byzantine_robust"
    DIFFERENTIAL_PRIVACY = "differential_privacy"


class PrivacyTechnique(Enum):
    """Privacy-preserving techniques"""    DIFFERENTIAL_PRIVACY = "differential_privacy"
    HOMOMORPHIC_ENCRYPTION = "homomorphic_encryption"
    SECURE_MULTIPARTY = "secure_multiparty"
    GRADIENT_COMPRESSION = "gradient_compression"
    NOISE_INJECTION = "noise_injection"
    GRADIENT_CLIPPING = "gradient_clipping"


class ClientSelectionStrategy(Enum):
    """Client selection strategies"""    RANDOM_SELECTION = "random_selection"
    STRATIFIED_SAMPLING = "stratified_sampling"
    RESOURCE_AWARE = "resource_aware"
    DATA_QUALITY_BASED = "data_quality_based"
    NETWORK_AWARE = "network_aware"
    CONTRIBUTION_BASED = "contribution_based"


@dataclass
class FederatedLearningConfig:
    """Federated learning configuration"""    federation_name: str
    strategy: FederatedStrategy = FederatedStrategy.FEDERATED_AVERAGING
    aggregation_method: AggregationMethod = AggregationMethod.WEIGHTED_AVERAGE
    privacy_techniques: List[PrivacyTechnique] = field(default_factory=lambda: [PrivacyTechnique.DIFFERENTIAL_PRIVACY])
    client_selection: ClientSelectionStrategy = ClientSelectionStrategy.RANDOM_SELECTION
    num_clients: int = 100
    clients_per_round: int = 10
    num_rounds: int = 100
    local_epochs: int = 5
    learning_rate: float = 0.01
    batch_size: int = 32
    min_data_samples: int = 100
    max_clients_per_round: int = 50
    convergence_threshold: float = 0.001
    privacy_budget: float = 1.0
    noise_scale: float = 0.1
    gradient_clip_norm: float = 1.0
    secure_aggregation: bool = True
    client_dropout_rate: float = 0.1
    data_heterogeneity: str = "iid"  # iid, non_iid, label_skew, feature_skew
    communication_rounds: int = 100
    min_available_clients: int = 5
    byzantine_resilience: bool = True
    personalization_enabled: bool = False
    model_compression: bool = True
    asynchronous_updates: bool = False
    
    def __post_init__(self):
        if not self.privacy_techniques:
            self.privacy_techniques = [PrivacyTechnique.DIFFERENTIAL_PRIVACY]


class FederatedLearningDeployment:
    """    Enterprise federated learning deployment system
    
    Provides comprehensive federated learning infrastructure with:
    - Multi-strategy federated training algorithms
    - Privacy-preserving learning techniques
    - Robust aggregation methods with Byzantine resilience
    - Intelligent client selection and management
    - Secure communication and model updates
    - Cross-device and cross-silo federation support
    - Real-time monitoring and analytics
    """    
    def __init__(self, namespace: str = "ia-influencer-federated"):
        """        Initialize federated learning deployment
        
        Args:
            namespace: Kubernetes namespace for federated infrastructure
        """        self.namespace = namespace
        self.federations = {}
        self.clients = {}
        self.aggregation_servers = {}
        self.status = "initializing"
        
        # Initialize clients and crypto
        self._initialize_clients()
        self._initialize_crypto()
    
    def _initialize_clients(self) -> None:
        """Initialize Kubernetes, Docker, and Redis clients"""        try:
            # Kubernetes client
            config.load_incluster_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_batch_v1 = client.BatchV1Api()
            self.k8s_networking_v1 = client.NetworkingV1Api()
            
            # Docker client for container management
            self._docker_client = docker.from_env()
            
            # Redis for federated coordination
            self._redis_client = redis.Redis(
                host='federated-redis',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            logger.info("Federated learning clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize federated clients: {e}")
            raise
    
    def _initialize_crypto(self) -> None:
        """Initialize cryptographic components"""        try:
            # Generate federation-wide encryption key
            self.federation_key = Fernet.generate_key()
            self.cipher_suite = Fernet(self.federation_key)
            
            # Initialize secure aggregation components
            self.secure_aggregator = SecureAggregator()
            
            logger.info("Cryptographic components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize crypto: {e}")
            raise
    
    async def deploy_federated_infrastructure(self) -> Dict[str, Any]:
        """        Deploy complete federated learning infrastructure
        
        Returns:
            Federated infrastructure deployment summary
        """        try:
            self.status = "deploying_federated_infrastructure"
            logger.info("Deploying federated learning infrastructure")
            
            # Create federated namespace
            await self._ensure_federated_namespace()
            
            # Deploy federated coordination layer
            coordinator_result = await self._deploy_federated_coordinator()
            
            # Deploy aggregation servers
            aggregation_result = await self._deploy_aggregation_servers()
            
            # Deploy client management system
            client_manager_result = await self._deploy_client_manager()
            
            # Deploy privacy infrastructure
            privacy_result = await self._deploy_privacy_infrastructure()
            
            # Deploy federated monitoring
            monitoring_result = await self._deploy_federated_monitoring()
            
            # Deploy model repository for federated models
            model_repo_result = await self._deploy_federated_model_repository()
            
            # Deploy communication infrastructure
            communication_result = await self._deploy_communication_infrastructure()
            
            # Configure federated networking and security
            await self._configure_federated_networking()
            
            # Validate federated infrastructure
            if await self._validate_federated_infrastructure():
                self.status = "federated_infrastructure_ready"
                logger.info("Federated learning infrastructure deployed successfully")
                
                return {
                    "status": "success",
                    "infrastructure": {
                        "coordinator": coordinator_result,
                        "aggregation_servers": aggregation_result,
                        "client_manager": client_manager_result,
                        "privacy_infrastructure": privacy_result,
                        "monitoring": monitoring_result,
                        "model_repository": model_repo_result,
                        "communication": communication_result
                    },
                    "capabilities": {
                        "supported_strategies": [s.value for s in FederatedStrategy],
                        "aggregation_methods": [a.value for a in AggregationMethod],
                        "privacy_techniques": [p.value for p in PrivacyTechnique],
                        "client_selection": [c.value for c in ClientSelectionStrategy],
                        "secure_aggregation": True,
                        "byzantine_resilience": True,
                        "personalization": True,
                        "cross_device_support": True,
                        "cross_silo_support": True
                    }
                }
            else:
                raise Exception("Federated infrastructure validation failed")
                
        except Exception as e:
            self.status = "federated_infrastructure_failed"
            logger.error(f"Federated infrastructure deployment failed: {e}")
            await self._cleanup_failed_federated_infrastructure()
            raise
    
    async def deploy_federation(self, config: FederatedLearningConfig) -> Dict[str, Any]:
        """        Deploy a federated learning federation
        
        Args:
            config: Federated learning configuration
            
        Returns:
            Federation deployment result
        """        try:
            federation_id = f"{config.federation_name}-{int(time.time())}"
            logger.info(f"Deploying federation: {federation_id}")
            
            # Validate federated configuration
            await self._validate_federated_config(config)
            
            # Create federation coordinator
            coordinator = await self._create_federation_coordinator(config, federation_id)
            
            # Deploy aggregation servers for this federation
            aggregation_servers = await self._deploy_federation_aggregation_servers(config, federation_id)
            
            # Initialize client pool
            client_pool = await self._initialize_federation_clients(config, federation_id)
            
            # Set up privacy-preserving mechanisms
            privacy_setup = await self._setup_federation_privacy(config, federation_id)
            
            # Configure secure communication
            communication_setup = await self._setup_federation_communication(config, federation_id)
            
            # Set up monitoring and analytics
            monitoring_setup = await self._setup_federation_monitoring(config, federation_id)
            
            # Store federation information
            self.federations[federation_id] = {
                "config": config,
                "coordinator": coordinator,
                "aggregation_servers": aggregation_servers,
                "client_pool": client_pool,
                "privacy_setup": privacy_setup,
                "communication_setup": communication_setup,
                "monitoring_setup": monitoring_setup,
                "status": "deployed",
                "deployed_at": datetime.utcnow().isoformat(),
                "rounds_completed": 0,
                "active_clients": 0
            }
            
            logger.info(f"Federation {federation_id} deployed successfully")
            
            return {
                "status": "success",
                "federation_id": federation_id,
                "coordinator": coordinator,
                "aggregation_servers": aggregation_servers,
                "client_pool_size": len(client_pool),
                "privacy_techniques": [p.value for p in config.privacy_techniques],
                "capabilities": {
                    "strategy": config.strategy.value,
                    "aggregation_method": config.aggregation_method.value,
                    "secure_aggregation": config.secure_aggregation,
                    "byzantine_resilience": config.byzantine_resilience,
                    "personalization": config.personalization_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"Federation deployment failed: {e}")
            await self._cleanup_failed_federation_deployment(config.federation_name)
            raise
    
    async def _ensure_federated_namespace(self) -> None:
        """Create federated namespace"""        try:
            self.k8s_core_v1.read_namespace(name=self.namespace)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                namespace_body = client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name=self.namespace,
                        labels={
                            "name": self.namespace,
                            "purpose": "federated-learning",
                            "privacy-preserving": "true",
                            "secure-aggregation": "true"
                        }
                    )
                )
                self.k8s_core_v1.create_namespace(body=namespace_body)
                logger.info(f"Created federated namespace: {self.namespace}")
    
    async def _deploy_federated_coordinator(self) -> Dict[str, Any]:
        """Deploy federated learning coordinator"""        coordinator = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "federated-coordinator",
                "namespace": self.namespace,
                "labels": {"app": "federated-coordinator", "component": "coordination"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "federated-coordinator"}},
                "template": {
                    "metadata": {"labels": {"app": "federated-coordinator"}},
                    "spec": {
                        "containers": [{
                            "name": "coordinator",
                            "image": "ia-influencer/federated-coordinator:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "FEDERATION_MANAGEMENT", "value": "true"},
                                {"name": "CLIENT_ORCHESTRATION", "value": "true"},
                                {"name": "ROUND_COORDINATION", "value": "true"},
                                {"name": "SECURE_AGGREGATION", "value": "true"},
                                {"name": "PRIVACY_PRESERVING", "value": "true"},
                                {"name": "BYZANTINE_RESILIENCE", "value": "true"},
                                {"name": "ASYNC_UPDATES", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "2Gi"},
                                "limits": {"cpu": "4000m", "memory": "8Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy coordinator
        coordinator_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=coordinator
        )
        
        return {
            "deployment_id": coordinator_deployment.metadata.uid,
            "service": "federated-coordinator",
            "features": ["federation_management", "client_orchestration", "secure_aggregation"]
        }
    
    async def _deploy_aggregation_servers(self) -> Dict[str, Any]:
        """Deploy federated aggregation servers"""        aggregation_server = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "aggregation-servers",
                "namespace": self.namespace,
                "labels": {"app": "aggregation-servers", "component": "aggregation"}
            },
            "spec": {
                "replicas": 5,
                "selector": {"matchLabels": {"app": "aggregation-servers"}},
                "template": {
                    "metadata": {"labels": {"app": "aggregation-servers"}},
                    "spec": {
                        "containers": [{
                            "name": "aggregation-server",
                            "image": "ia-influencer/aggregation-server:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "AGGREGATION_METHODS", "value": "weighted_avg,secure_agg,byzantine_robust"},
                                {"name": "PRIVACY_TECHNIQUES", "value": "differential_privacy,homomorphic_encryption"},
                                {"name": "MODEL_COMPRESSION", "value": "true"},
                                {"name": "GRADIENT_COMPRESSION", "value": "true"},
                                {"name": "SECURE_COMPUTATION", "value": "true"},
                                {"name": "NOISE_INJECTION", "value": "configurable"}
                            ],
                            "resources": {
                                "requests": {"cpu": "2000m", "memory": "4Gi"},
                                "limits": {"cpu": "8000m", "memory": "16Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy aggregation servers
        aggregation_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=aggregation_server
        )
        
        return {
            "deployment_id": aggregation_deployment.metadata.uid,
            "service": "aggregation-servers",
            "features": ["secure_aggregation", "privacy_preserving", "byzantine_robust"]
        }
    
    async def _deploy_client_manager(self) -> Dict[str, Any]:
        """Deploy federated client management system"""        client_manager = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "client-manager",
                "namespace": self.namespace,
                "labels": {"app": "client-manager", "component": "client_management"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "client-manager"}},
                "template": {
                    "metadata": {"labels": {"app": "client-manager"}},
                    "spec": {
                        "containers": [{
                            "name": "client-manager",
                            "image": "ia-influencer/client-manager:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "CLIENT_REGISTRATION", "value": "true"},
                                {"name": "CLIENT_SELECTION", "value": "intelligent"},
                                {"name": "RESOURCE_MONITORING", "value": "true"},
                                {"name": "DATA_QUALITY_ASSESSMENT", "value": "true"},
                                {"name": "PERFORMANCE_TRACKING", "value": "true"},
                                {"name": "INCENTIVE_MECHANISM", "value": "contribution_based"}
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
        
        # Deploy client manager
        cm_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=client_manager
        )
        
        return {
            "deployment_id": cm_deployment.metadata.uid,
            "service": "client-manager",
            "features": ["client_registration", "intelligent_selection", "performance_tracking"]
        }
    
    async def _deploy_privacy_infrastructure(self) -> Dict[str, Any]:
        """Deploy privacy-preserving infrastructure"""        privacy_infrastructure = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "privacy-infrastructure",
                "namespace": self.namespace,
                "labels": {"app": "privacy-infrastructure", "component": "privacy"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "privacy-infrastructure"}},
                "template": {
                    "metadata": {"labels": {"app": "privacy-infrastructure"}},
                    "spec": {
                        "containers": [{
                            "name": "privacy-engine",
                            "image": "ia-influencer/privacy-engine:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "DIFFERENTIAL_PRIVACY", "value": "true"},
                                {"name": "HOMOMORPHIC_ENCRYPTION", "value": "true"},
                                {"name": "SECURE_MULTIPARTY", "value": "true"},
                                {"name": "NOISE_MECHANISMS", "value": "gaussian,laplace"},
                                {"name": "PRIVACY_BUDGET_MANAGEMENT", "value": "automatic"},
                                {"name": "GRADIENT_CLIPPING", "value": "adaptive"}
                            ],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "2Gi"},
                                "limits": {"cpu": "4000m", "memory": "8Gi"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy privacy infrastructure
        privacy_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=privacy_infrastructure
        )
        
        return {
            "deployment_id": privacy_deployment.metadata.uid,
            "service": "privacy-infrastructure",
            "features": ["differential_privacy", "homomorphic_encryption", "secure_multiparty"]
        }
    
    async def _deploy_federated_monitoring(self) -> Dict[str, Any]:
        """Deploy federated learning monitoring"""        federated_monitor = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "federated-monitor",
                "namespace": self.namespace,
                "labels": {"app": "federated-monitor", "component": "monitoring"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "federated-monitor"}},
                "template": {
                    "metadata": {"labels": {"app": "federated-monitor"}},
                    "spec": {
                        "containers": [{
                            "name": "monitor",
                            "image": "ia-influencer/federated-monitor:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "CONVERGENCE_TRACKING", "value": "true"},
                                {"name": "CLIENT_PARTICIPATION", "value": "monitored"},
                                {"name": "PRIVACY_METRICS", "value": "true"},
                                {"name": "AGGREGATION_METRICS", "value": "true"},
                                {"name": "COMMUNICATION_EFFICIENCY", "value": "tracked"},
                                {"name": "FAIRNESS_ASSESSMENT", "value": "enabled"}
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
        
        # Deploy federated monitoring
        monitor_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=federated_monitor
        )
        
        return {
            "deployment_id": monitor_deployment.metadata.uid,
            "service": "federated-monitor",
            "features": ["convergence_tracking", "privacy_metrics", "fairness_assessment"]
        }
    
    async def _deploy_federated_model_repository(self) -> Dict[str, Any]:
        """Deploy federated model repository"""        model_repository = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "federated-model-repository",
                "namespace": self.namespace,
                "labels": {"app": "model-repository", "component": "storage"}
            },
            "spec": {
                "serviceName": "federated-model-repository",
                "replicas": 3,
                "selector": {"matchLabels": {"app": "model-repository"}},
                "template": {
                    "metadata": {"labels": {"app": "model-repository"}},
                    "spec": {
                        "containers": [{
                            "name": "repository",
                            "image": "ia-influencer/federated-model-repository:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "GLOBAL_MODEL_STORAGE", "value": "true"},
                                {"name": "PERSONALIZED_MODELS", "value": "true"},
                                {"name": "VERSION_CONTROL", "value": "git"},
                                {"name": "ENCRYPTION", "value": "aes256"},
                                {"name": "MODEL_COMPRESSION", "value": "true"},
                                {"name": "DELTA_STORAGE", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "2Gi"},
                                "limits": {"cpu": "2000m", "memory": "8Gi"}
                            },
                            "volumeMounts": [{
                                "name": "model-data",
                                "mountPath": "/data"
                            }]
                        }]
                    }
                },
                "volumeClaimTemplates": [{
                    "metadata": {"name": "model-data"},
                    "spec": {
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {"requests": {"storage": "200Gi"}},
                        "storageClassName": "fast-ssd"
                    }
                }]
            }
        }
        
        # Deploy model repository
        repository_deployment = self.k8s_apps_v1.create_namespaced_stateful_set(
            namespace=self.namespace,
            body=model_repository
        )
        
        return {
            "deployment_id": repository_deployment.metadata.uid,
            "service": "federated-model-repository",
            "features": ["global_models", "personalized_models", "version_control"]
        }
    
    async def _deploy_communication_infrastructure(self) -> Dict[str, Any]:
        """Deploy federated communication infrastructure"""        communication = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "federated-communication",
                "namespace": self.namespace,
                "labels": {"app": "federated-communication", "component": "communication"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "federated-communication"}},
                "template": {
                    "metadata": {"labels": {"app": "federated-communication"}},
                    "spec": {
                        "containers": [{
                            "name": "communication",
                            "image": "ia-influencer/federated-communication:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "SECURE_CHANNELS", "value": "true"},
                                {"name": "MESSAGE_ENCRYPTION", "value": "end_to_end"},
                                {"name": "COMPRESSION", "value": "adaptive"},
                                {"name": "ASYNCHRONOUS_UPDATES", "value": "true"},
                                {"name": "NETWORK_ADAPTATION", "value": "true"},
                                {"name": "FAULT_TOLERANCE", "value": "byzantine"}
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
        
        # Deploy communication infrastructure
        comm_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=communication
        )
        
        return {
            "deployment_id": comm_deployment.metadata.uid,
            "service": "federated-communication",
            "features": ["secure_channels", "adaptive_compression", "fault_tolerance"]
        }
    
    async def _configure_federated_networking(self) -> None:
        """Configure networking for federated infrastructure"""        # Federated network policy
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "federated-network-policy",
                "namespace": self.namespace
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {"namespaceSelector": {"matchLabels": {"name": "ia-influencer"}}},
                            {"podSelector": {"matchLabels": {"app": "federated-coordinator"}}}
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
        
        logger.info("Configured federated networking policies")
    
    async def _validate_federated_infrastructure(self) -> bool:
        """Validate federated infrastructure deployment"""        try:
            # Check essential federated services
            essential_services = [
                "federated-coordinator", "aggregation-servers", "client-manager",
                "privacy-infrastructure", "federated-monitor", "federated-model-repository",
                "federated-communication"
            ]
            
            for service in essential_services:
                try:
                    deployment = self.k8s_apps_v1.read_namespaced_deployment(
                        name=service,
                        namespace=self.namespace
                    )
                    if not deployment.status.ready_replicas:
                        logger.warning(f"Federated service {service} is not ready")
                        return False
                except Exception as e:
                    logger.error(f"Federated service {service} validation failed: {e}")
                    return False
            
            # Test federated coordination
            try:
                self._redis_client.ping()
                logger.info("Federated coordination connectivity validated")
            except Exception as e:
                logger.error(f"Federated coordination validation failed: {e}")
                return False
            
            logger.info("Federated infrastructure validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Federated infrastructure validation failed: {e}")
            return False
    
    async def _validate_federated_config(self, config: FederatedLearningConfig) -> None:
        """Validate federated learning configuration"""        if not config.federation_name:
            raise ValueError("Federation name is required")
        
        if config.num_clients <= 0:
            raise ValueError("Number of clients must be positive")
        
        if config.clients_per_round <= 0 or config.clients_per_round > config.num_clients:
            raise ValueError("Clients per round must be positive and <= total clients")
        
        if config.num_rounds <= 0:
            raise ValueError("Number of rounds must be positive")
        
        if config.local_epochs <= 0:
            raise ValueError("Local epochs must be positive")
        
        logger.info(f"Federated config validation passed for {config.federation_name}")
    
    async def _create_federation_coordinator(self, config: FederatedLearningConfig, federation_id: str) -> Dict[str, Any]:
        """Create federation coordinator"""        coordinator_config = {
            "federation_id": federation_id,
            "strategy": config.strategy.value,
            "aggregation_method": config.aggregation_method.value,
            "num_rounds": config.num_rounds,
            "clients_per_round": config.clients_per_round,
            "convergence_threshold": config.convergence_threshold,
            "secure_aggregation": config.secure_aggregation,
            "byzantine_resilience": config.byzantine_resilience
        }
        
        # Store coordinator configuration
        self._redis_client.hset(
            f"federation:coordinator:{federation_id}",
            mapping=coordinator_config
        )
        
        return {
            "coordinator_id": f"coordinator-{federation_id}",
            "config": coordinator_config
        }
    
    async def _deploy_federation_aggregation_servers(self, config: FederatedLearningConfig, federation_id: str) -> List[Dict[str, Any]]:
        """Deploy aggregation servers for specific federation"""        aggregation_servers = []
        
        # Deploy multiple aggregation servers based on federation size
        num_servers = min(5, max(1, config.num_clients // 20))
        
        for i in range(num_servers):
            server_config = {
                "server_id": f"agg-server-{federation_id}-{i}",
                "federation_id": federation_id,
                "aggregation_method": config.aggregation_method.value,
                "privacy_techniques": [p.value for p in config.privacy_techniques],
                "byzantine_resilience": config.byzantine_resilience
            }
            
            aggregation_servers.append(server_config)
            
            # Store server configuration
            self._redis_client.hset(
                f"federation:aggregation:{federation_id}:{i}",
                mapping=server_config
            )
        
        return aggregation_servers
    
    async def _initialize_federation_clients(self, config: FederatedLearningConfig, federation_id: str) -> List[Dict[str, Any]]:
        """Initialize client pool for federation"""        client_pool = []
        
        for i in range(config.num_clients):
            client_config = {
                "client_id": f"client-{federation_id}-{i}",
                "federation_id": federation_id,
                "local_epochs": config.local_epochs,
                "batch_size": config.batch_size,
                "learning_rate": config.learning_rate,
                "data_samples": np.random.randint(config.min_data_samples, config.min_data_samples * 5),
                "device_type": np.random.choice(["mobile", "desktop", "edge", "server"]),
                "network_quality": np.random.choice(["low", "medium", "high"]),
                "availability": np.random.uniform(0.7, 1.0),
                "data_quality_score": np.random.uniform(0.8, 1.0)
            }
            
            client_pool.append(client_config)
            
            # Store client configuration
            self._redis_client.hset(
                f"federation:client:{federation_id}:{i}",
                mapping=client_config
            )
        
        return client_pool
    
    async def _setup_federation_privacy(self, config: FederatedLearningConfig, federation_id: str) -> Dict[str, Any]:
        """Set up privacy-preserving mechanisms for federation"""        privacy_config = {
            "federation_id": federation_id,
            "privacy_techniques": [p.value for p in config.privacy_techniques],
            "privacy_budget": config.privacy_budget,
            "noise_scale": config.noise_scale,
            "gradient_clip_norm": config.gradient_clip_norm,
            "secure_aggregation": config.secure_aggregation
        }
        
        # Store privacy configuration
        self._redis_client.hset(
            f"federation:privacy:{federation_id}",
            mapping=privacy_config
        )
        
        return privacy_config
    
    async def _setup_federation_communication(self, config: FederatedLearningConfig, federation_id: str) -> Dict[str, Any]:
        """Set up secure communication for federation"""        communication_config = {
            "federation_id": federation_id,
            "encryption_enabled": True,
            "compression_enabled": config.model_compression,
            "asynchronous_updates": config.asynchronous_updates,
            "communication_rounds": config.communication_rounds
        }
        
        # Store communication configuration
        self._redis_client.hset(
            f"federation:communication:{federation_id}",
            mapping=communication_config
        )
        
        return communication_config
    
    async def _setup_federation_monitoring(self, config: FederatedLearningConfig, federation_id: str) -> Dict[str, Any]:
        """Set up monitoring for federation"""        monitoring_config = {
            "federation_id": federation_id,
            "convergence_tracking": True,
            "client_participation_monitoring": True,
            "privacy_metrics": True,
            "fairness_assessment": True,
            "communication_efficiency": True
        }
        
        # Store monitoring configuration
        self._redis_client.hset(
            f"federation:monitoring:{federation_id}",
            mapping=monitoring_config
        )
        
        return monitoring_config
    
    async def get_federated_metrics(self) -> Dict[str, Any]:
        """Get comprehensive federated learning metrics"""        try:
            metrics = {
                "infrastructure_status": self.status,
                "active_federations": len(self.federations),
                "total_clients": sum(len(fed["client_pool"]) for fed in self.federations.values()),
                "total_aggregation_servers": sum(len(fed["aggregation_servers"]) for fed in self.federations.values()),
                "global_privacy_budget_used": self._redis_client.get("global:privacy_budget_used") or "0",
                "total_communication_rounds": self._redis_client.get("global:communication_rounds") or "0",
                "federations": {}
            }
            
            # Get per-federation metrics
            for federation_id, federation_info in self.federations.items():
                federation_metrics = {
                    "status": federation_info["status"],
                    "deployed_at": federation_info["deployed_at"],
                    "rounds_completed": federation_info["rounds_completed"],
                    "active_clients": federation_info["active_clients"],
                    "strategy": federation_info["config"].strategy.value,
                    "aggregation_method": federation_info["config"].aggregation_method.value,
                    "privacy_techniques": [p.value for p in federation_info["config"].privacy_techniques],
                    "convergence_rate": self._redis_client.get(f"federation:convergence:{federation_id}") or "0",
                    "communication_efficiency": self._redis_client.get(f"federation:comm_efficiency:{federation_id}") or "0",
                    "fairness_score": self._redis_client.get(f"federation:fairness:{federation_id}") or "0"
                }
                metrics["federations"][federation_id] = federation_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get federated metrics: {e}")
            return {"error": str(e)}
    
    async def _cleanup_failed_federated_infrastructure(self) -> None:
        """Clean up failed federated infrastructure deployment"""        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            logger.info("Cleaned up failed federated infrastructure")
        except Exception as e:
            logger.error(f"Federated infrastructure cleanup failed: {e}")
    
    async def _cleanup_failed_federation_deployment(self, federation_name: str) -> None:
        """Clean up failed federation deployment"""        try:
            # Clean up federation-specific resources
            federation_keys = self._redis_client.keys(f"federation:*{federation_name}*")
            if federation_keys:
                self._redis_client.delete(*federation_keys)
            
            logger.info(f"Cleaned up failed federation deployment: {federation_name}")
            
        except Exception as e:
            logger.error(f"Federation deployment cleanup failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up entire federated learning infrastructure"""        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            
            self.status = "stopped"
            self.federations = {}
            self.clients = {}
            self.aggregation_servers = {}
            
            logger.info("Federated learning infrastructure cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Federated learning cleanup failed: {e}")
            raise


class SecureAggregator:
    """Secure aggregation implementation for federated learning"""    
    def __init__(self):
        self.aggregation_key = Fernet.generate_key()
        self.cipher = Fernet(self.aggregation_key)
    
    def secure_aggregate(self, client_updates: List[Dict[str, Any]], weights: List[float]) -> Dict[str, Any]:
        """        Perform secure aggregation of client updates
        
        Args:
            client_updates: List of encrypted client model updates
            weights: List of aggregation weights for each client
            
        Returns:
            Securely aggregated global model update
        """        try:
            # Decrypt client updates
            decrypted_updates = []
            for update in client_updates:
                decrypted = self.cipher.decrypt(update["encrypted_model"].encode())
                decrypted_updates.append(json.loads(decrypted.decode()))
            
            # Perform weighted aggregation
            aggregated_model = self._weighted_average(decrypted_updates, weights)
            
            # Encrypt aggregated model
            encrypted_aggregated = self.cipher.encrypt(json.dumps(aggregated_model).encode())
            
            return {
                "aggregated_model": encrypted_aggregated.decode(),
                "num_clients": len(client_updates),
                "aggregation_method": "secure_weighted_average"
            }
            
        except Exception as e:
            logger.error(f"Secure aggregation failed: {e}")
            raise
    
    def _weighted_average(self, models: List[Dict], weights: List[float]) -> Dict:
        """Compute weighted average of model parameters"""        if not models or not weights:
            raise ValueError("Models and weights cannot be empty")
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Initialize aggregated model with first model structure
        aggregated = {key: np.zeros_like(np.array(value)) for key, value in models[0].items()}
        
        # Weighted aggregation
        for model, weight in zip(models, normalized_weights):
            for key in aggregated:
                aggregated[key] += weight * np.array(model[key])
        
        # Convert back to lists for JSON serialization
        return {key: value.tolist() for key, value in aggregated.items()}
