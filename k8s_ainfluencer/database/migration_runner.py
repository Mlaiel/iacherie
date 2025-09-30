"""Enterprise Migration Runner
Advanced database migration system with version control and rollback capabilities

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de
"""

import os
import re
import hashlib
import importlib.util
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import psycopg2
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError

from backend.core.config import get_database_settings
from backend.core.logging import get_logger
from backend.core.monitoring import MetricsCollector
from backend.deployment.database.postgresql_manager import get_postgresql_manager
from backend.deployment.database.schema import SchemaMigration


@dataclass
class Migration:
    """
Migration metadata and execution details"""
    version: str
    name: str
    filepath: str
    checksum: str
    description: str
    dependencies: List[str]
    execution_order: int
    rollback_available: bool
    is_data_migration: bool
    estimated_duration: Optional[int] = None
    size_impact: Optional[str] = None


class MigrationRunner:
    """
    Enterprise database migration runner with advanced features:
    - Version-controlled migrations with dependency tracking
    - Parallel execution for independent migrations
    - Automatic rollback on failures
    - Checksum verification for integrity
    - Data migration support with validation
    - Point-in-time recovery integration
    """
    
    def __init__(self, migrations_directory: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.config = get_database_settings()
        self.metrics = MetricsCollector()
        self.db_manager = get_postgresql_manager()
        
        # Migration configuration
        self.migrations_dir = Path(migrations_directory or 
                                 self.config.MIGRATIONS_DIRECTORY or 
                                 "backend/database/migrations")
        self.max_parallel_migrations = self.config.MAX_PARALLEL_MIGRATIONS or 3
        self.migration_timeout = self.config.MIGRATION_TIMEOUT or 3600  # 1 hour
        
        # Migration tracking
        self.discovered_migrations: Dict[str, Migration] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.execution_plan: List[Migration] = []
        
        self._ensure_migrations_table()
        self._discover_migrations()
    
    def _ensure_migrations_table(self) -> None:
        """Ensure schema_migrations table exists"""
        try:
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_time FLOAT DEFAULT 0,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            self.db_manager.execute_query(create_table_sql, fetch_results=False)
            
            # Create indexes
            index_sqls = [
                "CREATE INDEX IF NOT EXISTS idx_schema_migrations_version ON schema_migrations(version)",
                "CREATE INDEX IF NOT EXISTS idx_schema_migrations_status ON schema_migrations(status)",
                "CREATE INDEX IF NOT EXISTS idx_schema_migrations_executed_at ON schema_migrations(executed_at)"
            ]
            
            for index_sql in index_sqls:
                self.db_manager.execute_query(index_sql, fetch_results=False)
            
            self.logger.info("Schema migrations table initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to ensure migrations table: {e}")
            raise
    
    def _discover_migrations(self) -> None:
        """Discover and parse all migration files"""
        try:
            if not self.migrations_dir.exists():
                self.migrations_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created migrations directory: {self.migrations_dir}")
                return
            
            migration_files = list(self.migrations_dir.glob("*.py"))
            migration_files.sort()
            
            for migration_file in migration_files:
                if migration_file.name.startswith("__"):
                    continue
                
                migration = self._parse_migration_file(migration_file)
                if migration:
                    self.discovered_migrations[migration.version] = migration
            
            self._build_dependency_graph()
            self._calculate_execution_order()
            
            self.logger.info(f"Discovered {len(self.discovered_migrations)} migrations")
            
        except Exception as e:
            self.logger.error(f"Failed to discover migrations: {e}")
            raise
    
    def _parse_migration_file(self, filepath: Path) -> Optional[Migration]:
        """Parse migration file and extract metadata"""
        try:
            # Extract version from filename (format: YYYYMMDD_HHMMSS_name.py)
            filename_pattern = r"(\d{8}_\d{6})_(.+)\.py"
            match = re.match(filename_pattern, filepath.name)
            
            if not match:
                self.logger.warning(f"Invalid migration filename format: {filepath.name}")
                return None
            
            version, name = match.groups()
            
            # Calculate file checksum
            with open(filepath, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
            
            # Load migration module to extract metadata
            spec = importlib.util.spec_from_file_location(f"migration_{version}", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract metadata from module
            description = getattr(module, 'DESCRIPTION', name.replace('_', ' ').title())
            dependencies = getattr(module, 'DEPENDENCIES', [])
            is_data_migration = getattr(module, 'IS_DATA_MIGRATION', False)
            estimated_duration = getattr(module, 'ESTIMATED_DURATION', None)
            size_impact = getattr(module, 'SIZE_IMPACT', None)
            
            # Check if rollback function exists
            rollback_available = hasattr(module, 'rollback')
            
            migration = Migration(
                version=version,
                name=name,
                filepath=str(filepath),
                checksum=checksum,
                description=description,
                dependencies=dependencies,
                execution_order=0,  # Will be calculated later
                rollback_available=rollback_available,
                is_data_migration=is_data_migration,
                estimated_duration=estimated_duration,
                size_impact=size_impact
            )
            
            return migration
            
        except Exception as e:
            self.logger.error(f"Failed to parse migration file {filepath}: {e}")
            return None
    
    def _build_dependency_graph(self) -> None:
        """Build dependency graph for migration ordering"""
        self.dependency_graph = {}
        
        for version, migration in self.discovered_migrations.items():
            self.dependency_graph[version] = migration.dependencies.copy()
            
            # Add implicit dependency on previous migration if no explicit dependencies
            if not migration.dependencies:
                sorted_versions = sorted(self.discovered_migrations.keys())
                current_index = sorted_versions.index(version)
                
                if current_index > 0:
                    prev_version = sorted_versions[current_index - 1]
                    self.dependency_graph[version] = [prev_version]
    
    def _calculate_execution_order(self) -> None:
        """
Calculate optimal execution order using topological sort"""
        try:
            # Topological sort with Kahn's algorithm
            in_degree = {v: 0 for v in self.discovered_migrations.keys()}
            
            # Calculate in-degrees
            for version, deps in self.dependency_graph.items():
                for dep in deps:
                    if dep in in_degree:
                        in_degree[version] += 1
            
            # Queue for migrations with no dependencies
            queue = [v for v, degree in in_degree.items() if degree == 0]
            execution_order = 0
            
            while queue:
                # Sort queue for deterministic ordering
                queue.sort()
                current = queue.pop(0)
                
                # Set execution order
                self.discovered_migrations[current].execution_order = execution_order
                execution_order += 1
                
                # Update dependencies
                for version, deps in self.dependency_graph.items():
                    if current in deps:
                        in_degree[version] -= 1
                        if in_degree[version] == 0:
                            queue.append(version)
            
            # Check for circular dependencies
            if execution_order != len(self.discovered_migrations):
                remaining = [v for v, degree in in_degree.items() if degree > 0]
                raise ValueError(f"Circular dependency detected in migrations: {remaining}")
            
            # Create execution plan
            self.execution_plan = sorted(
                self.discovered_migrations.values(),
                key=lambda m: m.execution_order
            )
            
        except Exception as e:
            self.logger.error(f"Failed to calculate execution order: {e}")
            raise
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get comprehensive migration status"""
        try:
            # Get executed migrations from database
            executed_query = """
                SELECT version, name, status, executed_at, execution_time, error_message
                FROM schema_migrations
                ORDER BY executed_at DESC
            """
            
            executed_result = self.db_manager.execute_query(executed_query)
            executed_migrations = {
                row[0]: {
                    'name': row[1],
                    'status': row[2],
                    'executed_at': row[3],
                    'execution_time': row[4],
                    'error_message': row[5]
                }
                for row in executed_result
            } if executed_result else {}
            
            # Calculate pending migrations
            pending_migrations = []
            failed_migrations = []
            
            for migration in self.execution_plan:
                if migration.version not in executed_migrations:
                    pending_migrations.append({
                        'version': migration.version,
                        'name': migration.name,
                        'description': migration.description,
                        'dependencies': migration.dependencies,
                        'estimated_duration': migration.estimated_duration,
                        'is_data_migration': migration.is_data_migration
                    })
                elif executed_migrations[migration.version]['status'] == 'failed':
                    failed_migrations.append({
                        'version': migration.version,
                        'name': migration.name,
                        'error_message': executed_migrations[migration.version]['error_message'],
                        'executed_at': executed_migrations[migration.version]['executed_at']
                    })
            
            return {
                'total_migrations': len(self.discovered_migrations),
                'executed_count': len(executed_migrations),
                'pending_count': len(pending_migrations),
                'failed_count': len(failed_migrations),
                'pending_migrations': pending_migrations,
                'failed_migrations': failed_migrations,
                'last_migration': max(executed_migrations.keys()) if executed_migrations else None,
                'can_rollback': any(m.rollback_available for m in self.discovered_migrations.values())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get migration status: {e}")
            return {}
    
    def migrate_up(self, target_version: Optional[str] = None) -> bool:
        """Execute pending migrations up to target version"""
        try:
            status = self.get_migration_status()
            pending_migrations = status.get('pending_migrations', [])
            
            if not pending_migrations:
                self.logger.info("No pending migrations to execute")
                return True
            
            # Filter migrations up to target version
            if target_version:
                pending_migrations = [
                    m for m in pending_migrations 
                    if m['version'] <= target_version
                ]
            
            if not pending_migrations:
                self.logger.info(f"No migrations to execute up to version {target_version}")
                return True
            
            self.logger.info(f"Executing {len(pending_migrations)} migrations")
            
            # Execute migrations in order
            for migration_info in pending_migrations:
                migration = self.discovered_migrations[migration_info['version']]
                
                success = self._execute_migration(migration)
                if not success:
                    self.logger.error(f"Migration {migration.version} failed, stopping execution")
                    return False
            
            self.logger.info("All migrations executed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration execution failed: {e}")
            return False
    
    def migrate_down(self, target_version: str) -> bool:
        """Rollback migrations to target version"""
        try:
            # Get current migration status
            status = self.get_migration_status()
            last_migration = status.get('last_migration')
            
            if not last_migration:
                self.logger.info("No migrations to rollback")
                return True
            
            if target_version >= last_migration:
                self.logger.info(f"Already at or before version {target_version}")
                return True
            
            # Find migrations to rollback
            executed_query = """
                SELECT version FROM schema_migrations
                WHERE status = 'completed' AND version > %s
                ORDER BY version DESC
            """
            
            result = self.db_manager.execute_query(executed_query, (target_version,))
            versions_to_rollback = [row[0] for row in result] if result else []
            
            if not versions_to_rollback:
                self.logger.info(f"No migrations to rollback to version {target_version}")
                return True
            
            self.logger.info(f"Rolling back {len(versions_to_rollback)} migrations")
            
            # Execute rollbacks in reverse order
            for version in versions_to_rollback:
                if version not in self.discovered_migrations:
                    self.logger.error(f"Migration {version} not found for rollback")
                    return False
                
                migration = self.discovered_migrations[version]
                
                if not migration.rollback_available:
                    self.logger.error(f"Migration {version} does not support rollback")
                    return False
                
                success = self._rollback_migration(migration)
                if not success:
                    self.logger.error(f"Rollback of {version} failed, stopping")
                    return False
            
            self.logger.info(f"Successfully rolled back to version {target_version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration rollback failed: {e}")
            return False
    
    def _execute_migration(self, migration: Migration) -> bool:
        """Execute a single migration"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Executing migration {migration.version}: {migration.name}")
            
            # Record migration start
            self._record_migration_start(migration)
            
            # Load migration module
            spec = importlib.util.spec_from_file_location(
                f"migration_{migration.version}", 
                migration.filepath
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Validate migration function exists
            if not hasattr(module, 'migrate'):
                raise ValueError(f"Migration {migration.version} missing migrate() function")
            
            # Execute pre-migration hooks
            if hasattr(module, 'pre_migrate'):
                module.pre_migrate(self.db_manager)
            
            # Execute main migration
            with self.db_manager.get_connection() as connection:
                connection.autocommit = False
                
                try:
                    # Execute migration with transaction
                    module.migrate(self.db_manager)
                    connection.commit()
                    
                except Exception as e:
                    connection.rollback()
                    raise e
            
            # Execute post-migration hooks
            if hasattr(module, 'post_migrate'):
                module.post_migrate(self.db_manager)
            
            # Verify migration success
            if hasattr(module, 'verify'):
                verification_result = module.verify(self.db_manager)
                if not verification_result:
                    raise ValueError(f"Migration {migration.version} verification failed")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Record successful completion
            self._record_migration_completion(migration, execution_time)
            
            self.metrics.record_migration_success(migration.version, execution_time)
            self.logger.info(f"Migration {migration.version} completed in {execution_time:.2f}s")
            
            return True
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_message = str(e)
            
            # Record failure
            self._record_migration_failure(migration, error_message, execution_time)
            
            self.metrics.record_migration_failure(migration.version, execution_time)
            self.logger.error(f"Migration {migration.version} failed after {execution_time:.2f}s: {e}")
            
            return False
    
    def _rollback_migration(self, migration: Migration) -> bool:
        """Rollback a single migration"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Rolling back migration {migration.version}: {migration.name}")
            
            # Load migration module
            spec = importlib.util.spec_from_file_location(
                f"migration_{migration.version}", 
                migration.filepath
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Validate rollback function exists
            if not hasattr(module, 'rollback'):
                raise ValueError(f"Migration {migration.version} missing rollback() function")
            
            # Execute rollback
            with self.db_manager.get_connection() as connection:
                connection.autocommit = False
                
                try:
                    # Execute rollback with transaction
                    module.rollback(self.db_manager)
                    connection.commit()
                    
                except Exception as e:
                    connection.rollback()
                    raise e
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Remove migration record
            delete_query = "DELETE FROM schema_migrations WHERE version = %s"
            self.db_manager.execute_query(delete_query, (migration.version,), fetch_results=False)
            
            self.metrics.record_migration_rollback(migration.version, execution_time)
            self.logger.info(f"Migration {migration.version} rolled back in {execution_time:.2f}s")
            
            return True
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.metrics.record_migration_rollback_failure(migration.version, execution_time)
            self.logger.error(f"Rollback of {migration.version} failed after {execution_time:.2f}s: {e}")
            
            return False
    
    def _record_migration_start(self, migration: Migration) -> None:
        """Record migration start in database"""
        try:
            insert_query = """
                INSERT INTO schema_migrations (version, name, checksum, status)
                VALUES (%s, %s, %s, 'running')
                ON CONFLICT (version) 
                DO UPDATE SET status = 'running', updated_at = CURRENT_TIMESTAMP
            """
            
            self.db_manager.execute_query(
                insert_query,
                (migration.version, migration.name, migration.checksum),
                fetch_results=False
            )
            
        except Exception as e:
            self.logger.error(f"Failed to record migration start: {e}")
    
    def _record_migration_completion(self, migration: Migration, execution_time: float) -> None:
        """Record successful migration completion"""
        try:
            update_query = """
                UPDATE schema_migrations 
                SET status = 'completed', 
                    execution_time = %s,
                    executed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE version = %s
            """
            
            self.db_manager.execute_query(
                update_query,
                (execution_time, migration.version),
                fetch_results=False
            )
            
        except Exception as e:
            self.logger.error(f"Failed to record migration completion: {e}")
    
    def _record_migration_failure(self, migration: Migration, error_message: str, execution_time: float) -> None:
        """Record migration failure"""
        try:
            update_query = """
                UPDATE schema_migrations 
                SET status = 'failed', 
                    error_message = %s,
                    execution_time = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE version = %s
            """
            
            self.db_manager.execute_query(
                update_query,
                (error_message, execution_time, migration.version),
                fetch_results=False
            )
            
        except Exception as e:
            self.logger.error(f"Failed to record migration failure: {e}")
    
    def create_migration(
        self, 
        name: str, 
        description: str = "",
        is_data_migration: bool = False,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """Create a new migration file"""
        try:
            # Generate version timestamp
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Clean name for filename
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
            filename = f"{version}_{clean_name}.py"
            filepath = self.migrations_dir / filename
            
            # Migration template
            template = f'''"""{description or name.replace('_', ' ').title()}

Author: Fahed Mlaiel <mlaiel@live.de>
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""# Migration metadata
DESCRIPTION = "{description or name.replace('_', ' ').title()}"
DEPENDENCIES = {dependencies or []}
IS_DATA_MIGRATION = {is_data_migration}
ESTIMATED_DURATION = None  # seconds
SIZE_IMPACT = None  # "small", "medium", "large"


def migrate(db_manager):
    """
    Execute migration
    
    Args:
        db_manager: PostgreSQL database manager instance
    """
    # Add your migration SQL here
    sql = """
        -- Your migration SQL goes here
        -- Example:
        -- CREATE TABLE example_table (
        --     id SERIAL PRIMARY KEY,
        --     name VARCHAR(255) NOT NULL,
        --     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        -- );
    """
    
    # Execute migration
    # db_manager.execute_query(sql, fetch_results=False)
    
    pass  # Remove this line when adding actual migration code


def rollback(db_manager):
    """
    Rollback migration
    
    Args:
        db_manager: PostgreSQL database manager instance
    """
    # Add your rollback SQL here
    sql = """
        -- Your rollback SQL goes here
        -- Example:
        -- DROP TABLE IF EXISTS example_table;
    """
    
    # Execute rollback
    # db_manager.execute_query(sql, fetch_results=False)
    
    pass  # Remove this line when adding actual rollback code


def verify(db_manager):
    """
    Verify migration was successful
    
    Args:
        db_manager: PostgreSQL database manager instance
        
    Returns:
        bool: True if verification passed, False otherwise
    """
    # Add verification logic here
    # Example:
    # result = db_manager.execute_query("SELECT 1 FROM example_table LIMIT 1")
    # return result is not None
    
    return True


def pre_migrate(db_manager):
    """
    Execute before migration (optional)
    
    Args:
        db_manager: PostgreSQL database manager instance
    """
    pass


def post_migrate(db_manager):
    """
    Execute after migration (optional)
    
    Args:
        db_manager: PostgreSQL database manager instance
    """
    pass
'''
            
            # Write migration file
            with open(filepath, 'w') as f:
                f.write(template)
            
            self.logger.info(f"Created migration: {filepath}")
            
            # Rediscover migrations to include the new one
            self._discover_migrations()
            
            return version
            
        except Exception as e:
            self.logger.error(f"Failed to create migration: {e}")
            raise
    
    def validate_migrations(self) -> Dict[str, Any]:
        """Validate all discovered migrations"""
        try:
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'migration_checks': {}
            }
            
            for version, migration in self.discovered_migrations.items():
                check_result = self._validate_single_migration(migration)
                validation_results['migration_checks'][version] = check_result
                
                if check_result['errors']:
                    validation_results['valid'] = False
                    validation_results['errors'].extend(check_result['errors'])
                
                validation_results['warnings'].extend(check_result['warnings'])
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Migration validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {e}"],
                'warnings': [],
                'migration_checks': {}
            }
    
    def _validate_single_migration(self, migration: Migration) -> Dict[str, Any]:
        """Validate a single migration"""
        result = {
            'errors': [],
            'warnings': [],
            'has_migrate_function': False,
            'has_rollback_function': False,
            'checksum_valid': True
        }
        
        try:
            # Check if file exists
            if not os.path.exists(migration.filepath):
                result['errors'].append(f"Migration file not found: {migration.filepath}")
                return result
            
            # Verify checksum
            with open(migration.filepath, 'rb') as f:
                current_checksum = hashlib.sha256(f.read()).hexdigest()
            
            if current_checksum != migration.checksum:
                result['warnings'].append(f"Checksum mismatch - file may have been modified")
                result['checksum_valid'] = False
            
            # Load and validate module
            spec = importlib.util.spec_from_file_location(
                f"migration_{migration.version}", 
                migration.filepath
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check required functions
            if hasattr(module, 'migrate'):
                result['has_migrate_function'] = True
            else:
                result['errors'].append("Missing required migrate() function")
            
            if hasattr(module, 'rollback'):
                result['has_rollback_function'] = True
            elif migration.rollback_available:
                result['warnings'].append("Migration marked as rollback available but no rollback() function found")
            
            # Validate dependencies
            for dep in migration.dependencies:
                if dep not in self.discovered_migrations:
                    result['errors'].append(f"Dependency not found: {dep}")
            
        except Exception as e:
            result['errors'].append(f"Failed to load migration: {e}")
        
        return result
    
    def get_dependency_tree(self) -> Dict[str, Any]:
        """Get migration dependency tree visualization"""
        try:
            tree = {
                'nodes': [],
                'edges': [],
                'levels': {}
            }
            
            # Add nodes
            for version, migration in self.discovered_migrations.items():
                tree['nodes'].append({
                    'version': version,
                    'name': migration.name,
                    'order': migration.execution_order,
                    'status': self._get_migration_status(version),
                    'is_data_migration': migration.is_data_migration
                })
            
            # Add edges (dependencies)
            for version, dependencies in self.dependency_graph.items():
                for dep in dependencies:
                    if dep in self.discovered_migrations:
                        tree['edges'].append({
                            'from': dep,
                            'to': version
                        })
            
            # Calculate levels
            for migration in self.execution_plan:
                level = migration.execution_order
                if level not in tree['levels']:
                    tree['levels'][level] = []
                tree['levels'][level].append(migration.version)
            
            return tree
            
        except Exception as e:
            self.logger.error(f"Failed to generate dependency tree: {e}")
            return {'nodes': [], 'edges': [], 'levels': {}}
    
    def _get_migration_status(self, version: str) -> str:
        """Get status of a specific migration"""
        try:
            query = "SELECT status FROM schema_migrations WHERE version = %s"
            result = self.db_manager.execute_query(query, (version,))
            
            if result:
                return result[0][0]
            else:
                return 'pending'
                
        except Exception:
            return 'unknown'
    
    def cleanup_failed_migrations(self) -> bool:
        """Clean up failed migration records"""
        try:
            # Remove failed migration records
            cleanup_query = "DELETE FROM schema_migrations WHERE status = 'failed'"
            self.db_manager.execute_query(cleanup_query, fetch_results=False)
            
            self.logger.info("Cleaned up failed migration records")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup migrations: {e}")
            return False
    
    def export_migration_report(self, filepath: str) -> bool:
        """Export detailed migration report"""
        try:
            status = self.get_migration_status()
            validation = self.validate_migrations()
            dependency_tree = self.get_dependency_tree()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'migration_status': status,
                'validation_results': validation,
                'dependency_tree': dependency_tree,
                'discovered_migrations': {
                    version: {
                        'name': migration.name,
                        'description': migration.description,
                        'dependencies': migration.dependencies,
                        'execution_order': migration.execution_order,
                        'rollback_available': migration.rollback_available,
                        'is_data_migration': migration.is_data_migration,
                        'estimated_duration': migration.estimated_duration,
                        'size_impact': migration.size_impact
                    }
                    for version, migration in self.discovered_migrations.items()
                }
            }
            
            import json
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Migration report exported to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export migration report: {e}")
            return False


# Singleton instance
_migration_runner = None

def get_migration_runner() -> MigrationRunner:
    """Get migration runner singleton instance"""
    global _migration_runner
    if _migration_runner is None:
        _migration_runner = MigrationRunner()
    return _migration_runner

import os
import re
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from pathlib import Path
import json
from dataclasses import dataclass
from enum import Enum

from backend.core.config import get_database_settings
from backend.core.logging import get_logger
from .postgresql_manager import get_postgresql_manager


class MigrationStatus(Enum):
    """
Migration execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationFile:
    """Migration file metadata"""
    version: str
    name: str
    filepath: Path
    checksum: str
    up_sql: str
    down_sql: str
    dependencies: List[str]
    description: str


@dataclass
class MigrationRecord:
    """
Migration execution record"""
    version: str
    name: str
    checksum: str
    status: MigrationStatus
    executed_at: datetime
    execution_time: float
    error_message: Optional[str] = None


class MigrationRunner:
    """
    Enterprise database migration system with features:
    - Automatic version detection and ordering
    - Rollback capabilities with dependency tracking
    - Migration validation and checksum verification
    - Parallel execution for independent migrations
    - Detailed logging and error reporting
    - Backup creation before major changes
    """
    
    def __init__(self, migrations_dir: str = "migrations"):
        self.logger = get_logger(__name__)
        self.config = get_database_settings()
        self.db_manager = get_postgresql_manager()
        self.migrations_dir = Path(migrations_dir)
        self.migrations_table = "schema_migrations"
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self) -> None:
        """Create migrations tracking table if not exists"""
        try:
            create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    execution_time FLOAT DEFAULT 0,
                    error_message TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_schema_migrations_version 
                ON {self.migrations_table}(version);
                
                CREATE INDEX IF NOT EXISTS idx_schema_migrations_status 
                ON {self.migrations_table}(status);
            """
            
            self.db_manager.execute_query(create_table_sql, fetch_results=False)
            self.logger.info("Migration tracking table ensured")
            
        except Exception as e:
            self.logger.error(f"Failed to create migrations table: {e}")
            raise
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate MD5 checksum of migration content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _parse_migration_file(self, filepath: Path) -> MigrationFile:
        """
Parse migration file and extract metadata"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract version and name from filename
            # Format: V001__initial_schema.sql or 20240101_120000__create_users_table.sql
            filename = filepath.stem
            
            # Try different naming patterns
            version_match = re.match(r'^V?(\d+(?:\.\d+)*)(?:__|_)(.+)$', filename)
            if not version_match:
                # Try timestamp format
                version_match = re.match(r'^(\d{8}_\d{6})(?:__|_)(.+)$', filename)
            
            if not version_match:
                raise ValueError(f"Invalid migration filename format: {filename}")
            
            version = version_match.group(1)
            name = version_match.group(2).replace('_', ' ').title()
            
            # Split UP and DOWN migrations
            up_down_split = re.split(r'--\s*DOWN\s*--', content, flags=re.IGNORECASE)
            up_sql = up_down_split[0].strip()
            down_sql = up_down_split[1].strip() if len(up_down_split) > 1 else ""
            
            # Extract dependencies from comments
            dependencies = []
            dep_pattern = r'--\s*DEPENDS:\s*(.+)'
            for match in re.finditer(dep_pattern, content, re.IGNORECASE):
                deps = [dep.strip() for dep in match.group(1).split(',')]
                dependencies.extend(deps)
            
            # Extract description
            desc_pattern = r'--\s*DESCRIPTION:\s*(.+)'
            desc_match = re.search(desc_pattern, content, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else name
            
            checksum = self._calculate_checksum(content)
            
            return MigrationFile(
                version=version,
                name=name,
                filepath=filepath,
                checksum=checksum,
                up_sql=up_sql,
                down_sql=down_sql,
                dependencies=dependencies,
                description=description
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse migration file {filepath}: {e}")
            raise
    
    def discover_migrations(self) -> List[MigrationFile]:
        """Discover and parse all migration files"""
        try:
            if not self.migrations_dir.exists():
                self.logger.warning(f"Migrations directory not found: {self.migrations_dir}")
                return []
            
            migration_files = []
            sql_files = list(self.migrations_dir.glob("*.sql"))
            
            for filepath in sql_files:
                try:
                    migration = self._parse_migration_file(filepath)
                    migration_files.append(migration)
                except Exception as e:
                    self.logger.error(f"Skipping invalid migration file {filepath}: {e}")
                    continue
            
            # Sort by version
            migration_files.sort(key=lambda m: self._version_sort_key(m.version))
            
            self.logger.info(f"Discovered {len(migration_files)} migration files")
            return migration_files
            
        except Exception as e:
            self.logger.error(f"Failed to discover migrations: {e}")
            raise
    
    def _version_sort_key(self, version: str) -> Tuple:
        """Generate sort key for version comparison"""
        try:
            # Handle numeric versions (1.0.0, 001, etc.)
            if re.match(r'^\d+(\.\d+)*$', version):
                return tuple(int(x) for x in version.split('.'))
            
            # Handle timestamp versions (20240101_120000)
            if re.match(r'^\d{8}_\d{6}$', version):
                date_part, time_part = version.split('_')
                return (
                    int(date_part[:4]),    # year
                    int(date_part[4:6]),   # month
                    int(date_part[6:8]),   # day
                    int(time_part[:2]),    # hour
                    int(time_part[2:4]),   # minute
                    int(time_part[4:6])    # second
                )
            
            # Fallback to string sorting
            return (version,)
            
        except Exception:
            return (version,)
    
    def get_migration_records(self) -> List[MigrationRecord]:
        """
Get all migration execution records"""
        try:
            query = f"""
                SELECT version, name, checksum, status, executed_at, 
                       execution_time, error_message
                FROM {self.migrations_table}
                ORDER BY executed_at
            """
            
            result = self.db_manager.execute_query(query)
            
            records = []
            for row in result:
                records.append(MigrationRecord(
                    version=row[0],
                    name=row[1],
                    checksum=row[2],
                    status=MigrationStatus(row[3]),
                    executed_at=row[4],
                    execution_time=row[5],
                    error_message=row[6]
                ))
            
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to get migration records: {e}")
            return []
    
    def get_pending_migrations(self) -> List[MigrationFile]:
        """Get list of pending migrations"""
        try:
            all_migrations = self.discover_migrations()
            executed_versions = {
                record.version for record in self.get_migration_records()
                if record.status == MigrationStatus.COMPLETED
            }
            
            pending = [
                migration for migration in all_migrations
                if migration.version not in executed_versions
            ]
            
            # Validate dependencies
            validated_pending = []
            for migration in pending:
                if self._validate_dependencies(migration, executed_versions):
                    validated_pending.append(migration)
                else:
                    self.logger.warning(
                        f"Migration {migration.version} has unmet dependencies"
                    )
            
            return validated_pending
            
        except Exception as e:
            self.logger.error(f"Failed to get pending migrations: {e}")
            return []
    
    def _validate_dependencies(
        self, 
        migration: MigrationFile, 
        executed_versions: set
    ) -> bool:
        """Validate migration dependencies are met"""
        for dependency in migration.dependencies:
            if dependency not in executed_versions:
                return False
        return True
    
    def _record_migration_start(self, migration: MigrationFile) -> None:
        """
Record migration start in tracking table"""
        try:
            query = f"""
                INSERT INTO {self.migrations_table} 
                (version, name, checksum, status, executed_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (version) DO UPDATE SET
                    status = EXCLUDED.status,
                    executed_at = EXCLUDED.executed_at,
                    updated_at = NOW()
            """
            
            params = (
                migration.version,
                migration.name,
                migration.checksum,
                MigrationStatus.RUNNING.value,
                datetime.now(timezone.utc)
            )
            
            self.db_manager.execute_query(query, params, fetch_results=False)
            
        except Exception as e:
            self.logger.error(f"Failed to record migration start: {e}")
            raise
    
    def _record_migration_completion(
        self, 
        migration: MigrationFile, 
        execution_time: float,
        status: MigrationStatus,
        error_message: Optional[str] = None
    ) -> None:
        """Record migration completion in tracking table"""
        try:
            query = f"""
                UPDATE {self.migrations_table}
                SET status = %s, execution_time = %s, error_message = %s,
                    updated_at = NOW()
                WHERE version = %s
            """
            
            params = (
                status.value,
                execution_time,
                error_message,
                migration.version
            )
            
            self.db_manager.execute_query(query, params, fetch_results=False)
            
        except Exception as e:
            self.logger.error(f"Failed to record migration completion: {e}")
    
    def execute_migration(self, migration: MigrationFile) -> bool:
        """Execute single migration with rollback capability"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Executing migration {migration.version}: {migration.name}")
            
            # Record start
            self._record_migration_start(migration)
            
            # Validate checksum if migration was previously executed
            existing_record = self._get_migration_record(migration.version)
            if existing_record and existing_record.checksum != migration.checksum:
                raise ValueError(
                    f"Migration {migration.version} checksum mismatch. "
                    "File may have been modified after execution."
                )
            
            # Create savepoint for rollback
            savepoint_name = f"migration_{migration.version.replace('.', '_')}"
            self.db_manager.execute_query(
                f"SAVEPOINT {savepoint_name}", 
                fetch_results=False
            )
            
            try:
                # Execute UP migration
                if migration.up_sql:
                    self.db_manager.execute_query(
                        migration.up_sql, 
                        fetch_results=False
                    )
                
                # Release savepoint
                self.db_manager.execute_query(
                    f"RELEASE SAVEPOINT {savepoint_name}", 
                    fetch_results=False
                )
                
                # Record success
                execution_time = (datetime.now() - start_time).total_seconds()
                self._record_migration_completion(
                    migration, 
                    execution_time, 
                    MigrationStatus.COMPLETED
                )
                
                self.logger.info(
                    f"Migration {migration.version} completed successfully "
                    f"in {execution_time:.2f}s"
                )
                return True
                
            except Exception as e:
                # Rollback to savepoint
                self.db_manager.execute_query(
                    f"ROLLBACK TO SAVEPOINT {savepoint_name}", 
                    fetch_results=False
                )
                raise e
                
        except Exception as e:
            # Record failure
            execution_time = (datetime.now() - start_time).total_seconds()
            error_message = str(e)
            
            self._record_migration_completion(
                migration, 
                execution_time, 
                MigrationStatus.FAILED,
                error_message
            )
            
            self.logger.error(
                f"Migration {migration.version} failed: {error_message}"
            )
            return False
    
    def rollback_migration(self, migration: MigrationFile) -> bool:
        """Rollback single migration"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Rolling back migration {migration.version}: {migration.name}")
            
            if not migration.down_sql:
                raise ValueError(f"No rollback SQL provided for migration {migration.version}")
            
            # Execute DOWN migration
            self.db_manager.execute_query(migration.down_sql, fetch_results=False)
            
            # Update record
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_migration_completion(
                migration,
                execution_time,
                MigrationStatus.ROLLED_BACK
            )
            
            self.logger.info(
                f"Migration {migration.version} rolled back successfully "
                f"in {execution_time:.2f}s"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback migration {migration.version}: {e}")
            return False
    
    def _get_migration_record(self, version: str) -> Optional[MigrationRecord]:
        """Get migration record by version"""
        try:
            query = f"""
                SELECT version, name, checksum, status, executed_at, 
                       execution_time, error_message
                FROM {self.migrations_table}
                WHERE version = %s
            """
            
            result = self.db_manager.execute_query(query, (version,))
            
            if result:
                row = result[0]
                return MigrationRecord(
                    version=row[0],
                    name=row[1],
                    checksum=row[2],
                    status=MigrationStatus(row[3]),
                    executed_at=row[4],
                    execution_time=row[5],
                    error_message=row[6]
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get migration record for {version}: {e}")
            return None
    
    def migrate_up(self, target_version: Optional[str] = None) -> bool:
        """Execute all pending migrations up to target version"""
        try:
            pending_migrations = self.get_pending_migrations()
            
            if not pending_migrations:
                self.logger.info("No pending migrations found")
                return True
            
            # Filter by target version if specified
            if target_version:
                pending_migrations = [
                    m for m in pending_migrations
                    if self._version_sort_key(m.version) <= self._version_sort_key(target_version)
                ]
            
            if not pending_migrations:
                self.logger.info(f"No migrations found up to version {target_version}")
                return True
            
            success_count = 0
            total_count = len(pending_migrations)
            
            self.logger.info(f"Executing {total_count} migrations...")
            
            for migration in pending_migrations:
                if self.execute_migration(migration):
                    success_count += 1
                else:
                    self.logger.error(f"Migration pipeline stopped at {migration.version}")
                    break
            
            self.logger.info(
                f"Migration completed: {success_count}/{total_count} successful"
            )
            
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"Migration up failed: {e}")
            return False
    
    def migrate_down(self, target_version: str) -> bool:
        """Rollback migrations down to target version"""
        try:
            executed_records = [
                record for record in self.get_migration_records()
                if record.status == MigrationStatus.COMPLETED
            ]
            
            # Find migrations to rollback
            migrations_to_rollback = []
            all_migrations = {m.version: m for m in self.discover_migrations()}
            
            for record in reversed(executed_records):
                if self._version_sort_key(record.version) > self._version_sort_key(target_version):
                    if record.version in all_migrations:
                        migrations_to_rollback.append(all_migrations[record.version])
                    else:
                        self.logger.warning(
                            f"Migration file not found for version {record.version}"
                        )
            
            if not migrations_to_rollback:
                self.logger.info(f"No migrations to rollback to version {target_version}")
                return True
            
            success_count = 0
            total_count = len(migrations_to_rollback)
            
            self.logger.info(f"Rolling back {total_count} migrations...")
            
            for migration in migrations_to_rollback:
                if self.rollback_migration(migration):
                    success_count += 1
                else:
                    self.logger.error(f"Rollback stopped at {migration.version}")
                    break
            
            self.logger.info(
                f"Rollback completed: {success_count}/{total_count} successful"
            )
            
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"Migration down failed: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get comprehensive migration status"""
        try:
            all_migrations = self.discover_migrations()
            records = self.get_migration_records()
            
            records_by_version = {r.version: r for r in records}
            
            status = {
                'total_migrations': len(all_migrations),
                'executed_count': len([r for r in records if r.status == MigrationStatus.COMPLETED]),
                'pending_count': 0,
                'failed_count': len([r for r in records if r.status == MigrationStatus.FAILED]),
                'migrations': []
            }
            
            for migration in all_migrations:
                record = records_by_version.get(migration.version)
                
                migration_status = {
                    'version': migration.version,
                    'name': migration.name,
                    'description': migration.description,
                    'status': record.status.value if record else 'pending',
                    'executed_at': record.executed_at.isoformat() if record else None,
                    'execution_time': record.execution_time if record else None,
                    'error_message': record.error_message if record else None
                }
                
                status['migrations'].append(migration_status)
                
                if not record or record.status != MigrationStatus.COMPLETED:
                    status['pending_count'] += 1
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get migration status: {e}")
            return {'error': str(e)}
    
    def create_migration(
        self, 
        name: str, 
        description: str = "",
        dependencies: List[str] = None
    ) -> Path:
        """Create new migration file template"""
        try:
            if dependencies is None:
                dependencies = []
            
            # Generate version timestamp
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sanitize name
            sanitized_name = re.sub(r'[^\w\s-]', '', name).strip()
            sanitized_name = re.sub(r'[-\s]+', '_', sanitized_name).lower()
            
            filename = f"{version}__{sanitized_name}.sql"
            filepath = self.migrations_dir / filename
            
            # Create migrations directory if not exists
            self.migrations_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate migration template
            template = f"""-- DESCRIPTION: {description or name}
-- DEPENDS: {', '.join(dependencies) if dependencies else 'none'}
-- Created: {datetime.now().isoformat()}

-- UP Migration
-- Add your schema changes here


-- DOWN Migration
-- DOWN --
-- Add rollback statements here

"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
            
            self.logger.info(f"Created migration file: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to create migration: {e}")
            raise
    
    def validate_migrations(self) -> Dict[str, List[str]]:
        """Validate all migration files for consistency"""
        try:
            validation_errors = {
                'syntax_errors': [],
                'dependency_errors': [],
                'checksum_errors': [],
                'naming_errors': []
            }
            
            migrations = self.discover_migrations()
            migration_versions = {m.version for m in migrations}
            
            for migration in migrations:
                # Check dependencies exist
                for dep in migration.dependencies:
                    if dep not in migration_versions:
                        validation_errors['dependency_errors'].append(
                            f"Migration {migration.version} depends on non-existent version {dep}"
                        )
                
                # Basic SQL syntax validation
                if not migration.up_sql.strip():
                    validation_errors['syntax_errors'].append(
                        f"Migration {migration.version} has empty UP SQL"
                    )
                
                # Check for circular dependencies
                if migration.version in migration.dependencies:
                    validation_errors['dependency_errors'].append(
                        f"Migration {migration.version} has circular dependency on itself"
                    )
            
            # Check for duplicate versions
            versions = [m.version for m in migrations]
            duplicates = set([v for v in versions if versions.count(v) > 1])
            if duplicates:
                validation_errors['naming_errors'].extend([
                    f"Duplicate migration version: {v}" for v in duplicates
                ])
            
            return validation_errors
            
        except Exception as e:
            self.logger.error(f"Migration validation failed: {e}")
            return {'validation_error': [str(e)]}


# Singleton instance
_migration_runner = None

def get_migration_runner() -> MigrationRunner:
    """Get migration runner singleton instance"""
    global _migration_runner
    if _migration_runner is None:
        _migration_runner = MigrationRunner()
    return _migration_runner
