"""
Rate Limiting Integration - Enterprise Circuit Breakers
Advanced coordination between circuit breakers and rate limiting

This module provides intelligent coordination between circuit breakers and 
rate limiting systems, implementing adaptive rate limiting, backpressure
management, and coordinated failure prevention.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
            Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - PROTECTION FORTE
Cette implémentation est la propriété exclusive de Fahed Mlaiel.
Toute reproduction ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, deque
import math
import redis.asyncio as redis


logger = logging.getLogger(__name__)


class RateLimitingAlgorithm(Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"


class BackpressureLevel(Enum):
    """Backpressure severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CoordinationStrategy(Enum):
    """Coordination strategies between circuit breakers and rate limiting"""
    INDEPENDENT = "independent"          # No coordination
    COOPERATIVE = "cooperative"          # Share information
    HIERARCHICAL = "hierarchical"        # Rate limiting controls circuit breakers
    CIRCUIT_PRIORITY = "circuit_priority" # Circuit breakers control rate limiting
    ADAPTIVE_COORDINATION = "adaptive_coordination"  # Dynamic coordination


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    service_name: str
    algorithm: RateLimitingAlgorithm = RateLimitingAlgorithm.ADAPTIVE
    base_rate_limit: int = 100  # requests per time window
    time_window_seconds: int = 60
    burst_capacity: int = 150
    circuit_integration: bool = True
    adaptive_factors: Dict[str, float] = field(default_factory=lambda: {
        'circuit_open_factor': 0.1,     # Reduce rate limit to 10% when circuit is open
        'circuit_half_open_factor': 0.5,  # Reduce rate limit to 50% when half-open
        'load_factor': 1.2,             # Increase rate limit by 20% under high load
        'error_factor': 0.8             # Reduce rate limit by 20% when error rate is high
    })
    backpressure_thresholds: Dict[BackpressureLevel, float] = field(default_factory=lambda: {
        BackpressureLevel.LOW: 0.7,
        BackpressureLevel.MEDIUM: 0.8,
        BackpressureLevel.HIGH: 0.9,
        BackpressureLevel.CRITICAL: 0.95
    })
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitMetrics:
    """Rate limiting performance metrics"""
    total_requests: int = 0
    allowed_requests: int = 0
    rejected_requests: int = 0
    current_rate: float = 0.0
    current_limit: int = 0
    utilization: float = 0.0
    backpressure_level: BackpressureLevel = BackpressureLevel.NONE
    circuit_state_factor: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class BackpressureSignal:
    """Backpressure signal data"""
    signal_id: str
    source_service: str
    target_service: str
    level: BackpressureLevel
    rate_reduction: float
    duration_seconds: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class TokenBucketRateLimiter:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = float(config.base_rate_limit)
        self.last_refill = time.time()
        self.max_tokens = config.burst_capacity
        self.refill_rate = config.base_rate_limit / config.time_window_seconds
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def acquire_token(self, tokens_needed: int = 1) -> bool:
        """Acquire tokens from bucket"""
        async with self.lock:
            now = time.time()
            
            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            tokens_to_add = elapsed * self.refill_rate
            self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            
            return False
    
    def update_rate_limit(self, new_limit: int):
        """Update rate limit dynamically"""
        self.config.base_rate_limit = new_limit
        self.refill_rate = new_limit / self.config.time_window_seconds
        self.max_tokens = max(new_limit, self.config.burst_capacity)


