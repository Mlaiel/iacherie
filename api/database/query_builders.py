"""
Query Builders - IA Influencer Agent Platform
Enterprise-grade query building with advanced features and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Type, Generic, TypeVar
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, date
from decimal import Decimal
import re
import json
from dataclasses import dataclass

from sqlalchemy import (
    select, insert, update, delete, func, text, and_, or_, not_, exists,
    case, cast, literal, distinct, union, union_all, intersect, except_,
    desc, asc, nullslast, nullsfirst, subquery, alias, join, outerjoin,
    Column, Table, Integer, String, DateTime, Boolean, Float, Text, JSON,
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.sql import Select, Insert, Update, Delete, ClauseElement
from sqlalchemy.sql.expression import BinaryExpression, UnaryExpression
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, Query, DeclarativeBase
import logging

from ..core.logging import get_logger
from ..models.database import Base

logger = get_logger(__name__)

T = TypeVar('T', bound=Base)


class FilterOperator(Enum):
    """Filter operators for query building"""
    EQ = "="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "IN"
    NOT_IN = "NOT IN"
    LIKE = "LIKE"
    ILIKE = "ILIKE"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT BETWEEN"
    CONTAINS = "@>"  # JSON contains
    CONTAINED_BY = "<@"  # JSON contained by
    HAS_KEY = "?"  # JSON has key
    HAS_ANY_KEY = "?|"  # JSON has any key
    HAS_ALL_KEYS = "?&"  # JSON has all keys
    REGEX = "~"  # Regular expression
    IREGEX = "~*"  # Case-insensitive regex
    FULL_TEXT = "@@"  # Full text search


class SortDirection(Enum):
    """Sort direction enumeration"""
    ASC = "ASC"
    DESC = "DESC"


class JoinType(Enum):
    """Join type enumeration"""
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FULL = "FULL"
    CROSS = "CROSS"


@dataclass
class FilterCondition:
    """Filter condition definition"""
    field: str
    operator: FilterOperator
    value: Any
    table_alias: Optional[str] = None
    case_sensitive: bool = True
    
    def __post_init__(self):
        """Validate filter condition"""
        if self.operator in [FilterOperator.BETWEEN, FilterOperator.NOT_BETWEEN]:
            if not isinstance(self.value, (list, tuple)) or len(self.value) != 2:
                raise ValueError(f"BETWEEN operator requires a list/tuple of 2 values, got: {self.value}")
        
        if self.operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
            if not isinstance(self.value, (list, tuple, set)):
                raise ValueError(f"IN operator requires a list/tuple/set of values, got: {self.value}")


@dataclass
class SortCondition:
    """Sort condition definition"""
    field: str
    direction: SortDirection = SortDirection.ASC
    table_alias: Optional[str] = None
    nulls_first: bool = False


@dataclass
class JoinCondition:
    """Join condition definition"""
    table: Union[str, Type[T]]
    join_type: JoinType = JoinType.INNER
    on_condition: Optional[str] = None
    alias: Optional[str] = None


@dataclass
class PaginationInfo:
    """Pagination information"""
    page: int = 1
    page_size: int = 50
    max_page_size: int = 1000
    
    def __post_init__(self):
        """Validate pagination parameters"""
        if self.page < 1:
            raise ValueError("Page number must be >= 1")
        if self.page_size < 1:
            raise ValueError("Page size must be >= 1")
        if self.page_size > self.max_page_size:
            raise ValueError(f"Page size cannot exceed {self.max_page_size}")


@dataclass
class QueryResult:
    """Query execution result"""
    data: Any
    total_count: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    has_next: bool = False
    has_previous: bool = False
    execution_time: Optional[float] = None
    query_sql: Optional[str] = None


class QueryBuilder:
    """
    Base query builder with essential functionality:
    - Basic CRUD operations
    - Filtering and sorting
    - Pagination
    - SQL generation
    """
    
    def __init__(self, model: Type[T]):
        self.model = model
        self.table = model.__table__
        self.query = None
        self.filters: List[FilterCondition] = []
        self.sorts: List[SortCondition] = []
        self.joins: List[JoinCondition] = []
        self.pagination: Optional[PaginationInfo] = None
        self._select_fields: List[str] = []
        self._group_by_fields: List[str] = []
        self._having_conditions: List[FilterCondition] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        
    def reset(self) -> 'QueryBuilder':
        """Reset query builder to initial state"""
        self.query = None
        self.filters = []
        self.sorts = []
        self.joins = []
        self.pagination = None
        self._select_fields = []
        self._group_by_fields = []
        self._having_conditions = []
        self._limit = None
        self._offset = None
        return self
    
    def select(self, *fields: str) -> 'QueryBuilder':
        """Select specific fields"""
        self._select_fields.extend(fields)
        return self
    
    def where(self, field: str, operator: FilterOperator, value: Any, 
              table_alias: Optional[str] = None, case_sensitive: bool = True) -> 'QueryBuilder':
        """Add WHERE condition"""
        condition = FilterCondition(
            field=field,
            operator=operator,
            value=value,
            table_alias=table_alias,
            case_sensitive=case_sensitive
        )
        self.filters.append(condition)
        return self
    
    def where_in(self, field: str, values: List[Any], 
                 table_alias: Optional[str] = None) -> 'QueryBuilder':
        """Add WHERE IN condition"""
        return self.where(field, FilterOperator.IN, values, table_alias)
    
    def where_between(self, field: str, start: Any, end: Any,
                      table_alias: Optional[str] = None) -> 'QueryBuilder':
        """Add WHERE BETWEEN condition"""
        return self.where(field, FilterOperator.BETWEEN, [start, end], table_alias)
    
    def where_like(self, field: str, pattern: str, case_sensitive: bool = True,
                   table_alias: Optional[str] = None) -> 'QueryBuilder':
        """Add WHERE LIKE condition"""
        operator = FilterOperator.LIKE if case_sensitive else FilterOperator.ILIKE
        return self.where(field, operator, pattern, table_alias, case_sensitive)
    
    def where_null(self, field: str, is_null: bool = True,
                   table_alias: Optional[str] = None) -> 'QueryBuilder':
        """Add WHERE NULL condition"""
        operator = FilterOperator.IS_NULL if is_null else FilterOperator.IS_NOT_NULL
        return self.where(field, operator, None, table_alias)
    
    def join(self, table: Union[str, Type[T]], join_type: JoinType = JoinType.INNER,
             on_condition: Optional[str] = None, alias: Optional[str] = None) -> 'QueryBuilder':
        """Add JOIN clause"""
        join_condition = JoinCondition(
            table=table,
            join_type=join_type,
            on_condition=on_condition,
            alias=alias
        )
        self.joins.append(join_condition)
        return self
    
    def left_join(self, table: Union[str, Type[T]], on_condition: Optional[str] = None,
                  alias: Optional[str] = None) -> 'QueryBuilder':
        """Add LEFT JOIN clause"""
        return self.join(table, JoinType.LEFT, on_condition, alias)
    
    def inner_join(self, table: Union[str, Type[T]], on_condition: Optional[str] = None,
                   alias: Optional[str] = None) -> 'QueryBuilder':
        """Add INNER JOIN clause"""
        return self.join(table, JoinType.INNER, on_condition, alias)
    
    def order_by(self, field: str, direction: SortDirection = SortDirection.ASC,
                 table_alias: Optional[str] = None, nulls_first: bool = False) -> 'QueryBuilder':
        """Add ORDER BY clause"""
        sort_condition = SortCondition(
            field=field,
            direction=direction,
            table_alias=table_alias,
            nulls_first=nulls_first
        )
        self.sorts.append(sort_condition)
        return self
    
    def order_by_desc(self, field: str, table_alias: Optional[str] = None) -> 'QueryBuilder':
        """Add ORDER BY DESC clause"""
        return self.order_by(field, SortDirection.DESC, table_alias)
    
    def group_by(self, *fields: str) -> 'QueryBuilder':
        """Add GROUP BY clause"""
        self._group_by_fields.extend(fields)
        return self
    
    def having(self, field: str, operator: FilterOperator, value: Any,
               table_alias: Optional[str] = None) -> 'QueryBuilder':
        """Add HAVING condition"""
        condition = FilterCondition(
            field=field,
            operator=operator,
            value=value,
            table_alias=table_alias
        )
        self._having_conditions.append(condition)
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """Add LIMIT clause"""
        if count < 0:
            raise ValueError("Limit must be non-negative")
        self._limit = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """Add OFFSET clause"""
        if count < 0:
            raise ValueError("Offset must be non-negative")
        self._offset = count
        return self
    
    def paginate(self, page: int = 1, page_size: int = 50,
                 max_page_size: int = 1000) -> 'QueryBuilder':
        """Add pagination"""
        self.pagination = PaginationInfo(page, page_size, max_page_size)
        return self
    
    def build_select(self) -> Select:
        """Build SELECT query"""
        # Start with base select
        if self._select_fields:
            # Select specific fields
            columns = []
            for field in self._select_fields:
                if hasattr(self.model, field):
                    columns.append(getattr(self.model, field))
                else:
                    # Assume it's a raw SQL expression
                    columns.append(text(field))
            query = select(*columns)
        else:
            # Select all fields from model
            query = select(self.model)
        
        # Add JOINs
        for join_condition in self.joins:
            query = self._apply_join(query, join_condition)
        
        # Add WHERE conditions
        if self.filters:
            where_clause = self._build_where_clause()
            query = query.where(where_clause)
        
        # Add GROUP BY
        if self._group_by_fields:
            group_columns = []
            for field in self._group_by_fields:
                if hasattr(self.model, field):
                    group_columns.append(getattr(self.model, field))
            if group_columns:
                query = query.group_by(*group_columns)
        
        # Add HAVING
        if self._having_conditions:
            having_clause = self._build_having_clause()
            query = query.having(having_clause)
        
        # Add ORDER BY
        if self.sorts:
            for sort_condition in self.sorts:
                query = self._apply_sort(query, sort_condition)
        
        # Add LIMIT and OFFSET
        if self.pagination:
            offset = (self.pagination.page - 1) * self.pagination.page_size
            query = query.offset(offset).limit(self.pagination.page_size)
        elif self._limit is not None:
            query = query.limit(self._limit)
            if self._offset is not None:
                query = query.offset(self._offset)
        
        return query
    
    def build_count_query(self) -> Select:
        """Build count query for pagination"""
        query = select(func.count()).select_from(self.model)
        
        # Add JOINs
        for join_condition in self.joins:
            query = self._apply_join(query, join_condition)
        
        # Add WHERE conditions
        if self.filters:
            where_clause = self._build_where_clause()
            query = query.where(where_clause)
        
        return query
    
    def _build_where_clause(self) -> ClauseElement:
        """Build WHERE clause from filter conditions"""
        if not self.filters:
            return text("1=1")  # Always true condition
        
        conditions = []
        for filter_condition in self.filters:
            condition = self._build_filter_condition(filter_condition)
            conditions.append(condition)
        
        # Combine all conditions with AND
        return and_(*conditions) if len(conditions) > 1 else conditions[0]
    
    def _build_having_clause(self) -> ClauseElement:
        """Build HAVING clause from having conditions"""
        if not self._having_conditions:
            return text("1=1")
        
        conditions = []
        for having_condition in self._having_conditions:
            condition = self._build_filter_condition(having_condition)
            conditions.append(condition)
        
        return and_(*conditions) if len(conditions) > 1 else conditions[0]
    
    def _build_filter_condition(self, filter_condition: FilterCondition) -> ClauseElement:
        """Build individual filter condition"""
        # Get the column
        if filter_condition.table_alias:
            # Handle aliased table (for joins)
            column = text(f"{filter_condition.table_alias}.{filter_condition.field}")
        elif hasattr(self.model, filter_condition.field):
            column = getattr(self.model, filter_condition.field)
        else:
            # Fallback to raw SQL
            column = text(filter_condition.field)
        
        value = filter_condition.value
        
        # Build condition based on operator
        if filter_condition.operator == FilterOperator.EQ:
            return column == value
        elif filter_condition.operator == FilterOperator.NE:
            return column != value
        elif filter_condition.operator == FilterOperator.GT:
            return column > value
        elif filter_condition.operator == FilterOperator.GTE:
            return column >= value
        elif filter_condition.operator == FilterOperator.LT:
            return column < value
        elif filter_condition.operator == FilterOperator.LTE:
            return column <= value
        elif filter_condition.operator == FilterOperator.IN:
            return column.in_(value)
        elif filter_condition.operator == FilterOperator.NOT_IN:
            return ~column.in_(value)
        elif filter_condition.operator == FilterOperator.LIKE:
            return column.like(value)
        elif filter_condition.operator == FilterOperator.ILIKE:
            return column.ilike(value)
        elif filter_condition.operator == FilterOperator.IS_NULL:
            return column.is_(None)
        elif filter_condition.operator == FilterOperator.IS_NOT_NULL:
            return column.is_not(None)
        elif filter_condition.operator == FilterOperator.BETWEEN:
            return column.between(value[0], value[1])
        elif filter_condition.operator == FilterOperator.NOT_BETWEEN:
            return ~column.between(value[0], value[1])
        elif filter_condition.operator == FilterOperator.CONTAINS:
            # JSON contains operation (PostgreSQL specific)
            return column.op('@>')(value)
        elif filter_condition.operator == FilterOperator.CONTAINED_BY:
            return column.op('<@')(value)
        elif filter_condition.operator == FilterOperator.HAS_KEY:
            return column.op('?')(value)
        elif filter_condition.operator == FilterOperator.REGEX:
            return column.op('~')(value)
        elif filter_condition.operator == FilterOperator.IREGEX:
            return column.op('~*')(value)
        elif filter_condition.operator == FilterOperator.FULL_TEXT:
            return column.op('@@')(func.to_tsquery(value))
        else:
            raise ValueError(f"Unsupported filter operator: {filter_condition.operator}")
    
    def _apply_join(self, query: Select, join_condition: JoinCondition) -> Select:
        """Apply JOIN to query"""
        # Get target table
        if isinstance(join_condition.table, str):
            target_table = text(join_condition.table)
        else:
            target_table = join_condition.table
        
        # Create alias if specified
        if join_condition.alias:
            target_table = target_table.alias(join_condition.alias)
        
        # Apply join based on type
        if join_condition.join_type == JoinType.INNER:
            if join_condition.on_condition:
                return query.join(target_table, text(join_condition.on_condition))
            else:
                return query.join(target_table)
        elif join_condition.join_type == JoinType.LEFT:
            if join_condition.on_condition:
                return query.outerjoin(target_table, text(join_condition.on_condition))
            else:
                return query.outerjoin(target_table)
        elif join_condition.join_type == JoinType.RIGHT:
            # SQLAlchemy doesn't have right join, use left join with reversed tables
            logger.warning("RIGHT JOIN converted to LEFT JOIN - consider restructuring query")
            return query.outerjoin(target_table)
        elif join_condition.join_type == JoinType.FULL:
            # Full outer join (PostgreSQL specific)
            return query.join(target_table, text(join_condition.on_condition), isouter=True, full=True)
        else:
            raise ValueError(f"Unsupported join type: {join_condition.join_type}")
    
    def _apply_sort(self, query: Select, sort_condition: SortCondition) -> Select:
        """Apply ORDER BY to query"""
        # Get the column
        if sort_condition.table_alias:
            column = text(f"{sort_condition.table_alias}.{sort_condition.field}")
        elif hasattr(self.model, sort_condition.field):
            column = getattr(self.model, sort_condition.field)
        else:
            column = text(sort_condition.field)
        
        # Apply direction and nulls handling
        if sort_condition.direction == SortDirection.DESC:
            if sort_condition.nulls_first:
                return query.order_by(desc(column).nullsfirst())
            else:
                return query.order_by(desc(column).nullslast())
        else:
            if sort_condition.nulls_first:
                return query.order_by(asc(column).nullsfirst())
            else:
                return query.order_by(asc(column).nullslast())
    
    def get_sql(self, compile_kwargs: Optional[Dict[str, Any]] = None) -> str:
        """Get SQL string representation of the query"""
        query = self.build_select()
        return str(query.compile(
            dialect=postgresql.dialect(),
            compile_kwargs=compile_kwargs or {"literal_binds": True}
        ))
    
    async def execute(self, session: AsyncSession, include_count: bool = False) -> QueryResult:
        """Execute the query and return results"""
        start_time = datetime.utcnow()
        
        # Build and execute main query
        query = self.build_select()
        result = await session.execute(query)
        data = result.scalars().all()
        
        # Get total count if needed
        total_count = None
        if include_count or self.pagination:
            count_query = self.build_count_query()
            count_result = await session.execute(count_query)
            total_count = count_result.scalar()
        
        # Calculate pagination info
        has_next = False
        has_previous = False
        if self.pagination and total_count is not None:
            total_pages = (total_count + self.pagination.page_size - 1) // self.pagination.page_size
            has_next = self.pagination.page < total_pages
            has_previous = self.pagination.page > 1
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return QueryResult(
            data=data,
            total_count=total_count,
            page=self.pagination.page if self.pagination else None,
            page_size=self.pagination.page_size if self.pagination else None,
            has_next=has_next,
            has_previous=has_previous,
            execution_time=execution_time,
            query_sql=self.get_sql()
        )


class AdvancedQueryBuilder(QueryBuilder):
    """
    Advanced query builder with complex operations:
    - Subqueries and CTEs
    - Window functions
    - JSON operations
    - Full-text search
    - Analytical functions
    """
    
    def __init__(self, model: Type[T]):
        super().__init__(model)
        self.subqueries: Dict[str, Select] = {}
        self.ctes: Dict[str, Select] = {}
        self.window_functions: List[Dict[str, Any]] = []
        
    def with_subquery(self, name: str, subquery: Select) -> 'AdvancedQueryBuilder':
        """Add a subquery"""
        self.subqueries[name] = subquery
        return self
    
    def with_cte(self, name: str, query: Select) -> 'AdvancedQueryBuilder':
        """Add a Common Table Expression (CTE)"""
        self.ctes[name] = query
        return self
    
    def add_window_function(self, function_name: str, partition_by: Optional[List[str]] = None,
                           order_by: Optional[List[str]] = None, alias: Optional[str] = None) -> 'AdvancedQueryBuilder':
        """Add window function"""
        window_func = {
            'function': function_name,
            'partition_by': partition_by or [],
            'order_by': order_by or [],
            'alias': alias or f"window_{len(self.window_functions)}"
        }
        self.window_functions.append(window_func)
        return self
    
    def where_json_contains(self, field: str, value: Dict[str, Any],
                           table_alias: Optional[str] = None) -> 'AdvancedQueryBuilder':
        """Add JSON contains condition"""
        return self.where(field, FilterOperator.CONTAINS, json.dumps(value), table_alias)
    
    def where_json_has_key(self, field: str, key: str,
                          table_alias: Optional[str] = None) -> 'AdvancedQueryBuilder':
        """Add JSON has key condition"""
        return self.where(field, FilterOperator.HAS_KEY, key, table_alias)
    
    def where_full_text_search(self, field: str, search_terms: str,
                              language: str = 'english',
                              table_alias: Optional[str] = None) -> 'AdvancedQueryBuilder':
        """Add full-text search condition"""
        return self.where(field, FilterOperator.FULL_TEXT, f"{language}::{search_terms}", table_alias)
    
    def where_regex(self, field: str, pattern: str, case_sensitive: bool = True,
                    table_alias: Optional[str] = None) -> 'AdvancedQueryBuilder':
        """Add regex condition"""
        operator = FilterOperator.REGEX if case_sensitive else FilterOperator.IREGEX
        return self.where(field, operator, pattern, table_alias)
    
    def distinct_on(self, *fields: str) -> 'AdvancedQueryBuilder':
        """Add DISTINCT ON clause (PostgreSQL specific)"""
        self._distinct_on_fields = fields
        return self
    
    def build_select(self) -> Select:
        """Build advanced SELECT query with CTEs and subqueries"""
        # Start with base query
        query = super().build_select()
        
        # Add CTEs
        for cte_name, cte_query in self.ctes.items():
            cte = cte_query.cte(cte_name)
            query = query.prefix_with(f"WITH {cte_name} AS")
        
        # Add window functions
        for window_func in self.window_functions:
            query = self._add_window_function(query, window_func)
        
        # Add DISTINCT ON if specified
        if hasattr(self, '_distinct_on_fields') and self._distinct_on_fields:
            columns = []
            for field in self._distinct_on_fields:
                if hasattr(self.model, field):
                    columns.append(getattr(self.model, field))
            if columns:
                query = query.distinct(*columns)
        
        return query
    
    def _add_window_function(self, query: Select, window_func: Dict[str, Any]) -> Select:
        """Add window function to query"""
        # Build partition by clause
        partition_columns = []
        for field in window_func['partition_by']:
            if hasattr(self.model, field):
                partition_columns.append(getattr(self.model, field))
        
        # Build order by clause for window
        order_columns = []
        for field in window_func['order_by']:
            if hasattr(self.model, field):
                order_columns.append(getattr(self.model, field))
        
        # Create window function based on type
        func_name = window_func['function'].lower()
        if func_name == 'row_number':
            window_expr = func.row_number().over(
                partition_by=partition_columns if partition_columns else None,
                order_by=order_columns if order_columns else None
            )
        elif func_name == 'rank':
            window_expr = func.rank().over(
                partition_by=partition_columns if partition_columns else None,
                order_by=order_columns if order_columns else None
            )
        elif func_name == 'dense_rank':
            window_expr = func.dense_rank().over(
                partition_by=partition_columns if partition_columns else None,
                order_by=order_columns if order_columns else None
            )
        elif func_name == 'lag':
            window_expr = func.lag(getattr(self.model, window_func.get('column', 'id'))).over(
                partition_by=partition_columns if partition_columns else None,
                order_by=order_columns if order_columns else None
            )
        elif func_name == 'lead':
            window_expr = func.lead(getattr(self.model, window_func.get('column', 'id'))).over(
                partition_by=partition_columns if partition_columns else None,
                order_by=order_columns if order_columns else None
            )
        else:
            # Generic window function
            window_expr = getattr(func, func_name)().over(
                partition_by=partition_columns if partition_columns else None,
                order_by=order_columns if order_columns else None
            )
        
        # Add to select with alias
        query = query.add_columns(window_expr.label(window_func['alias']))
        return query


class AggregationQueryBuilder(QueryBuilder):
    """
    Specialized query builder for aggregation operations:
    - COUNT, SUM, AVG, MIN, MAX
    - Group by with multiple levels
    - Having conditions
    - Rolling aggregations
    """
    
    def __init__(self, model: Type[T]):
        super().__init__(model)
        self.aggregations: List[Dict[str, Any]] = []
        
    def count(self, field: str = '*', alias: str = 'count') -> 'AggregationQueryBuilder':
        """Add COUNT aggregation"""
        self.aggregations.append({
            'function': 'count',
            'field': field,
            'alias': alias
        })
        return self
    
    def sum(self, field: str, alias: Optional[str] = None) -> 'AggregationQueryBuilder':
        """Add SUM aggregation"""
        self.aggregations.append({
            'function': 'sum',
            'field': field,
            'alias': alias or f'sum_{field}'
        })
        return self
    
    def avg(self, field: str, alias: Optional[str] = None) -> 'AggregationQueryBuilder':
        """Add AVG aggregation"""
        self.aggregations.append({
            'function': 'avg',
            'field': field,
            'alias': alias or f'avg_{field}'
        })
        return self
    
    def min(self, field: str, alias: Optional[str] = None) -> 'AggregationQueryBuilder':
        """Add MIN aggregation"""
        self.aggregations.append({
            'function': 'min',
            'field': field,
            'alias': alias or f'min_{field}'
        })
        return self
    
    def max(self, field: str, alias: Optional[str] = None) -> 'AggregationQueryBuilder':
        """Add MAX aggregation"""
        self.aggregations.append({
            'function': 'max',
            'field': field,
            'alias': alias or f'max_{field}'
        })
        return self
    
    def stddev(self, field: str, alias: Optional[str] = None) -> 'AggregationQueryBuilder':
        """Add STDDEV aggregation"""
        self.aggregations.append({
            'function': 'stddev',
            'field': field,
            'alias': alias or f'stddev_{field}'
        })
        return self
    
    def variance(self, field: str, alias: Optional[str] = None) -> 'AggregationQueryBuilder':
        """Add VARIANCE aggregation"""
        self.aggregations.append({
            'function': 'variance',
            'field': field,
            'alias': alias or f'variance_{field}'
        })
        return self
    
    def build_select(self) -> Select:
        """Build aggregation query"""
        if not self.aggregations:
            raise ValueError("No aggregations specified")
        
        # Build aggregation columns
        agg_columns = []
        for agg in self.aggregations:
            if agg['field'] == '*':
                column = text('*')
            elif hasattr(self.model, agg['field']):
                column = getattr(self.model, agg['field'])
            else:
                column = text(agg['field'])
            
            # Apply aggregation function
            func_name = agg['function']
            if func_name == 'count':
                if agg['field'] == '*':
                    agg_expr = func.count()
                else:
                    agg_expr = func.count(column)
            else:
                agg_expr = getattr(func, func_name)(column)
            
            agg_columns.append(agg_expr.label(agg['alias']))
        
        # Add group by columns to select
        group_columns = []
        for field in self._group_by_fields:
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                group_columns.append(column)
                agg_columns.append(column)
        
        # Create query
        query = select(*agg_columns)
        
        # Add FROM clause
        query = query.select_from(self.model)
        
        # Add JOINs
        for join_condition in self.joins:
            query = self._apply_join(query, join_condition)
        
        # Add WHERE conditions
        if self.filters:
            where_clause = self._build_where_clause()
            query = query.where(where_clause)
        
        # Add GROUP BY
        if group_columns:
            query = query.group_by(*group_columns)
        
        # Add HAVING
        if self._having_conditions:
            having_clause = self._build_having_clause()
            query = query.having(having_clause)
        
        # Add ORDER BY
        if self.sorts:
            for sort_condition in self.sorts:
                query = self._apply_sort(query, sort_condition)
        
        return query


class JoinQueryBuilder(QueryBuilder):
    """
    Specialized query builder for complex joins:
    - Multiple table joins
    - Self joins
    - Lateral joins
    - Cross joins
    """
    
    def __init__(self, model: Type[T]):
        super().__init__(model)
        self.table_aliases: Dict[str, str] = {}
        
    def add_table_alias(self, table: Union[str, Type[T]], alias: str) -> 'JoinQueryBuilder':
        """Add table alias mapping"""
        table_name = table.__tablename__ if hasattr(table, '__tablename__') else str(table)
        self.table_aliases[alias] = table_name
        return self
    
    def cross_join(self, table: Union[str, Type[T]], alias: Optional[str] = None) -> 'JoinQueryBuilder':
        """Add CROSS JOIN"""
        return self.join(table, JoinType.CROSS, alias=alias)
    
    def self_join(self, alias: str, on_condition: str) -> 'JoinQueryBuilder':
        """Add self join"""
        return self.join(self.model, JoinType.INNER, on_condition, alias)
    
    def lateral_join(self, subquery: Select, alias: str) -> 'JoinQueryBuilder':
        """Add LATERAL JOIN (PostgreSQL specific)"""
        # Note: This is a simplified implementation
        # Full lateral join support would require more complex SQLAlchemy usage
        logger.warning("Lateral joins require manual SQL construction in SQLAlchemy")
        return self
    
    def build_select(self) -> Select:
        """Build query with complex joins"""
        query = super().build_select()
        
        # Apply table aliases
        if self.table_aliases:
            for alias, table_name in self.table_aliases.items():
                # This would require more complex alias handling in SQLAlchemy
                pass
        
        return query


class SubQueryBuilder(QueryBuilder):
    """
    Specialized query builder for subqueries:
    - Correlated subqueries
    - EXISTS/NOT EXISTS
    - IN subqueries
    - Scalar subqueries
    """
    
    def __init__(self, model: Type[T]):
        super().__init__(model)
        self.exists_conditions: List[Dict[str, Any]] = []
        
    def where_exists(self, subquery: Select, negated: bool = False) -> 'SubQueryBuilder':
        """Add EXISTS condition"""
        self.exists_conditions.append({
            'subquery': subquery,
            'negated': negated
        })
        return self
    
    def where_not_exists(self, subquery: Select) -> 'SubQueryBuilder':
        """Add NOT EXISTS condition"""
        return self.where_exists(subquery, negated=True)
    
    def where_in_subquery(self, field: str, subquery: Select,
                         table_alias: Optional[str] = None) -> 'SubQueryBuilder':
        """Add IN subquery condition"""
        # Convert subquery to scalar subquery for IN operation
        scalar_subquery = subquery.scalar_subquery()
        return self.where(field, FilterOperator.IN, scalar_subquery, table_alias)
    
    def build_select(self) -> Select:
        """Build query with subqueries"""
        query = super().build_select()
        
        # Add EXISTS conditions
        for exists_condition in self.exists_conditions:
            if exists_condition['negated']:
                query = query.where(~exists(exists_condition['subquery']))
            else:
                query = query.where(exists(exists_condition['subquery']))
        
        return query
    
    def as_scalar_subquery(self) -> Select:
        """Return query as scalar subquery"""
        return self.build_select().scalar_subquery()
    
    def as_cte(self, name: str) -> Select:
        """Return query as CTE"""
        return self.build_select().cte(name)
