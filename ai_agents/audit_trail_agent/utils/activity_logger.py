"""
Activity Logger - Real-Time Platform Activity Tracking & Recording

Industrial-grade activity logging system for comprehensive platform monitoring,
user behavior tracking, and system event recording with high-performance capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and intellectual property belong exclusively to Fahed Mlaiel.
Unauthorized use, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Any, Union, Set, Callable
from dataclasses import dataclass, field
import json
import hashlib
from collections import defaultdict, deque
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from sqlalchemy import and_, or_, desc, func, text
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, Gauge, Summary

from ...core.config import settings
from ...core.database import get_db_session
from ...core.exceptions import ActivityLogError, ValidationError
from ...models.activity_models import (
    ActivityLog, UserSession, SystemEvent, 
    ContentActivity, APIActivity, SecurityActivity
)
from ...security.activity_encryption import ActivityEncryption
from ...utils.batch_processor import BatchProcessor
from ...utils.activity_aggregator import ActivityAggregator

logger = logging.getLogger(__name__)

class ActivityType(Enum):
    """Comprehensive activity type classification"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTRATION = "user_registration"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_DOWNLOAD = "content_download"
    CONTENT_VIEW = "content_view"
    CONTENT_SHARE = "content_share"
    CONTENT_DELETE = "content_delete"
    CONTENT_EDIT = "content_edit"
    PROFILE_UPDATE = "profile_update"
    PAYMENT_TRANSACTION = "payment_transaction"
    API_REQUEST = "api_request"
    SEARCH_QUERY = "search_query"
    COLLABORATION_REQUEST = "collaboration_request"
    PROTECTION_CLAIM = "protection_claim"
    REVENUE_DISTRIBUTION = "revenue_distribution"
    ADMIN_ACTION = "admin_action"
    SYSTEM_ERROR = "system_error"
    SECURITY_EVENT = "security_event"

class ActivitySeverity(IntEnum):
    """Activity severity levels"""
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

class ActivitySource(Enum):
    """Activity source classification"""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API = "api"
    SYSTEM = "system"
    BACKGROUND_TASK = "background_task"
    WEBHOOK = "webhook"
    ADMIN_PANEL = "admin_panel"
    THIRD_PARTY = "third_party"

@dataclass
class ActivityConfiguration:
    """Advanced activity logging configuration"""
    enable_real_time_logging: bool = True
    enable_batch_processing: bool = True
    enable_aggregation: bool = True
    enable_encryption: bool = True
    batch_size: int = 1000
    batch_timeout_seconds: int = 30
    retention_days: int = 365
    compression_enabled: bool = True
    anonymization_rules: Dict[str, str] = field(default_factory=dict)
    sampling_rate: float = 1.0  # 1.0 = log all activities
    performance_tracking: bool = True

@dataclass
class ActivityMetrics:
    """Comprehensive activity metrics tracking"""
    total_activities_logged: int = 0
    activities_by_type: Dict[str, int] = field(default_factory=dict)
    activities_by_source: Dict[str, int] = field(default_factory=dict)
    average_processing_time_ms: float = 0.0
    batch_processing_efficiency: float = 0.0
    error_rate: float = 0.0
    storage_size_mb: float = 0.0

