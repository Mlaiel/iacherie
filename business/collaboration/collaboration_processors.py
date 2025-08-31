"""Advanced Collaboration Processing Engine for IA Influencer Agent
Professional business logic processors for collaboration workflows

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
import json
import numpy as np
from collections import defaultdict

from .collaboration_models import (
    CollaborationRequest, CollaborationMatch, CollaborationContract,
    CollaborationSkill, CollaborationType, CollaborationStatus,
    SkillLevel, CollaborationAnalytics
)


logger = logging.getLogger(__name__)


class MatchingStrategy(Enum):
    """Different strategies for collaboration matching"""    SKILL_BASED = "skill_based"
    LOCATION_BASED = "location_based"
    BUDGET_BASED = "budget_based"
    TIMELINE_BASED = "timeline_based"
    HYBRID_INTELLIGENT = "hybrid_intelligent"
    ML_POWERED = "ml_powered"


@dataclass
class ProcessingResult:
    """Result of collaboration processing operation"""    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CollaborationMatchingProcessor:
    """Advanced collaboration matching processor with ML capabilities"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.matching_weights = self.config.get('matching_weights', {
            'skill_compatibility': 0.35,
            'location_proximity': 0.15,
            'budget_alignment': 0.20,
            'timeline_compatibility': 0.15,
            'reputation_score': 0.10,
            'communication_style': 0.05
        })
        self.min_match_threshold = self.config.get('min_match_threshold', 0.6)
        
    async def find_matches(
        self, 
        request: CollaborationRequest,
        candidate_profiles: List[Dict[str, Any]],
        strategy: MatchingStrategy = MatchingStrategy.HYBRID_INTELLIGENT
    ) -> ProcessingResult:
        """Find and rank collaboration matches"""        start_time = datetime.utcnow()
        
        try:
            if strategy == MatchingStrategy.HYBRID_INTELLIGENT:
                matches = await self._hybrid_intelligent_matching(request, candidate_profiles)
            elif strategy == MatchingStrategy.ML_POWERED:
                matches = await self._ml_powered_matching(request, candidate_profiles)
            elif strategy == MatchingStrategy.SKILL_BASED:
                matches = await self._skill_based_matching(request, candidate_profiles)
            elif strategy == MatchingStrategy.LOCATION_BASED:
                matches = await self._location_based_matching(request, candidate_profiles)
            elif strategy == MatchingStrategy.BUDGET_BASED:
                matches = await self._budget_based_matching(request, candidate_profiles)
            else:
                matches = await self._timeline_based_matching(request, candidate_profiles)
            
            # Filter and rank matches
            qualified_matches = [m for m in matches if m.compatibility_score >= self.min_match_threshold]
            qualified_matches.sort(key=lambda x: x.priority_score, reverse=True)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data=qualified_matches,
                metadata={
                    'strategy_used': strategy.value,
                    'total_candidates': len(candidate_profiles),
                    'qualified_matches': len(qualified_matches),
                    'average_score': np.mean([m.compatibility_score for m in qualified_matches]) if qualified_matches else 0
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Matching processing failed: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def _hybrid_intelligent_matching(
        self, 
        request: CollaborationRequest,
        candidates: List[Dict[str, Any]]
    ) -> List[CollaborationMatch]:
        """Advanced hybrid matching combining multiple strategies"""        matches = []
        
        for candidate in candidates:
            if candidate.get('id') == request.creator_id:
                continue  # Skip self-matching
                
            # Calculate comprehensive compatibility
            skill_score = await self._calculate_skill_compatibility(request, candidate)
            location_score = self._calculate_location_compatibility(request, candidate)
            budget_score = self._calculate_budget_compatibility(request, candidate)
            timeline_score = self._calculate_timeline_compatibility(request, candidate)
            reputation_score = candidate.get('reputation_score', 0.5)
            communication_score = self._calculate_communication_compatibility(request, candidate)
            
            # Weighted overall score
            overall_score = (
                skill_score * self.matching_weights['skill_compatibility'] +
                location_score * self.matching_weights['location_proximity'] +
                budget_score * self.matching_weights['budget_alignment'] +
                timeline_score * self.matching_weights['timeline_compatibility'] +
                reputation_score * self.matching_weights['reputation_score'] +
                communication_score * self.matching_weights['communication_style']
            )
            
            # Create match object
            match = CollaborationMatch(
                request_id=request.id,
                matched_creator_id=candidate['id'],
                compatibility_score=overall_score,
                skill_matches=await self._get_detailed_skill_matches(request, candidate),
                location_match=location_score > 0.8,
                language_match=self._check_language_compatibility(request, candidate),
                budget_compatible=budget_score > 0.7,
                timeline_compatible=timeline_score > 0.7,
                reputation_score=reputation_score,
                portfolio_relevance=self._calculate_portfolio_relevance(request, candidate),
                communication_style_match=communication_score,
                work_availability_match=self._calculate_availability_match(request, candidate)
            )
            
            matches.append(match)
            
        return matches
    
    async def _ml_powered_matching(
        self, 
        request: CollaborationRequest,
        candidates: List[Dict[str, Any]]
    ) -> List[CollaborationMatch]:
        """ML-powered matching using advanced algorithms"""        # Feature extraction for ML model
        request_features = self._extract_request_features(request)
        
        matches = []
        for candidate in candidates:
            if candidate.get('id') == request.creator_id:
                continue
                
            candidate_features = self._extract_candidate_features(candidate)
            
            # Simulate ML prediction (replace with actual ML model)
            compatibility_score = await self._ml_predict_compatibility(
                request_features, candidate_features
            )
            
            match = CollaborationMatch(
                request_id=request.id,
                matched_creator_id=candidate['id'],
                compatibility_score=compatibility_score,
                skill_matches=await self._get_detailed_skill_matches(request, candidate),
                location_match=self._check_location_match(request, candidate),
                language_match=self._check_language_compatibility(request, candidate),
                budget_compatible=self._check_budget_compatibility(request, candidate),
                timeline_compatible=self._check_timeline_compatibility(request, candidate),
                reputation_score=candidate.get('reputation_score', 0.5)
            )
            
            matches.append(match)
            
        return matches
    
    async def _calculate_skill_compatibility(
        self, 
        request: CollaborationRequest,
        candidate: Dict[str, Any]
    ) -> float:
        """Calculate skill compatibility score"""        if not request.required_skills or not candidate.get('skills'):
            return 0.0
            
        candidate_skills = [CollaborationSkill(**skill) for skill in candidate['skills']]
        total_score = 0.0
        skill_matches = 0
        
        for required_skill in request.required_skills:
            best_match_score = 0.0
            for candidate_skill in candidate_skills:
                score = required_skill.compatibility_score(candidate_skill)
                best_match_score = max(best_match_score, score)
            
            if best_match_score > 0:
                total_score += best_match_score
                skill_matches += 1
        
        return total_score / len(request.required_skills) if request.required_skills else 0.0
    
    def _calculate_location_compatibility(
        self, 
        request: CollaborationRequest,
        candidate: Dict[str, Any]
    ) -> float:
        """Calculate location compatibility score"""        if request.remote_work_allowed:
            return 1.0  # Perfect score for remote work
            
        candidate_locations = candidate.get('locations', [])
        if not request.preferred_locations or not candidate_locations:
            return 0.5  # Neutral score if no location preferences
            
        # Check for exact location matches
        common_locations = set(request.preferred_locations) & set(candidate_locations)
        if common_locations:
            return 1.0
            
        # Check for regional proximity (simplified)
        proximity_score = self._calculate_location_proximity(
            request.preferred_locations, candidate_locations
        )
        
        return proximity_score
    
    def _calculate_budget_compatibility(
        self, 
        request: CollaborationRequest,
        candidate: Dict[str, Any]
    ) -> float:
        """Calculate budget compatibility score"""        request_budget = request.budget_range
        candidate_rates = candidate.get('rates', {})
        
        if not request_budget or not candidate_rates:
            return 0.7  # Neutral score if no budget information
            
        request_max = request_budget.get('max', float('inf'))
        request_min = request_budget.get('min', 0)
        
        candidate_min_rate = candidate_rates.get('min', 0)
        candidate_max_rate = candidate_rates.get('max', float('inf'))
        
        # Check for overlap
        overlap_start = max(request_min, candidate_min_rate)
        overlap_end = min(request_max, candidate_max_rate)
        
        if overlap_start <= overlap_end:
            # Calculate overlap percentage
            request_range = request_max - request_min
            overlap_range = overlap_end - overlap_start
            
            if request_range > 0:
                return min(overlap_range / request_range, 1.0)
            return 1.0
        
        return 0.0
    
    def _calculate_timeline_compatibility(
        self, 
        request: CollaborationRequest,
        candidate: Dict[str, Any]
    ) -> float:
        """Calculate timeline compatibility score"""        request_timeline = request.timeline
        candidate_availability = candidate.get('availability', {})
        
        if not request_timeline or not candidate_availability:
            return 0.7  # Neutral score
            
        request_start = request_timeline.get('start')
        request_end = request_timeline.get('end')
        
        available_start = candidate_availability.get('start')
        available_end = candidate_availability.get('end')
        
        if not all([request_start, request_end, available_start, available_end]):
            return 0.5
            
        # Check for overlap
        overlap_start = max(request_start, available_start)
        overlap_end = min(request_end, available_end)
        
        if overlap_start <= overlap_end:
            # Calculate overlap percentage
            request_duration = (request_end - request_start).days
            overlap_duration = (overlap_end - overlap_start).days
            
            if request_duration > 0:
                return min(overlap_duration / request_duration, 1.0)
            return 1.0
        
        return 0.0
    
    async def _get_detailed_skill_matches(
        self, 
        request: CollaborationRequest,
        candidate: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get detailed skill matching information"""        matches = []
        candidate_skills = [CollaborationSkill(**skill) for skill in candidate.get('skills', [])]
        
        for required_skill in request.required_skills:
            best_match = None
            best_score = 0.0
            
            for candidate_skill in candidate_skills:
                score = required_skill.compatibility_score(candidate_skill)
                if score > best_score:
                    best_score = score
                    best_match = candidate_skill
            
            if best_match:
                matches.append({
                    'required_skill': required_skill.name,
                    'required_level': required_skill.level.value,
                    'matched_skill': best_match.name,
                    'matched_level': best_match.level.value,
                    'compatibility_score': best_score,
                    'experience_gap': abs(required_skill.experience_years - best_match.experience_years)
                })
        
        return matches
    
    def _extract_request_features(self, request: CollaborationRequest) -> Dict[str, Any]:
        """Extract features from collaboration request for ML"""        return {
            'collaboration_type': request.collaboration_type.value,
            'num_required_skills': len(request.required_skills),
            'num_offered_skills': len(request.offered_skills),
            'budget_range': request.budget_range or {},
            'remote_allowed': request.remote_work_allowed,
            'max_participants': request.max_participants,
            'urgency_score': self._calculate_urgency_score(request),
            'complexity_score': self._calculate_complexity_score(request)
        }
    
    def _extract_candidate_features(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from candidate profile for ML"""        return {
            'num_skills': len(candidate.get('skills', [])),
            'reputation_score': candidate.get('reputation_score', 0.5),
            'completion_rate': candidate.get('completion_rate', 0.5),
            'response_time': candidate.get('avg_response_time', 24),  # hours
            'portfolio_size': len(candidate.get('portfolio', [])),
            'collaboration_count': candidate.get('collaboration_count', 0),
            'rating_average': candidate.get('rating_average', 0.0),
            'specialization_depth': self._calculate_specialization_depth(candidate)
        }
    
    async def _ml_predict_compatibility(
        self, 
        request_features: Dict[str, Any],
        candidate_features: Dict[str, Any]
    ) -> float:
        """ML-powered compatibility prediction (simplified simulation)"""        # This is a simplified simulation - replace with actual ML model
        await asyncio.sleep(0.01)  # Simulate ML processing time
        
        # Feature-based scoring simulation
        collaboration_type_bonus = 0.1 if request_features.get('collaboration_type') == 'music_collaboration' else 0.0
        skill_ratio_score = min(candidate_features['num_skills'] / max(request_features['num_required_skills'], 1), 1.0)
        reputation_weight = candidate_features['reputation_score'] * 0.3
        completion_weight = candidate_features['completion_rate'] * 0.2
        
        base_score = (skill_ratio_score * 0.4 + reputation_weight + completion_weight + collaboration_type_bonus)
        
        # Add some realistic variance
        variance = np.random.normal(0, 0.05)  # Small random variance
        final_score = np.clip(base_score + variance, 0.0, 1.0)
        
        return float(final_score)


class CollaborationWorkflowProcessor:
    """Process collaboration workflows and state transitions"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.notification_enabled = self.config.get('notifications_enabled', True)
        
    async def process_collaboration_request(
        self, 
        request: CollaborationRequest,
        action: str,
        metadata: Dict[str, Any] = None
    ) -> ProcessingResult:
        """Process collaboration request actions"""        start_time = datetime.utcnow()
        
        try:
            if action == "submit":
                result = await self._process_submission(request, metadata or {})
            elif action == "update":
                result = await self._process_update(request, metadata or {})
            elif action == "cancel":
                result = await self._process_cancellation(request, metadata or {})
            elif action == "extend_deadline":
                result = await self._process_deadline_extension(request, metadata or {})
            else:
                raise ValueError(f"Unknown action: {action}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow processing failed for action {action}: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def _process_submission(
        self, 
        request: CollaborationRequest, 
        metadata: Dict[str, Any]
    ) -> ProcessingResult:
        """Process collaboration request submission"""        # Validation
        if not request.title or len(request.title) < 5:
            return ProcessingResult(
                success=False,
                error_message="Title must be at least 5 characters long"
            )
        
        if not request.required_skills:
            return ProcessingResult(
                success=False,
                error_message="At least one required skill must be specified"
            )
        
        # Update status
        request.status = CollaborationStatus.PENDING
        request.updated_at = datetime.utcnow()
        
        # Set expiration if not set
        if not request.expires_at:
            request.expires_at = datetime.utcnow() + timedelta(days=30)
        
        return ProcessingResult(
            success=True,
            data=request,
            metadata={
                'action': 'submitted',
                'new_status': request.status.value,
                'expires_at': request.expires_at.isoformat() if request.expires_at else None
            }
        )
    
    async def _process_update(
        self, 
        request: CollaborationRequest, 
        metadata: Dict[str, Any]
    ) -> ProcessingResult:
        """Process collaboration request update"""        # Track what was updated
        updated_fields = metadata.get('updated_fields', [])
        
        request.updated_at = datetime.utcnow()
        
        # If critical fields updated, may need re-matching
        critical_fields = {'required_skills', 'budget_range', 'timeline', 'collaboration_type'}
        needs_rematching = bool(set(updated_fields) & critical_fields)
        
        return ProcessingResult(
            success=True,
            data=request,
            metadata={
                'action': 'updated',
                'updated_fields': updated_fields,
                'needs_rematching': needs_rematching
            }
        )
    
    async def _process_cancellation(
        self, 
        request: CollaborationRequest, 
        metadata: Dict[str, Any]
    ) -> ProcessingResult:
        """Process collaboration request cancellation"""        cancellation_reason = metadata.get('reason', 'No reason provided')
        
        request.status = CollaborationStatus.CANCELLED
        request.updated_at = datetime.utcnow()
        
        return ProcessingResult(
            success=True,
            data=request,
            metadata={
                'action': 'cancelled',
                'reason': cancellation_reason,
                'cancelled_at': request.updated_at.isoformat()
            }
        )
    
    async def _process_deadline_extension(
        self, 
        request: CollaborationRequest, 
        metadata: Dict[str, Any]
    ) -> ProcessingResult:
        """Process deadline extension request"""        extension_days = metadata.get('extension_days', 7)
        reason = metadata.get('reason', 'Extension requested')
        
        if request.expires_at:
            new_expiry = request.expires_at + timedelta(days=extension_days)
            request.expires_at = new_expiry
            request.updated_at = datetime.utcnow()
        
        return ProcessingResult(
            success=True,
            data=request,
            metadata={
                'action': 'deadline_extended',
                'extension_days': extension_days,
                'new_expiry': request.expires_at.isoformat() if request.expires_at else None,
                'reason': reason
            }
        )


class CollaborationContractProcessor:
    """Process collaboration contracts and agreements"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
    async def create_contract(
        self,
        request: CollaborationRequest,
        selected_participants: List[str],
        contract_terms: Dict[str, Any]
    ) -> ProcessingResult:
        """Create a collaboration contract"""        start_time = datetime.utcnow()
        
        try:
            # Validate participants
            if len(selected_participants) < 2:
                return ProcessingResult(
                    success=False,
                    error_message="At least 2 participants required for collaboration"
                )
            
            if request.creator_id not in selected_participants:
                selected_participants.insert(0, request.creator_id)
            
            # Create contract
            contract = CollaborationContract(
                collaboration_request_id=request.id,
                participants=selected_participants,
                title=contract_terms.get('title', request.title),
                description=contract_terms.get('description', request.description),
                deliverables=contract_terms.get('deliverables', []),
                milestones=contract_terms.get('milestones', []),
                total_budget=contract_terms.get('total_budget'),
                payment_terms=contract_terms.get('payment_terms', {}),
                revenue_sharing=contract_terms.get('revenue_sharing', {}),
                start_date=contract_terms.get('start_date', datetime.utcnow()),
                end_date=contract_terms.get('end_date', datetime.utcnow() + timedelta(days=30)),
                intellectual_property_terms=contract_terms.get('ip_terms', {}),
                usage_rights=contract_terms.get('usage_rights', {}),
                confidentiality_terms=contract_terms.get('confidentiality', {})
            )
            
            # Validate revenue sharing totals to 100%
            if contract.revenue_sharing:
                total_share = sum(contract.revenue_sharing.values())
                if abs(total_share - 100.0) > 0.01:  # Allow for floating point precision
                    return ProcessingResult(
                        success=False,
                        error_message=f"Revenue sharing must total 100%, currently {total_share}%"
                    )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data=contract,
                metadata={
                    'contract_id': contract.id,
                    'participants_count': len(selected_participants),
                    'requires_signatures': len(selected_participants)
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Contract creation failed: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def process_contract_signature(
        self,
        contract: CollaborationContract,
        participant_id: str,
        signature_data: Dict[str, Any]
    ) -> ProcessingResult:
        """Process contract signature from participant"""        start_time = datetime.utcnow()
        
        try:
            # Validate participant
            if participant_id not in contract.participants:
                return ProcessingResult(
                    success=False,
                    error_message="Participant not authorized to sign this contract"
                )
            
            # Check if already signed
            if participant_id in contract.signatures:
                return ProcessingResult(
                    success=False,
                    error_message="Participant has already signed this contract"
                )
            
            # Add signature
            contract.signatures[participant_id] = datetime.utcnow()
            contract.updated_at = datetime.utcnow()
            
            # Check if fully signed
            if contract.is_fully_signed():
                contract.approved_by_all = True
                contract.status = CollaborationStatus.ACTIVE
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data=contract,
                metadata={
                    'signed_by': participant_id,
                    'signatures_count': len(contract.signatures),
                    'total_participants': len(contract.participants),
                    'fully_signed': contract.is_fully_signed(),
                    'contract_active': contract.status == CollaborationStatus.ACTIVE
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Contract signature processing failed: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )


# Export all processors
__all__ = [
    'MatchingStrategy',
    'ProcessingResult',
    'CollaborationMatchingProcessor',
    'CollaborationWorkflowProcessor', 
    'CollaborationContractProcessor'
]
