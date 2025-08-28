"""
Advanced Index Strategies Module

Enhanced index optimization strategies for the Ainflue platform with machine learning-based
recommendations, predictive indexing, and performance-driven adaptive strategies.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import json
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from .index_optimizer import IndexOptimizer, IndexRecommendation, IndexType, IndexPriority
from ...core.logging import get_logger

logger = get_logger(__name__)


class AdvancedIndexStrategy(Enum):
    """Advanced indexing strategies"""
    PREDICTIVE = "predictive"
    ADAPTIVE = "adaptive" 
    ML_DRIVEN = "ml_driven"
    WORKLOAD_AWARE = "workload_aware"
    COST_OPTIMIZED = "cost_optimized"
    TENANT_AWARE = "tenant_aware"


@dataclass
class IndexUsagePattern:
    """Index usage pattern analysis"""
    index_name: str
    table_name: str
    usage_frequency: int
    avg_scan_cost: float
    selectivity: float
    maintenance_cost: float
    space_utilization: float
    temporal_pattern: Dict[str, int]  # hour -> usage count
    query_patterns: List[str]
    performance_impact: float


@dataclass
class WorkloadProfile:
    """Database workload profile"""
    read_write_ratio: float
    peak_hours: List[int]
    query_complexity_distribution: Dict[str, float]
    table_access_patterns: Dict[str, int]
    join_frequency: Dict[str, int]
    filter_selectivity: Dict[str, float]
    data_growth_rate: float


class PredictiveIndexManager:
    """Predictive index management using historical patterns"""
    
    def __init__(self, base_optimizer: IndexOptimizer):
        self.base_optimizer = base_optimizer
        self.usage_history: Dict[str, List[IndexUsagePattern]] = defaultdict(list)
        self.workload_profiles: Dict[str, WorkloadProfile] = {}
        self.prediction_models: Dict[str, Any] = {}
        
    async def analyze_usage_patterns(self, engine: AsyncEngine, days_back: int = 30) -> Dict[str, IndexUsagePattern]:
        """Analyze index usage patterns over time"""
        try:
            patterns = {}
            
            # Get index usage statistics
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    pg_relation_size(indexrelid) as size_bytes
                FROM pg_stat_user_indexes 
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC
            """)
            
            async with engine.begin() as conn:
                result = await conn.execute(query)
                
                for row in result:
                    # Calculate usage pattern metrics
                    selectivity = (row.idx_tup_fetch / max(row.idx_tup_read, 1)) if row.idx_tup_read > 0 else 0
                    
                    pattern = IndexUsagePattern(
                        index_name=row.indexname,
                        table_name=row.tablename,
                        usage_frequency=row.idx_scan or 0,
                        avg_scan_cost=self._calculate_scan_cost(row.size_bytes, row.idx_scan),
                        selectivity=selectivity,
                        maintenance_cost=self._estimate_maintenance_cost(row.size_bytes),
                        space_utilization=row.size_bytes / (1024 * 1024),  # MB
                        temporal_pattern=await self._get_temporal_usage(engine, row.indexname),
                        query_patterns=[],
                        performance_impact=self._calculate_performance_impact(row.idx_scan, selectivity)
                    )
                    
                    patterns[row.indexname] = pattern
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze usage patterns: {e}")
            return {}
    
    def _calculate_scan_cost(self, size_bytes: int, scan_count: int) -> float:
        """Calculate average scan cost"""
        if scan_count == 0:
            return 0.0
        
        # Simplified cost calculation based on size and usage
        size_factor = size_bytes / (1024 * 1024)  # MB
        return size_factor / scan_count
    
    def _estimate_maintenance_cost(self, size_bytes: int) -> float:
        """Estimate index maintenance cost"""
        # Larger indexes have higher maintenance costs
        size_mb = size_bytes / (1024 * 1024)
        return size_mb * 0.1  # 10% of size as maintenance factor
    
    async def _get_temporal_usage(self, engine: AsyncEngine, index_name: str) -> Dict[str, int]:
        """Get temporal usage patterns (simplified)"""
        # In a real implementation, you'd query pg_stat_activity or custom logging
        # For now, return a placeholder pattern
        return {str(hour): 0 for hour in range(24)}
    
    def _calculate_performance_impact(self, usage_count: int, selectivity: float) -> float:
        """Calculate performance impact score"""
        return usage_count * selectivity * 10
    
    async def predict_index_needs(self, workload_profile: WorkloadProfile) -> List[IndexRecommendation]:
        """Predict future index needs based on workload patterns"""
        recommendations = []
        
        try:
            # Analyze growth patterns
            if workload_profile.data_growth_rate > 0.2:  # 20% growth
                recommendations.extend(self._recommend_growth_indexes(workload_profile))
            
            # Analyze temporal patterns
            if workload_profile.peak_hours:
                recommendations.extend(self._recommend_peak_optimization_indexes(workload_profile))
            
            # Analyze query complexity
            if workload_profile.query_complexity_distribution.get('complex', 0) > 0.3:
                recommendations.extend(self._recommend_complexity_indexes(workload_profile))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to predict index needs: {e}")
            return []
    
    def _recommend_growth_indexes(self, profile: WorkloadProfile) -> List[IndexRecommendation]:
        """Recommend indexes for high-growth scenarios"""
        recommendations = []
        
        # Recommend partitioning-friendly indexes
        for table, access_count in profile.table_access_patterns.items():
            if access_count > 1000:  # High-access tables
                recommendations.append(IndexRecommendation(
                    table_name=table,
                    columns=["created_at", "id"],
                    index_type=IndexType.BTREE,
                    priority=IndexPriority.HIGH,
                    estimated_benefit=40.0,
                    estimated_cost=20.0,
                    reason="High-growth table optimization with temporal partitioning support",
                    query_patterns=["time-based queries"]
                ))
        
        return recommendations
    
    def _recommend_peak_optimization_indexes(self, profile: WorkloadProfile) -> List[IndexRecommendation]:
        """Recommend indexes for peak hour optimization"""
        recommendations = []
        
        # Focus on read performance during peak hours
        for table, access_count in profile.table_access_patterns.items():
            recommendations.append(IndexRecommendation(
                table_name=table,
                columns=["user_id", "status"],
                index_type=IndexType.BTREE,
                priority=IndexPriority.MEDIUM,
                estimated_benefit=25.0,
                estimated_cost=15.0,
                reason="Peak hour read optimization",
                query_patterns=["user filtering", "status queries"]
            ))
        
        return recommendations
    
    def _recommend_complexity_indexes(self, profile: WorkloadProfile) -> List[IndexRecommendation]:
        """Recommend indexes for complex query optimization"""
        recommendations = []
        
        # Multi-column indexes for complex joins
        for join_pattern, frequency in profile.join_frequency.items():
            if frequency > 100:
                recommendations.append(IndexRecommendation(
                    table_name=join_pattern.split('.')[0],
                    columns=["id", "foreign_key", "created_at"],
                    index_type=IndexType.BTREE,
                    priority=IndexPriority.HIGH,
                    estimated_benefit=50.0,
                    estimated_cost=30.0,
                    reason="Complex join optimization",
                    query_patterns=[f"join pattern: {join_pattern}"]
                ))
        
        return recommendations


