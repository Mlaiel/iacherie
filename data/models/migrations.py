"""
Database Migrations Management
=============================

Alembic migrations support and database schema management utilities.
Provides migration scripts and schema evolution tools.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import logging

try:
    from alembic import command
    from alembic.config import Config
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import MetaData, Table, Column, String, Text, DateTime, Boolean
    from sqlalchemy.engine import Engine
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False

# Import models for metadata
from . import (
    ContentModel, UserModel, FingerprintModel, RevenueModel,
    AnalyticsModel, ProtectionModel, LicensingModel
)
from .content_model import Base

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Manages database migrations using Alembic.
    Provides utilities for schema evolution and version control.
    """
    
    def __init__(self, engine: Engine, alembic_ini_path: str = None):
        if not ALEMBIC_AVAILABLE:
            raise ImportError("Alembic is required for migration management")
        
        self.engine = engine
        self.alembic_ini_path = alembic_ini_path or self._find_alembic_ini()
        self.config = None
        
        if self.alembic_ini_path and os.path.exists(self.alembic_ini_path):
            self.config = Config(self.alembic_ini_path)
            self.config.set_main_option("sqlalchemy.url", str(engine.url))
    
    def _find_alembic_ini(self) -> Optional[str]:
        """Find alembic.ini file in project structure"""
        possible_paths = [
            'alembic.ini',
            '../alembic.ini',
            '../../alembic.ini',
            '../../../alembic.ini',
            'config/alembic.ini',
            '../config/alembic.ini'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        return None
    
    def init_alembic(self, directory: str = "migrations") -> bool:
        """Initialize Alembic in the project"""



        try:
            if not self.config:
                # Create basic alembic.ini
                alembic_ini_content = f"""
[alembic]
script_location = {directory}
sqlalchemy.url = {self.engine.url}

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
                with open('alembic.ini', 'w') as f:
                    f.write(alembic_ini_content)
                
                self.config = Config('alembic.ini')
            
            # Initialize Alembic directory
            command.init(self.config, directory)
            
            # Update env.py to import our models
            env_py_path = os.path.join(directory, 'env.py')
            if os.path.exists(env_py_path):
                self._update_env_py(env_py_path)
            
            logger.info(f"Alembic initialized in {directory}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Alembic: {e}")
            return False
    
    def _update_env_py(self, env_py_path: str):
        """Update env.py to import our models"""
        additional_imports = """
# Import all models for autogenerate support
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data.models import (
    ContentModel, UserModel, FingerprintModel, RevenueModel,
    AnalyticsModel, ProtectionModel, LicensingModel
)
from backend.data.models.content_model import Base

# Set target metadata
target_metadata = Base.metadata
"""



        
        try:
            with open(env_py_path, 'r') as f:
                content = f.read()
            
            # Add imports after existing imports
            if 'from backend.data.models' not in content:
                import_section = content.find('target_metadata = None')
                if import_section != -1:
                    new_content = (
                        content[:import_section] + 
                        additional_imports + 
                        content[import_section:].replace('target_metadata = None', '')
                    )
                    
                    with open(env_py_path, 'w') as f:
                        f.write(new_content)
                    
                    logger.info("Updated env.py with model imports")
        
        except Exception as e:
            logger.warning(f"Could not update env.py: {e}")
    
    def create_migration(self, message: str, autogenerate: bool = True) -> bool:
        """Create a new migration"""



        try:
            if not self.config:
                logger.error("Alembic not configured")
                return False
            
            if autogenerate:
                command.revision(
                    self.config, 
                    message=message, 
                    autogenerate=True
                )
            else:
                command.revision(self.config, message=message)
            
            logger.info(f"Created migration: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            return False
    
    def upgrade(self, revision: str = "head") -> bool:
        """Upgrade database to specified revision"""



        try:
            if not self.config:
                logger.error("Alembic not configured")
                return False
            
            command.upgrade(self.config, revision)
            logger.info(f"Upgraded database to {revision}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upgrade database: {e}")
            return False
    
    def downgrade(self, revision: str) -> bool:
        """Downgrade database to specified revision"""



        try:
            if not self.config:
                logger.error("Alembic not configured")
                return False
            
            command.downgrade(self.config, revision)
            logger.info(f"Downgraded database to {revision}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to downgrade database: {e}")
            return False
    
    def get_current_revision(self) -> Optional[str]:
        """Get current database revision"""



        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get migration history"""



        try:
            if not self.config:
                return []
            
            from alembic.script import ScriptDirectory
            script = ScriptDirectory.from_config(self.config)
            
            history = []
            for revision in script.walk_revisions():
                history.append({
                    'revision': revision.revision,
                    'down_revision': revision.down_revision,
                    'branch_labels': revision.branch_labels,
                    'depends_on': revision.depends_on,
                    'doc': revision.doc,
                    'is_head': revision.is_head,
                    'is_merge_point': revision.is_merge_point
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []
    
    def check_for_updates(self) -> Dict[str, Any]:
        """Check if database needs updates"""
        result = {
            'needs_update': False,
            'current_revision': None,
            'head_revision': None,
            'pending_migrations': []
        }
        
        try:
            current = self.get_current_revision()
            result['current_revision'] = current
            
            if self.config:
                from alembic.script import ScriptDirectory
                script = ScriptDirectory.from_config(self.config)
                head = script.get_current_head()
                result['head_revision'] = head
                
                if current != head:
                    result['needs_update'] = True
                    # Get pending migrations
                    if current:
                        revisions = list(script.iterate_revisions(head, current))
                        result['pending_migrations'] = [
                            {'revision': rev.revision, 'doc': rev.doc}
                            for rev in revisions
                        ]
        
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
        
        return result


class SchemaValidator:
    """
    Validates database schema against model definitions.
    Detects inconsistencies and suggests fixes.
    """
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.metadata = Base.metadata
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate current schema against models"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_tables': [],
            'extra_tables': [],
            'column_mismatches': {}
        }
        
        try:
            # Reflect current database schema
            current_metadata = MetaData()
            current_metadata.reflect(bind=self.engine)
            
            # Get expected tables from models
            expected_tables = set(self.metadata.tables.keys())
            current_tables = set(current_metadata.tables.keys())
            
            # Find missing and extra tables
            validation_result['missing_tables'] = list(expected_tables - current_tables)
            validation_result['extra_tables'] = list(current_tables - expected_tables)
            
            # Check columns for existing tables
            for table_name in expected_tables.intersection(current_tables):
                expected_table = self.metadata.tables[table_name]
                current_table = current_metadata.tables[table_name]
                
                column_issues = self._compare_table_columns(expected_table, current_table)
                if column_issues:
                    validation_result['column_mismatches'][table_name] = column_issues
            
            # Determine if schema is valid
            if (validation_result['missing_tables'] or 
                validation_result['extra_tables'] or 
                validation_result['column_mismatches']):
                validation_result['valid'] = False
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Schema validation failed: {e}")
        
        return validation_result
    
    def _compare_table_columns(self, expected_table: Table, current_table: Table) -> Dict[str, Any]:
        """Compare columns between expected and current table"""
        issues = {
            'missing_columns': [],
            'extra_columns': [],
            'type_mismatches': [],
            'nullable_mismatches': []
        }
        
        expected_columns = {col.name: col for col in expected_table.columns}
        current_columns = {col.name: col for col in current_table.columns}
        
        # Find missing and extra columns
        issues['missing_columns'] = list(
            set(expected_columns.keys()) - set(current_columns.keys())
        )
        issues['extra_columns'] = list(
            set(current_columns.keys()) - set(expected_columns.keys())
        )
        
        # Compare existing columns
        common_columns = set(expected_columns.keys()).intersection(set(current_columns.keys()))
        
        for col_name in common_columns:
            expected_col = expected_columns[col_name]
            current_col = current_columns[col_name]
            
            # Compare types (simplified)
            if str(expected_col.type) != str(current_col.type):
                issues['type_mismatches'].append({
                    'column': col_name,
                    'expected': str(expected_col.type),
                    'current': str(current_col.type)
                })
            
            # Compare nullable
            if expected_col.nullable != current_col.nullable:
                issues['nullable_mismatches'].append({
                    'column': col_name,
                    'expected_nullable': expected_col.nullable,
                    'current_nullable': current_col.nullable
                })
        
        # Remove empty lists
        return {k: v for k, v in issues.items() if v}


def create_initial_migration_script() -> str:
    """Generate initial migration script content"""



    return '''"""Initial migration: Create all tables

Revision ID: 001_initial
Revises: 
Create Date: {create_date}

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create all tables"""
    # This will be auto-generated by Alembic
    # when running: alembic revision --autogenerate -m "Initial migration"
    pass


def downgrade():
    """Drop all tables"""
    # This will be auto-generated by Alembic
    pass
'''.format(create_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))


def get_migration_commands() -> Dict[str, str]:
    """Get common migration commands for reference"""



    return {
        'init': 'alembic init migrations',
        'create_migration': 'alembic revision --autogenerate -m "Migration message"',
        'upgrade': 'alembic upgrade head',
        'downgrade': 'alembic downgrade -1',
        'current': 'alembic current',
        'history': 'alembic history',
        'show': 'alembic show <revision>',
        'stamp': 'alembic stamp head'
    }


# Quick setup function
def quick_setup_migrations(engine: Engine, directory: str = "migrations") -> MigrationManager:
    """Quick setup for migrations"""
    manager = MigrationManager(engine)
    
    if not manager.config:
        logger.info("Initializing Alembic...")
        if manager.init_alembic(directory):
            logger.info("Creating initial migration...")
            manager.create_migration("Initial migration with all models")
    
    return manager


# Export utilities
__all__ = [
    'MigrationManager',
    'SchemaValidator',
    'create_initial_migration_script',
    'get_migration_commands',
    'quick_setup_migrations'
]
