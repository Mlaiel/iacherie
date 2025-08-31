"""Performance Analytics Engine for Copyright Enforcement
Advanced analytics and reporting system for enforcement case tracking and optimization
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from pathlib import Path

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""
    DETECTION_RATE = "detection_rate"
    SUCCESS_RATE = "success_rate"
    RESPONSE_TIME = "response_time"
    RESOLUTION_TIME = "resolution_time"
    PLATFORM_PERFORMANCE = "platform_performance"
    VIOLATION_TRENDS = "violation_trends"
    REVENUE_RECOVERY = "revenue_recovery"
    CASE_VOLUME = "case_volume"
    QUALITY_SCORE = "quality_score"
    USER_SATISFACTION = "user_satisfaction"


class ReportType(Enum):
    """Types of reports generated"""
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_PERFORMANCE = "weekly_performance"
    MONTHLY_ANALYTICS = "monthly_analytics"
    QUARTERLY_REVIEW = "quarterly_review"
    ANNUAL_REPORT = "annual_report"
    PLATFORM_COMPARISON = "platform_comparison"
    TREND_ANALYSIS = "trend_analysis"
    EFFECTIVENESS_ANALYSIS = "effectiveness_analysis"
    COST_BENEFIT = "cost_benefit"
    CUSTOM_REPORT = "custom_report"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            'metric_type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'metadata': self.metadata,
            'tags': list(self.tags)
        }


@dataclass
class AnalyticsAlert:
    """Analytics-based alert"""
    id: str
    alert_type: str
    level: AlertLevel
    title: str
    description: str
    metric_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    metric_type: MetricType
    period: str
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0.0 to 1.0
    current_value: float
    previous_value: float
    change_percentage: float
    confidence_level: float
    projection: Optional[float] = None
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


class CaseAnalyzer:
    """Analyzer for enforcement case performance"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.min_cases_for_analysis = self.config.get('min_cases_for_analysis', 10)
    
    def analyze_case_performance(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance metrics from enforcement cases"""
        try:
            if len(cases) < self.min_cases_for_analysis:
                logger.warning(f"Insufficient cases for analysis: {len(cases)} < {self.min_cases_for_analysis}")
                return {}
            
            analysis = {
                'total_cases': len(cases),
                'success_rate': self._calculate_success_rate(cases),
                'average_resolution_time': self._calculate_avg_resolution_time(cases),
                'platform_breakdown': self._analyze_platform_performance(cases),
                'violation_type_distribution': self._analyze_violation_types(cases),
                'quality_metrics': self._analyze_quality_metrics(cases),
                'temporal_patterns': self._analyze_temporal_patterns(cases),
                'escalation_analysis': self._analyze_escalations(cases)
            }
            
            logger.info(f"Case performance analysis completed for {len(cases)} cases")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing case performance: {e}")
            return {}
    
    def _calculate_success_rate(self, cases: List[Dict[str, Any]]) -> float:
        """Calculate overall success rate"""
        try:
            completed_cases = [case for case in cases if case.get('status') in ['completed', 'resolved']]
            successful_cases = [case for case in completed_cases if case.get('outcome') == 'successful']
            
            if not completed_cases:
                return 0.0
            
            return len(successful_cases) / len(completed_cases)
            
        except Exception as e:
            logger.error(f"Error calculating success rate: {e}")
            return 0.0
    
    def _calculate_avg_resolution_time(self, cases: List[Dict[str, Any]]) -> float:
        """Calculate average resolution time in hours"""
        try:
            resolution_times = []
            
            for case in cases:
                if case.get('resolved_at') and case.get('created_at'):
                    created = datetime.fromisoformat(case['created_at'])
                    resolved = datetime.fromisoformat(case['resolved_at'])
                    resolution_time = (resolved - created).total_seconds() / 3600  # hours
                    resolution_times.append(resolution_time)
            
            return statistics.mean(resolution_times) if resolution_times else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average resolution time: {e}")
            return 0.0
    
    def _analyze_platform_performance(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by platform"""
        try:
            platform_stats = defaultdict(lambda: {
                'total_cases': 0,
                'successful_cases': 0,
                'avg_resolution_time': 0.0,
                'success_rate': 0.0
            })
            
            for case in cases:
                platform = case.get('evidence', {}).get('platform', 'unknown')
                platform_stats[platform]['total_cases'] += 1
                
                if case.get('outcome') == 'successful':
                    platform_stats[platform]['successful_cases'] += 1
                
                if case.get('resolved_at') and case.get('created_at'):
                    created = datetime.fromisoformat(case['created_at'])
                    resolved = datetime.fromisoformat(case['resolved_at'])
                    resolution_time = (resolved - created).total_seconds() / 3600
                    platform_stats[platform]['avg_resolution_time'] += resolution_time
            
            # Calculate averages and success rates
            for platform, stats in platform_stats.items():
                if stats['total_cases'] > 0:
                    stats['success_rate'] = stats['successful_cases'] / stats['total_cases']
                    stats['avg_resolution_time'] /= stats['total_cases']
            
            return dict(platform_stats)
            
        except Exception as e:
            logger.error(f"Error analyzing platform performance: {e}")
            return {}
    
    def _analyze_violation_types(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of violation types"""
        try:
            violation_counts = Counter()
            success_by_type = defaultdict(int)
            
            for case in cases:
                violation_type = case.get('evidence', {}).get('violation_type', 'unknown')
                violation_counts[violation_type] += 1
                
                if case.get('outcome') == 'successful':
                    success_by_type[violation_type] += 1
            
            # Calculate success rates by type
            type_analysis = {}
            for vtype, count in violation_counts.items():
                type_analysis[vtype] = {
                    'total_cases': count,
                    'successful_cases': success_by_type[vtype],
                    'success_rate': success_by_type[vtype] / count if count > 0 else 0.0,
                    'percentage_of_total': count / len(cases) * 100
                }
            
            return type_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing violation types: {e}")
            return {}
    
    def _analyze_quality_metrics(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality-related metrics"""
        try:
            similarity_scores = []
            confidence_scores = []
            evidence_quality_scores = []
            
            for case in cases:
                evidence = case.get('evidence', {})
                
                if 'similarity_score' in evidence:
                    similarity_scores.append(evidence['similarity_score'])
                
                if 'confidence_score' in evidence:
                    confidence_scores.append(evidence['confidence_score'])
                
                # Simulate evidence quality score
                if len(case.get('actions_taken', [])) > 0:
                    evidence_quality_scores.append(0.8)  # Placeholder
            
            quality_metrics = {}
            
            if similarity_scores:
                quality_metrics['similarity_scores'] = {
                    'mean': statistics.mean(similarity_scores),
                    'median': statistics.median(similarity_scores),
                    'std_dev': statistics.stdev(similarity_scores) if len(similarity_scores) > 1 else 0.0,
                    'min': min(similarity_scores),
                    'max': max(similarity_scores)
                }
            
            if confidence_scores:
                quality_metrics['confidence_scores'] = {
                    'mean': statistics.mean(confidence_scores),
                    'median': statistics.median(confidence_scores),
                    'std_dev': statistics.stdev(confidence_scores) if len(confidence_scores) > 1 else 0.0
                }
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing quality metrics: {e}")
            return {}
    
    def _analyze_temporal_patterns(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in cases"""
        try:
            hourly_counts = defaultdict(int)
            daily_counts = defaultdict(int)
            monthly_counts = defaultdict(int)
            
            for case in cases:
                if case.get('created_at'):
                    created = datetime.fromisoformat(case['created_at'])
                    
                    hour_key = created.hour
                    day_key = created.strftime('%A')
                    month_key = created.strftime('%Y-%m')
                    
                    hourly_counts[hour_key] += 1
                    daily_counts[day_key] += 1
                    monthly_counts[month_key] += 1
            
            patterns = {
                'peak_hours': sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                'peak_days': sorted(daily_counts.items(), key=lambda x: x[1], reverse=True)[:3],
                'monthly_trends': dict(monthly_counts),
                'hourly_distribution': dict(hourly_counts),
                'daily_distribution': dict(daily_counts)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing temporal patterns: {e}")
            return {}
    
    def _analyze_escalations(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze escalation patterns"""
        try:
            escalated_cases = [case for case in cases if case.get('status') == 'escalated']
            escalation_rate = len(escalated_cases) / len(cases) if cases else 0.0
            
            escalation_reasons = Counter()
            for case in escalated_cases:
                # Extract escalation reason from notes or metadata
                notes = case.get('notes', [])
                for note in notes:
                    if 'escalation' in note.lower():
                        escalation_reasons['timeout'] += 1  # Simplified
                        break
            
            escalation_analysis = {
                'escalation_rate': escalation_rate,
                'total_escalated': len(escalated_cases),
                'escalation_reasons': dict(escalation_reasons),
                'avg_escalation_time': self._calculate_avg_escalation_time(escalated_cases)
            }
            
            return escalation_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing escalations: {e}")
            return {}
    
    def _calculate_avg_escalation_time(self, escalated_cases: List[Dict[str, Any]]) -> float:
        """Calculate average time to escalation"""
        try:
            escalation_times = []
            
            for case in escalated_cases:
                if case.get('created_at') and case.get('updated_at'):
                    created = datetime.fromisoformat(case['created_at'])
                    updated = datetime.fromisoformat(case['updated_at'])
                    escalation_time = (updated - created).total_seconds() / 3600
                    escalation_times.append(escalation_time)
            
            return statistics.mean(escalation_times) if escalation_times else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average escalation time: {e}")
            return 0.0


class TrendAnalyzer:
    """Analyzer for trends and patterns"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.min_data_points = self.config.get('min_data_points', 5)
        self.trend_periods = self.config.get('trend_periods', ['daily', 'weekly', 'monthly'])
    
    def analyze_trends(self, metrics: List[PerformanceMetric]) -> List[TrendAnalysis]:
        """Analyze trends in performance metrics"""
        try:
            trends = []
            
            # Group metrics by type
            metrics_by_type = defaultdict(list)
            for metric in metrics:
                metrics_by_type[metric.metric_type].append(metric)
            
            # Analyze trends for each metric type
            for metric_type, metric_list in metrics_by_type.items():
                if len(metric_list) >= self.min_data_points:
                    for period in self.trend_periods:
                        trend = self._analyze_metric_trend(metric_type, metric_list, period)
                        if trend:
                            trends.append(trend)
            
            logger.info(f"Trend analysis completed: {len(trends)} trends identified")
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return []
    
    def _analyze_metric_trend(
        self,
        metric_type: MetricType,
        metrics: List[PerformanceMetric],
        period: str
    ) -> Optional[TrendAnalysis]:
        """Analyze trend for specific metric type and period"""
        try:
            # Sort metrics by timestamp
            sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
            
            if len(sorted_metrics) < 2:
                return None
            
            # Calculate trend using linear regression
            values = [m.value for m in sorted_metrics]
            timestamps = [(m.timestamp - sorted_metrics[0].timestamp).total_seconds() 
                         for m in sorted_metrics]
            
            # Simple linear regression
            n = len(values)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(timestamps, values))
            sum_x2 = sum(x * x for x in timestamps)
            
            # Calculate slope
            if n * sum_x2 - sum_x * sum_x == 0:
                slope = 0
            else:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Determine trend direction and strength
            current_value = sorted_metrics[-1].value
            previous_value = sorted_metrics[-2].value if len(sorted_metrics) > 1 else current_value
            
            change_percentage = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
            
            if abs(slope) < 0.01:
                trend_direction = "stable"
                trend_strength = 0.1
            elif slope > 0:
                trend_direction = "increasing"
                trend_strength = min(1.0, abs(slope) * 100)
            else:
                trend_direction = "decreasing"
                trend_strength = min(1.0, abs(slope) * 100)
            
            # Calculate confidence level (simplified)
            confidence_level = min(0.95, 0.5 + (len(sorted_metrics) - 2) * 0.1)
            
            # Simple projection for next period
            projection = current_value + slope * 86400  # Next day projection
            
            trend_analysis = TrendAnalysis(
                metric_type=metric_type,
                period=period,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                current_value=current_value,
                previous_value=previous_value,
                change_percentage=change_percentage,
                confidence_level=confidence_level,
                projection=projection
            )
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing metric trend: {e}")
            return None


class ReportGenerator:
    """Generator for analytics reports"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.report_storage_path = Path(self.config.get('report_storage_path', 'analytics_reports'))
        self.report_storage_path.mkdir(exist_ok=True)
        
        self.template_config = self.config.get('templates', {})
        self.include_charts = self.config.get('include_charts', True)
    
    async def generate_report(
        self,
        report_type: ReportType,
        data: Dict[str, Any],
        date_range: Tuple[datetime, datetime],
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate analytics report"""
        try:
            logger.info(f"Generating {report_type.value} report for {date_range[0]} to {date_range[1]}")
            
            report_id = f"{report_type.value}_{int(datetime.utcnow().timestamp())}"
            start_date, end_date = date_range
            
            # Generate report based on type
            if report_type == ReportType.DAILY_SUMMARY:
                report_content = await self._generate_daily_summary(data, start_date, end_date)
            elif report_type == ReportType.WEEKLY_PERFORMANCE:
                report_content = await self._generate_weekly_performance(data, start_date, end_date)
            elif report_type == ReportType.MONTHLY_ANALYTICS:
                report_content = await self._generate_monthly_analytics(data, start_date, end_date)
            elif report_type == ReportType.PLATFORM_COMPARISON:
                report_content = await self._generate_platform_comparison(data, start_date, end_date)
            elif report_type == ReportType.TREND_ANALYSIS:
                report_content = await self._generate_trend_analysis(data, start_date, end_date)
            elif report_type == ReportType.EFFECTIVENESS_ANALYSIS:
                report_content = await self._generate_effectiveness_analysis(data, start_date, end_date)
            else:
                report_content = await self._generate_custom_report(data, start_date, end_date, custom_params)
            
            # Create final report structure
            report = {
                'id': report_id,
                'type': report_type.value,
                'generated_at': datetime.utcnow().isoformat(),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': report_content.get('summary', {}),
                'detailed_metrics': report_content.get('detailed_metrics', {}),
                'visualizations': report_content.get('visualizations', []),
                'recommendations': report_content.get('recommendations', []),
                'alerts': report_content.get('alerts', []),
                'metadata': {
                    'version': '2.0',
                    'generator': 'analytics_engine',
                    'data_sources': list(data.keys()),
                    'custom_params': custom_params or {}
                }
            }
            
            # Save report to storage
            await self._save_report(report)
            
            logger.info(f"Report generated successfully: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    async def _generate_daily_summary(
        self,
        data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate daily summary report"""
        try:
            cases_data = data.get('cases', [])
            metrics_data = data.get('metrics', [])
            
            # Calculate daily metrics
            total_cases = len(cases_data)
            successful_cases = len([c for c in cases_data if c.get('outcome') == 'successful'])
            pending_cases = len([c for c in cases_data if c.get('status') == 'pending'])
            
            success_rate = (successful_cases / total_cases * 100) if total_cases > 0 else 0
            
            # Platform breakdown
            platform_breakdown = defaultdict(int)
            for case in cases_data:
                platform = case.get('evidence', {}).get('platform', 'unknown')
                platform_breakdown[platform] += 1
            
            summary = {
                'total_cases': total_cases,
                'successful_cases': successful_cases,
                'pending_cases': pending_cases,
                'success_rate': round(success_rate, 1),
                'platform_breakdown': dict(platform_breakdown)
            }
            
            # Detailed metrics
            detailed_metrics = {
                'case_distribution': {
                    'by_violation_type': self._analyze_violation_distribution(cases_data),
                    'by_platform': dict(platform_breakdown),
                    'by_hour': self._analyze_hourly_distribution(cases_data)
                },
                'performance_indicators': {
                    'avg_resolution_time': self._calculate_avg_metric(cases_data, 'resolution_time'),
                    'avg_similarity_score': self._calculate_avg_metric(cases_data, 'similarity_score'),
                    'escalation_rate': self._calculate_escalation_rate(cases_data)
                }
            }
            
            # Generate recommendations
            recommendations = self._generate_daily_recommendations(summary, detailed_metrics)
            
            return {
                'summary': summary,
                'detailed_metrics': detailed_metrics,
                'recommendations': recommendations,
                'visualizations': [],
                'alerts': []
            }
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return {}
    
    async def _generate_weekly_performance(
        self,
        data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate weekly performance report"""
        try:
            cases_data = data.get('cases', [])
            
            # Weekly aggregations
            daily_counts = defaultdict(int)
            daily_success_rates = defaultdict(list)
            
            for case in cases_data:
                if case.get('created_at'):
                    created = datetime.fromisoformat(case['created_at'])
                    day_key = created.strftime('%Y-%m-%d')
                    daily_counts[day_key] += 1
                    
                    if case.get('outcome') == 'successful':
                        daily_success_rates[day_key].append(1)
                    elif case.get('outcome') in ['failed', 'rejected']:
                        daily_success_rates[day_key].append(0)
            
            # Calculate weekly trends
            total_cases = len(cases_data)
            avg_daily_cases = total_cases / 7 if total_cases > 0 else 0
            
            weekly_success_rate = len([c for c in cases_data if c.get('outcome') == 'successful']) / total_cases * 100 if total_cases > 0 else 0
            
            summary = {
                'week_start': start_date.strftime('%Y-%m-%d'),
                'week_end': end_date.strftime('%Y-%m-%d'),
                'total_cases': total_cases,
                'avg_daily_cases': round(avg_daily_cases, 1),
                'weekly_success_rate': round(weekly_success_rate, 1),
                'peak_day': max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else None
            }
            
            # Detailed weekly analysis
            detailed_metrics = {
                'daily_trends': {
                    'case_counts': dict(daily_counts),
                    'success_rates': {day: (sum(rates) / len(rates) * 100) if rates else 0 
                                    for day, rates in daily_success_rates.items()}
                },
                'platform_performance': self._analyze_weekly_platform_performance(cases_data),
                'quality_trends': self._analyze_weekly_quality_trends(cases_data),
                'efficiency_metrics': self._calculate_weekly_efficiency(cases_data)
            }
            
            recommendations = self._generate_weekly_recommendations(summary, detailed_metrics)
            
            return {
                'summary': summary,
                'detailed_metrics': detailed_metrics,
                'recommendations': recommendations,
                'visualizations': [],
                'alerts': []
            }
            
        except Exception as e:
            logger.error(f"Error generating weekly performance report: {e}")
            return {}
    
    async def _generate_platform_comparison(
        self,
        data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate platform comparison report"""
        try:
            cases_data = data.get('cases', [])
            
            # Group cases by platform
            platform_cases = defaultdict(list)
            for case in cases_data:
                platform = case.get('evidence', {}).get('platform', 'unknown')
                platform_cases[platform].append(case)
            
            # Analyze each platform
            platform_analysis = {}
            for platform, platform_case_list in platform_cases.items():
                platform_analysis[platform] = {
                    'total_cases': len(platform_case_list),
                    'successful_cases': len([c for c in platform_case_list if c.get('outcome') == 'successful']),
                    'success_rate': len([c for c in platform_case_list if c.get('outcome') == 'successful']) / len(platform_case_list) * 100 if platform_case_list else 0,
                    'avg_resolution_time': self._calculate_avg_metric(platform_case_list, 'resolution_time'),
                    'avg_similarity_score': self._calculate_avg_metric(platform_case_list, 'similarity_score'),
                    'escalation_rate': self._calculate_escalation_rate(platform_case_list)
                }
            
            # Rankings
            rankings = {
                'by_success_rate': sorted(platform_analysis.items(), 
                                        key=lambda x: x[1]['success_rate'], reverse=True),
                'by_case_volume': sorted(platform_analysis.items(), 
                                       key=lambda x: x[1]['total_cases'], reverse=True),
                'by_resolution_speed': sorted(platform_analysis.items(), 
                                            key=lambda x: x[1]['avg_resolution_time'])
            }
            
            summary = {
                'platforms_analyzed': len(platform_analysis),
                'total_cases': len(cases_data),
                'best_performing_platform': rankings['by_success_rate'][0][0] if rankings['by_success_rate'] else None,
                'highest_volume_platform': rankings['by_case_volume'][0][0] if rankings['by_case_volume'] else None,
                'fastest_platform': rankings['by_resolution_speed'][0][0] if rankings['by_resolution_speed'] else None
            }
            
            detailed_metrics = {
                'platform_analysis': platform_analysis,
                'rankings': rankings,
                'comparative_metrics': self._calculate_comparative_metrics(platform_analysis),
                'correlation_analysis': self._analyze_platform_correlations(platform_analysis)
            }
            
            recommendations = self._generate_platform_recommendations(platform_analysis, rankings)
            
            return {
                'summary': summary,
                'detailed_metrics': detailed_metrics,
                'recommendations': recommendations,
                'visualizations': [],
                'alerts': []
            }
            
        except Exception as e:
            logger.error(f"Error generating platform comparison report: {e}")
            return {}
    
    def _analyze_violation_distribution(self, cases: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze distribution of violation types"""
        violation_counts = Counter()
        for case in cases:
            violation_type = case.get('evidence', {}).get('violation_type', 'unknown')
            violation_counts[violation_type] += 1
        return dict(violation_counts)
    
    def _analyze_hourly_distribution(self, cases: List[Dict[str, Any]]) -> Dict[int, int]:
        """Analyze hourly distribution of cases"""
        hourly_counts = defaultdict(int)
        for case in cases:
            if case.get('created_at'):
                created = datetime.fromisoformat(case['created_at'])
                hourly_counts[created.hour] += 1
        return dict(hourly_counts)
    
    def _calculate_avg_metric(self, cases: List[Dict[str, Any]], metric_name: str) -> float:
        """Calculate average of a specific metric"""
        try:
            values = []
            for case in cases:
                if metric_name == 'resolution_time' and case.get('resolved_at') and case.get('created_at'):
                    created = datetime.fromisoformat(case['created_at'])
                    resolved = datetime.fromisoformat(case['resolved_at'])
                    resolution_time = (resolved - created).total_seconds() / 3600
                    values.append(resolution_time)
                elif metric_name == 'similarity_score' and case.get('evidence', {}).get('similarity_score'):
                    values.append(case['evidence']['similarity_score'])
            
            return statistics.mean(values) if values else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average metric {metric_name}: {e}")
            return 0.0
    
    def _calculate_escalation_rate(self, cases: List[Dict[str, Any]]) -> float:
        """Calculate escalation rate"""
        escalated_cases = len([c for c in cases if c.get('status') == 'escalated'])
        return (escalated_cases / len(cases) * 100) if cases else 0.0
    
    def _generate_daily_recommendations(self, summary: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on daily analysis"""
        recommendations = []
        
        if summary['success_rate'] < 70:
            recommendations.append("Success rate is below optimal threshold. Review case quality and enforcement strategies.")
        
        if summary['pending_cases'] > summary['total_cases'] * 0.5:
            recommendations.append("High number of pending cases. Consider increasing automation or team capacity.")
        
        platform_breakdown = summary.get('platform_breakdown', {})
        if platform_breakdown:
            top_platform = max(platform_breakdown.items(), key=lambda x: x[1])
            if top_platform[1] > summary['total_cases'] * 0.6:
                recommendations.append(f"Heavy concentration on {top_platform[0]}. Consider diversifying monitoring.")
        
        return recommendations
    
    def _generate_weekly_recommendations(self, summary: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on weekly analysis"""
        recommendations = []
        
        if summary['avg_daily_cases'] < 5:
            recommendations.append("Low case volume detected. Review detection algorithms and monitoring coverage.")
        
        if summary['weekly_success_rate'] < 75:
            recommendations.append("Weekly success rate below target. Analyze failed cases for improvement opportunities.")
        
        daily_trends = metrics.get('daily_trends', {})
        case_counts = daily_trends.get('case_counts', {})
        if case_counts:
            max_day_count = max(case_counts.values())
            min_day_count = min(case_counts.values())
            if max_day_count > min_day_count * 3:
                recommendations.append("Significant daily variation in case volume. Consider load balancing strategies.")
        
        return recommendations
    
    def _generate_platform_recommendations(self, analysis: Dict[str, Any], rankings: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on platform analysis"""
        recommendations = []
        
        # Find platforms with low success rates
        low_performing = [platform for platform, data in analysis.items() 
                         if data['success_rate'] < 60 and data['total_cases'] > 5]
        
        if low_performing:
            recommendations.append(f"Platforms with low success rates: {', '.join(low_performing)}. Review platform-specific strategies.")
        
        # Find platforms with high escalation rates
        high_escalation = [platform for platform, data in analysis.items() 
                          if data['escalation_rate'] > 20 and data['total_cases'] > 5]
        
        if high_escalation:
            recommendations.append(f"High escalation rates on: {', '.join(high_escalation)}. Improve initial action selection.")
        
        # Check resolution time disparities
        resolution_times = {platform: data['avg_resolution_time'] for platform, data in analysis.items() 
                           if data['avg_resolution_time'] > 0}
        if len(resolution_times) > 1:
            max_time = max(resolution_times.values())
            min_time = min(resolution_times.values())
            if max_time > min_time * 2:
                slow_platform = max(resolution_times.items(), key=lambda x: x[1])[0]
                recommendations.append(f"Platform {slow_platform} has significantly slower resolution times. Investigate bottlenecks.")
        
        return recommendations
    
    async def _save_report(self, report: Dict[str, Any]):
        """Save report to storage"""
        try:
            report_file = self.report_storage_path / f"{report['id']}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.debug(f"Report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise


class AnalyticsEngine:
    """Main analytics engine for enforcement performance"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize analyzers
        self.case_analyzer = CaseAnalyzer(self.config.get('case_analysis', {}))
        self.trend_analyzer = TrendAnalyzer(self.config.get('trend_analysis', {}))
        self.report_generator = ReportGenerator(self.config.get('reporting', {}))
        
        # Metrics storage
        self.metrics_storage: List[PerformanceMetric] = []
        self.max_stored_metrics = self.config.get('max_stored_metrics', 10000)
        
        # Alert system
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'success_rate_warning': 70.0,
            'success_rate_critical': 50.0,
            'resolution_time_warning': 48.0,  # hours
            'resolution_time_critical': 72.0,
            'escalation_rate_warning': 15.0,
            'escalation_rate_critical': 25.0
        })
        
        self.active_alerts: List[AnalyticsAlert] = []
        self.alert_callbacks: List[callable] = []
        
        logger.info("Analytics engine initialized")
    
    async def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        try:
            self.metrics_storage.append(metric)
            
            # Maintain storage limit
            if len(self.metrics_storage) > self.max_stored_metrics:
                self.metrics_storage = self.metrics_storage[-self.max_stored_metrics:]
            
            # Check for alerts
            await self._check_metric_alerts(metric)
            
            logger.debug(f"Metric recorded: {metric.metric_type.value} = {metric.value}")
            
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
    
    async def analyze_performance(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive performance analysis"""
        try:
            logger.info(f"Starting performance analysis for {len(cases)} cases")
            
            # Case performance analysis
            case_analysis = self.case_analyzer.analyze_case_performance(cases)
            
            # Trend analysis
            trend_analysis = self.trend_analyzer.analyze_trends(self.metrics_storage)
            
            # Overall performance summary
            performance_summary = {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'total_cases_analyzed': len(cases),
                'total_metrics_analyzed': len(self.metrics_storage),
                'case_analysis': case_analysis,
                'trend_analysis': [trend.__dict__ for trend in trend_analysis],
                'active_alerts': len(self.active_alerts),
                'performance_score': self._calculate_overall_performance_score(case_analysis)
            }
            
            logger.info("Performance analysis completed")
            return performance_summary
            
        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
            return {}
    
    async def generate_analytics_report(
        self,
        report_type: ReportType,
        date_range: Tuple[datetime, datetime],
        cases_data: List[Dict[str, Any]],
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate analytics report"""
        try:
            # Prepare data for report generation
            report_data = {
                'cases': cases_data,
                'metrics': [metric.to_dict() for metric in self.metrics_storage],
                'alerts': [alert.__dict__ for alert in self.active_alerts]
            }
            
            # Generate report
            report = await self.report_generator.generate_report(
                report_type=report_type,
                data=report_data,
                date_range=date_range,
                custom_params=custom_params
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            raise
    
    def _calculate_overall_performance_score(self, case_analysis: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        try:
            if not case_analysis:
                return 0.0
            
            # Weight different factors
            success_rate = case_analysis.get('success_rate', 0.0) * 100
            avg_resolution_time = case_analysis.get('average_resolution_time', 48.0)
            
            # Normalize resolution time (lower is better)
            resolution_score = max(0, 100 - (avg_resolution_time / 24.0 * 20))  # 24h = 80 points
            
            # Calculate weighted score
            performance_score = (success_rate * 0.6) + (resolution_score * 0.4)
            
            return min(100.0, max(0.0, performance_score))
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 0.0
    
    async def _check_metric_alerts(self, metric: PerformanceMetric):
        """Check if metric triggers any alerts"""
        try:
            metric_type = metric.metric_type.value
            metric_value = metric.value
            
            # Success rate alerts
            if metric_type == 'success_rate':
                if metric_value < self.alert_thresholds['success_rate_critical']:
                    await self._create_alert(
                        alert_type='success_rate_critical',
                        level=AlertLevel.CRITICAL,
                        title='Critical Success Rate',
                        description=f'Success rate dropped to {metric_value:.1f}%',
                        metric_value=metric_value,
                        threshold=self.alert_thresholds['success_rate_critical']
                    )
                elif metric_value < self.alert_thresholds['success_rate_warning']:
                    await self._create_alert(
                        alert_type='success_rate_warning',
                        level=AlertLevel.WARNING,
                        title='Low Success Rate',
                        description=f'Success rate is {metric_value:.1f}%',
                        metric_value=metric_value,
                        threshold=self.alert_thresholds['success_rate_warning']
                    )
            
            # Resolution time alerts
            elif metric_type == 'resolution_time':
                if metric_value > self.alert_thresholds['resolution_time_critical']:
                    await self._create_alert(
                        alert_type='resolution_time_critical',
                        level=AlertLevel.CRITICAL,
                        title='Critical Resolution Time',
                        description=f'Average resolution time is {metric_value:.1f} hours',
                        metric_value=metric_value,
                        threshold=self.alert_thresholds['resolution_time_critical']
                    )
                elif metric_value > self.alert_thresholds['resolution_time_warning']:
                    await self._create_alert(
                        alert_type='resolution_time_warning',
                        level=AlertLevel.WARNING,
                        title='High Resolution Time',
                        description=f'Average resolution time is {metric_value:.1f} hours',
                        metric_value=metric_value,
                        threshold=self.alert_thresholds['resolution_time_warning']
                    )
            
        except Exception as e:
            logger.error(f"Error checking metric alerts: {e}")
    
    async def _create_alert(
        self,
        alert_type: str,
        level: AlertLevel,
        title: str,
        description: str,
        metric_value: float,
        threshold: float
    ):
        """Create new alert"""
        try:
            alert_id = f"{alert_type}_{int(datetime.utcnow().timestamp())}"
            
            alert = AnalyticsAlert(
                id=alert_id,
                alert_type=alert_type,
                level=level,
                title=title,
                description=description,
                metric_value=metric_value,
                threshold=threshold
            )
            
            self.active_alerts.append(alert)
            
            # Trigger alert callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
            
            logger.warning(f"Alert created: {title} - {description}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def add_alert_callback(self, callback: callable):
        """Add callback for alert notifications"""
        self.alert_callbacks.append(callback)
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an active alert"""
        try:
            for alert in self.active_alerts:
                if alert.id == alert_id:
                    alert.resolved = True
                    alert.resolved_at = datetime.utcnow()
                    logger.info(f"Alert resolved: {alert_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    def get_active_alerts(self) -> List[AnalyticsAlert]:
        """Get list of active alerts"""
        return [alert for alert in self.active_alerts if not alert.resolved]
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            active_alerts = self.get_active_alerts()
            
            # Metrics summary
            metrics_by_type = defaultdict(list)
            for metric in self.metrics_storage[-100:]:  # Last 100 metrics
                metrics_by_type[metric.metric_type.value].append(metric.value)
            
            metrics_summary = {}
            for metric_type, values in metrics_by_type.items():
                if values:
                    metrics_summary[metric_type] = {
                        'current': values[-1],
                        'average': statistics.mean(values),
                        'trend': 'stable'  # Simplified
                    }
            
            summary = {
                'total_metrics_recorded': len(self.metrics_storage),
                'active_alerts': len(active_alerts),
                'critical_alerts': len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
                'metrics_summary': metrics_summary,
                'last_analysis': datetime.utcnow().isoformat(),
                'system_status': 'normal' if len(active_alerts) == 0 else 'attention_required'
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}
    
    async def shutdown(self):
        """Shutdown analytics engine"""
        try:
            # Save current metrics and alerts if needed
            logger.info("Analytics engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down analytics engine: {e}")


# Global instance
analytics_engine = AnalyticsEngine()


async def get_analytics_engine() -> AnalyticsEngine:
    """Get the global analytics engine instance"""
    return analytics_engine


__all__ = [
    'AnalyticsEngine',
    'PerformanceMetric',
    'TrendAnalysis',
    'AnalyticsAlert',
    'MetricType',
    'ReportType',
    'AlertLevel',
    'CaseAnalyzer',
    'TrendAnalyzer',
    'ReportGenerator',
    'get_analytics_engine'
]
