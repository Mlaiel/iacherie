"""
Real-time Intent Detection Engine

High-performance intent detection system for real-time conversational interfaces
with advanced preprocessing, feature extraction, and streaming capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, AsyncGenerator, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import json

import numpy as np
from collections import deque
import torch

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...utils.text_processors import TextPreprocessor
from ...utils.rate_limiter import RateLimiter
from .intent_classifier import IntentClassifier, ClassificationResult, IntentCategory
from .config import IntentRecognitionConfig
from .exceptions import ClassificationError


class DetectionMode(Enum):
    """Intent detection operation modes"""
    REALTIME = "realtime"           # Sub-100ms response time
    BATCH = "batch"                 # Optimized for throughput
    STREAMING = "streaming"         # Continuous processing
    INTERACTIVE = "interactive"     # Conversational UI optimized


@dataclass
class DetectionRequest:
    """Intent detection request with metadata"""
    text: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    priority: int = 1  # 1=highest, 5=lowest
    mode: DetectionMode = DetectionMode.REALTIME
    timeout_ms: int = 500
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = field(default_factory=lambda: f"req_{int(time.time() * 1000)}")


@dataclass
class DetectionResponse:
    """Intent detection response with performance metrics"""
    request_id: str
    result: ClassificationResult
    processing_time_ms: float
    queue_time_ms: float = 0.0
    cache_hit: bool = False
    model_used: str = "primary"
    timestamp: datetime = field(default_factory=datetime.now)


class RealTimeIntentProcessor:
    """
    High-performance real-time intent processing engine
    
    Features:
    - Sub-100ms response times for real-time detection
    - Intelligent request queuing and prioritization
    - Adaptive caching and precomputation
    - Performance monitoring and optimization
    - Graceful degradation under load
    """
    
    def __init__(self, classifier: IntentClassifier, config: IntentRecognitionConfig):
        self.classifier = classifier
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("intent_detector")
        
        # Request processing
        self.request_queue = asyncio.Queue(maxsize=config.max_queue_size)
        self.processing_tasks = []
        self.rate_limiter = RateLimiter(
            max_requests=config.max_requests_per_second,
            time_window=1.0
        )
        
        # Performance optimization
        self.response_cache = {}
        self.precomputed_embeddings = {}
        self.performance_stats = {
            'total_requests': 0,
            'avg_response_time': 0.0,
            'cache_hit_rate': 0.0,
            'queue_overflow_count': 0
        }
        
        # Background processing
        self._start_background_processors()
    
    def _start_background_processors(self) -> None:
        """Start background processing tasks"""
        # Start request processors
        for i in range(self.config.processor_threads):
            task = asyncio.create_task(self._process_requests())
            self.processing_tasks.append(task)
        
        # Start cache cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_cache())
        self.processing_tasks.append(cleanup_task)
        
        # Start metrics collection task
        metrics_task = asyncio.create_task(self._collect_metrics())
        self.processing_tasks.append(metrics_task)
    
    async def detect_intent_async(
        self,
        request: DetectionRequest
    ) -> DetectionResponse:
        """
        Asynchronously detect intent with performance optimization
        
        Args:
            request: Detection request with input text and metadata
            
        Returns:
            Detection response with classification result and metrics
        """
        start_time = time.time()
        
        try:
            # Rate limiting check
            if not await self.rate_limiter.acquire(request.user_id or "anonymous"):
                raise ClassificationError("Rate limit exceeded")
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                response = DetectionResponse(
                    request_id=request.request_id,
                    result=cached_result,
                    processing_time_ms=(time.time() - start_time) * 1000,
                    cache_hit=True
                )
                await self._update_performance_stats(response)
                return response
            
            # Queue request for processing
            queue_start = time.time()
            
            if request.mode == DetectionMode.REALTIME:
                # High priority - process immediately if possible
                result = await self._process_realtime_request(request)
            else:
                # Queue for batch processing
                await self.request_queue.put(request)
                result = await self._wait_for_result(request.request_id, request.timeout_ms)
            
            queue_time = (time.time() - queue_start) * 1000
            processing_time = (time.time() - start_time) * 1000
            
            # Cache successful result
            if result:
                self._cache_result(cache_key, result.result, ttl=self.config.cache_ttl_seconds)
            
            response = DetectionResponse(
                request_id=request.request_id,
                result=result.result if result else self._get_fallback_result(),
                processing_time_ms=processing_time,
                queue_time_ms=queue_time,
                cache_hit=False
            )
            
            await self._update_performance_stats(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Intent detection failed: {str(e)}")
            
            # Return fallback response
            return DetectionResponse(
                request_id=request.request_id,
                result=self._get_fallback_result(),
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    async def _process_realtime_request(self, request: DetectionRequest) -> DetectionResponse:
        """Process high-priority real-time request immediately"""



        try:
            # Use optimized fast-path classification
            result = await self.classifier.classify_intent(
                text=request.text,
                context=request.context,
                user_id=request.user_id,
                session_id=request.session_id
            )
            
            return DetectionResponse(
                request_id=request.request_id,
                result=result,
                processing_time_ms=0,  # Will be calculated by caller
                model_used="fast_path"
            )
            
        except Exception as e:
            self.logger.error(f"Real-time processing failed: {str(e)}")
            raise
    
    async def _process_requests(self) -> None:
        """Background task to process queued requests"""
        while True:
            try:
                # Get request from queue with timeout
                request = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=1.0
                )
                
                # Process request
                start_time = time.time()
                
                result = await self.classifier.classify_intent(
                    text=request.text,
                    context=request.context,
                    user_id=request.user_id,
                    session_id=request.session_id
                )
                
                processing_time = (time.time() - start_time) * 1000
                
                response = DetectionResponse(
                    request_id=request.request_id,
                    result=result,
                    processing_time_ms=processing_time,
                    model_used="background"
                )
                
                # Store result for retrieval
                self._store_result(request.request_id, response)
                
                # Mark task as done
                self.request_queue.task_done()
                
            except asyncio.TimeoutError:
                # No requests in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Request processing error: {str(e)}")
                continue
    
    def _generate_cache_key(self, request: DetectionRequest) -> str:
        """Generate cache key for request"""
        key_components = [
            request.text.lower().strip(),
            request.user_id or "anonymous",
            str(request.mode.value)
        ]
        
        # Add context hash if available
        if request.context:
            context_str = json.dumps(request.context, sort_keys=True)
            key_components.append(str(hash(context_str)))
        
        return "|".join(key_components)
    
    def _get_cached_result(self, cache_key: str) -> Optional[ClassificationResult]:
        """Retrieve cached classification result"""



        try:
            cached_entry = self.response_cache.get(cache_key)
            if cached_entry:
                result, timestamp = cached_entry
                
                # Check if cache entry is still valid
                if datetime.now() - timestamp < timedelta(seconds=self.config.cache_ttl_seconds):
                    return result
                else:
                    # Remove expired entry
                    del self.response_cache[cache_key]
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Cache retrieval failed: {str(e)}")
            return None
    
    def _cache_result(
        self, 
        cache_key: str, 
        result: ClassificationResult, 
        ttl: int
    ) -> None:
        """Cache classification result"""



        try:
            # Prevent cache from growing too large
            if len(self.response_cache) >= self.config.max_cache_size:
                # Remove oldest entries
                oldest_keys = sorted(
                    self.response_cache.keys(),
                    key=lambda k: self.response_cache[k][1]
                )[:self.config.max_cache_size // 4]
                
                for key in oldest_keys:
                    del self.response_cache[key]
            
            # Store result with timestamp
            self.response_cache[cache_key] = (result, datetime.now())
            
        except Exception as e:
            self.logger.warning(f"Cache storage failed: {str(e)}")
    
    def _get_fallback_result(self) -> ClassificationResult:
        """Get fallback result for failed classifications"""
        from .intent_classifier import IntentConfidence
        
        return ClassificationResult(
            primary_intent=IntentCategory.UNKNOWN,
            confidence=IntentConfidence(primary_score=0.1),
            intent_parameters={'fallback': True},
            processing_time=0.0,
            model_version="fallback"
        )
    
    async def _wait_for_result(
        self, 
        request_id: str, 
        timeout_ms: int
    ) -> Optional[DetectionResponse]:
        """Wait for background processing result"""



        try:
            start_time = time.time()
            timeout_seconds = timeout_ms / 1000.0
            
            while (time.time() - start_time) < timeout_seconds:
                result = self._get_stored_result(request_id)
                if result:
                    return result
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
            
            # Timeout reached
            self.logger.warning(f"Request {request_id} timed out")
            return None
            
        except Exception as e:
            self.logger.error(f"Error waiting for result: {str(e)}")
            return None
    
    def _store_result(self, request_id: str, response: DetectionResponse) -> None:
        """Store processing result for retrieval"""
        # In production, this would use Redis or similar
        # For now, using in-memory storage with size limits
        if not hasattr(self, '_result_store'):
            self._result_store = {}
        
        # Prevent memory leak
        if len(self._result_store) > 1000:
            # Remove oldest entries
            oldest_keys = list(self._result_store.keys())[:500]
            for key in oldest_keys:
                del self._result_store[key]
        
        self._result_store[request_id] = response
    
    def _get_stored_result(self, request_id: str) -> Optional[DetectionResponse]:
        """Retrieve stored processing result"""
        if hasattr(self, '_result_store'):
            return self._result_store.get(request_id)
        return None
    
    async def _cleanup_cache(self) -> None:
        """Background task to clean up expired cache entries"""
        while True:
            try:
                await asyncio.sleep(self.config.cache_cleanup_interval_seconds)
                
                current_time = datetime.now()
                expired_keys = []
                
                for key, (result, timestamp) in self.response_cache.items():
                    if current_time - timestamp > timedelta(seconds=self.config.cache_ttl_seconds):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.response_cache[key]
                
                if expired_keys:
                    self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
            except Exception as e:
                self.logger.error(f"Cache cleanup error: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _collect_metrics(self) -> None:
        """Background task to collect and report performance metrics"""
        while True:
            try:
                await asyncio.sleep(self.config.metrics_interval_seconds)
                
                # Calculate current metrics
                total_requests = self.performance_stats['total_requests']
                
                if total_requests > 0:
                    cache_hit_rate = (
                        sum(1 for _, (_, timestamp) in self.response_cache.items() 
                            if datetime.now() - timestamp < timedelta(hours=1))
                        / total_requests
                    )
                    
                    self.performance_stats['cache_hit_rate'] = cache_hit_rate
                
                # Report metrics
                self.metrics.record_gauge('cache_size', len(self.response_cache))
                self.metrics.record_gauge('queue_size', self.request_queue.qsize())
                self.metrics.record_gauge('cache_hit_rate', self.performance_stats['cache_hit_rate'])
                self.metrics.record_gauge('avg_response_time', self.performance_stats['avg_response_time'])
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _update_performance_stats(self, response: DetectionResponse) -> None:
        """Update performance statistics"""



        try:
            stats = self.performance_stats
            stats['total_requests'] += 1
            
            # Update average response time
            current_avg = stats['avg_response_time']
            new_time = response.processing_time_ms
            total_requests = stats['total_requests']
            
            stats['avg_response_time'] = (
                (current_avg * (total_requests - 1) + new_time) / total_requests
            )
            
            # Record metrics
            self.metrics.record_histogram('response_time_ms', new_time)
            self.metrics.record_counter('requests_processed')
            
            if response.cache_hit:
                self.metrics.record_counter('cache_hits')
            
        except Exception as e:
            self.logger.warning(f"Failed to update performance stats: {str(e)}")


class IntentDetector(BaseService):
    """
    Main intent detection service with multiple operation modes
    
    Features:
    - Real-time and batch detection modes
    - Streaming intent processing for live conversations
    - Performance optimization and monitoring
    - Graceful degradation and error handling
    """
    
    def __init__(self, config: IntentRecognitionConfig):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize classifier and processor
        self.classifier = IntentClassifier(config)
        self.realtime_processor = RealTimeIntentProcessor(self.classifier, config)
        
        # Service state
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize the intent detection service"""



        try:
            self.logger.info("Initializing Intent Detection Service...")
            
            # Initialize classifier
            if hasattr(self.classifier, '_initialize_models'):
                await self.classifier._initialize_models()
            
            self.is_initialized = True
            self.logger.info("Intent Detection Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Service initialization failed: {str(e)}")
            raise
    
    async def detect_intent(
        self,
        text: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        mode: DetectionMode = DetectionMode.REALTIME,
        timeout_ms: int = 500
    ) -> DetectionResponse:
        """
        Detect intent from input text
        
        Args:
            text: Input text to analyze
            user_id: Optional user identifier
            session_id: Optional session identifier
            context: Optional conversation context
            mode: Detection mode (realtime, batch, streaming, interactive)
            timeout_ms: Maximum processing time in milliseconds
            
        Returns:
            Detection response with classification result and metrics
        """
        if not self.is_initialized:
            await self.initialize()
        
        request = DetectionRequest(
            text=text,
            user_id=user_id,
            session_id=session_id,
            context=context,
            mode=mode,
            timeout_ms=timeout_ms
        )
        
        return await self.realtime_processor.detect_intent_async(request)
    
    async def detect_intent_streaming(
        self,
        text_stream: AsyncGenerator[str, None],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[DetectionResponse, None]:
        """
        Process streaming text input for real-time intent detection
        
        Args:
            text_stream: Async generator of text chunks
            user_id: Optional user identifier
            session_id: Optional session identifier
            context: Optional conversation context
            
        Yields:
            Detection responses for each text chunk
        """
        if not self.is_initialized:
            await self.initialize()
        
        accumulated_text = ""
        chunk_count = 0
        
        async for text_chunk in text_stream:
            try:
                accumulated_text += text_chunk
                chunk_count += 1
                
                # Process complete sentences or meaningful chunks
                if self._is_complete_thought(accumulated_text):
                    response = await self.detect_intent(
                        text=accumulated_text,
                        user_id=user_id,
                        session_id=session_id,
                        context=context,
                        mode=DetectionMode.STREAMING
                    )
                    
                    yield response
                    
                    # Reset for next chunk
                    accumulated_text = ""
                    chunk_count = 0
                
            except Exception as e:
                self.logger.error(f"Streaming detection error: {str(e)}")
                continue
        
        # Process any remaining text
        if accumulated_text.strip():
            try:
                response = await self.detect_intent(
                    text=accumulated_text,
                    user_id=user_id,
                    session_id=session_id,
                    context=context,
                    mode=DetectionMode.STREAMING
                )
                yield response
                
            except Exception as e:
                self.logger.error(f"Final chunk detection error: {str(e)}")
    
    def _is_complete_thought(self, text: str) -> bool:
        """Determine if text represents a complete thought for processing"""
        # Simple heuristics for complete thoughts
        text = text.strip()
        
        if len(text) < 3:
            return False
        
        # Check for sentence endings
        if text.endswith(('.', '!', '?')):
            return True
        
        # Check for common complete phrases
        complete_phrases = [
            'upload', 'download', 'create', 'delete', 'share',
            'protect', 'monetize', 'analyze', 'help', 'show'
        ]
        
        if any(phrase in text.lower() for phrase in complete_phrases):
            return len(text.split()) >= 2  # At least action + object
        
        # Long enough text might be complete
        return len(text.split()) >= 5
    
    async def batch_detect_intents(
        self,
        texts: List[str],
        user_ids: Optional[List[str]] = None,
        contexts: Optional[List[Dict[str, Any]]] = None,
        timeout_ms: int = 5000
    ) -> List[DetectionResponse]:
        """
        Detect intents for multiple texts in batch mode
        
        Args:
            texts: List of input texts
            user_ids: Optional list of user identifiers
            contexts: Optional list of conversation contexts
            timeout_ms: Maximum processing time for entire batch
            
        Returns:
            List of detection responses
        """
        if not self.is_initialized:
            await self.initialize()
        
        # Prepare inputs
        if user_ids is None:
            user_ids = [None] * len(texts)
        if contexts is None:
            contexts = [None] * len(texts)
        
        # Create batch requests
        requests = [
            DetectionRequest(
                text=text,
                user_id=user_id,
                context=context,
                mode=DetectionMode.BATCH,
                timeout_ms=timeout_ms // len(texts)  # Distribute timeout
            )
            for text, user_id, context in zip(texts, user_ids, contexts)
        ]
        
        # Process batch
        tasks = [
            self.realtime_processor.detect_intent_async(request)
            for request in requests
        ]
        
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout_ms / 1000.0
            )
            
            # Handle exceptions in responses
            processed_responses = []
            for response in responses:
                if isinstance(response, Exception):
                    self.logger.error(f"Batch detection error: {str(response)}")
                    processed_responses.append(
                        DetectionResponse(
                            request_id="error",
                            result=self.realtime_processor._get_fallback_result(),
                            processing_time_ms=0
                        )
                    )
                else:
                    processed_responses.append(response)
            
            return processed_responses
            
        except asyncio.TimeoutError:
            self.logger.error(f"Batch detection timed out after {timeout_ms}ms")
            return [
                DetectionResponse(
                    request_id="timeout",
                    result=self.realtime_processor._get_fallback_result(),
                    processing_time_ms=timeout_ms
                )
                for _ in texts
            ]
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""



        return {
            'service_initialized': self.is_initialized,
            'classifier_info': self.classifier.get_model_info(),
            'processor_stats': self.realtime_processor.performance_stats,
            'cache_size': len(self.realtime_processor.response_cache),
            'queue_size': self.realtime_processor.request_queue.qsize(),
            'active_tasks': len(self.realtime_processor.processing_tasks)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform service health check"""



        try:
            # Test basic classification
            test_response = await self.detect_intent(
                text="test intent detection",
                mode=DetectionMode.REALTIME,
                timeout_ms=1000
            )
            
            is_healthy = (
                self.is_initialized and
                test_response.result.primary_intent is not None and
                test_response.processing_time_ms < 1000
            )
            
            return {
                'healthy': is_healthy,
                'initialized': self.is_initialized,
                'test_response_time_ms': test_response.processing_time_ms,
                'queue_size': self.realtime_processor.request_queue.qsize(),
                'cache_size': len(self.realtime_processor.response_cache)
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'initialized': self.is_initialized
            }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the service"""



        try:
            self.logger.info("Shutting down Intent Detection Service...")
            
            # Cancel background tasks
            for task in self.realtime_processor.processing_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(
                *self.realtime_processor.processing_tasks,
                return_exceptions=True
            )
            
            # Clear caches
            self.realtime_processor.response_cache.clear()
            
            self.logger.info("Intent Detection Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
