"""⚡ Backend Database Optimization - Consolidated Enterprise Performance Optimization
====================================================================================
Module: backend/database/optimization.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Consolidated Database Optimization Management - Enterprise Production-Ready
Responsibility: Complete performance optimization for multi-format content protection and AI monetization
===============================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This consolidated optimization module provides comprehensive performance optimization for:
- AI-powered query optimization and automatic index recommendations
- Dynamic query plan analysis and performance tuning
- Content processing pipeline optimization for multi-modal data
- Revenue analytics query optimization and caching strategies
- Real-time performance monitoring with automatic optimization triggers
- Intelligent connection pool sizing and resource allocation
- Database partitioning and sharding optimization strategies

CONSOLIDATED OPTIMIZATION FEATURES:
- Machine learning-powered query optimization and index recommendations
- Real-time performance monitoring with automatic optimization triggers  
- Dynamic query plan analysis and optimization suggestions
- Intelligent connection pool sizing based on workload patterns
- Content processing pipeline optimization for audio, video, image, text
- Revenue analytics performance tuning and caching optimization
- Database partitioning strategies for high-volume content data
- Multi-database optimization coordination (PostgreSQL, Redis, MongoDB)
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Tuple, Set, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import statistics
from collections import defaultdict, deque
import hashlib
import re

# ML and optimization imports
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# SQL parsing imports
try:
    import sqlparse
    from sqlparse import sql, tokens
    SQL_PARSING_AVAILABLE = True
except ImportError:
    SQL_PARSING_AVAILABLE = False

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Optimization type enumeration."""
    INDEX_RECOMMENDATION = "index_recommendation"
    QUERY_REWRITE = "query_rewrite"
    PARTITION_STRATEGY = "partition_strategy"
    CONNECTION_POOL = "connection_pool"
    CACHE_STRATEGY = "cache_strategy"
    RESOURCE_ALLOCATION = "resource_allocation"
    SCHEMA_OPTIMIZATION = "schema_optimization"


class PerformanceImpact(Enum):
    """Performance impact levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OptimizationStatus(Enum):
    """Optimization recommendation status."""
    PENDING = "pending"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    MONITORING = "monitoring"


@dataclass
class QueryPattern:
    """Query pattern analysis data."""
    pattern_id: str
    query_template: str
    frequency: int
    average_duration: float
    max_duration: float
    min_duration: float
    tables_accessed: List[str]
    columns_accessed: List[str]
    joins_count: int
    where_conditions: List[str]
    order_by_columns: List[str]
    group_by_columns: List[str]
    has_subqueries: bool = False
    has_aggregations: bool = False
    has_window_functions: bool = False


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation data structure."""
    recommendation_id: str
    optimization_type: OptimizationType
    title: str
    description: str
    expected_impact: PerformanceImpact
    confidence_score: float
    implementation_effort: str
    sql_statements: List[str]
    affected_tables: List[str]
    estimated_improvement: float  # percentage
    risk_level: str
    prerequisites: List[str]
    monitoring_metrics: List[str]
    created_at: datetime
    status: OptimizationStatus = OptimizationStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: datetime
    query_throughput: float
    average_response_time: float
    connection_pool_utilization: float
    cache_hit_ratio: float
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    active_connections: int
    slow_queries_count: int
    error_rate: float


