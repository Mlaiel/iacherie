"""🏪 Merchant Analytics - Enterprise Merchant Intelligence Engine
==============================================================

Advanced merchant performance analysis and risk assessment for Creator Economy Platform.
Comprehensive merchant onboarding, behavior analysis, and business intelligence.

Performance Targets: < 50ms merchant analysis
Enterprise merchant analytics with predictive insights and risk management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from decimal import Decimal
from collections import defaultdict, deque
import statistics
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import structlog

logger = structlog.get_logger(__name__)

class MerchantCategory(Enum):
    """Merchant business categories for Creator Economy"""
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ARTIST = "artist"
    CONTENT_CREATOR = "content_creator"
    EDUCATOR = "educator"
    PODCASTER = "podcaster"
    DESIGNER = "designer"

class MerchantStatus(Enum):
    """Merchant account status"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    UNDER_REVIEW = "under_review"
    TERMINATED = "terminated"
    ONBOARDING = "onboarding"

class RiskLevel(Enum):
    """Merchant risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class OnboardingStage(Enum):
    """Merchant onboarding stages"""
    REGISTRATION = "registration"
    VERIFICATION = "verification"
    DOCUMENT_UPLOAD = "document_upload"
    COMPLIANCE_CHECK = "compliance_check"
    APPROVAL = "approval"
    ACTIVATION = "activation"
    COMPLETED = "completed"

@dataclass
class MerchantProfile:
    """Comprehensive merchant profile"""
    merchant_id: str
    business_name: str
    category: MerchantCategory
    status: MerchantStatus
    created_at: datetime
    country: str
    currency: str
    contact_email: str
    business_type: str
    tax_id: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    verified: bool = False
    verification_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MerchantMetrics:
    """Merchant performance metrics"""
    merchant_id: str
    period_start: datetime
    period_end: datetime
    total_volume: Decimal
    transaction_count: int
    average_transaction: Decimal
    success_rate: float
    chargeback_rate: float
    refund_rate: float
    revenue_share: Decimal
    growth_rate: float
    customer_count: int
    repeat_customer_rate: float

@dataclass
class RiskAssessment:
    """Merchant risk assessment"""
    merchant_id: str
    risk_level: RiskLevel
    risk_score: float
    risk_factors: List[str]
    assessment_date: datetime
    recommendations: List[str]
    next_review_date: datetime
    risk_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class OnboardingTracking:
    """Merchant onboarding progress tracking"""
    merchant_id: str
    current_stage: OnboardingStage
    started_at: datetime
    completed_stages: List[OnboardingStage]
    pending_actions: List[str]
    estimated_completion: Optional[datetime] = None
    completion_percentage: float = 0.0
    last_updated: Optional[datetime] = None

class MerchantAnalyzer:
    """Core merchant analysis engine"""
    
    def __init__(self):
        self.merchant_data = {}
        self.analytics_cache = {}
        
    async def analyze_merchant_performance(
        self,
        merchant_id: str,
        time_period: timedelta = timedelta(days=30),
        comparison_period: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Comprehensive merchant performance analysis"""
        try:
            start_time = time.perf_counter()
            
            # Get merchant profile
            merchant_profile = await self._get_merchant_profile(merchant_id)
            if not merchant_profile:
                raise ValueError(f"Merchant {merchant_id} not found")
            
            # Calculate current period metrics
            current_metrics = await self._calculate_period_metrics(
                merchant_id, time_period
            )
            
            # Calculate comparison metrics if requested
            comparison_metrics = None
            if comparison_period:
                comparison_metrics = await self._calculate_period_metrics(
                    merchant_id, comparison_period, offset=time_period
                )
            
            # Performance analysis
            performance_analysis = await self._analyze_performance_trends(
                current_metrics, comparison_metrics
            )
            
            # Customer analysis
            customer_analysis = await self._analyze_customer_behavior(
                merchant_id, time_period
            )
            
            # Revenue analysis
            revenue_analysis = await self._analyze_revenue_patterns(
                merchant_id, time_period
            )
            
            # Risk indicators
            risk_indicators = await self._assess_performance_risks(
                current_metrics, merchant_profile
            )
            
            result = {
                "merchant_id": merchant_id,
                "merchant_profile": {
                    "business_name": merchant_profile.business_name,
                    "category": merchant_profile.category.value,
                    "status": merchant_profile.status.value,
                    "verified": merchant_profile.verified,
                    "country": merchant_profile.country
                },
                "current_metrics": {
                    "total_volume": float(current_metrics.total_volume),
                    "transaction_count": current_metrics.transaction_count,
                    "average_transaction": float(current_metrics.average_transaction),
                    "success_rate": current_metrics.success_rate,
                    "chargeback_rate": current_metrics.chargeback_rate,
                    "growth_rate": current_metrics.growth_rate
                },
                "performance_analysis": performance_analysis,
                "customer_analysis": customer_analysis,
                "revenue_analysis": revenue_analysis,
                "risk_indicators": risk_indicators,
                "analysis_period": {
                    "start": (datetime.utcnow() - time_period).isoformat(),
                    "end": datetime.utcnow().isoformat()
                }
            }
            
            if comparison_metrics:
                result["comparison_metrics"] = {
                    "total_volume": float(comparison_metrics.total_volume),
                    "transaction_count": comparison_metrics.transaction_count,
                    "success_rate": comparison_metrics.success_rate,
                    "growth_rate": comparison_metrics.growth_rate
                }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Merchant performance analyzed",
                merchant_id=merchant_id,
                volume=float(current_metrics.total_volume),
                transactions=current_metrics.transaction_count,
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing merchant performance: {e}")
            raise
    
    async def _get_merchant_profile(self, merchant_id: str) -> Optional[MerchantProfile]:
        """Get merchant profile (mock implementation)"""
        # In production, this would fetch from database
        return MerchantProfile(
            merchant_id=merchant_id,
            business_name=f"Business {merchant_id}",
            category=MerchantCategory.CONTENT_CREATOR,
            status=MerchantStatus.ACTIVE,
            created_at=datetime.utcnow() - timedelta(days=90),
            country="US",
            currency="USD",
            contact_email=f"merchant{merchant_id}@example.com",
            business_type="individual",
            verified=True
        )
    
    async def _calculate_period_metrics(
        self,
        merchant_id: str,
        period: timedelta,
        offset: timedelta = timedelta(0)
    ) -> MerchantMetrics:
        """Calculate merchant metrics for specified period"""
        # Mock calculation - in production, would query transaction data
        base_volume = 10000 + hash(merchant_id) % 50000
        
        # Simulate realistic metrics with some variance
        total_volume = Decimal(str(base_volume * (1 + np.random.normal(0, 0.1))))
        transaction_count = int(base_volume / 100)
        average_transaction = total_volume / transaction_count if transaction_count > 0 else Decimal('0')
        
        return MerchantMetrics(
            merchant_id=merchant_id,
            period_start=datetime.utcnow() - period - offset,
            period_end=datetime.utcnow() - offset,
            total_volume=max(Decimal('0'), total_volume),
            transaction_count=transaction_count,
            average_transaction=average_transaction,
            success_rate=95.0 + np.random.normal(0, 2),
            chargeback_rate=0.5 + np.random.normal(0, 0.2),
            refund_rate=2.0 + np.random.normal(0, 0.5),
            revenue_share=total_volume * Decimal('0.03'),  # 3% platform fee
            growth_rate=10.0 + np.random.normal(0, 5),
            customer_count=max(1, int(transaction_count * 0.7)),
            repeat_customer_rate=30.0 + np.random.normal(0, 10)
        )
    
    async def _analyze_performance_trends(
        self,
        current_metrics: MerchantMetrics,
        comparison_metrics: Optional[MerchantMetrics]
    ) -> Dict[str, Any]:
        """Analyze performance trends"""
        trends = {}
        
        if comparison_metrics:
            # Volume trend
            volume_change = (
                (current_metrics.total_volume - comparison_metrics.total_volume) /
                comparison_metrics.total_volume * 100
            ) if comparison_metrics.total_volume > 0 else 0
            
            # Transaction count trend
            transaction_change = (
                (current_metrics.transaction_count - comparison_metrics.transaction_count) /
                comparison_metrics.transaction_count * 100
            ) if comparison_metrics.transaction_count > 0 else 0
            
            # Success rate trend
            success_rate_change = current_metrics.success_rate - comparison_metrics.success_rate
            
            trends = {
                "volume_trend": {
                    "change_percentage": float(volume_change),
                    "direction": "up" if volume_change > 0 else "down" if volume_change < 0 else "stable",
                    "significance": "high" if abs(volume_change) > 20 else "medium" if abs(volume_change) > 10 else "low"
                },
                "transaction_trend": {
                    "change_percentage": float(transaction_change),
                    "direction": "up" if transaction_change > 0 else "down" if transaction_change < 0 else "stable"
                },
                "success_rate_trend": {
                    "change_percentage": float(success_rate_change),
                    "direction": "up" if success_rate_change > 0 else "down" if success_rate_change < 0 else "stable"
                }
            }
        else:
            # Single period analysis
            trends = {
                "performance_rating": self._rate_performance(current_metrics),
                "growth_assessment": self._assess_growth(current_metrics.growth_rate)
            }
        
        return trends
    
    def _rate_performance(self, metrics: MerchantMetrics) -> str:
        """Rate overall merchant performance"""
        score = 0
        
        # Success rate scoring
        if metrics.success_rate >= 98:
            score += 40
        elif metrics.success_rate >= 95:
            score += 30
        elif metrics.success_rate >= 90:
            score += 20
        else:
            score += 10
        
        # Chargeback rate scoring (lower is better)
        if metrics.chargeback_rate <= 0.5:
            score += 30
        elif metrics.chargeback_rate <= 1.0:
            score += 20
        elif metrics.chargeback_rate <= 2.0:
            score += 10
        
        # Volume scoring
        if metrics.total_volume >= 100000:
            score += 30
        elif metrics.total_volume >= 50000:
            score += 20
        elif metrics.total_volume >= 10000:
            score += 10
        
        # Rating based on score
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "poor"
    
    def _assess_growth(self, growth_rate: float) -> str:
        """Assess growth rate"""
        if growth_rate >= 20:
            return "high_growth"
        elif growth_rate >= 10:
            return "moderate_growth"
        elif growth_rate >= 0:
            return "slow_growth"
        else:
            return "declining"
    
    async def _analyze_customer_behavior(
        self,
        merchant_id: str,
        period: timedelta
    ) -> Dict[str, Any]:
        """Analyze customer behavior patterns"""
        # Mock customer analysis
        return {
            "new_customers": 150 + hash(merchant_id) % 100,
            "returning_customers": 80 + hash(merchant_id) % 50,
            "customer_lifetime_value": float(500 + hash(merchant_id) % 1000),
            "average_order_frequency": 2.5 + (hash(merchant_id) % 100) / 100,
            "customer_segments": [
                {"segment": "high_value", "count": 25, "avg_spend": 800},
                {"segment": "regular", "count": 120, "avg_spend": 200},
                {"segment": "occasional", "count": 85, "avg_spend": 75}
            ],
            "retention_rate": 65.0 + (hash(merchant_id) % 20)
        }
    
    async def _analyze_revenue_patterns(
        self,
        merchant_id: str,
        period: timedelta
    ) -> Dict[str, Any]:
        """Analyze revenue patterns and trends"""
        # Mock revenue analysis
        daily_revenues = [
            1000 + np.random.normal(0, 200) + 500 * np.sin(i * 0.2)
            for i in range(int(period.days))
        ]
        
        return {
            "daily_average": float(np.mean(daily_revenues)),
            "peak_day_revenue": float(np.max(daily_revenues)),
            "lowest_day_revenue": float(np.min(daily_revenues)),
            "revenue_volatility": float(np.std(daily_revenues)),
            "trending": "upward" if daily_revenues[-7:] > daily_revenues[:7] else "downward",
            "seasonal_patterns": {
                "weekday_avg": float(np.mean(daily_revenues[::7])),  # Simulate weekdays
                "weekend_avg": float(np.mean(daily_revenues[5::7]))   # Simulate weekends
            }
        }
    
    async def _assess_performance_risks(
        self,
        metrics: MerchantMetrics,
        profile: MerchantProfile
    ) -> List[str]:
        """Assess performance-related risks"""
        risks = []
        
        if metrics.chargeback_rate > 2.0:
            risks.append("High chargeback rate - review transaction quality")
        
        if metrics.success_rate < 90:
            risks.append("Low success rate - investigate payment failures")
        
        if metrics.refund_rate > 5.0:
            risks.append("High refund rate - review product/service quality")
        
        if metrics.growth_rate < -10:
            risks.append("Declining growth - implement retention strategies")
        
        return risks

