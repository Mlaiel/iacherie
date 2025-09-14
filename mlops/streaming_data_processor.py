"""
Enterprise Streaming Data Processor for ML Pipelines
ML Engineer + Backend Senior implementation with real-time data processing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import hashlib
import time

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Types of data streams"""
    AUDIO_STREAM = "audio_stream"
    VIDEO_STREAM = "video_stream"
    TEXT_STREAM = "text_stream"
    IMAGE_STREAM = "image_stream"
    METRIC_STREAM = "metric_stream"
    EVENT_STREAM = "event_stream"
    BEHAVIOR_STREAM = "behavior_stream"


class ProcessingMode(Enum):
    """Stream processing modes"""
    REAL_TIME = "real_time"
    MICRO_BATCH = "micro_batch"
    WINDOWED = "windowed"
    CONTINUOUS = "continuous"


class WindowType(Enum):
    """Window types for stream processing"""
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"
    GLOBAL = "global"


@dataclass
class StreamMessage:
    """Stream message structure"""
    message_id: str
    stream_id: str
    payload: Dict[str, Any]
    timestamp: datetime
    creator_id: Optional[str] = None
    creator_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamConfiguration:
    """Stream processing configuration"""
    stream_id: str
    stream_type: StreamType
    processing_mode: ProcessingMode
    window_type: Optional[WindowType] = None
    window_size: Optional[timedelta] = None
    batch_size: int = 1000
    parallelism: int = 4
    buffer_size: int = 10000
    creator_specific_rules: Dict[str, Any] = field(default_factory=dict)
    processing_functions: List[Callable] = field(default_factory=list)


@dataclass
class ProcessingResult:
    """Stream processing result"""
    result_id: str
    stream_id: str
    original_message_id: str
    processed_payload: Dict[str, Any]
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class StreamProcessor(ABC):
    """Abstract base class for stream processors"""
    
    @abstractmethod
    async def process(self, message: StreamMessage) -> ProcessingResult:
        """Process a single stream message"""
        pass
    
    @abstractmethod
    async def process_batch(self, messages: List[StreamMessage]) -> List[ProcessingResult]:
        """Process a batch of stream messages"""
        pass


