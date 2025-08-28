"""
🚀 Hyperparameter Tuning - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/training/hyperparameter_tuning.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 HYPERPARAMETER TUNING AVANCÉ
Optimisation automatique des hyperparamètres
- Bayesian Optimization avec Optuna
- Multi-objective optimization
- Early stopping et pruning intelligent
- Parallel trials et distributed tuning
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from pathlib import Path

import optuna
from optuna.samplers import TPESampler, CmaEsSampler
from optuna.pruners import MedianPruner, HyperbandPruner
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Configuration
logger = logging.getLogger(__name__)

class OptimizationDirection(Enum):
    """Direction d'optimisation"""
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"

class SamplerType(Enum):
    """Types de samplers Optuna"""
    TPE = "tpe"
    CMAES = "cmaes"
    RANDOM = "random"
    GRID = "grid"

class PrunerType(Enum):
    """Types de pruners Optuna"""
    MEDIAN = "median"
    HYPERBAND = "hyperband"
    NONE = "none"

@dataclass
class HyperparameterSpace:
    """Espace de recherche des hyperparamètres"""
    name: str
    param_type: str  # 'categorical', 'int', 'float', 'loguniform'
    choices: Optional[List[Any]] = None
    low: Optional[float] = None
    high: Optional[float] = None
    step: Optional[float] = None
    log: bool = False

@dataclass
class OptimizationConfig:
    """Configuration d'optimisation"""
    n_trials: int = 100
    timeout: Optional[int] = None
    direction: OptimizationDirection = OptimizationDirection.MAXIMIZE
    sampler_type: SamplerType = SamplerType.TPE
    pruner_type: PrunerType = PrunerType.MEDIAN
    cv_folds: int = 5
    n_jobs: int = 1
    random_state: int = 42
    study_name: Optional[str] = None
    storage_url: Optional[str] = None

@dataclass
class OptimizationResult:
    """Résultat d'optimisation"""
    study_name: str
    best_value: float
    best_params: Dict[str, Any]
    n_trials: int
    duration: float
    best_trial: Any
    trials_df: pd.DataFrame

