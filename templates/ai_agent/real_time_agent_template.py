"""
⚡ Real-Time AI Agent Template - Enterprise Real-Time Processing Framework
========================================================================

🎖️ LEAD DEV IA + ML ENGINEER - Advanced Real-Time AI Processing Agent
- Real-time content analysis and decision making
- Stream processing with <100ms latency
- Live content moderation and filtering
- Real-time recommendation systems
- Live sentiment analysis and trend detection
- Instant notification and alert systems

Author: Expert Team (Lead Dev IA + ML Engineer)
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import threading
from collections import deque
from abc import ABC, abstractmethod
import numpy as np
from pydantic import BaseModel, Field
import aioredis
import websockets
from concurrent.futures import ThreadPoolExecutor
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingPriority(Enum):
    """Processing priority levels"""
    CRITICAL = "critical"      # <10ms response time
    HIGH = "high"             # <50ms response time
    MEDIUM = "medium"         # <100ms response time
    LOW = "low"               # <500ms response time

class EventType(Enum):
    """Real-time event types"""
    CONTENT_UPLOAD = "content_upload"
    USER_INTERACTION = "user_interaction"
    CONTENT_VIEW = "content_view"
    COMMENT_POST = "comment_post"
    LIVE_STREAM = "live_stream"
    ALERT_TRIGGER = "alert_trigger"
    SYSTEM_METRIC = "system_metric"
    SECURITY_EVENT = "security_event"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class RealTimeEvent:
    """Real-time event data structure"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    priority: ProcessingPriority
    data: Dict[str, Any]
    source: str
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_latency: Optional[float] = None

@dataclass
class ProcessingResult:
    """Processing result with timing information"""
    event_id: str
    result: Any
    processing_time_ms: float
    success: bool
    error_message: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)

class RealTimeProcessor(ABC):
    """Abstract real-time processor"""
    
    @abstractmethod
    async def process_event(self, event: RealTimeEvent) -> ProcessingResult:
        """Process real-time event"""
        pass
    
    @abstractmethod
    def get_max_processing_time(self) -> float:
        """Get maximum allowed processing time in milliseconds"""
        pass

