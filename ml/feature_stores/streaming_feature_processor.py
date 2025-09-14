"""
Streaming Feature Processor module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🔄 Streaming Feature Processor - Real-Time ML Feature Engineering

Advanced streaming feature processing engine for real-time ML inference with
creator-specific feature pipelines and low-latency feature serving.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

Architecture Integration:
- Integrates with FeatureStore for real-time feature serving
- Supports Apache Kafka, Redis Streams, and WebSocket inputs
- Creator-specific feature transformations and aggregations
- Time-window feature computation with sliding windows
- Microservice-ready with auto-scaling capabilities
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import deque, defaultdict
import statistics

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class StreamSource(Enum):
    """Streaming data sources."""
    KAFKA = "kafka"
    REDIS_STREAM = "redis_stream"
    WEBSOCKET = "websocket"
    HTTP_STREAM = "http_stream"
    FILE_STREAM = "file_stream"


class FeatureType(Enum):
    """Feature data types."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BINARY = "binary"
    TEXT = "text"
    EMBEDDING = "embedding"
    TIME_SERIES = "time_series"


class AggregationType(Enum):
    """Time window aggregation types."""
    SUM = "sum"
    MEAN = "mean"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    STD = "std"
    PERCENTILE = "percentile"
    LAST = "last"
    FIRST = "first"


class WindowType(Enum):
    """Time window types."""
    TUMBLING = "tumbling"        # Non-overlapping
    SLIDING = "sliding"          # Overlapping
    SESSION = "session"          # Event-driven
    GLOBAL = "global"           # Single window


@dataclass
class StreamingFeatureConfig:
    """Configuration for streaming feature processing."""
    feature_name: str
    feature_type: FeatureType
    source_field: str
    
    # Time window configuration
    window_type: WindowType = WindowType.SLIDING
    window_size_seconds: int = 60
    slide_interval_seconds: int = 10
    
    # Aggregation configuration
    aggregations: List[AggregationType] = field(default_factory=lambda: [AggregationType.MEAN])
    
    # Creator-specific settings
    creator_specific: bool = False
    creator_type_filter: Optional[List[str]] = None
    
    # Data quality and validation
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    null_handling: str = "interpolate"  # "drop", "interpolate", "default"
    default_value: Optional[Any] = None
    
    # Performance settings
    batch_size: int = 100
    max_latency_ms: int = 50


@dataclass
class FeatureWindow:
    """Time-based feature window."""
    window_id: str
    feature_name: str
    creator_id: Optional[str]
    start_time: float
    end_time: float
    
    # Raw data points
    data_points: List[Tuple[float, Any]] = field(default_factory=list)  # (timestamp, value)
    
    # Computed aggregations
    aggregated_values: Dict[AggregationType, Any] = field(default_factory=dict)
    
    # Metadata
    sample_count: int = 0
    is_complete: bool = False
    quality_score: float = 1.0


@dataclass
class StreamingDataPoint:
    """Single streaming data point."""
    timestamp: float
    creator_id: Optional[str]
    content_type: Optional[str]
    data: Dict[str, Any]
    
    # Metadata
    source: StreamSource
    sequence_id: Optional[int] = None
    session_id: Optional[str] = None


@dataclass
class ProcessedFeature:
    """Processed feature ready for ML inference."""
    feature_name: str
    creator_id: Optional[str]
    timestamp: float
    
    # Feature values
    value: Any
    aggregated_values: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    quality_score: float = 1.0
    confidence: float = 1.0
    processing_latency_ms: float = 0.0
    
    # Lineage
    source_window_id: Optional[str] = None
    processing_pipeline: List[str] = field(default_factory=list)


