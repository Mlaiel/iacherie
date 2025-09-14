"""
Queue Intelligence
=================

Enterprise-grade intelligent queue management for content publication.
Uses AI to optimize publication queues across multiple platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import json
import heapq
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)

class QueuePriority(Enum):
    """Publication queue priorities"""
    CRITICAL = 1    # Breaking news, time-sensitive
    HIGH = 2        # Important announcements
    NORMAL = 3      # Regular content
    LOW = 4         # Evergreen, filler content
    BATCH = 5       # Bulk uploads

class ContentStatus(Enum):
    """Content status in queue"""
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class QueueStrategy(Enum):
    """Queue processing strategies"""
    FIFO = "fifo"                    # First In, First Out
    PRIORITY_BASED = "priority"      # Priority-based processing
    TIME_OPTIMIZED = "time_optimized"  # AI timing optimization
    PLATFORM_AWARE = "platform_aware"  # Platform-specific optimization
    ENGAGEMENT_MAXIMIZED = "engagement"  # Maximum engagement strategy

@dataclass
class QueuedContent:
    """Content item in publication queue"""
    id: str
    title: str
    content: str
    platform: str
    content_type: str
    priority: QueuePriority
    scheduled_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: ContentStatus = ContentStatus.QUEUED
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Content IDs this depends on
    tags: List[str] = field(default_factory=list)
    audience_segment: Optional[str] = None
    estimated_duration: Optional[int] = None  # Processing duration in seconds
    callback_url: Optional[str] = None

@dataclass
class QueueMetrics:
    """Queue performance metrics"""
    total_items: int
    queued_items: int
    processing_items: int
    completed_items: int
    failed_items: int
    average_wait_time: float
    average_processing_time: float
    success_rate: float
    throughput_per_hour: float
    peak_queue_length: int
    current_load: float

@dataclass
class QueueOptimization:
    """Queue optimization result"""
    reordered_queue: List[QueuedContent]
    estimated_completion_time: datetime
    optimization_score: float
    reasoning: List[str]
    resource_allocation: Dict[str, int]
    bottlenecks_identified: List[str]

class QueueProcessor(ABC):
    """Abstract base class for queue processors"""
    
    @abstractmethod
    async def process_item(self, item: QueuedContent) -> bool:
        """Process a single queue item"""
        pass
    
    @abstractmethod
    async def can_process(self, item: QueuedContent) -> bool:
        """Check if processor can handle this item"""
        pass

class PlatformQueueProcessor(QueueProcessor):
    """Platform-specific queue processor"""
    
    def __init__(self, platform -> None: str, rate_limit -> None: int = 60) -> None:
        self.platform = platform
        self.rate_limit = rate_limit  # Requests per hour
        self.last_requests: List[datetime] = []
        
    async def process_item(self, item: QueuedContent) -> bool:
        """Process item for specific platform"""
        try:
            # Check rate limits
            if not await self._check_rate_limit():
                return False
            
            # Simulate processing
            await asyncio.sleep(1)  # Simulated API call
            
            # Track request
            self.last_requests.append(datetime.now(timezone.utc))
            
            logger.info(f"Processed {item.id} for {self.platform}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {item.id}: {e}")
            return False
    
    async def can_process(self, item: QueuedContent) -> bool:
        """Check if this processor can handle the item"""
        return item.platform == self.platform and await self._check_rate_limit()
    
    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=1)
        
        # Remove old requests
        self.last_requests = [req for req in self.last_requests if req > cutoff]
        
        return len(self.last_requests) < self.rate_limit

class QueueIntelligence:
    """Intelligent queue management system"""
    
    def __init__(self) -> None:
        self.queues: Dict[str, List[QueuedContent]] = {}
        self.priority_queues: Dict[QueuePriority, List[QueuedContent]] = {
            priority: [] for priority in QueuePriority
        }
        self.processors: Dict[str, QueueProcessor] = {}
        self.metrics: Dict[str, QueueMetrics] = {}
        self.processing_items: Dict[str, QueuedContent] = {}
        self.completed_items: List[QueuedContent] = []
        self.failed_items: List[QueuedContent] = []
        
        # Configuration
        self.max_concurrent_processing = 10
        self.queue_optimization_interval = timedelta(minutes=5)
        self.last_optimization = datetime.now(timezone.utc)
        
        # AI optimization components
        self.optimization_weights = {
            "time_efficiency": 0.3,
            "priority_respect": 0.25,
            "platform_optimization": 0.2,
            "dependency_resolution": 0.15,
            "resource_utilization": 0.1
        }
    
    async def add_to_queue(
        self, 
        content: QueuedContent,
        queue_name: str = "default"
    ) -> str:
        """Add content to publication queue"""
        try:
            # Assign unique ID if not provided
            if not content.id:
                content.id = str(uuid.uuid4())
            
            # Initialize queue if it doesn't exist
            if queue_name not in self.queues:
                self.queues[queue_name] = []
            
            # Add to main queue
            self.queues[queue_name].append(content)
            
            # Add to priority queue
            heapq.heappush(self.priority_queues[content.priority], content)
            
            logger.info(f"Added content {content.id} to queue {queue_name}")
            
            # Trigger optimization if needed
            await self._check_optimization_trigger()
            
            return content.id
            
        except Exception as e:
            logger.error(f"Failed to add content to queue: {e}")
            raise
    
    async def remove_from_queue(
        self, 
        content_id: str,
        queue_name: str = "default"
    ) -> bool:
        """Remove content from queue"""
        try:
            if queue_name in self.queues:
                # Remove from main queue
                self.queues[queue_name] = [
                    item for item in self.queues[queue_name] 
                    if item.id != content_id
                ]
                
                # Remove from priority queues
                for priority_queue in self.priority_queues.values():
                    priority_queue[:] = [
                        item for item in priority_queue 
                        if item.id != content_id
                    ]
                
                # Update status if in processing
                if content_id in self.processing_items:
                    self.processing_items[content_id].status = ContentStatus.CANCELLED
                    del self.processing_items[content_id]
                
                logger.info(f"Removed content {content_id} from queue {queue_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove content from queue: {e}")
            return False
    
    async def get_next_item(
        self, 
        strategy: QueueStrategy = QueueStrategy.PRIORITY_BASED,
        platform_filter: Optional[str] = None
    ) -> Optional[QueuedContent]:
        """Get next item from queue based on strategy"""
        try:
            if strategy == QueueStrategy.FIFO:
                return await self._get_fifo_item(platform_filter)
            elif strategy == QueueStrategy.PRIORITY_BASED:
                return await self._get_priority_item(platform_filter)
            elif strategy == QueueStrategy.TIME_OPTIMIZED:
                return await self._get_time_optimized_item(platform_filter)
            elif strategy == QueueStrategy.PLATFORM_AWARE:
                return await self._get_platform_aware_item(platform_filter)
            elif strategy == QueueStrategy.ENGAGEMENT_MAXIMIZED:
                return await self._get_engagement_optimized_item(platform_filter)
            else:
                return await self._get_priority_item(platform_filter)
                
        except Exception as e:
            logger.error(f"Failed to get next item: {e}")
            return None
    
    async def _get_fifo_item(self, platform_filter: Optional[str]) -> Optional[QueuedContent]:
        """Get next item using FIFO strategy"""
        for queue in self.queues.values():
            for item in queue:
                if item.status == ContentStatus.QUEUED:
                    if platform_filter is None or item.platform == platform_filter:
                        return item
        return None
    
    async def _get_priority_item(self, platform_filter: Optional[str]) -> Optional[QueuedContent]:
        """Get next item using priority-based strategy"""
        for priority in QueuePriority:
            priority_queue = self.priority_queues[priority]
            for item in priority_queue:
                if item.status == ContentStatus.QUEUED:
                    if platform_filter is None or item.platform == platform_filter:
                        # Check dependencies
                        if await self._check_dependencies(item):
                            return item
        return None
    
    async def _get_time_optimized_item(self, platform_filter: Optional[str]) -> Optional[QueuedContent]:
        """Get next item using AI timing optimization"""
        eligible_items = []
        
        for queue in self.queues.values():
            for item in queue:
                if item.status == ContentStatus.QUEUED:
                    if platform_filter is None or item.platform == platform_filter:
                        if await self._check_dependencies(item):
                            eligible_items.append(item)
        
        if not eligible_items:
            return None
        
        # Score items based on timing optimization
        scored_items = []
        current_time = datetime.now(timezone.utc)
        
        for item in eligible_items:
            score = await self._calculate_timing_score(item, current_time)
            scored_items.append((score, item))
        
        # Sort by score (highest first)
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        return scored_items[0][1] if scored_items else None
    
    async def _get_platform_aware_item(self, platform_filter: Optional[str]) -> Optional[QueuedContent]:
        """Get next item using platform-aware strategy"""
        # Group items by platform
        platform_items = {}
        
        for queue in self.queues.values():
            for item in queue:
                if item.status == ContentStatus.QUEUED:
                    if platform_filter is None or item.platform == platform_filter:
                        if await self._check_dependencies(item):
                            if item.platform not in platform_items:
                                platform_items[item.platform] = []
                            platform_items[item.platform].append(item)
        
        # Select platform with highest priority items
        best_platform = None
        best_priority = QueuePriority.BATCH
        
        for platform, items in platform_items.items():
            platform_priority = min(item.priority for item in items)
            if platform_priority.value < best_priority.value:
                best_priority = platform_priority
                best_platform = platform
        
        if best_platform:
            # Return highest priority item from best platform
            platform_items[best_platform].sort(key=lambda x: x.priority.value)
            return platform_items[best_platform][0]
        
        return None
    
    async def _get_engagement_optimized_item(self, platform_filter: Optional[str]) -> Optional[QueuedContent]:
        """Get next item using engagement maximization strategy"""
        eligible_items = []
        
        for queue in self.queues.values():
            for item in queue:
                if item.status == ContentStatus.QUEUED:
                    if platform_filter is None or item.platform == platform_filter:
                        if await self._check_dependencies(item):
                            eligible_items.append(item)
        
        if not eligible_items:
            return None
        
        # Score items based on engagement potential
        scored_items = []
        
        for item in eligible_items:
            score = await self._calculate_engagement_score(item)
            scored_items.append((score, item))
        
        # Sort by score (highest first)
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        return scored_items[0][1] if scored_items else None
    
    async def _check_dependencies(self, item: QueuedContent) -> bool:
        """Check if all dependencies are satisfied"""
        if not item.dependencies:
            return True
        
        for dep_id in item.dependencies:
            # Check if dependency is completed
            completed = any(
                comp_item.id == dep_id 
                for comp_item in self.completed_items
            )
            if not completed:
                return False
        
        return True
    
    async def _calculate_timing_score(self, item: QueuedContent, current_time: datetime) -> float:
        """Calculate timing optimization score for an item"""
        score = 0.5  # Base score
        
        # Priority boost
        priority_boost = {
            QueuePriority.CRITICAL: 1.0,
            QueuePriority.HIGH: 0.8,
            QueuePriority.NORMAL: 0.6,
            QueuePriority.LOW: 0.4,
            QueuePriority.BATCH: 0.2
        }
        score += priority_boost.get(item.priority, 0.5)
        
        # Time-based scoring
        if item.scheduled_time:
            time_diff = abs((item.scheduled_time - current_time).total_seconds())
            # Prefer items closer to their scheduled time
            if time_diff < 300:  # Within 5 minutes
                score += 0.3
            elif time_diff < 1800:  # Within 30 minutes
                score += 0.2
            elif time_diff < 3600:  # Within 1 hour
                score += 0.1
        
        # Content type boost
        content_type_boost = {
            "live_stream": 0.4,
            "breaking_news": 0.3,
            "video": 0.2,
            "image": 0.1,
            "text": 0.0
        }
        score += content_type_boost.get(item.content_type, 0.0)
        
        # Age penalty (older items get slight boost)
        age_hours = (current_time - item.created_at).total_seconds() / 3600
        if age_hours > 24:
            score += 0.1
        
        return min(score, 2.0)  # Cap at 2.0
    
    async def _calculate_engagement_score(self, item: QueuedContent) -> float:
        """Calculate engagement potential score for an item"""
        score = 0.5  # Base score
        
        # Content type engagement multipliers
        engagement_multipliers = {
            "video": 1.3,
            "live_stream": 1.5,
            "image": 1.1,
            "poll": 1.4,
            "story": 1.2,
            "text": 1.0
        }
        score *= engagement_multipliers.get(item.content_type, 1.0)
        
        # Platform engagement factors
        platform_factors = {
            "tiktok": 1.4,
            "instagram": 1.3,
            "youtube": 1.2,
            "twitter": 1.1,
            "linkedin": 0.9,
            "facebook": 1.0
        }
        score *= platform_factors.get(item.platform.lower(), 1.0)
        
        # Tags boost
        if "trending" in item.tags:
            score += 0.2
        if "viral" in item.tags:
            score += 0.3
        if "exclusive" in item.tags:
            score += 0.1
        
        # Priority consideration
        priority_multiplier = {
            QueuePriority.CRITICAL: 1.2,
            QueuePriority.HIGH: 1.1,
            QueuePriority.NORMAL: 1.0,
            QueuePriority.LOW: 0.9,
            QueuePriority.BATCH: 0.8
        }
        score *= priority_multiplier.get(item.priority, 1.0)
        
        return score
    
    async def optimize_queue(self, queue_name: str = "default") -> QueueOptimization:
        """Optimize queue order using AI algorithms"""
        try:
            if queue_name not in self.queues:
                raise ValueError(f"Queue {queue_name} not found")
            
            original_queue = self.queues[queue_name].copy()
            queued_items = [item for item in original_queue if item.status == ContentStatus.QUEUED]
            
            if not queued_items:
                return QueueOptimization(
                    reordered_queue=original_queue,
                    estimated_completion_time=datetime.now(timezone.utc),
                    optimization_score=1.0,
                    reasoning=["No items in queue to optimize"],
                    resource_allocation={},
                    bottlenecks_identified=[]
                )
            
            # Create optimization score for original order
            original_score = await self._calculate_queue_score(queued_items)
            
            # Try different optimization strategies
            strategies = [
                self._optimize_by_priority,
                self._optimize_by_timing,
                self._optimize_by_dependencies,
                self._optimize_by_platform_batching
            ]
            
            best_order = queued_items.copy()
            best_score = original_score
            best_reasoning = []
            
            for strategy in strategies:
                optimized_order, reasoning = await strategy(queued_items.copy())
                score = await self._calculate_queue_score(optimized_order)
                
                if score > best_score:
                    best_order = optimized_order
                    best_score = score
                    best_reasoning = reasoning
            
            # Calculate estimated completion time
            estimated_completion = await self._estimate_completion_time(best_order)
            
            # Identify bottlenecks
            bottlenecks = await self._identify_bottlenecks(best_order)
            
            # Calculate resource allocation
            resource_allocation = await self._calculate_resource_allocation(best_order)
            
            # Update queue with optimized order
            self.queues[queue_name] = best_order + [
                item for item in original_queue 
                if item.status != ContentStatus.QUEUED
            ]
            
            self.last_optimization = datetime.now(timezone.utc)
            
            return QueueOptimization(
                reordered_queue=best_order,
                estimated_completion_time=estimated_completion,
                optimization_score=best_score / max(original_score, 0.1),
                reasoning=best_reasoning,
                resource_allocation=resource_allocation,
                bottlenecks_identified=bottlenecks
            )
            
        except Exception as e:
            logger.error(f"Failed to optimize queue: {e}")
            raise
    
    async def _calculate_queue_score(self, queue: List[QueuedContent]) -> float:
        """Calculate overall score for queue order"""
        if not queue:
            return 0.0
        
        total_score = 0.0
        
        for i, item in enumerate(queue):
            # Position penalty (later positions get slight penalty)
            position_factor = max(0.1, 1.0 - (i * 0.05))
            
            # Priority score
            priority_score = {
                QueuePriority.CRITICAL: 5.0,
                QueuePriority.HIGH: 4.0,
                QueuePriority.NORMAL: 3.0,
                QueuePriority.LOW: 2.0,
                QueuePriority.BATCH: 1.0
            }.get(item.priority, 3.0)
            
            # Time relevance score
            time_score = 1.0
            if item.scheduled_time:
                current_time = datetime.now(timezone.utc)
                time_diff = abs((item.scheduled_time - current_time).total_seconds())
                if time_diff < 3600:  # Within 1 hour
                    time_score = 2.0
                elif time_diff < 86400:  # Within 1 day
                    time_score = 1.5
            
            item_score = priority_score * position_factor * time_score
            total_score += item_score
        
        return total_score / len(queue)
    
    async def _optimize_by_priority(self, queue: List[QueuedContent]) -> Tuple[List[QueuedContent], List[str]]:
        """Optimize queue by priority"""
        queue.sort(key=lambda x: (x.priority.value, x.created_at))
        return queue, ["Optimized by priority and creation time"]
    
    async def _optimize_by_timing(self, queue: List[QueuedContent]) -> Tuple[List[QueuedContent], List[str]]:
        """Optimize queue by scheduled timing"""
        current_time = datetime.now(timezone.utc)
        
        # Separate items with and without scheduled times
        scheduled = [item for item in queue if item.scheduled_time]
        unscheduled = [item for item in queue if not item.scheduled_time]
        
        # Sort scheduled items by time
        scheduled.sort(key=lambda x: x.scheduled_time)
        
        # Sort unscheduled by priority
        unscheduled.sort(key=lambda x: x.priority.value)
        
        optimized = scheduled + unscheduled
        return optimized, ["Optimized by scheduled time and priority"]
    
    async def _optimize_by_dependencies(self, queue: List[QueuedContent]) -> Tuple[List[QueuedContent], List[str]]:
        """Optimize queue by resolving dependencies"""
        # Topological sort for dependency resolution
        dependency_graph = {}
        in_degree = {}
        
        for item in queue:
            dependency_graph[item.id] = item.dependencies.copy()
            in_degree[item.id] = len(item.dependencies)
        
        # Kahn's algorithm for topological sorting
        result = []
        queue_zero = [item for item in queue if in_degree[item.id] == 0]
        
        while queue_zero:
            current = queue_zero.pop(0)
            result.append(current)
            
            # Update in-degrees
            for item in queue:
                if current.id in dependency_graph[item.id]:
                    in_degree[item.id] -= 1
                    if in_degree[item.id] == 0:
                        queue_zero.append(item)
        
        # Add remaining items (circular dependencies)
        remaining = [item for item in queue if item not in result]
        result.extend(remaining)
        
        return result, ["Optimized by dependency resolution"]
    
    async def _optimize_by_platform_batching(self, queue: List[QueuedContent]) -> Tuple[List[QueuedContent], List[str]]:
        """Optimize queue by batching similar platforms"""
        platform_groups = {}
        
        for item in queue:
            if item.platform not in platform_groups:
                platform_groups[item.platform] = []
            platform_groups[item.platform].append(item)
        
        # Sort each platform group by priority
        for platform_items in platform_groups.values():
            platform_items.sort(key=lambda x: x.priority.value)
        
        # Interleave platforms to avoid bottlenecks
        result = []
        platform_iterators = {
            platform: iter(items) 
            for platform, items in platform_groups.items()
        }
        
        while platform_iterators:
            for platform in list(platform_iterators.keys()):
                try:
                    item = next(platform_iterators[platform])
                    result.append(item)
                except StopIteration:
                    del platform_iterators[platform]
        
        return result, ["Optimized by platform batching to avoid rate limits"]
    
    async def _estimate_completion_time(self, queue: List[QueuedContent]) -> datetime:
        """Estimate completion time for queue"""
        current_time = datetime.now(timezone.utc)
        
        # Estimate processing time per item (configurable)
        avg_processing_time = 30  # seconds per item
        
        total_time = len(queue) * avg_processing_time
        
        # Add buffer for rate limits and retries
        buffer_multiplier = 1.5
        total_time *= buffer_multiplier
        
        return current_time + timedelta(seconds=total_time)
    
    async def _identify_bottlenecks(self, queue: List[QueuedContent]) -> List[str]:
        """Identify potential bottlenecks in queue"""
        bottlenecks = []
        
        # Platform concentration bottleneck
        platform_counts = {}
        for item in queue:
            platform_counts[item.platform] = platform_counts.get(item.platform, 0) + 1
        
        for platform, count in platform_counts.items():
            if count > len(queue) * 0.5:  # More than 50% of queue
                bottlenecks.append(f"High concentration on {platform} platform")
        
        # Large file processing bottleneck
        large_items = [
            item for item in queue 
            if item.content_type in ["video", "audio"] and 
               item.estimated_duration and item.estimated_duration > 300
        ]
        
        if len(large_items) > 3:
            bottlenecks.append("Multiple large files may cause processing delays")
        
        # Dependency chain bottleneck
        max_dependencies = max(len(item.dependencies) for item in queue) if queue else 0
        if max_dependencies > 5:
            bottlenecks.append("Complex dependency chains detected")
        
        return bottlenecks
    
    async def _calculate_resource_allocation(self, queue: List[QueuedContent]) -> Dict[str, int]:
        """Calculate optimal resource allocation"""
        platform_counts = {}
        for item in queue:
            platform_counts[item.platform] = platform_counts.get(item.platform, 0) + 1
        
        total_items = len(queue)
        if total_items == 0:
            return {}
        
        # Allocate processors proportionally
        max_processors = self.max_concurrent_processing
        allocation = {}
        
        for platform, count in platform_counts.items():
            proportion = count / total_items
            allocated = max(1, int(max_processors * proportion))
            allocation[platform] = allocated
        
        return allocation
    
    async def _check_optimization_trigger(self) -> None:
        """Check if queue optimization should be triggered"""
        time_since_last = datetime.now(timezone.utc) - self.last_optimization
        
        if time_since_last > self.queue_optimization_interval:
            # Auto-optimize all queues
            for queue_name in self.queues.keys():
                try:
                    await self.optimize_queue(queue_name)
                except Exception as e:
                    logger.error(f"Auto-optimization failed for {queue_name}: {e}")
    
    async def get_queue_status(self, queue_name: str = "default") -> QueueMetrics:
        """Get current queue status and metrics"""
        if queue_name not in self.queues:
            return QueueMetrics(
                total_items=0, queued_items=0, processing_items=0,
                completed_items=0, failed_items=0, average_wait_time=0.0,
                average_processing_time=0.0, success_rate=0.0,
                throughput_per_hour=0.0, peak_queue_length=0, current_load=0.0
            )
        
        queue = self.queues[queue_name]
        
        # Count items by status
        queued = len([item for item in queue if item.status == ContentStatus.QUEUED])
        processing = len([item for item in queue if item.status == ContentStatus.PROCESSING])
        completed = len([item for item in queue if item.status == ContentStatus.PUBLISHED])
        failed = len([item for item in queue if item.status == ContentStatus.FAILED])
        
        total = len(queue)
        success_rate = (completed / max(total, 1)) * 100
        
        # Calculate averages (simplified)
        avg_wait_time = 120.0  # Default 2 minutes
        avg_processing_time = 30.0  # Default 30 seconds
        throughput = completed / max(1, (datetime.now(timezone.utc) - 
                                       min(item.created_at for item in queue) if queue else datetime.now(timezone.utc)
                                      ).total_seconds() / 3600)
        
        current_load = processing / max(self.max_concurrent_processing, 1)
        
        return QueueMetrics(
            total_items=total,
            queued_items=queued,
            processing_items=processing,
            completed_items=completed,
            failed_items=failed,
            average_wait_time=avg_wait_time,
            average_processing_time=avg_processing_time,
            success_rate=success_rate,
            throughput_per_hour=throughput,
            peak_queue_length=total,  # Simplified
            current_load=current_load
        )
    
    def add_processor(self, platform -> None: str, processor -> None: QueueProcessor) -> None:
        """Add a queue processor for a specific platform"""
        self.processors[platform] = processor
        logger.info(f"Added processor for {platform}")
    
    def remove_processor(self, platform -> None: str) -> None:
        """Remove a queue processor"""
        if platform in self.processors:
            del self.processors[platform]
            logger.info(f"Removed processor for {platform}")


# Export main components
__all__ = [
    "QueueIntelligence",
    "QueuedContent",
    "QueueMetrics", 
    "QueueOptimization",
    "QueueProcessor",
    "PlatformQueueProcessor",
    "QueuePriority",
    "ContentStatus",
    "QueueStrategy"
]