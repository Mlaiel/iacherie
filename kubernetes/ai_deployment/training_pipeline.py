"""Training Pipeline Deployment
Enterprise ML training infrastructure

This module provides comprehensive training pipeline deployment
including distributed training, hyperparameter optimization,
experiment tracking, and automated model deployment.

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
import numpy as np

logger = logging.getLogger(__name__)


class TrainingFramework(Enum):
    """Supported training frameworks"""    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    PYTORCH_LIGHTNING = "pytorch_lightning"
    HUGGINGFACE = "huggingface"
    SCIKIT_LEARN = "scikit_learn"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    RAY_TRAIN = "ray_train"
    HOROVOD = "horovod"


class TrainingType(Enum):
    """Training job types"""    SINGLE_NODE = "single_node"
    MULTI_NODE = "multi_node"
    DISTRIBUTED = "distributed"
    FEDERATED = "federated"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    ENSEMBLE = "ensemble"
    CONTINUAL_LEARNING = "continual_learning"


class OptimizationStrategy(Enum):
    """Hyperparameter optimization strategies"""    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    GENETIC_ALGORITHM = "genetic_algorithm"
    OPTUNA = "optuna"
    HYPERBAND = "hyperband"
    POPULATION_BASED = "population_based"


@dataclass
class TrainingPipelineConfig:
    """Training pipeline configuration"""    pipeline_name: str
    framework: TrainingFramework
    training_type: TrainingType = TrainingType.SINGLE_NODE
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BAYESIAN_OPTIMIZATION
    distributed_backend: str = "nccl"
    num_nodes: int = 1
    num_gpus_per_node: int = 2
    max_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    early_stopping: bool = True
    checkpoint_enabled: bool = True
    experiment_tracking: bool = True
    auto_model_deployment: bool = True
    hyperparameter_tuning: bool = False
    resource_limits: Dict[str, str] = None
    storage_size: str = "1Ti"
    data_parallel: bool = True
    model_parallel: bool = False
    gradient_accumulation_steps: int = 1
    mixed_precision: bool = True
    
    def __post_init__(self):
        if self.resource_limits is None:
            self.resource_limits = {
                "cpu": "8000m",
                "memory": "32Gi",
                "nvidia.com/gpu": str(self.num_gpus_per_node)
            }


class TrainingPipelineDeployment:
    """    Enterprise training pipeline deployment system
    
    Provides comprehensive ML training infrastructure with:
    - Multi-framework support (TensorFlow, PyTorch, Hugging Face, etc.)
    - Distributed and federated training
    - Hyperparameter optimization
    - Experiment tracking and management
    - Automated model deployment
    - Resource optimization and scheduling
    """    
    def __init__(self, namespace: str = "ia-influencer-training"):
        """        Initialize training pipeline deployment
        
        Args:
            namespace: Kubernetes namespace for training infrastructure
        """        self.namespace = namespace
        self.active_pipelines = {}
        self.completed_pipelines = {}
        self.training_jobs = {}
        self.status = "initializing"
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Kubernetes, Docker, and Redis clients"""        try:
            # Kubernetes client
            config.load_incluster_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_batch_v1 = client.BatchV1Api()
            self.k8s_custom_objects = client.CustomObjectsApi()
            self.k8s_storage_v1 = client.StorageV1Api()
            
            # Docker client for training images
            self._docker_client = docker.from_env()
            
            # Redis for training metadata and coordination
            self._redis_client = redis.Redis(
                host='training-redis',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            logger.info("Training pipeline clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize training clients: {e}")
            raise
    
    async def deploy_training_infrastructure(self) -> Dict[str, Any]:
        """        Deploy complete training pipeline infrastructure
        
        Returns:
            Infrastructure deployment summary
        """        try:
            self.status = "deploying_infrastructure"
            logger.info("Deploying training pipeline infrastructure")
            
            # Create training namespace
            await self._ensure_training_namespace()
            
            # Deploy core training infrastructure
            redis_result = await self._deploy_training_redis()
            scheduler_result = await self._deploy_training_scheduler()
            experiment_tracker_result = await self._deploy_experiment_tracker()
            hyperopt_result = await self._deploy_hyperparameter_optimizer()
            
            # Deploy distributed training infrastructure
            distributed_result = await self._deploy_distributed_training()
            
            # Deploy training storage
            storage_result = await self._deploy_training_storage()
            
            # Deploy monitoring and logging
            monitoring_result = await self._deploy_training_monitoring()
            
            # Deploy model registry integration
            registry_result = await self._deploy_model_registry_integration()
            
            # Configure GPU management
            gpu_result = await self._deploy_gpu_management()
            
            # Configure training networking
            await self._configure_training_networking()
            
            # Validate infrastructure
            if await self._validate_training_infrastructure():
                self.status = "infrastructure_ready"
                logger.info("Training infrastructure deployed successfully")
                
                return {
                    "status": "success",
                    "infrastructure": {
                        "redis": redis_result,
                        "scheduler": scheduler_result,
                        "experiment_tracker": experiment_tracker_result,
                        "hyperopt": hyperopt_result,
                        "distributed": distributed_result,
                        "storage": storage_result,
                        "monitoring": monitoring_result,
                        "model_registry": registry_result,
                        "gpu_management": gpu_result
                    },
                    "capabilities": {
                        "frameworks": [f.value for f in TrainingFramework],
                        "training_types": [t.value for t in TrainingType],
                        "optimization_strategies": [o.value for o in OptimizationStrategy],
                        "distributed_training": True,
                        "hyperparameter_tuning": True,
                        "experiment_tracking": True,
                        "auto_deployment": True
                    }
                }
            else:
                raise Exception("Training infrastructure validation failed")
                
        except Exception as e:
            self.status = "infrastructure_failed"
            logger.error(f"Training infrastructure deployment failed: {e}")
            await self._cleanup_failed_infrastructure()
            raise
    
    async def submit_training_job(self, config: TrainingPipelineConfig) -> Dict[str, Any]:
        """        Submit a training job
        
        Args:
            config: Training pipeline configuration
            
        Returns:
            Training job submission result
        """        try:
            job_id = f"{config.pipeline_name}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            logger.info(f"Submitting training job: {job_id}")
            
            # Validate training configuration
            await self._validate_training_config(config)
            
            # Create training job specification
            job_spec = await self._create_training_job_spec(config, job_id)
            
            # Submit job based on training type
            if config.training_type == TrainingType.SINGLE_NODE:
                job_result = await self._submit_single_node_job(config, job_spec)
            elif config.training_type == TrainingType.MULTI_NODE:
                job_result = await self._submit_multi_node_job(config, job_spec)
            elif config.training_type == TrainingType.DISTRIBUTED:
                job_result = await self._submit_distributed_job(config, job_spec)
            elif config.training_type == TrainingType.HYPERPARAMETER_TUNING:
                job_result = await self._submit_hyperparameter_job(config, job_spec)
            else:
                job_result = await self._submit_custom_job(config, job_spec)
            
            # Set up job monitoring
            await self._setup_job_monitoring(job_id, config)
            
            # Configure experiment tracking
            if config.experiment_tracking:
                await self._setup_experiment_tracking(job_id, config)
            
            # Store job information
            self.active_pipelines[job_id] = {
                "config": config,
                "job_result": job_result,
                "status": "submitted",
                "submitted_at": datetime.utcnow().isoformat(),
                "framework": config.framework.value,
                "training_type": config.training_type.value
            }
            
            logger.info(f"Training job {job_id} submitted successfully")
            
            return {
                "status": "success",
                "job_id": job_id,
                "job_result": job_result,
                "estimated_duration": self._estimate_training_duration(config),
                "resource_allocation": {
                    "nodes": config.num_nodes,
                    "gpus_per_node": config.num_gpus_per_node,
                    "total_gpus": config.num_nodes * config.num_gpus_per_node,
                    "memory": config.resource_limits.get("memory", "32Gi"),
                    "storage": config.storage_size
                }
            }
            
        except Exception as e:
            logger.error(f"Training job submission failed: {e}")
            raise
    
    async def _ensure_training_namespace(self) -> None:
        """Create training namespace"""        try:
            self.k8s_core_v1.read_namespace(name=self.namespace)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                namespace_body = client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name=self.namespace,
                        labels={
                            "name": self.namespace,
                            "purpose": "ml-training",
                            "gpu-enabled": "true",
                            "compute-intensive": "true",
                            "distributed-training": "true"
                        }
                    )
                )
                self.k8s_core_v1.create_namespace(body=namespace_body)
                logger.info(f"Created training namespace: {self.namespace}")
    
    async def _deploy_training_redis(self) -> Dict[str, Any]:
        """Deploy Redis for training coordination"""        redis_cluster = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "training-redis",
                "namespace": self.namespace,
                "labels": {"app": "training-redis", "component": "coordination"}
            },
            "spec": {
                "serviceName": "training-redis",
                "replicas": 3,
                "selector": {"matchLabels": {"app": "training-redis"}},
                "template": {
                    "metadata": {"labels": {"app": "training-redis"}},
                    "spec": {
                        "containers": [{
                            "name": "redis",
                            "image": "redis:7-alpine",
                            "args": [
                                "redis-server",
                                "--maxmemory", "8gb",
                                "--maxmemory-policy", "allkeys-lru",
                                "--appendonly", "yes",
                                "--tcp-keepalive", "60",
                                "--timeout", "300"
                            ],
                            "ports": [{"containerPort": 6379}],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "4Gi"},
                                "limits": {"cpu": "2000m", "memory": "8Gi"}
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
                        "resources": {"requests": {"storage": "100Gi"}},
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
            "service": "training-redis",
            "replicas": 3
        }
    
    async def _deploy_training_scheduler(self) -> Dict[str, Any]:
        """Deploy intelligent training scheduler"""        scheduler = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "training-scheduler",
                "namespace": self.namespace,
                "labels": {"app": "training-scheduler", "component": "orchestration"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "training-scheduler"}},
                "template": {
                    "metadata": {"labels": {"app": "training-scheduler"}},
                    "spec": {
                        "containers": [{
                            "name": "scheduler",
                            "image": "ia-influencer/training-scheduler:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "SCHEDULER_TYPE", "value": "kubernetes"},
                                {"name": "GPU_SCHEDULING", "value": "true"},
                                {"name": "PRIORITY_SCHEDULING", "value": "true"},
                                {"name": "RESOURCE_OPTIMIZATION", "value": "true"},
                                {"name": "QUEUE_MANAGEMENT", "value": "true"},
                                {"name": "PREEMPTION_ENABLED", "value": "true"}
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
        
        # Deploy scheduler
        scheduler_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=scheduler
        )
        
        return {
            "deployment_id": scheduler_deployment.metadata.uid,
            "service": "training-scheduler",
            "features": ["gpu_scheduling", "priority_queuing", "resource_optimization"]
        }
    
    async def _deploy_experiment_tracker(self) -> Dict[str, Any]:
        """Deploy experiment tracking system (MLflow)"""        experiment_tracker = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "experiment-tracker",
                "namespace": self.namespace,
                "labels": {"app": "experiment-tracker", "component": "tracking"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "experiment-tracker"}},
                "template": {
                    "metadata": {"labels": {"app": "experiment-tracker"}},
                    "spec": {
                        "containers": [{
                            "name": "mlflow",
                            "image": "ia-influencer/mlflow-tracking:v1.0",
                            "ports": [{"containerPort": 5000}],
                            "env": [
                                {"name": "MLFLOW_BACKEND_STORE_URI", "value": "postgresql://mlflow_user:password@postgres:5432/mlflow"},
                                {"name": "MLFLOW_DEFAULT_ARTIFACT_ROOT", "value": "s3://training-artifacts/experiments"},
                                {"name": "MLFLOW_TRACKING_URI", "value": "http://0.0.0.0:5000"},
                                {"name": "MLFLOW_SERVE_ARTIFACTS", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "1Gi"},
                                "limits": {"cpu": "2000m", "memory": "4Gi"}
                            },
                            "volumeMounts": [{
                                "name": "artifacts-storage",
                                "mountPath": "/artifacts"
                            }]
                        }],
                        "volumes": [{
                            "name": "artifacts-storage",
                            "persistentVolumeClaim": {"claimName": "artifacts-storage-pvc"}
                        }]
                    }
                }
            }
        }
        
        # Deploy experiment tracker
        tracker_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=experiment_tracker
        )
        
        return {
            "deployment_id": tracker_deployment.metadata.uid,
            "service": "experiment-tracker",
            "features": ["experiment_logging", "artifact_storage", "model_registry"]
        }
    
    async def _deploy_hyperparameter_optimizer(self) -> Dict[str, Any]:
        """Deploy hyperparameter optimization system"""        hyperopt = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "hyperparameter-optimizer",
                "namespace": self.namespace,
                "labels": {"app": "hyperopt", "component": "optimization"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "hyperopt"}},
                "template": {
                    "metadata": {"labels": {"app": "hyperopt"}},
                    "spec": {
                        "containers": [{
                            "name": "optuna",
                            "image": "ia-influencer/optuna-optimizer:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "OPTUNA_STORAGE", "value": "postgresql://optuna_user:password@postgres:5432/optuna"},
                                {"name": "OPTIMIZATION_ALGORITHMS", "value": "tpe,random,cmaes,nsga2"},
                                {"name": "PARALLEL_TRIALS", "value": "10"},
                                {"name": "PRUNING_ENABLED", "value": "true"},
                                {"name": "DASHBOARD_ENABLED", "value": "true"}
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
        
        # Deploy hyperparameter optimizer
        hyperopt_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=hyperopt
        )
        
        return {
            "deployment_id": hyperopt_deployment.metadata.uid,
            "service": "hyperparameter-optimizer",
            "features": ["bayesian_optimization", "parallel_trials", "pruning", "multi_objective"]
        }
    
    async def _deploy_distributed_training(self) -> Dict[str, Any]:
        """Deploy distributed training infrastructure"""        # Ray cluster for distributed training
        ray_cluster = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "ray-cluster-head",
                "namespace": self.namespace,
                "labels": {"app": "ray-head", "component": "distributed"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "ray-head"}},
                "template": {
                    "metadata": {"labels": {"app": "ray-head"}},
                    "spec": {
                        "containers": [{
                            "name": "ray-head",
                            "image": "rayproject/ray:latest-gpu",
                            "ports": [
                                {"containerPort": 10001, "name": "client"},
                                {"containerPort": 8265, "name": "dashboard"},
                                {"containerPort": 6379, "name": "redis"}
                            ],
                            "command": ["ray", "start", "--head", "--dashboard-host=0.0.0.0", "--block"],
                            "env": [
                                {"name": "RAY_DISABLE_IMPORT_WARNING", "value": "1"},
                                {"name": "CUDA_VISIBLE_DEVICES", "value": "0,1,2,3"}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "2000m",
                                    "memory": "8Gi",
                                    "nvidia.com/gpu": "2"
                                },
                                "limits": {
                                    "cpu": "8000m",
                                    "memory": "32Gi",
                                    "nvidia.com/gpu": "4"
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        # Ray workers
        ray_workers = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "ray-workers",
                "namespace": self.namespace,
                "labels": {"app": "ray-workers", "component": "distributed"}
            },
            "spec": {
                "replicas": 4,
                "selector": {"matchLabels": {"app": "ray-workers"}},
                "template": {
                    "metadata": {"labels": {"app": "ray-workers"}},
                    "spec": {
                        "containers": [{
                            "name": "ray-worker",
                            "image": "rayproject/ray:latest-gpu",
                            "command": ["ray", "start", "--address=ray-cluster-head:10001", "--block"],
                            "env": [
                                {"name": "RAY_DISABLE_IMPORT_WARNING", "value": "1"},
                                {"name": "CUDA_VISIBLE_DEVICES", "value": "0,1,2,3"}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "4000m",
                                    "memory": "16Gi",
                                    "nvidia.com/gpu": "4"
                                },
                                "limits": {
                                    "cpu": "16000m",
                                    "memory": "64Gi",
                                    "nvidia.com/gpu": "8"
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        # Deploy Ray cluster
        head_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=ray_cluster
        )
        
        workers_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=ray_workers
        )
        
        return {
            "head_deployment_id": head_deployment.metadata.uid,
            "workers_deployment_id": workers_deployment.metadata.uid,
            "service": "ray-cluster",
            "features": ["distributed_training", "auto_scaling", "fault_tolerance"]
        }
    
    async def _deploy_training_storage(self) -> Dict[str, Any]:
        """Deploy high-performance training storage"""        # Fast SSD storage class for training data
        storage_class = {
            "apiVersion": "storage.k8s.io/v1",
            "kind": "StorageClass",
            "metadata": {
                "name": "training-fast-ssd",
                "namespace": self.namespace
            },
            "provisioner": "kubernetes.io/aws-ebs",
            "parameters": {
                "type": "gp3",
                "iops": "3000",
                "throughput": "125",
                "fsType": "ext4"
            },
            "volumeBindingMode": "WaitForFirstConsumer",
            "allowVolumeExpansion": True
        }
        
        # Training data PVC
        training_data_pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": "training-data-pvc",
                "namespace": self.namespace,
                "labels": {"app": "training-storage", "type": "data"}
            },
            "spec": {
                "accessModes": ["ReadWriteMany"],
                "storageClassName": "training-fast-ssd",
                "resources": {"requests": {"storage": "10Ti"}}
            }
        }
        
        # Model checkpoints PVC
        checkpoints_pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": "model-checkpoints-pvc",
                "namespace": self.namespace,
                "labels": {"app": "training-storage", "type": "checkpoints"}
            },
            "spec": {
                "accessModes": ["ReadWriteMany"],
                "storageClassName": "training-fast-ssd",
                "resources": {"requests": {"storage": "5Ti"}}
            }
        }
        
        # Deploy storage resources
        self.k8s_storage_v1.create_storage_class(body=storage_class)
        
        data_pvc = self.k8s_core_v1.create_namespaced_persistent_volume_claim(
            namespace=self.namespace,
            body=training_data_pvc
        )
        
        checkpoints_pvc_result = self.k8s_core_v1.create_namespaced_persistent_volume_claim(
            namespace=self.namespace,
            body=checkpoints_pvc
        )
        
        return {
            "storage_class": "training-fast-ssd",
            "data_pvc": data_pvc.metadata.uid,
            "checkpoints_pvc": checkpoints_pvc_result.metadata.uid,
            "features": ["high_iops", "fast_throughput", "expandable"]
        }
    
    async def _deploy_training_monitoring(self) -> Dict[str, Any]:
        """Deploy training monitoring and logging"""        training_monitor = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "training-monitor",
                "namespace": self.namespace,
                "labels": {"app": "training-monitor", "component": "observability"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "training-monitor"}},
                "template": {
                    "metadata": {"labels": {"app": "training-monitor"}},
                    "spec": {
                        "containers": [{
                            "name": "monitor",
                            "image": "ia-influencer/training-monitor:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "METRICS_COLLECTION", "value": "gpu_utilization,memory_usage,loss,accuracy,throughput"},
                                {"name": "LOG_AGGREGATION", "value": "true"},
                                {"name": "REAL_TIME_DASHBOARD", "value": "true"},
                                {"name": "ALERTING_ENABLED", "value": "true"},
                                {"name": "ANOMALY_DETECTION", "value": "true"}
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
        
        # Deploy training monitor
        monitor_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=training_monitor
        )
        
        return {
            "deployment_id": monitor_deployment.metadata.uid,
            "service": "training-monitor",
            "features": ["real_time_metrics", "log_aggregation", "anomaly_detection"]
        }
    
    async def _deploy_model_registry_integration(self) -> Dict[str, Any]:
        """Deploy model registry integration"""        registry_integration = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "model-registry-integration",
                "namespace": self.namespace,
                "labels": {"app": "registry-integration", "component": "deployment"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "registry-integration"}},
                "template": {
                    "metadata": {"labels": {"app": "registry-integration"}},
                    "spec": {
                        "containers": [{
                            "name": "registry",
                            "image": "ia-influencer/model-registry:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "AUTO_REGISTRATION", "value": "true"},
                                {"name": "MODEL_VALIDATION", "value": "true"},
                                {"name": "DEPLOYMENT_AUTOMATION", "value": "true"},
                                {"name": "VERSION_MANAGEMENT", "value": "semantic"},
                                {"name": "A_B_TESTING", "value": "true"}
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
        
        # Deploy registry integration
        registry_deployment = self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=registry_integration
        )
        
        return {
            "deployment_id": registry_deployment.metadata.uid,
            "service": "model-registry-integration",
            "features": ["auto_registration", "model_validation", "deployment_automation"]
        }
    
    async def _deploy_gpu_management(self) -> Dict[str, Any]:
        """Deploy GPU resource management for training"""        gpu_manager = {
            "apiVersion": "apps/v1",
            "kind": "DaemonSet",
            "metadata": {
                "name": "training-gpu-manager",
                "namespace": self.namespace,
                "labels": {"app": "gpu-manager", "component": "resource-management"}
            },
            "spec": {
                "selector": {"matchLabels": {"app": "gpu-manager"}},
                "template": {
                    "metadata": {"labels": {"app": "gpu-manager"}},
                    "spec": {
                        "containers": [{
                            "name": "gpu-manager",
                            "image": "ia-influencer/gpu-manager:v1.0",
                            "env": [
                                {"name": "NVIDIA_VISIBLE_DEVICES", "value": "all"},
                                {"name": "NVIDIA_DRIVER_CAPABILITIES", "value": "compute,utility"},
                                {"name": "GPU_SCHEDULING", "value": "true"},
                                {"name": "MEMORY_FRACTION_MANAGEMENT", "value": "true"},
                                {"name": "MULTI_TENANT_ISOLATION", "value": "true"}
                            ],
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "128Mi"},
                                "limits": {"cpu": "500m", "memory": "512Mi"}
                            },
                            "volumeMounts": [
                                {
                                    "name": "nvidia-driver",
                                    "mountPath": "/usr/local/nvidia",
                                    "readOnly": True
                                },
                                {
                                    "name": "proc",
                                    "mountPath": "/host/proc",
                                    "readOnly": True
                                }
                            ]
                        }],
                        "volumes": [
                            {
                                "name": "nvidia-driver",
                                "hostPath": {"path": "/usr/local/nvidia"}
                            },
                            {
                                "name": "proc",
                                "hostPath": {"path": "/proc"}
                            }
                        ],
                        "hostNetwork": True,
                        "hostPID": True
                    }
                }
            }
        }
        
        # Deploy GPU manager
        gpu_deployment = self.k8s_apps_v1.create_namespaced_daemon_set(
            namespace=self.namespace,
            body=gpu_manager
        )
        
        return {
            "deployment_id": gpu_deployment.metadata.uid,
            "service": "training-gpu-manager",
            "features": ["gpu_scheduling", "memory_management", "multi_tenant_isolation"]
        }
    
    async def _configure_training_networking(self) -> None:
        """Configure networking for training infrastructure"""        # Training network policy
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "training-network-policy",
                "namespace": self.namespace
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {"namespaceSelector": {"matchLabels": {"name": "ia-influencer"}}},
                            {"podSelector": {"matchLabels": {"component": "training"}}}
                        ]
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
        
        logger.info("Configured training networking policies")
    
    async def _validate_training_infrastructure(self) -> bool:
        """Validate training infrastructure deployment"""        try:
            # Check essential services
            essential_services = [
                "training-redis", "training-scheduler", "experiment-tracker",
                "hyperparameter-optimizer", "training-monitor"
            ]
            
            for service in essential_services:
                try:
                    deployment = self.k8s_apps_v1.read_namespaced_deployment(
                        name=service,
                        namespace=self.namespace
                    )
                    if not deployment.status.ready_replicas:
                        logger.warning(f"Training service {service} is not ready")
                        return False
                except Exception as e:
                    logger.error(f"Training service {service} validation failed: {e}")
                    return False
            
            # Test Redis connectivity
            try:
                self._redis_client.ping()
                logger.info("Training Redis connectivity validated")
            except Exception as e:
                logger.error(f"Training Redis validation failed: {e}")
                return False
            
            logger.info("Training infrastructure validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Training infrastructure validation failed: {e}")
            return False
    
    async def _validate_training_config(self, config: TrainingPipelineConfig) -> None:
        """Validate training configuration"""        if not config.pipeline_name:
            raise ValueError("Pipeline name is required")
        
        if config.num_nodes < 1:
            raise ValueError("Number of nodes must be at least 1")
        
        if config.num_gpus_per_node < 0:
            raise ValueError("Number of GPUs per node cannot be negative")
        
        if config.max_epochs <= 0:
            raise ValueError("Max epochs must be positive")
        
        if config.batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        logger.info(f"Training config validation passed for {config.pipeline_name}")
    
    async def _create_training_job_spec(self, config: TrainingPipelineConfig, job_id: str) -> Dict[str, Any]:
        """Create Kubernetes job specification for training"""        job_spec = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"training-job-{job_id}",
                "namespace": self.namespace,
                "labels": {
                    "app": "training-job",
                    "job-id": job_id,
                    "pipeline-name": config.pipeline_name,
                    "framework": config.framework.value,
                    "training-type": config.training_type.value
                }
            },
            "spec": {
                "parallelism": config.num_nodes,
                "completions": config.num_nodes,
                "template": {
                    "metadata": {
                        "labels": {"app": "training-job", "job-id": job_id},
                        "annotations": {
                            "training-config": json.dumps({
                                "framework": config.framework.value,
                                "training_type": config.training_type.value,
                                "max_epochs": config.max_epochs,
                                "batch_size": config.batch_size,
                                "learning_rate": config.learning_rate
                            })
                        }
                    },
                    "spec": {
                        "restartPolicy": "OnFailure",
                        "containers": [{
                            "name": "training",
                            "image": f"ia-influencer/training-{config.framework.value}:v1.0",
                            "env": [
                                {"name": "JOB_ID", "value": job_id},
                                {"name": "PIPELINE_NAME", "value": config.pipeline_name},
                                {"name": "FRAMEWORK", "value": config.framework.value},
                                {"name": "TRAINING_TYPE", "value": config.training_type.value},
                                {"name": "MAX_EPOCHS", "value": str(config.max_epochs)},
                                {"name": "BATCH_SIZE", "value": str(config.batch_size)},
                                {"name": "LEARNING_RATE", "value": str(config.learning_rate)},
                                {"name": "DISTRIBUTED_BACKEND", "value": config.distributed_backend},
                                {"name": "MIXED_PRECISION", "value": str(config.mixed_precision).lower()},
                                {"name": "GRADIENT_ACCUMULATION_STEPS", "value": str(config.gradient_accumulation_steps)}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "4000m",
                                    "memory": "16Gi",
                                    "nvidia.com/gpu": str(config.num_gpus_per_node)
                                },
                                "limits": config.resource_limits
                            },
                            "volumeMounts": [
                                {
                                    "name": "training-data",
                                    "mountPath": "/data"
                                },
                                {
                                    "name": "model-checkpoints",
                                    "mountPath": "/checkpoints"
                                }
                            ]
                        }],
                        "volumes": [
                            {
                                "name": "training-data",
                                "persistentVolumeClaim": {"claimName": "training-data-pvc"}
                            },
                            {
                                "name": "model-checkpoints",
                                "persistentVolumeClaim": {"claimName": "model-checkpoints-pvc"}
                            }
                        ],
                        "nodeSelector": {"accelerator": "nvidia-tesla-v100"}
                    }
                }
            }
        }
        
        return job_spec
    
    async def _submit_single_node_job(self, config: TrainingPipelineConfig, job_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Submit single-node training job"""        # Adjust for single node
        job_spec["spec"]["parallelism"] = 1
        job_spec["spec"]["completions"] = 1
        
        # Submit job
        job = self.k8s_batch_v1.create_namespaced_job(
            namespace=self.namespace,
            body=job_spec
        )
        
        return {
            "job_id": job.metadata.uid,
            "job_name": job.metadata.name,
            "type": "single_node"
        }
    
    async def _submit_multi_node_job(self, config: TrainingPipelineConfig, job_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Submit multi-node training job"""        # Configure for multi-node
        job_spec["spec"]["template"]["spec"]["containers"][0]["env"].extend([
            {"name": "WORLD_SIZE", "value": str(config.num_nodes)},
            {"name": "MASTER_ADDR", "value": "training-job-master"},
            {"name": "MASTER_PORT", "value": "29500"}
        ])
        
        # Submit job
        job = self.k8s_batch_v1.create_namespaced_job(
            namespace=self.namespace,
            body=job_spec
        )
        
        return {
            "job_id": job.metadata.uid,
            "job_name": job.metadata.name,
            "type": "multi_node",
            "nodes": config.num_nodes
        }
    
    async def _submit_distributed_job(self, config: TrainingPipelineConfig, job_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Submit distributed training job"""        # Configure for distributed training with Ray
        job_spec["spec"]["template"]["spec"]["containers"][0]["env"].extend([
            {"name": "RAY_ADDRESS", "value": "ray://ray-cluster-head:10001"},
            {"name": "DISTRIBUTED_BACKEND", "value": config.distributed_backend},
            {"name": "NPROC_PER_NODE", "value": str(config.num_gpus_per_node)}
        ])
        
        # Submit job
        job = self.k8s_batch_v1.create_namespaced_job(
            namespace=self.namespace,
            body=job_spec
        )
        
        return {
            "job_id": job.metadata.uid,
            "job_name": job.metadata.name,
            "type": "distributed",
            "ray_cluster": "ray-cluster-head"
        }
    
    async def _submit_hyperparameter_job(self, config: TrainingPipelineConfig, job_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Submit hyperparameter tuning job"""        # Configure for hyperparameter tuning
        job_spec["spec"]["template"]["spec"]["containers"][0]["env"].extend([
            {"name": "HYPEROPT_ENABLED", "value": "true"},
            {"name": "OPTIMIZATION_STRATEGY", "value": config.optimization_strategy.value},
            {"name": "OPTUNA_STUDY_NAME", "value": f"study-{config.pipeline_name}"},
            {"name": "N_TRIALS", "value": "100"}
        ])
        
        # Submit job
        job = self.k8s_batch_v1.create_namespaced_job(
            namespace=self.namespace,
            body=job_spec
        )
        
        return {
            "job_id": job.metadata.uid,
            "job_name": job.metadata.name,
            "type": "hyperparameter_tuning",
            "optimization_strategy": config.optimization_strategy.value
        }
    
    async def _submit_custom_job(self, config: TrainingPipelineConfig, job_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Submit custom training job"""        # Submit as-is for custom jobs
        job = self.k8s_batch_v1.create_namespaced_job(
            namespace=self.namespace,
            body=job_spec
        )
        
        return {
            "job_id": job.metadata.uid,
            "job_name": job.metadata.name,
            "type": "custom"
        }
    
    async def _setup_job_monitoring(self, job_id: str, config: TrainingPipelineConfig) -> None:
        """Set up monitoring for training job"""        monitoring_config = {
            "job_id": job_id,
            "pipeline_name": config.pipeline_name,
            "framework": config.framework.value,
            "metrics": ["loss", "accuracy", "gpu_utilization", "memory_usage"],
            "alerting": True,
            "real_time_tracking": True
        }
        
        self._redis_client.hset(
            f"job:monitoring:{job_id}",
            mapping=monitoring_config
        )
        
        logger.info(f"Configured monitoring for job {job_id}")
    
    async def _setup_experiment_tracking(self, job_id: str, config: TrainingPipelineConfig) -> None:
        """Set up experiment tracking for training job"""        experiment_config = {
            "job_id": job_id,
            "experiment_name": f"{config.pipeline_name}-{job_id}",
            "framework": config.framework.value,
            "parameters": {
                "max_epochs": config.max_epochs,
                "batch_size": config.batch_size,
                "learning_rate": config.learning_rate,
                "num_nodes": config.num_nodes,
                "num_gpus": config.num_gpus_per_node
            },
            "tracking_enabled": True,
            "artifact_logging": True
        }
        
        self._redis_client.hset(
            f"job:experiment:{job_id}",
            mapping=experiment_config
        )
        
        logger.info(f"Configured experiment tracking for job {job_id}")
    
    def _estimate_training_duration(self, config: TrainingPipelineConfig) -> str:
        """Estimate training duration based on configuration"""        # Simple estimation logic (can be made more sophisticated)
        base_time = config.max_epochs * 5  # 5 minutes per epoch base
        
        # Adjust based on distributed training
        if config.training_type == TrainingType.DISTRIBUTED:
            base_time = base_time / max(1, config.num_nodes * 0.8)
        
        # Adjust based on GPU count
        gpu_speedup = 1 + (config.num_gpus_per_node - 1) * 0.7
        base_time = base_time / gpu_speedup
        
        hours = int(base_time // 60)
        minutes = int(base_time % 60)
        
        return f"{hours}h {minutes}m"
    
    async def get_training_metrics(self) -> Dict[str, Any]:
        """Get comprehensive training metrics"""        try:
            metrics = {
                "infrastructure_status": self.status,
                "active_pipelines": len(self.active_pipelines),
                "completed_pipelines": len(self.completed_pipelines),
                "total_jobs": len(self.training_jobs),
                "gpu_utilization": self._redis_client.get("gpu_utilization") or "0",
                "training_throughput": self._redis_client.get("training_throughput") or "0",
                "average_job_duration": self._redis_client.get("average_job_duration") or "0",
                "success_rate": self._redis_client.get("success_rate") or "0",
                "pipelines": {}
            }
            
            # Get per-pipeline metrics
            for pipeline_id, pipeline_info in self.active_pipelines.items():
                pipeline_metrics = {
                    "status": pipeline_info["status"],
                    "framework": pipeline_info["framework"],
                    "training_type": pipeline_info["training_type"],
                    "submitted_at": pipeline_info["submitted_at"],
                    "current_epoch": self._redis_client.get(f"job:epoch:{pipeline_id}") or "0",
                    "loss": self._redis_client.get(f"job:loss:{pipeline_id}") or "0",
                    "accuracy": self._redis_client.get(f"job:accuracy:{pipeline_id}") or "0"
                }
                metrics["pipelines"][pipeline_id] = pipeline_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get training metrics: {e}")
            return {"error": str(e)}
    
    async def _cleanup_failed_infrastructure(self) -> None:
        """Clean up failed training infrastructure"""        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            logger.info("Cleaned up failed training infrastructure")
        except Exception as e:
            logger.error(f"Training infrastructure cleanup failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up entire training infrastructure"""        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            
            self.status = "stopped"
            self.active_pipelines = {}
            self.completed_pipelines = {}
            self.training_jobs = {}
            
            logger.info("Training infrastructure cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Training cleanup failed: {e}")
            raise
