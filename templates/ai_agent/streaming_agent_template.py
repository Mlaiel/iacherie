"""
🌊 Streaming AI Agent Template - Enterprise Streaming Data Processing Framework
===============================================================================

🎖️ LEAD DEV IA + ML ENGINEER - Advanced Streaming AI Processing Agent
- Real-time streaming data processing and analysis
- Kafka/Pulsar stream processing integration
- Continuous ML model inference on streams
- Live content moderation and filtering
- Real-time analytics and aggregations
- Event-driven streaming architectures

Author: Expert Team (Lead Dev IA + ML Engineer)
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, AsyncGenerator, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import threading
from collections import deque, defaultdict
from abc import ABC, abstractmethod
import numpy as np
from pydantic import BaseModel, Field
import aioredis
import aiokafka
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import uuid
from concurrent.futures import ThreadPoolExecutor
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamEventType(Enum):
    """Streaming event types"""
    USER_ACTION = "user_action"
    CONTENT_UPDATE = "content_update"
    ENGAGEMENT_EVENT = "engagement_event"
    SYSTEM_METRIC = "system_metric"
    ALERT_EVENT = "alert_event"
    ML_INFERENCE = "ml_inference"
    ANALYTICS_EVENT = "analytics_event"

class ProcessingLatency(Enum):
    """Processing latency requirements"""
    ULTRA_LOW = 1      # <1ms
    LOW = 10           # <10ms
    MEDIUM = 100       # <100ms
    HIGH = 1000        # <1s

@dataclass
class StreamMessage:
    """Streaming message data structure"""
    message_id: str
    event_type: StreamEventType
    timestamp: datetime
    data: Dict[str, Any]
    source_topic: str
    source_partition: Optional[int] = None
    source_offset: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_deadline: Optional[datetime] = None

@dataclass
class StreamProcessor:
    """Stream processor configuration"""
    processor_id: str
    name: str
    input_topics: List[str]
    output_topics: List[str]
    processing_function: Callable
    latency_requirement: ProcessingLatency
    batch_size: int = 1
    batch_timeout_ms: int = 100
    parallelism: int = 1
    error_handling: str = "retry"  # retry, skip, dead_letter

@dataclass
class StreamingStats:
    """Streaming processing statistics"""
    messages_processed: int = 0
    messages_failed: int = 0
    total_processing_time: float = 0.0
    average_latency: float = 0.0
    throughput_per_second: float = 0.0
    latency_percentiles: Dict[str, float] = field(default_factory=dict)
    error_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class StreamingEventProcessor(ABC):
    """Abstract streaming event processor"""
    
    @abstractmethod
    async def process_message(self, message: StreamMessage) -> Optional[StreamMessage]:
        """Process a single streaming message"""
        pass
    
    @abstractmethod
    async def process_batch(self, messages: List[StreamMessage]) -> List[Optional[StreamMessage]]:
        """Process a batch of streaming messages"""
        pass
    
    def get_processor_name(self) -> str:
        """Get processor name"""
        return self.__class__.__name__

class RealTimeContentModerator(StreamingEventProcessor):
    """Real-time content moderation processor"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.moderation_rules = self.config.get("moderation_rules", {})
        self.toxic_patterns = [
            r'\b(hate|kill|murder)\b',
            r'\b(spam|scam|fraud)\b',
            r'\b(explicit|nsfw)\b'
        ]
        self.processed_count = 0
    
    async def process_message(self, message: StreamMessage) -> Optional[StreamMessage]:
        """Process content moderation message"""
        start_time = time.time()
        
        try:
            content = message.data.get("content", "")
            user_id = message.data.get("user_id")
            content_type = message.data.get("content_type", "text")
            
            # Fast content analysis
            moderation_result = await self._moderate_content(content, content_type)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Create output message if action needed
            if moderation_result["action_required"]:
                output_message = StreamMessage(
                    message_id=str(uuid.uuid4()),
                    event_type=StreamEventType.ALERT_EVENT,
                    timestamp=datetime.now(),
                    data={
                        "original_message_id": message.message_id,
                        "user_id": user_id,
                        "content_type": content_type,
                        "moderation_result": moderation_result,
                        "processing_time_ms": processing_time
                    },
                    source_topic="moderation_alerts"
                )
                
                self.processed_count += 1
                return output_message
            
            return None  # No action needed
            
        except Exception as e:
            logger.error(f"Content moderation error: {str(e)}")
            # Create error message
            error_message = StreamMessage(
                message_id=str(uuid.uuid4()),
                event_type=StreamEventType.ALERT_EVENT,
                timestamp=datetime.now(),
                data={
                    "error": str(e),
                    "original_message_id": message.message_id
                },
                source_topic="moderation_errors"
            )
            return error_message
    
    async def process_batch(self, messages: List[StreamMessage]) -> List[Optional[StreamMessage]]:
        """Process batch of content moderation messages"""
        results = []
        for message in messages:
            result = await self.process_message(message)
            results.append(result)
        return results
    
    async def _moderate_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """Moderate content for violations"""
        import re
        
        violations = []
        severity_score = 0
        
        # Pattern matching for fast detection
        for pattern in self.toxic_patterns:
            matches = re.findall(pattern, content.lower())
            if matches:
                violations.append({
                    "pattern": pattern,
                    "matches": matches,
                    "severity": "high" if "kill|murder" in pattern else "medium"
                })
                severity_score += len(matches)
        
        action_required = severity_score > 0
        
        return {
            "action_required": action_required,
            "violations": violations,
            "severity_score": severity_score,
            "recommended_action": "block" if severity_score >= 2 else "flag" if severity_score >= 1 else "approve"
        }

