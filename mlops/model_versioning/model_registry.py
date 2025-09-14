"""
MLOps Model Versioning and Registry
Implements complete model versioning with MLflow integration
"""

import warnings
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import hashlib
from datetime import datetime
import logging

# Optional dependencies with graceful degradation
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn("pandas not available. Some features will be limited.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    warnings.warn("numpy not available. Some features will be limited.")

# Optional MLflow import
try:
    import mlflow
    import mlflow.sklearn
    import mlflow.tracking
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    warnings.warn("MLflow not available. Install with: pip install mlflow")

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Central model registry with versioning capabilities"""
    
    def __init__(self, tracking_uri -> None: Optional[str] = None, experiment_name -> None: str = "ainflue_models") -> None:
        """Initialize model registry
        
        Args:
            tracking_uri: MLflow tracking URI
            experiment_name: Name of the MLflow experiment
        """
        if not MLFLOW_AVAILABLE:
            logger.warning("MLflow not available. Model registry will operate in mock mode.")
            self.experiment_id = "mock_experiment"
            return
            
        self.tracking_uri = tracking_uri or "file://./mlflow_runs"
        self.experiment_name = experiment_name
        
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(self.tracking_uri)
        
        # Create or get experiment
        try:
            self.experiment_id = mlflow.create_experiment(experiment_name)
        except mlflow.exceptions.MlflowException:
            self.experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
            
        mlflow.set_experiment(experiment_name)
        
    def register_model(
        self,
        model: Any,
        model_name: str,
        model_version: str,
        metrics: Dict[str, float],
        parameters: Dict[str, Any],
        artifacts: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        description: Optional[str] = None
    ) -> str:
        """Register a new model version
        
        Args:
            model: The trained model object
            model_name: Name of the model
            model_version: Version identifier
            metrics: Model performance metrics
            parameters: Model hyperparameters
            artifacts: Additional artifacts to log
            tags: Tags for the model
            description: Model description
            
        Returns:
            run_id: MLflow run ID
        """
        with mlflow.start_run() as run:
            # Log parameters
            mlflow.log_params(parameters)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            model_info = mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                registered_model_name=model_name
            )
            
            # Log artifacts if provided
            if artifacts:
                for artifact_name, artifact_path in artifacts.items():
                    mlflow.log_artifact(artifact_path, artifact_name)
            
            # Set tags
            if tags:
                mlflow.set_tags(tags)
                
            mlflow.set_tag("model_version", model_version)
            mlflow.set_tag("registration_time", datetime.now().isoformat())
            
            if description:
                mlflow.set_tag("description", description)
            
            # Calculate model fingerprint for integrity
            model_fingerprint = self._calculate_model_fingerprint(model, parameters)
            mlflow.set_tag("model_fingerprint", model_fingerprint)
            
            logger.info(f"Model {model_name} v{model_version} registered with run_id: {run.info.run_id}")
            
            return run.info.run_id
    
    def get_model(self, model_name: str, version: Optional[str] = None, stage: str = "Production") -> Tuple[Any, Dict]:
        """Load a model from registry
        
        Args:
            model_name: Name of the model
            version: Specific version (if None, gets latest from stage)
            stage: Model stage (Production, Staging, Archived)
            
        Returns:
            Tuple of (model, metadata)
        """
        try:
            if version:
                model_uri = f"models:/{model_name}/{version}"
            else:
                model_uri = f"models:/{model_name}/{stage}"
                
            model = mlflow.sklearn.load_model(model_uri)
            
            # Get model metadata
            client = mlflow.tracking.MlflowClient()
            if version:
                model_version = client.get_model_version(model_name, version)
            else:
                latest_versions = client.get_latest_versions(model_name, stages=[stage])
                if not latest_versions:
                    raise ValueError(f"No model found in {stage} stage")
                model_version = latest_versions[0]
            
            # Get run information
            run = client.get_run(model_version.run_id)
            
            metadata = {
                "version": model_version.version,
                "stage": model_version.current_stage,
                "run_id": model_version.run_id,
                "metrics": run.data.metrics,
                "params": run.data.params,
                "tags": run.data.tags,
                "creation_time": model_version.creation_timestamp,
                "last_updated": model_version.last_updated_timestamp
            }
            
            return model, metadata
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            raise
    
    def list_models(self) -> List[Dict]:
        """List all registered models"""
        client = mlflow.tracking.MlflowClient()
        models = client.list_registered_models()
        
        model_list = []
        for model in models:
            latest_versions = client.get_latest_versions(model.name)
            
            model_info = {
                "name": model.name,
                "description": model.description,
                "creation_time": model.creation_timestamp,
                "last_updated": model.last_updated_timestamp,
                "versions": []
            }
            
            for version in latest_versions:
                version_info = {
                    "version": version.version,
                    "stage": version.current_stage,
                    "run_id": version.run_id,
                    "creation_time": version.creation_timestamp
                }
                model_info["versions"].append(version_info)
            
            model_list.append(model_info)
        
        return model_list
    
    def transition_model_stage(self, model_name: str, version: str, stage: str) -> bool:
        """Transition model to different stage
        
        Args:
            model_name: Name of the model
            version: Model version
            stage: Target stage (Staging, Production, Archived)
            
        Returns:
            Success status
        """
        try:
            client = mlflow.tracking.MlflowClient()
            client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage
            )
            logger.info(f"Model {model_name} v{version} transitioned to {stage}")
            return True
        except Exception as e:
            logger.error(f"Error transitioning model stage: {str(e)}")
            return False
    
    def delete_model_version(self, model_name: str, version: str) -> bool:
        """Delete a specific model version
        
        Args:
            model_name: Name of the model
            version: Model version to delete
            
        Returns:
            Success status
        """
        try:
            client = mlflow.tracking.MlflowClient()
            client.delete_model_version(model_name, version)
            logger.info(f"Model {model_name} v{version} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting model version: {str(e)}")
            return False
    
    def get_model_lineage(self, model_name: str, version: str) -> Dict:
        """Get model lineage and provenance information
        
        Args:
            model_name: Name of the model
            version: Model version
            
        Returns:
            Lineage information
        """
        try:
            client = mlflow.tracking.MlflowClient()
            model_version = client.get_model_version(model_name, version)
            run = client.get_run(model_version.run_id)
            
            lineage = {
                "model_name": model_name,
                "version": version,
                "run_id": model_version.run_id,
                "experiment_id": run.info.experiment_id,
                "user_id": run.info.user_id,
                "start_time": run.info.start_time,
                "end_time": run.info.end_time,
                "source": run.info.source_name,
                "source_version": run.info.source_version,
                "git_commit": run.data.tags.get("mlflow.source.git.commit"),
                "parent_run_id": run.info.parent_run_id,
                "parameters": run.data.params,
                "metrics": run.data.metrics,
                "tags": run.data.tags
            }
            
            return lineage
            
        except Exception as e:
            logger.error(f"Error getting model lineage: {str(e)}")
            raise
    
    def _calculate_model_fingerprint(self, model: Any, parameters: Dict[str, Any]) -> str:
        """Calculate a fingerprint for model integrity"""
        # Combine model parameters and hyperparameters
        fingerprint_data = json.dumps(parameters, sort_keys=True)
        
        # Add model-specific information if available
        if hasattr(model, 'get_params'):
            model_params = model.get_params()
            fingerprint_data += json.dumps(model_params, sort_keys=True, default=str)
        
        # Calculate hash
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def validate_model_integrity(self, model_name: str, version: str) -> bool:
        """Validate model integrity using fingerprint
        
        Args:
            model_name: Name of the model
            version: Model version
            
        Returns:
            Integrity validation result
        """
        try:
            model, metadata = self.get_model(model_name, version)
            stored_fingerprint = metadata["tags"].get("model_fingerprint")
            
            if not stored_fingerprint:
                logger.warning(f"No fingerprint found for model {model_name} v{version}")
                return False
            
            # Recalculate fingerprint
            current_fingerprint = self._calculate_model_fingerprint(model, metadata["params"])
            
            if stored_fingerprint == current_fingerprint:
                logger.info(f"Model {model_name} v{version} integrity validated")
                return True
            else:
                logger.error(f"Model {model_name} v{version} integrity check failed")
                return False
                
        except Exception as e:
            logger.error(f"Error validating model integrity: {str(e)}")
            return False


class ModelVersionComparator:
    """Compare different model versions"""
    
    def __init__(self, registry -> None: ModelRegistry) -> None:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def compare_versions(self, model_name: str, version1: str, version2: str) -> Dict:
        """Compare two model versions
        
        Args:
            model_name: Name of the model
            version1: First version to compare
            version2: Second version to compare
            
        Returns:
            Comparison results
        """
        try:
            # Get model metadata for both versions
            _, metadata1 = self.registry.get_model(model_name, version1)
            _, metadata2 = self.registry.get_model(model_name, version2)
            
            comparison = {
                "model_name": model_name,
                "version1": version1,
                "version2": version2,
                "metrics_comparison": self._compare_metrics(metadata1["metrics"], metadata2["metrics"]),
                "params_comparison": self._compare_params(metadata1["params"], metadata2["params"]),
                "performance_improvement": self._calculate_improvement(metadata1["metrics"], metadata2["metrics"]),
                "creation_time_diff": metadata2["creation_time"] - metadata1["creation_time"]
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing model versions: {str(e)}")
            raise
    
    def _compare_metrics(self, metrics1: Dict, metrics2: Dict) -> Dict:
        """Compare metrics between versions"""
        comparison = {}
        all_metrics = set(metrics1.keys()) | set(metrics2.keys())
        
        for metric in all_metrics:
            val1 = metrics1.get(metric, 0)
            val2 = metrics2.get(metric, 0)
            
            comparison[metric] = {
                "version1": val1,
                "version2": val2,
                "difference": val2 - val1,
                "improvement_pct": ((val2 - val1) / val1 * 100) if val1 != 0 else 0
            }
        
        return comparison
    
    def _compare_params(self, params1: Dict, params2: Dict) -> Dict:
        """Compare parameters between versions"""
        comparison = {
            "added": {},
            "removed": {},
            "changed": {},
            "unchanged": {}
        }
        
        all_params = set(params1.keys()) | set(params2.keys())
        
        for param in all_params:
            if param in params1 and param in params2:
                if params1[param] != params2[param]:
                    comparison["changed"][param] = {
                        "old": params1[param],
                        "new": params2[param]
                    }
                else:
                    comparison["unchanged"][param] = params1[param]
            elif param in params1:
                comparison["removed"][param] = params1[param]
            else:
                comparison["added"][param] = params2[param]
        
        return comparison
    
    def _calculate_improvement(self, metrics1: Dict, metrics2: Dict) -> Dict:
        """Calculate overall performance improvement"""
        # Focus on common performance metrics
        performance_metrics = ["accuracy", "f1_score", "precision", "recall", "auc", "mse", "rmse"]
        
        improvements = {}
        for metric in performance_metrics:
            if metric in metrics1 and metric in metrics2:
                val1, val2 = metrics1[metric], metrics2[metric]
                
                # For error metrics (lower is better)
                if metric in ["mse", "rmse", "mae"]:
                    improvement = (val1 - val2) / val1 * 100 if val1 != 0 else 0
                else:
                    # For performance metrics (higher is better)
                    improvement = (val2 - val1) / val1 * 100 if val1 != 0 else 0
                
                improvements[metric] = improvement
        
        return improvements