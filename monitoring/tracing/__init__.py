"""
Ainflue Platform - Distributed Tracing Module
=============================================

Enterprise-grade distributed tracing system for monitoring audio processing pipelines,
business transactions, microservices dependencies, and performance optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from contextlib import contextmanager
from collections import defaultdict, deque
import contextvars
import functools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpanType(Enum):
    """Types of distributed trace spans."""
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    AUDIO_PROCESSING = "audio_processing"
    AI_INFERENCE = "ai_inference"
    MICROSERVICE_CALL = "microservice_call"
    BUSINESS_TRANSACTION = "business_transaction"
    EXTERNAL_API = "external_api"
    CACHE_OPERATION = "cache_operation"
    FILE_OPERATION = "file_operation"
    QUEUE_OPERATION = "queue_operation"

class SpanStatus(Enum):
    """Status of trace spans."""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    RETRY = "retry"

@dataclass
class TraceSpan:
    """Individual trace span representing an operation."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    span_type: SpanType
    service_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: SpanStatus = SpanStatus.OK
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    business_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributedTrace:
    """Complete distributed trace with multiple spans."""
    trace_id: str
    root_span_id: str
    spans: Dict[str, TraceSpan] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_duration_ms: Optional[float] = None
    business_transaction_type: Optional[str] = None
    user_id: Optional[str] = None

class AudioProcessingTracer:
    """Specialized tracer for audio processing operations."""
    
    def __init__(self):
        self.audio_spans: Dict[str, TraceSpan] = {}
        
    def trace_audio_processing(self, operation: str, audio_format: str, 
                             processing_params: Dict[str, Any]) -> str:
        """Start tracing an audio processing operation."""
        span_id = str(uuid.uuid4())
        span = TraceSpan(
            span_id=span_id,
            trace_id=str(uuid.uuid4()),
            parent_span_id=None,
            operation_name=f"audio_processing.{operation}",
            span_type=SpanType.AUDIO_PROCESSING,
            service_name="audio_processing_service",
            start_time=datetime.utcnow(),
            tags={
                "audio.format": audio_format,
                "audio.operation": operation,
                "audio.params": json.dumps(processing_params)
            },
            business_context={
                "processing_type": operation,
                "input_format": audio_format,
                "parameters": processing_params
            }
        )
        
        self.audio_spans[span_id] = span
        logger.info(f"🎵 Started audio processing trace: {operation}")
        return span_id
    
    def finish_audio_processing(self, span_id: str, output_metrics: Dict[str, Any]):
        """Finish audio processing trace with metrics."""
        if span_id in self.audio_spans:
            span = self.audio_spans[span_id]
            span.end_time = datetime.utcnow()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            
            span.tags.update({
                "audio.output_quality": output_metrics.get("quality_score", 0),
                "audio.processing_time_ms": span.duration_ms,
                "audio.memory_usage_mb": output_metrics.get("memory_usage", 0),
                "audio.cpu_usage_percent": output_metrics.get("cpu_usage", 0)
            })
            
            logger.info(f"🎵 Finished audio processing trace: {span.operation_name} ({span.duration_ms:.2f}ms)")

class BusinessTransactionTracer:
    """Specialized tracer for business transactions."""
    
    def __init__(self):
        self.business_traces: Dict[str, DistributedTrace] = {}
        
    def start_business_transaction(self, transaction_type: str, user_id: str, 
                                 transaction_data: Dict[str, Any]) -> str:
        """Start tracing a business transaction."""
        trace_id = str(uuid.uuid4())
        root_span_id = str(uuid.uuid4())
        
        root_span = TraceSpan(
            span_id=root_span_id,
            trace_id=trace_id,
            parent_span_id=None,
            operation_name=f"business_transaction.{transaction_type}",
            span_type=SpanType.BUSINESS_TRANSACTION,
            service_name="business_service",
            start_time=datetime.utcnow(),
            tags={
                "transaction.type": transaction_type,
                "transaction.user_id": user_id,
                "transaction.data": json.dumps(transaction_data)
            },
            business_context={
                "transaction_type": transaction_type,
                "user_id": user_id,
                "transaction_value": transaction_data.get("value", 0),
                "currency": transaction_data.get("currency", "USD")
            }
        )
        
        trace = DistributedTrace(
            trace_id=trace_id,
            root_span_id=root_span_id,
            business_transaction_type=transaction_type,
            user_id=user_id
        )
        
        trace.spans[root_span_id] = root_span
        self.business_traces[trace_id] = trace
        
        logger.info(f"💼 Started business transaction trace: {transaction_type} for user {user_id}")
        return trace_id

