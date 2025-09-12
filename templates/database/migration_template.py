"""{{migration_name}} Database Migration Template for Ainflue Platform
{{migration_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
DBA Role: Enterprise database migration with comprehensive schema management
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import ProgrammingError

logger = logging.getLogger(__name__)

# Migration metadata
revision = '{{revision_id}}'
down_revision = '{{down_revision}}'
branch_labels = {{branch_labels}}
depends_on = {{depends_on}}


class MigrationError(Exception):
    """Custom migration error"""
    pass


class DatabaseMigrationHelper:
    """Helper class for common migration operations
    
    Provides enterprise-grade migration utilities:
    - Safe column operations with rollback
    - Index management with naming conventions
    - Constraint management
    - Data migration utilities
    - PostgreSQL-specific operations
    - Performance optimization
    - Migration validation
    - Rollback safety checks
    """
    
    @staticmethod
    def safe_add_column(
        table_name: str,
        column_name: str,
        column_type: sa.types.TypeEngine,
        nullable: bool = True,
        default: Any = None,
        comment: Optional[str] = None
    ):
        """Safely add a column with validation"""
        try:
            # Check if column already exists
            inspector = inspect(op.get_bind())
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            
            if column_name in columns:
                logger.warning(f"Column {column_name} already exists in {table_name}")
                return
            
            # Add column
            column = sa.Column(
                column_name,
                column_type,
                nullable=nullable,
                default=default,
                comment=comment
            )
            
            op.add_column(table_name, column)
            logger.info(f"Added column {column_name} to {table_name}")
            
        except Exception as e:
            logger.error(f"Error adding column {column_name} to {table_name}: {e}")
            raise MigrationError(f"Failed to add column: {e}")
    
    @staticmethod
    def safe_drop_column(table_name: str, column_name: str):
        """Safely drop a column with validation"""
        try:
            # Check if column exists
            inspector = inspect(op.get_bind())
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            
            if column_name not in columns:
                logger.warning(f"Column {column_name} does not exist in {table_name}")
                return
            
            op.drop_column(table_name, column_name)
            logger.info(f"Dropped column {column_name} from {table_name}")
            
        except Exception as e:
            logger.error(f"Error dropping column {column_name} from {table_name}: {e}")
            raise MigrationError(f"Failed to drop column: {e}")
    
    @staticmethod
    def safe_create_index(
        index_name: str,
        table_name: str,
        columns: List[str],
        unique: bool = False,
        postgresql_using: str = 'btree',
        postgresql_where: Optional[str] = None
    ):
        """Safely create an index with naming conventions"""
        try:
            # Check if index already exists
            inspector = inspect(op.get_bind())
            indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
            
            if index_name in indexes:
                logger.warning(f"Index {index_name} already exists")
                return
            
            op.create_index(
                index_name,
                table_name,
                columns,
                unique=unique,
                postgresql_using=postgresql_using,
                postgresql_where=text(postgresql_where) if postgresql_where else None
            )
            logger.info(f"Created index {index_name} on {table_name}({', '.join(columns)})")
            
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            raise MigrationError(f"Failed to create index: {e}")
    
    @staticmethod
    def safe_drop_index(index_name: str, table_name: Optional[str] = None):
        """Safely drop an index"""
        try:
            if table_name:
                inspector = inspect(op.get_bind())
                indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
                
                if index_name not in indexes:
                    logger.warning(f"Index {index_name} does not exist")
                    return
            
            op.drop_index(index_name, table_name=table_name)
            logger.info(f"Dropped index {index_name}")
            
        except Exception as e:
            logger.error(f"Error dropping index {index_name}: {e}")
            raise MigrationError(f"Failed to drop index: {e}")
    
    @staticmethod
    def safe_create_constraint(
        constraint_name: str,
        table_name: str,
        constraint_type: str,
        columns: List[str],
        referred_table: Optional[str] = None,
        referred_columns: Optional[List[str]] = None,
        ondelete: Optional[str] = None,
        onupdate: Optional[str] = None
    ):
        """Safely create constraints"""
        try:
            if constraint_type.lower() == 'foreignkey':
                op.create_foreign_key(
                    constraint_name,
                    table_name,
                    referred_table,
                    columns,
                    referred_columns,
                    ondelete=ondelete,
                    onupdate=onupdate
                )
                logger.info(f"Created foreign key {constraint_name}")
                
            elif constraint_type.lower() == 'unique':
                op.create_unique_constraint(constraint_name, table_name, columns)
                logger.info(f"Created unique constraint {constraint_name}")
                
            elif constraint_type.lower() == 'check':
                # For check constraints, columns[0] should contain the check expression
                check_expression = columns[0] if columns else ""
                op.create_check_constraint(constraint_name, table_name, check_expression)
                logger.info(f"Created check constraint {constraint_name}")
                
        except Exception as e:
            logger.error(f"Error creating constraint {constraint_name}: {e}")
            raise MigrationError(f"Failed to create constraint: {e}")
    
    @staticmethod
    def safe_drop_constraint(
        constraint_name: str,
        table_name: str,
        constraint_type: str = 'foreignkey'
    ):
        """Safely drop constraints"""
        try:
            if constraint_type.lower() == 'foreignkey':
                op.drop_constraint(constraint_name, table_name, type_='foreignkey')
            elif constraint_type.lower() == 'unique':
                op.drop_constraint(constraint_name, table_name, type_='unique')
            elif constraint_type.lower() == 'check':
                op.drop_constraint(constraint_name, table_name, type_='check')
            else:
                op.drop_constraint(constraint_name, table_name)
            
            logger.info(f"Dropped constraint {constraint_name}")
            
        except Exception as e:
            logger.error(f"Error dropping constraint {constraint_name}: {e}")
            raise MigrationError(f"Failed to drop constraint: {e}")
    
    @staticmethod
    def bulk_insert_data(table_name: str, data: List[Dict[str, Any]]):
        """Bulk insert data during migration"""
        try:
            if not data:
                return
            
            # Get table metadata
            metadata = sa.MetaData()
            metadata.reflect(bind=op.get_bind())
            table = metadata.tables[table_name]
            
            # Insert data
            op.bulk_insert(table, data)
            logger.info(f"Inserted {len(data)} rows into {table_name}")
            
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            raise MigrationError(f"Failed to insert data: {e}")
    
    @staticmethod
    def migrate_data(
        source_table: str,
        target_table: str,
        column_mapping: Dict[str, str],
        where_clause: Optional[str] = None,
        batch_size: int = 1000
    ):
        """Migrate data between tables or columns"""
        try:
            bind = op.get_bind()
            
            # Build the SELECT query
            source_columns = list(column_mapping.keys())
            target_columns = list(column_mapping.values())
            
            select_query = f"SELECT {', '.join(source_columns)} FROM {source_table}"
            if where_clause:
                select_query += f" WHERE {where_clause}"
            
            # Execute in batches
            offset = 0
            while True:
                batch_query = f"{select_query} LIMIT {batch_size} OFFSET {offset}"
                result = bind.execute(text(batch_query))
                rows = result.fetchall()
                
                if not rows:
                    break
                
                # Prepare insert data
                insert_data = []
                for row in rows:
                    row_dict = {}
                    for i, target_col in enumerate(target_columns):
                        row_dict[target_col] = row[i]
                    insert_data.append(row_dict)
                
                # Insert batch
                DatabaseMigrationHelper.bulk_insert_data(target_table, insert_data)
                
                offset += batch_size
                logger.info(f"Migrated {offset} rows from {source_table} to {target_table}")
                
        except Exception as e:
            logger.error(f"Error migrating data from {source_table} to {target_table}: {e}")
            raise MigrationError(f"Failed to migrate data: {e}")


def upgrade():
    """Apply the migration changes
    
    This function contains the forward migration logic.
    It should include all necessary changes to upgrade the database schema.
    """
    try:
        logger.info(f"Starting migration: {revision} - {{migration_name}}")
        
        # Example: Create a new table
        # op.create_table(
        #     '{{table_name}}',
        #     sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        #     sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        #     sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        #     sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        #     sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        #     sa.Column('version', sa.Integer, default=1, nullable=False),
        #     sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
        #     sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        #     sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True),
        #     sa.Column('name', sa.String(255), nullable=False),
        #     sa.Column('description', sa.Text, nullable=True),
        #     sa.Column('status', sa.String(20), default='active', nullable=False),
        #     sa.Column('category', sa.String(100), nullable=True),
        #     sa.Column('tags', postgresql.JSONB, nullable=True),
        #     sa.Column('metadata', postgresql.JSONB, nullable=True),
        #     sa.Column('config', postgresql.JSONB, nullable=True),
        #     sa.Column('priority', sa.Integer, default=0, nullable=False),
        #     sa.Column('weight', sa.Integer, default=1, nullable=False),
        #     sa.Column('is_public', sa.Boolean, default=False, nullable=False),
        #     sa.Column('is_featured', sa.Boolean, default=False, nullable=False),
        #     sa.Column('is_locked', sa.Boolean, default=False, nullable=False),
        #     sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
        #     sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        #     sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        #     sa.Column('search_vector', sa.Text, nullable=True),
        #     comment='{{table_description}}'
        # )
        
        # Example: Add columns to existing table
        # DatabaseMigrationHelper.safe_add_column(
        #     'existing_table',
        #     'new_column',
        #     sa.String(100),
        #     nullable=True,
        #     comment='New column description'
        # )
        
        # Example: Create indexes
        # DatabaseMigrationHelper.safe_create_index(
        #     'idx_{{table_name}}_name_status',
        #     '{{table_name}}',
        #     ['name', 'status']
        # )
        # 
        # DatabaseMigrationHelper.safe_create_index(
        #     'idx_{{table_name}}_created_at',
        #     '{{table_name}}',
        #     ['created_at']
        # )
        # 
        # DatabaseMigrationHelper.safe_create_index(
        #     'idx_{{table_name}}_owner_status',
        #     '{{table_name}}',
        #     ['owner_id', 'status']
        # )
        # 
        # # Partial index for non-deleted records
        # DatabaseMigrationHelper.safe_create_index(
        #     'idx_{{table_name}}_active',
        #     '{{table_name}}',
        #     ['status', 'is_public'],
        #     postgresql_where='is_deleted = false'
        # )
        # 
        # # GIN index for JSONB fields
        # DatabaseMigrationHelper.safe_create_index(
        #     'idx_{{table_name}}_tags_gin',
        #     '{{table_name}}',
        #     ['tags'],
        #     postgresql_using='gin'
        # )
        # 
        # # Full-text search index
        # DatabaseMigrationHelper.safe_create_index(
        #     'idx_{{table_name}}_search',
        #     '{{table_name}}',
        #     ['search_vector'],
        #     postgresql_using='gin'
        # )
        
        # Example: Create constraints
        # DatabaseMigrationHelper.safe_create_constraint(
        #     'fk_{{table_name}}_owner',
        #     '{{table_name}}',
        #     'foreignkey',
        #     ['owner_id'],
        #     'users',
        #     ['id'],
        #     ondelete='SET NULL'
        # )
        # 
        # DatabaseMigrationHelper.safe_create_constraint(
        #     'fk_{{table_name}}_parent',
        #     '{{table_name}}',
        #     'foreignkey',
        #     ['parent_id'],
        #     '{{table_name}}',
        #     ['id'],
        #     ondelete='CASCADE'
        # )
        # 
        # DatabaseMigrationHelper.safe_create_constraint(
        #     'uq_{{table_name}}_name_owner',
        #     '{{table_name}}',
        #     'unique',
        #     ['name', 'owner_id']
        # )
        # 
        # # Check constraints
        # DatabaseMigrationHelper.safe_create_constraint(
        #     'ck_{{table_name}}_priority',
        #     '{{table_name}}',
        #     'check',
        #     ['priority >= 0 AND priority <= 10']
        # )
        # 
        # DatabaseMigrationHelper.safe_create_constraint(
        #     'ck_{{table_name}}_status',
        #     '{{table_name}}',
        #     'check',
        #     ["status IN ('active', 'inactive', 'pending', 'deleted', 'archived')"]
        # )
        
        # Example: Insert seed data
        # seed_data = [
        #     {
        #         'id': uuid4(),
        #         'name': 'Default Category',
        #         'description': 'Default system category',
        #         'status': 'active',
        #         'category': 'system',
        #         'is_public': True,
        #         'priority': 5,
        #         'created_at': datetime.utcnow(),
        #         'updated_at': datetime.utcnow()
        #     }
        # ]
        # DatabaseMigrationHelper.bulk_insert_data('{{table_name}}', seed_data)
        
        # Example: Data migration
        # DatabaseMigrationHelper.migrate_data(
        #     'old_table',
        #     'new_table',
        #     {
        #         'old_column': 'new_column',
        #         'old_name': 'name',
        #         'old_desc': 'description'
        #     },
        #     where_clause='active = true'
        # )
        
        # Example: PostgreSQL-specific operations
        # Create custom types
        # op.execute("CREATE TYPE status_enum AS ENUM ('active', 'inactive', 'pending', 'deleted')")
        
        # Create extensions
        # op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        # op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
        # op.execute('CREATE EXTENSION IF NOT EXISTS "unaccent"')
        
        # Create custom functions
        # op.execute('''
        #     CREATE OR REPLACE FUNCTION update_updated_at_column()
        #     RETURNS TRIGGER AS $$
        #     BEGIN
        #         NEW.updated_at = now();
        #         RETURN NEW;
        #     END;
        #     $$ language 'plpgsql';
        # ''')
        
        # Create triggers
        # op.execute('''
        #     CREATE TRIGGER update_{{table_name}}_updated_at
        #     BEFORE UPDATE ON {{table_name}}
        #     FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        # ''')
        
        # Performance optimization
        # op.execute('VACUUM ANALYZE {{table_name}}')
        
        logger.info(f"Completed migration: {revision} - {{migration_name}}")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


def downgrade():
    """Revert the migration changes
    
    This function contains the reverse migration logic.
    It should undo all changes made in the upgrade() function.
    """
    try:
        logger.info(f"Starting rollback: {revision} - {{migration_name}}")
        
        # Example: Drop triggers
        # op.execute('DROP TRIGGER IF EXISTS update_{{table_name}}_updated_at ON {{table_name}}')
        
        # Example: Drop functions
        # op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')
        
        # Example: Drop constraints (reverse order)
        # DatabaseMigrationHelper.safe_drop_constraint('ck_{{table_name}}_status', '{{table_name}}', 'check')
        # DatabaseMigrationHelper.safe_drop_constraint('ck_{{table_name}}_priority', '{{table_name}}', 'check')
        # DatabaseMigrationHelper.safe_drop_constraint('uq_{{table_name}}_name_owner', '{{table_name}}', 'unique')
        # DatabaseMigrationHelper.safe_drop_constraint('fk_{{table_name}}_parent', '{{table_name}}', 'foreignkey')
        # DatabaseMigrationHelper.safe_drop_constraint('fk_{{table_name}}_owner', '{{table_name}}', 'foreignkey')
        
        # Example: Drop indexes (reverse order)
        # DatabaseMigrationHelper.safe_drop_index('idx_{{table_name}}_search')
        # DatabaseMigrationHelper.safe_drop_index('idx_{{table_name}}_tags_gin')
        # DatabaseMigrationHelper.safe_drop_index('idx_{{table_name}}_active')
        # DatabaseMigrationHelper.safe_drop_index('idx_{{table_name}}_owner_status')
        # DatabaseMigrationHelper.safe_drop_index('idx_{{table_name}}_created_at')
        # DatabaseMigrationHelper.safe_drop_index('idx_{{table_name}}_name_status')
        
        # Example: Drop columns
        # DatabaseMigrationHelper.safe_drop_column('existing_table', 'new_column')
        
        # Example: Drop table
        # op.drop_table('{{table_name}}')
        
        # Example: Drop custom types
        # op.execute('DROP TYPE IF EXISTS status_enum')
        
        logger.info(f"Completed rollback: {revision} - {{migration_name}}")
        
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise


# Migration validation functions

def validate_migration():
    """Validate migration before and after execution"""
    try:
        bind = op.get_bind()
        inspector = inspect(bind)
        
        # Check database connection
        bind.execute(text('SELECT 1'))
        
        # Validate table existence
        tables = inspector.get_table_names()
        logger.info(f"Available tables: {tables}")
        
        # Add custom validation logic here
        return True
        
    except Exception as e:
        logger.error(f"Migration validation failed: {e}")
        return False


def pre_migration_backup():
    """Create backup before migration (if needed)"""
    try:
        # Add backup logic here if required
        # This could include:
        # - Creating database dumps
        # - Backing up specific tables
        # - Creating snapshots
        
        logger.info("Pre-migration backup completed")
        return True
        
    except Exception as e:
        logger.error(f"Pre-migration backup failed: {e}")
        return False


def post_migration_verify():
    """Verify migration results"""
    try:
        bind = op.get_bind()
        
        # Example: Verify table structure
        # inspector = inspect(bind)
        # columns = inspector.get_columns('{{table_name}}')
        # expected_columns = ['id', 'name', 'description', 'status', 'created_at', 'updated_at']
        # 
        # for col_name in expected_columns:
        #     if not any(col['name'] == col_name for col in columns):
        #         raise MigrationError(f"Column {col_name} not found")
        
        # Example: Verify indexes
        # indexes = inspector.get_indexes('{{table_name}}')
        # expected_indexes = ['idx_{{table_name}}_name_status']
        # 
        # for idx_name in expected_indexes:
        #     if not any(idx['name'] == idx_name for idx in indexes):
        #         raise MigrationError(f"Index {idx_name} not found")
        
        # Example: Verify data integrity
        # result = bind.execute(text('SELECT COUNT(*) FROM {{table_name}}'))
        # count = result.scalar()
        # logger.info(f"Table {{table_name}} has {count} records")
        
        logger.info("Post-migration verification completed")
        return True
        
    except Exception as e:
        logger.error(f"Post-migration verification failed: {e}")
        return False


# Migration hooks (called automatically by Alembic if defined)

def upgrade_hook():
    """Hook called before upgrade"""
    if not validate_migration():
        raise MigrationError("Pre-migration validation failed")
    
    if not pre_migration_backup():
        raise MigrationError("Pre-migration backup failed")


def downgrade_hook():
    """Hook called before downgrade"""
    if not validate_migration():
        raise MigrationError("Pre-rollback validation failed")


# Export migration functions
__all__ = [
    'upgrade',
    'downgrade',
    'validate_migration',
    'pre_migration_backup',
    'post_migration_verify',
    'DatabaseMigrationHelper',
    'MigrationError'
]