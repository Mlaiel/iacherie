"""
Dependency Resolver - Enterprise Dependency Management & Resolution Engine

Advanced dependency resolution system managing complex inter-service dependencies,
circular dependency detection, and automatic resolution strategies for the
IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This dependency resolution system is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization.

🎯 BUSINESS LOGIC:
Service Registration → Dependency Analysis → Resolution Strategy → 
Execution Order → Monitoring → Health Checks
"""

import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import networkx as nx
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of dependencies in the system"""
    SERVICE_DEPENDENCY = "service_dependency"
    DATA_DEPENDENCY = "data_dependency"
    RESOURCE_DEPENDENCY = "resource_dependency"
    EXECUTION_DEPENDENCY = "execution_dependency"
    CONFIGURATION_DEPENDENCY = "configuration_dependency"
    PLATFORM_DEPENDENCY = "platform_dependency"
    API_DEPENDENCY = "api_dependency"
    SECURITY_DEPENDENCY = "security_dependency"


class ResolutionStrategy(Enum):
    """Dependency resolution strategies"""
    LAZY_LOADING = "lazy_loading"
    EAGER_LOADING = "eager_loading"
    PARALLEL_RESOLUTION = "parallel_resolution"
    SEQUENTIAL_RESOLUTION = "sequential_resolution"
    CACHED_RESOLUTION = "cached_resolution"
    DYNAMIC_RESOLUTION = "dynamic_resolution"
    HIERARCHICAL_RESOLUTION = "hierarchical_resolution"


class DependencyStatus(Enum):
    """Dependency resolution status"""
    UNRESOLVED = "unresolved"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    FAILED = "failed"
    CACHED = "cached"
    EXPIRED = "expired"
    CIRCULAR = "circular"


class DependencyPriority(Enum):
    """Dependency resolution priority"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    OPTIONAL = 5


@dataclass
class DependencyDefinition:
    """Individual dependency definition"""
    dependency_id: str
    name: str
    dependency_type: DependencyType
    source_service: str
    target_service: str
    resolution_strategy: ResolutionStrategy
    priority: DependencyPriority
    required: bool = True
    timeout_seconds: int = 30
    retry_count: int = 3
    cache_duration: int = 300
    validation_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceDefinition:
    """Service definition with dependencies"""
    service_id: str
    name: str
    service_type: str
    endpoint: str
    dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    health_check_endpoint: Optional[str] = None
    initialization_order: int = 100
    startup_timeout: int = 60
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolutionResult:
    """Dependency resolution result"""
    dependency_id: str
    status: DependencyStatus
    resolved_at: datetime
    resolution_time: float
    result_data: Any = None
    error_message: Optional[str] = None
    cache_hit: bool = False
    retry_count: int = 0


