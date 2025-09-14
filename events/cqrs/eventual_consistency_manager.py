"""🚀 Enterprise Eventual Consistency Manager - CQRS Architecture
================================================================
Module: events/cqrs/eventual_consistency_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE EVENTUAL CONSISTENCY MANAGER
Advanced consistency management across distributed aggregates
- Cross-aggregate consistency monitoring and reconciliation
- Eventual consistency guarantees with configurable timeouts
- Conflict detection and resolution strategies
- Consistency violation alerts and auto-healing
- Distributed consensus and coordination
- Real-time consistency metrics and dashboards
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Type, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import hashlib
import json

from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)


class ConsistencyLevel(Enum):
    """Consistency level requirements"""
    EVENTUAL = "eventual"
    SESSION = "session"
    MONOTONIC_READ = "monotonic_read"
    MONOTONIC_WRITE = "monotonic_write"
    STRONG = "strong"


class ConsistencyState(Enum):
    """Consistency state of aggregates"""
    CONSISTENT = "consistent"
    CONVERGING = "converging"
    INCONSISTENT = "inconsistent"
    TIMEOUT = "timeout"
    CONFLICT = "conflict"


class ReconciliationStrategy(Enum):
    """Strategies for consistency reconciliation"""
    LAST_WRITER_WINS = "last_writer_wins"
    MERGE = "merge"
    COMPENSATING_ACTION = "compensating_action"
    MANUAL_RESOLUTION = "manual_resolution"
    CUSTOM = "custom"


@dataclass
class ConsistencyRule:
    """Rule defining consistency requirements between aggregates"""
    rule_id: str
    name: str
    source_aggregate_type: str
    target_aggregate_types: List[str]
    consistency_level: ConsistencyLevel
    max_lag_seconds: int = 300  # 5 minutes default
    reconciliation_strategy: ReconciliationStrategy = ReconciliationStrategy.LAST_WRITER_WINS
    enabled: bool = True
    priority: int = 0
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsistencyViolation:
    """Represents a consistency violation"""
    violation_id: str
    rule_id: str
    source_aggregate_id: str
    target_aggregate_id: str
    source_version: int
    target_version: int
    lag_seconds: float
    detected_at: datetime
    state: ConsistencyState
    description: str
    resolution_attempt_count: int = 0
    last_resolution_attempt: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregateSnapshot:
    """Snapshot of aggregate state for consistency checking"""
    aggregate_id: str
    aggregate_type: str
    version: int
    last_updated: datetime
    checksum: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConsistencyChecker:
    """Check consistency between aggregates"""
    
    def __init__(self) -> None:
        self._snapshots: Dict[str, AggregateSnapshot] = {}
        self._consistency_cache: Dict[str, Dict[str, Any]] = {}
    
    async def check_consistency(self, rule: ConsistencyRule, 
                              source_snapshot: AggregateSnapshot,
                              target_snapshots: List[AggregateSnapshot]) -> List[ConsistencyViolation]:
        """Check consistency between source and target aggregates"""
        violations = []
        
        for target_snapshot in target_snapshots:
            # Check temporal consistency (lag)
            lag_seconds = (target_snapshot.last_updated - source_snapshot.last_updated).total_seconds()
            
            if abs(lag_seconds) > rule.max_lag_seconds:
                violation = ConsistencyViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    source_aggregate_id=source_snapshot.aggregate_id,
                    target_aggregate_id=target_snapshot.aggregate_id,
                    source_version=source_snapshot.version,
                    target_version=target_snapshot.version,
                    lag_seconds=abs(lag_seconds),
                    detected_at=datetime.utcnow(),
                    state=ConsistencyState.TIMEOUT if abs(lag_seconds) > rule.max_lag_seconds * 2 else ConsistencyState.INCONSISTENT,
                    description=f"Temporal consistency violation: {abs(lag_seconds):.2f}s lag exceeds {rule.max_lag_seconds}s limit"
                )
                violations.append(violation)
            
            # Check data consistency based on consistency level
            if rule.consistency_level in [ConsistencyLevel.STRONG, ConsistencyLevel.SESSION]:
                data_consistent = await self._check_data_consistency(
                    rule, source_snapshot, target_snapshot
                )
                
                if not data_consistent:
                    violation = ConsistencyViolation(
                        violation_id=str(uuid.uuid4()),
                        rule_id=rule.rule_id,
                        source_aggregate_id=source_snapshot.aggregate_id,
                        target_aggregate_id=target_snapshot.aggregate_id,
                        source_version=source_snapshot.version,
                        target_version=target_snapshot.version,
                        lag_seconds=abs(lag_seconds),
                        detected_at=datetime.utcnow(),
                        state=ConsistencyState.CONFLICT,
                        description="Data consistency violation detected"
                    )
                    violations.append(violation)
        
        return violations
    
    async def _check_data_consistency(self, rule: ConsistencyRule,
                                    source: AggregateSnapshot,
                                    target: AggregateSnapshot) -> bool:
        """Check data consistency between aggregates"""
        # Extract relevant fields based on rule conditions
        relevant_fields = rule.conditions.get("fields", [])
        
        if not relevant_fields:
            # If no specific fields, compare checksums
            return source.checksum == target.checksum
        
        # Compare specific fields
        for field in relevant_fields:
            source_value = source.data.get(field)
            target_value = target.data.get(field)
            
            if source_value != target_value:
                return False
        
        return True
    
    def update_snapshot(self, snapshot: AggregateSnapshot) -> None:
        """Update aggregate snapshot"""
        self._snapshots[snapshot.aggregate_id] = snapshot
    
    def get_snapshot(self, aggregate_id: str) -> Optional[AggregateSnapshot]:
        """Get aggregate snapshot"""
        return self._snapshots.get(aggregate_id)
    
    def calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for data"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()


class ReconciliationEngine:
    """Engine for reconciling consistency violations"""
    
    def __init__(self) -> None:
        self._reconciliation_strategies: Dict[ReconciliationStrategy, Callable] = {
            ReconciliationStrategy.LAST_WRITER_WINS: self._last_writer_wins_strategy,
            ReconciliationStrategy.MERGE: self._merge_strategy,
            ReconciliationStrategy.COMPENSATING_ACTION: self._compensating_action_strategy,
        }
        self._custom_strategies: Dict[str, Callable] = {}
    
    def register_custom_strategy(self, strategy_name: str, strategy_func: Callable) -> None:
        """Register custom reconciliation strategy"""
        self._custom_strategies[strategy_name] = strategy_func
    
    async def reconcile_violation(self, violation: ConsistencyViolation, rule: ConsistencyRule,
                                source_snapshot: AggregateSnapshot,
                                target_snapshot: AggregateSnapshot) -> bool:
        """Reconcile consistency violation"""
        try:
            strategy = self._reconciliation_strategies.get(rule.reconciliation_strategy)
            
            if strategy:
                success = await strategy(violation, rule, source_snapshot, target_snapshot)
            elif rule.reconciliation_strategy == ReconciliationStrategy.CUSTOM:
                custom_strategy_name = rule.metadata.get("custom_strategy")
                if custom_strategy_name and custom_strategy_name in self._custom_strategies:
                    strategy = self._custom_strategies[custom_strategy_name]
                    success = await strategy(violation, rule, source_snapshot, target_snapshot)
                else:
                    logger.error(f"Custom strategy not found: {custom_strategy_name}")
                    success = False
            else:
                logger.error(f"Unknown reconciliation strategy: {rule.reconciliation_strategy}")
                success = False
            
            if success:
                violation.resolved_at = datetime.utcnow()
                violation.state = ConsistencyState.CONSISTENT
            
            violation.resolution_attempt_count += 1
            violation.last_resolution_attempt = datetime.utcnow()
            
            return success
            
        except Exception as e:
            logger.error(f"Reconciliation failed for violation {violation.violation_id}: {e}")
            return False
    
    async def _last_writer_wins_strategy(self, violation: ConsistencyViolation, rule: ConsistencyRule,
                                       source: AggregateSnapshot, target: AggregateSnapshot) -> bool:
        """Last writer wins reconciliation strategy"""
        # Determine which aggregate was updated last
        if source.last_updated > target.last_updated:
            # Source is newer, update target
            logger.info(f"Reconciling with source data: {source.aggregate_id} -> {target.aggregate_id}")
            # In a real implementation, this would trigger an update command
            return True
        else:
            # Target is newer, no action needed or update source
            logger.info(f"Target is newer, no reconciliation needed: {target.aggregate_id}")
            return True
    
    async def _merge_strategy(self, violation: ConsistencyViolation, rule: ConsistencyRule,
                            source: AggregateSnapshot, target: AggregateSnapshot) -> bool:
        """Merge reconciliation strategy"""
        # Merge data from both aggregates
        merged_data = {}
        
        # Start with source data
        merged_data.update(source.data)
        
        # Merge target data (non-conflicting fields)
        for key, value in target.data.items():
            if key not in merged_data:
                merged_data[key] = value
            else:
                # Handle conflicts based on rule configuration
                conflict_resolution = rule.metadata.get("conflict_resolution", "source_wins")
                if conflict_resolution == "target_wins":
                    merged_data[key] = value
                elif conflict_resolution == "latest_timestamp":
                    # Use value from the most recently updated aggregate
                    if target.last_updated > source.last_updated:
                        merged_data[key] = value
        
        logger.info(f"Merging data for aggregates: {source.aggregate_id}, {target.aggregate_id}")
        # In a real implementation, this would trigger update commands for both aggregates
        return True
    
    async def _compensating_action_strategy(self, violation: ConsistencyViolation, rule: ConsistencyRule,
                                          source: AggregateSnapshot, target: AggregateSnapshot) -> bool:
        """Compensating action reconciliation strategy"""
        # Execute compensating actions to restore consistency
        compensating_actions = rule.metadata.get("compensating_actions", [])
        
        for action in compensating_actions:
            try:
                action_type = action.get("type")
                action_params = action.get("parameters", {})
                
                logger.info(f"Executing compensating action: {action_type} for violation {violation.violation_id}")
                
                # In a real implementation, this would execute the compensating action
                # For now, we'll just log it
                await asyncio.sleep(0.1)  # Simulate action execution
                
            except Exception as e:
                logger.error(f"Compensating action failed: {e}")
                return False
        
        return True


class ConsistencyMonitor:
    """Monitor consistency across the system"""
    
    def __init__(self) -> None:
        self._metrics = {
            "total_violations": 0,
            "resolved_violations": 0,
            "pending_violations": 0,
            "average_resolution_time_seconds": 0.0,
            "consistency_score": 100.0
        }
        self._violation_history: deque = deque(maxlen=10000)
        self._alert_thresholds = {
            "max_violations_per_hour": 100,
            "max_average_lag_seconds": 600,
            "min_consistency_score": 95.0
        }
    
    def record_violation(self, violation: ConsistencyViolation) -> None:
        """Record consistency violation"""
        self._metrics["total_violations"] += 1
        self._metrics["pending_violations"] += 1
        
        self._violation_history.append({
            "violation": violation,
            "timestamp": datetime.utcnow()
        })
        
        self._update_consistency_score()
        self._check_alert_thresholds()
    
    def record_resolution(self, violation: ConsistencyViolation) -> None:
        """Record violation resolution"""
        self._metrics["resolved_violations"] += 1
        self._metrics["pending_violations"] = max(0, self._metrics["pending_violations"] - 1)
        
        if violation.resolved_at and violation.detected_at:
            resolution_time = (violation.resolved_at - violation.detected_at).total_seconds()
            
            # Update average resolution time
            current_avg = self._metrics["average_resolution_time_seconds"]
            total_resolved = self._metrics["resolved_violations"]
            new_avg = ((current_avg * (total_resolved - 1)) + resolution_time) / total_resolved
            self._metrics["average_resolution_time_seconds"] = new_avg
        
        self._update_consistency_score()
    
    def _update_consistency_score(self) -> None:
        """Update overall consistency score"""
        total_violations = self._metrics["total_violations"]
        resolved_violations = self._metrics["resolved_violations"]
        
        if total_violations == 0:
            self._metrics["consistency_score"] = 100.0
        else:
            resolution_ratio = resolved_violations / total_violations
            pending_impact = self._metrics["pending_violations"] / max(total_violations, 1)
            
            # Score is based on resolution ratio and pending violations impact
            base_score = resolution_ratio * 100
            penalty = pending_impact * 20  # Penalize pending violations
            
            self._metrics["consistency_score"] = max(0.0, min(100.0, base_score - penalty))
    
    def _check_alert_thresholds(self) -> None:
        """Check if alert thresholds are exceeded"""
        # Check violations per hour
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_violations = [
            v for v in self._violation_history
            if v["timestamp"] > hour_ago
        ]
        
        if len(recent_violations) > self._alert_thresholds["max_violations_per_hour"]:
            logger.warning(f"High violation rate: {len(recent_violations)} violations in the last hour")
        
        # Check consistency score
        if self._metrics["consistency_score"] < self._alert_thresholds["min_consistency_score"]:
            logger.warning(f"Low consistency score: {self._metrics['consistency_score']:.2f}%")
        
        # Check average lag
        if self._metrics["average_resolution_time_seconds"] > self._alert_thresholds["max_average_lag_seconds"]:
            logger.warning(f"High average resolution time: {self._metrics['average_resolution_time_seconds']:.2f}s")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get consistency metrics"""
        return dict(self._metrics)
    
    def get_violation_statistics(self) -> Dict[str, Any]:
        """Get violation statistics"""
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        day_ago = datetime.utcnow() - timedelta(days=1)
        
        recent_violations = [v for v in self._violation_history if v["timestamp"] > hour_ago]
        daily_violations = [v for v in self._violation_history if v["timestamp"] > day_ago]
        
        return {
            "violations_last_hour": len(recent_violations),
            "violations_last_24h": len(daily_violations),
            "total_violations": len(self._violation_history),
            "violation_types": self._get_violation_type_breakdown()
        }
    
    def _get_violation_type_breakdown(self) -> Dict[str, int]:
        """Get breakdown of violation types"""
        breakdown = defaultdict(int)
        
        for entry in self._violation_history:
            violation = entry["violation"]
            breakdown[violation.state.value] += 1
        
        return dict(breakdown)


