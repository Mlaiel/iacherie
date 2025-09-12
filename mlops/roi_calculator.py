"""MLOps ROI Calculator - Enterprise ML Investment Analysis
Calculateur de ROI intelligent pour investissements ML avec attribution précise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🎯 Business Logic Integration:
Creator → ML Investment → Model Performance → Business KPIs → ROI Calculation → Investment Optimization

🚀 Multi-Expert Implementation:
- ML Engineer: Model performance correlation with business outcomes
- Backend Senior: Infrastructure cost attribution and optimization
- DBA: Data pipeline cost analysis and ROI attribution
- DevOps: Operational costs and efficiency measurement
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from pathlib import Path
import aiofiles
import statistics
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvestmentType(Enum):
    """Types d'investissements ML pour ROI."""
    MODEL_DEVELOPMENT = "model_development"
    INFRASTRUCTURE = "infrastructure"
    DATA_PIPELINE = "data_pipeline"
    TRAINING_COMPUTE = "training_compute"
    INFERENCE_SERVING = "inference_serving"
    MONITORING_TOOLS = "monitoring_tools"
    SECURITY_COMPLIANCE = "security_compliance"
    TEAM_TRAINING = "team_training"

class BusinessMetric(Enum):
    """Métriques business pour attribution ROI."""
    REVENUE = "revenue"
    USER_ENGAGEMENT = "user_engagement"
    CONVERSION_RATE = "conversion_rate"
    RETENTION_RATE = "retention_rate"
    COST_SAVINGS = "cost_savings"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    MARKET_SHARE = "market_share"

@dataclass
class MLInvestment:
    """Investissement ML pour analyse ROI."""
    investment_id: str
    investment_type: InvestmentType
    amount_usd: float
    start_date: datetime
    expected_duration_months: int
    creator_segments: List[str]
    business_objectives: List[str]
    success_metrics: List[BusinessMetric]
    risk_level: str  # "low", "medium", "high"
    confidence_score: float

@dataclass
class BusinessImpact:
    """Impact business d'un investissement ML."""
    metric_type: BusinessMetric
    baseline_value: float
    current_value: float
    improvement_percentage: float
    attribution_confidence: float
    measurement_period_days: int
    creator_segment: Optional[str] = None
    timestamp: datetime = None

@dataclass
class ROICalculation:
    """Calcul de ROI détaillé pour investissement ML."""
    investment_id: str
    investment_amount: float
    business_value_generated: float
    operational_cost_savings: float
    efficiency_gains_value: float
    total_return: float
    roi_percentage: float
    payback_period_months: float
    net_present_value: float
    internal_rate_return: float
    risk_adjusted_roi: float
    confidence_score: float
    attribution_breakdown: Dict[str, float]

