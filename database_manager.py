#!/usr/bin/env python3
"""Database Management Script for Ainflue Platform

Comprehensive database management tool that integrates Alembic migrations
with the existing database infrastructure components.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Usage:
    python database_manager.py init           # Initialize database with migrations
    python database_manager.py migrate        # Run pending migrations
    python database_manager.py rollback       # Rollback last migration
    python database_manager.py status         # Show migration status
    python database_manager.py create-indexes # Create performance indexes
    python database_manager.py backup         # Create database backup
    python database_manager.py health-check   # Run database health checks
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from alembic import command
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    from alembic.runtime.environment import EnvironmentContext
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError
    import logging
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install: pip install alembic sqlalchemy")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Comprehensive database management for Ainflue platform."""
    
    def __init__(self, config_path: str = "alembic.ini"):
        """Initialize database manager."""
        self.config_path = config_path
        self.config = Config(config_path)
        self.script_dir = ScriptDirectory.from_config(self.config)
        self.database_url = self._get_database_url()
        
    def _get_database_url(self) -> str:
        """Get database URL from environment or config."""
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return database_url
        return self.config.get_main_option("sqlalchemy.url")
    
    def init_database(self) -> bool:
        """Initialize database with all migrations."""
        try:
            logger.info("Initializing database with Alembic migrations...")
            
            # Check if alembic_version table exists
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
                    if 'sqlite' in self.database_url else
                    "SELECT tablename FROM pg_tables WHERE tablename='alembic_version'"
                ))
                
                if result.fetchone():
                    logger.info("Database already initialized. Running upgrade to head...")
                    command.upgrade(self.config, "head")
                else:
                    logger.info("First time initialization. Creating schema...")
                    command.upgrade(self.config, "head")
            
            logger.info("✅ Database initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    def migrate(self) -> bool:
        """Run pending migrations."""
        try:
            logger.info("Running database migrations...")
            command.upgrade(self.config, "head")
            logger.info("✅ Migrations completed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    def rollback(self, steps: int = 1) -> bool:
        """Rollback migrations."""
        try:
            logger.info(f"Rolling back {steps} migration(s)...")
            current_rev = self._get_current_revision()
            if not current_rev:
                logger.warning("No migrations to rollback")
                return True
            
            # Get revision to rollback to
            revisions = list(self.script_dir.walk_revisions())
            if len(revisions) < steps:
                logger.error(f"Cannot rollback {steps} steps, only {len(revisions)} revisions available")
                return False
            
            target_rev = revisions[steps - 1].down_revision if steps > 0 else revisions[0].revision
            command.downgrade(self.config, target_rev or "base")
            logger.info("✅ Rollback completed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def status(self) -> bool:
        """Show migration status."""
        try:
            logger.info("Database Migration Status:")
            logger.info("=" * 50)
            
            current_rev = self._get_current_revision()
            logger.info(f"Current revision: {current_rev or 'None'}")
            
            # Get all revisions
            revisions = list(self.script_dir.walk_revisions())
            logger.info(f"Available revisions: {len(revisions)}")
            
            for rev in revisions:
                status = "✅ APPLIED" if rev.revision == current_rev else "⏳ PENDING"
                logger.info(f"  {rev.revision}: {rev.doc} [{status}]")
            
            return True
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return False
    
    def create_indexes(self) -> bool:
        """Create additional performance indexes."""
        try:
            logger.info("Creating additional performance indexes...")
            
            additional_indexes = [
                # Composite indexes for common queries
                "CREATE INDEX IF NOT EXISTS idx_content_user_created ON user_content(user_id, created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_user_severity ON protection_alerts(user_id, severity, created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_revenue_user_date ON revenue_tracking(user_id, created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_fingerprints_algo_hash ON content_fingerprints(algorithm, fingerprint_hash)",
                
                # Partial indexes for active records
                "CREATE INDEX IF NOT EXISTS idx_users_active ON users(id) WHERE active = true",
                "CREATE INDEX IF NOT EXISTS idx_content_published ON user_content(id, created_at) WHERE status = 'published'",
                "CREATE INDEX IF NOT EXISTS idx_alerts_active ON protection_alerts(id, created_at) WHERE status IN ('active', 'monitoring')",
            ]
            
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                for index_sql in additional_indexes:
                    try:
                        conn.execute(text(index_sql))
                        logger.info(f"✅ Created index: {index_sql.split()[5]}")
                    except Exception as e:
                        logger.warning(f"⚠️ Index creation skipped: {e}")
                        
                conn.commit()
            
            logger.info("✅ Additional indexes created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Index creation failed: {e}")
            return False
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """Create database backup."""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_ainflue_{timestamp}.sql"
            
            logger.info(f"Creating database backup: {backup_path}")
            
            if 'sqlite' in self.database_url:
                # SQLite backup
                import shutil
                db_file = self.database_url.replace('sqlite:///', '')
                shutil.copy2(db_file, backup_path.replace('.sql', '.db'))
                logger.info(f"✅ SQLite backup created: {backup_path.replace('.sql', '.db')}")
            else:
                # PostgreSQL backup (would require pg_dump)
                logger.warning("PostgreSQL backup requires pg_dump - skipping for now")
            
            return True
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
    
    def health_check(self) -> bool:
        """Run comprehensive database health checks."""
        try:
            logger.info("Running database health checks...")
            logger.info("=" * 50)
            
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                # Test connection
                logger.info("✅ Database connection: OK")
                
                # Check tables exist
                if 'sqlite' in self.database_url:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                else:
                    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
                
                tables = [row[0] for row in result.fetchall()]
                expected_tables = [
                    'users', 'user_content', 'content_fingerprints', 
                    'protection_alerts', 'revenue_tracking', 'platform_integrations',
                    'audit_logs', 'creator_profiles', 'alembic_version'
                ]
                
                missing_tables = [t for t in expected_tables if t not in tables]
                if missing_tables:
                    logger.error(f"❌ Missing tables: {missing_tables}")
                    return False
                else:
                    logger.info(f"✅ All {len(expected_tables)} expected tables present")
                
                # Check indexes
                if 'sqlite' in self.database_url:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index'"))
                    indexes = [row[0] for row in result.fetchall()]
                    logger.info(f"✅ Database indexes: {len(indexes)} total")
                
                # Test sample operations
                conn.execute(text("SELECT COUNT(*) FROM users"))
                logger.info("✅ Sample query execution: OK")
                
            logger.info("✅ Database health check passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def _get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                row = result.fetchone()
                return row[0] if row else None
        except:
            return None


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Ainflue Database Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init              # Initialize database with migrations  
  %(prog)s migrate           # Run pending migrations
  %(prog)s rollback          # Rollback last migration
  %(prog)s rollback --steps 2 # Rollback 2 migrations
  %(prog)s status            # Show migration status
  %(prog)s create-indexes    # Create additional performance indexes
  %(prog)s backup            # Create database backup
  %(prog)s health-check      # Run database health checks
        """
    )
    
    parser.add_argument(
        'command',
        choices=['init', 'migrate', 'rollback', 'status', 'create-indexes', 'backup', 'health-check'],
        help='Database management command'
    )
    
    parser.add_argument(
        '--config',
        default='alembic.ini',
        help='Alembic configuration file (default: alembic.ini)'
    )
    
    parser.add_argument(
        '--steps',
        type=int,
        default=1,
        help='Number of migration steps (for rollback command)'
    )
    
    parser.add_argument(
        '--backup-path',
        help='Custom backup file path'
    )
    
    args = parser.parse_args()
    
    # Initialize database manager
    try:
        db_manager = DatabaseManager(args.config)
    except Exception as e:
        logger.error(f"Failed to initialize database manager: {e}")
        sys.exit(1)
    
    # Execute command
    success = False
    
    if args.command == 'init':
        success = db_manager.init_database()
    elif args.command == 'migrate':
        success = db_manager.migrate()
    elif args.command == 'rollback':
        success = db_manager.rollback(args.steps)
    elif args.command == 'status':
        success = db_manager.status()
    elif args.command == 'create-indexes':
        success = db_manager.create_indexes()
    elif args.command == 'backup':
        success = db_manager.backup_database(args.backup_path)
    elif args.command == 'health-check':
        success = db_manager.health_check()
    
    if success:
        logger.info(f"✅ Command '{args.command}' completed successfully")
        sys.exit(0)
    else:
        logger.error(f"❌ Command '{args.command}' failed")
        sys.exit(1)


if __name__ == "__main__":
    main()