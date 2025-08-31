"""
 DMCA Performance Analytics & Metrics Engine
==============================================

Enterprise-grade performance monitoring and analytics system for DMCA operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

  LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION 
====================================================
This software and all associated concepts, algorithms, and implementations are the
exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).

Any unauthorized use, reproduction, distribution, or derivation of this work without
explicit written permission from Fahed Mlaiel is strictly prohibited and may result in:
- Immediate legal action under German and International copyright law
- Claims for damages and lost profits
- Injunctive relief to prevent further infringement
- Criminal prosecution where applicable

Contact: mlaiel@live.de for licensing inquiries.

Project Team Specialties:
- Lead AI Developer & Architect: Fahed Mlaiel (Advanced ML/AI systems)
- Backend Senior Engineer: Enterprise Python/FastAPI systems
- DevOps Engineer: Kubernetes/Cloud infrastructure
- Security Specialist: Cybersecurity & legal compliance
- Audio Processing Engineer: Digital signal processing
- Database Administrator: High-performance data systems
- Microservices Architect: Distributed systems design
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
import json
import statistics
from collections import defaultdict, Counter
import numpy as np
import pandas as pd
from scipy import stats

from . import (
    DMCAStatus, DMCAPriority, NotificationType, PlatformType,
    ContentType, DMCAContentInfo, DMCAInfringement
)

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics"""
    SUCCESS_RATE = "success_rate"
    RESPONSE_TIME = "response_time"
    RESOLUTION_TIME = "resolution_time"
    COMPLIANCE_RATE = "compliance_rate"
    COST_EFFECTIVENESS = "cost_effectiveness"
    PLATFORM_EFFICIENCY = "platform_efficiency"
    EVIDENCE_QUALITY = "evidence_quality"
    ESCALATION_RATE = "escalation_rate"
    REVENUE_RECOVERY = "revenue_recovery"
    USER_SATISFACTION = "user_satisfaction"


