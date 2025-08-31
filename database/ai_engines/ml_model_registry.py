"""
ML Model Registry - AI Engines Database Module

This module provides comprehensive machine learning model registry capabilities
for the IA Influencer Agent platform, including model versioning, metadata
storage, artifact management, and lifecycle tracking.

Core Components:
- AIModelRegistry: Central model registration and management
- ModelVersionManager: Version control for ML models
- ModelMetadataStore: Metadata storage and retrieval
- ModelArtifactManager: Model file and artifact management

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer & ML Engineer + Backend Senior + Database Administrator
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import pickle
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import aiofiles
import asyncpg
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

Base = declarative_base()

class ModelStatus(str, Enum):
    """Model lifecycle status enumeration."""
    DRAFT = "draft"
    TRAINING = "training"
    VALIDATION = "validation"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class ModelType(str, Enum):
    """Model type enumeration."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    GENERATION = "generation"
    DETECTION = "detection"
    SEGMENTATION = "segmentation"
    RECOMMENDATION = "recommendation"
    FINGERPRINTING = "fingerprinting"

class MLFramework(str, Enum):
    """ML framework enumeration."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SCIKIT_LEARN = "scikit_learn"
    HUGGINGFACE = "huggingface"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    ONNX = "onnx"

@dataclass
class ModelMetadata:
    """Model metadata structure."""
    model_id: str
    name: str
    version: str
    description: str
    model_type: ModelType
    framework: MLFramework
    status: ModelStatus
    author: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    dataset_info: Dict[str, Any]
    hardware_requirements: Dict[str, Any]

class ModelRegistrySchema(Base):
    """Database schema for model registry."""
    __tablename__ = "ai_model_registry"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    model_type = Column(String(50), nullable=False)
    framework = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default=ModelStatus.DRAFT)
    author = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = Column(JSON)
    parameters = Column(JSON)
    metrics = Column(JSON)
    dataset_info = Column(JSON)
    hardware_requirements = Column(JSON)
    artifact_path = Column(String(500))
    checksum = Column(String(128))
    file_size = Column(Integer)
    is_active = Column(Boolean, default=True)

class ModelVersionSchema(Base):
    """Database schema for model versions."""
    __tablename__ = "ai_model_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    parent_version = Column(String(50))
    changelog = Column(Text)
    performance_delta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=False)
    is_stable = Column(Boolean, default=False)
    is_production = Column(Boolean, default=False)

class ModelRequest(BaseModel):
    """Model registration request schema."""
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=5000)
    model_type: ModelType
    framework: MLFramework
    author: str = Field(..., min_length=1, max_length=255)
    tags: Optional[List[str]] = Field(default_factory=list)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metrics: Optional[Dict[str, float]] = Field(default_factory=dict)
    dataset_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    hardware_requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        return v

class AIModelRegistry:
    """
    Central AI model registry for managing ML models.
    
    This class provides comprehensive model management including registration,
    versioning, metadata storage, and lifecycle management.
    """
    
    def __init__(self, db_connection: Optional[asyncpg.Connection] = None):
        """Initialize the AI Model Registry."""
        self.db_connection = db_connection
        self.models_cache = {}
        self.initialized = False
        
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the model registry.
        
        Returns:
            Dict[str, Any]: Initialization status
        """



        try:
            if not self.db_connection:
                # Database connection would be injected in production
                logger.warning("No database connection provided, using mock mode")
            
            # Create tables if they don't exist
            await self._create_tables()
            
            # Load existing models into cache
            await self._load_models_cache()
            
            self.initialized = True
            
            logger.info("AI Model Registry initialized successfully")
            return {
                "status": "success",
                "models_loaded": len(self.models_cache),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Model Registry: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def register_model(self, model_request: ModelRequest, 
                           artifact_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new ML model.
        
        Args:
            model_request: Model registration request
            artifact_path: Path to model artifacts
            
        Returns:
            Dict[str, Any]: Registration result
        """



        try:
            # Generate unique model ID
            model_id = self._generate_model_id(model_request.name, model_request.version)
            
            # Validate model doesn't already exist
            if await self._model_exists(model_id):
                return {
                    "status": "error",
                    "error": f"Model {model_id} already exists",
                    "model_id": model_id
                }
            
            # Calculate artifact checksum if provided
            checksum = None
            file_size = None
            if artifact_path:
                checksum, file_size = await self._calculate_artifact_info(artifact_path)
            
            # Create model metadata
            metadata = ModelMetadata(
                model_id=model_id,
                name=model_request.name,
                version=model_request.version,
                description=model_request.description or "",
                model_type=model_request.model_type,
                framework=model_request.framework,
                status=ModelStatus.DRAFT,
                author=model_request.author,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                tags=model_request.tags or [],
                parameters=model_request.parameters or {},
                metrics=model_request.metrics or {},
                dataset_info=model_request.dataset_info or {},
                hardware_requirements=model_request.hardware_requirements or {}
            )
            
            # Store in database
            await self._store_model_metadata(metadata, artifact_path, checksum, file_size)
            
            # Update cache
            self.models_cache[model_id] = metadata
            
            logger.info(f"Model {model_id} registered successfully")
            return {
                "status": "success",
                "model_id": model_id,
                "version": model_request.version,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to register model: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """
        Get model metadata by ID.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Optional[ModelMetadata]: Model metadata if found
        """



        try:
            # Check cache first
            if model_id in self.models_cache:
                return self.models_cache[model_id]
            
            # Query database
            metadata = await self._load_model_metadata(model_id)
            if metadata:
                self.models_cache[model_id] = metadata
                
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get model {model_id}: {str(e)}")
            return None
    
    async def list_models(self, 
                         model_type: Optional[ModelType] = None,
                         framework: Optional[MLFramework] = None,
                         status: Optional[ModelStatus] = None,
                         author: Optional[str] = None,
                         tags: Optional[List[str]] = None,
                         limit: int = 100,
                         offset: int = 0) -> Dict[str, Any]:
        """
        List models with filtering options.
        
        Args:
            model_type: Filter by model type
            framework: Filter by framework
            status: Filter by status
            author: Filter by author
            tags: Filter by tags
            limit: Maximum results to return
            offset: Results offset for pagination
            
        Returns:
            Dict[str, Any]: List of models with metadata
        """



        try:
            # Apply filters
            filtered_models = []
            for model_id, metadata in self.models_cache.items():
                if model_type and metadata.model_type != model_type:
                    continue
                if framework and metadata.framework != framework:
                    continue
                if status and metadata.status != status:
                    continue
                if author and metadata.author != author:
                    continue
                if tags and not set(tags).intersection(set(metadata.tags)):
                    continue
                    
                filtered_models.append(metadata)
            
            # Sort by creation date (newest first)
            filtered_models.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            total_count = len(filtered_models)
            paginated_models = filtered_models[offset:offset + limit]
            
            return {
                "status": "success",
                "models": [asdict(model) for model in paginated_models],
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def update_model_status(self, model_id: str, 
                                new_status: ModelStatus) -> Dict[str, Any]:
        """
        Update model status.
        
        Args:
            model_id: Model identifier
            new_status: New status to set
            
        Returns:
            Dict[str, Any]: Update result
        """



        try:
            # Validate model exists
            metadata = await self.get_model(model_id)
            if not metadata:
                return {
                    "status": "error",
                    "error": f"Model {model_id} not found"
                }
            
            # Update metadata
            metadata.status = new_status
            metadata.updated_at = datetime.utcnow()
            
            # Update database
            await self._update_model_metadata(metadata)
            
            # Update cache
            self.models_cache[model_id] = metadata
            
            logger.info(f"Model {model_id} status updated to {new_status}")
            return {
                "status": "success",
                "model_id": model_id,
                "new_status": new_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update model status: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def delete_model(self, model_id: str, 
                          hard_delete: bool = False) -> Dict[str, Any]:
        """
        Delete model (soft delete by default).
        
        Args:
            model_id: Model identifier
            hard_delete: Whether to perform hard delete
            
        Returns:
            Dict[str, Any]: Deletion result
        """



        try:
            # Validate model exists
            metadata = await self.get_model(model_id)
            if not metadata:
                return {
                    "status": "error",
                    "error": f"Model {model_id} not found"
                }
            
            if hard_delete:
                # Remove from database
                await self._delete_model_hard(model_id)
                # Remove from cache
                if model_id in self.models_cache:
                    del self.models_cache[model_id]
            else:
                # Soft delete - mark as archived
                metadata.status = ModelStatus.ARCHIVED
                metadata.updated_at = datetime.utcnow()
                await self._update_model_metadata(metadata)
                self.models_cache[model_id] = metadata
            
            logger.info(f"Model {model_id} deleted ({'hard' if hard_delete else 'soft'})")
            return {
                "status": "success",
                "model_id": model_id,
                "delete_type": "hard" if hard_delete else "soft",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete model: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_total_models_count(self) -> int:
        """Get total number of registered models."""



        return len([m for m in self.models_cache.values() 
                   if m.status != ModelStatus.ARCHIVED])
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the model registry.
        
        Returns:
            Dict[str, Any]: Health status
        """



        try:
            if not self.initialized:
                return {
                    "status": "unhealthy",
                    "error": "Registry not initialized"
                }
            
            # Basic health metrics
            total_models = len(self.models_cache)
            active_models = len([m for m in self.models_cache.values() 
                               if m.status == ModelStatus.PRODUCTION])
            
            return {
                "status": "healthy",
                "total_models": total_models,
                "active_models": active_models,
                "cache_size": len(self.models_cache),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Private helper methods
    
    def _generate_model_id(self, name: str, version: str) -> str:
        """Generate unique model ID."""
        base_id = f"{name}_{version}".replace(" ", "_").lower()
        # Add timestamp for uniqueness
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{base_id}_{timestamp}"
    
    async def _model_exists(self, model_id: str) -> bool:
        """Check if model exists."""
        # In production, this would query the database
        return model_id in self.models_cache
    
    async def _calculate_artifact_info(self, artifact_path: str) -> Tuple[str, int]:
        """Calculate checksum and file size for artifact."""



        try:
            path = Path(artifact_path)
            if not path.exists():
                return "", 0
            
            # Calculate SHA-256 checksum
            hash_sha256 = hashlib.sha256()
            async with aiofiles.open(artifact_path, 'rb') as f:
                async for chunk in f:
                    hash_sha256.update(chunk)
            
            checksum = hash_sha256.hexdigest()
            file_size = path.stat().st_size
            
            return checksum, file_size
            
        except Exception as e:
            logger.error(f"Failed to calculate artifact info: {str(e)}")
            return "", 0
    
    async def _create_tables(self):
        """Create database tables if they don't exist."""
        # In production, this would use SQLAlchemy/Alembic migrations
        logger.info("Database tables creation would be handled by migrations")
    
    async def _load_models_cache(self):
        """Load existing models into cache."""
        # In production, this would query the database
        logger.info("Loading models from database into cache")
    
    async def _store_model_metadata(self, metadata: ModelMetadata, 
                                  artifact_path: Optional[str],
                                  checksum: Optional[str],
                                  file_size: Optional[int]):
        """Store model metadata in database."""
        # In production, this would insert into database
        logger.info(f"Storing model metadata for {metadata.model_id}")
    
    async def _load_model_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """Load model metadata from database."""
        # In production, this would query the database
        return None
    
    async def _update_model_metadata(self, metadata: ModelMetadata):
        """Update model metadata in database."""
        logger.info(f"Updating model metadata for {metadata.model_id}")
    
    async def _delete_model_hard(self, model_id: str):
        """Hard delete model from database."""
        logger.info(f"Hard deleting model {model_id}")

class ModelVersionManager:
    """
    Model version management system.
    
    Handles version control, branching, and version comparison for ML models.
    """
    
    def __init__(self, model_registry: AIModelRegistry):
        """Initialize the version manager."""
        self.model_registry = model_registry
        self.version_cache = {}
        
    async def create_version(self, model_id: str, version: str,
                           parent_version: Optional[str] = None,
                           changelog: Optional[str] = None,
                           created_by: str = "system") -> Dict[str, Any]:
        """
        Create a new model version.
        
        Args:
            model_id: Model identifier
            version: Version string
            parent_version: Parent version if applicable
            changelog: Version changelog
            created_by: Version creator
            
        Returns:
            Dict[str, Any]: Version creation result
        """



        try:
            # Validate model exists
            model = await self.model_registry.get_model(model_id)
            if not model:
                return {
                    "status": "error",
                    "error": f"Model {model_id} not found"
                }
            
            # Create version record
            version_record = {
                "model_id": model_id,
                "version": version,
                "parent_version": parent_version,
                "changelog": changelog or "",
                "created_at": datetime.utcnow(),
                "created_by": created_by,
                "is_stable": False,
                "is_production": False
            }
            
            # Store version
            version_key = f"{model_id}_{version}"
            self.version_cache[version_key] = version_record
            
            logger.info(f"Created version {version} for model {model_id}")
            return {
                "status": "success",
                "model_id": model_id,
                "version": version,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create version: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_version_history(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Get version history for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            List[Dict[str, Any]]: Version history
        """



        try:
            versions = []
            for key, version_record in self.version_cache.items():
                if version_record["model_id"] == model_id:
                    versions.append(version_record)
            
            # Sort by creation date
            versions.sort(key=lambda x: x["created_at"], reverse=True)
            
            return versions
            
        except Exception as e:
            logger.error(f"Failed to get version history: {str(e)}")
            return []
    
    async def mark_version_stable(self, model_id: str, version: str) -> Dict[str, Any]:
        """Mark a version as stable."""



        try:
            version_key = f"{model_id}_{version}"
            if version_key in self.version_cache:
                self.version_cache[version_key]["is_stable"] = True
                logger.info(f"Marked version {version} as stable for model {model_id}")
                return {"status": "success"}
            else:
                return {"status": "error", "error": "Version not found"}
        except Exception as e:
            logger.error(f"Failed to mark version stable: {str(e)}")
            return {"status": "error", "error": str(e)}

class ModelMetadataStore:
    """
    Model metadata storage and retrieval system.
    
    Provides advanced metadata management including search, indexing,
    and metadata analytics.
    """
    
    def __init__(self):
        """Initialize the metadata store."""
        self.metadata_index = {}
        self.search_index = {}
        
    async def store_metadata(self, model_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store model metadata with indexing.
        
        Args:
            model_id: Model identifier
            metadata: Metadata dictionary
            
        Returns:
            Dict[str, Any]: Storage result
        """



        try:
            # Store metadata
            self.metadata_index[model_id] = {
                **metadata,
                "stored_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Update search index
            await self._update_search_index(model_id, metadata)
            
            logger.info(f"Stored metadata for model {model_id}")
            return {
                "status": "success",
                "model_id": model_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to store metadata: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def search_models(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Search models by metadata.
        
        Args:
            query: Search query
            filters: Additional filters
            
        Returns:
            List[str]: List of matching model IDs
        """



        try:
            matching_models = []
            query_lower = query.lower()
            
            for model_id, metadata in self.metadata_index.items():
                # Simple text search in name, description, and tags
                searchable_text = " ".join([
                    metadata.get("name", ""),
                    metadata.get("description", ""),
                    " ".join(metadata.get("tags", []))
                ]).lower()
                
                if query_lower in searchable_text:
                    # Apply filters if provided
                    if filters:
                        match = True
                        for key, value in filters.items():
                            if metadata.get(key) != value:
                                match = False
                                break
                        if match:
                            matching_models.append(model_id)
                    else:
                        matching_models.append(model_id)
            
            return matching_models
            
        except Exception as e:
            logger.error(f"Failed to search models: {str(e)}")
            return []
    
    async def _update_search_index(self, model_id: str, metadata: Dict[str, Any]):
        """Update search index for a model."""
        # Create searchable keywords
        keywords = []
        keywords.extend(metadata.get("tags", []))
        keywords.append(metadata.get("name", ""))
        keywords.append(metadata.get("model_type", ""))
        keywords.append(metadata.get("framework", ""))
        
        self.search_index[model_id] = [k.lower() for k in keywords if k]

class ModelArtifactManager:
    """
    Model artifact management system.
    
    Handles storage, retrieval, and versioning of model files and artifacts.
    """
    
    def __init__(self, storage_backend: str = "filesystem"):
        """Initialize the artifact manager."""
        self.storage_backend = storage_backend
        self.artifacts_cache = {}
        
    async def store_artifact(self, model_id: str, version: str,
                           artifact_data: bytes, 
                           artifact_type: str = "model") -> Dict[str, Any]:
        """
        Store model artifact.
        
        Args:
            model_id: Model identifier
            version: Model version
            artifact_data: Artifact binary data
            artifact_type: Type of artifact
            
        Returns:
            Dict[str, Any]: Storage result
        """



        try:
            # Generate artifact path
            artifact_path = self._generate_artifact_path(model_id, version, artifact_type)
            
            # Calculate checksum
            checksum = hashlib.sha256(artifact_data).hexdigest()
            
            # Store artifact (mock implementation)
            artifact_info = {
                "model_id": model_id,
                "version": version,
                "artifact_type": artifact_type,
                "path": artifact_path,
                "checksum": checksum,
                "size": len(artifact_data),
                "stored_at": datetime.utcnow()
            }
            
            artifact_key = f"{model_id}_{version}_{artifact_type}"
            self.artifacts_cache[artifact_key] = artifact_info
            
            logger.info(f"Stored artifact for {model_id} v{version}")
            return {
                "status": "success",
                "artifact_path": artifact_path,
                "checksum": checksum,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to store artifact: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def retrieve_artifact(self, model_id: str, version: str,
                              artifact_type: str = "model") -> Optional[bytes]:
        """
        Retrieve model artifact.
        
        Args:
            model_id: Model identifier
            version: Model version
            artifact_type: Type of artifact
            
        Returns:
            Optional[bytes]: Artifact data if found
        """



        try:
            artifact_key = f"{model_id}_{version}_{artifact_type}"
            if artifact_key in self.artifacts_cache:
                logger.info(f"Retrieved artifact for {model_id} v{version}")
                # In production, this would read from actual storage
                return b"mock_artifact_data"
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve artifact: {str(e)}")
            return None
    
    def _generate_artifact_path(self, model_id: str, version: str, artifact_type: str) -> str:
        """Generate artifact storage path."""



        return f"models/{model_id}/{version}/{artifact_type}.bin"
