"""Usage Tracker
============

Real-time usage tracking system for licensed content monitoring,
analytics, and compliance verification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID
import logging
from enum import Enum
import asyncio
import json

from .models import (
    LicenseAgreement, LicenseUsageTracking, UsageType
)
from .repository import LicensingRepository
from .compliance import ComplianceEngine
from ...core.exceptions import TrackingError, ValidationError
from ...core.config import get_settings
from ...utils.analytics import AnalyticsEngine
from ...utils.cache import CacheManager
from ...utils.queue import QueueManager

logger = logging.getLogger(__name__)
settings = get_settings()


class TrackingEvent(Enum):
    """
Usage tracking event types"""

    PLAY = "play"
    STREAM = "stream"
    DOWNLOAD = "download"
    VIEW = "view"
    IMPRESSION = "impression"
    CLICK = "click"
    SHARE = "share"
    LIKE = "like"
    COMMENT = "comment"
    SUBSCRIBE = "subscribe"


class TrackingSource(Enum):
    """Tracking data sources"""

    DIRECT_API = "direct_api"
    PLATFORM_WEBHOOK = "platform_webhook"
    BATCH_IMPORT = "batch_import"
    CRAWLER = "crawler"
    SDK = "sdk"
    PIXEL_TRACKING = "pixel_tracking"


class UsageTracker:
    """
    Industrial-grade usage tracking system with real-time monitoring,
    analytics, and compliance validation capabilities.
    """
    
    def __init__(
        self,
        repository -> None: LicensingRepository = None,
        compliance_engine -> None: ComplianceEngine = None,
        analytics_engine -> None: AnalyticsEngine = None,
        cache_manager -> None: CacheManager = None,
        queue_manager -> None: QueueManager = None
    ) -> None:
        """
Initialize usage tracker with dependencies"""
        self.repository = repository or LicensingRepository()
        self.compliance_engine = compliance_engine or ComplianceEngine()
        self.analytics_engine = analytics_engine or AnalyticsEngine()
        self.cache_manager = cache_manager or CacheManager()
        self.queue_manager = queue_manager or QueueManager()
        self._logger = logger
        
        # Tracking configuration
        self.batch_size = settings.USAGE_TRACKING_BATCH_SIZE or 1000
        self.flush_interval = settings.USAGE_TRACKING_FLUSH_INTERVAL or 60  # seconds
        self.enable_real_time_compliance = settings.ENABLE_REAL_TIME_COMPLIANCE or True
        
        # Internal tracking buffer
        self._usage_buffer = []
        self._buffer_lock = asyncio.Lock()
        
        # Start background tasks
        self._background_tasks = []
        self._start_background_tasks()
    
    async def track_usage_event(
        self,
        license_agreement_id: UUID,
        event_type: str,
        event_data: Dict[str, Any],
        source: str = TrackingSource.DIRECT_API.value
    ) -> Dict[str, Any]:
        """
