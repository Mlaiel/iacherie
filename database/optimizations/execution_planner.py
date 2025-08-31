"""
Execution Planner Module

Advanced database execution planning system with cost-based optimization,
intelligent query rewriting, and adaptive execution strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import time
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import json
import statistics
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from ...core.logging import get_logger
from ...core.config import settings
from ...core.metrics import MetricsCollector

logger = get_logger(__name__)


class ExecutionStrategy(Enum):
    """Query execution strategies"""
    COST_BASED = "cost_based"
    RULE_BASED = "rule_based"
    ADAPTIVE = "adaptive"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    CACHED = "cached"


class PlanType(Enum):
    """Execution plan types"""
    EXPLAIN_ONLY = "explain_only"
    EXPLAIN_ANALYZE = "explain_analyze"
    EXECUTION = "execution"
    OPTIMIZATION = "optimization"


class OptimizationLevel(Enum):
    """Optimization levels"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    EXPERIMENTAL = "experimental"


@dataclass
class ExecutionNode:
    """Single node in execution plan"""
    node_id: str
    node_type: str
    operation: str
    table_name: Optional[str] = None
    index_name: Optional[str] = None
    cost: float = 0.0
    rows: int = 0
    width: int = 0
    startup_cost: float = 0.0
    total_cost: float = 0.0
    actual_time: Optional[float] = None
    actual_rows: Optional[int] = None
    children: List['ExecutionNode'] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    output_columns: List[str] = field(default_factory=list)
    
    @property
    def is_expensive(self) -> bool:
        """Check if node is expensive"""



        return self.total_cost > 1000 or (self.actual_time and self.actual_time > 100)
    
    @property
    def efficiency_ratio(self) -> float:
        """Calculate efficiency ratio"""
        if self.rows == 0:
            return 1.0
        estimated_rows = max(1, self.rows)
        actual_rows = self.actual_rows or estimated_rows
        return min(actual_rows / estimated_rows, estimated_rows / actual_rows)


@dataclass
class ExecutionStatistics:
    """Execution statistics and metrics"""
    query_id: str
    execution_time: float
    planning_time: float
    total_cost: float
    actual_cost: Optional[float] = None
    rows_processed: int = 0
    buffers_hit: int = 0
    buffers_read: int = 0
    buffers_dirtied: int = 0
    temp_read: int = 0
    temp_written: int = 0
    io_time: float = 0.0
    
    @property
    def buffer_hit_ratio(self) -> float:
        """Calculate buffer hit ratio"""
        total_buffers = self.buffers_hit + self.buffers_read
        if total_buffers == 0:
            return 0.0
        return self.buffers_hit / total_buffers
    
    @property
    def cost_accuracy(self) -> float:
        """Calculate cost estimation accuracy"""
        if self.actual_cost is None or self.total_cost == 0:
            return 0.0
        return 1.0 - abs(self.actual_cost - self.total_cost) / self.total_cost


@dataclass
class PlanOptimization:
    """Optimization suggestion for execution plan"""
    optimization_id: str
    type: str
    description: str
    estimated_improvement: float
    confidence: float
    original_cost: float
    optimized_cost: float
    implementation_complexity: str  # low, medium, high
    side_effects: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlanResult:
    """Complete execution plan with analysis"""
    plan_id: str
    query_text: str
    strategy: ExecutionStrategy
    optimization_level: OptimizationLevel
    root_node: ExecutionNode
    statistics: ExecutionStatistics
    optimizations: List[PlanOptimization] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_nodes(self) -> int:
        """Count total nodes in plan"""
        def count_nodes(node: ExecutionNode) -> int:
            return 1 + sum(count_nodes(child) for child in node.children)
        return count_nodes(self.root_node)
    
    @property
    def expensive_nodes(self) -> List[ExecutionNode]:
        """Get list of expensive nodes"""
        expensive = []
        
        def find_expensive(node: ExecutionNode):
            if node.is_expensive:
                expensive.append(node)
            for child in node.children:
                find_expensive(child)
        
        find_expensive(self.root_node)
        return expensive
    
    @property
    def table_scans(self) -> List[ExecutionNode]:
        """Get list of sequential scan nodes"""
        scans = []
        
        def find_scans(node: ExecutionNode):
            if 'Seq Scan' in node.node_type:
                scans.append(node)
            for child in node.children:
                find_scans(child)
        
        find_scans(self.root_node)
        return scans


