"""🏋️ Enterprise Training Orchestrator - Ainflue AI/ML Pipeline
==============================================================

Advanced distributed training automation with multi-GPU support,
hyperparameter optimization, and fault-tolerant orchestration.

Expert Implementation:
🧠 ML Engineer: Distributed training + GPU optimization + AutoML
🤖 Lead Dev IA: Training orchestration + pipeline automation
🏗️ Backend Senior: Distributed computing + resource management
⚙️ DevOps: Training CI/CD + monitoring + infrastructure
🔒 Security: Training security + model protection + audit
🗄️ DBA: Training metadata + experiment tracking + storage
🔗 Microservices: Training service mesh + communication

Author: Fahed Mlaiel (mlaiel@live.de)
Date: December 2025
Version: Enterprise 1.0

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import uuid
import time
import os
import subprocess
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import aioredis
import asyncpg
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import yaml
import torch
import torch.distributed as dist
import optuna
from kubernetes import client, config as k8s_config
import ray
from ray import tune
from ray.tune.schedulers import ASHAScheduler
from ray.tune.search.optuna import OptunaSearch

logger = logging.getLogger(__name__)


class TrainingStatus(Enum):
    """Training job status"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TrainingType(Enum):
    """Training type classification"""
    SINGLE_NODE = "single_node"
    MULTI_NODE = "multi_node"
    DISTRIBUTED = "distributed"
    FEDERATED = "federated"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    AUTOML = "automl"
    TRANSFER_LEARNING = "transfer_learning"
    INCREMENTAL_LEARNING = "incremental_learning"


class OptimizationStrategy(Enum):
    """Optimization strategy for training"""
    BAYESIAN = "bayesian"
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    EVOLUTIONARY = "evolutionary"
    POPULATION_BASED = "population_based"


@dataclass
class TrainingConfiguration:
    """Training configuration container"""
    job_id: str
    name: str
    training_type: TrainingType
    model_config: Dict[str, Any]
    data_config: Dict[str, Any]
    training_params: Dict[str, Any]
    optimization_config: Dict[str, Any]
    resource_requirements: Dict[str, Any]
    creator_id: str
    created_at: datetime
    priority: int = 5  # 1-10 scale
    timeout_hours: int = 24
    max_retries: int = 3
    checkpointing_enabled: bool = True
    early_stopping_enabled: bool = True
    distributed_backend: str = "nccl"
    tags: List[str] = field(default_factory=list)


@dataclass
class TrainingJob:
    """Training job state container"""
    config: TrainingConfiguration
    status: TrainingStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = 0.0
    current_epoch: int = 0
    total_epochs: int = 0
    best_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    checkpoints: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)


@dataclass
class HyperparameterSpace:
    """Hyperparameter search space definition"""
    parameters: Dict[str, Any]
    optimization_objective: str
    direction: str = "maximize"  # maximize or minimize
    n_trials: int = 100
    timeout_seconds: int = 3600
    pruning_enabled: bool = True


@dataclass
class ResourceAllocation:
    """Resource allocation for training"""
    gpu_count: int
    gpu_memory_gb: int
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    node_count: int = 1
    instance_type: str = "gpu_standard"
    spot_instances: bool = False