class ContentModerationProcessor(RealTimeProcessor):
    """Real-time content moderation processor"""
    
    def __init__(self):
        self.toxic_keywords = {
            "hate_speech": ["hate", "discrimination", "racist", "sexist"],
            "violence": ["kill", "murder", "attack", "violence"],
            "spam": ["click here", "free money", "urgent", "limited time"],
            "adult_content": ["explicit", "nsfw", "adult", "mature"]
        }
        self.confidence_threshold = 0.75
    
    async def process_event(self, event: RealTimeEvent) -> ProcessingResult:
        """Process content moderation event"""
        start_time = time.time()
        
        try:
            content = event.data.get("content", "")
            content_type = event.data.get("content_type", "text")
            
            # Real-time content analysis
            moderation_result = await self._analyze_content(content, content_type)
            
            processing_time = (time.time() - start_time) * 1000
            
            actions = []
            recommendations = []
            
            # Take immediate action if needed
            if moderation_result["is_violation"]:
                severity = moderation_result["severity"]
                
                if severity == "high":
                    actions.append("content_blocked")
                    actions.append("user_notified")
                elif severity == "medium":
                    actions.append("content_flagged")
                    recommendations.append("human_review_required")
                
            return ProcessingResult(
                event_id=event.event_id,
                result=moderation_result,
                processing_time_ms=processing_time,
                success=True,
                actions_taken=actions,
                recommendations=recommendations
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return ProcessingResult(
                event_id=event.event_id,
                result=None,
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _analyze_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """Analyze content for violations"""
        violations = []
        severity_score = 0
        
        # Keyword-based analysis (fast)
        for category, keywords in self.toxic_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    violations.append({
                        "category": category,
                        "keyword": keyword,
                        "confidence": 0.9
                    })
                    severity_score += 1
        
        # Determine severity
        if severity_score >= 3:
            severity = "high"
        elif severity_score >= 2:
            severity = "medium"
        elif severity_score >= 1:
            severity = "low"
        else:
            severity = "none"
        
        return {
            "is_violation": len(violations) > 0,
            "violations": violations,
            "severity": severity,
            "confidence": min(0.9, severity_score * 0.3),
            "content_type": content_type
        }
    
    def get_max_processing_time(self) -> float:
        """Maximum processing time: 50ms for real-time moderation"""
        return 50.0

class SentimentAnalysisProcessor(RealTimeProcessor):
    """Real-time sentiment analysis processor"""
    
    def __init__(self):
        self.positive_words = ["good", "great", "awesome", "love", "amazing", "excellent", "fantastic"]
        self.negative_words = ["bad", "hate", "terrible", "awful", "horrible", "disgusting", "worst"]
        self.neutral_words = ["okay", "fine", "average", "normal", "standard"]
    
    async def process_event(self, event: RealTimeEvent) -> ProcessingResult:
        """Process sentiment analysis event"""
        start_time = time.time()
        
        try:
            text = event.data.get("text", "")
            
            # Fast sentiment analysis
            sentiment_result = await self._analyze_sentiment(text)
            
            processing_time = (time.time() - start_time) * 1000
            
            recommendations = []
            if sentiment_result["sentiment"] == "negative" and sentiment_result["confidence"] > 0.8:
                recommendations.append("engage_with_user")
                recommendations.append("provide_support")
            
            return ProcessingResult(
                event_id=event.event_id,
                result=sentiment_result,
                processing_time_ms=processing_time,
                success=True,
                recommendations=recommendations
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return ProcessingResult(
                event_id=event.event_id,
                result=None,
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        words = text.lower().split()
        
        positive_score = sum(1 for word in words if word in self.positive_words)
        negative_score = sum(1 for word in words if word in self.negative_words)
        neutral_score = sum(1 for word in words if word in self.neutral_words)
        
        total_score = positive_score + negative_score + neutral_score
        
        if total_score == 0:
            sentiment = "neutral"
            confidence = 0.5
        elif positive_score > negative_score:
            sentiment = "positive"
            confidence = min(0.95, (positive_score / max(1, total_score)) + 0.3)
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = min(0.95, (negative_score / max(1, total_score)) + 0.3)
        else:
            sentiment = "neutral"
            confidence = 0.6
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": {
                "positive": positive_score,
                "negative": negative_score,
                "neutral": neutral_score
            }
        }
    
    def get_max_processing_time(self) -> float:
        """Maximum processing time: 25ms for real-time sentiment"""
        return 25.0

class RecommendationProcessor(RealTimeProcessor):
    """Real-time recommendation processor"""
    
    def __init__(self):
        self.user_preferences = {}  # Cache user preferences
        self.trending_content = []  # Trending content cache
        self.recommendation_cache = {}
    
    async def process_event(self, event: RealTimeEvent) -> ProcessingResult:
        """Process real-time recommendation event"""
        start_time = time.time()
        
        try:
            user_id = event.user_id
            content_type = event.data.get("content_type", "video")
            context = event.data.get("context", {})
            
            # Generate real-time recommendations
            recommendations = await self._generate_recommendations(user_id, content_type, context)
            
            processing_time = (time.time() - start_time) * 1000
            
            return ProcessingResult(
                event_id=event.event_id,
                result=recommendations,
                processing_time_ms=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return ProcessingResult(
                event_id=event.event_id,
                result=None,
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _generate_recommendations(self, user_id: str, content_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized recommendations"""
        # Check cache first
        cache_key = f"{user_id}_{content_type}_{hash(str(context))}"
        if cache_key in self.recommendation_cache:
            cached_rec = self.recommendation_cache[cache_key]
            if (datetime.now() - cached_rec["timestamp"]).seconds < 300:  # 5 minute cache
                return cached_rec["data"]
        
        # Generate new recommendations
        user_prefs = self.user_preferences.get(user_id, {})
        
        recommendations = {
            "recommended_content": [],
            "trending_now": self.trending_content[:5],
            "personalized_score": 0.0,
            "context_match": 0.0
        }
        
        # Simple recommendation logic (in production, use ML models)
        if content_type == "video":
            recommendations["recommended_content"] = [
                {"id": "video_001", "title": "AI Content Creation", "score": 0.95},
                {"id": "video_002", "title": "Social Media Tips", "score": 0.87},
                {"id": "video_003", "title": "Creator Economy", "score": 0.82}
            ]
        elif content_type == "image":
            recommendations["recommended_content"] = [
                {"id": "image_001", "title": "Photography Tips", "score": 0.91},
                {"id": "image_002", "title": "Visual Design", "score": 0.84},
                {"id": "image_003", "title": "Art Inspiration", "score": 0.79}
            ]
        
        # Cache the result
        self.recommendation_cache[cache_key] = {
            "data": recommendations,
            "timestamp": datetime.now()
        }
        
        return recommendations
    
    def get_max_processing_time(self) -> float:
        """Maximum processing time: 75ms for recommendations"""
        return 75.0

class RealTimeAgent:
    """⚡ Advanced Real-Time AI Agent for Live Processing and Response"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Real-Time Agent"""
        self.config = config or {}
        self.processors = self._initialize_processors()
        self.event_queue = asyncio.Queue(maxsize=10000)
        self.processing_stats = {
            "total_events": 0,
            "successful_events": 0,
            "failed_events": 0,
            "average_latency": 0.0,
            "latency_histogram": deque(maxlen=1000)
        }
        self.alert_handlers = []
        self.is_running = False
        self.worker_tasks = []
        
        # Real-time metrics
        self.metrics = {
            "events_per_second": 0,
            "current_queue_size": 0,
            "worker_utilization": 0.0,
            "memory_usage": 0.0
        }
        
        logger.info("⚡ Real-Time Agent initialized successfully")
    
    def _initialize_processors(self) -> Dict[EventType, RealTimeProcessor]:
        """Initialize event processors"""
        return {
            EventType.CONTENT_UPLOAD: ContentModerationProcessor(),
            EventType.COMMENT_POST: SentimentAnalysisProcessor(),
            EventType.USER_INTERACTION: RecommendationProcessor(),
            EventType.CONTENT_VIEW: RecommendationProcessor()
        }
    
    async def start(self, num_workers: int = 5):
        """Start the real-time processing system"""
        logger.info(f"Starting Real-Time Agent with {num_workers} workers")
        
        self.is_running = True
        
        # Start worker tasks
        for i in range(num_workers):
            task = asyncio.create_task(self._worker(f"worker_{i}"))
            self.worker_tasks.append(task)
        
        # Start metrics collection
        metrics_task = asyncio.create_task(self._collect_metrics())
        self.worker_tasks.append(metrics_task)
        
        logger.info("✅ Real-Time Agent started successfully")
    
    async def stop(self):
        """Stop the real-time processing system"""
        logger.info("Stopping Real-Time Agent")
        
        self.is_running = False
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        logger.info("✅ Real-Time Agent stopped")
    
    async def _worker(self, worker_id: str):
        """Worker coroutine for processing events"""
        logger.info(f"Worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )
                
                # Process event
                result = await self._process_event(event)
                
                # Update statistics
                self._update_stats(result)
                
                # Handle alerts if needed
                await self._handle_alerts(event, result)
                
                # Mark task as done
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                # No events in queue, continue
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
    
    async def _process_event(self, event: RealTimeEvent) -> ProcessingResult:
        """Process a single event"""
        start_time = time.time()
        
        try:
            # Get appropriate processor
            processor = self.processors.get(event.event_type)
            if not processor:
                return ProcessingResult(
                    event_id=event.event_id,
                    result=None,
                    processing_time_ms=(time.time() - start_time) * 1000,
                    success=False,
                    error_message=f"No processor for event type: {event.event_type}"
                )
            
            # Process with timeout based on priority
            timeout = self._get_timeout_for_priority(event.priority)
            
            try:
                result = await asyncio.wait_for(
                    processor.process_event(event),
                    timeout=timeout / 1000  # Convert to seconds
                )
                
                # Update event with processing latency
                event.processing_latency = result.processing_time_ms
                
                return result
                
            except asyncio.TimeoutError:
                processing_time = (time.time() - start_time) * 1000
                return ProcessingResult(
                    event_id=event.event_id,
                    result=None,
                    processing_time_ms=processing_time,
                    success=False,
                    error_message=f"Processing timeout ({timeout}ms exceeded)"
                )
                
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return ProcessingResult(
                event_id=event.event_id,
                result=None,
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def _get_timeout_for_priority(self, priority: ProcessingPriority) -> float:
        """Get timeout in milliseconds based on priority"""
        timeouts = {
            ProcessingPriority.CRITICAL: 10.0,
            ProcessingPriority.HIGH: 50.0,
            ProcessingPriority.MEDIUM: 100.0,
            ProcessingPriority.LOW: 500.0
        }
        return timeouts.get(priority, 100.0)
    
    def _update_stats(self, result: ProcessingResult):
        """Update processing statistics"""
        self.processing_stats["total_events"] += 1
        
        if result.success:
            self.processing_stats["successful_events"] += 1
        else:
            self.processing_stats["failed_events"] += 1
        
        # Update latency statistics
        latency = result.processing_time_ms
        self.processing_stats["latency_histogram"].append(latency)
        
        # Calculate rolling average latency
        if len(self.processing_stats["latency_histogram"]) > 0:
            self.processing_stats["average_latency"] = np.mean(
                list(self.processing_stats["latency_histogram"])
            )
    
    async def _handle_alerts(self, event: RealTimeEvent, result: ProcessingResult):
        """Handle alerts based on processing results"""
        alerts = []
        
        # Check for processing failures
        if not result.success:
            alerts.append({
                "level": AlertLevel.ERROR,
                "message": f"Event processing failed: {result.error_message}",
                "event_id": event.event_id,
                "timestamp": datetime.now()
            })
        
        # Check for high latency
        if result.processing_time_ms > self._get_timeout_for_priority(event.priority) * 0.8:
            alerts.append({
                "level": AlertLevel.WARNING,
                "message": f"High processing latency: {result.processing_time_ms:.1f}ms",
                "event_id": event.event_id,
                "timestamp": datetime.now()
            })
        
        # Check for critical content violations
        if (result.result and 
            isinstance(result.result, dict) and 
            result.result.get("severity") == "high"):
            alerts.append({
                "level": AlertLevel.CRITICAL,
                "message": "Critical content violation detected",
                "event_id": event.event_id,
                "timestamp": datetime.now()
            })
        
        # Send alerts
        for alert in alerts:
            await self._send_alert(alert)
    
    async def _send_alert(self, alert: Dict[str, Any]):
        """Send alert to configured handlers"""
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {str(e)}")
    
    async def _collect_metrics(self):
        """Collect real-time metrics"""
        last_event_count = 0
        last_time = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                current_events = self.processing_stats["total_events"]
                
                # Calculate events per second
                time_diff = current_time - last_time
                if time_diff > 0:
                    events_diff = current_events - last_event_count
                    self.metrics["events_per_second"] = events_diff / time_diff
                
                # Update other metrics
                self.metrics["current_queue_size"] = self.event_queue.qsize()
                self.metrics["worker_utilization"] = min(100.0, self.event_queue.qsize() / 100 * 100)
                
                last_event_count = current_events
                last_time = current_time
                
                await asyncio.sleep(1.0)  # Update every second
                
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
    
    async def submit_event(self, event: RealTimeEvent) -> bool:
        """Submit event for real-time processing"""
        try:
            # Add event to queue (non-blocking)
            self.event_queue.put_nowait(event)
            return True
        except asyncio.QueueFull:
            logger.warning(f"Event queue full, dropping event {event.event_id}")
            return False
    
    async def create_and_submit_event(self, 
                                     event_type: EventType,
                                     data: Dict[str, Any],
                                     priority: ProcessingPriority = ProcessingPriority.MEDIUM,
                                     user_id: Optional[str] = None,
                                     content_id: Optional[str] = None) -> str:
        """Create and submit event for processing"""
        
        event = RealTimeEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now(),
            priority=priority,
            data=data,
            source="real_time_agent",
            user_id=user_id,
            content_id=content_id
        )
        
        success = await self.submit_event(event)
        if success:
            return event.event_id
        else:
            raise Exception("Failed to submit event: queue full")
    
    def add_alert_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add alert handler"""
        self.alert_handlers.append(handler)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.processing_stats,
            **self.metrics,
            "queue_size": self.event_queue.qsize(),
            "is_running": self.is_running,
            "num_workers": len(self.worker_tasks)
        }
    
    def get_latency_percentiles(self) -> Dict[str, float]:
        """Get latency percentiles"""
        if not self.processing_stats["latency_histogram"]:
            return {}
        
        latencies = np.array(list(self.processing_stats["latency_histogram"]))
        
        return {
            "p50": np.percentile(latencies, 50),
            "p90": np.percentile(latencies, 90),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99),
            "max": np.max(latencies),
            "min": np.min(latencies)
        }

# WebSocket integration for real-time events
class WebSocketEventHandler:
    """WebSocket handler for real-time events"""
    
    def __init__(self, agent: RealTimeAgent):
        self.agent = agent
        self.connected_clients = set()
    
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                
                # Create event from WebSocket message
                event_id = await self.agent.create_and_submit_event(
                    event_type=EventType(data.get("event_type", "user_interaction")),
                    data=data.get("data", {}),
                    priority=ProcessingPriority(data.get("priority", "medium")),
                    user_id=data.get("user_id"),
                    content_id=data.get("content_id")
                )
                
                # Send response
                response = {
                    "event_id": event_id,
                    "status": "submitted",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(response))
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {websocket.remote_address}")
        finally:
            self.connected_clients.remove(websocket)
    
    async def broadcast_stats(self):
        """Broadcast processing stats to connected clients"""
        while True:
            if self.connected_clients:
                stats = self.agent.get_stats()
                message = {
                    "type": "stats_update",
                    "data": stats,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Send to all connected clients
                disconnected = []
                for client in self.connected_clients:
                    try:
                        await client.send(json.dumps(message))
                    except websockets.exceptions.ConnectionClosed:
                        disconnected.append(client)
                
                # Remove disconnected clients
                for client in disconnected:
                    self.connected_clients.discard(client)
            
            await asyncio.sleep(5.0)  # Broadcast every 5 seconds

# Usage Example and Template Testing
async def main():
    """Example usage of Real-Time Agent Template"""
    
    # Initialize the agent
    agent = RealTimeAgent()
    
    # Add custom alert handler
    async def alert_handler(alert):
        print(f"🚨 ALERT [{alert['level'].value.upper()}]: {alert['message']}")
    
    agent.add_alert_handler(alert_handler)
    
    # Start the agent
    await agent.start(num_workers=3)
    
    try:
        # Submit test events
        events_to_submit = [
            {
                "event_type": EventType.CONTENT_UPLOAD,
                "data": {
                    "content": "This is a test content upload",
                    "content_type": "text"
                },
                "priority": ProcessingPriority.HIGH,
                "user_id": "user_123"
            },
            {
                "event_type": EventType.COMMENT_POST,
                "data": {
                    "text": "This is an awesome video! I love it!"
                },
                "priority": ProcessingPriority.MEDIUM,
                "user_id": "user_456"
            },
            {
                "event_type": EventType.USER_INTERACTION,
                "data": {
                    "content_type": "video",
                    "context": {"page": "discover"}
                },
                "priority": ProcessingPriority.LOW,
                "user_id": "user_789"
            }
        ]
        
        # Submit events
        event_ids = []
        for event_data in events_to_submit:
            event_id = await agent.create_and_submit_event(**event_data)
            event_ids.append(event_id)
            print(f"✅ Submitted event: {event_id}")
        
        # Wait for processing
        await asyncio.sleep(2.0)
        
        # Get statistics
        stats = agent.get_stats()
        print(f"\n📊 Processing Statistics:")
        print(f"  Total Events: {stats['total_events']}")
        print(f"  Successful: {stats['successful_events']}")
        print(f"  Failed: {stats['failed_events']}")
        print(f"  Average Latency: {stats['average_latency']:.2f}ms")
        print(f"  Events/Second: {stats['events_per_second']:.1f}")
        
        # Get latency percentiles
        percentiles = agent.get_latency_percentiles()
        if percentiles:
            print(f"\n📈 Latency Percentiles:")
            print(f"  P50: {percentiles['p50']:.2f}ms")
            print(f"  P90: {percentiles['p90']:.2f}ms")
            print(f"  P95: {percentiles['p95']:.2f}ms")
            print(f"  P99: {percentiles['p99']:.2f}ms")
        
    except Exception as e:
        logger.error(f"Error in real-time processing: {str(e)}")
    finally:
        # Stop the agent
        await agent.stop()

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    print("⚡ Real-Time Agent Template demonstration completed!")