class CostEstimator:
    """Advanced cost estimation for query operations"""
    
    def __init__(self):
        # Cost constants (can be tuned based on database configuration)
        self.seq_page_cost = 1.0
        self.random_page_cost = 4.0
        self.cpu_tuple_cost = 0.01
        self.cpu_index_tuple_cost = 0.005
        self.cpu_operator_cost = 0.0025
        
        # Statistics cache
        self._table_stats: Dict[str, Dict[str, Any]] = {}
        self._index_stats: Dict[str, Dict[str, Any]] = {}
    
    async def estimate_scan_cost(
        self,
        table_name: str,
        scan_type: str,
        conditions: List[str],
        engine: AsyncEngine
    ) -> float:
        """Estimate cost of table scan operation"""



        
        try:
            # Get table statistics
            stats = await self._get_table_statistics(table_name, engine)
            
            pages = stats.get('pages', 1000)
            tuples = stats.get('tuples', 10000)
            
            if scan_type == 'Seq Scan':
                # Sequential scan cost
                disk_cost = pages * self.seq_page_cost
                cpu_cost = tuples * self.cpu_tuple_cost
                
                # Apply selectivity for WHERE conditions
                selectivity = self._estimate_selectivity(conditions, stats)
                cpu_cost *= selectivity
                
                return disk_cost + cpu_cost
            
            elif 'Index' in scan_type:
                # Index scan cost
                index_pages = stats.get('index_pages', 100)
                selectivity = self._estimate_selectivity(conditions, stats)
                
                # Index access cost
                index_cost = index_pages * self.random_page_cost * selectivity
                
                # Tuple processing cost
                selected_tuples = tuples * selectivity
                cpu_cost = selected_tuples * self.cpu_index_tuple_cost
                
                return index_cost + cpu_cost
            
            else:
                # Default estimation
                return tuples * self.cpu_tuple_cost
                
        except Exception as e:
            logger.warning(f"Cost estimation failed for {table_name}: {e}")
            return 1000.0  # Default high cost
    
    async def estimate_join_cost(
        self,
        left_table: str,
        right_table: str,
        join_type: str,
        join_conditions: List[str],
        engine: AsyncEngine
    ) -> float:
        """Estimate cost of join operation"""



        
        try:
            left_stats = await self._get_table_statistics(left_table, engine)
            right_stats = await self._get_table_statistics(right_table, engine)
            
            left_tuples = left_stats.get('tuples', 1000)
            right_tuples = right_stats.get('tuples', 1000)
            
            if join_type == 'Nested Loop':
                # Nested loop join
                return left_tuples * right_tuples * self.cpu_tuple_cost
            
            elif join_type == 'Hash Join':
                # Hash join
                build_cost = min(left_tuples, right_tuples) * self.cpu_tuple_cost
                probe_cost = max(left_tuples, right_tuples) * self.cpu_tuple_cost
                return build_cost + probe_cost
            
            elif join_type == 'Merge Join':
                # Merge join (assuming pre-sorted)
                return (left_tuples + right_tuples) * self.cpu_tuple_cost
            
            else:
                # Default join cost
                return left_tuples * right_tuples * self.cpu_tuple_cost * 0.1
                
        except Exception as e:
            logger.warning(f"Join cost estimation failed: {e}")
            return 10000.0
    
    async def _get_table_statistics(self, table_name: str, engine: AsyncEngine) -> Dict[str, Any]:
        """Get table statistics from database"""
        if table_name in self._table_stats:
            return self._table_stats[table_name]
        
        try:
            async with engine.begin() as conn:
                # PostgreSQL statistics query
                stats_query = text("""
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as tuples,
                        n_dead_tup as dead_tuples,
                        last_vacuum,
                        last_analyze
                    FROM pg_stat_user_tables 
                    WHERE tablename = :table_name
                """)
                
                result = await conn.execute(stats_query, {"table_name": table_name})
                row = result.fetchone()
                
                if row:
                    stats = {
                        'tuples': row.tuples or 1000,
                        'dead_tuples': row.dead_tuples or 0,
                        'inserts': row.inserts or 0,
                        'updates': row.updates or 0,
                        'deletes': row.deletes or 0,
                    }
                    
                    # Get table size
                    size_query = text("""
                        SELECT 
                            pg_relation_size(:table_name) / 8192 as pages,
                            pg_total_relation_size(:table_name) as total_size
                    """)
                    
                    size_result = await conn.execute(size_query, {"table_name": table_name})
                    size_row = size_result.fetchone()
                    
                    if size_row:
                        stats['pages'] = size_row.pages or 100
                        stats['total_size'] = size_row.total_size or 819200
                    
                    self._table_stats[table_name] = stats
                    return stats
        
        except Exception as e:
            logger.warning(f"Failed to get statistics for {table_name}: {e}")
        
        # Default statistics
        default_stats = {
            'tuples': 1000,
            'pages': 100,
            'dead_tuples': 0,
            'total_size': 819200
        }
        
        self._table_stats[table_name] = default_stats
        return default_stats
    
    def _estimate_selectivity(self, conditions: List[str], table_stats: Dict[str, Any]) -> float:
        """Estimate selectivity of WHERE conditions"""
        if not conditions:
            return 1.0
        
        # Simple heuristic-based selectivity estimation
        base_selectivity = 1.0
        
        for condition in conditions:
            condition_lower = condition.lower()
            
            if '=' in condition_lower:
                # Equality condition - typically very selective
                base_selectivity *= 0.1
            elif 'like' in condition_lower:
                if condition_lower.startswith("'%"):
                    # Leading wildcard - less selective
                    base_selectivity *= 0.3
                else:
                    # Prefix match - more selective
                    base_selectivity *= 0.1
            elif any(op in condition_lower for op in ['<', '>', '<=', '>=']):
                # Range condition - moderately selective
                base_selectivity *= 0.3
            elif 'in' in condition_lower:
                # IN clause - depends on list size, assume moderate
                base_selectivity *= 0.2
            else:
                # Unknown condition type - conservative estimate
                base_selectivity *= 0.5
        
        return max(0.001, min(1.0, base_selectivity))


