"""
Slow Query Detector

Advanced slow query detection and analysis system with intelligent pattern recognition,
automated optimization suggestions, and performance impact assessment.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

  AVERTISSEMENT STRICT 
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Propriété intellectuelle de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from collections import defaultdict, deque
import json
import statistics
import sqlparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_database_session
from ..models.monitoring import SlowQuery, QueryPattern, OptimizationSuggestion
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...ai.analysis.query_optimization_ai import QueryOptimizationAI


class QueryImpact(Enum):
    """Query performance impact levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QueryCategory(Enum):
    """Query categorization for analysis"""
    OLTP = "oltp"          # Online Transaction Processing
    OLAP = "olap"          # Online Analytical Processing
    BATCH = "batch"        # Batch processing
    MAINTENANCE = "maintenance"  # Database maintenance
    MONITORING = "monitoring"    # Monitoring queries
    UNKNOWN = "unknown"


@dataclass
class SlowQueryInstance:
    """Individual slow query execution instance"""
    query_id: str
    normalized_query: str
    original_query: str
    execution_time_ms: float
    rows_examined: int
    rows_returned: int
    query_start: datetime
    query_end: datetime
    database_name: str
    username: str
    application_name: str
    client_addr: str
    wait_events: List[str]
    lock_time_ms: float
    io_time_ms: float
    cpu_time_ms: float
    memory_usage_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['query_start'] = self.query_start.isoformat()
        data['query_end'] = self.query_end.isoformat()
        return data


@dataclass
class SlowQueryPattern:
    """Aggregated slow query pattern analysis"""
    pattern_id: str
    normalized_query: str
    query_category: QueryCategory
    impact_level: QueryImpact
    execution_count: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    avg_rows_examined: float
    avg_rows_returned: float
    first_seen: datetime
    last_seen: datetime
    affected_tables: List[str]
    common_wait_events: List[str]
    performance_trend: str  # improving, degrading, stable
    optimization_priority: int  # 1-10 scale
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['query_category'] = self.query_category.value
        data['impact_level'] = self.impact_level.value
        data['first_seen'] = self.first_seen.isoformat()
        data['last_seen'] = self.last_seen.isoformat()
        return data


