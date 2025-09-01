"""Distributed Tracing System

Advanced distributed tracing and request tracking system for the IA Influencer
platform, providing end-to-end visibility across microservices and AI operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import time
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field, asdict
from contextlib import asynccontextmanager, contextmanager
import json
import threading
from collections import defaultdict, deque
import weakref
import logging

logger = logging.getLogger(__name__)


class SpanKind(Enum):
    """
Span kinds following OpenTelemetry specification"""

    INTERNAL = "internal"       # Internal operation
    SERVER = "server"          # Server-side HTTP request
    CLIENT = "client"          # Client-side HTTP request  
    PRODUCER = "producer"      # Message producer
    CONSUMER = "consumer"      # Message consumer


class SpanStatus(Enum):
    """Span status codes"""

    UNSET = "unset"           # Default status
    OK = "ok"                 # Operation completed successfully
    ERROR = "error"           # Operation failed


@dataclass
class SpanEvent:
    """Individual event within a span"""
    name: str
    timestamp: datetime
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert span event to dictionary"""
        return {
            'name': self.name,
            'timestamp': self.timestamp.isoformat(),
            'attributes': self.attributes
        }


@dataclass
class SpanLink:
    """
Link to another span"""
    trace_id: str
    span_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert span link to dictionary"""
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'attributes': self.attributes
        }


@dataclass
class Span:
    """
    Distributed trace span representing a single operation
    
    A span represents a single operation within a trace. Spans can be nested
    to form a tree structure, representing the execution of the operation.
    """
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    kind: SpanKind
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: SpanStatus = SpanStatus.UNSET
    status_message: Optional[str] = None
    
    # Metadata
    service_name: str = "ia_influencer_platform"
    service_version: str = "1.0.0"
    
    # Attributes (tags)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Events and links
    events: List[SpanEvent] = field(default_factory=list)
    links: List[SpanLink] = field(default_factory=list)
    
    # Resource attributes
    resource: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.start_time.tzinfo is None:
            self.start_time = self.start_time.replace(tzinfo=timezone.utc)
        
        # Set default resource attributes
        if not self.resource:
            self.resource = {
                'service.name': self.service_name,
                'service.version': self.service_version,
                'platform': 'ia_influencer_agent'
            }
    
    def finish(self, status: SpanStatus = SpanStatus.OK, status_message: Optional[str] = None):
        """
Finish the span"""
        if self.end_time is None:
            self.end_time = datetime.now(timezone.utc)
            self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        
        self.status = status
        if status_message:
            self.status_message = status_message
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
Add an event to the span"""
        event = SpanEvent(
            name=name,
            timestamp=datetime.now(timezone.utc),
            attributes=attributes or {}
        )
        self.events.append(event)
    
    def add_link(self, trace_id: str, span_id: str, attributes: Optional[Dict[str, Any]] = None):
        """
Add a link to another span"""
        link = SpanLink(
            trace_id=trace_id,
            span_id=span_id,
            attributes=attributes or {}
        )
        self.links.append(link)
    
    def set_attribute(self, key: str, value: Any):
        """
Set a span attribute"""
        self.attributes[key] = value
    
    def set_attributes(self, attributes: Dict[str, Any]):
        """
Set multiple span attributes"""
        self.attributes.update(attributes)
    
    def record_exception(self, exception: Exception):
        """
Record an exception in the span"""
        self.status = SpanStatus.ERROR
        self.status_message = str(exception)
        
        self.add_event(
            name="exception",
            attributes={
                'exception.type': type(exception).__name__,
                'exception.message': str(exception),
                'exception.stacktrace': self._format_exception(exception)
            }
        )
    
    def _format_exception(self, exception: Exception) -> str:
        """Format exception for logging"""
        import traceback
        return ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert span to dictionary"""
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id,
            'operation_name': self.operation_name,
            'kind': self.kind.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_ms': self.duration_ms,
            'status': self.status.value,
            'status_message': self.status_message,
            'service_name': self.service_name,
            'service_version': self.service_version,
            'attributes': self.attributes,
            'events': [event.to_dict() for event in self.events],
            'links': [link.to_dict() for link in self.links],
            'resource': self.resource
        }
    
    def to_json(self) -> str:
        """
Convert span to JSON string"""
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)


@dataclass
class Trace:
    """
Collection of spans forming a complete trace"""
    trace_id: str
    spans: List[Span] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    
    def add_span(self, span: Span):
        """
Add a span to the trace"""
        self.spans.append(span)
        
        # Update trace timing
        if self.start_time is None or span.start_time < self.start_time:
            self.start_time = span.start_time
        
        if span.end_time:
            if self.end_time is None or span.end_time > self.end_time:
                self.end_time = span.end_time
        
        # Calculate duration
        if self.start_time and self.end_time:
            self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
    
    def get_root_spans(self) -> List[Span]:
        """
Get root spans (spans without parents)"""
        return [span for span in self.spans if span.parent_span_id is None]
    
    def get_span_children(self, span_id: str) -> List[Span]:
        """