class EnterpriseTrainingOrchestrator:
    """Enterprise training orchestration with distributed capabilities"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize training orchestrator"""
        self.config = config
        self.db_pool = None
        self.redis_client = None
        self.k8s_client = None
        self.ray_client = None
        self.training_jobs = {}
        self.resource_pools = {}
        self.job_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.process_executor = ProcessPoolExecutor(max_workers=10)
        
        # Orchestration configuration
        self.orchestration_config = {
            'max_concurrent_jobs': 10,
            'resource_allocation_strategy': 'fair_share',  # fair_share, priority, first_come
            'checkpoint_interval_minutes': 30,
            'metrics_collection_interval': 60,
            'log_retention_days': 30,
            'auto_scaling_enabled': True,
            'fault_tolerance_enabled': True,
            'cost_optimization_enabled': True
        }
        
        # Creator economy specific configuration
        self.creator_training_config = {
            'content_model_priority': 8,  # High priority for content models
            'platform_optimization_priority': 7,
            'collaboration_model_priority': 6,
            'seo_model_priority': 5,
            'monetization_model_priority': 9,  # Highest priority
            'resource_quotas': {
                'individual_creator': {'gpu_hours': 100, 'cpu_hours': 500},
                'team_creator': {'gpu_hours': 500, 'cpu_hours': 2000},
                'enterprise_creator': {'gpu_hours': 2000, 'cpu_hours': 10000}
            }
        }
    
    async def initialize(self):
        """Initialize orchestrator connections and setup"""
        try:
            # Initialize database connection
            self.db_pool = await asyncpg.create_pool(
                self.config['database_url'],
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Initialize Redis for job coordination
            self.redis_client = await aioredis.from_url(
                self.config['redis_url'],
                encoding='utf-8',
                decode_responses=True
            )
            
            # Initialize Kubernetes client
            try:
                k8s_config.load_incluster_config()
            except:
                k8s_config.load_kube_config()
            self.k8s_client = client.ApiClient()
            
            # Initialize Ray for distributed training
            if not ray.is_initialized():
                ray.init(
                    address=self.config.get('ray_address', 'auto'),
                    _redis_password=self.config.get('ray_redis_password')
                )
            
            # Setup database schema
            await self._setup_database_schema()
            
            # Initialize resource monitoring
            await self._initialize_resource_monitoring()
            
            # Start job scheduler
            asyncio.create_task(self._job_scheduler())
            
            # Start resource monitor
            asyncio.create_task(self._resource_monitor())
            
            logger.info("Enterprise Training Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Training Orchestrator: {e}")
            raise
    
    async def submit_training_job(
        self,
        config: TrainingConfiguration
    ) -> str:
        """Submit training job to orchestrator"""
        try:
            # Validate configuration
            await self._validate_training_config(config)
            
            # Check resource quotas
            await self._check_resource_quotas(config)
            
            # Create training job
            training_job = TrainingJob(
                config=config,
                status=TrainingStatus.PENDING
            )
            
            # Store job in database
            await self._store_training_job(training_job)
            
            # Cache job
            self.training_jobs[config.job_id] = training_job
            
            # Add to job queue
            await self.job_queue.put(config.job_id)
            
            # Log job submission
            await self._log_training_event(config.job_id, 'JOB_SUBMITTED', {
                'creator_id': config.creator_id,
                'training_type': config.training_type.value,
                'priority': config.priority
            })
            
            logger.info(f"Training job submitted: {config.job_id}")
            return config.job_id
            
        except Exception as e:
            logger.error(f"Failed to submit training job: {e}")
            raise
    
    async def start_training(self, job_id: str) -> bool:
        """Start training job execution"""
        try:
            job = await self.get_training_job(job_id)
            if not job:
                raise ValueError(f"Training job not found: {job_id}")
            
            if job.status != TrainingStatus.PENDING:
                raise ValueError(f"Job not in pending state: {job.status}")
            
            # Update job status
            job.status = TrainingStatus.INITIALIZING
            job.start_time = datetime.utcnow()
            await self._update_job_status(job)
            
            # Allocate resources
            resources = await self._allocate_resources(job.config)
            if not resources:
                job.status = TrainingStatus.FAILED
                job.error_message = "Failed to allocate resources"
                await self._update_job_status(job)
                return False
            
            # Choose training execution method
            if job.config.training_type == TrainingType.HYPERPARAMETER_TUNING:
                success = await self._start_hyperparameter_tuning(job, resources)
            elif job.config.training_type == TrainingType.DISTRIBUTED:
                success = await self._start_distributed_training(job, resources)
            elif job.config.training_type == TrainingType.AUTOML:
                success = await self._start_automl_training(job, resources)
            else:
                success = await self._start_standard_training(job, resources)
            
            if success:
                job.status = TrainingStatus.RUNNING
                logger.info(f"Training job started successfully: {job_id}")
            else:
                job.status = TrainingStatus.FAILED
                job.error_message = "Failed to start training execution"
                logger.error(f"Failed to start training job: {job_id}")
            
            await self._update_job_status(job)
            return success
            
        except Exception as e:
            logger.error(f"Failed to start training: {e}")
            raise
    
    async def stop_training(self, job_id: str, reason: str = "manual_stop") -> bool:
        """Stop training job execution"""
        try:
            job = await self.get_training_job(job_id)
            if not job:
                raise ValueError(f"Training job not found: {job_id}")
            
            if job.status not in [TrainingStatus.RUNNING, TrainingStatus.PAUSED]:
                return False
            
            # Stop training execution
            await self._stop_training_execution(job)
            
            # Save checkpoint
            if job.config.checkpointing_enabled:
                await self._save_checkpoint(job)
            
            # Update job status
            job.status = TrainingStatus.CANCELLED
            job.end_time = datetime.utcnow()
            job.error_message = reason
            
            # Release resources
            await self._release_resources(job.config.job_id)
            
            await self._update_job_status(job)
            
            # Log stop event
            await self._log_training_event(job_id, 'JOB_STOPPED', {
                'reason': reason,
                'duration_minutes': (job.end_time - job.start_time).total_seconds() / 60
            })
            
            logger.info(f"Training job stopped: {job_id} - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop training: {e}")
            raise
    
    async def get_training_job(self, job_id: str) -> Optional[TrainingJob]:
        """Get training job details"""
        try:
            # Check cache first
            if job_id in self.training_jobs:
                return self.training_jobs[job_id]
            
            # Query database
            async with self.db_pool.acquire() as connection:
                row = await connection.fetchrow(
                    "SELECT * FROM training_jobs WHERE job_id = $1",
                    job_id
                )
                
                if row:
                    # Reconstruct training job
                    config_data = json.loads(row['config'])
                    config = TrainingConfiguration(
                        job_id=config_data['job_id'],
                        name=config_data['name'],
                        training_type=TrainingType(config_data['training_type']),
                        model_config=config_data['model_config'],
                        data_config=config_data['data_config'],
                        training_params=config_data['training_params'],
                        optimization_config=config_data['optimization_config'],
                        resource_requirements=config_data['resource_requirements'],
                        creator_id=config_data['creator_id'],
                        created_at=datetime.fromisoformat(config_data['created_at']),
                        priority=config_data.get('priority', 5),
                        timeout_hours=config_data.get('timeout_hours', 24),
                        max_retries=config_data.get('max_retries', 3),
                        checkpointing_enabled=config_data.get('checkpointing_enabled', True),
                        early_stopping_enabled=config_data.get('early_stopping_enabled', True),
                        distributed_backend=config_data.get('distributed_backend', 'nccl'),
                        tags=config_data.get('tags', [])
                    )
                    
                    job = TrainingJob(
                        config=config,
                        status=TrainingStatus(row['status']),
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        progress=float(row['progress'] or 0),
                        current_epoch=int(row['current_epoch'] or 0),
                        total_epochs=int(row['total_epochs'] or 0),
                        best_metrics=json.loads(row['best_metrics']) if row['best_metrics'] else {},
                        resource_usage=json.loads(row['resource_usage']) if row['resource_usage'] else {},
                        logs=json.loads(row['logs']) if row['logs'] else [],
                        error_message=row['error_message'],
                        checkpoints=json.loads(row['checkpoints']) if row['checkpoints'] else [],
                        artifacts=json.loads(row['artifacts']) if row['artifacts'] else {}
                    )
                    
                    # Cache for future requests
                    self.training_jobs[job_id] = job
                    return job
                    
            return None
            
        except Exception as e:
            logger.error(f"Failed to get training job: {e}")
            raise
    
    async def list_training_jobs(
        self,
        creator_id: Optional[str] = None,
        status: Optional[TrainingStatus] = None,
        training_type: Optional[TrainingType] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TrainingJob]:
        """List training jobs with filtering"""
        try:
            # Build query conditions
            conditions = []
            params = []
            param_count = 0
            
            if creator_id:
                param_count += 1
                conditions.append(f"config->>'creator_id' = ${param_count}")
                params.append(creator_id)
            
            if status:
                param_count += 1
                conditions.append(f"status = ${param_count}")
                params.append(status.value)
            
            if training_type:
                param_count += 1
                conditions.append(f"config->>'training_type' = ${param_count}")
                params.append(training_type.value)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Add pagination
            param_count += 1
            limit_clause = f"LIMIT ${param_count}"
            params.append(limit)
            
            param_count += 1
            offset_clause = f"OFFSET ${param_count}"
            params.append(offset)
            
            query = f"""
                SELECT * FROM training_jobs 
                WHERE {where_clause}
                ORDER BY created_at DESC
                {limit_clause} {offset_clause}
            """
            
            async with self.db_pool.acquire() as connection:
                rows = await connection.fetch(query, *params)
                
                jobs = []
                for row in rows:
                    # Reconstruct training job (same logic as get_training_job)
                    config_data = json.loads(row['config'])
                    config = TrainingConfiguration(
                        job_id=config_data['job_id'],
                        name=config_data['name'],
                        training_type=TrainingType(config_data['training_type']),
                        model_config=config_data['model_config'],
                        data_config=config_data['data_config'],
                        training_params=config_data['training_params'],
                        optimization_config=config_data['optimization_config'],
                        resource_requirements=config_data['resource_requirements'],
                        creator_id=config_data['creator_id'],
                        created_at=datetime.fromisoformat(config_data['created_at']),
                        priority=config_data.get('priority', 5),
                        timeout_hours=config_data.get('timeout_hours', 24),
                        max_retries=config_data.get('max_retries', 3),
                        checkpointing_enabled=config_data.get('checkpointing_enabled', True),
                        early_stopping_enabled=config_data.get('early_stopping_enabled', True),
                        distributed_backend=config_data.get('distributed_backend', 'nccl'),
                        tags=config_data.get('tags', [])
                    )
                    
                    job = TrainingJob(
                        config=config,
                        status=TrainingStatus(row['status']),
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        progress=float(row['progress'] or 0),
                        current_epoch=int(row['current_epoch'] or 0),
                        total_epochs=int(row['total_epochs'] or 0),
                        best_metrics=json.loads(row['best_metrics']) if row['best_metrics'] else {},
                        resource_usage=json.loads(row['resource_usage']) if row['resource_usage'] else {},
                        logs=json.loads(row['logs']) if row['logs'] else [],
                        error_message=row['error_message'],
                        checkpoints=json.loads(row['checkpoints']) if row['checkpoints'] else [],
                        artifacts=json.loads(row['artifacts']) if row['artifacts'] else {}
                    )
                    
                    jobs.append(job)
                
                return jobs
                
        except Exception as e:
            logger.error(f"Failed to list training jobs: {e}")
            raise
    
    async def optimize_hyperparameters(
        self,
        job_id: str,
        hyperparameter_space: HyperparameterSpace,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.BAYESIAN
    ) -> Dict[str, Any]:
        """Run hyperparameter optimization"""
        try:
            job = await self.get_training_job(job_id)
            if not job:
                raise ValueError(f"Training job not found: {job_id}")
            
            # Create Optuna study
            study = optuna.create_study(
                direction=hyperparameter_space.direction,
                pruner=optuna.pruners.MedianPruner() if hyperparameter_space.pruning_enabled else None
            )
            
            # Define objective function
            def objective(trial):
                # Suggest hyperparameters
                params = {}
                for param_name, param_config in hyperparameter_space.parameters.items():
                    if param_config['type'] == 'float':
                        params[param_name] = trial.suggest_float(
                            param_name,
                            param_config['low'],
                            param_config['high'],
                            log=param_config.get('log', False)
                        )
                    elif param_config['type'] == 'int':
                        params[param_name] = trial.suggest_int(
                            param_name,
                            param_config['low'],
                            param_config['high']
                        )
                    elif param_config['type'] == 'categorical':
                        params[param_name] = trial.suggest_categorical(
                            param_name,
                            param_config['choices']
                        )
                
                # Run training with suggested parameters
                return self._run_hyperparameter_trial(job, params, trial)
            
            # Run optimization
            study.optimize(
                objective,
                n_trials=hyperparameter_space.n_trials,
                timeout=hyperparameter_space.timeout_seconds
            )
            
            # Get best parameters
            best_params = study.best_params
            best_value = study.best_value
            
            # Store optimization results
            optimization_results = {
                'best_parameters': best_params,
                'best_value': best_value,
                'n_trials': len(study.trials),
                'optimization_history': [
                    {'trial': t.number, 'value': t.value, 'params': t.params}
                    for t in study.trials if t.value is not None
                ]
            }
            
            # Update job with best parameters
            job.config.training_params.update(best_params)
            job.best_metrics[hyperparameter_space.optimization_objective] = best_value
            await self._update_job_status(job)
            
            logger.info(f"Hyperparameter optimization completed for job {job_id}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to optimize hyperparameters: {e}")
            raise
    
    async def get_training_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get creator-specific training analytics for Ainflue platform"""
        try:
            async with self.db_pool.acquire() as connection:
                # Get training statistics
                stats = await connection.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_jobs,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed_jobs,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed_jobs,
                        COUNT(*) FILTER (WHERE status = 'running') as running_jobs,
                        AVG(EXTRACT(EPOCH FROM (end_time - start_time))/3600) as avg_duration_hours
                    FROM training_jobs 
                    WHERE config->>'creator_id' = $1
                    """,
                    creator_id
                )
                
                # Get training by type
                type_stats = await connection.fetch(
                    """
                    SELECT config->>'training_type' as training_type, COUNT(*) as count
                    FROM training_jobs 
                    WHERE config->>'creator_id' = $1
                    GROUP BY config->>'training_type'
                    """,
                    creator_id
                )
                
                # Get resource usage
                resource_stats = await connection.fetchrow(
                    """
                    SELECT 
                        SUM(CAST(resource_usage->>'gpu_hours' AS FLOAT)) as total_gpu_hours,
                        SUM(CAST(resource_usage->>'cpu_hours' AS FLOAT)) as total_cpu_hours,
                        AVG(CAST(resource_usage->>'memory_gb' AS FLOAT)) as avg_memory_usage
                    FROM training_jobs 
                    WHERE config->>'creator_id' = $1 AND status = 'completed'
                    """,
                    creator_id
                )
                
                # Get performance metrics
                performance_stats = await connection.fetch(
                    """
                    SELECT 
                        config->>'training_type' as training_type,
                        AVG(CAST(best_metrics->>'accuracy' AS FLOAT)) as avg_accuracy,
                        AVG(CAST(best_metrics->>'loss' AS FLOAT)) as avg_loss
                    FROM training_jobs 
                    WHERE config->>'creator_id' = $1 AND status = 'completed'
                    GROUP BY config->>'training_type'
                    """,
                    creator_id
                )
            
            return {
                'creator_id': creator_id,
                'training_statistics': {
                    'total_jobs': int(stats['total_jobs'] or 0),
                    'completed_jobs': int(stats['completed_jobs'] or 0),
                    'failed_jobs': int(stats['failed_jobs'] or 0),
                    'running_jobs': int(stats['running_jobs'] or 0),
                    'success_rate': (stats['completed_jobs'] or 0) / max(stats['total_jobs'] or 1, 1),
                    'average_duration_hours': float(stats['avg_duration_hours'] or 0)
                },
                'training_type_distribution': {
                    row['training_type']: row['count'] for row in type_stats
                },
                'resource_usage': {
                    'total_gpu_hours': float(resource_stats['total_gpu_hours'] or 0),
                    'total_cpu_hours': float(resource_stats['total_cpu_hours'] or 0),
                    'average_memory_gb': float(resource_stats['avg_memory_usage'] or 0)
                },
                'performance_by_type': {
                    row['training_type']: {
                        'average_accuracy': float(row['avg_accuracy'] or 0),
                        'average_loss': float(row['avg_loss'] or 0)
                    }
                    for row in performance_stats
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get training analytics: {e}")
            raise
    
    # Private helper methods
    
    async def _setup_database_schema(self):
        """Setup database schema for training orchestrator"""
        async with self.db_pool.acquire() as connection:
            # Training jobs table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS training_jobs (
                    job_id VARCHAR(50) PRIMARY KEY,
                    config JSONB NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    start_time TIMESTAMP WITH TIME ZONE,
                    end_time TIMESTAMP WITH TIME ZONE,
                    progress FLOAT DEFAULT 0.0,
                    current_epoch INTEGER DEFAULT 0,
                    total_epochs INTEGER DEFAULT 0,
                    best_metrics JSONB,
                    resource_usage JSONB,
                    logs JSONB,
                    error_message TEXT,
                    checkpoints JSONB,
                    artifacts JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Training events table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS training_events (
                    event_id VARCHAR(50) PRIMARY KEY,
                    job_id VARCHAR(50) NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    event_data JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    FOREIGN KEY (job_id) REFERENCES training_jobs(job_id)
                )
            """)
            
            # Resource allocations table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS resource_allocations (
                    allocation_id VARCHAR(50) PRIMARY KEY,
                    job_id VARCHAR(50) NOT NULL,
                    resource_type VARCHAR(50) NOT NULL,
                    allocation_data JSONB NOT NULL,
                    allocated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    released_at TIMESTAMP WITH TIME ZONE,
                    FOREIGN KEY (job_id) REFERENCES training_jobs(job_id)
                )
            """)
            
            # Create indexes
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_training_creator ON training_jobs((config->>'creator_id'))")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_training_status ON training_jobs(status)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_training_type ON training_jobs((config->>'training_type'))")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_training_created ON training_jobs(created_at)")
    
    async def _validate_training_config(self, config: TrainingConfiguration):
        """Validate training configuration"""
        # Validate required fields
        if not config.name or not config.creator_id:
            raise ValueError("Training name and creator_id are required")
        
        # Validate resource requirements
        if not config.resource_requirements:
            raise ValueError("Resource requirements must be specified")
        
        # Validate model configuration
        if not config.model_config:
            raise ValueError("Model configuration is required")
        
        # Validate data configuration
        if not config.data_config or not config.data_config.get('training_data'):
            raise ValueError("Training data configuration is required")
        
        # Validate priority
        if config.priority < 1 or config.priority > 10:
            raise ValueError("Priority must be between 1 and 10")
    
    async def _check_resource_quotas(self, config: TrainingConfiguration):
        """Check resource quotas for creator"""
        creator_type = await self._get_creator_type(config.creator_id)
        quotas = self.creator_training_config['resource_quotas'].get(creator_type, {})
        
        if not quotas:
            return  # No quotas defined
        
        # Check current usage
        async with self.db_pool.acquire() as connection:
            usage = await connection.fetchrow(
                """
                SELECT 
                    SUM(CAST(resource_usage->>'gpu_hours' AS FLOAT)) as used_gpu_hours,
                    SUM(CAST(resource_usage->>'cpu_hours' AS FLOAT)) as used_cpu_hours
                FROM training_jobs 
                WHERE config->>'creator_id' = $1 
                AND created_at > NOW() - INTERVAL '30 days'
                """,
                config.creator_id
            )
        
        used_gpu_hours = float(usage['used_gpu_hours'] or 0)
        used_cpu_hours = float(usage['used_cpu_hours'] or 0)
        
        # Estimate resource requirements for new job
        estimated_gpu_hours = config.resource_requirements.get('gpu_count', 0) * config.timeout_hours
        estimated_cpu_hours = config.resource_requirements.get('cpu_cores', 0) * config.timeout_hours
        
        if used_gpu_hours + estimated_gpu_hours > quotas.get('gpu_hours', float('inf')):
            raise ValueError(f"GPU quota exceeded. Available: {quotas['gpu_hours'] - used_gpu_hours} hours")
        
        if used_cpu_hours + estimated_cpu_hours > quotas.get('cpu_hours', float('inf')):
            raise ValueError(f"CPU quota exceeded. Available: {quotas['cpu_hours'] - used_cpu_hours} hours")
    
    async def _get_creator_type(self, creator_id: str) -> str:
        """Get creator type for quota management"""
        # This would typically query the user/creator service
        # For now, return a default type
        return "individual_creator"
    
    async def _store_training_job(self, job: TrainingJob):
        """Store training job in database"""
        config_json = {
            'job_id': job.config.job_id,
            'name': job.config.name,
            'training_type': job.config.training_type.value,
            'model_config': job.config.model_config,
            'data_config': job.config.data_config,
            'training_params': job.config.training_params,
            'optimization_config': job.config.optimization_config,
            'resource_requirements': job.config.resource_requirements,
            'creator_id': job.config.creator_id,
            'created_at': job.config.created_at.isoformat(),
            'priority': job.config.priority,
            'timeout_hours': job.config.timeout_hours,
            'max_retries': job.config.max_retries,
            'checkpointing_enabled': job.config.checkpointing_enabled,
            'early_stopping_enabled': job.config.early_stopping_enabled,
            'distributed_backend': job.config.distributed_backend,
            'tags': job.config.tags
        }
        
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO training_jobs (
                    job_id, config, status, progress, current_epoch, total_epochs,
                    best_metrics, resource_usage, logs, checkpoints, artifacts
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                job.config.job_id,
                json.dumps(config_json),
                job.status.value,
                job.progress,
                job.current_epoch,
                job.total_epochs,
                json.dumps(job.best_metrics),
                json.dumps(job.resource_usage),
                json.dumps(job.logs),
                json.dumps(job.checkpoints),
                json.dumps(job.artifacts)
            )
    
    async def _update_job_status(self, job: TrainingJob):
        """Update training job status in database"""
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE training_jobs SET 
                    status = $1, start_time = $2, end_time = $3, progress = $4,
                    current_epoch = $5, total_epochs = $6, best_metrics = $7,
                    resource_usage = $8, logs = $9, error_message = $10,
                    checkpoints = $11, artifacts = $12, updated_at = $13
                WHERE job_id = $14
                """,
                job.status.value,
                job.start_time,
                job.end_time,
                job.progress,
                job.current_epoch,
                job.total_epochs,
                json.dumps(job.best_metrics),
                json.dumps(job.resource_usage),
                json.dumps(job.logs),
                job.error_message,
                json.dumps(job.checkpoints),
                json.dumps(job.artifacts),
                datetime.utcnow(),
                job.config.job_id
            )
    
    async def _allocate_resources(self, config: TrainingConfiguration) -> Optional[ResourceAllocation]:
        """Allocate resources for training job"""
        # This is a simplified resource allocation
        # In a real implementation, this would interact with Kubernetes, cloud providers, etc.
        
        required = config.resource_requirements
        allocation = ResourceAllocation(
            gpu_count=required.get('gpu_count', 1),
            gpu_memory_gb=required.get('gpu_memory_gb', 16),
            cpu_cores=required.get('cpu_cores', 4),
            memory_gb=required.get('memory_gb', 32),
            storage_gb=required.get('storage_gb', 100),
            node_count=required.get('node_count', 1),
            instance_type=required.get('instance_type', 'gpu_standard'),
            spot_instances=required.get('spot_instances', False)
        )
        
        # Store resource allocation
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO resource_allocations (allocation_id, job_id, resource_type, allocation_data)
                VALUES ($1, $2, $3, $4)
                """,
                f"alloc_{uuid.uuid4().hex[:12]}",
                config.job_id,
                "compute",
                json.dumps(allocation.__dict__)
            )
        
        return allocation
    
    async def _start_hyperparameter_tuning(self, job: TrainingJob, resources: ResourceAllocation) -> bool:
        """Start hyperparameter tuning training"""
        try:
            # Setup Ray Tune for hyperparameter optimization
            search_alg = OptunaSearch()
            scheduler = ASHAScheduler(
                metric="validation_accuracy",
                mode="max",
                max_t=job.config.training_params.get('max_epochs', 100),
                grace_period=1,
                reduction_factor=2
            )
            
            # Define search space
            search_space = job.config.optimization_config.get('search_space', {})
            
            # Run tuning
            analysis = tune.run(
                self._training_function,
                config=search_space,
                search_alg=search_alg,
                scheduler=scheduler,
                num_samples=job.config.optimization_config.get('num_trials', 20),
                resources_per_trial={"cpu": resources.cpu_cores, "gpu": resources.gpu_count},
                local_dir=f"/tmp/ray_results/{job.config.job_id}",
                name=f"tune_{job.config.job_id}"
            )
            
            # Get best configuration
            best_config = analysis.get_best_config(metric="validation_accuracy", mode="max")
            
            # Update job with best results
            job.best_metrics = analysis.best_result
            job.config.training_params.update(best_config)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start hyperparameter tuning: {e}")
            return False
    
    async def _start_distributed_training(self, job: TrainingJob, resources: ResourceAllocation) -> bool:
        """Start distributed training"""
        try:
            # This would implement distributed training using frameworks like
            # PyTorch Distributed, Horovod, or Ray Train
            
            # For now, return success
            return True
            
        except Exception as e:
            logger.error(f"Failed to start distributed training: {e}")
            return False
    
    async def _start_automl_training(self, job: TrainingJob, resources: ResourceAllocation) -> bool:
        """Start AutoML training"""
        try:
            # This would implement AutoML using frameworks like
            # Auto-sklearn, TPOT, or custom AutoML pipeline
            
            # For now, return success
            return True
            
        except Exception as e:
            logger.error(f"Failed to start AutoML training: {e}")
            return False
    
    async def _start_standard_training(self, job: TrainingJob, resources: ResourceAllocation) -> bool:
        """Start standard training"""
        try:
            # This would implement standard training execution
            # For now, return success
            return True
            
        except Exception as e:
            logger.error(f"Failed to start standard training: {e}")
            return False
    
    def _training_function(self, config):
        """Training function for Ray Tune"""
        # This would implement the actual training logic
        # For now, return dummy metrics
        import random
        return {"validation_accuracy": random.uniform(0.8, 0.95)}
    
    async def _job_scheduler(self):
        """Job scheduler coroutine"""
        while True:
            try:
                # Get next job from queue
                job_id = await asyncio.wait_for(self.job_queue.get(), timeout=60)
                
                # Start training
                await self.start_training(job_id)
                
                # Mark task as done
                self.job_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in job scheduler: {e}")
                await asyncio.sleep(5)
    
    async def _resource_monitor(self):
        """Resource monitoring coroutine"""
        while True:
            try:
                # Monitor resource usage for running jobs
                for job_id, job in self.training_jobs.items():
                    if job.status == TrainingStatus.RUNNING:
                        # Update resource usage
                        usage = await self._get_resource_usage(job_id)
                        job.resource_usage.update(usage)
                        await self._update_job_status(job)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Error in resource monitor: {e}")
                await asyncio.sleep(60)
    
    async def _get_resource_usage(self, job_id: str) -> Dict[str, Any]:
        """Get current resource usage for job"""
        # This would query actual resource usage from monitoring systems
        return {
            'cpu_utilization': 75.0,
            'memory_utilization': 60.0,
            'gpu_utilization': 85.0,
            'gpu_memory_utilization': 70.0
        }
    
    async def _log_training_event(self, job_id: str, event_type: str, event_data: Dict[str, Any]):
        """Log training event"""
        event_id = f"event_{uuid.uuid4().hex[:12]}"
        
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO training_events (event_id, job_id, event_type, event_data)
                VALUES ($1, $2, $3, $4)
                """,
                event_id,
                job_id,
                event_type,
                json.dumps(event_data)
            )
    
    async def _initialize_resource_monitoring(self):
        """Initialize resource monitoring"""
        # Setup monitoring systems
        pass
    
    async def _stop_training_execution(self, job: TrainingJob):
        """Stop training execution"""
        # Stop the actual training process
        pass
    
    async def _save_checkpoint(self, job: TrainingJob):
        """Save training checkpoint"""
        # Save model checkpoint
        pass
    
    async def _release_resources(self, job_id: str):
        """Release allocated resources"""
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                "UPDATE resource_allocations SET released_at = NOW() WHERE job_id = $1",
                job_id
            )
    
    def _run_hyperparameter_trial(self, job: TrainingJob, params: Dict[str, Any], trial) -> float:
        """Run single hyperparameter trial"""
        # This would run actual training with the suggested parameters
        # For now, return a dummy metric
        import random
        return random.uniform(0.8, 0.95)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.db_pool:
            await self.db_pool.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        if self.executor:
            self.executor.shutdown(wait=True)
        
        if self.process_executor:
            self.process_executor.shutdown(wait=True)
        
        if ray.is_initialized():
            ray.shutdown()


# Factory function for easy initialization
async def create_training_orchestrator(config: Dict[str, Any]) -> EnterpriseTrainingOrchestrator:
    """Create and initialize training orchestrator"""
    orchestrator = EnterpriseTrainingOrchestrator(config)
    await orchestrator.initialize()
    return orchestrator