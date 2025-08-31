"""
Advanced Collaboration Analytics Engine for IA Influencer Agent
Professional analytics and insights for collaboration performance

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import json
import statistics

from .collaboration_models import (
    CollaborationRequest, CollaborationMatch, CollaborationContract,
    CollaborationAnalytics, CollaborationType, CollaborationStatus
)


logger = logging.getLogger(__name__)


class AnalyticsMetric(Enum):
    """Types of analytics metrics"""
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    FINANCIAL = "financial"
    QUALITY = "quality"
    SATISFACTION = "satisfaction"
    EFFICIENCY = "efficiency"
    GROWTH = "growth"
    PREDICTIVE = "predictive"


@dataclass
class AnalyticsInsight:
    """Represents an analytics insight"""
    metric_type: AnalyticsMetric
    title: str
    description: str
    value: float
    trend_direction: str  # "up", "down", "stable"
    confidence_score: float
    actionable_recommendations: List[str] = field(default_factory=list)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollaborationTrendData:
    """Trend data for collaboration metrics"""
    metric_name: str
    time_series_data: List[Dict[str, Any]]
    trend_slope: float
    trend_direction: str
    correlation_factors: Dict[str, float] = field(default_factory=dict)
    forecasted_values: List[Dict[str, Any]] = field(default_factory=list)


class CollaborationAnalyticsEngine:
    """Advanced analytics engine for collaboration data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.analytics_cache = {}
        self.cache_duration = self.config.get('cache_duration_minutes', 30)
        
    async def generate_performance_analytics(
        self,
        collaboration_data: List[Dict[str, Any]],
        time_period: Dict[str, datetime] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive performance analytics"""



        try:
            if not collaboration_data:
                return self._empty_analytics_response("No collaboration data available")
            
            # Filter data by time period
            filtered_data = self._filter_by_time_period(collaboration_data, time_period)
            
            # Core performance metrics
            completion_metrics = self._calculate_completion_metrics(filtered_data)
            quality_metrics = self._calculate_quality_metrics(filtered_data)
            efficiency_metrics = self._calculate_efficiency_metrics(filtered_data)
            satisfaction_metrics = self._calculate_satisfaction_metrics(filtered_data)
            
            # Performance trends
            performance_trends = await self._analyze_performance_trends(filtered_data)
            
            # Comparative analysis
            comparative_analysis = self._generate_comparative_analysis(filtered_data)
            
            # Performance insights
            insights = self._generate_performance_insights(
                completion_metrics, quality_metrics, efficiency_metrics, 
                satisfaction_metrics, performance_trends
            )
            
            return {
                'summary': {
                    'total_collaborations': len(filtered_data),
                    'analysis_period': self._format_time_period(time_period),
                    'overall_performance_score': self._calculate_overall_performance_score(
                        completion_metrics, quality_metrics, efficiency_metrics, satisfaction_metrics
                    )
                },
                'completion_metrics': completion_metrics,
                'quality_metrics': quality_metrics,
                'efficiency_metrics': efficiency_metrics,
                'satisfaction_metrics': satisfaction_metrics,
                'performance_trends': performance_trends,
                'comparative_analysis': comparative_analysis,
                'insights': insights,
                'recommendations': self._generate_performance_recommendations(insights),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance analytics generation failed: {str(e)}")
            return {'error': str(e), 'success': False}
    
    async def generate_financial_analytics(
        self,
        collaboration_data: List[Dict[str, Any]],
        financial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive financial analytics"""



        try:
            if not collaboration_data:
                return self._empty_analytics_response("No collaboration data available")
            
            # Revenue analytics
            revenue_metrics = self._calculate_revenue_metrics(collaboration_data, financial_data)
            
            # Cost analytics
            cost_metrics = self._calculate_cost_metrics(collaboration_data, financial_data)
            
            # Profitability analytics
            profitability_metrics = self._calculate_profitability_metrics(
                revenue_metrics, cost_metrics
            )
            
            # ROI analytics
            roi_metrics = self._calculate_roi_metrics(collaboration_data, financial_data)
            
            # Financial trends
            financial_trends = await self._analyze_financial_trends(
                collaboration_data, financial_data
            )
            
            # Budget performance
            budget_performance = self._analyze_budget_performance(
                collaboration_data, financial_data
            )
            
            # Financial insights
            financial_insights = self._generate_financial_insights(
                revenue_metrics, cost_metrics, profitability_metrics, 
                roi_metrics, financial_trends
            )
            
            return {
                'summary': {
                    'total_revenue': revenue_metrics.get('total_revenue', 0),
                    'total_costs': cost_metrics.get('total_costs', 0),
                    'net_profit': profitability_metrics.get('net_profit', 0),
                    'average_roi': roi_metrics.get('average_roi', 0)
                },
                'revenue_metrics': revenue_metrics,
                'cost_metrics': cost_metrics,
                'profitability_metrics': profitability_metrics,
                'roi_metrics': roi_metrics,
                'financial_trends': financial_trends,
                'budget_performance': budget_performance,
                'insights': financial_insights,
                'recommendations': self._generate_financial_recommendations(financial_insights),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Financial analytics generation failed: {str(e)}")
            return {'error': str(e), 'success': False}
    
    async def generate_engagement_analytics(
        self,
        collaboration_data: List[Dict[str, Any]],
        engagement_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate engagement and interaction analytics"""



        try:
            # Communication analytics
            communication_metrics = self._analyze_communication_patterns(
                collaboration_data, engagement_data
            )
            
            # Response time analytics
            response_time_metrics = self._analyze_response_times(
                collaboration_data, engagement_data
            )
            
            # Interaction quality metrics
            interaction_quality = self._analyze_interaction_quality(
                collaboration_data, engagement_data
            )
            
            # Collaboration frequency analytics
            frequency_metrics = self._analyze_collaboration_frequency(collaboration_data)
            
            # Partner engagement analysis
            partner_engagement = self._analyze_partner_engagement(
                collaboration_data, engagement_data
            )
            
            # Engagement trends
            engagement_trends = await self._analyze_engagement_trends(
                collaboration_data, engagement_data
            )
            
            return {
                'summary': {
                    'total_interactions': communication_metrics.get('total_messages', 0),
                    'average_response_time': response_time_metrics.get('average_response_time', 0),
                    'engagement_score': interaction_quality.get('overall_engagement_score', 0)
                },
                'communication_metrics': communication_metrics,
                'response_time_metrics': response_time_metrics,
                'interaction_quality': interaction_quality,
                'frequency_metrics': frequency_metrics,
                'partner_engagement': partner_engagement,
                'engagement_trends': engagement_trends,
                'insights': self._generate_engagement_insights(
                    communication_metrics, response_time_metrics, interaction_quality
                ),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Engagement analytics generation failed: {str(e)}")
            return {'error': str(e), 'success': False}
    
    async def generate_predictive_analytics(
        self,
        historical_data: List[Dict[str, Any]],
        current_collaborations: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate predictive analytics and forecasts"""



        try:
            if len(historical_data) < 10:
                return {
                    'error': 'Insufficient historical data for predictions',
                    'minimum_required': 10,
                    'available_data_points': len(historical_data)
                }
            
            # Success probability predictions
            success_predictions = await self._predict_collaboration_success(
                historical_data, current_collaborations or []
            )
            
            # Revenue forecasting
            revenue_forecasts = await self._forecast_revenue_trends(historical_data)
            
            # Demand predictions
            demand_predictions = await self._predict_collaboration_demand(historical_data)
            
            # Market trend predictions
            market_trends = await self._predict_market_trends(historical_data)
            
            # Risk assessments
            risk_assessments = await self._assess_collaboration_risks(
                historical_data, current_collaborations or []
            )
            
            # Opportunity forecasting
            opportunity_forecasts = await self._forecast_opportunities(historical_data)
            
            return {
                'summary': {
                    'prediction_confidence': self._calculate_prediction_confidence(historical_data),
                    'forecast_horizon_days': 90,
                    'data_quality_score': self._assess_data_quality(historical_data)
                },
                'success_predictions': success_predictions,
                'revenue_forecasts': revenue_forecasts,
                'demand_predictions': demand_predictions,
                'market_trends': market_trends,
                'risk_assessments': risk_assessments,
                'opportunity_forecasts': opportunity_forecasts,
                'model_performance': self._get_model_performance_metrics(),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Predictive analytics generation failed: {str(e)}")
            return {'error': str(e), 'success': False}
    
    def _calculate_completion_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate collaboration completion metrics"""
        if not data:
            return {}
        
        total_collaborations = len(data)
        completed_collaborations = len([
            c for c in data if c.get('status') == 'completed'
        ])
        
        completion_rate = completed_collaborations / total_collaborations if total_collaborations > 0 else 0
        
        # On-time completion analysis
        on_time_completions = len([
            c for c in data 
            if c.get('status') == 'completed' and 
               c.get('completed_on_time', False)
        ])
        
        on_time_rate = on_time_completions / completed_collaborations if completed_collaborations > 0 else 0
        
        # Average completion time
        completion_times = [
            c.get('completion_days', 0) for c in data 
            if c.get('status') == 'completed' and c.get('completion_days', 0) > 0
        ]
        
        avg_completion_time = statistics.mean(completion_times) if completion_times else 0
        
        return {
            'total_collaborations': total_collaborations,
            'completed_collaborations': completed_collaborations,
            'completion_rate': completion_rate,
            'on_time_completions': on_time_completions,
            'on_time_rate': on_time_rate,
            'average_completion_time_days': avg_completion_time,
            'completion_time_variance': statistics.variance(completion_times) if len(completion_times) > 1 else 0
        }
    
    def _calculate_quality_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate collaboration quality metrics"""
        if not data:
            return {}
        
        # Quality scores
        quality_scores = [
            c.get('quality_score', 0) for c in data 
            if c.get('quality_score') is not None
        ]
        
        # Revision metrics
        revision_counts = [
            c.get('revision_count', 0) for c in data 
            if c.get('revision_count') is not None
        ]
        
        # Client feedback scores
        feedback_scores = [
            c.get('client_feedback_score', 0) for c in data 
            if c.get('client_feedback_score') is not None
        ]
        
        return {
            'average_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
            'quality_score_variance': statistics.variance(quality_scores) if len(quality_scores) > 1 else 0,
            'average_revision_count': statistics.mean(revision_counts) if revision_counts else 0,
            'low_revision_rate': len([r for r in revision_counts if r <= 1]) / len(revision_counts) if revision_counts else 0,
            'average_feedback_score': statistics.mean(feedback_scores) if feedback_scores else 0,
            'high_quality_rate': len([q for q in quality_scores if q >= 0.8]) / len(quality_scores) if quality_scores else 0
        }
    
    def _calculate_efficiency_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate collaboration efficiency metrics"""
        if not data:
            return {}
        
        # Time efficiency
        planned_durations = [
            c.get('planned_duration_days', 0) for c in data 
            if c.get('planned_duration_days', 0) > 0
        ]
        
        actual_durations = [
            c.get('actual_duration_days', 0) for c in data 
            if c.get('actual_duration_days', 0) > 0
        ]
        
        # Budget efficiency
        planned_budgets = [
            c.get('planned_budget', 0) for c in data 
            if c.get('planned_budget', 0) > 0
        ]
        
        actual_costs = [
            c.get('actual_cost', 0) for c in data 
            if c.get('actual_cost', 0) > 0
        ]
        
        # Calculate efficiency ratios
        time_efficiency_ratios = []
        budget_efficiency_ratios = []
        
        for i in range(min(len(planned_durations), len(actual_durations))):
            if planned_durations[i] > 0:
                ratio = actual_durations[i] / planned_durations[i]
                time_efficiency_ratios.append(ratio)
        
        for i in range(min(len(planned_budgets), len(actual_costs))):
            if planned_budgets[i] > 0:
                ratio = actual_costs[i] / planned_budgets[i]
                budget_efficiency_ratios.append(ratio)
        
        return {
            'average_time_efficiency': statistics.mean(time_efficiency_ratios) if time_efficiency_ratios else 1.0,
            'on_schedule_rate': len([r for r in time_efficiency_ratios if r <= 1.0]) / len(time_efficiency_ratios) if time_efficiency_ratios else 0,
            'average_budget_efficiency': statistics.mean(budget_efficiency_ratios) if budget_efficiency_ratios else 1.0,
            'under_budget_rate': len([r for r in budget_efficiency_ratios if r <= 1.0]) / len(budget_efficiency_ratios) if budget_efficiency_ratios else 0,
            'efficiency_trend': self._calculate_efficiency_trend(time_efficiency_ratios, budget_efficiency_ratios)
        }
    
    def _calculate_satisfaction_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate collaboration satisfaction metrics"""
        if not data:
            return {}
        
        # Overall satisfaction scores
        satisfaction_scores = [
            c.get('satisfaction_score', 0) for c in data 
            if c.get('satisfaction_score') is not None
        ]
        
        # Creator satisfaction
        creator_satisfaction = [
            c.get('creator_satisfaction', 0) for c in data 
            if c.get('creator_satisfaction') is not None
        ]
        
        # Partner satisfaction
        partner_satisfaction = [
            c.get('partner_satisfaction', 0) for c in data 
            if c.get('partner_satisfaction') is not None
        ]
        
        # Repeat collaboration indicators
        repeat_collaborations = len([
            c for c in data if c.get('is_repeat_collaboration', False)
        ])
        
        return {
            'average_satisfaction_score': statistics.mean(satisfaction_scores) if satisfaction_scores else 0,
            'satisfaction_variance': statistics.variance(satisfaction_scores) if len(satisfaction_scores) > 1 else 0,
            'high_satisfaction_rate': len([s for s in satisfaction_scores if s >= 0.8]) / len(satisfaction_scores) if satisfaction_scores else 0,
            'average_creator_satisfaction': statistics.mean(creator_satisfaction) if creator_satisfaction else 0,
            'average_partner_satisfaction': statistics.mean(partner_satisfaction) if partner_satisfaction else 0,
            'repeat_collaboration_rate': repeat_collaborations / len(data) if data else 0,
            'satisfaction_trend': self._calculate_satisfaction_trend(satisfaction_scores)
        }
    
    async def _analyze_performance_trends(self, data: List[Dict[str, Any]]) -> List[CollaborationTrendData]:
        """Analyze performance trends over time"""
        if not data:
            return []
        
        # Sort data by date
        sorted_data = sorted(data, key=lambda x: x.get('created_at', datetime.min))
        
        trends = []
        
        # Completion rate trend
        completion_trend = self._calculate_trend_data(
            sorted_data, 'completion_rate', 'Completion Rate Trend'
        )
        trends.append(completion_trend)
        
        # Quality score trend
        quality_trend = self._calculate_trend_data(
            sorted_data, 'quality_score', 'Quality Score Trend'
        )
        trends.append(quality_trend)
        
        # Satisfaction trend
        satisfaction_trend = self._calculate_trend_data(
            sorted_data, 'satisfaction_score', 'Satisfaction Score Trend'
        )
        trends.append(satisfaction_trend)
        
        return trends
    
    def _generate_performance_insights(self, *metrics_groups) -> List[AnalyticsInsight]:
        """Generate performance insights from metrics"""
        insights = []
        
        completion_metrics, quality_metrics, efficiency_metrics, satisfaction_metrics, trends = metrics_groups
        
        # Completion rate insight
        completion_rate = completion_metrics.get('completion_rate', 0)
        if completion_rate >= 0.9:
            insights.append(AnalyticsInsight(
                metric_type=AnalyticsMetric.PERFORMANCE,
                title="Excellent Completion Rate",
                description=f"Your collaboration completion rate of {completion_rate:.1%} is excellent",
                value=completion_rate,
                trend_direction="stable",
                confidence_score=0.95,
                actionable_recommendations=[
                    "Maintain current collaboration practices",
                    "Share best practices with other creators"
                ]
            ))
        elif completion_rate < 0.7:
            insights.append(AnalyticsInsight(
                metric_type=AnalyticsMetric.PERFORMANCE,
                title="Low Completion Rate Needs Attention",
                description=f"Your collaboration completion rate of {completion_rate:.1%} needs improvement",
                value=completion_rate,
                trend_direction="down",
                confidence_score=0.85,
                actionable_recommendations=[
                    "Review project scoping and planning processes",
                    "Improve communication with collaboration partners",
                    "Set more realistic timelines and expectations"
                ]
            ))
        
        # Quality insights
        avg_quality = quality_metrics.get('average_quality_score', 0)
        if avg_quality >= 0.85:
            insights.append(AnalyticsInsight(
                metric_type=AnalyticsMetric.QUALITY,
                title="High Quality Output",
                description=f"Your average quality score of {avg_quality:.2f} demonstrates excellence",
                value=avg_quality,
                trend_direction="up",
                confidence_score=0.9,
                actionable_recommendations=[
                    "Leverage quality as a competitive advantage",
                    "Consider premium pricing for high-quality work"
                ]
            ))
        
        # Efficiency insights
        time_efficiency = efficiency_metrics.get('average_time_efficiency', 1.0)
        if time_efficiency <= 0.9:  # Finishing ahead of schedule
            insights.append(AnalyticsInsight(
                metric_type=AnalyticsMetric.EFFICIENCY,
                title="Excellent Time Management",
                description=f"You consistently deliver ahead of schedule (efficiency: {time_efficiency:.2f})",
                value=time_efficiency,
                trend_direction="stable",
                confidence_score=0.88,
                actionable_recommendations=[
                    "Consider taking on more complex projects",
                    "Optimize pricing based on efficiency gains"
                ]
            ))
        
        return insights


class CollaborationReportGenerator:
    """Generate comprehensive collaboration reports"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.analytics_engine = CollaborationAnalyticsEngine(config)
    
    async def generate_comprehensive_report(
        self,
        creator_id: str,
        collaboration_data: List[Dict[str, Any]],
        report_type: str = "monthly",
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive collaboration report"""



        try:
            # Determine time period based on report type
            time_period = self._get_report_time_period(report_type)
            
            # Generate different types of analytics
            performance_analytics = await self.analytics_engine.generate_performance_analytics(
                collaboration_data, time_period
            )
            
            financial_analytics = await self.analytics_engine.generate_financial_analytics(
                collaboration_data
            )
            
            engagement_analytics = await self.analytics_engine.generate_engagement_analytics(
                collaboration_data
            )
            
            # Generate predictions if requested
            predictive_analytics = {}
            if include_predictions and len(collaboration_data) >= 10:
                predictive_analytics = await self.analytics_engine.generate_predictive_analytics(
                    collaboration_data
                )
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                performance_analytics, financial_analytics, engagement_analytics, predictive_analytics
            )
            
            # Generate actionable insights
            actionable_insights = self._compile_actionable_insights(
                performance_analytics, financial_analytics, engagement_analytics, predictive_analytics
            )
            
            return {
                'report_metadata': {
                    'creator_id': creator_id,
                    'report_type': report_type,
                    'time_period': time_period,
                    'generated_at': datetime.utcnow().isoformat(),
                    'data_points_analyzed': len(collaboration_data),
                    'includes_predictions': include_predictions
                },
                'executive_summary': executive_summary,
                'performance_analytics': performance_analytics,
                'financial_analytics': financial_analytics,
                'engagement_analytics': engagement_analytics,
                'predictive_analytics': predictive_analytics,
                'actionable_insights': actionable_insights,
                'report_version': '1.0'
            }
            
        except Exception as e:
            logger.error(f"Report generation failed for creator {creator_id}: {str(e)}")
            return {'error': str(e), 'success': False}
    
    def _generate_executive_summary(self, *analytics_data) -> Dict[str, Any]:
        """Generate executive summary from analytics data"""
        performance, financial, engagement, predictive = analytics_data
        
        # Extract key metrics
        key_metrics = {
            'completion_rate': performance.get('completion_metrics', {}).get('completion_rate', 0),
            'total_revenue': financial.get('summary', {}).get('total_revenue', 0),
            'average_satisfaction': performance.get('satisfaction_metrics', {}).get('average_satisfaction_score', 0),
            'engagement_score': engagement.get('summary', {}).get('engagement_score', 0)
        }
        
        # Generate summary insights
        summary_insights = []
        
        if key_metrics['completion_rate'] >= 0.9:
            summary_insights.append("Excellent collaboration completion rate demonstrates strong project management skills")
        
        if key_metrics['total_revenue'] > 0:
            summary_insights.append(f"Generated ${key_metrics['total_revenue']:,.2f} in collaboration revenue")
        
        if key_metrics['average_satisfaction'] >= 0.8:
            summary_insights.append("High client satisfaction scores indicate quality service delivery")
        
        return {
            'key_metrics': key_metrics,
            'summary_insights': summary_insights,
            'overall_performance_grade': self._calculate_performance_grade(key_metrics),
            'primary_strengths': self._identify_primary_strengths(performance, financial, engagement),
            'improvement_opportunities': self._identify_improvement_opportunities(performance, financial, engagement)
        }


# Export all analytics components
__all__ = [
    'AnalyticsMetric',
    'AnalyticsInsight', 
    'CollaborationTrendData',
    'CollaborationAnalyticsEngine',
    'CollaborationReportGenerator'
]