class AdaptiveIndexManager:
    """Adaptive index management that responds to workload changes"""
    
    def __init__(self, base_optimizer: IndexOptimizer):
        self.base_optimizer = base_optimizer
        self.adaptation_history: List[Dict[str, Any]] = []
        self.current_strategy = AdvancedIndexStrategy.ADAPTIVE
        
    async def adapt_to_workload_changes(self, engine: AsyncEngine, 
                                      new_workload: WorkloadProfile,
                                      current_workload: WorkloadProfile) -> List[str]:
        """Adapt indexes based on workload changes"""
        adaptations = []
        
        try:
            # Analyze workload shift
            read_write_shift = abs(new_workload.read_write_ratio - current_workload.read_write_ratio)
            
            if read_write_shift > 0.2:  # Significant shift
                if new_workload.read_write_ratio > current_workload.read_write_ratio:
                    # Shift towards more reads - optimize for read performance
                    adaptations.extend(await self._optimize_for_reads(engine, new_workload))
                else:
                    # Shift towards more writes - optimize for write performance
                    adaptations.extend(await self._optimize_for_writes(engine, new_workload))
            
            # Adapt to data growth
            growth_change = new_workload.data_growth_rate - current_workload.data_growth_rate
            if growth_change > 0.1:  # 10% increase in growth
                adaptations.extend(await self._adapt_for_growth(engine, new_workload))
            
            # Record adaptation
            self.adaptation_history.append({
                'timestamp': datetime.now(),
                'trigger': 'workload_change',
                'adaptations': adaptations,
                'workload_shift': {
                    'read_write_shift': read_write_shift,
                    'growth_change': growth_change
                }
            })
            
            return adaptations
            
        except Exception as e:
            logger.error(f"Failed to adapt to workload changes: {e}")
            return []
    
    async def _optimize_for_reads(self, engine: AsyncEngine, workload: WorkloadProfile) -> List[str]:
        """Optimize indexes for read-heavy workloads"""
        optimizations = []
        
        # Create covering indexes for frequent read patterns
        for table, access_count in workload.table_access_patterns.items():
            if access_count > 500:  # High read frequency
                create_sql = f"""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{table}_covering_read
                ON {table} (user_id, created_at) 
                INCLUDE (status, metadata)
                WHERE active = true
                """
                
                try:
                    async with engine.begin() as conn:
                        await conn.execute(text(create_sql))
                    optimizations.append(f"Created covering index for {table}")
                except Exception as e:
                    logger.warning(f"Failed to create covering index for {table}: {e}")
        
        return optimizations
    
    async def _optimize_for_writes(self, engine: AsyncEngine, workload: WorkloadProfile) -> List[str]:
        """Optimize indexes for write-heavy workloads"""
        optimizations = []
        
        # Drop unused indexes that slow down writes
        unused_indexes = await self._find_unused_indexes(engine)
        
        for index_name in unused_indexes[:3]:  # Drop up to 3 unused indexes
            try:
                drop_sql = f"DROP INDEX CONCURRENTLY IF EXISTS {index_name}"
                async with engine.begin() as conn:
                    await conn.execute(text(drop_sql))
                optimizations.append(f"Dropped unused index {index_name}")
            except Exception as e:
                logger.warning(f"Failed to drop index {index_name}: {e}")
        
        return optimizations
    
    async def _adapt_for_growth(self, engine: AsyncEngine, workload: WorkloadProfile) -> List[str]:
        """Adapt indexes for data growth"""
        adaptations = []
        
        # Create BRIN indexes for time-series data
        time_series_tables = ['content_performance', 'revenue_tracking', 'crawl_results']
        
        for table in time_series_tables:
            if table in workload.table_access_patterns:
                brin_sql = f"""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{table}_created_at_brin
                ON {table} USING BRIN (created_at)
                """
                
                try:
                    async with engine.begin() as conn:
                        await conn.execute(text(brin_sql))
                    adaptations.append(f"Created BRIN index for {table}")
                except Exception as e:
                    logger.warning(f"Failed to create BRIN index for {table}: {e}")
        
        return adaptations
    
    async def _find_unused_indexes(self, engine: AsyncEngine) -> List[str]:
        """Find unused indexes"""
        query = text("""
            SELECT indexname 
            FROM pg_stat_user_indexes 
            WHERE schemaname = 'public' 
            AND idx_scan = 0
            AND NOT indisunique
            ORDER BY pg_relation_size(indexrelid) DESC
        """)
        
        try:
            async with engine.begin() as conn:
                result = await conn.execute(query)
                return [row.indexname for row in result]
        except Exception as e:
            logger.error(f"Failed to find unused indexes: {e}")
            return []


