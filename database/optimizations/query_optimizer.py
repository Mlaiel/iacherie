"""
Query Optimizer Module

Advanced SQL query optimization engine with cost-based optimization, execution plan analysis,
and intelligent query rewriting for maximum database performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import re
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import sqlparse
from sqlparse import sql, tokens as T
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ...core.logging import get_logger
from ...core.config import settings
from ...core.metrics import MetricsCollector

logger = get_logger(__name__)


class OptimizationType(Enum):
    """Types of query optimizations"""
    INDEX_SUGGESTION = "index_suggestion"
    QUERY_REWRITE = "query_rewrite"
    JOIN_OPTIMIZATION = "join_optimization"
    WHERE_OPTIMIZATION = "where_optimization"
    SUBQUERY_OPTIMIZATION = "subquery_optimization"
    FUNCTION_OPTIMIZATION = "function_optimization"
    LIMIT_OPTIMIZATION = "limit_optimization"
    UNION_OPTIMIZATION = "union_optimization"


class QueryType(Enum):
    """SQL query types"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"
    UNKNOWN = "unknown"


class JoinType(Enum):
    """SQL join types"""
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    FULL = "full"
    CROSS = "cross"


@dataclass
class QueryComponent:
    """Parsed query component"""
    tables: List[str] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)
    where_conditions: List[str] = field(default_factory=list)
    joins: List[Dict[str, Any]] = field(default_factory=list)
    order_by: List[str] = field(default_factory=list)
    group_by: List[str] = field(default_factory=list)
    having_conditions: List[str] = field(default_factory=list)
    subqueries: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    limits: Optional[int] = None
    offset: Optional[int] = None
    
    @property
    def complexity_score(self) -> int:
        """Calculate query complexity score"""
        score = 0
        score += len(self.tables) * 2
        score += len(self.joins) * 5
        score += len(self.where_conditions) * 2
        score += len(self.subqueries) * 10
        score += len(self.functions) * 3
        score += len(self.order_by) * 1
        score += len(self.group_by) * 3
        return score


@dataclass
class ExecutionPlan:
    """Query execution plan representation"""
    plan_id: str
    query_text: str
    estimated_cost: float
    estimated_rows: int
    execution_time: Optional[float] = None
    plan_nodes: List[Dict[str, Any]] = field(default_factory=list)
    index_usage: List[str] = field(default_factory=list)
    table_scans: List[str] = field(default_factory=list)
    join_methods: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def efficiency_score(self) -> float:
        """Calculate plan efficiency score (0-100)"""
        score = 100.0
        
        # Penalize table scans
        score -= len(self.table_scans) * 20
        
        # Penalize high cost
        if self.estimated_cost > 1000:
            score -= 30
        elif self.estimated_cost > 100:
            score -= 15
        elif self.estimated_cost > 10:
            score -= 5
        
        # Penalize no index usage
        if not self.index_usage and self.table_scans:
            score -= 25
        
        # Penalize warnings
        score -= len(self.warnings) * 10
        
        return max(0.0, score)


@dataclass
class OptimizationSuggestion:
    """Query optimization suggestion"""
    optimization_type: OptimizationType
    priority: int  # 1-10 scale
    description: str
    original_query: str
    optimized_query: Optional[str] = None
    estimated_improvement: float = 0.0  # Percentage
    rationale: str = ""
    index_suggestions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def impact_score(self) -> float:
        """Calculate potential impact score"""
        return self.priority * 10 + self.estimated_improvement


@dataclass
class QueryPlan:
    """Complete query analysis and optimization plan"""
    query_id: str
    original_query: str
    query_type: QueryType
    components: QueryComponent
    execution_plan: Optional[ExecutionPlan] = None
    optimizations: List[OptimizationSuggestion] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def optimization_potential(self) -> float:
        """Calculate overall optimization potential"""
        if not self.optimizations:
            return 0.0
        return sum(opt.impact_score for opt in self.optimizations) / len(self.optimizations)


