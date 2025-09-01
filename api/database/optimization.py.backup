"""Database Optimization and Performance Tuning - IA Influencer Agent Platform
Advanced database optimization, indexing strategies, and performance analysis

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""
import asyncio
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Set, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import logging
import re
from collections import defaultdict, Counter

from sqlalchemy import text, inspect, MetaData, Table, Column, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from sqlalchemy.engine import Engine
import psutil

from ..core.config import get_settings
from ..core.logging import get_logger
from .connection import DatabaseConnection, SessionManager
from .monitoring import get_database_monitor

logger = get_logger(__name__)
settings = get_settings()


class OptimizationType(Enum):
    """Database optimization type enumeration"""
    INDEX_CREATION = "index_creation"
    INDEX_REMOVAL = "index_removal"
    QUERY_REWRITE = "query_rewrite"
    PARTITION_SUGGESTION = "partition_suggestion"
    DENORMALIZATION = "denormalization"
    NORMALIZATION = "normalization"
    ARCHIVE_SUGGESTION = "archive_suggestion"
    VACUUM_ANALYZE = "vacuum_analyze"
    CONSTRAINT_OPTIMIZATION = "constraint_optimization"


class IndexType(Enum):
    """Database index type enumeration"""
    BTREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"
    PARTIAL = "partial"
    UNIQUE = "unique"
    COMPOSITE = "composite"
    EXPRESSION = "expression"


class QueryComplexity(Enum):
    """Query complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class QueryProfile:
    """Query execution profile"""
    query_hash: str
    query_text: str
    execution_count: int
    total_execution_time_ms: float
    avg_execution_time_ms: float
    min_execution_time_ms: float
    max_execution_time_ms: float
    last_executed: datetime
    tables_accessed: List[str]
    complexity: QueryComplexity
    optimization_opportunities: List[str] = field(default_factory=list)
    
    @property
    def performance_score(self) -> float:
        """Calculate performance score (0-100, higher is better)"""
        # Base score on execution time (lower is better)
        if self.avg_execution_time_ms < 10:
            return 100.0
        elif self.avg_execution_time_ms < 50:
            return 90.0
        elif self.avg_execution_time_ms < 100:
            return 80.0
        elif self.avg_execution_time_ms < 500:
            return 60.0
        elif self.avg_execution_time_ms < 1000:
            return 40.0
        elif self.avg_execution_time_ms < 5000:
            return 20.0
        else:
            return 10.0


@dataclass
class IndexRecommendation:
    """Index creation recommendation"""
    table_name: str
    columns: List[str]
    index_type: IndexType
    estimated_benefit: float  # 0-100 score
    creation_cost: float      # 0-100 score
    maintenance_cost: float   # 0-100 score
    size_estimate_mb: float
    affected_queries: List[str]
    reason: str
    priority: str  # high, medium, low
    
    @property
    def recommendation_score(self) -> float:
        """Calculate overall recommendation score"""
        # Benefit vs cost analysis
        benefit_weight = 0.6
        cost_weight = 0.4
        
        total_cost = (self.creation_cost + self.maintenance_cost) / 2
        return (self.estimated_benefit * benefit_weight) - (total_cost * cost_weight)


@dataclass
class OptimizationRecommendation:
    """Database optimization recommendation"""
    optimization_type: OptimizationType
    priority: str
    title: str
    description: str
    impact_estimate: str  # high, medium, low
    effort_estimate: str  # high, medium, low
    sql_commands: List[str] = field(default_factory=list)
    affected_tables: List[str] = field(default_factory=list)
    estimated_improvement_pct: float = 0.0
    risk_level: str = "low"  # low, medium, high
    prerequisites: List[str] = field(default_factory=list)


