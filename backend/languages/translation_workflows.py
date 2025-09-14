"""Translation Workflows - Professional Translation Workflow Management Engine
================================================================================
Module: backend/languages/translation_workflows.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Translation Workflow Engine - Professional Integration and QA
Responsibility: Professional translator integration, review workflows, version control
Technologies: Python, Workflow Management, Version Control, Collaboration Tools
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Content submission → Workflow routing → Translator assignment → 
Translation process → Quality review → Approval → Version control → Delivery
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Translation workflow statuses"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowType(Enum):
    """Types of translation workflows"""
    STANDARD = "standard"           # Standard translation workflow
    EXPRESS = "express"            # Fast-track workflow
    PREMIUM = "premium"            # High-quality with multiple reviews
    COMMUNITY = "community"        # Community-driven translation
    AUTOMATED = "automated"        # Fully automated workflow
    HYBRID = "hybrid"             # AI + Human hybrid workflow


class TranslatorTier(Enum):
    """Translator qualification tiers"""
    JUNIOR = "junior"              # Entry level translators
    PROFESSIONAL = "professional"  # Experienced translators
    EXPERT = "expert"              # Domain experts
    NATIVE = "native"              # Native speakers
    CERTIFIED = "certified"        # Certified translators


class ReviewType(Enum):
    """Types of translation reviews"""
    LINGUISTIC = "linguistic"      # Language quality review
    TECHNICAL = "technical"        # Technical accuracy review
    CULTURAL = "cultural"          # Cultural appropriateness review
    LEGAL = "legal"               # Legal compliance review
    FINAL = "final"               # Final quality check


class PriorityLevel(Enum):
    """Priority levels for translation jobs"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass
class TranslatorProfile:
    """Translator profile information"""
    translator_id: str
    name: str
    email: str
    tier: TranslatorTier
    languages: List[str]
    specializations: List[str]
    rating: float
    completed_jobs: int
    active_jobs: int
    availability: bool
    timezone: str
    rate_per_word: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """Individual step in translation workflow"""
    step_id: str
    step_type: str
    assigned_to: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[timedelta] = None
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TranslationJob:
    """Translation job definition"""
    job_id: str
    source_content: str
    source_language: str
    target_language: str
    domain: str
    word_count: int
    priority: PriorityLevel
    deadline: datetime
    workflow_type: WorkflowType
    client_id: str
    created_at: datetime
    status: WorkflowStatus = WorkflowStatus.PENDING
    assigned_translator: Optional[str] = None
    assigned_reviewer: Optional[str] = None
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TranslationVersion:
    """Version of translation with history"""
    version_id: str
    job_id: str
    content: str
    translator_id: str
    created_at: datetime
    version_number: int
    change_summary: str
    quality_score: Optional[float] = None
    reviewer_notes: str = ""
    is_final: bool = False


@dataclass
class ReviewFeedback:
    """Review feedback for translations"""
    review_id: str
    job_id: str
    version_id: str
    reviewer_id: str
    review_type: ReviewType
    score: float
    comments: str
    suggestions: List[str]
    approved: bool
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowTemplate:
    """Template defining workflow steps"""
    template_id: str
    name: str
    workflow_type: WorkflowType
    steps: List[Dict[str, Any]]
    requirements: Dict[str, Any]
    estimated_duration: timedelta
    quality_gates: List[str]


@dataclass
class CollaborationSession:
    """Real-time collaboration session"""
    session_id: str
    job_id: str
    participants: List[str]
    started_at: datetime
    last_activity: datetime
    shared_content: str
    comments: List[Dict[str, Any]] = field(default_factory=list)
    changes_log: List[Dict[str, Any]] = field(default_factory=list)