class QueryParser:
    """Advanced SQL query parser"""
    
    def __init__(self):
        self._function_patterns = [
            r'\b(count|sum|avg|max|min|string_agg|array_agg)\s*\(',
            r'\b(upper|lower|trim|substring|length)\s*\(',
            r'\b(date_trunc|extract|now|current_timestamp)\s*\(',
        ]
    
    def parse_query(self, query: str) -> QueryComponent:
        """Parse SQL query into components"""
        try:
            # Parse with sqlparse
            parsed = sqlparse.parse(query)[0]
            
            component = QueryComponent()
            
            # Extract components
            component.tables = self._extract_tables(parsed)
            component.columns = self._extract_columns(parsed)
            component.where_conditions = self._extract_where_conditions(parsed)
            component.joins = self._extract_joins(parsed)
            component.order_by = self._extract_order_by(parsed)
            component.group_by = self._extract_group_by(parsed)
            component.having_conditions = self._extract_having(parsed)
            component.subqueries = self._extract_subqueries(parsed)
            component.functions = self._extract_functions(query)
            component.limits, component.offset = self._extract_limit_offset(parsed)
            
            return component
            
        except Exception as e:
            logger.warning(f"Failed to parse query: {e}")
            return QueryComponent()
    
    def _extract_tables(self, parsed) -> List[str]:
        """Extract table names from parsed query"""
        tables = []
        
        def extract_from_token(token):
            if isinstance(token, sql.IdentifierList):
                for identifier in token.get_identifiers():
                    tables.append(str(identifier.get_real_name() or identifier).strip())
            elif isinstance(token, sql.Identifier):
                tables.append(str(token.get_real_name() or token).strip())
            elif token.ttype is None and isinstance(token, sql.Token):
                # Simple table name
                tables.append(str(token).strip())
        
        # Find FROM clause
        in_from = False
        for token in parsed.flatten():
            if token.ttype is T.Keyword and token.value.upper() == 'FROM':
                in_from = True
                continue
            elif token.ttype is T.Keyword and token.value.upper() in ('WHERE', 'GROUP', 'ORDER', 'LIMIT', 'HAVING'):
                in_from = False
            elif in_from and token.ttype not in (T.Whitespace, T.Punctuation):
                if isinstance(token, sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        tables.append(str(identifier.get_real_name() or identifier).strip())
                elif isinstance(token, sql.Identifier):
                    tables.append(str(token.get_real_name() or token).strip())
                elif not token.is_keyword:
                    tables.append(str(token).strip())
        
        # Clean up table names
        cleaned_tables = []
        for table in tables:
            table = table.strip('(),').strip()
            if table and not table.upper() in ('AS', 'ON', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL'):
                cleaned_tables.append(table)
        
        return list(set(cleaned_tables))
    
    def _extract_columns(self, parsed) -> List[str]:
        """Extract column names from SELECT clause"""
        columns = []
        
        # Find SELECT clause
        in_select = False
        for token in parsed.flatten():
            if token.ttype is T.Keyword.DML and token.value.upper() == 'SELECT':
                in_select = True
                continue
            elif token.ttype is T.Keyword and token.value.upper() == 'FROM':
                in_select = False
            elif in_select and token.ttype not in (T.Whitespace, T.Punctuation):
                if isinstance(token, sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        columns.append(str(identifier).strip())
                elif isinstance(token, sql.Identifier):
                    columns.append(str(token).strip())
                elif not token.is_keyword and str(token) != '*':
                    columns.append(str(token).strip())
        
        return [col for col in columns if col and col != ',']
    
    def _extract_where_conditions(self, parsed) -> List[str]:
        """Extract WHERE conditions"""
        conditions = []
        where_clause = None
        
        # Find WHERE clause
        for token in parsed.tokens:
            if token.ttype is T.Keyword and token.value.upper() == 'WHERE':
                # Get the next token which should be the WHERE clause
                idx = parsed.tokens.index(token)
                if idx + 1 < len(parsed.tokens):
                    where_clause = parsed.tokens[idx + 1]
                break
        
        if where_clause:
            # Split by AND/OR
            where_str = str(where_clause).strip()
            # Simple split by AND/OR
            parts = re.split(r'\s+(?:AND|OR)\s+', where_str, flags=re.IGNORECASE)
            conditions = [part.strip() for part in parts if part.strip()]
        
        return conditions
    
    def _extract_joins(self, parsed) -> List[Dict[str, Any]]:
        """Extract JOIN information"""
        joins = []
        
        query_str = str(parsed)
        join_patterns = [
            r'(INNER\s+)?JOIN\s+(\w+)\s+(?:AS\s+\w+\s+)?ON\s+([^WHERE|GROUP|ORDER|LIMIT]+)',
            r'LEFT\s+(?:OUTER\s+)?JOIN\s+(\w+)\s+(?:AS\s+\w+\s+)?ON\s+([^WHERE|GROUP|ORDER|LIMIT]+)',
            r'RIGHT\s+(?:OUTER\s+)?JOIN\s+(\w+)\s+(?:AS\s+\w+\s+)?ON\s+([^WHERE|GROUP|ORDER|LIMIT]+)',
            r'FULL\s+(?:OUTER\s+)?JOIN\s+(\w+)\s+(?:AS\s+\w+\s+)?ON\s+([^WHERE|GROUP|ORDER|LIMIT]+)',
        ]
        
        for pattern in join_patterns:
            matches = re.finditer(pattern, query_str, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    join_type = "INNER"
                    if "LEFT" in match.group(0).upper():
                        join_type = "LEFT"
                    elif "RIGHT" in match.group(0).upper():
                        join_type = "RIGHT"
                    elif "FULL" in match.group(0).upper():
                        join_type = "FULL"
                    
                    joins.append({
                        "type": join_type,
                        "table": groups[-2] if len(groups) > 2 else groups[0],
                        "condition": groups[-1].strip()
                    })
        
        return joins
    
    def _extract_order_by(self, parsed) -> List[str]:
        """Extract ORDER BY columns"""
        order_columns = []
        
        query_str = str(parsed)
        order_match = re.search(r'ORDER\s+BY\s+([^LIMIT]+)', query_str, re.IGNORECASE)
        if order_match:
            order_clause = order_match.group(1).strip()
            # Split by comma
            columns = [col.strip() for col in order_clause.split(',')]
            order_columns = [col for col in columns if col]
        
        return order_columns
    
    def _extract_group_by(self, parsed) -> List[str]:
        """Extract GROUP BY columns"""
        group_columns = []
        
        query_str = str(parsed)
        group_match = re.search(r'GROUP\s+BY\s+([^HAVING|ORDER|LIMIT]+)', query_str, re.IGNORECASE)
        if group_match:
            group_clause = group_match.group(1).strip()
            columns = [col.strip() for col in group_clause.split(',')]
            group_columns = [col for col in columns if col]
        
        return group_columns
    
    def _extract_having(self, parsed) -> List[str]:
        """Extract HAVING conditions"""
        having_conditions = []
        
        query_str = str(parsed)
        having_match = re.search(r'HAVING\s+([^ORDER|LIMIT]+)', query_str, re.IGNORECASE)
        if having_match:
            having_clause = having_match.group(1).strip()
            # Split by AND/OR
            parts = re.split(r'\s+(?:AND|OR)\s+', having_clause, flags=re.IGNORECASE)
            having_conditions = [part.strip() for part in parts if part.strip()]
        
        return having_conditions
    
    def _extract_subqueries(self, parsed) -> List[str]:
        """Extract subqueries"""
        subqueries = []
        
        query_str = str(parsed)
        # Find parenthesized SELECT statements
        subquery_pattern = r'\(([^()]*SELECT[^()]*)\)'
        matches = re.finditer(subquery_pattern, query_str, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            subquery = match.group(1).strip()
            if subquery:
                subqueries.append(subquery)
        
        return subqueries
    
    def _extract_functions(self, query: str) -> List[str]:
        """Extract function calls"""
        functions = []
        
        for pattern in self._function_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                function_name = match.group(1) if match.groups() else match.group(0)
                functions.append(function_name.lower())
        
        return list(set(functions))
    
    def _extract_limit_offset(self, parsed) -> Tuple[Optional[int], Optional[int]]:
        """Extract LIMIT and OFFSET values"""
        query_str = str(parsed)
        
        limit = None
        offset = None
        
        # LIMIT clause
        limit_match = re.search(r'LIMIT\s+(\d+)', query_str, re.IGNORECASE)
        if limit_match:
            limit = int(limit_match.group(1))
        
        # OFFSET clause
        offset_match = re.search(r'OFFSET\s+(\d+)', query_str, re.IGNORECASE)
        if offset_match:
            offset = int(offset_match.group(1))
        
        return limit, offset


class QueryOptimizer:
    """Advanced SQL query optimizer"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.parser = QueryParser()
        self.metrics_collector = MetricsCollector()
        
        # Optimization rules
        self._optimization_rules = [
            self._optimize_where_conditions,
            self._optimize_joins,
            self._optimize_subqueries,
            self._optimize_functions,
            self._optimize_limits,
            self._suggest_indexes,
        ]
        
        # Query patterns and their optimizations
        self._query_cache: Dict[str, QueryPlan] = {}
        
    async def analyze_query(self, query: str) -> QueryPlan:
        """Analyze query and create optimization plan"""
        try:
            # Generate query ID
            query_id = self._generate_query_id(query)
            
            # Check cache
            if query_id in self._query_cache:
                cached_plan = self._query_cache[query_id]
                # Update timestamp
                cached_plan.analysis_timestamp = datetime.now()
                return cached_plan
            
            logger.debug(f"Analyzing query: {query[:100]}...")
            
            # Determine query type
            query_type = self._determine_query_type(query)
            
            # Parse query components
            components = self.parser.parse_query(query)
            
            # Create initial plan
            plan = QueryPlan(
                query_id=query_id,
                original_query=query,
                query_type=query_type,
                components=components
            )
            
            # Generate optimizations
            plan.optimizations = await self._generate_optimizations(plan)
            
            # Cache the plan
            self._query_cache[query_id] = plan
            
            # Send metrics
            self.metrics_collector.counter(
                "query_optimizer_analyses_total",
                1,
                {"query_type": query_type.value}
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            raise
    
    async def get_execution_plan(self, engine: AsyncEngine, query: str) -> Optional[ExecutionPlan]:
        """Get query execution plan from database"""
        try:
            async with engine.begin() as conn:
                # Get execution plan (PostgreSQL)
                explain_query = f"EXPLAIN (ANALYZE false, VERBOSE true, BUFFERS false, FORMAT JSON) {query}"
                result = await conn.execute(text(explain_query))
                plan_data = result.fetchone()[0]
                
                if isinstance(plan_data, list) and plan_data:
                    plan_info = plan_data[0]['Plan']
                    
                    # Extract plan information
                    execution_plan = ExecutionPlan(
                        plan_id=self._generate_plan_id(query),
                        query_text=query,
                        estimated_cost=plan_info.get('Total Cost', 0),
                        estimated_rows=plan_info.get('Plan Rows', 0),
                        plan_nodes=self._extract_plan_nodes(plan_info)
                    )
                    
                    # Extract index usage and table scans
                    execution_plan.index_usage = self._extract_index_usage(plan_info)
                    execution_plan.table_scans = self._extract_table_scans(plan_info)
                    execution_plan.join_methods = self._extract_join_methods(plan_info)
                    
                    return execution_plan
                
        except Exception as e:
            logger.warning(f"Failed to get execution plan: {e}")
            return None
    
    async def _generate_optimizations(self, plan: QueryPlan) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions for query plan"""
        optimizations = []
        
        # Apply optimization rules
        for rule in self._optimization_rules:
            suggestions = await rule(plan)
            optimizations.extend(suggestions)
        
        # Sort by priority and impact
        optimizations.sort(key=lambda x: (-x.priority, -x.estimated_improvement))
        
        return optimizations
    
    async def _optimize_where_conditions(self, plan: QueryPlan) -> List[OptimizationSuggestion]:
        """Optimize WHERE conditions"""
        suggestions = []
        
        for condition in plan.components.where_conditions:
            # Check for function calls on columns (prevent index usage)
            if re.search(r'\w+\s*\(\s*\w+\s*\)', condition):
                suggestions.append(OptimizationSuggestion(
                    optimization_type=OptimizationType.WHERE_OPTIMIZATION,
                    priority=7,
                    description="Avoid functions on columns in WHERE clause",
                    original_query=plan.original_query,
                    rationale="Functions on columns prevent index usage",
                    estimated_improvement=20.0
                ))
            
            # Check for leading wildcards in LIKE
            if re.search(r"LIKE\s+'%", condition, re.IGNORECASE):
                suggestions.append(OptimizationSuggestion(
                    optimization_type=OptimizationType.WHERE_OPTIMIZATION,
                    priority=6,
                    description="Avoid leading wildcards in LIKE patterns",
                    original_query=plan.original_query,
                    rationale="Leading wildcards prevent index usage",
                    estimated_improvement=15.0
                ))
            
            # Check for OR conditions (suggest UNION)
            if ' OR ' in condition.upper():
                suggestions.append(OptimizationSuggestion(
                    optimization_type=OptimizationType.QUERY_REWRITE,
                    priority=5,
                    description="Consider rewriting OR conditions as UNION",
                    original_query=plan.original_query,
                    rationale="UNION can be more efficient than OR for some queries",
                    estimated_improvement=10.0
                ))
        
        return suggestions
    
    async def _optimize_joins(self, plan: QueryPlan) -> List[OptimizationSuggestion]:
        """Optimize JOIN operations"""
        suggestions = []
        
        # Check for Cartesian products (missing JOIN conditions)
        total_tables = len(plan.components.tables)
        total_joins = len(plan.components.joins)
        
        if total_tables > 1 and total_joins < (total_tables - 1):
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.JOIN_OPTIMIZATION,
                priority=9,
                description="Possible Cartesian product detected",
                original_query=plan.original_query,
                rationale="Missing JOIN conditions can cause Cartesian products",
                estimated_improvement=50.0,
                warnings=["Review JOIN conditions to avoid Cartesian products"]
            ))
        
        # Suggest JOIN order optimization for many tables
        if total_tables > 3:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.JOIN_OPTIMIZATION,
                priority=6,
                description="Consider JOIN order optimization",
                original_query=plan.original_query,
                rationale="Optimal JOIN order can significantly improve performance",
                estimated_improvement=25.0
            ))
        
        # Check for inefficient JOIN types
        for join in plan.components.joins:
            if join['type'] == 'CROSS':
                suggestions.append(OptimizationSuggestion(
                    optimization_type=OptimizationType.JOIN_OPTIMIZATION,
                    priority=8,
                    description="Avoid CROSS JOINs when possible",
                    original_query=plan.original_query,
                    rationale="CROSS JOINs can be very expensive",
                    estimated_improvement=40.0
                ))
        
        return suggestions
    
    async def _optimize_subqueries(self, plan: QueryPlan) -> List[OptimizationSuggestion]:
        """Optimize subqueries"""
        suggestions = []
        
        if plan.components.subqueries:
            # Suggest converting correlated subqueries to JOINs
            for subquery in plan.components.subqueries:
                if 'WHERE' in subquery.upper():
                    suggestions.append(OptimizationSuggestion(
                        optimization_type=OptimizationType.SUBQUERY_OPTIMIZATION,
                        priority=7,
                        description="Consider converting subquery to JOIN",
                        original_query=plan.original_query,
                        rationale="JOINs are often more efficient than correlated subqueries",
                        estimated_improvement=30.0
                    ))
            
            # Suggest EXISTS instead of IN for large subqueries
            if len(plan.components.subqueries) > 1:
                suggestions.append(OptimizationSuggestion(
                    optimization_type=OptimizationType.SUBQUERY_OPTIMIZATION,
                    priority=6,
                    description="Consider using EXISTS instead of IN for subqueries",
                    original_query=plan.original_query,
                    rationale="EXISTS can be more efficient than IN for large result sets",
                    estimated_improvement=20.0
                ))
        
        return suggestions
    
    async def _optimize_functions(self, plan: QueryPlan) -> List[OptimizationSuggestion]:
        """Optimize function usage"""
        suggestions = []
        
        # Check for expensive functions
        expensive_functions = ['string_agg', 'array_agg', 'regexp_split_to_table']
        for func in plan.components.functions:
            if func in expensive_functions:
                suggestions.append(OptimizationSuggestion(
                    optimization_type=OptimizationType.FUNCTION_OPTIMIZATION,
                    priority=5,
                    description=f"Optimize {func} function usage",
                    original_query=plan.original_query,
                    rationale=f"{func} can be expensive on large datasets",
                    estimated_improvement=15.0
                ))
        
        # Suggest avoiding functions in WHERE clauses
        if plan.components.functions and plan.components.where_conditions:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.FUNCTION_OPTIMIZATION,
                priority=6,
                description="Avoid functions in WHERE clauses when possible",
                original_query=plan.original_query,
                rationale="Functions in WHERE prevent index usage",
                estimated_improvement=20.0
            ))
        
        return suggestions
    
    async def _optimize_limits(self, plan: QueryPlan) -> List[OptimizationSuggestion]:
        """Optimize LIMIT and OFFSET usage"""
        suggestions = []
        
        # Suggest using LIMIT for large result sets
        if not plan.components.limits and len(plan.components.tables) > 1:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.LIMIT_OPTIMIZATION,
                priority=4,
                description="Consider adding LIMIT to large queries",
                original_query=plan.original_query,
                rationale="LIMIT can prevent unnecessarily large result sets",
                estimated_improvement=10.0
            ))
        
        # Warn about large OFFSET values
        if plan.components.offset and plan.components.offset > 1000:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.LIMIT_OPTIMIZATION,
                priority=6,
                description="Large OFFSET values can be inefficient",
                original_query=plan.original_query,
                rationale="Consider cursor-based pagination instead of OFFSET",
                estimated_improvement=25.0
            ))
        
        return suggestions
    
    async def _suggest_indexes(self, plan: QueryPlan) -> List[OptimizationSuggestion]:
        """Suggest index optimizations"""
        suggestions = []
        index_suggestions = []
        
        # Indexes for WHERE conditions
        for condition in plan.components.where_conditions:
            # Extract column names from conditions
            column_matches = re.findall(r'\b(\w+)\s*[=<>!]', condition)
            for column in column_matches:
                for table in plan.components.tables:
                    index_suggestions.append(f"CREATE INDEX idx_{table}_{column} ON {table} ({column});")
        
        # Indexes for JOIN conditions
        for join in plan.components.joins:
            condition = join.get('condition', '')
            column_matches = re.findall(r'\b(\w+)\s*=\s*\w+\.(\w+)', condition)
            for match in column_matches:
                left_col, right_col = match
                index_suggestions.append(f"CREATE INDEX idx_join_{left_col} ON table ({left_col});")
                index_suggestions.append(f"CREATE INDEX idx_join_{right_col} ON table ({right_col});")
        
        # Indexes for ORDER BY
        if plan.components.order_by:
            for table in plan.components.tables:
                order_columns = [col.split()[0] for col in plan.components.order_by]  # Remove ASC/DESC
                if order_columns:
                    columns_str = ', '.join(order_columns)
                    index_suggestions.append(f"CREATE INDEX idx_{table}_order ON {table} ({columns_str});")
        
        if index_suggestions:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.INDEX_SUGGESTION,
                priority=8,
                description=f"Consider creating {len(index_suggestions)} indexes",
                original_query=plan.original_query,
                rationale="Indexes can significantly improve query performance",
                estimated_improvement=40.0,
                index_suggestions=list(set(index_suggestions))  # Remove duplicates
            ))
        
        return suggestions
    
    def _determine_query_type(self, query: str) -> QueryType:
        """Determine the type of SQL query"""
        query_upper = query.strip().upper()
        
        if query_upper.startswith('SELECT'):
            return QueryType.SELECT
        elif query_upper.startswith('INSERT'):
            return QueryType.INSERT
        elif query_upper.startswith('UPDATE'):
            return QueryType.UPDATE
        elif query_upper.startswith('DELETE'):
            return QueryType.DELETE
        elif query_upper.startswith('CREATE'):
            return QueryType.CREATE
        elif query_upper.startswith('ALTER'):
            return QueryType.ALTER
        elif query_upper.startswith('DROP'):
            return QueryType.DROP
        else:
            return QueryType.UNKNOWN
    
    def _generate_query_id(self, query: str) -> str:
        """Generate unique query ID"""
        normalized = self._normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _generate_plan_id(self, query: str) -> str:
        """Generate unique plan ID"""
        return f"plan_{self._generate_query_id(query)}"
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for comparison"""
        import re
        
        normalized = query.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = re.sub(r"'[^']*'", "?", normalized)
        normalized = re.sub(r'\b\d+\b', "?", normalized)
        
        return normalized
    
    def _extract_plan_nodes(self, plan_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract plan nodes from execution plan"""
        nodes = []
        
        def extract_node(node):
            node_info = {
                "node_type": node.get("Node Type"),
                "relation_name": node.get("Relation Name"),
                "total_cost": node.get("Total Cost"),
                "plan_rows": node.get("Plan Rows"),
                "plan_width": node.get("Plan Width"),
            }
            nodes.append(node_info)
            
            # Recursively extract child nodes
            for child in node.get("Plans", []):
                extract_node(child)
        
        extract_node(plan_info)
        return nodes
    
    def _extract_index_usage(self, plan_info: Dict[str, Any]) -> List[str]:
        """Extract index usage from execution plan"""
        indexes = []
        
        def extract_indexes(node):
            if node.get("Node Type") == "Index Scan":
                index_name = node.get("Index Name")
                if index_name:
                    indexes.append(index_name)
            
            for child in node.get("Plans", []):
                extract_indexes(child)
        
        extract_indexes(plan_info)
        return indexes
    
    def _extract_table_scans(self, plan_info: Dict[str, Any]) -> List[str]:
        """Extract table scans from execution plan"""
        scans = []
        
        def extract_scans(node):
            if node.get("Node Type") == "Seq Scan":
                relation_name = node.get("Relation Name")
                if relation_name:
                    scans.append(relation_name)
            
            for child in node.get("Plans", []):
                extract_scans(child)
        
        extract_scans(plan_info)
        return scans
    
    def _extract_join_methods(self, plan_info: Dict[str, Any]) -> List[str]:
        """Extract join methods from execution plan"""
        joins = []
        
        def extract_joins(node):
            node_type = node.get("Node Type", "")
            if "Join" in node_type:
                joins.append(node_type)
            
            for child in node.get("Plans", []):
                extract_joins(child)
        
        extract_joins(plan_info)
        return joins
    
    async def optimize_query(self, query: str) -> str:
        """Apply basic query optimizations and return optimized query"""
        try:
            # This is a simplified implementation
            # In a real system, you'd implement sophisticated query rewriting
            
            optimized = query
            
            # Remove unnecessary whitespace
            optimized = re.sub(r'\s+', ' ', optimized).strip()
            
            # Add LIMIT if missing and query looks like it could return many rows
            if ('SELECT' in optimized.upper() and 
                'LIMIT' not in optimized.upper() and 
                'JOIN' in optimized.upper()):
                
                # Don't add LIMIT if there's already aggregation
                if not any(func in optimized.upper() for func in ['COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(']):
                    optimized += " LIMIT 1000"
            
            return optimized
            
        except Exception as e:
            logger.warning(f"Query optimization failed: {e}")
            return query
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics"""
        return {
            "cached_plans": len(self._query_cache),
            "optimization_rules": len(self._optimization_rules),
            "total_analyses": sum(1 for plan in self._query_cache.values()),
            "avg_optimizations_per_query": (
                sum(len(plan.optimizations) for plan in self._query_cache.values()) / 
                len(self._query_cache) if self._query_cache else 0
            ),
        }
    
    def clear_cache(self, older_than_hours: int = 24) -> None:
        """Clear old cached plans"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        old_plans = [
            query_id for query_id, plan in self._query_cache.items()
            if plan.analysis_timestamp < cutoff_time
        ]
        
        for query_id in old_plans:
            del self._query_cache[query_id]
        
        logger.info(f"Cleared {len(old_plans)} old query plans from cache")


