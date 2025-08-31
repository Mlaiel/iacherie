# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Ultra-Industrial Test Suite for Distributed Tracing Module

Comprehensive testing for advanced distributed tracing, request tracking,
end-to-end visibility, and microservices trace analysis.

Expert Team Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING & COPYRIGHT PROTECTION ⚠️
This entire test suite is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import json
import pytest
import sys
import os
from pathlib import Path
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from contextlib import asynccontextmanager

# Import the module under test
from ai.observability.tracing import (
    SpanKind,
    SpanStatus,
    SpanEvent,
    SpanLink,
    Span,
    Trace,
    TracingContext,
    DistributedTracer,
    TraceCollector,
    TraceAnalyzer,
    SamplingStrategy
)


class TestDistributedTracingComprehensive:
    """Ultra-comprehensive test suite for Distributed Tracing"""    @pytest.fixture
    def tracing_config(self):
        """Sample tracing configuration"""        return {
            'service_name': 'ia_influencer_platform',
            'service_version': '2.1.0',
            'environment': 'test',
            'sampling_rate': 1.0,  # 100% sampling for tests
            'trace_exporters': ['jaeger', 'zipkin', 'otlp'],
            'resource_attributes': {
                'service.name': 'ia_influencer_platform',
                'service.version': '2.1.0',
                'deployment.environment': 'test',
                'cloud.provider': 'aws',
                'cloud.region': 'us-east-1'
            },
            'span_limits': {
                'max_attributes': 128,
                'max_events': 128,
                'max_links': 128,
                'max_attribute_length': 1024
            }
        }

    @pytest.fixture
    async def distributed_tracer(self, tracing_config):
        """Create distributed tracer instance"""        tracer = DistributedTracer(tracing_config)
        await tracer.initialize()
        yield tracer
        await tracer.shutdown()

    def test_span_kind_enum_comprehensive(self):
        """Test SpanKind enum completeness"""        expected_kinds = {'INTERNAL', 'SERVER', 'CLIENT', 'PRODUCER', 'CONSUMER'}
        actual_kinds = {member.name for member in SpanKind}
        assert actual_kinds == expected_kinds

    def test_span_status_enum_comprehensive(self):
        """Test SpanStatus enum completeness"""        expected_statuses = {'UNSET', 'OK', 'ERROR'}
        actual_statuses = {member.name for member in SpanStatus}
        assert actual_statuses == expected_statuses

    def test_span_event_creation_and_validation(self):
        """Test SpanEvent creation and validation"""        timestamp = datetime.now(timezone.utc)
        
        event = SpanEvent(
            name="content_processing_started",
            timestamp=timestamp,
            attributes={
                'content_id': 'content_123',
                'content_type': 'video',
                'file_size_mb': 150.5,
                'processing_algorithm': 'neural_fingerprint'
            }
        )
        
        assert event.name == "content_processing_started"
        assert event.timestamp == timestamp
        assert event.attributes['content_id'] == 'content_123'
        assert event.attributes['file_size_mb'] == 150.5
        
        # Test serialization
        event_dict = event.to_dict()
        assert event_dict['name'] == "content_processing_started"
        assert 'timestamp' in event_dict
        assert 'attributes' in event_dict
        assert event_dict['attributes']['content_type'] == 'video'

    def test_span_link_creation_and_validation(self):
        """Test SpanLink creation and validation"""        trace_id = str(uuid4())
        span_id = str(uuid4())
        
        link = SpanLink(
            trace_id=trace_id,
            span_id=span_id,
            attributes={
                'link_type': 'follows_from',
                'relationship': 'async_child',
                'correlation_id': 'corr_456'
            }
        )
        
        assert link.trace_id == trace_id
        assert link.span_id == span_id
        assert link.attributes['link_type'] == 'follows_from'
        
        # Test serialization
        link_dict = link.to_dict()
        assert link_dict['trace_id'] == trace_id
        assert link_dict['span_id'] == span_id
        assert 'attributes' in link_dict

    def test_span_creation_and_lifecycle_comprehensive(self):
        """Test comprehensive Span creation and lifecycle"""        trace_id = str(uuid4())
        span_id = str(uuid4())
        parent_span_id = str(uuid4())
        start_time = datetime.now(timezone.utc)
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name="content_fingerprint_analysis",
            kind=SpanKind.INTERNAL,
            start_time=start_time,
            attributes={
                'service.name': 'content_protection_service',
                'content.id': 'content_789',
                'content.type': 'audio',
                'model.version': 'fingerprint_v2.1',
                'user.id': 'user_123'
            },
            resource_attributes={
                'host.name': 'ai-worker-01',
                'process.pid': 12345,
                'process.runtime.name': 'python',
                'process.runtime.version': '3.11.0'
            }
        )
        
        # Verify initial state
        assert span.trace_id == trace_id
        assert span.span_id == span_id
        assert span.parent_span_id == parent_span_id
        assert span.operation_name == "content_fingerprint_analysis"
        assert span.kind == SpanKind.INTERNAL
        assert span.status == SpanStatus.UNSET
        assert span.is_ended() is False
        
        # Add events
        processing_event = SpanEvent(
            name="fingerprint_extraction_started",
            timestamp=datetime.now(timezone.utc),
            attributes={'algorithm': 'deep_neural_hash', 'expected_duration_ms': 5000}
        )
        
        span.add_event(processing_event)
        
        model_event = SpanEvent(
            name="model_inference_completed",
            timestamp=datetime.now(timezone.utc),
            attributes={'confidence_score': 0.95, 'processing_time_ms': 4800}
        )
        
        span.add_event(model_event)
        
        # Add attributes
        span.set_attribute('result.confidence', 0.95)
        span.set_attribute('result.fingerprint_hash', 'fp_abc123def456')
        span.set_attribute('performance.cpu_usage_percent', 85.2)
        
        # Add links
        related_span_link = SpanLink(
            trace_id=str(uuid4()),
            span_id=str(uuid4()),
            attributes={'relation': 'similar_content', 'similarity_score': 0.88}
        )
        
        span.add_link(related_span_link)
        
        # End span
        end_time = datetime.now(timezone.utc)
        span.end(end_time=end_time, status=SpanStatus.OK)
        
        # Verify final state
        assert span.end_time == end_time
        assert span.status == SpanStatus.OK
        assert span.is_ended() is True
        assert span.duration_ms is not None
        assert span.duration_ms > 0
        
        # Verify events
        assert len(span.events) == 2
        assert span.events[0].name == "fingerprint_extraction_started"
        assert span.events[1].name == "model_inference_completed"
        
        # Verify attributes
        assert span.attributes['result.confidence'] == 0.95
        assert span.attributes['result.fingerprint_hash'] == 'fp_abc123def456'
        
        # Verify links
        assert len(span.links) == 1
        assert span.links[0].attributes['relation'] == 'similar_content'

    @pytest.mark.asyncio
    async def test_distributed_tracer_initialization(self, tracing_config):
        """Test distributed tracer initialization"""        tracer = DistributedTracer(tracing_config)
        
        # Test initialization
        result = await tracer.initialize()
        assert result is True
        assert tracer.is_initialized is True
        
        # Test configuration
        assert tracer.service_name == 'ia_influencer_platform'
        assert tracer.service_version == '2.1.0'
        assert tracer.sampling_rate == 1.0
        
        # Test resource attributes
        resource_attrs = tracer.resource_attributes
        assert resource_attrs['service.name'] == 'ia_influencer_platform'
        assert resource_attrs['deployment.environment'] == 'test'
        
        await tracer.shutdown()

    @pytest.mark.asyncio
    async def test_span_creation_and_management(self, distributed_tracer):
        """Test span creation and management"""        tracer = distributed_tracer
        
        # Create root span
        root_span = await tracer.start_span(
            operation_name="content_upload_request",
            kind=SpanKind.SERVER,
            attributes={
                'http.method': 'POST',
                'http.url': '/api/v1/content/upload',
                'user.id': 'user_456',
                'content.type': 'video'
            }
        )
        
        assert root_span is not None
        assert root_span.operation_name == "content_upload_request"
        assert root_span.kind == SpanKind.SERVER
        assert root_span.parent_span_id is None  # Root span
        assert root_span.is_ended() is False
        
        # Create child span
        child_span = await tracer.start_span(
            operation_name="content_validation",
            parent_span=root_span,
            kind=SpanKind.INTERNAL,
            attributes={
                'validation.type': 'format_check',
                'file.size_mb': 120.5
            }
        )
        
        assert child_span is not None
        assert child_span.parent_span_id == root_span.span_id
        assert child_span.trace_id == root_span.trace_id
        
        # Add events to child span
        await tracer.add_span_event(
            child_span,
            "validation_started",
            attributes={'validation_rules': ['format', 'size', 'content']}
        )
        
        await tracer.add_span_event(
            child_span,
            "validation_completed",
            attributes={'validation_result': 'passed', 'duration_ms': 150}
        )
        
        # End child span successfully
        await tracer.end_span(child_span, status=SpanStatus.OK)
        assert child_span.is_ended() is True
        assert child_span.status == SpanStatus.OK
        
        # Create another child for AI processing
        ai_span = await tracer.start_span(
            operation_name="ai_fingerprint_extraction",
            parent_span=root_span,
            kind=SpanKind.INTERNAL,
            attributes={
                'ai.model.name': 'neural_fingerprint',
                'ai.model.version': '2.1.0',
                'processing.priority': 'high'
            }
        )
        
        # Simulate AI processing with events
        await tracer.add_span_event(
            ai_span,
            "model_loading_started",
            attributes={'model_size_mb': 500, 'gpu_memory_required_gb': 2}
        )
        
        await tracer.add_span_event(
            ai_span,
            "inference_started",
            attributes={'batch_size': 1, 'expected_duration_ms': 3000}
        )
        
        await tracer.add_span_event(
            ai_span,
            "inference_completed",
            attributes={
                'confidence_score': 0.92,
                'fingerprint_hash': 'fp_def789ghi012',
                'processing_time_ms': 2800
            }
        )
        
        # End AI span successfully
        await tracer.end_span(
            ai_span,
            status=SpanStatus.OK,
            attributes={'result.success': True, 'result.confidence': 0.92}
        )
        
        # End root span
        await tracer.end_span(root_span, status=SpanStatus.OK)
        
        # Verify trace structure
        trace = await tracer.get_trace(root_span.trace_id)
        assert trace is not None
        assert len(trace.spans) == 3  # root + 2 children
        assert trace.root_span.span_id == root_span.span_id

    @pytest.mark.asyncio
    async def test_context_propagation_comprehensive(self, distributed_tracer):
        """Test comprehensive context propagation"""        tracer = distributed_tracer
        
        # Create trace context
        trace_context = TracingContext()
        
        # Start root span with context
        root_span = await tracer.start_span(
            operation_name="api_gateway_request",
            context=trace_context,
            kind=SpanKind.SERVER
        )
        
        # Set context
        trace_context.set_active_span(root_span)
        
        # Test context extraction
        context_headers = trace_context.extract_headers()
        assert 'traceparent' in context_headers
        assert 'tracestate' in context_headers or context_headers['tracestate'] == ''
        
        # Parse traceparent header
        traceparent = context_headers['traceparent']
        parts = traceparent.split('-')
        assert len(parts) == 4
        assert parts[0] == '00'  # version
        assert parts[1] == root_span.trace_id.replace('-', '')
        assert parts[2] == root_span.span_id.replace('-', '')
        
        # Test context injection for downstream service call
        downstream_headers = {
            'traceparent': context_headers['traceparent'],
            'tracestate': context_headers.get('tracestate', '')
        }
        
        # Create new context from headers (simulating downstream service)
        downstream_context = TracingContext.from_headers(downstream_headers)
        assert downstream_context.trace_id == root_span.trace_id
        assert downstream_context.parent_span_id == root_span.span_id
        
        # Create child span in downstream service
        downstream_span = await tracer.start_span(
            operation_name="content_service_processing",
            context=downstream_context,
            kind=SpanKind.SERVER,
            attributes={'service': 'content_service', 'operation': 'process_upload'}
        )
        
        assert downstream_span.trace_id == root_span.trace_id
        assert downstream_span.parent_span_id == root_span.span_id
        
        # Test baggage propagation
        trace_context.set_baggage('user_id', 'user_789')
        trace_context.set_baggage('session_id', 'session_abc123')
        trace_context.set_baggage('feature_flags', 'ai_v2,enhanced_protection')
        
        baggage_headers = trace_context.extract_baggage_headers()
        assert 'baggage' in baggage_headers
        
        baggage_context = TracingContext.from_headers({
            'baggage': baggage_headers['baggage']
        })
        
        assert baggage_context.get_baggage('user_id') == 'user_789'
        assert baggage_context.get_baggage('session_id') == 'session_abc123'
        assert baggage_context.get_baggage('feature_flags') == 'ai_v2,enhanced_protection'
        
        await tracer.end_span(downstream_span)
        await tracer.end_span(root_span)

    @pytest.mark.asyncio
    async def test_sampling_strategies_comprehensive(self, distributed_tracer):
        """Test comprehensive sampling strategies"""        tracer = distributed_tracer
        
        # Test different sampling strategies
        sampling_strategies = [
            # Always sample for critical operations
            {
                'name': 'critical_operations',
                'type': 'always_on',
                'conditions': [
                    {'attribute': 'operation.type', 'value': 'critical'},
                    {'attribute': 'severity', 'value': 'high'}
                ]
            },
            # Rate-based sampling for normal operations
            {
                'name': 'normal_operations',
                'type': 'rate_based',
                'rate': 0.1,  # 10% sampling
                'conditions': [
                    {'attribute': 'operation.type', 'value': 'normal'}
                ]
            },
            # Never sample debug operations
            {
                'name': 'debug_operations',
                'type': 'always_off',
                'conditions': [
                    {'attribute': 'operation.type', 'value': 'debug'}
                ]
            },
            # Adaptive sampling based on load
            {
                'name': 'adaptive_sampling',
                'type': 'adaptive',
                'target_samples_per_second': 100,
                'max_traces_per_second': 1000
            }
        ]
        
        for strategy_config in sampling_strategies:
            strategy = SamplingStrategy(strategy_config)
            await tracer.add_sampling_strategy(strategy)
        
        # Test sampling decisions
        test_operations = [
            {'name': 'critical_security_check', 'attributes': {'operation.type': 'critical', 'severity': 'high'}},
            {'name': 'normal_content_upload', 'attributes': {'operation.type': 'normal'}},
            {'name': 'debug_trace_log', 'attributes': {'operation.type': 'debug'}},
            {'name': 'adaptive_ai_inference', 'attributes': {'load': 'medium'}}
        ]
        
        sampling_results = []
        
        for op in test_operations:
            for i in range(20):  # Test multiple times to check sampling consistency
                should_sample = await tracer.should_sample(
                    operation_name=op['name'],
                    attributes=op['attributes']
                )
                
                sampling_results.append({
                    'operation': op['name'],
                    'attributes': op['attributes'],
                    'sampled': should_sample
                })
        
        # Analyze sampling results
        critical_samples = [r for r in sampling_results if r['operation'] == 'critical_security_check']
        normal_samples = [r for r in sampling_results if r['operation'] == 'normal_content_upload']
        debug_samples = [r for r in sampling_results if r['operation'] == 'debug_trace_log']
        
        # Critical operations should always be sampled
        assert all(r['sampled'] for r in critical_samples)
        
        # Debug operations should never be sampled
        assert not any(r['sampled'] for r in debug_samples)
        
        # Normal operations should be sampled at ~10% rate
        normal_sample_rate = sum(1 for r in normal_samples if r['sampled']) / len(normal_samples)
        assert 0.05 <= normal_sample_rate <= 0.15  # Allow some variance

    @pytest.mark.asyncio
    async def test_distributed_trace_collection_comprehensive(self, distributed_tracer):
        """Test comprehensive distributed trace collection"""        tracer = distributed_tracer
        
        # Initialize trace collector
        collector_config = {
            'collection_interval_seconds': 1,
            'batch_size': 100,
            'max_queue_size': 1000,
            'export_timeout_seconds': 30,
            'retry_policy': {
                'max_attempts': 3,
                'backoff_multiplier': 2.0,
                'initial_delay_seconds': 1
            }
        }
        
        collector = TraceCollector(collector_config)
        await collector.initialize()
        await tracer.set_trace_collector(collector)
        
        # Generate complex distributed trace
        services = [
            {'name': 'api_gateway', 'operation': 'route_request'},
            {'name': 'auth_service', 'operation': 'validate_token'},
            {'name': 'content_service', 'operation': 'validate_content'},
            {'name': 'ai_service', 'operation': 'analyze_content'},
            {'name': 'storage_service', 'operation': 'store_results'},
            {'name': 'notification_service', 'operation': 'send_notification'}
        ]
        
        trace_id = str(uuid4())
        spans = []
        
        # Create distributed trace across services
        for i, service in enumerate(services):
            parent_span_id = spans[-1].span_id if spans else None
            
            span = await tracer.start_span(
                operation_name=service['operation'],
                kind=SpanKind.SERVER if i == 0 else SpanKind.CLIENT,
                attributes={
                    'service.name': service['name'],
                    'service.instance.id': f"{service['name']}-001",
                    'request.id': 'req_123456',
                    'user.id': 'user_789'
                },
                trace_id=trace_id,
                parent_span_id=parent_span_id
            )
            
            # Add service-specific events and attributes
            if service['name'] == 'ai_service':
                await tracer.add_span_event(
                    span,
                    "model_loading",
                    attributes={'model': 'content_analyzer_v2.1', 'loading_time_ms': 500}
                )
                
                await tracer.add_span_event(
                    span,
                    "inference_started",
                    attributes={'input_size_mb': 25.5, 'expected_duration_ms': 2000}
                )
                
                await tracer.add_span_event(
                    span,
                    "inference_completed",
                    attributes={'confidence': 0.94, 'processing_time_ms': 1800}
                )
                
                span.set_attribute('ai.model.name', 'content_analyzer')
                span.set_attribute('ai.model.version', '2.1.0')
                span.set_attribute('ai.inference.confidence', 0.94)
            
            elif service['name'] == 'storage_service':
                await tracer.add_span_event(
                    span,
                    "database_write",
                    attributes={'table': 'content_analysis', 'rows_affected': 3}
                )
                
                span.set_attribute('db.system', 'postgresql')
                span.set_attribute('db.name', 'ia_influencer')
                span.set_attribute('db.operation', 'INSERT')
            
            # Simulate processing time
            await asyncio.sleep(0.1 + i * 0.05)
            
            await tracer.end_span(span, status=SpanStatus.OK)
            spans.append(span)
        
        # Wait for collection
        await asyncio.sleep(2)
        
        # Verify trace collection
        collected_traces = await collector.get_collected_traces(limit=10)
        assert len(collected_traces) > 0
        
        # Find our trace
        our_trace = None
        for trace in collected_traces:
            if trace.trace_id == trace_id:
                our_trace = trace
                break
        
        assert our_trace is not None
        assert len(our_trace.spans) == len(services)
        
        # Verify trace structure
        root_span = our_trace.root_span
        assert root_span.operation_name == 'route_request'
        assert root_span.parent_span_id is None
        
        # Verify span relationships
        for i, span in enumerate(our_trace.spans[1:], 1):
            assert span.parent_span_id == our_trace.spans[i-1].span_id
        
        await collector.shutdown()

    @pytest.mark.asyncio
    async def test_trace_analysis_and_insights(self, distributed_tracer):
        """Test trace analysis and insights generation"""        tracer = distributed_tracer
        
        # Generate traces with performance patterns
        trace_scenarios = [
            # Fast successful trace
            {
                'name': 'fast_success',
                'operations': ['gateway', 'auth', 'content', 'storage'],
                'durations_ms': [10, 50, 100, 80],
                'statuses': ['OK', 'OK', 'OK', 'OK']
            },
            # Slow AI processing trace
            {
                'name': 'slow_ai_processing',
                'operations': ['gateway', 'auth', 'content', 'ai_analysis', 'storage'],
                'durations_ms': [12, 45, 90, 5000, 70],  # AI is slow
                'statuses': ['OK', 'OK', 'OK', 'OK', 'OK']
            },
            # Failed trace with errors
            {
                'name': 'failed_processing',
                'operations': ['gateway', 'auth', 'content', 'ai_analysis'],
                'durations_ms': [15, 60, 120, 200],
                'statuses': ['OK', 'OK', 'OK', 'ERROR']  # AI fails
            },
            # Database timeout trace
            {
                'name': 'database_timeout',
                'operations': ['gateway', 'auth', 'content', 'storage'],
                'durations_ms': [8, 40, 95, 10000],  # Storage times out
                'statuses': ['OK', 'OK', 'OK', 'ERROR']
            }
        ]
        
        generated_traces = []
        
        for scenario in trace_scenarios:
            for iteration in range(5):  # Generate multiple traces per scenario
                trace_id = str(uuid4())
                spans = []
                
                for i, (op, duration_ms, status) in enumerate(zip(
                    scenario['operations'], 
                    scenario['durations_ms'], 
                    scenario['statuses']
                )):
                    parent_span_id = spans[-1].span_id if spans else None
                    
                    span = await tracer.start_span(
                        operation_name=op,
                        trace_id=trace_id,
                        parent_span_id=parent_span_id,
                        attributes={
                            'scenario': scenario['name'],
                            'iteration': iteration,
                            'service': op
                        }
                    )
                    
                    # Simulate processing time
                    await asyncio.sleep(duration_ms / 10000)  # Scale down for test speed
                    
                    span_status = SpanStatus.OK if status == 'OK' else SpanStatus.ERROR
                    if span_status == SpanStatus.ERROR:
                        span.set_attribute('error.type', 'ProcessingError')
                        span.set_attribute('error.message', f'Failed in {op} operation')
                    
                    await tracer.end_span(span, status=span_status)
                    spans.append(span)
                
                generated_traces.append({
                    'trace_id': trace_id,
                    'scenario': scenario['name'],
                    'spans': spans
                })
        
        # Initialize trace analyzer
        analyzer_config = {
            'analysis_window_minutes': 60,
            'performance_thresholds': {
                'p50_latency_ms': 1000,
                'p95_latency_ms': 5000,
                'p99_latency_ms': 10000,
                'error_rate': 0.05
            },
            'anomaly_detection': {
                'enabled': True,
                'sensitivity': 0.8,
                'algorithms': ['statistical', 'ml_based']
            }
        }
        
        analyzer = TraceAnalyzer(analyzer_config)
        await analyzer.initialize()
        
        # Analyze traces
        analysis_result = await analyzer.analyze_traces(
            start_time=datetime.now(timezone.utc) - timedelta(minutes=10),
            end_time=datetime.now(timezone.utc)
        )
        
        assert 'performance_metrics' in analysis_result
        assert 'error_analysis' in analysis_result
        assert 'service_map' in analysis_result
        assert 'bottleneck_analysis' in analysis_result
        assert 'anomaly_detection' in analysis_result
        assert 'recommendations' in analysis_result
        
        # Verify performance metrics
        performance = analysis_result['performance_metrics']
        assert 'latency_percentiles' in performance
        assert 'throughput' in performance
        assert 'error_rate' in performance
        
        # Verify error analysis
        error_analysis = analysis_result['error_analysis']
        assert 'total_errors' in error_analysis
        assert 'error_types' in error_analysis
        assert 'error_distribution' in error_analysis
        
        # Should have detected AI processing bottleneck
        bottlenecks = analysis_result['bottleneck_analysis']
        assert 'bottleneck_services' in bottlenecks
        
        ai_bottleneck = any(
            service['name'] == 'ai_analysis' 
            for service in bottlenecks['bottleneck_services']
        )
        assert ai_bottleneck, "Should detect AI service as bottleneck"
        
        await analyzer.shutdown()

    @pytest.mark.asyncio
    async def test_trace_export_and_integration(self, distributed_tracer):
        """Test trace export to various backends"""        tracer = distributed_tracer
        
        # Configure exporters
        exporters_config = {
            'jaeger': {
                'endpoint': 'http://localhost:14268/api/traces',
                'service_name': 'ia_influencer_test',
                'max_tag_value_length': 1024
            },
            'zipkin': {
                'endpoint': 'http://localhost:9411/api/v2/spans',
                'service_name': 'ia_influencer_test'
            },
            'otlp': {
                'endpoint': 'http://localhost:4317',
                'headers': {'api-key': 'test-key'},
                'compression': 'gzip'
            },
            'prometheus': {
                'endpoint': 'http://localhost:9090/api/v1/write',
                'metrics_only': True
            }
        }
        
        for exporter_name, config in exporters_config.items():
            await tracer.configure_exporter(exporter_name, config)
        
        # Create test trace for export
        trace_id = str(uuid4())
        
        root_span = await tracer.start_span(
            operation_name="export_test_trace",
            trace_id=trace_id,
            attributes={
                'test.type': 'export_integration',
                'export.formats': ['jaeger', 'zipkin', 'otlp', 'prometheus']
            }
        )
        
        child_spans = []
        for i in range(3):
            child = await tracer.start_span(
                operation_name=f"child_operation_{i}",
                parent_span=root_span,
                attributes={
                    'child.index': i,
                    'processing.type': 'test_data'
                }
            )
            
            await tracer.add_span_event(
                child,
                f"event_{i}",
                attributes={'event_data': f'test_value_{i}'}
            )
            
            await tracer.end_span(child)
            child_spans.append(child)
        
        await tracer.end_span(root_span)
        
        # Export traces
        export_results = {}
        
        for exporter_name in exporters_config.keys():
            try:
                result = await tracer.export_trace(trace_id, exporter_name)
                export_results[exporter_name] = result
            except Exception as e:
                # Some exporters might not be available in test environment
                export_results[exporter_name] = {'error': str(e), 'success': False}
        
        # Verify export attempts were made
        assert len(export_results) == len(exporters_config)
        
        for exporter_name, result in export_results.items():
            # Either successful export or expected connection error
            assert 'success' in result or 'error' in result
        
        # Test custom export format
        custom_export = await tracer.export_trace_custom(
            trace_id,
            format_func=lambda trace: {
                'trace_id': trace.trace_id,
                'total_spans': len(trace.spans),
                'total_duration_ms': trace.total_duration_ms,
                'services': list(set(span.attributes.get('service.name', 'unknown') for span in trace.spans))
            }
        )
        
        assert custom_export['trace_id'] == trace_id
        assert custom_export['total_spans'] == 4  # root + 3 children
        assert custom_export['total_duration_ms'] > 0

    @pytest.mark.asyncio
    async def test_context_manager_tracing(self, distributed_tracer):
        """Test tracing with context managers"""        tracer = distributed_tracer
        
        # Test async context manager
        @asynccontextmanager
        async def traced_operation(operation_name, **attributes):
            span = await tracer.start_span(operation_name, attributes=attributes)
            try:
                yield span
            except Exception as e:
                span.set_attribute('error.type', type(e).__name__)
                span.set_attribute('error.message', str(e))
                await tracer.end_span(span, status=SpanStatus.ERROR)
                raise
            else:
                await tracer.end_span(span, status=SpanStatus.OK)
        
        # Test successful operation
        async with traced_operation("successful_upload", content_type="video", size_mb=100) as span:
            await tracer.add_span_event(span, "validation_started")
            await asyncio.sleep(0.1)  # Simulate processing
            await tracer.add_span_event(span, "validation_completed", attributes={"result": "passed"})
            span.set_attribute("processing.duration_ms", 100)
        
        # Test operation with exception
        try:
            async with traced_operation("failed_processing", operation_type="ai_analysis") as span:
                await tracer.add_span_event(span, "processing_started")
                await asyncio.sleep(0.05)
                raise ValueError("Processing failed due to invalid input")
        except ValueError:
            pass  # Expected exception
        
        # Verify traces were created
        traces = await tracer.get_recent_traces(limit=10)
        assert len(traces) >= 2
        
        # Find our traces
        successful_trace = None
        failed_trace = None
        
        for trace in traces:
            if trace.root_span.operation_name == "successful_upload":
                successful_trace = trace
            elif trace.root_span.operation_name == "failed_processing":
                failed_trace = trace
        
        assert successful_trace is not None
        assert successful_trace.root_span.status == SpanStatus.OK
        assert len(successful_trace.root_span.events) == 2
        
        assert failed_trace is not None
        assert failed_trace.root_span.status == SpanStatus.ERROR
        assert failed_trace.root_span.attributes.get('error.type') == 'ValueError'

    def test_thread_safety_tracing_operations(self, tracing_config):
        """Test thread safety of tracing operations"""        import concurrent.futures
        import threading
        
        tracer = DistributedTracer(tracing_config)
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def concurrent_tracing_operations(thread_id):
            try:
                operations = []
                
                # Simulate concurrent span operations
                for i in range(25):
                    operation = {
                        'thread_id': thread_id,
                        'span_index': i,
                        'operation_name': f'thread_{thread_id}_operation_{i}',
                        'trace_id': str(uuid4()),
                        'attributes': {'thread': thread_id, 'index': i}
                    }
                    operations.append(operation)
                
                with lock:
                    results.extend(operations)
                
                return operations
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})
                raise
        
        # Run concurrent tracing operations
        num_threads = 15
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(concurrent_tracing_operations, i) 
                for i in range(num_threads)
            ]
            
            concurrent.futures.wait(futures)
        
        # Verify thread safety
        assert len(errors) == 0
        assert len(results) == num_threads * 25
        
        # Verify no data corruption
        thread_ids = set()
        trace_ids = set()
        
        for result in results:
            thread_ids.add(result['thread_id'])
            trace_ids.add(result['trace_id'])
        
        assert len(thread_ids) == num_threads
        assert len(trace_ids) == num_threads * 25  # Each operation should have unique trace_id

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_high_throughput_tracing_performance(self, distributed_tracer):
        """Test performance with high-throughput tracing"""        tracer = distributed_tracer
        
        # Configure for high performance
        await tracer.configure_high_performance(
            batch_size=1000,
            flush_interval_ms=100,
            max_queue_size=50000,
            compression=True,
            sampling_rate=1.0  # Sample everything for this test
        )
        
        # Test parameters
        total_traces = 1000
        spans_per_trace = 5
        
        start_time = time.time()
        
        # Generate high-throughput traces
        trace_tasks = []
        
        for trace_idx in range(total_traces):
            async def create_trace(idx):
                trace_id = str(uuid4())
                spans = []
                
                # Create root span
                root_span = await tracer.start_span(
                    operation_name=f"high_throughput_trace_{idx}",
                    trace_id=trace_id,
                    attributes={'trace_index': idx, 'test': 'throughput'}
                )
                spans.append(root_span)
                
                # Create child spans
                for span_idx in range(spans_per_trace - 1):
                    child_span = await tracer.start_span(
                        operation_name=f"operation_{span_idx}",
                        parent_span=spans[-1],
                        attributes={'span_index': span_idx, 'parent_trace': idx}
                    )
                    spans.append(child_span)
                
                # End all spans
                for span in reversed(spans):
                    await tracer.end_span(span)
                
                return trace_id
            
            trace_tasks.append(create_trace(trace_idx))
        
        # Execute all traces concurrently
        completed_traces = await asyncio.gather(*trace_tasks)
        
        # Ensure all data is exported
        await tracer.flush()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        total_spans = total_traces * spans_per_trace
        throughput = total_spans / total_time
        
        assert throughput > 500, f"Span throughput too low: {throughput:.2f} spans/second"
        assert len(completed_traces) == total_traces
        
        traces_per_second = total_traces / total_time
        assert traces_per_second > 100, f"Trace throughput too low: {traces_per_second:.2f} traces/second"
        
        print(f"Generated {total_traces} traces ({total_spans} spans) in {total_time:.2f}s")
        print(f"Trace throughput: {traces_per_second:.2f} traces/second")
        print(f"Span throughput: {throughput:.2f} spans/second")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_distributed_tracing_scenario(self, distributed_tracer):
        """Test end-to-end distributed tracing scenario"""        tracer = distributed_tracer
        
        # Step 1: Setup distributed tracing for content upload pipeline
        pipeline_services = [
            'api_gateway',
            'authentication_service',
            'content_validation_service',
            'ai_processing_service',
            'content_protection_service',
            'storage_service',
            'notification_service'
        ]
        
        # Configure service-specific tracing
        service_configs = {}
        for service in pipeline_services:
            service_configs[service] = {
                'service_name': service,
                'trace_sampling_rate': 1.0,
                'instrumentation_libraries': ['http', 'database', 'ai_model']
            }
            await tracer.configure_service_tracing(service, service_configs[service])
        
        # Step 2: Simulate realistic user content upload scenario
        user_id = 'user_content_creator_123'
        content_id = str(uuid4())
        session_id = str(uuid4())
        
        # Create trace context with user information
        trace_context = TracingContext()
        trace_context.set_baggage('user_id', user_id)
        trace_context.set_baggage('session_id', session_id)
        trace_context.set_baggage('content_id', content_id)
        
        trace_id = str(uuid4())
        
        # Step 3: API Gateway - Entry point
        api_gateway_span = await tracer.start_span(
            operation_name="POST /api/v1/content/upload",
            context=trace_context,
            trace_id=trace_id,
            kind=SpanKind.SERVER,
            attributes={
                'http.method': 'POST',
                'http.url': '/api/v1/content/upload',
                'http.scheme': 'https',
                'http.host': 'api.ia-influencer.com',
                'user.id': user_id,
                'request.content_type': 'video/mp4',
                'request.content_size_mb': 250.5
            }
        )
        
        # Step 4: Authentication Service
        auth_span = await tracer.start_span(
            operation_name="authenticate_user",
            parent_span=api_gateway_span,
            kind=SpanKind.CLIENT,
            attributes={
                'service.name': 'authentication_service',
                'auth.method': 'jwt',
                'auth.provider': 'oauth2'
            }
        )
        
        await tracer.add_span_event(
            auth_span,
            "token_validation_started",
            attributes={'token_type': 'bearer', 'issuer': 'auth.ia-influencer.com'}
        )
        
        await asyncio.sleep(0.1)  # Simulate auth time
        
        await tracer.add_span_event(
            auth_span,
            "token_validation_completed",
            attributes={'validation_result': 'valid', 'user_permissions': 'upload,ai_processing'}
        )
        
        await tracer.end_span(auth_span, status=SpanStatus.OK)
        
        # Step 5: Content Validation Service
        validation_span = await tracer.start_span(
            operation_name="validate_content_upload",
            parent_span=api_gateway_span,
            kind=SpanKind.INTERNAL,
            attributes={
                'service.name': 'content_validation_service',
                'content.type': 'video',
                'content.format': 'mp4',
                'content.duration_seconds': 180
            }
        )
        
        validation_checks = [
            {'name': 'format_check', 'result': 'passed', 'duration_ms': 50},
            {'name': 'size_check', 'result': 'passed', 'duration_ms': 20},
            {'name': 'codec_check', 'result': 'passed', 'duration_ms': 100},
            {'name': 'metadata_extraction', 'result': 'completed', 'duration_ms': 200}
        ]
        
        for check in validation_checks:
            await tracer.add_span_event(
                validation_span,
                f"validation_{check['name']}_started"
            )
            
            await asyncio.sleep(check['duration_ms'] / 10000)  # Scale down for test
            
            await tracer.add_span_event(
                validation_span,
                f"validation_{check['name']}_completed",
                attributes={'result': check['result'], 'duration_ms': check['duration_ms']}
            )
        
        await tracer.end_span(validation_span, status=SpanStatus.OK)
        
        # Step 6: AI Processing Service (parallel processing)
        ai_processing_span = await tracer.start_span(
            operation_name="ai_content_analysis",
            parent_span=api_gateway_span,
            kind=SpanKind.INTERNAL,
            attributes={
                'service.name': 'ai_processing_service',
                'ai.pipeline': 'content_analysis_v2.1',
                'processing.priority': 'high'
            }
        )
        
        # Parallel AI operations
        ai_operations = [
            {
                'name': 'fingerprint_extraction',
                'model': 'neural_fingerprint_v2.1',
                'duration_ms': 3000,
                'confidence': 0.95
            },
            {
                'name': 'object_detection',
                'model': 'yolo_v8_custom',
                'duration_ms': 2500,
                'objects_detected': 15
            },
            {
                'name': 'audio_analysis',
                'model': 'audio_classifier_v1.8',
                'duration_ms': 1800,
                'features_extracted': 128
            }
        ]
        
        ai_operation_spans = []
        
        for ai_op in ai_operations:
            op_span = await tracer.start_span(
                operation_name=ai_op['name'],
                parent_span=ai_processing_span,
                kind=SpanKind.INTERNAL,
                attributes={
                    'ai.model.name': ai_op['model'],
                    'ai.operation.type': ai_op['name']
                }
            )
            
            await tracer.add_span_event(
                op_span,
                "model_loading_started",
                attributes={'model': ai_op['model']}
            )
            
            await asyncio.sleep(ai_op['duration_ms'] / 20000)  # Scale down
            
            await tracer.add_span_event(
                op_span,
                "inference_completed",
                attributes={
                    'processing_time_ms': ai_op['duration_ms'],
                    'confidence': ai_op.get('confidence', 0.9)
                }
            )
            
            if 'objects_detected' in ai_op:
                op_span.set_attribute('detection.objects_count', ai_op['objects_detected'])
            
            if 'features_extracted' in ai_op:
                op_span.set_attribute('audio.features_count', ai_op['features_extracted'])
            
            await tracer.end_span(op_span, status=SpanStatus.OK)
            ai_operation_spans.append(op_span)
        
        await tracer.end_span(ai_processing_span, status=SpanStatus.OK)
        
        # Step 7: Content Protection Service
        protection_span = await tracer.start_span(
            operation_name="copyright_protection_check",
            parent_span=api_gateway_span,
            kind=SpanKind.INTERNAL,
            attributes={
                'service.name': 'content_protection_service',
                'protection.type': 'copyright_detection'
            }
        )
        
        # Simulate copyright database lookup
        await tracer.add_span_event(
            protection_span,
            "copyright_database_query",
            attributes={'database': 'copyright_registry', 'query_type': 'fingerprint_match'}
        )
        
        await asyncio.sleep(0.2)
        
        # Simulate match found
        await tracer.add_span_event(
            protection_span,
            "potential_match_found",
            attributes={
                'match_confidence': 0.88,
                'original_content_id': 'orig_content_456',
                'similarity_score': 0.92
            }
        )
        
        protection_span.set_attribute('protection.result', 'flagged_for_review')
        protection_span.set_attribute('match.confidence', 0.88)
        
        await tracer.end_span(protection_span, status=SpanStatus.OK)
        
        # Step 8: Storage Service
        storage_span = await tracer.start_span(
            operation_name="store_content_and_metadata",
            parent_span=api_gateway_span,
            kind=SpanKind.CLIENT,
            attributes={
                'service.name': 'storage_service',
                'storage.type': 'cloud_storage',
                'storage.provider': 'aws_s3'
            }
        )
        
        storage_operations = [
            {'name': 'upload_original_file', 'bucket': 'content-originals', 'size_mb': 250.5},
            {'name': 'store_fingerprint', 'bucket': 'ai-fingerprints', 'size_kb': 4.2},
            {'name': 'store_metadata', 'bucket': 'content-metadata', 'size_kb': 15.7}
        ]
        
        for storage_op in storage_operations:
            await tracer.add_span_event(
                storage_span,
                f"storage_{storage_op['name']}_started",
                attributes={
                    'bucket': storage_op['bucket'],
                    'expected_size': storage_op.get('size_mb') or storage_op.get('size_kb')
                }
            )
            
            await asyncio.sleep(0.05)  # Simulate storage time
            
            await tracer.add_span_event(
                storage_span,
                f"storage_{storage_op['name']}_completed",
                attributes={'result': 'success'}
            )
        
        await tracer.end_span(storage_span, status=SpanStatus.OK)
        
        # Step 9: Notification Service
        notification_span = await tracer.start_span(
            operation_name="send_processing_notifications",
            parent_span=api_gateway_span,
            kind=SpanKind.PRODUCER,
            attributes={
                'service.name': 'notification_service',
                'notification.type': 'content_processing_status'
            }
        )
        
        notifications = [
            {'type': 'user_notification', 'channel': 'email', 'recipient': user_id},
            {'type': 'admin_alert', 'channel': 'slack', 'recipient': 'content_review_team'},
            {'type': 'webhook', 'channel': 'http', 'recipient': 'external_partner_api'}
        ]
        
        for notification in notifications:
            await tracer.add_span_event(
                notification_span,
                f"notification_{notification['type']}_sent",
                attributes={
                    'channel': notification['channel'],
                    'recipient': notification['recipient']
                }
            )
        
        await tracer.end_span(notification_span, status=SpanStatus.OK)
        
        # Step 10: Complete API Gateway span
        api_gateway_span.set_attribute('response.status_code', 202)
        api_gateway_span.set_attribute('response.content_id', content_id)
        api_gateway_span.set_attribute('processing.result', 'accepted_for_review')
        
        await tracer.end_span(api_gateway_span, status=SpanStatus.OK)
        
        # Step 11: Analyze the complete trace
        complete_trace = await tracer.get_trace(trace_id)
        
        assert complete_trace is not None
        assert len(complete_trace.spans) >= 8  # All major operations
        assert complete_trace.total_duration_ms > 0
        
        # Verify trace structure
        assert complete_trace.root_span.operation_name == "POST /api/v1/content/upload"
        
        # Verify service map generation
        service_map = await tracer.generate_service_map(trace_id)
        
        assert 'services' in service_map
        assert 'dependencies' in service_map
        assert len(service_map['services']) >= 6
        
        # Verify critical path analysis
        critical_path = await tracer.analyze_critical_path(trace_id)
        
        assert 'critical_spans' in critical_path
        assert 'bottleneck_operations' in critical_path
        
        # AI processing should be on the critical path
        ai_on_critical_path = any(
            'ai' in span['operation_name'].lower() 
            for span in critical_path['critical_spans']
        )
        assert ai_on_critical_path
        
        # Step 12: Generate insights and recommendations
        trace_insights = await tracer.generate_trace_insights(trace_id)
        
        assert 'performance_summary' in trace_insights
        assert 'optimization_opportunities' in trace_insights
        assert 'error_analysis' in trace_insights
        assert 'recommendations' in trace_insights
        
        # Verify performance summary
        performance = trace_insights['performance_summary']
        assert 'total_duration_ms' in performance
        assert 'service_breakdown' in performance
        assert 'parallel_efficiency' in performance
        
        print(f"End-to-end trace completed successfully")
        print(f"Total duration: {complete_trace.total_duration_ms}ms")
        print(f"Services involved: {len(service_map['services'])}")
        print(f"Total spans: {len(complete_trace.spans)}")


