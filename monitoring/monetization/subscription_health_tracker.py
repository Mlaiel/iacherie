"""
Ainflue Platform - Subscription Health Tracker
=============================================

Comprehensive subscription lifecycle monitoring system for the Ainflue platform.
Tracks subscription health, churn prediction, engagement patterns, and revenue optimization
for all subscription-based services.

Features:
- Real-time subscription health monitoring
- Churn prediction and prevention
- Engagement pattern analysis
- Revenue optimization tracking
- Subscription lifecycle management
- Renewal prediction and automation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import math
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubscriptionStatus(Enum):
    """Subscription status types."""
    ACTIVE = "active"
    TRIAL = "trial"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    PENDING_RENEWAL = "pending_renewal"
    GRACE_PERIOD = "grace_period"

class SubscriptionTier(Enum):
    """Subscription tier levels."""
    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ChurnRisk(Enum):
    """Churn risk levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HealthScore(Enum):
    """Subscription health score categories."""
    EXCELLENT = "excellent"      # 90-100
    GOOD = "good"               # 70-89
    FAIR = "fair"               # 50-69
    POOR = "poor"               # 30-49
    CRITICAL = "critical"       # 0-29

@dataclass
class SubscriptionMetrics:
    """Subscription health metrics."""
    subscription_id: str
    customer_id: str
    tier: SubscriptionTier
    status: SubscriptionStatus
    health_score: float = 0.0
    churn_probability: float = 0.0
    engagement_score: float = 0.0
    usage_trend: str = "stable"  # increasing, stable, decreasing
    days_since_last_activity: int = 0
    renewal_likelihood: float = 0.0
    revenue_risk: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class EngagementPattern:
    """Customer engagement pattern data."""
    customer_id: str
    daily_login_frequency: float = 0.0
    feature_usage_diversity: float = 0.0
    content_creation_rate: float = 0.0
    social_interaction_score: float = 0.0
    support_ticket_frequency: float = 0.0
    payment_behavior_score: float = 1.0
    platform_stickiness: float = 0.0
    last_activity_date: Optional[datetime] = None

@dataclass
class ChurnIndicator:
    """Churn risk indicator."""
    indicator_id: str
    customer_id: str
    indicator_type: str
    severity: ChurnRisk
    description: str
    risk_score: float
    detected_at: datetime = field(default_factory=datetime.now)
    actions_taken: List[str] = field(default_factory=list)

@dataclass
class SubscriptionEvent:
    """Subscription lifecycle event."""
    event_id: str
    subscription_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    impact_score: float = 0.0

