"""Validation Index - Central Validator Registry and Routing System
===================================================================

Industrial-grade validator registry and routing system for the IA Influencer
Agent Platform, providing centralized validator management, intelligent routing,
health monitoring, and dynamic discovery capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Registry Capabilities:
- Centralized validator registry with auto-discovery
- Intelligent routing based on content type and context
- Load balancing and health monitoring for validators
- Dynamic validator configuration and hot-reload
- Performance metrics aggregation and analysis
- Validator versioning and compatibility management
- Integration with validation chains and pipelines
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable, Set, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import importlib
import inspect
from pathlib import Path
import weakref
from concurrent.futures import ThreadPoolExecutor
import statistics

logger = logging.getLogger(__name__)

class ValidatorStatus(Enum):
    """Validator status states."""
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class RoutingStrategy(Enum):
    """Routing strategies for validator selection."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    BEST_PERFORMANCE = "best_performance"
    CONTENT_SPECIALIZED = "content_specialized"
    RANDOM = "random"

class LoadBalancingMode(Enum):
    """Load balancing modes."""
    SIMPLE = "simple"
    WEIGHTED = "weighted"
    ADAPTIVE = "adaptive"
    PRIORITY_BASED = "priority_based"

@dataclass
class ValidatorInfo:
    """Information about a registered validator."""
    validator_id: str
    validator_name: str
    validator_class: str
    version: str
    description: str
    supported_content_types: List[str] = field(default_factory=list)
    supported_contexts: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    performance_profile: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ValidatorMetrics:
    """Performance metrics for a validator."""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time_ms: float = 0.0
    min_execution_time_ms: float = float('inf')
    max_execution_time_ms: float = 0.0
    current_load: int = 0
    max_concurrent_load: int = 1
    last_execution_time: Optional[datetime] = None
    error_rate: float = 0.0
    availability_score: float = 1.0
    performance_score: float = 1.0

@dataclass
class ValidatorInstance:
    """Runtime instance of a validator."""
    validator_info: ValidatorInfo
    validator_object: Any
    status: ValidatorStatus = ValidatorStatus.AVAILABLE
    metrics: ValidatorMetrics = field(default_factory=ValidatorMetrics)
    current_config: Dict[str, Any] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None
    health_check_interval_seconds: int = 300  # 5 minutes
    instance_id: str = field(default_factory=lambda: f"instance_{id(object())}")

@dataclass
class RoutingRequest:
    """Request for validator routing."""
    content_type: str
    context: str
    capabilities_required: List[str] = field(default_factory=list)
    performance_requirements: Dict[str, Any] = field(default_factory=dict)
    exclude_validators: List[str] = field(default_factory=list)
    routing_strategy: RoutingStrategy = RoutingStrategy.BEST_PERFORMANCE
    load_balancing_mode: LoadBalancingMode = LoadBalancingMode.ADAPTIVE

