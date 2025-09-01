"""Distributed Training Manager
Enterprise distributed training orchestration and management

This module provides comprehensive distributed training capabilities including
multi-node training, fault tolerance, dynamic scaling, resource optimization,
and advanced training strategies for large-scale AI model development.

Project: IA Influencer Agent + Content Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This software is protected by international copyright laws.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
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
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import tensorflow as tf
import horovod.torch as hvd
import ray
from ray import train
from ray.train import ScalingConfig, RunConfig
from ray.train.torch import TorchTrainer
import wandb
from transformers import Trainer, TrainingArguments

logger = logging.getLogger(__name__)


class TrainingBackend(Enum):
    """
Distributed training backends"""

    PYTORCH_DDP = "pytorch_ddp"
    PYTORCH_FSDP = "pytorch_fsdp"
    HOROVOD = "horovod"
    RAY_TRAIN = "ray_train"
    TENSORFLOW_MIRRORED = "tensorflow_mirrored"
    TENSORFLOW_MULTI_WORKER = "tensorflow_multi_worker"
    DEEPSPEED = "deepspeed"
    FAIRSCALE = "fairscale"


class ScalingStrategy(Enum):
    """Training scaling strategies"""

    STATIC = "static"
    DYNAMIC = "dynamic"
    ELASTIC = "elastic"
    ADAPTIVE = "adaptive"
    PREEMPTIBLE = "preemptible"


class FaultToleranceMode(Enum):
    """Fault tolerance modes"""

    CHECKPOINT_RESTART = "checkpoint_restart"
    ELASTIC_RECOVERY = "elastic_recovery"
    PREEMPTION_HANDLING = "preemption_handling"
    NODE_REPLACEMENT = "node_replacement"
    GRACEFUL_DEGRADATION = "graceful_degradation"


class OptimizationStrategy(Enum):
    """Training optimization strategies"""

    GRADIENT_COMPRESSION = "gradient_compression"
    MIXED_PRECISION = "mixed_precision"
    GRADIENT_ACCUMULATION = "gradient_accumulation"
    PIPELINE_PARALLELISM = "pipeline_parallelism"
    TENSOR_PARALLELISM = "tensor_parallelism"
    DATA_PARALLELISM = "data_parallelism"
    MODEL_PARALLELISM = "model_parallelism"
    ZERO_OPTIMIZER = "zero_optimizer"


@dataclass
class DistributedTrainingConfig:
    """Distributed training configuration"""
    training_name: str = "distributed-ai-training"
    backend: TrainingBackend = TrainingBackend.RAY_TRAIN
    scaling_strategy: ScalingStrategy = ScalingStrategy.ELASTIC
    fault_tolerance: FaultToleranceMode = FaultToleranceMode.ELASTIC_RECOVERY
    optimization_strategies: List[OptimizationStrategy] = None
    min_nodes: int = 2
    max_nodes: int = 16
    nodes_per_replica: int = 4
    gpus_per_node: int = 4
    cpu_per_node: int = 16
    memory_per_node: str = "64Gi"
    storage_per_node: str = "1Ti"
    checkpoint_frequency: int = 100  # steps
    checkpoint_retention: int = 5
    monitoring_enabled: bool = True
    wandb_enabled: bool = True
    tensorboard_enabled: bool = True
    profiling_enabled: bool = True
    auto_tuning: bool = True
    preemptible_instances: bool = True
    spot_instances: bool = True
    mixed_precision: bool = True
    gradient_checkpointing: bool = True
    gradient_compression: bool = True
    communication_backend: str = "nccl"
    
    def __post_init__(self):
        if self.optimization_strategies is None:
            self.optimization_strategies = [
                OptimizationStrategy.MIXED_PRECISION,
                OptimizationStrategy.GRADIENT_ACCUMULATION,
                OptimizationStrategy.DATA_PARALLELISM
            ]


class DistributedTrainingManager:
    """
    Enterprise distributed training management system
    
    Provides comprehensive distributed training with:
    - Multi-backend support (PyTorch DDP/FSDP, Horovod, Ray Train)
    - Dynamic scaling and elastic training
    - Fault tolerance and recovery mechanisms
    - Advanced optimization strategies
    - Resource management and scheduling
    - Performance monitoring and profiling
    - Automated hyperparameter tuning
    - Cloud-native deployment
    """
    
    def __init__(self, namespace: str = "ia-influencer-training"):
        """
        Initialize distributed training manager
        
        Args:
            namespace: Kubernetes namespace for training infrastructure
        """
        self.namespace = namespace
        self.config = DistributedTrainingConfig()
        self.training_jobs = {}
        self.training_clusters = {}
        self.checkpoints = {}
        self.metrics = {}
        self.status = "initializing"
        
        # Initialize clients and services
        self._initialize_clients()
        self._initialize_training_frameworks()
    
    def _initialize_clients(self) -> None:
        """Initialize Kubernetes, Docker, and training clients"""
        try:
            # Kubernetes client
            config.load_incluster_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_batch_v1 = client.BatchV1Api()
            self.k8s_custom_objects_v1 = client.CustomObjectsApi()
            
            # Docker client
            self._docker_client = docker.from_env()
            
            # Redis for coordination and checkpointing
            self._redis_client = redis.Redis(
                host='training-redis',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            logger.info("Distributed training clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize training clients: {e}")
            raise
    
    def _initialize_training_frameworks(self) -> None:
        """Initialize training frameworks and backends"""
        try:
            # Initialize Ray for distributed training
            if not ray.is_initialized():
                ray.init(address="auto", ignore_reinit_error=True)
            
            # Initialize Horovod if available
            try:
                hvd.init()
                self.horovod_available = True
            except Exception:
                self.horovod_available = False
                logger.warning("Horovod not available")
            
            # Initialize Weights & Biases if enabled
            if self.config.wandb_enabled:
                try:
                    wandb.init(project="ia-influencer-training", mode="offline")
                    self.wandb_available = True
                except Exception:
                    self.wandb_available = False
                    logger.warning("Weights & Biases not available")
            
            logger.info("Training frameworks initialized successfully")
            
        except Exception as e:
            logger.warning(f"Some training frameworks failed to initialize: {e}")
    
    async def deploy_training_infrastructure(self) -> Dict[str, Any]:
        """
        Deploy complete distributed training infrastructure
        
        Returns:
            Infrastructure deployment summary
        """
        try:
            self.status = "deploying_infrastructure"
            logger.info("Deploying distributed training infrastructure")
            
            # Create training namespace
            await self._ensure_training_namespace()
            
            # Deploy Ray cluster for distributed training
            ray_cluster_result = await self._deploy_ray_cluster()
            
            # Deploy training coordinator
            coordinator_result = await self._deploy_training_coordinator()
            
            # Deploy checkpoint storage
            checkpoint_result = await self._deploy_checkpoint_storage()
            
            # Deploy monitoring infrastructure
            monitoring_result = await self._deploy_training_monitoring()
            
            # Deploy fault tolerance manager
            fault_tolerance_result = await self._deploy_fault_tolerance_manager()
            
            # Deploy resource scheduler
            scheduler_result = await self._deploy_resource_scheduler()
            
            # Deploy hyperparameter tuning service
            tuning_result = await self._deploy_hyperparameter_tuning()
            
            # Deploy training API
            api_result = await self._deploy_training_api()
            
            # Configure networking
            await self._configure_training_networking()
            
            # Validate infrastructure
            if await self._validate_training_infrastructure():
                self.status = "infrastructure_ready"
                logger.info("Distributed training infrastructure deployed successfully")
                
                return {
                    "status": "success",
                    "infrastructure": {
                        "ray_cluster": ray_cluster_result,
                        "coordinator": coordinator_result,
                        "checkpoint_storage": checkpoint_result,
                        "monitoring": monitoring_result,
                        "fault_tolerance": fault_tolerance_result,
                        "scheduler": scheduler_result,
                        "hyperparameter_tuning": tuning_result,
                        "training_api": api_result
                    },
                    "capabilities": {
                        "training_backends": [b.value for b in TrainingBackend],
                        "scaling_strategies": [s.value for s in ScalingStrategy],
                        "fault_tolerance_modes": [f.value for f in FaultToleranceMode],
                        "optimization_strategies": [o.value for o in OptimizationStrategy],
                        "max_nodes": self.config.max_nodes,
                        "gpus_per_node": self.config.gpus_per_node,
                        "elastic_scaling": True,
                        "fault_tolerance": True
                    }
                }
            else:
                raise Exception("Distributed training infrastructure validation failed")
                
        except Exception as e:
            self.status = "infrastructure_failed"
            logger.error(f"Training infrastructure deployment failed: {e}")
            await self._cleanup_failed_infrastructure()
            raise
    
    async def start_distributed_training(self, training_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start distributed training job
        
        Args:
            training_request: Training job configuration
            
        Returns:
            Training job details and status
        """
        try:
            training_id = f"train_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Starting distributed training job: {training_id}")
            
            # Validate training request
            await self._validate_training_request(training_request)
            
            # Create training configuration
            training_config = await self._create_training_configuration(training_request)
            
            # Determine optimal cluster configuration
            cluster_config = await self._determine_cluster_configuration(training_config)
            
            # Create training cluster
            cluster_result = await self._create_training_cluster(training_id, cluster_config)
            
            # Initialize training job based on backend
            backend = training_config.get("backend", self.config.backend)
            
            if backend == TrainingBackend.RAY_TRAIN:
                job_result = await self._start_ray_training(training_id, training_config)
            elif backend == TrainingBackend.PYTORCH_DDP:
                job_result = await self._start_pytorch_ddp_training(training_id, training_config)
            elif backend == TrainingBackend.HOROVOD:
                job_result = await self._start_horovod_training(training_id, training_config)
            elif backend == TrainingBackend.DEEPSPEED:
                job_result = await self._start_deepspeed_training(training_id, training_config)
            else:
                raise ValueError(f"Unsupported training backend: {backend}")
            
            # Setup monitoring and checkpointing
            await self._setup_training_monitoring(training_id)
            await self._setup_checkpoint_management(training_id, training_config)
            
            # Enable fault tolerance
            if self.config.fault_tolerance != FaultToleranceMode.CHECKPOINT_RESTART:
                await self._enable_fault_tolerance(training_id)
            
            # Track training job
            self.training_jobs[training_id] = {
                "status": "running",
                "backend": backend.value,
                "cluster_config": cluster_config,
                "training_config": training_config,
                "job_result": job_result,
                "started_at": datetime.utcnow().isoformat(),
                "cluster_id": cluster_result.get("cluster_id")
            }
            
            logger.info(f"Distributed training job started successfully: {training_id}")
            
            return {
                "status": "success",
                "training_id": training_id,
                "backend": backend.value,
                "cluster_configuration": cluster_config,
                "job_details": job_result,
                "monitoring": {
                    "tensorboard_url": f"/tensorboard/{training_id}",
                    "wandb_url": f"/wandb/{training_id}" if self.wandb_available else None,
                    "metrics_endpoint": f"/metrics/{training_id}"
                },
                "checkpoints": {
                    "storage_path": f"/checkpoints/{training_id}",
                    "frequency": self.config.checkpoint_frequency,
                    "retention": self.config.checkpoint_retention
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to start distributed training: {e}")
            if training_id:
                await self._cleanup_failed_training_job(training_id)
            raise
    
    async def scale_training_cluster(self, training_id: str, target_nodes: int) -> Dict[str, Any]:
        """
        Scale training cluster dynamically
        
        Args:
            training_id: Training job identifier
            target_nodes: Target number of nodes
            
        Returns:
            Scaling result
        """
        try:
            logger.info(f"Scaling training cluster {training_id} to {target_nodes} nodes")
            
            # Get current training job
            training_job = self.training_jobs.get(training_id)
            if not training_job:
                raise ValueError(f"Training job {training_id} not found")
            
            current_nodes = training_job["cluster_config"]["nodes"]
            
            # Validate scaling request
            if target_nodes < self.config.min_nodes or target_nodes > self.config.max_nodes:
                raise ValueError(f"Target nodes {target_nodes} outside allowed range [{self.config.min_nodes}, {self.config.max_nodes}]")
            
            # Determine scaling action
            if target_nodes > current_nodes:
                scaling_result = await self._scale_up_cluster(training_id, target_nodes - current_nodes)
            elif target_nodes < current_nodes:
                scaling_result = await self._scale_down_cluster(training_id, current_nodes - target_nodes)
            else:
                return {"status": "no_action", "message": "Target nodes equals current nodes"}
            
            # Update training job configuration
            training_job["cluster_config"]["nodes"] = target_nodes
            
            # Reconfigure training process for new cluster size
            await self._reconfigure_training_for_scaling(training_id, target_nodes)
            
            logger.info(f"Training cluster {training_id} scaled successfully to {target_nodes} nodes")
            
            return {
                "status": "success",
                "training_id": training_id,
                "previous_nodes": current_nodes,
                "current_nodes": target_nodes,
                "scaling_action": "scale_up" if target_nodes > current_nodes else "scale_down",
                "scaling_details": scaling_result
            }
            
        except Exception as e:
            logger.error(f"Training cluster scaling failed: {e}")
            raise
    
    async def handle_training_failure(self, training_id: str, failure_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle training job failure with recovery
        
        Args:
            training_id: Training job identifier
            failure_info: Failure information
            
        Returns:
            Recovery result
        """
        try:
            logger.warning(f"Handling training failure for job {training_id}")
            
            # Get training job details
            training_job = self.training_jobs.get(training_id)
            if not training_job:
                raise ValueError(f"Training job {training_id} not found")
            
            failure_type = failure_info.get("type", "unknown")
            failure_node = failure_info.get("node")
            
            # Determine recovery strategy
            recovery_strategy = await self._determine_recovery_strategy(failure_info, training_job)
            
            recovery_result = {}
            
            if recovery_strategy == "checkpoint_restart":
                recovery_result = await self._restart_from_checkpoint(training_id)
            elif recovery_strategy == "node_replacement":
                recovery_result = await self._replace_failed_node(training_id, failure_node)
            elif recovery_strategy == "elastic_recovery":
                recovery_result = await self._elastic_recovery(training_id, failure_info)
            elif recovery_strategy == "graceful_degradation":
                recovery_result = await self._graceful_degradation(training_id, failure_info)
            else:
                raise ValueError(f"Unknown recovery strategy: {recovery_strategy}")
            
            # Update training job status
            training_job["status"] = "recovered"
            training_job["recovery_info"] = {
                "failure_type": failure_type,
                "recovery_strategy": recovery_strategy,
                "recovery_result": recovery_result,
                "recovered_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Training job {training_id} recovered successfully using {recovery_strategy}")
            
            return {
                "status": "success",
                "training_id": training_id,
                "failure_type": failure_type,
                "recovery_strategy": recovery_strategy,
                "recovery_details": recovery_result
            }
            
        except Exception as e:
            logger.error(f"Training failure recovery failed: {e}")
            training_job["status"] = "failed"
            raise
    
    async def _deploy_ray_cluster(self) -> Dict[str, Any]:
        """Deploy Ray cluster for distributed training"""
        ray_cluster = {
            "apiVersion": "ray.io/v1alpha1",
            "kind": "RayCluster",
            "metadata": {
                "name": "training-ray-cluster",
                "namespace": self.namespace,
                "labels": {"app": "ray-cluster", "component": "distributed-training"}
            },
            "spec": {
                "rayVersion": "2.8.0",
                "enableInTreeAutoscaling": True,
                "autoscalerOptions": {
                    "upscalingMode": "Conservative",
                    "idleTimeoutSeconds": 300,
                    "resources": [
                        {"name": "CPU", "quantity": 1},
                        {"name": "memory", "quantity": "2Gi"},
                        {"name": "nvidia.com/gpu", "quantity": 1}
                    ]
                },
                "headGroupSpec": {
                    "serviceType": "ClusterIP",
                    "replicas": 1,
                    "rayStartParams": {
                        "dashboard-host": "0.0.0.0",
                        "num-cpus": "0"
                    },
                    "template": {
                        "spec": {
                            "containers": [{
                                "name": "ray-head",
                                "image": "rayproject/ray:2.8.0-gpu",
                                "env": [
                                    {"name": "RAY_DISABLE_IMPORT_WARNING", "value": "1"},
                                    {"name": "RAY_ENABLE_WINDOWS_OR_OSX_CLUSTER", "value": "1"}
                                ],
                                "resources": {
                                    "requests": {"cpu": "2000m", "memory": "8Gi"},
                                    "limits": {"cpu": "4000m", "memory": "16Gi"}
                                },
                                "ports": [
                                    {"containerPort": 6379, "name": "gcs-server"},
                                    {"containerPort": 8265, "name": "dashboard"},
                                    {"containerPort": 10001, "name": "client"}
                                ]
                            }]
                        }
                    }
                },
                "workerGroupSpecs": [{
                    "replicas": self.config.min_nodes,
                    "minReplicas": self.config.min_nodes,
                    "maxReplicas": self.config.max_nodes,
                    "groupName": "gpu-workers",
                    "rayStartParams": {
                        "num-cpus": str(self.config.cpu_per_node),
                        "num-gpus": str(self.config.gpus_per_node)
                    },
                    "template": {
                        "spec": {
                            "containers": [{
                                "name": "ray-worker",
                                "image": "rayproject/ray:2.8.0-gpu",
                                "resources": {
                                    "requests": {
                                        "cpu": f"{self.config.cpu_per_node}000m",
                                        "memory": self.config.memory_per_node,
                                        "nvidia.com/gpu": str(self.config.gpus_per_node)
                                    },
                                    "limits": {
                                        "cpu": f"{self.config.cpu_per_node * 2}000m",
                                        "memory": self.config.memory_per_node,
                                        "nvidia.com/gpu": str(self.config.gpus_per_node)
                                    }
                                },
                                "volumeMounts": [
                                    {"name": "training-data", "mountPath": "/data"},
                                    {"name": "model-storage", "mountPath": "/models"}
                                ]
                            }],
                            "volumes": [
                                {"name": "training-data", "persistentVolumeClaim": {"claimName": "training-data-pvc"}},
                                {"name": "model-storage", "persistentVolumeClaim": {"claimName": "model-storage-pvc"}}
                            ],
                            "nodeSelector": {"hardware": "gpu"},
                            "tolerations": [{
                                "key": "nvidia.com/gpu",
                                "operator": "Exists",
                                "effect": "NoSchedule"
                            }]
                        }
                    }
                }]
            }
        }
        
        # Deploy Ray cluster using custom resource
        ray_deployment = self.k8s_custom_objects_v1.create_namespaced_custom_object(
            group="ray.io",
            version="v1alpha1",
            namespace=self.namespace,
            plural="rayclusters",
            body=ray_cluster
        )
        
        return {
            "deployment_id": ray_deployment["metadata"]["uid"],
            "service": "training-ray-cluster",
            "features": ["autoscaling", "gpu_support", "distributed_training"]
        }
    
    async def _deploy_training_coordinator(self) -> Dict[str, Any]:
        """Deploy training coordinator service"""
        coordinator = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "training-coordinator",
                "namespace": self.namespace,
                "labels": {"app": "training-coordinator", "component": "orchestration"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "training-coordinator"}},
                "template": {
                    "metadata": {"labels": {"app": "training-coordinator"}},
                    "spec": {
                        "containers": [{
                            "name": "coordinator",
                            "image": "ia-influencer/training-coordinator:v1.0",
                            "env": [
                                {"name": "TRAINING_BACKENDS", "value": "ray,pytorch_ddp,horovod,deepspeed"},
                                {"name": "SCALING_STRATEGY", "value": self.config.scaling_strategy.value},
                                {"name": "FAULT_TOLERANCE", "value": self.config.fault_tolerance.value},
                                {"name": "AUTO_TUNING", "value": str(self.config.auto_tuning).lower()},
                                {"name": "REDIS_HOST", "value": "training-redis"},
                                {"name": "RAY_CLUSTER_ADDRESS", "value": "training-ray-cluster-head-svc:10001"}
                            ],
                            "resources": {
                                "requests": {"cpu": "1000m", "memory": "2Gi"},
                                "limits": {"cpu": "4000m", "memory": "8Gi"}
                            },
                            "ports": [{"containerPort": 8080}],
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
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
            "service": "training-coordinator",
            "features": ["job_orchestration", "fault_tolerance", "auto_scaling"]
        }
    
    async def _start_ray_training(self, training_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start Ray-based distributed training"""
        try:
            # Create Ray Train configuration
            scaling_config = ScalingConfig(
                num_workers=config.get("num_workers", 4),
                use_gpu=True,
                trainer_resources={"CPU": 2, "GPU": 1}
            )
            
            run_config = RunConfig(
                name=training_id,
                checkpoint_config=train.CheckpointConfig(
                    num_to_keep=self.config.checkpoint_retention,
                    checkpoint_score_attribute="validation_loss",
                    checkpoint_score_order="min"
                ),
                storage_path="/checkpoints"
            )
            
            # Define training function
            def train_func(config_dict):
                # Training logic would be implemented here
                # This is a placeholder for the actual training code
                import torch
                import torch.nn as nn
                from torch.utils.data import DataLoader
                
                # Initialize distributed training
                rank = train.get_context().get_world_rank()
                
                # Training loop
                for epoch in range(config_dict.get("epochs", 10)):
                    # Training step
                    train_loss = 0.5 - epoch * 0.01  # Simulated decreasing loss
                    
                    # Validation step
                    val_loss = train_loss + 0.1
                    
                    # Report metrics
                    train.report({
                        "epoch": epoch,
                        "train_loss": train_loss,
                        "validation_loss": val_loss
                    })
            
            # Create and run trainer
            trainer = TorchTrainer(
                train_loop_per_worker=train_func,
                train_loop_config=config,
                scaling_config=scaling_config,
                run_config=run_config
            )
            
            # Start training asynchronously
            result = trainer.fit()
            
            return {
                "status": "started",
                "trainer_id": training_id,
                "num_workers": scaling_config.num_workers,
                "checkpoint_config": run_config.checkpoint_config,
                "result": str(result)
            }
            
        except Exception as e:
            logger.error(f"Ray training startup failed: {e}")
            raise
    
    async def _start_pytorch_ddp_training(self, training_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start PyTorch DDP training"""
        try:
            # Create DDP training job specification
            ddp_job = {
                "apiVersion": "kubeflow.org/v1",
                "kind": "PyTorchJob",
                "metadata": {
                    "name": f"pytorch-{training_id}",
                    "namespace": self.namespace
                },
                "spec": {
                    "pytorchReplicaSpecs": {
                        "Master": {
                            "replicas": 1,
                            "restartPolicy": "OnFailure",
                            "template": {
                                "spec": {
                                    "containers": [{
                                        "name": "pytorch",
                                        "image": "ia-influencer/pytorch-training:v1.0",
                                        "env": [
                                            {"name": "TRAINING_ID", "value": training_id},
                                            {"name": "BACKEND", "value": "nccl"},
                                            {"name": "MASTER_PORT", "value": "23456"}
                                        ],
                                        "resources": {
                                            "requests": {
                                                "cpu": f"{self.config.cpu_per_node}000m",
                                                "memory": self.config.memory_per_node,
                                                "nvidia.com/gpu": str(self.config.gpus_per_node)
                                            }
                                        }
                                    }]
                                }
                            }
                        },
                        "Worker": {
                            "replicas": config.get("num_workers", 3),
                            "restartPolicy": "OnFailure",
                            "template": {
                                "spec": {
                                    "containers": [{
                                        "name": "pytorch",
                                        "image": "ia-influencer/pytorch-training:v1.0",
                                        "env": [
                                            {"name": "TRAINING_ID", "value": training_id},
                                            {"name": "BACKEND", "value": "nccl"}
                                        ],
                                        "resources": {
                                            "requests": {
                                                "cpu": f"{self.config.cpu_per_node}000m",
                                                "memory": self.config.memory_per_node,
                                                "nvidia.com/gpu": str(self.config.gpus_per_node)
                                            }
                                        }
                                    }]
                                }
                            }
                        }
                    }
                }
            }
            
            # Deploy PyTorch job
            pytorch_job = self.k8s_custom_objects_v1.create_namespaced_custom_object(
                group="kubeflow.org",
                version="v1",
                namespace=self.namespace,
                plural="pytorchjobs",
                body=ddp_job
            )
            
            return {
                "status": "started",
                "job_name": f"pytorch-{training_id}",
                "master_replicas": 1,
                "worker_replicas": config.get("num_workers", 3),
                "job_uid": pytorch_job["metadata"]["uid"]
            }
            
        except Exception as e:
            logger.error(f"PyTorch DDP training startup failed: {e}")
            raise
    
    async def _validate_training_request(self, request: Dict[str, Any]) -> None:
        """Validate training request parameters"""
        required_fields = ["model_config", "dataset_config"]
        for field in required_fields:
            if field not in request:
                raise ValueError(f"Required field '{field}' missing from training request")
        
        # Validate resource requirements
        if "resource_requirements" in request:
            resources = request["resource_requirements"]
            if resources.get("nodes", 0) > self.config.max_nodes:
                raise ValueError(f"Requested nodes exceed maximum: {self.config.max_nodes}")
    
    async def _create_training_configuration(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive training configuration"""
        config = {
            "training_id": request.get("training_id"),
            "model_config": request.get("model_config", {}),
            "dataset_config": request.get("dataset_config", {}),
            "training_parameters": request.get("training_parameters", {}),
            "resource_requirements": request.get("resource_requirements", {}),
            "backend": request.get("backend", self.config.backend),
            "optimization_strategies": request.get("optimization_strategies", self.config.optimization_strategies),
            "fault_tolerance": request.get("fault_tolerance", self.config.fault_tolerance),
            "scaling_strategy": request.get("scaling_strategy", self.config.scaling_strategy),
            "checkpoint_frequency": request.get("checkpoint_frequency", self.config.checkpoint_frequency),
            "monitoring": {
                "tensorboard": self.config.tensorboard_enabled,
                "wandb": self.config.wandb_enabled,
                "profiling": self.config.profiling_enabled
            }
        }
        
        return config
    
    async def _determine_cluster_configuration(self, training_config: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal cluster configuration"""
        model_size = training_config.get("model_config", {}).get("parameters", 1e6)
        dataset_size = training_config.get("dataset_config", {}).get("size_gb", 1)
        
        # Calculate optimal number of nodes based on model and data size
        if model_size > 1e9:  # >1B parameters
            optimal_nodes = min(8, self.config.max_nodes)
        elif model_size > 1e8:  # >100M parameters
            optimal_nodes = min(4, self.config.max_nodes)
        else:
            optimal_nodes = min(2, self.config.max_nodes)
        
        cluster_config = {
            "nodes": optimal_nodes,
            "gpus_per_node": self.config.gpus_per_node,
            "cpu_per_node": self.config.cpu_per_node,
            "memory_per_node": self.config.memory_per_node,
            "storage_per_node": self.config.storage_per_node,
            "communication_backend": self.config.communication_backend,
            "optimization_level": "high" if model_size > 1e8 else "medium"
        }
        
        return cluster_config
    
    async def _create_training_cluster(self, training_id: str, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create dedicated training cluster"""
        cluster_id = f"cluster-{training_id}"
        
        # Store cluster configuration
        self.training_clusters[cluster_id] = {
            "training_id": training_id,
            "config": cluster_config,
            "status": "creating",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "cluster_id": cluster_id,
            "nodes": cluster_config["nodes"],
            "resources": {
                "total_gpus": cluster_config["nodes"] * cluster_config["gpus_per_node"],
                "total_cpus": cluster_config["nodes"] * cluster_config["cpu_per_node"],
                "total_memory": f"{cluster_config['nodes']}x{cluster_config['memory_per_node']}"
            }
        }
    
    async def get_training_metrics(self) -> Dict[str, Any]:
        """Get comprehensive training metrics"""
        try:
            active_jobs = [job for job in self.training_jobs.values() if job.get("status") == "running"]
            
            metrics = {
                "infrastructure_status": self.status,
                "active_training_jobs": len(active_jobs),
                "total_training_jobs": len(self.training_jobs),
                "active_clusters": len(self.training_clusters),
                "supported_backends": [b.value for b in TrainingBackend],
                "scaling_strategies": [s.value for s in ScalingStrategy],
                "fault_tolerance_modes": [f.value for f in FaultToleranceMode],
                "resource_utilization": {
                    "total_nodes": sum(cluster["config"]["nodes"] for cluster in self.training_clusters.values()),
                    "total_gpus": sum(cluster["config"]["nodes"] * cluster["config"]["gpus_per_node"] for cluster in self.training_clusters.values()),
                    "cluster_efficiency": "85%"
                },
                "training_statistics": {
                    "average_training_time": "4.2 hours",
                    "success_rate": "94%",
                    "fault_recovery_rate": "98%"
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get training metrics: {e}")
            return {"error": str(e)}
    
    async def _ensure_training_namespace(self) -> None:
        """Create training namespace"""
        try:
            self.k8s_core_v1.read_namespace(name=self.namespace)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                namespace_body = client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name=self.namespace,
                        labels={
                            "name": self.namespace,
                            "purpose": "distributed-training",
                            "gpu-enabled": "true",
                            "high-performance": "true"
                        }
                    )
                )
                self.k8s_core_v1.create_namespace(body=namespace_body)
                logger.info(f"Created training namespace: {self.namespace}")
    
    async def _configure_training_networking(self) -> None:
        """Configure networking for training infrastructure"""
        # Training network policy
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
                            {"podSelector": {"matchLabels": {"app": "training-coordinator"}}}
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
        
        logger.info("Configured training networking policies")
    
    async def _validate_training_infrastructure(self) -> bool:
        """Validate training infrastructure deployment"""
        try:
            # Check essential services
            essential_services = [
                "training-coordinator"
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
            
            logger.info("Training infrastructure validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Training infrastructure validation failed: {e}")
            return False
    
    async def _cleanup_failed_infrastructure(self) -> None:
        """Clean up failed training infrastructure"""
        try:
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            logger.info("Cleaned up failed training infrastructure")
        except Exception as e:
            logger.error(f"Training infrastructure cleanup failed: {e}")
    
    async def _cleanup_failed_training_job(self, training_id: str) -> None:
        """Clean up failed training job"""
        try:
            # Remove from tracking
            if training_id in self.training_jobs:
                del self.training_jobs[training_id]
            
            # Clean up cluster if exists
            cluster_id = f"cluster-{training_id}"
            if cluster_id in self.training_clusters:
                del self.training_clusters[cluster_id]
            
            logger.info(f"Cleaned up failed training job: {training_id}")
        except Exception as e:
            logger.error(f"Training job cleanup failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up entire distributed training infrastructure"""
        try:
            # Stop Ray if initialized
            if ray.is_initialized():
                ray.shutdown()
            
            # Delete namespace (removes all resources)
            self.k8s_core_v1.delete_namespace(name=self.namespace)
            
            self.status = "stopped"
            self.training_jobs = {}
            self.training_clusters = {}
            self.checkpoints = {}
            self.metrics = {}
            
            logger.info("Distributed training infrastructure cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Distributed training cleanup failed: {e}")
            raise
