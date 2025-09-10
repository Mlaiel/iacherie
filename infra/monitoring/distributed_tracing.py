# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import logging
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import aiofiles
import aiohttp
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import statistics
import traceback
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/ainflue/distributed_tracing.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TraceSpan:
    """Distributed trace span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[float]
    status: str  # ok, error, timeout
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]
    baggage: Dict[str, str]

@dataclass
class TraceContext:
    """Trace context for propagation"""
    trace_id: str
    span_id: str
    sampled: bool
    baggage: Dict[str, str]

@dataclass
class DistributedTracingConfig:
    """Configuration for distributed tracing"""
    service_name: str
    jaeger_endpoint: str
    sampling_rate: float = 1.0
    max_spans_per_trace: int = 1000
    trace_timeout_seconds: int = 300
    enable_auto_instrumentation: bool = True
    custom_tags: Dict[str, str] = None
    propagation_headers: List[str] = None

class SpanProcessor:
    """Processes and enriches spans"""
    
    def __init__(self):
        self.span_processors = []
        self.enrichers = []
    
    def add_processor(self, processor: Callable[[TraceSpan], TraceSpan]):
        """Add span processor"""
        self.span_processors.append(processor)
    
    def add_enricher(self, enricher: Callable[[TraceSpan], TraceSpan]):
        """Add span enricher"""
        self.enrichers.append(enricher)
    
    async def process_span(self, span: TraceSpan) -> TraceSpan:
        """Process span through all processors and enrichers"""
        try:
            # Apply processors
            for processor in self.span_processors:
                span = processor(span)
            
            # Apply enrichers
            for enricher in self.enrichers:
                span = enricher(span)
            
            return span
        
        except Exception as e:
            logger.error(f"Error processing span: {e}")
            return span

class PerformanceAnalyzer:
    """Analyzes performance metrics from traces"""
    
    def __init__(self):
        self.service_metrics = defaultdict(lambda: {
            'request_count': 0,
            'error_count': 0,
            'total_duration': 0,
            'min_duration': float('inf'),
            'max_duration': 0,
            'durations': deque(maxlen=1000)  # Keep last 1000 requests
        })
        self.operation_metrics = defaultdict(lambda: defaultdict(lambda: {
            'count': 0,
            'errors': 0,
            'durations': deque(maxlen=100)
        }))
    
    def analyze_span(self, span: TraceSpan):
        """Analyze span and update metrics"""
        if span.duration_ms is None:
            return
        
        service = span.service_name
        operation = span.operation_name
        duration = span.duration_ms
        
        # Update service metrics
        service_stats = self.service_metrics[service]
        service_stats['request_count'] += 1
        service_stats['total_duration'] += duration
        service_stats['min_duration'] = min(service_stats['min_duration'], duration)
        service_stats['max_duration'] = max(service_stats['max_duration'], duration)
        service_stats['durations'].append(duration)
        
        if span.status == 'error':
            service_stats['error_count'] += 1
        
        # Update operation metrics
        op_stats = self.operation_metrics[service][operation]
        op_stats['count'] += 1
        op_stats['durations'].append(duration)
        
        if span.status == 'error':
            op_stats['errors'] += 1
    
    def get_service_summary(self, service_name: str) -> Dict[str, Any]:
        """Get performance summary for service"""
        if service_name not in self.service_metrics:
            return {}
        
        stats = self.service_metrics[service_name]
        durations = list(stats['durations'])
        
        if not durations:
            return {}
        
        return {
            'service_name': service_name,
            'request_count': stats['request_count'],
            'error_count': stats['error_count'],
            'error_rate': stats['error_count'] / stats['request_count'],
            'avg_duration_ms': statistics.mean(durations),
            'p50_duration_ms': statistics.median(durations),
            'p95_duration_ms': np.percentile(durations, 95),
            'p99_duration_ms': np.percentile(durations, 99),
            'min_duration_ms': stats['min_duration'],
            'max_duration_ms': stats['max_duration']
        }
    
    def get_operation_summary(self, service_name: str, operation_name: str) -> Dict[str, Any]:
        """Get performance summary for operation"""
        if (service_name not in self.operation_metrics or 
            operation_name not in self.operation_metrics[service_name]):
            return {}
        
        stats = self.operation_metrics[service_name][operation_name]
        durations = list(stats['durations'])
        
        if not durations:
            return {}
        
        return {
            'service_name': service_name,
            'operation_name': operation_name,
            'request_count': stats['count'],
            'error_count': stats['errors'],
            'error_rate': stats['errors'] / stats['count'] if stats['count'] > 0 else 0,
            'avg_duration_ms': statistics.mean(durations),
            'p95_duration_ms': np.percentile(durations, 95),
            'p99_duration_ms': np.percentile(durations, 99)
        }
    
    def detect_anomalies(self, service_name: str, threshold_multiplier: float = 3.0) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        anomalies = []
        
        if service_name not in self.service_metrics:
            return anomalies
        
        stats = self.service_metrics[service_name]
        durations = list(stats['durations'])
        
        if len(durations) < 10:  # Need sufficient data
            return anomalies
        
        mean_duration = statistics.mean(durations)
        stdev_duration = statistics.stdev(durations)
        threshold = mean_duration + (threshold_multiplier * stdev_duration)
        
        # Find recent anomalies (last 10 requests)
        recent_durations = durations[-10:]
        for i, duration in enumerate(recent_durations):
            if duration > threshold:
                anomalies.append({
                    'service_name': service_name,
                    'duration_ms': duration,
                    'threshold_ms': threshold,
                    'deviation': (duration - mean_duration) / stdev_duration,
                    'timestamp': datetime.utcnow() - timedelta(seconds=(10-i))
                })
        
        return anomalies

class TraceCorrelator:
    """Correlates traces across services"""
    
    def __init__(self):
        self.traces = {}  # trace_id -> list of spans
        self.trace_timeouts = {}  # trace_id -> timeout_time
    
    def add_span(self, span: TraceSpan):
        """Add span to trace correlation"""
        trace_id = span.trace_id
        
        if trace_id not in self.traces:
            self.traces[trace_id] = []
            # Set timeout for trace completion
            self.trace_timeouts[trace_id] = datetime.utcnow() + timedelta(minutes=5)
        
        self.traces[trace_id].append(span)
    
    def get_trace_timeline(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get chronological timeline of trace"""
        if trace_id not in self.traces:
            return []
        
        spans = sorted(self.traces[trace_id], key=lambda x: x.start_time)
        
        timeline = []
        for span in spans:
            timeline.append({
                'span_id': span.span_id,
                'service_name': span.service_name,
                'operation_name': span.operation_name,
                'start_time': span.start_time.isoformat(),
                'end_time': span.end_time.isoformat() if span.end_time else None,
                'duration_ms': span.duration_ms,
                'status': span.status,
                'tags': span.tags
            })
        
        return timeline
    
    def analyze_trace_performance(self, trace_id: str) -> Dict[str, Any]:
        """Analyze performance characteristics of trace"""
        if trace_id not in self.traces:
            return {}
        
        spans = self.traces[trace_id]
        
        # Calculate total trace duration
        start_times = [span.start_time for span in spans]
        end_times = [span.end_time for span in spans if span.end_time]
        
        if not start_times or not end_times:
            return {}
        
        trace_start = min(start_times)
        trace_end = max(end_times)
        total_duration = (trace_end - trace_start).total_seconds() * 1000
        
        # Calculate service breakdown
        service_durations = defaultdict(float)
        service_counts = defaultdict(int)
        
        for span in spans:
            if span.duration_ms:
                service_durations[span.service_name] += span.duration_ms
                service_counts[span.service_name] += 1
        
        # Find critical path
        critical_path = self._find_critical_path(spans)
        
        return {
            'trace_id': trace_id,
            'total_duration_ms': total_duration,
            'span_count': len(spans),
            'service_breakdown': dict(service_durations),
            'service_counts': dict(service_counts),
            'critical_path': critical_path,
            'error_spans': [s.span_id for s in spans if s.status == 'error']
        }
    
    def _find_critical_path(self, spans: List[TraceSpan]) -> List[str]:
        """Find critical path through trace"""
        # Build dependency graph
        children = defaultdict(list)
        
        for span in spans:
            if span.parent_span_id:
                children[span.parent_span_id].append(span.span_id)
        
        # Find root spans (no parent)
        root_spans = [s for s in spans if not s.parent_span_id]
        
        if not root_spans:
            return []
        
        # Simple critical path: longest sequential path
        span_map = {s.span_id: s for s in spans}
        
        def get_path_duration(span_id: str, visited: set) -> Tuple[float, List[str]]:
            if span_id in visited:
                return 0, []
            
            visited.add(span_id)
            span = span_map.get(span_id)
            
            if not span or not span.duration_ms:
                return 0, []
            
            # Find longest child path
            max_child_duration = 0
            best_child_path = []
            
            for child_id in children.get(span_id, []):
                child_duration, child_path = get_path_duration(child_id, visited.copy())
                if child_duration > max_child_duration:
                    max_child_duration = child_duration
                    best_child_path = child_path
            
            total_duration = span.duration_ms + max_child_duration
            path = [span_id] + best_child_path
            
            return total_duration, path
        
        # Find the root span with longest path
        best_path = []
        max_duration = 0
        
        for root_span in root_spans:
            duration, path = get_path_duration(root_span.span_id, set())
            if duration > max_duration:
                max_duration = duration
                best_path = path
        
        return best_path
    
    def cleanup_expired_traces(self):
        """Clean up expired traces"""
        current_time = datetime.utcnow()
        expired_traces = [
            trace_id for trace_id, timeout_time in self.trace_timeouts.items()
            if current_time > timeout_time
        ]
        
        for trace_id in expired_traces:
            if trace_id in self.traces:
                del self.traces[trace_id]
            if trace_id in self.trace_timeouts:
                del self.trace_timeouts[trace_id]
        
        if expired_traces:
            logger.info(f"Cleaned up {len(expired_traces)} expired traces")