class OnboardingTracker:
    """Merchant onboarding progress tracker"""
    
    def __init__(self):
        self.onboarding_data = {}
        self.stage_requirements = self._initialize_stage_requirements()
    
    def _initialize_stage_requirements(self) -> Dict[OnboardingStage, List[str]]:
        """Initialize requirements for each onboarding stage"""
        return {
            OnboardingStage.REGISTRATION: [
                "basic_info_provided",
                "email_verified",
                "terms_accepted"
            ],
            OnboardingStage.VERIFICATION: [
                "identity_verified",
                "phone_verified",
                "address_verified"
            ],
            OnboardingStage.DOCUMENT_UPLOAD: [
                "business_license_uploaded",
                "tax_documents_uploaded",
                "bank_statements_uploaded"
            ],
            OnboardingStage.COMPLIANCE_CHECK: [
                "kyc_completed",
                "aml_screening_passed",
                "risk_assessment_completed"
            ],
            OnboardingStage.APPROVAL: [
                "manual_review_completed",
                "approval_decision_made",
                "approval_notification_sent"
            ],
            OnboardingStage.ACTIVATION: [
                "payment_methods_configured",
                "test_transactions_completed",
                "live_processing_enabled"
            ],
            OnboardingStage.COMPLETED: [
                "onboarding_survey_completed",
                "welcome_materials_sent",
                "account_fully_active"
            ]
        }
    
    async def track_merchant_onboarding(
        self,
        merchant_id: str,
        current_data: Dict[str, Any]
    ) -> OnboardingTracking:
        """Track merchant onboarding progress"""
        try:
            start_time = time.perf_counter()
            
            # Determine current stage
            current_stage = await self._determine_current_stage(current_data)
            
            # Calculate completed stages
            completed_stages = await self._get_completed_stages(current_data)
            
            # Calculate completion percentage
            completion_percentage = len(completed_stages) / len(OnboardingStage) * 100
            
            # Identify pending actions
            pending_actions = await self._identify_pending_actions(
                current_stage, current_data
            )
            
            # Estimate completion time
            estimated_completion = await self._estimate_completion_time(
                current_stage, len(pending_actions)
            )
            
            tracking = OnboardingTracking(
                merchant_id=merchant_id,
                current_stage=current_stage,
                started_at=current_data.get("started_at", datetime.utcnow()),
                completed_stages=completed_stages,
                pending_actions=pending_actions,
                estimated_completion=estimated_completion,
                completion_percentage=completion_percentage,
                last_updated=datetime.utcnow()
            )
            
            # Store tracking data
            self.onboarding_data[merchant_id] = tracking
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Onboarding tracked",
                merchant_id=merchant_id,
                current_stage=current_stage.value,
                completion_percentage=completion_percentage,
                duration_ms=duration_ms
            )
            
            return tracking
            
        except Exception as e:
            logger.error(f"Error tracking merchant onboarding: {e}")
            raise
    
    async def _determine_current_stage(
        self,
        current_data: Dict[str, Any]
    ) -> OnboardingStage:
        """Determine the current onboarding stage"""
        # Check stages in order
        for stage in OnboardingStage:
            requirements = self.stage_requirements[stage]
            stage_complete = all(
                current_data.get(req, False) for req in requirements
            )
            
            if not stage_complete:
                return stage
        
        return OnboardingStage.COMPLETED
    
    async def _get_completed_stages(
        self,
        current_data: Dict[str, Any]
    ) -> List[OnboardingStage]:
        """Get list of completed onboarding stages"""
        completed = []
        
        for stage in OnboardingStage:
            requirements = self.stage_requirements[stage]
            stage_complete = all(
                current_data.get(req, False) for req in requirements
            )
            
            if stage_complete:
                completed.append(stage)
            else:
                break  # Stop at first incomplete stage
        
        return completed
    
    async def _identify_pending_actions(
        self,
        current_stage: OnboardingStage,
        current_data: Dict[str, Any]
    ) -> List[str]:
        """Identify pending actions for current stage"""
        if current_stage == OnboardingStage.COMPLETED:
            return []
        
        requirements = self.stage_requirements[current_stage]
        pending = [
            req for req in requirements
            if not current_data.get(req, False)
        ]
        
        # Convert technical requirements to user-friendly actions
        action_mapping = {
            "basic_info_provided": "Complete business information",
            "email_verified": "Verify email address",
            "terms_accepted": "Accept terms and conditions",
            "identity_verified": "Verify identity documentation",
            "phone_verified": "Verify phone number",
            "address_verified": "Verify business address",
            "business_license_uploaded": "Upload business license",
            "tax_documents_uploaded": "Upload tax documentation",
            "bank_statements_uploaded": "Upload bank statements",
            "kyc_completed": "Complete KYC verification",
            "aml_screening_passed": "Pass AML screening",
            "risk_assessment_completed": "Complete risk assessment",
            "manual_review_completed": "Wait for manual review",
            "approval_decision_made": "Wait for approval decision",
            "payment_methods_configured": "Configure payment methods",
            "test_transactions_completed": "Complete test transactions"
        }
        
        return [action_mapping.get(req, req) for req in pending]
    
    async def _estimate_completion_time(
        self,
        current_stage: OnboardingStage,
        pending_actions_count: int
    ) -> Optional[datetime]:
        """Estimate onboarding completion time"""
        if current_stage == OnboardingStage.COMPLETED:
            return None
        
        # Estimated days per stage
        stage_estimates = {
            OnboardingStage.REGISTRATION: 1,
            OnboardingStage.VERIFICATION: 2,
            OnboardingStage.DOCUMENT_UPLOAD: 3,
            OnboardingStage.COMPLIANCE_CHECK: 5,
            OnboardingStage.APPROVAL: 7,
            OnboardingStage.ACTIVATION: 2,
            OnboardingStage.COMPLETED: 0
        }
        
        # Calculate remaining time
        remaining_stages = list(OnboardingStage)[
            list(OnboardingStage).index(current_stage):
        ]
        
        total_days = sum(stage_estimates[stage] for stage in remaining_stages)
        
        # Adjust based on pending actions
        total_days += pending_actions_count * 0.5  # 0.5 days per pending action
        
        return datetime.utcnow() + timedelta(days=total_days)