Get child spans of a given span"""
        return [span for span in self.spans if span.parent_span_id == span_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert trace to dictionary"""
        return {
            'trace_id': self.trace_id,
            'spans': [span.to_dict() for span in self.spans],
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_ms': self.duration_ms,
            'span_count': len(self.spans)
        }


class SpanContext:
    """
    Thread-local storage for current span context
    """
    
    def __init__(self):
        self._local = threading.local()
    
    def get_current_span(self) -> Optional[Span]:
        """
Get the current active span"""
        return getattr(self._local, 'current_span', None)
    
    def set_current_span(self, span: Optional[Span]):
        """
Set the current active span"""
        self._local.current_span = span
    
    def get_trace_id(self) -> Optional[str]:
        """
Get the current trace ID"""
        span = self.get_current_span()
        return span.trace_id if span else None
    
    def get_span_id(self) -> Optional[str]:
        """
Get the current span ID"""
        span = self.get_current_span()
        return span.span_id if span else None


# Global span context
_span_context = SpanContext()


class SpanManager:
    """
    Manager for creating and managing spans
    
    Features:
    - Span lifecycle management
    - Context propagation
    - Automatic parent-child relationships
    - Span sampling
    - Export to tracing backends
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize span manager"""
        self.config = config or {}
        
        # Sampling configuration
        self.sampling_rate = self.config.get('sampling_rate', 1.0)  # 100% by default
        self.max_spans_per_trace = self.config.get('max_spans_per_trace', 1000)
        
        # Storage
        self.active_traces: Dict[str, Trace] = {}
        self.completed_traces: deque = deque(maxlen=self.config.get('max_completed_traces', 10000))
        
        # Exporters
        self.exporters: List[Any] = []
        
        # Background processing
        self.export_interval = self.config.get('export_interval', 30)  # seconds
        self.is_exporting = False
        self.export_task = None
        
        # Metrics
        self.metrics = {
            'spans_created': 0,
            'spans_exported': 0,
            'traces_completed': 0,
            'export_errors': 0
        }
    
    def create_span(self, 
                   operation_name: str,
                   kind: SpanKind = SpanKind.INTERNAL,
                   parent_span: Optional[Span] = None,
                   attributes: Optional[Dict[str, Any]] = None) -> Span:
        """
Create a new span"""
        
        # Get parent context
        if parent_span is None:
            parent_span = _span_context.get_current_span()
        
        # Generate IDs
        if parent_span:
            trace_id = parent_span.trace_id
            parent_span_id = parent_span.span_id
        else:
            trace_id = self._generate_trace_id()
            parent_span_id = None
        
        span_id = self._generate_span_id()
        
        # Check sampling
        if not self._should_sample(trace_id):
            # Return a no-op span
            return NoOpSpan()
        
        # Create span
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            kind=kind,
            start_time=datetime.now(timezone.utc)
        )
        
        # Set attributes
        if attributes:
            span.set_attributes(attributes)
        
        # Add to trace
        self._add_span_to_trace(span)
        
        # Update metrics
        self.metrics['spans_created'] += 1
        
        return span
    
    def _generate_trace_id(self) -> str:
        """
Generate a new trace ID"""
        return uuid.uuid4().hex
    
    def _generate_span_id(self) -> str:
        """
Generate a new span ID"""
        return uuid.uuid4().hex[:16]
    
    def _should_sample(self, trace_id: str) -> bool:
        """
Determine if trace should be sampled"""
        if self.sampling_rate >= 1.0:
            return True
        
        if self.sampling_rate <= 0.0:
            return False
        
        # Use trace ID for consistent sampling
        hash_value = hash(trace_id) % 1000000
        threshold = int(self.sampling_rate * 1000000)
        return hash_value < threshold
    
    def _add_span_to_trace(self, span: Span):
        """
Add span to its trace"""
        trace_id = span.trace_id
        
        if trace_id not in self.active_traces:
            self.active_traces[trace_id] = Trace(trace_id=trace_id)
        
        trace = self.active_traces[trace_id]
        
        # Check span limit
        if len(trace.spans) >= self.max_spans_per_trace:
            logger.warning(f"Trace {trace_id} exceeded maximum spans limit")
            return
        
        trace.add_span(span)
    
    def finish_span(self, span: Span, status: SpanStatus = SpanStatus.OK, 
                   status_message: Optional[str] = None):
        """Finish a span"""
        if isinstance(span, NoOpSpan):
            return
        
        span.finish(status, status_message)
        
        # Check if trace is complete
        trace = self.active_traces.get(span.trace_id)
        if trace and self._is_trace_complete(trace):
            self._complete_trace(trace)
    
    def _is_trace_complete(self, trace: Trace) -> bool:
        """
Check if all spans in trace are completed"""
        for span in trace.spans:
            if span.end_time is None:
                return False
        return True
    
    def _complete_trace(self, trace: Trace):
        """
Mark trace as complete and move to completed traces"""
        trace_id = trace.trace_id
        
        if trace_id in self.active_traces:
            del self.active_traces[trace_id]
        
        self.completed_traces.append(trace)
        self.metrics['traces_completed'] += 1
        
        # Schedule for export
        if self.exporters and not self.is_exporting:
            asyncio.create_task(self._export_traces())
    
    async def _export_traces(self):
        """
Export completed traces to backends"""
        if self.is_exporting:
            return
        
        self.is_exporting = True
        
        try:
            # Get traces to export
            traces_to_export = []
            while self.completed_traces and len(traces_to_export) < 100:
                traces_to_export.append(self.completed_traces.popleft())
            
            if not traces_to_export:
                return
            
            # Export to all configured exporters
            for exporter in self.exporters:
                try:
                    await self._export_to_backend(exporter, traces_to_export)
                    self.metrics['spans_exported'] += sum(len(trace.spans) for trace in traces_to_export)
                except Exception as e:
                    self.metrics['export_errors'] += 1
                    logger.error(f"Failed to export traces to {type(exporter).__name__}: {str(e)}")
        
        finally:
            self.is_exporting = False
    
    async def _export_to_backend(self, exporter: Any, traces: List[Trace]):
        """Export traces to a specific backend"""
        # This would be implemented based on the specific exporter
        # (Jaeger, Zipkin, OpenTelemetry Collector, etc.)
        pass
    
    def add_exporter(self, exporter: Any):
        """
Add a trace exporter"""
        self.exporters.append(exporter)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
