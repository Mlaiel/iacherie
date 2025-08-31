"""Index Optimizer Module

Advanced database index management and optimization system for maximum query performance,
including automated index creation, usage analysis, and intelligent recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import hashlib
from sqlalchemy import text, inspect, MetaData, Table, Index, Column
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.dialects import postgresql

from ...core.logging import get_logger
from ...core.config import settings
from ...core.metrics import MetricsCollector

logger = get_logger(__name__)


class IndexType(Enum):
    """Database index types"""    BTREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"
    SPGIST = "spgist"
    BRIN = "brin"
    PARTIAL = "partial"
    UNIQUE = "unique"
    COMPOSITE = "composite"


class IndexStrategy(Enum):
    """Index optimization strategies"""    PERFORMANCE = "performance"
    STORAGE = "storage"
    BALANCED = "balanced"
    WRITE_HEAVY = "write_heavy"
    READ_HEAVY = "read_heavy"


class IndexPriority(Enum):
    """Index creation priorities"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class IndexConfig:
    """Index optimization configuration"""    strategy: IndexStrategy = IndexStrategy.BALANCED
    auto_create: bool = True
    auto_drop: bool = False
    analysis_interval: int = 3600  # seconds
    usage_threshold: float = 0.1  # 10% minimum usage
    size_threshold: int = 100 * 1024 * 1024  # 100MB
    
    # Query analysis settings
    slow_query_threshold: float = 1.0  # seconds
    min_query_count: int = 10
    analysis_window_hours: int = 24
    
    # Index creation settings
    max_index_columns: int = 5
    max_indexes_per_table: int = 20
    concurrent_builds: bool = True
    
    # Monitoring settings
    metrics_enabled: bool = True
    detailed_analysis: bool = True


@dataclass
class IndexMetrics:
    """Index performance metrics"""    total_indexes: int = 0
    used_indexes: int = 0
    unused_indexes: int = 0
    duplicate_indexes: int = 0
    total_size_mb: float = 0.0
    avg_scan_ratio: float = 0.0
    index_hit_ratio: float = 0.0
    maintenance_cost: float = 0.0
    last_analyzed: datetime = field(default_factory=datetime.now)
    
    @property
    def usage_efficiency(self) -> float:
        """Calculate index usage efficiency"""        if self.total_indexes == 0:
            return 0.0
        return self.used_indexes / self.total_indexes
    
    @property
    def space_efficiency(self) -> float:
        """Calculate space efficiency"""        if self.total_size_mb == 0:
            return 100.0
        return (1 - (self.unused_indexes * 100 / self.total_indexes)) if self.total_indexes > 0 else 0.0


@dataclass
class IndexInfo:
    """Database index information"""    name: str
    table_name: str
    columns: List[str]
    index_type: IndexType
    is_unique: bool
    is_partial: bool
    condition: Optional[str] = None
    size_mb: float = 0.0
    scan_count: int = 0
    tuple_read: int = 0
    tuple_fetch: int = 0
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    
    @property
    def scan_ratio(self) -> float:
        """Calculate index scan ratio"""        if self.tuple_read == 0:
            return 0.0
        return self.tuple_fetch / self.tuple_read
    
    @property
    def usage_score(self) -> float:
        """Calculate usage score (0-100)"""        score = 0.0
        
        # Scan frequency (40%)
        if self.scan_count > 0:
            score += min(40, self.scan_count / 100 * 40)
        
        # Scan ratio (30%)
        score += self.scan_ratio * 30
        
        # Recency (20%)
        if self.last_used:
            days_since_use = (datetime.now() - self.last_used).days
            recency_score = max(0, 20 - days_since_use * 2)
            score += recency_score
        
        # Index type efficiency (10%)
        type_scores = {
            IndexType.BTREE: 10,
            IndexType.HASH: 8,
            IndexType.GIN: 9,
            IndexType.GIST: 7,
            IndexType.UNIQUE: 10,
        }
        score += type_scores.get(self.index_type, 5)
        
        return min(100, score)


@dataclass
class QueryPattern:
    """Query pattern for index analysis"""    pattern: str
    count: int
    avg_duration: float
    max_duration: float
    columns_used: Set[str]
    tables_used: Set[str]
    join_conditions: List[str]
    where_conditions: List[str]
    order_by_columns: List[str]
    
    @property
    def priority_score(self) -> float:
        """Calculate query pattern priority for indexing"""        score = 0.0
        
        # Frequency (40%)
        score += min(40, self.count / 100 * 40)
        
        # Performance impact (30%)
        if self.avg_duration > 1.0:
            score += min(30, self.avg_duration * 10)
        
        # Column selectivity (20%)
        score += len(self.columns_used) * 2
        
        # Join complexity (10%)
        score += len(self.join_conditions) * 5
        
        return min(100, score)


