"""
Ainflue Core Infrastructure - Distributed Tracing Core
=====================================================

Enterprise-grade distributed tracing system for monitoring, debugging, and 
performance analysis across microservices architecture. Provides OpenTelemetry
integration, custom span creation, and advanced trace analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager, contextmanager
import json
from datetime import datetime, timedelta

# Third-party imports (with fallbacks)
try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

logger = logging.getLogger(__name__)

class TracingLevel(str, Enum):
    """Tracing detail levels"""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    DEBUG = "debug"
    PERFORMANCE = "performance"

class SpanType(str, Enum):
    """Types of spans for categorization"""
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    CACHE_OPERATION = "cache_operation"
    EXTERNAL_API = "external_api"
    BUSINESS_LOGIC = "business_logic"
    AI_PROCESSING = "ai_processing"
    SECURITY_CHECK = "security_check"
    PAYMENT_PROCESSING = "payment_processing"

@dataclass
class SpanContext:
    """Custom span context for internal tracing"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"
    error: Optional[str] = None

    def finish(self, error: Optional[str] = None):
        """Finish the span"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = "error" if error else "completed"
        self.error = error

@dataclass
class TraceMetrics:
    """Trace performance metrics"""
    total_traces: int = 0
    active_traces: int = 0
    completed_traces: int = 0
    error_traces: int = 0
    avg_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0
    spans_per_trace: float = 0.0
    error_rate: float = 0.0

class TracingCore:
    """Enterprise distributed tracing system"""
    
    def __init__(self, level: str = "enterprise"):
        """Initialize tracing core"""
        self.level = TracingLevel.DETAILED if level == "enterprise" else TracingLevel.STANDARD
        self.active_spans: Dict[str, SpanContext] = {}
        self.completed_spans: List[SpanContext] = []
        self.trace_metrics = TraceMetrics()
        self.samplers: Dict[str, Callable] = {}
        self.processors: List[Callable] = []
        self.exporters: List[Any] = []
        
        # OpenTelemetry integration
        self.tracer_provider = None
        self.tracer = None
        
        # Configuration
        self.config = {
            "service_name": "ainflue-core",
            "service_version": "1.0.0",
            "environment": "production",
            "jaeger_endpoint": "http://localhost:14268/api/traces",
            "sample_rate": 1.0,
            "max_spans_per_trace": 1000,
            "max_trace_duration": 300,  # 5 minutes
            "batch_export_timeout": 30,
            "max_export_batch_size": 512
        }
        
        self._initialize_tracing()
        
        logger.info(f"🔍 Tracing Core initialized - Level: {self.level}")

    def _initialize_tracing(self):
        """Initialize tracing backend"""
        try:
            if OPENTELEMETRY_AVAILABLE:
                self._setup_opentelemetry()
            else:
                logger.warning("OpenTelemetry not available, using fallback tracing")
            
            # Setup custom processors
            self._setup_processors()
            
            # Setup samplers
            self._setup_samplers()
            
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {str(e)}")

    def _setup_opentelemetry(self):
        """Setup OpenTelemetry integration"""
        if not OPENTELEMETRY_AVAILABLE:
            return
            
        try:
            # Create tracer provider
            self.tracer_provider = TracerProvider()
            trace.set_tracer_provider(self.tracer_provider)
            
            # Create tracer
            self.tracer = trace.get_tracer(
                self.config["service_name"],
                self.config["service_version"]
            )
            
            # Setup Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
                collector_endpoint=self.config["jaeger_endpoint"]
            )
            
            # Add span processor
            span_processor = BatchSpanProcessor(
                jaeger_exporter,
                max_export_batch_size=self.config["max_export_batch_size"],
                export_timeout_millis=self.config["batch_export_timeout"] * 1000
            )
            
            self.tracer_provider.add_span_processor(span_processor)
            self.exporters.append(jaeger_exporter)
            
            logger.info("✅ OpenTelemetry initialized with Jaeger exporter")
            
        except Exception as e:
            logger.error(f"Failed to setup OpenTelemetry: {str(e)}")

    def _setup_processors(self):
        """Setup trace processors"""
        self.processors = [
            self._enrich_span_processor,
            self._performance_processor,
            self._security_processor,
            self._business_processor
        ]

    def _setup_samplers(self):
        """Setup trace samplers"""
        self.samplers = {
            "always": lambda: True,
            "never": lambda: False,
            "probability": lambda: time.time() % 1 < self.config["sample_rate"],
            "rate_limited": self._rate_limited_sampler,
            "error_biased": self._error_biased_sampler
        }

    def _rate_limited_sampler(self) -> bool:
        """Rate-limited sampling"""
        current_minute = int(time.time() // 60)
        key = f"sample_{current_minute}"
        
        if not hasattr(self, '_sample_counts'):
            self._sample_counts = {}
        
        count = self._sample_counts.get(key, 0)
        max_per_minute = 100  # Max 100 traces per minute
        
        if count < max_per_minute:
            self._sample_counts[key] = count + 1
            return True
        return False

    def _error_biased_sampler(self) -> bool:
        """Error-biased sampling - always sample errors"""
        # This would be determined at span finish time
        return True

    @asynccontextmanager
    async def trace(
        self,
        operation_name: str,
        span_type: SpanType = SpanType.BUSINESS_LOGIC,
        tags: Optional[Dict[str, Any]] = None,
        parent_span_id: Optional[str] = None
    ):
        """Create and manage a trace span"""
        span_id = str(uuid.uuid4())
        trace_id = parent_span_id or str(uuid.uuid4())
        
        span = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        # Add span type tag
        span.tags["span.type"] = span_type.value
        span.tags["service.name"] = self.config["service_name"]
        span.tags["service.version"] = self.config["service_version"]
        
        self.active_spans[span_id] = span
        self.trace_metrics.active_traces += 1
        
        try:
            # Use OpenTelemetry if available
            if self.tracer:
                with self.tracer.start_as_current_span(operation_name) as otel_span:
                    # Add tags to OpenTelemetry span
                    for key, value in span.tags.items():
                        otel_span.set_attribute(key, str(value))
                    
                    yield span
            else:
                yield span
                
        except Exception as e:
            span.finish(error=str(e))
            logger.error(f"Span error in {operation_name}: {str(e)}")
            raise
            
        finally:
            if span.status == "active":
                span.finish()
            
            # Move to completed spans
            self.active_spans.pop(span_id, None)
            self.completed_spans.append(span)
            
            # Process span
            await self._process_span(span)
            
            # Update metrics
            self._update_metrics()

    @contextmanager
    def sync_trace(
        self,
        operation_name: str,
        span_type: SpanType = SpanType.BUSINESS_LOGIC,
        tags: Optional[Dict[str, Any]] = None
    ):
        """Synchronous version of trace context manager"""
        span_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        
        span = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        span.tags["span.type"] = span_type.value
        span.tags["service.name"] = self.config["service_name"]
        
        self.active_spans[span_id] = span
        
        try:
            yield span
        except Exception as e:
            span.finish(error=str(e))
            raise
        finally:
            if span.status == "active":
                span.finish()
            
            self.active_spans.pop(span_id, None)
            self.completed_spans.append(span)

    async def _process_span(self, span: SpanContext):
        """Process completed span through processors"""
        for processor in self.processors:
            try:
                await processor(span)
            except Exception as e:
                logger.error(f"Processor error: {str(e)}")

    async def _enrich_span_processor(self, span: SpanContext):
        """Enrich span with additional metadata"""
        span.tags["timestamp"] = datetime.utcnow().isoformat()
        span.tags["environment"] = self.config["environment"]
        
        # Add resource usage if available
        try:
            import psutil
            span.tags["cpu_percent"] = psutil.cpu_percent()
            span.tags["memory_percent"] = psutil.virtual_memory().percent
        except ImportError:
            pass

    async def _performance_processor(self, span: SpanContext):
        """Process performance metrics"""
        if span.duration_ms:
            if span.duration_ms > 1000:  # Slow operation
                span.tags["performance.slow"] = True
                span.logs.append({
                    "level": "warning",
                    "message": f"Slow operation: {span.duration_ms:.2f}ms",
                    "timestamp": time.time()
                })

    async def _security_processor(self, span: SpanContext):
        """Process security-related information"""
        if span.span_id in self.active_spans:
            # Check for security-related operations
            if any(sec_tag in span.operation_name.lower() 
                   for sec_tag in ["auth", "login", "security", "encrypt"]):
                span.tags["security.sensitive"] = True

    async def _business_processor(self, span: SpanContext):
        """Process business logic metrics"""
        if "business_logic" in span.tags.get("span.type", ""):
            span.tags["business.processed"] = True

    def add_log_to_span(self, span_id: str, level: str, message: str, **kwargs):
        """Add log entry to active span"""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.logs.append({
                "level": level,
                "message": message,
                "timestamp": time.time(),
                **kwargs
            })

    def add_tag_to_span(self, span_id: str, key: str, value: Any):
        """Add tag to active span"""
        if span_id in self.active_spans:
            self.active_spans[span_id].tags[key] = value

    def _update_metrics(self):
        """Update trace metrics"""
        completed_count = len(self.completed_spans)
        if completed_count > 0:
            # Calculate averages
            durations = [s.duration_ms for s in self.completed_spans if s.duration_ms]
            if durations:
                self.trace_metrics.avg_duration_ms = sum(durations) / len(durations)
                durations.sort()
                p95_idx = int(len(durations) * 0.95)
                p99_idx = int(len(durations) * 0.99)
                self.trace_metrics.p95_duration_ms = durations[p95_idx] if p95_idx < len(durations) else 0
                self.trace_metrics.p99_duration_ms = durations[p99_idx] if p99_idx < len(durations) else 0
            
            # Error rate
            error_count = len([s for s in self.completed_spans if s.error])
            self.trace_metrics.error_rate = error_count / completed_count
            
        self.trace_metrics.total_traces = completed_count
        self.trace_metrics.active_traces = len(self.active_spans)

    def get_trace_by_id(self, trace_id: str) -> List[SpanContext]:
        """Get all spans for a trace ID"""
        return [span for span in self.completed_spans if span.trace_id == trace_id]

    def get_metrics(self) -> TraceMetrics:
        """Get current tracing metrics"""
        self._update_metrics()
        return self.trace_metrics

    def get_slow_operations(self, threshold_ms: float = 1000) -> List[SpanContext]:
        """Get operations slower than threshold"""
        return [
            span for span in self.completed_spans 
            if span.duration_ms and span.duration_ms > threshold_ms
        ]

    def get_error_traces(self) -> List[SpanContext]:
        """Get traces with errors"""
        return [span for span in self.completed_spans if span.error]

    def export_traces(self, format: str = "json") -> str:
        """Export traces in specified format"""
        if format == "json":
            traces_data = []
            for span in self.completed_spans:
                traces_data.append({
                    "traceId": span.trace_id,
                    "spanId": span.span_id,
                    "parentSpanId": span.parent_span_id,
                    "operationName": span.operation_name,
                    "startTime": span.start_time,
                    "endTime": span.end_time,
                    "duration": span.duration_ms,
                    "tags": span.tags,
                    "logs": span.logs,
                    "status": span.status,
                    "error": span.error
                })
            return json.dumps(traces_data, indent=2)
        
        return ""

    async def cleanup_old_traces(self, max_age_hours: int = 24):
        """Clean up old completed traces"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        initial_count = len(self.completed_spans)
        
        self.completed_spans = [
            span for span in self.completed_spans 
            if span.start_time > cutoff_time
        ]
        
        cleaned_count = initial_count - len(self.completed_spans)
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} old traces")

    async def health_check(self) -> bool:
        """Health check for tracing system"""
        try:
            # Check if tracing is working
            async with self.trace("health_check", SpanType.BUSINESS_LOGIC):
                pass
            
            # Check metrics
            metrics = self.get_metrics()
            
            # Check if error rate is acceptable
            if metrics.error_rate > 0.1:  # More than 10% error rate
                logger.warning(f"High error rate in traces: {metrics.error_rate:.2%}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Tracing health check failed: {str(e)}")
            return False

    def __del__(self):
        """Cleanup on destruction"""
        try:
            # Export remaining traces
            if self.completed_spans:
                logger.info(f"Exporting {len(self.completed_spans)} traces on shutdown")
        except Exception:
            pass

# Module exports
__all__ = [
    "TracingCore", "TracingLevel", "SpanType", "SpanContext", 
    "TraceMetrics"
]

logger.info("🔍 Tracing Core module loaded")