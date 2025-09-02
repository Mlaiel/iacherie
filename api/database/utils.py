"""Database Utils - IA Influencer Agent Platform
Enterprise-grade database utilities and performance optimization tools

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

import asyncio
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import re
from pathlib import Path

from sqlalchemy import (
    text, inspect, MetaData, Table, Column, Index, ForeignKey,
    func, select, update, delete, and_, or_
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from sqlalchemy.engine import Engine
from sqlalchemy.dialects import postgresql
import logging

from ..core.logging import get_logger
from ..core.config import get_settings
from .connection import DatabaseConnection, SessionManager

logger = get_logger(__name__)
settings = get_settings()


class IndexType(Enum):
    """
Database index types"""

    BTREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"
    SPGIST = "spgist"
    BRIN = "brin"


class TableAnalysisType(Enum):
    """Table analysis types"""

    SIZE_ANALYSIS = "size"
    PERFORMANCE_ANALYSIS = "performance"
    CONSTRAINT_ANALYSIS = "constraints"
    INDEX_ANALYSIS = "indexes"
    RELATIONSHIP_ANALYSIS = "relationships"


@dataclass
class TableInfo:
    """Table information structure"""
    name: str
    schema: str
    row_count: int
    size_bytes: int
    size_pretty: str
    last_vacuum: Optional[datetime]
    last_analyze: Optional[datetime]
    columns: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]


@dataclass
class IndexInfo:
    """
Index information structure"""
    name: str
    table_name: str
    columns: List[str]
    index_type: str
    is_unique: bool
    size_bytes: int
    size_pretty: str
    usage_stats: Optional[Dict[str, Any]]


@dataclass
class PerformanceMetrics:
    """
Database performance metrics"""
    slow_queries: List[Dict[str, Any]]
    table_stats: List[Dict[str, Any]]
    index_usage: List[Dict[str, Any]]
    lock_stats: Dict[str, Any]
    connection_stats: Dict[str, Any]
    cache_hit_ratio: float
    transaction_stats: Dict[str, Any]


class DatabaseUtils:
    """
    Core database utilities for:
    - Table information and statistics
    - Database introspection
    - General utility functions
    """
    
    def __init__(self):
        self.db_connection: Optional[DatabaseConnection] = None
        self.session_manager: Optional[SessionManager] = None
        self.metadata = MetaData()
        
    async def initialize(self):
        """
Initialize database utilities"""
        self.db_connection = await DatabaseConnection.get_instance()
        self.session_manager = SessionManager()
        await self.session_manager.initialize()
    
    async def get_database_version(self) -> Dict[str, Any]:
        """
