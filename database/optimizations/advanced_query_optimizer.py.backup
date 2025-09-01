"""Advanced Query Optimization Module

Enhanced query optimization with machine learning-based cost estimation,
adaptive query rewriting, and intelligent execution plan optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import re
import json
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from .query_optimizer import QueryOptimizer, QueryPlan, OptimizationSuggestion, OptimizationType
from ...core.logging import get_logger

logger = get_logger(__name__)


class OptimizationLevel(Enum):
    """Query optimization levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"


class QueryComplexity(Enum):
    """Query complexity classification"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class QueryPerformanceMetrics:
    """Query performance metrics"""
    execution_time: float
    rows_examined: int
    rows_returned: int
    index_usage_count: int
    table_scan_count: int
    join_count: int
    memory_usage: float
    cpu_usage: float
    io_cost: float


@dataclass
class OptimizationResult:
    """Query optimization result"""
    original_query: str
    optimized_query: str
    optimization_level: OptimizationLevel
    estimated_improvement: float
    optimizations_applied: List[str]
    warnings: List[str]
    execution_plan_changes: Dict[str, Any]


class MLQueryCostEstimator:
    """Machine learning-based query cost estimation"""
    
    def __init__(self):
        self.feature_weights = {
            'table_count': 2.0,
            'join_count': 5.0,
            'where_conditions': 1.5,
            'subquery_count': 8.0,
            'function_count': 3.0,
            'order_by_count': 2.0,
            'group_by_count': 4.0,
            'having_count': 3.0,
            'limit_factor': -1.0,  # LIMIT reduces cost
            'index_availability': -2.0  # Available indexes reduce cost
        }
        self.historical_costs: List[Dict[str, Any]] = []
        
    def extract_features(self, query_plan: QueryPlan) -> Dict[str, float]:
        """Extract features from query plan for cost estimation"""
        components = query_plan.components
        
        features = {
            'table_count': float(len(components.tables)),
            'join_count': float(len(components.joins)),
            'where_conditions': float(len(components.where_conditions)),
            'subquery_count': float(len(components.subqueries)),
            'function_count': float(len(components.functions)),
            'order_by_count': float(len(components.order_by)),
            'group_by_count': float(len(components.group_by)),
            'having_count': float(len(components.having_conditions)),
            'limit_factor': 1.0 if components.limits else 0.0,
            'index_availability': 0.0  # Will be updated based on available indexes
        }
        
        return features
    
    def estimate_cost(self, features: Dict[str, float]) -> float:
        """Estimate query cost using weighted features"""
        cost = 1.0  # Base cost
        
        for feature, value in features.items():
            weight = self.feature_weights.get(feature, 1.0)
            
            if feature == 'join_count' and value > 0:
                # Exponential cost for joins
                cost += weight * (2 ** value)
            elif feature == 'subquery_count' and value > 0:
                # High cost for subqueries
                cost += weight * value * 10
            else:
                cost += weight * value
        
        return max(cost, 1.0)
    
    def learn_from_execution(self, query_plan: QueryPlan, actual_cost: float):
        """Learn from actual query execution"""
        features = self.extract_features(query_plan)
        
        self.historical_costs.append({
            'timestamp': datetime.now(),
            'features': features,
            'actual_cost': actual_cost,
            'query_complexity': self._classify_complexity(query_plan)
        })
        
        # Keep only recent history
        if len(self.historical_costs) > 1000:
            self.historical_costs = self.historical_costs[-800:]
        
        # Update weights based on recent performance
        self._update_weights()
    
    def _classify_complexity(self, query_plan: QueryPlan) -> QueryComplexity:
        """Classify query complexity"""
        score = query_plan.components.complexity_score
        
        if score <= 10:
            return QueryComplexity.SIMPLE
        elif score <= 25:
            return QueryComplexity.MODERATE
        elif score <= 50:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.VERY_COMPLEX
    
    def _update_weights(self):
        """Update feature weights based on historical performance"""
        if len(self.historical_costs) < 10:
            return
        
        # Simple weight adjustment based on recent performance
        recent_costs = self.historical_costs[-50:]
        
        for feature in self.feature_weights:
            feature_values = [c['features'].get(feature, 0) for c in recent_costs]
            actual_costs = [c['actual_cost'] for c in recent_costs]
            
            if len(set(feature_values)) > 1:  # Only if feature varies
                # Calculate correlation (simplified)
                correlation = np.corrcoef(feature_values, actual_costs)[0, 1]
                if not np.isnan(correlation):
                    # Adjust weight slightly based on correlation
                    adjustment = correlation * 0.1
                    self.feature_weights[feature] *= (1 + adjustment)


class AdaptiveQueryRewriter:
    """Adaptive query rewriting system"""
    
    def __init__(self):
        self.rewrite_patterns = [
            self._rewrite_or_to_union,
            self._rewrite_exists_to_join,
            self._rewrite_subquery_to_cte,
            self._rewrite_case_to_filter,
            self._optimize_window_functions,
            self._optimize_aggregations,
            self._rewrite_inefficient_joins
        ]
        self.rewrite_success_rates: Dict[str, float] = {}
        
    async def rewrite_query(self, query: str, optimization_level: OptimizationLevel) -> str:
        """Rewrite query based on optimization level"""
        try:
            original_query = query
            current_query = query
            applied_rewrites = []
            
            # Apply rewrites based on optimization level
            patterns_to_apply = self._get_patterns_for_level(optimization_level)
            
            for pattern_func in patterns_to_apply:
                try:
                    rewritten = pattern_func(current_query)
                    if rewritten != current_query:
                        current_query = rewritten
                        applied_rewrites.append(pattern_func.__name__)
                except Exception as e:
                    logger.warning(f"Rewrite pattern {pattern_func.__name__} failed: {e}")
            
            if applied_rewrites:
                logger.info(f"Applied rewrites: {applied_rewrites}")
            
            return current_query
            
        except Exception as e:
            logger.error(f"Query rewriting failed: {e}")
            return query
    
    def _get_patterns_for_level(self, level: OptimizationLevel) -> List:
        """Get rewrite patterns based on optimization level"""
        if level == OptimizationLevel.BASIC:
            return self.rewrite_patterns[:2]
        elif level == OptimizationLevel.INTERMEDIATE:
            return self.rewrite_patterns[:4]
        elif level == OptimizationLevel.ADVANCED:
            return self.rewrite_patterns[:6]
        else:  # AGGRESSIVE
            return self.rewrite_patterns
    
    def _rewrite_or_to_union(self, query: str) -> str:
        """Rewrite OR conditions to UNION for better index usage"""
        # Simple OR to UNION rewrite
        pattern = r"WHERE\s+(\w+)\s*=\s*'?(\w+)'?\s+OR\s+\1\s*=\s*'?(\w+)'?"
        
        def replace_or(match):
            column = match.group(1)
            value1 = match.group(2)
            value2 = match.group(3)
            
            # Only rewrite if it's beneficial
            if len(value1) > 0 and len(value2) > 0:
                base_query = query.replace(match.group(0), f"WHERE {column} = '{value1}'")
                union_query = query.replace(match.group(0), f"WHERE {column} = '{value2}'")
                return f"({base_query}) UNION ({union_query})"
            return match.group(0)
        
        return re.sub(pattern, replace_or, query, flags=re.IGNORECASE)
    
    def _rewrite_exists_to_join(self, query: str) -> str:
        """Rewrite EXISTS subqueries to JOINs when beneficial"""
        # Pattern for EXISTS subqueries
        exists_pattern = r"EXISTS\s*\(\s*SELECT.*?FROM\s+(\w+).*?WHERE\s+(\w+\.\w+)\s*=\s*(\w+\.\w+).*?\)"
        
        def replace_exists(match):
            subquery_table = match.group(1)
            condition = f"{match.group(2)} = {match.group(3)}"
            
            # Replace EXISTS with INNER JOIN
            join_clause = f"INNER JOIN {subquery_table} ON {condition}"
            return join_clause
        
        # This is a simplified rewrite - in practice, you'd need more sophisticated parsing
        if "EXISTS" in query.upper():
            # For now, just log that we would rewrite it
            logger.debug("EXISTS subquery detected - candidate for JOIN rewrite")
        
        return query
    
    def _rewrite_subquery_to_cte(self, query: str) -> str:
        """Rewrite repeated subqueries to CTEs"""
        # Detect repeated subquery patterns
        subquery_pattern = r"\((SELECT.*?)\)"
        subqueries = re.findall(subquery_pattern, query, re.IGNORECASE | re.DOTALL)
        
        if len(subqueries) > 1:
            # Count occurrences
            subquery_counts = Counter(subqueries)
            repeated_subqueries = {sq: count for sq, count in subquery_counts.items() if count > 1}
            
            if repeated_subqueries:
                # Generate CTE
                cte_parts = []
                cte_replacements = {}
                
                for i, (subquery, count) in enumerate(repeated_subqueries.items()):
                    cte_name = f"cte_{i}"
                    cte_parts.append(f"{cte_name} AS ({subquery})")
                    cte_replacements[f"({subquery})"] = cte_name
                
                if cte_parts:
                    cte_clause = "WITH " + ", ".join(cte_parts)
                    
                    # Replace subqueries with CTE references
                    modified_query = query
                    for original, replacement in cte_replacements.items():
                        modified_query = modified_query.replace(original, replacement)
                    
                    return f"{cte_clause} {modified_query}"
        
        return query
    
    def _rewrite_case_to_filter(self, query: str) -> str:
        """Rewrite CASE statements to filters when possible"""
        # Pattern for simple CASE statements that can be filtered
        case_pattern = r"CASE\s+WHEN\s+(\w+)\s*=\s*'?(\w+)'?\s+THEN\s+(\w+)\s+ELSE\s+NULL\s+END"
        
        def replace_case(match):
            column = match.group(1)
            value = match.group(2)
            result = match.group(3)
            
            # Can be rewritten as a filter
            return f"{result} WHERE {column} = '{value}'"
        
        return re.sub(case_pattern, replace_case, query, flags=re.IGNORECASE)
    
    def _optimize_window_functions(self, query: str) -> str:
        """Optimize window function usage"""
        # Detect window functions that can be optimized
        if "OVER" in query.upper():
            # Add RANGE BETWEEN optimization for window functions
            window_pattern = r"(\w+\s*\([^)]*\))\s+OVER\s*\(\s*ORDER\s+BY\s+(\w+)\s*\)"
            
            def optimize_window(match):
                func = match.group(1)
                order_col = match.group(2)
                
                # Add optimized window frame
                return f"{func} OVER (ORDER BY {order_col} RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"
            
            query = re.sub(window_pattern, optimize_window, query, flags=re.IGNORECASE)
        
        return query
    
    def _optimize_aggregations(self, query: str) -> str:
        """Optimize aggregation queries"""
        # Optimize COUNT(*) to COUNT(1) when appropriate
        query = re.sub(r"COUNT\s*\(\s*\*\s*\)", "COUNT(1)", query, flags=re.IGNORECASE)
        
        # Optimize DISTINCT aggregations
        if "COUNT(DISTINCT" in query.upper():
            # Suggest using GROUP BY instead for large datasets
            logger.debug("COUNT(DISTINCT) detected - consider GROUP BY optimization")
        
        return query
    
    def _rewrite_inefficient_joins(self, query: str) -> str:
        """Rewrite inefficient JOIN patterns"""
        # Detect and optimize inefficient join conditions
        if "JOIN" in query.upper() and "OR" in query.upper():
            logger.debug("JOIN with OR condition detected - candidate for optimization")
        
        return query


class IntelligentExecutionPlanOptimizer:
    """Intelligent execution plan optimization"""
    
    def __init__(self):
        self.plan_cache: Dict[str, Any] = {}
        self.optimization_strategies = [
            self._optimize_join_order,
            self._optimize_index_selection,
            self._optimize_parallel_execution,
            self._optimize_memory_usage
        ]
    
    async def optimize_execution_plan(self, engine: AsyncEngine, query: str) -> Dict[str, Any]:
        """Optimize query execution plan"""
        try:
            # Get current execution plan
            plan_key = hashlib.md5(query.encode()).hexdigest()
            
            if plan_key in self.plan_cache:
                return self.plan_cache[plan_key]
            
            # Analyze execution plan
            explain_query = f"EXPLAIN (ANALYZE false, VERBOSE true, BUFFERS false, FORMAT JSON) {query}"
            
            async with engine.begin() as conn:
                result = await conn.execute(text(explain_query))
                plan_data = result.fetchone()[0]
            
            if isinstance(plan_data, list) and plan_data:
                plan_info = plan_data[0]['Plan']
                
                # Apply optimization strategies
                optimizations = {}
                for strategy in self.optimization_strategies:
                    try:
                        optimization = strategy(plan_info, query)
                        if optimization:
                            optimizations[strategy.__name__] = optimization
                    except Exception as e:
                        logger.warning(f"Optimization strategy {strategy.__name__} failed: {e}")
                
                result = {
                    'original_plan': plan_info,
                    'optimizations': optimizations,
                    'estimated_cost': plan_info.get('Total Cost', 0),
                    'estimated_rows': plan_info.get('Plan Rows', 0)
                }
                
                self.plan_cache[plan_key] = result
                return result
            
            return {}
            
        except Exception as e:
            logger.error(f"Execution plan optimization failed: {e}")
            return {}
    
    def _optimize_join_order(self, plan_info: Dict[str, Any], query: str) -> Optional[str]:
        """Optimize JOIN order"""
        # Analyze join nodes in plan
        join_nodes = self._find_join_nodes(plan_info)
        
        if len(join_nodes) > 2:
            # Suggest join order optimization
            return "Consider reordering joins based on table sizes and selectivity"
        
        return None
    
    def _optimize_index_selection(self, plan_info: Dict[str, Any], query: str) -> Optional[str]:
        """Optimize index selection"""
        # Look for sequential scans that could use indexes
        seq_scans = self._find_sequential_scans(plan_info)
        
        if seq_scans:
            tables = [scan.get('Relation Name') for scan in seq_scans]
            return f"Consider adding indexes for tables: {', '.join(tables)}"
        
        return None
    
    def _optimize_parallel_execution(self, plan_info: Dict[str, Any], query: str) -> Optional[str]:
        """Optimize parallel execution"""
        estimated_cost = plan_info.get('Total Cost', 0)
        
        if estimated_cost > 1000 and 'Parallel' not in str(plan_info):
            return "Consider enabling parallel execution for this expensive query"
        
        return None
    
    def _optimize_memory_usage(self, plan_info: Dict[str, Any], query: str) -> Optional[str]:
        """Optimize memory usage"""
        # Check for memory-intensive operations
        memory_intensive_nodes = ['Hash', 'Sort', 'Materialize']
        
        for node_type in memory_intensive_nodes:
            if self._has_node_type(plan_info, node_type):
                return f"Consider optimizing {node_type} operations - increase work_mem if needed"
        
        return None
    
    def _find_join_nodes(self, plan_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find join nodes in execution plan"""
        joins = []
        
        def find_joins(node):
            if 'Join' in node.get('Node Type', ''):
                joins.append(node)
            
            for child in node.get('Plans', []):
                find_joins(child)
        
        find_joins(plan_info)
        return joins
    
    def _find_sequential_scans(self, plan_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find sequential scan nodes"""
        scans = []
        
        def find_scans(node):
            if node.get('Node Type') == 'Seq Scan':
                scans.append(node)
            
            for child in node.get('Plans', []):
                find_scans(child)
        
        find_scans(plan_info)
        return scans
    
    def _has_node_type(self, plan_info: Dict[str, Any], node_type: str) -> bool:
        """Check if plan contains specific node type"""
        def check_node(node):
            if node_type in node.get('Node Type', ''):
                return True
            
            return any(check_node(child) for child in node.get('Plans', []))
        
        return check_node(plan_info)


class AdvancedQueryOptimizer:
    """Advanced query optimizer with ML and adaptive capabilities"""
    
    def __init__(self, base_optimizer: QueryOptimizer):
        self.base_optimizer = base_optimizer
        self.cost_estimator = MLQueryCostEstimator()
        self.query_rewriter = AdaptiveQueryRewriter()
        self.plan_optimizer = IntelligentExecutionPlanOptimizer()
        
        self.optimization_history: List[Dict[str, Any]] = []
        self.performance_tracking: Dict[str, List[float]] = defaultdict(list)
    
    async def optimize_query_advanced(self, engine: AsyncEngine, query: str, 
                                    optimization_level: OptimizationLevel = OptimizationLevel.INTERMEDIATE) -> OptimizationResult:
        """Perform advanced query optimization"""
        try:
            logger.info(f"Starting advanced optimization for query (level: {optimization_level.value})")
            
            # Step 1: Analyze original query
            original_plan = await self.base_optimizer.analyze_query(query)
            original_features = self.cost_estimator.extract_features(original_plan)
            original_cost = self.cost_estimator.estimate_cost(original_features)
            
            # Step 2: Apply query rewriting
            rewritten_query = await self.query_rewriter.rewrite_query(query, optimization_level)
            
            # Step 3: Optimize execution plan
            plan_optimizations = await self.plan_optimizer.optimize_execution_plan(engine, rewritten_query)
            
            # Step 4: Analyze optimized query
            if rewritten_query != query:
                optimized_plan = await self.base_optimizer.analyze_query(rewritten_query)
                optimized_features = self.cost_estimator.extract_features(optimized_plan)
                optimized_cost = self.cost_estimator.estimate_cost(optimized_features)
            else:
                optimized_cost = original_cost
            
            # Step 5: Calculate improvement
            improvement = max(0, (original_cost - optimized_cost) / original_cost * 100)
            
            # Step 6: Compile results
            optimizations_applied = []
            if rewritten_query != query:
                optimizations_applied.append("Query rewriting")
            if plan_optimizations.get('optimizations'):
                optimizations_applied.extend(plan_optimizations['optimizations'].keys())
            
            result = OptimizationResult(
                original_query=query,
                optimized_query=rewritten_query,
                optimization_level=optimization_level,
                estimated_improvement=improvement,
                optimizations_applied=optimizations_applied,
                warnings=[],
                execution_plan_changes=plan_optimizations
            )
            
            # Track optimization
            self.optimization_history.append({
                'timestamp': datetime.now(),
                'original_cost': original_cost,
                'optimized_cost': optimized_cost,
                'improvement': improvement,
                'level': optimization_level.value,
                'query_hash': hashlib.md5(query.encode()).hexdigest()
            })
            
            logger.info(f"Advanced optimization completed - Improvement: {improvement:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Advanced query optimization failed: {e}")
            return OptimizationResult(
                original_query=query,
                optimized_query=query,
                optimization_level=optimization_level,
                estimated_improvement=0.0,
                optimizations_applied=[],
                warnings=[f"Optimization failed: {e}"],
                execution_plan_changes={}
            )
    
    async def batch_optimize_queries(self, engine: AsyncEngine, queries: List[str]) -> List[OptimizationResult]:
        """Batch optimize multiple queries"""
        results = []
        
        for i, query in enumerate(queries):
            logger.info(f"Optimizing query {i+1}/{len(queries)}")
            
            # Use different optimization levels based on query complexity
            plan = await self.base_optimizer.analyze_query(query)
            complexity = self._determine_optimization_level(plan)
            
            result = await self.optimize_query_advanced(engine, query, complexity)
            results.append(result)
        
        return results
    
    def _determine_optimization_level(self, query_plan: QueryPlan) -> OptimizationLevel:
        """Determine appropriate optimization level based on query complexity"""
        complexity_score = query_plan.components.complexity_score
        
        if complexity_score <= 10:
            return OptimizationLevel.BASIC
        elif complexity_score <= 25:
            return OptimizationLevel.INTERMEDIATE
        elif complexity_score <= 50:
            return OptimizationLevel.ADVANCED
        else:
            return OptimizationLevel.AGGRESSIVE
    
    async def learn_from_execution(self, query: str, execution_time: float, 
                                 metrics: QueryPerformanceMetrics):
        """Learn from actual query execution"""
        try:
            # Analyze query
            plan = await self.base_optimizer.analyze_query(query)
            
            # Learn cost estimation
            self.cost_estimator.learn_from_execution(plan, execution_time)
            
            # Track performance
            query_hash = hashlib.md5(query.encode()).hexdigest()
            self.performance_tracking[query_hash].append(execution_time)
            
            # Keep only recent performance data
            if len(self.performance_tracking[query_hash]) > 100:
                self.performance_tracking[query_hash] = self.performance_tracking[query_hash][-50:]
            
            logger.debug(f"Learned from query execution - Time: {execution_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Failed to learn from execution: {e}")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        if not self.optimization_history:
            return {}
        
        improvements = [h['improvement'] for h in self.optimization_history]
        
        return {
            'total_optimizations': len(self.optimization_history),
            'average_improvement': np.mean(improvements),
            'max_improvement': max(improvements),
            'optimization_level_distribution': Counter(
                h['level'] for h in self.optimization_history
            ),
            'recent_optimizations': self.optimization_history[-10:],
            'queries_tracked': len(self.performance_tracking),
            'cost_estimator_accuracy': self._calculate_estimator_accuracy()
        }
    
    def _calculate_estimator_accuracy(self) -> float:
        """Calculate cost estimator accuracy"""
        if len(self.cost_estimator.historical_costs) < 10:
            return 0.0
        
        recent_costs = self.cost_estimator.historical_costs[-50:]
        errors = []
        
        for cost_data in recent_costs:
            estimated = self.cost_estimator.estimate_cost(cost_data['features'])
            actual = cost_data['actual_cost']
            
            if actual > 0:
                error = abs(estimated - actual) / actual
                errors.append(error)
        
        if errors:
            accuracy = 1.0 - np.mean(errors)
            return max(0.0, accuracy)
        
        return 0.0


# Export main class
__all__ = ['AdvancedQueryOptimizer', 'OptimizationLevel', 'OptimizationResult', 'QueryPerformanceMetrics']