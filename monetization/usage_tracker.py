"""Usage Tracker - Content Usage Monitoring System
===============================================

Advanced usage tracking system for content licenses with real-time monitoring,
analytics, and comprehensive reporting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class UsageType(Enum):
    """Types of content usage"""    STREAM = "stream"
    DOWNLOAD = "download"
    SYNC = "sync"
    COMMERCIAL = "commercial"
    BROADCAST = "broadcast"
    PUBLIC_PERFORMANCE = "public_performance"
    PREVIEW = "preview"
    SAMPLE = "sample"


class UsageStatus(Enum):
    """Status of usage records"""    RECORDED = "recorded"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


@dataclass
class UsageRecord:
    """Individual usage record"""    record_id: str
    license_id: int
    content_id: int
    user_id: int
    usage_type: UsageType
    usage_count: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: UsageStatus = UsageStatus.RECORDED
    verification_data: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    platform: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None


@dataclass
class UsageStatistics:
    """Usage statistics for a license"""    license_id: int
    period_start: datetime
    period_end: datetime
    total_usage: int
    usage_by_type: Dict[str, int]
    unique_users: int
    peak_usage_hour: Optional[int]
    peak_usage_day: Optional[str]
    geographic_distribution: Dict[str, int]
    platform_distribution: Dict[str, int]
    growth_rate: float


class UsageTracker:
    """    Advanced usage tracking and analytics system
    
    Features:
    - Real-time usage recording
    - Multi-dimensional analytics
    - Usage limit enforcement
    - Fraud detection
    - Geographic tracking
    - Platform-specific metrics
    - Historical trend analysis
    - Automated reporting
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize usage tracker"""        self.config = config or {}
        
        # Usage storage
        self.usage_records: List[UsageRecord] = []
        self.usage_cache: Dict[str, Any] = {}
        
        # Real-time tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.usage_queues: Dict[int, deque] = defaultdict(deque)  # license_id -> usage queue
        
        # Analytics cache
        self.statistics_cache: Dict[str, UsageStatistics] = {}
        self.analytics_last_updated: Dict[int, datetime] = {}
        
        # Fraud detection
        self.suspicious_patterns: List[Dict[str, Any]] = []
        self.user_usage_patterns: Dict[int, Dict[str, Any]] = defaultdict(dict)
        
        # Configuration
        self.fraud_detection_enabled = self.config.get("fraud_detection", True)
        self.real_time_analytics = self.config.get("real_time_analytics", True)
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes
        
        # Performance metrics
        self.metrics = {
            "total_records": 0,
            "records_per_minute": 0,
            "unique_licenses": 0,
            "unique_users": 0,
            "fraud_detections": 0
        }
        
        logger.info("UsageTracker initialized successfully")
    
    async def record_usage(self, usage_data: Dict[str, Any]) -> str:
        """        Record a usage event
        
        Args:
            usage_data: Usage event data
            
        Returns:
            str: Usage record ID
        """        try:
            # Generate record ID
            record_id = f"usage_{usage_data['license_id']}_{datetime.utcnow().timestamp()}"
            
            # Create usage record
            record = UsageRecord(
                record_id=record_id,
                license_id=usage_data["license_id"],
                content_id=usage_data.get("content_id", 0),
                user_id=usage_data.get("user_id", 0),
                usage_type=UsageType(usage_data.get("usage_type", "stream")),
                usage_count=usage_data.get("usage_count", 1),
                timestamp=datetime.utcnow(),
                metadata=usage_data.get("usage_data", {}),
                location=usage_data.get("location"),
                platform=usage_data.get("platform"),
                device_info=usage_data.get("device_info")
            )
            
            # Store record
            self.usage_records.append(record)
            
            # Add to real-time queue
            self.usage_queues[record.license_id].append(record)
            
            # Update user patterns for fraud detection
            if self.fraud_detection_enabled:
                await self._update_user_patterns(record)
                await self._detect_fraud(record)
            
            # Update real-time analytics
            if self.real_time_analytics:
                await self._update_real_time_analytics(record)
            
            # Update metrics
            self.metrics["total_records"] += 1
            await self._update_performance_metrics()
            
            logger.debug(f"Usage recorded: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error recording usage: {e}")
            raise
    
    async def get_usage_by_period(
        self,
        license_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """        Get usage records for a specific period
        
        Args:
            license_id: License ID
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            List[Dict]: Usage records in the period
        """        try:
            # Filter records by license and period
            filtered_records = [
                record for record in self.usage_records
                if (record.license_id == license_id and
                    start_date <= record.timestamp <= end_date)
            ]
            
            # Convert to dictionaries
            result = []
            for record in filtered_records:
                result.append({
                    "record_id": record.record_id,
                    "license_id": record.license_id,
                    "content_id": record.content_id,
                    "user_id": record.user_id,
                    "usage_type": record.usage_type.value,
                    "usage_count": record.usage_count,
                    "timestamp": record.timestamp.isoformat(),
                    "metadata": record.metadata,
                    "status": record.status.value,
                    "location": record.location,
                    "platform": record.platform,
                    "device_info": record.device_info
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting usage by period: {e}")
            return []
    
    async def get_current_usage(self, license_id: int, usage_type: str) -> int:
        """        Get current usage count for a license and usage type
        
        Args:
            license_id: License ID
            usage_type: Type of usage
            
        Returns:
            int: Current usage count
        """        try:
            # Get current month start
            now = datetime.utcnow()
            month_start = datetime(now.year, now.month, 1)
            
            # Count usage in current month
            count = sum(
                record.usage_count for record in self.usage_records
                if (record.license_id == license_id and
                    record.usage_type.value == usage_type and
                    record.timestamp >= month_start and
                    record.status != UsageStatus.CANCELLED)
            )
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting current usage: {e}")
            return 0
    
    async def get_license_usage_stats(self, license_id: int) -> Dict[str, Any]:
        """        Get comprehensive usage statistics for a license
        
        Args:
            license_id: License ID
            
        Returns:
            Dict: Usage statistics
        """        try:
            cache_key = f"stats_{license_id}"
            
            # Check cache
            if (cache_key in self.statistics_cache and
                license_id in self.analytics_last_updated and
                (datetime.utcnow() - self.analytics_last_updated[license_id]).seconds < self.cache_ttl):
                return self._statistics_to_dict(self.statistics_cache[cache_key])
            
            # Calculate statistics
            license_records = [
                record for record in self.usage_records
                if record.license_id == license_id
            ]
            
            if not license_records:
                return {"error": "No usage records found"}
            
            # Time period (last 30 days)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # Filter records to period
            period_records = [
                record for record in license_records
                if start_date <= record.timestamp <= end_date
            ]
            
            # Calculate statistics
            total_usage = sum(record.usage_count for record in period_records)
            
            # Usage by type
            usage_by_type = defaultdict(int)
            for record in period_records:
                usage_by_type[record.usage_type.value] += record.usage_count
            
            # Unique users
            unique_users = len(set(record.user_id for record in period_records))
            
            # Peak usage analysis
            hourly_usage = defaultdict(int)
            daily_usage = defaultdict(int)
            
            for record in period_records:
                hour = record.timestamp.hour
                day = record.timestamp.strftime("%A")
                hourly_usage[hour] += record.usage_count
                daily_usage[day] += record.usage_count
            
            peak_hour = max(hourly_usage.items(), key=lambda x: x[1])[0] if hourly_usage else None
            peak_day = max(daily_usage.items(), key=lambda x: x[1])[0] if daily_usage else None
            
            # Geographic distribution
            geo_distribution = defaultdict(int)
            for record in period_records:
                if record.location:
                    geo_distribution[record.location] += record.usage_count
            
            # Platform distribution
            platform_distribution = defaultdict(int)
            for record in period_records:
                if record.platform:
                    platform_distribution[record.platform] += record.usage_count
            
            # Growth rate calculation
            prev_start = start_date - timedelta(days=30)
            prev_records = [
                record for record in license_records
                if prev_start <= record.timestamp < start_date
            ]
            prev_total = sum(record.usage_count for record in prev_records)
            
            growth_rate = ((total_usage - prev_total) / prev_total * 100) if prev_total > 0 else 0
            
            # Create statistics object
            stats = UsageStatistics(
                license_id=license_id,
                period_start=start_date,
                period_end=end_date,
                total_usage=total_usage,
                usage_by_type=dict(usage_by_type),
                unique_users=unique_users,
                peak_usage_hour=peak_hour,
                peak_usage_day=peak_day,
                geographic_distribution=dict(geo_distribution),
                platform_distribution=dict(platform_distribution),
                growth_rate=growth_rate
            )
            
            # Cache statistics
            self.statistics_cache[cache_key] = stats
            self.analytics_last_updated[license_id] = datetime.utcnow()
            
            return self._statistics_to_dict(stats)
            
        except Exception as e:
            logger.error(f"Error getting license usage stats: {e}")
            return {"error": str(e)}
    
    async def get_real_time_analytics(self, license_id: int) -> Dict[str, Any]:
        """        Get real-time analytics for a license
        
        Args:
            license_id: License ID
            
        Returns:
            Dict: Real-time analytics data
        """        try:
            # Get recent usage (last hour)
            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=1)
            
            recent_records = [
                record for record in self.usage_records
                if (record.license_id == license_id and
                    record.timestamp >= hour_ago)
            ]
            
            # Calculate real-time metrics
            current_usage = len(recent_records)
            usage_rate = current_usage / 60  # per minute
            
            # Usage by minute (last hour)
            minute_usage = defaultdict(int)
            for record in recent_records:
                minute_key = record.timestamp.strftime("%H:%M")
                minute_usage[minute_key] += record.usage_count
            
            # Active sessions
            active_sessions = len([
                session for session in self.active_sessions.values()
                if session.get("license_id") == license_id
            ])
            
            return {
                "license_id": license_id,
                "timestamp": now.isoformat(),
                "current_usage_hour": current_usage,
                "usage_rate_per_minute": round(usage_rate, 2),
                "active_sessions": active_sessions,
                "minute_breakdown": dict(minute_usage),
                "trending": self._calculate_trend(license_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time analytics: {e}")
            return {"error": str(e)}
    
    async def detect_usage_anomalies(self, license_id: int) -> List[Dict[str, Any]]:
        """        Detect usage anomalies for fraud prevention
        
        Args:
            license_id: License ID
            
        Returns:
            List[Dict]: Detected anomalies
        """        anomalies = []
        
        try:
            # Get recent usage patterns
            now = datetime.utcnow()
            day_ago = now - timedelta(days=1)
            
            recent_records = [
                record for record in self.usage_records
                if (record.license_id == license_id and
                    record.timestamp >= day_ago)
            ]
            
            # Check for suspicious patterns
            
            # 1. Unusual volume spikes
            hourly_usage = defaultdict(int)
            for record in recent_records:
                hour_key = record.timestamp.strftime("%Y-%m-%d %H")
                hourly_usage[hour_key] += record.usage_count
            
            if hourly_usage:
                avg_hourly = sum(hourly_usage.values()) / len(hourly_usage)
                max_hourly = max(hourly_usage.values())
                
                if max_hourly > avg_hourly * 5:  # 5x average
                    anomalies.append({
                        "type": "volume_spike",
                        "description": f"Usage spike detected: {max_hourly} vs {avg_hourly:.1f} average",
                        "severity": "high",
                        "detected_at": now.isoformat()
                    })
            
            # 2. Geographic inconsistencies
            user_locations = defaultdict(set)
            for record in recent_records:
                if record.location:
                    user_locations[record.user_id].add(record.location)
            
            for user_id, locations in user_locations.items():
                if len(locations) > 3:  # User in more than 3 locations in 24h
                    anomalies.append({
                        "type": "geographic_anomaly",
                        "description": f"User {user_id} active in {len(locations)} locations",
                        "severity": "medium",
                        "detected_at": now.isoformat(),
                        "user_id": user_id
                    })
            
            # 3. Unusual timing patterns
            night_usage = [
                record for record in recent_records
                if 0 <= record.timestamp.hour <= 5  # Between midnight and 5 AM
            ]
            
            if len(night_usage) > len(recent_records) * 0.8:  # 80% night usage
                anomalies.append({
                    "type": "timing_anomaly",
                    "description": "Unusual concentration of night-time usage",
                    "severity": "medium",
                    "detected_at": now.isoformat()
                })
            
            # Store suspicious patterns
            for anomaly in anomalies:
                anomaly["license_id"] = license_id
                self.suspicious_patterns.append(anomaly)
            
            # Update fraud detection metrics
            self.metrics["fraud_detections"] += len(anomalies)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    async def start_session(self, session_data: Dict[str, Any]) -> str:
        """Start a usage tracking session"""        try:
            session_id = f"session_{datetime.utcnow().timestamp()}"
            
            self.active_sessions[session_id] = {
                **session_data,
                "started_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
            
            logger.debug(f"Session started: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return ""
    
    async def end_session(self, session_id: str) -> bool:
        """End a usage tracking session"""        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session["ended_at"] = datetime.utcnow()
                
                # Calculate session duration
                duration = session["ended_at"] - session["started_at"]
                session["duration_seconds"] = duration.total_seconds()
                
                # Remove from active sessions
                del self.active_sessions[session_id]
                
                logger.debug(f"Session ended: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return False
    
    async def _update_user_patterns(self, record: UsageRecord) -> None:
        """Update user usage patterns for fraud detection"""        try:
            user_id = record.user_id
            
            if user_id not in self.user_usage_patterns:
                self.user_usage_patterns[user_id] = {
                    "total_usage": 0,
                    "usage_types": set(),
                    "locations": set(),
                    "platforms": set(),
                    "hours": set(),
                    "first_seen": record.timestamp,
                    "last_seen": record.timestamp
                }
            
            pattern = self.user_usage_patterns[user_id]
            pattern["total_usage"] += record.usage_count
            pattern["usage_types"].add(record.usage_type.value)
            pattern["last_seen"] = record.timestamp
            
            if record.location:
                pattern["locations"].add(record.location)
            if record.platform:
                pattern["platforms"].add(record.platform)
            
            pattern["hours"].add(record.timestamp.hour)
            
        except Exception as e:
            logger.error(f"Error updating user patterns: {e}")
    
    async def _detect_fraud(self, record: UsageRecord) -> None:
        """Detect potential fraud in usage record"""        try:
            user_pattern = self.user_usage_patterns.get(record.user_id, {})
            
            # Check for rapid usage increases
            if user_pattern.get("total_usage", 0) > 1000:  # High usage threshold
                time_span = (record.timestamp - user_pattern["first_seen"]).total_seconds()
                if time_span < 3600:  # Less than 1 hour
                    logger.warning(f"Potential fraud: User {record.user_id} high usage in short time")
            
        except Exception as e:
            logger.error(f"Error detecting fraud: {e}")
    
    async def _update_real_time_analytics(self, record: UsageRecord) -> None:
        """Update real-time analytics cache"""        try:
            cache_key = f"realtime_{record.license_id}"
            
            if cache_key not in self.usage_cache:
                self.usage_cache[cache_key] = {
                    "minute_counts": defaultdict(int),
                    "total_today": 0,
                    "last_updated": datetime.utcnow()
                }
            
            cache_data = self.usage_cache[cache_key]
            minute_key = record.timestamp.strftime("%H:%M")
            cache_data["minute_counts"][minute_key] += record.usage_count
            
            # Reset daily count if new day
            if record.timestamp.date() != cache_data["last_updated"].date():
                cache_data["total_today"] = 0
            
            cache_data["total_today"] += record.usage_count
            cache_data["last_updated"] = record.timestamp
            
        except Exception as e:
            logger.error(f"Error updating real-time analytics: {e}")
    
    async def _update_performance_metrics(self) -> None:
        """Update performance metrics"""        try:
            # Update records per minute
            now = datetime.utcnow()
            minute_ago = now - timedelta(minutes=1)
            
            recent_records = [
                record for record in self.usage_records
                if record.timestamp >= minute_ago
            ]
            
            self.metrics["records_per_minute"] = len(recent_records)
            
            # Update unique counts
            all_licenses = set(record.license_id for record in self.usage_records)
            all_users = set(record.user_id for record in self.usage_records)
            
            self.metrics["unique_licenses"] = len(all_licenses)
            self.metrics["unique_users"] = len(all_users)
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    def _calculate_trend(self, license_id: int) -> str:
        """Calculate usage trend for license"""        try:
            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=1)
            two_hours_ago = now - timedelta(hours=2)
            
            # Get usage counts for last two hours
            current_hour = len([
                record for record in self.usage_records
                if (record.license_id == license_id and
                    record.timestamp >= hour_ago)
            ])
            
            previous_hour = len([
                record for record in self.usage_records
                if (record.license_id == license_id and
                    two_hours_ago <= record.timestamp < hour_ago)
            ])
            
            if previous_hour == 0:
                return "stable"
            
            change_rate = (current_hour - previous_hour) / previous_hour
            
            if change_rate > 0.2:
                return "increasing"
            elif change_rate < -0.2:
                return "decreasing"
            else:
                return "stable"
                
        except Exception:
            return "unknown"
    
    def _statistics_to_dict(self, stats: UsageStatistics) -> Dict[str, Any]:
        """Convert UsageStatistics to dictionary"""        return {
            "license_id": stats.license_id,
            "period": {
                "start": stats.period_start.isoformat(),
                "end": stats.period_end.isoformat()
            },
            "total_usage": stats.total_usage,
            "usage_by_type": stats.usage_by_type,
            "unique_users": stats.unique_users,
            "peak_usage_hour": stats.peak_usage_hour,
            "peak_usage_day": stats.peak_usage_day,
            "geographic_distribution": stats.geographic_distribution,
            "platform_distribution": stats.platform_distribution,
            "growth_rate": round(stats.growth_rate, 2)
        }
    
    def get_tracker_stats(self) -> Dict[str, Any]:
        """Get usage tracker statistics"""        return {
            "version": "1.0.0",
            "metrics": self.metrics,
            "active_sessions": len(self.active_sessions),
            "cached_analytics": len(self.statistics_cache),
            "suspicious_patterns": len(self.suspicious_patterns),
            "configuration": {
                "fraud_detection_enabled": self.fraud_detection_enabled,
                "real_time_analytics": self.real_time_analytics,
                "cache_ttl": self.cache_ttl
            },
            "supported_usage_types": [usage_type.value for usage_type in UsageType]
        }