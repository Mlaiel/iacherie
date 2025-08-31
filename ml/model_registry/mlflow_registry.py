"""🚀 MLflow Model Registry - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/model_registry/mlflow_registry.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 REGISTRE DE MODÈLES MLFLOW
Gestion complète du cycle de vie des modèles ML
- Versioning automatique des modèles
- Metadata et lineage tracking
- Model promotion et deployment
- Rollback et A/B testing support
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
import shutil

import mlflow
import mlflow.sklearn
import mlflow.pytorch
import mlflow.tensorflow
from mlflow.tracking import MlflowClient
from mlflow.entities import ViewType
import pandas as pd
import numpy as np

# Configuration
logger = logging.getLogger(__name__)

class ModelStage(Enum):
    """Stades du cycle de vie d'un modèle"""    NONE = "None"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"

class RegistryStatus(Enum):
    """Statut des opérations registry"""    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"

@dataclass
class ModelMetadata:
    """Métadonnées d'un modèle"""    name: str
    version: str
    stage: ModelStage
    description: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    created_timestamp: Optional[datetime] = None
    last_updated_timestamp: Optional[datetime] = None
    source_run_id: Optional[str] = None

@dataclass
class ModelRegistryConfig:
    """Configuration du model registry"""    tracking_uri: str = "sqlite:///mlflow.db"
    artifact_root: str = "./mlruns"
    experiment_name: str = "Default"
    enable_auto_versioning: bool = True
    enable_model_validation: bool = True
    max_versions_per_model: int = 10
    retention_days: int = 90

