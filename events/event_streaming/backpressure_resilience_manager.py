"""IA Influencer Agent - Backpressure Resilience Manager
Advanced Backpressure Management and System Resilience for Ainflue Event Streaming

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
import time
import statistics
from uuid import uuid4
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class BackpressureStrategy(Enum):
    """Backpressure handling strategies"""
    DROP_OLDEST = "drop_oldest"
    DROP_NEWEST = "drop_newest"
    THROTTLE = "throttle"
    CIRCUIT_BREAKER = "circuit_breaker"
    ADAPTIVE_BATCHING = "adaptive_batching"
    LOAD_SHEDDING = "load_shedding"


class SystemState(Enum):
    """System states for resilience management"""
    HEALTHY = "healthy"
    UNDER_PRESSURE = "under_pressure"
    CRITICAL = "critical"
    RECOVERY = "recovery"
    DEGRADED = "degraded"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class BackpressureMetrics:
    """Metrics for backpressure monitoring"""
    
    buffer_utilization: float = 0.0
    processing_latency_ms: float = 0.0
    throughput_per_sec: float = 0.0
    error_rate: float = 0.0
    dropped_events: int = 0
    throttled_events: int = 0
    circuit_breaker_trips: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ResilienceConfig:
    """Configuration for resilience management"""
    
    # Buffer configuration
    max_buffer_size: int = 10000
    buffer_high_watermark: float = 0.8
    buffer_low_watermark: float = 0.3
    
    # Latency thresholds
    latency_warning_threshold_ms: float = 100.0
    latency_critical_threshold_ms: float = 500.0
    
    # Throughput configuration
    min_throughput_per_sec: float = 100.0
    max_throughput_per_sec: float = 10000.0
    
    # Error rate thresholds
    error_rate_warning_threshold: float = 0.05
    error_rate_critical_threshold: float = 0.15
    
    # Circuit breaker configuration
    circuit_failure_threshold: int = 5
    circuit_timeout_seconds: int = 60
    circuit_half_open_max_calls: int = 3
    
    # Adaptive configuration
    adaptation_window_seconds: int = 60
    pressure_relief_factor: float = 0.7


class PressureGauge:
    """Measures system pressure based on multiple metrics"""
    
    def __init__(self, config -> None: ResilienceConfig) -> None:
        self.config = config
        self.metrics_history: deque = deque(maxlen=100)
        
    async def measure_pressure(self, metrics: BackpressureMetrics) -> float:
        """Measure current system pressure (0.0 = no pressure, 1.0 = maximum pressure)"""
        try:
            pressure_factors = []
            
            # Buffer pressure
            buffer_pressure = min(1.0, metrics.buffer_utilization)
            pressure_factors.append(buffer_pressure * 0.3)  # 30% weight
            
            # Latency pressure
            latency_pressure = min(1.0, 
                metrics.processing_latency_ms / self.config.latency_critical_threshold_ms
            )
            pressure_factors.append(latency_pressure * 0.3)  # 30% weight
            
            # Error rate pressure
            error_pressure = min(1.0, 
                metrics.error_rate / self.config.error_rate_critical_threshold
            )
            pressure_factors.append(error_pressure * 0.25)  # 25% weight
            
            # Throughput pressure (inverted - low throughput = high pressure)
            throughput_ratio = metrics.throughput_per_sec / self.config.max_throughput_per_sec
            throughput_pressure = max(0.0, 1.0 - throughput_ratio)
            pressure_factors.append(throughput_pressure * 0.15)  # 15% weight
            
            total_pressure = sum(pressure_factors)
            
            # Store in history
            self.metrics_history.append({
                "timestamp": datetime.now(timezone.utc),
                "pressure": total_pressure,
                "metrics": metrics
            })
            
            return total_pressure
            
        except Exception as e:
            logger.error(f"Error measuring pressure: {e}")
            return 0.0
    
    def get_pressure_trend(self) -> str:
        """Get pressure trend (increasing, decreasing, stable)"""
        try:
            if len(self.metrics_history) < 5:
                return "stable"
            
            recent_pressures = [entry["pressure"] for entry in list(self.metrics_history)[-5:]]
            
            # Calculate trend
            trend = statistics.linear_regression(range(len(recent_pressures)), recent_pressures)[0]
            
            if trend > 0.01:
                return "increasing"
            elif trend < -0.01:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating pressure trend: {e}")
            return "stable"


class CircuitBreaker:
    """Circuit breaker for protecting downstream systems"""
    
    def __init__(self, config -> None: ResilienceConfig) -> None:
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        
    async def call(self, operation: Callable) -> Any:
        """Execute operation through circuit breaker"""
        try:
            if self.state == CircuitState.OPEN:
                if await self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is open")
            
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.config.circuit_half_open_max_calls:
                    raise CircuitBreakerOpenError("Half-open call limit exceeded")
                
                self.half_open_calls += 1
            
            # Execute operation
            result = await operation()
            
            # Success
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time:
            time_since_failure = datetime.now(timezone.utc) - self.last_failure_time
            return time_since_failure.total_seconds() >= self.config.circuit_timeout_seconds
        return True
    
    async def _on_success(self) -> None:
        """Handle successful operation"""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            
        self.failure_count = 0
        self.half_open_calls = 0
    
    async def _on_failure(self) -> None:
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        
        if self.failure_count >= self.config.circuit_failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        return self.state == CircuitState.OPEN


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class AdaptiveBatchProcessor:
    """Adaptive batch processing to handle backpressure"""
    
    def __init__(self, config -> None: ResilienceConfig) -> None:
        self.config = config
        self.current_batch_size = 100
        self.min_batch_size = 10
        self.max_batch_size = 1000
        self.batch_performance_history: deque = deque(maxlen=50)
        
    async def process_batch(self, events: List[Any], processor: Callable) -> List[Any]:
        """Process events in adaptive batches"""
        try:
            results = []
            
            # Split events into adaptive batches
            for i in range(0, len(events), self.current_batch_size):
                batch = events[i:i + self.current_batch_size]
                
                batch_start_time = time.time()
                
                try:
                    batch_results = await processor(batch)
                    results.extend(batch_results)
                    
                    # Record successful batch
                    batch_time = time.time() - batch_start_time
                    await self._record_batch_performance(len(batch), batch_time, True)
                    
                except Exception as e:
                    logger.error(f"Batch processing failed: {e}")
                    await self._record_batch_performance(len(batch), time.time() - batch_start_time, False)
                    
                    # Process events individually as fallback
                    for event in batch:
                        try:
                            individual_result = await processor([event])
                            results.extend(individual_result)
                        except Exception as individual_error:
                            logger.error(f"Individual event processing failed: {individual_error}")
            
            # Adapt batch size based on performance
            await self._adapt_batch_size()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in adaptive batch processing: {e}")
            return []
    
    async def _record_batch_performance(self, batch_size -> None: int, processing_time -> None: float, success -> None: bool) -> None:
        """Record batch processing performance"""
        self.batch_performance_history.append({
            "batch_size": batch_size,
            "processing_time": processing_time,
            "success": success,
            "timestamp": datetime.now(timezone.utc)
        })
    
    async def _adapt_batch_size(self) -> None:
        """Adapt batch size based on recent performance"""
        try:
            if len(self.batch_performance_history) < 5:
                return
            
            recent_batches = list(self.batch_performance_history)[-10:]
            successful_batches = [b for b in recent_batches if b["success"]]
            
            if not successful_batches:
                # Reduce batch size if all recent batches failed
                self.current_batch_size = max(self.min_batch_size, int(self.current_batch_size * 0.7))
                return
            
            # Calculate average processing time per event
            avg_time_per_event = statistics.mean([
                b["processing_time"] / b["batch_size"] for b in successful_batches
            ])
            
            # Calculate success rate
            success_rate = len(successful_batches) / len(recent_batches)
            
            # Adapt batch size
            if success_rate > 0.9 and avg_time_per_event < 0.01:  # 10ms per event
                # Increase batch size
                self.current_batch_size = min(self.max_batch_size, int(self.current_batch_size * 1.2))
            elif success_rate < 0.7 or avg_time_per_event > 0.05:  # 50ms per event
                # Decrease batch size
                self.current_batch_size = max(self.min_batch_size, int(self.current_batch_size * 0.8))
            
            logger.debug(f"Adapted batch size to {self.current_batch_size}")
            
        except Exception as e:
            logger.error(f"Error adapting batch size: {e}")


class LoadShedder:
    """Load shedding to drop events under extreme pressure"""
    
    def __init__(self, config -> None: ResilienceConfig) -> None:
        self.config = config
        self.drop_rates_by_priority = {
            "low": 0.8,     # Drop 80% of low priority events
            "medium": 0.5,  # Drop 50% of medium priority events
            "high": 0.1,    # Drop 10% of high priority events
            "critical": 0.0 # Never drop critical events
        }
        
    async def should_drop_event(self, event: Dict[str, Any], pressure_level: float) -> bool:
        """Determine if event should be dropped based on pressure"""
        try:
            if pressure_level < 0.7:
                return False  # No load shedding under normal conditions
            
            # Extract event priority
            priority = event.get("priority", "medium")
            event_type = event.get("event_type", "")
            
            # Never drop critical business events
            if self._is_critical_business_event(event_type):
                return False
            
            # Calculate drop probability based on pressure and priority
            base_drop_rate = self.drop_rates_by_priority.get(priority, 0.5)
            pressure_multiplier = min(1.0, (pressure_level - 0.7) / 0.3)  # Scale from 0.7 to 1.0
            
            drop_probability = base_drop_rate * pressure_multiplier
            
            # Use deterministic dropping based on event hash for fairness
            import hashlib
            event_hash = hashlib.md5(event.get("event_id", str(uuid4())).encode()).hexdigest()
            hash_value = int(event_hash, 16) % 1000 / 1000.0
            
            should_drop = hash_value < drop_probability
            
            if should_drop:
                logger.debug(f"Load shedding: dropping event {event.get('event_id')} "
                           f"(priority: {priority}, pressure: {pressure_level:.2f})")
            
            return should_drop
            
        except Exception as e:
            logger.error(f"Error in load shedding decision: {e}")
            return False
    
    def _is_critical_business_event(self, event_type: str) -> bool:
        """Check if event type is critical for business operations"""
        critical_event_types = [
            "revenue_generated",
            "payment_processed", 
            "user_registration",
            "content_published",
            "collaboration_accepted",
            "system_alert"
        ]
        
        return any(critical_type in event_type.lower() for critical_type in critical_event_types)


class BackpressureResilienceManager:
    """Main backpressure and resilience manager for Ainflue streaming platform"""
    
    def __init__(self, config -> None: ResilienceConfig = None, metrics_collector=None) -> None:
        self.config = config or ResilienceConfig()
        self.metrics_collector = metrics_collector
        self.current_metrics = BackpressureMetrics()
        self.system_state = SystemState.HEALTHY
        
        # Components
        self.pressure_gauge = PressureGauge(self.config)
        self.circuit_breaker = CircuitBreaker(self.config)
        self.adaptive_batch_processor = AdaptiveBatchProcessor(self.config)
        self.load_shedder = LoadShedder(self.config)
        
        # Event buffers with different priorities
        self.event_buffers = {
            "critical": deque(maxlen=self.config.max_buffer_size),
            "high": deque(maxlen=self.config.max_buffer_size),
            "medium": deque(maxlen=self.config.max_buffer_size),
            "low": deque(maxlen=self.config.max_buffer_size)
        }
        
        self._manager_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self) -> None:
        """Start the backpressure resilience manager"""
        try:
            logger.info("Starting Backpressure Resilience Manager")
            
            # Start monitoring task
            self._manager_task = asyncio.create_task(self._manager_loop())
            
            logger.info("Backpressure Resilience Manager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start backpressure resilience manager: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the resilience manager"""
        try:
            logger.info("Stopping Backpressure Resilience Manager")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Wait for manager task
            if self._manager_task:
                await self._manager_task
            
            logger.info("Backpressure Resilience Manager stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping backpressure resilience manager: {e}")
            raise
    
    async def apply_backpressure_control(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply backpressure control to event stream"""
        try:
            # Update current metrics
            await self._update_metrics()
            
            # Measure current pressure
            pressure_level = await self.pressure_gauge.measure_pressure(self.current_metrics)
            
            # Update system state based on pressure
            await self._update_system_state(pressure_level)
            
            # Apply appropriate backpressure strategy
            controlled_events = await self._apply_backpressure_strategy(events, pressure_level)
            
            # Update metrics
            if self.metrics_collector:
                self.metrics_collector.histogram("backpressure_pressure_level", pressure_level)
                self.metrics_collector.increment_counter("backpressure_events_processed", len(controlled_events))
            
            return controlled_events
            
        except Exception as e:
            logger.error(f"Error applying backpressure control: {e}")
            return events  # Return original events on error
    
    async def _apply_backpressure_strategy(self, events: List[Dict[str, Any]], pressure_level: float) -> List[Dict[str, Any]]:
        """Apply appropriate backpressure strategy based on pressure level"""
        try:
            if pressure_level < self.config.buffer_low_watermark:
                # Normal processing
                return await self._process_normally(events)
            
            elif pressure_level < self.config.buffer_high_watermark:
                # Apply throttling and adaptive batching
                return await self._apply_throttling(events, pressure_level)
            
            else:
                # Apply aggressive load shedding
                return await self._apply_load_shedding(events, pressure_level)
                
        except Exception as e:
            logger.error(f"Error applying backpressure strategy: {e}")
            return events
    
    async def _process_normally(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process events normally without backpressure"""
        return events
    
    async def _apply_throttling(self, events: List[Dict[str, Any]], pressure_level: float) -> List[Dict[str, Any]]:
        """Apply throttling to reduce event processing rate"""
        try:
            # Calculate throttling delay based on pressure
            base_delay = 0.001  # 1ms base delay
            pressure_multiplier = (pressure_level - self.config.buffer_low_watermark) / (self.config.buffer_high_watermark - self.config.buffer_low_watermark)
            throttle_delay = base_delay * (1 + pressure_multiplier * 10)  # Up to 11ms delay
            
            # Apply throttling
            if throttle_delay > 0:
                await asyncio.sleep(throttle_delay)
                self.current_metrics.throttled_events += len(events)
            
            # Apply adaptive batching if pressure is high
            if pressure_level > 0.6:
                processed_events = await self.adaptive_batch_processor.process_batch(
                    events, 
                    self._mock_batch_processor
                )
                return processed_events
            
            return events
            
        except Exception as e:
            logger.error(f"Error applying throttling: {e}")
            return events
    
    async def _apply_load_shedding(self, events: List[Dict[str, Any]], pressure_level: float) -> List[Dict[str, Any]]:
        """Apply load shedding to drop events under extreme pressure"""
        try:
            kept_events = []
            
            for event in events:
                should_drop = await self.load_shedder.should_drop_event(event, pressure_level)
                
                if not should_drop:
                    kept_events.append(event)
                else:
                    self.current_metrics.dropped_events += 1
            
            logger.warning(f"Load shedding: kept {len(kept_events)}/{len(events)} events "
                          f"(pressure: {pressure_level:.2f})")
            
            return kept_events
            
        except Exception as e:
            logger.error(f"Error applying load shedding: {e}")
            return events
    
    async def _mock_batch_processor(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mock batch processor for demonstration"""
        # Simulate processing time
        await asyncio.sleep(0.001 * len(batch))
        return batch
    
    async def _update_metrics(self) -> None:
        """Update current backpressure metrics"""
        try:
            # Calculate buffer utilization
            total_events = sum(len(buffer) for buffer in self.event_buffers.values())
            max_capacity = len(self.event_buffers) * self.config.max_buffer_size
            self.current_metrics.buffer_utilization = total_events / max_capacity if max_capacity > 0 else 0
            
            # Processing latency would be measured from actual processing
            # For now, simulate based on buffer utilization
            self.current_metrics.processing_latency_ms = self.current_metrics.buffer_utilization * 100
            
            # Throughput simulation
            self.current_metrics.throughput_per_sec = max(
                0, self.config.max_throughput_per_sec * (1 - self.current_metrics.buffer_utilization)
            )
            
            # Error rate simulation (increases with pressure)
            self.current_metrics.error_rate = min(0.2, self.current_metrics.buffer_utilization * 0.1)
            
            self.current_metrics.last_updated = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    async def _update_system_state(self, pressure_level -> None: float) -> None:
        """Update system state based on pressure level"""
        try:
            previous_state = self.system_state
            
            if pressure_level < 0.3:
                self.system_state = SystemState.HEALTHY
            elif pressure_level < 0.7:
                self.system_state = SystemState.UNDER_PRESSURE
            elif pressure_level < 0.9:
                self.system_state = SystemState.CRITICAL
            else:
                self.system_state = SystemState.DEGRADED
            
            # Check for recovery state
            pressure_trend = self.pressure_gauge.get_pressure_trend()
            if (previous_state in [SystemState.CRITICAL, SystemState.DEGRADED] and 
                pressure_level < 0.8 and pressure_trend == "decreasing"):
                self.system_state = SystemState.RECOVERY
            
            # Log state changes
            if self.system_state != previous_state:
                logger.info(f"System state changed from {previous_state.value} to {self.system_state.value} "
                           f"(pressure: {pressure_level:.2f})")
                
                if self.metrics_collector:
                    self.metrics_collector.increment_counter(f"system_state_{self.system_state.value}")
                    
        except Exception as e:
            logger.error(f"Error updating system state: {e}")
    
    async def _manager_loop(self) -> None:
        """Main manager monitoring loop"""
        try:
            while not self._shutdown_event.is_set():
                # Update metrics and monitor system health
                await self._update_metrics()
                
                # Log current state periodically
                pressure_level = await self.pressure_gauge.measure_pressure(self.current_metrics)
                logger.debug(f"Backpressure manager health check: "
                           f"pressure={pressure_level:.2f}, state={self.system_state.value}, "
                           f"buffer_util={self.current_metrics.buffer_utilization:.2f}")
                
                # Sleep before next iteration
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except Exception as e:
            logger.error(f"Error in manager loop: {e}")
    
    def get_resilience_metrics(self) -> Dict[str, Any]:
        """Get comprehensive resilience metrics"""
        try:
            pressure_level = 0.0
            if self.pressure_gauge.metrics_history:
                pressure_level = self.pressure_gauge.metrics_history[-1]["pressure"]
            
            metrics = {
                "system_state": self.system_state.value,
                "pressure_level": pressure_level,
                "pressure_trend": self.pressure_gauge.get_pressure_trend(),
                "circuit_breaker_state": self.circuit_breaker.state.value,
                "current_batch_size": self.adaptive_batch_processor.current_batch_size,
                "buffer_utilization": self.current_metrics.buffer_utilization,
                "processing_latency_ms": self.current_metrics.processing_latency_ms,
                "throughput_per_sec": self.current_metrics.throughput_per_sec,
                "error_rate": self.current_metrics.error_rate,
                "dropped_events": self.current_metrics.dropped_events,
                "throttled_events": self.current_metrics.throttled_events,
                "circuit_breaker_trips": self.current_metrics.circuit_breaker_trips,
                "last_updated": self.current_metrics.last_updated.isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting resilience metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "BackpressureResilienceManager", "ResilienceConfig", "BackpressureMetrics",
    "PressureGauge", "CircuitBreaker", "AdaptiveBatchProcessor", "LoadShedder",
    "BackpressureStrategy", "SystemState", "CircuitState", "CircuitBreakerOpenError"
]