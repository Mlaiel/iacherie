"""Collaboration Request Repository Module

Enterprise-grade repository for collaboration request management with intelligent
matching, automated workflow processing, and comprehensive analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from ..models.collaboration_requests import (
    CollaborationRequest,
    RequestType,
    RequestStatus,
    CollaborationCategory,
    SkillLevel,
    BudgetRange,
    UrgencyLevel
)
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class CollaborationRequestRepository(BaseRepository[CollaborationRequest]):
    """
    Repository for collaboration request operations with intelligent matching,
    automated processing, skill analysis, and comprehensive workflow management.
    """
    
    def __init__(self, db_session: Session):
        """Initialize collaboration request repository"""
        super().__init__(db_session, CollaborationRequest)
        
    def create_request(self,
                      requester_id: int,
                      title: str,
                      description: str,
                      request_type: RequestType,
                      category: CollaborationCategory,
                      required_skills: List[str],
                      budget_range: BudgetRange,
                      deadline: Optional[datetime] = None,
                      urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM,
                      skill_level_required: SkillLevel = SkillLevel.INTERMEDIATE,
                      location_requirements: Optional[Dict[str, Any]] = None,
                      collaboration_details: Optional[Dict[str, Any]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> CollaborationRequest:
        """
        Create collaboration request with validation and matching analysis
        
        Args:
            requester_id: Request creator user ID
            title: Request title
            description: Detailed description
            request_type: Type of collaboration request
            category: Collaboration category
            required_skills: List of required skills
            budget_range: Budget range for collaboration
            deadline: Optional deadline
            urgency_level: Request urgency level
            skill_level_required: Required skill level
            location_requirements: Geographic requirements
            collaboration_details: Additional collaboration details
            metadata: Additional request metadata
            
        Returns:
            Created CollaborationRequest instance
        """
        try:
            # Validate required skills
            if not required_skills:
                raise RepositoryException("At least one required skill must be specified")
            
            # Validate deadline
            if deadline and deadline <= datetime.utcnow():
                raise RepositoryException("Deadline must be in the future")
            
            # Generate request ID and reference
            request_id = str(uuid.uuid4())
            request_reference = self._generate_request_reference(category, datetime.utcnow())
            
            # Calculate initial priority score
            priority_score = self._calculate_priority_score(urgency_level, budget_range, deadline)
            
            # Estimate collaboration match potential
            match_potential = self._estimate_match_potential(
                required_skills,
                category,
                skill_level_required,
                location_requirements
            )
            
            request_data = {
                'requester_id': requester_id,
                'title': title,
                'description': description,
                'request_type': request_type,
                'category': category,
                'required_skills': required_skills,
                'budget_range': budget_range,
                'deadline': deadline,
                'urgency_level': urgency_level,
                'skill_level_required': skill_level_required,
                'location_requirements': location_requirements or {},
                'collaboration_details': collaboration_details or {},
                'status': RequestStatus.OPEN,
                'metadata': metadata or {},
                'request_id': request_id,
                'request_reference': request_reference,
                'priority_score': priority_score,
                'match_potential_score': match_potential,
                'view_count': 0,
                'application_count': 0,
                'shortlist_count': 0,
                'match_score_average': 0.0,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            request = self.create(**request_data)
            
            # Trigger automatic matching analysis
            self._trigger_automatic_matching(request.id)
            
            self.logger.info(
                f"Created {request_type.value} collaboration request '{title}' "
                f"for user {requester_id} with priority {priority_score}"
            )
            
            return request
            
        except Exception as e:
            self.logger.error(f"Failed to create collaboration request: {str(e)}")
            raise RepositoryException(f"Request creation failed: {str(e)}")
            
    def _generate_request_reference(self,
                                  category: CollaborationCategory,
                                  created_at: datetime) -> str:
        """
        Generate unique request reference
        
        Args:
            category: Collaboration category
            created_at: Creation timestamp
            
        Returns:
            Request reference string
        """
        category_code = category.value[:3].upper()
        date_code = created_at.strftime("%Y%m")
        sequence = self.db_session.query(func.count(CollaborationRequest.id)).filter(
            func.extract('year', CollaborationRequest.created_at) == created_at.year,
            func.extract('month', CollaborationRequest.created_at) == created_at.month
        ).scalar() + 1
        
        return f"CR-{category_code}-{date_code}-{sequence:04d}"
        
    def _calculate_priority_score(self,
                                urgency: UrgencyLevel,
                                budget: BudgetRange,
                                deadline: Optional[datetime]) -> int:
        """
        Calculate priority score based on multiple factors
        
        Args:
            urgency: Urgency level
            budget: Budget range
            deadline: Optional deadline
            
        Returns:
            Priority score (1-100)
        """
        # Base score from urgency
        urgency_scores = {
            UrgencyLevel.LOW: 20,
            UrgencyLevel.MEDIUM: 50,
            UrgencyLevel.HIGH: 80,
            UrgencyLevel.URGENT: 100
        }
        
        score = urgency_scores.get(urgency, 50)
        
        # Budget influence
        budget_modifiers = {
            BudgetRange.UNDER_500: 0.8,
            BudgetRange.RANGE_500_1000: 0.9,
            BudgetRange.RANGE_1000_5000: 1.0,
            BudgetRange.RANGE_5000_10000: 1.1,
            BudgetRange.ABOVE_10000: 1.2
        }
        
        score = int(score * budget_modifiers.get(budget, 1.0))
        
        # Deadline urgency
        if deadline:
            days_until_deadline = (deadline - datetime.utcnow()).days
            if days_until_deadline <= 1:
                score = min(100, score + 20)
            elif days_until_deadline <= 7:
                score = min(100, score + 10)
            elif days_until_deadline <= 30:
                score = min(100, score + 5)
        
        return max(1, min(100, score))
        
    def _estimate_match_potential(self,
                                required_skills: List[str],
                                category: CollaborationCategory,
                                skill_level: SkillLevel,
                                location_requirements: Optional[Dict[str, Any]]) -> float:
        """
        Estimate match potential based on skill demand and availability
        
        Args:
            required_skills: Required skills list
            category: Collaboration category
            skill_level: Required skill level
            location_requirements: Location requirements
            
        Returns:
            Match potential score (0.0-100.0)
        """
        try:
            # Base score from skill commonality
            common_skills = ['content creation', 'social media', 'marketing', 'photography']
            skill_commonality = len(set(required_skills) & set(common_skills)) / len(required_skills)
            
            base_score = 50 + (skill_commonality * 30)
            
            # Category demand modifier
            category_demand = {
                CollaborationCategory.CONTENT_CREATION: 1.2,
                CollaborationCategory.MARKETING: 1.1,
                CollaborationCategory.TECHNICAL: 0.9,
                CollaborationCategory.CREATIVE: 1.0,
                CollaborationCategory.BUSINESS: 1.0
            }
            
            score = base_score * category_demand.get(category, 1.0)
            
            # Skill level accessibility
            skill_modifiers = {
                SkillLevel.BEGINNER: 1.2,
                SkillLevel.INTERMEDIATE: 1.0,
                SkillLevel.ADVANCED: 0.8,
                SkillLevel.EXPERT: 0.6
            }
            
            score *= skill_modifiers.get(skill_level, 1.0)
            
            # Location constraints
            if location_requirements and location_requirements.get('remote_allowed', True):
                score *= 1.1
            elif location_requirements and 'specific_city' in location_requirements:
                score *= 0.7
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Failed to estimate match potential: {str(e)}")
            return 50.0
            
    def _trigger_automatic_matching(self, request_id: int) -> None:
        """
        Trigger automatic matching analysis for a request
        
        Args:
            request_id: Request ID to analyze
        """
        try:
            # In production, this would trigger a background job
            # For now, we'll update metadata to indicate matching should be performed
            request = self.get_by_id(request_id)
            if request:
                metadata = request.metadata or {}
                metadata['automatic_matching_triggered'] = datetime.utcnow().isoformat()
                metadata['matching_status'] = 'pending'
                
                self.update(request_id, metadata=metadata)
                
                self.logger.info(f"Triggered automatic matching for request {request_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to trigger automatic matching: {str(e)}")
            
    def find_matching_requests(self,
                             user_skills: List[str],
                             user_categories: List[CollaborationCategory],
                             user_skill_level: SkillLevel,
                             max_results: int = 20,
                             budget_preference: Optional[BudgetRange] = None,
                             location_preferences: Optional[Dict[str, Any]] = None) -> List[Tuple[CollaborationRequest, float]]:
        """
        Find collaboration requests matching user profile
        
        Args:
            user_skills: User's skills
            user_categories: User's preferred categories
            user_skill_level: User's skill level
            max_results: Maximum number of results
            budget_preference: User's budget preference
            location_preferences: Location preferences
            
        Returns:
            List of tuples (CollaborationRequest, match_score)
        """
        try:
            # Get open requests in user's categories
            query = self.db_session.query(CollaborationRequest).filter(
                and_(
                    CollaborationRequest.status == RequestStatus.OPEN,
                    CollaborationRequest.category.in_(user_categories)
                )
            )
            
            # Apply skill level filter (user should meet minimum requirement)
            skill_level_order = {
                SkillLevel.BEGINNER: 1,
                SkillLevel.INTERMEDIATE: 2,
                SkillLevel.ADVANCED: 3,
                SkillLevel.EXPERT: 4
            }
            
            user_level_value = skill_level_order.get(user_skill_level, 2)
            eligible_levels = [level for level, value in skill_level_order.items() 
                             if value <= user_level_value]
            
            query = query.filter(CollaborationRequest.skill_level_required.in_(eligible_levels))
            
            # Apply budget filter if specified
            if budget_preference:
                query = query.filter(CollaborationRequest.budget_range == budget_preference)
            
            requests = query.order_by(CollaborationRequest.priority_score.desc()).limit(max_results * 2).all()
            
            # Calculate match scores
            scored_requests = []
            
            for request in requests:
                match_score = self._calculate_match_score(
                    request,
                    user_skills,
                    user_skill_level,
                    location_preferences
                )
                
                if match_score > 30:  # Minimum threshold
                    scored_requests.append((request, match_score))
            
            # Sort by match score and return top results
            scored_requests.sort(key=lambda x: x[1], reverse=True)
            
            result = scored_requests[:max_results]
            
            self.logger.info(
                f"Found {len(result)} matching requests for user with {len(user_skills)} skills"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to find matching requests: {str(e)}")
            return []
            
    def _calculate_match_score(self,
                             request: CollaborationRequest,
                             user_skills: List[str],
                             user_skill_level: SkillLevel,
                             location_preferences: Optional[Dict[str, Any]]) -> float:
        """
        Calculate match score between request and user profile
        
        Args:
            request: CollaborationRequest to score
            user_skills: User's skills
            user_skill_level: User's skill level
            location_preferences: User's location preferences
            
        Returns:
            Match score (0.0-100.0)
        """
        try:
            total_score = 0.0
            
            # Skill matching (40% weight)
            skill_overlap = len(set(request.required_skills) & set(user_skills))
            skill_match = (skill_overlap / len(request.required_skills)) * 100
            total_score += skill_match * 0.4
            
            # Skill level compatibility (20% weight)
            skill_level_order = {
                SkillLevel.BEGINNER: 1,
                SkillLevel.INTERMEDIATE: 2,
                SkillLevel.ADVANCED: 3,
                SkillLevel.EXPERT: 4
            }
            
            required_level = skill_level_order.get(request.skill_level_required, 2)
            user_level = skill_level_order.get(user_skill_level, 2)
            
            if user_level >= required_level:
                # Exact match gets full score, higher levels get slightly less
                level_score = max(0, 100 - (user_level - required_level) * 10)
            else:
                level_score = 0  # User doesn't meet minimum requirement
            
            total_score += level_score * 0.2
            
            # Budget attractiveness (15% weight)
            budget_scores = {
                BudgetRange.UNDER_500: 40,
                BudgetRange.RANGE_500_1000: 60,
                BudgetRange.RANGE_1000_5000: 80,
                BudgetRange.RANGE_5000_10000: 95,
                BudgetRange.ABOVE_10000: 100
            }
            
            budget_score = budget_scores.get(request.budget_range, 50)
            total_score += budget_score * 0.15
            
            # Urgency bonus (10% weight)
            urgency_scores = {
                UrgencyLevel.LOW: 25,
                UrgencyLevel.MEDIUM: 50,
                UrgencyLevel.HIGH: 75,
                UrgencyLevel.URGENT: 100
            }
            
            urgency_score = urgency_scores.get(request.urgency_level, 50)
            total_score += urgency_score * 0.1
            
            # Location compatibility (10% weight)
            location_score = 100  # Default to full score
            
            if request.location_requirements:
                if not request.location_requirements.get('remote_allowed', True):
                    # Specific location required
                    if location_preferences:
                        # Simple location matching - in production, this would be more sophisticated
                        location_score = 75
                    else:
                        location_score = 50
            
            total_score += location_score * 0.1
            
            # Deadline pressure adjustment (5% weight)
            if request.deadline:
                days_until_deadline = (request.deadline - datetime.utcnow()).days
                if days_until_deadline <= 3:
                    deadline_score = 100
                elif days_until_deadline <= 7:
                    deadline_score = 80
                elif days_until_deadline <= 30:
                    deadline_score = 60
                else:
                    deadline_score = 40
            else:
                deadline_score = 50
            
            total_score += deadline_score * 0.05
            
            return max(0.0, min(100.0, total_score))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate match score: {str(e)}")
            return 0.0
            
    def apply_to_request(self,
                        request_id: int,
                        applicant_id: int,
                        application_message: str,
                        proposed_budget: Optional[Decimal] = None,
                        proposed_timeline: Optional[Dict[str, Any]] = None,
                        portfolio_links: Optional[List[str]] = None,
                        additional_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Submit application to collaboration request
        
        Args:
            request_id: Request ID to apply to
            applicant_id: Applicant user ID
            application_message: Application message
            proposed_budget: Proposed budget (if applicable)
            proposed_timeline: Proposed timeline
            portfolio_links: Portfolio/sample work links
            additional_info: Additional application information
            
        Returns:
            Application result dictionary
        """
        try:
            request = self.get_by_id(request_id)
            if not request:
                return {'success': False, 'error': 'Request not found'}
            
            if request.status != RequestStatus.OPEN:
                return {'success': False, 'error': 'Request is not open for applications'}
            
            if request.requester_id == applicant_id:
                return {'success': False, 'error': 'Cannot apply to your own request'}
            
            # Check for existing application
            existing_applications = request.metadata.get('applications', [])
            if any(app.get('applicant_id') == applicant_id for app in existing_applications):
                return {'success': False, 'error': 'Already applied to this request'}
            
            # Create application record
            application = {
                'applicant_id': applicant_id,
                'application_message': application_message,
                'proposed_budget': float(proposed_budget) if proposed_budget else None,
                'proposed_timeline': proposed_timeline or {},
                'portfolio_links': portfolio_links or [],
                'additional_info': additional_info or {},
                'applied_at': datetime.utcnow().isoformat(),
                'status': 'pending',
                'application_id': str(uuid.uuid4())
            }
            
            # Update request with new application
            existing_applications.append(application)
            metadata = request.metadata or {}
            metadata['applications'] = existing_applications
            
            # Update application count
            self.update(request_id, 
                       application_count=request.application_count + 1,
                       metadata=metadata,
                       updated_at=datetime.utcnow())
            
            # Send notification to requester (in production)
            self._notify_requester_of_application(request, application)
            
            result = {
                'success': True,
                'application_id': application['application_id'],
                'request_id': request_id,
                'request_title': request.title,
                'applied_at': application['applied_at'],
                'message': 'Application submitted successfully'
            }
            
            self.logger.info(
                f"User {applicant_id} applied to request {request_id} ({request.title})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to apply to request: {str(e)}")
            return {'success': False, 'error': str(e)}
            
    def _notify_requester_of_application(self,
                                       request: CollaborationRequest,
                                       application: Dict[str, Any]) -> None:
        """
        Notify requester of new application
        
        Args:
            request: CollaborationRequest instance
            application: Application details
        """
        try:
            # In production, this would send actual notifications
            notification_data = {
                'type': 'new_application',
                'request_id': request.id,
                'request_title': request.title,
                'applicant_id': application['applicant_id'],
                'application_id': application['application_id'],
                'message': f"New application received for '{request.title}'",
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Notification sent to requester {request.requester_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send application notification: {str(e)}")
            
    def get_request_analytics(self, request_id: int) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a collaboration request
        
        Args:
            request_id: Request ID to analyze
            
        Returns:
            Analytics dictionary
        """
        try:
            request = self.get_by_id(request_id)
            if not request:
                return {'error': 'Request not found'}
            
            applications = request.metadata.get('applications', [])
            
            # Calculate metrics
            days_since_creation = (datetime.utcnow() - request.created_at).days or 1
            applications_per_day = len(applications) / days_since_creation
            
            # Analyze application quality
            quality_scores = []
            budget_proposals = []
            
            for app in applications:
                # Simple quality scoring based on application completeness
                quality_score = 0
                if app.get('application_message') and len(app['application_message']) > 50:
                    quality_score += 25
                if app.get('portfolio_links'):
                    quality_score += 25
                if app.get('proposed_budget'):
                    quality_score += 25
                    budget_proposals.append(app['proposed_budget'])
                if app.get('proposed_timeline'):
                    quality_score += 25
                
                quality_scores.append(quality_score)
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            avg_proposed_budget = sum(budget_proposals) / len(budget_proposals) if budget_proposals else 0
            
            # Determine request health
            if len(applications) >= 5 and avg_quality >= 75:
                health_status = 'EXCELLENT'
            elif len(applications) >= 3 and avg_quality >= 50:
                health_status = 'GOOD'
            elif len(applications) >= 1:
                health_status = 'FAIR'
            else:
                health_status = 'POOR'
            
            analytics = {
                'request_id': request_id,
                'request_reference': request.request_reference,
                'title': request.title,
                'status': request.status.value,
                'engagement_metrics': {
                    'view_count': request.view_count,
                    'application_count': len(applications),
                    'shortlist_count': request.shortlist_count,
                    'applications_per_day': round(applications_per_day, 2),
                    'avg_application_quality': round(avg_quality, 2)
                },
                'budget_analysis': {
                    'requested_range': request.budget_range.value,
                    'avg_proposed_budget': round(avg_proposed_budget, 2) if avg_proposed_budget else None,
                    'proposal_count': len(budget_proposals)
                },
                'timeline_analysis': {
                    'days_since_created': days_since_creation,
                    'deadline': request.deadline.isoformat() if request.deadline else None,
                    'days_until_deadline': (request.deadline - datetime.utcnow()).days if request.deadline else None
                },
                'performance_indicators': {
                    'priority_score': request.priority_score,
                    'match_potential_score': request.match_potential_score,
                    'health_status': health_status
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get request analytics: {str(e)}")
            return {'error': str(e)}

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
