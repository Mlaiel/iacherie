"""
Enterprise ROI Calculator for ML Investments
ML Engineer + Backend Senior implementation with business impact analysis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import uuid
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


class ROIMetricType(Enum):
    """Types of ROI metrics"""
    REVENUE_INCREASE = "revenue_increase"
    COST_REDUCTION = "cost_reduction"
    EFFICIENCY_GAIN = "efficiency_gain"
    USER_ENGAGEMENT = "user_engagement"
    CREATOR_SATISFACTION = "creator_satisfaction"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"


class InvestmentCategory(Enum):
    """ML investment categories"""
    MODEL_DEVELOPMENT = "model_development"
    INFRASTRUCTURE = "infrastructure"
    DATA_ACQUISITION = "data_acquisition"
    TALENT_ACQUISITION = "talent_acquisition"
    TOOLS_AND_PLATFORMS = "tools_and_platforms"
    MAINTENANCE = "maintenance"


class TimeFrame(Enum):
    """Time frames for ROI calculation"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class MLInvestment:
    """ML investment record"""
    investment_id: str
    name: str
    category: InvestmentCategory
    amount: float
    start_date: datetime
    expected_duration: timedelta
    description: str = ""
    creator_types_affected: List[str] = field(default_factory=list)
    expected_roi_percentage: float = 0.0
    risk_level: str = "medium"


@dataclass
class ROIBenefit:
    """ROI benefit measurement"""
    benefit_id: str
    investment_id: str
    metric_type: ROIMetricType
    baseline_value: float
    current_value: float
    improvement_percentage: float
    monetary_value: float
    measurement_date: datetime
    creator_type: Optional[str] = None
    confidence_level: float = 0.0


@dataclass
class ROIReport:
    """Comprehensive ROI report"""
    report_id: str
    investment_id: str
    time_frame: TimeFrame
    total_investment: float
    total_benefits: float
    net_roi: float
    roi_percentage: float
    payback_period: timedelta
    benefits_breakdown: Dict[ROIMetricType, float]
    creator_impact: Dict[str, Dict[str, float]]
    confidence_score: float
    generation_date: datetime = field(default_factory=datetime.utcnow)