class TenantAwareIndexManager:
    """Multi-tenant aware index management"""
    
    def __init__(self, base_optimizer: IndexOptimizer):
        self.base_optimizer = base_optimizer
        self.tenant_patterns: Dict[str, Dict[str, Any]] = {}
        
    async def analyze_tenant_patterns(self, engine: AsyncEngine) -> Dict[str, Any]:
        """Analyze per-tenant access patterns"""
        try:
            patterns = {}
            
            # Get tenant usage statistics
            query = text("""
                SELECT 
                    tenant_id,
                    COUNT(*) as query_count,
                    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_processing_time
                FROM (
                    SELECT tenant_id, created_at, updated_at FROM users 
                    UNION ALL
                    SELECT u.tenant_id, c.created_at, c.updated_at 
                    FROM content c JOIN users u ON c.user_id = u.id
                ) t
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY tenant_id
                ORDER BY query_count DESC
                LIMIT 100
            """)
            
            async with engine.begin() as conn:
                result = await conn.execute(query)
                
                for row in result:
                    patterns[row.tenant_id] = {
                        'query_count': row.query_count,
                        'avg_processing_time': row.avg_processing_time or 0,
                        'priority': 'high' if row.query_count > 1000 else 'medium' if row.query_count > 100 else 'low'
                    }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze tenant patterns: {e}")
            return {}
    
    async def create_tenant_specific_indexes(self, engine: AsyncEngine, 
                                           tenant_id: str, 
                                           pattern: Dict[str, Any]) -> List[str]:
        """Create tenant-specific indexes"""
        created_indexes = []
        
        if pattern.get('priority') == 'high':
            # High-priority tenants get dedicated indexes
            tenant_indexes = [
                f"""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_tenant_{tenant_id}
                ON users (tenant_id, id) WHERE tenant_id = '{tenant_id}'
                """,
                f"""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_tenant_{tenant_id}
                ON content (user_id, created_at) 
                WHERE user_id IN (SELECT id FROM users WHERE tenant_id = '{tenant_id}')
                """
            ]
            
            for index_sql in tenant_indexes:
                try:
                    async with engine.begin() as conn:
                        await conn.execute(text(index_sql))
                    created_indexes.append(f"Created tenant-specific index for {tenant_id}")
                except Exception as e:
                    logger.warning(f"Failed to create tenant index: {e}")
        
        return created_indexes


