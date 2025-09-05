"""Milestone Tracker Module - AI-Powered Project Milestone Management System
===========================================================================

Advanced milestone tracking system providing intelligent milestone planning,
progress monitoring, delivery forecasting, and performance analysis for
collaborative projects.

This module implements:
- Dynamic milestone creation and management
- AI-powered progress prediction
- Automated milestone validation
- Performance analytics and insights
- Risk assessment and mitigation
- Delivery forecasting with confidence intervals

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import json
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


class MilestoneStatus(Enum):
    """Milestone completion status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class MilestoneType(Enum):
    """Types of milestones"""
    DELIVERABLE = "deliverable"
    PAYMENT = "payment"
    APPROVAL = "approval"
    CHECKPOINT = "checkpoint"
    DEADLINE = "deadline"
    REVIEW = "review"
    RELEASE = "release"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProgressIndicator(Enum):
    """Progress trend indicators"""
    ON_TRACK = "on_track"
    AHEAD = "ahead"
    BEHIND = "behind"
    AT_RISK = "at_risk"
    CRITICAL = "critical"


@dataclass
class MilestoneDeliverable:
    """Deliverable associated with milestone"""
    deliverable_id: str
    name: str
    description: str
    file_type: str
    expected_size: Optional[int] = None
    quality_criteria: List[str] = field(default_factory=list)
    submitted_file: Optional[str] = None
    submission_date: Optional[datetime] = None
    approval_status: str = "pending"


@dataclass
class MilestoneMetrics:
    """Performance metrics for milestone"""
    planned_duration: timedelta
    actual_duration: Optional[timedelta] = None
    effort_estimate: float = 0.0  # Person-hours
    actual_effort: float = 0.0
    quality_score: float = 0.0  # 0-100
    stakeholder_satisfaction: float = 0.0  # 0-100
    budget_allocated: Decimal = Decimal("0")
    budget_used: Decimal = Decimal("0")
    complexity_score: float = 1.0  # 1-10


@dataclass
class RiskAssessment:
    """Risk assessment for milestone"""
    risk_id: str
    risk_level: RiskLevel
    probability: float  # 0-1
    impact: float  # 0-1
    description: str
    mitigation_plan: str
    contingency_plan: str
    owner: Optional[str] = None
    identified_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_reviewed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProjectMilestone:
    """Complete milestone definition"""
    milestone_id: str
    project_id: str
    name: str
    description: str
    milestone_type: MilestoneType
    status: MilestoneStatus
    
    # Timeline
    planned_start: datetime
    planned_end: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    baseline_end: Optional[datetime] = None  # Original planned end
    
    # Progress tracking
    progress_percentage: float = 0.0
    progress_indicator: ProgressIndicator = ProgressIndicator.ON_TRACK
    
    # Dependencies
    predecessor_milestones: List[str] = field(default_factory=list)
    successor_milestones: List[str] = field(default_factory=list)
    dependent_tasks: List[str] = field(default_factory=list)
    
    # Deliverables and criteria
    deliverables: List[MilestoneDeliverable] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    
    # Team and stakeholders
    responsible_team: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    approvers: List[str] = field(default_factory=list)
    
    # Performance metrics
    metrics: MilestoneMetrics = field(default_factory=MilestoneMetrics)
    
    # Risk management
    risks: List[RiskAssessment] = field(default_factory=list)
    
    # Communication
    last_update: Optional[datetime] = None
    update_notes: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None


@dataclass
class ProgressAnalysis:
    """Analysis of milestone progress"""
    milestone_id: str
    analysis_date: datetime
    
    # Current status
    current_progress: float
    expected_progress: float
    variance: float
    
    # Trend analysis
    velocity: float  # Progress per day
    acceleration: float  # Change in velocity
    trend_direction: str  # "improving", "declining", "stable"
    
    # Forecasting
    estimated_completion: datetime
    confidence_interval: Tuple[datetime, datetime]
    probability_on_time: float
    
    # Insights
    key_factors: List[str]
    blockers: List[str]
    recommendations: List[str]


@dataclass
class DeliveryForecast:
    """AI-powered delivery forecast"""
    forecast_id: str
    milestone_id: str
    forecast_date: datetime
    
    # Predictions
    most_likely_completion: datetime
    optimistic_completion: datetime
    pessimistic_completion: datetime
    confidence_score: float  # 0-1
    
    # Factors
    historical_performance: float
    current_velocity: float
    resource_availability: float
    complexity_factor: float
    external_dependencies: float
    
    # Scenarios
    best_case_scenario: str
    worst_case_scenario: str
    most_likely_scenario: str
    
    # Recommendations
    action_items: List[str]
    resource_needs: List[str]
    risk_mitigation: List[str]


