"""
Saga Monitoring Analytics module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""Saga Monitoring Analytics - Advanced Performance Analytics
============================================================

Advanced monitoring and analytics system for saga patterns.
Provides real-time metrics, performance insights, and
business intelligence for saga execution patterns.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class SagaMetric:
    """Individual saga metric"""
    saga_id: str
    saga_type: str
    metric_type: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for saga execution"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    p95_duration: float = 0.0
    p99_duration: float = 0.0
    error_rate: float = 0.0
    throughput_per_minute: float = 0.0


class SagaMonitoringAnalytics:
    """Main analytics system for saga monitoring"""
    
    def __init__(self, retention_hours -> None: int = 24) -> None:
        self.retention_hours = retention_hours
        self.metrics: deque = deque(maxlen=10000)  # Keep recent metrics
        self.saga_executions: Dict[str, Dict[str, Any]] = {}
        self.performance_cache: Dict[str, PerformanceMetrics] = {}
        self.aggregated_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Real-time counters
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        
        # Start background analytics (will be started when event loop is available)
        self._background_task = None
        self._should_start_background = True
    
    async def record_saga_started(
        self,
        saga_id -> None: str,
        saga_type -> None: str,
        metadata -> None: Dict[str, Any] = None
    ) -> None:
        """Record saga start event"""
        # Start background task if not started yet
        if self._should_start_background and self._background_task is None:
            try:
                self._background_task = asyncio.create_task(self._background_analytics())
                self._should_start_background = False
            except RuntimeError:
                # No event loop yet, will try again later
                pass
        self.saga_executions[saga_id] = {
            "saga_type": saga_type,
            "started_at": time.time(),
            "status": "running",
            "metadata": metadata or {}
        }
        
        # Update counters
        self.counters[f"saga_started_total"] += 1
        self.counters[f"saga_started_{saga_type}"] += 1
        self.gauges["active_sagas"] = len([
            s for s in self.saga_executions.values() 
            if s["status"] == "running"
        ])
        
        # Record metric
        await self._record_metric(
            saga_id, saga_type, "saga_started", 1.0, metadata
        )
    
    async def record_saga_completed(
        self,
        saga_id -> None: str,
        success -> None: bool = True,
        duration -> None: Optional[float] = None,
        metadata -> None: Dict[str, Any] = None
    ) -> None:
        """Record saga completion event"""
        if saga_id not in self.saga_executions:
            logger.warning(f"No start record found for saga {saga_id}")
            return
        
        execution = self.saga_executions[saga_id]
        saga_type = execution["saga_type"]
        
        # Calculate duration if not provided
        if duration is None:
            duration = time.time() - execution["started_at"]
        
        # Update execution record
        execution["completed_at"] = time.time()
        execution["duration"] = duration
        execution["status"] = "completed" if success else "failed"
        execution["success"] = success
        
        # Update counters
        if success:
            self.counters[f"saga_completed_total"] += 1
            self.counters[f"saga_completed_{saga_type}"] += 1
        else:
            self.counters[f"saga_failed_total"] += 1
            self.counters[f"saga_failed_{saga_type}"] += 1
        
        self.gauges["active_sagas"] = len([
            s for s in self.saga_executions.values() 
            if s["status"] == "running"
        ])
        
        # Record duration histogram
        self.histograms[f"saga_duration_{saga_type}"].append(duration)
        
        # Record metrics
        await self._record_metric(
            saga_id, saga_type, "saga_completed", 1.0 if success else 0.0, metadata
        )
        await self._record_metric(
            saga_id, saga_type, "saga_duration", duration, metadata
        )
        
        # Update performance cache
        await self._update_performance_metrics(saga_type)
    
    async def record_step_executed(
        self,
        saga_id -> None: str,
        step_name -> None: str,
        duration -> None: float,
        success -> None: bool = True,
        metadata -> None: Dict[str, Any] = None
    ) -> None:
        """Record saga step execution"""
        if saga_id not in self.saga_executions:
            return
        
        saga_type = self.saga_executions[saga_id]["saga_type"]
        
        # Update counters
        self.counters[f"step_executed_{step_name}"] += 1
        if success:
            self.counters[f"step_completed_{step_name}"] += 1
        else:
            self.counters[f"step_failed_{step_name}"] += 1
        
        # Record duration
        self.histograms[f"step_duration_{step_name}"].append(duration)
        
        # Record metrics
        await self._record_metric(
            saga_id, saga_type, f"step_{step_name}_duration", duration, metadata
        )
        await self._record_metric(
            saga_id, saga_type, f"step_{step_name}_success", 1.0 if success else 0.0, metadata
        )
    
    async def record_compensation_executed(
        self,
        saga_id -> None: str,
        compensation_type -> None: str,
        duration -> None: float,
        success -> None: bool = True,
        metadata -> None: Dict[str, Any] = None
    ) -> None:
        """Record compensation execution"""
        if saga_id not in self.saga_executions:
            return
        
        saga_type = self.saga_executions[saga_id]["saga_type"]
        
        # Update counters
        self.counters[f"compensation_executed_total"] += 1
        self.counters[f"compensation_{compensation_type}"] += 1
        
        if success:
            self.counters[f"compensation_success_total"] += 1
        else:
            self.counters[f"compensation_failed_total"] += 1
        
        # Record metrics
        await self._record_metric(
            saga_id, saga_type, f"compensation_{compensation_type}_duration", duration, metadata
        )
        await self._record_metric(
            saga_id, saga_type, f"compensation_{compensation_type}_success", 1.0 if success else 0.0, metadata
        )
    
    async def _record_metric(
        self,
        saga_id -> None: str,
        saga_type -> None: str,
        metric_type -> None: str,
        value -> None: float,
        metadata -> None: Dict[str, Any] = None
    ) -> None:
        """Record individual metric"""
        metric = SagaMetric(
            saga_id=saga_id,
            saga_type=saga_type,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
    
    async def _update_performance_metrics(self, saga_type -> None: str) -> None:
        """Update cached performance metrics"""
        # Get completed executions for saga type
        completed_executions = [
            exec_data for exec_data in self.saga_executions.values()
            if (exec_data["saga_type"] == saga_type and 
                exec_data["status"] in ["completed", "failed"] and
                "duration" in exec_data)
        ]
        
        if not completed_executions:
            return
        
        durations = [exec_data["duration"] for exec_data in completed_executions]
        successful = [exec_data for exec_data in completed_executions if exec_data.get("success", False)]
        
        # Calculate metrics
        metrics = PerformanceMetrics()
        metrics.total_executions = len(completed_executions)
        metrics.successful_executions = len(successful)
        metrics.failed_executions = metrics.total_executions - metrics.successful_executions
        metrics.error_rate = metrics.failed_executions / metrics.total_executions
        
        if durations:
            metrics.average_duration = sum(durations) / len(durations)
            metrics.min_duration = min(durations)
            metrics.max_duration = max(durations)
            
            # Calculate percentiles
            sorted_durations = sorted(durations)
            p95_index = int(0.95 * len(sorted_durations))
            p99_index = int(0.99 * len(sorted_durations))
            metrics.p95_duration = sorted_durations[p95_index] if p95_index < len(sorted_durations) else sorted_durations[-1]
            metrics.p99_duration = sorted_durations[p99_index] if p99_index < len(sorted_durations) else sorted_durations[-1]
        
        # Calculate throughput (executions per minute in last hour)
        current_time = time.time()
        recent_executions = [
            exec_data for exec_data in completed_executions
            if current_time - exec_data.get("completed_at", 0) <= 3600  # Last hour
        ]
        metrics.throughput_per_minute = len(recent_executions) / 60.0
        
        self.performance_cache[saga_type] = metrics
    
    async def get_performance_metrics(self, saga_type: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics for saga type"""
        if saga_type not in self.performance_cache:
            await self._update_performance_metrics(saga_type)
        
        return self.performance_cache.get(saga_type)
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics"""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "active_sagas": self.gauges["active_sagas"],
            "total_saga_executions": self.counters.get("saga_started_total", 0),
            "successful_sagas": self.counters.get("saga_completed_total", 0),
            "failed_sagas": self.counters.get("saga_failed_total", 0)
        }
    
    async def get_saga_type_analytics(self) -> Dict[str, Dict[str, Any]]:
        """Get analytics by saga type"""
        analytics = {}
        
        # Group executions by saga type
        by_type = defaultdict(list)
        for exec_data in self.saga_executions.values():
            if exec_data["status"] in ["completed", "failed"]:
                by_type[exec_data["saga_type"]].append(exec_data)
        
        for saga_type, executions in by_type.items():
            total = len(executions)
            successful = len([e for e in executions if e.get("success", False)])
            failed = total - successful
            
            analytics[saga_type] = {
                "total_executions": total,
                "successful_executions": successful,
                "failed_executions": failed,
                "success_rate": successful / total if total > 0 else 0,
                "error_rate": failed / total if total > 0 else 0
            }
            
            # Add performance metrics if available
            perf_metrics = await self.get_performance_metrics(saga_type)
            if perf_metrics:
                analytics[saga_type].update({
                    "average_duration": perf_metrics.average_duration,
                    "p95_duration": perf_metrics.p95_duration,
                    "throughput_per_minute": perf_metrics.throughput_per_minute
                })
        
        return analytics
    
    async def get_step_analytics(self) -> Dict[str, Dict[str, Any]]:
        """Get analytics by step type"""
        analytics = {}
        
        # Analyze step performance
        for key, count in self.counters.items():
            if key.startswith("step_executed_"):
                step_name = key.replace("step_executed_", "")
                completed = self.counters.get(f"step_completed_{step_name}", 0)
                failed = self.counters.get(f"step_failed_{step_name}", 0)
                
                analytics[step_name] = {
                    "total_executions": count,
                    "successful_executions": completed,
                    "failed_executions": failed,
                    "success_rate": completed / count if count > 0 else 0,
                    "error_rate": failed / count if count > 0 else 0
                }
                
                # Add duration statistics
                durations = self.histograms.get(f"step_duration_{step_name}", [])
                if durations:
                    analytics[step_name].update({
                        "average_duration": sum(durations) / len(durations),
                        "min_duration": min(durations),
                        "max_duration": max(durations)
                    })
        
        return analytics
    
    async def get_trending_metrics(self, hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Get trending metrics for specified time period"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_metrics = [
            metric for metric in self.metrics
            if metric.timestamp >= cutoff_time
        ]
        
        # Group by saga type and metric type
        trending = defaultdict(lambda: defaultdict(list))
        
        for metric in recent_metrics:
            trending[metric.saga_type][metric.metric_type].append({
                "timestamp": metric.timestamp.isoformat(),
                "value": metric.value
            })
        
        return dict(trending)
    
    async def _background_analytics(self) -> None:
        """Background task for continuous analytics"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Update all performance metrics
                saga_types = set(exec_data["saga_type"] for exec_data in self.saga_executions.values())
                for saga_type in saga_types:
                    await self._update_performance_metrics(saga_type)
                
                # Cleanup old data
                await self._cleanup_old_data()
                
            except Exception as e:
                logger.error(f"Background analytics error: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Cleanup old execution data"""
        cutoff_time = time.time() - (self.retention_hours * 3600)
        
        # Remove old saga executions
        to_remove = [
            saga_id for saga_id, exec_data in self.saga_executions.items()
            if (exec_data["status"] in ["completed", "failed"] and
                exec_data.get("completed_at", 0) < cutoff_time)
        ]
        
        for saga_id in to_remove:
            del self.saga_executions[saga_id]
        
        # Trim histograms
        for key in self.histograms:
            if len(self.histograms[key]) > 1000:
                self.histograms[key] = self.histograms[key][-1000:]
    
    async def export_metrics(self, format: str = "json") -> Dict[str, Any]:
        """Export all metrics in specified format"""
        export_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "real_time_metrics": await self.get_real_time_metrics(),
            "saga_type_analytics": await self.get_saga_type_analytics(),
            "step_analytics": await self.get_step_analytics(),
            "performance_metrics": {
                saga_type: {
                    "total_executions": metrics.total_executions,
                    "successful_executions": metrics.successful_executions,
                    "failed_executions": metrics.failed_executions,
                    "average_duration": metrics.average_duration,
                    "p95_duration": metrics.p95_duration,
                    "p99_duration": metrics.p99_duration,
                    "error_rate": metrics.error_rate,
                    "throughput_per_minute": metrics.throughput_per_minute
                }
                for saga_type, metrics in self.performance_cache.items()
            }
        }
        
        return export_data


# Global analytics instance
_monitoring_analytics: Optional[SagaMonitoringAnalytics] = None


def get_saga_monitoring_analytics() -> SagaMonitoringAnalytics:
    """Get global saga monitoring analytics"""
    global _monitoring_analytics
    if _monitoring_analytics is None:
        _monitoring_analytics = SagaMonitoringAnalytics()
    
    return _monitoring_analytics


# Convenience functions
async def record_saga_started(saga_id -> None: str, saga_type -> None: str, metadata -> None: Dict[str, Any] = None) -> None:
    """Convenience function to record saga start"""
    analytics = get_saga_monitoring_analytics()
    await analytics.record_saga_started(saga_id, saga_type, metadata)


async def record_saga_completed(saga_id -> None: str, success -> None: bool = True, duration -> None: float = None) -> None:
    """Convenience function to record saga completion"""
    analytics = get_saga_monitoring_analytics()
    await analytics.record_saga_completed(saga_id, success, duration)


__all__ = [
    "SagaMonitoringAnalytics",
    "SagaMetric",
    "PerformanceMetrics",
    "get_saga_monitoring_analytics",
    "record_saga_started",
    "record_saga_completed"
]