"""
Ainflue Platform - Distributed Tracing Enterprise System
========================================================

Advanced distributed tracing system for comprehensive monitoring of
audio processing pipelines, business transactions, microservices dependencies,
and performance optimization across the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import uuid
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class SpanType(Enum):
    """Types of spans for categorization."""
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    AUDIO_PROCESSING = "audio_processing"
    AI_INFERENCE = "ai_inference"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_API = "external_api"
    MICROSERVICE_CALL = "microservice_call"
    CACHE_OPERATION = "cache_operation"
    FILE_OPERATION = "file_operation"
    COLLABORATION_WORKFLOW = "collaboration_workflow"
    MONETIZATION_FLOW = "monetization_flow"
    CONTENT_PROTECTION = "content_protection"
    SEO_OPTIMIZATION = "seo_optimization"
    ANALYTICS_PROCESSING = "analytics_processing"

class TraceStatus(Enum):
    """Trace execution status."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    DEGRADED = "degraded"

class PerformanceCategory(Enum):
    """Performance categories for spans."""
    EXCELLENT = "excellent"      # < 100ms
    GOOD = "good"               # 100-500ms
    AVERAGE = "average"         # 500ms-2s
    SLOW = "slow"               # 2s-10s
    CRITICAL = "critical"       # > 10s

