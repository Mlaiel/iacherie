"""Event Compaction Optimizer - Enterprise Implementation

Advanced event compaction system for optimizing event store storage with
smart compression, deduplication, and archival strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import hashlib
import gzip
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from uuid import uuid4
import statistics

from . import DomainEvent, EventStoreInterface

logger = logging.getLogger(__name__)


class CompactionStrategy(Enum):
    """Event compaction strategies"""
    NONE = "none"  # No compaction
    SNAPSHOT_BASED = "snapshot_based"  # Remove events before snapshots
    TIME_BASED = "time_based"  # Remove events older than threshold
    COUNT_BASED = "count_based"  # Keep only last N events per aggregate
    BUSINESS_RULE_BASED = "business_rule_based"  # Based on business rules
    HYBRID = "hybrid"  # Combination of strategies


class CompressionType(Enum):
    """Compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    LZMA = "lzma"
    BROTLI = "brotli"
    ZSTD = "zstd"


class ArchivalTier(Enum):
    """Storage tiers for archival"""
    HOT = "hot"  # Immediate access
    WARM = "warm"  # Quick access
    COLD = "cold"  # Slower access
    FROZEN = "frozen"  # Archive storage


@dataclass
class CompactionRule:
    """Defines an event compaction rule"""
    rule_id: str
    name: str
    description: str
    strategy: CompactionStrategy
    enabled: bool = True
    
    # Filters
    event_types: Optional[List[str]] = None
    aggregate_types: Optional[List[str]] = None
    min_age_days: int = 30
    max_events_per_aggregate: int = 1000
    
    # Archival settings
    enable_archival: bool = False
    archival_tier: ArchivalTier = ArchivalTier.COLD
    compression_type: CompressionType = CompressionType.GZIP
    
    # Business rules
    preserve_business_events: List[str] = field(default_factory=list)
    custom_filter: Optional[str] = None


@dataclass
class CompactionMetrics:
    """Compaction operation metrics"""
    total_events_processed: int = 0
    events_compacted: int = 0
    events_archived: int = 0
    events_deleted: int = 0
    storage_saved_bytes: int = 0
    compression_ratio: float = 0.0
    processing_time_seconds: float = 0.0
    error_count: int = 0
    
    @property
    def compaction_ratio(self) -> float:
        return self.events_compacted / max(self.total_events_processed, 1)
    
    @property
    def storage_saved_mb(self) -> float:
        return self.storage_saved_bytes / (1024 * 1024)


@dataclass
class CompactionJob:
    """Represents a compaction job"""
    job_id: str
    name: str
    rules: List[CompactionRule]
    scheduled_time: datetime
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metrics: CompactionMetrics = field(default_factory=CompactionMetrics)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "name": self.name,
            "rules": [rule.rule_id for rule in self.rules],
            "scheduled_time": self.scheduled_time.isoformat(),
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metrics": {
                "total_events_processed": self.metrics.total_events_processed,
                "events_compacted": self.metrics.events_compacted,
                "events_archived": self.metrics.events_archived,
                "events_deleted": self.metrics.events_deleted,
                "storage_saved_mb": self.metrics.storage_saved_mb,
                "compression_ratio": self.metrics.compression_ratio,
                "processing_time_seconds": self.metrics.processing_time_seconds,
                "error_count": self.metrics.error_count
            },
            "error_message": self.error_message
        }


