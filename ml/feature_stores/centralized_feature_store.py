"""Centralized Feature Store - Enterprise Feature Management

High-performance feature store with versioning, validation, and real-time serving
for ML pipelines in the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class FeatureType(Enum):
    """Feature data types"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical" 
    TEXT = "text"
    TIMESTAMP = "timestamp"
    EMBEDDING = "embedding"
    BOOLEAN = "boolean"


class FeatureStatus(Enum):
    """Feature lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class FeatureSchema:
    """Feature schema definition"""
    name: str
    feature_type: FeatureType
    description: str
    source: str
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: FeatureStatus = FeatureStatus.DRAFT


@dataclass
class FeatureVersion:
    """Feature version metadata"""
    version_id: str
    feature_name: str
    version: str
    schema: FeatureSchema
    statistics: Dict[str, Any] = field(default_factory=dict)
    lineage: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    checksum: str = ""


@dataclass
class FeatureStoreConfig:
    """Feature store configuration"""
    store_path: str = "/tmp/ainflue_feature_store"
    cache_size: int = 1000
    version_retention_days: int = 90
    enable_monitoring: bool = True
    enable_validation: bool = True
    batch_size: int = 1000
    compression_enabled: bool = True


class CentralizedFeatureStore:
    """Enterprise-grade centralized feature store"""
    
    def __init__(self, config: FeatureStoreConfig = None):
        self.config = config or FeatureStoreConfig()
        self.features: Dict[str, FeatureSchema] = {}
        self.versions: Dict[str, List[FeatureVersion]] = {}
        self.feature_data: Dict[str, Any] = {}
        self.cache: Dict[str, Any] = {}
        self.monitoring_metrics: Dict[str, Any] = {}
        
        # Create store directory
        Path(self.config.store_path).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Feature store initialized at {self.config.store_path}")
    
    
    async def register_feature(self, schema: FeatureSchema) -> str:
        """Register a new feature with the store"""
        try:
            feature_id = f"{schema.name}_{int(time.time())}"
            
            # Validate schema
            if await self._validate_feature_schema(schema):
                self.features[schema.name] = schema
                
                # Create initial version
                version = FeatureVersion(
                    version_id=str(uuid.uuid4()),
                    feature_name=schema.name,
                    version="1.0.0",
                    schema=schema,
                    checksum=self._calculate_schema_checksum(schema)
                )
                
                if schema.name not in self.versions:
                    self.versions[schema.name] = []
                self.versions[schema.name].append(version)
                
                # Save to persistent storage
                await self._save_feature_metadata(schema.name)
                
                logger.info(f"Feature registered: {schema.name}")
                return feature_id
            else:
                raise ValueError(f"Feature schema validation failed for {schema.name}")
                
        except Exception as e:
            logger.error(f"Feature registration failed: {e}")
            raise
    
    
    async def store_feature_data(self, feature_name: str, data: Any, version: str = None) -> bool:
        """Store feature data with versioning"""
        try:
            if feature_name not in self.features:
                raise ValueError(f"Feature {feature_name} not registered")
            
            # Use latest version if not specified
            if version is None:
                version = self._get_latest_version(feature_name)
            
            # Validate data against schema
            if await self._validate_feature_data(feature_name, data):
                # Calculate data statistics
                stats = await self._calculate_statistics(data)
                
                # Store data
                storage_key = f"{feature_name}:{version}"
                self.feature_data[storage_key] = {
                    "data": data,
                    "timestamp": datetime.now(),
                    "statistics": stats,
                    "checksum": self._calculate_data_checksum(data)
                }
                
                # Update cache
                if len(self.cache) < self.config.cache_size:
                    self.cache[storage_key] = data
                
                # Save to persistent storage
                await self._save_feature_data(storage_key)
                
                logger.info(f"Feature data stored: {storage_key}")
                return True
            else:
                logger.error(f"Feature data validation failed for {feature_name}")
                return False
                
        except Exception as e:
            logger.error(f"Feature data storage failed: {e}")
            return False
    
    
    async def get_feature_data(self, feature_name: str, version: str = None) -> Optional[Any]:
        """Retrieve feature data by name and version"""
        try:
            if version is None:
                version = self._get_latest_version(feature_name)
            
            storage_key = f"{feature_name}:{version}"
            
            # Check cache first
            if storage_key in self.cache:
                logger.debug(f"Feature data retrieved from cache: {storage_key}")
                return self.cache[storage_key]
            
            # Load from storage
            if storage_key in self.feature_data:
                data = self.feature_data[storage_key]["data"]
                
                # Update cache
                if len(self.cache) < self.config.cache_size:
                    self.cache[storage_key] = data
                
                logger.debug(f"Feature data retrieved from storage: {storage_key}")
                return data
            
            logger.warning(f"Feature data not found: {storage_key}")
            return None
            
        except Exception as e:
            logger.error(f"Feature data retrieval failed: {e}")
            return None
    
    
    async def create_feature_version(self, feature_name: str, description: str = "") -> str:
        """Create a new version of a feature"""
        try:
            if feature_name not in self.features:
                raise ValueError(f"Feature {feature_name} not registered")
            
            current_versions = self.versions.get(feature_name, [])
            latest_version = current_versions[-1] if current_versions else None
            
            # Calculate new version number
            if latest_version:
                major, minor, patch = latest_version.version.split('.')
                new_version = f"{major}.{int(minor) + 1}.0"
            else:
                new_version = "1.0.0"
            
            # Create new version
            version = FeatureVersion(
                version_id=str(uuid.uuid4()),
                feature_name=feature_name,
                version=new_version,
                schema=self.features[feature_name],
                checksum=self._calculate_schema_checksum(self.features[feature_name])
            )
            
            self.versions[feature_name].append(version)
            
            # Save metadata
            await self._save_feature_metadata(feature_name)
            
            logger.info(f"New feature version created: {feature_name} v{new_version}")
            return new_version
            
        except Exception as e:
            logger.error(f"Feature version creation failed: {e}")
            raise
    
    
    async def get_feature_versions(self, feature_name: str) -> List[FeatureVersion]:
        """Get all versions of a feature"""
        return self.versions.get(feature_name, [])
    
    
    async def get_feature_statistics(self, feature_name: str, version: str = None) -> Dict[str, Any]:
        """Get statistics for a feature version"""
        try:
            if version is None:
                version = self._get_latest_version(feature_name)
            
            storage_key = f"{feature_name}:{version}"
            
            if storage_key in self.feature_data:
                return self.feature_data[storage_key]["statistics"]
            
            return {}
            
        except Exception as e:
            logger.error(f"Feature statistics retrieval failed: {e}")
            return {}
    
    
    async def cleanup_old_versions(self, days_old: int = None) -> int:
        """Clean up old feature versions"""
        if days_old is None:
            days_old = self.config.version_retention_days
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_count = 0
            
            for feature_name, versions in self.versions.items():
                # Keep at least one version
                if len(versions) <= 1:
                    continue
                
                # Sort by creation date  
                versions.sort(key=lambda v: v.created_at)
                
                # Remove old versions (keep latest)
                for version in versions[:-1]:
                    if version.created_at < cutoff_date:
                        # Remove from data storage
                        storage_key = f"{feature_name}:{version.version}"
                        if storage_key in self.feature_data:
                            del self.feature_data[storage_key]
                        if storage_key in self.cache:
                            del self.cache[storage_key]
                        
                        # Remove version
                        self.versions[feature_name].remove(version)
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old feature versions")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Feature cleanup failed: {e}")
            return 0
    
    
    def _get_latest_version(self, feature_name: str) -> str:
        """Get the latest version number for a feature"""
        versions = self.versions.get(feature_name, [])
        if versions:
            return versions[-1].version
        return "1.0.0"
    
    
    async def _validate_feature_schema(self, schema: FeatureSchema) -> bool:
        """Validate feature schema"""
        if not schema.name or not schema.feature_type:
            return False
        
        # Additional validation rules can be added here
        return True
    
    
    async def _validate_feature_data(self, feature_name: str, data: Any) -> bool:
        """Validate feature data against schema"""
        if not self.config.enable_validation:
            return True
        
        schema = self.features.get(feature_name)
        if not schema:
            return False
        
        # Basic validation - can be enhanced based on feature type
        if data is None:
            return False
        
        return True
    
    
    async def _calculate_statistics(self, data: Any) -> Dict[str, Any]:
        """Calculate basic statistics for feature data"""
        stats = {
            "count": 0,
            "null_count": 0,
            "calculated_at": datetime.now().isoformat()
        }
        
        try:
            if hasattr(data, '__len__'):
                stats["count"] = len(data)
            else:
                stats["count"] = 1
            
            # Additional statistics based on data type
            # This is a simplified implementation
            
        except Exception as e:
            logger.warning(f"Statistics calculation failed: {e}")
        
        return stats
    
    
    def _calculate_schema_checksum(self, schema: FeatureSchema) -> str:
        """Calculate checksum for schema"""
        schema_str = json.dumps(asdict(schema), default=str, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()
    
    
    def _calculate_data_checksum(self, data: Any) -> str:
        """Calculate checksum for data"""
        data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    
    async def _save_feature_metadata(self, feature_name: str):
        """Save feature metadata to persistent storage"""
        try:
            metadata_path = Path(self.config.store_path) / f"{feature_name}_metadata.json"
            
            metadata = {
                "schema": asdict(self.features[feature_name]),
                "versions": [asdict(v) for v in self.versions.get(feature_name, [])]
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, default=str, indent=2)
            
        except Exception as e:
            logger.error(f"Metadata save failed: {e}")
    
    
    async def _save_feature_data(self, storage_key: str):
        """Save feature data to persistent storage"""
        try:
            # In a production environment, this would use a proper database
            # For now, we keep data in memory with periodic saves
            pass
            
        except Exception as e:
            logger.error(f"Data save failed: {e}")