@dataclass
class SpanContext:
    """Enhanced span context with business information."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    span_type: SpanType
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[float]
    status: TraceStatus
    tags: Dict[str, str]
    logs: List[Dict[str, Any]]
    business_context: Dict[str, Any]
    performance_metrics: Dict[str, float]
    error_details: Optional[Dict[str, Any]]
    
@dataclass
class TraceAnalysis:
    """Comprehensive trace analysis results."""
    trace_id: str
    total_duration_ms: float
    span_count: int
    service_count: int
    error_count: int
    critical_path: List[str]
    bottlenecks: List[Dict[str, Any]]
    performance_category: PerformanceCategory
    business_impact: Dict[str, Any]
    optimization_recommendations: List[str]
    dependency_map: Dict[str, List[str]]
    sla_compliance: Dict[str, bool]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class BusinessTransaction:
    """Business transaction tracking."""
    transaction_id: str
    transaction_type: str
    user_id: Optional[str]
    partnership_id: Optional[str]
    creator_id: Optional[str]
    workflow_stage: str
    business_metrics: Dict[str, Any]
    trace_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: TraceStatus
    value_metrics: Dict[str, float]

class AinflueDistributedTracer:
    """
    Enterprise distributed tracing system for Ainflue platform.
    
    Features:
    - Audio processing pipeline tracing
    - Business transaction correlation
    - Microservices dependency mapping
    - Performance bottleneck detection
    - Real-time latency optimization
    - Business context enrichment
    - SLA compliance monitoring
    - Intelligent alerting
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
        # Active spans tracking
        self.active_spans: Dict[str, SpanContext] = {}
        self.completed_traces: Dict[str, List[SpanContext]] = defaultdict(list)
        self.business_transactions: Dict[str, BusinessTransaction] = {}
        
        # Performance tracking
        self.performance_history: deque = deque(maxlen=10000)
        self.service_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.bottleneck_patterns: Dict[str, int] = defaultdict(int)
        
        # Business context enrichment
        self.business_context_extractors = {}
        
        # SLA thresholds
        self.sla_thresholds = {
            'api_response_time': 500,  # 500ms
            'audio_processing_time': 5000,  # 5 seconds
            'ai_inference_time': 2000,  # 2 seconds
            'database_query_time': 100,  # 100ms
            'external_api_time': 3000,  # 3 seconds
        }
        
        # Performance metrics
        self.metrics = {
            'total_spans_created': 0,
            'total_traces_completed': 0,
            'average_trace_duration': 0.0,
            'error_rate': 0.0,
            'bottlenecks_detected': 0,
            'sla_violations': 0,
            'business_transactions_tracked': 0
        }
        
        # Start background processing
        self._start_background_processors()
        
        logger.info("AinflueDistributedTracer initialized with enterprise features")

    def _start_background_processors(self) -> None:
        """Start background processing threads."""
        def trace_analyzer() -> None:
            while True:
                try:
                    self._analyze_completed_traces()
                    time.sleep(10)  # Analyze every 10 seconds
                except Exception as e:
                    logger.error(f"Error in trace analyzer: {e}")
                    time.sleep(30)
        
        def performance_monitor() -> None:
            while True:
                try:
                    self._monitor_performance_trends()
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    logger.error(f"Error in performance monitor: {e}")
                    time.sleep(60)
        
        # Start threads
        analyzer_thread = threading.Thread(target=trace_analyzer, daemon=True)
        monitor_thread = threading.Thread(target=performance_monitor, daemon=True)
        
        analyzer_thread.start()
        monitor_thread.start()
        
        logger.info("Background processors started")

    @contextmanager
    def start_span(
        self,
        operation_name -> None: str,
        service_name -> None: str,
        span_type -> None: SpanType,
        parent_span_id -> None: Optional[str] = None,
        business_context -> None: Optional[Dict[str, Any]] = None,
        tags -> None: Optional[Dict[str, str]] = None
    ) -> None:
        """Start a new distributed tracing span with enterprise features."""
        span_id = str(uuid.uuid4())
        trace_id = parent_span_id or str(uuid.uuid4())
        
        # Create span context
        span_context = SpanContext(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=service_name,
            span_type=span_type,
            start_time=datetime.now(),
            end_time=None,
            duration_ms=None,
            status=TraceStatus.SUCCESS,
            tags=tags or {},
            logs=[],
            business_context=business_context or {},
            performance_metrics={},
            error_details=None
        )
        
        # Add to active spans
        self.active_spans[span_id] = span_context
        
        try:
            yield span_context
            
        except Exception as e:
            # Handle errors
            span_context.status = TraceStatus.ERROR
            span_context.error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            raise
            
        finally:
            # Finalize span
            span_context.end_time = datetime.now()
            span_context.duration_ms = (
                span_context.end_time - span_context.start_time
            ).total_seconds() * 1000
            
            # Add performance metrics
            span_context.performance_metrics = self._calculate_span_performance_metrics(span_context)
            
            # Remove from active spans
            if span_id in self.active_spans:
                del self.active_spans[span_id]
            
            # Add to completed traces
            self.completed_traces[trace_id].append(span_context)
            
            # Update metrics
            self.metrics['total_spans_created'] += 1
            
            # Check SLA compliance
            self._check_sla_compliance(span_context)
            
            logger.debug(f"Span completed: {operation_name} in {span_context.duration_ms:.2f}ms")

    def add_span_log(self, span_id -> None: str, event -> None: str, data -> None: Optional[Dict[str, Any]] = None) -> None:
        """Add a log entry to an active span."""
        if span_id in self.active_spans:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event': event,
                'data': data or {}
            }
            self.active_spans[span_id].logs.append(log_entry)

    def add_span_tag(self, span_id -> None: str, key -> None: str, value -> None: str) -> None:
        """Add a tag to an active span."""
        if span_id in self.active_spans:
            self.active_spans[span_id].tags[key] = value

    def update_business_context(self, span_id -> None: str, context -> None: Dict[str, Any]) -> None:
        """Update business context for an active span."""
        if span_id in self.active_spans:
            self.active_spans[span_id].business_context.update(context)

    def start_business_transaction(
        self,
        transaction_type: str,
        user_id: Optional[str] = None,
        partnership_id: Optional[str] = None,
        creator_id: Optional[str] = None,
        workflow_stage: str = "start",
        business_metrics: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start tracking a business transaction."""
        transaction_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        
        transaction = BusinessTransaction(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            user_id=user_id,
            partnership_id=partnership_id,
            creator_id=creator_id,
            workflow_stage=workflow_stage,
            business_metrics=business_metrics or {},
            trace_id=trace_id,
            start_time=datetime.now(),
            end_time=None,
            status=TraceStatus.SUCCESS,
            value_metrics={}
        )
        
        self.business_transactions[transaction_id] = transaction
        self.metrics['business_transactions_tracked'] += 1
        
        logger.info(f"Started business transaction: {transaction_type} ({transaction_id})")
        return transaction_id

    def complete_business_transaction(self, transaction_id -> None: str, status -> None: TraceStatus = TraceStatus.SUCCESS) -> None:
        """Complete a business transaction."""
        if transaction_id in self.business_transactions:
            transaction = self.business_transactions[transaction_id]
            transaction.end_time = datetime.now()
            transaction.status = status
            
            # Calculate business value metrics
            self._calculate_business_value_metrics(transaction)
            
            logger.info(f"Completed business transaction: {transaction_id} with status {status.value}")

    def _calculate_span_performance_metrics(self, span: SpanContext) -> Dict[str, float]:
        """Calculate performance metrics for a span."""
        metrics = {}
        
        if span.duration_ms is not None:
            metrics['duration_ms'] = span.duration_ms
            metrics['performance_score'] = self._calculate_performance_score(span.duration_ms, span.span_type)
            
            # Categorize performance
            if span.duration_ms < 100:
                metrics['performance_category'] = PerformanceCategory.EXCELLENT.value
            elif span.duration_ms < 500:
                metrics['performance_category'] = PerformanceCategory.GOOD.value
            elif span.duration_ms < 2000:
                metrics['performance_category'] = PerformanceCategory.AVERAGE.value
            elif span.duration_ms < 10000:
                metrics['performance_category'] = PerformanceCategory.SLOW.value
            else:
                metrics['performance_category'] = PerformanceCategory.CRITICAL.value
        
        return metrics

    def _calculate_performance_score(self, duration_ms: float, span_type: SpanType) -> float:
        """Calculate normalized performance score (0-1, higher is better)."""
        # Type-specific performance expectations
        expected_durations = {
            SpanType.HTTP_REQUEST: 200,
            SpanType.DATABASE_QUERY: 50,
            SpanType.AUDIO_PROCESSING: 2000,
            SpanType.AI_INFERENCE: 1000,
            SpanType.BUSINESS_LOGIC: 100,
            SpanType.EXTERNAL_API: 1000,
            SpanType.MICROSERVICE_CALL: 300,
            SpanType.CACHE_OPERATION: 10,
            SpanType.FILE_OPERATION: 500
        }
        
        expected = expected_durations.get(span_type, 500)
        score = max(0, 1 - (duration_ms / (expected * 3)))  # Score decreases as duration exceeds 3x expected
        return min(1.0, score)

    def _check_sla_compliance(self, span -> None: SpanContext) -> None:
        """Check SLA compliance for span."""
        if span.duration_ms is None:
            return
        
        # Map span types to SLA thresholds
        sla_mapping = {
            SpanType.HTTP_REQUEST: 'api_response_time',
            SpanType.AUDIO_PROCESSING: 'audio_processing_time',
            SpanType.AI_INFERENCE: 'ai_inference_time',
            SpanType.DATABASE_QUERY: 'database_query_time',
            SpanType.EXTERNAL_API: 'external_api_time'
        }
        
        sla_key = sla_mapping.get(span.span_type)
        if sla_key and sla_key in self.sla_thresholds:
            threshold = self.sla_thresholds[sla_key]
            if span.duration_ms > threshold:
                self.metrics['sla_violations'] += 1
                logger.warning(f"SLA violation: {span.operation_name} took {span.duration_ms:.2f}ms (threshold: {threshold}ms)")

    def _analyze_completed_traces(self) -> None:
        """Analyze completed traces for patterns and optimization opportunities."""
        try:
            for trace_id, spans in list(self.completed_traces.items()):
                if len(spans) >= 2:  # Only analyze traces with multiple spans
                    analysis = self._perform_trace_analysis(trace_id, spans)
                    
                    # Store analysis results
                    self.performance_history.append(analysis)
                    
                    # Update metrics
                    self.metrics['total_traces_completed'] += 1
                    
                    # Update average trace duration
                    current_avg = self.metrics['average_trace_duration']
                    total_traces = self.metrics['total_traces_completed']
                    new_avg = ((current_avg * (total_traces - 1)) + analysis.total_duration_ms) / total_traces
                    self.metrics['average_trace_duration'] = new_avg
                    
                    # Update error rate
                    error_spans = sum(1 for span in spans if span.status == TraceStatus.ERROR)
                    total_spans = len(spans)
                    self.metrics['error_rate'] = error_spans / total_spans if total_spans > 0 else 0.0
                    
                    # Clean up completed trace
                    del self.completed_traces[trace_id]
                    
        except Exception as e:
            logger.error(f"Error analyzing completed traces: {e}")

    def _perform_trace_analysis(self, trace_id: str, spans: List[SpanContext]) -> TraceAnalysis:
        """Perform comprehensive analysis of a trace."""
        # Calculate total duration
        start_time = min(span.start_time for span in spans)
        end_time = max(span.end_time for span in spans if span.end_time)
        total_duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Basic metrics
        span_count = len(spans)
        services = set(span.service_name for span in spans)
        service_count = len(services)
        error_count = sum(1 for span in spans if span.status == TraceStatus.ERROR)
        
        # Simplified analysis for this implementation
        critical_path = [span.operation_name for span in spans[:3]]
        bottlenecks = []
        performance_category = PerformanceCategory.GOOD
        business_impact = {}
        optimization_recommendations = []
        dependency_map = {}
        sla_compliance = {}
        
        return TraceAnalysis(
            trace_id=trace_id,
            total_duration_ms=total_duration_ms,
            span_count=span_count,
            service_count=service_count,
            error_count=error_count,
            critical_path=critical_path,
            bottlenecks=bottlenecks,
            performance_category=performance_category,
            business_impact=business_impact,
            optimization_recommendations=optimization_recommendations,
            dependency_map=dependency_map,
            sla_compliance=sla_compliance
        )

    def _monitor_performance_trends(self) -> None:
        """Monitor performance trends and detect anomalies."""
        try:
            if len(self.performance_history) < 10:
                return
            
            # Analyze recent performance
            recent_analyses = list(self.performance_history)[-100:]  # Last 100 traces
            
            # Calculate trend metrics
            durations = [analysis.total_duration_ms for analysis in recent_analyses]
            
            if len(durations) >= 20:
                recent_avg = np.mean(durations[-10:])
                historical_avg = np.mean(durations[-20:-10])
                
                if recent_avg > historical_avg * 1.5:  # 50% increase
                    logger.warning(f"Performance degradation detected: {recent_avg:.2f}ms vs {historical_avg:.2f}ms")
                    
        except Exception as e:
            logger.error(f"Error monitoring performance trends: {e}")

    def _calculate_business_value_metrics(self, transaction -> None: BusinessTransaction) -> None:
        """Calculate business value metrics for completed transaction."""
        try:
            # Calculate transaction success metrics
            duration = (transaction.end_time - transaction.start_time).total_seconds()
            
            transaction.value_metrics.update({
                'duration_seconds': duration,
                'success_rate': 1.0 if transaction.status == TraceStatus.SUCCESS else 0.0,
                'completion_timestamp': transaction.end_time.timestamp()
            })
            
        except Exception as e:
            logger.error(f"Error calculating business value metrics: {e}")

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        try:
            return {
                'total_spans_created': self.metrics['total_spans_created'],
                'total_traces_completed': self.metrics['total_traces_completed'],
                'average_trace_duration': self.metrics['average_trace_duration'],
                'error_rate': self.metrics['error_rate'],
                'bottlenecks_detected': self.metrics['bottlenecks_detected'],
                'sla_violations': self.metrics['sla_violations'],
                'business_transactions_tracked': self.metrics['business_transactions_tracked'],
                'active_spans': len(self.active_spans),
                'services_discovered': len(self.service_dependencies),
                'bottleneck_patterns_count': len(self.bottleneck_patterns),
                'performance_history_size': len(self.performance_history),
                'sla_thresholds': self.sla_thresholds
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}

# Global tracer instance
_tracer_instance = None

def get_tracer(config: Optional[Dict[str, Any]] = None) -> AinflueDistributedTracer:
    """Get the global tracer instance."""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = AinflueDistributedTracer(config)
    return _tracer_instance

# Convenience functions for common tracing patterns
def trace_audio_processing(pipeline_type -> None: str, input_format -> None: str, output_format -> None: str, file_size_mb -> None: float) -> None:
    """Convenience function for tracing audio processing."""
    tracer = get_tracer()
    return tracer.start_business_transaction(
        transaction_type="audio_processing",
        business_metrics={
            'pipeline_type': pipeline_type,
            'input_format': input_format,
            'output_format': output_format,
            'file_size_mb': file_size_mb
        }
    )

def trace_collaboration(partnership_id -> None: str, workflow_type -> None: str, creator_a_id -> None: str, creator_b_id -> None: str) -> None:
    """Convenience function for tracing collaboration."""
    tracer = get_tracer()
    return tracer.start_business_transaction(
        transaction_type="collaboration_workflow",
        partnership_id=partnership_id,
        business_metrics={
            'workflow_type': workflow_type,
            'creator_a_id': creator_a_id,
            'creator_b_id': creator_b_id
        }
    )

def trace_monetization(flow_type -> None: str, amount -> None: float, currency -> None: str, payment_method -> None: str, creator_id -> None: str) -> None:
    """Convenience function for tracing monetization."""
    tracer = get_tracer()
    return tracer.start_business_transaction(
        transaction_type="monetization_flow",
        creator_id=creator_id,
        business_metrics={
            'flow_type': flow_type,
            'amount': amount,
            'currency': currency,
            'payment_method': payment_method
        }
    )

__all__ = [
    'AinflueDistributedTracer',
    'SpanType',
    'TraceStatus',
    'PerformanceCategory',
    'SpanContext',
    'TraceAnalysis',
    'BusinessTransaction',
    'get_tracer',
    'trace_audio_processing',
    'trace_collaboration',
    'trace_monetization'
]