class SlidingWindowRateLimiter:
    """Sliding window rate limiter implementation"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests = deque()
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def acquire_token(self, tokens_needed: int = 1) -> bool:
        """Check if request is within rate limit"""
        async with self.lock:
            now = time.time()
            window_start = now - self.config.time_window_seconds
            
            # Remove old requests outside the window
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
            
            # Check if we can accept new requests
            if len(self.requests) + tokens_needed <= self.config.base_rate_limit:
                for _ in range(tokens_needed):
                    self.requests.append(now)
                return True
            
            return False
    
    def get_current_rate(self) -> float:
        """Get current request rate"""
        now = time.time()
        window_start = now - self.config.time_window_seconds
        
        # Count requests in current window
        current_requests = sum(1 for req_time in self.requests if req_time >= window_start)
        return current_requests / self.config.time_window_seconds


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on system conditions"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.base_limiter = TokenBucketRateLimiter(config)
        self.circuit_state = "CLOSED"
        self.system_load = 0.0
        self.error_rate = 0.0
        self.current_multiplier = 1.0
        self.adaptation_history = deque(maxlen=100)
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def acquire_token(self, tokens_needed: int = 1) -> bool:
        """Acquire token with adaptive rate limiting"""
        # Update current rate limit based on conditions
        await self._update_adaptive_rate_limit()
        
        return await self.base_limiter.acquire_token(tokens_needed)
    
    async def _update_adaptive_rate_limit(self):
        """Update rate limit based on system conditions"""
        async with self.lock:
            multiplier = 1.0
            
            # Circuit breaker state adjustment
            if self.circuit_state == "OPEN":
                multiplier *= self.config.adaptive_factors['circuit_open_factor']
            elif self.circuit_state == "HALF_OPEN":
                multiplier *= self.config.adaptive_factors['circuit_half_open_factor']
            
            # System load adjustment
            if self.system_load > 0.8:
                multiplier *= (2.0 - self.system_load)  # Reduce as load increases
            elif self.system_load < 0.5:
                multiplier *= self.config.adaptive_factors['load_factor']
            
            # Error rate adjustment
            if self.error_rate > 0.1:  # More than 10% error rate
                multiplier *= self.config.adaptive_factors['error_factor']
            
            # Smooth the adjustment
            if self.adaptation_history:
                recent_multipliers = list(self.adaptation_history)[-10:]
                smoothed_multiplier = statistics.mean(recent_multipliers + [multiplier])
            else:
                smoothed_multiplier = multiplier
            
            self.current_multiplier = smoothed_multiplier
            self.adaptation_history.append(smoothed_multiplier)
            
            # Apply the new rate limit
            new_limit = int(self.config.base_rate_limit * smoothed_multiplier)
            self.base_limiter.update_rate_limit(max(1, new_limit))  # Ensure at least 1 request is allowed
    
    def update_circuit_state(self, state: str):
        """Update circuit breaker state"""
        self.circuit_state = state
        self.logger.debug(f"🔄 Circuit state updated to {state} for {self.config.service_name}")
    
    def update_system_metrics(self, load: float, error_rate: float):
        """Update system metrics for adaptation"""
        self.system_load = max(0.0, min(1.0, load))
        self.error_rate = max(0.0, min(1.0, error_rate))


class BackpressureManager:
    """Backpressure signal management"""
    
    def __init__(self):
        self.active_signals: Dict[str, BackpressureSignal] = {}
        self.signal_handlers: Dict[BackpressureLevel, List[Callable]] = defaultdict(list)
        self.signal_history = deque(maxlen=1000)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def emit_backpressure_signal(self, signal: BackpressureSignal):
        """Emit backpressure signal"""
        self.active_signals[signal.signal_id] = signal
        self.signal_history.append(signal)
        
        # Trigger handlers for this level
        handlers = self.signal_handlers.get(signal.level, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(signal)
                else:
                    handler(signal)
            except Exception as e:
                self.logger.error(f"❌ Error in backpressure handler: {e}")
        
        self.logger.info(f"📡 Backpressure signal emitted: {signal.level.value} from {signal.source_service} to {signal.target_service}")
    
    async def clear_backpressure_signal(self, signal_id: str):
        """Clear backpressure signal"""
        if signal_id in self.active_signals:
            signal = self.active_signals.pop(signal_id)
            self.logger.info(f"✅ Backpressure signal cleared: {signal_id}")
    
    def register_handler(self, level: BackpressureLevel, handler: Callable):
        """Register backpressure signal handler"""
        self.signal_handlers[level].append(handler)
        self.logger.info(f"📝 Registered backpressure handler for {level.value}")
    
    def get_active_signals_for_service(self, service_name: str) -> List[BackpressureSignal]:
        """Get active backpressure signals for service"""
        return [signal for signal in self.active_signals.values() 
                if signal.target_service == service_name]


class RateLimitingIntegration:
    """
    Integration between circuit breakers and rate limiting systems.
    Implements coordinated failure prevention and adaptive rate limiting.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize rate limiting integration"""
        self.rate_limiters: Dict[str, Union[TokenBucketRateLimiter, SlidingWindowRateLimiter, AdaptiveRateLimiter]] = {}
        self.service_configs: Dict[str, RateLimitConfig] = {}
        self.metrics: Dict[str, RateLimitMetrics] = defaultdict(RateLimitMetrics)
        self.coordination_strategy = CoordinationStrategy.ADAPTIVE_COORDINATION
        self.backpressure_manager = BackpressureManager()
        self.circuit_breaker_states: Dict[str, str] = {}
        self.redis_client = redis_client
        self.monitoring_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Register default backpressure handlers
        self._register_default_handlers()
        
        self.logger.info("🚦 Rate Limiting Integration initialized - Enterprise coordination ready")
    
    def _register_default_handlers(self):
        """Register default backpressure handlers"""
        self.backpressure_manager.register_handler(
            BackpressureLevel.HIGH, 
            self._handle_high_backpressure
        )
        self.backpressure_manager.register_handler(
            BackpressureLevel.CRITICAL, 
            self._handle_critical_backpressure
        )
    
    async def coordinate_circuit_and_rate_limits(self, coordination_config: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate circuit breakers and rate limiting intelligently"""
        try:
            service_name = coordination_config.get('service_name')
            circuit_state = coordination_config.get('circuit_state', 'CLOSED')
            system_metrics = coordination_config.get('system_metrics', {})
            
            if not service_name:
                raise ValueError("Service name required for coordination")
            
            # Update circuit breaker state
            self.circuit_breaker_states[service_name] = circuit_state
            
            # Get or create rate limiter
            if service_name not in self.rate_limiters:
                config = RateLimitConfig(
                    service_name=service_name,
                    base_rate_limit=coordination_config.get('base_rate_limit', 100),
                    time_window_seconds=coordination_config.get('time_window', 60),
                    burst_capacity=coordination_config.get('burst_capacity', 150)
                )
                await self._create_rate_limiter(service_name, config)
            
            rate_limiter = self.rate_limiters[service_name]
            
            # Apply coordination strategy
            coordination_result = await self._apply_coordination_strategy(
                service_name, circuit_state, system_metrics
            )
            
            # Update metrics
            await self._update_coordination_metrics(service_name, coordination_result)
            
            self.logger.info(f"🤝 Coordination applied for {service_name}: {coordination_result}")
            return coordination_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to coordinate circuit and rate limits: {e}")
            raise
    
    async def _create_rate_limiter(self, service_name: str, config: RateLimitConfig):
        """Create appropriate rate limiter based on configuration"""
        if config.algorithm == RateLimitingAlgorithm.TOKEN_BUCKET:
            self.rate_limiters[service_name] = TokenBucketRateLimiter(config)
        elif config.algorithm == RateLimitingAlgorithm.SLIDING_WINDOW:
            self.rate_limiters[service_name] = SlidingWindowRateLimiter(config)
        elif config.algorithm == RateLimitingAlgorithm.ADAPTIVE:
            self.rate_limiters[service_name] = AdaptiveRateLimiter(config)
        else:
            # Default to adaptive
            self.rate_limiters[service_name] = AdaptiveRateLimiter(config)
        
        self.service_configs[service_name] = config
    
    async def _apply_coordination_strategy(self, service_name: str, circuit_state: str, 
                                         system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Apply coordination strategy between circuit breakers and rate limiting"""
        rate_limiter = self.rate_limiters[service_name]
        config = self.service_configs[service_name]
        
        if self.coordination_strategy == CoordinationStrategy.INDEPENDENT:
            return await self._independent_coordination(service_name)
        elif self.coordination_strategy == CoordinationStrategy.COOPERATIVE:
            return await self._cooperative_coordination(service_name, circuit_state, system_metrics)
        elif self.coordination_strategy == CoordinationStrategy.HIERARCHICAL:
            return await self._hierarchical_coordination(service_name, circuit_state, system_metrics)
        elif self.coordination_strategy == CoordinationStrategy.CIRCUIT_PRIORITY:
            return await self._circuit_priority_coordination(service_name, circuit_state, system_metrics)
        elif self.coordination_strategy == CoordinationStrategy.ADAPTIVE_COORDINATION:
            return await self._adaptive_coordination(service_name, circuit_state, system_metrics)
        else:
            return await self._adaptive_coordination(service_name, circuit_state, system_metrics)
    
    async def _independent_coordination(self, service_name: str) -> Dict[str, Any]:
        """Independent coordination - no interaction"""
        return {
            'strategy': 'independent',
            'adjustments': [],
            'rate_limit_change': 0
        }
    
    async def _cooperative_coordination(self, service_name: str, circuit_state: str, 
                                      system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Cooperative coordination - share information but maintain independence"""
        rate_limiter = self.rate_limiters[service_name]
        adjustments = []
        
        # Update adaptive rate limiter with circuit state
        if isinstance(rate_limiter, AdaptiveRateLimiter):
            rate_limiter.update_circuit_state(circuit_state)
            
            # Update system metrics
            load = system_metrics.get('cpu_usage', 0) / 100.0
            error_rate = system_metrics.get('error_rate', 0)
            rate_limiter.update_system_metrics(load, error_rate)
            
            adjustments.append('updated_adaptive_limiter')
        
        return {
            'strategy': 'cooperative',
            'adjustments': adjustments,
            'circuit_state_shared': circuit_state,
            'system_metrics_applied': bool(system_metrics)
        }
    
    async def _hierarchical_coordination(self, service_name: str, circuit_state: str, 
                                       system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Hierarchical coordination - rate limiting controls circuit breakers"""
        config = self.service_configs[service_name]
        metrics = self.metrics[service_name]
        adjustments = []
        
        # Rate limiter determines circuit breaker behavior
        if metrics.utilization > config.backpressure_thresholds[BackpressureLevel.HIGH]:
            # High utilization - suggest circuit breaker activation
            adjustments.append('suggest_circuit_breaker_activation')
            
            # Emit backpressure signal
            signal = BackpressureSignal(
                signal_id=str(uuid.uuid4()),
                source_service=f"{service_name}_rate_limiter",
                target_service=service_name,
                level=BackpressureLevel.HIGH,
                rate_reduction=0.5,
                duration_seconds=60,
                timestamp=datetime.now()
            )
            await self.backpressure_manager.emit_backpressure_signal(signal)
            adjustments.append('backpressure_signal_emitted')
        
        return {
            'strategy': 'hierarchical',
            'adjustments': adjustments,
            'rate_limiter_control': True
        }
    
    async def _circuit_priority_coordination(self, service_name: str, circuit_state: str, 
                                           system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Circuit priority coordination - circuit breakers control rate limiting"""
        rate_limiter = self.rate_limiters[service_name]
        config = self.service_configs[service_name]
        adjustments = []
        
        # Circuit breaker state determines rate limiting behavior
        if circuit_state == "OPEN":
            # Circuit is open - drastically reduce rate limit
            new_limit = int(config.base_rate_limit * config.adaptive_factors['circuit_open_factor'])
            rate_limiter.update_rate_limit(new_limit)
            adjustments.append(f'rate_limit_reduced_to_{new_limit}')
            
        elif circuit_state == "HALF_OPEN":
            # Circuit is half-open - moderately reduce rate limit
            new_limit = int(config.base_rate_limit * config.adaptive_factors['circuit_half_open_factor'])
            rate_limiter.update_rate_limit(new_limit)
            adjustments.append(f'rate_limit_reduced_to_{new_limit}')
            
        elif circuit_state == "CLOSED":
            # Circuit is closed - restore normal rate limit
            rate_limiter.update_rate_limit(config.base_rate_limit)
            adjustments.append(f'rate_limit_restored_to_{config.base_rate_limit}')
        
        return {
            'strategy': 'circuit_priority',
            'adjustments': adjustments,
            'circuit_breaker_control': True,
            'circuit_state': circuit_state
        }
    
    async def _adaptive_coordination(self, service_name: str, circuit_state: str, 
                                   system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptive coordination - dynamic coordination based on conditions"""
        # Combine multiple strategies based on current conditions
        error_rate = system_metrics.get('error_rate', 0)
        load = system_metrics.get('cpu_usage', 0) / 100.0
        
        adjustments = []
        
        # High error rate - prioritize circuit breaker control
        if error_rate > 0.2:
            result = await self._circuit_priority_coordination(service_name, circuit_state, system_metrics)
            adjustments.extend(result['adjustments'])
            adjustments.append('circuit_priority_due_to_high_error_rate')
        
        # High load - use hierarchical control
        elif load > 0.8:
            result = await self._hierarchical_coordination(service_name, circuit_state, system_metrics)
            adjustments.extend(result['adjustments'])
            adjustments.append('hierarchical_due_to_high_load')
        
        # Normal conditions - use cooperative
        else:
            result = await self._cooperative_coordination(service_name, circuit_state, system_metrics)
            adjustments.extend(result['adjustments'])
            adjustments.append('cooperative_under_normal_conditions')
        
        return {
            'strategy': 'adaptive',
            'adjustments': adjustments,
            'adaptive_decision': {
                'error_rate': error_rate,
                'load': load,
                'chosen_strategy': adjustments[-1] if adjustments else 'none'
            }
        }
    
    async def implement_adaptive_rate_limiting(self, traffic_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Implement adaptive rate limiting based on traffic patterns"""
        try:
            service_name = traffic_patterns.get('service_name')
            if not service_name:
                raise ValueError("Service name required for adaptive rate limiting")
            
            # Analyze traffic patterns
            pattern_analysis = await self._analyze_traffic_patterns(traffic_patterns)
            
            # Get or create adaptive rate limiter
            if service_name not in self.rate_limiters:
                config = RateLimitConfig(
                    service_name=service_name,
                    algorithm=RateLimitingAlgorithm.ADAPTIVE
                )
                await self._create_rate_limiter(service_name, config)
            
            rate_limiter = self.rate_limiters[service_name]
            
            # Apply adaptive adjustments
            adaptations = await self._apply_adaptive_adjustments(service_name, pattern_analysis)
            
            # Update metrics
            await self._update_adaptive_metrics(service_name, adaptations)
            
            self.logger.info(f"🔄 Adaptive rate limiting implemented for {service_name}: {adaptations}")
            return {
                'service_name': service_name,
                'pattern_analysis': pattern_analysis,
                'adaptations': adaptations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to implement adaptive rate limiting: {e}")
            raise
    
    async def _analyze_traffic_patterns(self, traffic_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze traffic patterns for adaptive rate limiting"""
        # Extract pattern metrics
        request_rates = traffic_patterns.get('request_rates', [])
        response_times = traffic_patterns.get('response_times', [])
        error_rates = traffic_patterns.get('error_rates', [])
        
        analysis = {
            'peak_rate': max(request_rates) if request_rates else 0,
            'average_rate': statistics.mean(request_rates) if request_rates else 0,
            'rate_variance': statistics.variance(request_rates) if len(request_rates) > 1 else 0,
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'error_rate': statistics.mean(error_rates) if error_rates else 0,
            'traffic_trend': 'increasing' if len(request_rates) > 1 and request_rates[-1] > request_rates[0] else 'stable'
        }
        
        # Determine traffic characteristics
        if analysis['rate_variance'] > analysis['average_rate'] * 0.5:
            analysis['pattern'] = 'highly_variable'
        elif analysis['peak_rate'] > analysis['average_rate'] * 2:
            analysis['pattern'] = 'bursty'
        elif analysis['traffic_trend'] == 'increasing':
            analysis['pattern'] = 'growing'
        else:
            analysis['pattern'] = 'stable'
        
        return analysis
    
    async def _apply_adaptive_adjustments(self, service_name: str, 
                                        pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply adaptive adjustments based on pattern analysis"""
        config = self.service_configs[service_name]
        rate_limiter = self.rate_limiters[service_name]
        adjustments = {}
        
        pattern = pattern_analysis['pattern']
        
        if pattern == 'highly_variable':
            # Increase burst capacity for variable traffic
            new_burst = int(config.burst_capacity * 1.5)
            adjustments['burst_capacity_increased'] = new_burst
            
        elif pattern == 'bursty':
            # Optimize for burst handling
            new_burst = int(pattern_analysis['peak_rate'] * 1.2)
            new_base_rate = int(pattern_analysis['average_rate'] * 1.1)
            adjustments['optimized_for_bursts'] = {
                'burst_capacity': new_burst,
                'base_rate': new_base_rate
            }
            
        elif pattern == 'growing':
            # Gradually increase rate limits
            growth_factor = 1.2
            new_base_rate = int(config.base_rate_limit * growth_factor)
            adjustments['rate_limit_increased'] = new_base_rate
            
        # Apply error rate adjustments
        if pattern_analysis['error_rate'] > 0.1:
            error_factor = config.adaptive_factors['error_factor']
            adjustments['error_rate_adjustment'] = error_factor
        
        return adjustments
    
    async def manage_backpressure_signals(self, backpressure_data: Dict[str, Any]) -> bool:
        """Manage backpressure signals between systems"""
        try:
            signal_type = backpressure_data.get('signal_type', 'rate_limit_exceeded')
            source_service = backpressure_data.get('source_service')
            target_service = backpressure_data.get('target_service')
            severity = backpressure_data.get('severity', 'medium')
            
            if not all([source_service, target_service]):
                raise ValueError("Source and target services required for backpressure signal")
            
            # Create backpressure signal
            level = BackpressureLevel[severity.upper()]
            signal = BackpressureSignal(
                signal_id=str(uuid.uuid4()),
                source_service=source_service,
                target_service=target_service,
                level=level,
                rate_reduction=backpressure_data.get('rate_reduction', 0.5),
                duration_seconds=backpressure_data.get('duration', 60),
                timestamp=datetime.now(),
                metadata=backpressure_data.get('metadata', {})
            )
            
            # Emit the signal
            await self.backpressure_manager.emit_backpressure_signal(signal)
            
            # Apply immediate adjustments if needed
            if level in [BackpressureLevel.HIGH, BackpressureLevel.CRITICAL]:
                await self._apply_emergency_adjustments(target_service, signal)
            
            self.logger.info(f"🔔 Backpressure signal managed: {signal_type} from {source_service} to {target_service}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to manage backpressure signals: {e}")
            return False
    
    async def _apply_emergency_adjustments(self, service_name: str, signal: BackpressureSignal):
        """Apply emergency adjustments for critical backpressure"""
        if service_name in self.rate_limiters:
            config = self.service_configs[service_name]
            rate_limiter = self.rate_limiters[service_name]
            
            # Drastically reduce rate limit
            emergency_rate = int(config.base_rate_limit * (1 - signal.rate_reduction))
            rate_limiter.update_rate_limit(max(1, emergency_rate))
            
            self.logger.warning(f"🚨 Emergency rate limit adjustment for {service_name}: {emergency_rate}")
    
    async def _handle_high_backpressure(self, signal: BackpressureSignal):
        """Handle high backpressure signal"""
        self.logger.warning(f"⚠️ High backpressure detected: {signal.source_service} -> {signal.target_service}")
        
        # Apply gradual rate reduction
        if signal.target_service in self.rate_limiters:
            await self._apply_gradual_rate_reduction(signal.target_service, 0.3)
    
    async def _handle_critical_backpressure(self, signal: BackpressureSignal):
        """Handle critical backpressure signal"""
        self.logger.error(f"🚨 Critical backpressure detected: {signal.source_service} -> {signal.target_service}")
        
        # Apply emergency measures
        await self._apply_emergency_adjustments(signal.target_service, signal)
        
        # Consider activating circuit breaker
        self.logger.info(f"💡 Recommending circuit breaker activation for {signal.target_service}")
    
    async def _apply_gradual_rate_reduction(self, service_name: str, reduction_factor: float):
        """Apply gradual rate reduction"""
        if service_name in self.rate_limiters:
            config = self.service_configs[service_name]
            rate_limiter = self.rate_limiters[service_name]
            
            new_rate = int(config.base_rate_limit * (1 - reduction_factor))
            rate_limiter.update_rate_limit(max(1, new_rate))
            
            self.logger.info(f"📉 Gradual rate reduction for {service_name}: {new_rate}")
    
    async def check_rate_limit(self, service_name: str, tokens_needed: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limit"""
        if service_name not in self.rate_limiters:
            return True, {'reason': 'no_rate_limiter_configured'}
        
        rate_limiter = self.rate_limiters[service_name]
        metrics = self.metrics[service_name]
        
        # Check rate limit
        allowed = await rate_limiter.acquire_token(tokens_needed)
        
        # Update metrics
        metrics.total_requests += 1
        if allowed:
            metrics.allowed_requests += 1
        else:
            metrics.rejected_requests += 1
        
        # Calculate current rate and utilization
        if hasattr(rate_limiter, 'get_current_rate'):
            metrics.current_rate = rate_limiter.get_current_rate()
        
        metrics.utilization = metrics.current_rate / max(metrics.current_limit, 1)
        metrics.last_updated = datetime.now()
        
        # Determine backpressure level
        config = self.service_configs[service_name]
        for level, threshold in config.backpressure_thresholds.items():
            if metrics.utilization >= threshold:
                metrics.backpressure_level = level
                break
        else:
            metrics.backpressure_level = BackpressureLevel.NONE
        
        return allowed, {
            'utilization': metrics.utilization,
            'backpressure_level': metrics.backpressure_level.value,
            'current_rate': metrics.current_rate,
            'current_limit': metrics.current_limit
        }
    
    async def _update_coordination_metrics(self, service_name: str, coordination_result: Dict[str, Any]):
        """Update coordination metrics"""
        metrics = self.metrics[service_name]
        
        # Update circuit state factor
        circuit_state = self.circuit_breaker_states.get(service_name, 'CLOSED')
        if circuit_state == 'OPEN':
            metrics.circuit_state_factor = 0.1
        elif circuit_state == 'HALF_OPEN':
            metrics.circuit_state_factor = 0.5
        else:
            metrics.circuit_state_factor = 1.0
        
        metrics.last_updated = datetime.now()
    
    async def _update_adaptive_metrics(self, service_name: str, adaptations: Dict[str, Any]):
        """Update adaptive metrics"""
        metrics = self.metrics[service_name]
        
        # Update current limit based on adaptations
        config = self.service_configs[service_name]
        if 'rate_limit_increased' in adaptations:
            metrics.current_limit = adaptations['rate_limit_increased']
        elif 'optimized_for_bursts' in adaptations:
            metrics.current_limit = adaptations['optimized_for_bursts']['base_rate']
        else:
            metrics.current_limit = config.base_rate_limit
        
        metrics.last_updated = datetime.now()
    
    async def get_rate_limiting_analytics(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive rate limiting analytics"""
        try:
            if service_name:
                # Single service analytics
                if service_name not in self.metrics:
                    return {'error': f'No data for service {service_name}'}
                
                metrics = self.metrics[service_name]
                config = self.service_configs.get(service_name, {})
                
                return {
                    'service_name': service_name,
                    'metrics': {
                        'total_requests': metrics.total_requests,
                        'allowed_requests': metrics.allowed_requests,
                        'rejected_requests': metrics.rejected_requests,
                        'rejection_rate': metrics.rejected_requests / max(metrics.total_requests, 1),
                        'current_rate': metrics.current_rate,
                        'current_limit': metrics.current_limit,
                        'utilization': metrics.utilization,
                        'backpressure_level': metrics.backpressure_level.value,
                        'circuit_state_factor': metrics.circuit_state_factor
                    },
                    'configuration': {
                        'algorithm': config.algorithm.value if hasattr(config, 'algorithm') else 'unknown',
                        'base_rate_limit': getattr(config, 'base_rate_limit', 0),
                        'coordination_enabled': getattr(config, 'circuit_integration', False)
                    },
                    'active_backpressure_signals': len(self.backpressure_manager.get_active_signals_for_service(service_name)),
                    'last_updated': metrics.last_updated.isoformat()
                }
            else:
                # System-wide analytics
                total_requests = sum(m.total_requests for m in self.metrics.values())
                total_rejections = sum(m.rejected_requests for m in self.metrics.values())
                
                return {
                    'system_wide': {
                        'total_services': len(self.metrics),
                        'total_requests': total_requests,
                        'total_rejections': total_rejections,
                        'overall_rejection_rate': total_rejections / max(total_requests, 1),
                        'coordination_strategy': self.coordination_strategy.value,
                        'active_rate_limiters': len(self.rate_limiters),
                        'active_backpressure_signals': len(self.backpressure_manager.active_signals)
                    },
                    'services': {name: {
                        'requests': metrics.total_requests,
                        'rejection_rate': metrics.rejected_requests / max(metrics.total_requests, 1),
                        'utilization': metrics.utilization,
                        'backpressure_level': metrics.backpressure_level.value
                    } for name, metrics in self.metrics.items()},
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get rate limiting analytics: {e}")
            raise
    
    async def start_monitoring(self):
        """Start monitoring task"""
        if not self.monitoring_task:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.logger.info("📊 Started rate limiting monitoring")
    
    async def stop_monitoring(self):
        """Stop monitoring task"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
            self.logger.info("⏹️ Stopped rate limiting monitoring")
    
    async def _monitoring_loop(self):
        """Monitoring loop for rate limiting metrics"""
        while True:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                # Check for backpressure signals to clear
                current_time = datetime.now()
                expired_signals = []
                
                for signal_id, signal in self.backpressure_manager.active_signals.items():
                    if (current_time - signal.timestamp).seconds > signal.duration_seconds:
                        expired_signals.append(signal_id)
                
                # Clear expired signals
                for signal_id in expired_signals:
                    await self.backpressure_manager.clear_backpressure_signal(signal_id)
                
                # Update metrics and check for adaptive adjustments
                for service_name in self.rate_limiters.keys():
                    try:
                        await self._check_adaptive_adjustments(service_name)
                    except Exception as e:
                        self.logger.error(f"❌ Error in adaptive adjustment for {service_name}: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")
    
    async def _check_adaptive_adjustments(self, service_name: str):
        """Check if adaptive adjustments are needed"""
        metrics = self.metrics[service_name]
        config = self.service_configs[service_name]
        
        # Check if high rejection rate requires adjustment
        if metrics.total_requests > 100:  # Minimum sample size
            rejection_rate = metrics.rejected_requests / metrics.total_requests
            
            if rejection_rate > 0.2:  # More than 20% rejection rate
                # Consider increasing rate limit
                new_limit = int(config.base_rate_limit * 1.1)
                if service_name in self.rate_limiters:
                    self.rate_limiters[service_name].update_rate_limit(new_limit)
                    self.logger.info(f"📈 Adaptive increase for {service_name}: {new_limit}")
    
    async def cleanup(self):
        """Cleanup rate limiting integration"""
        try:
            await self.stop_monitoring()
            
            # Close Redis connection if exists
            if self.redis_client:
                await self.redis_client.close()
            
            self.rate_limiters.clear()
            self.service_configs.clear()
            self.metrics.clear()
            self.circuit_breaker_states.clear()
            
            self.logger.info("🧹 Rate Limiting Integration cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")


# Global rate limiting integration instance
rate_limiting_integration = RateLimitingIntegration()


# Export main classes and functions
__all__ = [
    'RateLimitingIntegration',
    'RateLimitConfig',
    'RateLimitingAlgorithm',
    'BackpressureLevel',
    'CoordinationStrategy',
    'RateLimitMetrics',
    'BackpressureSignal',
    'BackpressureManager',
    'TokenBucketRateLimiter',
    'SlidingWindowRateLimiter',
    'AdaptiveRateLimiter',
    'rate_limiting_integration'
]


if __name__ == "__main__":
    async def demo():
        """Demo rate limiting integration functionality"""
        integration = RateLimitingIntegration()
        
        # Configure coordination
        coordination_config = {
            'service_name': 'user-service',
            'circuit_state': 'CLOSED',
            'base_rate_limit': 100,
            'time_window': 60,
            'system_metrics': {
                'cpu_usage': 70,
                'error_rate': 0.05
            }
        }
        
        # Coordinate circuit breakers and rate limiting
        coordination_result = await integration.coordinate_circuit_and_rate_limits(coordination_config)
        print(f"Coordination result: {json.dumps(coordination_result, indent=2)}")
        
        # Test rate limiting
        for i in range(10):
            allowed, info = await integration.check_rate_limit('user-service')
            print(f"Request {i+1}: {'✅ Allowed' if allowed else '❌ Rejected'} - {info}")
        
        # Get analytics
        analytics = await integration.get_rate_limiting_analytics('user-service')
        print(f"Analytics: {json.dumps(analytics, indent=2, default=str)}")
        
        # Cleanup
        await integration.cleanup()
    
    # Run demo
    asyncio.run(demo())