class ActivityLogger:
    """
    Enterprise Activity Logging System
    
    High-performance activity tracking system providing:
    - Real-time activity logging with microsecond precision
    - Batch processing for high-volume scenarios
    - Advanced filtering and sampling capabilities
    - Encrypted storage for sensitive activities
    - Real-time aggregation and analytics
    - Performance-optimized storage and retrieval
    - Compliance-ready activity trails
    """

    def __init__(self, config: Optional[ActivityConfiguration] = None):
        self.config = config or ActivityConfiguration()
        self.metrics = ActivityMetrics()
        
        # Core components
        self.activity_encryption = ActivityEncryption()
        self.batch_processor = BatchProcessor(
            batch_size=self.config.batch_size,
            timeout=self.config.batch_timeout_seconds
        )
        self.activity_aggregator = ActivityAggregator()
        
        # High-performance logging state
        self.activity_buffer: deque = deque(maxlen=10000)
        self.session_cache: Dict[str, Dict[str, Any]] = {}
        self.activity_counters: Dict[str, int] = defaultdict(int)
        
        # Performance metrics
        self.activity_counter = Counter('activities_logged_total', 'Total activities logged', ['activity_type', 'source'])
        self.processing_time = Histogram('activity_processing_duration_seconds', 'Activity processing time')
        self.batch_size_histogram = Histogram('activity_batch_size', 'Activity batch sizes')
        self.buffer_size_gauge = Gauge('activity_buffer_size', 'Current activity buffer size')
        self.storage_gauge = Gauge('activity_storage_mb', 'Activity storage size in MB')
        
        # Activity filters and samplers
        self.activity_filters: List[Callable] = []
        self.sampling_strategies: Dict[ActivityType, float] = {}
        
        # Background processing
        self.processing_tasks: Set[asyncio.Task] = set()
        
        logger.info("ActivityLogger initialized with enterprise performance capabilities")

    async def initialize(self) -> bool:
        """Initialize activity logging system with background services"""
        try:
            # Initialize database connections and indexes
            await self._initialize_activity_storage()
            
            # Start background processing services
            if self.config.enable_batch_processing:
                task = asyncio.create_task(self._start_batch_processor())
                self.processing_tasks.add(task)
            
            if self.config.enable_aggregation:
                task = asyncio.create_task(self._start_activity_aggregator())
                self.processing_tasks.add(task)
            
            # Start performance monitoring
            if self.config.performance_tracking:
                task = asyncio.create_task(self._start_performance_monitor())
                self.processing_tasks.add(task)
            
            # Load sampling strategies
            await self._load_sampling_strategies()
            
            logger.info("ActivityLogger fully initialized with background services")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ActivityLogger: {str(e)}")
            return False

    async def log_activity(
        self,
        activity_type: ActivityType,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source: ActivitySource = ActivitySource.SYSTEM,
        severity: ActivitySeverity = ActivitySeverity.INFO,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        resource_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Log high-performance activity with comprehensive tracking
        
        Args:
            activity_type: Type of activity being logged
            user_id: User identifier (if applicable)
            session_id: Session identifier
            source: Source of the activity
            severity: Activity severity level
            details: Activity-specific details
            metadata: Additional metadata
            resource_id: Resource identifier (if applicable)
            timestamp: Custom timestamp (defaults to current time)
            
        Returns:
            Unique activity ID
        """
        start_time = time.time()
        
        try:
            # Generate unique activity ID
            activity_id = str(uuid.uuid4())
            log_timestamp = timestamp or datetime.now(timezone.utc)
            
            # Apply sampling strategy
            if not await self._should_log_activity(activity_type, user_id):
                return activity_id  # Return ID but don't actually log
            
            # Prepare activity record
            activity_record = {
                "activity_id": activity_id,
                "activity_type": activity_type.value,
                "user_id": user_id,
                "session_id": session_id or self._generate_session_id(user_id),
                "source": source.value,
                "severity": severity.value,
                "timestamp": log_timestamp.isoformat(),
                "details": details or {},
                "metadata": metadata or {},
                "resource_id": resource_id,
                "client_info": await self._gather_client_info(),
                "performance_context": await self._gather_performance_context(),
                "correlation_id": self._generate_correlation_id()
            }
            
            # Apply activity filters
            if not await self._apply_activity_filters(activity_record):
                return activity_id  # Activity filtered out
            
            # Encrypt sensitive data if configured
            if self.config.enable_encryption:
                activity_record = await self._encrypt_sensitive_activity_data(activity_record)
            
            # High-performance logging path selection
            if self.config.enable_real_time_logging and severity >= ActivitySeverity.WARNING:
                # Real-time logging for critical activities
                await self._log_activity_real_time(activity_record)
            else:
                # Batch logging for performance
                await self._add_to_batch_queue(activity_record)
            
            # Update session tracking
            if session_id and user_id:
                await self._update_session_tracking(session_id, user_id, activity_type)
            
            # Update real-time metrics
            self.activity_counter.labels(
                activity_type=activity_type.value,
                source=source.value
            ).inc()
            
            # Update internal metrics
            self.metrics.total_activities_logged += 1
            self.activity_counters[activity_type.value] += 1
            self.metrics.activities_by_type[activity_type.value] = self.activity_counters[activity_type.value]
            self.metrics.activities_by_source[source.value] = self.metrics.activities_by_source.get(source.value, 0) + 1
            
            # Track processing time
            processing_time_ms = (time.time() - start_time) * 1000
            self.processing_time.observe(processing_time_ms / 1000)
            self.metrics.average_processing_time_ms = (
                (self.metrics.average_processing_time_ms * (self.metrics.total_activities_logged - 1) + processing_time_ms)
                / self.metrics.total_activities_logged
            )
            
            # Update buffer gauge
            self.buffer_size_gauge.set(len(self.activity_buffer))
            
            logger.debug(f"Activity logged: {activity_id} ({activity_type.value}) in {processing_time_ms:.2f}ms")
            return activity_id
            
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")
            self.metrics.error_rate += 1
            raise ActivityLogError(f"Activity logging failed: {str(e)}")

    async def query_activities(
        self,
        filters: Dict[str, Any],
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
        include_aggregated: bool = False
    ) -> Dict[str, Any]:
        """
        High-performance activity querying with advanced filtering
        
        Args:
            filters: Query filters (user_id, activity_type, source, etc.)
            time_range: Time range for query
            limit: Maximum results to return
            offset: Result offset for pagination
            sort_by: Field to sort by
            sort_order: Sort order (asc, desc)
            include_aggregated: Include aggregated activity data
            
        Returns:
            Query results with metadata
        """
        try:
            query_start_time = time.time()
            
            # Build optimized database query
            async with get_db_session() as session:
                query = session.query(ActivityLog)
                
                # Apply filters
                query = await self._apply_query_filters(query, filters)
                
                # Apply time range
                if time_range:
                    query = query.filter(
                        ActivityLog.timestamp >= time_range[0],
                        ActivityLog.timestamp <= time_range[1]
                    )
                
                # Apply sorting
                if sort_order.lower() == "desc":
                    query = query.order_by(desc(getattr(ActivityLog, sort_by)))
                else:
                    query = query.order_by(getattr(ActivityLog, sort_by))
                
                # Get total count for pagination
                total_count = query.count()
                
                # Apply pagination
                results = query.offset(offset).limit(limit).all()
                
                # Convert to dictionaries and decrypt if needed
                activity_records = []
                for result in results:
                    activity_dict = result.to_dict()
                    if self.config.enable_encryption:
                        activity_dict = await self._decrypt_activity_data(activity_dict)
                    activity_records.append(activity_dict)
                
                # Include aggregated data if requested
                aggregated_data = {}
                if include_aggregated:
                    aggregated_data = await self._get_aggregated_activity_data(filters, time_range)
                
                query_time = time.time() - query_start_time
                
                return {
                    "activities": activity_records,
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + len(activity_records) < total_count,
                    "aggregated_data": aggregated_data,
                    "query_metadata": {
                        "query_time_seconds": query_time,
                        "filters_applied": filters,
                        "time_range": {
                            "start": time_range[0].isoformat() if time_range and time_range[0] else None,
                            "end": time_range[1].isoformat() if time_range and time_range[1] else None
                        },
                        "sort": {"field": sort_by, "order": sort_order}
                    }
                }
                
        except Exception as e:
            logger.error(f"Activity query failed: {str(e)}")
            raise ActivityLogError(f"Query failed: {str(e)}")

    async def get_user_activity_summary(
        self,
        user_id: str,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Generate comprehensive user activity summary with analytics
        
        Args:
            user_id: User identifier
            time_period: Time period for summary
            
        Returns:
            Detailed user activity summary
        """
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - time_period
            
            # Query user activities
            user_activities = await self.query_activities(
                filters={"user_id": user_id},
                time_range=(start_time, end_time),
                limit=10000,  # Large limit for comprehensive analysis
                include_aggregated=True
            )
            
            activities = user_activities["activities"]
            
            # Analyze activity patterns
            activity_patterns = await self._analyze_user_activity_patterns(activities)
            
            # Calculate activity statistics
            activity_stats = {
                "total_activities": len(activities),
                "activities_by_type": defaultdict(int),
                "activities_by_source": defaultdict(int),
                "activities_by_hour": defaultdict(int),
                "activities_by_day": defaultdict(int),
                "most_active_day": None,
                "most_active_hour": None,
                "average_session_duration": 0.0
            }
            
            for activity in activities:
                activity_type = activity["activity_type"]
                activity_source = activity["source"]
                timestamp = datetime.fromisoformat(activity["timestamp"])
                
                activity_stats["activities_by_type"][activity_type] += 1
                activity_stats["activities_by_source"][activity_source] += 1
                activity_stats["activities_by_hour"][timestamp.hour] += 1
                activity_stats["activities_by_day"][timestamp.weekday()] += 1
            
            # Find peak activity times
            if activity_stats["activities_by_day"]:
                activity_stats["most_active_day"] = max(
                    activity_stats["activities_by_day"],
                    key=activity_stats["activities_by_day"].get
                )
            
            if activity_stats["activities_by_hour"]:
                activity_stats["most_active_hour"] = max(
                    activity_stats["activities_by_hour"],
                    key=activity_stats["activities_by_hour"].get
                )
            
            # Calculate session metrics
            session_metrics = await self._calculate_user_session_metrics(user_id, start_time, end_time)
            
            # Generate insights
            insights = await self._generate_user_activity_insights(activities, activity_stats, activity_patterns)
            
            summary = {
                "user_id": user_id,
                "summary_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration_days": time_period.days
                },
                "activity_statistics": dict(activity_stats),
                "activity_patterns": activity_patterns,
                "session_metrics": session_metrics,
                "insights": insights,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate user activity summary: {str(e)}")
            raise ActivityLogError(f"User activity summary failed: {str(e)}")

    async def get_activity_analytics(
        self,
        time_range: Tuple[datetime, datetime],
        granularity: str = "hour",
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive platform activity analytics
        
        Args:
            time_range: Time range for analytics
            granularity: Data granularity (minute, hour, day, week)
            metrics: Specific metrics to include
            
        Returns:
            Detailed activity analytics
        """
        try:
            start_time, end_time = time_range
            metrics = metrics or ["activity_count", "user_count", "session_count", "error_rate"]
            
            # Generate time series data
            time_series = await self._generate_activity_time_series(
                start_time, end_time, granularity
            )
            
            # Calculate comprehensive analytics
            analytics = {
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "granularity": granularity
                },
                "time_series": time_series,
                "summary_metrics": {},
                "trend_analysis": {},
                "anomaly_detection": {},
                "top_activities": {},
                "performance_metrics": {}
            }
            
            # Calculate summary metrics
            if "activity_count" in metrics:
                analytics["summary_metrics"]["total_activities"] = await self._count_activities_in_range(
                    start_time, end_time
                )
            
            if "user_count" in metrics:
                analytics["summary_metrics"]["unique_users"] = await self._count_unique_users_in_range(
                    start_time, end_time
                )
            
            if "session_count" in metrics:
                analytics["summary_metrics"]["total_sessions"] = await self._count_sessions_in_range(
                    start_time, end_time
                )
            
            if "error_rate" in metrics:
                analytics["summary_metrics"]["error_rate"] = await self._calculate_error_rate_in_range(
                    start_time, end_time
                )
            
            # Perform trend analysis
            analytics["trend_analysis"] = await self._analyze_activity_trends(time_series)
            
            # Detect anomalies
            analytics["anomaly_detection"] = await self._detect_activity_anomalies(time_series)
            
            # Get top activities
            analytics["top_activities"] = await self._get_top_activities_in_range(
                start_time, end_time
            )
            
            # Performance metrics
            analytics["performance_metrics"] = {
                "average_processing_time_ms": self.metrics.average_processing_time_ms,
                "current_buffer_size": len(self.activity_buffer),
                "batch_processing_efficiency": self.metrics.batch_processing_efficiency,
                "storage_size_mb": self.metrics.storage_size_mb
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to generate activity analytics: {str(e)}")
            raise ActivityLogError(f"Analytics generation failed: {str(e)}")

    # Private helper methods
    async def _should_log_activity(self, activity_type: ActivityType, user_id: Optional[str]) -> bool:
        """Determine if activity should be logged based on sampling strategy"""
        # Global sampling rate
        if np.random.random() > self.config.sampling_rate:
            return False
        
        # Activity-specific sampling
        type_sampling_rate = self.sampling_strategies.get(activity_type, 1.0)
        if np.random.random() > type_sampling_rate:
            return False
        
        return True

    async def _encrypt_sensitive_activity_data(self, activity_record: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in activity record"""
        sensitive_fields = ['user_id', 'details', 'client_info']
        encrypted_record = activity_record.copy()
        
        for field in sensitive_fields:
            if field in encrypted_record and encrypted_record[field]:
                encrypted_record[field] = await self.activity_encryption.encrypt_data(
                    json.dumps(encrypted_record[field])
                )
        
        return encrypted_record

    async def _log_activity_real_time(self, activity_record: Dict[str, Any]) -> None:
        """Log activity in real-time for critical events"""
        try:
            async with get_db_session() as session:
                activity_log = ActivityLog(
                    activity_id=activity_record['activity_id'],
                    activity_type=activity_record['activity_type'],
                    user_id=activity_record['user_id'],
                    session_id=activity_record['session_id'],
                    source=activity_record['source'],
                    severity=activity_record['severity'],
                    timestamp=datetime.fromisoformat(activity_record['timestamp']),
                    details=json.dumps(activity_record['details']),
                    metadata=json.dumps(activity_record['metadata']),
                    resource_id=activity_record['resource_id'],
                    correlation_id=activity_record['correlation_id']
                )
                session.add(activity_log)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Real-time activity logging failed: {str(e)}")
            # Fallback to batch queue
            await self._add_to_batch_queue(activity_record)

    async def _add_to_batch_queue(self, activity_record: Dict[str, Any]) -> None:
        """Add activity to batch processing queue"""
        self.activity_buffer.append(activity_record)
        
        # Force batch processing if buffer is full
        if len(self.activity_buffer) >= self.config.batch_size:
            asyncio.create_task(self._process_activity_batch())

    async def _start_batch_processor(self) -> None:
        """Start background batch processing service"""
        while True:
            try:
                if self.activity_buffer:
                    await self._process_activity_batch()
                await asyncio.sleep(self.config.batch_timeout_seconds)
            except Exception as e:
                logger.error(f"Batch processing error: {str(e)}")
                await asyncio.sleep(5)

    async def _process_activity_batch(self) -> None:
        """Process batched activities for high-performance storage"""
        if not self.activity_buffer:
            return
        
        batch_start_time = time.time()
        batch_activities = []
        
        # Extract batch from buffer
        batch_size = min(len(self.activity_buffer), self.config.batch_size)
        for _ in range(batch_size):
            if self.activity_buffer:
                batch_activities.append(self.activity_buffer.popleft())
        
        if not batch_activities:
            return
        
        try:
            # Bulk insert activities
            async with get_db_session() as session:
                activity_objects = []
                for record in batch_activities:
                    activity_log = ActivityLog(
                        activity_id=record['activity_id'],
                        activity_type=record['activity_type'],
                        user_id=record['user_id'],
                        session_id=record['session_id'],
                        source=record['source'],
                        severity=record['severity'],
                        timestamp=datetime.fromisoformat(record['timestamp']),
                        details=json.dumps(record['details']),
                        metadata=json.dumps(record['metadata']),
                        resource_id=record['resource_id'],
                        correlation_id=record['correlation_id']
                    )
                    activity_objects.append(activity_log)
                
                session.add_all(activity_objects)
                await session.commit()
            
            # Update batch processing metrics
            batch_time = time.time() - batch_start_time
            self.batch_size_histogram.observe(len(batch_activities))
            self.metrics.batch_processing_efficiency = len(batch_activities) / max(batch_time, 0.001)
            
            logger.debug(f"Processed activity batch: {len(batch_activities)} activities in {batch_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            # Re-add activities to buffer for retry
            self.activity_buffer.extendleft(reversed(batch_activities))

    def _generate_session_id(self, user_id: Optional[str]) -> str:
        """Generate session ID for activity correlation"""
        if user_id and user_id in self.session_cache:
            return self.session_cache[user_id]["session_id"]
        
        session_id = str(uuid.uuid4())
        if user_id:
            self.session_cache[user_id] = {
                "session_id": session_id,
                "created_at": datetime.now(timezone.utc),
                "last_activity": datetime.now(timezone.utc)
            }
        
        return session_id

    def _generate_correlation_id(self) -> str:
        """Generate correlation ID for request tracing"""
        return str(uuid.uuid4())

    async def _gather_client_info(self) -> Dict[str, Any]:
        """Gather client information from request context"""
        # This would typically extract from web framework context
        return {
            "ip_address": "127.0.0.1",  # Placeholder
            "user_agent": "Unknown",    # Placeholder
            "referrer": None,
            "location": None
        }

    async def _gather_performance_context(self) -> Dict[str, Any]:
        """Gather performance context for activity"""
        return {
            "memory_usage_mb": 0,  # Placeholder
            "cpu_usage_percent": 0,  # Placeholder
            "request_duration_ms": 0,  # Placeholder
            "database_queries": 0  # Placeholder
        }

    # Additional helper methods would be implemented here for completeness...
    # (Implementation continues with remaining helper methods...)
