"""IA Influencer Agent - Real-time Stream Processor
Complex Event Processing and Real-time Stream Processing for Ainflue Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Callable, Union, AsyncGenerator, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import json
import logging
import time
import statistics
from uuid import uuid4
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Stream processing modes"""
    AT_LEAST_ONCE = "at_least_once"
    AT_MOST_ONCE = "at_most_once"
    EXACTLY_ONCE = "exactly_once"


class StreamJoinType(Enum):
    """Stream join types"""
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    FULL = "full"


class AggregationType(Enum):
    """Aggregation types"""
    COUNT = "count"
    SUM = "sum"
    AVG = "average"
    MIN = "minimum"
    MAX = "maximum"
    DISTINCT_COUNT = "distinct_count"
    PERCENTILE = "percentile"


@dataclass
class StreamEvent:
    """Stream event structure"""
    
    event_id: str
    stream_name: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    processing_timestamp: Optional[datetime] = None
    watermark: Optional[datetime] = None
    partition_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProcessingContext:
    """Context for stream processing"""
    
    processing_time: datetime
    event_time: datetime
    watermark: datetime
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Result of stream processing"""
    
    output_events: List[StreamEvent] = field(default_factory=list)
    state_updates: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    should_continue: bool = True


class StreamProcessor(ABC):
    """Abstract base class for stream processors"""
    
    @abstractmethod
    async def process(self, event: StreamEvent, context: ProcessingContext) -> ProcessingResult:
        """Process a stream event"""
        pass
    
    @abstractmethod
    async def initialize_state(self) -> Dict[str, Any]:
        """Initialize processor state"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup processor resources"""
        pass