class HyperparameterTuner:
    """Tuner d'hyperparamètres avancé"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.studies: Dict[str, optuna.Study] = {}
        self.optimization_history: List[OptimizationResult] = []
        
        # Configuration Optuna
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    
    def create_study(self, 
                    study_name: Optional[str] = None,
                    load_if_exists: bool = True) -> optuna.Study:
        """Crée ou charge une étude Optuna"""
        
        if study_name is None:
            study_name = f"study_{uuid.uuid4().hex[:8]}"
        
        # Sampler configuration
        sampler = self._create_sampler()
        
        # Pruner configuration
        pruner = self._create_pruner()
        
        # Créer l'étude
        study = optuna.create_study(
            study_name=study_name,
            direction=self.config.direction.value,
            sampler=sampler,
            pruner=pruner,
            storage=self.config.storage_url,
            load_if_exists=load_if_exists
        )
        
        self.studies[study_name] = study
        logger.info(f"Étude créée: {study_name}")
        
        return study
    
    def _create_sampler(self) -> optuna.samplers.BaseSampler:
        """Crée un sampler selon la configuration"""
        if self.config.sampler_type == SamplerType.TPE:
            return TPESampler(
                n_startup_trials=10,
                n_ei_candidates=24,
                seed=self.config.random_state
            )
        elif self.config.sampler_type == SamplerType.CMAES:
            return CmaEsSampler(seed=self.config.random_state)
        else:  # Random
            return optuna.samplers.RandomSampler(seed=self.config.random_state)
    
    def _create_pruner(self) -> optuna.pruners.BasePruner:
        """Crée un pruner selon la configuration"""
        if self.config.pruner_type == PrunerType.MEDIAN:
            return MedianPruner(
                n_startup_trials=5,
                n_warmup_steps=30,
                interval_steps=1
            )
        elif self.config.pruner_type == PrunerType.HYPERBAND:
            return HyperbandPruner(
                min_resource=1,
                max_resource=self.config.cv_folds,
                reduction_factor=3
            )
        else:  # None
            return optuna.pruners.NopPruner()
    
    async def optimize_model(self,
                           model_class: Any,
                           param_space: List[HyperparameterSpace],
                           X: np.ndarray,
                           y: np.ndarray,
                           scoring: str = 'accuracy',
                           study_name: Optional[str] = None) -> OptimizationResult:
        """Optimise les hyperparamètres d'un modèle"""
        
        start_time = time.time()
        
        # Créer l'étude
        study = self.create_study(study_name)
        
        # Fonction objective
        def objective(trial):
            return self._objective_function(
                trial, model_class, param_space, X, y, scoring
            )
        
        # Optimisation
        try:
            study.optimize(
                objective,
                n_trials=self.config.n_trials,
                timeout=self.config.timeout,
                n_jobs=self.config.n_jobs,
                catch=(Exception,)
            )
            
            duration = time.time() - start_time
            
            # Créer le résultat
            result = OptimizationResult(
                study_name=study.study_name,
                best_value=study.best_value,
                best_params=study.best_params,
                n_trials=len(study.trials),
                duration=duration,
                best_trial=study.best_trial,
                trials_df=study.trials_dataframe()
            )
            
            self.optimization_history.append(result)
            
            logger.info(f"Optimisation terminée: {study.study_name}")
            logger.info(f"Meilleur score: {study.best_value:.4f}")
            logger.info(f"Meilleurs paramètres: {study.best_params}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation: {e}")
            raise
    
    def _objective_function(self,
                          trial: optuna.Trial,
                          model_class: Any,
                          param_space: List[HyperparameterSpace],
                          X: np.ndarray,
                          y: np.ndarray,
                          scoring: str) -> float:
        """Fonction objective pour l'optimisation"""
        
        try:
            # Suggérer les hyperparamètres
            params = {}
            for param in param_space:
                if param.param_type == 'categorical':
                    params[param.name] = trial.suggest_categorical(
                        param.name, param.choices
                    )
                elif param.param_type == 'int':
                    params[param.name] = trial.suggest_int(
                        param.name, int(param.low), int(param.high), 
                        step=param.step
                    )
                elif param.param_type == 'float':
                    if param.log:
                        params[param.name] = trial.suggest_float(
                            param.name, param.low, param.high, log=True
                        )
                    else:
                        params[param.name] = trial.suggest_float(
                            param.name, param.low, param.high, step=param.step
                        )
                elif param.param_type == 'loguniform':
                    params[param.name] = trial.suggest_loguniform(
                        param.name, param.low, param.high
                    )
            
            # Créer le modèle avec les paramètres suggérés
            model = model_class(**params)
            
            # Cross-validation avec pruning
            cv_scores = []
            kf = StratifiedKFold(n_splits=self.config.cv_folds, shuffle=True, 
                               random_state=self.config.random_state)
            
            for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                
                # Entraîner le modèle
                model.fit(X_train, y_train)
                
                # Prédictions
                y_pred = model.predict(X_val)
                
                # Calculer le score
                if scoring == 'accuracy':
                    score = accuracy_score(y_val, y_pred)
                elif scoring == 'precision':
                    score = precision_score(y_val, y_pred, average='weighted')
                elif scoring == 'recall':
                    score = recall_score(y_val, y_pred, average='weighted')
                elif scoring == 'f1':
                    score = f1_score(y_val, y_pred, average='weighted')
                else:
                    score = accuracy_score(y_val, y_pred)
                
                cv_scores.append(score)
                
                # Rapport intermédiaire pour le pruning
                trial.report(np.mean(cv_scores), fold)
                
                # Vérifier si le trial doit être arrêté
                if trial.should_prune():
                    raise optuna.exceptions.TrialPruned()
            
            return np.mean(cv_scores)
            
        except optuna.exceptions.TrialPruned:
            raise
        except Exception as e:
            logger.warning(f"Erreur dans l'objective function: {e}")
            return 0.0
    
    def get_study(self, study_name: str) -> Optional[optuna.Study]:
        """Récupère une étude par nom"""
        return self.studies.get(study_name)
    
    def plot_optimization_history(self, study_name: str) -> Any:
        """Trace l'historique d'optimisation"""
        study = self.studies.get(study_name)
        if study:
            try:
                return optuna.visualization.plot_optimization_history(study)
            except Exception as e:
                logger.error(f"Erreur lors du plot: {e}")
                return None
        return None
    
    def plot_param_importances(self, study_name: str) -> Any:
        """Trace l'importance des paramètres"""
        study = self.studies.get(study_name)
        if study:
            try:
                return optuna.visualization.plot_param_importances(study)
            except Exception as e:
                logger.error(f"Erreur lors du plot: {e}")
                return None
        return None
    
    def get_best_params_by_metric(self, 
                                study_name: str, 
                                metric: str = 'value') -> Dict[str, Any]:
        """Récupère les meilleurs paramètres selon une métrique"""
        study = self.studies.get(study_name)
        if study:
            return study.best_params
        return {}
    
    def export_study_results(self, study_name: str, filepath: str):
        """Exporte les résultats d'une étude"""
        study = self.studies.get(study_name)
        if study:
            try:
                df = study.trials_dataframe()
                df.to_csv(filepath, index=False)
                logger.info(f"Résultats exportés vers: {filepath}")
            except Exception as e:
                logger.error(f"Erreur lors de l'export: {e}")
    
    async def multi_objective_optimization(self,
                                         model_class: Any,
                                         param_space: List[HyperparameterSpace],
                                         X: np.ndarray,
                                         y: np.ndarray,
                                         objectives: List[str],
                                         study_name: Optional[str] = None) -> OptimizationResult:
        """Optimisation multi-objectifs"""
        
        start_time = time.time()
        
        # Créer l'étude multi-objectifs
        if study_name is None:
            study_name = f"multi_obj_{uuid.uuid4().hex[:8]}"
        
        study = optuna.create_study(
            study_name=study_name,
            directions=['maximize'] * len(objectives),
            sampler=self._create_sampler(),
            storage=self.config.storage_url,
            load_if_exists=True
        )
        
        # Fonction objective multi-objectifs
        def multi_objective(trial):
            return self._multi_objective_function(
                trial, model_class, param_space, X, y, objectives
            )
        
        # Optimisation
        try:
            study.optimize(
                multi_objective,
                n_trials=self.config.n_trials,
                timeout=self.config.timeout,
                n_jobs=self.config.n_jobs
            )
            
            duration = time.time() - start_time
            
            # Récupérer le meilleur trial (Pareto front)
            best_trial = None
            best_value = 0.0
            
            if study.trials:
                # Utiliser le premier point du front de Pareto
                best_trial = study.best_trials[0] if study.best_trials else study.trials[0]
                best_value = np.mean(best_trial.values) if best_trial.values else 0.0
            
            result = OptimizationResult(
                study_name=study.study_name,
                best_value=best_value,
                best_params=best_trial.params if best_trial else {},
                n_trials=len(study.trials),
                duration=duration,
                best_trial=best_trial,
                trials_df=study.trials_dataframe() if study.trials else pd.DataFrame()
            )
            
            self.studies[study_name] = study
            self.optimization_history.append(result)
            
            logger.info(f"Optimisation multi-objectifs terminée: {study_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation multi-objectifs: {e}")
            raise
    
    def _multi_objective_function(self,
                                trial: optuna.Trial,
                                model_class: Any,
                                param_space: List[HyperparameterSpace],
                                X: np.ndarray,
                                y: np.ndarray,
                                objectives: List[str]) -> List[float]:
        """Fonction objective multi-objectifs"""
        
        try:
            # Suggérer les hyperparamètres
            params = {}
            for param in param_space:
                if param.param_type == 'categorical':
                    params[param.name] = trial.suggest_categorical(
                        param.name, param.choices
                    )
                elif param.param_type == 'int':
                    params[param.name] = trial.suggest_int(
                        param.name, int(param.low), int(param.high)
                    )
                elif param.param_type == 'float':
                    params[param.name] = trial.suggest_float(
                        param.name, param.low, param.high
                    )
            
            # Créer et entraîner le modèle
            model = model_class(**params)
            
            # Cross-validation
            kf = StratifiedKFold(n_splits=self.config.cv_folds, shuffle=True,
                               random_state=self.config.random_state)
            
            objective_scores = {obj: [] for obj in objectives}
            
            for train_idx, val_idx in kf.split(X, y):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
                
                # Calculer chaque objectif
                for obj in objectives:
                    if obj == 'accuracy':
                        score = accuracy_score(y_val, y_pred)
                    elif obj == 'precision':
                        score = precision_score(y_val, y_pred, average='weighted')
                    elif obj == 'recall':
                        score = recall_score(y_val, y_pred, average='weighted')
                    elif obj == 'f1':
                        score = f1_score(y_val, y_pred, average='weighted')
                    else:
                        score = accuracy_score(y_val, y_pred)
                    
                    objective_scores[obj].append(score)
            
            # Moyennes des scores pour chaque objectif
            return [np.mean(objective_scores[obj]) for obj in objectives]
            
        except Exception as e:
            logger.warning(f"Erreur dans la fonction multi-objectifs: {e}")
            return [0.0] * len(objectives)


