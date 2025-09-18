"""Metrics Collection Engine - Advanced Multi-Source Data Aggregation
Enterprise-grade metrics collection system with real-time streaming,
data validation, API rate limiting, and performance optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use PROHIBITED without written authorization
- Reverse engineering STRICTLY FORBIDDEN
- Distribution PROHIBITED without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
import numpy as np
from collections import defaultdict, deque
import hashlib
import time
import redis
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import aiofiles

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data source types"""
    GOOGLE_ANALYTICS = "google_analytics"
    GOOGLE_SEARCH_CONSOLE = "google_search_console"
    GOOGLE_ADS = "google_ads"
    BING_WEBMASTER = "bing_webmaster"
    FACEBOOK_INSIGHTS = "facebook_insights"
    TWITTER_ANALYTICS = "twitter_analytics"
    YOUTUBE_ANALYTICS = "youtube_analytics"
    TIKTOK_ANALYTICS = "tiktok_analytics"
    INSTAGRAM_INSIGHTS = "instagram_insights"
    LINKEDIN_ANALYTICS = "linkedin_analytics"
    SEMRUSH = "semrush"
    AHREFS = "ahrefs"
    MOZZILLA = "mozzilla"
    SCREAMING_FROG = "screaming_frog"
    CUSTOM_API = "custom_api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE_UPLOAD = "file_upload"


class MetricType(Enum):
    """Metric data types"""
    COUNTER = "counter"          # Incrementing value
    GAUGE = "gauge"             # Point-in-time value
    HISTOGRAM = "histogram"     # Distribution of values
    RATE = "rate"              # Change over time
    PERCENTAGE = "percentage"   # Percentage value
    CURRENCY = "currency"      # Monetary value
    DURATION = "duration"      # Time duration
    BOOLEAN = "boolean"        # True/false value