@dataclass
class ResolutionContext:
    """Context for dependency resolution"""
    context_id: str
    requested_service: str
    resolution_strategy: ResolutionStrategy
    timeout_seconds: int
    cache_enabled: bool = True
    parallel_resolution: bool = True
    max_depth: int = 10
    current_depth: int = 0
    resolution_path: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DependencyResolver:
    """Enterprise dependency management and resolution engine"""
    
    def __init__(self, cache_size: int = 1000, max_resolution_depth: int = 20):
        self.cache_size = cache_size
        self.max_resolution_depth = max_resolution_depth
        
        # Dependency registry
        self.dependency_definitions: Dict[str, DependencyDefinition] = {}
        self.service_definitions: Dict[str, ServiceDefinition] = {}
        self.dependency_graph = nx.DiGraph()
        
        # Resolution cache
        self.resolution_cache: Dict[str, ResolutionResult] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Resolution tracking
        self.active_resolutions: Dict[str, ResolutionContext] = {}
        self.resolution_history: List[ResolutionResult] = []
        self.circular_dependencies: Set[Tuple[str, str]] = set()
        
        # Performance metrics
        self.resolution_metrics: Dict[str, List[float]] = defaultdict(list)
        self.cache_hit_rate: float = 0.0
        self.total_resolutions: int = 0
        self.successful_resolutions: int = 0
        
        # Event handling
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Thread pool for parallel resolution
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize standard dependencies
        self._initialize_standard_dependencies()
        
        logger.info("DependencyResolver initialized successfully")
    
    def _initialize_standard_dependencies(self):
        """Initialize standard platform dependencies"""
        # Content Processing Dependencies
        content_deps = [
            DependencyDefinition(
                dependency_id="content_analysis_fingerprinting",
                name="Content Analysis to Fingerprinting",
                dependency_type=DependencyType.SERVICE_DEPENDENCY,
                source_service="content_analysis",
                target_service="ai_fingerprinting",
                resolution_strategy=ResolutionStrategy.SEQUENTIAL_RESOLUTION,
                priority=DependencyPriority.CRITICAL,
                timeout_seconds=60
            ),
            DependencyDefinition(
                dependency_id="fingerprinting_protection",
                name="Fingerprinting to Protection",
                dependency_type=DependencyType.DATA_DEPENDENCY,
                source_service="ai_fingerprinting",
                target_service="content_protection",
                resolution_strategy=ResolutionStrategy.EAGER_LOADING,
                priority=DependencyPriority.HIGH,
                timeout_seconds=45
            ),
            DependencyDefinition(
                dependency_id="protection_monitoring",
                name="Protection to Monitoring",
                dependency_type=DependencyType.EXECUTION_DEPENDENCY,
                source_service="content_protection",
                target_service="web_monitoring",
                resolution_strategy=ResolutionStrategy.PARALLEL_RESOLUTION,
                priority=DependencyPriority.NORMAL,
                timeout_seconds=30
            )
        ]
        
        # Monetization Dependencies
        monetization_deps = [
            DependencyDefinition(
                dependency_id="revenue_platform_apis",
                name="Revenue Calculation to Platform APIs",
                dependency_type=DependencyType.API_DEPENDENCY,
                source_service="revenue_calculation",
                target_service="platform_apis",
                resolution_strategy=ResolutionStrategy.CACHED_RESOLUTION,
                priority=DependencyPriority.HIGH,
                timeout_seconds=120,
                cache_duration=600
            ),
            DependencyDefinition(
                dependency_id="licensing_payment",
                name="Licensing to Payment Processing",
                dependency_type=DependencyType.SERVICE_DEPENDENCY,
                source_service="licensing_engine",
                target_service="payment_processor",
                resolution_strategy=ResolutionStrategy.SEQUENTIAL_RESOLUTION,
                priority=DependencyPriority.CRITICAL,
                timeout_seconds=180
            )
        ]
        
        # Security Dependencies
        security_deps = [
            DependencyDefinition(
                dependency_id="auth_all_services",
                name="Authentication for All Services",
                dependency_type=DependencyType.SECURITY_DEPENDENCY,
                source_service="authentication_service",
                target_service="*",
                resolution_strategy=ResolutionStrategy.EAGER_LOADING,
                priority=DependencyPriority.CRITICAL,
                timeout_seconds=15
            ),
            DependencyDefinition(
                dependency_id="encryption_data_storage",
                name="Encryption for Data Storage",
                dependency_type=DependencyType.SECURITY_DEPENDENCY,
                source_service="encryption_service",
                target_service="data_storage",
                resolution_strategy=ResolutionStrategy.LAZY_LOADING,
                priority=DependencyPriority.HIGH,
                timeout_seconds=20
            )
        ]
        
        # Register all dependencies
        all_deps = content_deps + monetization_deps + security_deps
        for dep in all_deps:
            self.register_dependency(dep)
        
        # Initialize standard services
        self._initialize_standard_services()
    
    def _initialize_standard_services(self):
        """Initialize standard service definitions"""
        services = [
            ServiceDefinition(
                service_id="content_analysis",
                name="Content Analysis Service",
                service_type="processing",
                endpoint="/api/v1/content/analyze",
                provides=["content_metadata", "analysis_results"],
                health_check_endpoint="/health",
                initialization_order=10
            ),
            ServiceDefinition(
                service_id="ai_fingerprinting",
                name="AI Fingerprinting Service",
                service_type="ai_processing",
                endpoint="/api/v1/protection/fingerprint",
                dependencies=["content_analysis"],
                provides=["fingerprint_hash", "vector_embeddings"],
                health_check_endpoint="/health",
                initialization_order=20
            ),
            ServiceDefinition(
                service_id="content_protection",
                name="Content Protection Service",
                service_type="protection",
                endpoint="/api/v1/protection/manage",
                dependencies=["ai_fingerprinting"],
                provides=["protection_status", "monitoring_setup"],
                health_check_endpoint="/health",
                initialization_order=30
            ),
            ServiceDefinition(
                service_id="web_monitoring",
                name="Web Monitoring Service",
                service_type="monitoring",
                endpoint="/api/v1/monitoring/surveillance",
                dependencies=["content_protection"],
                provides=["violation_alerts", "monitoring_results"],
                health_check_endpoint="/health",
                initialization_order=40
            ),
            ServiceDefinition(
                service_id="revenue_calculation",
                name="Revenue Calculation Service",
                service_type="financial",
                endpoint="/api/v1/monetization/calculate",
                dependencies=["platform_apis"],
                provides=["revenue_data", "financial_analytics"],
                health_check_endpoint="/health",
                initialization_order=50
            ),
            ServiceDefinition(
                service_id="platform_apis",
                name="Platform APIs Integration",
                service_type="integration",
                endpoint="/api/v1/platform/sync",
                provides=["platform_data", "api_access"],
                health_check_endpoint="/health",
                initialization_order=15
            ),
            ServiceDefinition(
                service_id="licensing_engine",
                name="Licensing Management Engine",
                service_type="legal",
                endpoint="/api/v1/licensing/manage",
                dependencies=["revenue_calculation"],
                provides=["licensing_agreements", "legal_documentation"],
                health_check_endpoint="/health",
                initialization_order=60
            ),
            ServiceDefinition(
                service_id="payment_processor",
                name="Payment Processing Service",
                service_type="financial",
                endpoint="/api/v1/payment/process",
                dependencies=["licensing_engine"],
                provides=["payment_confirmations", "transaction_records"],
                health_check_endpoint="/health",
                initialization_order=70
            ),
            ServiceDefinition(
                service_id="authentication_service",
                name="Authentication & Authorization",
                service_type="security",
                endpoint="/api/v1/auth",
                provides=["auth_tokens", "user_permissions"],
                health_check_endpoint="/health",
                initialization_order=5
            ),
            ServiceDefinition(
                service_id="encryption_service",
                name="Data Encryption Service",
                service_type="security",
                endpoint="/api/v1/security/encrypt",
                provides=["encrypted_data", "security_keys"],
                health_check_endpoint="/health",
                initialization_order=8
            )
        ]
        
        for service in services:
            self.register_service(service)
    
    def register_dependency(self, dependency: DependencyDefinition) -> bool:
        """Register a new dependency definition"""
        try:
            # Validate dependency
            if not self._validate_dependency(dependency):
                return False
            
            # Store dependency
            self.dependency_definitions[dependency.dependency_id] = dependency
            
            # Update dependency graph
            self.dependency_graph.add_edge(
                dependency.source_service,
                dependency.target_service,
                dependency_id=dependency.dependency_id,
                weight=dependency.priority.value
            )
            
            # Check for circular dependencies
            if self._detect_circular_dependencies():
                logger.warning(f"Circular dependency detected involving {dependency.dependency_id}")
                self.circular_dependencies.add((dependency.source_service, dependency.target_service))
            
            logger.info(f"Dependency registered: {dependency.dependency_id}")
            return True
            
        except Exception as e:
            logger.error(f"Dependency registration failed: {e}")
            return False
    
    def register_service(self, service: ServiceDefinition) -> bool:
        """Register a new service definition"""
        try:
            # Validate service
            if not self._validate_service(service):
                return False
            
            self.service_definitions[service.service_id] = service
            
            # Add service to dependency graph
            if service.service_id not in self.dependency_graph:
                self.dependency_graph.add_node(service.service_id)
            
            logger.info(f"Service registered: {service.service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Service registration failed: {e}")
            return False
    
    def _validate_dependency(self, dependency: DependencyDefinition) -> bool:
        """Validate dependency definition"""
        try:
            # Required fields validation
            if not all([dependency.dependency_id, dependency.source_service, dependency.target_service]):
                logger.error("Missing required dependency fields")
                return False
            
            # Timeout validation
            if dependency.timeout_seconds <= 0:
                logger.error("Invalid timeout value")
                return False
            
            # Self-dependency check
            if dependency.source_service == dependency.target_service:
                logger.error("Self-dependency not allowed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Dependency validation error: {e}")
            return False
    
    def _validate_service(self, service: ServiceDefinition) -> bool:
        """Validate service definition"""
        try:
            # Required fields validation
            if not all([service.service_id, service.name, service.endpoint]):
                logger.error("Missing required service fields")
                return False
            
            # Endpoint validation
            if not service.endpoint.startswith(('/api/', '/health', '/')):
                logger.error("Invalid service endpoint format")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Service validation error: {e}")
            return False
    
    def _detect_circular_dependencies(self) -> bool:
        """Detect circular dependencies in the dependency graph"""
        try:
            return not nx.is_directed_acyclic_graph(self.dependency_graph)
        except Exception as e:
            logger.error(f"Circular dependency detection failed: {e}")
            return False
    
    async def resolve_dependencies(
        self,
        service_id: str,
        context: Optional[ResolutionContext] = None
    ) -> Dict[str, ResolutionResult]:
        """Resolve all dependencies for a given service"""
        try:
            if not context:
                context = ResolutionContext(
                    context_id=str(uuid.uuid4()),
                    requested_service=service_id,
                    resolution_strategy=ResolutionStrategy.PARALLEL_RESOLUTION,
                    timeout_seconds=120
                )
            
            # Check if service exists
            if service_id not in self.service_definitions:
                raise ValueError(f"Service '{service_id}' not found")
            
            # Check resolution depth
            if context.current_depth >= self.max_resolution_depth:
                raise ValueError("Maximum resolution depth exceeded")
            
            # Track active resolution
            self.active_resolutions[context.context_id] = context
            
            start_time = datetime.now(timezone.utc)
            results = {}
            
            try:
                # Get service dependencies
                service = self.service_definitions[service_id]
                
                if not service.dependencies:
                    logger.info(f"No dependencies found for service {service_id}")
                    return {}
                
                # Resolve based on strategy
                if context.resolution_strategy == ResolutionStrategy.PARALLEL_RESOLUTION:
                    results = await self._resolve_parallel(service.dependencies, context)
                elif context.resolution_strategy == ResolutionStrategy.SEQUENTIAL_RESOLUTION:
                    results = await self._resolve_sequential(service.dependencies, context)
                elif context.resolution_strategy == ResolutionStrategy.HIERARCHICAL_RESOLUTION:
                    results = await self._resolve_hierarchical(service_id, context)
                else:
                    results = await self._resolve_default(service.dependencies, context)
                
                # Update metrics
                resolution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                self.resolution_metrics[service_id].append(resolution_time)
                self.successful_resolutions += 1
                
                # Emit resolution completed event
                await self._emit_resolution_event("dependencies_resolved", {
                    "service_id": service_id,
                    "context_id": context.context_id,
                    "resolution_time": resolution_time,
                    "results_count": len(results)
                })
                
                return results
                
            finally:
                # Cleanup active resolution
                if context.context_id in self.active_resolutions:
                    del self.active_resolutions[context.context_id]
                
                self.total_resolutions += 1
                
        except Exception as e:
            logger.error(f"Dependency resolution failed for {service_id}: {e}")
            await self._emit_resolution_event("resolution_failed", {
                "service_id": service_id,
                "error": str(e)
            })
            raise
    
    async def _resolve_parallel(
        self,
        dependencies: List[str],
        context: ResolutionContext
    ) -> Dict[str, ResolutionResult]:
        """Resolve dependencies in parallel"""
        try:
            tasks = []
            for dep_service in dependencies:
                task = self._resolve_single_dependency(dep_service, context)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            resolved = {}
            for i, result in enumerate(results):
                dep_service = dependencies[i]
                if isinstance(result, Exception):
                    resolved[dep_service] = ResolutionResult(
                        dependency_id=dep_service,
                        status=DependencyStatus.FAILED,
                        resolved_at=datetime.now(timezone.utc),
                        resolution_time=0.0,
                        error_message=str(result)
                    )
                else:
                    resolved[dep_service] = result
            
            return resolved
            
        except Exception as e:
            logger.error(f"Parallel resolution failed: {e}")
            raise
    
    async def _resolve_sequential(
        self,
        dependencies: List[str],
        context: ResolutionContext
    ) -> Dict[str, ResolutionResult]:
        """Resolve dependencies sequentially"""
        try:
            results = {}
            
            for dep_service in dependencies:
                try:
                    result = await self._resolve_single_dependency(dep_service, context)
                    results[dep_service] = result
                    
                    # Check if critical dependency failed
                    if (result.status == DependencyStatus.FAILED and 
                        self._is_critical_dependency(dep_service)):
                        logger.error(f"Critical dependency {dep_service} failed, stopping resolution")
                        break
                        
                except Exception as e:
                    results[dep_service] = ResolutionResult(
                        dependency_id=dep_service,
                        status=DependencyStatus.FAILED,
                        resolved_at=datetime.now(timezone.utc),
                        resolution_time=0.0,
                        error_message=str(e)
                    )
            
            return results
            
        except Exception as e:
            logger.error(f"Sequential resolution failed: {e}")
            raise
    
    async def _resolve_hierarchical(
        self,
        service_id: str,
        context: ResolutionContext
    ) -> Dict[str, ResolutionResult]:
        """Resolve dependencies in hierarchical order based on initialization order"""
        try:
            # Get all dependencies in topological order
            dependency_order = self._get_topological_order(service_id)
            
            results = {}
            for level_services in dependency_order:
                # Resolve services at the same level in parallel
                level_results = await self._resolve_parallel(level_services, context)
                results.update(level_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Hierarchical resolution failed: {e}")
            raise
    
    async def _resolve_default(
        self,
        dependencies: List[str],
        context: ResolutionContext
    ) -> Dict[str, ResolutionResult]:
        """Default dependency resolution strategy"""
        return await self._resolve_parallel(dependencies, context)
    
    async def _resolve_single_dependency(
        self,
        service_id: str,
        context: ResolutionContext
    ) -> ResolutionResult:
        """Resolve a single dependency"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Check cache first
            if context.cache_enabled:
                cached_result = self._get_cached_result(service_id)
                if cached_result:
                    cached_result.cache_hit = True
                    self._update_cache_hit_rate(True)
                    return cached_result
            
            self._update_cache_hit_rate(False)
            
            # Check for circular dependency
            if service_id in context.resolution_path:
                return ResolutionResult(
                    dependency_id=service_id,
                    status=DependencyStatus.CIRCULAR,
                    resolved_at=datetime.now(timezone.utc),
                    resolution_time=0.0,
                    error_message=f"Circular dependency detected: {' -> '.join(context.resolution_path + [service_id])}"
                )
            
            # Add to resolution path
            new_context = ResolutionContext(
                context_id=context.context_id,
                requested_service=context.requested_service,
                resolution_strategy=context.resolution_strategy,
                timeout_seconds=context.timeout_seconds,
                cache_enabled=context.cache_enabled,
                parallel_resolution=context.parallel_resolution,
                max_depth=context.max_depth,
                current_depth=context.current_depth + 1,
                resolution_path=context.resolution_path + [service_id],
                metadata=context.metadata
            )
            
            # Perform actual resolution
            result_data = await self._perform_service_resolution(service_id, new_context)
            
            resolution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = ResolutionResult(
                dependency_id=service_id,
                status=DependencyStatus.RESOLVED,
                resolved_at=datetime.now(timezone.utc),
                resolution_time=resolution_time,
                result_data=result_data
            )
            
            # Cache result if enabled
            if context.cache_enabled:
                self._cache_result(service_id, result)
            
            return result
            
        except Exception as e:
            resolution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            return ResolutionResult(
                dependency_id=service_id,
                status=DependencyStatus.FAILED,
                resolved_at=datetime.now(timezone.utc),
                resolution_time=resolution_time,
                error_message=str(e)
            )
    
    async def _perform_service_resolution(
        self,
        service_id: str,
        context: ResolutionContext
    ) -> Any:
        """Perform actual service resolution logic"""
        try:
            if service_id not in self.service_definitions:
                raise ValueError(f"Service {service_id} not registered")
            
            service = self.service_definitions[service_id]
            
            # Simulate service health check
            await asyncio.sleep(0.1)  # Simulate network call
            
            # Check if service has sub-dependencies
            if service.dependencies:
                sub_dependencies = await self.resolve_dependencies(service_id, context)
                
                # Check if all critical sub-dependencies are resolved
                for dep_id, dep_result in sub_dependencies.items():
                    if (dep_result.status == DependencyStatus.FAILED and 
                        self._is_critical_dependency(dep_id)):
                        raise Exception(f"Critical sub-dependency {dep_id} failed")
            
            # Return resolution data
            return {
                "service_id": service_id,
                "service_name": service.name,
                "endpoint": service.endpoint,
                "status": "available",
                "resolved_at": datetime.now(timezone.utc).isoformat(),
                "provides": service.provides,
                "health_status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Service resolution failed for {service_id}: {e}")
            raise
    
    def _get_cached_result(self, service_id: str) -> Optional[ResolutionResult]:
        """Get cached resolution result if valid"""
        try:
            if service_id not in self.resolution_cache:
                return None
            
            cached_result = self.resolution_cache[service_id]
            cache_time = self.cache_timestamps.get(service_id)
            
            if not cache_time:
                return None
            
            # Check cache expiration
            cache_age = (datetime.now(timezone.utc) - cache_time).total_seconds()
            
            # Find dependency definition for cache duration
            cache_duration = 300  # Default 5 minutes
            for dep in self.dependency_definitions.values():
                if dep.target_service == service_id:
                    cache_duration = dep.cache_duration
                    break
            
            if cache_age < cache_duration:
                return cached_result
            else:
                # Remove expired cache
                del self.resolution_cache[service_id]
                del self.cache_timestamps[service_id]
                return None
                
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None
    
    def _cache_result(self, service_id: str, result: ResolutionResult):
        """Cache resolution result"""
        try:
            # Implement LRU cache behavior
            if len(self.resolution_cache) >= self.cache_size:
                # Remove oldest entry
                oldest_service = min(self.cache_timestamps.keys(), 
                                   key=lambda k: self.cache_timestamps[k])
                del self.resolution_cache[oldest_service]
                del self.cache_timestamps[oldest_service]
            
            self.resolution_cache[service_id] = result
            self.cache_timestamps[service_id] = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
    
    def _update_cache_hit_rate(self, hit: bool):
        """Update cache hit rate statistics"""
        # Simple exponential moving average
        if self.total_resolutions == 0:
            self.cache_hit_rate = 1.0 if hit else 0.0
        else:
            alpha = 0.1  # Smoothing factor
            hit_value = 1.0 if hit else 0.0
            self.cache_hit_rate = alpha * hit_value + (1 - alpha) * self.cache_hit_rate
    
    def _is_critical_dependency(self, service_id: str) -> bool:
        """Check if dependency is critical"""
        for dep in self.dependency_definitions.values():
            if (dep.target_service == service_id and 
                dep.priority in [DependencyPriority.CRITICAL, DependencyPriority.HIGH] and
                dep.required):
                return True
        return False
    
    def _get_topological_order(self, service_id: str) -> List[List[str]]:
        """Get topological order of dependencies for hierarchical resolution"""
        try:
            # Create subgraph with only dependencies of the service
            service_deps = self._get_all_dependencies(service_id)
            subgraph = self.dependency_graph.subgraph(service_deps)
            
            # Group by initialization order
            levels = defaultdict(list)
            for node in service_deps:
                if node in self.service_definitions:
                    order = self.service_definitions[node].initialization_order
                    levels[order].append(node)
            
            # Return sorted levels
            sorted_levels = []
            for order in sorted(levels.keys()):
                sorted_levels.append(levels[order])
            
            return sorted_levels
            
        except Exception as e:
            logger.error(f"Topological order calculation failed: {e}")
            return [[service_id]]
    
    def _get_all_dependencies(self, service_id: str) -> Set[str]:
        """Get all dependencies (direct and transitive) of a service"""
        try:
            if service_id not in self.dependency_graph:
                return set()
            
            dependencies = set()
            to_visit = deque([service_id])
            visited = set()
            
            while to_visit:
                current = to_visit.popleft()
                if current in visited:
                    continue
                
                visited.add(current)
                
                # Get direct dependencies
                for successor in self.dependency_graph.successors(current):
                    dependencies.add(successor)
                    if successor not in visited:
                        to_visit.append(successor)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Dependency traversal failed: {e}")
            return set()
    
    async def _emit_resolution_event(self, event_type: str, data: Dict[str, Any]):
        """Emit resolution events to registered handlers"""
        try:
            event_data = {
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **data
            }
            
            for handler in self.event_handlers.get(event_type, []):
                try:
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"Event emission failed: {e}")
    
    def get_dependency_graph_info(self) -> Dict[str, Any]:
        """Get dependency graph information and analysis"""
        try:
            graph_info = {
                "total_services": len(self.service_definitions),
                "total_dependencies": len(self.dependency_definitions),
                "graph_nodes": self.dependency_graph.number_of_nodes(),
                "graph_edges": self.dependency_graph.number_of_edges(),
                "is_acyclic": nx.is_directed_acyclic_graph(self.dependency_graph),
                "circular_dependencies": len(self.circular_dependencies),
                "strongly_connected_components": len(list(nx.strongly_connected_components(self.dependency_graph))),
                "cache_hit_rate": self.cache_hit_rate,
                "total_resolutions": self.total_resolutions,
                "successful_resolutions": self.successful_resolutions,
                "success_rate": (self.successful_resolutions / max(self.total_resolutions, 1)) * 100
            }
            
            return graph_info
            
        except Exception as e:
            logger.error(f"Graph info generation failed: {e}")
            return {}
    
    def get_service_dependencies(self, service_id: str) -> Dict[str, Any]:
        """Get detailed dependency information for a service"""
        try:
            if service_id not in self.service_definitions:
                return {}
            
            service = self.service_definitions[service_id]
            all_deps = self._get_all_dependencies(service_id)
            
            return {
                "service_id": service_id,
                "service_name": service.name,
                "direct_dependencies": service.dependencies,
                "all_dependencies": list(all_deps),
                "dependency_count": len(all_deps),
                "provides": service.provides,
                "initialization_order": service.initialization_order,
                "circular_dependencies": [
                    (source, target) for source, target in self.circular_dependencies
                    if source == service_id or target == service_id
                ]
            }
            
        except Exception as e:
            logger.error(f"Service dependency info failed: {e}")
            return {}
    
    def clear_cache(self, service_id: Optional[str] = None):
        """Clear resolution cache"""
        try:
            if service_id:
                if service_id in self.resolution_cache:
                    del self.resolution_cache[service_id]
                if service_id in self.cache_timestamps:
                    del self.cache_timestamps[service_id]
                logger.info(f"Cache cleared for service {service_id}")
            else:
                self.resolution_cache.clear()
                self.cache_timestamps.clear()
                logger.info("All resolution cache cleared")
                
        except Exception as e:
            logger.error(f"Cache clearing failed: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for resolution events"""
        self.event_handlers[event_type].append(handler)
    
    def get_resolution_metrics(self) -> Dict[str, Any]:
        """Get resolution performance metrics"""
        try:
            avg_resolution_times = {}
            for service_id, times in self.resolution_metrics.items():
                if times:
                    avg_resolution_times[service_id] = sum(times) / len(times)
            
            return {
                "total_resolutions": self.total_resolutions,
                "successful_resolutions": self.successful_resolutions,
                "success_rate": (self.successful_resolutions / max(self.total_resolutions, 1)) * 100,
                "cache_hit_rate": self.cache_hit_rate,
                "cache_size": len(self.resolution_cache),
                "active_resolutions": len(self.active_resolutions),
                "average_resolution_times": avg_resolution_times,
                "circular_dependencies_count": len(self.circular_dependencies)
            }
            
        except Exception as e:
            logger.error(f"Metrics generation failed: {e}")
            return {}
    
    def shutdown(self):
        """Shutdown dependency resolver and cleanup"""
        try:
            # Clear all caches
            self.clear_cache()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info("DependencyResolver shutdown completed")
            
        except Exception as e:
            logger.error(f"DependencyResolver shutdown failed: {e}")