class PlanOptimizer:
    """Intelligent execution plan optimizer"""
    
    def __init__(self):
        self.cost_estimator = CostEstimator()
        self._optimization_rules = [
            self._optimize_sequential_scans,
            self._optimize_join_order,
            self._optimize_subqueries,
            self._optimize_aggregations,
            self._optimize_sorting,
        ]
    
    async def optimize_plan(
        self,
        plan: ExecutionPlanResult,
        engine: AsyncEngine,
        optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    ) -> List[PlanOptimization]:
        """Generate optimization suggestions for execution plan"""
        
        optimizations = []
        
        for rule in self._optimization_rules:
            try:
                rule_optimizations = await rule(plan, engine, optimization_level)
                optimizations.extend(rule_optimizations)
            except Exception as e:
                logger.warning(f"Optimization rule failed: {e}")
        
        # Sort by estimated improvement
        optimizations.sort(key=lambda x: x.estimated_improvement, reverse=True)
        
        return optimizations
    
    async def _optimize_sequential_scans(
        self,
        plan: ExecutionPlanResult,
        engine: AsyncEngine,
        optimization_level: OptimizationLevel
    ) -> List[PlanOptimization]:
        """Optimize sequential scans"""
        optimizations = []
        
        for scan_node in plan.table_scans:
            if scan_node.table_name and scan_node.conditions:
                # Suggest index for WHERE conditions
                optimization = PlanOptimization(
                    optimization_id=f"index_{scan_node.table_name}_{hash(str(scan_node.conditions))}",
                    type="index_creation",
                    description=f"Create index on {scan_node.table_name} for conditions: {', '.join(scan_node.conditions)}",
                    estimated_improvement=50.0,  # Assume 50% improvement
                    confidence=0.8,
                    original_cost=scan_node.total_cost,
                    optimized_cost=scan_node.total_cost * 0.5,
                    implementation_complexity="medium",
                    prerequisites=[f"Analyze column statistics for {scan_node.table_name}"]
                )
                optimizations.append(optimization)
        
        return optimizations
    
    async def _optimize_join_order(
        self,
        plan: ExecutionPlanResult,
        engine: AsyncEngine,
        optimization_level: OptimizationLevel
    ) -> List[PlanOptimization]:
        """Optimize join order"""
        optimizations = []
        
        # Find join nodes
        join_nodes = self._find_join_nodes(plan.root_node)
        
        if len(join_nodes) > 2:  # Only optimize if multiple joins
            optimization = PlanOptimization(
                optimization_id=f"join_order_{plan.plan_id}",
                type="join_order",
                description="Consider reordering joins to reduce intermediate result size",
                estimated_improvement=25.0,
                confidence=0.6,
                original_cost=sum(node.total_cost for node in join_nodes),
                optimized_cost=sum(node.total_cost for node in join_nodes) * 0.75,
                implementation_complexity="high",
                side_effects=["May change query semantics in some edge cases"]
            )
            optimizations.append(optimization)
        
        return optimizations
    
    async def _optimize_subqueries(
        self,
        plan: ExecutionPlanResult,
        engine: AsyncEngine,
        optimization_level: OptimizationLevel
    ) -> List[PlanOptimization]:
        """Optimize subqueries"""
        optimizations = []
        
        # Find subquery nodes
        subquery_nodes = self._find_subquery_nodes(plan.root_node)
        
        for subquery_node in subquery_nodes:
            if subquery_node.is_expensive:
                optimization = PlanOptimization(
                    optimization_id=f"subquery_{subquery_node.node_id}",
                    type="subquery_optimization",
                    description="Convert correlated subquery to JOIN for better performance",
                    estimated_improvement=40.0,
                    confidence=0.7,
                    original_cost=subquery_node.total_cost,
                    optimized_cost=subquery_node.total_cost * 0.6,
                    implementation_complexity="medium"
                )
                optimizations.append(optimization)
        
        return optimizations
    
    async def _optimize_aggregations(
        self,
        plan: ExecutionPlanResult,
        engine: AsyncEngine,
        optimization_level: OptimizationLevel
    ) -> List[PlanOptimization]:
        """Optimize aggregation operations"""
        optimizations = []
        
        # Find aggregation nodes
        agg_nodes = self._find_aggregation_nodes(plan.root_node)
        
        for agg_node in agg_nodes:
            if agg_node.rows > 100000:  # Large aggregation
                optimization = PlanOptimization(
                    optimization_id=f"aggregation_{agg_node.node_id}",
                    type="aggregation_optimization",
                    description="Consider partial aggregation or materialized view for large aggregations",
                    estimated_improvement=30.0,
                    confidence=0.6,
                    original_cost=agg_node.total_cost,
                    optimized_cost=agg_node.total_cost * 0.7,
                    implementation_complexity="high",
                    prerequisites=["Evaluate aggregation frequency and data freshness requirements"]
                )
                optimizations.append(optimization)
        
        return optimizations
    
    async def _optimize_sorting(
        self,
        plan: ExecutionPlanResult,
        engine: AsyncEngine,
        optimization_level: OptimizationLevel
    ) -> List[PlanOptimization]:
        """Optimize sorting operations"""
        optimizations = []
        
        # Find sort nodes
        sort_nodes = self._find_sort_nodes(plan.root_node)
        
        for sort_node in sort_nodes:
            if sort_node.rows > 50000:  # Large sort
                optimization = PlanOptimization(
                    optimization_id=f"sort_{sort_node.node_id}",
                    type="sorting_optimization",
                    description="Create index to eliminate sort operation",
                    estimated_improvement=20.0,
                    confidence=0.8,
                    original_cost=sort_node.total_cost,
                    optimized_cost=sort_node.total_cost * 0.8,
                    implementation_complexity="low"
                )
                optimizations.append(optimization)
        
        return optimizations
    
    def _find_join_nodes(self, node: ExecutionNode) -> List[ExecutionNode]:
        """Find all join nodes in execution plan"""
        joins = []
        
        if 'Join' in node.node_type:
            joins.append(node)
        
        for child in node.children:
            joins.extend(self._find_join_nodes(child))
        
        return joins
    
    def _find_subquery_nodes(self, node: ExecutionNode) -> List[ExecutionNode]:
        """Find all subquery nodes in execution plan"""
        subqueries = []
        
        if 'SubPlan' in node.node_type or 'InitPlan' in node.node_type:
            subqueries.append(node)
        
        for child in node.children:
            subqueries.extend(self._find_subquery_nodes(child))
        
        return subqueries
    
    def _find_aggregation_nodes(self, node: ExecutionNode) -> List[ExecutionNode]:
        """Find all aggregation nodes in execution plan"""
        aggregations = []
        
        if any(agg in node.node_type for agg in ['Aggregate', 'Group', 'HashAggregate']):
            aggregations.append(node)
        
        for child in node.children:
            aggregations.extend(self._find_aggregation_nodes(child))
        
        return aggregations
    
    def _find_sort_nodes(self, node: ExecutionNode) -> List[ExecutionNode]:
        """Find all sort nodes in execution plan"""
        sorts = []
        
        if 'Sort' in node.node_type:
            sorts.append(node)
        
        for child in node.children:
            sorts.extend(self._find_sort_nodes(child))
        
        return sorts