@dataclass
class IndexRecommendation:
    """Index creation recommendation"""    table_name: str
    columns: List[str]
    index_type: IndexType
    priority: IndexPriority
    estimated_benefit: float
    estimated_cost: float
    reason: str
    query_patterns: List[str]
    
    @property
    def cost_benefit_ratio(self) -> float:
        """Calculate cost-benefit ratio"""        if self.estimated_cost == 0:
            return float('inf')
        return self.estimated_benefit / self.estimated_cost


class QueryAnalyzer:
    """Analyzes queries to identify indexing opportunities"""    
    def __init__(self, config: IndexConfig):
        self.config = config
        self._query_patterns: Dict[str, QueryPattern] = {}
        self._table_columns: Dict[str, Set[str]] = defaultdict(set)
        
    def analyze_query(self, query: str, duration: float) -> None:
        """Analyze a query for indexing opportunities"""        try:
            # Normalize query
            normalized = self._normalize_query(query)
            pattern_key = self._generate_pattern_key(normalized)
            
            # Extract query components
            tables = self._extract_tables(normalized)
            columns = self._extract_columns(normalized)
            where_conditions = self._extract_where_conditions(normalized)
            order_by = self._extract_order_by(normalized)
            joins = self._extract_joins(normalized)
            
            # Update or create pattern
            if pattern_key in self._query_patterns:
                pattern = self._query_patterns[pattern_key]
                pattern.count += 1
                pattern.avg_duration = (pattern.avg_duration * (pattern.count - 1) + duration) / pattern.count
                pattern.max_duration = max(pattern.max_duration, duration)
            else:
                pattern = QueryPattern(
                    pattern=normalized,
                    count=1,
                    avg_duration=duration,
                    max_duration=duration,
                    columns_used=columns,
                    tables_used=tables,
                    join_conditions=joins,
                    where_conditions=where_conditions,
                    order_by_columns=order_by
                )
                self._query_patterns[pattern_key] = pattern
            
            # Update table-column mappings
            for table in tables:
                self._table_columns[table].update(columns)
                
        except Exception as e:
            logger.warning(f"Query analysis failed: {e}")
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for pattern matching"""        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Replace literals with placeholders
        normalized = re.sub(r"'[^']*'", "?", normalized)
        normalized = re.sub(r'\b\d+\b', "?", normalized)
        normalized = re.sub(r'\$\d+', "?", normalized)
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def _generate_pattern_key(self, normalized_query: str) -> str:
        """Generate a unique key for query pattern"""        return hashlib.md5(normalized_query.encode()).hexdigest()
    
    def _extract_tables(self, query: str) -> Set[str]:
        """Extract table names from query"""        tables = set()
        
        # FROM clause
        from_match = re.search(r'from\s+(\w+)', query)
        if from_match:
            tables.add(from_match.group(1))
        
        # JOIN clauses
        join_matches = re.findall(r'join\s+(\w+)', query)
        tables.update(join_matches)
        
        # UPDATE/INSERT/DELETE
        update_match = re.search(r'update\s+(\w+)', query)
        if update_match:
            tables.add(update_match.group(1))
        
        insert_match = re.search(r'insert\s+into\s+(\w+)', query)
        if insert_match:
            tables.add(insert_match.group(1))
        
        delete_match = re.search(r'delete\s+from\s+(\w+)', query)
        if delete_match:
            tables.add(delete_match.group(1))
        
        return tables
    
    def _extract_columns(self, query: str) -> Set[str]:
        """Extract column names from query"""        columns = set()
        
        # WHERE conditions
        where_matches = re.findall(r'where.*?(\w+)\s*[=<>!]', query)
        columns.update(where_matches)
        
        # SELECT columns (basic extraction)
        select_match = re.search(r'select\s+(.*?)\s+from', query)
        if select_match:
            select_part = select_match.group(1)
            if select_part != '*':
                # Extract column names (simplified)
                cols = re.findall(r'\b(\w+)\b', select_part)
                columns.update(col for col in cols if not col in ['distinct', 'count', 'sum', 'avg', 'max', 'min'])
        
        # ORDER BY
        order_matches = re.findall(r'order\s+by\s+(\w+)', query)
        columns.update(order_matches)
        
        # GROUP BY
        group_matches = re.findall(r'group\s+by\s+(\w+)', query)
        columns.update(group_matches)
        
        return columns
    
    def _extract_where_conditions(self, query: str) -> List[str]:
        """Extract WHERE conditions"""        where_match = re.search(r'where\s+(.*?)(?:\s+order\s+by|\s+group\s+by|\s+limit|$)', query)
        if where_match:
            where_clause = where_match.group(1)
            # Split by AND/OR and clean up
            conditions = re.split(r'\s+(?:and|or)\s+', where_clause)
            return [cond.strip() for cond in conditions if cond.strip()]
        return []
    
    def _extract_order_by(self, query: str) -> List[str]:
        """Extract ORDER BY columns"""        order_match = re.search(r'order\s+by\s+(.*?)(?:\s+limit|$)', query)
        if order_match:
            order_clause = order_match.group(1)
            columns = re.findall(r'(\w+)', order_clause)
            return columns
        return []
    
    def _extract_joins(self, query: str) -> List[str]:
        """Extract JOIN conditions"""        join_matches = re.findall(r'join\s+\w+\s+on\s+(.*?)(?:\s+join|\s+where|\s+order|\s+group|$)', query)
        return [join.strip() for join in join_matches]
    
    def get_recommendations(self) -> List[IndexRecommendation]:
        """Generate index recommendations based on query analysis"""        recommendations = []
        
        for pattern in self._query_patterns.values():
            if pattern.count < self.config.min_query_count:
                continue
            
            if pattern.avg_duration < self.config.slow_query_threshold:
                continue
            
            recs = self._analyze_pattern_for_indexes(pattern)
            recommendations.extend(recs)
        
        # Sort by priority and cost-benefit ratio
        recommendations.sort(key=lambda x: (x.priority.value, -x.cost_benefit_ratio))
        
        return recommendations
    
    def _analyze_pattern_for_indexes(self, pattern: QueryPattern) -> List[IndexRecommendation]:
        """Analyze a query pattern for index opportunities"""        recommendations = []
        
        for table in pattern.tables_used:
            # WHERE clause indexes
            if pattern.where_conditions:
                rec = self._create_where_index_recommendation(table, pattern)
                if rec:
                    recommendations.append(rec)
            
            # ORDER BY indexes
            if pattern.order_by_columns:
                rec = self._create_order_by_index_recommendation(table, pattern)
                if rec:
                    recommendations.append(rec)
            
            # JOIN indexes
            if pattern.join_conditions:
                rec = self._create_join_index_recommendation(table, pattern)
                if rec:
                    recommendations.append(rec)
        
        return recommendations
    
    def _create_where_index_recommendation(self, table: str, pattern: QueryPattern) -> Optional[IndexRecommendation]:
        """Create index recommendation for WHERE conditions"""        # Extract columns from WHERE conditions
        where_columns = []
        for condition in pattern.where_conditions:
            cols = re.findall(r'\b(\w+)\s*[=<>!]', condition)
            where_columns.extend(cols)
        
        if not where_columns:
            return None
        
        # Limit columns for composite index
        index_columns = where_columns[:self.config.max_index_columns]
        
        priority = self._calculate_priority(pattern)
        benefit = pattern.priority_score
        cost = len(index_columns) * 10  # Simplified cost calculation
        
        return IndexRecommendation(
            table_name=table,
            columns=index_columns,
            index_type=IndexType.BTREE,
            priority=priority,
            estimated_benefit=benefit,
            estimated_cost=cost,
            reason=f"WHERE clause optimization for {len(pattern.where_conditions)} conditions",
            query_patterns=[pattern.pattern]
        )
    
    def _create_order_by_index_recommendation(self, table: str, pattern: QueryPattern) -> Optional[IndexRecommendation]:
        """Create index recommendation for ORDER BY"""        if not pattern.order_by_columns:
            return None
        
        index_columns = pattern.order_by_columns[:self.config.max_index_columns]
        
        priority = self._calculate_priority(pattern)
        benefit = pattern.priority_score * 0.8  # ORDER BY has slightly lower priority
        cost = len(index_columns) * 8
        
        return IndexRecommendation(
            table_name=table,
            columns=index_columns,
            index_type=IndexType.BTREE,
            priority=priority,
            estimated_benefit=benefit,
            estimated_cost=cost,
            reason=f"ORDER BY optimization for {len(index_columns)} columns",
            query_patterns=[pattern.pattern]
        )
    
    def _create_join_index_recommendation(self, table: str, pattern: QueryPattern) -> Optional[IndexRecommendation]:
        """Create index recommendation for JOINs"""        # Extract join columns (simplified)
        join_columns = []
        for join_condition in pattern.join_conditions:
            cols = re.findall(r'\b(\w+)\s*=\s*\w+\.(\w+)', join_condition)
            join_columns.extend([col[0] for col in cols])
        
        if not join_columns:
            return None
        
        index_columns = list(set(join_columns))[:self.config.max_index_columns]
        
        priority = self._calculate_priority(pattern)
        benefit = pattern.priority_score * 1.2  # JOINs have higher priority
        cost = len(index_columns) * 12
        
        return IndexRecommendation(
            table_name=table,
            columns=index_columns,
            index_type=IndexType.BTREE,
            priority=priority,
            estimated_benefit=benefit,
            estimated_cost=cost,
            reason=f"JOIN optimization for {len(pattern.join_conditions)} joins",
            query_patterns=[pattern.pattern]
        )
    
    def _calculate_priority(self, pattern: QueryPattern) -> IndexPriority:
        """Calculate recommendation priority"""        score = pattern.priority_score
        
        if score >= 80:
            return IndexPriority.CRITICAL
        elif score >= 60:
            return IndexPriority.HIGH
        elif score >= 40:
            return IndexPriority.MEDIUM
        else:
            return IndexPriority.LOW


class IndexOptimizer:
    """Advanced database index optimizer"""    
    def __init__(self, config: IndexConfig):
        self.config = config
        self.metrics = IndexMetrics()
        self.metrics_collector = MetricsCollector()
        self.query_analyzer = QueryAnalyzer(config)
        
        # Index tracking
        self._existing_indexes: Dict[str, IndexInfo] = {}
        self._recommendations: List[IndexRecommendation] = []
        
        # Monitoring
        self._last_analysis = datetime.now()
        
    async def analyze_indexes(self, engine: AsyncEngine) -> None:
        """Analyze existing indexes and their usage"""        try:
            logger.info("Starting index analysis")
            
            async with engine.begin() as conn:
                # Get index information
                await self._collect_index_info(conn)
                
                # Get index usage statistics
                await self._collect_usage_stats(conn)
                
                # Analyze for duplicates
                await self._detect_duplicate_indexes()
                
                # Update metrics
                self._update_metrics()
            
            self._last_analysis = datetime.now()
            logger.info("Index analysis completed")
            
        except Exception as e:
            logger.error(f"Index analysis failed: {e}")
            raise
    
    async def _collect_index_info(self, conn) -> None:
        """Collect index information from database"""        # PostgreSQL-specific query
        query = text("""            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef,
                COALESCE(pg_relation_size(indexrelid), 0) as size_bytes
            FROM pg_indexes 
            LEFT JOIN pg_stat_user_indexes USING (schemaname, tablename, indexname)
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        
        result = await conn.execute(query)
        
        for row in result:
            index_info = self._parse_index_definition(row)
            if index_info:
                self._existing_indexes[index_info.name] = index_info
    
    async def _collect_usage_stats(self, conn) -> None:
        """Collect index usage statistics"""        query = text("""            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
        """)
        
        result = await conn.execute(query)
        
        for row in result:
            index_name = row.indexname
            if index_name in self._existing_indexes:
                index_info = self._existing_indexes[index_name]
                index_info.scan_count = row.idx_scan or 0
                index_info.tuple_read = row.idx_tup_read or 0
                index_info.tuple_fetch = row.idx_tup_fetch or 0
    
    def _parse_index_definition(self, row) -> Optional[IndexInfo]:
        """Parse index definition from database row"""        try:
            index_def = row.indexdef
            index_name = row.indexname
            table_name = row.tablename
            size_mb = (row.size_bytes or 0) / (1024 * 1024)
            
            # Parse index type
            index_type = IndexType.BTREE  # Default
            if 'USING gin' in index_def.lower():
                index_type = IndexType.GIN
            elif 'USING gist' in index_def.lower():
                index_type = IndexType.GIST
            elif 'USING hash' in index_def.lower():
                index_type = IndexType.HASH
            elif 'USING spgist' in index_def.lower():
                index_type = IndexType.SPGIST
            elif 'USING brin' in index_def.lower():
                index_type = IndexType.BRIN
            
            # Parse columns
            columns = self._extract_index_columns(index_def)
            
            # Check if unique
            is_unique = 'UNIQUE' in index_def.upper()
            
            # Check if partial
            is_partial = 'WHERE' in index_def.upper()
            condition = None
            if is_partial:
                where_match = re.search(r'WHERE\s+(.+)$', index_def, re.IGNORECASE)
                if where_match:
                    condition = where_match.group(1)
            
            return IndexInfo(
                name=index_name,
                table_name=table_name,
                columns=columns,
                index_type=index_type,
                is_unique=is_unique,
                is_partial=is_partial,
                condition=condition,
                size_mb=size_mb
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse index definition: {e}")
            return None
    
    def _extract_index_columns(self, index_def: str) -> List[str]:
        """Extract column names from index definition"""        # Find the column list in parentheses
        match = re.search(r'\(([^)]+)\)', index_def)
        if not match:
            return []
        
        columns_str = match.group(1)
        
        # Split by comma and clean up
        columns = []
        for col in columns_str.split(','):
            col = col.strip()
            # Remove function calls, just get the column name
            col_match = re.search(r'\b(\w+)\b', col)
            if col_match:
                columns.append(col_match.group(1))
        
        return columns
    
    async def _detect_duplicate_indexes(self) -> None:
        """Detect duplicate or redundant indexes"""        duplicates = 0
        
        # Group indexes by table
        table_indexes = defaultdict(list)
        for index_info in self._existing_indexes.values():
            table_indexes[index_info.table_name].append(index_info)
        
        for table, indexes in table_indexes.items():
            # Check for exact duplicates
            column_sets = defaultdict(list)
            for index in indexes:
                column_key = tuple(sorted(index.columns))
                column_sets[column_key].append(index)
            
            for column_key, duplicate_indexes in column_sets.items():
                if len(duplicate_indexes) > 1:
                    duplicates += len(duplicate_indexes) - 1
                    logger.warning(f"Duplicate indexes found on {table}.{column_key}: {[idx.name for idx in duplicate_indexes]}")
        
        self.metrics.duplicate_indexes = duplicates
    
    def _update_metrics(self) -> None:
        """Update index metrics"""        total_indexes = len(self._existing_indexes)
        used_indexes = sum(1 for idx in self._existing_indexes.values() if idx.scan_count > 0)
        unused_indexes = total_indexes - used_indexes
        total_size = sum(idx.size_mb for idx in self._existing_indexes.values())
        
        # Calculate averages
        if total_indexes > 0:
            avg_scan_ratio = sum(idx.scan_ratio for idx in self._existing_indexes.values()) / total_indexes
            index_hit_ratio = used_indexes / total_indexes
        else:
            avg_scan_ratio = 0.0
            index_hit_ratio = 0.0
        
        # Update metrics
        self.metrics.total_indexes = total_indexes
        self.metrics.used_indexes = used_indexes
        self.metrics.unused_indexes = unused_indexes
        self.metrics.total_size_mb = total_size
        self.metrics.avg_scan_ratio = avg_scan_ratio
        self.metrics.index_hit_ratio = index_hit_ratio
        self.metrics.last_analyzed = datetime.now()
        
        # Send to monitoring
        if self.config.metrics_enabled:
            self._send_metrics()
    
    async def generate_recommendations(self) -> List[IndexRecommendation]:
        """Generate index optimization recommendations"""        recommendations = []
        
        # Query-based recommendations
        query_recs = self.query_analyzer.get_recommendations()
        recommendations.extend(query_recs)
        
        # Usage-based recommendations
        usage_recs = self._generate_usage_recommendations()
        recommendations.extend(usage_recs)
        
        # Deduplicate and prioritize
        recommendations = self._deduplicate_recommendations(recommendations)
        
        self._recommendations = recommendations
        return recommendations
    
    def _generate_usage_recommendations(self) -> List[IndexRecommendation]:
        """Generate recommendations based on index usage patterns"""        recommendations = []
        
        for index_info in self._existing_indexes.values():
            # Recommend dropping unused indexes
            if (index_info.scan_count == 0 and 
                index_info.size_mb > 10 and  # Only consider larger indexes
                not index_info.is_unique):  # Don't drop unique indexes
                
                rec = IndexRecommendation(
                    table_name=index_info.table_name,
                    columns=index_info.columns,
                    index_type=index_info.index_type,
                    priority=IndexPriority.MEDIUM,
                    estimated_benefit=index_info.size_mb,  # Space savings
                    estimated_cost=0,  # No cost to drop
                    reason=f"Unused index consuming {index_info.size_mb:.1f}MB",
                    query_patterns=[]
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[IndexRecommendation]) -> List[IndexRecommendation]:
        """Remove duplicate recommendations"""        seen = set()
        unique_recs = []
        
        for rec in recommendations:
            key = (rec.table_name, tuple(sorted(rec.columns)), rec.index_type)
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
        
        return unique_recs
    
    async def create_index(self, engine: AsyncEngine, recommendation: IndexRecommendation) -> bool:
        """Create an index based on recommendation"""        try:
            if not self.config.auto_create:
                logger.info(f"Auto-create disabled, skipping index creation: {recommendation.table_name}.{recommendation.columns}")
                return False
            
            index_name = self._generate_index_name(recommendation)
            
            # Check if index already exists
            if index_name in self._existing_indexes:
                logger.info(f"Index already exists: {index_name}")
                return False
            
            # Generate CREATE INDEX statement
            create_sql = self._generate_create_index_sql(index_name, recommendation)
            
            logger.info(f"Creating index: {create_sql}")
            
            async with engine.begin() as conn:
                if self.config.concurrent_builds:
                    create_sql += " CONCURRENTLY"
                
                await conn.execute(text(create_sql))
                
            logger.info(f"Successfully created index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index {recommendation.table_name}.{recommendation.columns}: {e}")
            return False
    
    async def drop_index(self, engine: AsyncEngine, index_name: str) -> bool:
        """Drop an unused index"""        try:
            if not self.config.auto_drop:
                logger.info(f"Auto-drop disabled, skipping index drop: {index_name}")
                return False
            
            logger.info(f"Dropping unused index: {index_name}")
            
            async with engine.begin() as conn:
                drop_sql = f"DROP INDEX CONCURRENTLY IF EXISTS {index_name}"
                await conn.execute(text(drop_sql))
            
            # Remove from tracking
            if index_name in self._existing_indexes:
                del self._existing_indexes[index_name]
            
            logger.info(f"Successfully dropped index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop index {index_name}: {e}")
            return False
    
    def _generate_index_name(self, recommendation: IndexRecommendation) -> str:
        """Generate a unique index name"""        table = recommendation.table_name
        columns = "_".join(recommendation.columns[:3])  # Limit length
        suffix = recommendation.index_type.value
        
        # Ensure uniqueness
        base_name = f"idx_{table}_{columns}_{suffix}"
        index_name = base_name
        counter = 1
        
        while index_name in self._existing_indexes:
            index_name = f"{base_name}_{counter}"
            counter += 1
        
        return index_name
    
    def _generate_create_index_sql(self, index_name: str, recommendation: IndexRecommendation) -> str:
        """Generate CREATE INDEX SQL statement"""        table = recommendation.table_name
        columns = ", ".join(recommendation.columns)
        index_type = recommendation.index_type.value.upper()
        
        sql = f"CREATE INDEX {index_name} ON {table}"
        
        if index_type != "BTREE":
            sql += f" USING {index_type}"
        
        sql += f" ({columns})"
        
        return sql
    
    def add_query_for_analysis(self, query: str, duration: float) -> None:
        """Add a query for analysis"""        self.query_analyzer.analyze_query(query, duration)
    
    def _send_metrics(self) -> None:
        """Send metrics to monitoring system"""        self.metrics_collector.gauge("database_indexes_total", self.metrics.total_indexes)
        self.metrics_collector.gauge("database_indexes_used", self.metrics.used_indexes)
        self.metrics_collector.gauge("database_indexes_unused", self.metrics.unused_indexes)
        self.metrics_collector.gauge("database_indexes_duplicate", self.metrics.duplicate_indexes)
        self.metrics_collector.gauge("database_indexes_size_mb", self.metrics.total_size_mb)
        self.metrics_collector.gauge("database_index_usage_efficiency", self.metrics.usage_efficiency)
        self.metrics_collector.gauge("database_index_hit_ratio", self.metrics.index_hit_ratio)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive index statistics"""        return {
            "total_indexes": self.metrics.total_indexes,
            "used_indexes": self.metrics.used_indexes,
            "unused_indexes": self.metrics.unused_indexes,
            "duplicate_indexes": self.metrics.duplicate_indexes,
            "total_size_mb": self.metrics.total_size_mb,
            "usage_efficiency": self.metrics.usage_efficiency,
            "space_efficiency": self.metrics.space_efficiency,
            "index_hit_ratio": self.metrics.index_hit_ratio,
            "avg_scan_ratio": self.metrics.avg_scan_ratio,
            "last_analyzed": self.metrics.last_analyzed.isoformat(),
            "recommendations_count": len(self._recommendations),
            "query_patterns_analyzed": len(self.query_analyzer._query_patterns),
        }


# Global index optimizer instance
_index_optimizer: Optional[IndexOptimizer] = None


def get_index_optimizer(config: Optional[IndexConfig] = None) -> IndexOptimizer:
    """Get global index optimizer instance"""    global _index_optimizer
    
    if _index_optimizer is None:
        _index_optimizer = IndexOptimizer(config or IndexConfig())
    
    return _index_optimizer


class IndexAnalyzer:
    """Helper class for index analysis"""    
    @staticmethod
    async def analyze_table_indexes(engine: AsyncEngine, table_name: str) -> Dict[str, Any]:
        """Analyze indexes for a specific table"""        query = text("""            SELECT 
                indexname,
                indexdef,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_relation_size(indexrelid) as size_bytes
            FROM pg_indexes 
            LEFT JOIN pg_stat_user_indexes USING (schemaname, tablename, indexname)
            WHERE tablename = :table_name AND schemaname = 'public'
        """)
        
        async with engine.begin() as conn:
            result = await conn.execute(query, {"table_name": table_name})
            
            indexes = []
            for row in result:
                indexes.append({
                    "name": row.indexname,
                    "definition": row.indexdef,
                    "scan_count": row.idx_scan or 0,
                    "tuples_read": row.idx_tup_read or 0,
                    "tuples_fetched": row.idx_tup_fetch or 0,
                    "size_mb": (row.size_bytes or 0) / (1024 * 1024),
                })
        
        return {
            "table_name": table_name,
            "indexes": indexes,
            "total_indexes": len(indexes),
            "total_size_mb": sum(idx["size_mb"] for idx in indexes),
        }


class ContentProtectionIndexOptimizer:
    """Specialized index optimizer for content protection and fingerprinting"""    
    def __init__(self, base_optimizer: IndexOptimizer):
        self.base_optimizer = base_optimizer
        self.content_indexes = [
            # Content fingerprints table optimizations
            IndexRecommendation(
                table_name="content_fingerprints",
                columns=["user_id", "content_type"],
                index_type=IndexType.BTREE,
                expected_benefit=0.85,
                query_pattern="SELECT * FROM content_fingerprints WHERE user_id = ? AND content_type = ?"
            ),
            IndexRecommendation(
                table_name="content_fingerprints",
                columns=["fingerprint_hash"],
                index_type=IndexType.HASH,
                expected_benefit=0.95,
                query_pattern="SELECT * FROM content_fingerprints WHERE fingerprint_hash = ?"
            ),
            IndexRecommendation(
                table_name="content_fingerprints",
                columns=["created_at"],
                index_type=IndexType.BTREE,
                expected_benefit=0.75,
                query_pattern="SELECT * FROM content_fingerprints WHERE created_at >= ? ORDER BY created_at DESC"
            ),
            # Vector embeddings GIN index for metadata searches
            IndexRecommendation(
                table_name="content_fingerprints",
                columns=["metadata"],
                index_type=IndexType.GIN,
                expected_benefit=0.80,
                query_pattern="SELECT * FROM content_fingerprints WHERE metadata @> ?"
            ),
            # Protection alerts optimizations
            IndexRecommendation(
                table_name="protection_alerts",
                columns=["fingerprint_id", "platform"],
                index_type=IndexType.BTREE,
                expected_benefit=0.90,
                query_pattern="SELECT * FROM protection_alerts WHERE fingerprint_id = ? AND platform = ?"
            ),
            IndexRecommendation(
                table_name="protection_alerts",
                columns=["status", "created_at"],
                index_type=IndexType.BTREE,
                expected_benefit=0.85,
                query_pattern="SELECT * FROM protection_alerts WHERE status = ? ORDER BY created_at DESC"
            ),
            IndexRecommendation(
                table_name="protection_alerts",
                columns=["similarity_score"],
                index_type=IndexType.BTREE,
                expected_benefit=0.70,
                query_pattern="SELECT * FROM protection_alerts WHERE similarity_score >= ? ORDER BY similarity_score DESC"
            ),
        ]
    
    async def optimize_content_protection_indexes(self, engine: AsyncEngine) -> List[str]:
        """Create optimized indexes for content protection operations"""        created_indexes = []
        
        for recommendation in self.content_indexes:
            success = await self.base_optimizer.create_index(engine, recommendation)
            if success:
                created_indexes.append(f"{recommendation.table_name}.{recommendation.columns}")
        
        # Create specialized vector search indexes
        await self._create_vector_search_indexes(engine)
        
        return created_indexes
    
    async def _create_vector_search_indexes(self, engine: AsyncEngine) -> None:
        """Create specialized indexes for vector similarity search"""        try:
            async with engine.begin() as conn:
                # Create GiST index for vector similarity if using pgvector
                vector_index_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_fingerprints_vector_embedding
                ON content_fingerprints USING ivfflat (vector_embedding vector_cosine_ops)
                WITH (lists = 100)
                """                await conn.execute(text(vector_index_sql))
                
                # Create partial index for active fingerprints
                active_fingerprints_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_fingerprints_active
                ON content_fingerprints (user_id, created_at)
                WHERE metadata->>'status' = 'active'
                """                await conn.execute(text(active_fingerprints_sql))
                
                logger.info("Successfully created vector search indexes")
                
        except Exception as e:
            logger.error(f"Failed to create vector search indexes: {e}")


class MonetizationIndexOptimizer:
    """Specialized index optimizer for monetization and revenue tracking"""    
    def __init__(self, base_optimizer: IndexOptimizer):
        self.base_optimizer = base_optimizer
        self.monetization_indexes = [
            # Revenue tracking optimizations
            IndexRecommendation(
                table_name="revenue_tracking",
                columns=["user_id", "platform", "period_start"],
                index_type=IndexType.BTREE,
                expected_benefit=0.90,
                query_pattern="SELECT * FROM revenue_tracking WHERE user_id = ? AND platform = ? AND period_start >= ?"
            ),
            IndexRecommendation(
                table_name="revenue_tracking",
                columns=["content_id", "currency"],
                index_type=IndexType.BTREE,
                expected_benefit=0.85,
                query_pattern="SELECT * FROM revenue_tracking WHERE content_id = ? AND currency = ?"
            ),
            IndexRecommendation(
                table_name="revenue_tracking",
                columns=["created_at"],
                index_type=IndexType.BTREE,
                expected_benefit=0.80,
                query_pattern="SELECT * FROM revenue_tracking WHERE created_at >= ? ORDER BY created_at DESC"
            ),
            # Creator analytics optimizations
            IndexRecommendation(
                table_name="creator_analytics",
                columns=["user_id", "platform", "metric_type"],
                index_type=IndexType.BTREE,
                expected_benefit=0.95,
                query_pattern="SELECT * FROM creator_analytics WHERE user_id = ? AND platform = ? AND metric_type = ?"
            ),
            IndexRecommendation(
                table_name="creator_analytics",
                columns=["timestamp", "aggregation_period"],
                index_type=IndexType.BTREE,
                expected_benefit=0.85,
                query_pattern="SELECT * FROM creator_analytics WHERE timestamp >= ? AND aggregation_period = ?"
            ),
        ]
    
    async def optimize_monetization_indexes(self, engine: AsyncEngine) -> List[str]:
        """Create optimized indexes for monetization operations"""        created_indexes = []
        
        for recommendation in self.monetization_indexes:
            success = await self.base_optimizer.create_index(engine, recommendation)
            if success:
                created_indexes.append(f"{recommendation.table_name}.{recommendation.columns}")
        
        # Create specialized aggregation indexes
        await self._create_aggregation_indexes(engine)
        
        return created_indexes
    
    async def _create_aggregation_indexes(self, engine: AsyncEngine) -> None:
        """Create specialized indexes for revenue aggregation"""        try:
            async with engine.begin() as conn:
                # Create partial index for recent revenue data
                recent_revenue_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_revenue_tracking_recent
                ON revenue_tracking (user_id, revenue_amount)
                WHERE created_at >= NOW() - INTERVAL '30 days'
                """                await conn.execute(text(recent_revenue_sql))
                
                # Create expression index for revenue calculations
                revenue_total_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_revenue_tracking_total
                ON revenue_tracking (user_id, (revenue_amount * CASE WHEN currency = 'USD' THEN 1.0 
                                                                   WHEN currency = 'EUR' THEN 1.1 
                                                                   ELSE 1.0 END))
                """                await conn.execute(text(revenue_total_sql))
                
                logger.info("Successfully created aggregation indexes")
                
        except Exception as e:
            logger.error(f"Failed to create aggregation indexes: {e}")


class MultimediaIndexOptimizer:
    """Specialized index optimizer for multimedia content operations"""    
    def __init__(self, base_optimizer: IndexOptimizer):
        self.base_optimizer = base_optimizer
        self.multimedia_indexes = [
            # Content metadata optimizations
            IndexRecommendation(
                table_name="content_metadata",
                columns=["user_id", "content_type"],
                index_type=IndexType.BTREE,
                expected_benefit=0.90,
                query_pattern="SELECT * FROM content_metadata WHERE user_id = ? AND content_type = ?"
            ),
            IndexRecommendation(
                table_name="content_metadata",
                columns=["file_size", "format"],
                index_type=IndexType.BTREE,
                expected_benefit=0.75,
                query_pattern="SELECT * FROM content_metadata WHERE file_size >= ? AND format = ?"
            ),
            IndexRecommendation(
                table_name="content_metadata",
                columns=["duration"],
                index_type=IndexType.BTREE,
                expected_benefit=0.70,
                query_pattern="SELECT * FROM content_metadata WHERE duration >= ? ORDER BY duration DESC"
            ),
            # Vector embeddings optimizations
            IndexRecommendation(
                table_name="vector_embeddings",
                columns=["content_id", "embedding_type"],
                index_type=IndexType.BTREE,
                expected_benefit=0.95,
                query_pattern="SELECT * FROM vector_embeddings WHERE content_id = ? AND embedding_type = ?"
            ),
            IndexRecommendation(
                table_name="vector_embeddings",
                columns=["model_version", "dimension"],
                index_type=IndexType.BTREE,
                expected_benefit=0.80,
                query_pattern="SELECT * FROM vector_embeddings WHERE model_version = ? AND dimension = ?"
            ),
        ]
    
    async def optimize_multimedia_indexes(self, engine: AsyncEngine) -> List[str]:
        """Create optimized indexes for multimedia operations"""        created_indexes = []
        
        for recommendation in self.multimedia_indexes:
            success = await self.base_optimizer.create_index(engine, recommendation)
            if success:
                created_indexes.append(f"{recommendation.table_name}.{recommendation.columns}")
        
        # Create specialized multimedia indexes
        await self._create_multimedia_specific_indexes(engine)
        
        return created_indexes
    
    async def _create_multimedia_specific_indexes(self, engine: AsyncEngine) -> None:
        """Create multimedia-specific specialized indexes"""        try:
            async with engine.begin() as conn:
                # Create GIN index for metadata search
                metadata_search_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_search
                ON content_metadata USING GIN (metadata)
                """                await conn.execute(text(metadata_search_sql))
                
                # Create partial indexes for different content types
                audio_content_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_audio
                ON content_metadata (user_id, duration, quality)
                WHERE content_type = 'audio'
                """                await conn.execute(text(audio_content_sql))
                
                video_content_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_video
                ON content_metadata (user_id, file_size, format)
                WHERE content_type = 'video'
                """                await conn.execute(text(video_content_sql))
                
                logger.info("Successfully created multimedia-specific indexes")
                
        except Exception as e:
            logger.error(f"Failed to create multimedia-specific indexes: {e}")


class AIProcessingIndexOptimizer:
    """Specialized index optimizer for AI processing operations"""    
    def __init__(self, base_optimizer: IndexOptimizer):
        self.base_optimizer = base_optimizer
    
    async def optimize_ai_processing_indexes(self, engine: AsyncEngine) -> List[str]:
        """Create optimized indexes for AI processing operations"""        created_indexes = []
        
        try:
            async with engine.begin() as conn:
                # Create indexes for ML model tracking
                model_tracking_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ml_models_version_status
                ON ml_models (model_version, status, created_at)
                """                await conn.execute(text(model_tracking_sql))
                created_indexes.append("ml_models.model_version_status")
                
                # Create indexes for inference logging
                inference_log_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inference_logs_model_timestamp
                ON inference_logs (model_id, timestamp DESC)
                """                await conn.execute(text(inference_log_sql))
                created_indexes.append("inference_logs.model_timestamp")
                
                # Create indexes for feature store
                features_sql = """                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_feature_store_entity_timestamp
                ON feature_store (entity_id, feature_timestamp DESC)
                """                await conn.execute(text(features_sql))
                created_indexes.append("feature_store.entity_timestamp")
                
                logger.info("Successfully created AI processing indexes")
                
        except Exception as e:
            logger.error(f"Failed to create AI processing indexes: {e}")
        
        return created_indexes
