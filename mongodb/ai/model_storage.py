"""MongoDB AI Model Storage
=========================

AI model storage, versioning, and metadata management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import json
import pickle
import base64
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
import gridfs

logger = logging.getLogger(__name__)

@dataclass
class ModelMetadata:
    """AI model metadata."""
    model_id: str
    name: str
    version: str
    model_type: str  # 'classification', 'regression', 'nlp', 'recommendation'
    framework: str   # 'tensorflow', 'pytorch', 'scikit-learn', 'transformers'
    created_at: datetime
    updated_at: datetime
    author: str
    description: str
    tags: List[str]
    metrics: Dict[str, float]
    hyperparameters: Dict[str, Any]
    training_data_info: Dict[str, Any]
    file_size_bytes: int
    status: str  # 'training', 'active', 'deprecated', 'archived'

@dataclass
class ModelVersion:
    """Model version information."""
    version: str
    created_at: datetime
    metrics: Dict[str, float]
    notes: str
    is_production: bool = False

class ModelStorage:
    """Advanced AI model storage with versioning and metadata management."""
    
    def __init__(self, client -> None: MongoClient, database_name -> None: str) -> None:
        """Initialize model storage.
        
        Args:
            client: MongoDB client instance
            database_name: Target database name
        """
        self.client = client
        self.database = client[database_name]
        
        # Collections
        self._models_collection = 'ai_models'
        self._model_versions_collection = 'ai_model_versions'
        
        # GridFS for large model files
        self._gridfs = gridfs.GridFS(self.database)
        
        # Initialize indexes
        self._initialize_indexes()
    
    def store_model(self, model_data: bytes, metadata: ModelMetadata) -> str:
        """Store AI model with metadata.
        
        Args:
            model_data: Serialized model data
            metadata: Model metadata
            
        Returns:
            GridFS file ID
        """
        try:
            # Store model file in GridFS
            file_id = self._gridfs.put(
                model_data,
                filename=f"{metadata.model_id}_v{metadata.version}",
                metadata={
                    'model_id': metadata.model_id,
                    'version': metadata.version,
                    'content_type': 'application/octet-stream'
                }
            )
            
            # Store metadata
            metadata_doc = asdict(metadata)
            metadata_doc['file_id'] = file_id
            metadata_doc['created_at'] = metadata.created_at
            metadata_doc['updated_at'] = metadata.updated_at
            
            self.database[self._models_collection].insert_one(metadata_doc)
            
            # Store version info
            version_doc = {
                'model_id': metadata.model_id,
                'version': metadata.version,
                'created_at': metadata.created_at,
                'metrics': metadata.metrics,
                'notes': metadata.description,
                'is_production': metadata.status == 'active',
                'file_id': file_id
            }
            
            self.database[self._model_versions_collection].insert_one(version_doc)
            
            logger.info(f"Stored model '{metadata.name}' version {metadata.version}")
            return str(file_id)
            
        except Exception as e:
            logger.error(f"Failed to store model: {e}")
            raise
    
    def load_model(self, model_id: str, version: str = None) -> Tuple[bytes, ModelMetadata]:
        """Load AI model and metadata.
        
        Args:
            model_id: Model identifier
            version: Specific version (latest if None)
            
        Returns:
            Tuple of (model_data, metadata)
        """
        try:
            # Find model metadata
            query = {'model_id': model_id}
            if version:
                query['version'] = version
            
            metadata_doc = self.database[self._models_collection].find_one(
                query,
                sort=[('created_at', -1)]  # Get latest if no version specified
            )
            
            if not metadata_doc:
                raise ValueError(f"Model '{model_id}' not found")
            
            # Load model file from GridFS
            file_id = metadata_doc['file_id']
            model_data = self._gridfs.get(file_id).read()
            
            # Create metadata object
            metadata_doc['created_at'] = metadata_doc.get('created_at', datetime.utcnow())
            metadata_doc['updated_at'] = metadata_doc.get('updated_at', datetime.utcnow())
            metadata = ModelMetadata(**{
                k: v for k, v in metadata_doc.items() 
                if k in ModelMetadata.__dataclass_fields__
            })
            
            logger.info(f"Loaded model '{model_id}' version {metadata.version}")
            return model_data, metadata
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def list_models(self, model_type: str = None, status: str = None) -> List[ModelMetadata]:
        """List stored models with optional filtering.
        
        Args:
            model_type: Filter by model type
            status: Filter by status
            
        Returns:
            List of model metadata
        """
        try:
            query = {}
            if model_type:
                query['model_type'] = model_type
            if status:
                query['status'] = status
            
            models = []
            for doc in self.database[self._models_collection].find(query):
                doc['created_at'] = doc.get('created_at', datetime.utcnow())
                doc['updated_at'] = doc.get('updated_at', datetime.utcnow())
                
                metadata = ModelMetadata(**{
                    k: v for k, v in doc.items() 
                    if k in ModelMetadata.__dataclass_fields__
                })
                models.append(metadata)
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def get_model_versions(self, model_id: str) -> List[ModelVersion]:
        """Get all versions of a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            List of model versions
        """
        try:
            versions = []
            for doc in self.database[self._model_versions_collection].find(
                {'model_id': model_id},
                sort=[('created_at', -1)]
            ):
                version = ModelVersion(
                    version=doc['version'],
                    created_at=doc['created_at'],
                    metrics=doc.get('metrics', {}),
                    notes=doc.get('notes', ''),
                    is_production=doc.get('is_production', False)
                )
                versions.append(version)
            
            return versions
            
        except Exception as e:
            logger.error(f"Failed to get model versions: {e}")
            return []
    
    def update_model_status(self, model_id: str, version: str, status: str) -> bool:
        """Update model status.
        
        Args:
            model_id: Model identifier
            version: Model version
            status: New status
            
        Returns:
            True if successful
        """
        try:
            result = self.database[self._models_collection].update_one(
                {'model_id': model_id, 'version': version},
                {
                    '$set': {
                        'status': status,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated model '{model_id}' v{version} status to '{status}'")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update model status: {e}")
            return False
    
    def delete_model(self, model_id: str, version: str = None) -> bool:
        """Delete model and associated data.
        
        Args:
            model_id: Model identifier
            version: Specific version (all versions if None)
            
        Returns:
            True if successful
        """
        try:
            query = {'model_id': model_id}
            if version:
                query['version'] = version
            
            # Find models to delete
            models_to_delete = list(self.database[self._models_collection].find(query))
            
            for model_doc in models_to_delete:
                # Delete GridFS file
                if 'file_id' in model_doc:
                    self._gridfs.delete(model_doc['file_id'])
                
                # Delete metadata
                self.database[self._models_collection].delete_one(
                    {'_id': model_doc['_id']}
                )
                
                # Delete version info
                self.database[self._model_versions_collection].delete_many({
                    'model_id': model_id,
                    'version': model_doc['version']
                })
            
            logger.info(f"Deleted model '{model_id}'" + (f" version {version}" if version else " (all versions)"))
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete model: {e}")
            return False
    
    def get_model_metrics_comparison(self, model_id: str) -> Dict[str, Any]:
        """Compare metrics across model versions.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Metrics comparison data
        """
        try:
            versions = self.get_model_versions(model_id)
            
            if not versions:
                return {}
            
            # Collect all metric names
            all_metrics = set()
            for version in versions:
                all_metrics.update(version.metrics.keys())
            
            # Create comparison data
            comparison = {
                'model_id': model_id,
                'versions': [],
                'metric_trends': {}
            }
            
            for version in versions:
                version_data = {
                    'version': version.version,
                    'created_at': version.created_at.isoformat(),
                    'metrics': version.metrics,
                    'is_production': version.is_production
                }
                comparison['versions'].append(version_data)
            
            # Calculate metric trends
            for metric_name in all_metrics:
                metric_values = []
                for version in reversed(versions):  # Chronological order
                    if metric_name in version.metrics:
                        metric_values.append({
                            'version': version.version,
                            'value': version.metrics[metric_name],
                            'created_at': version.created_at.isoformat()
                        })
                
                comparison['metric_trends'][metric_name] = metric_values
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to get model metrics comparison: {e}")
            return {}
    
    def _initialize_indexes(self) -> None:
        """Initialize database indexes for optimal performance."""
        try:
            # Models collection indexes
            self.database[self._models_collection].create_index([
                ('model_id', 1),
                ('version', 1)
            ], unique=True)
            
            self.database[self._models_collection].create_index([
                ('model_type', 1),
                ('status', 1)
            ])
            
            self.database[self._models_collection].create_index([
                ('created_at', -1)
            ])
            
            # Model versions collection indexes
            self.database[self._model_versions_collection].create_index([
                ('model_id', 1),
                ('version', 1)
            ])
            
            self.database[self._model_versions_collection].create_index([
                ('model_id', 1),
                ('created_at', -1)
            ])
            
            logger.debug("Initialized AI model storage indexes")
            
        except Exception as e:
            logger.warning(f"Failed to initialize model storage indexes: {e}")

# Global model storage instance
_default_model_storage: Optional[ModelStorage] = None

def get_model_storage(client: MongoClient, database_name: str) -> ModelStorage:
    """Get or create default model storage."""
    global _default_model_storage
    if _default_model_storage is None:
        _default_model_storage = ModelStorage(client, database_name)
    return _default_model_storage

__all__ = ['ModelStorage', 'ModelMetadata', 'ModelVersion', 'get_model_storage']