class ExecutionPlanner:
    """Advanced database execution planner"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics_collector = MetricsCollector()
        self.cost_estimator = CostEstimator()
        self.optimizer = PlanOptimizer()
        
        # Plan cache
        self._plan_cache: Dict[str, ExecutionPlanResult] = {}
        self._execution_history: List[ExecutionStatistics] = []
        
        # Configuration
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_ttl_minutes = self.config.get('cache_ttl_minutes', 60)
        self.max_cache_size = self.config.get('max_cache_size', 1000)
    
    async def create_execution_plan(
        self,
        query: str,
        strategy: ExecutionStrategy = ExecutionStrategy.ADAPTIVE,
        optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
        engine: Optional[AsyncEngine] = None
    ) -> ExecutionPlanResult:
        """Create optimized execution plan for query"""
        
        plan_id = self._generate_plan_id(query, strategy, optimization_level)
        
        # Check cache
        if self.cache_enabled and plan_id in self._plan_cache:
            cached_plan = self._plan_cache[plan_id]
            if self._is_plan_valid(cached_plan):
                logger.debug(f"Using cached execution plan: {plan_id}")
                return cached_plan
        
        try:
            logger.info(f"Creating execution plan: {strategy.value} - {optimization_level.value}")
            
            # Get execution plan from database
            if engine:
                raw_plan = await self._get_database_plan(query, engine)
                root_node = self._parse_plan_tree(raw_plan)
                
                # Extract statistics
                statistics = self._extract_statistics(raw_plan, query)
            else:
                # Create mock plan for testing
                root_node = self._create_mock_plan(query)
                statistics = ExecutionStatistics(
                    query_id=plan_id,
                    execution_time=0.0,
                    planning_time=0.0,
                    total_cost=1000.0
                )
            
            # Create plan result
            plan_result = ExecutionPlanResult(
                plan_id=plan_id,
                query_text=query,
                strategy=strategy,
                optimization_level=optimization_level,
                root_node=root_node,
                statistics=statistics
            )
            
            # Generate optimizations
            if engine:
                plan_result.optimizations = await self.optimizer.optimize_plan(
                    plan_result, engine, optimization_level
                )
            
            # Add warnings
            plan_result.warnings = self._generate_warnings(plan_result)
            
            # Cache the plan
            if self.cache_enabled:
                self._cache_plan(plan_result)
            
            # Send metrics
            await self._send_plan_metrics(plan_result)
            
            return plan_result
            
        except Exception as e:
            logger.error(f"Failed to create execution plan: {e}")
            raise
    
    async def execute_with_plan(
        self,
        query: str,
        engine: AsyncEngine,
        strategy: ExecutionStrategy = ExecutionStrategy.ADAPTIVE
    ) -> Tuple[Any, ExecutionStatistics]:
        """Execute query with optimal execution plan"""
        
        start_time = time.time()
        
        try:
            # Create execution plan
            plan = await self.create_execution_plan(query, strategy, engine=engine)
            
            planning_time = time.time() - start_time
            execution_start = time.time()
            
            # Execute query
            async with engine.begin() as conn:
                result = await conn.execute(text(query))
                execution_time = time.time() - execution_start
                
                # Update statistics
                plan.statistics.execution_time = execution_time
                plan.statistics.planning_time = planning_time
                
                # Record execution history
                self._execution_history.append(plan.statistics)
                
                return result, plan.statistics
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def _get_database_plan(self, query: str, engine: AsyncEngine) -> Dict[str, Any]:
        """Get execution plan from database"""



        try:
            async with engine.begin() as conn:
                # Get detailed execution plan
                explain_query = f"EXPLAIN (ANALYZE false, VERBOSE true, BUFFERS true, FORMAT JSON) {query}"
                result = await conn.execute(text(explain_query))
                plan_data = result.fetchone()[0]
                
                if isinstance(plan_data, list) and plan_data:
                    return plan_data[0]
                
                return plan_data
                
        except Exception as e:
            logger.error(f"Failed to get database plan: {e}")
            raise
    
    def _parse_plan_tree(self, plan_data: Dict[str, Any]) -> ExecutionNode:
        """Parse database plan into execution tree"""
        plan_info = plan_data.get('Plan', {})
        
        root_node = self._parse_plan_node(plan_info)
        return root_node
    
    def _parse_plan_node(self, node_data: Dict[str, Any]) -> ExecutionNode:
        """Parse single plan node"""
        node = ExecutionNode(
            node_id=str(hash(str(node_data))),
            node_type=node_data.get('Node Type', 'Unknown'),
            operation=node_data.get('Node Type', 'Unknown'),
            table_name=node_data.get('Relation Name'),
            index_name=node_data.get('Index Name'),
            cost=node_data.get('Total Cost', 0.0),
            rows=node_data.get('Plan Rows', 0),
            width=node_data.get('Plan Width', 0),
            startup_cost=node_data.get('Startup Cost', 0.0),
            total_cost=node_data.get('Total Cost', 0.0),
            actual_time=node_data.get('Actual Total Time'),
            actual_rows=node_data.get('Actual Rows')
        )
        
        # Parse conditions
        if 'Filter' in node_data:
            node.conditions.append(node_data['Filter'])
        if 'Index Cond' in node_data:
            node.conditions.append(node_data['Index Cond'])
        if 'Hash Cond' in node_data:
            node.conditions.append(node_data['Hash Cond'])
        
        # Parse child nodes
        for child_data in node_data.get('Plans', []):
            child_node = self._parse_plan_node(child_data)
            node.children.append(child_node)
        
        return node
    
    def _create_mock_plan(self, query: str) -> ExecutionNode:
        """Create mock execution plan for testing"""



        return ExecutionNode(
            node_id="mock_root",
            node_type="Seq Scan",
            operation="Scan",
            table_name="mock_table",
            cost=1000.0,
            rows=1000,
            total_cost=1000.0
        )
    
    def _extract_statistics(self, plan_data: Dict[str, Any], query: str) -> ExecutionStatistics:
        """Extract execution statistics from plan"""
        query_id = hashlib.md5(query.encode()).hexdigest()
        
        stats = ExecutionStatistics(
            query_id=query_id,
            execution_time=plan_data.get('Execution Time', 0.0),
            planning_time=plan_data.get('Planning Time', 0.0),
            total_cost=plan_data.get('Plan', {}).get('Total Cost', 0.0)
        )
        
        # Extract buffer statistics if available
        plan_info = plan_data.get('Plan', {})
        if 'Shared Hit Blocks' in plan_info:
            stats.buffers_hit = plan_info['Shared Hit Blocks']
        if 'Shared Read Blocks' in plan_info:
            stats.buffers_read = plan_info['Shared Read Blocks']
        if 'Shared Dirtied Blocks' in plan_info:
            stats.buffers_dirtied = plan_info['Shared Dirtied Blocks']
        
        return stats
    
    def _generate_warnings(self, plan: ExecutionPlanResult) -> List[str]:
        """Generate warnings based on execution plan analysis"""
        warnings = []
        
        # Check for expensive operations
        expensive_nodes = plan.expensive_nodes
        if expensive_nodes:
            warnings.append(f"Found {len(expensive_nodes)} expensive operations")
        
        # Check for table scans
        table_scans = plan.table_scans
        if table_scans:
            warnings.append(f"Found {len(table_scans)} sequential table scans")
        
        # Check for high cost
        if plan.statistics.total_cost > 10000:
            warnings.append("Query has very high estimated cost")
        
        # Check for large result sets
        if plan.root_node.rows > 100000:
            warnings.append("Query may return very large result set")
        
        return warnings
    
    def _generate_plan_id(
        self,
        query: str,
        strategy: ExecutionStrategy,
        optimization_level: OptimizationLevel
    ) -> str:
        """Generate unique plan ID"""
        plan_key = f"{query}_{strategy.value}_{optimization_level.value}"
        return hashlib.md5(plan_key.encode()).hexdigest()
    
    def _is_plan_valid(self, plan: ExecutionPlanResult) -> bool:
        """Check if cached plan is still valid"""
        if not self.cache_enabled:
            return False
        
        age = datetime.now() - plan.created_at
        return age.total_seconds() < (self.cache_ttl_minutes * 60)
    
    def _cache_plan(self, plan: ExecutionPlanResult) -> None:
        """Cache execution plan"""
        if len(self._plan_cache) >= self.max_cache_size:
            # Remove oldest plan
            oldest_plan_id = min(
                self._plan_cache.keys(),
                key=lambda k: self._plan_cache[k].created_at
            )
            del self._plan_cache[oldest_plan_id]
        
        self._plan_cache[plan.plan_id] = plan
    
    async def _send_plan_metrics(self, plan: ExecutionPlanResult) -> None:
        """Send plan metrics to monitoring system"""



        try:
            self.metrics_collector.histogram(
                "execution_plan_cost",
                plan.statistics.total_cost,
                {"strategy": plan.strategy.value}
            )
            
            self.metrics_collector.histogram(
                "execution_plan_nodes",
                plan.total_nodes
            )
            
            self.metrics_collector.counter(
                "execution_plan_warnings_total",
                len(plan.warnings)
            )
            
        except Exception as e:
            logger.warning(f"Failed to send plan metrics: {e}")
    
    def get_plan_statistics(self) -> Dict[str, Any]:
        """Get execution planner statistics"""



        return {
            "cached_plans": len(self._plan_cache),
            "execution_history_count": len(self._execution_history),
            "avg_planning_time": statistics.mean([
                stat.planning_time for stat in self._execution_history
            ]) if self._execution_history else 0.0,
            "avg_execution_time": statistics.mean([
                stat.execution_time for stat in self._execution_history
            ]) if self._execution_history else 0.0,
            "avg_total_cost": statistics.mean([
                stat.total_cost for stat in self._execution_history
            ]) if self._execution_history else 0.0,
        }
    
    def clear_cache(self, older_than_minutes: int = 60) -> None:
        """Clear old cached plans"""
        cutoff_time = datetime.now() - timedelta(minutes=older_than_minutes)
        
        old_plans = [
            plan_id for plan_id, plan in self._plan_cache.items()
            if plan.created_at < cutoff_time
        ]
        
        for plan_id in old_plans:
            del self._plan_cache[plan_id]
        
        logger.info(f"Cleared {len(old_plans)} old execution plans from cache")


# Global execution planner instance
_execution_planner: Optional[ExecutionPlanner] = None


def get_execution_planner(config: Optional[Dict[str, Any]] = None) -> ExecutionPlanner:
    """Get global execution planner instance"""
    global _execution_planner
    
    if _execution_planner is None:
        _execution_planner = ExecutionPlanner(config)
    
    return _execution_planner


class ContentProtectionExecutionPlanner:
    """Specialized execution planner for content protection operations"""
    
    def __init__(self, base_planner: ExecutionPlanner):
        self.base_planner = base_planner
        self.fingerprint_strategies = {
            'similarity_search': ExecutionStrategy.PARALLEL,
            'bulk_fingerprint': ExecutionStrategy.BATCH,
            'duplicate_detection': ExecutionStrategy.ADAPTIVE
        }
    
    async def plan_fingerprint_search(
        self,
        similarity_threshold: float,
        content_type: str,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for fingerprint similarity search"""
        
        # Optimized query for vector similarity
        query = f"""
        WITH similar_fingerprints AS (
            SELECT cf.id, cf.fingerprint_hash, cf.user_id,
                   cf.vector_embedding <-> %s AS distance
            FROM content_fingerprints cf
            WHERE cf.content_type = '{content_type}'
              AND cf.vector_embedding <-> %s < {1.0 - similarity_threshold}
            ORDER BY distance
            LIMIT 100
        )
        SELECT sf.*, cm.original_filename
        FROM similar_fingerprints sf
        JOIN content_metadata cm ON sf.id = cm.fingerprint_id
        """
        
        strategy = self.fingerprint_strategies['similarity_search']
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.AGGRESSIVE, engine
        )
    
    async def plan_bulk_fingerprint_insert(
        self,
        batch_size: int,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for bulk fingerprint insertion"""
        
        # Optimized bulk insert with conflict resolution
        query = f"""
        INSERT INTO content_fingerprints 
        (user_id, content_type, original_filename, fingerprint_hash, 
         vector_embedding, metadata, created_at)
        VALUES (unnest(%s), unnest(%s), unnest(%s), unnest(%s), 
                unnest(%s), unnest(%s), unnest(%s))
        ON CONFLICT (fingerprint_hash) DO UPDATE SET
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        RETURNING id, fingerprint_hash
        """
        
        strategy = self.fingerprint_strategies['bulk_fingerprint']
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.AGGRESSIVE, engine
        )
    
    async def plan_protection_alert_query(
        self,
        user_id: int,
        platform: str,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for protection alert queries"""
        
        query = f"""
        SELECT pa.*, cf.original_filename, cf.content_type
        FROM protection_alerts pa
        JOIN content_fingerprints cf ON pa.fingerprint_id = cf.id
        WHERE cf.user_id = {user_id}
          AND (pa.platform = '{platform}' OR pa.platform IS NULL)
          AND pa.status IN ('pending', 'investigating')
        ORDER BY pa.similarity_score DESC, pa.created_at DESC
        LIMIT 50
        """
        
        strategy = ExecutionStrategy.ADAPTIVE
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.STANDARD, engine
        )