class DataQuality(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"    # 95-100% quality
    GOOD = "good"             # 85-94% quality
    FAIR = "fair"             # 70-84% quality
    POOR = "poor"             # 50-69% quality
    UNRELIABLE = "unreliable" # <50% quality


class ProcessingStatus(Enum):
    """Data processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class DataSourceConfig:
    """Configuration for data source"""
    source_id: str
    source_type: DataSource
    name: str
    description: str
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    authentication: Dict[str, Any] = field(default_factory=dict)
    rate_limit: Optional[int] = None  # requests per hour
    timeout: int = 30  # seconds
    retry_attempts: int = 3
    retry_delay: int = 60  # seconds
    is_active: bool = True
    collection_frequency: int = 3600  # seconds
    metrics_config: Dict[str, Any] = field(default_factory=dict)
    transformation_rules: List[Dict[str, Any]] = field(default_factory=list)
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_collection: Optional[datetime] = None


@dataclass
class MetricDefinition:
    """Definition of a metric"""
    metric_id: str
    name: str
    description: str
    metric_type: MetricType
    unit: str
    data_sources: List[str]  # Source IDs
    aggregation_method: str = "sum"  # sum, avg, max, min, count
    retention_period: int = 365  # days
    quality_thresholds: Dict[str, float] = field(default_factory=dict)
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    transformation_pipeline: List[str] = field(default_factory=list)
    is_real_time: bool = True
    collection_interval: int = 60  # seconds
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricDataPoint:
    """Individual metric data point"""
    data_point_id: str
    metric_id: str
    source_id: str
    timestamp: datetime
    value: Union[float, int, str, bool]
    raw_value: Optional[Any] = None
    quality_score: float = 1.0
    quality_level: DataQuality = DataQuality.EXCELLENT
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    validation_errors: List[str] = field(default_factory=list)
    transformation_log: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None


@dataclass
class CollectionBatch:
    """Batch of metric collections"""
    batch_id: str
    source_id: str
    batch_size: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    data_points: List[MetricDataPoint] = field(default_factory=list)
    success_count: int = 0
    error_count: int = 0
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class RateLimitState:
    """Rate limiting state for data source"""
    source_id: str
    requests_made: int = 0
    window_start: datetime = field(default_factory=datetime.now)
    last_request: Optional[datetime] = None
    is_throttled: bool = False
    throttle_until: Optional[datetime] = None


class MetricsCollectionEngine:
    """Enterprise Metrics Collection Engine
    
    Advanced multi-source data aggregation system with real-time streaming,
    intelligent rate limiting, data quality monitoring, and performance optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Core storage
        self.data_sources: Dict[str, DataSourceConfig] = {}
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.rate_limit_states: Dict[str, RateLimitState] = {}
        self.collection_batches: Dict[str, CollectionBatch] = {}
        
        # Processing infrastructure
        self.collection_tasks: Dict[str, asyncio.Task] = {}
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.validation_queue: asyncio.Queue = asyncio.Queue()
        self.storage_queue: asyncio.Queue = asyncio.Queue()
        
        # Data quality monitoring
        self.quality_monitors: Dict[str, Any] = {}
        self.data_freshness_tracker: Dict[str, datetime] = {}
        self.schema_registry: Dict[str, Dict[str, Any]] = {}
        
        # Performance optimization
        self.connection_pool: Dict[str, aiohttp.ClientSession] = {}
        self.cache_layer: Optional[redis.Redis] = None
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        # Database connections
        self.db_engine = None
        self.async_session = None
        
        # Statistics and monitoring
        self.collection_stats = {
            'total_data_points_collected': 0,
            'total_collection_requests': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'rate_limit_hits': 0,
            'validation_errors': 0,
            'data_quality_issues': 0,
            'processing_time_total': 0.0,
            'avg_processing_time': 0.0,
            'throughput_per_second': 0.0
        }
        
        logger.info("Metrics Collection Engine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the collection engine"""
        try:
            # Initialize database connection
            await self._initialize_database()
            
            # Initialize cache layer
            await self._initialize_cache()
            
            # Start processing workers
            await self._start_processing_workers()
            
            # Load existing configurations
            await self._load_configurations()
            
            logger.info("Metrics Collection Engine initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics collection engine: {e}")
            return False
    
    async def register_data_source(
        self,
        source_config: DataSourceConfig
    ) -> str:
        """Register new data source for collection"""
        try:
            # Validate source configuration
            await self._validate_source_config(source_config)
            
            # Test source connectivity
            connectivity_test = await self._test_source_connectivity(source_config)
            if not connectivity_test:
                logger.warning(f"Data source connectivity test failed: {source_config.source_id}")
            
            # Store source configuration
            self.data_sources[source_config.source_id] = source_config
            
            # Initialize rate limiting
            self.rate_limit_states[source_config.source_id] = RateLimitState(
                source_id=source_config.source_id
            )
            
            # Create connection session if needed
            if source_config.api_endpoint:
                await self._create_connection_session(source_config)
            
            # Start collection task if active
            if source_config.is_active:
                await self._start_source_collection(source_config.source_id)
            
            logger.info(f"Data source registered: {source_config.source_id}")
            return source_config.source_id
            
        except Exception as e:
            logger.error(f"Failed to register data source: {e}")
            raise
    
    async def define_metric(
        self,
        metric_definition: MetricDefinition
    ) -> str:
        """Define new metric for collection"""
        try:
            # Validate metric definition
            await self._validate_metric_definition(metric_definition)
            
            # Verify data sources exist
            for source_id in metric_definition.data_sources:
                if source_id not in self.data_sources:
                    raise ValueError(f"Data source not found: {source_id}")
            
            # Store metric definition
            self.metric_definitions[metric_definition.metric_id] = metric_definition
            
            # Initialize quality monitoring
            await self._initialize_quality_monitoring(metric_definition)
            
            # Create schema registry entry
            await self._register_metric_schema(metric_definition)
            
            logger.info(f"Metric defined: {metric_definition.metric_id}")
            return metric_definition.metric_id
            
        except Exception as e:
            logger.error(f"Failed to define metric: {e}")
            raise
    
    async def collect_metrics(
        self,
        source_ids: Optional[List[str]] = None,
        metric_ids: Optional[List[str]] = None,
        force_collection: bool = False
    ) -> Dict[str, CollectionBatch]:
        """Collect metrics from specified sources"""
        try:
            collection_results = {}
            
            # Determine sources to collect from
            target_sources = source_ids or list(self.data_sources.keys())
            
            # Determine metrics to collect
            target_metrics = metric_ids or list(self.metric_definitions.keys())
            
            for source_id in target_sources:
                if source_id not in self.data_sources:
                    continue
                
                source_config = self.data_sources[source_id]
                
                # Check if collection is due or forced
                if not force_collection and not await self._is_collection_due(source_config):
                    continue
                
                # Check rate limiting
                if await self._is_rate_limited(source_id):
                    logger.warning(f"Rate limited: {source_id}")
                    self.collection_stats['rate_limit_hits'] += 1
                    continue
                
                # Perform collection
                batch = await self._collect_from_source(source_id, target_metrics)
                if batch:
                    collection_results[source_id] = batch
                    
                    # Update rate limiting
                    await self._update_rate_limit_state(source_id)
                    
                    # Update last collection time
                    source_config.last_collection = datetime.now()
            
            return collection_results
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {}
    
    async def stream_real_time_metrics(
        self,
        metric_ids: List[str],
        callback: Callable[[MetricDataPoint], None]
    ) -> str:
        """Start real-time metric streaming"""
        try:
            stream_id = str(uuid.uuid4())
            
            async def streaming_loop():
                while True:
                    try:
                        # Collect real-time metrics
                        for metric_id in metric_ids:
                            if metric_id not in self.metric_definitions:
                                continue
                            
                            metric_def = self.metric_definitions[metric_id]
                            
                            if not metric_def.is_real_time:
                                continue
                            
                            # Collect from all sources for this metric
                            for source_id in metric_def.data_sources:
                                data_point = await self._collect_real_time_data_point(
                                    source_id, metric_id
                                )
                                
                                if data_point:
                                    # Process and validate
                                    processed_data_point = await self._process_data_point(data_point)
                                    
                                    # Call callback
                                    callback(processed_data_point)
                        
                        # Wait for next collection interval
                        await asyncio.sleep(min(
                            metric_def.collection_interval 
                            for metric_def in [self.metric_definitions[mid] for mid in metric_ids]
                            if metric_def.is_real_time
                        ) or 60)
                        
                    except Exception as e:
                        logger.error(f"Streaming error: {e}")
                        await asyncio.sleep(30)
            
            # Start streaming task
            task = asyncio.create_task(streaming_loop())
            self.collection_tasks[stream_id] = task
            
            return stream_id
            
        except Exception as e:
            logger.error(f"Failed to start real-time streaming: {e}")
            raise
    
    async def validate_data_quality(
        self,
        data_points: List[MetricDataPoint],
        metric_id: str
    ) -> Dict[str, Any]:
        """Validate data quality for collected metrics"""
        try:
            if metric_id not in self.metric_definitions:
                raise ValueError(f"Metric definition not found: {metric_id}")
            
            metric_def = self.metric_definitions[metric_id]
            
            validation_results = {
                'metric_id': metric_id,
                'total_data_points': len(data_points),
                'validation_timestamp': datetime.now().isoformat(),
                'quality_scores': [],
                'validation_errors': [],
                'quality_summary': {},
                'recommendations': []
            }
            
            for data_point in data_points:
                # Validate individual data point
                point_validation = await self._validate_data_point(data_point, metric_def)
                
                validation_results['quality_scores'].append(point_validation['quality_score'])
                validation_results['validation_errors'].extend(point_validation['errors'])
                
                # Update data point with validation results
                data_point.quality_score = point_validation['quality_score']
                data_point.quality_level = point_validation['quality_level']
                data_point.validation_errors = point_validation['errors']
            
            # Calculate overall quality metrics
            if validation_results['quality_scores']:
                avg_quality = statistics.mean(validation_results['quality_scores'])
                min_quality = min(validation_results['quality_scores'])
                max_quality = max(validation_results['quality_scores'])
                
                validation_results['quality_summary'] = {
                    'average_quality': avg_quality,
                    'minimum_quality': min_quality,
                    'maximum_quality': max_quality,
                    'quality_distribution': self._calculate_quality_distribution(
                        validation_results['quality_scores']
                    ),
                    'overall_quality_level': self._determine_overall_quality_level(avg_quality)
                }
            
            # Generate recommendations
            validation_results['recommendations'] = await self._generate_quality_recommendations(
                validation_results
            )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate data quality: {e}")
            return {}
    
    async def get_collection_statistics(
        self,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive collection statistics"""
        try:
            stats = {
                'statistics_generated_at': datetime.now().isoformat(),
                'time_range': {
                    'start': time_range[0].isoformat() if time_range else None,
                    'end': time_range[1].isoformat() if time_range else None
                },
                'collection_overview': self.collection_stats.copy(),
                'source_statistics': {},
                'metric_statistics': {},
                'performance_metrics': {},
                'quality_metrics': {},
                'system_health': {}
            }
            
            # Source-level statistics
            for source_id, source_config in self.data_sources.items():
                source_stats = await self._calculate_source_statistics(source_id, time_range)
                stats['source_statistics'][source_id] = source_stats
            
            # Metric-level statistics
            for metric_id, metric_def in self.metric_definitions.items():
                metric_stats = await self._calculate_metric_statistics(metric_id, time_range)
                stats['metric_statistics'][metric_id] = metric_stats
            
            # Performance metrics
            stats['performance_metrics'] = {
                'avg_collection_time': self.collection_stats['avg_processing_time'],
                'throughput': self.collection_stats['throughput_per_second'],
                'success_rate': (
                    self.collection_stats['successful_collections'] / 
                    max(self.collection_stats['total_collection_requests'], 1)
                ) * 100,
                'error_rate': (
                    self.collection_stats['failed_collections'] / 
                    max(self.collection_stats['total_collection_requests'], 1)
                ) * 100
            }
            
            # Quality metrics
            stats['quality_metrics'] = await self._calculate_overall_quality_metrics()
            
            # System health
            stats['system_health'] = {
                'active_sources': len([s for s in self.data_sources.values() if s.is_active]),
                'total_sources': len(self.data_sources),
                'active_collection_tasks': len(self.collection_tasks),
                'queue_sizes': {
                    'processing_queue': self.processing_queue.qsize(),
                    'validation_queue': self.validation_queue.qsize(),
                    'storage_queue': self.storage_queue.qsize()
                },
                'memory_usage': await self._get_memory_usage(),
                'disk_usage': await self._get_disk_usage()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection statistics: {e}")
            return {}
    
    async def optimize_collection_performance(self) -> Dict[str, Any]:
        """Optimize collection performance based on current metrics"""
        try:
            optimization_results = {
                'optimization_timestamp': datetime.now().isoformat(),
                'current_performance': {},
                'optimizations_applied': [],
                'performance_improvements': {},
                'recommendations': []
            }
            
            # Analyze current performance
            current_stats = await self.get_collection_statistics()
            optimization_results['current_performance'] = current_stats['performance_metrics']
            
            # Optimize connection pooling
            connection_optimization = await self._optimize_connection_pooling()
            if connection_optimization['applied']:
                optimization_results['optimizations_applied'].append('connection_pooling')
                optimization_results['performance_improvements']['connection_pooling'] = connection_optimization
            
            # Optimize batch sizes
            batch_optimization = await self._optimize_batch_sizes()
            if batch_optimization['applied']:
                optimization_results['optimizations_applied'].append('batch_sizing')
                optimization_results['performance_improvements']['batch_sizing'] = batch_optimization
            
            # Optimize collection frequencies
            frequency_optimization = await self._optimize_collection_frequencies()
            if frequency_optimization['applied']:
                optimization_results['optimizations_applied'].append('collection_frequency')
                optimization_results['performance_improvements']['collection_frequency'] = frequency_optimization
            
            # Optimize cache utilization
            cache_optimization = await self._optimize_cache_utilization()
            if cache_optimization['applied']:
                optimization_results['optimizations_applied'].append('cache_utilization')
                optimization_results['performance_improvements']['cache_utilization'] = cache_optimization
            
            # Generate additional recommendations
            optimization_results['recommendations'] = await self._generate_performance_recommendations(
                current_stats
            )
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to optimize collection performance: {e}")
            return {}
    
    # Internal helper methods
    
    async def _initialize_database(self) -> None:
        """Initialize database connection and tables"""
        try:
            # This would connect to actual database
            # For now, use in-memory storage
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _initialize_cache(self) -> None:
        """Initialize cache layer"""
        try:
            # This would connect to Redis or other cache
            # For now, use in-memory cache
            logger.info("Cache layer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            raise
    
    async def _start_processing_workers(self) -> None:
        """Start background processing workers"""
        try:
            # Start processing worker
            processing_task = asyncio.create_task(self._processing_worker())
            self.collection_tasks['processing_worker'] = processing_task
            
            # Start validation worker
            validation_task = asyncio.create_task(self._validation_worker())
            self.collection_tasks['validation_worker'] = validation_task
            
            # Start storage worker
            storage_task = asyncio.create_task(self._storage_worker())
            self.collection_tasks['storage_worker'] = storage_task
            
            logger.info("Processing workers started")
        except Exception as e:
            logger.error(f"Failed to start processing workers: {e}")
            raise
    
    async def _processing_worker(self) -> None:
        """Background worker for processing data points"""
        while True:
            try:
                # Get data point from queue
                data_point = await self.processing_queue.get()
                
                # Process data point
                processed_point = await self._process_data_point(data_point)
                
                # Add to validation queue
                await self.validation_queue.put(processed_point)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Processing worker error: {e}")
                await asyncio.sleep(1)
    
    async def _validation_worker(self) -> None:
        """Background worker for validating data points"""
        while True:
            try:
                # Get data point from queue
                data_point = await self.validation_queue.get()
                
                # Validate data point
                if data_point.metric_id in self.metric_definitions:
                    metric_def = self.metric_definitions[data_point.metric_id]
                    validation_result = await self._validate_data_point(data_point, metric_def)
                    
                    # Update data point with validation results
                    data_point.quality_score = validation_result['quality_score']
                    data_point.quality_level = validation_result['quality_level']
                    data_point.validation_errors = validation_result['errors']
                
                # Add to storage queue
                await self.storage_queue.put(data_point)
                
                # Mark task as done
                self.validation_queue.task_done()
                
            except Exception as e:
                logger.error(f"Validation worker error: {e}")
                await asyncio.sleep(1)
    
    async def _storage_worker(self) -> None:
        """Background worker for storing validated data points"""
        while True:
            try:
                # Get data point from queue
                data_point = await self.storage_queue.get()
                
                # Store data point
                await self._store_data_point(data_point)
                
                # Update statistics
                self.collection_stats['total_data_points_collected'] += 1
                
                # Mark task as done
                self.storage_queue.task_done()
                
            except Exception as e:
                logger.error(f"Storage worker error: {e}")
                await asyncio.sleep(1)
    
    async def _load_configurations(self) -> None:
        """Load existing configurations from storage"""
        # Implementation would load from database
        pass
    
    async def _validate_source_config(self, config: DataSourceConfig) -> bool:
        """Validate data source configuration"""
        if not config.source_id or not config.name:
            raise ValueError("Source ID and name are required")
        
        if config.source_type == DataSource.CUSTOM_API and not config.api_endpoint:
            raise ValueError("API endpoint required for custom API source")
        
        return True
    
    async def _test_source_connectivity(self, config: DataSourceConfig) -> bool:
        """Test connectivity to data source"""
        try:
            if config.api_endpoint:
                # Test API connectivity
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        config.api_endpoint,
                        timeout=aiohttp.ClientTimeout(total=config.timeout)
                    ) as response:
                        return response.status < 500
            return True
        except Exception as e:
            logger.error(f"Connectivity test failed for {config.source_id}: {e}")
            return False
    
    async def _create_connection_session(self, config: DataSourceConfig) -> None:
        """Create persistent connection session for data source"""
        try:
            headers = {}
            if config.api_key:
                headers['Authorization'] = f"Bearer {config.api_key}"
            
            session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            )
            
            self.connection_pool[config.source_id] = session
            
        except Exception as e:
            logger.error(f"Failed to create connection session: {e}")
    
    async def _start_source_collection(self, source_id: str) -> None:
        """Start collection task for data source"""
        async def collection_loop():
            while source_id in self.data_sources and self.data_sources[source_id].is_active:
                try:
                    source_config = self.data_sources[source_id]
                    
                    # Check if collection is due
                    if await self._is_collection_due(source_config):
                        # Collect metrics
                        relevant_metrics = [
                            metric_id for metric_id, metric_def in self.metric_definitions.items()
                            if source_id in metric_def.data_sources
                        ]
                        
                        if relevant_metrics:
                            await self._collect_from_source(source_id, relevant_metrics)
                    
                    # Wait for next collection cycle
                    await asyncio.sleep(source_config.collection_frequency)
                    
                except Exception as e:
                    logger.error(f"Collection loop error for {source_id}: {e}")
                    await asyncio.sleep(60)  # Wait before retry
        
        # Start collection task
        task = asyncio.create_task(collection_loop())
        self.collection_tasks[f"collection_{source_id}"] = task
    
    async def _is_collection_due(self, source_config: DataSourceConfig) -> bool:
        """Check if collection is due for data source"""
        if not source_config.last_collection:
            return True
        
        time_since_last = datetime.now() - source_config.last_collection
        return time_since_last.total_seconds() >= source_config.collection_frequency
    
    async def _is_rate_limited(self, source_id: str) -> bool:
        """Check if source is rate limited"""
        if source_id not in self.rate_limit_states:
            return False
        
        rate_state = self.rate_limit_states[source_id]
        source_config = self.data_sources[source_id]
        
        if not source_config.rate_limit:
            return False
        
        # Check if currently throttled
        if rate_state.is_throttled and rate_state.throttle_until:
            if datetime.now() < rate_state.throttle_until:
                return True
            else:
                # Throttle period ended
                rate_state.is_throttled = False
                rate_state.throttle_until = None
        
        # Check request count in current window
        now = datetime.now()
        window_duration = timedelta(hours=1)
        
        if now - rate_state.window_start > window_duration:
            # Reset window
            rate_state.window_start = now
            rate_state.requests_made = 0
        
        return rate_state.requests_made >= source_config.rate_limit
    
    async def _update_rate_limit_state(self, source_id: str) -> None:
        """Update rate limit state after request"""
        if source_id in self.rate_limit_states:
            rate_state = self.rate_limit_states[source_id]
            rate_state.requests_made += 1
            rate_state.last_request = datetime.now()
    
    async def _collect_from_source(
        self,
        source_id: str,
        metric_ids: List[str]
    ) -> Optional[CollectionBatch]:
        """Collect metrics from specific data source"""
        try:
            start_time = time.time()
            
            batch = CollectionBatch(
                batch_id=str(uuid.uuid4()),
                source_id=source_id,
                batch_size=len(metric_ids),
                started_at=datetime.now(),
                status=ProcessingStatus.PROCESSING
            )
            
            source_config = self.data_sources[source_id]
            
            # Collect data points for each metric
            for metric_id in metric_ids:
                try:
                    data_point = await self._collect_metric_data_point(source_id, metric_id)
                    if data_point:
                        batch.data_points.append(data_point)
                        batch.success_count += 1
                        
                        # Add to processing queue
                        await self.processing_queue.put(data_point)
                
                except Exception as e:
                    batch.error_count += 1
                    batch.errors.append(f"Failed to collect {metric_id}: {str(e)}")
                    logger.error(f"Failed to collect metric {metric_id} from {source_id}: {e}")
            
            # Complete batch
            batch.completed_at = datetime.now()
            batch.processing_time = time.time() - start_time
            batch.status = ProcessingStatus.COMPLETED if batch.error_count == 0 else ProcessingStatus.FAILED
            
            # Store batch
            self.collection_batches[batch.batch_id] = batch
            
            # Update statistics
            self.collection_stats['total_collection_requests'] += 1
            if batch.status == ProcessingStatus.COMPLETED:
                self.collection_stats['successful_collections'] += 1
            else:
                self.collection_stats['failed_collections'] += 1
            
            self.collection_stats['processing_time_total'] += batch.processing_time
            self.collection_stats['avg_processing_time'] = (
                self.collection_stats['processing_time_total'] / 
                self.collection_stats['total_collection_requests']
            )
            
            return batch
            
        except Exception as e:
            logger.error(f"Failed to collect from source {source_id}: {e}")
            return None
    
    async def _collect_metric_data_point(
        self,
        source_id: str,
        metric_id: str
    ) -> Optional[MetricDataPoint]:
        """Collect single metric data point from source"""
        try:
            source_config = self.data_sources[source_id]
            metric_def = self.metric_definitions[metric_id]
            
            # This would implement actual data collection based on source type
            # For now, return mock data point
            import random
            
            value = random.uniform(0, 1000)
            
            data_point = MetricDataPoint(
                data_point_id=str(uuid.uuid4()),
                metric_id=metric_id,
                source_id=source_id,
                timestamp=datetime.now(),
                value=value,
                raw_value=value,
                quality_score=random.uniform(0.8, 1.0),
                metadata={
                    'collection_method': source_config.source_type.value,
                    'api_endpoint': source_config.api_endpoint
                }
            )
            
            return data_point
            
        except Exception as e:
            logger.error(f"Failed to collect data point {metric_id} from {source_id}: {e}")
            return None
    
    async def _collect_real_time_data_point(
        self,
        source_id: str,
        metric_id: str
    ) -> Optional[MetricDataPoint]:
        """Collect real-time data point"""
        # Use same collection method but prioritize speed
        return await self._collect_metric_data_point(source_id, metric_id)
    
    async def _process_data_point(self, data_point: MetricDataPoint) -> MetricDataPoint:
        """Process and transform data point"""
        try:
            data_point.processing_status = ProcessingStatus.PROCESSING
            
            # Apply transformations
            if data_point.metric_id in self.metric_definitions:
                metric_def = self.metric_definitions[data_point.metric_id]
                
                for transformation in metric_def.transformation_pipeline:
                    data_point = await self._apply_transformation(data_point, transformation)
            
            data_point.processing_status = ProcessingStatus.COMPLETED
            data_point.processed_at = datetime.now()
            
            return data_point
            
        except Exception as e:
            data_point.processing_status = ProcessingStatus.FAILED
            data_point.validation_errors.append(f"Processing failed: {str(e)}")
            logger.error(f"Failed to process data point: {e}")
            return data_point
    
    async def _apply_transformation(
        self,
        data_point: MetricDataPoint,
        transformation: str
    ) -> MetricDataPoint:
        """Apply transformation to data point"""
        # Implementation would apply various transformations
        # For now, just log the transformation
        data_point.transformation_log.append(f"Applied transformation: {transformation}")
        return data_point
    
    async def _validate_data_point(
        self,
        data_point: MetricDataPoint,
        metric_def: MetricDefinition
    ) -> Dict[str, Any]:
        """Validate individual data point"""
        validation_result = {
            'quality_score': 1.0,
            'quality_level': DataQuality.EXCELLENT,
            'errors': []
        }
        
        # Validate value type
        if metric_def.metric_type == MetricType.COUNTER and not isinstance(data_point.value, (int, float)):
            validation_result['errors'].append("Counter metric must be numeric")
            validation_result['quality_score'] *= 0.8
        
        # Validate value range
        if isinstance(data_point.value, (int, float)):
            if metric_def.metric_type == MetricType.PERCENTAGE and (data_point.value < 0 or data_point.value > 100):
                validation_result['errors'].append("Percentage value out of range")
                validation_result['quality_score'] *= 0.7
        
        # Validate timestamp
        if data_point.timestamp > datetime.now() + timedelta(minutes=5):
            validation_result['errors'].append("Future timestamp detected")
            validation_result['quality_score'] *= 0.9
        
        # Determine quality level
        if validation_result['quality_score'] >= 0.95:
            validation_result['quality_level'] = DataQuality.EXCELLENT
        elif validation_result['quality_score'] >= 0.85:
            validation_result['quality_level'] = DataQuality.GOOD
        elif validation_result['quality_score'] >= 0.70:
            validation_result['quality_level'] = DataQuality.FAIR
        elif validation_result['quality_score'] >= 0.50:
            validation_result['quality_level'] = DataQuality.POOR
        else:
            validation_result['quality_level'] = DataQuality.UNRELIABLE
        
        return validation_result
    
    async def _store_data_point(self, data_point: MetricDataPoint) -> None:
        """Store validated data point"""
        try:
            # This would store to actual database
            # For now, just log storage
            logger.debug(f"Stored data point: {data_point.data_point_id}")
        except Exception as e:
            logger.error(f"Failed to store data point: {e}")
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics"""
        return {
            'collection_stats': self.collection_stats.copy(),
            'system_status': {
                'total_data_sources': len(self.data_sources),
                'active_data_sources': len([s for s in self.data_sources.values() if s.is_active]),
                'total_metrics_defined': len(self.metric_definitions),
                'active_collection_tasks': len(self.collection_tasks),
                'connection_pool_size': len(self.connection_pool),
                'batch_count': len(self.collection_batches)
            },
            'performance_metrics': {
                'avg_processing_time': self.collection_stats['avg_processing_time'],
                'throughput_per_second': self.collection_stats['throughput_per_second'],
                'success_rate': (
                    self.collection_stats['successful_collections'] / 
                    max(self.collection_stats['total_collection_requests'], 1)
                ) * 100
            }
        }


# Export the main class
__all__ = [
    "MetricsCollectionEngine",
    "DataSourceConfig",
    "MetricDefinition", 
    "MetricDataPoint",
    "CollectionBatch",
    "DataSource",
    "MetricType",
    "DataQuality",
    "ProcessingStatus"
]