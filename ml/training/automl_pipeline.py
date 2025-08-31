"""
 AutoML Pipeline - IA Influencer Agent Platform Enterprise
===========================================================
Module: backend/ml/training/automl_pipeline.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

 PIPELINE AUTOML ENTERPRISE
Pipeline automatisé d'entraînement de modèles ML
- Hyperparameter tuning automatique
- Architecture search et optimization
- Cross-validation et validation robuste
- Model comparison et selection automatique
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline

# Configuration
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Types de modèles supportés"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    CONTENT_PROTECTION = "content_protection"
    SEO_OPTIMIZATION = "seo_optimization"

class TrainingStatus(Enum):
    """Statuts d'entraînement"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AutoMLConfig:
    """Configuration AutoML"""
    model_type: ModelType
    max_trials: int = 100
    max_time_minutes: int = 60
    cv_folds: int = 5
    test_size: float = 0.2
    random_state: int = 42
    scoring_metric: str = "accuracy"
    enable_feature_selection: bool = True
    enable_ensemble: bool = True
    enable_neural_networks: bool = False

@dataclass
class TrainingMetrics:
    """Métriques d'entraînement"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_time: float
    cross_val_scores: List[float]
    feature_importance: Dict[str, float]
    hyperparameters: Dict[str, Any]

@dataclass
class TrainingJob:
    """Job d'entraînement"""
    job_id: str
    model_type: ModelType
    status: TrainingStatus
    config: AutoMLConfig
    start_time: datetime
    end_time: Optional[datetime] = None
    metrics: Optional[TrainingMetrics] = None
    error_message: Optional[str] = None
    model_path: Optional[str] = None