Track individual usage event with real-time compliance"""
        try:
            # Validate inputs
            await self._validate_tracking_event(license_agreement_id, event_type, event_data)
            
            # Get license agreement for validation
            license_agreement = await self.repository.get_license_agreement(
                license_agreement_id, include_relations=True
            )
            
            if not license_agreement:
                raise ValidationError(f"License agreement {license_agreement_id} not found")
            
            # Enrich event data
            enriched_event = await self._enrich_event_data(
                event_data, license_agreement, source
            )
            
            # Real-time compliance check
            compliance_result = None
            if self.enable_real_time_compliance:
                compliance_result = await self.compliance_engine.monitor_real_time_compliance(
                    license_agreement_id, enriched_event
                )
            
            # Create tracking record
            tracking_data = await self._create_tracking_record_data(
                license_agreement_id, event_type, enriched_event, source
            )
            
            # Store tracking record
            tracking_record = await self.repository.create_usage_tracking_record(
                tracking_data
            )
            
            # Process for analytics
            await self._process_for_analytics(tracking_record, license_agreement)
            
            # Queue for batch processing if needed
            await self._queue_for_batch_processing(tracking_record)
            
            result = {
                "tracking_id": tracking_record.tracking_id,
                "event_type": event_type,
                "timestamp": tracking_record.usage_date.isoformat(),
                "compliance_status": compliance_result.get("compliance_status") if compliance_result else "pending",
                "processed": True
            }
            
            if compliance_result and compliance_result.get("violations_detected"):
                result["compliance_violations"] = compliance_result["violations_detected"]
                result["immediate_actions"] = compliance_result.get("immediate_actions", [])
            
            self._logger.info(
                f"Tracked usage event {event_type} for license {license_agreement.license_number}"
            )
            
            return result
            
        except (ValidationError, TrackingError):
            raise
        except Exception as e:
            raise TrackingError(f"Error tracking usage event: {str(e)}")
    
    async def track_batch_usage(
        self,
        usage_events: List[Dict[str, Any]],
        source: str = TrackingSource.BATCH_IMPORT.value
    ) -> Dict[str, Any]:
        """Track multiple usage events in batch"""
        try:
            results = {
                "total_events": len(usage_events),
                "successful": 0,
                "failed": 0,
                "errors": [],
                "tracking_ids": []
            }
            
            # Process events in batches
            for i in range(0, len(usage_events), self.batch_size):
                batch = usage_events[i:i + self.batch_size]
                batch_results = await self._process_usage_batch(batch, source)
                
                results["successful"] += batch_results["successful"]
                results["failed"] += batch_results["failed"]
                results["errors"].extend(batch_results["errors"])
                results["tracking_ids"].extend(batch_results["tracking_ids"])
            
            self._logger.info(
                f"Processed batch of {results['total_events']} usage events: "
                f"{results['successful']} successful, {results['failed']} failed"
            )
            
            return results
            
        except Exception as e:
            raise TrackingError(f"Error processing batch usage: {str(e)}")
    
    async def get_usage_analytics(
        self,
        license_agreement_id: UUID,
        start_date: date = None,
        end_date: date = None,
        granularity: str = "day",
        metrics: List[str] = None,
        user_id: UUID = None
    ) -> Dict[str, Any]:
        """Get comprehensive usage analytics"""
        try:
            # Validate access
            license_agreement = await self.repository.get_license_agreement(
                license_agreement_id, user_id
            )
            
            if not license_agreement:
                raise ValidationError("License agreement not found or access denied")
            
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Get base analytics from repository
            base_analytics = await self.repository.get_license_usage_analytics(
                license_agreement_id, user_id, start_date, end_date
            )
            
            # Enhance with detailed analytics
            detailed_analytics = await self._generate_detailed_analytics(
                license_agreement_id, start_date, end_date, granularity, metrics
            )
            
            # Combine results
            analytics_result = {
                "license_id": str(license_agreement_id),
                "license_number": license_agreement.license_number,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "granularity": granularity
                },
                "summary": base_analytics["summary"],
                "detailed_metrics": detailed_analytics,
                "platform_breakdown": base_analytics["platform_breakdown"],
                "territory_breakdown": base_analytics["territory_breakdown"],
                "trends": await self._calculate_usage_trends(
                    license_agreement_id, start_date, end_date
                ),
                "compliance_summary": await self._get_compliance_summary(
                    license_agreement_id, start_date, end_date
                ),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics_result
            
        except (ValidationError, TrackingError):
            raise
        except Exception as e:
            raise TrackingError(f"Error generating usage analytics: {str(e)}")
    
    async def get_real_time_metrics(
        self,
        license_agreement_id: UUID,
        user_id: UUID = None
    ) -> Dict[str, Any]:
        """Get real-time usage metrics"""
        try:
            # Check cache for recent metrics
            cache_key = f"real_time_metrics:{license_agreement_id}"
            cached_metrics = await self.cache_manager.get(cache_key)
            
            if cached_metrics:
                return cached_metrics
            
            # Validate access
            license_agreement = await self.repository.get_license_agreement(
                license_agreement_id, user_id
            )
            
            if not license_agreement:
                raise ValidationError("License agreement not found or access denied")
            
            # Calculate real-time metrics
            current_time = datetime.utcnow()
            
            # Last 24 hours
            last_24h_metrics = await self._calculate_period_metrics(
                license_agreement_id, current_time - timedelta(hours=24), current_time
            )
            
            # Last hour
            last_hour_metrics = await self._calculate_period_metrics(
                license_agreement_id, current_time - timedelta(hours=1), current_time
            )
            
            # Current active sessions (if available)
            active_sessions = await self._get_active_sessions(license_agreement_id)
            
            real_time_metrics = {
                "license_id": str(license_agreement_id),
                "timestamp": current_time.isoformat(),
                "last_24_hours": last_24h_metrics,
                "last_hour": last_hour_metrics,
                "active_sessions": active_sessions,
                "current_status": await self._get_current_license_status(license_agreement),
                "recent_events": await self._get_recent_events(license_agreement_id, limit=10)
            }
            
            # Cache for 5 minutes
            await self.cache_manager.set(cache_key, real_time_metrics, ttl=300)
            
            return real_time_metrics
            
        except (ValidationError, TrackingError):
            raise
        except Exception as e:
            raise TrackingError(f"Error getting real-time metrics: {str(e)}")
    
    async def export_usage_data(
        self,
        license_agreement_id: UUID,
        start_date: date,
        end_date: date,
        format_type: str = "csv",
        user_id: UUID = None
    ) -> Dict[str, Any]:
        """Export usage data for reporting"""
        try:
            # Validate access and parameters
            license_agreement = await self.repository.get_license_agreement(
                license_agreement_id, user_id
            )
            
            if not license_agreement:
                raise ValidationError("License agreement not found or access denied")
            
            if format_type not in ["csv", "json", "xlsx"]:
                raise ValidationError(f"Unsupported export format: {format_type}")
            
            # Get detailed usage data
            usage_data = await self._get_detailed_usage_data(
                license_agreement_id, start_date, end_date
            )
            
            # Format data according to requested format
            formatted_data = await self._format_export_data(usage_data, format_type)
            
            # Generate export metadata
            export_metadata = {
                "export_id": await self._generate_export_id(),
                "license_id": str(license_agreement_id),
                "license_number": license_agreement.license_number,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "format": format_type,
                "record_count": len(usage_data),
                "generated_by": str(user_id) if user_id else "system",
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "metadata": export_metadata,
                "data": formatted_data,
                "download_url": await self._generate_download_url(export_metadata["export_id"])
            }
            
        except (ValidationError, TrackingError):
            raise
        except Exception as e:
            raise TrackingError(f"Error exporting usage data: {str(e)}")
    
    # Private helper methods
    
    async def _validate_tracking_event(
        self,
        license_agreement_id: UUID,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """Validate tracking event data"""
        # Validate UUID
        if not isinstance(license_agreement_id, UUID):
            raise ValidationError("Invalid license agreement ID format")
        
        # Validate event type
        if event_type not in [e.value for e in TrackingEvent]:
            raise ValidationError(f"Invalid event type: {event_type}")
        
        # Validate required event data fields
        required_fields = ["timestamp", "platform"]
        for field in required_fields:
            if field not in event_data:
                raise ValidationError(f"Missing required field: {field}")
    
    async def _enrich_event_data(
        self,
        event_data: Dict[str, Any],
        license_agreement: LicenseAgreement,
        source: str
    ) -> Dict[str, Any]:
        """Enrich event data with additional context"""
        enriched_data = event_data.copy()
        
        # Add license context
        enriched_data["license_number"] = license_agreement.license_number
        enriched_data["content_id"] = str(license_agreement.content_id)
        enriched_data["tracking_source"] = source
        
        # Add geolocation if IP provided
        if "ip_address" in event_data:
            geo_data = await self._get_geolocation(event_data["ip_address"])
            enriched_data.update(geo_data)
        
        # Add user agent parsing if provided
        if "user_agent" in event_data:
            device_data = await self._parse_user_agent(event_data["user_agent"])
            enriched_data.update(device_data)
        
        # Add timestamp normalization
        if "timestamp" in enriched_data:
            enriched_data["normalized_timestamp"] = await self._normalize_timestamp(
                enriched_data["timestamp"]
            )
        
        return enriched_data
    
    async def _create_tracking_record_data(
        self,
        license_agreement_id: UUID,
        event_type: str,
        event_data: Dict[str, Any],
        source: str
    ) -> Dict[str, Any]:
        """Create tracking record data structure"""
        return {
            "license_agreement_id": license_agreement_id,
            "usage_date": event_data.get("normalized_timestamp", datetime.utcnow()),
            "usage_type": event_type,
            "platform": event_data.get("platform"),
            "territory": event_data.get("territory"),
            "play_count": 1 if event_type == TrackingEvent.PLAY.value else 0,
            "stream_count": 1 if event_type == TrackingEvent.STREAM.value else 0,
            "download_count": 1 if event_type == TrackingEvent.DOWNLOAD.value else 0,
            "view_count": 1 if event_type == TrackingEvent.VIEW.value else 0,
            "impression_count": 1 if event_type == TrackingEvent.IMPRESSION.value else 0,
            "click_count": 1 if event_type == TrackingEvent.CLICK.value else 0,
            "share_count": 1 if event_type == TrackingEvent.SHARE.value else 0,
            "total_play_duration": event_data.get("play_duration", 0),
            "average_play_duration": event_data.get("play_duration", 0),
            "completion_rate": event_data.get("completion_rate", 0.0),
            "revenue_generated": event_data.get("revenue", 0),
            "revenue_currency": event_data.get("currency", "USD"),
            "age_group_breakdown": event_data.get("demographics", {}).get("age_groups"),
            "gender_breakdown": event_data.get("demographics", {}).get("gender"),
            "device_breakdown": event_data.get("device_info"),
            "ip_address": event_data.get("ip_address"),
            "user_agent": event_data.get("user_agent"),
            "referrer_url": event_data.get("referrer"),
            "session_id": event_data.get("session_id"),
            "custom_metadata": event_data.get("custom_metadata"),
            "tracking_source": source
        }
    
    async def _process_for_analytics(
        self,
        tracking_record: LicenseUsageTracking,
        license_agreement: LicenseAgreement
    ) -> None:
        """Process tracking record for analytics"""
        if self.analytics_engine:
            await self.analytics_engine.process_usage_event(
                tracking_record, license_agreement
            )
    
    async def _queue_for_batch_processing(
        self,
        tracking_record: LicenseUsageTracking
    ) -> None:
        """