class QueryAnalyzer:
    """Advanced query analysis and optimization recommendations"""
    
    def __init__(self):
        self.query_profiles: Dict[str, QueryProfile] = {}
        self.session_manager = SessionManager()
        self.db_connection: Optional[DatabaseConnection] = None
    
    async def initialize(self):
        """Initialize query analyzer"""
        self.db_connection = await DatabaseConnection.get_instance()
        logger.info("Query analyzer initialized")
    
    async def analyze_query(self, query: str, execution_time_ms: float = None) -> QueryProfile:
        """Analyze a single query"""
        query_hash = self._generate_query_hash(query)
        normalized_query = self._normalize_query(query)
        
        # Get or create profile
        if query_hash in self.query_profiles:
            profile = self.query_profiles[query_hash]
            profile.execution_count += 1
            
            if execution_time_ms:
                profile.total_execution_time_ms += execution_time_ms
                profile.avg_execution_time_ms = profile.total_execution_time_ms / profile.execution_count
                profile.min_execution_time_ms = min(profile.min_execution_time_ms, execution_time_ms)
                profile.max_execution_time_ms = max(profile.max_execution_time_ms, execution_time_ms)
            
            profile.last_executed = datetime.utcnow()
        else:
            profile = QueryProfile(
                query_hash=query_hash,
                query_text=normalized_query,
                execution_count=1,
                total_execution_time_ms=execution_time_ms or 0.0,
                avg_execution_time_ms=execution_time_ms or 0.0,
                min_execution_time_ms=execution_time_ms or 0.0,
                max_execution_time_ms=execution_time_ms or 0.0,
                last_executed=datetime.utcnow(),
                tables_accessed=self._extract_tables_from_query(query),
                complexity=self._assess_query_complexity(query)
            )
            
            self.query_profiles[query_hash] = profile
        
        # Analyze optimization opportunities
        profile.optimization_opportunities = await self._identify_optimization_opportunities(profile)
        
        return profile
    
    def _generate_query_hash(self, query: str) -> str:
        """Generate hash for query normalization"""
        import hashlib
        normalized = self._normalize_query(query)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for pattern matching"""
        # Remove extra whitespace and standardize
        normalized = re.sub(r'\s+', ' ', query.strip().lower())
        
        # Replace parameter placeholders
        normalized = re.sub(r'\$\d+|\?|:\w+', '?', normalized)
        
        # Replace string literals
        normalized = re.sub(r"'[^']*'", "'?'", normalized)
        
        # Replace numeric literals
        normalized = re.sub(r'\b\d+\b', '?', normalized)
        
        return normalized
    
    def _extract_tables_from_query(self, query: str) -> List[str]:
        """Extract table names from query"""
        tables = []
        query_lower = query.lower()
        
        # Common table extraction patterns
        patterns = [
            r'from\s+([a-zA-Z_]\w*)',
            r'join\s+([a-zA-Z_]\w*)',
            r'into\s+([a-zA-Z_]\w*)',
            r'update\s+([a-zA-Z_]\w*)',
            r'delete\s+from\s+([a-zA-Z_]\w*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query_lower)
            tables.extend(matches)
        
        return list(set(tables))  # Remove duplicates
    
    def _assess_query_complexity(self, query: str) -> QueryComplexity:
        """Assess query complexity based on various factors"""
        query_lower = query.lower()
        complexity_score = 0
        
        # Count joins
        join_count = len(re.findall(r'\bjoin\b', query_lower))
        complexity_score += join_count * 2
        
        # Count subqueries
        subquery_count = len(re.findall(r'\bselect\b', query_lower)) - 1
        complexity_score += subquery_count * 3
        
        # Count aggregation functions
        agg_functions = ['sum', 'count', 'avg', 'min', 'max', 'group_concat']
        agg_count = sum(query_lower.count(func) for func in agg_functions)
        complexity_score += agg_count
        
        # Count window functions
        window_count = len(re.findall(r'\bover\s*\(', query_lower))
        complexity_score += window_count * 2
        
        # Count CTEs
        cte_count = len(re.findall(r'\bwith\b', query_lower))
        complexity_score += cte_count * 2
        
        # Determine complexity level
        if complexity_score <= 2:
            return QueryComplexity.SIMPLE
        elif complexity_score <= 6:
            return QueryComplexity.MODERATE
        elif complexity_score <= 12:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.VERY_COMPLEX
    
    async def _identify_optimization_opportunities(self, profile: QueryProfile) -> List[str]:
        """Identify optimization opportunities for a query"""
        opportunities = []
        
        # Slow query optimization
        if profile.avg_execution_time_ms > 1000:
            opportunities.append("Query execution time is slow - consider indexing")
        
        # Missing WHERE clause
        if 'where' not in profile.query_text and 'select' in profile.query_text:
            opportunities.append("Query lacks WHERE clause - may scan entire table")
        
        # SELECT * usage
        if 'select *' in profile.query_text:
            opportunities.append("Using SELECT * - specify only needed columns")
        
        # Implicit joins
        if ',' in profile.query_text and 'join' not in profile.query_text:
            opportunities.append("Using implicit joins - consider explicit JOINs")
        
        # OR conditions in WHERE
        if ' or ' in profile.query_text:
            opportunities.append("OR conditions may benefit from UNION or separate queries")
        
        # LIKE with leading wildcard
        if re.search(r"like\s+'%", profile.query_text):
            opportunities.append("LIKE with leading wildcard cannot use indexes")
        
        # Functions in WHERE clause
        if re.search(r'where.*\w+\s*\(', profile.query_text):
            opportunities.append("Functions in WHERE clause prevent index usage")
        
        return opportunities
    
    async def get_slowest_queries(self, limit: int = 10) -> List[QueryProfile]:
        """Get slowest queries by average execution time"""
        profiles = list(self.query_profiles.values())
        profiles.sort(key=lambda p: p.avg_execution_time_ms, reverse=True)
        return profiles[:limit]
    
    async def get_most_frequent_queries(self, limit: int = 10) -> List[QueryProfile]:
        """Get most frequently executed queries"""
        profiles = list(self.query_profiles.values())
        profiles.sort(key=lambda p: p.execution_count, reverse=True)
        return profiles[:limit]
    
    async def get_query_statistics(self) -> Dict[str, Any]:
        """Get query analysis statistics"""
        if not self.query_profiles:
            return {}
        
        profiles = list(self.query_profiles.values())
        execution_times = [p.avg_execution_time_ms for p in profiles]
        
        return {
            'total_unique_queries': len(profiles),
            'total_executions': sum(p.execution_count for p in profiles),
            'avg_execution_time_ms': statistics.mean(execution_times),
            'median_execution_time_ms': statistics.median(execution_times),
            'slowest_query_ms': max(execution_times) if execution_times else 0,
            'fastest_query_ms': min(execution_times) if execution_times else 0,
            'queries_needing_optimization': len([p for p in profiles if p.optimization_opportunities]),
            'complexity_distribution': {
                complexity.value: len([p for p in profiles if p.complexity == complexity])
                for complexity in QueryComplexity
            }
        }


class IndexOptimizer:
    """Advanced index optimization and recommendations"""
    
    def __init__(self, query_analyzer: QueryAnalyzer):
        self.query_analyzer = query_analyzer
        self.session_manager = SessionManager()
        self.existing_indexes: Dict[str, List[Dict[str, Any]]] = {}
    
    async def initialize(self):
        """Initialize index optimizer"""
        await self._load_existing_indexes()
        logger.info("Index optimizer initialized")
    
    async def _load_existing_indexes(self):
        """Load existing database indexes"""
        try:
            async with self.session_manager.get_async_session() as session:
                # Query PostgreSQL system catalogs for indexes
                query = text("""
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        indexdef,
                        CASE WHEN indisunique THEN 'unique' 
                             WHEN indisprimary THEN 'primary'
                             ELSE 'regular' END as index_type,
                        pg_size_pretty(pg_relation_size(indexrelid)) as size
                    FROM pg_indexes pi
                    JOIN pg_index i ON i.indexrelid = (schemaname||'.'||indexname)::regclass
                    WHERE schemaname = 'public'
                    ORDER BY tablename, indexname
                """)
                
                result = await session.execute(query)
                rows = result.fetchall()
                
                for row in rows:
                    table_name = row.tablename
                    if table_name not in self.existing_indexes:
                        self.existing_indexes[table_name] = []
                    
                    self.existing_indexes[table_name].append({
                        'name': row.indexname,
                        'definition': row.indexdef,
                        'type': row.index_type,
                        'size': row.size
                    })
                
                logger.info(f"Loaded indexes for {len(self.existing_indexes)} tables")
                
        except Exception as e:
            logger.error(f"Failed to load existing indexes: {e}")
    
    async def analyze_index_usage(self) -> Dict[str, Any]:
        """Analyze index usage statistics"""
        try:
            async with self.session_manager.get_async_session() as session:
                # Get index usage statistics from PostgreSQL
                query = text("""
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch,
                        pg_size_pretty(pg_relation_size(indexrelid)) as size,
                        CASE 
                            WHEN idx_scan = 0 THEN 'unused'
                            WHEN idx_scan < 100 THEN 'rarely_used'
                            WHEN idx_scan < 1000 THEN 'moderately_used'
                            ELSE 'frequently_used'
                        END as usage_category
                    FROM pg_stat_user_indexes 
                    WHERE schemaname = 'public'
                    ORDER BY idx_scan DESC
                """)
                
                result = await session.execute(query)
                rows = result.fetchall()
                
                usage_stats = {
                    'total_indexes': len(rows),
                    'unused_indexes': len([r for r in rows if r.usage_category == 'unused']),
                    'rarely_used_indexes': len([r for r in rows if r.usage_category == 'rarely_used']),
                    'moderately_used_indexes': len([r for r in rows if r.usage_category == 'moderately_used']),
                    'frequently_used_indexes': len([r for r in rows if r.usage_category == 'frequently_used']),
                    'indexes_by_table': {},
                    'unused_index_details': []
                }
                
                for row in rows:
                    table_name = row.tablename
                    
                    if table_name not in usage_stats['indexes_by_table']:
                        usage_stats['indexes_by_table'][table_name] = {
                            'total': 0,
                            'unused': 0,
                            'scans': 0
                        }
                    
                    usage_stats['indexes_by_table'][table_name]['total'] += 1
                    usage_stats['indexes_by_table'][table_name]['scans'] += row.idx_scan
                    
                    if row.usage_category == 'unused':
                        usage_stats['indexes_by_table'][table_name]['unused'] += 1
                        usage_stats['unused_index_details'].append({
                            'table': table_name,
                            'index': row.indexname,
                            'size': row.size,
                            'scans': row.idx_scan
                        })
                
                return usage_stats
                
        except Exception as e:
            logger.error(f"Failed to analyze index usage: {e}")
            return {}
    
    async def generate_index_recommendations(self) -> List[IndexRecommendation]:
        """Generate index creation recommendations"""
        recommendations = []
        
        # Analyze slow queries for index opportunities
        slow_queries = await self.query_analyzer.get_slowest_queries(20)
        
        for profile in slow_queries:
            if profile.avg_execution_time_ms > 100:  # Only consider queries > 100ms
                query_recommendations = await self._analyze_query_for_indexes(profile)
                recommendations.extend(query_recommendations)
        
        # Remove duplicates and prioritize
        unique_recommendations = self._deduplicate_recommendations(recommendations)
        
        # Sort by recommendation score
        unique_recommendations.sort(key=lambda r: r.recommendation_score, reverse=True)
        
        return unique_recommendations
    
    async def _analyze_query_for_indexes(self, profile: QueryProfile) -> List[IndexRecommendation]:
        """Analyze a query for potential index improvements"""
        recommendations = []
        
        # Extract WHERE clause conditions
        where_conditions = self._extract_where_conditions(profile.query_text)
        
        for table_name in profile.tables_accessed:
            table_conditions = [c for c in where_conditions if c['table'] == table_name]
            
            if not table_conditions:
                continue
            
            # Single column indexes
            for condition in table_conditions:
                if condition['column'] and not self._has_suitable_index(table_name, [condition['column']]):
                    rec = IndexRecommendation(
                        table_name=table_name,
                        columns=[condition['column']],
                        index_type=IndexType.BTREE,
                        estimated_benefit=self._estimate_index_benefit(profile, [condition['column']]),
                        creation_cost=30.0,
                        maintenance_cost=20.0,
                        size_estimate_mb=self._estimate_index_size(table_name, [condition['column']]),
                        affected_queries=[profile.query_hash],
                        reason=f"WHERE condition on {condition['column']}",
                        priority="medium"
                    )
                    recommendations.append(rec)
            
            # Composite indexes for multiple conditions
            if len(table_conditions) > 1:
                columns = [c['column'] for c in table_conditions if c['column']]
                if len(columns) > 1 and not self._has_suitable_index(table_name, columns):
                    rec = IndexRecommendation(
                        table_name=table_name,
                        columns=columns,
                        index_type=IndexType.COMPOSITE,
                        estimated_benefit=self._estimate_index_benefit(profile, columns),
                        creation_cost=50.0,
                        maintenance_cost=35.0,
                        size_estimate_mb=self._estimate_index_size(table_name, columns),
                        affected_queries=[profile.query_hash],
                        reason=f"Multiple WHERE conditions on {', '.join(columns)}",
                        priority="high" if profile.avg_execution_time_ms > 1000 else "medium"
                    )
                    recommendations.append(rec)
        
        # Analyze ORDER BY clauses
        order_by_columns = self._extract_order_by_columns(profile.query_text)
        for table_name, columns in order_by_columns.items():
            if not self._has_suitable_index(table_name, columns):
                rec = IndexRecommendation(
                    table_name=table_name,
                    columns=columns,
                    index_type=IndexType.BTREE,
                    estimated_benefit=40.0,  # ORDER BY benefits from indexes
                    creation_cost=35.0,
                    maintenance_cost=25.0,
                    size_estimate_mb=self._estimate_index_size(table_name, columns),
                    affected_queries=[profile.query_hash],
                    reason=f"ORDER BY clause on {', '.join(columns)}",
                    priority="medium"
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _extract_where_conditions(self, query: str) -> List[Dict[str, Any]]:
        """Extract WHERE clause conditions from query"""
        conditions = []
        
        # Simple pattern matching for WHERE conditions
        # In production, use a proper SQL parser
        where_match = re.search(r'where\s+(.+?)(?:group\s+by|order\s+by|limit|$)', query, re.IGNORECASE)
        
        if where_match:
            where_clause = where_match.group(1)
            
            # Extract column conditions (simplified)
            condition_patterns = [
                r'(\w+)\.(\w+)\s*[=<>!]+',
                r'(\w+)\s*[=<>!]+',
            ]
            
            for pattern in condition_patterns:
                matches = re.findall(pattern, where_clause)
                for match in matches:
                    if isinstance(match, tuple) and len(match) == 2:
                        conditions.append({
                            'table': match[0],
                            'column': match[1],
                            'operator': '='  # Simplified
                        })
                    else:
                        conditions.append({
                            'table': None,
                            'column': match,
                            'operator': '='  # Simplified
                        })
        
        return conditions
    
    def _extract_order_by_columns(self, query: str) -> Dict[str, List[str]]:
        """Extract ORDER BY columns from query"""
        order_by_columns = {}
        
        order_match = re.search(r'order\s+by\s+(.+?)(?:limit|$)', query, re.IGNORECASE)
        
        if order_match:
            order_clause = order_match.group(1)
            
            # Extract column names
            column_pattern = r'(\w+)\.(\w+)|(\w+)'
            matches = re.findall(column_pattern, order_clause)
            
            for match in matches:
                if match[0] and match[1]:  # table.column format
                    table_name = match[0]
                    column_name = match[1]
                    
                    if table_name not in order_by_columns:
                        order_by_columns[table_name] = []
                    order_by_columns[table_name].append(column_name)
                elif match[2]:  # column only
                    # Would need to infer table from context
                    pass
        
        return order_by_columns
    
    def _has_suitable_index(self, table_name: str, columns: List[str]) -> bool:
        """Check if a suitable index already exists"""
        if table_name not in self.existing_indexes:
            return False
        
        for index in self.existing_indexes[table_name]:
            # Simple check - in production, parse index definition properly
            index_def = index['definition'].lower()
            
            # Check if all columns are covered
            if all(col.lower() in index_def for col in columns):
                return True
        
        return False
    
    def _estimate_index_benefit(self, profile: QueryProfile, columns: List[str]) -> float:
        """Estimate benefit of creating an index"""
        base_benefit = 60.0
        
        # Higher benefit for slower queries
        if profile.avg_execution_time_ms > 1000:
            base_benefit += 20.0
        elif profile.avg_execution_time_ms > 500:
            base_benefit += 10.0
        
        # Higher benefit for frequently executed queries
        if profile.execution_count > 1000:
            base_benefit += 15.0
        elif profile.execution_count > 100:
            base_benefit += 10.0
        
        # Adjust for number of columns (composite indexes are more complex)
        if len(columns) > 2:
            base_benefit -= 10.0
        
        return min(base_benefit, 100.0)
    
    def _estimate_index_size(self, table_name: str, columns: List[str]) -> float:
        """Estimate index size in MB"""
        # Simplified estimation - would need actual table statistics
        base_size = 10.0  # Base size in MB
        
        # Estimate based on number of columns
        column_factor = len(columns) * 5.0
        
        # Rough estimate
        return base_size + column_factor
    
    def _deduplicate_recommendations(self, recommendations: List[IndexRecommendation]) -> List[IndexRecommendation]:
        """Remove duplicate index recommendations"""
        seen = set()
        unique_recommendations = []
        
        for rec in recommendations:
            key = (rec.table_name, tuple(sorted(rec.columns)))
            
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)
            else:
                # Merge with existing recommendation
                existing = next(r for r in unique_recommendations 
                              if (r.table_name, tuple(sorted(r.columns))) == key)
                existing.affected_queries.extend(rec.affected_queries)
                existing.estimated_benefit = max(existing.estimated_benefit, rec.estimated_benefit)
        
        return unique_recommendations
    
    async def get_unused_indexes(self) -> List[Dict[str, Any]]:
        """Get list of unused indexes that could be removed"""
        usage_stats = await self.analyze_index_usage()
        return usage_stats.get('unused_index_details', [])


class DatabaseOptimizer:
    """Main database optimization orchestrator"""
    
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.index_optimizer = IndexOptimizer(self.query_analyzer)
        self.session_manager = SessionManager()
        self.db_monitor = None
    
    async def initialize(self):
        """Initialize database optimizer"""
        await self.query_analyzer.initialize()
        await self.index_optimizer.initialize()
        self.db_monitor = await get_database_monitor()
        
        logger.info("Database optimizer initialized")
    
    async def perform_comprehensive_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive database optimization analysis"""
        logger.info("Starting comprehensive database optimization analysis")
        
        analysis_results = {
            'timestamp': datetime.utcnow(),
            'query_analysis': await self.query_analyzer.get_query_statistics(),
            'index_analysis': await self.index_optimizer.analyze_index_usage(),
            'recommendations': await self.generate_optimization_recommendations(),
            'performance_metrics': await self._collect_performance_metrics(),
            'table_statistics': await self._collect_table_statistics()
        }
        
        logger.info("Comprehensive database analysis completed")
        return analysis_results
    
    async def generate_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate comprehensive optimization recommendations"""
        recommendations = []
        
        # Index recommendations
        index_recommendations = await self.index_optimizer.generate_index_recommendations()
        for index_rec in index_recommendations[:5]:  # Top 5 index recommendations
            rec = OptimizationRecommendation(
                optimization_type=OptimizationType.INDEX_CREATION,
                priority=index_rec.priority,
                title=f"Create index on {index_rec.table_name}({', '.join(index_rec.columns)})",
                description=index_rec.reason,
                impact_estimate="high" if index_rec.estimated_benefit > 70 else "medium",
                effort_estimate="low" if len(index_rec.columns) == 1 else "medium",
                sql_commands=[self._generate_index_creation_sql(index_rec)],
                affected_tables=[index_rec.table_name],
                estimated_improvement_pct=index_rec.estimated_benefit
            )
            recommendations.append(rec)
        
        # Unused index removal recommendations
        unused_indexes = await self.index_optimizer.get_unused_indexes()
        for unused in unused_indexes[:3]:  # Top 3 unused indexes
            rec = OptimizationRecommendation(
                optimization_type=OptimizationType.INDEX_REMOVAL,
                priority="medium",
                title=f"Remove unused index {unused['index']}",
                description=f"Index {unused['index']} on table {unused['table']} is unused",
                impact_estimate="medium",
                effort_estimate="low",
                sql_commands=[f"DROP INDEX {unused['index']};"],
                affected_tables=[unused['table']],
                risk_level="low"
            )
            recommendations.append(rec)
        
        # Slow query optimization
        slow_queries = await self.query_analyzer.get_slowest_queries(5)
        for query in slow_queries:
            if query.avg_execution_time_ms > 1000:
                rec = OptimizationRecommendation(
                    optimization_type=OptimizationType.QUERY_REWRITE,
                    priority="high",
                    title=f"Optimize slow query (avg: {query.avg_execution_time_ms:.1f}ms)",
                    description=f"Query executed {query.execution_count} times with high average execution time",
                    impact_estimate="high",
                    effort_estimate="medium",
                    affected_tables=query.tables_accessed,
                    estimated_improvement_pct=50.0,
                    prerequisites=["Query analysis", "Execution plan review"]
                )
                recommendations.append(rec)
        
        # VACUUM and ANALYZE recommendations
        table_stats = await self._collect_table_statistics()
        for table_stat in table_stats:
            if table_stat.get('dead_tuple_ratio', 0) > 0.1:  # More than 10% dead tuples
                rec = OptimizationRecommendation(
                    optimization_type=OptimizationType.VACUUM_ANALYZE,
                    priority="medium",
                    title=f"VACUUM ANALYZE {table_stat['table_name']}",
                    description=f"Table has {table_stat['dead_tuple_ratio']:.1%} dead tuples",
                    impact_estimate="medium",
                    effort_estimate="low",
                    sql_commands=[f"VACUUM ANALYZE {table_stat['table_name']};"],
                    affected_tables=[table_stat['table_name']],
                    risk_level="low"
                )
                recommendations.append(rec)
        
        # Sort recommendations by priority and impact
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda r: (
            priority_order.get(r.priority, 0),
            r.estimated_improvement_pct
        ), reverse=True)
        
        return recommendations
    
    def _generate_index_creation_sql(self, index_rec: IndexRecommendation) -> str:
        """Generate SQL for index creation"""
        index_name = f"idx_{index_rec.table_name}_{'_'.join(index_rec.columns)}"
        columns_str = ', '.join(index_rec.columns)
        
        if index_rec.index_type == IndexType.UNIQUE:
            return f"CREATE UNIQUE INDEX {index_name} ON {index_rec.table_name} ({columns_str});"
        elif index_rec.index_type == IndexType.PARTIAL:
            return f"CREATE INDEX {index_name} ON {index_rec.table_name} ({columns_str}) WHERE /* condition */;"
        else:
            return f"CREATE INDEX {index_name} ON {index_rec.table_name} ({columns_str});"
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics"""
        try:
            if self.db_monitor:
                metrics = await self.db_monitor.get_current_metrics()
                return metrics or {}
            return {}
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")
            return {}
    
    async def _collect_table_statistics(self) -> List[Dict[str, Any]]:
        """Collect table-level statistics"""
        try:
            async with self.session_manager.get_async_session() as session:
                query = text("""
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_tuples,
                        n_dead_tup as dead_tuples,
                        CASE 
                            WHEN n_live_tup + n_dead_tup > 0 
                            THEN n_dead_tup::float / (n_live_tup + n_dead_tup)
                            ELSE 0
                        END as dead_tuple_ratio,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                    FROM pg_stat_user_tables 
                    WHERE schemaname = 'public'
                    ORDER BY n_live_tup DESC
                """)
                
                result = await session.execute(query)
                rows = result.fetchall()
                
                return [
                    {
                        'table_name': row.tablename,
                        'live_tuples': row.live_tuples,
                        'dead_tuples': row.dead_tuples,
                        'dead_tuple_ratio': float(row.dead_tuple_ratio),
                        'total_operations': row.inserts + row.updates + row.deletes,
                        'last_vacuum': row.last_vacuum,
                        'last_analyze': row.last_analyze,
                        'size': row.size
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"Failed to collect table statistics: {e}")
            return []
    
    async def execute_optimization_recommendation(self, 
                                                recommendation: OptimizationRecommendation,
                                                dry_run: bool = True) -> Dict[str, Any]:
        """Execute an optimization recommendation"""
        result = {
            'recommendation_id': recommendation.title,
            'success': False,
            'dry_run': dry_run,
            'executed_commands': [],
            'errors': []
        }
        
        if dry_run:
            logger.info(f"DRY RUN: Would execute optimization - {recommendation.title}")
            result['success'] = True
            result['executed_commands'] = recommendation.sql_commands
            return result
        
        try:
            async with self.session_manager.get_async_session() as session:
                for sql_command in recommendation.sql_commands:
                    logger.info(f"Executing optimization SQL: {sql_command}")
                    
                    await session.execute(text(sql_command))
                    result['executed_commands'].append(sql_command)
                
                await session.commit()
                result['success'] = True
                
                logger.info(f"Successfully executed optimization: {recommendation.title}")
                
        except Exception as e:
            logger.error(f"Failed to execute optimization {recommendation.title}: {e}")
            result['errors'].append(str(e))
            
            # Rollback transaction
            try:
                async with self.session_manager.get_async_session() as session:
                    await session.rollback()
            except:
                pass
        
        return result
    
    async def schedule_maintenance_tasks(self) -> List[Dict[str, Any]]:
        """Schedule routine maintenance tasks"""
        maintenance_tasks = []
        
        # Get table statistics
        table_stats = await self._collect_table_statistics()
        
        for table_stat in table_stats:
            # Schedule VACUUM for tables with high dead tuple ratio
            if table_stat['dead_tuple_ratio'] > 0.1:
                maintenance_tasks.append({
                    'task': 'vacuum',
                    'table': table_stat['table_name'],
                    'priority': 'high' if table_stat['dead_tuple_ratio'] > 0.2 else 'medium',
                    'command': f"VACUUM ANALYZE {table_stat['table_name']};",
                    'reason': f"Dead tuple ratio: {table_stat['dead_tuple_ratio']:.1%}"
                })
            
            # Schedule ANALYZE for tables without recent statistics
            if table_stat['last_analyze'] is None:
                maintenance_tasks.append({
                    'task': 'analyze',
                    'table': table_stat['table_name'],
                    'priority': 'medium',
                    'command': f"ANALYZE {table_stat['table_name']};",
                    'reason': "No recent statistics available"
                })
        
        return maintenance_tasks


# Global optimizer instance
_optimizer_instance: Optional[DatabaseOptimizer] = None


async def get_database_optimizer() -> DatabaseOptimizer:
    """Get global database optimizer instance"""
    global _optimizer_instance
    
    if _optimizer_instance is None:
        _optimizer_instance = DatabaseOptimizer()
        await _optimizer_instance.initialize()
    
    return _optimizer_instance


# Convenience functions
async def analyze_query_performance(query: str, execution_time_ms: float = None) -> QueryProfile:
    """Analyze query performance"""
    optimizer = await get_database_optimizer()
    return await optimizer.query_analyzer.analyze_query(query, execution_time_ms)


async def get_optimization_recommendations() -> List[OptimizationRecommendation]:
    """Get database optimization recommendations"""
    optimizer = await get_database_optimizer()
    return await optimizer.generate_optimization_recommendations()


async def get_index_recommendations() -> List[IndexRecommendation]:
    """Get index creation recommendations"""
    optimizer = await get_database_optimizer()
    return await optimizer.index_optimizer.generate_index_recommendations()