class AutoMLPipeline:
    """Pipeline AutoML Enterprise"""
    
    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.model_cache: Dict[str, Any] = {}
        
        # Modèles de base pour chaque type
        self.base_models = {
            ModelType.CLASSIFICATION: {
                'random_forest': RandomForestClassifier(random_state=config.random_state),
                'gradient_boosting': GradientBoostingClassifier(random_state=config.random_state),
                'logistic_regression': LogisticRegression(random_state=config.random_state),
                'svm': SVC(random_state=config.random_state)
            },
            ModelType.CONTENT_PROTECTION: {
                'random_forest': RandomForestClassifier(random_state=config.random_state),
                'gradient_boosting': GradientBoostingClassifier(random_state=config.random_state)
            }
        }
        
        # Hyperparameters grids
        self.param_grids = {
            'random_forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, 30, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'gradient_boosting': {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            'logistic_regression': {
                'C': [0.1, 1.0, 10.0],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            },
            'svm': {
                'C': [0.1, 1, 10],
                'kernel': ['rbf', 'linear'],
                'gamma': ['scale', 'auto']
            }
        }
    
    async def start_training(self, 
                           X: np.ndarray, 
                           y: np.ndarray,
                           job_name: Optional[str] = None) -> str:
        """Démarre un job d'entraînement AutoML"""



        try:
            job_id = str(uuid.uuid4())
            if job_name:
                job_id = f"{job_name}_{job_id[:8]}"
            
            # Créer le job
            job = TrainingJob(
                job_id=job_id,
                model_type=self.config.model_type,
                status=TrainingStatus.PENDING,
                config=self.config,
                start_time=datetime.now()
            )
            
            self.training_jobs[job_id] = job
            logger.info(f"Job d'entraînement créé: {job_id}")
            
            # Lancer l'entraînement en arrière-plan
            asyncio.create_task(self._train_models(job_id, X, y))
            
            return job_id
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de l'entraînement: {e}")
            raise
    
    async def _train_models(self, job_id: str, X: np.ndarray, y: np.ndarray):
        """Entraîne les modèles de façon asynchrone"""
        job = self.training_jobs[job_id]
        
        try:
            job.status = TrainingStatus.RUNNING
            start_time = time.time()
            
            logger.info(f"Début de l'entraînement pour le job {job_id}")
            
            # Préparation des données
            X_processed, y_processed = await self._preprocess_data(X, y)
            
            # Entraînement des modèles
            best_model, best_metrics = await self._train_and_select_best_model(
                X_processed, y_processed
            )
            
            # Sauvegarde du modèle
            model_path = await self._save_model(job_id, best_model)
            
            # Finalisation
            training_time = time.time() - start_time
            best_metrics.training_time = training_time
            
            job.status = TrainingStatus.COMPLETED
            job.end_time = datetime.now()
            job.metrics = best_metrics
            job.model_path = model_path
            
            logger.info(f"Entraînement terminé pour le job {job_id} en {training_time:.2f}s")
            
        except Exception as e:
            job.status = TrainingStatus.FAILED
            job.end_time = datetime.now()
            job.error_message = str(e)
            logger.error(f"Erreur lors de l'entraînement {job_id}: {e}")
    
    async def _preprocess_data(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Préprocessing des données"""



        try:
            # Normalisation des features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Encoding des labels si nécessaire
            if y.dtype == 'object':
                encoder = LabelEncoder()
                y_encoded = encoder.fit_transform(y)
            else:
                y_encoded = y
            
            return X_scaled, y_encoded
            
        except Exception as e:
            logger.error(f"Erreur lors du preprocessing: {e}")
            raise
    
    async def _train_and_select_best_model(self, 
                                         X: np.ndarray, 
                                         y: np.ndarray) -> Tuple[Any, TrainingMetrics]:
        """Entraîne tous les modèles et sélectionne le meilleur"""
        best_model = None
        best_metrics = None
        best_score = -float('inf')
        
        models = self.base_models.get(self.config.model_type, {})
        
        for model_name, base_model in models.items():
            try:
                logger.info(f"Entraînement du modèle: {model_name}")
                
                # Hyperparameter tuning
                param_grid = self.param_grids.get(model_name, {})
                
                if param_grid and self.config.max_trials > 1:
                    # Grid search avec cross-validation
                    grid_search = GridSearchCV(
                        base_model,
                        param_grid,
                        cv=self.config.cv_folds,
                        scoring=self.config.scoring_metric,
                        n_jobs=-1,
                        verbose=0
                    )
                    
                    grid_search.fit(X, y)
                    model = grid_search.best_estimator_
                    hyperparams = grid_search.best_params_
                    score = grid_search.best_score_
                else:
                    # Entraînement simple
                    model = base_model.fit(X, y)
                    hyperparams = model.get_params()
                    score = cross_val_score(
                        model, X, y, 
                        cv=self.config.cv_folds, 
                        scoring=self.config.scoring_metric
                    ).mean()
                
                # Calcul des métriques
                y_pred = model.predict(X)
                
                # Cross-validation scores
                cv_scores = cross_val_score(
                    model, X, y, 
                    cv=self.config.cv_folds, 
                    scoring=self.config.scoring_metric
                ).tolist()
                
                # Feature importance
                feature_importance = {}
                if hasattr(model, 'feature_importances_'):
                    feature_importance = {
                        f'feature_{i}': importance 
                        for i, importance in enumerate(model.feature_importances_)
                    }
                
                metrics = TrainingMetrics(
                    accuracy=accuracy_score(y, y_pred),
                    precision=precision_score(y, y_pred, average='weighted'),
                    recall=recall_score(y, y_pred, average='weighted'),
                    f1_score=f1_score(y, y_pred, average='weighted'),
                    training_time=0.0,  # Will be set later
                    cross_val_scores=cv_scores,
                    feature_importance=feature_importance,
                    hyperparameters=hyperparams
                )
                
                # Sélection du meilleur modèle
                if score > best_score:
                    best_score = score
                    best_model = model
                    best_metrics = metrics
                
                logger.info(f"Modèle {model_name} - Score: {score:.4f}")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'entraînement du modèle {model_name}: {e}")
                continue
        
        if best_model is None:
            raise ValueError("Aucun modèle n'a pu être entraîné avec succès")
        
        return best_model, best_metrics
    
    async def _save_model(self, job_id: str, model: Any) -> str:
        """Sauvegarde le modèle entraîné"""



        try:
            # Créer le répertoire si nécessaire
            models_dir = Path("models")
            models_dir.mkdir(exist_ok=True)
            
            # Chemin du modèle
            model_path = models_dir / f"{job_id}_model.pkl"
            
            # Sauvegarde
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Cache en mémoire
            self.model_cache[job_id] = model
            
            logger.info(f"Modèle sauvegardé: {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du modèle: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[TrainingJob]:
        """Récupère le statut d'un job"""



        return self.training_jobs.get(job_id)
    
    async def cancel_job(self, job_id: str) -> bool:
        """Annule un job d'entraînement"""
        job = self.training_jobs.get(job_id)
        if job and job.status in [TrainingStatus.PENDING, TrainingStatus.RUNNING]:
            job.status = TrainingStatus.CANCELLED
            job.end_time = datetime.now()
            logger.info(f"Job {job_id} annulé")
            return True
        return False
    
    async def load_model(self, job_id: str) -> Optional[Any]:
        """Charge un modèle entraîné"""
        # Vérifier le cache
        if job_id in self.model_cache:
            return self.model_cache[job_id]
        
        # Charger depuis le fichier
        job = self.training_jobs.get(job_id)
        if job and job.model_path:
            try:
                with open(job.model_path, 'rb') as f:
                    model = pickle.load(f)
                self.model_cache[job_id] = model
                return model
            except Exception as e:
                logger.error(f"Erreur lors du chargement du modèle {job_id}: {e}")
        
        return None
    
    async def predict(self, job_id: str, X: np.ndarray) -> Optional[np.ndarray]:
        """Fait des prédictions avec un modèle entraîné"""
        model = await self.load_model(job_id)
        if model:
            try:
                return model.predict(X)
            except Exception as e:
                logger.error(f"Erreur lors de la prédiction avec le modèle {job_id}: {e}")
        return None
    
    async def get_training_history(self) -> List[TrainingJob]:
        """Récupère l'historique des entraînements"""



        return list(self.training_jobs.values())
    
    async def cleanup_old_jobs(self, days_old: int = 30):
        """Nettoie les anciens jobs"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        jobs_to_remove = []
        
        for job_id, job in self.training_jobs.items():
            if job.end_time and job.end_time < cutoff_date:
                jobs_to_remove.append(job_id)
                
                # Supprimer le fichier modèle
                if job.model_path and Path(job.model_path).exists():
                    Path(job.model_path).unlink()
                
                # Supprimer du cache
                if job_id in self.model_cache:
                    del self.model_cache[job_id]
        
        for job_id in jobs_to_remove:
            del self.training_jobs[job_id]
        
        logger.info(f"{len(jobs_to_remove)} anciens jobs supprimés")


# Factory pour créer des pipelines spécialisés
class AutoMLPipelineFactory:
    """Factory pour créer des pipelines AutoML spécialisés"""
    
    @staticmethod
    def create_content_protection_pipeline() -> AutoMLPipeline:
        """Pipeline pour la protection de contenu"""
        config = AutoMLConfig(
            model_type=ModelType.CONTENT_PROTECTION,
            max_trials=50,
            max_time_minutes=30,
            scoring_metric="f1_weighted"
        )
        return AutoMLPipeline(config)
    
    @staticmethod
    def create_seo_optimization_pipeline() -> AutoMLPipeline:
        """Pipeline pour l'optimisation SEO"""
        config = AutoMLConfig(
            model_type=ModelType.SEO_OPTIMIZATION,
            max_trials=30,
            max_time_minutes=20,
            scoring_metric="accuracy"
        )
        return AutoMLPipeline(config)
    
    @staticmethod
    def create_recommendation_pipeline() -> AutoMLPipeline:
        """Pipeline pour les recommandations"""
        config = AutoMLConfig(
            model_type=ModelType.RECOMMENDATION,
            max_trials=100,
            max_time_minutes=60,
            scoring_metric="precision"
        )
        return AutoMLPipeline(config)


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation du pipeline AutoML"""
    
    # Créer des données d'exemple
    np.random.seed(42)
    X = np.random.randn(1000, 10)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    
    # Créer le pipeline
    pipeline = AutoMLPipelineFactory.create_content_protection_pipeline()
    
    # Démarrer l'entraînement
    job_id = await pipeline.start_training(X, y, "content_protection_v1")
    print(f"Job d'entraînement démarré: {job_id}")
    
    # Attendre la completion
    while True:
        job = await pipeline.get_job_status(job_id)
        if job.status in [TrainingStatus.COMPLETED, TrainingStatus.FAILED]:
            break
        await asyncio.sleep(1)
    
    # Vérifier les résultats
    if job.status == TrainingStatus.COMPLETED:
        print(f"Entraînement terminé avec succès!")
        print(f"Accuracy: {job.metrics.accuracy:.4f}")
        print(f"F1-Score: {job.metrics.f1_score:.4f}")
        
        # Faire des prédictions
        X_test = np.random.randn(10, 10)
        predictions = await pipeline.predict(job_id, X_test)
        print(f"Prédictions: {predictions}")
    else:
        print(f"Entraînement échoué: {job.error_message}")


if __name__ == "__main__":
    asyncio.run(example_usage())