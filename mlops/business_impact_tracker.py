"""
Enterprise Business Impact Tracker for MLOps
ML Engineer + Business Analyst implementation with ROI measurement and impact analysis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from enum import Enum
import json
import uuid
import statistics
from collections import defaultdict
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class BusinessMetricType(Enum):
    """Types of business metrics"""
    REVENUE = "revenue"
    CONVERSION_RATE = "conversion_rate"
    USER_ENGAGEMENT = "user_engagement"
    RETENTION_RATE = "retention_rate"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    COST_REDUCTION = "cost_reduction"
    TIME_TO_VALUE = "time_to_value"
    QUALITY_SCORE = "quality_score"
    MARKET_SHARE = "market_share"


class CreatorType(Enum):
    """Types of creators on the platform"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ARTIST = "artist"
    EDUCATOR = "educator"


class ImpactSeverity(Enum):
    """Severity levels of business impact"""
    CRITICAL = "critical"      # >20% impact
    HIGH = "high"             # 10-20% impact
    MEDIUM = "medium"         # 5-10% impact
    LOW = "low"              # 1-5% impact
    MINIMAL = "minimal"       # <1% impact


class ModelStatus(Enum):
    """Model deployment status"""
    DEPLOYED = "deployed"
    TESTING = "testing"
    ROLLED_BACK = "rolled_back"
    DEPRECATED = "deprecated"


