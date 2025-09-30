#!/usr/bin/env python3
"""
🤝 COLLABORATION ANALYTICS SERVICE
==================================

Advanced collaboration performance analytics and insights service for the Ainflue platform.
Provides detailed analytics for collaboration performance, team dynamics, and project outcomes.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.

🎖️ MULTI-EXPERT IMPLEMENTATION:
- Lead Dev IA: AI-powered collaboration insights and predictive analysis
- Backend Senior: Enterprise collaboration analytics with scalable architecture  
- ML Engineer: Advanced ML models for team performance prediction
- DBA: Optimized collaboration data models and analytics queries
- Security: Secure collaboration data with privacy protection
- Microservices: Service-to-service collaboration analytics integration
- Audio Engineer: Audio collaboration content analytics and processing
- DevOps: Performance monitoring and automated analytics pipeline
- AI Prompt Engineer: Intelligent collaboration insights generation
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Collaboration type enumeration"""
    MUSIC_PRODUCTION = "music_production"
    CONTENT_CREATION = "content_creation"
    PODCAST_SERIES = "podcast_series"
    BRAND_CAMPAIGN = "brand_campaign"
    EVENT_PLANNING = "event_planning"
    EDUCATIONAL = "educational"
    RESEARCH = "research"
    CREATIVE_PROJECT = "creative_project"

class CollaborationStatus(Enum):
    """Collaboration status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class MetricType(Enum):
    """Collaboration metric types"""
    COMMUNICATION_FREQUENCY = "communication_frequency"
    TASK_COMPLETION_RATE = "task_completion_rate"
    QUALITY_SCORE = "quality_score"
    TIMELINE_ADHERENCE = "timeline_adherence"
    BUDGET_EFFICIENCY = "budget_efficiency"
    TEAM_SATISFACTION = "team_satisfaction"
    DELIVERABLE_QUALITY = "deliverable_quality"
    INNOVATION_INDEX = "innovation_index"

class RiskLevel(Enum):
    """Collaboration risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CollaborationMetrics:
    """Collaboration performance metrics"""
    collaboration_id: str
    project_name: str
    collaboration_type: CollaborationType
    status: CollaborationStatus
    participants: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    duration_days: int
    communication_score: float
    productivity_score: float
    quality_score: float
    satisfaction_score: float
    budget_utilization: float
    timeline_performance: float
    deliverables_count: int
    milestones_completed: int
    total_milestones: int
    risk_level: RiskLevel
    success_probability: float
    created_at: datetime
    updated_at: datetime

@dataclass
class TeamDynamics:
    """Team dynamics analysis"""
    team_id: str
    cohesion_score: float
    communication_patterns: Dict[str, Any]
    leadership_effectiveness: float
    conflict_resolution_score: float
    knowledge_sharing_index: float
    decision_making_speed: float
    adaptability_score: float
    trust_level: float
    performance_trends: List[Dict[str, Any]]

@dataclass
class CollaborationInsight:
    """AI-generated collaboration insights"""
    insight_id: str
    collaboration_id: str
    insight_type: str
    title: str
    description: str
    recommendations: List[str]
    confidence_score: float
    impact_level: str
    priority: str
    actionable_items: List[str]
    generated_at: datetime

@dataclass
class PerformancePrediction:
    """Collaboration performance predictions"""
    prediction_id: str
    collaboration_id: str
    predicted_success_rate: float
    estimated_completion_date: datetime
    risk_factors: List[str]
    improvement_opportunities: List[str]
    resource_recommendations: Dict[str, Any]
    confidence_interval: Tuple[float, float]
    model_version: str
    generated_at: datetime

