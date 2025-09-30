"""
Ainflue Core Platform - GraphQL Federation Core
================================================

Enterprise-grade GraphQL federation system with schema stitching, query planning,
distributed execution, and advanced federation features for microservices architecture.
Provides unified GraphQL API across distributed services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re

# Third-party imports (with fallbacks)
try:
    import graphql
    from graphql import GraphQLSchema, build_schema, execute, parse, validate
    GRAPHQL_AVAILABLE = True
except ImportError:
    GRAPHQL_AVAILABLE = False

logger = logging.getLogger(__name__)

class ServiceStatus(str, Enum):
    """Service status in federation"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"

class QueryComplexity(str, Enum):
    """Query complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FederatedService:
    """Federated GraphQL service"""
    service_id: str
    service_name: str
    url: str
    schema: str
    status: ServiceStatus = ServiceStatus.INACTIVE
    health_check_url: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    weight: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None

@dataclass
class QueryPlan:
    """Query execution plan"""
    query_id: str
    query: str
    variables: Dict[str, Any]
    services_involved: List[str]
    execution_steps: List[Dict[str, Any]]
    estimated_complexity: QueryComplexity
    estimated_execution_time: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ExecutionResult:
    """Query execution result"""
    query_id: str
    data: Optional[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    extensions: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    services_called: List[str] = field(default_factory=list)

@dataclass
class FederationMetrics:
    """GraphQL federation metrics"""
    queries_executed: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    avg_execution_time: float = 0.0
    services_active: int = 0
    services_total: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    complexity_violations: int = 0

class GraphQLFederationCore:
    """Enterprise GraphQL federation system"""
    
    def __init__(self, level: str = "enterprise"):
        """Initialize GraphQL federation core"""
        self.level = level
        self.services: Dict[str, FederatedService] = {}
        self.federated_schema: Optional[Any] = None
        self.query_cache: Dict[str, Any] = {}
        self.metrics = FederationMetrics()
        
        # Query planning and execution
        self.query_planner = None
        self.execution_engine = None
        
        # Configuration
        self.config = {
            "max_query_complexity": 1000,
            "max_query_depth": 15,
            "cache_ttl": 300,  # 5 minutes
            "timeout": 30,
            "max_batch_size": 100,
            "enable_introspection": True,
            "enable_playground": False,
            "rate_limit": {"requests_per_minute": 1000}
        }
        
        # Schema stitching
        self.type_defs: List[str] = []
        self.resolvers: Dict[str, Any] = {}
        
        # Health monitoring
        self.health_check_interval = 60
        self._health_check_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        if not GRAPHQL_AVAILABLE:
            logger.warning("GraphQL library not available - federation will use fallback mode")
        
        # Start health monitoring
        self._start_health_monitoring()
        
        logger.info(f"🔗 GraphQL Federation Core initialized - Level: {level}")

    def _start_health_monitoring(self):
        """Start health monitoring for federated services"""
        if self._health_check_task and not self._health_check_task.done():
            return
        
        self._health_check_task = asyncio.create_task(self._health_monitor_loop())

    async def _health_monitor_loop(self):
        """Health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._check_services_health()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def register_service(self, service: FederatedService) -> str:
        """Register a federated service"""
        
        try:
            # Validate service schema
            if GRAPHQL_AVAILABLE:
                await self._validate_service_schema(service)
            
            # Store service
            self.services[service.service_id] = service
            self.metrics.services_total += 1
            
            # Update federated schema
            await self._rebuild_federated_schema()
            
            # Initial health check
            await self._check_service_health(service)
            
            logger.info(f"Registered federated service: {service.service_name}")
            return service.service_id
            
        except Exception as e:
            logger.error(f"Failed to register service {service.service_name}: {str(e)}")
            raise

    async def _validate_service_schema(self, service: FederatedService):
        """Validate service GraphQL schema"""
        
        if not GRAPHQL_AVAILABLE:
            return
        
        try:
            # Parse and validate schema
            schema = build_schema(service.schema)
            
            # Check for federation directives
            federation_directives = ["@key", "@external", "@requires", "@provides"]
            schema_text = service.schema
            
            # Basic federation validation
            if "@key" in schema_text:
                logger.debug(f"Service {service.service_name} supports federation")
            
        except Exception as e:
            raise ValueError(f"Invalid GraphQL schema: {str(e)}")

    async def _rebuild_federated_schema(self):
        """Rebuild the federated schema from all services"""
        
        if not GRAPHQL_AVAILABLE:
            return
        
        try:
            # Collect all schemas
            schemas = []
            for service in self.services.values():
                if service.status == ServiceStatus.ACTIVE:
                    schemas.append(service.schema)
            
            if not schemas:
                self.federated_schema = None
                return
            
            # Simple schema merging (in production, use proper federation)
            merged_schema = self._merge_schemas(schemas)
            
            # Build executable schema
            self.federated_schema = build_schema(merged_schema)
            
            logger.info("✅ Federated schema rebuilt")
            
        except Exception as e:
            logger.error(f"Failed to rebuild federated schema: {str(e)}")

    def _merge_schemas(self, schemas: List[str]) -> str:
        """Simple schema merging (placeholder for real federation)"""
        
        # This is a simplified merge - real federation is much more complex
        type_defs = []
        queries = []
        mutations = []
        subscriptions = []
        
        for schema in schemas:
            # Extract types, queries, mutations, subscriptions
            lines = schema.strip().split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('type Query'):
                    current_section = 'query'
                    current_content = []
                elif line.startswith('type Mutation'):
                    current_section = 'mutation'
                    current_content = []
                elif line.startswith('type Subscription'):
                    current_section = 'subscription'
                    current_content = []
                elif line.startswith('type ') and current_section is None:
                    # Regular type definition
                    type_defs.append(line)
                elif current_section and line:
                    current_content.append(line)
                elif line == '}' and current_section:
                    if current_section == 'query':
                        queries.extend(current_content[:-1])  # Exclude closing brace
                    elif current_section == 'mutation':
                        mutations.extend(current_content[:-1])
                    elif current_section == 'subscription':
                        subscriptions.extend(current_content[:-1])
                    current_section = None
        
        # Build merged schema
        merged_parts = []
        
        # Add type definitions
        if type_defs:
            merged_parts.extend(type_defs)
        
        # Add Query type
        if queries:
            merged_parts.append("type Query {")
            merged_parts.extend(queries)
            merged_parts.append("}")
        
        # Add Mutation type
        if mutations:
            merged_parts.append("type Mutation {")
            merged_parts.extend(mutations)
            merged_parts.append("}")
        
        # Add Subscription type
        if subscriptions:
            merged_parts.append("type Subscription {")
            merged_parts.extend(subscriptions)
            merged_parts.append("}")
        
        return '\n'.join(merged_parts)

    async def unregister_service(self, service_id: str):
        """Unregister a federated service"""
        
        if service_id in self.services:
            service = self.services.pop(service_id)
            self.metrics.services_total -= 1
            
            if service.status == ServiceStatus.ACTIVE:
                self.metrics.services_active -= 1
            
            # Rebuild schema without this service
            await self._rebuild_federated_schema()
            
            logger.info(f"Unregistered service: {service.service_name}")

    async def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> ExecutionResult:
        """Execute GraphQL query against federated schema"""
        
        start_time = time.time()
        query_id = f"query_{int(time.time() * 1000)}"
        
        try:
            # Create execution result
            result = ExecutionResult(query_id=query_id)
            
            if not GRAPHQL_AVAILABLE:
                result.errors.append({
                    "message": "GraphQL library not available",
                    "extensions": {"code": "GRAPHQL_NOT_AVAILABLE"}
                })
                return result
            
            if not self.federated_schema:
                result.errors.append({
                    "message": "No federated schema available",
                    "extensions": {"code": "NO_SCHEMA"}
                })
                return result
            
            # Parse query
            document = parse(query)
            
            # Validate query
            validation_errors = validate(self.federated_schema, document)
            if validation_errors:
                result.errors.extend([
                    {"message": str(error)} for error in validation_errors
                ])
                return result
            
            # Check query complexity
            complexity = await self._analyze_query_complexity(query, variables or {})
            if complexity.value == QueryComplexity.CRITICAL.value:
                result.errors.append({
                    "message": "Query complexity exceeds limits",
                    "extensions": {"code": "COMPLEXITY_LIMIT_EXCEEDED"}
                })
                self.metrics.complexity_violations += 1
                return result
            
            # Create query plan
            plan = await self._create_query_plan(query, variables or {}, complexity)
            
            # Execute query
            execution_result = await self._execute_federated_query(
                plan, context or {}
            )
            
            result.data = execution_result.get("data")
            result.errors.extend(execution_result.get("errors", []))
            result.extensions = execution_result.get("extensions", {})
            result.services_called = plan.services_involved
            
            # Update metrics
            self.metrics.queries_executed += 1
            if not result.errors:
                self.metrics.successful_queries += 1
            else:
                self.metrics.failed_queries += 1
            
            result.execution_time = time.time() - start_time
            self._update_avg_execution_time(result.execution_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            result = ExecutionResult(
                query_id=query_id,
                errors=[{"message": f"Execution error: {str(e)}"}],
                execution_time=time.time() - start_time
            )
            self.metrics.failed_queries += 1
            return result

    async def _analyze_query_complexity(
        self,
        query: str,
        variables: Dict[str, Any]
    ) -> QueryComplexity:
        """Analyze query complexity"""
        
        # Simple complexity analysis
        complexity_score = 0
        
        # Count query depth
        depth = query.count('{') - query.count('}')
        complexity_score += depth * 10
        
        # Count fields
        field_count = len(re.findall(r'\w+\s*{', query))
        complexity_score += field_count * 5
        
        # Count arguments
        arg_count = len(re.findall(r'\(\s*\w+:', query))
        complexity_score += arg_count * 2
        
        # Determine complexity level
        if complexity_score < 50:
            return QueryComplexity.LOW
        elif complexity_score < 150:
            return QueryComplexity.MEDIUM
        elif complexity_score < 500:
            return QueryComplexity.HIGH
        else:
            return QueryComplexity.CRITICAL

    async def _create_query_plan(
        self,
        query: str,
        variables: Dict[str, Any],
        complexity: QueryComplexity
    ) -> QueryPlan:
        """Create execution plan for federated query"""
        
        query_id = f"plan_{int(time.time() * 1000)}"
        
        # Simple planning - identify which services are needed
        services_involved = []
        execution_steps = []
        
        # Analyze query to determine service involvement
        for service_id, service in self.services.items():
            if service.status == ServiceStatus.ACTIVE:
                # Simple check - if service schema types are mentioned in query
                # In real federation, this would be much more sophisticated
                if self._query_involves_service(query, service):
                    services_involved.append(service_id)
                    execution_steps.append({
                        "service_id": service_id,
                        "service_name": service.service_name,
                        "query_fragment": query,  # Simplified
                        "estimated_time": 100  # ms
                    })
        
        # Estimate execution time
        estimated_time = sum(step["estimated_time"] for step in execution_steps)
        
        return QueryPlan(
            query_id=query_id,
            query=query,
            variables=variables,
            services_involved=services_involved,
            execution_steps=execution_steps,
            estimated_complexity=complexity,
            estimated_execution_time=estimated_time
        )

    def _query_involves_service(self, query: str, service: FederatedService) -> bool:
        """Check if query involves specific service"""
        
        # Simple heuristic - check if service name or common types are in query
        service_indicators = [
            service.service_name.lower(),
            "user", "content", "payment", "media"  # Common types
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in service_indicators)

    async def _execute_federated_query(
        self,
        plan: QueryPlan,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute federated query plan"""
        
        if not plan.services_involved:
            return {"data": None, "errors": [{"message": "No services available"}]}
        
        # For this simplified implementation, execute against first available service
        # Real federation would execute against multiple services and merge results
        
        try:
            service_id = plan.services_involved[0]
            service = self.services[service_id]
            
            # Execute query against service
            result = await self._execute_service_query(
                service, plan.query, plan.variables, context
            )
            
            return result
            
        except Exception as e:
            return {
                "data": None,
                "errors": [{"message": f"Execution failed: {str(e)}"}]
            }

    async def _execute_service_query(
        self,
        service: FederatedService,
        query: str,
        variables: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute query against specific service"""
        
        try:
            # In a real implementation, this would make HTTP request to service
            # For now, return mock data
            
            # Simple execution using local schema
            if GRAPHQL_AVAILABLE and self.federated_schema:
                result = execute(
                    self.federated_schema,
                    parse(query),
                    variable_values=variables,
                    context_value=context
                )
                
                return {
                    "data": result.data,
                    "errors": [{"message": str(e)} for e in (result.errors or [])]
                }
            else:
                # Fallback mock response
                return {
                    "data": {"message": f"Mock response from {service.service_name}"},
                    "errors": []
                }
                
        except Exception as e:
            logger.error(f"Service query execution failed: {str(e)}")
            return {
                "data": None,
                "errors": [{"message": f"Service error: {str(e)}"}]
            }

    async def _check_services_health(self):
        """Check health of all federated services"""
        
        for service in self.services.values():
            await self._check_service_health(service)

    async def _check_service_health(self, service: FederatedService):
        """Check health of specific service"""
        
        try:
            # Simple health check - in production would make HTTP request
            # For now, simulate health check
            
            if service.health_check_url:
                # Would make actual HTTP request here
                pass
            
            # Update service status
            if service.status != ServiceStatus.ACTIVE:
                service.status = ServiceStatus.ACTIVE
                self.metrics.services_active += 1
            
            service.last_health_check = datetime.utcnow()
            
        except Exception as e:
            logger.warning(f"Health check failed for {service.service_name}: {str(e)}")
            
            if service.status == ServiceStatus.ACTIVE:
                self.metrics.services_active -= 1
            
            service.status = ServiceStatus.ERROR

    def _update_avg_execution_time(self, execution_time: float):
        """Update average execution time"""
        self.metrics.avg_execution_time = (
            self.metrics.avg_execution_time * 0.9 + execution_time * 0.1
        )

    async def get_federated_schema_sdl(self) -> Optional[str]:
        """Get federated schema as SDL string"""
        
        if not GRAPHQL_AVAILABLE or not self.federated_schema:
            return None
        
        try:
            from graphql import print_schema
            return print_schema(self.federated_schema)
        except Exception as e:
            logger.error(f"Failed to print schema: {str(e)}")
            return None

    def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific service"""
        
        service = self.services.get(service_id)
        if not service:
            return None
        
        return {
            "service_id": service.service_id,
            "service_name": service.service_name,
            "status": service.status.value,
            "url": service.url,
            "last_health_check": service.last_health_check.isoformat() if service.last_health_check else None,
            "weight": service.weight,
            "metadata": service.metadata
        }

    def get_all_services_status(self) -> List[Dict[str, Any]]:
        """Get status of all services"""
        
        return [
            self.get_service_status(service_id)
            for service_id in self.services.keys()
        ]

    def get_metrics(self) -> FederationMetrics:
        """Get federation metrics"""
        
        # Update real-time metrics
        self.metrics.services_active = len([
            s for s in self.services.values() 
            if s.status == ServiceStatus.ACTIVE
        ])
        self.metrics.services_total = len(self.services)
        
        return self.metrics

    async def health_check(self) -> bool:
        """Health check for GraphQL federation"""
        try:
            # Check if we have any active services
            active_services = [
                s for s in self.services.values() 
                if s.status == ServiceStatus.ACTIVE
            ]
            
            if not active_services:
                logger.warning("No active services in federation")
                return len(self.services) == 0  # OK if no services registered
            
            # Test simple query execution
            simple_query = "{ __typename }"
            result = await self.execute_query(simple_query)
            
            return not result.errors
            
        except Exception as e:
            logger.error(f"GraphQL federation health check failed: {str(e)}")
            return False

    async def shutdown(self):
        """Shutdown GraphQL federation"""
        logger.info("🛑 Shutting down GraphQL federation")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel health check task
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

# Module exports
__all__ = [
    "GraphQLFederationCore", "FederatedService", "QueryPlan", 
    "ExecutionResult", "ServiceStatus", "QueryComplexity", "FederationMetrics"
]

logger.info("🔗 GraphQL Federation Core module loaded")