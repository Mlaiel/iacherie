"""🔬 Experiment Tracking System - ML Research & Development
===========================================================
Module: ml/experiments/experiment_tracking_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 COMPREHENSIVE EXPERIMENT TRACKING
Comprehensive experiment tracking with hyperparameter and metric logging
- Experiment lifecycle management
- Hyperparameter optimization tracking
- Metric comparison and visualization
- Research collaboration features
"""

import asyncio
import logging
import json
import uuid
import hashlib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pickle
import mlflow
import mlflow.tracking
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    """Experiment status tracking"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class HyperparameterType(Enum):
    """Hyperparameter data types"""
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    FLOAT = "float"

class OptimizationDirection(Enum):
    """Optimization direction for metrics"""
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"

@dataclass
class HyperparameterSpace:
    """Hyperparameter search space definition"""
    name: str
    param_type: HyperparameterType
    values: Union[List[Any], Dict[str, Any]]
    default: Optional[Any] = None
    description: Optional[str] = None

@dataclass
class Metric:
    """Experiment metric definition"""
    name: str
    value: float
    step: Optional[int] = None
    timestamp: Optional[datetime] = None
    direction: OptimizationDirection = OptimizationDirection.MAXIMIZE

@dataclass
class Artifact:
    """Experiment artifact metadata"""
    artifact_id: str
    name: str
    path: str
    artifact_type: str
    size_bytes: int
    checksum: str
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExperimentRun:
    """Individual experiment run"""
    run_id: str
    experiment_id: str
    name: str
    status: ExperimentStatus
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, List[Metric]]
    artifacts: List[Artifact]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    notes: Optional[str] = None
    creator_id: Optional[str] = None

@dataclass
class Experiment:
    """Experiment definition"""
    experiment_id: str
    name: str
    description: str
    created_by: str
    created_at: datetime
    hyperparameter_space: List[HyperparameterSpace]
    objective_metric: str
    optimization_direction: OptimizationDirection
    runs: List[ExperimentRun] = field(default_factory=list)
    status: ExperimentStatus = ExperimentStatus.CREATED
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class HyperparameterOptimizer:
    """Hyperparameter optimization strategies"""
    
    def __init__(self) -> None:
        self.optimization_history: Dict[str, List[Dict[str, Any]]] = {}
    
    async def suggest_hyperparameters(
        self,
        experiment: Experiment,
        strategy: str = "grid_search",
        n_suggestions: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Suggest hyperparameters based on optimization strategy
        """
        try:
            if strategy == "grid_search":
                return await self._grid_search_suggestions(experiment, n_suggestions)
            elif strategy == "random_search":
                return await self._random_search_suggestions(experiment, n_suggestions)
            elif strategy == "bayesian":
                return await self._bayesian_optimization_suggestions(experiment, n_suggestions)
            elif strategy == "evolutionary":
                return await self._evolutionary_suggestions(experiment, n_suggestions)
            else:
                logger.warning(f"Unknown strategy {strategy}, using random search")
                return await self._random_search_suggestions(experiment, n_suggestions)
                
        except Exception as e:
            logger.error(f"Error suggesting hyperparameters: {str(e)}")
            return []

    async def _grid_search_suggestions(
        self,
        experiment: Experiment,
        n_suggestions: int
    ) -> List[Dict[str, Any]]:
        """Grid search hyperparameter suggestions"""
        param_grid = {}
        
        for param_space in experiment.hyperparameter_space:
            if param_space.param_type == HyperparameterType.CATEGORICAL:
                param_grid[param_space.name] = param_space.values
            elif param_space.param_type in [HyperparameterType.NUMERICAL, HyperparameterType.FLOAT]:
                # Create range for numerical parameters
                min_val, max_val = param_space.values.get('min', 0), param_space.values.get('max', 1)
                step = param_space.values.get('step', (max_val - min_val) / 10)
                param_grid[param_space.name] = np.arange(min_val, max_val + step, step).tolist()
            elif param_space.param_type == HyperparameterType.INTEGER:
                min_val, max_val = param_space.values.get('min', 1), param_space.values.get('max', 10)
                param_grid[param_space.name] = list(range(min_val, max_val + 1))
            elif param_space.param_type == HyperparameterType.BOOLEAN:
                param_grid[param_space.name] = [True, False]
        
        # Generate all combinations
        grid = ParameterGrid(param_grid)
        suggestions = list(grid)[:n_suggestions]
        
        return suggestions

    async def _random_search_suggestions(
        self,
        experiment: Experiment,
        n_suggestions: int
    ) -> List[Dict[str, Any]]:
        """Random search hyperparameter suggestions"""
        suggestions = []
        
        for _ in range(n_suggestions):
            suggestion = {}
            
            for param_space in experiment.hyperparameter_space:
                if param_space.param_type == HyperparameterType.CATEGORICAL:
                    suggestion[param_space.name] = np.random.choice(param_space.values)
                elif param_space.param_type in [HyperparameterType.NUMERICAL, HyperparameterType.FLOAT]:
                    min_val = param_space.values.get('min', 0)
                    max_val = param_space.values.get('max', 1)
                    suggestion[param_space.name] = np.random.uniform(min_val, max_val)
                elif param_space.param_type == HyperparameterType.INTEGER:
                    min_val = param_space.values.get('min', 1)
                    max_val = param_space.values.get('max', 10)
                    suggestion[param_space.name] = np.random.randint(min_val, max_val + 1)
                elif param_space.param_type == HyperparameterType.BOOLEAN:
                    suggestion[param_space.name] = np.random.choice([True, False])
            
            suggestions.append(suggestion)
        
        return suggestions

    async def _bayesian_optimization_suggestions(
        self,
        experiment: Experiment,
        n_suggestions: int
    ) -> List[Dict[str, Any]]:
        """Bayesian optimization suggestions (simplified implementation)"""
        # In a real implementation, this would use libraries like scikit-optimize or optuna
        # For now, we'll use an intelligent random search based on previous results
        
        if not experiment.runs:
            # No previous runs, fall back to random search
            return await self._random_search_suggestions(experiment, n_suggestions)
        
        # Analyze previous runs to inform suggestions
        best_runs = sorted(
            [run for run in experiment.runs if run.status == ExperimentStatus.COMPLETED],
            key=lambda r: self._get_objective_value(r, experiment.objective_metric),
            reverse=(experiment.optimization_direction == OptimizationDirection.MAXIMIZE)
        )[:3]  # Top 3 runs
        
        suggestions = []
        
        for _ in range(n_suggestions):
            suggestion = {}
            
            if best_runs and np.random.random() < 0.7:  # 70% chance to explore around best runs
                base_run = np.random.choice(best_runs)
                
                for param_space in experiment.hyperparameter_space:
                    param_name = param_space.name
                    base_value = base_run.hyperparameters.get(param_name)
                    
                    if param_space.param_type == HyperparameterType.CATEGORICAL:
                        # Small chance to change categorical parameters
                        if np.random.random() < 0.3:
                            suggestion[param_name] = np.random.choice(param_space.values)
                        else:
                            suggestion[param_name] = base_value
                    elif param_space.param_type in [HyperparameterType.NUMERICAL, HyperparameterType.FLOAT]:
                        # Add noise to numerical parameters
                        min_val = param_space.values.get('min', 0)
                        max_val = param_space.values.get('max', 1)
                        noise_scale = (max_val - min_val) * 0.1
                        new_value = base_value + np.random.normal(0, noise_scale)
                        suggestion[param_name] = np.clip(new_value, min_val, max_val)
                    else:
                        suggestion[param_name] = base_value
            else:
                # Random exploration
                random_suggestions = await self._random_search_suggestions(experiment, 1)
                suggestion = random_suggestions[0]
            
            suggestions.append(suggestion)
        
        return suggestions

    async def _evolutionary_suggestions(
        self,
        experiment: Experiment,
        n_suggestions: int
    ) -> List[Dict[str, Any]]:
        """Evolutionary algorithm suggestions"""
        # Simplified genetic algorithm approach
        if len(experiment.runs) < 2:
            return await self._random_search_suggestions(experiment, n_suggestions)
        
        # Select parent runs (top performers)
        completed_runs = [run for run in experiment.runs if run.status == ExperimentStatus.COMPLETED]
        if len(completed_runs) < 2:
            return await self._random_search_suggestions(experiment, n_suggestions)
        
        parents = sorted(
            completed_runs,
            key=lambda r: self._get_objective_value(r, experiment.objective_metric),
            reverse=(experiment.optimization_direction == OptimizationDirection.MAXIMIZE)
        )[:max(2, len(completed_runs) // 2)]
        
        suggestions = []
        
        for _ in range(n_suggestions):
            # Select two parents
            parent1, parent2 = np.random.choice(parents, 2, replace=False)
            
            # Crossover
            suggestion = {}
            for param_space in experiment.hyperparameter_space:
                param_name = param_space.name
                
                # Choose from one of the parents
                if np.random.random() < 0.5:
                    suggestion[param_name] = parent1.hyperparameters.get(param_name)
                else:
                    suggestion[param_name] = parent2.hyperparameters.get(param_name)
                
                # Mutation
                if np.random.random() < 0.1:  # 10% mutation rate
                    if param_space.param_type == HyperparameterType.CATEGORICAL:
                        suggestion[param_name] = np.random.choice(param_space.values)
                    elif param_space.param_type in [HyperparameterType.NUMERICAL, HyperparameterType.FLOAT]:
                        min_val = param_space.values.get('min', 0)
                        max_val = param_space.values.get('max', 1)
                        suggestion[param_name] = np.random.uniform(min_val, max_val)
            
            suggestions.append(suggestion)
        
        return suggestions

    def _get_objective_value(self, run: ExperimentRun, objective_metric: str) -> float:
        """Get objective metric value from run"""
        if objective_metric in run.metrics and run.metrics[objective_metric]:
            return run.metrics[objective_metric][-1].value
        return 0.0

class ExperimentTrackingSystem:
    """
    Comprehensive experiment tracking system for ML research
    """
    
    def __init__(self, storage_path -> None: str = "./experiments", use_mlflow -> None: bool = True) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.experiments: Dict[str, Experiment] = {}
        self.use_mlflow = use_mlflow
        self.optimizer = HyperparameterOptimizer()
        
        if use_mlflow:
            mlflow.set_tracking_uri(f"file://{self.storage_path}/mlruns")

    async def create_experiment(
        self,
        name: str,
        description: str,
        created_by: str,
        hyperparameter_space: List[HyperparameterSpace],
        objective_metric: str,
        optimization_direction: OptimizationDirection = OptimizationDirection.MAXIMIZE,
        tags: Optional[Dict[str, str]] = None
    ) -> Experiment:
        """
        Create new experiment
        """
        try:
            experiment_id = str(uuid.uuid4())
            
            experiment = Experiment(
                experiment_id=experiment_id,
                name=name,
                description=description,
                created_by=created_by,
                created_at=datetime.utcnow(),
                hyperparameter_space=hyperparameter_space,
                objective_metric=objective_metric,
                optimization_direction=optimization_direction,
                tags=tags or {}
            )
            
            self.experiments[experiment_id] = experiment
            
            # Create MLflow experiment if enabled
            if self.use_mlflow:
                mlflow.create_experiment(
                    name=f"{name}_{experiment_id[:8]}",
                    tags=tags
                )
            
            # Persist experiment
            await self._persist_experiment(experiment)
            
            logger.info(f"Created experiment: {name} ({experiment_id})")
            return experiment
            
        except Exception as e:
            logger.error(f"Error creating experiment: {str(e)}")
            raise

    async def start_run(
        self,
        experiment_id: str,
        name: str,
        hyperparameters: Dict[str, Any],
        tags: Optional[Dict[str, str]] = None,
        notes: Optional[str] = None,
        creator_id: Optional[str] = None
    ) -> ExperimentRun:
        """
        Start new experiment run
        """
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            run_id = str(uuid.uuid4())
            
            run = ExperimentRun(
                run_id=run_id,
                experiment_id=experiment_id,
                name=name,
                status=ExperimentStatus.RUNNING,
                hyperparameters=hyperparameters,
                metrics={},
                artifacts=[],
                start_time=datetime.utcnow(),
                tags=tags or {},
                notes=notes,
                creator_id=creator_id
            )
            
            experiment.runs.append(run)
            
            # Start MLflow run if enabled
            if self.use_mlflow:
                mlflow.start_run(
                    run_name=name,
                    tags=tags
                )
                # Log hyperparameters
                mlflow.log_params(hyperparameters)
            
            logger.info(f"Started run: {name} ({run_id})")
            return run
            
        except Exception as e:
            logger.error(f"Error starting run: {str(e)}")
            raise

    async def log_metric(
        self,
        run_id: str,
        metric_name: str,
        value: float,
        step: Optional[int] = None
    ) -> None:
        """
        Log metric for experiment run
        """
        try:
            run = await self._find_run(run_id)
            if not run:
                raise ValueError(f"Run {run_id} not found")
            
            metric = Metric(
                name=metric_name,
                value=value,
                step=step,
                timestamp=datetime.utcnow()
            )
            
            if metric_name not in run.metrics:
                run.metrics[metric_name] = []
            
            run.metrics[metric_name].append(metric)
            
            # Log to MLflow if enabled
            if self.use_mlflow and mlflow.active_run():
                mlflow.log_metric(metric_name, value, step)
            
        except Exception as e:
            logger.error(f"Error logging metric: {str(e)}")

    async def log_artifact(
        self,
        run_id: str,
        artifact_path: str,
        artifact_name: Optional[str] = None,
        artifact_type: str = "file",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Artifact:
        """
        Log artifact for experiment run
        """
        try:
            run = await self._find_run(run_id)
            if not run:
                raise ValueError(f"Run {run_id} not found")
            
            artifact_path = Path(artifact_path)
            if not artifact_path.exists():
                raise FileNotFoundError(f"Artifact not found: {artifact_path}")
            
            # Calculate checksum
            with open(artifact_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
            
            artifact = Artifact(
                artifact_id=str(uuid.uuid4()),
                name=artifact_name or artifact_path.name,
                path=str(artifact_path),
                artifact_type=artifact_type,
                size_bytes=artifact_path.stat().st_size,
                checksum=checksum,
                created_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            run.artifacts.append(artifact)
            
            # Log to MLflow if enabled
            if self.use_mlflow and mlflow.active_run():
                mlflow.log_artifact(str(artifact_path))
            
            return artifact
            
        except Exception as e:
            logger.error(f"Error logging artifact: {str(e)}")
            raise

    async def finish_run(
        self,
        run_id: str,
        status: ExperimentStatus = ExperimentStatus.COMPLETED,
        error_message: Optional[str] = None
    ) -> None:
        """
        Finish experiment run
        """
        try:
            run = await self._find_run(run_id)
            if not run:
                raise ValueError(f"Run {run_id} not found")
            
            run.status = status
            run.end_time = datetime.utcnow()
            run.duration_seconds = (run.end_time - run.start_time).total_seconds()
            
            if error_message:
                run.error_message = error_message
            
            # End MLflow run if enabled
            if self.use_mlflow and mlflow.active_run():
                mlflow.end_run()
            
            # Persist experiment
            experiment = self.experiments[run.experiment_id]
            await self._persist_experiment(experiment)
            
            logger.info(f"Finished run: {run_id} ({status.value})")
            
        except Exception as e:
            logger.error(f"Error finishing run: {str(e)}")

    async def get_best_run(
        self,
        experiment_id: str,
        metric_name: Optional[str] = None
    ) -> Optional[ExperimentRun]:
        """
        Get best run from experiment
        """
        try:
            if experiment_id not in self.experiments:
                return None
            
            experiment = self.experiments[experiment_id]
            objective_metric = metric_name or experiment.objective_metric
            
            completed_runs = [
                run for run in experiment.runs 
                if run.status == ExperimentStatus.COMPLETED and 
                objective_metric in run.metrics
            ]
            
            if not completed_runs:
                return None
            
            best_run = max(
                completed_runs,
                key=lambda r: self.optimizer._get_objective_value(r, objective_metric)
                if experiment.optimization_direction == OptimizationDirection.MAXIMIZE
                else -self.optimizer._get_objective_value(r, objective_metric)
            )
            
            return best_run
            
        except Exception as e:
            logger.error(f"Error getting best run: {str(e)}")
            return None

    async def suggest_hyperparameters(
        self,
        experiment_id: str,
        strategy: str = "bayesian",
        n_suggestions: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Suggest hyperparameters for next runs
        """
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            suggestions = await self.optimizer.suggest_hyperparameters(
                experiment, strategy, n_suggestions
            )
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting hyperparameters: {str(e)}")
            return []

    async def compare_runs(
        self,
        run_ids: List[str],
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Compare multiple experiment runs
        """
        try:
            runs = []
            for run_id in run_ids:
                run = await self._find_run(run_id)
                if run:
                    runs.append(run)
            
            if not runs:
                return pd.DataFrame()
            
            comparison_data = []
            
            for run in runs:
                row = {
                    'run_id': run.run_id,
                    'name': run.name,
                    'status': run.status.value,
                    'duration_seconds': run.duration_seconds or 0
                }
                
                # Add hyperparameters
                for param, value in run.hyperparameters.items():
                    row[f'param_{param}'] = value
                
                # Add metrics (latest values)
                for metric_name, metric_list in run.metrics.items():
                    if metrics is None or metric_name in metrics:
                        if metric_list:
                            row[f'metric_{metric_name}'] = metric_list[-1].value
                
                comparison_data.append(row)
            
            return pd.DataFrame(comparison_data)
            
        except Exception as e:
            logger.error(f"Error comparing runs: {str(e)}")
            return pd.DataFrame()

    async def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get experiment summary statistics
        """
        try:
            if experiment_id not in self.experiments:
                return {}
            
            experiment = self.experiments[experiment_id]
            
            summary = {
                'experiment_id': experiment_id,
                'name': experiment.name,
                'description': experiment.description,
                'created_by': experiment.created_by,
                'created_at': experiment.created_at.isoformat(),
                'objective_metric': experiment.objective_metric,
                'optimization_direction': experiment.optimization_direction.value,
                'total_runs': len(experiment.runs),
                'completed_runs': len([r for r in experiment.runs if r.status == ExperimentStatus.COMPLETED]),
                'failed_runs': len([r for r in experiment.runs if r.status == ExperimentStatus.FAILED]),
                'running_runs': len([r for r in experiment.runs if r.status == ExperimentStatus.RUNNING])
            }
            
            # Best run information
            best_run = await self.get_best_run(experiment_id)
            if best_run:
                summary['best_run'] = {
                    'run_id': best_run.run_id,
                    'name': best_run.name,
                    'objective_value': self.optimizer._get_objective_value(best_run, experiment.objective_metric),
                    'hyperparameters': best_run.hyperparameters
                }
            
            # Hyperparameter space
            summary['hyperparameter_space'] = [
                {
                    'name': hs.name,
                    'type': hs.param_type.value,
                    'values': hs.values
                }
                for hs in experiment.hyperparameter_space
            ]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting experiment summary: {str(e)}")
            return {}

    async def _find_run(self, run_id: str) -> Optional[ExperimentRun]:
        """Find run by ID across all experiments"""
        for experiment in self.experiments.values():
            for run in experiment.runs:
                if run.run_id == run_id:
                    return run
        return None

    async def _persist_experiment(self, experiment: Experiment) -> None:
        """Persist experiment to storage"""
        try:
            experiment_file = self.storage_path / f"{experiment.experiment_id}.json"
            
            # Convert to serializable format
            experiment_dict = {
                'experiment_id': experiment.experiment_id,
                'name': experiment.name,
                'description': experiment.description,
                'created_by': experiment.created_by,
                'created_at': experiment.created_at.isoformat(),
                'objective_metric': experiment.objective_metric,
                'optimization_direction': experiment.optimization_direction.value,
                'status': experiment.status.value,
                'tags': experiment.tags,
                'metadata': experiment.metadata,
                'hyperparameter_space': [
                    {
                        'name': hs.name,
                        'param_type': hs.param_type.value,
                        'values': hs.values,
                        'default': hs.default,
                        'description': hs.description
                    }
                    for hs in experiment.hyperparameter_space
                ],
                'runs': [
                    {
                        'run_id': run.run_id,
                        'experiment_id': run.experiment_id,
                        'name': run.name,
                        'status': run.status.value,
                        'hyperparameters': run.hyperparameters,
                        'metrics': {
                            name: [
                                {
                                    'name': m.name,
                                    'value': m.value,
                                    'step': m.step,
                                    'timestamp': m.timestamp.isoformat() if m.timestamp else None
                                }
                                for m in metrics_list
                            ]
                            for name, metrics_list in run.metrics.items()
                        },
                        'artifacts': [
                            {
                                'artifact_id': a.artifact_id,
                                'name': a.name,
                                'path': a.path,
                                'artifact_type': a.artifact_type,
                                'size_bytes': a.size_bytes,
                                'checksum': a.checksum,
                                'created_at': a.created_at.isoformat(),
                                'metadata': a.metadata
                            }
                            for a in run.artifacts
                        ],
                        'start_time': run.start_time.isoformat(),
                        'end_time': run.end_time.isoformat() if run.end_time else None,
                        'duration_seconds': run.duration_seconds,
                        'error_message': run.error_message,
                        'tags': run.tags,
                        'notes': run.notes,
                        'creator_id': run.creator_id
                    }
                    for run in experiment.runs
                ]
            }
            
            with open(experiment_file, 'w') as f:
                json.dump(experiment_dict, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error persisting experiment: {str(e)}")

# Usage Example
async def main() -> None:
    """Example usage of ExperimentTrackingSystem"""
    system = ExperimentTrackingSystem()
    
    # Define hyperparameter space
    hyperparameter_space = [
        HyperparameterSpace(
            name="learning_rate",
            param_type=HyperparameterType.FLOAT,
            values={"min": 0.001, "max": 0.1}
        ),
        HyperparameterSpace(
            name="n_estimators",
            param_type=HyperparameterType.INTEGER,
            values={"min": 50, "max": 200}
        ),
        HyperparameterSpace(
            name="max_depth",
            param_type=HyperparameterType.CATEGORICAL,
            values=[3, 5, 7, 10, None]
        )
    ]
    
    # Create experiment
    experiment = await system.create_experiment(
        name="Content Classifier Optimization",
        description="Optimize content classifier for creator platform",
        created_by="fahed@example.com",
        hyperparameter_space=hyperparameter_space,
        objective_metric="accuracy",
        optimization_direction=OptimizationDirection.MAXIMIZE
    )
    
    print(f"Created experiment: {experiment.name}")
    
    # Suggest hyperparameters
    suggestions = await system.suggest_hyperparameters(
        experiment.experiment_id,
        strategy="random_search",
        n_suggestions=2
    )
    
    print(f"Suggested hyperparameters: {suggestions}")
    
    # Run experiments
    for i, params in enumerate(suggestions):
        run = await system.start_run(
            experiment_id=experiment.experiment_id,
            name=f"Run {i+1}",
            hyperparameters=params
        )
        
        # Simulate training and log metrics
        accuracy = np.random.uniform(0.85, 0.95)
        await system.log_metric(run.run_id, "accuracy", accuracy)
        await system.log_metric(run.run_id, "loss", np.random.uniform(0.1, 0.3))
        
        await system.finish_run(run.run_id)
        
        print(f"Completed run {i+1} with accuracy: {accuracy:.3f}")
    
    # Get best run
    best_run = await system.get_best_run(experiment.experiment_id)
    if best_run:
        print(f"Best run: {best_run.name} with accuracy: {best_run.metrics['accuracy'][-1].value:.3f}")
    
    # Get experiment summary
    summary = await system.get_experiment_summary(experiment.experiment_id)
    print(f"Experiment summary: {summary['total_runs']} total runs, {summary['completed_runs']} completed")

if __name__ == "__main__":
    asyncio.run(main())