Queue tracking record for batch processing"""
        if self.queue_manager:
            await self.queue_manager.enqueue(
                "usage_tracking_batch",
                {
                    "tracking_id": tracking_record.tracking_id,
                    "license_id": str(tracking_record.license_agreement_id),
                    "event_type": tracking_record.usage_type,
                    "timestamp": tracking_record.usage_date.isoformat()
                }
            )
    
    async def _generate_detailed_analytics(
        self,
        license_agreement_id: UUID,
        start_date: date,
        end_date: date,
        granularity: str,
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """Generate detailed analytics for the specified period"""
        # Implementation would generate time-series data, aggregations, etc.
        return {
            "time_series": await self._generate_time_series_data(
                license_agreement_id, start_date, end_date, granularity
            ),
            "aggregations": await self._calculate_aggregations(
                license_agreement_id, start_date, end_date, metrics
            ),
            "comparisons": await self._calculate_period_comparisons(
                license_agreement_id, start_date, end_date
            )
        }
    
    def _start_background_tasks(self) -> None:
        """Start background processing tasks"""
        # Start batch processing task
        task = asyncio.create_task(self._background_batch_processor())
        self._background_tasks.append(task)
        
        # Start cache warming task
        task = asyncio.create_task(self._background_cache_warmer())
        self._background_tasks.append(task)
    
    async def _background_batch_processor(self) -> None:
        """
Background task for batch processing"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_usage_buffer()
            except Exception as e:
                self._logger.error(f"Error in background batch processor: {str(e)}")
    
    async def _background_cache_warmer(self) -> None:
        """Background task for cache warming"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                await self._warm_popular_caches()
            except Exception as e:
                self._logger.error(f"Error in background cache warmer: {str(e)}")
    
    async def _generate_export_id(self) -> str:
        """Generate unique export ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"EXPORT-{timestamp}-{hash(timestamp) % 10000:04d}"
