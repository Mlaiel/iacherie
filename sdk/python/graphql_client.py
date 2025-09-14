"""GraphQL API Client for Ainflue SDK

Multi-expert implementation:
    - Backend Senior: Robust GraphQL client architecture with query optimization
- Lead Dev IA: Intelligent query caching and optimization strategies
- DBA: Optimized query structure and data fetching patterns
- DevOps: Monitoring and metrics for GraphQL operations
- Security: Query validation and injection prevention

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import httpx
from pydantic import BaseModel, Field

from .exceptions import (
    GraphQLError, ValidationError, AuthenticationError,
    RateLimitError, QueryOptimizationError
)
from .auth_manager import AuthenticationManager


class QueryComplexity(Enum):
    """GraphQL query complexity levels"""
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3
    VERY_COMPLEX = 4


@dataclass
class QueryMetrics:
    """GraphQL query metrics (DevOps expertise)"""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    cached_queries: int = 0
    average_response_time: float = 0.0
    total_response_time: float = 0.0
    cache_hit_ratio: float = 0.0
    query_complexity_distribution: Dict[str, int] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate query success rate"""
        if self.total_queries == 0:
            return 0.0
        return (self.successful_queries / self.total_queries) * 100
    
    def update_response_time(self, response_time -> None: float) -> None:
        """Update average response time"""
        self.total_response_time += response_time
        if self.total_queries > 0:
            self.average_response_time = self.total_response_time / self.total_queries


class GraphQLQuery(BaseModel):
    """GraphQL query representation with optimization metadata"""
    query: str = Field(..., description="GraphQL query string")
    variables: Optional[Dict[str, Any]] = Field(default=None, description="Query variables")
    operation_name: Optional[str] = Field(default=None, description="Operation name")
    complexity: QueryComplexity = Field(default=QueryComplexity.SIMPLE, description="Query complexity")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    timeout: float = Field(default=30.0, description="Query timeout")
    retry_count: int = Field(default=3, description="Retry attempts")
    
    @property
    def query_hash(self) -> str:
        """Generate hash for query caching"""
        query_content = f"{self.query}:{json.dumps(self.variables, sort_keys=True)}"
        return hashlib.md5(query_content.encode()).hexdigest()