class ContentUploadStreamProcessor(StreamProcessor):
    """Processor for Ainflue content upload events"""
    
    def __init__(self) -> None:
        self.state = {}
        self.creator_stats = defaultdict(lambda: {"upload_count": 0, "total_size": 0})
        
    async def initialize_state(self) -> Dict[str, Any]:
        """Initialize content upload processor state"""
        self.state = {
            "total_uploads": 0,
            "uploads_by_type": defaultdict(int),
            "processing_start_time": datetime.now(timezone.utc)
        }
        return self.state
    
    async def process(self, event: StreamEvent, context: ProcessingContext) -> ProcessingResult:
        """Process content upload event"""
        try:
            payload = event.payload
            creator_id = payload.get("creator_id")
            content_type = payload.get("content_type")
            content_size = payload.get("content_size", 0)
            
            # Update state
            self.state["total_uploads"] += 1
            self.state["uploads_by_type"][content_type] += 1
            
            # Update creator stats
            self.creator_stats[creator_id]["upload_count"] += 1
            self.creator_stats[creator_id]["total_size"] += content_size
            
            # Generate processing events
            output_events = []
            
            # Trigger AI analysis request
            ai_analysis_event = StreamEvent(
                event_id=str(uuid4()),
                stream_name="ai-analysis-requests",
                event_type="ainflue.content.ai.analysis.requested",
                payload={
                    "content_id": payload.get("content_id"),
                    "creator_id": creator_id,
                    "content_type": content_type,
                    "analysis_priority": self._calculate_analysis_priority(creator_id),
                    "original_event_id": event.event_id
                },
                timestamp=context.processing_time,
                partition_key=creator_id
            )
            output_events.append(ai_analysis_event)
            
            # Check if creator is trending
            if self._is_creator_trending(creator_id):
                trending_event = StreamEvent(
                    event_id=str(uuid4()),
                    stream_name="trending-creators",
                    event_type="ainflue.creator.trending.detected",
                    payload={
                        "creator_id": creator_id,
                        "upload_count_24h": self.creator_stats[creator_id]["upload_count"],
                        "trend_score": self._calculate_trend_score(creator_id)
                    },
                    timestamp=context.processing_time,
                    partition_key=creator_id
                )
                output_events.append(trending_event)
            
            return ProcessingResult(
                output_events=output_events,
                state_updates={"total_uploads": self.state["total_uploads"]},
                metrics={
                    "processing_latency_ms": (context.processing_time - event.timestamp).total_seconds() * 1000,
                    "content_size_bytes": content_size
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing content upload event: {e}")
            return ProcessingResult(should_continue=False)
    
    def _calculate_analysis_priority(self, creator_id: str) -> str:
        """Calculate AI analysis priority based on creator stats"""
        upload_count = self.creator_stats[creator_id]["upload_count"]
        
        if upload_count > 100:
            return "high"
        elif upload_count > 20:
            return "medium"
        else:
            return "low"
    
    def _is_creator_trending(self, creator_id: str) -> bool:
        """Check if creator is trending based on upload frequency"""
        upload_count = self.creator_stats[creator_id]["upload_count"]
        return upload_count > 5  # Simple trending threshold
    
    def _calculate_trend_score(self, creator_id: str) -> float:
        """Calculate trending score for creator"""
        stats = self.creator_stats[creator_id]
        return min(100.0, stats["upload_count"] * 10.0)  # Simple score calculation
    
    async def cleanup(self) -> None:
        """Cleanup content upload processor"""
        self.state.clear()
        self.creator_stats.clear()


class CollaborationMatchingProcessor(StreamProcessor):
    """Processor for collaboration matching events"""
    
    def __init__(self) -> None:
        self.state = {}
        self.creator_profiles = {}
        self.match_history = defaultdict(list)
        
    async def initialize_state(self) -> Dict[str, Any]:
        """Initialize collaboration matching processor state"""
        self.state = {
            "total_matches": 0,
            "successful_collaborations": 0,
            "matching_accuracy": 0.0
        }
        return self.state
    
    async def process(self, event: StreamEvent, context: ProcessingContext) -> ProcessingResult:
        """Process collaboration matching event"""
        try:
            payload = event.payload
            requester_id = payload.get("requester_id")
            target_categories = payload.get("target_categories", [])
            collaboration_type = payload.get("collaboration_type")
            
            # Find potential matches
            matches = await self._find_collaboration_matches(
                requester_id, target_categories, collaboration_type
            )
            
            output_events = []
            
            for match in matches:
                match_event = StreamEvent(
                    event_id=str(uuid4()),
                    stream_name="collaboration-matches",
                    event_type="ainflue.collaboration.match.found",
                    payload={
                        "requester_id": requester_id,
                        "matched_creator_id": match["creator_id"],
                        "compatibility_score": match["score"],
                        "match_reasons": match["reasons"],
                        "collaboration_type": collaboration_type,
                        "original_request_id": event.event_id
                    },
                    timestamp=context.processing_time,
                    partition_key=requester_id
                )
                output_events.append(match_event)
            
            # Update state
            self.state["total_matches"] += len(matches)
            
            return ProcessingResult(
                output_events=output_events,
                state_updates={"total_matches": self.state["total_matches"]},
                metrics={
                    "matches_found": len(matches),
                    "avg_compatibility_score": statistics.mean([m["score"] for m in matches]) if matches else 0.0
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing collaboration matching event: {e}")
            return ProcessingResult(should_continue=False)
    
    async def _find_collaboration_matches(self, 
                                        requester_id: str, 
                                        target_categories: List[str], 
                                        collaboration_type: str) -> List[Dict[str, Any]]:
        """Find collaboration matches using ML algorithm simulation"""
        try:
            # Simulate ML-based matching
            matches = []
            
            # Mock creator database
            mock_creators = [
                {"creator_id": f"creator_{i}", "categories": ["music", "lifestyle"], "score": 0.8 + (i % 3) * 0.1}
                for i in range(5)
            ]
            
            for creator in mock_creators:
                if creator["creator_id"] != requester_id:
                    # Calculate compatibility score
                    category_overlap = len(set(creator["categories"]) & set(target_categories))
                    compatibility_score = min(1.0, creator["score"] + (category_overlap * 0.2))
                    
                    if compatibility_score > 0.7:  # Threshold for good match
                        matches.append({
                            "creator_id": creator["creator_id"],
                            "score": compatibility_score,
                            "reasons": ["category_match", "engagement_score", "collaboration_history"]
                        })
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x["score"], reverse=True)
            
            return matches[:3]  # Return top 3 matches
            
        except Exception as e:
            logger.error(f"Error finding collaboration matches: {e}")
            return []
    
    async def cleanup(self) -> None:
        """Cleanup collaboration matching processor"""
        self.state.clear()
        self.creator_profiles.clear()
        self.match_history.clear()


class RevenueAnalyticsProcessor(StreamProcessor):
    """Processor for real-time revenue analytics"""
    
    def __init__(self) -> None:
        self.state = {}
        self.revenue_buckets = defaultdict(float)
        self.hourly_revenue = deque(maxlen=24)  # Last 24 hours
        
    async def initialize_state(self) -> Dict[str, Any]:
        """Initialize revenue analytics processor state"""
        self.state = {
            "total_revenue": 0.0,
            "revenue_by_creator": defaultdict(float),
            "revenue_by_hour": defaultdict(float),
            "top_earning_creators": []
        }
        return self.state
    
    async def process(self, event: StreamEvent, context: ProcessingContext) -> ProcessingResult:
        """Process revenue analytics event"""
        try:
            payload = event.payload
            creator_id = payload.get("creator_id")
            revenue_amount = float(payload.get("amount", 0))
            revenue_type = payload.get("revenue_type")
            
            # Update state
            self.state["total_revenue"] += revenue_amount
            self.state["revenue_by_creator"][creator_id] += revenue_amount
            
            # Update hourly revenue
            current_hour = context.processing_time.replace(minute=0, second=0, microsecond=0)
            self.state["revenue_by_hour"][current_hour.isoformat()] += revenue_amount
            
            output_events = []
            
            # Generate analytics events
            analytics_event = StreamEvent(
                event_id=str(uuid4()),
                stream_name="revenue-analytics",
                event_type="ainflue.revenue.analytics.updated",
                payload={
                    "creator_id": creator_id,
                    "revenue_amount": revenue_amount,
                    "revenue_type": revenue_type,
                    "creator_total_revenue": self.state["revenue_by_creator"][creator_id],
                    "platform_total_revenue": self.state["total_revenue"],
                    "timestamp": context.processing_time.isoformat()
                },
                timestamp=context.processing_time,
                partition_key=creator_id
            )
            output_events.append(analytics_event)
            
            # Check for revenue milestones
            creator_total = self.state["revenue_by_creator"][creator_id]
            if self._is_revenue_milestone(creator_total):
                milestone_event = StreamEvent(
                    event_id=str(uuid4()),
                    stream_name="revenue-milestones",
                    event_type="ainflue.revenue.milestone.reached",
                    payload={
                        "creator_id": creator_id,
                        "milestone_amount": self._get_milestone_amount(creator_total),
                        "total_revenue": creator_total,
                        "achievement_timestamp": context.processing_time.isoformat()
                    },
                    timestamp=context.processing_time,
                    partition_key=creator_id
                )
                output_events.append(milestone_event)
            
            return ProcessingResult(
                output_events=output_events,
                state_updates={
                    "total_revenue": self.state["total_revenue"],
                    "creator_revenue": self.state["revenue_by_creator"][creator_id]
                },
                metrics={
                    "revenue_amount": revenue_amount,
                    "revenue_processing_latency_ms": (context.processing_time - event.timestamp).total_seconds() * 1000
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing revenue analytics event: {e}")
            return ProcessingResult(should_continue=False)
    
    def _is_revenue_milestone(self, total_revenue: float) -> bool:
        """Check if total revenue reached a milestone"""
        milestones = [100, 500, 1000, 5000, 10000, 50000, 100000]
        
        for milestone in milestones:
            if total_revenue >= milestone and (total_revenue - milestone) < 100:  # Recently crossed
                return True
        
        return False
    
    def _get_milestone_amount(self, total_revenue: float) -> float:
        """Get the milestone amount that was just reached"""
        milestones = [100, 500, 1000, 5000, 10000, 50000, 100000]
        
        for milestone in reversed(milestones):
            if total_revenue >= milestone:
                return milestone
        
        return 0
    
    async def cleanup(self) -> None:
        """Cleanup revenue analytics processor"""
        self.state.clear()
        self.revenue_buckets.clear()
        self.hourly_revenue.clear()


class StreamJoinProcessor:
    """Processor for joining multiple streams"""
    
    def __init__(self, 
                 left_stream -> None: str, 
                 right_stream -> None: str, 
                 join_type -> None: StreamJoinType,
                 join_key_extractor -> None: Callable[[StreamEvent], str],
                 window_duration -> None: timedelta) -> None:
        self.left_stream = left_stream
        self.right_stream = right_stream
        self.join_type = join_type
        self.join_key_extractor = join_key_extractor
        self.window_duration = window_duration
        self.left_buffer: Dict[str, List[StreamEvent]] = defaultdict(list)
        self.right_buffer: Dict[str, List[StreamEvent]] = defaultdict(list)
        
    async def process_event(self, event: StreamEvent, context: ProcessingContext) -> List[StreamEvent]:
        """Process event for stream join"""
        try:
            join_key = self.join_key_extractor(event)
            
            if event.stream_name == self.left_stream:
                # Store in left buffer
                self.left_buffer[join_key].append(event)
                
                # Find matching events in right buffer
                matches = self.right_buffer.get(join_key, [])
                
            elif event.stream_name == self.right_stream:
                # Store in right buffer
                self.right_buffer[join_key].append(event)
                
                # Find matching events in left buffer
                matches = self.left_buffer.get(join_key, [])
            else:
                return []
            
            # Generate join results
            join_results = []
            
            for match_event in matches:
                # Check if events are within time window
                time_diff = abs((event.timestamp - match_event.timestamp).total_seconds())
                
                if time_diff <= self.window_duration.total_seconds():
                    joined_event = self._create_joined_event(event, match_event, context)
                    join_results.append(joined_event)
            
            # Clean old events from buffers
            await self._cleanup_old_events(context.processing_time)
            
            return join_results
            
        except Exception as e:
            logger.error(f"Error processing stream join: {e}")
            return []
    
    def _create_joined_event(self, left_event: StreamEvent, right_event: StreamEvent, context: ProcessingContext) -> StreamEvent:
        """Create joined event from two matching events"""
        joined_payload = {
            "left_event": {
                "event_id": left_event.event_id,
                "stream_name": left_event.stream_name,
                "event_type": left_event.event_type,
                "payload": left_event.payload,
                "timestamp": left_event.timestamp.isoformat()
            },
            "right_event": {
                "event_id": right_event.event_id,
                "stream_name": right_event.stream_name,
                "event_type": right_event.event_type,
                "payload": right_event.payload,
                "timestamp": right_event.timestamp.isoformat()
            },
            "join_timestamp": context.processing_time.isoformat()
        }
        
        return StreamEvent(
            event_id=str(uuid4()),
            stream_name=f"{self.left_stream}_{self.right_stream}_joined",
            event_type="stream.join.result",
            payload=joined_payload,
            timestamp=context.processing_time,
            partition_key=self.join_key_extractor(left_event)
        )
    
    async def _cleanup_old_events(self, current_time -> None: datetime) -> None:
        """Remove events older than window duration"""
        cutoff_time = current_time - self.window_duration
        
        # Clean left buffer
        for key in list(self.left_buffer.keys()):
            self.left_buffer[key] = [
                event for event in self.left_buffer[key]
                if event.timestamp > cutoff_time
            ]
            if not self.left_buffer[key]:
                del self.left_buffer[key]
        
        # Clean right buffer
        for key in list(self.right_buffer.keys()):
            self.right_buffer[key] = [
                event for event in self.right_buffer[key]
                if event.timestamp > cutoff_time
            ]
            if not self.right_buffer[key]:
                del self.right_buffer[key]


class RealtimeStreamProcessor:
    """Main real-time stream processing engine"""
    
    def __init__(self, metrics_collector=None) -> None:
        self.metrics_collector = metrics_collector
        self.processors: Dict[str, StreamProcessor] = {}
        self.join_processors: List[StreamJoinProcessor] = []
        self.processing_topology: Dict[str, List[str]] = {}
        self.state_store: Dict[str, Any] = {}
        self._processor_tasks: Dict[str, asyncio.Task] = {}
        self._shutdown_event = asyncio.Event()
        
    async def start(self) -> None:
        """Start the real-time stream processor"""
        try:
            logger.info("Starting Real-time Stream Processor")
            
            # Initialize default processors for Ainflue
            await self._setup_default_processors()
            
            # Initialize processor states
            for name, processor in self.processors.items():
                self.state_store[name] = await processor.initialize_state()
            
            logger.info("Real-time Stream Processor started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start real-time stream processor: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the stream processor"""
        try:
            logger.info("Stopping Real-time Stream Processor")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop all processor tasks
            for task in self._processor_tasks.values():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Cleanup processors
            for processor in self.processors.values():
                await processor.cleanup()
            
            logger.info("Real-time Stream Processor stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping real-time stream processor: {e}")
            raise
    
    async def _setup_default_processors(self) -> None:
        """Setup default processors for Ainflue platform"""
        try:
            # Content upload processor
            self.processors["content_upload"] = ContentUploadStreamProcessor()
            
            # Collaboration matching processor
            self.processors["collaboration_matching"] = CollaborationMatchingProcessor()
            
            # Revenue analytics processor
            self.processors["revenue_analytics"] = RevenueAnalyticsProcessor()
            
            # Setup processing topology
            self.processing_topology = {
                "content-uploads": ["content_upload"],
                "collaboration-requests": ["collaboration_matching"],
                "revenue-events": ["revenue_analytics"]
            }
            
            logger.info("Setup default processors for Ainflue platform")
            
        except Exception as e:
            logger.error(f"Error setting up default processors: {e}")
            raise
    
    async def process_event(self, event: StreamEvent) -> List[StreamEvent]:
        """Process a single stream event"""
        try:
            start_time = time.time()
            
            # Create processing context
            context = ProcessingContext(
                processing_time=datetime.now(timezone.utc),
                event_time=event.timestamp,
                watermark=event.watermark or event.timestamp
            )
            
            # Find processors for this stream
            processor_names = self.processing_topology.get(event.stream_name, [])
            
            all_output_events = []
            
            # Process with each configured processor
            for processor_name in processor_names:
                processor = self.processors.get(processor_name)
                if processor:
                    try:
                        result = await processor.process(event, context)
                        
                        if result.should_continue:
                            all_output_events.extend(result.output_events)
                            
                            # Update state store
                            if result.state_updates:
                                self.state_store[processor_name].update(result.state_updates)
                            
                            # Collect metrics
                            if self.metrics_collector and result.metrics:
                                for metric_name, value in result.metrics.items():
                                    self.metrics_collector.histogram(f"stream_processor_{metric_name}", value)
                        else:
                            logger.warning(f"Processor {processor_name} signaled to stop processing")
                            
                    except Exception as e:
                        logger.error(f"Error in processor {processor_name}: {e}")
                        if self.metrics_collector:
                            self.metrics_collector.increment_counter("stream_processing_errors")
            
            # Process with join processors
            for join_processor in self.join_processors:
                join_results = await join_processor.process_event(event, context)
                all_output_events.extend(join_results)
            
            # Update processing metrics
            processing_latency = (time.time() - start_time) * 1000
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("stream_events_processed")
                self.metrics_collector.histogram("stream_processing_latency", processing_latency)
            
            logger.debug(f"Processed event {event.event_id} in {processing_latency:.2f}ms, generated {len(all_output_events)} output events")
            
            return all_output_events
            
        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("stream_processing_errors")
            return []
    
    async def add_processor(self, name -> None: str, processor -> None: StreamProcessor, streams -> None: List[str]) -> None:
        """Add a new stream processor"""
        try:
            self.processors[name] = processor
            self.state_store[name] = await processor.initialize_state()
            
            # Update topology
            for stream in streams:
                if stream not in self.processing_topology:
                    self.processing_topology[stream] = []
                self.processing_topology[stream].append(name)
            
            logger.info(f"Added processor {name} for streams {streams}")
            
        except Exception as e:
            logger.error(f"Error adding processor {name}: {e}")
            raise
    
    async def add_join_processor(self, 
                                left_stream -> None: str, 
                                right_stream -> None: str, 
                                join_type -> None: StreamJoinType,
                                join_key_extractor -> None: Callable[[StreamEvent], str],
                                window_duration -> None: timedelta) -> None:
        """Add a stream join processor"""
        try:
            join_processor = StreamJoinProcessor(
                left_stream, right_stream, join_type, 
                join_key_extractor, window_duration
            )
            
            self.join_processors.append(join_processor)
            
            logger.info(f"Added join processor for {left_stream} and {right_stream}")
            
        except Exception as e:
            logger.error(f"Error adding join processor: {e}")
            raise
    
    def get_processor_metrics(self) -> Dict[str, Any]:
        """Get comprehensive processor metrics"""
        try:
            metrics = {
                "total_processors": len(self.processors),
                "total_join_processors": len(self.join_processors),
                "processing_topology": self.processing_topology,
                "processor_states": {}
            }
            
            # Get state from each processor
            for name, state in self.state_store.items():
                metrics["processor_states"][name] = state
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting processor metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "RealtimeStreamProcessor", "StreamProcessor", "StreamEvent", "ProcessingContext",
    "ProcessingResult", "ContentUploadStreamProcessor", "CollaborationMatchingProcessor",
    "RevenueAnalyticsProcessor", "StreamJoinProcessor", "ProcessingMode", "StreamJoinType",
    "AggregationType"
]