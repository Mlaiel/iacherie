"""
Incident Analytics Engine for Ainflue Platform
Advanced analytics and insights for incident management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import statistics
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
import asyncio

logger = logging.getLogger(__name__)


class AnalyticsType(Enum):
    """Types of incident analytics"""
    MTTR_ANALYSIS = "mttr_analysis"          # Mean Time To Resolution
    MTTD_ANALYSIS = "mttd_analysis"          # Mean Time To Detection
    FREQUENCY_ANALYSIS = "frequency_analysis"
    TREND_ANALYSIS = "trend_analysis"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    TEAM_PERFORMANCE = "team_performance"
    SERVICE_RELIABILITY = "service_reliability"
    CREATOR_IMPACT = "creator_impact"
    BUSINESS_IMPACT = "business_impact"
    SEASONAL_PATTERNS = "seasonal_patterns"


class ReportType(Enum):
    """Types of analytics reports"""
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"
    QUARTERLY_REVIEW = "quarterly_review"
    INCIDENT_POSTMORTEM = "incident_postmortem"
    TEAM_PERFORMANCE = "team_performance"
    SERVICE_HEALTH = "service_health"
    BUSINESS_IMPACT = "business_impact"


@dataclass
class IncidentMetrics:
    """Core incident metrics"""
    incident_id: str
    created_at: datetime
    detected_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    severity: str
    category: str
    affected_services: List[str]
    affected_creators: int
    financial_impact: float
    assigned_team: str
    root_cause: Optional[str]
    resolution_actions: List[str]
    escalation_count: int
    communication_count: int
    satisfaction_score: Optional[float]


@dataclass
class AnalyticsResult:
    """Analytics calculation result"""
    analysis_id: str
    analytics_type: AnalyticsType
    calculated_at: datetime
    time_period: Dict[str, datetime]
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    trend_direction: str  # improving, stable, degrading
    confidence_score: float
    data_points: int
    visualization_data: Dict[str, Any]


class IncidentAnalyticsEngine:
    """
    Advanced incident analytics and reporting engine
    Provides insights, trends, and performance metrics
    """
    
    def __init__(self):
        """Initialize the analytics engine"""
        self.incident_data = []
        self.cached_analytics = {}
        self.performance_targets = self._load_performance_targets()
        
        logger.info("Incident Analytics Engine initialized")
    
    def _load_performance_targets(self) -> Dict[str, Any]:
        """Load performance targets and SLAs"""
        return {
            "mttr_targets": {
                "critical": 60,    # 1 hour
                "high": 240,       # 4 hours  
                "medium": 480,     # 8 hours
                "low": 1440        # 24 hours
            },
            "mttd_targets": {
                "critical": 5,     # 5 minutes
                "high": 15,        # 15 minutes
                "medium": 30,      # 30 minutes
                "low": 60          # 1 hour
            },
            "satisfaction_targets": {
                "minimum": 3.5,    # Out of 5
                "target": 4.0,
                "excellent": 4.5
            },
            "escalation_targets": {
                "max_rate": 0.15,  # 15% of incidents
                "critical_max": 0.25
            }
        }
    
    def ingest_incident_data(self, incident: IncidentMetrics):
        """Ingest incident data for analytics"""
        self.incident_data.append(incident)
        
        # Clear relevant cached analytics
        self._invalidate_cache()
        
        logger.debug(f"Ingested incident data for {incident.incident_id}")
    
    def _invalidate_cache(self):
        """Invalidate cached analytics that need refresh"""
        # Keep cache for 1 hour, then invalidate
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        expired_keys = [
            key for key, result in self.cached_analytics.items()
            if result.calculated_at < cutoff_time
        ]
        
        for key in expired_keys:
            del self.cached_analytics[key]
    
    async def calculate_mttr_analysis(self, 
                                    time_period: Dict[str, datetime],
                                    group_by: str = "severity") -> AnalyticsResult:
        """Calculate Mean Time To Resolution analysis"""
        cache_key = f"mttr_{group_by}_{time_period['start'].isoformat()}"
        
        if cache_key in self.cached_analytics:
            return self.cached_analytics[cache_key]
        
        # Filter incidents by time period
        incidents = self._filter_incidents_by_period(time_period)
        resolved_incidents = [i for i in incidents if i.resolved_at]
        
        if not resolved_incidents:
            return self._create_empty_result(AnalyticsType.MTTR_ANALYSIS, time_period)
        
        # Group incidents
        grouped_data = defaultdict(list)
        for incident in resolved_incidents:
            group_key = getattr(incident, group_by, "unknown")
            
            # Calculate resolution time in minutes
            resolution_time = (incident.resolved_at - incident.created_at).total_seconds() / 60
            grouped_data[group_key].append(resolution_time)
        
        # Calculate metrics
        metrics = {}
        insights = []
        recommendations = []
        
        overall_times = []
        for group, times in grouped_data.items():
            avg_time = statistics.mean(times)
            median_time = statistics.median(times)
            p95_time = self._percentile(times, 95)
            
            metrics[f"{group}_avg_minutes"] = round(avg_time, 2)
            metrics[f"{group}_median_minutes"] = round(median_time, 2)
            metrics[f"{group}_p95_minutes"] = round(p95_time, 2)
            metrics[f"{group}_count"] = len(times)
            
            overall_times.extend(times)
            
            # Compare against targets
            target = self.performance_targets["mttr_targets"].get(group, 480)
            if avg_time > target:
                insights.append(f"{group.title()} incidents exceed MTTR target by {round(avg_time - target, 1)} minutes")
                recommendations.append(f"Focus on improving {group} incident resolution processes")
        
        # Overall metrics
        if overall_times:
            metrics["overall_avg_minutes"] = round(statistics.mean(overall_times), 2)
            metrics["overall_median_minutes"] = round(statistics.median(overall_times), 2)
            metrics["overall_p95_minutes"] = round(self._percentile(overall_times, 95), 2)
        
        # Trend analysis
        trend_direction = self._analyze_trend(resolved_incidents, "resolution_time")
        
        # Create visualization data
        visualization_data = {
            "chart_type": "bar",
            "data": [
                {"group": group, "avg_time": statistics.mean(times)}
                for group, times in grouped_data.items()
            ],
            "targets": self.performance_targets["mttr_targets"]
        }
        
        result = AnalyticsResult(
            analysis_id=f"mttr_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            analytics_type=AnalyticsType.MTTR_ANALYSIS,
            calculated_at=datetime.utcnow(),
            time_period=time_period,
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            trend_direction=trend_direction,
            confidence_score=self._calculate_confidence(len(resolved_incidents)),
            data_points=len(resolved_incidents),
            visualization_data=visualization_data
        )
        
        self.cached_analytics[cache_key] = result
        return result
    
    async def calculate_team_performance(self, 
                                       time_period: Dict[str, datetime]) -> AnalyticsResult:
        """Calculate team performance analytics"""
        incidents = self._filter_incidents_by_period(time_period)
        
        if not incidents:
            return self._create_empty_result(AnalyticsType.TEAM_PERFORMANCE, time_period)
        
        # Group by team
        team_data = defaultdict(lambda: {
            "incidents": [],
            "total_incidents": 0,
            "resolved_incidents": 0,
            "avg_resolution_time": 0,
            "escalations": 0,
            "satisfaction_scores": []
        })
        
        for incident in incidents:
            team = incident.assigned_team
            team_data[team]["incidents"].append(incident)
            team_data[team]["total_incidents"] += 1
            
            if incident.resolved_at:
                team_data[team]["resolved_incidents"] += 1
                resolution_time = (incident.resolved_at - incident.created_at).total_seconds() / 60
                team_data[team]["avg_resolution_time"] += resolution_time
            
            team_data[team]["escalations"] += incident.escalation_count
            
            if incident.satisfaction_score:
                team_data[team]["satisfaction_scores"].append(incident.satisfaction_score)
        
        # Calculate team metrics
        metrics = {}
        insights = []
        recommendations = []
        
        for team, data in team_data.items():
            if data["resolved_incidents"] > 0:
                avg_resolution = data["avg_resolution_time"] / data["resolved_incidents"]
                metrics[f"{team}_avg_resolution_minutes"] = round(avg_resolution, 2)
            
            resolution_rate = data["resolved_incidents"] / data["total_incidents"] if data["total_incidents"] > 0 else 0
            metrics[f"{team}_resolution_rate"] = round(resolution_rate, 3)
            
            escalation_rate = data["escalations"] / data["total_incidents"] if data["total_incidents"] > 0 else 0
            metrics[f"{team}_escalation_rate"] = round(escalation_rate, 3)
            
            if data["satisfaction_scores"]:
                avg_satisfaction = statistics.mean(data["satisfaction_scores"])
                metrics[f"{team}_avg_satisfaction"] = round(avg_satisfaction, 2)
                
                target_satisfaction = self.performance_targets["satisfaction_targets"]["target"]
                if avg_satisfaction < target_satisfaction:
                    insights.append(f"{team} satisfaction below target ({avg_satisfaction:.1f} vs {target_satisfaction})")
                    recommendations.append(f"Review {team} incident handling processes for satisfaction improvement")
            
            target_escalation = self.performance_targets["escalation_targets"]["max_rate"]
            if escalation_rate > target_escalation:
                insights.append(f"{team} escalation rate high ({escalation_rate:.1%} vs {target_escalation:.1%})")
                recommendations.append(f"Provide additional training for {team} on incident resolution")
        
        # Visualization data
        visualization_data = {
            "chart_type": "team_comparison",
            "teams": list(team_data.keys()),
            "metrics": ["resolution_rate", "avg_resolution_minutes", "escalation_rate", "avg_satisfaction"]
        }
        
        return AnalyticsResult(
            analysis_id=f"team_perf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            analytics_type=AnalyticsType.TEAM_PERFORMANCE,
            calculated_at=datetime.utcnow(),
            time_period=time_period,
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            trend_direction="stable",  # Would need historical data for trend
            confidence_score=self._calculate_confidence(len(incidents)),
            data_points=len(incidents),
            visualization_data=visualization_data
        )
    
    async def calculate_service_reliability(self,
                                          time_period: Dict[str, datetime]) -> AnalyticsResult:
        """Calculate service reliability analytics"""
        incidents = self._filter_incidents_by_period(time_period)
        
        if not incidents:
            return self._create_empty_result(AnalyticsType.SERVICE_RELIABILITY, time_period)
        
        # Group by service
        service_data = defaultdict(lambda: {
            "incidents": [],
            "total_downtime_minutes": 0,
            "critical_incidents": 0,
            "total_creators_affected": 0,
            "total_financial_impact": 0
        })
        
        for incident in incidents:
            for service in incident.affected_services:
                service_data[service]["incidents"].append(incident)
                
                if incident.resolved_at and incident.created_at:
                    downtime = (incident.resolved_at - incident.created_at).total_seconds() / 60
                    service_data[service]["total_downtime_minutes"] += downtime
                
                if incident.severity == "critical":
                    service_data[service]["critical_incidents"] += 1
                
                service_data[service]["total_creators_affected"] += incident.affected_creators
                service_data[service]["total_financial_impact"] += incident.financial_impact
        
        # Calculate reliability metrics
        metrics = {}
        insights = []
        recommendations = []
        
        total_period_minutes = (time_period["end"] - time_period["start"]).total_seconds() / 60
        
        for service, data in service_data.items():
            incident_count = len(data["incidents"])
            metrics[f"{service}_incident_count"] = incident_count
            
            # Availability percentage
            uptime_minutes = total_period_minutes - data["total_downtime_minutes"]
            availability = (uptime_minutes / total_period_minutes) * 100 if total_period_minutes > 0 else 100
            metrics[f"{service}_availability_percent"] = round(availability, 3)
            
            # MTBF (Mean Time Between Failures) in hours
            if incident_count > 1:
                mtbf_hours = total_period_minutes / (60 * incident_count)
                metrics[f"{service}_mtbf_hours"] = round(mtbf_hours, 2)
            
            metrics[f"{service}_total_downtime_minutes"] = round(data["total_downtime_minutes"], 2)
            metrics[f"{service}_critical_incidents"] = data["critical_incidents"]
            metrics[f"{service}_creators_affected"] = data["total_creators_affected"]
            metrics[f"{service}_financial_impact"] = round(data["total_financial_impact"], 2)
            
            # Service health insights
            if availability < 99.9:
                insights.append(f"{service} availability below 99.9% ({availability:.2f}%)")
                recommendations.append(f"Investigate {service} reliability issues and implement redundancy")
            
            if data["critical_incidents"] > 0:
                insights.append(f"{service} had {data['critical_incidents']} critical incidents")
                recommendations.append(f"Review {service} monitoring and alerting thresholds")
        
        # Visualization data
        visualization_data = {
            "chart_type": "service_reliability",
            "services": list(service_data.keys()),
            "availability_data": {
                service: metrics.get(f"{service}_availability_percent", 100)
                for service in service_data.keys()
            }
        }
        
        return AnalyticsResult(
            analysis_id=f"reliability_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            analytics_type=AnalyticsType.SERVICE_RELIABILITY,
            calculated_at=datetime.utcnow(),
            time_period=time_period,
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            trend_direction="stable",
            confidence_score=self._calculate_confidence(len(incidents)),
            data_points=len(incidents),
            visualization_data=visualization_data
        )
    
    async def generate_incident_report(self,
                                     report_type: ReportType,
                                     time_period: Dict[str, datetime]) -> Dict[str, Any]:
        """Generate comprehensive incident report"""
        try:
            # Calculate various analytics
            mttr_analysis = await self.calculate_mttr_analysis(time_period)
            team_performance = await self.calculate_team_performance(time_period)
            service_reliability = await self.calculate_service_reliability(time_period)
            
            # Get summary statistics
            incidents = self._filter_incidents_by_period(time_period)
            summary_stats = self._calculate_summary_statistics(incidents)
            
            # Create executive summary
            executive_summary = self._create_executive_summary(
                incidents, mttr_analysis, team_performance, service_reliability
            )
            
            report = {
                "report_id": f"RPT_{report_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "report_type": report_type.value,
                "generated_at": datetime.utcnow().isoformat(),
                "time_period": {
                    "start": time_period["start"].isoformat(),
                    "end": time_period["end"].isoformat()
                },
                "executive_summary": executive_summary,
                "summary_statistics": summary_stats,
                "analytics": {
                    "mttr_analysis": asdict(mttr_analysis),
                    "team_performance": asdict(team_performance),
                    "service_reliability": asdict(service_reliability)
                },
                "recommendations": self._consolidate_recommendations([
                    mttr_analysis, team_performance, service_reliability
                ]),
                "data_quality": {
                    "total_incidents": len(incidents),
                    "incidents_with_resolution": len([i for i in incidents if i.resolved_at]),
                    "confidence_score": min([
                        mttr_analysis.confidence_score,
                        team_performance.confidence_score,
                        service_reliability.confidence_score
                    ])
                }
            }
            
            logger.info(f"Generated {report_type.value} report for {len(incidents)} incidents")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate incident report: {e}")
            raise
    
    def _filter_incidents_by_period(self, time_period: Dict[str, datetime]) -> List[IncidentMetrics]:
        """Filter incidents by time period"""
        return [
            incident for incident in self.incident_data
            if time_period["start"] <= incident.created_at <= time_period["end"]
        ]
    
    def _create_empty_result(self, analytics_type: AnalyticsType, time_period: Dict[str, datetime]) -> AnalyticsResult:
        """Create empty analytics result when no data available"""
        return AnalyticsResult(
            analysis_id=f"empty_{analytics_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            analytics_type=analytics_type,
            calculated_at=datetime.utcnow(),
            time_period=time_period,
            metrics={},
            insights=["No incidents found in the specified time period"],
            recommendations=["Continue monitoring for incidents"],
            trend_direction="stable",
            confidence_score=0.0,
            data_points=0,
            visualization_data={}
        )
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * (percentile / 100)
        f = int(k)
        c = k - f
        
        if f + 1 < len(sorted_data):
            return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
        else:
            return sorted_data[f]
    
    def _analyze_trend(self, incidents: List[IncidentMetrics], metric: str) -> str:
        """Analyze trend direction for incidents"""
        if len(incidents) < 5:
            return "stable"
        
        # Simple trend analysis based on time periods
        mid_point = len(incidents) // 2
        first_half = incidents[:mid_point]
        second_half = incidents[mid_point:]
        
        if metric == "resolution_time":
            first_avg = statistics.mean([
                (i.resolved_at - i.created_at).total_seconds() / 60
                for i in first_half if i.resolved_at
            ]) if any(i.resolved_at for i in first_half) else 0
            
            second_avg = statistics.mean([
                (i.resolved_at - i.created_at).total_seconds() / 60
                for i in second_half if i.resolved_at
            ]) if any(i.resolved_at for i in second_half) else 0
            
            if second_avg > first_avg * 1.1:
                return "degrading"
            elif second_avg < first_avg * 0.9:
                return "improving"
        
        return "stable"
    
    def _calculate_confidence(self, data_points: int) -> float:
        """Calculate confidence score based on data points"""
        if data_points >= 100:
            return 0.95
        elif data_points >= 50:
            return 0.85
        elif data_points >= 20:
            return 0.75
        elif data_points >= 10:
            return 0.65
        elif data_points >= 5:
            return 0.50
        else:
            return 0.30
    
    def _calculate_summary_statistics(self, incidents: List[IncidentMetrics]) -> Dict[str, Any]:
        """Calculate summary statistics for incidents"""
        if not incidents:
            return {}
        
        total_incidents = len(incidents)
        resolved_incidents = [i for i in incidents if i.resolved_at]
        
        severity_counts = Counter(i.severity for i in incidents)
        category_counts = Counter(i.category for i in incidents)
        
        total_creators_affected = sum(i.affected_creators for i in incidents)
        total_financial_impact = sum(i.financial_impact for i in incidents)
        
        return {
            "total_incidents": total_incidents,
            "resolved_incidents": len(resolved_incidents),
            "resolution_rate": len(resolved_incidents) / total_incidents if total_incidents > 0 else 0,
            "severity_distribution": dict(severity_counts),
            "category_distribution": dict(category_counts),
            "total_creators_affected": total_creators_affected,
            "total_financial_impact": round(total_financial_impact, 2),
            "avg_creators_per_incident": round(total_creators_affected / total_incidents, 2) if total_incidents > 0 else 0,
            "avg_financial_impact": round(total_financial_impact / total_incidents, 2) if total_incidents > 0 else 0
        }
    
    def _create_executive_summary(self,
                                incidents: List[IncidentMetrics],
                                mttr_analysis: AnalyticsResult,
                                team_performance: AnalyticsResult,
                                service_reliability: AnalyticsResult) -> Dict[str, Any]:
        """Create executive summary"""
        if not incidents:
            return {"summary": "No incidents occurred in the reporting period."}
        
        total_incidents = len(incidents)
        critical_incidents = len([i for i in incidents if i.severity == "critical"])
        
        # Key highlights
        highlights = []
        
        if critical_incidents > 0:
            highlights.append(f"{critical_incidents} critical incidents occurred")
        
        # MTTR highlights
        overall_mttr = mttr_analysis.metrics.get("overall_avg_minutes", 0)
        if overall_mttr > 0:
            hours = int(overall_mttr // 60)
            minutes = int(overall_mttr % 60)
            highlights.append(f"Average resolution time: {hours}h {minutes}m")
        
        # Service reliability highlights
        if service_reliability.insights:
            highlights.extend(service_reliability.insights[:2])  # Top 2 insights
        
        return {
            "total_incidents": total_incidents,
            "critical_incidents": critical_incidents,
            "key_highlights": highlights,
            "overall_trend": "stable",  # Would calculate from historical data
            "action_required": len(service_reliability.recommendations) > 0
        }
    
    def _consolidate_recommendations(self, analyses: List[AnalyticsResult]) -> List[Dict[str, Any]]:
        """Consolidate recommendations from multiple analyses"""
        all_recommendations = []
        
        for analysis in analyses:
            for rec in analysis.recommendations:
                all_recommendations.append({
                    "recommendation": rec,
                    "source": analysis.analytics_type.value,
                    "priority": "high" if "critical" in rec.lower() else "medium"
                })
        
        # Remove duplicates and prioritize
        unique_recs = []
        seen = set()
        
        for rec in sorted(all_recommendations, key=lambda x: x["priority"], reverse=True):
            if rec["recommendation"] not in seen:
                unique_recs.append(rec)
                seen.add(rec["recommendation"])
        
        return unique_recs[:10]  # Top 10 recommendations
    
    def get_analytics_status(self) -> Dict[str, Any]:
        """Get analytics engine status"""
        return {
            "total_incidents_loaded": len(self.incident_data),
            "cached_analytics": len(self.cached_analytics),
            "performance_targets_loaded": bool(self.performance_targets),
            "last_incident_time": max([i.created_at for i in self.incident_data]).isoformat() if self.incident_data else None,
            "data_range": {
                "start": min([i.created_at for i in self.incident_data]).isoformat() if self.incident_data else None,
                "end": max([i.created_at for i in self.incident_data]).isoformat() if self.incident_data else None
            }
        }


# Factory function
def create_incident_analytics_engine() -> IncidentAnalyticsEngine:
    """Create new incident analytics engine instance"""
    return IncidentAnalyticsEngine()


# Export all classes and functions
__all__ = [
    'IncidentAnalyticsEngine',
    'AnalyticsType',
    'ReportType',
    'IncidentMetrics',
    'AnalyticsResult',
    'create_incident_analytics_engine'
]