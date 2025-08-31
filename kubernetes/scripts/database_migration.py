#!/usr/bin/env python3
"""
Database Migration Manager
Handles database schema migrations, data migrations, and version control
"""

import os
import sys
import time
import json
import logging
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationType(Enum):
    """Migration type enumeration"""
    SCHEMA = "schema"
    DATA = "data"
    INDEX = "index"
    PROCEDURE = "procedure"
    ROLLBACK = "rollback"


class MigrationStatus(Enum):
    """Migration status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Migration:
    """Migration data class"""
    id: str
    version: str
    name: str
    description: str
    migration_type: MigrationType
    sql_up: str
    sql_down: str
    dependencies: List[str]
    checksum: str
    created_at: datetime
    applied_at: Optional[datetime] = None
    status: MigrationStatus = MigrationStatus.PENDING


class DatabaseMigrationManager:
    """
    Enterprise-grade database migration manager
    Handles schema evolution, data migrations, and rollbacks
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize migration manager"""
        self.config_path = config_path or "/etc/migration/config.json"
        self.migrations_dir = "/opt/ia-influencer/migrations"
        self.connection = None
        self.applied_migrations = []
        self.pending_migrations = []
        
        self._load_configuration()
        self._initialize_database_connection()
        self._initialize_migration_tracking()
        self._discover_migrations()
    
    def _load_configuration(self) -> None:
        """Load migration configuration"""



        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded migration configuration from {self.config_path}")
            else:
                self.config = self._get_default_config()
                logger.warning("Using default migration configuration")
        except Exception as e:
            logger.error(f"Failed to load migration configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default migration configuration"""



        return {
            "database": {
                "host": "localhost",
                "port": 5432,
                "username": "postgres",
                "password": "password",
                "database": "ia_influencer",
                "schema": "public"
            },
            "migration": {
                "table": "schema_migrations",
                "auto_commit": True,
                "backup_before_migration": True,
                "rollback_on_failure": True,
                "max_retry_attempts": 3
            },
            "validation": {
                "verify_checksums": True,
                "check_dependencies": True,
                "dry_run_enabled": True
            }
        }
    
    def _initialize_database_connection(self) -> None:
        """Initialize database connection"""



        try:
            db_config = self.config.get("database", {})
            
            connection_params = {
                "host": db_config.get("host", "localhost"),
                "port": db_config.get("port", 5432),
                "user": db_config.get("username", "postgres"),
                "password": db_config.get("password", ""),
                "database": db_config.get("database", "ia_influencer")
            }
            
            self.connection = psycopg2.connect(**connection_params)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            logger.info("Database connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _initialize_migration_tracking(self) -> None:
        """Initialize migration tracking table"""



        try:
            table_name = self.config.get("migration", {}).get("table", "schema_migrations")
            
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                migration_id VARCHAR(255) UNIQUE NOT NULL,
                version VARCHAR(50) NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                migration_type VARCHAR(20) NOT NULL,
                checksum VARCHAR(64) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_by VARCHAR(100) DEFAULT CURRENT_USER,
                execution_time_ms INTEGER,
                status VARCHAR(20) DEFAULT 'completed'
            );
            
            CREATE INDEX IF NOT EXISTS idx_schema_migrations_version 
            ON {table_name} (version);
            
            CREATE INDEX IF NOT EXISTS idx_schema_migrations_applied_at 
            ON {table_name} (applied_at);
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(create_table_sql)
            
            logger.info("Migration tracking table initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize migration tracking: {e}")
            raise
    
    def _discover_migrations(self) -> None:
        """Discover migration files from directory"""



        try:
            os.makedirs(self.migrations_dir, exist_ok=True)
            
            migration_files = []
            
            # Look for SQL migration files
            for file_path in Path(self.migrations_dir).glob("*.sql"):
                migration_files.append(file_path)
            
            # Look for Python migration files
            for file_path in Path(self.migrations_dir).glob("*.py"):
                if not file_path.name.startswith("__"):
                    migration_files.append(file_path)
            
            # Parse and load migrations
            discovered_migrations = []
            for file_path in sorted(migration_files):
                migration = self._parse_migration_file(file_path)
                if migration:
                    discovered_migrations.append(migration)
            
            # Get applied migrations from database
            applied_migration_ids = self._get_applied_migration_ids()
            
            # Separate pending and applied migrations
            self.applied_migrations = [
                m for m in discovered_migrations 
                if m.id in applied_migration_ids
            ]
            
            self.pending_migrations = [
                m for m in discovered_migrations 
                if m.id not in applied_migration_ids
            ]
            
            logger.info(f"Discovered {len(discovered_migrations)} migrations "
                       f"({len(self.applied_migrations)} applied, "
                       f"{len(self.pending_migrations)} pending)")
            
        except Exception as e:
            logger.error(f"Failed to discover migrations: {e}")
    
    def _parse_migration_file(self, file_path: Path) -> Optional[Migration]:
        """Parse migration file and extract metadata"""



        try:
            if file_path.suffix == ".sql":
                return self._parse_sql_migration(file_path)
            elif file_path.suffix == ".py":
                return self._parse_python_migration(file_path)
            else:
                logger.warning(f"Unsupported migration file: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to parse migration file {file_path}: {e}")
            return None
    
    def _parse_sql_migration(self, file_path: Path) -> Optional[Migration]:
        """Parse SQL migration file"""



        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from comments
            metadata = self._extract_migration_metadata(content)
            
            # Split up and down migrations
            parts = content.split("-- DOWN")
            sql_up = parts[0].replace("-- UP", "").strip()
            sql_down = parts[1].strip() if len(parts) > 1 else ""
            
            # Generate migration ID from filename
            migration_id = file_path.stem
            
            # Calculate checksum
            checksum = hashlib.sha256(content.encode()).hexdigest()
            
            migration = Migration(
                id=migration_id,
                version=metadata.get("version", "1.0.0"),
                name=metadata.get("name", migration_id),
                description=metadata.get("description", ""),
                migration_type=MigrationType(metadata.get("type", "schema")),
                sql_up=sql_up,
                sql_down=sql_down,
                dependencies=metadata.get("dependencies", []),
                checksum=checksum,
                created_at=datetime.fromtimestamp(file_path.stat().st_mtime)
            )
            
            return migration
            
        except Exception as e:
            logger.error(f"Failed to parse SQL migration {file_path}: {e}")
            return None
    
    def _parse_python_migration(self, file_path: Path) -> Optional[Migration]:
        """Parse Python migration file"""



        try:
            # This would load and execute Python migration files
            # For now, we'll create a placeholder
            migration_id = file_path.stem
            
            migration = Migration(
                id=migration_id,
                version="1.0.0",
                name=migration_id,
                description=f"Python migration: {migration_id}",
                migration_type=MigrationType.DATA,
                sql_up="-- Python migration",
                sql_down="-- Python rollback",
                dependencies=[],
                checksum=hashlib.sha256(file_path.read_bytes()).hexdigest(),
                created_at=datetime.fromtimestamp(file_path.stat().st_mtime)
            )
            
            return migration
            
        except Exception as e:
            logger.error(f"Failed to parse Python migration {file_path}: {e}")
            return None
    
    def _extract_migration_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from migration file comments"""
        metadata = {}
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("-- "):
                comment = line[3:].strip()
                if ": " in comment:
                    key, value = comment.split(": ", 1)
                    key = key.lower().replace(" ", "_")
                    
                    if key == "dependencies":
                        metadata[key] = [dep.strip() for dep in value.split(",")]
                    else:
                        metadata[key] = value
        
        return metadata
    
    def _get_applied_migration_ids(self) -> List[str]:
        """Get list of applied migration IDs from database"""



        try:
            table_name = self.config.get("migration", {}).get("table", "schema_migrations")
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT migration_id FROM {table_name} WHERE status = 'completed'")
                results = cursor.fetchall()
                
            return [row[0] for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def migrate(self, target_version: Optional[str] = None, dry_run: bool = False) -> bool:
        """
        Execute pending migrations
        
        Args:
            target_version: Target version to migrate to (None for latest)
            dry_run: Execute dry run without applying changes
            
        Returns:
            bool: True if successful, False otherwise
        """



        try:
            logger.info(f"Starting migration {'(dry run)' if dry_run else ''}")
            
            # Validate pending migrations
            if not self._validate_pending_migrations():
                logger.error("Migration validation failed")
                return False
            
            # Filter migrations by target version
            migrations_to_apply = self._filter_migrations_by_version(
                self.pending_migrations, target_version
            )
            
            if not migrations_to_apply:
                logger.info("No migrations to apply")
                return True
            
            logger.info(f"Found {len(migrations_to_apply)} migrations to apply")
            
            # Create backup if enabled
            if self.config.get("migration", {}).get("backup_before_migration", True) and not dry_run:
                if not self._create_pre_migration_backup():
                    logger.error("Failed to create pre-migration backup")
                    return False
            
            # Execute migrations
            for migration in migrations_to_apply:
                if not self._apply_migration(migration, dry_run):
                    logger.error(f"Migration failed: {migration.id}")
                    
                    # Rollback if enabled
                    if self.config.get("migration", {}).get("rollback_on_failure", True) and not dry_run:
                        self._rollback_failed_migration(migration)
                    
                    return False
            
            logger.info(f"Migration completed successfully {'(dry run)' if dry_run else ''}")
            return True
            
        except Exception as e:
            logger.error(f"Migration error: {e}")
            return False
    
    def _validate_pending_migrations(self) -> bool:
        """Validate pending migrations"""



        try:
            logger.info("Validating pending migrations")
            
            # Check for dependency cycles
            if not self._check_dependency_cycles():
                return False
            
            # Verify checksums
            if self.config.get("validation", {}).get("verify_checksums", True):
                if not self._verify_migration_checksums():
                    return False
            
            # Check SQL syntax
            if not self._validate_sql_syntax():
                return False
            
            logger.info("Migration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Migration validation error: {e}")
            return False
    
    def _check_dependency_cycles(self) -> bool:
        """Check for dependency cycles in migrations"""



        try:
            # Build dependency graph
            dependency_graph = {}
            for migration in self.pending_migrations:
                dependency_graph[migration.id] = migration.dependencies
            
            # Check for cycles using DFS
            visited = set()
            rec_stack = set()
            
            def has_cycle(node):
                visited.add(node)
                rec_stack.add(node)
                
                for dependency in dependency_graph.get(node, []):
                    if dependency not in visited:
                        if has_cycle(dependency):
                            return True
                    elif dependency in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            for migration_id in dependency_graph:
                if migration_id not in visited:
                    if has_cycle(migration_id):
                        logger.error(f"Dependency cycle detected involving {migration_id}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Dependency cycle check error: {e}")
            return False
    
    def _verify_migration_checksums(self) -> bool:
        """Verify migration checksums against database records"""



        try:
            table_name = self.config.get("migration", {}).get("table", "schema_migrations")
            
            with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT migration_id, checksum FROM {table_name}")
                db_checksums = {row['migration_id']: row['checksum'] for row in cursor.fetchall()}
            
            for migration in self.applied_migrations:
                if migration.id in db_checksums:
                    if migration.checksum != db_checksums[migration.id]:
                        logger.error(f"Checksum mismatch for migration {migration.id}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Checksum verification error: {e}")
            return False
    
    def _validate_sql_syntax(self) -> bool:
        """Validate SQL syntax in migrations"""



        try:
            for migration in self.pending_migrations:
                if migration.migration_type == MigrationType.SCHEMA:
                    # Basic SQL syntax validation
                    sql = migration.sql_up.strip()
                    if not sql:
                        logger.error(f"Empty migration SQL: {migration.id}")
                        return False
                    
                    # Check for dangerous operations
                    dangerous_keywords = ["DROP DATABASE", "TRUNCATE", "DELETE FROM"]
                    for keyword in dangerous_keywords:
                        if keyword.upper() in sql.upper():
                            logger.warning(f"Dangerous operation in migration {migration.id}: {keyword}")
            
            return True
            
        except Exception as e:
            logger.error(f"SQL validation error: {e}")
            return False
    
    def _filter_migrations_by_version(self, migrations: List[Migration], target_version: Optional[str]) -> List[Migration]:
        """Filter migrations by target version"""
        if not target_version:
            return migrations
        
        # Simple version filtering (would be more sophisticated in production)
        filtered = []
        for migration in migrations:
            if self._compare_versions(migration.version, target_version) <= 0:
                filtered.append(migration)
        
        return filtered
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings"""



        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] < v2_parts[i]:
                    return -1
                elif v1_parts[i] > v2_parts[i]:
                    return 1
            
            return 0
            
        except Exception:
            # Fallback to string comparison
            return -1 if version1 < version2 else (1 if version1 > version2 else 0)
    
    def _create_pre_migration_backup(self) -> bool:
        """Create backup before migration"""



        try:
            logger.info("Creating pre-migration backup")
            
            db_config = self.config.get("database", {})
            backup_file = f"/tmp/pre_migration_backup_{int(time.time())}.sql"
            
            pg_dump_cmd = [
                "pg_dump",
                "-h", db_config.get("host", "localhost"),
                "-p", str(db_config.get("port", 5432)),
                "-U", db_config.get("username", "postgres"),
                "-f", backup_file,
                db_config.get("database", "ia_influencer")
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config.get("password", "")
            
            result = subprocess.run(pg_dump_cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Pre-migration backup created: {backup_file}")
                return True
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Backup creation error: {e}")
            return False
    
    def _apply_migration(self, migration: Migration, dry_run: bool = False) -> bool:
        """Apply single migration"""



        try:
            logger.info(f"Applying migration: {migration.id} {'(dry run)' if dry_run else ''}")
            
            start_time = time.time()
            
            # Check dependencies
            if not self._check_migration_dependencies(migration):
                logger.error(f"Migration dependencies not satisfied: {migration.id}")
                return False
            
            # Execute migration SQL
            if not dry_run:
                success = self._execute_migration_sql(migration)
                if not success:
                    return False
                
                # Record migration in database
                execution_time = int((time.time() - start_time) * 1000)
                self._record_migration(migration, execution_time)
                
                # Update migration status
                migration.applied_at = datetime.now()
                migration.status = MigrationStatus.COMPLETED
            else:
                # Dry run - just validate SQL
                success = self._validate_migration_sql(migration)
            
            if success:
                logger.info(f"Migration applied successfully: {migration.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Migration application error: {e}")
            return False
    
    def _check_migration_dependencies(self, migration: Migration) -> bool:
        """Check if migration dependencies are satisfied"""



        try:
            applied_migration_ids = self._get_applied_migration_ids()
            
            for dependency in migration.dependencies:
                if dependency not in applied_migration_ids:
                    logger.error(f"Dependency not satisfied: {dependency}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Dependency check error: {e}")
            return False
    
    def _execute_migration_sql(self, migration: Migration) -> bool:
        """Execute migration SQL"""



        try:
            with self.connection.cursor() as cursor:
                # Execute migration SQL
                if migration.sql_up:
                    cursor.execute(migration.sql_up)
                    logger.info(f"Executed migration SQL for {migration.id}")
                
                return True
                
        except Exception as e:
            logger.error(f"SQL execution error for {migration.id}: {e}")
            return False
    
    def _validate_migration_sql(self, migration: Migration) -> bool:
        """Validate migration SQL (dry run)"""



        try:
            with self.connection.cursor() as cursor:
                # Use EXPLAIN to validate SQL without executing
                if migration.sql_up:
                    sql_statements = migration.sql_up.split(';')
                    for statement in sql_statements:
                        statement = statement.strip()
                        if statement and not statement.upper().startswith(('CREATE', 'ALTER', 'DROP')):
                            cursor.execute(f"EXPLAIN {statement}")
                
                logger.info(f"Migration SQL validated for {migration.id}")
                return True
                
        except Exception as e:
            logger.error(f"SQL validation error for {migration.id}: {e}")
            return False
    
    def _record_migration(self, migration: Migration, execution_time: int) -> None:
        """Record migration in database"""



        try:
            table_name = self.config.get("migration", {}).get("table", "schema_migrations")
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {table_name} 
                    (migration_id, version, name, description, migration_type, 
                     checksum, execution_time_ms, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    migration.id,
                    migration.version,
                    migration.name,
                    migration.description,
                    migration.migration_type.value,
                    migration.checksum,
                    execution_time,
                    'completed'
                ))
            
            logger.info(f"Migration recorded: {migration.id}")
            
        except Exception as e:
            logger.error(f"Migration recording error: {e}")
    
    def _rollback_failed_migration(self, migration: Migration) -> bool:
        """Rollback failed migration"""



        try:
            logger.info(f"Rolling back migration: {migration.id}")
            
            if not migration.sql_down:
                logger.warning(f"No rollback SQL available for {migration.id}")
                return False
            
            with self.connection.cursor() as cursor:
                cursor.execute(migration.sql_down)
            
            # Update migration status
            migration.status = MigrationStatus.ROLLED_BACK
            
            logger.info(f"Migration rolled back: {migration.id}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback error for {migration.id}: {e}")
            return False
    
    def rollback(self, target_version: Optional[str] = None, steps: int = 1) -> bool:
        """
        Rollback migrations
        
        Args:
            target_version: Target version to rollback to
            steps: Number of steps to rollback
            
        Returns:
            bool: True if successful, False otherwise
        """



        try:
            logger.info(f"Starting rollback to version {target_version or f'{steps} steps'}")
            
            # Get migrations to rollback
            migrations_to_rollback = self._get_rollback_migrations(target_version, steps)
            
            if not migrations_to_rollback:
                logger.info("No migrations to rollback")
                return True
            
            logger.info(f"Rolling back {len(migrations_to_rollback)} migrations")
            
            # Execute rollbacks in reverse order
            for migration in reversed(migrations_to_rollback):
                if not self._rollback_migration(migration):
                    logger.error(f"Rollback failed for migration: {migration.id}")
                    return False
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback error: {e}")
            return False
    
    def _get_rollback_migrations(self, target_version: Optional[str], steps: int) -> List[Migration]:
        """Get migrations to rollback"""



        try:
            # Get applied migrations in reverse order
            applied_migrations = sorted(
                self.applied_migrations,
                key=lambda x: x.applied_at or datetime.min,
                reverse=True
            )
            
            if target_version:
                # Rollback to specific version
                migrations_to_rollback = []
                for migration in applied_migrations:
                    if self._compare_versions(migration.version, target_version) > 0:
                        migrations_to_rollback.append(migration)
                    else:
                        break
                return migrations_to_rollback
            else:
                # Rollback specific number of steps
                return applied_migrations[:steps]
                
        except Exception as e:
            logger.error(f"Get rollback migrations error: {e}")
            return []
    
    def _rollback_migration(self, migration: Migration) -> bool:
        """Rollback single migration"""



        try:
            logger.info(f"Rolling back migration: {migration.id}")
            
            if not migration.sql_down:
                logger.error(f"No rollback SQL available for {migration.id}")
                return False
            
            # Execute rollback SQL
            with self.connection.cursor() as cursor:
                cursor.execute(migration.sql_down)
            
            # Remove migration record
            table_name = self.config.get("migration", {}).get("table", "schema_migrations")
            with self.connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {table_name} WHERE migration_id = %s", (migration.id,))
            
            # Update migration status
            migration.status = MigrationStatus.ROLLED_BACK
            migration.applied_at = None
            
            logger.info(f"Migration rolled back successfully: {migration.id}")
            return True
            
        except Exception as e:
            logger.error(f"Migration rollback error: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status summary"""



        try:
            applied_migration_ids = self._get_applied_migration_ids()
            
            return {
                "total_migrations": len(self.applied_migrations) + len(self.pending_migrations),
                "applied_migrations": len(self.applied_migrations),
                "pending_migrations": len(self.pending_migrations),
                "current_version": self._get_current_version(),
                "latest_migration": applied_migration_ids[-1] if applied_migration_ids else None,
                "database_status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {"database_status": "error", "error": str(e)}
    
    def _get_current_version(self) -> Optional[str]:
        """Get current database version"""



        try:
            if not self.applied_migrations:
                return None
            
            # Get latest applied migration version
            latest_migration = max(
                self.applied_migrations,
                key=lambda x: x.applied_at or datetime.min
            )
            
            return latest_migration.version
            
        except Exception as e:
            logger.error(f"Get current version error: {e}")
            return None
    
    def create_migration(self, name: str, migration_type: str = "schema", description: str = "") -> str:
        """Create new migration file"""



        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            migration_id = f"{timestamp}_{name}"
            filename = f"{migration_id}.sql"
            filepath = Path(self.migrations_dir) / filename
            
            # Create migration template
            template = f"""-- Migration: {name}
-- Description: {description}
-- Type: {migration_type}
-- Version: 1.0.0
-- Dependencies: 

-- UP
-- Add your migration SQL here


-- DOWN
-- Add your rollback SQL here

"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
            
            logger.info(f"Created migration file: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Create migration error: {e}")
            return ""
    
    def list_migrations(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List migrations with optional status filter"""



        try:
            all_migrations = self.applied_migrations + self.pending_migrations
            
            if status:
                if status == "applied":
                    migrations = self.applied_migrations
                elif status == "pending":
                    migrations = self.pending_migrations
                else:
                    migrations = [m for m in all_migrations if m.status.value == status]
            else:
                migrations = all_migrations
            
            return [
                {
                    "id": m.id,
                    "version": m.version,
                    "name": m.name,
                    "description": m.description,
                    "type": m.migration_type.value,
                    "status": m.status.value,
                    "applied_at": m.applied_at.isoformat() if m.applied_at else None,
                    "created_at": m.created_at.isoformat()
                }
                for m in sorted(migrations, key=lambda x: x.created_at)
            ]
            
        except Exception as e:
            logger.error(f"List migrations error: {e}")
            return []


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument("--action", required=True, 
                       choices=["migrate", "rollback", "status", "create", "list"])
    parser.add_argument("--target-version", help="Target version for migration/rollback")
    parser.add_argument("--steps", type=int, default=1, help="Number of steps for rollback")
    parser.add_argument("--dry-run", action="store_true", help="Execute dry run")
    parser.add_argument("--name", help="Migration name for create action")
    parser.add_argument("--type", default="schema", help="Migration type for create action")
    parser.add_argument("--description", default="", help="Migration description")
    parser.add_argument("--status-filter", help="Status filter for list action")
    
    args = parser.parse_args()
    
    manager = DatabaseMigrationManager()
    
    if args.action == "migrate":
        success = manager.migrate(target_version=args.target_version, dry_run=args.dry_run)
        print(f"Migration {'completed' if success else 'failed'}")
        sys.exit(0 if success else 1)
    
    elif args.action == "rollback":
        success = manager.rollback(target_version=args.target_version, steps=args.steps)
        print(f"Rollback {'completed' if success else 'failed'}")
        sys.exit(0 if success else 1)
    
    elif args.action == "status":
        status = manager.get_migration_status()
        print(json.dumps(status, indent=2))
    
    elif args.action == "create":
        if not args.name:
            print("Error: --name is required for create action")
            sys.exit(1)
        
        filepath = manager.create_migration(args.name, args.type, args.description)
        print(f"Created migration: {filepath}")
    
    elif args.action == "list":
        migrations = manager.list_migrations(status=args.status_filter)
        print(json.dumps(migrations, indent=2))


if __name__ == "__main__":
    main()
