"""
📈 Business Metrics Tracker - ML Impact & ROI Analytics Module

Advanced business impact tracking system that measures ML model performance
against revenue, engagement, and business KPIs on the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Version: 1.0.0
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path
import redis
import asyncpg
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import concurrent.futures
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

@dataclass
class BusinessMetric:
    """Definition of a business metric"""
    name: str
    metric_type: str  # 'revenue', 'engagement', 'conversion', 'retention', 'growth'
    unit: str
    aggregation_method: str  # 'sum', 'mean', 'median', 'count', 'rate'
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    is_kpi: bool = False

@dataclass
class MLImpactAssessment:
    """ML model impact on business metrics"""
    model_id: str
    metric_name: str
    baseline_value: float
    current_value: float
    improvement_pct: float
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    attribution_score: float  # How much improvement is attributable to ML
    business_value: float  # Monetary value of improvement

@dataclass
class ROIAnalysis:
    """Return on Investment analysis for ML initiatives"""
    model_id: str
    implementation_cost: float
    operational_cost_monthly: float
    revenue_impact_monthly: float
    cost_savings_monthly: float
    roi_percentage: float
    payback_period_months: float
    net_present_value: float
    business_case_strength: str  # 'strong', 'moderate', 'weak'

class BusinessMetricsTracker:
    """
    📈 Advanced Business Impact & ROI Tracking System
    
    Measures ML model performance against business KPIs, calculates ROI,
    and provides actionable insights for business stakeholders.
    """
    
    def __init__(self,
                 redis_host -> None: str = "localhost",
                 redis_port -> None: int = 6379,
                 db_host -> None: str = "localhost",
                 db_port -> None: int = 5432,
                 db_name -> None: str = "ainflue_business") -> None:
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis for caching
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
        except:
            self.logger.warning("Redis not available, using memory cache")
            self.redis_client = None
        
        # Database connection details
        self.db_config = {
            'host': db_host,
            'port': db_port,
            'database': db_name
        }
        
        # Business metrics configuration for Ainflue platform
        self.business_metrics_config = {
            'revenue_metrics': [
                BusinessMetric('monthly_revenue', 'revenue', 'USD', 'sum', is_kpi=True),
                BusinessMetric('revenue_per_creator', 'revenue', 'USD', 'mean', is_kpi=True),
                BusinessMetric('subscription_revenue', 'revenue', 'USD', 'sum'),
                BusinessMetric('commission_revenue', 'revenue', 'USD', 'sum'),
                BusinessMetric('advertising_revenue', 'revenue', 'USD', 'sum')
            ],
            'engagement_metrics': [
                BusinessMetric('platform_engagement_rate', 'engagement', 'percentage', 'mean', is_kpi=True),
                BusinessMetric('content_interaction_rate', 'engagement', 'percentage', 'mean'),
                BusinessMetric('daily_active_users', 'engagement', 'count', 'mean', is_kpi=True),
                BusinessMetric('session_duration', 'engagement', 'minutes', 'mean'),
                BusinessMetric('content_completion_rate', 'engagement', 'percentage', 'mean')
            ],
            'conversion_metrics': [
                BusinessMetric('creator_conversion_rate', 'conversion', 'percentage', 'mean', is_kpi=True),
                BusinessMetric('subscription_conversion_rate', 'conversion', 'percentage', 'mean'),
                BusinessMetric('collaboration_success_rate', 'conversion', 'percentage', 'mean'),
                BusinessMetric('monetization_activation_rate', 'conversion', 'percentage', 'mean')
            ],
            'retention_metrics': [
                BusinessMetric('creator_retention_rate', 'retention', 'percentage', 'mean', is_kpi=True),
                BusinessMetric('audience_retention_rate', 'retention', 'percentage', 'mean'),
                BusinessMetric('churn_rate', 'retention', 'percentage', 'mean'),
                BusinessMetric('lifetime_value', 'retention', 'USD', 'mean')
            ],
            'growth_metrics': [
                BusinessMetric('new_creator_growth', 'growth', 'count', 'sum', is_kpi=True),
                BusinessMetric('platform_growth_rate', 'growth', 'percentage', 'mean'),
                BusinessMetric('market_share_growth', 'growth', 'percentage', 'mean'),
                BusinessMetric('content_volume_growth', 'growth', 'percentage', 'mean')
            ]
        }
        
        # ML model mappings to business outcomes
        self.ml_business_mappings = {
            'content_recommendation': ['platform_engagement_rate', 'session_duration', 'content_completion_rate'],
            'creator_matching': ['collaboration_success_rate', 'creator_retention_rate'],
            'fraud_detection': ['commission_revenue', 'creator_conversion_rate'],
            'content_moderation': ['platform_engagement_rate', 'creator_retention_rate'],
            'personalization': ['daily_active_users', 'session_duration', 'subscription_conversion_rate'],
            'pricing_optimization': ['subscription_revenue', 'revenue_per_creator'],
            'trend_prediction': ['content_interaction_rate', 'monetization_activation_rate']
        }
        
        # Performance tracking
        self.tracking_metrics = {
            'total_assessments': 0,
            'avg_roi_calculated': 0.0,
            'high_impact_models': 0,
            'business_value_generated': 0.0
        }
    
    async def track_business_impact(self,
                                  model_id: str,
                                  time_period_days: int = 30,
                                  comparison_period_days: int = 30) -> Dict[str, Any]:
        """
        📊 Track comprehensive business impact of ML model
        
        Args:
            model_id: ML model identifier
            time_period_days: Current period to analyze
            comparison_period_days: Baseline period for comparison
            
        Returns:
            Comprehensive business impact analysis
        """
        start_time = datetime.now()
        
        try:
            # Generate cache key
            cache_key = f"business_impact:{model_id}:{time_period_days}:{comparison_period_days}"
            
            # Check cache
            if self.redis_client:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
            
            # Get relevant business metrics for this model
            relevant_metrics = self._get_relevant_metrics(model_id)
            
            # Parallel data collection
            data_tasks = [
                self._collect_metric_data(metric, time_period_days, 'current'),
                self._collect_metric_data(metric, comparison_period_days, 'baseline'),
                self._collect_model_deployment_data(model_id),
                self._collect_external_factors_data(time_period_days)
            ]
            
            current_data, baseline_data, model_data, external_factors = await asyncio.gather(*data_tasks)
            
            # Calculate impact assessments
            impact_assessments = []
            for metric in relevant_metrics:
                assessment = await self._assess_ml_impact(
                    model_id, metric, current_data, baseline_data, model_data, external_factors
                )
                impact_assessments.append(assessment)
            
            # Calculate ROI
            roi_analysis = await self._calculate_roi(model_id, impact_assessments, model_data)
            
            # Generate business insights
            business_insights = await self._generate_business_insights(
                impact_assessments, roi_analysis, model_id
            )
            
            # Create comprehensive report
            impact_report = {
                'model_id': model_id,
                'analysis_period': {
                    'current_period_days': time_period_days,
                    'baseline_period_days': comparison_period_days,
                    'analysis_date': datetime.now().isoformat()
                },
                'impact_assessments': [asdict(assessment) for assessment in impact_assessments],
                'roi_analysis': asdict(roi_analysis),
                'business_insights': business_insights,
                'key_findings': await self._extract_key_findings(impact_assessments, roi_analysis),
                'recommendations': await self._generate_recommendations(impact_assessments, roi_analysis),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            
            # Cache results
            if self.redis_client:
                self.redis_client.setex(
                    cache_key,
                    3600,  # 1 hour TTL
                    json.dumps(impact_report, default=str)
                )
            
            # Update tracking metrics
            self._update_tracking_metrics(impact_report)
            
            return impact_report
            
        except Exception as e:
            self.logger.error(f"❌ Business impact tracking failed: {e}")
            raise
    
    async def _assess_ml_impact(self,
                              model_id: str,
                              metric: BusinessMetric,
                              current_data: Dict,
                              baseline_data: Dict,
                              model_data: Dict,
                              external_factors: Dict) -> MLImpactAssessment:
        """Assess ML model impact on specific business metric"""
        
        # Extract metric values
        current_value = current_data.get(metric.name, 0.0)
        baseline_value = baseline_data.get(metric.name, 0.0)
        
        # Calculate raw improvement
        if baseline_value != 0:
            improvement_pct = ((current_value - baseline_value) / baseline_value) * 100
        else:
            improvement_pct = 0.0
        
        # Calculate statistical significance
        statistical_significance = await self._calculate_statistical_significance(
            current_data.get(f"{metric.name}_samples", []),
            baseline_data.get(f"{metric.name}_samples", [])
        )
        
        # Calculate confidence interval
        confidence_interval = await self._calculate_confidence_interval(
            current_value, baseline_value, 
            current_data.get(f"{metric.name}_std", 0),
            baseline_data.get(f"{metric.name}_std", 0)
        )
        
        # Calculate attribution score (how much improvement is due to ML)
        attribution_score = await self._calculate_attribution_score(
            model_id, metric.name, improvement_pct, external_factors, model_data
        )
        
        # Calculate business value
        business_value = await self._calculate_business_value(
            metric, improvement_pct, attribution_score, current_value
        )
        
        return MLImpactAssessment(
            model_id=model_id,
            metric_name=metric.name,
            baseline_value=baseline_value,
            current_value=current_value,
            improvement_pct=improvement_pct,
            statistical_significance=statistical_significance,
            confidence_interval=confidence_interval,
            attribution_score=attribution_score,
            business_value=business_value
        )
    
    async def _calculate_roi(self,
                           model_id: str,
                           impact_assessments: List[MLImpactAssessment],
                           model_data: Dict) -> ROIAnalysis:
        """Calculate comprehensive ROI for ML model"""
        
        # Sum up business value from all impact assessments
        total_business_value_monthly = sum(
            assessment.business_value * assessment.attribution_score 
            for assessment in impact_assessments
        )
        
        # Get model costs
        implementation_cost = model_data.get('implementation_cost', 50000)  # Default estimate
        operational_cost_monthly = model_data.get('operational_cost_monthly', 5000)  # Default estimate
        
        # Separate revenue impact and cost savings
        revenue_impact_monthly = sum(
            assessment.business_value * assessment.attribution_score
            for assessment in impact_assessments
            if assessment.metric_name in ['monthly_revenue', 'revenue_per_creator', 'subscription_revenue']
        )
        
        cost_savings_monthly = total_business_value_monthly - revenue_impact_monthly
        
        # Calculate ROI percentage
        monthly_net_benefit = revenue_impact_monthly + cost_savings_monthly - operational_cost_monthly
        annual_net_benefit = monthly_net_benefit * 12
        
        if implementation_cost > 0:
            roi_percentage = (annual_net_benefit / implementation_cost) * 100
        else:
            roi_percentage = float('inf') if annual_net_benefit > 0 else 0
        
        # Calculate payback period
        if monthly_net_benefit > 0:
            payback_period_months = implementation_cost / monthly_net_benefit
        else:
            payback_period_months = float('inf')
        
        # Calculate NPV (assuming 10% discount rate)
        discount_rate = 0.10
        periods = 24  # 2 years
        npv = -implementation_cost
        for period in range(1, periods + 1):
            npv += monthly_net_benefit / ((1 + discount_rate/12) ** period)
        
        # Determine business case strength
        if roi_percentage > 200 and payback_period_months < 12:
            business_case_strength = 'strong'
        elif roi_percentage > 100 and payback_period_months < 18:
            business_case_strength = 'moderate'
        else:
            business_case_strength = 'weak'
        
        return ROIAnalysis(
            model_id=model_id,
            implementation_cost=implementation_cost,
            operational_cost_monthly=operational_cost_monthly,
            revenue_impact_monthly=revenue_impact_monthly,
            cost_savings_monthly=cost_savings_monthly,
            roi_percentage=roi_percentage,
            payback_period_months=payback_period_months,
            net_present_value=npv,
            business_case_strength=business_case_strength
        )
    
    async def generate_executive_dashboard(self,
                                         time_period_days: int = 30) -> Dict[str, Any]:
        """Generate executive dashboard with key business metrics and ML impact"""
        
        # Get all active ML models
        active_models = await self._get_active_models()
        
        # Collect high-level business metrics
        kpi_metrics = [metric for category in self.business_metrics_config.values() 
                      for metric in category if metric.is_kpi]
        
        dashboard_data = {
            'overview': {
                'total_active_models': len(active_models),
                'total_business_value_generated': 0.0,
                'average_roi': 0.0,
                'high_impact_models': 0
            },
            'kpi_performance': {},
            'model_performance': [],
            'trend_analysis': {},
            'alerts_and_recommendations': []
        }
        
        # Analyze each KPI metric
        for metric in kpi_metrics:
            kpi_data = await self._analyze_kpi_performance(metric, time_period_days)
            dashboard_data['kpi_performance'][metric.name] = kpi_data
        
        # Analyze model performance
        for model_id in active_models:
            model_impact = await self.track_business_impact(model_id, time_period_days)
            dashboard_data['model_performance'].append({
                'model_id': model_id,
                'roi_percentage': model_impact['roi_analysis']['roi_percentage'],
                'business_value': sum(
                    assessment['business_value'] 
                    for assessment in model_impact['impact_assessments']
                ),
                'status': 'performing' if model_impact['roi_analysis']['roi_percentage'] > 50 else 'underperforming'
            })
            
            # Update overview metrics
            dashboard_data['overview']['total_business_value_generated'] += sum(
                assessment['business_value'] for assessment in model_impact['impact_assessments']
            )
            if model_impact['roi_analysis']['roi_percentage'] > 100:
                dashboard_data['overview']['high_impact_models'] += 1
        
        # Calculate averages
        if len(active_models) > 0:
            dashboard_data['overview']['average_roi'] = np.mean([
                model['roi_percentage'] for model in dashboard_data['model_performance']
            ])
        
        # Generate trend analysis
        dashboard_data['trend_analysis'] = await self._analyze_business_trends(time_period_days)
        
        # Generate alerts and recommendations
        dashboard_data['alerts_and_recommendations'] = await self._generate_executive_alerts(
            dashboard_data
        )
        
        return dashboard_data
    
    async def track_creator_specific_metrics(self,
                                           creator_type: str,
                                           creator_id: Optional[str] = None,
                                           time_period_days: int = 30) -> Dict[str, Any]:
        """Track business metrics specific to creator types"""
        
        creator_metrics_map = {
            'musician': ['streaming_revenue', 'collaboration_rate', 'fan_engagement'],
            'blogger': ['content_monetization', 'seo_performance', 'reader_retention'],
            'photographer': ['licensing_revenue', 'portfolio_views', 'client_acquisition'],
            'influencer': ['brand_partnership_value', 'audience_growth', 'engagement_rate']
        }
        
        relevant_metrics = creator_metrics_map.get(creator_type, [])
        
        # Collect creator-specific data
        creator_data = await self._collect_creator_metrics(
            creator_type, creator_id, relevant_metrics, time_period_days
        )
        
        # Analyze ML impact on creator metrics
        ml_impact_analysis = await self._analyze_creator_ml_impact(
            creator_type, creator_data, time_period_days
        )
        
        return {
            'creator_type': creator_type,
            'creator_id': creator_id,
            'metrics_summary': creator_data,
            'ml_impact_analysis': ml_impact_analysis,
            'optimization_opportunities': await self._identify_creator_optimization_opportunities(
                creator_type, creator_data, ml_impact_analysis
            )
        }
    
    def _get_relevant_metrics(self, model_id: str) -> List[BusinessMetric]:
        """Get business metrics relevant to specific ML model"""
        
        # Determine model type based on model_id
        model_type = self._determine_model_type(model_id)
        
        # Get relevant metric names
        relevant_metric_names = self.ml_business_mappings.get(model_type, [])
        
        # Find metric objects
        relevant_metrics = []
        for category in self.business_metrics_config.values():
            for metric in category:
                if metric.name in relevant_metric_names:
                    relevant_metrics.append(metric)
        
        return relevant_metrics
    
    def _determine_model_type(self, model_id: str) -> str:
        """Determine model type from model ID"""
        # Simple heuristic based on model_id naming
        if 'recommend' in model_id.lower():
            return 'content_recommendation'
        elif 'match' in model_id.lower():
            return 'creator_matching'
        elif 'fraud' in model_id.lower():
            return 'fraud_detection'
        elif 'moderat' in model_id.lower():
            return 'content_moderation'
        elif 'personal' in model_id.lower():
            return 'personalization'
        elif 'pric' in model_id.lower():
            return 'pricing_optimization'
        elif 'trend' in model_id.lower():
            return 'trend_prediction'
        else:
            return 'content_recommendation'  # Default
    
    async def _collect_metric_data(self, metric: BusinessMetric, days: int, period_type: str) -> Dict:
        """Collect metric data from database"""
        # Simulated data collection - in production, this would query the database
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Generate simulated metric data
        base_value = {
            'monthly_revenue': 1000000,
            'revenue_per_creator': 2500,
            'platform_engagement_rate': 0.15,
            'daily_active_users': 50000,
            'creator_conversion_rate': 0.08,
            'creator_retention_rate': 0.85,
            'new_creator_growth': 500
        }.get(metric.name, 1000)
        
        # Add some variation
        variation = np.random.normal(0, 0.1)
        current_value = base_value * (1 + variation)
        
        return {
            metric.name: current_value,
            f"{metric.name}_samples": np.random.normal(current_value, current_value * 0.05, days),
            f"{metric.name}_std": current_value * 0.05
        }
    
    def _update_tracking_metrics(self, impact_report -> None: Dict) -> None:
        """Update tracking performance metrics"""
        self.tracking_metrics['total_assessments'] += 1
        
        # Update ROI average
        roi_value = impact_report['roi_analysis']['roi_percentage']
        total = self.tracking_metrics['total_assessments']
        self.tracking_metrics['avg_roi_calculated'] = (
            (self.tracking_metrics['avg_roi_calculated'] * (total - 1) + roi_value) / total
        )
        
        # Count high impact models
        if roi_value > 100:
            self.tracking_metrics['high_impact_models'] += 1
        
        # Sum business value
        total_value = sum(
            assessment['business_value'] 
            for assessment in impact_report['impact_assessments']
        )
        self.tracking_metrics['business_value_generated'] += total_value
    
    async def get_tracking_metrics(self) -> Dict[str, Any]:
        """Get business tracking performance metrics"""
        return {
            **self.tracking_metrics,
            'supported_model_types': list(self.ml_business_mappings.keys()),
            'tracked_metric_categories': list(self.business_metrics_config.keys()),
            'cache_status': 'active' if self.redis_client else 'disabled'
        }

# Example usage and integration
if __name__ == "__main__":
    async def main() -> None:
        # Initialize tracker
        tracker = BusinessMetricsTracker()
        
        print("📈 Business Metrics Tracker - Ready for Impact Analysis")
        
        # Example business impact tracking
        try:
            impact_report = await tracker.track_business_impact(
                model_id="content_recommender_v2",
                time_period_days=30
            )
            
            print(f"✅ Impact analysis completed in {impact_report['processing_time']:.2f}s")
            print(f"💰 ROI: {impact_report['roi_analysis']['roi_percentage']:.1f}%")
            print(f"📊 Business Value: ${sum(a['business_value'] for a in impact_report['impact_assessments']):,.0f}")
            
            # Generate executive dashboard
            dashboard = await tracker.generate_executive_dashboard()
            print(f"📋 Executive Dashboard: {dashboard['overview']['total_active_models']} active models")
            
        except Exception as e:
            print(f"❌ Tracking failed: {e}")
        
        # Get tracking metrics
        metrics = await tracker.get_tracking_metrics()
        print(f"📈 Tracker Metrics: {metrics}")

    if __name__ == "__main__":
        asyncio.run(main())