class TimeFrame(Enum):
    """Time frames for analytics"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PerformanceIndicator(Enum):
    """Key performance indicators"""
    EXCELLENT = "excellent"    # >95%
    GOOD = "good"             # 85-95%
    AVERAGE = "average"       # 70-85%
    POOR = "poor"             # 50-70%
    CRITICAL = "critical"     # <50%


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any]
    benchmark: Optional[float] = None
    target: Optional[float] = None
    trend: Optional[str] = None  # 'increasing', 'decreasing', 'stable'


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    generated_at: datetime
    time_frame: TimeFrame
    period_start: datetime
    period_end: datetime
    total_cases: int
    metrics: List[PerformanceMetric]
    summary: Dict[str, Any]
    trends: Dict[str, Any]
    recommendations: List[str]
    alerts: List[Dict[str, Any]]
    forecasts: Dict[str, Any]


@dataclass
class PlatformPerformance:
    """Platform-specific performance data"""
    platform: PlatformType
    total_cases: int
    success_rate: float
    avg_response_time: float
    avg_resolution_time: float
    compliance_rate: float
    cost_per_case: float
    revenue_recovered: float
    satisfaction_score: float


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    metric_type: MetricType
    trend_direction: str
    trend_strength: float
    correlation_coefficient: float
    seasonal_patterns: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    forecast: List[Dict[str, Any]]


class DMCAPerformanceAnalyzer:
    """Enterprise performance analyzer for DMCA operations"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetric] = []
        self.reports_cache: Dict[str, AnalyticsReport] = {}
        self.benchmarks: Dict[MetricType, float] = self._initialize_benchmarks()
        self.targets: Dict[MetricType, float] = self._initialize_targets()
    
    def _initialize_benchmarks(self) -> Dict[MetricType, float]:
        """Initialize industry benchmarks"""



        return {
            MetricType.SUCCESS_RATE: 85.0,
            MetricType.RESPONSE_TIME: 24.0,  # hours
            MetricType.RESOLUTION_TIME: 168.0,  # hours (7 days)
            MetricType.COMPLIANCE_RATE: 95.0,
            MetricType.COST_EFFECTIVENESS: 150.0,  # USD per case
            MetricType.PLATFORM_EFFICIENCY: 80.0,
            MetricType.EVIDENCE_QUALITY: 90.0,
            MetricType.ESCALATION_RATE: 15.0,
            MetricType.REVENUE_RECOVERY: 75.0,
            MetricType.USER_SATISFACTION: 80.0
        }
    
    def _initialize_targets(self) -> Dict[MetricType, float]:
        """Initialize performance targets"""



        return {
            MetricType.SUCCESS_RATE: 95.0,
            MetricType.RESPONSE_TIME: 12.0,  # hours
            MetricType.RESOLUTION_TIME: 72.0,  # hours (3 days)
            MetricType.COMPLIANCE_RATE: 99.0,
            MetricType.COST_EFFECTIVENESS: 100.0,  # USD per case
            MetricType.PLATFORM_EFFICIENCY: 95.0,
            MetricType.EVIDENCE_QUALITY: 98.0,
            MetricType.ESCALATION_RATE: 5.0,
            MetricType.REVENUE_RECOVERY: 90.0,
            MetricType.USER_SATISFACTION: 95.0
        }
    
    async def generate_comprehensive_report(
        self,
        time_frame: TimeFrame,
        start_date: datetime,
        end_date: datetime,
        case_data: List[Dict[str, Any]]
    ) -> AnalyticsReport:
        """Generate comprehensive performance analytics report"""
        report_id = f"ANALYTICS_{int(datetime.utcnow().timestamp())}"
        
        logger.info(f"Generating analytics report {report_id} for {time_frame.value}")
        
        # Initialize report
        report = AnalyticsReport(
            report_id=report_id,
            generated_at=datetime.utcnow(),
            time_frame=time_frame,
            period_start=start_date,
            period_end=end_date,
            total_cases=len(case_data),
            metrics=[],
            summary={},
            trends={},
            recommendations=[],
            alerts=[],
            forecasts={}
        )
        
        try:
            # Calculate all metrics
            await self._calculate_success_rate(case_data, report)
            await self._calculate_response_times(case_data, report)
            await self._calculate_resolution_times(case_data, report)
            await self._calculate_compliance_rate(case_data, report)
            await self._calculate_cost_effectiveness(case_data, report)
            await self._calculate_platform_efficiency(case_data, report)
            await self._calculate_evidence_quality(case_data, report)
            await self._calculate_escalation_rate(case_data, report)
            await self._calculate_revenue_recovery(case_data, report)
            await self._calculate_user_satisfaction(case_data, report)
            
            # Perform trend analysis
            await self._analyze_trends(case_data, report)
            
            # Generate platform-specific analysis
            await self._analyze_platform_performance(case_data, report)
            
            # Generate forecasts
            await self._generate_forecasts(case_data, report)
            
            # Generate summary and recommendations
            self._generate_summary(report)
            self._generate_recommendations(report)
            self._generate_alerts(report)
            
            # Cache report
            self.reports_cache[report_id] = report
            
            logger.info(f"Analytics report {report_id} generated successfully")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {str(e)}")
            raise
    
    async def _calculate_success_rate(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate DMCA success rate"""
        if not case_data:
            return
        
        successful_cases = len([
            case for case in case_data 
            if case.get('status') in [DMCAStatus.COMPLIED.value, DMCAStatus.SETTLED.value]
        ])
        
        success_rate = (successful_cases / len(case_data)) * 100
        
        metric = PerformanceMetric(
            metric_type=MetricType.SUCCESS_RATE,
            value=success_rate,
            unit="percentage",
            timestamp=datetime.utcnow(),
            context={"total_cases": len(case_data), "successful_cases": successful_cases},
            benchmark=self.benchmarks[MetricType.SUCCESS_RATE],
            target=self.targets[MetricType.SUCCESS_RATE]
        )
        
        report.metrics.append(metric)
        self.metrics_history.append(metric)
    
    async def _calculate_response_times(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate average response times"""
        response_times = []
        
        for case in case_data:
            created_at = case.get('created_at')
            response_at = case.get('first_response_at')
            
            if created_at and response_at:
                created_dt = datetime.fromisoformat(created_at) if isinstance(created_at, str) else created_at
                response_dt = datetime.fromisoformat(response_at) if isinstance(response_at, str) else response_at
                response_time = (response_dt - created_dt).total_seconds() / 3600  # hours
                response_times.append(response_time)
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            
            metric = PerformanceMetric(
                metric_type=MetricType.RESPONSE_TIME,
                value=avg_response_time,
                unit="hours",
                timestamp=datetime.utcnow(),
                context={
                    "median": median_response_time,
                    "min": min(response_times),
                    "max": max(response_times),
                    "count": len(response_times)
                },
                benchmark=self.benchmarks[MetricType.RESPONSE_TIME],
                target=self.targets[MetricType.RESPONSE_TIME]
            )
            
            report.metrics.append(metric)
            self.metrics_history.append(metric)
    
    async def _calculate_resolution_times(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate average case resolution times"""
        resolution_times = []
        
        for case in case_data:
            created_at = case.get('created_at')
            resolved_at = case.get('resolved_at')
            
            if created_at and resolved_at:
                created_dt = datetime.fromisoformat(created_at) if isinstance(created_at, str) else created_at
                resolved_dt = datetime.fromisoformat(resolved_at) if isinstance(resolved_at, str) else resolved_at
                resolution_time = (resolved_dt - created_dt).total_seconds() / 3600  # hours
                resolution_times.append(resolution_time)
        
        if resolution_times:
            avg_resolution_time = statistics.mean(resolution_times)
            median_resolution_time = statistics.median(resolution_times)
            
            metric = PerformanceMetric(
                metric_type=MetricType.RESOLUTION_TIME,
                value=avg_resolution_time,
                unit="hours",
                timestamp=datetime.utcnow(),
                context={
                    "median": median_resolution_time,
                    "min": min(resolution_times),
                    "max": max(resolution_times),
                    "count": len(resolution_times)
                },
                benchmark=self.benchmarks[MetricType.RESOLUTION_TIME],
                target=self.targets[MetricType.RESOLUTION_TIME]
            )
            
            report.metrics.append(metric)
            self.metrics_history.append(metric)
    
    async def _calculate_compliance_rate(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate legal compliance rate"""
        if not case_data:
            return
        
        compliant_cases = len([
            case for case in case_data 
            if case.get('compliance_verified', False)
        ])
        
        compliance_rate = (compliant_cases / len(case_data)) * 100
        
        metric = PerformanceMetric(
            metric_type=MetricType.COMPLIANCE_RATE,
            value=compliance_rate,
            unit="percentage",
            timestamp=datetime.utcnow(),
            context={"total_cases": len(case_data), "compliant_cases": compliant_cases},
            benchmark=self.benchmarks[MetricType.COMPLIANCE_RATE],
            target=self.targets[MetricType.COMPLIANCE_RATE]
        )
        
        report.metrics.append(metric)
        self.metrics_history.append(metric)
    
    async def _calculate_cost_effectiveness(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate cost effectiveness metrics"""
        total_costs = sum(case.get('processing_cost', 0) for case in case_data)
        
        if case_data:
            cost_per_case = total_costs / len(case_data)
            
            metric = PerformanceMetric(
                metric_type=MetricType.COST_EFFECTIVENESS,
                value=cost_per_case,
                unit="USD",
                timestamp=datetime.utcnow(),
                context={"total_costs": total_costs, "total_cases": len(case_data)},
                benchmark=self.benchmarks[MetricType.COST_EFFECTIVENESS],
                target=self.targets[MetricType.COST_EFFECTIVENESS]
            )
            
            report.metrics.append(metric)
            self.metrics_history.append(metric)
    
    async def _calculate_platform_efficiency(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate platform-specific efficiency"""
        platform_stats = defaultdict(list)
        
        for case in case_data:
            platform = case.get('platform', 'unknown')
            success = case.get('status') in [DMCAStatus.COMPLIED.value, DMCAStatus.SETTLED.value]
            platform_stats[platform].append(success)
        
        if platform_stats:
            platform_efficiencies = {}
            for platform, successes in platform_stats.items():
                efficiency = (sum(successes) / len(successes)) * 100
                platform_efficiencies[platform] = efficiency
            
            overall_efficiency = statistics.mean(platform_efficiencies.values())
            
            metric = PerformanceMetric(
                metric_type=MetricType.PLATFORM_EFFICIENCY,
                value=overall_efficiency,
                unit="percentage",
                timestamp=datetime.utcnow(),
                context={"platform_breakdown": platform_efficiencies},
                benchmark=self.benchmarks[MetricType.PLATFORM_EFFICIENCY],
                target=self.targets[MetricType.PLATFORM_EFFICIENCY]
            )
            
            report.metrics.append(metric)
            self.metrics_history.append(metric)
    
    async def _calculate_evidence_quality(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate evidence quality score"""
        quality_scores = []
        
        for case in case_data:
            evidence_list = case.get('evidence', [])
            if evidence_list:
                case_quality = statistics.mean([
                    evidence.get('quality_score', 0) for evidence in evidence_list
                ])
                quality_scores.append(case_quality)
        
        if quality_scores:
            avg_quality = statistics.mean(quality_scores)
            
            metric = PerformanceMetric(
                metric_type=MetricType.EVIDENCE_QUALITY,
                value=avg_quality,
                unit="score",
                timestamp=datetime.utcnow(),
                context={"sample_size": len(quality_scores)},
                benchmark=self.benchmarks[MetricType.EVIDENCE_QUALITY],
                target=self.targets[MetricType.EVIDENCE_QUALITY]
            )
            
            report.metrics.append(metric)
            self.metrics_history.append(metric)
    
    async def _calculate_escalation_rate(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate case escalation rate"""
        if not case_data:
            return
        
        escalated_cases = len([
            case for case in case_data 
            if case.get('escalation_count', 0) > 0
        ])
        
        escalation_rate = (escalated_cases / len(case_data)) * 100
        
        metric = PerformanceMetric(
            metric_type=MetricType.ESCALATION_RATE,
            value=escalation_rate,
            unit="percentage",
            timestamp=datetime.utcnow(),
            context={"total_cases": len(case_data), "escalated_cases": escalated_cases},
            benchmark=self.benchmarks[MetricType.ESCALATION_RATE],
            target=self.targets[MetricType.ESCALATION_RATE]
        )
        
        report.metrics.append(metric)
        self.metrics_history.append(metric)
    
    async def _calculate_revenue_recovery(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate revenue recovery metrics"""
        total_potential = sum(case.get('potential_revenue', 0) for case in case_data)
        total_recovered = sum(case.get('recovered_revenue', 0) for case in case_data)
        
        if total_potential > 0:
            recovery_rate = (total_recovered / total_potential) * 100
            
            metric = PerformanceMetric(
                metric_type=MetricType.REVENUE_RECOVERY,
                value=recovery_rate,
                unit="percentage",
                timestamp=datetime.utcnow(),
                context={
                    "total_potential": total_potential,
                    "total_recovered": total_recovered,
                    "net_recovery": total_recovered
                },
                benchmark=self.benchmarks[MetricType.REVENUE_RECOVERY],
                target=self.targets[MetricType.REVENUE_RECOVERY]
            )
            
            report.metrics.append(metric)
            self.metrics_history.append(metric)
    
    async def _calculate_user_satisfaction(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Calculate user satisfaction score"""
        satisfaction_scores = [
            case.get('satisfaction_score', 0) for case in case_data
            if case.get('satisfaction_score') is not None
        ]
        
        if satisfaction_scores:
            avg_satisfaction = statistics.mean(satisfaction_scores)
            
            metric = PerformanceMetric(
                metric_type=MetricType.USER_SATISFACTION,
                value=avg_satisfaction,
                unit="score",
                timestamp=datetime.utcnow(),
                context={"sample_size": len(satisfaction_scores)},
                benchmark=self.benchmarks[MetricType.USER_SATISFACTION],
                target=self.targets[MetricType.USER_SATISFACTION]
            )
            
            report.metrics.append(metric)
            self.metrics_history.append(metric)
    
    async def _analyze_trends(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Analyze performance trends"""
        # Group cases by time periods
        time_series_data = defaultdict(list)
        
        for case in case_data:
            created_at = case.get('created_at')
            if created_at:
                date_key = created_at[:10] if isinstance(created_at, str) else created_at.date()
                time_series_data[date_key].append(case)
        
        # Calculate trends for each metric
        trends = {}
        for metric in report.metrics:
            trend_data = self._calculate_metric_trend(metric.metric_type, time_series_data)
            trends[metric.metric_type.value] = trend_data
        
        report.trends = trends
    
    async def _analyze_platform_performance(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Analyze platform-specific performance"""
        platform_data = defaultdict(list)
        
        for case in case_data:
            platform = case.get('platform', 'unknown')
            platform_data[platform].append(case)
        
        platform_performances = []
        
        for platform, cases in platform_data.items():
            if platform == 'unknown':
                continue
                
            performance = await self._calculate_platform_metrics(platform, cases)
            platform_performances.append(performance)
        
        report.summary['platform_performance'] = [
            {
                'platform': p.platform.value if hasattr(p.platform, 'value') else str(p.platform),
                'total_cases': p.total_cases,
                'success_rate': p.success_rate,
                'avg_response_time': p.avg_response_time,
                'avg_resolution_time': p.avg_resolution_time,
                'compliance_rate': p.compliance_rate
            }
            for p in platform_performances
        ]
    
    async def _calculate_platform_metrics(self, platform: str, cases: List[Dict[str, Any]]) -> PlatformPerformance:
        """Calculate metrics for specific platform"""
        total_cases = len(cases)
        
        # Success rate
        successful = len([c for c in cases if c.get('status') in [DMCAStatus.COMPLIED.value, DMCAStatus.SETTLED.value]])
        success_rate = (successful / total_cases) * 100 if total_cases > 0 else 0
        
        # Response times
        response_times = []
        for case in cases:
            created_at = case.get('created_at')
            response_at = case.get('first_response_at')
            if created_at and response_at:
                # Calculate response time logic here
                response_times.append(24.0)  # Placeholder
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        # Resolution times
        resolution_times = []
        for case in cases:
            created_at = case.get('created_at')
            resolved_at = case.get('resolved_at')
            if created_at and resolved_at:
                # Calculate resolution time logic here
                resolution_times.append(72.0)  # Placeholder
        
        avg_resolution_time = statistics.mean(resolution_times) if resolution_times else 0
        
        # Compliance rate
        compliant = len([c for c in cases if c.get('compliance_verified', False)])
        compliance_rate = (compliant / total_cases) * 100 if total_cases > 0 else 0
        
        # Other metrics (simplified)
        cost_per_case = 100.0  # Placeholder
        revenue_recovered = 1000.0  # Placeholder
        satisfaction_score = 85.0  # Placeholder
        
        return PlatformPerformance(
            platform=platform,
            total_cases=total_cases,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            avg_resolution_time=avg_resolution_time,
            compliance_rate=compliance_rate,
            cost_per_case=cost_per_case,
            revenue_recovered=revenue_recovered,
            satisfaction_score=satisfaction_score
        )
    
    async def _generate_forecasts(self, case_data: List[Dict[str, Any]], report: AnalyticsReport):
        """Generate performance forecasts"""
        # Simplified forecasting logic
        forecasts = {}
        
        for metric in report.metrics:
            forecast_data = self._generate_metric_forecast(metric)
            forecasts[metric.metric_type.value] = forecast_data
        
        report.forecasts = forecasts
    
    def _calculate_metric_trend(self, metric_type: MetricType, time_series_data: Dict) -> Dict[str, Any]:
        """Calculate trend for specific metric"""
        # Simplified trend calculation
        return {
            "direction": "stable",
            "strength": 0.5,
            "confidence": 0.8,
            "seasonal_pattern": False
        }
    
    def _generate_metric_forecast(self, metric: PerformanceMetric) -> Dict[str, Any]:
        """Generate forecast for specific metric"""
        # Simplified forecasting
        return {
            "next_period": metric.value * 1.02,  # 2% improvement assumption
            "confidence_interval": [metric.value * 0.95, metric.value * 1.05],
            "forecast_accuracy": 0.85
        }
    
    def _generate_summary(self, report: AnalyticsReport):
        """Generate report summary"""
        metrics_by_type = {m.metric_type: m for m in report.metrics}
        
        report.summary.update({
            "total_cases": report.total_cases,
            "period_days": (report.period_end - report.period_start).days,
            "key_metrics": {
                "success_rate": metrics_by_type.get(MetricType.SUCCESS_RATE, {}).value if MetricType.SUCCESS_RATE in metrics_by_type else 0,
                "avg_response_time": metrics_by_type.get(MetricType.RESPONSE_TIME, {}).value if MetricType.RESPONSE_TIME in metrics_by_type else 0,
                "compliance_rate": metrics_by_type.get(MetricType.COMPLIANCE_RATE, {}).value if MetricType.COMPLIANCE_RATE in metrics_by_type else 0
            },
            "performance_indicators": self._calculate_performance_indicators(report.metrics)
        })
    
    def _generate_recommendations(self, report: AnalyticsReport):
        """Generate performance recommendations"""
        recommendations = []
        
        for metric in report.metrics:
            if metric.target and metric.value < metric.target:
                gap = metric.target - metric.value
                recommendations.append(
                    f"Improve {metric.metric_type.value.replace('_', ' ')} by {gap:.1f} {metric.unit} to meet target"
                )
            
            if metric.benchmark and metric.value < metric.benchmark:
                recommendations.append(
                    f"{metric.metric_type.value.replace('_', ' ').title()} is below industry benchmark"
                )
        
        # Add specific recommendations
        if report.total_cases > 0:
            success_metric = next((m for m in report.metrics if m.metric_type == MetricType.SUCCESS_RATE), None)
            if success_metric and success_metric.value < 90:
                recommendations.append("Consider reviewing and improving DMCA notice templates")
                recommendations.append("Implement additional evidence validation processes")
        
        report.recommendations = recommendations
    
    def _generate_alerts(self, report: AnalyticsReport):
        """Generate performance alerts"""
        alerts = []
        
        for metric in report.metrics:
            # Critical alerts
            if metric.target and metric.value < metric.target * 0.8:
                alerts.append({
                    "severity": "critical",
                    "metric": metric.metric_type.value,
                    "message": f"{metric.metric_type.value.replace('_', ' ').title()} is critically below target",
                    "value": metric.value,
                    "target": metric.target
                })
            
            # Warning alerts
            elif metric.benchmark and metric.value < metric.benchmark * 0.9:
                alerts.append({
                    "severity": "warning",
                    "metric": metric.metric_type.value,
                    "message": f"{metric.metric_type.value.replace('_', ' ').title()} is below industry benchmark",
                    "value": metric.value,
                    "benchmark": metric.benchmark
                })
        
        report.alerts = alerts
    
    def _calculate_performance_indicators(self, metrics: List[PerformanceMetric]) -> Dict[str, str]:
        """Calculate performance indicators for each metric"""
        indicators = {}
        
        for metric in metrics:
            if metric.target:
                ratio = metric.value / metric.target
                if ratio >= 0.95:
                    indicators[metric.metric_type.value] = PerformanceIndicator.EXCELLENT.value
                elif ratio >= 0.85:
                    indicators[metric.metric_type.value] = PerformanceIndicator.GOOD.value
                elif ratio >= 0.70:
                    indicators[metric.metric_type.value] = PerformanceIndicator.AVERAGE.value
                elif ratio >= 0.50:
                    indicators[metric.metric_type.value] = PerformanceIndicator.POOR.value
                else:
                    indicators[metric.metric_type.value] = PerformanceIndicator.CRITICAL.value
        
        return indicators
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        if not self.metrics_history:
            return {}
        
        # Get latest metrics
        latest_metrics = {}
        for metric_type in MetricType:
            recent_metrics = [
                m for m in self.metrics_history 
                if m.metric_type == metric_type and 
                m.timestamp > datetime.utcnow() - timedelta(hours=24)
            ]
            if recent_metrics:
                latest_metrics[metric_type.value] = recent_metrics[-1].value
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": latest_metrics,
            "status": "operational"
        }


# Factory function
def create_performance_analyzer() -> DMCAPerformanceAnalyzer:
    """Factory function to create DMCA performance analyzer"""



    return DMCAPerformanceAnalyzer()
