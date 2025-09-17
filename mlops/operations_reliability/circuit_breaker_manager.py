"""
🛡️ Circuit Breaker Manager - Enterprise Creator Economy
========================================================

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

Enterprise circuit breaker manager for cascade failure prevention
Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import time
import statistics
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import random

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"           # Normal operation
    OPEN = "open"              # Circuit open, blocking requests
    HALF_OPEN = "half_open"    # Testing if service recovered


class FailureType(Enum):
    """Types of failures that can trigger circuit breaker"""
    TIMEOUT = "timeout"
    ERROR_RESPONSE = "error_response"
    CONNECTION_ERROR = "connection_error"
    RATE_LIMIT = "rate_limit"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    CUSTOM = "custom"


class CircuitBreakerStrategy(Enum):
    """Circuit breaker strategies"""
    COUNT_BASED = "count_based"          # Based on failure count
    TIME_BASED = "time_based"            # Based on failure rate over time
    PERCENTAGE_BASED = "percentage_based" # Based on failure percentage
    ADAPTIVE = "adaptive"                # Adaptive threshold based on patterns


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    circuit_id: str
    name: str
    service_name: str
    strategy: CircuitBreakerStrategy = CircuitBreakerStrategy.COUNT_BASED
    
    # Failure thresholds
    failure_threshold: int = 5           # Number of failures to open circuit
    failure_rate_threshold: float = 50.0 # Percentage of failures to open circuit
    timeout_duration_ms: int = 5000      # Request timeout
    
    # Circuit timings
    open_timeout_seconds: int = 60       # How long circuit stays open
    half_open_max_requests: int = 3      # Max requests in half-open state
    
    # Monitoring window
    monitoring_window_seconds: int = 60  # Window for failure rate calculation
    min_requests_threshold: int = 10     # Minimum requests before opening circuit
    
    # Creator Economy specific
    creator_impact_level: str = "medium" # "critical", "high", "medium", "low"
    fallback_enabled: bool = True
    fallback_response: Dict[str, Any] = field(default_factory=dict)
    preserve_creator_data: bool = True
    revenue_protection_mode: bool = False


@dataclass
class RequestResult:
    """Individual request result"""
    request_id: str
    timestamp: datetime
    success: bool
    response_time_ms: float
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None
    creator_id: Optional[str] = None
    request_type: str = "api_call"


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    blocked_requests: int = 0
    
    # Performance metrics
    average_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    
    # Circuit state tracking
    state_changes: int = 0
    time_in_open_state_seconds: float = 0.0
    time_in_half_open_state_seconds: float = 0.0
    
    # Creator Economy metrics
    creator_requests_blocked: int = 0
    revenue_requests_blocked: int = 0
    fallback_responses_served: int = 0
    creator_satisfaction_impact: float = 0.0


class CircuitBreaker:
    """
    Individual circuit breaker implementation
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change = datetime.utcnow()
        self.next_attempt_time: Optional[datetime] = None
        
        # Request tracking
        self.request_history: deque = deque(maxlen=1000)
        self.half_open_requests = 0
        
        # Metrics
        self.metrics = CircuitBreakerMetrics()
        
        # Creator Economy specific
        self.creator_request_tracking: Dict[str, int] = defaultdict(int)
        self.revenue_request_tracking: int = 0
        
        logger.info(f"Circuit breaker created: {config.name}")
    
    async def call(self, request_func: Callable, *args, **kwargs) -> Any:
        """
        Execute a request through the circuit breaker
        
        Args:
            request_func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result or fallback response
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Check if circuit should block request
            if await self._should_block_request():
                return await self._handle_blocked_request(request_id)
            
            # Execute request
            result = await self._execute_request(request_func, request_id, *args, **kwargs)
            
            # Record success
            response_time = (time.time() - start_time) * 1000
            await self._record_success(request_id, response_time)
            
            return result
            
        except Exception as e:
            # Record failure
            response_time = (time.time() - start_time) * 1000
            await self._record_failure(request_id, response_time, str(e))
            
            # Return fallback or raise
            if self.config.fallback_enabled:
                return await self._get_fallback_response(request_id, str(e))
            else:
                raise
    
    async def _should_block_request(self) -> bool:
        """Check if request should be blocked"""
        current_time = datetime.utcnow()
        
        if self.state == CircuitState.CLOSED:
            return False
        
        elif self.state == CircuitState.OPEN:
            # Check if we should transition to half-open
            if self.next_attempt_time and current_time >= self.next_attempt_time:
                await self._transition_to_half_open()
                return False
            return True
        
        elif self.state == CircuitState.HALF_OPEN:
            # Allow limited requests in half-open state
            return self.half_open_requests >= self.config.half_open_max_requests
        
        return False
    
    async def _execute_request(self, request_func: Callable, request_id: str, *args, **kwargs) -> Any:
        """Execute the actual request"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_requests += 1
        
        # Set timeout
        try:
            result = await asyncio.wait_for(
                request_func(*args, **kwargs),
                timeout=self.config.timeout_duration_ms / 1000
            )
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Request timeout after {self.config.timeout_duration_ms}ms")
    
    async def _record_success(self, request_id: str, response_time_ms: float):
        """Record successful request"""
        result = RequestResult(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            success=True,
            response_time_ms=response_time_ms
        )
        
        self.request_history.append(result)
        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        
        # Update response time metrics
        if self.metrics.successful_requests == 1:
            self.metrics.average_response_time_ms = response_time_ms
        else:
            self.metrics.average_response_time_ms = (
                (self.metrics.average_response_time_ms * (self.metrics.successful_requests - 1) + 
                 response_time_ms) / self.metrics.successful_requests
            )
        
        # Reset failure count on success
        self.failure_count = 0
        
        # Handle half-open state
        if self.state == CircuitState.HALF_OPEN:
            # Check if we have enough successful requests to close circuit
            recent_successes = sum(1 for r in self.request_history 
                                 if r.timestamp > datetime.utcnow() - timedelta(seconds=30) and r.success)
            
            if recent_successes >= self.config.half_open_max_requests:
                await self._transition_to_closed()
    
    async def _record_failure(self, request_id: str, response_time_ms: float, error_message: str):
        """Record failed request"""
        # Determine failure type
        failure_type = FailureType.ERROR_RESPONSE
        if "timeout" in error_message.lower():
            failure_type = FailureType.TIMEOUT
        elif "connection" in error_message.lower():
            failure_type = FailureType.CONNECTION_ERROR
        
        result = RequestResult(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            success=False,
            response_time_ms=response_time_ms,
            failure_type=failure_type,
            error_message=error_message
        )
        
        self.request_history.append(result)
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        # Check if circuit should open
        await self._check_circuit_opening_conditions()
    
    async def _check_circuit_opening_conditions(self):
        """Check if circuit should open based on failure patterns"""
        if self.state == CircuitState.OPEN:
            return
        
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=self.config.monitoring_window_seconds)
        
        # Get recent requests within monitoring window
        recent_requests = [r for r in self.request_history if r.timestamp >= window_start]
        
        if len(recent_requests) < self.config.min_requests_threshold:
            return  # Not enough requests to make decision
        
        # Apply strategy-specific logic
        should_open = False
        
        if self.config.strategy == CircuitBreakerStrategy.COUNT_BASED:
            should_open = self.failure_count >= self.config.failure_threshold
        
        elif self.config.strategy == CircuitBreakerStrategy.PERCENTAGE_BASED:
            failed_requests = [r for r in recent_requests if not r.success]
            failure_rate = (len(failed_requests) / len(recent_requests)) * 100
            should_open = failure_rate >= self.config.failure_rate_threshold
        
        elif self.config.strategy == CircuitBreakerStrategy.TIME_BASED:
            # Check failure rate over time windows
            failure_rate = self._calculate_time_based_failure_rate(recent_requests)
            should_open = failure_rate >= self.config.failure_rate_threshold
        
        elif self.config.strategy == CircuitBreakerStrategy.ADAPTIVE:
            # Adaptive threshold based on historical patterns
            should_open = await self._adaptive_threshold_check(recent_requests)
        
        if should_open:
            await self._transition_to_open()
    
    def _calculate_time_based_failure_rate(self, recent_requests: List[RequestResult]) -> float:
        """Calculate failure rate for time-based strategy"""
        if not recent_requests:
            return 0.0
        
        # Group requests by time buckets (e.g., 10-second intervals)
        bucket_size = 10  # seconds
        buckets = defaultdict(list)
        
        for request in recent_requests:
            bucket_time = int(request.timestamp.timestamp() // bucket_size) * bucket_size
            buckets[bucket_time].append(request)
        
        # Calculate failure rate across buckets
        total_buckets = len(buckets)
        failed_buckets = 0
        
        for bucket_requests in buckets.values():
            bucket_failures = sum(1 for r in bucket_requests if not r.success)
            if bucket_failures / len(bucket_requests) > 0.3:  # 30% failure in bucket
                failed_buckets += 1
        
        return (failed_buckets / total_buckets) * 100 if total_buckets > 0 else 0.0
    
    async def _adaptive_threshold_check(self, recent_requests: List[RequestResult]) -> bool:
        """Adaptive threshold check based on patterns"""
        if not recent_requests:
            return False
        
        # Calculate baseline failure rate from historical data
        historical_failure_rate = self._get_historical_failure_rate()
        
        # Current failure rate
        current_failures = sum(1 for r in recent_requests if not r.success)
        current_failure_rate = (current_failures / len(recent_requests)) * 100
        
        # Adaptive threshold: open if current rate is significantly higher than baseline
        adaptive_threshold = max(historical_failure_rate * 2, 10.0)  # At least 10%
        
        return current_failure_rate > adaptive_threshold
    
    def _get_historical_failure_rate(self) -> float:
        """Get historical failure rate for adaptive threshold"""
        # Calculate from longer history (last 1000 requests or 1 hour)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        historical_requests = [r for r in self.request_history if r.timestamp >= cutoff_time]
        
        if not historical_requests:
            return 5.0  # Default baseline
        
        failures = sum(1 for r in historical_requests if not r.success)
        return (failures / len(historical_requests)) * 100
    
    async def _transition_to_open(self):
        """Transition circuit to open state"""
        if self.state == CircuitState.OPEN:
            return
        
        self.state = CircuitState.OPEN
        self.next_attempt_time = datetime.utcnow() + timedelta(seconds=self.config.open_timeout_seconds)
        self.metrics.state_changes += 1
        self.last_state_change = datetime.utcnow()
        
        logger.warning(f"Circuit breaker opened: {self.config.name}")
        
        # Creator Economy impact analysis
        await self._analyze_creator_impact("circuit_opened")
    
    async def _transition_to_half_open(self):
        """Transition circuit to half-open state"""
        self.state = CircuitState.HALF_OPEN
        self.half_open_requests = 0
        self.metrics.state_changes += 1
        
        # Update time tracking
        if self.last_state_change:
            time_in_open = (datetime.utcnow() - self.last_state_change).total_seconds()
            self.metrics.time_in_open_state_seconds += time_in_open
        
        self.last_state_change = datetime.utcnow()
        
        logger.info(f"Circuit breaker half-opened: {self.config.name}")
    
    async def _transition_to_closed(self):
        """Transition circuit to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.next_attempt_time = None
        self.metrics.state_changes += 1
        
        # Update time tracking
        if self.last_state_change:
            time_in_half_open = (datetime.utcnow() - self.last_state_change).total_seconds()
            self.metrics.time_in_half_open_state_seconds += time_in_half_open
        
        self.last_state_change = datetime.utcnow()
        
        logger.info(f"Circuit breaker closed: {self.config.name}")
        
        # Creator Economy impact analysis
        await self._analyze_creator_impact("circuit_closed")
    
    async def _handle_blocked_request(self, request_id: str) -> Any:
        """Handle blocked request when circuit is open"""
        self.metrics.blocked_requests += 1
        
        # Track Creator Economy impact
        if self.config.creator_impact_level in ["critical", "high"]:
            self.metrics.creator_requests_blocked += 1
        
        if self.config.revenue_protection_mode:
            self.metrics.revenue_requests_blocked += 1
        
        logger.debug(f"Request blocked by circuit breaker: {request_id}")
        
        if self.config.fallback_enabled:
            return await self._get_fallback_response(request_id, "Circuit breaker open")
        else:
            raise Exception(f"Circuit breaker open for service: {self.config.service_name}")
    
    async def _get_fallback_response(self, request_id: str, error_message: str) -> Any:
        """Get fallback response when circuit is open or request fails"""
        self.metrics.fallback_responses_served += 1
        
        # Return configured fallback response
        if self.config.fallback_response:
            return self.config.fallback_response
        
        # Creator Economy specific fallbacks
        if self.config.creator_impact_level == "critical":
            return {
                "status": "degraded",
                "message": "Service temporarily unavailable, using cached data",
                "fallback": True,
                "request_id": request_id
            }
        else:
            return {
                "status": "error",
                "message": error_message,
                "fallback": True,
                "request_id": request_id
            }
    
    async def _analyze_creator_impact(self, event_type: str):
        """Analyze impact on Creator Economy"""
        try:
            impact_score = 0.0
            
            if self.config.creator_impact_level == "critical":
                impact_score = 0.8
            elif self.config.creator_impact_level == "high":
                impact_score = 0.6
            elif self.config.creator_impact_level == "medium":
                impact_score = 0.4
            else:
                impact_score = 0.2
            
            # Adjust based on event type
            if event_type == "circuit_opened":
                self.metrics.creator_satisfaction_impact -= impact_score
            elif event_type == "circuit_closed":
                self.metrics.creator_satisfaction_impact += impact_score * 0.5  # Partial recovery
            
            logger.info(f"Creator impact analysis for {self.config.name}: {event_type} -> {impact_score}")
            
        except Exception as e:
            logger.error(f"Failed to analyze creator impact: {str(e)}")
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "circuit_id": self.config.circuit_id,
            "name": self.config.name,
            "service_name": self.config.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "next_attempt_time": self.next_attempt_time.isoformat() if self.next_attempt_time else None,
            "half_open_requests": self.half_open_requests,
            "metrics": self.metrics.__dict__,
            "creator_impact_level": self.config.creator_impact_level,
            "fallback_enabled": self.config.fallback_enabled
        }


class CircuitBreakerManager:
    """
    ⚡ Enterprise Circuit Breaker Manager for Creator Economy
    
    Gestionnaire circuit breakers enterprise avec:
    - Service failure isolation
    - Creator experience protection
    - Cascade failure prevention
    - Self-healing system integration
    - Hystrix/Resilience4j integration
    
    Features:
    - Multi-strategy circuit breaker implementations
    - Creator-aware failure isolation and fallback responses
    - Real-time circuit state monitoring and alerting
    - Adaptive threshold management based on service patterns
    - Revenue protection with intelligent fallback mechanisms
    """
    
    def __init__(self):
        self.manager_id = str(uuid.uuid4())
        self.circuits: Dict[str, CircuitBreaker] = {}
        self.global_metrics = {
            "total_circuits": 0,
            "open_circuits": 0,
            "half_open_circuits": 0,
            "closed_circuits": 0,
            "total_blocked_requests": 0,
            "total_fallback_responses": 0,
            "cascade_failures_prevented": 0
        }
        
        # Monitoring and alerting
        self.monitoring_active = False
        self.alert_thresholds = {
            "max_open_circuits": 5,
            "max_blocked_requests_per_minute": 1000,
            "cascade_failure_threshold": 3
        }
        
        # Creator Economy specific
        self.creator_service_mapping: Dict[str, str] = {}  # service -> creator impact level
        self.revenue_critical_services: List[str] = []
        
        logger.info(f"Circuit Breaker Manager initialized: {self.manager_id}")
    
    async def initialize(self) -> bool:
        """
        Initialize circuit breaker manager
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Circuit Breaker Manager...")
            
            # Setup default circuit breakers
            await self._setup_default_circuits()
            
            # Initialize Creator Economy mappings
            await self._setup_creator_service_mappings()
            
            # Start monitoring
            await self._start_monitoring()
            
            logger.info("Circuit Breaker Manager successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize circuit breaker manager: {str(e)}")
            return False
    
    async def _setup_default_circuits(self):
        """Setup default circuit breakers for key services"""
        
        # Creator Dashboard API
        dashboard_config = CircuitBreakerConfig(
            circuit_id="creator_dashboard_api",
            name="Creator Dashboard API Circuit",
            service_name="creator_dashboard_api",
            strategy=CircuitBreakerStrategy.PERCENTAGE_BASED,
            failure_threshold=3,
            failure_rate_threshold=30.0,
            timeout_duration_ms=3000,
            open_timeout_seconds=30,
            creator_impact_level="critical",
            fallback_enabled=True,
            fallback_response={
                "status": "degraded",
                "message": "Dashboard temporarily using cached data",
                "cached": True
            },
            preserve_creator_data=True
        )
        
        # Payment Processing Service
        payment_config = CircuitBreakerConfig(
            circuit_id="payment_processor",
            name="Payment Processing Circuit",
            service_name="payment_processor",
            strategy=CircuitBreakerStrategy.COUNT_BASED,
            failure_threshold=2,  # Very sensitive for payments
            timeout_duration_ms=5000,
            open_timeout_seconds=60,
            creator_impact_level="critical",
            fallback_enabled=True,
            fallback_response={
                "status": "queued",
                "message": "Payment queued for processing",
                "queued": True
            },
            revenue_protection_mode=True
        )
        
        # Content Processing Service
        content_config = CircuitBreakerConfig(
            circuit_id="content_processor",
            name="Content Processing Circuit",
            service_name="content_processor",
            strategy=CircuitBreakerStrategy.ADAPTIVE,
            failure_threshold=5,
            failure_rate_threshold=40.0,
            timeout_duration_ms=10000,  # Content processing can take longer
            open_timeout_seconds=120,
            creator_impact_level="high",
            fallback_enabled=True,
            fallback_response={
                "status": "queued",
                "message": "Content queued for processing",
                "estimated_delay_minutes": 15
            }
        )
        
        # Analytics API
        analytics_config = CircuitBreakerConfig(
            circuit_id="analytics_api",
            name="Analytics API Circuit",
            service_name="analytics_api",
            strategy=CircuitBreakerStrategy.TIME_BASED,
            failure_rate_threshold=25.0,
            timeout_duration_ms=2000,
            open_timeout_seconds=45,
            creator_impact_level="medium",
            fallback_enabled=True,
            fallback_response={
                "status": "cached",
                "message": "Showing cached analytics data",
                "data_age_hours": 1
            }
        )
        
        # Notification Service
        notification_config = CircuitBreakerConfig(
            circuit_id="notification_service",
            name="Notification Service Circuit",
            service_name="notification_service",
            strategy=CircuitBreakerStrategy.PERCENTAGE_BASED,
            failure_rate_threshold=20.0,
            timeout_duration_ms=1000,
            open_timeout_seconds=30,
            creator_impact_level="low",
            fallback_enabled=True,
            fallback_response={
                "status": "queued",
                "message": "Notification queued for delivery"
            }
        )
        
        # Create circuit breakers
        configs = [dashboard_config, payment_config, content_config, analytics_config, notification_config]
        
        for config in configs:
            circuit = CircuitBreaker(config)
            self.circuits[config.circuit_id] = circuit
            
            if config.revenue_protection_mode:
                self.revenue_critical_services.append(config.service_name)
        
        self.global_metrics["total_circuits"] = len(self.circuits)
        
        logger.info(f"Setup {len(configs)} default circuit breakers")
    
    async def _setup_creator_service_mappings(self):
        """Setup Creator Economy service impact mappings"""
        self.creator_service_mapping = {
            "creator_dashboard_api": "critical",
            "payment_processor": "critical",
            "content_processor": "high",
            "analytics_api": "medium",
            "notification_service": "low",
            "social_integration": "medium",
            "audience_engagement": "high"
        }
        
        logger.info("Creator service mappings configured")
    
    async def _start_monitoring(self):
        """Start monitoring circuit breakers"""
        self.monitoring_active = True
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._cascade_failure_detection_loop())
        
        logger.info("Circuit breaker monitoring started")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Update global metrics
                await self._update_global_metrics()
                
                # Check alert conditions
                await self._check_alert_conditions()
                
                # Update circuit states
                await self._update_circuit_states()
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Circuit breaker monitoring error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _health_check_loop(self):
        """Health check loop for individual circuits"""
        while self.monitoring_active:
            try:
                for circuit_id, circuit in self.circuits.items():
                    # Perform health assessment
                    await self._assess_circuit_health(circuit)
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error(f"Circuit health check error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cascade_failure_detection_loop(self):
        """Detect and prevent cascade failures"""
        while self.monitoring_active:
            try:
                await self._detect_cascade_failures()
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"Cascade failure detection error: {str(e)}")
                await asyncio.sleep(45)
    
    async def _update_global_metrics(self):
        """Update global circuit breaker metrics"""
        try:
            open_count = 0
            half_open_count = 0
            closed_count = 0
            total_blocked = 0
            total_fallbacks = 0
            
            for circuit in self.circuits.values():
                if circuit.state == CircuitState.OPEN:
                    open_count += 1
                elif circuit.state == CircuitState.HALF_OPEN:
                    half_open_count += 1
                else:
                    closed_count += 1
                
                total_blocked += circuit.metrics.blocked_requests
                total_fallbacks += circuit.metrics.fallback_responses_served
            
            self.global_metrics.update({
                "open_circuits": open_count,
                "half_open_circuits": half_open_count,
                "closed_circuits": closed_count,
                "total_blocked_requests": total_blocked,
                "total_fallback_responses": total_fallbacks
            })
            
        except Exception as e:
            logger.error(f"Failed to update global metrics: {str(e)}")
    
    async def _check_alert_conditions(self):
        """Check for alert conditions"""
        try:
            # Too many open circuits
            if self.global_metrics["open_circuits"] > self.alert_thresholds["max_open_circuits"]:
                logger.critical(f"Alert: {self.global_metrics['open_circuits']} circuits open (threshold: {self.alert_thresholds['max_open_circuits']})")
            
            # High rate of blocked requests
            blocked_per_minute = await self._calculate_blocked_requests_per_minute()
            if blocked_per_minute > self.alert_thresholds["max_blocked_requests_per_minute"]:
                logger.critical(f"Alert: {blocked_per_minute} requests blocked per minute (threshold: {self.alert_thresholds['max_blocked_requests_per_minute']})")
            
        except Exception as e:
            logger.error(f"Failed to check alert conditions: {str(e)}")
    
    async def _calculate_blocked_requests_per_minute(self) -> int:
        """Calculate blocked requests per minute across all circuits"""
        try:
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
            total_blocked = 0
            
            for circuit in self.circuits.values():
                recent_requests = [
                    r for r in circuit.request_history 
                    if r.timestamp >= one_minute_ago and not r.success
                ]
                total_blocked += len(recent_requests)
            
            return total_blocked
            
        except Exception as e:
            logger.error(f"Failed to calculate blocked requests per minute: {str(e)}")
            return 0
    
    async def _update_circuit_states(self):
        """Update circuit states and perform maintenance"""
        try:
            for circuit in self.circuits.values():
                # Clean old request history
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                circuit.request_history = deque(
                    [r for r in circuit.request_history if r.timestamp >= cutoff_time],
                    maxlen=1000
                )
                
        except Exception as e:
            logger.error(f"Failed to update circuit states: {str(e)}")
    
    async def _assess_circuit_health(self, circuit: CircuitBreaker):
        """Assess health of individual circuit"""
        try:
            current_time = datetime.utcnow()
            
            # Calculate recent metrics
            recent_cutoff = current_time - timedelta(minutes=5)
            recent_requests = [r for r in circuit.request_history if r.timestamp >= recent_cutoff]
            
            if recent_requests:
                success_rate = sum(1 for r in recent_requests if r.success) / len(recent_requests) * 100
                
                # Log health status
                if success_rate < 50:
                    logger.warning(f"Circuit {circuit.config.name} health degraded: {success_rate:.1f}% success rate")
                elif success_rate > 95 and circuit.state == CircuitState.OPEN:
                    logger.info(f"Circuit {circuit.config.name} may be ready to recover: {success_rate:.1f}% success rate")
            
        except Exception as e:
            logger.error(f"Failed to assess circuit health: {str(e)}")
    
    async def _detect_cascade_failures(self):
        """Detect potential cascade failures"""
        try:
            current_time = datetime.utcnow()
            recent_cutoff = current_time - timedelta(minutes=5)
            
            # Count circuits that opened recently
            recently_opened = 0
            for circuit in self.circuits.values():
                if (circuit.state == CircuitState.OPEN and 
                    circuit.last_state_change >= recent_cutoff):
                    recently_opened += 1
            
            # Check for cascade failure pattern
            if recently_opened >= self.alert_thresholds["cascade_failure_threshold"]:
                logger.critical(f"Cascade failure detected: {recently_opened} circuits opened recently")
                self.global_metrics["cascade_failures_prevented"] += 1
                
                # Implement cascade failure mitigation
                await self._mitigate_cascade_failure()
            
        except Exception as e:
            logger.error(f"Failed to detect cascade failures: {str(e)}")
    
    async def _mitigate_cascade_failure(self):
        """Mitigate cascade failure by adjusting circuit parameters"""
        try:
            logger.info("Implementing cascade failure mitigation")
            
            # Temporarily increase thresholds for non-critical circuits
            for circuit in self.circuits.values():
                if circuit.config.creator_impact_level in ["low", "medium"]:
                    # Increase failure threshold temporarily
                    original_threshold = circuit.config.failure_threshold
                    circuit.config.failure_threshold = min(original_threshold * 2, 20)
                    
                    # Extend timeout
                    circuit.config.open_timeout_seconds = min(circuit.config.open_timeout_seconds * 1.5, 300)
                    
                    logger.info(f"Adjusted thresholds for circuit {circuit.config.name}")
            
            # Schedule threshold reset
            asyncio.create_task(self._reset_cascade_mitigation_after_delay(300))  # 5 minutes
            
        except Exception as e:
            logger.error(f"Failed to mitigate cascade failure: {str(e)}")
    
    async def _reset_cascade_mitigation_after_delay(self, delay_seconds: int):
        """Reset cascade mitigation settings after delay"""
        try:
            await asyncio.sleep(delay_seconds)
            
            # Reset to original thresholds
            for circuit in self.circuits.values():
                if circuit.config.creator_impact_level in ["low", "medium"]:
                    # Reset thresholds to more restrictive values
                    circuit.config.failure_threshold = max(circuit.config.failure_threshold // 2, 3)
                    circuit.config.open_timeout_seconds = max(circuit.config.open_timeout_seconds // 1.5, 30)
            
            logger.info("Cascade mitigation settings reset to normal")
            
        except Exception as e:
            logger.error(f"Failed to reset cascade mitigation: {str(e)}")
    
    async def create_circuit_breaker(self, config: CircuitBreakerConfig) -> str:
        """
        Create a new circuit breaker
        
        Args:
            config: Circuit breaker configuration
            
        Returns:
            str: Circuit ID
        """
        try:
            if config.circuit_id in self.circuits:
                raise ValueError(f"Circuit {config.circuit_id} already exists")
            
            circuit = CircuitBreaker(config)
            self.circuits[config.circuit_id] = circuit
            self.global_metrics["total_circuits"] += 1
            
            logger.info(f"Created circuit breaker: {config.name}")
            return config.circuit_id
            
        except Exception as e:
            logger.error(f"Failed to create circuit breaker: {str(e)}")
            raise
    
    async def execute_with_circuit_breaker(
        self, 
        circuit_id: str, 
        request_func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """
        Execute a function through a circuit breaker
        
        Args:
            circuit_id: Circuit breaker ID
            request_func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result or fallback response
        """
        try:
            if circuit_id not in self.circuits:
                raise ValueError(f"Circuit {circuit_id} not found")
            
            circuit = self.circuits[circuit_id]
            return await circuit.call(request_func, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Failed to execute with circuit breaker {circuit_id}: {str(e)}")
            raise
    
    async def force_open_circuit(self, circuit_id: str, reason: str = "Manual override"):
        """
        Manually force a circuit to open
        
        Args:
            circuit_id: Circuit to open
            reason: Reason for opening
        """
        try:
            if circuit_id not in self.circuits:
                raise ValueError(f"Circuit {circuit_id} not found")
            
            circuit = self.circuits[circuit_id]
            await circuit._transition_to_open()
            
            logger.warning(f"Manually opened circuit {circuit_id}: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to force open circuit {circuit_id}: {str(e)}")
            raise
    
    async def force_close_circuit(self, circuit_id: str, reason: str = "Manual override"):
        """
        Manually force a circuit to close
        
        Args:
            circuit_id: Circuit to close
            reason: Reason for closing
        """
        try:
            if circuit_id not in self.circuits:
                raise ValueError(f"Circuit {circuit_id} not found")
            
            circuit = self.circuits[circuit_id]
            await circuit._transition_to_closed()
            
            logger.info(f"Manually closed circuit {circuit_id}: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to force close circuit {circuit_id}: {str(e)}")
            raise
    
    async def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker status"""
        return {
            "manager_id": self.manager_id,
            "monitoring_active": self.monitoring_active,
            "global_metrics": self.global_metrics,
            "circuits": {
                circuit_id: circuit.get_current_state()
                for circuit_id, circuit in self.circuits.items()
            },
            "creator_service_mapping": self.creator_service_mapping,
            "revenue_critical_services": self.revenue_critical_services,
            "alert_thresholds": self.alert_thresholds,
            "cascade_failures_prevented": self.global_metrics["cascade_failures_prevented"]
        }
    
    async def health_check(self) -> bool:
        """Health check for circuit breaker manager"""
        try:
            # Check if monitoring is active
            if not self.monitoring_active:
                return False
            
            # Check if too many circuits are open
            if self.global_metrics["open_circuits"] > len(self.circuits) * 0.5:
                return False
            
            # Check if critical Creator services are protected
            critical_circuits_open = 0
            for circuit in self.circuits.values():
                if (circuit.config.creator_impact_level == "critical" and 
                    circuit.state == CircuitState.OPEN):
                    critical_circuits_open += 1
            
            if critical_circuits_open > 2:  # Too many critical circuits open
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Circuit breaker manager health check failed: {str(e)}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown of circuit breaker manager"""
        try:
            logger.info("Shutting down Circuit Breaker Manager...")
            
            # Stop monitoring
            self.monitoring_active = False
            
            # Reset all circuits to closed state (if safe)
            for circuit_id, circuit in self.circuits.items():
                if circuit.state != CircuitState.CLOSED:
                    logger.info(f"Resetting circuit {circuit_id} to closed state")
                    await circuit._transition_to_closed()
            
            logger.info("Circuit Breaker Manager shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during circuit breaker manager shutdown: {str(e)}")


# Factory function
def create_circuit_breaker_manager() -> CircuitBreakerManager:
    """Factory function to create circuit breaker manager"""
    return CircuitBreakerManager()


# Example usage
async def main():
    """Example usage of circuit breaker manager"""
    logging.basicConfig(level=logging.INFO)
    
    manager = create_circuit_breaker_manager()
    
    try:
        # Initialize
        await manager.initialize()
        
        # Example service function that sometimes fails
        async def example_service_call(should_fail: bool = False):
            await asyncio.sleep(0.1)  # Simulate network call
            if should_fail or random.random() < 0.3:  # 30% failure rate
                raise Exception("Service temporarily unavailable")
            return {"status": "success", "data": "Service response"}
        
        # Test circuit breaker with successful calls
        print("Testing successful calls...")
        for i in range(5):
            try:
                result = await manager.execute_with_circuit_breaker(
                    "creator_dashboard_api",
                    example_service_call,
                    should_fail=False
                )
                print(f"Call {i+1}: {result}")
            except Exception as e:
                print(f"Call {i+1} failed: {str(e)}")
            
            await asyncio.sleep(0.2)
        
        # Test circuit breaker with failing calls
        print("\nTesting failing calls to trigger circuit breaker...")
        for i in range(10):
            try:
                result = await manager.execute_with_circuit_breaker(
                    "creator_dashboard_api",
                    example_service_call,
                    should_fail=True
                )
                print(f"Fail call {i+1}: {result}")
            except Exception as e:
                print(f"Fail call {i+1} failed: {str(e)}")
            
            await asyncio.sleep(0.1)
        
        # Get status
        status = await manager.get_circuit_breaker_status()
        print(f"\nCircuit Breaker Status:")
        print(f"Total circuits: {status['global_metrics']['total_circuits']}")
        print(f"Open circuits: {status['global_metrics']['open_circuits']}")
        print(f"Blocked requests: {status['global_metrics']['total_blocked_requests']}")
        print(f"Fallback responses: {status['global_metrics']['total_fallback_responses']}")
        
        # Show individual circuit states
        for circuit_id, circuit_info in status['circuits'].items():
            print(f"\nCircuit {circuit_id}:")
            print(f"  State: {circuit_info['state']}")
            print(f"  Failure count: {circuit_info['failure_count']}")
            print(f"  Total requests: {circuit_info['metrics']['total_requests']}")
            print(f"  Success rate: {circuit_info['metrics']['successful_requests'] / max(1, circuit_info['metrics']['total_requests']) * 100:.1f}%")
        
        # Wait a bit then try again to see circuit recovery
        print("\nWaiting for circuit recovery...")
        await asyncio.sleep(35)  # Wait longer than open timeout
        
        # Test recovery
        print("Testing recovery...")
        for i in range(3):
            try:
                result = await manager.execute_with_circuit_breaker(
                    "creator_dashboard_api",
                    example_service_call,
                    should_fail=False
                )
                print(f"Recovery call {i+1}: {result}")
            except Exception as e:
                print(f"Recovery call {i+1} failed: {str(e)}")
            
            await asyncio.sleep(1)
        
        # Final status
        final_status = await manager.get_circuit_breaker_status()
        dashboard_circuit = final_status['circuits']['creator_dashboard_api']
        print(f"\nFinal circuit state: {dashboard_circuit['state']}")
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())