class ROICalculator:
    """Enterprise ROI calculator pour investissements ML avec attribution précise."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize ROI calculator with enterprise configuration."""
        self.config = self._load_config(config_path)
        self.investments: List[MLInvestment] = []
        self.business_impacts: List[BusinessImpact] = []
        self.roi_calculations: List[ROICalculation] = []
        
        # Creator segment business models
        self.creator_value_models = {
            "musicians": {
                "avg_revenue_per_user": 15.0,
                "engagement_to_revenue_multiplier": 0.03,
                "conversion_rate_baseline": 0.08,
                "retention_value_monthly": 12.0
            },
            "photographers": {
                "avg_revenue_per_user": 45.0,
                "engagement_to_revenue_multiplier": 0.05,
                "conversion_rate_baseline": 0.12,
                "retention_value_monthly": 35.0
            },
            "bloggers": {
                "avg_revenue_per_user": 8.0,
                "engagement_to_revenue_multiplier": 0.02,
                "conversion_rate_baseline": 0.06,
                "retention_value_monthly": 6.0
            },
            "influencers": {
                "avg_revenue_per_user": 25.0,
                "engagement_to_revenue_multiplier": 0.04,
                "conversion_rate_baseline": 0.10,
                "retention_value_monthly": 18.0
            },
            "comedians": {
                "avg_revenue_per_user": 12.0,
                "engagement_to_revenue_multiplier": 0.025,
                "conversion_rate_baseline": 0.07,
                "retention_value_monthly": 9.0
            }
        }
        
        logger.info("💰 ROICalculator enterprise initialized with ML attribution models")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load ROI calculator configuration."""
        default_config = {
            "financial_settings": {
                "discount_rate": 0.12,  # 12% discount rate for NPV
                "risk_free_rate": 0.03,  # 3% risk-free rate
                "market_rate": 0.08,    # 8% market rate
                "tax_rate": 0.25        # 25% corporate tax rate
            },
            "attribution_settings": {
                "min_attribution_confidence": 0.70,
                "baseline_measurement_days": 90,
                "attribution_decay_rate": 0.85,
                "control_group_size": 0.10
            },
            "roi_thresholds": {
                "excellent_roi": 3.0,     # 300% ROI
                "good_roi": 1.5,          # 150% ROI  
                "acceptable_roi": 0.5,    # 50% ROI
                "poor_roi": 0.0           # 0% ROI
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config

    async def register_ml_investment(self,
                                   investment_type: InvestmentType,
                                   amount_usd: float,
                                   creator_segments: List[str],
                                   expected_duration_months: int = 12,
                                   business_objectives: Optional[List[str]] = None,
                                   success_metrics: Optional[List[BusinessMetric]] = None) -> str:
        """Enregistrer un nouvel investissement ML pour suivi ROI."""
        try:
            investment_id = f"inv_{int(datetime.now().timestamp())}_{investment_type.value[:4]}"
            
            # Default business objectives and metrics based on investment type
            if not business_objectives:
                business_objectives = self._get_default_objectives(investment_type)
            
            if not success_metrics:
                success_metrics = self._get_default_metrics(investment_type)
            
            # Risk assessment based on investment type and amount
            risk_level = self._assess_investment_risk(investment_type, amount_usd, creator_segments)
            
            # Confidence score based on historical data and investment characteristics
            confidence_score = self._calculate_investment_confidence(
                investment_type, amount_usd, creator_segments, expected_duration_months
            )
            
            investment = MLInvestment(
                investment_id=investment_id,
                investment_type=investment_type,
                amount_usd=amount_usd,
                start_date=datetime.now(),
                expected_duration_months=expected_duration_months,
                creator_segments=creator_segments,
                business_objectives=business_objectives,
                success_metrics=success_metrics,
                risk_level=risk_level,
                confidence_score=confidence_score
            )
            
            self.investments.append(investment)
            
            logger.info(f"📊 Registered ML investment {investment_id}: ${amount_usd:,.2f} "
                       f"for {creator_segments} with {risk_level} risk")
            
            return investment_id
            
        except Exception as e:
            logger.error(f"❌ Error registering ML investment: {e}")
            return ""

    def _get_default_objectives(self, investment_type: InvestmentType) -> List[str]:
        """Obtenir les objectifs business par défaut pour un type d'investissement."""
        objectives_map = {
            InvestmentType.MODEL_DEVELOPMENT: [
                "improve_prediction_accuracy",
                "reduce_inference_latency",
                "increase_user_engagement"
            ],
            InvestmentType.INFRASTRUCTURE: [
                "reduce_operational_costs",
                "improve_system_reliability",
                "enable_global_scaling"
            ],
            InvestmentType.DATA_PIPELINE: [
                "improve_data_quality",
                "reduce_data_processing_time",
                "enable_real_time_analytics"
            ],
            InvestmentType.TRAINING_COMPUTE: [
                "accelerate_model_training",
                "enable_larger_model_architectures",
                "improve_model_performance"
            ],
            InvestmentType.INFERENCE_SERVING: [
                "reduce_inference_costs",
                "improve_response_time",
                "increase_throughput_capacity"
            ]
        }
        
        return objectives_map.get(investment_type, ["improve_business_outcomes"])

    def _get_default_metrics(self, investment_type: InvestmentType) -> List[BusinessMetric]:
        """Obtenir les métriques de succès par défaut."""
        metrics_map = {
            InvestmentType.MODEL_DEVELOPMENT: [
                BusinessMetric.USER_ENGAGEMENT,
                BusinessMetric.CONVERSION_RATE,
                BusinessMetric.REVENUE
            ],
            InvestmentType.INFRASTRUCTURE: [
                BusinessMetric.COST_SAVINGS,
                BusinessMetric.OPERATIONAL_EFFICIENCY,
                BusinessMetric.CUSTOMER_SATISFACTION
            ],
            InvestmentType.DATA_PIPELINE: [
                BusinessMetric.OPERATIONAL_EFFICIENCY,
                BusinessMetric.COST_SAVINGS,
                BusinessMetric.USER_ENGAGEMENT
            ]
        }
        
        return metrics_map.get(investment_type, [BusinessMetric.REVENUE])

    def _assess_investment_risk(self, 
                               investment_type: InvestmentType,
                               amount_usd: float,
                               creator_segments: List[str]) -> str:
        """Évaluer le niveau de risque d'un investissement."""
        risk_score = 0
        
        # Risk based on investment type
        type_risk = {
            InvestmentType.MODEL_DEVELOPMENT: 2,
            InvestmentType.INFRASTRUCTURE: 1,
            InvestmentType.DATA_PIPELINE: 1,
            InvestmentType.TRAINING_COMPUTE: 1,
            InvestmentType.INFERENCE_SERVING: 1,
            InvestmentType.MONITORING_TOOLS: 0,
            InvestmentType.SECURITY_COMPLIANCE: 0,
            InvestmentType.TEAM_TRAINING: 1
        }
        risk_score += type_risk.get(investment_type, 1)
        
        # Risk based on amount
        if amount_usd > 100000:
            risk_score += 2
        elif amount_usd > 50000:
            risk_score += 1
        
        # Risk based on creator segments diversity
        if len(creator_segments) > 3:
            risk_score += 1
        
        # Convert to risk level
        if risk_score <= 2:
            return "low"
        elif risk_score <= 4:
            return "medium"
        else:
            return "high"

    def _calculate_investment_confidence(self,
                                       investment_type: InvestmentType,
                                       amount_usd: float,
                                       creator_segments: List[str],
                                       duration_months: int) -> float:
        """Calculer le score de confiance pour un investissement."""
        base_confidence = 0.70
        
        # Confidence based on investment type (historical success rates)
        type_confidence_boost = {
            InvestmentType.INFRASTRUCTURE: 0.15,
            InvestmentType.MONITORING_TOOLS: 0.12,
            InvestmentType.DATA_PIPELINE: 0.10,
            InvestmentType.INFERENCE_SERVING: 0.08,
            InvestmentType.MODEL_DEVELOPMENT: 0.05,
            InvestmentType.TRAINING_COMPUTE: 0.05,
            InvestmentType.SECURITY_COMPLIANCE: 0.10,
            InvestmentType.TEAM_TRAINING: 0.07
        }
        
        confidence = base_confidence + type_confidence_boost.get(investment_type, 0.05)
        
        # Adjust for investment size (sweet spot optimization)
        if 10000 <= amount_usd <= 75000:
            confidence += 0.05  # Sweet spot for ROI
        elif amount_usd > 200000:
            confidence -= 0.10  # Higher risk for large investments
        
        # Adjust for duration (shorter projects often more predictable)
        if duration_months <= 6:
            confidence += 0.05
        elif duration_months > 18:
            confidence -= 0.08
        
        # Adjust for creator segment focus
        if len(creator_segments) <= 2:
            confidence += 0.03  # Focused approach
        
        return min(0.95, max(0.50, confidence))

    async def record_business_impact(self,
                                   metric_type: BusinessMetric,
                                   baseline_value: float,
                                   current_value: float,
                                   creator_segment: Optional[str] = None,
                                   measurement_period_days: int = 30,
                                   attribution_confidence: float = 0.80) -> None:
        """Enregistrer l'impact business pour attribution ROI."""
        try:
            improvement_percentage = ((current_value - baseline_value) / baseline_value * 100) if baseline_value > 0 else 0
            
            impact = BusinessImpact(
                metric_type=metric_type,
                baseline_value=baseline_value,
                current_value=current_value,
                improvement_percentage=improvement_percentage,
                attribution_confidence=attribution_confidence,
                measurement_period_days=measurement_period_days,
                creator_segment=creator_segment,
                timestamp=datetime.now()
            )
            
            self.business_impacts.append(impact)
            
            logger.info(f"📈 Recorded business impact: {metric_type.value} "
                       f"{improvement_percentage:+.1f}% for {creator_segment or 'all segments'}")
            
        except Exception as e:
            logger.error(f"❌ Error recording business impact: {e}")

    async def calculate_investment_roi(self, investment_id: str) -> Optional[ROICalculation]:
        """Calculer le ROI détaillé pour un investissement spécifique."""
        try:
            # Find the investment
            investment = next((inv for inv in self.investments if inv.investment_id == investment_id), None)
            if not investment:
                logger.error(f"Investment {investment_id} not found")
                return None
            
            # Calculate time since investment
            days_since_investment = (datetime.now() - investment.start_date).days
            
            # Get relevant business impacts
            relevant_impacts = [
                impact for impact in self.business_impacts
                if (impact.timestamp >= investment.start_date and
                    (not impact.creator_segment or impact.creator_segment in investment.creator_segments) and
                    impact.metric_type in investment.success_metrics)
            ]
            
            if not relevant_impacts:
                logger.warning(f"No business impacts found for investment {investment_id}")
                return self._create_preliminary_roi_calculation(investment)
            
            # Calculate business value generated
            business_value = await self._calculate_business_value(investment, relevant_impacts)
            
            # Calculate operational cost savings
            cost_savings = await self._calculate_cost_savings(investment, relevant_impacts)
            
            # Calculate efficiency gains value
            efficiency_value = await self._calculate_efficiency_gains_value(investment, relevant_impacts)
            
            # Total return calculation
            total_return = business_value + cost_savings + efficiency_value
            
            # ROI percentage
            roi_percentage = (total_return - investment.amount_usd) / investment.amount_usd * 100
            
            # Payback period
            monthly_return = total_return / max(1, days_since_investment / 30)
            payback_period_months = investment.amount_usd / monthly_return if monthly_return > 0 else float('inf')
            
            # Net Present Value
            npv = await self._calculate_npv(investment, total_return)
            
            # Internal Rate of Return (simplified)
            irr = await self._calculate_irr(investment, total_return, days_since_investment)
            
            # Risk-adjusted ROI
            risk_adjustment = {"low": 1.0, "medium": 0.85, "high": 0.70}[investment.risk_level]
            risk_adjusted_roi = roi_percentage * risk_adjustment
            
            # Attribution breakdown
            attribution_breakdown = await self._calculate_attribution_breakdown(investment, relevant_impacts)
            
            # Confidence score (average of impact confidences weighted by value)
            total_impact_value = sum(
                self._impact_to_monetary_value(impact, investment.creator_segments)
                for impact in relevant_impacts
            )
            
            confidence_score = (
                sum(
                    impact.attribution_confidence * self._impact_to_monetary_value(impact, investment.creator_segments)
                    for impact in relevant_impacts
                ) / total_impact_value if total_impact_value > 0 else investment.confidence_score
            )
            
            roi_calc = ROICalculation(
                investment_id=investment_id,
                investment_amount=investment.amount_usd,
                business_value_generated=business_value,
                operational_cost_savings=cost_savings,
                efficiency_gains_value=efficiency_value,
                total_return=total_return,
                roi_percentage=roi_percentage,
                payback_period_months=payback_period_months,
                net_present_value=npv,
                internal_rate_return=irr,
                risk_adjusted_roi=risk_adjusted_roi,
                confidence_score=confidence_score,
                attribution_breakdown=attribution_breakdown
            )
            
            self.roi_calculations.append(roi_calc)
            
            logger.info(f"💰 Calculated ROI for {investment_id}: {roi_percentage:.1f}% "
                       f"(${total_return:,.2f} return on ${investment.amount_usd:,.2f})")
            
            return roi_calc
            
        except Exception as e:
            logger.error(f"❌ Error calculating ROI for investment {investment_id}: {e}")
            return None

    def _create_preliminary_roi_calculation(self, investment: MLInvestment) -> ROICalculation:
        """Créer un calcul ROI préliminaire sans impacts mesurés."""
        # Use industry benchmarks and investment confidence
        expected_return_multiplier = {
            InvestmentType.MODEL_DEVELOPMENT: 2.5,
            InvestmentType.INFRASTRUCTURE: 1.8,
            InvestmentType.DATA_PIPELINE: 2.0,
            InvestmentType.TRAINING_COMPUTE: 1.5,
            InvestmentType.INFERENCE_SERVING: 2.2,
            InvestmentType.MONITORING_TOOLS: 1.6,
            InvestmentType.SECURITY_COMPLIANCE: 1.4,
            InvestmentType.TEAM_TRAINING: 1.7
        }
        
        multiplier = expected_return_multiplier.get(investment.investment_type, 1.5)
        expected_return = investment.amount_usd * multiplier * investment.confidence_score
        
        return ROICalculation(
            investment_id=investment.investment_id,
            investment_amount=investment.amount_usd,
            business_value_generated=expected_return * 0.7,
            operational_cost_savings=expected_return * 0.2,
            efficiency_gains_value=expected_return * 0.1,
            total_return=expected_return,
            roi_percentage=(expected_return - investment.amount_usd) / investment.amount_usd * 100,
            payback_period_months=investment.expected_duration_months * 0.6,
            net_present_value=expected_return * 0.85,  # Simplified NPV
            internal_rate_return=0.15,  # Default 15% IRR estimate
            risk_adjusted_roi=((expected_return - investment.amount_usd) / investment.amount_usd * 100) * 0.8,
            confidence_score=investment.confidence_score * 0.7,  # Lower confidence for preliminary
            attribution_breakdown={"estimated": 1.0}
        )

    async def _calculate_business_value(self, 
                                      investment: MLInvestment,
                                      impacts: List[BusinessImpact]) -> float:
        """Calculer la valeur business générée."""
        total_value = 0.0
        
        for impact in impacts:
            monetary_value = self._impact_to_monetary_value(impact, investment.creator_segments)
            
            # Apply attribution confidence
            attributed_value = monetary_value * impact.attribution_confidence
            
            # Time decay for older impacts
            days_old = (datetime.now() - impact.timestamp).days
            decay_factor = self.config["attribution_settings"]["attribution_decay_rate"] ** (days_old / 30)
            
            total_value += attributed_value * decay_factor
        
        return total_value

    def _impact_to_monetary_value(self, impact: BusinessImpact, creator_segments: List[str]) -> float:
        """Convertir un impact business en valeur monétaire."""
        # Get average value model for relevant creator segments
        relevant_segments = [impact.creator_segment] if impact.creator_segment else creator_segments
        
        avg_model = {}
        for key in ["avg_revenue_per_user", "engagement_to_revenue_multiplier", "conversion_rate_baseline", "retention_value_monthly"]:
            values = [
                self.creator_value_models[segment][key] 
                for segment in relevant_segments 
                if segment in self.creator_value_models
            ]
            avg_model[key] = statistics.mean(values) if values else 10.0
        
        # Convert impact to monetary value based on metric type
        improvement_abs = impact.current_value - impact.baseline_value
        
        if impact.metric_type == BusinessMetric.REVENUE:
            return improvement_abs  # Direct revenue impact
        
        elif impact.metric_type == BusinessMetric.USER_ENGAGEMENT:
            # Engagement improvement to revenue
            return improvement_abs * avg_model["engagement_to_revenue_multiplier"] * 100
        
        elif impact.metric_type == BusinessMetric.CONVERSION_RATE:
            # Conversion rate improvement (assuming percentage points)
            user_base = 10000  # Estimated user base
            return (improvement_abs / 100) * user_base * avg_model["avg_revenue_per_user"]
        
        elif impact.metric_type == BusinessMetric.RETENTION_RATE:
            # Retention improvement value
            user_base = 10000
            return (improvement_abs / 100) * user_base * avg_model["retention_value_monthly"] * 12
        
        elif impact.metric_type == BusinessMetric.COST_SAVINGS:
            return improvement_abs  # Direct cost savings
        
        elif impact.metric_type == BusinessMetric.OPERATIONAL_EFFICIENCY:
            # Efficiency improvement to cost savings (estimate 2% of operating costs per 10% efficiency gain)
            operating_costs = 50000  # Monthly estimate
            return (improvement_abs / 10) * 0.02 * operating_costs * 12
        
        elif impact.metric_type == BusinessMetric.CUSTOMER_SATISFACTION:
            # Satisfaction to retention and revenue (rough estimate)
            return (improvement_abs / 10) * 0.05 * avg_model["avg_revenue_per_user"] * 1000
        
        else:
            # Default estimate for other metrics
            return improvement_abs * 10

    async def _calculate_cost_savings(self, 
                                    investment: MLInvestment,
                                    impacts: List[BusinessImpact]) -> float:
        """Calculer les économies de coûts opérationnels."""
        cost_savings = 0.0
        
        cost_saving_impacts = [
            impact for impact in impacts 
            if impact.metric_type in [BusinessMetric.COST_SAVINGS, BusinessMetric.OPERATIONAL_EFFICIENCY]
        ]
        
        for impact in cost_saving_impacts:
            if impact.metric_type == BusinessMetric.COST_SAVINGS:
                savings = impact.current_value - impact.baseline_value
                cost_savings += savings * impact.attribution_confidence
            
            elif impact.metric_type == BusinessMetric.OPERATIONAL_EFFICIENCY:
                # Convert efficiency gains to cost savings
                efficiency_gain = impact.improvement_percentage
                estimated_monthly_costs = 20000  # Base operational costs
                monthly_savings = estimated_monthly_costs * (efficiency_gain / 100) * 0.3  # 30% of efficiency gain
                cost_savings += monthly_savings * 12 * impact.attribution_confidence
        
        return cost_savings

    async def _calculate_efficiency_gains_value(self,
                                              investment: MLInvestment,
                                              impacts: List[BusinessImpact]) -> float:
        """Calculer la valeur des gains d'efficacité."""
        efficiency_value = 0.0
        
        # Infrastructure and process efficiency investments
        if investment.investment_type in [InvestmentType.INFRASTRUCTURE, InvestmentType.DATA_PIPELINE]:
            efficiency_impacts = [
                impact for impact in impacts
                if impact.metric_type == BusinessMetric.OPERATIONAL_EFFICIENCY
            ]
            
            for impact in efficiency_impacts:
                # Convert efficiency gains to monetary value
                efficiency_improvement = impact.improvement_percentage
                
                # Estimate value based on time savings and productivity gains
                team_size = 20  # Average team size affected
                avg_hourly_rate = 100  # Average hourly rate
                hours_saved_per_month = team_size * 40 * (efficiency_improvement / 100) * 0.2  # 20% time impact
                
                monthly_value = hours_saved_per_month * avg_hourly_rate
                annual_value = monthly_value * 12
                
                efficiency_value += annual_value * impact.attribution_confidence
        
        return efficiency_value

    async def _calculate_npv(self, investment: MLInvestment, total_return: float) -> float:
        """Calculer la Net Present Value."""
        discount_rate = self.config["financial_settings"]["discount_rate"]
        
        # Assume returns are spread over investment duration
        monthly_return = total_return / investment.expected_duration_months
        
        npv = -investment.amount_usd  # Initial investment (negative cash flow)
        
        for month in range(1, investment.expected_duration_months + 1):
            discounted_return = monthly_return / ((1 + discount_rate / 12) ** month)
            npv += discounted_return
        
        return npv

    async def _calculate_irr(self, 
                           investment: MLInvestment,
                           total_return: float,
                           days_elapsed: int) -> float:
        """Calculer l'Internal Rate of Return (approximation)."""
        if days_elapsed <= 0:
            return 0.0
        
        # Simplified IRR calculation
        periods = days_elapsed / 365  # Convert to years
        
        if periods > 0 and investment.amount_usd > 0:
            irr = (total_return / investment.amount_usd) ** (1 / periods) - 1
            return min(1.0, max(-0.5, irr))  # Cap between -50% and 100%
        
        return 0.0

    async def _calculate_attribution_breakdown(self,
                                             investment: MLInvestment,
                                             impacts: List[BusinessImpact]) -> Dict[str, float]:
        """Calculer la répartition d'attribution des impacts."""
        breakdown = {}
        
        total_value = sum(
            self._impact_to_monetary_value(impact, investment.creator_segments) * impact.attribution_confidence
            for impact in impacts
        )
        
        if total_value <= 0:
            return {"unknown": 1.0}
        
        # Break down by business metric
        for metric_type in BusinessMetric:
            metric_impacts = [impact for impact in impacts if impact.metric_type == metric_type]
            metric_value = sum(
                self._impact_to_monetary_value(impact, investment.creator_segments) * impact.attribution_confidence
                for impact in metric_impacts
            )
            
            if metric_value > 0:
                breakdown[metric_type.value] = metric_value / total_value
        
        # Break down by creator segment
        for segment in investment.creator_segments:
            segment_impacts = [
                impact for impact in impacts 
                if not impact.creator_segment or impact.creator_segment == segment
            ]
            segment_value = sum(
                self._impact_to_monetary_value(impact, [segment]) * impact.attribution_confidence
                for impact in segment_impacts
            )
            
            if segment_value > 0:
                breakdown[f"segment_{segment}"] = segment_value / total_value
        
        return breakdown

    async def generate_portfolio_roi_analysis(self) -> Dict[str, Any]:
        """Générer une analyse ROI complète du portfolio d'investissements."""
        try:
            if not self.investments:
                return {"error": "No investments found for portfolio analysis"}
            
            # Calculate ROI for all investments
            portfolio_rois = []
            for investment in self.investments:
                roi_calc = await self.calculate_investment_roi(investment.investment_id)
                if roi_calc:
                    portfolio_rois.append(roi_calc)
            
            if not portfolio_rois:
                return {"error": "No ROI calculations available"}
            
            # Portfolio-level metrics
            total_invested = sum(roi.investment_amount for roi in portfolio_rois)
            total_returns = sum(roi.total_return for roi in portfolio_rois)
            portfolio_roi = (total_returns - total_invested) / total_invested * 100 if total_invested > 0 else 0
            
            avg_payback_period = statistics.mean([
                roi.payback_period_months for roi in portfolio_rois 
                if roi.payback_period_months != float('inf')
            ])
            
            # Performance by investment type
            performance_by_type = {}
            for inv_type in InvestmentType:
                type_rois = [roi for roi in portfolio_rois 
                           if any(inv.investment_type == inv_type for inv in self.investments 
                                 if inv.investment_id == roi.investment_id)]
                
                if type_rois:
                    performance_by_type[inv_type.value] = {
                        "count": len(type_rois),
                        "total_invested": sum(roi.investment_amount for roi in type_rois),
                        "total_returns": sum(roi.total_return for roi in type_rois),
                        "avg_roi_percentage": statistics.mean([roi.roi_percentage for roi in type_rois]),
                        "avg_confidence": statistics.mean([roi.confidence_score for roi in type_rois])
                    }
            
            # Performance by creator segment
            performance_by_segment = {}
            for segment in ["musicians", "photographers", "bloggers", "influencers", "comedians"]:
                segment_investments = [inv for inv in self.investments if segment in inv.creator_segments]
                segment_rois = [roi for roi in portfolio_rois 
                              if roi.investment_id in [inv.investment_id for inv in segment_investments]]
                
                if segment_rois:
                    performance_by_segment[segment] = {
                        "count": len(segment_rois),
                        "total_invested": sum(roi.investment_amount for roi in segment_rois),
                        "total_returns": sum(roi.total_return for roi in segment_rois),
                        "avg_roi_percentage": statistics.mean([roi.roi_percentage for roi in segment_rois])
                    }
            
            # Risk-return analysis
            risk_return_analysis = {}
            for risk_level in ["low", "medium", "high"]:
                risk_investments = [inv for inv in self.investments if inv.risk_level == risk_level]
                risk_rois = [roi for roi in portfolio_rois 
                           if roi.investment_id in [inv.investment_id for inv in risk_investments]]
                
                if risk_rois:
                    risk_return_analysis[risk_level] = {
                        "count": len(risk_rois),
                        "avg_roi": statistics.mean([roi.roi_percentage for roi in risk_rois]),
                        "avg_risk_adjusted_roi": statistics.mean([roi.risk_adjusted_roi for roi in risk_rois])
                    }
            
            # ROI quality assessment
            excellent_rois = len([roi for roi in portfolio_rois 
                                if roi.roi_percentage >= self.config["roi_thresholds"]["excellent_roi"] * 100])
            good_rois = len([roi for roi in portfolio_rois 
                           if self.config["roi_thresholds"]["good_roi"] * 100 <= roi.roi_percentage < self.config["roi_thresholds"]["excellent_roi"] * 100])
            
            portfolio_analysis = {
                "portfolio_overview": {
                    "total_investments": len(self.investments),
                    "total_invested_usd": round(total_invested, 2),
                    "total_returns_usd": round(total_returns, 2),
                    "portfolio_roi_percentage": round(portfolio_roi, 1),
                    "avg_payback_period_months": round(avg_payback_period, 1),
                    "portfolio_npv": round(sum(roi.net_present_value for roi in portfolio_rois), 2)
                },
                "performance_by_investment_type": performance_by_type,
                "performance_by_creator_segment": performance_by_segment,
                "risk_return_analysis": risk_return_analysis,
                "roi_quality_distribution": {
                    "excellent_rois": excellent_rois,
                    "good_rois": good_rois,
                    "total_calculated": len(portfolio_rois)
                },
                "top_performing_investments": [
                    {
                        "investment_id": roi.investment_id,
                        "roi_percentage": round(roi.roi_percentage, 1),
                        "total_return": round(roi.total_return, 2),
                        "confidence_score": round(roi.confidence_score, 2)
                    } for roi in sorted(portfolio_rois, key=lambda x: x.roi_percentage, reverse=True)[:5]
                ]
            }
            
            logger.info(f"📊 Portfolio ROI Analysis: {portfolio_roi:.1f}% overall ROI, "
                       f"${total_returns:,.2f} returns on ${total_invested:,.2f} invested")
            
            return portfolio_analysis
            
        except Exception as e:
            logger.error(f"❌ Error generating portfolio ROI analysis: {e}")
            return {"error": str(e)}

    async def export_roi_report(self, format_type: str = "json") -> str:
        """Exporter un rapport ROI complet."""
        try:
            # Generate comprehensive analysis
            portfolio_analysis = await self.generate_portfolio_roi_analysis()
            
            report_data = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "ml_investment_roi_analysis",
                    "total_investments": len(self.investments),
                    "total_business_impacts": len(self.business_impacts)
                },
                "portfolio_analysis": portfolio_analysis,
                "detailed_investments": [
                    {
                        **asdict(inv),
                        "investment_type": inv.investment_type.value,
                        "start_date": inv.start_date.isoformat(),
                        "success_metrics": [metric.value for metric in inv.success_metrics]
                    } for inv in self.investments
                ],
                "roi_calculations": [
                    asdict(roi) for roi in self.roi_calculations
                ],
                "business_impacts": [
                    {
                        **asdict(impact),
                        "metric_type": impact.metric_type.value,
                        "timestamp": impact.timestamp.isoformat() if impact.timestamp else None
                    } for impact in self.business_impacts
                ]
            }
            
            # Export to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/ml_roi_analysis_{timestamp}.{format_type}"
            
            async with aiofiles.open(filename, 'w') as f:
                if format_type == "json":
                    await f.write(json.dumps(report_data, indent=2, default=str))
                
            logger.info(f"📊 ML ROI analysis report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error exporting ROI report: {e}")
            return ""