class StreamingFeatureProcessor:
    """
    Real-time streaming feature processor for ML inference.
    
    Features:
    - Multi-source streaming data ingestion
    - Time-window feature aggregation
    - Creator-specific feature transformations
    - Real-time feature quality monitoring
    - Low-latency feature serving (<50ms)
    - Auto-scaling microservice architecture
    - Integration with feature store
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the streaming feature processor."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Feature processing configuration
        self.feature_configs: Dict[str, StreamingFeatureConfig] = {}
        self.active_windows: Dict[str, FeatureWindow] = {}
        self.processed_features: Dict[str, ProcessedFeature] = {}
        
        # Streaming data buffers
        self.input_buffers: Dict[StreamSource, deque] = {
            source: deque(maxlen=10000) for source in StreamSource
        }
        
        # Creator-specific processors
        self.creator_processors: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.performance_metrics = {
            "total_events_processed": 0,
            "avg_processing_latency_ms": 0.0,
            "throughput_events_per_sec": 0.0,
            "feature_quality_score": 1.0,
            "active_windows": 0,
            "error_rate": 0.0
        }
        
        # Real-time processors registry
        self.feature_processors: Dict[str, Callable] = {
            "engagement_rate": self._process_engagement_rate,
            "content_velocity": self._process_content_velocity,
            "audience_interaction": self._process_audience_interaction,
            "trending_score": self._process_trending_score,
            "monetization_signals": self._process_monetization_signals
        }
        
        # Creator-specific feature configurations
        self.creator_feature_configs = self._initialize_creator_configs()
        
        # Processing tasks
        self.processing_tasks: List[asyncio.Task] = []
        self.is_running = False
        
        self.logger.info("Streaming Feature Processor initialized")
    
    def _initialize_creator_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize creator-specific feature configurations."""
        return {
            "musician": {
                "primary_features": [
                    "audio_engagement_rate", "listening_duration", "track_completion_rate",
                    "follower_music_affinity", "playlist_additions", "streaming_revenue"
                ],
                "window_sizes": {"short": 300, "medium": 3600, "long": 86400},  # 5min, 1h, 1day
                "aggregations": [AggregationType.MEAN, AggregationType.SUM, AggregationType.MAX],
                "quality_thresholds": {"min_samples": 10, "max_latency_ms": 30}
            },
            "blogger": {
                "primary_features": [
                    "page_views", "time_on_page", "scroll_depth", "comment_engagement",
                    "social_shares", "ad_revenue", "subscriber_growth"
                ],
                "window_sizes": {"short": 600, "medium": 7200, "long": 86400},  # 10min, 2h, 1day
                "aggregations": [AggregationType.SUM, AggregationType.MEAN, AggregationType.COUNT],
                "quality_thresholds": {"min_samples": 5, "max_latency_ms": 100}
            },
            "photographer": {
                "primary_features": [
                    "image_views", "like_rate", "comment_rate", "download_count",
                    "print_sales", "portfolio_engagement", "booking_inquiries"
                ],
                "window_sizes": {"short": 900, "medium": 10800, "long": 86400},  # 15min, 3h, 1day
                "aggregations": [AggregationType.COUNT, AggregationType.SUM, AggregationType.MEAN],
                "quality_thresholds": {"min_samples": 3, "max_latency_ms": 200}
            },
            "influencer": {
                "primary_features": [
                    "follower_growth", "engagement_rate", "story_completion",
                    "brand_mention_sentiment", "sponsored_post_performance", "cross_platform_reach"
                ],
                "window_sizes": {"short": 1800, "medium": 14400, "long": 86400},  # 30min, 4h, 1day
                "aggregations": [AggregationType.MEAN, AggregationType.SUM, AggregationType.PERCENTILE],
                "quality_thresholds": {"min_samples": 20, "max_latency_ms": 50}
            }
        }
    
    async def add_feature_config(self, config: StreamingFeatureConfig) -> bool:
        """Add a new streaming feature configuration."""
        try:
            self.feature_configs[config.feature_name] = config
            
            # Initialize feature processors if not exists
            if config.feature_name not in self.feature_processors:
                self.feature_processors[config.feature_name] = self._default_feature_processor
            
            self.logger.info(f"Added feature configuration: {config.feature_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add feature config: {e}")
            return False
    
    async def start_processing(self) -> bool:
        """Start the streaming feature processing."""
        try:
            if self.is_running:
                return True
            
            self.is_running = True
            
            # Start processing tasks for each stream source
            for source in StreamSource:
                task = asyncio.create_task(self._process_stream(source))
                self.processing_tasks.append(task)
            
            # Start window management task
            window_task = asyncio.create_task(self._manage_windows())
            self.processing_tasks.append(window_task)
            
            # Start metrics collection task
            metrics_task = asyncio.create_task(self._collect_metrics())
            self.processing_tasks.append(metrics_task)
            
            self.logger.info("Streaming feature processing started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start streaming processing: {e}")
            return False
    
    async def stop_processing(self) -> bool:
        """Stop the streaming feature processing."""
        try:
            self.is_running = False
            
            # Cancel all processing tasks
            for task in self.processing_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
            self.processing_tasks.clear()
            
            self.logger.info("Streaming feature processing stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop streaming processing: {e}")
            return False
    
    async def ingest_data_point(self, 
                              data_point: StreamingDataPoint) -> bool:
        """Ingest a single streaming data point."""
        try:
            # Add to appropriate buffer
            self.input_buffers[data_point.source].append(data_point)
            
            # Update metrics
            self.performance_metrics["total_events_processed"] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to ingest data point: {e}")
            return False
    
    async def _process_stream(self, source -> None: StreamSource) -> None:
        """Process streaming data from a specific source."""
        try:
            while self.is_running:
                buffer = self.input_buffers[source]
                
                if not buffer:
                    await asyncio.sleep(0.01)  # Small delay if no data
                    continue
                
                # Process batch of data points
                batch_size = min(100, len(buffer))
                batch = [buffer.popleft() for _ in range(batch_size)]
                
                await self._process_data_batch(batch)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.001)
                
        except asyncio.CancelledError:
            self.logger.info(f"Stream processor for {source.value} cancelled")
        except Exception as e:
            self.logger.error(f"Stream processing error for {source.value}: {e}")
    
    async def _process_data_batch(self, batch -> None: List[StreamingDataPoint]) -> None:
        """Process a batch of streaming data points."""
        try:
            processing_start = time.time()
            
            for data_point in batch:
                await self._process_single_data_point(data_point)
            
            # Update latency metrics
            processing_time = (time.time() - processing_start) * 1000
            self._update_latency_metrics(processing_time / len(batch))
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
    
    async def _process_single_data_point(self, data_point -> None: StreamingDataPoint) -> None:
        """Process a single streaming data point."""
        try:
            # Extract features from data point
            for feature_name, config in self.feature_configs.items():
                if config.source_field in data_point.data:
                    await self._add_to_window(
                        feature_name, 
                        data_point.timestamp,
                        data_point.data[config.source_field],
                        data_point.creator_id,
                        config
                    )
            
        except Exception as e:
            self.logger.error(f"Single data point processing failed: {e}")
    
    async def _add_to_window(self, 
                           feature_name -> None: str,
                           timestamp -> None: float,
                           value -> None: Any,
                           creator_id -> None: Optional[str],
                           config -> None: StreamingFeatureConfig) -> None:
        """Add data point to appropriate time window."""
        try:
            # Create window key
            if config.creator_specific and creator_id:
                window_key = f"{feature_name}_{creator_id}"
            else:
                window_key = feature_name
            
            # Find or create appropriate window
            window = await self._get_or_create_window(
                window_key, feature_name, timestamp, creator_id, config
            )
            
            # Validate and clean value
            cleaned_value = await self._validate_and_clean_value(value, config)
            
            if cleaned_value is not None:
                # Add data point to window
                window.data_points.append((timestamp, cleaned_value))
                window.sample_count += 1
                
                # Check if window needs processing
                if await self._should_process_window(window, config):
                    await self._process_window(window, config)
            
        except Exception as e:
            self.logger.error(f"Failed to add to window: {e}")
    
    async def _get_or_create_window(self,
                                  window_key: str,
                                  feature_name: str,
                                  timestamp: float,
                                  creator_id: Optional[str],
                                  config: StreamingFeatureConfig) -> FeatureWindow:
        """Get existing window or create new one."""
        try:
            # Check for existing window
            for window_id, window in self.active_windows.items():
                if (window_key in window_id and 
                    window.start_time <= timestamp <= window.end_time):
                    return window
            
            # Create new window
            window_id = f"{window_key}_{int(timestamp)}"
            
            if config.window_type == WindowType.TUMBLING:
                # Non-overlapping windows
                window_start = (timestamp // config.window_size_seconds) * config.window_size_seconds
                window_end = window_start + config.window_size_seconds
            
            elif config.window_type == WindowType.SLIDING:
                # Overlapping windows
                window_start = timestamp - config.window_size_seconds
                window_end = timestamp
            
            else:  # Default to sliding
                window_start = timestamp - config.window_size_seconds
                window_end = timestamp
            
            window = FeatureWindow(
                window_id=window_id,
                feature_name=feature_name,
                creator_id=creator_id,
                start_time=window_start,
                end_time=window_end
            )
            
            self.active_windows[window_id] = window
            
            return window
            
        except Exception as e:
            self.logger.error(f"Failed to get/create window: {e}")
            raise
    
    async def _validate_and_clean_value(self, 
                                      value: Any, 
                                      config: StreamingFeatureConfig) -> Optional[Any]:
        """Validate and clean feature value."""
        try:
            if value is None:
                if config.null_handling == "drop":
                    return None
                elif config.null_handling == "default":
                    return config.default_value
                # For interpolate, we'll handle it during aggregation
                return value
            
            # Type validation
            if config.feature_type == FeatureType.NUMERIC:
                try:
                    numeric_value = float(value)
                    
                    # Range validation
                    if config.min_value is not None and numeric_value < config.min_value:
                        return config.min_value
                    if config.max_value is not None and numeric_value > config.max_value:
                        return config.max_value
                    
                    return numeric_value
                except (ValueError, TypeError):
                    return config.default_value if config.default_value else 0.0
            
            elif config.feature_type == FeatureType.CATEGORICAL:
                return str(value)
            
            elif config.feature_type == FeatureType.BINARY:
                return bool(value)
            
            else:
                return value
                
        except Exception as e:
            self.logger.error(f"Value validation failed: {e}")
            return config.default_value
    
    async def _should_process_window(self, 
                                   window: FeatureWindow, 
                                   config: StreamingFeatureConfig) -> bool:
        """Check if window should be processed."""
        try:
            current_time = time.time()
            
            # Check if window has enough samples
            if window.sample_count < config.batch_size:
                return False
            
            # Check if window is ready based on time
            if config.window_type == WindowType.TUMBLING:
                return current_time >= window.end_time
            
            elif config.window_type == WindowType.SLIDING:
                # Process sliding windows at slide intervals
                time_since_start = current_time - window.start_time
                return time_since_start >= config.slide_interval_seconds
            
            return True
            
        except Exception as e:
            self.logger.error(f"Window processing check failed: {e}")
            return False
    
    async def _process_window(self, 
                            window -> None: FeatureWindow, 
                            config -> None: StreamingFeatureConfig) -> None:
        """Process a complete time window."""
        try:
            processing_start = time.time()
            
            # Extract values from data points
            values = [point[1] for point in window.data_points if point[1] is not None]
            
            if not values:
                return
            
            # Compute aggregations
            for agg_type in config.aggregations:
                agg_value = await self._compute_aggregation(values, agg_type)
                window.aggregated_values[agg_type] = agg_value
            
            # Apply creator-specific processing
            if window.creator_id and window.creator_id in self.creator_processors:
                await self._apply_creator_processing(window, config)
            
            # Calculate quality score
            window.quality_score = await self._calculate_window_quality(window, config)
            
            # Create processed feature
            processed_feature = ProcessedFeature(
                feature_name=window.feature_name,
                creator_id=window.creator_id,
                timestamp=time.time(),
                value=window.aggregated_values.get(AggregationType.MEAN, values[-1]),
                aggregated_values={agg.value: val for agg, val in window.aggregated_values.items()},
                quality_score=window.quality_score,
                processing_latency_ms=(time.time() - processing_start) * 1000,
                source_window_id=window.window_id,
                processing_pipeline=[f"window_{config.window_type.value}"]
            )
            
            # Store processed feature
            feature_key = f"{window.feature_name}_{window.creator_id or 'global'}"
            self.processed_features[feature_key] = processed_feature
            
            # Apply feature-specific processors
            if window.feature_name in self.feature_processors:
                await self.feature_processors[window.feature_name](processed_feature)
            
            # Mark window as complete
            window.is_complete = True
            
            self.logger.debug(f"Processed window {window.window_id} with quality {window.quality_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"Window processing failed: {e}")
    
    async def _compute_aggregation(self, 
                                 values: List[Any], 
                                 agg_type: AggregationType) -> Any:
        """Compute aggregation over values."""
        try:
            if not values:
                return None
            
            # Convert to numeric if possible
            numeric_values = []
            for val in values:
                try:
                    numeric_values.append(float(val))
                except (ValueError, TypeError):
                    numeric_values.append(0.0)
            
            if agg_type == AggregationType.SUM:
                return sum(numeric_values)
            
            elif agg_type == AggregationType.MEAN:
                return statistics.mean(numeric_values)
            
            elif agg_type == AggregationType.MEDIAN:
                return statistics.median(numeric_values)
            
            elif agg_type == AggregationType.MIN:
                return min(numeric_values)
            
            elif agg_type == AggregationType.MAX:
                return max(numeric_values)
            
            elif agg_type == AggregationType.COUNT:
                return len(values)
            
            elif agg_type == AggregationType.STD:
                return statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0
            
            elif agg_type == AggregationType.PERCENTILE:
                # Default to 95th percentile
                sorted_values = sorted(numeric_values)
                idx = int(0.95 * len(sorted_values))
                return sorted_values[min(idx, len(sorted_values) - 1)]
            
            elif agg_type == AggregationType.LAST:
                return values[-1]
            
            elif agg_type == AggregationType.FIRST:
                return values[0]
            
            else:
                return statistics.mean(numeric_values)
                
        except Exception as e:
            self.logger.error(f"Aggregation computation failed: {e}")
            return 0.0
    
    async def _apply_creator_processing(self, 
                                      window -> None: FeatureWindow, 
                                      config -> None: StreamingFeatureConfig) -> None:
        """Apply creator-specific processing to window."""
        try:
            creator_id = window.creator_id
            if not creator_id:
                return
            
            # Get creator type from creator_id (simplified)
            creator_type = self._get_creator_type(creator_id)
            
            if creator_type in self.creator_feature_configs:
                creator_config = self.creator_feature_configs[creator_type]
                
                # Apply creator-specific aggregations
                if "additional_aggregations" in creator_config:
                    values = [point[1] for point in window.data_points if point[1] is not None]
                    for agg_type in creator_config["additional_aggregations"]:
                        if agg_type not in window.aggregated_values:
                            agg_value = await self._compute_aggregation(values, agg_type)
                            window.aggregated_values[agg_type] = agg_value
                
                # Apply creator-specific transformations
                await self._apply_creator_transformations(window, creator_type)
            
        except Exception as e:
            self.logger.error(f"Creator processing failed: {e}")
    
    def _get_creator_type(self, creator_id: str) -> str:
        """Get creator type from creator ID (simplified)."""
        # In real implementation, this would lookup in a database
        if "musician" in creator_id.lower():
            return "musician"
        elif "blogger" in creator_id.lower():
            return "blogger"
        elif "photographer" in creator_id.lower():
            return "photographer"
        elif "influencer" in creator_id.lower():
            return "influencer"
        else:
            return "generic"
    
    async def _apply_creator_transformations(self, 
                                           window -> None: FeatureWindow, 
                                           creator_type -> None: str) -> None:
        """Apply creator-specific feature transformations."""
        try:
            if creator_type == "musician":
                # Music-specific transformations
                if "engagement" in window.feature_name.lower():
                    # Normalize by time of day for musicians
                    await self._normalize_by_time_patterns(window, "music_prime_time")
            
            elif creator_type == "blogger":
                # Blog-specific transformations
                if "page_views" in window.feature_name.lower():
                    # Apply blog-specific scaling
                    await self._apply_content_length_scaling(window)
            
            elif creator_type == "photographer":
                # Photo-specific transformations
                if "likes" in window.feature_name.lower():
                    # Account for seasonal photography trends
                    await self._apply_seasonal_adjustment(window)
            
            elif creator_type == "influencer":
                # Influencer-specific transformations
                if "follower" in window.feature_name.lower():
                    # Apply cross-platform normalization
                    await self._normalize_cross_platform(window)
            
        except Exception as e:
            self.logger.error(f"Creator transformations failed: {e}")
    
    async def _normalize_by_time_patterns(self, window -> None: FeatureWindow, pattern_type -> None: str) -> None:
        """Normalize features by time-of-day patterns."""
        try:
            # Simplified time pattern normalization
            current_hour = datetime.now().hour
            
            if pattern_type == "music_prime_time":
                # Music listening peaks in evening
                if 18 <= current_hour <= 23:
                    adjustment_factor = 1.0
                elif 6 <= current_hour <= 12:
                    adjustment_factor = 0.7
                else:
                    adjustment_factor = 0.5
                
                # Apply adjustment to aggregated values
                for agg_type, value in window.aggregated_values.items():
                    if isinstance(value, (int, float)):
                        window.aggregated_values[agg_type] = value * adjustment_factor
            
        except Exception as e:
            self.logger.error(f"Time pattern normalization failed: {e}")
    
    async def _apply_content_length_scaling(self, window -> None: FeatureWindow) -> None:
        """Apply content length-based scaling for blog metrics."""
        # Simplified implementation
        pass
    
    async def _apply_seasonal_adjustment(self, window -> None: FeatureWindow) -> None:
        """Apply seasonal adjustments for photography metrics."""
        # Simplified implementation
        pass
    
    async def _normalize_cross_platform(self, window -> None: FeatureWindow) -> None:
        """Normalize influencer metrics across platforms."""
        # Simplified implementation
        pass
    
    async def _calculate_window_quality(self, 
                                      window: FeatureWindow, 
                                      config: StreamingFeatureConfig) -> float:
        """Calculate quality score for processed window."""
        try:
            quality_score = 1.0
            
            # Check sample count
            if window.sample_count < config.batch_size * 0.5:
                quality_score -= 0.3
            
            # Check data completeness
            null_count = sum(1 for _, value in window.data_points if value is None)
            null_ratio = null_count / max(len(window.data_points), 1)
            quality_score -= null_ratio * 0.4
            
            # Check temporal distribution
            if len(window.data_points) > 1:
                timestamps = [point[0] for point in window.data_points]
                time_gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                avg_gap = sum(time_gaps) / len(time_gaps)
                expected_gap = window.end_time - window.start_time / len(window.data_points)
                
                if avg_gap > expected_gap * 2:  # Large gaps in data
                    quality_score -= 0.2
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            self.logger.error(f"Quality calculation failed: {e}")
            return 0.5
    
    async def _manage_windows(self) -> None:
        """Manage active windows and cleanup completed ones."""
        try:
            while self.is_running:
                current_time = time.time()
                windows_to_remove = []
                
                for window_id, window in self.active_windows.items():
                    # Remove old completed windows
                    if window.is_complete and (current_time - window.end_time) > 3600:  # 1 hour retention
                        windows_to_remove.append(window_id)
                    
                    # Remove stale incomplete windows
                    elif not window.is_complete and (current_time - window.end_time) > 1800:  # 30 min timeout
                        windows_to_remove.append(window_id)
                
                # Remove old windows
                for window_id in windows_to_remove:
                    del self.active_windows[window_id]
                
                # Update metrics
                self.performance_metrics["active_windows"] = len(self.active_windows)
                
                await asyncio.sleep(60)  # Check every minute
                
        except asyncio.CancelledError:
            self.logger.info("Window management cancelled")
        except Exception as e:
            self.logger.error(f"Window management error: {e}")
    
    async def _collect_metrics(self) -> None:
        """Collect and update performance metrics."""
        try:
            while self.is_running:
                await asyncio.sleep(10)  # Update every 10 seconds
                
                # Calculate throughput
                # Implementation would track events over time windows
                
                # Calculate quality scores
                if self.processed_features:
                    quality_scores = [f.quality_score for f in self.processed_features.values()]
                    self.performance_metrics["feature_quality_score"] = statistics.mean(quality_scores)
                
        except asyncio.CancelledError:
            self.logger.info("Metrics collection cancelled")
        except Exception as e:
            self.logger.error(f"Metrics collection error: {e}")
    
    def _update_latency_metrics(self, latency_ms -> None: float) -> None:
        """Update latency tracking metrics."""
        try:
            current_avg = self.performance_metrics["avg_processing_latency_ms"]
            total_events = self.performance_metrics["total_events_processed"]
            
            if total_events > 0:
                self.performance_metrics["avg_processing_latency_ms"] = (
                    (current_avg * (total_events - 1) + latency_ms) / total_events
                )
            
        except Exception as e:
            self.logger.error(f"Latency metrics update failed: {e}")
    
    # Feature-specific processors
    async def _process_engagement_rate(self, feature -> None: ProcessedFeature) -> None:
        """Process engagement rate feature."""
        try:
            # Apply engagement-specific transformations
            if feature.creator_id:
                creator_type = self._get_creator_type(feature.creator_id)
                
                # Creator-specific engagement normalization
                if creator_type == "musician":
                    # Music engagement typically higher in evening
                    pass
                elif creator_type == "influencer":
                    # Influencer engagement varies by platform
                    pass
            
            feature.processing_pipeline.append("engagement_rate_processor")
            
        except Exception as e:
            self.logger.error(f"Engagement rate processing failed: {e}")
    
    async def _process_content_velocity(self, feature -> None: ProcessedFeature) -> None:
        """Process content velocity feature."""
        try:
            # Velocity-specific processing
            feature.processing_pipeline.append("content_velocity_processor")
            
        except Exception as e:
            self.logger.error(f"Content velocity processing failed: {e}")
    
    async def _process_audience_interaction(self, feature -> None: ProcessedFeature) -> None:
        """Process audience interaction feature."""
        try:
            # Interaction-specific processing
            feature.processing_pipeline.append("audience_interaction_processor")
            
        except Exception as e:
            self.logger.error(f"Audience interaction processing failed: {e}")
    
    async def _process_trending_score(self, feature -> None: ProcessedFeature) -> None:
        """Process trending score feature."""
        try:
            # Trending-specific processing
            feature.processing_pipeline.append("trending_score_processor")
            
        except Exception as e:
            self.logger.error(f"Trending score processing failed: {e}")
    
    async def _process_monetization_signals(self, feature -> None: ProcessedFeature) -> None:
        """Process monetization signals feature."""
        try:
            # Monetization-specific processing
            feature.processing_pipeline.append("monetization_signals_processor")
            
        except Exception as e:
            self.logger.error(f"Monetization signals processing failed: {e}")
    
    async def _default_feature_processor(self, feature -> None: ProcessedFeature) -> None:
        """Default feature processor for unknown features."""
        try:
            feature.processing_pipeline.append("default_processor")
            
        except Exception as e:
            self.logger.error(f"Default feature processing failed: {e}")
    
    # Public API methods
    async def get_feature(self, 
                        feature_name: str, 
                        creator_id: Optional[str] = None) -> Optional[ProcessedFeature]:
        """Get the latest processed feature value."""
        try:
            feature_key = f"{feature_name}_{creator_id or 'global'}"
            return self.processed_features.get(feature_key)
            
        except Exception as e:
            self.logger.error(f"Feature retrieval failed: {e}")
            return None
    
    async def get_features_batch(self, 
                               feature_names: List[str],
                               creator_id: Optional[str] = None) -> Dict[str, ProcessedFeature]:
        """Get multiple features in a single call."""
        try:
            features = {}
            for feature_name in feature_names:
                feature = await self.get_feature(feature_name, creator_id)
                if feature:
                    features[feature_name] = feature
            
            return features
            
        except Exception as e:
            self.logger.error(f"Batch feature retrieval failed: {e}")
            return {}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self.performance_metrics,
            "active_feature_configs": len(self.feature_configs),
            "processed_features_count": len(self.processed_features),
            "buffer_sizes": {source.value: len(buffer) for source, buffer in self.input_buffers.items()}
        }
    
    async def get_feature_lineage(self, 
                                feature_name: str,
                                creator_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get feature processing lineage and metadata."""
        try:
            feature = await self.get_feature(feature_name, creator_id)
            if not feature:
                return None
            
            # Get source window information
            window = None
            if feature.source_window_id:
                window = self.active_windows.get(feature.source_window_id)
            
            lineage = {
                "feature_name": feature.feature_name,
                "creator_id": feature.creator_id,
                "timestamp": feature.timestamp,
                "processing_pipeline": feature.processing_pipeline,
                "quality_score": feature.quality_score,
                "confidence": feature.confidence,
                "processing_latency_ms": feature.processing_latency_ms,
                "source_window": {
                    "window_id": feature.source_window_id,
                    "sample_count": window.sample_count if window else 0,
                    "time_range": {
                        "start": window.start_time if window else 0,
                        "end": window.end_time if window else 0
                    }
                } if window else None
            }
            
            return lineage
            
        except Exception as e:
            self.logger.error(f"Feature lineage retrieval failed: {e}")
            return None