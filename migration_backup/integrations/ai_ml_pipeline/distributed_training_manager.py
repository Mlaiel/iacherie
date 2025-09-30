"""
Distributed Training Manager - AI/ML Pipeline Infrastructure
Enterprise distributed training coordination with multi-GPU optimization and scaling automation.

Created by: Fahed Mlaiel (mlaiel@live.de)
Copyright: EXCLUSIVE INTELLECTUAL PROPERTY - Fahed Mlaiel
WARNING: Unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import GPUtil
from kubernetes import client, config
import redis
import pickle
import boto3
import ray
import horovod.torch as hvd
from mpi4py import MPI


@dataclass
class DistributedTrainingConfig:
    """Configuration for distributed training job"""
    job_id: str
    model_config: Dict[str, Any]
    dataset_config: Dict[str, Any]
    training_config: Dict[str, Any]
    resource_requirements: Dict[str, Any]
    scaling_policy: Dict[str, Any]
    checkpoint_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class TrainingNode:
    """Distributed training node representation"""
    node_id: str
    rank: int
    world_size: int
    local_rank: int
    master_addr: str
    master_port: int
    gpu_devices: List[int]
    cpu_cores: int
    memory_gb: float
    status: str
    last_heartbeat: datetime


@dataclass
class TrainingJob:
    """Distributed training job state"""
    job_id: str
    config: DistributedTrainingConfig
    nodes: List[TrainingNode]
    status: str
    current_epoch: int
    total_epochs: int
    training_metrics: Dict[str, Any]
    resource_usage: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]


@dataclass
class ScalingDecision:
    """Auto-scaling decision for training job"""
    job_id: str
    action: str  # scale_up, scale_down, no_action
    target_nodes: int
    current_nodes: int
    reason: str
    confidence: float
    recommended_at: datetime


class DistributedTrainingOrchestrator:
    """Enterprise distributed training orchestration with multi-GPU optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        self.s3_client = boto3.client('s3') if config.get('s3_enabled') else None
        self.logger = self._setup_logging()
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.resource_monitor = ResourceMonitor(config)
        self.scaling_manager = AutoScalingManager(config)
        self.checkpoint_manager = CheckpointManager(config)
        self.communication_backend = config.get('communication_backend', 'nccl')
        
        # Initialize Ray for distributed coordination
        if not ray.is_initialized():
            ray.init(address=config.get('ray_address', 'auto'))
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for distributed training"""
        logger = logging.getLogger('distributed_training')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    async def create_training_job(
        self,
        model_config: Dict[str, Any],
        dataset_config: Dict[str, Any],
        training_config: Dict[str, Any],
        resource_requirements: Dict[str, Any]
    ) -> str:
        """Create new distributed training job"""
        job_id = str(uuid.uuid4())
        
        # Create job configuration
        job_config = DistributedTrainingConfig(
            job_id=job_id,
            model_config=model_config,
            dataset_config=dataset_config,
            training_config=training_config,
            resource_requirements=resource_requirements,
            scaling_policy=training_config.get('scaling_policy', {}),
            checkpoint_config=training_config.get('checkpoint_config', {}),
            monitoring_config=training_config.get('monitoring_config', {}),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Initialize training job
        training_job = TrainingJob(
            job_id=job_id,
            config=job_config,
            nodes=[],
            status='pending',
            current_epoch=0,
            total_epochs=training_config.get('epochs', 100),
            training_metrics={},
            resource_usage={},
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            error_message=None
        )
        
        self.training_jobs[job_id] = training_job
        
        # Store job in Redis for persistence
        await self._store_job_state(training_job)
        
        self.logger.info(f"Created distributed training job: {job_id}")
        return job_id
    
    async def start_training_job(self, job_id: str) -> bool:
        """Start distributed training job with resource allocation"""
        if job_id not in self.training_jobs:
            raise ValueError(f"Training job {job_id} not found")
        
        job = self.training_jobs[job_id]
        
        try:
            # Allocate training resources
            nodes = await self._allocate_training_resources(job)
            if not nodes:
                raise RuntimeError("Failed to allocate required training resources")
            
            job.nodes = nodes
            job.status = 'starting'
            job.started_at = datetime.utcnow()
            
            # Initialize distributed training cluster
            await self._initialize_training_cluster(job)
            
            # Start training processes on all nodes
            await self._start_training_processes(job)
            
            job.status = 'running'
            await self._store_job_state(job)
            
            # Start monitoring and auto-scaling
            asyncio.create_task(self._monitor_training_job(job_id))
            asyncio.create_task(self._auto_scale_training_job(job_id))
            
            self.logger.info(f"Started distributed training job: {job_id}")
            return True
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            await self._store_job_state(job)
            self.logger.error(f"Failed to start training job {job_id}: {e}")
            return False
    
    async def _allocate_training_resources(self, job: TrainingJob) -> List[TrainingNode]:
        """Allocate training resources based on job requirements"""
        requirements = job.config.resource_requirements
        required_gpus = requirements.get('min_gpus', 1)
        max_gpus = requirements.get('max_gpus', required_gpus)
        
        # Query available resources
        available_resources = await self.resource_monitor.get_available_resources()
        
        # Select optimal nodes for training
        selected_nodes = []
        total_gpus = 0
        
        for node_info in available_resources['nodes']:
            if total_gpus >= max_gpus:
                break
                
            available_gpus = node_info['available_gpus']
            if available_gpus > 0:
                node_gpus = min(available_gpus, max_gpus - total_gpus)
                
                training_node = TrainingNode(
                    node_id=node_info['node_id'],
                    rank=len(selected_nodes),
                    world_size=0,  # Will be set after all nodes selected
                    local_rank=0,
                    master_addr=node_info['ip_address'],
                    master_port=requirements.get('master_port', 29500),
                    gpu_devices=list(range(node_gpus)),
                    cpu_cores=node_info['available_cpus'],
                    memory_gb=node_info['available_memory_gb'],
                    status='allocated',
                    last_heartbeat=datetime.utcnow()
                )
                
                selected_nodes.append(training_node)
                total_gpus += node_gpus
        
        if total_gpus < required_gpus:
            raise RuntimeError(f"Insufficient GPU resources: required {required_gpus}, available {total_gpus}")
        
        # Set world size for all nodes
        for node in selected_nodes:
            node.world_size = len(selected_nodes)
        
        # Set master node
        if selected_nodes:
            selected_nodes[0].master_addr = selected_nodes[0].master_addr
            for i, node in enumerate(selected_nodes[1:], 1):
                node.master_addr = selected_nodes[0].master_addr
        
        return selected_nodes
    
    async def _initialize_training_cluster(self, job: TrainingJob) -> None:
        """Initialize distributed training cluster"""
        master_node = job.nodes[0]
        
        # Initialize process group on each node
        init_tasks = []
        for node in job.nodes:
            task = self._initialize_node_process_group(job, node, master_node)
            init_tasks.append(task)
        
        await asyncio.gather(*init_tasks)
        
        # Wait for all nodes to join
        await self._wait_for_cluster_ready(job)
    
    async def _initialize_node_process_group(
        self,
        job: TrainingJob,
        node: TrainingNode,
        master_node: TrainingNode
    ) -> None:
        """Initialize distributed process group on a node"""
        
        @ray.remote
        def init_process_group(rank, world_size, master_addr, master_port, backend):
            import torch.distributed as dist
            import os
            
            os.environ['MASTER_ADDR'] = master_addr
            os.environ['MASTER_PORT'] = str(master_port)
            os.environ['RANK'] = str(rank)
            os.environ['WORLD_SIZE'] = str(world_size)
            
            dist.init_process_group(
                backend=backend,
                rank=rank,
                world_size=world_size,
                timeout=timedelta(minutes=30)
            )
            
            return f"Node {rank} initialized successfully"
        
        result = await init_process_group.remote(
            node.rank,
            node.world_size,
            master_node.master_addr,
            master_node.master_port,
            self.communication_backend
        )
        
        self.logger.info(f"Initialized process group for node {node.node_id}: {result}")
    
    async def _start_training_processes(self, job: TrainingJob) -> None:
        """Start training processes on all nodes"""
        training_tasks = []
        
        for node in job.nodes:
            task = self._start_node_training(job, node)
            training_tasks.append(task)
        
        # Start all training processes
        await asyncio.gather(*training_tasks, return_exceptions=True)
    
    async def _start_node_training(self, job: TrainingJob, node: TrainingNode) -> None:
        """Start training process on a specific node"""
        
        @ray.remote(num_gpus=len(node.gpu_devices))
        def train_on_node(job_config, node_config):
            """Training function to run on each node"""
            import torch
            import torch.nn as nn
            from torch.nn.parallel import DistributedDataParallel as DDP
            from torch.utils.data import DataLoader, DistributedSampler
            
            # Set device
            local_rank = node_config['local_rank']
            torch.cuda.set_device(local_rank)
            device = torch.device(f'cuda:{local_rank}')
            
            # Create model
            model = create_model_from_config(job_config['model_config'])
            model = model.to(device)
            model = DDP(model, device_ids=[local_rank])
            
            # Create dataset and data loader
            dataset = create_dataset_from_config(job_config['dataset_config'])
            sampler = DistributedSampler(dataset, shuffle=True)
            dataloader = DataLoader(
                dataset,
                batch_size=job_config['training_config']['batch_size'],
                sampler=sampler,
                num_workers=4,
                pin_memory=True
            )
            
            # Create optimizer and scheduler
            optimizer = create_optimizer_from_config(
                model.parameters(),
                job_config['training_config']['optimizer']
            )
            scheduler = create_scheduler_from_config(
                optimizer,
                job_config['training_config'].get('scheduler', {})
            )
            
            # Training loop
            num_epochs = job_config['training_config']['epochs']
            for epoch in range(num_epochs):
                sampler.set_epoch(epoch)
                
                model.train()
                epoch_loss = 0.0
                num_batches = 0
                
                for batch_idx, (data, target) in enumerate(dataloader):
                    data, target = data.to(device), target.to(device)
                    
                    optimizer.zero_grad()
                    output = model(data)
                    loss = compute_loss(output, target)
                    loss.backward()
                    optimizer.step()
                    
                    epoch_loss += loss.item()
                    num_batches += 1
                    
                    # Log progress periodically
                    if batch_idx % 100 == 0:
                        print(f"Rank {node_config['rank']}: Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.6f}")
                
                # Synchronize metrics across all nodes
                avg_loss = epoch_loss / num_batches
                print(f"Rank {node_config['rank']}: Epoch {epoch} completed, Average Loss: {avg_loss:.6f}")
                
                # Save checkpoint periodically
                if epoch % 10 == 0 and node_config['rank'] == 0:
                    save_checkpoint(model, optimizer, epoch, avg_loss, job_config['job_id'])
                
                scheduler.step()
            
            return f"Training completed on rank {node_config['rank']}"
        
        # Prepare node configuration
        node_config = {
            'rank': node.rank,
            'world_size': node.world_size,
            'local_rank': node.local_rank,
            'gpu_devices': node.gpu_devices
        }
        
        # Start training on remote node
        result = await train_on_node.remote(asdict(job.config), node_config)
        self.logger.info(f"Training process started on node {node.node_id}")
    
    async def _monitor_training_job(self, job_id: str) -> None:
        """Monitor training job progress and health"""
        while True:
            try:
                job = self.training_jobs.get(job_id)
                if not job or job.status in ['completed', 'failed', 'cancelled']:
                    break
                
                # Collect metrics from all nodes
                metrics = await self._collect_training_metrics(job)
                
                # Update job metrics
                job.training_metrics.update(metrics)
                job.updated_at = datetime.utcnow()
                
                # Check for training completion
                if self._is_training_complete(job, metrics):
                    await self._complete_training_job(job_id)
                    break
                
                # Check for training failures
                if self._detect_training_failures(job, metrics):
                    await self._handle_training_failure(job_id, "Training failure detected")
                    break
                
                # Store updated job state
                await self._store_job_state(job)
                
                # Wait before next monitoring cycle
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error monitoring training job {job_id}: {e}")
                await asyncio.sleep(60)
    
    async def _auto_scale_training_job(self, job_id: str) -> None:
        """Auto-scale training job based on performance and resource utilization"""
        while True:
            try:
                job = self.training_jobs.get(job_id)
                if not job or job.status in ['completed', 'failed', 'cancelled']:
                    break
                
                # Analyze scaling requirements
                scaling_decision = await self.scaling_manager.analyze_scaling_requirements(job)
                
                if scaling_decision.action != 'no_action':
                    await self._execute_scaling_action(job_id, scaling_decision)
                
                # Wait before next scaling analysis
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error auto-scaling training job {job_id}: {e}")
                await asyncio.sleep(600)  # 10 minutes
    
    async def stop_training_job(self, job_id: str, reason: str = "User requested") -> bool:
        """Stop distributed training job"""
        if job_id not in self.training_jobs:
            return False
        
        job = self.training_jobs[job_id]
        
        try:
            # Stop training processes on all nodes
            stop_tasks = []
            for node in job.nodes:
                task = self._stop_node_training(job, node)
                stop_tasks.append(task)
            
            await asyncio.gather(*stop_tasks, return_exceptions=True)
            
            # Clean up distributed process group
            await self._cleanup_training_cluster(job)
            
            # Release allocated resources
            await self._release_training_resources(job)
            
            job.status = 'cancelled'
            job.completed_at = datetime.utcnow()
            job.error_message = reason
            
            await self._store_job_state(job)
            
            self.logger.info(f"Stopped distributed training job: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping training job {job_id}: {e}")
            return False
    
    async def get_training_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of training job"""
        job = self.training_jobs.get(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'status': job.status,
            'current_epoch': job.current_epoch,
            'total_epochs': job.total_epochs,
            'progress_percentage': (job.current_epoch / job.total_epochs) * 100,
            'nodes': [
                {
                    'node_id': node.node_id,
                    'rank': node.rank,
                    'status': node.status,
                    'gpu_devices': node.gpu_devices,
                    'last_heartbeat': node.last_heartbeat.isoformat()
                }
                for node in job.nodes
            ],
            'training_metrics': job.training_metrics,
            'resource_usage': job.resource_usage,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message
        }
    
    async def list_training_jobs(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all training jobs with optional status filtering"""
        jobs = []
        
        for job in self.training_jobs.values():
            if status_filter and job.status != status_filter:
                continue
            
            job_info = await self.get_training_job_status(job.job_id)
            if job_info:
                jobs.append(job_info)
        
        return jobs
    
    async def _store_job_state(self, job: TrainingJob) -> None:
        """Store training job state in Redis"""
        job_data = {
            'job_id': job.job_id,
            'status': job.status,
            'config': asdict(job.config),
            'nodes': [asdict(node) for node in job.nodes],
            'current_epoch': job.current_epoch,
            'total_epochs': job.total_epochs,
            'training_metrics': job.training_metrics,
            'resource_usage': job.resource_usage,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message
        }
        
        self.redis_client.setex(
            f"training_job:{job.job_id}",
            timedelta(days=30),
            pickle.dumps(job_data)
        )


class ResourceMonitor:
    """Monitor and track distributed training resources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('resource_monitor')
    
    async def get_available_resources(self) -> Dict[str, Any]:
        """Get currently available training resources"""
        # This would integrate with Kubernetes, SLURM, or other resource managers
        # For now, return mock data
        return {
            'nodes': [
                {
                    'node_id': 'gpu-node-1',
                    'ip_address': '10.0.1.10',
                    'available_gpus': 8,
                    'available_cpus': 32,
                    'available_memory_gb': 256,
                    'gpu_types': ['V100', 'V100'],
                    'status': 'available'
                },
                {
                    'node_id': 'gpu-node-2',
                    'ip_address': '10.0.1.11',
                    'available_gpus': 4,
                    'available_cpus': 16,
                    'available_memory_gb': 128,
                    'gpu_types': ['A100'],
                    'status': 'available'
                }
            ],
            'total_available_gpus': 12,
            'total_available_cpus': 48,
            'total_available_memory_gb': 384
        }


class AutoScalingManager:
    """Manage auto-scaling decisions for distributed training"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('autoscaling_manager')
    
    async def analyze_scaling_requirements(self, job: TrainingJob) -> ScalingDecision:
        """Analyze if training job needs scaling"""
        # Mock scaling decision logic
        return ScalingDecision(
            job_id=job.job_id,
            action='no_action',
            target_nodes=len(job.nodes),
            current_nodes=len(job.nodes),
            reason='Training progressing normally',
            confidence=0.8,
            recommended_at=datetime.utcnow()
        )


class CheckpointManager:
    """Manage distributed training checkpoints"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.s3_client = boto3.client('s3') if config.get('s3_enabled') else None
        self.logger = logging.getLogger('checkpoint_manager')
    
    async def save_checkpoint(
        self,
        job_id: str,
        epoch: int,
        model_state: Dict[str, Any],
        optimizer_state: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> str:
        """Save training checkpoint"""
        checkpoint_id = f"{job_id}_epoch_{epoch}_{int(datetime.utcnow().timestamp())}"
        
        checkpoint_data = {
            'job_id': job_id,
            'epoch': epoch,
            'model_state': model_state,
            'optimizer_state': optimizer_state,
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Save to S3 if configured
        if self.s3_client:
            checkpoint_key = f"checkpoints/{job_id}/{checkpoint_id}.pkl"
            self.s3_client.put_object(
                Bucket=self.config['checkpoint_bucket'],
                Key=checkpoint_key,
                Body=pickle.dumps(checkpoint_data)
            )
        
        self.logger.info(f"Saved checkpoint: {checkpoint_id}")
        return checkpoint_id


# Helper functions for model creation and training
def create_model_from_config(model_config: Dict[str, Any]):
    """Create model from configuration"""
    # Mock model creation - would be replaced with actual model factory
    import torch.nn as nn
    return nn.Sequential(
        nn.Linear(784, 128),
        nn.ReLU(),
        nn.Linear(128, 10)
    )


def create_dataset_from_config(dataset_config: Dict[str, Any]):
    """Create dataset from configuration"""
    # Mock dataset creation - would be replaced with actual dataset factory
    from torch.utils.data import TensorDataset
    import torch
    
    data = torch.randn(1000, 784)
    targets = torch.randint(0, 10, (1000,))
    return TensorDataset(data, targets)


def create_optimizer_from_config(parameters, optimizer_config: Dict[str, Any]):
    """Create optimizer from configuration"""
    import torch.optim as optim
    
    optimizer_type = optimizer_config.get('type', 'adam')
    learning_rate = optimizer_config.get('learning_rate', 0.001)
    
    if optimizer_type.lower() == 'adam':
        return optim.Adam(parameters, lr=learning_rate)
    elif optimizer_type.lower() == 'sgd':
        return optim.SGD(parameters, lr=learning_rate, momentum=0.9)
    else:
        return optim.Adam(parameters, lr=learning_rate)


def create_scheduler_from_config(optimizer, scheduler_config: Dict[str, Any]):
    """Create learning rate scheduler from configuration"""
    import torch.optim.lr_scheduler as lr_scheduler
    
    scheduler_type = scheduler_config.get('type', 'step')
    
    if scheduler_type.lower() == 'step':
        step_size = scheduler_config.get('step_size', 30)
        gamma = scheduler_config.get('gamma', 0.1)
        return lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
    elif scheduler_type.lower() == 'cosine':
        T_max = scheduler_config.get('T_max', 100)
        return lr_scheduler.CosineAnnealingLR(optimizer, T_max=T_max)
    else:
        return lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)


def compute_loss(output, target):
    """Compute training loss"""
    import torch.nn.functional as F
    return F.cross_entropy(output, target)


def save_checkpoint(model, optimizer, epoch, loss, job_id):
    """Save training checkpoint"""
    import torch
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
        'job_id': job_id
    }
    torch.save(checkpoint, f'/tmp/checkpoint_{job_id}_epoch_{epoch}.pth')


# Factory function for creating distributed training manager
def create_distributed_training_manager(config: Dict[str, Any]) -> DistributedTrainingOrchestrator:
    """Create distributed training manager instance"""
    return DistributedTrainingOrchestrator(config)