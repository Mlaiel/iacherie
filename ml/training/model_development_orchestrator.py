"""🚀 Model Development Orchestrator - IA Influencer Agent Platform Enterprise
============================================================================
Module: backend/ml/training/model_development_orchestrator.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ORCHESTRATEUR DE DÉVELOPPEMENT DE MODÈLES
Gestion complète du cycle de vie de développement ML
- Orchestration automatisée train/validation/test
- Experiment tracking et version control intégré
- Pipeline A/B testing et validation croisée
- Integration avec MLflow et monitoring continu
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import hashlib
from pathlib import Path
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import shutil

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, KFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# Configuration
logger = logging.getLogger(__name__)

class DevelopmentPhase(Enum):
    """Phases de développement"""
    EXPLORATION = "exploration"
    PREPROCESSING = "preprocessing"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_SELECTION = "model_selection"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    TRAINING = "training"
    VALIDATION = "validation"
    TESTING = "testing"
    DEPLOYMENT_PREP = "deployment_prep"
    COMPLETED = "completed"

class ModelType(Enum):
    """Types de modèles"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    TIME_SERIES = "time_series"

class ExperimentStatus(Enum):
    """Statuts d'expérimentation"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ValidationStrategy(Enum):
    """Stratégies de validation"""
    TRAIN_TEST_SPLIT = "train_test_split"
    CROSS_VALIDATION = "cross_validation"
    STRATIFIED_CV = "stratified_cv"
    TIME_SERIES_CV = "time_series_cv"
    CUSTOM = "custom"

@dataclass
class ModelCandidate:
    """Candidat de modèle"""
    candidate_id: str
    name: str
    model_class: Union[str, type]
    hyperparameters: Dict[str, Any]
    estimated_training_time: float = 0.0
    priority: int = 1
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class ExperimentConfig:
    """Configuration d'expérimentation"""
    experiment_id: str
    name: str
    description: Optional[str] = None
    model_type: ModelType = ModelType.CLASSIFICATION
    validation_strategy: ValidationStrategy = ValidationStrategy.CROSS_VALIDATION
    test_size: float = 0.2
    cv_folds: int = 5
    random_state: int = 42
    max_training_time_hours: int = 24
    early_stopping_patience: int = 10
    enable_feature_selection: bool = True
    enable_hyperparameter_tuning: bool = True
    enable_model_comparison: bool = True
    target_metric: str = "accuracy"
    optimize_direction: str = "maximize"  # maximize or minimize

@dataclass
class TrainingRun:
    """Exécution d'entraînement"""
    run_id: str
    experiment_id: str
    candidate_id: str
    status: ExperimentStatus
    phase: DevelopmentPhase
    start_time: datetime
    end_time: Optional[datetime] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    model_path: Optional[str] = None
    error_message: Optional[str] = None
    mlflow_run_id: Optional[str] = None

@dataclass
class ModelEvaluation:
    """Évaluation de modèle"""
    evaluation_id: str
    run_id: str
    dataset_split: str  # train, validation, test
    metrics: Dict[str, float]
    confusion_matrix: Optional[np.ndarray] = None
    feature_importance: Optional[Dict[str, float]] = None
    predictions: Optional[np.ndarray] = None
    prediction_probabilities: Optional[np.ndarray] = None
    evaluation_time: datetime = field(default_factory=datetime.now)