# Global query optimizer instance
_query_optimizer: Optional[QueryOptimizer] = None


def get_query_optimizer(config: Optional[Dict[str, Any]] = None) -> QueryOptimizer:
    """Get global query optimizer instance"""
    global _query_optimizer
    
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer(config)
    
    return _query_optimizer


# Execution planner helper classes
class PlanOptimizer:
    """Advanced execution plan optimizer"""
    
    @staticmethod
    async def optimize_execution_plan(engine: AsyncEngine, query: str) -> Optional[str]:
        """Optimize query based on execution plan analysis"""
        optimizer = get_query_optimizer()
        
        # Get execution plan
        plan = await optimizer.get_execution_plan(engine, query)
        if not plan:
            return query
        
        # Apply plan-based optimizations
        optimized_query = query
        
        # If there are table scans, suggest adding LIMIT
        if plan.table_scans and 'LIMIT' not in query.upper():
            optimized_query += " LIMIT 1000"
        
        return optimized_query


class CostEstimator:
    """Query cost estimation utilities"""
    
    @staticmethod
    def estimate_query_cost(components: QueryComponent) -> float:
        """Estimate query execution cost based on components"""
        cost = 1.0
        
        # Table costs
        cost += len(components.tables) * 10
        
        # Join costs (exponential)
        if components.joins:
            cost *= (2 ** len(components.joins))
        
        # Subquery costs
        cost += len(components.subqueries) * 50
        
        # Function costs
        cost += len(components.functions) * 5
        
        # WHERE condition costs
        cost += len(components.where_conditions) * 2
        
        # ORDER BY costs
        if components.order_by:
            cost += len(components.order_by) * 3
            
        # GROUP BY costs
        if components.group_by:
            cost += len(components.group_by) * 8
        
        return cost
