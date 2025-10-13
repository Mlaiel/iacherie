"""
Customer Lifecycle Management - Complete Customer Journey Optimization
=====================================================================

Advanced customer acquisition, onboarding automation, retention strategies,
and churn prediction with AI-powered interventions.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class CustomerStage(Enum):
    """
        Customer lifecycle stages"""
    PROSPECT = "prospect"
    LEAD = "lead"
    TRIAL = "trial"
    ACTIVE = "active"
    POWER_USER = "power_user"
    AT_RISK = "at_risk"
    CHURNED = "churned"
    WON_BACK = "won_back"


class AcquisitionChannel(Enum):
    """Customer acquisition channels"""
    ORGANIC_SEARCH = "organic_search"
    PAID_SEARCH = "paid_search"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    REFERRAL = "referral"
    DIRECT = "direct"
    PARTNERSHIP = "partnership"
    CONTENT = "content"


class ChurnRisk(Enum):
    """Churn risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CustomerProfile:
    """Complete customer profile"""
    customer_id: str
    stage: CustomerStage
    acquisition_channel: AcquisitionChannel
    acquisition_date: datetime
    lifetime_value: Decimal
    engagement_score: float
    churn_risk: ChurnRisk
    activities: List[Dict[str, Any]] = field(default_factory=list)
    touchpoints: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    last_interaction: Optional[datetime] = None


@dataclass
class OnboardingWorkflow:
    """
        Onboarding workflow configuration"""
    workflow_id: str
    name: str
    steps: List[Dict[str, Any]]
    completion_rate: float = 0.0
    average_time: timedelta = timedelta(days=7)
    triggers: List[str] = field(default_factory=list)


@dataclass
class RetentionCampaign:
    """
        Retention campaign details"""
    campaign_id: str
    name: str
    target_segment: str
    actions: List[Dict[str, Any]]
    success_rate: float = 0.0
    participants: int = 0


