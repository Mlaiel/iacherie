"""📚 Feature Versioning Manager - Feature Evolution Control
=====================================================================
Module: ml/feature_stores/feature_versioning_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 FEATURE VERSIONING & BACKWARD COMPATIBILITY
Advanced feature versioning with backward compatibility management
- Semantic versioning pour feature evolution
- Backward compatibility validation et migration
- Feature schema evolution tracking
- Creator-specific versioning strategies
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import semver
from collections import defaultdict

# Configuration
logger = logging.getLogger(__name__)

class VersionType(Enum):
    """Types de versions"""
    
    MAJOR = "major"        # Breaking changes
    MINOR = "minor"        # New features, backward compatible
    PATCH = "patch"        # Bug fixes, backward compatible
    PRERELEASE = "prerelease"  # Alpha, beta, rc

class CompatibilityLevel(Enum):
    """Niveaux de compatibilité"""
    
    FULL = "full"                    # 100% compatible
    BACKWARD = "backward"            # Backward compatible only
    FORWARD = "forward"              # Forward compatible only
    NONE = "none"                    # Breaking changes
    MIGRATION_REQUIRED = "migration_required"  # Requires data migration

class FeatureChangeType(Enum):
    """Types de changements de features"""
    
    SCHEMA_CHANGE = "schema_change"
    DATA_TYPE_CHANGE = "data_type_change"
    COMPUTATION_CHANGE = "computation_change"
    DEPENDENCY_CHANGE = "dependency_change"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    BUG_FIX = "bug_fix"
    DEPRECATION = "deprecation"

@dataclass
class FeatureVersion:
    """Version d'une feature"""
    
    feature_name: str
    version: str  # Semantic version (e.g., "1.2.3")
    created_at: datetime
    created_by: str
    description: str
    change_type: FeatureChangeType
    compatibility: CompatibilityLevel
    schema_hash: str
    data_sample_hash: str
    dependencies: List[str] = field(default_factory=list)
    creator_types: List[str] = field(default_factory=list)
    migration_required: bool = False
    migration_script: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'feature_name': self.feature_name,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'description': self.description,
            'change_type': self.change_type.value,
            'compatibility': self.compatibility.value,
            'schema_hash': self.schema_hash,
            'data_sample_hash': self.data_sample_hash,
            'dependencies': self.dependencies,
            'creator_types': self.creator_types,
            'migration_required': self.migration_required,
            'migration_script': self.migration_script,
            'performance_metrics': self.performance_metrics,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureVersion':
        return cls(
            feature_name=data['feature_name'],
            version=data['version'],
            created_at=datetime.fromisoformat(data['created_at']),
            created_by=data['created_by'],
            description=data['description'],
            change_type=FeatureChangeType(data['change_type']),
            compatibility=CompatibilityLevel(data['compatibility']),
            schema_hash=data['schema_hash'],
            data_sample_hash=data['data_sample_hash'],
            dependencies=data.get('dependencies', []),
            creator_types=data.get('creator_types', []),
            migration_required=data.get('migration_required', False),
            migration_script=data.get('migration_script'),
            performance_metrics=data.get('performance_metrics', {}),
            metadata=data.get('metadata', {})
        )

@dataclass
class VersionCompatibilityResult:
    """Résultat de vérification de compatibilité"""
    
    source_version: str
    target_version: str
    compatibility_level: CompatibilityLevel
    issues: List[str] = field(default_factory=list)
    migration_path: List[str] = field(default_factory=list)
    estimated_migration_time: Optional[float] = None  # en heures
    breaking_changes: List[str] = field(default_factory=list)

@dataclass
class VersioningStrategy:
    """Stratégie de versioning"""
    
    auto_increment: bool = True
    allow_breaking_changes: bool = True
    require_migration_scripts: bool = True
    enforce_semantic_versioning: bool = True
    creator_approval_required: bool = False
    max_concurrent_versions: int = 5
    deprecation_notice_days: int = 30