Get database version information"""
        try:
            async with self.session_manager.get_async_session() as session:
                version_query = text("SELECT version()")
                result = await session.execute(version_query)
                version_string = result.scalar()
                
                # Parse PostgreSQL version
                version_match = re.match(r'PostgreSQL (\d+\.\d+(?:\.\d+)?)', version_string)
                version_number = version_match.group(1) if version_match else "unknown"
                
                return {
                    'database_type': 'PostgreSQL',
                    'version_string': version_string,
                    'version_number': version_number,
                    'retrieved_at': datetime.utcnow()
                }
        except Exception as e:
            logger.error(f"Error getting database version: {e}")
            return {'error': str(e)}
    
    async def get_database_size(self) -> Dict[str, Any]:
        """Get total database size"""
        try:
            async with self.session_manager.get_async_session() as session:
                size_query = text("""
                    SELECT 
                        pg_database_size(current_database()) as size_bytes,
                        pg_size_pretty(pg_database_size(current_database())) as size_pretty
                """)
                result = await session.execute(size_query)
                row = result.fetchone()
                
                return {
                    'database_name': settings.DATABASE_NAME,
                    'size_bytes': row.size_bytes,
                    'size_pretty': row.size_pretty,
                    'measured_at': datetime.utcnow()
                }
        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            return {'error': str(e)}
    
    async def list_all_tables(self, include_system: bool = False) -> List[str]:
        """List all tables in the database"""
        try:
            async with self.session_manager.get_async_session() as session:
                if include_system:
                    query = text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema IN ('public', 'information_schema', 'pg_catalog')
                        ORDER BY table_name
                    """)
                else:
                    query = text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """)
                
                result = await session.execute(query)
                return [row.table_name for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return []
    
    async def get_table_info(self, table_name: str) -> Optional[TableInfo]:
        """Get comprehensive table information"""
        try:
            async with self.session_manager.get_async_session() as session:
                # Get basic table stats
                stats_query = text("""
                    SELECT 
                        schemaname,
                        relname,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_tuples,
                        n_dead_tup as dead_tuples,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables 
                    WHERE relname = :table_name
                """)
                
                stats_result = await session.execute(stats_query, {'table_name': table_name})
                stats_row = stats_result.fetchone()
                
                if not stats_row:
                    return None
                
                # Get table size
                size_query = text("""
                    SELECT 
                        pg_total_relation_size(:table_name) as size_bytes,
                        pg_size_pretty(pg_total_relation_size(:table_name)) as size_pretty
                """)
                size_result = await session.execute(size_query, {'table_name': table_name})
                size_row = size_result.fetchone()
                
                # Get column information
                columns_query = text("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale
                    FROM information_schema.columns 
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """)
                columns_result = await session.execute(columns_query, {'table_name': table_name})
                columns = [
                    {
                        'name': row.column_name,
                        'type': row.data_type,
                        'nullable': row.is_nullable == 'YES',
                        'default': row.column_default,
                        'max_length': row.character_maximum_length,
                        'precision': row.numeric_precision,
                        'scale': row.numeric_scale
                    }
                    for row in columns_result.fetchall()
                ]
                
                # Get index information
                indexes = await self._get_table_indexes(session, table_name)
                
                # Get constraint information
                constraints = await self._get_table_constraints(session, table_name)
                
                return TableInfo(
                    name=table_name,
                    schema=stats_row.schemaname,
                    row_count=stats_row.live_tuples,
                    size_bytes=size_row.size_bytes,
                    size_pretty=size_row.size_pretty,
                    last_vacuum=stats_row.last_vacuum or stats_row.last_autovacuum,
                    last_analyze=stats_row.last_analyze or stats_row.last_autoanalyze,
                    columns=columns,
                    indexes=indexes,
                    constraints=constraints
                )
                
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return None
    
    async def _get_table_indexes(self, session: AsyncSession, table_name: str) -> List[Dict[str, Any]]:
        """Get index information for a table"""
        try:
            indexes_query = text("""
                SELECT 
                    i.relname as index_name,
                    am.amname as index_type,
                    ix.indisunique as is_unique,
                    ix.indisprimary as is_primary,
                    array_agg(a.attname ORDER BY a.attnum) as columns,
                    pg_relation_size(i.oid) as size_bytes,
                    pg_size_pretty(pg_relation_size(i.oid)) as size_pretty
                FROM pg_class i
                JOIN pg_index ix ON i.oid = ix.indexrelid
                JOIN pg_class t ON ix.indrelid = t.oid
                JOIN pg_am am ON i.relam = am.oid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                WHERE t.relname = :table_name
                GROUP BY i.relname, am.amname, ix.indisunique, ix.indisprimary, i.oid
                ORDER BY i.relname
            """)
            
            result = await session.execute(indexes_query, {'table_name': table_name})
            return [
                {
                    'name': row.index_name,
                    'type': row.index_type,
                    'is_unique': row.is_unique,
                    'is_primary': row.is_primary,
                    'columns': row.columns,
                    'size_bytes': row.size_bytes,
                    'size_pretty': row.size_pretty
                }
                for row in result.fetchall()
            ]
        except Exception as e:
            logger.error(f"Error getting indexes for {table_name}: {e}")
            return []
    
    async def _get_table_constraints(self, session: AsyncSession, table_name: str) -> List[Dict[str, Any]]:
        """Get constraint information for a table"""
        try:
            constraints_query = text("""
                SELECT 
                    tc.constraint_name,
                    tc.constraint_type,
                    kcu.column_name,
                    ccu.table_name AS references_table,
                    ccu.column_name AS references_column
                FROM information_schema.table_constraints tc
                LEFT JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                LEFT JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.table_name = :table_name
                ORDER BY tc.constraint_name
            """)
            
            result = await session.execute(constraints_query, {'table_name': table_name})
            return [
                {
                    'name': row.constraint_name,
                    'type': row.constraint_type,
                    'column': row.column_name,
                    'references_table': row.references_table,
                    'references_column': row.references_column
                }
                for row in result.fetchall()
            ]
        except Exception as e:
            logger.error(f"Error getting constraints for {table_name}: {e}")
            return []
    
    async def check_table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        try:
            async with self.session_manager.get_async_session() as session:
                query = text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = :table_name AND table_schema = 'public'
                """)
                result = await session.execute(query, {'table_name': table_name})
                return result.scalar() > 0
        except Exception as e:
            logger.error(f"Error checking table existence {table_name}: {e}")
            return False
    
    async def vacuum_table(self, table_name: str, full: bool = False, analyze: bool = True) -> Dict[str, Any]:
        """Run VACUUM on a specific table"""
        try:
            # VACUUM cannot be run in a transaction, so use autocommit
            engine = self.db_connection.get_postgresql_engine(async_mode=False)
            
            with engine.connect() as conn:
                conn = conn.execution_options(autocommit=True)
                
                vacuum_cmd = "VACUUM"
                if full:
                    vacuum_cmd += " FULL"
                if analyze:
                    vacuum_cmd += " ANALYZE"
                vacuum_cmd += f" {table_name}"
                
                start_time = time.time()
                conn.execute(text(vacuum_cmd))
                execution_time = time.time() - start_time
                
                return {
                    'success': True,
                    'table_name': table_name,
                    'vacuum_type': 'FULL' if full else 'STANDARD',
                    'analyze': analyze,
                    'execution_time': execution_time
                }
        except Exception as e:
            logger.error(f"Error vacuuming table {table_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_table(self, table_name: str) -> Dict[str, Any]:
        """Run ANALYZE on a specific table"""
        try:
            engine = self.db_connection.get_postgresql_engine(async_mode=False)
            
            with engine.connect() as conn:
                conn = conn.execution_options(autocommit=True)
                
                start_time = time.time()
                conn.execute(text(f"ANALYZE {table_name}"))
                execution_time = time.time() - start_time
                
                return {
                    'success': True,
                    'table_name': table_name,
                    'execution_time': execution_time
                }
        except Exception as e:
            logger.error(f"Error analyzing table {table_name}: {e}")
            return {'success': False, 'error': str(e)}


class TableUtils:
    """
    Table-specific utilities for:
    - Table maintenance operations
    - Data consistency checks
    - Table optimization
    """
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def initialize(self):
        """