class AudioStreamProcessor(StreamProcessor):
    """Audio stream processor for musicians"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
    async def process(self, message: StreamMessage) -> ProcessingResult:
        """Process audio stream message"""
        start_time = time.time()
        
        try:
            # Extract audio features
            audio_data = message.payload.get('audio_data')
            if not audio_data:
                raise ValueError("No audio data in message")
            
            # Simulate audio processing
            features = await self._extract_audio_features(audio_data)
            
            # Apply creator-specific processing
            if message.creator_type == 'musicians':
                features = await self._apply_music_specific_processing(features, message)
            
            result = ProcessingResult(
                result_id=str(uuid.uuid4()),
                stream_id=message.stream_id,
                original_message_id=message.message_id,
                processed_payload={
                    'features': features,
                    'metadata': {
                        'creator_type': message.creator_type,
                        'processing_time': time.time() - start_time
                    }
                },
                processing_time=time.time() - start_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return ProcessingResult(
                result_id=str(uuid.uuid4()),
                stream_id=message.stream_id,
                original_message_id=message.message_id,
                processed_payload={},
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def process_batch(self, messages: List[StreamMessage]) -> List[ProcessingResult]:
        """Process batch of audio messages"""
        results = []
        for message in messages:
            result = await self.process(message)
            results.append(result)
        return results
    
    async def _extract_audio_features(self, audio_data: bytes) -> Dict[str, Any]:
        """Extract features from audio data"""
        # Simulate feature extraction
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            'mfcc': [0.1, 0.2, 0.3],  # Simulated MFCC features
            'spectral_centroid': 1500.0,
            'tempo': 120.0,
            'key': 'C',
            'duration': 3.5
        }
    
    async def _apply_music_specific_processing(self, 
                                            features: Dict[str, Any], 
                                            message: StreamMessage) -> Dict[str, Any]:
        """Apply music-specific processing"""
        # Add music-specific analysis
        features['genre_prediction'] = 'electronic'
        features['mood'] = 'upbeat'
        features['energy_level'] = 0.8
        
        return features


class TextStreamProcessor(StreamProcessor):
    """Text stream processor for bloggers and content creators"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
    async def process(self, message: StreamMessage) -> ProcessingResult:
        """Process text stream message"""
        start_time = time.time()
        
        try:
            # Extract text data
            text_data = message.payload.get('text_data')
            if not text_data:
                raise ValueError("No text data in message")
            
            # Process text
            analysis = await self._analyze_text(text_data)
            
            # Apply creator-specific processing
            if message.creator_type == 'bloggers':
                analysis = await self._apply_blog_specific_processing(analysis, message)
            
            result = ProcessingResult(
                result_id=str(uuid.uuid4()),
                stream_id=message.stream_id,
                original_message_id=message.message_id,
                processed_payload={
                    'analysis': analysis,
                    'metadata': {
                        'creator_type': message.creator_type,
                        'processing_time': time.time() - start_time
                    }
                },
                processing_time=time.time() - start_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return ProcessingResult(
                result_id=str(uuid.uuid4()),
                stream_id=message.stream_id,
                original_message_id=message.message_id,
                processed_payload={},
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def process_batch(self, messages: List[StreamMessage]) -> List[ProcessingResult]:
        """Process batch of text messages"""
        results = []
        for message in messages:
            result = await self.process(message)
            results.append(result)
        return results
    
    async def _analyze_text(self, text_data: str) -> Dict[str, Any]:
        """Analyze text content"""
        # Simulate text analysis
        await asyncio.sleep(0.05)  # Simulate processing time
        
        return {
            'word_count': len(text_data.split()),
            'sentiment': 'positive',
            'sentiment_score': 0.8,
            'topics': ['technology', 'innovation'],
            'readability_score': 85.0,
            'language': 'en'
        }
    
    async def _apply_blog_specific_processing(self, 
                                            analysis: Dict[str, Any], 
                                            message: StreamMessage) -> Dict[str, Any]:
        """Apply blog-specific processing"""
        # Add blog-specific analysis
        analysis['seo_score'] = 0.75
        analysis['engagement_prediction'] = 0.82
        analysis['viral_potential'] = 0.65
        
        return analysis


class ImageStreamProcessor(StreamProcessor):
    """Image stream processor for photographers"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
    async def process(self, message: StreamMessage) -> ProcessingResult:
        """Process image stream message"""
        start_time = time.time()
        
        try:
            # Extract image data
            image_data = message.payload.get('image_data')
            if not image_data:
                raise ValueError("No image data in message")
            
            # Process image
            features = await self._extract_image_features(image_data)
            
            # Apply creator-specific processing
            if message.creator_type == 'photographers':
                features = await self._apply_photo_specific_processing(features, message)
            
            result = ProcessingResult(
                result_id=str(uuid.uuid4()),
                stream_id=message.stream_id,
                original_message_id=message.message_id,
                processed_payload={
                    'features': features,
                    'metadata': {
                        'creator_type': message.creator_type,
                        'processing_time': time.time() - start_time
                    }
                },
                processing_time=time.time() - start_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return ProcessingResult(
                result_id=str(uuid.uuid4()),
                stream_id=message.stream_id,
                original_message_id=message.message_id,
                processed_payload={},
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def process_batch(self, messages: List[StreamMessage]) -> List[ProcessingResult]:
        """Process batch of image messages"""
        results = []
        for message in messages:
            result = await self.process(message)
            results.append(result)
        return results
    
    async def _extract_image_features(self, image_data: bytes) -> Dict[str, Any]:
        """Extract features from image data"""
        # Simulate image processing
        await asyncio.sleep(0.2)  # Simulate processing time
        
        return {
            'dimensions': [1920, 1080],
            'color_histogram': [0.3, 0.4, 0.3],
            'dominant_colors': ['#FF5733', '#33FF57'],
            'sharpness': 0.85,
            'brightness': 0.65,
            'contrast': 0.75
        }
    
    async def _apply_photo_specific_processing(self, 
                                             features: Dict[str, Any], 
                                             message: StreamMessage) -> Dict[str, Any]:
        """Apply photography-specific processing"""
        # Add photography-specific analysis
        features['aesthetic_score'] = 0.88
        features['style'] = 'portrait'
        features['composition_score'] = 0.92
        features['market_appeal'] = 0.78
        
        return features


class StreamingDataProcessor:
    """Enterprise streaming data processor for ML pipelines"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.streams: Dict[str, StreamConfiguration] = {}
        self.processors: Dict[StreamType, StreamProcessor] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        self.metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'messages_processed': 0,
            'processing_time_total': 0.0,
            'errors': 0,
            'throughput': 0.0
        })
        
        # Creator-specific processing configurations
        self.creator_configs = {
            'musicians': {
                'preferred_batch_size': 100,
                'processing_priority': 'high',
                'feature_extraction': 'advanced_audio',
                'real_time_requirements': True
            },
            'photographers': {
                'preferred_batch_size': 50,
                'processing_priority': 'high',
                'feature_extraction': 'advanced_vision',
                'real_time_requirements': False
            },
            'bloggers': {
                'preferred_batch_size': 200,
                'processing_priority': 'medium',
                'feature_extraction': 'nlp_advanced',
                'real_time_requirements': False
            },
            'influencers': {
                'preferred_batch_size': 150,
                'processing_priority': 'high',
                'feature_extraction': 'multi_modal',
                'real_time_requirements': True
            },
            'comedians': {
                'preferred_batch_size': 75,
                'processing_priority': 'medium',
                'feature_extraction': 'video_audio',
                'real_time_requirements': False
            }
        }
        
    async def initialize(self) -> bool:
        """Initialize streaming data processor"""
        try:
            logger.info("Initializing Streaming Data Processor...")
            
            # Setup processors
            await self._setup_processors()
            
            # Initialize metrics collection
            await self._setup_metrics_collection()
            
            logger.info("Streaming Data Processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Streaming Data Processor: {e}")
            return False
    
    async def create_stream(self, config: StreamConfiguration) -> bool:
        """Create new data stream"""
        try:
            self.streams[config.stream_id] = config
            
            # Create message queue for stream
            queue_size = config.buffer_size
            self.message_queues[config.stream_id] = asyncio.Queue(maxsize=queue_size)
            
            # Start processing task
            task = asyncio.create_task(self._process_stream(config))
            self.processing_tasks[config.stream_id] = task
            
            logger.info(f"Created stream: {config.stream_id} ({config.stream_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create stream: {e}")
            return False
    
    async def send_message(self, stream_id: str, message: StreamMessage) -> bool:
        """Send message to stream"""
        try:
            if stream_id not in self.message_queues:
                logger.error(f"Stream {stream_id} not found")
                return False
            
            queue = self.message_queues[stream_id]
            
            # Apply creator-specific optimizations
            message = await self._optimize_message_for_creator(message)
            
            await queue.put(message)
            return True
            
        except asyncio.QueueFull:
            logger.warning(f"Queue full for stream {stream_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def get_stream_metrics(self, stream_id: Optional[str] = None) -> Dict[str, Any]:
        """Get processing metrics for streams"""
        try:
            if stream_id:
                return self.metrics.get(stream_id, {})
            
            return dict(self.metrics)
            
        except Exception as e:
            logger.error(f"Failed to get stream metrics: {e}")
            return {}
    
    async def stop_stream(self, stream_id: str) -> bool:
        """Stop processing stream"""
        try:
            if stream_id in self.processing_tasks:
                self.processing_tasks[stream_id].cancel()
                del self.processing_tasks[stream_id]
            
            if stream_id in self.message_queues:
                del self.message_queues[stream_id]
            
            if stream_id in self.streams:
                del self.streams[stream_id]
            
            logger.info(f"Stopped stream: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop stream: {e}")
            return False
    
    async def get_processing_backlog(self, stream_id: str) -> int:
        """Get processing backlog for stream"""
        try:
            if stream_id not in self.message_queues:
                return 0
            
            return self.message_queues[stream_id].qsize()
            
        except Exception as e:
            logger.error(f"Failed to get backlog: {e}")
            return 0
    
    async def _setup_processors(self) -> None:
        """Setup stream processors for different data types"""
        self.processors[StreamType.AUDIO_STREAM] = AudioStreamProcessor()
        self.processors[StreamType.TEXT_STREAM] = TextStreamProcessor()
        self.processors[StreamType.IMAGE_STREAM] = ImageStreamProcessor()
        
        # Add more processors as needed
        # self.processors[StreamType.VIDEO_STREAM] = VideoStreamProcessor()
        # self.processors[StreamType.METRIC_STREAM] = MetricStreamProcessor()
    
    async def _setup_metrics_collection(self) -> None:
        """Setup metrics collection system"""
        # Start metrics collection task
        asyncio.create_task(self._collect_metrics())
    
    async def _process_stream(self, config -> None: StreamConfiguration) -> None:
        """Process messages from stream"""
        stream_id = config.stream_id
        queue = self.message_queues[stream_id]
        processor = self.processors.get(config.stream_type)
        
        if not processor:
            logger.error(f"No processor found for stream type: {config.stream_type}")
            return
        
        logger.info(f"Started processing stream: {stream_id}")
        
        try:
            if config.processing_mode == ProcessingMode.REAL_TIME:
                await self._process_real_time(queue, processor, config)
            elif config.processing_mode == ProcessingMode.MICRO_BATCH:
                await self._process_micro_batch(queue, processor, config)
            elif config.processing_mode == ProcessingMode.WINDOWED:
                await self._process_windowed(queue, processor, config)
            else:
                await self._process_continuous(queue, processor, config)
                
        except asyncio.CancelledError:
            logger.info(f"Stream processing cancelled: {stream_id}")
        except Exception as e:
            logger.error(f"Stream processing error: {e}")
    
    async def _process_real_time(self, 
                               queue -> None: asyncio.Queue,
                               processor -> None: StreamProcessor,
                               config -> None: StreamConfiguration) -> None:
        """Process messages in real-time mode"""
        while True:
            try:
                message = await queue.get()
                start_time = time.time()
                
                # Process message
                result = await processor.process(message)
                
                # Update metrics
                processing_time = time.time() - start_time
                await self._update_metrics(config.stream_id, processing_time, result.success)
                
                # Handle result
                await self._handle_processing_result(result)
                
                queue.task_done()
                
            except Exception as e:
                logger.error(f"Real-time processing error: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_micro_batch(self, 
                                 queue -> None: asyncio.Queue,
                                 processor -> None: StreamProcessor,
                                 config -> None: StreamConfiguration) -> None:
        """Process messages in micro-batch mode"""
        batch_size = config.batch_size
        batch = []
        
        while True:
            try:
                # Collect batch
                try:
                    # Wait for first message
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    batch.append(message)
                    
                    # Collect remaining messages up to batch size
                    while len(batch) < batch_size:
                        try:
                            message = queue.get_nowait()
                            batch.append(message)
                        except asyncio.QueueEmpty:
                            break
                            
                except asyncio.TimeoutError:
                    # No messages, continue
                    continue
                
                if batch:
                    start_time = time.time()
                    
                    # Process batch
                    results = await processor.process_batch(batch)
                    
                    # Update metrics
                    processing_time = time.time() - start_time
                    success_count = sum(1 for r in results if r.success)
                    
                    for _ in range(len(batch)):
                        await self._update_metrics(
                            config.stream_id, 
                            processing_time / len(batch),
                            success_count / len(batch) > 0.8
                        )
                        queue.task_done()
                    
                    # Handle results
                    for result in results:
                        await self._handle_processing_result(result)
                    
                    batch.clear()
                
            except Exception as e:
                logger.error(f"Micro-batch processing error: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_windowed(self, 
                              queue -> None: asyncio.Queue,
                              processor -> None: StreamProcessor,
                              config -> None: StreamConfiguration) -> None:
        """Process messages using windowing"""
        window_size = config.window_size or timedelta(seconds=10)
        window_messages = []
        window_start = datetime.utcnow()
        
        while True:
            try:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    window_messages.append(message)
                    
                    # Check if window is complete
                    current_time = datetime.utcnow()
                    if current_time - window_start >= window_size:
                        # Process window
                        if window_messages:
                            start_time = time.time()
                            results = await processor.process_batch(window_messages)
                            
                            # Update metrics and handle results
                            processing_time = time.time() - start_time
                            for result in results:
                                await self._update_metrics(
                                    config.stream_id, 
                                    processing_time / len(window_messages),
                                    result.success
                                )
                                await self._handle_processing_result(result)
                                queue.task_done()
                            
                            window_messages.clear()
                            window_start = current_time
                        
                except asyncio.TimeoutError:
                    # Check if window should be processed anyway
                    current_time = datetime.utcnow()
                    if (current_time - window_start >= window_size and 
                        window_messages):
                        # Process partial window
                        start_time = time.time()
                        results = await processor.process_batch(window_messages)
                        
                        processing_time = time.time() - start_time
                        for result in results:
                            await self._update_metrics(
                                config.stream_id, 
                                processing_time / len(window_messages),
                                result.success
                            )
                            await self._handle_processing_result(result)
                            queue.task_done()
                        
                        window_messages.clear()
                        window_start = current_time
                
            except Exception as e:
                logger.error(f"Windowed processing error: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_continuous(self, 
                                queue -> None: asyncio.Queue,
                                processor -> None: StreamProcessor,
                                config -> None: StreamConfiguration) -> None:
        """Process messages in continuous mode"""
        # Similar to real-time but with different batching strategy
        await self._process_real_time(queue, processor, config)
    
    async def _optimize_message_for_creator(self, message: StreamMessage) -> StreamMessage:
        """Optimize message processing based on creator type"""
        if message.creator_type in self.creator_configs:
            creator_config = self.creator_configs[message.creator_type]
            
            # Add creator-specific processing context
            message.processing_context.update({
                'priority': creator_config['processing_priority'],
                'feature_extraction': creator_config['feature_extraction'],
                'real_time_required': creator_config['real_time_requirements']
            })
        
        return message
    
    async def _handle_processing_result(self, result -> None: ProcessingResult) -> None:
        """Handle processing result"""
        try:
            if result.success:
                # Store or forward processed data
                logger.debug(f"Processed message {result.original_message_id} successfully")
            else:
                logger.warning(f"Failed to process message {result.original_message_id}: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Failed to handle processing result: {e}")
    
    async def _update_metrics(self, stream_id -> None: str, processing_time -> None: float, success -> None: bool) -> None:
        """Update processing metrics"""
        try:
            metrics = self.metrics[stream_id]
            metrics['messages_processed'] += 1
            metrics['processing_time_total'] += processing_time
            
            if not success:
                metrics['errors'] += 1
            
            # Calculate throughput (messages per second)
            if metrics['messages_processed'] > 0:
                avg_processing_time = metrics['processing_time_total'] / metrics['messages_processed']
                metrics['throughput'] = 1.0 / avg_processing_time if avg_processing_time > 0 else 0
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    async def _collect_metrics(self) -> None:
        """Collect and log metrics periodically"""
        while True:
            try:
                # Log metrics every 60 seconds
                await asyncio.sleep(60)
                
                for stream_id, metrics in self.metrics.items():
                    logger.info(f"Stream {stream_id} metrics: {metrics}")
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")


# Example usage and testing
async def main() -> None:
    """Example usage of Streaming Data Processor"""
    processor = StreamingDataProcessor()
    
    # Initialize
    await processor.initialize()
    
    # Create audio stream for musicians
    audio_config = StreamConfiguration(
        stream_id="musician_audio_stream",
        stream_type=StreamType.AUDIO_STREAM,
        processing_mode=ProcessingMode.REAL_TIME,
        batch_size=50,
        parallelism=2
    )
    
    await processor.create_stream(audio_config)
    
    # Send test messages
    for i in range(10):
        message = StreamMessage(
            message_id=str(uuid.uuid4()),
            stream_id="musician_audio_stream",
            payload={'audio_data': b'fake_audio_data'},
            timestamp=datetime.utcnow(),
            creator_id="musician123",
            creator_type="musicians"
        )
        
        await processor.send_message("musician_audio_stream", message)
    
    # Wait a bit and check metrics
    await asyncio.sleep(5)
    
    metrics = await processor.get_stream_metrics("musician_audio_stream")
    print(f"Stream Metrics: {json.dumps(metrics, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())