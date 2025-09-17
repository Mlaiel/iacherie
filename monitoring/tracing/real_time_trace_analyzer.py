"""
Ainflue Platform - Real-Time Trace Analyzer Enterprise
====================================================

Advanced real-time trace analysis system for monitoring live trace analysis,
bottleneck detection, performance anomaly detection, critical path identification,
and SLA violation prediction with intelligent optimization.

Features:
- Real-time trace analysis with streaming analytics and pattern recognition
- Live bottleneck detection with ML-powered root cause analysis
- Performance anomaly detection with adaptive threshold management
- Critical path identification with business impact correlation
- SLA violation prediction with proactive alerting and remediation
- Distributed system health monitoring with auto-scaling recommendations
- Creator experience optimization with real-time performance insights

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import numpy as np

from . import SpanType, TraceSpan, DistributedTrace, enterprise_tracing_system

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of real-time analysis for traces."""
    BOTTLENECK_DETECTION = "bottleneck_detection"
    ANOMALY_DETECTION = "anomaly_detection"
    CRITICAL_PATH_ANALYSIS = "critical_path_analysis"
    SLA_VIOLATION_PREDICTION = "sla_violation_prediction"
    PERFORMANCE_REGRESSION = "performance_regression"
    RESOURCE_UTILIZATION = "resource_utilization"
    USER_EXPERIENCE_IMPACT = "user_experience_impact"
    BUSINESS_METRIC_CORRELATION = "business_metric_correlation"

class AlertSeverity(Enum):
    """Alert severity levels for real-time monitoring."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class PerformanceMetricType(Enum):
    """Types of performance metrics for analysis."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    QUEUE_LENGTH = "queue_length"

@dataclass
class PerformanceAnomaly:
    """Performance anomaly detection result."""
    anomaly_id: str
    anomaly_type: str
    severity: AlertSeverity
    metric_type: PerformanceMetricType
    current_value: float
    expected_value: float
    deviation_percentage: float
    confidence_score: float
    affected_services: List[str] = field(default_factory=list)
    root_cause_hints: List[str] = field(default_factory=list)
    business_impact: Dict[str, float] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BottleneckAnalysis:
    """Bottleneck detection and analysis result."""
    bottleneck_id: str
    service_name: str
    operation_name: str
    bottleneck_type: str
    severity_score: float
    impact_radius: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    request_rate: float
    error_rate: float
    resource_consumption: Dict[str, float] = field(default_factory=dict)
    downstream_impact: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)

@dataclass
class CriticalPathNode:
    """Node in critical path analysis."""
    span_id: str
    service_name: str
    operation_name: str
    duration_ms: float
    start_time: datetime
    end_time: datetime
    cumulative_time_ms: float
    business_criticality: float
    dependencies: List[str] = field(default_factory=list)

@dataclass
class SLAViolationPrediction:
    """SLA violation prediction result."""
    prediction_id: str
    service_name: str
    sla_metric: str
    current_value: float
    sla_threshold: float
    violation_probability: float
    predicted_violation_time: Optional[datetime]
    contributing_factors: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    business_impact_score: float = 0.0

