"""Retention Optimization Workflow

AI-powered user retention optimization workflow for gamification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class RetentionRisk(Enum):
    """User retention risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionType(Enum):
    """Types of retention interventions"""
    ENGAGEMENT_BOOST = "engagement_boost"
    PERSONALIZED_CONTENT = "personalized_content"
    SOCIAL_CONNECTION = "social_connection"
    ACHIEVEMENT_REMINDER = "achievement_reminder"
    SKILL_DEVELOPMENT = "skill_development"
    COMMUNITY_INVITATION = "community_invitation"
    REWARD_INCENTIVE = "reward_incentive"
    RE_ONBOARDING = "re_onboarding"


@dataclass
class RetentionProfile:
    """User retention profile"""
    user_id: str
    risk_level: RetentionRisk
    churn_probability: float
    days_since_last_activity: int
    engagement_score: float
    retention_factors: Dict[str, float]
    warning_signals: List[str]
    protective_factors: List[str]
    last_assessment: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RetentionIntervention:
    """Retention intervention record"""
    intervention_id: str
    user_id: str
    intervention_type: InterventionType
    trigger_reason: str
    intervention_data: Dict[str, Any]
    implemented_at: datetime = field(default_factory=datetime.utcnow)
    effectiveness_score: Optional[float] = None
    follow_up_date: Optional[datetime] = None