class PerformanceEvaluator:
    """Advanced merchant performance evaluation"""
    
    def __init__(self):
        self.evaluation_models = {}
        self.benchmarks = self._initialize_benchmarks()
    
    def _initialize_benchmarks(self) -> Dict[MerchantCategory, Dict[str, float]]:
        """Initialize industry benchmarks by merchant category"""
        return {
            MerchantCategory.MUSICIAN: {
                "avg_transaction": 25.0,
                "success_rate": 96.0,
                "chargeback_rate": 0.8,
                "growth_rate": 15.0
            },
            MerchantCategory.PHOTOGRAPHER: {
                "avg_transaction": 150.0,
                "success_rate": 97.5,
                "chargeback_rate": 0.3,
                "growth_rate": 12.0
            },
            MerchantCategory.BLOGGER: {
                "avg_transaction": 45.0,
                "success_rate": 95.5,
                "chargeback_rate": 1.2,
                "growth_rate": 18.0
            },
            MerchantCategory.CONTENT_CREATOR: {
                "avg_transaction": 35.0,
                "success_rate": 96.5,
                "chargeback_rate": 0.9,
                "growth_rate": 20.0
            }
        }
    
    async def evaluate_merchant_risk(
        self,
        merchant_id: str,
        merchant_data: Dict[str, Any],
        transaction_history: List[Dict[str, Any]]
    ) -> RiskAssessment:
        """Comprehensive merchant risk evaluation"""
        try:
            start_time = time.perf_counter()
            
            # Calculate risk factors
            risk_factors = await self._calculate_risk_factors(
                merchant_data, transaction_history
            )
            
            # Calculate overall risk score
            risk_score = await self._calculate_risk_score(risk_factors)
            
            # Determine risk level
            risk_level = await self._determine_risk_level(risk_score)
            
            # Generate recommendations
            recommendations = await self._generate_risk_recommendations(
                risk_factors, risk_level
            )
            
            # Calculate next review date
            next_review_date = await self._calculate_next_review_date(risk_level)
            
            assessment = RiskAssessment(
                merchant_id=merchant_id,
                risk_level=risk_level,
                risk_score=risk_score,
                risk_factors=risk_factors,
                assessment_date=datetime.utcnow(),
                recommendations=recommendations,
                next_review_date=next_review_date
            )
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Merchant risk evaluated",
                merchant_id=merchant_id,
                risk_level=risk_level.value,
                risk_score=risk_score,
                duration_ms=duration_ms
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error evaluating merchant risk: {e}")
            raise
    
    async def _calculate_risk_factors(
        self,
        merchant_data: Dict[str, Any],
        transaction_history: List[Dict[str, Any]]
    ) -> List[str]:
        """Calculate specific risk factors"""
        risk_factors = []
        
        # Account age risk
        created_at = merchant_data.get("created_at", datetime.utcnow())
        account_age_days = (datetime.utcnow() - created_at).days
        
        if account_age_days < 30:
            risk_factors.append("New merchant account (< 30 days)")
        
        # Transaction volume risk
        total_volume = sum(
            txn.get("amount", 0) for txn in transaction_history
        )
        
        if total_volume > 100000:  # High volume
            risk_factors.append("High transaction volume")
        
        # Geographic risk
        country = merchant_data.get("country", "")
        high_risk_countries = ["XX", "YY", "ZZ"]  # Example high-risk countries
        
        if country in high_risk_countries:
            risk_factors.append(f"High-risk country: {country}")
        
        # Business type risk
        business_type = merchant_data.get("business_type", "")
        if business_type == "high_risk_category":
            risk_factors.append("High-risk business category")
        
        # Chargeback risk
        chargebacks = [
            txn for txn in transaction_history
            if txn.get("status") == "chargeback"
        ]
        
        if len(chargebacks) > 5:
            risk_factors.append("High chargeback count")
        
        # Verification status
        if not merchant_data.get("verified", False):
            risk_factors.append("Unverified merchant account")
        
        return risk_factors
    
    async def _calculate_risk_score(self, risk_factors: List[str]) -> float:
        """Calculate numerical risk score (0-100)"""
        base_score = 0
        
        # Weight different risk factors
        factor_weights = {
            "New merchant account": 15,
            "High transaction volume": 20,
            "High-risk country": 25,
            "High-risk business category": 30,
            "High chargeback count": 35,
            "Unverified merchant account": 20
        }
        
        for factor in risk_factors:
            # Check if factor matches any weighted factor
            for weighted_factor, weight in factor_weights.items():
                if weighted_factor.lower() in factor.lower():
                    base_score += weight
                    break
            else:
                # Default weight for unspecified factors
                base_score += 10
        
        return min(100.0, base_score)
    
    async def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score"""
        if risk_score >= 80:
            return RiskLevel.CRITICAL
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _generate_risk_recommendations(
        self,
        risk_factors: List[str],
        risk_level: RiskLevel
    ) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        # General recommendations based on risk level
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Immediate review required",
                "Suspend high-value transactions",
                "Enhanced monitoring enabled"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Weekly monitoring recommended",
                "Implement transaction limits",
                "Require additional verification"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Monthly risk review",
                "Monitor chargeback rates",
                "Update verification documents"
            ])
        
        # Specific recommendations based on risk factors
        for factor in risk_factors:
            if "chargeback" in factor.lower():
                recommendations.append("Implement chargeback prevention measures")
            elif "unverified" in factor.lower():
                recommendations.append("Complete merchant verification process")
            elif "high-risk country" in factor.lower():
                recommendations.append("Enhanced due diligence required")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _calculate_next_review_date(self, risk_level: RiskLevel) -> datetime:
        """Calculate next risk review date"""
        review_intervals = {
            RiskLevel.CRITICAL: timedelta(days=7),
            RiskLevel.HIGH: timedelta(days=30),
            RiskLevel.MEDIUM: timedelta(days=90),
            RiskLevel.LOW: timedelta(days=180)
        }
        
        interval = review_intervals.get(risk_level, timedelta(days=90))
        return datetime.utcnow() + interval

class MerchantAnalytics:
    """Main merchant analytics orchestrator"""
    
    def __init__(self):
        self.merchant_analyzer = MerchantAnalyzer()
        self.onboarding_tracker = OnboardingTracker()
        self.performance_evaluator = PerformanceEvaluator()
        
    async def analyze_merchant_performance(
        self,
        merchant_id: str,
        analysis_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Main entry point for merchant performance analysis"""
        return await self.merchant_analyzer.analyze_merchant_performance(
            merchant_id, analysis_period
        )
    
    async def track_merchant_onboarding(
        self,
        merchant_id: str,
        onboarding_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track merchant onboarding progress"""
        tracking = await self.onboarding_tracker.track_merchant_onboarding(
            merchant_id, onboarding_data
        )
        
        return {
            "merchant_id": merchant_id,
            "current_stage": tracking.current_stage.value,
            "completion_percentage": tracking.completion_percentage,
            "pending_actions": tracking.pending_actions,
            "estimated_completion": tracking.estimated_completion.isoformat() if tracking.estimated_completion else None,
            "completed_stages": [stage.value for stage in tracking.completed_stages]
        }
    
    async def evaluate_merchant_risk(
        self,
        merchant_id: str,
        merchant_data: Dict[str, Any],
        transaction_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate merchant risk"""
        transaction_history = transaction_history or []
        
        assessment = await self.performance_evaluator.evaluate_merchant_risk(
            merchant_id, merchant_data, transaction_history
        )
        
        return {
            "merchant_id": merchant_id,
            "risk_level": assessment.risk_level.value,
            "risk_score": assessment.risk_score,
            "risk_factors": assessment.risk_factors,
            "recommendations": assessment.recommendations,
            "next_review_date": assessment.next_review_date.isoformat(),
            "assessment_date": assessment.assessment_date.isoformat()
        }

if __name__ == "__main__":
    # Enterprise testing and validation
    async def test_merchant_analytics():
        """Test merchant analytics functionality"""
        analytics = MerchantAnalytics()
        
        # Test merchant performance analysis
        print("Testing merchant performance analysis...")
        performance = await analytics.analyze_merchant_performance("merchant_001")
        print(f"Performance rating: {performance['performance_analysis'].get('performance_rating', 'unknown')}")
        print(f"Total volume: ${performance['current_metrics']['total_volume']:.2f}")
        
        # Test onboarding tracking
        print("\nTesting onboarding tracking...")
        onboarding_data = {
            "started_at": datetime.utcnow() - timedelta(days=5),
            "basic_info_provided": True,
            "email_verified": True,
            "terms_accepted": True,
            "identity_verified": False,
            "phone_verified": False
        }
        
        onboarding = await analytics.track_merchant_onboarding("merchant_002", onboarding_data)
        print(f"Onboarding stage: {onboarding['current_stage']}")
        print(f"Completion: {onboarding['completion_percentage']:.1f}%")
        
        # Test risk evaluation
        print("\nTesting risk evaluation...")
        merchant_data = {
            "created_at": datetime.utcnow() - timedelta(days=10),
            "country": "US",
            "business_type": "individual",
            "verified": False
        }
        
        risk = await analytics.evaluate_merchant_risk("merchant_003", merchant_data)
        print(f"Risk level: {risk['risk_level']}")
        print(f"Risk score: {risk['risk_score']:.1f}")
        
        print("\nMerchant analytics tests completed successfully!")
    
    # Run tests
    asyncio.run(test_merchant_analytics())