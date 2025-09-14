"""
Cross-Platform Sync Monitor - Distribution Module
================================================

Real-time monitoring system for cross-platform content synchronization
in the Ainflue ecosystem. Provides comprehensive tracking of sync operations,
timing analysis, and conflict resolution.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class SyncPriority(Enum):
    """Sync operation priority levels"""
    LOW = "low"
    NORMAL = "normal" 
    HIGH = "high"
    CRITICAL = "critical"

class SyncConflictType(Enum):
    """Types of sync conflicts"""
    VERSION_MISMATCH = "version_mismatch"
    METADATA_CONFLICT = "metadata_conflict"
    PLATFORM_RESTRICTION = "platform_restriction"
    SIZE_LIMIT = "size_limit"
    FORMAT_INCOMPATIBLE = "format_incompatible"

@dataclass
class SyncOperation:
    """Individual sync operation tracking"""
    operation_id: str
    content_id: str
    source_platform: str
    target_platform: str
    priority: SyncPriority
    status: str
    start_time: datetime
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    progress_percentage: float = 0.0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SyncConflict:
    """Sync conflict tracking"""
    conflict_id: str
    sync_operation_id: str
    conflict_type: SyncConflictType
    description: str
    platforms_affected: List[str]
    severity: str
    resolution_strategy: Optional[str] = None
    resolved: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

class CrossPlatformSyncMonitor:
    """
    Advanced cross-platform synchronization monitoring system.
    
    Provides real-time tracking of sync operations across multiple platforms,
    conflict detection, performance optimization, and automated resolution.
    """
    
    def __init__(self) -> None:
        self.active_syncs: Dict[str, SyncOperation] = {}
        self.sync_history: List[SyncOperation] = []
        self.conflicts: Dict[str, SyncConflict] = {}
        self.platform_sync_queues: Dict[str, List[str]] = {}
        self.sync_performance_metrics: Dict[str, List[float]] = {}
        self.conflict_resolution_rules: Dict[SyncConflictType, str] = {}
        self._initialize_resolution_rules()
        logger.info("Cross-Platform Sync Monitor initialized")
    
    def _initialize_resolution_rules(self) -> None:
        """Initialize conflict resolution rules"""
        self.conflict_resolution_rules = {
            SyncConflictType.VERSION_MISMATCH: "use_latest_version",
            SyncConflictType.METADATA_CONFLICT: "merge_metadata",
            SyncConflictType.PLATFORM_RESTRICTION: "skip_restricted_platform",
            SyncConflictType.SIZE_LIMIT: "compress_content",
            SyncConflictType.FORMAT_INCOMPATIBLE: "convert_format"
        }
    
    async def start_sync_operation(self, content_id: str, source_platform: str,
                                  target_platforms: List[str],
                                  priority: SyncPriority = SyncPriority.NORMAL,
                                  metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Start cross-platform sync operation
        
        Args:
            content_id: Content to sync
            source_platform: Source platform
            target_platforms: List of target platforms
            priority: Sync priority level
            metadata: Additional sync metadata
            
        Returns:
            List of operation IDs for tracking
        """
        operation_ids = []
        
        for target_platform in target_platforms:
            operation_id = str(uuid.uuid4())
            
            # Estimate completion time based on platform and priority
            estimated_time = self._estimate_sync_time(source_platform, target_platform, priority)
            
            sync_op = SyncOperation(
                operation_id=operation_id,
                content_id=content_id,
                source_platform=source_platform,
                target_platform=target_platform,
                priority=priority,
                status="queued",
                start_time=datetime.utcnow(),
                estimated_completion=datetime.utcnow() + estimated_time,
                metadata=metadata or {}
            )
            
            self.active_syncs[operation_id] = sync_op
            operation_ids.append(operation_id)
            
            # Add to platform queue
            if target_platform not in self.platform_sync_queues:
                self.platform_sync_queues[target_platform] = []
            self.platform_sync_queues[target_platform].append(operation_id)
            
            # Start async processing
            asyncio.create_task(self._process_sync_operation(operation_id))
            
        logger.info(f"Started sync operations for content {content_id} to {len(target_platforms)} platforms")
        return operation_ids
    
    def _estimate_sync_time(self, source_platform: str, target_platform: str, 
                           priority: SyncPriority) -> timedelta:
        """Estimate sync completion time"""
        base_time = 60  # Base time in seconds
        
        # Platform-specific modifiers
        platform_modifiers = {
            'youtube': 2.0,
            'tiktok': 1.0,
            'instagram': 1.5,
            'spotify': 3.0,
            'soundcloud': 1.8
        }
        
        modifier = platform_modifiers.get(target_platform.lower(), 1.0)
        
        # Priority modifiers
        priority_modifiers = {
            SyncPriority.CRITICAL: 0.5,
            SyncPriority.HIGH: 0.7,
            SyncPriority.NORMAL: 1.0,
            SyncPriority.LOW: 1.5
        }
        
        total_time = base_time * modifier * priority_modifiers[priority]
        return timedelta(seconds=total_time)
    
    async def _process_sync_operation(self, operation_id -> None: str) -> None:
        """Process individual sync operation"""
        try:
            sync_op = self.active_syncs[operation_id]
            sync_op.status = "in_progress"
            
            # Simulate sync process with progress updates
            for progress in [20, 40, 60, 80, 95]:
                await asyncio.sleep(0.2)  # Simulate work
                sync_op.progress_percentage = progress
                
                # Check for potential conflicts
                conflict = await self._check_for_conflicts(sync_op)
                if conflict:
                    await self._handle_conflict(conflict)
            
            # Complete sync
            sync_op.progress_percentage = 100.0
            sync_op.status = "completed"
            sync_op.actual_completion = datetime.utcnow()
            
            # Record performance metrics
            duration = (sync_op.actual_completion - sync_op.start_time).total_seconds()
            if sync_op.target_platform not in self.sync_performance_metrics:
                self.sync_performance_metrics[sync_op.target_platform] = []
            self.sync_performance_metrics[sync_op.target_platform].append(duration)
            
            # Move to history
            self.sync_history.append(sync_op)
            del self.active_syncs[operation_id]
            
            # Remove from queue
            if operation_id in self.platform_sync_queues.get(sync_op.target_platform, []):
                self.platform_sync_queues[sync_op.target_platform].remove(operation_id)
            
            logger.info(f"Sync operation {operation_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Sync operation {operation_id} failed: {e}")
            sync_op = self.active_syncs.get(operation_id)
            if sync_op:
                sync_op.status = "failed"
                sync_op.errors.append(str(e))
    
    async def _check_for_conflicts(self, sync_op: SyncOperation) -> Optional[SyncConflict]:
        """Check for potential sync conflicts"""
        # Simulate conflict detection logic
        conflict_probability = hash(sync_op.content_id + sync_op.target_platform) % 100
        
        if conflict_probability < 5:  # 5% chance of conflict
            conflict_types = list(SyncConflictType)
            conflict_type = conflict_types[hash(sync_op.operation_id) % len(conflict_types)]
            
            conflict = SyncConflict(
                conflict_id=str(uuid.uuid4()),
                sync_operation_id=sync_op.operation_id,
                conflict_type=conflict_type,
                description=f"Detected {conflict_type.value} for sync operation",
                platforms_affected=[sync_op.target_platform],
                severity="medium"
            )
            
            self.conflicts[conflict.conflict_id] = conflict
            return conflict
        
        return None
    
    async def _handle_conflict(self, conflict -> None: SyncConflict) -> None:
        """Handle sync conflict using resolution rules"""
        resolution_strategy = self.conflict_resolution_rules.get(conflict.conflict_type)
        
        if resolution_strategy:
            conflict.resolution_strategy = resolution_strategy
            
            # Simulate conflict resolution
            await asyncio.sleep(0.1)
            conflict.resolved = True
            
            logger.info(f"Resolved conflict {conflict.conflict_id} using strategy: {resolution_strategy}")
        else:
            logger.warning(f"No resolution strategy for conflict type: {conflict.conflict_type}")
    
    def get_sync_status(self, operation_id: str) -> Optional[SyncOperation]:
        """Get status of specific sync operation"""
        return self.active_syncs.get(operation_id)
    
    def get_platform_sync_queue(self, platform: str) -> List[SyncOperation]:
        """Get sync queue for specific platform"""
        queue_ids = self.platform_sync_queues.get(platform, [])
        return [self.active_syncs[op_id] for op_id in queue_ids if op_id in self.active_syncs]
    
    def get_active_syncs_summary(self) -> Dict[str, Any]:
        """Get summary of all active sync operations"""
        total_active = len(self.active_syncs)
        
        status_counts = {}
        platform_counts = {}
        priority_counts = {}
        
        for sync_op in self.active_syncs.values():
            # Count by status
            status_counts[sync_op.status] = status_counts.get(sync_op.status, 0) + 1
            
            # Count by platform
            platform_counts[sync_op.target_platform] = platform_counts.get(sync_op.target_platform, 0) + 1
            
            # Count by priority
            priority_counts[sync_op.priority.value] = priority_counts.get(sync_op.priority.value, 0) + 1
        
        # Calculate average progress
        total_progress = sum(sync_op.progress_percentage for sync_op in self.active_syncs.values())
        avg_progress = total_progress / total_active if total_active > 0 else 0
        
        return {
            'total_active_syncs': total_active,
            'average_progress': round(avg_progress, 2),
            'status_breakdown': status_counts,
            'platform_breakdown': platform_counts,
            'priority_breakdown': priority_counts,
            'total_conflicts': len([c for c in self.conflicts.values() if not c.resolved])
        }
    
    def get_sync_performance_metrics(self, platform: Optional[str] = None, 
                                   hours: int = 24) -> Dict[str, Any]:
        """Get sync performance metrics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter recent operations
        recent_ops = [
            op for op in self.sync_history 
            if op.actual_completion and op.actual_completion >= cutoff_time
            and (platform is None or op.target_platform == platform)
        ]
        
        if not recent_ops:
            return {"message": "No recent sync operations", "period": f"{hours}h"}
        
        # Calculate metrics
        total_ops = len(recent_ops)
        successful_ops = len([op for op in recent_ops if op.status == "completed"])
        success_rate = successful_ops / total_ops
        
        # Duration statistics
        durations = [
            (op.actual_completion - op.start_time).total_seconds() 
            for op in recent_ops if op.actual_completion
        ]
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Platform breakdown
        platform_stats = {}
        if platform is None:
            for plat in set(op.target_platform for op in recent_ops):
                plat_ops = [op for op in recent_ops if op.target_platform == plat]
                plat_durations = [
                    (op.actual_completion - op.start_time).total_seconds() 
                    for op in plat_ops if op.actual_completion
                ]
                platform_stats[plat] = {
                    'operations': len(plat_ops),
                    'success_rate': len([op for op in plat_ops if op.status == "completed"]) / len(plat_ops),
                    'avg_duration': sum(plat_durations) / len(plat_durations) if plat_durations else 0
                }
        
        return {
            'period': f'{hours}h',
            'total_operations': total_ops,
            'success_rate': round(success_rate, 4),
            'duration_stats': {
                'average_seconds': round(avg_duration, 2),
                'min_seconds': round(min_duration, 2),
                'max_seconds': round(max_duration, 2)
            },
            'platform_stats': platform_stats
        }
    
    async def optimize_sync_scheduling(self) -> Dict[str, Any]:
        """Optimize sync scheduling based on performance data"""
        recommendations = []
        
        # Analyze platform performance
        for platform, metrics in self.sync_performance_metrics.items():
            if len(metrics) >= 5:  # Need sufficient data
                avg_time = sum(metrics[-10:]) / len(metrics[-10:])  # Last 10 operations
                
                if avg_time > 300:  # More than 5 minutes
                    recommendations.append(f"Consider optimizing sync performance for {platform}")
                elif avg_time < 30:  # Less than 30 seconds
                    recommendations.append(f"Excellent performance for {platform} - consider as priority platform")
        
        # Check queue lengths
        for platform, queue in self.platform_sync_queues.items():
            if len(queue) > 10:
                recommendations.append(f"High queue length for {platform} - consider load balancing")
        
        # Conflict analysis
        unresolved_conflicts = [c for c in self.conflicts.values() if not c.resolved]
        if len(unresolved_conflicts) > 5:
            recommendations.append("High number of unresolved conflicts - review resolution strategies")
        
        if not recommendations:
            recommendations.append("Sync scheduling is optimized")
        
        return {
            "recommendations": recommendations,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "active_syncs": len(self.active_syncs),
            "total_conflicts": len(self.conflicts)
        }

# Global monitor instance
cross_platform_sync_monitor = CrossPlatformSyncMonitor()

# Export main components
__all__ = [
    'CrossPlatformSyncMonitor',
    'SyncOperation',
    'SyncConflict', 
    'SyncPriority',
    'SyncConflictType',
    'cross_platform_sync_monitor'
]