Get tracing metrics"""
        return {
            **self.metrics,
            'active_traces': len(self.active_traces),
            'completed_traces': len(self.completed_traces),
            'sampling_rate': self.sampling_rate
        }


class NoOpSpan(Span):
    """
No-operation span for when sampling is disabled"""
    
    def __init__(self):
        # Initialize with minimal data
        super().__init__(
            trace_id="",
            span_id="",
            parent_span_id=None,
            operation_name="",
            kind=SpanKind.INTERNAL,
            start_time=datetime.now(timezone.utc)
        )
    
    def finish(self, status: SpanStatus = SpanStatus.OK, status_message: Optional[str] = None):
        """No-op finish"""
        pass
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
No-op add event"""
        pass
    
    def set_attribute(self, key: str, value: Any):
        """
No-op set attribute"""
        pass
    
    def set_attributes(self, attributes: Dict[str, Any]):
        """
No-op set attributes"""
        pass
    
    def record_exception(self, exception: Exception):
        """
No-op record exception"""
        pass


class DistributedTracer:
    """
    Main distributed tracer class providing high-level tracing API
    
    Features:
    - Automatic trace context management
    - Span lifecycle management
    - Cross-service trace propagation
    - Performance monitoring integration
    - Business logic tracing
    """
    
    def __init__(self, service_name: str, config: Optional[Dict[str, Any]] = None):
        """
Initialize distributed tracer"""
        self.service_name = service_name
        self.config = config or {}
        
        # Initialize span manager
        self.span_manager = SpanManager(config)
        
        # Service metadata
        self.service_version = self.config.get('service_version', '1.0.0')
        self.service_namespace = self.config.get('service_namespace', 'ia_influencer')
        
        # Instrumentation settings
        self.auto_instrument = self.config.get('auto_instrument', True)
        self.trace_http_requests = self.config.get('trace_http_requests', True)
        self.trace_database_queries = self.config.get('trace_database_queries', True)
        self.trace_ai_operations = self.config.get('trace_ai_operations', True)
        
        logger.info(f"Distributed tracer initialized for service: {service_name}")
    
    def start_span(self, 
                   operation_name: str,
                   kind: SpanKind = SpanKind.INTERNAL,
                   parent: Optional[Span] = None,
                   attributes: Optional[Dict[str, Any]] = None) -> Span:
        """Start a new span"""
        
        # Add service attributes
        span_attributes = {
            'service.name': self.service_name,
            'service.version': self.service_version,
            'service.namespace': self.service_namespace
        }
        
        if attributes:
            span_attributes.update(attributes)
        
        span = self.span_manager.create_span(
            operation_name=operation_name,
            kind=kind,
            parent_span=parent,
            attributes=span_attributes
        )
        
        return span
    
    def start_active_span(self, 
                         operation_name: str,
                         kind: SpanKind = SpanKind.INTERNAL,
                         attributes: Optional[Dict[str, Any]] = None):
        """
Start a new active span (sets as current span)"""
        
        span = self.start_span(operation_name, kind, attributes=attributes)
        _span_context.set_current_span(span)
        
        return span
    
    def get_current_span(self) -> Optional[Span]:
        """
Get the current active span"""
        return _span_context.get_current_span()
    
    def get_current_trace_id(self) -> Optional[str]:
        """
Get the current trace ID"""
        return _span_context.get_trace_id()
    
    def finish_span(self, span: Span, status: SpanStatus = SpanStatus.OK, 
                   status_message: Optional[str] = None):
        """
Finish a span"""
        self.span_manager.finish_span(span, status, status_message)
        
        # Clear current span if it's this one
        current_span = _span_context.get_current_span()
        if current_span and current_span.span_id == span.span_id:
            # Set parent as current if exists
            parent_span = self._find_parent_span(span)
            _span_context.set_current_span(parent_span)
    
    def _find_parent_span(self, span: Span) -> Optional[Span]:
        """
Find parent span of given span"""
        if not span.parent_span_id:
            return None
        
        # Look for parent in active traces
        trace = self.span_manager.active_traces.get(span.trace_id)
        if not trace:
            return None
        
        for trace_span in trace.spans:
            if trace_span.span_id == span.parent_span_id:
                return trace_span
        
        return None
    
    @contextmanager
    def span(self, 
             operation_name: str,
             kind: SpanKind = SpanKind.INTERNAL,
             attributes: Optional[Dict[str, Any]] = None):
        """
Context manager for span lifecycle"""
        
        span = self.start_active_span(operation_name, kind, attributes)
        
        try:
            yield span
            self.finish_span(span, SpanStatus.OK)
        except Exception as e:
            span.record_exception(e)
            self.finish_span(span, SpanStatus.ERROR, str(e))
            raise
    
    @asynccontextmanager
    async def async_span(self, 
                        operation_name: str,
                        kind: SpanKind = SpanKind.INTERNAL,
                        attributes: Optional[Dict[str, Any]] = None):
        """
Async context manager for span lifecycle"""
        
        span = self.start_active_span(operation_name, kind, attributes)
        
        try:
            yield span
            self.finish_span(span, SpanStatus.OK)
        except Exception as e:
            span.record_exception(e)
            self.finish_span(span, SpanStatus.ERROR, str(e))
            raise
    
    def trace_function(self, 
                      operation_name: Optional[str] = None,
                      kind: SpanKind = SpanKind.INTERNAL,
                      attributes: Optional[Dict[str, Any]] = None):
        """
Decorator for tracing functions"""
        
        def decorator(func):
            func_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper(*args, **kwargs):
                    async with self.async_span(func_name, kind, attributes) as span:
                        # Add function metadata
                        span.set_attributes({
                            'function.name': func.__name__,
                            'function.module': func.__module__,
                            'function.args_count': len(args),
                            'function.kwargs_count': len(kwargs)
                        })
                        
                        start_time = time.time()
                        try:
                            result = await func(*args, **kwargs)
                            duration = (time.time() - start_time) * 1000
                            span.set_attribute('function.duration_ms', duration)
                            return result
                        except Exception as e:
                            span.record_exception(e)
                            raise
                
                return async_wrapper
            else:
                def wrapper(*args, **kwargs):
                    with self.span(func_name, kind, attributes) as span:
                        # Add function metadata
                        span.set_attributes({
                            'function.name': func.__name__,
                            'function.module': func.__module__,
                            'function.args_count': len(args),
                            'function.kwargs_count': len(kwargs)
                        })
                        
                        start_time = time.time()
                        try:
                            result = func(*args, **kwargs)
                            duration = (time.time() - start_time) * 1000
                            span.set_attribute('function.duration_ms', duration)
                            return result
                        except Exception as e:
                            span.record_exception(e)
                            raise
                
                return wrapper
        
        return decorator
    
    def trace_ai_operation(self, 
                          model_name: str,
                          operation_type: str,
                          input_size: Optional[int] = None,
                          attributes: Optional[Dict[str, Any]] = None):
        """Trace AI/ML operations"""
        
        operation_name = f"ai.{operation_type}"
        ai_attributes = {
            'ai.model.name': model_name,
            'ai.operation.type': operation_type,
            'ai.service': self.service_name
        }
        
        if input_size is not None:
            ai_attributes['ai.input.size'] = input_size
        
        if attributes:
            ai_attributes.update(attributes)
        
        return self.span(operation_name, SpanKind.INTERNAL, ai_attributes)
    
    def trace_content_protection(self, 
                               content_type: str,
                               protection_method: str,
                               content_id: Optional[str] = None,
                               attributes: Optional[Dict[str, Any]] = None):
        """Trace content protection operations"""
        
        operation_name = f"content_protection.{protection_method}"
        protection_attributes = {
            'content.type': content_type,
            'content.protection.method': protection_method,
            'content.service': 'ia_influencer_protection'
        }
        
        if content_id:
            protection_attributes['content.id'] = content_id
        
        if attributes:
            protection_attributes.update(attributes)
        
        return self.span(operation_name, SpanKind.INTERNAL, protection_attributes)
    
    def trace_user_action(self, 
                         user_id: str,
                         action: str,
                         resource: Optional[str] = None,
                         attributes: Optional[Dict[str, Any]] = None):
        """Trace user actions"""
        
        operation_name = f"user.{action}"
        user_attributes = {
            'user.id': user_id,
            'user.action': action,
            'user.service': self.service_name
        }
        
        if resource:
            user_attributes['user.resource'] = resource
        
        if attributes:
            user_attributes.update(attributes)
        
        return self.span(operation_name, SpanKind.SERVER, user_attributes)
    
    def inject_trace_context(self, carrier: Dict[str, str]):
        """Inject trace context into carrier for cross-service propagation"""
        
        current_span = self.get_current_span()
        if not current_span:
            return
        
        # W3C Trace Context format
        carrier['traceparent'] = f"00-{current_span.trace_id}-{current_span.span_id}-01"
        
        # Custom headers for additional context
        carrier['x-trace-id'] = current_span.trace_id
        carrier['x-span-id'] = current_span.span_id
        carrier['x-service-name'] = self.service_name
    
    def extract_trace_context(self, carrier: Dict[str, str]) -> Optional[Span]:
        """Extract trace context from carrier"""
        
        # Try W3C Trace Context first
        traceparent = carrier.get('traceparent')
        if traceparent:
            try:
                parts = traceparent.split('-')
                if len(parts) >= 4:
                    trace_id = parts[1]
                    parent_span_id = parts[2]
                    
                    # Create span context (not a real span, just context)
                    return self._create_span_context(trace_id, parent_span_id)
            except Exception as e:
                logger.warning(f"Failed to parse traceparent: {str(e)}")
        
        # Try custom headers
        trace_id = carrier.get('x-trace-id')
        span_id = carrier.get('x-span-id')
        
        if trace_id and span_id:
            return self._create_span_context(trace_id, span_id)
        
        return None
    
    def _create_span_context(self, trace_id: str, parent_span_id: str) -> Span:
        """Create a span context for remote parent"""
        
        # Create a minimal span representing remote parent
        remote_span = Span(
            trace_id=trace_id,
            span_id=parent_span_id,
            parent_span_id=None,
            operation_name="remote_parent",
            kind=SpanKind.INTERNAL,
            start_time=datetime.now(timezone.utc)
        )
        
        # Mark as remote
        remote_span.set_attribute('span.remote', True)
        
        return remote_span
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get tracing metrics"""
        return self.span_manager.get_metrics()


class TraceAnalyzer:
    """
    Advanced trace analysis system for performance insights
    and anomaly detection in distributed traces.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize trace analyzer"""
        self.config = config or {}
        
        # Analysis configuration
        self.analysis_window = self.config.get('analysis_window', 3600)  # 1 hour
        self.slow_operation_threshold = self.config.get('slow_operation_threshold', 1000)  # ms
        self.error_rate_threshold = self.config.get('error_rate_threshold', 0.05)  # 5%
        
        # Storage for analysis
        self.trace_buffer: List[Trace] = []
        self.operation_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0,
            'error_count': 0,
            'min_duration': float('inf'),
            'max_duration': 0,
            'durations': deque(maxlen=1000)
        })
        
        # Analysis results
        self.performance_insights: List[Dict[str, Any]] = []
        self.anomalies: List[Dict[str, Any]] = []
    
    async def analyze_traces(self, traces: List[Trace]) -> Dict[str, Any]:
        """
