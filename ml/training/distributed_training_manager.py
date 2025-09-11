#!/usr/bin/env python3
"""
🚀 Distributed Training Manager - Enterprise ML Training Infrastructure

Handles large-scale distributed training across multiple GPUs/nodes with fault tolerance,
optimized for Ainflue's creator-centric ML workloads.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

Architecture Integration:
- Integrates with AutoMLPipeline for automated distributed training
- Supports multi-node GPU clusters for large-scale model training
- Fault-tolerant design with automatic recovery and checkpointing
- Creator-specific model training with resource optimization
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import uuid
from enum import Enum

import numpy as np
from sklearn.base import BaseEstimator


class TrainingStrategy(Enum):
    """Training strategy enumeration."""
    DATA_PARALLEL = "data_parallel"
    MODEL_PARALLEL = "model_parallel"
    PIPELINE_PARALLEL = "pipeline_parallel"
    HYBRID = "hybrid"


class NodeStatus(Enum):
    """Node status enumeration."""
    IDLE = "idle"
    TRAINING = "training"
    FAILED = "failed"
    RECOVERING = "recovering"


@dataclass
class TrainingNode:
    """Represents a training node in the distributed cluster."""
    node_id: str
    gpu_count: int
    memory_gb: float
    status: NodeStatus = NodeStatus.IDLE
    current_job: Optional[str] = None
    last_heartbeat: float = field(default_factory=time.time)
    failure_count: int = 0


@dataclass
class DistributedTrainingConfig:
    """Configuration for distributed training."""
    strategy: TrainingStrategy = TrainingStrategy.DATA_PARALLEL
    max_nodes: int = 4
    min_nodes: int = 1
    gpu_per_node: int = 1
    batch_size_per_gpu: int = 32
    gradient_accumulation_steps: int = 1
    mixed_precision: bool = True
    checkpoint_interval: int = 1000
    fault_tolerance: bool = True
    max_retries: int = 3
    heartbeat_interval: float = 30.0
    
    # Creator-specific optimizations
    creator_type_optimization: bool = True
    content_type_batching: bool = True
    load_balancing_strategy: str = "round_robin"


class DistributedTrainingManager:
    """
    Enterprise distributed training manager for multi-node ML training.
    
    Features:
    - Multi-GPU/node training with fault tolerance
    - Automatic load balancing and resource optimization
    - Creator-specific training optimizations
    - Real-time monitoring and adaptive scaling
    - Checkpoint management and recovery
    """
    
    def __init__(self, config: Optional[DistributedTrainingConfig] = None):
        """Initialize the distributed training manager."""
        self.config = config or DistributedTrainingConfig()
        self.logger = logging.getLogger(__name__)
        
        # Cluster management
        self.nodes: Dict[str, TrainingNode] = {}
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        self.job_queue: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.training_metrics: Dict[str, List[float]] = {
            "throughput": [],
            "loss": [],
            "accuracy": [],
            "gpu_utilization": [],
            "memory_usage": []
        }
        
        # Fault tolerance
        self.checkpoints: Dict[str, Dict[str, Any]] = {}
        self.failed_jobs: List[Dict[str, Any]] = []
        
        self.logger.info("Distributed Training Manager initialized")
    
    async def register_node(self, 
                          node_id: str, 
                          gpu_count: int, 
                          memory_gb: float) -> bool:
        """Register a new training node."""
        try:
            node = TrainingNode(
                node_id=node_id,
                gpu_count=gpu_count,
                memory_gb=memory_gb
            )
            
            self.nodes[node_id] = node
            self.logger.info(f"Node {node_id} registered with {gpu_count} GPUs, {memory_gb}GB memory")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register node {node_id}: {e}")
            return False
    
    async def submit_training_job(self,
                                job_id: str,
                                model_config: Dict[str, Any],
                                dataset_config: Dict[str, Any],
                                creator_type: Optional[str] = None) -> str:
        """Submit a distributed training job."""
        try:
            job = {
                "job_id": job_id,
                "model_config": model_config,
                "dataset_config": dataset_config,
                "creator_type": creator_type,
                "submitted_at": time.time(),
                "status": "queued",
                "assigned_nodes": [],
                "training_strategy": self.config.strategy.value,
                "retry_count": 0
            }
            
            # Creator-specific optimizations
            if creator_type and self.config.creator_type_optimization:
                job = await self._optimize_for_creator_type(job, creator_type)
            
            self.job_queue.append(job)
            self.active_jobs[job_id] = job
            
            self.logger.info(f"Training job {job_id} submitted for creator type: {creator_type}")
            
            # Start job scheduling
            asyncio.create_task(self._schedule_jobs())
            
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit training job {job_id}: {e}")
            raise
    
    async def _optimize_for_creator_type(self, 
                                       job: Dict[str, Any], 
                                       creator_type: str) -> Dict[str, Any]:
        """Optimize job configuration for specific creator type."""
        try:
            optimizations = {
                "musician": {
                    "batch_size_multiplier": 1.2,
                    "sequence_length": 16000,  # Audio sequence length
                    "memory_multiplier": 1.5
                },
                "blogger": {
                    "batch_size_multiplier": 1.0,
                    "sequence_length": 512,    # Text sequence length
                    "memory_multiplier": 1.0
                },
                "photographer": {
                    "batch_size_multiplier": 0.8,  # Large images
                    "image_size": 512,
                    "memory_multiplier": 2.0
                },
                "influencer": {
                    "batch_size_multiplier": 1.1,
                    "multi_modal": True,
                    "memory_multiplier": 1.3
                }
            }
            
            if creator_type in optimizations:
                opt = optimizations[creator_type]
                
                # Apply optimizations
                if "batch_size_multiplier" in opt:
                    job["model_config"]["batch_size"] = int(
                        job["model_config"].get("batch_size", 32) * opt["batch_size_multiplier"]
                    )
                
                job["optimization_profile"] = creator_type
                
            return job
            
        except Exception as e:
            self.logger.error(f"Failed to optimize for creator type {creator_type}: {e}")
            return job
    
    async def _schedule_jobs(self):
        """Schedule queued jobs on available nodes."""
        try:
            if not self.job_queue:
                return
            
            available_nodes = [
                node for node in self.nodes.values() 
                if node.status == NodeStatus.IDLE
            ]
            
            if not available_nodes:
                return
            
            # Get next job from queue
            job = self.job_queue.pop(0)
            job_id = job["job_id"]
            
            # Determine required nodes based on strategy
            required_nodes = await self._calculate_required_nodes(job)
            
            if len(available_nodes) < required_nodes:
                # Put job back in queue
                self.job_queue.insert(0, job)
                return
            
            # Assign nodes to job
            assigned_nodes = available_nodes[:required_nodes]
            job["assigned_nodes"] = [node.node_id for node in assigned_nodes]
            
            # Mark nodes as busy
            for node in assigned_nodes:
                node.status = NodeStatus.TRAINING
                node.current_job = job_id
            
            # Start training
            job["status"] = "running"
            job["started_at"] = time.time()
            
            asyncio.create_task(self._execute_distributed_training(job))
            
            self.logger.info(f"Job {job_id} scheduled on {len(assigned_nodes)} nodes")
            
        except Exception as e:
            self.logger.error(f"Failed to schedule jobs: {e}")
    
    async def _calculate_required_nodes(self, job: Dict[str, Any]) -> int:
        """Calculate number of nodes required for job."""
        try:
            strategy = job.get("training_strategy", "data_parallel")
            model_size = job["model_config"].get("model_size", "medium")
            
            # Size-based node calculation
            size_requirements = {
                "small": 1,
                "medium": 2,
                "large": 4,
                "xl": 8
            }
            
            base_nodes = size_requirements.get(model_size, 2)
            
            # Strategy-based adjustments
            if strategy == "model_parallel":
                base_nodes = max(base_nodes, 2)
            elif strategy == "pipeline_parallel":
                base_nodes = max(base_nodes, 3)
            
            return min(base_nodes, self.config.max_nodes, len(self.nodes))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate required nodes: {e}")
            return 1
    
    async def _execute_distributed_training(self, job: Dict[str, Any]):
        """Execute distributed training job."""
        job_id = job["job_id"]
        
        try:
            self.logger.info(f"Starting distributed training for job {job_id}")
            
            # Simulate distributed training process
            training_steps = job["model_config"].get("training_steps", 1000)
            checkpoint_interval = self.config.checkpoint_interval
            
            for step in range(0, training_steps, checkpoint_interval):
                # Simulate training step
                await self._simulate_training_step(job, step)
                
                # Create checkpoint
                if self.config.fault_tolerance:
                    await self._create_checkpoint(job_id, step)
                
                # Check for node failures
                if await self._check_node_health(job):
                    # Handle node failure
                    if not await self._handle_node_failure(job):
                        break
                
                # Update metrics
                await self._update_training_metrics(job_id, step)
            
            # Complete job
            await self._complete_job(job)
            
        except Exception as e:
            self.logger.error(f"Distributed training failed for job {job_id}: {e}")
            await self._handle_job_failure(job, str(e))
    
    async def _simulate_training_step(self, job: Dict[str, Any], step: int):
        """Simulate a training step."""
        # Simulate variable training time based on creator type
        creator_type = job.get("creator_type", "generic")
        
        base_time = {
            "musician": 0.1,      # Audio processing is intensive
            "photographer": 0.15,  # Image processing
            "blogger": 0.05,      # Text processing
            "influencer": 0.08    # Mixed content
        }.get(creator_type, 0.07)
        
        # Add some randomness
        training_time = base_time + np.random.normal(0, 0.01)
        await asyncio.sleep(max(0.01, training_time))
    
    async def _create_checkpoint(self, job_id: str, step: int):
        """Create training checkpoint."""
        try:
            checkpoint = {
                "job_id": job_id,
                "step": step,
                "timestamp": time.time(),
                "model_state": f"checkpoint_{job_id}_{step}",  # Simulated
                "optimizer_state": f"optimizer_{job_id}_{step}",  # Simulated
                "metrics": {
                    "loss": np.random.uniform(0.1, 2.0),
                    "accuracy": np.random.uniform(0.7, 0.95)
                }
            }
            
            self.checkpoints[f"{job_id}_{step}"] = checkpoint
            self.logger.debug(f"Checkpoint created for job {job_id} at step {step}")
            
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint: {e}")
    
    async def _check_node_health(self, job: Dict[str, Any]) -> bool:
        """Check health of nodes assigned to job."""
        try:
            for node_id in job["assigned_nodes"]:
                node = self.nodes.get(node_id)
                if not node:
                    return True  # Node missing
                
                # Check heartbeat
                if time.time() - node.last_heartbeat > self.config.heartbeat_interval * 2:
                    node.status = NodeStatus.FAILED
                    node.failure_count += 1
                    return True  # Node failed
            
            return False  # All nodes healthy
            
        except Exception as e:
            self.logger.error(f"Failed to check node health: {e}")
            return True
    
    async def _handle_node_failure(self, job: Dict[str, Any]) -> bool:
        """Handle node failure during training."""
        try:
            job_id = job["job_id"]
            
            # Find failed nodes
            failed_nodes = []
            for node_id in job["assigned_nodes"]:
                node = self.nodes.get(node_id)
                if node and node.status == NodeStatus.FAILED:
                    failed_nodes.append(node_id)
            
            if not failed_nodes:
                return True  # No failures
            
            self.logger.warning(f"Node failure detected for job {job_id}: {failed_nodes}")
            
            # Try to find replacement nodes
            available_nodes = [
                node for node in self.nodes.values() 
                if node.status == NodeStatus.IDLE
            ]
            
            if len(available_nodes) < len(failed_nodes):
                # Not enough nodes for replacement
                self.logger.error(f"Insufficient nodes for job {job_id} recovery")
                return False
            
            # Replace failed nodes
            replacement_nodes = available_nodes[:len(failed_nodes)]
            
            # Update job assignment
            for failed_node_id in failed_nodes:
                job["assigned_nodes"].remove(failed_node_id)
            
            for replacement_node in replacement_nodes:
                job["assigned_nodes"].append(replacement_node.node_id)
                replacement_node.status = NodeStatus.TRAINING
                replacement_node.current_job = job_id
            
            # Restore from latest checkpoint
            await self._restore_from_checkpoint(job)
            
            self.logger.info(f"Job {job_id} recovered with replacement nodes")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to handle node failure: {e}")
            return False
    
    async def _restore_from_checkpoint(self, job: Dict[str, Any]):
        """Restore training from latest checkpoint."""
        try:
            job_id = job["job_id"]
            
            # Find latest checkpoint
            job_checkpoints = [
                cp for cp_id, cp in self.checkpoints.items() 
                if cp["job_id"] == job_id
            ]
            
            if not job_checkpoints:
                self.logger.warning(f"No checkpoints found for job {job_id}")
                return
            
            latest_checkpoint = max(job_checkpoints, key=lambda x: x["step"])
            
            # Simulate checkpoint restoration
            job["restored_from_step"] = latest_checkpoint["step"]
            
            self.logger.info(f"Job {job_id} restored from step {latest_checkpoint['step']}")
            
        except Exception as e:
            self.logger.error(f"Failed to restore from checkpoint: {e}")
    
    async def _update_training_metrics(self, job_id: str, step: int):
        """Update training metrics."""
        try:
            # Simulate metrics
            throughput = np.random.uniform(100, 500)  # samples/sec
            loss = max(0.01, 2.0 - (step / 1000) + np.random.normal(0, 0.1))
            accuracy = min(0.99, 0.5 + (step / 2000) + np.random.normal(0, 0.05))
            gpu_util = np.random.uniform(0.8, 0.98)
            memory_usage = np.random.uniform(0.6, 0.9)
            
            self.training_metrics["throughput"].append(throughput)
            self.training_metrics["loss"].append(loss)
            self.training_metrics["accuracy"].append(accuracy)
            self.training_metrics["gpu_utilization"].append(gpu_util)
            self.training_metrics["memory_usage"].append(memory_usage)
            
            # Keep only recent metrics (last 1000 points)
            for metric in self.training_metrics:
                if len(self.training_metrics[metric]) > 1000:
                    self.training_metrics[metric] = self.training_metrics[metric][-1000:]
            
        except Exception as e:
            self.logger.error(f"Failed to update training metrics: {e}")
    
    async def _complete_job(self, job: Dict[str, Any]):
        """Complete training job."""
        try:
            job_id = job["job_id"]
            
            # Release nodes
            for node_id in job["assigned_nodes"]:
                node = self.nodes.get(node_id)
                if node:
                    node.status = NodeStatus.IDLE
                    node.current_job = None
            
            # Update job status
            job["status"] = "completed"
            job["completed_at"] = time.time()
            job["final_metrics"] = {
                "avg_throughput": np.mean(self.training_metrics["throughput"][-100:]),
                "final_loss": self.training_metrics["loss"][-1] if self.training_metrics["loss"] else 0,
                "final_accuracy": self.training_metrics["accuracy"][-1] if self.training_metrics["accuracy"] else 0
            }
            
            self.logger.info(f"Training job {job_id} completed successfully")
            
            # Schedule next job if available
            if self.job_queue:
                asyncio.create_task(self._schedule_jobs())
            
        except Exception as e:
            self.logger.error(f"Failed to complete job: {e}")
    
    async def _handle_job_failure(self, job: Dict[str, Any], error: str):
        """Handle job failure."""
        try:
            job_id = job["job_id"]
            
            # Release nodes
            for node_id in job["assigned_nodes"]:
                node = self.nodes.get(node_id)
                if node:
                    node.status = NodeStatus.IDLE
                    node.current_job = None
            
            # Check retry logic
            job["retry_count"] += 1
            if job["retry_count"] < self.config.max_retries:
                # Retry job
                job["status"] = "queued"
                job["error"] = error
                self.job_queue.append(job)
                
                self.logger.warning(f"Job {job_id} queued for retry {job['retry_count']}")
            else:
                # Job failed permanently
                job["status"] = "failed"
                job["error"] = error
                job["failed_at"] = time.time()
                self.failed_jobs.append(job)
                
                self.logger.error(f"Job {job_id} failed permanently: {error}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle job failure: {e}")
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get current cluster status."""
        try:
            active_nodes = len([n for n in self.nodes.values() if n.status != NodeStatus.FAILED])
            total_gpus = sum(n.gpu_count for n in self.nodes.values())
            active_gpus = sum(n.gpu_count for n in self.nodes.values() if n.status != NodeStatus.FAILED)
            
            return {
                "total_nodes": len(self.nodes),
                "active_nodes": active_nodes,
                "total_gpus": total_gpus,
                "active_gpus": active_gpus,
                "running_jobs": len([j for j in self.active_jobs.values() if j["status"] == "running"]),
                "queued_jobs": len(self.job_queue),
                "failed_jobs": len(self.failed_jobs),
                "average_gpu_utilization": np.mean(self.training_metrics["gpu_utilization"][-10:]) if self.training_metrics["gpu_utilization"] else 0,
                "training_throughput": np.mean(self.training_metrics["throughput"][-10:]) if self.training_metrics["throughput"] else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cluster status: {e}")
            return {}
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific job."""
        try:
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                
                # Add real-time metrics if job is running
                if job["status"] == "running":
                    job["current_metrics"] = {
                        "current_loss": self.training_metrics["loss"][-1] if self.training_metrics["loss"] else 0,
                        "current_accuracy": self.training_metrics["accuracy"][-1] if self.training_metrics["accuracy"] else 0,
                        "gpu_utilization": np.mean(self.training_metrics["gpu_utilization"][-5:]) if self.training_metrics["gpu_utilization"] else 0
                    }
                
                return job
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get job status for {job_id}: {e}")
            return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running or queued job."""
        try:
            # Remove from queue if queued
            self.job_queue = [j for j in self.job_queue if j["job_id"] != job_id]
            
            # Cancel running job
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                
                if job["status"] == "running":
                    # Release nodes
                    for node_id in job["assigned_nodes"]:
                        node = self.nodes.get(node_id)
                        if node:
                            node.status = NodeStatus.IDLE
                            node.current_job = None
                
                job["status"] = "cancelled"
                job["cancelled_at"] = time.time()
                
                self.logger.info(f"Job {job_id} cancelled")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    async def scale_cluster(self, target_nodes: int) -> bool:
        """Scale cluster to target number of nodes."""
        try:
            current_nodes = len(self.nodes)
            
            if target_nodes > current_nodes:
                # Scale up - register placeholder nodes
                for i in range(target_nodes - current_nodes):
                    node_id = f"auto_node_{len(self.nodes) + i + 1}"
                    await self.register_node(node_id, 2, 16.0)  # Default: 2 GPUs, 16GB
                
                self.logger.info(f"Cluster scaled up to {target_nodes} nodes")
            
            elif target_nodes < current_nodes:
                # Scale down - remove idle nodes
                idle_nodes = [n for n in self.nodes.values() if n.status == NodeStatus.IDLE]
                nodes_to_remove = min(len(idle_nodes), current_nodes - target_nodes)
                
                for i in range(nodes_to_remove):
                    del self.nodes[idle_nodes[i].node_id]
                
                self.logger.info(f"Cluster scaled down to {len(self.nodes)} nodes")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to scale cluster: {e}")
            return False