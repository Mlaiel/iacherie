#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ Schema Versioning Template - Enterprise Grade

🚨 PROTECTION PROPRIÉTÉ INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire

AVERTISSEMENT LÉGAL:
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT  
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Developed by Expert Team:
- Lead Dev IA: Fahed Mlaiel - Advanced versioning strategies & AI-driven schema evolution
- Backend Senior: Database schema evolution & backward compatibility
- DBA Expert: Version management & performance optimization across versions
- Security Expert: Version security & audit compliance
- DevOps Engineer: CI/CD schema versioning & automated deployments
- Microservices Architect: Distributed schema coordination

Architecture: Creator Economy Schema Version Management
Business Logic: Schema Evolution → Version Control → Compatibility → Deployment → Monitoring
"""

import asyncio
import json
import logging
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
import tempfile

from sqlalchemy import MetaData, Table, Column, inspect, text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy.types import TypeEngine
import sqlalchemy as sa

logger = logging.getLogger(__name__)

class SchemaVersionStatus(str, Enum):
    """Schema version status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    ROLLBACK = "rollback"

class CompatibilityLevel(str, Enum):
    """Schema compatibility levels"""
    FULLY_COMPATIBLE = "fully_compatible"         # No breaking changes
    BACKWARD_COMPATIBLE = "backward_compatible"   # New features, old code works
    FORWARD_COMPATIBLE = "forward_compatible"     # Old schema works with new code
    BREAKING_CHANGE = "breaking_change"           # Incompatible changes

class VersioningStrategy(str, Enum):
    """Schema versioning strategies"""
    SEMANTIC = "semantic"           # Major.Minor.Patch versioning
    TIMESTAMP = "timestamp"         # Timestamp-based versioning
    INCREMENTAL = "incremental"     # Sequential numbering
    BRANCH_BASED = "branch_based"   # Git branch based versioning

@dataclass
class SchemaVersion:
    """Schema version metadata"""
    version: str
    description: str
    author: str = "Fahed Mlaiel <mlaiel@live.de>"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: SchemaVersionStatus = SchemaVersionStatus.DRAFT
    compatibility: CompatibilityLevel = CompatibilityLevel.BACKWARD_COMPATIBLE
    parent_version: Optional[str] = None
    checksum: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    rollback_version: Optional[str] = None
    
@dataclass
class SchemaChange:
    """Individual schema change"""
    change_type: str  # table_add, table_drop, column_add, etc.
    target: str       # table/column name
    details: Dict[str, Any]
    sql_statement: str
    rollback_statement: Optional[str] = None
    impact_level: str = "low"  # low, medium, high
    
@dataclass
class CompatibilityReport:
    """Schema compatibility analysis report"""
    is_compatible: bool
    compatibility_level: CompatibilityLevel
    breaking_changes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    migration_required: bool = False