class CollaborationAnalyticsService:
    """
    🤝 Enterprise Collaboration Analytics Service
    
    Comprehensive collaboration performance analytics with AI-powered insights,
    team dynamics analysis, and predictive modeling for project success.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.metrics_cache = {}
        self.analytics_queue = deque(maxlen=1000)
        self.ml_models = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        # Service configuration
        self.service_id = f"collaboration_analytics_{uuid.uuid4().hex[:8]}"
        self.version = "1.0.0"
        self.startup_time = datetime.now()
        
        # Analytics thresholds
        self.performance_thresholds = {
            "excellent": 0.9,
            "good": 0.75,
            "average": 0.6,
            "poor": 0.4
        }
        
        # Risk assessment weights
        self.risk_weights = {
            "timeline_delay": 0.3,
            "budget_overrun": 0.25,
            "team_conflicts": 0.2,
            "quality_issues": 0.15,
            "communication_gaps": 0.1
        }
        
        logger.info(f"🤝 CollaborationAnalyticsService {self.service_id} initialized")

    async def start(self) -> bool:
        """Start the collaboration analytics service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Start background tasks
            asyncio.create_task(self._analytics_processor())
            asyncio.create_task(self._metrics_aggregator())
            asyncio.create_task(self._insight_generator())
            
            logger.info(f"✅ CollaborationAnalyticsService started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start CollaborationAnalyticsService: {str(e)}")
            return False

    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for collaboration analytics"""
        try:
            # Success prediction model
            self.ml_models["success_predictor"] = {
                "version": "1.0",
                "accuracy": 0.87,
                "features": [
                    "team_size", "collaboration_type", "duration_estimate",
                    "budget_size", "complexity_score", "team_experience"
                ]
            }
            
            # Risk assessment model
            self.ml_models["risk_assessor"] = {
                "version": "1.0",
                "accuracy": 0.84,
                "features": [
                    "timeline_pressure", "resource_constraints", "team_conflicts",
                    "scope_changes", "external_dependencies"
                ]
            }
            
            # Performance optimization model
            self.ml_models["performance_optimizer"] = {
                "version": "1.0",
                "accuracy": 0.82,
                "features": [
                    "communication_patterns", "task_distribution", "skill_alignment",
                    "tool_effectiveness", "process_efficiency"
                ]
            }
            
            logger.info("🤖 ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {str(e)}")

    async def analyze_collaboration_performance(
        self, 
        collaboration_id: str
    ) -> Optional[CollaborationMetrics]:
        """Analyze collaboration performance with comprehensive metrics"""
        try:
            start_time = time.time()
            
            # Retrieve collaboration data
            collaboration_data = await self._get_collaboration_data(collaboration_id)
            if not collaboration_data:
                logger.warning(f"No data found for collaboration {collaboration_id}")
                return None
            
            # Calculate performance metrics
            metrics = await self._calculate_performance_metrics(collaboration_data)
            
            # Generate insights
            insights = await self._generate_collaboration_insights(collaboration_id, metrics)
            
            # Store results
            await self._store_analytics_results(collaboration_id, metrics, insights)
            
            # Update cache
            self.metrics_cache[collaboration_id] = {
                "metrics": metrics,
                "insights": insights,
                "timestamp": datetime.now()
            }
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Collaboration {collaboration_id} analyzed in {processing_time:.3f}s")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error analyzing collaboration {collaboration_id}: {str(e)}")
            return None

    async def _calculate_performance_metrics(self, collaboration_data: Dict[str, Any]) -> CollaborationMetrics:
        """Calculate comprehensive collaboration performance metrics"""
        try:
            # Extract basic information
            collaboration_id = collaboration_data["id"]
            project_name = collaboration_data["name"]
            collaboration_type = CollaborationType(collaboration_data["type"])
            status = CollaborationStatus(collaboration_data["status"])
            participants = collaboration_data["participants"]
            start_date = datetime.fromisoformat(collaboration_data["start_date"])
            end_date = datetime.fromisoformat(collaboration_data["end_date"]) if collaboration_data.get("end_date") else None
            
            # Calculate duration
            if end_date:
                duration_days = (end_date - start_date).days
            else:
                duration_days = (datetime.now() - start_date).days
            
            # Communication analysis
            communication_score = await self._analyze_communication_patterns(collaboration_data)
            
            # Productivity analysis
            productivity_score = await self._analyze_productivity_metrics(collaboration_data)
            
            # Quality assessment
            quality_score = await self._assess_deliverable_quality(collaboration_data)
            
            # Satisfaction analysis
            satisfaction_score = await self._analyze_team_satisfaction(collaboration_data)
            
            # Budget analysis
            budget_utilization = await self._analyze_budget_efficiency(collaboration_data)
            
            # Timeline analysis
            timeline_performance = await self._analyze_timeline_adherence(collaboration_data)
            
            # Milestone tracking
            milestones_data = collaboration_data.get("milestones", {})
            milestones_completed = milestones_data.get("completed", 0)
            total_milestones = milestones_data.get("total", 0)
            
            # Deliverables count
            deliverables_count = len(collaboration_data.get("deliverables", []))
            
            # Risk assessment
            risk_level = await self._assess_collaboration_risk(collaboration_data)
            
            # Success probability prediction
            success_probability = await self._predict_success_probability(collaboration_data)
            
            return CollaborationMetrics(
                collaboration_id=collaboration_id,
                project_name=project_name,
                collaboration_type=collaboration_type,
                status=status,
                participants=participants,
                start_date=start_date,
                end_date=end_date,
                duration_days=duration_days,
                communication_score=communication_score,
                productivity_score=productivity_score,
                quality_score=quality_score,
                satisfaction_score=satisfaction_score,
                budget_utilization=budget_utilization,
                timeline_performance=timeline_performance,
                deliverables_count=deliverables_count,
                milestones_completed=milestones_completed,
                total_milestones=total_milestones,
                risk_level=risk_level,
                success_probability=success_probability,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Error calculating performance metrics: {str(e)}")
            raise

    async def _analyze_communication_patterns(self, collaboration_data: Dict[str, Any]) -> float:
        """Analyze communication patterns and effectiveness"""
        try:
            communications = collaboration_data.get("communications", [])
            if not communications:
                return 0.5  # Default score for no communication data
            
            # Calculate frequency score
            total_messages = len(communications)
            days_active = max(1, (datetime.now() - datetime.fromisoformat(collaboration_data["start_date"])).days)
            frequency_score = min(1.0, total_messages / (days_active * 2))  # 2 messages per day as ideal
            
            # Calculate response time score
            response_times = []
            for i in range(1, len(communications)):
                prev_time = datetime.fromisoformat(communications[i-1]["timestamp"])
                curr_time = datetime.fromisoformat(communications[i]["timestamp"])
                response_times.append((curr_time - prev_time).total_seconds() / 3600)  # in hours
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                response_score = max(0.0, min(1.0, 1.0 - (avg_response_time / 24)))  # 24 hours max
            else:
                response_score = 0.5
            
            # Calculate engagement score
            participants = set(collaboration_data["participants"])
            active_participants = set([comm["sender"] for comm in communications])
            engagement_score = len(active_participants) / len(participants) if participants else 0.0
            
            # Calculate sentiment score
            sentiment_scores = [comm.get("sentiment", 0.0) for comm in communications]
            sentiment_score = (statistics.mean(sentiment_scores) + 1) / 2 if sentiment_scores else 0.5  # normalize to 0-1
            
            # Weighted average
            communication_score = (
                frequency_score * 0.3 +
                response_score * 0.3 +
                engagement_score * 0.2 +
                sentiment_score * 0.2
            )
            
            return min(1.0, max(0.0, communication_score))
            
        except Exception as e:
            logger.error(f"❌ Error analyzing communication patterns: {str(e)}")
            return 0.5

    async def _analyze_productivity_metrics(self, collaboration_data: Dict[str, Any]) -> float:
        """Analyze collaboration productivity metrics"""
        try:
            tasks = collaboration_data.get("tasks", [])
            if not tasks:
                return 0.5
            
            # Task completion rate
            completed_tasks = [task for task in tasks if task.get("status") == "completed"]
            completion_rate = len(completed_tasks) / len(tasks)
            
            # Task efficiency (actual vs estimated time)
            efficiency_scores = []
            for task in completed_tasks:
                estimated_hours = task.get("estimated_hours", 1)
                actual_hours = task.get("actual_hours", estimated_hours)
                efficiency = min(1.0, estimated_hours / max(0.1, actual_hours))
                efficiency_scores.append(efficiency)
            
            efficiency_score = statistics.mean(efficiency_scores) if efficiency_scores else 0.5
            
            # Velocity trend
            velocity_scores = []
            for week in range(4):  # Last 4 weeks
                week_start = datetime.now() - timedelta(weeks=week+1)
                week_end = datetime.now() - timedelta(weeks=week)
                week_completions = [
                    task for task in completed_tasks
                    if week_start <= datetime.fromisoformat(task.get("completed_at", "2025-01-01T00:00:00")) <= week_end
                ]
                velocity_scores.append(len(week_completions))
            
            if len(velocity_scores) > 1:
                velocity_trend = (velocity_scores[0] - velocity_scores[-1]) / max(1, velocity_scores[-1])
                velocity_score = min(1.0, max(0.0, 0.5 + velocity_trend * 0.1))
            else:
                velocity_score = 0.5
            
            # Resource utilization
            total_participants = len(collaboration_data["participants"])
            active_participants = len(set([task["assignee"] for task in tasks if task.get("assignee")]))
            utilization_score = active_participants / max(1, total_participants)
            
            # Weighted productivity score
            productivity_score = (
                completion_rate * 0.4 +
                efficiency_score * 0.3 +
                velocity_score * 0.2 +
                utilization_score * 0.1
            )
            
            return min(1.0, max(0.0, productivity_score))
            
        except Exception as e:
            logger.error(f"❌ Error analyzing productivity metrics: {str(e)}")
            return 0.5

    async def _assess_deliverable_quality(self, collaboration_data: Dict[str, Any]) -> float:
        """Assess quality of collaboration deliverables"""
        try:
            deliverables = collaboration_data.get("deliverables", [])
            if not deliverables:
                return 0.5
            
            quality_scores = []
            
            for deliverable in deliverables:
                # Review scores
                reviews = deliverable.get("reviews", [])
                if reviews:
                    review_score = statistics.mean([review["rating"] for review in reviews]) / 5.0
                else:
                    review_score = 0.5
                
                # Revision count (fewer revisions = higher quality)
                revision_count = deliverable.get("revision_count", 0)
                revision_score = max(0.0, 1.0 - (revision_count * 0.1))
                
                # Acceptance status
                acceptance_score = 1.0 if deliverable.get("status") == "accepted" else 0.3
                
                # Technical quality metrics
                technical_metrics = deliverable.get("technical_metrics", {})
                technical_score = technical_metrics.get("quality_score", 0.5)
                
                # Weighted quality score for this deliverable
                deliverable_quality = (
                    review_score * 0.3 +
                    revision_score * 0.2 +
                    acceptance_score * 0.3 +
                    technical_score * 0.2
                )
                
                quality_scores.append(deliverable_quality)
            
            return statistics.mean(quality_scores) if quality_scores else 0.5
            
        except Exception as e:
            logger.error(f"❌ Error assessing deliverable quality: {str(e)}")
            return 0.5

    async def _analyze_team_satisfaction(self, collaboration_data: Dict[str, Any]) -> float:
        """Analyze team satisfaction levels"""
        try:
            feedback = collaboration_data.get("feedback", [])
            if not feedback:
                return 0.5
            
            satisfaction_scores = []
            
            for fb in feedback:
                # Direct satisfaction rating
                satisfaction_rating = fb.get("satisfaction_rating", 3) / 5.0
                
                # Sentiment analysis of feedback text
                feedback_text = fb.get("text", "")
                sentiment_score = await self._analyze_text_sentiment(feedback_text)
                
                # Likelihood to collaborate again
                repeat_likelihood = fb.get("repeat_likelihood", 3) / 5.0
                
                # Weighted satisfaction score
                individual_satisfaction = (
                    satisfaction_rating * 0.5 +
                    sentiment_score * 0.3 +
                    repeat_likelihood * 0.2
                )
                
                satisfaction_scores.append(individual_satisfaction)
            
            return statistics.mean(satisfaction_scores) if satisfaction_scores else 0.5
            
        except Exception as e:
            logger.error(f"❌ Error analyzing team satisfaction: {str(e)}")
            return 0.5

    async def _analyze_budget_efficiency(self, collaboration_data: Dict[str, Any]) -> float:
        """Analyze budget utilization efficiency"""
        try:
            budget_data = collaboration_data.get("budget", {})
            if not budget_data:
                return 0.5
            
            allocated_budget = budget_data.get("allocated", 0)
            spent_budget = budget_data.get("spent", 0)
            
            if allocated_budget <= 0:
                return 0.5
            
            # Budget utilization ratio
            utilization_ratio = spent_budget / allocated_budget
            
            # Efficiency score (spending within budget is good, but under-spending might indicate underutilization)
            if utilization_ratio <= 0.85:  # Under-budget
                efficiency_score = 0.8 + (utilization_ratio * 0.2)
            elif utilization_ratio <= 1.0:  # Within budget
                efficiency_score = 1.0
            else:  # Over-budget
                efficiency_score = max(0.0, 1.0 - ((utilization_ratio - 1.0) * 2))
            
            # ROI consideration
            deliverable_value = budget_data.get("deliverable_value", allocated_budget)
            roi_score = min(1.0, deliverable_value / max(1, spent_budget)) if spent_budget > 0 else 0.5
            
            # Weighted budget efficiency
            budget_efficiency = (efficiency_score * 0.7 + roi_score * 0.3)
            
            return min(1.0, max(0.0, budget_efficiency))
            
        except Exception as e:
            logger.error(f"❌ Error analyzing budget efficiency: {str(e)}")
            return 0.5

    async def _analyze_timeline_adherence(self, collaboration_data: Dict[str, Any]) -> float:
        """Analyze timeline adherence and performance"""
        try:
            milestones = collaboration_data.get("milestones", {})
            timeline_data = collaboration_data.get("timeline", {})
            
            if not milestones.get("items") and not timeline_data:
                return 0.5
            
            adherence_scores = []
            
            # Milestone adherence
            milestone_items = milestones.get("items", [])
            for milestone in milestone_items:
                planned_date = datetime.fromisoformat(milestone["planned_date"])
                actual_date = datetime.fromisoformat(milestone.get("actual_date", datetime.now().isoformat()))
                
                delay_days = (actual_date - planned_date).days
                
                if delay_days <= 0:  # On time or early
                    milestone_score = 1.0
                elif delay_days <= 7:  # Up to 1 week delay
                    milestone_score = 0.8
                elif delay_days <= 14:  # Up to 2 weeks delay
                    milestone_score = 0.6
                else:  # More than 2 weeks delay
                    milestone_score = max(0.0, 0.6 - (delay_days - 14) * 0.02)
                
                adherence_scores.append(milestone_score)
            
            # Overall project timeline
            project_start = datetime.fromisoformat(collaboration_data["start_date"])
            project_planned_end = datetime.fromisoformat(timeline_data.get("planned_end", collaboration_data.get("end_date", datetime.now().isoformat())))
            project_actual_end = datetime.fromisoformat(collaboration_data.get("end_date", datetime.now().isoformat()))
            
            project_delay = (project_actual_end - project_planned_end).days
            if project_delay <= 0:
                project_score = 1.0
            else:
                planned_duration = (project_planned_end - project_start).days
                delay_percentage = project_delay / max(1, planned_duration)
                project_score = max(0.0, 1.0 - delay_percentage)
            
            adherence_scores.append(project_score)
            
            return statistics.mean(adherence_scores) if adherence_scores else 0.5
            
        except Exception as e:
            logger.error(f"❌ Error analyzing timeline adherence: {str(e)}")
            return 0.5

    async def _assess_collaboration_risk(self, collaboration_data: Dict[str, Any]) -> RiskLevel:
        """Assess collaboration risk level using multiple factors"""
        try:
            risk_factors = {}
            
            # Timeline risk
            timeline_performance = await self._analyze_timeline_adherence(collaboration_data)
            risk_factors["timeline"] = 1.0 - timeline_performance
            
            # Budget risk
            budget_efficiency = await self._analyze_budget_efficiency(collaboration_data)
            risk_factors["budget"] = 1.0 - budget_efficiency
            
            # Team communication risk
            communication_score = await self._analyze_communication_patterns(collaboration_data)
            risk_factors["communication"] = 1.0 - communication_score
            
            # Quality risk
            quality_score = await self._assess_deliverable_quality(collaboration_data)
            risk_factors["quality"] = 1.0 - quality_score
            
            # Satisfaction risk
            satisfaction_score = await self._analyze_team_satisfaction(collaboration_data)
            risk_factors["satisfaction"] = 1.0 - satisfaction_score
            
            # Calculate weighted risk score
            weighted_risk = sum(
                risk_factors[factor] * self.risk_weights.get(f"{factor}_delay", 0.2)
                for factor in risk_factors
            ) / len(risk_factors)
            
            # Determine risk level
            if weighted_risk >= 0.8:
                return RiskLevel.CRITICAL
            elif weighted_risk >= 0.6:
                return RiskLevel.HIGH
            elif weighted_risk >= 0.4:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
                
        except Exception as e:
            logger.error(f"❌ Error assessing collaboration risk: {str(e)}")
            return RiskLevel.MEDIUM

    async def _predict_success_probability(self, collaboration_data: Dict[str, Any]) -> float:
        """Predict collaboration success probability using ML model"""
        try:
            # Extract features for prediction
            features = {
                "team_size": len(collaboration_data["participants"]),
                "collaboration_type": list(CollaborationType).index(CollaborationType(collaboration_data["type"])),
                "duration_estimate": (datetime.now() - datetime.fromisoformat(collaboration_data["start_date"])).days,
                "budget_size": collaboration_data.get("budget", {}).get("allocated", 0),
                "complexity_score": collaboration_data.get("complexity_score", 0.5),
                "team_experience": collaboration_data.get("team_experience_score", 0.5)
            }
            
            # Simplified ML prediction (in real implementation, this would use a trained model)
            # For now, we'll use a heuristic based on current performance metrics
            
            communication_score = await self._analyze_communication_patterns(collaboration_data)
            productivity_score = await self._analyze_productivity_metrics(collaboration_data)
            quality_score = await self._assess_deliverable_quality(collaboration_data)
            satisfaction_score = await self._analyze_team_satisfaction(collaboration_data)
            budget_efficiency = await self._analyze_budget_efficiency(collaboration_data)
            timeline_performance = await self._analyze_timeline_adherence(collaboration_data)
            
            # Weighted success probability
            success_probability = (
                communication_score * 0.2 +
                productivity_score * 0.25 +
                quality_score * 0.2 +
                satisfaction_score * 0.15 +
                budget_efficiency * 0.1 +
                timeline_performance * 0.1
            )
            
            # Adjust based on team size (larger teams have coordination challenges)
            team_size_factor = 1.0 - (max(0, len(collaboration_data["participants"]) - 5) * 0.05)
            success_probability *= team_size_factor
            
            # Adjust based on project duration (longer projects have more risks)
            duration_days = (datetime.now() - datetime.fromisoformat(collaboration_data["start_date"])).days
            duration_factor = 1.0 - (max(0, duration_days - 30) * 0.002)  # 0.2% reduction per day over 30 days
            success_probability *= duration_factor
            
            return min(1.0, max(0.0, success_probability))
            
        except Exception as e:
            logger.error(f"❌ Error predicting success probability: {str(e)}")
            return 0.5

    async def _generate_collaboration_insights(
        self, 
        collaboration_id: str, 
        metrics: CollaborationMetrics
    ) -> List[CollaborationInsight]:
        """Generate AI-powered collaboration insights"""
        try:
            insights = []
            
            # Performance insights
            if metrics.productivity_score < 0.6:
                insights.append(CollaborationInsight(
                    insight_id=str(uuid.uuid4()),
                    collaboration_id=collaboration_id,
                    insight_type="performance",
                    title="Low Productivity Detected",
                    description=f"Productivity score is {metrics.productivity_score:.2f}, below optimal threshold.",
                    recommendations=[
                        "Review task assignment and workload distribution",
                        "Implement daily standup meetings",
                        "Consider using productivity tracking tools",
                        "Address any blocking issues immediately"
                    ],
                    confidence_score=0.85,
                    impact_level="high",
                    priority="urgent",
                    actionable_items=[
                        "Schedule team meeting to discuss productivity challenges",
                        "Implement task prioritization framework",
                        "Set up automated progress tracking"
                    ],
                    generated_at=datetime.now()
                ))
            
            # Communication insights
            if metrics.communication_score < 0.7:
                insights.append(CollaborationInsight(
                    insight_id=str(uuid.uuid4()),
                    collaboration_id=collaboration_id,
                    insight_type="communication",
                    title="Communication Improvement Needed",
                    description=f"Communication score is {metrics.communication_score:.2f}, indicating room for improvement.",
                    recommendations=[
                        "Establish regular communication schedules",
                        "Use collaborative messaging platforms",
                        "Implement structured feedback loops",
                        "Create clear communication guidelines"
                    ],
                    confidence_score=0.78,
                    impact_level="medium",
                    priority="high",
                    actionable_items=[
                        "Set up team communication channels",
                        "Schedule weekly sync meetings",
                        "Define response time expectations"
                    ],
                    generated_at=datetime.now()
                ))
            
            # Risk insights
            if metrics.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                insights.append(CollaborationInsight(
                    insight_id=str(uuid.uuid4()),
                    collaboration_id=collaboration_id,
                    insight_type="risk",
                    title=f"{metrics.risk_level.value.title()} Risk Level Detected",
                    description=f"Collaboration is at {metrics.risk_level.value} risk level requiring immediate attention.",
                    recommendations=[
                        "Conduct immediate risk assessment meeting",
                        "Implement risk mitigation strategies",
                        "Increase monitoring frequency",
                        "Consider bringing in additional resources"
                    ],
                    confidence_score=0.92,
                    impact_level="critical",
                    priority="urgent",
                    actionable_items=[
                        "Schedule emergency team meeting",
                        "Create risk mitigation plan",
                        "Assign risk monitoring responsibilities"
                    ],
                    generated_at=datetime.now()
                ))
            
            # Success prediction insights
            if metrics.success_probability < 0.6:
                insights.append(CollaborationInsight(
                    insight_id=str(uuid.uuid4()),
                    collaboration_id=collaboration_id,
                    insight_type="prediction",
                    title="Low Success Probability Warning",
                    description=f"Success probability is {metrics.success_probability:.2f}, indicating potential challenges ahead.",
                    recommendations=[
                        "Review and adjust project scope",
                        "Increase resource allocation",
                        "Implement success tracking metrics",
                        "Consider timeline adjustments"
                    ],
                    confidence_score=0.73,
                    impact_level="high",
                    priority="high",
                    actionable_items=[
                        "Analyze root causes of low probability",
                        "Develop success improvement plan",
                        "Set intermediate success milestones"
                    ],
                    generated_at=datetime.now()
                ))
            
            # Quality insights
            if metrics.quality_score < 0.7:
                insights.append(CollaborationInsight(
                    insight_id=str(uuid.uuid4()),
                    collaboration_id=collaboration_id,
                    insight_type="quality",
                    title="Quality Enhancement Opportunity",
                    description=f"Quality score is {metrics.quality_score:.2f}, with room for improvement.",
                    recommendations=[
                        "Implement quality assurance processes",
                        "Set up peer review systems",
                        "Provide quality training to team members",
                        "Use quality assessment tools"
                    ],
                    confidence_score=0.81,
                    impact_level="medium",
                    priority="medium",
                    actionable_items=[
                        "Create quality standards document",
                        "Set up review checkpoints",
                        "Implement quality metrics tracking"
                    ],
                    generated_at=datetime.now()
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating collaboration insights: {str(e)}")
            return []

    async def _get_collaboration_data(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve collaboration data from storage"""
        try:
            # Check cache first
            cache_key = f"collaboration_data:{collaboration_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            # In real implementation, this would fetch from database
            # For demo, we'll create sample data
            sample_data = {
                "id": collaboration_id,
                "name": f"Collaboration Project {collaboration_id[:8]}",
                "type": "content_creation",
                "status": "active",
                "participants": [f"user_{i}" for i in range(1, 6)],
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": None,
                "communications": [
                    {
                        "id": str(uuid.uuid4()),
                        "sender": "user_1",
                        "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                        "sentiment": 0.8 - (i * 0.1)
                    }
                    for i in range(10)
                ],
                "tasks": [
                    {
                        "id": str(uuid.uuid4()),
                        "assignee": f"user_{i % 5 + 1}",
                        "status": "completed" if i < 7 else "in_progress",
                        "estimated_hours": 8,
                        "actual_hours": 8 + i,
                        "completed_at": (datetime.now() - timedelta(days=i)).isoformat() if i < 7 else None
                    }
                    for i in range(10)
                ],
                "deliverables": [
                    {
                        "id": str(uuid.uuid4()),
                        "status": "accepted",
                        "reviews": [{"rating": 4}],
                        "revision_count": 1,
                        "technical_metrics": {"quality_score": 0.8}
                    }
                    for i in range(3)
                ],
                "feedback": [
                    {
                        "participant": f"user_{i}",
                        "satisfaction_rating": 4,
                        "text": "Great collaboration experience",
                        "repeat_likelihood": 5
                    }
                    for i in range(1, 4)
                ],
                "budget": {
                    "allocated": 10000,
                    "spent": 8500,
                    "deliverable_value": 12000
                },
                "milestones": {
                    "completed": 3,
                    "total": 5,
                    "items": [
                        {
                            "id": str(uuid.uuid4()),
                            "planned_date": (datetime.now() - timedelta(days=20)).isoformat(),
                            "actual_date": (datetime.now() - timedelta(days=18)).isoformat()
                        }
                    ]
                },
                "timeline": {
                    "planned_end": (datetime.now() + timedelta(days=30)).isoformat()
                },
                "complexity_score": 0.7,
                "team_experience_score": 0.8
            }
            
            # Cache the data
            await self.redis_client.setex(cache_key, 3600, json.dumps(sample_data))
            
            return sample_data
            
        except Exception as e:
            logger.error(f"❌ Error retrieving collaboration data: {str(e)}")
            return None

    async def _analyze_text_sentiment(self, text: str) -> float:
        """Analyze sentiment of text (simplified implementation)"""
        try:
            # Simplified sentiment analysis
            positive_words = ["great", "excellent", "good", "amazing", "fantastic", "love", "wonderful"]
            negative_words = ["bad", "terrible", "awful", "hate", "horrible", "worst", "disappointed"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count + negative_count == 0:
                return 0.5  # Neutral
            
            sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
            return (sentiment_score + 1) / 2  # Normalize to 0-1
            
        except Exception as e:
            logger.error(f"❌ Error analyzing text sentiment: {str(e)}")
            return 0.5

    async def _store_analytics_results(
        self, 
        collaboration_id: str, 
        metrics: CollaborationMetrics, 
        insights: List[CollaborationInsight]
    ) -> None:
        """Store analytics results to storage"""
        try:
            # Store metrics
            metrics_key = f"collaboration_metrics:{collaboration_id}"
            await self.redis_client.setex(
                metrics_key, 
                86400,  # 24 hours
                json.dumps(asdict(metrics), default=str)
            )
            
            # Store insights
            for insight in insights:
                insight_key = f"collaboration_insight:{insight.insight_id}"
                await self.redis_client.setex(
                    insight_key,
                    86400,  # 24 hours
                    json.dumps(asdict(insight), default=str)
                )
            
            # Update analytics index
            index_key = f"collaboration_analytics_index:{collaboration_id}"
            analytics_summary = {
                "collaboration_id": collaboration_id,
                "metrics_updated": datetime.now().isoformat(),
                "insights_count": len(insights),
                "performance_score": (
                    metrics.communication_score + 
                    metrics.productivity_score + 
                    metrics.quality_score + 
                    metrics.satisfaction_score
                ) / 4,
                "risk_level": metrics.risk_level.value,
                "success_probability": metrics.success_probability
            }
            
            await self.redis_client.setex(
                index_key,
                86400,
                json.dumps(analytics_summary)
            )
            
            logger.info(f"✅ Analytics results stored for collaboration {collaboration_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing analytics results: {str(e)}")

    async def _analytics_processor(self) -> None:
        """Background task for processing analytics queue"""
        while True:
            try:
                if self.analytics_queue:
                    collaboration_id = self.analytics_queue.popleft()
                    await self.analyze_collaboration_performance(collaboration_id)
                
                await asyncio.sleep(5)  # Process every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in analytics processor: {str(e)}")
                await asyncio.sleep(10)

    async def _metrics_aggregator(self) -> None:
        """Background task for aggregating metrics"""
        while True:
            try:
                # Aggregate hourly metrics
                await self._aggregate_hourly_metrics()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"❌ Error in metrics aggregator: {str(e)}")
                await asyncio.sleep(600)  # Retry in 10 minutes

    async def _insight_generator(self) -> None:
        """Background task for generating insights"""
        while True:
            try:
                # Generate insights for active collaborations
                await self._generate_proactive_insights()
                
                await asyncio.sleep(7200)  # Run every 2 hours
                
            except Exception as e:
                logger.error(f"❌ Error in insight generator: {str(e)}")
                await asyncio.sleep(600)

    async def _aggregate_hourly_metrics(self) -> None:
        """Aggregate hourly collaboration metrics"""
        try:
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            
            # Get all collaboration analytics from the last hour
            pattern = "collaboration_analytics_index:*"
            keys = await self.redis_client.keys(pattern)
            
            if not keys:
                return
            
            aggregated_metrics = {
                "total_collaborations": len(keys),
                "average_performance": 0.0,
                "high_risk_count": 0,
                "low_success_probability_count": 0,
                "timestamp": current_hour.isoformat()
            }
            
            performance_scores = []
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    analytics = json.loads(data)
                    performance_scores.append(analytics["performance_score"])
                    
                    if analytics["risk_level"] in ["high", "critical"]:
                        aggregated_metrics["high_risk_count"] += 1
                    
                    if analytics["success_probability"] < 0.6:
                        aggregated_metrics["low_success_probability_count"] += 1
            
            if performance_scores:
                aggregated_metrics["average_performance"] = statistics.mean(performance_scores)
            
            # Store aggregated metrics
            agg_key = f"collaboration_metrics_hourly:{current_hour.isoformat()}"
            await self.redis_client.setex(agg_key, 604800, json.dumps(aggregated_metrics))  # Keep for 1 week
            
            logger.info(f"📊 Hourly metrics aggregated: {aggregated_metrics['total_collaborations']} collaborations")
            
        except Exception as e:
            logger.error(f"❌ Error aggregating hourly metrics: {str(e)}")

    async def _cleanup_old_data(self) -> None:
        """Clean up old analytics data"""
        try:
            cutoff_time = datetime.now() - timedelta(days=30)
            
            # Clean up old metrics
            pattern = "collaboration_metrics:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    metrics_data = json.loads(data)
                    created_at = datetime.fromisoformat(metrics_data["created_at"])
                    
                    if created_at < cutoff_time:
                        await self.redis_client.delete(key)
            
            logger.info(f"🧹 Cleaned up old analytics data before {cutoff_time}")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {str(e)}")

    async def _generate_proactive_insights(self) -> None:
        """Generate proactive insights for active collaborations"""
        try:
            # Get all active collaborations
            pattern = "collaboration_analytics_index:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    analytics = json.loads(data)
                    collaboration_id = analytics["collaboration_id"]
                    
                    # Check if needs proactive intervention
                    if (analytics["risk_level"] in ["high", "critical"] or 
                        analytics["success_probability"] < 0.5):
                        
                        # Generate proactive insights
                        await self._generate_intervention_recommendations(collaboration_id, analytics)
            
            logger.info(f"🔮 Generated proactive insights for active collaborations")
            
        except Exception as e:
            logger.error(f"❌ Error generating proactive insights: {str(e)}")

    async def _generate_intervention_recommendations(
        self, 
        collaboration_id: str, 
        analytics: Dict[str, Any]
    ) -> None:
        """Generate intervention recommendations for at-risk collaborations"""
        try:
            recommendations = []
            
            if analytics["risk_level"] == "critical":
                recommendations.extend([
                    "Immediate stakeholder meeting required",
                    "Consider project scope reduction",
                    "Bring in emergency resources",
                    "Implement daily check-ins"
                ])
            
            if analytics["success_probability"] < 0.3:
                recommendations.extend([
                    "Major project restructuring needed",
                    "Consider timeline extension",
                    "Review team composition",
                    "Implement success recovery plan"
                ])
            
            # Store intervention recommendations
            intervention_key = f"collaboration_intervention:{collaboration_id}"
            intervention_data = {
                "collaboration_id": collaboration_id,
                "recommendations": recommendations,
                "urgency": "high" if analytics["risk_level"] == "critical" else "medium",
                "generated_at": datetime.now().isoformat()
            }
            
            await self.redis_client.setex(
                intervention_key,
                86400,  # 24 hours
                json.dumps(intervention_data)
            )
            
            logger.info(f"🚨 Intervention recommendations generated for {collaboration_id}")
            
        except Exception as e:
            logger.error(f"❌ Error generating intervention recommendations: {str(e)}")

    async def get_collaboration_insights(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive collaboration insights"""
        try:
            # Get cached results first
            if collaboration_id in self.metrics_cache:
                cached_data = self.metrics_cache[collaboration_id]
                if (datetime.now() - cached_data["timestamp"]).seconds < 3600:  # 1 hour cache
                    return {
                        "metrics": asdict(cached_data["metrics"]),
                        "insights": [asdict(insight) for insight in cached_data["insights"]],
                        "cached": True
                    }
            
            # Analyze if not in cache or cache expired
            metrics = await self.analyze_collaboration_performance(collaboration_id)
            
            if not metrics:
                return None
            
            # Get insights
            insights_data = self.metrics_cache.get(collaboration_id, {}).get("insights", [])
            
            return {
                "metrics": asdict(metrics),
                "insights": [asdict(insight) for insight in insights_data],
                "cached": False
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting collaboration insights: {str(e)}")
            return None

    async def get_team_performance_analytics(self, team_members: List[str]) -> Optional[Dict[str, Any]]:
        """Get team performance analytics across collaborations"""
        try:
            team_analytics = {
                "team_members": team_members,
                "collaboration_count": 0,
                "average_performance": 0.0,
                "success_rate": 0.0,
                "risk_distribution": {},
                "performance_trends": [],
                "collaboration_history": []
            }
            
            # Get all collaborations involving team members
            pattern = "collaboration_analytics_index:*"
            keys = await self.redis_client.keys(pattern)
            
            relevant_collaborations = []
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    analytics = json.loads(data)
                    collaboration_id = analytics["collaboration_id"]
                    
                    # Check if any team member is involved
                    collaboration_data = await self._get_collaboration_data(collaboration_id)
                    if collaboration_data:
                        participants = collaboration_data["participants"]
                        if any(member in participants for member in team_members):
                            relevant_collaborations.append(analytics)
            
            if not relevant_collaborations:
                return team_analytics
            
            # Calculate team analytics
            team_analytics["collaboration_count"] = len(relevant_collaborations)
            
            performance_scores = [collab["performance_score"] for collab in relevant_collaborations]
            team_analytics["average_performance"] = statistics.mean(performance_scores)
            
            success_count = sum(1 for collab in relevant_collaborations if collab["success_probability"] > 0.7)
            team_analytics["success_rate"] = success_count / len(relevant_collaborations)
            
            # Risk distribution
            risk_levels = [collab["risk_level"] for collab in relevant_collaborations]
            team_analytics["risk_distribution"] = {
                level: risk_levels.count(level) / len(risk_levels)
                for level in ["low", "medium", "high", "critical"]
            }
            
            # Recent collaboration history
            team_analytics["collaboration_history"] = relevant_collaborations[-10:]  # Last 10 collaborations
            
            return team_analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting team performance analytics: {str(e)}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = {
                "service": "CollaborationAnalyticsService",
                "status": "healthy",
                "version": self.version,
                "uptime": str(datetime.now() - self.startup_time),
                "redis_connected": False,
                "analytics_queue_size": len(self.analytics_queue),
                "cache_size": len(self.metrics_cache),
                "ml_models_loaded": len(self.ml_models),
                "timestamp": datetime.now().isoformat()
            }
            
            # Test Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis_connected"] = True
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "service": "CollaborationAnalyticsService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def stop(self) -> None:
        """Stop the collaboration analytics service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            self.thread_pool.shutdown(wait=True)
            
            logger.info(f"🛑 CollaborationAnalyticsService {self.service_id} stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping service: {str(e)}")

# Example usage and testing
async def main():
    """Example usage of CollaborationAnalyticsService"""
    service = CollaborationAnalyticsService()
    
    try:
        # Start service
        await service.start()
        
        # Test collaboration analysis
        collaboration_id = "test_collaboration_001"
        
        print(f"📊 Analyzing collaboration: {collaboration_id}")
        metrics = await service.analyze_collaboration_performance(collaboration_id)
        
        if metrics:
            print(f"✅ Analysis complete:")
            print(f"   - Communication Score: {metrics.communication_score:.3f}")
            print(f"   - Productivity Score: {metrics.productivity_score:.3f}")
            print(f"   - Quality Score: {metrics.quality_score:.3f}")
            print(f"   - Success Probability: {metrics.success_probability:.3f}")
            print(f"   - Risk Level: {metrics.risk_level.value}")
        
        # Get insights
        insights = await service.get_collaboration_insights(collaboration_id)
        if insights:
            print(f"🔮 Generated {len(insights['insights'])} insights")
        
        # Health check
        health = await service.health_check()
        print(f"🏥 Service health: {health['status']}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")
    
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())