class TranslationWorkflowEngine:
    """
    Professional translation workflow management engine supporting
    complex translation processes with human translators and AI integration
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize translation workflow engine"""
        self.config = config or {}
        
        # Storage for workflow data
        self.translation_jobs: Dict[str, TranslationJob] = {}
        self.translators: Dict[str, TranslatorProfile] = {}
        self.workflow_templates: Dict[str, WorkflowTemplate] = {}
        self.translation_versions: Dict[str, List[TranslationVersion]] = {}
        self.review_feedback: Dict[str, List[ReviewFeedback]] = {}
        self.collaboration_sessions: Dict[str, CollaborationSession] = {}
        
        # Workflow statistics
        self.workflow_stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "active_jobs": 0,
            "average_completion_time": timedelta(hours=24),
            "quality_scores": []
        }
        
        # Load default workflow templates
        self._initialize_workflow_templates()
        
        # Load sample translators (would come from database in production)
        self._load_sample_translators()
        
        logger.info("TranslationWorkflowEngine initialized")
    
    async def create_translation_job(self, source_content: str, source_language: str,
                                   target_language: str, domain: str,
                                   workflow_type: WorkflowType = WorkflowType.STANDARD,
                                   priority: PriorityLevel = PriorityLevel.NORMAL,
                                   deadline: Optional[datetime] = None,
                                   client_id: str = "default") -> TranslationJob:
        """
        Create a new translation job
        
        Args:
            source_content: Content to translate
            source_language: Source language code
            target_language: Target language code
            domain: Domain/specialization
            workflow_type: Type of workflow to use
            priority: Priority level
            deadline: Completion deadline
            client_id: Client identifier
            
        Returns:
            Created TranslationJob
        """
        job_id = str(uuid.uuid4())
        word_count = len(source_content.split())
        
        if deadline is None:
            # Estimate deadline based on word count and workflow type
            hours_per_1000_words = {
                WorkflowType.EXPRESS: 4,
                WorkflowType.STANDARD: 8,
                WorkflowType.PREMIUM: 16,
                WorkflowType.HYBRID: 6
            }
            
            estimated_hours = (word_count / 1000) * hours_per_1000_words.get(workflow_type, 8)
            deadline = datetime.now(timezone.utc) + timedelta(hours=estimated_hours)
        
        job = TranslationJob(
            job_id=job_id,
            source_content=source_content,
            source_language=source_language,
            target_language=target_language,
            domain=domain,
            word_count=word_count,
            priority=priority,
            deadline=deadline,
            workflow_type=workflow_type,
            client_id=client_id,
            created_at=datetime.now(timezone.utc)
        )
        
        self.translation_jobs[job_id] = job
        self.workflow_stats["total_jobs"] += 1
        self.workflow_stats["active_jobs"] += 1
        
        # Initialize workflow
        await self._initialize_job_workflow(job)
        
        logger.info(f"Translation job created: {job_id} ({source_language} -> {target_language})")
        
        return job
    
    async def assign_translator(self, job_id: str, 
                              translator_id: Optional[str] = None) -> bool:
        """
        Assign translator to a job (automatic if translator_id not provided)
        
        Args:
            job_id: Job identifier
            translator_id: Specific translator to assign (optional)
            
        Returns:
            Success status
        """
        if job_id not in self.translation_jobs:
            return False
        
        job = self.translation_jobs[job_id]
        
        if translator_id is None:
            # Auto-assign best available translator
            translator_id = await self._find_best_translator(job)
        
        if translator_id and translator_id in self.translators:
            translator = self.translators[translator_id]
            
            # Check availability and qualifications
            if (translator.availability and 
                job.target_language in translator.languages and
                translator.active_jobs < 5):  # Max concurrent jobs
                
                job.assigned_translator = translator_id
                job.status = WorkflowStatus.ASSIGNED
                translator.active_jobs += 1
                
                # Update workflow step
                await self._update_workflow_step(job_id, "translation", "assigned", translator_id)
                
                logger.info(f"Translator {translator_id} assigned to job {job_id}")
                return True
        
        return False
    
    async def submit_translation(self, job_id: str, translator_id: str, 
                               translated_content: str, 
                               change_summary: str = "") -> str:
        """
        Submit translation for review
        
        Args:
            job_id: Job identifier
            translator_id: Translator identifier
            translated_content: Translated content
            change_summary: Summary of changes made
            
        Returns:
            Version ID of submitted translation
        """
        if job_id not in self.translation_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.translation_jobs[job_id]
        
        if job.assigned_translator != translator_id:
            raise ValueError("Translator not assigned to this job")
        
        # Create new version
        version_id = str(uuid.uuid4())
        version_number = len(self.translation_versions.get(job_id, [])) + 1
        
        version = TranslationVersion(
            version_id=version_id,
            job_id=job_id,
            content=translated_content,
            translator_id=translator_id,
            created_at=datetime.now(timezone.utc),
            version_number=version_number,
            change_summary=change_summary
        )
        
        if job_id not in self.translation_versions:
            self.translation_versions[job_id] = []
        
        self.translation_versions[job_id].append(version)
        
        # Update job status
        job.status = WorkflowStatus.UNDER_REVIEW
        
        # Assign reviewer
        await self._assign_reviewer(job)
        
        # Update workflow step
        await self._update_workflow_step(job_id, "review", "pending")
        
        logger.info(f"Translation submitted for job {job_id}, version {version_number}")
        
        return version_id
    
    async def submit_review(self, job_id: str, version_id: str, reviewer_id: str,
                          review_type: ReviewType, score: float, comments: str,
                          suggestions: List[str], approved: bool) -> str:
        """
        Submit review feedback
        
        Args:
            job_id: Job identifier
            version_id: Version being reviewed
            reviewer_id: Reviewer identifier
            review_type: Type of review
            score: Quality score (0.0-1.0)
            comments: Review comments
            suggestions: Improvement suggestions
            approved: Whether translation is approved
            
        Returns:
            Review ID
        """
        review_id = str(uuid.uuid4())
        
        review = ReviewFeedback(
            review_id=review_id,
            job_id=job_id,
            version_id=version_id,
            reviewer_id=reviewer_id,
            review_type=review_type,
            score=score,
            comments=comments,
            suggestions=suggestions,
            approved=approved,
            created_at=datetime.now(timezone.utc)
        )
        
        if job_id not in self.review_feedback:
            self.review_feedback[job_id] = []
        
        self.review_feedback[job_id].append(review)
        
        # Update job status based on review
        job = self.translation_jobs[job_id]
        
        if approved and score >= 0.8:
            job.status = WorkflowStatus.APPROVED
            await self._finalize_translation(job_id, version_id)
        elif not approved or score < 0.6:
            job.status = WorkflowStatus.REJECTED
            await self._request_revision(job_id, version_id, suggestions)
        
        logger.info(f"Review submitted for job {job_id}: {score:.2f} ({'approved' if approved else 'rejected'})")
        
        return review_id
    
    async def start_collaboration_session(self, job_id: str, 
                                        participants: List[str]) -> CollaborationSession:
        """
        Start real-time collaboration session
        
        Args:
            job_id: Job identifier
            participants: List of participant IDs
            
        Returns:
            CollaborationSession object
        """
        session_id = str(uuid.uuid4())
        
        # Get current content for collaboration
        job = self.translation_jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        current_content = job.source_content
        versions = self.translation_versions.get(job_id, [])
        if versions:
            current_content = versions[-1].content
        
        session = CollaborationSession(
            session_id=session_id,
            job_id=job_id,
            participants=participants,
            started_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            shared_content=current_content
        )
        
        self.collaboration_sessions[session_id] = session
        
        logger.info(f"Collaboration session started for job {job_id} with {len(participants)} participants")
        
        return session
    
    async def add_collaboration_comment(self, session_id: str, user_id: str, 
                                      comment: str, position: Optional[int] = None) -> bool:
        """
        Add comment to collaboration session
        
        Args:
            session_id: Session identifier
            user_id: User making comment
            comment: Comment text
            position: Position in text (optional)
            
        Returns:
            Success status
        """
        if session_id not in self.collaboration_sessions:
            return False
        
        session = self.collaboration_sessions[session_id]
        
        comment_data = {
            "comment_id": str(uuid.uuid4()),
            "user_id": user_id,
            "comment": comment,
            "position": position,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        session.comments.append(comment_data)
        session.last_activity = datetime.now(timezone.utc)
        
        return True
    
    async def track_collaboration_change(self, session_id: str, user_id: str,
                                       change_type: str, change_data: Dict[str, Any]) -> bool:
        """
        Track changes in collaboration session
        
        Args:
            session_id: Session identifier
            user_id: User making change
            change_type: Type of change
            change_data: Change details
            
        Returns:
            Success status
        """
        if session_id not in self.collaboration_sessions:
            return False
        
        session = self.collaboration_sessions[session_id]
        
        change_log = {
            "change_id": str(uuid.uuid4()),
            "user_id": user_id,
            "change_type": change_type,
            "change_data": change_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        session.changes_log.append(change_log)
        session.last_activity = datetime.now(timezone.utc)
        
        return True
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get comprehensive job status
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
        """
        if job_id not in self.translation_jobs:
            return {"error": "Job not found"}
        
        job = self.translation_jobs[job_id]
        versions = self.translation_versions.get(job_id, [])
        reviews = self.review_feedback.get(job_id, [])
        
        # Calculate progress
        template = self.workflow_templates.get(job.workflow_type.value)
        total_steps = len(template.steps) if template else 5
        completed_steps = len(job.completed_steps)
        progress_percentage = (completed_steps / total_steps) * 100
        
        return {
            "job_id": job_id,
            "status": job.status.value,
            "progress_percentage": progress_percentage,
            "assigned_translator": job.assigned_translator,
            "assigned_reviewer": job.assigned_reviewer,
            "current_step": job.current_step,
            "completed_steps": job.completed_steps,
            "versions_count": len(versions),
            "reviews_count": len(reviews),
            "deadline": job.deadline.isoformat(),
            "created_at": job.created_at.isoformat(),
            "word_count": job.word_count,
            "domain": job.domain,
            "priority": job.priority.value,
            "workflow_type": job.workflow_type.value
        }
    
    async def get_workflow_analytics(self) -> Dict[str, Any]:
        """
        Get workflow analytics and performance metrics
        
        Returns:
            Analytics data
        """
        # Calculate metrics
        total_jobs = len(self.translation_jobs)
        completed_jobs = len([j for j in self.translation_jobs.values() 
                             if j.status == WorkflowStatus.COMPLETED])
        active_jobs = len([j for j in self.translation_jobs.values() 
                          if j.status in [WorkflowStatus.ASSIGNED, WorkflowStatus.IN_PROGRESS, 
                                         WorkflowStatus.UNDER_REVIEW]])
        
        # Calculate average completion time
        completed_times = []
        for job in self.translation_jobs.values():
            if job.status == WorkflowStatus.COMPLETED:
                # This would be calculated from actual completion timestamps
                completion_time = timedelta(hours=24)  # Placeholder
                completed_times.append(completion_time.total_seconds())
        
        avg_completion_time = (sum(completed_times) / len(completed_times) 
                              if completed_times else 0) / 3600  # Convert to hours
        
        # Calculate quality metrics
        all_reviews = []
        for reviews in self.review_feedback.values():
            all_reviews.extend(reviews)
        
        avg_quality_score = (sum(r.score for r in all_reviews) / len(all_reviews) 
                           if all_reviews else 0.0)
        
        # Status distribution
        status_distribution = {}
        for status in WorkflowStatus:
            count = len([j for j in self.translation_jobs.values() if j.status == status])
            status_distribution[status.value] = count
        
        # Language pair statistics
        language_pairs = {}
        for job in self.translation_jobs.values():
            pair = f"{job.source_language}-{job.target_language}"
            language_pairs[pair] = language_pairs.get(pair, 0) + 1
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "active_jobs": active_jobs,
            "completion_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            "average_completion_time_hours": avg_completion_time,
            "average_quality_score": avg_quality_score,
            "status_distribution": status_distribution,
            "top_language_pairs": sorted(language_pairs.items(), 
                                       key=lambda x: x[1], reverse=True)[:10],
            "active_translators": len([t for t in self.translators.values() if t.active_jobs > 0]),
            "total_translators": len(self.translators),
            "active_collaboration_sessions": len(self.collaboration_sessions)
        }
    
    # Private helper methods
    
    async def _initialize_job_workflow(self, job -> None: TranslationJob) -> None:
        """Initialize workflow for a job"""
        template = self.workflow_templates.get(job.workflow_type.value)
        if template:
            job.current_step = template.steps[0]["name"]
            job.metadata["workflow_template"] = template.template_id
    
    async def _find_best_translator(self, job: TranslationJob) -> Optional[str]:
        """Find the best available translator for a job"""
        candidates = []
        
        for translator_id, translator in self.translators.items():
            if (translator.availability and 
                job.target_language in translator.languages and
                translator.active_jobs < 5):
                
                # Calculate score based on specialization, rating, and availability
                score = translator.rating
                
                if job.domain in translator.specializations:
                    score += 0.5
                
                # Prefer less busy translators
                score -= translator.active_jobs * 0.1
                
                candidates.append((translator_id, score))
        
        if candidates:
            # Return translator with highest score
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    async def _assign_reviewer(self, job -> None: TranslationJob) -> None:
        """Assign reviewer to a job"""
        # Find available reviewer with appropriate qualifications
        for translator_id, translator in self.translators.items():
            if (translator_id != job.assigned_translator and
                translator.tier in [TranslatorTier.PROFESSIONAL, TranslatorTier.EXPERT, 
                                   TranslatorTier.CERTIFIED] and
                job.target_language in translator.languages):
                
                job.assigned_reviewer = translator_id
                break
    
    async def _update_workflow_step(self, job_id -> None: str, step_name -> None: str, 
                                  status -> None: str, assigned_to -> None: Optional[str] = None) -> None:
        """Update workflow step status"""
        job = self.translation_jobs[job_id]
        
        if status == "completed" and step_name not in job.completed_steps:
            job.completed_steps.append(step_name)
        
        job.current_step = step_name
        
        # Update job status based on workflow progress
        if step_name == "translation" and status == "assigned":
            job.status = WorkflowStatus.IN_PROGRESS
        elif step_name == "review" and status == "pending":
            job.status = WorkflowStatus.UNDER_REVIEW
    
    async def _finalize_translation(self, job_id -> None: str, version_id -> None: str) -> None:
        """Finalize approved translation"""
        job = self.translation_jobs[job_id]
        versions = self.translation_versions.get(job_id, [])
        
        # Mark version as final
        for version in versions:
            if version.version_id == version_id:
                version.is_final = True
                break
        
        # Update job status
        job.status = WorkflowStatus.COMPLETED
        
        # Update translator statistics
        if job.assigned_translator:
            translator = self.translators[job.assigned_translator]
            translator.completed_jobs += 1
            translator.active_jobs -= 1
        
        # Update workflow statistics
        self.workflow_stats["completed_jobs"] += 1
        self.workflow_stats["active_jobs"] -= 1
        
        logger.info(f"Translation finalized for job {job_id}")
    
    async def _request_revision(self, job_id -> None: str, version_id -> None: str, suggestions -> None: List[str]) -> None:
        """Request revision from translator"""
        job = self.translation_jobs[job_id]
        job.status = WorkflowStatus.IN_PROGRESS
        
        # Add revision request to job metadata
        if "revision_requests" not in job.metadata:
            job.metadata["revision_requests"] = []
        
        job.metadata["revision_requests"].append({
            "version_id": version_id,
            "suggestions": suggestions,
            "requested_at": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Revision requested for job {job_id}")
    
    def _initialize_workflow_templates(self) -> None:
        """Initialize default workflow templates"""
        # Standard workflow template
        self.workflow_templates["standard"] = WorkflowTemplate(
            template_id="standard",
            name="Standard Translation Workflow",
            workflow_type=WorkflowType.STANDARD,
            steps=[
                {"name": "assignment", "type": "automatic", "duration_hours": 1},
                {"name": "translation", "type": "human", "duration_hours": 8},
                {"name": "review", "type": "human", "duration_hours": 2},
                {"name": "approval", "type": "automatic", "duration_hours": 1},
                {"name": "delivery", "type": "automatic", "duration_hours": 1}
            ],
            requirements={
                "translator_tier": ["professional", "expert", "certified"],
                "reviewer_required": True
            },
            estimated_duration=timedelta(hours=13),
            quality_gates=["translation_complete", "review_approved"]
        )
        
        # Express workflow template
        self.workflow_templates["express"] = WorkflowTemplate(
            template_id="express",
            name="Express Translation Workflow",
            workflow_type=WorkflowType.EXPRESS,
            steps=[
                {"name": "assignment", "type": "automatic", "duration_hours": 0.5},
                {"name": "translation", "type": "human", "duration_hours": 3},
                {"name": "quick_review", "type": "human", "duration_hours": 0.5},
                {"name": "delivery", "type": "automatic", "duration_hours": 0.5}
            ],
            requirements={
                "translator_tier": ["expert", "certified"],
                "reviewer_required": True
            },
            estimated_duration=timedelta(hours=4.5),
            quality_gates=["translation_complete"]
        )
        
        # Premium workflow template
        self.workflow_templates["premium"] = WorkflowTemplate(
            template_id="premium",
            name="Premium Translation Workflow",
            workflow_type=WorkflowType.PREMIUM,
            steps=[
                {"name": "assignment", "type": "automatic", "duration_hours": 2},
                {"name": "translation", "type": "human", "duration_hours": 12},
                {"name": "linguistic_review", "type": "human", "duration_hours": 3},
                {"name": "technical_review", "type": "human", "duration_hours": 2},
                {"name": "final_review", "type": "human", "duration_hours": 1},
                {"name": "approval", "type": "manual", "duration_hours": 2},
                {"name": "delivery", "type": "automatic", "duration_hours": 1}
            ],
            requirements={
                "translator_tier": ["expert", "certified"],
                "multiple_reviewers": True,
                "final_approval": True
            },
            estimated_duration=timedelta(hours=23),
            quality_gates=["translation_complete", "all_reviews_approved", "final_approval"]
        )
    
    def _load_sample_translators(self) -> None:
        """Load sample translator profiles"""
        sample_translators = [
            {
                "translator_id": "trans_001",
                "name": "Maria García",
                "email": "maria@example.com",
                "tier": TranslatorTier.EXPERT,
                "languages": ["en", "es", "pt"],
                "specializations": ["legal", "medical", "technical"],
                "rating": 4.8,
                "completed_jobs": 250,
                "active_jobs": 2,
                "availability": True,
                "timezone": "CET",
                "rate_per_word": 0.15
            },
            {
                "translator_id": "trans_002",
                "name": "Hiroshi Tanaka",
                "email": "hiroshi@example.com",
                "tier": TranslatorTier.CERTIFIED,
                "languages": ["en", "ja"],
                "specializations": ["technical", "automotive", "electronics"],
                "rating": 4.9,
                "completed_jobs": 180,
                "active_jobs": 1,
                "availability": True,
                "timezone": "JST",
                "rate_per_word": 0.20
            },
            {
                "translator_id": "trans_003",
                "name": "Sophie Dubois",
                "email": "sophie@example.com",
                "tier": TranslatorTier.PROFESSIONAL,
                "languages": ["en", "fr", "de"],
                "specializations": ["marketing", "fashion", "tourism"],
                "rating": 4.6,
                "completed_jobs": 320,
                "active_jobs": 3,
                "availability": True,
                "timezone": "CET",
                "rate_per_word": 0.12
            },
            {
                "translator_id": "trans_004",
                "name": "Ahmed Al-Rashid",
                "email": "ahmed@example.com",
                "tier": TranslatorTier.EXPERT,
                "languages": ["en", "ar", "fr"],
                "specializations": ["legal", "finance", "government"],
                "rating": 4.7,
                "completed_jobs": 200,
                "active_jobs": 2,
                "availability": True,
                "timezone": "GST",
                "rate_per_word": 0.18
            }
        ]
        
        for translator_data in sample_translators:
            profile = TranslatorProfile(**translator_data)
            self.translators[profile.translator_id] = profile
    
    async def get_workflow_capabilities(self) -> Dict[str, Any]:
        """Get workflow engine capabilities"""
        return {
            "workflow_types": [wt.value for wt in WorkflowType],
            "translator_tiers": [tt.value for tt in TranslatorTier],
            "review_types": [rt.value for rt in ReviewType],
            "priority_levels": [pl.value for pl in PriorityLevel],
            "workflow_statuses": [ws.value for ws in WorkflowStatus],
            "available_templates": list(self.workflow_templates.keys()),
            "registered_translators": len(self.translators),
            "active_jobs": self.workflow_stats["active_jobs"],
            "completed_jobs": self.workflow_stats["completed_jobs"],
            "collaboration_sessions": len(self.collaboration_sessions),
            "version_control": True,
            "real_time_collaboration": True,
            "automated_assignment": True,
            "quality_assurance": True
        }