class LiveEngagementAnalyzer(StreamingEventProcessor):
    """Real-time engagement analysis processor"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.engagement_windows = defaultdict(deque)  # Rolling windows per content
        self.window_size = self.config.get("window_size_seconds", 300)  # 5 minutes
        self.processed_count = 0
    
    async def process_message(self, message: StreamMessage) -> Optional[StreamMessage]:
        """Process engagement event"""
        start_time = time.time()
        
        try:
            content_id = message.data.get("content_id")
            engagement_type = message.data.get("engagement_type")  # like, share, comment, view
            user_id = message.data.get("user_id")
            timestamp = message.timestamp
            
            if not content_id or not engagement_type:
                return None
            
            # Add to rolling window
            window = self.engagement_windows[content_id]
            window.append({
                "type": engagement_type,
                "user_id": user_id,
                "timestamp": timestamp
            })
            
            # Remove old events outside window
            cutoff_time = timestamp - timedelta(seconds=self.window_size)
            while window and window[0]["timestamp"] < cutoff_time:
                window.popleft()
            
            # Calculate engagement metrics
            metrics = await self._calculate_engagement_metrics(content_id, window)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Create analytics message
            analytics_message = StreamMessage(
                message_id=str(uuid.uuid4()),
                event_type=StreamEventType.ANALYTICS_EVENT,
                timestamp=datetime.now(),
                data={
                    "content_id": content_id,
                    "metrics": metrics,
                    "window_size_seconds": self.window_size,
                    "processing_time_ms": processing_time
                },
                source_topic="engagement_analytics"
            )
            
            self.processed_count += 1
            return analytics_message
            
        except Exception as e:
            logger.error(f"Engagement analysis error: {str(e)}")
            return None
    
    async def process_batch(self, messages: List[StreamMessage]) -> List[Optional[StreamMessage]]:
        """Process batch of engagement messages"""
        results = []
        for message in messages:
            result = await self.process_message(message)
            results.append(result)
        return results
    
    async def _calculate_engagement_metrics(self, content_id: str, window: deque) -> Dict[str, Any]:
        """Calculate engagement metrics for content"""
        if not window:
            return {"total_engagements": 0}
        
        # Count by type
        engagement_counts = defaultdict(int)
        unique_users = set()
        
        for event in window:
            engagement_counts[event["type"]] += 1
            unique_users.add(event["user_id"])
        
        # Calculate rates (events per minute)
        window_minutes = self.window_size / 60
        
        metrics = {
            "total_engagements": len(window),
            "unique_users": len(unique_users),
            "engagement_rate_per_minute": len(window) / window_minutes,
            "engagement_breakdown": dict(engagement_counts),
            "user_engagement_ratio": len(unique_users) / max(1, len(window))
        }
        
        # Calculate engagement score
        weights = {"view": 1, "like": 3, "share": 5, "comment": 7}
        engagement_score = sum(
            engagement_counts[eng_type] * weights.get(eng_type, 1)
            for eng_type in engagement_counts
        )
        metrics["engagement_score"] = engagement_score
        
        return metrics

class StreamingMLInference(StreamingEventProcessor):
    """Real-time ML inference processor"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.model_cache = {}
        self.inference_cache = {}
        self.cache_ttl = self.config.get("cache_ttl_seconds", 300)
        self.processed_count = 0
    
    async def process_message(self, message: StreamMessage) -> Optional[StreamMessage]:
        """Process ML inference message"""
        start_time = time.time()
        
        try:
            model_type = message.data.get("model_type", "sentiment")
            input_data = message.data.get("input_data")
            user_id = message.data.get("user_id")
            
            if not input_data:
                return None
            
            # Check cache first
            cache_key = f"{model_type}_{hash(str(input_data))}"
            cached_result = self.inference_cache.get(cache_key)
            
            if cached_result and (datetime.now() - cached_result["timestamp"]).seconds < self.cache_ttl:
                inference_result = cached_result["result"]
                cache_hit = True
            else:
                # Perform inference
                inference_result = await self._run_inference(model_type, input_data)
                
                # Cache result
                self.inference_cache[cache_key] = {
                    "result": inference_result,
                    "timestamp": datetime.now()
                }
                cache_hit = False
            
            processing_time = (time.time() - start_time) * 1000
            
            # Create inference result message
            result_message = StreamMessage(
                message_id=str(uuid.uuid4()),
                event_type=StreamEventType.ML_INFERENCE,
                timestamp=datetime.now(),
                data={
                    "original_message_id": message.message_id,
                    "model_type": model_type,
                    "user_id": user_id,
                    "inference_result": inference_result,
                    "processing_time_ms": processing_time,
                    "cache_hit": cache_hit
                },
                source_topic="ml_inference_results"
            )
            
            self.processed_count += 1
            return result_message
            
        except Exception as e:
            logger.error(f"ML inference error: {str(e)}")
            return None
    
    async def process_batch(self, messages: List[StreamMessage]) -> List[Optional[StreamMessage]]:
        """Process batch of ML inference messages"""
        # Batch inference for better efficiency
        batch_inputs = []
        model_types = []
        
        for message in messages:
            model_type = message.data.get("model_type", "sentiment")
            input_data = message.data.get("input_data")
            if input_data:
                batch_inputs.append(input_data)
                model_types.append(model_type)
        
        # Run batch inference
        if batch_inputs:
            batch_results = await self._run_batch_inference(model_types, batch_inputs)
        else:
            batch_results = []
        
        # Create result messages
        results = []
        for i, message in enumerate(messages):
            if i < len(batch_results):
                result_message = StreamMessage(
                    message_id=str(uuid.uuid4()),
                    event_type=StreamEventType.ML_INFERENCE,
                    timestamp=datetime.now(),
                    data={
                        "original_message_id": message.message_id,
                        "inference_result": batch_results[i],
                        "batch_processed": True
                    },
                    source_topic="ml_inference_results"
                )
                results.append(result_message)
            else:
                results.append(None)
        
        return results
    
    async def _run_inference(self, model_type: str, input_data: Any) -> Dict[str, Any]:
        """Run ML inference on input data"""
        # Simulate different types of ML inference
        if model_type == "sentiment":
            return await self._sentiment_inference(input_data)
        elif model_type == "classification":
            return await self._classification_inference(input_data)
        elif model_type == "recommendation":
            return await self._recommendation_inference(input_data)
        else:
            return {"error": f"Unknown model type: {model_type}"}
    
    async def _run_batch_inference(self, model_types: List[str], batch_inputs: List[Any]) -> List[Dict[str, Any]]:
        """Run batch ML inference"""
        results = []
        for model_type, input_data in zip(model_types, batch_inputs):
            result = await self._run_inference(model_type, input_data)
            results.append(result)
        return results
    
    async def _sentiment_inference(self, text: str) -> Dict[str, Any]:
        """Sentiment analysis inference"""
        # Simplified sentiment analysis
        positive_words = ["good", "great", "awesome", "love", "amazing"]
        negative_words = ["bad", "hate", "terrible", "awful"]
        
        words = text.lower().split()
        positive_score = sum(1 for word in words if word in positive_words)
        negative_score = sum(1 for word in words if word in negative_words)
        
        if positive_score > negative_score:
            sentiment = "positive"
            confidence = min(0.95, positive_score / max(1, len(words)) * 10)
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = min(0.95, negative_score / max(1, len(words)) * 10)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "model_version": "1.0"
        }
    
    async def _classification_inference(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Content classification inference"""
        # Simplified classification
        content = data.get("content", "")
        
        categories = {
            "technology": ["ai", "tech", "software", "digital"],
            "entertainment": ["music", "video", "game", "show"],
            "education": ["learn", "teach", "course", "tutorial"]
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in content.lower())
            scores[category] = score / len(keywords)
        
        predicted_category = max(scores, key=scores.get) if scores else "other"
        confidence = max(scores.values()) if scores else 0.1
        
        return {
            "predicted_category": predicted_category,
            "confidence": confidence,
            "all_scores": scores,
            "model_version": "1.0"
        }
    
    async def _recommendation_inference(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommendation inference"""
        user_id = data.get("user_id")
        context = data.get("context", {})
        
        # Simplified recommendation
        recommendations = [
            {"item_id": "item_001", "score": 0.95, "reason": "trending"},
            {"item_id": "item_002", "score": 0.87, "reason": "similar_users"},
            {"item_id": "item_003", "score": 0.82, "reason": "user_history"}
        ]
        
        return {
            "recommendations": recommendations,
            "user_id": user_id,
            "context": context,
            "model_version": "1.0"
        }

class StreamingAgent:
    """🌊 Advanced Streaming AI Agent for Real-Time Data Processing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Streaming Agent"""
        self.config = config or {}
        self.kafka_config = self.config.get("kafka", {
            "bootstrap_servers": ["localhost:9092"],
            "group_id": "streaming_agent",
            "auto_offset_reset": "latest"
        })
        
        self.processors = {}
        self.consumers = {}
        self.producers = {}
        self.stats = defaultdict(StreamingStats)
        self.is_running = False
        self.processing_tasks = []
        
        # Metrics collection
        self.latency_buffer = deque(maxlen=1000)
        self.throughput_buffer = deque(maxlen=60)  # 1 minute of throughput data
        
        logger.info("🌊 Streaming Agent initialized successfully")
    
    def register_processor(self, processor_config: StreamProcessor, processor: StreamingEventProcessor):
        """Register a streaming processor"""
        self.processors[processor_config.processor_id] = {
            "config": processor_config,
            "processor": processor
        }
        logger.info(f"Registered processor: {processor_config.name}")
    
    async def start(self):
        """Start the streaming agent"""
        logger.info("Starting Streaming Agent")
        self.is_running = True
        
        # Initialize Kafka connections
        await self._initialize_kafka()
        
        # Start processing tasks for each processor
        for processor_id, processor_info in self.processors.items():
            task = asyncio.create_task(
                self._process_stream(processor_id, processor_info)
            )
            self.processing_tasks.append(task)
        
        # Start metrics collection
        metrics_task = asyncio.create_task(self._collect_metrics())
        self.processing_tasks.append(metrics_task)
        
        logger.info("✅ Streaming Agent started")
    
    async def stop(self):
        """Stop the streaming agent"""
        logger.info("Stopping Streaming Agent")
        self.is_running = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        # Close Kafka connections
        await self._cleanup_kafka()
        
        logger.info("✅ Streaming Agent stopped")
    
    async def _initialize_kafka(self):
        """Initialize Kafka producers and consumers"""
        # Create shared producer
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_config["bootstrap_servers"],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        
        # Create consumers for each processor
        for processor_id, processor_info in self.processors.items():
            config = processor_info["config"]
            
            consumer = AIOKafkaConsumer(
                *config.input_topics,
                bootstrap_servers=self.kafka_config["bootstrap_servers"],
                group_id=f"{self.kafka_config['group_id']}_{processor_id}",
                auto_offset_reset=self.kafka_config["auto_offset_reset"],
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            await consumer.start()
            self.consumers[processor_id] = consumer
    
    async def _cleanup_kafka(self):
        """Clean up Kafka connections"""
        # Stop producer
        if hasattr(self, 'producer'):
            await self.producer.stop()
        
        # Stop consumers
        for consumer in self.consumers.values():
            await consumer.stop()
    
    async def _process_stream(self, processor_id: str, processor_info: Dict[str, Any]):
        """Process stream for a specific processor"""
        config = processor_info["config"]
        processor = processor_info["processor"]
        consumer = self.consumers[processor_id]
        stats = self.stats[processor_id]
        
        logger.info(f"Started stream processing for {config.name}")
        
        message_batch = []
        last_batch_time = time.time()
        
        try:
            async for msg in consumer:
                if not self.is_running:
                    break
                
                start_time = time.time()
                
                try:
                    # Convert Kafka message to StreamMessage
                    stream_message = StreamMessage(
                        message_id=str(uuid.uuid4()),
                        event_type=StreamEventType(msg.value.get("event_type", "user_action")),
                        timestamp=datetime.fromisoformat(msg.value.get("timestamp", datetime.now().isoformat())),
                        data=msg.value.get("data", {}),
                        source_topic=msg.topic,
                        source_partition=msg.partition,
                        source_offset=msg.offset,
                        headers=msg.value.get("headers", {})
                    )
                    
                    # Add to batch or process immediately
                    if config.batch_size > 1:
                        message_batch.append(stream_message)
                        
                        # Process batch if full or timeout
                        current_time = time.time()
                        batch_full = len(message_batch) >= config.batch_size
                        batch_timeout = (current_time - last_batch_time) * 1000 >= config.batch_timeout_ms
                        
                        if batch_full or batch_timeout:
                            await self._process_message_batch(processor, message_batch, config, stats)
                            message_batch = []
                            last_batch_time = current_time
                    else:
                        # Process single message
                        await self._process_single_message(processor, stream_message, config, stats)
                    
                    # Update latency metrics
                    processing_time = (time.time() - start_time) * 1000
                    self.latency_buffer.append(processing_time)
                    
                except Exception as e:
                    logger.error(f"Error processing message in {processor_id}: {str(e)}")
                    stats.messages_failed += 1
        
        except Exception as e:
            logger.error(f"Stream processing error for {processor_id}: {str(e)}")
        finally:
            # Process any remaining messages in batch
            if message_batch:
                await self._process_message_batch(processor, message_batch, config, stats)
    
    async def _process_single_message(self, processor: StreamingEventProcessor, 
                                    message: StreamMessage, config: StreamProcessor, 
                                    stats: StreamingStats):
        """Process a single message"""
        start_time = time.time()
        
        try:
            result = await processor.process_message(message)
            
            if result:
                # Send result to output topics
                for topic in config.output_topics:
                    await self._send_message(topic, result)
            
            processing_time = time.time() - start_time
            stats.messages_processed += 1
            stats.total_processing_time += processing_time
            
        except Exception as e:
            logger.error(f"Single message processing error: {str(e)}")
            stats.messages_failed += 1
            
            if config.error_handling == "dead_letter":
                await self._send_to_dead_letter(message, str(e))
    
    async def _process_message_batch(self, processor: StreamingEventProcessor, 
                                   messages: List[StreamMessage], config: StreamProcessor, 
                                   stats: StreamingStats):
        """Process a batch of messages"""
        start_time = time.time()
        
        try:
            results = await processor.process_batch(messages)
            
            # Send results to output topics
            for result in results:
                if result:
                    for topic in config.output_topics:
                        await self._send_message(topic, result)
            
            processing_time = time.time() - start_time
            stats.messages_processed += len(messages)
            stats.total_processing_time += processing_time
            
        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            stats.messages_failed += len(messages)
    
    async def _send_message(self, topic: str, message: StreamMessage):
        """Send message to Kafka topic"""
        try:
            message_data = {
                "message_id": message.message_id,
                "event_type": message.event_type.value,
                "timestamp": message.timestamp.isoformat(),
                "data": message.data,
                "headers": message.headers,
                "metadata": message.metadata
            }
            
            await self.producer.send_and_wait(topic, message_data)
            
        except Exception as e:
            logger.error(f"Error sending message to {topic}: {str(e)}")
    
    async def _send_to_dead_letter(self, message: StreamMessage, error: str):
        """Send failed message to dead letter queue"""
        dead_letter_topic = "dead_letter_queue"
        
        dead_letter_message = {
            "original_message": {
                "message_id": message.message_id,
                "event_type": message.event_type.value,
                "timestamp": message.timestamp.isoformat(),
                "data": message.data
            },
            "error": error,
            "failed_at": datetime.now().isoformat()
        }
        
        await self.producer.send_and_wait(dead_letter_topic, dead_letter_message)
    
    async def _collect_metrics(self):
        """Collect and update streaming metrics"""
        last_message_count = 0
        last_time = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Calculate throughput
                total_messages = sum(stats.messages_processed for stats in self.stats.values())
                time_diff = current_time - last_time
                
                if time_diff > 0:
                    throughput = (total_messages - last_message_count) / time_diff
                    self.throughput_buffer.append(throughput)
                
                # Update individual processor stats
                for processor_id, stats in self.stats.items():
                    if stats.messages_processed > 0:
                        stats.average_latency = stats.total_processing_time / stats.messages_processed * 1000
                        stats.throughput_per_second = stats.messages_processed / max(1, time_diff)
                        stats.error_rate = stats.messages_failed / (stats.messages_processed + stats.messages_failed) * 100
                    
                    stats.last_updated = datetime.now()
                
                # Calculate latency percentiles
                if self.latency_buffer:
                    latencies = sorted(self.latency_buffer)
                    percentiles = {
                        "p50": latencies[len(latencies) // 2],
                        "p90": latencies[int(len(latencies) * 0.9)],
                        "p95": latencies[int(len(latencies) * 0.95)],
                        "p99": latencies[int(len(latencies) * 0.99)]
                    }
                    
                    for stats in self.stats.values():
                        stats.latency_percentiles = percentiles
                
                last_message_count = total_messages
                last_time = current_time
                
                await asyncio.sleep(5.0)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get streaming statistics"""
        total_processed = sum(stats.messages_processed for stats in self.stats.values())
        total_failed = sum(stats.messages_failed for stats in self.stats.values())
        
        overall_stats = {
            "total_messages_processed": total_processed,
            "total_messages_failed": total_failed,
            "overall_error_rate": total_failed / max(1, total_processed + total_failed) * 100,
            "average_throughput": statistics.mean(self.throughput_buffer) if self.throughput_buffer else 0,
            "processor_count": len(self.processors),
            "is_running": self.is_running
        }
        
        processor_stats = {}
        for processor_id, stats in self.stats.items():
            processor_stats[processor_id] = {
                "messages_processed": stats.messages_processed,
                "messages_failed": stats.messages_failed,
                "average_latency_ms": stats.average_latency,
                "throughput_per_second": stats.throughput_per_second,
                "error_rate": stats.error_rate,
                "latency_percentiles": stats.latency_percentiles,
                "last_updated": stats.last_updated.isoformat()
            }
        
        return {
            "overall": overall_stats,
            "processors": processor_stats
        }

# Usage Example and Template Testing
async def main():
    """Example usage of Streaming Agent Template"""
    
    # Initialize the agent
    agent = StreamingAgent()
    
    # Create processors
    content_moderator = RealTimeContentModerator()
    engagement_analyzer = LiveEngagementAnalyzer()
    ml_inference = StreamingMLInference()
    
    # Configure stream processors
    moderation_processor = StreamProcessor(
        processor_id="content_moderation",
        name="Real-time Content Moderation",
        input_topics=["user_content"],
        output_topics=["moderation_alerts"],
        processing_function=content_moderator.process_message,
        latency_requirement=ProcessingLatency.LOW,
        batch_size=10,
        batch_timeout_ms=100
    )
    
    engagement_processor = StreamProcessor(
        processor_id="engagement_analysis",
        name="Live Engagement Analysis",
        input_topics=["user_engagement"],
        output_topics=["engagement_analytics"],
        processing_function=engagement_analyzer.process_message,
        latency_requirement=ProcessingLatency.MEDIUM,
        batch_size=5,
        batch_timeout_ms=200
    )
    
    inference_processor = StreamProcessor(
        processor_id="ml_inference",
        name="Real-time ML Inference",
        input_topics=["inference_requests"],
        output_topics=["ml_inference_results"],
        processing_function=ml_inference.process_message,
        latency_requirement=ProcessingLatency.MEDIUM,
        batch_size=20,
        batch_timeout_ms=50
    )
    
    # Register processors
    agent.register_processor(moderation_processor, content_moderator)
    agent.register_processor(engagement_processor, engagement_analyzer)
    agent.register_processor(inference_processor, ml_inference)
    
    try:
        # Note: In a real implementation, you would have Kafka running
        # For this demo, we'll simulate the startup process
        print("🌊 Streaming Agent Demo")
        print("✅ Processors registered:")
        print(f"  - {moderation_processor.name}")
        print(f"  - {engagement_processor.name}")
        print(f"  - {inference_processor.name}")
        
        # Simulate some processing
        print("\n🔄 Simulating stream processing...")
        
        # Simulate processing statistics
        agent.stats["content_moderation"].messages_processed = 1250
        agent.stats["content_moderation"].messages_failed = 15
        agent.stats["content_moderation"].average_latency = 8.5
        agent.stats["content_moderation"].throughput_per_second = 125.0
        
        agent.stats["engagement_analysis"].messages_processed = 890
        agent.stats["engagement_analysis"].messages_failed = 5
        agent.stats["engagement_analysis"].average_latency = 15.2
        agent.stats["engagement_analysis"].throughput_per_second = 89.0
        
        agent.stats["ml_inference"].messages_processed = 2340
        agent.stats["ml_inference"].messages_failed = 23
        agent.stats["ml_inference"].average_latency = 45.8
        agent.stats["ml_inference"].throughput_per_second = 234.0
        
        # Get statistics
        stats = agent.get_stats()
        
        print(f"\n📊 Streaming Statistics:")
        print(f"  Total Messages Processed: {stats['overall']['total_messages_processed']:,}")
        print(f"  Total Messages Failed: {stats['overall']['total_messages_failed']:,}")
        print(f"  Overall Error Rate: {stats['overall']['overall_error_rate']:.2f}%")
        print(f"  Active Processors: {stats['overall']['processor_count']}")
        
        print(f"\n📈 Processor Performance:")
        for processor_id, processor_stats in stats['processors'].items():
            print(f"  {processor_id}:")
            print(f"    Messages/sec: {processor_stats['throughput_per_second']:.1f}")
            print(f"    Avg Latency: {processor_stats['average_latency_ms']:.1f}ms")
            print(f"    Error Rate: {processor_stats['error_rate']:.2f}%")
        
        print("\n✅ Streaming Agent demonstration completed!")
        
    except Exception as e:
        logger.error(f"Error in streaming demo: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    print("🌊 Streaming Agent Template demonstration completed!")