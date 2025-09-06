"""Event Correlation Analyzer - Cross-Services for Ainflue Events

Advanced event correlation analyzer for identifying patterns, dependencies,
and business relationships across Ainflue services and workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class CorrelationType(Enum):
    """Types of event correlations"""
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    WORKFLOW = "workflow"
    USER_JOURNEY = "user_journey"
    BUSINESS_PROCESS = "business_process"
    ANOMALY = "anomaly"


@dataclass
class CorrelationRule:
    """Rule for event correlation"""
    name: str
    event_patterns: List[str]
    time_window_seconds: int
    correlation_type: CorrelationType
    business_impact: str
    confidence_threshold: float = 0.7
    enabled: bool = True


@dataclass
class EventCorrelation:
    """Correlation between events"""
    correlation_id: str
    correlation_type: CorrelationType
    correlated_events: List[Dict[str, Any]]
    confidence_score: float
    business_significance: str
    pattern_description: str
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    
    
@dataclass
class CorrelationInsight:
    """Business insight from correlation analysis"""
    insight_type: str
    description: str
    affected_services: List[str]
    business_impact: str
    recommended_actions: List[str]
    confidence_level: float


class EventCorrelationAnalyzer:
    """
    Advanced event correlation analyzer for Ainflue cross-services
    Identifies patterns, dependencies, and business relationships in event streams
    """
    
    def __init__(self, correlation_window_hours: int = 24):
        self.correlation_window_hours = correlation_window_hours
        self.event_buffer: deque = deque(maxlen=10000)
        self.correlation_rules = self._initialize_correlation_rules()
        self.discovered_correlations: List[EventCorrelation] = []
        self.correlation_patterns: Dict[str, int] = defaultdict(int)
        
        logger.info(f"EventCorrelationAnalyzer initialized with {correlation_window_hours}h window")
    
    def _initialize_correlation_rules(self) -> List[CorrelationRule]:
        """Initialize Ainflue-specific correlation rules"""
        
        return [
            CorrelationRule(
                name="content_upload_processing_workflow",
                event_patterns=["content.upload.completed", "content.processing.started", "content.processing.completed"],
                time_window_seconds=3600,
                correlation_type=CorrelationType.WORKFLOW,
                business_impact="Content processing pipeline efficiency"
            ),
            CorrelationRule(
                name="collaboration_matching_sequence",
                event_patterns=["collaboration.requested", "collaboration.matched", "collaboration.accepted"],
                time_window_seconds=7200,
                correlation_type=CorrelationType.USER_JOURNEY,
                business_impact="Collaboration success rate optimization"
            ),
            CorrelationRule(
                name="monetization_revenue_flow",
                event_patterns=["content.published", "revenue.generated", "payment.processed"],
                time_window_seconds=86400,
                correlation_type=CorrelationType.BUSINESS_PROCESS,
                business_impact="Revenue attribution and optimization"
            ),
            CorrelationRule(
                name="user_engagement_pattern",
                event_patterns=["user.login", "content.viewed", "content.liked", "collaboration.initiated"],
                time_window_seconds=1800,
                correlation_type=CorrelationType.USER_JOURNEY,
                business_impact="User engagement optimization"
            ),
            CorrelationRule(
                name="ai_processing_performance",
                event_patterns=["ai.processing.started", "ai.processing.completed", "content.quality.scored"],
                time_window_seconds=1800,
                correlation_type=CorrelationType.TEMPORAL,
                business_impact="AI processing efficiency monitoring"
            )
        ]
    
    async def analyze_event_correlations(self, new_event: Dict[str, Any]) -> List[EventCorrelation]:
        """Analyze correlations for a new event"""
        
        # Add event to buffer
        enriched_event = self._enrich_event_for_correlation(new_event)
        self.event_buffer.append(enriched_event)
        
        # Find correlations
        correlations = []
        
        # Apply correlation rules
        for rule in self.correlation_rules:
            if not rule.enabled:
                continue
                
            rule_correlations = await self._apply_correlation_rule(enriched_event, rule)
            correlations.extend(rule_correlations)
        
        # Detect anomaly correlations
        anomaly_correlations = await self._detect_anomaly_correlations(enriched_event)
        correlations.extend(anomaly_correlations)
        
        # Store discovered correlations
        self.discovered_correlations.extend(correlations)
        
        # Update pattern statistics
        for correlation in correlations:
            pattern_key = f"{correlation.correlation_type.value}_{len(correlation.correlated_events)}"
            self.correlation_patterns[pattern_key] += 1
        
        return correlations
    
    def _enrich_event_for_correlation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich event with correlation metadata"""
        
        enriched = event.copy()
        
        # Add correlation metadata
        enriched["correlation_metadata"] = {
            "received_at": datetime.utcnow(),
            "event_category": self._categorize_event(event.get("event_type", "")),
            "user_context": self._extract_user_context(event),
            "business_context": self._extract_business_context(event),
            "temporal_markers": self._extract_temporal_markers(event)
        }
        
        return enriched
    
    def _categorize_event(self, event_type: str) -> str:
        """Categorize event for correlation analysis"""
        
        if event_type.startswith("content."):
            return "content_lifecycle"
        elif event_type.startswith("collaboration."):
            return "collaboration"
        elif event_type.startswith("monetization.") or event_type.startswith("revenue.") or event_type.startswith("payment."):
            return "monetization"
        elif event_type.startswith("user."):
            return "user_activity"
        elif event_type.startswith("ai."):
            return "ai_processing"
        elif event_type.startswith("analytics."):
            return "analytics"
        else:
            return "general"
    
    def _extract_user_context(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user context for correlation"""
        
        return {
            "user_id": event.get("user_id"),
            "user_tier": event.get("payload", {}).get("user_tier", "unknown"),
            "session_id": event.get("payload", {}).get("session_id"),
            "device_type": event.get("payload", {}).get("device_type", "unknown")
        }
    
    def _extract_business_context(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business context for correlation"""
        
        business_metadata = event.get("business_metadata", {})
        payload = event.get("payload", {})
        
        return {
            "business_value": business_metadata.get("business_value", 0),
            "workflow_stage": business_metadata.get("workflow_stage", "unknown"),
            "priority": business_metadata.get("priority", "normal"),
            "content_type": payload.get("content_type"),
            "collaboration_type": payload.get("collaboration_type"),
            "transaction_amount": payload.get("amount", 0)
        }
    
    def _extract_temporal_markers(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal markers for time-based correlation"""
        
        timestamp = event.get("timestamp")
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                dt = datetime.utcnow()
        else:
            dt = datetime.utcnow()
        
        return {
            "hour_of_day": dt.hour,
            "day_of_week": dt.weekday(),
            "is_weekend": dt.weekday() >= 5,
            "is_business_hours": 9 <= dt.hour <= 17,
            "quarter_hour": dt.minute // 15
        }
    
    async def _apply_correlation_rule(self, new_event: Dict[str, Any], rule: CorrelationRule) -> List[EventCorrelation]:
        """Apply a specific correlation rule"""
        
        correlations = []
        
        # Find events matching the pattern within time window
        window_start = datetime.utcnow() - timedelta(seconds=rule.time_window_seconds)
        
        relevant_events = [
            event for event in self.event_buffer
            if (event["correlation_metadata"]["received_at"] >= window_start and
                self._event_matches_pattern(event, rule.event_patterns))
        ]
        
        # Add current event if it matches
        if self._event_matches_pattern(new_event, rule.event_patterns):
            relevant_events.append(new_event)
        
        # Look for complete patterns
        pattern_sequences = self._find_pattern_sequences(relevant_events, rule.event_patterns)
        
        for sequence in pattern_sequences:
            confidence = self._calculate_correlation_confidence(sequence, rule)
            
            if confidence >= rule.confidence_threshold:
                correlation = EventCorrelation(
                    correlation_id=f"corr_{rule.name}_{int(time.time() * 1000)}",
                    correlation_type=rule.correlation_type,
                    correlated_events=sequence,
                    confidence_score=confidence,
                    business_significance=rule.business_impact,
                    pattern_description=f"Pattern: {' -> '.join(rule.event_patterns)}"
                )
                correlations.append(correlation)
        
        return correlations
    
    def _event_matches_pattern(self, event: Dict[str, Any], patterns: List[str]) -> bool:
        """Check if event matches any pattern"""
        
        event_type = event.get("event_type", "")
        
        for pattern in patterns:
            if pattern in event_type or event_type.startswith(pattern):
                return True
        
        return False
    
    def _find_pattern_sequences(self, events: List[Dict[str, Any]], patterns: List[str]) -> List[List[Dict[str, Any]]]:
        """Find sequences of events matching the pattern order"""
        
        sequences = []
        
        # Group events by pattern
        events_by_pattern = defaultdict(list)
        for event in events:
            event_type = event.get("event_type", "")
            for pattern in patterns:
                if pattern in event_type:
                    events_by_pattern[pattern].append(event)
                    break
        
        # Find sequences where events follow the pattern order
        if len(events_by_pattern) >= 2:
            # Simple case: look for any sequence that has events from multiple patterns
            pattern_events = []
            for pattern in patterns:
                if pattern in events_by_pattern:
                    pattern_events.extend(events_by_pattern[pattern])
            
            if len(pattern_events) >= 2:
                # Sort by timestamp and group related events
                pattern_events.sort(key=lambda e: e["correlation_metadata"]["received_at"])
                
                # Look for sequences by user or correlation ID
                user_sequences = defaultdict(list)
                for event in pattern_events:
                    user_id = event.get("user_id") or event.get("correlation_id")
                    if user_id:
                        user_sequences[user_id].append(event)
                
                # Return sequences with multiple events
                for user_id, user_events in user_sequences.items():
                    if len(user_events) >= 2:
                        sequences.append(user_events)
        
        return sequences
    
    def _calculate_correlation_confidence(self, sequence: List[Dict[str, Any]], rule: CorrelationRule) -> float:
        """Calculate confidence score for correlation"""
        
        base_confidence = 0.5
        
        # Time proximity increases confidence
        if len(sequence) >= 2:
            time_span = (sequence[-1]["correlation_metadata"]["received_at"] - 
                        sequence[0]["correlation_metadata"]["received_at"]).total_seconds()
            
            time_score = max(0, 1 - (time_span / rule.time_window_seconds))
            base_confidence += time_score * 0.3
        
        # Pattern completeness increases confidence
        unique_patterns = set()
        for event in sequence:
            event_type = event.get("event_type", "")
            for pattern in rule.event_patterns:
                if pattern in event_type:
                    unique_patterns.add(pattern)
        
        pattern_completeness = len(unique_patterns) / len(rule.event_patterns)
        base_confidence += pattern_completeness * 0.3
        
        # Business context alignment increases confidence
        if rule.correlation_type == CorrelationType.USER_JOURNEY:
            # Same user increases confidence
            user_ids = [e.get("user_id") for e in sequence if e.get("user_id")]
            if len(set(user_ids)) == 1:
                base_confidence += 0.2
        
        return min(1.0, base_confidence)
    
    async def _detect_anomaly_correlations(self, new_event: Dict[str, Any]) -> List[EventCorrelation]:
        """Detect anomalous correlations"""
        
        correlations = []
        
        # Detect unusual time patterns
        event_category = new_event["correlation_metadata"]["event_category"]
        temporal_markers = new_event["correlation_metadata"]["temporal_markers"]
        
        # Check for unusual timing
        if temporal_markers["is_weekend"] and event_category == "monetization":
            # Unusual monetization activity on weekends
            anomaly = EventCorrelation(
                correlation_id=f"anomaly_weekend_monetization_{int(time.time())}",
                correlation_type=CorrelationType.ANOMALY,
                correlated_events=[new_event],
                confidence_score=0.8,
                business_significance="Unusual weekend monetization activity",
                pattern_description="Monetization event detected during weekend"
            )
            correlations.append(anomaly)
        
        elif not temporal_markers["is_business_hours"] and event_category == "collaboration":
            # Unusual collaboration activity outside business hours
            anomaly = EventCorrelation(
                correlation_id=f"anomaly_offhours_collaboration_{int(time.time())}",
                correlation_type=CorrelationType.ANOMALY,
                correlated_events=[new_event],
                confidence_score=0.7,
                business_significance="Off-hours collaboration activity",
                pattern_description="Collaboration event detected outside business hours"
            )
            correlations.append(anomaly)
        
        return correlations
    
    async def generate_correlation_insights(self, time_window_hours: int = 24) -> List[CorrelationInsight]:
        """Generate business insights from correlation analysis"""
        
        insights = []
        
        # Analyze recent correlations
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        recent_correlations = [
            c for c in self.discovered_correlations 
            if c.discovered_at >= cutoff_time
        ]
        
        # Workflow efficiency insights
        workflow_correlations = [c for c in recent_correlations if c.correlation_type == CorrelationType.WORKFLOW]
        
        if workflow_correlations:
            avg_confidence = sum(c.confidence_score for c in workflow_correlations) / len(workflow_correlations)
            
            if avg_confidence < 0.7:
                insights.append(CorrelationInsight(
                    insight_type="workflow_efficiency",
                    description=f"Workflow correlations show lower than expected confidence ({avg_confidence:.2f})",
                    affected_services=["content", "processing", "ai"],
                    business_impact="Potential workflow inefficiencies affecting user experience",
                    recommended_actions=[
                        "Review workflow timeouts and error handling",
                        "Optimize processing pipeline steps",
                        "Monitor for system bottlenecks"
                    ],
                    confidence_level=0.8
                ))
        
        # User journey insights
        user_journey_correlations = [c for c in recent_correlations if c.correlation_type == CorrelationType.USER_JOURNEY]
        
        if user_journey_correlations:
            # Analyze user engagement patterns
            successful_journeys = [c for c in user_journey_correlations if c.confidence_score > 0.8]
            success_rate = len(successful_journeys) / len(user_journey_correlations)
            
            if success_rate < 0.6:
                insights.append(CorrelationInsight(
                    insight_type="user_engagement",
                    description=f"User journey success rate is {success_rate:.2f}, below optimal threshold",
                    affected_services=["collaboration", "content", "user"],
                    business_impact="Lower user engagement may impact platform growth",
                    recommended_actions=[
                        "Improve collaboration matching algorithms",
                        "Optimize user onboarding experience",
                        "Enhance content discovery features"
                    ],
                    confidence_level=0.9
                ))
        
        # Anomaly insights
        anomaly_correlations = [c for c in recent_correlations if c.correlation_type == CorrelationType.ANOMALY]
        
        if len(anomaly_correlations) > 10:  # Threshold for concern
            insights.append(CorrelationInsight(
                insight_type="anomaly_detection",
                description=f"High number of anomalies detected: {len(anomaly_correlations)}",
                affected_services=["monitoring", "security"],
                business_impact="Potential system issues or security concerns",
                recommended_actions=[
                    "Investigate unusual activity patterns",
                    "Review security monitoring alerts",
                    "Check for system performance issues"
                ],
                confidence_level=0.85
            ))
        
        # Business process insights
        business_correlations = [c for c in recent_correlations if c.correlation_type == CorrelationType.BUSINESS_PROCESS]
        
        if business_correlations:
            # Revenue correlation analysis
            revenue_patterns = [c for c in business_correlations if "revenue" in c.pattern_description.lower()]
            
            if revenue_patterns:
                avg_revenue_confidence = sum(c.confidence_score for c in revenue_patterns) / len(revenue_patterns)
                
                insights.append(CorrelationInsight(
                    insight_type="revenue_optimization",
                    description=f"Revenue correlation patterns show {avg_revenue_confidence:.2f} confidence",
                    affected_services=["monetization", "content", "analytics"],
                    business_impact="Revenue attribution and optimization opportunities",
                    recommended_actions=[
                        "Strengthen content-to-revenue tracking",
                        "Optimize monetization workflows",
                        "Enhance revenue analytics capabilities"
                    ],
                    confidence_level=avg_revenue_confidence
                ))
        
        return insights
    
    def get_correlation_statistics(self) -> Dict[str, Any]:
        """Get correlation analysis statistics"""
        
        total_correlations = len(self.discovered_correlations)
        
        if total_correlations == 0:
            return {"message": "No correlations discovered yet"}
        
        # Group by type
        by_type = defaultdict(int)
        total_confidence = 0
        
        for correlation in self.discovered_correlations:
            by_type[correlation.correlation_type.value] += 1
            total_confidence += correlation.confidence_score
        
        avg_confidence = total_confidence / total_correlations
        
        # Recent activity
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_correlations = [
            c for c in self.discovered_correlations 
            if c.discovered_at >= recent_cutoff
        ]
        
        return {
            "total_correlations": total_correlations,
            "average_confidence": avg_confidence,
            "correlations_by_type": dict(by_type),
            "recent_correlations_1h": len(recent_correlations),
            "correlation_patterns": dict(self.correlation_patterns),
            "buffer_size": len(self.event_buffer),
            "active_rules": len([r for r in self.correlation_rules if r.enabled])
        }
    
    async def find_related_events(self, event_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Find events related to a specific event"""
        
        # Find the original event
        target_event = None
        for event in self.event_buffer:
            if event.get("event_id") == event_id:
                target_event = event
                break
        
        if not target_event:
            return []
        
        related_events = []
        
        # Find correlations containing this event
        for correlation in self.discovered_correlations:
            event_ids_in_correlation = [e.get("event_id") for e in correlation.correlated_events]
            
            if event_id in event_ids_in_correlation:
                # Add all other events from this correlation
                for corr_event in correlation.correlated_events:
                    if corr_event.get("event_id") != event_id:
                        corr_event["correlation_context"] = {
                            "correlation_id": correlation.correlation_id,
                            "correlation_type": correlation.correlation_type.value,
                            "confidence": correlation.confidence_score,
                            "business_significance": correlation.business_significance
                        }
                        related_events.append(corr_event)
        
        # Also find events with similar context
        target_user = target_event.get("user_id")
        target_category = target_event["correlation_metadata"]["event_category"]
        
        if target_user:
            for event in self.event_buffer:
                if (event.get("user_id") == target_user and 
                    event.get("event_id") != event_id and
                    event["correlation_metadata"]["event_category"] == target_category):
                    
                    event["relation_context"] = {
                        "relation_type": "same_user_category",
                        "similarity_score": 0.6
                    }
                    related_events.append(event)
        
        # Remove duplicates and limit results
        seen_event_ids = set()
        unique_related = []
        
        for event in related_events:
            event_id_key = event.get("event_id")
            if event_id_key and event_id_key not in seen_event_ids:
                seen_event_ids.add(event_id_key)
                unique_related.append(event)
                
                if len(unique_related) >= max_results:
                    break
        
        return unique_related


# Export main classes
__all__ = [
    'EventCorrelationAnalyzer',
    'CorrelationType',
    'CorrelationRule',
    'EventCorrelation',
    'CorrelationInsight'
]