# Example usage and testing
async def main():
    """Example usage of enterprise ROI calculator."""
    print("💰 MLOps ROI Calculator - Enterprise Demo")
    print("="*50)
    
    # Create ROI calculator
    roi_calc = ROICalculator()
    
    # Register sample investments
    print("\n📊 Registering ML investments...")
    
    inv1 = await roi_calc.register_ml_investment(
        investment_type=InvestmentType.MODEL_DEVELOPMENT,
        amount_usd=75000,
        creator_segments=["musicians", "photographers"],
        expected_duration_months=8,
        business_objectives=["improve_recommendation_accuracy", "increase_user_engagement"]
    )
    
    inv2 = await roi_calc.register_ml_investment(
        investment_type=InvestmentType.INFRASTRUCTURE,
        amount_usd=50000,
        creator_segments=["influencers", "bloggers"],
        expected_duration_months=6
    )
    
    print(f"   Registered investments: {inv1}, {inv2}")
    
    # Record business impacts
    print(f"\n📈 Recording business impacts...")
    
    await roi_calc.record_business_impact(
        metric_type=BusinessMetric.USER_ENGAGEMENT,
        baseline_value=100000,
        current_value=125000,
        creator_segment="musicians",
        attribution_confidence=0.85
    )
    
    await roi_calc.record_business_impact(
        metric_type=BusinessMetric.COST_SAVINGS,
        baseline_value=0,
        current_value=8000,
        creator_segment="influencers",
        attribution_confidence=0.90
    )
    
    print("   Recorded engagement and cost savings impacts")
    
    # Calculate ROI for investments
    print(f"\n💰 Calculating investment ROI...")
    
    roi1 = await roi_calc.calculate_investment_roi(inv1)
    roi2 = await roi_calc.calculate_investment_roi(inv2)
    
    if roi1:
        print(f"   {inv1}: {roi1.roi_percentage:.1f}% ROI, ${roi1.total_return:,.2f} return")
    if roi2:
        print(f"   {inv2}: {roi2.roi_percentage:.1f}% ROI, ${roi2.total_return:,.2f} return")
    
    # Generate portfolio analysis
    print(f"\n📊 Generating portfolio analysis...")
    portfolio = await roi_calc.generate_portfolio_roi_analysis()
    
    if "portfolio_overview" in portfolio:
        overview = portfolio["portfolio_overview"]
        print(f"   Portfolio ROI: {overview['portfolio_roi_percentage']}%")
        print(f"   Total Returns: ${overview['total_returns_usd']:,.2f}")
        print(f"   Payback Period: {overview['avg_payback_period_months']:.1f} months")
    
    # Export report
    print(f"\n📊 Exporting ROI report...")
    report_file = await roi_calc.export_roi_report()
    print(f"   Report saved to: {report_file}")
    
    print(f"\n✅ ROI analysis complete!")

if __name__ == "__main__":
    asyncio.run(main())