"""Real-time Streaming Aggregation
================================

Real-time data processing and streaming aggregation with change streams.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class StreamingAggregation:
    """Real-time streaming aggregation processor."""
    
    def __init__(self):
        """Initialize streaming aggregation."""
        self._running = False
        self._stream_handlers: Dict[str, Callable] = {}
        self._real_time_metrics: Dict[str, Any] = {}
        self._update_lock = threading.Lock()
    
    def start_streaming(self):
        """Start real-time streaming processing."""
        self._running = True
        logger.info("Streaming aggregation started")
    
    def stop_streaming(self):
        """Stop streaming processing."""
        self._running = False
        logger.info("Streaming aggregation stopped")
    
    def register_stream_handler(self, collection: str, handler: Callable):
        """Register handler for collection change streams."""
        self._stream_handlers[collection] = handler
        logger.info(f"Registered stream handler for collection: {collection}")
    
    def process_change_event(self, collection: str, change_event: Dict[str, Any]):
        """Process a change stream event."""
        if collection in self._stream_handlers:
            try:
                self._stream_handlers[collection](change_event)
            except Exception as e:
                logger.error(f"Error processing change event for {collection}: {e}")
    
    def update_real_time_metric(self, metric_name: str, value: Any):
        """Update real-time metric."""
        with self._update_lock:
            self._real_time_metrics[metric_name] = {
                "value": value,
                "updated_at": datetime.utcnow()
            }
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics."""
        with self._update_lock:
            return self._real_time_metrics.copy()

_default_streaming: Optional[StreamingAggregation] = None

def get_streaming_aggregation() -> StreamingAggregation:
    global _default_streaming
    if _default_streaming is None:
        _default_streaming = StreamingAggregation()
    return _default_streaming

__all__ = ['StreamingAggregation', 'get_streaming_aggregation']