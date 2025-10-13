"""🚀 Enterprise Cross-Aggregate Query Engine - CQRS Architecture
==================================================================
Module: events/cqrs/cross_aggregate_query_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
==================================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE CROSS-AGGREGATE QUERY ENGINE
Advanced query engine for complex queries spanning multiple aggregates
- Cross-aggregate join optimization and execution
- Distributed query planning and execution
- Query result composition and aggregation  
- Consistency level management across aggregates
- Performance optimization through intelligent caching
- Real-time and analytical query support
"""

import asyncio
import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Union, Type, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import hashlib

from .query_bus import Query, QueryResult, QueryStatus
from .eventual_consistency_manager import ConsistencyLevel
from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)


class JoinType(Enum):
    """Types of joins for cross-aggregate queries"""
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    FULL_OUTER = "full_outer"
    CROSS = "cross"


class AggregationFunction(Enum):
    """Aggregation functions"""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    GROUP_CONCAT = "group_concat"
    FIRST = "first"
    LAST = "last"


class QueryExecutionStrategy(Enum):
    """Query execution strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    MATERIALIZED_VIEW = "materialized_view"
    STREAMING = "streaming"
    HYBRID = "hybrid"


@dataclass
class AggregateSource:
    """Source aggregate for cross-aggregate queries"""
    aggregate_type: str
    alias: str
    filters: Dict[str, Any] = field(default_factory=dict)
    projection: List[str] = field(default_factory=list)
    consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL
    max_results: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JoinCondition:
    """Join condition between aggregates"""
    left_aggregate: str
    left_field: str
    right_aggregate: str
    right_field: str
    join_type: JoinType = JoinType.INNER
    additional_conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregationSpec:
    """Aggregation specification"""
    function: AggregationFunction
    field: str
    alias: Optional[str] = None
    group_by: List[str] = field(default_factory=list)
    having: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossAggregateQuery:
    """Cross-aggregate query definition"""
    query_id: str
    name: str
    description: str
    sources: List[AggregateSource]
    joins: List[JoinCondition] = field(default_factory=list)
    aggregations: List[AggregationSpec] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    sorting: List[Dict[str, str]] = field(default_factory=list)
    pagination: Dict[str, int] = field(default_factory=lambda: {"page": 1, "limit": 100})
    execution_strategy: QueryExecutionStrategy = QueryExecutionStrategy.PARALLEL
    consistency_requirement: ConsistencyLevel = ConsistencyLevel.EVENTUAL
    timeout_seconds: int = 30
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryExecutionPlan:
    """Query execution plan"""
    plan_id: str
    query: CrossAggregateQuery
    execution_steps: List[Dict[str, Any]] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_duration_ms: float = 0.0
    parallelizable_steps: Set[int] = field(default_factory=set)
    dependencies: Dict[int, List[int]] = field(default_factory=dict)
    optimizations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QueryExecutionResult:
    """Result of cross-aggregate query execution"""
    query_id: str
    status: QueryStatus
    data: Optional[List[Dict[str, Any]]] = None
    total_count: Optional[int] = None
    execution_time_ms: float = 0.0
    execution_plan_id: Optional[str] = None
    steps_executed: int = 0
    cache_hit: bool = False
    consistency_achieved: bool = True
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AggregateDataProvider:
    """Abstract provider for aggregate data"""
    
    def __init__(self, aggregate_type: str):
        self.aggregate_type = aggregate_type
    
    async def fetch_data(self, source: AggregateSource) -> List[Dict[str, Any]]:
        """Fetch data from aggregate"""
        raise NotImplementedError
    
    async def count_data(self, source: AggregateSource) -> int:
        """Count data in aggregate"""
        raise NotImplementedError
    
    async def check_consistency(self, consistency_level: ConsistencyLevel) -> bool:
        """Check if aggregate meets consistency requirements"""
        raise NotImplementedError


class MockAggregateDataProvider(AggregateDataProvider):
    """Mock data provider for testing"""
    
    def __init__(self, aggregate_type: str):
        super().__init__(aggregate_type)
        self._data_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._generate_mock_data()
    
    def _generate_mock_data(self) -> None:
        """Generate mock data for different aggregate types"""
        if self.aggregate_type == "user":
            self._data_cache["user"] = [
                {"id": i, "name": f"User {i}", "email": f"user{i}@example.com", "age": 20 + (i % 50), "city": f"City {i % 10}"}
                for i in range(1, 1001)
            ]
        elif self.aggregate_type == "order":
            self._data_cache["order"] = [
                {"id": i, "user_id": (i % 100) + 1, "amount": round(10 + (i * 15.75) % 500, 2), 
                 "status": "completed" if i % 3 == 0 else "pending", "created_at": f"2025-01-{(i % 30) + 1:02d}"}
                for i in range(1, 2001)
            ]
        elif self.aggregate_type == "product":
            self._data_cache["product"] = [
                {"id": i, "name": f"Product {i}", "category": f"Category {i % 5}", 
                 "price": round(5 + (i * 12.33) % 200, 2), "in_stock": i % 4 != 0}
                for i in range(1, 501)
            ]
        elif self.aggregate_type == "content":
            self._data_cache["content"] = [
                {"id": i, "user_id": (i % 100) + 1, "title": f"Content {i}", "type": ["video", "audio", "image"][i % 3],
                 "views": i * 10, "likes": i * 2, "created_at": f"2025-01-{(i % 30) + 1:02d}"}
                for i in range(1, 1501)
            ]
    
    async def fetch_data(self, source: AggregateSource) -> List[Dict[str, Any]]:
        """Fetch mock data"""
        data = self._data_cache.get(self.aggregate_type, [])
        
        # Apply filters
        filtered_data = self._apply_filters(data, source.filters)
        
        # Apply projection
        if source.projection:
            projected_data = []
            for item in filtered_data:
                projected_item = {field: item.get(field) for field in source.projection}
                projected_data.append(projected_item)
            filtered_data = projected_data
        
        # Apply limit
        if source.max_results:
            filtered_data = filtered_data[:source.max_results]
        
        return filtered_data
    
    async def count_data(self, source: AggregateSource) -> int:
        """Count mock data"""
        data = self._data_cache.get(self.aggregate_type, [])
        filtered_data = self._apply_filters(data, source.filters)
        return len(filtered_data)
    
    async def check_consistency(self, consistency_level: ConsistencyLevel) -> bool:
        """Mock consistency check"""
        # Simulate consistency check based on level
        if consistency_level == ConsistencyLevel.EVENTUAL:
            return True
        elif consistency_level == ConsistencyLevel.SESSION:
            return True  # Assume session consistency is always met in mock
        elif consistency_level == ConsistencyLevel.STRONG:
            return True  # Assume strong consistency for mock
        return True
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to data"""
        if not filters:
            return data
        
        filtered = []
        for item in data:
            matches = True
            for key, value in filters.items():
                if key not in item:
                    matches = False
                    break
                
                # Handle different filter types
                if isinstance(value, dict):
                    # Range or comparison filters
                    if "gte" in value and item[key] < value["gte"]:
                        matches = False
                        break
                    if "lte" in value and item[key] > value["lte"]:
                        matches = False
                        break
                    if "gt" in value and item[key] <= value["gt"]:
                        matches = False
                        break
                    if "lt" in value and item[key] >= value["lt"]:
                        matches = False
                        break
                    if "in" in value and item[key] not in value["in"]:
                        matches = False
                        break
                elif item[key] != value:
                    matches = False
                    break
            
            if matches:
                filtered.append(item)
        
        return filtered