Analyze a batch of traces"""
        
        try:
            analysis_results = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analyzed_traces': len(traces),
                'total_spans': sum(len(trace.spans) for trace in traces),
                'performance_insights': [],
                'anomalies': [],
                'operation_stats': {},
                'recommendations': []
            }
            
            # Update operation statistics
            self._update_operation_stats(traces)
            
            # Performance analysis
            performance_insights = await self._analyze_performance(traces)
            analysis_results['performance_insights'] = performance_insights
            
            # Anomaly detection
            anomalies = await self._detect_trace_anomalies(traces)
            analysis_results['anomalies'] = anomalies
            
            # Generate operation statistics
            operation_stats = self._generate_operation_stats()
            analysis_results['operation_stats'] = operation_stats
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(analysis_results)
            analysis_results['recommendations'] = recommendations
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Failed to analyze traces: {str(e)}")
            return {}
    
    def _update_operation_stats(self, traces: List[Trace]):
        """Update operation statistics with new traces"""
        
        for trace in traces:
            for span in trace.spans:
                operation = span.operation_name
                stats = self.operation_stats[operation]
                
                # Update counters
                stats['count'] += 1
                
                if span.duration_ms is not None:
                    duration = span.duration_ms
                    stats['total_duration'] += duration
                    stats['min_duration'] = min(stats['min_duration'], duration)
                    stats['max_duration'] = max(stats['max_duration'], duration)
                    stats['durations'].append(duration)
                
                # Count errors
                if span.status == SpanStatus.ERROR:
                    stats['error_count'] += 1
    
    async def _analyze_performance(self, traces: List[Trace]) -> List[Dict[str, Any]]:
        """