Initialize table utilities"""
        await self.db_utils.initialize()
    
    async def find_duplicate_rows(self, table_name: str, 
                                columns: Optional[List[str]] = None,
                                limit: int = 100) -> Dict[str, Any]:
        """
Find duplicate rows in a table"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                if columns:
                    # Check for duplicates based on specific columns
                    column_list = ', '.join(columns)
                    query = text(f"""
                        SELECT {column_list}, COUNT(*) as duplicate_count
                        FROM {table_name}
                        GROUP BY {column_list}
                        HAVING COUNT(*) > 1
                        ORDER BY duplicate_count DESC
                        LIMIT :limit
                    """)
                else:
                    # Check for completely identical rows
                    # Get all columns first
                    columns_query = text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    """)
                    columns_result = await session.execute(columns_query, {'table_name': table_name})
                    all_columns = [row.column_name for row in columns_result.fetchall()]
                    
                    if not all_columns:
                        return {'success': False, 'error': f'Table {table_name} not found or has no columns'}
                    
                    column_list = ', '.join(all_columns)
                    query = text(f"""
                        SELECT {column_list}, COUNT(*) as duplicate_count
                        FROM {table_name}
                        GROUP BY {column_list}
                        HAVING COUNT(*) > 1
                        ORDER BY duplicate_count DESC
                        LIMIT :limit
                    """)
                
                result = await session.execute(query, {'limit': limit})
                duplicates = result.fetchall()
                
                return {
                    'success': True,
                    'table_name': table_name,
                    'duplicate_count': len(duplicates),
                    'duplicates': [dict(row._mapping) for row in duplicates],
                    'checked_columns': columns or 'all'
                }
                
        except Exception as e:
            logger.error(f"Error finding duplicates in {table_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def check_referential_integrity(self, table_name: str) -> Dict[str, Any]:
        """Check referential integrity for foreign keys"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                # Get foreign key constraints
                fk_query = text("""
                    SELECT 
                        tc.constraint_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = :table_name
                """)
                
                fk_result = await session.execute(fk_query, {'table_name': table_name})
                foreign_keys = fk_result.fetchall()
                
                integrity_issues = []
                
                for fk in foreign_keys:
                    # Check for orphaned records
                    orphans_query = text(f"""
                        SELECT COUNT(*) as orphan_count
                        FROM {table_name} t
                        WHERE t.{fk.column_name} IS NOT NULL
                        AND NOT EXISTS (
                            SELECT 1 FROM {fk.foreign_table_name} f
                            WHERE f.{fk.foreign_column_name} = t.{fk.column_name}
                        )
                    """)
                    
                    orphans_result = await session.execute(orphans_query)
                    orphan_count = orphans_result.scalar()
                    
                    if orphan_count > 0:
                        integrity_issues.append({
                            'constraint_name': fk.constraint_name,
                            'column': fk.column_name,
                            'references_table': fk.foreign_table_name,
                            'references_column': fk.foreign_column_name,
                            'orphaned_records': orphan_count
                        })
                
                return {
                    'success': True,
                    'table_name': table_name,
                    'foreign_key_count': len(foreign_keys),
                    'integrity_issues': integrity_issues,
                    'has_issues': len(integrity_issues) > 0
                }
                
        except Exception as e:
            logger.error(f"Error checking referential integrity for {table_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """Get comprehensive table statistics"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                # Basic statistics
                stats_query = text(f"""
                    SELECT 
                        COUNT(*) as total_rows,
                        COUNT(DISTINCT *) as unique_rows,
                        pg_total_relation_size('{table_name}') as total_size,
                        pg_relation_size('{table_name}') as table_size,
                        (pg_total_relation_size('{table_name}') - pg_relation_size('{table_name}')) as index_size
                """)
                
                stats_result = await session.execute(stats_query)
                stats = stats_result.fetchone()
                
                # Column statistics
                column_stats = []
                columns_query = text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns 
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """)
                columns_result = await session.execute(columns_query, {'table_name': table_name})
                
                for col in columns_result.fetchall():
                    # Get column-specific stats
                    col_stats_query = text(f"""
                        SELECT 
                            COUNT(*) as total_count,
                            COUNT({col.column_name}) as non_null_count,
                            COUNT(DISTINCT {col.column_name}) as distinct_count
                        FROM {table_name}
                    """)
                    
                    col_stats_result = await session.execute(col_stats_query)
                    col_stats = col_stats_result.fetchone()
                    
                    null_percentage = ((col_stats.total_count - col_stats.non_null_count) / 
                                     col_stats.total_count * 100) if col_stats.total_count > 0 else 0
                    
                    uniqueness_ratio = (col_stats.distinct_count / col_stats.non_null_count 
                                      if col_stats.non_null_count > 0 else 0)
                    
                    column_stats.append({
                        'column_name': col.column_name,
                        'data_type': col.data_type,
                        'total_count': col_stats.total_count,
                        'non_null_count': col_stats.non_null_count,
                        'distinct_count': col_stats.distinct_count,
                        'null_percentage': round(null_percentage, 2),
                        'uniqueness_ratio': round(uniqueness_ratio, 4)
                    })
                
                return {
                    'success': True,
                    'table_name': table_name,
                    'total_rows': stats.total_rows,
                    'unique_rows': stats.unique_rows,
                    'duplicate_rows': stats.total_rows - stats.unique_rows,
                    'total_size_bytes': stats.total_size,
                    'table_size_bytes': stats.table_size,
                    'index_size_bytes': stats.index_size,
                    'total_size_pretty': self._bytes_to_human(stats.total_size),
                    'table_size_pretty': self._bytes_to_human(stats.table_size),
                    'index_size_pretty': self._bytes_to_human(stats.index_size),
                    'column_statistics': column_stats
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics for {table_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _bytes_to_human(self, bytes_size: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
    
    async def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """Optimize table performance"""
        try:
            results = []
            
            # Run VACUUM ANALYZE
            vacuum_result = await self.db_utils.vacuum_table(table_name, analyze=True)
            results.append(vacuum_result)
            
            # Update table statistics
            analyze_result = await self.db_utils.analyze_table(table_name)
            results.append(analyze_result)
            
            return {
                'success': True,
                'table_name': table_name,
                'optimization_results': results
            }
            
        except Exception as e:
            logger.error(f"Error optimizing table {table_name}: {e}")
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
class IndexUtils:
    """
    Index management utilities for:
    - Index creation and dropping
    - Index usage analysis
    - Index recommendations
    """
    
    def __init__(self):
        self.db_utils = DatabaseUtils()
        
    async def initialize(self):
        """
Initialize index utilities"""
        await self.db_utils.initialize()
    
    async def get_index_usage_stats(self, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
Get index usage statistics"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                if table_name:
                    query = text("""
                        SELECT 
                            schemaname,
                            tablename,
                            indexname,
                            idx_scan as scans,
                            idx_tup_read as tuples_read,
                            idx_tup_fetch as tuples_fetched,
                            pg_size_pretty(pg_relation_size(indexname::regclass)) as size
                        FROM pg_stat_user_indexes
                        WHERE tablename = :table_name
                        ORDER BY idx_scan DESC
                    """)
                    result = await session.execute(query, {'table_name': table_name})
                else:
                    query = text("""
                        SELECT 
                            schemaname,
                            tablename,
                            indexname,
                            idx_scan as scans,
                            idx_tup_read as tuples_read,
                            idx_tup_fetch as tuples_fetched,
                            pg_size_pretty(pg_relation_size(indexname::regclass)) as size
                        FROM pg_stat_user_indexes
                        ORDER BY idx_scan DESC
                    """)
                    result = await session.execute(query)
                
                return [dict(row._mapping) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting index usage stats: {e}")
            return []
    
    async def find_unused_indexes(self, min_size_mb: int = 10) -> List[Dict[str, Any]]:
        """Find unused indexes that are consuming space"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                query = text("""
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan as scans,
                        pg_relation_size(indexname::regclass) as size_bytes,
                        pg_size_pretty(pg_relation_size(indexname::regclass)) as size_pretty
                    FROM pg_stat_user_indexes
                    WHERE idx_scan = 0 
                    AND pg_relation_size(indexname::regclass) > :min_size_bytes
                    AND indexname NOT LIKE '%_pkey'  -- Exclude primary keys
                    ORDER BY pg_relation_size(indexname::regclass) DESC
                """)
                
                min_size_bytes = min_size_mb * 1024 * 1024
                result = await session.execute(query, {'min_size_bytes': min_size_bytes})
                
                return [dict(row._mapping) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Error finding unused indexes: {e}")
            return []
    
    async def find_duplicate_indexes(self) -> List[Dict[str, Any]]:
        """Find duplicate or redundant indexes"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                query = text("""
                    SELECT 
                        t.relname as table_name,
                        array_agg(i.relname) as index_names,
                        array_agg(a.attname ORDER BY a.attnum) as columns,
                        COUNT(*) as duplicate_count
                    FROM pg_class i
                    JOIN pg_index ix ON i.oid = ix.indexrelid
                    JOIN pg_class t ON ix.indrelid = t.oid
                    JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                    WHERE i.relkind = 'i'
                    AND t.relkind = 'r'
                    AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                    GROUP BY t.relname, ix.indkey
                    HAVING COUNT(*) > 1
                    ORDER BY t.relname, duplicate_count DESC
                """)
                
                result = await session.execute(query)
                return [dict(row._mapping) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Error finding duplicate indexes: {e}")
            return []
    
    async def analyze_index_recommendations(self, table_name: str) -> Dict[str, Any]:
        """Analyze and recommend indexes for a table"""
        try:
            recommendations = []
            
            async with self.db_utils.session_manager.get_async_session() as session:
                # Get frequently queried columns (this would need query log analysis in practice)
                # For now, we'll look at foreign key columns and frequently updated columns
                
                # Check for foreign keys without indexes
                fk_query = text("""
                    SELECT 
                        kcu.column_name,
                        ccu.table_name AS references_table,
                        ccu.column_name AS references_column
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.table_name = :table_name
                    AND tc.constraint_type = 'FOREIGN KEY'
                """)
                
                fk_result = await session.execute(fk_query, {'table_name': table_name})
                
                for fk in fk_result.fetchall():
                    # Check if there's already an index on this column
                    index_check_query = text("""
                        SELECT COUNT(*) 
                        FROM pg_indexes 
                        WHERE tablename = :table_name 
                        AND indexdef LIKE :column_pattern
                    """)
                    
                    index_check_result = await session.execute(index_check_query, {
                        'table_name': table_name,
                        'column_pattern': f'%{fk.column_name}%'
                    })
                    
                    index_count = index_check_result.scalar()
                    
                    if index_count == 0:
                        recommendations.append({
                            'type': 'missing_fk_index',
                            'column': fk.column_name,
                            'reason': f'Foreign key to {fk.references_table}.{fk.references_column} lacks index',
                            'recommended_sql': f'CREATE INDEX idx_{table_name}_{fk.column_name} ON {table_name}({fk.column_name});',
                            'priority': 'high'
                        })
                
                # Check for columns that might benefit from partial indexes
                # (columns with high null percentage)
                table_stats = await self.db_utils.db_utils.get_table_statistics(table_name)
                if table_stats.get('success'):
                    for col_stat in table_stats.get('column_statistics', []):
                        if (col_stat['null_percentage'] > 80 and 
                            col_stat['non_null_count'] > 1000):
                            recommendations.append({
                                'type': 'partial_index',
                                'column': col_stat['column_name'],
                                'reason': f'High null percentage ({col_stat["null_percentage"]}%) - consider partial index',
                                'recommended_sql': f'CREATE INDEX idx_{table_name}_{col_stat["column_name"]}_not_null ON {table_name}({col_stat["column_name"]}) WHERE {col_stat["column_name"]} IS NOT NULL;',
                                'priority': 'medium'
                            })
                
                return {
                    'success': True,
                    'table_name': table_name,
                    'recommendations': recommendations,
                    'total_recommendations': len(recommendations)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing index recommendations for {table_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def create_index(self, table_name: str, columns: List[str], 
                          index_name: Optional[str] = None,
                          index_type: IndexType = IndexType.BTREE,
                          unique: bool = False,
                          where_condition: Optional[str] = None) -> Dict[str, Any]:
        """Create an index on specified columns"""
        try:
            if not index_name:
                index_name = f"idx_{table_name}_{'_'.join(columns)}"
            
            # Build CREATE INDEX statement
            create_sql = "CREATE"
            if unique:
                create_sql += " UNIQUE"
            
            create_sql += f" INDEX {index_name} ON {table_name}"
            
            if index_type != IndexType.BTREE:
                create_sql += f" USING {index_type.value}"
            
            create_sql += f" ({', '.join(columns)})"
            
            if where_condition:
                create_sql += f" WHERE {where_condition}"
            
            # Execute index creation
            engine = self.db_utils.db_connection.get_postgresql_engine(async_mode=False)
            
            with engine.connect() as conn:
                conn = conn.execution_options(autocommit=True)
                
                start_time = time.time()
                conn.execute(text(create_sql))
                execution_time = time.time() - start_time
                
                return {
                    'success': True,
                    'index_name': index_name,
                    'table_name': table_name,
                    'columns': columns,
                    'index_type': index_type.value,
                    'unique': unique,
                    'where_condition': where_condition,
                    'sql_executed': create_sql,
                    'execution_time': execution_time
                }
                
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def drop_index(self, index_name: str, cascade: bool = False) -> Dict[str, Any]:
        """Drop an index"""
        try:
            drop_sql = f"DROP INDEX {index_name}"
            if cascade:
                drop_sql += " CASCADE"
            
            engine = self.db_utils.db_connection.get_postgresql_engine(async_mode=False)
            
            with engine.connect() as conn:
                conn = conn.execution_options(autocommit=True)
                
                start_time = time.time()
                conn.execute(text(drop_sql))
                execution_time = time.time() - start_time
                
                return {
                    'success': True,
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
                return {
                    'success': True,
                    'index_name': index_name,
                    'cascade': cascade,
                    'sql_executed': drop_sql,
                    'execution_time': execution_time
                }
                
        except Exception as e:
            logger.error(f"Error dropping index {index_name}: {e}")
            return {'success': False, 'error': str(e)}


class ConstraintUtils:
    """
    Constraint management utilities for:
    - Constraint validation
    - Constraint creation and dropping
    - Data integrity checks
    """
    
    def __init__(self):
        self.db_utils = DatabaseUtils()
        
    async def initialize(self):
        """
Initialize constraint utilities"""
        await self.db_utils.initialize()
    
    async def validate_all_constraints(self, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
Validate all constraints in database or specific table"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                if table_name:
                    # Validate constraints for specific table
                    return await self._validate_table_constraints(session, table_name)
                else:
                    # Validate all constraints
                    tables = await self.db_utils.list_all_tables()
                    all_results = {}
                    
                    for table in tables:
                        result = await self._validate_table_constraints(session, table)
                        all_results[table] = result
                    
                    return {
                        'success': True,
                        'tables_checked': len(tables),
                        'results': all_results
                    }
                    
        except Exception as e:
            logger.error(f"Error validating constraints: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _validate_table_constraints(self, session: AsyncSession, table_name: str) -> Dict[str, Any]:
        """Validate constraints for a specific table"""
        violations = []
        
        try:
            # Get all constraints for the table
            constraints_query = text("""
                SELECT 
                    tc.constraint_name,
                    tc.constraint_type,
                    kcu.column_name,
                    cc.check_clause,
                    ccu.table_name AS references_table,
                    ccu.column_name AS references_column
                FROM information_schema.table_constraints tc
                LEFT JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                LEFT JOIN information_schema.check_constraints cc
                    ON tc.constraint_name = cc.constraint_name
                LEFT JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.table_name = :table_name
                ORDER BY tc.constraint_type, tc.constraint_name
            """)
            
            constraints_result = await session.execute(constraints_query, {'table_name': table_name})
            constraints = constraints_result.fetchall()
            
            for constraint in constraints:
                if constraint.constraint_type == 'FOREIGN KEY':
                    # Check foreign key violations
                    fk_violations_query = text(f"""
                        SELECT COUNT(*) as violation_count
                        FROM {table_name} t
                        WHERE t.{constraint.column_name} IS NOT NULL
                        AND NOT EXISTS (
                            SELECT 1 FROM {constraint.references_table} r
                            WHERE r.{constraint.references_column} = t.{constraint.column_name}
                        )
                    """)
                    
                    fk_result = await session.execute(fk_violations_query)
                    violation_count = fk_result.scalar()
                    
                    if violation_count > 0:
                        violations.append({
                            'constraint_name': constraint.constraint_name,
                            'constraint_type': constraint.constraint_type,
                            'column': constraint.column_name,
                            'violation_count': violation_count,
                            'details': f'Foreign key violations in column {constraint.column_name}'
                        })
                
                elif constraint.constraint_type == 'CHECK':
                    # Check constraint violations
                    if constraint.check_clause:
                        check_violations_query = text(f"""
                            SELECT COUNT(*) as violation_count
                            FROM {table_name}
                            WHERE NOT ({constraint.check_clause})
                        """)
                        
                        check_result = await session.execute(check_violations_query)
                        violation_count = check_result.scalar()
                        
                        if violation_count > 0:
                            violations.append({
                                'constraint_name': constraint.constraint_name,
                                'constraint_type': constraint.constraint_type,
                                'violation_count': violation_count,
                                'details': f'Check constraint violations: {constraint.check_clause}'
                            })
                
                elif constraint.constraint_type == 'UNIQUE':
                    # Check unique constraint violations
                    unique_violations_query = text(f"""
                        SELECT {constraint.column_name}, COUNT(*) as duplicate_count
                        FROM {table_name}
                        GROUP BY {constraint.column_name}
                        HAVING COUNT(*) > 1
                        LIMIT 10
                    """)
                    
                    unique_result = await session.execute(unique_violations_query)
                    unique_violations = unique_result.fetchall()
                    
                    if unique_violations:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
                    unique_result = await session.execute(unique_violations_query)
                    unique_violations = unique_result.fetchall()
                    
                    if unique_violations:
                        violations.append({
                            'constraint_name': constraint.constraint_name,
                            'constraint_type': constraint.constraint_type,
                            'column': constraint.column_name,
                            'violation_count': len(unique_violations),
                            'details': f'Unique constraint violations in column {constraint.column_name}',
                            'sample_violations': [dict(row._mapping) for row in unique_violations]
                        })
            
            return {
                'success': True,
                'table_name': table_name,
                'constraints_checked': len(constraints),
                'violations_found': len(violations),
                'violations': violations,
                'is_valid': len(violations) == 0
            }
            
        except Exception as e:
            logger.error(f"Error validating constraints for {table_name}: {e}")
            return {'success': False, 'table_name': table_name, 'error': str(e)}


class PerformanceAnalyzer:
    """
    Database performance analysis tools:
    - Query performance analysis
    - System resource monitoring
    - Bottleneck identification
    - Optimization recommendations
    """
    
    def __init__(self):
        self.db_utils = DatabaseUtils()
        
    async def initialize(self):
        """
Initialize performance analyzer"""
        await self.db_utils.initialize()
    
    async def get_slow_queries(self, limit: int = 50, min_duration_ms: int = 1000) -> List[Dict[str, Any]]:
        """
Get slow queries from pg_stat_statements"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                # Check if pg_stat_statements extension is available
                extension_check = text("""
                    SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_stat_statements'
                """)
                extension_result = await session.execute(extension_check)
                
                if extension_result.scalar() == 0:
                    logger.warning("pg_stat_statements extension not available")
                    return []
                
                slow_queries_query = text("""
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        min_time,
                        max_time,
                        rows,
                        100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                    FROM pg_stat_statements
                    WHERE mean_time >= :min_duration_ms
                    ORDER BY mean_time DESC
                    LIMIT :limit
                """)
                
                result = await session.execute(slow_queries_query, {
                    'min_duration_ms': min_duration_ms,
                    'limit': limit
                })
                
                return [dict(row._mapping) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting slow queries: {e}")
            return []
    
    async def analyze_table_performance(self, table_name: str) -> Dict[str, Any]:
        """Analyze performance metrics for a specific table"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                # Get table access patterns
                table_stats_query = text("""
                    SELECT 
                        schemaname,
                        relname,
                        seq_scan,
                        seq_tup_read,
                        idx_scan,
                        idx_tup_fetch,
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del,
                        n_tup_hot_upd,
                        n_live_tup,
                        n_dead_tup,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables
                    WHERE relname = :table_name
                """)
                
                table_stats_result = await session.execute(table_stats_query, {'table_name': table_name})
                table_stats = table_stats_result.fetchone()
                
                if not table_stats:
                    return {'success': False, 'error': f'Table {table_name} not found in statistics'}
                
                # Calculate performance ratios
                total_scans = (table_stats.seq_scan or 0) + (table_stats.idx_scan or 0)
                seq_scan_ratio = (table_stats.seq_scan / total_scans * 100) if total_scans > 0 else 0
                
                dead_tuple_ratio = (table_stats.n_dead_tup / max(1, table_stats.n_live_tup) * 100) if table_stats.n_live_tup else 0
                
                hot_update_ratio = (table_stats.n_tup_hot_upd / max(1, table_stats.n_tup_upd) * 100) if table_stats.n_tup_upd else 100
                
                # Get index usage for this table
                index_usage_query = text("""
                    SELECT 
                        indexname,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_stat_user_indexes
                    WHERE tablename = :table_name
                    ORDER BY idx_scan DESC
                """)
                
                index_usage_result = await session.execute(index_usage_query, {'table_name': table_name})
                index_usage = [dict(row._mapping) for row in index_usage_result.fetchall()]
                
                # Performance assessment
                issues = []
                if seq_scan_ratio > 50:
                    issues.append(f"High sequential scan ratio ({seq_scan_ratio:.1f}%) - consider adding indexes")
                
                if dead_tuple_ratio > 20:
                    issues.append(f"High dead tuple ratio ({dead_tuple_ratio:.1f}%) - table needs vacuuming")
                
                if hot_update_ratio < 50:
                    issues.append(f"Low HOT update ratio ({hot_update_ratio:.1f}%) - consider column ordering optimization")
                
                return {
                    'success': True,
                    'table_name': table_name,
                    'performance_metrics': {
                        'total_scans': total_scans,
                        'sequential_scans': table_stats.seq_scan,
                        'index_scans': table_stats.idx_scan,
                        'seq_scan_ratio': round(seq_scan_ratio, 2),
                        'live_tuples': table_stats.n_live_tup,
                        'dead_tuples': table_stats.n_dead_tup,
                        'dead_tuple_ratio': round(dead_tuple_ratio, 2),
                        'hot_update_ratio': round(hot_update_ratio, 2),
                        'total_inserts': table_stats.n_tup_ins,
                        'total_updates': table_stats.n_tup_upd,
                        'total_deletes': table_stats.n_tup_del
                    },
                    'index_usage': index_usage,
                    'maintenance_info': {
                        'last_vacuum': table_stats.last_vacuum,
                        'last_autovacuum': table_stats.last_autovacuum,
                        'last_analyze': table_stats.last_analyze,
                        'last_autoanalyze': table_stats.last_autoanalyze
                    },
                    'performance_issues': issues,
                    'overall_health': 'good' if not issues else 'needs_attention'
                }
                
        except Exception as e:
            logger.error(f"Error analyzing table performance for {table_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_database_performance_overview(self) -> Dict[str, Any]:
        """Get overall database performance overview"""
        try:
            async with self.db_utils.session_manager.get_async_session() as session:
                # Database-wide statistics
                db_stats_query = text("""
                    SELECT 
                        numbackends as active_connections,
                        xact_commit as committed_transactions,
                        xact_rollback as rolled_back_transactions,
                        blks_read as disk_blocks_read,
                        blks_hit as buffer_hits,
                        tup_returned as tuples_returned,
                        tup_fetched as tuples_fetched,
                        tup_inserted as tuples_inserted,
                        tup_updated as tuples_updated,
                        tup_deleted as tuples_deleted
                    FROM pg_stat_database
                    WHERE datname = current_database()
                """)
                
                db_stats_result = await session.execute(db_stats_query)
                db_stats = db_stats_result.fetchone()
                
                if not db_stats:
                    return {'success': False, 'error': 'Could not retrieve database statistics'}
                
                # Calculate cache hit ratio
                total_blocks = db_stats.disk_blocks_read + db_stats.buffer_hits
                cache_hit_ratio = (db_stats.buffer_hits / total_blocks * 100) if total_blocks > 0 else 0
                
                # Transaction success ratio
                total_transactions = db_stats.committed_transactions + db_stats.rolled_back_transactions
                transaction_success_ratio = (db_stats.committed_transactions / total_transactions * 100) if total_transactions > 0 else 0
                
                # Get lock statistics
                locks_query = text("""
                    SELECT 
                        mode,
                        COUNT(*) as lock_count
                    FROM pg_locks
                    WHERE granted = true
                    GROUP BY mode
                    ORDER BY lock_count DESC
                """)
                
                locks_result = await session.execute(locks_query)
                lock_stats = {row.mode: row.lock_count for row in locks_result.fetchall()}
                
                # Get connection information
                connections_query = text("""
                    SELECT 
                        state,
                        COUNT(*) as connection_count
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                    GROUP BY state
                """)
                
                connections_result = await session.execute(connections_query)
                connection_stats = {row.state: row.connection_count for row in connections_result.fetchall()}
                
                return {
                    'success': True,
                    'database_metrics': {
                        'active_connections': db_stats.active_connections,
                        'cache_hit_ratio': round(cache_hit_ratio, 2),
                        'transaction_success_ratio': round(transaction_success_ratio, 2),
                        'total_transactions': total_transactions,
                        'committed_transactions': db_stats.committed_transactions,
                        'rolled_back_transactions': db_stats.rolled_back_transactions,
                        'disk_blocks_read': db_stats.disk_blocks_read,
                        'buffer_hits': db_stats.buffer_hits
                    },
                    'activity_metrics': {
                        'tuples_returned': db_stats.tuples_returned,
                        'tuples_fetched': db_stats.tuples_fetched,
                        'tuples_inserted': db_stats.tuples_inserted,
                        'tuples_updated': db_stats.tuples_updated,
                        'tuples_deleted': db_stats.tuples_deleted
                    },
                    'lock_statistics': lock_stats,
                    'connection_statistics': connection_stats,
                    'performance_assessment': self._assess_performance(cache_hit_ratio, transaction_success_ratio),
                    'measured_at': datetime.utcnow()
                }
                
        except Exception as e:
            logger.error(f"Error getting database performance overview: {e}")
            return {'success': False, 'error': str(e)}
    
    def _assess_performance(self, cache_hit_ratio: float, transaction_success_ratio: float) -> Dict[str, Any]:
        """Assess overall database performance"""
        issues = []
        recommendations = []
        
        if cache_hit_ratio < 95:
            issues.append(f"Low buffer cache hit ratio ({cache_hit_ratio:.1f}%)")
            recommendations.append("Consider increasing shared_buffers parameter")
        
        if transaction_success_ratio < 95:
            issues.append(f"High transaction rollback ratio ({100 - transaction_success_ratio:.1f}%)")
            recommendations.append("Investigate application logic causing transaction failures")
        
        if cache_hit_ratio >= 95 and transaction_success_ratio >= 99:
            overall_health = "excellent"
        elif cache_hit_ratio >= 90 and transaction_success_ratio >= 95:
            overall_health = "good"
        elif cache_hit_ratio >= 80 and transaction_success_ratio >= 90:
            overall_health = "fair"
        else:
            overall_health = "poor"
        
        return {
            'overall_health': overall_health,
            'issues': issues,
            'recommendations': recommendations
        }
