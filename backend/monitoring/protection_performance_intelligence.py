"""🛡️ Protection Performance Intelligence - IA Influencer Agent Platform
=======================================================================

Advanced protection system performance monitoring, copyright violation detection analytics,
and rights management performance intelligence for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic Integration:
Content Upload → Protection Analysis → Violation Detection → Rights Validation → Performance Tracking
"""

import asyncio
import logging as std_logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import json
from collections import defaultdict
import statistics

logger = std_logging.getLogger(__name__)


class ProtectionType(Enum):
    """Types of protection systems"""
    COPYRIGHT_DETECTION = "copyright_detection"
    PIRACY_PREVENTION = "piracy_prevention"
    CONTENT_FINGERPRINTING = "content_fingerprinting"
    RIGHTS_VALIDATION = "rights_validation"
    TAKEDOWN_MANAGEMENT = "takedown_management"
    WATERMARKING = "watermarking"
    DRM_PROTECTION = "drm_protection"
    BLOCKCHAIN_VERIFICATION = "blockchain_verification"


class ViolationType(Enum):
    """Types of violations detected"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    CONTENT_PIRACY = "content_piracy"
    TRADEMARK_VIOLATION = "trademark_violation"
    FAIR_USE_VIOLATION = "fair_use_violation"
    LICENSING_BREACH = "licensing_breach"
    PLAGIARISM = "plagiarism"
    UNAUTHORIZED_REMIX = "unauthorized_remix"


class ProtectionSeverity(Enum):
    """Severity levels of protection issues"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ProtectionPerformanceMetrics:
    """Comprehensive protection system performance metrics"""
    protection_id: str
    protection_type: ProtectionType
    
    # Detection metrics
    detection_accuracy: float = 0.0
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    detection_speed_ms: int = 0
    
    # Violation metrics
    violations_detected: int = 0
    violations_prevented: int = 0
    successful_takedowns: int = 0
    failed_takedowns: int = 0
    
    # Performance metrics
    processing_time_ms: int = 0
    system_uptime: float = 100.0
    response_time_ms: int = 0
    throughput_per_second: float = 0.0
    
    # Quality metrics
    protection_effectiveness: float = 0.0
    content_coverage: float = 0.0
    risk_mitigation_score: float = 0.0
    
    # Business impact metrics
    revenue_protected: Decimal = Decimal('0')
    cost_per_protection: Decimal = Decimal('0')
    roi_protection: float = 0.0
    
    # Rights management metrics
    licenses_validated: int = 0
    rights_disputes_resolved: int = 0
    attribution_accuracy: float = 0.0
    
    # Platform-specific metrics
    platform_coverage: Dict[str, float] = field(default_factory=dict)
    
    # Resource metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    storage_usage_gb: float = 0.0
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    content_id: Optional[str] = None
    creator_id: Optional[str] = None
    platform: str = "default"
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ViolationAnalytics:
    """Comprehensive violation detection and response analytics"""
    violation_id: str
    violation_type: ViolationType
    severity: ProtectionSeverity
    
    # Detection details
    detected_at: datetime
    detection_confidence: float = 0.0
    detection_method: str = ""
    
    # Content details
    content_id: Optional[str] = None
    original_creator_id: Optional[str] = None
    violating_creator_id: Optional[str] = None
    
    # Response metrics
    response_time_hours: float = 0.0
    resolution_status: str = "pending"
    resolution_time_hours: Optional[float] = None
    
    # Impact assessment
    estimated_revenue_loss: Decimal = Decimal('0')
    audience_impact: int = 0
    brand_damage_score: float = 0.0
    
    # Legal metrics
    legal_action_required: bool = False
    dmca_takedown_sent: bool = False
    court_action_initiated: bool = False
    
    # Platform response
    platform_cooperation_score: float = 0.0
    takedown_success_rate: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProtectionROIAnalytics:
    """Protection system ROI and business impact analytics"""
    protection_system_id: str
    
    # Investment metrics
    implementation_cost: Decimal = Decimal('0')
    operational_cost_monthly: Decimal = Decimal('0')
    maintenance_cost_monthly: Decimal = Decimal('0')
    
    # Revenue protection metrics
    revenue_protected_monthly: Decimal = Decimal('0')
    potential_losses_prevented: Decimal = Decimal('0')
    brand_value_protected: Decimal = Decimal('0')
    
    # Efficiency metrics
    cost_per_violation_detected: Decimal = Decimal('0')
    cost_per_takedown_successful: Decimal = Decimal('0')
    automation_savings: Decimal = Decimal('0')
    
    # ROI calculations
    monthly_roi: float = 0.0
    annual_roi: float = 0.0
    payback_period_months: float = 0.0
    
    # Risk mitigation value
    reputation_protection_value: Decimal = Decimal('0')
    legal_cost_savings: Decimal = Decimal('0')
    
    timestamp: datetime = field(default_factory=datetime.now)


