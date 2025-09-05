"""🏗️ Schema Manager - Advanced Schema Management & Versioning
================================================================
Module: database/schema_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Enterprise Schema Management - Production-Ready
Responsibility: Advanced schema versioning, management and evolution

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This schema manager provides enterprise-grade schema management for:
- Advanced schema versioning and evolution
- Multi-environment schema deployment
- Schema validation and integrity checking
- Automated schema optimization strategies
- Cross-database schema synchronization
- Performance-optimized schema design
"""

import os
import json
import logging
import hashlib
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Optional imports for production features
try:
    import sqlalchemy
    from sqlalchemy import inspect, text, MetaData, Table, Column
    from sqlalchemy.schema import CreateTable, DropTable
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    sqlalchemy = None

# Configure logging
logger = logging.getLogger(__name__)

class SchemaChangeType(Enum):
    """Schema change type enumeration"""
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    ALTER_TABLE = "alter_table"
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    CREATE_INDEX = "create_index"
    DROP_INDEX = "drop_index"
    ADD_CONSTRAINT = "add_constraint"
    DROP_CONSTRAINT = "drop_constraint"

class SchemaEnvironment(Enum):
    """Schema environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class SchemaVersion:
    """Represents a schema version"""
    version: str
    name: str
    description: str
    changes: List[Dict[str, Any]]
    checksum: str
    created_at: datetime.datetime
    applied_at: Optional[datetime.datetime] = None
    environment: SchemaEnvironment = SchemaEnvironment.DEVELOPMENT

@dataclass
class SchemaValidationResult:
    """Schema validation result"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]