Analyze performance characteristics of traces"""
        
        insights = []
        
        try:
            # Analyze slow operations
            slow_operations = []
            for operation, stats in self.operation_stats.items():
                if stats['count'] > 0 and stats['total_duration'] > 0:
                    avg_duration = stats['total_duration'] / stats['count']
                    if avg_duration > self.slow_operation_threshold:
                        slow_operations.append({
                            'operation': operation,
                            'avg_duration_ms': avg_duration,
                            'count': stats['count'],
                            'max_duration_ms': stats['max_duration']
                        })
            
            if slow_operations:
                insights.append({
                    'type': 'slow_operations',
                    'message': f"Found {len(slow_operations)} slow operations",
                    'operations': slow_operations
                })
            
            # Analyze error rates
            high_error_operations = []
            for operation, stats in self.operation_stats.items():
                if stats['count'] > 10:  # Minimum sample size
                    error_rate = stats['error_count'] / stats['count']
                    if error_rate > self.error_rate_threshold:
                        high_error_operations.append({
                            'operation': operation,
                            'error_rate': error_rate,
                            'error_count': stats['error_count'],
                            'total_count': stats['count']
                        })
            
            if high_error_operations:
                insights.append({
                    'type': 'high_error_rates',
                    'message': f"Found {len(high_error_operations)} operations with high error rates",
                    'operations': high_error_operations
                })
            
            # Analyze trace duration distribution
            trace_durations = [trace.duration_ms for trace in traces if trace.duration_ms]
            if trace_durations:
                avg_duration = sum(trace_durations) / len(trace_durations)
                max_duration = max(trace_durations)
                
                insights.append({
                    'type': 'trace_duration_analysis',
                    'message': f"Analyzed {len(trace_durations)} complete traces",
                    'avg_duration_ms': avg_duration,
                    'max_duration_ms': max_duration,
                    'trace_count': len(trace_durations)
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to analyze performance: {str(e)}")
            return []
    
    async def _detect_trace_anomalies(self, traces: List[Trace]) -> List[Dict[str, Any]]:
        """Detect anomalies in traces"""
        
        anomalies = []
        
        try:
            # Detect unusually long traces
            if traces:
                trace_durations = [t.duration_ms for t in traces if t.duration_ms]
                if trace_durations:
                    avg_duration = sum(trace_durations) / len(trace_durations)
                    
                    for trace in traces:
                        if trace.duration_ms and trace.duration_ms > avg_duration * 3:
                            anomalies.append({
                                'type': 'unusually_long_trace',
                                'trace_id': trace.trace_id,
                                'duration_ms': trace.duration_ms,
                                'avg_duration_ms': avg_duration,
                                'severity': 'medium'
                            })
            
            # Detect traces with many errors
            for trace in traces:
                error_spans = [span for span in trace.spans if span.status == SpanStatus.ERROR]
                if len(error_spans) > len(trace.spans) * 0.3:  # More than 30% errors
                    anomalies.append({
                        'type': 'high_error_trace',
                        'trace_id': trace.trace_id,
                        'error_span_count': len(error_spans),
                        'total_span_count': len(trace.spans),
                        'error_rate': len(error_spans) / len(trace.spans),
                        'severity': 'high'
                    })
            
            # Detect traces with unusual span counts
            if traces:
                span_counts = [len(trace.spans) for trace in traces]
                avg_span_count = sum(span_counts) / len(span_counts)
                
                for trace in traces:
                    if len(trace.spans) > avg_span_count * 5:  # 5x more spans than average
                        anomalies.append({
                            'type': 'unusual_span_count',
                            'trace_id': trace.trace_id,
                            'span_count': len(trace.spans),
                            'avg_span_count': avg_span_count,
                            'severity': 'low'
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect trace anomalies: {str(e)}")
            return []
    
    def _generate_operation_stats(self) -> Dict[str, Any]:
        """Generate operation statistics summary"""
        
        stats_summary = {}
        
        for operation, stats in self.operation_stats.items():
            if stats['count'] > 0:
                avg_duration = stats['total_duration'] / stats['count'] if stats['total_duration'] > 0 else 0
                error_rate = stats['error_count'] / stats['count']
                
                # Calculate percentiles if we have duration data
                percentiles = {}
                if stats['durations']:
                    durations = sorted(stats['durations'])
                    percentiles = {
                        'p50': self._calculate_percentile(durations, 0.5),
                        'p90': self._calculate_percentile(durations, 0.9),
                        'p95': self._calculate_percentile(durations, 0.95),
                        'p99': self._calculate_percentile(durations, 0.99)
                    }
                
                stats_summary[operation] = {
                    'count': stats['count'],
                    'error_count': stats['error_count'],
                    'error_rate': error_rate,
                    'avg_duration_ms': avg_duration,
                    'min_duration_ms': stats['min_duration'] if stats['min_duration'] != float('inf') else None,
                    'max_duration_ms': stats['max_duration'],
                    'percentiles': percentiles
                }
        
        return stats_summary
    
    def _calculate_percentile(self, sorted_values: List[float], percentile: float) -> float:
        """