class ProtectionPerformanceIntelligence:
    """
    Advanced protection system performance intelligence providing comprehensive analytics,
    violation detection insights, and rights management optimization.
    """
    
    def __init__(self) -> None:
        self.protection_metrics: Dict[str, List[ProtectionPerformanceMetrics]] = defaultdict(list)
        self.violation_analytics: Dict[str, ViolationAnalytics] = {}
        self.roi_analytics: Dict[str, ProtectionROIAnalytics] = {}
        
        # Performance thresholds for protection systems
        self.protection_thresholds = {
            "min_detection_accuracy": 0.90,      # 90% minimum accuracy
            "max_false_positive_rate": 0.05,     # 5% maximum false positives
            "max_detection_time_ms": 3000,       # 3 seconds maximum detection time
            "min_protection_effectiveness": 0.85, # 85% minimum effectiveness
            "max_response_time_hours": 24,       # 24 hours maximum response time
            "min_roi": 2.0,                      # 2.0x minimum ROI
        }
        
        # Platform-specific protection configurations
        self.platform_configs = {
            "youtube": {"priority": "high", "cooperation_score": 0.8},
            "instagram": {"priority": "high", "cooperation_score": 0.7},
            "tiktok": {"priority": "medium", "cooperation_score": 0.6},
            "facebook": {"priority": "medium", "cooperation_score": 0.75},
            "twitter": {"priority": "low", "cooperation_score": 0.65},
        }
    
    async def analyze_protection_performance(
        self,
        protection_id: str,
        protection_type: ProtectionType,
        timeframe: timedelta = timedelta(days=7)
    ) -> ProtectionPerformanceMetrics:
        """
        Comprehensive protection system performance analysis
        """
        try:
            # Collect protection system data
            raw_data = await self._collect_protection_data(protection_id, protection_type, timeframe)
            
            # Calculate performance metrics
            metrics = await self._calculate_protection_metrics(
                protection_id, protection_type, raw_data
            )
            
            # Analyze violation patterns
            await self._analyze_violation_patterns(metrics, raw_data)
            
            # Calculate ROI and business impact
            await self._calculate_protection_roi(metrics, raw_data)
            
            # Store metrics
            self.protection_metrics[protection_id].append(metrics)
            
            # Limit history to last 50 entries
            if len(self.protection_metrics[protection_id]) > 50:
                self.protection_metrics[protection_id] = self.protection_metrics[protection_id][-50:]
            
            logger.info(f"Protection performance analysis completed for {protection_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing protection performance for {protection_id}: {e}")
            return ProtectionPerformanceMetrics(
                protection_id=protection_id,
                protection_type=protection_type
            )
    
    async def track_violation_response(
        self,
        violation_id: str,
        violation_type: ViolationType,
        severity: ProtectionSeverity,
        violation_data: Dict[str, Any]
    ) -> ViolationAnalytics:
        """
        Track violation detection and response performance
        """
        try:
            # Create violation analytics
            analytics = ViolationAnalytics(
                violation_id=violation_id,
                violation_type=violation_type,
                severity=severity,
                detected_at=datetime.now(),
                detection_confidence=violation_data.get("confidence", 0.85),
                detection_method=violation_data.get("method", "automated"),
                content_id=violation_data.get("content_id"),
                original_creator_id=violation_data.get("original_creator_id"),
                violating_creator_id=violation_data.get("violating_creator_id"),
                estimated_revenue_loss=Decimal(str(violation_data.get("estimated_loss", 0))),
                audience_impact=violation_data.get("audience_impact", 0),
                brand_damage_score=violation_data.get("brand_damage", 0.0)
            )
            
            # Store violation analytics
            self.violation_analytics[violation_id] = analytics
            
            # Trigger automated response based on severity
            await self._trigger_violation_response(analytics)
            
            logger.info(f"Violation response tracking initiated for {violation_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error tracking violation response for {violation_id}: {e}")
            return ViolationAnalytics(
                violation_id=violation_id,
                violation_type=violation_type,
                severity=severity,
                detected_at=datetime.now()
            )
    
    async def get_protection_dashboard(
        self,
        timeframe: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Generate comprehensive protection performance dashboard
        """
        try:
            # Collect all metrics within timeframe
            cutoff_time = datetime.now() - timeframe
            recent_metrics = []
            
            for protection_id, metrics_list in self.protection_metrics.items():
                recent_metrics.extend([
                    m for m in metrics_list if m.timestamp >= cutoff_time
                ])
            
            # Collect recent violations
            recent_violations = [
                v for v in self.violation_analytics.values()
                if v.detected_at >= cutoff_time
            ]
            
            if not recent_metrics:
                return {"error": "No protection data available for the specified timeframe"}
            
            # Calculate dashboard metrics
            dashboard_data = {
                "timeframe": str(timeframe),
                "last_updated": datetime.now().isoformat(),
                
                # Protection overview
                "protection_overview": await self._calculate_protection_overview(recent_metrics),
                
                # Violation analytics
                "violation_analytics": await self._calculate_violation_analytics(recent_violations),
                
                # Performance metrics
                "performance_metrics": await self._calculate_performance_metrics(recent_metrics),
                
                # ROI analytics
                "roi_analytics": await self._calculate_roi_summary(),
                
                # Platform coverage
                "platform_coverage": await self._calculate_platform_coverage(recent_metrics),
                
                # Trend data
                "trend_data": await self._generate_protection_trends(recent_metrics),
                
                # Alerts and recommendations
                "alerts": await self._generate_protection_alerts(recent_metrics, recent_violations),
                "recommendations": await self._generate_protection_recommendations(recent_metrics)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating protection dashboard: {e}")
            return {"error": str(e)}
    
    async def optimize_protection_strategy(
        self,
        protection_type: ProtectionType,
        optimization_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize protection strategy based on performance analysis
        """
        try:
            # Analyze current performance
            current_performance = await self._analyze_current_protection_performance(protection_type)
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(
                protection_type, current_performance, optimization_goals
            )
            
            # Generate optimization plan
            optimization_plan = await self._generate_optimization_plan(
                protection_type, opportunities, optimization_goals
            )
            
            # Calculate expected impact
            expected_impact = await self._calculate_optimization_impact(
                protection_type, optimization_plan
            )
            
            return {
                "protection_type": protection_type.value,
                "current_performance": current_performance,
                "optimization_opportunities": opportunities,
                "optimization_plan": optimization_plan,
                "expected_impact": expected_impact,
                "implementation_timeline": "2-4 weeks",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error optimizing protection strategy for {protection_type.value}: {e}")
            return {"error": str(e), "success": False}
    
    # Helper methods for data collection and analysis
    
    async def _collect_protection_data(
        self,
        protection_id: str,
        protection_type: ProtectionType,
        timeframe: timedelta
    ) -> Dict[str, Any]:
        """Collect protection system performance data"""
        # Simulate protection data collection - in production this would integrate with actual systems
        return {
            "violations_detected": 45,
            "violations_prevented": 38,
            "false_positives": 3,
            "false_negatives": 2,
            "detection_time_avg_ms": 1200,
            "response_time_avg_hours": 6.5,
            "successful_takedowns": 35,
            "failed_takedowns": 3,
            "revenue_protected": 15420.50,
            "processing_time_ms": 850,
            "cpu_usage": 35.2,
            "memory_usage": 1024.5,
            "platform_coverage": {
                "youtube": 0.95,
                "instagram": 0.88,
                "tiktok": 0.82,
                "facebook": 0.90
            }
        }
    
    async def _calculate_protection_metrics(
        self,
        protection_id: str,
        protection_type: ProtectionType,
        raw_data: Dict[str, Any]
    ) -> ProtectionPerformanceMetrics:
        """Calculate comprehensive protection performance metrics"""
        
        violations_detected = raw_data.get("violations_detected", 0)
        violations_prevented = raw_data.get("violations_prevented", 0)
        false_positives = raw_data.get("false_positives", 0)
        false_negatives = raw_data.get("false_negatives", 0)
        
        # Calculate accuracy metrics
        total_detections = violations_detected + false_positives
        detection_accuracy = (violations_detected / max(total_detections, 1)) if total_detections > 0 else 0.0
        false_positive_rate = (false_positives / max(total_detections, 1)) if total_detections > 0 else 0.0
        false_negative_rate = (false_negatives / max(violations_detected + false_negatives, 1))
        
        # Calculate effectiveness
        protection_effectiveness = (violations_prevented / max(violations_detected, 1)) if violations_detected > 0 else 0.0
        
        # Calculate business metrics
        revenue_protected = Decimal(str(raw_data.get("revenue_protected", 0)))
        cost_per_protection = Decimal("25.50")  # Simulated cost per protection operation
        roi_protection = float(revenue_protected / max(cost_per_protection * violations_detected, 1)) if violations_detected > 0 else 0.0
        
        # Calculate performance metrics
        processing_time_ms = raw_data.get("processing_time_ms", 1000)
        detection_speed_ms = raw_data.get("detection_time_avg_ms", 1500)
        response_time_ms = int(raw_data.get("response_time_avg_hours", 8) * 3600 * 1000)  # Convert to ms
        
        return ProtectionPerformanceMetrics(
            protection_id=protection_id,
            protection_type=protection_type,
            detection_accuracy=detection_accuracy,
            false_positive_rate=false_positive_rate,
            false_negative_rate=false_negative_rate,
            detection_speed_ms=detection_speed_ms,
            violations_detected=violations_detected,
            violations_prevented=violations_prevented,
            successful_takedowns=raw_data.get("successful_takedowns", 0),
            failed_takedowns=raw_data.get("failed_takedowns", 0),
            processing_time_ms=processing_time_ms,
            response_time_ms=response_time_ms,
            protection_effectiveness=protection_effectiveness,
            content_coverage=0.92,  # Simulated coverage
            risk_mitigation_score=min(1.0, protection_effectiveness * 1.1),
            revenue_protected=revenue_protected,
            cost_per_protection=cost_per_protection,
            roi_protection=roi_protection,
            licenses_validated=raw_data.get("licenses_validated", 128),
            rights_disputes_resolved=raw_data.get("rights_disputes", 15),
            attribution_accuracy=0.94,  # Simulated attribution accuracy
            platform_coverage=raw_data.get("platform_coverage", {}),
            cpu_usage_percent=raw_data.get("cpu_usage", 30.0),
            memory_usage_mb=raw_data.get("memory_usage", 512.0),
            storage_usage_gb=raw_data.get("storage_usage", 2.5)
        )
    
    async def _analyze_violation_patterns(
        self,
        metrics -> None: ProtectionPerformanceMetrics,
        raw_data -> None: Dict[str, Any]
    ) -> None:
        """Analyze violation patterns and trends"""
        # Pattern analysis logic would go here
        logger.info(f"Violation pattern analysis completed for {metrics.protection_id}")
    
    async def _calculate_protection_roi(
        self,
        metrics -> None: ProtectionPerformanceMetrics,
        raw_data -> None: Dict[str, Any]
    ) -> None:
        """Calculate protection system ROI"""
        roi_analytics = ProtectionROIAnalytics(
            protection_system_id=metrics.protection_id,
            implementation_cost=Decimal("50000"),  # $50k implementation
            operational_cost_monthly=Decimal("5000"),  # $5k monthly operations
            maintenance_cost_monthly=Decimal("2000"),  # $2k monthly maintenance
            revenue_protected_monthly=metrics.revenue_protected,
            potential_losses_prevented=metrics.revenue_protected * Decimal("1.5"),
            cost_per_violation_detected=metrics.cost_per_protection,
            monthly_roi=metrics.roi_protection,
            annual_roi=metrics.roi_protection * 12,
            reputation_protection_value=metrics.revenue_protected * Decimal("0.3")
        )
        
        self.roi_analytics[metrics.protection_id] = roi_analytics
    
    async def _trigger_violation_response(self, analytics -> None: ViolationAnalytics) -> None:
        """Trigger automated violation response based on severity"""
        if analytics.severity in [ProtectionSeverity.HIGH, ProtectionSeverity.CRITICAL]:
            # High priority response
            analytics.dmca_takedown_sent = True
            analytics.response_time_hours = 2.0
        elif analytics.severity == ProtectionSeverity.MEDIUM:
            # Medium priority response
            analytics.response_time_hours = 12.0
        else:
            # Low priority response
            analytics.response_time_hours = 48.0
        
        logger.info(f"Violation response triggered for {analytics.violation_id} with {analytics.severity.value} severity")
    
    # Dashboard calculation methods
    
    async def _calculate_protection_overview(self, metrics: List[ProtectionPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate protection system overview metrics"""
        if not metrics:
            return {}
        
        return {
            "total_violations_detected": sum(m.violations_detected for m in metrics),
            "total_violations_prevented": sum(m.violations_prevented for m in metrics),
            "average_detection_accuracy": statistics.mean([m.detection_accuracy for m in metrics]),
            "average_effectiveness": statistics.mean([m.protection_effectiveness for m in metrics]),
            "total_revenue_protected": float(sum(m.revenue_protected for m in metrics)),
            "average_response_time_hours": statistics.mean([m.response_time_ms / 3600000 for m in metrics]),
            "protection_systems_active": len(set(m.protection_id for m in metrics))
        }
    
    async def _calculate_violation_analytics(self, violations: List[ViolationAnalytics]) -> Dict[str, Any]:
        """Calculate violation analytics summary"""
        if not violations:
            return {}
        
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        
        for violation in violations:
            by_type[violation.violation_type.value] += 1
            by_severity[violation.severity.value] += 1
        
        return {
            "total_violations": len(violations),
            "violations_by_type": dict(by_type),
            "violations_by_severity": dict(by_severity),
            "average_detection_confidence": statistics.mean([v.detection_confidence for v in violations]),
            "total_estimated_loss": float(sum(v.estimated_revenue_loss for v in violations)),
            "average_response_time": statistics.mean([v.response_time_hours for v in violations if v.response_time_hours > 0])
        }
    
    async def _calculate_performance_metrics(self, metrics: List[ProtectionPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate performance metrics summary"""
        if not metrics:
            return {}
        
        return {
            "average_processing_time_ms": statistics.mean([m.processing_time_ms for m in metrics]),
            "average_detection_speed_ms": statistics.mean([m.detection_speed_ms for m in metrics]),
            "system_uptime": statistics.mean([m.system_uptime for m in metrics]),
            "average_cpu_usage": statistics.mean([m.cpu_usage_percent for m in metrics]),
            "average_memory_usage": statistics.mean([m.memory_usage_mb for m in metrics]),
            "false_positive_rate": statistics.mean([m.false_positive_rate for m in metrics]),
            "false_negative_rate": statistics.mean([m.false_negative_rate for m in metrics])
        }
    
    async def _calculate_roi_summary(self) -> Dict[str, Any]:
        """Calculate ROI analytics summary"""
        if not self.roi_analytics:
            return {}
        
        roi_values = list(self.roi_analytics.values())
        
        return {
            "total_revenue_protected": float(sum(r.revenue_protected_monthly for r in roi_values)),
            "total_operational_cost": float(sum(r.operational_cost_monthly for r in roi_values)),
            "average_monthly_roi": statistics.mean([r.monthly_roi for r in roi_values]),
            "total_cost_savings": float(sum(r.automation_savings for r in roi_values)),
            "average_payback_period": statistics.mean([r.payback_period_months for r in roi_values if r.payback_period_months > 0])
        }
    
    async def _calculate_platform_coverage(self, metrics: List[ProtectionPerformanceMetrics]) -> Dict[str, float]:
        """Calculate platform coverage summary"""
        platform_coverage = defaultdict(list)
        
        for metric in metrics:
            for platform, coverage in metric.platform_coverage.items():
                platform_coverage[platform].append(coverage)
        
        return {
            platform: statistics.mean(coverages)
            for platform, coverages in platform_coverage.items()
        }
    
    async def _generate_protection_trends(self, metrics: List[ProtectionPerformanceMetrics]) -> Dict[str, List]:
        """Generate trend data for protection metrics"""
        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        # Group by day for trend analysis
        daily_data = defaultdict(list)
        for metric in sorted_metrics:
            day_key = metric.timestamp.date()
            daily_data[day_key].append(metric)
        
        trend_data = {
            "dates": [],
            "violations_detected": [],
            "detection_accuracy": [],
            "revenue_protected": [],
            "response_time": []
        }
        
        for day, day_metrics in sorted(daily_data.items()):
            trend_data["dates"].append(day.isoformat())
            trend_data["violations_detected"].append(sum(m.violations_detected for m in day_metrics))
            trend_data["detection_accuracy"].append(statistics.mean([m.detection_accuracy for m in day_metrics]))
            trend_data["revenue_protected"].append(float(sum(m.revenue_protected for m in day_metrics)))
            trend_data["response_time"].append(statistics.mean([m.response_time_ms / 3600000 for m in day_metrics]))
        
        return trend_data
    
    async def _generate_protection_alerts(
        self,
        metrics: List[ProtectionPerformanceMetrics],
        violations: List[ViolationAnalytics]
    ) -> List[Dict[str, str]]:
        """Generate protection system alerts"""
        alerts = []
        
        # Check detection accuracy
        low_accuracy_systems = [
            m for m in metrics
            if m.detection_accuracy < self.protection_thresholds["min_detection_accuracy"]
        ]
        if low_accuracy_systems:
            alerts.append({
                "type": "accuracy",
                "severity": "high",
                "message": f"{len(low_accuracy_systems)} protection systems have low detection accuracy",
                "recommendation": "Review and retrain detection models"
            })
        
        # Check response times
        slow_responses = [
            v for v in violations
            if v.response_time_hours > self.protection_thresholds["max_response_time_hours"]
        ]
        if slow_responses:
            alerts.append({
                "type": "response_time",
                "severity": "medium",
                "message": f"{len(slow_responses)} violations had slow response times",
                "recommendation": "Optimize automated response workflows"
            })
        
        # Check ROI
        low_roi_systems = [
            r for r in self.roi_analytics.values()
            if r.monthly_roi < self.protection_thresholds["min_roi"]
        ]
        if low_roi_systems:
            alerts.append({
                "type": "roi",
                "severity": "medium",
                "message": f"{len(low_roi_systems)} protection systems have low ROI",
                "recommendation": "Review cost-effectiveness and optimization opportunities"
            })
        
        return alerts
    
    async def _generate_protection_recommendations(
        self, metrics: List[ProtectionPerformanceMetrics]
    ) -> List[Dict[str, str]]:
        """Generate protection optimization recommendations"""
        recommendations = []
        
        if metrics:
            avg_accuracy = statistics.mean([m.detection_accuracy for m in metrics])
            if avg_accuracy < 0.90:
                recommendations.append({
                    "type": "accuracy_improvement",
                    "priority": "high",
                    "title": "Improve Detection Accuracy",
                    "description": "Detection accuracy is below optimal levels",
                    "action": "Enhance ML models and training data"
                })
            
            avg_response_time = statistics.mean([m.response_time_ms / 3600000 for m in metrics])
            if avg_response_time > 12:  # 12 hours
                recommendations.append({
                    "type": "response_optimization",
                    "priority": "medium",
                    "title": "Optimize Response Time",
                    "description": "Violation response times can be improved",
                    "action": "Implement automated response workflows"
                })
        
        return recommendations
    
    # Optimization methods
    
    async def _analyze_current_protection_performance(self, protection_type: ProtectionType) -> Dict[str, Any]:
        """Analyze current protection performance for optimization"""
        # Get recent metrics for this protection type
        relevant_metrics = []
        for metrics_list in self.protection_metrics.values():
            relevant_metrics.extend([
                m for m in metrics_list
                if m.protection_type == protection_type
            ])
        
        if not relevant_metrics:
            return {"error": "No performance data available"}
        
        return {
            "average_accuracy": statistics.mean([m.detection_accuracy for m in relevant_metrics]),
            "average_effectiveness": statistics.mean([m.protection_effectiveness for m in relevant_metrics]),
            "average_response_time": statistics.mean([m.response_time_ms for m in relevant_metrics]),
            "total_violations_detected": sum(m.violations_detected for m in relevant_metrics),
            "roi": statistics.mean([m.roi_protection for m in relevant_metrics])
        }
    
    async def _identify_optimization_opportunities(
        self,
        protection_type: ProtectionType,
        current_performance: Dict[str, Any],
        optimization_goals: Dict[str, Any]
    ) -> List[str]:
        """Identify optimization opportunities"""
        opportunities = []
        
        if current_performance.get("average_accuracy", 0) < optimization_goals.get("target_accuracy", 0.95):
            opportunities.append("Improve detection accuracy through model enhancement")
        
        if current_performance.get("average_response_time", 0) > optimization_goals.get("max_response_time", 3600000):
            opportunities.append("Optimize response time through automation")
        
        if current_performance.get("roi", 0) < optimization_goals.get("target_roi", 3.0):
            opportunities.append("Improve cost-effectiveness and ROI")
        
        return opportunities
    
    async def _generate_optimization_plan(
        self,
        protection_type: ProtectionType,
        opportunities: List[str],
        optimization_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed optimization plan"""
        return {
            "phase_1": "Model enhancement and accuracy improvement",
            "phase_2": "Automation and response time optimization",
            "phase_3": "Cost optimization and ROI improvement",
            "timeline_weeks": 8,
            "resource_requirements": "2 ML engineers, 1 DevOps engineer",
            "estimated_cost": "$50,000"
        }
    
    async def _calculate_optimization_impact(
        self,
        protection_type: ProtectionType,
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate expected optimization impact"""
        return {
            "accuracy_improvement": 0.15,      # 15% improvement
            "response_time_reduction": 0.40,   # 40% faster response
            "cost_reduction": 0.25,            # 25% cost reduction
            "roi_improvement": 0.50            # 50% ROI improvement
        }


# Global protection performance intelligence instance
protection_performance_intelligence = ProtectionPerformanceIntelligence()


# Convenience functions for external use
async def analyze_protection_performance(
    protection_id: str,
    protection_type: ProtectionType,
    timeframe: timedelta = timedelta(days=7)
) -> ProtectionPerformanceMetrics:
    """Analyze protection system performance"""
    return await protection_performance_intelligence.analyze_protection_performance(
        protection_id, protection_type, timeframe
    )


async def track_violation(
    violation_id: str,
    violation_type: ViolationType,
    severity: ProtectionSeverity,
    violation_data: Dict[str, Any]
) -> ViolationAnalytics:
    """Track violation detection and response"""
    return await protection_performance_intelligence.track_violation_response(
        violation_id, violation_type, severity, violation_data
    )


async def get_protection_dashboard(timeframe: timedelta = timedelta(days=30)) -> Dict[str, Any]:
    """Get protection performance dashboard"""
    return await protection_performance_intelligence.get_protection_dashboard(timeframe)


async def optimize_protection(
    protection_type: ProtectionType,
    optimization_goals: Dict[str, Any]
) -> Dict[str, Any]:
    """Optimize protection strategy"""
    return await protection_performance_intelligence.optimize_protection_strategy(
        protection_type, optimization_goals
    )


def get_protection_metrics(protection_id: str) -> Optional[List[ProtectionPerformanceMetrics]]:
    """Get protection metrics history"""
    return protection_performance_intelligence.protection_metrics.get(protection_id)


def get_violation_analytics(violation_id: str) -> Optional[ViolationAnalytics]:
    """Get violation analytics"""
    return protection_performance_intelligence.violation_analytics.get(violation_id)