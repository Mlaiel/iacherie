#!/usr/bin/env python3
"""Production Database Migration Management Script

This script provides production-ready database migration management with
comprehensive safety checks, monitoring, and rollback capabilities.

Usage:
    python scripts/production_migrations.py init
    python scripts/production_migrations.py migrate
    python scripts/production_migrations.py rollback
    python scripts/production_migrations.py status

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import subprocess
import psutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/migrations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionMigrationManager:
    """Production-grade database migration manager."""
    
    def __init__(self):
        self.config = Config('alembic.ini')
        self.script_dir = ScriptDirectory.from_config(self.config)
        self.engine: Optional[Engine] = None
        
    def _get_database_url(self) -> str:
        """Get production database URL with SSL."""
        return "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}?sslmode=require".format(
            user=os.getenv('POSTGRES_USER_PRODUCTION', 'ainflue_user'),
            password=os.getenv('POSTGRES_PASSWORD_PRODUCTION', ''),
            host=os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
            port=os.getenv('POSTGRES_PORT_PRODUCTION', '5432'),
            database=os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
        )
    
    def _create_engine(self) -> Engine:
        """Create database engine with production settings."""
        if self.engine is None:
            self.engine = create_engine(
                self._get_database_url(),
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "sslmode": "require",
                    "connect_timeout": 10,
                    "application_name": "ainflue_migrations"
                }
            )
        return self.engine
    
    def check_prerequisites(self) -> bool:
        """Check if system is ready for migrations."""
        logger.info("Checking migration prerequisites...")
        
        # Check if we're in production environment
        if os.getenv('ENVIRONMENT') != 'production':
            logger.warning("Not in production environment. Continue? (y/N)")
            if input().lower() != 'y':
                return False
        
        # Check database connectivity
        try:
            engine = self._create_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"Connected to PostgreSQL: {version}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
        
        # Check disk space (at least 10GB free)
        disk_usage = psutil.disk_usage('/')
        free_gb = disk_usage.free / (1024**3)
        if free_gb < 10:
            logger.error(f"Insufficient disk space: {free_gb:.1f}GB free (minimum 10GB required)")
            return False
        
        # Check if pg_stat_statements extension is available
        try:
            engine = self._create_engine()
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT EXISTS(SELECT 1 FROM pg_available_extensions WHERE name = 'pg_stat_statements')"
                ))
                if not result.scalar():
                    logger.warning("pg_stat_statements extension not available")
        except Exception as e:
            logger.warning(f"Could not check pg_stat_statements: {e}")
        
        logger.info("Prerequisites check passed")
        return True
    
    def create_backup(self) -> str:
        """Create database backup before migration."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"/backup/ainflue_pre_migration_{timestamp}.sql"
        
        logger.info(f"Creating backup: {backup_path}")
        
        # Create backup directory
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Run pg_dump
        cmd = [
            'pg_dump',
            '--host', os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
            '--port', os.getenv('POSTGRES_PORT_PRODUCTION', '5432'),
            '--username', os.getenv('POSTGRES_USER_PRODUCTION', 'ainflue_user'),
            '--dbname', os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
            '--format', 'custom',
            '--compress', '9',
            '--file', backup_path,
            '--verbose'
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Backup created successfully: {backup_path}")
            return backup_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e.stderr}")
            raise
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        engine = self._create_engine()
        
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()
            
        # Get all available revisions
        revisions = list(self.script_dir.walk_revisions())
        
        return {
            'current_revision': current_rev,
            'latest_revision': revisions[0].revision if revisions else None,
            'total_revisions': len(revisions),
            'pending_migrations': [r.revision for r in revisions if r.revision != current_rev]
        }
    
    def init_database(self):
        """Initialize Alembic for the database."""
        logger.info("Initializing database with Alembic...")
        
        if not self.check_prerequisites():
            logger.error("Prerequisites check failed")
            return False
        
        try:
            # Stamp the database with the current head
            command.stamp(self.config, "head")
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def run_migrations(self, dry_run: bool = False):
        """Run pending migrations."""
        logger.info("Starting migration process...")
        
        if not self.check_prerequisites():
            logger.error("Prerequisites check failed")
            return False
        
        # Get current status
        status = self.get_migration_status()
        logger.info(f"Current revision: {status['current_revision']}")
        logger.info(f"Latest revision: {status['latest_revision']}")
        
        if not status['pending_migrations']:
            logger.info("No pending migrations")
            return True
        
        logger.info(f"Pending migrations: {len(status['pending_migrations'])}")
        
        if dry_run:
            logger.info("DRY RUN - Would execute the following migrations:")
            for rev in status['pending_migrations']:
                logger.info(f"  - {rev}")
            return True
        
        # Create backup
        backup_path = self.create_backup()
        
        try:
            # Run migrations
            logger.info("Executing migrations...")
            command.upgrade(self.config, "head")
            logger.info("Migrations completed successfully")
            
            # Verify migration
            new_status = self.get_migration_status()
            logger.info(f"New revision: {new_status['current_revision']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            logger.info(f"Backup available at: {backup_path}")
            raise
    
    def rollback_migration(self, target_revision: Optional[str] = None):
        """Rollback to a specific revision."""
        logger.info("Starting rollback process...")
        
        if not self.check_prerequisites():
            logger.error("Prerequisites check failed")
            return False
        
        # Create backup before rollback
        backup_path = self.create_backup()
        
        try:
            if target_revision:
                logger.info(f"Rolling back to revision: {target_revision}")
                command.downgrade(self.config, target_revision)
            else:
                logger.info("Rolling back one revision")
                command.downgrade(self.config, "-1")
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            logger.info(f"Backup available at: {backup_path}")
            raise

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Production Database Migration Manager')
    parser.add_argument('action', choices=['init', 'migrate', 'rollback', 'status', 'dry-run'],
                       help='Action to perform')
    parser.add_argument('--revision', help='Target revision for rollback')
    
    args = parser.parse_args()
    
    manager = ProductionMigrationManager()
    
    try:
        if args.action == 'init':
            success = manager.init_database()
        elif args.action == 'migrate':
            success = manager.run_migrations()
        elif args.action == 'dry-run':
            success = manager.run_migrations(dry_run=True)
        elif args.action == 'rollback':
            success = manager.rollback_migration(args.revision)
        elif args.action == 'status':
            status = manager.get_migration_status()
            print(json.dumps(status, indent=2))
            success = True
        else:
            logger.error(f"Unknown action: {args.action}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Migration management failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()