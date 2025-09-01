"""Global Platform Health Scoring System
Comprehensive health scoring system that aggregates all platform metrics
into a single normalized health score with detailed breakdown by category.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import statistics

# Import existing monitoring systems
from ..health.health_checks import HealthChecksManager, SystemMetrics
from ..sla_monitoring.sla_tracker import sla_tracker
from ...security.monitoring import SecurityMonitor

logger = logging.getLogger(__name__)


class HealthCategory(Enum):
    """Health scoring categories"""
    SYSTEM_PERFORMANCE = "system_performance"
    API_RESPONSE = "api_response"
    SECURITY = "security"
    AVAILABILITY = "availability"
    ERROR_RATES = "error_rates"
    RESOURCE_UTILIZATION = "resource_utilization"
    SLA_COMPLIANCE = "sla_compliance"
    BUSINESS_METRICS = "business_metrics"


@dataclass
class HealthScore:
    """Individual health score for a category"""
    category: HealthCategory
    score: float  # 0-100 scale
    weight: float  # Weight in overall score
    status: str  # "excellent", "good", "warning", "critical"
    details: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    trend: str = "stable"  # "improving", "stable", "declining"


class GlobalHealthScorer:
    """
    Global platform health scoring system
    Aggregates multiple monitoring sources into unified health scores
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scores: Dict[HealthCategory, HealthScore] = {}
        self.score_history: List[Tuple[datetime, float]] = []
        self.weight_config = {
            HealthCategory.SYSTEM_PERFORMANCE: 0.20,
            HealthCategory.API_RESPONSE: 0.18,
            HealthCategory.SECURITY: 0.15,
            HealthCategory.AVAILABILITY: 0.15,
            HealthCategory.ERROR_RATES: 0.12,
            HealthCategory.RESOURCE_UTILIZATION: 0.10,
            HealthCategory.SLA_COMPLIANCE: 0.08,
            HealthCategory.BUSINESS_METRICS: 0.02
        }
        
        # Initialize monitoring components
        self.system_metrics = SystemMetrics()
        self.security_monitor = None  # Will be initialized if available
        
        # Score thresholds
        self.thresholds = {
            "excellent": 90.0,
            "good": 75.0,
            "warning": 60.0,
            "critical": 0.0
        }
        
    async def initialize(self) -> bool:
        """Initialize health scoring system"""
        try:
            # Initialize security monitor if available
            try:
                self.security_monitor = SecurityMonitor()
            except Exception as e:
                self.logger.warning(f"Security monitor not available: {e}")
                
            self.logger.info("Global health scoring system initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize health scoring: {e}")
            return False
    
    def _get_status_from_score(self, score: float) -> str:
        """Convert numeric score to status string"""
        if score >= self.thresholds["excellent"]:
            return "excellent"
        elif score >= self.thresholds["good"]:
            return "good"
        elif score >= self.thresholds["warning"]:
            return "warning"
        else:
            return "critical"
    
    async def calculate_system_performance_score(self) -> HealthScore:
        """Calculate system performance health score"""
        try:
            stats = self.system_metrics.get_system_stats()
            
            # CPU score (0-100, inverted from usage percentage)
            cpu_score = max(0, 100 - stats["cpu_percent"])
            
            # Memory score (0-100, inverted from usage percentage)
            memory_score = max(0, 100 - stats["memory"]["percent"])
            
            # Disk score (0-100, inverted from usage percentage)
            disk_score = max(0, 100 - stats["disk"]["percent"])
            
            # Network score (simplified - assume good if no errors)
            network_score = 95.0  # Placeholder
            
            # Weighted average
            overall_score = (
                cpu_score * 0.30 +
                memory_score * 0.30 +
                disk_score * 0.25 +
                network_score * 0.15
            )
            
            score = HealthScore(
                category=HealthCategory.SYSTEM_PERFORMANCE,
                score=overall_score,
                weight=self.weight_config[HealthCategory.SYSTEM_PERFORMANCE],
                status=self._get_status_from_score(overall_score),
                details={
                    "cpu_score": cpu_score,
                    "memory_score": memory_score,
                    "disk_score": disk_score,
                    "network_score": network_score,
                    "cpu_percent": stats["cpu_percent"],
                    "memory_percent": stats["memory"]["percent"],
                    "disk_percent": stats["disk"]["percent"]
                }
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating system performance score: {e}")
            return HealthScore(
                category=HealthCategory.SYSTEM_PERFORMANCE,
                score=0.0,
                weight=self.weight_config[HealthCategory.SYSTEM_PERFORMANCE],
                status="critical",
                details={"error": str(e)}
            )
    
    async def calculate_api_response_score(self) -> HealthScore:
        """Calculate API response time health score"""
        try:
            sla_status = await sla_tracker.get_sla_status()
            
            # Get response time metric
            response_time_metric = sla_status.get("metrics", {}).get("response_time_p95", {})
            current_p95 = response_time_metric.get("current_value", 0)
            target_p95 = response_time_metric.get("target_value", 2000)
            
            # Calculate score based on how close we are to target
            if current_p95 == 0:
                score_value = 100.0  # No data yet
            elif current_p95 <= target_p95:
                # Linear scale from 100 at 0ms to 75 at target
                score_value = 100 - (current_p95 / target_p95) * 25
            else:
                # Linear scale from 75 at target to 0 at 2x target
                overage = (current_p95 - target_p95) / target_p95
                score_value = max(0, 75 - (overage * 75))
            
            score = HealthScore(
                category=HealthCategory.API_RESPONSE,
                score=score_value,
                weight=self.weight_config[HealthCategory.API_RESPONSE],
                status=self._get_status_from_score(score_value),
                details={
                    "current_p95_ms": current_p95,
                    "target_p95_ms": target_p95,
                    "compliance": response_time_metric.get("compliance", True)
                }
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating API response score: {e}")
            return HealthScore(
                category=HealthCategory.API_RESPONSE,
                score=0.0,
                weight=self.weight_config[HealthCategory.API_RESPONSE],
                status="critical",
                details={"error": str(e)}
            )
    
    async def calculate_security_score(self) -> HealthScore:
        """Calculate security health score"""
        try:
            score_value = 85.0  # Base security score
            details = {"base_score": score_value}
            
            # If security monitor is available, get real metrics
            if self.security_monitor:
                try:
                    security_status = await self.security_monitor.get_security_status()
                    
                    # Adjust score based on security findings
                    critical_alerts = security_status.get("critical_alerts", 0)
                    high_alerts = security_status.get("high_alerts", 0)
                    
                    # Deduct points for alerts
                    score_value -= (critical_alerts * 15 + high_alerts * 5)
                    score_value = max(0, score_value)
                    
                    details.update({
                        "critical_alerts": critical_alerts,
                        "high_alerts": high_alerts,
                        "security_status": security_status
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Could not get security status: {e}")
            
            score = HealthScore(
                category=HealthCategory.SECURITY,
                score=score_value,
                weight=self.weight_config[HealthCategory.SECURITY],
                status=self._get_status_from_score(score_value),
                details=details
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating security score: {e}")
            return HealthScore(
                category=HealthCategory.SECURITY,
                score=0.0,
                weight=self.weight_config[HealthCategory.SECURITY],
                status="critical",
                details={"error": str(e)}
            )
    
    async def calculate_availability_score(self) -> HealthScore:
        """Calculate availability health score"""
        try:
            sla_status = await sla_tracker.get_sla_status()
            
            # Get uptime metric
            uptime_metric = sla_status.get("metrics", {}).get("uptime_percentage", {})
            current_uptime = uptime_metric.get("current_value", 100.0)
            target_uptime = uptime_metric.get("target_value", 99.9)
            
            # Calculate score based on uptime percentage
            if current_uptime >= target_uptime:
                score_value = 100.0
            else:
                # Linear scale based on how far below target
                deficit = target_uptime - current_uptime
                score_value = max(0, 100 - (deficit * 20))  # 5% deficit = 0 score
            
            score = HealthScore(
                category=HealthCategory.AVAILABILITY,
                score=score_value,
                weight=self.weight_config[HealthCategory.AVAILABILITY],
                status=self._get_status_from_score(score_value),
                details={
                    "current_uptime": current_uptime,
                    "target_uptime": target_uptime,
                    "compliance": uptime_metric.get("compliance", True)
                }
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating availability score: {e}")
            return HealthScore(
                category=HealthCategory.AVAILABILITY,
                score=0.0,
                weight=self.weight_config[HealthCategory.AVAILABILITY],
                status="critical",
                details={"error": str(e)}
            )
    
    async def calculate_error_rates_score(self) -> HealthScore:
        """Calculate error rates health score"""
        try:
            app_stats = self.system_metrics.get_application_stats()
            error_rate = app_stats.get("error_rate", 0.0)
            
            # Score based on error rate (lower is better)
            if error_rate <= 0.1:  # Less than 0.1% error rate
                score_value = 100.0
            elif error_rate <= 1.0:  # Less than 1% error rate
                score_value = 90.0 - (error_rate * 50)
            elif error_rate <= 5.0:  # Less than 5% error rate
                score_value = 40.0 - ((error_rate - 1) * 10)
            else:  # Above 5% error rate
                score_value = max(0, 10.0 - (error_rate - 5))
            
            score = HealthScore(
                category=HealthCategory.ERROR_RATES,
                score=score_value,
                weight=self.weight_config[HealthCategory.ERROR_RATES],
                status=self._get_status_from_score(score_value),
                details={
                    "error_rate_percent": error_rate,
                    "total_requests": app_stats.get("requests_total", 0),
                    "total_errors": app_stats.get("errors_total", 0)
                }
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating error rates score: {e}")
            return HealthScore(
                category=HealthCategory.ERROR_RATES,
                score=0.0,
                weight=self.weight_config[HealthCategory.ERROR_RATES],
                status="critical",
                details={"error": str(e)}
            )
    
    async def calculate_resource_utilization_score(self) -> HealthScore:
        """Calculate resource utilization health score"""
        try:
            stats = self.system_metrics.get_system_stats()
            app_stats = self.system_metrics.get_application_stats()
            
            # CPU utilization score (optimal around 50-70%)
            cpu_percent = stats["cpu_percent"]
            if 50 <= cpu_percent <= 70:
                cpu_score = 100.0
            elif cpu_percent < 50:
                cpu_score = 80.0 + (cpu_percent / 50) * 20
            else:
                cpu_score = max(0, 100 - ((cpu_percent - 70) * 2))
            
            # Memory utilization score (optimal around 60-80%)
            memory_percent = stats["memory"]["percent"]
            if 60 <= memory_percent <= 80:
                memory_score = 100.0
            elif memory_percent < 60:
                memory_score = 80.0 + (memory_percent / 60) * 20
            else:
                memory_score = max(0, 100 - ((memory_percent - 80) * 3))
            
            # Thread utilization score
            active_threads = app_stats.get("active_threads", 1)
            if active_threads < 100:
                thread_score = 100.0
            else:
                thread_score = max(0, 100 - ((active_threads - 100) * 0.5))
            
            # Overall resource utilization score
            overall_score = (cpu_score * 0.4 + memory_score * 0.4 + thread_score * 0.2)
            
            score = HealthScore(
                category=HealthCategory.RESOURCE_UTILIZATION,
                score=overall_score,
                weight=self.weight_config[HealthCategory.RESOURCE_UTILIZATION],
                status=self._get_status_from_score(overall_score),
                details={
                    "cpu_score": cpu_score,
                    "memory_score": memory_score,
                    "thread_score": thread_score,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "active_threads": active_threads
                }
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating resource utilization score: {e}")
            return HealthScore(
                category=HealthCategory.RESOURCE_UTILIZATION,
                score=0.0,
                weight=self.weight_config[HealthCategory.RESOURCE_UTILIZATION],
                status="critical",
                details={"error": str(e)}
            )
    
    async def calculate_sla_compliance_score(self) -> HealthScore:
        """Calculate SLA compliance health score"""
        try:
            sla_status = await sla_tracker.get_sla_status()
            
            overall_compliance = sla_status.get("overall_compliance", True)
            violations = sla_status.get("violations", 0)
            warnings = sla_status.get("warnings", 0)
            
            # Base score based on overall compliance
            if overall_compliance:
                score_value = 100.0
            else:
                score_value = 50.0
            
            # Deduct points for violations and warnings
            score_value -= (violations * 10 + warnings * 5)
            score_value = max(0, score_value)
            
            score = HealthScore(
                category=HealthCategory.SLA_COMPLIANCE,
                score=score_value,
                weight=self.weight_config[HealthCategory.SLA_COMPLIANCE],
                status=self._get_status_from_score(score_value),
                details={
                    "overall_compliance": overall_compliance,
                    "violations": violations,
                    "warnings": warnings,
                    "sla_status": sla_status
                }
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating SLA compliance score: {e}")
            return HealthScore(
                category=HealthCategory.SLA_COMPLIANCE,
                score=0.0,
                weight=self.weight_config[HealthCategory.SLA_COMPLIANCE],
                status="critical",
                details={"error": str(e)}
            )
    
    async def calculate_business_metrics_score(self) -> HealthScore:
        """Calculate business metrics health score"""
        try:
            # Placeholder for business metrics
            # In a real implementation, this would check:
            # - Revenue metrics
            # - User engagement
            # - Content processing rates
            # - Platform growth metrics
            
            score_value = 80.0  # Base business score
            
            score = HealthScore(
                category=HealthCategory.BUSINESS_METRICS,
                score=score_value,
                weight=self.weight_config[HealthCategory.BUSINESS_METRICS],
                status=self._get_status_from_score(score_value),
                details={
                    "note": "Business metrics scoring not fully implemented",
                    "base_score": score_value
                }
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating business metrics score: {e}")
            return HealthScore(
                category=HealthCategory.BUSINESS_METRICS,
                score=0.0,
                weight=self.weight_config[HealthCategory.BUSINESS_METRICS],
                status="critical",
                details={"error": str(e)}
            )
    
    async def calculate_all_scores(self) -> Dict[HealthCategory, HealthScore]:
        """Calculate all health scores"""
        scores = {}
        
        # Calculate individual category scores
        calculation_tasks = [
            self.calculate_system_performance_score(),
            self.calculate_api_response_score(),
            self.calculate_security_score(),
            self.calculate_availability_score(),
            self.calculate_error_rates_score(),
            self.calculate_resource_utilization_score(),
            self.calculate_sla_compliance_score(),
            self.calculate_business_metrics_score()
        ]
        
        try:
            results = await asyncio.gather(*calculation_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, HealthScore):
                    scores[result.category] = result
                else:
                    self.logger.error(f"Error in score calculation: {result}")
                    
        except Exception as e:
            self.logger.error(f"Error calculating health scores: {e}")
        
        self.scores = scores
        return scores
    
    async def get_global_health_score(self) -> Dict[str, Any]:
        """Get the global health score with breakdown"""
        await self.calculate_all_scores()
        
        # Calculate weighted overall score
        total_weighted_score = 0.0
        total_weight = 0.0
        
        category_scores = {}
        for category, score in self.scores.items():
            weighted_score = score.score * score.weight
            total_weighted_score += weighted_score
            total_weight += score.weight
            
            category_scores[category.value] = {
                "score": score.score,
                "status": score.status,
                "weight": score.weight,
                "details": score.details,
                "last_updated": score.last_updated.isoformat(),
                "trend": score.trend
            }
        
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        overall_status = self._get_status_from_score(overall_score)
        
        # Add to history
        self.score_history.append((datetime.now(), overall_score))
        
        # Calculate trend (compare with previous scores)
        trend = "stable"
        if len(self.score_history) >= 2:
            recent_scores = [score for _, score in self.score_history[-5:]]
            if len(recent_scores) >= 2:
                if recent_scores[-1] > recent_scores[0]:
                    trend = "improving"
                elif recent_scores[-1] < recent_scores[0]:
                    trend = "declining"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_score": round(overall_score, 2),
            "overall_status": overall_status,
            "trend": trend,
            "category_scores": category_scores,
            "score_distribution": {
                "excellent": sum(1 for s in self.scores.values() if s.status == "excellent"),
                "good": sum(1 for s in self.scores.values() if s.status == "good"),
                "warning": sum(1 for s in self.scores.values() if s.status == "warning"),
                "critical": sum(1 for s in self.scores.values() if s.status == "critical")
            },
            "recommendations": await self._generate_recommendations()
        }
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        for category, score in self.scores.items():
            if score.status == "critical":
                if category == HealthCategory.SYSTEM_PERFORMANCE:
                    recommendations.append("Critical: System performance degraded - check CPU, memory, and disk usage")
                elif category == HealthCategory.API_RESPONSE:
                    recommendations.append("Critical: API response times are too high - optimize database queries and caching")
                elif category == HealthCategory.SECURITY:
                    recommendations.append("Critical: Security issues detected - review security alerts immediately")
                elif category == HealthCategory.AVAILABILITY:
                    recommendations.append("Critical: System availability below target - check for service outages")
                elif category == HealthCategory.ERROR_RATES:
                    recommendations.append("Critical: High error rates detected - review application logs")
                    
            elif score.status == "warning":
                if category == HealthCategory.SYSTEM_PERFORMANCE:
                    recommendations.append("Warning: System performance declining - consider scaling resources")
                elif category == HealthCategory.API_RESPONSE:
                    recommendations.append("Warning: API response times increasing - monitor query performance")
                elif category == HealthCategory.SECURITY:
                    recommendations.append("Warning: Security alerts detected - review and address security findings")
        
        return recommendations


# Global health scorer instance
global_health_scorer = GlobalHealthScorer()