class ROICalculator:
    """Enterprise ROI calculator for ML investments"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.investments: Dict[str, MLInvestment] = {}
        self.benefits: List[ROIBenefit] = []
        self.roi_reports: List[ROIReport] = []
        
        # Creator value metrics (average revenue per creator per month)
        self.creator_value_metrics = {
            'musicians': {
                'avg_monthly_revenue': 2500.0,
                'engagement_value': 150.0,
                'collaboration_value': 500.0,
                'retention_value': 1200.0
            },
            'photographers': {
                'avg_monthly_revenue': 3200.0,
                'engagement_value': 200.0,
                'portfolio_value': 800.0,
                'retention_value': 1500.0
            },
            'bloggers': {
                'avg_monthly_revenue': 1800.0,
                'engagement_value': 120.0,
                'content_value': 300.0,
                'retention_value': 900.0
            },
            'influencers': {
                'avg_monthly_revenue': 4500.0,
                'engagement_value': 300.0,
                'brand_partnership_value': 2000.0,
                'retention_value': 2200.0
            },
            'comedians': {
                'avg_monthly_revenue': 2800.0,
                'engagement_value': 180.0,
                'performance_value': 600.0,
                'retention_value': 1100.0
            }
        }
        
        # Business impact weights
        self.impact_weights = {
            ROIMetricType.REVENUE_INCREASE: 1.0,
            ROIMetricType.COST_REDUCTION: 0.9,
            ROIMetricType.EFFICIENCY_GAIN: 0.7,
            ROIMetricType.USER_ENGAGEMENT: 0.6,
            ROIMetricType.CREATOR_SATISFACTION: 0.5,
            ROIMetricType.OPERATIONAL_EFFICIENCY: 0.4
        }
        
    async def initialize(self) -> bool:
        """Initialize ROI calculator"""
        try:
            logger.info("Initializing ROI Calculator...")
            
            # Setup baseline measurements
            await self._setup_baseline_measurements()
            
            # Initialize tracking systems
            await self._setup_tracking_systems()
            
            logger.info("ROI Calculator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ROI Calculator: {e}")
            return False
    
    async def record_investment(self, investment: MLInvestment) -> bool:
        """Record new ML investment"""
        try:
            self.investments[investment.investment_id] = investment
            
            logger.info(f"Recorded investment: {investment.name} - ${investment.amount:,.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record investment: {e}")
            return False
    
    async def record_benefit(self, benefit: ROIBenefit) -> bool:
        """Record benefit from ML investment"""
        try:
            self.benefits.append(benefit)
            
            logger.info(f"Recorded benefit: {benefit.metric_type.value} - ${benefit.monetary_value:,.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record benefit: {e}")
            return False
    
    async def calculate_roi(self, 
                          investment_id: str,
                          time_frame: TimeFrame = TimeFrame.MONTHLY,
                          include_projections: bool = True) -> Optional[ROIReport]:
        """Calculate ROI for specific investment"""
        try:
            if investment_id not in self.investments:
                logger.error(f"Investment {investment_id} not found")
                return None
            
            investment = self.investments[investment_id]
            
            # Get benefits for this investment
            investment_benefits = [
                b for b in self.benefits 
                if b.investment_id == investment_id
            ]
            
            if not investment_benefits:
                logger.warning(f"No benefits recorded for investment {investment_id}")
                return None
            
            # Calculate total benefits
            total_benefits = await self._calculate_total_benefits(investment_benefits)
            
            # Calculate ROI metrics
            net_roi = total_benefits - investment.amount
            roi_percentage = (net_roi / investment.amount) * 100
            
            # Calculate payback period
            payback_period = await self._calculate_payback_period(investment, investment_benefits)
            
            # Benefits breakdown
            benefits_breakdown = await self._calculate_benefits_breakdown(investment_benefits)
            
            # Creator impact analysis
            creator_impact = await self._analyze_creator_impact(investment_benefits)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(investment_benefits)
            
            # Include projections if requested
            if include_projections:
                projected_benefits = await self._project_future_benefits(investment, investment_benefits)
                total_benefits += projected_benefits
                net_roi = total_benefits - investment.amount
                roi_percentage = (net_roi / investment.amount) * 100
            
            report = ROIReport(
                report_id=str(uuid.uuid4()),
                investment_id=investment_id,
                time_frame=time_frame,
                total_investment=investment.amount,
                total_benefits=total_benefits,
                net_roi=net_roi,
                roi_percentage=roi_percentage,
                payback_period=payback_period,
                benefits_breakdown=benefits_breakdown,
                creator_impact=creator_impact,
                confidence_score=confidence_score
            )
            
            self.roi_reports.append(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to calculate ROI: {e}")
            return None
    
    async def get_portfolio_roi(self, time_period: Optional[timedelta] = None) -> Dict[str, Any]:
        """Calculate ROI for entire ML investment portfolio"""
        try:
            if time_period:
                cutoff_date = datetime.utcnow() - time_period
                relevant_investments = {
                    k: v for k, v in self.investments.items()
                    if v.start_date >= cutoff_date
                }
            else:
                relevant_investments = self.investments
            
            portfolio_analysis = {
                'total_investments': len(relevant_investments),
                'total_invested': 0.0,
                'total_benefits': 0.0,
                'average_roi': 0.0,
                'best_performing': None,
                'worst_performing': None,
                'by_category': {},
                'by_creator_type': {},
                'risk_analysis': {},
                'recommendations': []
            }
            
            roi_values = []
            
            for investment_id in relevant_investments:
                roi_report = await self.calculate_roi(investment_id, include_projections=False)
                if roi_report:
                    portfolio_analysis['total_invested'] += roi_report.total_investment
                    portfolio_analysis['total_benefits'] += roi_report.total_benefits
                    roi_values.append(roi_report.roi_percentage)
                    
                    # Track best and worst performing
                    if (not portfolio_analysis['best_performing'] or 
                        roi_report.roi_percentage > portfolio_analysis['best_performing']['roi']):
                        portfolio_analysis['best_performing'] = {
                            'investment_id': investment_id,
                            'roi': roi_report.roi_percentage,
                            'name': relevant_investments[investment_id].name
                        }
                    
                    if (not portfolio_analysis['worst_performing'] or 
                        roi_report.roi_percentage < portfolio_analysis['worst_performing']['roi']):
                        portfolio_analysis['worst_performing'] = {
                            'investment_id': investment_id,
                            'roi': roi_report.roi_percentage,
                            'name': relevant_investments[investment_id].name
                        }
            
            # Calculate portfolio metrics
            if roi_values:
                portfolio_analysis['average_roi'] = statistics.mean(roi_values)
                portfolio_analysis['roi_std_dev'] = statistics.stdev(roi_values) if len(roi_values) > 1 else 0
            
            # Category analysis
            portfolio_analysis['by_category'] = await self._analyze_by_category(relevant_investments)
            
            # Creator type analysis
            portfolio_analysis['by_creator_type'] = await self._analyze_by_creator_type(relevant_investments)
            
            # Generate recommendations
            portfolio_analysis['recommendations'] = await self._generate_portfolio_recommendations(
                portfolio_analysis
            )
            
            return portfolio_analysis
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio ROI: {e}")
            return {}
    
    async def predict_roi(self, 
                        investment: MLInvestment,
                        prediction_horizon: timedelta = timedelta(days=365)) -> Dict[str, Any]:
        """Predict ROI for proposed investment"""
        try:
            # Use historical data to predict ROI
            historical_data = await self._get_historical_performance_data(investment.category)
            
            # Calculate baseline prediction
            base_prediction = await self._calculate_base_prediction(investment, historical_data)
            
            # Apply creator-specific adjustments
            creator_adjustments = await self._apply_creator_adjustments(investment, base_prediction)
            
            # Risk adjustment
            risk_adjusted_prediction = await self._apply_risk_adjustment(
                investment, creator_adjustments
            )
            
            prediction = {
                'investment': investment.amount,
                'predicted_benefits': risk_adjusted_prediction['benefits'],
                'predicted_roi_percentage': risk_adjusted_prediction['roi_percentage'],
                'confidence_interval': risk_adjusted_prediction['confidence_interval'],
                'payback_period_estimate': risk_adjusted_prediction['payback_period'],
                'risk_factors': risk_adjusted_prediction['risk_factors'],
                'recommendation': risk_adjusted_prediction['recommendation'],
                'creator_impact_prediction': risk_adjusted_prediction['creator_impact']
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to predict ROI: {e}")
            return {}
    
    async def get_roi_trends(self, time_period: timedelta = timedelta(days=365)) -> Dict[str, Any]:
        """Analyze ROI trends over time"""
        try:
            cutoff_date = datetime.utcnow() - time_period
            
            # Get reports within time period
            relevant_reports = [
                r for r in self.roi_reports
                if r.generation_date >= cutoff_date
            ]
            
            if not relevant_reports:
                return {'message': 'No ROI data available for the specified period'}
            
            # Analyze trends
            trends = {
                'overall_trend': await self._calculate_overall_trend(relevant_reports),
                'category_trends': await self._calculate_category_trends(relevant_reports),
                'creator_type_trends': await self._calculate_creator_type_trends(relevant_reports),
                'seasonal_patterns': await self._identify_seasonal_patterns(relevant_reports),
                'improvement_areas': await self._identify_improvement_areas(relevant_reports)
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze ROI trends: {e}")
            return {}
    
    async def _setup_baseline_measurements(self) -> None:
        """Setup baseline measurements for ROI calculation"""
        # Initialize baseline metrics for each creator type
        for creator_type in self.creator_value_metrics:
            # Record baseline measurements
            pass
    
    async def _setup_tracking_systems(self) -> None:
        """Setup systems for tracking benefits and investments"""
        # Initialize tracking infrastructure
        pass
    
    async def _calculate_total_benefits(self, benefits: List[ROIBenefit]) -> float:
        """Calculate total monetary benefits"""
        total = 0.0
        
        for benefit in benefits:
            # Apply confidence weighting
            weighted_value = benefit.monetary_value * benefit.confidence_level
            
            # Apply metric type weighting
            metric_weight = self.impact_weights.get(benefit.metric_type, 1.0)
            weighted_value *= metric_weight
            
            total += weighted_value
        
        return total
    
    async def _calculate_payback_period(self, 
                                     investment: MLInvestment,
                                     benefits: List[ROIBenefit]) -> timedelta:
        """Calculate investment payback period"""
        if not benefits:
            return timedelta(days=365 * 10)  # Default to 10 years if no benefits
        
        # Sort benefits by date
        sorted_benefits = sorted(benefits, key=lambda x: x.measurement_date)
        
        cumulative_benefits = 0.0
        start_date = investment.start_date
        
        for benefit in sorted_benefits:
            cumulative_benefits += benefit.monetary_value
            if cumulative_benefits >= investment.amount:
                return benefit.measurement_date - start_date
        
        # Estimate based on current rate
        if cumulative_benefits > 0:
            days_elapsed = (datetime.utcnow() - start_date).days
            daily_benefit_rate = cumulative_benefits / max(days_elapsed, 1)
            remaining_amount = investment.amount - cumulative_benefits
            estimated_days = remaining_amount / daily_benefit_rate
            return timedelta(days=days_elapsed + estimated_days)
        
        return timedelta(days=365 * 10)  # Default to 10 years
    
    async def _calculate_benefits_breakdown(self, benefits: List[ROIBenefit]) -> Dict[ROIMetricType, float]:
        """Calculate breakdown of benefits by metric type"""
        breakdown = defaultdict(float)
        
        for benefit in benefits:
            breakdown[benefit.metric_type] += benefit.monetary_value
        
        return dict(breakdown)
    
    async def _analyze_creator_impact(self, benefits: List[ROIBenefit]) -> Dict[str, Dict[str, float]]:
        """Analyze impact by creator type"""
        creator_impact = defaultdict(lambda: defaultdict(float))
        
        for benefit in benefits:
            if benefit.creator_type:
                creator_impact[benefit.creator_type]['total_benefit'] += benefit.monetary_value
                creator_impact[benefit.creator_type]['improvement_percentage'] += benefit.improvement_percentage
        
        # Calculate averages
        for creator_type in creator_impact:
            count = len([b for b in benefits if b.creator_type == creator_type])
            if count > 0:
                creator_impact[creator_type]['avg_improvement'] = (
                    creator_impact[creator_type]['improvement_percentage'] / count
                )
        
        return dict(creator_impact)
    
    async def _calculate_confidence_score(self, benefits: List[ROIBenefit]) -> float:
        """Calculate overall confidence score for ROI calculation"""
        if not benefits:
            return 0.0
        
        confidence_scores = [b.confidence_level for b in benefits if b.confidence_level > 0]
        
        if not confidence_scores:
            return 0.5  # Default moderate confidence
        
        return statistics.mean(confidence_scores)
    
    async def _project_future_benefits(self, 
                                     investment: MLInvestment,
                                     historical_benefits: List[ROIBenefit]) -> float:
        """Project future benefits based on historical data"""
        if not historical_benefits:
            return 0.0
        
        # Calculate trend
        monthly_benefits = defaultdict(float)
        for benefit in historical_benefits:
            month_key = benefit.measurement_date.strftime('%Y-%m')
            monthly_benefits[month_key] += benefit.monetary_value
        
        if len(monthly_benefits) < 2:
            return 0.0
        
        # Simple linear projection
        benefit_values = list(monthly_benefits.values())
        avg_monthly_benefit = statistics.mean(benefit_values)
        
        # Project 6 months into future
        projected_benefits = avg_monthly_benefit * 6
        
        return projected_benefits
    
    async def _analyze_by_category(self, investments: Dict[str, MLInvestment]) -> Dict[str, Any]:
        """Analyze ROI by investment category"""
        category_analysis = defaultdict(lambda: {
            'total_invested': 0.0,
            'total_benefits': 0.0,
            'count': 0,
            'avg_roi': 0.0
        })
        
        for investment_id, investment in investments.items():
            roi_report = await self.calculate_roi(investment_id, include_projections=False)
            if roi_report:
                category = investment.category.value
                category_analysis[category]['total_invested'] += roi_report.total_investment
                category_analysis[category]['total_benefits'] += roi_report.total_benefits
                category_analysis[category]['count'] += 1
        
        # Calculate averages
        for category in category_analysis:
            if category_analysis[category]['total_invested'] > 0:
                category_analysis[category]['avg_roi'] = (
                    (category_analysis[category]['total_benefits'] - 
                     category_analysis[category]['total_invested']) /
                    category_analysis[category]['total_invested'] * 100
                )
        
        return dict(category_analysis)
    
    async def _analyze_by_creator_type(self, investments: Dict[str, MLInvestment]) -> Dict[str, Any]:
        """Analyze ROI by creator type"""
        creator_analysis = defaultdict(lambda: {
            'total_invested': 0.0,
            'total_benefits': 0.0,
            'count': 0,
            'avg_roi': 0.0
        })
        
        for investment_id, investment in investments.items():
            roi_report = await self.calculate_roi(investment_id, include_projections=False)
            if roi_report:
                for creator_type in investment.creator_types_affected:
                    creator_analysis[creator_type]['total_invested'] += roi_report.total_investment
                    creator_analysis[creator_type]['total_benefits'] += roi_report.total_benefits
                    creator_analysis[creator_type]['count'] += 1
        
        return dict(creator_analysis)
    
    async def _generate_portfolio_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on portfolio analysis"""
        recommendations = []
        
        if analysis['average_roi'] < 15:
            recommendations.append("Consider reviewing investment strategy - average ROI below 15%")
        
        if analysis['best_performing'] and analysis['worst_performing']:
            best_roi = analysis['best_performing']['roi']
            worst_roi = analysis['worst_performing']['roi']
            if best_roi - worst_roi > 50:
                recommendations.append("High variance in ROI - focus on replicating best practices")
        
        recommendations.append("Continue monitoring and optimizing high-performing investments")
        
        return recommendations
    
    async def _get_historical_performance_data(self, category: InvestmentCategory) -> Dict[str, Any]:
        """Get historical performance data for investment category"""
        # Simulate historical data
        return {
            'avg_roi': 25.0,
            'std_dev': 10.0,
            'success_rate': 0.75,
            'avg_payback_months': 8
        }
    
    async def _calculate_base_prediction(self, 
                                       investment: MLInvestment,
                                       historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate base ROI prediction"""
        predicted_roi = historical_data.get('avg_roi', 20.0)
        predicted_benefits = investment.amount * (predicted_roi / 100)
        
        return {
            'benefits': predicted_benefits,
            'roi_percentage': predicted_roi,
            'payback_months': historical_data.get('avg_payback_months', 12)
        }
    
    async def _apply_creator_adjustments(self, 
                                       investment: MLInvestment,
                                       base_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Apply creator-specific adjustments to prediction"""
        # Adjust based on creator types affected
        adjustment_factor = 1.0
        
        for creator_type in investment.creator_types_affected:
            if creator_type in self.creator_value_metrics:
                # Higher value creators might generate higher ROI
                creator_value = self.creator_value_metrics[creator_type]['avg_monthly_revenue']
                if creator_value > 3000:
                    adjustment_factor += 0.1
        
        adjusted_prediction = base_prediction.copy()
        adjusted_prediction['benefits'] *= adjustment_factor
        adjusted_prediction['roi_percentage'] *= adjustment_factor
        
        return adjusted_prediction
    
    async def _apply_risk_adjustment(self, 
                                   investment: MLInvestment,
                                   prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Apply risk adjustments to prediction"""
        risk_multipliers = {
            'low': 0.9,
            'medium': 0.8,
            'high': 0.6
        }
        
        risk_multiplier = risk_multipliers.get(investment.risk_level, 0.8)
        
        adjusted_prediction = prediction.copy()
        adjusted_prediction['benefits'] *= risk_multiplier
        adjusted_prediction['roi_percentage'] *= risk_multiplier
        
        # Add confidence interval
        adjusted_prediction['confidence_interval'] = {
            'lower': adjusted_prediction['roi_percentage'] * 0.7,
            'upper': adjusted_prediction['roi_percentage'] * 1.3
        }
        
        # Add risk factors
        adjusted_prediction['risk_factors'] = [
            f"Risk level: {investment.risk_level}",
            "Market conditions may vary",
            "Creator adoption rates may differ"
        ]
        
        # Add recommendation
        if adjusted_prediction['roi_percentage'] > 20:
            adjusted_prediction['recommendation'] = "Recommended - High ROI potential"
        elif adjusted_prediction['roi_percentage'] > 10:
            adjusted_prediction['recommendation'] = "Consider - Moderate ROI potential"
        else:
            adjusted_prediction['recommendation'] = "Review - Low ROI potential"
        
        # Creator impact prediction
        adjusted_prediction['creator_impact'] = {
            creator_type: f"Expected {adjusted_prediction['roi_percentage']:.1f}% improvement"
            for creator_type in investment.creator_types_affected
        }
        
        return adjusted_prediction
    
    async def _calculate_overall_trend(self, reports: List[ROIReport]) -> Dict[str, Any]:
        """Calculate overall ROI trend"""
        if len(reports) < 2:
            return {'trend': 'insufficient_data'}
        
        # Sort by date
        sorted_reports = sorted(reports, key=lambda x: x.generation_date)
        
        roi_values = [r.roi_percentage for r in sorted_reports]
        
        # Simple trend calculation
        first_half = roi_values[:len(roi_values)//2]
        second_half = roi_values[len(roi_values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg * 1.1:
            trend = 'improving'
        elif second_avg < first_avg * 0.9:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'improvement_rate': ((second_avg - first_avg) / first_avg) * 100
        }
    
    async def _calculate_category_trends(self, reports: List[ROIReport]) -> Dict[str, Any]:
        """Calculate trends by investment category"""
        # Group reports by category
        category_trends = {}
        # Implementation would analyze trends by category
        return category_trends
    
    async def _calculate_creator_type_trends(self, reports: List[ROIReport]) -> Dict[str, Any]:
        """Calculate trends by creator type"""
        # Group reports by creator type
        creator_trends = {}
        # Implementation would analyze trends by creator type
        return creator_trends
    
    async def _identify_seasonal_patterns(self, reports: List[ROIReport]) -> Dict[str, Any]:
        """Identify seasonal patterns in ROI"""
        # Analyze seasonal variations
        seasonal_patterns = {}
        # Implementation would identify patterns
        return seasonal_patterns
    
    async def _identify_improvement_areas(self, reports: List[ROIReport]) -> List[str]:
        """Identify areas for ROI improvement"""
        improvements = [
            "Optimize model performance monitoring",
            "Enhance creator onboarding processes",
            "Improve data quality and collection"
        ]
        return improvements


# Example usage and testing
async def main() -> None:
    """Example usage of ROI Calculator"""
    calculator = ROICalculator()
    
    # Initialize
    await calculator.initialize()
    
    # Record investment
    investment = MLInvestment(
        investment_id="audio_ml_v2",
        name="Advanced Audio ML Model V2",
        category=InvestmentCategory.MODEL_DEVELOPMENT,
        amount=150000.0,
        start_date=datetime.utcnow() - timedelta(days=90),
        expected_duration=timedelta(days=365),
        creator_types_affected=['musicians'],
        expected_roi_percentage=35.0
    )
    
    await calculator.record_investment(investment)
    
    # Record benefits
    benefit = ROIBenefit(
        benefit_id=str(uuid.uuid4()),
        investment_id="audio_ml_v2",
        metric_type=ROIMetricType.REVENUE_INCREASE,
        baseline_value=100000.0,
        current_value=125000.0,
        improvement_percentage=25.0,
        monetary_value=25000.0,
        measurement_date=datetime.utcnow(),
        creator_type='musicians',
        confidence_level=0.85
    )
    
    await calculator.record_benefit(benefit)
    
    # Calculate ROI
    roi_report = await calculator.calculate_roi("audio_ml_v2")
    print(f"ROI Report: {json.dumps(roi_report.__dict__, indent=2, default=str) if roi_report else 'None'}")
    
    # Get portfolio analysis
    portfolio = await calculator.get_portfolio_roi()
    print(f"Portfolio Analysis: {json.dumps(portfolio, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())