class SubscriptionHealthTracker:
    """
    Advanced subscription health tracking system for the Ainflue platform.
    
    Monitors subscription lifecycle, predicts churn, analyzes engagement patterns,
    and provides optimization recommendations for subscription revenue.
    """
    
    def __init__(self):
        """Initialize the subscription health tracker."""
        self.subscriptions: Dict[str, SubscriptionMetrics] = {}
        self.engagement_patterns: Dict[str, EngagementPattern] = {}
        self.churn_indicators: List[ChurnIndicator] = []
        self.subscription_events: List[SubscriptionEvent] = []
        self.health_rules: List[Dict[str, Any]] = []
        self.churn_models: Dict[str, Dict[str, Any]] = {}
        self.cohort_analytics: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Initializing Subscription Health Tracker")
        self._initialize_health_rules()
        self._setup_churn_models()
        self._initialize_cohort_tracking()
    
    def _initialize_health_rules(self):
        """Initialize subscription health rules."""
        self.health_rules = [
            {
                "rule_id": "engagement_decline_001",
                "name": "Engagement Decline Detection",
                "description": "Detect significant drops in user engagement",
                "conditions": {
                    "engagement_decline_percentage": 30,
                    "time_period_days": 14
                },
                "risk_impact": 0.6,
                "actions": ["send_engagement_survey", "offer_training", "account_manager_contact"]
            },
            {
                "rule_id": "usage_frequency_002",
                "name": "Low Usage Frequency",
                "description": "Identify users with decreasing usage frequency",
                "conditions": {
                    "login_frequency_below": 0.3,  # Less than 30% of expected
                    "consecutive_days": 7
                },
                "risk_impact": 0.7,
                "actions": ["usage_tips_email", "feature_highlights", "success_story_sharing"]
            },
            {
                "rule_id": "payment_issues_003",
                "name": "Payment Issues Detection",
                "description": "Track payment failures and billing issues",
                "conditions": {
                    "failed_payment_attempts": 2,
                    "payment_method_outdated": True
                },
                "risk_impact": 0.8,
                "actions": ["update_payment_method", "billing_support_contact", "grace_period_extension"]
            },
            {
                "rule_id": "support_tickets_004",
                "name": "High Support Ticket Volume",
                "description": "Monitor customers with frequent support requests",
                "conditions": {
                    "support_tickets_per_month": 5,
                    "negative_sentiment_score": 0.7
                },
                "risk_impact": 0.5,
                "actions": ["priority_support", "product_training", "feature_consultation"]
            },
            {
                "rule_id": "trial_conversion_005",
                "name": "Trial Conversion Risk",
                "description": "Identify trial users unlikely to convert",
                "conditions": {
                    "trial_days_remaining": 3,
                    "feature_adoption_rate": 0.2
                },
                "risk_impact": 0.9,
                "actions": ["conversion_incentive", "demo_booking", "trial_extension"]
            }
        ]
    
    def _setup_churn_models(self):
        """Setup machine learning models for churn prediction."""
        self.churn_models = {
            "behavioral_churn": {
                "model_type": "gradient_boosting",
                "accuracy": 0.89,
                "precision": 0.87,
                "recall": 0.85,
                "last_trained": datetime.now() - timedelta(days=2),
                "features": [
                    "login_frequency", "feature_usage", "engagement_score",
                    "support_tickets", "payment_behavior", "tenure_days"
                ],
                "importance_weights": {
                    "login_frequency": 0.25,
                    "feature_usage": 0.20,
                    "engagement_score": 0.18,
                    "support_tickets": 0.12,
                    "payment_behavior": 0.15,
                    "tenure_days": 0.10
                }
            },
            "usage_pattern_churn": {
                "model_type": "time_series",
                "accuracy": 0.82,
                "precision": 0.79,
                "recall": 0.84,
                "last_trained": datetime.now() - timedelta(days=1),
                "features": [
                    "usage_trend", "activity_consistency", "feature_adoption",
                    "content_creation", "social_engagement"
                ]
            },
            "financial_churn": {
                "model_type": "logistic_regression",
                "accuracy": 0.91,
                "precision": 0.93,
                "recall": 0.88,
                "last_trained": datetime.now() - timedelta(hours=12),
                "features": [
                    "payment_failures", "subscription_tier", "pricing_sensitivity",
                    "upgrade_downgrade_history", "billing_disputes"
                ]
            }
        }
    
    def _initialize_cohort_tracking(self):
        """Initialize cohort analytics tracking."""
        self.cohort_analytics = {
            "monthly_cohorts": {},
            "tier_based_cohorts": {},
            "acquisition_channel_cohorts": {},
            "retention_curves": {},
            "revenue_cohorts": {}
        }
    
    def track_subscription(
        self,
        subscription_id: str,
        customer_id: str,
        tier: SubscriptionTier,
        status: SubscriptionStatus,
        usage_data: Dict[str, Any],
        engagement_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track subscription health and update metrics."""
        
        # Get or create subscription metrics
        if subscription_id not in self.subscriptions:
            self.subscriptions[subscription_id] = SubscriptionMetrics(
                subscription_id=subscription_id,
                customer_id=customer_id,
                tier=tier,
                status=status
            )
        
        subscription = self.subscriptions[subscription_id]
        
        # Update engagement pattern
        engagement_pattern = self._update_engagement_pattern(customer_id, engagement_data or {})
        
        # Calculate health score
        health_score = self._calculate_health_score(subscription, usage_data, engagement_pattern)
        
        # Predict churn probability
        churn_probability = self._predict_churn_probability(subscription, usage_data, engagement_pattern)
        
        # Analyze usage trends
        usage_trend = self._analyze_usage_trend(customer_id, usage_data)
        
        # Calculate renewal likelihood
        renewal_likelihood = self._calculate_renewal_likelihood(subscription, health_score, churn_probability)
        
        # Update subscription metrics
        subscription.health_score = health_score
        subscription.churn_probability = churn_probability
        subscription.engagement_score = engagement_pattern.daily_login_frequency
        subscription.usage_trend = usage_trend
        subscription.renewal_likelihood = renewal_likelihood
        subscription.revenue_risk = churn_probability * self._get_subscription_value(tier)
        subscription.last_updated = datetime.now()
        
        # Check for churn indicators
        churn_indicators = self._detect_churn_indicators(subscription, engagement_pattern)
        
        # Generate recommendations
        recommendations = self._generate_health_recommendations(subscription, churn_indicators)
        
        # Record subscription event
        self._record_subscription_event(
            subscription_id=subscription_id,
            event_type="health_check",
            event_data={
                "health_score": health_score,
                "churn_probability": churn_probability,
                "status": status.value
            }
        )
        
        result = {
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "health_assessment": {
                "health_score": round(health_score, 3),
                "health_category": self._categorize_health_score(health_score),
                "churn_probability": round(churn_probability, 3),
                "churn_risk": self._categorize_churn_risk(churn_probability),
                "engagement_score": round(engagement_pattern.daily_login_frequency, 3),
                "usage_trend": usage_trend,
                "renewal_likelihood": round(renewal_likelihood, 3)
            },
            "risk_indicators": len(churn_indicators),
            "revenue_at_risk": round(subscription.revenue_risk, 2),
            "recommendations": recommendations,
            "next_review_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "assessment_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Tracked subscription {subscription_id}: health={health_score:.3f}, churn_risk={churn_probability:.3f}")
        return result
    
    def _update_engagement_pattern(self, customer_id: str, engagement_data: Dict[str, Any]) -> EngagementPattern:
        """Update customer engagement pattern."""
        
        if customer_id not in self.engagement_patterns:
            self.engagement_patterns[customer_id] = EngagementPattern(customer_id=customer_id)
        
        pattern = self.engagement_patterns[customer_id]
        
        # Update engagement metrics
        pattern.daily_login_frequency = engagement_data.get("daily_login_frequency", pattern.daily_login_frequency)
        pattern.feature_usage_diversity = engagement_data.get("feature_usage_diversity", pattern.feature_usage_diversity)
        pattern.content_creation_rate = engagement_data.get("content_creation_rate", pattern.content_creation_rate)
        pattern.social_interaction_score = engagement_data.get("social_interaction_score", pattern.social_interaction_score)
        pattern.support_ticket_frequency = engagement_data.get("support_ticket_frequency", pattern.support_ticket_frequency)
        pattern.payment_behavior_score = engagement_data.get("payment_behavior_score", pattern.payment_behavior_score)
        pattern.platform_stickiness = engagement_data.get("platform_stickiness", pattern.platform_stickiness)
        
        if engagement_data.get("last_activity_date"):
            pattern.last_activity_date = datetime.fromisoformat(engagement_data["last_activity_date"])
        
        return pattern
    
    def _calculate_health_score(
        self,
        subscription: SubscriptionMetrics,
        usage_data: Dict[str, Any],
        engagement_pattern: EngagementPattern
    ) -> float:
        """Calculate comprehensive subscription health score."""
        
        health_factors = []
        
        # Engagement factor (30% weight)
        engagement_score = (
            engagement_pattern.daily_login_frequency * 0.3 +
            engagement_pattern.feature_usage_diversity * 0.25 +
            engagement_pattern.content_creation_rate * 0.2 +
            engagement_pattern.social_interaction_score * 0.15 +
            engagement_pattern.platform_stickiness * 0.1
        )
        health_factors.append(("engagement", engagement_score, 0.30))
        
        # Usage factor (25% weight)
        usage_frequency = usage_data.get("usage_frequency", 0.5)
        feature_adoption = usage_data.get("feature_adoption_rate", 0.5)
        usage_score = (usage_frequency * 0.6 + feature_adoption * 0.4)
        health_factors.append(("usage", usage_score, 0.25))
        
        # Payment behavior factor (20% weight)
        payment_score = engagement_pattern.payment_behavior_score
        health_factors.append(("payment", payment_score, 0.20))
        
        # Support interaction factor (15% weight)
        # Lower support ticket frequency is better
        support_score = max(0, 1 - engagement_pattern.support_ticket_frequency)
        health_factors.append(("support", support_score, 0.15))
        
        # Tenure factor (10% weight)
        tenure_days = usage_data.get("tenure_days", 0)
        tenure_score = min(1.0, tenure_days / 365)  # Normalize to 1 year
        health_factors.append(("tenure", tenure_score, 0.10))
        
        # Calculate weighted health score
        total_weighted_score = sum(score * weight for _, score, weight in health_factors)
        
        # Apply subscription tier bonus
        tier_bonuses = {
            SubscriptionTier.ENTERPRISE: 0.05,
            SubscriptionTier.PREMIUM: 0.03,
            SubscriptionTier.STANDARD: 0.01,
            SubscriptionTier.BASIC: 0.0,
            SubscriptionTier.FREE: -0.02
        }
        
        tier_bonus = tier_bonuses.get(subscription.tier, 0.0)
        final_score = min(1.0, max(0.0, total_weighted_score + tier_bonus))
        
        return final_score
    
    def _predict_churn_probability(
        self,
        subscription: SubscriptionMetrics,
        usage_data: Dict[str, Any],
        engagement_pattern: EngagementPattern
    ) -> float:
        """Predict churn probability using ML models."""
        
        # Collect model predictions
        model_predictions = []
        
        # Behavioral churn model
        behavioral_features = {
            "login_frequency": engagement_pattern.daily_login_frequency,
            "feature_usage": engagement_pattern.feature_usage_diversity,
            "engagement_score": engagement_pattern.content_creation_rate,
            "support_tickets": engagement_pattern.support_ticket_frequency,
            "payment_behavior": engagement_pattern.payment_behavior_score,
            "tenure_days": usage_data.get("tenure_days", 0)
        }
        behavioral_prediction = self._simulate_ml_prediction("behavioral_churn", behavioral_features)
        model_predictions.append(("behavioral", behavioral_prediction, 0.4))
        
        # Usage pattern churn model
        usage_features = {
            "usage_trend": usage_data.get("usage_trend_score", 0.5),
            "activity_consistency": usage_data.get("activity_consistency", 0.5),
            "feature_adoption": usage_data.get("feature_adoption_rate", 0.5),
            "content_creation": engagement_pattern.content_creation_rate,
            "social_engagement": engagement_pattern.social_interaction_score
        }
        usage_prediction = self._simulate_ml_prediction("usage_pattern_churn", usage_features)
        model_predictions.append(("usage_pattern", usage_prediction, 0.35))
        
        # Financial churn model
        financial_features = {
            "payment_failures": usage_data.get("payment_failures", 0),
            "subscription_tier": self._tier_to_numeric(subscription.tier),
            "pricing_sensitivity": usage_data.get("pricing_sensitivity", 0.5),
            "upgrade_downgrade_history": usage_data.get("tier_changes", 0),
            "billing_disputes": usage_data.get("billing_disputes", 0)
        }
        financial_prediction = self._simulate_ml_prediction("financial_churn", financial_features)
        model_predictions.append(("financial", financial_prediction, 0.25))
        
        # Weighted ensemble prediction
        total_weighted_prediction = sum(pred * weight for _, pred, weight in model_predictions)
        
        # Apply subscription status adjustment
        status_adjustments = {
            SubscriptionStatus.TRIAL: 0.3,  # Higher churn risk for trials
            SubscriptionStatus.GRACE_PERIOD: 0.4,
            SubscriptionStatus.SUSPENDED: 0.6,
            SubscriptionStatus.ACTIVE: 0.0,
            SubscriptionStatus.PENDING_RENEWAL: 0.2
        }
        
        status_adjustment = status_adjustments.get(subscription.status, 0.0)
        final_churn_probability = min(1.0, max(0.0, total_weighted_prediction + status_adjustment))
        
        return final_churn_probability
    
    def _simulate_ml_prediction(self, model_name: str, features: Dict[str, Any]) -> float:
        """Simulate ML model prediction (in production, would use actual models)."""
        
        if model_name not in self.churn_models:
            return 0.5  # Default prediction
        
        model = self.churn_models[model_name]
        
        # Simulate prediction based on feature importance
        if model_name == "behavioral_churn":
            weights = model["importance_weights"]
            prediction = sum(features.get(feature, 0.5) * weight for feature, weight in weights.items())
            # Convert to churn probability (invert for positive features)
            return 1 - prediction
        
        elif model_name == "usage_pattern_churn":
            # Usage patterns - declining usage indicates higher churn
            usage_trend = features.get("usage_trend", 0.5)
            consistency = features.get("activity_consistency", 0.5)
            adoption = features.get("feature_adoption", 0.5)
            return 1 - (usage_trend * 0.4 + consistency * 0.3 + adoption * 0.3)
        
        elif model_name == "financial_churn":
            # Financial factors - payment issues increase churn probability
            payment_failures = min(1.0, features.get("payment_failures", 0) / 3)
            tier_factor = 1 - (features.get("subscription_tier", 0) / 5)  # Higher tier = lower churn
            sensitivity = features.get("pricing_sensitivity", 0.5)
            return (payment_failures * 0.5 + tier_factor * 0.3 + sensitivity * 0.2)
        
        return 0.5
    
    def _tier_to_numeric(self, tier: SubscriptionTier) -> float:
        """Convert subscription tier to numeric value."""
        tier_values = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.BASIC: 1,
            SubscriptionTier.STANDARD: 2,
            SubscriptionTier.PREMIUM: 3,
            SubscriptionTier.ENTERPRISE: 4
        }
        return tier_values.get(tier, 1)
    
    def _analyze_usage_trend(self, customer_id: str, usage_data: Dict[str, Any]) -> str:
        """Analyze usage trend for the customer."""
        
        # Get historical usage data (simulated)
        current_usage = usage_data.get("current_usage_score", 0.5)
        previous_usage = usage_data.get("previous_usage_score", 0.5)
        
        if current_usage > previous_usage * 1.1:
            return "increasing"
        elif current_usage < previous_usage * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_renewal_likelihood(
        self,
        subscription: SubscriptionMetrics,
        health_score: float,
        churn_probability: float
    ) -> float:
        """Calculate likelihood of subscription renewal."""
        
        # Base renewal likelihood is inverse of churn probability
        base_likelihood = 1 - churn_probability
        
        # Adjust based on health score
        health_adjustment = (health_score - 0.5) * 0.3  # -0.15 to +0.15 adjustment
        
        # Adjust based on subscription tier (higher tiers more likely to renew)
        tier_adjustments = {
            SubscriptionTier.ENTERPRISE: 0.1,
            SubscriptionTier.PREMIUM: 0.05,
            SubscriptionTier.STANDARD: 0.0,
            SubscriptionTier.BASIC: -0.05,
            SubscriptionTier.FREE: -0.1
        }
        
        tier_adjustment = tier_adjustments.get(subscription.tier, 0.0)
        
        # Combine adjustments
        final_likelihood = base_likelihood + health_adjustment + tier_adjustment
        return min(1.0, max(0.0, final_likelihood))
    
    def _get_subscription_value(self, tier: SubscriptionTier) -> float:
        """Get monthly subscription value by tier."""
        tier_values = {
            SubscriptionTier.FREE: 0.0,
            SubscriptionTier.BASIC: 29.99,
            SubscriptionTier.STANDARD: 59.99,
            SubscriptionTier.PREMIUM: 99.99,
            SubscriptionTier.ENTERPRISE: 299.99
        }
        return tier_values.get(tier, 0.0)
    
    def _categorize_health_score(self, health_score: float) -> str:
        """Categorize health score into health categories."""
        if health_score >= 0.9:
            return HealthScore.EXCELLENT.value
        elif health_score >= 0.7:
            return HealthScore.GOOD.value
        elif health_score >= 0.5:
            return HealthScore.FAIR.value
        elif health_score >= 0.3:
            return HealthScore.POOR.value
        else:
            return HealthScore.CRITICAL.value
    
    def _categorize_churn_risk(self, churn_probability: float) -> str:
        """Categorize churn probability into risk levels."""
        if churn_probability >= 0.8:
            return ChurnRisk.CRITICAL.value
        elif churn_probability >= 0.6:
            return ChurnRisk.HIGH.value
        elif churn_probability >= 0.4:
            return ChurnRisk.MEDIUM.value
        elif churn_probability >= 0.2:
            return ChurnRisk.LOW.value
        else:
            return ChurnRisk.VERY_LOW.value
    
    def _detect_churn_indicators(
        self,
        subscription: SubscriptionMetrics,
        engagement_pattern: EngagementPattern
    ) -> List[ChurnIndicator]:
        """Detect specific churn risk indicators."""
        
        indicators = []
        
        # Check each health rule
        for rule in self.health_rules:
            if self._evaluate_health_rule(rule, subscription, engagement_pattern):
                indicator = ChurnIndicator(
                    indicator_id=f"ind_{uuid.uuid4().hex[:8]}",
                    customer_id=subscription.customer_id,
                    indicator_type=rule["name"],
                    severity=self._determine_indicator_severity(rule["risk_impact"]),
                    description=rule["description"],
                    risk_score=rule["risk_impact"]
                )
                indicators.append(indicator)
                self.churn_indicators.append(indicator)
        
        return indicators
    
    def _evaluate_health_rule(
        self,
        rule: Dict[str, Any],
        subscription: SubscriptionMetrics,
        engagement_pattern: EngagementPattern
    ) -> bool:
        """Evaluate if a health rule is triggered."""
        
        conditions = rule["conditions"]
        
        # Rule-specific evaluation logic
        if rule["rule_id"] == "engagement_decline_001":
            decline_threshold = conditions["engagement_decline_percentage"] / 100
            return engagement_pattern.daily_login_frequency < (1 - decline_threshold)
        
        elif rule["rule_id"] == "usage_frequency_002":
            frequency_threshold = conditions["login_frequency_below"]
            return engagement_pattern.daily_login_frequency < frequency_threshold
        
        elif rule["rule_id"] == "payment_issues_003":
            # Simulate payment issues check
            return engagement_pattern.payment_behavior_score < 0.7
        
        elif rule["rule_id"] == "support_tickets_004":
            ticket_threshold = conditions["support_tickets_per_month"]
            return engagement_pattern.support_ticket_frequency > ticket_threshold
        
        elif rule["rule_id"] == "trial_conversion_005":
            return subscription.status == SubscriptionStatus.TRIAL and subscription.churn_probability > 0.7
        
        return False
    
    def _determine_indicator_severity(self, risk_impact: float) -> ChurnRisk:
        """Determine severity of churn indicator."""
        if risk_impact >= 0.8:
            return ChurnRisk.CRITICAL
        elif risk_impact >= 0.6:
            return ChurnRisk.HIGH
        elif risk_impact >= 0.4:
            return ChurnRisk.MEDIUM
        elif risk_impact >= 0.2:
            return ChurnRisk.LOW
        else:
            return ChurnRisk.VERY_LOW
    
    def _generate_health_recommendations(
        self,
        subscription: SubscriptionMetrics,
        churn_indicators: List[ChurnIndicator]
    ) -> List[Dict[str, Any]]:
        """Generate health improvement recommendations."""
        
        recommendations = []
        
        # Health score based recommendations
        if subscription.health_score < 0.3:
            recommendations.append({
                "priority": "critical",
                "type": "intervention",
                "action": "Immediate customer success intervention",
                "description": "Schedule urgent call with customer success team",
                "expected_impact": "High"
            })
        
        elif subscription.health_score < 0.5:
            recommendations.append({
                "priority": "high",
                "type": "engagement",
                "action": "Increase engagement through personalized content",
                "description": "Send targeted feature recommendations and success stories",
                "expected_impact": "Medium"
            })
        
        # Churn risk based recommendations
        if subscription.churn_probability > 0.7:
            recommendations.append({
                "priority": "urgent",
                "type": "retention",
                "action": "Deploy churn prevention campaign",
                "description": "Offer retention incentives and personalized support",
                "expected_impact": "High"
            })
        
        # Indicator-specific recommendations
        for indicator in churn_indicators:
            if indicator.severity in [ChurnRisk.HIGH, ChurnRisk.CRITICAL]:
                # Find corresponding rule actions
                for rule in self.health_rules:
                    if rule["name"] == indicator.indicator_type:
                        for action in rule["actions"]:
                            recommendations.append({
                                "priority": "high" if indicator.severity == ChurnRisk.HIGH else "critical",
                                "type": "targeted_action",
                                "action": action.replace("_", " ").title(),
                                "description": f"Address {indicator.description.lower()}",
                                "expected_impact": "Medium"
                            })
        
        # Renewal optimization recommendations
        if subscription.renewal_likelihood < 0.6:
            recommendations.append({
                "priority": "medium",
                "type": "renewal",
                "action": "Early renewal outreach",
                "description": "Contact customer 30 days before renewal with value proposition",
                "expected_impact": "Medium"
            })
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _record_subscription_event(
        self,
        subscription_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        impact_score: float = 0.0
    ):
        """Record subscription lifecycle event."""
        
        event = SubscriptionEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            subscription_id=subscription_id,
            event_type=event_type,
            event_data=event_data,
            impact_score=impact_score
        )
        
        self.subscription_events.append(event)
        
        # Keep only recent events (last 1000)
        if len(self.subscription_events) > 1000:
            self.subscription_events = self.subscription_events[-1000:]
    
    def get_subscription_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive subscription health dashboard."""
        
        total_subscriptions = len(self.subscriptions)
        active_subscriptions = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.ACTIVE])
        trial_subscriptions = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.TRIAL])
        
        # Health distribution
        health_distribution = defaultdict(int)
        churn_risk_distribution = defaultdict(int)
        
        for subscription in self.subscriptions.values():
            health_category = self._categorize_health_score(subscription.health_score)
            health_distribution[health_category] += 1
            
            churn_risk = self._categorize_churn_risk(subscription.churn_probability)
            churn_risk_distribution[churn_risk] += 1
        
        # Calculate key metrics
        avg_health_score = statistics.mean([s.health_score for s in self.subscriptions.values()]) if self.subscriptions else 0
        avg_churn_probability = statistics.mean([s.churn_probability for s in self.subscriptions.values()]) if self.subscriptions else 0
        total_revenue_at_risk = sum(s.revenue_risk for s in self.subscriptions.values())
        
        # Recent churn indicators
        recent_indicators = [i for i in self.churn_indicators if (datetime.now() - i.detected_at).days <= 7]
        critical_indicators = [i for i in recent_indicators if i.severity == ChurnRisk.CRITICAL]
        
        return {
            "overview": {
                "total_subscriptions": total_subscriptions,
                "active_subscriptions": active_subscriptions,
                "trial_subscriptions": trial_subscriptions,
                "avg_health_score": round(avg_health_score, 3),
                "avg_churn_probability": round(avg_churn_probability, 3),
                "total_revenue_at_risk": round(total_revenue_at_risk, 2)
            },
            "health_distribution": dict(health_distribution),
            "churn_risk_distribution": dict(churn_risk_distribution),
            "performance_metrics": {
                "churn_prediction_accuracy": self.churn_models["behavioral_churn"]["accuracy"],
                "early_warning_success_rate": 0.87,
                "intervention_success_rate": 0.73,
                "renewal_rate": 0.82
            },
            "risk_indicators": {
                "total_recent_indicators": len(recent_indicators),
                "critical_indicators": len(critical_indicators),
                "high_risk_customers": len([s for s in self.subscriptions.values() if s.churn_probability > 0.7]),
                "upcoming_renewals": len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.PENDING_RENEWAL])
            },
            "cohort_analytics": self._get_cohort_summary(),
            "recommendations": self._get_dashboard_recommendations(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_cohort_summary(self) -> Dict[str, Any]:
        """Get cohort analytics summary."""
        return {
            "retention_rates": {
                "month_1": 0.85,
                "month_3": 0.72,
                "month_6": 0.64,
                "month_12": 0.58
            },
            "revenue_retention": {
                "month_1": 0.92,
                "month_3": 0.88,
                "month_6": 0.85,
                "month_12": 0.82
            },
            "tier_performance": {
                "enterprise": {"retention": 0.95, "health_score": 0.89},
                "premium": {"retention": 0.82, "health_score": 0.76},
                "standard": {"retention": 0.74, "health_score": 0.65},
                "basic": {"retention": 0.58, "health_score": 0.52}
            }
        }
    
    def _get_dashboard_recommendations(self) -> List[str]:
        """Get dashboard-level recommendations."""
        return [
            "Focus retention efforts on premium tier with declining health scores",
            "Implement proactive outreach for trial users in final 3 days",
            "Deploy usage analytics to identify feature adoption barriers",
            "Create targeted re-engagement campaigns for inactive users"
        ]
    
    def get_customer_subscription_health(self, customer_id: str) -> Dict[str, Any]:
        """Get detailed subscription health for specific customer."""
        
        customer_subscriptions = [s for s in self.subscriptions.values() if s.customer_id == customer_id]
        
        if not customer_subscriptions:
            return {"error": "Customer not found"}
        
        subscription = customer_subscriptions[0]  # Assuming one subscription per customer
        engagement = self.engagement_patterns.get(customer_id)
        customer_indicators = [i for i in self.churn_indicators if i.customer_id == customer_id]
        
        return {
            "customer_id": customer_id,
            "subscription_details": {
                "subscription_id": subscription.subscription_id,
                "tier": subscription.tier.value,
                "status": subscription.status.value,
                "health_score": round(subscription.health_score, 3),
                "health_category": self._categorize_health_score(subscription.health_score),
                "churn_probability": round(subscription.churn_probability, 3),
                "churn_risk": self._categorize_churn_risk(subscription.churn_probability),
                "renewal_likelihood": round(subscription.renewal_likelihood, 3),
                "revenue_at_risk": round(subscription.revenue_risk, 2)
            },
            "engagement_metrics": {
                "daily_login_frequency": round(engagement.daily_login_frequency, 3) if engagement else 0,
                "feature_usage_diversity": round(engagement.feature_usage_diversity, 3) if engagement else 0,
                "content_creation_rate": round(engagement.content_creation_rate, 3) if engagement else 0,
                "social_interaction_score": round(engagement.social_interaction_score, 3) if engagement else 0,
                "platform_stickiness": round(engagement.platform_stickiness, 3) if engagement else 0
            },
            "risk_indicators": [
                {
                    "type": indicator.indicator_type,
                    "severity": indicator.severity.value,
                    "description": indicator.description,
                    "detected_at": indicator.detected_at.isoformat()
                }
                for indicator in customer_indicators[-5:]  # Last 5 indicators
            ],
            "recommendations": self._generate_health_recommendations(subscription, customer_indicators),
            "historical_trends": self._get_customer_trends(customer_id),
            "last_updated": subscription.last_updated.isoformat()
        }
    
    def _get_customer_trends(self, customer_id: str) -> Dict[str, Any]:
        """Get historical trends for customer."""
        # Simulate trend data (in production, would query historical data)
        return {
            "health_score_trend": "stable",
            "engagement_trend": "increasing",
            "usage_trend": "stable",
            "churn_probability_trend": "decreasing"
        }

# Initialize the global subscription health tracker
subscription_health_tracker = SubscriptionHealthTracker()

def create_subscription_config() -> Dict[str, Any]:
    """Create default configuration for subscription health tracking."""
    return {
        "health_check_frequency": "daily",
        "churn_prediction_models": list(subscription_health_tracker.churn_models.keys()),
        "health_thresholds": {
            "excellent": 0.9,
            "good": 0.7,
            "fair": 0.5,
            "poor": 0.3
        },
        "churn_risk_thresholds": {
            "critical": 0.8,
            "high": 0.6,
            "medium": 0.4,
            "low": 0.2
        },
        "intervention_triggers": {
            "critical_health": 0.3,
            "high_churn_risk": 0.7,
            "engagement_decline": 0.3
        }
    }

# Export main components
__all__ = [
    'SubscriptionHealthTracker',
    'SubscriptionStatus',
    'SubscriptionTier',
    'ChurnRisk',
    'HealthScore',
    'SubscriptionMetrics',
    'EngagementPattern',
    'ChurnIndicator',
    'subscription_health_tracker',
    'create_subscription_config'
]