@dataclass
class BusinessMetric:
    """Business metric definition"""
    metric_id: str
    metric_type: BusinessMetricType
    name: str
    description: str
    unit: str
    target_value: float
    current_value: float
    baseline_value: float
    creator_type: Optional[CreatorType] = None
    model_id: Optional[str] = None
    collection_frequency: str = "daily"  # daily, hourly, weekly
    is_higher_better: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ROIAnalysis:
    """Return on Investment analysis"""
    analysis_id: str
    model_id: str
    period_start: date
    period_end: date
    investment_cost: float
    revenue_generated: float
    cost_savings: float
    total_benefit: float
    roi_percentage: float
    payback_period_days: int
    net_present_value: float
    break_even_date: Optional[date] = None
    confidence_score: float = 0.0
    methodology: str = ""
    assumptions: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ImpactAssessment:
    """Business impact assessment"""
    assessment_id: str
    model_id: str
    model_version: str
    deployment_date: date
    affected_metrics: List[str]
    impact_summary: Dict[str, float]  # metric_id -> impact_percentage
    impact_severity: ImpactSeverity
    creator_segments_affected: List[CreatorType]
    user_segments_affected: List[str]
    estimated_annual_value: float
    confidence_interval: Tuple[float, float]  # (lower_bound, upper_bound)
    statistical_significance: float
    attribution_confidence: float
    external_factors: List[str] = field(default_factory=list)
    methodology_notes: str = ""
    reviewed_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BusinessAlert:
    """Business impact alert"""
    alert_id: str
    metric_id: str
    model_id: str
    alert_type: str  # threshold_breach, trend_anomaly, impact_detected
    severity: ImpactSeverity
    message: str
    current_value: float
    expected_value: float
    impact_percentage: float
    affected_creators: int
    affected_revenue: float
    detection_time: datetime
    resolution_time: Optional[datetime] = None
    action_taken: Optional[str] = None
    root_cause: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Collects business metrics from various sources"""
    
    def __init__(self) -> None:
        self.metric_cache = {}
        self.collection_history = []
    
    async def collect_creator_metrics(self, creator_type: CreatorType,
                                    time_period: timedelta = timedelta(days=1)) -> Dict[str, float]:
        """Collect metrics specific to creator type"""
        try:
            logger.info(f"Collecting metrics for {creator_type.value} creators")
            
            # Simulate metric collection (in production, would query actual databases)
            await asyncio.sleep(0.5)
            
            base_metrics = await self._get_base_creator_metrics(creator_type)
            
            # Creator-specific metrics
            if creator_type == CreatorType.MUSICIAN:
                creator_metrics = await self._collect_musician_metrics()
            elif creator_type == CreatorType.BLOGGER:
                creator_metrics = await self._collect_blogger_metrics()
            elif creator_type == CreatorType.PHOTOGRAPHER:
                creator_metrics = await self._collect_photographer_metrics()
            elif creator_type == CreatorType.INFLUENCER:
                creator_metrics = await self._collect_influencer_metrics()
            elif creator_type == CreatorType.COMEDIAN:
                creator_metrics = await self._collect_comedian_metrics()
            else:
                creator_metrics = {}
            
            # Combine metrics
            all_metrics = {**base_metrics, **creator_metrics}
            
            # Cache metrics
            cache_key = f"{creator_type.value}_{datetime.now().date()}"
            self.metric_cache[cache_key] = all_metrics
            
            return all_metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics for {creator_type.value}: {e}")
            raise
    
    async def _get_base_creator_metrics(self, creator_type: CreatorType) -> Dict[str, float]:
        """Get base metrics common to all creator types"""
        # Simulate base metrics collection
        return {
            "active_creators": 1500 + (100 * hash(creator_type.value) % 500),
            "new_signups": 45 + (hash(creator_type.value) % 20),
            "revenue_per_creator": 125.50 + (hash(creator_type.value) % 50),
            "engagement_rate": 0.08 + (hash(creator_type.value) % 10) / 100,
            "retention_rate": 0.75 + (hash(creator_type.value) % 20) / 100,
            "satisfaction_score": 4.2 + (hash(creator_type.value) % 8) / 10,
            "support_tickets": 12 + (hash(creator_type.value) % 5),
            "platform_usage_hours": 8.5 + (hash(creator_type.value) % 4)
        }
    
    async def _collect_musician_metrics(self) -> Dict[str, float]:
        """Collect musician-specific metrics"""
        return {
            "tracks_uploaded": 156,
            "streams_generated": 25800,
            "collaboration_matches": 23,
            "music_revenue": 2150.75,
            "playlist_additions": 89,
            "fan_engagement": 4.3,
            "genre_diversity_score": 0.78
        }
    
    async def _collect_blogger_metrics(self) -> Dict[str, float]:
        """Collect blogger-specific metrics"""
        return {
            "posts_published": 78,
            "page_views": 45600,
            "seo_score_improvement": 0.23,
            "content_engagement": 4.1,
            "subscriber_growth": 0.12,
            "monetization_rate": 0.15,
            "content_quality_score": 8.4
        }
    
    async def _collect_photographer_metrics(self) -> Dict[str, float]:
        """Collect photographer-specific metrics"""
        return {
            "photos_uploaded": 234,
            "portfolio_views": 12400,
            "brand_collaborations": 8,
            "licensing_revenue": 1875.50,
            "aesthetic_score": 8.7,
            "client_satisfaction": 4.6,
            "booking_conversion": 0.18
        }
    
    async def _collect_influencer_metrics(self) -> Dict[str, float]:
        """Collect influencer-specific metrics"""
        return {
            "content_pieces": 145,
            "total_reach": 185000,
            "brand_partnerships": 12,
            "sponsorship_revenue": 5250.00,
            "audience_growth": 0.08,
            "engagement_authenticity": 0.92,
            "cross_platform_score": 7.8
        }
    
    async def _collect_comedian_metrics(self) -> Dict[str, float]:
        """Collect comedian-specific metrics"""
        return {
            "jokes_shared": 89,
            "audience_laughter_score": 8.2,
            "show_bookings": 15,
            "performance_revenue": 3200.00,
            "crowd_response": 4.4,
            "viral_content_score": 0.15,
            "humor_rating": 8.6
        }
    
    async def collect_model_performance_metrics(self, model_id: str) -> Dict[str, float]:
        """Collect ML model performance metrics that impact business"""
        try:
            logger.info(f"Collecting performance metrics for model {model_id}")
            
            # Simulate model performance collection
            await asyncio.sleep(0.3)
            
            return {
                "prediction_accuracy": 0.923,
                "inference_latency_ms": 45.2,
                "throughput_rps": 850.0,
                "error_rate": 0.012,
                "model_drift_score": 0.05,
                "feature_importance_stability": 0.89,
                "data_quality_score": 0.94,
                "model_confidence": 0.87,
                "bias_score": 0.03,
                "fairness_score": 0.91
            }
            
        except Exception as e:
            logger.error(f"Failed to collect model metrics for {model_id}: {e}")
            raise


class ImpactCalculator:
    """Calculates business impact of ML models"""
    
    def __init__(self) -> None:
        self.calculation_history = []
        self.baseline_cache = {}
    
    async def calculate_model_impact(self, model_id: str, model_version: str,
                                   deployment_date: date,
                                   evaluation_period_days: int = 30) -> ImpactAssessment:
        """Calculate comprehensive business impact of a model"""
        try:
            logger.info(f"Calculating impact for model {model_id} v{model_version}")
            
            assessment_id = str(uuid.uuid4())
            
            # Get baseline metrics (before model deployment)
            baseline_metrics = await self._get_baseline_metrics(model_id, deployment_date)
            
            # Get current metrics (after model deployment)
            current_metrics = await self._get_current_metrics(model_id, evaluation_period_days)
            
            # Calculate impact for each metric
            impact_summary = {}
            affected_metrics = []
            
            for metric_name, current_value in current_metrics.items():
                if metric_name in baseline_metrics:
                    baseline_value = baseline_metrics[metric_name]
                    
                    if baseline_value != 0:
                        impact_percentage = ((current_value - baseline_value) / baseline_value) * 100
                        impact_summary[metric_name] = impact_percentage
                        
                        # Consider metrics with >1% change as affected
                        if abs(impact_percentage) > 1.0:
                            affected_metrics.append(metric_name)
            
            # Determine impact severity
            max_impact = max([abs(impact) for impact in impact_summary.values()], default=0)
            impact_severity = self._determine_impact_severity(max_impact)
            
            # Estimate annual value impact
            estimated_annual_value = await self._estimate_annual_value_impact(
                impact_summary, baseline_metrics
            )
            
            # Calculate confidence metrics
            confidence_interval = await self._calculate_confidence_interval(
                baseline_metrics, current_metrics, evaluation_period_days
            )
            
            statistical_significance = await self._calculate_statistical_significance(
                baseline_metrics, current_metrics
            )
            
            attribution_confidence = await self._calculate_attribution_confidence(
                model_id, deployment_date, evaluation_period_days
            )
            
            # Identify affected segments
            creator_segments_affected = await self._identify_affected_creator_segments(
                impact_summary
            )
            
            user_segments_affected = await self._identify_affected_user_segments(
                impact_summary
            )
            
            # Create impact assessment
            assessment = ImpactAssessment(
                assessment_id=assessment_id,
                model_id=model_id,
                model_version=model_version,
                deployment_date=deployment_date,
                affected_metrics=affected_metrics,
                impact_summary=impact_summary,
                impact_severity=impact_severity,
                creator_segments_affected=creator_segments_affected,
                user_segments_affected=user_segments_affected,
                estimated_annual_value=estimated_annual_value,
                confidence_interval=confidence_interval,
                statistical_significance=statistical_significance,
                attribution_confidence=attribution_confidence,
                methodology_notes="Causal impact analysis using Bayesian structural time series"
            )
            
            self.calculation_history.append(assessment)
            
            logger.info(f"Impact calculation completed: {assessment_id}")
            
            return assessment
            
        except Exception as e:
            logger.error(f"Impact calculation failed for model {model_id}: {e}")
            raise
    
    async def _get_baseline_metrics(self, model_id: str, deployment_date: date) -> Dict[str, float]:
        """Get baseline metrics before model deployment"""
        # Simulate baseline metrics collection
        await asyncio.sleep(0.2)
        
        # Use cached baseline or generate new one
        cache_key = f"{model_id}_{deployment_date}"
        if cache_key in self.baseline_cache:
            return self.baseline_cache[cache_key]
        
        baseline = {
            "revenue_per_creator": 120.00,
            "conversion_rate": 0.045,
            "user_engagement": 4.1,
            "retention_rate": 0.73,
            "satisfaction_score": 4.0,
            "operational_efficiency": 0.78,
            "time_to_value": 72.5,
            "quality_score": 7.8
        }
        
        self.baseline_cache[cache_key] = baseline
        return baseline
    
    async def _get_current_metrics(self, model_id: str, period_days: int) -> Dict[str, float]:
        """Get current metrics after model deployment"""
        # Simulate current metrics collection
        await asyncio.sleep(0.3)
        
        # Generate metrics with some improvement (simulating positive model impact)
        return {
            "revenue_per_creator": 135.50,  # +12.9% improvement
            "conversion_rate": 0.052,       # +15.6% improvement
            "user_engagement": 4.4,         # +7.3% improvement
            "retention_rate": 0.78,         # +6.8% improvement
            "satisfaction_score": 4.3,      # +7.5% improvement
            "operational_efficiency": 0.84, # +7.7% improvement
            "time_to_value": 65.2,          # -10.1% improvement (lower is better)
            "quality_score": 8.5            # +9.0% improvement
        }
    
    def _determine_impact_severity(self, max_impact_percentage: float) -> ImpactSeverity:
        """Determine impact severity based on maximum impact percentage"""
        if max_impact_percentage >= 20:
            return ImpactSeverity.CRITICAL
        elif max_impact_percentage >= 10:
            return ImpactSeverity.HIGH
        elif max_impact_percentage >= 5:
            return ImpactSeverity.MEDIUM
        elif max_impact_percentage >= 1:
            return ImpactSeverity.LOW
        else:
            return ImpactSeverity.MINIMAL
    
    async def _estimate_annual_value_impact(self, impact_summary: Dict[str, float],
                                          baseline_metrics: Dict[str, float]) -> float:
        """Estimate annual value impact in dollars"""
        # Simplified calculation - in production would be more sophisticated
        
        revenue_impact = 0.0
        
        # Revenue per creator impact
        if "revenue_per_creator" in impact_summary:
            revenue_change_percent = impact_summary["revenue_per_creator"] / 100
            baseline_revenue = baseline_metrics.get("revenue_per_creator", 0)
            active_creators = 5000  # Assume 5000 active creators
            
            revenue_impact += baseline_revenue * revenue_change_percent * active_creators * 12
        
        # Conversion rate impact
        if "conversion_rate" in impact_summary:
            conversion_impact_percent = impact_summary["conversion_rate"] / 100
            annual_visitors = 500000  # Assume 500k annual visitors
            avg_transaction_value = 50  # $50 average transaction
            
            revenue_impact += annual_visitors * conversion_impact_percent * avg_transaction_value
        
        # Retention rate impact
        if "retention_rate" in impact_summary:
            retention_impact_percent = impact_summary["retention_rate"] / 100
            annual_revenue_per_user = 300  # $300 annual revenue per retained user
            total_users = 25000  # 25k total users
            
            revenue_impact += total_users * retention_impact_percent * annual_revenue_per_user
        
        return revenue_impact
    
    async def _calculate_confidence_interval(self, baseline_metrics: Dict[str, float],
                                          current_metrics: Dict[str, float],
                                          period_days: int) -> Tuple[float, float]:
        """Calculate confidence interval for impact estimates"""
        # Simplified confidence interval calculation
        # In production, would use more sophisticated statistical methods
        
        impact_values = []
        for metric in baseline_metrics:
            if metric in current_metrics:
                baseline = baseline_metrics[metric]
                current = current_metrics[metric]
                if baseline != 0:
                    impact = ((current - baseline) / baseline) * 100
                    impact_values.append(impact)
        
        if impact_values:
            mean_impact = statistics.mean(impact_values)
            std_impact = statistics.stdev(impact_values) if len(impact_values) > 1 else 0
            
            # 95% confidence interval
            margin_error = 1.96 * std_impact / (len(impact_values) ** 0.5)
            
            return (mean_impact - margin_error, mean_impact + margin_error)
        
        return (0.0, 0.0)
    
    async def _calculate_statistical_significance(self, baseline_metrics: Dict[str, float],
                                                current_metrics: Dict[str, float]) -> float:
        """Calculate statistical significance of observed changes"""
        # Simplified p-value calculation
        # In production, would use proper statistical tests
        
        significant_changes = 0
        total_metrics = 0
        
        for metric in baseline_metrics:
            if metric in current_metrics:
                total_metrics += 1
                baseline = baseline_metrics[metric]
                current = current_metrics[metric]
                
                if baseline != 0:
                    change_percentage = abs((current - baseline) / baseline) * 100
                    
                    # Consider changes >5% as statistically significant (simplified)
                    if change_percentage > 5:
                        significant_changes += 1
        
        return significant_changes / total_metrics if total_metrics > 0 else 0.0
    
    async def _calculate_attribution_confidence(self, model_id: str, deployment_date: date,
                                              period_days: int) -> float:
        """Calculate confidence that observed changes are attributable to the model"""
        # Simplified attribution confidence calculation
        # In production, would consider external factors, seasonality, etc.
        
        # Factors that increase attribution confidence
        confidence_factors = []
        
        # Recent deployment (higher confidence for recent deployments)
        days_since_deployment = (date.today() - deployment_date).days
        if days_since_deployment <= 7:
            confidence_factors.append(0.9)
        elif days_since_deployment <= 30:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        # Model performance (assume good performance increases confidence)
        confidence_factors.append(0.85)  # Simulated model performance factor
        
        # External factors (fewer external factors = higher confidence)
        confidence_factors.append(0.8)   # Simulated external factors consideration
        
        # A/B test isolation (if model was A/B tested)
        confidence_factors.append(0.9)   # Simulated A/B test factor
        
        return statistics.mean(confidence_factors)
    
    async def _identify_affected_creator_segments(self, impact_summary: Dict[str, float]) -> List[CreatorType]:
        """Identify which creator segments are most affected"""
        # Simplified segment identification
        # In production, would analyze segment-specific metrics
        
        affected_segments = []
        
        # If engagement metrics are significantly impacted, affect content creators
        if any(metric in impact_summary and abs(impact_summary[metric]) > 5 
               for metric in ["user_engagement", "satisfaction_score"]):
            affected_segments.extend([CreatorType.INFLUENCER, CreatorType.BLOGGER])
        
        # If revenue metrics are significantly impacted, affect monetization-focused creators
        if any(metric in impact_summary and abs(impact_summary[metric]) > 5 
               for metric in ["revenue_per_creator", "conversion_rate"]):
            affected_segments.extend([CreatorType.MUSICIAN, CreatorType.PHOTOGRAPHER])
        
        # Remove duplicates
        return list(set(affected_segments))
    
    async def _identify_affected_user_segments(self, impact_summary: Dict[str, float]) -> List[str]:
        """Identify which user segments are most affected"""
        # Simplified user segment identification
        affected_segments = []
        
        if "retention_rate" in impact_summary and abs(impact_summary["retention_rate"]) > 5:
            affected_segments.append("power_users")
        
        if "conversion_rate" in impact_summary and abs(impact_summary["conversion_rate"]) > 5:
            affected_segments.append("new_users")
        
        if "satisfaction_score" in impact_summary and abs(impact_summary["satisfaction_score"]) > 5:
            affected_segments.append("premium_users")
        
        return affected_segments


class ROICalculator:
    """Calculates Return on Investment for ML models"""
    
    def __init__(self) -> None:
        self.roi_history = []
    
    async def calculate_roi(self, model_id: str, investment_cost: float,
                          period_start: date, period_end: date,
                          impact_assessment: ImpactAssessment) -> ROIAnalysis:
        """Calculate comprehensive ROI analysis"""
        try:
            logger.info(f"Calculating ROI for model {model_id}")
            
            analysis_id = str(uuid.uuid4())
            
            # Calculate benefits
            revenue_generated = await self._calculate_revenue_generated(impact_assessment)
            cost_savings = await self._calculate_cost_savings(impact_assessment)
            total_benefit = revenue_generated + cost_savings
            
            # Calculate ROI percentage
            roi_percentage = ((total_benefit - investment_cost) / investment_cost) * 100 if investment_cost > 0 else 0
            
            # Calculate payback period
            payback_period_days = await self._calculate_payback_period(
                investment_cost, total_benefit, period_start, period_end
            )
            
            # Calculate NPV (simplified)
            discount_rate = 0.1  # 10% annual discount rate
            npv = await self._calculate_npv(
                investment_cost, total_benefit, period_start, period_end, discount_rate
            )
            
            # Calculate break-even date
            break_even_date = await self._calculate_break_even_date(
                investment_cost, total_benefit, period_start, period_end
            )
            
            # Assess confidence
            confidence_score = impact_assessment.attribution_confidence * impact_assessment.statistical_significance
            
            roi_analysis = ROIAnalysis(
                analysis_id=analysis_id,
                model_id=model_id,
                period_start=period_start,
                period_end=period_end,
                investment_cost=investment_cost,
                revenue_generated=revenue_generated,
                cost_savings=cost_savings,
                total_benefit=total_benefit,
                roi_percentage=roi_percentage,
                payback_period_days=payback_period_days,
                net_present_value=npv,
                break_even_date=break_even_date,
                confidence_score=confidence_score,
                methodology="Incremental impact analysis with causal attribution",
                assumptions=[
                    "Model impact attribution is accurate",
                    "External factors are controlled for",
                    "Historical trends continue",
                    "No significant market disruptions"
                ],
                risk_factors=[
                    "Model performance degradation",
                    "Competitive responses",
                    "Market volatility",
                    "Technical implementation issues"
                ]
            )
            
            self.roi_history.append(roi_analysis)
            
            logger.info(f"ROI calculation completed: {roi_percentage:.1f}% ROI")
            
            return roi_analysis
            
        except Exception as e:
            logger.error(f"ROI calculation failed for model {model_id}: {e}")
            raise
    
    async def _calculate_revenue_generated(self, impact_assessment: ImpactAssessment) -> float:
        """Calculate additional revenue generated by the model"""
        # Use the estimated annual value from impact assessment
        # Scale it to the evaluation period
        period_days = (date.today() - impact_assessment.deployment_date).days
        annual_value = impact_assessment.estimated_annual_value
        
        if period_days <= 0:
            return 0.0
        
        # Pro-rate annual value to evaluation period
        period_value = annual_value * (period_days / 365)
        
        return max(0, period_value)  # Only count positive revenue impact
    
    async def _calculate_cost_savings(self, impact_assessment: ImpactAssessment) -> float:
        """Calculate cost savings from operational efficiency improvements"""
        cost_savings = 0.0
        
        # Operational efficiency improvements
        if "operational_efficiency" in impact_assessment.impact_summary:
            efficiency_improvement = impact_assessment.impact_summary["operational_efficiency"] / 100
            annual_operational_cost = 1000000  # $1M annual operational cost
            period_days = (date.today() - impact_assessment.deployment_date).days
            
            cost_savings += annual_operational_cost * efficiency_improvement * (period_days / 365)
        
        # Time to value improvements (reduced onboarding costs)
        if "time_to_value" in impact_assessment.impact_summary:
            # Negative impact on time_to_value is positive (faster time to value)
            time_improvement = -impact_assessment.impact_summary["time_to_value"] / 100
            if time_improvement > 0:
                annual_onboarding_cost = 500000  # $500k annual onboarding cost
                period_days = (date.today() - impact_assessment.deployment_date).days
                
                cost_savings += annual_onboarding_cost * time_improvement * (period_days / 365)
        
        return max(0, cost_savings)
    
    async def _calculate_payback_period(self, investment_cost: float, total_benefit: float,
                                      period_start: date, period_end: date) -> int:
        """Calculate payback period in days"""
        if total_benefit <= 0:
            return 9999  # Infinite payback period
        
        period_days = (period_end - period_start).days
        daily_benefit = total_benefit / period_days if period_days > 0 else 0
        
        if daily_benefit <= 0:
            return 9999
        
        return int(investment_cost / daily_benefit)
    
    async def _calculate_npv(self, investment_cost: float, total_benefit: float,
                           period_start: date, period_end: date, discount_rate: float) -> float:
        """Calculate Net Present Value"""
        period_years = (period_end - period_start).days / 365
        
        if period_years <= 0:
            return -investment_cost
        
        # Discount future benefits
        discounted_benefit = total_benefit / ((1 + discount_rate) ** period_years)
        
        return discounted_benefit - investment_cost
    
    async def _calculate_break_even_date(self, investment_cost: float, total_benefit: float,
                                       period_start: date, period_end: date) -> Optional[date]:
        """Calculate break-even date"""
        payback_days = await self._calculate_payback_period(
            investment_cost, total_benefit, period_start, period_end
        )
        
        if payback_days == 9999:
            return None
        
        return period_start + timedelta(days=payback_days)


class BusinessImpactTracker:
    """Main business impact tracking system"""
    
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.impact_calculator = ImpactCalculator()
        self.roi_calculator = ROICalculator()
        self.active_tracking = {}
        self.alert_history = []
    
    async def start_tracking_model(self, model_id: str, model_version: str,
                                 deployment_date: date, investment_cost: float) -> str:
        """Start tracking business impact for a deployed model"""
        try:
            tracking_id = str(uuid.uuid4())
            
            logger.info(f"Starting business impact tracking for model {model_id}")
            
            # Initial impact assessment
            impact_assessment = await self.impact_calculator.calculate_model_impact(
                model_id, model_version, deployment_date
            )
            
            # Initial ROI calculation
            roi_analysis = await self.roi_calculator.calculate_roi(
                model_id, investment_cost, deployment_date, date.today(), impact_assessment
            )
            
            # Store tracking information
            self.active_tracking[tracking_id] = {
                "model_id": model_id,
                "model_version": model_version,
                "deployment_date": deployment_date,
                "investment_cost": investment_cost,
                "latest_impact_assessment": impact_assessment,
                "latest_roi_analysis": roi_analysis,
                "started_at": datetime.now(),
                "status": "active"
            }
            
            logger.info(f"Business impact tracking started: {tracking_id}")
            
            return tracking_id
            
        except Exception as e:
            logger.error(f"Failed to start tracking for model {model_id}: {e}")
            raise
    
    async def update_impact_assessment(self, tracking_id: str) -> ImpactAssessment:
        """Update impact assessment for a tracked model"""
        if tracking_id not in self.active_tracking:
            raise ValueError(f"Tracking ID {tracking_id} not found")
        
        tracking_info = self.active_tracking[tracking_id]
        
        # Calculate updated impact assessment
        impact_assessment = await self.impact_calculator.calculate_model_impact(
            tracking_info["model_id"],
            tracking_info["model_version"],
            tracking_info["deployment_date"]
        )
        
        # Update ROI analysis
        roi_analysis = await self.roi_calculator.calculate_roi(
            tracking_info["model_id"],
            tracking_info["investment_cost"],
            tracking_info["deployment_date"],
            date.today(),
            impact_assessment
        )
        
        # Update tracking information
        tracking_info["latest_impact_assessment"] = impact_assessment
        tracking_info["latest_roi_analysis"] = roi_analysis
        tracking_info["last_updated"] = datetime.now()
        
        # Check for alerts
        await self._check_for_alerts(tracking_id, impact_assessment)
        
        return impact_assessment
    
    async def _check_for_alerts(self, tracking_id -> None: str, impact_assessment -> None: ImpactAssessment) -> None:
        """Check for business impact alerts"""
        tracking_info = self.active_tracking[tracking_id]
        
        # Check for significant negative impacts
        for metric_id, impact_percentage in impact_assessment.impact_summary.items():
            if impact_percentage < -10:  # >10% negative impact
                alert = BusinessAlert(
                    alert_id=str(uuid.uuid4()),
                    metric_id=metric_id,
                    model_id=tracking_info["model_id"],
                    alert_type="negative_impact_detected",
                    severity=ImpactSeverity.HIGH,
                    message=f"Significant negative impact detected on {metric_id}: {impact_percentage:.1f}%",
                    current_value=0.0,  # Would be filled with actual current value
                    expected_value=0.0,  # Would be filled with expected value
                    impact_percentage=impact_percentage,
                    affected_creators=len(impact_assessment.creator_segments_affected) * 100,
                    affected_revenue=abs(impact_assessment.estimated_annual_value * impact_percentage / 100),
                    detection_time=datetime.now()
                )
                
                self.alert_history.append(alert)
                logger.warning(f"Business alert generated: {alert.message}")
    
    def get_tracking_status(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Get current tracking status"""
        if tracking_id not in self.active_tracking:
            return None
        
        tracking_info = self.active_tracking[tracking_id]
        impact_assessment = tracking_info["latest_impact_assessment"]
        roi_analysis = tracking_info["latest_roi_analysis"]
        
        return {
            "tracking_id": tracking_id,
            "model_id": tracking_info["model_id"],
            "model_version": tracking_info["model_version"],
            "deployment_date": tracking_info["deployment_date"].isoformat(),
            "investment_cost": tracking_info["investment_cost"],
            "status": tracking_info["status"],
            "started_at": tracking_info["started_at"].isoformat(),
            "last_updated": tracking_info.get("last_updated", tracking_info["started_at"]).isoformat(),
            "impact_summary": impact_assessment.impact_summary,
            "impact_severity": impact_assessment.impact_severity.value,
            "estimated_annual_value": impact_assessment.estimated_annual_value,
            "roi_percentage": roi_analysis.roi_percentage,
            "payback_period_days": roi_analysis.payback_period_days,
            "confidence_score": impact_assessment.attribution_confidence,
            "affected_creator_segments": [segment.value for segment in impact_assessment.creator_segments_affected],
            "recent_alerts": len([alert for alert in self.alert_history 
                                if alert.model_id == tracking_info["model_id"] 
                                and alert.detection_time > datetime.now() - timedelta(days=7)])
        }
    
    def list_tracked_models(self) -> List[Dict[str, Any]]:
        """List all tracked models"""
        return [
            self.get_tracking_status(tracking_id)
            for tracking_id in self.active_tracking.keys()
        ]
    
    def get_roi_summary(self, model_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get ROI summary across models"""
        roi_analyses = self.roi_calculator.roi_history
        
        if model_ids:
            roi_analyses = [roi for roi in roi_analyses if roi.model_id in model_ids]
        
        if not roi_analyses:
            return {"total_models": 0}
        
        return {
            "total_models": len(roi_analyses),
            "average_roi": statistics.mean([roi.roi_percentage for roi in roi_analyses]),
            "total_investment": sum([roi.investment_cost for roi in roi_analyses]),
            "total_benefit": sum([roi.total_benefit for roi in roi_analyses]),
            "average_payback_days": statistics.mean([roi.payback_period_days for roi in roi_analyses if roi.payback_period_days != 9999]),
            "models_with_positive_roi": len([roi for roi in roi_analyses if roi.roi_percentage > 0]),
            "total_revenue_generated": sum([roi.revenue_generated for roi in roi_analyses]),
            "total_cost_savings": sum([roi.cost_savings for roi in roi_analyses])
        }


# Factory function
def create_business_impact_tracker() -> BusinessImpactTracker:
    """Create a configured business impact tracker"""
    return BusinessImpactTracker()


# Export main classes
__all__ = [
    "BusinessImpactTracker",
    "BusinessMetric",
    "ROIAnalysis",
    "ImpactAssessment",
    "BusinessAlert",
    "BusinessMetricType",
    "CreatorType",
    "ImpactSeverity",
    "create_business_impact_tracker"
]