class FeatureSchema:
    """Schéma d'une feature"""
    
    def __init__(self, feature_data: Any):
        self.schema = self._extract_schema(feature_data)
        self.hash = self._compute_hash()
    
    def _extract_schema(self, data: Any) -> Dict[str, Any]:
        """Extraire le schéma des données"""
        
        if isinstance(data, np.ndarray):
            return {
                'type': 'numpy_array',
                'dtype': str(data.dtype),
                'shape': data.shape,
                'ndim': data.ndim
            }
        elif isinstance(data, pd.DataFrame):
            return {
                'type': 'dataframe',
                'columns': list(data.columns),
                'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
                'shape': data.shape
            }
        elif isinstance(data, pd.Series):
            return {
                'type': 'series',
                'dtype': str(data.dtype),
                'length': len(data),
                'name': data.name
            }
        elif isinstance(data, dict):
            return {
                'type': 'dict',
                'keys': list(data.keys()),
                'value_types': {k: type(v).__name__ for k, v in data.items()}
            }
        elif isinstance(data, list):
            return {
                'type': 'list',
                'length': len(data),
                'element_type': type(data[0]).__name__ if data else None
            }
        else:
            return {
                'type': type(data).__name__,
                'value': str(data)[:100]  # Limité pour hash
            }
    
    def _compute_hash(self) -> str:
        """Calculer le hash du schéma"""
        schema_str = json.dumps(self.schema, sort_keys=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()[:16]
    
    def is_compatible_with(self, other_schema: 'FeatureSchema') -> CompatibilityLevel:
        """Vérifier la compatibilité avec un autre schéma"""
        
        if self.hash == other_schema.hash:
            return CompatibilityLevel.FULL
        
        # Vérifications spécifiques par type
        if self.schema['type'] != other_schema.schema['type']:
            return CompatibilityLevel.NONE
        
        if self.schema['type'] == 'numpy_array':
            return self._check_numpy_compatibility(other_schema)
        elif self.schema['type'] == 'dataframe':
            return self._check_dataframe_compatibility(other_schema)
        elif self.schema['type'] == 'dict':
            return self._check_dict_compatibility(other_schema)
        else:
            return CompatibilityLevel.BACKWARD
    
    def _check_numpy_compatibility(self, other: 'FeatureSchema') -> CompatibilityLevel:
        """Vérifier compatibilité numpy array"""
        
        # Shape change = breaking
        if self.schema['shape'] != other.schema['shape']:
            return CompatibilityLevel.NONE
        
        # dtype change peut être acceptable
        old_dtype = np.dtype(self.schema['dtype'])
        new_dtype = np.dtype(other.schema['dtype'])
        
        if old_dtype == new_dtype:
            return CompatibilityLevel.FULL
        elif np.can_cast(old_dtype, new_dtype):
            return CompatibilityLevel.FORWARD
        elif np.can_cast(new_dtype, old_dtype):
            return CompatibilityLevel.BACKWARD
        else:
            return CompatibilityLevel.MIGRATION_REQUIRED
    
    def _check_dataframe_compatibility(self, other: 'FeatureSchema') -> CompatibilityLevel:
        """Vérifier compatibilité DataFrame"""
        
        old_cols = set(self.schema['columns'])
        new_cols = set(other.schema['columns'])
        
        if old_cols == new_cols:
            # Vérifier les types de colonnes
            for col in old_cols:
                if self.schema['dtypes'][col] != other.schema['dtypes'][col]:
                    return CompatibilityLevel.MIGRATION_REQUIRED
            return CompatibilityLevel.FULL
        
        elif old_cols.issubset(new_cols):
            return CompatibilityLevel.FORWARD  # Nouvelles colonnes ajoutées
        
        elif new_cols.issubset(old_cols):
            return CompatibilityLevel.BACKWARD  # Colonnes supprimées
        
        else:
            return CompatibilityLevel.MIGRATION_REQUIRED
    
    def _check_dict_compatibility(self, other: 'FeatureSchema') -> CompatibilityLevel:
        """Vérifier compatibilité dictionnaire"""
        
        old_keys = set(self.schema['keys'])
        new_keys = set(other.schema['keys'])
        
        if old_keys == new_keys:
            return CompatibilityLevel.FULL
        elif old_keys.issubset(new_keys):
            return CompatibilityLevel.FORWARD
        elif new_keys.issubset(old_keys):
            return CompatibilityLevel.BACKWARD
        else:
            return CompatibilityLevel.MIGRATION_REQUIRED

class FeatureVersioningManager:
    """
    📚 Feature Versioning Manager
    
    Gestionnaire de versions avec:
    - Semantic versioning automatique
    - Validation de compatibilité
    - Migration automatique des données
    - Creator-specific versioning strategies
    """
    
    def __init__(
        self,
        storage_path: str = "data/feature_versions",
        default_strategy: Optional[VersioningStrategy] = None,
        enable_auto_migration: bool = True,
        max_version_history: int = 100
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.default_strategy = default_strategy or VersioningStrategy()
        self.enable_auto_migration = enable_auto_migration
        self.max_version_history = max_version_history
        
        # Stockage des versions
        self.feature_versions: Dict[str, List[FeatureVersion]] = defaultdict(list)
        self.current_versions: Dict[str, str] = {}  # feature_name -> version
        
        # Stratégies par creator type
        self.creator_strategies: Dict[str, VersioningStrategy] = {
            'musician': VersioningStrategy(
                auto_increment=True,
                allow_breaking_changes=False,  # Stability important
                require_migration_scripts=True,
                creator_approval_required=True
            ),
            'blogger': VersioningStrategy(
                auto_increment=True,
                allow_breaking_changes=True,
                require_migration_scripts=False,  # Plus flexible
                max_concurrent_versions=10
            ),
            'photographer': VersioningStrategy(
                auto_increment=True,
                allow_breaking_changes=True,
                require_migration_scripts=True,
                deprecation_notice_days=7  # Plus rapide
            )
        }
        
        # Cache pour optimisation
        self.compatibility_cache: Dict[str, VersionCompatibilityResult] = {}
        self.schema_cache: Dict[str, FeatureSchema] = {}
        
        # Chargement des versions existantes
        asyncio.create_task(self._load_existing_versions())
        
        logger.info("📚 Feature Versioning Manager initialized")
    
    async def create_version(
        self,
        feature_name: str,
        feature_data: Any,
        description: str,
        created_by: str,
        creator_types: Optional[List[str]] = None,
        change_type: Optional[FeatureChangeType] = None,
        version_type: Optional[VersionType] = None,
        migration_script: Optional[str] = None
    ) -> FeatureVersion:
        """Créer une nouvelle version d'une feature"""
        
        creator_types = creator_types or []
        
        # Déterminer la stratégie de versioning
        strategy = self._get_versioning_strategy(creator_types)
        
        # Calculer le schéma et hash
        schema = FeatureSchema(feature_data)
        data_hash = self._compute_data_hash(feature_data)
        
        # Déterminer la nouvelle version
        current_version = self.current_versions.get(feature_name, "0.0.0")
        
        if version_type is None:
            version_type = await self._auto_determine_version_type(
                feature_name, schema, change_type
            )
        
        new_version = self._increment_version(current_version, version_type)
        
        # Vérifier les compatibilités
        compatibility = await self._check_compatibility_with_previous(
            feature_name, schema
        )
        
        # Validation selon la stratégie
        if not strategy.allow_breaking_changes and compatibility == CompatibilityLevel.NONE:
            raise ValueError(f"Breaking changes not allowed for feature {feature_name}")
        
        if strategy.require_migration_scripts and compatibility == CompatibilityLevel.MIGRATION_REQUIRED:
            if not migration_script:
                raise ValueError(f"Migration script required for feature {feature_name}")
        
        # Créer la version
        feature_version = FeatureVersion(
            feature_name=feature_name,
            version=new_version,
            created_at=datetime.now(),
            created_by=created_by,
            description=description,
            change_type=change_type or FeatureChangeType.SCHEMA_CHANGE,
            compatibility=compatibility,
            schema_hash=schema.hash,
            data_sample_hash=data_hash,
            creator_types=creator_types,
            migration_required=(compatibility == CompatibilityLevel.MIGRATION_REQUIRED),
            migration_script=migration_script,
            performance_metrics=await self._compute_performance_metrics(feature_data)
        )
        
        # Stocker la version
        self.feature_versions[feature_name].append(feature_version)
        self.current_versions[feature_name] = new_version
        self.schema_cache[f"{feature_name}_{new_version}"] = schema
        
        # Nettoyage des anciennes versions
        await self._cleanup_old_versions(feature_name, strategy)
        
        # Persister
        await self._persist_version(feature_version)
        
        logger.info(f"📚 Created version {new_version} for feature {feature_name}")
        return feature_version
    
    async def get_feature_version(
        self,
        feature_name: str,
        version: Optional[str] = None
    ) -> Optional[FeatureVersion]:
        """Récupérer une version spécifique d'une feature"""
        
        if feature_name not in self.feature_versions:
            return None
        
        versions = self.feature_versions[feature_name]
        
        if version is None:
            # Dernière version
            return versions[-1] if versions else None
        
        # Version spécifique
        for v in versions:
            if v.version == version:
                return v
        
        return None
    
    async def list_feature_versions(
        self,
        feature_name: str,
        include_deprecated: bool = False
    ) -> List[FeatureVersion]:
        """Lister toutes les versions d'une feature"""
        
        versions = self.feature_versions.get(feature_name, [])
        
        if not include_deprecated:
            # Filtrer les versions dépréciées
            active_versions = []
            for version in versions:
                # Vérifier si la version est dépréciée
                deprecation_date = version.metadata.get('deprecated_at')
                if not deprecation_date:
                    active_versions.append(version)
                else:
                    deprecation_dt = datetime.fromisoformat(deprecation_date)
                    if datetime.now() - deprecation_dt < timedelta(days=30):
                        active_versions.append(version)  # Garde 30 jours après dépréciation
            return active_versions
        
        return versions
    
    async def check_compatibility(
        self,
        feature_name: str,
        source_version: str,
        target_version: str
    ) -> VersionCompatibilityResult:
        """Vérifier la compatibilité entre deux versions"""
        
        cache_key = f"{feature_name}_{source_version}_{target_version}"
        if cache_key in self.compatibility_cache:
            return self.compatibility_cache[cache_key]
        
        # Récupérer les versions
        source_v = await self.get_feature_version(feature_name, source_version)
        target_v = await self.get_feature_version(feature_name, target_version)
        
        if not source_v or not target_v:
            result = VersionCompatibilityResult(
                source_version=source_version,
                target_version=target_version,
                compatibility_level=CompatibilityLevel.NONE,
                issues=["Version not found"]
            )
            return result
        
        # Vérifier la compatibilité des schémas
        source_schema = self.schema_cache.get(f"{feature_name}_{source_version}")
        target_schema = self.schema_cache.get(f"{feature_name}_{target_version}")
        
        if source_schema and target_schema:
            compatibility = source_schema.is_compatible_with(target_schema)
        else:
            compatibility = target_v.compatibility
        
        # Calculer le chemin de migration
        migration_path = await self._calculate_migration_path(
            feature_name, source_version, target_version
        )
        
        # Analyser les changements breaking
        breaking_changes = []
        if compatibility == CompatibilityLevel.NONE:
            breaking_changes = await self._analyze_breaking_changes(source_v, target_v)
        
        result = VersionCompatibilityResult(
            source_version=source_version,
            target_version=target_version,
            compatibility_level=compatibility,
            migration_path=migration_path,
            breaking_changes=breaking_changes,
            estimated_migration_time=len(migration_path) * 0.5  # 30min par étape
        )
        
        # Cache le résultat
        self.compatibility_cache[cache_key] = result
        return result
    
    async def migrate_feature_data(
        self,
        feature_name: str,
        data: Any,
        source_version: str,
        target_version: str
    ) -> Any:
        """Migrer des données d'une version à une autre"""
        
        if source_version == target_version:
            return data
        
        # Vérifier la compatibilité
        compatibility = await self.check_compatibility(
            feature_name, source_version, target_version
        )
        
        if compatibility.compatibility_level == CompatibilityLevel.FULL:
            return data
        
        if not compatibility.migration_path:
            raise ValueError(f"No migration path available from {source_version} to {target_version}")
        
        # Appliquer les migrations étape par étape
        current_data = data
        current_version = source_version
        
        for next_version in compatibility.migration_path:
            next_feature_version = await self.get_feature_version(feature_name, next_version)
            
            if next_feature_version and next_feature_version.migration_script:
                # Exécuter le script de migration
                current_data = await self._execute_migration_script(
                    next_feature_version.migration_script,
                    current_data,
                    current_version,
                    next_version
                )
            else:
                # Migration automatique basique
                current_data = await self._auto_migrate_data(
                    current_data, current_version, next_version
                )
            
            current_version = next_version
        
        logger.info(f"🔄 Migrated {feature_name} data from {source_version} to {target_version}")
        return current_data
    
    async def deprecate_version(
        self,
        feature_name: str,
        version: str,
        reason: str,
        replacement_version: Optional[str] = None
    ) -> bool:
        """Déprécier une version"""
        
        feature_version = await self.get_feature_version(feature_name, version)
        if not feature_version:
            return False
        
        # Marquer comme dépréciée
        feature_version.metadata['deprecated_at'] = datetime.now().isoformat()
        feature_version.metadata['deprecation_reason'] = reason
        if replacement_version:
            feature_version.metadata['replacement_version'] = replacement_version
        
        # Persister
        await self._persist_version(feature_version)
        
        logger.info(f"⚠️ Deprecated version {version} of feature {feature_name}")
        return True
    
    def _get_versioning_strategy(self, creator_types: List[str]) -> VersioningStrategy:
        """Obtenir la stratégie de versioning appropriée"""
        
        if not creator_types:
            return self.default_strategy
        
        # Prendre la stratégie du premier creator type trouvé
        for creator_type in creator_types:
            if creator_type in self.creator_strategies:
                return self.creator_strategies[creator_type]
        
        return self.default_strategy
    
    async def _auto_determine_version_type(
        self,
        feature_name: str,
        schema: FeatureSchema,
        change_type: Optional[FeatureChangeType]
    ) -> VersionType:
        """Déterminer automatiquement le type de version"""
        
        if not change_type:
            return VersionType.MINOR
        
        # Règles pour déterminer le type de version
        if change_type in [FeatureChangeType.SCHEMA_CHANGE, FeatureChangeType.DATA_TYPE_CHANGE]:
            # Vérifier si c'est breaking
            compatibility = await self._check_compatibility_with_previous(feature_name, schema)
            if compatibility == CompatibilityLevel.NONE:
                return VersionType.MAJOR
            else:
                return VersionType.MINOR
        
        elif change_type == FeatureChangeType.BUG_FIX:
            return VersionType.PATCH
        
        elif change_type == FeatureChangeType.PERFORMANCE_IMPROVEMENT:
            return VersionType.PATCH
        
        else:
            return VersionType.MINOR
    
    async def _check_compatibility_with_previous(
        self,
        feature_name: str,
        new_schema: FeatureSchema
    ) -> CompatibilityLevel:
        """Vérifier la compatibilité avec la version précédente"""
        
        versions = self.feature_versions.get(feature_name, [])
        if not versions:
            return CompatibilityLevel.FULL
        
        last_version = versions[-1]
        last_schema = self.schema_cache.get(f"{feature_name}_{last_version.version}")
        
        if last_schema:
            return last_schema.is_compatible_with(new_schema)
        else:
            return CompatibilityLevel.BACKWARD
    
    def _increment_version(self, current_version: str, version_type: VersionType) -> str:
        """Incrémenter une version selon le type"""
        
        try:
            if version_type == VersionType.MAJOR:
                return semver.bump_major(current_version)
            elif version_type == VersionType.MINOR:
                return semver.bump_minor(current_version)
            elif version_type == VersionType.PATCH:
                return semver.bump_patch(current_version)
            else:
                return semver.bump_minor(current_version)
        except:
            # Fallback si semver échoue
            parts = current_version.split('.')
            if len(parts) != 3:
                return "1.0.0"
            
            major, minor, patch = map(int, parts)
            
            if version_type == VersionType.MAJOR:
                return f"{major + 1}.0.0"
            elif version_type == VersionType.MINOR:
                return f"{major}.{minor + 1}.0"
            else:
                return f"{major}.{minor}.{patch + 1}"
    
    def _compute_data_hash(self, data: Any) -> str:
        """Calculer le hash d'un échantillon de données"""
        
        try:
            # Prendre un échantillon pour le hash
            if isinstance(data, np.ndarray):
                sample = data.flatten()[:100] if data.size > 100 else data.flatten()
            elif isinstance(data, pd.DataFrame):
                sample = data.head(10).to_dict()
            elif isinstance(data, pd.Series):
                sample = data.head(10).tolist()
            elif isinstance(data, (list, tuple)):
                sample = data[:10]
            elif isinstance(data, dict):
                sample = {k: v for i, (k, v) in enumerate(data.items()) if i < 10}
            else:
                sample = str(data)[:100]
            
            sample_str = json.dumps(sample, default=str, sort_keys=True)
            return hashlib.sha256(sample_str.encode()).hexdigest()[:16]
        except:
            return "unknown"
    
    async def _compute_performance_metrics(self, data: Any) -> Dict[str, float]:
        """Calculer les métriques de performance"""
        
        metrics = {}
        
        try:
            # Taille
            if hasattr(data, '__sizeof__'):
                metrics['size_bytes'] = data.__sizeof__()
            
            # Métriques spécifiques par type
            if isinstance(data, np.ndarray):
                metrics['memory_usage'] = data.nbytes
                metrics['shape_complexity'] = np.prod(data.shape)
                metrics['sparsity'] = float(np.count_nonzero(data == 0) / data.size)
            
            elif isinstance(data, pd.DataFrame):
                metrics['memory_usage'] = data.memory_usage(deep=True).sum()
                metrics['row_count'] = len(data)
                metrics['column_count'] = len(data.columns)
                metrics['null_ratio'] = data.isnull().sum().sum() / (len(data) * len(data.columns))
            
            elif isinstance(data, pd.Series):
                metrics['memory_usage'] = data.memory_usage(deep=True)
                metrics['length'] = len(data)
                metrics['null_ratio'] = data.isnull().sum() / len(data)
            
        except Exception as e:
            logger.warning(f"Failed to compute performance metrics: {e}")
        
        return metrics
    
    async def _calculate_migration_path(
        self,
        feature_name: str,
        source_version: str,
        target_version: str
    ) -> List[str]:
        """Calculer le chemin de migration entre deux versions"""
        
        versions = self.feature_versions.get(feature_name, [])
        if not versions:
            return []
        
        # Trouver les indices des versions
        source_idx = None
        target_idx = None
        
        for i, v in enumerate(versions):
            if v.version == source_version:
                source_idx = i
            if v.version == target_version:
                target_idx = i
        
        if source_idx is None or target_idx is None:
            return []
        
        # Construire le chemin
        if source_idx < target_idx:
            # Migration vers version plus récente
            path = [versions[i].version for i in range(source_idx + 1, target_idx + 1)]
        else:
            # Migration vers version plus ancienne (downgrade)
            path = [versions[i].version for i in range(source_idx - 1, target_idx - 1, -1)]
        
        return path
    
    async def _analyze_breaking_changes(
        self,
        source_version: FeatureVersion,
        target_version: FeatureVersion
    ) -> List[str]:
        """Analyser les changements breaking entre deux versions"""
        
        breaking_changes = []
        
        # Comparer les schémas
        if source_version.schema_hash != target_version.schema_hash:
            breaking_changes.append("Schema structure changed")
        
        # Comparer les dépendances
        source_deps = set(source_version.dependencies)
        target_deps = set(target_version.dependencies)
        
        removed_deps = source_deps - target_deps
        if removed_deps:
            breaking_changes.append(f"Dependencies removed: {', '.join(removed_deps)}")
        
        # Analyser le type de changement
        if target_version.change_type in [
            FeatureChangeType.SCHEMA_CHANGE,
            FeatureChangeType.DATA_TYPE_CHANGE
        ]:
            breaking_changes.append(f"Breaking change type: {target_version.change_type.value}")
        
        return breaking_changes
    
    async def _execute_migration_script(
        self,
        script: str,
        data: Any,
        source_version: str,
        target_version: str
    ) -> Any:
        """Exécuter un script de migration"""
        
        # Créer un environnement sécurisé pour l'exécution
        local_vars = {
            'data': data,
            'source_version': source_version,
            'target_version': target_version,
            'np': np,
            'pd': pd
        }
        
        try:
            exec(script, {}, local_vars)
            return local_vars['data']
        except Exception as e:
            logger.error(f"Migration script failed: {e}")
            raise
    
    async def _auto_migrate_data(
        self,
        data: Any,
        source_version: str,
        target_version: str
    ) -> Any:
        """Migration automatique basique"""
        
        # Migration simple - pas de transformation
        # Dans un cas réel, on implémenterait des règles spécifiques
        logger.debug(f"Auto-migrating data from {source_version} to {target_version}")
        return data
    
    async def _cleanup_old_versions(
        self,
        feature_name: str,
        strategy: VersioningStrategy
    ):
        """Nettoyer les anciennes versions"""
        
        versions = self.feature_versions[feature_name]
        
        if len(versions) > strategy.max_concurrent_versions:
            # Garder les N dernières versions
            to_keep = versions[-strategy.max_concurrent_versions:]
            self.feature_versions[feature_name] = to_keep
            
            logger.debug(f"🧹 Cleaned up old versions for {feature_name}")
    
    async def _persist_version(self, version: FeatureVersion):
        """Persister une version"""
        
        version_file = self.storage_path / f"{version.feature_name}_{version.version}.json"
        
        with open(version_file, 'w') as f:
            json.dump(version.to_dict(), f, indent=2)
    
    async def _load_existing_versions(self):
        """Charger les versions existantes"""
        
        if not self.storage_path.exists():
            return
        
        for version_file in self.storage_path.glob("*.json"):
            try:
                with open(version_file, 'r') as f:
                    data = json.load(f)
                    version = FeatureVersion.from_dict(data)
                    
                    self.feature_versions[version.feature_name].append(version)
                    
                    # Mettre à jour la version courante
                    current = self.current_versions.get(version.feature_name, "0.0.0")
                    if semver.compare(version.version, current) > 0:
                        self.current_versions[version.feature_name] = version.version
                        
            except Exception as e:
                logger.warning(f"Failed to load version file {version_file}: {e}")
        
        logger.info(f"📚 Loaded {sum(len(v) for v in self.feature_versions.values())} feature versions")
    
    async def get_versioning_analytics(self) -> Dict[str, Any]:
        """Obtenir les analytics de versioning"""
        
        total_features = len(self.feature_versions)
        total_versions = sum(len(versions) for versions in self.feature_versions.values())
        
        # Analyse des types de changements
        change_type_stats = defaultdict(int)
        compatibility_stats = defaultdict(int)
        
        for versions in self.feature_versions.values():
            for version in versions:
                change_type_stats[version.change_type.value] += 1
                compatibility_stats[version.compatibility.value] += 1
        
        # Features avec le plus de versions
        version_counts = {
            name: len(versions)
            for name, versions in self.feature_versions.items()
        }
        most_versioned = sorted(
            version_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Taux de migration requis
        migration_required = sum(
            sum(1 for v in versions if v.migration_required)
            for versions in self.feature_versions.values()
        )
        migration_rate = migration_required / total_versions if total_versions > 0 else 0
        
        return {
            'summary': {
                'total_features': total_features,
                'total_versions': total_versions,
                'avg_versions_per_feature': total_versions / total_features if total_features > 0 else 0,
                'migration_required_rate': migration_rate
            },
            'change_types': dict(change_type_stats),
            'compatibility_levels': dict(compatibility_stats),
            'most_versioned_features': most_versioned,
            'strategies': {
                creator_type: strategy.__dict__
                for creator_type, strategy in self.creator_strategies.items()
            }
        }

# Usage Example
async def main():
    """Exemple d'utilisation du Feature Versioning Manager"""
    
    manager = FeatureVersioningManager(
        storage_path="data/feature_versions",
        enable_auto_migration=True
    )
    
    # Créer des versions de features
    feature_data_v1 = np.random.rand(100)
    
    version_v1 = await manager.create_version(
        feature_name="user_engagement_score",
        feature_data=feature_data_v1,
        description="Initial version of user engagement scoring",
        created_by="data_scientist_1",
        creator_types=["musician"],
        change_type=FeatureChangeType.SCHEMA_CHANGE
    )
    
    print(f"Created version: {version_v1.version}")
    
    # Nouvelle version avec changement
    feature_data_v2 = np.random.rand(200)  # Taille différente = breaking change
    
    version_v2 = await manager.create_version(
        feature_name="user_engagement_score",
        feature_data=feature_data_v2,
        description="Extended engagement score with more features",
        created_by="data_scientist_2",
        creator_types=["musician"],
        change_type=FeatureChangeType.SCHEMA_CHANGE,
        migration_script="""
# Migration script example
import numpy as np
if len(data) == 100:
    # Extend with zeros
    data = np.concatenate([data, np.zeros(100)])
"""
    )
    
    print(f"Created version: {version_v2.version}")
    
    # Vérifier la compatibilité
    compatibility = await manager.check_compatibility(
        "user_engagement_score",
        version_v1.version,
        version_v2.version
    )
    
    print(f"Compatibility: {compatibility.compatibility_level}")
    print(f"Migration required: {compatibility.migration_path}")
    
    # Analytics
    analytics = await manager.get_versioning_analytics()
    print(f"Versioning analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(main())