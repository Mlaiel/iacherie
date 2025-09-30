"""
Experiment Orchestrator
Enterprise-grade experiment orchestration and lifecycle management

This module handles:
- Experiment creation and configuration
- Lifecycle management (start, pause, stop, rollback)
- Multi-variate experiment coordination
- Resource allocation and scheduling
- Experiment dependency management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class ExperimentType(Enum):
    AB_TEST = "ab_test"
    MULTIVARIATE = "multivariate"
    SPLIT_TEST = "split_test"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"

@dataclass
class ExperimentConfig:
    """Experiment configuration dataclass"""
    name: str
    description: str
    experiment_type: ExperimentType
    model_variants: List[str]
    traffic_allocation: Dict[str, float]
    target_metrics: List[str]
    success_criteria: Dict[str, Any]
    duration_days: int
    minimum_sample_size: int
    confidence_level: float = 0.95
    power: float = 0.8
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ExperimentState:
    """Current experiment state"""
    experiment_id: str
    config: ExperimentConfig
    status: ExperimentStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_allocation: Optional[Dict[str, float]] = None
    collected_metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class ExperimentOrchestrator:
    """
    Enterprise experiment orchestrator for MLOps
    Manages complex experiments across multiple models and environments
    """
    
    def __init__(self):
        self.experiments: Dict[str, ExperimentState] = {}
        self.scheduler_running = False
        self.resource_manager = None
        
    async def create_experiment(
        self,
        name: str,
        model_a: str,
        model_b: str,
        traffic_split: float = 0.5,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new A/B experiment
        
        Args:
            name: Experiment name
            model_a: Control model identifier
            model_b: Treatment model identifier
            traffic_split: Traffic allocation for model B
            config: Additional configuration
            
        Returns:
            experiment_id: Unique experiment identifier
        """
        try:
            experiment_id = str(uuid.uuid4())
            
            # Default configuration
            default_config = {
                "description": f"A/B test comparing {model_a} vs {model_b}",
                "experiment_type": ExperimentType.AB_TEST,
                "model_variants": [model_a, model_b],
                "traffic_allocation": {
                    model_a: 1.0 - traffic_split,
                    model_b: traffic_split
                },
                "target_metrics": ["accuracy", "latency", "throughput"],
                "success_criteria": {
                    "primary_metric": "accuracy",
                    "minimum_improvement": 0.02,
                    "maximum_degradation": {"latency": 0.1}
                },
                "duration_days": 7,
                "minimum_sample_size": 1000,
                "confidence_level": 0.95,
                "power": 0.8
            }
            
            # Merge with provided config
            if config:
                default_config.update(config)
                
            # Create experiment configuration
            experiment_config = ExperimentConfig(
                name=name,
                **default_config
            )
            
            # Initialize experiment state
            experiment_state = ExperimentState(
                experiment_id=experiment_id,
                config=experiment_config,
                status=ExperimentStatus.DRAFT,
                created_at=datetime.utcnow()
            )
            
            # Store experiment
            self.experiments[experiment_id] = experiment_state
            
            logger.info(f"Created experiment {experiment_id}: {name}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            raise
    
    async def create_multivariate_experiment(
        self,
        name: str,
        model_variants: List[str],
        traffic_allocation: Dict[str, float],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create multivariate experiment with multiple model variants
        
        Args:
            name: Experiment name
            model_variants: List of model identifiers
            traffic_allocation: Traffic distribution across variants
            config: Additional configuration
            
        Returns:
            experiment_id: Unique experiment identifier
        """
        try:
            # Validate traffic allocation
            if abs(sum(traffic_allocation.values()) - 1.0) > 0.001:
                raise ValueError("Traffic allocation must sum to 1.0")
                
            if not all(variant in model_variants for variant in traffic_allocation.keys()):
                raise ValueError("All variants in allocation must be in model_variants")
                
            experiment_id = str(uuid.uuid4())
            
            # Multivariate configuration
            multivariate_config = {
                "description": f"Multivariate test with {len(model_variants)} variants",
                "experiment_type": ExperimentType.MULTIVARIATE,
                "model_variants": model_variants,
                "traffic_allocation": traffic_allocation,
                "target_metrics": ["accuracy", "precision", "recall", "f1_score", "latency"],
                "success_criteria": {
                    "primary_metric": "accuracy",
                    "minimum_improvement": 0.02,
                    "statistical_power": 0.8
                },
                "duration_days": 14,  # Longer duration for multivariate
                "minimum_sample_size": 2000,  # Larger sample size needed
                "confidence_level": 0.95
            }
            
            if config:
                multivariate_config.update(config)
                
            experiment_config = ExperimentConfig(
                name=name,
                **multivariate_config
            )
            
            experiment_state = ExperimentState(
                experiment_id=experiment_id,
                config=experiment_config,
                status=ExperimentStatus.DRAFT,
                created_at=datetime.utcnow()
            )
            
            self.experiments[experiment_id] = experiment_state
            
            logger.info(f"Created multivariate experiment {experiment_id}: {name}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create multivariate experiment: {e}")
            raise
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """
        Start an experiment
        
        Args:
            experiment_id: Experiment to start
            
        Returns:
            success: Whether experiment started successfully
        """
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
                
            experiment = self.experiments[experiment_id]
            
            if experiment.status != ExperimentStatus.DRAFT:
                raise ValueError(f"Experiment {experiment_id} is not in draft status")
            
            # Pre-flight checks
            await self._validate_experiment_setup(experiment)
            
            # Allocate resources
            await self._allocate_experiment_resources(experiment)
            
            # Start traffic routing
            await self._configure_traffic_routing(experiment)
            
            # Update experiment status
            experiment.status = ExperimentStatus.RUNNING
            experiment.started_at = datetime.utcnow()
            experiment.current_allocation = experiment.config.traffic_allocation.copy()
            
            # Start monitoring
            await self._start_experiment_monitoring(experiment)
            
            logger.info(f"Started experiment {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start experiment {experiment_id}: {e}")
            if experiment_id in self.experiments:
                self.experiments[experiment_id].status = ExperimentStatus.FAILED
                self.experiments[experiment_id].error_message = str(e)
            raise
    
    async def pause_experiment(self, experiment_id: str) -> bool:
        """Pause a running experiment"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
                
            experiment = self.experiments[experiment_id]
            
            if experiment.status != ExperimentStatus.RUNNING:
                raise ValueError(f"Experiment {experiment_id} is not running")
            
            # Stop traffic routing
            await self._stop_traffic_routing(experiment)
            
            # Update status
            experiment.status = ExperimentStatus.PAUSED
            
            logger.info(f"Paused experiment {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause experiment {experiment_id}: {e}")
            raise
    
    async def stop_experiment(self, experiment_id: str) -> bool:
        """Stop and complete an experiment"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
                
            experiment = self.experiments[experiment_id]
            
            if experiment.status not in [ExperimentStatus.RUNNING, ExperimentStatus.PAUSED]:
                raise ValueError(f"Experiment {experiment_id} cannot be stopped from current status")
            
            # Stop traffic routing
            await self._stop_traffic_routing(experiment)
            
            # Collect final metrics
            final_metrics = await self._collect_final_metrics(experiment)
            experiment.collected_metrics = final_metrics
            
            # Clean up resources
            await self._cleanup_experiment_resources(experiment)
            
            # Update status
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.utcnow()
            
            logger.info(f"Completed experiment {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop experiment {experiment_id}: {e}")
            raise
    
    async def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Get current experiment status and metrics"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
                
            experiment = self.experiments[experiment_id]
            
            # Get current metrics
            current_metrics = await self._get_current_metrics(experiment)
            
            return {
                "experiment_id": experiment_id,
                "name": experiment.config.name,
                "status": experiment.status.value,
                "created_at": experiment.created_at.isoformat(),
                "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
                "completed_at": experiment.completed_at.isoformat() if experiment.completed_at else None,
                "config": asdict(experiment.config),
                "current_allocation": experiment.current_allocation,
                "current_metrics": current_metrics,
                "error_message": experiment.error_message
            }
            
        except Exception as e:
            logger.error(f"Failed to get experiment status: {e}")
            raise
    
    async def list_experiments(
        self,
        status_filter: Optional[ExperimentStatus] = None
    ) -> List[Dict[str, Any]]:
        """List all experiments with optional status filter"""
        try:
            experiments = []
            
            for experiment_id, experiment in self.experiments.items():
                if status_filter and experiment.status != status_filter:
                    continue
                    
                experiments.append({
                    "experiment_id": experiment_id,
                    "name": experiment.config.name,
                    "status": experiment.status.value,
                    "experiment_type": experiment.config.experiment_type.value,
                    "created_at": experiment.created_at.isoformat(),
                    "model_variants": experiment.config.model_variants
                })
            
            return experiments
            
        except Exception as e:
            logger.error(f"Failed to list experiments: {e}")
            raise
    
    async def _validate_experiment_setup(self, experiment: ExperimentState) -> None:
        """Validate experiment configuration before starting"""
        # Validate models exist and are ready
        for variant in experiment.config.model_variants:
            if not await self._validate_model_ready(variant):
                raise ValueError(f"Model {variant} is not ready for experiment")
        
        # Validate traffic allocation
        total_allocation = sum(experiment.config.traffic_allocation.values())
        if abs(total_allocation - 1.0) > 0.001:
            raise ValueError("Traffic allocation must sum to 1.0")
    
    async def _validate_model_ready(self, model_id: str) -> bool:
        """Validate that a model is ready for experimentation"""
        # Placeholder - implement actual model validation
        return True
    
    async def _allocate_experiment_resources(self, experiment: ExperimentState) -> None:
        """Allocate necessary resources for experiment"""
        # Placeholder - implement resource allocation
        pass
    
    async def _configure_traffic_routing(self, experiment: ExperimentState) -> None:
        """Configure traffic routing for experiment"""
        # Placeholder - implement traffic routing configuration
        pass
    
    async def _start_experiment_monitoring(self, experiment: ExperimentState) -> None:
        """Start monitoring for experiment metrics"""
        # Placeholder - implement monitoring setup
        pass
    
    async def _stop_traffic_routing(self, experiment: ExperimentState) -> None:
        """Stop traffic routing for experiment"""
        # Placeholder - implement traffic routing cleanup
        pass
    
    async def _collect_final_metrics(self, experiment: ExperimentState) -> Dict[str, Any]:
        """Collect final metrics for completed experiment"""
        # Placeholder - implement final metrics collection
        return {}
    
    async def _cleanup_experiment_resources(self, experiment: ExperimentState) -> None:
        """Clean up resources allocated to experiment"""
        # Placeholder - implement resource cleanup
        pass
    
    async def _get_current_metrics(self, experiment: ExperimentState) -> Dict[str, Any]:
        """Get current metrics for running experiment"""
        # Placeholder - implement current metrics collection
        return {}