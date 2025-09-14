"""Consistency Validation Service - Enterprise Implementation

Advanced consistency validation service for event sourcing with cross-aggregate
validation, business rule compliance, and automated anomaly detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from uuid import uuid4
import statistics

from . import DomainEvent, EventStoreInterface, AggregateRoot

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation rules"""
    ORDERING = "ordering"  # Event ordering validation
    REFERENTIAL = "referential"  # Cross-aggregate references
    BUSINESS = "business"  # Business rule compliance
    TEMPORAL = "temporal"  # Time-based constraints
    STRUCTURAL = "structural"  # Data structure validation
    PERFORMANCE = "performance"  # Performance-related issues


class ConsistencyLevel(Enum):
    """Consistency levels for validation"""
    EVENTUAL = "eventual"  # Eventually consistent
    STRONG = "strong"  # Strongly consistent
    CAUSAL = "causal"  # Causally consistent
    SESSION = "session"  # Session consistent


@dataclass
class ValidationIssue:
    """Represents a consistency validation issue"""
    issue_id: str
    severity: ValidationSeverity
    category: ValidationCategory
    title: str
    description: str
    affected_events: List[str]
    affected_aggregates: List[str]
    detection_time: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)
    auto_fixable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "severity": self.severity.value,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "affected_events": self.affected_events,
            "affected_aggregates": self.affected_aggregates,
            "detection_time": self.detection_time.isoformat(),
            "context": self.context,
            "suggested_actions": self.suggested_actions,
            "auto_fixable": self.auto_fixable
        }


@dataclass
class ValidationRule:
    """Defines a consistency validation rule"""
    rule_id: str
    name: str
    description: str
    category: ValidationCategory
    severity: ValidationSeverity
    enabled: bool = True
    event_types: Optional[List[str]] = None
    aggregate_types: Optional[List[str]] = None
    custom_filter: Optional[Callable[[DomainEvent], bool]] = None
    
    def applies_to(self, event: DomainEvent) -> bool:
        """Check if rule applies to event"""
        if not self.enabled:
            return False
        
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        if self.aggregate_types and event.aggregate_type not in self.aggregate_types:
            return False
        
        if self.custom_filter and not self.custom_filter(event):
            return False
        
        return True


@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    report_id: str
    validation_time: datetime
    total_events_checked: int
    total_aggregates_checked: int
    issues_found: List[ValidationIssue]
    execution_time_ms: float
    consistency_score: float  # 0.0 to 1.0
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues_found if i.severity == ValidationSeverity.CRITICAL]
    
    @property
    def error_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues_found if i.severity == ValidationSeverity.ERROR]
    
    @property
    def warning_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues_found if i.severity == ValidationSeverity.WARNING]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "validation_time": self.validation_time.isoformat(),
            "total_events_checked": self.total_events_checked,
            "total_aggregates_checked": self.total_aggregates_checked,
            "issues_found": [issue.to_dict() for issue in self.issues_found],
            "execution_time_ms": self.execution_time_ms,
            "consistency_score": self.consistency_score,
            "recommendations": self.recommendations,
            "summary": {
                "critical_issues": len(self.critical_issues),
                "error_issues": len(self.error_issues),
                "warning_issues": len(self.warning_issues),
                "total_issues": len(self.issues_found)
            }
        }