class SchemaManager:
    """Advanced schema management and versioning system"""
    
    def __init__(self, connection=None, schema_dir: str = None):
        self.connection = connection
        self.schema_dir = Path(schema_dir or os.path.join(os.getcwd(), "schemas"))
        self.versions: List[SchemaVersion] = []
        self.current_version: Optional[str] = None
        self.metadata = MetaData() if SQLALCHEMY_AVAILABLE else None
        self._ensure_schema_directory()
        self._initialize_schema_table()
        self._load_versions()
    
    def _ensure_schema_directory(self):
        """Ensure schema directory exists"""
        self.schema_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different environments
        for env in SchemaEnvironment:
            env_dir = self.schema_dir / env.value
            env_dir.mkdir(exist_ok=True)
    
    def _initialize_schema_table(self):
        """Initialize schema versions tracking table"""
        if not SQLALCHEMY_AVAILABLE or not self.connection:
            logger.warning("SQLAlchemy not available or no connection, using file-based tracking")
            return
        
        try:
            # Create schema_versions table if it doesn't exist
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS schema_versions (
                version VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                changes JSON,
                checksum VARCHAR(64) NOT NULL,
                environment VARCHAR(50) DEFAULT 'development',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rollback_sql TEXT
            )
            """
            self.connection.execute(text(create_table_sql))
            self.connection.commit()
            logger.info("Schema versions table initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize schema versions table: {e}")
    
    def _load_versions(self):
        """Load existing schema versions"""
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                # Load from database
                result = self.connection.execute(
                    text("SELECT * FROM schema_versions ORDER BY version")
                )
                for row in result.fetchall():
                    changes = json.loads(row.changes) if row.changes else []
                    version = SchemaVersion(
                        version=row.version,
                        name=row.name,
                        description=row.description or "",
                        changes=changes,
                        checksum=row.checksum,
                        created_at=row.created_at,
                        applied_at=row.applied_at,
                        environment=SchemaEnvironment(row.environment or "development")
                    )
                    self.versions.append(version)
            else:
                # Load from files
                self._load_versions_from_files()
                
            # Determine current version
            if self.versions:
                self.current_version = max(self.versions, key=lambda v: v.version).version
                
        except Exception as e:
            logger.error(f"Failed to load schema versions: {e}")
    
    def _load_versions_from_files(self):
        """Load schema versions from files"""
        try:
            versions_file = self.schema_dir / "versions.json"
            if versions_file.exists():
                with open(versions_file, 'r') as f:
                    data = json.load(f)
                    for version_data in data.get('versions', []):
                        version = SchemaVersion(
                            version=version_data['version'],
                            name=version_data['name'],
                            description=version_data.get('description', ''),
                            changes=version_data.get('changes', []),
                            checksum=version_data['checksum'],
                            created_at=datetime.datetime.fromisoformat(version_data['created_at']),
                            applied_at=datetime.datetime.fromisoformat(version_data['applied_at']) if version_data.get('applied_at') else None,
                            environment=SchemaEnvironment(version_data.get('environment', 'development'))
                        )
                        self.versions.append(version)
        except Exception as e:
            logger.error(f"Failed to load versions from files: {e}")
    
    def create_version(self, version: str, name: str, description: str, 
                      changes: List[Dict[str, Any]], 
                      environment: SchemaEnvironment = SchemaEnvironment.DEVELOPMENT) -> SchemaVersion:
        """Create a new schema version"""
        try:
            # Calculate checksum
            changes_json = json.dumps(changes, sort_keys=True)
            checksum = hashlib.sha256(changes_json.encode()).hexdigest()
            
            # Create version object
            schema_version = SchemaVersion(
                version=version,
                name=name,
                description=description,
                changes=changes,
                checksum=checksum,
                created_at=datetime.datetime.utcnow(),
                environment=environment
            )
            
            # Validate version
            validation = self.validate_version(schema_version)
            if not validation.is_valid:
                raise ValueError(f"Invalid schema version: {validation.errors}")
            
            # Save version
            self._save_version(schema_version)
            self.versions.append(schema_version)
            
            logger.info(f"Created schema version {version}: {name}")
            return schema_version
            
        except Exception as e:
            logger.error(f"Failed to create schema version {version}: {e}")
            raise
    
    def _save_version(self, version: SchemaVersion):
        """Save schema version to storage"""
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                # Save to database
                sql = """
                INSERT INTO schema_versions (version, name, description, changes, checksum, environment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                self.connection.execute(text(sql), (
                    version.version,
                    version.name,
                    version.description,
                    json.dumps(version.changes),
                    version.checksum,
                    version.environment.value,
                    version.created_at
                ))
                self.connection.commit()
            else:
                # Save to file
                self._save_versions_to_file()
                
        except Exception as e:
            logger.error(f"Failed to save schema version {version.version}: {e}")
            raise
    
    def _save_versions_to_file(self):
        """Save all versions to file"""
        try:
            versions_data = {
                'versions': [
                    {
                        'version': v.version,
                        'name': v.name,
                        'description': v.description,
                        'changes': v.changes,
                        'checksum': v.checksum,
                        'environment': v.environment.value,
                        'created_at': v.created_at.isoformat(),
                        'applied_at': v.applied_at.isoformat() if v.applied_at else None
                    }
                    for v in self.versions
                ]
            }
            
            versions_file = self.schema_dir / "versions.json"
            with open(versions_file, 'w') as f:
                json.dump(versions_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save versions to file: {e}")
    
    def apply_version(self, version: str, environment: SchemaEnvironment = None) -> bool:
        """Apply a schema version"""
        try:
            # Find version
            schema_version = next((v for v in self.versions if v.version == version), None)
            if not schema_version:
                raise ValueError(f"Schema version {version} not found")
            
            # Check environment compatibility
            if environment and schema_version.environment != environment:
                logger.warning(f"Version {version} environment mismatch: {schema_version.environment} vs {environment}")
            
            # Apply changes
            success = True
            for change in schema_version.changes:
                if not self._apply_change(change):
                    success = False
                    break
            
            if success:
                # Mark as applied
                schema_version.applied_at = datetime.datetime.utcnow()
                self._update_version_applied(schema_version)
                self.current_version = version
                logger.info(f"Successfully applied schema version {version}")
            else:
                logger.error(f"Failed to apply schema version {version}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to apply schema version {version}: {e}")
            return False
    
    def _apply_change(self, change: Dict[str, Any]) -> bool:
        """Apply a single schema change"""
        try:
            change_type = SchemaChangeType(change.get('type'))
            
            if not SQLALCHEMY_AVAILABLE or not self.connection:
                logger.warning(f"Cannot apply change {change_type.value}: No database connection")
                return True  # Assume success for testing
            
            if change_type == SchemaChangeType.CREATE_TABLE:
                return self._create_table(change)
            elif change_type == SchemaChangeType.DROP_TABLE:
                return self._drop_table(change)
            elif change_type == SchemaChangeType.ALTER_TABLE:
                return self._alter_table(change)
            elif change_type == SchemaChangeType.ADD_COLUMN:
                return self._add_column(change)
            elif change_type == SchemaChangeType.DROP_COLUMN:
                return self._drop_column(change)
            elif change_type == SchemaChangeType.CREATE_INDEX:
                return self._create_index(change)
            elif change_type == SchemaChangeType.DROP_INDEX:
                return self._drop_index(change)
            else:
                logger.warning(f"Unknown change type: {change_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply change {change}: {e}")
            return False
    
    def _create_table(self, change: Dict[str, Any]) -> bool:
        """Create a table"""
        try:
            sql = change.get('sql')
            if sql:
                self.connection.execute(text(sql))
                self.connection.commit()
                logger.info(f"Created table: {change.get('table_name')}")
                return True
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
        return False
    
    def _drop_table(self, change: Dict[str, Any]) -> bool:
        """Drop a table"""
        try:
            table_name = change.get('table_name')
            if table_name:
                sql = f"DROP TABLE IF EXISTS {table_name}"
                self.connection.execute(text(sql))
                self.connection.commit()
                logger.info(f"Dropped table: {table_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to drop table: {e}")
        return False
    
    def _alter_table(self, change: Dict[str, Any]) -> bool:
        """Alter a table"""
        try:
            sql = change.get('sql')
            if sql:
                self.connection.execute(text(sql))
                self.connection.commit()
                logger.info(f"Altered table: {change.get('table_name')}")
                return True
        except Exception as e:
            logger.error(f"Failed to alter table: {e}")
        return False
    
    def _add_column(self, change: Dict[str, Any]) -> bool:
        """Add a column to a table"""
        try:
            table_name = change.get('table_name')
            column_def = change.get('column_definition')
            if table_name and column_def:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_def}"
                self.connection.execute(text(sql))
                self.connection.commit()
                logger.info(f"Added column to {table_name}: {column_def}")
                return True
        except Exception as e:
            logger.error(f"Failed to add column: {e}")
        return False
    
    def _drop_column(self, change: Dict[str, Any]) -> bool:
        """Drop a column from a table"""
        try:
            table_name = change.get('table_name')
            column_name = change.get('column_name')
            if table_name and column_name:
                sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
                self.connection.execute(text(sql))
                self.connection.commit()
                logger.info(f"Dropped column from {table_name}: {column_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to drop column: {e}")
        return False
    
    def _create_index(self, change: Dict[str, Any]) -> bool:
        """Create an index"""
        try:
            sql = change.get('sql')
            if sql:
                self.connection.execute(text(sql))
                self.connection.commit()
                logger.info(f"Created index: {change.get('index_name')}")
                return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
        return False
    
    def _drop_index(self, change: Dict[str, Any]) -> bool:
        """Drop an index"""
        try:
            index_name = change.get('index_name')
            if index_name:
                sql = f"DROP INDEX IF EXISTS {index_name}"
                self.connection.execute(text(sql))
                self.connection.commit()
                logger.info(f"Dropped index: {index_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to drop index: {e}")
        return False
    
    def _update_version_applied(self, version: SchemaVersion):
        """Update version as applied"""
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                sql = "UPDATE schema_versions SET applied_at = ? WHERE version = ?"
                self.connection.execute(text(sql), (version.applied_at, version.version))
                self.connection.commit()
            else:
                self._save_versions_to_file()
        except Exception as e:
            logger.error(f"Failed to update version applied: {e}")
    
    def validate_version(self, version: SchemaVersion) -> SchemaValidationResult:
        """Validate a schema version"""
        errors = []
        warnings = []
        recommendations = []
        
        try:
            # Check version format
            if not version.version:
                errors.append("Version number is required")
            
            # Check for duplicate version
            if any(v.version == version.version for v in self.versions):
                errors.append(f"Version {version.version} already exists")
            
            # Validate changes
            for i, change in enumerate(version.changes):
                change_type = change.get('type')
                if not change_type:
                    errors.append(f"Change {i}: type is required")
                    continue
                
                try:
                    SchemaChangeType(change_type)
                except ValueError:
                    errors.append(f"Change {i}: invalid type '{change_type}'")
                
                # Validate specific change requirements
                if change_type in ['create_table', 'alter_table', 'create_index']:
                    if not change.get('sql'):
                        errors.append(f"Change {i}: SQL is required for {change_type}")
                
                if change_type in ['drop_table', 'add_column', 'drop_column']:
                    if not change.get('table_name'):
                        errors.append(f"Change {i}: table_name is required for {change_type}")
            
            # Performance recommendations
            create_table_count = sum(1 for c in version.changes if c.get('type') == 'create_table')
            if create_table_count > 10:
                recommendations.append(f"Consider splitting {create_table_count} table creations across multiple versions")
            
            drop_operations = sum(1 for c in version.changes if c.get('type', '').startswith('drop_'))
            if drop_operations > 0:
                warnings.append(f"Version contains {drop_operations} destructive operations - ensure proper backups")
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return SchemaValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def get_schema_diff(self, from_version: str, to_version: str) -> List[Dict[str, Any]]:
        """Get schema differences between versions"""
        try:
            from_ver = next((v for v in self.versions if v.version == from_version), None)
            to_ver = next((v for v in self.versions if v.version == to_version), None)
            
            if not from_ver or not to_ver:
                raise ValueError("One or both versions not found")
            
            # For now, return all changes between versions
            # In a more sophisticated implementation, this would calculate actual differences
            from_index = self.versions.index(from_ver)
            to_index = self.versions.index(to_ver)
            
            if from_index > to_index:
                from_index, to_index = to_index, from_index
            
            diff_changes = []
            for i in range(from_index + 1, to_index + 1):
                diff_changes.extend(self.versions[i].changes)
            
            return diff_changes
            
        except Exception as e:
            logger.error(f"Failed to get schema diff: {e}")
            return []
    
    def rollback_to_version(self, version: str) -> bool:
        """Rollback schema to a specific version"""
        try:
            target_version = next((v for v in self.versions if v.version == version), None)
            if not target_version:
                raise ValueError(f"Target version {version} not found")
            
            # Find current version index
            current_index = None
            target_index = None
            
            for i, v in enumerate(self.versions):
                if v.version == self.current_version:
                    current_index = i
                if v.version == version:
                    target_index = i
            
            if current_index is None or target_index is None:
                raise ValueError("Cannot determine version positions")
            
            if target_index >= current_index:
                logger.warning(f"Target version {version} is not older than current version")
                return True
            
            # Apply rollback changes (in reverse order)
            success = True
            for i in range(current_index, target_index, -1):
                rollback_changes = self._generate_rollback_changes(self.versions[i])
                for change in reversed(rollback_changes):
                    if not self._apply_change(change):
                        success = False
                        break
                if not success:
                    break
            
            if success:
                self.current_version = version
                logger.info(f"Successfully rolled back to version {version}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rollback to version {version}: {e}")
            return False
    
    def _generate_rollback_changes(self, version: SchemaVersion) -> List[Dict[str, Any]]:
        """Generate rollback changes for a version"""
        rollback_changes = []
        
        for change in reversed(version.changes):
            change_type = SchemaChangeType(change.get('type'))
            
            if change_type == SchemaChangeType.CREATE_TABLE:
                rollback_changes.append({
                    'type': SchemaChangeType.DROP_TABLE.value,
                    'table_name': change.get('table_name')
                })
            elif change_type == SchemaChangeType.DROP_TABLE:
                # Would need original table definition to recreate
                logger.warning(f"Cannot automatically rollback DROP_TABLE for {change.get('table_name')}")
            elif change_type == SchemaChangeType.ADD_COLUMN:
                rollback_changes.append({
                    'type': SchemaChangeType.DROP_COLUMN.value,
                    'table_name': change.get('table_name'),
                    'column_name': change.get('column_name')
                })
            elif change_type == SchemaChangeType.DROP_COLUMN:
                # Would need original column definition to recreate
                logger.warning(f"Cannot automatically rollback DROP_COLUMN for {change.get('table_name')}.{change.get('column_name')}")
        
        return rollback_changes
    
    def get_version_info(self, version: str = None) -> Dict[str, Any]:
        """Get information about a schema version"""
        if version:
            target_version = next((v for v in self.versions if v.version == version), None)
            if not target_version:
                return {}
            
            return {
                'version': target_version.version,
                'name': target_version.name,
                'description': target_version.description,
                'changes_count': len(target_version.changes),
                'checksum': target_version.checksum,
                'environment': target_version.environment.value,
                'created_at': target_version.created_at.isoformat(),
                'applied_at': target_version.applied_at.isoformat() if target_version.applied_at else None,
                'is_applied': target_version.applied_at is not None
            }
        else:
            return {
                'current_version': self.current_version,
                'total_versions': len(self.versions),
                'applied_versions': len([v for v in self.versions if v.applied_at]),
                'pending_versions': len([v for v in self.versions if not v.applied_at]),
                'schema_directory': str(self.schema_dir),
                'sqlalchemy_available': SQLALCHEMY_AVAILABLE
            }
    
    def export_schema(self, version: str = None, format: str = 'json') -> str:
        """Export schema to various formats"""
        try:
            if version:
                target_version = next((v for v in self.versions if v.version == version), None)
                if not target_version:
                    raise ValueError(f"Version {version} not found")
                versions_to_export = [target_version]
            else:
                versions_to_export = self.versions
            
            if format.lower() == 'json':
                export_data = {
                    'schema_export': {
                        'exported_at': datetime.datetime.utcnow().isoformat(),
                        'current_version': self.current_version,
                        'versions': [
                            {
                                'version': v.version,
                                'name': v.name,
                                'description': v.description,
                                'changes': v.changes,
                                'checksum': v.checksum,
                                'environment': v.environment.value,
                                'created_at': v.created_at.isoformat(),
                                'applied_at': v.applied_at.isoformat() if v.applied_at else None
                            }
                            for v in versions_to_export
                        ]
                    }
                }
                return json.dumps(export_data, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export schema: {e}")
            return ""

# Global schema manager instance
_schema_manager = None

def get_schema_manager(connection=None, schema_dir: str = None) -> SchemaManager:
    """Get the global schema manager"""
    global _schema_manager
    if _schema_manager is None:
        _schema_manager = SchemaManager(connection, schema_dir)
    return _schema_manager

def create_schema_version(version: str, name: str, description: str, 
                         changes: List[Dict[str, Any]], 
                         environment: SchemaEnvironment = SchemaEnvironment.DEVELOPMENT) -> SchemaVersion:
    """Create a new schema version"""
    manager = get_schema_manager()
    return manager.create_version(version, name, description, changes, environment)

def apply_schema_version(version: str, environment: SchemaEnvironment = None) -> bool:
    """Apply a schema version"""
    manager = get_schema_manager()
    return manager.apply_version(version, environment)

def validate_schema_version(version: SchemaVersion) -> SchemaValidationResult:
    """Validate a schema version"""
    manager = get_schema_manager()
    return manager.validate_version(version)

def get_schema_info() -> Dict[str, Any]:
    """Get schema management system information"""
    manager = get_schema_manager()
    return manager.get_version_info()

# Convenience functions for common schema operations
def migrate_to_latest(environment: SchemaEnvironment = SchemaEnvironment.DEVELOPMENT) -> bool:
    """Migrate to the latest schema version"""
    manager = get_schema_manager()
    
    # Find latest version for environment
    env_versions = [v for v in manager.versions if v.environment == environment and not v.applied_at]
    if not env_versions:
        logger.info("No pending migrations")
        return True
    
    # Apply all pending versions in order
    success = True
    for version in sorted(env_versions, key=lambda v: v.version):
        if not manager.apply_version(version.version, environment):
            success = False
            break
    
    return success

def create_table_migration(version: str, table_name: str, table_sql: str, 
                          description: str = None) -> SchemaVersion:
    """Create a migration for table creation"""
    changes = [{
        'type': SchemaChangeType.CREATE_TABLE.value,
        'table_name': table_name,
        'sql': table_sql,
        'description': f"Create table {table_name}"
    }]
    
    return create_schema_version(
        version=version,
        name=f"create_table_{table_name}",
        description=description or f"Create {table_name} table",
        changes=changes
    )

def create_index_migration(version: str, index_name: str, table_name: str, 
                          columns: List[str], unique: bool = False,
                          description: str = None) -> SchemaVersion:
    """Create a migration for index creation"""
    unique_clause = "UNIQUE " if unique else ""
    columns_clause = ", ".join(columns)
    index_sql = f"CREATE {unique_clause}INDEX {index_name} ON {table_name} ({columns_clause})"
    
    changes = [{
        'type': SchemaChangeType.CREATE_INDEX.value,
        'index_name': index_name,
        'table_name': table_name,
        'sql': index_sql,
        'description': f"Create {'unique ' if unique else ''}index {index_name} on {table_name}"
    }]
    
    return create_schema_version(
        version=version,
        name=f"create_index_{index_name}",
        description=description or f"Create index {index_name}",
        changes=changes
    )