class DistributedTracingEngine:
    """Main distributed tracing engine"""
    
    def __init__(self, config: DistributedTracingConfig):
        self.config = config
        self.tracer_provider = None
        self.tracer = None
        self.span_processor = SpanProcessor()
        self.performance_analyzer = PerformanceAnalyzer()
        self.trace_correlator = TraceCorrelator()
        self.active_spans = {}
        self.is_running = False
    
    async def initialize(self):
        """Initialize distributed tracing"""
        logger.info("Initializing Ainflue Distributed Tracing Engine")
        
        try:
            # Create resource with service information
            resource = Resource.create({
                "service.name": self.config.service_name,
                "service.version": "1.0.0",
                "deployment.environment": "production"
            })
            
            # Create tracer provider
            self.tracer_provider = TracerProvider(resource=resource)
            
            # Configure Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.config.jaeger_endpoint.split('://')[1].split(':')[0],
                agent_port=int(self.config.jaeger_endpoint.split(':')[-1]),
            )
            
            # Add span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__)
            
            # Setup auto-instrumentation
            if self.config.enable_auto_instrumentation:
                await self._setup_auto_instrumentation()
            
            # Setup span processors
            self._setup_span_processors()
            
            logger.info("Distributed tracing initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize distributed tracing: {e}")
            raise
    
    async def _setup_auto_instrumentation(self):
        """Setup automatic instrumentation for common libraries"""
        try:
            # Instrument HTTP requests
            RequestsInstrumentor().instrument()
            
            # Instrument Flask if available
            try:
                FlaskInstrumentor().instrument()
            except Exception:
                logger.debug("Flask instrumentation not available")
            
            # Instrument SQLAlchemy if available
            try:
                SQLAlchemyInstrumentor().instrument()
            except Exception:
                logger.debug("SQLAlchemy instrumentation not available")
            
            logger.info("Auto-instrumentation setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup auto-instrumentation: {e}")
    
    def _setup_span_processors(self):
        """Setup custom span processors"""
        # Add performance analyzer
        self.span_processor.add_processor(self._performance_processor)
        
        # Add error enricher
        self.span_processor.add_enricher(self._error_enricher)
        
        # Add custom tags enricher
        if self.config.custom_tags:
            self.span_processor.add_enricher(self._custom_tags_enricher)
    
    def _performance_processor(self, span: TraceSpan) -> TraceSpan:
        """Process span for performance analysis"""
        self.performance_analyzer.analyze_span(span)
        return span
    
    def _error_enricher(self, span: TraceSpan) -> TraceSpan:
        """Enrich spans with error information"""
        if span.status == 'error':
            # Add error context to tags
            span.tags['error'] = True
            span.tags['error.kind'] = 'exception'
            
            # Add stack trace if available in logs
            for log in span.logs:
                if 'stack' in log:
                    span.tags['error.stack'] = log['stack'][:1000]  # Truncate long stacks
        
        return span
    
    def _custom_tags_enricher(self, span: TraceSpan) -> TraceSpan:
        """Add custom tags to spans"""
        if self.config.custom_tags:
            span.tags.update(self.config.custom_tags)
        return span
    
    async def start_span(self, operation_name: str, parent_context: Optional[TraceContext] = None,
                        tags: Optional[Dict[str, Any]] = None) -> str:
        """Start a new span"""
        try:
            # Generate span context
            import uuid
            span_id = str(uuid.uuid4())
            
            if parent_context:
                trace_id = parent_context.trace_id
                parent_span_id = parent_context.span_id
            else:
                trace_id = str(uuid.uuid4())
                parent_span_id = None
            
            # Create span
            span = TraceSpan(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                service_name=self.config.service_name,
                start_time=datetime.utcnow(),
                end_time=None,
                duration_ms=None,
                status='ok',
                tags=tags or {},
                logs=[],
                baggage=parent_context.baggage if parent_context else {}
            )
            
            self.active_spans[span_id] = span
            
            logger.debug(f"Started span: {operation_name} ({span_id})")
            return span_id
        
        except Exception as e:
            logger.error(f"Failed to start span: {e}")
            raise
    
    async def finish_span(self, span_id: str, status: str = 'ok', 
                         tags: Optional[Dict[str, Any]] = None):
        """Finish a span"""
        try:
            if span_id not in self.active_spans:
                logger.warning(f"Span not found: {span_id}")
                return
            
            span = self.active_spans[span_id]
            span.end_time = datetime.utcnow()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            span.status = status
            
            if tags:
                span.tags.update(tags)
            
            # Process span
            processed_span = await self.span_processor.process_span(span)
            
            # Add to trace correlator
            self.trace_correlator.add_span(processed_span)
            
            # Remove from active spans
            del self.active_spans[span_id]
            
            logger.debug(f"Finished span: {span.operation_name} ({span_id}) - {span.duration_ms:.2f}ms")
        
        except Exception as e:
            logger.error(f"Failed to finish span: {e}")
    
    async def add_span_log(self, span_id: str, log_data: Dict[str, Any]):
        """Add log entry to span"""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                **log_data
            }
            span.logs.append(log_entry)
    
    async def add_span_tag(self, span_id: str, key: str, value: Any):
        """Add tag to span"""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.tags[key] = value
    
    def create_trace_context(self, span_id: str) -> Optional[TraceContext]:
        """Create trace context for propagation"""
        if span_id not in self.active_spans:
            return None
        
        span = self.active_spans[span_id]
        return TraceContext(
            trace_id=span.trace_id,
            span_id=span_id,
            sampled=True,
            baggage=span.baggage
        )
    
    def extract_trace_context(self, headers: Dict[str, str]) -> Optional[TraceContext]:
        """Extract trace context from headers"""
        try:
            # Standard OpenTelemetry headers
            trace_parent = headers.get('traceparent')
            if trace_parent:
                parts = trace_parent.split('-')
                if len(parts) >= 4:
                    trace_id = parts[1]
                    span_id = parts[2]
                    sampled = bool(int(parts[3], 16) & 1)
                    
                    # Extract baggage
                    baggage = {}
                    baggage_header = headers.get('baggage', '')
                    for item in baggage_header.split(','):
                        if '=' in item:
                            key, value = item.strip().split('=', 1)
                            baggage[key] = value
                    
                    return TraceContext(
                        trace_id=trace_id,
                        span_id=span_id,
                        sampled=sampled,
                        baggage=baggage
                    )
        
        except Exception as e:
            logger.error(f"Failed to extract trace context: {e}")
        
        return None
    
    def inject_trace_context(self, context: TraceContext) -> Dict[str, str]:
        """Inject trace context into headers"""
        headers = {}
        
        try:
            # Create traceparent header
            flags = '01' if context.sampled else '00'
            headers['traceparent'] = f"00-{context.trace_id}-{context.span_id}-{flags}"
            
            # Create baggage header
            if context.baggage:
                baggage_items = [f"{k}={v}" for k, v in context.baggage.items()]
                headers['baggage'] = ','.join(baggage_items)
        
        except Exception as e:
            logger.error(f"Failed to inject trace context: {e}")
        
        return headers
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'service_performance': {
                service: self.performance_analyzer.get_service_summary(service)
                for service in self.performance_analyzer.service_metrics.keys()
            },
            'anomalies': {
                service: self.performance_analyzer.detect_anomalies(service)
                for service in self.performance_analyzer.service_metrics.keys()
            },
            'active_spans': len(self.active_spans),
            'total_traces': len(self.trace_correlator.traces)
        }
    
    async def cleanup(self):
        """Cleanup expired traces and spans"""
        self.trace_correlator.cleanup_expired_traces()
        
        # Clean up old spans from active spans (shouldn't happen normally)
        current_time = datetime.utcnow()
        expired_spans = [
            span_id for span_id, span in self.active_spans.items()
            if (current_time - span.start_time).total_seconds() > self.config.trace_timeout_seconds
        ]
        
        for span_id in expired_spans:
            await self.finish_span(span_id, status='timeout')

