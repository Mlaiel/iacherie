"""
Enterprise Distributed Tracing System

Advanced distributed tracing infrastructure for request flow monitoring,
performance analysis, and dependency tracking in the IA Influencer platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + Security

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, copying, or implementation without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""

import uuid
import time
import threading
import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from contextlib import contextmanager, asynccontextmanager
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class SpanKind(Enum):
    """Span kind definitions."""
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class SpanStatus(Enum):
    """Span status definitions."""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class SpanTag:
    """Structured span tag."""
    key: str
    value: Any
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class SpanLog:
    """Structured span log entry."""
    timestamp: datetime
    level: str
    message: str
    fields: Dict[str, Any] = None

    def __post_init__(self):
        if self.fields is None:
            self.fields = {}


class Span:
    """Enhanced span with rich metadata and context tracking."""
    
    def __init__(self, 
                 name: str, 
                 trace_id: str, 
                 parent_id: Optional[str] = None,
                 span_kind: SpanKind = SpanKind.INTERNAL,
                 service_name: str = "ia-influencer"):
        
        self.span_id = str(uuid.uuid4())
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.name = name
        self.service_name = service_name
        self.span_kind = span_kind
        
        # Timing
        self.start_time = time.time()
        self.end_time = None
        self.duration_ms = None
        
        # Status and metadata
        self.status = SpanStatus.OK
        self.status_message = None
        self.tags: Dict[str, SpanTag] = {}
        self.logs: List[SpanLog] = []
        
        # Error tracking
        self.error = None
        self.exception_info = None
        
        # Content processing specific
        self.content_id = None
        self.user_id = None
        self.operation_type = None
        
        # Performance metrics
        self.resource_usage = {}
        self.dependency_calls = []
        
        # Business context
        self.business_context = {}

    def set_tag(self, key: str, value: Any):
        """Set a tag on the span."""
        self.tags[key] = SpanTag(key=key, value=value)

    def set_business_tag(self, key: str, value: Any):
        """Set business context tag."""
        self.business_context[key] = value
        self.set_tag(f"business.{key}", value)

    def set_content_info(self, content_id: str, content_type: str, user_id: str):
        """Set content processing information."""
        self.content_id = content_id
        self.user_id = user_id
        self.set_tag("content.id", content_id)
        self.set_tag("content.type", content_type)
        self.set_tag("user.id", user_id)

    def set_ai_operation(self, model_name: str, operation_type: str, input_size: int = 0):
        """Set AI operation information."""
        self.operation_type = operation_type
        self.set_tag("ai.model", model_name)
        self.set_tag("ai.operation", operation_type)
        if input_size > 0:
            self.set_tag("ai.input_size", input_size)

    def log(self, message: str, level: str = "info", fields: Optional[Dict] = None):
        """Add a structured log entry to the span."""
        log_entry = SpanLog(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            fields=fields or {}
        )
        self.logs.append(log_entry)

    def log_event(self, event_name: str, details: Optional[Dict] = None):
        """Log a structured event."""
        self.log(
            f"Event: {event_name}",
            level="info",
            fields={"event_name": event_name, "details": details or {}}
        )

    def set_error(self, error: Exception, error_message: Optional[str] = None):
        """Mark span as having an error."""
        self.status = SpanStatus.ERROR
        self.status_message = error_message or str(error)
        
        self.error = {
            "type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store exception info for debugging
        import traceback
        self.exception_info = traceback.format_exc()
        
        self.set_tag("error", True)
        self.set_tag("error.type", type(error).__name__)
        self.set_tag("error.message", str(error))
        
        # Log the error
        self.log(f"Error occurred: {error}", "error", {"exception_type": type(error).__name__})

    def record_dependency_call(self, service: str, operation: str, duration_ms: float, success: bool):
        """Record external service dependency call."""
        call_info = {
            "service": service,
            "operation": operation,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.dependency_calls.append(call_info)
        
        # Add as tags for easier querying
        self.set_tag(f"dependency.{service}.called", True)
        self.set_tag(f"dependency.{service}.duration_ms", duration_ms)

    def record_resource_usage(self, cpu_percent: float, memory_mb: float):
        """Record resource usage during span execution."""
        self.resource_usage = {
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.set_tag("resource.cpu_percent", cpu_percent)
        self.set_tag("resource.memory_mb", memory_mb)

    def finish(self, status: Optional[SpanStatus] = None, status_message: Optional[str] = None):
        """Mark the span as finished."""
        if self.end_time is None:
            self.end_time = time.time()
            self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
            
            if status:
                self.status = status
            if status_message:
                self.status_message = status_message
            
            # Add final timing tags
            self.set_tag("duration_ms", self.duration_ms)
            self.set_tag("finished_at", datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        """Convert span to dictionary for serialization."""



        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "service_name": self.service_name,
            "span_kind": self.span_kind.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "status_message": self.status_message,
            "tags": {k: {"value": v.value, "timestamp": v.timestamp.isoformat()} for k, v in self.tags.items()},
            "logs": [{"timestamp": log.timestamp.isoformat(), "level": log.level, "message": log.message, "fields": log.fields} for log in self.logs],
            "error": self.error,
            "exception_info": self.exception_info,
            "content_id": self.content_id,
            "user_id": self.user_id,
            "operation_type": self.operation_type,
            "resource_usage": self.resource_usage,
            "dependency_calls": self.dependency_calls,
            "business_context": self.business_context
        }

    def to_jaeger_format(self) -> Dict:
        """Convert span to Jaeger-compatible format."""



        return {
            "traceID": self.trace_id.replace("-", ""),
            "spanID": self.span_id.replace("-", ""),
            "parentSpanID": self.parent_id.replace("-", "") if self.parent_id else None,
            "operationName": self.name,
            "startTime": int(self.start_time * 1000000),  # microseconds
            "duration": int(self.duration_ms * 1000) if self.duration_ms else 0,  # microseconds
            "tags": [{"key": k, "value": str(v.value)} for k, v in self.tags.items()],
            "logs": [
                {
                    "timestamp": int(log.timestamp.timestamp() * 1000000),
                    "fields": [{"key": "message", "value": log.message}] + 
                             [{"key": k, "value": str(v)} for k, v in log.fields.items()]
                }
                for log in self.logs
            ],
            "process": {
                "serviceName": self.service_name,
                "tags": []
            }
        }


class TracingManager:
    """Enhanced tracing manager with advanced features."""
    
    def __init__(self, service_name: str = "ia-influencer", retention_hours: int = 24):
        self.service_name = service_name
        self.retention_hours = retention_hours
        self.traces = defaultdict(list)  # trace_id -> [spans]
        self.active_spans = {}  # thread_id -> span
        self.span_index = {}  # span_id -> span
        self._lock = threading.Lock()
        
        # Metrics and analytics
        self.trace_metrics = defaultdict(int)
        self.span_metrics = defaultdict(int)
        self.error_traces = deque(maxlen=1000)
        self.slow_traces = deque(maxlen=1000)
        
        # Configuration
        self.slow_trace_threshold_ms = 5000  # 5 seconds
        self.sampling_rate = 1.0  # 100% sampling by default

    def should_sample_trace(self) -> bool:
        """Determine if trace should be sampled."""
        import random
        return random.random() < self.sampling_rate

    def start_trace(self, operation_name: str, span_kind: SpanKind = SpanKind.SERVER) -> str:
        """Start a new trace."""
        if not self.should_sample_trace():
            return None
            
        trace_id = str(uuid.uuid4())
        span = self.start_span(operation_name, trace_id=trace_id, span_kind=span_kind)
        
        with self._lock:
            self.trace_metrics["traces_started"] += 1
            
        return trace_id

    def start_span(self, 
                   name: str, 
                   trace_id: Optional[str] = None, 
                   parent_id: Optional[str] = None,
                   span_kind: SpanKind = SpanKind.INTERNAL) -> Optional[Span]:
        """Start a new span."""
        
        if trace_id is None:
            # Try to get trace_id from current active span
            current_span = self.get_active_span()
            if current_span:
                trace_id = current_span.trace_id
            else:
                # Start a new trace if none exists
                trace_id = self.start_trace(name, span_kind)
                if not trace_id:  # Not sampled
                    return None

        if parent_id is None:
            # Try to get parent from current active span
            current_span = self.get_active_span()
            parent_id = current_span.span_id if current_span else None

        span = Span(name, trace_id, parent_id, span_kind, self.service_name)
        
        with self._lock:
            self.traces[trace_id].append(span)
            self.span_index[span.span_id] = span
            self.active_spans[threading.get_ident()] = span
            self.span_metrics["spans_started"] += 1
        
        return span

    def finish_span(self, span: Span, status: Optional[SpanStatus] = None):
        """Finish a span and update metrics."""
        span.finish(status)
        
        with self._lock:
            # Remove from active spans
            thread_id = threading.get_ident()
            if thread_id in self.active_spans and self.active_spans[thread_id].span_id == span.span_id:
                del self.active_spans[thread_id]
            
            # Update metrics
            self.span_metrics["spans_finished"] += 1
            self.span_metrics[f"spans_by_status_{span.status.value}"] += 1
            
            # Track error traces
            if span.status == SpanStatus.ERROR:
                self.error_traces.append({
                    "trace_id": span.trace_id,
                    "span_id": span.span_id,
                    "error": span.error,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Track slow traces
            if span.duration_ms and span.duration_ms > self.slow_trace_threshold_ms:
                self.slow_traces.append({
                    "trace_id": span.trace_id,
                    "span_id": span.span_id,
                    "duration_ms": span.duration_ms,
                    "operation": span.name,
                    "timestamp": datetime.utcnow().isoformat()
                })

    def get_active_span(self) -> Optional[Span]:
        """Get the active span for current thread."""
        thread_id = threading.get_ident()
        return self.active_spans.get(thread_id)

    def set_active_span(self, span: Optional[Span]):
        """Set the active span for current thread."""
        thread_id = threading.get_ident()
        if span:
            self.active_spans[thread_id] = span
        elif thread_id in self.active_spans:
            del self.active_spans[thread_id]

    @contextmanager
    def trace_operation(self, 
                       operation_name: str, 
                       span_kind: SpanKind = SpanKind.INTERNAL,
                       **kwargs):
        """Context manager for tracing operations."""
        span = self.start_span(operation_name, span_kind=span_kind)
        if not span:  # Not sampled
            yield None
            return
            
        # Set additional attributes
        for key, value in kwargs.items():
            span.set_tag(key, value)
        
        try:
            yield span
        except Exception as e:
            span.set_error(e)
            raise
        finally:
            self.finish_span(span)

    @asynccontextmanager
    async def trace_async_operation(self, 
                                   operation_name: str,
                                   span_kind: SpanKind = SpanKind.INTERNAL,
                                   **kwargs):
        """Async context manager for tracing operations."""
        span = self.start_span(operation_name, span_kind=span_kind)
        if not span:  # Not sampled
            yield None
            return
            
        # Set additional attributes
        for key, value in kwargs.items():
            span.set_tag(key, value)
        
        try:
            yield span
        except Exception as e:
            span.set_error(e)
            raise
        finally:
            self.finish_span(span)

    def get_trace(self, trace_id: str) -> Optional[List[Span]]:
        """Get all spans for a trace."""



        return self.traces.get(trace_id)

    def get_span(self, span_id: str) -> Optional[Span]:
        """Get a specific span by ID."""



        return self.span_index.get(span_id)

    def get_trace_tree(self, trace_id: str) -> Optional[Dict]:
        """Get trace as a tree structure."""
        spans = self.get_trace(trace_id)
        if not spans:
            return None
        
        # Build tree structure
        span_map = {span.span_id: span for span in spans}
        root_spans = [span for span in spans if span.parent_id is None]
        
        def build_tree(span: Span) -> Dict:
            children = [
                build_tree(child_span)
                for child_span in spans
                if child_span.parent_id == span.span_id
            ]
            
            return {
                "span": span.to_dict(),
                "children": children
            }
        
        return {
            "trace_id": trace_id,
            "root_spans": [build_tree(root) for root in root_spans],
            "total_spans": len(spans),
            "total_duration_ms": max(span.duration_ms or 0 for span in spans),
            "status": "error" if any(span.status == SpanStatus.ERROR for span in spans) else "ok"
        }

    def search_traces(self, 
                     operation_name: Optional[str] = None,
                     service_name: Optional[str] = None,
                     tag_filters: Optional[Dict[str, str]] = None,
                     min_duration_ms: Optional[float] = None,
                     max_duration_ms: Optional[float] = None,
                     status: Optional[SpanStatus] = None,
                     hours_back: int = 1,
                     limit: int = 100) -> List[Dict]:
        """Search traces with filters."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        matching_traces = []
        
        for trace_id, spans in list(self.traces.items()):
            if len(matching_traces) >= limit:
                break
                
            # Filter by time
            if not any(datetime.fromtimestamp(span.start_time) >= cutoff_time for span in spans):
                continue
            
            # Check filters
            trace_matches = False
            for span in spans:
                matches = True
                
                if operation_name and operation_name not in span.name:
                    matches = False
                
                if service_name and span.service_name != service_name:
                    matches = False
                
                if status and span.status != status:
                    matches = False
                
                if min_duration_ms and (not span.duration_ms or span.duration_ms < min_duration_ms):
                    matches = False
                
                if max_duration_ms and (span.duration_ms and span.duration_ms > max_duration_ms):
                    matches = False
                
                if tag_filters:
                    for tag_key, tag_value in tag_filters.items():
                        if tag_key not in span.tags or str(span.tags[tag_key].value) != tag_value:
                            matches = False
                            break
                
                if matches:
                    trace_matches = True
                    break
            
            if trace_matches:
                trace_tree = self.get_trace_tree(trace_id)
                if trace_tree:
                    matching_traces.append(trace_tree)
        
        return matching_traces

    def get_tracing_metrics(self) -> Dict:
        """Get comprehensive tracing metrics."""
        with self._lock:
            active_spans_count = len(self.active_spans)
            total_traces = len(self.traces)
            total_spans = len(self.span_index)
            
            # Calculate average spans per trace
            avg_spans_per_trace = total_spans / total_traces if total_traces > 0 else 0
            
            # Recent errors and slow traces
            recent_errors = len([e for e in self.error_traces 
                               if datetime.fromisoformat(e['timestamp']) >= datetime.utcnow() - timedelta(hours=1)])
            
            recent_slow = len([s for s in self.slow_traces
                             if datetime.fromisoformat(s['timestamp']) >= datetime.utcnow() - timedelta(hours=1)])
        
        return {
            "active_spans": active_spans_count,
            "total_traces": total_traces,
            "total_spans": total_spans,
            "avg_spans_per_trace": round(avg_spans_per_trace, 2),
            "sampling_rate": self.sampling_rate,
            "recent_errors_1h": recent_errors,
            "recent_slow_traces_1h": recent_slow,
            "span_metrics": dict(self.span_metrics),
            "trace_metrics": dict(self.trace_metrics),
            "slow_threshold_ms": self.slow_trace_threshold_ms,
            "retention_hours": self.retention_hours,
            "service_name": self.service_name
        }

    def get_performance_insights(self) -> Dict:
        """Get performance insights from tracing data."""
        insights = {
            "slowest_operations": [],
            "most_error_prone": [],
            "dependency_performance": defaultdict(list),
            "resource_usage_patterns": []
        }
        
        # Analyze recent spans for insights
        recent_spans = []
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        for spans_list in self.traces.values():
            recent_spans.extend([
                span for span in spans_list
                if span.end_time and datetime.fromtimestamp(span.end_time) >= cutoff_time
            ])
        
        # Find slowest operations
        operation_durations = defaultdict(list)
        operation_errors = defaultdict(int)
        
        for span in recent_spans:
            if span.duration_ms:
                operation_durations[span.name].append(span.duration_ms)
            
            if span.status == SpanStatus.ERROR:
                operation_errors[span.name] += 1
        
        # Calculate averages and identify slow operations
        for op_name, durations in operation_durations.items():
            avg_duration = sum(durations) / len(durations)
            if avg_duration > 1000:  # More than 1 second
                insights["slowest_operations"].append({
                    "operation": op_name,
                    "avg_duration_ms": round(avg_duration, 2),
                    "max_duration_ms": max(durations),
                    "call_count": len(durations)
                })
        
        # Sort by average duration
        insights["slowest_operations"].sort(key=lambda x: x["avg_duration_ms"], reverse=True)
        insights["slowest_operations"] = insights["slowest_operations"][:10]
        
        # Find most error-prone operations
        for op_name, error_count in operation_errors.items():
            total_calls = len(operation_durations.get(op_name, [0]))
            error_rate = error_count / total_calls if total_calls > 0 else 0
            
            if error_rate > 0.01:  # More than 1% error rate
                insights["most_error_prone"].append({
                    "operation": op_name,
                    "error_count": error_count,
                    "total_calls": total_calls,
                    "error_rate": round(error_rate * 100, 2)
                })
        
        insights["most_error_prone"].sort(key=lambda x: x["error_rate"], reverse=True)
        insights["most_error_prone"] = insights["most_error_prone"][:10]
        
        return insights

    def cleanup_old_traces(self):
        """Clean up old traces beyond retention period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        traces_to_remove = []
        
        for trace_id, spans in self.traces.items():
            # Check if all spans in trace are old
            if all(span.end_time and datetime.fromtimestamp(span.end_time) < cutoff_time for span in spans):
                traces_to_remove.append(trace_id)
        
        # Remove old traces
        for trace_id in traces_to_remove:
            spans = self.traces.pop(trace_id, [])
            for span in spans:
                self.span_index.pop(span.span_id, None)
        
        logging.info(f"Cleaned up {len(traces_to_remove)} old traces")

    def export_traces_jaeger(self, trace_ids: List[str]) -> Dict:
        """Export traces in Jaeger format."""
        jaeger_data = {
            "data": []
        }
        
        for trace_id in trace_ids:
            spans = self.get_trace(trace_id)
            if spans:
                jaeger_spans = [span.to_jaeger_format() for span in spans]
                jaeger_data["data"].append({
                    "traceID": trace_id.replace("-", ""),
                    "spans": jaeger_spans
                })
        
        return jaeger_data


class DistributedTracer:
    """High-level distributed tracer for business operations."""
    
    def __init__(self, tracing_manager: TracingManager):
        self.tracing_manager = tracing_manager
    
    @contextmanager
    def trace_content_upload(self, user_id: str, content_type: str, file_size: int):
        """Trace content upload operation."""
        with self.tracing_manager.trace_operation(
            "content_upload",
            SpanKind.SERVER,
            user_id=user_id,
            content_type=content_type,
            file_size=file_size
        ) as span:
            if span:
                span.set_content_info(str(uuid.uuid4()), content_type, user_id)
                span.set_tag("file_size_bytes", file_size)
            yield span

    @contextmanager  
    def trace_ai_processing(self, model_name: str, operation_type: str, content_id: str):
        """Trace AI processing operation."""
        with self.tracing_manager.trace_operation(
            f"ai_processing_{operation_type}",
            SpanKind.INTERNAL,
            model=model_name,
            operation=operation_type
        ) as span:
            if span:
                span.set_ai_operation(model_name, operation_type)
                span.set_tag("content_id", content_id)
            yield span

    @contextmanager
    def trace_content_protection(self, content_id: str, protection_type: str):
        """Trace content protection operation."""
        with self.tracing_manager.trace_operation(
            f"content_protection_{protection_type}",
            SpanKind.INTERNAL,
            content_id=content_id,
            protection_type=protection_type
        ) as span:
            if span:
                span.set_tag("content_id", content_id)
                span.set_tag("protection_type", protection_type)
            yield span

    @contextmanager
    def trace_collaboration_matching(self, user_id: str, match_criteria: Dict):
        """Trace collaboration matching operation."""
        with self.tracing_manager.trace_operation(
            "collaboration_matching",
            SpanKind.INTERNAL,
            user_id=user_id
        ) as span:
            if span:
                span.set_tag("user_id", user_id)
                span.set_tag("match_criteria_count", len(match_criteria))
                for key, value in match_criteria.items():
                    span.set_tag(f"criteria_{key}", str(value))
            yield span

    @contextmanager
    def trace_database_operation(self, operation: str, table: str, query_type: str = "read"):
        """Trace database operation."""
        with self.tracing_manager.trace_operation(
            f"db_{operation}",
            SpanKind.CLIENT,
            db_table=table,
            query_type=query_type
        ) as span:
            if span:
                span.set_tag("db.table", table)
                span.set_tag("db.operation", operation)
                span.set_tag("db.type", "postgresql")
            yield span

    @contextmanager
    def trace_external_api_call(self, service_name: str, endpoint: str, method: str = "GET"):
        """Trace external API call."""
        with self.tracing_manager.trace_operation(
            f"external_api_{service_name}",
            SpanKind.CLIENT,
            service=service_name,
            endpoint=endpoint,
            method=method
        ) as span:
            if span:
                span.set_tag("external.service", service_name)
                span.set_tag("external.endpoint", endpoint)
                span.set_tag("http.method", method)
            yield span


class RequestTracer:
    """Request-specific tracer for HTTP operations."""
    
    def __init__(self, tracing_manager: TracingManager):
        self.tracing_manager = tracing_manager
    
    def start_request_trace(self, 
                           method: str, 
                           endpoint: str, 
                           user_id: Optional[str] = None,
                           request_id: Optional[str] = None) -> Optional[Span]:
        """Start tracing an HTTP request."""
        operation_name = f"{method} {endpoint}"
        span = self.tracing_manager.start_span(operation_name, span_kind=SpanKind.SERVER)
        
        if span:
            span.set_tag("http.method", method)
            span.set_tag("http.endpoint", endpoint)
            if user_id:
                span.set_tag("user.id", user_id)
            if request_id:
                span.set_tag("request.id", request_id)
        
        return span
    
    def finish_request_trace(self, 
                           span: Span, 
                           status_code: int, 
                           response_size: Optional[int] = None):
        """Finish tracing an HTTP request."""
        span.set_tag("http.status_code", status_code)
        if response_size:
            span.set_tag("response.size_bytes", response_size)
        
        # Determine span status based on HTTP status code
        if status_code >= 500:
            status = SpanStatus.ERROR
        elif status_code >= 400:
            status = SpanStatus.ERROR  # Client errors are also considered errors in tracing
        else:
            status = SpanStatus.OK
        
        self.tracing_manager.finish_span(span, status)
    
    @contextmanager
    def trace_http_request(self, 
                          method: str, 
                          endpoint: str,
                          user_id: Optional[str] = None,
                          request_id: Optional[str] = None):
        """Context manager for tracing HTTP requests."""
        span = self.start_request_trace(method, endpoint, user_id, request_id)
        try:
            yield span
        except Exception as e:
            if span:
                span.set_error(e)
            raise
        # Note: finish_request_trace should be called explicitly with status code
        return span

    def get_active_span(self) -> Optional[Span]:
        """Get the currently active span for this thread."""



        return self.active_spans.get(threading.get_ident())

    def finish_span(self, span: Span):
        """Finish a span."""
        span.finish()
        thread_id = threading.get_ident()
        
        with self._lock:
            # If this was the active span, remove it
            if self.active_spans.get(thread_id) == span:
                del self.active_spans[thread_id]

    @contextmanager
    def trace_operation(self, name: str, trace_id: Optional[str] = None):
        """Context manager for tracing an operation."""
        span = self.start_span(name, trace_id)
        try:
            yield span
        except Exception as e:
            span.set_error(e)
            raise
        finally:
            self.finish_span(span)

    def get_trace(self, trace_id: str) -> Dict:
        """Get complete trace information."""
        with self._lock:
            spans = self.traces.get(trace_id, [])
        
        if not spans:
            return {"error": "Trace not found"}

        # Build span hierarchy
        span_dict = {span.span_id: span.to_dict() for span in spans}
        root_spans = [s for s in span_dict.values() if s["parent_id"] is None]
        
        # Calculate trace statistics
        total_duration = max((s["duration_ms"] or 0) for s in span_dict.values())
        error_count = sum(1 for s in span_dict.values() if s["status"] == "error")
        
        return {
            "trace_id": trace_id,
            "spans": span_dict,
            "root_spans": root_spans,
            "total_spans": len(spans),
            "total_duration_ms": total_duration,
            "error_count": error_count,
            "status": "error" if error_count > 0 else "ok"
        }

    def get_trace_summary(self, trace_id: str) -> Dict:
        """Get summary statistics for a trace."""
        trace_data = self.get_trace(trace_id)
        if "error" in trace_data:
            return trace_data

        spans = trace_data["spans"].values()
        
        # Service breakdown
        services = defaultdict(lambda: {"count": 0, "total_duration": 0})
        for span in spans:
            service = span["tags"].get("service.name", "unknown")
            services[service]["count"] += 1
            services[service]["total_duration"] += span["duration_ms"] or 0

        # Operation breakdown
        operations = defaultdict(int)
        for span in spans:
            operations[span["name"]] += 1

        return {
            "trace_id": trace_id,
            "total_duration_ms": trace_data["total_duration_ms"],
            "span_count": trace_data["total_spans"],
            "error_count": trace_data["error_count"],
            "services": dict(services),
            "top_operations": dict(sorted(operations.items(), key=lambda x: x[1], reverse=True)[:5])
        }

    def instrument_content_upload(self, trace_id: str, content_info: Dict) -> Span:
        """Create instrumented span for content upload."""
        span = self.start_span("content.upload", trace_id)
        span.set_tag("content.type", content_info.get("media_type", "unknown"))
        span.set_tag("content.size_bytes", content_info.get("size", 0))
        span.set_tag("creator.id", content_info.get("creator_id", "unknown"))
        span.set_tag("service.name", "content-service")
        return span

    def instrument_ai_processing(self, trace_id: str, processing_type: str) -> Span:
        """Create instrumented span for AI processing."""
        span = self.start_span(f"ai.{processing_type}", trace_id)
        span.set_tag("ai.processing_type", processing_type)
        span.set_tag("service.name", "ai-service")
        return span

    def instrument_blockchain_operation(self, trace_id: str, operation: str) -> Span:
        """Create instrumented span for blockchain operations."""
        span = self.start_span(f"blockchain.{operation}", trace_id)
        span.set_tag("blockchain.operation", operation)
        span.set_tag("service.name", "blockchain-service")
        return span

    def get_performance_insights(self, hours: int = 24) -> Dict:
        """Get performance insights from recent traces."""
        cutoff_time = time.time() - (hours * 3600)
        recent_traces = []
        
        with self._lock:
            for trace_id, spans in self.traces.items():
                if any(span.start_time > cutoff_time for span in spans):
                    recent_traces.append((trace_id, spans))

        if not recent_traces:
            return {"message": "No recent traces found"}

        # Analyze performance
        operation_stats = defaultdict(lambda: {"count": 0, "total_duration": 0, "errors": 0})
        
        for trace_id, spans in recent_traces:
            for span in spans:
                op_name = span.name
                operation_stats[op_name]["count"] += 1
                operation_stats[op_name]["total_duration"] += span.duration_ms or 0
                if span.status == "error":
                    operation_stats[op_name]["errors"] += 1

        # Calculate averages and error rates
        insights = {}
        for op_name, stats in operation_stats.items():
            avg_duration = stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0
            error_rate = (stats["errors"] / stats["count"]) * 100 if stats["count"] > 0 else 0
            
            insights[op_name] = {
                "avg_duration_ms": round(avg_duration, 2),
                "total_operations": stats["count"],
                "error_rate_percent": round(error_rate, 2),
                "total_errors": stats["errors"]
            }

        return {
            "time_period_hours": hours,
            "total_traces": len(recent_traces),
            "operation_insights": insights,
            "slowest_operations": sorted(
                [(op, data["avg_duration_ms"]) for op, data in insights.items()],
                key=lambda x: x[1], reverse=True
            )[:5]
        }

    def cleanup_old_traces(self, max_age_hours: int = 24):
        """Clean up old trace data."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        with self._lock:
            traces_to_remove = []
            for trace_id, spans in self.traces.items():
                # Remove trace if all spans are older than cutoff
                if all(span.start_time < cutoff_time for span in spans):
                    traces_to_remove.append(trace_id)
            
            for trace_id in traces_to_remove:
                del self.traces[trace_id]
        
        return {"cleaned_traces": len(traces_to_remove)}
