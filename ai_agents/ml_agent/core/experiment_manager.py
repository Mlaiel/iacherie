"""ML Experiment Manager - Advanced ML Experiment Tracking & Management System

Industrial-grade experiment management providing comprehensive experiment tracking,
hyperparameter optimization, A/B testing, model comparison, and result analysis
for the IA-Influencer-Agent ML platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This experiment management system and methodologies are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025

🎯 BUSINESS LOGIC INTEGRATION:
Experiment Design → Model Training → Performance Evaluation → Statistical Analysis
→ Model Selection → Deployment Decision → Continuous Monitoring

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
import time
import uuid
import json
import pickle
import hashlib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from pathlib import Path
import traceback
import yaml
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# ML and statistics
import sklearn
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, roc_auc_score,
    mean_squared_error, r2_score, classification_report
)

# Experiment tracking
import mlflow
import mlflow.sklearn
import mlflow.tensorflow
import mlflow.pytorch
import wandb

# Hyperparameter optimization
try:
    import optuna
    from optuna.samplers import TPESampler
    from optuna.pruners import MedianPruner
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

# Platform core
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import ExperimentError, ValidationError, ConfigurationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ExperimentError, ValidationError, ConfigurationError = globals().get('ExperimentError, ValidationError, ConfigurationError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.cache import CacheManager

logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    """Experiment execution status"""    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class ExperimentType(Enum):
    """Types of ML experiments"""    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    MODEL_COMPARISON = "model_comparison"
    FEATURE_SELECTION = "feature_selection"
    ARCHITECTURE_SEARCH = "architecture_search"
    AB_TESTING = "ab_testing"
    PERFORMANCE_BENCHMARK = "performance_benchmark"

class MetricType(Enum):
    """ML metric types"""    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    ROC_AUC = "roc_auc"
    MSE = "mse"
    RMSE = "rmse"
    R2_SCORE = "r2_score"
    MAE = "mae"
    LOSS = "loss"

@dataclass
class ExperimentConfig:
    """Experiment configuration"""    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    model_configs: List[Dict[str, Any]]
    hyperparameter_space: Dict[str, Any] = field(default_factory=dict)
    evaluation_metrics: List[MetricType] = field(default_factory=lambda: [MetricType.ACCURACY])
    cross_validation_folds: int = 5
    optimization_direction: str = "maximize"  # maximize or minimize
    max_trials: int = 100
    timeout: int = 3600
    early_stopping_patience: int = 10
    random_seed: int = 42
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExperimentResult:
    """Individual experiment result"""    trial_id: str
    experiment_id: str
    model_config: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, float]
    training_time: float
    cross_val_scores: List[float]
    model_path: Optional[str] = None
    artifacts: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "completed"
    error_message: Optional[str] = None

@dataclass
class ExperimentSummary:
    """Experiment summary and statistics"""    experiment_id: str
    total_trials: int
    completed_trials: int
    failed_trials: int
    best_trial_id: str
    best_score: float
    best_hyperparameters: Dict[str, Any]
    execution_time: float
    statistical_significance: Optional[Dict[str, float]] = None
    convergence_analysis: Optional[Dict[str, Any]] = None

class MLExperimentTracker:
    """    Ultra-advanced ML experiment tracker providing comprehensive
    experiment management, tracking, and analysis capabilities
    """    
    def __init__(self):
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.results: Dict[str, List[ExperimentResult]] = {}
        self.performance_monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()
        self._initialize_tracking()
    
    def _initialize_tracking(self):
        """Initialize experiment tracking backends"""        try:
            # Initialize MLflow
            mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
            
            # Initialize Weights & Biases if configured
            if hasattr(settings, 'WANDB_PROJECT'):
                wandb.login(key=settings.WANDB_API_KEY)
                
            logger.info("Experiment tracking initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize some tracking backends: {str(e)}")
    
    async def create_experiment(self, config: ExperimentConfig) -> str:
        """Create a new ML experiment"""        try:
            # Validate experiment configuration
            await self._validate_experiment_config(config)
            
            # Create MLflow experiment
            experiment_name = f"{config.name}_{config.experiment_id}"
            mlflow_experiment = mlflow.create_experiment(experiment_name)
            
            # Store experiment configuration
            self.experiments[config.experiment_id] = config
            self.results[config.experiment_id] = []
            
            # Log experiment configuration
            with mlflow.start_run(experiment_id=mlflow_experiment):
                mlflow.log_params(asdict(config))
                mlflow.set_tag("experiment_type", config.experiment_type.value)
                mlflow.set_tag("created_at", datetime.now(timezone.utc).isoformat())
            
            logger.info(f"Experiment created: {config.experiment_id}")
            return config.experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create experiment: {str(e)}")
            raise ExperimentError(f"Experiment creation failed: {str(e)}")
    
    async def _validate_experiment_config(self, config: ExperimentConfig):
        """Validate experiment configuration"""        if not config.name:
            raise ValidationError("Experiment name is required")
        
        if not config.model_configs:
            raise ValidationError("At least one model configuration is required")
        
        if config.max_trials <= 0:
            raise ValidationError("Max trials must be positive")
        
        if config.cross_validation_folds < 2:
            raise ValidationError("Cross validation folds must be at least 2")
    
    async def run_experiment(self, experiment_id: str, training_data: Any, target_data: Any) -> ExperimentSummary:
        """Execute a complete ML experiment"""        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            config = self.experiments[experiment_id]
            start_time = time.time()
            
            logger.info(f"Starting experiment: {experiment_id}")
            
            # Execute based on experiment type
            if config.experiment_type == ExperimentType.HYPERPARAMETER_TUNING:
                results = await self._run_hyperparameter_tuning(config, training_data, target_data)
            elif config.experiment_type == ExperimentType.MODEL_COMPARISON:
                results = await self._run_model_comparison(config, training_data, target_data)
            elif config.experiment_type == ExperimentType.FEATURE_SELECTION:
                results = await self._run_feature_selection(config, training_data, target_data)
            else:
                raise ValueError(f"Unsupported experiment type: {config.experiment_type}")
            
            # Store results
            self.results[experiment_id] = results
            
            # Generate summary
            summary = await self._generate_experiment_summary(
                experiment_id, results, time.time() - start_time
            )
            
            # Log summary to tracking backend
            await self._log_experiment_summary(summary)
            
            logger.info(f"Experiment completed: {experiment_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Experiment failed: {experiment_id} - {str(e)}")
            raise ExperimentError(f"Experiment execution failed: {str(e)}")
    
    async def _run_hyperparameter_tuning(
        self, 
        config: ExperimentConfig, 
        training_data: Any, 
        target_data: Any
    ) -> List[ExperimentResult]:
        """Run hyperparameter tuning experiment"""        results = []
        
        if not OPTUNA_AVAILABLE:
            raise ConfigurationError("Optuna is required for hyperparameter tuning")
        
        # Create Optuna study
        study = optuna.create_study(
            direction=config.optimization_direction,
            sampler=TPESampler(seed=config.random_seed),
            pruner=MedianPruner(n_startup_trials=5, n_warmup_steps=10)
        )
        
        def objective(trial):
            return asyncio.run(self._optuna_objective(trial, config, training_data, target_data, results))
        
        # Run optimization
        study.optimize(objective, n_trials=config.max_trials, timeout=config.timeout)
        
        return results
    
    async def _optuna_objective(
        self, 
        trial, 
        config: ExperimentConfig,
        training_data: Any,
        target_data: Any,
        results: List[ExperimentResult]
    ) -> float:
        """Optuna objective function"""        trial_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Sample hyperparameters
            hyperparams = {}
            for param_name, param_config in config.hyperparameter_space.items():
                if param_config['type'] == 'uniform':
                    hyperparams[param_name] = trial.suggest_uniform(
                        param_name, param_config['low'], param_config['high']
                    )
                elif param_config['type'] == 'int':
                    hyperparams[param_name] = trial.suggest_int(
                        param_name, param_config['low'], param_config['high']
                    )
                elif param_config['type'] == 'categorical':
                    hyperparams[param_name] = trial.suggest_categorical(
                        param_name, param_config['choices']
                    )
            
            # Create and train model
            model = await self._create_model_with_hyperparams(
                config.model_configs[0], hyperparams
            )
            
            # Perform cross-validation
            cv_scores = cross_val_score(
                model, training_data, target_data,
                cv=StratifiedKFold(n_splits=config.cross_validation_folds, shuffle=True, random_state=config.random_seed),
                scoring='accuracy',
                n_jobs=-1
            )
            
            mean_score = np.mean(cv_scores)
            
            # Create result record
            result = ExperimentResult(
                trial_id=trial_id,
                experiment_id=config.experiment_id,
                model_config=config.model_configs[0],
                hyperparameters=hyperparams,
                metrics={'accuracy': mean_score, 'std': np.std(cv_scores)},
                training_time=time.time() - start_time,
                cross_val_scores=cv_scores.tolist()
            )
            
            results.append(result)
            
            # Log to MLflow
            with mlflow.start_run(nested=True):
                mlflow.log_params(hyperparams)
                mlflow.log_metric("accuracy", mean_score)
                mlflow.log_metric("accuracy_std", np.std(cv_scores))
                mlflow.log_metric("training_time", result.training_time)
            
            return mean_score
            
        except Exception as e:
            logger.error(f"Trial failed: {trial_id} - {str(e)}")
            result = ExperimentResult(
                trial_id=trial_id,
                experiment_id=config.experiment_id,
                model_config=config.model_configs[0],
                hyperparameters=hyperparams if 'hyperparams' in locals() else {},
                metrics={},
                training_time=time.time() - start_time,
                cross_val_scores=[],
                status="failed",
                error_message=str(e)
            )
            results.append(result)
            raise optuna.TrialPruned()
    
    async def _run_model_comparison(
        self, 
        config: ExperimentConfig,
        training_data: Any,
        target_data: Any
    ) -> List[ExperimentResult]:
        """Run model comparison experiment"""        results = []
        
        for model_config in config.model_configs:
            trial_id = str(uuid.uuid4())
            start_time = time.time()
            
            try:
                # Create model
                model = await self._create_model(model_config)
                
                # Perform cross-validation
                cv_scores = cross_val_score(
                    model, training_data, target_data,
                    cv=StratifiedKFold(n_splits=config.cross_validation_folds, shuffle=True, random_state=config.random_seed),
                    scoring='accuracy',
                    n_jobs=-1
                )
                
                mean_score = np.mean(cv_scores)
                
                # Create result record
                result = ExperimentResult(
                    trial_id=trial_id,
                    experiment_id=config.experiment_id,
                    model_config=model_config,
                    hyperparameters=model_config.get('parameters', {}),
                    metrics={'accuracy': mean_score, 'std': np.std(cv_scores)},
                    training_time=time.time() - start_time,
                    cross_val_scores=cv_scores.tolist()
                )
                
                results.append(result)
                
                # Log to MLflow
                with mlflow.start_run(nested=True):
                    mlflow.log_params(model_config.get('parameters', {}))
                    mlflow.log_metric("accuracy", mean_score)
                    mlflow.log_metric("accuracy_std", np.std(cv_scores))
                    mlflow.log_metric("training_time", result.training_time)
                    mlflow.set_tag("model_type", model_config['type'])
                
            except Exception as e:
                logger.error(f"Model comparison trial failed: {trial_id} - {str(e)}")
                result = ExperimentResult(
                    trial_id=trial_id,
                    experiment_id=config.experiment_id,
                    model_config=model_config,
                    hyperparameters=model_config.get('parameters', {}),
                    metrics={},
                    training_time=time.time() - start_time,
                    cross_val_scores=[],
                    status="failed",
                    error_message=str(e)
                )
                results.append(result)
        
        return results
    
    async def _run_feature_selection(
        self,
        config: ExperimentConfig,
        training_data: Any,
        target_data: Any
    ) -> List[ExperimentResult]:
        """Run feature selection experiment"""        from sklearn.feature_selection import SelectKBest, RFE, SelectFromModel
        from sklearn.ensemble import RandomForestClassifier
        
        results = []
        feature_selectors = [
            ('selectkbest', SelectKBest()),
            ('rfe', RFE(RandomForestClassifier())),
            ('selectfrommodel', SelectFromModel(RandomForestClassifier()))
        ]
        
        for selector_name, selector in feature_selectors:
            trial_id = str(uuid.uuid4())
            start_time = time.time()
            
            try:
                # Apply feature selection
                selected_features = selector.fit_transform(training_data, target_data)
                
                # Train model with selected features
                model = await self._create_model(config.model_configs[0])
                
                cv_scores = cross_val_score(
                    model, selected_features, target_data,
                    cv=StratifiedKFold(n_splits=config.cross_validation_folds, shuffle=True, random_state=config.random_seed),
                    scoring='accuracy',
                    n_jobs=-1
                )
                
                mean_score = np.mean(cv_scores)
                
                result = ExperimentResult(
                    trial_id=trial_id,
                    experiment_id=config.experiment_id,
                    model_config=config.model_configs[0],
                    hyperparameters={'feature_selector': selector_name},
                    metrics={'accuracy': mean_score, 'std': np.std(cv_scores), 'n_features': selected_features.shape[1]},
                    training_time=time.time() - start_time,
                    cross_val_scores=cv_scores.tolist()
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Feature selection trial failed: {trial_id} - {str(e)}")
        
        return results
    
    async def _create_model(self, model_config: Dict[str, Any]):
        """Create model instance from configuration"""        model_type = model_config['type']
        parameters = model_config.get('parameters', {})
        
        if model_type == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(**parameters)
        elif model_type == 'gradient_boosting':
            from sklearn.ensemble import GradientBoostingClassifier
            return GradientBoostingClassifier(**parameters)
        elif model_type == 'svm':
            from sklearn.svm import SVC
            return SVC(**parameters)
        elif model_type == 'logistic_regression':
            from sklearn.linear_model import LogisticRegression
            return LogisticRegression(**parameters)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    async def _create_model_with_hyperparams(self, model_config: Dict[str, Any], hyperparams: Dict[str, Any]):
        """Create model with specific hyperparameters"""        combined_params = {**model_config.get('parameters', {}), **hyperparams}
        model_config_with_params = {**model_config, 'parameters': combined_params}
        return await self._create_model(model_config_with_params)
    
    async def _generate_experiment_summary(
        self,
        experiment_id: str,
        results: List[ExperimentResult],
        execution_time: float
    ) -> ExperimentSummary:
        """Generate comprehensive experiment summary"""        if not results:
            raise ExperimentError("No results to summarize")
        
        completed_results = [r for r in results if r.status == "completed"]
        failed_results = [r for r in results if r.status == "failed"]
        
        if not completed_results:
            raise ExperimentError("No completed trials to summarize")
        
        # Find best result
        best_result = max(completed_results, key=lambda r: r.metrics.get('accuracy', 0))
        
        # Statistical significance analysis
        statistical_significance = await self._analyze_statistical_significance(completed_results)
        
        # Convergence analysis
        convergence_analysis = await self._analyze_convergence(completed_results)
        
        summary = ExperimentSummary(
            experiment_id=experiment_id,
            total_trials=len(results),
            completed_trials=len(completed_results),
            failed_trials=len(failed_results),
            best_trial_id=best_result.trial_id,
            best_score=best_result.metrics.get('accuracy', 0),
            best_hyperparameters=best_result.hyperparameters,
            execution_time=execution_time,
            statistical_significance=statistical_significance,
            convergence_analysis=convergence_analysis
        )
        
        return summary
    
    async def _analyze_statistical_significance(self, results: List[ExperimentResult]) -> Dict[str, float]:
        """Analyze statistical significance of results"""        if len(results) < 2:
            return {}
        
        scores = [r.metrics.get('accuracy', 0) for r in results]
        
        # Basic statistics
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        # Confidence interval
        n = len(scores)
        sem = std_score / np.sqrt(n)
        confidence_interval = stats.t.interval(0.95, n-1, loc=mean_score, scale=sem)
        
        return {
            'mean_score': mean_score,
            'std_score': std_score,
            'confidence_interval_lower': confidence_interval[0],
            'confidence_interval_upper': confidence_interval[1],
            'coefficient_of_variation': std_score / mean_score if mean_score != 0 else float('inf')
        }
    
    async def _analyze_convergence(self, results: List[ExperimentResult]) -> Dict[str, Any]:
        """Analyze experiment convergence"""        scores = [r.metrics.get('accuracy', 0) for r in results]
        
        if len(scores) < 5:
            return {'status': 'insufficient_data'}
        
        # Calculate moving average
        window_size = min(10, len(scores) // 2)
        moving_avg = pd.Series(scores).rolling(window=window_size).mean().tolist()
        
        # Check for convergence (stabilization of moving average)
        recent_scores = moving_avg[-5:]
        score_variance = np.var(recent_scores)
        
        converged = score_variance < 0.001  # Threshold for convergence
        
        return {
            'status': 'converged' if converged else 'not_converged',
            'score_variance': score_variance,
            'moving_average': moving_avg,
            'convergence_threshold': 0.001
        }
    
    async def _log_experiment_summary(self, summary: ExperimentSummary):
        """Log experiment summary to tracking backend"""        with mlflow.start_run():
            mlflow.log_metrics({
                'best_score': summary.best_score,
                'total_trials': summary.total_trials,
                'completed_trials': summary.completed_trials,
                'failed_trials': summary.failed_trials,
                'execution_time': summary.execution_time
            })
            
            mlflow.log_params(summary.best_hyperparameters)
            
            if summary.statistical_significance:
                mlflow.log_metrics(summary.statistical_significance)
    
    async def compare_experiments(self, experiment_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple experiments"""        if len(experiment_ids) < 2:
            raise ValueError("At least two experiments are required for comparison")
        
        comparison_data = {}
        
        for exp_id in experiment_ids:
            if exp_id not in self.results:
                raise ValueError(f"Experiment not found: {exp_id}")
            
            results = self.results[exp_id]
            completed_results = [r for r in results if r.status == "completed"]
            
            if not completed_results:
                continue
            
            best_result = max(completed_results, key=lambda r: r.metrics.get('accuracy', 0))
            scores = [r.metrics.get('accuracy', 0) for r in completed_results]
            
            comparison_data[exp_id] = {
                'experiment_name': self.experiments[exp_id].name,
                'best_score': best_result.metrics.get('accuracy', 0),
                'mean_score': np.mean(scores),
                'std_score': np.std(scores),
                'total_trials': len(results),
                'completed_trials': len(completed_results),
                'best_hyperparameters': best_result.hyperparameters
            }
        
        # Statistical comparison
        if len(comparison_data) >= 2:
            experiment_names = list(comparison_data.keys())
            scores_lists = []
            
            for exp_id in experiment_names:
                results = self.results[exp_id]
                completed_results = [r for r in results if r.status == "completed"]
                scores = [r.metrics.get('accuracy', 0) for r in completed_results]
                scores_lists.append(scores)
            
            # Perform statistical tests
            if len(scores_lists) == 2 and len(scores_lists[0]) > 0 and len(scores_lists[1]) > 0:
                t_stat, p_value = stats.ttest_ind(scores_lists[0], scores_lists[1])
                comparison_data['statistical_test'] = {
                    'test': 't_test',
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
        
        return comparison_data
    
    async def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get detailed experiment results"""        if experiment_id not in self.results:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        results = self.results[experiment_id]
        config = self.experiments[experiment_id]
        
        return {
            'experiment_id': experiment_id,
            'experiment_name': config.name,
            'experiment_type': config.experiment_type.value,
            'total_trials': len(results),
            'completed_trials': len([r for r in results if r.status == "completed"]),
            'failed_trials': len([r for r in results if r.status == "failed"]),
            'results': [asdict(r) for r in results]
        }
    
    async def export_experiment_report(self, experiment_id: str, format: str = 'json') -> str:
        """Export comprehensive experiment report"""        results_data = await self.get_experiment_results(experiment_id)
        
        if format == 'json':
            report_path = f"/tmp/experiment_report_{experiment_id}.json"
            with open(report_path, 'w') as f:
                json.dump(results_data, f, indent=2, default=str)
        
        elif format == 'html':
            report_path = f"/tmp/experiment_report_{experiment_id}.html"
            # Generate HTML report with visualizations
            await self._generate_html_report(results_data, report_path)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return report_path
    
    async def _generate_html_report(self, results_data: Dict[str, Any], output_path: str):
        """Generate HTML experiment report with visualizations"""        html_content = f"""        <!DOCTYPE html>
        <html>
        <head>
            <title>ML Experiment Report - {results_data['experiment_name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .metrics {{ margin: 20px 0; }}
                .metric-box {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
                .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .results-table th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ML Experiment Report</h1>
                <h2>{results_data['experiment_name']} ({results_data['experiment_id']})</h2>
                <p><strong>Type:</strong> {results_data['experiment_type']}</p>
                <p><strong>Generated:</strong> {datetime.now(timezone.utc).isoformat()}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-box">
                    <h3>Total Trials</h3>
                    <p>{results_data['total_trials']}</p>
                </div>
                <div class="metric-box">
                    <h3>Completed</h3>
                    <p>{results_data['completed_trials']}</p>
                </div>
                <div class="metric-box">
                    <h3>Failed</h3>
                    <p>{results_data['failed_trials']}</p>
                </div>
            </div>
            
            <h2>Results</h2>
            <table class="results-table">
                <tr>
                    <th>Trial ID</th>
                    <th>Status</th>
                    <th>Accuracy</th>
                    <th>Training Time</th>
                </tr>
        """        
        for result in results_data['results']:
            html_content += f"""                <tr>
                    <td>{result['trial_id'][:8]}...</td>
                    <td>{result['status']}</td>
                    <td>{result['metrics'].get('accuracy', 'N/A'):.4f}</td>
                    <td>{result['training_time']:.2f}s</td>
                </tr>
            """        
        html_content += """            </table>
        </body>
        </html>
        """        
        with open(output_path, 'w') as f:
            f.write(html_content)

# Global experiment tracker instance
experiment_tracker = MLExperimentTracker()

# Export all components
__all__ = [
    'MLExperimentTracker',
    'ExperimentConfig',
    'ExperimentResult',
    'ExperimentSummary',
    'ExperimentStatus',
    'ExperimentType',
    'MetricType',
    'experiment_tracker'
]
