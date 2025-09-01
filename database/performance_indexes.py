"""Production Performance Index Management

This module provides automated index creation and management for high-volume
tables in the Ainflue production database.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy import text, MetaData, Table, Index
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.engine import Engine
import json

logger = logging.getLogger(__name__)

@dataclass
class IndexDefinition:
    """Definition of a database index."""
    name: str
    table: str
    columns: List[str]
    unique: bool = False
    partial_condition: Optional[str] = None
    index_type: str = 'btree'
    description: str = ''

@dataclass
class IndexStats:
    """Statistics for a database index."""
    name: str
    size_bytes: int
    scans: int
    tuples_read: int
    tuples_fetched: int
    effectiveness_ratio: float

class ProductionIndexManager:
    """Manages performance indexes for production database."""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.indexes = self._define_production_indexes()
    
    def _define_production_indexes(self) -> List[IndexDefinition]:
        """Define all production indexes for high-volume tables."""
        return [
            # Content-related indexes
            IndexDefinition(
                name='idx_content_creator_id_status',
                table='content_metadata',
                columns=['creator_id', 'status'],
                description='Fast lookup of content by creator and status'
            ),
            IndexDefinition(
                name='idx_content_created_at_desc',
                table='content_metadata',
                columns=['created_at DESC'],
                description='Chronological content ordering'
            ),
            IndexDefinition(
                name='idx_content_fingerprint_hash',
                table='content_metadata',
                columns=['fingerprint_hash'],
                unique=True,
                description='Unique content fingerprint lookup'
            ),
            IndexDefinition(
                name='idx_content_platform_content_id',
                table='content_metadata',
                columns=['platform', 'content_id'],
                unique=True,
                description='Platform-specific content identification'
            ),
            IndexDefinition(
                name='idx_content_visibility_published',
                table='content_metadata',
                columns=['visibility', 'published_at'],
                partial_condition="status = 'published'",
                description='Public content discovery'
            ),
            
            # User and Creator indexes
            IndexDefinition(
                name='idx_users_email_lower',
                table='users',
                columns=['LOWER(email)'],
                unique=True,
                description='Case-insensitive email lookup'
            ),
            IndexDefinition(
                name='idx_users_username_lower',
                table='users',
                columns=['LOWER(username)'],
                unique=True,
                description='Case-insensitive username lookup'
            ),
            IndexDefinition(
                name='idx_creators_verification_status',
                table='creators',
                columns=['verification_status', 'created_at'],
                description='Creator verification queries'
            ),
            
            # Analytics indexes
            IndexDefinition(
                name='idx_analytics_event_date_type',
                table='analytics_events',
                columns=['event_date', 'event_type'],
                description='Analytics aggregation by date and type'
            ),
            IndexDefinition(
                name='idx_analytics_user_content',
                table='analytics_events',
                columns=['user_id', 'content_id', 'event_date'],
                description='User-content analytics tracking'
            ),
            IndexDefinition(
                name='idx_analytics_session_id',
                table='analytics_events',
                columns=['session_id'],
                description='Session-based analytics'
            ),
            
            # Rights tracking indexes
            IndexDefinition(
                name='idx_rights_content_id_status',
                table='rights_records',
                columns=['content_id', 'status'],
                description='Rights status lookup per content'
            ),
            IndexDefinition(
                name='idx_rights_owner_id_active',
                table='rights_records',
                columns=['rights_owner_id'],
                partial_condition="status = 'active'",
                description='Active rights by owner'
            ),
            IndexDefinition(
                name='idx_rights_expiry_date',
                table='rights_records',
                columns=['expiry_date'],
                partial_condition="expiry_date IS NOT NULL",
                description='Rights expiration tracking'
            ),
            
            # License agreements indexes
            IndexDefinition(
                name='idx_licenses_content_licensee',
                table='license_agreements',
                columns=['content_id', 'licensee_id', 'status'],
                description='License lookup by content and licensee'
            ),
            IndexDefinition(
                name='idx_licenses_start_end_date',
                table='license_agreements',
                columns=['start_date', 'end_date'],
                description='License period queries'
            ),
            
            # Payment and revenue indexes
            IndexDefinition(
                name='idx_payments_transaction_id',
                table='payment_records',
                columns=['transaction_id'],
                unique=True,
                description='Payment transaction lookup'
            ),
            IndexDefinition(
                name='idx_payments_creator_date',
                table='payment_records',
                columns=['creator_id', 'payment_date'],
                description='Creator payment history'
            ),
            IndexDefinition(
                name='idx_payments_status_amount',
                table='payment_records',
                columns=['status', 'amount'],
                description='Payment reporting and reconciliation'
            ),
            IndexDefinition(
                name='idx_revenue_content_period',
                table='revenue_tracking',
                columns=['content_id', 'period_start', 'period_end'],
                description='Revenue tracking by content and period'
            ),
            
            # Audit and monitoring indexes
            IndexDefinition(
                name='idx_audit_logs_timestamp_entity',
                table='audit_logs',
                columns=['timestamp DESC', 'entity_type'],
                description='Audit trail chronological lookup'
            ),
            IndexDefinition(
                name='idx_audit_logs_entity_id_action',
                table='audit_logs',
                columns=['entity_id', 'action'],
                description='Entity change history'
            ),
            
            # Performance monitoring indexes
            IndexDefinition(
                name='idx_slow_queries_timestamp_desc',
                table='slow_query_logs',
                columns=['timestamp DESC'],
                description='Recent slow query analysis'
            ),
            IndexDefinition(
                name='idx_slow_queries_execution_time',
                table='slow_query_logs',
                columns=['execution_time_ms DESC'],
                description='Query performance ranking'
            ),
        ]
    
    async def analyze_table_statistics(self) -> Dict[str, Any]:
        """Analyze table statistics to determine index needs."""
        stats_query = """
        SELECT 
            schemaname,
            tablename,
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
        ORDER BY n_live_tup DESC;
        """
        
        async with self.engine.begin() as conn:
            result = await conn.execute(text(stats_query))
            stats = result.fetchall()
        
        return {
            'table_statistics': [dict(row._mapping) for row in stats],
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    async def check_missing_indexes(self) -> List[str]:
        """Check for missing indexes from our definition."""
        existing_indexes_query = """
        SELECT 
            indexname,
            tablename,
            indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public'
        AND indexname NOT LIKE 'pg_%';
        """
        
        async with self.engine.begin() as conn:
            result = await conn.execute(text(existing_indexes_query))
            existing = {row.indexname for row in result}
        
        missing = []
        for index_def in self.indexes:
            if index_def.name not in existing:
                missing.append(index_def.name)
        
        return missing
    
    async def create_index(self, index_def: IndexDefinition, if_not_exists: bool = True) -> bool:
        """Create a single index."""
        try:
            # Build CREATE INDEX statement
            sql_parts = ['CREATE']
            
            if index_def.unique:
                sql_parts.append('UNIQUE')
            
            sql_parts.append('INDEX')
            
            if if_not_exists:
                sql_parts.append('IF NOT EXISTS')
            
            sql_parts.append(index_def.name)
            sql_parts.append('ON')
            sql_parts.append(index_def.table)
            
            if index_def.index_type != 'btree':
                sql_parts.append(f'USING {index_def.index_type}')
            
            # Format column list
            columns_str = ', '.join(index_def.columns)
            sql_parts.append(f'({columns_str})')
            
            if index_def.partial_condition:
                sql_parts.append(f'WHERE {index_def.partial_condition}')
            
            create_sql = ' '.join(sql_parts) + ';'
            
            logger.info(f"Creating index {index_def.name}: {index_def.description}")
            logger.debug(f"SQL: {create_sql}")
            
            async with self.engine.begin() as conn:
                await conn.execute(text(create_sql))
            
            logger.info(f"Successfully created index {index_def.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index {index_def.name}: {e}")
            return False
    
    async def create_all_indexes(self, force: bool = False) -> Dict[str, bool]:
        """Create all defined indexes."""
        results = {}
        
        logger.info(f"Creating {len(self.indexes)} production indexes...")
        
        for index_def in self.indexes:
            try:
                success = await self.create_index(index_def, if_not_exists=not force)
                results[index_def.name] = success
            except Exception as e:
                logger.error(f"Error creating index {index_def.name}: {e}")
                results[index_def.name] = False
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"Created {successful}/{len(self.indexes)} indexes successfully")
        
        return results
    
    async def get_index_statistics(self) -> List[IndexStats]:
        """Get usage statistics for all indexes."""
        stats_query = """
        SELECT 
            i.indexname,
            pg_relation_size(i.indexrelid) as size_bytes,
            s.idx_scan as scans,
            s.idx_tup_read as tuples_read,
            s.idx_tup_fetch as tuples_fetched,
            CASE 
                WHEN s.idx_tup_read > 0 
                THEN (s.idx_tup_fetch::float / s.idx_tup_read) * 100 
                ELSE 0 
            END as effectiveness_ratio
        FROM pg_indexes i
        LEFT JOIN pg_stat_user_indexes s ON i.indexname = s.indexname
        WHERE i.schemaname = 'public'
        AND i.indexname NOT LIKE 'pg_%'
        ORDER BY s.idx_scan DESC NULLS LAST;
        """
        
        async with self.engine.begin() as conn:
            result = await conn.execute(text(stats_query))
            rows = result.fetchall()
        
        return [
            IndexStats(
                name=row.indexname,
                size_bytes=row.size_bytes or 0,
                scans=row.scans or 0,
                tuples_read=row.tuples_read or 0,
                tuples_fetched=row.tuples_fetched or 0,
                effectiveness_ratio=row.effectiveness_ratio or 0
            )
            for row in rows
        ]
    
    async def analyze_unused_indexes(self, min_scans: int = 10) -> List[str]:
        """Find indexes that might be unused."""
        stats = await self.get_index_statistics()
        
        unused = []
        for stat in stats:
            if stat.scans < min_scans and stat.name.startswith('idx_'):
                unused.append(stat.name)
        
        return unused
    
    async def optimize_indexes(self) -> Dict[str, Any]:
        """Perform index optimization."""
        logger.info("Starting index optimization...")
        
        # Analyze current state
        table_stats = await self.analyze_table_statistics()
        index_stats = await self.get_index_statistics()
        missing_indexes = await self.check_missing_indexes()
        unused_indexes = await self.analyze_unused_indexes()
        
        # Create missing indexes
        if missing_indexes:
            logger.info(f"Creating {len(missing_indexes)} missing indexes...")
            creation_results = await self.create_all_indexes()
        else:
            creation_results = {}
        
        # REINDEX heavily used indexes
        heavy_indexes = [stat for stat in index_stats if stat.scans > 1000]
        for index_stat in heavy_indexes:
            try:
                logger.info(f"Reindexing heavily used index: {index_stat.name}")
                async with self.engine.begin() as conn:
                    await conn.execute(text(f"REINDEX INDEX CONCURRENTLY {index_stat.name};"))
            except Exception as e:
                logger.warning(f"Could not reindex {index_stat.name}: {e}")
        
        return {
            'optimization_timestamp': datetime.utcnow().isoformat(),
            'table_statistics': table_stats,
            'missing_indexes_created': creation_results,
            'unused_indexes': unused_indexes,
            'reindexed_count': len(heavy_indexes),
            'total_indexes': len(index_stats)
        }

async def main():
    """Main function for standalone execution."""
    from sqlalchemy.ext.asyncio import create_async_engine
    import os
    
    # Create async engine
    db_url = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
        user=os.getenv('POSTGRES_USER_PRODUCTION', 'ainflue_user'),
        password=os.getenv('POSTGRES_PASSWORD_PRODUCTION', ''),
        host=os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
        port=os.getenv('POSTGRES_PORT_PRODUCTION', '5432'),
        database=os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
    )
    
    engine = create_async_engine(db_url, echo=True)
    manager = ProductionIndexManager(engine)
    
    # Run optimization
    results = await manager.optimize_indexes()
    print(json.dumps(results, indent=2, default=str))

if __name__ == '__main__':
    asyncio.run(main())