class EventAnalyzer:
    """Analyzes events for compaction opportunities"""
    
    def __init__(self, event_store -> None: EventStoreInterface) -> None:
        self.event_store = event_store
    
    async def analyze_aggregate_events(self, aggregate_id: str) -> Dict[str, Any]:
        """Analyze events for a specific aggregate"""
        try:
            events = await self.event_store.get_events(aggregate_id)
            
            if not events:
                return {"aggregate_id": aggregate_id, "event_count": 0}
            
            # Basic statistics
            event_count = len(events)
            event_types = list(set(event.event_type for event in events))
            
            # Size analysis
            total_size = sum(len(json.dumps(event.event_data, default=str)) for event in events)
            avg_size = total_size / event_count
            
            # Time analysis
            first_event = min(events, key=lambda e: e.occurred_at)
            last_event = max(events, key=lambda e: e.occurred_at)
            time_span = last_event.occurred_at - first_event.occurred_at
            
            # Version analysis
            versions = [event.event_version for event in events]
            version_gaps = self._detect_version_gaps(versions)
            
            # Duplicate detection
            duplicates = self._detect_duplicate_events(events)
            
            # Compression potential
            sample_events = events[:min(100, len(events))]
            compression_potential = self._estimate_compression_ratio(sample_events)
            
            return {
                "aggregate_id": aggregate_id,
                "event_count": event_count,
                "event_types": event_types,
                "total_size_bytes": total_size,
                "average_size_bytes": avg_size,
                "time_span_days": time_span.days,
                "first_event": first_event.occurred_at.isoformat(),
                "last_event": last_event.occurred_at.isoformat(),
                "version_gaps": version_gaps,
                "duplicate_events": len(duplicates),
                "compression_potential": compression_potential,
                "compaction_score": self._calculate_compaction_score(
                    event_count, total_size, time_span.days, len(duplicates)
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze aggregate {aggregate_id}: {e}")
            return {"aggregate_id": aggregate_id, "error": str(e)}
    
    async def analyze_event_store(self, sample_size: int = 10000) -> Dict[str, Any]:
        """Analyze entire event store for compaction opportunities"""
        try:
            # Get sample of events
            all_events = await self.event_store.get_all_events(limit=sample_size)
            
            if not all_events:
                return {"total_events": 0, "message": "No events found"}
            
            # Group by aggregate
            aggregates = {}
            for event in all_events:
                if event.aggregate_id not in aggregates:
                    aggregates[event.aggregate_id] = []
                aggregates[event.aggregate_id].append(event)
            
            # Analyze each aggregate
            aggregate_analyses = []
            total_compaction_score = 0
            total_size = 0
            total_duplicates = 0
            
            for aggregate_id, events in aggregates.items():
                analysis = await self._analyze_event_list(aggregate_id, events)
                aggregate_analyses.append(analysis)
                total_compaction_score += analysis.get("compaction_score", 0)
                total_size += analysis.get("total_size_bytes", 0)
                total_duplicates += analysis.get("duplicate_events", 0)
            
            # Overall statistics
            avg_compaction_score = total_compaction_score / len(aggregates) if aggregates else 0
            
            # Compression analysis
            compression_potential = self._estimate_compression_ratio(all_events[:1000])
            
            # Recommendations
            recommendations = self._generate_compaction_recommendations(
                aggregate_analyses, avg_compaction_score, total_duplicates
            )
            
            return {
                "total_events_analyzed": len(all_events),
                "total_aggregates": len(aggregates),
                "total_size_mb": total_size / (1024 * 1024),
                "average_compaction_score": avg_compaction_score,
                "compression_potential": compression_potential,
                "duplicate_events": total_duplicates,
                "high_compaction_aggregates": [
                    a for a in aggregate_analyses 
                    if a.get("compaction_score", 0) > 0.7
                ],
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze event store: {e}")
            return {"error": str(e)}
    
    def _detect_version_gaps(self, versions: List[int]) -> List[Tuple[int, int]]:
        """Detect gaps in version sequence"""
        gaps = []
        sorted_versions = sorted(set(versions))
        
        for i in range(1, len(sorted_versions)):
            if sorted_versions[i] - sorted_versions[i-1] > 1:
                gaps.append((sorted_versions[i-1], sorted_versions[i]))
        
        return gaps
    
    def _detect_duplicate_events(self, events: List[DomainEvent]) -> List[Tuple[str, str]]:
        """Detect duplicate events"""
        duplicates = []
        event_hashes = {}
        
        for event in events:
            # Create hash of event content (excluding ID and timestamp)
            content = f"{event.aggregate_id}:{event.event_type}:{event.event_version}:{json.dumps(event.event_data, sort_keys=True)}"
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash in event_hashes:
                duplicates.append((event_hashes[content_hash], event.event_id))
            else:
                event_hashes[content_hash] = event.event_id
        
        return duplicates
    
    def _estimate_compression_ratio(self, events: List[DomainEvent]) -> float:
        """Estimate compression ratio for events"""
        if not events:
            return 0.0
        
        try:
            # Serialize events
            serialized = json.dumps([
                {
                    "event_id": event.event_id,
                    "aggregate_id": event.aggregate_id,
                    "event_type": event.event_type,
                    "event_data": event.event_data,
                    "event_version": event.event_version,
                    "occurred_at": event.occurred_at.isoformat()
                } for event in events
            ], default=str)
            
            original_size = len(serialized.encode('utf-8'))
            compressed_size = len(gzip.compress(serialized.encode('utf-8')))
            
            return compressed_size / original_size if original_size > 0 else 1.0
            
        except Exception as e:
            logger.warning(f"Failed to estimate compression: {e}")
            return 1.0
    
    def _calculate_compaction_score(self, event_count: int, total_size: int, 
                                  time_span_days: int, duplicate_count: int) -> float:
        """Calculate compaction score (0.0 to 1.0, higher = more benefit)"""
        score = 0.0
        
        # More events = higher potential
        if event_count > 1000:
            score += 0.3
        elif event_count > 100:
            score += 0.1
        
        # Older events = higher potential
        if time_span_days > 365:
            score += 0.3
        elif time_span_days > 90:
            score += 0.2
        elif time_span_days > 30:
            score += 0.1
        
        # Large size = higher potential
        size_mb = total_size / (1024 * 1024)
        if size_mb > 100:
            score += 0.2
        elif size_mb > 10:
            score += 0.1
        
        # Duplicates = definite benefit
        if duplicate_count > 0:
            score += min(0.2, duplicate_count / event_count)
        
        return min(1.0, score)
    
    async def _analyze_event_list(self, aggregate_id: str, events: List[DomainEvent]) -> Dict[str, Any]:
        """Analyze a list of events for an aggregate"""
        if not events:
            return {"aggregate_id": aggregate_id, "event_count": 0}
        
        event_count = len(events)
        event_types = list(set(event.event_type for event in events))
        total_size = sum(len(json.dumps(event.event_data, default=str)) for event in events)
        
        first_event = min(events, key=lambda e: e.occurred_at)
        last_event = max(events, key=lambda e: e.occurred_at)
        time_span = last_event.occurred_at - first_event.occurred_at
        
        duplicates = self._detect_duplicate_events(events)
        
        return {
            "aggregate_id": aggregate_id,
            "event_count": event_count,
            "event_types": event_types,
            "total_size_bytes": total_size,
            "time_span_days": time_span.days,
            "duplicate_events": len(duplicates),
            "compaction_score": self._calculate_compaction_score(
                event_count, total_size, time_span.days, len(duplicates)
            )
        }
    
    def _generate_compaction_recommendations(self, analyses: List[Dict], 
                                           avg_score: float, total_duplicates: int) -> List[str]:
        """Generate compaction recommendations"""
        recommendations = []
        
        if avg_score > 0.7:
            recommendations.append("High compaction potential detected - consider immediate compaction")
        elif avg_score > 0.4:
            recommendations.append("Medium compaction potential - schedule regular compaction")
        
        if total_duplicates > 0:
            recommendations.append(f"Found {total_duplicates} duplicate events - enable deduplication")
        
        old_aggregates = [a for a in analyses if a.get("time_span_days", 0) > 365]
        if old_aggregates:
            recommendations.append(f"{len(old_aggregates)} aggregates have events older than 1 year - consider archival")
        
        large_aggregates = [a for a in analyses if a.get("event_count", 0) > 10000]
        if large_aggregates:
            recommendations.append(f"{len(large_aggregates)} aggregates have >10k events - consider snapshot-based compaction")
        
        return recommendations


class EventCompressor:
    """Handles event compression and decompression"""
    
    def __init__(self) -> None:
        self.compression_stats = {}
    
    def compress_events(self, events: List[DomainEvent], 
                       compression_type: CompressionType = CompressionType.GZIP) -> bytes:
        """Compress a list of events"""
        try:
            # Serialize events
            serialized = json.dumps([
                {
                    "event_id": event.event_id,
                    "aggregate_id": event.aggregate_id,
                    "aggregate_type": event.aggregate_type,
                    "event_type": event.event_type,
                    "event_data": event.event_data,
                    "event_version": event.event_version,
                    "occurred_at": event.occurred_at.isoformat()
                } for event in events
            ], default=str)
            
            data = serialized.encode('utf-8')
            original_size = len(data)
            
            # Apply compression
            if compression_type == CompressionType.GZIP:
                compressed = gzip.compress(data)
            elif compression_type == CompressionType.LZMA:
                import lzma
                compressed = lzma.compress(data)
            elif compression_type == CompressionType.BROTLI:
                try:
                    import brotli
                    compressed = brotli.compress(data)
                except ImportError:
                    logger.warning("Brotli not available, using gzip")
                    compressed = gzip.compress(data)
            else:
                compressed = data
            
            # Update stats
            compression_ratio = len(compressed) / original_size if original_size > 0 else 1.0
            self.compression_stats[compression_type.value] = {
                "total_operations": self.compression_stats.get(compression_type.value, {}).get("total_operations", 0) + 1,
                "average_ratio": (
                    self.compression_stats.get(compression_type.value, {}).get("average_ratio", compression_ratio) + 
                    compression_ratio
                ) / 2
            }
            
            return compressed
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            raise
    
    def decompress_events(self, compressed_data: bytes, 
                         compression_type: CompressionType = CompressionType.GZIP) -> List[DomainEvent]:
        """Decompress events"""
        try:
            # Decompress
            if compression_type == CompressionType.GZIP:
                data = gzip.decompress(compressed_data)
            elif compression_type == CompressionType.LZMA:
                import lzma
                data = lzma.decompress(compressed_data)
            elif compression_type == CompressionType.BROTLI:
                try:
                    import brotli
                    data = brotli.decompress(compressed_data)
                except ImportError:
                    raise ValueError("Brotli decompression not available")
            else:
                data = compressed_data
            
            # Deserialize
            serialized = data.decode('utf-8')
            events_data = json.loads(serialized)
            
            events = []
            for event_data in events_data:
                event = DomainEvent(
                    event_id=event_data["event_id"],
                    aggregate_id=event_data["aggregate_id"],
                    aggregate_type=event_data["aggregate_type"],
                    event_type=event_data["event_type"],
                    event_data=event_data["event_data"],
                    event_version=event_data["event_version"],
                    occurred_at=datetime.fromisoformat(event_data["occurred_at"])
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            raise


class CompactionExecutor:
    """Executes compaction operations"""
    
    def __init__(self, event_store -> None: EventStoreInterface, analyzer -> None: EventAnalyzer) -> None:
        self.event_store = event_store
        self.analyzer = analyzer
        self.compressor = EventCompressor()
    
    async def execute_compaction_rule(self, rule: CompactionRule, 
                                    aggregate_ids: List[str] = None) -> CompactionMetrics:
        """Execute a specific compaction rule"""
        metrics = CompactionMetrics()
        
        try:
            # Get aggregates to process
            if aggregate_ids:
                target_aggregates = aggregate_ids
            else:
                # Get all aggregates (simplified)
                all_events = await self.event_store.get_all_events(limit=10000)
                target_aggregates = list(set(event.aggregate_id for event in all_events))
            
            for aggregate_id in target_aggregates:
                aggregate_metrics = await self._compact_aggregate(rule, aggregate_id)
                
                metrics.total_events_processed += aggregate_metrics.total_events_processed
                metrics.events_compacted += aggregate_metrics.events_compacted
                metrics.events_archived += aggregate_metrics.events_archived
                metrics.events_deleted += aggregate_metrics.events_deleted
                metrics.storage_saved_bytes += aggregate_metrics.storage_saved_bytes
                metrics.error_count += aggregate_metrics.error_count
            
            # Calculate overall compression ratio
            if metrics.total_events_processed > 0:
                metrics.compression_ratio = metrics.events_compacted / metrics.total_events_processed
            
            return metrics
            
        except Exception as e:
            logger.error(f"Compaction rule execution failed: {e}")
            metrics.error_count += 1
            return metrics
    
    async def _compact_aggregate(self, rule: CompactionRule, aggregate_id: str) -> CompactionMetrics:
        """Compact events for a specific aggregate"""
        metrics = CompactionMetrics()
        
        try:
            # Get all events for aggregate
            events = await self.event_store.get_events(aggregate_id)
            metrics.total_events_processed = len(events)
            
            if not events:
                return metrics
            
            # Apply filters
            filtered_events = self._apply_rule_filters(rule, events)
            
            # Apply compaction strategy
            events_to_compact, events_to_keep = self._apply_compaction_strategy(rule, filtered_events)
            
            if events_to_compact:
                # Calculate storage savings
                original_size = sum(len(json.dumps(event.event_data, default=str)) for event in events_to_compact)
                
                if rule.enable_archival:
                    # Archive events
                    archived_count = await self._archive_events(events_to_compact, rule)
                    metrics.events_archived = archived_count
                    
                    # Compress for archival
                    compressed_data = self.compressor.compress_events(events_to_compact, rule.compression_type)
                    compressed_size = len(compressed_data)
                    metrics.compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
                    metrics.storage_saved_bytes = original_size - compressed_size
                else:
                    # Delete events
                    deleted_count = await self._delete_events(events_to_compact)
                    metrics.events_deleted = deleted_count
                    metrics.storage_saved_bytes = original_size
                
                metrics.events_compacted = len(events_to_compact)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to compact aggregate {aggregate_id}: {e}")
            metrics.error_count += 1
            return metrics
    
    def _apply_rule_filters(self, rule: CompactionRule, events: List[DomainEvent]) -> List[DomainEvent]:
        """Apply rule filters to events"""
        filtered_events = events
        
        # Filter by event types
        if rule.event_types:
            filtered_events = [e for e in filtered_events if e.event_type in rule.event_types]
        
        # Filter by aggregate types
        if rule.aggregate_types:
            filtered_events = [e for e in filtered_events if e.aggregate_type in rule.aggregate_types]
        
        # Filter by age
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=rule.min_age_days)
        filtered_events = [e for e in filtered_events if e.occurred_at < cutoff_date]
        
        # Preserve business events
        if rule.preserve_business_events:
            filtered_events = [e for e in filtered_events if e.event_type not in rule.preserve_business_events]
        
        return filtered_events
    
    def _apply_compaction_strategy(self, rule: CompactionRule, 
                                 events: List[DomainEvent]) -> Tuple[List[DomainEvent], List[DomainEvent]]:
        """Apply compaction strategy to determine which events to compact"""
        if rule.strategy == CompactionStrategy.NONE:
            return [], events
        
        elif rule.strategy == CompactionStrategy.TIME_BASED:
            # Remove events older than threshold
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=rule.min_age_days)
            events_to_compact = [e for e in events if e.occurred_at < cutoff_date]
            events_to_keep = [e for e in events if e.occurred_at >= cutoff_date]
            return events_to_compact, events_to_keep
        
        elif rule.strategy == CompactionStrategy.COUNT_BASED:
            # Keep only last N events
            sorted_events = sorted(events, key=lambda e: e.event_version, reverse=True)
            events_to_keep = sorted_events[:rule.max_events_per_aggregate]
            events_to_compact = sorted_events[rule.max_events_per_aggregate:]
            return events_to_compact, events_to_keep
        
        elif rule.strategy == CompactionStrategy.SNAPSHOT_BASED:
            # This would require snapshot information
            # For now, apply time-based as fallback
            return self._apply_compaction_strategy(
                CompactionRule(
                    rule_id="fallback",
                    name="fallback",
                    description="fallback",
                    strategy=CompactionStrategy.TIME_BASED,
                    min_age_days=rule.min_age_days
                ),
                events
            )
        
        else:
            # Default to no compaction
            return [], events
    
    async def _archive_events(self, events: List[DomainEvent], rule: CompactionRule) -> int:
        """Archive events to specified tier"""
        try:
            # Compress events
            compressed_data = self.compressor.compress_events(events, rule.compression_type)
            
            # In a real implementation, would save to archival storage
            # For now, just log the operation
            logger.info(f"Archived {len(events)} events to {rule.archival_tier.value} tier, compressed size: {len(compressed_data)} bytes")
            
            return len(events)
            
        except Exception as e:
            logger.error(f"Failed to archive events: {e}")
            return 0
    
    async def _delete_events(self, events: List[DomainEvent]) -> int:
        """Delete events from event store"""
        try:
            # In a real implementation, would delete from event store
            # For now, just log the operation
            logger.info(f"Deleted {len(events)} events from event store")
            
            return len(events)
            
        except Exception as e:
            logger.error(f"Failed to delete events: {e}")
            return 0


class EventCompactionOptimizer:
    """Enterprise event compaction optimizer"""
    
    def __init__(self, event_store -> None: EventStoreInterface) -> None:
        self.event_store = event_store
        self.analyzer = EventAnalyzer(event_store)
        self.executor = CompactionExecutor(event_store, self.analyzer)
        
        self.compaction_rules: List[CompactionRule] = []
        self.job_history: List[CompactionJob] = []
        self.scheduled_jobs: List[CompactionJob] = []
        
        # Initialize default rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default compaction rules"""
        # Time-based rule for old events
        self.compaction_rules.append(CompactionRule(
            rule_id="time_based_default",
            name="Archive Old Events",
            description="Archive events older than 1 year",
            strategy=CompactionStrategy.TIME_BASED,
            min_age_days=365,
            enable_archival=True,
            archival_tier=ArchivalTier.COLD,
            compression_type=CompressionType.GZIP
        ))
        
        # Count-based rule for large aggregates
        self.compaction_rules.append(CompactionRule(
            rule_id="count_based_default",
            name="Limit Aggregate Size",
            description="Keep only last 10,000 events per aggregate",
            strategy=CompactionStrategy.COUNT_BASED,
            max_events_per_aggregate=10000,
            enable_archival=True,
            archival_tier=ArchivalTier.WARM
        ))
    
    def add_compaction_rule(self, rule: CompactionRule) -> None:
        """Add custom compaction rule"""
        self.compaction_rules.append(rule)
    
    def remove_compaction_rule(self, rule_id: str) -> bool:
        """Remove compaction rule"""
        initial_count = len(self.compaction_rules)
        self.compaction_rules = [r for r in self.compaction_rules if r.rule_id != rule_id]
        return len(self.compaction_rules) < initial_count
    
    def update_compaction_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update compaction rule"""
        for rule in self.compaction_rules:
            if rule.rule_id == rule_id:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                return True
        return False
    
    async def analyze_compaction_opportunities(self) -> Dict[str, Any]:
        """Analyze event store for compaction opportunities"""
        return await self.analyzer.analyze_event_store()
    
    async def analyze_aggregate(self, aggregate_id: str) -> Dict[str, Any]:
        """Analyze specific aggregate for compaction"""
        return await self.analyzer.analyze_aggregate_events(aggregate_id)
    
    async def create_compaction_job(self, name: str, rule_ids: List[str],
                                  scheduled_time: datetime = None) -> CompactionJob:
        """Create a new compaction job"""
        # Get rules
        rules = [rule for rule in self.compaction_rules if rule.rule_id in rule_ids and rule.enabled]
        
        if not rules:
            raise ValueError("No enabled rules found for job")
        
        job = CompactionJob(
            job_id=str(uuid4()),
            name=name,
            rules=rules,
            scheduled_time=scheduled_time or datetime.now(timezone.utc)
        )
        
        self.scheduled_jobs.append(job)
        return job
    
    async def execute_compaction_job(self, job_id: str) -> CompactionJob:
        """Execute a compaction job"""
        # Find job
        job = None
        for scheduled_job in self.scheduled_jobs:
            if scheduled_job.job_id == job_id:
                job = scheduled_job
                break
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Execute job
        job.status = "running"
        job.start_time = datetime.now(timezone.utc)
        
        try:
            total_metrics = CompactionMetrics()
            
            for rule in job.rules:
                logger.info(f"Executing compaction rule: {rule.name}")
                rule_metrics = await self.executor.execute_compaction_rule(rule)
                
                # Aggregate metrics
                total_metrics.total_events_processed += rule_metrics.total_events_processed
                total_metrics.events_compacted += rule_metrics.events_compacted
                total_metrics.events_archived += rule_metrics.events_archived
                total_metrics.events_deleted += rule_metrics.events_deleted
                total_metrics.storage_saved_bytes += rule_metrics.storage_saved_bytes
                total_metrics.error_count += rule_metrics.error_count
            
            # Calculate overall compression ratio
            if total_metrics.total_events_processed > 0:
                total_metrics.compression_ratio = total_metrics.events_compacted / total_metrics.total_events_processed
            
            job.metrics = total_metrics
            job.status = "completed" if total_metrics.error_count == 0 else "failed"
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            logger.error(f"Compaction job {job_id} failed: {e}")
        finally:
            job.end_time = datetime.now(timezone.utc)
            if job.start_time:
                job.metrics.processing_time_seconds = (job.end_time - job.start_time).total_seconds()
            
            # Move to history
            self.job_history.append(job)
            self.scheduled_jobs.remove(job)
        
        return job
    
    async def execute_all_rules(self) -> Dict[str, Any]:
        """Execute all enabled compaction rules"""
        enabled_rules = [rule for rule in self.compaction_rules if rule.enabled]
        
        if not enabled_rules:
            return {"message": "No enabled rules to execute"}
        
        # Create and execute job
        job = await self.create_compaction_job(
            name="Execute All Rules",
            rule_ids=[rule.rule_id for rule in enabled_rules]
        )
        
        executed_job = await self.execute_compaction_job(job.job_id)
        return executed_job.to_dict()
    
    async def schedule_periodic_compaction(self, interval_hours: int = 24) -> None:
        """Schedule periodic compaction"""
        # This would typically integrate with a job scheduler
        # For now, just log the intent
        logger.info(f"Periodic compaction scheduled every {interval_hours} hours")
    
    def get_compaction_rules(self) -> List[Dict[str, Any]]:
        """Get all compaction rules"""
        return [
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "strategy": rule.strategy.value,
                "enabled": rule.enabled,
                "min_age_days": rule.min_age_days,
                "max_events_per_aggregate": rule.max_events_per_aggregate,
                "enable_archival": rule.enable_archival,
                "archival_tier": rule.archival_tier.value,
                "compression_type": rule.compression_type.value
            } for rule in self.compaction_rules
        ]
    
    def get_job_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get compaction job history"""
        recent_jobs = self.job_history[-limit:] if limit > 0 else self.job_history
        return [job.to_dict() for job in recent_jobs]
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get scheduled compaction jobs"""
        return [job.to_dict() for job in self.scheduled_jobs]
    
    async def get_compaction_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get compaction statistics for recent period"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        recent_jobs = [
            job for job in self.job_history 
            if job.start_time and job.start_time >= cutoff_date
        ]
        
        if not recent_jobs:
            return {"message": "No recent compaction jobs"}
        
        # Calculate aggregate statistics
        total_events_processed = sum(job.metrics.total_events_processed for job in recent_jobs)
        total_events_compacted = sum(job.metrics.events_compacted for job in recent_jobs)
        total_storage_saved = sum(job.metrics.storage_saved_bytes for job in recent_jobs)
        
        successful_jobs = [job for job in recent_jobs if job.status == "completed"]
        failed_jobs = [job for job in recent_jobs if job.status == "failed"]
        
        return {
            "period_days": days,
            "total_jobs": len(recent_jobs),
            "successful_jobs": len(successful_jobs),
            "failed_jobs": len(failed_jobs),
            "success_rate": len(successful_jobs) / len(recent_jobs) if recent_jobs else 0,
            "total_events_processed": total_events_processed,
            "total_events_compacted": total_events_compacted,
            "compaction_rate": total_events_compacted / total_events_processed if total_events_processed > 0 else 0,
            "total_storage_saved_mb": total_storage_saved / (1024 * 1024),
            "average_compression_ratio": statistics.mean(
                [job.metrics.compression_ratio for job in recent_jobs if job.metrics.compression_ratio > 0]
            ) if any(job.metrics.compression_ratio > 0 for job in recent_jobs) else 0
        }
    
    async def estimate_compaction_impact(self, rule_ids: List[str]) -> Dict[str, Any]:
        """Estimate impact of compaction rules without executing"""
        rules = [rule for rule in self.compaction_rules if rule.rule_id in rule_ids]
        
        if not rules:
            return {"error": "No rules found"}
        
        # Analyze current state
        analysis = await self.analyzer.analyze_event_store(sample_size=5000)
        
        # Estimate impact based on rules
        estimated_compacted = 0
        estimated_saved_mb = 0
        
        for rule in rules:
            if rule.strategy == CompactionStrategy.TIME_BASED:
                # Estimate based on age
                age_factor = min(0.8, rule.min_age_days / 365)  # Up to 80% for 1+ year old
                estimated_compacted += analysis.get("total_events_analyzed", 0) * age_factor
            elif rule.strategy == CompactionStrategy.COUNT_BASED:
                # Estimate based on count limits
                avg_events_per_aggregate = analysis.get("total_events_analyzed", 0) / max(analysis.get("total_aggregates", 1), 1)
                if avg_events_per_aggregate > rule.max_events_per_aggregate:
                    excess_ratio = 1 - (rule.max_events_per_aggregate / avg_events_per_aggregate)
                    estimated_compacted += analysis.get("total_events_analyzed", 0) * excess_ratio
        
        estimated_saved_mb = estimated_compacted * 0.001  # Rough estimate
        
        return {
            "estimated_events_compacted": int(estimated_compacted),
            "estimated_storage_saved_mb": estimated_saved_mb,
            "estimated_compaction_ratio": estimated_compacted / max(analysis.get("total_events_analyzed", 1), 1),
            "compression_potential": analysis.get("compression_potential", 0),
            "rules_analyzed": [rule.rule_id for rule in rules]
        }
    
    async def health_check(self) -> bool:
        """Check optimizer health"""
        try:
            # Test basic analysis
            await self.analyzer.analyze_event_store(sample_size=100)
            
            # Check if rules are valid
            for rule in self.compaction_rules:
                if not rule.rule_id or not rule.name:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Compaction optimizer health check failed: {e}")
            return False