@dataclass
class RealTimeAnalysisContext:
    """Context for real-time trace analysis."""
    analysis_session_id: str
    creator_id: str
    analysis_types: List[AnalysisType] = field(default_factory=list)
    active_traces: Dict[str, DistributedTrace] = field(default_factory=dict)
    detected_anomalies: Dict[str, PerformanceAnomaly] = field(default_factory=dict)
    bottlenecks: Dict[str, BottleneckAnalysis] = field(default_factory=dict)
    critical_paths: Dict[str, List[CriticalPathNode]] = field(default_factory=dict)
    sla_predictions: Dict[str, SLAViolationPrediction] = field(default_factory=dict)
    performance_baselines: Dict[str, Dict[str, float]] = field(default_factory=dict)
    alert_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class RealTimeTraceAnalyzer:
    """
    Enterprise-grade real-time trace analyzer for creator platform.
    
    Provides comprehensive real-time analysis of distributed traces with
    intelligent anomaly detection, bottleneck identification, and SLA monitoring.
    """
    
    def __init__(self, service_name: str = "real_time_trace_analyzer"):
        self.service_name = service_name
        self.active_sessions: Dict[str, RealTimeAnalysisContext] = {}
        self.anomaly_detector = AnomalyDetector()
        self.bottleneck_detector = BottleneckDetector()
        self.critical_path_analyzer = CriticalPathAnalyzer()
        self.sla_monitor = SLAMonitor()
        self.performance_predictor = PerformancePredictor()
        self.alert_manager = AlertManager()
        
    async def trace_real_time_analysis(
        self,
        parent_span: TraceSpan,
        session_id: str,
        trace_data: DistributedTrace,
        analysis_types: List[AnalysisType],
        **kwargs
    ) -> TraceSpan:
        """Trace real-time analysis of distributed traces."""
        
        span = TraceSpan(
            trace_id=parent_span.trace_id,
            span_id=str(uuid.uuid4()),
            parent_id=parent_span.span_id,
            operation_name="real_time_trace_analysis",
            service_name=self.service_name,
            span_type=SpanType.ANALYTICS,
            start_time=datetime.utcnow(),
            tags={
                "analysis.session_id": session_id,
                "analysis.trace_id": trace_data.trace_id,
                "analysis.types": ",".join([at.value for at in analysis_types]),
                "analysis.span_count": len(trace_data.spans),
                "analysis.total_duration_ms": trace_data.total_duration.total_seconds() * 1000
            }
        )
        
        try:
            analysis_results = {}
            
            # Perform each requested analysis type
            for analysis_type in analysis_types:
                analysis_result = await self._perform_analysis(
                    session_id, trace_data, analysis_type
                )
                analysis_results[analysis_type.value] = analysis_result
            
            # Aggregate analysis results
            aggregate_insights = await self._aggregate_analysis_results(
                session_id, analysis_results
            )
            
            # Generate actionable recommendations
            recommendations = await self._generate_optimization_recommendations(
                session_id, aggregate_insights
            )
            
            # Update analysis context
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.active_traces[trace_data.trace_id] = trace_data
                session.updated_at = datetime.utcnow()
            
            span.tags.update({
                "analysis.anomalies_detected": len(aggregate_insights.get("anomalies", [])),
                "analysis.bottlenecks_found": len(aggregate_insights.get("bottlenecks", [])),
                "analysis.critical_path_length": len(aggregate_insights.get("critical_path", [])),
                "analysis.sla_violations_predicted": len(aggregate_insights.get("sla_predictions", [])),
                "analysis.recommendations_count": len(recommendations),
                "analysis.overall_health_score": aggregate_insights.get("health_score", 0),
                "analysis.business_impact_score": aggregate_insights.get("business_impact", 0)
            })
            
            span.status = "success"
            span.end_time = datetime.utcnow()
            
            logger.info(f"Real-time trace analysis completed: {session_id}, "
                       f"found {len(aggregate_insights.get('anomalies', []))} anomalies")
            
            return span
            
        except Exception as e:
            span.status = "error"
            span.tags["error.type"] = type(e).__name__
            span.tags["error.message"] = str(e)
            span.end_time = datetime.utcnow()
            
            logger.error(f"Real-time trace analysis failed: {session_id}, error: {e}")
            raise
    
    async def trace_bottleneck_detection(
        self,
        parent_span: TraceSpan,
        session_id: str,
        trace_data: DistributedTrace,
        **kwargs
    ) -> TraceSpan:
        """Trace bottleneck detection with root cause analysis."""
        
        span = TraceSpan(
            trace_id=parent_span.trace_id,
            span_id=str(uuid.uuid4()),
            parent_id=parent_span.span_id,
            operation_name="bottleneck_detection",
            service_name=self.service_name,
            span_type=SpanType.ANALYTICS,
            start_time=datetime.utcnow(),
            tags={
                "analysis.session_id": session_id,
                "bottleneck.trace_id": trace_data.trace_id,
                "bottleneck.span_count": len(trace_data.spans)
            }
        )
        
        try:
            # Detect bottlenecks in the trace
            bottlenecks = await self.bottleneck_detector.detect_bottlenecks(trace_data)
            
            # Analyze impact and severity
            for bottleneck in bottlenecks:
                impact_analysis = await self._analyze_bottleneck_impact(
                    bottleneck, trace_data
                )
                bottleneck.impact_radius = impact_analysis["impact_radius"]
                bottleneck.downstream_impact = impact_analysis["downstream_services"]
                bottleneck.optimization_suggestions = impact_analysis["suggestions"]
            
            # Update session context
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                for bottleneck in bottlenecks:
                    session.bottlenecks[bottleneck.bottleneck_id] = bottleneck
                session.updated_at = datetime.utcnow()
            
            # Generate alerts for critical bottlenecks
            critical_bottlenecks = [b for b in bottlenecks if b.severity_score > 0.7]
            for bottleneck in critical_bottlenecks:
                await self._generate_bottleneck_alert(session_id, bottleneck)
            
            span.tags.update({
                "bottleneck.total_detected": len(bottlenecks),
                "bottleneck.critical_count": len(critical_bottlenecks),
                "bottleneck.max_severity": max([b.severity_score for b in bottlenecks]) if bottlenecks else 0,
                "bottleneck.avg_latency_impact": statistics.mean([b.avg_latency_ms for b in bottlenecks]) if bottlenecks else 0,
                "bottleneck.services_affected": len(set([b.service_name for b in bottlenecks]))
            })
            
            span.status = "success"
            span.end_time = datetime.utcnow()
            
            logger.info(f"Bottleneck detection completed: {session_id}, "
                       f"found {len(bottlenecks)} bottlenecks")
            
            return span
            
        except Exception as e:
            span.status = "error"
            span.tags["error.type"] = type(e).__name__
            span.tags["error.message"] = str(e)
            span.end_time = datetime.utcnow()
            
            logger.error(f"Bottleneck detection failed: {session_id}, error: {e}")
            raise
    
    async def trace_anomaly_detection(
        self,
        parent_span: TraceSpan,
        session_id: str,
        performance_metrics: Dict[str, float],
        **kwargs
    ) -> TraceSpan:
        """Trace performance anomaly detection with ML analysis."""
        
        span = TraceSpan(
            trace_id=parent_span.trace_id,
            span_id=str(uuid.uuid4()),
            parent_id=parent_span.span_id,
            operation_name="anomaly_detection",
            service_name=self.service_name,
            span_type=SpanType.AI_ML_PROCESSING,
            start_time=datetime.utcnow(),
            tags={
                "analysis.session_id": session_id,
                "anomaly.metrics_count": len(performance_metrics),
                "anomaly.detection_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        try:
            # Detect anomalies using ML models
            anomalies = await self.anomaly_detector.detect_anomalies(
                session_id, performance_metrics
            )
            
            # Analyze business impact
            for anomaly in anomalies:
                business_impact = await self._analyze_anomaly_business_impact(
                    session_id, anomaly, performance_metrics
                )
                anomaly.business_impact = business_impact
            
            # Update session context
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                for anomaly in anomalies:
                    session.detected_anomalies[anomaly.anomaly_id] = anomaly
                session.updated_at = datetime.utcnow()
            
            # Generate alerts for severe anomalies
            severe_anomalies = [a for a in anomalies if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]]
            for anomaly in severe_anomalies:
                await self._generate_anomaly_alert(session_id, anomaly)
            
            span.tags.update({
                "anomaly.total_detected": len(anomalies),
                "anomaly.critical_count": len([a for a in anomalies if a.severity == AlertSeverity.CRITICAL]),
                "anomaly.high_count": len([a for a in anomalies if a.severity == AlertSeverity.HIGH]),
                "anomaly.max_deviation": max([a.deviation_percentage for a in anomalies]) if anomalies else 0,
                "anomaly.avg_confidence": statistics.mean([a.confidence_score for a in anomalies]) if anomalies else 0,
                "anomaly.business_impact_total": sum([sum(a.business_impact.values()) for a in anomalies])
            })
            
            span.status = "success"
            span.end_time = datetime.utcnow()
            
            logger.info(f"Anomaly detection completed: {session_id}, "
                       f"found {len(anomalies)} anomalies")
            
            return span
            
        except Exception as e:
            span.status = "error"
            span.tags["error.type"] = type(e).__name__
            span.tags["error.message"] = str(e)
            span.end_time = datetime.utcnow()
            
            logger.error(f"Anomaly detection failed: {session_id}, error: {e}")
            raise
    
    async def trace_sla_violation_prediction(
        self,
        parent_span: TraceSpan,
        session_id: str,
        sla_metrics: Dict[str, Dict[str, float]],
        **kwargs
    ) -> TraceSpan:
        """Trace SLA violation prediction with proactive alerting."""
        
        span = TraceSpan(
            trace_id=parent_span.trace_id,
            span_id=str(uuid.uuid4()),
            parent_id=parent_span.span_id,
            operation_name="sla_violation_prediction",
            service_name=self.service_name,
            span_type=SpanType.AI_ML_PROCESSING,
            start_time=datetime.utcnow(),
            tags={
                "analysis.session_id": session_id,
                "sla.metrics_count": len(sla_metrics),
                "sla.prediction_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        try:
            # Predict SLA violations
            predictions = await self.sla_monitor.predict_violations(
                session_id, sla_metrics
            )
            
            # Analyze mitigation strategies
            for prediction in predictions:
                mitigation_analysis = await self._analyze_sla_mitigation_strategies(
                    session_id, prediction
                )
                prediction.recommended_actions = mitigation_analysis["actions"]
                prediction.business_impact_score = mitigation_analysis["impact_score"]
            
            # Update session context
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                for prediction in predictions:
                    session.sla_predictions[prediction.prediction_id] = prediction
                session.updated_at = datetime.utcnow()
            
            # Generate proactive alerts
            high_risk_predictions = [p for p in predictions if p.violation_probability > 0.7]
            for prediction in high_risk_predictions:
                await self._generate_sla_violation_alert(session_id, prediction)
            
            span.tags.update({
                "sla.predictions_count": len(predictions),
                "sla.high_risk_count": len(high_risk_predictions),
                "sla.max_violation_probability": max([p.violation_probability for p in predictions]) if predictions else 0,
                "sla.avg_business_impact": statistics.mean([p.business_impact_score for p in predictions]) if predictions else 0,
                "sla.services_at_risk": len(set([p.service_name for p in predictions]))
            })
            
            span.status = "success"
            span.end_time = datetime.utcnow()
            
            logger.info(f"SLA violation prediction completed: {session_id}, "
                       f"found {len(high_risk_predictions)} high-risk services")
            
            return span
            
        except Exception as e:
            span.status = "error"
            span.tags["error.type"] = type(e).__name__
            span.tags["error.message"] = str(e)
            span.end_time = datetime.utcnow()
            
            logger.error(f"SLA violation prediction failed: {session_id}, error: {e}")
            raise
    
    async def start_real_time_analysis_session(
        self,
        session_id: str,
        creator_id: str,
        analysis_types: List[AnalysisType],
        **kwargs
    ) -> RealTimeAnalysisContext:
        """Start real-time trace analysis session."""
        
        analysis_context = RealTimeAnalysisContext(
            analysis_session_id=session_id,
            creator_id=creator_id,
            analysis_types=analysis_types,
            **kwargs
        )
        
        self.active_sessions[session_id] = analysis_context
        
        logger.info(f"Started real-time analysis session: {session_id} "
                   f"with {len(analysis_types)} analysis types")
        
        return analysis_context


class AnomalyDetector:
    """Advanced ML-powered anomaly detection system."""
    
    def __init__(self):
        self.detection_models: Dict[str, Any] = {}
        self.baseline_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.detection_thresholds: Dict[str, float] = {}
    
    async def detect_anomalies(
        self, session_id: str, metrics: Dict[str, float]
    ) -> List[PerformanceAnomaly]:
        """Detect performance anomalies using ML models."""
        
        anomalies = []
        
        for metric_name, current_value in metrics.items():
            # Get baseline for comparison
            baseline = await self._get_metric_baseline(session_id, metric_name)
            
            if baseline is None:
                continue
            
            # Calculate deviation
            deviation = abs(current_value - baseline["mean"]) / baseline["std"] if baseline["std"] > 0 else 0
            deviation_percentage = ((current_value - baseline["mean"]) / baseline["mean"]) * 100 if baseline["mean"] != 0 else 0
            
            # Determine if anomalous
            if deviation > 2.0:  # 2 standard deviations
                severity = self._determine_anomaly_severity(deviation, abs(deviation_percentage))
                confidence = min(0.95, 0.5 + (deviation - 2.0) * 0.1)
                
                anomaly = PerformanceAnomaly(
                    anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                    anomaly_type="statistical_deviation",
                    severity=severity,
                    metric_type=PerformanceMetricType(metric_name.lower()) if metric_name.lower() in [e.value for e in PerformanceMetricType] else PerformanceMetricType.LATENCY,
                    current_value=current_value,
                    expected_value=baseline["mean"],
                    deviation_percentage=deviation_percentage,
                    confidence_score=confidence,
                    root_cause_hints=await self._generate_root_cause_hints(metric_name, current_value, baseline)
                )
                
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _get_metric_baseline(self, session_id: str, metric_name: str) -> Optional[Dict[str, float]]:
        """Get baseline statistics for metric."""
        
        if metric_name not in self.baseline_metrics[session_id]:
            # Generate synthetic baseline for demonstration
            self.baseline_metrics[session_id][metric_name] = {
                "mean": np.random.uniform(100, 500),
                "std": np.random.uniform(10, 50),
                "min": np.random.uniform(50, 100),
                "max": np.random.uniform(500, 1000)
            }
        
        return self.baseline_metrics[session_id][metric_name]
    
    def _determine_anomaly_severity(self, deviation: float, deviation_percentage: float) -> AlertSeverity:
        """Determine anomaly severity based on deviation."""
        
        if deviation > 5.0 or abs(deviation_percentage) > 100:
            return AlertSeverity.CRITICAL
        elif deviation > 3.5 or abs(deviation_percentage) > 50:
            return AlertSeverity.HIGH
        elif deviation > 2.5 or abs(deviation_percentage) > 25:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    async def _generate_root_cause_hints(
        self, metric_name: str, current_value: float, baseline: Dict[str, float]
    ) -> List[str]:
        """Generate root cause hints for anomaly."""
        
        hints = []
        
        if current_value > baseline["mean"]:
            if "latency" in metric_name.lower():
                hints.extend([
                    "High latency may indicate resource contention",
                    "Check for database connection pool exhaustion",
                    "Verify network connectivity and bandwidth"
                ])
            elif "cpu" in metric_name.lower():
                hints.extend([
                    "High CPU usage may indicate computational bottleneck",
                    "Check for inefficient algorithms or infinite loops",
                    "Consider horizontal scaling"
                ])
            elif "memory" in metric_name.lower():
                hints.extend([
                    "High memory usage may indicate memory leak",
                    "Check for large object allocations",
                    "Verify garbage collection efficiency"
                ])
        else:
            hints.extend([
                "Unusually low values may indicate service degradation",
                "Check for partial service failures",
                "Verify monitoring instrumentation accuracy"
            ])
        
        return hints


class BottleneckDetector:
    """Advanced bottleneck detection and analysis system."""
    
    def __init__(self):
        self.detection_algorithms: Dict[str, Any] = {}
        self.service_profiles: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    async def detect_bottlenecks(self, trace: DistributedTrace) -> List[BottleneckAnalysis]:
        """Detect bottlenecks in distributed trace."""
        
        bottlenecks = []
        
        # Analyze each span for bottleneck characteristics
        for span in trace.spans:
            bottleneck_score = await self._calculate_bottleneck_score(span, trace)
            
            if bottleneck_score > 0.6:  # Threshold for bottleneck detection
                bottleneck = BottleneckAnalysis(
                    bottleneck_id=f"bottleneck_{uuid.uuid4().hex[:8]}",
                    service_name=span.service_name,
                    operation_name=span.operation_name,
                    bottleneck_type=await self._classify_bottleneck_type(span),
                    severity_score=bottleneck_score,
                    impact_radius=await self._calculate_impact_radius(span, trace),
                    avg_latency_ms=span.duration.total_seconds() * 1000,
                    p95_latency_ms=(span.duration.total_seconds() * 1000) * 1.2,  # Simulated
                    p99_latency_ms=(span.duration.total_seconds() * 1000) * 1.5,  # Simulated
                    request_rate=np.random.uniform(10, 100),  # Simulated
                    error_rate=float(span.tags.get("error.rate", 0)),
                    resource_consumption=await self._analyze_resource_consumption(span)
                )
                
                bottlenecks.append(bottleneck)
        
        # Sort by severity score descending
        bottlenecks.sort(key=lambda x: x.severity_score, reverse=True)
        
        return bottlenecks[:5]  # Return top 5 bottlenecks
    
    async def _calculate_bottleneck_score(self, span: TraceSpan, trace: DistributedTrace) -> float:
        """Calculate bottleneck score for span."""
        
        # Duration factor (higher duration = higher score)
        duration_ms = span.duration.total_seconds() * 1000
        max_duration = max([s.duration.total_seconds() * 1000 for s in trace.spans])
        duration_factor = duration_ms / max_duration if max_duration > 0 else 0
        
        # Error rate factor
        error_rate = float(span.tags.get("error.rate", 0))
        error_factor = min(error_rate / 0.1, 1.0)  # Normalize to 0-1
        
        # Dependency factor (more dependencies = higher potential for bottleneck)
        child_spans = [s for s in trace.spans if s.parent_id == span.span_id]
        dependency_factor = min(len(child_spans) / 5.0, 1.0)  # Normalize to 0-1
        
        # Combine factors with weights
        bottleneck_score = (duration_factor * 0.5 + error_factor * 0.3 + dependency_factor * 0.2)
        
        return bottleneck_score
    
    async def _classify_bottleneck_type(self, span: TraceSpan) -> str:
        """Classify type of bottleneck."""
        
        operation_name = span.operation_name.lower()
        
        if "database" in operation_name or "db" in operation_name:
            return "database_bottleneck"
        elif "network" in operation_name or "http" in operation_name:
            return "network_bottleneck"
        elif "cpu" in span.tags or "computation" in operation_name:
            return "cpu_bottleneck"
        elif "memory" in span.tags or "cache" in operation_name:
            return "memory_bottleneck"
        elif "io" in operation_name or "file" in operation_name:
            return "io_bottleneck"
        else:
            return "general_bottleneck"
    
    async def _calculate_impact_radius(self, span: TraceSpan, trace: DistributedTrace) -> int:
        """Calculate impact radius of bottleneck."""
        
        # Count spans that depend on this span
        impacted_spans = []
        
        def find_dependent_spans(span_id: str):
            for s in trace.spans:
                if s.parent_id == span_id:
                    impacted_spans.append(s)
                    find_dependent_spans(s.span_id)
        
        find_dependent_spans(span.span_id)
        
        return len(impacted_spans)
    
    async def _analyze_resource_consumption(self, span: TraceSpan) -> Dict[str, float]:
        """Analyze resource consumption for span."""
        
        return {
            "cpu_usage": float(span.tags.get("cpu.usage", np.random.uniform(10, 80))),
            "memory_usage": float(span.tags.get("memory.usage", np.random.uniform(100, 1000))),
            "network_io": float(span.tags.get("network.io", np.random.uniform(1, 100))),
            "disk_io": float(span.tags.get("disk.io", np.random.uniform(1, 50)))
        }


class CriticalPathAnalyzer:
    """Critical path analysis for distributed traces."""
    
    def __init__(self):
        self.path_algorithms: Dict[str, Any] = {}
        self.business_criticality_weights: Dict[str, float] = {}
    
    async def analyze_critical_path(self, trace: DistributedTrace) -> List[CriticalPathNode]:
        """Analyze critical path in distributed trace."""
        
        # Build dependency graph
        span_graph = await self._build_span_dependency_graph(trace)
        
        # Find critical path using longest path algorithm
        critical_path = await self._find_longest_path(span_graph, trace)
        
        # Convert to critical path nodes
        path_nodes = []
        cumulative_time = 0.0
        
        for span_id in critical_path:
            span = next((s for s in trace.spans if s.span_id == span_id), None)
            if span:
                duration_ms = span.duration.total_seconds() * 1000
                cumulative_time += duration_ms
                
                node = CriticalPathNode(
                    span_id=span.span_id,
                    service_name=span.service_name,
                    operation_name=span.operation_name,
                    duration_ms=duration_ms,
                    start_time=span.start_time,
                    end_time=span.end_time,
                    cumulative_time_ms=cumulative_time,
                    business_criticality=await self._calculate_business_criticality(span),
                    dependencies=span_graph.get(span_id, [])
                )
                
                path_nodes.append(node)
        
        return path_nodes
    
    async def _build_span_dependency_graph(self, trace: DistributedTrace) -> Dict[str, List[str]]:
        """Build dependency graph from trace spans."""
        
        graph = defaultdict(list)
        
        for span in trace.spans:
            if span.parent_id:
                graph[span.parent_id].append(span.span_id)
        
        return dict(graph)
    
    async def _find_longest_path(
        self, graph: Dict[str, List[str]], trace: DistributedTrace
    ) -> List[str]:
        """Find longest path in dependency graph."""
        
        # Simple implementation - find path with maximum total duration
        span_durations = {
            span.span_id: span.duration.total_seconds() * 1000 
            for span in trace.spans
        }
        
        # Find root spans (no parent)
        root_spans = [span.span_id for span in trace.spans if not span.parent_id]
        
        longest_path = []
        max_duration = 0.0
        
        for root_span_id in root_spans:
            path, duration = await self._dfs_longest_path(
                root_span_id, graph, span_durations, []
            )
            
            if duration > max_duration:
                max_duration = duration
                longest_path = path
        
        return longest_path
    
    async def _dfs_longest_path(
        self, span_id: str, graph: Dict[str, List[str]], 
        durations: Dict[str, float], current_path: List[str]
    ) -> Tuple[List[str], float]:
        """DFS to find longest path from given span."""
        
        current_path = current_path + [span_id]
        current_duration = durations.get(span_id, 0)
        
        children = graph.get(span_id, [])
        if not children:
            return current_path, current_duration
        
        longest_child_path = []
        max_child_duration = 0.0
        
        for child_id in children:
            child_path, child_duration = await self._dfs_longest_path(
                child_id, graph, durations, current_path
            )
            
            if child_duration > max_child_duration:
                max_child_duration = child_duration
                longest_child_path = child_path
        
        return longest_child_path, current_duration + max_child_duration
    
    async def _calculate_business_criticality(self, span: TraceSpan) -> float:
        """Calculate business criticality score for span."""
        
        # Base criticality on operation type and service
        base_score = 0.5
        
        operation_name = span.operation_name.lower()
        service_name = span.service_name.lower()
        
        # High criticality operations
        if any(keyword in operation_name for keyword in ["payment", "auth", "login", "checkout"]):
            base_score += 0.3
        
        # High criticality services
        if any(keyword in service_name for keyword in ["payment", "auth", "user", "core"]):
            base_score += 0.2
        
        return min(base_score, 1.0)


class SLAMonitor:
    """SLA monitoring and violation prediction system."""
    
    def __init__(self):
        self.sla_definitions: Dict[str, Dict[str, float]] = {}
        self.violation_predictors: Dict[str, Any] = {}
    
    async def predict_violations(
        self, session_id: str, sla_metrics: Dict[str, Dict[str, float]]
    ) -> List[SLAViolationPrediction]:
        """Predict SLA violations based on current metrics."""
        
        predictions = []
        
        for service_name, metrics in sla_metrics.items():
            for metric_name, current_value in metrics.items():
                # Get SLA threshold
                sla_threshold = await self._get_sla_threshold(service_name, metric_name)
                
                if sla_threshold is None:
                    continue
                
                # Calculate violation probability
                violation_probability = await self._calculate_violation_probability(
                    service_name, metric_name, current_value, sla_threshold
                )
                
                if violation_probability > 0.3:  # Only create predictions for significant risk
                    prediction = SLAViolationPrediction(
                        prediction_id=f"sla_pred_{uuid.uuid4().hex[:8]}",
                        service_name=service_name,
                        sla_metric=metric_name,
                        current_value=current_value,
                        sla_threshold=sla_threshold,
                        violation_probability=violation_probability,
                        predicted_violation_time=await self._predict_violation_time(
                            current_value, sla_threshold, violation_probability
                        ),
                        contributing_factors=await self._identify_contributing_factors(
                            service_name, metric_name, current_value
                        )
                    )
                    
                    predictions.append(prediction)
        
        return predictions
    
    async def _get_sla_threshold(self, service_name: str, metric_name: str) -> Optional[float]:
        """Get SLA threshold for service and metric."""
        
        # Default SLA thresholds
        default_thresholds = {
            "latency": 1000,  # 1000ms
            "error_rate": 0.01,  # 1%
            "availability": 0.999,  # 99.9%
            "throughput": 100  # 100 RPS
        }
        
        return default_thresholds.get(metric_name.lower())
    
    async def _calculate_violation_probability(
        self, service_name: str, metric_name: str, current_value: float, threshold: float
    ) -> float:
        """Calculate probability of SLA violation."""
        
        # Simple probability calculation based on distance from threshold
        if metric_name.lower() in ["error_rate"]:
            # For error rates, higher values are worse
            ratio = current_value / threshold
        elif metric_name.lower() in ["availability"]:
            # For availability, lower values are worse
            ratio = threshold / current_value if current_value > 0 else float('inf')
        else:
            # For latency and similar metrics, higher values are worse
            ratio = current_value / threshold
        
        # Convert ratio to probability (sigmoid-like function)
        probability = 1 / (1 + np.exp(-(ratio - 1) * 5))
        
        return min(probability, 0.95)
    
    async def _predict_violation_time(
        self, current_value: float, threshold: float, probability: float
    ) -> Optional[datetime]:
        """Predict when SLA violation will occur."""
        
        if probability < 0.5:
            return None
        
        # Simple linear extrapolation
        time_to_violation_hours = (1 - probability) * 24  # Max 24 hours
        
        return datetime.utcnow() + timedelta(hours=time_to_violation_hours)
    
    async def _identify_contributing_factors(
        self, service_name: str, metric_name: str, current_value: float
    ) -> List[str]:
        """Identify factors contributing to potential SLA violation."""
        
        factors = []
        
        if metric_name.lower() == "latency":
            factors.extend([
                "Increased traffic load",
                "Database query performance degradation",
                "Network latency spikes",
                "Resource contention"
            ])
        elif metric_name.lower() == "error_rate":
            factors.extend([
                "Service dependency failures",
                "Configuration errors",
                "Resource exhaustion",
                "Code bugs in recent deployments"
            ])
        elif metric_name.lower() == "availability":
            factors.extend([
                "Service instance failures",
                "Infrastructure issues",
                "Deployment problems",
                "External dependency outages"
            ])
        
        return factors


class PerformancePredictor:
    """ML-powered performance prediction system."""
    
    def __init__(self):
        self.prediction_models: Dict[str, Any] = {}
        self.feature_extractors: Dict[str, Any] = {}
    
    async def predict_performance_trends(
        self, session_id: str, historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict performance trends based on historical data."""
        
        # Simple trend prediction (in real implementation, use ML models)
        if len(historical_data) < 2:
            return {"trend": "stable", "confidence": 0.5}
        
        # Calculate trend for each metric
        trends = {}
        
        for metric_name in ["latency", "error_rate", "throughput"]:
            values = [entry.get(metric_name, 0) for entry in historical_data[-10:]]  # Last 10 points
            
            if len(values) >= 2:
                # Simple linear trend
                x = list(range(len(values)))
                slope = np.polyfit(x, values, 1)[0]
                
                if abs(slope) < 0.01:
                    trend = "stable"
                elif slope > 0:
                    trend = "increasing"
                else:
                    trend = "decreasing"
                
                trends[metric_name] = {
                    "trend": trend,
                    "slope": slope,
                    "confidence": min(0.8 + abs(slope) * 0.1, 0.95)
                }
        
        return trends


class AlertManager:
    """Advanced alert management and notification system."""
    
    def __init__(self):
        self.alert_channels: Dict[str, Any] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.alert_suppression_rules: Dict[str, Any] = {}
    
    async def generate_alert(
        self, session_id: str, alert_type: str, severity: AlertSeverity, 
        message: str, metadata: Dict[str, Any]
    ) -> str:
        """Generate and route alert based on severity and type."""
        
        alert_id = f"alert_{uuid.uuid4().hex[:8]}"
        
        alert = {
            "alert_id": alert_id,
            "session_id": session_id,
            "type": alert_type,
            "severity": severity.value,
            "message": message,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        self.alert_history.append(alert)
        
        # Route alert based on severity
        await self._route_alert(alert)
        
        logger.info(f"Generated alert: {alert_id} [{severity.value}] {message}")
        
        return alert_id
    
    async def _route_alert(self, alert: Dict[str, Any]):
        """Route alert to appropriate channels."""
        
        severity = alert["severity"]
        
        if severity in ["critical", "high"]:
            # Send to immediate notification channels
            await self._send_immediate_notification(alert)
        elif severity == "medium":
            # Send to standard notification channels
            await self._send_standard_notification(alert)
        else:
            # Log only for low severity
            await self._log_alert(alert)
    
    async def _send_immediate_notification(self, alert: Dict[str, Any]):
        """Send immediate notification for critical alerts."""
        logger.warning(f"CRITICAL ALERT: {alert['message']}")
    
    async def _send_standard_notification(self, alert: Dict[str, Any]):
        """Send standard notification for medium severity alerts."""
        logger.info(f"ALERT: {alert['message']}")
    
    async def _log_alert(self, alert: Dict[str, Any]):
        """Log alert for low severity issues."""
        logger.debug(f"Alert logged: {alert['message']}")