class CostOptimizedIndexManager:
    """Cost-optimized index management"""
    
    def __init__(self, base_optimizer: IndexOptimizer):
        self.base_optimizer = base_optimizer
        self.cost_models: Dict[str, Any] = {}
        
    async def optimize_index_costs(self, engine: AsyncEngine, 
                                 budget_constraint: float = 100.0) -> List[Dict[str, Any]]:
        """Optimize indexes within budget constraints (in MB)"""
        try:
            # Get current index costs
            current_indexes = await self._get_index_costs(engine)
            
            # Calculate total current cost
            total_current_cost = sum(idx['size_mb'] for idx in current_indexes.values())
            
            if total_current_cost <= budget_constraint:
                return [{'action': 'no_optimization_needed', 'current_cost': total_current_cost}]
            
            # Optimize within budget
            optimizations = []
            
            # Sort indexes by cost-benefit ratio
            sorted_indexes = sorted(
                current_indexes.items(),
                key=lambda x: x[1]['usage_count'] / max(x[1]['size_mb'], 0.1),
                reverse=True
            )
            
            # Keep high-value indexes, remove low-value ones
            target_cost = budget_constraint * 0.9  # 90% of budget
            current_cost = 0
            kept_indexes = []
            removed_indexes = []
            
            for index_name, index_info in sorted_indexes:
                if current_cost + index_info['size_mb'] <= target_cost:
                    current_cost += index_info['size_mb']
                    kept_indexes.append(index_name)
                else:
                    removed_indexes.append(index_name)
            
            # Remove low-value indexes
            for index_name in removed_indexes[:5]:  # Limit removals
                try:
                    drop_sql = f"DROP INDEX CONCURRENTLY IF EXISTS {index_name}"
                    async with engine.begin() as conn:
                        await conn.execute(text(drop_sql))
                    
                    optimizations.append({
                        'action': 'dropped_index',
                        'index_name': index_name,
                        'size_saved_mb': current_indexes[index_name]['size_mb']
                    })
                except Exception as e:
                    logger.warning(f"Failed to drop index {index_name}: {e}")
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Failed to optimize index costs: {e}")
            return []
    
    async def _get_index_costs(self, engine: AsyncEngine) -> Dict[str, Dict[str, Any]]:
        """Get index cost information"""
        query = text("""
            SELECT 
                indexname,
                idx_scan as usage_count,
                pg_relation_size(indexrelid) / (1024 * 1024) as size_mb
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY size_mb DESC
        """)
        
        costs = {}
        
        try:
            async with engine.begin() as conn:
                result = await conn.execute(query)
                
                for row in result:
                    costs[row.indexname] = {
                        'usage_count': row.usage_count or 0,
                        'size_mb': float(row.size_mb or 0)
                    }
            
            return costs
            
        except Exception as e:
            logger.error(f"Failed to get index costs: {e}")
            return {}


