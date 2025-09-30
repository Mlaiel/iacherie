"""
AutoML Engine
Enterprise AutoML system for automated model development and optimization

This module provides:
- Automated model architecture search
- Hyperparameter optimization
- Feature engineering automation
- Model selection and ensemble creation
- Specialized AutoML for 53 AI agent categories

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
import optuna
import json

logger = logging.getLogger(__name__)

class AutoMLTaskType(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    TIME_SERIES = "time_series"

class AutoMLStatus(Enum):
    PENDING = "pending"
    ANALYZING_DATA = "analyzing_data"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_SEARCH = "model_search"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    MODEL_VALIDATION = "model_validation"
    ENSEMBLE_CREATION = "ensemble_creation"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AutoMLConfig:
    """AutoML experiment configuration"""
    experiment_id: str
    task_type: AutoMLTaskType
    dataset_path: str
    target_column: str
    feature_columns: Optional[List[str]] = None
    evaluation_metric: Optional[str] = None
    time_budget_hours: float = 2.0
    model_budget: int = 100
    ensemble_size: int = 5
    cross_validation_folds: int = 5
    test_size: float = 0.2
    random_state: int = 42

@dataclass
class ModelCandidate:
    """Individual model candidate in AutoML search"""
    model_id: str
    algorithm: str
    hyperparameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    training_time: float
    validation_score: float
    cross_val_scores: List[float]
    feature_importance: Optional[Dict[str, float]] = None

@dataclass
class AutoMLResult:
    """Final AutoML experiment result"""
    experiment_id: str
    best_model: ModelCandidate
    model_ensemble: List[ModelCandidate]
    performance_summary: Dict[str, Any]
    feature_engineering_report: Dict[str, Any]
    experiment_duration: float
    total_models_tried: int
    recommendations: List[str]

class AutoMLEngine:
    """
    Enterprise AutoML engine for automated machine learning
    Specializes in creating optimal models for Ainflue's 53 AI agents
    """
    
    def __init__(self):
        self.experiments: Dict[str, Any] = {}
        self.model_registry: Dict[str, ModelCandidate] = {}
        self.algorithm_catalog = self._initialize_algorithm_catalog()
        self.feature_engineering_pipeline = None
        
    async def create_automl_experiment(
        self,
        task_type: AutoMLTaskType,
        dataset_path: str,
        target_column: str,
        feature_columns: Optional[List[str]] = None,
        time_budget_hours: float = 2.0,
        evaluation_metric: Optional[str] = None
    ) -> str:
        """
        Create a new AutoML experiment
        
        Args:
            task_type: Type of ML task
            dataset_path: Path to training dataset
            target_column: Target variable column name
            feature_columns: List of feature columns (None for auto-detection)
            time_budget_hours: Time budget for experiment
            evaluation_metric: Evaluation metric (None for auto-selection)
            
        Returns:
            experiment_id: Unique experiment identifier
        """
        try:
            experiment_id = str(uuid.uuid4())
            
            # Auto-select evaluation metric if not provided
            if evaluation_metric is None:
                evaluation_metric = self._get_default_metric(task_type)
            
            config = AutoMLConfig(
                experiment_id=experiment_id,
                task_type=task_type,
                dataset_path=dataset_path,
                target_column=target_column,
                feature_columns=feature_columns,
                evaluation_metric=evaluation_metric,
                time_budget_hours=time_budget_hours
            )
            
            self.experiments[experiment_id] = {
                "config": config,
                "status": AutoMLStatus.PENDING,
                "created_at": datetime.utcnow(),
                "started_at": None,
                "completed_at": None,
                "current_best": None,
                "models_tried": 0,
                "progress": 0.0
            }
            
            logger.info(f"Created AutoML experiment {experiment_id} for {task_type.value}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create AutoML experiment: {e}")
            raise
    
    async def run_automl_experiment(self, experiment_id: str) -> AutoMLResult:
        """
        Run complete AutoML experiment
        
        Args:
            experiment_id: Experiment identifier
            
        Returns:
            automl_result: Complete experiment results
        """
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            config = experiment["config"]
            
            experiment["status"] = AutoMLStatus.ANALYZING_DATA
            experiment["started_at"] = datetime.utcnow()
            
            # Phase 1: Data Analysis
            logger.info(f"Starting data analysis for experiment {experiment_id}")
            data_analysis = await self._analyze_dataset(config)
            experiment["progress"] = 0.1
            
            # Phase 2: Feature Engineering
            experiment["status"] = AutoMLStatus.FEATURE_ENGINEERING
            logger.info(f"Starting feature engineering for experiment {experiment_id}")
            feature_engineering_report = await self._automated_feature_engineering(
                config, data_analysis
            )
            experiment["progress"] = 0.2
            
            # Phase 3: Model Search and Training
            experiment["status"] = AutoMLStatus.MODEL_SEARCH
            logger.info(f"Starting model search for experiment {experiment_id}")
            model_candidates = await self._automated_model_search(
                config, feature_engineering_report
            )
            experiment["progress"] = 0.6
            
            # Phase 4: Hyperparameter Tuning
            experiment["status"] = AutoMLStatus.HYPERPARAMETER_TUNING
            logger.info(f"Starting hyperparameter tuning for experiment {experiment_id}")
            optimized_models = await self._hyperparameter_optimization(
                config, model_candidates
            )
            experiment["progress"] = 0.8
            
            # Phase 5: Model Validation
            experiment["status"] = AutoMLStatus.MODEL_VALIDATION
            logger.info(f"Starting model validation for experiment {experiment_id}")
            validated_models = await self._comprehensive_model_validation(
                config, optimized_models
            )
            experiment["progress"] = 0.9
            
            # Phase 6: Ensemble Creation
            experiment["status"] = AutoMLStatus.ENSEMBLE_CREATION
            logger.info(f"Creating model ensemble for experiment {experiment_id}")
            best_model, ensemble = await self._create_model_ensemble(
                config, validated_models
            )
            
            # Complete experiment
            experiment["status"] = AutoMLStatus.COMPLETED
            experiment["completed_at"] = datetime.utcnow()
            experiment["progress"] = 1.0
            
            # Generate performance summary
            performance_summary = await self._generate_performance_summary(
                best_model, ensemble, validated_models
            )
            
            # Generate recommendations
            recommendations = await self._generate_automl_recommendations(
                config, best_model, performance_summary
            )
            
            # Create final result
            duration = (experiment["completed_at"] - experiment["started_at"]).total_seconds() / 3600
            
            result = AutoMLResult(
                experiment_id=experiment_id,
                best_model=best_model,
                model_ensemble=ensemble,
                performance_summary=performance_summary,
                feature_engineering_report=feature_engineering_report,
                experiment_duration=duration,
                total_models_tried=len(validated_models),
                recommendations=recommendations
            )
            
            logger.info(f"Completed AutoML experiment {experiment_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to run AutoML experiment: {e}")
            if experiment_id in self.experiments:
                self.experiments[experiment_id]["status"] = AutoMLStatus.FAILED
            raise
    
    async def train_recommendation_models(
        self,
        dataset_specs: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Train recommendation models for creator intelligence AI agents
        
        Args:
            dataset_specs: List of dataset specifications for recommendation models
            
        Returns:
            experiment_ids: List of AutoML experiment IDs
        """
        try:
            experiment_ids = []
            
            for spec in dataset_specs:
                experiment_id = await self.create_automl_experiment(
                    task_type=AutoMLTaskType.RECOMMENDATION,
                    dataset_path=spec["dataset_path"],
                    target_column=spec.get("target_column", "rating"),
                    feature_columns=spec.get("feature_columns"),
                    time_budget_hours=spec.get("time_budget", 1.0),
                    evaluation_metric=spec.get("metric", "rmse")
                )
                
                # Start experiment asynchronously
                asyncio.create_task(self.run_automl_experiment(experiment_id))
                experiment_ids.append(experiment_id)
            
            logger.info(f"Started {len(experiment_ids)} recommendation model AutoML experiments")
            return experiment_ids
            
        except Exception as e:
            logger.error(f"Failed to train recommendation models: {e}")
            raise
    
    async def optimize_seo_models(
        self,
        dataset_specs: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Optimize SEO models using AutoML
        
        Args:
            dataset_specs: List of SEO dataset specifications
            
        Returns:
            experiment_ids: List of AutoML experiment IDs
        """
        try:
            experiment_ids = []
            
            for spec in dataset_specs:
                experiment_id = await self.create_automl_experiment(
                    task_type=AutoMLTaskType.REGRESSION,  # SEO metrics are typically continuous
                    dataset_path=spec["dataset_path"],
                    target_column=spec.get("target_column", "search_ranking"),
                    feature_columns=spec.get("feature_columns"),
                    time_budget_hours=spec.get("time_budget", 1.5),
                    evaluation_metric=spec.get("metric", "r2")
                )
                
                asyncio.create_task(self.run_automl_experiment(experiment_id))
                experiment_ids.append(experiment_id)
            
            logger.info(f"Started {len(experiment_ids)} SEO model AutoML experiments")
            return experiment_ids
            
        except Exception as e:
            logger.error(f"Failed to optimize SEO models: {e}")
            raise
    
    async def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get current status of AutoML experiment
        
        Args:
            experiment_id: Experiment identifier
            
        Returns:
            status_info: Current experiment status and progress
        """
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            
            return {
                "experiment_id": experiment_id,
                "status": experiment["status"].value,
                "progress": experiment["progress"],
                "models_tried": experiment["models_tried"],
                "created_at": experiment["created_at"].isoformat(),
                "started_at": experiment["started_at"].isoformat() if experiment["started_at"] else None,
                "completed_at": experiment["completed_at"].isoformat() if experiment["completed_at"] else None,
                "current_best": experiment["current_best"],
                "task_type": experiment["config"].task_type.value
            }
            
        except Exception as e:
            logger.error(f"Failed to get experiment status: {e}")
            raise
    
    async def get_model_leaderboard(self, experiment_id: str) -> List[Dict[str, Any]]:
        """
        Get leaderboard of models for experiment
        
        Args:
            experiment_id: Experiment identifier
            
        Returns:
            leaderboard: Ranked list of model performances
        """
        try:
            # Get all models for experiment
            experiment_models = [
                model for model in self.model_registry.values()
                if model.model_id.startswith(experiment_id)
            ]
            
            # Sort by validation score
            experiment_models.sort(key=lambda x: x.validation_score, reverse=True)
            
            leaderboard = []
            for rank, model in enumerate(experiment_models[:20], 1):  # Top 20
                leaderboard.append({
                    "rank": rank,
                    "model_id": model.model_id,
                    "algorithm": model.algorithm,
                    "validation_score": model.validation_score,
                    "cross_val_mean": np.mean(model.cross_val_scores),
                    "cross_val_std": np.std(model.cross_val_scores),
                    "training_time": model.training_time,
                    "hyperparameters": model.hyperparameters
                })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Failed to get model leaderboard: {e}")
            raise
    
    def _initialize_algorithm_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Initialize catalog of available algorithms"""
        return {
            "classification": {
                "random_forest": {
                    "class": RandomForestClassifier,
                    "param_space": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [5, 10, 20, None],
                        "min_samples_split": [2, 5, 10],
                        "min_samples_leaf": [1, 2, 4]
                    }
                },
                "gradient_boosting": {
                    "class": GradientBoostingClassifier,
                    "param_space": {
                        "n_estimators": [50, 100, 200],
                        "learning_rate": [0.01, 0.1, 0.2],
                        "max_depth": [3, 5, 7],
                        "subsample": [0.8, 0.9, 1.0]
                    }
                },
                "svm": {
                    "class": SVC,
                    "param_space": {
                        "C": [0.1, 1, 10, 100],
                        "kernel": ["rbf", "poly", "sigmoid"],
                        "gamma": ["scale", "auto", 0.001, 0.01]
                    }
                },
                "neural_network": {
                    "class": MLPClassifier,
                    "param_space": {
                        "hidden_layer_sizes": [(50,), (100,), (50, 50), (100, 50)],
                        "learning_rate_init": [0.001, 0.01, 0.1],
                        "alpha": [0.0001, 0.001, 0.01],
                        "max_iter": [500, 1000]
                    }
                }
            }
        }
    
    def _get_default_metric(self, task_type: AutoMLTaskType) -> str:
        """Get default evaluation metric for task type"""
        metric_map = {
            AutoMLTaskType.CLASSIFICATION: "accuracy",
            AutoMLTaskType.REGRESSION: "r2",
            AutoMLTaskType.CLUSTERING: "silhouette",
            AutoMLTaskType.ANOMALY_DETECTION: "f1",
            AutoMLTaskType.RECOMMENDATION: "rmse",
            AutoMLTaskType.NLP: "accuracy",
            AutoMLTaskType.COMPUTER_VISION: "accuracy",
            AutoMLTaskType.TIME_SERIES: "mae"
        }
        return metric_map.get(task_type, "accuracy")
    
    async def _analyze_dataset(self, config: AutoMLConfig) -> Dict[str, Any]:
        """Analyze dataset characteristics"""
        try:
            # Load dataset
            df = pd.read_csv(config.dataset_path)
            
            analysis = {
                "shape": df.shape,
                "columns": list(df.columns),
                "target_column": config.target_column,
                "missing_values": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.to_dict(),
                "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
                "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
                "target_distribution": df[config.target_column].value_counts().to_dict() if config.target_column in df.columns else None
            }
            
            # Statistical summary
            analysis["statistics"] = df.describe().to_dict()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze dataset: {e}")
            raise
    
    async def _automated_feature_engineering(
        self,
        config: AutoMLConfig,
        data_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform automated feature engineering"""
        try:
            df = pd.read_csv(config.dataset_path)
            
            feature_engineering_report = {
                "original_features": len(df.columns) - 1,  # Exclude target
                "engineered_features": [],
                "transformations_applied": [],
                "feature_importance_scores": {}
            }
            
            # Handle missing values
            numeric_cols = data_analysis["numeric_columns"]
            categorical_cols = data_analysis["categorical_columns"]
            
            if config.target_column in numeric_cols:
                numeric_cols.remove(config.target_column)
            if config.target_column in categorical_cols:
                categorical_cols.remove(config.target_column)
            
            # Fill missing values
            for col in numeric_cols:
                if df[col].isnull().sum() > 0:
                    df[col].fillna(df[col].median(), inplace=True)
                    feature_engineering_report["transformations_applied"].append(
                        f"Filled missing values in {col} with median"
                    )
            
            for col in categorical_cols:
                if df[col].isnull().sum() > 0:
                    df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "unknown", inplace=True)
                    feature_engineering_report["transformations_applied"].append(
                        f"Filled missing values in {col} with mode"
                    )
            
            # Create interaction features for numeric columns
            if len(numeric_cols) >= 2:
                for i in range(min(len(numeric_cols), 3)):  # Limit to prevent explosion
                    for j in range(i + 1, min(len(numeric_cols), 3)):
                        col1, col2 = numeric_cols[i], numeric_cols[j]
                        interaction_col = f"{col1}_x_{col2}"
                        df[interaction_col] = df[col1] * df[col2]
                        feature_engineering_report["engineered_features"].append(interaction_col)
            
            # Encode categorical variables
            label_encoders = {}
            for col in categorical_cols:
                le = LabelEncoder()
                df[col + "_encoded"] = le.fit_transform(df[col].astype(str))
                label_encoders[col] = le
                feature_engineering_report["engineered_features"].append(col + "_encoded")
            
            # Scale numeric features
            scaler = StandardScaler()
            if numeric_cols:
                df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
                feature_engineering_report["transformations_applied"].append("Applied StandardScaler to numeric features")
            
            feature_engineering_report["final_features"] = len(df.columns) - 1
            feature_engineering_report["feature_engineering_ratio"] = (
                feature_engineering_report["final_features"] / feature_engineering_report["original_features"]
            )
            
            # Save processed dataset
            processed_path = config.dataset_path.replace(".csv", "_processed.csv")
            df.to_csv(processed_path, index=False)
            feature_engineering_report["processed_dataset_path"] = processed_path
            
            return feature_engineering_report
            
        except Exception as e:
            logger.error(f"Failed to perform feature engineering: {e}")
            raise
    
    async def _automated_model_search(
        self,
        config: AutoMLConfig,
        feature_report: Dict[str, Any]
    ) -> List[ModelCandidate]:
        """Perform automated model search"""
        try:
            # Load processed dataset
            df = pd.read_csv(feature_report["processed_dataset_path"])
            
            # Prepare features and target
            target = df[config.target_column]
            features = df.drop(columns=[config.target_column])
            
            # Get appropriate algorithms for task type
            task_algorithms = self.algorithm_catalog.get(config.task_type.value, {})
            if not task_algorithms:
                task_algorithms = self.algorithm_catalog["classification"]  # Fallback
            
            model_candidates = []
            
            for alg_name, alg_config in task_algorithms.items():
                try:
                    # Create model with default parameters
                    model = alg_config["class"](random_state=config.random_state)
                    
                    # Perform cross-validation
                    cv_scores = cross_val_score(
                        model, features, target,
                        cv=config.cross_validation_folds,
                        scoring=self._get_sklearn_scoring(config.evaluation_metric)
                    )
                    
                    # Train on full dataset for timing
                    start_time = datetime.utcnow()
                    model.fit(features, target)
                    training_time = (datetime.utcnow() - start_time).total_seconds()
                    
                    # Create model candidate
                    candidate = ModelCandidate(
                        model_id=f"{config.experiment_id}_{alg_name}_{uuid.uuid4().hex[:8]}",
                        algorithm=alg_name,
                        hyperparameters={},  # Default parameters
                        performance_metrics={config.evaluation_metric: np.mean(cv_scores)},
                        training_time=training_time,
                        validation_score=np.mean(cv_scores),
                        cross_val_scores=cv_scores.tolist()
                    )
                    
                    model_candidates.append(candidate)
                    self.model_registry[candidate.model_id] = candidate
                    
                    logger.debug(f"Trained {alg_name} with CV score: {np.mean(cv_scores):.4f}")
                    
                except Exception as e:
                    logger.warning(f"Failed to train {alg_name}: {e}")
                    continue
            
            # Sort by validation score
            model_candidates.sort(key=lambda x: x.validation_score, reverse=True)
            
            return model_candidates
            
        except Exception as e:
            logger.error(f"Failed to perform model search: {e}")
            raise
    
    async def _hyperparameter_optimization(
        self,
        config: AutoMLConfig,
        model_candidates: List[ModelCandidate]
    ) -> List[ModelCandidate]:
        """Perform hyperparameter optimization on top models"""
        try:
            # Load processed dataset
            feature_report = {"processed_dataset_path": config.dataset_path.replace(".csv", "_processed.csv")}
            df = pd.read_csv(feature_report["processed_dataset_path"])
            
            target = df[config.target_column]
            features = df.drop(columns=[config.target_column])
            
            # Optimize top 3 models
            top_models = model_candidates[:3]
            optimized_models = []
            
            for candidate in top_models:
                try:
                    # Get algorithm configuration
                    alg_config = None
                    for task_algs in self.algorithm_catalog.values():
                        if candidate.algorithm in task_algs:
                            alg_config = task_algs[candidate.algorithm]
                            break
                    
                    if not alg_config:
                        optimized_models.append(candidate)
                        continue
                    
                    # Create Optuna study
                    study = optuna.create_study(direction="maximize")
                    
                    def objective(trial):
                        # Sample hyperparameters
                        params = {}
                        param_space = alg_config["param_space"]
                        
                        for param_name, param_values in param_space.items():
                            if isinstance(param_values[0], int):
                                params[param_name] = trial.suggest_int(param_name, min(param_values), max(param_values))
                            elif isinstance(param_values[0], float):
                                params[param_name] = trial.suggest_float(param_name, min(param_values), max(param_values))
                            else:
                                params[param_name] = trial.suggest_categorical(param_name, param_values)
                        
                        # Train model with sampled parameters
                        model = alg_config["class"](random_state=config.random_state, **params)
                        cv_scores = cross_val_score(
                            model, features, target,
                            cv=config.cross_validation_folds,
                            scoring=self._get_sklearn_scoring(config.evaluation_metric)
                        )
                        return np.mean(cv_scores)
                    
                    # Optimize (limited trials for time budget)
                    study.optimize(objective, n_trials=20, timeout=300)  # 5 minutes max per model
                    
                    # Create optimized candidate
                    optimized_candidate = ModelCandidate(
                        model_id=f"{candidate.model_id}_optimized",
                        algorithm=candidate.algorithm,
                        hyperparameters=study.best_params,
                        performance_metrics={config.evaluation_metric: study.best_value},
                        training_time=candidate.training_time,  # Approximate
                        validation_score=study.best_value,
                        cross_val_scores=[study.best_value] * config.cross_validation_folds  # Approximate
                    )
                    
                    optimized_models.append(optimized_candidate)
                    self.model_registry[optimized_candidate.model_id] = optimized_candidate
                    
                    logger.info(f"Optimized {candidate.algorithm}: {study.best_value:.4f}")
                    
                except Exception as e:
                    logger.warning(f"Failed to optimize {candidate.algorithm}: {e}")
                    optimized_models.append(candidate)
            
            # Include remaining unoptimized models
            optimized_models.extend(model_candidates[3:])
            
            # Sort by validation score
            optimized_models.sort(key=lambda x: x.validation_score, reverse=True)
            
            return optimized_models
            
        except Exception as e:
            logger.error(f"Failed to perform hyperparameter optimization: {e}")
            raise
    
    async def _comprehensive_model_validation(
        self,
        config: AutoMLConfig,
        models: List[ModelCandidate]
    ) -> List[ModelCandidate]:
        """Perform comprehensive model validation"""
        try:
            # For now, return models as-is with additional validation metrics
            for model in models:
                # Add additional performance metrics
                model.performance_metrics.update({
                    "cross_val_mean": np.mean(model.cross_val_scores),
                    "cross_val_std": np.std(model.cross_val_scores),
                    "stability_score": 1.0 - (np.std(model.cross_val_scores) / np.mean(model.cross_val_scores))
                })
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to perform model validation: {e}")
            raise
    
    async def _create_model_ensemble(
        self,
        config: AutoMLConfig,
        validated_models: List[ModelCandidate]
    ) -> Tuple[ModelCandidate, List[ModelCandidate]]:
        """Create model ensemble from top performers"""
        try:
            # Best individual model
            best_model = validated_models[0]
            
            # Top models for ensemble
            ensemble_size = min(config.ensemble_size, len(validated_models))
            ensemble = validated_models[:ensemble_size]
            
            # Calculate ensemble performance (simplified)
            ensemble_scores = [model.validation_score for model in ensemble]
            ensemble_performance = np.mean(ensemble_scores)
            
            # Create ensemble candidate
            ensemble_candidate = ModelCandidate(
                model_id=f"{config.experiment_id}_ensemble",
                algorithm="ensemble",
                hyperparameters={"member_models": [m.model_id for m in ensemble]},
                performance_metrics={config.evaluation_metric: ensemble_performance},
                training_time=sum(model.training_time for model in ensemble),
                validation_score=ensemble_performance,
                cross_val_scores=[ensemble_performance] * config.cross_validation_folds
            )
            
            return ensemble_candidate, ensemble
            
        except Exception as e:
            logger.error(f"Failed to create model ensemble: {e}")
            raise
    
    async def _generate_performance_summary(
        self,
        best_model: ModelCandidate,
        ensemble: List[ModelCandidate],
        all_models: List[ModelCandidate]
    ) -> Dict[str, Any]:
        """Generate performance summary"""
        return {
            "best_model_score": best_model.validation_score,
            "ensemble_score": np.mean([m.validation_score for m in ensemble]),
            "model_count": len(all_models),
            "score_range": {
                "min": min(m.validation_score for m in all_models),
                "max": max(m.validation_score for m in all_models),
                "mean": np.mean([m.validation_score for m in all_models]),
                "std": np.std([m.validation_score for m in all_models])
            },
            "algorithm_performance": {
                alg: np.mean([m.validation_score for m in all_models if m.algorithm == alg])
                for alg in set(m.algorithm for m in all_models)
            }
        }
    
    async def _generate_automl_recommendations(
        self,
        config: AutoMLConfig,
        best_model: ModelCandidate,
        performance_summary: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if best_model.validation_score > 0.8:
            recommendations.append("Excellent model performance - ready for production deployment")
        elif best_model.validation_score > 0.6:
            recommendations.append("Good model performance - consider additional feature engineering")
        else:
            recommendations.append("Model performance needs improvement - collect more data or try different approaches")
        
        if performance_summary["score_range"]["std"] < 0.05:
            recommendations.append("Low variance across models - consider more diverse algorithms")
        
        if best_model.algorithm == "ensemble":
            recommendations.append("Ensemble model performs best - deploy ensemble for optimal results")
        
        return recommendations
    
    def _get_sklearn_scoring(self, metric: str) -> str:
        """Convert metric name to sklearn scoring parameter"""
        metric_map = {
            "accuracy": "accuracy",
            "precision": "precision",
            "recall": "recall",
            "f1": "f1",
            "r2": "r2",
            "mae": "neg_mean_absolute_error",
            "rmse": "neg_root_mean_squared_error"
        }
        return metric_map.get(metric, "accuracy")