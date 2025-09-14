"""Event Debugging Inspector - Advanced for Ainflue Events

Advanced debugging and inspection toolkit for event processing
with detailed tracing, performance analysis, and error diagnostics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
import json
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import traceback

logger = logging.getLogger(__name__)


class InspectionLevel(Enum):
    """Debug inspection levels"""
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    TRACE = "trace"


@dataclass
class DebugTrace:
    """Debug trace information"""
    trace_id: str
    event_id: str
    component: str
    operation: str
    timestamp: datetime
    duration_ms: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_info: Optional[str] = None


@dataclass
class InspectionReport:
    """Event inspection report"""
    event_id: str
    inspection_level: InspectionLevel
    traces: List[DebugTrace]
    performance_summary: Dict[str, Any]
    error_analysis: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)


class EventDebuggingInspector:
    """
    Advanced event debugging inspector for Ainflue platform
    Provides detailed tracing, performance analysis, and error diagnostics
    """
    
    def __init__(self, max_traces -> None: int = 5000) -> None:
        self.max_traces = max_traces
        self.debug_traces: deque = deque(maxlen=max_traces)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.performance_baselines: Dict[str, float] = {}
        
        logger.info("EventDebuggingInspector initialized")
    
    async def start_inspection_session(self, event_data: Dict[str, Any], 
                                     level: InspectionLevel = InspectionLevel.DETAILED) -> str:
        """Start debugging inspection session for an event"""
        
        session_id = f"debug_{event_data.get('event_id', 'unknown')}_{int(time.time() * 1000)}"
        
        session = {
            "session_id": session_id,
            "event_data": event_data,
            "inspection_level": level,
            "start_time": datetime.utcnow(),
            "traces": [],
            "performance_metrics": {},
            "errors": []
        }
        
        self.active_sessions[session_id] = session
        
        # Add initial trace
        await self.add_trace(session_id, "inspector", "session_started", success=True, metadata={
            "event_type": event_data.get("event_type"),
            "inspection_level": level.value
        })
        
        logger.debug(f"Started inspection session {session_id} for event {event_data.get('event_id')}")
        return session_id
    
    async def add_trace(self, session_id -> None: str, component -> None: str, operation -> None: str,
                       success -> None: bool = True, duration_ms -> None: Optional[float] = None,
                       metadata -> None: Optional[Dict[str, Any]] = None,
                       error_info -> None: Optional[str] = None) -> None:
        """Add a debug trace to inspection session"""
        
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found for trace")
            return
        
        session = self.active_sessions[session_id]
        
        trace = DebugTrace(
            trace_id=f"trace_{len(session['traces']) + 1}",
            event_id=session["event_data"].get("event_id", "unknown"),
            component=component,
            operation=operation,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms or 0.0,
            success=success,
            metadata=metadata or {},
            error_info=error_info
        )
        
        session["traces"].append(trace)
        self.debug_traces.append(trace)
        
        # Track error patterns
        if not success and error_info:
            error_key = f"{component}_{operation}"
            self.error_patterns[error_key] += 1
        
        # Update performance metrics
        if duration_ms and success:
            perf_key = f"{component}_{operation}"
            if perf_key not in session["performance_metrics"]:
                session["performance_metrics"][perf_key] = []
            session["performance_metrics"][perf_key].append(duration_ms)
            
            # Update baseline
            if perf_key not in self.performance_baselines:
                self.performance_baselines[perf_key] = duration_ms
            else:
                self.performance_baselines[perf_key] = (self.performance_baselines[perf_key] * 0.9 + duration_ms * 0.1)
        
        logger.debug(f"Added trace to session {session_id}: {component}.{operation}")
    
    async def end_inspection_session(self, session_id: str) -> InspectionReport:
        """End inspection session and generate report"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Generate performance summary
        performance_summary = await self._analyze_performance(session)
        
        # Generate error analysis
        error_analysis = await self._analyze_errors(session)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(session, performance_summary, error_analysis)
        
        report = InspectionReport(
            event_id=session["event_data"].get("event_id", "unknown"),
            inspection_level=session["inspection_level"],
            traces=session["traces"],
            performance_summary=performance_summary,
            error_analysis=error_analysis,
            recommendations=recommendations
        )
        
        # Clean up session
        del self.active_sessions[session_id]
        
        logger.info(f"Generated inspection report for session {session_id}")
        return report
    
    async def _analyze_performance(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics from session"""
        
        perf_metrics = session["performance_metrics"]
        
        analysis = {
            "total_duration": 0.0,
            "component_breakdown": {},
            "slowest_operations": [],
            "performance_issues": []
        }
        
        # Calculate total duration
        if session["traces"]:
            start_time = min(trace.timestamp for trace in session["traces"])
            end_time = max(trace.timestamp for trace in session["traces"])
            analysis["total_duration"] = (end_time - start_time).total_seconds() * 1000
        
        # Analyze component performance
        for perf_key, durations in perf_metrics.items():
            component, operation = perf_key.split("_", 1)
            
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            if component not in analysis["component_breakdown"]:
                analysis["component_breakdown"][component] = {
                    "total_time": 0.0,
                    "operation_count": 0,
                    "operations": {}
                }
            
            comp_data = analysis["component_breakdown"][component]
            comp_data["total_time"] += sum(durations)
            comp_data["operation_count"] += len(durations)
            comp_data["operations"][operation] = {
                "avg_duration": avg_duration,
                "max_duration": max_duration,
                "call_count": len(durations)
            }
            
            # Check against baseline
            baseline = self.performance_baselines.get(perf_key)
            if baseline and avg_duration > baseline * 2:  # 2x slower than baseline
                analysis["performance_issues"].append({
                    "component": component,
                    "operation": operation,
                    "issue": "performance_degradation",
                    "avg_duration": avg_duration,
                    "baseline": baseline,
                    "degradation_factor": avg_duration / baseline
                })
            
            # Track slowest operations
            analysis["slowest_operations"].append({
                "component": component,
                "operation": operation,
                "avg_duration": avg_duration,
                "max_duration": max_duration
            })
        
        # Sort slowest operations
        analysis["slowest_operations"].sort(key=lambda x: x["avg_duration"], reverse=True)
        analysis["slowest_operations"] = analysis["slowest_operations"][:5]
        
        return analysis
    
    async def _analyze_errors(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze errors from session traces"""
        
        error_traces = [trace for trace in session["traces"] if not trace.success]
        
        analysis = {
            "total_errors": len(error_traces),
            "error_rate": len(error_traces) / len(session["traces"]) if session["traces"] else 0.0,
            "error_categories": defaultdict(int),
            "error_patterns": [],
            "critical_errors": []
        }
        
        for trace in error_traces:
            # Categorize error
            if "timeout" in trace.error_info.lower() if trace.error_info else False:
                analysis["error_categories"]["timeout"] += 1
            elif "validation" in trace.error_info.lower() if trace.error_info else False:
                analysis["error_categories"]["validation"] += 1
            elif "permission" in trace.error_info.lower() if trace.error_info else False:
                analysis["error_categories"]["permission"] += 1
            elif "network" in trace.error_info.lower() if trace.error_info else False:
                analysis["error_categories"]["network"] += 1
            else:
                analysis["error_categories"]["unknown"] += 1
            
            # Check for critical errors
            if trace.component in ["payment", "security", "data"]:
                analysis["critical_errors"].append({
                    "component": trace.component,
                    "operation": trace.operation,
                    "error": trace.error_info,
                    "timestamp": trace.timestamp.isoformat()
                })
        
        # Identify error patterns
        component_errors = defaultdict(list)
        for trace in error_traces:
            component_errors[trace.component].append(trace)
        
        for component, errors in component_errors.items():
            if len(errors) > 1:  # Multiple errors in same component
                analysis["error_patterns"].append({
                    "component": component,
                    "error_count": len(errors),
                    "pattern": "repeated_component_failures",
                    "severity": "high" if component in ["payment", "security"] else "medium"
                })
        
        return analysis
    
    async def _generate_recommendations(self, session: Dict[str, Any],
                                      performance_summary: Dict[str, Any],
                                      error_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Performance recommendations
        if performance_summary["performance_issues"]:
            recommendations.append("Performance degradation detected - review slow operations and optimize")
            
            for issue in performance_summary["performance_issues"]:
                if issue["degradation_factor"] > 5:
                    recommendations.append(f"Critical: {issue['component']}.{issue['operation']} is {issue['degradation_factor']:.1f}x slower than baseline")
        
        if performance_summary["total_duration"] > 10000:  # 10 seconds
            recommendations.append("Total processing time exceeds 10 seconds - consider async processing")
        
        # Error recommendations
        if error_analysis["error_rate"] > 0.1:  # 10% error rate
            recommendations.append("High error rate detected - investigate error patterns and add resilience")
        
        if error_analysis["critical_errors"]:
            recommendations.append("Critical errors detected in sensitive components - immediate attention required")
        
        if "timeout" in error_analysis["error_categories"]:
            recommendations.append("Timeout errors detected - review timeout configurations and add retries")
        
        if "validation" in error_analysis["error_categories"]:
            recommendations.append("Validation errors found - strengthen input validation and error messaging")
        
        # Event-specific recommendations
        event_type = session["event_data"].get("event_type", "")
        
        if event_type.startswith("content.") and performance_summary["total_duration"] > 5000:
            recommendations.append("Content processing taking too long - consider background processing")
        
        if event_type.startswith("monetization.") and error_analysis["total_errors"] > 0:
            recommendations.append("Monetization errors require immediate review for business impact")
        
        if not recommendations:
            recommendations.append("No significant issues detected - event processing appears healthy")
        
        return recommendations
    
    async def inspect_event_processing_chain(self, event_data: Dict[str, Any],
                                           processing_chain: List[Callable],
                                           level: InspectionLevel = InspectionLevel.DETAILED) -> InspectionReport:
        """Inspect a complete event processing chain"""
        
        session_id = await self.start_inspection_session(event_data, level)
        
        try:
            for i, processor in enumerate(processing_chain):
                processor_name = processor.__name__ if hasattr(processor, '__name__') else f"processor_{i}"
                
                await self.add_trace(session_id, "chain", f"starting_{processor_name}", success=True)
                
                start_time = time.time()
                try:
                    # Execute processor (simplified - in real implementation would actually call it)
                    await self._simulate_processor_execution(processor_name)
                    
                    duration = (time.time() - start_time) * 1000
                    await self.add_trace(session_id, processor_name, "execute", 
                                       success=True, duration_ms=duration)
                    
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    await self.add_trace(session_id, processor_name, "execute",
                                       success=False, duration_ms=duration,
                                       error_info=str(e))
                    
                    # Continue with inspection even if processor fails
                    logger.warning(f"Processor {processor_name} failed: {e}")
            
            await self.add_trace(session_id, "chain", "completed", success=True)
            
        except Exception as e:
            await self.add_trace(session_id, "inspector", "chain_error",
                               success=False, error_info=str(e))
        
        return await self.end_inspection_session(session_id)
    
    async def _simulate_processor_execution(self, processor_name -> None: str) -> None:
        """Simulate processor execution for demonstration"""
        
        # Simulate different execution times and potential failures
        import random
        import asyncio
        
        base_time = 0.1
        if "ai" in processor_name.lower():
            base_time = 2.0
        elif "database" in processor_name.lower():
            base_time = 0.5
        elif "network" in processor_name.lower():
            base_time = 1.0
        
        # Add some randomness
        execution_time = base_time * (0.5 + random.random())
        await asyncio.sleep(execution_time)
        
        # Simulate occasional failures
        if random.random() < 0.05:  # 5% failure rate
            raise Exception(f"Simulated failure in {processor_name}")
    
    def search_traces(self, 
                     event_id: Optional[str] = None,
                     component: Optional[str] = None,
                     operation: Optional[str] = None,
                     success: Optional[bool] = None,
                     time_range: Optional[Tuple[datetime, datetime]] = None,
                     limit: int = 100) -> List[DebugTrace]:
        """Search debug traces with filters"""
        
        results = []
        
        for trace in self.debug_traces:
            # Apply filters
            if event_id and trace.event_id != event_id:
                continue
            if component and trace.component != component:
                continue
            if operation and trace.operation != operation:
                continue
            if success is not None and trace.success != success:
                continue
            if time_range:
                start_time, end_time = time_range
                if not (start_time <= trace.timestamp <= end_time):
                    continue
            
            results.append(trace)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics from debug traces"""
        
        total_traces = len(self.debug_traces)
        error_traces = [trace for trace in self.debug_traces if not trace.success]
        
        stats = {
            "total_traces": total_traces,
            "total_errors": len(error_traces),
            "error_rate": len(error_traces) / total_traces if total_traces > 0 else 0.0,
            "error_patterns": dict(self.error_patterns),
            "errors_by_component": defaultdict(int),
            "recent_errors": []
        }
        
        # Group errors by component
        for trace in error_traces:
            stats["errors_by_component"][trace.component] += 1
        
        # Get recent errors (last hour)
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_errors = [
            trace for trace in error_traces 
            if trace.timestamp >= recent_cutoff
        ]
        
        stats["recent_errors"] = [
            {
                "component": trace.component,
                "operation": trace.operation,
                "error": trace.error_info,
                "timestamp": trace.timestamp.isoformat()
            }
            for trace in recent_errors[-10:]  # Last 10 recent errors
        ]
        
        return stats
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance statistics from debug traces"""
        
        component_performance = defaultdict(list)
        
        for trace in self.debug_traces:
            if trace.success and trace.duration_ms > 0:
                key = f"{trace.component}_{trace.operation}"
                component_performance[key].append(trace.duration_ms)
        
        stats = {
            "total_successful_traces": len([t for t in self.debug_traces if t.success]),
            "performance_baselines": dict(self.performance_baselines),
            "component_performance": {}
        }
        
        for key, durations in component_performance.items():
            if durations:
                stats["component_performance"][key] = {
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "call_count": len(durations),
                    "p95_duration": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations)
                }
        
        return stats
    
    def export_debug_data(self, format: str = "json") -> str:
        """Export debug data for external analysis"""
        
        export_data = {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "total_traces": len(self.debug_traces),
                "active_sessions": len(self.active_sessions)
            },
            "traces": [
                {
                    "trace_id": trace.trace_id,
                    "event_id": trace.event_id,
                    "component": trace.component,
                    "operation": trace.operation,
                    "timestamp": trace.timestamp.isoformat(),
                    "duration_ms": trace.duration_ms,
                    "success": trace.success,
                    "metadata": trace.metadata,
                    "error_info": trace.error_info
                }
                for trace in self.debug_traces
            ],
            "error_patterns": dict(self.error_patterns),
            "performance_baselines": dict(self.performance_baselines)
        }
        
        if format == "json":
            return json.dumps(export_data, indent=2)
        else:
            return str(export_data)


# Export main classes
__all__ = [
    'EventDebuggingInspector',
    'InspectionLevel',
    'DebugTrace',
    'InspectionReport'
]