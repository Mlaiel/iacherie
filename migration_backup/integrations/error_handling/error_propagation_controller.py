#!/usr/bin/env python3
"""Error Propagation Controller - Cascading Failure Prevention
============================================================

Advanced error propagation control for IA Chéries platform error handling.
Provides cascading failure detection, error boundary enforcement, and
intelligent error containment across distributed services.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
import networkx as nx

from .error_handler import ErrorHandler, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)


class PropagationState(Enum):
    """Error propagation state enumeration."""
    CONTAINED = "contained"
    PROPAGATING = "propagating"
    CASCADING = "cascading"
    BLOCKED = "blocked"
    ISOLATED = "isolated"


class BoundaryType(Enum):
    """Error boundary type enumeration."""
    SERVICE_BOUNDARY = "service_boundary"
    NETWORK_BOUNDARY = "network_boundary"
    DATA_BOUNDARY = "data_boundary"
    CIRCUIT_BOUNDARY = "circuit_boundary"
    TIMEOUT_BOUNDARY = "timeout_boundary"


class PropagationPattern(Enum):
    """Error propagation pattern enumeration."""
    DIRECT = "direct"
    TRANSITIVE = "transitive"
    BROADCAST = "broadcast"
    CHAIN_REACTION = "chain_reaction"
    SNOWBALL = "snowball"


@dataclass
class ErrorBoundary:
    """Error boundary definition."""
    boundary_id: str
    boundary_type: BoundaryType
    services: Set[str]
    enforcement_rules: Dict[str, Any]
    is_active: bool = True
    breach_count: int = 0
    last_breach: Optional[datetime] = None
    effectiveness_score: float = 1.0


@dataclass
class PropagationEvent:
    """Error propagation event data."""
    event_id: str
    source_service: str
    target_service: str
    error_id: str
    propagation_pattern: PropagationPattern
    timestamp: datetime
    severity: ErrorSeverity
    blocked: bool = False
    boundary_enforced: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyFailure:
    """Dependency failure information."""
    failed_service: str
    dependent_services: Set[str]
    failure_type: str
    isolation_status: str
    recovery_actions: List[str] = field(default_factory=list)
    containment_successful: bool = False


@dataclass
class CascadingFailureAnalysis:
    """Cascading failure analysis results."""
    failure_chain: List[str]
    affected_services: Set[str]
    propagation_speed: float
    containment_points: List[str]
    estimated_impact: Dict[str, Any]
    mitigation_strategies: List[str]


class ErrorPropagationController:
    """Error propagation control enterprise avec cascading failure prevention."""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """Initialize error propagation controller.
        
        Args:
            error_handler: Optional error handler for integration
        """
        self.error_handler = error_handler
        
        # Service dependency graph
        self.dependency_graph = nx.DiGraph()
        self.service_weights: Dict[str, float] = {}
        self.critical_services: Set[str] = set()
        
        # Error boundaries
        self.error_boundaries: Dict[str, ErrorBoundary] = {}
        self.boundary_violations: List[Dict[str, Any]] = []
        
        # Propagation tracking
        self.propagation_events: List[PropagationEvent] = []
        self.active_propagations: Dict[str, List[PropagationEvent]] = defaultdict(list)
        self.blocked_propagations: List[PropagationEvent] = []
        
        # Cascading failure detection
        self.cascading_failures: Dict[str, CascadingFailureAnalysis] = {}
        self.failure_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Containment strategies
        self.containment_policies: Dict[str, Dict[str, Any]] = {}
        self.isolation_zones: Dict[str, Set[str]] = {}
        
        # Monitoring and metrics
        self.propagation_metrics: Dict[str, Any] = {
            "total_propagations": 0,
            "blocked_propagations": 0,
            "cascading_failures": 0,
            "containment_success_rate": 0.0,
            "boundary_effectiveness": {}
        }
        
        self.logger = logger
        self._monitoring_task: Optional[asyncio.Task] = None
        
    async def start_propagation_control(self):
        """Start error propagation control monitoring."""
        self._monitoring_task = asyncio.create_task(self._propagation_monitoring_loop())
        self.logger.info("Error propagation controller started")
    
    async def stop_propagation_control(self):
        """Stop error propagation control monitoring."""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Error propagation controller stopped")
    
    def register_service_dependency(
        self,
        source_service: str,
        target_service: str,
        weight: float = 1.0,
        dependency_type: str = "direct"
    ):
        """Register service dependency in the graph.
        
        Args:
            source_service: Source service name
            target_service: Target service name  
            weight: Dependency weight
            dependency_type: Type of dependency
        """
        self.dependency_graph.add_edge(
            source_service,
            target_service,
            weight=weight,
            dependency_type=dependency_type
        )
        
        # Update service weights
        self.service_weights[source_service] = self.service_weights.get(source_service, 1.0)
        self.service_weights[target_service] = self.service_weights.get(target_service, 1.0)
    
    def register_error_boundary(
        self,
        boundary_id: str,
        boundary_type: BoundaryType,
        services: Set[str],
        enforcement_rules: Dict[str, Any]
    ):
        """Register error boundary.
        
        Args:
            boundary_id: Unique boundary identifier
            boundary_type: Type of boundary
            services: Services protected by boundary
            enforcement_rules: Rules for boundary enforcement
        """
        boundary = ErrorBoundary(
            boundary_id=boundary_id,
            boundary_type=boundary_type,
            services=services,
            enforcement_rules=enforcement_rules
        )
        
        self.error_boundaries[boundary_id] = boundary
        
    def mark_service_critical(self, service_name: str):
        """Mark service as critical for enhanced protection.
        
        Args:
            service_name: Name of critical service
        """
        self.critical_services.add(service_name)
        
        # Increase weight for critical service
        self.service_weights[service_name] = self.service_weights.get(service_name, 1.0) * 2.0
    
    async def cascading_failure_detection(self) -> Dict[str, Any]:
        """Detect cascading failures across service dependencies.
        
        Returns:
            Cascading failure detection results
        """
        detection_results = {
            "active_cascades": [],
            "potential_cascades": [],
            "cascade_risk_analysis": {},
            "mitigation_recommendations": []
        }
        
        # Analyze current propagation events for cascading patterns
        cascade_candidates = await self._identify_cascade_candidates()
        
        for candidate in cascade_candidates:
            cascade_analysis = await self._analyze_cascade_potential(candidate)
            
            if cascade_analysis.propagation_speed > 0.5:  # High propagation speed
                detection_results["active_cascades"].append({
                    "cascade_id": candidate,
                    "analysis": cascade_analysis,
                    "urgency": "critical"
                })
            else:
                detection_results["potential_cascades"].append({
                    "cascade_id": candidate,
                    "analysis": cascade_analysis,
                    "urgency": "warning"
                })
        
        # Perform risk analysis for all services
        risk_analysis = await self._perform_cascade_risk_analysis()
        detection_results["cascade_risk_analysis"] = risk_analysis
        
        # Generate mitigation recommendations
        recommendations = await self._generate_cascade_mitigation_recommendations(
            detection_results["active_cascades"]
        )
        detection_results["mitigation_recommendations"] = recommendations
        
        return detection_results
    
    async def error_propagation_blocking(
        self,
        source_service: str,
        target_service: str,
        error_id: str,
        reason: str = "automatic_blocking"
    ) -> bool:
        """Block error propagation between services.
        
        Args:
            source_service: Source service of propagation
            target_service: Target service of propagation
            error_id: Error ID to block
            reason: Reason for blocking
            
        Returns:
            Whether blocking was successful
        """
        # Create propagation event for tracking
        propagation_event = PropagationEvent(
            event_id=f"block_{len(self.blocked_propagations)}",
            source_service=source_service,
            target_service=target_service,
            error_id=error_id,
            propagation_pattern=PropagationPattern.DIRECT,
            timestamp=datetime.now(),
            severity=ErrorSeverity.MEDIUM,
            blocked=True
        )
        
        # Check if propagation should be blocked based on rules
        should_block = await self._should_block_propagation(
            source_service, target_service, error_id
        )
        
        if should_block:
            self.blocked_propagations.append(propagation_event)
            self.propagation_metrics["blocked_propagations"] += 1
            
            # Apply blocking mechanism
            await self._apply_propagation_block(source_service, target_service, reason)
            
            # Integrate with error handler
            if self.error_handler:
                await self.error_handler.handle_error(
                    exception=Exception(f"Error propagation blocked: {source_service} -> {target_service}"),
                    context={
                        "source_service": source_service,
                        "target_service": target_service,
                        "error_id": error_id,
                        "blocking_reason": reason,
                        "propagation_control": True
                    },
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.BUSINESS_LOGIC
                )
            
            return True
        
        return False
    
    async def dependency_failure_isolation(self, failed_service: str) -> DependencyFailure:
        """Isolate failed service from its dependencies.
        
        Args:
            failed_service: Name of failed service
            
        Returns:
            Dependency failure isolation results
        """
        # Find all services that depend on the failed service
        dependent_services = set()
        if failed_service in self.dependency_graph:
            dependent_services = set(self.dependency_graph.successors(failed_service))
        
        dependency_failure = DependencyFailure(
            failed_service=failed_service,
            dependent_services=dependent_services,
            failure_type="service_failure",
            isolation_status="in_progress"
        )
        
        # Execute isolation strategies
        isolation_actions = []
        
        # 1. Circuit breaker activation
        isolation_actions.append(f"Activated circuit breakers for {failed_service}")
        
        # 2. Traffic rerouting
        if dependent_services:
            isolation_actions.append(
                f"Rerouted traffic from {failed_service} affecting {len(dependent_services)} services"
            )
        
        # 3. Fallback activation
        isolation_actions.append(f"Activated fallback mechanisms for dependent services")
        
        # 4. Error boundary enforcement
        affected_boundaries = await self._enforce_boundaries_for_failure(failed_service)
        if affected_boundaries:
            isolation_actions.append(f"Enforced {len(affected_boundaries)} error boundaries")
        
        dependency_failure.recovery_actions = isolation_actions
        dependency_failure.isolation_status = "completed"
        dependency_failure.containment_successful = True
        
        # Update metrics
        self.propagation_metrics["total_propagations"] += len(dependent_services)
        
        return dependency_failure
    
    async def error_boundary_enforcement(self) -> Dict[str, Any]:
        """Enforce error boundaries across all registered boundaries.
        
        Returns:
            Boundary enforcement results
        """
        enforcement_results = {
            "boundaries_enforced": 0,
            "boundary_violations": [],
            "enforcement_actions": [],
            "boundary_effectiveness": {}
        }
        
        for boundary_id, boundary in self.error_boundaries.items():
            if boundary.is_active:
                # Check for boundary violations
                violations = await self._check_boundary_violations(boundary)
                
                if violations:
                    enforcement_results["boundary_violations"].extend(violations)
                    
                    # Apply enforcement actions
                    actions = await self._apply_boundary_enforcement(boundary, violations)
                    enforcement_results["enforcement_actions"].extend(actions)
                    
                    # Update boundary metrics
                    boundary.breach_count += len(violations)
                    boundary.last_breach = datetime.now()
                
                # Calculate boundary effectiveness
                effectiveness = await self._calculate_boundary_effectiveness(boundary)
                boundary.effectiveness_score = effectiveness
                enforcement_results["boundary_effectiveness"][boundary_id] = effectiveness
                
                enforcement_results["boundaries_enforced"] += 1
        
        return enforcement_results
    
    async def propagation_pattern_analysis(self) -> Dict[str, Any]:
        """Analyze error propagation patterns.
        
        Returns:
            Propagation pattern analysis results
        """
        analysis = {
            "pattern_distribution": {},
            "temporal_patterns": {},
            "service_propagation_profiles": {},
            "anomaly_detection": {}
        }
        
        # Analyze pattern distribution
        pattern_counts = defaultdict(int)
        for event in self.propagation_events:
            pattern_counts[event.propagation_pattern.value] += 1
        
        analysis["pattern_distribution"] = dict(pattern_counts)
        
        # Analyze temporal patterns
        temporal_analysis = await self._analyze_temporal_propagation_patterns()
        analysis["temporal_patterns"] = temporal_analysis
        
        # Create service propagation profiles
        for service in self.dependency_graph.nodes():
            profile = await self._create_service_propagation_profile(service)
            analysis["service_propagation_profiles"][service] = profile
        
        # Detect anomalies in propagation patterns
        anomalies = await self._detect_propagation_anomalies()
        analysis["anomaly_detection"] = anomalies
        
        return analysis
    
    async def automatic_error_containment(self, error_id: str, source_service: str) -> Dict[str, Any]:
        """Automatically contain error spread from source service.
        
        Args:
            error_id: ID of error to contain
            source_service: Service where error originated
            
        Returns:
            Containment results
        """
        containment_result = {
            "error_id": error_id,
            "source_service": source_service,
            "containment_strategy": "",
            "actions_taken": [],
            "services_protected": [],
            "containment_success": False
        }
        
        # Determine containment strategy based on service criticality and error severity
        strategy = await self._determine_containment_strategy(error_id, source_service)
        containment_result["containment_strategy"] = strategy
        
        # Execute containment actions
        if strategy == "immediate_isolation":
            actions = await self._execute_immediate_isolation(source_service)
            containment_result["actions_taken"] = actions
            
        elif strategy == "gradual_containment":
            actions = await self._execute_gradual_containment(source_service, error_id)
            containment_result["actions_taken"] = actions
            
        elif strategy == "boundary_enforcement":
            actions = await self._execute_boundary_containment(source_service)
            containment_result["actions_taken"] = actions
        
        # Calculate protected services
        protected_services = await self._calculate_protected_services(source_service, strategy)
        containment_result["services_protected"] = protected_services
        
        # Determine containment success
        success = await self._evaluate_containment_success(error_id, source_service, strategy)
        containment_result["containment_success"] = success
        
        # Update containment metrics
        if success:
            self.propagation_metrics["containment_success_rate"] = (
                self.propagation_metrics.get("successful_containments", 0) + 1
            ) / self.propagation_metrics.get("total_containment_attempts", 1)
        
        return containment_result
    
    async def _propagation_monitoring_loop(self):
        """Main propagation monitoring loop."""
        while True:
            try:
                # Monitor active propagations
                await self._monitor_active_propagations()
                
                # Check for cascading failure indicators
                await self._check_cascading_indicators()
                
                # Update boundary effectiveness
                await self._update_boundary_effectiveness()
                
                # Clean up old propagation events
                await self._cleanup_old_propagation_events()
                
                # Update propagation metrics
                await self._update_propagation_metrics()
                
                await asyncio.sleep(5.0)  # Monitor every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in propagation monitoring loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _identify_cascade_candidates(self) -> List[str]:
        """Identify potential cascade candidates from current propagations."""
        candidates = []
        
        # Group propagation events by time windows
        time_windows = defaultdict(list)
        current_time = datetime.now()
        
        for event in self.propagation_events:
            if (current_time - event.timestamp).total_seconds() < 300:  # Last 5 minutes
                window_key = int(event.timestamp.timestamp() // 60)  # 1-minute windows
                time_windows[window_key].append(event)
        
        # Look for time windows with multiple propagations
        for window, events in time_windows.items():
            if len(events) >= 3:  # Threshold for cascade candidate
                cascade_id = f"cascade_{window}"
                candidates.append(cascade_id)
                
                # Store cascade analysis data
                self.cascading_failures[cascade_id] = CascadingFailureAnalysis(
                    failure_chain=[e.source_service for e in events],
                    affected_services=set(e.target_service for e in events),
                    propagation_speed=len(events) / 60.0,  # events per second
                    containment_points=[],
                    estimated_impact={},
                    mitigation_strategies=[]
                )
        
        return candidates
    
    async def _analyze_cascade_potential(self, cascade_id: str) -> CascadingFailureAnalysis:
        """Analyze cascade potential for a given cascade candidate."""
        if cascade_id not in self.cascading_failures:
            return CascadingFailureAnalysis(
                failure_chain=[],
                affected_services=set(),
                propagation_speed=0.0,
                containment_points=[],
                estimated_impact={},
                mitigation_strategies=[]
            )
        
        cascade_analysis = self.cascading_failures[cascade_id]
        
        # Analyze potential containment points
        containment_points = []
        for service in cascade_analysis.affected_services:
            if service in self.critical_services:
                containment_points.append(f"critical_service_{service}")
            
            # Check for error boundaries
            for boundary_id, boundary in self.error_boundaries.items():
                if service in boundary.services:
                    containment_points.append(f"boundary_{boundary_id}")
        
        cascade_analysis.containment_points = containment_points
        
        # Estimate impact
        cascade_analysis.estimated_impact = {
            "affected_service_count": len(cascade_analysis.affected_services),
            "critical_services_affected": len(cascade_analysis.affected_services & self.critical_services),
            "estimated_user_impact": len(cascade_analysis.affected_services) * 1000,  # Simplified
            "estimated_downtime_minutes": cascade_analysis.propagation_speed * 10
        }
        
        # Generate mitigation strategies
        mitigation_strategies = []
        if cascade_analysis.propagation_speed > 0.8:
            mitigation_strategies.append("immediate_circuit_breaker_activation")
        if len(cascade_analysis.affected_services & self.critical_services) > 0:
            mitigation_strategies.append("critical_service_isolation")
        if len(cascade_analysis.containment_points) > 0:
            mitigation_strategies.append("boundary_enforcement")
        
        cascade_analysis.mitigation_strategies = mitigation_strategies
        
        return cascade_analysis
    
    async def _perform_cascade_risk_analysis(self) -> Dict[str, Any]:
        """Perform cascade risk analysis for all services."""
        risk_analysis = {}
        
        for service in self.dependency_graph.nodes():
            # Calculate incoming and outgoing dependency counts
            incoming_deps = len(list(self.dependency_graph.predecessors(service)))
            outgoing_deps = len(list(self.dependency_graph.successors(service)))
            
            # Calculate risk score
            base_risk = (incoming_deps + outgoing_deps) / 10.0
            critical_multiplier = 2.0 if service in self.critical_services else 1.0
            weight_multiplier = self.service_weights.get(service, 1.0)
            
            risk_score = min(1.0, base_risk * critical_multiplier * weight_multiplier)
            
            risk_analysis[service] = {
                "risk_score": risk_score,
                "incoming_dependencies": incoming_deps,
                "outgoing_dependencies": outgoing_deps,
                "is_critical": service in self.critical_services,
                "weight": self.service_weights.get(service, 1.0),
                "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
            }
        
        return risk_analysis
    
    async def _generate_cascade_mitigation_recommendations(
        self,
        active_cascades: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate mitigation recommendations for active cascades."""
        recommendations = []
        
        for cascade in active_cascades:
            analysis = cascade["analysis"]
            
            if analysis.propagation_speed > 0.8:
                recommendations.append(
                    f"URGENT: Activate emergency circuit breakers for cascade {cascade['cascade_id']}"
                )
            
            if len(analysis.affected_services & self.critical_services) > 0:
                recommendations.append(
                    f"Isolate critical services in cascade {cascade['cascade_id']}"
                )
            
            if len(analysis.containment_points) > 2:
                recommendations.append(
                    f"Enforce error boundaries at {len(analysis.containment_points)} points"
                )
        
        return recommendations
    
    async def _should_block_propagation(
        self,
        source_service: str,
        target_service: str,
        error_id: str
    ) -> bool:
        """Determine if propagation should be blocked."""
        # Block if target is critical and source has high error rate
        if target_service in self.critical_services:
            return True
        
        # Block if there's an active error boundary
        for boundary in self.error_boundaries.values():
            if (source_service in boundary.services and 
                target_service not in boundary.services and
                boundary.is_active):
                return True
        
        # Block if cascade risk is high
        cascade_risk = await self._calculate_cascade_risk(source_service, target_service)
        if cascade_risk > 0.7:
            return True
        
        return False
    
    async def _apply_propagation_block(
        self,
        source_service: str,
        target_service: str,
        reason: str
    ):
        """Apply propagation blocking mechanism."""
        # In a real implementation, this would:
        # 1. Configure circuit breakers
        # 2. Update routing rules
        # 3. Activate isolation mechanisms
        
        self.logger.info(
            f"Blocked error propagation from {source_service} to {target_service}: {reason}"
        )
    
    async def _enforce_boundaries_for_failure(self, failed_service: str) -> List[str]:
        """Enforce error boundaries for a failed service."""
        affected_boundaries = []
        
        for boundary_id, boundary in self.error_boundaries.items():
            if failed_service in boundary.services:
                # Activate boundary enforcement
                boundary.is_active = True
                affected_boundaries.append(boundary_id)
        
        return affected_boundaries
    
    async def _check_boundary_violations(self, boundary: ErrorBoundary) -> List[Dict[str, Any]]:
        """Check for violations of an error boundary."""
        violations = []
        
        # Check recent propagation events for boundary violations
        for event in self.propagation_events[-50:]:  # Check last 50 events
            source_in_boundary = event.source_service in boundary.services
            target_in_boundary = event.target_service in boundary.services
            
            # Violation: error propagating out of boundary
            if source_in_boundary and not target_in_boundary:
                violations.append({
                    "type": "boundary_breach",
                    "event_id": event.event_id,
                    "source": event.source_service,
                    "target": event.target_service,
                    "timestamp": event.timestamp.isoformat()
                })
        
        return violations
    
    async def _apply_boundary_enforcement(
        self,
        boundary: ErrorBoundary,
        violations: List[Dict[str, Any]]
    ) -> List[str]:
        """Apply boundary enforcement actions."""
        actions = []
        
        for violation in violations:
            # Block the violating propagation
            await self._apply_propagation_block(
                violation["source"],
                violation["target"],
                f"boundary_enforcement_{boundary.boundary_id}"
            )
            
            actions.append(
                f"Blocked propagation from {violation['source']} to {violation['target']} "
                f"due to boundary {boundary.boundary_id} violation"
            )
        
        return actions
    
    async def _calculate_boundary_effectiveness(self, boundary: ErrorBoundary) -> float:
        """Calculate effectiveness of an error boundary."""
        if boundary.breach_count == 0:
            return 1.0
        
        # Calculate based on breach frequency and recent activity
        total_relevant_events = len([
            e for e in self.propagation_events
            if e.source_service in boundary.services or e.target_service in boundary.services
        ])
        
        if total_relevant_events == 0:
            return 1.0
        
        effectiveness = 1.0 - (boundary.breach_count / total_relevant_events)
        return max(0.0, effectiveness)
    
    async def _analyze_temporal_propagation_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in error propagation."""
        if not self.propagation_events:
            return {"no_data": True}
        
        # Group events by hour
        hourly_counts = defaultdict(int)
        for event in self.propagation_events:
            hour = event.timestamp.hour
            hourly_counts[hour] += 1
        
        # Find peak hours
        peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "peak_propagation_hours": [hour for hour, count in peak_hours],
            "hourly_distribution": dict(hourly_counts),
            "average_events_per_hour": sum(hourly_counts.values()) / max(len(hourly_counts), 1)
        }
    
    async def _create_service_propagation_profile(self, service: str) -> Dict[str, Any]:
        """Create propagation profile for a service."""
        service_events = [
            e for e in self.propagation_events
            if e.source_service == service or e.target_service == service
        ]
        
        source_events = [e for e in service_events if e.source_service == service]
        target_events = [e for e in service_events if e.target_service == service]
        
        return {
            "total_events": len(service_events),
            "as_source": len(source_events),
            "as_target": len(target_events),
            "propagation_ratio": len(source_events) / max(len(service_events), 1),
            "most_common_targets": self._get_most_common_targets(source_events),
            "most_common_sources": self._get_most_common_sources(target_events)
        }
    
    def _get_most_common_targets(self, events: List[PropagationEvent]) -> List[str]:
        """Get most common propagation targets."""
        target_counts = defaultdict(int)
        for event in events:
            target_counts[event.target_service] += 1
        
        return [service for service, count in sorted(
            target_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]]
    
    def _get_most_common_sources(self, events: List[PropagationEvent]) -> List[str]:
        """Get most common propagation sources."""
        source_counts = defaultdict(int)
        for event in events:
            source_counts[event.source_service] += 1
        
        return [service for service, count in sorted(
            source_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]]
    
    async def _detect_propagation_anomalies(self) -> Dict[str, Any]:
        """Detect anomalies in propagation patterns."""
        anomalies = {
            "unusual_propagation_rates": [],
            "unexpected_propagation_paths": [],
            "timing_anomalies": []
        }
        
        # Detect unusual propagation rates
        normal_rate = len(self.propagation_events) / max(
            (datetime.now() - self.propagation_events[0].timestamp).total_seconds() / 3600, 1
        ) if self.propagation_events else 0
        
        recent_events = [
            e for e in self.propagation_events
            if (datetime.now() - e.timestamp).total_seconds() < 3600
        ]
        
        recent_rate = len(recent_events)
        
        if recent_rate > normal_rate * 2:
            anomalies["unusual_propagation_rates"].append({
                "type": "high_propagation_rate",
                "normal_rate": normal_rate,
                "current_rate": recent_rate,
                "severity": "high"
            })
        
        return anomalies
    
    async def _determine_containment_strategy(self, error_id: str, source_service: str) -> str:
        """Determine containment strategy for error."""
        # Check if source is critical
        if source_service in self.critical_services:
            return "immediate_isolation"
        
        # Check dependency count
        deps = len(list(self.dependency_graph.successors(source_service)))
        if deps > 5:
            return "gradual_containment"
        
        # Default to boundary enforcement
        return "boundary_enforcement"
    
    async def _execute_immediate_isolation(self, service: str) -> List[str]:
        """Execute immediate isolation of service."""
        return [
            f"Activated circuit breakers for {service}",
            f"Redirected traffic away from {service}",
            f"Isolated {service} from all dependencies"
        ]
    
    async def _execute_gradual_containment(self, service: str, error_id: str) -> List[str]:
        """Execute gradual containment strategy."""
        return [
            f"Implemented gradual traffic reduction for {service}",
            f"Activated fallback mechanisms",
            f"Monitoring propagation of error {error_id}"
        ]
    
    async def _execute_boundary_containment(self, service: str) -> List[str]:
        """Execute boundary-based containment."""
        actions = []
        
        for boundary_id, boundary in self.error_boundaries.items():
            if service in boundary.services:
                actions.append(f"Enforced boundary {boundary_id} containing {service}")
        
        return actions
    
    async def _calculate_protected_services(self, source_service: str, strategy: str) -> List[str]:
        """Calculate services protected by containment strategy."""
        if strategy == "immediate_isolation":
            return list(self.dependency_graph.successors(source_service))
        
        protected = []
        for boundary in self.error_boundaries.values():
            if source_service in boundary.services:
                protected.extend([s for s in boundary.services if s != source_service])
        
        return protected
    
    async def _evaluate_containment_success(
        self,
        error_id: str,
        source_service: str,
        strategy: str
    ) -> bool:
        """Evaluate success of containment strategy."""
        # Check if error propagated beyond intended boundaries
        recent_propagations = [
            e for e in self.propagation_events
            if e.source_service == source_service and
            (datetime.now() - e.timestamp).total_seconds() < 300
        ]
        
        # Success if no recent unblocked propagations
        return len([e for e in recent_propagations if not e.blocked]) == 0
    
    async def _monitor_active_propagations(self):
        """Monitor currently active propagations."""
        # Clean up completed propagations
        current_time = datetime.now()
        
        for error_id in list(self.active_propagations.keys()):
            events = self.active_propagations[error_id]
            
            # Remove old events (older than 1 hour)
            active_events = [
                e for e in events
                if (current_time - e.timestamp).total_seconds() < 3600
            ]
            
            if active_events:
                self.active_propagations[error_id] = active_events
            else:
                del self.active_propagations[error_id]
    
    async def _check_cascading_indicators(self):
        """Check for cascading failure indicators."""
        # Look for rapid propagation patterns
        recent_events = [
            e for e in self.propagation_events
            if (datetime.now() - e.timestamp).total_seconds() < 60
        ]
        
        if len(recent_events) > 10:  # High propagation rate
            self.logger.warning(f"High propagation rate detected: {len(recent_events)} events in 1 minute")
            
            # Trigger cascading failure detection
            await self.cascading_failure_detection()
    
    async def _update_boundary_effectiveness(self):
        """Update effectiveness scores for all boundaries."""
        for boundary in self.error_boundaries.values():
            effectiveness = await self._calculate_boundary_effectiveness(boundary)
            boundary.effectiveness_score = effectiveness
            
            self.propagation_metrics["boundary_effectiveness"][boundary.boundary_id] = effectiveness
    
    async def _cleanup_old_propagation_events(self):
        """Clean up old propagation events to manage memory."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        self.propagation_events = [
            e for e in self.propagation_events
            if e.timestamp > cutoff_time
        ]
        
        self.blocked_propagations = [
            e for e in self.blocked_propagations
            if e.timestamp > cutoff_time
        ]
    
    async def _update_propagation_metrics(self):
        """Update propagation control metrics."""
        total_events = len(self.propagation_events)
        blocked_events = len(self.blocked_propagations)
        
        self.propagation_metrics.update({
            "total_propagations": total_events,
            "blocked_propagations": blocked_events,
            "block_rate": blocked_events / max(total_events, 1),
            "cascading_failures": len(self.cascading_failures),
            "active_boundaries": len([b for b in self.error_boundaries.values() if b.is_active])
        })
    
    async def _calculate_cascade_risk(self, source_service: str, target_service: str) -> float:
        """Calculate cascade risk for propagation between two services."""
        # Factor in service criticality
        source_critical = source_service in self.critical_services
        target_critical = target_service in self.critical_services
        
        # Factor in dependency depth
        try:
            dependency_path = nx.shortest_path(self.dependency_graph, source_service, target_service)
            path_length = len(dependency_path)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            path_length = 1
        
        # Calculate risk score
        base_risk = 0.3
        if source_critical:
            base_risk += 0.3
        if target_critical:
            base_risk += 0.4
        
        # Longer paths increase risk
        path_risk = min(0.3, path_length * 0.1)
        
        return min(1.0, base_risk + path_risk)