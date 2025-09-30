"""IA Influencer Agent - Windowing Computation Engine
Advanced Time-Windowed Computations for Ainflue Event Streaming Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Callable, Union, Tuple, Iterator
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import json
import logging
import time
import bisect
from uuid import uuid4
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class WindowAlignment(Enum):
    """Window alignment options"""
    EPOCH = "epoch"
    PROCESSING_TIME = "processing_time"
    EVENT_TIME = "event_time"
    CUSTOM = "custom"


class WatermarkStrategy(Enum):
    """Watermark generation strategies"""
    BOUNDED_OUT_OF_ORDERNESS = "bounded_out_of_orderness"
    PERIODIC = "periodic"
    PUNCTUATED = "punctuated"
    ASCENDING_TIMESTAMPS = "ascending_timestamps"


class TriggerType(Enum):
    """Window trigger types"""
    PROCESSING_TIME = "processing_time"
    EVENT_TIME = "event_time"
    COUNT = "count"
    CUSTOM = "custom"


class AinflueBusinesWindowTypes:
    """Business-specific window types for Ainflue platform"""
    
    # Content analytics windows
    CONTENT_ENGAGEMENT_WINDOW = {
        "type": "tumbling",
        "duration": timedelta(minutes=15),
        "aligned_to": "epoch"
    }
    
    CREATOR_ACTIVITY_WINDOW = {
        "type": "sliding",
        "duration": timedelta(hours=1),
        "step": timedelta(minutes=10)
    }
    
    # Revenue windows
    REVENUE_REPORTING_WINDOW = {
        "type": "tumbling",
        "duration": timedelta(days=1),
        "aligned_to": "midnight"
    }
    
    COMMISSION_CALCULATION_WINDOW = {
        "type": "tumbling",
        "duration": timedelta(weeks=1),
        "aligned_to": "monday"
    }
    
    # Collaboration windows
    MATCHING_PERFORMANCE_WINDOW = {
        "type": "sliding",
        "duration": timedelta(hours=2),
        "step": timedelta(minutes=30)
    }
    
    COLLABORATION_SUCCESS_WINDOW = {
        "type": "session",
        "timeout": timedelta(minutes=30)
    }
    
    # SEO optimization windows
    SEO_PERFORMANCE_WINDOW = {
        "type": "tumbling",
        "duration": timedelta(hours=6)
    }
    
    SEARCH_TRENDING_WINDOW = {
        "type": "sliding",
        "duration": timedelta(hours=24),
        "step": timedelta(hours=1)
    }


@dataclass
class WindowEvent:
    """Event within a window"""
    
    event_id: str
    timestamp: datetime
    event_time: datetime
    payload: Dict[str, Any]
    watermark: Optional[datetime] = None
    late_arrival: bool = False


@dataclass
class WindowState:
    """State of a window"""
    
    window_id: str
    start_time: datetime
    end_time: datetime
    events: List[WindowEvent] = field(default_factory=list)
    state_data: Dict[str, Any] = field(default_factory=dict)
    watermark: Optional[datetime] = None
    triggered: bool = False
    closed: bool = False
    allowed_lateness: timedelta = timedelta(minutes=5)


@dataclass
class Trigger:
    """Window trigger configuration"""
    
    trigger_type: TriggerType
    condition: Any  # Condition for triggering (time, count, etc.)
    repeat: bool = False
    early_firing: bool = False
    late_firing: bool = True


@dataclass
class WindowResult:
    """Result of window computation"""
    
    window_id: str
    window_start: datetime
    window_end: datetime
    results: Dict[str, Any]
    event_count: int
    computation_time: datetime
    is_final: bool = False


class Window(ABC):
    """Abstract base class for windows"""
    
    def __init__(self, window_id: str, start_time: datetime, end_time: datetime):
        self.window_id = window_id
        self.start_time = start_time
        self.end_time = end_time
        self.state = WindowState(window_id, start_time, end_time)
    
    @abstractmethod
    def contains(self, event_time: datetime) -> bool:
        """Check if event time belongs to this window"""
        pass
    
    @abstractmethod
    def should_trigger(self, current_time: datetime, watermark: datetime) -> bool:
        """Check if window should be triggered"""
        pass
    
    def add_event(self, event: WindowEvent) -> bool:
        """Add event to window"""
        if self.contains(event.event_time):
            # Check for late arrivals
            if self.state.watermark and event.event_time < self.state.watermark:
                if (self.state.watermark - event.event_time) <= self.state.allowed_lateness:
                    event.late_arrival = True
                    self.state.events.append(event)
                    return True
                else:
                    logger.warning(f"Event too late for window {self.window_id}: {event.event_id}")
                    return False
            else:
                self.state.events.append(event)
                return True
        return False
    
    def get_events(self) -> List[WindowEvent]:
        """Get all events in window"""
        return self.state.events.copy()
    
    def update_watermark(self, watermark: datetime):
        """Update window watermark"""
        self.state.watermark = watermark


class TumblingWindow(Window):
    """Tumbling (fixed) window implementation"""
    
    def __init__(self, window_id: str, start_time: datetime, size: timedelta):
        end_time = start_time + size
        super().__init__(window_id, start_time, end_time)
        self.size = size
    
    def contains(self, event_time: datetime) -> bool:
        """Check if event belongs to this tumbling window"""
        return self.start_time <= event_time < self.end_time
    
    def should_trigger(self, current_time: datetime, watermark: datetime) -> bool:
        """Trigger when watermark passes window end"""
        return watermark >= self.end_time and not self.state.triggered


class SlidingWindow(Window):
    """Sliding window implementation"""
    
    def __init__(self, window_id: str, start_time: datetime, size: timedelta, slide: timedelta):
        end_time = start_time + size
        super().__init__(window_id, start_time, end_time)
        self.size = size
        self.slide = slide
    
    def contains(self, event_time: datetime) -> bool:
        """Check if event belongs to this sliding window"""
        return self.start_time <= event_time < self.end_time
    
    def should_trigger(self, current_time: datetime, watermark: datetime) -> bool:
        """Trigger when watermark passes window end"""
        return watermark >= self.end_time and not self.state.triggered


class SessionWindow(Window):
    """Session window implementation"""
    
    def __init__(self, window_id: str, start_time: datetime, session_timeout: timedelta):
        super().__init__(window_id, start_time, start_time)
        self.session_timeout = session_timeout
        self.last_event_time = start_time
    
    def contains(self, event_time: datetime) -> bool:
        """Check if event belongs to this session"""
        if not self.state.events:
            return True
        
        # Check if event is within session timeout
        return (event_time - self.last_event_time) <= self.session_timeout
    
    def add_event(self, event: WindowEvent) -> bool:
        """Add event and extend session window"""
        if self.contains(event.event_time):
            self.state.events.append(event)
            self.last_event_time = event.event_time
            
            # Extend window end time
            self.end_time = event.event_time + self.session_timeout
            self.state.end_time = self.end_time
            
            return True
        return False
    
    def should_trigger(self, current_time: datetime, watermark: datetime) -> bool:
        """Trigger when session times out"""
        return (watermark >= self.end_time or 
                (self.last_event_time and watermark - self.last_event_time >= self.session_timeout)) and not self.state.triggered


class GlobalWindow(Window):
    """Global window (never closes) implementation"""
    
    def __init__(self, window_id: str):
        # Global window spans from min to max datetime
        super().__init__(
            window_id, 
            datetime.min.replace(tzinfo=timezone.utc), 
            datetime.max.replace(tzinfo=timezone.utc)
        )
    
    def contains(self, event_time: datetime) -> bool:
        """Global window contains all events"""
        return True
    
    def should_trigger(self, current_time: datetime, watermark: datetime) -> bool:
        """Global window only triggers on explicit triggers"""
        return False


class WatermarkGenerator:
    """Generates watermarks for event streams"""
    
    def __init__(self, strategy: WatermarkStrategy, **kwargs):
        self.strategy = strategy
        self.max_out_of_orderness = kwargs.get('max_out_of_orderness', timedelta(seconds=30))
        self.periodic_interval = kwargs.get('periodic_interval', timedelta(seconds=10))
        self.last_watermark = datetime.min.replace(tzinfo=timezone.utc)
        self.last_event_time = datetime.min.replace(tzinfo=timezone.utc)
    
    def generate_watermark(self, event_time: datetime, processing_time: datetime) -> Optional[datetime]:
        """Generate watermark based on strategy"""
        try:
            if self.strategy == WatermarkStrategy.BOUNDED_OUT_OF_ORDERNESS:
                # Watermark = max event time - max out of orderness
                self.last_event_time = max(self.last_event_time, event_time)
                new_watermark = self.last_event_time - self.max_out_of_orderness
                
                if new_watermark > self.last_watermark:
                    self.last_watermark = new_watermark
                    return new_watermark
            
            elif self.strategy == WatermarkStrategy.PERIODIC:
                # Generate watermark periodically based on processing time
                if processing_time - self.last_watermark >= self.periodic_interval:
                    new_watermark = processing_time - self.max_out_of_orderness
                    self.last_watermark = new_watermark
                    return new_watermark
            
            elif self.strategy == WatermarkStrategy.ASCENDING_TIMESTAMPS:
                # Watermark = current event time (assumes ascending timestamps)
                if event_time > self.last_watermark:
                    self.last_watermark = event_time
                    return event_time
            
            elif self.strategy == WatermarkStrategy.PUNCTUATED:
                # Watermark embedded in events (custom logic)
                # Implementation depends on specific event structure
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating watermark: {e}")
            return None


class WindowAssigner:
    """Assigns events to windows"""
    
    def __init__(self, window_type: str, **config):
        self.window_type = window_type
        self.config = config
        self.windows: Dict[str, Window] = {}
    
    def assign_to_windows(self, event: WindowEvent) -> List[str]:
        """Assign event to appropriate windows"""
        try:
            window_ids = []
            
            if self.window_type == "tumbling":
                window_id = self._assign_to_tumbling_window(event)
                if window_id:
                    window_ids.append(window_id)
            
            elif self.window_type == "sliding":
                window_ids = self._assign_to_sliding_windows(event)
            
            elif self.window_type == "session":
                window_id = self._assign_to_session_window(event)
                if window_id:
                    window_ids.append(window_id)
            
            elif self.window_type == "global":
                window_id = self._assign_to_global_window(event)
                if window_id:
                    window_ids.append(window_id)
            
            return window_ids
            
        except Exception as e:
            logger.error(f"Error assigning event to windows: {e}")
            return []
    
    def _assign_to_tumbling_window(self, event: WindowEvent) -> Optional[str]:
        """Assign event to tumbling window"""
        try:
            duration = self.config.get('duration', timedelta(minutes=15))
            alignment = self.config.get('aligned_to', 'epoch')
            
            # Calculate window start based on alignment
            if alignment == 'epoch':
                epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
                window_number = int((event.event_time - epoch).total_seconds() // duration.total_seconds())
                window_start = epoch + timedelta(seconds=window_number * duration.total_seconds())
            elif alignment == 'midnight':
                # Align to midnight
                event_date = event.event_time.date()
                window_start = datetime.combine(event_date, datetime.min.time(), tzinfo=timezone.utc)
                while window_start + duration <= event.event_time:
                    window_start += duration
            else:
                # Default alignment to processing time
                window_start = event.event_time.replace(second=0, microsecond=0)
                window_start = window_start.replace(minute=(window_start.minute // duration.seconds) * (duration.seconds // 60))
            
            window_id = f"tumbling_{window_start.isoformat()}"
            
            # Create window if it doesn't exist
            if window_id not in self.windows:
                self.windows[window_id] = TumblingWindow(window_id, window_start, duration)
            
            return window_id
            
        except Exception as e:
            logger.error(f"Error in tumbling window assignment: {e}")
            return None
    
    def _assign_to_sliding_windows(self, event: WindowEvent) -> List[str]:
        """Assign event to sliding windows"""
        try:
            duration = self.config.get('duration', timedelta(hours=1))
            slide = self.config.get('step', timedelta(minutes=10))
            
            window_ids = []
            
            # Calculate all sliding windows that should contain this event
            # Find the first window that ends after the event time
            window_end = event.event_time + duration
            
            # Round down to slide boundary
            slide_seconds = slide.total_seconds()
            aligned_end = datetime.fromtimestamp(
                (window_end.timestamp() // slide_seconds) * slide_seconds,
                tz=timezone.utc
            )
            
            # Generate windows that contain this event
            current_end = aligned_end
            while current_end - duration <= event.event_time:
                window_start = current_end - duration
                window_id = f"sliding_{window_start.isoformat()}_{current_end.isoformat()}"
                
                # Create window if it doesn't exist
                if window_id not in self.windows:
                    self.windows[window_id] = SlidingWindow(window_id, window_start, duration, slide)
                
                window_ids.append(window_id)
                current_end += slide
            
            return window_ids
            
        except Exception as e:
            logger.error(f"Error in sliding window assignment: {e}")
            return []
    
    def _assign_to_session_window(self, event: WindowEvent) -> Optional[str]:
        """Assign event to session window"""
        try:
            session_timeout = self.config.get('timeout', timedelta(minutes=30))
            session_key = self.config.get('session_key', 'default')
            
            # Extract session identifier from event
            session_id = event.payload.get(session_key, 'default_session')
            
            # Find existing session window or create new one
            existing_window = None
            for window in self.windows.values():
                if (isinstance(window, SessionWindow) and 
                    session_id in window.window_id and
                    window.contains(event.event_time)):
                    existing_window = window
                    break
            
            if existing_window:
                return existing_window.window_id
            else:
                # Create new session window
                window_id = f"session_{session_id}_{event.event_time.isoformat()}"
                self.windows[window_id] = SessionWindow(window_id, event.event_time, session_timeout)
                return window_id
                
        except Exception as e:
            logger.error(f"Error in session window assignment: {e}")
            return None
    
    def _assign_to_global_window(self, event: WindowEvent) -> Optional[str]:
        """Assign event to global window"""
        try:
            window_id = "global_window"
            
            if window_id not in self.windows:
                self.windows[window_id] = GlobalWindow(window_id)
            
            return window_id
            
        except Exception as e:
            logger.error(f"Error in global window assignment: {e}")
            return None
    
    def get_window(self, window_id: str) -> Optional[Window]:
        """Get window by ID"""
        return self.windows.get(window_id)
    
    def get_all_windows(self) -> List[Window]:
        """Get all windows"""
        return list(self.windows.values())
    
    def cleanup_windows(self, watermark: datetime):
        """Clean up old windows that are beyond allowed lateness"""
        try:
            windows_to_remove = []
            
            for window_id, window in self.windows.items():
                if (window.state.closed and 
                    watermark > window.end_time + window.state.allowed_lateness):
                    windows_to_remove.append(window_id)
            
            for window_id in windows_to_remove:
                del self.windows[window_id]
                logger.debug(f"Cleaned up window {window_id}")
                
        except Exception as e:
            logger.error(f"Error cleaning up windows: {e}")


class WindowFunction(ABC):
    """Abstract base class for window functions"""
    
    @abstractmethod
    async def apply(self, window: Window) -> Dict[str, Any]:
        """Apply function to window events"""
        pass


class ContentEngagementWindowFunction(WindowFunction):
    """Window function for content engagement analytics"""
    
    async def apply(self, window: Window) -> Dict[str, Any]:
        """Calculate content engagement metrics"""
        try:
            events = window.get_events()
            
            if not events:
                return {"engagement_score": 0, "interaction_count": 0}
            
            # Calculate engagement metrics
            total_interactions = 0
            unique_users = set()
            content_views = 0
            engagement_scores = []
            
            for event in events:
                payload = event.payload
                
                if payload.get("event_type") == "content_interaction":
                    total_interactions += 1
                    user_id = payload.get("user_id")
                    if user_id:
                        unique_users.add(user_id)
                    
                    engagement_score = payload.get("engagement_score", 0)
                    if engagement_score > 0:
                        engagement_scores.append(engagement_score)
                
                elif payload.get("event_type") == "content_view":
                    content_views += 1
            
            avg_engagement_score = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
            
            return {
                "total_interactions": total_interactions,
                "unique_users": len(unique_users),
                "content_views": content_views,
                "avg_engagement_score": avg_engagement_score,
                "engagement_rate": total_interactions / max(1, content_views),
                "window_start": window.start_time.isoformat(),
                "window_end": window.end_time.isoformat(),
                "event_count": len(events)
            }
            
        except Exception as e:
            logger.error(f"Error applying content engagement window function: {e}")
            return {"error": str(e)}


class RevenueCalculationWindowFunction(WindowFunction):
    """Window function for revenue calculations"""
    
    async def apply(self, window: Window) -> Dict[str, Any]:
        """Calculate revenue metrics"""
        try:
            events = window.get_events()
            
            if not events:
                return {"total_revenue": 0, "transaction_count": 0}
            
            total_revenue = 0
            transaction_count = 0
            revenue_by_creator = defaultdict(float)
            revenue_by_type = defaultdict(float)
            
            for event in events:
                payload = event.payload
                
                if payload.get("event_type") in ["revenue_generated", "payment_processed"]:
                    amount = float(payload.get("amount", 0))
                    creator_id = payload.get("creator_id")
                    revenue_type = payload.get("revenue_type", "unknown")
                    
                    total_revenue += amount
                    transaction_count += 1
                    
                    if creator_id:
                        revenue_by_creator[creator_id] += amount
                    
                    revenue_by_type[revenue_type] += amount
            
            # Calculate commission (assuming 10% platform fee)
            platform_commission = total_revenue * 0.1
            creator_revenue = total_revenue - platform_commission
            
            return {
                "total_revenue": total_revenue,
                "creator_revenue": creator_revenue,
                "platform_commission": platform_commission,
                "transaction_count": transaction_count,
                "avg_transaction_value": total_revenue / max(1, transaction_count),
                "revenue_by_creator": dict(revenue_by_creator),
                "revenue_by_type": dict(revenue_by_type),
                "top_earning_creators": sorted(
                    revenue_by_creator.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10],
                "window_start": window.start_time.isoformat(),
                "window_end": window.end_time.isoformat(),
                "event_count": len(events)
            }
            
        except Exception as e:
            logger.error(f"Error applying revenue calculation window function: {e}")
            return {"error": str(e)}


class CollaborationSuccessWindowFunction(WindowFunction):
    """Window function for collaboration success metrics"""
    
    async def apply(self, window: Window) -> Dict[str, Any]:
        """Calculate collaboration success metrics"""
        try:
            events = window.get_events()
            
            if not events:
                return {"success_rate": 0, "collaboration_count": 0}
            
            collaboration_requests = 0
            successful_collaborations = 0
            collaboration_types = defaultdict(int)
            success_by_type = defaultdict(lambda: {"requests": 0, "successful": 0})
            
            for event in events:
                payload = event.payload
                event_type = payload.get("event_type")
                
                if event_type == "collaboration_request_sent":
                    collaboration_requests += 1
                    collab_type = payload.get("collaboration_type", "unknown")
                    collaboration_types[collab_type] += 1
                    success_by_type[collab_type]["requests"] += 1
                
                elif event_type == "collaboration_accepted":
                    successful_collaborations += 1
                    collab_type = payload.get("collaboration_type", "unknown")
                    success_by_type[collab_type]["successful"] += 1
            
            success_rate = successful_collaborations / max(1, collaboration_requests)
            
            # Calculate success rate by type
            success_rates_by_type = {}
            for collab_type, stats in success_by_type.items():
                if stats["requests"] > 0:
                    success_rates_by_type[collab_type] = stats["successful"] / stats["requests"]
            
            return {
                "collaboration_requests": collaboration_requests,
                "successful_collaborations": successful_collaborations,
                "success_rate": success_rate,
                "collaboration_types": dict(collaboration_types),
                "success_rates_by_type": success_rates_by_type,
                "window_start": window.start_time.isoformat(),
                "window_end": window.end_time.isoformat(),
                "event_count": len(events)
            }
            
        except Exception as e:
            logger.error(f"Error applying collaboration success window function: {e}")
            return {"error": str(e)}


class WindowingComputationEngine:
    """Main windowing computation engine for Ainflue platform"""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector
        self.window_assigners: Dict[str, WindowAssigner] = {}
        self.window_functions: Dict[str, WindowFunction] = {}
        self.watermark_generator = WatermarkGenerator(
            WatermarkStrategy.BOUNDED_OUT_OF_ORDERNESS,
            max_out_of_orderness=timedelta(seconds=30)
        )
        self.triggered_windows: deque = deque(maxlen=1000)
        self._computation_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the windowing computation engine"""
        try:
            logger.info("Starting Windowing Computation Engine")
            
            # Setup default window assigners and functions for Ainflue
            await self._setup_default_windows()
            
            # Start computation task
            self._computation_task = asyncio.create_task(self._computation_loop())
            
            logger.info("Windowing Computation Engine started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start windowing computation engine: {e}")
            raise
    
    async def stop(self):
        """Stop the computation engine"""
        try:
            logger.info("Stopping Windowing Computation Engine")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Wait for computation task
            if self._computation_task:
                await self._computation_task
            
            logger.info("Windowing Computation Engine stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping windowing computation engine: {e}")
            raise
    
    async def _setup_default_windows(self):
        """Setup default window assigners and functions for Ainflue"""
        try:
            # Content engagement windows
            self.window_assigners["content_engagement"] = WindowAssigner(
                "tumbling", 
                **AinflueBusinesWindowTypes.CONTENT_ENGAGEMENT_WINDOW
            )
            self.window_functions["content_engagement"] = ContentEngagementWindowFunction()
            
            # Creator activity windows
            self.window_assigners["creator_activity"] = WindowAssigner(
                "sliding",
                **AinflueBusinesWindowTypes.CREATOR_ACTIVITY_WINDOW
            )
            
            # Revenue calculation windows
            self.window_assigners["revenue_calculation"] = WindowAssigner(
                "tumbling",
                **AinflueBusinesWindowTypes.REVENUE_REPORTING_WINDOW
            )
            self.window_functions["revenue_calculation"] = RevenueCalculationWindowFunction()
            
            # Collaboration success windows
            self.window_assigners["collaboration_success"] = WindowAssigner(
                "session",
                **AinflueBusinesWindowTypes.COLLABORATION_SUCCESS_WINDOW
            )
            self.window_functions["collaboration_success"] = CollaborationSuccessWindowFunction()
            
            logger.info("Setup default window assigners and functions")
            
        except Exception as e:
            logger.error(f"Error setting up default windows: {e}")
            raise
    
    async def process_event(self, event_data: Dict[str, Any]) -> List[WindowResult]:
        """Process event through windowing system"""
        try:
            start_time = time.time()
            
            # Create window event
            window_event = WindowEvent(
                event_id=event_data.get("event_id", str(uuid4())),
                timestamp=datetime.now(timezone.utc),
                event_time=datetime.fromisoformat(
                    event_data.get("timestamp", datetime.now(timezone.utc).isoformat())
                ),
                payload=event_data
            )
            
            # Generate watermark
            watermark = self.watermark_generator.generate_watermark(
                window_event.event_time, 
                window_event.timestamp
            )
            
            if watermark:
                window_event.watermark = watermark
            
            results = []
            
            # Process event through each window assigner
            for assigner_name, assigner in self.window_assigners.items():
                try:
                    # Assign event to windows
                    window_ids = assigner.assign_to_windows(window_event)
                    
                    for window_id in window_ids:
                        window = assigner.get_window(window_id)
                        if window:
                            # Add event to window
                            added = window.add_event(window_event)
                            
                            if added and watermark:
                                window.update_watermark(watermark)
                                
                                # Check if window should be triggered
                                if window.should_trigger(window_event.timestamp, watermark):
                                    window_result = await self._compute_window(assigner_name, window)
                                    if window_result:
                                        results.append(window_result)
                                        window.state.triggered = True
                    
                    # Cleanup old windows
                    if watermark:
                        assigner.cleanup_windows(watermark)
                        
                except Exception as e:
                    logger.error(f"Error processing event with assigner {assigner_name}: {e}")
            
            processing_time = (time.time() - start_time) * 1000
            
            if self.metrics_collector:
                self.metrics_collector.histogram("windowing_processing_time", processing_time)
                self.metrics_collector.increment_counter("windowing_events_processed")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing event in windowing engine: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("windowing_processing_errors")
            return []
    
    async def _compute_window(self, assigner_name: str, window: Window) -> Optional[WindowResult]:
        """Compute window result using appropriate function"""
        try:
            window_function = self.window_functions.get(assigner_name)
            
            if window_function:
                computation_start = time.time()
                
                # Apply window function
                results = await window_function.apply(window)
                
                computation_time = (time.time() - computation_start) * 1000
                
                window_result = WindowResult(
                    window_id=window.window_id,
                    window_start=window.start_time,
                    window_end=window.end_time,
                    results=results,
                    event_count=len(window.state.events),
                    computation_time=datetime.now(timezone.utc),
                    is_final=True
                )
                
                # Store triggered window
                self.triggered_windows.append({
                    "window_id": window.window_id,
                    "assigner": assigner_name,
                    "trigger_time": datetime.now(timezone.utc).isoformat(),
                    "event_count": len(window.state.events),
                    "computation_time_ms": computation_time
                })
                
                if self.metrics_collector:
                    self.metrics_collector.histogram("window_computation_time", computation_time)
                    self.metrics_collector.increment_counter("windows_computed")
                
                logger.debug(f"Computed window {window.window_id} with {len(window.state.events)} events")
                
                return window_result
            else:
                logger.warning(f"No window function found for assigner {assigner_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error computing window {window.window_id}: {e}")
            return None
    
    async def _computation_loop(self):
        """Main computation monitoring loop"""
        try:
            while not self._shutdown_event.is_set():
                # Perform periodic maintenance
                await self._perform_maintenance()
                
                # Sleep before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in computation loop: {e}")
    
    async def _perform_maintenance(self):
        """Perform routine maintenance tasks"""
        try:
            # Log system status
            total_windows = sum(len(assigner.windows) for assigner in self.window_assigners.values())
            logger.debug(f"Windowing engine health check: {total_windows} active windows")
            
            # Could add more maintenance tasks like memory cleanup, metrics reporting, etc.
            
        except Exception as e:
            logger.error(f"Error performing maintenance: {e}")
    
    def add_window_assigner(self, name: str, window_type: str, **config):
        """Add custom window assigner"""
        try:
            self.window_assigners[name] = WindowAssigner(window_type, **config)
            logger.info(f"Added window assigner: {name}")
            
        except Exception as e:
            logger.error(f"Error adding window assigner {name}: {e}")
            raise
    
    def add_window_function(self, name: str, function: WindowFunction):
        """Add custom window function"""
        try:
            self.window_functions[name] = function
            logger.info(f"Added window function: {name}")
            
        except Exception as e:
            logger.error(f"Error adding window function {name}: {e}")
            raise
    
    def get_engine_metrics(self) -> Dict[str, Any]:
        """Get comprehensive engine metrics"""
        try:
            total_windows = 0
            windows_by_assigner = {}
            
            for name, assigner in self.window_assigners.items():
                window_count = len(assigner.windows)
                total_windows += window_count
                windows_by_assigner[name] = window_count
            
            metrics = {
                "total_windows": total_windows,
                "windows_by_assigner": windows_by_assigner,
                "window_assigners": len(self.window_assigners),
                "window_functions": len(self.window_functions),
                "triggered_windows_count": len(self.triggered_windows),
                "recent_triggered_windows": list(self.triggered_windows)[-10:] if self.triggered_windows else []
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting engine metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "WindowingComputationEngine", "WindowAssigner", "WindowFunction", "Window",
    "TumblingWindow", "SlidingWindow", "SessionWindow", "GlobalWindow",
    "WatermarkGenerator", "WindowEvent", "WindowState", "WindowResult",
    "ContentEngagementWindowFunction", "RevenueCalculationWindowFunction",
    "CollaborationSuccessWindowFunction", "AinflueBusinesWindowTypes",
    "WindowAlignment", "WatermarkStrategy", "TriggerType"
]