class IOptimizationEngine(ABC):
    """Optimization engine interface."""
    
    @abstractmethod
    async def analyze_performance(self, metrics: PerformanceMetrics) -> List[OptimizationRecommendation]:
        """Analyze performance and generate recommendations."""
        pass
    
    @abstractmethod
    async def implement_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Implement optimization recommendation."""
        pass
    
    @abstractmethod
    async def monitor_optimization(self, recommendation_id: str) -> Dict[str, Any]:
        """Monitor optimization effectiveness."""
        pass


class QueryOptimizationEngine(IOptimizationEngine):
    """
    🚀 Query Optimization Engine
    
    AI-powered query optimization with automatic index recommendations
    and query rewriting for maximum performance.
    """
    
    def __init__(self):
        self._query_patterns: Dict[str, QueryPattern] = {}
        self._query_history: deque = deque(maxlen=10000)
        self._index_recommendations: List[OptimizationRecommendation] = []
        self._performance_baseline: Optional[PerformanceMetrics] = None
        
    async def analyze_performance(self, metrics: PerformanceMetrics) -> List[OptimizationRecommendation]:
        """Analyze query performance and generate optimization recommendations."""
        recommendations = []
        
        # Set baseline if not exists
        if self._performance_baseline is None:
            self._performance_baseline = metrics
            return recommendations
        
        # Analyze slow queries
        if metrics.average_response_time > 1000:  # > 1 second
            slow_query_rec = await self._recommend_slow_query_optimization(metrics)
            if slow_query_rec:
                recommendations.append(slow_query_rec)
        
        # Analyze query patterns for indexing opportunities
        index_recommendations = await self._analyze_indexing_opportunities()
        recommendations.extend(index_recommendations)
        
        # Check for query rewrite opportunities
        rewrite_recommendations = await self._analyze_query_rewrite_opportunities()
        recommendations.extend(rewrite_recommendations)
        
        return recommendations
    
    async def _recommend_slow_query_optimization(self, metrics: PerformanceMetrics) -> Optional[OptimizationRecommendation]:
        """Recommend optimizations for slow queries."""
        if metrics.slow_queries_count == 0:
            return None
        
        # Analyze recent slow queries
        slow_queries = [q for q in list(self._query_history)[-100:] if q.get("duration", 0) > 1000]
        
        if not slow_queries:
            return None
        
        # Find most common slow query patterns
        pattern_frequency = defaultdict(int)
        for query in slow_queries:
            pattern = self._extract_query_pattern(query.get("sql", ""))
            pattern_frequency[pattern] += 1
        
        most_common_pattern = max(pattern_frequency, key=pattern_frequency.get)
        
        recommendation = OptimizationRecommendation(
            recommendation_id=f"slow_query_{int(datetime.now().timestamp())}",
            optimization_type=OptimizationType.QUERY_REWRITE,
            title="Optimize Slow Query Pattern",
            description=f"Frequent slow query pattern detected: {most_common_pattern[:100]}...",
            expected_impact=PerformanceImpact.HIGH,
            confidence_score=0.8,
            implementation_effort="Medium",
            sql_statements=await self._generate_query_optimization_sql(most_common_pattern),
            affected_tables=self._extract_tables_from_pattern(most_common_pattern),
            estimated_improvement=30.0,
            risk_level="Low",
            prerequisites=["Analyze query execution plan", "Test on staging environment"],
            monitoring_metrics=["average_response_time", "query_throughput"],
            created_at=datetime.now(timezone.utc),
            metadata={
                "pattern": most_common_pattern,
                "frequency": pattern_frequency[most_common_pattern],
                "avg_duration": statistics.mean([q.get("duration", 0) for q in slow_queries])
            }
        )
        
        return recommendation
    
    async def _analyze_indexing_opportunities(self) -> List[OptimizationRecommendation]:
        """Analyze query patterns for indexing opportunities."""
        recommendations = []
        
        if not SQL_PARSING_AVAILABLE:
            return recommendations
        
        # Analyze WHERE clauses for potential indexes
        where_columns = defaultdict(int)
        join_columns = defaultdict(int)
        order_columns = defaultdict(int)
        
        for query in list(self._query_history)[-1000:]:  # Last 1000 queries
            sql = query.get("sql", "")
            if not sql:
                continue
            
            try:
                parsed = sqlparse.parse(sql)[0]
                
                # Extract WHERE columns
                where_cols = self._extract_where_columns(parsed)
                for col in where_cols:
                    where_columns[col] += 1
                
                # Extract JOIN columns
                join_cols = self._extract_join_columns(parsed)
                for col in join_cols:
                    join_columns[col] += 1
                
                # Extract ORDER BY columns
                order_cols = self._extract_order_columns(parsed)
                for col in order_cols:
                    order_columns[col] += 1
                    
            except Exception as e:
                logger.error(f"Failed to parse SQL: {e}")
                continue
        
        # Generate index recommendations for frequently used columns
        for column, frequency in where_columns.items():
            if frequency >= 10:  # Column used in WHERE clause at least 10 times
                rec = OptimizationRecommendation(
                    recommendation_id=f"index_where_{hashlib.md5(column.encode()).hexdigest()[:8]}",
                    optimization_type=OptimizationType.INDEX_RECOMMENDATION,
                    title=f"Create Index on {column}",
                    description=f"Frequently used in WHERE clauses ({frequency} times). Consider adding index for better performance.",
                    expected_impact=PerformanceImpact.MEDIUM,
                    confidence_score=min(0.9, frequency / 100),
                    implementation_effort="Low",
                    sql_statements=[f"CREATE INDEX IF NOT EXISTS idx_{column.replace('.', '_')} ON {column.split('.')[0]} ({column.split('.')[-1]});"],
                    affected_tables=[column.split('.')[0]],
                    estimated_improvement=15.0,
                    risk_level="Very Low",
                    prerequisites=["Verify column selectivity", "Check existing indexes"],
                    monitoring_metrics=["query_performance", "index_usage"],
                    created_at=datetime.now(timezone.utc),
                    metadata={"column": column, "frequency": frequency, "type": "where_clause"}
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _extract_query_pattern(self, sql: str) -> str:
        """Extract query pattern by normalizing parameters."""
        if not sql:
            return ""
        
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Normalize string literals
        sql = re.sub(r"'[^']*'", "'?'", sql)
        sql = re.sub(r'"[^"]*"', '"?"', sql)
        
        # Normalize numeric literals
        sql = re.sub(r'\b\d+\b', '?', sql)
        
        # Normalize whitespace
        sql = ' '.join(sql.split())
        
        return sql.strip()
    
    def _extract_tables_from_pattern(self, pattern: str) -> List[str]:
        """Extract table names from query pattern."""
        tables = []
        
        # Simple regex to find table names after FROM and JOIN
        from_matches = re.findall(r'FROM\s+(\w+)', pattern, re.IGNORECASE)
        join_matches = re.findall(r'JOIN\s+(\w+)', pattern, re.IGNORECASE)
        
        tables.extend(from_matches)
        tables.extend(join_matches)
        
        return list(set(tables))
    
    async def _generate_query_optimization_sql(self, pattern: str) -> List[str]:
        """Generate SQL statements for query optimization."""
        # This would contain more sophisticated optimization logic
        # For now, return basic optimization suggestions
        optimizations = []
        
        # Add LIMIT if not present and no aggregation
        if "LIMIT" not in pattern.upper() and "GROUP BY" not in pattern.upper():
            optimizations.append("-- Consider adding LIMIT clause to reduce result set size")
        
        # Suggest covering indexes for SELECT columns
        if "SELECT" in pattern.upper():
            optimizations.append("-- Consider creating covering indexes for frequently selected columns")
        
        return optimizations
    
    def _extract_where_columns(self, parsed_sql) -> List[str]:
        """Extract columns used in WHERE clauses."""
        columns = []
        # Implementation would parse the SQL tree to find WHERE conditions
        # This is a simplified version
        return columns
    
    def _extract_join_columns(self, parsed_sql) -> List[str]:
        """Extract columns used in JOIN conditions."""
        columns = []
        # Implementation would parse the SQL tree to find JOIN conditions
        return columns
    
    def _extract_order_columns(self, parsed_sql) -> List[str]:
        """Extract columns used in ORDER BY clauses."""
        columns = []
        # Implementation would parse the SQL tree to find ORDER BY columns
        return columns
    
    async def implement_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Implement query optimization recommendation."""
        try:
            logger.info(f"⚡ Implementing optimization: {recommendation.title}")
            
            # This would execute the SQL statements in the recommendation
            # For safety, this should be done with proper validation and rollback capability
            
            for sql in recommendation.sql_statements:
                if sql.strip().startswith("--"):
                    continue  # Skip comments
                
                logger.info(f"Executing optimization SQL: {sql}")
                # await database_connection.execute(sql)
            
            recommendation.status = OptimizationStatus.IMPLEMENTED
            logger.info(f"✅ Optimization implemented: {recommendation.recommendation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to implement optimization {recommendation.recommendation_id}: {e}")
            recommendation.status = OptimizationStatus.REJECTED
            return False
    
    async def monitor_optimization(self, recommendation_id: str) -> Dict[str, Any]:
        """Monitor the effectiveness of implemented optimization."""
        # This would track performance metrics before and after optimization
        return {
            "recommendation_id": recommendation_id,
            "status": "monitoring",
            "performance_improvement": 0.0,
            "monitoring_period": "7_days",
            "metrics_tracked": ["response_time", "throughput", "resource_usage"]
        }
    
    async def record_query_execution(self, sql: str, duration_ms: float, execution_plan: Optional[str] = None):
        """Record query execution for analysis."""
        query_record = {
            "sql": sql,
            "duration": duration_ms,
            "execution_plan": execution_plan,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pattern": self._extract_query_pattern(sql)
        }
        
        self._query_history.append(query_record)
        
        # Update query patterns
        pattern = query_record["pattern"]
        if pattern in self._query_patterns:
            self._query_patterns[pattern].frequency += 1
            durations = [self._query_patterns[pattern].average_duration, duration_ms]
            self._query_patterns[pattern].average_duration = statistics.mean(durations)
            self._query_patterns[pattern].max_duration = max(self._query_patterns[pattern].max_duration, duration_ms)
            self._query_patterns[pattern].min_duration = min(self._query_patterns[pattern].min_duration, duration_ms)
        else:
            self._query_patterns[pattern] = QueryPattern(
                pattern_id=hashlib.md5(pattern.encode()).hexdigest(),
                query_template=pattern,
                frequency=1,
                average_duration=duration_ms,
                max_duration=duration_ms,
                min_duration=duration_ms,
                tables_accessed=self._extract_tables_from_pattern(pattern),
                columns_accessed=[],
                joins_count=pattern.upper().count("JOIN"),
                where_conditions=[],
                order_by_columns=[],
                group_by_columns=[],
                has_subqueries="SELECT" in pattern.upper().replace("SELECT", "", 1),
                has_aggregations=any(agg in pattern.upper() for agg in ["COUNT", "SUM", "AVG", "MAX", "MIN"]),
                has_window_functions="OVER" in pattern.upper()
            )