class RetentionOptimizationWorkflow:
    """AI-powered retention optimization workflow"""
    
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.user_profiles: Dict[str, RetentionProfile] = {}
        self.interventions: Dict[str, List[RetentionIntervention]] = {}
        
    async def assess_retention_risk(
        self,
        user_id: str,
        user_activity_data: Dict[str, Any],
        user_engagement_data: Dict[str, Any]
    ) -> RetentionProfile:
        """
        Assess user's retention risk and create profile
        
        Args:
            user_id: User identifier
            user_activity_data: User's recent activity data
            user_engagement_data: User's engagement metrics
            
        Returns:
            RetentionProfile with risk assessment
        """
        try:
            logger.info(f"Assessing retention risk for user {user_id}")
            
            # Calculate risk factors
            risk_factors = await self._calculate_risk_factors(user_activity_data, user_engagement_data)
            
            # Calculate churn probability using AI model
            churn_probability = await self._predict_churn_probability(risk_factors, user_activity_data)
            
            # Determine risk level
            risk_level = await self._determine_risk_level(churn_probability)
            
            # Calculate engagement score
            engagement_score = await self._calculate_engagement_score(user_engagement_data)
            
            # Identify warning signals and protective factors
            warning_signals = await self._identify_warning_signals(risk_factors, user_activity_data)
            protective_factors = await self._identify_protective_factors(risk_factors, user_engagement_data)
            
            # Calculate days since last activity
            last_activity = user_activity_data.get("last_activity_date")
            days_since_activity = 0
            if last_activity:
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity)
                days_since_activity = (datetime.utcnow() - last_activity).days
            
            # Create retention profile
            profile = RetentionProfile(
                user_id=user_id,
                risk_level=risk_level,
                churn_probability=churn_probability,
                days_since_last_activity=days_since_activity,
                engagement_score=engagement_score,
                retention_factors=risk_factors,
                warning_signals=warning_signals,
                protective_factors=protective_factors
            )
            
            # Store profile
            self.user_profiles[user_id] = profile
            
            # Trigger interventions if needed
            if risk_level in [RetentionRisk.HIGH, RetentionRisk.CRITICAL]:
                await self._trigger_retention_interventions(profile)
            
            # Record metrics
            await self.metrics_collector.record_metric("retention_assessments", 1)
            await self.metrics_collector.record_metric(f"retention_risk_{risk_level.value}", 1)
            await self.metrics_collector.record_metric("churn_probability", churn_probability)
            
            logger.info(f"Retention assessment completed: {risk_level.value} risk ({churn_probability:.3f})")
            return profile
            
        except Exception as e:
            logger.error(f"Retention risk assessment failed: {e}")
            raise WorkflowError(f"Retention risk assessment failed: {e}")
    
    async def implement_intervention(
        self,
        user_id: str,
        intervention_type: InterventionType,
        trigger_reason: str,
        custom_data: Dict[str, Any] = None
    ) -> RetentionIntervention:
        """
        Implement retention intervention for user
        
        Args:
            user_id: User identifier
            intervention_type: Type of intervention to implement
            trigger_reason: Reason for triggering intervention
            custom_data: Custom data for intervention
            
        Returns:
            RetentionIntervention record
        """
        try:
            intervention_id = f"intervention_{int(datetime.utcnow().timestamp())}_{user_id}"
            
            # Generate intervention data
            intervention_data = await self._generate_intervention_data(
                user_id, intervention_type, custom_data
            )
            
            # Create intervention record
            intervention = RetentionIntervention(
                intervention_id=intervention_id,
                user_id=user_id,
                intervention_type=intervention_type,
                trigger_reason=trigger_reason,
                intervention_data=intervention_data,
                follow_up_date=datetime.utcnow() + timedelta(days=7)  # Follow up in 7 days
            )
            
            # Store intervention
            if user_id not in self.interventions:
                self.interventions[user_id] = []
            self.interventions[user_id].append(intervention)
            
            # Execute intervention
            await self._execute_intervention(intervention)
            
            # Record metrics
            await self.metrics_collector.record_metric("retention_interventions", 1)
            await self.metrics_collector.record_metric(f"intervention_{intervention_type.value}", 1)
            
            logger.info(f"Intervention implemented: {intervention_type.value} for user {user_id}")
            return intervention
            
        except Exception as e:
            logger.error(f"Intervention implementation failed: {e}")
            raise WorkflowError(f"Intervention implementation failed: {e}")
    
    async def get_retention_insights(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Get retention insights and analytics"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        
        # Analyze recent profiles
        recent_profiles = [
            profile for profile in self.user_profiles.values()
            if profile.last_assessment >= cutoff_date
        ]
        
        if not recent_profiles:
            return {"message": "No recent retention data available"}
        
        # Calculate risk distribution
        risk_distribution = {}
        for profile in recent_profiles:
            risk = profile.risk_level.value
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
        
        # Calculate average metrics
        avg_churn_probability = sum(p.churn_probability for p in recent_profiles) / len(recent_profiles)
        avg_engagement_score = sum(p.engagement_score for p in recent_profiles) / len(recent_profiles)
        
        # Analyze interventions
        recent_interventions = []
        for user_interventions in self.interventions.values():
            for intervention in user_interventions:
                if intervention.implemented_at >= cutoff_date:
                    recent_interventions.append(intervention)
        
        # Calculate intervention effectiveness
        effective_interventions = [
            i for i in recent_interventions 
            if i.effectiveness_score and i.effectiveness_score > 0.7
        ]
        
        intervention_effectiveness = (
            len(effective_interventions) / len(recent_interventions) * 100
            if recent_interventions else 0
        )
        
        # Identify top warning signals
        all_warning_signals = []
        for profile in recent_profiles:
            all_warning_signals.extend(profile.warning_signals)
        
        warning_signal_counts = {}
        for signal in all_warning_signals:
            warning_signal_counts[signal] = warning_signal_counts.get(signal, 0) + 1
        
        top_warning_signals = sorted(
            warning_signal_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        insights = {
            "period_days": time_period_days,
            "total_users_assessed": len(recent_profiles),
            "risk_distribution": risk_distribution,
            "average_churn_probability": round(avg_churn_probability, 3),
            "average_engagement_score": round(avg_engagement_score, 3),
            "total_interventions": len(recent_interventions),
            "intervention_effectiveness_percentage": round(intervention_effectiveness, 2),
            "top_warning_signals": [{"signal": signal, "count": count} for signal, count in top_warning_signals],
            "retention_recommendations": await self._generate_retention_recommendations(recent_profiles)
        }
        
        return insights
    
    async def _calculate_risk_factors(
        self, 
        activity_data: Dict[str, Any], 
        engagement_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate various retention risk factors"""
        
        risk_factors = {}
        
        # Activity frequency risk
        login_frequency = activity_data.get("login_frequency", 0)
        risk_factors["low_login_frequency"] = max(0, 1 - (login_frequency / 7))  # Expected: 7 logins/week
        
        # Content creation risk
        content_creation_rate = activity_data.get("content_creation_rate", 0)
        risk_factors["low_content_creation"] = max(0, 1 - (content_creation_rate / 3))  # Expected: 3 posts/week
        
        # Social engagement risk
        social_interactions = engagement_data.get("social_interactions", 0)
        risk_factors["low_social_engagement"] = max(0, 1 - (social_interactions / 10))  # Expected: 10 interactions/week
        
        # Feature adoption risk
        features_used = len(activity_data.get("features_used", []))
        risk_factors["limited_feature_adoption"] = max(0, 1 - (features_used / 10))  # Expected: 10 features
        
        # Session duration risk
        avg_session_duration = activity_data.get("avg_session_duration", 0)
        risk_factors["short_sessions"] = max(0, 1 - (avg_session_duration / 30))  # Expected: 30 minutes
        
        # Community participation risk
        community_participation = engagement_data.get("community_participation", 0)
        risk_factors["low_community_participation"] = max(0, 1 - (community_participation / 5))  # Expected: 5 activities/week
        
        return risk_factors
    
    async def _predict_churn_probability(self, risk_factors: Dict[str, float], activity_data: Dict[str, Any]) -> float:
        """Predict churn probability using AI model simulation"""
        
        # Simulate AI model prediction
        # In real implementation, this would use trained ML models
        
        # Weight the risk factors
        factor_weights = {
            "low_login_frequency": 0.25,
            "low_content_creation": 0.20,
            "low_social_engagement": 0.20,
            "limited_feature_adoption": 0.15,
            "short_sessions": 0.10,
            "low_community_participation": 0.10
        }
        
        # Calculate weighted risk score
        weighted_risk = sum(
            risk_factors.get(factor, 0) * weight
            for factor, weight in factor_weights.items()
        )
        
        # Apply time-based adjustment
        days_since_signup = activity_data.get("days_since_signup", 0)
        if days_since_signup < 30:  # New users have higher base churn
            weighted_risk += 0.2
        
        # Convert to probability (0-1)
        churn_probability = min(weighted_risk, 1.0)
        
        return round(churn_probability, 3)
    
    async def _determine_risk_level(self, churn_probability: float) -> RetentionRisk:
        """Determine risk level from churn probability"""
        
        if churn_probability >= 0.8:
            return RetentionRisk.CRITICAL
        elif churn_probability >= 0.6:
            return RetentionRisk.HIGH
        elif churn_probability >= 0.3:
            return RetentionRisk.MEDIUM
        else:
            return RetentionRisk.LOW
    
    async def _calculate_engagement_score(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate overall engagement score"""
        
        # Normalize engagement metrics to 0-1 scale
        social_score = min(engagement_data.get("social_interactions", 0) / 50, 1.0)
        content_score = min(engagement_data.get("content_engagement", 0) / 100, 1.0)
        community_score = min(engagement_data.get("community_participation", 0) / 20, 1.0)
        
        # Weighted average
        engagement_score = (social_score * 0.4 + content_score * 0.35 + community_score * 0.25)
        
        return round(engagement_score, 3)
    
    async def _identify_warning_signals(self, risk_factors: Dict[str, float], activity_data: Dict[str, Any]) -> List[str]:
        """Identify specific warning signals for churn"""
        
        signals = []
        threshold = 0.6  # Warning threshold
        
        for factor, score in risk_factors.items():
            if score >= threshold:
                if factor == "low_login_frequency":
                    signals.append("Declining login frequency")
                elif factor == "low_content_creation":
                    signals.append("Reduced content creation activity")
                elif factor == "low_social_engagement":
                    signals.append("Minimal social interactions")
                elif factor == "limited_feature_adoption":
                    signals.append("Limited platform feature usage")
                elif factor == "short_sessions":
                    signals.append("Decreasing session duration")
                elif factor == "low_community_participation":
                    signals.append("Low community engagement")
        
        # Additional specific signals
        if activity_data.get("support_tickets", 0) > 2:
            signals.append("Multiple support requests")
        
        if activity_data.get("failed_uploads", 0) > 5:
            signals.append("Technical difficulties with uploads")
        
        return signals
    
    async def _identify_protective_factors(self, risk_factors: Dict[str, float], engagement_data: Dict[str, Any]) -> List[str]:
        """Identify factors that protect against churn"""
        
        factors = []
        
        # Strong areas (low risk scores)
        for factor, score in risk_factors.items():
            if score <= 0.3:  # Strong performance
                if factor == "low_login_frequency":
                    factors.append("Consistent daily usage")
                elif factor == "low_content_creation":
                    factors.append("Active content creator")
                elif factor == "low_social_engagement":
                    factors.append("Strong social connections")
                elif factor == "limited_feature_adoption":
                    factors.append("Power user of platform features")
        
        # Additional protective factors
        if engagement_data.get("achievements_earned", 0) > 10:
            factors.append("High achievement motivation")
        
        if engagement_data.get("collaborations", 0) > 3:
            factors.append("Active collaborator")
        
        if engagement_data.get("mentoring_relationships", 0) > 0:
            factors.append("Engaged in mentoring")
        
        return factors
    
    async def _trigger_retention_interventions(self, profile -> None: RetentionProfile) -> None:
        """Automatically trigger appropriate interventions based on risk profile"""
        
        user_id = profile.user_id
        risk_level = profile.risk_level
        
        # Select interventions based on warning signals and risk level
        if "Declining login frequency" in profile.warning_signals:
            await self.implement_intervention(
                user_id, InterventionType.ENGAGEMENT_BOOST, "declining_login_frequency"
            )
        
        if "Reduced content creation activity" in profile.warning_signals:
            await self.implement_intervention(
                user_id, InterventionType.PERSONALIZED_CONTENT, "low_content_creation"
            )
        
        if "Minimal social interactions" in profile.warning_signals:
            await self.implement_intervention(
                user_id, InterventionType.SOCIAL_CONNECTION, "low_social_engagement"
            )
        
        if risk_level == RetentionRisk.CRITICAL:
            # High-touch interventions for critical cases
            await self.implement_intervention(
                user_id, InterventionType.RE_ONBOARDING, "critical_churn_risk"
            )
            await self.implement_intervention(
                user_id, InterventionType.REWARD_INCENTIVE, "critical_retention_effort"
            )
    
    async def _generate_intervention_data(
        self, 
        user_id: str, 
        intervention_type: InterventionType, 
        custom_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate specific intervention data based on type"""
        
        base_data = custom_data or {}
        
        if intervention_type == InterventionType.ENGAGEMENT_BOOST:
            base_data.update({
                "boost_type": "daily_challenge",
                "challenge_difficulty": "easy",
                "reward_multiplier": 2.0,
                "duration_days": 7
            })
        
        elif intervention_type == InterventionType.PERSONALIZED_CONTENT:
            base_data.update({
                "content_suggestions": [
                    "Try creating video content for higher engagement",
                    "Experiment with trending hashtags in your niche",
                    "Collaborate with other creators in your area"
                ],
                "template_access": "premium_templates",
                "tutorial_recommendations": ["video_editing_basics", "engagement_strategies"]
            })
        
        elif intervention_type == InterventionType.SOCIAL_CONNECTION:
            base_data.update({
                "suggested_connections": 5,
                "community_group_invitations": ["content_creators", "beginners_support"],
                "mentorship_offer": True
            })
        
        elif intervention_type == InterventionType.REWARD_INCENTIVE:
            base_data.update({
                "bonus_points": 500,
                "exclusive_badge": "comeback_champion",
                "premium_trial_days": 14,
                "special_features_access": ["advanced_analytics", "priority_support"]
            })
        
        return base_data
    
    async def _execute_intervention(self, intervention -> None: RetentionIntervention) -> None:
        """Execute the intervention (send notifications, apply rewards, etc.)"""
        
        # In real implementation, this would:
        # 1. Send targeted notifications
        # 2. Apply rewards and bonuses
        # 3. Grant feature access
        # 4. Schedule follow-up actions
        # 5. Update user experience
        
        logger.info(f"Executing intervention: {intervention.intervention_type.value} for user {intervention.user_id}")
        logger.info(f"Intervention data: {intervention.intervention_data}")
    
    async def _generate_retention_recommendations(self, profiles: List[RetentionProfile]) -> List[str]:
        """Generate high-level retention strategy recommendations"""
        
        recommendations = []
        
        # Analyze common warning signals
        all_signals = []
        for profile in profiles:
            all_signals.extend(profile.warning_signals)
        
        signal_counts = {}
        for signal in all_signals:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
        
        top_signals = sorted(signal_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for signal, count in top_signals:
            if "login frequency" in signal:
                recommendations.append("Implement daily engagement rewards and reminders")
            elif "content creation" in signal:
                recommendations.append("Provide more content creation tools and inspiration")
            elif "social interactions" in signal:
                recommendations.append("Enhance community features and social discovery")
        
        # Risk level distribution recommendations
        high_risk_count = len([p for p in profiles if p.risk_level in [RetentionRisk.HIGH, RetentionRisk.CRITICAL]])
        high_risk_percentage = (high_risk_count / len(profiles)) * 100
        
        if high_risk_percentage > 20:
            recommendations.append("Focus on proactive retention campaigns for high-risk segments")
        
        if high_risk_percentage > 35:
            recommendations.append("Consider major platform improvements to address fundamental retention issues")
        
        return recommendations[:5]  # Limit to 5 recommendations