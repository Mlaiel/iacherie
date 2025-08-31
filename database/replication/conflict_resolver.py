"""
Conflict Resolver - IA Influencer Agent Platform

Advanced conflict detection and resolution for multi-master database replication
with intelligent merge strategies and data consistency guarantees.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
from .config import ReplicationConfig


class ConflictType(Enum):
    """Types of replication conflicts"""
    INSERT_INSERT = "insert_insert"
    UPDATE_UPDATE = "update_update"
    UPDATE_DELETE = "update_delete"
    DELETE_UPDATE = "delete_update"
    SCHEMA_CONFLICT = "schema_conflict"
    UNIQUE_VIOLATION = "unique_violation"
    FOREIGN_KEY_VIOLATION = "foreign_key_violation"
    TIMESTAMP_CONFLICT = "timestamp_conflict"


class ResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL_RESOLUTION = "manual_resolution"
    MERGE_VALUES = "merge_values"
    PRIORITY_BASED = "priority_based"
    CUSTOM_RESOLVER = "custom_resolver"
    REJECT_CONFLICT = "reject_conflict"


class ConflictSeverity(Enum):
    """Conflict severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConflictRecord:
    """Database conflict record"""
    id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    table_name: str
    primary_key: Dict[str, Any]
    database_type: str
    source_node: str
    target_node: str
    source_data: Dict[str, Any]
    target_data: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolved_data: Optional[Dict[str, Any]] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictResolutionRule:
    """Conflict resolution rule configuration"""
    table_pattern: str
    conflict_types: List[ConflictType]
    strategy: ResolutionStrategy
    priority: int
    conditions: Dict[str, Any] = field(default_factory=dict)
    custom_resolver: Optional[str] = None
    auto_resolve: bool = True


