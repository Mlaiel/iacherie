"""🗄️ Model Version Controller - Enterprise ML Model Versioning
============================================================
Module: ml/model_registry/model_version_controller.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE MODEL VERSIONING
Advanced model versioning with semantic versioning and rollback capabilities
- Semantic versioning (major.minor.patch)
- Model lineage tracking
- Automated rollback mechanisms
- Performance comparison across versions
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import semver

logger = logging.getLogger(__name__)

class VersionType(Enum):
    """Version increment types"""
    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features, backward compatible
    PATCH = "patch"  # Bug fixes, backward compatible

class ModelStatus(Enum):
    """Model version status"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

@dataclass
class ModelVersion:
    """Model version metadata"""
    model_id: str
    version: str
    status: ModelStatus
    created_at: datetime
    performance_metrics: Dict[str, float]
    metadata: Dict[str, Any]
    artifacts_path: str
    parent_version: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    checksum: Optional[str] = None
    size_bytes: Optional[int] = None

@dataclass
class VersionComparison:
    """Version comparison result"""
    version_a: str
    version_b: str
    performance_diff: Dict[str, float]
    compatibility_score: float
    recommendation: str

class ModelVersionController:
    """
    Enterprise model version controller with semantic versioning
    """
    
    def __init__(self, registry_path -> None: str = "./model_registry") -> None:
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(exist_ok=True)
        self.versions_db: Dict[str, List[ModelVersion]] = {}
        self.active_versions: Dict[str, str] = {}  # model_id -> active_version
        
    async def create_version(
        self,
        model_id: str,
        artifacts_path: str,
        version_type: VersionType = VersionType.PATCH,
        performance_metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> ModelVersion:
        """
        Create new model version with semantic versioning
        """
        try:
            # Get current version
            current_version = await self.get_latest_version(model_id)
            
            # Calculate new version
            if current_version:
                new_version = self._increment_version(current_version.version, version_type)
                parent_version = current_version.version
            else:
                new_version = "1.0.0"
                parent_version = None
            
            # Calculate artifacts checksum
            checksum = await self._calculate_checksum(artifacts_path)
            size_bytes = await self._get_artifacts_size(artifacts_path)
            
            # Create version object
            version = ModelVersion(
                model_id=model_id,
                version=new_version,
                status=ModelStatus.DEVELOPMENT,
                created_at=datetime.utcnow(),
                performance_metrics=performance_metrics or {},
                metadata=metadata or {},
                artifacts_path=artifacts_path,
                parent_version=parent_version,
                tags=tags or [],
                checksum=checksum,
                size_bytes=size_bytes
            )
            
            # Store version
            if model_id not in self.versions_db:
                self.versions_db[model_id] = []
            
            self.versions_db[model_id].append(version)
            await self._persist_version(version)
            
            logger.info(f"Created version {new_version} for model {model_id}")
            return version
            
        except Exception as e:
            logger.error(f"Failed to create version for model {model_id}: {str(e)}")
            raise

    async def promote_version(
        self,
        model_id: str,
        version: str,
        target_status: ModelStatus
    ) -> bool:
        """
        Promote model version to target status
        """
        try:
            model_version = await self.get_version(model_id, version)
            if not model_version:
                raise ValueError(f"Version {version} not found for model {model_id}")
            
            # Validation based on target status
            if target_status == ModelStatus.PRODUCTION:
                if not await self._validate_production_readiness(model_version):
                    raise ValueError("Model version not ready for production")
                
                # Demote current production version
                current_prod = await self.get_production_version(model_id)
                if current_prod and current_prod.version != version:
                    current_prod.status = ModelStatus.DEPRECATED
                    await self._persist_version(current_prod)
                
                # Set as active version
                self.active_versions[model_id] = version
            
            # Update status
            model_version.status = target_status
            await self._persist_version(model_version)
            
            logger.info(f"Promoted model {model_id} version {version} to {target_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to promote version {version} for model {model_id}: {str(e)}")
            return False

    async def rollback_version(
        self,
        model_id: str,
        target_version: Optional[str] = None
    ) -> bool:
        """
        Rollback to previous stable version
        """
        try:
            if target_version:
                # Rollback to specific version
                version = await self.get_version(model_id, target_version)
                if not version:
                    raise ValueError(f"Target version {target_version} not found")
            else:
                # Rollback to previous stable version
                version = await self.get_previous_stable_version(model_id)
                if not version:
                    raise ValueError("No previous stable version found")
            
            # Promote target version to production
            await self.promote_version(model_id, version.version, ModelStatus.PRODUCTION)
            
            logger.info(f"Rolled back model {model_id} to version {version.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback model {model_id}: {str(e)}")
            return False

    async def compare_versions(
        self,
        model_id: str,
        version_a: str,
        version_b: str
    ) -> VersionComparison:
        """
        Compare two model versions
        """
        try:
            v_a = await self.get_version(model_id, version_a)
            v_b = await self.get_version(model_id, version_b)
            
            if not v_a or not v_b:
                raise ValueError("One or both versions not found")
            
            # Calculate performance differences
            performance_diff = {}
            for metric in set(v_a.performance_metrics.keys()) | set(v_b.performance_metrics.keys()):
                val_a = v_a.performance_metrics.get(metric, 0)
                val_b = v_b.performance_metrics.get(metric, 0)
                performance_diff[metric] = val_b - val_a
            
            # Calculate compatibility score
            compatibility_score = await self._calculate_compatibility(v_a, v_b)
            
            # Generate recommendation
            recommendation = await self._generate_upgrade_recommendation(v_a, v_b, performance_diff)
            
            return VersionComparison(
                version_a=version_a,
                version_b=version_b,
                performance_diff=performance_diff,
                compatibility_score=compatibility_score,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Failed to compare versions: {str(e)}")
            raise

    async def get_version(self, model_id: str, version: str) -> Optional[ModelVersion]:
        """Get specific model version"""
        if model_id in self.versions_db:
            for v in self.versions_db[model_id]:
                if v.version == version:
                    return v
        return None

    async def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
        """Get latest model version"""
        if model_id not in self.versions_db or not self.versions_db[model_id]:
            return None
        
        # Sort by semantic version
        versions = sorted(
            self.versions_db[model_id],
            key=lambda v: semver.VersionInfo.parse(v.version),
            reverse=True
        )
        return versions[0]

    async def get_production_version(self, model_id: str) -> Optional[ModelVersion]:
        """Get current production version"""
        if model_id in self.versions_db:
            for v in self.versions_db[model_id]:
                if v.status == ModelStatus.PRODUCTION:
                    return v
        return None

    async def get_previous_stable_version(self, model_id: str) -> Optional[ModelVersion]:
        """Get previous stable (production/staging) version"""
        if model_id not in self.versions_db:
            return None
        
        stable_versions = [
            v for v in self.versions_db[model_id]
            if v.status in [ModelStatus.PRODUCTION, ModelStatus.STAGING]
        ]
        
        if len(stable_versions) < 2:
            return None
        
        # Sort by creation date and return second latest
        stable_versions.sort(key=lambda v: v.created_at, reverse=True)
        return stable_versions[1]

    async def list_versions(
        self,
        model_id: str,
        status_filter: Optional[ModelStatus] = None
    ) -> List[ModelVersion]:
        """List all versions for a model"""
        if model_id not in self.versions_db:
            return []
        
        versions = self.versions_db[model_id]
        if status_filter:
            versions = [v for v in versions if v.status == status_filter]
        
        # Sort by semantic version
        return sorted(
            versions,
            key=lambda v: semver.VersionInfo.parse(v.version),
            reverse=True
        )

    def _increment_version(self, current: str, version_type: VersionType) -> str:
        """Increment semantic version"""
        version = semver.VersionInfo.parse(current)
        
        if version_type == VersionType.MAJOR:
            return str(version.bump_major())
        elif version_type == VersionType.MINOR:
            return str(version.bump_minor())
        else:  # PATCH
            return str(version.bump_patch())

    async def _calculate_checksum(self, artifacts_path: str) -> str:
        """Calculate artifacts checksum"""
        try:
            path = Path(artifacts_path)
            if path.is_file():
                with open(path, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()
            elif path.is_dir():
                # Calculate checksum for all files in directory
                checksums = []
                for file_path in sorted(path.rglob('*')):
                    if file_path.is_file():
                        with open(file_path, 'rb') as f:
                            checksums.append(hashlib.sha256(f.read()).hexdigest())
                combined = ''.join(checksums)
                return hashlib.sha256(combined.encode()).hexdigest()
            else:
                return ""
        except Exception:
            return ""

    async def _get_artifacts_size(self, artifacts_path: str) -> int:
        """Get total size of artifacts"""
        try:
            path = Path(artifacts_path)
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            else:
                return 0
        except Exception:
            return 0

    async def _validate_production_readiness(self, version: ModelVersion) -> bool:
        """Validate if version is ready for production"""
        # Check performance metrics
        required_metrics = ['accuracy', 'precision', 'recall']
        min_thresholds = {'accuracy': 0.95, 'precision': 0.90, 'recall': 0.90}
        
        for metric in required_metrics:
            if metric not in version.performance_metrics:
                return False
            if version.performance_metrics[metric] < min_thresholds[metric]:
                return False
        
        # Check artifacts exist
        if not Path(version.artifacts_path).exists():
            return False
        
        return True

    async def _calculate_compatibility(self, v_a: ModelVersion, v_b: ModelVersion) -> float:
        """Calculate compatibility score between versions"""
        # Simple compatibility based on version distance and metadata similarity
        try:
            version_a = semver.VersionInfo.parse(v_a.version)
            version_b = semver.VersionInfo.parse(v_b.version)
            
            # Major version difference reduces compatibility significantly
            if version_a.major != version_b.major:
                return 0.3
            elif version_a.minor != version_b.minor:
                return 0.7
            else:
                return 0.95
        except Exception:
            return 0.5

    async def _generate_upgrade_recommendation(
        self,
        v_a: ModelVersion,
        v_b: ModelVersion,
        performance_diff: Dict[str, float]
    ) -> str:
        """Generate upgrade recommendation based on comparison"""
        improvements = sum(1 for diff in performance_diff.values() if diff > 0)
        total_metrics = len(performance_diff)
        
        if improvements >= total_metrics * 0.8:
            return f"Strong recommendation: Version {v_b.version} shows significant improvements"
        elif improvements >= total_metrics * 0.5:
            return f"Moderate recommendation: Version {v_b.version} shows some improvements"
        else:
            return f"Caution: Version {v_b.version} may not provide better performance"

    async def _persist_version(self, version: ModelVersion) -> None:
        """Persist version metadata to storage"""
        version_file = self.registry_path / f"{version.model_id}_v{version.version}.json"
        
        version_data = {
            'model_id': version.model_id,
            'version': version.version,
            'status': version.status.value,
            'created_at': version.created_at.isoformat(),
            'performance_metrics': version.performance_metrics,
            'metadata': version.metadata,
            'artifacts_path': version.artifacts_path,
            'parent_version': version.parent_version,
            'tags': version.tags,
            'checksum': version.checksum,
            'size_bytes': version.size_bytes
        }
        
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)

# Usage Example
async def main() -> None:
    """Example usage of ModelVersionController"""
    controller = ModelVersionController()
    
    # Create new version
    version = await controller.create_version(
        model_id="content-classifier",
        artifacts_path="/models/content-classifier-v2",
        version_type=VersionType.MINOR,
        performance_metrics={
            'accuracy': 0.96,
            'precision': 0.94,
            'recall': 0.95,
            'f1_score': 0.945
        },
        metadata={'training_data_size': 100000, 'epochs': 50},
        tags=['production-ready', 'content-classification']
    )
    
    # Promote to production
    await controller.promote_version(
        model_id="content-classifier",
        version=version.version,
        target_status=ModelStatus.PRODUCTION
    )
    
    print(f"Created and promoted version {version.version}")

if __name__ == "__main__":
    asyncio.run(main())