class QueryPlanner:
    """Plan execution for cross-aggregate queries"""
    
    def __init__(self):
        self._cost_model: Dict[str, float] = {
            "fetch_aggregate": 10.0,
            "join_operation": 50.0,
            "aggregation": 20.0,
            "sort": 15.0,
            "filter": 5.0
        }
    
    async def create_execution_plan(self, query: CrossAggregateQuery) -> QueryExecutionPlan:
        """Create optimized execution plan"""
        plan_id = str(uuid.uuid4())
        
        execution_steps = []
        total_cost = 0.0
        parallelizable_steps = set()
        dependencies = {}
        optimizations = []
        
        step_id = 0
        
        # Step 1: Fetch data from all source aggregates
        fetch_steps = []
        for i, source in enumerate(query.sources):
            step = {
                "step_id": step_id,
                "type": "fetch_aggregate",
                "aggregate_type": source.aggregate_type,
                "alias": source.alias,
                "source": source,
                "estimated_cost": self._cost_model["fetch_aggregate"]
            }
            execution_steps.append(step)
            fetch_steps.append(step_id)
            parallelizable_steps.add(step_id)
            total_cost += step["estimated_cost"]
            step_id += 1
        
        # Step 2: Join operations (if any)
        join_step_id = None
        if query.joins:
            join_step_id = step_id
            step = {
                "step_id": step_id,
                "type": "join_operations",
                "joins": query.joins,
                "estimated_cost": len(query.joins) * self._cost_model["join_operation"]
            }
            execution_steps.append(step)
            dependencies[step_id] = fetch_steps  # Depends on all fetch steps
            total_cost += step["estimated_cost"]
            step_id += 1
        
        # Step 3: Apply global filters
        filter_step_id = None
        if query.filters:
            filter_step_id = step_id
            step = {
                "step_id": step_id,
                "type": "apply_filters",
                "filters": query.filters,
                "estimated_cost": self._cost_model["filter"]
            }
            execution_steps.append(step)
            if join_step_id is not None:
                dependencies[step_id] = [join_step_id]
            else:
                dependencies[step_id] = fetch_steps
            total_cost += step["estimated_cost"]
            step_id += 1
        
        # Step 4: Aggregations (if any)
        aggregation_step_id = None
        if query.aggregations:
            aggregation_step_id = step_id
            step = {
                "step_id": step_id,
                "type": "aggregations",
                "aggregations": query.aggregations,
                "estimated_cost": len(query.aggregations) * self._cost_model["aggregation"]
            }
            execution_steps.append(step)
            prev_step = filter_step_id or join_step_id
            if prev_step is not None:
                dependencies[step_id] = [prev_step]
            else:
                dependencies[step_id] = fetch_steps
            total_cost += step["estimated_cost"]
            step_id += 1
        
        # Step 5: Sorting (if any)
        sort_step_id = None
        if query.sorting:
            sort_step_id = step_id
            step = {
                "step_id": step_id,
                "type": "sort",
                "sorting": query.sorting,
                "estimated_cost": self._cost_model["sort"]
            }
            execution_steps.append(step)
            prev_step = aggregation_step_id or filter_step_id or join_step_id
            if prev_step is not None:
                dependencies[step_id] = [prev_step]
            else:
                dependencies[step_id] = fetch_steps
            total_cost += step["estimated_cost"]
            step_id += 1
        
        # Step 6: Pagination
        pagination_step_id = step_id
        step = {
            "step_id": step_id,
            "type": "pagination",
            "pagination": query.pagination,
            "estimated_cost": 1.0
        }
        execution_steps.append(step)
        prev_step = sort_step_id or aggregation_step_id or filter_step_id or join_step_id
        if prev_step is not None:
            dependencies[step_id] = [prev_step]
        else:
            dependencies[step_id] = fetch_steps
        total_cost += step["estimated_cost"]
        
        # Add optimizations
        if len(query.sources) > 1 and not query.joins:
            optimizations.append("Consider adding joins for better performance")
        
        if query.execution_strategy == QueryExecutionStrategy.PARALLEL and fetch_steps:
            optimizations.append("Parallel fetch enabled for source aggregates")
        
        # Estimate duration (simplified model)
        estimated_duration = total_cost * 10  # 10ms per cost unit
        
        return QueryExecutionPlan(
            plan_id=plan_id,
            query=query,
            execution_steps=execution_steps,
            estimated_cost=total_cost,
            estimated_duration_ms=estimated_duration,
            parallelizable_steps=parallelizable_steps,
            dependencies=dependencies,
            optimizations=optimizations
        )


