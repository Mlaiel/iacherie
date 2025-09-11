"""
Lifetime Value Analytics Engine
=============================

Advanced customer lifetime value analysis system for Ainflue Distribution Platform.
Calculates predictive LTV, segment analysis, and optimization recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from collections import defaultdict
import json
import math

logger = logging.getLogger(__name__)

class LTVModel(Enum):
    """Lifetime value calculation models"""
    HISTORICAL = "historical"  # Based on actual historical data
    PREDICTIVE = "predictive"  # ML-based prediction
    COHORT_BASED = "cohort_based"  # Cohort analysis approach
    PROBABILISTIC = "probabilistic"  # BG/NBD or similar models
    SEGMENTED = "segmented"  # Segment-specific calculations

class CustomerSegment(Enum):
    """Customer segmentation categories"""
    HIGH_VALUE = "high_value"
    MEDIUM_VALUE = "medium_value"
    LOW_VALUE = "low_value"
    NEW_CUSTOMER = "new_customer"
    CHURNED = "churned"
    AT_RISK = "at_risk"
    LOYAL = "loyal"
    PREMIUM = "premium"

class RevenueType(Enum):
    """Types of revenue to track"""
    SUBSCRIPTION = "subscription"
    ONE_TIME_PURCHASE = "one_time_purchase"
    ADVERTISING = "advertising"
    COMMISSION = "commission"
    TIP = "tip"
    MERCHANDISE = "merchandise"
    COURSE_SALE = "course_sale"
    CONSULTATION = "consultation"

@dataclass
class CustomerTransaction:
    """Individual customer transaction record"""
    customer_id: str
    transaction_id: str
    transaction_date: datetime
    revenue_amount: float
    revenue_type: RevenueType
    platform: str
    content_id: Optional[str] = None
    acquisition_channel: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CustomerProfile:
    """Customer profile for LTV analysis"""
    customer_id: str
    first_transaction_date: datetime
    last_transaction_date: datetime
    total_revenue: float
    transaction_count: int
    avg_order_value: float
    purchase_frequency: float  # transactions per month
    tenure_days: int
    segment: CustomerSegment
    acquisition_channel: str
    preferred_platforms: List[str] = field(default_factory=list)
    churn_probability: float = 0.0
    predicted_ltv: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LTVSegmentAnalysis:
    """LTV analysis for a customer segment"""
    segment: CustomerSegment
    customer_count: int
    avg_ltv: float
    median_ltv: float
    ltv_percentiles: Dict[int, float] = field(default_factory=dict)
    avg_tenure_days: float = 0.0
    avg_order_value: float = 0.0
    avg_purchase_frequency: float = 0.0
    churn_rate: float = 0.0
    total_segment_value: float = 0.0
    growth_rate: float = 0.0

@dataclass
class LTVPrediction:
    """LTV prediction result"""
    customer_id: str
    current_ltv: float
    predicted_ltv_12m: float
    predicted_ltv_24m: float
    predicted_ltv_lifetime: float
    confidence_score: float
    key_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)

@dataclass
class LTVAnalysisResult:
    """Complete LTV analysis results"""
    analysis_date: datetime
    total_customers: int
    total_ltv: float
    avg_ltv: float
    median_ltv: float
    model_used: LTVModel
    segment_analysis: List[LTVSegmentAnalysis] = field(default_factory=list)
    top_customers: List[CustomerProfile] = field(default_factory=list)
    churn_predictions: List[LTVPrediction] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    ltv_distribution: Dict[str, Any] = field(default_factory=dict)

class LifetimeValueAnalytics:
    """
    Advanced lifetime value analytics engine
    
    Features:
    - Multiple LTV calculation models
    - Customer segmentation analysis
    - Predictive LTV modeling
    - Churn risk assessment
    - Revenue optimization insights
    - Channel attribution for LTV
    - Cohort-based LTV tracking
    """
    
    def __init__(self):
        self.customer_transactions: List[CustomerTransaction] = []
        self.customer_profiles: Dict[str, CustomerProfile] = {}
        self.analysis_cache: Dict[str, LTVAnalysisResult] = {}
        self._segment_thresholds = {
            CustomerSegment.HIGH_VALUE: 500.0,
            CustomerSegment.MEDIUM_VALUE: 100.0,
            CustomerSegment.LOW_VALUE: 20.0
        }
        
    async def add_transactions(self, transactions: List[CustomerTransaction]):
        """Add customer transaction data"""
        for transaction in transactions:
            self.customer_transactions.append(transaction)
            
            # Update customer profile
            await self._update_customer_profile(transaction)
            
        logger.info(f"Added {len(transactions)} transactions for LTV analysis")
        
    async def _update_customer_profile(self, transaction: CustomerTransaction):
        """Update or create customer profile based on transaction"""
        customer_id = transaction.customer_id
        
        if customer_id not in self.customer_profiles:
            # Create new profile
            profile = CustomerProfile(
                customer_id=customer_id,
                first_transaction_date=transaction.transaction_date,
                last_transaction_date=transaction.transaction_date,
                total_revenue=transaction.revenue_amount,
                transaction_count=1,
                avg_order_value=transaction.revenue_amount,
                purchase_frequency=0.0,  # Will be calculated later
                tenure_days=0,
                segment=CustomerSegment.NEW_CUSTOMER,
                acquisition_channel=transaction.acquisition_channel or "unknown",
                preferred_platforms=[transaction.platform]
            )
            self.customer_profiles[customer_id] = profile
        else:
            # Update existing profile
            profile = self.customer_profiles[customer_id]
            profile.last_transaction_date = max(profile.last_transaction_date, transaction.transaction_date)
            profile.total_revenue += transaction.revenue_amount
            profile.transaction_count += 1
            profile.avg_order_value = profile.total_revenue / profile.transaction_count
            
            # Update tenure
            profile.tenure_days = (profile.last_transaction_date - profile.first_transaction_date).days
            
            # Update purchase frequency (transactions per month)
            if profile.tenure_days > 0:
                profile.purchase_frequency = profile.transaction_count / (profile.tenure_days / 30.44)  # avg days per month
            else:
                profile.purchase_frequency = profile.transaction_count
                
            # Update preferred platforms
            if transaction.platform not in profile.preferred_platforms:
                profile.preferred_platforms.append(transaction.platform)
                
        # Update customer segment
        await self._update_customer_segment(profile)
        
    async def _update_customer_segment(self, profile: CustomerProfile):
        """Update customer segment based on behavior and value"""
        # Calculate recency (days since last purchase)
        days_since_last = (datetime.now(timezone.utc) - profile.last_transaction_date).days
        
        # Segment based on total revenue and behavior
        if profile.total_revenue >= self._segment_thresholds[CustomerSegment.HIGH_VALUE]:
            if days_since_last > 90:
                profile.segment = CustomerSegment.AT_RISK
            elif profile.purchase_frequency > 2:  # More than 2 transactions per month
                profile.segment = CustomerSegment.LOYAL
            else:
                profile.segment = CustomerSegment.HIGH_VALUE
        elif profile.total_revenue >= self._segment_thresholds[CustomerSegment.MEDIUM_VALUE]:
            if days_since_last > 60:
                profile.segment = CustomerSegment.AT_RISK
            else:
                profile.segment = CustomerSegment.MEDIUM_VALUE
        elif profile.total_revenue >= self._segment_thresholds[CustomerSegment.LOW_VALUE]:
            if days_since_last > 30:
                profile.segment = CustomerSegment.AT_RISK
            else:
                profile.segment = CustomerSegment.LOW_VALUE
        else:
            if days_since_last > 180:
                profile.segment = CustomerSegment.CHURNED
            elif profile.tenure_days < 30:
                profile.segment = CustomerSegment.NEW_CUSTOMER
            else:
                profile.segment = CustomerSegment.LOW_VALUE
                
    async def analyze_ltv(
        self, 
        model: LTVModel = LTVModel.HISTORICAL,
        include_predictions: bool = True,
        segment_analysis: bool = True
    ) -> LTVAnalysisResult:
        """
        Perform comprehensive LTV analysis
        
        Args:
            model: LTV calculation model to use
            include_predictions: Whether to include predictive analysis
            segment_analysis: Whether to perform segment-level analysis
            
        Returns:
            Complete LTV analysis results
        """
        logger.info(f"Performing LTV analysis using {model.value} model")
        
        # Calculate LTV for all customers
        await self._calculate_customer_ltv(model)
        
        # Basic statistics
        ltvs = [profile.predicted_ltv for profile in self.customer_profiles.values()]
        total_customers = len(self.customer_profiles)
        total_ltv = sum(ltvs)
        avg_ltv = total_ltv / total_customers if total_customers > 0 else 0.0
        median_ltv = np.median(ltvs) if ltvs else 0.0
        
        # LTV distribution
        ltv_distribution = await self._calculate_ltv_distribution(ltvs)
        
        # Segment analysis
        segment_analyses = []
        if segment_analysis:
            segment_analyses = await self._analyze_segments()
            
        # Top customers
        top_customers = sorted(
            self.customer_profiles.values(), 
            key=lambda p: p.predicted_ltv, 
            reverse=True
        )[:20]
        
        # Churn predictions
        churn_predictions = []
        if include_predictions:
            churn_predictions = await self._generate_churn_predictions()
            
        # Generate insights and recommendations
        insights = await self._generate_ltv_insights(segment_analyses, ltvs)
        recommendations = await self._generate_ltv_recommendations(segment_analyses, churn_predictions)
        
        result = LTVAnalysisResult(
            analysis_date=datetime.now(timezone.utc),
            total_customers=total_customers,
            total_ltv=total_ltv,
            avg_ltv=avg_ltv,
            median_ltv=median_ltv,
            model_used=model,
            segment_analysis=segment_analyses,
            top_customers=top_customers,
            churn_predictions=churn_predictions,
            insights=insights,
            recommendations=recommendations,
            ltv_distribution=ltv_distribution
        )
        
        # Cache result
        cache_key = f"{model.value}_{datetime.now().strftime('%Y%m%d')}"
        self.analysis_cache[cache_key] = result
        
        logger.info(f"LTV analysis completed: {total_customers} customers, avg LTV ${avg_ltv:.2f}")
        return result
        
    async def _calculate_customer_ltv(self, model: LTVModel):
        """Calculate LTV for all customers based on selected model"""
        for profile in self.customer_profiles.values():
            if model == LTVModel.HISTORICAL:
                profile.predicted_ltv = await self._calculate_historical_ltv(profile)
            elif model == LTVModel.PREDICTIVE:
                profile.predicted_ltv = await self._calculate_predictive_ltv(profile)
            elif model == LTVModel.COHORT_BASED:
                profile.predicted_ltv = await self._calculate_cohort_ltv(profile)
            elif model == LTVModel.PROBABILISTIC:
                profile.predicted_ltv = await self._calculate_probabilistic_ltv(profile)
            elif model == LTVModel.SEGMENTED:
                profile.predicted_ltv = await self._calculate_segmented_ltv(profile)
                
    async def _calculate_historical_ltv(self, profile: CustomerProfile) -> float:
        """Calculate LTV based on historical transaction data"""
        return profile.total_revenue
        
    async def _calculate_predictive_ltv(self, profile: CustomerProfile) -> float:
        """Calculate predictive LTV using behavioral patterns"""
        # Simple predictive model based on recency, frequency, monetary value
        
        # Base LTV on current revenue
        base_ltv = profile.total_revenue
        
        # Adjust based on purchase frequency
        frequency_multiplier = min(profile.purchase_frequency * 0.5, 3.0)  # Cap at 3x
        
        # Adjust based on tenure (longer tenure = higher future value)
        tenure_months = profile.tenure_days / 30.44
        tenure_multiplier = 1 + (tenure_months * 0.1)
        
        # Adjust based on recent activity
        days_since_last = (datetime.now(timezone.utc) - profile.last_transaction_date).days
        recency_multiplier = max(0.5, 1 - (days_since_last / 365))  # Decay over a year
        
        # Calculate predicted future value
        predicted_future = base_ltv * frequency_multiplier * tenure_multiplier * recency_multiplier
        
        return min(predicted_future, base_ltv * 5)  # Cap at 5x current value
        
    async def _calculate_cohort_ltv(self, profile: CustomerProfile) -> float:
        """Calculate LTV based on cohort behavior"""
        # Find customers from same acquisition period (month)
        acquisition_month = profile.first_transaction_date.replace(day=1)
        cohort_customers = [
            p for p in self.customer_profiles.values()
            if p.first_transaction_date.replace(day=1) == acquisition_month
        ]
        
        if len(cohort_customers) < 5:  # Not enough data for cohort analysis
            return await self._calculate_historical_ltv(profile)
            
        # Calculate cohort averages
        cohort_avg_revenue = sum(p.total_revenue for p in cohort_customers) / len(cohort_customers)
        cohort_avg_frequency = sum(p.purchase_frequency for p in cohort_customers) / len(cohort_customers)
        
        # Adjust individual LTV based on cohort performance
        individual_factor = profile.total_revenue / cohort_avg_revenue if cohort_avg_revenue > 0 else 1.0
        frequency_factor = profile.purchase_frequency / cohort_avg_frequency if cohort_avg_frequency > 0 else 1.0
        
        cohort_ltv = cohort_avg_revenue * individual_factor * frequency_factor
        
        return cohort_ltv
        
    async def _calculate_probabilistic_ltv(self, profile: CustomerProfile) -> float:
        """Calculate LTV using probabilistic model (simplified BG/NBD)"""
        # Simplified version of BG/NBD model
        
        # Parameters (would normally be fitted from data)
        r = 0.5  # shape parameter for transaction rate
        alpha = 1.0  # scale parameter for transaction rate
        a = 1.0  # shape parameter for dropout rate
        b = 2.0  # scale parameter for dropout rate
        
        # Calculate expected number of future transactions
        if profile.tenure_days > 0:
            # Simplified calculation
            transaction_rate = profile.transaction_count / (profile.tenure_days / 30.44)
            expected_lifetime_months = 12  # Assume 12 month horizon
            
            # Probability customer is still active
            p_active = (b + profile.tenure_days/30.44) / (a + b + profile.tenure_days/30.44)
            
            # Expected future transactions
            expected_future_transactions = p_active * transaction_rate * expected_lifetime_months
            
            # Expected LTV
            ltv = profile.total_revenue + (expected_future_transactions * profile.avg_order_value)
        else:
            ltv = profile.avg_order_value * 2  # Minimum assumption for new customers
            
        return ltv
        
    async def _calculate_segmented_ltv(self, profile: CustomerProfile) -> float:
        """Calculate LTV based on customer segment characteristics"""
        segment_multipliers = {
            CustomerSegment.HIGH_VALUE: 3.0,
            CustomerSegment.MEDIUM_VALUE: 2.0,
            CustomerSegment.LOW_VALUE: 1.2,
            CustomerSegment.NEW_CUSTOMER: 1.5,
            CustomerSegment.CHURNED: 0.1,
            CustomerSegment.AT_RISK: 0.8,
            CustomerSegment.LOYAL: 3.5,
            CustomerSegment.PREMIUM: 4.0
        }
        
        base_ltv = profile.total_revenue
        multiplier = segment_multipliers.get(profile.segment, 1.0)
        
        return base_ltv * multiplier
        
    async def _calculate_ltv_distribution(self, ltvs: List[float]) -> Dict[str, Any]:
        """Calculate LTV distribution statistics"""
        if not ltvs:
            return {}
            
        ltvs_array = np.array(ltvs)
        
        return {
            "min": float(np.min(ltvs_array)),
            "max": float(np.max(ltvs_array)),
            "mean": float(np.mean(ltvs_array)),
            "median": float(np.median(ltvs_array)),
            "std": float(np.std(ltvs_array)),
            "percentiles": {
                "25th": float(np.percentile(ltvs_array, 25)),
                "75th": float(np.percentile(ltvs_array, 75)),
                "90th": float(np.percentile(ltvs_array, 90)),
                "95th": float(np.percentile(ltvs_array, 95)),
                "99th": float(np.percentile(ltvs_array, 99))
            },
            "distribution_buckets": self._create_ltv_buckets(ltvs_array)
        }
        
    def _create_ltv_buckets(self, ltvs: np.ndarray) -> List[Dict[str, Any]]:
        """Create LTV distribution buckets"""
        if len(ltvs) == 0:
            return []
            
        max_ltv = np.max(ltvs)
        bucket_size = max(10, max_ltv / 10)  # 10 buckets
        
        buckets = []
        for i in range(10):
            bucket_min = i * bucket_size
            bucket_max = (i + 1) * bucket_size
            count = np.sum((ltvs >= bucket_min) & (ltvs < bucket_max))
            
            buckets.append({
                "range": f"${bucket_min:.0f}-${bucket_max:.0f}",
                "count": int(count),
                "percentage": float(count / len(ltvs) * 100)
            })
            
        return buckets
        
    async def _analyze_segments(self) -> List[LTVSegmentAnalysis]:
        """Perform segment-level LTV analysis"""
        segment_data = defaultdict(list)
        
        # Group customers by segment
        for profile in self.customer_profiles.values():
            segment_data[profile.segment].append(profile)
            
        segment_analyses = []
        
        for segment, customers in segment_data.items():
            if not customers:
                continue
                
            ltvs = [c.predicted_ltv for c in customers]
            revenues = [c.total_revenue for c in customers]
            tenures = [c.tenure_days for c in customers]
            aovs = [c.avg_order_value for c in customers]
            frequencies = [c.purchase_frequency for c in customers]
            
            # Calculate churn rate for segment
            churned_count = sum(1 for c in customers if c.segment == CustomerSegment.CHURNED)
            churn_rate = churned_count / len(customers) if customers else 0.0
            
            analysis = LTVSegmentAnalysis(
                segment=segment,
                customer_count=len(customers),
                avg_ltv=sum(ltvs) / len(ltvs) if ltvs else 0.0,
                median_ltv=np.median(ltvs) if ltvs else 0.0,
                ltv_percentiles={
                    25: float(np.percentile(ltvs, 25)) if ltvs else 0.0,
                    50: float(np.percentile(ltvs, 50)) if ltvs else 0.0,
                    75: float(np.percentile(ltvs, 75)) if ltvs else 0.0,
                    90: float(np.percentile(ltvs, 90)) if ltvs else 0.0
                },
                avg_tenure_days=sum(tenures) / len(tenures) if tenures else 0.0,
                avg_order_value=sum(aovs) / len(aovs) if aovs else 0.0,
                avg_purchase_frequency=sum(frequencies) / len(frequencies) if frequencies else 0.0,
                churn_rate=churn_rate,
                total_segment_value=sum(revenues)
            )
            
            segment_analyses.append(analysis)
            
        return segment_analyses
        
    async def _generate_churn_predictions(self) -> List[LTVPrediction]:
        """Generate churn risk predictions for customers"""
        predictions = []
        
        for profile in self.customer_profiles.values():
            # Simple churn probability calculation
            days_since_last = (datetime.now(timezone.utc) - profile.last_transaction_date).days
            
            # Risk factors
            risk_score = 0.0
            risk_factors = []
            
            # Recency risk
            if days_since_last > 90:
                risk_score += 0.4
                risk_factors.append("No recent activity (90+ days)")
            elif days_since_last > 30:
                risk_score += 0.2
                risk_factors.append("Declining activity")
                
            # Frequency risk
            if profile.purchase_frequency < 0.5:  # Less than 1 transaction per 2 months
                risk_score += 0.3
                risk_factors.append("Low purchase frequency")
                
            # Tenure risk
            if profile.tenure_days < 30:
                risk_score += 0.2
                risk_factors.append("New customer - not yet established")
                
            # Value risk
            if profile.avg_order_value < 10:
                risk_score += 0.1
                risk_factors.append("Low order values")
                
            churn_probability = min(risk_score, 0.95)
            
            # Generate recommendations
            recommendations = []
            if churn_probability > 0.7:
                recommendations.extend([
                    "Immediate re-engagement campaign needed",
                    "Offer personalized incentive to return",
                    "Reach out via preferred communication channel"
                ])
            elif churn_probability > 0.4:
                recommendations.extend([
                    "Monitor closely for further decline",
                    "Send targeted content based on preferences",
                    "Offer loyalty program enrollment"
                ])
                
            # Predict future LTV
            retention_probability = 1 - churn_probability
            predicted_ltv_12m = profile.predicted_ltv * retention_probability
            predicted_ltv_24m = predicted_ltv_12m * (retention_probability ** 2)
            
            prediction = LTVPrediction(
                customer_id=profile.customer_id,
                current_ltv=profile.total_revenue,
                predicted_ltv_12m=predicted_ltv_12m,
                predicted_ltv_24m=predicted_ltv_24m,
                predicted_ltv_lifetime=profile.predicted_ltv,
                confidence_score=max(0.6, 1 - (churn_probability * 0.5)),
                key_factors=[
                    f"Purchase frequency: {profile.purchase_frequency:.1f}/month",
                    f"Avg order value: ${profile.avg_order_value:.2f}",
                    f"Tenure: {profile.tenure_days} days"
                ],
                recommendations=recommendations,
                risk_factors=risk_factors
            )
            
            predictions.append(prediction)
            
        # Sort by churn risk (highest first)
        predictions.sort(key=lambda p: 1 - p.confidence_score, reverse=True)
        
        return predictions[:50]  # Return top 50 at-risk customers
        
    async def _generate_ltv_insights(
        self, 
        segment_analyses: List[LTVSegmentAnalysis], 
        ltvs: List[float]
    ) -> List[str]:
        """Generate insights from LTV analysis"""
        insights = []
        
        if not ltvs:
            return ["No customer data available for LTV analysis"]
            
        avg_ltv = sum(ltvs) / len(ltvs)
        
        # Overall LTV insights
        if avg_ltv > 200:
            insights.append(f"Strong customer lifetime value of ${avg_ltv:.2f} indicates effective monetization")
        elif avg_ltv > 50:
            insights.append(f"Moderate LTV of ${avg_ltv:.2f} with opportunities for optimization")
        else:
            insights.append(f"Low LTV of ${avg_ltv:.2f} suggests need for value enhancement strategies")
            
        # Segment insights
        if segment_analyses:
            high_value_segments = [s for s in segment_analyses if s.avg_ltv > avg_ltv * 1.5]
            if high_value_segments:
                best_segment = max(high_value_segments, key=lambda s: s.avg_ltv)
                insights.append(
                    f"{best_segment.segment.value} segment shows highest LTV (${best_segment.avg_ltv:.2f}) - "
                    f"focus acquisition on similar profiles"
                )
                
            # Churn insights
            high_churn_segments = [s for s in segment_analyses if s.churn_rate > 0.3]
            for segment in high_churn_segments:
                insights.append(
                    f"{segment.segment.value} segment has high churn rate ({segment.churn_rate:.1%}) - "
                    f"implement retention strategies"
                )
                
        # Distribution insights
        ltv_std = np.std(ltvs)
        ltv_mean = np.mean(ltvs)
        coefficient_of_variation = ltv_std / ltv_mean if ltv_mean > 0 else 0
        
        if coefficient_of_variation > 1.5:
            insights.append("High LTV variance suggests opportunity for customer segmentation strategies")
        elif coefficient_of_variation < 0.5:
            insights.append("Consistent LTV across customers indicates predictable business model")
            
        return insights
        
    async def _generate_ltv_recommendations(
        self, 
        segment_analyses: List[LTVSegmentAnalysis],
        churn_predictions: List[LTVPrediction]
    ) -> List[str]:
        """Generate actionable recommendations for LTV optimization"""
        recommendations = []
        
        # Segment-based recommendations
        if segment_analyses:
            # Find best performing segment
            best_segment = max(segment_analyses, key=lambda s: s.avg_ltv)
            recommendations.append(
                f"Scale acquisition for {best_segment.segment.value} segment - "
                f"shows ${best_segment.avg_ltv:.2f} avg LTV"
            )
            
            # Find segments with improvement potential
            low_performing = [s for s in segment_analyses if s.avg_ltv < best_segment.avg_ltv * 0.5]
            for segment in low_performing:
                if segment.avg_order_value < best_segment.avg_order_value:
                    recommendations.append(
                        f"Increase AOV for {segment.segment.value} segment through upselling/cross-selling"
                    )
                if segment.avg_purchase_frequency < best_segment.avg_purchase_frequency:
                    recommendations.append(
                        f"Improve purchase frequency for {segment.segment.value} segment with loyalty programs"
                    )
                    
        # Churn prevention recommendations
        high_risk_customers = len([p for p in churn_predictions if p.confidence_score < 0.5])
        if high_risk_customers > 0:
            recommendations.append(
                f"Implement immediate retention campaign for {high_risk_customers} high-risk customers"
            )
            
        # General LTV optimization
        recommendations.extend([
            "Implement customer success programs to increase retention",
            "Develop premium product tiers to increase average order value",
            "Create referral programs to leverage high-value customers",
            "Use predictive analytics to identify upselling opportunities"
        ])
        
        return recommendations
        
    async def predict_customer_ltv(self, customer_id: str) -> Optional[LTVPrediction]:
        """Get detailed LTV prediction for a specific customer"""
        if customer_id not in self.customer_profiles:
            return None
            
        profile = self.customer_profiles[customer_id]
        
        # Find in existing predictions
        churn_predictions = await self._generate_churn_predictions()
        for prediction in churn_predictions:
            if prediction.customer_id == customer_id:
                return prediction
                
        return None
        
    async def compare_ltv_by_channel(self) -> Dict[str, Any]:
        """Compare LTV performance by acquisition channel"""
        channel_data = defaultdict(list)
        
        for profile in self.customer_profiles.values():
            channel_data[profile.acquisition_channel].append(profile)
            
        channel_analysis = {}
        
        for channel, customers in channel_data.items():
            ltvs = [c.predicted_ltv for c in customers]
            channel_analysis[channel] = {
                "customer_count": len(customers),
                "avg_ltv": sum(ltvs) / len(ltvs) if ltvs else 0.0,
                "total_ltv": sum(ltvs),
                "avg_aov": sum(c.avg_order_value for c in customers) / len(customers) if customers else 0.0,
                "avg_frequency": sum(c.purchase_frequency for c in customers) / len(customers) if customers else 0.0
            }
            
        # Find best performing channel
        best_channel = max(channel_analysis.items(), key=lambda x: x[1]["avg_ltv"])
        
        return {
            "channel_performance": channel_analysis,
            "best_channel": {
                "name": best_channel[0],
                "avg_ltv": best_channel[1]["avg_ltv"],
                "customer_count": best_channel[1]["customer_count"]
            },
            "recommendations": [
                f"Increase investment in {best_channel[0]} channel - highest LTV source",
                "Analyze successful channel characteristics for replication",
                "Consider reducing spend on underperforming channels"
            ]
        }
    
    async def calculate_customer_ltv(self, customer_id: str, 
                                   model_type: LTVModel = LTVModel.HISTORICAL,
                                   prediction_months: int = 12) -> Dict[str, Any]:
        """
        Calculate lifetime value for a specific customer
        
        Args:
            customer_id: Customer identifier
            model_type: LTV calculation model to use
            prediction_months: Number of months to predict (for predictive models)
            
        Returns:
            Dict containing LTV calculation results
        """
        try:
            # Check if customer exists
            if customer_id not in self.customer_profiles:
                self.logger.warning(f"Customer {customer_id} not found in profiles. Returning zero LTV.")
                return {
                    'customer_id': customer_id,
                    'ltv_value': 0.0,
                    'model_used': model_type.value,
                    'confidence_score': 0.0,
                    'error': 'Customer profile not found'
                }
            
            customer_profile = self.customer_profiles[customer_id]
            
            # Use existing historical calculation method
            ltv_value = await self._calculate_historical_ltv(customer_profile)
            
            return {
                'customer_id': customer_id,
                'ltv_value': ltv_value,
                'model_used': model_type.value,
                'confidence_score': 0.9,
                'customer_segment': customer_profile.segment,
                'total_transactions': len(customer_profile.transaction_history),
                'calculated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Customer LTV calculation failed for {customer_id}: {e}")
            raise

# Usage example
async def example_usage():
    """Example usage of LifetimeValueAnalytics"""
    analytics = LifetimeValueAnalytics()
    
    # Generate sample transactions
    sample_transactions = []
    base_time = datetime.now(timezone.utc) - timedelta(days=365)
    
    for customer_id in range(1, 501):  # 500 customers
        customer_start = base_time + timedelta(days=customer_id % 300)
        
        # Number of transactions varies by customer
        transaction_count = max(1, int(np.random.poisson(3)))  # Average 3 transactions
        
        for transaction_num in range(transaction_count):
            transaction_date = customer_start + timedelta(days=transaction_num * 30 + np.random.randint(0, 30))
            revenue = max(5.0, np.random.normal(50, 25))  # Average $50, std $25
            
            transaction = CustomerTransaction(
                customer_id=f"customer_{customer_id}",
                transaction_id=f"txn_{customer_id}_{transaction_num}",
                transaction_date=transaction_date,
                revenue_amount=revenue,
                revenue_type=RevenueType.SUBSCRIPTION if transaction_num > 0 else RevenueType.ONE_TIME_PURCHASE,
                platform="instagram",
                acquisition_channel=["organic", "paid_social", "referral", "email"][customer_id % 4]
            )
            
            sample_transactions.append(transaction)
            
    await analytics.add_transactions(sample_transactions)
    
    # Perform LTV analysis
    result = await analytics.analyze_ltv(
        model=LTVModel.PREDICTIVE,
        include_predictions=True,
        segment_analysis=True
    )
    
    print(f"LTV Analysis Results:")
    print(f"Total Customers: {result.total_customers}")
    print(f"Average LTV: ${result.avg_ltv:.2f}")
    print(f"Median LTV: ${result.median_ltv:.2f}")
    print(f"Total LTV: ${result.total_ltv:.2f}")
    
    print(f"\nSegment Analysis:")
    for segment in result.segment_analysis:
        print(f"  {segment.segment.value}: {segment.customer_count} customers, ${segment.avg_ltv:.2f} avg LTV")
        
    print(f"\nTop Insights:")
    for insight in result.insights[:3]:
        print(f"  - {insight}")
        
    print(f"\nKey Recommendations:")
    for rec in result.recommendations[:3]:
        print(f"  - {rec}")
        
    # Channel comparison
    channel_comparison = await analytics.compare_ltv_by_channel()
    print(f"\nBest Channel: {channel_comparison['best_channel']['name']} "
          f"(${channel_comparison['best_channel']['avg_ltv']:.2f} avg LTV)")

if __name__ == "__main__":
    asyncio.run(example_usage())