class DistributedTracingSystem:
    """
    Enterprise distributed tracing system for Ainflue platform.
    
    Features:
    - Audio processing pipeline tracing
    - Business transaction correlation
    - Microservices dependency mapping
    - Performance bottleneck detection
    - Latency optimization tracking
    - Business context trace enrichment
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.traces: Dict[str, DistributedTrace] = {}
        self.active_spans: Dict[str, TraceSpan] = {}
        self.audio_tracer = AudioProcessingTracer()
        self.business_tracer = BusinessTransactionTracer()
        self.performance_thresholds: Dict[str, float] = {
            "audio_processing_ms": 5000,  # 5 seconds
            "database_query_ms": 1000,   # 1 second
            "microservice_call_ms": 2000, # 2 seconds
            "business_transaction_ms": 10000, # 10 seconds
            "external_api_ms": 5000       # 5 seconds
        }
        
        logger.info("🔍 Distributed Tracing System initialized")
    
    @contextmanager
    def start_trace(self, operation_name: str, service_name: str, 
                   span_type: SpanType = SpanType.HTTP_REQUEST,
                   business_context: Optional[Dict[str, Any]] = None):
        """
        Context manager for creating distributed traces.
        
        Args:
            operation_name: Name of the operation being traced
            service_name: Name of the service performing the operation
            span_type: Type of span being created
            business_context: Business context for the trace
        """
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=None,
            operation_name=operation_name,
            span_type=span_type,
            service_name=service_name,
            start_time=datetime.utcnow(),
            business_context=business_context or {}
        )
        
        trace = DistributedTrace(
            trace_id=trace_id,
            root_span_id=span_id
        )
        
        trace.spans[span_id] = span
        self.traces[trace_id] = trace
        self.active_spans[span_id] = span
        
        try:
            logger.info(f"🔍 Started trace: {operation_name} [{trace_id}]")
            yield trace
        
        except Exception as e:
            span.status = SpanStatus.ERROR
            span.logs.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": "ERROR",
                "message": str(e)
            })
            
            logger.error(f"❌ Trace error in {operation_name}: {e}")
            raise
        
        finally:
            span.end_time = datetime.utcnow()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            
            trace.end_time = span.end_time
            trace.total_duration_ms = span.duration_ms
            
            # Check performance thresholds
            threshold_key = f"{span.span_type.value}_ms"
            threshold = self.performance_thresholds.get(threshold_key)
            
            if threshold and span.duration_ms > threshold:
                logger.warning(f"⚠️ Performance threshold exceeded: {operation_name} ({span.duration_ms:.2f}ms > {threshold}ms)")
            
            if span_id in self.active_spans:
                del self.active_spans[span_id]
            
            logger.info(f"🔍 Finished trace: {operation_name} ({span.duration_ms:.2f}ms)")
    
    @contextmanager
    def start_span(self, operation_name: str, span_type: SpanType,
                  tags: Optional[Dict[str, Any]] = None,
                  business_context: Optional[Dict[str, Any]] = None):
        """Context manager for creating child spans."""
        span_id = str(uuid.uuid4())
        
        span = TraceSpan(
            span_id=span_id,
            trace_id=str(uuid.uuid4()),  # Simplified for now
            parent_span_id=None,
            operation_name=operation_name,
            span_type=span_type,
            service_name="unknown",
            start_time=datetime.utcnow(),
            tags=tags or {},
            business_context=business_context or {}
        )
        
        self.active_spans[span_id] = span
        
        try:
            logger.debug(f"🔗 Started span: {operation_name}")
            yield span
        
        except Exception as e:
            span.status = SpanStatus.ERROR
            span.logs.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": "ERROR",
                "message": str(e)
            })
            raise
        
        finally:
            span.end_time = datetime.utcnow()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            
            if span_id in self.active_spans:
                del self.active_spans[span_id]
            
            logger.debug(f"🔗 Finished span: {operation_name} ({span.duration_ms:.2f}ms)")
    
    async def get_trace_analytics(self, period_days: int = 7) -> Dict[str, Any]:
        """
        Get comprehensive trace analytics.
        
        Args:
            period_days: Analysis period in days
            
        Returns:
            Trace analytics data
        """
        try:
            period_start = datetime.utcnow() - timedelta(days=period_days)
            
            period_traces = [
                trace for trace in self.traces.values()
                if trace.start_time >= period_start
            ]
            
            if not period_traces:
                return {"status": "no_data", "message": "No traces found in period"}
            
            # Calculate analytics
            analytics = {
                "period_days": period_days,
                "total_traces": len(period_traces),
                "total_spans": sum(len(trace.spans) for trace in period_traces),
                "error_rate": self._calculate_error_rate(period_traces),
                "average_trace_duration": self._calculate_average_duration(period_traces),
                "service_performance": self._analyze_service_performance(period_traces),
                "bottleneck_analysis": self._analyze_bottlenecks(period_traces),
                "business_insights": self._analyze_business_metrics(period_traces)
            }
            
            logger.info(f"📊 Generated trace analytics for {period_days} days")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error generating trace analytics: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_error_rate(self, traces: List[DistributedTrace]) -> float:
        """Calculate error rate from traces."""
        total_spans = sum(len(trace.spans) for trace in traces)
        error_spans = sum(
            len([span for span in trace.spans.values() if span.status == SpanStatus.ERROR])
            for trace in traces
        )
        
        return error_spans / max(total_spans, 1)
    
    def _calculate_average_duration(self, traces: List[DistributedTrace]) -> float:
        """Calculate average trace duration."""
        durations = [trace.total_duration_ms for trace in traces if trace.total_duration_ms]
        return sum(durations) / max(len(durations), 1)
    
    def _analyze_service_performance(self, traces: List[DistributedTrace]) -> Dict[str, Any]:
        """Analyze performance by service."""
        service_metrics = defaultdict(lambda: {"durations": [], "error_count": 0, "total_count": 0})
        
        for trace in traces:
            for span in trace.spans.values():
                service = span.service_name
                service_metrics[service]["total_count"] += 1
                
                if span.duration_ms:
                    service_metrics[service]["durations"].append(span.duration_ms)
                
                if span.status == SpanStatus.ERROR:
                    service_metrics[service]["error_count"] += 1
        
        # Calculate aggregated metrics
        performance_data = {}
        for service, metrics in service_metrics.items():
            durations = metrics["durations"]
            performance_data[service] = {
                "average_duration_ms": sum(durations) / max(len(durations), 1),
                "error_rate": metrics["error_count"] / max(metrics["total_count"], 1),
                "total_operations": metrics["total_count"]
            }
        
        return performance_data
    
    def _analyze_bottlenecks(self, traces: List[DistributedTrace]) -> List[Dict[str, Any]]:
        """Analyze performance bottlenecks."""
        bottlenecks = []
        
        # Find spans with high duration
        all_spans = []
        for trace in traces:
            all_spans.extend(trace.spans.values())
        
        # Sort by duration
        sorted_spans = sorted([s for s in all_spans if s.duration_ms], 
                            key=lambda x: x.duration_ms, reverse=True)
        
        # Top 10 slowest operations
        for span in sorted_spans[:10]:
            bottlenecks.append({
                "operation": span.operation_name,
                "service": span.service_name,
                "duration_ms": span.duration_ms,
                "span_type": span.span_type.value,
                "trace_id": span.trace_id
            })
        
        return bottlenecks
    
    def _analyze_business_metrics(self, traces: List[DistributedTrace]) -> Dict[str, Any]:
        """Analyze business metrics from traces."""
        business_metrics = {
            "transaction_types": defaultdict(int),
            "user_journey_analysis": {},
            "revenue_impact": 0.0
        }
        
        for trace in traces:
            if trace.business_transaction_type:
                business_metrics["transaction_types"][trace.business_transaction_type] += 1
            
            # Analyze revenue impact from business context
            for span in trace.spans.values():
                if "transaction_value" in span.business_context:
                    business_metrics["revenue_impact"] += span.business_context["transaction_value"]
        
        return business_metrics

# Decorator for automatic tracing
def trace_operation(operation_name: str, span_type: SpanType = SpanType.HTTP_REQUEST,
                   tags: Optional[Dict[str, Any]] = None):
    """
    Decorator for automatic operation tracing.
    
    Args:
        operation_name: Name of the operation
        span_type: Type of span to create
        tags: Additional tags for the span
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            async with distributed_tracing_system.start_span(operation_name, span_type, tags):
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global instance
distributed_tracing_system = DistributedTracingSystem()

__all__ = [
    'DistributedTracingSystem',
    'TraceSpan',
    'DistributedTrace',
    'SpanType',
    'SpanStatus',
    'AudioProcessingTracer',
    'BusinessTransactionTracer',
    'trace_operation',
    'distributed_tracing_system'
]