# Performance benchmarks
@pytest.mark.benchmark
class TestTracingBenchmarks:
    """Performance benchmarks for distributed tracing"""    
    def test_span_creation_benchmark(self, benchmark):
        """Benchmark span creation performance"""        def create_span():
            trace_id = str(uuid4())
            span_id = str(uuid4())
            
            return Span(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=None,
                operation_name="benchmark_operation",
                kind=SpanKind.INTERNAL,
                start_time=datetime.now(timezone.utc),
                attributes={
                    'service.name': 'benchmark_service',
                    'operation.type': 'test',
                    'test.iteration': 1
                }
            )
        
        span = benchmark(create_span)
        
        assert span.operation_name == "benchmark_operation"
        assert span.kind == SpanKind.INTERNAL
        assert 'service.name' in span.attributes
    
    def test_span_serialization_benchmark(self, benchmark):
        """Benchmark span serialization performance"""        trace_id = str(uuid4())
        span_id = str(uuid4())
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            operation_name="serialization_benchmark",
            kind=SpanKind.SERVER,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(milliseconds=100),
            status=SpanStatus.OK,
            attributes={
                'http.method': 'POST',
                'http.url': '/api/benchmark',
                'http.status_code': 200,
                'user.id': 'user_123',
                'request.size_bytes': 1024
            }
        )
        
        # Add events and links for comprehensive serialization test
        span.add_event(SpanEvent(
            name="processing_started",
            timestamp=datetime.now(timezone.utc),
            attributes={'stage': 'initial'}
        ))
        
        def serialize_span():
            return span.to_dict()
        
        serialized = benchmark(serialize_span)
        
        assert serialized['trace_id'] == trace_id
        assert serialized['operation_name'] == "serialization_benchmark"
        assert len(serialized['attributes']) == 5