class CustomerAcquisitionOptimizer:
    """
        Optimize customer acquisition strategies and channels"""
    
    def __init__(self):
        self.channels: Dict[AcquisitionChannel, Dict[str, Any]] = {}
        self.campaigns: Dict[str, Dict[str, Any]] = {}
        self.conversion_funnels: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.cost_per_acquisition: Dict[AcquisitionChannel, Decimal] = {}
        logger.info("CustomerAcquisitionOptimizer initialized")
    
    async def optimize_channel_mix(
        self,
        budget: Decimal,
        channel_performance: Dict[AcquisitionChannel, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Optimize budget allocation across channels"""
        
        channel_roi = {}
        for channel, metrics in channel_performance.items():
            conversions = metrics.get("conversions", 0)


            cost = metrics.get("cost", 1)


            ltv = metrics.get("lifetime_value", 0)


            
            roi = (conversions * ltv - cost) / cost if cost > 0 else 0
            channel_roi[channel] = {
                "roi": roi,
                "conversions": conversions,
                "cost": cost,
                "cpa": cost / conversions if conversions > 0 else float('inf')
            }

        
        sorted_channels = sorted(channel_roi.items(), key=lambda x: x[1]["roi"], reverse=True)


        
        allocation = {}

        remaining_budget = budget
        
        for channel, metrics in sorted_channels:
            if remaining_budget <= 0:
                break
            
            if metrics["roi"] > 0:
                channel_budget = min(
                    remaining_budget * Decimal("0.4"),
                    Decimal(str(metrics["cost"])) * Decimal("1.5")
                )

                allocation[channel.value] = {
                    "budget": channel_budget,
                    "expected_roi": metrics["roi"],
                    "expected_conversions": int(channel_budget / Decimal(str(metrics["cpa"])))
                }
                remaining_budget -= channel_budget
        
        if remaining_budget > 0 and allocation:
            best_channel = sorted_channels[0][0]
            allocation[best_channel.value]["budget"] += remaining_budget
        
        return {
            "total_budget": budget,
            "allocations": allocation,
            "expected_total_roi": sum(a["expected_roi"] * float(a["budget"]) for a in allocation.values()),
            "expected_conversions": sum(a["expected_conversions"] for a in allocation.values())
        }
    
    async def analyze_conversion_funnel(
        self,
        funnel_name: str,
        stages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze conversion funnel performance"""
        
        if len(stages) < 2:
            return {"error": "Funnel must have at least 2 stages"}

        
        conversion_rates = []

        dropoff_points = []
        
        for i in range(len(stages) - 1):
            current = stages[i].get("visitors", 0)


            next_stage = stages[i + 1].get("visitors", 0)


            
            rate = (next_stage / current * 100) if current > 0 else 0
            conversion_rates.append(rate)

            
            if rate < 50:
                dropoff_points.append({
                    "stage": stages[i].get("name", f"Stage {i+1}"),
                    "rate": rate,
                    "lost_visitors": current - next_stage
                })


        
        overall_conversion = (stages[-1].get("visitors", 0) / stages[0].get("visitors", 1)) * 100
        
        self.conversion_funnels[funnel_name] = stages
        
        return {
            "funnel_name": funnel_name,
            "stages": len(stages),
            "overall_conversion_rate": overall_conversion,
            "stage_conversion_rates": conversion_rates,
            "critical_dropoff_points": sorted(dropoff_points, key=lambda x: x["lost_visitors"], reverse=True)[:3],
            "total_visitors": stages[0].get("visitors", 0),
            "conversions": stages[-1].get("visitors", 0)
        }
    
    async def predict_acquisition_cost(
        self,
        channel: AcquisitionChannel,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict future acquisition costs"""
        
        if len(historical_data) < 5:
            return {
                "channel": channel.value,
                "predicted_cpa": 0,
                "confidence": 0.3,
                "trend": "insufficient_data"
            }

        
        costs = [d.get("cost", 0) for d in historical_data]

        conversions = [d.get("conversions", 1) for d in historical_data]

        cpas = [costs[i] / conversions[i] if conversions[i] > 0 else 0 for i in range(len(costs))]

        
        recent_cpa = statistics.mean(cpas[-5:])

        older_cpa = statistics.mean(cpas[:5])


        
        trend = "increasing" if recent_cpa > older_cpa * 1.1 else \
                "decreasing" if recent_cpa < older_cpa * 0.9 else "stable"
        
        predicted_cpa = recent_cpa * 1.05 if trend == "increasing" else \
                       recent_cpa * 0.95 if trend == "decreasing" else recent_cpa

        
        variance = statistics.stdev(cpas) if len(cpas) > 1 else 0

        confidence = max(0.5, 1.0 - (variance / recent_cpa if recent_cpa > 0 else 1))

        
        self.cost_per_acquisition[channel] = Decimal(str(predicted_cpa))

        
        return {
            "channel": channel.value,
            "current_cpa": recent_cpa,
            "predicted_cpa": predicted_cpa,
            "confidence": confidence,
            "trend": trend,
            "variance": variance
        }


class OnboardingAutomationWorkflows:
    """Automated customer onboarding workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, OnboardingWorkflow] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.completion_stats: Dict[str, List[float]] = defaultdict(list)
        logger.info("OnboardingAutomationWorkflows initialized")
    
    async def create_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        triggers: List[str] = None
    ) -> OnboardingWorkflow:
        """Create new onboarding workflow"""
        
        workflow_id = f"workflow_{name.lower().replace(' ', '_')}_{datetime.now().timestamp()}"
        
        workflow = OnboardingWorkflow(
            workflow_id=workflow_id,
            name=name,
            steps=steps,
            triggers=triggers or ["user_signup"]
        )

        
        self.workflows[workflow_id] = workflow
        logger.info(f"Onboarding workflow created: {name} with {len(steps)} steps")

        
        return workflow
    
    async def start_onboarding(
        self,
        customer_id: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Start onboarding process for customer"""
        
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}

        
        workflow = self.workflows[workflow_id]

        
        session = {
            "customer_id": customer_id,
            "workflow_id": workflow_id,
            "started_at": datetime.now(timezone.utc),
            "current_step": 0,
            "completed_steps": [],
            "status": "in_progress"
        }
        
        self.active_sessions[customer_id] = session

        
        first_step = workflow.steps[0] if workflow.steps else None
        
        return {
            "session_id": customer_id,
            "workflow": workflow.name,
            "total_steps": len(workflow.steps),
            "current_step": first_step,
            "estimated_completion": workflow.average_time
        }
    
    async def complete_step(
        self,
        customer_id: str,
        step_index: int
    ) -> Dict[str, Any]:
        """Mark onboarding step as completed"""
        
        if customer_id not in self.active_sessions:
            return {"error": "No active onboarding session"}

        
        session = self.active_sessions[customer_id]

        workflow = self.workflows[session["workflow_id"]]
        
        if step_index >= len(workflow.steps):
            return {"error": "Invalid step index"}
        
        session["completed_steps"].append(step_index)
        session["current_step"] = step_index + 1

        
        completion_percentage = (len(session["completed_steps"]) / len(workflow.steps)) * 100
        
        if session["current_step"] >= len(workflow.steps):
            session["status"] = "completed"
            session["completed_at"] = datetime.now(timezone.utc)


            
            duration = (session["completed_at"] - session["started_at"]).total_seconds()

            self.completion_stats[workflow.workflow_id].append(duration)

            
            workflow.completion_rate = len(self.completion_stats[workflow.workflow_id]) / \
                                      (len(self.completion_stats[workflow.workflow_id]) + 1) * 100

        
        next_step = workflow.steps[session["current_step"]] if session["current_step"] < len(workflow.steps) else None
        
        return {
            "customer_id": customer_id,
            "completion_percentage": completion_percentage,
            "completed_steps": len(session["completed_steps"]),
            "total_steps": len(workflow.steps),
            "next_step": next_step,
            "status": session["status"]
        }
    
    async def get_workflow_analytics(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Get analytics for onboarding workflow"""
        
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}

        
        workflow = self.workflows[workflow_id]

        
        active_count = sum(1 for s in self.active_sessions.values()
 
                          if s["workflow_id"] == workflow_id and s["status"] == "in_progress")


        
        completed_count = sum(1 for s in self.active_sessions.values()
 
                             if s["workflow_id"] == workflow_id and s["status"] == "completed")


        
        completion_times = self.completion_stats.get(workflow_id, [])

        avg_time = statistics.mean(completion_times) if completion_times else 0
        
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "total_steps": len(workflow.steps),
            "active_sessions": active_count,
            "completed_sessions": completed_count,
            "completion_rate": (completed_count / (active_count + completed_count) * 100) if (active_count + completed_count) > 0 else 0,
            "average_completion_time_seconds": avg_time,
            "average_completion_time_readable": f"{avg_time / 3600:.1f} hours"
        }