class MilestoneTracker:
    """Advanced milestone tracking and analysis system"""
    
    def __init__(self):
        self.milestones: Dict[str, ProjectMilestone] = {}
        self.progress_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.forecasts: Dict[str, List[DeliveryForecast]] = defaultdict(list)
        self.project_timelines: Dict[str, List[str]] = defaultdict(list)
        
        # Configuration
        self.progress_update_threshold = 5.0  # 5% change to trigger updates
        self.risk_assessment_frequency = timedelta(days=7)
        self.forecast_horizon = timedelta(days=90)
        
        logger.info("🎯 Milestone Tracker initialized with AI-powered forecasting")
    
    async def create_milestone(
        self,
        project_id: str,
        name: str,
        description: str,
        milestone_type: MilestoneType,
        planned_start: datetime,
        planned_end: datetime,
        responsible_team: List[str],
        acceptance_criteria: Optional[List[str]] = None,
        deliverables: Optional[List[Dict[str, Any]]] = None
    ) -> ProjectMilestone:
        """Create a new project milestone"""
        try:
            milestone_id = str(uuid.uuid4())
            
            # Create deliverables
            milestone_deliverables = []
            if deliverables:
                for deliv_data in deliverables:
                    deliverable = MilestoneDeliverable(
                        deliverable_id=str(uuid.uuid4()),
                        name=deliv_data["name"],
                        description=deliv_data["description"],
                        file_type=deliv_data.get("file_type", "document"),
                        quality_criteria=deliv_data.get("quality_criteria", [])
                    )
                    milestone_deliverables.append(deliverable)
            
            # Calculate initial metrics
            planned_duration = planned_end - planned_start
            complexity_score = await self._calculate_complexity_score(
                description, milestone_deliverables, planned_duration
            )
            
            metrics = MilestoneMetrics(
                planned_duration=planned_duration,
                complexity_score=complexity_score
            )
            
            milestone = ProjectMilestone(
                milestone_id=milestone_id,
                project_id=project_id,
                name=name,
                description=description,
                milestone_type=milestone_type,
                status=MilestoneStatus.PLANNED,
                planned_start=planned_start,
                planned_end=planned_end,
                baseline_end=planned_end,
                responsible_team=responsible_team,
                acceptance_criteria=acceptance_criteria or [],
                deliverables=milestone_deliverables,
                metrics=metrics
            )
            
            self.milestones[milestone_id] = milestone
            self.project_timelines[project_id].append(milestone_id)
            
            # Initial risk assessment
            await self._assess_initial_risks(milestone)
            
            logger.info(f"🎯 Milestone created: {milestone_id} - {name}")
            return milestone
            
        except Exception as e:
            logger.error(f"❌ Error creating milestone: {e}")
            raise
    
    async def update_milestone_progress(
        self,
        milestone_id: str,
        progress_percentage: float,
        update_notes: Optional[str] = None,
        deliverable_updates: Optional[List[Dict[str, Any]]] = None
    ) -> ProgressAnalysis:
        """Update milestone progress and analyze trends"""
        try:
            if milestone_id not in self.milestones:
                raise ValueError(f"Milestone {milestone_id} not found")
            
            milestone = self.milestones[milestone_id]
            previous_progress = milestone.progress_percentage
            
            # Update progress
            milestone.progress_percentage = min(100.0, max(0.0, progress_percentage))
            milestone.last_update = datetime.now(timezone.utc)
            milestone.updated_at = datetime.now(timezone.utc)
            
            if update_notes:
                milestone.update_notes.append(f"{datetime.now(timezone.utc).isoformat()}: {update_notes}")
            
            # Update deliverables
            if deliverable_updates:
                await self._update_deliverables(milestone, deliverable_updates)
            
            # Update status based on progress
            await self._update_milestone_status(milestone)
            
            # Record progress history
            progress_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "progress": progress_percentage,
                "notes": update_notes,
                "status": milestone.status.value
            }
            self.progress_history[milestone_id].append(progress_entry)
            
            # Analyze progress if significant change
            if abs(progress_percentage - previous_progress) >= self.progress_update_threshold:
                analysis = await self.analyze_milestone_progress(milestone_id)
                
                # Update progress indicator
                milestone.progress_indicator = await self._determine_progress_indicator(analysis)
                
                # Generate new forecast
                await self._generate_delivery_forecast(milestone_id)
                
                return analysis
            
            logger.info(f"📊 Progress updated: {milestone_id} - {progress_percentage:.1f}%")
            return await self.analyze_milestone_progress(milestone_id)
            
        except Exception as e:
            logger.error(f"❌ Error updating milestone progress: {e}")
            raise
    
    async def analyze_milestone_progress(self, milestone_id: str) -> ProgressAnalysis:
        """Analyze milestone progress and trends"""
        try:
            if milestone_id not in self.milestones:
                raise ValueError(f"Milestone {milestone_id} not found")
            
            milestone = self.milestones[milestone_id]
            progress_data = self.progress_history[milestone_id]
            
            # Calculate expected progress
            now = datetime.now(timezone.utc)
            if now < milestone.planned_start:
                expected_progress = 0.0
            elif now > milestone.planned_end:
                expected_progress = 100.0
            else:
                elapsed = now - milestone.planned_start
                total_duration = milestone.planned_end - milestone.planned_start
                expected_progress = (elapsed.total_seconds() / total_duration.total_seconds()) * 100
            
            # Calculate variance
            variance = milestone.progress_percentage - expected_progress
            
            # Calculate velocity and acceleration
            velocity, acceleration = await self._calculate_velocity_metrics(progress_data)
            
            # Determine trend
            trend_direction = await self._analyze_trend_direction(progress_data)
            
            # Forecast completion
            estimated_completion, confidence_interval, probability_on_time = await self._forecast_completion(
                milestone, velocity
            )
            
            # Identify factors and blockers
            key_factors = await self._identify_key_factors(milestone, progress_data)
            blockers = await self._identify_blockers(milestone)
            recommendations = await self._generate_recommendations(milestone, variance, velocity)
            
            analysis = ProgressAnalysis(
                milestone_id=milestone_id,
                analysis_date=now,
                current_progress=milestone.progress_percentage,
                expected_progress=expected_progress,
                variance=variance,
                velocity=velocity,
                acceleration=acceleration,
                trend_direction=trend_direction,
                estimated_completion=estimated_completion,
                confidence_interval=confidence_interval,
                probability_on_time=probability_on_time,
                key_factors=key_factors,
                blockers=blockers,
                recommendations=recommendations
            )
            
            logger.info(f"📈 Progress analysis completed: {milestone_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing milestone progress: {e}")
            raise
    
    async def generate_milestone_forecast(self, milestone_id: str) -> DeliveryForecast:
        """Generate AI-powered delivery forecast"""
        try:
            if milestone_id not in self.milestones:
                raise ValueError(f"Milestone {milestone_id} not found")
            
            milestone = self.milestones[milestone_id]
            
            # Gather input factors
            historical_performance = await self._calculate_historical_performance(milestone.project_id)
            current_velocity = await self._get_current_velocity(milestone_id)
            resource_availability = await self._assess_resource_availability(milestone)
            complexity_factor = milestone.metrics.complexity_score / 10.0
            external_dependencies = await self._assess_external_dependencies(milestone)
            
            # Generate scenarios
            optimistic_days = await self._calculate_optimistic_scenario(
                milestone, current_velocity, resource_availability
            )
            pessimistic_days = await self._calculate_pessimistic_scenario(
                milestone, complexity_factor, external_dependencies
            )
            most_likely_days = await self._calculate_most_likely_scenario(
                milestone, historical_performance, current_velocity
            )
            
            # Convert to dates
            base_date = milestone.actual_start or datetime.now(timezone.utc)
            optimistic_completion = base_date + timedelta(days=optimistic_days)
            pessimistic_completion = base_date + timedelta(days=pessimistic_days)
            most_likely_completion = base_date + timedelta(days=most_likely_days)
            
            # Calculate confidence score
            confidence_score = await self._calculate_forecast_confidence(
                historical_performance, current_velocity, complexity_factor
            )
            
            # Generate scenarios descriptions
            scenarios = await self._generate_scenario_descriptions(milestone, optimistic_days, pessimistic_days)
            
            # Generate recommendations
            action_items = await self._generate_action_items(milestone, most_likely_completion)
            resource_needs = await self._identify_resource_needs(milestone, resource_availability)
            risk_mitigation = await self._suggest_risk_mitigation(milestone)
            
            forecast = DeliveryForecast(
                forecast_id=str(uuid.uuid4()),
                milestone_id=milestone_id,
                forecast_date=datetime.now(timezone.utc),
                most_likely_completion=most_likely_completion,
                optimistic_completion=optimistic_completion,
                pessimistic_completion=pessimistic_completion,
                confidence_score=confidence_score,
                historical_performance=historical_performance,
                current_velocity=current_velocity,
                resource_availability=resource_availability,
                complexity_factor=complexity_factor,
                external_dependencies=external_dependencies,
                best_case_scenario=scenarios["best_case"],
                worst_case_scenario=scenarios["worst_case"],
                most_likely_scenario=scenarios["most_likely"],
                action_items=action_items,
                resource_needs=resource_needs,
                risk_mitigation=risk_mitigation
            )
            
            self.forecasts[milestone_id].append(forecast)
            
            logger.info(f"🔮 Delivery forecast generated: {milestone_id}")
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Error generating forecast: {e}")
            raise
    
    async def get_project_milestone_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive milestone dashboard for project"""
        try:
            project_milestones = [
                milestone for milestone in self.milestones.values()
                if milestone.project_id == project_id
            ]
            
            if not project_milestones:
                return {"error": "No milestones found for project"}
            
            # Calculate summary statistics
            total_milestones = len(project_milestones)
            completed_milestones = len([m for m in project_milestones if m.status == MilestoneStatus.COMPLETED])
            in_progress_milestones = len([m for m in project_milestones if m.status == MilestoneStatus.IN_PROGRESS])
            delayed_milestones = len([m for m in project_milestones if m.status == MilestoneStatus.DELAYED])
            
            # Calculate overall progress
            total_progress = sum(m.progress_percentage for m in project_milestones)
            overall_progress = total_progress / total_milestones if total_milestones > 0 else 0
            
            # Identify critical milestones
            critical_milestones = [
                m for m in project_milestones
                if m.progress_indicator in [ProgressIndicator.AT_RISK, ProgressIndicator.CRITICAL]
            ]
            
            # Calculate timeline metrics
            timeline_metrics = await self._calculate_timeline_metrics(project_milestones)
            
            # Get upcoming milestones
            upcoming_milestones = [
                m for m in project_milestones
                if m.planned_end > datetime.now(timezone.utc) and m.status != MilestoneStatus.COMPLETED
            ]
            upcoming_milestones.sort(key=lambda x: x.planned_end)
            
            # Risk assessment
            high_risk_milestones = [
                m for m in project_milestones
                if any(risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] for risk in m.risks)
            ]
            
            dashboard = {
                "project_id": project_id,
                "summary": {
                    "total_milestones": total_milestones,
                    "completed": completed_milestones,
                    "in_progress": in_progress_milestones,
                    "delayed": delayed_milestones,
                    "overall_progress": overall_progress,
                    "completion_rate": (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
                },
                "timeline": timeline_metrics,
                "critical_milestones": [
                    {
                        "milestone_id": m.milestone_id,
                        "name": m.name,
                        "status": m.status.value,
                        "progress": m.progress_percentage,
                        "planned_end": m.planned_end.isoformat(),
                        "indicator": m.progress_indicator.value
                    }
                    for m in critical_milestones[:5]  # Top 5 critical
                ],
                "upcoming_milestones": [
                    {
                        "milestone_id": m.milestone_id,
                        "name": m.name,
                        "planned_end": m.planned_end.isoformat(),
                        "progress": m.progress_percentage,
                        "days_remaining": (m.planned_end - datetime.now(timezone.utc)).days
                    }
                    for m in upcoming_milestones[:5]  # Next 5
                ],
                "risk_assessment": {
                    "high_risk_count": len(high_risk_milestones),
                    "total_risks": sum(len(m.risks) for m in project_milestones),
                    "risk_distribution": await self._calculate_risk_distribution(project_milestones)
                },
                "performance_insights": await self._generate_performance_insights(project_milestones)
            }
            
            logger.info(f"📊 Milestone dashboard generated for project {project_id}")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Error generating milestone dashboard: {e}")
            return {"error": str(e)}
    
    # Helper methods for calculations and analysis
    
    async def _calculate_complexity_score(
        self,
        description: str,
        deliverables: List[MilestoneDeliverable],
        duration: timedelta
    ) -> float:
        """Calculate complexity score based on various factors"""
        score = 1.0
        
        # Duration factor
        if duration.days > 30:
            score += 2.0
        elif duration.days > 14:
            score += 1.0
        elif duration.days > 7:
            score += 0.5
        
        # Deliverables factor
        score += len(deliverables) * 0.5
        
        # Description complexity (simplified NLP)
        complex_keywords = ["integration", "complex", "multiple", "coordinate", "dependencies", "critical"]
        for keyword in complex_keywords:
            if keyword in description.lower():
                score += 0.3
        
        return min(score, 10.0)
    
    async def _assess_initial_risks(self, milestone: ProjectMilestone):
        """Assess initial risks for milestone"""
        risks = []
        
        # Timeline risk
        if milestone.metrics.complexity_score > 7.0:
            risks.append(RiskAssessment(
                risk_id=str(uuid.uuid4()),
                risk_level=RiskLevel.MEDIUM,
                probability=0.6,
                impact=0.7,
                description="High complexity may lead to timeline delays",
                mitigation_plan="Break down into smaller tasks, add buffer time",
                contingency_plan="Extend deadline or reduce scope if necessary"
            ))
        
        # Resource risk
        if len(milestone.responsible_team) < 2:
            risks.append(RiskAssessment(
                risk_id=str(uuid.uuid4()),
                risk_level=RiskLevel.MEDIUM,
                probability=0.4,
                impact=0.8,
                description="Single point of failure with limited team",
                mitigation_plan="Assign backup team members",
                contingency_plan="Cross-train team members or outsource"
            ))
        
        milestone.risks.extend(risks)
    
    async def _update_deliverables(self, milestone: ProjectMilestone, updates: List[Dict[str, Any]]):
        """Update milestone deliverables"""
        for update in updates:
            deliverable_id = update.get("deliverable_id")
            deliverable = next(
                (d for d in milestone.deliverables if d.deliverable_id == deliverable_id),
                None
            )
            
            if deliverable:
                if "submitted_file" in update:
                    deliverable.submitted_file = update["submitted_file"]
                    deliverable.submission_date = datetime.now(timezone.utc)
                
                if "approval_status" in update:
                    deliverable.approval_status = update["approval_status"]
    
    async def _update_milestone_status(self, milestone: ProjectMilestone):
        """Update milestone status based on progress and conditions"""
        if milestone.progress_percentage == 0:
            milestone.status = MilestoneStatus.PLANNED
        elif milestone.progress_percentage < 100:
            milestone.status = MilestoneStatus.IN_PROGRESS
        else:
            # Check if all deliverables are approved
            all_approved = all(
                d.approval_status == "approved" for d in milestone.deliverables
            ) if milestone.deliverables else True
            
            if all_approved:
                milestone.status = MilestoneStatus.COMPLETED
                milestone.actual_end = datetime.now(timezone.utc)
            else:
                milestone.status = MilestoneStatus.UNDER_REVIEW
    
    async def _calculate_velocity_metrics(self, progress_data: List[Dict[str, Any]]) -> Tuple[float, float]:
        """Calculate velocity and acceleration from progress data"""
        if len(progress_data) < 2:
            return 0.0, 0.0
        
        # Calculate daily velocity
        recent_data = progress_data[-7:]  # Last 7 data points
        velocities = []
        
        for i in range(1, len(recent_data)):
            time_diff = (
                datetime.fromisoformat(recent_data[i]["timestamp"]) -
                datetime.fromisoformat(recent_data[i-1]["timestamp"])
            ).total_seconds() / 86400  # Convert to days
            
            progress_diff = recent_data[i]["progress"] - recent_data[i-1]["progress"]
            
            if time_diff > 0:
                velocities.append(progress_diff / time_diff)
        
        velocity = statistics.mean(velocities) if velocities else 0.0
        
        # Calculate acceleration (change in velocity)
        if len(velocities) >= 2:
            recent_velocity = statistics.mean(velocities[-3:]) if len(velocities) >= 3 else velocities[-1]
            early_velocity = statistics.mean(velocities[:3]) if len(velocities) >= 3 else velocities[0]
            acceleration = recent_velocity - early_velocity
        else:
            acceleration = 0.0
        
        return velocity, acceleration
    
    async def _analyze_trend_direction(self, progress_data: List[Dict[str, Any]]) -> str:
        """Analyze trend direction from progress data"""
        if len(progress_data) < 3:
            return "stable"
        
        recent_progress = [entry["progress"] for entry in progress_data[-5:]]
        
        # Calculate linear trend
        x = list(range(len(recent_progress)))
        slope = sum((x[i] - statistics.mean(x)) * (recent_progress[i] - statistics.mean(recent_progress)) 
                   for i in range(len(x))) / sum((x[i] - statistics.mean(x))**2 for i in range(len(x)))
        
        if slope > 1.0:
            return "improving"
        elif slope < -1.0:
            return "declining"
        else:
            return "stable"
    
    async def _forecast_completion(
        self,
        milestone: ProjectMilestone,
        velocity: float
    ) -> Tuple[datetime, Tuple[datetime, datetime], float]:
        """Forecast completion date and confidence"""
        if velocity <= 0:
            # Fallback to planned end if no velocity data
            estimated = milestone.planned_end
            confidence_interval = (milestone.planned_end, milestone.planned_end + timedelta(days=7))
            probability = 0.5
        else:
            remaining_progress = 100.0 - milestone.progress_percentage
            days_to_completion = remaining_progress / velocity if velocity > 0 else 30
            
            estimated = datetime.now(timezone.utc) + timedelta(days=days_to_completion)
            
            # Confidence interval (±20% of estimated time)
            margin_days = days_to_completion * 0.2
            confidence_interval = (
                estimated - timedelta(days=margin_days),
                estimated + timedelta(days=margin_days)
            )
            
            # Probability of on-time completion
            if estimated <= milestone.planned_end:
                probability = 0.8
            else:
                days_late = (estimated - milestone.planned_end).days
                probability = max(0.1, 0.8 - (days_late * 0.1))
        
        return estimated, confidence_interval, probability
    
    async def _determine_progress_indicator(self, analysis: ProgressAnalysis) -> ProgressIndicator:
        """Determine progress indicator based on analysis"""
        if analysis.variance > 10:
            return ProgressIndicator.AHEAD
        elif analysis.variance < -20:
            return ProgressIndicator.CRITICAL
        elif analysis.variance < -10:
            return ProgressIndicator.AT_RISK
        elif analysis.variance < -5:
            return ProgressIndicator.BEHIND
        else:
            return ProgressIndicator.ON_TRACK
    
    async def _identify_key_factors(self, milestone: ProjectMilestone, progress_data: List[Dict[str, Any]]) -> List[str]:
        """Identify key factors affecting milestone progress"""
        factors = []
        
        if milestone.metrics.complexity_score > 7:
            factors.append("High complexity milestone requiring careful coordination")
        
        if len(milestone.responsible_team) > 5:
            factors.append("Large team requiring effective communication")
        
        if len(milestone.dependencies) > 3:
            factors.append("Multiple dependencies affecting timeline")
        
        if milestone.deliverables:
            factors.append(f"{len(milestone.deliverables)} deliverables requiring quality review")
        
        return factors
    
    async def _identify_blockers(self, milestone: ProjectMilestone) -> List[str]:
        """Identify current blockers"""
        blockers = []
        
        # Check for unsubmitted deliverables past due
        for deliverable in milestone.deliverables:
            if not deliverable.submitted_file and milestone.progress_percentage > 80:
                blockers.append(f"Missing deliverable: {deliverable.name}")
        
        # Check for high-risk items
        for risk in milestone.risks:
            if risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                blockers.append(f"High risk: {risk.description}")
        
        return blockers
    
    async def _generate_recommendations(self, milestone: ProjectMilestone, variance: float, velocity: float) -> List[str]:
        """Generate recommendations based on milestone analysis"""
        recommendations = []
        
        if variance < -10:
            recommendations.append("Consider adding resources or extending timeline")
        
        if velocity < 2.0:
            recommendations.append("Review process efficiency and remove bottlenecks")
        
        if len(milestone.risks) > 3:
            recommendations.append("Implement risk mitigation strategies")
        
        if milestone.progress_percentage > 50 and not milestone.deliverables:
            recommendations.append("Define and track specific deliverables")
        
        return recommendations
    
    # Forecasting helper methods
    
    async def _generate_delivery_forecast(self, milestone_id: str):
        """Generate and store delivery forecast"""
        forecast = await self.generate_milestone_forecast(milestone_id)
        # Forecast is automatically stored in generate_milestone_forecast
        return forecast
    
    async def _calculate_historical_performance(self, project_id: str) -> float:
        """Calculate historical performance factor"""
        project_milestones = [m for m in self.milestones.values() if m.project_id == project_id]
        completed_milestones = [m for m in project_milestones if m.status == MilestoneStatus.COMPLETED]
        
        if not completed_milestones:
            return 0.8  # Default moderate performance
        
        on_time_count = sum(
            1 for m in completed_milestones
            if m.actual_end and m.planned_end and m.actual_end <= m.planned_end
        )
        
        return on_time_count / len(completed_milestones)
    
    async def _get_current_velocity(self, milestone_id: str) -> float:
        """Get current velocity for milestone"""
        progress_data = self.progress_history[milestone_id]
        velocity, _ = await self._calculate_velocity_metrics(progress_data)
        return max(velocity, 0.1)  # Minimum velocity to avoid division by zero
    
    async def _assess_resource_availability(self, milestone: ProjectMilestone) -> float:
        """Assess resource availability factor"""
        # Simplified assessment - in real implementation would check actual resource allocation
        if len(milestone.responsible_team) >= 3:
            return 0.9  # Good resource availability
        elif len(milestone.responsible_team) >= 2:
            return 0.7  # Moderate availability
        else:
            return 0.5  # Limited availability
    
    async def _assess_external_dependencies(self, milestone: ProjectMilestone) -> float:
        """Assess external dependency factor"""
        # Simplified assessment based on dependency count
        dependency_count = len(milestone.predecessor_milestones)
        if dependency_count == 0:
            return 0.1
        elif dependency_count <= 2:
            return 0.3
        else:
            return 0.6
    
    async def _calculate_optimistic_scenario(self, milestone: ProjectMilestone, velocity: float, resource_availability: float) -> float:
        """Calculate optimistic completion days"""
        remaining_progress = 100.0 - milestone.progress_percentage
        base_days = remaining_progress / max(velocity, 0.1)
        
        # Apply optimistic factors
        optimistic_days = base_days * 0.8 * resource_availability
        return max(optimistic_days, 1.0)
    
    async def _calculate_pessimistic_scenario(self, milestone: ProjectMilestone, complexity_factor: float, external_dependencies: float) -> float:
        """Calculate pessimistic completion days"""
        remaining_progress = 100.0 - milestone.progress_percentage
        velocity = await self._get_current_velocity(milestone.milestone_id)
        base_days = remaining_progress / max(velocity, 0.1)
        
        # Apply pessimistic factors
        pessimistic_days = base_days * (1.5 + complexity_factor * 0.3 + external_dependencies * 0.4)
        return pessimistic_days
    
    async def _calculate_most_likely_scenario(self, milestone: ProjectMilestone, historical_performance: float, velocity: float) -> float:
        """Calculate most likely completion days"""
        remaining_progress = 100.0 - milestone.progress_percentage
        base_days = remaining_progress / max(velocity, 0.1)
        
        # Adjust based on historical performance
        performance_factor = 1.0 + (0.8 - historical_performance) * 0.5
        most_likely_days = base_days * performance_factor
        
        return most_likely_days
    
    async def _calculate_forecast_confidence(self, historical_performance: float, velocity: float, complexity_factor: float) -> float:
        """Calculate confidence score for forecast"""
        confidence = 0.5  # Base confidence
        
        # Historical performance factor
        confidence += (historical_performance - 0.5) * 0.3
        
        # Velocity factor (consistent velocity increases confidence)
        if velocity > 1.0:
            confidence += 0.2
        
        # Complexity factor (higher complexity reduces confidence)
        confidence -= (complexity_factor - 5.0) / 10.0 * 0.2
        
        return max(0.1, min(1.0, confidence))
    
    async def _generate_scenario_descriptions(self, milestone: ProjectMilestone, optimistic_days: float, pessimistic_days: float) -> Dict[str, str]:
        """Generate scenario descriptions"""
        return {
            "best_case": f"With optimal resources and no blockers, completion in {optimistic_days:.0f} days",
            "worst_case": f"With current challenges and risks, may take up to {pessimistic_days:.0f} days",
            "most_likely": "Based on current velocity and team performance, moderate timeline expected"
        }
    
    async def _generate_action_items(self, milestone: ProjectMilestone, estimated_completion: datetime) -> List[str]:
        """Generate action items for milestone"""
        actions = []
        
        if estimated_completion > milestone.planned_end:
            actions.append("Review timeline and consider scope adjustments")
        
        if milestone.progress_percentage < 50:
            actions.append("Accelerate initial milestone activities")
        
        if len(milestone.risks) > 0:
            actions.append("Address identified risks and implement mitigation plans")
        
        return actions
    
    async def _identify_resource_needs(self, milestone: ProjectMilestone, resource_availability: float) -> List[str]:
        """Identify resource needs"""
        needs = []
        
        if resource_availability < 0.7:
            needs.append("Additional team members or skill augmentation")
        
        if milestone.metrics.complexity_score > 7:
            needs.append("Subject matter expert consultation")
        
        needs.append("Regular progress monitoring and reporting")
        
        return needs
    
    async def _suggest_risk_mitigation(self, milestone: ProjectMilestone) -> List[str]:
        """Suggest risk mitigation strategies"""
        strategies = []
        
        for risk in milestone.risks:
            if risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                strategies.append(f"Implement {risk.mitigation_plan}")
        
        if not strategies:
            strategies.append("Establish regular checkpoint reviews")
        
        return strategies
    
    # Dashboard helper methods
    
    async def _calculate_timeline_metrics(self, milestones: List[ProjectMilestone]) -> Dict[str, Any]:
        """Calculate timeline metrics for project"""
        if not milestones:
            return {}
        
        # Overall timeline
        earliest_start = min(m.planned_start for m in milestones)
        latest_end = max(m.planned_end for m in milestones)
        total_duration = (latest_end - earliest_start).days
        
        # Progress metrics
        completed_on_time = len([
            m for m in milestones
            if m.status == MilestoneStatus.COMPLETED and m.actual_end and m.actual_end <= m.planned_end
        ])
        total_completed = len([m for m in milestones if m.status == MilestoneStatus.COMPLETED])
        
        return {
            "project_duration_days": total_duration,
            "earliest_start": earliest_start.isoformat(),
            "latest_end": latest_end.isoformat(),
            "on_time_completion_rate": (completed_on_time / max(total_completed, 1)) * 100,
            "average_milestone_duration": statistics.mean(
                [(m.planned_end - m.planned_start).days for m in milestones]
            )
        }
    
    async def _calculate_risk_distribution(self, milestones: List[ProjectMilestone]) -> Dict[str, int]:
        """Calculate risk distribution across milestones"""
        distribution = {level.value: 0 for level in RiskLevel}
        
        for milestone in milestones:
            for risk in milestone.risks:
                distribution[risk.risk_level.value] += 1
        
        return distribution
    
    async def _generate_performance_insights(self, milestones: List[ProjectMilestone]) -> List[str]:
        """Generate performance insights for project"""
        insights = []
        
        # Progress insights
        avg_progress = statistics.mean([m.progress_percentage for m in milestones])
        if avg_progress > 75:
            insights.append("Project is making good overall progress")
        elif avg_progress < 25:
            insights.append("Project may need additional focus and resources")
        
        # Timeline insights
        delayed_count = len([m for m in milestones if m.status == MilestoneStatus.DELAYED])
        if delayed_count > len(milestones) * 0.3:
            insights.append("Multiple milestone delays detected - review timeline")
        
        # Risk insights
        high_risk_count = sum(
            len([r for r in m.risks if r.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
            for m in milestones
        )
        if high_risk_count > 5:
            insights.append("High number of critical risks require immediate attention")
        
        return insights


# Example usage
async def main():
    """Example usage of milestone tracker"""
    tracker = MilestoneTracker()
    
    project_id = "project_001"
    
    # Create milestones
    milestone1 = await tracker.create_milestone(
        project_id=project_id,
        name="Design Phase Completion",
        description="Complete all design mockups and user experience flows",
        milestone_type=MilestoneType.DELIVERABLE,
        planned_start=datetime.now(timezone.utc),
        planned_end=datetime.now(timezone.utc) + timedelta(days=14),
        responsible_team=["designer_001", "ux_researcher_001"],
        acceptance_criteria=[
            "All mockups approved by stakeholders",
            "UX flows documented and validated",
            "Design system components defined"
        ],
        deliverables=[
            {
                "name": "UI Mockups",
                "description": "Complete UI mockups for all pages",
                "file_type": "figma",
                "quality_criteria": ["Responsive design", "Accessibility compliance"]
            },
            {
                "name": "UX Flow Documentation",
                "description": "User experience flow documentation",
                "file_type": "pdf",
                "quality_criteria": ["Complete user journeys", "Clear annotations"]
            }
        ]
    )
    
    print(f"Milestone created: {milestone1.milestone_id}")
    
    # Update progress
    analysis = await tracker.update_milestone_progress(
        milestone_id=milestone1.milestone_id,
        progress_percentage=25.0,
        update_notes="Initial design concepts completed"
    )
    
    print(f"Progress analysis: {analysis.variance:.1f}% variance from expected")
    
    # Generate forecast
    forecast = await tracker.generate_milestone_forecast(milestone1.milestone_id)
    print(f"Forecast: Most likely completion on {forecast.most_likely_completion.date()}")
    
    # Get dashboard
    dashboard = await tracker.get_project_milestone_dashboard(project_id)
    print(f"Project dashboard: {dashboard['summary']}")


if __name__ == "__main__":
    asyncio.run(main())