class ModelDevelopmentOrchestrator:
    """Orchestrateur de développement de modèles enterprise"""
    
    def __init__(self,
                 max_concurrent_experiments: int = 5,
                 max_concurrent_runs: int = 10,
                 models_directory: str = "./models",
                 experiments_directory: str = "./experiments",
                 mlflow_tracking_uri: str = "sqlite:///mlflow.db"):
        
        self.max_concurrent_experiments = max_concurrent_experiments
        self.max_concurrent_runs = max_concurrent_runs
        self.models_directory = Path(models_directory)
        self.experiments_directory = Path(experiments_directory)
        self.mlflow_tracking_uri = mlflow_tracking_uri
        
        # Créer les répertoires
        self.models_directory.mkdir(exist_ok=True, parents=True)
        self.experiments_directory.mkdir(exist_ok=True, parents=True)
        
        # State management
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.model_candidates: Dict[str, List[ModelCandidate]] = defaultdict(list)
        self.training_runs: Dict[str, TrainingRun] = {}
        self.evaluations: Dict[str, List[ModelEvaluation]] = defaultdict(list)
        
        # Execution
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.running_experiments: Dict[str, asyncio.Task] = {}
        self.running_runs: Dict[str, asyncio.Task] = {}
        
        # MLflow integration
        self.mlflow_client = None
        self._initialize_mlflow()
        
        # Built-in models
        self.builtin_models = {
            "random_forest_classifier": RandomForestClassifier,
            "random_forest_regressor": RandomForestRegressor,
            "gradient_boosting_classifier": GradientBoostingClassifier,
            "logistic_regression": LogisticRegression,
            "linear_regression": LinearRegression,
            "svm_classifier": SVC,
            "svm_regressor": SVR
        }
        
        # Hyperparameter grids
        self.hyperparameter_grids = {
            "random_forest_classifier": {
                "n_estimators": [50, 100, 200],
                "max_depth": [10, 20, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4]
            },
            "gradient_boosting_classifier": {
                "n_estimators": [100, 200],
                "learning_rate": [0.01, 0.1, 0.2],
                "max_depth": [3, 5, 7]
            },
            "logistic_regression": {
                "C": [0.1, 1.0, 10.0],
                "penalty": ["l1", "l2"],
                "solver": ["liblinear", "saga"]
            }
        }
        
        # Metrics
        self.development_metrics = {
            "total_experiments": 0,
            "successful_experiments": 0,
            "failed_experiments": 0,
            "total_models_trained": 0,
            "best_model_accuracy": 0.0,
            "average_training_time": 0.0
        }
        
        # State management
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # Callbacks
        self.experiment_callbacks: List[Callable] = []
        self.run_callbacks: List[Callable] = []
        self.evaluation_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
    
    def _initialize_mlflow(self):
        """Initialise MLflow"""
        try:
            mlflow.set_tracking_uri(self.mlflow_tracking_uri)
            self.mlflow_client = MlflowClient()
            logger.info(f"MLflow initialisé: {self.mlflow_tracking_uri}")
        except Exception as e:
            logger.error(f"Erreur initialisation MLflow: {e}")
    
    async def start(self):
        """Démarre l'orchestrateur"""
        try:
            self.is_running = True
            logger.info("Démarrage orchestrateur de développement de modèles")
            
            # Démarrer les tâches de monitoring
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._cleanup_loop())
            
            logger.info("Orchestrateur démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage orchestrateur: {e}")
            raise
    
    async def stop(self):
        """Arrête l'orchestrateur"""
        try:
            logger.info("Arrêt orchestrateur de développement...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Arrêter les expérimentations en cours
            for exp_id, task in self.running_experiments.items():
                logger.info(f"Arrêt expérimentation {exp_id}")
                task.cancel()
            
            # Arrêter les runs en cours
            for run_id, task in self.running_runs.items():
                logger.info(f"Arrêt run {run_id}")
                task.cancel()
            
            # Fermer l'executor
            self.executor.shutdown(wait=True)
            
            logger.info("Orchestrateur arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt orchestrateur: {e}")
    
    async def create_experiment(self,
                               config: ExperimentConfig,
                               model_candidates: List[ModelCandidate]) -> bool:
        """Crée une nouvelle expérimentation"""
        try:
            if config.experiment_id in self.experiments:
                raise ValueError(f"Expérimentation {config.experiment_id} existe déjà")
            
            if len(self.running_experiments) >= self.max_concurrent_experiments:
                raise ValueError("Limite d'expérimentations concurrentes atteinte")
            
            # Valider les candidats
            for candidate in model_candidates:
                await self._validate_model_candidate(candidate)
            
            # Enregistrer l'expérimentation
            self.experiments[config.experiment_id] = config
            self.model_candidates[config.experiment_id] = model_candidates
            
            # Créer l'expérience MLflow
            try:
                mlflow_exp = mlflow.create_experiment(
                    name=f"{config.name}_{config.experiment_id}",
                    artifact_location=str(self.experiments_directory / config.experiment_id)
                )
                logger.info(f"Expérience MLflow créée: {mlflow_exp}")
            except Exception as e:
                logger.warning(f"Erreur création expérience MLflow: {e}")
            
            logger.info(f"Expérimentation {config.experiment_id} créée avec {len(model_candidates)} candidats")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création expérimentation {config.experiment_id}: {e}")
            return False
    
    async def _validate_model_candidate(self, candidate: ModelCandidate):
        """Valide un candidat de modèle"""
        if isinstance(candidate.model_class, str):
            if candidate.model_class not in self.builtin_models:
                raise ValueError(f"Modèle inconnu: {candidate.model_class}")
        elif not (isinstance(candidate.model_class, type) and 
                 issubclass(candidate.model_class, BaseEstimator)):
            raise ValueError(f"Classe de modèle invalide: {candidate.model_class}")
    
    async def start_experiment(self,
                              experiment_id: str,
                              X_train: np.ndarray,
                              y_train: np.ndarray,
                              X_test: Optional[np.ndarray] = None,
                              y_test: Optional[np.ndarray] = None) -> bool:
        """Démarre une expérimentation"""
        
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Expérimentation {experiment_id} n'existe pas")
            
            if experiment_id in self.running_experiments:
                raise ValueError(f"Expérimentation {experiment_id} déjà en cours")
            
            # Créer la tâche d'expérimentation
            task = asyncio.create_task(
                self._run_experiment(experiment_id, X_train, y_train, X_test, y_test)
            )
            self.running_experiments[experiment_id] = task
            
            logger.info(f"Expérimentation {experiment_id} démarrée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage expérimentation {experiment_id}: {e}")
            return False
    
    async def _run_experiment(self,
                             experiment_id: str,
                             X_train: np.ndarray,
                             y_train: np.ndarray,
                             X_test: Optional[np.ndarray] = None,
                             y_test: Optional[np.ndarray] = None):
        """Exécute une expérimentation complète"""
        
        config = self.experiments[experiment_id]
        candidates = self.model_candidates[experiment_id]
        
        try:
            logger.info(f"Début expérimentation {experiment_id}")
            self.development_metrics["total_experiments"] += 1
            
            # Préparer les données
            if X_test is None or y_test is None:
                X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(
                    X_train, y_train, 
                    test_size=config.test_size,
                    random_state=config.random_state,
                    stratify=y_train if config.model_type == ModelType.CLASSIFICATION else None
                )
            else:
                X_train_split, y_train_split = X_train, y_train
                X_test_split, y_test_split = X_test, y_test
            
            # Trier les candidats par priorité
            sorted_candidates = sorted(candidates, key=lambda x: x.priority, reverse=True)
            
            # Entraîner tous les candidats
            training_tasks = []
            for candidate in sorted_candidates:
                if len(self.running_runs) < self.max_concurrent_runs:
                    task = asyncio.create_task(
                        self._train_model_candidate(
                            experiment_id, candidate, 
                            X_train_split, y_train_split,
                            X_test_split, y_test_split
                        )
                    )
                    training_tasks.append(task)
                else:
                    # Attendre qu'une place se libère
                    await asyncio.sleep(1)
            
            # Attendre tous les entraînements
            completed_runs = []
            for task in training_tasks:
                try:
                    run_result = await task
                    completed_runs.append(run_result)
                except Exception as e:
                    logger.error(f"Erreur entraînement candidat: {e}")
            
            # Analyser les résultats
            await self._analyze_experiment_results(experiment_id, completed_runs)
            
            # Sélectionner le meilleur modèle
            best_run = await self._select_best_model(experiment_id)
            
            if best_run:
                logger.info(f"Meilleur modèle pour {experiment_id}: {best_run.candidate_id} "
                           f"(métrique: {best_run.metrics.get(config.target_metric, 'N/A')})")
                
                # Sauvegarder le meilleur modèle
                await self._save_best_model(experiment_id, best_run)
            
            self.development_metrics["successful_experiments"] += 1
            
            # Appeler les callbacks
            for callback in self.experiment_callbacks:
                try:
                    await callback(experiment_id, completed_runs, best_run)
                except Exception as e:
                    logger.error(f"Erreur callback expérimentation: {e}")
            
        except Exception as e:
            logger.error(f"Erreur expérimentation {experiment_id}: {e}")
            self.development_metrics["failed_experiments"] += 1
            
            # Appeler les callbacks d'erreur
            for callback in self.error_callbacks:
                try:
                    await callback(e, experiment_id)
                except Exception as cb_error:
                    logger.error(f"Erreur callback erreur: {cb_error}")
            raise
        
        finally:
            # Nettoyer
            if experiment_id in self.running_experiments:
                del self.running_experiments[experiment_id]
    
    async def _train_model_candidate(self,
                                   experiment_id: str,
                                   candidate: ModelCandidate,
                                   X_train: np.ndarray,
                                   y_train: np.ndarray,
                                   X_test: np.ndarray,
                                   y_test: np.ndarray) -> TrainingRun:
        """Entraîne un candidat de modèle"""
        
        config = self.experiments[experiment_id]
        run_id = f"{experiment_id}_{candidate.candidate_id}_{int(time.time())}"
        
        # Créer le run
        training_run = TrainingRun(
            run_id=run_id,
            experiment_id=experiment_id,
            candidate_id=candidate.candidate_id,
            status=ExperimentStatus.RUNNING,
            phase=DevelopmentPhase.TRAINING,
            start_time=datetime.now(),
            parameters=candidate.hyperparameters.copy()
        )
        
        self.training_runs[run_id] = training_run
        
        try:
            # Démarrer un run MLflow
            with mlflow.start_run(run_name=f"{candidate.name}_{run_id}") as mlflow_run:
                training_run.mlflow_run_id = mlflow_run.info.run_id
                
                # Log des paramètres
                mlflow.log_params(candidate.hyperparameters)
                mlflow.log_param("model_type", candidate.model_class)
                mlflow.log_param("experiment_id", experiment_id)
                
                start_time = time.time()
                
                # Créer le modèle
                model = self._create_model_instance(candidate)
                
                # Entraînement
                training_run.phase = DevelopmentPhase.TRAINING
                model.fit(X_train, y_train)
                
                training_time = time.time() - start_time
                
                # Validation
                training_run.phase = DevelopmentPhase.VALIDATION
                metrics = await self._evaluate_model(
                    model, X_train, y_train, X_test, y_test, config
                )
                
                training_run.metrics = metrics
                training_run.status = ExperimentStatus.COMPLETED
                training_run.end_time = datetime.now()
                
                # Sauvegarder le modèle
                model_path = self.models_directory / experiment_id / f"{run_id}_model.pkl"
                model_path.parent.mkdir(exist_ok=True, parents=True)
                
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                
                training_run.model_path = str(model_path)
                
                # Log des métriques dans MLflow
                for metric_name, metric_value in metrics.items():
                    mlflow.log_metric(metric_name, metric_value)
                
                mlflow.log_metric("training_time_seconds", training_time)
                
                # Log du modèle
                mlflow.sklearn.log_model(model, "model")
                
                # Mettre à jour les métriques globales
                self.development_metrics["total_models_trained"] += 1
                
                total_time = self.development_metrics["average_training_time"]
                total_models = self.development_metrics["total_models_trained"]
                self.development_metrics["average_training_time"] = (
                    (total_time * (total_models - 1) + training_time) / total_models
                )
                
                # Mettre à jour la meilleure accuracy
                if config.target_metric in metrics:
                    metric_value = metrics[config.target_metric]
                    if metric_value > self.development_metrics["best_model_accuracy"]:
                        self.development_metrics["best_model_accuracy"] = metric_value
                
                logger.info(f"Modèle {candidate.candidate_id} entraîné avec succès "
                           f"(temps: {training_time:.2f}s, "
                           f"métrique: {metrics.get(config.target_metric, 'N/A')})")
                
                # Appeler les callbacks
                for callback in self.run_callbacks:
                    try:
                        await callback(training_run)
                    except Exception as e:
                        logger.error(f"Erreur callback run: {e}")
                
                return training_run
        
        except Exception as e:
            logger.error(f"Erreur entraînement candidat {candidate.candidate_id}: {e}")
            
            training_run.status = ExperimentStatus.FAILED
            training_run.end_time = datetime.now()
            training_run.error_message = str(e)
            
            raise
    
    def _create_model_instance(self, candidate: ModelCandidate):
        """Crée une instance de modèle"""
        if isinstance(candidate.model_class, str):
            model_class = self.builtin_models[candidate.model_class]
        else:
            model_class = candidate.model_class
        
        return model_class(**candidate.hyperparameters)
    
    async def _evaluate_model(self,
                             model,
                             X_train: np.ndarray,
                             y_train: np.ndarray,
                             X_test: np.ndarray,
                             y_test: np.ndarray,
                             config: ExperimentConfig) -> Dict[str, float]:
        """Évalue un modèle"""
        
        metrics = {}
        
        try:
            # Prédictions sur les ensembles d'entraînement et de test
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            if config.model_type == ModelType.CLASSIFICATION:
                # Métriques de classification
                metrics.update({
                    "train_accuracy": accuracy_score(y_train, y_train_pred),
                    "test_accuracy": accuracy_score(y_test, y_test_pred),
                    "train_precision": precision_score(y_train, y_train_pred, average='weighted'),
                    "test_precision": precision_score(y_test, y_test_pred, average='weighted'),
                    "train_recall": recall_score(y_train, y_train_pred, average='weighted'),
                    "test_recall": recall_score(y_test, y_test_pred, average='weighted'),
                    "train_f1": f1_score(y_train, y_train_pred, average='weighted'),
                    "test_f1": f1_score(y_test, y_test_pred, average='weighted')
                })
                
                # Métrique principale
                if config.target_metric == "accuracy":
                    metrics["accuracy"] = metrics["test_accuracy"]
                elif config.target_metric == "f1":
                    metrics["f1"] = metrics["test_f1"]
                elif config.target_metric == "precision":
                    metrics["precision"] = metrics["test_precision"]
                elif config.target_metric == "recall":
                    metrics["recall"] = metrics["test_recall"]
            
            elif config.model_type == ModelType.REGRESSION:
                # Métriques de régression
                metrics.update({
                    "train_mse": mean_squared_error(y_train, y_train_pred),
                    "test_mse": mean_squared_error(y_test, y_test_pred),
                    "train_rmse": np.sqrt(mean_squared_error(y_train, y_train_pred)),
                    "test_rmse": np.sqrt(mean_squared_error(y_test, y_test_pred)),
                    "train_r2": r2_score(y_train, y_train_pred),
                    "test_r2": r2_score(y_test, y_test_pred)
                })
                
                # Métrique principale
                if config.target_metric == "mse":
                    metrics["mse"] = metrics["test_mse"]
                elif config.target_metric == "rmse":
                    metrics["rmse"] = metrics["test_rmse"]
                elif config.target_metric == "r2":
                    metrics["r2"] = metrics["test_r2"]
            
            # Cross-validation si activée
            if config.validation_strategy in [ValidationStrategy.CROSS_VALIDATION, ValidationStrategy.STRATIFIED_CV]:
                cv_scores = await self._perform_cross_validation(model, X_train, y_train, config)
                metrics.update({
                    "cv_mean": np.mean(cv_scores),
                    "cv_std": np.std(cv_scores),
                    "cv_scores": cv_scores.tolist()
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur évaluation modèle: {e}")
            return {"error": 1.0}
    
    async def _perform_cross_validation(self,
                                       model,
                                       X: np.ndarray,
                                       y: np.ndarray,
                                       config: ExperimentConfig) -> np.ndarray:
        """Effectue la validation croisée"""
        
        if config.validation_strategy == ValidationStrategy.STRATIFIED_CV:
            cv = StratifiedKFold(n_splits=config.cv_folds, shuffle=True, random_state=config.random_state)
        else:
            cv = KFold(n_splits=config.cv_folds, shuffle=True, random_state=config.random_state)
        
        scoring = config.target_metric
        if config.model_type == ModelType.CLASSIFICATION and scoring == "accuracy":
            scoring = "accuracy"
        elif config.model_type == ModelType.REGRESSION and scoring == "mse":
            scoring = "neg_mean_squared_error"
        
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
        
        # Inverser les scores négatifs si nécessaire
        if scoring.startswith("neg_"):
            cv_scores = -cv_scores
        
        return cv_scores
    
    async def _analyze_experiment_results(self, experiment_id: str, completed_runs: List[TrainingRun]):
        """Analyse les résultats d'une expérimentation"""
        
        config = self.experiments[experiment_id]
        
        if not completed_runs:
            logger.warning(f"Aucun run complété pour l'expérimentation {experiment_id}")
            return
        
        # Statistiques des résultats
        target_metric = config.target_metric
        metric_values = [
            run.metrics.get(target_metric, 0.0) 
            for run in completed_runs 
            if run.status == ExperimentStatus.COMPLETED
        ]
        
        if metric_values:
            stats = {
                "mean": np.mean(metric_values),
                "std": np.std(metric_values),
                "min": np.min(metric_values),
                "max": np.max(metric_values),
                "median": np.median(metric_values)
            }
            
            logger.info(f"Statistiques expérimentation {experiment_id}:")
            logger.info(f"- Métrique {target_metric}: {stats}")
            logger.info(f"- Runs complétés: {len(metric_values)}/{len(completed_runs)}")
    
    async def _select_best_model(self, experiment_id: str) -> Optional[TrainingRun]:
        """Sélectionne le meilleur modèle d'une expérimentation"""
        
        config = self.experiments[experiment_id]
        
        # Récupérer tous les runs complétés
        completed_runs = [
            run for run in self.training_runs.values()
            if (run.experiment_id == experiment_id and 
                run.status == ExperimentStatus.COMPLETED and
                config.target_metric in run.metrics)
        ]
        
        if not completed_runs:
            return None
        
        # Trier selon la métrique cible
        if config.optimize_direction == "maximize":
            best_run = max(completed_runs, key=lambda x: x.metrics[config.target_metric])
        else:
            best_run = min(completed_runs, key=lambda x: x.metrics[config.target_metric])
        
        return best_run
    
    async def _save_best_model(self, experiment_id: str, best_run: TrainingRun):
        """Sauvegarde le meilleur modèle"""
        try:
            if not best_run.model_path or not Path(best_run.model_path).exists():
                logger.error(f"Modèle non trouvé pour le run {best_run.run_id}")
                return
            
            # Copier le modèle vers le répertoire des meilleurs modèles
            best_model_dir = self.models_directory / experiment_id / "best_model"
            best_model_dir.mkdir(exist_ok=True, parents=True)
            
            best_model_path = best_model_dir / "model.pkl"
            shutil.copy2(best_run.model_path, best_model_path)
            
            # Sauvegarder les métadonnées
            metadata = {
                "experiment_id": experiment_id,
                "run_id": best_run.run_id,
                "candidate_id": best_run.candidate_id,
                "metrics": best_run.metrics,
                "parameters": best_run.parameters,
                "selection_time": datetime.now().isoformat(),
                "mlflow_run_id": best_run.mlflow_run_id
            }
            
            with open(best_model_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Meilleur modèle sauvegardé: {best_model_path}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde meilleur modèle: {e}")
    
    # Hyperparameter tuning automatique
    
    async def generate_hyperparameter_candidates(self,
                                               base_model: str,
                                               n_candidates: int = 10) -> List[ModelCandidate]:
        """Génère des candidats avec hyperparamètres optimisés"""
        
        candidates = []
        
        if base_model not in self.hyperparameter_grids:
            logger.warning(f"Pas de grille d'hyperparamètres pour {base_model}")
            return candidates
        
        param_grid = self.hyperparameter_grids[base_model]
        
        # Génération aléatoire de combinaisons
        import itertools
        import random
        
        # Générer toutes les combinaisons possibles
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        all_combinations = list(itertools.product(*param_values))
        
        # Sélectionner un échantillon aléatoire
        selected_combinations = random.sample(
            all_combinations, 
            min(n_candidates, len(all_combinations))
        )
        
        for i, combination in enumerate(selected_combinations):
            hyperparams = dict(zip(param_names, combination))
            
            candidate = ModelCandidate(
                candidate_id=f"{base_model}_candidate_{i}",
                name=f"{base_model} Variant {i+1}",
                model_class=base_model,
                hyperparameters=hyperparams,
                priority=1
            )
            
            candidates.append(candidate)
        
        return candidates
    
    # Boucles de maintenance
    
    async def _monitoring_loop(self):
        """Boucle de monitoring"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Toutes les minutes
                
                # Log des métriques
                logger.info(
                    f"Development metrics - "
                    f"Experiments: {self.development_metrics['total_experiments']}, "
                    f"Success rate: {(self.development_metrics['successful_experiments'] / max(self.development_metrics['total_experiments'], 1)):.2%}, "
                    f"Models trained: {self.development_metrics['total_models_trained']}, "
                    f"Best accuracy: {self.development_metrics['best_model_accuracy']:.4f}, "
                    f"Avg training time: {self.development_metrics['average_training_time']:.2f}s"
                )
                
                # Monitoring des runs en cours
                active_runs = len(self.running_runs)
                active_experiments = len(self.running_experiments)
                
                logger.info(f"Active - Experiments: {active_experiments}, Runs: {active_runs}")
                
            except Exception as e:
                logger.error(f"Erreur boucle monitoring: {e}")
    
    async def _cleanup_loop(self):
        """Boucle de nettoyage"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Toutes les heures
                
                # Nettoyer les anciens runs
                cutoff_time = datetime.now() - timedelta(days=7)
                
                runs_to_remove = []
                for run_id, run in self.training_runs.items():
                    if run.end_time and run.end_time < cutoff_time:
                        runs_to_remove.append(run_id)
                
                for run_id in runs_to_remove:
                    # Supprimer le fichier modèle si existe
                    run = self.training_runs[run_id]
                    if run.model_path and Path(run.model_path).exists():
                        try:
                            Path(run.model_path).unlink()
                        except Exception as e:
                            logger.error(f"Erreur suppression modèle {run.model_path}: {e}")
                    
                    del self.training_runs[run_id]
                
                logger.debug(f"Nettoyage: {len(runs_to_remove)} anciens runs supprimés")
                
            except Exception as e:
                logger.error(f"Erreur boucle nettoyage: {e}")
    
    # API publique
    
    def get_experiment_runs(self, experiment_id: str) -> List[TrainingRun]:
        """Récupère tous les runs d'une expérimentation"""
        return [
            run for run in self.training_runs.values()
            if run.experiment_id == experiment_id
        ]
    
    def get_training_run(self, run_id: str) -> Optional[TrainingRun]:
        """Récupère un run d'entraînement"""
        return self.training_runs.get(run_id)
    
    def get_best_model_path(self, experiment_id: str) -> Optional[str]:
        """Récupère le chemin du meilleur modèle"""
        best_model_path = self.models_directory / experiment_id / "best_model" / "model.pkl"
        return str(best_model_path) if best_model_path.exists() else None
    
    def list_experiments(self) -> List[str]:
        """Liste les expérimentations"""
        return list(self.experiments.keys())
    
    def get_development_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de développement"""
        return self.development_metrics.copy()
    
    def add_experiment_callback(self, callback: Callable):
        """Ajoute un callback d'expérimentation"""
        self.experiment_callbacks.append(callback)
    
    def add_run_callback(self, callback: Callable):
        """Ajoute un callback de run"""
        self.run_callbacks.append(callback)
    
    def add_evaluation_callback(self, callback: Callable):
        """Ajoute un callback d'évaluation"""
        self.evaluation_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable):
        """Ajoute un callback d'erreur"""
        self.error_callbacks.append(callback)
    
    async def cancel_experiment(self, experiment_id: str) -> bool:
        """Annule une expérimentation"""
        try:
            if experiment_id in self.running_experiments:
                task = self.running_experiments[experiment_id]
                task.cancel()
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur annulation expérimentation {experiment_id}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "registered_experiments": len(self.experiments),
            "running_experiments": len(self.running_experiments),
            "running_runs": len(self.running_runs),
            "total_training_runs": len(self.training_runs),
            "development_metrics": self.development_metrics,
            "mlflow_connected": self.mlflow_client is not None
        }


# Factory pour créer des orchestrateurs spécialisés
class DevelopmentOrchestratorFactory:
    """Factory pour créer des orchestrateurs spécialisés"""
    
    @staticmethod
    def create_production_orchestrator() -> ModelDevelopmentOrchestrator:
        """Orchestrateur pour production"""
        return ModelDevelopmentOrchestrator(
            max_concurrent_experiments=10,
            max_concurrent_runs=20,
            models_directory="./production_models",
            experiments_directory="./production_experiments"
        )
    
    @staticmethod
    def create_development_orchestrator() -> ModelDevelopmentOrchestrator:
        """Orchestrateur pour développement"""
        return ModelDevelopmentOrchestrator(
            max_concurrent_experiments=3,
            max_concurrent_runs=5,
            models_directory="./dev_models",
            experiments_directory="./dev_experiments"
        )


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation de l'orchestrateur"""
    
    from sklearn.datasets import make_classification, make_regression
    import numpy as np
    
    # Créer des données d'exemple
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
    
    # Créer l'orchestrateur
    orchestrator = DevelopmentOrchestratorFactory.create_development_orchestrator()
    
    try:
        await orchestrator.start()
        
        # Configuration d'expérimentation
        config = ExperimentConfig(
            experiment_id="classification_experiment",
            name="Classification Experiment",
            description="Expérimentation de classification binaire",
            model_type=ModelType.CLASSIFICATION,
            validation_strategy=ValidationStrategy.CROSS_VALIDATION,
            cv_folds=5,
            target_metric="accuracy",
            optimize_direction="maximize"
        )
        
        # Créer des candidats de modèles
        candidates = [
            ModelCandidate(
                candidate_id="rf_default",
                name="Random Forest Default",
                model_class="random_forest_classifier",
                hyperparameters={"n_estimators": 100, "random_state": 42},
                priority=1
            ),
            ModelCandidate(
                candidate_id="rf_optimized",
                name="Random Forest Optimized",
                model_class="random_forest_classifier",
                hyperparameters={
                    "n_estimators": 200,
                    "max_depth": 15,
                    "min_samples_split": 5,
                    "random_state": 42
                },
                priority=2
            ),
            ModelCandidate(
                candidate_id="logistic",
                name="Logistic Regression",
                model_class="logistic_regression",
                hyperparameters={"C": 1.0, "random_state": 42},
                priority=1
            )
        ]
        
        # Générer des candidats automatiques
        auto_candidates = await orchestrator.generate_hyperparameter_candidates(
            "random_forest_classifier", 
            n_candidates=3
        )
        candidates.extend(auto_candidates)
        
        # Créer l'expérimentation
        success = await orchestrator.create_experiment(config, candidates)
        if not success:
            print("Erreur création expérimentation")
            return
        
        print(f"Expérimentation créée avec {len(candidates)} candidats")
        
        # Callbacks
        async def experiment_callback(exp_id, runs, best_run):
            print(f"Expérimentation {exp_id} terminée")
            if best_run:
                print(f"Meilleur modèle: {best_run.candidate_id}")
                print(f"Accuracy: {best_run.metrics.get('accuracy', 'N/A')}")
        
        async def run_callback(run):
            print(f"Run {run.candidate_id} terminé - "
                  f"Accuracy: {run.metrics.get('accuracy', 'N/A')}")
        
        orchestrator.add_experiment_callback(experiment_callback)
        orchestrator.add_run_callback(run_callback)
        
        # Démarrer l'expérimentation
        success = await orchestrator.start_experiment(
            "classification_experiment",
            X, y
        )
        
        if not success:
            print("Erreur démarrage expérimentation")
            return
        
        print("Expérimentation démarrée...")
        
        # Attendre la completion
        while "classification_experiment" in orchestrator.running_experiments:
            await asyncio.sleep(2)
            
            # Afficher les runs en cours
            runs = orchestrator.get_experiment_runs("classification_experiment")
            completed = len([r for r in runs if r.status == ExperimentStatus.COMPLETED])
            total = len(runs)
            
            if total > 0:
                print(f"Progrès: {completed}/{total} runs complétés")
        
        # Afficher les résultats finaux
        final_runs = orchestrator.get_experiment_runs("classification_experiment")
        print(f"\nRésultats finaux:")
        for run in final_runs:
            if run.status == ExperimentStatus.COMPLETED:
                print(f"- {run.candidate_id}: {run.metrics.get('accuracy', 'N/A'):.4f}")
        
        # Meilleur modèle
        best_model_path = orchestrator.get_best_model_path("classification_experiment")
        if best_model_path:
            print(f"\nMeilleur modèle sauvegardé: {best_model_path}")
        
        # Métriques de développement
        dev_metrics = orchestrator.get_development_metrics()
        print(f"\nMétriques de développement: {dev_metrics}")
        
        # Santé du système
        health = await orchestrator.health_check()
        print(f"\nSanté système: {health}")
        
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())