class MonetizationExecutionPlanner:
    """Specialized execution planner for monetization operations"""
    
    def __init__(self, base_planner: ExecutionPlanner):
        self.base_planner = base_planner
        self.revenue_strategies = {
            'aggregation': ExecutionStrategy.PARALLEL,
            'reporting': ExecutionStrategy.ADAPTIVE,
            'analytics': ExecutionStrategy.BATCH
        }
    
    async def plan_revenue_aggregation(
        self,
        user_id: int,
        start_date: str,
        end_date: str,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for revenue aggregation"""
        
        query = f"""
        WITH revenue_summary AS (
            SELECT 
                platform,
                currency,
                SUM(revenue_amount) as total_revenue,
                COUNT(*) as transaction_count,
                AVG(revenue_amount) as avg_revenue,
                MIN(period_start) as first_period,
                MAX(period_end) as last_period
            FROM revenue_tracking
            WHERE user_id = {user_id}
              AND period_start >= '{start_date}'
              AND period_end <= '{end_date}'
            GROUP BY platform, currency
        ),
        converted_revenue AS (
            SELECT *,
                CASE 
                    WHEN currency = 'USD' THEN total_revenue
                    WHEN currency = 'EUR' THEN total_revenue * 1.1
                    WHEN currency = 'GBP' THEN total_revenue * 1.25
                    ELSE total_revenue
                END as total_revenue_usd
            FROM revenue_summary
        )
        SELECT platform, 
               SUM(total_revenue_usd) as platform_revenue_usd,
               SUM(transaction_count) as total_transactions
        FROM converted_revenue
        GROUP BY platform
        ORDER BY platform_revenue_usd DESC
        """
        
        strategy = self.revenue_strategies['aggregation']
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.AGGRESSIVE, engine
        )
    
    async def plan_analytics_report(
        self,
        report_type: str,
        aggregation_period: str,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for analytics reporting"""
        
        time_grouping = {
            'daily': "DATE_TRUNC('day', timestamp)",
            'weekly': "DATE_TRUNC('week', timestamp)",
            'monthly': "DATE_TRUNC('month', timestamp)"
        }.get(aggregation_period, "DATE_TRUNC('day', timestamp)")
        
        query = f"""
        SELECT 
            {time_grouping} as period,
            platform,
            metric_type,
            SUM(metric_value) as total_value,
            AVG(metric_value) as avg_value,
            COUNT(*) as data_points
        FROM creator_analytics
        WHERE aggregation_period = '{aggregation_period}'
          AND timestamp >= NOW() - INTERVAL '90 days'
        GROUP BY {time_grouping}, platform, metric_type
        ORDER BY period DESC, total_value DESC
        """
        
        strategy = self.revenue_strategies['analytics']
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.STANDARD, engine
        )
    
    async def plan_revenue_projection(
        self,
        user_id: int,
        prediction_days: int,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for revenue projection calculations"""
        
        query = f"""
        WITH historical_revenue AS (
            SELECT 
                platform,
                DATE_TRUNC('day', period_start) as revenue_date,
                SUM(revenue_amount) as daily_revenue
            FROM revenue_tracking
            WHERE user_id = {user_id}
              AND period_start >= NOW() - INTERVAL '30 days'
            GROUP BY platform, DATE_TRUNC('day', period_start)
        ),
        trend_analysis AS (
            SELECT 
                platform,
                AVG(daily_revenue) as avg_daily_revenue,
                STDDEV(daily_revenue) as revenue_stddev,
                REGR_SLOPE(daily_revenue, EXTRACT(EPOCH FROM revenue_date)) as growth_rate
            FROM historical_revenue
            GROUP BY platform
        )
        SELECT 
            platform,
            avg_daily_revenue,
            growth_rate,
            avg_daily_revenue * {prediction_days} + 
            (growth_rate * {prediction_days} * ({prediction_days} - 1) / 2) as projected_revenue
        FROM trend_analysis
        WHERE avg_daily_revenue > 0
        ORDER BY projected_revenue DESC
        """
        
        strategy = ExecutionStrategy.ADAPTIVE
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.STANDARD, engine
        )


class MultimediaExecutionPlanner:
    """Specialized execution planner for multimedia content operations"""
    
    def __init__(self, base_planner: ExecutionPlanner):
        self.base_planner = base_planner
        self.multimedia_strategies = {
            'content_search': ExecutionStrategy.ADAPTIVE,
            'metadata_aggregation': ExecutionStrategy.PARALLEL,
            'bulk_processing': ExecutionStrategy.BATCH
        }
    
    async def plan_content_search(
        self,
        user_id: int,
        content_type: str,
        filters: Dict[str, Any],
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for multimedia content search"""
        
        # Build dynamic filters
        filter_conditions = []
        if filters.get('min_duration'):
            filter_conditions.append(f"cm.duration >= {filters['min_duration']}")
        if filters.get('max_file_size'):
            filter_conditions.append(f"cm.file_size <= {filters['max_file_size']}")
        if filters.get('format'):
            filter_conditions.append(f"cm.format = '{filters['format']}'")
        
        additional_filters = " AND " + " AND ".join(filter_conditions) if filter_conditions else ""
        
        query = f"""
        SELECT cm.*, cf.fingerprint_hash
        FROM content_metadata cm
        LEFT JOIN content_fingerprints cf ON cm.id = cf.content_id
        WHERE cm.user_id = {user_id}
          AND cm.content_type = '{content_type}'
          {additional_filters}
        ORDER BY cm.created_at DESC
        LIMIT 100
        """
        
        strategy = self.multimedia_strategies['content_search']
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.STANDARD, engine
        )
    
    async def plan_metadata_aggregation(
        self,
        content_type: str,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for content metadata aggregation"""
        
        query = f"""
        SELECT 
            format,
            COUNT(*) as file_count,
            AVG(file_size) as avg_file_size,
            SUM(file_size) as total_file_size,
            AVG(duration) as avg_duration,
            MIN(duration) as min_duration,
            MAX(duration) as max_duration
        FROM content_metadata
        WHERE content_type = '{content_type}'
          AND created_at >= NOW() - INTERVAL '30 days'
        GROUP BY format
        ORDER BY file_count DESC
        """
        
        strategy = self.multimedia_strategies['metadata_aggregation']
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.STANDARD, engine
        )
    
    async def plan_bulk_content_processing(
        self,
        batch_size: int,
        content_type: str,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for bulk content processing"""
        
        query = f"""
        WITH unprocessed_content AS (
            SELECT id, file_path, format, file_size
            FROM content_metadata
            WHERE content_type = '{content_type}'
              AND metadata->>'processing_status' IS NULL
              OR metadata->>'processing_status' = 'pending'
            ORDER BY created_at ASC
            LIMIT {batch_size}
        )
        UPDATE content_metadata
        SET metadata = metadata || '{{"processing_status": "in_progress"}}'::jsonb,
            updated_at = NOW()
        FROM unprocessed_content
        WHERE content_metadata.id = unprocessed_content.id
        RETURNING content_metadata.id, content_metadata.file_path
        """
        
        strategy = self.multimedia_strategies['bulk_processing']
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.AGGRESSIVE, engine
        )