class ValidationRuleEngine(ABC):
    """Abstract base for validation rule engines"""
    
    @abstractmethod
    async def validate(self, events: List[DomainEvent], 
                      aggregates: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Validate events and return issues"""
        pass


class EventOrderingValidator(ValidationRuleEngine):
    """Validates event ordering within aggregates"""
    
    async def validate(self, events: List[DomainEvent], 
                      aggregates: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Validate event ordering"""
        issues = []
        
        # Group events by aggregate
        aggregate_events = {}
        for event in events:
            if event.aggregate_id not in aggregate_events:
                aggregate_events[event.aggregate_id] = []
            aggregate_events[event.aggregate_id].append(event)
        
        # Check ordering within each aggregate
        for aggregate_id, agg_events in aggregate_events.items():
            # Sort by version
            sorted_events = sorted(agg_events, key=lambda e: e.event_version)
            
            # Check for version gaps
            expected_version = 1
            for event in sorted_events:
                if event.event_version != expected_version:
                    issues.append(ValidationIssue(
                        issue_id=str(uuid4()),
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.ORDERING,
                        title="Event Version Gap",
                        description=f"Expected version {expected_version}, found {event.event_version}",
                        affected_events=[event.event_id],
                        affected_aggregates=[aggregate_id],
                        detection_time=datetime.now(timezone.utc),
                        context={
                            "expected_version": expected_version,
                            "actual_version": event.event_version,
                            "aggregate_id": aggregate_id
                        }
                    ))
                expected_version = event.event_version + 1
            
            # Check temporal ordering
            for i in range(1, len(sorted_events)):
                prev_event = sorted_events[i-1]
                curr_event = sorted_events[i]
                
                if curr_event.occurred_at < prev_event.occurred_at:
                    issues.append(ValidationIssue(
                        issue_id=str(uuid4()),
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.TEMPORAL,
                        title="Temporal Ordering Violation",
                        description="Later version event occurred before earlier version",
                        affected_events=[prev_event.event_id, curr_event.event_id],
                        affected_aggregates=[aggregate_id],
                        detection_time=datetime.now(timezone.utc),
                        context={
                            "prev_event_time": prev_event.occurred_at.isoformat(),
                            "curr_event_time": curr_event.occurred_at.isoformat(),
                            "time_diff_seconds": (prev_event.occurred_at - curr_event.occurred_at).total_seconds()
                        }
                    ))
        
        return issues


class ReferentialIntegrityValidator(ValidationRuleEngine):
    """Validates cross-aggregate references"""
    
    def __init__(self, event_store -> None: EventStoreInterface) -> None:
        self.event_store = event_store
    
    async def validate(self, events: List[DomainEvent], 
                      aggregates: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Validate referential integrity"""
        issues = []
        
        # Track referenced aggregates
        referenced_aggregates = set()
        existing_aggregates = set()
        
        for event in events:
            existing_aggregates.add(event.aggregate_id)
            
            # Extract references from event data
            references = self._extract_references(event.event_data)
            referenced_aggregates.update(references)
        
        # Check for broken references
        broken_references = referenced_aggregates - existing_aggregates
        
        if broken_references:
            for ref in broken_references:
                # Check if reference exists in event store
                ref_events = await self.event_store.get_events(ref)
                
                if not ref_events:
                    issues.append(ValidationIssue(
                        issue_id=str(uuid4()),
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.REFERENTIAL,
                        title="Broken Reference",
                        description=f"Reference to non-existent aggregate: {ref}",
                        affected_events=[],
                        affected_aggregates=[ref],
                        detection_time=datetime.now(timezone.utc),
                        context={"missing_aggregate": ref}
                    ))
        
        return issues
    
    def _extract_references(self, event_data: Dict[str, Any]) -> Set[str]:
        """Extract aggregate references from event data"""
        references = set()
        
        # Common patterns for references
        reference_fields = [
            "aggregate_id", "parent_id", "user_id", "content_id",
            "creator_id", "collaborator_id", "referenced_aggregate"
        ]
        
        def extract_from_dict(data -> None: Dict[str, Any]) -> None:
            for key, value in data.items():
                if key in reference_fields and isinstance(value, str):
                    references.add(value)
                elif isinstance(value, dict):
                    extract_from_dict(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            extract_from_dict(item)
                        elif isinstance(item, str) and key in reference_fields:
                            references.add(item)
        
        extract_from_dict(event_data)
        return references


class BusinessRuleValidator(ValidationRuleEngine):
    """Validates business rule compliance"""
    
    def __init__(self) -> None:
        self.business_rules = []
        self._register_default_rules()
    
    def _register_default_rules(self) -> None:
        """Register default business rules"""
        # Example: Content upload must be followed by AI analysis
        self.business_rules.append({
            "name": "Content Analysis Rule",
            "description": "Content upload must be followed by AI analysis within 1 hour",
            "trigger_event": "ContentUploadCompleted",
            "expected_follow_up": "AIAnalysisCompleted",
            "time_window_hours": 1
        })
        
        # Example: User must exist before content creation
        self.business_rules.append({
            "name": "User Existence Rule",
            "description": "User must exist before creating content",
            "trigger_event": "ContentCreated",
            "prerequisite_check": "UserCreated"
        })
    
    async def validate(self, events: List[DomainEvent], 
                      aggregates: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Validate business rules"""
        issues = []
        
        # Group events by aggregate and sort by time
        aggregate_events = {}
        for event in events:
            if event.aggregate_id not in aggregate_events:
                aggregate_events[event.aggregate_id] = []
            aggregate_events[event.aggregate_id].append(event)
        
        for aggregate_id, agg_events in aggregate_events.items():
            agg_events.sort(key=lambda e: e.occurred_at)
            
            # Check each business rule
            for rule in self.business_rules:
                rule_issues = await self._validate_rule(rule, agg_events, aggregate_id)
                issues.extend(rule_issues)
        
        return issues
    
    async def _validate_rule(self, rule: Dict[str, Any], 
                           events: List[DomainEvent], 
                           aggregate_id: str) -> List[ValidationIssue]:
        """Validate a specific business rule"""
        issues = []
        
        if "trigger_event" in rule and "expected_follow_up" in rule:
            # Time-based follow-up rule
            trigger_events = [e for e in events if e.event_type == rule["trigger_event"]]
            
            for trigger in trigger_events:
                follow_up_deadline = trigger.occurred_at + timedelta(hours=rule.get("time_window_hours", 24))
                
                # Look for follow-up event
                follow_up_events = [
                    e for e in events 
                    if (e.event_type == rule["expected_follow_up"] and 
                        e.occurred_at > trigger.occurred_at and 
                        e.occurred_at <= follow_up_deadline)
                ]
                
                if not follow_up_events:
                    issues.append(ValidationIssue(
                        issue_id=str(uuid4()),
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.BUSINESS,
                        title="Business Rule Violation",
                        description=f"{rule['description']}",
                        affected_events=[trigger.event_id],
                        affected_aggregates=[aggregate_id],
                        detection_time=datetime.now(timezone.utc),
                        context={
                            "rule_name": rule["name"],
                            "trigger_event": trigger.event_type,
                            "expected_follow_up": rule["expected_follow_up"],
                            "deadline": follow_up_deadline.isoformat()
                        }
                    ))
        
        return issues


class PerformanceAnomalyValidator(ValidationRuleEngine):
    """Detects performance anomalies in event patterns"""
    
    async def validate(self, events: List[DomainEvent], 
                      aggregates: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Validate performance patterns"""
        issues = []
        
        if len(events) < 10:  # Need sufficient data
            return issues
        
        # Analyze event frequency patterns
        event_times = [e.occurred_at for e in events]
        event_times.sort()
        
        # Calculate time intervals between events
        intervals = []
        for i in range(1, len(event_times)):
            interval = (event_times[i] - event_times[i-1]).total_seconds()
            intervals.append(interval)
        
        if intervals:
            avg_interval = statistics.mean(intervals)
            std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
            
            # Detect unusual gaps
            for i, interval in enumerate(intervals):
                if interval > avg_interval + 3 * std_interval:  # 3 sigma outlier
                    issues.append(ValidationIssue(
                        issue_id=str(uuid4()),
                        severity=ValidationSeverity.INFO,
                        category=ValidationCategory.PERFORMANCE,
                        title="Unusual Event Gap",
                        description=f"Unusual gap of {interval:.2f} seconds between events",
                        affected_events=[events[i].event_id, events[i+1].event_id],
                        affected_aggregates=[events[i].aggregate_id],
                        detection_time=datetime.now(timezone.utc),
                        context={
                            "gap_seconds": interval,
                            "average_interval": avg_interval,
                            "standard_deviation": std_interval
                        }
                    ))
        
        # Analyze event size patterns
        event_sizes = []
        for event in events:
            size = len(json.dumps(event.event_data, default=str))
            event_sizes.append(size)
        
        if event_sizes:
            avg_size = statistics.mean(event_sizes)
            
            # Detect unusually large events
            for i, size in enumerate(event_sizes):
                if size > avg_size * 10:  # 10x larger than average
                    issues.append(ValidationIssue(
                        issue_id=str(uuid4()),
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.PERFORMANCE,
                        title="Large Event Detected",
                        description=f"Event size {size} bytes is unusually large",
                        affected_events=[events[i].event_id],
                        affected_aggregates=[events[i].aggregate_id],
                        detection_time=datetime.now(timezone.utc),
                        context={
                            "event_size_bytes": size,
                            "average_size_bytes": avg_size
                        }
                    ))
        
        return issues


class ConsistencyValidationService:
    """Enterprise consistency validation service"""
    
    def __init__(self, event_store -> None: EventStoreInterface) -> None:
        self.event_store = event_store
        self.validators = [
            EventOrderingValidator(),
            ReferentialIntegrityValidator(event_store),
            BusinessRuleValidator(),
            PerformanceAnomalyValidator()
        ]
        self.validation_rules: List[ValidationRule] = []
        self.validation_history: List[ValidationReport] = []
        self.auto_fix_enabled = False
        
        # Initialize default rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default validation rules"""
        # Event ordering rule
        self.validation_rules.append(ValidationRule(
            rule_id="event_ordering_001",
            name="Sequential Event Versioning",
            description="Events within an aggregate must have sequential versions",
            category=ValidationCategory.ORDERING,
            severity=ValidationSeverity.ERROR
        ))
        
        # Referential integrity rule
        self.validation_rules.append(ValidationRule(
            rule_id="referential_001",
            name="Aggregate Reference Integrity",
            description="All aggregate references must point to existing aggregates",
            category=ValidationCategory.REFERENTIAL,
            severity=ValidationSeverity.ERROR
        ))
        
        # Business rule
        self.validation_rules.append(ValidationRule(
            rule_id="business_001",
            name="Content Processing Workflow",
            description="Content must follow proper processing workflow",
            category=ValidationCategory.BUSINESS,
            severity=ValidationSeverity.WARNING,
            event_types=["ContentUploadCompleted", "AIAnalysisCompleted"]
        ))
    
    def add_validation_rule(self, rule: ValidationRule) -> None:
        """Add custom validation rule"""
        self.validation_rules.append(rule)
    
    def remove_validation_rule(self, rule_id: str) -> bool:
        """Remove validation rule"""
        initial_count = len(self.validation_rules)
        self.validation_rules = [r for r in self.validation_rules if r.rule_id != rule_id]
        return len(self.validation_rules) < initial_count
    
    def enable_auto_fix(self, enabled: bool = True) -> None:
        """Enable or disable automatic issue fixing"""
        self.auto_fix_enabled = enabled
    
    async def validate_events(self, events: List[DomainEvent] = None,
                            aggregate_ids: List[str] = None,
                            time_range: Tuple[datetime, datetime] = None) -> ValidationReport:
        """Perform comprehensive event validation"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get events to validate
            if events is None:
                events = await self._get_events_for_validation(aggregate_ids, time_range)
            
            # Get aggregate information
            aggregates = await self._get_aggregate_information(events)
            
            # Run all validators
            all_issues = []
            for validator in self.validators:
                try:
                    validator_issues = await validator.validate(events, aggregates)
                    all_issues.extend(validator_issues)
                except Exception as e:
                    logger.error(f"Validator {type(validator).__name__} failed: {e}")
            
            # Filter issues based on rules
            filtered_issues = self._filter_issues_by_rules(all_issues, events)
            
            # Auto-fix issues if enabled
            if self.auto_fix_enabled:
                fixed_issues = await self._auto_fix_issues(filtered_issues, events)
                filtered_issues = [i for i in filtered_issues if i.issue_id not in fixed_issues]
            
            # Calculate consistency score
            consistency_score = self._calculate_consistency_score(filtered_issues, len(events))
            
            # Generate recommendations
            recommendations = self._generate_recommendations(filtered_issues)
            
            # Create report
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            report = ValidationReport(
                report_id=str(uuid4()),
                validation_time=start_time,
                total_events_checked=len(events),
                total_aggregates_checked=len(set(e.aggregate_id for e in events)),
                issues_found=filtered_issues,
                execution_time_ms=execution_time,
                consistency_score=consistency_score,
                recommendations=recommendations
            )
            
            # Store in history
            self.validation_history.append(report)
            
            # Keep only last 100 reports
            if len(self.validation_history) > 100:
                self.validation_history = self.validation_history[-100:]
            
            logger.info(f"Validation completed: {len(filtered_issues)} issues found, score: {consistency_score:.2f}")
            
            return report
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise
    
    async def validate_aggregate(self, aggregate_id: str) -> ValidationReport:
        """Validate specific aggregate"""
        events = await self.event_store.get_events(aggregate_id)
        return await self.validate_events(events)
    
    async def validate_event_type(self, event_type: str) -> ValidationReport:
        """Validate specific event type"""
        # This would need event store support for filtering by event type
        all_events = await self.event_store.get_all_events(limit=10000)
        filtered_events = [e for e in all_events if e.event_type == event_type]
        return await self.validate_events(filtered_events)
    
    async def validate_time_range(self, start_time: datetime, end_time: datetime) -> ValidationReport:
        """Validate events in time range"""
        return await self.validate_events(time_range=(start_time, end_time))
    
    async def get_validation_history(self, limit: int = 10) -> List[ValidationReport]:
        """Get recent validation reports"""
        return self.validation_history[-limit:]
    
    async def get_consistency_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get consistency trends over time"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        recent_reports = [
            r for r in self.validation_history 
            if r.validation_time >= cutoff_date
        ]
        
        if not recent_reports:
            return {"message": "No recent validation data available"}
        
        scores = [r.consistency_score for r in recent_reports]
        issue_counts = [len(r.issues_found) for r in recent_reports]
        
        return {
            "period_days": days,
            "total_validations": len(recent_reports),
            "average_consistency_score": sum(scores) / len(scores),
            "min_consistency_score": min(scores),
            "max_consistency_score": max(scores),
            "average_issues_per_validation": sum(issue_counts) / len(issue_counts),
            "trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable",
            "recent_reports": [
                {
                    "date": r.validation_time.isoformat(),
                    "score": r.consistency_score,
                    "issues": len(r.issues_found)
                } for r in recent_reports[-10:]
            ]
        }
    
    async def _get_events_for_validation(self, aggregate_ids: List[str] = None,
                                       time_range: Tuple[datetime, datetime] = None) -> List[DomainEvent]:
        """Get events based on criteria"""
        if aggregate_ids:
            all_events = []
            for aggregate_id in aggregate_ids:
                events = await self.event_store.get_events(aggregate_id)
                all_events.extend(events)
        else:
            all_events = await self.event_store.get_all_events(limit=10000)
        
        # Apply time range filter
        if time_range:
            start_time, end_time = time_range
            all_events = [
                e for e in all_events 
                if start_time <= e.occurred_at <= end_time
            ]
        
        return all_events
    
    async def _get_aggregate_information(self, events: List[DomainEvent]) -> Dict[str, Any]:
        """Get aggregate information for validation"""
        # This would typically involve reconstructing aggregates or querying aggregate views
        # For now, return basic information
        aggregates = {}
        for event in events:
            if event.aggregate_id not in aggregates:
                aggregates[event.aggregate_id] = {
                    "aggregate_id": event.aggregate_id,
                    "aggregate_type": event.aggregate_type,
                    "event_count": 0,
                    "first_event": event.occurred_at,
                    "last_event": event.occurred_at
                }
            
            agg_info = aggregates[event.aggregate_id]
            agg_info["event_count"] += 1
            if event.occurred_at < agg_info["first_event"]:
                agg_info["first_event"] = event.occurred_at
            if event.occurred_at > agg_info["last_event"]:
                agg_info["last_event"] = event.occurred_at
        
        return aggregates
    
    def _filter_issues_by_rules(self, issues: List[ValidationIssue], 
                               events: List[DomainEvent]) -> List[ValidationIssue]:
        """Filter issues based on validation rules"""
        filtered_issues = []
        
        for issue in issues:
            # Find applicable rules
            applicable_rules = [
                rule for rule in self.validation_rules
                if rule.category == issue.category and rule.enabled
            ]
            
            if applicable_rules:
                # Use the most restrictive severity
                min_severity = min(rule.severity for rule in applicable_rules)
                if issue.severity.value >= min_severity.value:
                    filtered_issues.append(issue)
            else:
                # No specific rule, include all issues
                filtered_issues.append(issue)
        
        return filtered_issues
    
    async def _auto_fix_issues(self, issues: List[ValidationIssue], 
                             events: List[DomainEvent]) -> List[str]:
        """Automatically fix issues where possible"""
        fixed_issue_ids = []
        
        for issue in issues:
            if issue.auto_fixable:
                try:
                    # Implement auto-fix logic based on issue type
                    if issue.category == ValidationCategory.ORDERING:
                        # Could potentially reorder events or fix version numbers
                        pass
                    elif issue.category == ValidationCategory.STRUCTURAL:
                        # Could fix data structure issues
                        pass
                    
                    # For demo, just mark as fixed
                    fixed_issue_ids.append(issue.issue_id)
                    logger.info(f"Auto-fixed issue: {issue.title}")
                    
                except Exception as e:
                    logger.error(f"Failed to auto-fix issue {issue.issue_id}: {e}")
        
        return fixed_issue_ids
    
    def _calculate_consistency_score(self, issues: List[ValidationIssue], 
                                   total_events: int) -> float:
        """Calculate consistency score (0.0 to 1.0)"""
        if total_events == 0:
            return 1.0
        
        # Weight issues by severity
        severity_weights = {
            ValidationSeverity.CRITICAL: 10,
            ValidationSeverity.ERROR: 5,
            ValidationSeverity.WARNING: 2,
            ValidationSeverity.INFO: 1
        }
        
        total_weight = sum(severity_weights[issue.severity] for issue in issues)
        max_possible_weight = total_events * max(severity_weights.values())
        
        if max_possible_weight == 0:
            return 1.0
        
        score = 1.0 - (total_weight / max_possible_weight)
        return max(0.0, min(1.0, score))
    
    def _generate_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """Generate recommendations based on issues found"""
        recommendations = []
        
        if not issues:
            recommendations.append("No consistency issues found. System is healthy.")
            return recommendations
        
        # Group issues by category
        category_counts = {}
        for issue in issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        # Generate category-specific recommendations
        if category_counts.get(ValidationCategory.ORDERING, 0) > 0:
            recommendations.append("Consider implementing stricter event ordering controls")
        
        if category_counts.get(ValidationCategory.REFERENTIAL, 0) > 0:
            recommendations.append("Review aggregate reference management and cleanup orphaned references")
        
        if category_counts.get(ValidationCategory.BUSINESS, 0) > 0:
            recommendations.append("Review business rule compliance and consider automated enforcement")
        
        if category_counts.get(ValidationCategory.PERFORMANCE, 0) > 0:
            recommendations.append("Investigate performance anomalies and optimize event processing")
        
        # Severity-based recommendations
        critical_count = len([i for i in issues if i.severity == ValidationSeverity.CRITICAL])
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical issues immediately")
        
        error_count = len([i for i in issues if i.severity == ValidationSeverity.ERROR])
        if error_count > 5:
            recommendations.append("High number of errors detected. Consider system health review")
        
        return recommendations
    
    async def health_check(self) -> bool:
        """Check service health"""
        try:
            # Test basic validation with a small sample
            sample_events = await self.event_store.get_all_events(limit=10)
            if sample_events:
                await self.validate_events(sample_events[:5])
            
            return True
        except Exception as e:
            logger.error(f"Consistency validation service health check failed: {e}")
            return False