class ConflictResolver:
    """
    Advanced conflict resolution system for database replication.
    
    Provides intelligent conflict detection, analysis, and resolution
    with multiple strategies and customizable rules for the content
    creator platform.
    """
    
    def __init__(self, config: ReplicationConfig):
        """
        Initialize conflict resolver.
        
        Args:
            config: Replication configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ConflictResolver")
        
        # Conflict storage
        self.active_conflicts: Dict[str, ConflictRecord] = {}
        self.resolved_conflicts: Dict[str, ConflictRecord] = {}
        self.conflict_history: List[ConflictRecord] = []
        
        # Resolution rules
        self.resolution_rules: List[ConflictResolutionRule] = []
        self.custom_resolvers: Dict[str, callable] = {}
        
        # Monitoring
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self.metrics = {
            "total_conflicts": 0,
            "resolved_conflicts": 0,
            "auto_resolved_conflicts": 0,
            "manual_resolved_conflicts": 0,
            "rejected_conflicts": 0,
            "resolution_time_avg_ms": 0.0,
            "last_conflict_time": None,
            "conflicts_by_type": {},
            "conflicts_by_severity": {}
        }
        
        # Load default resolution rules
        self._load_default_resolution_rules()
        
        self.logger.info("ConflictResolver initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize conflict resolver.
        
        Returns:
            bool: True if initialization successful
        """



        try:
            self.logger.info("Initializing conflict resolver...")
            
            # Load custom resolution rules
            await self._load_custom_resolution_rules()
            
            # Register custom resolvers
            await self._register_custom_resolvers()
            
            # Start monitoring
            await self._start_monitoring()
            
            self.logger.info("Conflict resolver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize conflict resolver: {e}")
            return False
    
    def _load_default_resolution_rules(self) -> None:
        """Load default conflict resolution rules"""



        try:
            default_rules = [
                # User data conflicts - priority based
                ConflictResolutionRule(
                    table_pattern="users*",
                    conflict_types=[ConflictType.UPDATE_UPDATE],
                    strategy=ResolutionStrategy.LAST_WRITE_WINS,
                    priority=100,
                    auto_resolve=True
                ),
                
                # Content fingerprints - first write wins
                ConflictResolutionRule(
                    table_pattern="*fingerprints*",
                    conflict_types=[ConflictType.INSERT_INSERT],
                    strategy=ResolutionStrategy.FIRST_WRITE_WINS,
                    priority=90,
                    auto_resolve=True
                ),
                
                # Analytics data - merge values
                ConflictResolutionRule(
                    table_pattern="analytics*",
                    conflict_types=[ConflictType.UPDATE_UPDATE],
                    strategy=ResolutionStrategy.MERGE_VALUES,
                    priority=80,
                    auto_resolve=True
                ),
                
                # Revenue data - manual resolution (critical)
                ConflictResolutionRule(
                    table_pattern="*revenue*",
                    conflict_types=[ConflictType.UPDATE_UPDATE, ConflictType.UPDATE_DELETE],
                    strategy=ResolutionStrategy.MANUAL_RESOLUTION,
                    priority=95,
                    auto_resolve=False
                ),
                
                # System configuration - reject conflicts
                ConflictResolutionRule(
                    table_pattern="*config*",
                    conflict_types=[ConflictType.UPDATE_UPDATE],
                    strategy=ResolutionStrategy.REJECT_CONFLICT,
                    priority=100,
                    auto_resolve=True
                ),
                
                # Schema conflicts - always manual
                ConflictResolutionRule(
                    table_pattern="*",
                    conflict_types=[ConflictType.SCHEMA_CONFLICT],
                    strategy=ResolutionStrategy.MANUAL_RESOLUTION,
                    priority=100,
                    auto_resolve=False
                )
            ]
            
            self.resolution_rules.extend(default_rules)
            self.logger.info(f"Loaded {len(default_rules)} default resolution rules")
            
        except Exception as e:
            self.logger.error(f"Failed to load default resolution rules: {e}")
    
    async def _load_custom_resolution_rules(self) -> None:
        """Load custom resolution rules from configuration"""



        try:
            custom_rules_config = self.config.config_data.get("conflict_resolution", {}).get("rules", [])
            
            for rule_config in custom_rules_config:
                rule = ConflictResolutionRule(
                    table_pattern=rule_config["table_pattern"],
                    conflict_types=[ConflictType(ct) for ct in rule_config["conflict_types"]],
                    strategy=ResolutionStrategy(rule_config["strategy"]),
                    priority=rule_config.get("priority", 50),
                    conditions=rule_config.get("conditions", {}),
                    custom_resolver=rule_config.get("custom_resolver"),
                    auto_resolve=rule_config.get("auto_resolve", True)
                )
                
                self.resolution_rules.append(rule)
            
            # Sort rules by priority (higher priority first)
            self.resolution_rules.sort(key=lambda r: r.priority, reverse=True)
            
            self.logger.info(f"Loaded {len(custom_rules_config)} custom resolution rules")
            
        except Exception as e:
            self.logger.error(f"Failed to load custom resolution rules: {e}")
    
    async def _register_custom_resolvers(self) -> None:
        """Register custom conflict resolver functions"""



        try:
            # Register built-in custom resolvers
            self.custom_resolvers.update({
                "content_fingerprint_resolver": self._resolve_content_fingerprint_conflict,
                "user_profile_resolver": self._resolve_user_profile_conflict,
                "analytics_aggregation_resolver": self._resolve_analytics_aggregation_conflict,
                "revenue_validation_resolver": self._resolve_revenue_validation_conflict,
                "timestamp_based_resolver": self._resolve_timestamp_based_conflict
            })
            
            self.logger.info(f"Registered {len(self.custom_resolvers)} custom resolvers")
            
        except Exception as e:
            self.logger.error(f"Failed to register custom resolvers: {e}")
    
    async def _start_monitoring(self) -> None:
        """Start conflict monitoring"""
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Conflict monitoring started")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for conflict resolution"""
        while self.is_monitoring:
            try:
                # Process pending conflicts
                await self._process_pending_conflicts()
                
                # Clean up old resolved conflicts
                await self._cleanup_old_conflicts()
                
                # Update metrics
                await self._update_metrics()
                
                # Log conflict statistics
                await self._log_conflict_statistics()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in conflict monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def detect_conflict(
        self,
        table_name: str,
        primary_key: Dict[str, Any],
        source_data: Dict[str, Any],
        target_data: Dict[str, Any],
        source_node: str,
        target_node: str,
        database_type: str = "postgresql"
    ) -> Optional[ConflictRecord]:
        """
        Detect and analyze potential conflicts.
        
        Args:
            table_name: Name of the table
            primary_key: Primary key of the conflicting record
            source_data: Data from source node
            target_data: Data from target node
            source_node: Source node identifier
            target_node: Target node identifier
            database_type: Type of database
            
        Returns:
            ConflictRecord if conflict detected, None otherwise
        """



        try:
            # Determine conflict type
            conflict_type = self._determine_conflict_type(source_data, target_data)
            
            if conflict_type is None:
                return None  # No conflict detected
            
            # Generate conflict ID
            conflict_id = self._generate_conflict_id(
                table_name, primary_key, source_node, target_node
            )
            
            # Determine severity
            severity = self._determine_conflict_severity(
                conflict_type, table_name, source_data, target_data
            )
            
            # Create conflict record
            conflict = ConflictRecord(
                id=conflict_id,
                conflict_type=conflict_type,
                severity=severity,
                table_name=table_name,
                primary_key=primary_key,
                database_type=database_type,
                source_node=source_node,
                target_node=target_node,
                source_data=source_data,
                target_data=target_data,
                timestamp=datetime.utcnow(),
                metadata={
                    "detected_at": datetime.utcnow().isoformat(),
                    "data_size": len(json.dumps(source_data)) + len(json.dumps(target_data))
                }
            )
            
            # Store conflict
            self.active_conflicts[conflict_id] = conflict
            self.conflict_history.append(conflict)
            
            # Update metrics
            self.metrics["total_conflicts"] += 1
            self.metrics["last_conflict_time"] = datetime.utcnow().isoformat()
            self.metrics["conflicts_by_type"][conflict_type.value] = \
                self.metrics["conflicts_by_type"].get(conflict_type.value, 0) + 1
            self.metrics["conflicts_by_severity"][severity.value] = \
                self.metrics["conflicts_by_severity"].get(severity.value, 0) + 1
            
            self.logger.warning(f"Conflict detected: {conflict_id} ({conflict_type.value}, {severity.value})")
            
            # Attempt automatic resolution
            if await self._should_auto_resolve(conflict):
                await self.resolve_conflict(conflict_id)
            
            return conflict
            
        except Exception as e:
            self.logger.error(f"Failed to detect conflict: {e}")
            return None
    
    def _determine_conflict_type(
        self, 
        source_data: Dict[str, Any], 
        target_data: Dict[str, Any]
    ) -> Optional[ConflictType]:
        """Determine the type of conflict"""



        try:
            source_exists = source_data is not None and len(source_data) > 0
            target_exists = target_data is not None and len(target_data) > 0
            
            # Check for data existence patterns
            if source_exists and target_exists:
                # Both records exist - check for differences
                if self._data_differs(source_data, target_data):
                    return ConflictType.UPDATE_UPDATE
                else:
                    return None  # No actual conflict
            elif source_exists and not target_exists:
                # Source exists, target doesn't - potential delete conflict
                return ConflictType.UPDATE_DELETE
            elif not source_exists and target_exists:
                # Target exists, source doesn't - potential delete conflict
                return ConflictType.DELETE_UPDATE
            else:
                # Neither exists - no conflict
                return None
            
        except Exception as e:
            self.logger.error(f"Failed to determine conflict type: {e}")
            return ConflictType.UPDATE_UPDATE  # Default fallback
    
    def _data_differs(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> bool:
        """Check if two data records differ significantly"""



        try:
            # Exclude timestamp fields from comparison
            exclude_fields = {"updated_at", "modified_at", "last_modified", "timestamp"}
            
            data1_filtered = {k: v for k, v in data1.items() if k not in exclude_fields}
            data2_filtered = {k: v for k, v in data2.items() if k not in exclude_fields}
            
            return data1_filtered != data2_filtered
            
        except Exception as e:
            self.logger.error(f"Failed to compare data: {e}")
            return True  # Assume conflict if comparison fails
    
    def _determine_conflict_severity(
        self,
        conflict_type: ConflictType,
        table_name: str,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any]
    ) -> ConflictSeverity:
        """Determine conflict severity based on context"""



        try:
            # Critical tables always get high severity
            critical_tables = ["users", "revenue", "payments", "content_protection"]
            if any(critical in table_name.lower() for critical in critical_tables):
                return ConflictSeverity.CRITICAL
            
            # Schema conflicts are always high severity
            if conflict_type == ConflictType.SCHEMA_CONFLICT:
                return ConflictSeverity.HIGH
            
            # Delete conflicts are medium-high severity
            if conflict_type in [ConflictType.UPDATE_DELETE, ConflictType.DELETE_UPDATE]:
                return ConflictSeverity.HIGH
            
            # Check data sensitivity
            sensitive_fields = ["password", "api_key", "token", "email", "phone"]
            for field in sensitive_fields:
                if (field in source_data or field in target_data):
                    return ConflictSeverity.HIGH
            
            # Analytics and logs are typically low severity
            low_severity_tables = ["analytics", "logs", "metrics", "events"]
            if any(low_table in table_name.lower() for low_table in low_severity_tables):
                return ConflictSeverity.LOW
            
            # Default to medium severity
            return ConflictSeverity.MEDIUM
            
        except Exception as e:
            self.logger.error(f"Failed to determine conflict severity: {e}")
            return ConflictSeverity.MEDIUM
    
    def _generate_conflict_id(
        self,
        table_name: str,
        primary_key: Dict[str, Any],
        source_node: str,
        target_node: str
    ) -> str:
        """Generate unique conflict identifier"""



        try:
            # Create a hash from conflict components
            conflict_string = f"{table_name}:{json.dumps(primary_key, sort_keys=True)}:{source_node}:{target_node}"
            conflict_hash = hashlib.md5(conflict_string.encode()).hexdigest()[:8]
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            return f"conflict_{timestamp}_{conflict_hash}"
            
        except Exception as e:
            self.logger.error(f"Failed to generate conflict ID: {e}")
            return f"conflict_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_unknown"
    
    async def _should_auto_resolve(self, conflict: ConflictRecord) -> bool:
        """Determine if conflict should be automatically resolved"""



        try:
            # Find matching resolution rule
            rule = self._find_resolution_rule(conflict)
            
            if rule:
                return rule.auto_resolve
            
            # Default behavior based on severity
            return conflict.severity in [ConflictSeverity.LOW, ConflictSeverity.MEDIUM]
            
        except Exception as e:
            self.logger.error(f"Failed to determine auto-resolution for {conflict.id}: {e}")
            return False
    
    def _find_resolution_rule(self, conflict: ConflictRecord) -> Optional[ConflictResolutionRule]:
        """Find applicable resolution rule for conflict"""



        try:
            import fnmatch
            
            for rule in self.resolution_rules:
                # Check table pattern match
                if not fnmatch.fnmatch(conflict.table_name, rule.table_pattern):
                    continue
                
                # Check conflict type match
                if conflict.conflict_type not in rule.conflict_types:
                    continue
                
                # Check additional conditions
                if rule.conditions:
                    if not self._check_rule_conditions(conflict, rule.conditions):
                        continue
                
                return rule
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find resolution rule for {conflict.id}: {e}")
            return None
    
    def _check_rule_conditions(self, conflict: ConflictRecord, conditions: Dict[str, Any]) -> bool:
        """Check if conflict meets rule conditions"""



        try:
            # Check severity condition
            if "severity" in conditions:
                required_severity = ConflictSeverity(conditions["severity"])
                if conflict.severity != required_severity:
                    return False
            
            # Check data field conditions
            if "field_conditions" in conditions:
                for field, expected_value in conditions["field_conditions"].items():
                    source_value = conflict.source_data.get(field)
                    target_value = conflict.target_data.get(field)
                    
                    if source_value != expected_value and target_value != expected_value:
                        return False
            
            # Check node conditions
            if "source_node_pattern" in conditions:
                import fnmatch
                if not fnmatch.fnmatch(conflict.source_node, conditions["source_node_pattern"]):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check rule conditions: {e}")
            return False
    
    async def resolve_conflict(self, conflict_id: str, strategy: Optional[ResolutionStrategy] = None) -> bool:
        """
        Resolve a specific conflict.
        
        Args:
            conflict_id: Conflict identifier
            strategy: Override resolution strategy
            
        Returns:
            bool: True if conflict resolved successfully
        """



        try:
            if conflict_id not in self.active_conflicts:
                self.logger.error(f"Conflict not found: {conflict_id}")
                return False
            
            conflict = self.active_conflicts[conflict_id]
            
            self.logger.info(f"Resolving conflict: {conflict_id}")
            
            start_time = datetime.utcnow()
            
            # Determine resolution strategy
            if strategy is None:
                rule = self._find_resolution_rule(conflict)
                strategy = rule.strategy if rule else ResolutionStrategy.LAST_WRITE_WINS
            
            # Apply resolution strategy
            resolution_result = await self._apply_resolution_strategy(conflict, strategy)
            
            if resolution_result:
                # Mark conflict as resolved
                conflict.resolved = True
                conflict.resolution_strategy = strategy
                conflict.resolved_data = resolution_result
                conflict.resolved_at = datetime.utcnow()
                conflict.resolved_by = "system"
                
                # Move to resolved conflicts
                self.resolved_conflicts[conflict_id] = conflict
                del self.active_conflicts[conflict_id]
                
                # Update metrics
                resolution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.metrics["resolved_conflicts"] += 1
                self.metrics["auto_resolved_conflicts"] += 1
                
                # Update average resolution time
                current_avg = self.metrics["resolution_time_avg_ms"]
                resolved_count = self.metrics["resolved_conflicts"]
                self.metrics["resolution_time_avg_ms"] = (
                    (current_avg * (resolved_count - 1) + resolution_time) / resolved_count
                )
                
                self.logger.info(f"Conflict resolved: {conflict_id} using {strategy.value} "
                               f"in {resolution_time:.1f}ms")
                
                return True
            else:
                self.logger.error(f"Failed to resolve conflict: {conflict_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to resolve conflict {conflict_id}: {e}")
            return False
    
    async def _apply_resolution_strategy(
        self, 
        conflict: ConflictRecord, 
        strategy: ResolutionStrategy
    ) -> Optional[Dict[str, Any]]:
        """Apply specific resolution strategy to conflict"""



        try:
            if strategy == ResolutionStrategy.LAST_WRITE_WINS:
                return await self._resolve_last_write_wins(conflict)
            elif strategy == ResolutionStrategy.FIRST_WRITE_WINS:
                return await self._resolve_first_write_wins(conflict)
            elif strategy == ResolutionStrategy.MERGE_VALUES:
                return await self._resolve_merge_values(conflict)
            elif strategy == ResolutionStrategy.PRIORITY_BASED:
                return await self._resolve_priority_based(conflict)
            elif strategy == ResolutionStrategy.CUSTOM_RESOLVER:
                return await self._resolve_custom(conflict)
            elif strategy == ResolutionStrategy.REJECT_CONFLICT:
                return await self._resolve_reject_conflict(conflict)
            elif strategy == ResolutionStrategy.MANUAL_RESOLUTION:
                return await self._queue_manual_resolution(conflict)
            else:
                self.logger.error(f"Unknown resolution strategy: {strategy}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to apply resolution strategy {strategy}: {e}")
            return None
    
    async def _resolve_last_write_wins(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """Resolve using last write wins strategy"""



        try:
            # Compare timestamps
            source_timestamp = self._extract_timestamp(conflict.source_data)
            target_timestamp = self._extract_timestamp(conflict.target_data)
            
            if source_timestamp and target_timestamp:
                if source_timestamp > target_timestamp:
                    return conflict.source_data.copy()
                else:
                    return conflict.target_data.copy()
            else:
                # Fall back to source data if timestamps unavailable
                return conflict.source_data.copy()
                
        except Exception as e:
            self.logger.error(f"Failed last write wins resolution: {e}")
            return conflict.source_data.copy()
    
    async def _resolve_first_write_wins(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """Resolve using first write wins strategy"""



        try:
            # Compare timestamps
            source_timestamp = self._extract_timestamp(conflict.source_data)
            target_timestamp = self._extract_timestamp(conflict.target_data)
            
            if source_timestamp and target_timestamp:
                if source_timestamp < target_timestamp:
                    return conflict.source_data.copy()
                else:
                    return conflict.target_data.copy()
            else:
                # Fall back to target data if timestamps unavailable
                return conflict.target_data.copy()
                
        except Exception as e:
            self.logger.error(f"Failed first write wins resolution: {e}")
            return conflict.target_data.copy()
    
    async def _resolve_merge_values(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """Resolve by merging non-conflicting values"""



        try:
            merged_data = conflict.target_data.copy()
            
            for key, source_value in conflict.source_data.items():
                target_value = conflict.target_data.get(key)
                
                # Skip timestamp fields
                if key in ["updated_at", "modified_at", "last_modified", "timestamp"]:
                    # Use latest timestamp
                    if isinstance(source_value, datetime) and isinstance(target_value, datetime):
                        merged_data[key] = max(source_value, target_value)
                    continue
                
                # Merge numerical values by taking average
                if isinstance(source_value, (int, float)) and isinstance(target_value, (int, float)):
                    merged_data[key] = (source_value + target_value) / 2
                
                # For strings, prefer non-empty values
                elif isinstance(source_value, str) and isinstance(target_value, str):
                    if len(source_value) > len(target_value):
                        merged_data[key] = source_value
                
                # For arrays, merge unique values
                elif isinstance(source_value, list) and isinstance(target_value, list):
                    merged_data[key] = list(set(source_value + target_value))
                
                # Use source value if target is None/empty
                elif not target_value and source_value:
                    merged_data[key] = source_value
            
            return merged_data
            
        except Exception as e:
            self.logger.error(f"Failed merge values resolution: {e}")
            return conflict.source_data.copy()
    
    async def _resolve_priority_based(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """Resolve based on node priority"""



        try:
            # This would integrate with topology manager to get node priorities
            # For now, use a simple rule: primary nodes have higher priority
            
            if "primary" in conflict.source_node.lower():
                return conflict.source_data.copy()
            elif "primary" in conflict.target_node.lower():
                return conflict.target_data.copy()
            else:
                # Fall back to last write wins
                return await self._resolve_last_write_wins(conflict)
                
        except Exception as e:
            self.logger.error(f"Failed priority based resolution: {e}")
            return conflict.source_data.copy()
    
    async def _resolve_custom(self, conflict: ConflictRecord) -> Optional[Dict[str, Any]]:
        """Resolve using custom resolver function"""



        try:
            # Find applicable custom resolver
            rule = self._find_resolution_rule(conflict)
            
            if rule and rule.custom_resolver:
                resolver_func = self.custom_resolvers.get(rule.custom_resolver)
                
                if resolver_func:
                    return await resolver_func(conflict)
                else:
                    self.logger.error(f"Custom resolver not found: {rule.custom_resolver}")
            
            # Fall back to last write wins
            return await self._resolve_last_write_wins(conflict)
            
        except Exception as e:
            self.logger.error(f"Failed custom resolution: {e}")
            return None
    
    async def _resolve_reject_conflict(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """Reject the conflict and keep target data"""



        try:
            self.metrics["rejected_conflicts"] += 1
            self.logger.info(f"Conflict rejected: {conflict.id}")
            
            return conflict.target_data.copy()
            
        except Exception as e:
            self.logger.error(f"Failed reject conflict resolution: {e}")
            return conflict.target_data.copy()
    
    async def _queue_manual_resolution(self, conflict: ConflictRecord) -> None:
        """Queue conflict for manual resolution"""



        try:
            # This would integrate with a manual resolution queue/UI
            self.logger.info(f"Conflict queued for manual resolution: {conflict.id}")
            
            conflict.metadata["queued_for_manual"] = True
            conflict.metadata["queued_at"] = datetime.utcnow().isoformat()
            
            self.metrics["manual_resolved_conflicts"] += 1
            
            return None  # Return None to indicate manual resolution needed
            
        except Exception as e:
            self.logger.error(f"Failed to queue manual resolution: {e}")
            return None
    
    def _extract_timestamp(self, data: Dict[str, Any]) -> Optional[datetime]:
        """Extract timestamp from data record"""



        try:
            timestamp_fields = ["updated_at", "modified_at", "last_modified", "timestamp", "created_at"]
            
            for field in timestamp_fields:
                if field in data:
                    value = data[field]
                    
                    if isinstance(value, datetime):
                        return value
                    elif isinstance(value, str):
                        # Try to parse ISO format
                        try:
                            return datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except:
                            pass
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract timestamp: {e}")
            return None
    
    # Custom resolver functions
    async def _resolve_content_fingerprint_conflict(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """Custom resolver for content fingerprint conflicts"""



        try:
            # For fingerprints, prefer the one with more complete metadata
            source_metadata = conflict.source_data.get("metadata", {})
            target_metadata = conflict.target_data.get("metadata", {})
            
            if len(source_metadata) > len(target_metadata):
                return conflict.source_data.copy()
            else:
                return conflict.target_data.copy()
                
        except Exception as e:
            self.logger.error(f"Failed content fingerprint resolution: {e}")
            return await self._resolve_first_write_wins(conflict)
    
    async def _resolve_user_profile_conflict(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """Custom resolver for user profile conflicts"""



        try:
            # Merge user profiles intelligently
            merged_data = conflict.target_data.copy()
            
            # Prefer non-empty profile fields
            for field in ["bio", "website", "location", "avatar_url"]:
                source_value = conflict.source_data.get(field)
                if source_value and not merged_data.get(field):
                    merged_data[field] = source_value
            
            # Use latest login time
            source_login = conflict.source_data.get("last_login")
            target_login = conflict.target_data.get("last_login")
            
            if source_login and target_login:
                merged_data["last_login"] = max(source_login, target_login)
            
            return merged_data
            
        except Exception as e:
            self.logger.error(f"Failed user profile resolution: {e}")
            return await self._resolve_merge_values(conflict)
    
    async def _resolve_analytics_aggregation_conflict(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """Custom resolver for analytics aggregation conflicts"""



        try:
            # For analytics, sum numerical values
            merged_data = conflict.target_data.copy()
            
            for key, source_value in conflict.source_data.items():
                target_value = conflict.target_data.get(key)
                
                if isinstance(source_value, (int, float)) and isinstance(target_value, (int, float)):
                    merged_data[key] = source_value + target_value
            
            return merged_data
            
        except Exception as e:
            self.logger.error(f"Failed analytics aggregation resolution: {e}")
            return await self._resolve_merge_values(conflict)
    
    async def _resolve_revenue_validation_conflict(self, conflict: ConflictRecord) -> Optional[Dict[str, Any]]:
        """Custom resolver for revenue data conflicts - requires validation"""



        try:
            # Revenue conflicts always require manual validation
            self.logger.critical(f"Revenue conflict detected - manual validation required: {conflict.id}")
            
            conflict.metadata["requires_financial_validation"] = True
            conflict.metadata["escalated_to_finance"] = True
            
            # Don't auto-resolve revenue conflicts
            return None
            
        except Exception as e:
            self.logger.error(f"Failed revenue validation resolution: {e}")
            return None
    
    async def _resolve_timestamp_based_conflict(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """Custom resolver based on timestamp comparison"""



        try:
            # Use the record with the latest timestamp
            return await self._resolve_last_write_wins(conflict)
            
        except Exception as e:
            self.logger.error(f"Failed timestamp based resolution: {e}")
            return conflict.source_data.copy()
    
    async def _process_pending_conflicts(self) -> None:
        """Process pending conflicts for auto-resolution"""



        try:
            conflicts_to_process = list(self.active_conflicts.values())
            
            for conflict in conflicts_to_process:
                if not conflict.resolved and await self._should_auto_resolve(conflict):
                    await self.resolve_conflict(conflict.id)
            
        except Exception as e:
            self.logger.error(f"Failed to process pending conflicts: {e}")
    
    async def _cleanup_old_conflicts(self) -> None:
        """Clean up old resolved conflicts"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            
            # Remove old resolved conflicts
            old_conflicts = [
                conflict_id for conflict_id, conflict in self.resolved_conflicts.items()
                if conflict.resolved_at and conflict.resolved_at < cutoff_time
            ]
            
            for conflict_id in old_conflicts:
                del self.resolved_conflicts[conflict_id]
            
            # Trim conflict history
            self.conflict_history = [
                conflict for conflict in self.conflict_history
                if conflict.timestamp > cutoff_time
            ]
            
            if old_conflicts:
                self.logger.info(f"Cleaned up {len(old_conflicts)} old conflicts")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old conflicts: {e}")
    
    async def _update_metrics(self) -> None:
        """Update conflict resolution metrics"""



        try:
            # Update current metrics
            active_count = len(self.active_conflicts)
            resolved_count = len(self.resolved_conflicts)
            
            # Calculate resolution rate
            total_conflicts = active_count + resolved_count
            resolution_rate = (resolved_count / total_conflicts) * 100 if total_conflicts > 0 else 0
            
            self.metrics.update({
                "active_conflicts": active_count,
                "resolution_rate_percentage": resolution_rate,
                "last_updated": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics: {e}")
    
    async def _log_conflict_statistics(self) -> None:
        """Log conflict statistics periodically"""



        try:
            # Log every 10 minutes
            if datetime.utcnow().minute % 10 == 0:
                stats = {
                    "total_conflicts": self.metrics["total_conflicts"],
                    "active_conflicts": len(self.active_conflicts),
                    "resolved_conflicts": self.metrics["resolved_conflicts"],
                    "resolution_rate": self.metrics.get("resolution_rate_percentage", 0),
                    "avg_resolution_time_ms": self.metrics["resolution_time_avg_ms"]
                }
                
                self.logger.info(f"Conflict statistics: {json.dumps(stats)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log conflict statistics: {e}")
    
    def get_conflict_by_id(self, conflict_id: str) -> Optional[ConflictRecord]:
        """
        Get conflict by ID.
        
        Args:
            conflict_id: Conflict identifier
            
        Returns:
            ConflictRecord or None if not found
        """



        return (self.active_conflicts.get(conflict_id) or 
                self.resolved_conflicts.get(conflict_id))
    
    def get_active_conflicts(self) -> List[ConflictRecord]:
        """
        Get all active conflicts.
        
        Returns:
            List of active conflicts
        """



        return list(self.active_conflicts.values())
    
    def get_conflicts_by_table(self, table_name: str) -> List[ConflictRecord]:
        """
        Get conflicts for specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of conflicts for the table
        """



        return [
            conflict for conflict in self.active_conflicts.values()
            if conflict.table_name == table_name
        ]
    
    def get_conflicts_by_severity(self, severity: ConflictSeverity) -> List[ConflictRecord]:
        """
        Get conflicts by severity level.
        
        Args:
            severity: Conflict severity
            
        Returns:
            List of conflicts with specified severity
        """



        return [
            conflict for conflict in self.active_conflicts.values()
            if conflict.severity == severity
        ]
    
    def get_conflict_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive conflict metrics.
        
        Returns:
            Dict containing conflict metrics
        """



        return self.metrics.copy()
    
    def get_resolution_rules(self) -> List[Dict[str, Any]]:
        """
        Get all resolution rules.
        
        Returns:
            List of resolution rules as dictionaries
        """



        return [
            {
                "table_pattern": rule.table_pattern,
                "conflict_types": [ct.value for ct in rule.conflict_types],
                "strategy": rule.strategy.value,
                "priority": rule.priority,
                "auto_resolve": rule.auto_resolve,
                "custom_resolver": rule.custom_resolver
            }
            for rule in self.resolution_rules
        ]
    
    async def shutdown(self) -> None:
        """Shutdown conflict resolver"""



        try:
            self.logger.info("Shutting down conflict resolver...")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Resolve any remaining critical conflicts
            critical_conflicts = [
                conflict for conflict in self.active_conflicts.values()
                if conflict.severity == ConflictSeverity.CRITICAL
            ]
            
            for conflict in critical_conflicts:
                await self.resolve_conflict(conflict.id)
            
            self.logger.info("Conflict resolver shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during conflict resolver shutdown: {e}")