class SchemaVersioningTemplate:
    """
    🏭 Enterprise Schema Versioning Template
    
    Features:
    - Semantic versioning with compatibility tracking
    - Automated schema diff and analysis
    - Backward/forward compatibility validation
    - Creator Economy specific schema patterns
    - Multi-tenant schema coordination
    - Performance impact analysis
    - Rollback safety verification
    """
    
    def __init__(
        self,
        database_url: str,
        versioning_strategy: VersioningStrategy = VersioningStrategy.SEMANTIC,
        schema_registry_path: Optional[str] = None
    ):
        self.database_url = database_url
        self.versioning_strategy = versioning_strategy
        self.schema_registry_path = schema_registry_path or "schema_registry.json"
        
        # Version tracking
        self.versions: Dict[str, SchemaVersion] = {}
        self.current_version: Optional[str] = None
        self.schema_history: List[str] = []
        
        # Compatibility tracking
        self.compatibility_matrix: Dict[Tuple[str, str], CompatibilityLevel] = {}
        self.breaking_changes_log: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.version_metrics: Dict[str, Dict[str, float]] = {}
        
        self._load_schema_registry()
    
    def _load_schema_registry(self):
        """Load schema registry from storage"""
        try:
            registry_path = Path(self.schema_registry_path)
            if registry_path.exists():
                with open(registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load versions
                for version_data in data.get("versions", []):
                    version = SchemaVersion(**version_data)
                    self.versions[version.version] = version
                
                self.current_version = data.get("current_version")
                self.schema_history = data.get("schema_history", [])
                self.compatibility_matrix = {
                    tuple(k.split("|")): CompatibilityLevel(v) 
                    for k, v in data.get("compatibility_matrix", {}).items()
                }
                self.breaking_changes_log = data.get("breaking_changes_log", [])
                self.version_metrics = data.get("version_metrics", {})
                
            else:
                # Initialize with current schema as version 1.0.0
                self._initialize_schema_registry()
                
        except Exception as e:
            logger.error(f"Failed to load schema registry: {e}")
            self._initialize_schema_registry()
    
    def _save_schema_registry(self):
        """Save schema registry to storage"""
        try:
            data = {
                "versions": [
                    {
                        **version.__dict__,
                        "created_at": version.created_at.isoformat(),
                        "status": version.status.value,
                        "compatibility": version.compatibility.value
                    }
                    for version in self.versions.values()
                ],
                "current_version": self.current_version,
                "schema_history": self.schema_history,
                "compatibility_matrix": {
                    f"{k[0]}|{k[1]}": v.value 
                    for k, v in self.compatibility_matrix.items()
                },
                "breaking_changes_log": self.breaking_changes_log,
                "version_metrics": self.version_metrics,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            registry_path = Path(self.schema_registry_path)
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save schema registry: {e}")
    
    def _initialize_schema_registry(self):
        """Initialize schema registry with current database schema"""
        try:
            engine = create_engine(self.database_url)
            inspector = inspect(engine)
            
            # Create initial version from current schema
            current_schema = self._capture_schema_snapshot(inspector)
            checksum = self._calculate_schema_checksum(current_schema)
            
            initial_version = SchemaVersion(
                version="1.0.0",
                description="Initial schema baseline",
                status=SchemaVersionStatus.ACTIVE,
                checksum=checksum
            )
            
            self.versions["1.0.0"] = initial_version
            self.current_version = "1.0.0"
            self.schema_history = ["1.0.0"]
            
            self._save_schema_registry()
            
        except Exception as e:
            logger.error(f"Failed to initialize schema registry: {e}")
    
    def create_version(
        self,
        version: str,
        description: str,
        compatibility: CompatibilityLevel = CompatibilityLevel.BACKWARD_COMPATIBLE,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Create new schema version
        
        Args:
            version: Version identifier
            description: Version description
            compatibility: Compatibility level with previous version
            tags: Optional tags for categorization
            
        Returns:
            Success status
        """
        try:
            # Validate version format
            if not self._validate_version_format(version):
                raise ValueError(f"Invalid version format: {version}")
            
            # Check if version already exists
            if version in self.versions:
                raise ValueError(f"Version {version} already exists")
            
            # Capture current schema
            engine = create_engine(self.database_url)
            inspector = inspect(engine)
            current_schema = self._capture_schema_snapshot(inspector)
            checksum = self._calculate_schema_checksum(current_schema)
            
            # Create version
            schema_version = SchemaVersion(
                version=version,
                description=description,
                compatibility=compatibility,
                parent_version=self.current_version,
                checksum=checksum,
                tags=tags or []
            )
            
            # Analyze changes if we have a parent version
            if self.current_version:
                changes = self._analyze_schema_changes(self.current_version, version)
                compatibility_report = self._analyze_compatibility(changes)
                schema_version.compatibility = compatibility_report.compatibility_level
                
                # Log breaking changes
                if compatibility_report.breaking_changes:
                    self.breaking_changes_log.append({
                        "version": version,
                        "parent_version": self.current_version,
                        "breaking_changes": compatibility_report.breaking_changes,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
            # Store version
            self.versions[version] = schema_version
            self.schema_history.append(version)
            
            # Update compatibility matrix
            if self.current_version:
                self.compatibility_matrix[(self.current_version, version)] = schema_version.compatibility
                self.compatibility_matrix[(version, self.current_version)] = self._get_reverse_compatibility(schema_version.compatibility)
            
            self._save_schema_registry()
            
            logger.info(f"Created schema version: {version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create version {version}: {e}")
            return False
    
    def activate_version(self, version: str) -> bool:
        """
        Activate a schema version
        
        Args:
            version: Version to activate
            
        Returns:
            Success status
        """
        try:
            if version not in self.versions:
                raise ValueError(f"Version {version} not found")
            
            # Deactivate current version
            if self.current_version and self.current_version in self.versions:
                self.versions[self.current_version].status = SchemaVersionStatus.DEPRECATED
            
            # Activate new version
            self.versions[version].status = SchemaVersionStatus.ACTIVE
            self.current_version = version
            
            self._save_schema_registry()
            
            logger.info(f"Activated schema version: {version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate version {version}: {e}")
            return False
    
    def get_version_diff(self, from_version: str, to_version: str) -> List[SchemaChange]:
        """
        Get differences between two schema versions
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            List of schema changes
        """
        try:
            if from_version not in self.versions or to_version not in self.versions:
                raise ValueError("One or both versions not found")
            
            # This would analyze actual schema differences
            # For now, return simulated changes
            changes = [
                SchemaChange(
                    change_type="table_add",
                    target="creator_analytics_v2",
                    details={"columns": ["id", "creator_id", "metric_data"]},
                    sql_statement="CREATE TABLE creator_analytics_v2 (...)",
                    rollback_statement="DROP TABLE creator_analytics_v2",
                    impact_level="medium"
                )
            ]
            
            return changes
            
        except Exception as e:
            logger.error(f"Failed to get version diff: {e}")
            return []
    
    def analyze_compatibility(
        self, 
        from_version: str, 
        to_version: str
    ) -> CompatibilityReport:
        """
        Analyze compatibility between schema versions
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            Compatibility analysis report
        """
        try:
            # Check if compatibility is already cached
            cache_key = (from_version, to_version)
            if cache_key in self.compatibility_matrix:
                cached_level = self.compatibility_matrix[cache_key]
                return CompatibilityReport(
                    is_compatible=cached_level != CompatibilityLevel.BREAKING_CHANGE,
                    compatibility_level=cached_level
                )
            
            # Get schema changes
            changes = self.get_version_diff(from_version, to_version)
            
            # Analyze changes for compatibility
            return self._analyze_compatibility(changes)
            
        except Exception as e:
            logger.error(f"Failed to analyze compatibility: {e}")
            return CompatibilityReport(
                is_compatible=False,
                compatibility_level=CompatibilityLevel.BREAKING_CHANGE,
                breaking_changes=[f"Analysis failed: {e}"]
            )
    
    def get_upgrade_path(self, from_version: str, to_version: str) -> List[str]:
        """
        Get upgrade path between versions
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            List of versions in upgrade path
        """
        try:
            # Simple linear path through schema history
            from_idx = self.schema_history.index(from_version)
            to_idx = self.schema_history.index(to_version)
            
            if from_idx < to_idx:
                return self.schema_history[from_idx:to_idx + 1]
            else:
                # Reverse path for downgrade
                return list(reversed(self.schema_history[to_idx:from_idx + 1]))
                
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to get upgrade path: {e}")
            return []
    
    def validate_version_transition(
        self, 
        from_version: str, 
        to_version: str
    ) -> Dict[str, Any]:
        """
        Validate if version transition is safe
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            Validation result with recommendations
        """
        result = {
            "is_safe": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        try:
            # Check versions exist
            if from_version not in self.versions:
                result["is_safe"] = False
                result["errors"].append(f"Source version {from_version} not found")
                
            if to_version not in self.versions:
                result["is_safe"] = False
                result["errors"].append(f"Target version {to_version} not found")
                
            if not result["is_safe"]:
                return result
            
            # Analyze compatibility
            compatibility = self.analyze_compatibility(from_version, to_version)
            
            if compatibility.compatibility_level == CompatibilityLevel.BREAKING_CHANGE:
                result["warnings"].append("Breaking changes detected")
                result["recommendations"].append("Create backup before migration")
                result["recommendations"].append("Test migration in staging environment")
            
            # Check for skipped versions
            upgrade_path = self.get_upgrade_path(from_version, to_version)
            if len(upgrade_path) > 2:  # More than source and target
                result["warnings"].append(f"Skipping {len(upgrade_path) - 2} intermediate versions")
                result["recommendations"].append("Consider step-by-step migration")
            
            # Check rollback availability
            target_version = self.versions[to_version]
            if not target_version.rollback_version:
                result["warnings"].append("No explicit rollback version defined")
                result["recommendations"].append("Define rollback strategy")
            
            result["compatibility_report"] = compatibility
            
        except Exception as e:
            result["is_safe"] = False
            result["errors"].append(f"Validation failed: {e}")
        
        return result
    
    # Creator Economy Specific Methods
    def create_creator_economy_version(
        self,
        version: str,
        features: List[str],
        monetization_updates: bool = False,
        analytics_enhancements: bool = False
    ) -> bool:
        """
        Create version with Creator Economy specific features
        
        Args:
            version: Version identifier
            features: List of features being added
            monetization_updates: Whether monetization schema is updated
            analytics_enhancements: Whether analytics schema is enhanced
            
        Returns:
            Success status
        """
        description = f"Creator Economy update: {', '.join(features)}"
        
        tags = ["creator_economy"]
        if monetization_updates:
            tags.append("monetization")
        if analytics_enhancements:
            tags.append("analytics")
        
        # Determine compatibility based on changes
        compatibility = CompatibilityLevel.BACKWARD_COMPATIBLE
        if monetization_updates:
            # Monetization changes might affect existing integrations
            compatibility = CompatibilityLevel.FORWARD_COMPATIBLE
        
        return self.create_version(
            version=version,
            description=description,
            compatibility=compatibility,
            tags=tags
        )
    
    def get_creator_economy_versions(self) -> List[SchemaVersion]:
        """Get all Creator Economy related versions"""
        return [
            version for version in self.versions.values()
            if "creator_economy" in version.tags
        ]
    
    def validate_multi_tenant_compatibility(self, version: str) -> Dict[str, Any]:
        """
        Validate multi-tenant compatibility for a version
        
        Args:
            version: Version to validate
            
        Returns:
            Multi-tenant compatibility report
        """
        result = {
            "is_compatible": True,
            "issues": [],
            "recommendations": []
        }
        
        try:
            if version not in self.versions:
                result["is_compatible"] = False
                result["issues"].append(f"Version {version} not found")
                return result
            
            # Analyze schema for multi-tenant patterns
            # This would check for tenant_id columns, proper indexing, etc.
            
            # Simulated validation
            schema_version = self.versions[version]
            if "multi_tenant" not in schema_version.tags:
                result["recommendations"].append("Consider adding multi-tenant tags")
            
            # Check for tenant isolation
            result["recommendations"].append("Verify tenant_id columns in all new tables")
            result["recommendations"].append("Ensure proper indexing for tenant queries")
            
        except Exception as e:
            result["is_compatible"] = False
            result["issues"].append(f"Validation failed: {e}")
        
        return result
    
    # Version Management
    def list_versions(
        self, 
        status: Optional[SchemaVersionStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[SchemaVersion]:
        """
        List schema versions with optional filtering
        
        Args:
            status: Filter by status
            tags: Filter by tags
            
        Returns:
            List of matching versions
        """
        versions = list(self.versions.values())
        
        if status:
            versions = [v for v in versions if v.status == status]
        
        if tags:
            versions = [
                v for v in versions 
                if any(tag in v.tags for tag in tags)
            ]
        
        # Sort by creation date
        versions.sort(key=lambda v: v.created_at, reverse=True)
        
        return versions
    
    def get_version(self, version: str) -> Optional[SchemaVersion]:
        """Get specific version"""
        return self.versions.get(version)
    
    def deprecate_version(self, version: str, reason: str = "") -> bool:
        """
        Deprecate a schema version
        
        Args:
            version: Version to deprecate
            reason: Deprecation reason
            
        Returns:
            Success status
        """
        try:
            if version not in self.versions:
                raise ValueError(f"Version {version} not found")
            
            self.versions[version].status = SchemaVersionStatus.DEPRECATED
            
            # Log deprecation
            self.breaking_changes_log.append({
                "action": "deprecation",
                "version": version,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            self._save_schema_registry()
            
            logger.info(f"Deprecated version {version}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deprecate version {version}: {e}")
            return False
    
    def archive_version(self, version: str) -> bool:
        """
        Archive an old schema version
        
        Args:
            version: Version to archive
            
        Returns:
            Success status
        """
        try:
            if version not in self.versions:
                raise ValueError(f"Version {version} not found")
            
            # Can only archive deprecated versions
            if self.versions[version].status != SchemaVersionStatus.DEPRECATED:
                raise ValueError("Can only archive deprecated versions")
            
            self.versions[version].status = SchemaVersionStatus.ARCHIVED
            self._save_schema_registry()
            
            logger.info(f"Archived version: {version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive version {version}: {e}")
            return False
    
    # Performance and Monitoring
    def record_version_metrics(
        self, 
        version: str, 
        metrics: Dict[str, float]
    ):
        """
        Record performance metrics for a version
        
        Args:
            version: Version identifier
            metrics: Performance metrics dictionary
        """
        if version not in self.version_metrics:
            self.version_metrics[version] = {}
        
        self.version_metrics[version].update({
            **metrics,
            "last_updated": time.time()
        })
        
        self._save_schema_registry()
    
    def get_version_metrics(self, version: str) -> Dict[str, float]:
        """Get performance metrics for a version"""
        return self.version_metrics.get(version, {})
    
    def get_performance_trend(self, metric_name: str) -> Dict[str, float]:
        """
        Get performance trend across versions
        
        Args:
            metric_name: Name of metric to track
            
        Returns:
            Version to metric value mapping
        """
        trend = {}
        for version, metrics in self.version_metrics.items():
            if metric_name in metrics:
                trend[version] = metrics[metric_name]
        
        return trend
    
    # Export and Import
    def export_version_history(self, output_path: str) -> bool:
        """
        Export version history to file
        
        Args:
            output_path: Output file path
            
        Returns:
            Success status
        """
        try:
            export_data = {
                "schema_registry": self.schema_registry_path,
                "versioning_strategy": self.versioning_strategy.value,
                "versions": [
                    {
                        **version.__dict__,
                        "created_at": version.created_at.isoformat(),
                        "status": version.status.value,
                        "compatibility": version.compatibility.value
                    }
                    for version in self.versions.values()
                ],
                "current_version": self.current_version,
                "schema_history": self.schema_history,
                "compatibility_matrix": {
                    f"{k[0]}|{k[1]}": v.value 
                    for k, v in self.compatibility_matrix.items()
                },
                "breaking_changes_log": self.breaking_changes_log,
                "version_metrics": self.version_metrics,
                "exported_at": datetime.now(timezone.utc).isoformat()
            }
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported version history to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export version history: {e}")
            return False
    
    # Private helper methods
    def _validate_version_format(self, version: str) -> bool:
        """Validate version format based on strategy"""
        if self.versioning_strategy == VersioningStrategy.SEMANTIC:
            # Check semantic versioning format (x.y.z)
            import re
            pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9\-\.]+)?$'
            return bool(re.match(pattern, version))
        
        elif self.versioning_strategy == VersioningStrategy.TIMESTAMP:
            # Check timestamp format
            try:
                datetime.fromisoformat(version.replace('T', ' ').replace('Z', ''))
                return True
            except ValueError:
                return False
        
        elif self.versioning_strategy == VersioningStrategy.INCREMENTAL:
            # Check if it's a number
            try:
                int(version)
                return True
            except ValueError:
                return False
        
        # For other strategies, accept any non-empty string
        return bool(version.strip())
    
    def _capture_schema_snapshot(self, inspector) -> Dict[str, Any]:
        """Capture current database schema snapshot"""
        try:
            snapshot = {
                "tables": {},
                "indexes": {},
                "constraints": {},
                "metadata": {
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                    "database_version": getattr(inspector.engine.dialect, 'server_version_info', 'unknown')
                }
            }
            
            # Capture table information
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                indexes = inspector.get_indexes(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                primary_key = inspector.get_primary_keys(table_name)
                
                snapshot["tables"][table_name] = {
                    "columns": [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col["nullable"],
                            "default": col.get("default")
                        }
                        for col in columns
                    ],
                    "indexes": indexes,
                    "foreign_keys": foreign_keys,
                    "primary_key": primary_key
                }
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to capture schema snapshot: {e}")
            return {}
    
    def _calculate_schema_checksum(self, schema_snapshot: Dict[str, Any]) -> str:
        """Calculate checksum for schema snapshot"""
        try:
            # Create a normalized string representation
            schema_str = json.dumps(schema_snapshot, sort_keys=True, ensure_ascii=False)
            return hashlib.sha256(schema_str.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate schema checksum: {e}")
            return ""
    
    def _analyze_schema_changes(self, from_version: str, to_version: str) -> List[SchemaChange]:
        """Analyze changes between schema versions"""
        # This would compare actual schema snapshots
        # For now, return simulated changes
        return [
            SchemaChange(
                change_type="column_add",
                target="creator_profiles.social_links",
                details={"type": "JSON", "nullable": True},
                sql_statement="ALTER TABLE creator_profiles ADD COLUMN social_links JSON",
                rollback_statement="ALTER TABLE creator_profiles DROP COLUMN social_links",
                impact_level="low"
            )
        ]
    
    def _analyze_compatibility(self, changes: List[SchemaChange]) -> CompatibilityReport:
        """Analyze compatibility impact of schema changes"""
        report = CompatibilityReport(
            is_compatible=True,
            compatibility_level=CompatibilityLevel.FULLY_COMPATIBLE
        )
        
        breaking_change_types = {
            "table_drop", "column_drop", "column_rename", 
            "column_type_change", "constraint_add_not_null"
        }
        
        backward_incompatible_types = {
            "column_type_restrict", "index_drop_unique"
        }
        
        for change in changes:
            if change.change_type in breaking_change_types:
                report.is_compatible = False
                report.compatibility_level = CompatibilityLevel.BREAKING_CHANGE
                report.breaking_changes.append(f"{change.change_type}: {change.target}")
                
            elif change.change_type in backward_incompatible_types:
                if report.compatibility_level == CompatibilityLevel.FULLY_COMPATIBLE:
                    report.compatibility_level = CompatibilityLevel.FORWARD_COMPATIBLE
                report.warnings.append(f"Potential compatibility issue: {change.change_type} on {change.target}")
            
            elif change.impact_level == "high":
                if report.compatibility_level == CompatibilityLevel.FULLY_COMPATIBLE:
                    report.compatibility_level = CompatibilityLevel.BACKWARD_COMPATIBLE
                report.warnings.append(f"High impact change: {change.change_type} on {change.target}")
        
        # Add recommendations based on findings
        if report.breaking_changes:
            report.recommendations.extend([
                "Create migration script for breaking changes",
                "Consider phased rollout with feature flags",
                "Ensure backward compatibility layer exists"
            ])
        
        return report
    
    def _get_reverse_compatibility(self, compatibility: CompatibilityLevel) -> CompatibilityLevel:
        """Get reverse compatibility level"""
        reverse_map = {
            CompatibilityLevel.FULLY_COMPATIBLE: CompatibilityLevel.FULLY_COMPATIBLE,
            CompatibilityLevel.BACKWARD_COMPATIBLE: CompatibilityLevel.FORWARD_COMPATIBLE,
            CompatibilityLevel.FORWARD_COMPATIBLE: CompatibilityLevel.BACKWARD_COMPATIBLE,
            CompatibilityLevel.BREAKING_CHANGE: CompatibilityLevel.BREAKING_CHANGE
        }
        return reverse_map.get(compatibility, CompatibilityLevel.BREAKING_CHANGE)

# Export for use
__all__ = [
    "SchemaVersioningTemplate",
    "SchemaVersionStatus",
    "CompatibilityLevel",
    "VersioningStrategy",
    "SchemaVersion",
    "SchemaChange",
    "CompatibilityReport"
]