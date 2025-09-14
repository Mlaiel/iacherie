"""
Error Analysis System for Ainflue Platform
Advanced error pattern analysis and machine learning insights

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ErrorPattern:
    """Detected error pattern"""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    services_affected: List[str]
    workflow_stages_affected: List[str]
    first_seen: datetime
    last_seen: datetime
    severity_score: float
    recommended_actions: List[str]


@dataclass
class ErrorTrend:
    """Error trend analysis"""
    trend_type: str
    direction: str  # increasing, decreasing, stable
    change_percentage: float
    time_period: str
    significance: str  # high, medium, low
    description: str


class ErrorAnalyzer:
    """
    Advanced error analysis system
    Provides pattern detection, trend analysis, and actionable insights
    """
    
    def __init__(self) -> None:
        """Initialize error analyzer"""
        self.patterns: Dict[str, ErrorPattern] = {}
        self.known_patterns = self._load_known_patterns()
        self.correlation_cache = {}
    
    def analyze_errors(self, events: List[Any], time_window: int = 24) -> Dict[str, Any]:
        """
        Comprehensive error analysis
        
        Args:
            events: List of error events
            time_window: Analysis time window in hours
            
        Returns:
            Comprehensive analysis results
        """
        if not events:
            return {
                "patterns": [],
                "trends": [],
                "correlations": [],
                "recommendations": [],
                "severity_assessment": "low"
            }
        
        # Detect patterns
        patterns = self._detect_patterns(events)
        
        # Analyze trends
        trends = self._analyze_trends(events, time_window)
        
        # Find correlations
        correlations = self._find_correlations(events)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(patterns, trends, correlations)
        
        # Assess overall severity
        severity = self._assess_severity(patterns, trends, events)
        
        return {
            "patterns": [self._pattern_to_dict(p) for p in patterns],
            "trends": [self._trend_to_dict(t) for t in trends],
            "correlations": correlations,
            "recommendations": recommendations,
            "severity_assessment": severity,
            "analysis_metadata": {
                "total_events": len(events),
                "time_window_hours": time_window,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def _detect_patterns(self, events: List[Any]) -> List[ErrorPattern]:
        """Detect error patterns in events"""
        patterns = []
        
        # Group events by error signature
        error_groups = defaultdict(list)
        for event in events:
            signature = self._generate_error_signature(event)
            error_groups[signature].append(event)
        
        # Analyze each group for patterns
        for signature, group_events in error_groups.items():
            if len(group_events) >= 3:  # Minimum threshold for pattern
                pattern = self._analyze_error_group(signature, group_events)
                if pattern:
                    patterns.append(pattern)
        
        # Detect sequence patterns
        sequence_patterns = self._detect_sequence_patterns(events)
        patterns.extend(sequence_patterns)
        
        # Detect frequency patterns
        frequency_patterns = self._detect_frequency_patterns(events)
        patterns.extend(frequency_patterns)
        
        return patterns
    
    def _generate_error_signature(self, event: Any) -> str:
        """Generate unique signature for error clustering"""
        # Normalize error message (remove dynamic content)
        normalized_message = self._normalize_error_message(
            getattr(event, 'error_message', '')
        )
        
        # Create signature from key attributes
        signature_parts = [
            getattr(event, 'error_type', 'unknown'),
            getattr(event, 'service_name', 'unknown'),
            getattr(event, 'workflow_stage', 'unknown'),
            normalized_message[:100]  # First 100 chars of normalized message
        ]
        
        signature_string = "|".join(signature_parts)
        return hashlib.md5(signature_string.encode()).hexdigest()[:16]
    
    def _normalize_error_message(self, message: str) -> str:
        """Normalize error message by removing dynamic content"""
        if not message:
            return ""
        
        # Remove timestamps
        message = re.sub(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}', '<TIMESTAMP>', message)
        
        # Remove UUIDs
        message = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<UUID>', message)
        
        # Remove file paths
        message = re.sub(r'/[/\w\-\.]+\.py', '<FILEPATH>', message)
        
        # Remove line numbers
        message = re.sub(r'line \d+', 'line <LINE>', message)
        
        # Remove IP addresses
        message = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '<IP>', message)
        
        # Remove numbers that might be dynamic
        message = re.sub(r'\b\d{4,}\b', '<NUMBER>', message)
        
        return message.strip()
    
    def _analyze_error_group(self, signature: str, events: List[Any]) -> Optional[ErrorPattern]:
        """Analyze a group of similar errors"""
        if not events:
            return None
        
        first_event = events[0]
        
        # Extract common attributes
        services = set(getattr(e, 'service_name', 'unknown') for e in events)
        workflows = set(getattr(e, 'workflow_stage', 'unknown') for e in events)
        
        # Calculate time span
        timestamps = [getattr(e, 'timestamp', datetime.utcnow()) for e in events]
        first_seen = min(timestamps)
        last_seen = max(timestamps)
        
        # Determine pattern type
        pattern_type = self._classify_pattern_type(events)
        
        # Generate description
        description = self._generate_pattern_description(events, pattern_type)
        
        # Calculate severity score
        severity_score = self._calculate_pattern_severity(events, pattern_type)
        
        # Generate recommendations
        recommendations = self._generate_pattern_recommendations(events, pattern_type)
        
        return ErrorPattern(
            pattern_id=signature,
            pattern_type=pattern_type,
            description=description,
            frequency=len(events),
            services_affected=list(services),
            workflow_stages_affected=list(workflows),
            first_seen=first_seen,
            last_seen=last_seen,
            severity_score=severity_score,
            recommended_actions=recommendations
        )
    
    def _classify_pattern_type(self, events: List[Any]) -> str:
        """Classify the type of error pattern"""
        if len(events) < 3:
            return "isolated"
        
        # Check time distribution
        timestamps = [getattr(e, 'timestamp', datetime.utcnow()) for e in events]
        time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                     for i in range(len(timestamps)-1)]
        
        avg_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        
        if avg_diff < 60:  # Less than 1 minute apart
            return "burst"
        elif avg_diff < 3600:  # Less than 1 hour apart
            return "recurring"
        elif len(events) > 10:
            return "persistent"
        else:
            return "intermittent"
    
    def _generate_pattern_description(self, events: List[Any], pattern_type: str) -> str:
        """Generate human-readable pattern description"""
        first_event = events[0]
        error_type = getattr(first_event, 'error_type', 'Unknown error')
        service = getattr(first_event, 'service_name', 'unknown service')
        workflow = getattr(first_event, 'workflow_stage', 'unknown stage')
        
        descriptions = {
            "burst": f"Burst of {len(events)} {error_type} errors in {service} during {workflow}",
            "recurring": f"Recurring {error_type} errors in {service} ({len(events)} occurrences)",
            "persistent": f"Persistent {error_type} errors affecting {service} in {workflow} stage",
            "intermittent": f"Intermittent {error_type} errors in {service}",
            "isolated": f"Isolated {error_type} error in {service}"
        }
        
        return descriptions.get(pattern_type, f"{error_type} error pattern in {service}")
    
    def _calculate_pattern_severity(self, events: List[Any], pattern_type: str) -> float:
        """Calculate severity score for pattern (0-1)"""
        base_score = {
            "burst": 0.8,
            "recurring": 0.6,
            "persistent": 0.9,
            "intermittent": 0.4,
            "isolated": 0.2
        }.get(pattern_type, 0.5)
        
        # Adjust based on frequency
        frequency_multiplier = min(len(events) / 10, 1.0)
        
        # Adjust based on services affected
        services = set(getattr(e, 'service_name', '') for e in events)
        service_multiplier = min(len(services) / 3, 1.0)
        
        # Adjust based on severity levels
        severities = [getattr(e, 'severity', 'error') for e in events]
        critical_count = sum(1 for s in severities if s in ['critical', 'emergency'])
        severity_multiplier = 1.0 + (critical_count / len(events))
        
        final_score = base_score * (1 + frequency_multiplier + service_multiplier + severity_multiplier) / 4
        return min(final_score, 1.0)
    
    def _generate_pattern_recommendations(self, events: List[Any], pattern_type: str) -> List[str]:
        """Generate actionable recommendations for pattern"""
        recommendations = []
        
        first_event = events[0]
        service = getattr(first_event, 'service_name', 'unknown')
        workflow = getattr(first_event, 'workflow_stage', 'unknown')
        error_type = getattr(first_event, 'error_type', 'Unknown')
        
        if pattern_type == "burst":
            recommendations.extend([
                f"Investigate sudden spike in {error_type} errors in {service}",
                "Check for recent deployments or configuration changes",
                "Review resource utilization during burst period",
                "Consider implementing circuit breaker pattern"
            ])
        elif pattern_type == "recurring":
            recommendations.extend([
                f"Implement retry logic with exponential backoff for {error_type}",
                f"Add monitoring alerts for {service} error rates",
                "Review error handling in affected workflow stages",
                "Consider adding health checks"
            ])
        elif pattern_type == "persistent":
            recommendations.extend([
                f"Critical: Address persistent {error_type} in {service}",
                "Review service configuration and dependencies",
                "Check database connections and external service availability",
                "Consider temporary workaround or service isolation"
            ])
        
        return recommendations
    
    def _detect_sequence_patterns(self, events: List[Any]) -> List[ErrorPattern]:
        """Detect sequential error patterns across services"""
        patterns = []
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: getattr(e, 'timestamp', datetime.utcnow()))
        
        # Look for cascading failures
        cascade_sequences = self._find_cascade_sequences(sorted_events)
        
        for sequence in cascade_sequences:
            if len(sequence) >= 3:
                pattern = self._create_sequence_pattern(sequence)
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_frequency_patterns(self, events: List[Any]) -> List[ErrorPattern]:
        """Detect frequency-based patterns"""
        patterns = []
        
        # Group by hour and analyze frequency patterns
        hourly_counts = defaultdict(int)
        for event in events:
            timestamp = getattr(event, 'timestamp', datetime.utcnow())
            hour_key = timestamp.strftime("%H")
            hourly_counts[hour_key] += 1
        
        # Detect peak hours
        if hourly_counts:
            max_count = max(hourly_counts.values())
            avg_count = sum(hourly_counts.values()) / len(hourly_counts)
            
            if max_count > avg_count * 2:  # Peak is 2x average
                peak_hours = [hour for hour, count in hourly_counts.items() if count > avg_count * 1.5]
                
                if peak_hours:
                    pattern = ErrorPattern(
                        pattern_id=f"frequency_peak_{hash(''.join(peak_hours)) % 10000}",
                        pattern_type="frequency_peak",
                        description=f"Error frequency peaks during hours: {', '.join(peak_hours)}",
                        frequency=max_count,
                        services_affected=[],
                        workflow_stages_affected=[],
                        first_seen=min(getattr(e, 'timestamp', datetime.utcnow()) for e in events),
                        last_seen=max(getattr(e, 'timestamp', datetime.utcnow()) for e in events),
                        severity_score=0.6,
                        recommended_actions=[
                            "Investigate system load during peak hours",
                            "Consider scaling resources during identified peak periods",
                            "Review batch job schedules"
                        ]
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _find_cascade_sequences(self, sorted_events: List[Any]) -> List[List[Any]]:
        """Find cascading failure sequences"""
        sequences = []
        current_sequence = []
        last_timestamp = None
        
        for event in sorted_events:
            timestamp = getattr(event, 'timestamp', datetime.utcnow())
            
            if last_timestamp is None:
                current_sequence = [event]
            elif (timestamp - last_timestamp).total_seconds() <= 300:  # 5 minutes
                current_sequence.append(event)
            else:
                if len(current_sequence) >= 3:
                    sequences.append(current_sequence)
                current_sequence = [event]
            
            last_timestamp = timestamp
        
        # Don't forget the last sequence
        if len(current_sequence) >= 3:
            sequences.append(current_sequence)
        
        return sequences
    
    def _create_sequence_pattern(self, sequence: List[Any]) -> Optional[ErrorPattern]:
        """Create pattern from error sequence"""
        if not sequence:
            return None
        
        services = [getattr(e, 'service_name', 'unknown') for e in sequence]
        workflows = [getattr(e, 'workflow_stage', 'unknown') for e in sequence]
        
        # Look for service cascade pattern
        unique_services = []
        for service in services:
            if not unique_services or service != unique_services[-1]:
                unique_services.append(service)
        
        if len(unique_services) >= 2:
            pattern_id = f"cascade_{hash('->'.join(unique_services)) % 10000}"
            description = f"Cascading failures: {' -> '.join(unique_services)}"
            
            return ErrorPattern(
                pattern_id=pattern_id,
                pattern_type="cascade",
                description=description,
                frequency=len(sequence),
                services_affected=list(set(services)),
                workflow_stages_affected=list(set(workflows)),
                first_seen=getattr(sequence[0], 'timestamp', datetime.utcnow()),
                last_seen=getattr(sequence[-1], 'timestamp', datetime.utcnow()),
                severity_score=0.8,
                recommended_actions=[
                    "Implement circuit breaker patterns between dependent services",
                    "Review service dependencies and timeout configurations",
                    "Add bulkhead isolation between service components",
                    "Investigate root cause in initial failing service"
                ]
            )
        
        return None
    
    def _analyze_trends(self, events: List[Any], time_window: int) -> List[ErrorTrend]:
        """Analyze error trends over time"""
        trends = []
        
        if len(events) < 10:  # Need sufficient data for trend analysis
            return trends
        
        # Analyze overall error trend
        overall_trend = self._analyze_overall_trend(events, time_window)
        if overall_trend:
            trends.append(overall_trend)
        
        # Analyze service-specific trends
        service_trends = self._analyze_service_trends(events, time_window)
        trends.extend(service_trends)
        
        # Analyze workflow-specific trends
        workflow_trends = self._analyze_workflow_trends(events, time_window)
        trends.extend(workflow_trends)
        
        return trends
    
    def _analyze_overall_trend(self, events: List[Any], time_window: int) -> Optional[ErrorTrend]:
        """Analyze overall error trend"""
        # Split time window in half for comparison
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window//2)
        
        recent_events = [e for e in events if getattr(e, 'timestamp', datetime.utcnow()) > cutoff_time]
        older_events = [e for e in events if getattr(e, 'timestamp', datetime.utcnow()) <= cutoff_time]
        
        if not older_events:
            return None
        
        recent_rate = len(recent_events) / (time_window / 2)
        older_rate = len(older_events) / (time_window / 2)
        
        if older_rate == 0:
            return None
        
        change_percentage = ((recent_rate - older_rate) / older_rate) * 100
        
        if abs(change_percentage) < 10:
            direction = "stable"
            significance = "low"
        elif change_percentage > 0:
            direction = "increasing"
            significance = "high" if change_percentage > 50 else "medium"
        else:
            direction = "decreasing"
            significance = "high" if change_percentage < -50 else "medium"
        
        return ErrorTrend(
            trend_type="overall",
            direction=direction,
            change_percentage=round(change_percentage, 2),
            time_period=f"{time_window}h",
            significance=significance,
            description=f"Overall error rate is {direction} by {abs(change_percentage):.1f}%"
        )
    
    def _analyze_service_trends(self, events: List[Any], time_window: int) -> List[ErrorTrend]:
        """Analyze trends per service"""
        trends = []
        
        # Group events by service
        service_events = defaultdict(list)
        for event in events:
            service = getattr(event, 'service_name', 'unknown')
            service_events[service].append(event)
        
        # Analyze trend for each service with sufficient data
        for service, svc_events in service_events.items():
            if len(svc_events) >= 5:
                trend = self._analyze_single_service_trend(service, svc_events, time_window)
                if trend:
                    trends.append(trend)
        
        return trends
    
    def _analyze_single_service_trend(self, service: str, events: List[Any], time_window: int) -> Optional[ErrorTrend]:
        """Analyze trend for single service"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window//2)
        
        recent_events = [e for e in events if getattr(e, 'timestamp', datetime.utcnow()) > cutoff_time]
        older_events = [e for e in events if getattr(e, 'timestamp', datetime.utcnow()) <= cutoff_time]
        
        if not older_events:
            return None
        
        recent_rate = len(recent_events) / (time_window / 2)
        older_rate = len(older_events) / (time_window / 2)
        
        if older_rate == 0:
            return None
        
        change_percentage = ((recent_rate - older_rate) / older_rate) * 100
        
        if abs(change_percentage) < 20:
            return None  # Not significant enough for service-level reporting
        
        direction = "increasing" if change_percentage > 0 else "decreasing"
        significance = "high" if abs(change_percentage) > 50 else "medium"
        
        return ErrorTrend(
            trend_type="service",
            direction=direction,
            change_percentage=round(change_percentage, 2),
            time_period=f"{time_window}h",
            significance=significance,
            description=f"Error rate in {service} is {direction} by {abs(change_percentage):.1f}%"
        )
    
    def _analyze_workflow_trends(self, events: List[Any], time_window: int) -> List[ErrorTrend]:
        """Analyze trends per workflow stage"""
        trends = []
        
        # Group events by workflow stage
        workflow_events = defaultdict(list)
        for event in events:
            workflow = getattr(event, 'workflow_stage', 'unknown')
            workflow_events[workflow].append(event)
        
        # Analyze trend for each workflow with sufficient data
        for workflow, wf_events in workflow_events.items():
            if len(wf_events) >= 5:
                trend = self._analyze_single_workflow_trend(workflow, wf_events, time_window)
                if trend:
                    trends.append(trend)
        
        return trends
    
    def _analyze_single_workflow_trend(self, workflow: str, events: List[Any], time_window: int) -> Optional[ErrorTrend]:
        """Analyze trend for single workflow stage"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window//2)
        
        recent_events = [e for e in events if getattr(e, 'timestamp', datetime.utcnow()) > cutoff_time]
        older_events = [e for e in events if getattr(e, 'timestamp', datetime.utcnow()) <= cutoff_time]
        
        if not older_events:
            return None
        
        recent_rate = len(recent_events) / (time_window / 2)
        older_rate = len(older_events) / (time_window / 2)
        
        if older_rate == 0:
            return None
        
        change_percentage = ((recent_rate - older_rate) / older_rate) * 100
        
        if abs(change_percentage) < 25:
            return None  # Not significant enough for workflow-level reporting
        
        direction = "increasing" if change_percentage > 0 else "decreasing"
        significance = "high" if abs(change_percentage) > 50 else "medium"
        
        return ErrorTrend(
            trend_type="workflow",
            direction=direction,
            change_percentage=round(change_percentage, 2),
            time_period=f"{time_window}h",
            significance=significance,
            description=f"Error rate in {workflow} workflow is {direction} by {abs(change_percentage):.1f}%"
        )
    
    def _find_correlations(self, events: List[Any]) -> List[Dict[str, Any]]:
        """Find correlations between different error types and conditions"""
        correlations = []
        
        # Service-to-service correlations
        service_correlations = self._find_service_correlations(events)
        correlations.extend(service_correlations)
        
        # Time-based correlations
        time_correlations = self._find_time_correlations(events)
        correlations.extend(time_correlations)
        
        # Workflow correlations
        workflow_correlations = self._find_workflow_correlations(events)
        correlations.extend(workflow_correlations)
        
        return correlations
    
    def _find_service_correlations(self, events: List[Any]) -> List[Dict[str, Any]]:
        """Find correlations between service errors"""
        correlations = []
        
        # Build service error timeline
        service_timeline = defaultdict(list)
        for event in events:
            service = getattr(event, 'service_name', 'unknown')
            timestamp = getattr(event, 'timestamp', datetime.utcnow())
            service_timeline[service].append(timestamp)
        
        # Look for temporal correlations between services
        services = list(service_timeline.keys())
        for i, service_a in enumerate(services):
            for service_b in services[i+1:]:
                correlation = self._calculate_service_correlation(
                    service_a, service_timeline[service_a],
                    service_b, service_timeline[service_b]
                )
                if correlation and correlation['strength'] > 0.3:
                    correlations.append(correlation)
        
        return correlations
    
    def _calculate_service_correlation(self, service_a: str, times_a: List[datetime],
                                     service_b: str, times_b: List[datetime]) -> Optional[Dict[str, Any]]:
        """Calculate correlation between two services"""
        if len(times_a) < 3 or len(times_b) < 3:
            return None
        
        # Count co-occurrences within 5-minute windows
        co_occurrences = 0
        total_windows = 0
        
        for time_a in times_a:
            total_windows += 1
            for time_b in times_b:
                if abs((time_a - time_b).total_seconds()) <= 300:  # 5 minutes
                    co_occurrences += 1
                    break
        
        if total_windows == 0:
            return None
        
        strength = co_occurrences / total_windows
        
        return {
            "type": "service_correlation",
            "service_a": service_a,
            "service_b": service_b,
            "strength": round(strength, 3),
            "co_occurrences": co_occurrences,
            "description": f"Errors in {service_a} and {service_b} occur together {strength:.1%} of the time"
        }
    
    def _find_time_correlations(self, events: List[Any]) -> List[Dict[str, Any]]:
        """Find time-based correlations"""
        correlations = []
        
        # Group by hour of day
        hourly_counts = defaultdict(int)
        for event in events:
            timestamp = getattr(event, 'timestamp', datetime.utcnow())
            hour = timestamp.hour
            hourly_counts[hour] += 1
        
        if hourly_counts:
            max_hour = max(hourly_counts, key=hourly_counts.get)
            max_count = hourly_counts[max_hour]
            avg_count = sum(hourly_counts.values()) / len(hourly_counts)
            
            if max_count > avg_count * 2:
                correlations.append({
                    "type": "time_correlation",
                    "pattern": "hourly_peak",
                    "peak_hour": max_hour,
                    "peak_count": max_count,
                    "average_count": round(avg_count, 1),
                    "description": f"Error peak at hour {max_hour}:00 ({max_count} errors vs {avg_count:.1f} average)"
                })
        
        return correlations
    
    def _find_workflow_correlations(self, events: List[Any]) -> List[Dict[str, Any]]:
        """Find workflow stage correlations"""
        correlations = []
        
        # Build workflow transition patterns
        workflow_transitions = defaultdict(int)
        sorted_events = sorted(events, key=lambda e: getattr(e, 'timestamp', datetime.utcnow()))
        
        for i in range(len(sorted_events) - 1):
            current_stage = getattr(sorted_events[i], 'workflow_stage', 'unknown')
            next_stage = getattr(sorted_events[i + 1], 'workflow_stage', 'unknown')
            
            if current_stage != next_stage:
                transition = f"{current_stage} -> {next_stage}"
                workflow_transitions[transition] += 1
        
        # Find common transition patterns
        if workflow_transitions:
            for transition, count in workflow_transitions.items():
                if count >= 3:  # Minimum threshold
                    correlations.append({
                        "type": "workflow_correlation",
                        "transition": transition,
                        "frequency": count,
                        "description": f"Common error transition: {transition} ({count} occurrences)"
                    })
        
        return correlations
    
    def _generate_recommendations(self, patterns: List[ErrorPattern], 
                                trends: List[ErrorTrend],
                                correlations: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = set()
        
        # Recommendations based on patterns
        for pattern in patterns:
            recommendations.update(pattern.recommended_actions)
        
        # Recommendations based on trends
        for trend in trends:
            if trend.direction == "increasing" and trend.significance == "high":
                if trend.trend_type == "service":
                    recommendations.add(f"Urgent: Investigate increasing error rate in affected service")
                else:
                    recommendations.add("Urgent: Address increasing overall error rate")
            elif trend.direction == "decreasing" and trend.significance == "high":
                recommendations.add("Monitor continued error rate improvement")
        
        # Recommendations based on correlations
        for correlation in correlations:
            if correlation["type"] == "service_correlation" and correlation["strength"] > 0.5:
                recommendations.add(
                    f"Investigate dependency between {correlation['service_a']} and {correlation['service_b']}"
                )
            elif correlation["type"] == "time_correlation":
                recommendations.add("Consider load balancing during peak error hours")
        
        return list(recommendations)
    
    def _assess_severity(self, patterns: List[ErrorPattern], 
                        trends: List[ErrorTrend], 
                        events: List[Any]) -> str:
        """Assess overall severity level"""
        severity_score = 0.0
        
        # Factor in pattern severity
        if patterns:
            avg_pattern_severity = sum(p.severity_score for p in patterns) / len(patterns)
            severity_score += avg_pattern_severity * 0.4
        
        # Factor in trend severity
        for trend in trends:
            if trend.direction == "increasing" and trend.significance == "high":
                severity_score += 0.3
            elif trend.direction == "increasing" and trend.significance == "medium":
                severity_score += 0.2
        
        # Factor in total error count
        error_count_score = min(len(events) / 100, 0.3)  # Cap at 0.3
        severity_score += error_count_score
        
        # Convert to severity level
        if severity_score >= 0.8:
            return "critical"
        elif severity_score >= 0.6:
            return "high"
        elif severity_score >= 0.4:
            return "medium"
        elif severity_score >= 0.2:
            return "low"
        else:
            return "minimal"
    
    def _pattern_to_dict(self, pattern: ErrorPattern) -> Dict[str, Any]:
        """Convert ErrorPattern to dictionary"""
        return {
            "pattern_id": pattern.pattern_id,
            "pattern_type": pattern.pattern_type,
            "description": pattern.description,
            "frequency": pattern.frequency,
            "services_affected": pattern.services_affected,
            "workflow_stages_affected": pattern.workflow_stages_affected,
            "first_seen": pattern.first_seen.isoformat(),
            "last_seen": pattern.last_seen.isoformat(),
            "severity_score": pattern.severity_score,
            "recommended_actions": pattern.recommended_actions
        }
    
    def _trend_to_dict(self, trend: ErrorTrend) -> Dict[str, Any]:
        """Convert ErrorTrend to dictionary"""
        return {
            "trend_type": trend.trend_type,
            "direction": trend.direction,
            "change_percentage": trend.change_percentage,
            "time_period": trend.time_period,
            "significance": trend.significance,
            "description": trend.description
        }
    
    def _load_known_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load known error patterns for faster recognition"""
        return {
            "database_connection_timeout": {
                "keywords": ["connection", "timeout", "database"],
                "severity": 0.7,
                "recommendations": [
                    "Check database connection pool settings",
                    "Verify database server health",
                    "Review query performance"
                ]
            },
            "api_rate_limit": {
                "keywords": ["rate", "limit", "429", "throttle"],
                "severity": 0.5,
                "recommendations": [
                    "Implement exponential backoff",
                    "Review API usage patterns",
                    "Consider request batching"
                ]
            },
            "out_of_memory": {
                "keywords": ["memory", "oom", "heap"],
                "severity": 0.9,
                "recommendations": [
                    "Urgent: Increase memory allocation",
                    "Review memory usage patterns",
                    "Implement memory leak detection"
                ]
            }
        }


# Global error analyzer instance
error_analyzer = ErrorAnalyzer()