class AIProcessingExecutionPlanner:
    """Specialized execution planner for AI processing operations"""
    
    def __init__(self, base_planner: ExecutionPlanner):
        self.base_planner = base_planner
        self.ai_strategies = {
            'model_inference': ExecutionStrategy.PARALLEL,
            'feature_extraction': ExecutionStrategy.BATCH,
            'training_data': ExecutionStrategy.ADAPTIVE
        }
    
    async def plan_model_inference_batch(
        self,
        model_id: str,
        batch_size: int,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for batch model inference"""
        
        query = f"""
        WITH inference_batch AS (
            SELECT id, vector_data, content_id
            FROM vector_embeddings
            WHERE model_version = '{model_id}'
              AND metadata->>'inference_status' IS NULL
            ORDER BY created_at ASC
            LIMIT {batch_size}
        )
        SELECT ib.*, cm.content_type, cm.metadata
        FROM inference_batch ib
        JOIN content_metadata cm ON ib.content_id = cm.id
        """
        
        strategy = self.ai_strategies['model_inference']
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.AGGRESSIVE, engine
        )
    
    async def plan_feature_extraction(
        self,
        content_type: str,
        extraction_type: str,
        engine: AsyncEngine
    ) -> ExecutionPlanResult:
        """Plan execution for feature extraction operations"""
        
        query = f"""
        SELECT cm.id, cm.file_path, cm.metadata,
               cf.fingerprint_hash, cf.vector_embedding
        FROM content_metadata cm
        LEFT JOIN content_fingerprints cf ON cm.id = cf.content_id
        WHERE cm.content_type = '{content_type}'
          AND (cm.metadata->>'features_extracted' IS NULL 
               OR cm.metadata->>'features_extracted' != '{extraction_type}')
        ORDER BY cm.file_size ASC
        LIMIT 50
        """
        
        strategy = self.ai_strategies['feature_extraction']
        return await self.base_planner.create_execution_plan(
            query, strategy, OptimizationLevel.STANDARD, engine
        )
