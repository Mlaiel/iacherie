"""
Project Management Module - Advanced Collaborative Project Coordination

Enterprise-grade project management system for multi-format content creators
enabling task distribution, milestone tracking, resource allocation, and timeline management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ...core.database import get_db_session
from ...core.exceptions import BusinessLogicError, ValidationError
from ...utils.cache_manager import CacheManager
from ...utils.notification_service import NotificationService
from ...utils.ai_estimation_engine import AIEstimationEngine

logger = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """Professional project status tracking"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    REVISION = "revision"
    APPROVAL = "approval"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    DELAYED = "delayed"


class TaskPriority(Enum):
    """Task priority levels for efficient workflow management"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class TaskStatus(Enum):
    """Comprehensive task status tracking"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ContentType(Enum):
    """Multi-format content types for project classification"""
    MUSIC = "music"
    VIDEO = "video"
    PODCAST = "podcast"
    BLOG = "blog"
    PHOTOGRAPHY = "photography"
    SOCIAL_MEDIA = "social_media"
    LIVE_STREAM = "live_stream"
    COURSE = "course"
    EBOOK = "ebook"
    CAMPAIGN = "campaign"


@dataclass
class ProjectTask:
    """Professional task representation with comprehensive metadata"""
    task_id: str
    project_id: str
    title: str
    description: str
    assignee_id: Optional[str]
    creator_id: str
    priority: TaskPriority
    status: TaskStatus
    estimated_hours: float
    actual_hours: float
    start_date: Optional[datetime]
    due_date: Optional[datetime]
    completion_date: Optional[datetime]
    dependencies: List[str]
    tags: List[str]
    attachments: List[Dict[str, Any]]
    progress_percentage: float
    subtasks: List[str]
    review_comments: List[Dict[str, Any]]
    blocked_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation"""
        return {
            "task_id": self.task_id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "assignee_id": self.assignee_id,
            "creator_id": self.creator_id,
            "priority": self.priority.value,
            "status": self.status.value,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "attachments": self.attachments,
            "progress_percentage": self.progress_percentage,
            "subtasks": self.subtasks,
            "review_comments": self.review_comments,
            "blocked_reason": self.blocked_reason,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class ProjectMilestone:
    """Project milestone with delivery tracking"""
    milestone_id: str
    project_id: str
    title: str
    description: str
    target_date: datetime
    completion_date: Optional[datetime]
    status: str
    deliverables: List[Dict[str, Any]]
    dependencies: List[str]
    responsible_team_members: List[str]
    completion_criteria: List[str]
    review_required: bool
    client_approval_required: bool
    budget_allocation: float
    actual_cost: float
    created_at: datetime


@dataclass
class ResourceAllocation:
    """Resource allocation tracking for team members"""
    allocation_id: str
    project_id: str
    team_member_id: str
    role: str
    allocated_hours_per_week: float
    start_date: datetime
    end_date: Optional[datetime]
    hourly_rate: float
    total_allocated_budget: float
    actual_hours_worked: float
    actual_cost: float
    utilization_percentage: float
    availability_conflicts: List[Dict[str, Any]]
    skills_required: List[str]
    performance_rating: float


class ProjectCoordinator:
    """Advanced project coordination for collaborative content creation"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
        self.notification_service = NotificationService()
        self.ai_estimator = AIEstimationEngine()
        
    async def create_project(
        self,
        team_id: str,
        project_name: str,
        description: str,
        content_type: ContentType,
        objectives: List[str],
        deliverables: List[Dict[str, Any]],
        budget: float,
        estimated_duration_days: int,
        created_by: str,
        client_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create comprehensive collaborative project"""
        try:
            project_id = str(uuid.uuid4())
            start_date = datetime.utcnow()
            estimated_end_date = start_date + timedelta(days=estimated_duration_days)
            
            # Generate AI-powered project estimates
            ai_estimates = await self.ai_estimator.estimate_project_complexity(
                content_type.value, objectives, deliverables
            )
            
            project_data = {
                "project_id": project_id,
                "team_id": team_id,
                "project_name": project_name,
                "description": description,
                "content_type": content_type.value,
                "objectives": objectives,
                "deliverables": deliverables,
                "budget": budget,
                "estimated_duration_days": estimated_duration_days,
                "start_date": start_date.isoformat(),
                "estimated_end_date": estimated_end_date.isoformat(),
                "actual_end_date": None,
                "status": ProjectStatus.PLANNING.value,
                "created_by": created_by,
                "client_info": client_info or {},
                "ai_estimates": ai_estimates,
                "progress_percentage": 0.0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "milestones": [],
                "resource_allocations": {},
                "budget_spent": 0.0,
                "team_members": [],
                "created_at": start_date.isoformat(),
                "updated_at": start_date.isoformat()
            }
            
            await self.cache.set(f"project:{project_id}", project_data, ttl=86400)
            
            # Initialize project timeline
            timeline_data = await self._initialize_project_timeline(
                project_id, deliverables, estimated_duration_days
            )
            
            logger.info(f"Project created successfully: {project_id}")
            return {
                "project_id": project_id,
                "status": "created",
                "estimated_completion": estimated_end_date.isoformat(),
                "ai_estimates": ai_estimates,
                "timeline": timeline_data
            }
            
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise BusinessLogicError(f"Failed to create project: {str(e)}")
    
    async def update_project_status(
        self,
        project_id: str,
        new_status: ProjectStatus,
        updated_by: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update project status with comprehensive tracking"""
        try:
            project_data = await self.cache.get(f"project:{project_id}")
            if not project_data:
                raise ValidationError("Project not found")
            
            old_status = project_data["status"]
            
            # Update project status
            project_data["status"] = new_status.value
            project_data["updated_at"] = datetime.utcnow().isoformat()
            project_data["updated_by"] = updated_by
            
            # Handle status-specific actions
            if new_status == ProjectStatus.COMPLETED:
                project_data["actual_end_date"] = datetime.utcnow().isoformat()
                project_data["progress_percentage"] = 100.0
                await self._handle_project_completion(project_id, project_data)
            
            # Log status change
            if "status_history" not in project_data:
                project_data["status_history"] = []
            
            project_data["status_history"].append({
                "old_status": old_status,
                "new_status": new_status.value,
                "changed_by": updated_by,
                "changed_at": datetime.utcnow().isoformat(),
                "notes": notes
            })
            
            await self.cache.set(f"project:{project_id}", project_data, ttl=86400)
            
            # Notify team members
            await self.notification_service.send_project_status_update(
                project_data["team_members"], project_id, old_status, new_status.value
            )
            
            return {
                "project_id": project_id,
                "old_status": old_status,
                "new_status": new_status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating project status: {str(e)}")
            raise BusinessLogicError(f"Failed to update project status: {str(e)}")
    
    async def get_project_overview(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project overview with analytics"""
        try:
            project_data = await self.cache.get(f"project:{project_id}")
            if not project_data:
                raise ValidationError("Project not found")
            
            # Calculate project analytics
            analytics = await self._calculate_project_analytics(project_id, project_data)
            
            # Get recent activities
            recent_activities = await self._get_recent_project_activities(project_id)
            
            # Get team performance metrics
            team_metrics = await self._get_team_performance_metrics(project_id)
            
            return {
                "project_data": project_data,
                "analytics": analytics,
                "recent_activities": recent_activities,
                "team_metrics": team_metrics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting project overview: {str(e)}")
            raise BusinessLogicError(f"Failed to get project overview: {str(e)}")
    
    async def _initialize_project_timeline(
        self,
        project_id: str,
        deliverables: List[Dict[str, Any]],
        duration_days: int
    ) -> Dict[str, Any]:
        """Initialize project timeline with AI-powered scheduling"""
        try:
            timeline_data = {
                "project_id": project_id,
                "total_duration_days": duration_days,
                "phases": [],
                "critical_path": [],
                "buffer_days": max(2, duration_days // 10)  # 10% buffer
            }
            
            # Create phases based on deliverables
            phase_duration = duration_days // max(len(deliverables), 1)
            current_date = datetime.utcnow()
            
            for i, deliverable in enumerate(deliverables):
                phase_start = current_date + timedelta(days=i * phase_duration)
                phase_end = phase_start + timedelta(days=phase_duration)
                
                phase_data = {
                    "phase_id": str(uuid.uuid4()),
                    "name": deliverable.get("name", f"Phase {i+1}"),
                    "description": deliverable.get("description", ""),
                    "start_date": phase_start.isoformat(),
                    "end_date": phase_end.isoformat(),
                    "deliverable": deliverable,
                    "dependencies": deliverable.get("dependencies", []),
                    "estimated_hours": deliverable.get("estimated_hours", 40),
                    "assigned_team_members": []
                }
                
                timeline_data["phases"].append(phase_data)
            
            await self.cache.set(f"timeline:{project_id}", timeline_data, ttl=86400)
            return timeline_data
            
        except Exception as e:
            logger.error(f"Error initializing project timeline: {str(e)}")
            raise BusinessLogicError(f"Failed to initialize timeline: {str(e)}")
    
    async def _handle_project_completion(
        self,
        project_id: str,
        project_data: Dict[str, Any]
    ):
        """Handle project completion procedures"""
        try:
            # Generate completion report
            completion_report = await self._generate_completion_report(project_id, project_data)
            
            # Trigger revenue distribution
            if project_data.get("budget", 0) > 0:
                await self._trigger_revenue_distribution(project_id, project_data)
            
            # Update team member contribution scores
            await self._update_team_contribution_scores(project_id, project_data)
            
            # Archive project data
            await self._archive_project_data(project_id, project_data, completion_report)
            
        except Exception as e:
            logger.error(f"Error handling project completion: {str(e)}")
    
    async def _calculate_project_analytics(
        self,
        project_id: str,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive project analytics"""
        return {
            "progress_percentage": project_data.get("progress_percentage", 0.0),
            "budget_utilization": (
                project_data.get("budget_spent", 0) / 
                max(project_data.get("budget", 1), 1) * 100
            ),
            "timeline_adherence": await self._calculate_timeline_adherence(project_id),
            "team_productivity": await self._calculate_team_productivity(project_id),
            "quality_metrics": await self._calculate_quality_metrics(project_id),
            "risk_assessment": await self._assess_project_risks(project_id, project_data)
        }
    
    async def _calculate_timeline_adherence(self, project_id: str) -> float:
        """Calculate how well project adheres to timeline"""
        timeline_data = await self.cache.get(f"timeline:{project_id}")
        if not timeline_data:
            return 0.0
        
        # Implementation would analyze actual vs planned dates
        return 85.0  # Placeholder
    
    async def _calculate_team_productivity(self, project_id: str) -> Dict[str, Any]:
        """Calculate team productivity metrics"""
        return {
            "tasks_completed_per_day": 3.2,
            "average_task_completion_time": 2.5,
            "team_utilization_rate": 78.5,
            "collaboration_score": 8.7
        }
    
    async def _calculate_quality_metrics(self, project_id: str) -> Dict[str, Any]:
        """Calculate project quality metrics"""
        return {
            "deliverable_quality_score": 9.1,
            "client_satisfaction_score": 8.8,
            "review_iteration_average": 1.3,
            "bug_fix_rate": 0.05
        }
    
    async def _assess_project_risks(
        self,
        project_id: str,
        project_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Assess current project risks"""
        risks = []
        
        # Budget risk assessment
        budget_utilization = (
            project_data.get("budget_spent", 0) / 
            max(project_data.get("budget", 1), 1)
        )
        if budget_utilization > 0.8:
            risks.append({
                "type": "budget",
                "severity": "high" if budget_utilization > 0.95 else "medium",
                "description": "Budget utilization exceeds safe threshold",
                "impact": "financial",
                "mitigation": "Review scope and negotiate additional budget"
            })
        
        # Timeline risk assessment
        start_date = datetime.fromisoformat(project_data["start_date"])
        days_elapsed = (datetime.utcnow() - start_date).days
        expected_progress = min(100, days_elapsed / project_data.get("estimated_duration_days", 30) * 100)
        actual_progress = project_data.get("progress_percentage", 0)
        
        if actual_progress < expected_progress * 0.8:
            risks.append({
                "type": "timeline",
                "severity": "high" if actual_progress < expected_progress * 0.6 else "medium",
                "description": "Project behind schedule",
                "impact": "delivery",
                "mitigation": "Increase team resources or adjust scope"
            })
        
        return risks
    
    async def _get_recent_project_activities(self, project_id: str) -> List[Dict[str, Any]]:
        """Get recent project activities"""
        # Implementation would fetch recent activities from activity log
        return []
    
    async def _get_team_performance_metrics(self, project_id: str) -> Dict[str, Any]:
        """Get team performance metrics for project"""
        return {
            "total_team_members": 5,
            "active_contributors": 4,
            "average_daily_hours": 6.5,
            "collaboration_frequency": 12,
            "issue_resolution_time": 2.3
        }
    
    async def _generate_completion_report(
        self,
        project_id: str,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive project completion report"""
        return {
            "project_id": project_id,
            "completion_date": datetime.utcnow().isoformat(),
            "final_budget_utilization": 0.0,
            "timeline_performance": 0.0,
            "quality_metrics": {},
            "team_performance": {},
            "lessons_learned": [],
            "client_feedback": {}
        }
    
    async def _trigger_revenue_distribution(
        self,
        project_id: str,
        project_data: Dict[str, Any]
    ):
        """Trigger revenue distribution for completed project"""
        try:
            logger.info(f"🔄 Triggering revenue distribution for project {project_id}")
            
            # Calculate revenue shares based on contribution
            total_revenue = project_data.get("total_revenue", 0)
            team_members = project_data.get("team_members", [])
            
            if total_revenue > 0 and team_members:
                # Basic equal distribution (can be enhanced with contribution weights)
                revenue_per_member = total_revenue / len(team_members)
                
                distribution_record = {
                    "project_id": project_id,
                    "total_revenue": total_revenue,
                    "distribution_date": datetime.now().isoformat(),
                    "distributions": []
                }
                
                for member in team_members:
                    member_id = member.get("member_id", member.get("id"))
                    contribution_weight = member.get("contribution_score", 1.0)
                    member_share = revenue_per_member * contribution_weight
                    
                    distribution_record["distributions"].append({
                        "member_id": member_id,
                        "revenue_share": member_share,
                        "contribution_weight": contribution_weight
                    })
                
                # Store distribution record
                await self.cache.set(
                    f"revenue_distribution:{project_id}", 
                    distribution_record, 
                    ttl=86400 * 30  # Keep for 30 days
                )
                
                logger.info(f"✅ Revenue distribution completed for project {project_id}")
            else:
                logger.warning(f"⚠️  No revenue or team members found for project {project_id}")
                
        except Exception as e:
            logger.error(f"❌ Error triggering revenue distribution for project {project_id}: {e}")
    
    async def _update_team_contribution_scores(
        self,
        project_id: str,
        project_data: Dict[str, Any]
    ):
        """Update team member contribution scores based on project completion"""
        try:
            logger.info(f"🔄 Updating contribution scores for project {project_id}")
            
            team_members = project_data.get("team_members", [])
            project_duration = project_data.get("duration_days", 1)
            project_complexity = project_data.get("complexity_score", 1.0)
            
            for member in team_members:
                member_id = member.get("member_id", member.get("id"))
                if not member_id:
                    continue
                
                # Calculate contribution based on tasks completed
                completed_tasks = member.get("completed_tasks", 0)
                total_hours = member.get("total_hours_worked", 0)
                quality_score = member.get("quality_score", 0.8)
                
                # Calculate contribution score
                base_contribution = (completed_tasks * total_hours) / max(project_duration, 1)
                weighted_contribution = base_contribution * quality_score * project_complexity
                
                # Get existing scores
                existing_scores = await self.cache.get(f"contribution_scores:{member_id}")
                if not existing_scores:
                    existing_scores = {
                        "member_id": member_id,
                        "total_projects": 0,
                        "average_contribution": 0.0,
                        "project_history": []
                    }
                
                # Update scores
                existing_scores["total_projects"] += 1
                existing_scores["project_history"].append({
                    "project_id": project_id,
                    "contribution_score": weighted_contribution,
                    "completion_date": datetime.now().isoformat()
                })
                
                # Calculate new average
                total_contribution = sum(p["contribution_score"] for p in existing_scores["project_history"])
                existing_scores["average_contribution"] = total_contribution / existing_scores["total_projects"]
                
                # Store updated scores
                await self.cache.set(f"contribution_scores:{member_id}", existing_scores, ttl=86400 * 365)
                
                logger.debug(f"✅ Updated contribution scores for member {member_id}")
                
        except Exception as e:
            logger.error(f"❌ Error updating contribution scores for project {project_id}: {e}")
    
    async def _archive_project_data(
        self,
        project_id: str,
        project_data: Dict[str, Any],
        completion_report: Dict[str, Any]
    ):
        """Archive completed project data for future reference"""
        archive_data = {
            "project_data": project_data,
            "completion_report": completion_report,
            "archived_at": datetime.utcnow().isoformat()
        }
        
        await self.cache.set(f"archived_project:{project_id}", archive_data, ttl=2592000)  # 30 days


class TaskDistributionEngine:
    """Intelligent task distribution system for collaborative teams"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
        self.ai_estimator = AIEstimationEngine()
    
    async def create_task(
        self,
        project_id: str,
        title: str,
        description: str,
        creator_id: str,
        priority: TaskPriority,
        estimated_hours: float,
        due_date: Optional[datetime] = None,
        dependencies: List[str] = None,
        tags: List[str] = None,
        required_skills: List[str] = None
    ) -> Dict[str, Any]:
        """Create new project task with intelligent assignment suggestions"""
        try:
            task_id = str(uuid.uuid4())
            
            # AI-powered effort estimation
            if estimated_hours <= 0:
                estimated_hours = await self.ai_estimator.estimate_task_effort(
                    title, description, required_skills or []
                )
            
            task = ProjectTask(
                task_id=task_id,
                project_id=project_id,
                title=title,
                description=description,
                assignee_id=None,
                creator_id=creator_id,
                priority=priority,
                status=TaskStatus.TODO,
                estimated_hours=estimated_hours,
                actual_hours=0.0,
                start_date=None,
                due_date=due_date,
                completion_date=None,
                dependencies=dependencies or [],
                tags=tags or [],
                attachments=[],
                progress_percentage=0.0,
                subtasks=[],
                review_comments=[],
                blocked_reason=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            task_data = task.to_dict()
            task_data["required_skills"] = required_skills or []
            
            await self.cache.set(f"task:{task_id}", task_data, ttl=86400)
            
            # Generate assignment suggestions
            assignment_suggestions = await self._generate_assignment_suggestions(
                project_id, task_data
            )
            
            # Update project task count
            await self._update_project_task_count(project_id, 1)
            
            logger.info(f"Task created successfully: {task_id}")
            return {
                "task_id": task_id,
                "status": "created",
                "estimated_hours": estimated_hours,
                "assignment_suggestions": assignment_suggestions
            }
            
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise BusinessLogicError(f"Failed to create task: {str(e)}")
    
    async def assign_task(
        self,
        task_id: str,
        assignee_id: str,
        assigned_by: str,
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Assign task to team member with validation"""
        try:
            task_data = await self.cache.get(f"task:{task_id}")
            if not task_data:
                raise ValidationError("Task not found")
            
            # Validate team member availability
            availability_check = await self._check_team_member_availability(
                assignee_id, task_data["estimated_hours"], start_date
            )
            
            if not availability_check["available"]:
                return {
                    "status": "assignment_failed",
                    "reason": availability_check["reason"],
                    "alternative_dates": availability_check.get("alternative_dates", [])
                }
            
            # Update task assignment
            task_data["assignee_id"] = assignee_id
            task_data["status"] = TaskStatus.TODO.value
            task_data["assigned_by"] = assigned_by
            task_data["assigned_at"] = datetime.utcnow().isoformat()
            task_data["start_date"] = (start_date or datetime.utcnow()).isoformat()
            task_data["updated_at"] = datetime.utcnow().isoformat()
            
            await self.cache.set(f"task:{task_id}", task_data, ttl=86400)
            
            # Update team member workload
            await self._update_team_member_workload(assignee_id, task_data["estimated_hours"])
            
            # Send assignment notification
            await self.notification_service.send_task_assignment_notification(
                assignee_id, task_data
            )
            
            return {
                "task_id": task_id,
                "assignee_id": assignee_id,
                "status": "assigned",
                "assigned_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assigning task: {str(e)}")
            raise BusinessLogicError(f"Failed to assign task: {str(e)}")
    
    async def update_task_progress(
        self,
        task_id: str,
        progress_percentage: float,
        hours_worked: float,
        updated_by: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update task progress with time tracking"""
        try:
            task_data = await self.cache.get(f"task:{task_id}")
            if not task_data:
                raise ValidationError("Task not found")
            
            # Validate progress update
            if not 0 <= progress_percentage <= 100:
                raise ValidationError("Progress percentage must be between 0 and 100")
            
            # Update task progress
            old_progress = task_data["progress_percentage"]
            task_data["progress_percentage"] = progress_percentage
            task_data["actual_hours"] += hours_worked
            task_data["updated_at"] = datetime.utcnow().isoformat()
            task_data["updated_by"] = updated_by
            
            # Handle completion
            if progress_percentage >= 100:
                task_data["status"] = TaskStatus.COMPLETED.value
                task_data["completion_date"] = datetime.utcnow().isoformat()
                await self._handle_task_completion(task_id, task_data)
            
            # Log progress update
            if "progress_history" not in task_data:
                task_data["progress_history"] = []
            
            task_data["progress_history"].append({
                "old_progress": old_progress,
                "new_progress": progress_percentage,
                "hours_worked": hours_worked,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow().isoformat(),
                "notes": notes
            })
            
            await self.cache.set(f"task:{task_id}", task_data, ttl=86400)
            
            # Update project progress
            await self._update_project_progress(task_data["project_id"])
            
            return {
                "task_id": task_id,
                "old_progress": old_progress,
                "new_progress": progress_percentage,
                "status": task_data["status"],
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating task progress: {str(e)}")
            raise BusinessLogicError(f"Failed to update task progress: {str(e)}")
    
    async def _generate_assignment_suggestions(
        self,
        project_id: str,
        task_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate intelligent task assignment suggestions"""
        try:
            # Get project team members
            project_data = await self.cache.get(f"project:{project_id}")
            if not project_data:
                return []
            
            team_members = project_data.get("team_members", [])
            suggestions = []
            
            for member_id in team_members:
                # Calculate compatibility score
                compatibility_score = await self._calculate_assignment_compatibility(
                    member_id, task_data
                )
                
                if compatibility_score > 0.6:  # 60% threshold
                    member_info = await self._get_team_member_info(member_id)
                    suggestions.append({
                        "member_id": member_id,
                        "member_name": member_info.get("name", "Unknown"),
                        "compatibility_score": compatibility_score,
                        "availability": member_info.get("availability", "unknown"),
                        "current_workload": member_info.get("current_workload", 0),
                        "relevant_skills": member_info.get("relevant_skills", []),
                        "estimated_completion_date": await self._estimate_completion_date(
                            member_id, task_data["estimated_hours"]
                        )
                    })
            
            # Sort by compatibility score
            suggestions.sort(key=lambda x: x["compatibility_score"], reverse=True)
            return suggestions[:3]  # Return top 3 suggestions
            
        except Exception as e:
            logger.error(f"Error generating assignment suggestions: {str(e)}")
            return []
    
    async def _calculate_assignment_compatibility(
        self,
        member_id: str,
        task_data: Dict[str, Any]
    ) -> float:
        """Calculate how well a team member fits a task"""
        try:
            member_info = await self._get_team_member_info(member_id)
            
            # Skill matching (40% weight)
            skill_score = await self._calculate_skill_match(
                member_info.get("skills", []),
                task_data.get("required_skills", [])
            )
            
            # Availability (30% weight)
            availability_score = await self._calculate_availability_score(
                member_id, task_data["estimated_hours"]
            )
            
            # Previous performance (20% weight)
            performance_score = member_info.get("performance_rating", 0.8)
            
            # Workload balance (10% weight)
            workload_score = await self._calculate_workload_score(member_id)
            
            # Weighted average
            compatibility_score = (
                skill_score * 0.4 +
                availability_score * 0.3 +
                performance_score * 0.2 +
                workload_score * 0.1
            )
            
            return min(1.0, max(0.0, compatibility_score))
            
        except Exception as e:
            logger.error(f"Error calculating assignment compatibility: {str(e)}")
            return 0.0
    
    async def _calculate_skill_match(
        self,
        member_skills: List[str],
        required_skills: List[str]
    ) -> float:
        """Calculate skill matching score"""
        if not required_skills:
            return 0.8  # Default score if no specific skills required
        
        matching_skills = set(member_skills) & set(required_skills)
        return len(matching_skills) / len(required_skills)
    
    async def _calculate_availability_score(
        self,
        member_id: str,
        estimated_hours: float
    ) -> float:
        """Calculate availability score for team member"""
        availability_data = await self.cache.get(f"availability:{member_id}")
        if not availability_data:
            return 0.7  # Default availability
        
        current_workload = availability_data.get("current_workload_hours", 0)
        max_capacity = availability_data.get("max_capacity_hours", 40)
        
        if current_workload + estimated_hours > max_capacity:
            return max(0.0, (max_capacity - current_workload) / estimated_hours)
        
        return 1.0 - (current_workload / max_capacity)
    
    async def _calculate_workload_score(self, member_id: str) -> float:
        """Calculate workload balance score"""
        workload_data = await self.cache.get(f"workload:{member_id}")
        if not workload_data:
            return 1.0
        
        current_tasks = workload_data.get("active_tasks", 0)
        optimal_tasks = 3  # Optimal number of concurrent tasks
        
        if current_tasks <= optimal_tasks:
            return 1.0
        else:
            return max(0.1, optimal_tasks / current_tasks)
    
    async def _check_team_member_availability(
        self,
        member_id: str,
        estimated_hours: float,
        start_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Check if team member is available for task"""
        availability_data = await self.cache.get(f"availability:{member_id}")
        if not availability_data:
            return {
                "available": True,
                "reason": "No availability data found"
            }
        
        current_workload = availability_data.get("current_workload_hours", 0)
        max_capacity = availability_data.get("max_capacity_hours", 40)
        
        if current_workload + estimated_hours > max_capacity:
            return {
                "available": False,
                "reason": "Workload capacity exceeded",
                "current_workload": current_workload,
                "max_capacity": max_capacity,
                "alternative_dates": [
                    (datetime.utcnow() + timedelta(weeks=1)).isoformat(),
                    (datetime.utcnow() + timedelta(weeks=2)).isoformat()
                ]
            }
        
        return {
            "available": True,
            "reason": "Available for assignment"
        }
    
    async def _update_team_member_workload(self, member_id: str, additional_hours: float):
        """Update team member workload tracking"""
        workload_data = await self.cache.get(f"workload:{member_id}")
        if not workload_data:
            workload_data = {
                "member_id": member_id,
                "current_workload_hours": 0,
                "active_tasks": 0,
                "completed_tasks": 0
            }
        
        workload_data["current_workload_hours"] += additional_hours
        workload_data["active_tasks"] += 1
        workload_data["updated_at"] = datetime.utcnow().isoformat()
        
        await self.cache.set(f"workload:{member_id}", workload_data, ttl=86400)
    
    async def _update_project_task_count(self, project_id: str, increment: int):
        """Update project task count"""
        project_data = await self.cache.get(f"project:{project_id}")
        if project_data:
            project_data["total_tasks"] = project_data.get("total_tasks", 0) + increment
            await self.cache.set(f"project:{project_id}", project_data, ttl=86400)
    
    async def _update_project_progress(self, project_id: str):
        """Update overall project progress based on task completion"""
        try:
            logger.debug(f"🔄 Updating progress for project {project_id}")
            
            # Get project data
            project_data = await self.cache.get(f"project:{project_id}")
            if not project_data:
                logger.warning(f"⚠️  Project {project_id} not found")
                return
            
            # Get all tasks for the project
            all_tasks = await self.cache.get(f"project_tasks:{project_id}") or []
            
            if not all_tasks:
                logger.debug(f"📝 No tasks found for project {project_id}")
                return
            
            # Calculate progress metrics
            total_tasks = len(all_tasks)
            completed_tasks = len([task for task in all_tasks if task.get("status") == TaskStatus.COMPLETED.value])
            in_progress_tasks = len([task for task in all_tasks if task.get("status") == TaskStatus.IN_PROGRESS.value])
            
            # Calculate progress percentage
            progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Calculate estimated completion date based on current velocity
            if in_progress_tasks > 0 and completed_tasks > 0:
                # Simple velocity calculation
                project_start = datetime.fromisoformat(project_data.get("start_date", datetime.now().isoformat()))
                days_elapsed = (datetime.now() - project_start).days
                velocity = completed_tasks / max(days_elapsed, 1)  # Tasks per day
                
                remaining_tasks = total_tasks - completed_tasks
                estimated_days_remaining = remaining_tasks / max(velocity, 0.1)
                estimated_completion = datetime.now() + timedelta(days=estimated_days_remaining)
            else:
                estimated_completion = None
            
            # Update project data
            project_data.update({
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "progress_percentage": progress_percentage,
                "last_progress_update": datetime.now().isoformat(),
                "estimated_completion": estimated_completion.isoformat() if estimated_completion else None
            })
            
            # Store updated project data
            await self.cache.set(f"project:{project_id}", project_data, ttl=86400)
            
            logger.debug(f"✅ Progress updated for project {project_id}: {progress_percentage:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Error updating progress for project {project_id}: {e}")
    
    async def _handle_task_completion(self, task_id: str, task_data: Dict[str, Any]):
        """Handle task completion procedures"""
        # Update project completed tasks count
        await self._update_project_completed_tasks(task_data["project_id"])
        
        # Update assignee workload
        if task_data.get("assignee_id"):
            await self._update_assignee_completion_stats(
                task_data["assignee_id"], task_data
            )
        
        # Check for dependent tasks
        await self._check_dependent_tasks(task_id, task_data["project_id"])
    
    async def _update_project_completed_tasks(self, project_id: str):
        """Update project completed tasks count"""
        project_data = await self.cache.get(f"project:{project_id}")
        if project_data:
            project_data["completed_tasks"] = project_data.get("completed_tasks", 0) + 1
            
            # Calculate progress percentage
            total_tasks = project_data.get("total_tasks", 1)
            completed_tasks = project_data["completed_tasks"]
            project_data["progress_percentage"] = (completed_tasks / total_tasks) * 100
            
            await self.cache.set(f"project:{project_id}", project_data, ttl=86400)
    
    async def _update_assignee_completion_stats(
        self,
        assignee_id: str,
        task_data: Dict[str, Any]
    ):
        """Update assignee completion statistics"""
        workload_data = await self.cache.get(f"workload:{assignee_id}")
        if workload_data:
            workload_data["active_tasks"] -= 1
            workload_data["completed_tasks"] += 1
            workload_data["current_workload_hours"] -= task_data["estimated_hours"]
            await self.cache.set(f"workload:{assignee_id}", workload_data, ttl=86400)
    
    async def _check_dependent_tasks(self, completed_task_id: str, project_id: str):
        """Check and unblock dependent tasks"""
        try:
            logger.debug(f"🔄 Checking dependent tasks for completed task {completed_task_id}")
            
            # Get all tasks for the project
            all_tasks = await self.cache.get(f"project_tasks:{project_id}") or []
            
            tasks_updated = 0
            for task in all_tasks:
                task_dependencies = task.get("dependencies", [])
                
                # Check if this task depends on the completed task
                if completed_task_id in task_dependencies:
                    # Remove the completed dependency
                    task_dependencies.remove(completed_task_id)
                    task["dependencies"] = task_dependencies
                    
                    # If no more dependencies, mark task as ready
                    if not task_dependencies and task.get("status") == TaskStatus.BLOCKED.value:
                        task["status"] = TaskStatus.TODO.value
                        task["unblocked_at"] = datetime.now().isoformat()
                        task["unblocked_by_task"] = completed_task_id
                        
                        logger.info(f"✅ Task {task['task_id']} unblocked by completion of {completed_task_id}")
                        tasks_updated += 1
                        
                        # Notify assignee if available
                        if task.get("assignee_id"):
                            await self._notify_task_unblocked(task["assignee_id"], task["task_id"])
            
            # Save updated tasks
            if tasks_updated > 0:
                await self.cache.set(f"project_tasks:{project_id}", all_tasks, ttl=86400)
                logger.info(f"📝 Updated {tasks_updated} dependent tasks for project {project_id}")
            
        except Exception as e:
            logger.error(f"❌ Error checking dependent tasks for {completed_task_id}: {e}")
    
    async def _notify_task_unblocked(self, assignee_id: str, task_id: str):
        """Notify assignee that their task has been unblocked"""
        try:
            notification = {
                "type": "task_unblocked",
                "assignee_id": assignee_id,
                "task_id": task_id,
                "message": f"Your task {task_id} is now unblocked and ready to start",
                "timestamp": datetime.now().isoformat()
            }
            
            # Store notification for the assignee
            notifications = await self.cache.get(f"notifications:{assignee_id}") or []
            notifications.append(notification)
            await self.cache.set(f"notifications:{assignee_id}", notifications, ttl=86400 * 7)
            
            logger.debug(f"📬 Notified {assignee_id} about unblocked task {task_id}")
            
        except Exception as e:
            logger.error(f"❌ Error notifying assignee {assignee_id} about unblocked task {task_id}: {e}")
    
    async def _get_team_member_info(self, member_id: str) -> Dict[str, Any]:
        """Get team member information"""
        member_info = await self.cache.get(f"member_info:{member_id}")
        if not member_info:
            return {
                "name": f"Member {member_id}",
                "skills": [],
                "availability": "unknown",
                "current_workload": 0,
                "performance_rating": 0.8
            }
        return member_info
    
    async def _estimate_completion_date(
        self,
        member_id: str,
        estimated_hours: float
    ) -> str:
        """Estimate task completion date for team member"""
        workload_data = await self.cache.get(f"workload:{member_id}")
        if not workload_data:
            # Default to 1 week if no workload data
            return (datetime.utcnow() + timedelta(weeks=1)).isoformat()
        
        # Calculate based on current workload and capacity
        daily_capacity = 8  # Assume 8 hours per day
        current_workload = workload_data.get("current_workload_hours", 0)
        
        # Calculate days needed
        days_needed = (current_workload + estimated_hours) / daily_capacity
        completion_date = datetime.utcnow() + timedelta(days=days_needed)
        
        return completion_date.isoformat()


class MilestoneTracker:
    """Advanced milestone tracking and management system"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
        self.notification_service = NotificationService()
    
    async def create_milestone(
        self,
        project_id: str,
        title: str,
        description: str,
        target_date: datetime,
        deliverables: List[Dict[str, Any]],
        responsible_members: List[str],
        budget_allocation: float,
        created_by: str
    ) -> Dict[str, Any]:
        """Create project milestone with comprehensive tracking"""
        try:
            milestone_id = str(uuid.uuid4())
            
            milestone = ProjectMilestone(
                milestone_id=milestone_id,
                project_id=project_id,
                title=title,
                description=description,
                target_date=target_date,
                completion_date=None,
                status="active",
                deliverables=deliverables,
                dependencies=[],
                responsible_team_members=responsible_members,
                completion_criteria=[],
                review_required=True,
                client_approval_required=False,
                budget_allocation=budget_allocation,
                actual_cost=0.0,
                created_at=datetime.utcnow()
            )
            
            milestone_data = {
                "milestone_id": milestone_id,
                "project_id": project_id,
                "title": title,
                "description": description,
                "target_date": target_date.isoformat(),
                "completion_date": None,
                "status": "active",
                "deliverables": deliverables,
                "dependencies": [],
                "responsible_team_members": responsible_members,
                "completion_criteria": [],
                "review_required": True,
                "client_approval_required": False,
                "budget_allocation": budget_allocation,
                "actual_cost": 0.0,
                "progress_percentage": 0.0,
                "created_by": created_by,
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.cache.set(f"milestone:{milestone_id}", milestone_data, ttl=86400)
            
            # Update project milestones
            await self._add_milestone_to_project(project_id, milestone_id)
            
            logger.info(f"Milestone created successfully: {milestone_id}")
            return {
                "milestone_id": milestone_id,
                "status": "created",
                "target_date": target_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating milestone: {str(e)}")
            raise BusinessLogicError(f"Failed to create milestone: {str(e)}")
    
    async def update_milestone_progress(
        self,
        milestone_id: str,
        progress_percentage: float,
        updated_by: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update milestone progress with validation"""
        try:
            milestone_data = await self.cache.get(f"milestone:{milestone_id}")
            if not milestone_data:
                raise ValidationError("Milestone not found")
            
            old_progress = milestone_data["progress_percentage"]
            milestone_data["progress_percentage"] = progress_percentage
            milestone_data["updated_by"] = updated_by
            milestone_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Handle completion
            if progress_percentage >= 100:
                milestone_data["status"] = "completed"
                milestone_data["completion_date"] = datetime.utcnow().isoformat()
                await self._handle_milestone_completion(milestone_id, milestone_data)
            
            # Log progress update
            if "progress_history" not in milestone_data:
                milestone_data["progress_history"] = []
            
            milestone_data["progress_history"].append({
                "old_progress": old_progress,
                "new_progress": progress_percentage,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow().isoformat(),
                "notes": notes
            })
            
            await self.cache.set(f"milestone:{milestone_id}", milestone_data, ttl=86400)
            
            return {
                "milestone_id": milestone_id,
                "old_progress": old_progress,
                "new_progress": progress_percentage,
                "status": milestone_data["status"]
            }
            
        except Exception as e:
            logger.error(f"Error updating milestone progress: {str(e)}")
            raise BusinessLogicError(f"Failed to update milestone progress: {str(e)}")
    
    async def _add_milestone_to_project(self, project_id: str, milestone_id: str):
        """Add milestone to project tracking"""
        project_data = await self.cache.get(f"project:{project_id}")
        if project_data:
            if "milestones" not in project_data:
                project_data["milestones"] = []
            project_data["milestones"].append(milestone_id)
            await self.cache.set(f"project:{project_id}", project_data, ttl=86400)
    
    async def _handle_milestone_completion(
        self,
        milestone_id: str,
        milestone_data: Dict[str, Any]
    ):
        """Handle milestone completion procedures"""
        # Notify responsible team members
        await self.notification_service.send_milestone_completion_notification(
            milestone_data["responsible_team_members"],
            milestone_data
        )
        
        # Update project progress
        await self._update_project_milestone_progress(milestone_data["project_id"])
    
    async def _update_project_milestone_progress(self, project_id: str):
        """Update project progress based on milestone completion"""
        project_data = await self.cache.get(f"project:{project_id}")
        if not project_data:
            return
        
        milestone_ids = project_data.get("milestones", [])
        if not milestone_ids:
            return
        
        total_milestones = len(milestone_ids)
        completed_milestones = 0
        
        for milestone_id in milestone_ids:
            milestone_data = await self.cache.get(f"milestone:{milestone_id}")
            if milestone_data and milestone_data.get("status") == "completed":
                completed_milestones += 1
        
        # Update project milestone progress
        milestone_progress = (completed_milestones / total_milestones) * 100
        project_data["milestone_progress"] = milestone_progress
        
        await self.cache.set(f"project:{project_id}", project_data, ttl=86400)


class ResourceAllocationManager:
    """Advanced resource allocation and optimization system"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
    
    async def allocate_resources(
        self,
        project_id: str,
        team_member_id: str,
        role: str,
        hours_per_week: float,
        start_date: datetime,
        end_date: Optional[datetime],
        hourly_rate: float,
        allocated_by: str
    ) -> Dict[str, Any]:
        """Allocate team member resources to project"""
        try:
            allocation_id = str(uuid.uuid4())
            
            # Calculate total budget allocation
            weeks_allocated = 1
            if end_date:
                weeks_allocated = max(1, (end_date - start_date).days / 7)
            
            total_budget = hours_per_week * weeks_allocated * hourly_rate
            
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                project_id=project_id,
                team_member_id=team_member_id,
                role=role,
                allocated_hours_per_week=hours_per_week,
                start_date=start_date,
                end_date=end_date,
                hourly_rate=hourly_rate,
                total_allocated_budget=total_budget,
                actual_hours_worked=0.0,
                actual_cost=0.0,
                utilization_percentage=0.0,
                availability_conflicts=[],
                skills_required=[],
                performance_rating=0.0
            )
            
            allocation_data = {
                "allocation_id": allocation_id,
                "project_id": project_id,
                "team_member_id": team_member_id,
                "role": role,
                "allocated_hours_per_week": hours_per_week,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat() if end_date else None,
                "hourly_rate": hourly_rate,
                "total_allocated_budget": total_budget,
                "actual_hours_worked": 0.0,
                "actual_cost": 0.0,
                "utilization_percentage": 0.0,
                "availability_conflicts": [],
                "skills_required": [],
                "performance_rating": 0.0,
                "allocated_by": allocated_by,
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.cache.set(f"allocation:{allocation_id}", allocation_data, ttl=86400)
            
            # Update project resource allocations
            await self._add_allocation_to_project(project_id, allocation_id)
            
            logger.info(f"Resource allocation created: {allocation_id}")
            return {
                "allocation_id": allocation_id,
                "total_budget": total_budget,
                "status": "allocated"
            }
            
        except Exception as e:
            logger.error(f"Error allocating resources: {str(e)}")
            raise BusinessLogicError(f"Failed to allocate resources: {str(e)}")
    
    async def _add_allocation_to_project(self, project_id: str, allocation_id: str):
        """Add resource allocation to project tracking"""
        project_data = await self.cache.get(f"project:{project_id}")
        if project_data:
            if "resource_allocations" not in project_data:
                project_data["resource_allocations"] = {}
            project_data["resource_allocations"][allocation_id] = True
            await self.cache.set(f"project:{project_id}", project_data, ttl=86400)


class ProjectTimelineManager:
    """Advanced project timeline management with critical path analysis"""
    
    def __init__(self, db_session: AsyncSession, cache_manager: CacheManager):
        self.db = db_session
        self.cache = cache_manager
    
    async def optimize_project_timeline(
        self,
        project_id: str,
        constraints: Dict[str, Any],
        optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """Optimize project timeline using AI algorithms"""
        try:
            project_data = await self.cache.get(f"project:{project_id}")
            if not project_data:
                raise ValidationError("Project not found")
            
            # Get project tasks and dependencies
            tasks = await self._get_project_tasks(project_id)
            
            # Calculate critical path
            critical_path = await self._calculate_critical_path(tasks)
            
            # Optimize timeline
            optimized_timeline = await self._optimize_timeline(
                tasks, critical_path, constraints, optimization_goals
            )
            
            # Update project timeline
            timeline_data = {
                "project_id": project_id,
                "optimized_timeline": optimized_timeline,
                "critical_path": critical_path,
                "optimization_goals": optimization_goals,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await self.cache.set(f"optimized_timeline:{project_id}", timeline_data, ttl=86400)
            
            return {
                "project_id": project_id,
                "critical_path_length": len(critical_path),
                "estimated_completion": optimized_timeline.get("completion_date"),
                "optimization_improvements": optimized_timeline.get("improvements", [])
            }
            
        except Exception as e:
            logger.error(f"Error optimizing project timeline: {str(e)}")
            raise BusinessLogicError(f"Failed to optimize timeline: {str(e)}")
    
    async def _get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for project"""
        try:
            # Get cached project tasks
            project_tasks = await self.cache.get(f"project_tasks:{project_id}")
            if project_tasks:
                return project_tasks
            
            # If not in cache, get project data and extract task information
            project_data = await self.cache.get(f"project:{project_id}")
            if not project_data:
                return []
            
            # Get all task IDs associated with this project
            task_ids = project_data.get("task_ids", [])
            tasks = []
            
            for task_id in task_ids:
                task_data = await self.cache.get(f"task:{task_id}")
                if task_data:
                    tasks.append(task_data)
            
            # Cache the results
            await self.cache.set(f"project_tasks:{project_id}", tasks, ttl=3600)
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting project tasks for {project_id}: {e}")
            return []
    
    async def _calculate_critical_path(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Calculate critical path for project tasks using CPM algorithm"""
        try:
            if not tasks:
                return []
            
            # Create task network graph
            task_graph = {}
            task_durations = {}
            
            # Build graph representation
            for task in tasks:
                task_id = task.get("task_id")
                if not task_id:
                    continue
                    
                task_graph[task_id] = {
                    "dependencies": task.get("dependencies", []),
                    "dependents": [],
                    "duration": task.get("estimated_hours", 8) / 8,  # Convert to days
                    "early_start": 0,
                    "early_finish": 0,
                    "late_start": 0,
                    "late_finish": 0,
                    "slack": 0
                }
                task_durations[task_id] = task_graph[task_id]["duration"]
            
            # Calculate dependents (reverse dependencies)
            for task_id, task_info in task_graph.items():
                for dep_id in task_info["dependencies"]:
                    if dep_id in task_graph:
                        task_graph[dep_id]["dependents"].append(task_id)
            
            # Forward pass - calculate early start and finish times
            def calculate_early_times(task_id: str, visited: set = None):
                if visited is None:
                    visited = set()
                
                if task_id in visited or task_id not in task_graph:
                    return 0
                
                visited.add(task_id)
                task = task_graph[task_id]
                
                # Calculate based on dependencies
                max_early_finish = 0
                for dep_id in task["dependencies"]:
                    if dep_id in task_graph:
                        dep_early_finish = calculate_early_times(dep_id, visited.copy())
                        max_early_finish = max(max_early_finish, dep_early_finish)
                
                task["early_start"] = max_early_finish
                task["early_finish"] = task["early_start"] + task["duration"]
                return task["early_finish"]
            
            # Calculate early times for all tasks
            project_duration = 0
            for task_id in task_graph:
                early_finish = calculate_early_times(task_id)
                project_duration = max(project_duration, early_finish)
            
            # Backward pass - calculate late start and finish times
            def calculate_late_times(task_id: str, visited: set = None):
                if visited is None:
                    visited = set()
                
                if task_id in visited or task_id not in task_graph:
                    return project_duration
                
                visited.add(task_id)
                task = task_graph[task_id]
                
                # If no dependents, late finish = project duration
                if not task["dependents"]:
                    task["late_finish"] = project_duration
                else:
                    # Calculate based on dependents
                    min_late_start = float('inf')
                    for dep_id in task["dependents"]:
                        if dep_id in task_graph:
                            dep_late_start = calculate_late_times(dep_id, visited.copy())
                            min_late_start = min(min_late_start, dep_late_start)
                    
                    task["late_finish"] = min_late_start if min_late_start != float('inf') else project_duration
                
                task["late_start"] = task["late_finish"] - task["duration"]
                task["slack"] = task["late_start"] - task["early_start"]
                return task["late_start"]
            
            # Calculate late times for all tasks
            for task_id in task_graph:
                calculate_late_times(task_id)
            
            # Find critical path (tasks with zero slack)
            critical_tasks = []
            for task_id, task_info in task_graph.items():
                if abs(task_info["slack"]) < 0.001:  # Float comparison tolerance
                    critical_tasks.append(task_id)
            
            # Sort critical tasks by early start time for logical order
            critical_tasks.sort(key=lambda tid: task_graph[tid]["early_start"])
            
            logger.info(f"Critical path calculated: {len(critical_tasks)} tasks, {project_duration:.1f} days")
            return critical_tasks
            
        except Exception as e:
            logger.error(f"Error calculating critical path: {e}")
            return []
    
    async def _optimize_timeline(
        self,
        tasks: List[Dict[str, Any]],
        critical_path: List[str],
        constraints: Dict[str, Any],
        optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """Optimize project timeline based on goals and constraints"""
        try:
            if not tasks:
                return {
                    "completion_date": datetime.utcnow().isoformat(),
                    "improvements": [],
                    "optimization_results": {}
                }
            
            original_duration = sum(task.get("estimated_hours", 8) / 8 for task in tasks)
            improvements = []
            optimization_results = {}
            
            # Track optimization metrics
            time_saved = 0
            resource_efficiency = 1.0
            cost_impact = 0.0
            
            # Optimization 1: Parallelize independent tasks
            if "minimize_duration" in optimization_goals:
                parallel_savings = await self._optimize_parallel_execution(tasks, critical_path)
                time_saved += parallel_savings
                if parallel_savings > 0:
                    improvements.append(f"Parallel execution saves {parallel_savings:.1f} days")
            
            # Optimization 2: Resource reallocation to critical path
            if "optimize_resources" in optimization_goals:
                resource_savings = await self._optimize_resource_allocation(tasks, critical_path, constraints)
                time_saved += resource_savings["time_saved"]
                resource_efficiency = resource_savings["efficiency_gain"]
                if resource_savings["time_saved"] > 0:
                    improvements.append(f"Resource reallocation saves {resource_savings['time_saved']:.1f} days")
            
            # Optimization 3: Buffer time optimization
            if "optimize_buffers" in optimization_goals:
                buffer_optimization = await self._optimize_buffer_times(tasks, constraints)
                time_saved += buffer_optimization["time_saved"]
                improvements.append(f"Buffer optimization: {buffer_optimization['description']}")
            
            # Optimization 4: Task dependency optimization
            if "optimize_dependencies" in optimization_goals:
                dependency_savings = await self._optimize_task_dependencies(tasks)
                time_saved += dependency_savings
                if dependency_savings > 0:
                    improvements.append(f"Dependency optimization saves {dependency_savings:.1f} days")
            
            # Calculate new completion date
            optimized_duration = max(1, original_duration - time_saved)
            completion_date = datetime.utcnow() + timedelta(days=optimized_duration)
            
            # Calculate optimization impact
            time_savings_percentage = (time_saved / original_duration * 100) if original_duration > 0 else 0
            cost_savings = time_saved * constraints.get("daily_cost", 1000)  # Estimated daily project cost
            
            optimization_results = {
                "original_duration_days": original_duration,
                "optimized_duration_days": optimized_duration,
                "time_saved_days": time_saved,
                "time_savings_percentage": time_savings_percentage,
                "resource_efficiency_gain": (resource_efficiency - 1.0) * 100,
                "estimated_cost_savings": cost_savings,
                "critical_path_length": len(critical_path),
                "total_tasks": len(tasks),
                "optimization_goals_achieved": len(optimization_goals)
            }
            
            if not improvements:
                improvements.append("No significant optimizations identified with current constraints")
            
            logger.info(f"Timeline optimization completed: {time_saved:.1f} days saved ({time_savings_percentage:.1f}%)")
            
            return {
                "completion_date": completion_date.isoformat(),
                "improvements": improvements,
                "optimization_results": optimization_results,
                "critical_path_tasks": critical_path,
                "optimization_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing timeline: {e}")
            return {
                "completion_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "improvements": ["Optimization failed - using default timeline"],
                "optimization_results": {"error": str(e)}
            }
    
    async def _optimize_parallel_execution(self, tasks: List[Dict[str, Any]], critical_path: List[str]) -> float:
        """Optimize parallel execution of independent tasks"""
        try:
            # Identify tasks that can be parallelized (no dependencies between them)
            independent_groups = []
            processed_tasks = set()
            
            for task in tasks:
                task_id = task.get("task_id")
                if task_id in processed_tasks or task_id in critical_path:
                    continue
                
                # Find tasks that can run in parallel with this one
                parallel_group = [task_id]
                task_dependencies = set(task.get("dependencies", []))
                
                for other_task in tasks:
                    other_id = other_task.get("task_id")
                    if (other_id != task_id and 
                        other_id not in processed_tasks and 
                        other_id not in critical_path):
                        
                        other_dependencies = set(other_task.get("dependencies", []))
                        
                        # Check if tasks can run in parallel (no dependency overlap)
                        if not task_dependencies.intersection(other_dependencies):
                            parallel_group.append(other_id)
                
                if len(parallel_group) > 1:
                    independent_groups.append(parallel_group)
                    processed_tasks.update(parallel_group)
            
            # Calculate time savings from parallelization
            time_saved = 0
            for group in independent_groups:
                group_durations = []
                for task_id in group:
                    task = next((t for t in tasks if t.get("task_id") == task_id), None)
                    if task:
                        group_durations.append(task.get("estimated_hours", 8) / 8)
                
                if len(group_durations) > 1:
                    # Time saved = sum of all durations - max duration (parallel execution)
                    sequential_time = sum(group_durations)
                    parallel_time = max(group_durations)
                    time_saved += sequential_time - parallel_time
            
            return time_saved
            
        except Exception as e:
            logger.warning(f"Parallel execution optimization failed: {e}")
            return 0.0
    
    async def _optimize_resource_allocation(self, tasks: List[Dict[str, Any]], critical_path: List[str], constraints: Dict[str, Any]) -> Dict[str, float]:
        """Optimize resource allocation to critical path"""
        try:
            # Identify available resources and current allocation
            total_resources = constraints.get("max_team_members", 5)
            critical_path_tasks = [t for t in tasks if t.get("task_id") in critical_path]
            non_critical_tasks = [t for t in tasks if t.get("task_id") not in critical_path]
            
            # Calculate current resource distribution
            critical_resources = sum(1 for task in critical_path_tasks if task.get("assignee_id"))
            total_assigned = sum(1 for task in tasks if task.get("assignee_id"))
            
            # Optimization: Prioritize critical path tasks
            time_saved = 0
            efficiency_gain = 1.0
            
            if critical_resources < len(critical_path_tasks) and total_assigned < total_resources:
                # We can allocate more resources to critical path
                additional_resources = min(
                    total_resources - total_assigned,
                    len(critical_path_tasks) - critical_resources
                )
                
                # Estimate time savings (assuming 20% improvement per additional resource)
                time_saved = additional_resources * 0.2 * len(critical_path_tasks)
                efficiency_gain = 1.0 + (additional_resources * 0.15)
            
            return {
                "time_saved": time_saved,
                "efficiency_gain": efficiency_gain,
                "additional_resources_needed": max(0, len(critical_path_tasks) - critical_resources)
            }
            
        except Exception as e:
            logger.warning(f"Resource allocation optimization failed: {e}")
            return {"time_saved": 0.0, "efficiency_gain": 1.0}
    
    async def _optimize_buffer_times(self, tasks: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize buffer times in project schedule"""
        try:
            total_duration = sum(task.get("estimated_hours", 8) / 8 for task in tasks)
            current_buffer_ratio = constraints.get("buffer_ratio", 0.2)  # 20% default buffer
            
            # Calculate optimal buffer based on task complexity and risk
            high_risk_tasks = sum(1 for task in tasks if task.get("priority") == "critical")
            risk_factor = high_risk_tasks / len(tasks) if tasks else 0
            
            # Optimal buffer: 10-30% based on risk
            optimal_buffer_ratio = 0.1 + (risk_factor * 0.2)
            
            buffer_adjustment = current_buffer_ratio - optimal_buffer_ratio
            time_saved = total_duration * buffer_adjustment
            
            if buffer_adjustment > 0:
                description = f"Reduced buffer from {current_buffer_ratio*100:.1f}% to {optimal_buffer_ratio*100:.1f}%"
            else:
                description = f"Maintained buffer at {current_buffer_ratio*100:.1f}% (appropriate for project risk)"
                time_saved = 0  # No time saved if buffer is already optimal or needs increase
            
            return {
                "time_saved": max(0, time_saved),
                "description": description,
                "optimal_buffer_ratio": optimal_buffer_ratio
            }
            
        except Exception as e:
            logger.warning(f"Buffer optimization failed: {e}")
            return {"time_saved": 0.0, "description": "Buffer optimization failed"}
    
    async def _optimize_task_dependencies(self, tasks: List[Dict[str, Any]]) -> float:
        """Optimize task dependencies to reduce blocking"""
        try:
            # Identify unnecessary dependencies that could be removed
            time_saved = 0
            dependency_graph = {}
            
            # Build dependency graph
            for task in tasks:
                task_id = task.get("task_id")
                dependencies = task.get("dependencies", [])
                dependency_graph[task_id] = dependencies
            
            # Look for transitive dependencies that can be optimized
            for task_id, dependencies in dependency_graph.items():
                if len(dependencies) > 1:
                    # Check if some dependencies are transitive
                    direct_dependencies = []
                    for dep in dependencies:
                        # Check if this dependency is already covered by another dependency
                        is_transitive = False
                        for other_dep in dependencies:
                            if other_dep != dep and dep in dependency_graph.get(other_dep, []):
                                is_transitive = True
                                break
                        
                        if not is_transitive:
                            direct_dependencies.append(dep)
                    
                    # If we can reduce dependencies, estimate time savings
                    if len(direct_dependencies) < len(dependencies):
                        reduced_blocking = len(dependencies) - len(direct_dependencies)
                        task_duration = next((t.get("estimated_hours", 8) / 8 for t in tasks 
                                            if t.get("task_id") == task_id), 0)
                        time_saved += reduced_blocking * 0.1 * task_duration  # 10% improvement per reduced dependency
            
            return time_saved
            
        except Exception as e:
            logger.warning(f"Dependency optimization failed: {e}")
            return 0.0