class QueryExecutor:
    """Execute cross-aggregate queries"""
    
    def __init__(self):
        self._data_providers: Dict[str, AggregateDataProvider] = {}
        self._execution_cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, datetime] = {}
    
    def register_data_provider(self, aggregate_type: str, provider: AggregateDataProvider) -> None:
        """Register data provider for aggregate type"""
        self._data_providers[aggregate_type] = provider
        logger.info(f"Registered data provider for aggregate type: {aggregate_type}")
    
    async def execute_plan(self, plan: QueryExecutionPlan) -> QueryExecutionResult:
        """Execute query plan"""
        start_time = time.time()
        
        try:
            # Check cache first
            if plan.query.cache_enabled:
                cache_key = self._generate_cache_key(plan.query)
                cached_result = await self._get_cached_result(cache_key)
                if cached_result:
                    cached_result.cache_hit = True
                    return cached_result
            
            # Check consistency requirements
            consistency_achieved = await self._check_consistency(plan.query)
            
            # Execute plan steps
            execution_context = {}
            steps_executed = 0
            
            # Determine execution order
            execution_order = self._determine_execution_order(plan)
            
            for step_id in execution_order:
                step = plan.execution_steps[step_id]
                await self._execute_step(step, execution_context, plan.query)
                steps_executed += 1
            
            # Get final result
            result_data = execution_context.get("final_result", [])
            total_count = execution_context.get("total_count", len(result_data))
            
            execution_time = (time.time() - start_time) * 1000
            
            result = QueryExecutionResult(
                query_id=plan.query.query_id,
                status=QueryStatus.COMPLETED,
                data=result_data,
                total_count=total_count,
                execution_time_ms=execution_time,
                execution_plan_id=plan.plan_id,
                steps_executed=steps_executed,
                consistency_achieved=consistency_achieved
            )
            
            # Cache result
            if plan.query.cache_enabled:
                cache_key = self._generate_cache_key(plan.query)
                await self._cache_result(cache_key, result, plan.query.cache_ttl_seconds)
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return QueryExecutionResult(
                query_id=plan.query.query_id,
                status=QueryStatus.FAILED,
                execution_time_ms=execution_time,
                execution_plan_id=plan.plan_id,
                error=str(e)
            )
    
    def _determine_execution_order(self, plan: QueryExecutionPlan) -> List[int]:
        """Determine optimal execution order considering dependencies"""
        executed = set()
        execution_order = []
        
        def can_execute(step_id: int) -> bool:
            deps = plan.dependencies.get(step_id, [])
            return all(dep in executed for dep in deps)
        
        # Execute steps based on dependencies
        while len(executed) < len(plan.execution_steps):
            # Find executable steps
            executable_steps = [
                i for i in range(len(plan.execution_steps))
                if i not in executed and can_execute(i)
            ]
            
            if not executable_steps:
                break  # Circular dependency or other issue
            
            # Execute parallelizable steps first
            parallelizable = [s for s in executable_steps if s in plan.parallelizable_steps]
            if parallelizable:
                execution_order.extend(parallelizable)
                executed.update(parallelizable)
            else:
                # Execute first available step
                step_id = executable_steps[0]
                execution_order.append(step_id)
                executed.add(step_id)
        
        return execution_order
    
    async def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any], query: CrossAggregateQuery) -> None:
        """Execute individual step"""
        step_type = step["type"]
        
        if step_type == "fetch_aggregate":
            await self._execute_fetch_step(step, context)
        elif step_type == "join_operations":
            await self._execute_join_step(step, context)
        elif step_type == "apply_filters":
            await self._execute_filter_step(step, context)
        elif step_type == "aggregations":
            await self._execute_aggregation_step(step, context)
        elif step_type == "sort":
            await self._execute_sort_step(step, context)
        elif step_type == "pagination":
            await self._execute_pagination_step(step, context)
    
    async def _execute_fetch_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Execute fetch aggregate step"""
        source = step["source"]
        provider = self._data_providers.get(source.aggregate_type)
        
        if not provider:
            raise EventProcessingError(f"No data provider for aggregate type: {source.aggregate_type}")
        
        data = await provider.fetch_data(source)
        context[source.alias] = data
    
    async def _execute_join_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Execute join operations step"""
        joins = step["joins"]
        
        # Start with first table
        if not context:
            raise EventProcessingError("No data available for join operations")
        
        # Get first dataset
        first_alias = list(context.keys())[0]
        result = context[first_alias]
        
        # Apply joins sequentially
        for join in joins:
            left_data = result if join.left_aggregate == first_alias else context.get(join.left_aggregate, [])
            right_data = context.get(join.right_aggregate, [])
            
            result = self._perform_join(left_data, right_data, join)
        
        context["joined_result"] = result
    
    def _perform_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
                     join: JoinCondition) -> List[Dict[str, Any]]:
        """Perform join operation"""
        result = []
        
        if join.join_type == JoinType.INNER:
            for left_item in left_data:
                for right_item in right_data:
                    if left_item.get(join.left_field) == right_item.get(join.right_field):
                        joined_item = {**left_item, **right_item}
                        result.append(joined_item)
        
        elif join.join_type == JoinType.LEFT:
            for left_item in left_data:
                matched = False
                for right_item in right_data:
                    if left_item.get(join.left_field) == right_item.get(join.right_field):
                        joined_item = {**left_item, **right_item}
                        result.append(joined_item)
                        matched = True
                
                if not matched:
                    result.append(left_item)
        
        # Add more join types as needed
        
        return result
    
    async def _execute_filter_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Execute filter step"""
        filters = step["filters"]
        
        # Get data to filter
        data = context.get("joined_result")
        if data is None:
            # Use first available dataset
            data = next(iter(context.values()), [])
        
        filtered_data = self._apply_global_filters(data, filters)
        context["filtered_result"] = filtered_data
    
    def _apply_global_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply global filters to data"""
        if not filters:
            return data
        
        filtered = []
        for item in data:
            matches = True
            for key, value in filters.items():
                if key not in item or item[key] != value:
                    matches = False
                    break
            if matches:
                filtered.append(item)
        
        return filtered
    
    async def _execute_aggregation_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Execute aggregation step"""
        aggregations = step["aggregations"]
        
        # Get data to aggregate
        data = context.get("filtered_result") or context.get("joined_result")
        if data is None:
            data = next(iter(context.values()), [])
        
        aggregated_data = self._perform_aggregations(data, aggregations)
        context["aggregated_result"] = aggregated_data
    
    def _perform_aggregations(self, data: List[Dict[str, Any]], aggregations: List[AggregationSpec]) -> List[Dict[str, Any]]:
        """Perform aggregation operations"""
        if not aggregations:
            return data
        
        # Group data if needed
        grouped_data = {}
        for agg in aggregations:
            if agg.group_by:
                # Group by specified fields
                for item in data:
                    group_key = tuple(item.get(field, '') for field in agg.group_by)
                    if group_key not in grouped_data:
                        grouped_data[group_key] = []
                    grouped_data[group_key].append(item)
                break
        
        if not grouped_data:
            # No grouping, aggregate all data
            grouped_data = {'all': data}
        
        # Perform aggregations
        result = []
        for group_key, group_data in grouped_data.items():
            aggregated_item = {}
            
            # Add group by fields
            if group_key != 'all':
                for i, agg in enumerate(aggregations):
                    if agg.group_by:
                        for j, field in enumerate(agg.group_by):
                            aggregated_item[field] = group_key[j]
                        break
            
            # Apply aggregation functions
            for agg in aggregations:
                field_values = [item.get(agg.field) for item in group_data if agg.field in item]
                
                if agg.function == AggregationFunction.COUNT:
                    value = len(field_values)
                elif agg.function == AggregationFunction.SUM:
                    value = sum(v for v in field_values if isinstance(v, (int, float)))
                elif agg.function == AggregationFunction.AVG:
                    numeric_values = [v for v in field_values if isinstance(v, (int, float))]
                    value = sum(numeric_values) / len(numeric_values) if numeric_values else 0
                elif agg.function == AggregationFunction.MIN:
                    value = min(field_values) if field_values else None
                elif agg.function == AggregationFunction.MAX:
                    value = max(field_values) if field_values else None
                else:
                    value = len(field_values)  # Default to count
                
                alias = agg.alias or f"{agg.function.value}_{agg.field}"
                aggregated_item[alias] = value
            
            result.append(aggregated_item)
        
        return result
    
    async def _execute_sort_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Execute sort step"""
        sorting = step["sorting"]
        
        # Get data to sort
        data = (context.get("aggregated_result") or 
                context.get("filtered_result") or 
                context.get("joined_result"))
        if data is None:
            data = next(iter(context.values()), [])
        
        sorted_data = self._apply_sorting(data, sorting)
        context["sorted_result"] = sorted_data
    
    def _apply_sorting(self, data: List[Dict[str, Any]], sorting: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Apply sorting to data"""
        if not sorting:
            return data
        
        sorted_data = data.copy()
        
        for sort_spec in reversed(sorting):  # Apply sorts in reverse order
            field = sort_spec.get("field")
            direction = sort_spec.get("direction", "asc")
            
            if field:
                sorted_data.sort(
                    key=lambda x: x.get(field, ""),
                    reverse=(direction.lower() == "desc")
                )
        
        return sorted_data
    
    async def _execute_pagination_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Execute pagination step"""
        pagination = step["pagination"]
        
        # Get data to paginate
        data = (context.get("sorted_result") or 
                context.get("aggregated_result") or 
                context.get("filtered_result") or 
                context.get("joined_result"))
        if data is None:
            data = next(iter(context.values()), [])
        
        context["total_count"] = len(data)
        
        page = pagination.get("page", 1)
        limit = pagination.get("limit", 100)
        
        start_index = (page - 1) * limit
        end_index = start_index + limit
        
        paginated_data = data[start_index:end_index]
        context["final_result"] = paginated_data
    
    async def _check_consistency(self, query: CrossAggregateQuery) -> bool:
        """Check consistency requirements across aggregates"""
        for source in query.sources:
            provider = self._data_providers.get(source.aggregate_type)
            if provider:
                is_consistent = await provider.check_consistency(source.consistency_level)
                if not is_consistent:
                    return False
        return True
    
    def _generate_cache_key(self, query: CrossAggregateQuery) -> str:
        """Generate cache key for query"""
        query_dict = {
            "sources": [source.aggregate_type for source in query.sources],
            "joins": [(j.left_aggregate, j.right_aggregate, j.join_type.value) for j in query.joins],
            "filters": query.filters,
            "aggregations": [(a.function.value, a.field) for a in query.aggregations],
            "sorting": query.sorting,
            "pagination": query.pagination
        }
        query_str = json.dumps(query_dict, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()
    
    async def _get_cached_result(self, cache_key: str) -> Optional[QueryExecutionResult]:
        """Get cached query result"""
        if cache_key in self._execution_cache:
            expiry = self._cache_ttl.get(cache_key)
            if expiry and expiry > datetime.utcnow():
                return self._execution_cache[cache_key]
            else:
                # Expired, remove from cache
                del self._execution_cache[cache_key]
                self._cache_ttl.pop(cache_key, None)
        return None
    
    async def _cache_result(self, cache_key: str, result: QueryExecutionResult, ttl_seconds: int) -> None:
        """Cache query result"""
        self._execution_cache[cache_key] = result
        self._cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=ttl_seconds)


class EnterpriseCrossAggregateQueryEngine:
    """Enterprise cross-aggregate query engine"""
    
    def __init__(self):
        self._query_planner = QueryPlanner()
        self._query_executor = QueryExecutor()
        self._registered_queries: Dict[str, CrossAggregateQuery] = {}
        
        # Metrics
        self._metrics = {
            "queries_executed": 0,
            "queries_cached": 0,
            "average_execution_time_ms": 0.0,
            "total_execution_time_ms": 0.0,
            "cache_hit_ratio": 0.0
        }
        
        # Register mock data providers for testing
        self._register_mock_providers()
    
    def _register_mock_providers(self) -> None:
        """Register mock data providers for testing"""
        aggregate_types = ["user", "order", "product", "content"]
        for aggregate_type in aggregate_types:
            provider = MockAggregateDataProvider(aggregate_type)
            self._query_executor.register_data_provider(aggregate_type, provider)
    
    def register_data_provider(self, aggregate_type: str, provider: AggregateDataProvider) -> None:
        """Register data provider for aggregate type"""
        self._query_executor.register_data_provider(aggregate_type, provider)
    
    def register_predefined_query(self, query: CrossAggregateQuery) -> None:
        """Register predefined cross-aggregate query"""
        self._registered_queries[query.query_id] = query
        logger.info(f"Registered predefined query: {query.query_id}")
    
    async def execute_query(self, query: CrossAggregateQuery) -> QueryExecutionResult:
        """Execute cross-aggregate query"""
        start_time = time.time()
        
        try:
            # Create execution plan
            plan = await self._query_planner.create_execution_plan(query)
            
            # Execute plan
            result = await self._query_executor.execute_plan(plan)
            
            # Update metrics
            execution_time = (time.time() - start_time) * 1000
            self._update_metrics(execution_time, result.cache_hit)
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._update_metrics(execution_time, False)
            
            return QueryExecutionResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                execution_time_ms=execution_time,
                error=str(e)
            )
    
    async def execute_predefined_query(self, query_id: str, parameters: Dict[str, Any] = None) -> QueryExecutionResult:
        """Execute predefined query with parameters"""
        if query_id not in self._registered_queries:
            return QueryExecutionResult(
                query_id=query_id,
                status=QueryStatus.FAILED,
                error=f"Predefined query {query_id} not found"
            )
        
        query = self._registered_queries[query_id]
        
        # Apply parameters if provided
        if parameters:
            query = self._apply_query_parameters(query, parameters)
        
        return await self.execute_query(query)
    
    def _apply_query_parameters(self, query: CrossAggregateQuery, parameters: Dict[str, Any]) -> CrossAggregateQuery:
        """Apply parameters to query"""
        # Create a copy of the query with parameter substitution
        # This is a simplified implementation
        modified_query = CrossAggregateQuery(
            query_id=query.query_id,
            name=query.name,
            description=query.description,
            sources=query.sources.copy(),
            joins=query.joins.copy(),
            aggregations=query.aggregations.copy(),
            filters={**query.filters, **parameters.get("filters", {})},
            sorting=parameters.get("sorting", query.sorting),
            pagination=parameters.get("pagination", query.pagination),
            execution_strategy=query.execution_strategy,
            consistency_requirement=query.consistency_requirement,
            timeout_seconds=query.timeout_seconds,
            cache_enabled=query.cache_enabled,
            cache_ttl_seconds=query.cache_ttl_seconds,
            metadata=query.metadata
        )
        
        return modified_query
    
    def _update_metrics(self, execution_time_ms: float, cache_hit: bool) -> None:
        """Update execution metrics"""
        self._metrics["queries_executed"] += 1
        
        if cache_hit:
            self._metrics["queries_cached"] += 1
        
        self._metrics["total_execution_time_ms"] += execution_time_ms
        self._metrics["average_execution_time_ms"] = (
            self._metrics["total_execution_time_ms"] / self._metrics["queries_executed"]
        )
        
        cache_hits = self._metrics["queries_cached"]
        total_queries = self._metrics["queries_executed"]
        self._metrics["cache_hit_ratio"] = (cache_hits / total_queries * 100) if total_queries > 0 else 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics"""
        return dict(self._metrics)
    
    def get_predefined_queries(self) -> List[Dict[str, Any]]:
        """Get list of predefined queries"""
        return [
            {
                "query_id": query.query_id,
                "name": query.name,
                "description": query.description,
                "source_aggregates": [source.aggregate_type for source in query.sources],
                "has_joins": bool(query.joins),
                "has_aggregations": bool(query.aggregations),
                "execution_strategy": query.execution_strategy.value,
                "cache_enabled": query.cache_enabled
            }
            for query in self._registered_queries.values()
        ]
    
    async def analyze_query_performance(self, query: CrossAggregateQuery) -> Dict[str, Any]:
        """Analyze query performance without executing"""
        plan = await self._query_planner.create_execution_plan(query)
        
        return {
            "query_id": query.query_id,
            "estimated_cost": plan.estimated_cost,
            "estimated_duration_ms": plan.estimated_duration_ms,
            "execution_steps": len(plan.execution_steps),
            "parallelizable_steps": len(plan.parallelizable_steps),
            "optimizations": plan.optimizations,
            "consistency_requirement": query.consistency_requirement.value,
            "cache_enabled": query.cache_enabled
        }


# Convenience function to create common query types
def create_user_orders_query(user_filters: Dict[str, Any] = None) -> CrossAggregateQuery:
    """Create a common user-orders cross-aggregate query"""
    return CrossAggregateQuery(
        query_id="user_orders_analysis",
        name="User Orders Analysis",
        description="Analyze user behavior with their order history",
        sources=[
            AggregateSource(
                aggregate_type="user",
                alias="users",
                filters=user_filters or {},
                projection=["id", "name", "email", "city"]
            ),
            AggregateSource(
                aggregate_type="order",
                alias="orders",
                projection=["id", "user_id", "amount", "status", "created_at"]
            )
        ],
        joins=[
            JoinCondition(
                left_aggregate="users",
                left_field="id",
                right_aggregate="orders",
                right_field="user_id",
                join_type=JoinType.LEFT
            )
        ],
        aggregations=[
            AggregationSpec(
                function=AggregationFunction.COUNT,
                field="id",
                alias="order_count",
                group_by=["user_id", "name"]
            ),
            AggregationSpec(
                function=AggregationFunction.SUM,
                field="amount",
                alias="total_amount",
                group_by=["user_id", "name"]
            )
        ],
        sorting=[{"field": "total_amount", "direction": "desc"}],
        execution_strategy=QueryExecutionStrategy.PARALLEL
    )


# Singleton instance for global access
_cross_aggregate_query_engine_instance: Optional[EnterpriseCrossAggregateQueryEngine] = None


def get_cross_aggregate_query_engine() -> EnterpriseCrossAggregateQueryEngine:
    """Get singleton cross-aggregate query engine instance"""
    global _cross_aggregate_query_engine_instance
    if _cross_aggregate_query_engine_instance is None:
        _cross_aggregate_query_engine_instance = EnterpriseCrossAggregateQueryEngine()
    return _cross_aggregate_query_engine_instance


def reset_cross_aggregate_query_engine() -> None:
    """Reset cross-aggregate query engine instance (for testing)"""
    global _cross_aggregate_query_engine_instance
    _cross_aggregate_query_engine_instance = None