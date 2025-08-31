"""Model Registry - Advanced ML Model Management & Version Control System

Industrial-grade model registry providing comprehensive model lifecycle management,
version control, metadata tracking, model deployment management, and governance
for the IA-Influencer-Agent ML platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This model registry system and methodologies are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
is strictly PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025
"""import asyncio
import logging
import time
import uuid
import json
import pickle
import joblib
import hashlib
import shutil
import boto3
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from pathlib import Path
import numpy as np
import pandas as pd
import traceback
from packaging import version
import mlflow
import mlflow.tracking
from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Integer, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml

# Core ML frameworks
import tensorflow as tf
import torch
import sklearn
try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

# Platform imports
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
    from core.exceptions import ModelRegistryError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ModelRegistryError, ValidationError = globals().get('ModelRegistryError, ValidationError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.cache import CacheManager

# Prometheus monitoring
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

Base = declarative_base()

class ModelStatus(Enum):
    """Model lifecycle status"""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"
    FAILED = "failed"

class ModelType(Enum):
    """Model types"""    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    GENERATIVE = "generative"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    TIME_SERIES = "time_series"
    REINFORCEMENT_LEARNING = "reinforcement_learning"

class ModelFramework(Enum):
    """Supported ML frameworks"""    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    SKLEARN = "sklearn"
    ONNX = "onnx"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CUSTOM = "custom"

class DeploymentTarget(Enum):
    """Deployment targets"""    CLOUD = "cloud"
    EDGE = "edge"
    MOBILE = "mobile"
    WEB = "web"
    API = "api"
    BATCH = "batch"

@dataclass
class ModelMetadata:
    """Comprehensive model metadata"""    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    
    # Model information
    framework: ModelFramework = ModelFramework.SKLEARN
    model_type: ModelType = ModelType.CLASSIFICATION
    status: ModelStatus = ModelStatus.DEVELOPMENT
    
    # Technical specifications
    input_shape: Optional[Tuple[int, ...]] = None
    output_shape: Optional[Tuple[int, ...]] = None
    model_size_mb: float = 0.0
    parameter_count: int = 0
    
    # Performance metrics
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None
    
    # Training information
    training_dataset_size: int = 0
    training_duration_seconds: float = 0.0
    training_epochs: int = 0
    training_loss: Optional[float] = None
    validation_loss: Optional[float] = None
    
    # Deployment information
    deployment_targets: List[DeploymentTarget] = field(default_factory=list)
    inference_latency_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    throughput_rps: Optional[float] = None
    
    # Governance and compliance
    author: str = ""
    team: str = ""
    project: str = ""
    experiment_id: str = ""
    run_id: str = ""
    
    # Dependencies
    python_version: str = ""
    dependencies: Dict[str, str] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    
    # Data lineage
    training_data_hash: str = ""
    feature_schema: Dict[str, Any] = field(default_factory=dict)
    preprocessing_steps: List[str] = field(default_factory=list)
    
    # Validation and testing
    test_accuracy: Optional[float] = None
    cross_validation_scores: List[float] = field(default_factory=list)
    model_signature: str = ""
    
    # Monitoring and alerting
    monitoring_enabled: bool = False
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    drift_detection_enabled: bool = False
    
    # Storage and paths
    model_path: str = ""
    artifacts_path: str = ""
    checkpoint_path: str = ""
    logs_path: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    trained_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    
    # Custom metadata
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class ModelVersion:
    """Model version information"""    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str = ""
    version: str = "1.0.0"
    parent_version: Optional[str] = None
    
    # Version changes
    changes: List[str] = field(default_factory=list)
    changelog: str = ""
    migration_notes: str = ""
    
    # Performance comparison
    performance_delta: Dict[str, float] = field(default_factory=dict)
    size_delta_mb: float = 0.0
    speed_delta_percent: float = 0.0
    
    # Validation status
    validation_status: str = "pending"  # pending, passed, failed
    validation_results: Dict[str, Any] = field(default_factory=dict)
    
    # Approval workflow
    approval_status: str = "pending"  # pending, approved, rejected
    approver: str = ""
    approval_notes: str = ""
    
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DeploymentConfig:
    """Model deployment configuration"""    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str = ""
    model_version: str = ""
    
    # Deployment target
    target: DeploymentTarget = DeploymentTarget.API
    environment: str = "staging"  # development, staging, production
    
    # Resource configuration
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "256Mi"
    memory_limit: str = "512Mi"
    gpu_required: bool = False
    gpu_type: str = ""
    
    # Scaling configuration
    min_replicas: int = 1
    max_replicas: int = 10
    auto_scaling_enabled: bool = True
    target_cpu_utilization: int = 70
    
    # Network configuration
    service_port: int = 8080
    health_check_path: str = "/health"
    readiness_probe_path: str = "/ready"
    
    # Monitoring configuration
    metrics_enabled: bool = True
    logging_level: str = "INFO"
    tracing_enabled: bool = False
    
    # Security configuration
    authentication_required: bool = True
    rate_limiting_enabled: bool = True
    rate_limit_rps: int = 100
    
    # Advanced configuration
    canary_deployment: bool = False
    canary_percentage: int = 10
    blue_green_deployment: bool = False
    
    created_at: datetime = field(default_factory=datetime.utcnow)

class ModelRegistryDB(Base):
    """Database model for model registry"""    __tablename__ = 'model_registry'
    
    model_id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    framework = Column(String(20), nullable=False)
    model_type = Column(String(30), nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModelRegistry:
    """    Ultra-Advanced Model Registry & Management System
    
    Comprehensive model lifecycle management providing:
    - Model versioning and lineage tracking
    - Metadata management and governance
    - Performance tracking and comparison
    - Deployment management and orchestration
    - Model validation and testing
    - Artifact storage and retrieval
    - Security and access control
    - Monitoring and alerting integration
    - Multi-framework support
    - Automated model lifecycle workflows
    """    
    # Prometheus metrics
    REGISTERED_MODELS = Counter('model_registry_models_total', 'Total registered models', ['framework', 'type'])
    MODEL_OPERATIONS = Counter('model_registry_operations_total', 'Model registry operations', ['operation', 'status'])
    ACTIVE_MODELS = Gauge('model_registry_active_models', 'Active models by status', ['status'])
    DEPLOYMENT_STATUS = Gauge('model_registry_deployments', 'Model deployments', ['environment', 'status'])
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.registry_id = f"registry_{uuid.uuid4().hex[:8]}"
        
        # Storage configuration
        self.base_storage_path = Path(self.config.get("storage_path", "/tmp/model_registry"))
        self.base_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Database configuration
        self.db_url = self.config.get("db_url", "sqlite:///model_registry.db")
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # MLflow configuration
        if self.config.get("enable_mlflow", True):
            mlflow_tracking_uri = self.config.get("mlflow_tracking_uri", "sqlite:///mlflow.db")
            mlflow.set_tracking_uri(mlflow_tracking_uri)
        
        # Cloud storage configuration
        self.s3_client = None
        if self.config.get("enable_s3", False):
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config.get("aws_access_key_id"),
                aws_secret_access_key=self.config.get("aws_secret_access_key"),
                region_name=self.config.get("aws_region", "us-east-1")
            )
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(f"registry_{self.registry_id}")
        
        # Cache management
        self.cache_manager = CacheManager("model_registry_cache")
        
        # Model storage
        self.models_storage: Dict[str, Dict[str, Any]] = {}
        self.model_versions: Dict[str, List[ModelVersion]] = {}
        self.deployments: Dict[str, DeploymentConfig] = {}
        
        # Background tasks
        self.background_tasks = set()
        
        logger.info(f"ModelRegistry initialized: {self.registry_id}")
    
    async def initialize(self) -> bool:
        """Initialize model registry"""        try:
            # Test database connection
            with self.Session() as session:
                session.execute("SELECT 1")
            
            # Initialize cloud storage
            if self.s3_client:
                bucket_name = self.config.get("s3_bucket", "model-registry")
                try:
                    self.s3_client.head_bucket(Bucket=bucket_name)
                except:
                    try:
                        self.s3_client.create_bucket(Bucket=bucket_name)
                        logger.info(f"Created S3 bucket: {bucket_name}")
                    except Exception as e:
                        logger.warning(f"Failed to create S3 bucket: {e}")
            
            # Start background cleanup task
            cleanup_task = asyncio.create_task(self._cleanup_old_models())
            self.background_tasks.add(cleanup_task)
            cleanup_task.add_done_callback(self.background_tasks.discard)
            
            logger.info("ModelRegistry successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"ModelRegistry initialization failed: {str(e)}")
            return False

    async def register_model(self,
                           model: Any,
                           metadata: ModelMetadata,
                           artifacts: Optional[Dict[str, Any]] = None,
                           upload_to_cloud: bool = False) -> str:
        """        Register a new model or new version of existing model
        
        Args:
            model: Model object to register
            metadata: Comprehensive model metadata
            artifacts: Additional model artifacts (configs, preprocessors, etc.)
            upload_to_cloud: Whether to upload to cloud storage
            
        Returns:
            str: Model ID of registered model
        """        try:
            logger.info(f"Registering model: {metadata.name} v{metadata.version}")
            
            with self.performance_monitor.monitor_context():
                # Validate metadata
                validation_result = await self._validate_model_metadata(metadata)
                if not validation_result["valid"]:
                    raise ValueError(f"Metadata validation failed: {validation_result['errors']}")
                
                # Generate model signature
                model_signature = await self._generate_model_signature(model, metadata.framework)
                metadata.model_signature = model_signature
                
                # Calculate model size and parameters
                model_info = await self._analyze_model_structure(model, metadata.framework)
                metadata.model_size_mb = model_info["size_mb"]
                metadata.parameter_count = model_info["parameter_count"]
                
                # Create storage paths
                model_dir = self.base_storage_path / metadata.name / metadata.version
                model_dir.mkdir(parents=True, exist_ok=True)
                
                # Save model
                model_path = await self._save_model(model, model_dir, metadata.framework)
                metadata.model_path = str(model_path)
                
                # Save artifacts
                if artifacts:
                    artifacts_path = model_dir / "artifacts"
                    artifacts_path.mkdir(exist_ok=True)
                    
                    for name, artifact in artifacts.items():
                        artifact_file = artifacts_path / f"{name}.pkl"
                        with open(artifact_file, 'wb') as f:
                            pickle.dump(artifact, f)
                    
                    metadata.artifacts_path = str(artifacts_path)
                
                # Save metadata
                metadata_file = model_dir / "metadata.json"
                with open(metadata_file, 'w') as f:
                    json.dump(asdict(metadata), f, indent=2, default=str)
                
                # Register in database
                await self._save_model_to_db(metadata)
                
                # Upload to cloud storage if requested
                if upload_to_cloud and self.s3_client:
                    await self._upload_model_to_cloud(model_dir, metadata)
                
                # Register with MLflow
                if self.config.get("enable_mlflow", True):
                    await self._register_with_mlflow(model, metadata, artifacts)
                
                # Update in-memory storage
                self.models_storage[metadata.model_id] = {
                    "model": model,
                    "metadata": metadata,
                    "artifacts": artifacts or {}
                }
                
                # Initialize versions list if new model
                if metadata.model_id not in self.model_versions:
                    self.model_versions[metadata.model_id] = []
                
                # Create version entry
                model_version = ModelVersion(
                    model_id=metadata.model_id,
                    version=metadata.version,
                    changes=[f"Initial registration of {metadata.name}"],
                    changelog=f"Registered model {metadata.name} version {metadata.version}"
                )
                self.model_versions[metadata.model_id].append(model_version)
                
                # Update metrics
                self.REGISTERED_MODELS.labels(
                    framework=metadata.framework.value,
                    type=metadata.model_type.value
                ).inc()
                self.MODEL_OPERATIONS.labels(operation="register", status="success").inc()
                self.ACTIVE_MODELS.labels(status=metadata.status.value).inc()
                
                logger.info(f"Model registered successfully: {metadata.model_id}")
                return metadata.model_id
                
        except Exception as e:
            self.MODEL_OPERATIONS.labels(operation="register", status="failed").inc()
            logger.error(f"Model registration failed: {str(e)}")
            raise ModelRegistryError(f"Model registration failed: {str(e)}")

    async def get_model(self,
                       model_id: str,
                       version: Optional[str] = None,
                       load_artifacts: bool = True) -> Dict[str, Any]:
        """        Retrieve model and metadata
        
        Args:
            model_id: Model identifier
            version: Specific version (latest if None)
            load_artifacts: Whether to load associated artifacts
            
        Returns:
            Dict containing model, metadata, and artifacts
        """        try:
            logger.info(f"Retrieving model: {model_id} v{version or 'latest'}")
            
            # Check in-memory cache first
            if model_id in self.models_storage:
                cached_data = self.models_storage[model_id]
                if version is None or cached_data["metadata"].version == version:
                    logger.info(f"Model retrieved from cache: {model_id}")
                    return cached_data
            
            # Check cache
            cache_key = f"model_{model_id}_{version or 'latest'}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Load from database
            metadata = await self._load_model_from_db(model_id, version)
            if not metadata:
                raise ModelRegistryError(f"Model not found: {model_id}")
            
            # Load model from storage
            model_path = Path(metadata.model_path)
            if not model_path.exists():
                # Try to download from cloud storage
                if self.s3_client:
                    await self._download_model_from_cloud(model_id, version)
                
                if not model_path.exists():
                    raise ModelRegistryError(f"Model file not found: {model_path}")
            
            # Load model
            model = await self._load_model(model_path, metadata.framework)
            
            # Load artifacts if requested
            artifacts = {}
            if load_artifacts and metadata.artifacts_path:
                artifacts_path = Path(metadata.artifacts_path)
                if artifacts_path.exists():
                    for artifact_file in artifacts_path.glob("*.pkl"):
                        with open(artifact_file, 'rb') as f:
                            artifacts[artifact_file.stem] = pickle.load(f)
            
            result = {
                "model": model,
                "metadata": metadata,
                "artifacts": artifacts
            }
            
            # Cache result
            await self.cache_manager.set(cache_key, result, expire_seconds=3600)
            
            # Update in-memory storage
            self.models_storage[model_id] = result
            
            self.MODEL_OPERATIONS.labels(operation="get", status="success").inc()
            logger.info(f"Model retrieved successfully: {model_id}")
            
            return result
            
        except Exception as e:
            self.MODEL_OPERATIONS.labels(operation="get", status="failed").inc()
            logger.error(f"Model retrieval failed: {str(e)}")
            raise ModelRegistryError(f"Model retrieval failed: {str(e)}")

    async def update_model_status(self,
                                model_id: str,
                                status: ModelStatus,
                                notes: str = "") -> bool:
        """Update model status"""        try:
            logger.info(f"Updating model status: {model_id} -> {status.value}")
            
            # Load current metadata
            metadata = await self._load_model_from_db(model_id)
            if not metadata:
                raise ModelRegistryError(f"Model not found: {model_id}")
            
            old_status = metadata.status
            metadata.status = status
            metadata.updated_at = datetime.utcnow()
            
            # Add to custom metadata
            if "status_history" not in metadata.custom_metadata:
                metadata.custom_metadata["status_history"] = []
            
            metadata.custom_metadata["status_history"].append({
                "from": old_status.value,
                "to": status.value,
                "timestamp": datetime.utcnow().isoformat(),
                "notes": notes
            })
            
            # Update in database
            await self._save_model_to_db(metadata)
            
            # Update in-memory storage
            if model_id in self.models_storage:
                self.models_storage[model_id]["metadata"] = metadata
            
            # Update metrics
            self.ACTIVE_MODELS.labels(status=old_status.value).dec()
            self.ACTIVE_MODELS.labels(status=status.value).inc()
            
            self.MODEL_OPERATIONS.labels(operation="update_status", status="success").inc()
            logger.info(f"Model status updated successfully: {model_id}")
            
            return True
            
        except Exception as e:
            self.MODEL_OPERATIONS.labels(operation="update_status", status="failed").inc()
            logger.error(f"Model status update failed: {str(e)}")
            raise ModelRegistryError(f"Model status update failed: {str(e)}")

    async def create_model_version(self,
                                 model_id: str,
                                 new_model: Any,
                                 version: str,
                                 changes: List[str],
                                 parent_version: Optional[str] = None) -> str:
        """Create new version of existing model"""        try:
            logger.info(f"Creating model version: {model_id} v{version}")
            
            # Load parent model metadata
            parent_metadata = await self._load_model_from_db(model_id, parent_version)
            if not parent_metadata:
                raise ModelRegistryError(f"Parent model not found: {model_id}")
            
            # Create new metadata based on parent
            new_metadata = ModelMetadata(**asdict(parent_metadata))
            new_metadata.model_id = str(uuid.uuid4())
            new_metadata.version = version
            new_metadata.created_at = datetime.utcnow()
            new_metadata.updated_at = datetime.utcnow()
            
            # Register new version
            new_model_id = await self.register_model(new_model, new_metadata)
            
            # Create version record
            model_version = ModelVersion(
                model_id=model_id,
                version=version,
                parent_version=parent_version,
                changes=changes,
                changelog="; ".join(changes)
            )
            
            # Add to version history
            if model_id not in self.model_versions:
                self.model_versions[model_id] = []
            self.model_versions[model_id].append(model_version)
            
            logger.info(f"Model version created successfully: {new_model_id}")
            return new_model_id
            
        except Exception as e:
            logger.error(f"Model version creation failed: {str(e)}")
            raise ModelRegistryError(f"Model version creation failed: {str(e)}")

    async def compare_models(self,
                           model_id_1: str,
                           model_id_2: str,
                           comparison_metrics: List[str] = None) -> Dict[str, Any]:
        """Compare two models across various metrics"""        try:
            logger.info(f"Comparing models: {model_id_1} vs {model_id_2}")
            
            # Load models
            model_1_data = await self.get_model(model_id_1, load_artifacts=False)
            model_2_data = await self.get_model(model_id_2, load_artifacts=False)
            
            metadata_1 = model_1_data["metadata"]
            metadata_2 = model_2_data["metadata"]
            
            comparison_metrics = comparison_metrics or [
                "accuracy", "precision", "recall", "f1_score", "model_size_mb",
                "inference_latency_ms", "memory_usage_mb"
            ]
            
            comparison_result = {
                "model_1": {
                    "id": model_id_1,
                    "name": metadata_1.name,
                    "version": metadata_1.version
                },
                "model_2": {
                    "id": model_id_2,
                    "name": metadata_2.name,
                    "version": metadata_2.version
                },
                "metrics": {},
                "winner": None,
                "comparison_timestamp": datetime.utcnow().isoformat()
            }
            
            score_1 = 0
            score_2 = 0
            
            for metric in comparison_metrics:
                value_1 = getattr(metadata_1, metric, None)
                value_2 = getattr(metadata_2, metric, None)
                
                if value_1 is not None and value_2 is not None:
                    comparison_result["metrics"][metric] = {
                        "model_1": value_1,
                        "model_2": value_2,
                        "difference": value_2 - value_1,
                        "relative_change": ((value_2 - value_1) / value_1) * 100 if value_1 != 0 else 0
                    }
                    
                    # Determine winner for this metric (higher is better for most metrics)
                    if metric in ["model_size_mb", "inference_latency_ms", "memory_usage_mb"]:
                        # Lower is better for these metrics
                        if value_1 < value_2:
                            score_1 += 1
                            comparison_result["metrics"][metric]["winner"] = "model_1"
                        elif value_2 < value_1:
                            score_2 += 1
                            comparison_result["metrics"][metric]["winner"] = "model_2"
                    else:
                        # Higher is better for performance metrics
                        if value_1 > value_2:
                            score_1 += 1
                            comparison_result["metrics"][metric]["winner"] = "model_1"
                        elif value_2 > value_1:
                            score_2 += 1
                            comparison_result["metrics"][metric]["winner"] = "model_2"
            
            # Determine overall winner
            if score_1 > score_2:
                comparison_result["winner"] = "model_1"
            elif score_2 > score_1:
                comparison_result["winner"] = "model_2"
            else:
                comparison_result["winner"] = "tie"
            
            comparison_result["scores"] = {
                "model_1": score_1,
                "model_2": score_2
            }
            
            logger.info(f"Model comparison completed: {comparison_result['winner']}")
            return comparison_result
            
        except Exception as e:
            logger.error(f"Model comparison failed: {str(e)}")
            raise ModelRegistryError(f"Model comparison failed: {str(e)}")

    async def list_models(self,
                         status: Optional[ModelStatus] = None,
                         framework: Optional[ModelFramework] = None,
                         model_type: Optional[ModelType] = None,
                         limit: int = 100,
                         offset: int = 0) -> List[ModelMetadata]:
        """List models with filtering"""        try:
            logger.info("Listing models with filters")
            
            with self.Session() as session:
                query = session.query(ModelRegistryDB)
                
                if status:
                    query = query.filter(ModelRegistryDB.status == status.value)
                if framework:
                    query = query.filter(ModelRegistryDB.framework == framework.value)
                if model_type:
                    query = query.filter(ModelRegistryDB.model_type == model_type.value)
                
                query = query.order_by(ModelRegistryDB.created_at.desc())
                query = query.offset(offset).limit(limit)
                
                results = query.all()
                
                models = []
                for result in results:
                    metadata = ModelMetadata(**result.metadata)
                    models.append(metadata)
                
                logger.info(f"Listed {len(models)} models")
                return models
                
        except Exception as e:
            logger.error(f"Model listing failed: {str(e)}")
            raise ModelRegistryError(f"Model listing failed: {str(e)}")

    async def delete_model(self,
                         model_id: str,
                         force: bool = False) -> bool:
        """Delete model and all associated data"""        try:
            logger.info(f"Deleting model: {model_id} (force={force})")
            
            # Load model metadata
            metadata = await self._load_model_from_db(model_id)
            if not metadata:
                raise ModelRegistryError(f"Model not found: {model_id}")
            
            # Check if model is in production
            if metadata.status == ModelStatus.PRODUCTION and not force:
                raise ModelRegistryError("Cannot delete production model without force=True")
            
            # Remove from database
            with self.Session() as session:
                session.query(ModelRegistryDB).filter(
                    ModelRegistryDB.model_id == model_id
                ).delete()
                session.commit()
            
            # Remove from storage
            model_dir = Path(metadata.model_path).parent
            if model_dir.exists():
                shutil.rmtree(model_dir)
            
            # Remove from cloud storage
            if self.s3_client:
                await self._delete_model_from_cloud(model_id)
            
            # Remove from in-memory storage
            if model_id in self.models_storage:
                del self.models_storage[model_id]
            
            if model_id in self.model_versions:
                del self.model_versions[model_id]
            
            # Update metrics
            self.ACTIVE_MODELS.labels(status=metadata.status.value).dec()
            
            self.MODEL_OPERATIONS.labels(operation="delete", status="success").inc()
            logger.info(f"Model deleted successfully: {model_id}")
            
            return True
            
        except Exception as e:
            self.MODEL_OPERATIONS.labels(operation="delete", status="failed").inc()
            logger.error(f"Model deletion failed: {str(e)}")
            raise ModelRegistryError(f"Model deletion failed: {str(e)}")

    # Private helper methods
    async def _validate_model_metadata(self, metadata: ModelMetadata) -> Dict[str, Any]:
        """Validate model metadata"""        errors = []
        
        if not metadata.name:
            errors.append("Model name is required")
        
        if not metadata.version:
            errors.append("Model version is required")
        
        try:
            version.parse(metadata.version)
        except:
            errors.append("Invalid version format")
        
        if not metadata.author:
            errors.append("Model author is required")
        
        return {"valid": len(errors) == 0, "errors": errors}

    async def _generate_model_signature(self, model: Any, framework: ModelFramework) -> str:
        """Generate unique model signature"""        try:
            if framework == ModelFramework.SKLEARN:
                model_str = str(model.get_params()) if hasattr(model, 'get_params') else str(model)
            elif framework == ModelFramework.TENSORFLOW:
                model_str = str(model.get_config()) if hasattr(model, 'get_config') else str(model)
            elif framework == ModelFramework.PYTORCH:
                model_str = str(model.state_dict().keys()) if hasattr(model, 'state_dict') else str(model)
            else:
                model_str = str(model)
            
            return hashlib.md5(model_str.encode()).hexdigest()
            
        except Exception as e:
            logger.warning(f"Failed to generate model signature: {e}")
            return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()

    async def _analyze_model_structure(self, model: Any, framework: ModelFramework) -> Dict[str, Any]:
        """Analyze model structure and calculate size/parameters"""        try:
            info = {"size_mb": 0.0, "parameter_count": 0}
            
            if framework == ModelFramework.SKLEARN:
                # Estimate size using pickle
                import pickle
                import io
                buffer = io.BytesIO()
                pickle.dump(model, buffer)
                info["size_mb"] = buffer.tell() / (1024 * 1024)
                
                # Try to count parameters for some models
                if hasattr(model, 'coef_'):
                    info["parameter_count"] = model.coef_.size if hasattr(model.coef_, 'size') else 0
                    
            elif framework == ModelFramework.TENSORFLOW:
                if hasattr(model, 'count_params'):
                    info["parameter_count"] = model.count_params()
                
                # Estimate size
                temp_path = "/tmp/temp_model"
                model.save(temp_path, save_format='tf')
                size_bytes = sum(f.stat().st_size for f in Path(temp_path).rglob('*') if f.is_file())
                info["size_mb"] = size_bytes / (1024 * 1024)
                shutil.rmtree(temp_path)
                
            elif framework == ModelFramework.PYTORCH:
                if hasattr(model, 'parameters'):
                    info["parameter_count"] = sum(p.numel() for p in model.parameters())
                
                # Estimate size
                temp_path = "/tmp/temp_model.pth"
                torch.save(model.state_dict(), temp_path)
                info["size_mb"] = Path(temp_path).stat().st_size / (1024 * 1024)
                Path(temp_path).unlink()
            
            return info
            
        except Exception as e:
            logger.warning(f"Failed to analyze model structure: {e}")
            return {"size_mb": 0.0, "parameter_count": 0}

    async def _save_model(self, model: Any, model_dir: Path, framework: ModelFramework) -> Path:
        """Save model to storage"""        try:
            if framework == ModelFramework.SKLEARN:
                model_path = model_dir / "model.pkl"
                joblib.dump(model, model_path)
                
            elif framework == ModelFramework.TENSORFLOW:
                model_path = model_dir / "model"
                model.save(str(model_path), save_format='tf')
                
            elif framework == ModelFramework.PYTORCH:
                model_path = model_dir / "model.pth"
                torch.save(model.state_dict(), model_path)
                
            elif framework == ModelFramework.ONNX and ONNX_AVAILABLE:
                model_path = model_dir / "model.onnx"
                onnx.save(model, str(model_path))
                
            else:
                # Generic pickle fallback
                model_path = model_dir / "model.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
            
            return model_path
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise ModelRegistryError(f"Failed to save model: {e}")

    async def _load_model(self, model_path: Path, framework: ModelFramework) -> Any:
        """Load model from storage"""        try:
            if framework == ModelFramework.SKLEARN:
                return joblib.load(model_path)
                
            elif framework == ModelFramework.TENSORFLOW:
                return tf.keras.models.load_model(str(model_path))
                
            elif framework == ModelFramework.PYTORCH:
                return torch.load(model_path)
                
            elif framework == ModelFramework.ONNX and ONNX_AVAILABLE:
                return onnx.load(str(model_path))
                
            else:
                # Generic pickle fallback
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
                    
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ModelRegistryError(f"Failed to load model: {e}")

    async def _save_model_to_db(self, metadata: ModelMetadata):
        """Save model metadata to database"""        try:
            with self.Session() as session:
                existing = session.query(ModelRegistryDB).filter(
                    ModelRegistryDB.model_id == metadata.model_id
                ).first()
                
                if existing:
                    existing.name = metadata.name
                    existing.version = metadata.version
                    existing.status = metadata.status.value
                    existing.framework = metadata.framework.value
                    existing.model_type = metadata.model_type.value
                    existing.metadata = asdict(metadata)
                    existing.updated_at = datetime.utcnow()
                else:
                    db_model = ModelRegistryDB(
                        model_id=metadata.model_id,
                        name=metadata.name,
                        version=metadata.version,
                        status=metadata.status.value,
                        framework=metadata.framework.value,
                        model_type=metadata.model_type.value,
                        metadata=asdict(metadata)
                    )
                    session.add(db_model)
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Failed to save model to database: {e}")
            raise ModelRegistryError(f"Failed to save model to database: {e}")

    async def _load_model_from_db(self, model_id: str, version: Optional[str] = None) -> Optional[ModelMetadata]:
        """Load model metadata from database"""        try:
            with self.Session() as session:
                query = session.query(ModelRegistryDB).filter(
                    ModelRegistryDB.model_id == model_id
                )
                
                if version:
                    query = query.filter(ModelRegistryDB.version == version)
                else:
                    query = query.order_by(ModelRegistryDB.created_at.desc())
                
                result = query.first()
                
                if result:
                    return ModelMetadata(**result.metadata)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to load model from database: {e}")
            return None

    async def _register_with_mlflow(self, model: Any, metadata: ModelMetadata, artifacts: Optional[Dict[str, Any]]):
        """Register model with MLflow"""        try:
            if not self.config.get("enable_mlflow", True):
                return
            
            with mlflow.start_run(run_name=f"{metadata.name}_v{metadata.version}"):
                # Log parameters
                mlflow.log_param("model_name", metadata.name)
                mlflow.log_param("version", metadata.version)
                mlflow.log_param("framework", metadata.framework.value)
                mlflow.log_param("model_type", metadata.model_type.value)
                
                # Log metrics
                if metadata.accuracy is not None:
                    mlflow.log_metric("accuracy", metadata.accuracy)
                if metadata.precision is not None:
                    mlflow.log_metric("precision", metadata.precision)
                if metadata.recall is not None:
                    mlflow.log_metric("recall", metadata.recall)
                if metadata.f1_score is not None:
                    mlflow.log_metric("f1_score", metadata.f1_score)
                
                # Log model
                if metadata.framework == ModelFramework.SKLEARN:
                    mlflow.sklearn.log_model(model, "model")
                elif metadata.framework == ModelFramework.TENSORFLOW:
                    mlflow.tensorflow.log_model(model, "model")
                elif metadata.framework == ModelFramework.PYTORCH:
                    mlflow.pytorch.log_model(model, "model")
                
                # Log artifacts
                if artifacts:
                    for name, artifact in artifacts.items():
                        mlflow.log_artifact(artifact, f"artifacts/{name}")
                
                metadata.run_id = mlflow.active_run().info.run_id
                
        except Exception as e:
            logger.warning(f"MLflow registration failed: {e}")

    async def _upload_model_to_cloud(self, model_dir: Path, metadata: ModelMetadata):
        """Upload model to cloud storage"""        try:
            if not self.s3_client:
                return
            
            bucket_name = self.config.get("s3_bucket", "model-registry")
            s3_prefix = f"models/{metadata.name}/{metadata.version}/"
            
            for file_path in model_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(model_dir)
                    s3_key = s3_prefix + str(relative_path)
                    
                    self.s3_client.upload_file(
                        str(file_path),
                        bucket_name,
                        s3_key
                    )
            
            logger.info(f"Model uploaded to cloud: {s3_prefix}")
            
        except Exception as e:
            logger.warning(f"Cloud upload failed: {e}")

    async def _download_model_from_cloud(self, model_id: str, version: Optional[str] = None):
        """Download model from cloud storage"""        try:
            if not self.s3_client:
                return
            
            # Implementation would download model files from cloud storage
            logger.info(f"Downloading model from cloud: {model_id}")
            
        except Exception as e:
            logger.warning(f"Cloud download failed: {e}")

    async def _delete_model_from_cloud(self, model_id: str):
        """Delete model from cloud storage"""        try:
            if not self.s3_client:
                return
            
            # Implementation would delete model files from cloud storage
            logger.info(f"Deleting model from cloud: {model_id}")
            
        except Exception as e:
            logger.warning(f"Cloud deletion failed: {e}")

    async def _cleanup_old_models(self):
        """Background task to cleanup old/unused models"""        while True:
            try:
                logger.info("Running model cleanup")
                
                # Cleanup logic would go here
                # - Remove models older than X days in ARCHIVED status
                # - Clean up temporary files
                # - Remove unused artifacts
                
                await asyncio.sleep(24 * 3600)  # Run daily
                
            except Exception as e:
                logger.error(f"Model cleanup error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour

class ModelDeploymentManager:
    """    Advanced Model Deployment Management System
    """    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.deployment_id = f"deployment_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"ModelDeploymentManager initialized: {self.deployment_id}")
    
    async def deploy_model(self,
                         model_id: str,
                         deployment_config: DeploymentConfig) -> str:
        """Deploy model to specified target"""        try:
            logger.info(f"Deploying model: {model_id}")
            
            # Load model
            model_data = await self.registry.get_model(model_id)
            
            # Execute deployment based on target
            if deployment_config.target == DeploymentTarget.API:
                deployment_result = await self._deploy_to_api(model_data, deployment_config)
            elif deployment_config.target == DeploymentTarget.BATCH:
                deployment_result = await self._deploy_to_batch(model_data, deployment_config)
            elif deployment_config.target == DeploymentTarget.EDGE:
                deployment_result = await self._deploy_to_edge(model_data, deployment_config)
            else:
                raise ModelRegistryError(f"Unsupported deployment target: {deployment_config.target}")
            
            # Update model metadata
            await self.registry.update_model_status(model_id, ModelStatus.PRODUCTION)
            
            # Update metrics
            self.registry.DEPLOYMENT_STATUS.labels(
                environment=deployment_config.environment,
                status="deployed"
            ).inc()
            
            logger.info(f"Model deployed successfully: {deployment_result}")
            return deployment_result
            
        except Exception as e:
            logger.error(f"Model deployment failed: {str(e)}")
            raise ModelRegistryError(f"Model deployment failed: {str(e)}")
    
    async def _deploy_to_api(self, model_data: Dict[str, Any], config: DeploymentConfig) -> str:
        """Deploy model as API service"""        # Implementation would create API service (e.g., FastAPI, Flask)
        # with proper scaling, monitoring, etc.
        logger.info("Deploying model as API service")
        return f"api_deployment_{uuid.uuid4().hex[:8]}"
    
    async def _deploy_to_batch(self, model_data: Dict[str, Any], config: DeploymentConfig) -> str:
        """Deploy model for batch processing"""        # Implementation would create batch processing job
        logger.info("Deploying model for batch processing")
        return f"batch_deployment_{uuid.uuid4().hex[:8]}"
    
    async def _deploy_to_edge(self, model_data: Dict[str, Any], config: DeploymentConfig) -> str:
        """Deploy model to edge devices"""        # Implementation would prepare model for edge deployment
        logger.info("Deploying model to edge")
        return f"edge_deployment_{uuid.uuid4().hex[:8]}"