# Classes helper pour définir les espaces de paramètres communs
class CommonParameterSpaces:
    """Espaces de paramètres communs pour différents modèles"""
    
    @staticmethod
    def random_forest_space() -> List[HyperparameterSpace]:
        """Espace de paramètres pour Random Forest"""
        return [
            HyperparameterSpace("n_estimators", "int", low=50, high=500),
            HyperparameterSpace("max_depth", "int", low=3, high=20),
            HyperparameterSpace("min_samples_split", "int", low=2, high=20),
            HyperparameterSpace("min_samples_leaf", "int", low=1, high=10),
            HyperparameterSpace("max_features", "categorical", 
                              choices=["sqrt", "log2", None])
        ]
    
    @staticmethod
    def gradient_boosting_space() -> List[HyperparameterSpace]:
        """Espace de paramètres pour Gradient Boosting"""
        return [
            HyperparameterSpace("n_estimators", "int", low=50, high=300),
            HyperparameterSpace("learning_rate", "float", low=0.01, high=0.3),
            HyperparameterSpace("max_depth", "int", low=3, high=10),
            HyperparameterSpace("subsample", "float", low=0.6, high=1.0),
            HyperparameterSpace("min_samples_split", "int", low=2, high=20)
        ]
    
    @staticmethod
    def svm_space() -> List[HyperparameterSpace]:
        """Espace de paramètres pour SVM"""
        return [
            HyperparameterSpace("C", "loguniform", low=0.1, high=100),
            HyperparameterSpace("kernel", "categorical", 
                              choices=["rbf", "linear", "poly"]),
            HyperparameterSpace("gamma", "categorical", 
                              choices=["scale", "auto"]),
            HyperparameterSpace("degree", "int", low=2, high=5)
        ]


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation du tuner"""
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    
    # Créer des données d'exemple
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, 
                             random_state=42)
    
    # Configuration
    config = OptimizationConfig(
        n_trials=50,
        direction=OptimizationDirection.MAXIMIZE,
        sampler_type=SamplerType.TPE,
        pruner_type=PrunerType.MEDIAN,
        cv_folds=5
    )
    
    # Créer le tuner
    tuner = HyperparameterTuner(config)
    
    # Espace de paramètres
    param_space = CommonParameterSpaces.random_forest_space()
    
    # Optimisation
    result = await tuner.optimize_model(
        RandomForestClassifier,
        param_space,
        X, y,
        scoring='f1',
        study_name='rf_optimization'
    )
    
    print(f"Meilleur score: {result.best_value:.4f}")
    print(f"Meilleurs paramètres: {result.best_params}")
    print(f"Nombre d'essais: {result.n_trials}")
    print(f"Durée: {result.duration:.2f}s")


if __name__ == "__main__":
    asyncio.run(example_usage())