class AdvancedIndexStrategiesManager:
    """Main manager for advanced index strategies"""
    
    def __init__(self, base_optimizer: IndexOptimizer):
        self.base_optimizer = base_optimizer
        self.predictive_manager = PredictiveIndexManager(base_optimizer)
        self.adaptive_manager = AdaptiveIndexManager(base_optimizer)
        self.tenant_manager = TenantAwareIndexManager(base_optimizer)
        self.cost_manager = CostOptimizedIndexManager(base_optimizer)
        
        self.current_strategy = AdvancedIndexStrategy.ADAPTIVE
        self.strategy_history: List[Dict[str, Any]] = []
    
    async def execute_strategy(self, engine: AsyncEngine, 
                             strategy: AdvancedIndexStrategy,
                             parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute specific indexing strategy"""
        parameters = parameters or {}
        results = {'strategy': strategy.value, 'timestamp': datetime.now()}
        
        try:
            if strategy == AdvancedIndexStrategy.PREDICTIVE:
                workload_profile = parameters.get('workload_profile')
                if workload_profile:
                    recommendations = await self.predictive_manager.predict_index_needs(workload_profile)
                    results['recommendations'] = len(recommendations)
                    results['details'] = [r.description for r in recommendations]
            
            elif strategy == AdvancedIndexStrategy.ADAPTIVE:
                new_workload = parameters.get('new_workload')
                current_workload = parameters.get('current_workload')
                if new_workload and current_workload:
                    adaptations = await self.adaptive_manager.adapt_to_workload_changes(
                        engine, new_workload, current_workload
                    )
                    results['adaptations'] = adaptations
            
            elif strategy == AdvancedIndexStrategy.TENANT_AWARE:
                tenant_patterns = await self.tenant_manager.analyze_tenant_patterns(engine)
                results['tenant_patterns'] = len(tenant_patterns)
                
                # Create indexes for high-priority tenants
                high_priority_tenants = [
                    tid for tid, pattern in tenant_patterns.items() 
                    if pattern.get('priority') == 'high'
                ]
                
                created_indexes = []
                for tenant_id in high_priority_tenants[:5]:  # Limit to 5 tenants
                    indexes = await self.tenant_manager.create_tenant_specific_indexes(
                        engine, tenant_id, tenant_patterns[tenant_id]
                    )
                    created_indexes.extend(indexes)
                
                results['created_tenant_indexes'] = len(created_indexes)
            
            elif strategy == AdvancedIndexStrategy.COST_OPTIMIZED:
                budget = parameters.get('budget_mb', 100.0)
                optimizations = await self.cost_manager.optimize_index_costs(engine, budget)
                results['optimizations'] = optimizations
            
            # Record strategy execution
            self.strategy_history.append(results)
            self.current_strategy = strategy
            
            logger.info(f"Executed {strategy.value} strategy: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute {strategy.value} strategy: {e}")
            results['error'] = str(e)
            return results
    
    async def auto_select_strategy(self, engine: AsyncEngine) -> AdvancedIndexStrategy:
        """Automatically select best strategy based on current conditions"""
        try:
            # Analyze current database state
            index_stats = self.base_optimizer.get_stats()
            
            # Simple heuristics for strategy selection
            if index_stats.get('unused_indexes', 0) > 10:
                return AdvancedIndexStrategy.COST_OPTIMIZED
            
            elif index_stats.get('total_size_mb', 0) > 500:  # Large index footprint
                return AdvancedIndexStrategy.ADAPTIVE
            
            elif index_stats.get('query_patterns_analyzed', 0) > 100:
                return AdvancedIndexStrategy.PREDICTIVE
            
            else:
                return AdvancedIndexStrategy.TENANT_AWARE
                
        except Exception as e:
            logger.error(f"Failed to auto-select strategy: {e}")
            return AdvancedIndexStrategy.ADAPTIVE
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Get strategy execution statistics"""
        return {
            'current_strategy': self.current_strategy.value,
            'total_executions': len(self.strategy_history),
            'strategy_distribution': Counter(
                h['strategy'] for h in self.strategy_history
            ),
            'last_execution': self.strategy_history[-1] if self.strategy_history else None,
            'average_recommendations_per_execution': (
                sum(h.get('recommendations', 0) for h in self.strategy_history) / 
                len(self.strategy_history) if self.strategy_history else 0
            )
        }


# Export main class
__all__ = ['AdvancedIndexStrategiesManager', 'AdvancedIndexStrategy', 'WorkloadProfile']