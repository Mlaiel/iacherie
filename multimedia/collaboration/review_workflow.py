"""
Ainflue Platform - Multimedia Collaboration - Review Workflow System
Professional content review and feedback management for collaborative multimedia projects

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """Review status enumeration"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CHANGES = "needs_changes"
    CANCELLED = "cancelled"


class ReviewType(Enum):
    """Review type enumeration"""
    CONTENT_QUALITY = "content_quality"
    TECHNICAL_REVIEW = "technical_review"
    CREATIVE_REVIEW = "creative_review"
    COMPLIANCE_REVIEW = "compliance_review"
    FINAL_APPROVAL = "final_approval"


class ReviewPriority(Enum):
    """Review priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass
class ReviewComment:
    """Review comment data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reviewer_id: str = ""
    content: str = ""
    timestamp: Optional[float] = None
    position: Optional[Dict[str, float]] = None  # For timeline/spatial comments
    category: str = "general"
    severity: str = "info"  # info, warning, error, critical
    resolved: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()


@dataclass
class ReviewRequest:
    """Review request data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    reviewer_id: str = ""
    requester_id: str = ""
    review_type: ReviewType = ReviewType.CONTENT_QUALITY
    priority: ReviewPriority = ReviewPriority.NORMAL
    status: ReviewStatus = ReviewStatus.PENDING
    deadline: Optional[float] = None
    created_at: Optional[float] = None
    completed_at: Optional[float] = None
    comments: List[ReviewComment] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().timestamp()


class ReviewWorkflowManager:
    """Professional review workflow management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize review workflow manager"""
        self.config = config or {}
        self.reviews: Dict[str, ReviewRequest] = {}
        self.workflows: Dict[str, List[ReviewType]] = {}
        self.reviewers: Dict[str, Dict[str, Any]] = {}
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.notifications_enabled = self.config.get('notifications', True)
        
        # Initialize default workflows
        self._initialize_default_workflows()
        
    def _initialize_default_workflows(self):
        """Initialize default review workflows"""
        self.workflows.update({
            'standard': [
                ReviewType.CONTENT_QUALITY,
                ReviewType.TECHNICAL_REVIEW,
                ReviewType.FINAL_APPROVAL
            ],
            'creative': [
                ReviewType.CREATIVE_REVIEW,
                ReviewType.CONTENT_QUALITY,
                ReviewType.FINAL_APPROVAL
            ],
            'compliance': [
                ReviewType.COMPLIANCE_REVIEW,
                ReviewType.CONTENT_QUALITY,
                ReviewType.TECHNICAL_REVIEW,
                ReviewType.FINAL_APPROVAL
            ],
            'express': [
                ReviewType.CONTENT_QUALITY,
                ReviewType.FINAL_APPROVAL
            ]
        })
    
    async def create_review_request(
        self,
        content_id: str,
        reviewer_id: str,
        requester_id: str,
        review_type: ReviewType = ReviewType.CONTENT_QUALITY,
        priority: ReviewPriority = ReviewPriority.NORMAL,
        deadline_hours: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReviewRequest:
        """Create a new review request"""
        try:
            deadline = None
            if deadline_hours:
                deadline = (datetime.now() + timedelta(hours=deadline_hours)).timestamp()
            
            review = ReviewRequest(
                content_id=content_id,
                reviewer_id=reviewer_id,
                requester_id=requester_id,
                review_type=review_type,
                priority=priority,
                deadline=deadline,
                metadata=metadata or {}
            )
            
            self.reviews[review.id] = review
            
            # Send notification to reviewer
            if self.notifications_enabled:
                await self._send_review_notification(review, 'new_request')
            
            logger.info(f"Created review request {review.id} for content {content_id}")
            return review
            
        except Exception as e:
            logger.error(f"Error creating review request: {e}")
            raise
    
    async def start_workflow(
        self,
        content_id: str,
        workflow_type: str = 'standard',
        requester_id: str = "",
        priority: ReviewPriority = ReviewPriority.NORMAL,
        reviewers: Optional[Dict[ReviewType, str]] = None
    ) -> List[ReviewRequest]:
        """Start a complete review workflow"""
        try:
            if workflow_type not in self.workflows:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
            
            workflow_steps = self.workflows[workflow_type]
            created_reviews = []
            
            for step in workflow_steps:
                reviewer_id = ""
                if reviewers and step in reviewers:
                    reviewer_id = reviewers[step]
                else:
                    reviewer_id = await self._assign_reviewer(step)
                
                review = await self.create_review_request(
                    content_id=content_id,
                    reviewer_id=reviewer_id,
                    requester_id=requester_id,
                    review_type=step,
                    priority=priority
                )
                
                created_reviews.append(review)
            
            logger.info(f"Started {workflow_type} workflow for content {content_id}")
            return created_reviews
            
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            raise
    
    async def submit_review(
        self,
        review_id: str,
        reviewer_id: str,
        status: ReviewStatus,
        comments: List[ReviewComment],
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Submit a review with feedback"""
        try:
            if review_id not in self.reviews:
                raise ValueError(f"Review {review_id} not found")
            
            review = self.reviews[review_id]
            
            if review.reviewer_id != reviewer_id:
                raise ValueError("Unauthorized reviewer")
            
            if review.status != ReviewStatus.IN_REVIEW and review.status != ReviewStatus.PENDING:
                raise ValueError(f"Cannot submit review in status {review.status.value}")
            
            review.status = status
            review.comments.extend(comments)
            review.completed_at = datetime.now().timestamp()
            
            if attachments:
                review.attachments.extend(attachments)
            
            # Send notification to requester
            if self.notifications_enabled:
                await self._send_review_notification(review, 'review_completed')
            
            logger.info(f"Review {review_id} submitted with status {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting review: {e}")
            raise
    
    async def add_comment(
        self,
        review_id: str,
        reviewer_id: str,
        content: str,
        position: Optional[Dict[str, float]] = None,
        category: str = "general",
        severity: str = "info"
    ) -> ReviewComment:
        """Add a comment to a review"""
        try:
            if review_id not in self.reviews:
                raise ValueError(f"Review {review_id} not found")
            
            review = self.reviews[review_id]
            
            comment = ReviewComment(
                reviewer_id=reviewer_id,
                content=content,
                position=position,
                category=category,
                severity=severity
            )
            
            review.comments.append(comment)
            
            # Send notification about new comment
            if self.notifications_enabled:
                await self._send_review_notification(review, 'new_comment')
            
            logger.info(f"Added comment to review {review_id}")
            return comment
            
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            raise
    
    async def resolve_comment(
        self,
        review_id: str,
        comment_id: str,
        resolver_id: str
    ) -> bool:
        """Mark a comment as resolved"""
        try:
            if review_id not in self.reviews:
                raise ValueError(f"Review {review_id} not found")
            
            review = self.reviews[review_id]
            
            for comment in review.comments:
                if comment.id == comment_id:
                    comment.resolved = True
                    logger.info(f"Comment {comment_id} resolved by {resolver_id}")
                    return True
            
            raise ValueError(f"Comment {comment_id} not found")
            
        except Exception as e:
            logger.error(f"Error resolving comment: {e}")
            raise
    
    async def get_reviews_by_content(
        self,
        content_id: str,
        status_filter: Optional[ReviewStatus] = None
    ) -> List[ReviewRequest]:
        """Get all reviews for specific content"""
        try:
            reviews = [
                review for review in self.reviews.values()
                if review.content_id == content_id
            ]
            
            if status_filter:
                reviews = [r for r in reviews if r.status == status_filter]
            
            return sorted(reviews, key=lambda x: x.created_at or 0)
            
        except Exception as e:
            logger.error(f"Error getting reviews by content: {e}")
            raise
    
    async def get_reviews_by_reviewer(
        self,
        reviewer_id: str,
        status_filter: Optional[ReviewStatus] = None
    ) -> List[ReviewRequest]:
        """Get all reviews assigned to a reviewer"""
        try:
            reviews = [
                review for review in self.reviews.values()
                if review.reviewer_id == reviewer_id
            ]
            
            if status_filter:
                reviews = [r for r in reviews if r.status == status_filter]
            
            return sorted(reviews, key=lambda x: x.created_at or 0)
            
        except Exception as e:
            logger.error(f"Error getting reviews by reviewer: {e}")
            raise
    
    async def get_overdue_reviews(self) -> List[ReviewRequest]:
        """Get all overdue reviews"""
        try:
            current_time = datetime.now().timestamp()
            overdue_reviews = [
                review for review in self.reviews.values()
                if (review.deadline and 
                    review.deadline < current_time and 
                    review.status in [ReviewStatus.PENDING, ReviewStatus.IN_REVIEW])
            ]
            
            return sorted(overdue_reviews, key=lambda x: x.deadline or 0)
            
        except Exception as e:
            logger.error(f"Error getting overdue reviews: {e}")
            raise
    
    async def escalate_review(
        self,
        review_id: str,
        escalation_reason: str,
        escalated_by: str
    ) -> bool:
        """Escalate a review to higher priority"""
        try:
            if review_id not in self.reviews:
                raise ValueError(f"Review {review_id} not found")
            
            review = self.reviews[review_id]
            
            # Increase priority
            if review.priority == ReviewPriority.LOW:
                review.priority = ReviewPriority.NORMAL
            elif review.priority == ReviewPriority.NORMAL:
                review.priority = ReviewPriority.HIGH
            elif review.priority == ReviewPriority.HIGH:
                review.priority = ReviewPriority.URGENT
            elif review.priority == ReviewPriority.URGENT:
                review.priority = ReviewPriority.CRITICAL
            
            # Add escalation metadata
            review.metadata['escalation'] = {
                'reason': escalation_reason,
                'escalated_by': escalated_by,
                'escalated_at': datetime.now().timestamp()
            }
            
            # Send escalation notification
            if self.notifications_enabled:
                await self._send_review_notification(review, 'escalated')
            
            logger.info(f"Review {review_id} escalated to {review.priority.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error escalating review: {e}")
            raise
    
    async def _assign_reviewer(self, review_type: ReviewType) -> str:
        """Auto-assign reviewer based on type and availability"""
        try:
            # This would typically integrate with user management system
            # For now, return a placeholder that can be configured
            return self.config.get('default_reviewers', {}).get(review_type.value, 'auto-assigned')
            
        except Exception as e:
            logger.error(f"Error assigning reviewer: {e}")
            return 'unassigned'
    
    async def _send_review_notification(
        self,
        review: ReviewRequest,
        notification_type: str
    ):
        """Send review-related notifications"""
        try:
            # This would integrate with notification system
            notification_data = {
                'type': notification_type,
                'review_id': review.id,
                'content_id': review.content_id,
                'reviewer_id': review.reviewer_id,
                'requester_id': review.requester_id,
                'priority': review.priority.value,
                'timestamp': datetime.now().timestamp()
            }
            
            logger.info(f"Sending {notification_type} notification for review {review.id}")
            # TODO: Implement actual notification sending
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    async def get_review_statistics(
        self,
        reviewer_id: Optional[str] = None,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """Get review statistics"""
        try:
            cutoff_time = (datetime.now() - timedelta(days=time_range_days)).timestamp()
            
            relevant_reviews = [
                review for review in self.reviews.values()
                if (review.created_at or 0) >= cutoff_time
            ]
            
            if reviewer_id:
                relevant_reviews = [r for r in relevant_reviews if r.reviewer_id == reviewer_id]
            
            stats = {
                'total_reviews': len(relevant_reviews),
                'by_status': {},
                'by_type': {},
                'by_priority': {},
                'average_completion_time': 0,
                'overdue_count': 0
            }
            
            completion_times = []
            
            for review in relevant_reviews:
                # Count by status
                status = review.status.value
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Count by type
                review_type = review.review_type.value
                stats['by_type'][review_type] = stats['by_type'].get(review_type, 0) + 1
                
                # Count by priority
                priority = review.priority.value
                stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
                
                # Calculate completion time
                if review.completed_at and review.created_at:
                    completion_time = review.completed_at - review.created_at
                    completion_times.append(completion_time)
                
                # Count overdue
                if (review.deadline and 
                    review.deadline < datetime.now().timestamp() and 
                    review.status in [ReviewStatus.PENDING, ReviewStatus.IN_REVIEW]):
                    stats['overdue_count'] += 1
            
            if completion_times:
                stats['average_completion_time'] = sum(completion_times) / len(completion_times)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting review statistics: {e}")
            raise


# Export main classes
__all__ = [
    'ReviewWorkflowManager',
    'ReviewRequest',
    'ReviewComment',
    'ReviewStatus',
    'ReviewType',
    'ReviewPriority'
]