@dataclass
class DeploymentInfo:
    """Informations de déploiement"""    model_name: str
    version: str
    stage: ModelStage
    endpoint_url: Optional[str] = None
    deployment_time: Optional[datetime] = None
    health_status: str = "unknown"
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class MLflowModelRegistry:
    """Registre de modèles MLflow Enterprise"""    
    def __init__(self, config: ModelRegistryConfig):
        self.config = config
        self.client = None
        self.experiment_id = None
        
        # Initialiser MLflow
        self._initialize_mlflow()
        
        # Cache local
        self.model_cache: Dict[str, Any] = {}
        self.deployment_cache: Dict[str, DeploymentInfo] = {}
    
    def _initialize_mlflow(self):
        """Initialise la connexion MLflow"""        try:
            # Configuration MLflow
            mlflow.set_tracking_uri(self.config.tracking_uri)
            
            # Créer le client
            self.client = MlflowClient()
            
            # Créer ou récupérer l'expérience
            try:
                experiment = mlflow.get_experiment_by_name(self.config.experiment_name)
                if experiment is None:
                    self.experiment_id = mlflow.create_experiment(
                        self.config.experiment_name,
                        artifact_location=self.config.artifact_root
                    )
                else:
                    self.experiment_id = experiment.experiment_id
            except Exception as e:
                logger.warning(f"Erreur création expérience: {e}")
                self.experiment_id = "0"  # Default experiment
            
            logger.info(f"MLflow initialisé - Experiment ID: {self.experiment_id}")
            
        except Exception as e:
            logger.error(f"Erreur initialisation MLflow: {e}")
            raise
    
    async def register_model(self,
                           model: Any,
                           model_name: str,
                           run_id: Optional[str] = None,
                           description: Optional[str] = None,
                           tags: Optional[Dict[str, str]] = None,
                           metrics: Optional[Dict[str, float]] = None,
                           params: Optional[Dict[str, Any]] = None) -> str:
        """Enregistre un nouveau modèle dans le registry"""        
        try:
            # Démarrer un run MLflow si nécessaire
            if run_id is None:
                with mlflow.start_run(experiment_id=self.experiment_id) as run:
                    run_id = run.info.run_id
                    
                    # Log du modèle
                    model_uri = await self._log_model(model, model_name, metrics, params)
            else:
                model_uri = f"runs:/{run_id}/{model_name}"
            
            # Enregistrer le modèle dans le registry
            model_version = mlflow.register_model(
                model_uri=model_uri,
                name=model_name,
                tags=tags or {}
            )
            
            # Mettre à jour la description si fournie
            if description:
                self.client.update_model_version(
                    name=model_name,
                    version=model_version.version,
                    description=description
                )
            
            # Ajouter des tags supplémentaires
            if tags:
                for key, value in tags.items():
                    self.client.set_model_version_tag(
                        name=model_name,
                        version=model_version.version,
                        key=key,
                        value=value
                    )
            
            # Validation automatique si activée
            if self.config.enable_model_validation:
                await self._validate_model(model_name, model_version.version)
            
            logger.info(f"Modèle enregistré: {model_name} v{model_version.version}")
            
            return model_version.version
            
        except Exception as e:
            logger.error(f"Erreur enregistrement modèle {model_name}: {e}")
            raise
    
    async def _log_model(self,
                        model: Any,
                        model_name: str,
                        metrics: Optional[Dict[str, float]] = None,
                        params: Optional[Dict[str, Any]] = None) -> str:
        """Log un modèle dans MLflow"""        
        try:
            # Déterminer le type de modèle et le logger approprié
            model_type = type(model).__module__
            
            if 'sklearn' in model_type:
                mlflow.sklearn.log_model(model, model_name)
            elif 'torch' in model_type:
                mlflow.pytorch.log_model(model, model_name)
            elif 'tensorflow' in model_type or 'keras' in model_type:
                mlflow.tensorflow.log_model(model, model_name)
            else:
                # Fallback: utiliser pickle
                mlflow.sklearn.log_model(model, model_name)
            
            # Log des métriques
            if metrics:
                for key, value in metrics.items():
                    mlflow.log_metric(key, value)
            
            # Log des paramètres
            if params:
                for key, value in params.items():
                    mlflow.log_param(key, value)
            
            return f"runs:/{mlflow.active_run().info.run_id}/{model_name}"
            
        except Exception as e:
            logger.error(f"Erreur log modèle: {e}")
            raise
    
    async def _validate_model(self, model_name: str, version: str) -> bool:
        """Valide un modèle enregistré"""        
        try:
            # Charger le modèle pour validation
            model_uri = f"models:/{model_name}/{version}"
            model = mlflow.sklearn.load_model(model_uri)
            
            # Tests de validation basiques
            validation_passed = True
            
            # Vérifier que le modèle a les méthodes requises
            if not hasattr(model, 'predict'):
                logger.error(f"Modèle {model_name} v{version} n'a pas de méthode predict")
                validation_passed = False
            
            # Ajouter un tag de validation
            validation_tag = "validated" if validation_passed else "validation_failed"
            self.client.set_model_version_tag(
                name=model_name,
                version=version,
                key="validation_status",
                value=validation_tag
            )
            
            return validation_passed
            
        except Exception as e:
            logger.error(f"Erreur validation modèle {model_name} v{version}: {e}")
            return False
    
    async def promote_model(self,
                          model_name: str,
                          version: str,
                          stage: ModelStage) -> bool:
        """Promeut un modèle vers un nouveau stade"""        
        try:
            # Vérifier que le modèle existe
            model_version = self.client.get_model_version(model_name, version)
            
            if model_version is None:
                logger.error(f"Modèle {model_name} v{version} non trouvé")
                return False
            
            # Si promotion vers Production, archiver l'ancien modèle en Production
            if stage == ModelStage.PRODUCTION:
                await self._archive_production_models(model_name)
            
            # Promouvoir le modèle
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage.value
            )
            
            # Ajouter des tags de promotion
            self.client.set_model_version_tag(
                name=model_name,
                version=version,
                key="promoted_at",
                value=datetime.now().isoformat()
            )
            
            self.client.set_model_version_tag(
                name=model_name,
                version=version,
                key="promoted_to",
                value=stage.value
            )
            
            logger.info(f"Modèle {model_name} v{version} promu vers {stage.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur promotion modèle {model_name} v{version}: {e}")
            return False
    
    async def _archive_production_models(self, model_name: str):
        """Archive les modèles actuellement en production"""        
        try:
            # Récupérer les modèles en production
            production_models = self.client.get_latest_versions(
                model_name, stages=[ModelStage.PRODUCTION.value]
            )
            
            # Archiver chaque modèle en production
            for model_version in production_models:
                self.client.transition_model_version_stage(
                    name=model_name,
                    version=model_version.version,
                    stage=ModelStage.ARCHIVED.value
                )
                
                logger.info(f"Modèle {model_name} v{model_version.version} archivé")
                
        except Exception as e:
            logger.error(f"Erreur archivage modèles production: {e}")
    
    async def get_model(self, 
                       model_name: str, 
                       version: Optional[str] = None,
                       stage: Optional[ModelStage] = None) -> Optional[Any]:
        """Récupère un modèle du registry"""        
        try:
            # Déterminer l'URI du modèle
            if version:
                model_uri = f"models:/{model_name}/{version}"
                cache_key = f"{model_name}:{version}"
            elif stage:
                model_uri = f"models:/{model_name}/{stage.value}"
                cache_key = f"{model_name}:{stage.value}"
            else:
                # Dernière version
                model_uri = f"models:/{model_name}/latest"
                cache_key = f"{model_name}:latest"
            
            # Vérifier le cache
            if cache_key in self.model_cache:
                return self.model_cache[cache_key]
            
            # Charger le modèle
            model = mlflow.sklearn.load_model(model_uri)
            
            # Mettre en cache
            self.model_cache[cache_key] = model
            
            return model
            
        except Exception as e:
            logger.error(f"Erreur chargement modèle {model_name}: {e}")
            return None
    
    async def get_model_metadata(self,
                               model_name: str,
                               version: Optional[str] = None) -> Optional[ModelMetadata]:
        """Récupère les métadonnées d'un modèle"""        
        try:
            if version:
                model_version = self.client.get_model_version(model_name, version)
            else:
                # Dernière version
                latest_versions = self.client.get_latest_versions(model_name)
                if not latest_versions:
                    return None
                model_version = latest_versions[0]
            
            # Récupérer les métriques et paramètres du run
            run = self.client.get_run(model_version.run_id)
            
            # Créer les métadonnées
            metadata = ModelMetadata(
                name=model_version.name,
                version=model_version.version,
                stage=ModelStage(model_version.current_stage),
                description=model_version.description,
                tags=dict(model_version.tags),
                metrics=dict(run.data.metrics),
                params=dict(run.data.params),
                created_timestamp=datetime.fromtimestamp(model_version.creation_timestamp / 1000),
                last_updated_timestamp=datetime.fromtimestamp(model_version.last_updated_timestamp / 1000),
                source_run_id=model_version.run_id
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Erreur récupération métadonnées {model_name}: {e}")
            return None
    
    async def list_models(self) -> List[str]:
        """Liste tous les modèles dans le registry"""        
        try:
            registered_models = self.client.list_registered_models()
            return [model.name for model in registered_models]
            
        except Exception as e:
            logger.error(f"Erreur listage modèles: {e}")
            return []
    
    async def list_model_versions(self, model_name: str) -> List[ModelMetadata]:
        """Liste toutes les versions d'un modèle"""        
        try:
            model_versions = self.client.search_model_versions(f"name='{model_name}'")
            
            metadata_list = []
            for model_version in model_versions:
                metadata = await self.get_model_metadata(model_name, model_version.version)
                if metadata:
                    metadata_list.append(metadata)
            
            return metadata_list
            
        except Exception as e:
            logger.error(f"Erreur listage versions {model_name}: {e}")
            return []
    
    async def delete_model_version(self, model_name: str, version: str) -> bool:
        """Supprime une version spécifique d'un modèle"""        
        try:
            self.client.delete_model_version(model_name, version)
            
            # Supprimer du cache
            cache_key = f"{model_name}:{version}"
            if cache_key in self.model_cache:
                del self.model_cache[cache_key]
            
            logger.info(f"Version {version} du modèle {model_name} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression version {model_name} v{version}: {e}")
            return False
    
    async def compare_models(self,
                           model_specs: List[Tuple[str, str]],
                           metrics: List[str] = None) -> pd.DataFrame:
        """Compare plusieurs modèles"""        
        try:
            if metrics is None:
                metrics = ['accuracy', 'precision', 'recall', 'f1_score']
            
            comparison_data = []
            
            for model_name, version in model_specs:
                metadata = await self.get_model_metadata(model_name, version)
                if metadata:
                    row = {
                        'model_name': model_name,
                        'version': version,
                        'stage': metadata.stage.value,
                        'created_at': metadata.created_timestamp
                    }
                    
                    # Ajouter les métriques
                    for metric in metrics:
                        row[metric] = metadata.metrics.get(metric, None)
                    
                    comparison_data.append(row)
            
            return pd.DataFrame(comparison_data)
            
        except Exception as e:
            logger.error(f"Erreur comparaison modèles: {e}")
            return pd.DataFrame()
    
    async def rollback_to_version(self, model_name: str, version: str) -> bool:
        """Rollback vers une version spécifique en production"""        
        try:
            # Vérifier que la version existe
            model_version = self.client.get_model_version(model_name, version)
            if model_version is None:
                logger.error(f"Version {version} du modèle {model_name} non trouvée")
                return False
            
            # Archiver les modèles actuellement en production
            await self._archive_production_models(model_name)
            
            # Promouvoir la version cible vers Production
            success = await self.promote_model(model_name, version, ModelStage.PRODUCTION)
            
            if success:
                # Ajouter un tag de rollback
                self.client.set_model_version_tag(
                    name=model_name,
                    version=version,
                    key="rollback_at",
                    value=datetime.now().isoformat()
                )
                
                logger.info(f"Rollback réussi vers {model_name} v{version}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur rollback {model_name} v{version}: {e}")
            return False
    
    async def cleanup_old_versions(self, days_old: int = None) -> int:
        """Nettoie les anciennes versions de modèles"""        
        if days_old is None:
            days_old = self.config.retention_days
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_count = 0
            
            # Liste tous les modèles
            models = await self.list_models()
            
            for model_name in models:
                # Récupérer toutes les versions
                versions = await self.list_model_versions(model_name)
                
                # Trier par date de création
                versions.sort(key=lambda x: x.created_timestamp or datetime.min)
                
                # Garder au moins une version et ne pas supprimer Production/Staging
                for version in versions[:-1]:  # Garder la dernière version
                    if (version.created_timestamp and 
                        version.created_timestamp < cutoff_date and
                        version.stage not in [ModelStage.PRODUCTION, ModelStage.STAGING]):
                        
                        success = await self.delete_model_version(
                            model_name, version.version
                        )
                        if success:
                            deleted_count += 1
            
            logger.info(f"{deleted_count} anciennes versions supprimées")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Erreur nettoyage versions: {e}")
            return 0
    
    async def export_model_metadata(self, filepath: str) -> bool:
        """Exporte les métadonnées de tous les modèles"""        
        try:
            all_metadata = []
            models = await self.list_models()
            
            for model_name in models:
                versions = await self.list_model_versions(model_name)
                for version in versions:
                    metadata_dict = {
                        'model_name': version.name,
                        'version': version.version,
                        'stage': version.stage.value,
                        'description': version.description,
                        'created_timestamp': version.created_timestamp.isoformat() if version.created_timestamp else None,
                        'last_updated_timestamp': version.last_updated_timestamp.isoformat() if version.last_updated_timestamp else None,
                        'source_run_id': version.source_run_id,
                        'tags': version.tags,
                        'metrics': version.metrics,
                        'params': version.params
                    }
                    all_metadata.append(metadata_dict)
            
            # Exporter en JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(all_metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Métadonnées exportées vers: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur export métadonnées: {e}")
            return False


# Factory pour créer des registry spécialisés
class ModelRegistryFactory:
    """Factory pour créer des registres spécialisés"""    
    @staticmethod
    def create_local_registry(experiment_name: str = "Local_ML_Experiments") -> MLflowModelRegistry:
        """Registry local pour développement"""        config = ModelRegistryConfig(
            tracking_uri="sqlite:///local_mlflow.db",
            artifact_root="./local_mlruns",
            experiment_name=experiment_name
        )
        return MLflowModelRegistry(config)
    
    @staticmethod
    def create_production_registry(tracking_uri: str, 
                                 artifact_root: str) -> MLflowModelRegistry:
        """Registry pour production"""        config = ModelRegistryConfig(
            tracking_uri=tracking_uri,
            artifact_root=artifact_root,
            experiment_name="Production_ML_Models",
            enable_model_validation=True,
            max_versions_per_model=20,
            retention_days=180
        )
        return MLflowModelRegistry(config)


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation du model registry"""    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    from sklearn.metrics import accuracy_score
    
    # Créer des données d'exemple
    X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
    
    # Entraîner un modèle
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Calculer des métriques
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    
    # Créer le registry
    registry = ModelRegistryFactory.create_local_registry("Content_Protection_Models")
    
    # Enregistrer le modèle
    version = await registry.register_model(
        model=model,
        model_name="content_protection_classifier",
        description="Random Forest pour la protection de contenu",
        tags={"algorithm": "random_forest", "domain": "content_protection"},
        metrics={"accuracy": accuracy},
        params={"n_estimators": 100, "random_state": 42}
    )
    
    print(f"Modèle enregistré avec la version: {version}")
    
    # Promouvoir vers staging
    await registry.promote_model(
        "content_protection_classifier", 
        version, 
        ModelStage.STAGING
    )
    
    # Récupérer le modèle
    loaded_model = await registry.get_model(
        "content_protection_classifier", 
        stage=ModelStage.STAGING
    )
    
    # Tester le modèle chargé
    if loaded_model:
        test_pred = loaded_model.predict(X[:5])
        print(f"Prédictions test: {test_pred}")
    
    # Lister tous les modèles
    models = await registry.list_models()
    print(f"Modèles dans le registry: {models}")


if __name__ == "__main__":
    asyncio.run(example_usage())