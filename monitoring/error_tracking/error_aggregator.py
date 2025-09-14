"""
Error Aggregation System for Ainflue Platform
Centralized error collection and statistical analysis

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import json
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class ErrorEvent:
    """Structured error event for aggregation"""
    timestamp: datetime
    error_type: str
    error_message: str
    service_name: str
    workflow_stage: str
    user_id: Optional[str] = None
    severity: str = "error"
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None


@dataclass
class ErrorStatistics:
    """Error statistics for a specific time period"""
    total_errors: int
    unique_errors: int
    error_rate: float
    most_common_errors: List[Tuple[str, int]]
    affected_services: List[str]
    affected_users: int
    time_period: str
    generated_at: datetime


class ErrorAggregator:
    """
    Centralized error aggregation and analysis system
    Collects errors from multiple sources and provides statistics
    """
    
    def __init__(self, max_events -> None: int = 10000, retention_hours -> None: int = 24) -> None:
        """
        Initialize error aggregator
        
        Args:
            max_events: Maximum number of events to keep in memory
            retention_hours: How long to retain error events
        """
        self.max_events = max_events
        self.retention_hours = retention_hours
        self.events: List[ErrorEvent] = []
        self.error_counts = defaultdict(int)
        self.service_errors = defaultdict(int)
        self.workflow_errors = defaultdict(int)
        self.hourly_errors = defaultdict(int)
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def add_error(self, 
                  error_type: str,
                  error_message: str,
                  service_name: str,
                  workflow_stage: str,
                  user_id: Optional[str] = None,
                  severity: str = "error",
                  stack_trace: Optional[str] = None,
                  context: Optional[Dict[str, Any]] = None,
                  event_id: Optional[str] = None) -> None:
        """
        Add error event to aggregator
        
        Args:
            error_type: Type of error (exception class name)
            error_message: Error message
            service_name: Service where error occurred
            workflow_stage: Business workflow stage
            user_id: User ID if available
            severity: Error severity level
            stack_trace: Stack trace if available
            context: Additional context data
            event_id: Unique event identifier
        """
        event = ErrorEvent(
            timestamp=datetime.utcnow(),
            error_type=error_type,
            error_message=error_message,
            service_name=service_name,
            workflow_stage=workflow_stage,
            user_id=user_id,
            severity=severity,
            stack_trace=stack_trace,
            context=context,
            event_id=event_id
        )
        
        # Add to events list
        self.events.append(event)
        
        # Update counters
        self._update_counters(event)
        
        # Clean up old events if necessary
        if len(self.events) > self.max_events:
            self._cleanup_old_events()
        
        logger.debug(f"Added error event: {error_type} in {service_name}")
    
    def _update_counters(self, event: ErrorEvent) -> None:
        """Update internal counters with new event"""
        # Error type counting
        error_key = f"{event.error_type}:{event.service_name}"
        self.error_counts[error_key] += 1
        
        # Service error counting
        self.service_errors[event.service_name] += 1
        
        # Workflow stage error counting
        self.workflow_errors[event.workflow_stage] += 1
        
        # Hourly error counting
        hour_key = event.timestamp.strftime("%Y-%m-%d-%H")
        self.hourly_errors[hour_key] += 1
    
    def _cleanup_old_events(self) -> None:
        """Remove old events based on retention policy"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        # Filter out old events
        old_count = len(self.events)
        self.events = [event for event in self.events if event.timestamp > cutoff_time]
        new_count = len(self.events)
        
        if old_count > new_count:
            logger.info(f"Cleaned up {old_count - new_count} old error events")
            
            # Rebuild counters from remaining events
            self._rebuild_counters()
    
    def _rebuild_counters(self) -> None:
        """Rebuild all counters from current events"""
        self.error_counts.clear()
        self.service_errors.clear()
        self.workflow_errors.clear()
        self.hourly_errors.clear()
        
        for event in self.events:
            self._update_counters(event)
    
    def get_statistics(self, time_period: str = "24h") -> ErrorStatistics:
        """
        Get error statistics for specified time period
        
        Args:
            time_period: Time period (1h, 6h, 24h, 7d)
            
        Returns:
            ErrorStatistics object with aggregated data
        """
        # Parse time period
        hours = self._parse_time_period(time_period)
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter events for time period
        period_events = [event for event in self.events if event.timestamp > cutoff_time]
        
        if not period_events:
            return ErrorStatistics(
                total_errors=0,
                unique_errors=0,
                error_rate=0.0,
                most_common_errors=[],
                affected_services=[],
                affected_users=0,
                time_period=time_period,
                generated_at=datetime.utcnow()
            )
        
        # Calculate statistics
        total_errors = len(period_events)
        unique_errors = len(set(f"{e.error_type}:{e.error_message}" for e in period_events))
        
        # Error rate (errors per hour)
        error_rate = total_errors / hours if hours > 0 else total_errors
        
        # Most common errors
        error_counter = Counter(f"{e.error_type}: {e.error_message[:100]}" for e in period_events)
        most_common_errors = error_counter.most_common(10)
        
        # Affected services
        affected_services = list(set(e.service_name for e in period_events))
        
        # Affected users
        affected_users = len(set(e.user_id for e in period_events if e.user_id))
        
        return ErrorStatistics(
            total_errors=total_errors,
            unique_errors=unique_errors,
            error_rate=round(error_rate, 2),
            most_common_errors=most_common_errors,
            affected_services=affected_services,
            affected_users=affected_users,
            time_period=time_period,
            generated_at=datetime.utcnow()
        )
    
    def get_service_statistics(self, service_name: str, time_period: str = "24h") -> Dict[str, Any]:
        """
        Get error statistics for specific service
        
        Args:
            service_name: Name of the service
            time_period: Time period to analyze
            
        Returns:
            Service-specific error statistics
        """
        hours = self._parse_time_period(time_period)
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter events for service and time period
        service_events = [
            event for event in self.events 
            if event.service_name == service_name and event.timestamp > cutoff_time
        ]
        
        if not service_events:
            return {
                "service_name": service_name,
                "total_errors": 0,
                "error_rate": 0.0,
                "most_common_errors": [],
                "workflow_stages": [],
                "time_period": time_period
            }
        
        # Calculate service statistics
        total_errors = len(service_events)
        error_rate = total_errors / hours if hours > 0 else total_errors
        
        # Most common errors in this service
        error_counter = Counter(f"{e.error_type}: {e.error_message[:100]}" for e in service_events)
        most_common_errors = error_counter.most_common(5)
        
        # Workflow stages affected
        workflow_counter = Counter(e.workflow_stage for e in service_events)
        workflow_stages = workflow_counter.most_common()
        
        return {
            "service_name": service_name,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 2),
            "most_common_errors": most_common_errors,
            "workflow_stages": workflow_stages,
            "time_period": time_period
        }
    
    def get_workflow_statistics(self, workflow_stage: str, time_period: str = "24h") -> Dict[str, Any]:
        """
        Get error statistics for specific workflow stage
        
        Args:
            workflow_stage: Business workflow stage
            time_period: Time period to analyze
            
        Returns:
            Workflow-specific error statistics
        """
        hours = self._parse_time_period(time_period)
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter events for workflow stage and time period
        workflow_events = [
            event for event in self.events 
            if event.workflow_stage == workflow_stage and event.timestamp > cutoff_time
        ]
        
        if not workflow_events:
            return {
                "workflow_stage": workflow_stage,
                "total_errors": 0,
                "error_rate": 0.0,
                "most_common_errors": [],
                "affected_services": [],
                "time_period": time_period
            }
        
        # Calculate workflow statistics
        total_errors = len(workflow_events)
        error_rate = total_errors / hours if hours > 0 else total_errors
        
        # Most common errors in this workflow
        error_counter = Counter(f"{e.error_type}: {e.error_message[:100]}" for e in workflow_events)
        most_common_errors = error_counter.most_common(5)
        
        # Services affected
        service_counter = Counter(e.service_name for e in workflow_events)
        affected_services = service_counter.most_common()
        
        return {
            "workflow_stage": workflow_stage,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 2),
            "most_common_errors": most_common_errors,
            "affected_services": affected_services,
            "time_period": time_period
        }
    
    def get_hourly_trend(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get hourly error trend data
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            List of hourly error counts
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        trend_data = []
        
        for i in range(hours):
            hour_time = cutoff_time + timedelta(hours=i)
            hour_key = hour_time.strftime("%Y-%m-%d-%H")
            
            # Count errors for this hour
            hour_events = [
                event for event in self.events
                if event.timestamp.strftime("%Y-%m-%d-%H") == hour_key
            ]
            
            trend_data.append({
                "hour": hour_time.strftime("%Y-%m-%d %H:00"),
                "error_count": len(hour_events),
                "unique_errors": len(set(f"{e.error_type}:{e.error_message}" for e in hour_events))
            })
        
        return trend_data
    
    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """
        Get critical alerts based on error patterns
        
        Returns:
            List of critical alerts
        """
        alerts = []
        
        # Check for error spikes in last hour
        recent_events = [
            event for event in self.events
            if event.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        if len(recent_events) > 50:  # Threshold for error spike
            alerts.append({
                "type": "error_spike",
                "severity": "critical",
                "message": f"Error spike detected: {len(recent_events)} errors in last hour",
                "count": len(recent_events),
                "threshold": 50
            })
        
        # Check for service-specific issues
        service_counts = Counter(e.service_name for e in recent_events)
        for service, count in service_counts.items():
            if count > 20:  # Threshold for service issues
                alerts.append({
                    "type": "service_errors",
                    "severity": "warning",
                    "message": f"High error rate in {service}: {count} errors in last hour",
                    "service": service,
                    "count": count,
                    "threshold": 20
                })
        
        # Check for workflow stage issues
        workflow_counts = Counter(e.workflow_stage for e in recent_events)
        for workflow, count in workflow_counts.items():
            if count > 15:  # Threshold for workflow issues
                alerts.append({
                    "type": "workflow_errors",
                    "severity": "warning",
                    "message": f"High error rate in {workflow} workflow: {count} errors in last hour",
                    "workflow_stage": workflow,
                    "count": count,
                    "threshold": 15
                })
        
        return alerts
    
    def export_events(self, time_period: str = "24h", format: str = "json") -> str:
        """
        Export error events for external analysis
        
        Args:
            time_period: Time period to export
            format: Export format (json, csv)
            
        Returns:
            Serialized events data
        """
        hours = self._parse_time_period(time_period)
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter events for time period
        export_events = [
            event for event in self.events 
            if event.timestamp > cutoff_time
        ]
        
        if format == "json":
            return json.dumps(
                [asdict(event) for event in export_events],
                default=str,
                indent=2
            )
        elif format == "csv":
            # Simple CSV export
            csv_lines = ["timestamp,error_type,error_message,service_name,workflow_stage,user_id,severity"]
            for event in export_events:
                csv_lines.append(
                    f"{event.timestamp},{event.error_type},"
                    f'"{event.error_message}",{event.service_name},'
                    f"{event.workflow_stage},{event.user_id or ''},"
                    f"{event.severity}"
                )
            return "\n".join(csv_lines)
        
        return ""
    
    def _parse_time_period(self, time_period: str) -> int:
        """Parse time period string to hours"""
        if time_period.endswith('h'):
            return int(time_period[:-1])
        elif time_period.endswith('d'):
            return int(time_period[:-1]) * 24
        elif time_period.endswith('w'):
            return int(time_period[:-1]) * 24 * 7
        else:
            return 24  # Default to 24 hours
    
    def _start_cleanup_task(self) -> None:
        """Start background cleanup task"""
        try:
            # Try to start async cleanup if in async context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._periodic_cleanup())
        except RuntimeError:
            # Not in async context, cleanup will happen on new events
            pass
    
    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup task"""
        while True:
            await asyncio.sleep(3600)  # Run every hour
            self._cleanup_old_events()


# Global error aggregator instance
error_aggregator = ErrorAggregator()