class RetentionStrategyImplementer:
    """Implement and manage customer retention strategies"""
    
    def __init__(self):
        self.campaigns: Dict[str, RetentionCampaign] = {}
        self.engagement_triggers: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.retention_scores: Dict[str, float] = {}
        logger.info("RetentionStrategyImplementer initialized")
    
    async def create_retention_campaign(
        self,
        name: str,
        target_segment: str,
        actions: List[Dict[str, Any]]
    ) -> RetentionCampaign:
        """Create new retention campaign"""
        
        campaign_id = f"retention_{name.lower().replace(' ', '_')}_{datetime.now().timestamp()}"
        
        campaign = RetentionCampaign(
            campaign_id=campaign_id,
            name=name,
            target_segment=target_segment,
            actions=actions
        )

        
        self.campaigns[campaign_id] = campaign
        logger.info(f"Retention campaign created: {name} targeting {target_segment}")

        
        return campaign
    
    async def calculate_retention_score(
        self,
        customer_id: str,
        activity_data: Dict[str, Any]
    ) -> float:
        """Calculate customer retention score"""
        
        recency_score = self._calculate_recency_score(activity_data.get("last_activity_days", 90))

        frequency_score = self._calculate_frequency_score(activity_data.get("activities_per_month", 0))

        monetary_score = self._calculate_monetary_score(activity_data.get("total_spent", 0))

        engagement_score = activity_data.get("engagement_score", 0.5)


        
        retention_score = (
            recency_score * 0.3 +
            frequency_score * 0.25 +
            monetary_score * 0.25 +
            engagement_score * 0.2
        )

        
        self.retention_scores[customer_id] = retention_score
        
        return retention_score
    
    def _calculate_recency_score(self, days_since_activity: int) -> float:
        """Score based on recency of activity"""
        if days_since_activity <= 7:
            return 1.0
        elif days_since_activity <= 30:
            return 0.8
        elif days_since_activity <= 90:
            return 0.5
        else:
            return 0.2
    
    def _calculate_frequency_score(self, activities_per_month: float) -> float:
        """
        Score based on activity frequency"""
        if activities_per_month >= 20:
            return 1.0
        elif activities_per_month >= 10:
            return 0.8
        elif activities_per_month >= 5:
            return 0.6
        else:
            return 0.3
    
    def _calculate_monetary_score(self, total_spent: float) -> float:
        """
        Score based on monetary value"""
        if total_spent >= 1000:
            return 1.0
        elif total_spent >= 500:
            return 0.8
        elif total_spent >= 100:
            return 0.6
        else:
            return 0.4
    
    async def trigger_intervention(
        self,
        customer_id: str,
        intervention_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger retention intervention"""
        
        interventions = {
            "reactivation_email": self._send_reactivation_email,
            "special_offer": self._send_special_offer,
            "personal_outreach": self._schedule_personal_outreach,
            "feature_education": self._send_feature_education,
            "win_back_campaign": self._start_win_back_campaign
        }
        
        if intervention_type not in interventions:
            return {"error": "Unknown intervention type"}

        
        result = await interventions[intervention_type](customer_id, context)

        
        self.engagement_triggers[customer_id].append({
            "type": intervention_type,
            "triggered_at": datetime.now(timezone.utc),
            "context": context,
            "result": result
        })

        
        return result
    
    async def _send_reactivation_email(self, customer_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send reactivation email"""
        return {
            "action": "reactivation_email",
            "customer_id": customer_id,
            "status": "sent",
            "message": "Reactivation email sent with personalized content"
        }
    
    async def _send_special_offer(self, customer_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send special offer"""
        discount = context.get("discount_percentage", 20)
        return {
            "action": "special_offer",
            "customer_id": customer_id,
            "offer": f"{discount}% discount",
            "status": "sent"
        }
    
    async def _schedule_personal_outreach(self, customer_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule personal outreach"""
        return {
            "action": "personal_outreach",
            "customer_id": customer_id,
            "scheduled_for": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "status": "scheduled"
        }
    
    async def _send_feature_education(self, customer_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send feature education"""
        return {
            "action": "feature_education",
            "customer_id": customer_id,
            "features": context.get("features", []),
            "status": "sent"
        }
    
    async def _start_win_back_campaign(self, customer_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Start win-back campaign"""
        return {
            "action": "win_back_campaign",
            "customer_id": customer_id,
            "campaign_duration": "30_days",
            "status": "started"
        }


class ChurnPredictionPreventer:
    """Predict customer churn and prevent it proactively"""
    
    def __init__(self):
        self.churn_predictions: Dict[str, Dict[str, Any]] = {}
        self.risk_factors: Dict[str, List[str]] = defaultdict(list)
        self.prevention_actions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        logger.info("ChurnPredictionPreventer initialized")
    
    async def predict_churn_risk(
        self,
        customer_id: str,
        activity_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict customer churn risk using multiple factors"""
        
        risk_factors = []

        risk_score = 0.0

        
        days_inactive = activity_metrics.get("days_since_last_activity", 0)
        if days_inactive > 30:
            risk_factors.append("Extended inactivity")

            risk_score += 0.3
        elif days_inactive > 14:
            risk_factors.append("Recent inactivity")

            risk_score += 0.15

        
        engagement_trend = activity_metrics.get("engagement_trend", 0)
        if engagement_trend < -0.2:
            risk_factors.append("Declining engagement")

            risk_score += 0.25

        
        support_tickets = activity_metrics.get("recent_support_tickets", 0)
        if support_tickets > 3:
            risk_factors.append("Multiple support issues")

            risk_score += 0.2

        
        feature_usage = activity_metrics.get("feature_usage_percentage", 100)
        if feature_usage < 30:
            risk_factors.append("Low feature adoption")

            risk_score += 0.15

        
        payment_issues = activity_metrics.get("payment_failures", 0)
        if payment_issues > 0:
            risk_factors.append("Payment problems")

            risk_score += 0.25

        
        competitor_research = activity_metrics.get("competitor_research_detected", False)
        if competitor_research:
            risk_factors.append("Researching competitors")

            risk_score += 0.2

        
        risk_score = min(risk_score, 1.0)

        
        if risk_score >= 0.7:
            risk_level = ChurnRisk.CRITICAL
        elif risk_score >= 0.5:
            risk_level = ChurnRisk.HIGH
        elif risk_score >= 0.3:
            risk_level = ChurnRisk.MEDIUM
        else:
            risk_level = ChurnRisk.LOW
        
        self.churn_predictions[customer_id] = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "predicted_at": datetime.now(timezone.utc)
        }
        
        self.risk_factors[customer_id] = risk_factors
        
        logger.info(f"Churn risk predicted for {customer_id}: {risk_level.value} ({risk_score:.2f})")

        
        return {
            "customer_id": customer_id,
            "risk_level": risk_level.value,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommended_actions": await self._recommend_prevention_actions(risk_level, risk_factors)
        }
    
    async def _recommend_prevention_actions(
        self,
        risk_level: ChurnRisk,
        risk_factors: List[str]
    ) -> List[Dict[str, Any]]:
        """Recommend prevention actions based on risk"""
        
        actions = []
        
        if risk_level in [ChurnRisk.CRITICAL, ChurnRisk.HIGH]:
            actions.append({
                "priority": "urgent",
                "action": "personal_outreach",
                "description": "Schedule immediate call with customer success manager"
            })

            
            if "Payment problems" in risk_factors:
                actions.append({
                    "priority": "urgent",
                    "action": "payment_assistance",
                    "description": "Offer payment plan options or temporary access"
                })

            
            actions.append({
                "priority": "high",
                "action": "special_retention_offer",
                "description": "Provide exclusive discount or feature upgrade"
            })

        
        if risk_level == ChurnRisk.MEDIUM:
            actions.append({
                "priority": "medium",
                "action": "engagement_campaign",
                "description": "Send targeted feature education and success stories"
            })

            
            if "Low feature adoption" in risk_factors:
                actions.append({
                    "priority": "medium",
                    "action": "onboarding_refresh",
                    "description": "Provide personalized product tour"
                })

        
        if "Multiple support issues" in risk_factors:
            actions.append({
                "priority": "high",
                "action": "support_escalation",
                "description": "Assign dedicated support representative"
            })

        
        return actions
    
    async def execute_prevention_strategy(
        self,
        customer_id: str,
        actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute churn prevention strategy"""
        
        executed = []
        
        for action in actions:
            result = {
                "action_type": action["action"],
                "executed_at": datetime.now(timezone.utc),
                "status": "completed",
                "details": action.get("description")
            }
            
            executed.append(result)

            self.prevention_actions[customer_id].append(result)

        
        logger.info(f"Executed {len(executed)} prevention actions for {customer_id}")

        
        return {
            "customer_id": customer_id,
            "actions_executed": len(executed),
            "execution_details": executed,
            "next_review_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        }
    
    async def track_prevention_effectiveness(
        self,
        customer_id: str,
        outcome: str
    ) -> Dict[str, Any]:
        """Track effectiveness of prevention efforts"""
        
        if customer_id not in self.churn_predictions:
            return {"error": "No prediction record found"}

        
        prediction = self.churn_predictions[customer_id]

        actions_taken = len(self.prevention_actions.get(customer_id, []))


        
        effectiveness = {
            "customer_id": customer_id,
            "initial_risk": prediction["risk_level"].value,
            "actions_taken": actions_taken,
            "outcome": outcome,
            "days_since_prediction": (datetime.now(timezone.utc) - prediction["predicted_at"]).days
        }
        
        if outcome == "retained":
            effectiveness["success"] = True
            effectiveness["message"] = "Prevention strategy successful"
        elif outcome == "churned":
            effectiveness["success"] = False
            effectiveness["message"] = "Customer churned despite prevention efforts"
        else:
            effectiveness["success"] = None
            effectiveness["message"] = "Outcome pending"
        
        return effectiveness