# Context manager for easy span management
class TracingContext:
    """Context manager for distributed tracing"""
    
    def __init__(self, engine: DistributedTracingEngine, operation_name: str,
                 parent_context: Optional[TraceContext] = None,
                 tags: Optional[Dict[str, Any]] = None):
        self.engine = engine
        self.operation_name = operation_name
        self.parent_context = parent_context
        self.tags = tags
        self.span_id = None
    
    async def __aenter__(self):
        self.span_id = await self.engine.start_span(
            self.operation_name, self.parent_context, self.tags
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.span_id:
            status = 'error' if exc_type else 'ok'
            error_tags = {}
            
            if exc_type:
                error_tags['error.type'] = exc_type.__name__
                error_tags['error.message'] = str(exc_val)
                error_tags['error.stack'] = traceback.format_exc()
            
            await self.engine.finish_span(self.span_id, status, error_tags)
    
    async def add_log(self, log_data: Dict[str, Any]):
        """Add log to current span"""
        if self.span_id:
            await self.engine.add_span_log(self.span_id, log_data)
    
    async def add_tag(self, key: str, value: Any):
        """Add tag to current span"""
        if self.span_id:
            await self.engine.add_span_tag(self.span_id, key, value)
    
    def get_context(self) -> Optional[TraceContext]:
        """Get trace context for propagation"""
        if self.span_id:
            return self.engine.create_trace_context(self.span_id)
        return None

async def main():
    """Main function for testing"""
    config = DistributedTracingConfig(
        service_name="ainflue-api",
        jaeger_endpoint="http://localhost:14268"
    )
    
    engine = DistributedTracingEngine(config)
    await engine.initialize()
    
    # Example usage
    async with TracingContext(engine, "process_user_request") as trace:
        await trace.add_tag("user.id", "12345")
        await trace.add_log({"event": "request_started"})
        
        # Simulate some work
        await asyncio.sleep(0.1)
        
        # Child span
        child_context = trace.get_context()
        async with TracingContext(engine, "database_query", child_context) as child_trace:
            await child_trace.add_tag("db.query", "SELECT * FROM users")
            await asyncio.sleep(0.05)
        
        await trace.add_log({"event": "request_completed"})
    
    # Get performance summary
    summary = await engine.get_performance_summary()
    print(json.dumps(summary, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())