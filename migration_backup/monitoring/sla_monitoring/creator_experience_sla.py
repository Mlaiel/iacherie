"""Creator Experience SLA Monitoring System
Advanced SLA tracking for creator journey optimization and user experience metrics.

⚠️ PROPRIETARY CODE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use, distribution, or modification is strictly prohibited.
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import deque, defaultdict
import json
import time
from enum import Enum

class CreatorJourneyStage(Enum):
    """Creator journey stages for SLA tracking"""
    ONBOARDING = "onboarding"
    CONTENT_UPLOAD = "content_upload"
    PROFILE_SETUP = "profile_setup"
    FIRST_MONETIZATION = "first_monetization"
    COLLABORATION_SETUP = "collaboration_setup"
    PLATFORM_MASTERY = "platform_mastery"

@dataclass
class CreatorExperienceMetric:
    """Creator experience metric with SLA targets"""
    metric_name: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    journey_stage: CreatorJourneyStage = CreatorJourneyStage.ONBOARDING
    creator_tier: str = "standard"
    measurement_window: int = 300  # 5 minutes default
    last_measurement: datetime = field(default_factory=datetime.now)
    violation_count: int = 0
    
@dataclass
class CreatorSLATargets:
    """Comprehensive Creator Experience SLA targets"""
    # Onboarding SLA
    onboarding_completion_seconds: float = 300.0  # <5min setup
    profile_setup_seconds: float = 180.0  # <3min profile completion
    first_upload_success_rate: float = 99.5  # 99.5% first upload success
    
    # Content Processing SLA  
    upload_processing_seconds: float = 30.0  # <30s processing
    format_conversion_seconds: float = 60.0  # <60s format conversion
    content_analysis_seconds: float = 10.0  # <10s AI analysis
    
    # Dashboard & Platform Responsiveness
    dashboard_load_seconds: float = 2.0  # <2s dashboard load
    api_response_ms: float = 200.0  # <200ms API response
    search_response_seconds: float = 1.0  # <1s search response
    
    # Creator Support SLA
    support_response_hours: float = 1.0  # <1h support response
    chat_response_seconds: float = 30.0  # <30s chat response
    ticket_resolution_hours: float = 24.0  # <24h ticket resolution
    
    # Creator Satisfaction & Engagement
    satisfaction_score: float = 95.0  # >95% satisfaction
    platform_adoption_rate: float = 90.0  # >90% feature adoption
    creator_retention_rate: float = 95.0  # >95% monthly retention
    
    # Performance & Reliability
    platform_uptime: float = 99.99  # 99.99% uptime
    feature_availability: float = 99.95  # 99.95% feature availability
    data_sync_seconds: float = 5.0  # <5s data synchronization

class CreatorExperienceSLA:
    """
    Advanced Creator Experience SLA monitoring system
    Tracks all aspects of creator journey and platform interaction
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.targets = CreatorSLATargets()
        self.metrics: Dict[str, CreatorExperienceMetric] = {}
        self.measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Dict[str, Any]] = []
        self.creator_profiles: Dict[str, Dict[str, Any]] = {}
        self.journey_tracking: Dict[str, Dict[str, Any]] = {}
        
        # Performance monitoring
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.error_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.satisfaction_scores: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        
        self._setup_default_metrics()
        
    def _setup_default_metrics(self):
        """Initialize default creator experience metrics"""
        default_metrics = [
            ("onboarding_time", self.targets.onboarding_completion_seconds, "seconds", CreatorJourneyStage.ONBOARDING),
            ("upload_processing_time", self.targets.upload_processing_seconds, "seconds", CreatorJourneyStage.CONTENT_UPLOAD),
            ("dashboard_load_time", self.targets.dashboard_load_seconds, "seconds", CreatorJourneyStage.PLATFORM_MASTERY),
            ("api_response_time", self.targets.api_response_ms, "milliseconds", CreatorJourneyStage.PLATFORM_MASTERY),
            ("support_response_time", self.targets.support_response_hours, "hours", CreatorJourneyStage.PLATFORM_MASTERY),
            ("creator_satisfaction", self.targets.satisfaction_score, "percentage", CreatorJourneyStage.PLATFORM_MASTERY),
            ("platform_uptime", self.targets.platform_uptime, "percentage", CreatorJourneyStage.PLATFORM_MASTERY),
        ]
        
        for metric_name, target, unit, stage in default_metrics:
            self.metrics[metric_name] = CreatorExperienceMetric(
                metric_name=metric_name,
                target_value=target,
                unit=unit,
                journey_stage=stage
            )
    
    async def track_creator_onboarding(self, creator_id: str, start_time: datetime, completion_time: datetime) -> Dict[str, Any]:
        """Track creator onboarding process SLA compliance"""
        try:
            onboarding_duration = (completion_time - start_time).total_seconds()
            
            # Update metric
            metric = self.metrics["onboarding_time"]
            metric.current_value = onboarding_duration
            metric.last_measurement = completion_time
            
            # Check SLA compliance
            is_compliant = onboarding_duration <= self.targets.onboarding_completion_seconds
            
            if not is_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Creator Onboarding SLA Violation",
                    f"Creator {creator_id} onboarding took {onboarding_duration:.2f}s (target: {self.targets.onboarding_completion_seconds}s)",
                    "high",
                    {"creator_id": creator_id, "duration": onboarding_duration}
                )
            
            # Store measurement
            self.measurements["onboarding_time"].append({
                "timestamp": completion_time,
                "value": onboarding_duration,
                "creator_id": creator_id,
                "compliant": is_compliant
            })
            
            # Update creator journey tracking
            self.journey_tracking[creator_id] = {
                "onboarding_completed": completion_time,
                "onboarding_duration": onboarding_duration,
                "onboarding_compliant": is_compliant,
                "current_stage": CreatorJourneyStage.CONTENT_UPLOAD.value
            }
            
            self.logger.info(f"Creator onboarding tracked - ID: {creator_id}, Duration: {onboarding_duration:.2f}s, Compliant: {is_compliant}")
            
            return {
                "creator_id": creator_id,
                "onboarding_duration": onboarding_duration,
                "sla_compliant": is_compliant,
                "target_seconds": self.targets.onboarding_completion_seconds
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking creator onboarding: {e}")
            raise
    
    async def track_content_upload_performance(self, creator_id: str, upload_id: str, 
                                             start_time: datetime, completion_time: datetime,
                                             file_size_mb: float, content_type: str) -> Dict[str, Any]:
        """Track content upload processing SLA compliance"""
        try:
            processing_duration = (completion_time - start_time).total_seconds()
            
            # Update metric
            metric = self.metrics["upload_processing_time"]
            metric.current_value = processing_duration
            metric.last_measurement = completion_time
            
            # Dynamic SLA based on file size and type
            size_factor = min(file_size_mb / 100, 2.0)  # Max 2x for large files
            type_factor = 1.5 if content_type in ["video", "audio"] else 1.0
            adjusted_target = self.targets.upload_processing_seconds * size_factor * type_factor
            
            is_compliant = processing_duration <= adjusted_target
            
            if not is_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Content Upload SLA Violation",
                    f"Upload {upload_id} took {processing_duration:.2f}s (target: {adjusted_target:.2f}s)",
                    "medium",
                    {
                        "creator_id": creator_id,
                        "upload_id": upload_id,
                        "duration": processing_duration,
                        "file_size_mb": file_size_mb,
                        "content_type": content_type
                    }
                )
            
            # Store measurement
            self.measurements["upload_processing_time"].append({
                "timestamp": completion_time,
                "value": processing_duration,
                "creator_id": creator_id,
                "upload_id": upload_id,
                "file_size_mb": file_size_mb,
                "content_type": content_type,
                "compliant": is_compliant,
                "adjusted_target": adjusted_target
            })
            
            self.logger.info(f"Content upload tracked - Creator: {creator_id}, Upload: {upload_id}, Duration: {processing_duration:.2f}s")
            
            return {
                "creator_id": creator_id,
                "upload_id": upload_id,
                "processing_duration": processing_duration,
                "sla_compliant": is_compliant,
                "adjusted_target": adjusted_target,
                "file_size_mb": file_size_mb
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking content upload: {e}")
            raise
    
    async def track_dashboard_performance(self, creator_id: str, page_type: str, 
                                        load_start: datetime, load_complete: datetime) -> Dict[str, Any]:
        """Track dashboard and UI responsiveness SLA"""
        try:
            load_duration = (load_complete - load_start).total_seconds()
            
            # Update metric
            metric = self.metrics["dashboard_load_time"]
            metric.current_value = load_duration
            metric.last_measurement = load_complete
            
            # Page-specific SLA targets
            page_targets = {
                "main_dashboard": self.targets.dashboard_load_seconds,
                "analytics": self.targets.dashboard_load_seconds * 1.5,
                "content_library": self.targets.dashboard_load_seconds * 1.2,
                "monetization": self.targets.dashboard_load_seconds,
                "settings": self.targets.dashboard_load_seconds * 0.8
            }
            
            target = page_targets.get(page_type, self.targets.dashboard_load_seconds)
            is_compliant = load_duration <= target
            
            if not is_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Dashboard Performance SLA Violation",
                    f"Dashboard page '{page_type}' took {load_duration:.2f}s to load (target: {target:.2f}s)",
                    "medium",
                    {
                        "creator_id": creator_id,
                        "page_type": page_type,
                        "load_duration": load_duration
                    }
                )
            
            # Store measurement
            self.measurements["dashboard_load_time"].append({
                "timestamp": load_complete,
                "value": load_duration,
                "creator_id": creator_id,
                "page_type": page_type,
                "compliant": is_compliant,
                "target": target
            })
            
            # Update response time tracking
            self.response_times[page_type].append(load_duration)
            
            return {
                "creator_id": creator_id,
                "page_type": page_type,
                "load_duration": load_duration,
                "sla_compliant": is_compliant,
                "target_seconds": target
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking dashboard performance: {e}")
            raise
    
    async def track_creator_satisfaction(self, creator_id: str, satisfaction_score: float, 
                                       feedback_category: str, timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """Track creator satisfaction metrics and SLA compliance"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Update metric
            metric = self.metrics["creator_satisfaction"]
            metric.current_value = satisfaction_score
            metric.last_measurement = timestamp
            
            is_compliant = satisfaction_score >= self.targets.satisfaction_score
            
            if not is_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Creator Satisfaction SLA Violation",
                    f"Creator {creator_id} satisfaction score: {satisfaction_score}% (target: {self.targets.satisfaction_score}%)",
                    "high",
                    {
                        "creator_id": creator_id,
                        "satisfaction_score": satisfaction_score,
                        "feedback_category": feedback_category
                    }
                )
            
            # Store measurement
            self.measurements["creator_satisfaction"].append({
                "timestamp": timestamp,
                "value": satisfaction_score,
                "creator_id": creator_id,
                "feedback_category": feedback_category,
                "compliant": is_compliant
            })
            
            # Update satisfaction tracking
            self.satisfaction_scores[creator_id].append(satisfaction_score)
            
            return {
                "creator_id": creator_id,
                "satisfaction_score": satisfaction_score,
                "sla_compliant": is_compliant,
                "target_score": self.targets.satisfaction_score,
                "feedback_category": feedback_category
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking creator satisfaction: {e}")
            raise
    
    async def track_support_response(self, creator_id: str, ticket_id: str, 
                                   ticket_created: datetime, first_response: datetime,
                                   priority: str = "medium") -> Dict[str, Any]:
        """Track creator support response time SLA"""
        try:
            response_duration = (first_response - ticket_created).total_seconds() / 3600  # Convert to hours
            
            # Update metric
            metric = self.metrics["support_response_time"]
            metric.current_value = response_duration
            metric.last_measurement = first_response
            
            # Priority-based SLA targets
            priority_targets = {
                "critical": self.targets.support_response_hours * 0.25,  # 15 minutes
                "high": self.targets.support_response_hours * 0.5,      # 30 minutes
                "medium": self.targets.support_response_hours,          # 1 hour
                "low": self.targets.support_response_hours * 2          # 2 hours
            }
            
            target = priority_targets.get(priority, self.targets.support_response_hours)
            is_compliant = response_duration <= target
            
            if not is_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Support Response SLA Violation",
                    f"Support ticket {ticket_id} response took {response_duration:.2f}h (target: {target:.2f}h)",
                    "high" if priority in ["critical", "high"] else "medium",
                    {
                        "creator_id": creator_id,
                        "ticket_id": ticket_id,
                        "response_duration_hours": response_duration,
                        "priority": priority
                    }
                )
            
            # Store measurement
            self.measurements["support_response_time"].append({
                "timestamp": first_response,
                "value": response_duration,
                "creator_id": creator_id,
                "ticket_id": ticket_id,
                "priority": priority,
                "compliant": is_compliant,
                "target": target
            })
            
            return {
                "creator_id": creator_id,
                "ticket_id": ticket_id,
                "response_duration_hours": response_duration,
                "sla_compliant": is_compliant,
                "target_hours": target,
                "priority": priority
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking support response: {e}")
            raise
    
    async def get_creator_experience_summary(self, creator_id: Optional[str] = None, 
                                           time_window_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive creator experience SLA summary"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            summary = {
                "time_window_hours": time_window_hours,
                "cutoff_time": cutoff_time.isoformat(),
                "overall_compliance": {},
                "metric_summaries": {},
                "creator_specific": {},
                "journey_analytics": {},
                "recommendations": []
            }
            
            # Calculate overall compliance for each metric
            for metric_name, metric in self.metrics.items():
                measurements = [
                    m for m in self.measurements[metric_name]
                    if m["timestamp"] >= cutoff_time
                ]
                
                if measurements:
                    compliant_count = sum(1 for m in measurements if m["compliant"])
                    compliance_rate = (compliant_count / len(measurements)) * 100
                    
                    avg_value = statistics.mean([m["value"] for m in measurements])
                    p95_value = statistics.quantiles([m["value"] for m in measurements], n=20)[18] if len(measurements) >= 20 else max([m["value"] for m in measurements])
                    
                    summary["metric_summaries"][metric_name] = {
                        "compliance_rate": compliance_rate,
                        "measurement_count": len(measurements),
                        "avg_value": avg_value,
                        "p95_value": p95_value,
                        "target_value": metric.target_value,
                        "unit": metric.unit,
                        "violation_count": metric.violation_count
                    }
                    
                    summary["overall_compliance"][metric_name] = compliance_rate >= 95.0
            
            # Creator-specific analysis if requested
            if creator_id:
                creator_measurements = {}
                for metric_name, measurements in self.measurements.items():
                    creator_data = [
                        m for m in measurements
                        if m.get("creator_id") == creator_id and m["timestamp"] >= cutoff_time
                    ]
                    if creator_data:
                        creator_measurements[metric_name] = creator_data
                
                summary["creator_specific"] = {
                    "creator_id": creator_id,
                    "measurements": creator_measurements,
                    "journey_stage": self.journey_tracking.get(creator_id, {}).get("current_stage", "unknown"),
                    "satisfaction_trend": list(self.satisfaction_scores.get(creator_id, []))[-10:]  # Last 10 scores
                }
            
            # Journey analytics
            journey_stats = defaultdict(list)
            for creator_id, journey in self.journey_tracking.items():
                if "onboarding_duration" in journey:
                    journey_stats["onboarding_durations"].append(journey["onboarding_duration"])
                    journey_stats["onboarding_compliance"].append(journey.get("onboarding_compliant", False))
            
            if journey_stats["onboarding_durations"]:
                summary["journey_analytics"] = {
                    "avg_onboarding_duration": statistics.mean(journey_stats["onboarding_durations"]),
                    "onboarding_compliance_rate": (sum(journey_stats["onboarding_compliance"]) / len(journey_stats["onboarding_compliance"])) * 100,
                    "total_creators_tracked": len(self.journey_tracking)
                }
            
            # Generate recommendations
            for metric_name, compliance in summary["overall_compliance"].items():
                if not compliance:
                    metric_summary = summary["metric_summaries"][metric_name]
                    if metric_name == "onboarding_time":
                        summary["recommendations"].append("Optimize onboarding flow - simplify form fields and add progress indicators")
                    elif metric_name == "upload_processing_time":
                        summary["recommendations"].append("Implement parallel processing for content uploads and optimize AI processing pipeline")
                    elif metric_name == "dashboard_load_time":
                        summary["recommendations"].append("Implement dashboard caching and lazy loading for improved performance")
                    elif metric_name == "creator_satisfaction":
                        summary["recommendations"].append("Conduct creator surveys to identify pain points and implement UX improvements")
                    elif metric_name == "support_response_time":
                        summary["recommendations"].append("Expand support team capacity and implement AI-powered ticket routing")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating creator experience summary: {e}")
            raise
    
    async def _generate_alert(self, title: str, message: str, severity: str, metadata: Dict[str, Any]):
        """Generate SLA violation alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "severity": severity,
            "component": "creator_experience_sla",
            "metadata": metadata
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"SLA Alert - {title}: {message}")
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time creator experience metrics for monitoring dashboards"""
        try:
            current_time = datetime.now()
            
            metrics_data = {}
            for metric_name, metric in self.metrics.items():
                # Get recent measurements (last 5 minutes)
                recent_measurements = [
                    m for m in self.measurements[metric_name]
                    if (current_time - m["timestamp"]).total_seconds() <= 300
                ]
                
                if recent_measurements:
                    current_avg = statistics.mean([m["value"] for m in recent_measurements])
                    compliance_rate = (sum(1 for m in recent_measurements if m["compliant"]) / len(recent_measurements)) * 100
                else:
                    current_avg = metric.current_value
                    compliance_rate = 100.0 if metric.current_value <= metric.target_value else 0.0
                
                metrics_data[metric_name] = {
                    "current_value": current_avg,
                    "target_value": metric.target_value,
                    "compliance_rate": compliance_rate,
                    "unit": metric.unit,
                    "status": "compliant" if compliance_rate >= 95.0 else "violation",
                    "last_updated": metric.last_measurement.isoformat(),
                    "recent_measurements_count": len(recent_measurements)
                }
            
            return {
                "timestamp": current_time.isoformat(),
                "metrics": metrics_data,
                "overall_health": "healthy" if all(m["compliance_rate"] >= 95.0 for m in metrics_data.values()) else "degraded",
                "active_alerts_count": len([a for a in self.alerts if (current_time - datetime.fromisoformat(a["timestamp"])).total_seconds() <= 3600])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            raise

# Global instance for easy access
creator_experience_sla = CreatorExperienceSLA()