@dataclass
class RoutingResult:
    """Result of validator routing."""
    validator_instance: Optional[ValidatorInstance]
    routing_score: float
    selection_reasoning: str
    alternative_validators: List[str] = field(default_factory=list)
    routing_duration_ms: int = 0
    routed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class ValidatorRegistry:
    """Central registry for all validators."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize validator registry.
        
        Args:
            config: Optional configuration
        """
        self.config = config or {}
        self.validators: Dict[str, ValidatorInstance] = {}
        self.validator_classes: Dict[str, Type] = {}
        self.routing_history: List[Dict[str, Any]] = []
        
        # Registry settings
        self.auto_discovery_enabled = self.config.get('auto_discovery_enabled', True)
        self.health_monitoring_enabled = self.config.get('health_monitoring_enabled', True)
        self.metrics_collection_enabled = self.config.get('metrics_collection_enabled', True)
        self.max_routing_history = self.config.get('max_routing_history', 1000)
        
        # Load balancing settings
        self.default_routing_strategy = RoutingStrategy(
            self.config.get('default_routing_strategy', 'best_performance')
        )
        self.max_concurrent_validators = self.config.get('max_concurrent_validators', 10)
        
        # Initialize background tasks
        self._health_check_task = None
        self._metrics_aggregation_task = None
        
        logger.info("ValidatorRegistry initialized")
    
    async def start(self):
        """Start registry background tasks."""
        if self.health_monitoring_enabled:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        if self.metrics_collection_enabled:
            self._metrics_aggregation_task = asyncio.create_task(self._metrics_aggregation_loop())
        
        # Auto-discover validators if enabled
        if self.auto_discovery_enabled:
            await self._auto_discover_validators()
        
        logger.info("ValidatorRegistry started")
    
    async def stop(self):
        """Stop registry background tasks."""
        if self._health_check_task:
            self._health_check_task.cancel()
        
        if self._metrics_aggregation_task:
            self._metrics_aggregation_task.cancel()
        
        logger.info("ValidatorRegistry stopped")
    
    async def register_validator(self, validator_info: ValidatorInfo,
                                validator_class: Type,
                                config: Optional[Dict[str, Any]] = None) -> str:
        """Register a validator with the registry.
        
        Args:
            validator_info: Validator information
            validator_class: Validator class
            config: Optional configuration for the validator
            
        Returns:
            Instance ID of registered validator
        """
        try:
            # Create validator instance
            validator_object = validator_class(config or {})
            
            # Create validator instance record
            instance = ValidatorInstance(
                validator_info=validator_info,
                validator_object=validator_object,
                current_config=config or {}
            )
            
            # Store in registry
            self.validators[instance.instance_id] = instance
            self.validator_classes[validator_info.validator_name] = validator_class
            
            logger.info(f"Registered validator '{validator_info.validator_name}' with ID '{instance.instance_id}'")
            
            # Perform initial health check
            await self._perform_health_check(instance)
            
            return instance.instance_id
            
        except Exception as e:
            logger.error(f"Failed to register validator '{validator_info.validator_name}': {e}")
            raise
    
    def unregister_validator(self, instance_id: str) -> bool:
        """Unregister a validator from the registry.
        
        Args:
            instance_id: Instance ID of validator to unregister
            
        Returns:
            True if validator was unregistered
        """
        if instance_id in self.validators:
            validator_name = self.validators[instance_id].validator_info.validator_name
            del self.validators[instance_id]
            logger.info(f"Unregistered validator instance '{instance_id}' ({validator_name})")
            return True
        return False
    
    async def route_to_validator(self, request: RoutingRequest) -> RoutingResult:
        """Route request to appropriate validator.
        
        Args:
            request: Routing request
            
        Returns:
            RoutingResult with selected validator
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Find suitable validators
            candidates = self._find_suitable_validators(request)
            
            if not candidates:
                return RoutingResult(
                    validator_instance=None,
                    routing_score=0.0,
                    selection_reasoning="No suitable validators found",
                    routing_duration_ms=int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                )
            
            # Apply routing strategy
            selected_validator = await self._apply_routing_strategy(candidates, request)
            
            # Calculate routing score
            routing_score = self._calculate_routing_score(selected_validator, request)
            
            # Generate alternative validators
            alternatives = [v.instance_id for v in candidates if v != selected_validator][:3]
            
            # Record routing decision
            self._record_routing_decision(request, selected_validator, routing_score)
            
            end_time = datetime.now(timezone.utc)
            routing_duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return RoutingResult(
                validator_instance=selected_validator,
                routing_score=routing_score,
                selection_reasoning=self._generate_selection_reasoning(selected_validator, request),
                alternative_validators=alternatives,
                routing_duration_ms=routing_duration_ms
            )
            
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return RoutingResult(
                validator_instance=None,
                routing_score=0.0,
                selection_reasoning=f"Routing error: {str(e)}",
                routing_duration_ms=int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            )
    
    def _find_suitable_validators(self, request: RoutingRequest) -> List[ValidatorInstance]:
        """Find validators suitable for the request.
        
        Args:
            request: Routing request
            
        Returns:
            List of suitable validator instances
        """
        suitable_validators = []
        
        for instance in self.validators.values():
            # Skip excluded validators
            if instance.instance_id in request.exclude_validators:
                continue
            
            # Check availability
            if instance.status not in [ValidatorStatus.AVAILABLE, ValidatorStatus.BUSY]:
                continue
            
            # Check content type support
            if (request.content_type and 
                instance.validator_info.supported_content_types and
                request.content_type not in instance.validator_info.supported_content_types):
                continue
            
            # Check context support
            if (request.context and
                instance.validator_info.supported_contexts and
                request.context not in instance.validator_info.supported_contexts):
                continue
            
            # Check required capabilities
            if request.capabilities_required:
                missing_capabilities = set(request.capabilities_required) - set(instance.validator_info.capabilities)
                if missing_capabilities:
                    continue
            
            # Check performance requirements
            if not self._meets_performance_requirements(instance, request.performance_requirements):
                continue
            
            suitable_validators.append(instance)
        
        return suitable_validators
    
    def _meets_performance_requirements(self, instance: ValidatorInstance,
                                      requirements: Dict[str, Any]) -> bool:
        """Check if validator meets performance requirements.
        
        Args:
            instance: Validator instance
            requirements: Performance requirements
            
        Returns:
            True if requirements are met
        """
        metrics = instance.metrics
        
        # Check maximum execution time
        if 'max_execution_time_ms' in requirements:
            if metrics.average_execution_time_ms > requirements['max_execution_time_ms']:
                return False
        
        # Check minimum availability
        if 'min_availability' in requirements:
            if metrics.availability_score < requirements['min_availability']:
                return False
        
        # Check maximum error rate
        if 'max_error_rate' in requirements:
            if metrics.error_rate > requirements['max_error_rate']:
                return False
        
        # Check load capacity
        if 'max_load' in requirements:
            if metrics.current_load >= requirements['max_load']:
                return False
        
        return True
    
    async def _apply_routing_strategy(self, candidates: List[ValidatorInstance],
                                    request: RoutingRequest) -> ValidatorInstance:
        """Apply routing strategy to select validator.
        
        Args:
            candidates: List of candidate validators
            request: Routing request
            
        Returns:
            Selected validator instance
        """
        if not candidates:
            raise ValueError("No candidates available for routing")
        
        if len(candidates) == 1:
            return candidates[0]
        
        strategy = request.routing_strategy
        
        if strategy == RoutingStrategy.ROUND_ROBIN:
            return self._select_round_robin(candidates)
        
        elif strategy == RoutingStrategy.LEAST_LOADED:
            return self._select_least_loaded(candidates)
        
        elif strategy == RoutingStrategy.BEST_PERFORMANCE:
            return self._select_best_performance(candidates)
        
        elif strategy == RoutingStrategy.CONTENT_SPECIALIZED:
            return self._select_content_specialized(candidates, request.content_type)
        
        elif strategy == RoutingStrategy.RANDOM:
            import random
            return random.choice(candidates)
        
        else:
            # Default to best performance
            return self._select_best_performance(candidates)
    
    def _select_round_robin(self, candidates: List[ValidatorInstance]) -> ValidatorInstance:
        """Select validator using round-robin strategy.
        
        Args:
            candidates: List of candidate validators
            
        Returns:
            Selected validator instance
        """
        # Simple round-robin based on total executions
        return min(candidates, key=lambda v: v.metrics.total_executions)
    
    def _select_least_loaded(self, candidates: List[ValidatorInstance]) -> ValidatorInstance:
        """Select validator with least current load.
        
        Args:
            candidates: List of candidate validators
            
        Returns:
            Selected validator instance
        """
        return min(candidates, key=lambda v: v.metrics.current_load)
    
    def _select_best_performance(self, candidates: List[ValidatorInstance]) -> ValidatorInstance:
        """Select validator with best performance score.
        
        Args:
            candidates: List of candidate validators
            
        Returns:
            Selected validator instance
        """
        return max(candidates, key=lambda v: v.metrics.performance_score)
    
    def _select_content_specialized(self, candidates: List[ValidatorInstance],
                                  content_type: str) -> ValidatorInstance:
        """Select validator specialized for content type.
        
        Args:
            candidates: List of candidate validators
            content_type: Content type
            
        Returns:
            Selected validator instance
        """
        # Prefer validators that specialize in the content type
        specialized = [v for v in candidates 
                      if content_type in v.validator_info.supported_content_types]
        
        if specialized:
            return self._select_best_performance(specialized)
        else:
            return self._select_best_performance(candidates)
    
    def _calculate_routing_score(self, validator: ValidatorInstance,
                               request: RoutingRequest) -> float:
        """Calculate routing score for selected validator.
        
        Args:
            validator: Selected validator instance
            request: Routing request
            
        Returns:
            Routing score (0.0 to 1.0)
        """
        score = 0.0
        factors = 0
        
        # Performance score factor
        score += validator.metrics.performance_score
        factors += 1
        
        # Availability score factor
        score += validator.metrics.availability_score
        factors += 1
        
        # Load factor (inverse of current load)
        max_load = max(validator.metrics.max_concurrent_load, 1)
        load_factor = 1.0 - (validator.metrics.current_load / max_load)
        score += load_factor
        factors += 1
        
        # Content type specialization factor
        if (request.content_type and 
            request.content_type in validator.validator_info.supported_content_types):
            score += 1.0
            factors += 1
        
        # Context specialization factor
        if (request.context and 
            request.context in validator.validator_info.supported_contexts):
            score += 1.0
            factors += 1
        
        # Capability match factor
        if request.capabilities_required:
            validator_capabilities = set(validator.validator_info.capabilities)
            required_capabilities = set(request.capabilities_required)
            match_ratio = len(required_capabilities & validator_capabilities) / len(required_capabilities)
            score += match_ratio
            factors += 1
        
        return score / factors if factors > 0 else 0.0
    
    def _generate_selection_reasoning(self, validator: ValidatorInstance,
                                    request: RoutingRequest) -> str:
        """Generate human-readable selection reasoning.
        
        Args:
            validator: Selected validator instance
            request: Routing request
            
        Returns:
            Selection reasoning string
        """
        reasons = []
        
        # Performance reasoning
        if validator.metrics.performance_score >= 0.8:
            reasons.append("high performance score")
        
        # Load reasoning
        if validator.metrics.current_load == 0:
            reasons.append("no current load")
        elif validator.metrics.current_load < validator.metrics.max_concurrent_load / 2:
            reasons.append("low current load")
        
        # Specialization reasoning
        if (request.content_type and 
            request.content_type in validator.validator_info.supported_content_types):
            reasons.append(f"specialized for {request.content_type}")
        
        if (request.context and 
            request.context in validator.validator_info.supported_contexts):
            reasons.append(f"supports {request.context} context")
        
        # Capability reasoning
        if request.capabilities_required:
            matching_capabilities = set(request.capabilities_required) & set(validator.validator_info.capabilities)
            if matching_capabilities:
                reasons.append(f"provides {', '.join(matching_capabilities)}")
        
        if reasons:
            return f"Selected '{validator.validator_info.validator_name}' due to: {', '.join(reasons)}"
        else:
            return f"Selected '{validator.validator_info.validator_name}' as available option"
    
    def _record_routing_decision(self, request: RoutingRequest,
                               validator: ValidatorInstance,
                               routing_score: float) -> None:
        """Record routing decision for analysis.
        
        Args:
            request: Routing request
            validator: Selected validator
            routing_score: Routing score
        """
        decision = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'content_type': request.content_type,
            'context': request.context,
            'routing_strategy': request.routing_strategy.value,
            'selected_validator': validator.validator_info.validator_name,
            'validator_instance_id': validator.instance_id,
            'routing_score': routing_score,
            'validator_load': validator.metrics.current_load,
            'validator_performance': validator.metrics.performance_score
        }
        
        self.routing_history.append(decision)
        
        # Maintain history size limit
        if len(self.routing_history) > self.max_routing_history:
            self.routing_history = self.routing_history[-self.max_routing_history:]
    
    async def _auto_discover_validators(self) -> None:
        """Auto-discover validators in the validators module."""
        try:
            # Import validators module
            validators_module = importlib.import_module('data.validators')
            
            # Scan for validator classes
            for name in dir(validators_module):
                obj = getattr(validators_module, name)
                
                # Check if it's a validator class
                if (inspect.isclass(obj) and 
                    name.endswith('Validator') and
                    name != 'ValidatorRegistry'):
                    
                    try:
                        # Extract validator information
                        validator_info = self._extract_validator_info(obj)
                        
                        # Register validator if not already registered
                        if not any(v.validator_info.validator_name == validator_info.validator_name 
                                 for v in self.validators.values()):
                            
                            await self.register_validator(validator_info, obj)
                            logger.info(f"Auto-discovered and registered validator: {validator_info.validator_name}")
                    
                    except Exception as e:
                        logger.warning(f"Failed to auto-register validator {name}: {e}")
            
        except Exception as e:
            logger.error(f"Auto-discovery failed: {e}")
    
    def _extract_validator_info(self, validator_class: Type) -> ValidatorInfo:
        """Extract validator information from class.
        
        Args:
            validator_class: Validator class
            
        Returns:
            ValidatorInfo object
        """
        # Extract basic information
        validator_name = validator_class.__name__
        description = validator_class.__doc__ or f"{validator_name} validator"
        
        # Extract version from class or module
        version = getattr(validator_class, '__version__', '1.0.0')
        
        # Extract supported content types (if available)
        supported_content_types = getattr(validator_class, 'SUPPORTED_CONTENT_TYPES', ['*'])
        
        # Extract supported contexts (if available)
        supported_contexts = getattr(validator_class, 'SUPPORTED_CONTEXTS', ['*'])
        
        # Extract capabilities (if available)
        capabilities = getattr(validator_class, 'CAPABILITIES', [])
        
        # Extract dependencies (if available)
        dependencies = getattr(validator_class, 'DEPENDENCIES', [])
        
        return ValidatorInfo(
            validator_id=f"{validator_name}_{id(validator_class)}",
            validator_name=validator_name,
            validator_class=f"{validator_class.__module__}.{validator_class.__name__}",
            version=version,
            description=description.split('\n')[0],  # First line of docstring
            supported_content_types=supported_content_types,
            supported_contexts=supported_contexts,
            capabilities=capabilities,
            dependencies=dependencies
        )
    
    async def _health_check_loop(self) -> None:
        """Background task for validator health checking."""
        while True:
            try:
                for instance in list(self.validators.values()):
                    await self._perform_health_check(instance)
                
                # Wait for next health check cycle
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _perform_health_check(self, instance: ValidatorInstance) -> None:
        """Perform health check on validator instance.
        
        Args:
            instance: Validator instance to check
        """
        try:
            # Check if health check is due
            now = datetime.now(timezone.utc)
            if (instance.last_health_check and 
                (now - instance.last_health_check).total_seconds() < instance.health_check_interval_seconds):
                return
            
            # Perform health check (simplified)
            start_time = now
            
            # Check if validator object is still valid
            if not hasattr(instance.validator_object, '__call__'):
                instance.status = ValidatorStatus.ERROR
                return
            
            # Try to call a health check method if available
            if hasattr(instance.validator_object, 'health_check'):
                result = await instance.validator_object.health_check()
                if not result:
                    instance.status = ValidatorStatus.UNAVAILABLE
                    return
            
            # Update status and timestamp
            instance.status = ValidatorStatus.AVAILABLE
            instance.last_health_check = now
            
            # Update availability score based on health check success
            instance.metrics.availability_score = min(1.0, instance.metrics.availability_score + 0.1)
            
        except Exception as e:
            logger.warning(f"Health check failed for {instance.validator_info.validator_name}: {e}")
            instance.status = ValidatorStatus.ERROR
            instance.metrics.availability_score = max(0.0, instance.metrics.availability_score - 0.2)
    
    async def _metrics_aggregation_loop(self) -> None:
        """Background task for metrics aggregation."""
        while True:
            try:
                await self._aggregate_metrics()
                await asyncio.sleep(300)  # Aggregate every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics aggregation loop error: {e}")
                await asyncio.sleep(60)
    
    async def _aggregate_metrics(self) -> None:
        """Aggregate metrics across all validators."""
        for instance in self.validators.values():
            metrics = instance.metrics
            
            # Calculate error rate
            if metrics.total_executions > 0:
                metrics.error_rate = metrics.failed_executions / metrics.total_executions
            
            # Calculate performance score
            performance_factors = []
            
            # Execution time factor
            if metrics.average_execution_time_ms > 0:
                # Lower execution time = better performance
                time_factor = max(0.0, 1.0 - (metrics.average_execution_time_ms / 10000))  # 10s baseline
                performance_factors.append(time_factor)
            
            # Success rate factor
            if metrics.total_executions > 0:
                success_rate = metrics.successful_executions / metrics.total_executions
                performance_factors.append(success_rate)
            
            # Load factor
            if metrics.max_concurrent_load > 0:
                load_factor = 1.0 - (metrics.current_load / metrics.max_concurrent_load)
                performance_factors.append(load_factor)
            
            # Calculate overall performance score
            if performance_factors:
                metrics.performance_score = statistics.mean(performance_factors)
            else:
                metrics.performance_score = 1.0
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get overall registry status.
        
        Returns:
            Registry status information
        """
        total_validators = len(self.validators)
        available_validators = sum(1 for v in self.validators.values() 
                                 if v.status == ValidatorStatus.AVAILABLE)
        busy_validators = sum(1 for v in self.validators.values() 
                            if v.status == ValidatorStatus.BUSY)
        error_validators = sum(1 for v in self.validators.values() 
                             if v.status == ValidatorStatus.ERROR)
        
        # Calculate aggregate metrics
        total_executions = sum(v.metrics.total_executions for v in self.validators.values())
        total_failures = sum(v.metrics.failed_executions for v in self.validators.values())
        
        return {
            'total_validators': total_validators,
            'available_validators': available_validators,
            'busy_validators': busy_validators,
            'error_validators': error_validators,
            'registry_health': available_validators / total_validators if total_validators > 0 else 0.0,
            'total_executions': total_executions,
            'overall_error_rate': total_failures / total_executions if total_executions > 0 else 0.0,
            'routing_history_size': len(self.routing_history),
            'auto_discovery_enabled': self.auto_discovery_enabled,
            'health_monitoring_enabled': self.health_monitoring_enabled
        }
    
    def get_validator_metrics(self, validator_name: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for specific validator or all validators.
        
        Args:
            validator_name: Optional validator name filter
            
        Returns:
            Validator metrics
        """
        if validator_name:
            # Get metrics for specific validator
            instances = [v for v in self.validators.values() 
                        if v.validator_info.validator_name == validator_name]
            if not instances:
                return {}
            
            instance = instances[0]  # Use first instance
            return {
                'validator_name': validator_name,
                'instance_id': instance.instance_id,
                'status': instance.status.value,
                'metrics': {
                    'total_executions': instance.metrics.total_executions,
                    'successful_executions': instance.metrics.successful_executions,
                    'failed_executions': instance.metrics.failed_executions,
                    'average_execution_time_ms': instance.metrics.average_execution_time_ms,
                    'current_load': instance.metrics.current_load,
                    'error_rate': instance.metrics.error_rate,
                    'availability_score': instance.metrics.availability_score,
                    'performance_score': instance.metrics.performance_score
                }
            }
        else:
            # Get metrics for all validators
            return {
                instance.instance_id: {
                    'validator_name': instance.validator_info.validator_name,
                    'status': instance.status.value,
                    'metrics': {
                        'total_executions': instance.metrics.total_executions,
                        'successful_executions': instance.metrics.successful_executions,
                        'failed_executions': instance.metrics.failed_executions,
                        'average_execution_time_ms': instance.metrics.average_execution_time_ms,
                        'current_load': instance.metrics.current_load,
                        'error_rate': instance.metrics.error_rate,
                        'availability_score': instance.metrics.availability_score,
                        'performance_score': instance.metrics.performance_score
                    }
                }
                for instance in self.validators.values()
            }
    
    def update_validator_metrics(self, instance_id: str, execution_time_ms: int,
                               success: bool) -> None:
        """Update validator metrics after execution.
        
        Args:
            instance_id: Validator instance ID
            execution_time_ms: Execution time in milliseconds
            success: Whether execution was successful
        """
        if instance_id not in self.validators:
            return
        
        instance = self.validators[instance_id]
        metrics = instance.metrics
        
        # Update execution counts
        metrics.total_executions += 1
        if success:
            metrics.successful_executions += 1
        else:
            metrics.failed_executions += 1
        
        # Update execution times
        if execution_time_ms > 0:
            if metrics.total_executions == 1:
                metrics.average_execution_time_ms = execution_time_ms
            else:
                # Rolling average
                total_time = metrics.average_execution_time_ms * (metrics.total_executions - 1)
                metrics.average_execution_time_ms = (total_time + execution_time_ms) / metrics.total_executions
            
            metrics.min_execution_time_ms = min(metrics.min_execution_time_ms, execution_time_ms)
            metrics.max_execution_time_ms = max(metrics.max_execution_time_ms, execution_time_ms)
        
        # Update last execution time
        metrics.last_execution_time = datetime.now(timezone.utc)
        
        # Update availability score based on success
        if success:
            metrics.availability_score = min(1.0, metrics.availability_score + 0.01)
        else:
            metrics.availability_score = max(0.0, metrics.availability_score - 0.05)

class ValidationEngine:
    """Main validation engine combining registry and management."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize validation engine.
        
        Args:
            config: Optional configuration
        """
        self.config = config or {}
        self.registry = ValidatorRegistry(config.get('registry', {}))
        
        # Engine settings
        self.enable_caching = self.config.get('enable_caching', True)
        self.cache_ttl_seconds = self.config.get('cache_ttl_seconds', 3600)
        self.max_concurrent_validations = self.config.get('max_concurrent_validations', 10)
        
        # Execution tracking
        self.active_validations: Dict[str, datetime] = {}
        self.validation_cache: Dict[str, Any] = {}
        
        logger.info("ValidationEngine initialized")
    
    async def start(self):
        """Start validation engine."""
        await self.registry.start()
        logger.info("ValidationEngine started")
    
    async def stop(self):
        """Stop validation engine."""
        await self.registry.stop()
        logger.info("ValidationEngine stopped")
    
    async def validate(self, content: Any, content_type: str, context: str = "default",
                     validator_name: Optional[str] = None,
                     routing_strategy: RoutingStrategy = RoutingStrategy.BEST_PERFORMANCE,
                     config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate content using appropriate validator.
        
        Args:
            content: Content to validate
            content_type: Type of content
            context: Validation context
            validator_name: Specific validator to use (optional)
            routing_strategy: Routing strategy for validator selection
            config: Optional configuration
            
        Returns:
            Validation result
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Check concurrency limit
            if len(self.active_validations) >= self.max_concurrent_validations:
                return {
                    'success': False,
                    'error': 'Maximum concurrent validations reached',
                    'validation_time_ms': 0
                }
            
            # Generate cache key
            cache_key = self._generate_cache_key(content, content_type, context, config)
            
            # Check cache if enabled
            if self.enable_caching and cache_key in self.validation_cache:
                cached_result = self.validation_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    logger.debug(f"Returning cached validation result for {content_type}")
                    return cached_result['result']
            
            # Track active validation
            validation_id = f"val_{id(content)}_{int(start_time.timestamp())}"
            self.active_validations[validation_id] = start_time
            
            try:
                # Route to appropriate validator
                if validator_name:
                    # Use specific validator
                    validator_instance = self._get_validator_by_name(validator_name)
                    if not validator_instance:
                        return {
                            'success': False,
                            'error': f'Validator {validator_name} not found',
                            'validation_time_ms': 0
                        }
                else:
                    # Use routing
                    routing_request = RoutingRequest(
                        content_type=content_type,
                        context=context,
                        routing_strategy=routing_strategy
                    )
                    routing_result = await self.registry.route_to_validator(routing_request)
                    validator_instance = routing_result.validator_instance
                    
                    if not validator_instance:
                        return {
                            'success': False,
                            'error': 'No suitable validator found',
                            'routing_info': routing_result,
                            'validation_time_ms': 0
                        }
                
                # Execute validation
                execution_start = datetime.now(timezone.utc)
                
                # Update validator status
                validator_instance.status = ValidatorStatus.BUSY
                validator_instance.metrics.current_load += 1
                
                try:
                    # Call validator
                    if hasattr(validator_instance.validator_object, 'validate'):
                        result = await validator_instance.validator_object.validate(content, **(config or {}))
                    else:
                        result = await validator_instance.validator_object(content, **(config or {}))
                    
                    execution_end = datetime.now(timezone.utc)
                    execution_time_ms = int((execution_end - execution_start).total_seconds() * 1000)
                    
                    # Update validator metrics
                    self.registry.update_validator_metrics(
                        validator_instance.instance_id, 
                        execution_time_ms, 
                        True
                    )
                    
                    # Prepare result
                    validation_result = {
                        'success': True,
                        'result': result,
                        'validator_used': validator_instance.validator_info.validator_name,
                        'validation_time_ms': execution_time_ms,
                        'execution_context': {
                            'content_type': content_type,
                            'context': context,
                            'validator_instance_id': validator_instance.instance_id
                        }
                    }
                    
                    # Cache result if enabled
                    if self.enable_caching:
                        self.validation_cache[cache_key] = {
                            'result': validation_result,
                            'cached_at': datetime.now(timezone.utc)
                        }
                    
                    return validation_result
                
                except Exception as e:
                    execution_end = datetime.now(timezone.utc)
                    execution_time_ms = int((execution_end - execution_start).total_seconds() * 1000)
                    
                    # Update validator metrics for failure
                    self.registry.update_validator_metrics(
                        validator_instance.instance_id, 
                        execution_time_ms, 
                        False
                    )
                    
                    logger.error(f"Validation execution failed: {e}")
                    return {
                        'success': False,
                        'error': f'Validation execution failed: {str(e)}',
                        'validator_used': validator_instance.validator_info.validator_name,
                        'validation_time_ms': execution_time_ms
                    }
                
                finally:
                    # Update validator status
                    validator_instance.status = ValidatorStatus.AVAILABLE
                    validator_instance.metrics.current_load = max(0, validator_instance.metrics.current_load - 1)
            
            finally:
                # Remove from active validations
                if validation_id in self.active_validations:
                    del self.active_validations[validation_id]
        
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            end_time = datetime.now(timezone.utc)
            validation_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return {
                'success': False,
                'error': f'Validation failed: {str(e)}',
                'validation_time_ms': validation_time_ms
            }
    
    def _get_validator_by_name(self, validator_name: str) -> Optional[ValidatorInstance]:
        """Get validator instance by name.
        
        Args:
            validator_name: Validator name
            
        Returns:
            Validator instance or None
        """
        for instance in self.registry.validators.values():
            if instance.validator_info.validator_name == validator_name:
                return instance
        return None
    
    def _generate_cache_key(self, content: Any, content_type: str, context: str,
                          config: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for validation result.
        
        Args:
            content: Content to validate
            content_type: Type of content
            context: Validation context
            config: Optional configuration
            
        Returns:
            Cache key string
        """
        import hashlib
        
        # Create content hash
        if isinstance(content, (str, bytes)):
            content_hash = hashlib.md5(str(content).encode()).hexdigest()[:16]
        else:
            content_hash = hashlib.md5(str(id(content)).encode()).hexdigest()[:16]
        
        # Create config hash
        config_hash = hashlib.md5(str(config or {}).encode()).hexdigest()[:8]
        
        return f"{content_type}_{context}_{content_hash}_{config_hash}"
    
    def _is_cache_valid(self, cached_item: Dict[str, Any]) -> bool:
        """Check if cached item is still valid.
        
        Args:
            cached_item: Cached validation result
            
        Returns:
            True if cache is valid
        """
        if 'cached_at' not in cached_item:
            return False
        
        cached_at = cached_item['cached_at']
        now = datetime.now(timezone.utc)
        
        return (now - cached_at).total_seconds() < self.cache_ttl_seconds
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get validation engine status.
        
        Returns:
            Engine status information
        """
        registry_status = self.registry.get_registry_status()
        
        return {
            'engine_status': 'running',
            'active_validations': len(self.active_validations),
            'max_concurrent_validations': self.max_concurrent_validations,
            'cache_enabled': self.enable_caching,
            'cache_size': len(self.validation_cache),
            'registry_status': registry_status
        }

# Global validation engine instance
_validation_engine: Optional[ValidationEngine] = None

def get_validation_engine() -> ValidationEngine:
    """Get global validation engine instance.
    
    Returns:
        Global ValidationEngine instance
    """
    global _validation_engine
    if _validation_engine is None:
        _validation_engine = ValidationEngine()
    return _validation_engine

# Main classes and utilities for validation management
class ValidationManager:
    """High-level validation management interface."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize validation manager.
        
        Args:
            config: Optional configuration
        """
        self.engine = get_validation_engine()
        self.config = config or {}
    
    async def start(self):
        """Start validation manager."""
        await self.engine.start()
    
    async def stop(self):
        """Stop validation manager."""
        await self.engine.stop()
    
    async def validate_content(self, content: Any, **kwargs) -> Dict[str, Any]:
        """Validate content with simplified interface.
        
        Args:
            content: Content to validate
            **kwargs: Additional validation parameters
            
        Returns:
            Validation result
        """
        return await self.engine.validate(content, **kwargs)

# Configuration management
class ValidationConfig:
    """Validation configuration management."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize validation configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or defaults.
        
        Returns:
            Configuration dictionary
        """
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
        
        # Return default configuration
        return {
            'registry': {
                'auto_discovery_enabled': True,
                'health_monitoring_enabled': True,
                'metrics_collection_enabled': True,
                'default_routing_strategy': 'best_performance'
            },
            'engine': {
                'enable_caching': True,
                'cache_ttl_seconds': 3600,
                'max_concurrent_validations': 10
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

# Export main classes and functions
__all__ = [
    'ValidationEngine',
    'ValidatorRegistry',
    'ValidationManager',
    'ValidationConfig',
    'ValidatorInfo',
    'ValidatorInstance',
    'ValidatorMetrics',
    'RoutingRequest',
    'RoutingResult',
    'ValidatorStatus',
    'RoutingStrategy',
    'LoadBalancingMode',
    'get_validation_engine'
]