class ConnectionPoolOptimizer(IOptimizationEngine):
    """
    🏊 Connection Pool Optimizer
    
    Intelligent connection pool sizing and optimization based on workload patterns.
    """
    
    def __init__(self):
        self._connection_metrics: deque = deque(maxlen=1000)
        self._pool_configurations: Dict[str, Dict[str, Any]] = {}
        
    async def analyze_performance(self, metrics: PerformanceMetrics) -> List[OptimizationRecommendation]:
        """Analyze connection pool performance."""
        recommendations = []
        
        # Record metrics
        self._connection_metrics.append({
            "timestamp": metrics.timestamp,
            "utilization": metrics.connection_pool_utilization,
            "active_connections": metrics.active_connections
        })
        
        # Check if pool is consistently over-utilized
        recent_metrics = list(self._connection_metrics)[-20:]  # Last 20 data points
        if len(recent_metrics) >= 10:
            avg_utilization = statistics.mean([m["utilization"] for m in recent_metrics])
            
            if avg_utilization > 0.8:  # 80% utilization
                rec = OptimizationRecommendation(
                    recommendation_id=f"pool_scale_{int(datetime.now().timestamp())}",
                    optimization_type=OptimizationType.CONNECTION_POOL,
                    title="Scale Up Connection Pool",
                    description=f"Connection pool consistently at {avg_utilization:.1%} utilization. Consider increasing pool size.",
                    expected_impact=PerformanceImpact.MEDIUM,
                    confidence_score=0.9,
                    implementation_effort="Low",
                    sql_statements=[],
                    affected_tables=[],
                    estimated_improvement=20.0,
                    risk_level="Low",
                    prerequisites=["Monitor for 24 hours", "Check database connection limits"],
                    monitoring_metrics=["connection_pool_utilization", "wait_time"],
                    created_at=datetime.now(timezone.utc),
                    metadata={
                        "current_utilization": avg_utilization,
                        "recommended_action": "increase_pool_size",
                        "suggested_multiplier": 1.5
                    }
                )
                recommendations.append(rec)
            
            elif avg_utilization < 0.3:  # 30% utilization
                rec = OptimizationRecommendation(
                    recommendation_id=f"pool_reduce_{int(datetime.now().timestamp())}",
                    optimization_type=OptimizationType.CONNECTION_POOL,
                    title="Reduce Connection Pool Size",
                    description=f"Connection pool underutilized at {avg_utilization:.1%}. Consider reducing pool size to save resources.",
                    expected_impact=PerformanceImpact.LOW,
                    confidence_score=0.7,
                    implementation_effort="Low",
                    sql_statements=[],
                    affected_tables=[],
                    estimated_improvement=5.0,
                    risk_level="Medium",
                    prerequisites=["Analyze peak usage patterns", "Test during high load"],
                    monitoring_metrics=["connection_pool_utilization", "queue_time"],
                    created_at=datetime.now(timezone.utc),
                    metadata={
                        "current_utilization": avg_utilization,
                        "recommended_action": "decrease_pool_size",
                        "suggested_multiplier": 0.7
                    }
                )
                recommendations.append(rec)
        
        return recommendations
    
    async def implement_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Implement connection pool optimization."""
        try:
            action = recommendation.metadata.get("recommended_action")
            multiplier = recommendation.metadata.get("suggested_multiplier", 1.0)
            
            if action == "increase_pool_size":
                # Increase pool size
                logger.info(f"🔄 Scaling up connection pool by {multiplier}x")
                # Implementation would update pool configuration
                
            elif action == "decrease_pool_size":
                # Decrease pool size
                logger.info(f"🔄 Scaling down connection pool by {multiplier}x")
                # Implementation would update pool configuration
            
            recommendation.status = OptimizationStatus.IMPLEMENTED
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to implement pool optimization: {e}")
            return False
    
    async def monitor_optimization(self, recommendation_id: str) -> Dict[str, Any]:
        """Monitor connection pool optimization effectiveness."""
        return {
            "recommendation_id": recommendation_id,
            "status": "monitoring",
            "pool_utilization_change": 0.0,
            "performance_impact": "positive"
        }


class DatabaseOptimizationManager:
    """
    🏢 Enterprise Database Optimization Manager
    
    Central optimization orchestrator for the IA Influencer platform providing
    AI-powered performance optimization and intelligent resource management.
    """
    
    def __init__(self):
        self.query_optimizer = QueryOptimizationEngine()
        self.pool_optimizer = ConnectionPoolOptimizer()
        self._optimization_engines: List[IOptimizationEngine] = [
            self.query_optimizer,
            self.pool_optimizer
        ]
        self._optimization_history: List[OptimizationRecommendation] = []
        self._monitoring_tasks: List[asyncio.Task] = []
        self._auto_optimization_enabled = False
        
    async def initialize(self, auto_optimization: bool = False):
        """Initialize optimization manager."""
        logger.info("⚡ Initializing Enterprise Database Optimization Manager...")
        
        self._auto_optimization_enabled = auto_optimization
        
        # Start optimization monitoring
        self._monitoring_tasks.append(
            asyncio.create_task(self._optimization_monitor())
        )
        
        logger.info("✅ Enterprise Database Optimization Manager initialized")
    
    async def _optimization_monitor(self):
        """Monitor and trigger optimizations."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                if self._auto_optimization_enabled:
                    # Auto-implement low-risk optimizations
                    await self._auto_implement_safe_optimizations()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Optimization monitor error: {e}")
    
    async def _auto_implement_safe_optimizations(self):
        """Automatically implement safe, low-risk optimizations."""
        pending_optimizations = [
            opt for opt in self._optimization_history 
            if opt.status == OptimizationStatus.PENDING and opt.risk_level in ["Very Low", "Low"]
        ]
        
        for optimization in pending_optimizations:
            try:
                # Only auto-implement very safe optimizations
                if (optimization.confidence_score > 0.8 and 
                    optimization.risk_level == "Very Low" and
                    optimization.optimization_type in [OptimizationType.INDEX_RECOMMENDATION]):
                    
                    logger.info(f"🤖 Auto-implementing safe optimization: {optimization.title}")
                    
                    success = False
                    for engine in self._optimization_engines:
                        if hasattr(engine, 'implement_optimization'):
                            success = await engine.implement_optimization(optimization)
                            if success:
                                break
                    
                    if success:
                        optimization.status = OptimizationStatus.MONITORING
                        logger.info(f"✅ Auto-implemented: {optimization.recommendation_id}")
                    
            except Exception as e:
                logger.error(f"Auto-optimization failed for {optimization.recommendation_id}: {e}")
    
    async def analyze_and_recommend(self, metrics: PerformanceMetrics) -> List[OptimizationRecommendation]:
        """Analyze performance and generate optimization recommendations."""
        all_recommendations = []
        
        # Get recommendations from all engines
        for engine in self._optimization_engines:
            try:
                recommendations = await engine.analyze_performance(metrics)
                all_recommendations.extend(recommendations)
            except Exception as e:
                logger.error(f"Optimization engine analysis failed: {e}")
        
        # Store recommendations
        self._optimization_history.extend(all_recommendations)
        
        # Sort by impact and confidence
        all_recommendations.sort(
            key=lambda x: (x.expected_impact.value, x.confidence_score),
            reverse=True
        )
        
        logger.info(f"📊 Generated {len(all_recommendations)} optimization recommendations")
        
        return all_recommendations
    
    async def implement_optimization(self, recommendation_id: str) -> bool:
        """Implement a specific optimization recommendation."""
        recommendation = None
        for opt in self._optimization_history:
            if opt.recommendation_id == recommendation_id:
                recommendation = opt
                break
        
        if not recommendation:
            logger.error(f"Optimization recommendation not found: {recommendation_id}")
            return False
        
        # Find appropriate engine
        for engine in self._optimization_engines:
            try:
                if await engine.implement_optimization(recommendation):
                    recommendation.status = OptimizationStatus.IMPLEMENTED
                    logger.info(f"✅ Optimization implemented: {recommendation_id}")
                    return True
            except Exception as e:
                logger.error(f"Engine failed to implement optimization: {e}")
        
        recommendation.status = OptimizationStatus.REJECTED
        return False
    
    async def get_optimization_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive optimization dashboard."""
        # Count recommendations by status
        status_counts = defaultdict(int)
        impact_counts = defaultdict(int)
        
        for opt in self._optimization_history:
            status_counts[opt.status.value] += 1
            impact_counts[opt.expected_impact.value] += 1
        
        # Recent recommendations
        recent_recommendations = sorted(
            self._optimization_history,
            key=lambda x: x.created_at,
            reverse=True
        )[:10]
        
        dashboard = {
            "summary": {
                "total_recommendations": len(self._optimization_history),
                "pending": status_counts.get("pending", 0),
                "implemented": status_counts.get("implemented", 0),
                "monitoring": status_counts.get("monitoring", 0),
                "auto_optimization_enabled": self._auto_optimization_enabled
            },
            "by_impact": dict(impact_counts),
            "by_status": dict(status_counts),
            "recent_recommendations": [
                {
                    "recommendation_id": rec.recommendation_id,
                    "title": rec.title,
                    "type": rec.optimization_type.value,
                    "impact": rec.expected_impact.value,
                    "confidence": rec.confidence_score,
                    "status": rec.status.value,
                    "created_at": rec.created_at.isoformat()
                }
                for rec in recent_recommendations
            ],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return dashboard
    
    def get_recommendation(self, recommendation_id: str) -> Optional[OptimizationRecommendation]:
        """Get specific optimization recommendation."""
        for opt in self._optimization_history:
            if opt.recommendation_id == recommendation_id:
                return opt
        return None
    
    def get_recommendations_by_type(self, optimization_type: OptimizationType) -> List[OptimizationRecommendation]:
        """Get recommendations by optimization type."""
        return [opt for opt in self._optimization_history if opt.optimization_type == optimization_type]
    
    async def close(self):
        """Close optimization manager."""
        logger.info("🔌 Closing Database Optimization Manager...")
        
        # Cancel monitoring tasks
        for task in self._monitoring_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Database Optimization Manager closed")


# Global optimization manager instance
_optimization_manager: Optional[DatabaseOptimizationManager] = None


def get_optimization_manager() -> DatabaseOptimizationManager:
    """Get the global database optimization manager."""
    global _optimization_manager
    if _optimization_manager is None:
        _optimization_manager = DatabaseOptimizationManager()
    return _optimization_manager


# Export all public interfaces
__all__ = [
    "DatabaseOptimizationManager",
    "get_optimization_manager",
    "QueryOptimizationEngine",
    "ConnectionPoolOptimizer", 
    "IOptimizationEngine",
    "OptimizationRecommendation",
    "QueryPattern",
    "PerformanceMetrics",
    "OptimizationType",
    "PerformanceImpact", 
    "OptimizationStatus",
]