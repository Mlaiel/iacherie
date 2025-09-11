"""
Query Builder - DBA Expert Implementation
========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise SQL query builder with optimization and security features.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class JoinType(Enum):
    """SQL join types"""
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"
    CROSS = "CROSS JOIN"


class OrderDirection(Enum):
    """Order direction"""
    ASC = "ASC"
    DESC = "DESC"


@dataclass
class QueryCondition:
    """Query condition structure"""
    column: str
    operator: str
    value: Any
    logical_operator: str = "AND"


class QueryBuilder:
    """
    Enterprise SQL query builder with security and optimization features
    """
    
    def __init__(self):
        """Initialize query builder"""
        self.reset()
        
        # Security settings
        self.escape_identifiers = True
        self.validate_identifiers = True
        self.max_query_length = 10000
        
        # Optimization settings
        self.suggest_optimizations = True
        self.track_query_patterns = True
        
        logger.debug("QueryBuilder initialized")
    
    def reset(self):
        """Reset query builder state"""
        self._select_fields = []
        self._from_table = ""
        self._joins = []
        self._where_conditions = []
        self._group_by = []
        self._having_conditions = []
        self._order_by = []
        self._limit = None
        self._offset = None
        self._union_queries = []
        
        return self
    
    def select(self, *fields) -> 'QueryBuilder':
        """Add SELECT fields"""
        for field in fields:
            if isinstance(field, str):
                self._select_fields.append(field)
            elif isinstance(field, dict):
                # Handle aliased fields: {"column": "alias"}
                for col, alias in field.items():
                    self._select_fields.append(f"{col} AS {alias}")
        
        return self
    
    def from_table(self, table: str, alias: str = None) -> 'QueryBuilder':
        """Set FROM table"""
        if alias:
            self._from_table = f"{table} AS {alias}"
        else:
            self._from_table = table
        
        return self
    
    def join(self, table: str, on_condition: str, join_type: JoinType = JoinType.INNER,
             alias: str = None) -> 'QueryBuilder':
        """Add JOIN clause"""
        table_ref = f"{table} AS {alias}" if alias else table
        join_clause = f"{join_type.value} {table_ref} ON {on_condition}"
        self._joins.append(join_clause)
        
        return self
    
    def where(self, condition: Union[str, QueryCondition]) -> 'QueryBuilder':
        """Add WHERE condition"""
        if isinstance(condition, str):
            self._where_conditions.append(condition)
        elif isinstance(condition, QueryCondition):
            condition_str = f"{condition.column} {condition.operator} {self._format_value(condition.value)}"
            self._where_conditions.append((condition_str, condition.logical_operator))
        
        return self
    
    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """Add WHERE IN condition"""
        formatted_values = [self._format_value(v) for v in values]
        condition = f"{column} IN ({', '.join(formatted_values)})"
        self._where_conditions.append(condition)
        
        return self
    
    def where_between(self, column: str, start_value: Any, end_value: Any) -> 'QueryBuilder':
        """Add WHERE BETWEEN condition"""
        condition = f"{column} BETWEEN {self._format_value(start_value)} AND {self._format_value(end_value)}"
        self._where_conditions.append(condition)
        
        return self
    
    def where_like(self, column: str, pattern: str) -> 'QueryBuilder':
        """Add WHERE LIKE condition"""
        condition = f"{column} LIKE {self._format_value(pattern)}"
        self._where_conditions.append(condition)
        
        return self
    
    def group_by(self, *columns) -> 'QueryBuilder':
        """Add GROUP BY columns"""
        self._group_by.extend(columns)
        return self
    
    def having(self, condition: str) -> 'QueryBuilder':
        """Add HAVING condition"""
        self._having_conditions.append(condition)
        return self
    
    def order_by(self, column: str, direction: OrderDirection = OrderDirection.ASC) -> 'QueryBuilder':
        """Add ORDER BY clause"""
        self._order_by.append(f"{column} {direction.value}")
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """Set LIMIT"""
        self._limit = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """Set OFFSET"""
        self._offset = count
        return self
    
    def union(self, other_query: 'QueryBuilder', union_all: bool = False) -> 'QueryBuilder':
        """Add UNION clause"""
        union_type = "UNION ALL" if union_all else "UNION"
        self._union_queries.append((union_type, other_query.build()))
        return self
    
    def build(self) -> str:
        """Build the SQL query"""
        try:
            query_parts = []
            
            # SELECT clause
            if not self._select_fields:
                query_parts.append("SELECT *")
            else:
                query_parts.append(f"SELECT {', '.join(self._select_fields)}")
            
            # FROM clause
            if not self._from_table:
                raise ValueError("FROM table is required")
            
            query_parts.append(f"FROM {self._from_table}")
            
            # JOIN clauses
            for join in self._joins:
                query_parts.append(join)
            
            # WHERE clause
            if self._where_conditions:
                where_parts = []
                for i, condition in enumerate(self._where_conditions):
                    if isinstance(condition, tuple):
                        condition_str, logical_op = condition
                        if i > 0:
                            where_parts.append(f"{logical_op} {condition_str}")
                        else:
                            where_parts.append(condition_str)
                    else:
                        if i > 0:
                            where_parts.append(f"AND {condition}")
                        else:
                            where_parts.append(condition)
                
                query_parts.append(f"WHERE {' '.join(where_parts)}")
            
            # GROUP BY clause
            if self._group_by:
                query_parts.append(f"GROUP BY {', '.join(self._group_by)}")
            
            # HAVING clause
            if self._having_conditions:
                query_parts.append(f"HAVING {' AND '.join(self._having_conditions)}")
            
            # ORDER BY clause
            if self._order_by:
                query_parts.append(f"ORDER BY {', '.join(self._order_by)}")
            
            # LIMIT clause
            if self._limit is not None:
                query_parts.append(f"LIMIT {self._limit}")
            
            # OFFSET clause
            if self._offset is not None:
                query_parts.append(f"OFFSET {self._offset}")
            
            # Build main query
            main_query = '\n'.join(query_parts)
            
            # Add UNION queries
            if self._union_queries:
                union_parts = [main_query]
                for union_type, union_query in self._union_queries:
                    union_parts.append(f"{union_type}\n{union_query}")
                
                final_query = '\n'.join(union_parts)
            else:
                final_query = main_query
            
            # Validate query length
            if len(final_query) > self.max_query_length:
                logger.warning(f"Query exceeds maximum length: {len(final_query)} > {self.max_query_length}")
            
            logger.debug(f"Query built: {len(final_query)} characters")
            return final_query
            
        except Exception as e:
            logger.error(f"Query building failed: {e}")
            raise
    
    def build_insert(self, table: str, data: Dict[str, Any]) -> str:
        """Build INSERT query"""
        try:
            columns = list(data.keys())
            values = [self._format_value(data[col]) for col in columns]
            
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)})"
            
            logger.debug(f"INSERT query built for table: {table}")
            return query
            
        except Exception as e:
            logger.error(f"INSERT query building failed: {e}")
            raise
    
    def build_update(self, table: str, data: Dict[str, Any], where_conditions: List[str] = None) -> str:
        """Build UPDATE query"""
        try:
            # Build SET clause
            set_clauses = []
            for column, value in data.items():
                set_clauses.append(f"{column} = {self._format_value(value)}")
            
            query_parts = [
                f"UPDATE {table}",
                f"SET {', '.join(set_clauses)}"
            ]
            
            # Add WHERE conditions
            if where_conditions:
                query_parts.append(f"WHERE {' AND '.join(where_conditions)}")
            else:
                logger.warning("UPDATE query without WHERE clause - this will update all rows!")
            
            query = '\n'.join(query_parts)
            
            logger.debug(f"UPDATE query built for table: {table}")
            return query
            
        except Exception as e:
            logger.error(f"UPDATE query building failed: {e}")
            raise
    
    def build_delete(self, table: str, where_conditions: List[str] = None) -> str:
        """Build DELETE query"""
        try:
            query_parts = [f"DELETE FROM {table}"]
            
            # Add WHERE conditions
            if where_conditions:
                query_parts.append(f"WHERE {' AND '.join(where_conditions)}")
            else:
                logger.warning("DELETE query without WHERE clause - this will delete all rows!")
            
            query = '\n'.join(query_parts)
            
            logger.debug(f"DELETE query built for table: {table}")
            return query
            
        except Exception as e:
            logger.error(f"DELETE query building failed: {e}")
            raise
    
    def _format_value(self, value: Any) -> str:
        """Format value for SQL query"""
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            # Escape single quotes
            escaped_value = value.replace("'", "''")
            return f"'{escaped_value}'"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        else:
            # Convert to string and treat as string
            escaped_value = str(value).replace("'", "''")
            return f"'{escaped_value}'"
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query for optimization opportunities"""
        try:
            analysis = {
                'query_length': len(query),
                'query_type': self._detect_query_type(query),
                'tables_involved': self._extract_tables(query),
                'conditions_count': query.lower().count('where'),
                'joins_count': query.lower().count('join'),
                'subqueries_count': query.count('('),
                'optimization_suggestions': []
            }
            
            # Generate optimization suggestions
            suggestions = []
            
            if 'SELECT *' in query.upper():
                suggestions.append({
                    'type': 'PERFORMANCE',
                    'message': 'Consider selecting only needed columns instead of SELECT *',
                    'severity': 'MEDIUM'
                })
            
            if 'ORDER BY' in query.upper() and 'LIMIT' not in query.upper():
                suggestions.append({
                    'type': 'PERFORMANCE', 
                    'message': 'Consider adding LIMIT when using ORDER BY',
                    'severity': 'LOW'
                })
            
            if analysis['joins_count'] > 3:
                suggestions.append({
                    'type': 'COMPLEXITY',
                    'message': 'Query has many joins - consider breaking into smaller queries',
                    'severity': 'MEDIUM'
                })
            
            if 'WHERE' not in query.upper() and analysis['query_type'] in ['UPDATE', 'DELETE']:
                suggestions.append({
                    'type': 'SAFETY',
                    'message': 'Missing WHERE clause in UPDATE/DELETE - affects all rows',
                    'severity': 'HIGH'
                })
            
            analysis['optimization_suggestions'] = suggestions
            
            return analysis
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return {'error': str(e)}
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of SQL query"""
        query_upper = query.strip().upper()
        
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        elif query_upper.startswith('CREATE'):
            return 'CREATE'
        elif query_upper.startswith('DROP'):
            return 'DROP'
        elif query_upper.startswith('ALTER'):
            return 'ALTER'
        else:
            return 'UNKNOWN'
    
    def _extract_tables(self, query: str) -> List[str]:
        """Extract table names from query"""
        tables = []
        query_upper = query.upper()
        
        # Simple extraction - would be more sophisticated in production
        if 'FROM ' in query_upper:
            parts = query_upper.split('FROM ')[1].split()
            if parts:
                tables.append(parts[0].strip(','))
        
        # Extract JOIN tables
        join_keywords = ['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL OUTER JOIN', 'CROSS JOIN']
        for join_keyword in join_keywords:
            if join_keyword in query_upper:
                parts = query_upper.split(join_keyword)
                for part in parts[1:]:
                    table_part = part.strip().split()[0]
                    if table_part:
                        tables.append(table_part)
        
        return list(set(tables))  # Remove duplicates


# Global instance
query_builder = QueryBuilder()