@dataclass
class OptimizationSuggestion:
    """Query optimization suggestion"""
    suggestion_id: str
    query_pattern_id: str
    suggestion_type: str
    title: str
    description: str
    implementation_steps: List[str]
    estimated_improvement_percent: float
    implementation_effort: str  # low, medium, high
    confidence_score: float
    sql_example: Optional[str]
    index_suggestions: List[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


class SlowQueryDetector:
    """
    Advanced slow query detection and analysis system.
    
    Features:
    - Real-time slow query capture
    - Intelligent query pattern recognition
    - Performance impact assessment
    - Automated optimization suggestions
    - Trend analysis and alerting
    - Query categorization and prioritization
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.ai_optimizer = QueryOptimizationAI()
        
        # Detection configuration
        self.slow_query_threshold_ms = getattr(settings, 'slow_query_threshold_ms', 1000)
        self.analysis_window_hours = 24
        self.max_query_length = 10000
        
        # Data storage
        self.slow_queries: deque = deque(maxlen=10000)
        self.query_patterns: Dict[str, SlowQueryPattern] = {}
        self.optimization_suggestions: Dict[str, List[OptimizationSuggestion]] = defaultdict(list)
        
        # Detection state
        self.detecting_active = False
        self.last_analysis_time = datetime.utcnow()
        
        # Query normalization patterns
        self.normalization_patterns = [
            (r'\b\d+\b', 'N'),                    # Numbers
            (r"'[^']*'", "'VALUE'"),             # String literals
            (r'\$\d+', '$N'),                    # Parameter placeholders
            (r'\s+', ' '),                       # Multiple spaces
            (r'IN\s*\([^)]+\)', 'IN (VALUES)'),  # IN clauses
        ]
        
        self.logger.info("Slow Query Detector initialized")
    
    async def start_detection(self, check_interval: int = 30) -> None:
        """Start slow query detection"""
        if self.detecting_active:
            self.logger.warning("Slow query detection already active")
            return
        
        self.detecting_active = True
        self.logger.info(f"Starting slow query detection with {check_interval}s interval")
        
        try:
            # Start detection tasks
            await asyncio.gather(
                self._detect_slow_queries_loop(check_interval),
                self._analyze_patterns_loop(300),  # Analyze patterns every 5 minutes
                self._generate_suggestions_loop(900),  # Generate suggestions every 15 minutes
                return_exceptions=True
            )
        except Exception as e:
            self.logger.error(f"Slow query detection error: {e}")
            self.detecting_active = False
            raise
    
    async def stop_detection(self) -> None:
        """Stop slow query detection"""
        self.detecting_active = False
        self.logger.info("Slow query detection stopped")
    
    async def _detect_slow_queries_loop(self, interval: int) -> None:
        """Main detection loop for slow queries"""
        while self.detecting_active:
            try:
                await self._capture_slow_queries()
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in slow query detection loop: {e}")
                await asyncio.sleep(interval)
    
    async def _analyze_patterns_loop(self, interval: int) -> None:
        """Pattern analysis loop"""
        while self.detecting_active:
            try:
                await self._analyze_query_patterns()
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in pattern analysis loop: {e}")
                await asyncio.sleep(interval)
    
    async def _generate_suggestions_loop(self, interval: int) -> None:
        """Optimization suggestions generation loop"""
        while self.detecting_active:
            try:
                await self._generate_optimization_suggestions()
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in suggestions generation loop: {e}")
                await asyncio.sleep(interval)
    
    async def _capture_slow_queries(self) -> None:
        """Capture slow queries from database"""



        try:
            async with get_database_session() as session:
                # Get slow queries from pg_stat_activity
                result = await session.execute(text("""
                    SELECT 
                        pid,
                        query,
                        query_start,
                        now() as query_end,
                        EXTRACT(EPOCH FROM (now() - query_start)) * 1000 as duration_ms,
                        datname,
                        usename,
                        application_name,
                        client_addr,
                        wait_event_type,
                        wait_event,
                        state
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                    AND query_start IS NOT NULL
                    AND query NOT LIKE '%pg_stat_activity%'
                    AND query NOT LIKE '%slow_query_detector%'
                    AND EXTRACT(EPOCH FROM (now() - query_start)) * 1000 > :threshold
                    ORDER BY query_start DESC
                    LIMIT 50
                """), {"threshold": self.slow_query_threshold_ms})
                
                for row in result:
                    await self._process_slow_query_row(row)
                
                # Also capture from pg_stat_statements if available
                await self._capture_from_pg_stat_statements(session)
                
        except Exception as e:
            self.logger.error(f"Error capturing slow queries: {e}")
    
    async def _process_slow_query_row(self, row) -> None:
        """Process a single slow query row"""



        try:
            # Clean and normalize query
            original_query = row.query[:self.max_query_length] if row.query else ""
            normalized_query = self._normalize_query(original_query)
            query_id = self._generate_query_id(normalized_query)
            
            # Extract wait events
            wait_events = []
            if row.wait_event_type and row.wait_event:
                wait_events.append(f"{row.wait_event_type}:{row.wait_event}")
            
            slow_query = SlowQueryInstance(
                query_id=query_id,
                normalized_query=normalized_query,
                original_query=original_query,
                execution_time_ms=row.duration_ms,
                rows_examined=0,  # Not available from pg_stat_activity
                rows_returned=0,  # Not available from pg_stat_activity
                query_start=row.query_start,
                query_end=row.query_end,
                database_name=row.datname or "unknown",
                username=row.usename or "unknown",
                application_name=row.application_name or "unknown",
                client_addr=row.client_addr or "unknown",
                wait_events=wait_events,
                lock_time_ms=0.0,  # Not directly available
                io_time_ms=0.0,   # Not directly available
                cpu_time_ms=0.0,  # Not directly available
                memory_usage_mb=0.0  # Not directly available
            )
            
            # Store slow query
            self.slow_queries.append(slow_query)
            
            # Cache for immediate access
            await self.cache.lpush(
                "slow_queries:recent",
                json.dumps(slow_query.to_dict())
            )
            await self.cache.ltrim("slow_queries:recent", 0, 999)  # Keep last 1000
            
            self.logger.info(f"Captured slow query: {query_id} ({row.duration_ms:.1f}ms)")
            
        except Exception as e:
            self.logger.error(f"Error processing slow query row: {e}")
    
    async def _capture_from_pg_stat_statements(self, session: AsyncSession) -> None:
        """Capture slow queries from pg_stat_statements"""



        try:
            # Check if pg_stat_statements is available
            result = await session.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                )
            """))
            
            if not result.scalar():
                return
            
            # Get slow queries from pg_stat_statements
            result = await session.execute(text("""
                SELECT 
                    queryid,
                    query,
                    calls,
                    total_exec_time,
                    mean_exec_time,
                    min_exec_time,
                    max_exec_time,
                    rows,
                    shared_blks_hit,
                    shared_blks_read,
                    local_blks_hit,
                    local_blks_read,
                    temp_blks_read,
                    temp_blks_written
                FROM pg_stat_statements 
                WHERE mean_exec_time > :threshold
                AND query NOT LIKE '%pg_stat_%'
                ORDER BY mean_exec_time DESC
                LIMIT 50
            """), {"threshold": self.slow_query_threshold_ms})
            
            for row in result:
                await self._process_pg_stat_statements_row(row)
                
        except Exception as e:
            self.logger.debug(f"pg_stat_statements not available or error: {e}")
    
    async def _process_pg_stat_statements_row(self, row) -> None:
        """Process row from pg_stat_statements"""



        try:
            original_query = row.query[:self.max_query_length] if row.query else ""
            normalized_query = self._normalize_query(original_query)
            query_id = self._generate_query_id(normalized_query)
            
            # Check if we already have this pattern
            if query_id in [sq.query_id for sq in self.slow_queries]:
                return
            
            # Create slow query instance (synthetic data for aggregate stats)
            slow_query = SlowQueryInstance(
                query_id=query_id,
                normalized_query=normalized_query,
                original_query=original_query,
                execution_time_ms=row.mean_exec_time,
                rows_examined=row.shared_blks_hit + row.shared_blks_read,
                rows_returned=row.rows // row.calls if row.calls > 0 else 0,
                query_start=datetime.utcnow() - timedelta(minutes=5),  # Approximate
                query_end=datetime.utcnow(),
                database_name="unknown",
                username="unknown",
                application_name="pg_stat_statements",
                client_addr="unknown",
                wait_events=[],
                lock_time_ms=0.0,
                io_time_ms=0.0,
                cpu_time_ms=0.0,
                memory_usage_mb=0.0
            )
            
            self.slow_queries.append(slow_query)
            
        except Exception as e:
            self.logger.error(f"Error processing pg_stat_statements row: {e}")
    
    def _normalize_query(self, query: str) -> str:
        """Normalize SQL query for pattern matching"""
        if not query:
            return ""
        
        # Basic cleanup
        normalized = query.strip()
        
        # Remove comments
        normalized = re.sub(r'--.*$', '', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
        
        # Convert to uppercase for consistency
        normalized = normalized.upper()
        
        # Apply normalization patterns
        for pattern, replacement in self.normalization_patterns:
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        # Clean up whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _generate_query_id(self, normalized_query: str) -> str:
        """Generate unique ID for query pattern"""



        return hashlib.md5(normalized_query.encode()).hexdigest()[:16]
    
    async def _analyze_query_patterns(self) -> None:
        """Analyze slow query patterns and trends"""



        try:
            # Group slow queries by pattern
            pattern_groups = defaultdict(list)
            
            cutoff_time = datetime.utcnow() - timedelta(hours=self.analysis_window_hours)
            
            for slow_query in self.slow_queries:
                if slow_query.query_start >= cutoff_time:
                    pattern_groups[slow_query.query_id].append(slow_query)
            
            # Analyze each pattern
            for query_id, queries in pattern_groups.items():
                if len(queries) >= 2:  # Only analyze patterns with multiple instances
                    pattern = await self._create_query_pattern(query_id, queries)
                    if pattern:
                        self.query_patterns[query_id] = pattern
                        
                        # Cache pattern
                        await self.cache.set(
                            f"slow_pattern:{query_id}",
                            json.dumps(pattern.to_dict()),
                            expire=3600
                        )
            
            self.last_analysis_time = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Error analyzing query patterns: {e}")
    
    async def _create_query_pattern(
        self, 
        query_id: str, 
        queries: List[SlowQueryInstance]
    ) -> Optional[SlowQueryPattern]:
        """Create query pattern from slow query instances"""



        try:
            if not queries:
                return None
            
            # Calculate aggregated statistics
            execution_times = [q.execution_time_ms for q in queries]
            rows_examined = [q.rows_examined for q in queries if q.rows_examined > 0]
            rows_returned = [q.rows_returned for q in queries if q.rows_returned > 0]
            
            # Determine query category
            query_category = self._categorize_query(queries[0].normalized_query)
            
            # Calculate impact level
            impact_level = self._calculate_impact_level(queries)
            
            # Extract affected tables
            affected_tables = self._extract_table_names(queries[0].normalized_query)
            
            # Analyze wait events
            all_wait_events = []
            for q in queries:
                all_wait_events.extend(q.wait_events)
            common_wait_events = [
                event for event, count in 
                defaultdict(int, {event: all_wait_events.count(event) for event in set(all_wait_events)}).items()
                if count >= len(queries) * 0.3  # Appear in at least 30% of instances
            ]
            
            # Determine performance trend
            performance_trend = self._analyze_performance_trend(execution_times)
            
            # Calculate optimization priority
            optimization_priority = self._calculate_optimization_priority(
                len(queries), statistics.mean(execution_times), impact_level
            )
            
            pattern = SlowQueryPattern(
                pattern_id=query_id,
                normalized_query=queries[0].normalized_query,
                query_category=query_category,
                impact_level=impact_level,
                execution_count=len(queries),
                total_time_ms=sum(execution_times),
                avg_time_ms=statistics.mean(execution_times),
                min_time_ms=min(execution_times),
                max_time_ms=max(execution_times),
                avg_rows_examined=statistics.mean(rows_examined) if rows_examined else 0,
                avg_rows_returned=statistics.mean(rows_returned) if rows_returned else 0,
                first_seen=min(q.query_start for q in queries),
                last_seen=max(q.query_start for q in queries),
                affected_tables=affected_tables,
                common_wait_events=common_wait_events,
                performance_trend=performance_trend,
                optimization_priority=optimization_priority
            )
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"Error creating query pattern: {e}")
            return None
    
    def _categorize_query(self, normalized_query: str) -> QueryCategory:
        """Categorize query based on its pattern"""
        query_upper = normalized_query.upper()
        
        # OLTP patterns
        if any(pattern in query_upper for pattern in [
            'INSERT INTO', 'UPDATE', 'DELETE FROM',
            'SELECT * FROM', 'WHERE ID =', 'LIMIT 1'
        ]):
            return QueryCategory.OLTP
        
        # OLAP patterns
        elif any(pattern in query_upper for pattern in [
            'GROUP BY', 'HAVING', 'WINDOW', 'PARTITION BY',
            'SUM(', 'COUNT(', 'AVG(', 'MIN(', 'MAX('
        ]):
            return QueryCategory.OLAP
        
        # Batch patterns
        elif any(pattern in query_upper for pattern in [
            'BULK', 'BATCH', 'LOAD', 'IMPORT',
            'WITHOUT WHERE', 'TRUNCATE'
        ]):
            return QueryCategory.BATCH
        
        # Maintenance patterns
        elif any(pattern in query_upper for pattern in [
            'VACUUM', 'ANALYZE', 'REINDEX', 'CLUSTER',
            'CREATE INDEX', 'DROP INDEX'
        ]):
            return QueryCategory.MAINTENANCE
        
        # Monitoring patterns
        elif any(pattern in query_upper for pattern in [
            'PG_STAT_', 'INFORMATION_SCHEMA', 'PG_CATALOG',
            'SHOW', 'EXPLAIN'
        ]):
            return QueryCategory.MONITORING
        
        else:
            return QueryCategory.UNKNOWN
    
    def _calculate_impact_level(self, queries: List[SlowQueryInstance]) -> QueryImpact:
        """Calculate performance impact level"""
        # Consider frequency and duration
        frequency = len(queries)
        avg_duration = statistics.mean(q.execution_time_ms for q in queries)
        total_time = sum(q.execution_time_ms for q in queries)
        
        # Impact scoring
        impact_score = 0
        
        # Frequency impact
        if frequency >= 100:
            impact_score += 3
        elif frequency >= 20:
            impact_score += 2
        elif frequency >= 5:
            impact_score += 1
        
        # Duration impact
        if avg_duration >= 10000:  # 10 seconds
            impact_score += 3
        elif avg_duration >= 5000:  # 5 seconds
            impact_score += 2
        elif avg_duration >= 2000:  # 2 seconds
            impact_score += 1
        
        # Total time impact
        if total_time >= 300000:  # 5 minutes total
            impact_score += 2
        elif total_time >= 60000:  # 1 minute total
            impact_score += 1
        
        # Map score to impact level
        if impact_score >= 7:
            return QueryImpact.CRITICAL
        elif impact_score >= 5:
            return QueryImpact.HIGH
        elif impact_score >= 3:
            return QueryImpact.MEDIUM
        else:
            return QueryImpact.LOW
    
    def _extract_table_names(self, normalized_query: str) -> List[str]:
        """Extract table names from normalized query"""
        table_names = []
        
        # Simple regex patterns for table extraction
        patterns = [
            r'FROM\s+([A-Za-z_][A-Za-z0-9_]*)',
            r'JOIN\s+([A-Za-z_][A-Za-z0-9_]*)',
            r'UPDATE\s+([A-Za-z_][A-Za-z0-9_]*)',
            r'INSERT\s+INTO\s+([A-Za-z_][A-Za-z0-9_]*)',
            r'DELETE\s+FROM\s+([A-Za-z_][A-Za-z0-9_]*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, normalized_query, re.IGNORECASE)
            table_names.extend(matches)
        
        return list(set(table_names))  # Remove duplicates
    
    def _analyze_performance_trend(self, execution_times: List[float]) -> str:
        """Analyze performance trend over time"""
        if len(execution_times) < 3:
            return "stable"
        
        # Simple trend analysis using first/last quartiles
        quarter_size = len(execution_times) // 4
        if quarter_size == 0:
            return "stable"
        
        first_quarter = execution_times[:quarter_size]
        last_quarter = execution_times[-quarter_size:]
        
        first_avg = statistics.mean(first_quarter)
        last_avg = statistics.mean(last_quarter)
        
        # 20% threshold for trend detection
        if last_avg > first_avg * 1.2:
            return "degrading"
        elif last_avg < first_avg * 0.8:
            return "improving"
        else:
            return "stable"
    
    def _calculate_optimization_priority(
        self, 
        frequency: int, 
        avg_duration: float, 
        impact_level: QueryImpact
    ) -> int:
        """Calculate optimization priority (1-10 scale)"""
        priority = 1
        
        # Frequency contribution
        if frequency >= 100:
            priority += 3
        elif frequency >= 20:
            priority += 2
        elif frequency >= 5:
            priority += 1
        
        # Duration contribution
        if avg_duration >= 10000:
            priority += 3
        elif avg_duration >= 5000:
            priority += 2
        elif avg_duration >= 2000:
            priority += 1
        
        # Impact level contribution
        impact_points = {
            QueryImpact.CRITICAL: 3,
            QueryImpact.HIGH: 2,
            QueryImpact.MEDIUM: 1,
            QueryImpact.LOW: 0
        }
        priority += impact_points.get(impact_level, 0)
        
        return min(priority, 10)  # Cap at 10
    
    async def _generate_optimization_suggestions(self) -> None:
        """Generate optimization suggestions for slow query patterns"""



        try:
            for pattern_id, pattern in self.query_patterns.items():
                if pattern.optimization_priority >= 5:  # Only high-priority patterns
                    suggestions = await self._generate_pattern_suggestions(pattern)
                    if suggestions:
                        self.optimization_suggestions[pattern_id] = suggestions
                        
                        # Cache suggestions
                        await self.cache.set(
                            f"slow_suggestions:{pattern_id}",
                            json.dumps([s.to_dict() for s in suggestions]),
                            expire=3600
                        )
                        
        except Exception as e:
            self.logger.error(f"Error generating optimization suggestions: {e}")
    
    async def _generate_pattern_suggestions(
        self, 
        pattern: SlowQueryPattern
    ) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions for a specific pattern"""
        suggestions = []
        
        try:
            query = pattern.normalized_query
            
            # Index suggestions
            if "WHERE" in query and "INDEX" not in query:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"idx_{pattern.pattern_id}_{int(time.time())}",
                    query_pattern_id=pattern.pattern_id,
                    suggestion_type="indexing",
                    title="Add Missing Indexes",
                    description="Query appears to benefit from additional indexes on WHERE clause columns",
                    implementation_steps=[
                        "Analyze EXPLAIN output to identify sequential scans",
                        "Create composite indexes on frequently filtered columns",
                        "Monitor query performance after index creation"
                    ],
                    estimated_improvement_percent=50.0,
                    implementation_effort="low",
                    confidence_score=0.8,
                    sql_example=f"CREATE INDEX idx_table_columns ON table (col1, col2);",
                    index_suggestions=self._suggest_indexes(query, pattern.affected_tables),
                    created_at=datetime.utcnow()
                ))
            
            # JOIN optimization
            if pattern.query_category == QueryCategory.OLAP and "JOIN" in query:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"join_{pattern.pattern_id}_{int(time.time())}",
                    query_pattern_id=pattern.pattern_id,
                    suggestion_type="join_optimization",
                    title="Optimize JOIN Operations",
                    description="Multiple JOINs detected that may benefit from optimization",
                    implementation_steps=[
                        "Review JOIN order and conditions",
                        "Consider denormalization for frequent JOINs",
                        "Add indexes on JOIN columns"
                    ],
                    estimated_improvement_percent=30.0,
                    implementation_effort="medium",
                    confidence_score=0.7,
                    sql_example="CREATE INDEX idx_join_columns ON table (join_col);",
                    index_suggestions=[],
                    created_at=datetime.utcnow()
                ))
            
            # High frequency caching
            if pattern.execution_count >= 50:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"cache_{pattern.pattern_id}_{int(time.time())}",
                    query_pattern_id=pattern.pattern_id,
                    suggestion_type="caching",
                    title="Implement Query Result Caching",
                    description=f"Query executed {pattern.execution_count} times, consider caching results",
                    implementation_steps=[
                        "Implement application-level caching",
                        "Use Redis or Memcached for result storage",
                        "Set appropriate cache expiration times"
                    ],
                    estimated_improvement_percent=80.0,
                    implementation_effort="medium",
                    confidence_score=0.9,
                    sql_example="-- Implement in application layer",
                    index_suggestions=[],
                    created_at=datetime.utcnow()
                ))
            
            # Query rewriting suggestions
            if "SELECT *" in query:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"rewrite_{pattern.pattern_id}_{int(time.time())}",
                    query_pattern_id=pattern.pattern_id,
                    suggestion_type="query_rewriting",
                    title="Avoid SELECT * Queries",
                    description="SELECT * queries can be inefficient, specify only needed columns",
                    implementation_steps=[
                        "Identify actually needed columns",
                        "Rewrite query to select specific columns",
                        "Update application code accordingly"
                    ],
                    estimated_improvement_percent=25.0,
                    implementation_effort="low",
                    confidence_score=0.6,
                    sql_example="SELECT col1, col2, col3 FROM table WHERE ...",
                    index_suggestions=[],
                    created_at=datetime.utcnow()
                ))
            
        except Exception as e:
            self.logger.error(f"Error generating suggestions for pattern {pattern.pattern_id}: {e}")
        
        return suggestions
    
    def _suggest_indexes(self, query: str, tables: List[str]) -> List[str]:
        """Suggest specific indexes based on query analysis"""
        suggestions = []
        
        # Extract WHERE conditions
        where_match = re.search(r'WHERE\s+(.*?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+LIMIT|$)', 
                               query, re.IGNORECASE | re.DOTALL)
        
        if where_match and tables:
            where_clause = where_match.group(1)
            
            # Simple column extraction
            column_patterns = re.findall(r'(\w+)\s*[=<>!]', where_clause)
            
            if column_patterns:
                for table in tables:
                    if len(column_patterns) == 1:
                        suggestions.append(f"CREATE INDEX idx_{table}_{column_patterns[0]} ON {table} ({column_patterns[0]});")
                    elif len(column_patterns) > 1:
                        cols = ", ".join(column_patterns[:3])  # Limit to 3 columns
                        suggestions.append(f"CREATE INDEX idx_{table}_composite ON {table} ({cols});")
        
        return suggestions
    
    async def get_slow_query_summary(self) -> Dict[str, Any]:
        """Get slow query detection summary"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.analysis_window_hours)
            recent_queries = [q for q in self.slow_queries if q.query_start >= cutoff_time]
            
            summary = {
                "detection_active": self.detecting_active,
                "threshold_ms": self.slow_query_threshold_ms,
                "analysis_window_hours": self.analysis_window_hours,
                "total_slow_queries": len(recent_queries),
                "unique_patterns": len(self.query_patterns),
                "high_priority_patterns": sum(1 for p in self.query_patterns.values() if p.optimization_priority >= 7),
                "total_suggestions": sum(len(suggestions) for suggestions in self.optimization_suggestions.values()),
                "last_analysis": self.last_analysis_time.isoformat(),
                "queries_by_category": {
                    category.value: sum(1 for p in self.query_patterns.values() if p.query_category == category)
                    for category in QueryCategory
                },
                "queries_by_impact": {
                    impact.value: sum(1 for p in self.query_patterns.values() if p.impact_level == impact)
                    for impact in QueryImpact
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting slow query summary: {e}")
            return {"error": str(e)}
    
    async def get_slow_query_patterns(
        self, 
        limit: int = 20, 
        min_priority: int = 1
    ) -> List[Dict[str, Any]]:
        """Get slow query patterns sorted by priority"""



        try:
            # Filter and sort patterns
            filtered_patterns = [
                pattern for pattern in self.query_patterns.values()
                if pattern.optimization_priority >= min_priority
            ]
            
            # Sort by priority and total time
            filtered_patterns.sort(
                key=lambda x: (x.optimization_priority, x.total_time_ms),
                reverse=True
            )
            
            # Convert to dictionaries and add suggestions count
            result = []
            for pattern in filtered_patterns[:limit]:
                pattern_dict = pattern.to_dict()
                pattern_dict['suggestions_count'] = len(self.optimization_suggestions.get(pattern.pattern_id, []))
                result.append(pattern_dict)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting slow query patterns: {e}")
            return []
    
    async def get_optimization_suggestions(self, pattern_id: str = None) -> List[Dict[str, Any]]:
        """Get optimization suggestions"""



        try:
            if pattern_id:
                # Get suggestions for specific pattern
                suggestions = self.optimization_suggestions.get(pattern_id, [])
                return [s.to_dict() for s in suggestions]
            else:
                # Get all suggestions
                all_suggestions = []
                for suggestions in self.optimization_suggestions.values():
                    all_suggestions.extend([s.to_dict() for s in suggestions])
                
                # Sort by confidence and impact
                all_suggestions.sort(
                    key=lambda x: (x['confidence_score'], x['estimated_improvement_percent']),
                    reverse=True
                )
                
                return all_suggestions
                
        except Exception as e:
            self.logger.error(f"Error getting optimization suggestions: {e}")
            return []
    
    async def get_recent_slow_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent slow query instances"""



        try:
            recent_queries = list(self.slow_queries)[-limit:]
            return [q.to_dict() for q in reversed(recent_queries)]
        except Exception as e:
            self.logger.error(f"Error getting recent slow queries: {e}")
            return []
    
    async def analyze_query_now(self, query: str) -> Dict[str, Any]:
        """Analyze a specific query immediately"""



        try:
            normalized = self._normalize_query(query)
            query_id = self._generate_query_id(normalized)
            
            # Check if we have pattern data
            pattern = self.query_patterns.get(query_id)
            suggestions = self.optimization_suggestions.get(query_id, [])
            
            analysis = {
                "query_id": query_id,
                "normalized_query": normalized,
                "pattern_found": pattern is not None,
                "pattern_data": pattern.to_dict() if pattern else None,
                "suggestions_count": len(suggestions),
                "suggestions": [s.to_dict() for s in suggestions],
                "query_category": self._categorize_query(normalized).value,
                "affected_tables": self._extract_table_names(normalized),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing query: {e}")
            return {"error": str(e)}