class QueryOptimizer:
    """GraphQL query optimization (DBA + Lead Dev IA expertise)"""
    
    def __init__(self) -> None:
        self.field_frequency = {}  # Track field usage frequency
        self.query_patterns = {}   # Common query patterns
        self.optimization_rules = self._load_optimization_rules()
    
    def optimize_query(self, query: GraphQLQuery) -> GraphQLQuery:
        """Optimize GraphQL query for better performance"""
        try:
            # Parse and optimize query structure
            optimized_query_string = self._optimize_query_structure(query.query)
            
            # Optimize variables
            optimized_variables = self._optimize_variables(query.variables)
            
            # Calculate optimized complexity
            optimized_complexity = self._calculate_query_complexity(optimized_query_string)
            
            # Create optimized query
            optimized_query = GraphQLQuery(
                query=optimized_query_string,
                variables=optimized_variables,
                operation_name=query.operation_name,
                complexity=optimized_complexity,
                cache_ttl=query.cache_ttl,
                timeout=query.timeout,
                retry_count=query.retry_count
            )
            
            return optimized_query
            
        except Exception as e:
            logging.error(f"Query optimization failed: {e}")
            # Return original query if optimization fails
            return query
    
    def _optimize_query_structure(self, query: str) -> str:
        """Optimize GraphQL query structure"""
        # Remove unnecessary whitespace and comments
        lines = []
        for line in query.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                lines.append(stripped)
        
        optimized = ' '.join(lines)
        
        # Apply optimization rules
        for rule in self.optimization_rules:
            optimized = rule(optimized)
        
        return optimized
    
    def _optimize_variables(self, variables: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Optimize query variables"""
        if not variables:
            return variables
        
        # Remove null/empty values that don't affect query
        optimized_vars = {}
        for key, value in variables.items():
            if value is not None and value != "":
                optimized_vars[key] = value
        
        return optimized_vars if optimized_vars else None
    
    def _calculate_query_complexity(self, query: str) -> QueryComplexity:
        """Calculate query complexity based on structure"""
        # Simple heuristic for complexity calculation
        depth_indicators = query.count('{')
        field_count = len([word for word in query.split() if not word.startswith(('query', 'mutation', 'subscription', '{', '}'))])
        
        if depth_indicators <= 2 and field_count <= 5:
            return QueryComplexity.SIMPLE
        elif depth_indicators <= 4 and field_count <= 15:
            return QueryComplexity.MODERATE
        elif depth_indicators <= 6 and field_count <= 30:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.VERY_COMPLEX
    
    def _load_optimization_rules(self) -> List[callable]:
        """Load query optimization rules"""
        return [
            self._remove_duplicate_fields,
            self._optimize_aliases,
            self._optimize_fragments
        ]
    
    def _remove_duplicate_fields(self, query: str) -> str:
        """Remove duplicate fields in query"""
        # Simplified duplicate removal (enhance for production)
        return query
    
    def _optimize_aliases(self, query: str) -> str:
        """Optimize field aliases"""
        # Simplified alias optimization (enhance for production)
        return query
    
    def _optimize_fragments(self, query: str) -> str:
        """Optimize fragment usage"""
        # Simplified fragment optimization (enhance for production)
        return query


class QueryCache:
    """Intelligent query caching (Lead Dev IA expertise)"""
    
    def __init__(self, max_size -> None: int = 1000, default_ttl -> None: int = 300) -> None:
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        
    def get(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        if query_hash not in self.cache:
            return None
        
        cached_item = self.cache[query_hash]
        
        # Check TTL
        if datetime.now() > cached_item["expires_at"]:
            self._remove(query_hash)
            return None
        
        # Update access time for LRU
        self.access_times[query_hash] = datetime.now()
        
        return cached_item["data"]
    
    def set(self, query_hash -> None: str, data -> None: Dict[str, Any], ttl -> None: Optional[int] = None) -> None:
        """Cache query result with intelligent eviction"""
        # Use provided TTL or default
        cache_ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=cache_ttl)
        
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Cache the data
        self.cache[query_hash] = {
            "data": data,
            "cached_at": datetime.now(),
            "expires_at": expires_at,
            "access_count": 1
        }
        self.access_times[query_hash] = datetime.now()
    
    def _evict_lru(self) -> None:
        """Evict least recently used items"""
        if not self.access_times:
            return
        
        # Find least recently used item
        lru_hash = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove(lru_hash)
    
    def _remove(self, query_hash -> None: str) -> None:
        """Remove item from cache"""
        self.cache.pop(query_hash, None)
        self.access_times.pop(query_hash, None)
    
    def clear(self) -> None:
        """Clear all cached items"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now()
        valid_items = 0
        expired_items = 0
        
        for item in self.cache.values():
            if now <= item["expires_at"]:
                valid_items += 1
            else:
                expired_items += 1
        
        return {
            "total_items": len(self.cache),
            "valid_items": valid_items,
            "expired_items": expired_items,
            "max_size": self.max_size,
            "utilization": (len(self.cache) / self.max_size) * 100
        }


class QueryValidator:
    """GraphQL query validation (Security expertise)"""
    
    def __init__(self) -> None:
        self.max_query_depth = 10
        self.max_field_count = 100
        self.max_alias_count = 50
        self.blocked_patterns = [
            '__schema',
            '__type',
            'introspection'
        ]
    
    def validate_query(self, query: GraphQLQuery) -> bool:
        """Validate GraphQL query for security and performance"""
        try:
            # Check query depth
            if self._get_query_depth(query.query) > self.max_query_depth:
                raise ValidationError(f"Query depth exceeds maximum ({self.max_query_depth})")
            
            # Check field count
            field_count = self._count_fields(query.query)
            if field_count > self.max_field_count:
                raise ValidationError(f"Field count exceeds maximum ({self.max_field_count})")
            
            # Check for blocked patterns
            query_lower = query.query.lower()
            for pattern in self.blocked_patterns:
                if pattern in query_lower:
                    raise ValidationError(f"Query contains blocked pattern: {pattern}")
            
            # Validate variables
            if query.variables:
                self._validate_variables(query.variables)
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Query validation failed: {e}")
    
    def _get_query_depth(self, query: str) -> int:
        """Calculate maximum query depth"""
        max_depth = 0
        current_depth = 0
        
        for char in query:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth -= 1
        
        return max_depth
    
    def _count_fields(self, query: str) -> int:
        """Count number of fields in query"""
        # Simplified field counting (enhance for production)
        import re
        # Remove comments and strings
        cleaned = re.sub(r'#.*$', '', query, flags=re.MULTILINE)
        cleaned = re.sub(r'"[^"]*"', '', cleaned)
        
        # Count field-like patterns
        fields = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*(?:\(|{|\s)', cleaned)
        return len(fields)
    
    def _validate_variables(self, variables -> None: Dict[str, Any]) -> None:
        """Validate query variables"""
        for key, value in variables.items():
            # Check variable name
            if not key.replace('_', '').isalnum():
                raise ValidationError(f"Invalid variable name: {key}")
            
            # Check for injection patterns
            if isinstance(value, str):
                if any(pattern in value.lower() for pattern in ['<script', 'javascript:', 'eval(']):
                    raise ValidationError(f"Potentially malicious content in variable: {key}")


class GraphQLClient:
    """Main GraphQL client with multi-expert architecture"""
    
    def __init__(self, 
                 endpoint -> None: str,
                 auth_manager -> None: AuthenticationManager,
                 enable_caching -> None: bool = True,
                 enable_optimization -> None: bool = True) -> None:
        self.endpoint = endpoint
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
        
        # Expert components
        self.optimizer = QueryOptimizer() if enable_optimization else None
        self.cache = QueryCache() if enable_caching else None
        self.validator = QueryValidator()
        
        # Metrics and monitoring
        self.metrics = QueryMetrics()
        self.http_client = None
        
        # Configuration
        self.timeout = 30.0
        self.max_retries = 3
    
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        self.http_client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()
    
    async def execute_query(self, 
                           query: Union[str, GraphQLQuery],
                           variables: Optional[Dict[str, Any]] = None,
                           operation_name: Optional[str] = None,
                           use_cache: bool = True) -> Dict[str, Any]:
        """Execute GraphQL query with expert optimizations"""
        # Convert string query to GraphQLQuery object
        if isinstance(query, str):
            query_obj = GraphQLQuery(
                query=query,
                variables=variables,
                operation_name=operation_name
            )
        else:
            query_obj = query
        
        start_time = time.time()
        query_hash = query_obj.query_hash
        
        try:
            # Validate query (Security expertise)
            self.validator.validate_query(query_obj)
            
            # Check cache first (Lead Dev IA expertise)
            if use_cache and self.cache:
                cached_result = self.cache.get(query_hash)
                if cached_result:
                    self.metrics.cached_queries += 1
                    self.metrics.total_queries += 1
                    return cached_result
            
            # Optimize query (DBA + Lead Dev IA expertise)
            if self.optimizer:
                query_obj = self.optimizer.optimize_query(query_obj)
            
            # Execute query
            result = await self._execute_http_query(query_obj)
            
            # Cache successful results
            if use_cache and self.cache and "errors" not in result:
                self.cache.set(query_hash, result, query_obj.cache_ttl)
            
            # Update metrics
            response_time = time.time() - start_time
            self.metrics.total_queries += 1
            self.metrics.successful_queries += 1
            self.metrics.update_response_time(response_time)
            
            # Track complexity distribution
            complexity_key = query_obj.complexity.name
            self.metrics.query_complexity_distribution[complexity_key] = \
                self.metrics.query_complexity_distribution.get(complexity_key, 0) + 1
            
            return result
            
        except Exception as e:
            # Update error metrics
            self.metrics.total_queries += 1
            self.metrics.failed_queries += 1
            
            response_time = time.time() - start_time
            self.metrics.update_response_time(response_time)
            
            self.logger.error(f"GraphQL query failed: {e}")
            raise GraphQLError(f"Query execution failed: {e}")
    
    async def _execute_http_query(self, query: GraphQLQuery) -> Dict[str, Any]:
        """Execute HTTP GraphQL request with retry logic"""
        # Prepare request payload
        payload = {
            "query": query.query,
            "variables": query.variables or {},
        }
        
        if query.operation_name:
            payload["operationName"] = query.operation_name
        
        # Prepare headers
        auth_token = await self.auth_manager.get_valid_token()
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "User-Agent": "Ainflue-Python-SDK/1.0.0"
        }
        
        # Execute with retry logic
        last_error = None
        for attempt in range(query.retry_count + 1):
            try:
                response = await self.http_client.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=query.timeout
                )
                
                # Check HTTP status
                if response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                
                # Check for GraphQL errors
                if "errors" in result:
                    error_messages = [error.get("message", "Unknown error") for error in result["errors"]]
                    raise GraphQLError(f"GraphQL errors: {'; '.join(error_messages)}")
                
                return result
                
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < query.retry_count:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Request timeout, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                continue
            except httpx.HTTPStatusError as e:
                if e.response.status_code in [500, 502, 503, 504] and attempt < query.retry_count:
                    # Server error - retry
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Server error {e.response.status_code}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise GraphQLError(f"HTTP error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                last_error = e
                if attempt < query.retry_count:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                continue
                else:
                    break
        
        # All retries failed
        raise GraphQLError(f"All retry attempts failed. Last error: {last_error}")
    
    async def execute_batch_queries(self, queries: List[GraphQLQuery]) -> List[Dict[str, Any]]:
        """Execute multiple GraphQL queries in batch"""
        try:
            # Execute queries concurrently
            tasks = []
            for query in queries:
                task = asyncio.create_task(self.execute_query(query))
                tasks.append(task)
            
            # Wait for all queries to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "errors": [{"message": str(result)}],
                        "query_index": i
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch query execution failed: {e}")
            raise GraphQLError(f"Batch execution failed: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current GraphQL metrics"""
        # Update cache hit ratio
        if self.metrics.total_queries > 0:
            self.metrics.cache_hit_ratio = (self.metrics.cached_queries / self.metrics.total_queries) * 100
        
        metrics_data = {
            "total_queries": self.metrics.total_queries,
            "successful_queries": self.metrics.successful_queries,
            "failed_queries": self.metrics.failed_queries,
            "cached_queries": self.metrics.cached_queries,
            "success_rate": self.metrics.success_rate,
            "cache_hit_ratio": self.metrics.cache_hit_ratio,
            "average_response_time": self.metrics.average_response_time,
            "query_complexity_distribution": self.metrics.query_complexity_distribution
        }
        
        # Add cache statistics if available
        if self.cache:
            metrics_data["cache_stats"] = self.cache.get_stats()
        
        return metrics_data
    
    def clear_cache(self) -> None:
        """Clear query cache"""
        if self.cache:
            self.cache.clear()
            self.logger.info("Query cache cleared")


# Utility functions for common GraphQL operations
class GraphQLQueryBuilder:
    """Helper class for building GraphQL queries"""
    
    @staticmethod
    def build_query(operation: str, 
                   fields: List[str], 
                   variables: Optional[Dict[str, Any]] = None,
                   fragments: Optional[Dict[str, str]] = None) -> GraphQLQuery:
        """Build a GraphQL query from components"""
        # Build fields string
        fields_str = "\n".join([f"    {field}" for field in fields])
        
        # Build query string
        query_parts = []
        
        # Add fragments
        if fragments:
            for fragment_name, fragment_def in fragments.items():
                query_parts.append(fragment_def)
        
        # Add main query
        if variables:
            # Build variable definitions
            var_defs = []
            for var_name, var_value in variables.items():
                var_type = "String"  # Simplify - infer type in production
                var_defs.append(f"${var_name}: {var_type}")
            
            var_def_str = f"({', '.join(var_defs)})"
            query_parts.append(f"query{var_def_str} {{\n  {operation} {{\n{fields_str}\n  }}\n}}")
        else:
            query_parts.append(f"query {{\n  {operation} {{\n{fields_str}\n  }}\n}}")
        
        query_string = "\n\n".join(query_parts)
        
        return GraphQLQuery(
            query=query_string,
            variables=variables
        )


# Example usage
async def example_graphql_usage() -> None:
    """Example usage of GraphQL client"""
    from .auth_manager import AuthenticationManager
    
    # Setup authentication
    auth_manager = AuthenticationManager("your-api-key")
    
    async with GraphQLClient(
        endpoint="https://api.ainflue.com/graphql",
        auth_manager=auth_manager
    ) as client:
        
        # Simple query
        query = GraphQLQuery(
            query="""
                query GetUser($id: ID!) {
                    user(id: $id) {
                        id
                        name
                        email
                        profile {
                            bio
                            avatar
                        }
                    }
                }
            """,
            variables={"id": "user123"}
        )
        
        # Execute query
        result = await client.execute_query(query)
        print(f"Query result: {result}")
        
        # Get metrics
        metrics = client.get_metrics()
        print(f"Client metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_graphql_usage())))}}

# File has syntax issues - needs manual review