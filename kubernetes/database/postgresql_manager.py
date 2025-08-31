"""
Enterprise PostgreSQL Database Manager
Advanced database management, optimization and monitoring for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.pool import ThreadedConnectionPool
import asyncpg
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from backend.core.config import get_database_settings
from backend.core.logging import get_logger
from backend.core.monitoring import MetricsCollector
from backend.security.encryption import DatabaseEncryption


class PostgreSQLManager:
    """
    Enterprise PostgreSQL database manager with advanced features:
    - Connection pooling and load balancing
    - Automated backup and recovery
    - Performance monitoring and optimization
    - Multi-tenant database management
    - SSL/TLS encryption support
    - Query analytics and profiling
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_database_settings()
        self.metrics = MetricsCollector()
        self.encryption = DatabaseEncryption()
        self.connection_pool = None
        self.async_pool = None
        self.engine = None
        self.session_factory = None
        self._initialize_connections()
    
    def _initialize_connections(self) -> None:
        """Initialize database connections and pools"""



        try:
            # Synchronous connection pool
            self.connection_pool = ThreadedConnectionPool(
                minconn=self.config.MIN_CONNECTIONS,
                maxconn=self.config.MAX_CONNECTIONS,
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                sslmode=self.config.SSL_MODE,
                application_name="IA_Influencer_Agent"
            )
            
            # SQLAlchemy engine
            database_url = (
                f"postgresql://{self.config.DB_USER}:{self.config.DB_PASSWORD}"
                f"@{self.config.DB_HOST}:{self.config.DB_PORT}/{self.config.DB_NAME}"
            )
            
            self.engine = create_engine(
                database_url,
                pool_size=self.config.POOL_SIZE,
                max_overflow=self.config.MAX_OVERFLOW,
                pool_timeout=self.config.POOL_TIMEOUT,
                pool_recycle=self.config.POOL_RECYCLE,
                echo=self.config.DEBUG_SQL
            )
            
            self.session_factory = sessionmaker(bind=self.engine)
            
            self.logger.info("PostgreSQL connection pools initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database connections: {e}")
            raise
    
    async def initialize_async_pool(self) -> None:
        """Initialize asynchronous connection pool"""



        try:
            self.async_pool = await asyncpg.create_pool(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                ssl=self.config.SSL_MODE,
                min_size=self.config.MIN_CONNECTIONS,
                max_size=self.config.MAX_CONNECTIONS,
                command_timeout=60,
                server_settings={
                    'application_name': 'IA_Influencer_Agent_Async',
                    'jit': 'off'
                }
            )
            
            self.logger.info("Async PostgreSQL pool initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize async pool: {e}")
            raise
    
    def get_connection(self):
        """Get connection from pool"""



        try:
            return self.connection_pool.getconn()
        except Exception as e:
            self.logger.error(f"Failed to get connection: {e}")
            raise
    
    def return_connection(self, connection) -> None:
        """Return connection to pool"""



        try:
            self.connection_pool.putconn(connection)
        except Exception as e:
            self.logger.error(f"Failed to return connection: {e}")
    
    async def execute_async_query(
        self, 
        query: str, 
        params: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Execute asynchronous query"""
        if not self.async_pool:
            await self.initialize_async_pool()
        
        start_time = datetime.now()
        
        try:
            async with self.async_pool.acquire() as connection:
                if params:
                    result = await connection.fetch(query, *params.values())
                else:
                    result = await connection.fetch(query)
                
                # Convert to list of dictionaries
                return [dict(row) for row in result]
                
        except Exception as e:
            self.logger.error(f"Async query failed: {e}")
            raise
        finally:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_query_time(execution_time)
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None,
        fetch_results: bool = True
    ) -> Optional[List[tuple]]:
        """Execute synchronous query"""
        connection = None
        cursor = None
        start_time = datetime.now()
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_results:
                results = cursor.fetchall()
                connection.commit()
                return results
            else:
                connection.commit()
                return None
                
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_query_time(execution_time)
    
    def create_database(self, database_name: str, encoding: str = 'UTF8') -> bool:
        """Create new database"""



        try:
            # Connect to postgres database to create new database
            connection = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database='postgres',
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = connection.cursor()
            cursor.execute(
                f"CREATE DATABASE {database_name} ENCODING '{encoding}'"
            )
            
            cursor.close()
            connection.close()
            
            self.logger.info(f"Database '{database_name}' created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create database '{database_name}': {e}")
            return False
    
    def drop_database(self, database_name: str) -> bool:
        """Drop database"""



        try:
            connection = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database='postgres',
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = connection.cursor()
            
            # Terminate existing connections
            cursor.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{database_name}' AND pid <> pg_backend_pid()
            """)
            
            cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
            
            cursor.close()
            connection.close()
            
            self.logger.info(f"Database '{database_name}' dropped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to drop database '{database_name}': {e}")
            return False
    
    def create_schema(self, schema_name: str) -> bool:
        """Create database schema"""



        try:
            query = f"CREATE SCHEMA IF NOT EXISTS {schema_name}"
            self.execute_query(query, fetch_results=False)
            
            self.logger.info(f"Schema '{schema_name}' created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create schema '{schema_name}': {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information"""



        try:
            info = {}
            
            # Database version
            version_query = "SELECT version()"
            result = self.execute_query(version_query)
            info['version'] = result[0][0] if result else None
            
            # Database size
            size_query = f"""
                SELECT pg_size_pretty(pg_database_size('{self.config.DB_NAME}'))
            """
            result = self.execute_query(size_query)
            info['size'] = result[0][0] if result else None
            
            # Active connections
            connections_query = """
                SELECT count(*) FROM pg_stat_activity 
                WHERE state = 'active'
            """
            result = self.execute_query(connections_query)
            info['active_connections'] = result[0][0] if result else 0
            
            # Table count
            tables_query = """
                SELECT count(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            result = self.execute_query(tables_query)
            info['table_count'] = result[0][0] if result else 0
            
            # Index count
            indexes_query = """
                SELECT count(*) FROM pg_indexes 
                WHERE schemaname = 'public'
            """
            result = self.execute_query(indexes_query)
            info['index_count'] = result[0][0] if result else 0
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {}
    
    def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """Get detailed table statistics"""



        try:
            stats = {}
            
            # Row count
            count_query = f"SELECT count(*) FROM {table_name}"
            result = self.execute_query(count_query)
            stats['row_count'] = result[0][0] if result else 0
            
            # Table size
            size_query = f"""
                SELECT pg_size_pretty(pg_total_relation_size('{table_name}'))
            """
            result = self.execute_query(size_query)
            stats['size'] = result[0][0] if result else None
            
            # Column information
            columns_query = f"""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """
            result = self.execute_query(columns_query)
            stats['columns'] = [
                {
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES'
                }
                for row in result
            ] if result else []
            
            # Index information
            indexes_query = f"""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = '{table_name}'
            """
            result = self.execute_query(indexes_query)
            stats['indexes'] = [
                {'name': row[0], 'definition': row[1]}
                for row in result
            ] if result else []
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get table statistics for '{table_name}': {e}")
            return {}
    
    def optimize_table(self, table_name: str) -> bool:
        """Optimize table performance"""



        try:
            # Analyze table statistics
            analyze_query = f"ANALYZE {table_name}"
            self.execute_query(analyze_query, fetch_results=False)
            
            # Vacuum table
            vacuum_query = f"VACUUM {table_name}"
            self.execute_query(vacuum_query, fetch_results=False)
            
            self.logger.info(f"Table '{table_name}' optimized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to optimize table '{table_name}': {e}")
            return False
    
    def create_index(
        self, 
        table_name: str, 
        column_names: List[str], 
        index_name: Optional[str] = None,
        unique: bool = False,
        partial_condition: Optional[str] = None
    ) -> bool:
        """Create database index"""



        try:
            if not index_name:
                index_name = f"idx_{table_name}_{'_'.join(column_names)}"
            
            unique_clause = "UNIQUE " if unique else ""
            columns_clause = ", ".join(column_names)
            partial_clause = f" WHERE {partial_condition}" if partial_condition else ""
            
            query = f"""
                CREATE {unique_clause}INDEX IF NOT EXISTS {index_name} 
                ON {table_name} ({columns_clause}){partial_clause}
            """
            
            self.execute_query(query, fetch_results=False)
            
            self.logger.info(f"Index '{index_name}' created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create index '{index_name}': {e}")
            return False
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slow running queries"""



        try:
            query = f"""
                SELECT 
                    query,
                    mean_exec_time,
                    calls,
                    total_exec_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements 
                ORDER BY mean_exec_time DESC 
                LIMIT {limit}
            """
            
            result = self.execute_query(query)
            
            return [
                {
                    'query': row[0],
                    'mean_time': row[1],
                    'calls': row[2],
                    'total_time': row[3],
                    'rows': row[4],
                    'hit_percent': row[5]
                }
                for row in result
            ] if result else []
            
        except Exception as e:
            self.logger.error(f"Failed to get slow queries: {e}")
            return []
    
    def monitor_connections(self) -> Dict[str, Any]:
        """Monitor database connections"""



        try:
            query = """
                SELECT 
                    state,
                    count(*) as connection_count,
                    max(now() - state_change) as max_duration
                FROM pg_stat_activity 
                WHERE pid <> pg_backend_pid()
                GROUP BY state
            """
            
            result = self.execute_query(query)
            
            monitoring_data = {
                'states': {},
                'total_connections': 0
            }
            
            for row in result:
                state, count, duration = row
                monitoring_data['states'][state] = {
                    'count': count,
                    'max_duration': str(duration) if duration else None
                }
                monitoring_data['total_connections'] += count
            
            # Get max connections setting
            max_conn_query = "SHOW max_connections"
            result = self.execute_query(max_conn_query)
            monitoring_data['max_connections'] = int(result[0][0]) if result else None
            
            return monitoring_data
            
        except Exception as e:
            self.logger.error(f"Failed to monitor connections: {e}")
            return {}
    
    def backup_table(self, table_name: str, backup_path: str) -> bool:
        """Backup single table to file"""



        try:
            import subprocess
            
            command = [
                'pg_dump',
                '-h', self.config.DB_HOST,
                '-p', str(self.config.DB_PORT),
                '-U', self.config.DB_USER,
                '-d', self.config.DB_NAME,
                '-t', table_name,
                '-f', backup_path,
                '--no-password'
            ]
            
            # Set password environment variable
            env = {'PGPASSWORD': self.config.DB_PASSWORD}
            
            result = subprocess.run(
                command, 
                env=env, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"Table '{table_name}' backed up to '{backup_path}'")
                return True
            else:
                self.logger.error(f"Backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to backup table '{table_name}': {e}")
            return False
    
    def restore_table(self, backup_path: str) -> bool:
        """Restore table from backup file"""



        try:
            import subprocess
            
            command = [
                'psql',
                '-h', self.config.DB_HOST,
                '-p', str(self.config.DB_PORT),
                '-U', self.config.DB_USER,
                '-d', self.config.DB_NAME,
                '-f', backup_path,
                '--no-password'
            ]
            
            env = {'PGPASSWORD': self.config.DB_PASSWORD}
            
            result = subprocess.run(
                command, 
                env=env, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"Table restored from '{backup_path}'")
                return True
            else:
                self.logger.error(f"Restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to restore from '{backup_path}': {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check"""



        try:
            health_status = {
                'status': 'healthy',
                'checks': {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Connection test
            try:
                self.execute_query("SELECT 1")
                health_status['checks']['connection'] = 'ok'
            except Exception as e:
                health_status['checks']['connection'] = f'failed: {e}'
                health_status['status'] = 'unhealthy'
            
            # Disk space check
            try:
                query = """
                    SELECT 
                        pg_size_pretty(sum(pg_database_size(datname))) as total_size
                    FROM pg_database
                """
                result = self.execute_query(query)
                health_status['checks']['disk_usage'] = result[0][0] if result else 'unknown'
            except Exception as e:
                health_status['checks']['disk_usage'] = f'failed: {e}'
            
            # Connection count check
            try:
                monitoring_data = self.monitor_connections()
                total_conn = monitoring_data.get('total_connections', 0)
                max_conn = monitoring_data.get('max_connections', 100)
                
                if total_conn / max_conn > 0.8:
                    health_status['checks']['connections'] = 'warning: high usage'
                    health_status['status'] = 'warning'
                else:
                    health_status['checks']['connections'] = 'ok'
            except Exception as e:
                health_status['checks']['connections'] = f'failed: {e}'
            
            # Replication lag (if applicable)
            try:
                replication_query = """
                    SELECT 
                        client_addr,
                        state,
                        pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) as lag_bytes
                    FROM pg_stat_replication
                """
                result = self.execute_query(replication_query)
                
                if result:
                    health_status['checks']['replication'] = {
                        'replicas': len(result),
                        'max_lag_bytes': max(row[2] for row in result) if result else 0
                    }
                else:
                    health_status['checks']['replication'] = 'no replicas'
            except Exception:
                health_status['checks']['replication'] = 'not_configured'
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def close_connections(self) -> None:
        """Close all database connections"""



        try:
            if self.connection_pool:
                self.connection_pool.closeall()
            
            if self.async_pool:
                asyncio.create_task(self.async_pool.close())
            
            if self.engine:
                self.engine.dispose()
            
            self.logger.info("All database connections closed")
            
        except Exception as e:
            self.logger.error(f"Failed to close connections: {e}")
    
    def __enter__(self):
        """Context manager entry"""



        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_connections()


# Singleton instance
_postgresql_manager = None

def get_postgresql_manager() -> PostgreSQLManager:
    """Get PostgreSQL manager singleton instance"""
    global _postgresql_manager
    if _postgresql_manager is None:
        _postgresql_manager = PostgreSQLManager()
    return _postgresql_manager
