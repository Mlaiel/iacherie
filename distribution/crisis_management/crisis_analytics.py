"""Crisis Analytics - Advanced Crisis Performance Analysis

Comprehensive analytics system for crisis management performance tracking,
insights generation, and strategy optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json

# Analytics imports
import pandas as pd
import numpy as np

# Core imports
from ..config.crisis_configs import CrisisConfiguration


class AnalyticsTimeframe(Enum):
    """Analytics timeframe options"""
    HOUR = "1h"
    DAY = "24h"
    WEEK = "7d"
    MONTH = "30d"
    QUARTER = "90d"
    YEAR = "365d"


@dataclass
class CrisisMetrics:
    """Crisis performance metrics"""
    crisis_id: str
    detection_time: timedelta
    response_time: timedelta
    resolution_time: Optional[timedelta]
    impact_score: float
    recovery_score: float
    stakeholder_satisfaction: float
    media_coverage_sentiment: float
    financial_impact: float
    reputation_recovery: float
    lesson_learned_count: int
    preventive_measures_implemented: int


@dataclass
class AnalyticsInsight:
    """Analytics insight"""
    insight_id: str
    category: str
    title: str
    description: str
    confidence: float
    impact: str  # 'low', 'medium', 'high'
    recommendations: List[str]
    supporting_data: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.utcnow)


class CrisisAnalytics:
    """Advanced crisis management analytics system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Analytics configuration
        self.crisis_config = CrisisConfiguration()
        
        # Data storage
        self.crisis_metrics: List[CrisisMetrics] = []
        self.performance_history: Dict[str, List[float]] = {}
        self.insights_generated: List[AnalyticsInsight] = []
        
        # Analytics settings
        self.benchmark_data = self._load_benchmark_data()
        self.kpi_targets = self._load_kpi_targets()
        
        self.logger.info("CrisisAnalytics initialized")
    
    def _load_benchmark_data(self) -> Dict[str, float]:
        """Load industry benchmark data"""
        return {
            'avg_detection_time_minutes': 15,
            'avg_response_time_minutes': 30,
            'avg_resolution_time_hours': 24,
            'target_recovery_score': 0.8,
            'target_stakeholder_satisfaction': 0.75,
            'acceptable_financial_impact': 50000
        }
    
    def _load_kpi_targets(self) -> Dict[str, float]:
        """Load KPI targets"""
        return {
            'detection_time_target_minutes': 10,
            'response_time_target_minutes': 20,
            'resolution_time_target_hours': 12,
            'recovery_score_target': 0.85,
            'stakeholder_satisfaction_target': 0.8,
            'reputation_recovery_target': 0.9
        }
    
    async def track_crisis_metrics(self, crisis_id: str, crisis_data: Dict[str, Any]) -> CrisisMetrics:
        """Track comprehensive metrics for a crisis"""
        try:
            # Calculate detection time
            detection_time = timedelta(minutes=crisis_data.get('detection_time_minutes', 0))
            
            # Calculate response time
            response_time = timedelta(minutes=crisis_data.get('response_time_minutes', 0))
            
            # Calculate resolution time (if crisis is resolved)
            resolution_time = None
            if crisis_data.get('resolved_at'):
                resolution_hours = crisis_data.get('resolution_time_hours', 0)
                resolution_time = timedelta(hours=resolution_hours)
            
            # Create metrics object
            metrics = CrisisMetrics(
                crisis_id=crisis_id,
                detection_time=detection_time,
                response_time=response_time,
                resolution_time=resolution_time,
                impact_score=crisis_data.get('impact_score', 0.0),
                recovery_score=crisis_data.get('recovery_score', 0.0),
                stakeholder_satisfaction=crisis_data.get('stakeholder_satisfaction', 0.0),
                media_coverage_sentiment=crisis_data.get('media_sentiment', 0.0),
                financial_impact=crisis_data.get('financial_impact', 0.0),
                reputation_recovery=crisis_data.get('reputation_recovery', 0.0),
                lesson_learned_count=crisis_data.get('lessons_learned', 0),
                preventive_measures_implemented=crisis_data.get('preventive_measures', 0)
            )
            
            # Store metrics
            self.crisis_metrics.append(metrics)
            
            # Update performance history
            self._update_performance_history(metrics)
            
            self.logger.info(f"Crisis metrics tracked for: {crisis_id}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Crisis metrics tracking failed: {e}")
            raise
    
    def _update_performance_history(self, metrics -> None: CrisisMetrics) -> None:
        """Update performance history with new metrics"""
        performance_indicators = [
            ('detection_time', metrics.detection_time.total_seconds() / 60),  # minutes
            ('response_time', metrics.response_time.total_seconds() / 60),    # minutes
            ('impact_score', metrics.impact_score),
            ('recovery_score', metrics.recovery_score),
            ('stakeholder_satisfaction', metrics.stakeholder_satisfaction),
            ('reputation_recovery', metrics.reputation_recovery)
        ]
        
        for indicator, value in performance_indicators:
            if indicator not in self.performance_history:
                self.performance_history[indicator] = []
            self.performance_history[indicator].append(value)
            
            # Keep only last 100 records
            if len(self.performance_history[indicator]) > 100:
                self.performance_history[indicator] = self.performance_history[indicator][-100:]
    
    async def generate_performance_report(self, timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTH) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            # Filter metrics by timeframe
            cutoff_date = self._get_cutoff_date(timeframe)
            recent_metrics = [m for m in self.crisis_metrics if self._get_metric_date(m) >= cutoff_date]
            
            if not recent_metrics:
                return {
                    'report_id': f"crisis_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    'timeframe': timeframe.value,
                    'period': f"{cutoff_date.isoformat()} to {datetime.utcnow().isoformat()}",
                    'summary': 'No crisis data available for the selected timeframe',
                    'metrics': {},
                    'insights': [],
                    'recommendations': []
                }
            
            # Calculate summary statistics
            summary_stats = self._calculate_summary_statistics(recent_metrics)
            
            # Generate performance comparisons
            performance_comparison = self._compare_with_benchmarks(recent_metrics)
            
            # Calculate trends
            trends = self._calculate_performance_trends(recent_metrics)
            
            # Generate insights
            insights = await self._generate_performance_insights(recent_metrics)
            
            # Create recommendations
            recommendations = self._generate_recommendations(recent_metrics, performance_comparison)
            
            report = {
                'report_id': f"crisis_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'generated_at': datetime.utcnow().isoformat(),
                'timeframe': timeframe.value,
                'period': f"{cutoff_date.isoformat()} to {datetime.utcnow().isoformat()}",
                'total_crises': len(recent_metrics),
                'summary_statistics': summary_stats,
                'performance_comparison': performance_comparison,
                'trends': trends,
                'insights': insights,
                'recommendations': recommendations,
                'detailed_metrics': self._format_detailed_metrics(recent_metrics)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Performance report generation failed: {e}")
            raise
    
    def _get_cutoff_date(self, timeframe: AnalyticsTimeframe) -> datetime:
        """Get cutoff date for timeframe"""
        now = datetime.utcnow()
        
        if timeframe == AnalyticsTimeframe.HOUR:
            return now - timedelta(hours=1)
        elif timeframe == AnalyticsTimeframe.DAY:
            return now - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEK:
            return now - timedelta(weeks=1)
        elif timeframe == AnalyticsTimeframe.MONTH:
            return now - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.QUARTER:
            return now - timedelta(days=90)
        elif timeframe == AnalyticsTimeframe.YEAR:
            return now - timedelta(days=365)
        
        return now - timedelta(days=30)  # Default to month
    
    def _get_metric_date(self, metrics: CrisisMetrics) -> datetime:
        """Get date from metrics (simplified - would use actual crisis start date in real implementation)"""
        # For demo purposes, we'll use current time - this would be actual crisis date in real implementation
        return datetime.utcnow()
    
    def _calculate_summary_statistics(self, metrics: List[CrisisMetrics]) -> Dict[str, Any]:
        """Calculate summary statistics for metrics"""
        if not metrics:
            return {}
        
        # Detection times
        detection_times = [m.detection_time.total_seconds() / 60 for m in metrics]  # minutes
        response_times = [m.response_time.total_seconds() / 60 for m in metrics]    # minutes
        
        # Resolution times (only for resolved crises)
        resolution_times = [m.resolution_time.total_seconds() / 3600 for m in metrics if m.resolution_time]  # hours
        
        # Other metrics
        impact_scores = [m.impact_score for m in metrics]
        recovery_scores = [m.recovery_score for m in metrics]
        satisfaction_scores = [m.stakeholder_satisfaction for m in metrics]
        financial_impacts = [m.financial_impact for m in metrics]
        
        return {
            'detection_time': {
                'avg_minutes': np.mean(detection_times),
                'median_minutes': np.median(detection_times),
                'min_minutes': np.min(detection_times),
                'max_minutes': np.max(detection_times),
                'std_minutes': np.std(detection_times)
            },
            'response_time': {
                'avg_minutes': np.mean(response_times),
                'median_minutes': np.median(response_times),
                'min_minutes': np.min(response_times),
                'max_minutes': np.max(response_times),
                'std_minutes': np.std(response_times)
            },
            'resolution_time': {
                'avg_hours': np.mean(resolution_times) if resolution_times else 0,
                'median_hours': np.median(resolution_times) if resolution_times else 0,
                'resolved_count': len(resolution_times),
                'resolution_rate': len(resolution_times) / len(metrics) * 100
            },
            'impact_assessment': {
                'avg_impact_score': np.mean(impact_scores),
                'avg_recovery_score': np.mean(recovery_scores),
                'avg_satisfaction': np.mean(satisfaction_scores),
                'total_financial_impact': np.sum(financial_impacts),
                'avg_financial_impact': np.mean(financial_impacts)
            }
        }
    
    def _compare_with_benchmarks(self, metrics: List[CrisisMetrics]) -> Dict[str, Any]:
        """Compare performance with industry benchmarks"""
        if not metrics:
            return {}
        
        # Calculate current performance
        avg_detection_time = np.mean([m.detection_time.total_seconds() / 60 for m in metrics])
        avg_response_time = np.mean([m.response_time.total_seconds() / 60 for m in metrics])
        avg_recovery_score = np.mean([m.recovery_score for m in metrics])
        avg_satisfaction = np.mean([m.stakeholder_satisfaction for m in metrics])
        
        # Compare with benchmarks
        benchmark = self.benchmark_data
        targets = self.kpi_targets
        
        return {
            'detection_time': {
                'current_avg': avg_detection_time,
                'benchmark': benchmark['avg_detection_time_minutes'],
                'target': targets['detection_time_target_minutes'],
                'vs_benchmark': ((avg_detection_time - benchmark['avg_detection_time_minutes']) / benchmark['avg_detection_time_minutes']) * 100,
                'vs_target': ((avg_detection_time - targets['detection_time_target_minutes']) / targets['detection_time_target_minutes']) * 100,
                'status': 'good' if avg_detection_time <= targets['detection_time_target_minutes'] else 'needs_improvement'
            },
            'response_time': {
                'current_avg': avg_response_time,
                'benchmark': benchmark['avg_response_time_minutes'],
                'target': targets['response_time_target_minutes'],
                'vs_benchmark': ((avg_response_time - benchmark['avg_response_time_minutes']) / benchmark['avg_response_time_minutes']) * 100,
                'vs_target': ((avg_response_time - targets['response_time_target_minutes']) / targets['response_time_target_minutes']) * 100,
                'status': 'good' if avg_response_time <= targets['response_time_target_minutes'] else 'needs_improvement'
            },
            'recovery_performance': {
                'current_avg': avg_recovery_score,
                'target': targets['recovery_score_target'],
                'vs_target': ((avg_recovery_score - targets['recovery_score_target']) / targets['recovery_score_target']) * 100,
                'status': 'good' if avg_recovery_score >= targets['recovery_score_target'] else 'needs_improvement'
            },
            'stakeholder_satisfaction': {
                'current_avg': avg_satisfaction,
                'target': targets['stakeholder_satisfaction_target'],
                'vs_target': ((avg_satisfaction - targets['stakeholder_satisfaction_target']) / targets['stakeholder_satisfaction_target']) * 100,
                'status': 'good' if avg_satisfaction >= targets['stakeholder_satisfaction_target'] else 'needs_improvement'
            }
        }
    
    def _calculate_performance_trends(self, metrics: List[CrisisMetrics]) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(metrics) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        # Sort metrics by crisis_id (proxy for time in this demo)
        sorted_metrics = sorted(metrics, key=lambda x: x.crisis_id)
        
        # Calculate trends for key metrics
        detection_times = [m.detection_time.total_seconds() / 60 for m in sorted_metrics]
        response_times = [m.response_time.total_seconds() / 60 for m in sorted_metrics]
        recovery_scores = [m.recovery_score for m in sorted_metrics]
        satisfaction_scores = [m.stakeholder_satisfaction for m in sorted_metrics]
        
        def calculate_trend(values) -> None:
            if len(values) < 2:
                return 'stable'
            
            # Simple linear trend calculation
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            if slope > 0.1:
                return 'improving'
            elif slope < -0.1:
                return 'declining'
            else:
                return 'stable'
        
        return {
            'detection_time_trend': calculate_trend(detection_times),
            'response_time_trend': calculate_trend(response_times),
            'recovery_score_trend': calculate_trend(recovery_scores),
            'satisfaction_trend': calculate_trend(satisfaction_scores),
            'overall_trend': self._calculate_overall_trend(sorted_metrics)
        }
    
    def _calculate_overall_trend(self, sorted_metrics: List[CrisisMetrics]) -> str:
        """Calculate overall performance trend"""
        if len(sorted_metrics) < 2:
            return 'stable'
        
        # Create composite performance score
        performance_scores = []
        for m in sorted_metrics:
            # Normalize and combine key metrics (lower detection/response time is better)
            detection_norm = max(0, 1 - (m.detection_time.total_seconds() / 60) / 60)  # Normalize to 0-1
            response_norm = max(0, 1 - (m.response_time.total_seconds() / 60) / 120)   # Normalize to 0-1
            
            composite_score = (detection_norm + response_norm + m.recovery_score + m.stakeholder_satisfaction) / 4
            performance_scores.append(composite_score)
        
        # Calculate trend
        x = np.arange(len(performance_scores))
        slope = np.polyfit(x, performance_scores, 1)[0]
        
        if slope > 0.05:
            return 'improving'
        elif slope < -0.05:
            return 'declining'
        else:
            return 'stable'
    
    async def _generate_performance_insights(self, metrics: List[CrisisMetrics]) -> List[Dict[str, Any]]:
        """Generate AI-powered performance insights"""
        insights = []
        
        if not metrics:
            return insights
        
        # Insight 1: Response time patterns
        response_times = [m.response_time.total_seconds() / 60 for m in metrics]
        avg_response_time = np.mean(response_times)
        
        if avg_response_time > self.kpi_targets['response_time_target_minutes']:
            insights.append({
                'category': 'response_time',
                'title': 'Response Time Optimization Opportunity',
                'description': f'Average response time ({avg_response_time:.1f} min) exceeds target ({self.kpi_targets["response_time_target_minutes"]} min)',
                'confidence': 0.9,
                'impact': 'high',
                'recommendations': [
                    'Implement automated alert systems',
                    'Pre-approve crisis response templates',
                    'Establish dedicated crisis response team'
                ]
            })
        
        # Insight 2: Recovery performance patterns
        recovery_scores = [m.recovery_score for m in metrics]
        avg_recovery = np.mean(recovery_scores)
        
        if avg_recovery < self.kpi_targets['recovery_score_target']:
            insights.append({
                'category': 'recovery',
                'title': 'Recovery Strategy Enhancement Needed',
                'description': f'Average recovery score ({avg_recovery:.2f}) below target ({self.kpi_targets["recovery_score_target"]})',
                'confidence': 0.85,
                'impact': 'high',
                'recommendations': [
                    'Review and enhance recovery playbooks',
                    'Implement stakeholder engagement protocols',
                    'Develop post-crisis communication strategies'
                ]
            })
        
        # Insight 3: Stakeholder satisfaction patterns
        satisfaction_scores = [m.stakeholder_satisfaction for m in metrics]
        if satisfaction_scores:
            avg_satisfaction = np.mean(satisfaction_scores)
            satisfaction_variance = np.var(satisfaction_scores)
            
            if satisfaction_variance > 0.1:  # High variance
                insights.append({
                    'category': 'stakeholder_satisfaction',
                    'title': 'Inconsistent Stakeholder Satisfaction',
                    'description': f'High variance in stakeholder satisfaction scores indicates inconsistent crisis handling',
                    'confidence': 0.8,
                    'impact': 'medium',
                    'recommendations': [
                        'Standardize stakeholder communication protocols',
                        'Provide consistent crisis communication training',
                        'Implement stakeholder feedback collection system'
                    ]
                })
        
        # Insight 4: Financial impact analysis
        financial_impacts = [m.financial_impact for m in metrics if m.financial_impact > 0]
        if financial_impacts:
            total_impact = sum(financial_impacts)
            avg_impact = np.mean(financial_impacts)
            
            if avg_impact > self.benchmark_data['acceptable_financial_impact']:
                insights.append({
                    'category': 'financial_impact',
                    'title': 'High Financial Impact Pattern',
                    'description': f'Average crisis financial impact (${avg_impact:,.0f}) exceeds acceptable threshold',
                    'confidence': 0.9,
                    'impact': 'high',
                    'recommendations': [
                        'Implement early warning systems to reduce impact',
                        'Develop crisis prevention protocols',
                        'Consider crisis insurance coverage',
                        'Improve rapid response capabilities'
                    ]
                })
        
        return insights
    
    def _generate_recommendations(self, metrics: List[CrisisMetrics], 
                                 performance_comparison: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Based on performance comparison
        for metric_name, comparison in performance_comparison.items():
            if isinstance(comparison, dict) and comparison.get('status') == 'needs_improvement':
                if metric_name == 'detection_time':
                    recommendations.append("Implement automated monitoring systems to reduce crisis detection time")
                elif metric_name == 'response_time':
                    recommendations.append("Establish pre-approved response protocols to accelerate initial response")
                elif metric_name == 'recovery_performance':
                    recommendations.append("Enhance recovery strategies and stakeholder engagement processes")
                elif metric_name == 'stakeholder_satisfaction':
                    recommendations.append("Improve communication clarity and transparency during crisis situations")
        
        # Based on metrics patterns
        if metrics:
            # Check for high-impact crises
            high_impact_crises = [m for m in metrics if m.impact_score > 7.0]
            if len(high_impact_crises) / len(metrics) > 0.3:  # More than 30% high impact
                recommendations.append("Focus on crisis prevention strategies to reduce high-impact incidents")
            
            # Check for low recovery scores
            low_recovery_crises = [m for m in metrics if m.recovery_score < 0.6]
            if len(low_recovery_crises) / len(metrics) > 0.2:  # More than 20% poor recovery
                recommendations.append("Develop comprehensive post-crisis recovery and reputation rehabilitation programs")
        
        # General recommendations if no specific issues found
        if not recommendations:
            recommendations.extend([
                "Continue monitoring crisis management performance",
                "Regular training and simulation exercises for crisis response team",
                "Maintain updated crisis communication templates and protocols"
            ])
        
        return recommendations
    
    def _format_detailed_metrics(self, metrics: List[CrisisMetrics]) -> List[Dict[str, Any]]:
        """Format detailed metrics for reporting"""
        formatted_metrics = []
        
        for m in metrics:
            formatted_metrics.append({
                'crisis_id': m.crisis_id,
                'detection_time_minutes': m.detection_time.total_seconds() / 60,
                'response_time_minutes': m.response_time.total_seconds() / 60,
                'resolution_time_hours': m.resolution_time.total_seconds() / 3600 if m.resolution_time else None,
                'impact_score': m.impact_score,
                'recovery_score': m.recovery_score,
                'stakeholder_satisfaction': m.stakeholder_satisfaction,
                'media_coverage_sentiment': m.media_coverage_sentiment,
                'financial_impact': m.financial_impact,
                'reputation_recovery': m.reputation_recovery,
                'lessons_learned': m.lesson_learned_count,
                'preventive_measures': m.preventive_measures_implemented
            })
        
        return formatted_metrics
    
    async def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        try:
            # Get recent metrics (last 30 days)
            recent_metrics = self.crisis_metrics[-30:] if len(self.crisis_metrics) > 30 else self.crisis_metrics
            
            if not recent_metrics:
                return {
                    'status': 'no_data',
                    'message': 'No crisis data available',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Calculate key performance indicators
            avg_detection_time = np.mean([m.detection_time.total_seconds() / 60 for m in recent_metrics])
            avg_response_time = np.mean([m.response_time.total_seconds() / 60 for m in recent_metrics])
            avg_recovery_score = np.mean([m.recovery_score for m in recent_metrics])
            avg_satisfaction = np.mean([m.stakeholder_satisfaction for m in recent_metrics])
            
            # Calculate performance status
            performance_status = self._calculate_overall_performance_status(recent_metrics)
            
            dashboard_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'overview': {
                    'total_crises_tracked': len(self.crisis_metrics),
                    'recent_crises_30d': len(recent_metrics),
                    'performance_status': performance_status,
                    'avg_detection_time_minutes': avg_detection_time,
                    'avg_response_time_minutes': avg_response_time,
                    'avg_recovery_score': avg_recovery_score,
                    'avg_stakeholder_satisfaction': avg_satisfaction
                },
                'performance_indicators': {
                    'detection_time_status': 'good' if avg_detection_time <= self.kpi_targets['detection_time_target_minutes'] else 'needs_improvement',
                    'response_time_status': 'good' if avg_response_time <= self.kpi_targets['response_time_target_minutes'] else 'needs_improvement',
                    'recovery_status': 'good' if avg_recovery_score >= self.kpi_targets['recovery_score_target'] else 'needs_improvement',
                    'satisfaction_status': 'good' if avg_satisfaction >= self.kpi_targets['stakeholder_satisfaction_target'] else 'needs_improvement'
                },
                'recent_insights': [insight.__dict__ for insight in self.insights_generated[-5:]],
                'trend_summary': self._calculate_performance_trends(recent_metrics)
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Dashboard data generation failed: {e}")
            raise
    
    def _calculate_overall_performance_status(self, metrics: List[CrisisMetrics]) -> str:
        """Calculate overall performance status"""
        if not metrics:
            return 'unknown'
        
        # Check how many KPIs are meeting targets
        avg_detection_time = np.mean([m.detection_time.total_seconds() / 60 for m in metrics])
        avg_response_time = np.mean([m.response_time.total_seconds() / 60 for m in metrics])
        avg_recovery_score = np.mean([m.recovery_score for m in metrics])
        avg_satisfaction = np.mean([m.stakeholder_satisfaction for m in metrics])
        
        targets_met = 0
        total_targets = 4
        
        if avg_detection_time <= self.kpi_targets['detection_time_target_minutes']:
            targets_met += 1
        if avg_response_time <= self.kpi_targets['response_time_target_minutes']:
            targets_met += 1
        if avg_recovery_score >= self.kpi_targets['recovery_score_target']:
            targets_met += 1
        if avg_satisfaction >= self.kpi_targets['stakeholder_satisfaction_target']:
            targets_met += 1
        
        performance_ratio = targets_met / total_targets
        
        if performance_ratio >= 0.8:
            return 'excellent'
        elif performance_ratio >= 0.6:
            return 'good'
        elif performance_ratio >= 0.4:
            return 'fair'
        else:
            return 'poor'


# Export classes
__all__ = [
    'CrisisAnalytics',
    'CrisisMetrics',
    'AnalyticsInsight',
    'AnalyticsTimeframe'
]