Calculate percentile from sorted values"""
        if not sorted_values:
            return 0.0
        
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    async def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Generate recommendations based on trace analysis"""
        
        recommendations = []
        
        try:
            # Performance recommendations
            performance_insights = analysis_results.get('performance_insights', [])
            for insight in performance_insights:
                if insight.get('type') == 'slow_operations':
                    recommendations.append({
                        'type': 'performance_optimization',
                        'priority': 'high',
                        'message': 'Optimize slow operations detected',
                        'action': 'investigate_slow_operations',
                        'operations': [op['operation'] for op in insight.get('operations', [])]
                    })
                
                elif insight.get('type') == 'high_error_rates':
                    recommendations.append({
                        'type': 'error_investigation',
                        'priority': 'critical',
                        'message': 'High error rates detected - immediate attention required',
                        'action': 'investigate_errors',
                        'operations': [op['operation'] for op in insight.get('operations', [])]
                    })
            
            # Anomaly recommendations
            anomalies = analysis_results.get('anomalies', [])
            high_severity_anomalies = [a for a in anomalies if a.get('severity') == 'high']
            if high_severity_anomalies:
                recommendations.append({
                    'type': 'anomaly_investigation',
                    'priority': 'high',
                    'message': f'Found {len(high_severity_anomalies)} high-severity trace anomalies',
                    'action': 'investigate_anomalies',
                    'trace_ids': [a.get('trace_id') for a in high_severity_anomalies]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return []


class RequestTracker:
    """
    HTTP request tracking and correlation system
    """
    
    def __init__(self, tracer: DistributedTracer):
        """
Initialize request tracker"""
        self.tracer = tracer
        self.active_requests: Dict[str, Dict[str, Any]] = {}
    
    def start_request_tracking(self, 
                              request_id: str,
                              method: str,
                              url: str,
                              headers: Optional[Dict[str, str]] = None) -> Span:
        """
Start tracking an HTTP request"""
        
        # Extract trace context from headers if present
        parent_span = None
        if headers:
            parent_span = self.tracer.extract_trace_context(headers)
        
        # Create request span
        span = self.tracer.start_span(
            f"HTTP {method}",
            kind=SpanKind.SERVER,
            parent=parent_span,
            attributes={
                'http.method': method,
                'http.url': url,
                'http.request_id': request_id
            }
        )
        
        # Track request
        self.active_requests[request_id] = {
            'span': span,
            'start_time': time.time(),
            'method': method,
            'url': url
        }
        
        # Set as current span
        _span_context.set_current_span(span)
        
        return span
    
    def finish_request_tracking(self, 
                               request_id: str,
                               status_code: int,
                               response_size: Optional[int] = None):
        """Finish tracking an HTTP request"""
        
        request_info = self.active_requests.get(request_id)
        if not request_info:
            return
        
        span = request_info['span']
        
        # Add response attributes
        span.set_attributes({
            'http.status_code': status_code,
            'http.status_class': f"{status_code // 100}xx"
        })
        
        if response_size is not None:
            span.set_attribute('http.response_size_bytes', response_size)
        
        # Determine status
        if 400 <= status_code < 600:
            status = SpanStatus.ERROR
            status_message = f"HTTP {status_code}"
        else:
            status = SpanStatus.OK
            status_message = None
        
        # Finish span
        self.tracer.finish_span(span, status, status_message)
        
        # Remove from active requests
        del self.active_requests[request_id]


class PerformanceTracer:
    """
    Performance-focused tracing for detailed performance analysis
    """
    
    def __init__(self, tracer: DistributedTracer):
        """
Initialize performance tracer"""
        self.tracer = tracer
        self.performance_data: Dict[str, List[float]] = defaultdict(list)
    
    def trace_performance_critical_operation(self, 
                                           operation_name: str,
                                           threshold_ms: float = 100):
        """
Trace performance-critical operations with detailed metrics"""
        
        @contextmanager
        def performance_span():
            span = self.tracer.start_active_span(
                f"perf.{operation_name}",
                attributes={
                    'performance.critical': True,
                    'performance.threshold_ms': threshold_ms
                }
            )
            
            start_time = time.perf_counter()
            
            try:
                yield span
                
                # Calculate performance metrics
                duration = (time.perf_counter() - start_time) * 1000
                self.performance_data[operation_name].append(duration)
                
                # Add performance attributes
                span.set_attributes({
                    'performance.duration_ms': duration,
                    'performance.exceeded_threshold': duration > threshold_ms
                })
                
                # Add performance event
                if duration > threshold_ms:
                    span.add_event(
                        'performance_threshold_exceeded',
                        {
                            'threshold_ms': threshold_ms,
                            'actual_duration_ms': duration,
                            'exceeded_by_ms': duration - threshold_ms
                        }
                    )
                
                self.tracer.finish_span(span, SpanStatus.OK)
                
            except Exception as e:
                span.record_exception(e)
                self.tracer.finish_span(span, SpanStatus.ERROR, str(e))
                raise
        
        return performance_span()
    
    def get_performance_summary(self, operation_name: str) -> Dict[str, Any]:
        """Get performance summary for an operation"""
        
        durations = self.performance_data.get(operation_name, [])
        if not durations:
            return {}
        
        return {
            'operation': operation_name,
            'sample_count': len(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'avg_duration_ms': sum(durations) / len(durations),
            'p50_duration_ms': sorted(durations)[len(durations) // 2],
            'p95_duration_ms': sorted(durations)[int(len(durations) * 0.95)],
            'p99_duration_ms': sorted(durations)[int(len(durations) * 0.99)]
        }


class AIOperationTracer:
    """
    Specialized tracer for AI/ML operations with model-specific tracking
    """
    
    def __init__(self, tracer: DistributedTracer):
        """
Initialize AI operation tracer"""
        self.tracer = tracer
        self.model_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'inference_count': 0,
            'total_inference_time': 0,
            'error_count': 0,
            'input_sizes': [],
            'output_sizes': []
        })
    
    def trace_model_inference(self, 
                             model_name: str,
                             model_version: str,
                             input_shape: Optional[tuple] = None,
                             batch_size: int = 1):
        """
Trace AI model inference operations"""
        
        @contextmanager
        def inference_span():
            span = self.tracer.start_active_span(
                f"ai.inference.{model_name}",
                attributes={
                    'ai.model.name': model_name,
                    'ai.model.version': model_version,
                    'ai.operation.type': 'inference',
                    'ai.batch_size': batch_size
                }
            )
            
            if input_shape:
                span.set_attribute('ai.input.shape', str(input_shape))
                span.set_attribute('ai.input.size', input_shape[0] if input_shape else 0)
            
            start_time = time.perf_counter()
            
            try:
                yield span
                
                # Calculate metrics
                inference_time = (time.perf_counter() - start_time) * 1000
                
                # Update model metrics
                metrics = self.model_metrics[model_name]
                metrics['inference_count'] += 1
                metrics['total_inference_time'] += inference_time
                
                if input_shape:
                    metrics['input_sizes'].append(input_shape[0] if input_shape else 0)
                
                # Add inference metrics to span
                span.set_attributes({
                    'ai.inference.duration_ms': inference_time,
                    'ai.inference.throughput': batch_size / (inference_time / 1000) if inference_time > 0 else 0
                })
                
                # Performance event for slow inferences
                if inference_time > 5000:  # 5 seconds
                    span.add_event(
                        'slow_inference_detected',
                        {
                            'duration_ms': inference_time,
                            'model_name': model_name,
                            'batch_size': batch_size
                        }
                    )
                
                self.tracer.finish_span(span, SpanStatus.OK)
                
            except Exception as e:
                metrics = self.model_metrics[model_name]
                metrics['error_count'] += 1
                
                span.record_exception(e)
                self.tracer.finish_span(span, SpanStatus.ERROR, str(e))
                raise
        
        return inference_span()
    
    def trace_model_training(self, 
                           model_name: str,
                           epoch: int,
                           batch_count: int):
        """Trace model training operations"""
        
        return self.tracer.span(
            f"ai.training.{model_name}",
            attributes={
                'ai.model.name': model_name,
                'ai.operation.type': 'training',
                'ai.training.epoch': epoch,
                'ai.training.batch_count': batch_count
            }
        )
    
    def trace_data_preprocessing(self, 
                               dataset_name: str,
                               operation: str,
                               record_count: int):
        """Trace data preprocessing operations"""
        
        return self.tracer.span(
            f"ai.preprocessing.{operation}",
            attributes={
                'ai.dataset.name': dataset_name,
                'ai.operation.type': 'preprocessing',
                'ai.preprocessing.operation': operation,
                'ai.data.record_count': record_count
            }
        )
    
    def get_model_performance_summary(self, model_name: str) -> Dict[str, Any]:
        """Get performance summary for a specific model"""
        
        metrics = self.model_metrics.get(model_name, {})
        if not metrics or metrics['inference_count'] == 0:
            return {}
        
        avg_inference_time = metrics['total_inference_time'] / metrics['inference_count']
        error_rate = metrics['error_count'] / metrics['inference_count']
        
        return {
            'model_name': model_name,
            'inference_count': metrics['inference_count'],
            'error_count': metrics['error_count'],
            'error_rate': error_rate,
            'avg_inference_time_ms': avg_inference_time,
            'total_inference_time_ms': metrics['total_inference_time'],
            'avg_input_size': sum(metrics['input_sizes']) / len(metrics['input_sizes']) if metrics['input_sizes'] else 0
        }


# Factory functions for creating tracers
def create_tracer(service_name: str, config: Optional[Dict[str, Any]] = None) -> DistributedTracer:
    """
Factory function for creating distributed tracers"""
    return DistributedTracer(service_name, config)


def create_request_tracker(tracer: DistributedTracer) -> RequestTracker:
    """
Factory function for creating request trackers"""
    return RequestTracker(tracer)


def create_performance_tracer(tracer: DistributedTracer) -> PerformanceTracer:
    """
Factory function for creating performance tracers"""
    return PerformanceTracer(tracer)


def create_ai_operation_tracer(tracer: DistributedTracer) -> AIOperationTracer:
    """
Factory function for creating AI operation tracers"""
    return AIOperationTracer(tracer)


# Global tracer instance
_global_tracer: Optional[DistributedTracer] = None


def get_global_tracer() -> Optional[DistributedTracer]:
    """
Get the global tracer instance"""
    return _global_tracer


def set_global_tracer(tracer: DistributedTracer):
    """
Set the global tracer instance"""
    global _global_tracer
    _global_tracer = tracer


def trace(operation_name: str, **kwargs):
    """
Convenient function for tracing with global tracer"""
    tracer = get_global_tracer()
    if not tracer:
        # Return a no-op context manager if no tracer is set
        @contextmanager
        def noop():
            yield
        return noop()
    
    return tracer.span(operation_name, **kwargs)
