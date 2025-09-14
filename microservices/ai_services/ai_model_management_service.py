"""
Ai Model Management Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Enterprise AI Model Management Service
ML model lifecycle and version management for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
import json
import hashlib
import pickle
import joblib
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union, Tuple, Type
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    """Model status enumeration"""
    TRAINING = "training"
    READY = "ready"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"
    ARCHIVED = "archived"

class ModelType(Enum):
    """Model type enumeration"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    DEEP_LEARNING = "deep_learning"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    CUSTOM = "custom"

class ModelFramework(Enum):
    """Model framework enumeration"""
    SCIKIT_LEARN = "scikit_learn"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    HUGGING_FACE = "hugging_face"
    ONNX = "onnx"
    CUSTOM = "custom"

class DeploymentEnvironment(Enum):
    """Deployment environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    A_B_TEST = "a_b_test"

@dataclass
class ModelMetadata:
    """Model metadata structure"""
    name: str
    version: str
    description: str
    model_type: ModelType
    framework: ModelFramework
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    training_config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    author: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class ModelVersion:
    """Model version information"""
    model_id: str
    version: str
    status: ModelStatus
    metadata: ModelMetadata
    model_path: str
    model_size: int = 0
    checksum: str = ""
    parent_version: Optional[str] = None
    deployments: List[DeploymentEnvironment] = field(default_factory=list)
    performance_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)

@dataclass
class ModelDeployment:
    """Model deployment information"""
    deployment_id: str
    model_id: str
    version: str
    environment: DeploymentEnvironment
    endpoint_url: str
    status: str
    replica_count: int = 1
    resource_allocation: Dict[str, str] = field(default_factory=dict)
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    health_check_url: str = ""
    deployed_at: float = field(default_factory=time.time)
    last_health_check: float = 0.0

@dataclass
class ModelRegistry:
    """Model registry entry"""
    model_id: str
    name: str
    current_version: str
    versions: Dict[str, ModelVersion] = field(default_factory=dict)
    deployments: Dict[str, ModelDeployment] = field(default_factory=dict)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

class AIModelManagementService:
    """
    Enterprise AI Model Management Service
    
    Provides comprehensive ML model lifecycle management with:
    - Model versioning and registry
    - Automated deployment
    - Performance monitoring
    - A/B testing support
    - Model rollback capabilities
    - Resource optimization
    """
    
    def __init__(self, storage_path -> None: str = "/tmp/models") -> None:
        """Initialize AI model management service"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Model registry
        self.model_registry: Dict[str, ModelRegistry] = {}
        
        # Active models cache
        self.loaded_models: Dict[str, Any] = {}
        self.model_cache_size = 10
        
        # Performance tracking
        self.prediction_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "request_count": 0,
            "total_latency": 0.0,
            "avg_latency": 0.0,
            "error_count": 0,
            "success_rate": 1.0,
            "last_prediction": 0.0
        })
        
        # Deployment tracking
        self.deployment_queue: List[Dict[str, Any]] = []
        self.rollback_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.config = {
            "auto_deployment_enabled": True,
            "performance_threshold": 0.8,
            "max_versions_per_model": 10,
            "cache_ttl": 3600.0,  # 1 hour
            "health_check_interval": 300.0,  # 5 minutes
            "backup_enabled": True,
            "compression_enabled": True,
            "monitoring_enabled": True
        }
        
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # Background tasks
        self.health_check_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("AIModelManagementService initialized with storage: %s", storage_path)
    
    async def start(self) -> None:
        """Start the model management service"""
        try:
            # Load existing model registry
            await self._load_registry()
            
            # Start background tasks
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("AIModelManagementService started successfully")
        except Exception as e:
            logger.error("Failed to start AIModelManagementService: %s", e)
            raise
    
    async def stop(self) -> None:
        """Stop the model management service"""
        try:
            self.shutdown_event.set()
            
            # Save registry
            await self._save_registry()
            
            # Stop background tasks
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Clear loaded models
            self.loaded_models.clear()
            
            logger.info("AIModelManagementService stopped successfully")
        except Exception as e:
            logger.error("Error stopping AIModelManagementService: %s", e)
    
    async def register_model(
        self,
        model_id: str,
        model_object: Any,
        metadata: ModelMetadata,
        replace_existing: bool = False
    ) -> str:
        """Register a new model or version"""
        async with self._lock:
            # Generate version if not provided
            version = metadata.version or await self._generate_version(model_id)
            metadata.version = version
            
            # Create model path
            model_path = self.storage_path / model_id / version
            model_path.mkdir(parents=True, exist_ok=True)
            
            # Save model
            model_file_path = await self._save_model(model_object, model_path, metadata.framework)
            
            # Calculate checksum
            checksum = await self._calculate_checksum(model_file_path)
            
            # Get model size
            model_size = model_file_path.stat().st_size
            
            # Create model version
            model_version = ModelVersion(
                model_id=model_id,
                version=version,
                status=ModelStatus.READY,
                metadata=metadata,
                model_path=str(model_file_path),
                model_size=model_size,
                checksum=checksum
            )
            
            # Update registry
            if model_id not in self.model_registry:
                self.model_registry[model_id] = ModelRegistry(
                    model_id=model_id,
                    name=metadata.name,
                    current_version=version
                )
            
            registry = self.model_registry[model_id]
            
            # Check version conflicts
            if version in registry.versions and not replace_existing:
                raise ValueError(f"Version {version} already exists for model {model_id}")
            
            registry.versions[version] = model_version
            registry.current_version = version
            registry.last_accessed = time.time()
            
            # Limit number of versions
            await self._cleanup_old_versions(model_id)
            
            # Auto-deploy if enabled
            if self.config["auto_deployment_enabled"]:
                await self._schedule_deployment(model_id, version, DeploymentEnvironment.STAGING)
        
        logger.info("Registered model %s version %s", model_id, version)
        return version
    
    async def get_model(self, model_id: str, version: Optional[str] = None) -> Any:
        """Get a model by ID and version"""
        async with self._lock:
            if model_id not in self.model_registry:
                raise ValueError(f"Model {model_id} not found")
            
            registry = self.model_registry[model_id]
            target_version = version or registry.current_version
            
            if target_version not in registry.versions:
                raise ValueError(f"Version {target_version} not found for model {model_id}")
            
            model_version = registry.versions[target_version]
            cache_key = f"{model_id}:{target_version}"
            
            # Check cache first
            if cache_key in self.loaded_models:
                registry.access_count += 1
                registry.last_accessed = time.time()
                model_version.last_accessed = time.time()
                return self.loaded_models[cache_key]
            
            # Load model
            model = await self._load_model(model_version)
            
            # Cache model (with LRU eviction)
            await self._cache_model(cache_key, model)
            
            # Update access tracking
            registry.access_count += 1
            registry.last_accessed = time.time()
            model_version.last_accessed = time.time()
            
            return model
    
    async def deploy_model(
        self,
        model_id: str,
        version: str,
        environment: DeploymentEnvironment,
        deployment_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Deploy a model to an environment"""
        async with self._lock:
            if model_id not in self.model_registry:
                raise ValueError(f"Model {model_id} not found")
            
            registry = self.model_registry[model_id]
            
            if version not in registry.versions:
                raise ValueError(f"Version {version} not found for model {model_id}")
            
            model_version = registry.versions[version]
            
            if model_version.status != ModelStatus.READY:
                raise ValueError(f"Model version {version} is not ready for deployment")
            
            # Generate deployment ID
            deployment_id = f"deploy_{model_id}_{version}_{environment.value}_{int(time.time())}"
            
            # Create deployment configuration
            config = deployment_config or {}
            endpoint_url = config.get("endpoint_url", f"/models/{model_id}/{version}")
            
            deployment = ModelDeployment(
                deployment_id=deployment_id,
                model_id=model_id,
                version=version,
                environment=environment,
                endpoint_url=endpoint_url,
                status="deploying",
                replica_count=config.get("replica_count", 1),
                resource_allocation=config.get("resource_allocation", {}),
                deployment_config=config,
                health_check_url=config.get("health_check_url", f"{endpoint_url}/health")
            )
            
            # Store deployment
            registry.deployments[deployment_id] = deployment
            model_version.deployments.append(environment)
            model_version.status = ModelStatus.DEPLOYED
            
            # Simulate deployment process
            await self._execute_deployment(deployment)
        
        logger.info("Deployed model %s:%s to %s", model_id, version, environment.value)
        return deployment_id
    
    async def rollback_model(
        self,
        model_id: str,
        target_version: str,
        environment: DeploymentEnvironment
    ) -> bool:
        """Rollback model to a previous version"""
        async with self._lock:
            if model_id not in self.model_registry:
                raise ValueError(f"Model {model_id} not found")
            
            registry = self.model_registry[model_id]
            
            if target_version not in registry.versions:
                raise ValueError(f"Target version {target_version} not found")
            
            # Find current deployment
            current_deployment = None
            for deployment in registry.deployments.values():
                if deployment.environment == environment and deployment.status == "active":
                    current_deployment = deployment
                    break
            
            if not current_deployment:
                raise ValueError(f"No active deployment found for environment {environment.value}")
            
            # Record rollback
            rollback_record = {
                "model_id": model_id,
                "from_version": current_deployment.version,
                "to_version": target_version,
                "environment": environment.value,
                "timestamp": time.time(),
                "reason": "manual_rollback"
            }
            self.rollback_history.append(rollback_record)
            
            # Update deployment
            current_deployment.version = target_version
            current_deployment.deployed_at = time.time()
            
            # Update model status
            target_model = registry.versions[target_version]
            target_model.status = ModelStatus.DEPLOYED
            if environment not in target_model.deployments:
                target_model.deployments.append(environment)
        
        logger.info("Rolled back model %s to version %s in %s", model_id, target_version, environment.value)
        return True
    
    async def predict(
        self,
        model_id: str,
        input_data: Any,
        version: Optional[str] = None,
        track_performance: bool = True
    ) -> Any:
        """Make prediction using a model"""
        start_time = time.time()
        
        try:
            # Get model
            model = await self.get_model(model_id, version)
            
            # Make prediction
            if hasattr(model, 'predict'):
                result = model.predict(input_data)
            elif hasattr(model, '__call__'):
                result = model(input_data)
            else:
                raise ValueError(f"Model {model_id} does not support prediction")
            
            # Track performance
            if track_performance:
                latency = time.time() - start_time
                await self._update_prediction_metrics(model_id, latency, True)
            
            return result
            
        except Exception as e:
            # Track error
            if track_performance:
                latency = time.time() - start_time
                await self._update_prediction_metrics(model_id, latency, False)
            
            logger.error("Prediction error for model %s: %s", model_id, e)
            raise
    
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get comprehensive model information"""
        async with self._lock:
            if model_id not in self.model_registry:
                raise ValueError(f"Model {model_id} not found")
            
            registry = self.model_registry[model_id]
            
            # Get version information
            versions_info = {}
            for version, model_version in registry.versions.items():
                versions_info[version] = {
                    "status": model_version.status.value,
                    "size": model_version.model_size,
                    "created_at": model_version.created_at,
                    "last_accessed": model_version.last_accessed,
                    "deployments": [env.value for env in model_version.deployments],
                    "metrics": model_version.metadata.metrics
                }
            
            # Get deployment information
            deployments_info = {}
            for deployment_id, deployment in registry.deployments.items():
                deployments_info[deployment_id] = {
                    "environment": deployment.environment.value,
                    "status": deployment.status,
                    "endpoint": deployment.endpoint_url,
                    "deployed_at": deployment.deployed_at,
                    "replica_count": deployment.replica_count
                }
            
            # Get performance metrics
            performance = self.prediction_metrics.get(model_id, {})
            
            return {
                "model_id": model_id,
                "name": registry.name,
                "current_version": registry.current_version,
                "access_count": registry.access_count,
                "last_accessed": registry.last_accessed,
                "versions": versions_info,
                "deployments": deployments_info,
                "performance": dict(performance)
            }
    
    async def list_models(self, filter_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all models with optional filtering"""
        async with self._lock:
            models = []
            
            for model_id, registry in self.model_registry.items():
                current_version = registry.versions.get(registry.current_version)
                if not current_version:
                    continue
                
                model_info = {
                    "model_id": model_id,
                    "name": registry.name,
                    "current_version": registry.current_version,
                    "status": current_version.status.value,
                    "model_type": current_version.metadata.model_type.value,
                    "framework": current_version.metadata.framework.value,
                    "created_at": current_version.created_at,
                    "last_accessed": registry.last_accessed,
                    "access_count": registry.access_count
                }
                
                # Apply filters
                if filter_params:
                    if not self._matches_filter(model_info, current_version.metadata, filter_params):
                        continue
                
                models.append(model_info)
            
            return models
    
    async def delete_model(self, model_id: str, version: Optional[str] = None) -> bool:
        """Delete a model or specific version"""
        async with self._lock:
            if model_id not in self.model_registry:
                raise ValueError(f"Model {model_id} not found")
            
            registry = self.model_registry[model_id]
            
            if version:
                # Delete specific version
                if version not in registry.versions:
                    raise ValueError(f"Version {version} not found")
                
                model_version = registry.versions[version]
                
                # Check if version is deployed
                if model_version.deployments:
                    raise ValueError(f"Cannot delete deployed version {version}")
                
                # Remove model files
                model_path = Path(model_version.model_path)
                if model_path.exists():
                    model_path.unlink()
                
                # Remove from registry
                del registry.versions[version]
                
                # Update current version if needed
                if registry.current_version == version:
                    if registry.versions:
                        registry.current_version = max(registry.versions.keys())
                    else:
                        registry.current_version = ""
                
                # Remove from cache
                cache_key = f"{model_id}:{version}"
                self.loaded_models.pop(cache_key, None)
                
            else:
                # Delete entire model
                for deployment in registry.deployments.values():
                    if deployment.status == "active":
                        raise ValueError(f"Cannot delete model with active deployments")
                
                # Remove all model files
                model_dir = self.storage_path / model_id
                if model_dir.exists():
                    shutil.rmtree(model_dir)
                
                # Remove from cache
                cache_keys_to_remove = [
                    key for key in self.loaded_models.keys()
                    if key.startswith(f"{model_id}:")
                ]
                for key in cache_keys_to_remove:
                    del self.loaded_models[key]
                
                # Remove from registry
                del self.model_registry[model_id]
        
        logger.info("Deleted model %s%s", model_id, f" version {version}" if version else "")
        return True
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        async with self._lock:
            total_models = len(self.model_registry)
            total_versions = sum(len(registry.versions) for registry in self.model_registry.values())
            total_deployments = sum(len(registry.deployments) for registry in self.model_registry.values())
            
            # Calculate storage usage
            total_size = sum(
                sum(version.model_size for version in registry.versions.values())
                for registry in self.model_registry.values()
            )
            
            # Performance summary
            total_predictions = sum(
                metrics["request_count"] for metrics in self.prediction_metrics.values()
            )
            
            avg_latency = 0.0
            if self.prediction_metrics:
                avg_latency = sum(
                    metrics["avg_latency"] for metrics in self.prediction_metrics.values()
                ) / len(self.prediction_metrics)
            
            return {
                "total_models": total_models,
                "total_versions": total_versions,
                "total_deployments": total_deployments,
                "total_storage_bytes": total_size,
                "cached_models": len(self.loaded_models),
                "total_predictions": total_predictions,
                "avg_prediction_latency": avg_latency,
                "rollback_count": len(self.rollback_history),
                "config": dict(self.config)
            }
    
    async def _generate_version(self, model_id: str) -> str:
        """Generate next version for a model"""
        if model_id not in self.model_registry:
            return "1.0.0"
        
        versions = list(self.model_registry[model_id].versions.keys())
        if not versions:
            return "1.0.0"
        
        # Simple version increment (in production, use semantic versioning)
        max_version = max(versions)
        try:
            major, minor, patch = map(int, max_version.split('.'))
            return f"{major}.{minor}.{patch + 1}"
        except:
            return f"{len(versions) + 1}.0.0"
    
    async def _save_model(self, model_object: Any, model_path: Path, framework: ModelFramework) -> Path:
        """Save model to disk"""
        if framework == ModelFramework.SCIKIT_LEARN:
            model_file = model_path / "model.joblib"
            joblib.dump(model_object, model_file)
        elif framework == ModelFramework.TENSORFLOW:
            model_file = model_path / "model.h5"
            # model_object.save(model_file)  # Would use TensorFlow's save
            # For now, use pickle as fallback
            model_file = model_path / "model.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model_object, f)
        else:
            # Default pickle serialization
            model_file = model_path / "model.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model_object, f)
        
        # Save metadata
        metadata_file = model_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump({"framework": framework.value}, f)
        
        return model_file
    
    async def _load_model(self, model_version: ModelVersion) -> Any:
        """Load model from disk"""
        model_path = Path(model_version.model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        framework = model_version.metadata.framework
        
        if framework == ModelFramework.SCIKIT_LEARN and model_path.suffix == '.joblib':
            return joblib.load(model_path)
        elif framework == ModelFramework.TENSORFLOW and model_path.suffix == '.h5':
            # return tf.keras.models.load_model(model_path)
            # For now, fallback to pickle
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        else:
            # Default pickle loading
            with open(model_path, 'rb') as f:
                return pickle.load(f)
    
    async def _cache_model(self, cache_key -> None: str, model -> None: Any) -> None:
        """Cache model with LRU eviction"""
        # Remove oldest cached model if cache is full
        if len(self.loaded_models) >= self.model_cache_size:
            # Simple FIFO eviction (in production, use proper LRU)
            oldest_key = next(iter(self.loaded_models))
            del self.loaded_models[oldest_key]
        
        self.loaded_models[cache_key] = model
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def _cleanup_old_versions(self, model_id -> None: str) -> None:
        """Clean up old versions beyond the limit"""
        registry = self.model_registry[model_id]
        max_versions = self.config["max_versions_per_model"]
        
        if len(registry.versions) <= max_versions:
            return
        
        # Sort versions by creation time
        sorted_versions = sorted(
            registry.versions.items(),
            key=lambda x: x[1].created_at
        )
        
        # Remove oldest versions
        versions_to_remove = sorted_versions[:-max_versions]
        
        for version, model_version in versions_to_remove:
            # Skip if deployed
            if model_version.deployments:
                continue
            
            # Remove files
            model_path = Path(model_version.model_path)
            if model_path.exists():
                model_path.unlink()
            
            # Remove from registry
            del registry.versions[version]
            
            logger.info("Cleaned up old version %s of model %s", version, model_id)
    
    async def _update_prediction_metrics(self, model_id -> None: str, latency -> None: float, success -> None: bool) -> None:
        """Update prediction performance metrics"""
        metrics = self.prediction_metrics[model_id]
        
        metrics["request_count"] += 1
        metrics["total_latency"] += latency
        metrics["avg_latency"] = metrics["total_latency"] / metrics["request_count"]
        metrics["last_prediction"] = time.time()
        
        if not success:
            metrics["error_count"] += 1
        
        metrics["success_rate"] = (
            (metrics["request_count"] - metrics["error_count"]) / metrics["request_count"]
        )
    
    async def _schedule_deployment(self, model_id -> None: str, version -> None: str, environment -> None: DeploymentEnvironment) -> None:
        """Schedule model deployment"""
        deployment_task = {
            "model_id": model_id,
            "version": version,
            "environment": environment,
            "scheduled_at": time.time()
        }
        self.deployment_queue.append(deployment_task)
    
    async def _execute_deployment(self, deployment -> None: ModelDeployment) -> None:
        """Execute model deployment (simulation)"""
        # Simulate deployment process
        await asyncio.sleep(0.1)
        deployment.status = "active"
        deployment.last_health_check = time.time()
    
    async def _matches_filter(self, model_info: Dict[str, Any], metadata: ModelMetadata, filters: Dict[str, Any]) -> bool:
        """Check if model matches filter criteria"""
        for key, value in filters.items():
            if key == "model_type" and metadata.model_type.value != value:
                return False
            elif key == "framework" and metadata.framework.value != value:
                return False
            elif key == "tags" and not any(tag in metadata.tags for tag in value):
                return False
            elif key == "status" and model_info.get("status") != value:
                return False
        
        return True
    
    async def _load_registry(self) -> None:
        """Load model registry from disk"""
        registry_path = self.storage_path / "registry.json"
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct registry (simplified for this example)
                logger.info("Loaded model registry with %d models", len(data))
            except Exception as e:
                logger.warning("Failed to load registry: %s", e)
    
    async def _save_registry(self) -> None:
        """Save model registry to disk"""
        registry_path = self.storage_path / "registry.json"
        try:
            # Simplified registry save (in production, serialize full registry)
            registry_data = {
                model_id: {
                    "name": registry.name,
                    "current_version": registry.current_version,
                    "version_count": len(registry.versions)
                }
                for model_id, registry in self.model_registry.items()
            }
            
            with open(registry_path, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
            logger.info("Saved model registry")
        except Exception as e:
            logger.error("Failed to save registry: %s", e)
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config["health_check_interval"])
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in health check loop: %s", e)
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on deployed models"""
        async with self._lock:
            for registry in self.model_registry.values():
                for deployment in registry.deployments.values():
                    if deployment.status == "active":
                        # Simulate health check
                        deployment.last_health_check = time.time()
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in cleanup loop: %s", e)
    
    async def _perform_cleanup(self) -> None:
        """Perform cleanup tasks"""
        async with self._lock:
            # Clean up old cache entries
            current_time = time.time()
            ttl = self.config["cache_ttl"]
            
            # Simple cleanup (in production, track access times)
            if len(self.loaded_models) > self.model_cache_size:
                oldest_keys = list(self.loaded_models.keys())[:len(self.loaded_models) - self.model_cache_size]
                for key in oldest_keys:
                    del self.loaded_models[key]

# Global model management service instance
_model_service: Optional[AIModelManagementService] = None

async def get_model_service(storage_path: str = "/tmp/models") -> AIModelManagementService:
    """Get global model management service instance"""
    global _model_service
    if _model_service is None:
        _model_service = AIModelManagementService(storage_path)
        await _model_service.start()
    return _model_service

async def shutdown_model_service() -> None:
    """Shutdown global model management service"""
    global _model_service
    if _model_service:
        await _model_service.stop()
        _model_service = None

if __name__ == "__main__":
    async def test_model_service() -> None:
        """Test model management service functionality"""
        service = AIModelManagementService("/tmp/test_models")
        await service.start()
        
        try:
            # Create a simple test model
            class SimpleModel:
    """SimpleModel: class implementation"""
                def predict(self, X) -> None:
                    return [1] * len(X) if hasattr(X, '__len__') else 1
            
            model = SimpleModel()
            
            # Create metadata
            metadata = ModelMetadata(
                name="Test Classification Model",
                version="1.0.0",
                description="A simple test model",
                model_type=ModelType.CLASSIFICATION,
                framework=ModelFramework.CUSTOM,
                metrics={"accuracy": 0.95, "precision": 0.92}
            )
            
            # Register model
            version = await service.register_model("test_model", model, metadata)
            print(f"Registered model version: {version}")
            
            # Get model and make prediction
            loaded_model = await service.get_model("test_model")
            result = await service.predict("test_model", [1, 2, 3])
            print(f"Prediction result: {result}")
            
            # Deploy model
            deployment_id = await service.deploy_model(
                "test_model", version, DeploymentEnvironment.STAGING
            )
            print(f"Deployment ID: {deployment_id}")
            
            # Get model info
            info = await service.get_model_info("test_model")
            print(f"Model info: {info}")
            
            # List models
            models = await service.list_models()
            print(f"Models: {len(models)}")
            
            # Get metrics
            metrics = await service.get_service_metrics()
            print(f"Service metrics: {metrics}")
            
        finally:
            await service.stop()
    
    # Run test
    asyncio.run(test_model_service())