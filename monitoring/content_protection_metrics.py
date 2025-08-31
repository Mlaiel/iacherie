"""🛡️ Content Protection Metrics - Advanced Security & Copyright Analytics
======================================================================

Comprehensive metrics for content protection, copyright detection,
fingerprinting accuracy, and intellectual property security on the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
from collections import defaultdict, Counter
import statistics
import hashlib

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class ProtectionType(Enum):
    """Types of content protection"""
    COPYRIGHT_DETECTION = "copyright_detection"
    FINGERPRINT_MATCHING = "fingerprint_matching"
    WATERMARK_DETECTION = "watermark_detection"
    PLAGIARISM_CHECK = "plagiarism_check"
    BRAND_PROTECTION = "brand_protection"
    DMCA_COMPLIANCE = "dmca_compliance"


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionMethod(Enum):
    """Detection method types"""
    VISUAL_FINGERPRINTING = "visual_fingerprinting"
    AUDIO_FINGERPRINTING = "audio_fingerprinting"
    HASH_MATCHING = "hash_matching"
    ML_CLASSIFICATION = "ml_classification"
    METADATA_ANALYSIS = "metadata_analysis"
    BLOCKCHAIN_VERIFICATION = "blockchain_verification"


@dataclass
class ProtectionEvent:
    """Individual content protection event"""
    event_id: str
    content_id: int
    protection_type: ProtectionType
    detection_method: DetectionMethod
    threat_level: ThreatLevel
    timestamp: datetime
    confidence_score: float
    processing_time_ms: float
    match_details: Dict[str, Any] = field(default_factory=dict)
    action_taken: Optional[str] = None
    user_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtectionStats:
    """Protection system statistics"""
    total_scans: int
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float


class ContentProtectionTracker:
    """
    Advanced content protection tracking system
    
    Features:
    - Multi-modal content fingerprinting
    - Real-time threat detection
    - Copyright infringement tracking
    - Protection system performance metrics
    - False positive/negative analysis
    - Automated response tracking
    - Compliance monitoring
    """
    
    def __init__(self):
        """Initialize content protection tracker"""
        
        # Prometheus metrics
        self.protection_scans_total = Counter(
            'ainflue_protection_scans_total',
            'Total protection scans performed',
            ['type', 'method', 'result']
        )
        
        self.protection_accuracy = Gauge(
            'ainflue_protection_accuracy_percentage',
            'Protection system accuracy percentage',
            ['type', 'method']
        )
        
        self.threat_detection_rate = Gauge(
            'ainflue_threat_detection_rate',
            'Threat detection rate percentage',
            ['threat_level', 'type']
        )
        
        self.processing_time = Histogram(
            'ainflue_protection_processing_seconds',
            'Protection processing time',
            ['type', 'method'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, float('inf')]
        )
        
        self.false_positive_rate = Gauge(
            'ainflue_false_positive_rate_percentage',
            'False positive rate percentage',
            ['type', 'method']
        )
        
        self.content_matches_found = Counter(
            'ainflue_content_matches_total',
            'Total content matches found',
            ['match_type', 'confidence_level']
        )
        
        self.dmca_takedowns = Counter(
            'ainflue_dmca_takedowns_total',
            'DMCA takedown requests',
            ['status', 'reason']
        )
        
        # Data storage
        self.protection_events: List[ProtectionEvent] = []
        self.protection_stats: Dict[str, ProtectionStats] = {}
        self.content_fingerprints: Dict[int, Dict[str, Any]] = {}
        self.known_threats: Set[str] = set()
        self.whitelist: Set[str] = set()
        
        # Performance tracking
        self.system_performance: Dict[str, Any] = {
            "daily_scans": defaultdict(int),
            "accuracy_history": defaultdict(list),
            "threat_trends": defaultdict(list)
        }
        
        # Analytics cache
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_timestamp = datetime.utcnow()
        self.cache_ttl = timedelta(minutes=5)
        
        logger.info("ContentProtectionTracker initialized successfully")
    
    async def track_protection_scan(
        self,
        content_id: int,
        protection_type: ProtectionType,
        detection_method: DetectionMethod,
        result: str,  # "threat_detected", "clean", "inconclusive"
        confidence_score: float,
        processing_time_ms: float,
        threat_level: Optional[ThreatLevel] = None,
        match_details: Optional[Dict[str, Any]] = None,
        action_taken: Optional[str] = None,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track a content protection scan
        
        Args:
            content_id: Content identifier
            protection_type: Type of protection check
            detection_method: Method used for detection
            result: Scan result
            confidence_score: Confidence in result (0-100)
            processing_time_ms: Processing time in milliseconds
            threat_level: Severity of detected threat
            match_details: Details about any matches found
            action_taken: Action taken in response
            user_id: Associated user ID
            metadata: Additional metadata
        """
        try:
            # Generate event ID
            event_id = hashlib.md5(
                f"{content_id}_{protection_type.value}_{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]
            
            # Create protection event
            event = ProtectionEvent(
                event_id=event_id,
                content_id=content_id,
                protection_type=protection_type,
                detection_method=detection_method,
                threat_level=threat_level or ThreatLevel.LOW,
                timestamp=datetime.utcnow(),
                confidence_score=confidence_score,
                processing_time_ms=processing_time_ms,
                match_details=match_details or {},
                action_taken=action_taken,
                user_id=user_id,
                metadata=metadata or {}
            )
            
            # Store event
            self.protection_events.append(event)
            
            # Update Prometheus metrics
            self.protection_scans_total.labels(
                type=protection_type.value,
                method=detection_method.value,
                result=result
            ).inc()
            
            self.processing_time.labels(
                type=protection_type.value,
                method=detection_method.value
            ).observe(processing_time_ms / 1000.0)  # Convert to seconds
            
            # Track content matches
            if result == "threat_detected" and threat_level:
                confidence_level = self._get_confidence_level(confidence_score)
                
                self.content_matches_found.labels(
                    match_type=protection_type.value,
                    confidence_level=confidence_level
                ).inc()
                
                self.threat_detection_rate.labels(
                    threat_level=threat_level.value,
                    type=protection_type.value
                ).inc()
            
            # Update daily scan counter
            today = datetime.utcnow().strftime("%Y-%m-%d")
            self.system_performance["daily_scans"][today] += 1
            
            # Update protection statistics
            await self._update_protection_stats(protection_type, detection_method)
            
            # Clear cache
            self.analytics_cache.clear()
            
            logger.debug(f"Protection scan tracked: {content_id} - {result}")
            
        except Exception as e:
            logger.error(f"Error tracking protection scan: {e}")
    
    async def track_dmca_takedown(
        self,
        content_id: int,
        request_id: str,
        status: str,  # "submitted", "approved", "rejected", "resolved"
        reason: str,
        requester_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track DMCA takedown request"""
        try:
            # Update DMCA metrics
            self.dmca_takedowns.labels(
                status=status,
                reason=reason
            ).inc()
            
            # Store DMCA event
            dmca_event = {
                "content_id": content_id,
                "request_id": request_id,
                "status": status,
                "reason": reason,
                "timestamp": datetime.utcnow(),
                "requester_info": requester_info or {},
                "metadata": metadata or {}
            }
            
            # Store in metadata for analysis
            if not hasattr(self, 'dmca_events'):
                self.dmca_events = []
            self.dmca_events.append(dmca_event)
            
            logger.debug(f"DMCA takedown tracked: {request_id} - {status}")
            
        except Exception as e:
            logger.error(f"Error tracking DMCA takedown: {e}")
    
    async def track_fingerprint_generation(
        self,
        content_id: int,
        fingerprint_type: str,  # "visual", "audio", "metadata"
        fingerprint_data: Dict[str, Any],
        generation_time_ms: float,
        quality_score: float
    ) -> None:
        """Track fingerprint generation"""
        try:
            fingerprint_info = {
                "type": fingerprint_type,
                "data": fingerprint_data,
                "generated_at": datetime.utcnow(),
                "generation_time_ms": generation_time_ms,
                "quality_score": quality_score,
                "version": "1.0"  # Fingerprint algorithm version
            }
            
            if content_id not in self.content_fingerprints:
                self.content_fingerprints[content_id] = {}
            
            self.content_fingerprints[content_id][fingerprint_type] = fingerprint_info
            
            logger.debug(f"Fingerprint generated for content {content_id}: {fingerprint_type}")
            
        except Exception as e:
            logger.error(f"Error tracking fingerprint generation: {e}")
    
    async def get_protection_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive protection analytics
        
        Args:
            period_days: Analysis period in days
            
        Returns:
            Protection analytics data
        """
        try:
            # Check cache
            cache_key = f"protection_analytics_{period_days}"
            if (cache_key in self.analytics_cache and 
                datetime.utcnow() - self.cache_timestamp < self.cache_ttl):
                return self.analytics_cache[cache_key]
            
            # Calculate analytics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=period_days)
            
            period_events = [
                event for event in self.protection_events
                if start_time <= event.timestamp <= end_time
            ]
            
            analytics = {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": period_days
                },
                "summary": await self._calculate_protection_summary(period_events),
                "accuracy_metrics": await self._calculate_accuracy_metrics(period_events),
                "threat_analysis": await self._calculate_threat_analysis(period_events),
                "performance_metrics": await self._calculate_performance_metrics(period_events),
                "detection_methods": await self._analyze_detection_methods(period_events),
                "compliance_status": await self._calculate_compliance_metrics(),
                "trends": await self._calculate_protection_trends(period_days),
                "recommendations": await self._generate_protection_recommendations(period_events)
            }
            
            # Cache results
            self.analytics_cache[cache_key] = analytics
            self.cache_timestamp = datetime.utcnow()
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting protection analytics: {e}")
            return {"error": str(e)}
    
    async def _calculate_protection_summary(self, events: List[ProtectionEvent]) -> Dict[str, Any]:
        """Calculate protection system summary"""
        if not events:
            return {
                "total_scans": 0,
                "threats_detected": 0,
                "clean_content": 0,
                "average_confidence": 0,
                "average_processing_time": 0
            }
        
        threats_detected = len([e for e in events if e.threat_level != ThreatLevel.LOW])
        clean_content = len(events) - threats_detected
        
        avg_confidence = statistics.mean([e.confidence_score for e in events])
        avg_processing_time = statistics.mean([e.processing_time_ms for e in events])
        
        return {
            "total_scans": len(events),
            "threats_detected": threats_detected,
            "clean_content": clean_content,
            "threat_rate_percentage": round((threats_detected / len(events)) * 100, 2),
            "average_confidence": round(avg_confidence, 2),
            "average_processing_time_ms": round(avg_processing_time, 2),
            "protection_types": dict(Counter(e.protection_type.value for e in events)),
            "detection_methods": dict(Counter(e.detection_method.value for e in events))
        }
    
    async def _calculate_accuracy_metrics(self, events: List[ProtectionEvent]) -> Dict[str, Any]:
        """Calculate protection accuracy metrics"""
        # This would require ground truth data for accurate calculation
        # For now, we'll use confidence scores as a proxy
        
        high_confidence_events = [e for e in events if e.confidence_score >= 90]
        medium_confidence_events = [e for e in events if 70 <= e.confidence_score < 90]
        low_confidence_events = [e for e in events if e.confidence_score < 70]
        
        # Group by protection type and method
        accuracy_by_type = defaultdict(list)
        accuracy_by_method = defaultdict(list)
        
        for event in events:
            accuracy_by_type[event.protection_type.value].append(event.confidence_score)
            accuracy_by_method[event.detection_method.value].append(event.confidence_score)
        
        # Update Prometheus metrics
        for ptype, scores in accuracy_by_type.items():
            avg_accuracy = statistics.mean(scores)
            for method, method_scores in accuracy_by_method.items():
                method_avg = statistics.mean(method_scores)
                self.protection_accuracy.labels(
                    type=ptype,
                    method=method
                ).set(method_avg)
        
        return {
            "overall_confidence": {
                "high_confidence": len(high_confidence_events),
                "medium_confidence": len(medium_confidence_events),
                "low_confidence": len(low_confidence_events)
            },
            "accuracy_by_type": {
                ptype: round(statistics.mean(scores), 2)
                for ptype, scores in accuracy_by_type.items()
            },
            "accuracy_by_method": {
                method: round(statistics.mean(scores), 2)
                for method, scores in accuracy_by_method.items()
            }
        }
    
    async def _calculate_threat_analysis(self, events: List[ProtectionEvent]) -> Dict[str, Any]:
        """Calculate threat analysis metrics"""
        threat_events = [e for e in events if e.threat_level != ThreatLevel.LOW]
        
        if not threat_events:
            return {
                "total_threats": 0,
                "threat_distribution": {},
                "top_threat_types": [],
                "threat_trends": {}
            }
        
        threat_distribution = Counter(e.threat_level.value for e in threat_events)
        threat_types = Counter(e.protection_type.value for e in threat_events)
        
        # Calculate threat trends (daily)
        daily_threats = defaultdict(int)
        for event in threat_events:
            day = event.timestamp.strftime("%Y-%m-%d")
            daily_threats[day] += 1
        
        return {
            "total_threats": len(threat_events),
            "threat_distribution": dict(threat_distribution),
            "threat_rate_percentage": round((len(threat_events) / len(events)) * 100, 2),
            "top_threat_types": [
                {"type": ptype, "count": count}
                for ptype, count in threat_types.most_common(5)
            ],
            "daily_threat_trend": dict(sorted(daily_threats.items())[-7:])  # Last 7 days
        }
    
    async def _calculate_performance_metrics(self, events: List[ProtectionEvent]) -> Dict[str, Any]:
        """Calculate system performance metrics"""
        if not events:
            return {"average_processing_time": 0, "throughput": 0, "performance_by_method": {}}
        
        # Processing time analysis
        processing_times = [e.processing_time_ms for e in events]
        
        # Group by detection method for performance comparison
        performance_by_method = defaultdict(list)
        for event in events:
            performance_by_method[event.detection_method.value].append(event.processing_time_ms)
        
        # Calculate throughput (scans per hour)
        time_span_hours = (max(e.timestamp for e in events) - min(e.timestamp for e in events)).total_seconds() / 3600
        throughput = len(events) / max(time_span_hours, 1)
        
        return {
            "average_processing_time_ms": round(statistics.mean(processing_times), 2),
            "median_processing_time_ms": round(statistics.median(processing_times), 2),
            "processing_time_p95": round(statistics.quantiles(processing_times, n=20)[18], 2) if len(processing_times) >= 20 else max(processing_times),
            "throughput_per_hour": round(throughput, 2),
            "performance_by_method": {
                method: {
                    "average_ms": round(statistics.mean(times), 2),
                    "median_ms": round(statistics.median(times), 2),
                    "count": len(times)
                }
                for method, times in performance_by_method.items()
            }
        }
    
    async def _analyze_detection_methods(self, events: List[ProtectionEvent]) -> Dict[str, Any]:
        """Analyze effectiveness of different detection methods"""
        method_analysis = defaultdict(lambda: {
            "total_scans": 0,
            "threats_detected": 0,
            "average_confidence": [],
            "average_processing_time": []
        })
        
        for event in events:
            method = event.detection_method.value
            analysis = method_analysis[method]
            
            analysis["total_scans"] += 1
            analysis["average_confidence"].append(event.confidence_score)
            analysis["average_processing_time"].append(event.processing_time_ms)
            
            if event.threat_level != ThreatLevel.LOW:
                analysis["threats_detected"] += 1
        
        # Calculate final metrics
        method_effectiveness = {}
        for method, data in method_analysis.items():
            if data["total_scans"] > 0:
                threat_detection_rate = (data["threats_detected"] / data["total_scans"]) * 100
                avg_confidence = statistics.mean(data["average_confidence"])
                avg_processing_time = statistics.mean(data["average_processing_time"])
                
                # Calculate effectiveness score (weighted combination)
                effectiveness_score = (
                    avg_confidence * 0.4 +  # 40% confidence
                    min(threat_detection_rate * 2, 100) * 0.3 +  # 30% detection rate
                    max(0, 100 - (avg_processing_time / 100)) * 0.3  # 30% speed (inverse of processing time)
                )
                
                method_effectiveness[method] = {
                    "total_scans": data["total_scans"],
                    "threats_detected": data["threats_detected"],
                    "threat_detection_rate": round(threat_detection_rate, 2),
                    "average_confidence": round(avg_confidence, 2),
                    "average_processing_time_ms": round(avg_processing_time, 2),
                    "effectiveness_score": round(effectiveness_score, 2)
                }
        
        return method_effectiveness
    
    async def _calculate_compliance_metrics(self) -> Dict[str, Any]:
        """Calculate compliance metrics"""
        dmca_events = getattr(self, 'dmca_events', [])
        
        if not dmca_events:
            return {
                "dmca_requests": 0,
                "dmca_compliance_rate": 100,
                "average_response_time": 0
            }
        
        total_requests = len(dmca_events)
        resolved_requests = len([e for e in dmca_events if e["status"] == "resolved"])
        
        return {
            "dmca_requests": total_requests,
            "dmca_compliance_rate": round((resolved_requests / total_requests) * 100, 2) if total_requests > 0 else 100,
            "average_response_time_hours": 24,  # Placeholder - would calculate from actual data
            "compliance_status": "compliant" if resolved_requests / max(total_requests, 1) >= 0.95 else "needs_attention"
        }
    
    async def _calculate_protection_trends(self, period_days: int) -> Dict[str, Any]:
        """Calculate protection trends"""
        # Simplified trend calculation
        return {
            "threat_trend": "stable",  # Would be calculated from historical data
            "accuracy_trend": "improving",
            "performance_trend": "stable"
        }
    
    async def _generate_protection_recommendations(self, events: List[ProtectionEvent]) -> List[str]:
        """Generate protection system recommendations"""
        recommendations = []
        
        if not events:
            recommendations.append("Increase content scanning frequency to build baseline metrics")
            return recommendations
        
        # Analyze processing times
        avg_processing_time = statistics.mean([e.processing_time_ms for e in events])
        if avg_processing_time > 5000:  # 5 seconds
            recommendations.append("Consider optimizing detection algorithms to reduce processing time")
        
        # Analyze confidence scores
        low_confidence_events = [e for e in events if e.confidence_score < 70]
        if len(low_confidence_events) / len(events) > 0.2:  # More than 20% low confidence
            recommendations.append("Review and improve detection model training to increase confidence scores")
        
        # Analyze threat detection
        threats = [e for e in events if e.threat_level != ThreatLevel.LOW]
        if len(threats) / len(events) > 0.1:  # More than 10% threats
            recommendations.append("Consider implementing additional content filtering measures")
        
        return recommendations
    
    async def _update_protection_stats(
        self,
        protection_type: ProtectionType,
        detection_method: DetectionMethod
    ) -> None:
        """Update protection statistics for accuracy tracking"""
        try:
            key = f"{protection_type.value}_{detection_method.value}"
            
            # This would be more sophisticated with ground truth data
            # For now, we'll use confidence scores as a proxy for accuracy
            
            relevant_events = [
                e for e in self.protection_events
                if e.protection_type == protection_type and e.detection_method == detection_method
            ]
            
            if len(relevant_events) >= 10:  # Need minimum events for meaningful stats
                high_confidence = len([e for e in relevant_events if e.confidence_score >= 90])
                total = len(relevant_events)
                
                estimated_accuracy = (high_confidence / total) * 100
                
                # Update Prometheus metric
                self.protection_accuracy.labels(
                    type=protection_type.value,
                    method=detection_method.value
                ).set(estimated_accuracy)
            
        except Exception as e:
            logger.error(f"Error updating protection stats: {e}")
    
    def _get_confidence_level(self, confidence_score: float) -> str:
        """Convert confidence score to level"""
        if confidence_score >= 90:
            return "high"
        elif confidence_score >= 70:
            return "medium"
        else:
            return "low"
    
    def get_tracker_stats(self) -> Dict[str, Any]:
        """Get protection tracker statistics"""
        return {
            "total_events": len(self.protection_events),
            "unique_content_scanned": len(set(e.content_id for e in self.protection_events)),
            "fingerprints_stored": len(self.content_fingerprints),
            "known_threats": len(self.known_threats),
            "whitelist_entries": len(self.whitelist),
            "cache_entries": len(self.analytics_cache),
            "dmca_events": len(getattr(self, 'dmca_events', [])),
            "protection_types_active": len(set(e.protection_type.value for e in self.protection_events))
        }


# Export classes
__all__ = [
    "ContentProtectionTracker",
    "ProtectionEvent",
    "ProtectionStats",
    "ProtectionType",
    "ThreatLevel", 
    "DetectionMethod"
]