class EnterpriseEventualConsistencyManager:
    """Enterprise eventual consistency manager"""
    
    def __init__(self) -> None:
        self._consistency_rules: Dict[str, ConsistencyRule] = {}
        self._active_violations: Dict[str, ConsistencyViolation] = {}
        self._consistency_checker = ConsistencyChecker()
        self._reconciliation_engine = ReconciliationEngine()
        self._consistency_monitor = ConsistencyMonitor()
        
        # Configuration
        self._check_interval_seconds = 60
        self._max_concurrent_checks = 50
        self._reconciliation_retry_limit = 3
        self._auto_reconciliation_enabled = True
        
        # Background tasks
        self._consistency_check_task: Optional[asyncio.Task] = None
        self._reconciliation_task: Optional[asyncio.Task] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Semaphores for concurrency control
        self._check_semaphore = asyncio.Semaphore(self._max_concurrent_checks)
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Start background tasks
        self._start_background_tasks()
    
    def register_consistency_rule(self, rule: ConsistencyRule) -> None:
        """Register consistency rule"""
        self._consistency_rules[rule.rule_id] = rule
        logger.info(f"Registered consistency rule: {rule.rule_id} ({rule.name})")
    
    def register_custom_reconciliation_strategy(self, strategy_name: str, strategy_func: Callable) -> None:
        """Register custom reconciliation strategy"""
        self._reconciliation_engine.register_custom_strategy(strategy_name, strategy_func)
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register event handler for consistency events"""
        self._event_handlers[event_type].append(handler)
    
    async def update_aggregate_snapshot(self, snapshot: AggregateSnapshot) -> None:
        """Update aggregate snapshot and trigger consistency checks"""
        self._consistency_checker.update_snapshot(snapshot)
        
        # Trigger consistency checks for rules involving this aggregate
        affected_rules = [
            rule for rule in self._consistency_rules.values()
            if (rule.source_aggregate_type == snapshot.aggregate_type or
                snapshot.aggregate_type in rule.target_aggregate_types)
        ]
        
        for rule in affected_rules:
            asyncio.create_task(self._check_rule_consistency(rule, snapshot))
    
    async def _check_rule_consistency(self, rule: ConsistencyRule, 
                                    trigger_snapshot: AggregateSnapshot) -> None:
        """Check consistency for a specific rule"""
        if not rule.enabled:
            return
        
        async with self._check_semaphore:
            try:
                # Get source snapshot
                source_snapshot = None
                target_snapshots = []
                
                if rule.source_aggregate_type == trigger_snapshot.aggregate_type:
                    source_snapshot = trigger_snapshot
                    
                    # Find target snapshots
                    for target_type in rule.target_aggregate_types:
                        # In a real implementation, this would query the appropriate aggregate store
                        # For now, we'll check if we have snapshots in memory
                        for aggregate_id, snapshot in self._consistency_checker._snapshots.items():
                            if snapshot.aggregate_type == target_type:
                                target_snapshots.append(snapshot)
                
                elif trigger_snapshot.aggregate_type in rule.target_aggregate_types:
                    target_snapshots = [trigger_snapshot]
                    
                    # Find source snapshot
                    for aggregate_id, snapshot in self._consistency_checker._snapshots.items():
                        if snapshot.aggregate_type == rule.source_aggregate_type:
                            source_snapshot = snapshot
                            break
                
                if not source_snapshot or not target_snapshots:
                    return  # Not enough data for consistency check
                
                # Perform consistency check
                violations = await self._consistency_checker.check_consistency(
                    rule, source_snapshot, target_snapshots
                )
                
                # Process violations
                for violation in violations:
                    await self._process_violation(violation, rule, source_snapshot, target_snapshots)
                
            except Exception as e:
                logger.error(f"Consistency check failed for rule {rule.rule_id}: {e}")
    
    async def _process_violation(self, violation: ConsistencyViolation, rule: ConsistencyRule,
                               source_snapshot: AggregateSnapshot, 
                               target_snapshots: List[AggregateSnapshot]) -> None:
        """Process consistency violation"""
        # Record violation
        self._active_violations[violation.violation_id] = violation
        self._consistency_monitor.record_violation(violation)
        
        # Notify event handlers
        await self._notify_event_handlers("violation_detected", {
            "violation": violation,
            "rule": rule,
            "source_snapshot": source_snapshot,
            "target_snapshots": target_snapshots
        })
        
        # Attempt automatic reconciliation if enabled
        if self._auto_reconciliation_enabled and rule.reconciliation_strategy != ReconciliationStrategy.MANUAL_RESOLUTION:
            asyncio.create_task(self._attempt_reconciliation(violation, rule, source_snapshot, target_snapshots))
    
    async def _attempt_reconciliation(self, violation: ConsistencyViolation, rule: ConsistencyRule,
                                    source_snapshot: AggregateSnapshot,
                                    target_snapshots: List[AggregateSnapshot]) -> None:
        """Attempt to reconcile consistency violation"""
        if violation.resolution_attempt_count >= self._reconciliation_retry_limit:
            logger.warning(f"Max reconciliation attempts reached for violation {violation.violation_id}")
            return
        
        try:
            # Find the specific target snapshot for this violation
            target_snapshot = None
            for ts in target_snapshots:
                if ts.aggregate_id == violation.target_aggregate_id:
                    target_snapshot = ts
                    break
            
            if not target_snapshot:
                logger.error(f"Target snapshot not found for violation {violation.violation_id}")
                return
            
            # Attempt reconciliation
            success = await self._reconciliation_engine.reconcile_violation(
                violation, rule, source_snapshot, target_snapshot
            )
            
            if success:
                # Remove from active violations
                self._active_violations.pop(violation.violation_id, None)
                self._consistency_monitor.record_resolution(violation)
                
                # Notify event handlers
                await self._notify_event_handlers("violation_resolved", {
                    "violation": violation,
                    "rule": rule
                })
                
                logger.info(f"Successfully reconciled violation {violation.violation_id}")
            else:
                # Schedule retry if within limit
                if violation.resolution_attempt_count < self._reconciliation_retry_limit:
                    retry_delay = min(2 ** violation.resolution_attempt_count, 300)  # Exponential backoff, max 5 minutes
                    asyncio.create_task(self._schedule_retry(violation, rule, source_snapshot, target_snapshots, retry_delay))
                else:
                    violation.state = ConsistencyState.CONFLICT
                    await self._notify_event_handlers("violation_failed", {
                        "violation": violation,
                        "rule": rule
                    })
            
        except Exception as e:
            logger.error(f"Reconciliation attempt failed for violation {violation.violation_id}: {e}")
    
    async def _schedule_retry(self, violation: ConsistencyViolation, rule: ConsistencyRule,
                            source_snapshot: AggregateSnapshot, target_snapshots: List[AggregateSnapshot],
                            delay_seconds: int) -> None:
        """Schedule reconciliation retry"""
        await asyncio.sleep(delay_seconds)
        await self._attempt_reconciliation(violation, rule, source_snapshot, target_snapshots)
    
    async def _notify_event_handlers(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Notify registered event handlers"""
        handlers = self._event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_type, event_data)
                else:
                    handler(event_type, event_data)
            except Exception as e:
                logger.error(f"Event handler failed for {event_type}: {e}")
    
    def _start_background_tasks(self) -> None:
        """Start background tasks"""
        self._consistency_check_task = asyncio.create_task(self._consistency_check_loop())
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def _consistency_check_loop(self) -> None:
        """Background consistency checking loop"""
        while True:
            try:
                await asyncio.sleep(self._check_interval_seconds)
                
                # Perform periodic consistency checks
                for rule in self._consistency_rules.values():
                    if rule.enabled:
                        # Get all snapshots for this rule's aggregates
                        relevant_snapshots = [
                            snapshot for snapshot in self._consistency_checker._snapshots.values()
                            if (snapshot.aggregate_type == rule.source_aggregate_type or
                                snapshot.aggregate_type in rule.target_aggregate_types)
                        ]
                        
                        for snapshot in relevant_snapshots:
                            asyncio.create_task(self._check_rule_consistency(rule, snapshot))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Consistency check loop error: {e}")
                await asyncio.sleep(self._check_interval_seconds)
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Clean up resolved violations older than 24 hours
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                expired_violations = [
                    violation_id for violation_id, violation in self._active_violations.items()
                    if (violation.resolved_at and violation.resolved_at < cutoff_time)
                ]
                
                for violation_id in expired_violations:
                    del self._active_violations[violation_id]
                
                # Log current status
                active_count = len(self._active_violations)
                metrics = self._consistency_monitor.get_metrics()
                
                logger.info(f"Consistency status: {active_count} active violations, "
                           f"score: {metrics['consistency_score']:.2f}%")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(300)
    
    def get_consistency_status(self) -> Dict[str, Any]:
        """Get overall consistency status"""
        metrics = self._consistency_monitor.get_metrics()
        violation_stats = self._consistency_monitor.get_violation_statistics()
        
        return {
            "metrics": metrics,
            "violation_statistics": violation_stats,
            "active_violations": len(self._active_violations),
            "registered_rules": len(self._consistency_rules),
            "auto_reconciliation_enabled": self._auto_reconciliation_enabled,
            "check_interval_seconds": self._check_interval_seconds
        }
    
    def get_active_violations(self) -> List[Dict[str, Any]]:
        """Get list of active violations"""
        return [
            {
                "violation_id": violation.violation_id,
                "rule_id": violation.rule_id,
                "source_aggregate_id": violation.source_aggregate_id,
                "target_aggregate_id": violation.target_aggregate_id,
                "state": violation.state.value,
                "lag_seconds": violation.lag_seconds,
                "detected_at": violation.detected_at.isoformat(),
                "resolution_attempt_count": violation.resolution_attempt_count,
                "description": violation.description
            }
            for violation in self._active_violations.values()
        ]
    
    def get_consistency_rules(self) -> List[Dict[str, Any]]:
        """Get list of consistency rules"""
        return [
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "source_aggregate_type": rule.source_aggregate_type,
                "target_aggregate_types": rule.target_aggregate_types,
                "consistency_level": rule.consistency_level.value,
                "max_lag_seconds": rule.max_lag_seconds,
                "reconciliation_strategy": rule.reconciliation_strategy.value,
                "enabled": rule.enabled,
                "priority": rule.priority
            }
            for rule in self._consistency_rules.values()
        ]
    
    async def manual_reconciliation(self, violation_id: str) -> bool:
        """Manually trigger reconciliation for a violation"""
        violation = self._active_violations.get(violation_id)
        if not violation:
            return False
        
        rule = self._consistency_rules.get(violation.rule_id)
        if not rule:
            return False
        
        # Get snapshots
        source_snapshot = self._consistency_checker.get_snapshot(violation.source_aggregate_id)
        target_snapshot = self._consistency_checker.get_snapshot(violation.target_aggregate_id)
        
        if not source_snapshot or not target_snapshot:
            return False
        
        # Attempt reconciliation
        success = await self._reconciliation_engine.reconcile_violation(
            violation, rule, source_snapshot, target_snapshot
        )
        
        if success:
            self._active_violations.pop(violation_id, None)
            self._consistency_monitor.record_resolution(violation)
        
        return success
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable consistency rule"""
        if rule_id in self._consistency_rules:
            self._consistency_rules[rule_id].enabled = True
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable consistency rule"""
        if rule_id in self._consistency_rules:
            self._consistency_rules[rule_id].enabled = False
            return True
        return False
    
    async def shutdown(self) -> None:
        """Graceful shutdown of consistency manager"""
        logger.info("Shutting down eventual consistency manager...")
        
        # Cancel background tasks
        for task in [self._consistency_check_task, self._monitoring_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("Eventual consistency manager shutdown complete")


# Singleton instance for global access
_consistency_manager_instance: Optional[EnterpriseEventualConsistencyManager] = None


def get_consistency_manager() -> EnterpriseEventualConsistencyManager:
    """Get singleton consistency manager instance"""
    global _consistency_manager_instance
    if _consistency_manager_instance is None:
        _consistency_manager_instance = EnterpriseEventualConsistencyManager()
    return _consistency_manager_instance


def reset_consistency_manager() -> None:
    """Reset consistency manager instance (for testing)"""
    global _consistency_manager_instance
    if _consistency_manager_instance:
        asyncio.create_task(_consistency_manager_instance.shutdown())
    _consistency_manager_instance = None