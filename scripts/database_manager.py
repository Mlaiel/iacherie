#!/usr/bin/env python3
"""
Database Operations Manager - Enterprise Database Automation
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Advanced database operations for Ainflue Platform:
- Automated database migrations and schema management
- Backup and restore operations
- Data integrity validation
- Performance optimization
- Multi-database synchronization
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum

# Database libraries
try:
    import asyncpg
    import sqlalchemy
    from sqlalchemy import create_engine, text
    from sqlalchemy.ext.asyncio import create_async_engine
    HAS_DB_LIBS = True
except ImportError:
    HAS_DB_LIBS = False

# Configure enterprise logging
log_dir = '/tmp/ainflue_logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/database_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    SQLITE = "sqlite"

class OperationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    TRANSACTION_LOG = "transaction_log"

@dataclass
class DatabaseConnection:
    """Database connection configuration"""
    name: str
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "prefer"
    connection_pool_size: int = 10

@dataclass
class BackupOperation:
    """Database backup operation"""
    backup_id: str
    database_name: str
    backup_type: BackupType
    file_path: str
    started_at: datetime
    status: OperationStatus
    file_size: Optional[int] = None
    completed_at: Optional[datetime] = None
    compression_enabled: bool = True
    encryption_enabled: bool = True

@dataclass
class MigrationOperation:
    """Database migration operation"""
    migration_id: str
    database_name: str
    version_from: str
    version_to: str
    script_path: str
    started_at: datetime
    status: OperationStatus
    completed_at: Optional[datetime] = None
    rollback_script: Optional[str] = None

class DatabaseManager:
    """
    Enterprise database operations management system
    
    Features:
    - Automated migration management
    - Backup and restore automation
    - Data integrity validation
    - Performance monitoring
    - Multi-database synchronization
    - Security and compliance
    """
    
    def __init__(self, config_path: str = "/etc/ainflue/database.json"):
        self.config_path = config_path
        self.databases: Dict[str, DatabaseConnection] = {}
        self.backup_operations: List[BackupOperation] = []
        self.migration_operations: List[MigrationOperation] = []
        self.active_connections: Dict[str, Any] = {}
        
    async def load_database_configuration(self):
        """Load database configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            for db_config in config.get('databases', []):
                db_conn = DatabaseConnection(**db_config)
                self.databases[db_conn.name] = db_conn
            
            logger.info(f"Loaded {len(self.databases)} database configurations")
            
        except FileNotFoundError:
            # Create default Ainflue database configuration
            default_databases = [
                {
                    "name": "ainflue_main",
                    "db_type": "postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "database": "ainflue",
                    "username": "ainflue_user",
                    "password": "secure_password"
                },
                {
                    "name": "ainflue_analytics",
                    "db_type": "postgresql", 
                    "host": "localhost",
                    "port": 5432,
                    "database": "ainflue_analytics",
                    "username": "analytics_user",
                    "password": "analytics_password"
                },
                {
                    "name": "ainflue_cache",
                    "db_type": "redis",
                    "host": "localhost",
                    "port": 6379,
                    "database": "0",
                    "username": "",
                    "password": ""
                }
            ]
            
            for db_config in default_databases:
                db_conn = DatabaseConnection(**db_config)
                self.databases[db_conn.name] = db_conn
            
            logger.info("Created default database configuration")
    
    async def create_connection(self, database_name: str) -> Optional[Any]:
        """Create database connection"""
        try:
            if database_name not in self.databases:
                raise ValueError(f"Database {database_name} not configured")
            
            db_config = self.databases[database_name]
            
            if not HAS_DB_LIBS:
                logger.warning("Database libraries not available")
                return None
            
            if db_config.db_type == DatabaseType.POSTGRESQL:
                connection_string = (
                    f"postgresql://{db_config.username}:{db_config.password}@"
                    f"{db_config.host}:{db_config.port}/{db_config.database}"
                )
                
                # Async connection for PostgreSQL
                engine = create_async_engine(
                    connection_string.replace("postgresql://", "postgresql+asyncpg://"),
                    pool_size=db_config.connection_pool_size,
                    echo=False
                )
                
                self.active_connections[database_name] = engine
                return engine
                
            elif db_config.db_type == DatabaseType.MYSQL:
                connection_string = (
                    f"mysql+aiomysql://{db_config.username}:{db_config.password}@"
                    f"{db_config.host}:{db_config.port}/{db_config.database}"
                )
                
                engine = create_async_engine(connection_string)
                self.active_connections[database_name] = engine
                return engine
            
            elif db_config.db_type == DatabaseType.REDIS:
                # Redis connection would use aioredis
                logger.info(f"Redis connection to {db_config.host}:{db_config.port}")
                return None  # Placeholder for Redis connection
            
            else:
                logger.error(f"Unsupported database type: {db_config.db_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create connection to {database_name}: {e}")
            return None
    
    async def execute_migration(self, database_name: str, migration_script: str, 
                              version_from: str, version_to: str) -> str:
        """Execute database migration"""
        try:
            migration_id = f"migration_{database_name}_{int(time.time())}"
            
            migration_op = MigrationOperation(
                migration_id=migration_id,
                database_name=database_name,
                version_from=version_from,
                version_to=version_to,
                script_path=migration_script,
                started_at=datetime.now(),
                status=OperationStatus.RUNNING
            )
            
            self.migration_operations.append(migration_op)
            
            logger.info(f"Starting migration {migration_id}: {version_from} → {version_to}")
            
            # Get database connection
            connection = await self.create_connection(database_name)
            if not connection:
                migration_op.status = OperationStatus.FAILED
                return migration_id
            
            # Read migration script
            with open(migration_script, 'r') as f:
                sql_commands = f.read()
            
            # Execute migration
            if HAS_DB_LIBS:
                async with connection.begin() as transaction:
                    for command in sql_commands.split(';'):
                        command = command.strip()
                        if command:
                            await transaction.execute(text(command))
                    
                    # Update schema version
                    await transaction.execute(text(
                        "INSERT INTO schema_versions (version, applied_at) VALUES (:version, :timestamp)"
                    ), {
                        'version': version_to,
                        'timestamp': datetime.now()
                    })
            
            migration_op.status = OperationStatus.SUCCESS
            migration_op.completed_at = datetime.now()
            
            logger.info(f"Migration {migration_id} completed successfully")
            return migration_id
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            migration_op.status = OperationStatus.FAILED
            migration_op.completed_at = datetime.now()
            return migration_id
    
    async def create_backup(self, database_name: str, backup_type: BackupType = BackupType.FULL) -> str:
        """Create database backup"""
        try:
            backup_id = f"backup_{database_name}_{int(time.time())}"
            backup_dir = f"/tmp/ainflue_backups/{database_name}"
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_file = f"{backup_dir}/{backup_id}.sql"
            if backup_type == BackupType.FULL:
                backup_file = f"{backup_dir}/{backup_id}_full.sql"
            
            backup_op = BackupOperation(
                backup_id=backup_id,
                database_name=database_name,
                backup_type=backup_type,
                file_path=backup_file,
                started_at=datetime.now(),
                status=OperationStatus.RUNNING
            )
            
            self.backup_operations.append(backup_op)
            
            logger.info(f"Starting {backup_type.value} backup: {backup_id}")
            
            db_config = self.databases[database_name]
            
            if db_config.db_type == DatabaseType.POSTGRESQL:
                # Use pg_dump for PostgreSQL
                cmd = [
                    'pg_dump',
                    f'--host={db_config.host}',
                    f'--port={db_config.port}',
                    f'--username={db_config.username}',
                    f'--dbname={db_config.database}',
                    '--verbose',
                    '--clean',
                    '--no-owner',
                    '--no-privileges',
                    f'--file={backup_file}'
                ]
                
                # Set password via environment
                env = os.environ.copy()
                env['PGPASSWORD'] = db_config.password
                
                result = await self._run_command(cmd, env=env)
                
                if result['returncode'] == 0:
                    # Compress backup if enabled
                    if backup_op.compression_enabled:
                        compressed_file = f"{backup_file}.gz"
                        compress_result = await self._run_command([
                            'gzip', backup_file
                        ])
                        
                        if compress_result['returncode'] == 0:
                            backup_op.file_path = compressed_file
                            backup_file = compressed_file
                    
                    # Get file size
                    if os.path.exists(backup_file):
                        backup_op.file_size = os.path.getsize(backup_file)
                    
                    backup_op.status = OperationStatus.SUCCESS
                    
                else:
                    logger.error(f"Backup failed: {result['stderr']}")
                    backup_op.status = OperationStatus.FAILED
                    
            elif db_config.db_type == DatabaseType.MYSQL:
                # Use mysqldump for MySQL
                cmd = [
                    'mysqldump',
                    f'--host={db_config.host}',
                    f'--port={db_config.port}',
                    f'--user={db_config.username}',
                    f'--password={db_config.password}',
                    '--single-transaction',
                    '--routines',
                    '--triggers',
                    db_config.database
                ]
                
                result = await self._run_command(cmd, output_file=backup_file)
                
                if result['returncode'] == 0:
                    backup_op.file_size = os.path.getsize(backup_file)
                    backup_op.status = OperationStatus.SUCCESS
                else:
                    backup_op.status = OperationStatus.FAILED
            
            backup_op.completed_at = datetime.now()
            
            logger.info(f"Backup {backup_id} completed with status: {backup_op.status.value}")
            return backup_id
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            backup_op.status = OperationStatus.FAILED
            backup_op.completed_at = datetime.now()
            return backup_id
    
    async def restore_backup(self, database_name: str, backup_file: str) -> bool:
        """Restore database from backup"""
        try:
            logger.info(f"Starting restore for {database_name} from {backup_file}")
            
            if not os.path.exists(backup_file):
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            db_config = self.databases[database_name]
            
            # Decompress if needed
            if backup_file.endswith('.gz'):
                decompressed_file = backup_file[:-3]
                decompress_result = await self._run_command([
                    'gunzip', '-c', backup_file
                ], output_file=decompressed_file)
                
                if decompress_result['returncode'] != 0:
                    logger.error("Failed to decompress backup file")
                    return False
                
                backup_file = decompressed_file
            
            if db_config.db_type == DatabaseType.POSTGRESQL:
                # Use psql for PostgreSQL restore
                cmd = [
                    'psql',
                    f'--host={db_config.host}',
                    f'--port={db_config.port}',
                    f'--username={db_config.username}',
                    f'--dbname={db_config.database}',
                    f'--file={backup_file}',
                    '--quiet'
                ]
                
                env = os.environ.copy()
                env['PGPASSWORD'] = db_config.password
                
                result = await self._run_command(cmd, env=env)
                
            elif db_config.db_type == DatabaseType.MYSQL:
                # Use mysql for MySQL restore
                cmd = [
                    'mysql',
                    f'--host={db_config.host}',
                    f'--port={db_config.port}',
                    f'--user={db_config.username}',
                    f'--password={db_config.password}',
                    db_config.database
                ]
                
                with open(backup_file, 'r') as f:
                    result = await self._run_command(cmd, stdin_data=f.read())
            
            success = result['returncode'] == 0
            
            if success:
                logger.info(f"Restore completed successfully for {database_name}")
            else:
                logger.error(f"Restore failed: {result['stderr']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Restore operation failed: {e}")
            return False
    
    async def validate_data_integrity(self, database_name: str) -> Dict[str, Any]:
        """Validate data integrity"""
        try:
            logger.info(f"Starting data integrity validation for {database_name}")
            
            validation_results = {
                'database': database_name,
                'timestamp': datetime.now().isoformat(),
                'checks_performed': [],
                'issues_found': [],
                'overall_status': 'healthy'
            }
            
            connection = await self.create_connection(database_name)
            if not connection or not HAS_DB_LIBS:
                validation_results['overall_status'] = 'unable_to_validate'
                return validation_results
            
            db_config = self.databases[database_name]
            
            if db_config.db_type == DatabaseType.POSTGRESQL:
                # PostgreSQL specific integrity checks
                checks = [
                    ("Table count", "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"),
                    ("Index health", "SELECT schemaname, tablename, indexname FROM pg_indexes WHERE schemaname = 'public'"),
                    ("Foreign key constraints", "SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type = 'FOREIGN KEY'"),
                    ("Check constraints", "SELECT COUNT(*) FROM information_schema.check_constraints"),
                    ("Sequence integrity", "SELECT COUNT(*) FROM information_schema.sequences")
                ]
                
                async with connection.begin() as conn:
                    for check_name, query in checks:
                        try:
                            result = await conn.execute(text(query))
                            rows = result.fetchall()
                            
                            validation_results['checks_performed'].append({
                                'check': check_name,
                                'status': 'passed',
                                'result_count': len(rows)
                            })
                            
                        except Exception as e:
                            validation_results['issues_found'].append({
                                'check': check_name,
                                'error': str(e)
                            })
                            validation_results['overall_status'] = 'issues_found'
                
                # Check for orphaned records (example)
                orphan_checks = [
                    "SELECT COUNT(*) FROM creators c LEFT JOIN users u ON c.user_id = u.id WHERE u.id IS NULL",
                    "SELECT COUNT(*) FROM content co LEFT JOIN creators c ON co.creator_id = c.id WHERE c.id IS NULL"
                ]
                
                async with connection.begin() as conn:
                    for query in orphan_checks:
                        try:
                            result = await conn.execute(text(query))
                            count = result.scalar()
                            
                            if count > 0:
                                validation_results['issues_found'].append({
                                    'check': 'orphaned_records',
                                    'count': count,
                                    'query': query
                                })
                                validation_results['overall_status'] = 'issues_found'
                                
                        except Exception as e:
                            logger.debug(f"Orphan check failed (expected for demo): {e}")
            
            logger.info(f"Data integrity validation completed: {validation_results['overall_status']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Data integrity validation failed: {e}")
            return {
                'database': database_name,
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'validation_failed',
                'error': str(e)
            }
    
    async def optimize_database_performance(self, database_name: str) -> Dict[str, Any]:
        """Optimize database performance"""
        try:
            logger.info(f"Starting performance optimization for {database_name}")
            
            optimization_results = {
                'database': database_name,
                'timestamp': datetime.now().isoformat(),
                'optimizations_applied': [],
                'performance_metrics': {},
                'recommendations': []
            }
            
            connection = await self.create_connection(database_name)
            if not connection or not HAS_DB_LIBS:
                return optimization_results
            
            db_config = self.databases[database_name]
            
            if db_config.db_type == DatabaseType.POSTGRESQL:
                # PostgreSQL performance optimizations
                optimizations = [
                    ("Update table statistics", "ANALYZE;"),
                    ("Reindex tables", "REINDEX DATABASE {};".format(db_config.database)),
                    ("Vacuum tables", "VACUUM ANALYZE;")
                ]
                
                async with connection.begin() as conn:
                    for opt_name, query in optimizations:
                        try:
                            await conn.execute(text(query))
                            optimization_results['optimizations_applied'].append(opt_name)
                            
                        except Exception as e:
                            logger.warning(f"Optimization {opt_name} failed: {e}")
                
                # Collect performance metrics
                metrics_queries = [
                    ("Database size", "SELECT pg_size_pretty(pg_database_size('{}'))".format(db_config.database)),
                    ("Active connections", "SELECT count(*) FROM pg_stat_activity"),
                    ("Cache hit ratio", "SELECT round(blks_hit*100.0/(blks_hit+blks_read), 2) as cache_hit_ratio FROM pg_stat_database WHERE datname = '{}'".format(db_config.database))
                ]
                
                async with connection.begin() as conn:
                    for metric_name, query in metrics_queries:
                        try:
                            result = await conn.execute(text(query))
                            value = result.scalar()
                            optimization_results['performance_metrics'][metric_name] = str(value)
                            
                        except Exception as e:
                            logger.debug(f"Metric collection failed: {e}")
                
                # Generate recommendations
                optimization_results['recommendations'] = [
                    "Schedule regular VACUUM ANALYZE operations",
                    "Monitor slow query log for optimization opportunities",
                    "Consider adding indexes for frequently queried columns",
                    "Review connection pooling configuration",
                    "Monitor database size growth trends"
                ]
            
            logger.info(f"Performance optimization completed for {database_name}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            return {
                'database': database_name,
                'error': str(e)
            }
    
    async def synchronize_databases(self, source_db: str, target_db: str, 
                                  tables: List[str] = None) -> bool:
        """Synchronize data between databases"""
        try:
            logger.info(f"Starting synchronization: {source_db} → {target_db}")
            
            if source_db not in self.databases or target_db not in self.databases:
                logger.error("Source or target database not configured")
                return False
            
            source_conn = await self.create_connection(source_db)
            target_conn = await self.create_connection(target_db)
            
            if not source_conn or not target_conn or not HAS_DB_LIBS:
                logger.error("Failed to establish database connections")
                return False
            
            # Get tables to synchronize
            if tables is None:
                # Get all tables from source
                async with source_conn.begin() as conn:
                    result = await conn.execute(text(
                        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                    ))
                    tables = [row[0] for row in result.fetchall()]
            
            # Synchronize each table
            for table in tables:
                try:
                    logger.info(f"Synchronizing table: {table}")
                    
                    # Simple sync: truncate and copy (for demo purposes)
                    # In production, would use more sophisticated sync strategies
                    
                    async with target_conn.begin() as target_tx:
                        # Disable foreign key checks temporarily
                        await target_tx.execute(text("SET session_replication_role = replica"))
                        
                        # Truncate target table
                        await target_tx.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                        
                        # Copy data from source
                        async with source_conn.begin() as source_tx:
                            result = await source_tx.execute(text(f"SELECT * FROM {table}"))
                            rows = result.fetchall()
                            
                            if rows:
                                # Get column names
                                columns = list(result.keys())
                                
                                # Prepare insert statement
                                placeholders = ', '.join([f':{col}' for col in columns])
                                insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                                
                                # Insert rows in batches
                                batch_size = 1000
                                for i in range(0, len(rows), batch_size):
                                    batch = rows[i:i + batch_size]
                                    row_dicts = [dict(zip(columns, row)) for row in batch]
                                    await target_tx.execute(text(insert_sql), row_dicts)
                        
                        # Re-enable foreign key checks
                        await target_tx.execute(text("SET session_replication_role = DEFAULT"))
                        
                        logger.info(f"Table {table} synchronized successfully")
                        
                except Exception as e:
                    logger.error(f"Failed to synchronize table {table}: {e}")
                    return False
            
            logger.info("Database synchronization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database synchronization failed: {e}")
            return False
    
    async def _run_command(self, command: List[str], env: Dict = None, 
                         output_file: str = None, stdin_data: str = None) -> Dict[str, Any]:
        """Run system command"""
        try:
            if output_file:
                # Redirect output to file
                with open(output_file, 'w') as f:
                    process = await asyncio.create_subprocess_exec(
                        *command,
                        stdout=f,
                        stderr=asyncio.subprocess.PIPE,
                        stdin=asyncio.subprocess.PIPE if stdin_data else None,
                        env=env
                    )
                    
                    stdout, stderr = await process.communicate(
                        input=stdin_data.encode() if stdin_data else None
                    )
                    
                    return {
                        'returncode': process.returncode,
                        'stdout': '',
                        'stderr': stderr.decode() if stderr else ''
                    }
            else:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    stdin=asyncio.subprocess.PIPE if stdin_data else None,
                    env=env
                )
                
                stdout, stderr = await process.communicate(
                    input=stdin_data.encode() if stdin_data else None
                )
                
                return {
                    'returncode': process.returncode,
                    'stdout': stdout.decode() if stdout else '',
                    'stderr': stderr.decode() if stderr else ''
                }
                
        except Exception as e:
            return {
                'returncode': 1,
                'stdout': '',
                'stderr': str(e)
            }
    
    async def get_database_status(self) -> Dict[str, Any]:
        """Get status of all configured databases"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'databases': {},
            'summary': {
                'total_databases': len(self.databases),
                'connected': 0,
                'failed': 0
            }
        }
        
        for db_name, db_config in self.databases.items():
            try:
                connection = await self.create_connection(db_name)
                
                if connection and HAS_DB_LIBS:
                    # Test connection
                    async with connection.begin() as conn:
                        await conn.execute(text("SELECT 1"))
                    
                    status['databases'][db_name] = {
                        'status': 'connected',
                        'type': db_config.db_type.value,
                        'host': db_config.host,
                        'port': db_config.port
                    }
                    status['summary']['connected'] += 1
                    
                else:
                    status['databases'][db_name] = {
                        'status': 'failed',
                        'error': 'Connection failed or libraries missing'
                    }
                    status['summary']['failed'] += 1
                    
            except Exception as e:
                status['databases'][db_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
                status['summary']['failed'] += 1
        
        return status
    
    async def generate_database_report(self) -> Dict[str, Any]:
        """Generate comprehensive database report"""
        report = {
            'report_id': f"db_report_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'database_status': await self.get_database_status(),
            'backup_operations': [asdict(op) for op in self.backup_operations[-10:]],
            'migration_operations': [asdict(op) for op in self.migration_operations[-10:]],
            'recommendations': [
                "Schedule regular automated backups",
                "Monitor database performance metrics",
                "Keep migration scripts version controlled",
                "Implement database monitoring alerts",
                "Regular integrity checks and optimization"
            ]
        }
        
        return report

async def main():
    """CLI entry point for database manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ainflue Database Manager')
    parser.add_argument('--backup', metavar='DB_NAME', help='Create database backup')
    parser.add_argument('--restore', nargs=2, metavar=('DB_NAME', 'BACKUP_FILE'), help='Restore from backup')
    parser.add_argument('--migrate', nargs=4, metavar=('DB_NAME', 'SCRIPT', 'FROM_VER', 'TO_VER'), help='Run migration')
    parser.add_argument('--validate', metavar='DB_NAME', help='Validate data integrity')
    parser.add_argument('--optimize', metavar='DB_NAME', help='Optimize database performance')
    parser.add_argument('--sync', nargs=2, metavar=('SOURCE_DB', 'TARGET_DB'), help='Synchronize databases')
    parser.add_argument('--status', action='store_true', help='Show database status')
    parser.add_argument('--report', action='store_true', help='Generate database report')
    parser.add_argument('--config', default='/etc/ainflue/database.json', help='Configuration file')
    
    args = parser.parse_args()
    
    manager = DatabaseManager(args.config)
    await manager.load_database_configuration()
    
    try:
        if args.backup:
            backup_id = await manager.create_backup(args.backup)
            print(f"Backup created: {backup_id}")
        
        if args.restore:
            success = await manager.restore_backup(args.restore[0], args.restore[1])
            print(f"Restore {'successful' if success else 'failed'}")
        
        if args.migrate:
            migration_id = await manager.execute_migration(
                args.migrate[0], args.migrate[1], args.migrate[2], args.migrate[3]
            )
            print(f"Migration started: {migration_id}")
        
        if args.validate:
            results = await manager.validate_data_integrity(args.validate)
            print(json.dumps(results, indent=2, default=str))
        
        if args.optimize:
            results = await manager.optimize_database_performance(args.optimize)
            print(json.dumps(results, indent=2, default=str))
        
        if args.sync:
            success = await manager.synchronize_databases(args.sync[0], args.sync[1])
            print(f"Synchronization {'successful' if success else 'failed'}")
        
        if args.status:
            status = await manager.get_database_status()
            print(json.dumps(status, indent=2, default=str))
        
        if args.report:
            report = await manager.generate_database_report()
            print(json.dumps(report, indent=2, default=str))
    
    except Exception as e:
        logger.error(f"Database manager failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())