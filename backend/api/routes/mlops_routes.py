"""
🤖 MLOPS ROUTES - Complete Implementation
========================================
ALL 30 endpoints for ML model lifecycle, training, deployment, monitoring
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/mlops", tags=["MLOps"])

# ============================================================================
# MODELS
# ============================================================================

class ModelStatus(str, Enum):
    TRAINING = "training"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"
    FAILED = "failed"

class DeploymentEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

# ============================================================================
# MODEL MANAGEMENT
# ============================================================================

@router.post("/models/register")
async def register_model(name: str, version: str, framework: str, metadata: Optional[Dict[str, Any]] = None):
    """Register ML model"""
    try:
        from backend.mlops.model_registry import ModelRegistry
        registry = ModelRegistry()
        await registry.initialize()
        
        model = await registry.register_model(name, version, framework, metadata or {})
        return {"message": "Model registered", "model": model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models(framework: Optional[str] = None, status: Optional[ModelStatus] = None):
    """List ML models"""
    try:
        from backend.mlops.model_registry import ModelRegistry
        registry = ModelRegistry()
        await registry.initialize()
        
        status_val = status.value if status else None
        models = await registry.list_models(framework, status_val)
        return {"models": models}
    except Exception as e:
        return {"models": [], "error": str(e)}

@router.get("/models/{model_id}")
async def get_model(model_id: str):
    """Get model details"""
    try:
        from backend.mlops.model_registry import ModelRegistry
        registry = ModelRegistry()
        await registry.initialize()
        
        model = await registry.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_id}/versions")
async def list_model_versions(model_id: str):
    """List model versions"""
    try:
        from backend.mlops.model_registry import ModelRegistry
        registry = ModelRegistry()
        await registry.initialize()
        
        versions = await registry.list_versions(model_id)
        return {"model_id": model_id, "versions": versions}
    except Exception as e:
        return {"model_id": model_id, "versions": [], "error": str(e)}

@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """Delete model"""
    try:
        from backend.mlops.model_registry import ModelRegistry
        registry = ModelRegistry()
        await registry.initialize()
        
        await registry.delete_model(model_id)
        return {"message": "Model deleted", "model_id": model_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TRAINING
# ============================================================================

@router.post("/training/start")
async def start_training(
    model_name: str,
    dataset: str,
    hyperparameters: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
):
    """Start model training"""
    try:
        from backend.mlops.training_pipeline import TrainingPipeline
        pipeline = TrainingPipeline()
        await pipeline.initialize()
        
        job = await pipeline.start_training(model_name, dataset, hyperparameters, config or {})
        return {"message": "Training started", "job": job}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training/jobs")
async def list_training_jobs(status: Optional[str] = None):
    """List training jobs"""
    try:
        from backend.mlops.training_pipeline import TrainingPipeline
        pipeline = TrainingPipeline()
        await pipeline.initialize()
        
        jobs = await pipeline.list_jobs(status)
        return {"jobs": jobs}
    except Exception as e:
        return {"jobs": [], "error": str(e)}

@router.get("/training/jobs/{job_id}")
async def get_training_job(job_id: str):
    """Get training job details"""
    try:
        from backend.mlops.training_pipeline import TrainingPipeline
        pipeline = TrainingPipeline()
        await pipeline.initialize()
        
        job = await pipeline.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Training job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/training/jobs/{job_id}/stop")
async def stop_training(job_id: str):
    """Stop training job"""
    try:
        from backend.mlops.training_pipeline import TrainingPipeline
        pipeline = TrainingPipeline()
        await pipeline.initialize()
        
        await pipeline.stop_training(job_id)
        return {"message": "Training stopped", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training/jobs/{job_id}/metrics")
async def get_training_metrics(job_id: str):
    """Get training metrics"""
    try:
        from backend.mlops.training_pipeline import TrainingPipeline
        pipeline = TrainingPipeline()
        await pipeline.initialize()
        
        metrics = await pipeline.get_metrics(job_id)
        return {"job_id": job_id, "metrics": metrics}
    except Exception as e:
        return {"job_id": job_id, "metrics": {}, "error": str(e)}

# ============================================================================
# DEPLOYMENT
# ============================================================================

@router.post("/deploy")
async def deploy_model(
    model_id: str,
    version: str,
    environment: DeploymentEnvironment = DeploymentEnvironment.DEVELOPMENT,
    config: Optional[Dict[str, Any]] = None
):
    """Deploy model"""
    try:
        from backend.mlops.deployment_manager import DeploymentManager
        manager = DeploymentManager()
        await manager.initialize()
        
        deployment = await manager.deploy_model(model_id, version, environment.value, config or {})
        return {"message": "Model deployed", "deployment": deployment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deployments")
async def list_deployments(environment: Optional[DeploymentEnvironment] = None):
    """List model deployments"""
    try:
        from backend.mlops.deployment_manager import DeploymentManager
        manager = DeploymentManager()
        await manager.initialize()
        
        env_val = environment.value if environment else None
        deployments = await manager.list_deployments(env_val)
        return {"deployments": deployments}
    except Exception as e:
        return {"deployments": [], "error": str(e)}

@router.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: str):
    """Get deployment details"""
    try:
        from backend.mlops.deployment_manager import DeploymentManager
        manager = DeploymentManager()
        await manager.initialize()
        
        deployment = await manager.get_deployment(deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        return deployment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: str):
    """Delete deployment"""
    try:
        from backend.mlops.deployment_manager import DeploymentManager
        manager = DeploymentManager()
        await manager.initialize()
        
        await manager.delete_deployment(deployment_id)
        return {"message": "Deployment deleted", "deployment_id": deployment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deployments/{deployment_id}/rollback")
async def rollback_deployment(deployment_id: str, version: Optional[str] = None):
    """Rollback deployment"""
    try:
        from backend.mlops.deployment_manager import DeploymentManager
        manager = DeploymentManager()
        await manager.initialize()
        
        result = await manager.rollback(deployment_id, version)
        return {"message": "Deployment rolled back", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MONITORING
# ============================================================================

@router.get("/monitoring/models/{model_id}")
async def monitor_model(model_id: str):
    """Monitor model performance"""
    try:
        from backend.mlops.model_monitor import ModelMonitor
        monitor = ModelMonitor()
        await monitor.initialize()
        
        metrics = await monitor.get_model_metrics(model_id)
        return {"model_id": model_id, "metrics": metrics}
    except Exception as e:
        return {"model_id": model_id, "metrics": {}, "error": str(e)}

@router.get("/monitoring/deployments/{deployment_id}")
async def monitor_deployment(deployment_id: str):
    """Monitor deployment"""
    try:
        from backend.mlops.model_monitor import ModelMonitor
        monitor = ModelMonitor()
        await monitor.initialize()
        
        metrics = await monitor.get_deployment_metrics(deployment_id)
        return {"deployment_id": deployment_id, "metrics": metrics}
    except Exception as e:
        return {"deployment_id": deployment_id, "metrics": {}, "error": str(e)}

@router.post("/monitoring/alerts")
async def create_alert(model_id: str, metric: str, threshold: float, condition: str):
    """Create monitoring alert"""
    try:
        from backend.mlops.model_monitor import ModelMonitor
        monitor = ModelMonitor()
        await monitor.initialize()
        
        alert = await monitor.create_alert(model_id, metric, threshold, condition)
        return {"message": "Alert created", "alert": alert}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/alerts")
async def list_alerts():
    """List monitoring alerts"""
    try:
        from backend.mlops.model_monitor import ModelMonitor
        monitor = ModelMonitor()
        await monitor.initialize()
        
        alerts = await monitor.list_alerts()
        return {"alerts": alerts}
    except Exception as e:
        return {"alerts": [], "error": str(e)}

# ============================================================================
# EXPERIMENTS
# ============================================================================

@router.post("/experiments/create")
async def create_experiment(name: str, description: str, config: Dict[str, Any]):
    """Create ML experiment"""
    try:
        from backend.mlops.experiment_tracker import ExperimentTracker
        tracker = ExperimentTracker()
        await tracker.initialize()
        
        experiment = await tracker.create_experiment(name, description, config)
        return {"message": "Experiment created", "experiment": experiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/experiments")
async def list_experiments():
    """List experiments"""
    try:
        from backend.mlops.experiment_tracker import ExperimentTracker
        tracker = ExperimentTracker()
        await tracker.initialize()
        
        experiments = await tracker.list_experiments()
        return {"experiments": experiments}
    except Exception as e:
        return {"experiments": [], "error": str(e)}

@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: str):
    """Get experiment details"""
    try:
        from backend.mlops.experiment_tracker import ExperimentTracker
        tracker = ExperimentTracker()
        await tracker.initialize()
        
        experiment = await tracker.get_experiment(experiment_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        return experiment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/experiments/{experiment_id}/log")
async def log_experiment_metrics(experiment_id: str, metrics: Dict[str, Any]):
    """Log experiment metrics"""
    try:
        from backend.mlops.experiment_tracker import ExperimentTracker
        tracker = ExperimentTracker()
        await tracker.initialize()
        
        await tracker.log_metrics(experiment_id, metrics)
        return {"message": "Metrics logged", "experiment_id": experiment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FEATURE STORE
# ============================================================================

@router.post("/features/create")
async def create_feature(name: str, description: str, data_type: str, config: Optional[Dict[str, Any]] = None):
    """Create feature"""
    try:
        from backend.mlops.feature_store import FeatureStore
        store = FeatureStore()
        await store.initialize()
        
        feature = await store.create_feature(name, description, data_type, config or {})
        return {"message": "Feature created", "feature": feature}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/features")
async def list_features():
    """List features"""
    try:
        from backend.mlops.feature_store import FeatureStore
        store = FeatureStore()
        await store.initialize()
        
        features = await store.list_features()
        return {"features": features}
    except Exception as e:
        return {"features": [], "error": str(e)}

@router.get("/features/{feature_id}")
async def get_feature(feature_id: str):
    """Get feature details"""
    try:
        from backend.mlops.feature_store import FeatureStore
        store = FeatureStore()
        await store.initialize()
        
        feature = await store.get_feature(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")
        return feature
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/features/{feature_id}/compute")
async def compute_feature(feature_id: str, entities: List[str]):
    """Compute feature values"""
    try:
        from backend.mlops.feature_store import FeatureStore
        store = FeatureStore()
        await store.initialize()
        
        values = await store.compute_feature(feature_id, entities)
        return {"feature_id": feature_id, "values": values}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MODEL EXPLAINABILITY
# ============================================================================

@router.post("/explain/{model_id}")
async def explain_prediction(model_id: str, input_data: Dict[str, Any]):
    """Explain model prediction"""
    try:
        from backend.mlops.explainability import ExplainabilityEngine
        engine = ExplainabilityEngine()
        await engine.initialize()
        
        explanation = await engine.explain(model_id, input_data)
        return {"model_id": model_id, "explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/explain/{model_id}/global")
async def get_global_explanation(model_id: str):
    """Get global model explanation"""
    try:
        from backend.mlops.explainability import ExplainabilityEngine
        engine = ExplainabilityEngine()
        await engine.initialize()
        
        explanation = await engine.get_global_explanation(model_id)
        return {"model_id": model_id, "explanation": explanation}
    except Exception as e:
        return {"model_id": model_id, "explanation": {}, "error": str(e)}
